"""Independent saved-run audit of the base joint factor UNKNOWN outcome.

The large partial trace is NOT rehashed or proof-checked. Its original
native/copy hashes are authenticated receipt evidence, explicitly distinct
from fresh byte identity verification.
"""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import re
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'acceleration/results/20260930_triangle_joint_factor_native_pilot'
TRACE=D/'main/proof.drat'
TRACE_SHA='46fd17658f8656d56d33736e78e6d1b3dc1dab13c18bf6f08a80dd05637e5b59'
TRACE_BYTES=574434634

def need(value,message):
    if not value:raise ValueError(message)
def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(1<<20),b''):h.update(block)
    return h.hexdigest()
def key(path):return Path(path).resolve().relative_to(ROOT).as_posix()
def read(path):return json.loads(Path(path).read_bytes())
def save(path,data):
    with Path(path).open('x',encoding='utf-8') as f:json.dump(data,f,indent=2);f.write('\n')

def interpret(stdout,receipt,launch,manifest):
    lines=stdout.splitlines()
    need(lines.count('c UNKNOWN')==1 and not any(x.startswith('s ') for x in lines),'explicit unique UNKNOWN without SAT/UNSAT status')
    need(receipt['actual_exit_code']==0 and receipt['outer_windows_guard_expired'] is False and 'c exit 0' in lines,'completed native UNKNOWN exit')
    need(receipt['command']==launch['command'],'exact launch/receipt command equality')
    command=receipt['command'];need(command[command.index('-c')+1]=='1000000','declared conflict cap argument')
    need('300s' in command and '--as=4294967296:4294967296' in command and '--fsize=10737418240:10737418240' in command,'declared native resource caps')
    need(manifest['limits']['conflicts']==1000000 and manifest['limits']['native_seconds']==300,'run manifest cap agreement')
    need('c setting conflict limit to 1000000 conflicts' in stdout,'solver acknowledges conflict cap')
    conflicts=re.findall(r'^c conflicts:\s+(\d+)\s',stdout,re.M);need(conflicts==['1000000'],'actual terminal conflict count')
    version=re.findall(r'^c Version ([^\r\n]+)',stdout,re.M);need(version==['1.9.5 146207318796f094dcded87349a64f0c6927309e'],'exact solver version/source revision')
    need("c found 'p cnf 58860 203748' header" in lines and 'c parsed 203748 clauses' in stdout,'actual parsed problem dimensions')
    proofbytes=re.findall(r'^c DRAT (\d+) bytes',stdout,re.M);need(proofbytes==[str(TRACE_BYTES)],'solver trace byte count')
    real=re.findall(r'^c total real time since initialization:\s+([0-9.]+)\s+seconds',stdout,re.M)
    cpu=re.findall(r'^c total process time since initialization:\s+([0-9.]+)\s+seconds',stdout,re.M)
    need(real==['69.55'] and cpu==['68.81'],'recorded solver timing fields')
    need(0<receipt['wall_seconds']<300,'native wrapper returned before time limit')
    return dict(result='UNKNOWN_CONFLICT_LIMIT_REACHED',conflicts=1000000,native_exit_code=0,wall_timeout_reached=False,reported_native_real_seconds=69.55,reported_native_process_seconds=68.81,wrapper_wall_seconds=receipt['wall_seconds'],solver_version=version[0],variables=58860,clauses=203748)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False);bindings={}
    def bind(path,expected=None):
        need(Path(path).resolve()!=TRACE.resolve(),'large partial trace must not be silently rehashed')
        value=digest(path);need(expected is None or value==expected,'hash mismatch '+str(path));bindings[key(path)]=value;return Path(path)
    def load(path):return read(bind(path))
    try:
        manifest=load(D/'manifest.json');summary=load(D/'summary.json');launch=load(D/'main/launch.json');receipt=load(D/'main/solver.receipt.json')
        need(summary['receipt']==receipt and summary['actual_exit_code']==0 and summary['research_calls']==1 and summary['automatic_retry'] is False,'one recorded completed base call')
        for path,value in manifest['inputs_sha256'].items():bind(ROOT/path,value)
        for path,value in summary['outputs_sha256'].items():
            if path==key(TRACE):need(value==TRACE_SHA,'recorded partial trace hash')
            else:bind(ROOT/path,value)
        for channel in ['stdout','stderr']:
            bind(ROOT/receipt[channel],receipt[channel+'_sha256'])
        stdout=(ROOT/receipt['stdout']).read_text();need((ROOT/receipt['stderr']).read_bytes()==b'','empty saved stderr')
        outcome=interpret(stdout,receipt,launch,manifest)
        need(launch['cnf_sha256']==manifest['inputs_sha256']['acceleration/results/20260930_triangle_joint_factor_cnf/instance.cnf'],'exact base CNF identity')
        trace=summary['proof_copy'];need(trace['sha256']==TRACE_SHA and trace['bytes']==TRACE_BYTES and TRACE.stat().st_size==TRACE_BYTES,'recorded trace identity/current size')
        hashreceipt=load(D/'main/transfer_hash.receipt.json');copyreceipt=load(D/'main/transfer_copy.receipt.json')
        need(hashreceipt==trace['native_hash_receipt'] and copyreceipt==trace['copy_receipt'],'complete original native/copy receipts')
        for r in [hashreceipt,copyreceipt]:
            need(r['actual_exit_code']==0 and not r['outer_windows_guard_expired'],'successful saved transfer command')
            for channel in ['stdout','stderr']:bind(ROOT/r[channel],r[channel+'_sha256'])
        native_hash=(ROOT/hashreceipt['stdout']).read_text().strip().split()
        need(native_hash==[TRACE_SHA,trace['linux_source']],'actual saved native sha256 output')
        need(trace['windows_hash_wall_seconds']>0,'recorded subsequent destination hash computation')
        need(not (D/'main/parsed_model.json').exists() and not (D/'main/decoded_factor.json').exists(),'no saved SAT object from UNKNOWN call')
        corrupt=[]
        for label in ['false_UNSAT','wrong_exit','wrong_conflicts','wrong_input_size','outer_timeout']:
            s=stdout;r=deepcopy(receipt)
            if label=='false_UNSAT':s=s.replace('c UNKNOWN','s UNSATISFIABLE')
            elif label=='wrong_exit':r['actual_exit_code']=20
            elif label=='wrong_conflicts':s=s.replace('c conflicts:               1000000','c conflicts:               999999')
            elif label=='wrong_input_size':s=s.replace('p cnf 58860 203748','p cnf 58860 203747')
            else:r['outer_windows_guard_expired']=True
            try:interpret(s,r,launch,manifest)
            except ValueError:corrupt.append(label)
            else:raise ValueError('corrupt run record accepted '+label)
        ps_command=['wsl.exe','--distribution','Ubuntu-24.04','--exec','/usr/bin/ps','-eo','pid,args']
        ps=subprocess.run(ps_command,capture_output=True,text=True,timeout=20)
        need(ps.returncode==0,'read-only current process observation')
        fragment='/acceleration/results/20260930_triangle_joint_factor_cnf/instance.cnf'
        observed=[line.strip() for line in ps.stdout.splitlines() if fragment in line]
        process=dict(timestamp=datetime.now(timezone.utc).isoformat(),command=ps_command,exit_code=ps.returncode,matching_base_input_processes=observed,state='NOT_OBSERVED' if not observed else 'OBSERVED',scope='Only process command lines containing the exact base joint-factor CNF path; not a claim about other experiments.')
        bind(__file__);bind(ROOT/'uv.lock');bind(ROOT/'pyproject.toml')
        report=dict(status='INDEPENDENT_TRIANGLE_JOINT_FACTOR_UNKNOWN_RUN_AUDIT_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),verifier='/root/eight_domain_audit independent run-record interpretation',inputs_sha256=bindings,
          original_run_source_commit=manifest['source_commit'],original_run_command=manifest['command'],native_command=receipt['command'],native_limits=manifest['limits'],actual_result=outcome,current_process_observation=process,
          statement='The saved single base joint-factor pilot ended with native UNKNOWN/exit0 at its configured1000000conflict cap, before the300second wall deadline. No SAT model or checked UNSAT proof was produced.',kind='empirical/engineering result',basis=['COMPUTED'],recommendation='VERIFIED',review_state='CLEAR',
          partial_trace=dict(path=key(TRACE),artifact_availability='LOCAL_ONLY',bytes=TRACE_BYTES,recorded_sha256=TRACE_SHA,retrieval='Existing repository-local path; original Linux path retained in run proof_copy record.',hash_evidence='Saved original native sha256sum stdout and source-audited Windows copy/hash receipt agree. Independent audit rehashed these small records and checked current trace size; it did not repeat the574MB trace hash.',fresh_full_trace_hash=False,proof_check_performed=False,unsat_certificate=False),
          corrupted_controls_rejected=corrupt,scope='One recorded capped engineering attempt on the fixed-core factor CNF; no mathematical exclusion or performance comparison.',artifact_availability='LOCAL_ONLY',target_resolution=False,external_review=False,limitations=['The large partial trace bytes were not independently rehashed in this audit.','Trace validity is not claimed, and no DRAT proof checker was run.','Reported CPU/wall times are observed log/receipt values, not repeated performance measurements.','No statement about satisfiability follows from UNKNOWN.'])
        save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))
    except BaseException as e:
        save(args.out/'failure.json',dict(status='AUDIT_FAILED',error=repr(e)));raise

if __name__=='__main__':main()
