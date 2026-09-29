"""Generate a dated registry/run checkpoint from saved records and live observation."""
from collections import Counter
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import yaml

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'
def read(p):return json.loads((ROOT/p).read_bytes())
def h(p):return sha256((ROOT/p).read_bytes()).hexdigest()
def save(p,v):
    with (ROOT/p).open('x',encoding='utf-8') as f:json.dump(v,f,indent=2);f.write('\n')

def main():
    ledger=yaml.safe_load((ROOT/'CLAIMS.yaml').read_bytes())
    snapshot=B+'resume/claims_at_second_milestone.yaml'
    with (ROOT/snapshot).open('xb')as f:f.write((ROOT/'CLAIMS.yaml').read_bytes())
    ps="Get-CimInstance Win32_Process | Where-Object { ($_.Name -like '*python*' -or $_.Name -like 'moment_pdhg_gpu*') -and $_.CommandLine -like '*conway-99-graph*' } | Select-Object Name,ProcessId,CreationDate,CommandLine | ConvertTo-Json -Depth 3"
    command=['powershell','-NoProfile','-Command',ps]
    observed=subprocess.check_output(command,text=True)
    observation=dict(timestamp=datetime.now(timezone.utc).isoformat(),command=command,processes=json.loads(observed) if observed.strip() else [],limitation='Only matching local Python/native processes at the stated time; this is not persistent liveness.')
    save(B+'resume/second_milestone_process_observation.json',observation)
    first=read(B+'resume/first_milestone_checkpoint.json')
    regs=[read(B+'resume/'+p) for p in ['rook_fixed_star_registration.json','second_milestone_registration.json']]
    new=[i for r in regs for i in r['new_claim_ids']]
    evidence={p:h(p) for p in [snapshot,B+'resume/second_milestone_process_observation.json',
        B+'independent_review/eight_matching_filter_claim_binding.json',B+'independent_review/eight_filtered_moments/summary.json',
        B+'rook_sat_independent_proof/summary.json',B+'rook_free_internal_independent_certificate/summary.json',
        B+'independent_review/rook_original_gram.json',B+'independent_review/eight_gpu_support_run01.json',
        B+'independent_review/large_gpu_cpu_parity/summary.json']}
    checkpoint=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        command=[sys.executable,*sys.argv],cwd=str(Path.cwd()),previous_report='docs/RESEARCH_20260930_FIRST_WAVE.md',
        previous_checkpoint_sha256=h(B+'resume/first_milestone_checkpoint.json'),target_resolution='UNKNOWN',external_target_review=None,external_target_review_reason='No candidate target resolution exists in this repository.',
        claim_population=len(ledger['claims']),claim_status_counts=dict(Counter(c['status'] for c in ledger['claims'])),claim_review_counts=dict(Counter(c['review_state'] for c in ledger['claims'])),
        verified_clear=sum(c['status']=='VERIFIED' and c['review_state']=='CLEAR' for c in ledger['claims']),new_verified_ids=new,
        matching_filter=read(B+'independent_review/eight_matching_filter_claim_binding.json')['counts'],
        moment_model=dict(rows=5730,columns=1882186,probability_choices=1875214,slacks=6972,nonzeros=156321767,independent_verification='ALL_ENTRIES'),
        rook_fixed_star=dict(edge_variables=600,clauses=819840,result='UNSAT',complete_independent_proof_replay='PASS',scope='Exact fixed central star and five internal matchings only'),
        rook_free_internal=dict(edge_variables=780,clauses=3689820,result='SAT_LOCAL59',complete_independent_clause_and_graph_check='PASS',one_graph_target_extension='EXCLUDED_BY_EXACT_GRAM'),
        gpu_first_attempt=dict(result='IMPORT_CAP_ERROR',native_returncode=2,completed_checkpoints=0,independently_checked_skips=6,exact_bound_evaluations=0),
        live_execution_observation=B+'resume/second_milestone_process_observation.json',
        coverage='Overall search coverage: UNKNOWN; no validated denominator.',
        exact_six_family_bound='14157/16384',bound_scope='Earlier 132-fixed-K family; not an eight-family bound or target-wide metric.',
        next_experiment='Complete the larger-input eight-coordinate GPU retry and independently evaluate each of its six recorded exact support attempts.',
        evidence_sha256=evidence)
    save(B+'resume/second_milestone_checkpoint.json',checkpoint)
    print(json.dumps({k:checkpoint[k] for k in ['timestamp','source_commit','claim_population','verified_clear','new_verified_ids']}))

if __name__=='__main__':main()
