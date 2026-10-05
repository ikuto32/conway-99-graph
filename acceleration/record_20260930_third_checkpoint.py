"""Finite completed wave report from the authoritative ledger and saved audits."""
from collections import Counter
from datetime import datetime,timezone
from hashlib import sha256
import json
import subprocess
import sys
import yaml
from record_20260930_second_checkpoint import ROOT,B,read,h,save

def main():
    raw=(ROOT/'CLAIMS.yaml').read_bytes();ledger=yaml.safe_load(raw)
    snapshot=B+'resume/claims_at_third_milestone.yaml'
    with (ROOT/snapshot).open('xb')as f:f.write(raw)
    ps="Get-CimInstance Win32_Process | Where-Object { ($_.Name -like '*python*' -or $_.Name -like 'moment_pdhg_gpu*') -and $_.CommandLine -like '*conway-99-graph*' } | Select-Object Name,ProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 3"
    command=['powershell','-NoProfile','-Command',ps];observed=subprocess.check_output(command,text=True)
    observation=dict(timestamp=datetime.now(timezone.utc).isoformat(),command=command,processes=json.loads(observed) if observed.strip() else [],limitation='Time-specific matching local processes only; no persistent liveness claim.')
    save(B+'resume/third_milestone_process_observation.json',observation)
    gpu=read(B+'independent_review/eight_gpu_support_run02_claim_binding.json');wave=read(B+'independent_review/rook_lazy_wave01_binding.json')
    new=read(B+'resume/third_milestone_registration.json')['new_claim_ids']
    evidence=[snapshot,B+'resume/third_milestone_process_observation.json',B+'independent_review/eight_gpu_support_run02_claim_binding.json',B+'independent_review/rook_lazy_wave01_binding.json',B+'independent_review/target_gram_support_lemma.json',B+'independent_review/minimized_gram_nogood_claim_binding.json',B+'independent_review/large_gpu_calibration_claim_binding.json']
    out=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),
        previous_report='docs/RESEARCH_20260930_SECOND_WAVE.md',previous_checkpoint_sha256=h(B+'resume/second_milestone_checkpoint.json'),target_resolution='UNKNOWN',external_review=None,external_review_reason='No candidate target resolution is present.',
        claim_population=len(ledger['claims']),claim_status_counts=dict(Counter(c['status'] for c in ledger['claims'])),claim_review_counts=dict(Counter(c['review_state'] for c in ledger['claims'])),verified_clear=sum(c['status']=='VERIFIED' and c['review_state']=='CLEAR' for c in ledger['claims']),new_verified_ids=new,
        gpu_counts=gpu['counts'],gpu_exact_values=gpu['exact_values'],gpu_best_attempt=gpu['best_bound'],
        rook_counts=wave['counts'],rook_distinct_new_raw_graphs=wave['distinct_new_raw59_graphs'],rook_initial_cuts=wave['initial_cuts'],rook_accepted_cuts=wave['accepted_cuts_at_end'],
        completed_experiments=['GPU run01 import failure and six skipped attempts','GPU run02 all three checkpoints and six independently checked support evaluations','Local SAT lazy wave01: nine solver attempts and full independent finite-wave binding'],
        next_experiment='Independently check stronger Gram box cuts before a new bounded local SAT wave.',
        coverage='Overall search coverage: UNKNOWN; no validated denominator.',evidence_sha256={p:h(p) for p in evidence})
    save(B+'resume/third_milestone_checkpoint.json',out)
    print(json.dumps({k:out[k] for k in ['timestamp','source_commit','claim_population','verified_clear']}))

if __name__=='__main__':main()
