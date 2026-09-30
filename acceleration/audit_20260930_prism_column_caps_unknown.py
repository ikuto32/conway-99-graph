"""Raw native UNKNOWN outcome and complete partial-trace identity audit.

No producer imports. Reuses conventions of the separately authored ordered-pair
run auditor; does not reapprove the cap encoding produced by this reviewer.
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
RUN=ROOT/'acceleration/results/20260930_prism_column_caps_native_pilot'
CNF='acceleration/results/20260930_prism_column_caps_v3/instance.cnf'
MODEL='acceleration/results/20260930_prism_column_caps_v3/model.json'
SCOPE='acceleration/results/20260930_prism_column_caps_v3/scope.json'
CNF_SHA='2b013ebf7f0d7090c192d5b54ec236241d8f4cab0a6efbde90b9498f707bde88'
MODEL_SHA='524b7bf0bdbdaa617acfca4ebece53560d5adb7b3e700a9bae25cfddbab7cf72'
SCOPE_SHA='f4c8914db51ac62f2d796aff3ac789ef60196b204a891905f157c5fb58711540'
NATIVE='build/research-cadical195/source/build/cadical'
NATIVE_SHA='021e58781c761296b436cfbdf49507ff290db175f67e5609bf6f41e4cc62d0b7'
VERSION='1.9.5 146207318796f094dcded87349a64f0c6927309e'
GATES=[('acceleration/results/20260930_independent_review/prism_column_caps/summary.json',
        '5c137eb4b497433d02d99e7b1105c34e06f679b55cd5cbe722b8f265d3f47edf',
        'INDEPENDENT_SIX_PRISM_COLUMN_CAP_EXTENSION_PASS'),
       ('acceleration/results/20260930_independent_review/prism_column_caps_object_calibration/summary.json',
        'a0ffaef3a8088a3cf6dd33a1eb7f18696c6b9ddff7e6ad8ac72ffb4a174a7b75',
        'INDEPENDENT_SIX_PRISM_COLUMN_CAP_OBJECT_CHECKER_CALIBRATION_PASS')]

def need(ok,message):
    if not ok: raise ValueError(message)

def digest(path):
    h=sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(4<<20),b''): h.update(block)
    return h.hexdigest()

def key(path): return Path(path).resolve().relative_to(ROOT).as_posix()
def stamp(): return datetime.now(timezone.utc).isoformat()

def save(path,value):
    with Path(path).open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(value,stream,indent=2); stream.write('\n')

def only(pattern,text,label):
    values=re.findall(pattern,text,re.M)
    need(len(values)==1,'exactly one '+label)
    return values[0]

def interpret(text,receipt):
    lines=text.splitlines()
    need(lines.count('c UNKNOWN')==1 and not any(x.startswith(('s ','v ')) for x in lines),'explicit UNKNOWN and no SAT/UNSAT/model output')
    need(receipt['actual_exit_code'] in (0,124) and receipt['outer_windows_guard_expired'] is False,'bounded UNKNOWN process exit')
    need(lines.count("c found 'p cnf 247320 920401' header")==1,'exact actual CNF dimensions')
    need(lines.count('c Version '+VERSION)==1,'native version')
    need(lines.count("c setting conflict limit to 5000000 conflicts (due to '5000000')")==1,'configured native conflict limit')
    conflicts=int(only(r'^c conflicts:\s+(\d+)\s',text,'conflict statistic'))
    real=only(r'^c total real time since initialization:\s+([0-9.]+)\s+seconds',text,'native real time')
    cpu=only(r'^c total process time since initialization:\s+([0-9.]+)\s+seconds',text,'native process time')
    need(0<float(real)<905 and 0<float(cpu)<905,'positive bounded native timing statistics')
    wall=receipt['wall_seconds']; need(type(wall) in (int,float) and wall>0,'literal positive wrapper timing')
    if receipt['actual_exit_code']==124:
        need(lines.count('c caught signal 15 (SIGTERM)')==1 and lines[-1]=='c raising signal 15 (SIGTERM)','explicit native SIGTERM end')
        need('c exit 0' not in lines and 900<=wall<905,'GNU timeout wall interpretation')
        result='UNKNOWN_GNU_TIMEOUT_SIGTERM'; exit_code=None
    else:
        need(lines[-1]=='c exit 0' and not any('caught signal' in x for x in lines),'explicit native exit0 without signal')
        need(conflicts>=5000000 and wall<900,'native conflict cap reached before deadline')
        result='UNKNOWN_NATIVE_CONFLICT_CAP'; exit_code=0
    return dict(result=result,wrapper_exit_code=receipt['actual_exit_code'],native_exit_code=exit_code,
        native_exit_code_null_reason='The timeout wrapper exited124; signal termination is not a native SAT/UNSAT exit.' if exit_code is None else None,
        configured_conflict_limit=5000000,observed_final_conflicts=conflicts,conflict_cap_reached=conflicts>=5000000,
        native_real_seconds=real,native_process_seconds=cpu,wrapper_wall_seconds=wall)

def controls(text,receipt):
    bads=[('false_UNSAT',text.replace('c UNKNOWN','s UNSATISFIABLE'),receipt),
          ('false_SAT_exit10',text,{**receipt,'actual_exit_code':10}),
          ('missing_conflict_statistics',re.sub(r'^c conflicts:.*\n','',text,flags=re.M),receipt),
          ('missing_termination',text.rsplit(text.splitlines()[-1],1)[0],receipt),
          ('expired_outer_guard',text,{**receipt,'outer_windows_guard_expired':True}),
          ('wrong_dimensions',text.replace('p cnf 247320 920401','p cnf 247320 1'),receipt),
          ('wrong_solver_version',text.replace('c Version '+VERSION,'c Version altered'),receipt),
          ('wrong_configured_conflicts',text.replace('c setting conflict limit to 5000000 conflicts','c setting conflict limit to 5 conflicts'),receipt),
          ('false_wrapper_time',text,{**receipt,'wall_seconds':9999}),
          ('spurious_model_line',text+'v 1 0\n',receipt)]
    rejected=[]
    for name,t,r in bads:
        try: interpret(t,r)
        except ValueError: rejected.append(name)
        else: raise ValueError('corrupted receipt/log accepted: '+name)
    return rejected

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--summary-sha256',required=True); ap.add_argument('--out',required=True,type=Path)
    args=ap.parse_args(); need((RUN/'summary.json').exists(),'completed producer summary required; do not audit a live trace')
    need(digest(RUN/'summary.json')==args.summary_sha256,'frozen completed run summary')
    args.out.mkdir(parents=True,exist_ok=False); start=time.monotonic(); bindings={}
    def bind(path,expected=None):
        path=Path(path); k=key(path); value=digest(path)
        need(expected is None or value==expected,'exact input/output identity '+k); bindings[k]=value; return path
    def read(path,expected=None): return json.loads(bind(path,expected).read_bytes())
    try:
        summary=read(RUN/'summary.json',args.summary_sha256); manifest=read(RUN/'manifest.json')
        receipt=read(RUN/'main/solver.receipt.json'); launch=read(RUN/'main/launch.json'); workspace=read(RUN/'workspace.json')
        need(summary['receipt']==receipt and summary['actual_exit_code']==receipt['actual_exit_code'],'summary matches raw receipt')
        need(summary['research_calls']==1 and summary['automatic_retry'] is False and summary['target_resolution'] is False,'one research call without promotion/retry')
        need(summary['interpreted_result']=='UNKNOWN_NATIVE_OR_RESOURCE_OUTCOME','producer reports UNKNOWN only')
        need(manifest['mode']=='RESEARCH','actual research mode')
        expected_limits=dict(native_seconds=900,conflicts=5000000,address_space_bytes=4294967296,file_bytes=10737418240,
            kill_after_seconds=5,outer_windows_guard_seconds=920,maximum_research_attempts=1,automatic_retry=False)
        need(manifest['limits']==expected_limits,'complete configured limits')
        for p,h in manifest['inputs_sha256'].items(): bind(ROOT/p,h)
        for p,h in [(CNF,CNF_SHA),(MODEL,MODEL_SHA),(SCOPE,SCOPE_SHA),(NATIVE,NATIVE_SHA)]:
            need(manifest['inputs_sha256'][p]==h,'frozen intended input/binary')
        for path,h,status in GATES:
            gate=read(ROOT/path,h); need(gate['status']==status,'separately approved encoding/object gate')
            for p,identity in [(CNF,CNF_SHA),(MODEL,MODEL_SHA),(SCOPE,SCOPE_SHA)]:
                need(gate['inputs_sha256'][p]==identity,'independent gate exact run scope')
        linux_root='/mnt/c/'+ROOT.as_posix()[3:]
        proof=workspace['path']+'/proof.drat'
        need(re.fullmatch(r'/tmp/conway99-prism-column-caps-[A-Za-z0-9]+',workspace['path']) is not None and workspace['preserved'] is True,'exclusive saved native proof workspace')
        expected_command=['wsl.exe','--distribution','Ubuntu-24.04','--exec','/usr/bin/timeout','--signal=TERM','--kill-after=5s','900s','/usr/bin/prlimit',
            '--as=4294967296:4294967296','--fsize=10737418240:10737418240','--core=0:0',linux_root+'/'+NATIVE,'--no-binary','-c','5000000',linux_root+'/'+CNF,proof]
        need(launch['command']==receipt['command']==expected_command,'independently reconstructed exact launch command')
        need(launch['cnf_sha256']==CNF_SHA and launch['model_sha256']==MODEL_SHA and launch['ext4_proof']==proof,'launch exact formula/model/proof location')
        need(receipt['outer_windows_guard_seconds']==920,'saved outer guard limit')
        text=bind(ROOT/receipt['stdout'],receipt['stdout_sha256']).read_text(encoding='utf-8')
        need(bind(ROOT/receipt['stderr'],receipt['stderr_sha256']).read_bytes()==b'','raw solver stderr empty')
        parsed=interpret(text,receipt); rejected=controls(text,receipt)
        parser_positives=[]
        for old_name,old_header in [('20260930_variable_core_pair_orbits_native_pilot','114484 561121'),
                                    ('20260930_prism_first_choice_native_pilot','245880 874801')]:
            old=ROOT/'acceleration/results'/old_name/'main'
            old_text=bind(old/'solver.stdout.log').read_text(encoding='utf-8')
            old_receipt=read(old/'solver.receipt.json')
            need(digest(old/'solver.stdout.log')==old_receipt['stdout_sha256'],'positive-control raw stdout identity')
            adapted=old_text.replace('p cnf '+old_header,'p cnf 247320 920401')
            result=interpret(adapted,old_receipt)
            parser_positives.append(dict(raw_stdout=key(old/'solver.stdout.log'),raw_receipt=key(old/'solver.receipt.json'),
                transformation='Only the displayed CNF dimensions are substituted for parser calibration; not a run on the caps formula.',
                expected_branch='UNKNOWN_NATIVE_CONFLICT_CAP' if old_receipt['actual_exit_code']==0 else 'UNKNOWN_GNU_TIMEOUT_SIGTERM',result=result))
        trace=RUN/'main/proof.drat'; trace_before=trace.stat(); hash_start=time.monotonic()
        for p,h in summary['outputs_sha256'].items(): bind(ROOT/p,h)
        trace_hash_seconds=time.monotonic()-hash_start; trace_after=trace.stat()
        need(trace_before.st_size==trace_after.st_size and trace_before.st_mtime_ns==trace_after.st_mtime_ns,'completed local trace remained stable during full hash')
        copy=summary['proof_copy']; need(copy['sha256']==bindings[key(trace)] and copy['bytes']==trace_after.st_size and copy['linux_source']==proof,'native/local complete partial-trace identity')
        hash_receipt=read(RUN/'main/transfer_hash.receipt.json'); copy_receipt=read(RUN/'main/transfer_copy.receipt.json')
        need(copy['native_hash_receipt']==hash_receipt and copy['copy_receipt']==copy_receipt,'summary matches original transfer receipts')
        support=[hash_receipt,copy_receipt,manifest['filesystem_receipt'],manifest['ext4_disk_receipt'],manifest['memory_receipt'],workspace['mktemp']]
        for r in support:
            need(r['actual_exit_code']==0 and r['outer_windows_guard_expired'] is False,'supporting command actually completed')
            for channel in ('stdout','stderr'): bind(ROOT/r[channel],r[channel+'_sha256'])
        need((ROOT/hash_receipt['stdout']).read_text(encoding='utf-8').split()==[bindings[key(trace)],proof],'native sha256sum matches complete local bytes')
        need(hash_receipt['command']==['wsl.exe','--distribution','Ubuntu-24.04','--exec','/usr/bin/sha256sum',proof],'native hash command identity')
        need(copy_receipt['command']==['wsl.exe','--distribution','Ubuntu-24.04','--exec','/usr/bin/cp','--',proof,linux_root+'/'+key(trace)],'native-to-local copy command identity')
        need(not(RUN/'main/parsed_model.json').exists() and not(RUN/'main/decoded_factor.json').exists(),'no saved SAT artifact')
        ps_command=['wsl.exe','--distribution','Ubuntu-24.04','--exec','/usr/bin/ps','-eo','pid,args']
        ps=subprocess.run(ps_command,capture_output=True,text=True,timeout=20); need(ps.returncode==0,'fresh live process query')
        matches=[line.strip() for line in ps.stdout.splitlines() if '/'+CNF in line]
        process=dict(timestamp=stamp(),command=ps_command,exit_code=ps.returncode,matching_exact_input_processes=matches)
        save(args.out/'process_observation.json',process); need(not matches,'no ongoing native process for the completed exact input')
        bind(__file__); bind(ROOT/'acceleration/audit_20260930_variable_core_pair_orbits_unknown.py')
        bind(ROOT/'acceleration/audit_20260930_normalized_unknown_common.py'); bind(ROOT/'uv.lock'); bind(ROOT/'pyproject.toml')
        bind(ROOT/'docs/AUDIT_20260930_PRISM_COLUMN_CAP_UNKNOWN.md')
        need(all(digest(ROOT/p)==h for p,h in bindings.items() if p!=key(trace)),'other frozen bound artifacts remained unchanged')
        report=dict(status='INDEPENDENT_SIX_PRISM_COLUMN_CAP_UNKNOWN_RUN_AUDIT_PASS',created_at=stamp(),updated_at=stamp(),
            source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),
            uv_version=subprocess.check_output(['uv','--version'],text=True).strip(),inputs_sha256=bindings,
            verifier='/root/eight_domain_audit separate raw native execution/log/receipt/hash checking path',
            method='independent_artifact_check',kind='empirical/engineering result',basis=['COMPUTED'],recommendation='VERIFIED',review_state='CLEAR',
            statement='The exact fixed-six-prism factor-plus-column-cap native run made one capped attempt and ended UNKNOWN as specified by the raw log and receipt; its complete saved partial trace matches the recorded native hash and is not a checked proof.',
            scope='Execution outcome only for one fixed-six-prism normalized factor-plus-all-outside-column-caps formula; no residual D or unrestricted coverage.',
            actual_attempts=1,completed_UNKNOWN=1,SAT_objects=0,checked_UNSAT_proofs=0,
            run_source_commit=manifest['source_commit'],run_command=manifest['command'],native_command=expected_command,
            configured_limits=expected_limits,outcome=parsed,solver_version='CaDiCaL '+VERSION,solver_binary_sha256=NATIVE_SHA,
            partial_trace=dict(path=key(trace),bytes=trace_after.st_size,sha256=bindings[key(trace)],fresh_complete_local_hash=True,
                hash_and_output_checks_seconds=trace_hash_seconds,availability='LOCAL_ONLY',retrieval='Existing local main/proof.drat, with native /tmp copy preserved; not published as a proof.',
                native_path=proof,proof_checked=False,unsat_certificate=False),
            parser_positive_controls=parser_positives,corrupted_controls_rejected=rejected,current_process_observation=process,
            shared_components=['The auditor authored the caps producer. This audit does not approve encoding semantics, coverage or the mathematical model; it binds Structural\'s independent cap gate and independently calibrated object gate.',
                'Raw receipt/parser conventions reuse the earlier independently authored normalized and ordered-pair UNKNOWN audits; this source imports no producer or those audit implementations.',
                'The same solver binary/native wrapper environment is authenticated, not a second solver implementation.'],
            limitations=['UNKNOWN excludes nothing and supplies no feasible factor or target graph.',
                'Complete partial-trace hashing verifies byte identity only; no DRAT proof replay was performed.',
                'Resource figures distinguish configured caps from observed final statistics; peak-resource use is not certified.',
                'No general performance or comparison claim.'],
            artifact_availability='LOCAL_ONLY',target_resolution=False,external_review=False,elapsed_seconds=time.monotonic()-start)
        save(args.out/'summary.json',report)
        print(json.dumps(dict(status=report['status'],summary=key(args.out/'summary.json'),sha256=digest(args.out/'summary.json'),outcome=parsed)))
    except BaseException as error:
        save(args.out/'failure.json',dict(status='AUDIT_FAILED',timestamp=stamp(),error=repr(error))); raise

if __name__=='__main__': main()
