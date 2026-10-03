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
D=ROOT/'acceleration/results/20260930_prism_all_columns_native_pilot'
INPUT='acceleration/results/20260930_prism_all_columns/instance.cnf'
TRACE_SHA='c00ce180a9a0e6e9a2ad9e3ed4fe63f98641e7538fbe71cdf612ac059733c37b'
TRACE_BYTES=720744448
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
    need(lines.count('c UNKNOWN')==1 and not any(x.startswith('s ') for x in lines),'explicit UNKNOWN without SAT/UNSAT status')
    need(receipt['actual_exit_code']==124 and receipt['outer_windows_guard_expired'] is False,'GNU timeout124, not outer Windows guard')
    need('c caught signal 15 (SIGTERM)' in lines and lines[-1]=='c raising signal 15 (SIGTERM)','native termination signal observed')
    need("c found 'p cnf 245880 874800' header" in lines,'actual exact input dimensions')
    need('c Version 1.9.5 146207318796f094dcded87349a64f0c6927309e' in lines,'exact native version')
    need('c setting conflict limit to 1000000 conflicts' in text,'configured conflict cap')
    need(re.findall(r'^c conflicts:\s+(\d+)\s',text,re.M)==['817260'],'observed conflicts below conflict cap')
    need(re.findall(r'^c total real time since initialization:\s+([0-9.]+)\s+seconds',text,re.M)==['299.99'],'observed native wall time')
    need(re.findall(r'^c total process time since initialization:\s+([0-9.]+)\s+seconds',text,re.M)==['296.68'],'observed native CPU time')
    need(300<=receipt['wall_seconds']<305,'configured300second deadline observed')
    return dict(result='UNKNOWN_GNU_TIMEOUT_SIGTERM',wrapper_exit_code=124,configured_conflict_limit=1000000,observed_final_conflicts=817260,conflict_cap_reached=False,native_real_seconds='299.99',native_process_seconds='296.68',wrapper_wall_seconds=receipt['wall_seconds'],native_exit_code=None,native_exit_code_null_reason='Solver ended through SIGTERM;124is the GNU timeout wrapper outcome, not a SAT/UNSAT solver result.')
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
        need(summary['receipt']==receipt and summary['actual_exit_code']==124 and summary['research_calls']==1 and summary['automatic_retry'] is False,'exact single completed attempt')
        need(receipt['command']==launch['command'],'exact launch/receipt invocation')
        command=receipt['command'];need(command[command.index('-c')+1]=='1000000' and '300s' in command and '--kill-after=5s' in command and '--as=4294967296:4294967296' in command and '--fsize=10737418240:10737418240' in command and '--core=0:0' in command,'configured native wrapper resources')
        need(manifest['limits']==dict(native_seconds=300,conflicts=1000000,address_space_bytes=4294967296,file_bytes=10737418240,kill_after_seconds=5,outer_windows_guard_seconds=320),'exact saved configured limits')
        need(launch['cnf_sha256']==manifest['inputs_sha256'][INPUT] and any(x.endswith('/'+INPUT) for x in command),'exact launched input identity')
        text=bind(ROOT/receipt['stdout'],receipt['stdout_sha256']).read_text();need(bind(ROOT/receipt['stderr'],receipt['stderr_sha256']).read_bytes()==b'','empty native stderr')
        parsed=outcome(text,receipt);rejected=[]
        controls=[('false_UNSAT',text.replace('c UNKNOWN','s UNSATISFIABLE'),receipt),('false_exit20',text,{**receipt,'actual_exit_code':20}),('changed_observed_conflicts',re.sub(r'(^c conflicts:\s+)\d+',r'\g<1>1000000',text,flags=re.M),receipt),('missing_final_signal',text.rsplit('c raising signal 15 (SIGTERM)',1)[0],receipt),('wall_guard_expired',text,{**receipt,'outer_windows_guard_expired':True})]
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
        save(args.out/'process_observation.json',process);bind(ROOT/'acceleration/audit_20260930_triangle_column_cap_factor_unknown.py','3ccf10f4c0a519886bef1d41afcbfcff071948583dbdc8af4ae19cf5c395b0a8');bind(__file__)
        # Recheck small inputs, without repeating the already complete 720MB hash.
        need(all(digest(ROOT/p)==v for p,v in bindings.items() if p!=key(trace)),'stable input/output receipts')
        report=dict(status='INDEPENDENT_SIX_PRISM_ALL_COLUMNS_UNKNOWN_RUN_AUDIT_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,
          verifier='/root/eight_domain_audit independent raw log/receipt/full-trace identity checker',shared_components=['Frozen receipt/identity audit scaffolding reused; new explicit GNU timeout and SIGTERM interpretation. No producer imports.'],recommendation='VERIFIED',review_state='CLEAR',kind='empirical/engineering result',basis=['COMPUTED'],actual_attempts=1,completed_UNKNOWN=1,SAT_objects=0,checked_UNSAT_proofs=0,
          run_source_commit=manifest['source_commit'],run_command=manifest['command'],native_command=command,configured_limits=manifest['limits'],outcome=parsed,solver_version='CaDiCaL1.9.5 146207318796f094dcded87349a64f0c6927309e',solver_binary_sha256=manifest['inputs_sha256']['build/research-cadical195/source/build/cadical'],
          partial_trace=dict(path=key(trace),bytes=TRACE_BYTES,sha256=TRACE_SHA,fresh_complete_local_hash=True,hash_and_other_output_checks_seconds=fresh_hash_seconds,availability='LOCAL_ONLY',retrieval='Existing local run main/proof.drat; not committed as a proof artifact.',proof_checked=False,unsat_certificate=False),
          corrupted_controls_rejected=rejected,current_process_observation=process,scope='One wall-capped native attempt on the fixed six-prism abstract factor model; column caps and residual D absent.',
          limitations=['UNKNOWN establishes no feasibility or exclusion result.','The complete local bytes of a partial trace are authenticated, but no proof checker was invoked and no UNSAT certificate is claimed.','Recorded resource caps are configured limits, not measurements of peak memory or proof completeness.','No performance comparison with different formulas is inferred.'],target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY',elapsed_seconds=time.monotonic()-start)
        save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))
    except BaseException as e:save(args.out/'failure.json',dict(status='AUDIT_FAILED',error=repr(e)));raise

if __name__=='__main__':main()
