"""Independent raw native outcome audit for the single coarse60 attempt."""
from datetime import datetime,timezone
from pathlib import Path
import argparse
import json
import platform
import subprocess
import sys
import time
import audit_20260930_connected_fixed_core_native_outcome_v2 as previous

ROOT=previous.ROOT
RUN=ROOT/'acceleration/results/20260930_prism_coarse60_bitflip_native_pilot'
D=ROOT/'acceleration/results/20260930_prism_coarse60_bitflip'
BASE=ROOT/'acceleration/results/20260930_prism_coarse60_bitlift'
need,digest,key,save,read=previous.need,previous.digest,previous.key,previous.save,previous.read
PINS={
 'acceleration/results/20260930_prism_coarse60_bitflip/extension.json':'4838c853fc99f3ffbb3736aa234e30a3f2a6f90da67b1a50217c132efe2f8c83',
 'acceleration/native_20260930_prism_coarse60_bitflip.py':'f441150494323f394897f6b6831495ce460c00a64d404461970c38c19d50af12',
 'acceleration/audit_20260930_connected_fixed_core_native_outcome_v2.py':'b788077b58db41737f9e541e7c74de9d2135d50f72da07df288435b4d65bc472',
 'acceleration/results/20260930_prism_coarse60_bitflip/instance.cnf':'afa6581bfc3309e6c1ddb434996fb53aee712771fabaf2aef9432cfc30dc3c72',
 'acceleration/results/20260930_prism_coarse60_bitlift/model.json':'a437d3f1381e9554bff2376726a991f1d1e0ea23c240f8ebacf005c57e82fcb5',
 'acceleration/results/20260930_prism_coarse60_bitlift/scope.json':'3237da2a02c60fc3f0c61e562788582b7ce25946afb523a84dc6634912ed98e9',
 'acceleration/results/20260930_independent_review/prism_coarse60_bitflip/summary.json':'ea41069f8bad705c1163e55d04735bca99c24276e447e1b1437ac7aa3d1b7123',
 'acceleration/results/20260930_independent_review/prism_coarse60_bitflip_object_calibration/summary.json':'a0802564228f308fa925755f1ad1ad5b76409346a7889ecff3f9d46fe3b86254'}

def outcome(text,receipt):
    need(text.splitlines().count("c found 'p cnf 5238 85704' header")==1,'actual coarse60 input dimensions')
    # The shared parser only specializes its input-dimension check; actual
    # dimensions have just been checked separately. No saved log is edited.
    normalized=text.replace("c found 'p cnf 5238 85704' header","c found 'p cnf 110904 518184' header")
    return previous.parse_outcome(normalized,receipt)

def controls():
    old=previous.controls();positives=[];negatives=[]
    for index,case in enumerate(old['positive_synthetic_cases']):
        text=case['stdout'].replace('110904 518184','5238 85704');receipt=case['receipt']
        positives.append(dict(label='SYNTHETIC coarse60 outcome parser only',result=outcome(text,receipt)))
        for label,bad,r in [('wrong_actual_header',text.replace('5238 85704','5238 85703'),receipt),
                            ('false_terminal',text+'s SATISFIABLE\n',receipt),
                            ('wrong_annotation',text.replace('2000000 conflicts',"2000000 conflicts (due to '1')"),receipt),
                            ('outer_guard',text,{**receipt,'outer_windows_guard_expired':True})]:
            try:outcome(bad,r)
            except ValueError:negatives.append(f'{index}_{label}')
            else:raise ValueError('corruption accepted '+label)
    return dict(positive_synthetic_cases=positives,new_corruptions_rejected=negatives,
                shared_parser_corruptions_rejected=old['corruptions_rejected'],no_research_outcome_asserted=True)

def main():
    ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='mode',required=True)
    p=sub.add_parser('calibrate');p.add_argument('--out',type=Path,required=True)
    p=sub.add_parser('audit');p.add_argument('--out',type=Path,required=True);p.add_argument('--summary-sha256',required=True)
    args=ap.parse_args();args.out=args.out.resolve();args.out.mkdir(parents=True,exist_ok=False);bindings={};start=time.monotonic()
    def pin(p,h=None,progress=False):
        value=digest(p,progress);need(h is None or value==h,'hash '+key(p));bindings[key(p)]=value;return value
    def load(p,h=None):pin(p,h);return read(p)
    try:
        for p,h in PINS.items():pin(ROOT/p,h)
        for p in [Path(__file__),ROOT/'uv.lock',ROOT/'pyproject.toml']:pin(p)
        control=controls();save(args.out/'controls.json',control)
        common=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),verifier='/root/state_literature_audit',
            shared_components=['Frozen independently calibrated2000000-conflict/300-second native outcome parser. Actual coarse60 header checked separately before in-memory adapter. No producer imports.'],
            artifact_availability='LOCAL_ONLY',target_resolution=False,external_review=False)
        if args.mode=='calibrate':
            report={**common,'status':'INDEPENDENT_PRISM_COARSE60_BITFLIP_OUTCOME_PARSER_CALIBRATION_PASS','inputs_sha256':bindings,
                    'positive_synthetic_cases':4,'new_corruptions_rejected':16,'shared_corruptions_rejected':28,'scope':'Log-parser calibration only.'}
        else:
            summary=load(RUN/'summary.json',args.summary_sha256);manifest=load(RUN/'manifest.json')
            receipt=load(RUN/'main/solver.receipt.json');launch=load(RUN/'main/launch.json')
            for p,h in manifest['inputs_sha256'].items():pin(ROOT/p,h)
            need(manifest['mode']=='RESEARCH','declared actual research attempt')
            limits=dict(native_seconds=300,conflicts=2000000,address_space_bytes=4294967296,file_bytes=10737418240,
                        kill_after_seconds=5,outer_windows_guard_seconds=320,maximum_research_attempts=1,automatic_retry=False)
            need(manifest['limits']==limits,'exact frozen limits')
            need(summary['receipt']==receipt and summary['actual_exit_code']==receipt['actual_exit_code'] and
                 summary['research_calls']==1 and summary['automatic_retry'] is False,'single actual invocation')
            command=receipt['command'];need(command==launch['command'],'invocation identity')
            need(command[command.index('-c')+1]=='2000000' and all(s in command for s in ['300s','--kill-after=5s',
                 '--as=4294967296:4294967296','--fsize=10737418240:10737418240','--core=0:0','--no-binary']),'resource invocation')
            cnfkey=key(D/'instance.cnf');need(launch['cnf_sha256']==PINS[cnfkey] and any(s.endswith('/'+cnfkey) for s in command),'exact launched formula')
            need(launch['model_sha256']==PINS[key(BASE/'model.json')],'exact model binding')
            for path,h in summary['outputs_sha256'].items():pin(ROOT/path,h,progress=Path(path).name=='proof.drat')
            need(bindings[receipt['stdout']]==receipt['stdout_sha256'] and bindings[receipt['stderr']]==receipt['stderr_sha256'],'log byte identities')
            need((ROOT/receipt['stderr']).read_bytes()==b'','empty native stderr')
            parsed=outcome((ROOT/receipt['stdout']).read_text(),receipt);trace=RUN/'main/proof.drat';copy=summary['proof_copy']
            need(copy['sha256']==bindings[key(trace)] and copy['bytes']==trace.stat().st_size,'fresh whole trace and transfer identity')
            hr=load(RUN/'main/transfer_hash.receipt.json');cr=load(RUN/'main/transfer_copy.receipt.json')
            need(copy['native_hash_receipt']==hr and copy['copy_receipt']==cr,'saved transfer receipts')
            for rec in [hr,cr,manifest['filesystem_receipt'],manifest['ext4_disk_receipt']]:
                need(rec['actual_exit_code']==0 and rec['outer_windows_guard_expired'] is False,'supporting command success')
                for channel in ['stdout','stderr']:pin(ROOT/rec[channel],rec[channel+'_sha256'])
            need((ROOT/hr['stdout']).read_text().split()==[copy['sha256'],copy['linux_source']],'native full sha256sum identity')
            if receipt['actual_exit_code'] in (0,124):need(not(RUN/'main/parsed_model.json').exists() and not(RUN/'main/decoded_factor.json').exists(),'UNKNOWN has no raw SAT object')
            pscommand=['wsl.exe','--distribution','Ubuntu-24.04','--exec','/usr/bin/ps','-eo','pid,args']
            proc=subprocess.run(pscommand,capture_output=True,text=True,timeout=20);need(proc.returncode==0,'fresh read-only process check')
            observation=dict(timestamp=datetime.now(timezone.utc).isoformat(),command=pscommand,
                             matching_exact_input_processes=[s.strip() for s in proc.stdout.splitlines() if '/'+cnfkey in s])
            save(args.out/'process_observation.json',observation)
            report={**common,'status':'INDEPENDENT_PRISM_COARSE60_BITFLIP_NATIVE_OUTCOME_AUDIT_PASS','inputs_sha256':bindings,
                'actual_attempts':1,'outcome':parsed,'configured_limits':limits,'native_command':command,
                'run_source_commit':manifest['source_commit'],'run_command':manifest['command'],
                'trace':dict(path=key(trace),bytes=trace.stat().st_size,sha256=bindings[key(trace)],fresh_complete_local_hash=True,
                             proof_checked=False,unsat_certificate=False,availability='LOCAL_ONLY',linux_original=copy['linux_source']),
                'checked_UNSAT_proofs':0,'checked_SAT_objects':0,'current_process_observation':observation,
                'scope':'One frozen first-column-zero six-prism60-pattern construction attempt; outcome and artifacts only.',
                'limitations':['Native SAT/UNSAT requires separate object/proof verification; no such decision is approved here.',
                               'UNKNOWN and incomplete traces prove neither feasibility nor exclusion.',
                               'Configured resource limits are not peak-resource measurements; no performance claim.'],
                'elapsed_seconds':time.monotonic()-start}
        save(args.out/'summary.json',report);print(json.dumps(dict(status=report['status'],sha256=digest(args.out/'summary.json'))))
    except BaseException as e:save(args.out/'failure.json',dict(error=repr(e)));raise
if __name__=='__main__':main()
