"""Independent complete proof collection review; no producer or solver imports."""
import argparse,hashlib,importlib.util,json,platform,re,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results'
RUN=B/'20260930_hadamard_four_profile_native_campaign';D=B/'20260930_hadamard_four_profile_cnfs'
ENC=B/'20260930_independent_review/hadamard_fifteen_profile_cnfs/summary.json'
OBJ=B/'20260930_independent_review/hadamard_fifteen_profile_object_calibration/summary.json'
PRIOR=B/'20260930_independent_review/hadamard_balanced_gram_unsat_v2/summary.json'
HELPER=ROOT/'acceleration/audit_20260930_hadamard_balanced_gram_unsat_v2.py'
CASES=[6,12,18,24,30,36,42,48,51,72,78,84,90,96,102]
PINS={RUN/'summary.json':'1b735246ecd4ca2e5d3512d356b3c8130c67db74bfb0911dd6fa54e4f87a8b1f',RUN/'manifest.json':'c0b8a542a042ed8029988468702bab559097cc53cf7e81cbdad7a75cebd8f9b5',RUN/'campaign_manifest.json':'ab7e5c13b027425b9b616b3050330131e7e32094beefda61ec57361d79fab75d',ENC:'8566b0ab977d4918a51708e3f6390ef276483bc6a7b55722c59c4b2825c4f88b',OBJ:'57678825066d0e448de1b80824c3b84ea75e28d811bfa2d92b6bf90d7f89deb0',PRIOR:'edbbda720ea38ca5c565837bc39b5083eb145a64386c9e070fe89dfe5d6cebc5'}
def need(x,m):
    if not x:raise ValueError(m)
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(p.read_bytes())
def save(p,v):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,indent=2);f.write('\n')
def parse(text,r):
    need([l for l in text.splitlines() if l.startswith('s ')]==['s UNSATISFIABLE'],'sole UNSAT status')
    need(text.splitlines().count("c found 'p cnf 10564 187408' header")==1,'literal dimensions')
    need(text.splitlines().count('c exit 20')==1 and r['actual_exit_code']==20 and r['outer_windows_guard_expired'] is False,'normal UNSAT exit20')
    need('c Version 1.9.5 146207318796f094dcded87349a64f0c6927309e' in text,'actual solver version')
    need("c setting conflict limit to 1000000 conflicts (due to '1000000')" in text,'configured conflict budget')
    def one(pattern,typ):
        v=re.findall(pattern,text,re.M);need(len(v)==1,'unique statistic');return typ(v[0])
    s=dict(conflicts=one(r'^c conflicts:\s+(\d+)\s',int),native_cpu_seconds=one(r'^c total process time since initialization:\s+([0-9.]+)\s+seconds$',float),native_wall_seconds=one(r'^c total real time since initialization:\s+([0-9.]+)\s+seconds$',float),trace_bytes=one(r'^c DRAT (\d+) bytes ',int),wrapper_wall_seconds=r['wall_seconds'])
    need(0<s['conflicts']<=1000000 and 0<s['trace_bytes']<=10737418240 and 0<=s['native_wall_seconds']<60 and s['wrapper_wall_seconds']<70,'bounded complete result')
    return s
def command_check(cmd,cnf,linuxproof):
    prefix=['wsl.exe','--distribution','Ubuntu-24.04','--exec','/usr/bin/timeout','--signal=TERM','--kill-after=5s','60s','/usr/bin/prlimit','--as=4294967296:4294967296','--fsize=10737418240:10737418240','--core=0:0']
    need(cmd[:12]==prefix and len(cmd)==18,'literal guarded command')
    need(cmd[12].endswith('/build/research-cadical195/source/build/cadical') and cmd[13:16]==['--no-binary','-c','1000000'],'solver and options')
    need(cmd[16].endswith('/'+key(cnf)) and cmd[17]==linuxproof,'exact input and proof paths')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};start=time.perf_counter()
    def pin(p,h=None):
        p=p.resolve();k=key(p)
        if k not in pins:pins[k]=sha(p)
        need(h is None or pins[k]==h,'identity '+k)
        return pins[k]
    def receipt(r,exitcode=None):
        need(r['outer_windows_guard_expired'] is False,'receipt outer timeout')
        if exitcode is not None:need(r['actual_exit_code']==exitcode,'receipt exit')
        for c in ['stdout','stderr']:pin(ROOT/r[c],r[c+'_sha256'])
    try:
        for p,h in PINS.items():pin(p,h)
        pin(ROOT/'acceleration/audit_20260930_hadamard_fifteen_profile_unsat.py','2636a3a5ea4d0eaaeeb544555dae58c562093a64c1d16d97da40b1f17802bb3b')
        pin(ROOT/'acceleration/results/20260930_independent_review/hadamard_fifteen_profile_unsat/failure.json','08584bb426db4b3077d57384280905bb4b1114839fd2f7925dc1b36a57d77f09')
        pin(HELPER,read(PRIOR)['inputs_sha256'][key(HELPER)])
        spec=importlib.util.spec_from_file_location('independent_drat_helper',HELPER);helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
        for p in [helper.BUILD/'drat-trim.exe',helper.BUILD/'build_manifest.json',helper.BUILD/'build_receipt.json']:pin(p,helper.PINS[p])
        provenance=helper.authenticate(pin)
        enc,obj=read(ENC),read(OBJ)
        need(enc['status']=='INDEPENDENT_HADAMARD_FIFTEEN_PROFILE_ENCODING_PASS' and enc['checked_cases']==CASES and enc['formulas_checked']==15 and enc['variables_per_formula']==10564 and enc['clauses_per_formula']==187408,'complete independent encoding')
        need(obj['status']=='INDEPENDENT_HADAMARD_FIFTEEN_PROFILE_OBJECT_CALIBRATION_PASS','prelaunch object gate')
        for g in [enc,obj]:
            for p,h in g['inputs_sha256'].items():pin(ROOT/p,h)
        ebp=ENC.parent/'claim_binding.json';pin(ebp,enc['outputs_sha256'][key(ebp)]);eb=read(ebp)
        need(eb['id']=='C-FIXED-HADAMARD-FIFTEEN-FOUR-EXCEPTION-GRAM-ENCODINGS' and eb['revision']==1,'encoding claim revision')
        final,m,cm=read(RUN/'summary.json'),read(RUN/'manifest.json'),read(RUN/'campaign_manifest.json')
        for p,h in m['inputs_sha256'].items():pin(ROOT/p,h)
        for p in RUN.iterdir():
            if p.is_file():pin(p)
        need(final['selected_cases']==cm['selection']==CASES and [r['case'] for r in final['case_records']]==CASES,'exact selected population')
        need(final['completed_attempts']==15 and final['unattempted_cases']==[] and final['stop_reason']=='ALL_SELECTED_CASES_ATTEMPTED' and final['automatic_retry'] is False,'complete final outcome')
        need(m['mode']=='RESEARCH' and m['resume_checkpoint'] is None and m['automatic_retry'] is False and m['limits']==cm['limits'],'fresh bounded campaign')
        limits=m['limits'];need(limits['native_wall_seconds_per_case']==60 and limits['conflicts_per_case']==1000000 and limits['campaign_wrapped_wall_seconds']==900 and limits['maximum_cases']==15,'declared allocation')
        progress=[json.loads(l) for l in (RUN/'progress.jsonl').read_text().splitlines()];need(progress==final['case_records'],'all progress records exact')
        for n,case in enumerate([None]+CASES):
            cp=read(RUN/('checkpoint_initial.json' if case is None else f'checkpoint_case_{case:03d}.json'))
            need(cp['selected_cases']==CASES and cp['case_records']==final['case_records'][:n] and cp['inputs_sha256']==m['inputs_sha256'],'immutable checkpoint prefix')
        fixtures={'tiny_unsat.cnf':b'p cnf 2 4\n1 2 0\n1 -2 0\n-1 2 0\n-1 -2 0\n','tiny_sat.cnf':b'p cnf 2 3\n1 2 0\n1 -2 0\n-1 2 0\n','tiny_valid.drat':b'-2 0\n1 0\n0\n','empty_only.drat':b'0\n','fresh_unit.drat':b'3 0\n0\n'}
        for name,data in fixtures.items():(out/name).write_bytes(data)
        tiny=[(1,2),(1,-2),(-1,2),(-1,-2)];oracle=lambda cs:[b for b in range(4) if all(any(bool(b&(1<<(abs(v)-1)))==(v>0) for v in c) for c in cs)]
        need(oracle(tiny)==[] and oracle(tiny[:-1])==[3],'tiny truth-table calibration')
        controls=[helper.replay(n,out/c,out/p,out,e) for n,c,p,e in [('positive_reasoning','tiny_unsat.cnf','tiny_valid.drat',True),('missing_reasoning','tiny_unsat.cnf','empty_only.drat',False),('unsupported_unit','tiny_unsat.cnf','fresh_unit.drat',False),('changed_SAT_input','tiny_sat.cnf','tiny_valid.drat',False)]]
        records=[];corruptions=[]
        for pos,ref in enumerate(final['case_records']):
            case=ref['case'];rp=ROOT/ref['summary_path'];pin(rp,ref['summary_sha256']);s=read(rp);folder=rp.parent;cnf=D/f'case_{case:03d}'/'instance.cnf';model=cnf.with_name('model.json');scope=cnf.with_name('scope.json');rawscope=read(scope)
            need(s['case']==rawscope['selected_case']==case and s['research_calls']==1 and s['stop_reason'] is None and s['interpreted_result']==ref['interpreted_result']=='UNSAT_COMPLETE_TRACE_UNCHECKED','literal completed case')
            need(s['inputs_sha256']==m['inputs_sha256'],'frozen per-case inputs')
            for p,h in s['outputs_sha256'].items():pin(ROOT/p,h)
            for p,n in [(cnf,'cnf'),(model,'model'),(scope,'scope')]:pin(p,s[n+'_sha256']);need(enc['inputs_sha256'][key(p)]==s[n+'_sha256'],'exact encoding match')
            need(rawscope['within_group_column_caps_encoded'] and not rawscope['cross_group_column_caps_encoded'] and not rawscope['residual_D_encoded'],'recorded conditional scope')
            r=read(folder/'main/solver.receipt.json');launch=read(folder/'main/launch.json');t=s['proof_copy'];proof=folder/'main/proof.drat'
            need(r==s['native_receipt'] and launch['command']==r['command'] and launch['cnf_sha256']==s['cnf_sha256'],'native receipt and launch')
            command_check(r['command'],cnf,t['linux_source']);need(r['outer_windows_guard_seconds']==70,'outer guard')
            receipt(r,20);text=(ROOT/r['stdout']).read_text();stats=parse(text,r)
            need(stats['trace_bytes']==proof.stat().st_size==t['bytes'] and s['retained_raw_trace_bytes']==ref['retained_raw_trace_bytes']==2*t['bytes'],'proof byte inventories')
            pin(proof,t['sha256']);receipt(t['native_hash_receipt'],0);receipt(t['copy_receipt'],0)
            need(t['native_hash_receipt']['command'][-2:]==['/usr/bin/sha256sum',t['linux_source']] and t['copy_receipt']['command'][-4:-1]==['/usr/bin/cp','--',t['linux_source']] and t['copy_receipt']['command'][-1].endswith('/'+key(proof)),'immediate exact trace transport')
            need((ROOT/t['native_hash_receipt']['stdout']).read_text().split()==[t['sha256'],t['linux_source']],'native and host whole-trace identity')
            resource=s['resource_check'];need(resource['host_free_bytes']>=limits['host_free_reserve_bytes'] and resource['ext4_free_bytes']>=limits['ext4_free_reserve_bytes'],'prelaunch reserves')
            for field in ['mount_receipt','disk_receipt']:receipt(resource[field],0)
            need('ext4' in (ROOT/resource['mount_receipt']['stdout']).read_text().split(),'actual ext4 proof location')
            need(int((ROOT/resource['disk_receipt']['stdout']).read_text().split()[-1])==resource['ext4_free_bytes'],'disk reading')
            for phase in ['processes_before','processes_after']:
                pr=s[phase];receipt(pr);need(pr['actual_exit_code'] in (0,1) and pr['command'][4:]==['/usr/bin/ps','-C','cadical','-o','pid,ppid,comm,pcpu,rss,args'],'targeted saved observation')
                need('/'+key(cnf) not in (ROOT/pr['stdout']).read_text(),'no surviving exact-input process in saved observation')
            need(ref['wrapped_wall_seconds']==r['wall_seconds'],'case wall counter')
            for name,bad,rr in [('header',text.replace('10564 187408','10564 187409'),r),('status',text.replace('s UNSATISFIABLE','s SATISFIABLE'),r),('duplicate',text+'s UNSATISFIABLE\n',r),('exit',text,{**r,'actual_exit_code':0}),('timeout',text,{**r,'outer_windows_guard_expired':True}),('allocation',text.replace("1000000 conflicts (due to '1000000')","1000000 conflicts (due to '2')"),r)]:
                try:parse(bad,rr)
                except ValueError:corruptions.append(dict(case=case,kind=name))
                else:raise ValueError('accepted native corruption')
            controls.append(helper.replay(f'case_{case:03d}_empty_only',cnf,out/'empty_only.drat',out,False))
            replay=helper.replay(f'case_{case:03d}_complete',cnf,proof,out,True)
            record=dict(case=case,cnf_path=key(cnf),cnf_sha256=sha(cnf),model_path=key(model),model_sha256=s['model_sha256'],scope_path=key(scope),scope_sha256=s['scope_sha256'],literal_profile={k:rawscope[k] for k in ['exceptional_groups','common_support','circuit_relation','deviation_profile','balanced_groups']},proof=dict(path=key(proof),sha256=t['sha256'],bytes=t['bytes'],complete_independent_replay=True,availability='LOCAL_ONLY',availability_reason='Raw local proof awaits publication; identity alone is not public retrieval.'),replay=replay,native_stats=stats,native_receipt_path=key(folder/'main/solver.receipt.json'),native_receipt_sha256=sha(folder/'main/solver.receipt.json'),run_summary_path=key(rp),run_summary_sha256=ref['summary_sha256'])
            records.append(record);save(out/f'case_{case:03d}.json',record)
        need(sum(r['native_stats']['wrapper_wall_seconds'] for r in records)==final['wrapped_solver_wall_seconds']<900,'aggregate solver time')
        total=sum(r['proof']['bytes'] for r in records);need(2*total==final['retained_raw_trace_bytes_known']==299143844,'whole final trace counts')
        # No global process argument inventory: exact executable name only.
        cmd=['wsl.exe','--distribution','Ubuntu-24.04','--exec','/usr/bin/ps','-C','cadical','-o','pid,ppid,comm,pcpu,rss,args'];p=subprocess.run(cmd,cwd=ROOT,capture_output=True,text=True,timeout=10)
        need(p.returncode in (0,1) and (p.returncode!=1 or len(p.stdout.splitlines())<=1),'fresh targeted observation')
        (out/'process.stdout.log').write_text(p.stdout,encoding='utf-8');(out/'process.stderr.log').write_text(p.stderr,encoding='utf-8')
        observation=dict(timestamp=datetime.now(timezone.utc).isoformat(),command=cmd,exit_code=p.returncode,stdout_sha256=sha(out/'process.stdout.log'),stderr_sha256=sha(out/'process.stderr.log'),exact_campaign_processes=[l for l in p.stdout.splitlines() if '/'+key(D)+'/' in l]);save(out/'process_observation.json',observation)
        pin(Path(__file__));pin(ROOT/'docs/AUDIT_20260930_HADAMARD_FIFTEEN_PROFILE_UNSAT.md');ts=datetime.now(timezone.utc).isoformat()
        limitations=['Exactly the15 literal profiles listed; fibre-orbit transfer and complete profile coverage require a separate audit.','Fixed six-prism Hadamard support and within-group column caps; no whole-support, core or unrestricted-target exclusion.','Cross-group column caps and residualD are omitted from these UNSAT formulas.','Trusted DRAT-trim, reviewed Windows shim, compiler and runtime; no formal or diverse-checker claim. Solver correctness is not a premise.']
        statement='For each literal case in '+str(CASES)+', no binary36x60factor on the pinned six-prism Hadamard support realizes its prescribed count profile, full integer Gram and within-group column caps. Each of the15 independently checked10564-variable187408-clause encodings is UNSAT by complete exact DRAT replay.'
        binding=dict(id='C-FIXED-HADAMARD-FIFTEEN-FOUR-EXCEPTION-EXCLUSIONS',revision=1,kind='exclusion',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',statement=statement,scope=limitations[0],assumptions=['Pinned fixed support and all15 literal scope files.','Within-group column caps; no target automorphism assumption.'],dependencies=[dict(id=eb['id'],revision=1,relation='encoding_equivalence')],verifier='/root/structural_attack',producer='/root',method='Complete independent DRAT replay for every exact formula, authenticated checker and positive/corrupt proof controls, native receipts and campaign prefix binding.',shared_components=['Frozen independently authored balanced-proof authentication/replay helper reused, with same source-authenticated DRAT-trim build.','No producer Python imported; compiler/runtime and DRAT-trim implementation remain trusted.'],inputs_sha256=pins,evidence_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},case_records=records,limitations=limitations,artifact_availability='LOCAL_ONLY',availability_reason='Awaiting parent publication and any packaging required for larger complete traces.',external_review=None,external_review_reason='No external peer review asserted.',created_at=ts,updated_at=ts)
        save(out/'claim_binding.json',binding)
        report=dict(status='INDEPENDENT_FIXED_HADAMARD_FIFTEEN_PROFILE_UNSAT_PASS',timestamp=ts,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,outputs_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},case_records=records,checked_cases=CASES,completed_proof_replays=15,SAT=0,UNKNOWN=0,proof_bytes=total,retained_two_copy_bytes=2*total,checker_provenance=provenance,controls=controls,native_receipt_corruptions_rejected=corruptions,configured_limits=limits,run_source_commit=m['source_commit'],run_command=m['command'],wrapped_solver_wall_seconds=final['wrapped_solver_wall_seconds'],recorded_end_to_end_wall_seconds=final['end_to_end_wall_seconds'],process_observation=observation,claim_id=binding['id'],claim_revision=1,statement=statement,limitations=limitations,new_solver_calls=0,target_resolution=False,elapsed_seconds=time.perf_counter()-start)
        save(out/'summary.json',report);print(json.dumps(dict(status=report['status'],summary_sha256=sha(out/'summary.json'),claim_binding_sha256=sha(out/'claim_binding.json'))))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e)));raise
if __name__=='__main__':main()
