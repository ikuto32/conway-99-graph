"""Read-only post-run trace availability observation; no rerun or deletion."""
from pathlib import Path
from datetime import datetime, timezone
import sys, subprocess
import native_20260930_unrestricted_full99 as h

def main():
    root=h.ROOT
    batch=root/'acceleration/results/20260930_hadamard_parity_phase_batch_pilot'
    out=root/'acceleration/results/20260930_hadamard_batch_trace_availability'
    out.mkdir(exist_ok=False)
    original=h.read(batch/'summary.json')
    records=[]
    for item in original['cases']:
        path=item['trace']['linux_path']
        receipt=h.run_record([*h.WSL,'/usr/bin/stat','--format=%s','--',path],out/f"case_{item['index']:02d}_stat",10)
        records.append(dict(index=item['index'],linux_path=path,receipt=receipt,
            historical_sha256=item['trace'].get('sha256'),historical_bytes=item['trace'].get('bytes'),
            availability='LOCAL_ONLY' if receipt['actual_exit_code']==0 else 'MISSING',
            retrieval=None,retrieval_null_reason='Original path unavailable; no alternate copy has been identified.' if receipt['actual_exit_code']!=0 else 'Original recorded path.'))
    observations={}
    for name,command in [('uptime',['/usr/bin/cat','/proc/uptime']),('temp_policy',['/usr/bin/cat','/usr/lib/tmpfiles.d/tmp.conf']),('target_process',['/usr/bin/pgrep','-x','cadical'])]:
        observations[name]=h.run_record([*h.WSL,*command],out/name,10)
    h.save(out/'summary.json',dict(status='POST_BATCH_TRACE_AVAILABILITY_OBSERVATION',timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(root),
        inputs_sha256={h.key(batch/'summary.json'):h.digest(batch/'summary.json'),h.key(Path(__file__)):h.digest(__file__)},
        records=records,observations=observations,solver_calls=0,deleted_files=0,
        cause=None,cause_null_reason='Availability is observed; the cause of disappearance is not established.',
        mathematical_impact='No UNSAT claim exists. Saved complete SAT assignments and literal GF3 exclusion certificates remain available and independently checkable without learned traces.',
        outputs_sha256={h.key(p):h.digest(p) for p in out.iterdir() if p.is_file()}))

if __name__=='__main__':main()
