"""Independent one-run outcome, complete proof or complete factor validation."""
from datetime import datetime,timezone
from pathlib import Path
import argparse,json,platform,subprocess,sys,time
import audit_20260930_connected_fixed_core_native_outcome_v2 as parser
import audit_20260930_hadamard_cyclic_unsat as drat
ROOT=parser.ROOT;B=ROOT/'acceleration/results';RUN=B/'20260930_hadamard_prism_ordered_native_pilot';D=B/'20260930_hadamard_prism_ordered_cnf'
ENC=B/'20260930_independent_review/hadamard_prism_ordered_cnf/summary.json';OBJECT=B/'20260930_independent_review/hadamard_prism_ordered_object_calibration/summary.json'
need,digest,key,save,read=parser.need,parser.digest,parser.key,parser.save,parser.read
PINS={key(ENC):'377e985056a4f6daae704d342c63d4a06d7086ee43b3b5e9636d9a1135d18132',key(OBJECT):'1732d5f2288473740c52120974182021f25034b461efd7aec669603a5daad29b',key(D/'instance.cnf'):'51cedaa0e54ab569e6ec4b8ad19fb17136ad5e8a9bdbd751b994903e4024f5df',key(D/'model.json'):'85f2008d34c5f089e04e87306462a10be4919c582da6b6a2303523f5f6ea737a',key(D/'scope.json'):'5d8cac247339006994035ac21c379edafdb8b55ec11213eba2ac22859430b466','acceleration/native_20260930_hadamard_prism_ordered.py':'154a6ebdee0382cef0aaf2cec15faed1eb51799add32d202077a2cb052568254','acceleration/audit_20260930_connected_fixed_core_native_outcome_v2.py':'b788077b58db41737f9e541e7c74de9d2135d50f72da07df288435b4d65bc472'}

def outcome(text,receipt):
    need(text.splitlines().count("c found 'p cnf 595464 3336642' header")==1,'exact actual input dimensions')
    return parser.parse_outcome(text.replace("c found 'p cnf 595464 3336642' header","c found 'p cnf 110904 518184' header"),receipt)

def controls():
    prior=parser.controls();positives=[];rejects=[]
    for i,case in enumerate(prior['positive_synthetic_cases']):
        text=case['stdout'].replace('110904 518184','595464 3336642');receipt=case['receipt'];positives.append(dict(label='SYNTHETIC outcome parser only',checked=outcome(text,receipt)))
        for name,bad,rec in [('header',text.replace('3336642','3336641'),receipt),('terminal',text+'s SATISFIABLE\n',receipt),('limit_annotation',text.replace('2000000 conflicts',"2000000 conflicts (due to '1')"),receipt),('outer_guard',text,{**receipt,'outer_windows_guard_expired':True})]:
            try:outcome(bad,rec)
            except ValueError:rejects.append(f'{i}_{name}')
            else:raise ValueError('accepted outcome corruption '+name)
    return dict(positive_synthetic_cases=positives,new_corruptions_rejected=rejects,shared_parser_corruptions_rejected=prior['corruptions_rejected'])

def replay(name,cnf,proof,out,expected):
    command=[str(ROOT/'build/rook-drat-checker/drat-trim.exe'),str(cnf),str(proof)];begin=time.monotonic();run=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=600)
    for suffix,data in [('stdout.log',run.stdout),('stderr.log',run.stderr)]:(out/f'{name}.{suffix}').write_bytes(data)
    accepted=run.returncode==0 and b's VERIFIED' in run.stdout;record=dict(name=name,command=command,cwd=str(ROOT),timestamp=datetime.now(timezone.utc).isoformat(),exit_code=run.returncode,accepted=accepted,expected_acceptance=expected,timeout_seconds=600,elapsed_seconds=time.monotonic()-begin,cnf_sha256=digest(cnf),proof_sha256=digest(proof),stdout=key(out/f'{name}.stdout.log'),stdout_sha256=digest(out/f'{name}.stdout.log'),stderr=key(out/f'{name}.stderr.log'),stderr_sha256=digest(out/f'{name}.stderr.log'))
    save(out/f'{name}.receipt.json',record);print(json.dumps(dict(name=name,accepted=accepted,expected=expected)),flush=True);need(accepted==expected,'proof replay/control '+name);return record

def full_proof(trace,out,bindings):
    # Reuses the frozen independently authored authentication path. Its earlier
    # cyclic input bindings are retained as disclosed provenance, not premises.
    provenance=drat.authenticate(bindings);fixtures={'tiny_unsat.cnf':b'p cnf 2 4\n1 2 0\n1 -2 0\n-1 2 0\n-1 -2 0\n','tiny_sat.cnf':b'p cnf 2 3\n1 2 0\n1 -2 0\n-1 2 0\n','tiny_valid.drat':b'-2 0\n1 0\n0\n','invalid_empty_only.drat':b'0\n','invalid_fresh_unit.drat':b'3 0\n0\n'}
    for name,data in fixtures.items():(out/name).write_bytes(data)
    clauses=[(1,2),(1,-2),(-1,2),(-1,-2)];sat=lambda cs:[v for v in range(4)if all(any(bool(v&(1<<(abs(x)-1)))==(x>0)for x in row)for row in cs)];need(sat(clauses)==[]and sat(clauses[:3])==[3],'tiny independent truth oracle')
    specs=[('positive_tiny',out/'tiny_unsat.cnf',out/'tiny_valid.drat',True),('corrupt_missing_units',out/'tiny_unsat.cnf',out/'invalid_empty_only.drat',False),('corrupt_fresh_unit',out/'tiny_unsat.cnf',out/'invalid_fresh_unit.drat',False),('corrupt_formula_is_sat',out/'tiny_sat.cnf',out/'tiny_valid.drat',False),('corrupt_main_empty_only',D/'instance.cnf',out/'invalid_empty_only.drat',False),('main_complete_proof',D/'instance.cnf',trace,True)]
    return provenance,[replay(*spec[:3],out,spec[3])for spec in specs]

def main():
    ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='mode',required=True);c=sub.add_parser('calibrate');c.add_argument('--out',type=Path,required=True);a=sub.add_parser('audit');a.add_argument('--summary-sha256',required=True);a.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);bindings={};started=time.monotonic()
    def pin(p,h=None,progress=False):
        value=digest(p,progress);need(h is None or value==h,'input identity '+key(p));bindings[key(p)]=value;return value
    try:
        for p,h in PINS.items():pin(ROOT/p,h)
        for p in [Path(__file__),Path(drat.__file__),ROOT/'docs/AUDIT_20260930_HADAMARD_PRISM_ORDERED_OUTCOME.md',ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(p)
        control=controls();save(out/'controls.json',control);base=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),verifier='/root/state_literature_audit',shared_components=['Frozen independent native outcome parser with separately checked actual input dimensions.','On UNSAT, prior independent DRAT build authentication and fresh complete proof replay; on SAT, separately frozen full-object checker.','No producer imports or solver execution.'],artifact_availability='LOCAL_ONLY',target_resolution=False,external_review=False)
        if args.mode=='calibrate':
            report={**base,'status':'INDEPENDENT_HADAMARD_PRISM_ORDERED_OUTCOME_PARSER_CALIBRATION_PASS','inputs_sha256':bindings,'positive_synthetic_cases':4,'new_corruptions_rejected':16,'shared_corruptions_rejected':28,'scope':'Parser calibration only; no current run inspected or approved.'}
        else:
            pin(RUN/'summary.json',args.summary_sha256);summary=read(RUN/'summary.json');manifest=read(RUN/'manifest.json');receipt=read(RUN/'main/solver.receipt.json');launch=read(RUN/'main/launch.json')
            for p in [RUN/'manifest.json',RUN/'main/solver.receipt.json',RUN/'main/launch.json']:pin(p)
            for p,h in manifest['inputs_sha256'].items():pin(ROOT/p,h)
            need(read(ENC)['status']=='INDEPENDENT_FIXED_SUPPORT_PRISM_ORDERED_COLORING_CNF_PASS'and read(OBJECT)['status']=='INDEPENDENT_FIXED_SUPPORT_PRISM_ORDERED_COLORING_OBJECT_CHECKER_CALIBRATION_PASS','both independent gates')
            need(read(OBJECT)['inputs_sha256'][key(ENC)]==PINS[key(ENC)],'same exact encoding gate')
            limits=dict(native_wall_seconds=300,cpu_seconds_limit=None,cpu_seconds_limit_null_reason='Existing calibrated wall-time guard retained; no CPU rlimit set.',conflicts=2000000,address_space_bytes=4294967296,file_bytes=10737418240,kill_after_seconds=5,outer_windows_guard_seconds=320,maximum_research_attempts=1,automatic_retry=False)
            need(manifest['mode']=='RESEARCH'and manifest['limits']==limits and summary['research_calls']==1 and summary['automatic_retry']is False,'one frozen bounded attempt')
            need(summary['receipt']==receipt and summary['actual_exit_code']==receipt['actual_exit_code']and launch['command']==receipt['command'],'actual invocation identity');command=receipt['command']
            need(all(x in command for x in ['300s','--signal=TERM','--kill-after=5s','--as=4294967296:4294967296','--fsize=10737418240:10737418240','--core=0:0','--no-binary'])and command[command.index('-c')+1]=='2000000','exact wall/resource invocation')
            need(launch['cnf_sha256']==PINS[key(D/'instance.cnf')]and launch['model_sha256']==PINS[key(D/'model.json')]and any(x.endswith('/'+key(D/'instance.cnf'))for x in command),'actual exact CNF/model')
            for p,h in summary['outputs_sha256'].items():pin(ROOT/p,h,progress=Path(p).name=='proof.drat')
            need(digest(ROOT/receipt['stdout'])==receipt['stdout_sha256']and digest(ROOT/receipt['stderr'])==receipt['stderr_sha256']and(ROOT/receipt['stderr']).read_bytes()==b'','actual log bytes')
            parsed=outcome((ROOT/receipt['stdout']).read_text(),receipt);trace=RUN/'main/proof.drat';copy=summary['proof_copy'];need(copy['sha256']==bindings[key(trace)]and copy['bytes']==trace.stat().st_size,'entire trace identity')
            for name,field in [('transfer_hash','native_hash_receipt'),('transfer_copy','copy_receipt')]:
                rec=read(RUN/'main'/f'{name}.receipt.json');need(rec==copy[field]and rec['actual_exit_code']==0 and not rec['outer_windows_guard_expired'],'successful transfer record')
                for channel in ['stdout','stderr']:pin(ROOT/rec[channel],rec[channel+'_sha256'])
            need((ROOT/copy['native_hash_receipt']['stdout']).read_text().split()==[copy['sha256'],copy['linux_source']],'native whole trace hash')
            for rec in [manifest['filesystem_receipt'],manifest['ext4_disk_receipt']]:
                need(rec['actual_exit_code']==0 and not rec['outer_windows_guard_expired'],'filesystem command success')
                for channel in ['stdout','stderr']:pin(ROOT/rec[channel],rec[channel+'_sha256'])
            proof_result=None;object_result=None;code=receipt['actual_exit_code']
            if code==20:
                proofout=out/'proof_replay';proofout.mkdir();checker,replays=full_proof(trace,proofout,bindings);proof_result=dict(checker_provenance=checker,replays=replays,complete_independent_replay=True)
            elif code==10:
                objout=out/'raw_object';object_command=[sys.executable,'-B','acceleration/audit_20260930_hadamard_prism_ordered_object.py','sat','--assignment',key(RUN/'main/parsed_model.json'),'--native-output',key(RUN/'main/solver.stdout.log'),'--out',key(objout)]
                if(RUN/'main/decoded_factor.json').exists():object_command+=['--decoded',key(RUN/'main/decoded_factor.json')]
                checked=subprocess.run(object_command,cwd=ROOT,capture_output=True,timeout=120);(out/'object.stdout.log').write_bytes(checked.stdout);(out/'object.stderr.log').write_bytes(checked.stderr);need(checked.returncode==0,'independent complete SAT object accepted');obj=read(objout/'summary.json');need(obj['status']=='INDEPENDENT_FIXED_SUPPORT_PRISM_ORDERED_COLORING_FACTOR_OBJECT_PASS','complete object status');object_result=dict(command=object_command,exit_code=checked.returncode,summary_path=key(objout/'summary.json'),summary_sha256=digest(objout/'summary.json'))
            else:need(not(RUN/'main/parsed_model.json').exists()and not(RUN/'main/decoded_factor.json').exists(),'UNKNOWN has no claimed SAT object')
            pscommand=['wsl.exe','--distribution','Ubuntu-24.04','--exec','/usr/bin/ps','-eo','pid,args'];ps=subprocess.run(pscommand,capture_output=True,text=True,timeout=20);need(ps.returncode==0,'fresh read-only process observation');observation=dict(timestamp=datetime.now(timezone.utc).isoformat(),command=pscommand,matching_exact_input_processes=[s.strip()for s in ps.stdout.splitlines()if '/'+key(D/'instance.cnf')in s]);save(out/'process_observation.json',observation)
            # Complete final rebind uses streaming hashes and authenticates the
            # proof too; no mutation during replay can pass silently.
            for p,h in list(bindings.items()):pin(ROOT/p,h)
            status='INDEPENDENT_FIXED_HADAMARD_PRISM_ORDERED_UNSAT_PASS'if code==20 else'INDEPENDENT_FIXED_HADAMARD_PRISM_ORDERED_SAT_FACTOR_PASS'if code==10 else'INDEPENDENT_HADAMARD_PRISM_ORDERED_UNKNOWN_RUN_AUDIT_PASS'
            report={**base,'status':status,'inputs_sha256':bindings,'actual_attempts':1,'outcome':parsed,'configured_limits':limits,'native_command':command,'run_source_commit':manifest['source_commit'],'run_command':manifest['command'],'trace':dict(path=key(trace),bytes=trace.stat().st_size,sha256=bindings[key(trace)],availability='LOCAL_ONLY',complete_independent_UNSAT_replay=code==20),'proof_result':proof_result,'object_result':object_result,'current_process_observation':observation,'scope':'One literal fixed-support factor family modulo audited identical-support ordering; no cyclic restriction, residual D or other-support coverage.','limitations':['UNKNOWN is not an exclusion, and its partial trace is not a proof.','A complete factor still requires residual D and full99 target validation.','Any checked UNSAT excludes only this fixed support, not its core or the target.','Resource settings are configured limits; no performance conclusion.'],'elapsed_seconds':time.monotonic()-started}
        report['outputs_sha256']={key(p):digest(p)for p in out.rglob('*')if p.is_file()};save(out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(out/'summary.json'))))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e)));raise
if __name__=='__main__':main()
