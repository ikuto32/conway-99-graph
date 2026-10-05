"""Independent native outcome/receipt/complete trace-identity audit; no proof approval."""
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import platform
import re
import subprocess
import sys
import time
from tqdm import tqdm

ROOT=Path(__file__).resolve().parents[1]
BATCH=ROOT/'acceleration/results/20260930_connected_fixed_core_cnf/summary.json'
BATCH_SHA='39425b88f3fa5e46d95c3f4231b044c05484fc9d209250d7c045de6589cd82d6'
SOURCE=ROOT/'acceleration/native_20260930_connected_fixed_core.py'
SOURCE_SHA='f8954ee61adcdec97d7c19df191ccf42645e9a42824ed2914119b42f25dc4d6c'
ENCODING='acceleration/results/20260930_independent_review/connected_fixed_core_cnf/summary.json'
ENCODING_SHA='3ab0a89b8ab4f7043b0bca8d3c66bdb6cbfc7b52a5f4e949de2602feabcf7d3b'
OBJECT='acceleration/results/20260930_independent_review/connected_fixed_core_object_calibration/summary.json'
OBJECT_SHA='b0b7927781afd3dc8f618cea13ae11a196eeb1ca12aeabc5daeb0a08bfa68e7e'
VERSION='c Version 1.9.5 146207318796f094dcded87349a64f0c6927309e'
def need(x,s):
    if not x:raise ValueError(s)
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def digest(p,progress=False):
    h=hashlib.sha256()
    with Path(p).open('rb') as f,tqdm(total=Path(p).stat().st_size,unit='B',unit_scale=True,
                                  desc=Path(p).name,disable=not progress) as bar:
        for block in iter(lambda:f.read(1<<20),b''):h.update(block);bar.update(len(block))
    return h.hexdigest()
def save(p,x):
    with Path(p).open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
def read(p):return json.loads(Path(p).read_bytes())

def parse_outcome(text,receipt):
    lines=text.splitlines();code=receipt['actual_exit_code']
    need(receipt['outer_windows_guard_expired'] is False,'outer guard must not have expired')
    need(lines.count(VERSION)==1,'native exact version')
    need(lines.count("c found 'p cnf 110904 518184' header")==1,'native exact dimensions')
    need(len(re.findall(r"^c setting conflict limit to 2000000 conflicts(?: \(due to '2000000'\))?$",text,re.M))==1,'declared conflict limit')
    def unique(pattern,cast):
        values=re.findall(pattern,text,re.M);need(len(values)==1,'unique native statistic '+pattern);return cast(values[0])
    conflicts=unique(r'^c conflicts:\s+(\d+)\s',int)
    real=unique(r'^c total real time since initialization:\s+([0-9.]+)\s+seconds',float)
    cpu=unique(r'^c total process time since initialization:\s+([0-9.]+)\s+seconds',float)
    statuses=[x for x in lines if x.startswith('s ')];unknown=lines.count('c UNKNOWN')
    need(0<=cpu and 0<=real and 0<=receipt['wall_seconds']<321,'nonnegative bounded recorded times')
    if code==0:
        need(not statuses and unknown==1 and lines[-1]=='c exit 0','explicit native UNKNOWN exit0')
        need(conflicts>=2000000 and not any('caught signal' in x for x in lines),'observed conflict cap')
        result='UNKNOWN_NATIVE_CONFLICT_CAP';native_exit=0
    elif code==124:
        need(not statuses and unknown==1 and 'c caught signal 15 (SIGTERM)' in lines and
             lines[-1]=='c raising signal 15 (SIGTERM)','GNU timeout with explicit native UNKNOWN/SIGTERM')
        need(300<=receipt['wall_seconds']<306,'recorded 300-second timeout')
        result='UNKNOWN_GNU_TIMEOUT_SIGTERM';native_exit=None
    elif code in (10,20):
        expected='s SATISFIABLE' if code==10 else 's UNSATISFIABLE'
        need(statuses==[expected] and unknown==0 and lines[-1]==f'c exit {code}', 'unique native SAT/UNSAT exit')
        need(not any('caught signal' in x for x in lines),'completed native decision without signal')
        result='SAT_RAW_OBJECT_REQUIRES_SEPARATE_CHECK' if code==10 else 'UNSAT_RAW_TRACE_REQUIRES_INDEPENDENT_REPLAY'
        native_exit=code
    else:raise ValueError('unsupported/error native outcome retained but not approved '+str(code))
    return dict(recorded_outcome=result,wrapper_exit_code=code,native_exit_code=native_exit,
                native_exit_code_null_reason='GNU timeout wrapper exit124; native received SIGTERM.' if native_exit is None else None,
                observed_final_conflicts=conflicts,configured_conflict_limit=2000000,
                conflict_cap_reached=conflicts>=2000000,native_real_seconds=real,native_process_seconds=cpu,
                wrapper_wall_seconds=receipt['wall_seconds'])

def controls():
    prefix=VERSION+"\nc found 'p cnf 110904 518184' header\nc setting conflict limit to 2000000 conflicts\n"
    cases=[];rejections=[]
    for code in (0,124,10,20):
        suffix=('c UNKNOWN\n' if code in (0,124) else ('s SATISFIABLE\n' if code==10 else 's UNSATISFIABLE\n'))
        if code==124:suffix+='c caught signal 15 (SIGTERM)\n'
        suffix+='c conflicts: '+('2000001' if code==0 else '42')+' 0.0 per second\n'
        suffix+='c total real time since initialization: 100.00 seconds\nc total process time since initialization: 99.00 seconds\n'
        suffix+=('c raising signal 15 (SIGTERM)\n' if code==124 else f'c exit {code}\n')
        receipt=dict(actual_exit_code=code,outer_windows_guard_expired=False,wall_seconds=300.1 if code==124 else 100.1)
        text=(prefix.replace('2000000 conflicts','2000000 conflicts '+"(due to '2000000')") if code==0 else prefix)+suffix;cases.append(dict(label='SYNTHETIC outcome parser only',stdout=text,receipt=receipt,checked=parse_outcome(text,receipt)))
        bads=[('wrong_dimensions',text.replace('110904 518184','110904 518160'),receipt),
              ('wrong_limit',text.replace('2000000 conflicts','2000001 conflicts'),receipt),
              ('wrong_argument_annotation',text.replace('2000000 conflicts',"2000000 conflicts (due to '1')"),receipt),
              ('duplicate_status',text+'s SATISFIABLE\n',receipt),
              ('outer_guard',text,{**receipt,'outer_windows_guard_expired':True}),
              ('missing_termination','\n'.join(text.splitlines()[:-1])+'\n',receipt),
              ('wrong_exit',text,{**receipt,'actual_exit_code':20 if code!=20 else 10})]
        for label,bad,r in bads:
            try:parse_outcome(bad,r)
            except ValueError:rejections.append(f'{code}_{label}')
            else:raise AssertionError(label)
    return dict(positive_synthetic_cases=cases,corruptions_rejected=rejections,research_claim=False)

def main():
    ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='mode',required=True)
    p=sub.add_parser('calibrate');p.add_argument('--out',type=Path,required=True)
    p=sub.add_parser('audit');p.add_argument('--out',type=Path,required=True);p.add_argument('--core-index',type=int,choices=range(4),required=True)
    p.add_argument('--summary-sha256',required=True)
    args=ap.parse_args();args.out=args.out.resolve();args.out.mkdir(parents=True,exist_ok=False)
    bindings={};start=time.monotonic()
    def pin(p,h=None,progress=False):
        value=digest(p,progress);need(h is None or h==value,'exact hash '+key(p));bindings[key(p)]=value;return value
    def load(p,h=None):pin(p,h);return read(p)
    try:
        control=controls();save(args.out/'controls.json',control)
        for p in [Path(__file__),ROOT/'acceleration/audit_20260930_connected_fixed_core_native_outcome.py',ROOT/'acceleration/results/20260930_independent_review/connected_fixed_core_native_00/failure.json',ROOT/'acceleration/results/20260930_independent_review/connected_fixed_core_outcome_calibration/summary.json',ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(p)
        common=dict(correction_history='V1 rejected the authenticated optional native conflict-limit argument annotation. Original source, calibration and failed core00 audit are preserved and bound; v2 accepts only exact matching annotations and adds rejection controls.',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),
            verifier='/root/state_literature_audit',shared_components=['Standard-library log/receipt parser and SHA256; tqdm progress only. No producer imports.'],
            artifact_availability='LOCAL_ONLY',target_resolution=False,external_review=False)
        if args.mode=='calibrate':
            report={**common,'status':'INDEPENDENT_CONNECTED_FIXED_CORE_OUTCOME_PARSER_CALIBRATION_PASS',
                    'inputs_sha256':bindings,'positive_synthetic_outcome_cases':4,'corrupted_controls_rejected':28,
                    'scope':'Parser calibration only; no native run or mathematical decision.'}
        else:
            directory=ROOT/f'acceleration/results/20260930_connected_fixed_core_native_{args.core_index:02d}'
            summary=load(directory/'summary.json',args.summary_sha256);manifest=load(directory/'manifest.json')
            receipt=load(directory/'main/solver.receipt.json');launch=load(directory/'main/launch.json')
            batch=load(BATCH,BATCH_SHA);record=batch['records'][args.core_index]
            need(summary['core_index']==manifest['core_index']==launch['core_index']==args.core_index,'exact case index')
            need(manifest['mode']=='RESEARCH' and manifest['fixed_instance']==record,'one declared research instance')
            for path,h in manifest['inputs_sha256'].items():pin(ROOT/path,h)
            need(bindings.get(key(SOURCE))==SOURCE_SHA,'frozen native harness source')
            for p,h,status in [(ENCODING,ENCODING_SHA,'INDEPENDENT_CONNECTED_FIXED_CORE_CNF_BATCH_PASS'),
                               (OBJECT,OBJECT_SHA,'INDEPENDENT_CONNECTED_FIXED_CORE_OBJECT_CHECKER_CALIBRATION_PASS')]:
                need(bindings.get(p)==h and read(ROOT/p)['status']==status,'required independently checked gate')
            limits=dict(native_seconds=300,conflicts=2000000,address_space_bytes=4294967296,file_bytes=10737418240,
                        kill_after_seconds=5,outer_windows_guard_seconds=320,maximum_research_attempts=1,automatic_retry=False)
            need(manifest['limits']==limits,'frozen exact resource limits')
            need(summary['receipt']==receipt and summary['research_calls']==1 and summary['automatic_retry'] is False and
                 summary['actual_exit_code']==receipt['actual_exit_code'],'one saved actual invocation')
            need(receipt['command']==launch['command'],'invocation equality');command=receipt['command']
            need(command[command.index('-c')+1]=='2000000' and all(x in command for x in ['300s','--kill-after=5s',
                 '--as=4294967296:4294967296','--fsize=10737418240:10737418240','--core=0:0','--no-binary']), 'exact native resource flags')
            need(launch['cnf_sha256']==record['cnf_sha256'] and launch['core_sha256']==record['core_sha256'] and
                 launch['model_sha256']==record['base_model_sha256'] and any(x.endswith('/'+record['cnf_path']) for x in command), 'launched exact raw core and CNF')
            for path,h in summary['outputs_sha256'].items():pin(ROOT/path,h,progress=Path(path).name=='proof.drat')
            text=(ROOT/receipt['stdout']).read_text()
            need(bindings[receipt['stdout']]==receipt['stdout_sha256'] and bindings[receipt['stderr']]==receipt['stderr_sha256'],'native log hashes')
            need((ROOT/receipt['stderr']).read_bytes()==b'','empty stderr for supported normal outcome')
            parsed=parse_outcome(text,receipt);trace=directory/'main/proof.drat';copy=summary['proof_copy']
            need(bindings[key(trace)]==copy['sha256'] and trace.stat().st_size==copy['bytes'],'fresh complete trace identity')
            hr=load(directory/'main/transfer_hash.receipt.json');cr=load(directory/'main/transfer_copy.receipt.json')
            need(copy['native_hash_receipt']==hr and copy['copy_receipt']==cr,'transfer receipt equality')
            for rec in [hr,cr,manifest['filesystem_receipt'],manifest['ext4_disk_receipt']]:
                need(rec['actual_exit_code']==0 and rec['outer_windows_guard_expired'] is False,'supporting command success')
                for channel in ('stdout','stderr'):pin(ROOT/rec[channel],rec[channel+'_sha256'])
            need((ROOT/hr['stdout']).read_text().split()==[copy['sha256'],copy['linux_source']],'native full sha256sum identity')
            if receipt['actual_exit_code'] in (0,124):
                need(not(directory/'main/parsed_model.json').exists() and not(directory/'main/decoded_factor.json').exists(),'UNKNOWN has no saved SAT object')
            ps_command=['wsl.exe','--distribution','Ubuntu-24.04','--exec','/usr/bin/ps','-eo','pid,args']
            observation=subprocess.run(ps_command,capture_output=True,text=True,timeout=20);need(observation.returncode==0,'fresh process observation')
            matches=[line.strip() for line in observation.stdout.splitlines() if '/'+record['cnf_path'] in line]
            process=dict(timestamp=datetime.now(timezone.utc).isoformat(),command=ps_command,matching_exact_input_processes=matches)
            save(args.out/'process_observation.json',process)
            report={**common,'status':'INDEPENDENT_CONNECTED_FIXED_CORE_NATIVE_OUTCOME_AUDIT_PASS','inputs_sha256':bindings,
                'core_index':args.core_index,'actual_attempts':1,'outcome':parsed,'configured_limits':limits,
                'run_source_commit':manifest['source_commit'],'run_command':manifest['command'],'native_command':command,
                'solver_version':VERSION,'solver_binary_sha256':manifest['inputs_sha256']['build/research-cadical195/source/build/cadical'],
                'trace':dict(path=key(trace),bytes=trace.stat().st_size,sha256=bindings[key(trace)],fresh_complete_local_hash=True,
                    proof_checked=False,unsat_certificate=False,availability='LOCAL_ONLY',linux_original=copy['linux_source']),
                'checked_UNSAT_proofs':0,'checked_SAT_objects':0,'current_process_observation':process,
                'corrupted_controls_rejected':control['corruptions_rejected'],
                'scope':'Observed outcome, source/input bindings, configured limits and whole saved trace identity for one fixed-core attempt only.',
                'limitations':['No raw SAT/UNSAT result is a verified mathematical decision in this report.',
                               'UNKNOWN proves no feasibility or exclusion; a partial trace is not a proof.',
                               'Resource settings are configured limits, not measured peak-resource guarantees.',
                               'No process is launched, stopped or retried by this audit.'],
                'elapsed_seconds':time.monotonic()-start}
        save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))
    except BaseException as e:save(args.out/'failure.json',dict(error=repr(e)));raise
if __name__=='__main__':main()
