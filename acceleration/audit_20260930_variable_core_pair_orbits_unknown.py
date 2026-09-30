"""Independent receipt/complete partial-trace identity audit for the complete ordered-pair UNKNOWN run.

Shares receipt auditing conventions with the prior independent six-prism run
checker, not any producer import or mathematical encoding implementation.
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import platform
import re
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]

def need(ok,message):
    if not ok: raise ValueError(message)

def digest(p):
    h=sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda:f.read(1<<20),b''): h.update(block)
    return h.hexdigest()

def key(p): return Path(p).resolve().relative_to(ROOT).as_posix()

def save(p,x):
    with Path(p).open('x',encoding='utf-8',newline='\n') as f: json.dump(x,f,indent=2); f.write('\n')

def outcome(text,receipt,cfg):
    lines=text.splitlines()
    need(lines.count('c UNKNOWN')==1 and not any(x.startswith('s ') for x in lines),'explicit UNKNOWN without SAT/UNSAT status')
    need(receipt['actual_exit_code']==cfg['exit'] and receipt['outer_windows_guard_expired'] is False,'actual wrapper exit and no expired outer guard')
    need(f"c found 'p cnf {cfg['variables']} {cfg['clauses']}' header" in lines,'exact input dimensions')
    need('c Version 1.9.5 146207318796f094dcded87349a64f0c6927309e' in lines,'native version')
    need('c setting conflict limit to 5000000 conflicts' in text,'configured conflict cap')
    need(re.findall(r'^c conflicts:\s+(\d+)\s',text,re.M)==[str(cfg['conflicts'])],'actual conflicts')
    need(re.findall(r'^c total real time since initialization:\s+([0-9.]+)\s+seconds',text,re.M)==[cfg['real']],'actual native real time')
    need(re.findall(r'^c total process time since initialization:\s+([0-9.]+)\s+seconds',text,re.M)==[cfg['cpu']],'actual native CPU time')
    if cfg['exit']==124:
        need('c caught signal 15 (SIGTERM)' in lines and lines[-1]=='c raising signal 15 (SIGTERM)','explicit SIGTERM termination')
        need(900<=receipt['wall_seconds']<905,'configured deadline observed')
        result='UNKNOWN_GNU_TIMEOUT_SIGTERM'; native_exit=None
    else:
        need(lines[-1]=='c exit 0' and not any('caught signal' in x for x in lines),'native exit0 without signal')
        need(872<=receipt['wall_seconds']<874 and cfg['conflicts']>=5000000,'native conflict cap reached')
        result='UNKNOWN_NATIVE_CONFLICT_CAP'; native_exit=0
    return dict(result=result,wrapper_exit_code=cfg['exit'],native_exit_code=native_exit,native_exit_code_null_reason='GNU timeout124 records wrapper SIGTERM outcome, not a native SAT/UNSAT exit.' if native_exit is None else None,configured_conflict_limit=5000000,observed_final_conflicts=cfg['conflicts'],conflict_cap_reached=cfg['conflicts']>=5000000,native_real_seconds=cfg['real'],native_process_seconds=cfg['cpu'],wrapper_wall_seconds=receipt['wall_seconds'])

def run(cfg,entry):
    ap=argparse.ArgumentParser(); ap.add_argument('--out',type=Path,required=True); args=ap.parse_args(); args.out.mkdir(parents=True,exist_ok=False); start=time.monotonic(); bindings={}
    directory=ROOT/cfg['directory']; input_key=cfg['input']
    def bind(p,expected=None):
        p=Path(p); value=digest(p); need(expected is None or value==expected,'exact artifact hash '+str(p)); bindings[key(p)]=value; return p
    def read(p,expected=None): return json.loads(bind(p,expected).read_bytes())
    try:
        manifest=read(directory/'manifest.json'); summary=read(directory/'summary.json',cfg['summary_sha256']); receipt=read(directory/'main/solver.receipt.json'); launch=read(directory/'main/launch.json')
        for path,sha in manifest['inputs_sha256'].items(): bind(ROOT/path,sha)
        trace=directory/'main/proof.drat'; hash_start=time.monotonic()
        for path,sha in summary['outputs_sha256'].items(): bind(ROOT/path,sha)
        fresh_hash_seconds=time.monotonic()-hash_start
        need(bindings[key(trace)]==cfg['trace_sha256'] and trace.stat().st_size==cfg['trace_bytes'],'fresh complete partial-trace hash and length')
        need(summary['receipt']==receipt and summary['actual_exit_code']==cfg['exit'] and summary['research_calls']==1 and summary['automatic_retry'] is False,'single actual attempt')
        need(receipt['command']==launch['command'],'launch/receipt invocation identity')
        command=receipt['command']
        need(command[command.index('-c')+1]=='5000000' and '900s' in command and '--kill-after=5s' in command and '--as=4294967296:4294967296' in command and '--fsize=10737418240:10737418240' in command and '--core=0:0' in command,'native resource flags')
        required=dict(native_seconds=900,conflicts=5000000,address_space_bytes=4294967296,file_bytes=10737418240,kill_after_seconds=5,outer_windows_guard_seconds=920)
        need(all(manifest['limits'][k]==v for k,v in required.items()),'configured saved limits')
        need(launch['cnf_sha256']==manifest['inputs_sha256'][input_key] and any(x.endswith('/'+input_key) for x in command),'actual launched input')
        text=bind(ROOT/receipt['stdout'],receipt['stdout_sha256']).read_text(); need(bind(ROOT/receipt['stderr'],receipt['stderr_sha256']).read_bytes()==b'','empty stderr')
        parsed=outcome(text,receipt,cfg); rejected=[]
        controls=[('false_UNSAT',text.replace('c UNKNOWN','s UNSATISFIABLE'),receipt),('false_exit20',text,{**receipt,'actual_exit_code':20}),('changed_conflicts',re.sub(r'(^c conflicts:\s+)\d+',r'\g<1>1',text,flags=re.M),receipt),('missing_termination',text.rsplit(lines_last:=text.splitlines()[-1],1)[0],receipt),('outer_guard',text,{**receipt,'outer_windows_guard_expired':True}),('wrong_dimensions',text.replace(f"p cnf {cfg['variables']} {cfg['clauses']}",f"p cnf {cfg['variables']} 1"),receipt)]
        for name,badtext,badreceipt in controls:
            try: outcome(badtext,badreceipt,cfg)
            except ValueError: rejected.append(name)
            else: raise ValueError('corruption accepted '+name)
        copy=summary['proof_copy']; need(copy['sha256']==cfg['trace_sha256'] and copy['bytes']==cfg['trace_bytes'],'transfer identities')
        hr=read(directory/'main/transfer_hash.receipt.json'); cr=read(directory/'main/transfer_copy.receipt.json')
        need(copy['native_hash_receipt']==hr and copy['copy_receipt']==cr,'saved transfer receipts')
        for r in [hr,cr,manifest['filesystem_receipt'],manifest['ext4_disk_receipt']]:
            need(r['actual_exit_code']==0 and r['outer_windows_guard_expired'] is False,'supporting command success')
            for channel in ('stdout','stderr'): bind(ROOT/r[channel],r[channel+'_sha256'])
        need((ROOT/hr['stdout']).read_text().split()==[cfg['trace_sha256'],copy['linux_source']],'native sha256sum identity')
        need(not(directory/'main/parsed_model.json').exists() and not(directory/'main/decoded_factor.json').exists(),'no saved SAT object')
        ps_command=['wsl.exe','--distribution','Ubuntu-24.04','--exec','/usr/bin/ps','-eo','pid,args']; ps=subprocess.run(ps_command,capture_output=True,text=True,timeout=20); need(ps.returncode==0,'fresh process observation')
        matches=[line.strip() for line in ps.stdout.splitlines() if '/'+input_key in line]
        process=dict(timestamp=datetime.now(timezone.utc).isoformat(),command=ps_command,matching_exact_input_processes=matches)
        save(args.out/'process_observation.json',process)
        bind(__file__); bind(entry); bind(ROOT/'acceleration/audit_20260930_normalized_unknown_common.py'); bind(ROOT/'acceleration/audit_20260930_prism_all_columns_unknown.py'); bind(ROOT/'uv.lock'); bind(ROOT/'pyproject.toml')
        need(all(digest(ROOT/p)==v for p,v in bindings.items() if p!=key(trace)),'stable small artifacts')
        report=dict(status=cfg['status'],timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,
          verifier='/root/eight_domain_audit independent raw log/receipt/full partial-trace identity path',shared_components=['Receipt audit conventions adapted from frozen independent audit_20260930_prism_all_columns_unknown.py. Copied frozen audit_20260930_normalized_unknown_common.py with new exact run bindings and wall interval; shared independent receipt/parser method disclosed. No producer imports.'],recommendation='VERIFIED',review_state='CLEAR',kind='empirical/engineering result',basis=['COMPUTED'],actual_attempts=1,completed_UNKNOWN=1,SAT_objects=0,checked_UNSAT_proofs=0,
          run_source_commit=manifest['source_commit'],run_command=manifest['command'],native_command=command,configured_limits=manifest['limits'],outcome=parsed,solver_version='CaDiCaL1.9.5 146207318796f094dcded87349a64f0c6927309e',solver_binary_sha256=manifest['inputs_sha256']['build/research-cadical195/source/build/cadical'],
          partial_trace=dict(path=key(trace),bytes=cfg['trace_bytes'],sha256=cfg['trace_sha256'],fresh_complete_local_hash=True,hash_and_output_checks_seconds=fresh_hash_seconds,availability='LOCAL_ONLY',retrieval='Existing local main/proof.drat; an incomplete trace, not published as a proof.',proof_checked=False,unsat_certificate=False),
          corrupted_controls_rejected=rejected,current_process_observation=process,scope=cfg['scope'],
          limitations=['UNKNOWN establishes no feasibility or exclusion.','The partial trace bytes were fully hashed; no proof checking or UNSAT claim.','Recorded resource caps are configured limits; no peak-resource guarantee.','No performance comparison between distinct formulas or concurrent runs.'],target_resolution=False,external_review=False,artifact_availability='LOCAL_ONLY',elapsed_seconds=time.monotonic()-start)
        save(args.out/'summary.json',report); print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))
    except BaseException as e: save(args.out/'failure.json',dict(status='AUDIT_FAILED',error=repr(e))); raise

CONFIG=dict(directory='acceleration/results/20260930_variable_core_pair_orbits_native_pilot',input='acceleration/results/20260930_variable_core_pair_orbits/instance.cnf',summary_sha256='31a14dc3ab3e5f64e6f404570599f3cc288a85f13c59ac46fb6db07041fe791a',trace_sha256='8076ece031d0ff1588d33337197810a6ac5d55199bcd3ed545b95aef7754f931',trace_bytes=5621796493,exit=0,variables=114484,clauses=561121,conflicts=5000002,real='872.48',cpu='870.15',status='INDEPENDENT_VARIABLE_CORE_PAIR_ORBITS_UNKNOWN_RUN_AUDIT_PASS',scope='One capped attempt on the fully ordered-matching-pair-normalized universally necessary arbitrary-core factor encoding. No residual D or complete target graph supplied; UNKNOWN excludes nothing.')

if __name__=='__main__': run(CONFIG,__file__)
