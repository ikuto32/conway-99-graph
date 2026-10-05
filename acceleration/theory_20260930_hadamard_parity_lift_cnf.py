"""Exact candidate color lift of one authenticated parity assignment; no solver."""
from collections import Counter
from datetime import datetime, timezone
from importlib.metadata import version
from itertools import combinations, permutations, product
from pathlib import Path
import argparse
import json
import platform
import shutil
import subprocess
import sys
import time
from tqdm import tqdm
from theory_20260930_eight_full99_cnf import Clauses, Encoder, ResourceCap, counter_controls, digest, package, save

ROOT = Path(__file__).resolve().parents[1]
DEFAULT = ROOT / 'acceleration/results/20260930_hadamard_parity_lift_cnf'
PREFIX = 'acceleration/results/'
PINS = {
    PREFIX+'20260930_hadamard20_support/six_prism.json': 'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',
    PREFIX+'20260930_independent_review/hadamard20_support_v2/summary.json': 'a8477256446e3e402a2a21241dc383a515162dc9c8c07a9a8e26326c07b0f58f',
    PREFIX+'20260930_hadamard_triplicate_counts/local_triples.json': '9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',
    PREFIX+'20260930_independent_review/hadamard_triplicate_counts_v2/summary.json': 'cb9f1c7f8cfe0db557f554ded5427a9cba46dda10dcd9b5df9968e1d3b776f88',
    PREFIX+'20260930_independent_review/hadamard_six_prism_column_order/groups.json': 'a3d8366a607bfd10787d4e879f8971c84ba5835b2b22c71ebfd081f55352f404',
    PREFIX+'20260930_independent_review/hadamard_six_prism_column_order/summary.json': '0ce1be9ca11a3e860aa97791cfb4f42c1660d937a69ac7a9b7d96ca37640c9d2',
    PREFIX+'20260930_hadamard_balanced_parity_native_pilot/main/decoded_projection.json': '0e80251a964330092d8da9030df2e2ee7f56476cee9e588be921dbe2f470e646',
    PREFIX+'20260930_independent_review/hadamard_balanced_parity_sat_v2/summary.json': 'd2536119ac3fa0d45c190a6562de2ccc67c3f9c9765fbfc03257e37b15097f9c',
    PREFIX+'20260930_independent_review/hadamard_parity_object_v2_delta/summary.json': '599b7b2f713124e658ce0a7c3b06be0d0a79f170a5fb9fed45531eb5aec914b5',
    'acceleration/theory_20260930_eight_full99_cnf.py': '21c357543c9397456a911175b277da6e6caa769be31d18c12e034cc76d99074c',
    'acceleration/theory_20260930_full_srg_validator.py': 'c0e070aa1ac39e8860b52a7f5e086b3e8da5e01f83d0f4fe76ab1e91c077279b',
    'uv.lock': 'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',
    'pyproject.toml': '273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339',
}

def need(ok, why):
    if not ok:
        raise ValueError(why)

def key(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()

def read(path):
    return json.loads(Path(path).read_bytes())

def load(suffix):
    return read(ROOT / (PREFIX+suffix))

def pattern(words):
    need(len(words)==3 and all(len(w)==6 for w in words), 'three six-letter words')
    signs=[]
    for k in range(6):
        p=[w[k] for w in words]
        need(sorted(p)==[0,1,2], 'balanced coordinate permutations')
        signs.append(sum(p[a]>p[b] for a,b in combinations(range(3),2)) % 2)
    return [s ^ signs[0] for s in signs]

def local_rows(coords, words):
    need(len(coords)==len(set(coords))==6, 'six distinct coordinates')
    need(all(sorted(w)==[0,0,1,1,2,2] for w in words), 'two colors each')
    pattern(words)
    rows=[sorted(12*g+a for a,g in zip(coords,w,strict=True)) for w in words]
    need(all(not set(a)&set(b) for a,b in combinations(rows,2)), 'within-block disjointness')
    return rows

def prepare(raw, local, groups, projection):
    m=[a^1 for a in range(12)]
    need(raw['matchings']==[m,m,m], 'fixed six-prism matchings')
    words=local['words'];triples=local['balanced']
    need(words==[list(w) for w in product(range(3),repeat=6) if all(w.count(g)==2 for g in range(3))], 'all90 ordered words')
    need(len(triples)==len({tuple(t) for t in triples})==150, '150 unique balanced triples')
    need(all(t==sorted(t) and len(set(t))==3 for t in triples), 'strict word ordering')
    patterns=[pattern([words[j] for j in t]) for t in triples]
    counts=Counter(tuple(p) for p in patterns)
    need(len(counts)==11 and sorted(counts.values())==[12]*10+[30], 'complete normalized pattern fibers')
    transports=0
    for t,p in zip(triples,patterns,strict=True):
        for perm in permutations(range(3)):
            need(pattern([words[t[i]] for i in perm])==p, 'column permutation gauge invariance')
            transports+=1
    selected=projection['selected_group_parity_patterns']
    need(len(selected)==20 and sum(any(p) for p in selected)==16, 'selected16mixed4constant')
    domains=[];next_id=1
    for record,p in zip(groups,selected,strict=True):
        group=record['group'];coords=record['support'];columns=record['columns']
        need(group==len(domains) and columns==sorted(columns), 'canonical group ordering')
        need(all(raw['support_columns'][d]==coords for d in columns), 'raw support alignment')
        choices=[]
        for original_index,(triple,parity) in enumerate(zip(triples,patterns,strict=True)):
            if parity != p:
                continue
            rows=local_rows(coords,[words[j] for j in triple])
            choices.append(dict(selector=next_id,choice_index=len(choices),balanced_triple_index=original_index,
                word_indices=triple,color_words=[words[j] for j in triple],lifted_rows=rows,
                lifted_masks_hex=[format(sum(1<<i for i in r),'09x') for r in rows]))
            next_id+=1
        need(len(choices)==(12 if any(p) else 30), 'exact selected pattern fiber size')
        domains.append(dict(group=group,support_coordinates=coords,raw_columns=columns,selected_parity_pattern=p,choices=choices))
    need(next_id==313, '312 primary selectors')
    failures=[]
    for name,coords,badwords in [
        ('duplicate_coordinate',[0,0,4,6,8,10],[words[j] for j in triples[0]]),
        ('duplicate_word',[0,2,4,6,8,10],[words[triples[0][0]]]*3),
        ('unbalanced_word',[0,2,4,6,8,10],[[0]*6,words[triples[0][1]],words[triples[0][2]]])]:
        try:
            local_rows(coords,badwords)
        except ValueError:
            failures.append(name)
        else:
            raise AssertionError('corruption accepted: '+name)
    controls=dict(normalized_pattern_fiber_counts=[dict(pattern=list(p),count=n) for p,n in sorted(counts.items())],
        complete150_local_positive_controls=True,common_column_permutation_controls=transports,
        corrupted_local_objects_rejected=failures,selected_domain_sizes=[len(d['choices']) for d in domains],
        complete_research_factor_positive=None,complete_research_factor_positive_reason='Local controls do not establish any joint36x60 factor.')
    return domains,controls

def build(out):
    out.mkdir(parents=True,exist_ok=False);cap=ResourceCap();cap.check()
    created=datetime.now(timezone.utc).isoformat()
    try:
        need(all(digest(ROOT/p)==h for p,h in PINS.items()), 'all frozen input hashes')
        actual=load('20260930_independent_review/hadamard_balanced_parity_sat_v2/summary.json')
        need(actual['status']=='INDEPENDENT_HADAMARD_BALANCED_PARITY_SAT_OBJECT_PASS', 'actual parity SAT gate')
        projection_key=PREFIX+'20260930_hadamard_balanced_parity_native_pilot/main/decoded_projection.json'
        need(actual['inputs_sha256'][projection_key]==PINS[projection_key], 'raw projection directly gate-bound')
        need(load('20260930_independent_review/hadamard_parity_object_v2_delta/summary.json')['status']=='INDEPENDENT_HADAMARD_PARITY_OBJECT_V2_DELTA_AND_CALIBRATION_PASS','corrected checker review')
        pins={**PINS,key(__file__):digest(__file__),key(Path(__file__).with_name('theory_20260930_hadamard_parity_lift_cnf_spec.md')):digest(Path(__file__).with_name('theory_20260930_hadamard_parity_lift_cnf_spec.md'))}
        save(out/'manifest.json',dict(created_at=created,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            command=[sys.executable,*sys.argv],working_directory=str(ROOT),inputs_sha256=pins,
            versions=dict(python=platform.python_version(),uv=subprocess.check_output(['uv','--version'],text=True).strip(),tqdm=version('tqdm')),
            selection='First saved independently checked parity SAT assignment; no score-based selection.',
            limits=dict(build_seconds=120,memory_bytes=8*1024**3,solver_calls=0),numerical_acceptance_threshold=None,
            numerical_acceptance_threshold_reason='Only exact integer construction; no optimizer invocation.',target_automorphism_assumed=False))
        raw=load('20260930_hadamard20_support/six_prism.json');local=load('20260930_hadamard_triplicate_counts/local_triples.json')
        groups=load('20260930_independent_review/hadamard_six_prism_column_order/groups.json')['groups']
        projection=read(ROOT/projection_key);domains,local_control=prepare(raw,local,groups,projection)
        save(out/'local_controls.json',local_control);save(out/'counter_controls.json',counter_controls())
        scope=dict(schema='FIXED_HADAMARD_SINGLE_PARITY_BALANCED_LIFT_SCOPE_V1',raw_support=PREFIX+'20260930_hadamard20_support/six_prism.json',
            raw_support_sha256=PINS[PREFIX+'20260930_hadamard20_support/six_prism.json'],parity_projection=projection_key,parity_projection_sha256=PINS[projection_key],
            matchings=raw['matchings'],core_adjacency=raw['core_adjacency'],target_gram36=raw['prescribed_Gram36'],L=raw['L'],domains=domains,
            selected_pattern_indices=projection['selected_pattern_indices'],balanced_group_columns=True,
            one_fixed_parity_branch=True,all_balanced_branches_covered=False,arbitrary_fixedL_factors_covered=False,
            column_word_order='Strictly increasing word indices along the ascending three raw columns of each identical-support group.',
            residual_D_encoded=False,target_graph=False,no_target_automorphism_assumed=True)
        save(out/'scope.json',scope)
        gram_rows=[]
        for i in range(36):
            for j in range(i,36):
                terms=[]
                for d in domains:
                    for choice in d['choices']:
                        count=sum(i in r and j in r for r in choice['lifted_rows'])
                        need(count in (0,1), 'binary Gram block coefficient')
                        if count:terms.append(choice['selector'])
                gram_rows.append(dict(rows=[i,j],target=scope['target_gram36'][i][j],inputs=terms))
        need(len(gram_rows)==666, 'all upper Gram entries')
        nontrivial=[r for r in gram_rows if r['rows'][0]!=r['rows'][1] and r['target']>0]
        need(len(nontrivial)==540 and all(r['target'] in (1,2) for r in nontrivial), '540 nontrivial Gram rows')
        lp_rows=[dict(kind='group_exactone',group=d['group'],inputs=[c['selector'] for c in d['choices']],target=1) for d in domains]
        lp_rows.extend(dict(kind='gram_count',**r) for r in nontrivial)
        lp_columns=[[] for _ in range(312)]
        for row_index,row in enumerate(lp_rows):
            for v in row['inputs']:lp_columns[v-1].append(row_index)
        save(out/'exact_model.json',dict(nonnegative_variables=True,columns_nonzero_row_indices=lp_columns,rhs=[r['target'] for r in lp_rows],
            selectors=[[d['group'],c['choice_index']] for d in domains for c in d['choices']],variables=312,equations=560,binary_coefficients=True,
            row_metadata=lp_rows,scope_sha256=digest(out/'scope.json'),omitted_constraints=['selector integrality','all inter-group outside-column caps'],
            relaxation_only=True,independent_approval=False))
        counterrows=[];sections=[];caps=[];pairchecks=0;all9checks=0
        with (out/'clauses.body').open('xb') as body:
            clauses=Clauses(body,cap);enc=Encoder(312,clauses);first=clauses.count+1
            for d in domains:
                counterrows.append(enc.counter([c['selector'] for c in d['choices']],1,True,dict(kind='group_exactone',group=d['group'])))
            sections.append(dict(kind='20group_exactone',first_clause=first,last_clause=clauses.count,count=clauses.count-first+1));first=clauses.count+1
            for r in gram_rows:
                counterrows.append(enc.counter(r['inputs'],r['target'],True,dict(kind='gram_count',rows=r['rows'])))
            sections.append(dict(kind='666exact_Gram_counts',first_clause=first,last_clause=clauses.count,count=clauses.count-first+1));first=clauses.count+1
            for p,q in tqdm(list(combinations(range(20),2)),desc='Fixed parity lift cap relations'):
                cap.check();begin=clauses.count+1;forbidden=[];hist=Counter()
                for x in domains[p]['choices']:
                    xs=[int(v,16) for v in x['lifted_masks_hex']];mask=0
                    for j,y in enumerate(domains[q]['choices']):
                        ys=[int(v,16) for v in y['lifted_masks_hex']];overlaps=[(a&b).bit_count() for a in xs for b in ys]
                        maximum=max(overlaps);hist[maximum]+=1;pairchecks+=1;all9checks+=9
                        if maximum>2:clauses.emit(-x['selector'],-y['selector']);mask|=1<<j
                    forbidden.append(format(mask,'x'))
                caps.append(dict(groups=[p,q],actual_column_pairs=[[d,e] for d in domains[p]['raw_columns'] for e in domains[q]['raw_columns']],
                    forbidden_right_masks_hex=forbidden,maximum_overlap_histogram=dict(sorted(hist.items())),first_clause=begin,clause_count=clauses.count-begin+1))
            sections.append(dict(kind='190lifted_cap_choice_relations',first_clause=first,last_clause=clauses.count,count=clauses.count-first+1))
        with (out/'instance.cnf').open('xb') as dest,(out/'clauses.body').open('rb') as source:
            dest.write(f'p cnf {enc.top} {clauses.count}\n'.encode());shutil.copyfileobj(source,dest,1048576)
        model=dict(schema='HADAMARD_SINGLE_PARITY_BALANCED_LIFT_PREFIX_CNF_V1',variables=enc.top,clauses=clauses.count,primary_selectors=312,
            scope_path=key(out/'scope.json'),scope_sha256=digest(out/'scope.json'),domains=domains,counter_rows=counterrows,lifted_cap_relations=caps,clause_sections=sections,
            full_target_encoded=False,counter_prefix_reference_format='JSON Boolean constants; positive integer variable IDs.',
            counter_gate_order=dict(and_gate=['a -z','b -z','-a -b z'],or_gate=['-a z','-b z','a b -z'],recurrence=['-a z','-b -c z','a b -z','a c -z']))
        save(out/'model.json',model);cap.check()
        save(out/'artifact_packages.json',dict(packages=[package(p,cap) for p in [out/'instance.cnf',out/'clauses.body',out/'model.json']],mathematical_verification=False))
        need(all(digest(ROOT/p)==h for p,h in pins.items()), 'inputs unchanged')
        summary=dict(status='CANDIDATE_SINGLE_PARITY_BALANCED_LIFT_CNF',created_at=created,completed_at=datetime.now(timezone.utc).isoformat(),inputs_sha256=pins,
            outputs_sha256={key(p):digest(p) for p in out.iterdir() if p.is_file()},variables=enc.top,clauses=clauses.count,primary_selectors=312,
            domains=20,domain_sizes=[len(d['choices']) for d in domains],onehot_rows=20,gram_equalities=666,lp_equations=560,lp_variables=312,
            group_pair_choice_checks=pairchecks,lifted_column_pair_checks=all9checks,actual_column_pairs_covered=1770,withintriplet_disjoint_pairs=60,
            forbidden_choice_pairs=sum(r['clause_count'] for r in caps),clause_sections=sections,wall_seconds=time.monotonic()-cap.start,peak_memory_bytes=cap.peak_bytes,
            solver_calls=0,independent_approval=False,target_resolution='UNKNOWN',scope='One selected parity branch of the extra balanced-triplet family on one fixed Hadamard six-prism support; D absent.')
        save(out/'summary.json',summary)
        print(json.dumps({k:v for k,v in summary.items() if k not in ['inputs_sha256','outputs_sha256']}))
    except BaseException as error:
        save(out/'failure.json',dict(exception=repr(error),elapsed_seconds=time.monotonic()-cap.start,mathematical_exclusion=False));raise

def decode(assignment,model_path=DEFAULT/'model.json',scope_path=DEFAULT/'scope.json'):
    model=read(model_path);scope=read(scope_path);need(digest(scope_path)==model['scope_sha256'],'scope pin')
    values={}
    for v in assignment:
        need(type(v)is int and v and abs(v) not in values,'unique integer literals');values[abs(v)]=v>0
    need(set(values)==set(range(1,model['variables']+1)), 'complete assignment')
    factor=[[0]*60 for _ in range(36)];selected=[];records=[]
    for domain in model['domains']:
        options=[x for x in domain['choices'] if values[x['selector']]];need(len(options)==1,'exact one group choice');choice=options[0]
        need(pattern(choice['color_words'])==domain['selected_parity_pattern'], 'selected parity branch')
        selected.append(choice['selector']);records.append(dict(group=domain['group'],selector=choice['selector'],word_indices=choice['word_indices'],balanced_triple_index=choice['balanced_triple_index']))
        for d,rows in zip(domain['raw_columns'],choice['lifted_rows'],strict=True):
            for i in rows:factor[i][d]=1
    need(all(sum(factor[i][d]*factor[j][d] for d in range(60))==scope['target_gram36'][i][j] for i in range(36) for j in range(36)), 'all1296 exact Gram entries')
    need(all(sum(factor[12*g+a][d] for g in range(3))==scope['L'][a][d] for a in range(12) for d in range(60)), 'exact support projection')
    need(all(sum(factor[12*g+a][d] for a in range(12))==2 for g in range(3) for d in range(60)), 'two per fibre')
    need(all(sum(factor[i][d]*factor[i][e] for i in range(36))<=2 for d,e in combinations(range(60),2)), 'all1770 outside caps')
    need(all(factor[i][d]+sum(scope['core_adjacency'][i][j]*factor[j][d] for j in range(36))<=2 for i in range(36) for d in range(60)), 'all2160 mixed caps')
    pairs=[tuple(i for i in range(12) if factor[i][d]) for d in range(60)];catalog=[p for p in combinations(range(12),2) if p[1]!=(p[0]^1)]
    need(sorted(pairs)==catalog, 'complete C0 edge catalog');order=[pairs.index(p) for p in catalog]
    return dict(factor=factor,L=scope['L'],selected_selector_ids=selected,group_records=records,core_adjacency=scope['core_adjacency'],matchings=scope['matchings'],
        M0=scope['matchings'][0],M1=scope['matchings'][1],M2=scope['matchings'][2],P=list(range(12)),target_gram36=scope['target_gram36'],
        canonical_factor=[[row[d] for d in order] for row in factor],canonical_column_order=order,canonical_C0_columns=[list(p) for p in catalog],
        scope_sha256=digest(scope_path),model_sha256=digest(model_path),one_fixed_parity_branch=True,balanced_group_columns=True,
        residual_D=None,residual_D_reason='No residual adjacency is encoded or constructed.',target_graph=False,independent_approval=False)

def main():
    parser=argparse.ArgumentParser();sub=parser.add_subparsers(dest='mode',required=True)
    b=sub.add_parser('build');b.add_argument('--out',type=Path,required=True)
    d=sub.add_parser('decode');d.add_argument('--assignment',type=Path,required=True);d.add_argument('--model',type=Path,default=DEFAULT/'model.json');d.add_argument('--scope',type=Path,default=DEFAULT/'scope.json');d.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    if args.mode=='build':build(args.out.resolve())
    else:
        value=read(args.assignment);save(args.out,decode(value if type(value)is list else value.get('assignment',value.get('model')),args.model,args.scope))

if __name__=='__main__':main()
