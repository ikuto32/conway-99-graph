"""Explicit 56-checkpoint + eight-fresh batch04 continuation; no automatic retry."""
import argparse, copy, json, re, sys, traceback
from datetime import datetime, timezone
from pathlib import Path
import run_20260930_exact_eight_four_builds_v2 as backend

base=backend.base
ROOT=base.ROOT; A=base.A
SPEC=Path(__file__).with_name(Path(__file__).stem+'_spec.md')
B='acceleration/results/20261001_exact_eight_prefix64_batch04_'
AUTH='acceleration/theory_20261001_exact_eight_prefix64_batch04_continuation_plan.md'
PARENT=B+'selection/selection.json'; OLD_PLAN=B+'selection/launch_plan.json'
OLD_LAUNCHER=B+'build_launcher/summary.json'
BACKEND=Path(backend.__file__).resolve()
ENGINEERING='acceleration/results/20260930_independent_review/four_serial_build_engineering/summary.json'
CHECKPOINT_HASHES=[
 '9e8962290834f7b4297f0271d893554761aa7201e2f3fc7d75b965a9f9c84f69',
 'c762875f038cbc68310270fe93cf92aa5f0db107275ec30f3449255162b9b6a3',
 'cbd77901c9a93d02062591a24c350ca9b523c96b102835f1108468912fd605ca',
 '95c56dbd6a86f07c2678db0c99d2358475a76ff59d0f841c11f264f5bbd5ae3b',
]
PINS={
 PARENT:'c37c5ce7b3be8b2629abde0d0a65a8f479f049953f04b232daebf99e8bffbfcc',
 OLD_PLAN:'0db31ae7cf3756bf5a5d403829ec741e3a5b1f59c0f26600fab82f3f303c96b6',
 OLD_LAUNCHER:'a9af4f12d632f62a1dd8607cb8b00289cf5aedfd6076af933899a93dc01b405f',
 base.key(BACKEND):'11715c9438dc8749a80f62b5ee69646dbccee194c53a1a56ded1bff83a5601e8',
 base.key(backend.SPEC):'63941c78d5e60dd124b1ceb2a4ff6cb4ab1292712f7f312bb0f4ce2d82fbdc24',
 ENGINEERING:'206d943e8a399595856c9d6fa6673f6aef2b7b6faec8d1c060688f1121fd82e9',
}
PINS.update({base.key(p):h for p,h in backend.PINS.items()})
PREFLIGHT_STATUS='INDEPENDENT_EXACT_EIGHT_BATCH04_CONTINUATION_PREFLIGHT_PASS'
need=base.need; sha=base.sha; key=base.key; read=base.read; save=base.save

def file(name):
    need(type(name)is str and not name.startswith('tools/') and name not in ('PROMPT.md','CLAIMS.yaml') and not name.endswith('/process.stdout.log'),'allowed research file')
    return base.repo_file(name)

class Store:
    def __init__(self):self.pins={}
    def pin(self,name,expected=None):
        p=file(name); actual=sha(p)
        need(expected is None or actual==expected,'unchanged '+name)
        need(name not in self.pins or self.pins[name]==actual,'conflicting input identity')
        self.pins[name]=actual
        # Raw payloads are hash-bound; independent formula review parses them.
        return read(p) if p.suffix=='.json' and p.name not in {'model.json','initial_domains.json','selected_profile.json'} else p
    def ref(self,name):return dict(path=name,sha256=self.pins[name])

def suffix(parent_ids,checkpoint):
    need(len(parent_ids)==16 and len(set(parent_ids))==16,'original16 IDs')
    completed=checkpoint['completed_records']; pending=checkpoint['pending_case_ids']
    need(len(completed)==14 and [r['case_id']for r in completed]==parent_ids[:14],'exact14 checkpoint prefix')
    need(pending==parent_ids[14:] and len(pending)==2,'exact two-case suffix')
    need(checkpoint['selected_case_ids']==parent_ids and checkpoint['native_calls']==0 and checkpoint['producer_calls']==14,'checkpoint scope')
    return list(pending)

def receipt(st,folder,index,command_record):
    p=folder+f'/case_{index:03d}.receipt.json'; r=st.pin(p)
    need(r['command']==command_record['command'] and r['case_id']==command_record['case_id'] and r['attempt_id']==command_record['attempt_id'],'literal producer receipt')
    need(type(r['actual_exit_code'])is int and r['actual_exit_code']==0 and not r['outer_guard_expired'] and r['producer_calls']==1 and r['native_calls']==0,'successful producer invocation, not a formula approval')
    return st.ref(p)

def record(st,r,p):
    need(r['case_id']==p['case_id'] and r['case_index']==p['case_index'] and r['subset_index']==p['subset_index'] and r['attempt_id']==p['attempt_id'],'literal retained/new record')
    names={'summary.json','instance.cnf','model.json','scope.json','selected_profile.json','initial_domains.json','selection.json','model_package.json'}
    need(set(r['files'])==names,'all eight raw record files')
    for n,v in r['files'].items():
        need(v['path']==p['output_path']+'/'+n,'exact child path')
        st.pin(v['path'],v['sha256']);need(file(v['path']).stat().st_size==v['bytes'],'raw size')
    s=read(file(r['files']['summary.json']['path']))
    need(s['status']=='CANDIDATE_EXACT_EIGHT_CAMPAIGN_LITERAL_FULL_GRAM_BUILT' and s['case_id']==r['case_id'] and s['attempt_id']==r['attempt_id'] and s['selected_full_count_sha256']==r['full_count_profile_sha256'] and s['native_calls']==0,'raw child completion/identity')
    for n,h in {**s['inputs_sha256'],**s['outputs_sha256']}.items():st.pin(n,h)
    for n in ['selectors','variables','clauses','initial_domain_sizes']:need(s[n]==r[n],'actual recorded dimensions')

def old_state(st):
    parent=st.pin(PARENT,PINS[PARENT]); ids=base.selection_ids(parent,read(base.MANIFEST)); need(len(ids)==64,'original parent64')
    plan=st.pin(OLD_PLAN,PINS[OLD_PLAN]); launch=st.pin(OLD_LAUNCHER,PINS[OLD_LAUNCHER])
    need(plan['workers']==4 and plan['seconds_per_chunk']==120 and len(plan['build_selections'])==4,'original allocation')
    rs=launch['monitor']['receipts'];need(len(rs)==4 and not launch['monitor']['failure'] and not launch['monitor']['stop_errors'],'old stop metadata')
    need(launch['selected_case_ids']==ids and launch['native_calls']==0 and launch['build_invocations']==4,'old attempted selection')
    parts=[]; retained=[]; repeated=[]
    for i,(entry,rr)in enumerate(zip(plan['build_selections'],rs)):
        need(rr['chunk']==i and rr['stop_reason']=='CHUNK_DEADLINE' and rr['actual_exit_code']==1223 and rr['reaped'] and rr['job_active_zero_observed'] and not rr['cleanup_errors'],'old terminated and reaped tree')
        for name,v in launch['chunks'][i]['preserved_files'].items():
            st.pin(name,v['sha256']);need(file(name).stat().st_size==v['bytes'],'preserved interrupted output')
        part=st.pin(entry['path'],entry['sha256']); part_ids=base.selection_ids(part,read(base.MANIFEST))
        need(part_ids==ids[i*16:i*16+16] and part['partition_index']==i and part['parent_selection_path']==PARENT and part['parent_selection_sha256']==PINS[PARENT],'original literal partition')
        folder=B+f'cnfs_part{i:02d}';need(entry['out']==folder and not (ROOT/folder/'summary.json').exists(),'do not fabricate original terminal success')
        cp_path=folder+'/checkpoint_014.json';cp=st.pin(cp_path,CHECKPOINT_HASHES[i]); pending=suffix(part_ids,cp)
        need(cp['selection_sha256']==entry['sha256'],'checkpoint binds original selection')
        p=st.pin(folder+'/plan.json');need(p['ordered_case_ids']==part_ids and p['allocation_seconds']==120 and p['selection_sha256']==entry['sha256'] and len(p['commands'])==16,'original producer plan')
        actual_receipts=sorted(q.name for q in (ROOT/folder).glob('case_*.receipt.json'))
        need(actual_receipts==[f'case_{k:03d}.receipt.json'for k in range(15)],'exact15 original producer receipts')
        recs=[receipt(st,folder,k,p['commands'][k])for k in range(15)]
        for k,r in enumerate(cp['completed_records']):record(st,r,p['commands'][k])
        retained.extend(cp['completed_records']);repeated.append(part_ids[14])
        parts.append(dict(partition_index=i,original_partition=st.ref(entry['path']),retained_checkpoint=st.ref(cp_path),pending_case_ids=pending,retained_prefix_count=14,old_producer_calls=15,old_receipts=recs,unaccepted_completed_child=p['commands'][14],old_plan=st.ref(folder+'/plan.json')))
    need(len(retained)==56 and len({r['case_id']for r in retained})==56,'exact retained56')
    return parent,ids,parts,retained,repeated

def child_selection(parent,oldpart,info,auth):
    s=copy.deepcopy(oldpart)
    s.update(selection_policy='AUTHORIZED_CHECKPOINT_SUFFIX_CONTINUATION_V1',ordered_case_ids=info['pending_case_ids'],selected_instances=2,
        selection_reason='Explicit batch04 continuation: only the two saved pending IDs; preserve fourteen checkpointed records and all unaccepted outputs.',
        authorization_record_path=auth['path'],authorization_record_sha256=auth['sha256'],original_partition=info['original_partition'],retained_checkpoint=info['retained_checkpoint'],
        interrupted_launcher=dict(path=OLD_LAUNCHER,sha256=PINS[OLD_LAUNCHER]),retained_prefix_count=14)
    return s

def validate_launch(st,path,pin,fresh):
    launch=st.pin(path,pin);parent,ids,parts,retained,repeated=old_state(st)
    need(launch['schema']=='EXACT_EIGHT_FOUR_CHECKPOINT_SUFFIX_BUILD_PLAN_V1' and launch['workers']==4 and launch['seconds_per_chunk']==120,'explicit four by two allocation')
    need(launch['original_selection']==st.ref(PARENT) and launch['interrupted_launcher']==st.ref(OLD_LAUNCHER) and launch['original_launch_plan']==st.ref(OLD_PLAN),'old identity references')
    auth=launch['authorization'];need(auth['path']==AUTH,'specific root-adopted continuation plan');st.pin(auth['path'],auth['sha256'])
    need(launch['retained_checkpoints']==[p['retained_checkpoint']for p in parts] and launch['original_producer_calls']==60 and launch['additional_allocated_producer_calls']==8 and launch['repeated_uncheckpointed_case_ids']==repeated,'literal60+8 accounting')
    entries=launch['build_selections'];need(len(entries)==4,'four fresh serial invocations')
    for i,(entry,info)in enumerate(zip(entries,parts)):
        s=st.pin(entry['path'],entry['sha256']);old=read(file(info['original_partition']['path']))
        need(s==child_selection(parent,old,info,auth),'exact saved suffix selection')
        need(entry['out']==B+f'continuation_cnfs_part{i:02d}' and entry['attempt_id']==f'prefix64-batch04-continuation-part{i:02d}-build-attempt01','fixed fresh paths/attempts')
        if fresh:need(not (ROOT/entry['out']).exists(),'no continuation output overwrite')
    return launch,ids,parts,retained,repeated

def prepare(args,st,out):
    need(key(out)==B+'continuation_selection','exact fresh selection directory')
    need(args.authorization==AUTH,'exact candidate authorization path');st.pin(AUTH,args.authorization_sha256)
    parent,ids,parts,retained,repeated=old_state(st);auth=st.ref(AUTH);entries=[]
    for i,info in enumerate(parts):
        p=out/f'partition_{i:02d}.json';save(p,child_selection(parent,read(file(info['original_partition']['path'])),info,auth));st.pin(key(p))
        entries.append(dict(path=key(p),sha256=sha(p),attempt_id=f'prefix64-batch04-continuation-part{i:02d}-build-attempt01',out=B+f'continuation_cnfs_part{i:02d}'))
    plan=dict(schema='EXACT_EIGHT_FOUR_CHECKPOINT_SUFFIX_BUILD_PLAN_V1',original_selection=st.ref(PARENT),original_launch_plan=st.ref(OLD_PLAN),interrupted_launcher=st.ref(OLD_LAUNCHER),retained_checkpoints=[p['retained_checkpoint']for p in parts],authorization=auth,workers=4,seconds_per_chunk=120,build_selections=entries,original_producer_calls=60,additional_allocated_producer_calls=8,repeated_uncheckpointed_case_ids=repeated)
    save(out/'launch_plan.json',plan)
    save(out/'summary.json',dict(status='CANDIDATE_BATCH04_CHECKPOINT_CONTINUATION_PREPARED',inputs_sha256=st.pins,selected_case_ids=ids,retained_count=56,pending_case_ids=[c for p in parts for c in p['pending_case_ids']],original_producer_calls=60,additional_allocated_producer_calls=8,native_calls=0,build_invocations=0,outputs_sha256={key(p):sha(p)for p in out.iterdir()if p.is_file()}))

def build(args,st,out):
    need(key(out)==B+'continuation_build_launcher','exact fresh continuation launcher directory')
    plan,ids,parts,retained,repeated=validate_launch(st,args.launch_plan,args.launch_plan_sha256,True)
    eg=st.pin(ENGINEERING,PINS[ENGINEERING]);need(eg['status']=='INDEPENDENT_FOUR_SERIAL_BUILD_ENGINEERING_PASS','frozen backend gate')
    for n,h in eg['inputs_sha256'].items():st.pin(n,h)
    need(eg['inputs_sha256'][key(BACKEND)]==PINS[key(BACKEND)],'direct unchanged backend binding')
    gate=st.pin(args.prebuild_gate,args.prebuild_gate_sha256);need(gate['status']==PREFLIGHT_STATUS,'new independent continuation gate')
    for n,h in gate['inputs_sha256'].items():st.pin(n,h)
    for n in [key(Path(__file__)),key(SPEC),args.launch_plan,AUTH,ENGINEERING,PARENT,OLD_PLAN,OLD_LAUNCHER]+[p['retained_checkpoint']['path']for p in parts]:need(gate['inputs_sha256'].get(n)==st.pins[n],'direct continuation gate binding '+n)
    entries=plan['build_selections'];commands=[[sys.executable,'-B',str(backend.SERIAL),'build','--selection',str(ROOT/e['path']),'--selection-sha256',e['sha256'],'--attempt-id',e['attempt_id'],'--seconds','120','--out',str(ROOT/e['out'])]for e in entries]
    save(out/'prepared_commands.json',dict(inputs_sha256=st.pins,commands=commands,seconds_per_chunk=120,total_allocated_build_seconds=480,maximum_workers=4,native_calls=0,automatic_retry=False))
    trees=[];result=None
    try:
        for i,cmd in enumerate(commands):trees.append(backend.SuspendedTree(cmd,ROOT,out/f'chunk_{i:02d}.stdout.log',out/f'chunk_{i:02d}.stderr.log'))
        result=backend.monitor(trees,seconds=120)
        need(not result['stop_errors'] and all(r.get('reaped') and r.get('job_active_zero_observed') and not r.get('cleanup_errors')for r in result['receipts']),'every continuation tree reaped')
        chunks=[]
        for i,e in enumerate(entries):
            folder=ROOT/e['out'];p=folder/'summary.json'
            chunks.append(dict(chunk=i,selection=e,process_receipt=result['receipts'][i],summary_path=key(p)if p.is_file()else None,summary_sha256=sha(p)if p.is_file()else None,preserved_files={key(q):dict(sha256=sha(q),bytes=q.stat().st_size)for q in folder.rglob('*')if q.is_file()}if folder.exists()else{}))
        save(out/'summary.json',dict(status='CANDIDATE_BATCH04_CONTINUATION_INVOCATIONS_RECORDED',inputs_sha256=st.pins,launch_plan=dict(path=args.launch_plan,sha256=args.launch_plan_sha256),chunks=chunks,monitor=result,build_invocations=sum(t.resumed for t in trees),native_calls=0,automatic_retry=False,consolidation_required=True,outputs_sha256={key(p):sha(p)for p in out.iterdir()if p.is_file()}))
    except BaseException:
        if result is None:
            for t in trees:
                try:t.request_stop('CONTINUATION_LAUNCH_FAILURE')
                except BaseException:pass
            cleanup=[]
            for t in trees:
                try:cleanup.append(t.cleanup())
                except BaseException as e:cleanup.append(dict(error=repr(e)))
        else:cleanup=result
        save(out/'cleanup_failure.json',dict(cleanup=cleanup,native_calls=0));raise

def consolidate(args,st,out):
    need(key(out)==B+'continuation_consolidated','new labelled consolidation')
    need(re.fullmatch('[0-9a-f]{40}',args.recorded_source_commit) is not None,'literal recorded source commit')
    plan,ids,parts,retained,repeated=validate_launch(st,args.launch_plan,args.launch_plan_sha256,False)
    launcher=st.pin(args.continuation_launcher,args.continuation_launcher_sha256)
    need(args.continuation_launcher==B+'continuation_build_launcher/summary.json' and launcher['status']=='CANDIDATE_BATCH04_CONTINUATION_INVOCATIONS_RECORDED','actual continuation launcher')
    need(launcher['launch_plan']==dict(path=args.launch_plan,sha256=args.launch_plan_sha256) and launcher['build_invocations']==4 and launcher['native_calls']==0,'actual four invocations')
    need(not launcher['monitor']['failure'] and not launcher['monitor']['stop_errors'] and len(launcher['chunks'])==4,'complete launcher report')
    new=[];summaries=[]
    for i,e in enumerate(plan['build_selections']):
        ch=launcher['chunks'][i];rr=ch['process_receipt']
        need(ch['selection']==e and rr['actual_exit_code']==0 and rr['stop_reason']=='SERIAL_ROOT_EXIT' and rr['reaped'] and rr['job_active_zero_observed'] and not rr['cleanup_errors'],'successful actual new serial process')
        for n,v in ch['preserved_files'].items():st.pin(n,v['sha256']);need(file(n).stat().st_size==v['bytes'],'preserved new bytes')
        folder=e['out'];s=st.pin(folder+'/summary.json',ch['summary_sha256']);p=st.pin(folder+'/plan.json')
        need(ch['summary_path']==folder+'/summary.json' and s['status']=='CANDIDATE_EXACT_EIGHT_EXPLICIT_FORMULAS_COMPLETE' and s['selected_case_ids']==parts[i]['pending_case_ids'] and s['pending_case_ids']==[] and s['completed_formulas']==s['producer_calls']==2 and s['native_calls']==0,'two complete fresh formulas only')
        need(p['ordered_case_ids']==parts[i]['pending_case_ids'] and p['selection_sha256']==e['sha256'] and p['attempt_id']==e['attempt_id'] and len(p['commands'])==2,'exact continuation commands')
        need(p['allocation_seconds']==120 and p['mode']=='build' and p['native_calls']==0 and p['automatic_resume']is False and p['automatic_skip']is False and p['previous_outcomes_consumed']==0,'unchanged serial plan semantics')
        for n,h in {**s['inputs_sha256'],**s['outputs_sha256']}.items():st.pin(n,h)
        for k in [1,2]:
            chk=st.pin(folder+f'/checkpoint_{k:03d}.json')
            need(chk==dict(status='CANDIDATE_EXPLICIT_BUILD_PREFIX',selected_case_ids=parts[i]['pending_case_ids'],completed_records=s['records'][:k],pending_case_ids=parts[i]['pending_case_ids'][k:],native_calls=0,producer_calls=k,selection_sha256=e['sha256'],automatic_resume=False,automatic_skip=False),'exact fresh checkpoint chain')
        for k,r in enumerate(s['records']):receipt(st,folder,k,p['commands'][k]);record(st,r,p['commands'][k]);new.append(r)
        summaries.append(st.ref(folder+'/summary.json'))
    allrecords=retained+new;byid={r['case_id']:r for r in allrecords}
    need(len(new)==8 and len(allrecords)==len(byid)==64 and set(byid)==set(ids),'exact disjoint56+8 covers parent64')
    save(out/'summary.json',dict(schema='EXACT_EIGHT_CHECKPOINT_CONTINUATION_CONSOLIDATION_V1',status='CANDIDATE_EXACT_EIGHT_EXPLICIT_FORMULAS_COMPLETE',timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=st.pins,selected_case_ids=ids,records=[byid[c]for c in ids],pending_case_ids=[],completed_formulas=64,original_selection=st.ref(PARENT),original_launch_plan=st.ref(OLD_PLAN),interrupted_launcher=st.ref(OLD_LAUNCHER),retained_checkpoints=[p['retained_checkpoint']for p in parts],continuation_launch_plan=st.ref(args.launch_plan),continuation_launcher=st.ref(args.continuation_launcher),build_selections=plan['build_selections'],build_summaries=summaries,retained_checkpoint_records=56,new_formula_records=8,original_producer_calls=60,new_producer_calls=8,producer_calls=68,repeated_uncheckpointed_case_ids=repeated,native_calls=0,recorded_source_commit=args.recorded_source_commit,source_commit=args.recorded_source_commit,source_sha256=sha(Path(__file__)),command=[sys.executable,*sys.argv],automatic_resume=False,automatic_skip=False,automatic_retry=False,independent_approval=False))

def main():
    ap=argparse.ArgumentParser();sp=ap.add_subparsers(dest='mode',required=True)
    for mode in ['prepare','build','consolidate']:
        p=sp.add_parser(mode);p.add_argument('--out',type=Path,required=True)
        if mode=='prepare':p.add_argument('--authorization',required=True);p.add_argument('--authorization-sha256',required=True)
        else:p.add_argument('--launch-plan',required=True);p.add_argument('--launch-plan-sha256',required=True)
        if mode=='build':p.add_argument('--prebuild-gate',required=True);p.add_argument('--prebuild-gate-sha256',required=True)
        if mode=='consolidate':p.add_argument('--continuation-launcher',required=True);p.add_argument('--continuation-launcher-sha256',required=True);p.add_argument('--recorded-source-commit',required=True)
    a=ap.parse_args();out=a.out.resolve();need(out.is_relative_to(ROOT/'acceleration/results'),'repository result directory');out.mkdir(parents=True,exist_ok=False);st=Store()
    try:
        for n,h in PINS.items():st.pin(n,h)
        for p in [Path(__file__),SPEC,base.SPEC]:st.pin(key(p))
        {'prepare':prepare,'build':build,'consolidate':consolidate}[a.mode](a,st,out)
        print(json.dumps(dict(summary_path=key(out/'summary.json'),summary_sha256=sha(out/'summary.json'),mode=a.mode)))
    except BaseException as e:
        save(out/'failure.json',dict(error=repr(e),traceback=traceback.format_exc(),inputs_sha256=st.pins,command=[sys.executable,*sys.argv],native_calls=0,automatic_retry=False));raise

if __name__=='__main__':main()
