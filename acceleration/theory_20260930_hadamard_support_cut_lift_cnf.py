"""Fresh exact CNF for the 240-choice support-cut-selected parity lift; no SAT."""
from collections import Counter
from datetime import datetime,timezone
from importlib.metadata import version
from itertools import combinations,product
from pathlib import Path
import argparse,json,platform,shutil,subprocess,sys,time
from tqdm import tqdm
from theory_20260930_eight_full99_cnf import Clauses,Encoder,ResourceCap,counter_controls,digest,package,save

ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_';BASE=ROOT/(B+'hadamard_support_cut_lift_matrix')
DEFAULT=ROOT/(B+'hadamard_support_cut_lift_cnf')
PINS={B+'hadamard_support_cut_lift_matrix/scope.json':'9c4723d00e7788b1aea471c604b9d7e4b38545da83ce0467e4e6c0b71642715a',
 B+'hadamard_support_cut_lift_matrix/exact_model.json':'cdedc77904ba8cfc8b3a12d1da876cd55c87e85fd85427caf6c2d766715b493b',
 'acceleration/theory_20260930_hadamard_support_cut_lift_matrix.py':'e80ddaef90a8864b9dab8987e7503bae8df0a893f6103984081c1ef9f132ba75',
 'acceleration/theory_20260930_hadamard_support_cut_lift_matrix_spec.md':'773ada15794b9ace867257cf90eef6f695c8427c81c4d081bcb0f67e71156a32',
 B+'independent_review/hadamard_parity_support_cuts_sat/summary.json':'02ae20d479a0d2589c02f435e2a8fdd781ec0459b60095d130b68b5f2721a04a',
 'acceleration/theory_20260930_eight_full99_cnf.py':'21c357543c9397456a911175b277da6e6caa769be31d18c12e034cc76d99074c',
 'acceleration/theory_20260930_full_srg_validator.py':'c0e070aa1ac39e8860b52a7f5e086b3e8da5e01f83d0f4fe76ab1e91c077279b',
 'uv.lock':'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',
 'pyproject.toml':'273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339'}
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(Path(p).read_bytes())
def need(ok,why):
    if not ok:raise ValueError(why)
def count_exact(enc,inputs,bound,annotation):
    need(type(bound)is int and len(inputs)==len(set(inputs))and all(type(x)is int and x>0 for x in inputs),'counter input types')
    if bound<0 or bound>len(inputs):
        first=enc.clauses.count+1;enc.clauses.emit()
        return dict(**annotation,encoding_case='impossible_bound',inputs=inputs,bound=bound,equality=True,states=[],
            first_auxiliary_variable=None,last_auxiliary_variable=None,auxiliary_null_reason='Impossible cardinality emits an empty clause without auxiliary variables.',
            first_clause=first,clause_count=1)
    return dict(encoding_case='prefix_threshold',**enc.counter(inputs,bound,True,annotation))
def controls():
    ordinary=counter_controls();bad=[]
    for n in range(5):
        for bound in(-1,n+1):
            clauses=Clauses();enc=Encoder(n,clauses);row=count_exact(enc,list(range(1,n+1)),bound,{})
            need(clauses.rows==[[]]and enc.top==n and row['encoding_case']=='impossible_bound','exact impossible cardinality')
            for bits in product((False,True),repeat=n):
                need(not all(any(bits[abs(v)-1]==(v>0)for v in clause)for clause in clauses.rows),'impossible input rejected')
            corrupted=[]
            need(all(any(False for _ in c)for c in corrupted),'missing empty clause is falsified by satisfiable corrupt formula')
            bad.append(dict(n=n,bound=bound,clauses=clauses.rows,corrupt_missing_clause_detected=True))
    clauses=Clauses();enc=Encoder(0,clauses);count_exact(enc,[],0,{})
    need(clauses.rows==[]and enc.top==0,'empty exactzero is true')
    return dict(status='PRODUCER_EXTENDED_COUNTER_CONTROLS_PASS',inherited=ordinary,impossible_cases=bad,empty_exactzero_positive=True,independent_review=False)
def build(out):
    out.mkdir(parents=True,exist_ok=False);cap=ResourceCap()
    try:
        need(all(digest(ROOT/p)==h for p,h in PINS.items()),'pinned raw inputs')
        scope=read(BASE/'scope.json');domains=scope['domains'];need(len(domains)==20 and all(len(d['choices'])==12 for d in domains),'20 complete12-option domains')
        need([c['selector']for d in domains for c in d['choices']]==list(range(1,241)),'exact240ID mapping')
        gate=read(ROOT/(B+'independent_review/hadamard_parity_support_cuts_sat/summary.json'))
        need(gate['status']=='INDEPENDENT_HADAMARD_PARITY_SUPPORT_CUT_SAT_OBJECT_PASS','new parity SAT gate')
        pins={**PINS,key(__file__):digest(__file__),key(Path(__file__).with_name('theory_20260930_hadamard_support_cut_lift_cnf_spec.md')):digest(Path(__file__).with_name('theory_20260930_hadamard_support_cut_lift_cnf_spec.md'))}
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),uv=subprocess.check_output(['uv','--version'],text=True).strip(),tqdm=version('tqdm'),
            inputs_sha256=pins,limits=dict(wall_seconds=120,memory_bytes=8*1024**3,solver_calls=0),selection='All240 choices for the first checked support-cut parity SAT object; no further pattern normalization.',
            scope='One selected mixed parity branch of a fixed balanced Hadamard six-prism factor family; no residualD.',independent_approval=False))
        save(out/'counter_controls.json',controls());save(out/'scope.json',scope)
        rows=[]
        for i in range(36):
            for j in range(i,36):
                terms=[]
                for d in domains:
                    for c in d['choices']:
                        n=sum(i in r and j in r for r in c['lifted_rows']);need(n in(0,1),'binary local Gram coefficient')
                        if n:terms.append(c['selector'])
                rows.append(dict(rows=[i,j],target=scope['target_gram36'][i][j],inputs=terms))
        counterrows=[];sections=[];caps=[];option_pairs=0
        with(out/'clauses.body').open('xb')as body:
            clauses=Clauses(body,cap);enc=Encoder(240,clauses);start=clauses.count+1
            for d in domains:counterrows.append(count_exact(enc,[c['selector']for c in d['choices']],1,dict(kind='group_exactone',group=d['group'])))
            sections.append(dict(kind='20group_exactone',first_clause=start,last_clause=clauses.count,count=clauses.count-start+1));start=clauses.count+1
            for r in rows:counterrows.append(count_exact(enc,r['inputs'],r['target'],dict(kind='gram_count',rows=r['rows'])))
            sections.append(dict(kind='666exact_Gram_counts',first_clause=start,last_clause=clauses.count,count=clauses.count-start+1));start=clauses.count+1
            for p,q in tqdm(list(combinations(range(20),2)),desc='All240-lift intergroup cap relations'):
                cap.check();first=clauses.count+1;forbidden=[];hist=Counter()
                for x in domains[p]['choices']:
                    xs=[int(v,16)for v in x['lifted_masks_hex']];mask=0
                    for k,y in enumerate(domains[q]['choices']):
                        ys=[int(v,16)for v in y['lifted_masks_hex']];maximum=max((a&b).bit_count()for a in xs for b in ys);hist[maximum]+=1;option_pairs+=1
                        if maximum>2:clauses.emit(-x['selector'],-y['selector']);mask|=1<<k
                    forbidden.append(format(mask,'03x'))
                caps.append(dict(groups=[p,q],actual_column_pairs=[[d,e]for d in domains[p]['raw_columns']for e in domains[q]['raw_columns']],
                    forbidden_right_masks_hex=forbidden,maximum_overlap_histogram=dict(sorted(hist.items())),first_clause=first,clause_count=clauses.count-first+1))
            sections.append(dict(kind='190lifted_cap_relations',first_clause=start,last_clause=clauses.count,count=clauses.count-start+1))
        with(out/'instance.cnf').open('xb')as dest,(out/'clauses.body').open('rb')as source:
            dest.write(f'p cnf {enc.top} {clauses.count}\n'.encode());shutil.copyfileobj(source,dest,1048576)
        model=dict(schema='SUPPORT_CUT_SELECTED_PARITY_LIFT_PREFIX_CNF_V1',variables=enc.top,clauses=clauses.count,primary_selectors=240,
            scope_path=key(out/'scope.json'),scope_sha256=digest(out/'scope.json'),domains=domains,counter_rows=counterrows,lifted_cap_relations=caps,clause_sections=sections,
            full_target_encoded=False,counter_prefix_reference_format='JSON Boolean constants; positive integer variable IDs.',
            counter_gate_order=dict(and_gate=['a -z','b -z','-a -b z'],or_gate=['-a z','-b z','a b -z'],recurrence=['-a z','-b -c z','a b -z','a c -z']),
            impossible_counter_rule='If the integer bound is outside[0,len(inputs)], emit exactly one empty clause and no auxiliary variables.')
        save(out/'model.json',model);cap.check()
        save(out/'artifact_packages.json',dict(packages=[package(p,cap)for p in[out/'instance.cnf',out/'clauses.body',out/'model.json']],mathematical_verification=False))
        need(all(digest(ROOT/p)==h for p,h in pins.items()),'unchanged frozen inputs')
        summary=dict(status='CANDIDATE_SUPPORT_CUT_SELECTED_PARITY_LIFT_CNF',timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=pins,
            outputs_sha256={key(p):digest(p)for p in out.iterdir()if p.is_file()},variables=enc.top,clauses=clauses.count,primary_selectors=240,
            onehot_rows=20,gram_rows=666,impossible_bound_rows=sum(r['encoding_case']=='impossible_bound'for r in counterrows),
            group_pair_relations=190,option_pairs=option_pairs,literal_column_pair_checks=9*option_pairs,within_group_disjoint_pairs=60,
            actual_outside_column_pairs=1770,forbidden_option_pairs=sum(r['clause_count']for r in caps),clause_sections=sections,
            wall_seconds=time.monotonic()-cap.start,peak_memory_bytes=cap.peak_bytes,solver_calls=0,independent_approval=False,target_resolution='UNKNOWN')
        save(out/'summary.json',summary);print(json.dumps({k:v for k,v in summary.items()if k not in('inputs_sha256','outputs_sha256')}))
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),wall_seconds=time.monotonic()-cap.start,mathematical_exclusion=False));raise
def decode(assignment,model_path=DEFAULT/'model.json'):
    model=read(model_path);scope_path=ROOT/model['scope_path'];need(digest(scope_path)==model['scope_sha256'],'scope pin');scope=read(scope_path);values={}
    for literal in assignment:
        need(type(literal)is int and literal and abs(literal)not in values,'distinct nonzero native literals');values[abs(literal)]=literal>0
    need(set(values)==set(range(1,model['variables']+1)),'complete native assignment')
    factor=[[0]*60 for _ in range(36)];selected=[];records=[]
    for d in model['domains']:
        options=[c for c in d['choices']if values[c['selector']]];need(len(options)==1,'one selected local triple');c=options[0];selected.append(c['selector'])
        records.append(dict(group=d['group'],selector=c['selector'],choice_index=c['choice_index'],word_indices=c['word_indices'],selected_parity_pattern=d['selected_parity_pattern']))
        for column,rows in zip(d['raw_columns'],c['lifted_rows'],strict=True):
            for row in rows:factor[row][column]=1
    need(all(sum(factor[i][d]*factor[j][d]for d in range(60))==scope['target_gram36'][i][j]for i in range(36)for j in range(36)),'all1296 integer Gram entries')
    need(all(sum(factor[12*g+a][d]for g in range(3))==scope['L'][a][d]for a in range(12)for d in range(60)),'fixed projection')
    need(all(sum(factor[12*g+a][d]for a in range(12))==2 for g in range(3)for d in range(60)),'fibre column margins')
    need(all(sum(factor[i][d]*factor[i][e]for i in range(36))<=2 for d,e in combinations(range(60),2)),'all1770 column caps')
    need(all(factor[i][d]+sum(scope['core_adjacency'][i][j]*factor[j][d]for j in range(36))<=2 for i in range(36)for d in range(60)),'all2160 mixed caps')
    pairs=[tuple(i for i in range(12)if factor[i][d])for d in range(60)];catalog=[p for p in combinations(range(12),2)if p[1]!=(p[0]^1)]
    need(sorted(pairs)==catalog,'canonical C0 catalog');order=[pairs.index(p)for p in catalog]
    return dict(factor=factor,L=scope['L'],selected_selector_ids=selected,group_records=records,matchings=scope['matchings'],core_adjacency=scope['core_adjacency'],
        M0=scope['matchings'][0],M1=scope['matchings'][1],M2=scope['matchings'][2],P=list(range(12)),target_gram36=scope['target_gram36'],
        canonical_factor=[[r[d]for d in order]for r in factor],canonical_column_order=order,canonical_C0_columns=[list(p)for p in catalog],
        scope_sha256=digest(scope_path),model_sha256=digest(model_path),one_fixed_parity_branch=True,balance_is_additional_assumption=True,
        residual_D=None,residual_D_reason='No residual graph encoded or supplied.',target_graph=False,independent_approval=False)
def main():
    ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='mode',required=True);b=sub.add_parser('build');b.add_argument('--out',type=Path,required=True)
    d=sub.add_parser('decode');d.add_argument('--assignment',type=Path,required=True);d.add_argument('--model',type=Path,default=DEFAULT/'model.json');d.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    if a.mode=='build':build(a.out.resolve())
    else:
        v=read(a.assignment);save(a.out,decode(v if type(v)is list else v.get('assignment',v.get('model')),a.model))
if __name__=='__main__':main()
