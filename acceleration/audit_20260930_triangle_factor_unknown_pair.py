"""Bind two completed UNKNOWN attempts; partial trace hashes are receipts only."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import re
import subprocess
import sys
from audit_20260930_triangle_joint_factor_unknown import need,digest,key,save

ROOT=Path(__file__).resolve().parents[1]
CASES=[dict(name='base',run='20260930_triangle_joint_factor_native_pilot',input='20260930_triangle_joint_factor_cnf',variables=58860,clauses=203748,conflicts=1000000,real='69.55',cpu='68.81',bytes=574434634,trace='46fd17658f8656d56d33736e78e6d1b3dc1dab13c18bf6f08a80dd05637e5b59'),dict(name='component_strengthened',run='20260930_triangle_component_factor_native_pilot',input='20260930_triangle_factor_components',variables=61296,clauses=212580,conflicts=1000002,real='81.39',cpu='80.62',bytes=646423799,trace='727a3bab407ea9e21d58c2e4d89a1fab5ad8787a839c883ade01d2072f7395c7')]

def status_check(text,receipt,case):
    lines=text.splitlines()
    need(lines.count('c UNKNOWN')==1 and not any(x.startswith('s ') for x in lines),'unique UNKNOWN without SAT/UNSAT')
    need(receipt['actual_exit_code']==0 and not receipt['outer_windows_guard_expired'] and lines[-1]=='c exit 0','normal UNKNOWN exit')
    need('c setting conflict limit to 1000000 conflicts' in text,'actual configured conflict cap')
    need(re.findall(r'^c conflicts:\s+(\d+)\s',text,re.M)==[str(case['conflicts'])],'actual conflict count including overshoot')
    need("c found 'p cnf %d %d' header"%(case['variables'],case['clauses']) in lines,'actual input dimensions')
    need(re.findall(r'^c DRAT (\d+) bytes',text,re.M)==[str(case['bytes'])],'actual partial trace byte count')
    need(re.findall(r'^c total real time since initialization:\s+([0-9.]+)\s+seconds',text,re.M)==[case['real']],'actual real time')
    need(re.findall(r'^c total process time since initialization:\s+([0-9.]+)\s+seconds',text,re.M)==[case['cpu']],'actual CPU time')
    need('c Version 1.9.5 146207318796f094dcded87349a64f0c6927309e' in lines,'exact solver version')
    need(receipt['wall_seconds']<300,'no wall timeout')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False);bindings={};results=[];controls=[]
    def bind(path,expected=None):
        path=Path(path);need(path.name!='proof.drat','partial trace not rehashed')
        value=digest(path);need(expected is None or value==expected,'hash mismatch '+str(path));bindings[key(path)]=value;return path
    def read(path):return json.loads(bind(path).read_bytes())
    try:
        for case in CASES:
            d=ROOT/'acceleration/results'/case['run'];m=read(d/'manifest.json');s=read(d/'summary.json');r=read(d/'main/solver.receipt.json');launch=read(d/'main/launch.json')
            for p,v in m['inputs_sha256'].items():bind(ROOT/p,v)
            trace=d/'main/proof.drat'
            for p,v in s['outputs_sha256'].items():
                if p==key(trace):need(v==case['trace'],'saved trace output hash')
                else:bind(ROOT/p,v)
            need(s['receipt']==r and s['actual_exit_code']==0 and s['research_calls']==1 and s['automatic_retry'] is False,'exact single completed attempt')
            need(r['command']==launch['command'],'exact native command receipt')
            command=r['command'];need(command[command.index('-c')+1]=='1000000' and '300s' in command and '--as=4294967296:4294967296' in command and '--fsize=10737418240:10737418240' in command,'actual resource invocation')
            need(m['limits']['conflicts']==1000000 and m['limits']['native_seconds']==300,'matching resource manifest')
            cnf='acceleration/results/'+case['input']+'/instance.cnf'
            need(launch['cnf_sha256']==m['inputs_sha256'][cnf] and any(x.endswith('/'+cnf) for x in command),'exact input pathname and identity')
            for channel in ['stdout','stderr']:bind(ROOT/r[channel],r[channel+'_sha256'])
            text=(ROOT/r['stdout']).read_text();need((ROOT/r['stderr']).read_bytes()==b'','empty stderr');status_check(text,r,case)
            for label,badtext,badr in [('false_UNSAT',text.replace('c UNKNOWN','s UNSATISFIABLE'),r),('false_exit',text,{**r,'actual_exit_code':20}),('wrong_final_conflicts',re.sub(r'(^c conflicts:\s+)\d+',r'\g<1>999999',text,flags=re.M),r)]:
                try:status_check(badtext,badr,case)
                except ValueError:controls.append(case['name']+':'+label)
                else:raise ValueError('corrupt run accepted '+label)
            copy=s['proof_copy'];need(copy['sha256']==case['trace'] and copy['bytes']==case['bytes']==trace.stat().st_size,'recorded trace identity and current size')
            hr=read(d/'main/transfer_hash.receipt.json');cr=read(d/'main/transfer_copy.receipt.json')
            need(copy['native_hash_receipt']==hr and copy['copy_receipt']==cr,'original complete transfer receipts')
            for rr in [hr,cr]:
                need(rr['actual_exit_code']==0 and not rr['outer_windows_guard_expired'],'successful transfer')
                for channel in ['stdout','stderr']:bind(ROOT/rr[channel],rr[channel+'_sha256'])
            need((ROOT/hr['stdout']).read_text().split()==[case['trace'],copy['linux_source']],'native hash command output')
            need(copy['windows_hash_wall_seconds']>0,'original subsequent destination hash recorded')
            need(not (d/'main/parsed_model.json').exists() and not (d/'main/decoded_factor.json').exists(),'no saved SAT object')
            results.append(dict(case=case['name'],run_manifest=key(d/'manifest.json'),run_summary=key(d/'summary.json'),source_commit=m['source_commit'],command=m['command'],native_command=command,limits=m['limits'],result='UNKNOWN_NATIVE_CONFLICT_CAP',native_exit_code=0,configured_conflict_limit=1000000,observed_final_conflicts=case['conflicts'],observed_conflict_overshoot=case['conflicts']-1000000,reported_native_real_seconds=case['real'],reported_native_process_seconds=case['cpu'],wrapper_wall_seconds=r['wall_seconds'],solver_version='CaDiCaL1.9.5 146207318796f094dcded87349a64f0c6927309e',partial_trace=dict(path=key(trace),bytes=case['bytes'],recorded_sha256=case['trace'],availability='LOCAL_ONLY',fresh_trace_hash=False,hash_basis='Authenticated original native sha256sum stdout and recorded Windows destination hash; current size checked. No repeated fulltrace hash.',proof_checked=False,unsat_certificate=False)))
        baseaudit=ROOT/'acceleration/results/20260930_independent_review/triangle_joint_factor_unknown/summary.json'
        bind(baseaudit,'f98f30d5279951c430b491ab8615b6d9f52b2f6c6d9e65b48adac50039ce0d44')
        pscommand=['wsl.exe','--distribution','Ubuntu-24.04','--exec','/usr/bin/ps','-eo','pid,args'];p=subprocess.run(pscommand,capture_output=True,text=True,timeout=20);need(p.returncode==0,'current process read')
        observations={case['name']:[line.strip() for line in p.stdout.splitlines() if '/acceleration/results/'+case['input']+'/instance.cnf' in line] for case in CASES}
        bind(__file__);bind(ROOT/'acceleration/audit_20260930_triangle_joint_factor_unknown.py')
        report=dict(status='INDEPENDENT_TRIANGLE_FACTOR_TWO_UNKNOWN_RUNS_AUDIT_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,verifier='/root/eight_domain_audit separate raw log/receipt checker',actual_attempts=2,completed_UNKNOWN=2,SAT_objects=0,checked_UNSAT_proofs=0,runs=results,corrupted_controls_rejected=controls,current_process_observation=dict(timestamp=datetime.now(timezone.utc).isoformat(),command=pscommand,matches_by_exact_input=observations),recommendation='VERIFIED',kind='empirical/engineering result',basis=['COMPUTED'],review_state='CLEAR',scope='Two saved capped native attempts on the same fixed-core factor family, with and without entailed component equations.',artifact_availability='LOCAL_ONLY',limitations=['Both mathematical feasibility questions remain unresolved by these attempts.','No partial trace is a claimed proof; complete trace bytes were not freshly rehashed.','Two distinct formula runs are not a controlled performance comparison.','Conflict limits are configured1,000,000; strengthened actual final count is1,000,002.'],target_resolution=False,external_review=False)
        save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))
    except BaseException as e:save(args.out/'failure.json',dict(status='AUDIT_FAILED',error=repr(e)));raise

if __name__=='__main__':main()
