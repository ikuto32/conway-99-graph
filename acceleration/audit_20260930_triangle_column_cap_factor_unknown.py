"""Independent saved capped run audit; full partial-trace hash, no proof claim."""
import argparse
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import platform
import re
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'acceleration/results/20260930_triangle_column_cap_factor_native_pilot'
INPUT='acceleration/results/20260930_triangle_factor_column_caps/instance.cnf'
TRACE_SHA='ef85eb33ba7188f2a0db5030f15268a92bd4b966f4c0cad8b4432455d4b236f5'
TRACE_BYTES=657451587
def need(ok,message):
    if not ok:raise ValueError(message)
def digest(p):
    h=sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda:f.read(1<<20),b''):h.update(block)
    return h.hexdigest()
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def save(p,x):
    with Path(p).open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')

def outcome(text,receipt):
    lines=text.splitlines()
    need(lines.count('c UNKNOWN')==1 and not any(x.startswith('s ') for x in lines),'unique UNKNOWN and no SAT/UNSAT status')
    need(receipt['actual_exit_code']==0 and receipt['outer_windows_guard_expired'] is False and lines[-1]=='c exit 0','completed normal native UNKNOWN')
    need("c found 'p cnf 61296 256320' header" in lines,'observed input dimensions')
    need('c Version 1.9.5 146207318796f094dcded87349a64f0c6927309e' in lines,'exact native version')
    need('c setting conflict limit to 1000000 conflicts' in text,'configured conflict cap')
    need(re.findall(r'^c conflicts:\s+(\d+)\s',text,re.M)==['1000001'],'observed final conflict count and overshoot')
    need(re.findall(r'^c DRAT (\d+) bytes',text,re.M)==[str(TRACE_BYTES)],'observed partial trace length')
    need(re.findall(r'^c total real time since initialization:\s+([0-9.]+)\s+seconds',text,re.M)==['83.17'],'observed native real time')
    need(re.findall(r'^c total process time since initialization:\s+([0-9.]+)\s+seconds',text,re.M)==['82.17'],'observed native CPU time')
    need(receipt['wall_seconds']<300,'no configured wall deadline reached')
    return dict(result='UNKNOWN_NATIVE_CONFLICT_CAP',configured_conflict_limit=1000000,observed_final_conflicts=1000001,conflict_overshoot=1,native_real_seconds='83.17',native_process_seconds='82.17',wrapper_wall_seconds=receipt['wall_seconds'])

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();bindings={}
    def bind(p,expected=None):
        p=Path(p);v=digest(p);need(expected is None or v==expected,'exact artifact hash '+str(p));bindings[key(p)]=v;return p
    def read(p):return json.loads(bind(p).read_bytes())
    try:
        manifest=read(D/'manifest.json');summary=read(D/'summary.json');receipt=read(D/'main/solver.receipt.json');launch=read(D/'main/launch.json')
        for p,v in manifest['inputs_sha256'].items():bind(ROOT/p,v)
        trace=D/'main/proof.drat';hash_start=time.monotonic()
        for p,v in summary['outputs_sha256'].items():bind(ROOT/p,v)
        fresh_hash_seconds=time.monotonic()-hash_start
        need(bindings[key(trace)]==TRACE_SHA and trace.stat().st_size==TRACE_BYTES,'complete fresh local partial-trace hash/length')
        need(summary['receipt']==receipt and summary['actual_exit_code']==0 and summary['research_calls']==1 and summary['automatic_retry'] is False,'exact single completed attempt')
        need(receipt['command']==launch['command'],'exact launch/receipt invocation')
        command=receipt['command'];need(command[command.index('-c')+1]=='1000000' and '300s' in command and '--kill-after=5s' in command and '--as=4294967296:4294967296' in command and '--fsize=10737418240:10737418240' in command and '--core=0:0' in command,'configured native wrapper resources')
        need(manifest['limits']==dict(native_seconds=300,conflicts=1000000,address_space_bytes=4294967296,file_bytes=10737418240,kill_after_seconds=5,outer_windows_guard_seconds=320),'exact saved configured limits')
        need(launch['cnf_sha256']==manifest['inputs_sha256'][INPUT] and any(x.endswith('/'+INPUT) for x in command),'exact launched input identity')
        text=bind(ROOT/receipt['stdout'],receipt['stdout_sha256']).read_text();need(bind(ROOT/receipt['stderr'],receipt['stderr_sha256']).read_bytes()==b'','empty native stderr')
        parsed=outcome(text,receipt);rejected=[]
        controls=[('false_UNSAT',text.replace('c UNKNOWN','s UNSATISFIABLE'),receipt),('false_exit20',text,{**receipt,'actual_exit_code':20}),('changed_observed_conflicts',re.sub(r'(^c conflicts:\s+)\d+',r'\g<1>1000000',text,flags=re.M),receipt),('missing_final_exit',text.rsplit('c exit 0',1)[0],receipt),('wall_guard_expired',text,{**receipt,'outer_windows_guard_expired':True})]
        for name,badtext,badreceipt in controls:
            try:outcome(badtext,badreceipt)
            except ValueError:rejected.append(name)
            else:raise ValueError('corrupted outcome accepted '+name)
        copy=summary['proof_copy'];need(copy['sha256']==TRACE_SHA and copy['bytes']==TRACE_BYTES,'producer transfer identities agree')
        hr=read(D/'main/transfer_hash.receipt.json');cr=read(D/'main/transfer_copy.receipt.json')
        need(copy['native_hash_receipt']==hr and copy['copy_receipt']==cr,'complete transfer receipts')
        for r in [hr,cr,manifest['filesystem_receipt'],manifest['ext4_disk_receipt']]:
            need(r['actual_exit_code']==0 and r['outer_windows_guard_expired'] is False,'successful recorded supporting command')
            for channel in ['stdout','stderr']:bind(ROOT/r[channel],r[channel+'_sha256'])
        need((ROOT/hr['stdout']).read_text().split()==[TRACE_SHA,copy['linux_source']],'native sha256sum output')
        need(not (D/'main/parsed_model.json').exists() and not (D/'main/decoded_factor.json').exists(),'no saved SAT object')
        ps_command=['wsl.exe','--distribution','Ubuntu-24.04','--exec','/usr/bin/ps','-eo','pid,args'];ps=subprocess.run(ps_command,capture_output=True,text=True,timeout=20);need(ps.returncode==0,'fresh read-only process observation')
        matches=[line.strip() for line in ps.stdout.splitlines() if '/'+INPUT in line]
        process=dict(timestamp=datetime.now(timezone.utc).isoformat(),command=ps_command,matching_exact_input_processes=matches)
        save(args.out/'process_observation.json',process);bind(__file__)
        # Recheck small inputs, without repeating the already complete 657MB hash.
        need(all(digest(ROOT/p)==v for p,v in bindings.items() if p!=key(trace)),'stable input/output receipts')
        report=dict(status='INDEPENDENT_TRIANGLE_COLUMN_CAP_FACTOR_UNKNOWN_RUN_AUDIT_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,
          verifier='/root/eight_domain_audit independent raw log/receipt/full-trace identity checker',recommendation='VERIFIED',review_state='CLEAR',kind='empirical/engineering result',basis=['COMPUTED'],actual_attempts=1,completed_UNKNOWN=1,SAT_objects=0,checked_UNSAT_proofs=0,
          run_source_commit=manifest['source_commit'],run_command=manifest['command'],native_command=command,configured_limits=manifest['limits'],outcome=parsed,solver_version='CaDiCaL1.9.5 146207318796f094dcded87349a64f0c6927309e',solver_binary_sha256=manifest['inputs_sha256']['build/research-cadical195/source/build/cadical'],
          partial_trace=dict(path=key(trace),bytes=TRACE_BYTES,sha256=TRACE_SHA,fresh_complete_local_hash=True,hash_and_other_output_checks_seconds=fresh_hash_seconds,availability='LOCAL_ONLY',retrieval='Existing local run main/proof.drat; not committed as a proof artifact.',proof_checked=False,unsat_certificate=False),
          corrupted_controls_rejected=rejected,current_process_observation=process,scope='One recorded conflict-capped attempt on full36 binary factors with target column caps for one fixed39core, residual D absent.',
          limitations=['UNKNOWN establishes no feasibility or exclusion result.','The complete local bytes of a partial trace are authenticated, but no proof checker was invoked and no UNSAT certificate is claimed.','Recorded resource caps are configured limits, not measurements of peak memory or proof completeness.','No performance comparison with different formulas is inferred.'],target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY',elapsed_seconds=time.monotonic()-start)
        save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))
    except BaseException as e:save(args.out/'failure.json',dict(status='AUDIT_FAILED',error=repr(e)));raise

if __name__=='__main__':main()
