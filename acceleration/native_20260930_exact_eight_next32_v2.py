"""Gated next32 sequential native attempts; import/preparation never runs a solver."""
from datetime import datetime,timezone
from pathlib import Path
import argparse,json,platform,re,shutil,subprocess,sys,time
from tqdm import tqdm
import native_20260930_unrestricted_full99 as h
import native_20260930_proof_location as e
import theory_20260930_exact_eight_campaign as producer
ROOT=h.ROOT;B=ROOT/'acceleration/results';SPEC=Path(__file__).with_name(Path(__file__).stem+'_spec.md')
BATCH=None;UNIVERSE=B/'20260930_exact_eight_campaign_preparation/campaign_manifest.json'
ENCODING_GATE=B/'20260930_independent_review/exact_eight_next32_cnfs/summary.json'
ENCODING_STATUS='INDEPENDENT_EXACT_EIGHT_NEXT32_ENCODING_PASS';OBJECT_STATUS='INDEPENDENT_EXACT_EIGHT_NEXT32_OBJECT_CALIBRATION_PASS'
LIMITS=dict(native_wall_seconds_per_attempt=60,conflicts_per_attempt=1000000,address_space_bytes=4*1024**3,proof_file_bytes=256*1024**2,kill_grace_seconds=5,outer_guard_seconds=70,first_batch_allocated_native_wall_seconds=1920,maximum_cases=32,aggregate_retained_artifact_bytes=64*1024**3,next_attempt_artifact_reserve_bytes=1024**3,host_free_reserve_bytes=32*1024**3,ext4_free_reserve_bytes=2*1024**3,sequential=True,automatic_retry=False,automatic_resume=False)
SEED=0;SEED_HELP=B/'20260930_native_cli_calibration/native_full_help.stdout.log'
PINS={UNIVERSE:'e7b07ea2f7c6b9f6738641afc22779a503841d5ac3da58d3873ebb0fa4b784ba',Path(producer.__file__):'9ebd87fea886f45fc916ad8afb9dc212fa089f760d4b96e55082926baef02c57',producer.SPEC:'76d89e652dc0d90084863e4478b9d887658daac21aedfa20ffc72bf7bf48bf69',Path(h.__file__):'da7ee9c03d454bd5ad0af0d82bead3520f3f270c70e71d4355161d036fd8ef22',Path(e.__file__):'ff7fd55658b7cb63e9586bd862f8f182269f2978a3b873ba9afccfa41a345854',SEED_HELP:'4958e610188eb62780aceb78bb466b98fb265dfd4c16553150a6b4c4aadd5c08',h.NATIVE:h.NATIVE_SHA,h.CHECKER:h.CHECKER_SHA,ROOT/'uv.lock':'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',ROOT/'pyproject.toml':'273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339'}
PINS.update(producer.PINS)
SELECTION=B/'20260930_exact_eight_next32_selection/selection.json'
NEXT_PLAN=ROOT/'acceleration/theory_20260930_exact_eight_next32_plan.md'
PRIOR_PROOFS=B/'20260930_independent_review/exact_eight_first12_proofs/summary.json'
PINS.update({SELECTION:'b906256dcf706c7d03360cc2cb7e31e5dd09b52cec3ba994ae9600954aeb88cd',NEXT_PLAN:'b91ff543c53b223b8db55d03d04a9266ffaca71b43bdbca10d85ddfa607bbd42',PRIOR_PROOFS:'a47da7d0e2e70d61c51679477de5257c676a201e59cc8977b250ed75e8c05ef9'})

def validate_next32(u,selection,prior):
    ids=[r['case_id']for r in u['records']];h.require(len(ids)==len(set(ids))==792 and u['universe_size']==792,'all792 distinct cases')
    h.require(not u['historical_profiles_subtracted']and not u['prior_exclusions_used'],'original population unchanged')
    h.require(prior['status']=='INDEPENDENT_EXACT_EIGHT_FIRST12_LITERAL_PROOFS_PASS'and prior['completed_proof_replays']==12 and prior['completed_attempts']==12 and prior['SAT_pending']==prior['UNKNOWN']==0 and not prior['pending_case_ids'],'complete independent first12 proof premise')
    old=prior['case_records'];oldids=[r['case_id']for r in old];h.require(oldids==prior['selected_case_ids']==u['first_batch_case_ids']and len(oldids)==len(set(oldids))==12,'exact previously verified12, no other subtraction')
    byid={r['case_id']:r for r in u['records']}
    for r in old:
        w=byid[r['case_id']];h.require(r['case_index']==w['case_index']and r['subset_index']==w['subset_index']and r['full_count_profile_sha256']==w['full_count_profile_sha256'],'prior proof literal membership')
        h.require(r['outcome']=='UNSAT_VERIFIED'and r['trace']['complete_proof']and r['replay']['accepted']and r['replay']['actual_exit_code']==0,'prior proof actually verified')
    expected=[cid for cid in ids if cid not in set(oldids)][:32]
    h.require(selection['schema']=='EXACT_EIGHT_EXPLICIT_BUILD_SELECTION_V1'and selection['campaign_manifest_path']==h.key(UNIVERSE)and selection['campaign_manifest_sha256']==PINS[UNIVERSE],'exact selection manifest')
    h.require(selection['authorization_record_path']==h.key(NEXT_PLAN)and selection['authorization_record_sha256']==PINS[NEXT_PLAN]and selection['completed_proof_gate_path']==h.key(PRIOR_PROOFS)and selection['completed_proof_gate_sha256']==PINS[PRIOR_PROOFS],'selection authorization and proof gate')
    h.require(selection['skipped_verified_case_ids']==oldids and selection['ordered_case_ids']==expected and len(set(expected))==32,'exact next32 order')
    h.require((selection['population'],selection['unresolved_before_batch'],selection['selected_instances'])==(792,780,32),'selection cardinalities')
    return expected


def source_closure():
    paths={Path(__file__).resolve(),SPEC.resolve(),producer.SPEC.resolve(),producer.shared.BASE.resolve()}
    for module in tuple(sys.modules.values()):
        name=getattr(module,'__file__',None)
        if name:
            p=Path(name).resolve()
            if p.is_relative_to(ROOT/'acceleration')and p.suffix=='.py':paths.add(p)
    return paths

def preflight(args):
    bindings={};cache={}
    def digest(p):
        p=p.resolve()
        if p not in cache:cache[p]=h.digest(p)
        return cache[p]
    for p,v in PINS.items():h.require(digest(p)==v,'frozen source/input/tool '+h.key(p));bindings[h.key(p)]=v
    h.require(args.encoding_gate.resolve()==ENCODING_GATE.resolve(),'exact next32 independent encoding report')
    h.require(digest(BATCH)==args.batch_summary_sha256,'explicit exact32 build summary');bindings[h.key(BATCH)]=args.batch_summary_sha256
    h.require(e.AS_LIMIT==LIMITS['address_space_bytes'],'unchanged4GiB address-space helper')
    h.require('--seed=0..2e9              random seed [0]'in SEED_HELP.read_text(),'authenticated actual default seed0')
    u=h.read(UNIVERSE);selection=h.read(SELECTION);prior=h.checked_gate(PRIOR_PROOFS,PINS[PRIOR_PROOFS],'INDEPENDENT_EXACT_EIGHT_FIRST12_LITERAL_PROOFS_PASS');ids=validate_next32(u,selection,prior);batch=h.read(BATCH);records=batch['records'];byid={r['case_id']:r for r in u['records']}
    for r in prior['case_records']:
        for field in['cnf','scope','run_summary','native_receipt']:
            p=ROOT/r[field+'_path'];v=r[field+'_sha256'];h.require(digest(p)==v and prior['inputs_sha256'].get(h.key(p))==v,'prior verified literal input/receipt');bindings[h.key(p)]=v
        p=ROOT/r['trace']['path'];v=r['trace']['sha256'];h.require(digest(p)==v and p.stat().st_size==r['trace']['bytes']and prior['inputs_sha256'].get(h.key(p))==v,'prior complete checked proof identity');bindings[h.key(p)]=v
        oldscope=h.read(ROOT/r['scope_path']);h.require(oldscope['campaign_case_id']==r['case_id']and oldscope['coordinate_group_fibre_counts']==byid[r['case_id']]['raw_representative']['counts'],'prior exact raw-count scope')
    h.require(batch['status']=='CANDIDATE_EXACT_EIGHT_EXPLICIT_FORMULAS_COMPLETE'and batch['completed_formulas']==32 and not batch['pending_case_ids']and batch['native_calls']==0,'all32 literal formulas built')
    h.require(batch['selected_case_ids']==ids==[r['case_id']for r in records]and len(ids)==len(set(ids))==32,'exact selected32 build order')
    h.require(batch['inputs_sha256'].get(h.key(SELECTION))==PINS[SELECTION],'build exact selection pin')
    direct={BATCH,UNIVERSE,SELECTION,NEXT_PLAN,PRIOR_PROOFS,producer.RAW,producer.LOCAL,producer.PLAN,Path(producer.__file__),producer.SPEC,producer.BLOCK_GATE,producer.BLOCK_SUMMARY}
    for r in records:
        ident=r['case_id'];w=byid[ident];h.require(ident=='exact_eight_'+w['full_count_profile_sha256']and r['case_index']==w['case_index']and r['subset_index']==w['subset_index'],'stable full-count case identity')
        for name,f in r['files'].items():
            p=ROOT/f['path'];h.require(digest(p)==f['sha256']and p.stat().st_size==f['bytes'],'all prepared case files');bindings[h.key(p)]=f['sha256'];direct.add(p)
        summary=h.read(ROOT/r['files']['summary.json']['path'])
        h.require(summary['case_id']==r['case_id']and summary['attempt_id']==r['attempt_id']and summary['status']=='CANDIDATE_EXACT_EIGHT_CAMPAIGN_LITERAL_FULL_GRAM_BUILT'and summary['native_calls']==0,'individual complete build/attempt identity across consolidation')
        for name,v in {**summary['inputs_sha256'],**summary['outputs_sha256']}.items():h.require(digest(ROOT/name)==v,'all case preparation inputs/outputs');bindings[name]=v
        scope=h.read(ROOT/r['files']['scope.json']['path']);profile=h.read(ROOT/r['files']['selected_profile.json']['path']);model=h.read(ROOT/r['files']['model.json']['path'])
        h.require(scope['campaign_case_id']==scope['selected_profile_id']==profile['campaign_case_id']==ident and scope['campaign_manifest_sha256']==PINS[UNIVERSE],'literal campaign scope')
        h.require(scope['selected_full_count_sha256']==profile['full_count_profile_sha256']==w['full_count_profile_sha256']and scope['selected_profile_sha256']==profile['profile_sha256'],'both digest conventions')
        h.require(profile['coordinate_group_fibre_counts']==w['raw_representative']['counts']and scope['exceptional_groups']==profile['exceptional_groups']==w['raw_representative']['exceptional_groups']and len(scope['exceptional_groups'])==8,'literal raw counts')
        h.require(scope['within_group_column_caps_encoded']and not any(scope[k]for k in ['cross_group_column_caps_encoded','residual_D_encoded','arc_pruning_used','orbit_coverage_used','target_graph']),'exact full-initial scope and omissions')
        sizes=[len(d['choices'])for d in model['domains']];S=sum(sizes)
        h.require(sizes==r['initial_domain_sizes']and(r['selectors'],r['variables'],r['clauses'])==(S,2*S+5380,49*S+60400)==(model['primary_selectors'],model['variables'],model['clauses']),'actual per-case dimensions')
        with(ROOT/r['files']['instance.cnf']['path']).open('rb')as f:h.require(f.readline()==f"p cnf {r['variables']} {r['clauses']}\n".encode(),'exact actual CNF header')
    reports=[]
    for p,v,status in [(args.encoding_gate,args.encoding_gate_sha256,ENCODING_STATUS),(args.object_gate,args.object_gate_sha256,OBJECT_STATUS)]:
        report=h.checked_gate(p,v,status);reports.append(report)
        for name,w in report['inputs_sha256'].items():h.require(digest(ROOT/name)==w,'unchanged gate input '+name);bindings[name]=w
        for raw in direct:h.require(report['inputs_sha256'].get(h.key(raw))==digest(raw),'direct case/population gate '+h.key(raw))
        bindings[h.key(p)]=v
    h.require(reports[1]['inputs_sha256'].get(h.key(args.encoding_gate))==args.encoding_gate_sha256,'same exact encoding gate')
    h.require(reports[0]['population_size']==792 and reports[0]['complete_formulas']==32 and reports[0]['selected_case_ids']==ids,'encoding gate exact aggregate scope')
    checked=reports[0]['checked_cases'];h.require([r['case_id']for r in checked]==ids,'literal gate case order')
    for rec,approved in zip(records,checked):
        h.require(approved['case_index']==rec['case_index']and approved['full_count_profile_sha256']==rec['full_count_profile_sha256'],'same independently checked literal case')
        for name,field in [('instance.cnf','cnf'),('model.json','model'),('scope.json','scope')]:h.require(approved[field+'_path']==rec['files'][name]['path']and approved[field+'_sha256']==rec['files'][name]['sha256'],'same independently checked formula')
    for p in source_closure()|{args.object_checker.resolve()}:
        v=digest(p);h.require(reports[1]['inputs_sha256'].get(h.key(p))==v,'complete native/checker source closure');bindings[h.key(p)]=v
    for name,v,status in [('20260930_native_cli_calibration','f5ff562aff2ec550a97685c7012b302e760314a6f3829d80d022e2a669e680eb','INDEPENDENT_NATIVE_CADICAL195_CLI_CALIBRATION_PASS'),('20260930_native_proof_location','d1036cfcbe9b24e0f7ea6e0a3799968a5d9232e8167fb31b224211e5c845c619','NATIVE_EXT4_PROOF_PATH_CALIBRATION_PASS')]:
        p=B/name/'summary.json';h.checked_gate(p,v,status);bindings[h.key(p)]=v
    return bindings,records

def command(cnf,proof):return e.command(60,[h.linux(h.NATIVE),'--no-binary','--seed=0','-c','1000000',h.linux(cnf),proof],file_limit=LIMITS['proof_file_bytes'])

def observe(prefix):
    r=h.run_record([*h.WSL,'/usr/bin/ps','-C','cadical','-o','pid,ppid,comm,pcpu,rss,args'],prefix,10)
    h.require(not r['outer_windows_guard_expired']and r['actual_exit_code']in(0,1),'targeted process observation')
    if r['actual_exit_code']==1:h.require(len(Path(str(prefix)+'.stdout.log').read_text().strip().splitlines())<=1,'no matching process')
    return r

def resources(folder,linux='/tmp'):
    folder.mkdir(parents=True,exist_ok=False);mount,text=e.local_capture(['/usr/bin/findmnt','--target',linux,'--output','TARGET,SOURCE,FSTYPE,OPTIONS','--noheadings'],folder/'filesystem');h.require('ext4'in text.split(),'ext4 proof mount')
    disk,text=e.local_capture(['/usr/bin/df','--output=avail','-B1',linux],folder/'disk_free');host=shutil.disk_usage(ROOT).free;ext4=int(text.splitlines()[-1])
    return dict(host_free_bytes=host,ext4_free_bytes=ext4,mount_receipt=mount,disk_receipt=disk,pass_reserves=host>=LIMITS['host_free_reserve_bytes']and ext4>=LIMITS['ext4_free_reserve_bytes'])

def observed_result(receipt,stdout,proof_bytes):
    code=receipt['actual_exit_code'];statuses=[line.strip()for line in stdout.splitlines()if line.startswith('s ')];conflicts=[]
    for line in stdout.splitlines():
        m=re.match(r'^c\s+conflicts:\s*([\d,]+)',line)
        if m:conflicts.append(int(m.group(1).replace(',','')))
    valid_sat=code==10 and statuses==['s SATISFIABLE'];valid_unsat=code==20 and statuses==['s UNSATISFIABLE']
    if receipt['outer_windows_guard_expired']:reason='OUTER_GUARD_PROCESS_STATE_UNKNOWN'
    elif valid_sat:reason='SAT_RAW_OBJECT_PENDING_REVIEW'
    elif valid_unsat and proof_bytes is not None:reason='UNSAT_TRACE_PENDING_COMPLETE_REPLAY'
    elif valid_unsat:reason='UNSAT_TRACE_UNAVAILABLE_UNKNOWN'
    elif code==124:reason='UNKNOWN_WALL_LIMIT'
    elif code==153 or proof_bytes is not None and proof_bytes>=LIMITS['proof_file_bytes']:reason='UNKNOWN_FILE_LIMIT_OR_FULL_TRACE_CAP'
    elif code==0 and conflicts and conflicts[-1]>=LIMITS['conflicts_per_attempt']:reason='UNKNOWN_CONFLICT_LIMIT'
    elif code in(137,143):reason='UNKNOWN_SIGNAL_OR_RESOURCE_TERMINATION'
    else:reason='UNKNOWN_NATIVE_STATUS_OR_RESOURCE_OUTCOME'
    return dict(interpretation=reason,actual_exit_code=code,native_status_lines=statuses,observed_conflicts=conflicts[-1]if conflicts else None,observed_conflicts_null_reason=None if conflicts else'Counter absent from preserved stdout; no invented value.',configured_conflict_limit=LIMITS['conflicts_per_attempt'],configured_wall_limit=60,configured_file_limit=LIMITS['proof_file_bytes'],mathematical_approval=False)

def one_case(args,record,out,bindings):
    index=record['case_index'];cid=record['case_id'];attempt=args.attempt_id+f'_case_{index:04d}';folder=out/f'case_{index:04d}';folder.mkdir();files=record['files']
    for name,f in files.items():h.require(h.digest(ROOT/f['path'])==f['sha256'],'immediate prepared-input identity')
    cnf=ROOT/files['instance.cnf']['path'];before=observe(folder/'processes_before');made,directory=e.local_capture(['/usr/bin/mktemp','-d',f'/tmp/conway99-exact-eight-{index:04d}-XXXXXX'],folder/'mktemp')
    h.require(directory.startswith(f'/tmp/conway99-exact-eight-{index:04d}-')and'\n'not in directory,'fresh ext4 workspace');h.save(folder/'workspace.json',dict(path=directory,creation_observed=True,created_at=datetime.now(timezone.utc).isoformat(),future_availability='UNKNOWN',deletion_requested_by_driver=False,receipt=made))
    reserve=resources(folder/'resources',directory)
    if not reserve['pass_reserves']:h.save(folder/'not_launched.json',dict(case_id=cid,attempt_id=attempt,reason='HOST_OR_EXT4_RESERVE',resource_check=reserve));return None,'HOST_OR_EXT4_RESERVE'
    main=folder/'main';main.mkdir();proof=directory+'/proof.drat';cmd=command(cnf,proof)
    h.save(main/'launch.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),case_id=cid,case_index=index,attempt_id=attempt,command=cmd,seed=SEED,seed_setting='Explicit --seed=0, equal to authenticated native default.',cnf_sha256=files['instance.cnf']['sha256'],ext4_proof=proof,inputs_sha256=bindings,limits=LIMITS))
    print(json.dumps(dict(state='EXACT_EIGHT_NEXT32_NATIVE_LAUNCH',case_id=cid,attempt_id=attempt,variables=record['variables'],clauses=record['clauses'])),flush=True)
    native=h.run_record(cmd,main/'solver',70);result=dict(status='EXACT_EIGHT_NEXT32_CASE_PENDING_INDEPENDENT_OUTCOME',case_id=cid,case_index=index,attempt_id=attempt,inputs_sha256=bindings,cnf=files['instance.cnf'],model=files['model.json'],scope=files['scope.json'],selected_profile=files['selected_profile.json'],native_receipt=native,seed=SEED,processes_before=before,resource_check=reserve,native_calls=1,independent_approval=False,target_graph=False)
    stop=None
    if native['outer_windows_guard_expired']:stop='OUTER_GUARD_PROCESS_STATE_UNKNOWN'
    else:
        t=time.monotonic()
        try:result['proof_copy']=e.proof_copy(proof,main/'proof.drat',main/'transfer');h.require(result['proof_copy']['bytes']<=LIMITS['proof_file_bytes'],'actual256MiB proof cap')
        except BaseException as ex:result['proof_copy_failure']=dict(error=repr(ex),linux_original_path=proof,identity_available=False,future_availability='UNKNOWN');stop='TRACE_IDENTITY_UNAVAILABLE'
        result['transfer_wall_seconds']=time.monotonic()-t
        if native['actual_exit_code']==10:
            stop='SAT_PENDING_INDEPENDENT_REVIEW'
            try:assignment=h.parse_sat_stdout((main/'solver.stdout.log').read_text(),record['variables']);h.save(main/'parsed_model.json',dict(assignment=assignment))
            except BaseException as ex:result['assignment_parse_failure']=repr(ex)
            if(main/'parsed_model.json').exists():
                try:decoded=producer.decode(assignment,ROOT/files['model.json']['path'],ROOT/files['scope.json']['path'],cnf);h.save(main/'decoded_Gram_factor.json',decoded)
                except BaseException as ex:result['candidate_decode_failure']=repr(ex)
                try:
                    check=[sys.executable,'-B',str(args.object_checker),'sat','--case-id',cid,'--encoding-gate',str(args.encoding_gate),'--encoding-gate-sha256',args.encoding_gate_sha256,'--assignment',str(main/'parsed_model.json'),'--native-output',str(main/'solver.stdout.log'),'--out',str(folder/'independent_object')]
                    if(main/'decoded_Gram_factor.json').exists():check+=['--decoded',str(main/'decoded_Gram_factor.json')]
                    result['independent_object_receipt']=h.run_record(check,folder/'independent_object_command',120)
                except BaseException as ex:result['independent_object_failure']=repr(ex)
        try:result['processes_after']=observe(folder/'processes_after')
        except BaseException as ex:result['process_observation_failure']=repr(ex);stop=stop or'PROCESS_OBSERVATION_FAILED'
    proof_bytes=result.get('proof_copy',{}).get('bytes');outcome=observed_result(native,(main/'solver.stdout.log').read_text(errors='replace'),proof_bytes);result['outcome']=outcome
    if outcome['interpretation']!='UNSAT_TRACE_PENDING_COMPLETE_REPLAY':stop=stop or outcome['interpretation']
    result['stop_reason']=stop;result['host_artifact_bytes_before_summary']=sum(p.stat().st_size for p in folder.rglob('*')if p.is_file());result['ext4_trace_bytes']=proof_bytes;result['ext4_trace_bytes_null_reason']=None if proof_bytes is not None else'Unknown trace identity/size; campaign stops.'
    result['outputs_sha256']={h.key(p):h.digest(p)for p in folder.rglob('*')if p.is_file()};h.save(folder/'summary.json',result)
    return dict(case_id=cid,case_index=index,attempt_id=attempt,summary_path=h.key(folder/'summary.json'),summary_sha256=h.digest(folder/'summary.json'),actual_exit_code=native['actual_exit_code'],interpreted_result=outcome['interpretation'],wrapped_wall_seconds=native['wall_seconds'],allocated_native_wall_seconds=60,ext4_trace_bytes=proof_bytes),stop

def run(args):
    global BATCH
    BATCH=args.batch_summary.resolve();h.require(BATCH.is_relative_to(ROOT)and BATCH.is_file(),'explicit repository-contained complete32 consolidation')
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic();completed=[];selection=[]
    try:
        h.require(args.attempt_id and args.attempt_id.isascii()and all(c.isalnum()or c in '_-'for c in args.attempt_id),'explicit safe attempt identity')
        bindings,records=preflight(args);selection=[r['case_id']for r in records];initial=resources(out/'initial_resources');h.require(initial['pass_reserves'],'initial32GiBhost/2GiBext4 reserve')
        manifest=dict(build_consolidation_path=h.key(BATCH),build_consolidation_sha256=args.batch_summary_sha256,timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,limits=LIMITS,seed=SEED,seed_option='--seed=0',seed_default_evidence=dict(path=h.key(SEED_HELP),sha256=PINS[SEED_HELP],line='--seed=0..2e9 random seed [0]'),selection=selection,campaign_population_manifest=dict(path=h.key(UNIVERSE),sha256=PINS[UNIVERSE]),attempt_id=args.attempt_id,mode='PREFLIGHT_ONLY'if args.preflight else'RESEARCH',automatic_resume=False)
        h.save(out/'manifest.json',manifest)
        if args.preflight:h.save(out/'summary.json',dict(status='EXACT_EIGHT_NEXT32_NATIVE_PREFLIGHT_PASS',inputs_sha256=bindings,selected_case_ids=selection,limits=LIMITS,seed=SEED,native_calls=0));return
        stop='ALL_NEXT32_ATTEMPTED';base=dict(inputs_sha256=bindings,selected_case_ids=selection,manifest_path=h.key(out/'manifest.json'),manifest_sha256=h.digest(out/'manifest.json'),attempt_id=args.attempt_id)
        for r in tqdm(records,desc='Native next32 exact-eight cases',mininterval=1):
            host=sum(p.stat().st_size for p in out.rglob('*')if p.is_file());ext4=sum(x['ext4_trace_bytes']or 0 for x in completed)
            if host+ext4+LIMITS['next_attempt_artifact_reserve_bytes']>LIMITS['aggregate_retained_artifact_bytes']:stop='AGGREGATE_ARTIFACT_RESERVE';break
            if 60*(len(completed)+1)>LIMITS['first_batch_allocated_native_wall_seconds']:stop='ALLOCATED_NATIVE_WALL_LIMIT';break
            row,reason=one_case(args,r,out,bindings)
            if row is None:stop=reason;break
            completed.append(row);h.save(out/f'checkpoint_{len(completed):02d}.json',dict(status='EXACT_EIGHT_NEXT32_CHECKPOINT',**base,case_records=completed,pending_case_ids=selection[len(completed):],stop_reason=reason,automatic_resume=False))
            total=sum(p.stat().st_size for p in out.rglob('*')if p.is_file())+sum(x['ext4_trace_bytes']or 0 for x in completed)
            if reason:stop=reason;break
            if total>LIMITS['aggregate_retained_artifact_bytes']:stop='OBSERVED_AGGREGATE_ARTIFACT_LIMIT';break
        host=sum(p.stat().st_size for p in out.rglob('*')if p.is_file());ext4=sum(x['ext4_trace_bytes']or 0 for x in completed)
        h.save(out/'restart_requirements.json',dict(automatic_resume=False,pending_case_ids=selection[len(completed):],completed_attempts=completed,requirements=['This wrapper has no resume option and never overwrites an existing attempt directory.','Root must independently authenticate each completed native outcome/proof or SAT object before any continuation may skip it. Exit20 alone is not proof verification.','Any continuation needs a separately frozen exact remaining-case plan/source and new attempt/output paths, binding unchanged formula, prior receipts and independent outcome gates.','SAT, UNKNOWN, missing trace identity or unknown process state require root reassessment before further native calls.'],mathematical_exclusions_asserted=0))
        h.save(out/'summary.json',dict(status='EXACT_EIGHT_NEXT32_NATIVE_STOPPED',timestamp=datetime.now(timezone.utc).isoformat(),**base,case_records=completed,completed_attempts=len(completed),pending_case_ids=selection[len(completed):],stop_reason=stop,native_calls=len(completed),allocated_native_wall_seconds=60*len(completed),wrapped_native_wall_seconds=sum(x['wrapped_wall_seconds']for x in completed),host_artifact_bytes_before_summary=host,known_ext4_trace_bytes=ext4,observed_artifact_bytes_before_summary=host+ext4,trace_accounting='Host originals/receipts/logs plus separate ext4 trace copies; missing trace identity stops and is not counted as known zero.',end_to_end_wall_seconds=time.monotonic()-start,independent_approval=False,target_resolution=False,automatic_retry=False,automatic_resume=False,limitations=['UNSAT is pending complete independent DRAT replay, not a verified case exclusion.','SAT pauses after the independent raw-object path and does not establish residualD or a target graph.','Every UNKNOWN or resource stop pauses for reassessment and excludes nothing.','Allocated1920s covers32x60 native limits; actual wrapped, transfer and verification overhead are recorded separately.']))
    except BaseException as ex:h.save(out/'failure.json',dict(error=repr(ex),source_sha256=h.digest(Path(__file__)),completed_attempts=completed,selected_case_ids=selection,automatic_retry=False));raise

def main():
    p=argparse.ArgumentParser();m=p.add_mutually_exclusive_group(required=True);m.add_argument('--preflight',action='store_true');m.add_argument('--research',action='store_true')
    for n in ['out','batch-summary','encoding-gate','object-gate','object-checker']:p.add_argument('--'+n,type=Path,required=True)
    for n in ['encoding-gate-sha256','object-gate-sha256','batch-summary-sha256','attempt-id']:p.add_argument('--'+n,required=True)
    run(p.parse_args())
if __name__=='__main__':main()
