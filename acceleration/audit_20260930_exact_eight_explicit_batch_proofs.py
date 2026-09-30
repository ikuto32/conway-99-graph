"""Complete explicit1..64 receipt, raw SAT object and DRAT review; no native search."""
import argparse,hashlib,importlib.util,json,platform,re,subprocess,sys,time,traceback
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results';I=B/'20260930_independent_review'
PRIOR=I/'hadamard_balanced_gram_unsat_v2/summary.json';HELPER=ROOT/'acceleration/audit_20260930_hadamard_balanced_gram_unsat_v2.py'
DOC=ROOT/'docs/AUDIT_20260930_EXACT_EIGHT_EXPLICIT_BATCH_PROOFS.md'
DRIVER=ROOT/'acceleration/native_20260930_exact_eight_explicit_batch.py';DRIVER_SPEC=ROOT/'acceleration/native_20260930_exact_eight_explicit_batch_spec.md'
OBJECT_SOURCE=ROOT/'acceleration/audit_20260930_exact_eight_explicit_batch_v2.py'
PINS={PRIOR:'edbbda720ea38ca5c565837bc39b5083eb145a64386c9e070fe89dfe5d6cebc5',DRIVER:'5362d31514a4e8bc0458c345f5324e776946b819cf7e5e89c09c20c3e1626169',DRIVER_SPEC:'0e152e160026497c405eab3f9a6596f4dc5b44bd89313e2fa7a6189974c4765d',OBJECT_SOURCE:'55787855b41863e007d7de8e7ea92ccc038caabb5dc1c6d0790f282804baed02'}
LIMITS=dict(native_wall_seconds_per_attempt=60,conflicts_per_attempt=1000000,address_space_bytes=4*1024**3,proof_file_bytes=256*1024**2,kill_grace_seconds=5,outer_guard_seconds=70,maximum_cases=64,allocation_rule='60 times selected case count',aggregate_retained_artifact_bytes=64*1024**3,next_attempt_artifact_reserve_bytes=1024**3,host_free_reserve_bytes=32*1024**3,ext4_free_reserve_bytes=2*1024**3,sequential=True,automatic_retry=False,automatic_resume=False)
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
    need((stats['conflicts']is None or 0<=stats['conflicts'])and 0<stats['trace_bytes']<=256*1024**2 and 0<=stats['native_wall_seconds']<60 and r['wall_seconds']<70,'complete bounded native result')
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
    ap=argparse.ArgumentParser()
    for name in ['campaign-summary','encoding-gate','object-gate']:ap.add_argument('--'+name,type=Path,required=True);ap.add_argument('--'+name+'-sha256',required=True)
    ap.add_argument('--claim-id');ap.add_argument('--out',type=Path,required=True);a=ap.parse_args()
    for value in [a.campaign_summary_sha256,a.encoding_gate_sha256,a.object_gate_sha256]:need(re.fullmatch('[0-9a-f]{64}',value),'explicit terminal/gate hash')
    RUN=a.campaign_summary.resolve().parent;ENC=a.encoding_gate.resolve();OBJ=a.object_gate.resolve()
    need(a.campaign_summary.resolve()==RUN/'summary.json','literal terminal summary filename')
    CID=a.claim_id or 'C-FIXED-HADAMARD-EXACT-EIGHT-EXPLICIT-'+a.campaign_summary_sha256[:16].upper()+'-LITERAL-EXCLUSIONS'
    need(CID.startswith('C-')and all(c.isupper()or c.isdigit()or c=='-'for c in CID),'safe literal claim label')
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
        provenance=helper.authenticate(pin);pin(ENC,a.encoding_gate_sha256);pin(OBJ,a.object_gate_sha256);enc=read(ENC);obj=read(OBJ)
        need(enc['status']=='INDEPENDENT_EXACT_EIGHT_EXPLICIT_BATCH_ENCODING_PASS'and obj['status']=='INDEPENDENT_EXACT_EIGHT_EXPLICIT_BATCH_OBJECT_CALIBRATION_PASS','exact prelaunch gates');need(obj['inputs_sha256'][key(ENC)]==a.encoding_gate_sha256,'same encoding gate')
        for report in [enc,obj]:
            for name,h in report['inputs_sha256'].items():pin(ROOT/name,h)
        ep=ENC.parent/'claim_binding.json';pin(ep,enc['outputs_sha256'][key(ep)]);eb=read(ep);need(eb['kind']=='encoding'and eb['status']=='VERIFIED'and eb['revision']==1 and eb['checked_cases']==enc['checked_cases'],'exact actual encoding binding')
        DATA=ROOT/enc['batch_summary_path'];SELECTION=ROOT/enc['selection_path'];pin(DATA,enc['batch_summary_sha256']);pin(SELECTION,enc['selection_sha256'])
        need(obj['batch_summary_path']==key(DATA)and obj['batch_summary_sha256']==enc['batch_summary_sha256']and obj['selection_path']==key(SELECTION)and obj['selection_sha256']==enc['selection_sha256'],'same calibrated selection/build')
        for p,h in PINS.items():need(obj['inputs_sha256'].get(key(p))==h if p in [DRIVER,DRIVER_SPEC,OBJECT_SOURCE]else True,'exact calibrated driver/checker pins')
        data=read(DATA);selection=data['selected_case_ids'];formula={r['case_id']:r for r in data['records']};approved={r['case_id']:r for r in enc['checked_cases']}
        N=len(selection);need(1<=N<=64 and selection==enc['selected_case_ids']==obj['selected_case_ids']==read(SELECTION)['ordered_case_ids']and N==len(set(selection))==len(approved)==enc['complete_formulas']==obj['complete_formulas'],'exact bounded distinct literal cases')
        need(data['completed_formulas']==N and data['pending_case_ids']==[]and data['native_calls']==0,'complete authenticated prepared formulas')
        final=read(RUN/'summary.json');manifest=read(RUN/'manifest.json')
        for p in RUN.rglob('*'):
            if p.is_file():pin(p)
        for name,h in manifest['inputs_sha256'].items():pin(ROOT/name,h)
        need(final['status']=='EXACT_EIGHT_EXPLICIT_BATCH_NATIVE_STOPPED'and manifest['mode']=='RESEARCH','completed source-bound research record')
        need(manifest['selection']==final['selected_case_ids']==selection,'exact selected list')
        if 'limits'in final:need(manifest['limits']==final['limits'],'same summary allocation')
        need(manifest['limits']==LIMITS and manifest['seed']==0 and manifest['seed_option']=='--seed=0'and manifest['automatic_resume']is False,'entire declared native allocation')
        need(final['inputs_sha256']==manifest['inputs_sha256']and final['manifest_path']==key(RUN/'manifest.json')and final['manifest_sha256']==sha(RUN/'manifest.json'),'exact immutable campaign inputs')
        need(manifest['build_consolidation_path']==key(DATA)and manifest['build_consolidation_sha256']==enc['batch_summary_sha256'],'exact reviewed build launched')
        need(manifest['explicit_selection_path']==final['explicit_selection_path']==key(SELECTION)and manifest['explicit_selection_sha256']==final['explicit_selection_sha256']==enc['selection_sha256'],'exact reviewed selection launched')
        need(manifest['selected_case_count']==final['selected_case_count']==N and manifest['allocated_native_wall_limit_seconds']==final['allocated_native_wall_limit_seconds']==60*N,'declared actual N-dependent allocation')
        need(manifest['inputs_sha256'].get(key(ENC))==a.encoding_gate_sha256 and manifest['inputs_sha256'].get(key(OBJ))==a.object_gate_sha256,'actual launch exact independent gates')
        options=manifest['command'][2:];need(len(options)%2==1 and options[0]=='--research','research command flag shape')
        parsed=dict(zip(options[1::2],options[2::2]));need(len(parsed)==len(options[1::2]),'unique research command options')
        expected_paths={'--out':RUN,'--selection':SELECTION,'--batch-summary':DATA,'--encoding-gate':ENC,'--object-gate':OBJ,'--object-checker':OBJECT_SOURCE}
        expected_values={'--selection-sha256':enc['selection_sha256'],'--batch-summary-sha256':enc['batch_summary_sha256'],'--encoding-gate-sha256':a.encoding_gate_sha256,'--object-gate-sha256':a.object_gate_sha256,'--attempt-id':manifest['attempt_id']}
        need(set(parsed)==set(expected_paths)|set(expected_values)and all((ROOT/parsed[k]).resolve()==v.resolve()for k,v in expected_paths.items())and all(parsed[k]==v for k,v in expected_values.items()),'complete exact research driver invocation')
        need((ROOT/manifest['command'][1]).resolve()==DRIVER and manifest['cwd']==str(ROOT),'actual pinned native driver/workspace')
        for name in ['filesystem','disk_free']:
            observed=read(RUN/'initial_resources'/(name+'.receipt.json'));receipt(observed,0)
            if name=='filesystem':need('ext4'in(ROOT/observed['stdout']).read_text().split(),'initial observed ext4 mount')
            else:need(int((ROOT/observed['stdout']).read_text().split()[-1])>=2*1024**3,'initial ext4 reserve')
        records=final['case_records'];need([r['case_id']for r in records]==selection[:len(records)]and final['pending_case_ids']==selection[len(records):]and final['completed_attempts']==final['native_calls']==len(records),'attempted prefix and unattempted suffix')
        need(len(records)<=N and final['automatic_retry']is False and final['automatic_resume']is False and final['independent_approval']is False and final['target_resolution']is False,'no hidden retries or promoted producer outcome')
        if final['stop_reason']=='ALL_EXPLICITLY_SELECTED_CASES_ATTEMPTED':need(len(records)==N and all(r['interpreted_result']=='UNSAT_TRACE_PENDING_COMPLETE_REPLAY'for r in records),'honest completed campaign boundary')
        restart=read(RUN/'restart_requirements.json');need(restart['automatic_resume']is False and restart['pending_case_ids']==final['pending_case_ids']and restart['completed_attempts']==records and restart['mathematical_exclusions_asserted']==0,'honest restart prerequisites')
        for index,ref in enumerate(records,1):
            checkpoint=read(RUN/f'checkpoint_{index:02d}.json');need(checkpoint['case_records']==records[:index]and checkpoint['pending_case_ids']==selection[index:]and checkpoint['inputs_sha256']==manifest['inputs_sha256'],'each exact immutable attempt checkpoint')
        fixtures={'tiny_unsat.cnf':b'p cnf 2 4\n1 2 0\n1 -2 0\n-1 2 0\n-1 -2 0\n','tiny_sat.cnf':b'p cnf 2 3\n1 2 0\n1 -2 0\n-1 2 0\n','tiny_valid.drat':b'-2 0\n1 0\n0\n','empty_only.drat':b'0\n','fresh_unit.drat':b'3 0\n0\n'}
        for name,contents in fixtures.items():(out/name).write_bytes(contents)
        tiny=[(1,2),(1,-2),(-1,2),(-1,-2)];oracle=lambda cs:[bits for bits in range(4)if all(any(bool(bits&(1<<(abs(v)-1)))==(v>0)for v in c)for c in cs)];need(oracle(tiny)==[]and oracle(tiny[:-1])==[3],'complete tiny truth controls')
        tests=[('positive_reasoning','tiny_unsat.cnf','tiny_valid.drat',True),('missing_reasoning','tiny_unsat.cnf','empty_only.drat',False),('fresh_unit','tiny_unsat.cnf','fresh_unit.drat',False),('changed_SAT_input','tiny_sat.cnf','tiny_valid.drat',False)]
        controls=[helper.replay(name,out/cnf,out/proof,out,wanted)for name,cnf,proof,wanted in tests];checked=[];totals=Counter();attacks=[];used=0.;known_ext4=0
        classifications=[]
        for code,text,n,guard,expected in [(124,'',None,False,'UNKNOWN_WALL_LIMIT'),(153,'',256*1024**2,False,'UNKNOWN_FILE_LIMIT_OR_FULL_TRACE_CAP'),(20,'s UNSATISFIABLE\ns SATISFIABLE\n',10,False,'UNKNOWN_NATIVE_STATUS_OR_RESOURCE_OUTCOME'),(20,'s UNSATISFIABLE\n',10,False,'UNSAT_TRACE_PENDING_COMPLETE_REPLAY'),(20,'s UNSATISFIABLE\n',None,False,'UNSAT_TRACE_UNAVAILABLE_UNKNOWN'),(10,'s SATISFIABLE\n',0,False,'SAT_RAW_OBJECT_PENDING_REVIEW'),(0,'c conflicts: 1000002\n',None,False,'UNKNOWN_CONFLICT_LIMIT'),(20,'s UNSATISFIABLE\n',10,True,'OUTER_GUARD_PROCESS_STATE_UNKNOWN')]:
            got=classify(text,dict(actual_exit_code=code,outer_windows_guard_expired=guard),n)[0];need(got==expected,'independent terminal classification control');classifications.append(dict(code=code,stdout=text,trace_bytes=n,outer_guard=guard,expected=expected,observed=got))
        save(out/'outcome_classification_controls.json',classifications)
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
            need(re.fullmatch(f'/tmp/conway99-exact-eight-{f["case_index"]:04d}-[A-Za-z0-9]+',workspace['path'])and(ROOT/workspace['receipt']['stdout']).read_text().strip()==workspace['path'],'literal fresh workspace creation receipt')
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
            need(row['outcome']['actual_exit_code']==r['actual_exit_code']and row['outcome']['configured_conflict_limit']==1000000 and row['outcome']['configured_wall_limit']==60 and row['outcome']['configured_file_limit']==256*1024**2 and row['outcome']['mathematical_approval']is False,'exact configured versus observed boundary')
            need(sum((ROOT/name).stat().st_size for name in row['outputs_sha256'])==row['host_artifact_bytes_before_summary'],'entire saved per-case host accounting')
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
            elif kind=='SAT_RAW_OBJECT_PENDING_REVIEW':
                need(row['stop_reason']is not None,'SAT pauses expansion');import audit_20260930_exact_eight_explicit_batch_v2 as object_checker
                pin(Path(object_checker.__file__),PINS[OBJECT_SOURCE])
                profile=read(ROOT/f['files']['selected_profile.json']['path']);model=read(ROOT/f['files']['model.json']['path']);raw=read(object_checker.prior.RAW)
                rebuilt=object_checker.core.verify_formula(raw,profile,scope,model,f['files']['scope.json']['sha256'],cnf.read_bytes())
                assignment=main/'parsed_model.json';pin(assignment);values=object_checker.codec.assignment(read(assignment)['assignment'],model['variables']);need(values==object_checker.codec.native(text,model['variables']),'complete independent raw SAT assignment/native equality')
                result=object_checker.core.decode_and_verify(values,model,scope,profile,rebuilt['clauses']);factor=object_checker.prior.native_decode_shape(result,model,scope,profile);factor['model_sha256']=f['files']['model.json']['sha256'];factor['scope_sha256']=f['files']['scope.json']['sha256']
                decoded=main/'decoded_Gram_factor.json'
                if decoded.is_file():need(object_checker.same(factor,read(decoded)),'entire optional candidate factor independently checked')
                factorpath=out/f'case_{f["case_index"]:04d}_independent_Gram_factor.json';save(factorpath,factor);rr.update(outcome='SAT_GRAM_FACTOR_VERIFIED',independent_factor_path=key(factorpath),independent_factor_sha256=sha(factorpath),cross_caps_diagnostic_only=True,residual_D=None);totals['SAT_VERIFIED']+=1
            else:rr['outcome']='UNKNOWN';totals['UNKNOWN']+=1;need(row['stop_reason']is not None,'all nonconclusive outcomes stop')
            need(n==len(records)-1 or rr['outcome']=='UNSAT_VERIFIED','no further launch after SAT/UNKNOWN')
            used+=r['wall_seconds'];known_ext4+=trace['bytes']if trace else 0;checked.append(rr);save(out/f'case_{f["case_index"]:04d}.json',rr);print(json.dumps(dict(case_id=cid,outcome=rr['outcome'],checked=len(checked))),flush=True)
        need(used==final['wrapped_native_wall_seconds']and final['allocated_native_wall_seconds']==60*len(records)<=60*N and known_ext4==final['known_ext4_trace_bytes'],'exact aggregate observed/allocated values')
        need(final['host_artifact_bytes_before_summary']+known_ext4==final['observed_artifact_bytes_before_summary']<=64*1024**3,'aggregate artifact accounting')
        need(sum(p.stat().st_size for p in RUN.rglob('*')if p.is_file()and p not in [RUN/'summary.json',RUN/'restart_requirements.json'])==final['host_artifact_bytes_before_summary'],'exact host byte accounting before terminal metadata')
        skipped=enc['skipped_verified_case_ids'];need(set(selection).isdisjoint(skipped)and len(skipped)==len(set(skipped)),'new explicit attempts do not count verified skips')
        repeated=dict(prior_skip_authentication_gate_path=key(ENC),prior_skip_authentication_gate_sha256=a.encoding_gate_sha256,skipped_verified_case_ids=skipped,overlap_with_skipped_cases=[],distinct_cases_this_batch=len(checked),scope='No union with earlier historical literal/orbit claims is asserted here.')
        all_unsat=len(checked)==N and totals['UNSAT_VERIFIED']==N;stamp=datetime.now(timezone.utc).isoformat();limitations=['Only the explicitly replayed literal fixed-support count profiles are excluded. The792 coverage/fibre transports and whole-eight union remain separate.','Within-triplicate caps and full integer Gram; cross-triplicate caps and residualD are omitted.','Previously proved skipped cases are never counted as new attempts here. Other historical-profile overlaps require a separate union review.','Same authenticated DRAT-trim/Windows shim/compiler/runtime and independent authentication/replay helper; no second prover or formal verification claim.','SAT factors are independently validated but supply no residualD; UNKNOWN gives no exclusion. Current ext4 availability was not inspected or inferred.']
        if all_unsat:
            save(out/'claim_binding.json',dict(id=CID,revision=1,kind='exclusion',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',statement=f'Each of the exact {N} literal count-profile formulas in this independently authenticated explicit batch is UNSAT by complete independently replayed DRAT proof. Consequently no binary36x60 factor on the fixed six-prism Hadamard support has any of those literal count tables, full prescribed integer Gram and within-triplicate column caps.',scope=limitations[0],assumptions=['Exact fixed support and the explicitly enumerated complete literal initial domains; no target automorphism assumption.'],dependencies=[dict(id=eb['id'],revision=1,relation='encoding_equivalence')],verifier='/root/structural_attack',producer='/root/eight_domain_audit (formula/driver), /root (native execution)',method='Authenticate all exact inputs/receipts/tool sources and all complete host proof bytes, replay every DRAT proof, and reject positive/negative fixture and receipt corruptions.',shared_components=['Fresh parameterization of the previously checked first12/next32 complete-proof auditors; frozen independent balanced-proof authentication/replay helper and exact DRAT-trim binary.','SAT uses the separately calibrated independent explicit-batch raw-clause/factor checker. No producer or native Python imports; no solver calls.'],inputs_sha256=pins,case_records=checked,prior_literal_overlap=repeated,limitations=limitations,artifact_availability='LOCAL_ONLY',availability_reason='Public proof transport is separate.',created_at=stamp,updated_at=stamp))
        report=dict(status='INDEPENDENT_EXACT_EIGHT_EXPLICIT_BATCH_LITERAL_PROOFS_PASS'if all_unsat else'INDEPENDENT_EXACT_EIGHT_EXPLICIT_BATCH_OUTCOME_RECEIPT_AUDIT_PASS',timestamp=stamp,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],python=platform.python_version(),inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in out.rglob('*')if p.is_file()},selection_path=key(SELECTION),selection_sha256=enc['selection_sha256'],batch_summary_path=key(DATA),batch_summary_sha256=enc['batch_summary_sha256'],encoding_gate_path=key(ENC),encoding_gate_sha256=a.encoding_gate_sha256,object_gate_path=key(OBJ),object_gate_sha256=a.object_gate_sha256,selected_case_ids=selection,case_records=checked,completed_attempts=len(checked),completed_proof_replays=totals['UNSAT_VERIFIED'],SAT_verified=totals['SAT_VERIFIED'],UNKNOWN=totals['UNKNOWN'],pending_case_ids=final['pending_case_ids'],proof_bytes=sum(r['trace']['bytes']for r in checked if r['outcome']=='UNSAT_VERIFIED'),known_two_trace_copy_bytes=2*known_ext4,limits=LIMITS,wrapped_native_wall_seconds=used,recorded_end_to_end_wall_seconds=final['end_to_end_wall_seconds'],checker_provenance=provenance,controls=controls,native_receipt_corruptions_rejected=attacks,prior_literal_overlap=repeated,claim_id=CID if all_unsat else None,claim_id_null_reason=None if all_unsat else'No entire selected-batch exclusion without complete verified proofs for every selected case.',limitations=limitations,new_solver_calls=0,target_resolution=False,elapsed_seconds=time.perf_counter()-start)
        save(out/'summary.json',report);print(json.dumps(dict(status=report['status'],summary_sha256=sha(out/'summary.json'))))
    except BaseException as error:save(out/'failure.json',dict(error=repr(error),traceback=traceback.format_exc(),source_sha256=sha(Path(__file__)),inputs_sha256=pins));raise
if __name__=='__main__':main()
