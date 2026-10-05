"""Complete independent proof/receipt review. No producer or solver imports."""
import argparse, hashlib, importlib.util, json, platform, re, subprocess, sys, time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; B=ROOT/'acceleration/results'
RUN=B/'20260930_hadamard_six_profile_batch_campaign'
DATA=B/'20260930_hadamard_six_remaining_cnfs/run01'
ENC=B/'20260930_independent_review/hadamard_fiftyfour_profile_cnfs/summary.json'
OBJ=B/'20260930_independent_review/hadamard_fiftyfour_profile_object_calibration/summary.json'
PRIOR=B/'20260930_independent_review/hadamard_balanced_gram_unsat_v2/summary.json'
HELPER=ROOT/'acceleration/audit_20260930_hadamard_balanced_gram_unsat_v2.py'
PLAN=ROOT/'docs/AUDIT_20260930_HADAMARD_FIFTYFOUR_PROFILE_PROOFS.md'
CID='C-FIXED-HADAMARD-FIFTYFOUR-SIX-EXCEPTION-PROFILE-EXCLUSIONS'
PINS={ENC:'4fa50584776c9862e4e4c0286567b212b9a436c13a6cf0ebf0cd0b0ad751a6e5',OBJ:'15c0c12deb3c56e685650abb408717c30036d927c534d626a135a3310acec2c9',PRIOR:'edbbda720ea38ca5c565837bc39b5083eb145a64386c9e070fe89dfe5d6cebc5',DATA/'summary.json':'a52427bce883858f43187d3916d172ac656afb6f6f60a7e0835ca5e8cb11be47',ROOT/'acceleration/native_20260930_hadamard_six_profile_batch.py':'cf1ca91b527a7422668085fc1acf75dae259f7b460a2f6eea95ee5bd5e2bbd0b'}

def need(ok,msg):
    if not ok: raise ValueError(msg)
def sha(path):
    with path.open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def key(path):return path.resolve().relative_to(ROOT).as_posix()
def read(path):return json.loads(path.read_bytes())
def save(path,obj):
    with path.open('x',encoding='utf8',newline='\n') as stream:json.dump(obj,stream,indent=2);stream.write('\n')

def parse_unsat(text,receipt,variables,clauses):
    lines=text.splitlines()
    need([line for line in lines if line.startswith('s ')]==['s UNSATISFIABLE'],'unique UNSAT status')
    need(lines.count(f"c found 'p cnf {variables} {clauses}' header")==1,'exact formula dimensions')
    need(lines.count('c exit 20')==1 and receipt['actual_exit_code']==20 and receipt['outer_windows_guard_expired'] is False,'normal UNSAT exit20')
    need('c Version 1.9.5 146207318796f094dcded87349a64f0c6927309e' in text,'solver version')
    need("c setting conflict limit to 1000000 conflicts (due to '1000000')" in lines,'configured conflict limit')
    def one(pattern,kind):
        matches=re.findall(pattern,text,re.M);need(len(matches)==1,'unique native statistic');return kind(matches[0])
    result=dict(conflicts=one(r'^c conflicts:\s+(\d+)\s',int),native_cpu_seconds=one(r'^c total process time since initialization:\s+([0-9.]+)\s+seconds$',float),native_wall_seconds=one(r'^c total real time since initialization:\s+([0-9.]+)\s+seconds$',float),trace_bytes=one(r'^c DRAT (\d+) bytes ',int),wrapper_wall_seconds=receipt['wall_seconds'])
    need(0<result['conflicts']<=1000000 and 0<result['trace_bytes']<=10737418240 and 0<=result['native_wall_seconds']<60 and result['wrapper_wall_seconds']<70,'bounded UNSAT receipt')
    return result

def command_check(command,cnf,proof):
    prefix=['wsl.exe','--distribution','Ubuntu-24.04','--exec','/usr/bin/timeout','--signal=TERM','--kill-after=5s','60s','/usr/bin/prlimit','--as=4294967296:4294967296','--fsize=10737418240:10737418240','--core=0:0']
    need(command[:12]==prefix and len(command)==18,'literal guarded solver command')
    need(command[12].endswith('/build/research-cadical195/source/build/cadical') and command[13:16]==['--no-binary','-c','1000000'],'native binary/options')
    need(command[16].endswith('/'+key(cnf)) and command[17]==proof,'exact CNF/trace command inputs')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--campaign-summary-sha256',required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    need(re.fullmatch('[0-9a-f]{64}',args.campaign_summary_sha256) is not None,'explicit final summary identity')
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};started=time.perf_counter()
    def pin(path,expected=None):
        path=path.resolve();name=key(path)
        if name not in pins:pins[name]=sha(path)
        need(expected is None or pins[name]==expected,'hash '+name);return pins[name]
    def receipt(r,exitcode=None,allow_guard=False):
        need(allow_guard or r['outer_windows_guard_expired'] is False,'receipt guard')
        if exitcode is not None:need(r['actual_exit_code']==exitcode,'receipt exit')
        for field in ['stdout','stderr']:pin(ROOT/r[field],r[field+'_sha256'])
    try:
        pin(RUN/'summary.json',args.campaign_summary_sha256)
        for path,digest in PINS.items():pin(path,digest)
        pin(HELPER,read(PRIOR)['inputs_sha256'][key(HELPER)])
        spec=importlib.util.spec_from_file_location('independent_drat_helper',HELPER);helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
        for path in [helper.BUILD/'drat-trim.exe',helper.BUILD/'build_manifest.json',helper.BUILD/'build_receipt.json']:pin(path,helper.PINS[path])
        provenance=helper.authenticate(pin)
        enc,obj=read(ENC),read(OBJ)
        need(enc['status']=='INDEPENDENT_HADAMARD_FIFTYFOUR_PROFILE_ENCODING_PASS' and enc['checked_formulas']==54,'complete formula gate')
        need(obj['status']=='INDEPENDENT_HADAMARD_FIFTYFOUR_PROFILE_OBJECT_CALIBRATION_PASS','prelaunch object gate')
        for report in [enc,obj]:
            for name,digest in report['inputs_sha256'].items():pin(ROOT/name,digest)
        binding_path=ENC.parent/'claim_binding.json';pin(binding_path,enc['outputs_sha256'][key(binding_path)]);binding=read(binding_path)
        need(binding['id']=='C-FIXED-HADAMARD-FIFTYFOUR-SIX-EXCEPTION-GRAM-ENCODINGS' and binding['revision']==1,'exact encoding revision')
        data=read(DATA/'summary.json');selection=data['selection'];formula={r['profile_id']:r for r in data['records']}
        need(len(selection)==len(set(selection))==len(formula)==54 and selection==obj['selected_profiles'],'frozen 54 inputs')
        final=read(RUN/'summary.json');manifest=read(RUN/'manifest.json');cm=read(RUN/'campaign_manifest.json')
        need(manifest['mode']=='RESEARCH' and manifest['resume_checkpoint'] is None and manifest['automatic_retry'] is False,'fresh single campaign')
        for name,digest in manifest['inputs_sha256'].items():pin(ROOT/name,digest)
        for path in RUN.iterdir():
            if path.is_file():pin(path)
        need(final['manifest_path']==key(RUN/'manifest.json') and final['manifest_sha256']==pins[key(RUN/'manifest.json')],'final manifest identity')
        need(final['campaign_manifest']==manifest['campaign_manifest']==dict(path=key(RUN/'campaign_manifest.json'),sha256=pins[key(RUN/'campaign_manifest.json')]),'campaign origin identity')
        need(final['selected_profiles']==cm['selection']==selection and final['inputs_sha256']==cm['inputs_sha256']==manifest['inputs_sha256'],'selection/input binding')
        records=final['profile_records'];attempted=[r['profile_id'] for r in records]
        need(attempted==selection[:len(records)] and final['completed_attempts']==len(records) and final['unattempted_profiles']==selection[len(records):],'complete attempt prefix and unattempted suffix')
        need(final['automatic_retry'] is False and len(records)<=54,'no hidden retries')
        limits=manifest['limits'];need(limits==cm['limits'],'same declared allocation')
        need(limits['native_wall_seconds_per_case']==60 and limits['conflicts_per_case']==1000000 and limits['campaign_wrapped_wall_seconds']==900 and limits['maximum_cases']==54 and limits['next_launch_reserve_seconds']==70 and limits['total_retained_trace_soft_bytes']==2147483648,'declared limits')
        progress=[json.loads(line) for line in (RUN/'progress.jsonl').read_text().splitlines()];need(progress==records,'complete progress records')
        for i,profile in enumerate([None]+attempted):
            cp=read(RUN/('checkpoint_initial.json' if profile is None else f'checkpoint_{profile}.json'))
            need(cp['selected_profiles']==selection and cp['profile_records']==records[:i] and cp['inputs_sha256']==manifest['inputs_sha256'],'immutable checkpoint prefix')
        if len(records)==54:need(final['stop_reason']=='ALL_SELECTED_PROFILES_ATTEMPTED','complete batch stop')
        fixtures={'tiny_unsat.cnf':b'p cnf 2 4\n1 2 0\n1 -2 0\n-1 2 0\n-1 -2 0\n','tiny_sat.cnf':b'p cnf 2 3\n1 2 0\n1 -2 0\n-1 2 0\n','tiny_valid.drat':b'-2 0\n1 0\n0\n','empty_only.drat':b'0\n','fresh_unit.drat':b'3 0\n0\n'}
        for name,value in fixtures.items():(out/name).write_bytes(value)
        tiny=[(1,2),(1,-2),(-1,2),(-1,-2)];oracle=lambda cs:[bits for bits in range(4) if all(any(bool(bits&(1<<(abs(v)-1)))==(v>0) for v in c) for c in cs)]
        need(oracle(tiny)==[] and oracle(tiny[:-1])==[3],'exact tiny SAT/UNSAT calibration')
        controls=[helper.replay(name,out/cnf,out/proof,out,expected) for name,cnf,proof,expected in [('positive_reasoning','tiny_unsat.cnf','tiny_valid.drat',True),('missing_reasoning','tiny_unsat.cnf','empty_only.drat',False),('unsupported_unit','tiny_unsat.cnf','fresh_unit.drat',False),('changed_SAT_input','tiny_sat.cnf','tiny_valid.drat',False)]]
        checked=[];corruptions=[];totals=Counter();used=0.;retained=0
        for ref in records:
            profile=ref['profile_id'];selected=formula[profile];rp=ROOT/ref['summary_path'];pin(rp,ref['summary_sha256']);s=read(rp);folder=rp.parent
            need(rp==RUN/profile/'summary.json' and s['profile_id']==profile and s['research_calls']==1,'literal attempt identity')
            need(used+70<=900 and retained<2147483648,'prelaunch cumulative reserves')
            need(s['inputs_sha256']==manifest['inputs_sha256'],'per-profile immutable inputs')
            for name,digest in s['outputs_sha256'].items():pin(ROOT/name,digest)
            for field in ['cnf','model','scope']:
                path=ROOT/selected[field+'_path'];pin(path,selected[field+'_sha256']);need(s[field+'_sha256']==selected[field+'_sha256']==enc['inputs_sha256'][key(path)],'exact reviewed formula')
            cnf=ROOT/selected['cnf_path'];scope=read(ROOT/selected['scope_path'])
            need(scope['selected_profile_id']==profile and len(scope['exceptional_groups'])==6,'literal six profile')
            need(scope['within_group_column_caps_encoded'] and not scope['cross_group_column_caps_encoded'] and not scope['residual_D_encoded'] and not scope['arc_pruning_used'] and not scope['orbit_coverage_used'],'conditional scope')
            r=read(folder/'main/solver.receipt.json');launch=read(folder/'main/launch.json')
            need(r==s['native_receipt'] and launch['command']==r['command'] and launch['cnf_sha256']==selected['cnf_sha256'],'launch receipt binding')
            command_check(r['command'],cnf,launch['ext4_proof']);need(r['outer_windows_guard_seconds']==70,'outer70s guard');receipt(r,allow_guard=True)
            resource=s['resource_check'];need(resource['host_free_bytes']>=limits['host_free_reserve_bytes'] and resource['ext4_free_bytes']>=limits['ext4_free_reserve_bytes'],'actual prelaunch disk reserves')
            for field in ['mount_receipt','disk_receipt']:receipt(resource[field],0)
            need('ext4' in (ROOT/resource['mount_receipt']['stdout']).read_text().split(),'actual ext4 location')
            need(int((ROOT/resource['disk_receipt']['stdout']).read_text().split()[-1])==resource['ext4_free_bytes'],'actual disk reading')
            for phase in ['processes_before','processes_after']:
                if phase not in s:need(s['stop_reason'] is not None,'missing observation disclosed');continue
                pr=s[phase];receipt(pr);need(pr['actual_exit_code'] in (0,1) and pr['command'][4:]==['/usr/bin/ps','-C','cadical','-o','pid,ppid,comm,pcpu,rss,args'],'targeted native observation')
                need('/'+key(cnf) not in (ROOT/pr['stdout']).read_text(),'no exact-input process in saved observation')
            trace=None
            if 'proof_copy' in s:
                t=s['proof_copy'];proof=folder/'main/proof.drat';pin(proof,t['sha256']);need(proof.stat().st_size==t['bytes']<=10737418240,'full host trace hash/size')
                receipt(t['native_hash_receipt'],0);receipt(t['copy_receipt'],0)
                need(t['linux_source']==launch['ext4_proof'] and t['native_hash_receipt']['command'][-2:]==['/usr/bin/sha256sum',t['linux_source']],'exact native trace hash command')
                need(t['copy_receipt']['command'][-4:-1]==['/usr/bin/cp','--',t['linux_source']] and t['copy_receipt']['command'][-1].endswith('/'+key(proof)),'exact immediate copy command')
                need((ROOT/t['native_hash_receipt']['stdout']).read_text().split()==[t['sha256'],t['linux_source']],'native/host complete identity')
                need(s['retained_raw_trace_bytes']==ref['retained_raw_trace_bytes']==2*t['bytes'],'two-copy inventory')
                trace=dict(path=key(proof),sha256=t['sha256'],bytes=t['bytes'],availability='LOCAL_ONLY',availability_reason='Preserved host artifact; public transport or publication requires a separate availability record.')
            else:need(s['stop_reason'] is not None and ref['retained_raw_trace_bytes'] is None,'unavailable trace explicitly disclosed')
            need(ref['wrapped_wall_seconds']==r['wall_seconds'] and ref['interpreted_result']==s['interpreted_result'],'receipt-derived campaign counters')
            used+=r['wall_seconds'];retained+=ref['retained_raw_trace_bytes'] or 0
            record=dict(profile_id=profile,cnf_path=key(cnf),cnf_sha256=selected['cnf_sha256'],model_path=selected['model_path'],model_sha256=selected['model_sha256'],scope_path=selected['scope_path'],scope_sha256=selected['scope_sha256'],literal_profile={k:scope[k] for k in ['selected_profile_id','selected_profile_sha256','exceptional_groups','coordinate_fibre_deviations','balanced_groups']},run_summary_path=key(rp),run_summary_sha256=ref['summary_sha256'],native_receipt_path=key(folder/'main/solver.receipt.json'),native_receipt_sha256=sha(folder/'main/solver.receipt.json'),trace=trace)
            text=(ROOT/r['stdout']).read_text();code=r['actual_exit_code']
            if code==20:
                need(trace is not None and s['stop_reason'] is None and s['interpreted_result']=='UNSAT_COMPLETE_TRACE_UNCHECKED','complete native UNSAT')
                stats=parse_unsat(text,r,selected['variables'],selected['clauses']);need(stats['trace_bytes']==trace['bytes'],'native trace byte counter')
                for kind,bad,rr in [('header',text.replace(f"{selected['variables']} {selected['clauses']}",f"{selected['variables']} {selected['clauses']+1}"),r),('status',text.replace('s UNSATISFIABLE','s SATISFIABLE'),r),('duplicate',text+'s UNSATISFIABLE\n',r),('exit',text,{**r,'actual_exit_code':0}),('guard',text,{**r,'outer_windows_guard_expired':True}),('allocation',text.replace("1000000 conflicts (due to '1000000')","1000000 conflicts (due to '2')"),r)]:
                    try:parse_unsat(bad,rr,selected['variables'],selected['clauses'])
                    except ValueError:corruptions.append(dict(profile_id=profile,kind=kind))
                    else:raise ValueError('accepted native corruption '+kind)
                controls.append(helper.replay(profile+'_empty_only',cnf,out/'empty_only.drat',out,False))
                record.update(outcome='UNSAT_VERIFIED',native_stats=stats,replay=helper.replay(profile+'_complete',cnf,proof,out,True));totals['UNSAT_VERIFIED']+=1
            elif code==10:
                need([line for line in text.splitlines() if line.startswith('s ')]==['s SATISFIABLE'] and s['stop_reason']=='SAT_PENDING_INDEPENDENT_REVIEW','SAT receipt boundary')
                record.update(outcome='SAT_PENDING_SEPARATE_OBJECT_REVIEW',native_stats=None,native_stats_null_reason='Proof-collection checker does not approve a decoded SAT factor.');totals['SAT_PENDING']+=1
            else:
                need(s['interpreted_result']=='UNKNOWN_NATIVE_OR_RESOURCE_OUTCOME' and not any(line in ('s SATISFIABLE','s UNSATISFIABLE') for line in text.splitlines()),'UNKNOWN receipt is not a conclusive result')
                record.update(outcome='UNKNOWN',native_stats=None,native_stats_null_reason='Nonconclusive or interrupted native outcome; raw receipts remain authoritative.');totals['UNKNOWN']+=1
            checked.append(record);save(out/(profile+'.json'),record);print(json.dumps(dict(profile_id=profile,outcome=record['outcome'],checked=len(checked))),flush=True)
        need(used==final['wrapped_solver_wall_seconds'] and retained==final['retained_raw_trace_bytes_known'] and used<=900,'exact final aggregate accounting')
        pin(Path(__file__));pin(PLAN);now=datetime.now(timezone.utc).isoformat();all_unsat=len(checked)==54 and totals['UNSAT_VERIFIED']==54
        limitations=['Only the exact literal UNSAT profiles checked here are excluded; fibre-orbit transfer and complete exception-count coverage require separate review.','Pinned six-prism Hadamard support, full Gram and within-group caps; no cross-group caps or residual D are encoded.','UNKNOWN, unattempted and pending SAT outcomes give no exclusion.','No new native solver execution; trusted DRAT-trim, reviewed Windows shim, compiler/runtime and shared independent authentication helper disclosed.']
        if all_unsat:
            statement='For each of the 54 literal six-exception profiles in the authenticated selected_profiles list, no binary36x60 factor on the fixed six-prism Hadamard support realizes its prescribed profile, full integer Gram and within-group column caps. Every exact CNF has an independently replayed complete DRAT proof.'
            claim=dict(id=CID,revision=1,statement=statement,kind='exclusion',basis=['DERIVED','COMPUTED'],status='VERIFIED',review_state='CLEAR',scope=limitations[0],assumptions=['Exact fixed support and all 54 literal scope files; no target automorphism assumption.'],dependencies=[dict(id=binding['id'],revision=1,relation='encoding_equivalence')],verifier='/root/structural_attack',producer='/root/state_literature_audit',checking_method='Full independent complete DRAT replay, raw receipt/trace identities and positive/corrupted controls.',shared_components=['Same authenticated DRAT-trim binary and frozen independently authored balanced-proof authentication/replay helper as earlier checks.','No producer code or solver imported.'],inputs_sha256=pins,evidence_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},profile_records=checked,limitations=limitations,artifact_availability='LOCAL_ONLY',availability_reason='Any later public proof transport is a separate record.',created_at=now,updated_at=now)
            save(out/'claim_binding.json',claim)
        report=dict(status='INDEPENDENT_FIXED_HADAMARD_FIFTYFOUR_PROFILE_UNSAT_PASS' if all_unsat else 'INDEPENDENT_FIFTYFOUR_PROFILE_CAMPAIGN_RECEIPT_AUDIT_PASS',timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,outputs_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},selected_profiles=selection,profile_records=checked,completed_attempts=len(checked),completed_proof_replays=totals['UNSAT_VERIFIED'],SAT_pending_separate_review=totals['SAT_PENDING'],UNKNOWN=totals['UNKNOWN'],unattempted_profiles=final['unattempted_profiles'],proof_bytes=sum(r['trace']['bytes'] for r in checked if r['outcome']=='UNSAT_VERIFIED'),retained_two_copy_bytes=retained,configured_limits=limits,wrapped_solver_wall_seconds=used,recorded_end_to_end_wall_seconds=final['end_to_end_wall_seconds'],checker_provenance=provenance,controls=controls,native_receipt_corruptions_rejected=corruptions,claim_id=CID if all_unsat else None,claim_id_null_reason=None if all_unsat else 'No aggregate 54-exclusion claim without every complete proof.',limitations=limitations,new_solver_calls=0,target_resolution=False,elapsed_seconds=time.perf_counter()-started)
        save(out/'summary.json',report);print(json.dumps(dict(status=report['status'],summary_sha256=sha(out/'summary.json'))))
    except BaseException as exc:save(out/'failure.json',dict(error=repr(exc),source_sha256=sha(Path(__file__))));raise

if __name__=='__main__':main()
