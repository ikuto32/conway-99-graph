"""Prepared one-shot interval count pilot; raw SAT is checked only independently."""
from datetime import datetime,timezone
from pathlib import Path
import argparse,json,platform,shutil,subprocess,sys,time
import native_20260930_unrestricted_full99 as h
import native_20260930_proof_location as e

ROOT=h.ROOT;B=ROOT/'acceleration/results';DATA=B/'20260930_count_interval_cnf';BASE=B/'20260930_hadamard_count_master_cnf'
CNF=DATA/'instance.cnf';MODEL=DATA/'model.json';SCOPE=DATA/'scope.json';SPEC=Path(__file__).with_name('native_20260930_count_interval_spec.md')
BASE_GATE=B/'20260930_independent_review/hadamard_count_master_cnf_v2/summary.json';INTERVAL_GATE=B/'20260930_independent_review/count_gram_intervals/summary.json'
N=185963;M=7659287
ENCODING_STATUS='INDEPENDENT_COUNT_INTERVAL_ENCODING_PASS';OBJECT_STATUS='INDEPENDENT_COUNT_INTERVAL_OBJECT_CALIBRATION_PASS'
LIMITS=dict(native_wall_seconds=60,conflicts=1000000,address_space_bytes=4294967296,trace_file_bytes=10737418240,kill_grace_seconds=5,outer_guard_seconds=70,maximum_research_calls=1,automatic_retry=False,host_reserve_bytes=21*1024**3,ext4_reserve_bytes=11*1024**3)
PINS={CNF:'5ee253b41de8cfcc5529175c4685c0fc9a8886b8d6c3600e435ae9db5146cbab',MODEL:'ae40c085c48dc44b7a7438b4c707f2c16408258d4501e855b151200ef1b6c995',SCOPE:'5e7e1ee1dd23e327609dde81a6a137f8efb46171b1d7eca9907b4f20058ca6e3',DATA/'summary.json':'224eb5e1d016bda6ac903de5c59ab489c1c3d4c0abdc5ecf342c97d4f2ea0a84',BASE_GATE:'80137a50c7097a0ebec1d958e5e48fd05364ea9b84cfd5793a705a07a10e1888',INTERVAL_GATE:'ebace5fc527bded41f3c31fb66455e78b0eb133c8575508d4426eff912e6ae33',BASE/'model.json':'a9a354e2fc28bff8a8f986d69f3cfd30fc06de0d76e394e125ffff884debdc44',BASE/'at_least_seven.cnf':'f303edec9a91dc9bcecb95804ee151d0e38e8100b17c9c45a7b4d58b8edbf55e',Path(h.__file__):'da7ee9c03d454bd5ad0af0d82bead3520f3f270c70e71d4355161d036fd8ef22',Path(e.__file__):'ff7fd55658b7cb63e9586bd862f8f182269f2978a3b873ba9afccfa41a345854',h.NATIVE:h.NATIVE_SHA,h.CHECKER:h.CHECKER_SHA,ROOT/'uv.lock':'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',ROOT/'pyproject.toml':'273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339'}

def source_closure():
    paths={Path(__file__).resolve(),SPEC.resolve()}
    for module in tuple(sys.modules.values()):
        name=getattr(module,'__file__',None)
        if name:
            path=Path(name).resolve()
            if path.is_relative_to(ROOT/'acceleration')and path.suffix=='.py':
                paths.add(path);spec=path.with_name(path.stem+'_spec.md')
                if spec.exists():paths.add(spec)
    return paths

def preflight(args):
    bindings={}
    for p,digest in PINS.items():h.require(h.digest(p)==digest,'frozen input/source/tool '+h.key(p));bindings[h.key(p)]=digest
    summary=h.read(DATA/'summary.json')
    h.require(summary['status']=='CANDIDATE_EXACT_COUNT_INTERVAL_CNF_BUILT','completed candidate build')
    for p,digest in {**summary['inputs_sha256'],**summary['outputs_sha256']}.items():h.require(h.digest(ROOT/p)==digest,'producer artifact '+p);bindings[p]=digest
    model=h.read(MODEL);scope=h.read(SCOPE)
    h.require((model['variables'],model['clauses'])==(N,M)and model['cnf_path']==h.key(CNF)and model['cnf_sha256']==PINS[CNF],'literal interval formula')
    h.require(model['base_variant']=='at_least_seven'and model['base_model_path']==h.key(BASE/'model.json')and model['base_model_sha256']==PINS[BASE/'model.json'],'literal base-model binding')
    h.require(model['base_cnf_path']==h.key(BASE/'at_least_seven.cnf')and model['base_cnf_sha256']==PINS[BASE/'at_least_seven.cnf'],'literal base-CNF binding')
    h.require(model['scope_path']==h.key(SCOPE)and model['scope_sha256']==PINS[SCOPE]and not model['complete_factor']and not model['target_graph'],'literal scope/object type')
    h.require(all(scope[k]for k in ['necessary_only','complete_coordinate_count_domains','complete_group_count_signatures','at_least_seven_exceptional_groups','all_540_exact_signature_interval_bounds','within_group_caps_inherited']),'required count and interval scope')
    h.require(not any(scope[k]for k in ['cross_group_caps_encoded','full_Gram_encoded','residual_D_encoded','target_automorphism_assumed','full_factor','target_graph']),'omitted conditions and object scope')
    h.require(e.AS_LIMIT==LIMITS['address_space_bytes']and e.FILE_LIMIT==LIMITS['trace_file_bytes'],'engineering helper exact limits')
    with CNF.open('rb')as f:h.require(f.readline()==f'p cnf {N} {M}\n'.encode(),'exact header')
    h.checked_gate(BASE_GATE,PINS[BASE_GATE],'INDEPENDENT_HADAMARD_COUNT_MASTER_ENCODING_PASS');h.checked_gate(INTERVAL_GATE,PINS[INTERVAL_GATE],'INDEPENDENT_COUNT_SIGNATURE_GRAM_INTERVALS_PASS')
    reports=[];direct=[CNF,MODEL,SCOPE,DATA/'summary.json',BASE/'model.json',BASE/'at_least_seven.cnf',BASE_GATE,INTERVAL_GATE]
    for p,digest,status in [(args.encoding_gate,args.encoding_gate_sha256,ENCODING_STATUS),(args.object_gate,args.object_gate_sha256,OBJECT_STATUS)]:
        report=h.checked_gate(p,digest,status);reports.append(report)
        for name,value in report['inputs_sha256'].items():h.require(h.digest(ROOT/name)==value,'unchanged independent gate input '+name);bindings[name]=value
        for raw in direct:h.require(report['inputs_sha256'][h.key(raw)]==h.digest(raw),'direct raw/premise binding '+h.key(raw))
        bindings[h.key(p)]=digest
    h.require(reports[1]['inputs_sha256'][h.key(args.encoding_gate)]==args.encoding_gate_sha256,'same new interval encoding gate')
    for p in source_closure()|{args.object_checker.resolve(),h.NATIVE,h.CHECKER}:
        digest=h.digest(p);h.require(reports[1]['inputs_sha256'][h.key(p)]==digest,'object/runtime/checker closure '+h.key(p));bindings[h.key(p)]=digest
    for name,digest,status in [('20260930_native_cli_calibration','f5ff562aff2ec550a97685c7012b302e760314a6f3829d80d022e2a669e680eb','INDEPENDENT_NATIVE_CADICAL195_CLI_CALIBRATION_PASS'),('20260930_native_proof_location','d1036cfcbe9b24e0f7ea6e0a3799968a5d9232e8167fb31b224211e5c845c619','NATIVE_EXT4_PROOF_PATH_CALIBRATION_PASS')]:
        p=B/name/'summary.json';h.checked_gate(p,digest,status);bindings[h.key(p)]=digest
    return bindings

def observe(prefix):
    receipt=h.run_record([*h.WSL,'/usr/bin/ps','-C','cadical','-o','pid,ppid,comm,pcpu,rss,args'],prefix,10)
    h.require(not receipt['outer_windows_guard_expired']and receipt['actual_exit_code']in(0,1),'targeted native observation')
    if receipt['actual_exit_code']==1:h.require(len(Path(str(prefix)+'.stdout.log').read_text().strip().splitlines())<=1,'no exact-named process')
    return receipt

def run(args):
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);started=time.monotonic()
    try:
        bindings=preflight(args);mount,text=e.local_capture(['/usr/bin/findmnt','--target','/tmp','--output','TARGET,SOURCE,FSTYPE,OPTIONS','--noheadings'],out/'filesystem');h.require('ext4'in text.split(),'ext4 proof mount')
        disk,text=e.local_capture(['/usr/bin/df','--output=avail','-B1','/tmp'],out/'disk_free');host=shutil.disk_usage(ROOT).free;ext4=int(text.splitlines()[-1]);h.require(host>=LIMITS['host_reserve_bytes']and ext4>=LIMITS['ext4_reserve_bytes'],'host/ext4 reserves')
        h.save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,limits=LIMITS,mode='PREFLIGHT_ONLY'if args.preflight else'RESEARCH',host_free_bytes=host,ext4_free_bytes=ext4,mount_receipt=mount,disk_receipt=disk,scope='At-least-seven count relaxation plus exact-class Gram intervals; not a full factor or residual completion.',random_seed=None,random_seed_null_reason='Native default retained.',cpu_limit=None,cpu_limit_null_reason='Wall guard; no additional CPU rlimit.',shared_components=['Authenticated parser/native/ext4 engineering helpers.','Only a separately gated independent checker receives the raw SAT assignment; no producer decoder import.']))
        if args.preflight:h.save(out/'summary.json',dict(status='COUNT_INTERVAL_NATIVE_PREFLIGHT_PASS',research_calls=0,inputs_sha256=bindings));return
        before=observe(out/'processes_before');made,directory=e.local_capture(['/usr/bin/mktemp','-d','/tmp/conway99-count-interval-XXXXXX'],out/'mktemp');h.require(directory.startswith('/tmp/conway99-count-interval-')and '\n'not in directory,'fresh ext4 directory');h.save(out/'workspace.json',dict(path=directory,preserved=True,receipt=made));folder=out/'main';folder.mkdir();proof=directory+'/proof.drat'
        disk,text=e.local_capture(['/usr/bin/df','--output=avail','-B1',directory],out/'disk_before_launch');h.require(shutil.disk_usage(ROOT).free>=LIMITS['host_reserve_bytes']and int(text.splitlines()[-1])>=LIMITS['ext4_reserve_bytes'],'immediate launch reserves')
        command=e.command(60,[h.linux(h.NATIVE),'--no-binary','-c','1000000',h.linux(CNF),proof]);h.save(folder/'launch.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),command=command,cnf_sha256=PINS[CNF],ext4_proof=proof));print(json.dumps(dict(state='COUNT_INTERVAL_NATIVE_LAUNCH',variables=N,clauses=M,wall_seconds=60)),flush=True)
        native=h.run_record(command,folder/'solver',70);result=dict(status='COUNT_INTERVAL_NATIVE_PENDING_INDEPENDENT_REVIEW',inputs_sha256=bindings,receipt=native,processes_before=before,research_calls=1,automatic_retry=False,target_resolution=False,independent_approval=False)
        if not native['outer_windows_guard_expired']:
            transfer_start=time.monotonic()
            try:result['proof_copy']=e.proof_copy(proof,folder/'proof.drat',folder/'transfer');h.require(result['proof_copy']['bytes']<=LIMITS['trace_file_bytes'],'trace cap')
            except BaseException as error:result['proof_copy_failure']=dict(error=repr(error),linux_original_path=proof,sha256=None,reason='Complete identity unavailable; preserve raw original and receipts.')
            result['proof_transfer_and_hash_wall_seconds']=time.monotonic()-transfer_start
            if native['actual_exit_code']==10:
                try:assignment=h.parse_sat_stdout((folder/'solver.stdout.log').read_text(),N);h.save(folder/'parsed_model.json',dict(assignment=assignment))
                except BaseException as error:result['parse_failure']=repr(error)
                if(folder/'parsed_model.json').exists():
                    try:
                        cmd=[sys.executable,'-B',str(args.object_checker),'sat','--encoding-gate',str(args.encoding_gate),'--encoding-gate-sha256',args.encoding_gate_sha256,'--assignment',str(folder/'parsed_model.json'),'--native-output',str(folder/'solver.stdout.log'),'--out',str(out/'independent_object')]
                        result['independent_object_receipt']=h.run_record(cmd,out/'independent_object_command',180)
                    except BaseException as error:result['independent_object_failure']=repr(error)
                result['stop_reason']='SAT_COUNT_INTERVAL_PROFILE_PENDING_INDEPENDENT_REVIEW'
            try:result['fresh_process_observation']=observe(out/'processes_after')
            except BaseException as error:result['process_observation_failure']=repr(error)
        code=native['actual_exit_code'];result['interpreted_result']='SAT_RAW_UNCHECKED'if code==10 else'UNSAT_TRACE_UNCHECKED'if code==20 else'UNKNOWN_NATIVE_OR_RESOURCE_OUTCOME';result['end_to_end_wall_seconds']=time.monotonic()-started
        result['outputs_sha256']={h.key(p):h.digest(p)for p in out.rglob('*')if p.is_file()};result['limitations']=['SAT requires separate complete count and interval object checking; no full factor or 99-vertex graph.','UNSAT requires complete proof replay and the scoped necessity/encoding gates.','Full unsummed Gram realization, cross-group caps and residual D are omitted.','UNKNOWN excludes nothing.'];h.save(out/'summary.json',result);print(json.dumps(dict(result=result['interpreted_result'],code=code)))
    except BaseException as error:h.save(out/'failure.json',dict(error=repr(error),source_sha256=h.digest(Path(__file__))));raise

def main():
    p=argparse.ArgumentParser();mode=p.add_mutually_exclusive_group(required=True);mode.add_argument('--preflight',action='store_true');mode.add_argument('--research',action='store_true')
    for name in('out','encoding-gate','object-gate','object-checker'):p.add_argument('--'+name,type=Path,required=True)
    for name in('encoding-gate-sha256','object-gate-sha256'):p.add_argument('--'+name,required=True)
    run(p.parse_args())
if __name__=='__main__':main()
