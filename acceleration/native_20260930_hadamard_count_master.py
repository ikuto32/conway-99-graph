"""One gated native call on the exact joint-count plus at-least-seven formula."""
from datetime import datetime,timezone
from pathlib import Path
import argparse,json,platform,shutil,subprocess,sys,time
import native_20260930_unrestricted_full99 as h
import native_20260930_proof_location as e
import theory_20260930_hadamard_count_master_cnf as producer
ROOT=h.ROOT;B=ROOT/'acceleration/results';DATA=B/'20260930_hadamard_count_master_cnf';CNF=DATA/'at_least_seven.cnf';MODEL=DATA/'model.json';SCOPE=DATA/'scope.json';SPEC=Path(__file__).with_name('native_20260930_hadamard_count_master_spec.md')
N=155939;M=705833
ENCODING_STATUS='INDEPENDENT_HADAMARD_COUNT_MASTER_ENCODING_PASS';OBJECT_STATUS='INDEPENDENT_HADAMARD_COUNT_MASTER_OBJECT_CALIBRATION_PASS'
LIMITS=dict(native_wall_seconds=60,conflicts=1000000,address_space_bytes=e.AS_LIMIT,trace_file_bytes=e.FILE_LIMIT,kill_grace_seconds=5,outer_guard_seconds=70,maximum_research_calls=1,automatic_retry=False)
PINS={CNF:'f303edec9a91dc9bcecb95804ee151d0e38e8100b17c9c45a7b4d58b8edbf55e',MODEL:'a9a354e2fc28bff8a8f986d69f3cfd30fc06de0d76e394e125ffff884debdc44',SCOPE:'719fb6e1d7b98656f23b31a83343fb9dfa952ea9a0c14fef3d564faf896f0959',DATA/'summary.json':'2137fe0c32043a82166a484085d366309e4037d24aa558dabca20a44e73bff04',Path(producer.__file__):'470cbec724f891264593dc5b438648dc2995b3f860f89decf4b6ac8bc1c4f28b',Path(producer.__file__).with_name('theory_20260930_hadamard_count_master_cnf_spec.md'):'67b5e379c1b5e6d1dcb6e6aff0c022821a56169a55e1656abf3d353aac5b5d19',Path(h.__file__):'da7ee9c03d454bd5ad0af0d82bead3520f3f270c70e71d4355161d036fd8ef22',Path(e.__file__):'ff7fd55658b7cb63e9586bd862f8f182269f2978a3b873ba9afccfa41a345854',h.NATIVE:h.NATIVE_SHA,h.CHECKER:h.CHECKER_SHA,ROOT/'uv.lock':'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',ROOT/'pyproject.toml':'273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339'}
PINS.update(producer.PINS)
def source_closure():
    paths={Path(__file__).resolve(),SPEC.resolve(),Path(producer.__file__).with_name('theory_20260930_hadamard_count_master_cnf_spec.md').resolve()}
    for module in tuple(sys.modules.values()):
        name=getattr(module,'__file__',None)
        if name:
            path=Path(name).resolve()
            if path.is_relative_to(ROOT/'acceleration') and path.suffix=='.py':paths.add(path)
    return paths
def preflight(args):
    bindings={}
    for p,digest in PINS.items():h.require(h.digest(p)==digest,'frozen input/source/tool '+h.key(p));bindings[h.key(p)]=digest
    summary=h.read(DATA/'summary.json')
    for p,digest in {**summary['inputs_sha256'],**summary['outputs_sha256']}.items():h.require(h.digest(ROOT/p)==digest,'producer artifact '+p);bindings[p]=digest
    scope=h.read(SCOPE);model=h.read(MODEL);variant=model['variants']['at_least_seven']
    h.require((variant['variables'],variant['clauses'])==(N,M) and variant['cnf_sha256']==PINS[CNF] and variant['cnf_path']==h.key(CNF),'literal augmented formula')
    h.require(scope['within_group_caps_inherited'] and not scope['cross_group_caps_encoded'] and not scope['full_Gram_encoded'] and not scope['residual_D_encoded'] and not scope['target_automorphism_assumed'],'exact count scope')
    h.require(model['extension']['at_most']==13 and len(model['extension']['input_variables'])==20 and not model['full_factor'] and not model['target_graph'],'additional bound and object kind')
    with CNF.open('rb') as f:h.require(f.readline()==f'p cnf {N} {M}\n'.encode(),'exact header')
    reports=[];direct=[CNF,MODEL,SCOPE,DATA/'extension.json',DATA/'summary.json',Path(producer.__file__)]
    for p,digest,status in [(args.encoding_gate,args.encoding_gate_sha256,ENCODING_STATUS),(args.object_gate,args.object_gate_sha256,OBJECT_STATUS)]:
        report=h.checked_gate(p,digest,status);reports.append(report)
        for name,value in report['inputs_sha256'].items():h.require(h.digest(ROOT/name)==value,'unchanged gate input '+name);bindings[name]=value
        for raw in direct:h.require(report['inputs_sha256'][h.key(raw)]==h.digest(raw),'direct input gate '+h.key(raw))
        bindings[h.key(p)]=digest
    h.require(reports[1]['inputs_sha256'][h.key(args.encoding_gate)]==args.encoding_gate_sha256,'same encoding gate')
    for p in source_closure()|{args.object_checker.resolve()}:
        digest=h.digest(p);h.require(reports[1]['inputs_sha256'][h.key(p)]==digest,'object native/checker closure '+h.key(p));bindings[h.key(p)]=digest
    for name,digest,status in [('20260930_native_cli_calibration','f5ff562aff2ec550a97685c7012b302e760314a6f3829d80d022e2a669e680eb','INDEPENDENT_NATIVE_CADICAL195_CLI_CALIBRATION_PASS'),('20260930_native_proof_location','d1036cfcbe9b24e0f7ea6e0a3799968a5d9232e8167fb31b224211e5c845c619','NATIVE_EXT4_PROOF_PATH_CALIBRATION_PASS')]:
        p=B/name/'summary.json';h.checked_gate(p,digest,status);bindings[h.key(p)]=digest
    return bindings
def observe(prefix):
    receipt=h.run_record([*h.WSL,'/usr/bin/ps','-C','cadical','-o','pid,ppid,comm,pcpu,rss,args'],prefix,10);h.require(not receipt['outer_windows_guard_expired'] and receipt['actual_exit_code'] in (0,1),'targeted native observation')
    if receipt['actual_exit_code']==1:h.require(len(Path(str(prefix)+'.stdout.log').read_text().strip().splitlines())<=1,'no exact named process')
    return receipt
def run(args):
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);started=time.monotonic()
    try:
        bindings=preflight(args);mount,text=e.local_capture(['/usr/bin/findmnt','--target','/tmp','--output','TARGET,SOURCE,FSTYPE,OPTIONS','--noheadings'],out/'filesystem');h.require('ext4' in text.split(),'ext4 proof mount');disk,text=e.local_capture(['/usr/bin/df','--output=avail','-B1','/tmp'],out/'disk_free');host=shutil.disk_usage(ROOT).free;ext4=int(text.splitlines()[-1]);h.require(host>=21*1024**3 and ext4>=11*1024**3,'host/ext4 reserves')
        h.save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,limits=LIMITS,mode='PREFLIGHT_ONLY' if args.preflight else 'RESEARCH',host_free_bytes=host,ext4_free_bytes=ext4,mount_receipt=mount,disk_receipt=disk,scope='Exact count-table relaxation with separately justified at-least-seven extension; no full Gram or residual completion.',random_seed=None,random_seed_null_reason='Native default retained.',cpu_limit=None,cpu_limit_null_reason='Wall guard; no additional CPU rlimit.',shared_components=['Authenticated parser/native/ext4 helpers.','Producer count decoder; this path is not independent checking.']))
        if args.preflight:h.save(out/'summary.json',dict(status='COUNT_MASTER_NATIVE_PREFLIGHT_PASS',research_calls=0,inputs_sha256=bindings));return
        before=observe(out/'processes_before');made,directory=e.local_capture(['/usr/bin/mktemp','-d','/tmp/conway99-count-master-XXXXXX'],out/'mktemp');h.require(directory.startswith('/tmp/conway99-count-master-') and '\n' not in directory,'fresh ext4 directory');h.save(out/'workspace.json',dict(path=directory,preserved=True,receipt=made));folder=out/'main';folder.mkdir();proof=directory+'/proof.drat'
        disk,text=e.local_capture(['/usr/bin/df','--output=avail','-B1',directory],out/'disk_before_launch');h.require(shutil.disk_usage(ROOT).free>=21*1024**3 and int(text.splitlines()[-1])>=11*1024**3,'immediate launch reserves')
        command=e.command(60,[h.linux(h.NATIVE),'--no-binary','-c','1000000',h.linux(CNF),proof]);h.save(folder/'launch.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),command=command,cnf_sha256=PINS[CNF],ext4_proof=proof));print(json.dumps(dict(state='COUNT_MASTER_NATIVE_LAUNCH',variables=N,clauses=M,wall_seconds=60)),flush=True)
        native=h.run_record(command,folder/'solver',70);result=dict(status='COUNT_MASTER_NATIVE_PENDING_INDEPENDENT_REVIEW',inputs_sha256=bindings,receipt=native,processes_before=before,research_calls=1,automatic_retry=False,target_resolution=False,independent_approval=False)
        if not native['outer_windows_guard_expired']:
            transfer_start=time.monotonic()
            try:result['proof_copy']=e.proof_copy(proof,folder/'proof.drat',folder/'transfer');h.require(result['proof_copy']['bytes']<=e.FILE_LIMIT,'trace cap')
            except BaseException as error:result['proof_copy_failure']=dict(error=repr(error),linux_original_path=proof,sha256=None,reason='Complete identity unavailable; preserve raw original and receipts.')
            result['proof_transfer_and_hash_wall_seconds']=time.monotonic()-transfer_start
            if native['actual_exit_code']==10:
                try:assignment=h.parse_sat_stdout((folder/'solver.stdout.log').read_text(),N);h.save(folder/'parsed_model.json',dict(assignment=assignment))
                except BaseException as error:result['parse_failure']=repr(error)
                if (folder/'parsed_model.json').exists():
                    try:decoded=producer.decode(assignment,MODEL,'at_least_seven');h.save(folder/'decoded_count_profile.json',decoded)
                    except BaseException as error:result['candidate_decode_failure']=repr(error)
                    try:
                        cmd=[sys.executable,'-B',str(args.object_checker),'sat','--variant','at_least_seven','--encoding-gate',str(args.encoding_gate),'--encoding-gate-sha256',args.encoding_gate_sha256,'--assignment',str(folder/'parsed_model.json'),'--native-output',str(folder/'solver.stdout.log'),'--out',str(out/'independent_object')]
                        if (folder/'decoded_count_profile.json').exists():cmd+=['--decoded',str(folder/'decoded_count_profile.json')]
                        result['independent_object_receipt']=h.run_record(cmd,out/'independent_object_command',180)
                    except BaseException as error:result['independent_object_failure']=repr(error)
                result['stop_reason']='SAT_COUNT_PROFILE_PENDING_INDEPENDENT_REVIEW'
            try:result['fresh_process_observation']=observe(out/'processes_after')
            except BaseException as error:result['process_observation_failure']=repr(error)
        code=native['actual_exit_code'];result['interpreted_result']='COUNT_MASTER_SAT_RAW_UNCHECKED' if code==10 else 'COUNT_MASTER_UNSAT_TRACE_UNCHECKED' if code==20 else 'UNKNOWN_NATIVE_OR_RESOURCE_OUTCOME';result['end_to_end_wall_seconds']=time.monotonic()-started;result['outputs_sha256']={h.key(p):h.digest(p) for p in out.rglob('*') if p.is_file()};result['limitations']=['SAT needs independent complete count-object checking; no full factor or99graph.','UNSAT needs complete proof replay and scoped necessary-encoding review.','Full unsummed Gram, cross-group caps, interval strengthening and residualD omitted.','UNKNOWN excludes nothing.'];h.save(out/'summary.json',result);print(json.dumps(dict(result=result['interpreted_result'],code=code)))
    except BaseException as error:h.save(out/'failure.json',dict(error=repr(error),source_sha256=h.digest(Path(__file__))));raise
def main():
    p=argparse.ArgumentParser();mode=p.add_mutually_exclusive_group(required=True);mode.add_argument('--preflight',action='store_true');mode.add_argument('--research',action='store_true')
    for name in ('out','encoding-gate','object-gate','object-checker'):p.add_argument('--'+name,type=Path,required=True)
    for name in ('encoding-gate-sha256','object-gate-sha256'):p.add_argument('--'+name,required=True)
    run(p.parse_args())
if __name__=='__main__':main()
