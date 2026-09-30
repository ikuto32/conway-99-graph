"""Record the authorized contained four-build invocation and actual terminal receipt."""
import argparse,hashlib,json,platform,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];B='acceleration/results/20260930_'
LAUNCHER='acceleration/run_20260930_exact_eight_four_builds_v2.py'
PLAN=B+'exact_eight_next64_launch_preparation/launch_plan.json'
OUT=B+'exact_eight_next64_launch_execution';CHILD=B+'exact_eight_next64_build_launcher'
def h(p):
    with(ROOT/p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,x):
    with(ROOT/p).open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--engineering-gate',required=True);ap.add_argument('--engineering-gate-sha256',required=True);args=ap.parse_args()
    assert h(LAUNCHER)=='11715c9438dc8749a80f62b5ee69646dbccee194c53a1a56ded1bff83a5601e8'
    assert h(PLAN)=='8306b8d9111bc6defedb336fd8de5392867b02e22c5ac57edb3df30def6b0ec9'
    assert h(args.engineering_gate)==args.engineering_gate_sha256
    assert not(ROOT/OUT).exists()and not(ROOT/CHILD).exists();(ROOT/OUT).mkdir()
    command=[sys.executable,'-B',LAUNCHER,'build','--launch-plan',PLAN,'--launch-plan-sha256',h(PLAN),'--engineering-gate',args.engineering_gate,'--engineering-gate-sha256',args.engineering_gate_sha256,'--out',CHILD]
    save(OUT+'/manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],child_command=command,cwd=str(ROOT),python=platform.python_version(),platform=platform.platform(),inputs_sha256={p:h(p)for p in[LAUNCHER,PLAN,args.engineering_gate,'uv.lock','pyproject.toml',Path(__file__).relative_to(ROOT).as_posix()]},allocation=dict(partitions=4,cases_per_partition=16,build_seconds_per_partition=120,aggregate_allocated_build_seconds=480,maximum_concurrent_builders=4),native_calls=0,scope='Engineering execution provenance only; actual formulas await complete independent checking.'))
    start=time.monotonic()
    with(ROOT/(OUT+'/stdout.log')).open('xb')as stdout,(ROOT/(OUT+'/stderr.log')).open('xb')as stderr:
        p=subprocess.Popen(command,cwd=ROOT,stdout=stdout,stderr=stderr)
        save(OUT+'/launched.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),owned_launcher_pid=p.pid,command=command))
        last=start
        while p.poll()is None:
            time.sleep(1)
            if time.monotonic()-last>=15:
                print(json.dumps(dict(observed_at=datetime.now(timezone.utc).isoformat(),owned_launcher_pid=p.pid,process_state='RUNNING_OBSERVED'if p.poll()is None else'TERMINAL_OBSERVED',elapsed_seconds=round(time.monotonic()-start,3))),flush=True);last=time.monotonic()
    files=[OUT+'/manifest.json',OUT+'/launched.json',OUT+'/stdout.log',OUT+'/stderr.log']
    for name in['summary.json','failure.json']:
        q=CHILD+'/'+name
        if(ROOT/q).is_file():files.append(q)
    save(OUT+'/summary.json',dict(status='FOUR_BUILD_LAUNCHER_RETURNED'if p.returncode==0 else'FOUR_BUILD_LAUNCHER_FAILED',timestamp=datetime.now(timezone.utc).isoformat(),actual_exit_code=p.returncode,end_to_end_wall_seconds=time.monotonic()-start,owned_launcher_pid=p.pid,outputs_sha256={q:h(q)for q in files},native_calls=0,mathematical_approval=False,limitations=['Elapsed time includes process preparation, cleanup and artifact hashing; not kernel time or a speedup measurement.','Exit zero alone does not establish complete formulas or their correctness; inspect each child receipt and independent gate.']))
    print(json.dumps(dict(exit_code=p.returncode,summary_sha256=h(OUT+'/summary.json'))),flush=True)
    raise SystemExit(p.returncode)
if __name__=='__main__':main()
