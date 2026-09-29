"""Freeze four ledger claims, one checked projection and its single fixed exclusion."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import yaml

ROOT=Path(__file__).resolve().parents[1]
B='acceleration/results/20260930_'


def read(p):return json.loads((ROOT/p).read_bytes())


def h(p):
    with (ROOT/p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def main():
    now=datetime.now(timezone.utc).isoformat();source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    raw=(ROOT/'CLAIMS.yaml').read_bytes();ledger=yaml.safe_load(raw)
    ids=read(B+'tenth_preparation_registration/summary.json')['new_claim_ids']+read(B+'capacity_q1_exclusion_registration/summary.json')['new_claim_ids']
    claims=[c for c in ledger['claims'] if c['id'] in ids]
    assert len(claims)==4 and all(c['status']=='VERIFIED' and c['review_state']=='CLEAR' for c in claims)
    snapshot=B+'resume/claims_at_tenth_milestone.yaml'
    with (ROOT/snapshot).open('xb') as f:f.write(raw)
    artifacts={a['id']:a for a in ledger['artifacts']}
    row=read(B+'independent_review/triangle_capacity_q1_rows/claim_binding.json')
    satpath=B+'triangle_q1_capacity_native_pilot/summary.json';sat=read(satpath)
    assert sat['actual_exit_code']==10 and sat['research_calls']==1
    log=(ROOT/sat['receipt']['stdout']).read_text()
    lines=[s for s in log.splitlines() if s.startswith('c conflicts:')]
    assert len(lines)==1;conflicts=int(lines[0].split()[2])
    command=['wsl.exe','-d','Ubuntu-24.04','--','ps','-C','cadical','-o','pid,etime,pcpu,rss,args']
    observed=datetime.now(timezone.utc).isoformat();process=subprocess.run(command,cwd=ROOT,capture_output=True)
    for suffix,content in [('stdout',process.stdout),('stderr',process.stderr)]:
        with (ROOT/(B+'resume/tenth_process_snapshot.'+suffix+'.log')).open('xb') as f:f.write(content)
    state='CADICAL_PROCESS_OBSERVED' if process.returncode==0 else 'NO_CADICAL_PROCESS_OBSERVED' if process.returncode==1 else 'UNKNOWN_OBSERVATION_ERROR'
    paths={artifacts[aid]['path'] for c in claims for aid in c['evidence']}
    paths.update([snapshot,B+'tenth_preparation_registration/summary.json',B+'capacity_q1_exclusion_registration/summary.json',B+'tenth_artifact_packaging/catalog.json'])
    counts=row['counts']
    record=dict(timestamp=now,source_commit=source,command=[sys.executable,*sys.argv],cwd=str(ROOT),
        previous_report='docs/RESEARCH_20260930_NINTH_WAVE.md',previous_checkpoint_sha256=h(B+'resume/ninth_milestone_checkpoint.json'),
        target_resolution='UNKNOWN',external_review=None,external_review_reason='No validated target graph or general nonexistence proof exists in this repository.',
        claim_population=len(ledger['claims']),verified_clear=sum(c['status']=='VERIFIED' and c['review_state']=='CLEAR' for c in ledger['claims']),
        claim_status_counts=dict(Counter(c['status'] for c in ledger['claims'])),claim_review_counts=dict(Counter(c['review_state'] for c in ledger['claims'])),
        new_verified_ids=ids,projection=dict(variables=19686,clauses=68328,free_primary_entries=600,Gram_entries=576,component_capacities=180),
        completed_native_attempts=1,native_result='SAT',native_exit_code=10,native_conflicts=conflicts,
        wrapper_wall_seconds=sat['receipt']['wall_seconds'],independently_validated_partial_factors=1,
        partial_factor_shape=[24,60],complete36_factors=0,complete99_graphs=0,complete_unsat_traces=0,
        fixed_factor_row_exclusion=counts,newly_excluded_unrestricted_branches=0,
        coverage='Overall search coverage: UNKNOWN; no validated denominator.',
        execution=dict(observed_at=observed,command=command,exit_code=process.returncode,state=state,
            stdout_sha256=h(B+'resume/tenth_process_snapshot.stdout.log'),stderr_sha256=h(B+'resume/tenth_process_snapshot.stderr.log'),
            scope='The recorded projection solver and all12 row searches have completed; any observed solver belongs to a separate later experiment.'),
        next_experiment='Jointly choose the free Q1 incidence block and one C2 row, with explicit target-necessary column-pair caps; independently audit the new scope, encoding and object checker before native search.',
        evidence_sha256={p:h(p) for p in sorted(paths)})
    with (ROOT/(B+'resume/tenth_milestone_checkpoint.json')).open('x',encoding='utf-8',newline='\n') as f:json.dump(record,f,indent=2);f.write('\n')
    rows='\n'.join('| `'+c['id']+'` | '+c['scope']['description']+' [Audit](../'+artifacts[c['evidence'][0]]['path']+'). |' for c in claims)
    text=f'''# Tenth resumed milestone, 2026-09-30 JST

Four independently verified claims were added since the [ninth milestone](RESEARCH_20260930_NINTH_WAVE.md). A smaller necessary projection produced a valid capacity-compatible 24x60 partial factor. Complete row proofs then excluded that exact factor from extending to the target. An independent block derivation also established the conditional residual-completion equations.

**As of:** {now}; source commit `{source}`. [Checkpoint](../{B}resume/tenth_milestone_checkpoint.json), [ledger snapshot](../{snapshot}); previous report: ninth milestone.

**Verdict:** target resolution UNKNOWN. This repository has neither an independently validated target graph nor a general nonexistence proof. No target candidate is under external review. [Draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3) remains unmerged. This is not a worldwide literature verdict.

**Verified changes:** all four records are revision 1.

| Claim | Exact scope and evidence |
| --- | --- |
{rows}

**Work completed:** the projection leaves 600 C1 entries free and encodes 282 exact equations plus 180 component-capacity inequalities in 19,686 variables and 68,328 clauses. Its exact equivalence was independently checked before the native call, as was a separately authored object checker. One native attempt returned SAT after {conflicts:,} conflicts, with wrapper wall time {sat['receipt']['wall_seconds']:.3f}s. This is a single-run measurement, not a performance comparison. Independent checking confirmed every clause, all 576 principal Gram entries, row and fibre margins, all 180 capacities, and the complete Q1 permutation. Five additional corruptions of the actual artifact were rejected.

The verified 24x60 construction is a partial factor, not a full 36x60 factor or a 99-vertex graph. All twelve possible C2 row positions were then tested separately with that Q1 fixed. Their complete contradiction trees contain 2,774 nodes, 1,381 exhaustive splits and 1,393 contradiction leaves. The independent reviewer rebuilt all 9,801 entries of the raw partial graph and checked every constraint, branch and individual forced bit. Fifty fresh corruption controls were rejected. These are twelve explanations of **one fixed-configuration exclusion**, not twelve disjoint excluded graph families. Other capacity-compatible Q1 choices remain unclassified.

For a future validated full factor F, exact block multiplication proves that the residual symmetric binary zero-diagonal 60x60 D completes the target if and only if FD=2J-F-CF and D^2+F^TF=12I-D+2J. Its degree 8 follows from the diagonal. This is a conditional equivalence with no existence premise supplied. Necessary local screens were checked algebraically; no residual search or target-sized positive F was fabricated.

**Coverage:** Overall search coverage: UNKNOWN; no validated denominator. No unrestricted branch or entire fixed-core family is excluded. One partial factor was generated by one SAT attempt, one partial factor was independently validated, and the same factor was excluded from target completion. These stages overlap and are not added. Ledger population: {len(ledger['claims'])} claims, {record['verified_clear']} VERIFIED/CLEAR and 2 CANDIDATE/CLEAR.

**Best result:** an exact capacity-compatible partial factor and complete direct proofs showing why it fails to extend. This identifies a limitation of selecting Q1 before testing a missing row; it provides no target-level bound.

**Problems:** the component-capacity filter is necessary but insufficient. The row exclusions use necessary target conditions and do not prove that the whole abstract factor family is infeasible. Passing individual row tests would still not establish simultaneous compatibility. The residual equivalence is independently derived, but a full SAT encoding or exhaustive residual-domain search would require new gates.

**Execution:** the SAT attempt and all twelve row searches are complete. A fresh observation at {observed} returned `{state}`; its exact command and logs are in the checkpoint. Any observed process concerns separate subsequent work, not these completed outcomes. The user's continuation instruction remains active.

**Next experiment:** jointly choose Q1 and one C2 row, adding explicit target-necessary column-pair caps. The new model must distinguish target necessity from implications of the abstract Gram-only factor problem. Independently check its exact encoding and complete-object validator before native search.

**References:** [source commit](https://github.com/ikuto32/conway-99-graph/commit/{source}), [draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3), [artifact catalog](../{B}tenth_artifact_packaging/catalog.json), [replay guide](REPRODUCING_20260930_TENTH_WAVE.md). PUBLIC pointers require immutable remote publication confirmation.
'''
    with (ROOT/'docs/RESEARCH_20260930_TENTH_WAVE.md').open('x',encoding='utf-8',newline='\n') as f:f.write(text)
    print(json.dumps(dict(claims=len(ledger['claims']),verified_clear=record['verified_clear'],native_state=state,target_resolution='UNKNOWN')))


if __name__=='__main__':main()
