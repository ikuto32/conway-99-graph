"""Independent semantic review of the restricted cyclic-factor reduction.

No producer or solver imports. Reuses a pinned independent raw-domain checker;
does not approve the threshold CNF or any complete factor.
"""
import argparse
from collections import Counter
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import sha256
from itertools import combinations,product
import json
from pathlib import Path
import platform
import subprocess
import sys
import audit_20260930_hadamard_prism_relaxation_and_order as rawcheck

ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';I=B+'independent_review/';RUN=B+'hadamard_six_prism_cyclic_cnf/'
RAW=B+'hadamard20_support/six_prism.json';ORDER=I+'hadamard_six_prism_column_order/summary.json'
PINS={RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',
 ORDER:'0ce1be9ca11a3e860aa97791cfb4f42c1660d937a69ac7a9b7d96ca37640c9d2',
 RUN+'summary.json':'ef468795786fae63bdaa21e15fa3d81968b6a87e14d5ceb4076858cbdaa20190',
 RUN+'scope.json':'847cd3aa5ab82216a552ea9c57bb63663ef9e906fadbb8be7e9b019562ced7f0',
 RUN+'model.json':'9799d69cd02c2293e0d7f89615ba9000949c5f2bd097dea710acd4ac235f4b57'}
def need(ok,why):
    if not ok:raise ValueError(why)
def digest(p):return sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def reject(name,op,records):
    try:op()
    except (ValueError,KeyError,IndexError,TypeError):records.append(dict(name=name,rejected=True))
    else:raise AssertionError('corruption accepted '+name)

def gauge_words():
    words=[]
    for other_zero in range(1,6):
        rest=[a for a in range(1,6)if a!=other_zero]
        for ones in combinations(rest,2):words.append(tuple(0 if a in(0,other_zero)else 1 if a in ones else 2 for a in range(6)))
    return sorted(words)

def verify_scope(raw,scope):
    gram,supports,options=rawcheck.raw_domain(raw);groups={}
    for d,s in enumerate(supports):groups.setdefault(tuple(s),[]).append(d)
    ordered=sorted(groups.items(),key=lambda kv:kv[1][0]);words=gauge_words();need(len(words)==len(set(words))==30,'complete gauged30domain')
    need(scope['raw_support']==RAW and scope['raw_support_sha256']==PINS[RAW],'exact support binding')
    need(scope['L']==raw['L'] and scope['core_adjacency']==raw['core_adjacency'] and scope['target_gram36']==gram and scope['matchings']==raw['matchings'],'all raw fixed geometry')
    need(scope['first_coordinate_color']==0 and scope['within_group_phase_by_sorted_column']==[0,1,2],'exact cyclic phase convention')
    need(scope['extra_cyclic_factor_constraint']is True and scope['arbitrary_fixedL_factors_covered']is False and scope['all_D_unencoded']is True and scope['target_graph']is False and scope['no_target_automorphism_assumed']is True,'explicit construction restriction')
    domains=scope['domains'];need(len(domains)==20,'20base groups');lifted=[];phase_receipts=[]
    for p,((coords,cols),domain)in enumerate(zip(ordered,domains,strict=True)):
        need(domain['group']==p and domain['support_coordinates']==list(coords)and domain['raw_columns']==cols,'exact group/column mapping')
        need(len(domain['choices'])==30,'30choices each group');triples=[]
        for j,(word,choice)in enumerate(zip(words,domain['choices'],strict=True)):
            expected=[{12*((word[a]+r)%3)+coords[a]for a in range(6)}for r in range(3)]
            need(choice['selector']==30*p+j+1 and choice['choice_index']==j and choice['coloring']==list(word),'exact primary selector and colour word')
            need(choice['lifted_rows']==[sorted(s)for s in expected]and [int(v,16)for v in choice['lifted_masks_hex']]==[sum(2**i for i in s)for s in expected],'all literal lifted triples')
            need(all(len(s)==6 and all(sum(i//12==g for i in s)==2 for g in range(3))for s in expected),'balanced actual columns')
            need(all(expected[r].isdisjoint(expected[s])for r in range(3)for s in range(r+1,3)),'withintriplet disjointness')
            need(all(sum(12*g+a in s for s in expected)==1 for a in coords for g in range(3)),'eachcoordinateonceperfiberpergroup')
            triples.append(expected)
        lifted.append(triples)
        # Gauge coverage checked on actual coordinate labels, for all90 words.
        for original in sorted(tuple(o['fibres_by_sorted_coordinate'])for o in raw['column_colour_options'][cols[0]]):
            phase=original[0];normalized=tuple((v-phase)%3 for v in original);j=words.index(normalized)
            before=[{12*((original[a]+r)%3)+coords[a]for a in range(6)}for r in range(3)]
            need(all(lifted[p][j][r]==before[(r-phase)%3]for r in range(3)),'actual cyclic relabelling transports original phase')
            phase_receipts.append(dict(group=p,original=list(original),normalized_choice=j,removed_phase=phase,new_column_takes_old_phase=[(r-phase)%3 for r in range(3)]))
    coordinate_counts=[sum(a in coords for coords,_ in ordered)for a in range(12)];need(coordinate_counts==[10]*12,'allautomatic row10margins')
    pairs=[(a,b)for a in range(12)for b in range(a+1,12)if b!=(a^1)]
    expected_pairs=[dict(coordinates=[a,b],containing_groups=[p for p,(s,_)in enumerate(ordered)if a in s and b in s])for a,b in pairs]
    need(scope['coordinate_pairs']==expected_pairs and all(len(r['containing_groups'])==5 for r in expected_pairs),'all60nonmatching pairs have5base occurrences')
    return words,lifted,phase_receipts,expected_pairs

def verify_equations(scope,model,words,lifted,pairs):
    need(model['domains']==scope['domains'],'model domains equal audited semantic scope')
    rows=model['counter_rows'];need(len(rows)==200,'20onehot plus180difference equations')
    semantic=[];local_checks=0
    for p in range(20):semantic.append(dict(kind='group_exactone',group=p,inputs=list(range(30*p+1,30*p+31)),bound=1,equality=True))
    for pair in pairs:
        a,b=pair['coordinates']
        for delta in range(3):
            terms=[]
            for p in pair['containing_groups']:
                coords=scope['domains'][p]['support_coordinates'];ia,ib=coords.index(a),coords.index(b)
                for j,word in enumerate(words):
                    difference=(word[ib]-word[ia])%3
                    if difference==delta:terms.append(30*p+j+1)
            semantic.append(dict(kind='coordinate_difference_count',coordinates=[a,b],difference=delta,inputs=terms,bound=[1,2,2][delta],equality=True))
        for p in pair['containing_groups']:
            coords=scope['domains'][p]['support_coordinates'];ia,ib=coords.index(a),coords.index(b)
            for j,word in enumerate(words):
                delta=(word[ib]-word[ia])%3
                for g,h in product(range(3),repeat=2):
                    actual=sum(12*g+a in s and 12*h+b in s for s in lifted[p][j])
                    need(actual==int((h-g)%3==delta),'literal localGram equals delta coefficient');local_checks+=1
    for expected,row in zip(semantic,rows,strict=True):need(all(row[k]==v for k,v in expected.items()),'every exact abstract equation coefficient')
    need(local_checks==81000,'complete local offdiagonal checks')
    return semantic,local_checks

def verify_caps(scope,model,words,lifted):
    expected_pairs=[(p,q)for p in range(20)for q in range(p+1,20)]
    records=model['lifted_cap_relations'];need([tuple(r['groups'])for r in records]==expected_pairs,'all190group pairs')
    checks=forbidden=0;receipts=[]
    for record,(p,q)in zip(records,expected_pairs,strict=True):
        left=scope['domains'][p];right=scope['domains'][q];coords=sorted(set(left['support_coordinates'])&set(right['support_coordinates']))
        need(record['actual_column_pairs']==[[d,e]for d in left['raw_columns']for e in right['raw_columns']],'all9actual column pairs')
        masks=[];hist=Counter()
        for i,x in enumerate(words):
            mask=0
            for j,y in enumerate(words):
                counts=[0]*3
                for a in coords:counts[(y[right['support_coordinates'].index(a)]-x[left['support_coordinates'].index(a)])%3]+=1
                for r,s in product(range(3),repeat=2):
                    actual=len(lifted[p][i][r]&lifted[q][j][s])
                    need(actual==counts[(r-s)%3],'all9literal overlaps equal difference histogram');checks+=1
                maximum=max(counts);hist[maximum]+=1
                if maximum>2:mask+=2**j;forbidden+=1
            masks.append(mask)
        need([int(x,16)for x in record['forbidden_right_masks_hex']]==masks,'complete binary cap relation')
        need(record['maximum_overlap_histogram']=={str(k):v for k,v in sorted(hist.items())},'all900choice-pair max-overlap census')
        need(record['clause_count']==sum(m.bit_count()for m in masks),'declared semantic forbidden count')
        receipts.append(dict(groups=[p,q],common_support_coordinates=coords,maximum_overlap_histogram=dict(sorted(hist.items())),forbidden=sum(m.bit_count()for m in masks)))
    need(checks==1539000 and forbidden==28674,'complete finite cap predicate counts')
    return checks,forbidden,receipts

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve()
    need(out.is_relative_to(ROOT),'workspace output');out.mkdir(parents=True,exist_ok=False);now=datetime.now(timezone.utc).isoformat();bindings={};corrupt=[]
    try:
        for p,h in PINS.items():need(digest(ROOT/p)==h,'frozen premise '+p);bindings[p]=h
        order=read(ORDER);helper=key(Path(rawcheck.__file__));need(digest(ROOT/helper)==order['inputs_sha256'][helper],'shared independent raw checker pinned')
        bindings[helper]=digest(ROOT/helper)
        summary=read(RUN+'summary.json')
        for p,h in summary['inputs_sha256'].items():need(digest(ROOT/p)==h,'producer immutable source/input '+p);bindings[p]=h
        raw=read(RAW);scope=read(RUN+'scope.json');model=read(RUN+'model.json')
        # Generic two-coordinate truth controls, before full domain/cap checking.
        truth=0
        for ca,cb,g,h in product(range(3),repeat=4):
            direct=sum(int((ca+r)%3==g and(cb+r)%3==h)for r in range(3))
            need(direct==int((h-g)%3==(cb-ca)%3),'all81cyclic pair truth cases');truth+=1
        words,lifted,phase,pairs=verify_scope(raw,scope)
        semantic,local_checks=verify_equations(scope,model,words,lifted,pairs)
        capchecks,forbidden,caps=verify_caps(scope,model,words,lifted)
        save(out/'phase_transports.json',dict(records=phase,scope='All1800group-specific balanced-word gauges; only within the extra cyclic-F subclass.'))
        save(out/'exact_semantic_equations.json',dict(records=semantic,scope='Abstract primary-selector constraints; no auxiliary or DIMACS clause approval.'))
        save(out/'cap_predicate_checks.json',dict(records=caps,literal_column_pair_checks=capchecks,forbidden_choice_pairs=forbidden))
        for name,change in [('wrong_raw_column_group',lambda s:s['domains'][0]['raw_columns'].__setitem__(1,1)),
                            ('wrong_phase_convention',lambda s:s.update(within_group_phase_by_sorted_column=[0,2,1])),
                            ('wrong_gauge_colour',lambda s:s['domains'][0]['choices'][0]['coloring'].__setitem__(0,1)),
                            ('wrong_lifted_row',lambda s:s['domains'][0]['choices'][0]['lifted_rows'][0].__setitem__(0,35)),
                            ('claims_unrestricted_Fcoverage',lambda s:s.update(arbitrary_fixedL_factors_covered=True))]:
            bad=deepcopy(scope);change(bad);reject(name,lambda:verify_scope(raw,bad),corrupt)
        bad=deepcopy(model);bad['counter_rows'][20]['inputs'].pop();reject('missing_delta_coefficient',lambda:verify_equations(scope,bad,words,lifted,pairs),corrupt)
        bad=deepcopy(model);bad['counter_rows'][21]['bound']=1;reject('wrong_delta_target',lambda:verify_equations(scope,bad,words,lifted,pairs),corrupt)
        bad=deepcopy(model);bad['lifted_cap_relations'][0]['forbidden_right_masks_hex'][0]='ffffffff';reject('wrong_cap_relation',lambda:verify_caps(scope,bad,words,lifted),corrupt)
        bad=deepcopy(model);bad['lifted_cap_relations'].pop();reject('missing_group_pair',lambda:verify_caps(scope,bad,words,lifted),corrupt)
        save(out/'controls.json',dict(local_cyclic_truth_cases=truth,corruptions=corrupt,no_full_research_factor_positive=True))
        for p in [Path(__file__),ROOT/'docs/AUDIT_20260930_HADAMARD_CYCLIC_REDUCTION.md',ROOT/'uv.lock',ROOT/'pyproject.toml']:bindings[key(p)]=digest(p)
        need(all(digest(ROOT/p)==h for p,h in bindings.items()),'all bound bytes stable')
        report=dict(status='INDEPENDENT_HADAMARD_CYCLIC_FACTOR_REDUCTION_PASS',created_at=now,updated_at=datetime.now(timezone.utc).isoformat(),
            source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),
            inputs_sha256=bindings,outputs_sha256={key(p):digest(p)for p in out.iterdir()if p.is_file()},
            claim_id='C-FIXED-HADAMARD-SIX-PRISM-CYCLIC-FIBRE-REDUCTION',claim_revision=1,kind='mathematical result',basis=['DERIVED','COMPUTED'],
            recommendation='VERIFIED',review_state='CLEAR',verifier='/root/eight_domain_audit',method='independent_derivation_and_exact_artifact_check',
            statement='Within the explicit fixed Hadamard six-prism subclass whose three columns in each identical-support group are cyclic fibre shifts, a column relabelling gauges the first coordinate colour to0, leaving30choices pergroup; the full prescribed36Gram is equivalent to180coordinate-difference count equations with targets(1,2,2), and all1770outside-column caps are equivalent to the saved within-triple disjointness and190complete binary group-choice predicates.',
            scope='Exactly the specified20triplicate-support cyclic-F construction subclass. This is not without loss of generality among arbitrary fixed-support factors; residualD is arbitrary and unencoded.',
            dependencies=[dict(id='C-FIVE-FIXED-HADAMARD20-SUPPORT-PROJECTIONS',revision=1,relation='premise'),
                dict(id='C-FIXED-HADAMARD-SIX-PRISM-IDENTICAL-SUPPORT-ORDER-NORMALIZATION',revision=1,relation='uses_result')],
            assumptions=['The extra cyclic-fibre relation among each triple of F columns is explicitly imposed.','No automorphism of a target graph or residualD is assumed.'],
            counts=dict(groups=20,choices=600,group_specific_gauge_transports=1800,exact_abstract_equations=200,difference_equalities=180,
                local_Gram_coefficients=local_checks,group_choice_pairs=171000,literal_overlap_checks=capchecks,forbidden_choice_pairs=forbidden,
                actual_column_pairs=1770,local_truth_controls=truth,corruptions=len(corrupt)),
            shared_components=['Frozen independently authored raw-domain helper from the uniform/order audit, pinned by its prior gate.','No producer code, threshold builder, solver or previous cap checker is imported.'],
            limitations=['This semantic reduction gate does not reconstruct or approve auxiliary gates, all DIMACS clauses, SAT objects or proof traces.',
                'No complete F, residualD or target graph is supplied.','UNSAT in this subclass would not exclude other colorings of the same support or other supports.',
                'No novelty or target-wide coverage claim.'],artifact_availability='LOCAL_ONLY',retrieval='All exact raw input and semantic checking records are hash-bound; public publication not yet confirmed.',
            target_resolution=False,external_review=False,overall_search_coverage='UNKNOWN; no validated denominator.')
        save(out/'summary.json',report);print(json.dumps(dict(status=report['status'],summary_sha256=digest(out/'summary.json'))))
    except BaseException as exc:
        save(out/'failure.json',dict(error=repr(exc),source_sha256=digest(Path(__file__)),timestamp=datetime.now(timezone.utc).isoformat()));raise

if __name__=='__main__':main()
