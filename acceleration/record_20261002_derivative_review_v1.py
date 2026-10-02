"""Save root's explicit continuation reassessment using fresh observed records.

No timeout extension, automatic retries, or mathematical progress estimate.
"""
from datetime import datetime,timezone
from pathlib import Path
import hashlib,json,os

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'acceleration/results/20261002_drat_derivative_native01'
OUTER=ROOT/'acceleration/results/20261002_drat_derivative_native_supervision01'
DEST=ROOT/'acceleration/results/20261002_drat_derivative_native_review01.json'


def main():
    out=ROOT/'acceleration/results/20261002_drat_derivative_reassessment01'
    out.mkdir(parents=True,exist_ok=False)
    raw=(RUN/'progress.json').read_bytes();progress=json.loads(raw)
    outer_raw=(OUTER/'progress.jsonl').read_bytes().splitlines()[-1];outer=json.loads(outer_raw)
    manifest=json.loads((OUTER/'manifest.json').read_bytes())
    stamp=datetime.now(timezone.utc)
    for source in [progress,outer]:
        age=(stamp-datetime.fromisoformat(source['timestamp'])).total_seconds()
        if not 0<=age<50:raise ValueError('Recent real observations required')
    processes=progress['current_processes']['matching_processes']
    if not processes or progress['phase']!='native':raise ValueError('Native work no longer observed; reassess new state')
    resource=progress['resources']['linux_native_processes']
    observed=dict(timestamp=stamp.isoformat(),producer_progress=progress,outer_progress=outer,
        recent_native_stdout_tail=(RUN/'instance/solver.stdout.log').read_text(errors='replace').splitlines()[-18:],
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    review=dict(invocation_id=manifest['invocation_id'],observed_at_elapsed_seconds=outer['elapsed_seconds'],
        observed_at_producer_elapsed_seconds=progress['elapsed_seconds'],decision='continue',
        observations='Exact native process remains observed; CPU time and logged conflict/inference counters advance. Observed resources: '+json.dumps(resource)+'. No SAT/UNSAT outcome or target certificate yet.',
        remaining_cost='Producer has %.3f wall seconds remaining in its immutable2050-second allocation. Native guard remains1800 seconds and the declared150-second transfer/shutdown reserve stays in force. No hard deadline is extended.'%progress['remaining_seconds'],
        benefit_and_alternatives='Complete the predeclared single continuation beyond the earlier300-second pilot while exact structural rerooted-count falsification runs separately. Learning-state inference remains active, and the observed memory is below the8GiB guard. An eventual complete result has higher value than these raw conflict counters; alternate structural/search methods remain available.',
        uncertainty='No calibrated success probability, target-wide coverage denominator, or monotone solution-quality metric exists. Increasing conflicts or trace size does not prove approach success or nonexistence. A timeout will preserve raw evidence and require another method/continuation review.',
        success_probability=None,calibration_evidence=None)
    (out/'observations.json').write_text(json.dumps(observed,indent=2)+'\n',encoding='utf8',newline='\n')
    pending=out/'review.pending.json';pending.write_text(json.dumps(review,indent=2)+'\n',encoding='utf8',newline='\n')
    os.replace(pending,DEST)
    (out/'review.json').write_bytes(DEST.read_bytes())
    print(json.dumps(dict(status='ROOT_EXPLICIT_CONTINUATION_REVIEW_SAVED',invocation_id=review['invocation_id'],producer_elapsed_seconds=progress['elapsed_seconds'],hard_deadline_extended=False)))


if __name__=='__main__':main()
