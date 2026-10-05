"""Prepared one-shot partial-cut count pilot; no producer decoder imported."""
from datetime import datetime, timezone
from pathlib import Path
import argparse, json, platform, shutil, subprocess, sys, time
import native_20260930_unrestricted_full99 as h
import native_20260930_proof_location as e

ROOT=h.ROOT
B=ROOT/'acceleration/results'
DATA=B/'20260930_count_master_scalar_cuts'
BASE=B/'20260930_hadamard_count_master_cnf'
OLD=B/'20260930_count_master_eight_orbit_cuts'
CNF=DATA/'instance.cnf';MODEL=DATA/'model.json';SCOPE=DATA/'scope.json'
SPEC=Path(__file__).with_name('native_20260930_count_master_partial_cuts_spec.md')
N=155939;M=705845
ENCODING_STATUS='INDEPENDENT_COUNT_MASTER_PARTIAL_CUT_CNF_PASS'
OBJECT_STATUS='INDEPENDENT_COUNT_MASTER_PARTIAL_CUT_OBJECT_CALIBRATION_PASS'
LIMITS=dict(native_wall_seconds=60,conflicts=1000000,address_space_bytes=4294967296,
 trace_file_bytes=10737418240,kill_grace_seconds=5,outer_guard_seconds=70,
 maximum_research_calls=1,automatic_retry=False,host_reserve_bytes=21*1024**3,ext4_reserve_bytes=11*1024**3)
PINS={
 CNF:'baca89a7014e10e1fea9fd1873ef5dde4a090ab02dfe1791b4734a196677880b',
 MODEL:'5e69de324c1a1d406764e95e3962dacf08924dab0c0b687a758614cc7fd49add',
 SCOPE:'acaaa3b8bb3df262f71ee8f14b063c47c29e5305dc82b7875ce0e1a2459abda0',
 DATA/'summary.json':'d2c4e4eb6c50e5b14aef98039b4a485e7971786ecf420e7dc339a2f167bf8502',
 BASE/'model.json':'a9a354e2fc28bff8a8f986d69f3cfd30fc06de0d76e394e125ffff884debdc44',
 OLD/'model.json':'a4376d5ee0e4cd8e990d311444f8ccda61d4b39af1c1c2371ade73e96dbe3d22',
 OLD/'scope.json':'5d604cc2c7725bee0865d9c746c97a005d2cd3aed08db078acb676d44cbf8518',
 OLD/'instance.cnf':'c3c0a9c0533d41bb814011d3736a4115d388e529f4c9cd2f89af609dc94793e2',
 Path(h.__file__):'da7ee9c03d454bd5ad0af0d82bead3520f3f270c70e71d4355161d036fd8ef22',
 Path(e.__file__):'ff7fd55658b7cb63e9586bd862f8f182269f2978a3b873ba9afccfa41a345854',
 h.NATIVE:h.NATIVE_SHA,h.CHECKER:h.CHECKER_SHA,
 ROOT/'uv.lock':'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',
 ROOT/'pyproject.toml':'273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339'}

def source_closure():
    paths={Path(__file__).resolve(),SPEC.resolve()}
    for module in tuple(sys.modules.values()):
        name=getattr(module,'__file__',None)
        if name:
            path=Path(name).resolve()
            if path.is_relative_to(ROOT/'acceleration') and path.suffix=='.py':
                paths.add(path)
                spec=path.with_name(path.stem+'_spec.md')
                if spec.exists(): paths.add(spec)
    return paths

def preflight(args):
    bindings={}
    for path,digest in PINS.items():
        h.require(h.digest(path)==digest,'frozen input/source/tool '+h.key(path));bindings[h.key(path)]=digest
    summary=h.read(DATA/'summary.json')
    h.require(summary['status']=='CANDIDATE_COUNT_MASTER_SIX_ORBIT_AND_SIX_SCALAR_CUT_CNF_BUILT','complete new build')
    for path,digest in {**summary['inputs_sha256'],**summary['outputs_sha256']}.items():
        h.require(h.digest(ROOT/path)==digest,'producer artifact '+path);bindings[path]=digest
    model=h.read(MODEL);scope=h.read(SCOPE)
    h.require(model['schema']=='COUNT_MASTER_SCALAR_CUT_REFERENCE_MODEL_V1','new model schema')
    h.require((model['variables'],model['clauses'])==(N,M) and model['cnf_path']==h.key(CNF) and model['cnf_sha256']==PINS[CNF],'literal formula')
    h.require(model['scope_path']==h.key(SCOPE) and model['scope_sha256']==PINS[SCOPE],'scope pin')
    h.require(model['base_variant']=='at_least_seven' and model['base_count_model_path']==h.key(BASE/'model.json') and model['base_count_model_sha256']==PINS[BASE/'model.json'],'inherited count model')
    h.require(model['old_model_path']==h.key(OLD/'model.json') and model['old_model_sha256']==PINS[OLD/'model.json'],'inherited orbit model')
    h.require(model['old_cnf_path']==h.key(OLD/'instance.cnf') and model['old_cnf_sha256']==PINS[OLD/'instance.cnf'] and model['old_clause_count']==705839,'inherited exact prefix')
    h.require(len(model['old_full_profile_clauses'])==6 and len(model['scalar_clause_records'])==6,'six plus six cuts')
    h.require([r['index'] for r in model['scalar_clause_records']]==list(range(705840,705846)) and all(len(r['clause'])==25 for r in model['scalar_clause_records']),'new clause indices/lengths')
    h.require(scope['schema']=='COUNT_MASTER_SIX_ORBIT_PLUS_SIX_SCALAR_CUT_SCOPE_V1' and scope['minimum_exception_count']==7 and scope['base_variant']=='at_least_seven','scope bound')
    h.require(scope['old_orbit_scope_path']==h.key(OLD/'scope.json') and scope['old_orbit_scope_sha256']==PINS[OLD/'scope.json'],'inherited scope')
    h.require(scope['old_full_profile_nogoods']==6 and scope['new_scalar_necessary_clauses']==6 and scope['new_clause_lengths']==[25]*6 and scope['local_group_catalogue_membership_retained'],'count and cut scope')
    h.require(not any(scope[k] for k in ['new_clauses_use_local_caps','new_clauses_use_symmetry','full_Gram_encoded','all_column_caps_encoded','residual_D_encoded','full_factor','target_graph']),'omitted constraints')
    h.require(e.AS_LIMIT==LIMITS['address_space_bytes'] and e.FILE_LIMIT==LIMITS['trace_file_bytes'],'helper resource constants')
    with CNF.open('rb') as stream:h.require(stream.readline()==f'p cnf {N} {M}\n'.encode(),'exact header')
    reports=[]
    direct=[CNF,MODEL,SCOPE,DATA/'summary.json',BASE/'model.json',OLD/'model.json',OLD/'scope.json',OLD/'instance.cnf']
    for path,digest,status in [(args.encoding_gate,args.encoding_gate_sha256,ENCODING_STATUS),(args.object_gate,args.object_gate_sha256,OBJECT_STATUS)]:
        report=h.checked_gate(path,digest,status);reports.append(report)
        for name,value in report['inputs_sha256'].items():
            h.require(h.digest(ROOT/name)==value,'unchanged independent gate input '+name);bindings[name]=value
        for raw in direct:h.require(report['inputs_sha256'][h.key(raw)]==h.digest(raw),'direct input binding '+h.key(raw))
        bindings[h.key(path)]=digest
    h.require(reports[1]['inputs_sha256'][h.key(args.encoding_gate)]==args.encoding_gate_sha256,'same encoding gate')
    for path in source_closure()|{args.object_checker.resolve(),h.NATIVE,h.CHECKER}:
        digest=h.digest(path);h.require(reports[1]['inputs_sha256'][h.key(path)]==digest,'runtime/checker closure '+h.key(path));bindings[h.key(path)]=digest
    for name,digest,status in [('20260930_native_cli_calibration','f5ff562aff2ec550a97685c7012b302e760314a6f3829d80d022e2a669e680eb','INDEPENDENT_NATIVE_CADICAL195_CLI_CALIBRATION_PASS'),('20260930_native_proof_location','d1036cfcbe9b24e0f7ea6e0a3799968a5d9232e8167fb31b224211e5c845c619','NATIVE_EXT4_PROOF_PATH_CALIBRATION_PASS')]:
        path=B/name/'summary.json';h.checked_gate(path,digest,status);bindings[h.key(path)]=digest
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
        h.save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,limits=LIMITS,mode='PREFLIGHT_ONLY'if args.preflight else'RESEARCH',host_free_bytes=host,ext4_free_bytes=ext4,mount_receipt=mount,disk_receipt=disk,scope='At-least-seven count relaxation plus six whole-profile exclusions and six scalar necessary cuts; not a full factor or residual completion.',random_seed=None,random_seed_null_reason='Native default retained.',cpu_limit=None,cpu_limit_null_reason='Wall guard; no additional CPU rlimit.',shared_components=['Authenticated parser/native/ext4 engineering helpers.','Only a separately gated independent checker receives the raw SAT assignment; no producer decoder import.']))
        if args.preflight:h.save(out/'summary.json',dict(status='COUNT_MASTER_PARTIAL_CUT_NATIVE_PREFLIGHT_PASS',research_calls=0,inputs_sha256=bindings));return
        before=observe(out/'processes_before');made,directory=e.local_capture(['/usr/bin/mktemp','-d','/tmp/conway99-count-partial-cuts-XXXXXX'],out/'mktemp');h.require(directory.startswith('/tmp/conway99-count-partial-cuts-')and '\n'not in directory,'fresh ext4 directory');h.save(out/'workspace.json',dict(path=directory,creation_observed=True,retention_intent='This wrapper does not delete the ext4 workspace.',future_availability='UNKNOWN',limitation='Creation and immediate transfer observations do not guarantee permanent ext4 retention.',receipt=made));folder=out/'main';folder.mkdir();proof=directory+'/proof.drat'
        disk,text=e.local_capture(['/usr/bin/df','--output=avail','-B1',directory],out/'disk_before_launch');h.require(shutil.disk_usage(ROOT).free>=LIMITS['host_reserve_bytes']and int(text.splitlines()[-1])>=LIMITS['ext4_reserve_bytes'],'immediate launch reserves')
        command=e.command(60,[h.linux(h.NATIVE),'--no-binary','-c','1000000',h.linux(CNF),proof]);h.save(folder/'launch.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),command=command,cnf_sha256=PINS[CNF],ext4_proof=proof));print(json.dumps(dict(state='COUNT_MASTER_PARTIAL_CUT_NATIVE_LAUNCH',variables=N,clauses=M,wall_seconds=60)),flush=True)
        native=h.run_record(command,folder/'solver',70);result=dict(status='COUNT_MASTER_PARTIAL_CUT_NATIVE_PENDING_INDEPENDENT_REVIEW',inputs_sha256=bindings,receipt=native,processes_before=before,research_calls=1,automatic_retry=False,target_resolution=False,independent_approval=False)
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
                        cmd=[sys.executable,'-B',str(args.object_checker),'sat','--variant','at_least_seven','--encoding-gate',str(args.encoding_gate),'--encoding-gate-sha256',args.encoding_gate_sha256,'--assignment',str(folder/'parsed_model.json'),'--native-output',str(folder/'solver.stdout.log'),'--out',str(out/'independent_object')]
                        result['independent_object_receipt']=h.run_record(cmd,out/'independent_object_command',180)
                    except BaseException as error:result['independent_object_failure']=repr(error)
                result['stop_reason']='SAT_COUNT_MASTER_PARTIAL_CUT_PROFILE_PENDING_INDEPENDENT_REVIEW'
            try:result['fresh_process_observation']=observe(out/'processes_after')
            except BaseException as error:result['process_observation_failure']=repr(error)
        code=native['actual_exit_code'];result['interpreted_result']='SAT_RAW_UNCHECKED'if code==10 else'UNSAT_TRACE_UNCHECKED'if code==20 else'UNKNOWN_NATIVE_OR_RESOURCE_OUTCOME';result['end_to_end_wall_seconds']=time.monotonic()-started
        result['outputs_sha256']={h.key(p):h.digest(p)for p in out.rglob('*')if p.is_file()};result['limitations']=['SAT requires separate complete count and scalar-cut object checking; no full factor or 99-vertex graph.','UNSAT requires complete proof replay and the scoped necessity/encoding gates.','Full unsummed Gram realization, cross-group caps and residual D are omitted.','UNKNOWN excludes nothing.'];h.save(out/'summary.json',result);print(json.dumps(dict(result=result['interpreted_result'],code=code)))
    except BaseException as error:h.save(out/'failure.json',dict(error=repr(error),source_sha256=h.digest(Path(__file__))));raise

def main():
    p=argparse.ArgumentParser();mode=p.add_mutually_exclusive_group(required=True);mode.add_argument('--preflight',action='store_true');mode.add_argument('--research',action='store_true')
    for name in('out','encoding-gate','object-gate','object-checker'):p.add_argument('--'+name,type=Path,required=True)
    for name in('encoding-gate-sha256','object-gate-sha256'):p.add_argument('--'+name,required=True)
    run(p.parse_args())
if __name__=='__main__':main()
