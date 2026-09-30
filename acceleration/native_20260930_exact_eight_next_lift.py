"""Prepared one-shot native pilot for the next selected literal exact-eight count profile."""
from datetime import datetime,timezone
from pathlib import Path
import argparse,json,platform,shutil,subprocess,sys,time
import native_20260930_unrestricted_full99 as h
import native_20260930_proof_location as e
import theory_20260930_exact_eight_next_lift as producer
ROOT=h.ROOT;B=ROOT/'acceleration/results';DATA=B/'20260930_exact_eight_next_lift'
CNF=DATA/'instance.cnf';MODEL=DATA/'model.json';SCOPE=DATA/'scope.json';PROFILE=DATA/'selected_profile.json'
SPEC=Path(__file__).with_name('native_20260930_exact_eight_next_lift_spec.md')
ENCODING_STATUS='INDEPENDENT_EXACT_EIGHT_NEXT_LITERAL_GRAM_ENCODING_PASS';OBJECT_STATUS='INDEPENDENT_EXACT_EIGHT_NEXT_LITERAL_GRAM_OBJECT_CALIBRATION_PASS'
LIMITS=dict(native_wall_seconds=60,conflicts=1000000,address_space_bytes=e.AS_LIMIT,trace_file_bytes=e.FILE_LIMIT,kill_grace_seconds=5,outer_guard_seconds=70,maximum_research_calls=1,automatic_retry=False)
PINS={CNF:'6fecea814c533a081ee0292087b1bf4cccb9cb132ea232b907acd227ba610962',MODEL:'91084af7baa7041e6f66ce9cdcfb00b72eebce07389a5d0e160209457438109d',SCOPE:'d8a05714c5297495c2a2d28835bd0c41de90a956162f998158dea39f78cf04b1',PROFILE:'7997ff6bb2ae409cade1094e0a3d16ef82f17051a2fbfa2a96412342e4bdc446',DATA/'summary.json':'6cad750feb66e73dbeec98d818ca1a15b049105167c4cacce70e3a1071bd17dc',Path(producer.__file__):'473b4774650f43fbd51dc9387f006bf1b9626e70acfd80e4a3ab45c25ac04dff',producer.SPEC:'ef0f6cbc9688db47eea55ddcb97de0fca063b6eb3361827c28426926ccfe53fd',Path(h.__file__):'da7ee9c03d454bd5ad0af0d82bead3520f3f270c70e71d4355161d036fd8ef22',Path(e.__file__):'ff7fd55658b7cb63e9586bd862f8f182269f2978a3b873ba9afccfa41a345854',h.NATIVE:h.NATIVE_SHA,h.CHECKER:h.CHECKER_SHA,ROOT/'uv.lock':'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',ROOT/'pyproject.toml':'273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339'}
PINS.update(producer.PINS)
PINS.update({ROOT/'acceleration/native_20260930_eight_count_profile_lift_third.py':'e73f44028b13dbeac8710f98826439b22a30504956f3a6a4d127d35469928a59',ROOT/'acceleration/native_20260930_eight_count_profile_lift_third_spec.md':'b566790256cacc66758dd51c5eee1f1846c9499d0d5c1a1eb9a92df467fcf94d'})
SELECTION=DATA/'selection.json';BLOCK_GATE=B/'20260930_independent_review/exact_eight_block_screen/summary.json';BLOCK_SUMMARY=B/'20260930_exact_eight_block_screen/summary.json'
ENCODING_GATE=B/'20260930_independent_review/exact_eight_next_lift/summary.json';ENCODING_SHA='395a7396168bd0ec5faf1413f12b14d6e630d3c961723d1b68f0d6c07c96402e'
PINS.update({SELECTION:'dbc6460fabee748ba25a6a1f801d2fe45300f9a440ebeba2b410b00b1c920590',BLOCK_GATE:'6c21ef6951f72fbeabab8be0a649f178ca8b17eb91edcc35c3291d6790f6256a',BLOCK_SUMMARY:'9fbfde4c8d1f1b4fc0aee7b89783a76dcd71c48adf75dbe6c32f116438634edb',ENCODING_GATE:ENCODING_SHA})
def source_closure():
    paths={producer.shared.BASE.resolve(),Path(__file__).resolve(),SPEC.resolve(),producer.SPEC.resolve()}
    for module in tuple(sys.modules.values()):
        name=getattr(module,'__file__',None)
        if name:
            path=Path(name).resolve()
            if path.is_relative_to(ROOT/'acceleration') and path.suffix=='.py':paths.add(path)
    return paths
def preflight(args):
    bindings={}
    for path,digest in PINS.items():h.require(h.digest(path)==digest,'frozen source/input/tool '+h.key(path));bindings[h.key(path)]=digest
    h.require(args.encoding_gate.resolve()==ENCODING_GATE.resolve() and args.encoding_gate_sha256==ENCODING_SHA,'exact approved encoding gate')
    scope=h.read(SCOPE);profile=h.read(PROFILE);model=h.read(MODEL)
    h.require(profile['selected_subset_index']==0 and scope['selected_full_count_sha256']==profile['full_count_profile_sha256']=='a2a3d60e21811916cde9269f08221000990e8235629bcc67d880ae472b6a18f9','selected complete count profile')
    h.require(scope['selected_profile_id']=='exact_eight_first_block_survivor_outside_three_historical_orbits' and scope['selected_profile_sha256']==profile['profile_sha256']=='40c141a31c059e2d413e99e8f20ccb8d149b25599139a64258c5259d9b649cb9','literal initial profile')
    h.require(scope['exceptional_groups']==[0,1,2,5,9,10,12,14] and scope['within_group_column_caps_encoded'] and not scope['cross_group_column_caps_encoded'] and not scope['residual_D_encoded'] and not scope['arc_pruning_used'] and not scope['orbit_coverage_used'],'exact omissions/initial scope')
    direct=[CNF,MODEL,SCOPE,PROFILE,DATA/'summary.json',producer.RAW,Path(producer.__file__),producer.SPEC]
    initial=DATA/'initial_domains.json';h.require(h.digest(initial)==scope['initial_domains_sha256']=='eecca94d25028ffe61d728165fcad57180fb1e7537a6ff0e841cb0da023681cc','complete twenty initial domains');direct+=[initial,SELECTION,BLOCK_GATE,BLOCK_SUMMARY];bindings[h.key(initial)]=h.digest(initial)
    h.require([len(d['choices']) for d in model['domains'] if d['group'] in scope['exceptional_groups']]==[48,48,48,48,48,48,48,48] and all(len(d['choices'])==150 for d in model['domains'] if d['group'] not in scope['exceptional_groups']),'actual domain populations')
    with CNF.open('rb') as f:h.require(f.readline()==b'p cnf 9748 167416\n','exact header')
    reports=[]
    for path,digest,status in [(args.encoding_gate,args.encoding_gate_sha256,ENCODING_STATUS),(args.object_gate,args.object_gate_sha256,OBJECT_STATUS)]:
        report=h.checked_gate(path,digest,status);reports.append(report)
        for name,value in report['inputs_sha256'].items():h.require(h.digest(ROOT/name)==value,'unchanged gate input '+name);bindings[name]=value
        for raw in direct:h.require(report['inputs_sha256'][h.key(raw)]==h.digest(raw),'direct literal input gate '+h.key(raw))
        bindings[h.key(path)]=digest
    h.require(reports[1]['inputs_sha256'][h.key(args.encoding_gate)]==args.encoding_gate_sha256,'same encoding gate')
    for path in source_closure()|{args.object_checker.resolve()}:
        digest=h.digest(path);h.require(reports[1]['inputs_sha256'][h.key(path)]==digest,'object gate native/checker closure '+h.key(path));bindings[h.key(path)]=digest
    for name,digest,status in [('20260930_native_cli_calibration','f5ff562aff2ec550a97685c7012b302e760314a6f3829d80d022e2a669e680eb','INDEPENDENT_NATIVE_CADICAL195_CLI_CALIBRATION_PASS'),('20260930_native_proof_location','d1036cfcbe9b24e0f7ea6e0a3799968a5d9232e8167fb31b224211e5c845c619','NATIVE_EXT4_PROOF_PATH_CALIBRATION_PASS')]:
        path=B/name/'summary.json';h.checked_gate(path,digest,status);bindings[h.key(path)]=digest
    return bindings
def observe(prefix):
    receipt=h.run_record([*h.WSL,'/usr/bin/ps','-C','cadical','-o','pid,ppid,comm,pcpu,rss,args'],prefix,10);h.require(not receipt['outer_windows_guard_expired'] and receipt['actual_exit_code'] in (0,1),'targeted native observation')
    if receipt['actual_exit_code']==1:h.require(len(Path(str(prefix)+'.stdout.log').read_text().strip().splitlines())<=1,'no exact named process')
    return receipt
def literal_factor(decoded):
    scope=h.read(SCOPE);f=decoded['factor'];c=scope['core_adjacency36'];h.require(len(f)==36 and all(len(row)==60 and all(type(x)is int and x in(0,1) for x in row) for row in f),'complete literal binary factor')
    gram=[[sum(f[i][d]*f[j][d] for d in range(60)) for j in range(36)] for i in range(36)];h.require(gram==scope['prescribed_Gram36'],'all1296 integer Gram entries');h.require(all(sum(row)==10 for row in f),'row margins');h.require(all(sum(f[12*z+a][d] for a in range(12))==2 for z in range(3) for d in range(60)),'fibre margins')
    h.require([[sum(f[12*z+a][d] for z in range(3)) for d in range(60)] for a in range(12)]==scope['L12x60'],'720 support entries')
    pairs=[dict(columns=[d,z],overlap=sum(f[i][d]*f[i][z] for i in range(36))) for d in range(60) for z in range(d+1,60)];bad=[p for p in pairs if p['overlap']>2];mixed=[dict(row=i,column=d,value=f[i][d]+sum(c[i][j]*f[j][d] for j in range(36))) for i in range(36) for d in range(60)];mixedbad=[m for m in mixed if m['value']>2]
    h.require(pairs==decoded['checks']['column_pair_records'] and bad==decoded['checks']['column_cap_violations'] and mixedbad==decoded['checks']['mixed_cap_violations'],'candidate decoder diagnostics agree')
    return dict(status='PRODUCER_LITERAL_RAW_FACTOR_CHECK_ONLY',Gram_entries=1296,column_pairs=1770,mixed_entries=2160,column_pair_records=pairs,column_cap_violations=bad,mixed_cap_violations=mixedbad,independent_approval=False,target_graph=False,residual_D=None)
def run(args):
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);started=time.monotonic()
    try:
        bindings=preflight(args);mount,text=e.local_capture(['/usr/bin/findmnt','--target','/tmp','--output','TARGET,SOURCE,FSTYPE,OPTIONS','--noheadings'],out/'filesystem');h.require('ext4' in text.split(),'ext4 proof mount');disk,text=e.local_capture(['/usr/bin/df','--output=avail','-B1','/tmp'],out/'disk_free');host=shutil.disk_usage(ROOT).free;ext4=int(text.splitlines()[-1]);h.require(host>=21*1024**3 and ext4>=11*1024**3,'host/ext4 reserves')
        h.save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,limits=LIMITS,mode='PREFLIGHT_ONLY' if args.preflight else 'RESEARCH',host_free_bytes=host,ext4_free_bytes=ext4,mount_receipt=mount,disk_receipt=disk,scope=h.read(SCOPE)['scope'],random_seed=None,random_seed_null_reason='Native default retained.',cpu_limit=None,cpu_limit_null_reason='Wall guard; no additional CPU rlimit.',shared_components=['Authenticated parser/native/ext4 helpers.','Candidate selected exact-eight-profile decoder and its frozen generic helpers; not independent checking.']))
        if args.preflight:h.save(out/'summary.json',dict(status='EXACT_EIGHT_NEXT_LITERAL_GRAM_NATIVE_PREFLIGHT_PASS',research_calls=0,inputs_sha256=bindings));return
        before=observe(out/'processes_before');made,directory=e.local_capture(['/usr/bin/mktemp','-d','/tmp/conway99-exact-eight-next-lift-XXXXXX'],out/'mktemp');h.require(directory.startswith('/tmp/conway99-exact-eight-next-lift-') and '\n' not in directory,'fresh ext4 directory');h.save(out/'workspace.json',dict(path=directory,creation_observed=True,created_at=datetime.now(timezone.utc).isoformat(),deletion_requested_by_driver=False,future_availability='UNKNOWN',receipt=made))
        disk,text=e.local_capture(['/usr/bin/df','--output=avail','-B1',directory],out/'disk_before_launch');h.require(shutil.disk_usage(ROOT).free>=21*1024**3 and int(text.splitlines()[-1])>=11*1024**3,'immediate launch reserves');folder=out/'main';folder.mkdir();proof=directory+'/proof.drat';command=e.command(60,[h.linux(h.NATIVE),'--no-binary','-c','1000000',h.linux(CNF),proof]);h.save(folder/'launch.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),command=command,cnf_sha256=PINS[CNF],ext4_proof=proof))
        print(json.dumps(dict(state='EXACT_EIGHT_NEXT_LITERAL_GRAM_NATIVE_LAUNCH',variables=9748,clauses=167416,wall_seconds=60)),flush=True);native=h.run_record(command,folder/'solver',70);result=dict(status='EXACT_EIGHT_NEXT_LITERAL_GRAM_NATIVE_PENDING_INDEPENDENT_REVIEW',inputs_sha256=bindings,receipt=native,processes_before=before,research_calls=1,automatic_retry=False,target_resolution=False,independent_approval=False)
        if not native['outer_windows_guard_expired']:
            transfer_start=time.monotonic()
            try:result['proof_copy']=e.proof_copy(proof,folder/'proof.drat',folder/'transfer');h.require(result['proof_copy']['bytes']<=e.FILE_LIMIT,'trace cap')
            except BaseException as error:result['proof_copy_failure']=dict(error=repr(error),linux_original_path=proof,sha256=None,reason='Full identity unavailable; receipts are retained. Original ext4 availability is UNKNOWN; this driver requests no deletion.')
            result['proof_transfer_and_hash_wall_seconds']=time.monotonic()-transfer_start
            if native['actual_exit_code']==10:
                try:assignment=h.parse_sat_stdout((folder/'solver.stdout.log').read_text(),9748);h.save(folder/'parsed_model.json',dict(assignment=assignment))
                except BaseException as error:result['parse_failure']=repr(error)
                if (folder/'parsed_model.json').exists():
                    try:decoded=producer.decode(assignment,MODEL,SCOPE,CNF);h.save(folder/'decoded_Gram_factor.json',decoded);h.save(folder/'literal_factor_check.json',literal_factor(decoded))
                    except BaseException as error:result['candidate_decode_failure']=repr(error)
                    try:
                        cmd=[sys.executable,'-B',str(args.object_checker),'sat','--encoding-gate',str(args.encoding_gate),'--encoding-gate-sha256',args.encoding_gate_sha256,'--assignment',str(folder/'parsed_model.json'),'--native-output',str(folder/'solver.stdout.log'),'--out',str(out/'independent_object')]
                        if (folder/'decoded_Gram_factor.json').exists():cmd+=['--decoded',str(folder/'decoded_Gram_factor.json')]
                        result['independent_object_receipt']=h.run_record(cmd,out/'independent_object_command',120)
                    except BaseException as error:result['independent_object_failure']=repr(error)
                result['stop_reason']='SAT_PENDING_INDEPENDENT_REVIEW'
            try:result['fresh_process_observation']=observe(out/'processes_after')
            except BaseException as error:result['process_observation_failure']=repr(error)
        code=native['actual_exit_code'];result['interpreted_result']='EXACT_EIGHT_NEXT_LITERAL_GRAM_SAT_RAW_UNCHECKED' if code==10 else 'EXACT_EIGHT_NEXT_LITERAL_GRAM_UNSAT_TRACE_UNCHECKED' if code==20 else 'UNKNOWN_NATIVE_OR_RESOURCE_OUTCOME';result['end_to_end_wall_seconds']=time.monotonic()-started;result['outputs_sha256']={h.key(p):h.digest(p) for p in out.rglob('*') if p.is_file()};result['limitations']=['SAT requires separate complete assignment/clause/raw factor approval.','Cross-group caps and residualD omitted.','UNSAT requires full proof replay and exact literal profile encoding; no general target exclusion.','UNKNOWN excludes nothing.'];h.save(out/'summary.json',result);print(json.dumps(dict(result=result['interpreted_result'],code=code)))
    except BaseException as error:h.save(out/'failure.json',dict(error=repr(error),source_sha256=h.digest(Path(__file__))));raise
def main():
    p=argparse.ArgumentParser();mode=p.add_mutually_exclusive_group(required=True);mode.add_argument('--preflight',action='store_true');mode.add_argument('--research',action='store_true')
    for name in ('out','encoding-gate','object-gate','object-checker'):p.add_argument('--'+name,type=Path,required=True)
    for name in ('encoding-gate-sha256','object-gate-sha256'):p.add_argument('--'+name,required=True)
    run(p.parse_args())
if __name__=='__main__':main()
