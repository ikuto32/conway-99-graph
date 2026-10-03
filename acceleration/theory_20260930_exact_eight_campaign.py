"""Parameterized complete exact-eight campaign producer; no native solver."""
from collections import defaultdict
from datetime import datetime,timezone
from itertools import permutations,combinations
from pathlib import Path
import argparse,gzip,hashlib,json,platform,subprocess,sys,time,traceback
import theory_20260930_hadamard_four_profile_cnf as shared
ROOT=shared.ROOT;B=ROOT/'acceleration/results';RAW=shared.RAW;LOCAL=shared.LOCAL
SPEC=Path(__file__).with_name(Path(__file__).stem+'_spec.md');PLAN=ROOT/'acceleration/theory_20260930_exact_eight_campaign_plan.md';PROFILE=None;GATE=None
PREVIOUS=ROOT/'acceleration/theory_20260930_eight_count_profile_lift_third.py'
PINS={PREVIOUS:'59cf7df0013dc62b79812b784a15a7e9b42ee101510f5a94db0dcfa998812767',PREVIOUS.with_name(PREVIOUS.stem+'_spec.md'):'b6386f66bb570df301a766ce4e59f389850e3adcbf11cb959c614fcd0a5b221f',PLAN:'d497a23778ac45f644e95a0f928988e8d682875466aae81a65cc71319315fee9',RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',LOCAL:'9e2cc28f419241755a9c7380fbe217ff04bff0bb4bcd3708be104a40295d9776',B/'20260930_independent_review/hadamard_triplicate_counts_v2/summary.json':'cb9f1c7f8cfe0db557f554ded5427a9cba46dda10dcd9b5df9968e1d3b776f88',Path(shared.__file__):'0b4b737486974a499026bee4146cc7b461b654aeeb5af46e0553e908fa012f2f',Path(shared.__file__).with_name('theory_20260930_hadamard_four_profile_cnf_spec.md'):'929c19abc9d0cdd8292148c71d0b0b4b7addf79ddb1618a886b0994b86159113',shared.BASE:'ffb5c842b29d0268073656ce948561af0557c24d067bf0260a9cc8f65ab07016',shared.FIXTURE:shared.PINS[shared.FIXTURE],shared.FIXTURE_GATE:shared.PINS[shared.FIXTURE_GATE]}
need=shared.need;sha=shared.sha;key=shared.key;read=shared.read;save=shared.save

def flattened(counts):return tuple(x for row in counts for t in row for x in t)
def fibre_images(v):return {tuple(v[k+p[f]]for k in range(0,len(v),3)for f in range(3))for p in permutations(range(3))}

def margins(groups,counts):
    records=[]
    for a in range(12):
        for f in range(3):
            n=sum(counts[g][groups[g].index(a)][f]for g in range(20)if a in groups[g]);need(n==10,'literal row margin10');records.append(dict(coordinate=a,fibre=f,total=n))
    return records

def check_within(rows):
    need(len(rows)==3 and all(len(x)==6 and len(set(x))==6 for x in rows),'three six-entry columns')
    need(all(len(set(x)&set(y))<=2 for x,y in combinations(rows,2)),'all within-group caps')

def check_zero(rows,gram):
    need(all(gram[a][b]!=0 for column in rows for a,b in combinations(column,2)),'all automatic zero Gram entries')

def prepare(h,p):
    base=h.scope_from_raw(read(RAW));groups=base['groups'];catalog=read(LOCAL);words=catalog['words'];triples=catalog['survivors'];counts=p['coordinate_group_fibre_counts'];exceptional=p['exceptional_groups'];expected=p['local_survivor_indices_by_group'];by_signature=defaultdict(list)
    need(len(counts)==12 and all(len(row)==20 and all(len(v)==3 and all(type(x)is int and 0<=x<=3 for x in v)for v in row)for row in counts),'literal count table shape/bounds')
    for a in range(12):
        for g,support in enumerate(groups):need(sum(counts[a][g])==(3 if a in support else 0),'raw support coordinate totals')
    digest=hashlib.sha256(json.dumps(dict(groups=exceptional,deviations=p['coordinate_fibre_deviations']),sort_keys=True,separators=(',',':')).encode()).hexdigest();need(digest==p['profile_sha256'],'literal profile digest')
    actual_exceptional=[g for g,s in enumerate(groups)if any(counts[a][g]!=[1,1,1]for a in s)];need(actual_exceptional==exceptional and len(exceptional)==p['exception_count'],'actual arbitrary exception list')
    for ti,t in enumerate(triples):by_signature[tuple(sum(words[w][a]==f for w in t)for a in range(6)for f in range(3))].append(ti)
    scope=dict(schema='LITERAL_COUNT_PROFILE_FULL_GRAM_SCOPE_V1',source_count_profile_path=key(PROFILE),source_count_profile_sha256=PINS[PROFILE],source_count_gate_path=key(GATE),source_count_gate_sha256=PINS[GATE],selected_profile_id=p['campaign_case_id'],selected_profile_sha256=digest,raw_support_path=key(RAW),raw_support_sha256=PINS[RAW],core_adjacency36=base['core_adjacency36'],prescribed_Gram36=base['prescribed_Gram36'],L12x60=base['L12x60'],groups=groups,group_columns=base['group_columns'],coordinate_pairs=base['coordinate_pairs'],exceptional_groups=exceptional,coordinate_fibre_deviations=p['coordinate_fibre_deviations'],coordinate_group_fibre_counts=counts,balanced_groups=[g for g in range(20)if g not in exceptional],within_group_column_caps_encoded=True,cross_group_column_caps_encoded=False,residual_D_encoded=False,target_graph=False,assumed_target_automorphism=None,assumed_target_automorphism_null_reason='No target automorphism is assumed.',balance_WLOG=False,profile_is_additional_assumption=True,orbit_coverage_used=False,arc_pruning_used=False,scope='Complete prescribed Gram in this one literal count profile and full initial local domains, with within-group caps. Cross-group caps and residualD omitted.',normalization='Balanced first-coordinate permutation identity; exceptional words sorted. Only equal-support column relabellings.')
    balanced=h.local_options();domains=[];rank_lists=[];selector=1;wanted_counts=[]
    for g,support in enumerate(groups):
        want=[counts[a][g]for a in support];signature=tuple(x for row in want for x in row);ids=by_signature[signature];need(ids==expected[g]and ids,'complete original initial signature class')
        if g in exceptional:choices=[dict(choice_index=i,local_survivor_index=ti,word_indices=triples[ti],colour_words=[words[w]for w in triples[ti]])for i,ti in enumerate(ids)];kind='exceptional_sorted_local_triple'
        else:need(signature==(1,)*18 and len(ids)==150,'balanced class');choices=[dict(choice_index=c['choice_index'],colour_words=c['colour_words'],coordinate_permutations=c['coordinate_permutations'])for c in balanced];kind='balanced_normalized_triple'
        for c in choices:
            c['selector']=selector;selector+=1;c['lifted_rows']=[[12*w[pos]+a for pos,a in enumerate(support)]for w in c['colour_words']]
            need([[sum(w[pos]==f for w in c['colour_words'])for f in range(3)]for pos in range(6)]==want,'all literal option counts')
            check_within(c['lifted_rows'])
            check_zero(c['lifted_rows'],scope['prescribed_Gram36'])
        domains.append(dict(group=g,support=support,columns=scope['group_columns'][g],kind=kind,fixed_counts=want,choices=choices));wanted_counts.append(want);rank_lists.append(dict(group=g,count_signature=list(signature),local_survivor_indices=ids,count=len(ids)))
    scope['derived_row_margins']=margins(groups,wanted_counts)
    damaged=json.loads(json.dumps(wanted_counts));damaged[0][0][0]+=1
    try:margins(groups,damaged)
    except ValueError:pass
    else:raise ValueError('changed profile accepted')
    for g in range(20):
        for ids in [rank_lists[g]['local_survivor_indices'][:-1],rank_lists[g]['local_survivor_indices']+[rank_lists[g]['local_survivor_indices'][0]]]:need(ids!=expected[g],'missing/extra domain control')
    try:check_within([list(range(6))]*3)
    except ValueError:pass
    else:raise ValueError('overlap corruption accepted')
    zero=next((a,b)for a in range(36)for b in range(a+1,36)if scope['prescribed_Gram36'][a][b]==0)
    try:check_zero([list(zero)],scope['prescribed_Gram36'])
    except ValueError:pass
    else:raise ValueError('zero-Gram corruption accepted')
    return scope,domains,rank_lists

def decode(assignment,model_path,scope_path,cnf_path):
    result=shared.decode(assignment,model_path,scope_path,cnf_path);scope=read(scope_path);result['selected_profile_sha256']=scope['selected_profile_sha256'];result['selected_profile_id']=scope['selected_profile_id'];return result

BLOCK_GATE=B/'20260930_independent_review/exact_eight_block_screen/summary.json'
BLOCK_SUMMARY=B/'20260930_exact_eight_block_screen/summary.json'
BLOCK_GATE_SHA='6c21ef6951f72fbeabab8be0a649f178ca8b17eb91edcc35c3291d6790f6256a'
BLOCK_SUMMARY_SHA='9fbfde4c8d1f1b4fc0aee7b89783a76dcd71c48adf75dbe6c32f116438634edb'
PINS.update({BLOCK_GATE:BLOCK_GATE_SHA,BLOCK_SUMMARY:BLOCK_SUMMARY_SHA,ROOT/'acceleration/theory_20260930_exact_eight_next_lift.py':'473b4774650f43fbd51dc9387f006bf1b9626e70acfd80e4a3ab45c25ac04dff'})

def compact_save(path,data):
    with path.open('x',encoding='utf8',newline='\n')as f:json.dump(data,f,sort_keys=True,separators=(',',':'));f.write('\n')

def authenticated_population(pin):
    for p,h in PINS.items():pin(p,h)
    gate=read(BLOCK_GATE);need(gate['status']=='INDEPENDENT_EXACT_EIGHT_BLOCK_SCREEN_PASS','independent complete block screen')
    summary=read(BLOCK_SUMMARY);need(gate['inputs_sha256'][key(BLOCK_SUMMARY)]==BLOCK_SUMMARY_SHA,'direct block-summary binding')
    need(summary['complete']and summary['representatives_checked']==792 and summary['complete_profile_pair_tests']==47520,'all792 block population')
    for name,h in summary['outputs_sha256'].items():pin(ROOT/name,h);need(gate['inputs_sha256'].get(name)==h,'authenticated full block output '+name)
    source=BLOCK_SUMMARY.parent/'surviving_representatives.json.gz'
    with gzip.open(source,'rt',encoding='utf8')as f:raw=json.load(f)
    need(raw['complete']and len(raw['records'])==792,'exact complete survivor count')
    rows=sorted(raw['records'],key=lambda r:(r['subset_index'],r['canonical_fibre_profile_sha256']));records=[]
    for i,r in enumerate(rows):
        v=flattened(r['counts']);need(len(v)==720 and v==min(fibre_images(v))and hashlib.sha256(bytes(v)).hexdigest()==r['canonical_fibre_profile_sha256'],'canonical full literal table')
        records.append(dict(case_index=i,case_id='exact_eight_'+r['canonical_fibre_profile_sha256'],subset_index=r['subset_index'],full_count_profile_sha256=r['canonical_fibre_profile_sha256'],raw_representative=r))
    need(len({r['case_id']for r in records})==792,'distinct full canonical case identifiers')
    chosen=[];seen=set()
    for r in records:
        if r['subset_index']not in seen:
            seen.add(r['subset_index']);chosen.append(r['case_id'])
            if len(chosen)==12:break
    need(len(chosen)==12,'at least12 distinct nonempty subset indices')
    return dict(schema='EXACT_EIGHT_ALL792_CAMPAIGN_MANIFEST_V1',status='CANDIDATE_COMPLETE_GATED_POPULATION_AND_FIRST12_SELECTION',plan_path=key(PLAN),plan_sha256=PINS[PLAN],block_gate_path=key(BLOCK_GATE),block_gate_sha256=BLOCK_GATE_SHA,block_summary_path=key(BLOCK_SUMMARY),block_summary_sha256=BLOCK_SUMMARY_SHA,survivor_path=key(source),survivor_sha256=sha(source),universe_size=792,ordering=['subset_index','canonical_full_count_sha256'],records=records,first_batch_case_ids=chosen,selection_rule='First canonical profile from each of the first12 distinct subset indices in the full ordered792 population.',historical_profiles_subtracted=False,prior_exclusions_used=False,full_fibre_orbit_sizes_assumed=False,full_factor_claim=False)

def selected_profile(record,selection_path):
    chosen=record['raw_representative'];counts=chosen['counts'];raw=read(RAW);groups=list(dict.fromkeys(tuple(a for a in range(12)if raw['L'][a][d])for d in range(60)))
    exceptional=[g for g,s in enumerate(groups)if any(counts[a][g]!=[1,1,1]for a in s)]
    need(exceptional==chosen['exceptional_groups']and len(exceptional)==8,'actual eight exceptions')
    local=read(LOCAL);words=local['words'];classes=defaultdict(list)
    for i,t in enumerate(local['survivors']):classes[tuple(sum(words[w][a]==f for w in t)for a in range(6)for f in range(3))].append(i)
    deviations=[[[counts[a][g][f]-int(a in groups[g])for g in exceptional]for f in range(3)]for a in range(12)]
    digest=hashlib.sha256(json.dumps(dict(groups=exceptional,deviations=deviations),sort_keys=True,separators=(',',':')).encode()).hexdigest()
    ranks=[classes[tuple(x for a in s for x in counts[a][g])]for g,s in enumerate(groups)];need(all(ranks),'all original classes nonempty')
    return dict(coordinate_group_fibre_counts=counts,coordinate_fibre_deviations=deviations,exceptional_groups=exceptional,exception_count=8,local_survivor_indices_by_group=ranks,profile_sha256=digest,full_count_profile_sha256=record['full_count_profile_sha256'],selected_subset_index=record['subset_index'],campaign_case_id=record['case_id'],campaign_case_index=record['case_index'],source_selection_path=key(selection_path),source_selection_sha256=sha(selection_path))

def main():
    global PROFILE,GATE
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['prepare','build']);ap.add_argument('--campaign-manifest',type=Path);ap.add_argument('--campaign-manifest-sha256');ap.add_argument('--case-id');ap.add_argument('--attempt-id');ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.perf_counter();pins={}
    def pin(p,h=None):
        p=p.resolve();v=sha(p);need(h is None or v==h,'pin '+key(p));pins[key(p)]=v
    try:
        for p in [Path(__file__),SPEC,shared.BASE.with_name(shared.BASE.stem+'_spec.md'),ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(p)
        universe=authenticated_population(pin)
        manifest=dict(timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=pins,command=[sys.executable,*sys.argv],python=platform.python_version(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),allocation_seconds=120,native_calls=0,shared_components=['Copied frozen next-lift/third-lift local-class preparation.','Frozen weighted four-profile builder/decoder and dynamically loaded balanced helper.','Producer reuse, no independent self-approval.'])
        if args.mode=='prepare':
            need(not any([args.case_id,args.campaign_manifest,args.campaign_manifest_sha256,args.attempt_id]),'prepare selects immutable universe only')
            compact_save(out/'campaign_manifest.json',universe);save(out/'manifest.json',manifest)
            save(out/'summary.json',dict(status='CANDIDATE_EXACT_EIGHT_ALL792_CAMPAIGN_PREPARED',inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in out.iterdir()},universe_size=792,first_batch_case_ids=universe['first_batch_case_ids'],historical_subtractions=0,formula_builds=0,native_calls=0,elapsed_seconds=time.perf_counter()-start))
        else:
            need(args.campaign_manifest and args.campaign_manifest_sha256 and args.case_id and args.attempt_id,'explicit manifest/case/attempt');need(args.attempt_id.isascii()and all(c.isalnum()or c in '_-'for c in args.attempt_id),'safe stable attempt identity')
            pin(args.campaign_manifest,args.campaign_manifest_sha256);need(read(args.campaign_manifest)==universe,'complete792 manifest independently regenerated by producer')
            found=[r for r in universe['records']if r['case_id']==args.case_id];need(len(found)==1,'literal complete-universe membership');record=found[0]
            selection=dict(campaign_manifest_path=key(args.campaign_manifest),campaign_manifest_sha256=args.campaign_manifest_sha256,plan_path=key(PLAN),plan_sha256=PINS[PLAN],case_id=args.case_id,case_index=record['case_index'],attempt_id=args.attempt_id,literal_record=record,first_batch_member=args.case_id in universe['first_batch_case_ids'],prior_exclusion_used=False)
            save(out/'selection.json',selection);p=selected_profile(record,out/'selection.json');PROFILE=out/'selected_profile.json';GATE=BLOCK_GATE;save(PROFILE,p);PINS[PROFILE]=sha(PROFILE)
            h=shared.helper();save(out/'gadget_controls.json',shared.controls(h));scope,domains,ranks=prepare(h,p)
            scope.update(source_count_gate_role='Independent full block-population gate, with this selected profile derived from the authenticated complete792 manifest.',selection_path=key(out/'selection.json'),selection_sha256=sha(out/'selection.json'),selected_full_count_sha256=p['full_count_profile_sha256'],campaign_manifest_path=key(args.campaign_manifest),campaign_manifest_sha256=args.campaign_manifest_sha256,campaign_case_id=args.case_id,campaign_case_index=record['case_index'],campaign_subset_index=record['subset_index'],campaign_plan_path=key(PLAN),campaign_plan_sha256=PINS[PLAN])
            save(out/'initial_domains.json',dict(records=ranks,all_initial=True,AC_pruning_used=False));scope.update(selected_profile_artifact_sha256=sha(PROFILE),initial_domains_path=key(out/'initial_domains.json'),initial_domains_sha256=sha(out/'initial_domains.json'));save(out/'scope.json',scope)
            model,clauses=shared.build(h,scope,domains);model['schema']='LITERAL_COUNT_PROFILE_FULL_GRAM_WEIGHTED_CNF_V1';model['scope_sha256']=sha(out/'scope.json');S=sum(len(d['choices'])for d in domains)
            need((model['primary_selectors'],model['variables'],model['clauses'])==(S,2*S+5380,49*S+60400),'actual domain-derived dimensions');save(out/'model.json',model)
            with(out/'instance.cnf').open('x',encoding='ascii',newline='\n')as f:
                f.write(f"p cnf {model['variables']} {model['clauses']}\n")
                for c in clauses:f.write(' '.join(map(str,c))+' 0\n')
            with(out/'model.json').open('rb')as f,(out/'model.json.gz').open('xb')as rawgzip:
                with gzip.GzipFile(filename='',mode='wb',fileobj=rawgzip,mtime=0)as g:
                    for b in iter(lambda:f.read(1048576),b''):g.write(b)
            whole=hashlib.sha256();length=0
            with gzip.open(out/'model.json.gz','rb')as g,(out/'model.json').open('rb')as original:
                for b in iter(lambda:g.read(1048576),b''):need(original.read(len(b))==b,'literal original bytes');whole.update(b);length+=len(b)
                need(not original.read(1),'no trailing original bytes')
            need(whole.hexdigest()==sha(out/'model.json')and length==(out/'model.json').stat().st_size and(out/'model.json.gz').stat().st_size<10*1024**2,'complete compressed recovery')
            save(out/'model_package.json',dict(raw_path=key(out/'model.json'),raw_sha256=whole.hexdigest(),raw_bytes=length,gzip_path=key(out/'model.json.gz'),gzip_sha256=sha(out/'model.json.gz'),gzip_bytes=(out/'model.json.gz').stat().st_size,recovery_identity=True))
            manifest.update(case_id=args.case_id,attempt_id=args.attempt_id);save(out/'manifest.json',manifest)
            need(time.perf_counter()-start<120,'120-second build allocation')
            save(out/'summary.json',dict(status='CANDIDATE_EXACT_EIGHT_CAMPAIGN_LITERAL_FULL_GRAM_BUILT',inputs_sha256=pins,outputs_sha256={key(q):sha(q)for q in out.iterdir()},case_id=args.case_id,case_index=record['case_index'],attempt_id=args.attempt_id,selected_subset_index=record['subset_index'],selected_profile_sha256=p['profile_sha256'],selected_full_count_sha256=p['full_count_profile_sha256'],exceptional_groups=p['exceptional_groups'],initial_domain_sizes=[len(d['choices'])for d in domains],selectors=S,variables=model['variables'],clauses=model['clauses'],scope=scope['scope'],cross_group_column_caps_encoded=False,residual_D_encoded=False,arc_pruning_used=False,historical_exclusion_used=False,native_calls=0,independent_approval=False,elapsed_seconds=time.perf_counter()-start))
        print(json.dumps(dict(mode=args.mode,summary_path=key(out/'summary.json'),summary_sha256=sha(out/'summary.json'))))
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),traceback=traceback.format_exc(),inputs_sha256=pins));raise
if __name__=='__main__':main()

