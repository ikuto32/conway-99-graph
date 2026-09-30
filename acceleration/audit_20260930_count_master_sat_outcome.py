"""Independent saved native SAT execution and exact count-witness binding."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,copy,hashlib,json,platform,re,subprocess,sys,time,traceback
import audit_20260930_hadamard_count_master_object as obj
ROOT=obj.ROOT;B=obj.B;R=B+'hadamard_count_master_native_pilot_v2/';OLD=B+'hadamard_count_master_native_pilot/'
need=obj.need;read=obj.read;sha=obj.sha;save=obj.save;key=obj.key
def receipt_check(summary,text):
    rec=summary['receipt'];cmd=rec['command']
    need(rec['actual_exit_code']==10 and not rec['outer_windows_guard_expired']and rec['outer_windows_guard_seconds']==70,'native SAT return without guard')
    need([l for l in text.splitlines()if l.startswith('s ')]==['s SATISFIABLE'],'one actual SAT status')
    need(cmd[4:13]==['/usr/bin/timeout','--signal=TERM','--kill-after=5s','60s','/usr/bin/prlimit','--as=4294967296:4294967296','--fsize=10737418240:10737418240','--core=0:0',cmd[12]],'resource wrapper')
    need(cmd[-5:-2]==['--no-binary','-c','1000000']and cmd[-2].endswith('/'+obj.D+'at_least_seven.cnf'),'exact solver options/input')
    need(summary['research_calls']==1 and summary['automatic_retry']is False,'one actual research call')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={};start=time.perf_counter()
    def pin(p,h=None):pins[p]=sha(ROOT/p);need(h is None or h==pins[p],'hash '+p)
    try:
        for p in [R+'summary.json',R+'manifest.json',R+'main/launch.json',R+'independent_object/summary.json',OLD+'failure.json',OLD+'invocation_correction.json']:pin(p)
        run=read(R+'summary.json');gate=read(R+'independent_object/summary.json')
        for p,h in {**run['inputs_sha256'],**run['outputs_sha256'],**gate['inputs_sha256']}.items():pin(p,h)
        need(gate['status']=='INDEPENDENT_HADAMARD_COUNT_MASTER_SAT_OBJECT_PASS'and gate['actual_clauses_checked']==705833,'saved independent object gate')
        stdout=(ROOT/(R+'main/solver.stdout.log')).read_text();receipt_check(run,stdout)
        rec=run['receipt'];need(sha(ROOT/rec['stdout'])==rec['stdout_sha256']and sha(ROOT/rec['stderr'])==rec['stderr_sha256'],'native raw receipt identities')
        trace=run['proof_copy'];need(sha(ROOT/(R+'main/proof.drat'))==trace['sha256']and (ROOT/(R+'main/proof.drat')).stat().st_size==trace['bytes'],'fresh full native trace identity')
        need(run['independent_object_receipt']['actual_exit_code']==0 and not run['independent_object_receipt']['outer_windows_guard_expired'],'actual independent child success')
        correction=read(OLD+'invocation_correction.json');need(correction['native_calls']==0 and correction['status']=='PREFLIGHT_REFUSAL_BEFORE_NATIVE'and correction['failure_sha256']==pins[OLD+'failure.json']and not (ROOT/(OLD+'main/launch.json')).exists(),'preserved pre-execution refusal')
        model=read(obj.D+'model.json');decoded,clauses=obj.evaluate(model,'at_least_seven',ROOT/(R+'main/parsed_model.json'),ROOT/(R+'main/solver.stdout.log'),ROOT/(R+'main/decoded_count_profile.json'))
        need(decoded==read(R+'independent_object/independent_count_profile.json'),'fresh raw independent replay matches saved child')
        need(decoded['exception_count']==8 and decoded['profile_sha256']=='d2b0c89bb1d8f0d75b47f541603e952618cebe9b7ecccd8e1b2c23a279ac8dd9','exact eight-exception profile')
        rejected=[]
        for name in ['exit','guard','wall','conflicts','input','research_count','status']:
            bad=copy.deepcopy(run);text=stdout
            if name=='exit':bad['receipt']['actual_exit_code']=20
            elif name=='guard':bad['receipt']['outer_windows_guard_expired']=True
            elif name=='wall':bad['receipt']['command'][7]='600s'
            elif name=='conflicts':bad['receipt']['command'][-3]='100'
            elif name=='input':bad['receipt']['command'][-2]='wrong.cnf'
            elif name=='research_count':bad['research_calls']=2
            else:text=stdout.replace('s SATISFIABLE','s UNSATISFIABLE')
            try:receipt_check(bad,text)
            except ValueError:rejected.append(name)
            else:raise ValueError('receipt corruption accepted '+name)
        save(out/'controls.json',dict(known_positive_actual_SAT_receipt=True,rejected_receipt_corruptions=rejected,object_controls_bound_to=obj.GATE_SHA))
        save(out/'independent_count_profile.json',decoded)
        for p in [key(Path(__file__)),key(Path(obj.__file__)),key(Path(obj.independent.__file__)),'uv.lock','pyproject.toml']:pin(p)
        ts=datetime.now(timezone.utc).isoformat();record=dict(id='C-FIXED-HADAMARD-AT-LEAST-SEVEN-COUNT-CSP-WITNESS',revision=1,statement='The pinned 155939-variable 705833-clause count-master formula with at least seven exceptional groups has the complete saved satisfying assignment, independently decoding to the exact count profile d2b0c89bb1d8f0d75b47f541603e952618cebe9b7ecccd8e1b2c23a279ac8dd9 with eight exceptional groups.',kind='construction',basis=['COMPUTED'],status='VERIFIED',review_state='CLEAR',scope='One necessary integer count-CSP witness on the literal fixed support; no full factor, unsummed Gram, cross-group caps or residual graph asserted.',dependencies=[dict(id='C-FIXED-HADAMARD-ARBITRARY-EXCEPTION-COUNT-MASTER-ENCODING',revision=1,relation='encoding_equivalence')],assumptions=['Exact immutable model/input encoding and fixed support as authenticated by the encoding gate.'],verifier='/root/eight_domain_audit',checking_method='Independent strict native/JSON parser, all705833 literal clause checks and exact raw720-entry count/marginal/signature reconstruction, plus separate native receipt/trace identity audit. Repeated artifact checking reuses our frozen independent checker; it is not a new implementation.',trusted_components=['Frozen independent object and encoding checkers, standard-library exact arithmetic. No producer imports.'],verification_records=[dict(claim_id='C-FIXED-HADAMARD-AT-LEAST-SEVEN-COUNT-CSP-WITNESS',claim_revision=1,verifier='/root/eight_domain_audit',kind='independent_artifact_checking',timestamp=ts,outcome='PASS',inputs_sha256=pins,command=[sys.executable,*sys.argv],cwd=str(ROOT),scope='Complete assignment/native clauses/raw count object and saved execution evidence only.')],limitations=['This positive count table is not an incidence factor or target graph.','The SAT trace is preserved as execution evidence, not an UNSAT proof.','Initial failed invocation made zero native calls; corrected v2 made the first and only actual research call.'],artifact_availability='LOCAL_ONLY',availability_reason='Awaiting publication.',created_at=ts,updated_at=ts,external_review=None,external_review_null_reason='Internal independent check only.')
        save(out/'claim_binding.json',record)
        result=dict(status='INDEPENDENT_COUNT_MASTER_NATIVE_SAT_OUTCOME_PASS',timestamp=ts,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in out.iterdir()},native_calls_completed=1,initial_refused_native_calls=0,actual_native_exit=10,actual_clauses_checked=clauses,exception_count=8,profile_sha256=decoded['profile_sha256'],partial_SAT_trace=dict(path=R+'main/proof.drat',sha256=trace['sha256'],bytes=trace['bytes'],proof_of_UNSAT=False,availability='LOCAL_ONLY'),new_solver_calls=0,target_resolution=False,elapsed_seconds=time.perf_counter()-start)
        save(out/'summary.json',result);print(json.dumps(dict(status=result['status'],summary_sha256=sha(out/'summary.json'),binding_sha256=sha(out/'claim_binding.json'))))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e),traceback=traceback.format_exc(),source_sha256=sha(Path(__file__)),inputs_sha256=pins));raise
if __name__=='__main__':main()
