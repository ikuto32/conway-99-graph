"""Prepared gated serial native campaign; no execution on import."""
from datetime import datetime,timezone
from pathlib import Path
import argparse,json,platform,shutil,subprocess,sys,time
import native_20260930_unrestricted_full99 as h
import native_20260930_proof_location as e
import theory_20260930_hadamard_four_profile_cnf as producer
ROOT=h.ROOT;B=ROOT/'acceleration/results'
DATA=B/'20260930_hadamard_four_profile_cnfs'
BATCH=DATA/'summary.json'
SELECTION=B/'20260930_independent_review/hadamard_remaining_profile_universe/summary.json'
SPEC=Path(__file__).with_name('native_20260930_hadamard_four_profile_batch_spec.md')
PRODUCER_SPEC=Path(producer.__file__).with_name('theory_20260930_hadamard_four_profile_cnf_spec.md')
ENCODING_STATUS='INDEPENDENT_HADAMARD_FIFTEEN_PROFILE_ENCODING_PASS'
OBJECT_STATUS='INDEPENDENT_HADAMARD_FIFTEEN_PROFILE_OBJECT_CALIBRATION_PASS'
LIMITS=dict(native_wall_seconds_per_case=60,conflicts_per_case=1000000,address_space_bytes=e.AS_LIMIT,individual_trace_bytes=e.FILE_LIMIT,kill_after_seconds=5,outer_guard_seconds=70,campaign_wrapped_wall_seconds=900,next_launch_reserve_seconds=70,total_retained_trace_soft_bytes=2*1024**3,host_free_reserve_bytes=21*1024**3,ext4_free_reserve_bytes=11*1024**3,maximum_cases=15,automatic_retry=False)
PINS={BATCH:'692f74a5bf3be681832978d2a0ec51ec373237d45f3df24ccf1c01cfb009584b',SELECTION:'dffd4d638ee0cfca637a6ae4ba1a5cff5d7cb40d50f0dad2a9dd8f3ac79853ec',Path(producer.__file__):'0b4b737486974a499026bee4146cc7b461b654aeeb5af46e0553e908fa012f2f',PRODUCER_SPEC:'929c19abc9d0cdd8292148c71d0b0b4b7addf79ddb1618a886b0994b86159113',Path(h.__file__):'da7ee9c03d454bd5ad0af0d82bead3520f3f270c70e71d4355161d036fd8ef22',Path(e.__file__):'ff7fd55658b7cb63e9586bd862f8f182269f2978a3b873ba9afccfa41a345854',ROOT/'uv.lock':'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',ROOT/'pyproject.toml':'273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339',h.NATIVE:h.NATIVE_SHA,h.CHECKER:h.CHECKER_SHA}
PINS.update(producer.PINS)
def source_closure():
    paths={producer.BASE.resolve(),Path(__file__).resolve(),SPEC.resolve(),PRODUCER_SPEC.resolve()}
    for module in tuple(sys.modules.values()):
        filename=getattr(module,'__file__',None)
        if filename:
            path=Path(filename).resolve()
            if path.is_relative_to(ROOT/'acceleration') and path.suffix=='.py':paths.add(path)
    return paths
def preflight(args):
    bindings={}
    for path,digest in PINS.items():h.require(h.digest(path)==digest,'frozen source/input/tool '+h.key(path));bindings[h.key(path)]=digest
    selection=h.read(SELECTION);batch=h.read(BATCH);cases=selection['remaining_representatives'];records=batch['records'];h.require(cases==batch['selection']==[r['case'] for r in records] and len(cases)==15,'exact immutable15-case selection')
    direct=[BATCH,SELECTION,producer.RAW,Path(producer.__file__),PRODUCER_SPEC]
    for record in records:
        for field in ('cnf','model','scope'):
            path=ROOT/record[field+'_path'];digest=record[field+'_sha256'];h.require(h.digest(path)==digest,'actual case input');bindings[h.key(path)]=digest;direct.append(path)
        with (ROOT/record['cnf_path']).open('rb') as f:h.require(f.readline()==f"p cnf {record['variables']} {record['clauses']}\n".encode(),'exact formula header')
        scope=h.read(ROOT/record['scope_path']);h.require(scope['selected_case']==record['case'] and scope['within_group_column_caps_encoded'] and not scope['cross_group_column_caps_encoded'] and not scope['residual_D_encoded'] and not scope['target_graph'],'literal percase scope/omissions')
    reports=[]
    for gate_path,digest,status in [(args.encoding_gate,args.encoding_gate_sha256,ENCODING_STATUS),(args.object_gate,args.object_gate_sha256,OBJECT_STATUS)]:
        report=h.checked_gate(gate_path,digest,status);reports.append(report)
        for name,value in report['inputs_sha256'].items():h.require(h.digest(ROOT/name)==value,'unchanged gate input '+name);bindings[name]=value
        for path in direct:h.require(report['inputs_sha256'][h.key(path)]==h.digest(path),'direct fullbatch gate binding '+h.key(path))
        bindings[h.key(gate_path)]=digest
    h.require(reports[1]['inputs_sha256'][h.key(args.encoding_gate)]==args.encoding_gate_sha256,'object gate binds same encoding')
    for path in source_closure()|{args.object_checker.resolve()}:
        digest=h.digest(path);h.require(reports[1]['inputs_sha256'][h.key(path)]==digest,'object gate complete native/checker closure '+h.key(path));bindings[h.key(path)]=digest
    bindings[h.key(args.encoding_gate)]=args.encoding_gate_sha256;bindings[h.key(args.object_gate)]=args.object_gate_sha256
    for name,digest,status in [('20260930_native_cli_calibration','f5ff562aff2ec550a97685c7012b302e760314a6f3829d80d022e2a669e680eb','INDEPENDENT_NATIVE_CADICAL195_CLI_CALIBRATION_PASS'),('20260930_native_proof_location','d1036cfcbe9b24e0f7ea6e0a3799968a5d9232e8167fb31b224211e5c845c619','NATIVE_EXT4_PROOF_PATH_CALIBRATION_PASS')]:
        path=B/name/'summary.json';h.checked_gate(path,digest,status);bindings[h.key(path)]=digest
    return bindings,records
def observe(prefix):
    receipt=h.run_record([*h.WSL,'/usr/bin/ps','-C','cadical','-o','pid,ppid,comm,pcpu,rss,args'],prefix,10);h.require(not receipt['outer_windows_guard_expired'] and receipt['actual_exit_code'] in (0,1),'targeted named process observation')
    if receipt['actual_exit_code']==1:h.require(len(Path(str(prefix)+'.stdout.log').read_text().strip().splitlines())<=1,'no matching named process')
    return receipt
def resources(folder,linux_path='/tmp'):
    host=shutil.disk_usage(ROOT).free;mount,text=e.local_capture(['/usr/bin/findmnt','--target',linux_path,'--output','TARGET,SOURCE,FSTYPE,OPTIONS','--noheadings'],folder/'filesystem');h.require('ext4' in text.split(),'ext4 proof mount')
    disk,text=e.local_capture(['/usr/bin/df','--output=avail','-B1',linux_path],folder/'disk_free');free=int(text.splitlines()[-1]);return dict(host_free_bytes=host,ext4_free_bytes=free,mount_receipt=mount,disk_receipt=disk,pass_reserves=host>=LIMITS['host_free_reserve_bytes'] and free>=LIMITS['ext4_free_reserve_bytes'])
def literal_factor(decoded,scope):
    f=decoded['factor'];c=scope['core_adjacency36'];h.require(len(f)==36 and all(len(row)==60 and all(type(x) is int and x in(0,1) for x in row) for row in f),'complete binary36x60')
    gram=[[sum(f[i][d]*f[j][d] for d in range(60)) for j in range(36)] for i in range(36)];h.require(gram==scope['prescribed_Gram36'],'literal1296 Gram entries');h.require(all(sum(row)==10 for row in f),'row margins')
    h.require(all(sum(f[12*g+a][d] for a in range(12))==2 for g in range(3) for d in range(60)),'fibre margins');h.require([[sum(f[12*g+a][d] for g in range(3)) for d in range(60)] for a in range(12)]==scope['L12x60'],'literal support')
    caps=[dict(columns=[d,z],overlap=sum(f[a][d]*f[a][z] for a in range(36))) for d in range(60) for z in range(d+1,60)];violations=[x for x in caps if x['overlap']>2];mixed=[dict(row=a,column=d,value=f[a][d]+sum(c[a][b]*f[b][d] for b in range(36))) for a in range(36) for d in range(60)];mixedbad=[x for x in mixed if x['value']>2]
    h.require(caps==decoded['checks']['column_pair_records'] and violations==decoded['checks']['column_cap_violations'] and mixedbad==decoded['checks']['mixed_cap_violations'],'literal diagnostic agreement')
    return dict(status='PRODUCER_LITERAL_GRAM_CHECK_ONLY',Gram_entries=1296,column_pairs=1770,mixed_entries=2160,column_pair_records=caps,column_cap_violations=violations,mixed_cap_violations=mixedbad,target_graph=False,residual_D=None,independent_approval=False)
def load_resume(args,bindings,selection,out):
    if args.resume_checkpoint is None:
        h.require(args.resume_checkpoint_sha256 is None,'resume hash requires checkpoint');return None,[]
    h.require(args.resume_checkpoint_sha256 is not None,'resume requires externally supplied checkpoint hash')
    checkpoint=args.resume_checkpoint.resolve();h.require(h.digest(checkpoint)==args.resume_checkpoint_sha256,'explicit resume checkpoint identity');state=h.read(checkpoint)
    h.require(state['status'] in ('FIFTEEN_PROFILE_NATIVE_CAMPAIGN_CHECKPOINT','FIFTEEN_PROFILE_NATIVE_CAMPAIGN_STOPPED'),'research resume checkpoint only')
    h.require(state['inputs_sha256']==bindings and state['selected_cases']==[r['case'] for r in selection],'resume input/selection identity')
    h.require(state['stop_reason'] not in ('SAT_PENDING_INDEPENDENT_REVIEW','TRACE_IDENTITY_UNAVAILABLE','OUTER_GUARD_PROCESS_STATE_UNKNOWN','PROCESS_OBSERVATION_FAILED'),'resume requires separate review after incomplete/SAT outcome')
    manifest_path=ROOT/state['manifest_path'];h.require(h.digest(manifest_path)==state['manifest_sha256'],'resume source manifest identity');manifest=h.read(manifest_path)
    h.require(manifest['inputs_sha256']==bindings and manifest['limits']==LIMITS and manifest['mode']=='RESEARCH','unchanged research campaign bindings/limits')
    origin=manifest['campaign_manifest'];h.require(origin==state['campaign_manifest'] and h.digest(ROOT/origin['path'])==origin['sha256'],'initial fixed campaign manifest');initial=h.read(ROOT/origin['path'])
    h.require(initial['inputs_sha256']==bindings and initial['limits']==LIMITS and initial['selection']==[r['case'] for r in selection],'initial frozen protocol')
    records=state['case_records'];h.require([r['case'] for r in records]==[r['case'] for r in selection[:len(records)]] and len(records)<=15,'completed attempts form exact selection prefix')
    seen=set();prior_folders={manifest_path.parent}
    for r,selected in zip(records,selection):
        seen.add(r['case']);path=ROOT/r['summary_path'];prior_folders.add(path.parent.parent);h.require(h.digest(path)==r['summary_sha256'],'completed case summary pin');case=h.read(path)
        h.require(case['case']==r['case'] and case['inputs_sha256']==bindings,'case identity/input bindings')
        for field in ('cnf','model','scope'):h.require(case[field+'_sha256']==selected[field+'_sha256'],'case exact formula scope')
        for name,digest in case['outputs_sha256'].items():h.require(h.digest(ROOT/name)==digest,'previous raw output pin')
        native=case['native_receipt'];h.require(native['actual_exit_code']!=10 and not native['outer_windows_guard_expired'] and 'proof_copy' in case and case['stop_reason'] is None,'no automatic retry/resume past incomplete or SAT outcome')
        proof=case['proof_copy'];host_proof=path.parent/'main/proof.drat';h.require(h.digest(host_proof)==proof['sha256'] and host_proof.stat().st_size==proof['bytes'],'saved host proof identity')
        h.require(r['wrapped_wall_seconds']==native['wall_seconds'] and r['retained_raw_trace_bytes']==2*proof['bytes']==case['retained_raw_trace_bytes'] and r['interpreted_result']==case['interpreted_result'],'resume accounting derived from authenticated receipts')
        expected=e.command(60,[h.linux(h.NATIVE),'--no-binary','-c','1000000',h.linux(ROOT/selected['cnf_path']),proof['linux_source']]);h.require(native['command']==expected,'exact previous solver command')
        receipt,text=e.local_capture(['/usr/bin/sha256sum',proof['linux_source']],out/f'resume_case_{r["case"]:03d}_ext4');h.require(text.split()[0]==proof['sha256'],'preserved ext4 original on resume')
    for prior in prior_folders:
        for folder in prior.glob('case_*'):
            if folder.is_dir() and (folder/'main/launch.json').exists():h.require((folder/'summary.json').exists() and h.read(folder/'summary.json')['case'] in seen,'later or incomplete launch cannot be omitted/retried automatically')
    return origin,records
def one_case(args,record,out,bindings):
    case=record['case'];folder=out/f'case_{case:03d}';folder.mkdir();cnf=ROOT/record['cnf_path'];model=ROOT/record['model_path'];scope=ROOT/record['scope_path'];before=observe(folder/'processes_before')
    made,directory=e.local_capture(['/usr/bin/mktemp','-d',f'/tmp/conway99-profile-{case:03d}-XXXXXX'],folder/'mktemp');h.require(directory.startswith(f'/tmp/conway99-profile-{case:03d}-') and '\n' not in directory,'fresh ext4 workspace');h.save(folder/'workspace.json',dict(path=directory,preserved=True,receipt=made))
    reserve=resources(folder,directory)
    if not reserve['pass_reserves']:
        h.save(folder/'not_launched.json',dict(reason='HOST_OR_EXT4_RESERVE',resource_check=reserve));return None,'HOST_OR_EXT4_RESERVE'
    main=folder/'main';main.mkdir();proof=directory+'/proof.drat';command=e.command(60,[h.linux(h.NATIVE),'--no-binary','-c','1000000',h.linux(cnf),proof]);h.save(main/'launch.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),case=case,command=command,cnf_sha256=record['cnf_sha256'],ext4_proof=proof,inputs_sha256=bindings))
    print(json.dumps(dict(state='NATIVE_PROFILE_LAUNCH',case=case,variables=record['variables'],clauses=record['clauses'],wall_seconds=60)),flush=True);native=h.run_record(command,main/'solver',70)
    result=dict(status='NATIVE_PROFILE_RESULT_PENDING_INDEPENDENT_REVIEW',case=case,timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=bindings,native_receipt=native,processes_before=before,resource_check=reserve,cnf_sha256=record['cnf_sha256'],model_sha256=record['model_sha256'],scope_sha256=record['scope_sha256'],research_calls=1,target_resolution=False,independent_approval=False);stop=None
    if native['outer_windows_guard_expired']:stop='OUTER_GUARD_PROCESS_STATE_UNKNOWN'
    else:
        began=time.monotonic()
        try:result['proof_copy']=e.proof_copy(proof,main/'proof.drat',main/'transfer');h.require(result['proof_copy']['bytes']<=e.FILE_LIMIT,'individual proof cap')
        except BaseException as error:result['proof_copy_failure']=dict(error=repr(error),linux_original_path=proof,sha256=None,reason='Complete identity unavailable; preserved raw paths/receipts require manual review.');stop='TRACE_IDENTITY_UNAVAILABLE'
        result['proof_transfer_and_hash_wall_seconds']=time.monotonic()-began
        if native['actual_exit_code']==10:
            stop='SAT_PENDING_INDEPENDENT_REVIEW'
            try:
                assignment=h.parse_sat_stdout((main/'solver.stdout.log').read_text(),record['variables']);h.save(main/'parsed_model.json',dict(assignment=assignment))
            except BaseException as error:result['assignment_parse_failure']=repr(error)
            if (main/'parsed_model.json').exists():
                try:
                    decoded=producer.decode(assignment,model,scope,cnf);h.save(main/'decoded_Gram_factor.json',decoded);h.save(main/'literal_factor_check.json',literal_factor(decoded,h.read(scope)))
                except BaseException as error:result['candidate_decode_failure']=repr(error)
                try:
                    check=[sys.executable,'-B',str(args.object_checker),'sat','--case',str(case),'--encoding-gate',str(args.encoding_gate),'--encoding-gate-sha256',args.encoding_gate_sha256,'--assignment',str(main/'parsed_model.json'),'--native-output',str(main/'solver.stdout.log'),'--out',str(folder/'independent_object')]
                    if (main/'decoded_Gram_factor.json').exists():check+=['--decoded',str(main/'decoded_Gram_factor.json')]
                    began=time.monotonic();result['independent_object_receipt']=h.run_record(check,folder/'independent_object_command',120);result['independent_object_checker_wall_seconds']=time.monotonic()-began
                except BaseException as error:result['independent_object_checker_failure']=repr(error)
        try:result['processes_after']=observe(folder/'processes_after')
        except BaseException as error:result['process_observation_failure']=repr(error);stop=stop or 'PROCESS_OBSERVATION_FAILED'
    code=native['actual_exit_code'];result['interpreted_result']='SAT_RAW_OBJECT_PENDING_REVIEW' if code==10 else 'UNSAT_COMPLETE_TRACE_UNCHECKED' if code==20 and 'proof_copy' in result else 'UNSAT_TRACE_UNAVAILABLE' if code==20 else 'UNKNOWN_NATIVE_OR_RESOURCE_OUTCOME';result['stop_reason']=stop
    result['retained_raw_trace_bytes']=2*result['proof_copy']['bytes'] if 'proof_copy' in result else None;result['retained_raw_trace_bytes_null_reason']=None if 'proof_copy' in result else 'At least one raw copy size/identity unconfirmed; campaign stops.'
    result['outputs_sha256']={h.key(p):h.digest(p) for p in folder.rglob('*') if p.is_file()};h.save(folder/'summary.json',result)
    return dict(case=case,summary_path=h.key(folder/'summary.json'),summary_sha256=h.digest(folder/'summary.json'),wrapped_wall_seconds=native['wall_seconds'],retained_raw_trace_bytes=result['retained_raw_trace_bytes'],interpreted_result=result['interpreted_result']),stop
def run(args):
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);started=time.monotonic()
    try:
        bindings,selection=preflight(args);origin,completed=load_resume(args,bindings,selection,out)
        if origin is None:
            path=out/'campaign_manifest.json';h.save(path,dict(timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=bindings,selection=[r['case'] for r in selection],limits=LIMITS,scope='Fifteen separate fullGram/within-group-cap profiles; no cross-group-cap or residualD encoding.'));origin=dict(path=h.key(path),sha256=h.digest(path))
        h.save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,limits=LIMITS,campaign_manifest=origin,mode='PREFLIGHT_ONLY' if args.preflight else 'RESEARCH',resume_checkpoint=None if args.resume_checkpoint is None else str(args.resume_checkpoint),resume_checkpoint_sha256=args.resume_checkpoint_sha256,automatic_retry=False))
        initial=resources(out);h.require(initial['pass_reserves'],'initial host/ext4 reserves')
        if args.preflight:h.save(out/'summary.json',dict(status='FIFTEEN_PROFILE_NATIVE_PREFLIGHT_PASS',research_calls=0,inputs_sha256=bindings,selection=[r['case'] for r in selection],resource_check=initial));return
        with (out/'progress.jsonl').open('x',encoding='utf-8',newline='\n') as f:
            for old in completed:f.write(json.dumps(old)+'\n')
        used=sum(r['wrapped_wall_seconds'] for r in completed);retained=sum(r['retained_raw_trace_bytes'] for r in completed);done={r['case'] for r in completed};stop='ALL_SELECTED_CASES_ATTEMPTED'
        state_base=dict(inputs_sha256=bindings,campaign_manifest=origin,manifest_path=h.key(out/'manifest.json'),manifest_sha256=h.digest(out/'manifest.json'),selected_cases=[r['case'] for r in selection])
        h.save(out/'checkpoint_initial.json',dict(status='FIFTEEN_PROFILE_NATIVE_CAMPAIGN_CHECKPOINT',**state_base,case_records=completed,stop_reason=None))
        for record in selection:
            if record['case'] in done:continue
            if used+70>900:stop='CAMPAIGN_WRAPPED_WALL_RESERVE';break
            if retained>=2*1024**3:stop='AGGREGATE_RETAINED_TRACE_SOFT_CAP';break
            r,reason=one_case(args,record,out,bindings)
            if r is None:stop=reason;break
            completed.append(r);done.add(r['case']);used+=r['wrapped_wall_seconds'];retained+=r['retained_raw_trace_bytes'] or 0
            with (out/'progress.jsonl').open('a',encoding='utf-8',newline='\n') as f:
                f.write(json.dumps(r)+'\n')
            h.save(out/f'checkpoint_case_{r["case"]:03d}.json',dict(status='FIFTEEN_PROFILE_NATIVE_CAMPAIGN_CHECKPOINT',**state_base,case_records=completed,stop_reason=reason))
            print(json.dumps(dict(state='NATIVE_PROFILE_COMPLETE',case=r['case'],result=r['interpreted_result'],used_wrapped_wall_seconds=used,retained_raw_trace_bytes=retained)),flush=True)
            if reason:stop=reason;break
        h.save(out/'summary.json',dict(status='FIFTEEN_PROFILE_NATIVE_CAMPAIGN_STOPPED',timestamp=datetime.now(timezone.utc).isoformat(),**state_base,case_records=completed,completed_attempts=len(completed),unattempted_cases=[r['case'] for r in selection if r['case'] not in done],stop_reason=stop,wrapped_solver_wall_seconds=used,retained_raw_trace_bytes_known=retained,raw_trace_counting='Both ext4 originals and host copies; unknown identities stop the campaign.',end_to_end_wall_seconds=time.monotonic()-started,target_resolution=False,independent_approval=False,automatic_retry=False,limitations=['UNSAT results require separate complete proof checking and exact profile/union coverage review.','UNKNOWN excludes nothing.','SAT stops for independent raw-factor checking; no residualD/full99 graph is established.','Transfer/hash/checker overhead is outside the900 wrapped-solver wall budget.']))
    except BaseException as error:
        h.save(out/'failure.json',dict(error=repr(error),source_sha256=h.digest(Path(__file__)),automatic_retry=False));raise
def main():
    p=argparse.ArgumentParser();m=p.add_mutually_exclusive_group(required=True);m.add_argument('--preflight',action='store_true');m.add_argument('--research',action='store_true')
    for name in ('out','encoding-gate','object-gate','object-checker'):p.add_argument('--'+name,type=Path,required=True)
    for name in ('encoding-gate-sha256','object-gate-sha256'):p.add_argument('--'+name,required=True)
    p.add_argument('--resume-checkpoint',type=Path);p.add_argument('--resume-checkpoint-sha256');run(p.parse_args())
if __name__=='__main__':main()
