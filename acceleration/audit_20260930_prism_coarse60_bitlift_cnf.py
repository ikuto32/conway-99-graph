"""Independent complete coarse60 selector/channel/Gram/cap CNF reconstruction."""
from collections import Counter
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import file_digest,sha256
from itertools import combinations,product
from pathlib import Path
import argparse
import json
import platform
import subprocess
import sys
import time
import audit_20260930_prism_coarse_complement as local

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'acceleration/results/20260930_prism_coarse60_bitlift'
DOMAIN=ROOT/'acceleration/results/20260930_prism_coarse_complement'
GATE=ROOT/'acceleration/results/20260930_independent_review/prism_coarse_complement/summary.json'
GATE_SHA='7087ce1ff80ffd93e186c2e0d642bb99b1b003262f79bb19862e05015a8c590d'
DOC=ROOT/'docs/AUDIT_20260930_PRISM_COARSE60_BITLIFT.md'
PINS={'summary.json':'d7215028fd294d8b23ed787465449f8c16106b3370ceb73f04b842622db1bbb5',
      'instance.cnf':'eaace18635e6c0140a7020ef9f05af298298267dc1545e451d147f4b47577eb5',
      'model.json':'a437d3f1381e9554bff2376726a991f1d1e0ea23c240f8ebacf005c57e82fcb5',
      'scope.json':'3237da2a02c60fc3f0c61e562788582b7ce25946afb523a84dc6634912ed98e9'}

def need(ok,msg):
    if not ok:raise ValueError(msg)
def digest(path):
    with Path(path).open('rb') as f:return file_digest(f,'sha256').hexdigest()
def key(path):return Path(path).resolve().relative_to(ROOT).as_posix()
def stamp():return datetime.now(timezone.utc).isoformat()
def save(path,value):
    with Path(path).open('x',encoding='utf-8',newline='\n') as f:json.dump(value,f,indent=2);f.write('\n')
def same(actual,expected,why):need(actual==expected,why)
def line(clause):return (' '.join(map(str,clause))+' 0\n').encode('ascii')
def accepts(clauses,truth):return all(any(truth[abs(x)]==(x>0) for x in clause) for clause in clauses)

def exact_one_clauses(n):
    rows=[];previous=1;aux=[]
    for selector in range(2,n+1):
        current=n+selector-1;rows.extend([[-previous,current],[-selector,current],[previous,selector,-current],[-previous,-selector]])
        aux.append(current);previous=current
    rows.append([previous]);return rows,aux

def cap_clauses(k):
    rows=[]
    for triple in combinations(range(k),3):
        for setting in product((0,1),repeat=3):
            rows.append([(-v if bit else v) for a,bit in zip(triple,setting) for v in (2*a+1,2*a+2)])
    return rows

def controls():
    exact_cases=0;valid_lifts=0;relation_cases=0;cap_cases=0;rejected=[]
    # Exhaust all auxiliaries too, rather than only the producer's calculated lift.
    for n in range(1,7):
        rows,aux=exact_one_clauses(n)
        for primary in product((False,True),repeat=n):
            extensions=0
            for values in product((False,True),repeat=len(aux)):
                truth=dict(enumerate(primary,1));truth.update(zip(aux,values));extensions+=accepts(rows,truth);exact_cases+=1
            same(extensions,int(sum(primary)==1),'full auxiliary-existential exact-one control');valid_lifts+=extensions
    # Every binary relation2x3, on every one-hot pair, tests allowed-list semantics.
    for bits in product((0,1),repeat=6):
        clauses=[[-1,*[3+j for j in range(3) if bits[j]]],[-2,*[3+j for j in range(3) if bits[3+j]]]]
        for a,b in product(range(2),range(3)):
            truth={1:a==0,2:a==1,3:b==0,4:b==1,5:b==2}
            same(accepts(clauses,truth),bool(bits[3*a+b]),'all tiny relation entries');relation_cases+=1
    for k in range(7):
        clauses=cap_clauses(k)
        for bits in product((False,True),repeat=2*k):
            truth=dict(enumerate(bits,1));same(accepts(clauses,truth),sum(bits[2*a]==bits[2*a+1] for a in range(k))<=2,'complete shared-component cap truth table');cap_cases+=1
    # A selected mask must force the entire local bit word, including its zeroes.
    channel_cases=0
    for chosen in product((False,True),repeat=4):
        clauses=[[-1,(2+i if bit else -(2+i))] for i,bit in enumerate(chosen)]
        for assigned in product((False,True),repeat=4):
            same(accepts(clauses,{1:True,**dict(enumerate(assigned,2))}),assigned==chosen,'full channel truth/false-bit control');channel_cases+=1
    for name,actual,expected in [('flipped_clause',b'1 -2 0\n',b'1 2 0\n'),('missing_clause',b'',b'1 0\n'),
            ('extra_unit',b'1 0\n',b''),('wrong_header',b'p cnf 5238 85697\n',b'p cnf 5238 85698\n')]:
        try:same(actual,expected,'literal byte control')
        except ValueError:rejected.append(name)
        else:raise ValueError('byte corruption accepted')
    return dict(exact_one_all_primary_and_auxiliary_assignments=exact_cases,exact_one_valid_lifts=valid_lifts,
        every_two_by_three_relation_assignment=relation_cases,all_shared_component_cap_truth_assignments=cap_cases,
        mask_channel_truth_assignments=channel_cases,corruptions_rejected=rejected,
        complete_research_factor_positive=None,complete_research_factor_positive_null_reason='No full factor is available; finite logical positives calibrate the encoding without fabricating a research witness.')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    start=time.monotonic();bindings={}
    def bind(path,h=None):
        value=digest(path);need(h is None or h==value,'exact artifact '+key(path));bindings[key(path)]=value;return path
    def read(path,h=None):return json.loads(bind(path,h).read_bytes())
    try:
        summary=read(DATA/'summary.json',PINS['summary.json']);model=read(DATA/'model.json',PINS['model.json']);scope=read(DATA/'scope.json',PINS['scope.json'])
        manifest=read(DATA/'manifest.json');gate=read(GATE,GATE_SHA)
        same(gate['status'],'INDEPENDENT_SIX_PRISM_COARSE60_LOCAL_DOMAINS_PASS','prior domain audit status')
        for p,h in gate['inputs_sha256'].items():bind(ROOT/p,h)
        for p,h in summary['inputs_sha256'].items():bind(ROOT/p,h)
        for p,h in summary['outputs_sha256'].items():bind(ROOT/p,h)
        same(digest(Path(local.__file__)),'d3bdd6d650fd158d61961d7cdbed07728943881a9b65f7ce8b8d41d708223e03','frozen independently authored geometry helper')
        raw=read(DOMAIN/'coarse_template.json');old=read(ROOT/'acceleration/results/20260930_prism_unpaired_design_pilot/model.json')
        words,adjacency,gram=local.check_template(raw,old)
        expected_scope=dict(schema='FIXED_SIX_PRISM_DISTINCT60_BITLIFT_SCOPE_V1',columns60=list(map(list,words)),core_adjacency39=adjacency,target_gram36=gram,
            columns_each_once=True,coordinate_bits_free=True,full_Gram_required=True,all_distinct_column_caps_required=True,
            source_template_path=key(DOMAIN/'coarse_template.json'),source_template_sha256=digest(DOMAIN/'coarse_template.json'),
            canonical_C0_not_prescribed=True,no_complement_pairing=True,no_target_automorphism_assumed=True,residual_D_encoded=False,
            target_graph_encoded=False,unrestricted_prism_coverage=False)
        same(scope,expected_scope,'entire exact fixed template scope')
        for field,value in [('schema','SIX_PRISM_COARSE60_DOMAIN_CSP_CNF_V1'),('variables',5238),('clauses',85698),('domain_selectors',2448),
                            ('scope_sha256',PINS['scope.json']),('local_domain_gate',key(GATE)),('local_domain_gate_sha256',GATE_SHA),
                            ('complete_target_graph',False),('residual_D_encoded',False)]:same(model[field],value,'model '+field)
        expected_bits=[dict(variable=2449+6*d+a,column=d,component=a,fibre=words[d][a]) for d in range(60) for a in range(6)]
        same(model['raw_bits'],expected_bits,'all360 literal bit coordinates')
        domains=[];supports=[]
        for a,g in product(range(6),range(3)):
            path=DOMAIN/f'domain_{a}_{g}.json';d=read(path);positions=d['column_positions'];masks=d['survivors']
            same(gate['inputs_sha256'][key(path)],digest(path),'every exact independently enumerated domain')
            sets=[frozenset(col for i,col in enumerate(positions) if mask>>i&1) for mask in masks]
            expected=dict(component=a,fibre=g,source_path=key(path),source_sha256=digest(path),column_positions=positions,
                selectors=list(range(1+(3*a+g)*136,1+(3*a+g+1)*136)),local_masks=masks,
                global_bit1_masks_hex=[format(sum(2**col for col in ones),'015x') for ones in sets])
            domains.append(expected);supports.append(sets)
        same(model['domains'],domains,'all selector mappings and literal local-to-global supports')
        calibration=controls();rejected=calibration['corruptions_rejected']
        for name,actual,expected in [('wrong_scope',dict(scope,target_graph_encoded=True),expected_scope),
                ('changed_bit_coordinate',[dict(expected_bits[0],component=5),*expected_bits[1:]],expected_bits),
                ('changed_domain_hash',[dict(domains[0],source_sha256='0'*64),*domains[1:]],domains),
                ('duplicate_selector',[dict(domains[0],selectors=[1]*136),*domains[1:]],domains)]:
            try:same(actual,expected,name)
            except ValueError:rejected.append(name)
            else:raise ValueError('metadata corruption accepted '+name)
        seen=0;sections=[];expected_prefix=[];expected_relations=[];expected_caps=[];cnf_hash=sha256();body_hash=sha256();sample_lines={}
        with (DATA/'instance.cnf').open('rb') as cnf:
            header=b'p cnf 5238 85698\n';same(cnf.readline(),header,'exact DIMACS header');cnf_hash.update(header)
            def emit(clause):
                nonlocal seen
                need(clause and all(type(x)is int and 1<=abs(x)<=5238 for x in clause),'well formed exact expected clause')
                expected=line(clause);same(cnf.readline(),expected,'complete actual clause '+str(seen+1));seen+=1
                cnf_hash.update(expected);body_hash.update(expected)
                if seen in (1,9739,58699,77059,85698):sample_lines[str(seen)]=expected.decode('ascii')
            def section(kind,first):sections.append(dict(kind=kind,first_clause=first,last_clause=seen,count=seen-first+1))
            top=2808;first=seen+1
            for i,domain in enumerate(domains):
                rows=[];previous=domain['selectors'][0]
                for selector in domain['selectors'][1:]:
                    top+=1;current=top
                    for clause in [[-previous,current],[-selector,current],[previous,selector,-current],[-previous,-selector]]:emit(clause)
                    rows.append(dict(variable=current,previous=previous,selector=selector));previous=current
                emit([previous]);expected_prefix.append(dict(domain=i,prefixes=rows,final_unit=previous))
            section('exactly_one',first);same(top,5238,'all2430 unique prefix variables');same(model['exact_one_prefixes'],expected_prefix,'all prefix DAG mappings')
            first=seen+1
            for i,domain in enumerate(domains):
                a=domain['component']
                for choice,ones in enumerate(supports[i]):
                    for d in domain['column_positions']:emit([-domain['selectors'][choice],(2449+6*d+a)*(1 if d in ones else -1)])
            section('selected_mask_bit_channels',first)
            first=seen+1;allowed_total=0
            for a,b in combinations(range(6),2):
                for g,h in product(range(3),repeat=2):
                    left,right=3*a+g,3*b+h;target=1 if g==h else 2
                    same(gram[12*g+2*a+1][12*h+2*b+1],target,'literal raw Gram pair target')
                    first_relation=seen+1;rows=[];counts=[]
                    for i,ones in enumerate(supports[left]):
                        # Set intersections use independent literal column coordinates,
                        # not the producer's global integer bitset/popcount method.
                        indices=[j for j,other in enumerate(supports[right]) if len(ones.intersection(other))==target]
                        emit([-domains[left]['selectors'][i],*[domains[right]['selectors'][j] for j in indices]])
                        rows.append(format(sum(2**j for j in indices),'034x'));counts.append(len(indices))
                    allowed_total+=sum(counts)
                    expected_relations.append(dict(left_domain=left,right_domain=right,target_bit11=target,allowed_right_masks_hex=rows,
                        row_allowed_counts=counts,allowed_pairs=sum(counts),forbidden_pairs=136**2-sum(counts),first_clause=first_relation,last_clause=seen))
            section('all135_Gram_compatibility_relations',first);same(model['Gram_relations'],expected_relations,'all2496960 compatibility outcomes and all relation intervals')
            first=seen+1;hist=Counter()
            for d,e in combinations(range(60),2):
                shared=[a for a in range(6) if words[d][a]==words[e][a]];hist[len(shared)]+=1
                triples=list(combinations(shared,3));first_cap=seen+1
                for triple in triples:
                    for common in product((0,1),repeat=3):
                        emit([(2449+6*col+a)*(-1 if bit else 1) for a,bit in zip(triple,common) for col in (d,e)])
                expected_caps.append(dict(columns=[d,e],same_fibre_components=shared,triples=list(map(list,triples)),
                    first_clause=first_cap if triples else None,last_clause=seen if triples else None,clause_count=8*len(triples)))
            section('all1770_required_Y_caps',first);same(model['column_caps'],expected_caps,'all1770 cap scopes and every component triple')
            same(cnf.read(),b'','no extra clauses/units/trailing bytes')
        same(model['clause_sections'],sections,'all exact section boundaries');same(model['same_fibre_component_histogram'],{str(k):v for k,v in sorted(hist.items())},'complete cap histogram')
        same(seen,85698,'full clause coverage');same(cnf_hash.hexdigest(),PINS['instance.cnf'],'independent reconstructed complete CNF hash')
        same(body_hash.hexdigest(),digest(DATA/'clauses.body'),'independent complete raw body identity')
        same([x['count'] for x in sections],[9738,48960,18360,8640],'derived clause inventory')
        same((summary['variables'],summary['clauses'],summary['compatibility_allowed_pairs'],summary['compatibility_forbidden_pairs']),(5238,85698,allowed_total,135*136**2-allowed_total),'exact producer inventory')
        # Adversarial checks on actual bound maps and actual reconstructed clause bytes.
        for name,actual,expected in [('missing_compatibility',expected_relations[:-1],expected_relations),
                ('missing_cap_triple',[dict(expected_caps[0],triples=[]),*expected_caps[1:]],expected_caps),
                ('changed_prefix',[dict(expected_prefix[0],final_unit=1),*expected_prefix[1:]],expected_prefix)]:
            try:same(actual,expected,name)
            except ValueError:rejected.append(name)
            else:raise ValueError('actual mapping corruption accepted')
        for number,text in sample_lines.items():
            clause=[int(x) for x in text.split()[:-1]];clause[0]*=-1
            try:same(line(clause),text.encode('ascii'),'actual clause sign flip')
            except ValueError:rejected.append('actual_clause_'+number+'_sign_flip')
            else:raise ValueError('actual clause corruption accepted')
        save(args.out/'controls.json',calibration)
        save(args.out/'complete_inventory.json',dict(variables=5238,clauses=seen,sections=sections,selector_variables=2448,bit_variables=360,prefix_variables=2430,
            compatibility_pairs=135*136**2,allowed=allowed_total,forbidden=135*136**2-allowed_total,
            shared_component_histogram=dict(sorted(hist.items())),reconstructed_cnf_sha256=cnf_hash.hexdigest(),reconstructed_body_sha256=body_hash.hexdigest(),actual_clause_samples=sample_lines))
        for path in [Path(__file__),Path(local.__file__),DOC,ROOT/'uv.lock',ROOT/'pyproject.toml']:bind(path)
        need(all(digest(ROOT/p)==h for p,h in bindings.items()),'all frozen audit inputs remain unchanged')
        now=stamp();report=dict(status='INDEPENDENT_SIX_PRISM_COARSE60_BITLIFT_CNF_PASS',
            claim_id='C-SIX-PRISM-COARSE60-EXACT-BITLIFT-CNF',claim_revision=1,
            statement='The exact5238-variable85698-clause formula is satisfiable if and only if the frozen60distinct coarse columns of the fixed six-prism core admit binary coordinate bits producing the complete prescribed36x36integer Gram and all1770distinct-column overlap caps at most2.',
            kind='encoding',basis=['DERIVED','COMPUTED'],recommendation='VERIFIED',review_state='CLEAR',
            scope='Exact equivalence for one specified60-pattern fixed-core family; arbitrary bits and no symmetry fixing, residual D, full99adjacency or all-template coverage.',
            dependencies=[dict(id='C-SIX-PRISM-COMPLEMENT60-SINGLE-ROW-DOMAINS',revision=1,relation='encoding_equivalence'),
                dict(id='C-SIX-PRISM-COMPLETE-COLUMN-FACTOR-CNF',revision=1,relation='verification_dependency')],
            assumptions=['Fixed literal six-prism core and exact60coarse patterns, each once.','The independently checked local lists are complete for their prescribed single-row marginals.','No target automorphism assumption.'],
            verifier='/root/eight_domain_audit independently reconstructed whole CNF and logical equivalence',method='independent_artifact_check_and_derivation',
            shared_components=['Reuses the reviewer\'s frozen independent coarse-domain geometry helper. No producer encoding, popcount relation computation or SAT solver imported.',
                'Uses the prior independent complete local-domain audit as an explicit premise; does not relabel producer agreement as another independent enumeration.'],
            written_audit=key(DOC),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),
            uv_version=subprocess.check_output(['uv','--version'],text=True).strip(),inputs_sha256=bindings,
            exact_variables=5238,clauses_completely_reconstructed=seen,domain_pairs=135,compatibility_pairs_completely_checked=135*136**2,
            compatibility_allowed_pairs=allowed_total,column_pairs_completely_checked=1770,column_cap_clauses=8640,
            controls=calibration,producer_source_commit=manifest['source_commit'],producer_command=manifest['command'],
            limitations=['A full factor with column caps is not a99-vertex SRG; residual and mixed completion conditions remain.',
                'No real satisfying factor or proof artifact was supplied or approved by this encoding audit.',
                'No blanket source approval, solver result, fixed-core exclusion or unrestricted target coverage.'],
            outputs_sha256={key(p):digest(p) for p in args.out.iterdir() if p.is_file()},created_at=now,updated_at=now,
            elapsed_seconds=time.monotonic()-start,artifact_availability='LOCAL_ONLY',target_resolution=False,external_review=False)
        save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))
    except BaseException as error:save(args.out/'failure.json',dict(timestamp=stamp(),error=repr(error)));raise

if __name__=='__main__':main()
