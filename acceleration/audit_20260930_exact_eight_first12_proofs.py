"""Complete first12 campaign receipt and DRAT review. No native solver calls."""
import argparse,hashlib,importlib.util,json,platform,re,subprocess,sys,time,traceback
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results';I=B/'20260930_independent_review'
RUN=B/'20260930_exact_eight_first12_native_pilot';DATA=B/'20260930_exact_eight_first12_cnfs/summary.json'
ENC=I/'exact_eight_campaign/summary.json';OBJ=I/'exact_eight_campaign_object_calibration/summary.json'
PRIOR=I/'hadamard_balanced_gram_unsat_v2/summary.json';HELPER=ROOT/'acceleration/audit_20260930_hadamard_balanced_gram_unsat_v2.py'
OLD=I/'exact_eight_next_lift_unsat/summary.json';DOC=ROOT/'docs/AUDIT_20260930_EXACT_EIGHT_FIRST12_PROOFS.md'
CID='C-FIXED-HADAMARD-EXACT-EIGHT-FIRST12-LITERAL-PROFILE-EXCLUSIONS'
PINS={DATA:'3f7abda7d7e12a6babaf48c6c690f85bf1db69e6401098f2ece9a881b1772136',ENC:'e334293416c1048cf3a6e7c4bd8242892dc84e7f7d773bd388b506fdde77ea27',OBJ:'35977335717b169b33448d1ff84eb7f00319ee6a59f522b82ff9906014268763',PRIOR:'edbbda720ea38ca5c565837bc39b5083eb145a64386c9e070fe89dfe5d6cebc5',OLD:'a21cd5fc95f1fb1dcd7eb849b620584fbde489cdcf4819e392ddf935d621c037',ROOT/'acceleration/native_20260930_exact_eight_campaign_v2.py':'e4a406a8b6f77db93257bc9a6265ffa0c7944af26d4a77e2b7017c67ef3dce2f',ROOT/'acceleration/native_20260930_exact_eight_campaign_v2_spec.md':'586619b415f4d44eda57c8fd6874fe14597036a40edc21f6724baf7daf96a817'}
LIMITS=dict(native_wall_seconds_per_attempt=60,conflicts_per_attempt=1000000,address_space_bytes=4*1024**3,proof_file_bytes=256*1024**2,kill_grace_seconds=5,outer_guard_seconds=70,first_batch_allocated_native_wall_seconds=720,maximum_cases=12,aggregate_retained_artifact_bytes=64*1024**3,next_attempt_artifact_reserve_bytes=1024**3,host_free_reserve_bytes=32*1024**3,ext4_free_reserve_bytes=2*1024**3,sequential=True,automatic_retry=False,automatic_resume=False)
def need(v,m):
    if not v:raise ValueError(m)
def sha(p):
    with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(p.read_bytes())
def save(p,v):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(v,f,indent=2);f.write('\n')
def linux(p):return '/mnt/'+str(p.resolve())[0].lower()+str(p.resolve())[2:].replace('\\','/')
def parse_unsat(text,r,V,M):
    lines=text.splitlines();need([l for l in lines if l.startswith('s ')]==['s UNSATISFIABLE'],'one exact UNSAT status')
    need(lines.count(f"c found 'p cnf {V} {M}' header")==1,'actual checked formula dimensions')
    need(lines.count('c exit 20')==1 and r['actual_exit_code']==20 and r['outer_windows_guard_expired'] is False,'normal native20')
    need('c Version 1.9.5 146207318796f094dcded87349a64f0c6927309e'in lines,'authenticated native version')
    need("c setting conflict limit to 1000000 conflicts (due to '1000000')"in lines,'configured conflict bound')
    def one(pattern,typ):
        vals=re.findall(pattern,text,re.M);need(len(vals)==1,'unique native statistic');return typ(vals[0])
    conflicts=re.findall(r'^c conflicts:\s+(\d+)\s',text,re.M);need(len(conflicts)<=1,'optional unique conflicts statistic')
    stats=dict(conflicts=int(conflicts[0])if conflicts else None,conflicts_null_reason=None if conflicts else'Native did not print the named statistic.',native_cpu_seconds=one(r'^c total process time since initialization:\s+([0-9.]+)\s+seconds$',float),native_wall_seconds=one(r'^c total real time since initialization:\s+([0-9.]+)\s+seconds$',float),trace_bytes=one(r'^c DRAT (\d+) bytes ',int),wrapper_wall_seconds=r['wall_seconds'])
    need((stats['conflicts']is None or 0<=stats['conflicts']<=1000000)and 0<stats['trace_bytes']<=256*1024**2 and 0<=stats['native_wall_seconds']<60 and r['wall_seconds']<70,'complete bounded native result')
    return stats
def classify(text,r,n):
    statuses=[l.strip()for l in text.splitlines()if l.startswith('s ')];conflicts=re.findall(r'^c\s+conflicts:\s*([\d,]+)',text,re.M);c=int(conflicts[-1].replace(',',''))if conflicts else None;code=r['actual_exit_code']
    if r['outer_windows_guard_expired']:kind='OUTER_GUARD_PROCESS_STATE_UNKNOWN'
    elif code==10 and statuses==['s SATISFIABLE']:kind='SAT_RAW_OBJECT_PENDING_REVIEW'
    elif code==20 and statuses==['s UNSATISFIABLE']:kind='UNSAT_TRACE_PENDING_COMPLETE_REPLAY'if n is not None else'UNSAT_TRACE_UNAVAILABLE_UNKNOWN'
    elif code==124:kind='UNKNOWN_WALL_LIMIT'
    elif code==153 or n is not None and n>=256*1024**2:kind='UNKNOWN_FILE_LIMIT_OR_FULL_TRACE_CAP'
    elif code==0 and c is not None and c>=1000000:kind='UNKNOWN_CONFLICT_LIMIT'
    elif code in (137,143):kind='UNKNOWN_SIGNAL_OR_RESOURCE_TERMINATION'
    else:kind='UNKNOWN_NATIVE_STATUS_OR_RESOURCE_OUTCOME'
    return kind,statuses,c
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--campaign-summary-sha256',required=True);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();need(re.fullmatch('[0-9a-f]{64}',a.campaign_summary_sha256),'explicit terminal campaign hash')
    out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};start=time.perf_counter()
    def pin(p,h=None):
        p=p.resolve();name=key(p)
        if name not in pins:pins[name]=sha(p)
        need(h is None or pins[name]==h,'hash '+name);return pins[name]
    def receipt(r,code=None,guard=False):
        need(guard or r['outer_windows_guard_expired']is False,'observed receipt guard')
        if code is not None:need(r['actual_exit_code']==code,'receipt exit')
        for f in ['stdout','stderr']:pin(ROOT/r[f],r[f+'_sha256'])
    def resource(r):
        need(r['pass_reserves']is True and r['host_free_bytes']>=32*1024**3 and r['ext4_free_bytes']>=2*1024**3,'actual prelaunch reserves')
        for field in ['mount_receipt','disk_receipt']:receipt(r[field],0)
        need('ext4'in(ROOT/r['mount_receipt']['stdout']).read_text().split(),'observed ext4 mount');need(int((ROOT/r['disk_receipt']['stdout']).read_text().split()[-1])==r['ext4_free_bytes'],'actual disk reading')
    try:
        pin(RUN/'summary.json',a.campaign_summary_sha256)
        for p,h in PINS.items():pin(p,h)
        for p in [Path(__file__),DOC]:pin(p)
        pin(HELPER,read(PRIOR)['inputs_sha256'][key(HELPER)]);s=importlib.util.spec_from_file_location('independent_drat_replay_helper',HELPER);helper=importlib.util.module_from_spec(s);s.loader.exec_module(helper)
        for p in [helper.BUILD/'drat-trim.exe',helper.BUILD/'build_manifest.json',helper.BUILD/'build_receipt.json']:pin(p,helper.PINS[p])
        provenance=helper.authenticate(pin);enc=read(ENC);obj=read(OBJ)
        need(enc['status']=='INDEPENDENT_EXACT_EIGHT_CAMPAIGN_ENCODING_PASS'and obj['status']=='INDEPENDENT_EXACT_EIGHT_CAMPAIGN_OBJECT_CALIBRATION_PASS','exact prelaunch gates');need(obj['inputs_sha256'][key(ENC)]==PINS[ENC],'same encoding gate')
        for report in [enc,obj]:
            for name,h in report['inputs_sha256'].items():pin(ROOT/name,h)
        ep=ENC.parent/'claim_binding.json';pin(ep,enc['outputs_sha256'][key(ep)]);eb=read(ep);need(eb['id']=='C-FIXED-HADAMARD-EXACT-EIGHT-CAMPAIGN-FIRST12-GRAM-ENCODINGS'and eb['revision']==1,'exact encoding revision')
        data=read(DATA);selection=data['selected_case_ids'];formula={r['case_id']:r for r in data['records']};approved={r['case_id']:r for r in enc['checked_cases']}
        need(selection==enc['selected_case_ids']and len(selection)==len(set(selection))==len(approved)==12,'exact12 distinct literal cases')
        final=read(RUN/'summary.json');manifest=read(RUN/'manifest.json')
        for p in RUN.rglob('*'):
            if p.is_file():pin(p)
        for name,h in manifest['inputs_sha256'].items():pin(ROOT/name,h)
        need(final['status']=='EXACT_EIGHT_CAMPAIGN_NATIVE_STOPPED'and manifest['mode']=='RESEARCH','completed source-bound research record')
        need(manifest['selection']==final['selected_case_ids']==selection,'exact selected list')
        if 'limits'in final:need(manifest['limits']==final['limits'],'same summary allocation')
        need(manifest['limits']==LIMITS and manifest['seed']==0 and manifest['seed_option']=='--seed=0'and manifest['automatic_resume']is False,'entire declared native allocation')
        need(final['inputs_sha256']==manifest['inputs_sha256']and final['manifest_path']==key(RUN/'manifest.json')and final['manifest_sha256']==sha(RUN/'manifest.json'),'exact immutable campaign inputs')
        records=final['case_records'];need([r['case_id']for r in records]==selection[:len(records)]and final['pending_case_ids']==selection[len(records):]and final['completed_attempts']==final['native_calls']==len(records),'attempted prefix and unattempted suffix')
        need(len(records)<=12 and final['automatic_retry']is False and final['automatic_resume']is False and final['independent_approval']is False and final['target_resolution']is False,'no hidden retries or promoted producer outcome')
        if len(records)==12:need(final['stop_reason']=='ALL_FIRST12_ATTEMPTED','complete campaign stop reason')
        restart=read(RUN/'restart_requirements.json');need(restart['automatic_resume']is False and restart['pending_case_ids']==final['pending_case_ids']and restart['completed_attempts']==records and restart['mathematical_exclusions_asserted']==0,'honest restart prerequisites')
        for index,ref in enumerate(records,1):
            checkpoint=read(RUN/f'checkpoint_{index:02d}.json');need(checkpoint['case_records']==records[:index]and checkpoint['pending_case_ids']==selection[index:]and checkpoint['inputs_sha256']==manifest['inputs_sha256'],'each exact immutable attempt checkpoint')
        fixtures={'tiny_unsat.cnf':b'p cnf 2 4\n1 2 0\n1 -2 0\n-1 2 0\n-1 -2 0\n','tiny_sat.cnf':b'p cnf 2 3\n1 2 0\n1 -2 0\n-1 2 0\n','tiny_valid.drat':b'-2 0\n1 0\n0\n','empty_only.drat':b'0\n','fresh_unit.drat':b'3 0\n0\n'}
        for name,contents in fixtures.items():(out/name).write_bytes(contents)
        tiny=[(1,2),(1,-2),(-1,2),(-1,-2)];oracle=lambda cs:[bits for bits in range(4)if all(any(bool(bits&(1<<(abs(v)-1)))==(v>0)for v in c)for c in cs)];need(oracle(tiny)==[]and oracle(tiny[:-1])==[3],'complete tiny truth controls')
        tests=[('positive_reasoning','tiny_unsat.cnf','tiny_valid.drat',True),('missing_reasoning','tiny_unsat.cnf','empty_only.drat',False),('fresh_unit','tiny_unsat.cnf','fresh_unit.drat',False),('changed_SAT_input','tiny_sat.cnf','tiny_valid.drat',False)]
        controls=[helper.replay(name,out/cnf,out/proof,out,wanted)for name,cnf,proof,wanted in tests];checked=[];totals=Counter();attacks=[];used=0.;known_ext4=0
        for n,ref in enumerate(records):
            cid=ref['case_id'];f=formula[cid];apr=approved[cid];sp=ROOT/ref['summary_path'];pin(sp,ref['summary_sha256']);row=read(sp);folder=sp.parent;main=folder/'main'
            need(sp==RUN/f"case_{f['case_index']:04d}"/'summary.json'and row['case_id']==cid and row['case_index']==f['case_index']and row['attempt_id']==ref['attempt_id']==manifest['attempt_id']+f"_case_{f['case_index']:04d}",'exact case/attempt/path identity')
            need(row['native_calls']==1 and row['independent_approval']is False and row['target_graph']is False and row['inputs_sha256']==manifest['inputs_sha256'],'literal native call bookkeeping')
            for name,h in row['outputs_sha256'].items():pin(ROOT/name,h)
            for name,field in [('instance.cnf','cnf'),('model.json','model'),('scope.json','scope'),('selected_profile.json','selected_profile')]:
                need(row[field]==f['files'][name],'same actual prepared file');ff=f['files'][name];pin(ROOT/ff['path'],ff['sha256']);need(enc['inputs_sha256'][ff['path']]==ff['sha256'],'independent exact input binding')
            cnf=ROOT/f['files']['instance.cnf']['path'];scope=read(ROOT/f['files']['scope.json']['path']);need(scope['selected_profile_id']==cid and scope['selected_full_count_sha256']==f['full_count_profile_sha256']==apr['full_count_profile_sha256'],'same complete count table identity')
            need(scope['within_group_column_caps_encoded']is True and all(scope[k]is False for k in ['cross_group_column_caps_encoded','residual_D_encoded','arc_pruning_used','orbit_coverage_used','target_graph']),'exact initial-domain literal scope')
            r=read(main/'solver.receipt.json');launch=read(main/'launch.json');workspace=read(folder/'workspace.json');need(row['native_receipt']==r and launch['command']==r['command']and launch['cnf_sha256']==f['files']['instance.cnf']['sha256']and launch['limits']==LIMITS and launch['seed']==row['seed']==0,'complete actual launch agreement')
            need(workspace['creation_observed']is True and workspace['future_availability']=='UNKNOWN'and workspace['deletion_requested_by_driver']is False,'recorded creation, no invented current availability');receipt(workspace['receipt'],0)
            proof_source=workspace['path']+'/proof.drat';cmd=['wsl.exe','--distribution','Ubuntu-24.04','--exec','/usr/bin/timeout','--signal=TERM','--kill-after=5s','60s','/usr/bin/prlimit','--as=4294967296:4294967296','--fsize=268435456:268435456','--core=0:0',linux(ROOT/'build/research-cadical195/source/build/cadical'),'--no-binary','--seed=0','-c','1000000',linux(cnf),proof_source]
            need(r['command']==cmd and launch['ext4_proof']==proof_source and r['outer_windows_guard_seconds']==70,'exact new256MiB/seed0 command, not old10GiB');receipt(r,guard=True);resource(row['resource_check'])
            for phase in ['processes_before','processes_after']:
                if phase not in row:need(row['stop_reason']is not None,'missing process observation disclosed');continue
                pr=row[phase];receipt(pr);need(pr['command'][4:]==['/usr/bin/ps','-C','cadical','-o','pid,ppid,comm,pcpu,rss,args']and pr['actual_exit_code']in(0,1),'targeted saved process observation');need('/'+key(cnf)not in(ROOT/pr['stdout']).read_text(),'no live exact-input process in saved observation')
            trace=None
            if 'proof_copy'in row:
                t=row['proof_copy'];proof=main/'proof.drat';pin(proof,t['sha256']);need(proof.stat().st_size==t['bytes']<=256*1024**2,'exact saved host trace size/hash');receipt(t['native_hash_receipt'],0);receipt(t['copy_receipt'],0)
                need(t['linux_source']==proof_source and t['native_hash_receipt']['command'][-2:]==['/usr/bin/sha256sum',proof_source]and(ROOT/t['native_hash_receipt']['stdout']).read_text().split()==[t['sha256'],proof_source],'historical full ext4 hash identity')
                need(t['copy_receipt']['command'][-4:-1]==['/usr/bin/cp','--',proof_source]and t['copy_receipt']['command'][-1]==linux(proof),'immediate exact host transfer')
                trace=dict(path=key(proof),sha256=t['sha256'],bytes=t['bytes'],historical_ext4_path=proof_source,historical_full_transfer_checked=True,current_ext4_availability='NOT_OBSERVED',availability='LOCAL_ONLY',complete_proof=False)
            need(row['ext4_trace_bytes']==ref['ext4_trace_bytes']==(trace['bytes']if trace else None),'known trace accounting; no unknown-as-zero assertion')
            text=(ROOT/r['stdout']).read_text(errors='replace');kind,statuses,conflicts=classify(text,r,trace['bytes']if trace else None);need(row['outcome']['interpretation']==ref['interpreted_result']==kind and row['outcome']['observed_conflicts']==conflicts and row['outcome']['native_status_lines']==statuses,'separate literal outcome classification')
            need(ref['actual_exit_code']==r['actual_exit_code']and ref['wrapped_wall_seconds']==r['wall_seconds']and ref['allocated_native_wall_seconds']==60,'receipt-derived attempt counters')
            rr=dict(case_id=cid,case_index=f['case_index'],subset_index=f['subset_index'],attempt_id=ref['attempt_id'],full_count_profile_sha256=f['full_count_profile_sha256'],run_summary_path=key(sp),run_summary_sha256=sha(sp),cnf_path=key(cnf),cnf_sha256=sha(cnf),scope_path=f['files']['scope.json']['path'],scope_sha256=f['files']['scope.json']['sha256'],trace=trace,native_receipt_path=key(main/'solver.receipt.json'),native_receipt_sha256=sha(main/'solver.receipt.json'),interpreted_native_result=kind)
            if kind=='UNSAT_TRACE_PENDING_COMPLETE_REPLAY':
                need(row['stop_reason']is None and trace is not None,'complete trace/normal native outcome');stats=parse_unsat(text,r,f['variables'],f['clauses']);need(stats['trace_bytes']==trace['bytes'],'complete native byte counter')
                for label,tx,r2 in [('header',text.replace(f"{f['variables']} {f['clauses']}",f"{f['variables']} {f['clauses']+1}"),r),('status',text.replace('s UNSATISFIABLE','s SATISFIABLE'),r),('duplicate_status',text+'s UNSATISFIABLE\n',r),('exit',text,{**r,'actual_exit_code':0}),('outer_guard',text,{**r,'outer_windows_guard_expired':True}),('allocation',text.replace("1000000 conflicts (due to '1000000')","1000000 conflicts (due to '2')"),r)]:
                    try:parse_unsat(tx,r2,f['variables'],f['clauses'])
                    except ValueError:attacks.append(dict(case_id=cid,kind=label))
                    else:raise ValueError('accepted mutated native receipt '+label)
                replay=helper.replay(f'case_{f["case_index"]:04d}_complete',cnf,proof,out,True);trace['complete_proof']=True;rr.update(outcome='UNSAT_VERIFIED',native_stats=stats,replay=replay);totals['UNSAT_VERIFIED']+=1
                # A complete research trace must not prove an empty-clause-set SAT input.
                if totals['UNSAT_VERIFIED']==1:
                    wrong=out/'wrong_empty_formula.cnf';wrong.write_text(f"p cnf {f['variables']} 0\n",encoding='ascii');controls.append(helper.replay('actual_proof_changed_SAT_input',wrong,proof,out,False))
            elif kind=='SAT_RAW_OBJECT_PENDING_REVIEW':rr['outcome']='SAT_PENDING_SEPARATE_RAW_OBJECT_REVIEW';totals['SAT_PENDING']+=1;need(row['stop_reason']is not None,'SAT pauses expansion')
            else:rr['outcome']='UNKNOWN';totals['UNKNOWN']+=1;need(row['stop_reason']is not None,'all nonconclusive outcomes stop')
            need(n==len(records)-1 or rr['outcome']=='UNSAT_VERIFIED','no further launch after SAT/UNKNOWN')
            used+=r['wall_seconds'];known_ext4+=trace['bytes']if trace else 0;checked.append(rr);save(out/f'case_{f["case_index"]:04d}.json',rr);print(json.dumps(dict(case_id=cid,outcome=rr['outcome'],checked=len(checked))),flush=True)
        need(used==final['wrapped_native_wall_seconds']and final['allocated_native_wall_seconds']==60*len(records)<=720 and known_ext4==final['known_ext4_trace_bytes'],'exact aggregate observed/allocated values')
        need(final['host_artifact_bytes_before_summary']+known_ext4==final['observed_artifact_bytes_before_summary']<=64*1024**3,'aggregate artifact accounting')
        old=read(OLD);same_old=[r for r in checked if r['cnf_sha256']=='6fecea814c533a081ee0292087b1bf4cccb9cb132ea232b907acd227ba610962'];need(len(same_old)<=1,'same literal pilot never counted twice within batch')
        repeated=dict(prior_gate_path=key(OLD),prior_gate_sha256=PINS[OLD],matching_case_ids=[r['case_id']for r in same_old],same_distinct_literal_case=True,new_proof_replayed=True if same_old and same_old[0]['outcome']=='UNSAT_VERIFIED'else None,additional_distinct_exclusions_beyond_prior_pilot=max(0,totals['UNSAT_VERIFIED']-sum(r['outcome']=='UNSAT_VERIFIED'for r in same_old)))
        all_unsat=len(checked)==12 and totals['UNSAT_VERIFIED']==12;stamp=datetime.now(timezone.utc).isoformat();limitations=['Only the explicitly replayed literal fixed-support count profiles are excluded. The792 coverage/fibre transports and whole-eight union remain separate.','Within-triplicate caps and full integer Gram; cross-triplicate caps and residualD are omitted.','The earlier a2a3... pilot is the same distinct literal case; this campaign replays its new trace and does not add it twice.','Same authenticated DRAT-trim/Windows shim/compiler/runtime and independent authentication/replay helper; no second prover or formal verification claim.','SAT and UNKNOWN are not exclusions. Current ext4 availability was not inspected or inferred.']
        if all_unsat:
            save(out/'claim_binding.json',dict(id=CID,revision=1,kind='exclusion',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',statement='Each of the twelve literal count-profile formulas in the independently authenticated first batch is UNSAT by complete independently replayed DRAT proof. Consequently no binary36x60 factor on the fixed six-prism Hadamard support has any of those literal count tables, full prescribed integer Gram and within-triplicate column caps.',scope=limitations[0],assumptions=['Exact fixed support and twelve complete literal initial domains; no target automorphism assumption.'],dependencies=[dict(id=eb['id'],revision=1,relation='encoding_equivalence')],verifier='/root/structural_attack',producer='/root/eight_domain_audit (formula/driver), /root (native execution)',method='Authenticate all exact inputs/receipts/tool sources and all complete host proof bytes, replay every DRAT proof, and reject positive/negative fixture and receipt corruptions.',shared_components=['Frozen independent balanced-proof authentication/replay helper and its exact DRAT-trim binary.','No producer or native Python imports; no solver calls.'],inputs_sha256=pins,case_records=checked,prior_literal_overlap=repeated,limitations=limitations,artifact_availability='LOCAL_ONLY',availability_reason='Public proof transport is separate.',created_at=stamp,updated_at=stamp))
        report=dict(status='INDEPENDENT_EXACT_EIGHT_FIRST12_LITERAL_PROOFS_PASS'if all_unsat else'INDEPENDENT_EXACT_EIGHT_FIRST12_OUTCOME_RECEIPT_AUDIT_PASS',timestamp=stamp,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],python=platform.python_version(),inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in out.rglob('*')if p.is_file()},selected_case_ids=selection,case_records=checked,completed_attempts=len(checked),completed_proof_replays=totals['UNSAT_VERIFIED'],SAT_pending=totals['SAT_PENDING'],UNKNOWN=totals['UNKNOWN'],pending_case_ids=final['pending_case_ids'],proof_bytes=sum(r['trace']['bytes']for r in checked if r['outcome']=='UNSAT_VERIFIED'),known_two_trace_copy_bytes=2*known_ext4,limits=LIMITS,wrapped_native_wall_seconds=used,recorded_end_to_end_wall_seconds=final['end_to_end_wall_seconds'],checker_provenance=provenance,controls=controls,native_receipt_corruptions_rejected=attacks,prior_literal_overlap=repeated,claim_id=CID if all_unsat else None,claim_id_null_reason=None if all_unsat else'No12-case exclusion without12 complete verified proofs.',limitations=limitations,new_solver_calls=0,target_resolution=False,elapsed_seconds=time.perf_counter()-start)
        save(out/'summary.json',report);print(json.dumps(dict(status=report['status'],summary_sha256=sha(out/'summary.json'))))
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),traceback=traceback.format_exc(),source_sha256=sha(Path(__file__)),inputs_sha256=pins));raise
if __name__=='__main__':main()
