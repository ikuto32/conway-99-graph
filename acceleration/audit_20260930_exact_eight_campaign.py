"""Independent all792 population and parameterized first12 encoding/object review.

Prepared source; batch contract is finalized before first execution. No producer
or native module imports, solver call, ledger or Git mutation.
"""
import argparse,ast,copy,gzip,hashlib,itertools,json,platform,subprocess,sys,time,traceback
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
import audit_20260930_exact_eight_population_core as core
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results';I=B/'20260930_independent_review'
PLAN=ROOT/'acceleration/theory_20260930_exact_eight_campaign_plan.md'
DOC=ROOT/'docs/PLAN_20260930_EXACT_EIGHT_CAMPAIGN_INDEPENDENT_AUDIT.md'
POP=B/'20260930_exact_eight_campaign_preparation/campaign_manifest.json'
BG=I/'exact_eight_block_screen/summary.json';BS=B/'20260930_exact_eight_block_screen/summary.json';SUR=BS.parent/'surviving_representatives.json.gz'
RAW=B/'20260930_hadamard20_support/six_prism.json';LOCAL=B/'20260930_hadamard_triplicate_counts/local_triples.json';FIXTURE=core.base.FIXTURE
STATUSES=dict(audit='INDEPENDENT_EXACT_EIGHT_CAMPAIGN_ENCODING_PASS',calibrate='INDEPENDENT_EXACT_EIGHT_CAMPAIGN_OBJECT_CALIBRATION_PASS',sat='INDEPENDENT_EXACT_EIGHT_CAMPAIGN_SAT_OBJECT_PASS')
PINS={POP:'e7b07ea2f7c6b9f6738641afc22779a503841d5ac3da58d3873ebb0fa4b784ba',PLAN:'d497a23778ac45f644e95a0f928988e8d682875466aae81a65cc71319315fee9',BG:'6c21ef6951f72fbeabab8be0a649f178ca8b17eb91edcc35c3291d6790f6256a',BS:'9fbfde4c8d1f1b4fc0aee7b89783a76dcd71c48adf75dbe6c32f116438634edb',SUR:'2cf8ab222d5dd220381fdc14bd225438c173aea40d895353e02f752bc537de5f',RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',LOCAL:'9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',FIXTURE:core.base.PINS[FIXTURE],Path(core.__file__):'d0dd31a7373069801ec8d635c420dc7183f9e2043f11642118c65540a7efcd86',ROOT/'acceleration/theory_20260930_exact_eight_campaign.py':'9ebd87fea886f45fc916ad8afb9dc212fa089f760d4b96e55082926baef02c57',ROOT/'acceleration/theory_20260930_exact_eight_campaign_spec.md':'76d89e652dc0d90084863e4478b9d887658daac21aedfa20ffc72bf7bf48bf69'}
PINS.update(core.HELPER_PINS)
need=core.need;same=core.same;codec=core.codec;shared=core.shared
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def sha(p):
    with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):
    if p.suffix=='.gz':
        with gzip.open(p,'rt',encoding='utf8')as f:return json.load(f)
    return json.loads(p.read_bytes())
def save(p,x):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,separators=(',',':'));f.write('\n')
def static_closure(path):
    seen=set();pending=[path]
    while pending:
        p=pending.pop().resolve()
        if p in seen:continue
        seen.add(p)
        for n in ast.walk(ast.parse(p.read_text(encoding='utf-8-sig'))):
            names=[v.name for v in n.names]if isinstance(n,ast.Import)else[n.module]if isinstance(n,ast.ImportFrom)and n.module else[]
            for name in names:
                q=ROOT/'acceleration'/(name.split('.')[0]+'.py')
                if q.is_file():pending.append(q)
    return seen
def images(v):return {bytes(v[k+p[f]]for k in range(0,720,3)for f in range(3))for p in itertools.permutations(range(3))}

def population(pin):
    gate=read(BG);summary=read(BS);need(gate['status']=='INDEPENDENT_EXACT_EIGHT_BLOCK_SCREEN_PASS','complete independent population premise')
    need(gate['inputs_sha256'].get(key(BS))==PINS[BS] and gate['inputs_sha256'].get(key(SUR))==PINS[SUR],'direct summary/survivor premise')
    need(summary['complete'] and summary['representatives_checked']==792 and summary['complete_profile_pair_tests']==47520,'full prior block population')
    for name,h in summary['outputs_sha256'].items():pin(ROOT/name,h);need(gate['inputs_sha256'].get(name)==h,'all original complete block records authenticated')
    raw=read(SUR);need(raw['complete']and len(raw['records'])==792,'all792 source records')
    rows=sorted(raw['records'],key=lambda r:(r['subset_index'],r['canonical_fibre_profile_sha256']));records=[];seen=set()
    for i,r in enumerate(rows):
        v=core.counts_vector(r['counts']);dg=hashlib.sha256(v).hexdigest();need(v==min(images(v))and dg==r['canonical_fibre_profile_sha256']and dg not in seen,'complete distinct canonical count table');seen.add(dg)
        records.append(dict(case_index=i,case_id='exact_eight_'+dg,subset_index=r['subset_index'],full_count_profile_sha256=dg,raw_representative=r))
    first=[];subsets=set()
    for rec in records:
        if rec['subset_index']not in subsets:
            subsets.add(rec['subset_index']);first.append(rec['case_id'])
            if len(first)==12:break
    expected=dict(schema='EXACT_EIGHT_ALL792_CAMPAIGN_MANIFEST_V1',status='CANDIDATE_COMPLETE_GATED_POPULATION_AND_FIRST12_SELECTION',plan_path=key(PLAN),plan_sha256=PINS[PLAN],block_gate_path=key(BG),block_gate_sha256=PINS[BG],block_summary_path=key(BS),block_summary_sha256=PINS[BS],survivor_path=key(SUR),survivor_sha256=PINS[SUR],universe_size=792,ordering=['subset_index','canonical_full_count_sha256'],records=records,first_batch_case_ids=first,selection_rule='First canonical profile from each of the first12 distinct subset indices in the full ordered792 population.',historical_profiles_subtracted=False,prior_exclusions_used=False,full_fibre_orbit_sizes_assumed=False,full_factor_claim=False)
    need(same(expected,read(POP)),'entire792 manifest and deterministic first12 selection')
    return expected

def case_review(record,summary_path,summary_hash,pin,catalogue,expected_attempt=None):
    pin(summary_path,summary_hash);s=read(summary_path);d=summary_path.parent
    need(s['status']=='CANDIDATE_EXACT_EIGHT_CAMPAIGN_LITERAL_FULL_GRAM_BUILT','terminal producer build, no inferred directory completion')
    for name,h in {**s['inputs_sha256'],**s['outputs_sha256']}.items():pin(ROOT/name,h)
    case_id=record['case_id'];attempt=s['attempt_id'];need(expected_attempt is None or expected_attempt==attempt,'declared build attempt')
    need(attempt.isascii() and attempt and all(c.isalnum()or c in '_-'for c in attempt),'safe explicit attempt identity')
    selection=dict(campaign_manifest_path=key(POP),campaign_manifest_sha256=PINS[POP],plan_path=key(PLAN),plan_sha256=PINS[PLAN],case_id=case_id,case_index=record['case_index'],attempt_id=attempt,literal_record=record,first_batch_member=case_id in read(POP)['first_batch_case_ids'],prior_exclusion_used=False)
    need(same(selection,read(d/'selection.json')),'entire case-selection provenance')
    p=read(d/'selected_profile.json');scope=read(d/'scope.json');actual_model=read(d/'model.json')
    need(p['coordinate_group_fibre_counts']==record['raw_representative']['counts'],'literal universe table, no profile substitution')
    rebuilt=core.verify_formula(read(RAW),p,scope,actual_model,sha(d/'scope.json'),(d/'instance.cnf').read_bytes(),catalogue);facts=rebuilt['facts'];initial=rebuilt['initial_domains'];model=rebuilt['model'];clauses=rebuilt['clauses']
    ep=dict(coordinate_group_fibre_counts=record['raw_representative']['counts'],coordinate_fibre_deviations=facts['coordinate_fibre_deviations'],exceptional_groups=facts['exceptional_groups'],exception_count=8,local_survivor_indices_by_group=[r['local_survivor_indices']for r in initial['records']],profile_sha256=facts['selected_profile_sha256'],full_count_profile_sha256=record['full_count_profile_sha256'],selected_subset_index=record['subset_index'],campaign_case_id=case_id,campaign_case_index=record['case_index'],source_selection_path=key(d/'selection.json'),source_selection_sha256=sha(d/'selection.json'))
    need(same(p,ep)and same(initial,read(d/'initial_domains.json')),'complete profile and all original rank lists')
    es=dict(schema='LITERAL_COUNT_PROFILE_FULL_GRAM_SCOPE_V1',source_count_profile_path=key(d/'selected_profile.json'),source_count_profile_sha256=sha(d/'selected_profile.json'),source_count_gate_path=key(BG),source_count_gate_sha256=PINS[BG],selected_profile_id=case_id,raw_support_path=key(RAW),raw_support_sha256=PINS[RAW],**facts,within_group_column_caps_encoded=True,cross_group_column_caps_encoded=False,residual_D_encoded=False,target_graph=False,assumed_target_automorphism=None,assumed_target_automorphism_null_reason='No target automorphism is assumed.',balance_WLOG=False,profile_is_additional_assumption=True,orbit_coverage_used=False,arc_pruning_used=False,scope='Complete prescribed Gram in this one literal count profile and full initial local domains, with within-group caps. Cross-group caps and residualD omitted.',normalization='Balanced first-coordinate permutation identity; exceptional words sorted. Only equal-support column relabellings.',source_count_gate_role='Independent full block-population gate, with this selected profile derived from the authenticated complete792 manifest.',selection_path=key(d/'selection.json'),selection_sha256=sha(d/'selection.json'),campaign_manifest_path=key(POP),campaign_manifest_sha256=PINS[POP],campaign_case_id=case_id,campaign_case_index=record['case_index'],campaign_subset_index=record['subset_index'],campaign_plan_path=key(PLAN),campaign_plan_sha256=PINS[PLAN],selected_profile_artifact_sha256=sha(d/'selected_profile.json'),initial_domains_path=key(d/'initial_domains.json'),initial_domains_sha256=sha(d/'initial_domains.json'))
    need(same(scope,es),'every mathematical/provenance/omission scope field')
    need([s[k]for k in ['case_id','case_index','selected_subset_index','selected_profile_sha256','selected_full_count_sha256','exceptional_groups','initial_domain_sizes','selectors','variables','clauses']]==[case_id,record['case_index'],record['subset_index'],p['profile_sha256'],p['full_count_profile_sha256'],facts['exceptional_groups'],[len(x['choices'])for x in model['domains']],model['primary_selectors'],model['variables'],model['clauses']],'all actual case dimensions and identity')
    need(all(s[k] is False for k in ['cross_group_column_caps_encoded','residual_D_encoded','arc_pruning_used','historical_exclusion_used','independent_approval'])and s['native_calls']==0,'producer result scope')
    need(gzip.decompress((d/'model.json.gz').read_bytes())==(d/'model.json').read_bytes(),'complete model recovery bytes');pkg=read(d/'model_package.json');need(pkg==dict(raw_path=key(d/'model.json'),raw_sha256=sha(d/'model.json'),raw_bytes=(d/'model.json').stat().st_size,gzip_path=key(d/'model.json.gz'),gzip_sha256=sha(d/'model.json.gz'),gzip_bytes=(d/'model.json.gz').stat().st_size,recovery_identity=True),'exact public recovery mapping')
    checked=dict(case_id=case_id,case_index=record['case_index'],subset_index=record['subset_index'],attempt_id=attempt,summary_path=key(summary_path),summary_sha256=summary_hash,cnf_path=key(d/'instance.cnf'),cnf_sha256=sha(d/'instance.cnf'),model_path=key(d/'model.json'),model_sha256=sha(d/'model.json'),scope_path=key(d/'scope.json'),scope_sha256=sha(d/'scope.json'),profile_path=key(d/'selected_profile.json'),profile_sha256=sha(d/'selected_profile.json'),full_count_profile_sha256=p['full_count_profile_sha256'],compact_deviation_sha256=p['profile_sha256'],variables=model['variables'],clauses=model['clauses'],selectors=model['primary_selectors'],initial_domain_sizes=s['initial_domain_sizes'],complete_raw_clause_reconstruction=True,all_initial_domains=True)
    return checked,(model,scope,p,clauses)

def controls(cases,out):
    truth=Counter();rejected=[]
    def satisfied(cs,v):return all(any(v[abs(x)]==(x>0)for x in c)for c in cs)
    def reject(name,fn):
        try:fn()
        except(ValueError,TypeError,IndexError,KeyError,AssertionError):rejected.append(name)
        else:raise ValueError('accepted corrupted control '+name)
    for n in range(2,7):
        cs=shared.onehot_clauses(list(range(1,n+1)),list(range(n+1,2*n)))
        for bits in itertools.product([False,True],repeat=2*n-1):need(satisfied(cs,dict(enumerate(bits,1)))==(sum(bits[:n])==1 and all(bits[n+i]==any(bits[:i+1])for i in range(n-1))),'prefix exact truth');truth['prefix']+=1
    for n in range(6):
        cs=shared.or_clauses(n+1,list(range(1,n+1)))
        for bits in itertools.product([False,True],repeat=n+1):need(satisfied(cs,dict(enumerate(bits,1)))==(bits[-1]==any(bits[:-1])),'OR/empty exact truth');truth['OR']+=1
    for k in [1,2]:
        cs=shared.count_clauses(list(range(1,11)),k)
        for bits in itertools.product([False,True],repeat=10):need(satisfied(cs,dict(enumerate(bits,1)))==(sum(bits)==k),'exact counter truth');truth['counter']+=1
    fix=read(FIXTURE);F=fix['factor60x180'];C=fix['cubic_core60'];shared.raw_factor(F,C,20);shared.raw_factor([r[::-1]for r in F],C,20);shared.canonical(F,20)
    for kind in ['bit','boolean','length','nonbinary']:
        bad=copy.deepcopy(F)
        if kind=='bit':bad[0][0]^=1
        elif kind=='boolean':bad[0][0]=bool(bad[0][0])
        elif kind=='length':bad[0].pop()
        else:bad[0][0]=2
        reject('genuine243_'+kind,lambda bad=bad:shared.raw_factor(bad,C,20))
    codecs=[];local=[];seen=set()
    for label,(model,scope,profile,clauses)in cases:
        V=model['variables'];M=model['clauses'];dimensions=(V,M)
        if dimensions not in seen:
            seen.add(dimensions);lits=[i if i%2 else-i for i in range(1,V+1)];vals=codec.assignment(lits,V);text='c SYNTHETIC CODEC ONLY\ns SATISFIABLE\n'+'\n'.join('v '+' '.join(map(str,lits[i:i+113]))for i in range(0,V,113))+' 0\n';need(codec.native(text,V)==vals,'all signed native IDs');synthetic=[[lits[i%V]]for i in range(M)];codec.all_clauses(synthetic,vals)
            for name,t in [('missing_status',text.replace('s SATISFIABLE\n','')),('wrong_status',text.replace('SATISFIABLE','UNSATISFIABLE')),('duplicate_status',text+'s SATISFIABLE\n'),('terminal',text.replace(' 0\n','\n')),('duplicate',text.replace('v 1 -2','v 1 1')),('out_of_range',text.replace('v 1 -2','v '+str(V+1)+' -2')),('post_zero',text+'v 1\n')]:reject(str(dimensions)+'_'+name,lambda t=t:codec.native(t,V))
            reject(str(dimensions)+'_missing_JSON',lambda:codec.assignment(lits[:-1],V));reject(str(dimensions)+'_boolean_JSON',lambda:codec.assignment([True,*lits[1:]],V));reject(str(dimensions)+'_native_disagrees',lambda:need(codec.assignment([-lits[0],*lits[1:]],V)==vals,'all raw native/JSON IDs'));synthetic[-1][0]*=-1;reject(str(dimensions)+'_false_clause',lambda:codec.all_clauses(synthetic,vals));synthetic[-1][0]*=-1
            co=out/f'codec_{V}_{M}';co.mkdir();save(co/'assignment.json',dict(assignment=lits,research_SAT=False));(co/'native.stdout.log').write_text(text,encoding='ascii');(co/'synthetic.cnf').write_bytes(codec.cnf_bytes(synthetic,V));codecs.append(dict(variables=V,clauses=M,scope='Complete synthetic codec only, not research factor.'))
        # A deterministic local decoder positive; no assumption it satisfies full Gram.
        f=[[0]*60 for _ in range(36)];selected=[]
        for dom in model['domains']:
            o=dom['choices'][0];selected.append(o['selector'])
            for d,rows in zip(dom['columns'],o['lifted_rows']):
                for r in rows:f[r][d]=1
        counts=[[[sum(f[12*z+a][d]for d in ds)for z in range(3)]for ds in scope['group_columns']]for a in range(12)];need(counts==profile['coordinate_group_fibre_counts']and all(sum(r)==10 for r in f),'all local counts/margins');local.append(dict(case_id=label,selected=selected,factor=f,scope='Local-only positive; no full Gram claimed.'))
        bad=copy.deepcopy(model);bad['domains'][0]['choices'].pop();reject(label+'_missing_option',lambda bad=bad:need(same(bad,model),'complete original model'))
        bad=copy.deepcopy(model);bad['pair_cell_counts'][0]['group_contributions'][0]['coefficients'][0]+=1;reject(label+'_weighted_coefficient',lambda bad=bad:need(same(bad,model),'raw coefficient reconstruction'))
        bad=copy.deepcopy(scope);bad['arc_pruning_used']=True;reject(label+'_scope_AC',lambda bad=bad:core.verify_scope({k:scope[k]for k in ['core_adjacency36']},bad))
    save(out/'local_decode_controls.json',local)
    return dict(truth_cases=dict(truth),genuine243_positive=True,reversed_column_positive=True,codec_dimensions=codecs,rejected_corruptions=rejected,local_only_case_controls=len(local),research_factor_positive=False)

def native_decode_shape(result,model,scope,profile):
    # The public candidate decoder schema matches the previous weighted factor path.
    return dict(factor=result['factor'],L=scope['L12x60'],selected_selector_ids=[r['selector']for r in result['selected_choices']],actual_group_profiles=[dict(group=d['group'],counts=[[sum(result['factor'][12*f+a][j]for j in d['columns'])for f in range(3)]for a in d['support']])for d in model['domains']],canonical_column_order=result['canonical_column_order'],canonical_factor=result['canonical_factor'],core_adjacency=scope['core_adjacency36'],target_gram=scope['prescribed_Gram36'],checks=result['checks'],Gram_factor=True,factor_also_passes_column_caps=not result['checks']['column_cap_violations'],factor_also_passes_mixed_caps=not result['checks']['mixed_cap_violations'],target_graph=False,residual_D=None,profile_is_additional_assumption=True,model_sha256=None,scope_sha256=None,independent_approval=False,selected_profile_id=scope['selected_profile_id'],selected_profile_sha256=scope['selected_profile_sha256'])

SPEC=ROOT/'acceleration/audit_20260930_exact_eight_campaign_spec.md'
BATCH=B/'20260930_exact_eight_first12_cnfs/summary.json'
BATCH_HASH='3f7abda7d7e12a6babaf48c6c690f85bf1db69e6401098f2ece9a881b1772136'
ENCODING=I/'exact_eight_campaign/summary.json'
PINS.update({BATCH:BATCH_HASH,ROOT/'acceleration/build_20260930_exact_eight_first12.py':'94804592ee27e2ba00e6fc4cfc5b6a50b73b54227b4b9277bf744f304b8759bf'})

def batch_review(pop,pin):
    batch=read(BATCH);byid={r['case_id']:r for r in pop['records']}
    need(batch['status']=='CANDIDATE_FIRST12_EXACT_EIGHT_FORMULAS_COMPLETE' and batch['completed_formulas']==12,'complete actual first12 build')
    need(batch['selected_case_ids']==pop['first_batch_case_ids'] and batch['pending_case_ids']==[] and batch['stop'] is None,'exact predeclared first12, no pending cases')
    need(batch['native_calls']==0 and batch['independent_approval'] is False,'build evidence only')
    need([r['case_id']for r in batch['records']]==pop['first_batch_case_ids'],'exact ordered case records')
    for name,h in {**batch['inputs_sha256'],**batch['outputs_sha256']}.items():pin(ROOT/name,h)
    expected_names={'summary.json','instance.cnf','model.json','scope.json','selected_profile.json','initial_domains.json','selection.json','model_package.json'}
    for number,r in enumerate(batch['records'],1):
        source=byid[r['case_id']];need(r['case_index']==source['case_index'] and r['subset_index']==source['subset_index'] and r['full_count_profile_sha256']==source['full_count_profile_sha256'],'each batch identity')
        need(r['attempt_id']=='first12_build01' and set(r['files'])==expected_names,'frozen build attempt and complete named files')
        for name,entry in r['files'].items():
            p=ROOT/entry['path'];need(p.parent==BATCH.parent/f"case_{source['case_index']:04d}" and p.name==name,'exact case-relative file identity');pin(p,entry['sha256']);need(p.stat().st_size==entry['bytes'],'file byte size')
        cp=read(BATCH.parent/f'checkpoint_{number:02d}.json');need(cp==dict(completed_records=batch['records'][:number],pending_case_ids=pop['first_batch_case_ids'][number:],native_calls=0),'entire immutable build prefix checkpoint')
        receipt=read(BATCH.parent/f'case_{number-1:02d}.receipt.json');need(receipt['actual_exit_code']==0 and receipt['native_calls']==0 and receipt['outer_guard_expired'] is False,'producer-only successful build receipt')
        command=receipt['command'];need(command[1:4]==['-B',str(ROOT/'acceleration/theory_20260930_exact_eight_campaign.py'),'build'],'build command executable scope')
        expected_args=['--campaign-manifest',str(POP),'--campaign-manifest-sha256',PINS[POP],'--case-id',r['case_id'],'--attempt-id',r['attempt_id'],'--out',str((ROOT/r['files']['summary.json']['path']).parent)]
        need(command[4:]==expected_args,'exact per-case build command')
    return batch,byid

def main():
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=list(STATUSES));ap.add_argument('--case-id');ap.add_argument('--encoding-gate',type=Path);ap.add_argument('--encoding-gate-sha256');ap.add_argument('--assignment',type=Path);ap.add_argument('--native-output',type=Path);ap.add_argument('--decoded',type=Path);ap.add_argument('--native-driver',type=Path);ap.add_argument('--native-driver-sha256');ap.add_argument('--native-spec',type=Path);ap.add_argument('--native-spec-sha256');ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};start=time.perf_counter()
    def pin(p,h=None):
        p=p.resolve();v=sha(p);need(h is None or v==h,'hash '+key(p));pins[key(p)]=v
    try:
        for p,h in PINS.items():pin(p,h)
        for p in [Path(__file__),SPEC,DOC]:pin(p)
        checker_closure=static_closure(Path(__file__))
        for p in checker_closure:pin(p)
        need(all(not p.name.startswith(('theory_','native_'))for p in checker_closure),'no producer/native imports')
        pop=population(pin);batch,byid=batch_review(pop,pin)
        if args.mode!='audit':
            need(args.encoding_gate and args.encoding_gate.resolve()==ENCODING.resolve() and args.encoding_gate_sha256,'explicit exact campaign encoding gate');pin(args.encoding_gate,args.encoding_gate_sha256);eg=read(args.encoding_gate);need(eg['status']==STATUSES['audit'],'approved aggregate encoding')
            for name,h in eg['inputs_sha256'].items():pin(ROOT/name,h)
            need(eg['selected_case_ids']==pop['first_batch_case_ids'] and eg['complete_formulas']==12 and eg['population_size']==792,'gate covers exact frozen batch and complete population')
        else:eg=None
        need(args.case_id is None if args.mode!='sat' else args.case_id in pop['first_batch_case_ids'],'explicit SAT case is among actual approved formulas')
        chosen=batch['records'] if args.mode!='sat' else [r for r in batch['records']if r['case_id']==args.case_id]
        catalogue=core.prior.catalogue();checked=[];cases=[]
        for entry in chosen:
            record=byid[entry['case_id']];f=entry['files']['summary.json'];row,data=case_review(record,ROOT/f['path'],f['sha256'],pin,catalogue,entry['attempt_id']);checked.append(row);cases.append((row['case_id'],data))
            need([row[k]for k in ['variables','clauses','selectors','initial_domain_sizes']]==[entry[k]for k in ['variables','clauses','selectors','initial_domain_sizes']],'aggregate dimensions match independently reconstructed case')
            if eg is not None:need(row in eg['checked_cases'],'complete case identity agrees with prior encoding gate')
            print(json.dumps(dict(checked_case_id=row['case_id'],complete_clauses=row['clauses'])),flush=True)
        native_closure=[]
        if args.mode=='calibrate':
            need(args.native_driver and args.native_driver_sha256 and args.native_spec and args.native_spec_sha256,'explicit frozen native driver/spec');pin(args.native_driver,args.native_driver_sha256);pin(args.native_spec,args.native_spec_sha256)
            ns=static_closure(args.native_driver)|{args.native_spec.resolve(),ROOT/'acceleration/theory_20260930_exact_eight_campaign_spec.md',ROOT/'acceleration/theory_20260930_hadamard_balanced_gram_cnf.py'}
            for p in ns:pin(p)
            native_closure=sorted(map(key,ns))
        if args.mode in ('audit','calibrate'):
            control=controls(cases,out)
            errors=[]
            for label,mutator in [('duplicate_case',lambda p:p['records'].__setitem__(1,p['records'][0])),('old_subtraction',lambda p:p.__setitem__('historical_profiles_subtracted',True)),('reordered_first12',lambda p:p['first_batch_case_ids'].reverse()),('missing_population',lambda p:p['records'].pop())]:
                bad=copy.deepcopy(pop);mutator(bad);need(not same(bad,pop),'reject altered complete population '+label);errors.append(label)
            control['population_corruptions']=errors
            for label,data in cases:
                model,scope,profile,clauses=data
                need(codec.cnf_bytes(clauses[:-1],model['variables'])!=(ROOT/next(r['cnf_path']for r in checked if r['case_id']==label)).read_bytes(),'missing actual clause rejected')
                original=clauses[0][0];clauses[0][0]=-original
                need(codec.cnf_bytes(clauses,model['variables'])!=(ROOT/next(r['cnf_path']for r in checked if r['case_id']==label)).read_bytes(),'signed actual clause rejected');clauses[0][0]=original
            control['actual_clause_corruptions']=2*len(cases);save(out/'controls.json',control)
        else:
            control=None;need(args.assignment and args.native_output,'complete actual SAT files');pin(args.assignment);pin(args.native_output);model,scope,profile,clauses=cases[0][1]
            values=codec.assignment(read(args.assignment)['assignment'],model['variables']);need(values==codec.native(args.native_output.read_text(encoding='utf8'),model['variables']),'all native and parsed signed IDs identical')
            result=core.decode_and_verify(values,model,scope,profile,clauses);obj=native_decode_shape(result,model,scope,profile);obj['model_sha256']=checked[0]['model_sha256'];obj['scope_sha256']=checked[0]['scope_sha256']
            if args.decoded:pin(args.decoded);need(same(obj,read(args.decoded)),'entire candidate raw decoded object')
            save(out/'independent_Gram_factor.json',obj);save(out/'independent_case_identity.json',checked[0])
        stamp=datetime.now(timezone.utc).isoformat();need(time.perf_counter()-start<180,'bounded180-second independent audit allocation')
        if args.mode=='audit':
            save(out/'claim_binding.json',dict(id='C-FIXED-HADAMARD-EXACT-EIGHT-CAMPAIGN-FIRST12-GRAM-ENCODINGS',revision=1,kind='encoding',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',statement='For each of the exact twelve first-batch cases in the authenticated all792 manifest, its complete CNF is satisfiable iff the fixed six-prism Hadamard support admits a binary36x60 factor with that literal count table, full prescribed integer Gram and within-triplicate column caps, modulo independent equal-support column relabelling. Every original local option is retained and auxiliary assignments are unique.',scope='Exactly twelve literal formulas. The complete792 manifest determines case identities and selection; this gate does not approve unbuilt formulas, supply factors, exclude any case or establish fibre-orbit coverage. Cross-group caps and D are omitted.',assumptions=['Frozen fixed support and complete locally cap-filtered triple catalogue.','Authenticated block-survivor population and declared deterministic first12 selection.'],dependencies=[dict(id='C-FIVE-FIXED-HADAMARD20-SUPPORT-PROJECTIONS',revision=1,relation='premise'),dict(id='C-FIXED-HADAMARD-SIX-PRISM-LOCAL-TRIPLE-CENSUS',revision=1,relation='verification_dependency'),dict(id='C-FIXED-HADAMARD-EXACT-EIGHT-SEPARATE-GRAM-BLOCK-SCREEN',revision=1,relation='uses_result')],verifier='/root/structural_attack',producer='/root/eight_domain_audit',method='Independent raw catalogue/count domains/Gram coefficients/unique channel semantics and literal comparison of every actual CNF clause, exact aggregate selection and checkpoint verification, generic genuine243 and synthetic codec/corruption controls.',shared_components=['Frozen independent third-lift and seven/balanced/codec helpers; fresh parameterized population core and aggregate checker.','No producer or native imports.'],inputs_sha256=pins,checked_cases=checked,limitations=['No solver calls.','Object calibration additionally requires the actual new driver/spec pins.'],artifact_availability='LOCAL_ONLY',availability_reason='Pending publication.',external_review=None,external_review_reason='Independent internal review only.',created_at=stamp,updated_at=stamp))
        save(out/'summary.json',dict(status=STATUSES[args.mode],timestamp=stamp,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],python=platform.python_version(),inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in out.rglob('*')if p.is_file()},population_size=792,selected_case_ids=pop['first_batch_case_ids'],complete_formulas=len(checked),checked_cases=checked,complete_clauses_checked=sum(r['clauses']for r in checked),literal_catalogue_candidates=117480,local_survivors=31110,controls=control,native_source_closure=native_closure,checker_source_closure=sorted(map(key,checker_closure)),elapsed_seconds=time.perf_counter()-start,solver_calls=0,target_resolution=False,cross_group_column_caps_encoded=False,residual_D_encoded=False))
        print(json.dumps(dict(status=STATUSES[args.mode],summary_sha256=sha(out/'summary.json'),source_sha256=sha(Path(__file__)))),flush=True)
    except Exception as error:save(out/'failure.json',dict(error=repr(error),traceback=traceback.format_exc(),source_sha256=sha(Path(__file__)),inputs_sha256=pins));raise
if __name__=='__main__':main()
