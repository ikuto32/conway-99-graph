"""Authenticate the one native SAT run and bind encoding/witness claims."""
from copy import deepcopy
from datetime import datetime,timezone
from pathlib import Path
import argparse,json,platform,re,subprocess,sys
import audit_20260930_hadamard_parity_support_cuts as checker
ROOT=checker.ROOT;B=checker.B
RUN=B/'20260930_hadamard_parity_support_cuts_native_pilot'
SAT=B/'20260930_independent_review/hadamard_parity_support_cuts_sat/summary.json'
ENC=B/'20260930_independent_review/hadamard_parity_support_cuts_encoding/summary.json'
CAL=B/'20260930_independent_review/hadamard_parity_support_cuts_object_calibration/summary.json'
PINS={RUN/'summary.json':'0d036c56c26fd3af0ff27d17566d494c5e514fe5d9221badecd4e41320f2df2a',SAT:'02ae20d479a0d2589c02f435e2a8fdd781ec0459b60095d130b68b5f2721a04a',ENC:'7a9b76b9e139f065c850194b6968ebf4a98c0211668e1f824d2ac75640b7dd12',CAL:'31ee1edda7ac30c17bc1d2287da9c7b81222ad7f50ae761da2e1761199c88eb4'}
read,sha,key,save,need=checker.read,checker.sha,checker.key,checker.save,checker.need

def records_check(summary,receipt,launch,stdout,stderr):
    need(summary['actual_exit_code']==receipt['actual_exit_code']==10 and summary['receipt']==receipt,'actual SAT receipt identity')
    need(summary['research_calls']==1 and summary['automatic_retry']is False and summary['target_resolution']is False,'one attempt, no target claim')
    cmd=receipt['command'];need(cmd==launch['command'],'exact launched command')
    expected=['wsl.exe','--distribution','Ubuntu-24.04','--exec','/usr/bin/timeout','--signal=TERM','--kill-after=5s','60s','/usr/bin/prlimit','--as=4294967296:4294967296','--fsize=10737418240:10737418240','--core=0:0','/mnt/c/Users/ikuto/projects/conway-99-graph/build/research-cadical195/source/build/cadical','--no-binary','-c','100000','/mnt/c/Users/ikuto/projects/conway-99-graph/acceleration/results/20260930_hadamard_parity_support_cuts/instance.cnf',launch['ext4_proof']]
    need(cmd==expected and launch['ext4_proof'].startswith('/tmp/conway99-hadamard-support-cuts-')and launch['ext4_proof'].endswith('/proof.drat'),'all frozen limits, exact binary/input and ext4 proof path')
    need(launch['cnf_sha256']==checker.PINS[checker.D/'instance.cnf'] and launch['model_sha256']==checker.PINS[checker.D/'model.json'],'exact formula launch')
    need(receipt['outer_windows_guard_expired']is False and receipt['outer_windows_guard_seconds']==80 and receipt['linux_process_state']=='WRAPPED_COMMAND_RETURNED','completed process guard')
    need(stderr=='' and re.findall(r'^s .*$',stdout,re.M)==['s SATISFIABLE']and re.findall(r'^c exit (\d+)\s*$',stdout,re.M)==['10'],'literal SAT status and exit')
    need('found \'p cnf 520 4541\' header'in stdout,'actual solver formula dimensions')
    need('Version sc2021'in stdout or 'Version 1.9.5'in stdout or 'version 1.9.5'in stdout or 'c Version 1.9.5'in stdout,'native version1.9.5 log')
    conflicts=re.findall(r'^c conflicts:\s+(\d+)\s',stdout,re.M);cpu=re.findall(r'^c total process time since initialization:\s+([0-9.]+)\s+seconds',stdout,re.M);wall=re.findall(r'^c total real time since initialization:\s+([0-9.]+)\s+seconds',stdout,re.M)
    need(len(conflicts)==len(cpu)==len(wall)==1 and int(conflicts[0])<100000 and float(wall[0])<60 and receipt['wall_seconds']<80,'observed successful run within saved limits')
    return dict(native_exit_code=10,research_calls=1,conflicts=int(conflicts[0]),native_cpu_seconds=float(cpu[0]),native_wall_seconds=float(wall[0]),wrapper_wall_seconds=receipt['wall_seconds'],wall_limit_seconds=60,conflict_limit=100000,address_space_limit_bytes=4294967296,trace_file_limit_bytes=10737418240,outer_guard_seconds=80,native_version='1.9.5')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);pins={}
    def pin(p,h=None):
        v=sha(p);need(h is None or v==h,'input identity '+key(p));pins[key(p)]=v
    try:
        for p,h in PINS.items():pin(p,h)
        summary=read(RUN/'summary.json');manifest=read(RUN/'manifest.json');pin(RUN/'manifest.json')
        for rec in[summary,manifest,read(SAT),read(ENC),read(CAL)]:
            for p,h in{**rec.get('inputs_sha256',{}),**rec.get('outputs_sha256',{})}.items():pin(ROOT/p,h)
        receipt=read(RUN/'main/solver.receipt.json');launch=read(RUN/'main/launch.json');stdout=(RUN/'main/solver.stdout.log').read_text();stderr=(RUN/'main/solver.stderr.log').read_text()
        result=records_check(summary,receipt,launch,stdout,stderr)
        need(sha(ROOT/receipt['stdout'])==receipt['stdout_sha256'] and sha(ROOT/receipt['stderr'])==receipt['stderr_sha256'],'exact raw output receipt bindings')
        proof=RUN/'main/proof.drat';ph=sha(proof);size=proof.stat().st_size
        need(ph==summary['proof_copy']['sha256'] and size==summary['proof_copy']['bytes']==1514570,'entire learned trace identity')
        transfer=(RUN/'main/transfer_hash.stdout.log').read_text().split()
        need(transfer==[ph,launch['ext4_proof']],'source trace exact hash transfer')
        for name in ['transfer_hash','transfer_copy']:
            r=read(RUN/f'main/{name}.receipt.json');need(r['actual_exit_code']==0 and r['outer_windows_guard_expired']is False,'successful artifact transfer')
            for stream in['stdout','stderr']:need(sha(ROOT/r[stream])==r[stream+'_sha256'],'artifact transfer raw stream hash')
        projection=read(SAT.parent/'independent_projection.json');need(len(projection['selected_pattern_indices'])==20 and all(projection['selected_pattern_indices'])and all(r['count']==3 for r in projection['pair_disagreement_counts'])and all(r['satisfied']and not r['selected_constant_groups']and r['disagreement_count']==3 for r in projection['support_cut_checks']),'actual raw all-mixed projection counts')
        rejected=[]
        for case in ['wrong_exit','wrong_conflict_cap','wrong_wall_cap','wrong_input','guard_expired','bad_model_pin','UNSAT_status','missing_log_exit','stderr_error']:
            s,r,l,t,e=deepcopy(summary),deepcopy(receipt),deepcopy(launch),stdout,stderr
            if case=='wrong_exit':r['actual_exit_code']=20;s['receipt']=r;s['actual_exit_code']=20
            elif case in['wrong_conflict_cap','wrong_wall_cap','wrong_input']:
                index={'wrong_conflict_cap':15,'wrong_wall_cap':7,'wrong_input':16}[case];r['command'][index]='WRONG';l['command']=r['command'];s['receipt']=r
            elif case=='guard_expired':r['outer_windows_guard_expired']=True;s['receipt']=r
            elif case=='bad_model_pin':l['model_sha256']='0'*64
            elif case=='UNSAT_status':t=t.replace('s SATISFIABLE','s UNSATISFIABLE')
            elif case=='missing_log_exit':t=t.replace('c exit 10','c no_exit_record')
            else:e='simulated error'
            try:records_check(s,r,l,t,e)
            except ValueError as err:rejected.append(dict(case=case,reason=str(err)))
            else:raise ValueError('corrupt outcome accepted '+case)
        save(out/'controls.json',dict(positive_scope='Authentic completed SAT run, whose raw assignment has a separate full-object PASS.',rejected=rejected))
        command=['wsl.exe','--distribution','Ubuntu-24.04','--exec','/usr/bin/ps','-C','cadical','-o','pid=,args='];ps=subprocess.run(command,capture_output=True,text=True)
        need(ps.returncode in(0,1),'read-only process snapshot available');matches=[line for line in ps.stdout.splitlines()if '20260930_hadamard_parity_support_cuts/instance.cnf'in line]
        save(out/'process_observation.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),command=command,exit_code=ps.returncode,exact_input_matches=matches,stderr=ps.stderr,scope='Current CaDiCaL process lines for this exact input only; no inference about other research.'))
        for p in[Path(__file__),Path(checker.__file__),ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(p)
        now=datetime.now(timezone.utc).isoformat();record=dict(status='INDEPENDENT_HADAMARD_PARITY_SUPPORT_CUT_SAT_OUTCOME_PASS',timestamp=now,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,outputs_sha256={key(p):sha(p)for p in out.iterdir()if p.is_file()},verifier='/root/state_literature_audit',method='Independent saved command/status/log/transfer authentication, separate frozen full-object gate',result=result,selected_groups=20,nonconstant_groups=20,constant_groups=0,coordinate_pair_disagreement_counts_all_three=60,raw_support_cut_checks=60,learned_trace=dict(sha256=ph,bytes=size,classification='SAT-run learned trace; not an UNSAT certificate',proof_checker_called=False),corrupted_controls_rejected=len(rejected),fresh_exact_input_process_matches=len(matches),artifact_availability='LOCAL_ONLY',target_resolution=False,solver_calls_by_this_audit=0,limitations=['Only the strengthened parity projection is constructed. No full Gram factor, outside adjacency or residual D is supplied.','Native times and conflict counts are telemetry for one attempt, not a performance guarantee.','No mathematical exclusion; a SAT learned trace is not used as proof.'])
        save(out/'summary.json',record)
        encoding=read(ENC.parent/'claim_binding.json')
        encoding.update(artifact_availability='LOCAL_ONLY',verification_records=[dict(claim_id=encoding['id'],claim_revision=1,verifier='/root/state_literature_audit',method='Independent exact full-CNF reconstruction and proved-clause mapping',report_path=key(ENC),report_sha256=PINS[ENC],outcome='PASS',timestamp=read(ENC)['timestamp'],scope='Necessary strengthened projection with explicit balanced support, full Gram and outside-column caps; no converse factor construction.')])
        sid='C-FIXED-HADAMARD-SIX-PRISM-SUPPORT-CUT-PARITY-SAT-WITNESS'
        witness=dict(id=sid,revision=1,statement='The authenticated saved 520-variable assignment satisfies all 4541 clauses of the strengthened support-cut parity formula and decodes to twenty nonconstant group patterns, all sixty coordinate-pair disagreement counts equal to three, and all sixty raw-pattern support cuts satisfied.',kind='construction',basis=['COMPUTED'],recommendation='VERIFIED',review_state='CLEAR',scope='One exact parity-projection witness on the fixed support; not a full Gram factor or graph.',assumptions=['Exact assignment, CNF, model and raw-projection hashes bound in the independent object gate.','No nontrivial target automorphism is assumed.'],dependencies=[dict(id=encoding['id'],revision=1,relation='encoding_equivalence')],evidence=[dict(path=key(SAT),sha256=PINS[SAT],availability='LOCAL_ONLY'),dict(path=key(CAL),sha256=PINS[CAL],availability='LOCAL_ONLY'),dict(path=key(out/'summary.json'),sha256=sha(out/'summary.json'),availability='LOCAL_ONLY')],verification_records=[dict(claim_id=sid,claim_revision=1,verifier='/root/state_literature_audit',method='Independent complete native/JSON assignment, all actual clauses and raw pattern checks',report_path=key(SAT),report_sha256=PINS[SAT],timestamp=read(SAT)['timestamp'],outcome='PASS',scope='Every520 assignment ID, every4541 actual clause, all20 patterns/all60 disagreements/all60 support cuts and producer decoded comparison.',shared_components=read(SAT)['shared_components'])],limitations=['No converse from parity SAT to a full Gram factor, full column caps, or residual D.','The earlier cyclic exclusion is a premise for necessity of the formula, not evidence that this witness lifts.','The old projection remains a valid witness for its old formula.','No external review or novelty claim.'],artifact_availability='LOCAL_ONLY',created_at=now,updated_at=now)
        save(out/'claim_bindings.json',dict(timestamp=now,encoding=encoding,projection_witness=witness,ledger_modified=False))
        print(json.dumps(dict(status=record['status'],summary_sha256=sha(out/'summary.json'),claim_bindings_sha256=sha(out/'claim_bindings.json'))))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e)));raise

if __name__=='__main__':main()
