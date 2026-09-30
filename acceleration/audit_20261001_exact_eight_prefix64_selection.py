"""Reusable independent request/first64/partition identity review, no producer import."""
import argparse, copy, hashlib, json, re, sys, time, traceback
from datetime import datetime, timezone
from pathlib import Path
import audit_20260930_exact_eight_explicit_batch_v3 as checked

ROOT=checked.ROOT
prior=checked.prior
need=checked.need
read=checked.read
sha=checked.sha
key=checked.key
save=checked.save
SPEC=Path(__file__).with_name(Path(__file__).stem+'_spec.md')
PRODUCER=ROOT/'acceleration/select_20260930_exact_eight_prefix64.py'
PRODUCER_SPEC=PRODUCER.with_name(PRODUCER.stem+'_spec.md')
PINS={Path(checked.__file__):'0387354132a3e72496cfc8e0c9a3bbe4216767ee68cbcb6b6de070f6314ece10',
      ROOT/'acceleration/audit_20260930_exact_eight_explicit_batch_v3_spec.md':'50bb97614dca5de8f137b3edc68132176c5628046748cda3e6b99a8bcc528c3a',
      PRODUCER:'16807bb5e5a9bcdb4fbadaa5b0f0ee69e360df46ac60664c0980540e0a891ce8',
      PRODUCER_SPEC:'fe04ab0a06577496ae024ec4102e0c6cc869e4bff58f0b3878b3375f3d7ddc27'}
STATUS='INDEPENDENT_EXACT_EIGHT_PREFIX64_SELECTION_PREPARATION_PASS'
REQUEST_FIELDS={'schema','campaign_manifest_path','campaign_manifest_sha256','authorization_record_path','authorization_record_sha256','completed_proof_gates','selection_reason','build_allocations','recorded_source_commit'}

def same(a,b):
    return json.dumps(a,sort_keys=True,separators=(',',':'))==json.dumps(b,sort_keys=True,separators=(',',':'))

def canonical(name):
    need(type(name)is str and name and '\\'not in name and not Path(name).is_absolute(),'canonical relative repository path')
    p=(ROOT/name).resolve()
    need(p.is_relative_to(ROOT)and key(p)==name,'no path alias or escape')
    need(name not in ['PROMPT.md','CLAIMS.yaml','acceleration/results/20260930_independent_review/hadamard_oriented_unknown/process.stdout.log']and not name.startswith(('tools/','external_conway99_research/')),'protected input refused before read')
    need(p.name.lower()not in {'.env','.env.local','credentials','credentials.json','id_rsa','id_ed25519'}and p.suffix.lower()not in {'.pem','.key'},'private-shaped input refused')
    return p

def exact(actual,expected,message):
    need(same(actual,expected),message)

def request_shape(request):
    need(type(request)is dict and set(request)==REQUEST_FIELDS and request['schema']=='EXACT_EIGHT_PREFIX64_REQUEST_V1','entire explicit request schema')
    need(request['campaign_manifest_path']==key(prior.POP)and request['campaign_manifest_sha256']==prior.PINS[prior.POP],'unchanged complete792 universe')
    need(type(request['selection_reason'])is str and bool(request['selection_reason'].strip()),'explicit allocation reason')
    need(type(request['recorded_source_commit'])is str and re.fullmatch('[0-9a-f]{40}',request['recorded_source_commit']),'recorded commit metadata')
    refs=request['completed_proof_gates']
    need(type(refs)is list and refs and all(type(r)is dict and {'path','sha256'}<=set(r)<={'path','sha256','completed_cases'}for r in refs),'explicit finite proof-gate reference list')
    need(len({r['path']for r in refs})==len(refs),'duplicate proof gate refused')
    for r in refs:
        canonical(r['path']);need(type(r['sha256'])is str and re.fullmatch('[0-9a-f]{64}',r['sha256']),'proof gate hash')
        need('completed_cases'not in r or type(r['completed_cases'])is int and r['completed_cases']>0,'optional literal positive proof count')
    allocations=request['build_allocations']
    need(type(allocations)is list and len(allocations)==4 and all(type(r)is dict and set(r)=={'attempt_id','out'}for r in allocations),'four explicit original serial allocations')
    folders=[];attempts=[]
    for r in allocations:
        p=canonical(r['out']);a=r['attempt_id']
        need(p.is_relative_to(ROOT/'acceleration/results'),'research result output boundary')
        need(type(a)is str and bool(a)and a.isascii()and all(c.isalnum()or c in '_-'for c in a),'safe literal build attempt')
        folders.append(p);attempts.append(a)
    need(len(set(folders))==len(set(attempts))==4 and all(not a.is_relative_to(b)for a in folders for b in folders if a!=b),'disjoint four attempts/outputs')
    return folders

def parent_for(request,ids,skips,normalized):
    return dict(schema='EXACT_EIGHT_EXPLICIT_BUILD_SELECTION_V1',selection_policy='FIRST_UNPROVED_MANIFEST_PREFIX_V1',campaign_manifest_path=key(prior.POP),campaign_manifest_sha256=prior.PINS[prior.POP],ordered_case_ids=ids,selection_reason=request['selection_reason'],authorization_record_path=request['authorization_record_path'],authorization_record_sha256=request['authorization_record_sha256'],completed_proof_gates=normalized,skipped_verified_case_ids=skips,population=792,unresolved_before_batch=792-len(skips),selected_instances=64)

def child_for(parent,parent_ref,i):
    expected=copy.deepcopy(parent)
    expected.update(selection_policy='AUTHORIZED_DISJOINT_BUILD_PARTITION_V1',ordered_case_ids=parent['ordered_case_ids'][16*i:16*(i+1)],selection_reason=f'Explicit contiguous16-case partition{i} of the authenticated first-unproved64 selection; no new proof or skip inference.',parent_selection_path=parent_ref['path'],parent_selection_sha256=parent_ref['sha256'],partition_index=i,partition_offset=16*i,selected_instances=16)
    return expected

def compare_controls(request,parent,parts,launch):
    rejected=[]
    mutations=[('unknown_request_field',lambda x:x.update(unrequested=True)),('wrong_request_schema',lambda x:x.update(schema='OTHER')),('duplicate_proof_gate',lambda x:x['completed_proof_gates'].append(copy.deepcopy(x['completed_proof_gates'][0]))),('boolean_proof_count',lambda x:x['completed_proof_gates'][0].update(completed_cases=True)),('wrong_manifest',lambda x:x.update(campaign_manifest_sha256='0'*64)),('three_allocations',lambda x:x['build_allocations'].pop()),('duplicate_attempt',lambda x:x['build_allocations'][1].update(attempt_id=x['build_allocations'][0]['attempt_id'])),('duplicate_output',lambda x:x['build_allocations'][1].update(out=x['build_allocations'][0]['out']))]
    for name,mutate in mutations:
        bad=copy.deepcopy(request);mutate(bad)
        try:request_shape(bad)
        except (ValueError,KeyError,TypeError):rejected.append(name)
        else:raise ValueError('accepted request corruption '+name)
    for name,mutate in [('parent_reordered',lambda x:x['ordered_case_ids'].reverse()),('parent_skips_selected',lambda x:x['skipped_verified_case_ids'].append(x['ordered_case_ids'][0])),('parent_wrong_remaining',lambda x:x.update(unresolved_before_batch=0)),('parent_wrong_count',lambda x:x.update(selected_instances=63))]:
        bad=copy.deepcopy(parent);mutate(bad);need(not same(bad,parent),'parent corruption rejected');rejected.append(name)
    for i,part in enumerate(parts):
        for field,value in [('partition_offset',1),('partition_index',4),('parent_selection_sha256','0'*64),('selected_instances',15)]:
            bad=copy.deepcopy(part);bad[field]=value;need(not same(bad,part),'partition corruption rejected');rejected.append(f'partition{i}_{field}')
    for name,mutate in [('wrong_workers',lambda x:x.update(workers=3)),('wrong_budget',lambda x:x.update(seconds_per_chunk=121)),('reordered_launch',lambda x:x['build_selections'].reverse()),('duplicate_launch',lambda x:x['build_selections'].__setitem__(1,copy.deepcopy(x['build_selections'][0]))),('wrong_parent',lambda x:x.update(parent_selection_sha256='0'*64))]:
        bad=copy.deepcopy(launch);mutate(bad);need(not same(bad,launch),'launch corruption rejected');rejected.append(name)
    return dict(prefix_policy=checked.prefix_controls(),partition=checked.partition_controls(),request_parent_partition_launch_rejected=rejected)

def main():
    ap=argparse.ArgumentParser()
    for field in ['request','selection','launch-plan']:
        ap.add_argument('--'+field,type=Path,required=True);ap.add_argument('--'+field+'-sha256',required=True)
    ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    out=args.out.resolve();need(out.is_relative_to(ROOT/'acceleration/results'),'review output boundary');out.mkdir(parents=True,exist_ok=False)
    pins={};start=time.perf_counter()
    def pin(p,h=None):
        p=p.resolve();name=key(p);need(canonical(name)==p,'safe exact pinned path')
        if h is not None:need(type(h)is str and re.fullmatch('[0-9a-f]{64}',h),'literal expected SHA256')
        if name not in pins:pins[name]=sha(p)
        need(h is None or pins[name]==h,'hash '+name)
    try:
        for p,h in {**checked.PINS,**PINS}.items():pin(p,h)
        for p in [Path(__file__),SPEC]:pin(p)
        closure=prior.static_closure(Path(__file__))
        for p in closure:pin(p);need(not p.name.startswith(('theory_','native_','select_')),'independent checking helpers only; no producer imports')
        rp=args.request.resolve();sp=args.selection.resolve();lp=args.launch_plan.resolve()
        for p,h in [(rp,args.request_sha256),(sp,args.selection_sha256),(lp,args.launch_plan_sha256)]:pin(p,h)
        need(sp.name=='selection.json'and lp==sp.parent/'launch_plan.json','literal candidate output layout')
        request=read(rp);folders=request_shape(request)
        pin(canonical(request['authorization_record_path']),request['authorization_record_sha256'])
        need(all(not p.exists()and not p.is_relative_to(sp.parent)and not sp.parent.is_relative_to(p)for p in folders),'prebuild gate: four fresh outputs separate from selection')
        pop=prior.population(pin);byid={r['case_id']:r for r in pop['records']}
        skipped,bindings,proof_rows=checked.proof_skips(request,byid,pin)
        normalized=[dict(path=r['path'],sha256=r['sha256'],completed_cases=read(canonical(r['path']))['completed_proof_replays'])for r in request['completed_proof_gates']]
        ids=checked.prefix_selection([r['case_id']for r in pop['records']],skipped,64)
        expected=parent_for(request,ids,skipped,normalized);parent=read(sp);exact(parent,expected,'entire independently reconstructed first64 selection')
        pref=dict(path=key(sp),sha256=args.selection_sha256)
        parts=[];partrefs=[]
        for i in range(4):
            p=sp.parent/f'partition_{i:02d}.json';pin(p);r=dict(path=key(p),sha256=pins[key(p)])
            child=read(p);exact(child,child_for(expected,pref,i),'entire exact four-way partition');parts.append(child);partrefs.append(r)
        checked.validate_partition(ids,[p['ordered_case_ids']for p in parts])
        want_launch=dict(schema='EXACT_EIGHT_FOUR_SERIAL_BUILD_PLAN_V1',parent_selection_path=key(sp),parent_selection_sha256=args.selection_sha256,workers=4,seconds_per_chunk=120,build_selections=[dict(**r,**a)for r,a in zip(partrefs,request['build_allocations'],strict=True)])
        launch=read(lp);exact(launch,want_launch,'complete launch plan, explicit attempts/outputs, four120-second budgets')
        meta_path=sp.parent/'summary.json';pin(meta_path);meta=read(meta_path)
        need(meta['status']=='CANDIDATE_EXACT_EIGHT_PREFIX64_SELECTION_PREPARED'and meta['source_sha256']==PINS[PRODUCER]and meta['native_calls']==meta['producer_calls']==0 and meta['independent_approval']is False,'candidate selection-only receipt')
        for field in ['inputs_sha256','outputs_sha256']:
            for name,h in meta[field].items():pin(canonical(name),h)
        need(meta['inputs_sha256'].get(key(rp))==args.request_sha256,'actual producer binds exact request')
        need(meta['source_commit']==request['recorded_source_commit']and meta['source_commit_provenance']=='Caller-frozen request metadata; no current Git query.','honest recorded commit metadata')
        exact(meta['selection'],pref,'summary exact selection');exact(meta['build_selections'],partrefs,'summary exact partitions');exact(meta['launch_plan'],dict(path=key(lp),sha256=args.launch_plan_sha256),'summary exact launch plan')
        indices=[byid[x]['case_index']for x in ids]
        need(meta['selected_case_ids']==ids and meta['skipped_verified_case_ids']==skipped and meta['selected_case_indices']==indices,'summary exact literal identities')
        command=meta['command'];need(type(command)is list and len(command)==9 and (ROOT/command[1]).resolve()==PRODUCER and command[2]=='select','actual selector command source/mode')
        options=dict(zip(command[3::2],command[4::2]));need(len(options)==3 and set(options)=={'--request','--request-sha256','--out'}and (ROOT/options['--request']).resolve()==rp and options['--request-sha256']==args.request_sha256 and (ROOT/options['--out']).resolve()==sp.parent,'exact explicit selector command options')
        raw_review=sp.parent/'prior_proof_identity_review.json';pin(raw_review)
        normalized_rows=[dict(case_id=r['case_id'],case_index=byid[r['case_id']]['case_index'],full_count_profile_sha256=r['full_count_profile_sha256'],proof_gate={k:r['proof_gate'][k]for k in ['path','sha256']},cnf_sha256=r['cnf_sha256'],proof_sha256=r['proof_sha256'],proof_bytes=r['proof_bytes'])for r in proof_rows]
        exact(read(raw_review),normalized_rows,'all producer-recorded prior proof identities checked separately')
        wanted_outputs={key(p)for p in [sp,lp,raw_review,*[sp.parent/f'partition_{i:02d}.json'for i in range(4)]]}
        need(set(meta['outputs_sha256'])==wanted_outputs,'all seven original selection outputs, no inferred output')
        controls=compare_controls(request,parent,parts,launch)
        save(out/'proof_identity_records.json',proof_rows);save(out/'controls.json',controls)
        need(time.perf_counter()-start<120,'bounded120-second identity review')
        report=dict(status=STATUS,timestamp=datetime.now(timezone.utc).isoformat(),command=[sys.executable,*sys.argv],inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in out.rglob('*')if p.is_file()},request_path=key(rp),request_sha256=args.request_sha256,selection_path=key(sp),selection_sha256=args.selection_sha256,launch_plan_path=key(lp),launch_plan_sha256=args.launch_plan_sha256,authorization_record_path=request['authorization_record_path'],authorization_record_sha256=request['authorization_record_sha256'],population_size=792,prior_proof_gate_counts=[r['completed_cases']for r in normalized],prior_verified_skips=len(skipped),prior_verified_case_ids=skipped,remaining_before_selection=792-len(skipped),selected_case_ids=ids,selected_case_indices=indices,selected_cases=64,overlap_with_prior_verified=[],build_partition_sizes=[16]*4,allocated_build_seconds_per_partition=120,total_allocated_build_seconds=480,checker_source_closure=sorted(map(key,closure)),controls=controls,scope='Prebuild selection/partition/provenance identities only; no new formula, launcher guarantee, native outcome, literal exclusion or fibre expansion.',new_formula_checks=0,new_solver_calls=0,new_proof_replays=0,producer_imports=0,git_commands=0,elapsed_seconds=time.perf_counter()-start)
        save(out/'summary.json',report);print(json.dumps(dict(status=STATUS,summary_sha256=sha(out/'summary.json'))))
    except BaseException as error:
        save(out/'failure.json',dict(error=repr(error),traceback=traceback.format_exc(),inputs_sha256=pins,source_sha256=sha(Path(__file__))));raise

if __name__=='__main__':main()
