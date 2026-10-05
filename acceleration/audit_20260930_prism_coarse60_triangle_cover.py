"""Independent truth-table census, literal cover and finite-tree checking."""
import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'
I=B+'independent_review/'
RUN=B+'prism_coarse60_triangle_cover/'
MODEL=B+'prism_coarse60_bitlift/model.json'
SCOPE=B+'prism_coarse60_bitlift/scope.json'
TEMPLATE=B+'prism_coarse_complement/coarse_template.json'
GATE=I+'identity_p_triangle_partition/summary.json'
PINS={RUN+'summary.json':'70a35a60105be0c00f12d64c05bfe1b8ca6991305bbb0a3e88aaa3abec9ac188',
      RUN+'all_triples.json':'fd6c1a24ba39005702ac61742119ed643540285ef5775cdc4555f678e66f8ce3',
      RUN+'coarse_cover_witness.json':'d9309ee9b5d30e783f8564a0ac4e17ef1ff0b6aef05632afdef8748e93aff65a',
      GATE:'15a32c8e4fb4928f78a6e931e09054ddcfd90c027717e8c0d0828c6f5406a516'}

def need(ok,why):
    if not ok:raise ValueError(why)
def digest(p):return sha256(p.read_bytes()).hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads((ROOT/p).read_bytes())
def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
def reject(name,operation,records):
    try:operation()
    except (ValueError,KeyError,IndexError,TypeError):records.append(dict(name=name,rejected=True))
    else:raise AssertionError('corrupt control accepted: '+name)

def truth_table():
    table={};truth_cases=0
    for fibres in product(range(3),repeat=3):
        assignments=[]
        for bits in product(range(2),repeat=3):
            chosen=[(fibres[i],bits[i]) for i in range(3)]
            valid=all(chosen[i]!=chosen[j] for i in range(3) for j in range(i+1,3))
            truth_cases+=1
            if valid:assignments.append(bits)
        required=[(i,j) for i in range(3) for j in range(i+1,3)
                  if assignments and all(v[i]!=v[j] for v in assignments)]
        # Characterization checked against all eight possibilities, not assumed.
        predicted=[v for v in product(range(2),repeat=3) if assignments and all(v[i]!=v[j] for i,j in required)]
        need(assignments==predicted,'truth-table characterization complete')
        need(len(assignments) in (0,4,8),'component assignment multiplicity')
        table[fibres]=dict(assignments=assignments,required=required)
    return table,truth_cases

def cover_check(n,triples,cover):
    need(type(cover)is list and len(cover)*3==n,'cover cardinality')
    need(all(type(i)is int and 0<=i<len(triples) for i in cover),'cover IDs')
    need(sorted(v for i in cover for v in triples[i])==list(range(n)),'every vertex covered once')

def check_census(records,words,table):
    expected_population=[(d,e,f) for d in range(58) for e in range(d+1,59) for f in range(e+1,60)]
    need(len(records)==len(expected_population)==34220,'all choose60,3 triples')
    triples=[];rejects=Counter();requirements_hist=Counter();local_counts=Counter()
    for population_id,(columns,row) in enumerate(zip(expected_population,records,strict=True)):
        need(row['population_id']==population_id and row['columns']==list(columns),'complete lexicographic universe')
        impossible=[];requirements=[];assignment_count=1
        for a in range(6):
            fibres=tuple(words[d][a] for d in columns);truth=table[fibres]
            assignment_count*=len(truth['assignments'])
            if not truth['assignments']:impossible.append(a)
            else:
                for i,j in truth['required']:
                    d,e=columns[i],columns[j]
                    requirements.append(dict(component=a,columns=[d,e],variables=[2449+6*d+a,2449+6*e+a]))
        need(row['all_same_components']==impossible,'all exact impossibility components')
        if impossible:
            need(row['required_opposite_bits'] is None and 'admissible_id' not in row and 'local_bit_assignments' not in row,'rejected-record scope')
            need(assignment_count==0,'rejected triples have no local bit lift');rejects[len(impossible)]+=1
        else:
            need(row['admissible_id']==len(triples),'contiguous admissible IDs')
            need(row['required_opposite_bits']==requirements,'all and only forced opposite pairs')
            need(row['local_bit_assignments']==assignment_count==2**(18-len(requirements)),'exact independent-component product count')
            triples.append(list(columns));requirements_hist[len(requirements)]+=1;local_counts[assignment_count]+=1
    return triples,rejects,requirements_hist,local_counts

def check_tree(tree,triples):
    """Verify saved nodes and stopping at a SAT witness, without running search."""
    nodes=tree['nodes'];need(len(nodes)==25 and tree['root_node']==0,'saved25node population')
    need([r['id']for r in nodes]==list(range(len(nodes))),'unique contiguous node IDs')
    sets=[set(t) for t in triples];incident=[{i for i,s in enumerate(sets) if v in s} for v in range(60)]
    seen=set()
    def visit(index,remaining):
        need(type(index)is int and 0<=index<len(nodes) and index not in seen,'unique reachable node')
        seen.add(index);row=nodes[index]
        need(int(row['remaining_mask_hex'],16)==sum(2**v for v in remaining),'literal remaining set')
        if not remaining:
            need(row['status']=='SAT' and row['cover_triple_ids']==[],'empty residual SAT leaf');return []
        available={v:sorted(i for i in incident[v] if sets[i]<=remaining) for v in remaining}
        vertex=min(remaining,key=lambda v:(len(available[v]),v));choices=available[vertex]
        need(row['branch_vertex']==vertex and row['available_triple_ids']==choices,'exact deterministic branching record')
        children=row['children'];need([c['triple_id'] for c in children]==choices[:len(children)],'children are exact ordered prefix')
        found=None
        for c in children:
            need(found is None,'no exploration after SAT witness')
            result=visit(c['child'],remaining-sets[c['triple_id']]);need(c['status']==('SAT' if result is not None else 'UNSAT'),'child status')
            if result is not None:found=[c['triple_id'],*result]
        if found is None:
            need(len(children)==len(choices) and row['status']=='UNSAT','local visited rejection complete');return None
        need(row['status']=='SAT' and row['cover_triple_ids']==found,'exact saved subtree cover');return found
    cover=visit(0,set(range(60)))
    need(seen==set(range(len(nodes))) and tree['status']=='SAT' and tree['cover_triple_ids']==cover,'complete saved tree identity')
    need(tree['stopped_by_resource_limit'] is False and tree['max_nodes']==100000,'recorded stopping scope')
    cover_check(60,triples,cover);return cover

def gram_from_raw39(adjacency):
    need(len(adjacency)==39 and all(len(r)==39 for r in adjacency),'literal39 dimensions')
    need(all(type(x)is int and x in (0,1) for r in adjacency for x in r),'literal39 binary')
    need(all(adjacency[i][i]==0 and all(adjacency[i][j]==adjacency[j][i] for j in range(39)) for i in range(39)),'simple raw39')
    return [[(14 if i==j else 2-adjacency[3+i][3+j])-sum(adjacency[3+i][k]*adjacency[3+j][k] for k in range(39))
             for j in range(36)]for i in range(36)]

def check_witness(witness,triples,words,target,cover):
    need(witness['admissible_triple_ids']==cover and witness['triangles']==[triples[i]for i in cover],'raw20triangle witness identity')
    cover_check(60,triples,witness['admissible_triple_ids'])
    bits=witness['bits60x6'];need(len(bits)==60 and all(len(r)==6 for r in bits),'bit dimensions')
    need(all(type(x)is int and x in (0,1)for r in bits for x in r),'binary coordinate bits')
    supports=[sorted(12*word[a]+2*a+bits[d][a]for a in range(6))for d,word in enumerate(words)]
    need(supports==witness['column_supports36'] and all(len(set(s))==6 for s in supports),'literal raw column supports')
    pairs=[]
    for t in witness['triangles']:
        for i in range(3):
            for j in range(i+1,3):
                d,e=t[i],t[j];need(set(supports[d]).isdisjoint(supports[e]),'each triangle pair literally disjoint');pairs.append([d,e])
    need(len(pairs)==witness['literal_disjoint_column_pair_checks']==60,'all60withintriangle pairs')
    rows=[{d for d,s in enumerate(supports)if r in s}for r in range(36)]
    actual=[[len(a&b)for b in rows]for a in rows]
    mismatches=[dict(row=i,column=j,actual=actual[i][j],prescribed=target[i][j])for i in range(36)for j in range(36)if actual[i][j]!=target[i][j]]
    need(len(mismatches)==witness['full_Gram_mismatching_entries']==900,'all1296Gramcoefficients')
    need(witness['full_Gram_matches'] is False and witness['target_graph'] is False and witness['residual_degree8_graph'] is None,'precise nonfactor scope')
    return dict(incidence_matrix=[[int(d in r)for d in range(60)]for r in rows],actual_gram=actual,prescribed_gram=target,
                mismatches=mismatches,row_sums=list(map(len,rows)),within_triangle_pairs=pairs,
                mathematical_meaning='Coarse cover and local disjoint bits only; not an exact prescribed-Gram factor.')

def controls(table,truth_cases):
    need(truth_cases==216,'complete local truth population')
    need(len(table[0,0,0]['assignments'])==0 and len(table[0,0,1]['assignments'])==4 and len(table[0,1,2]['assignments'])==8,'all three fibre types')
    triples=[[0,1,2],[3,4,5],[0,3,4]];cover_check(6,triples,[0,1])
    bad=[]
    for value in [[0,0],[0],[0,999],[0,2]]:reject('invalid_tiny_cover_'+str(value),lambda:cover_check(6,triples,value),bad)
    # Exhaust all subsets of the20 three-sets on6vertices of size2: disjointness
    # agrees exactly with literal multiplicity-one cover checking.
    universe=[[a,b,c]for a in range(4)for b in range(a+1,5)for c in range(b+1,6)]
    tested=0;valid=0
    for i in range(19):
        for j in range(i+1,20):
            predicted=set(universe[i]).isdisjoint(universe[j]);tested+=1
            try:cover_check(6,universe,[i,j]);accepted=True
            except ValueError:accepted=False
            need(accepted==predicted,'literal tiny cover equivalence');valid+=accepted
    return dict(component_truth_cases=truth_cases,tiny_cover_pairs=tested,tiny_valid_covers=valid,corruptions=bad,
                research_Gram_factor_positive=None,reason='No full research factor is asserted; controls certify only the local/cover checks.')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    out=args.out.resolve();need(out.is_relative_to(ROOT),'workspace output');out.mkdir(parents=True,exist_ok=False)
    started=time.monotonic();now=datetime.now(timezone.utc).isoformat();bindings={}
    try:
        table,truth_cases=truth_table();calibration=controls(table,truth_cases);save(out/'controls.json',calibration)
        for p,h in PINS.items():need(digest(ROOT/p)==h,'frozen exact input '+p);bindings[p]=h
        summary=read(RUN+'summary.json');gate=read(GATE)
        need(gate['status']=='INDEPENDENT_IDENTITY_P_MIXED_AND_TRIANGLE_PARTITION_PASS','conditional triangle premise')
        for p,h in {**summary['inputs_sha256'],**summary['outputs_sha256']}.items():need(digest(ROOT/p)==h,'frozen raw source/artifact '+p);bindings[p]=h
        scope=read(SCOPE);template=read(TEMPLATE);words=scope['columns60'];model=read(MODEL)
        need(words==template['columns60'] and len(words)==60,'exact template scope')
        need(model['raw_bits']==[dict(variable=2449+6*d+a,column=d,component=a,fibre=word[a])for d,word in enumerate(words)for a in range(6)],'all360variable mappings')
        records=read(RUN+'all_triples.json')['records'];triples,rhist,qhist,bitcounts=check_census(records,words,table)
        need(len(triples)==18440 and sum(rhist.values())==15780,'complete finite census totals')
        tree=read(RUN+'search_tree.json');cover=check_tree(tree,triples)
        target=gram_from_raw39(template['complete_raw39_adjacency']);need(target==scope['target_gram36']==template['prescribed_gram36'],'independent literal targetGram')
        witness=read(RUN+'coarse_cover_witness.json');raw=check_witness(witness,triples,words,target,cover)
        save(out/'independent_raw_witness.json',raw)
        save(out/'census_receipt.json',dict(population='All unordered3-subsets of the60exact labelled coarse columns',population_size=len(records),
            admissible=len(triples),rejected=sum(rhist.values()),rejected_component_histogram=dict(sorted(rhist.items())),
            opposite_requirement_histogram=dict(sorted(qhist.items())),local_bit_assignment_count_histogram=dict(sorted(bitcounts.items())),
            admissible_triples_sha256=sha256(json.dumps(triples,separators=(',',':')).encode()).hexdigest(),saved_tree_nodes=len(tree['nodes']),
            tree_review='Every saved node/choice/child/status checked; only explored finite subtree, not an all-search exclusion.'))
        for k,v in dict(total_column_triples=34220,admissible_triples=18440,rejected_triples=15780,
            rejection_all_same_component_histogram={str(k):v for k,v in sorted(rhist.items())},
            opposite_requirement_histogram={str(k):v for k,v in sorted(qhist.items())},cover_status='SAT',search_nodes=25,
            cover_size=20,raw_bit_witness_full_Gram_disagreements=900,solver_calls=0).items():need(summary[k]==v,'exact producer summary '+k)
        corrupt=[]
        for name,change in [
            ('missing_census_record',lambda x:x.pop()),
            ('wrong_population_id',lambda x:x[0].update(population_id=1)),
            ('wrong_admissible_local_count',lambda x:next(r for r in x if 'admissible_id'in r).update(local_bit_assignments=1)),
            ('missing_rejection_component',lambda x:next(r for r in x if r['all_same_components'])['all_same_components'].pop()),
            ('wrong_bit_variable_mapping',lambda x:next(r for r in x if r.get('required_opposite_bits'))['required_opposite_bits'][0]['variables'].__setitem__(0,1)),
        ]:
            bad=deepcopy(records);change(bad);reject(name,lambda:check_census(bad,words,table),corrupt)
        for name,change in [
            ('overlapping_cover',lambda x:x['triangles'].__setitem__(1,x['triangles'][0])),
            ('nonbinary_bit',lambda x:x['bits60x6'][0].__setitem__(0,2)),
            ('wrong_raw_support',lambda x:x['column_supports36'][0].__setitem__(0,35)),
            ('claims_full_Gram',lambda x:x.update(full_Gram_matches=True)),
            ('wrong_mismatch_count',lambda x:x.update(full_Gram_mismatching_entries=899)),
        ]:
            bad=deepcopy(witness);change(bad);reject(name,lambda:check_witness(bad,triples,words,target,cover),corrupt)
        bad=deepcopy(tree);bad['nodes'][0]['available_triple_ids'].pop();reject('omitted_tree_branch',lambda:check_tree(bad,triples),corrupt)
        bad=deepcopy(tree);bad['nodes'][0]['children'][0]['child']=0;reject('tree_cycle',lambda:check_tree(bad,triples),corrupt)
        save(out/'research_corruptions.json',dict(controls=corrupt))
        for p in [Path(__file__),ROOT/'docs/AUDIT_20260930_PRISM_COARSE60_TRIANGLE_COVER.md',ROOT/'uv.lock',ROOT/'pyproject.toml',ROOT/(I+'identity_p_triangle_partition/claim_bindings.json')]:bindings[key(p)]=digest(p)
        need(all(digest(ROOT/p)==h for p,h in bindings.items()),'stable inputs')
        statement='Among all34220 unordered triples of the frozen60 coarse columns, exactly18440 admit local binary choices making their three36-row incidence supports pairwise disjoint and15780 do not; the saved20-triple partition covers all60 columns once, and its saved local bits satisfy all60 within-triple disjointness checks but disagree with the prescribed Gram at exactly900 of1296 ordered entries.'
        report=dict(status='INDEPENDENT_SIX_PRISM_COARSE60_TRIANGLE_COVER_SCOUT_PASS',created_at=now,updated_at=datetime.now(timezone.utc).isoformat(),
            source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),
            inputs_sha256=bindings,outputs_sha256={key(p):digest(p)for p in out.iterdir()if p.is_file()},
            claim_id='C-SIX-PRISM-COARSE60-DISJOINT-TRIPLE-CENSUS-AND-COVER',claim_revision=1,statement=statement,
            kind='empirical/engineering result',basis=['DERIVED','COMPUTED'],recommendation='VERIFIED',review_state='CLEAR',
            scope='One frozen labelled60-column six-prism template; complete triple census and one coarse/local-bit cover witness, not a prescribed-Gram factor.',
            dependencies=[dict(id='C-SIX-PRISM-COARSE60-EXACT-BITLIFT-CNF',revision=1,relation='uses_result'),
                dict(id='C-IDENTITY-P-COMPLETION-THIRTYTHREE-TRIANGLE-PARTITION',revision=1,relation='premise')],
            assumptions=['The identity-cross and specified coarse60 template are explicit restrictions.','No target automorphism, complement pairing or bit normalization is assumed.'],
            verifier='/root/eight_domain_audit',method='independent_derivation_and_exact_artifact_check',
            shared_components=['Raw template/model and separately audited identity-cross triangle-partition premise.','Checker uses only Python standard library; no producer or earlier checking code imported.'],
            counts=dict(triples=34220,admissible=18440,rejected=15780,cover_size=20,within_triple_pairs=60,Gram_entries=1296,Gram_mismatches=900,
                saved_tree_nodes=25,local_truth_controls=216,tiny_cover_pairs=190,corruptions=len(corrupt)+len(calibration['corruptions'])),
            conditional_necessity='Any target completion of this exact template induces such a partition: each residual triangle is supplied by the pinned identity-cross premise, and lambda=1 prevents its adjacent columns from sharing an inner neighbor.',
            limitations=['No complete prescribed-Gram factor, degree8 residual adjacency or target graph.','Only the selected coarse template is covered.',
                'The explored25node tree is checked as a SAT witness record, not an exhaustive nonexistence certificate.',
                'Producer timing is historical evidence, not an independently established performance claim.','No novelty claim.'],
            artifact_availability='LOCAL_ONLY',retrieval='All exact paths/hashes and independent_raw_witness.json are saved; immutable public publication has not yet been confirmed.',
            target_resolution=False,external_review=False,overall_search_coverage='UNKNOWN; no validated denominator.',wall_seconds=time.monotonic()-started)
        save(out/'summary.json',report);print(json.dumps(dict(status=report['status'],summary_sha256=digest(out/'summary.json'),wall_seconds=report['wall_seconds'])))
    except BaseException as exc:
        save(out/'failure.json',dict(error=repr(exc),source_sha256=digest(Path(__file__)),timestamp=datetime.now(timezone.utc).isoformat()));raise

if __name__=='__main__':main()
