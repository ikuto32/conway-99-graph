"""Freeze ledger-derived ninth-wave counts and actually completed native outcomes."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
B = 'acceleration/results/20260930_'


def read(path):
    return json.loads((ROOT/path).read_bytes())


def digest(path):
    with (ROOT/path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def save(path, value):
    with (ROOT/path).open('x', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, indent=2)
        f.write('\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--native-audit', required=True)
    args = ap.parse_args()
    now = datetime.now(timezone.utc).isoformat()
    source = subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip()
    raw = (ROOT/'CLAIMS.yaml').read_bytes()
    ledger = yaml.safe_load(raw)
    ids = read(B+'ninth_registration/summary.json')['new_claim_ids']
    claims = [c for c in ledger['claims'] if c['id'] in ids]
    assert len(claims)==7 and all(c['status']=='VERIFIED' and c['review_state']=='CLEAR' for c in claims)
    snapshot = B+'resume/claims_at_ninth_milestone.yaml'
    with (ROOT/snapshot).open('xb') as f:
        f.write(raw)
    artifacts = {a['id']:a for a in ledger['artifacts']}
    scout = read(B+'independent_review/triangle_q1_binary_scout/summary.json')
    components = read(B+'independent_review/triangle_factor_components/summary.json')
    runs = []
    for name in ['triangle_joint_factor_native_pilot','triangle_component_factor_native_pilot']:
        path = B+name+'/summary.json'
        r = read(path)
        assert r['actual_exit_code']==0 and r['interpreted_result']=='UNKNOWN_NATIVE_OR_RESOURCE_OUTCOME'
        log = (ROOT/r['receipt']['stdout']).read_text()
        conflict_lines = [s for s in log.splitlines() if s.startswith('c conflicts:')]
        assert len(conflict_lines)==1, conflict_lines
        conflicts = int(conflict_lines[0].split()[2])
        runs.append(dict(name=name, summary=path, summary_sha256=digest(path),
            configured_conflicts=1000000, reported_conflicts=conflicts,
            result='UNKNOWN', research_attempts=1, actual_exit_code=r['actual_exit_code'],
            wrapper_wall_seconds=r['receipt']['wall_seconds'],
            incomplete_trace=dict(path=B+name+'/main/proof.drat',sha256=r['proof_copy']['sha256'],
                                  bytes=r['proof_copy']['bytes'],availability='LOCAL_ONLY'),
            proof_status='Incomplete trace; no UNSAT claim and no refutation replay.'))
    command = ['wsl.exe','-d','Ubuntu-24.04','--','ps','-C','cadical','-o','pid,etime,pcpu,rss,args']
    observed = datetime.now(timezone.utc).isoformat()
    process = subprocess.run(command, cwd=ROOT, capture_output=True)
    for suffix, content in [('stdout',process.stdout),('stderr',process.stderr)]:
        with (ROOT/(B+'resume/ninth_process_snapshot.'+suffix+'.log')).open('xb') as f:
            f.write(content)
    state = 'CADICAL_PROCESS_OBSERVED' if process.returncode==0 else 'NO_CADICAL_PROCESS_OBSERVED' if process.returncode==1 else 'UNKNOWN_OBSERVATION_ERROR'
    paths = {artifacts[aid]['path'] for c in claims for aid in c['evidence']}
    paths.update([snapshot,B+'ninth_registration/summary.json',B+'ninth_artifact_packaging/catalog.json',args.native_audit])
    record = dict(timestamp=now, source_commit=source, command=[sys.executable,*sys.argv],cwd=str(ROOT),
        previous_report='docs/RESEARCH_20260930_EIGHTH_WAVE.md',
        previous_checkpoint_sha256=digest(B+'resume/eighth_milestone_checkpoint.json'),
        target_resolution='UNKNOWN', external_review=None,
        external_review_reason='No internally verified target resolution exists; no target candidate is submitted for external review.',
        claim_population=len(ledger['claims']),
        verified_clear=sum(c['status']=='VERIFIED' and c['review_state']=='CLEAR' for c in ledger['claims']),
        claim_status_counts=dict(Counter(c['status'] for c in ledger['claims'])),
        claim_review_counts=dict(Counter(c['review_state'] for c in ledger['claims'])),
        new_verified_ids=ids, q1_checked_population=scout['counts'],
        component_overflow_counts=components['overflow_counts'],
        native_attempts=runs, completed_native_attempts=len(runs), complete_proofs=0, decoded_factors=0,
        newly_excluded_unrestricted_branches=0,
        coverage='Overall search coverage: UNKNOWN; no validated denominator.',
        execution=dict(observed_at=observed,command=command,exit_code=process.returncode,state=state,
            stdout_sha256=digest(B+'resume/ninth_process_snapshot.stdout.log'),
            stderr_sha256=digest(B+'resume/ninth_process_snapshot.stderr.log'),
            scope='Fresh CaDiCaL observation, not a promise about future processes; both listed pilots have ended.'),
        next_experiment='Independently gate and solve the necessary Q1-only binary factor projection with component-capacity inequalities; validate any raw factor or complete proof.',
        evidence_sha256={p:digest(p) for p in sorted(paths)})
    save(B+'resume/ninth_milestone_checkpoint.json', record)
    rows = '\n'.join('| `'+c['id']+'` | '+c['scope']['description']+' [Audit](../'+artifacts[c['evidence'][0]]['path']+'). |' for c in claims)
    text = f'''# Ninth resumed milestone, 2026-09-30 JST

Seven independently checked claims were added since the [eighth milestone](RESEARCH_20260930_EIGHTH_WAVE.md). Three new fixed factors are exactly excluded; a component-kernel argument gives short obstructions for all five saved factors. Two broader binary-factor encodings are verified, but both bounded native attempts ended UNKNOWN.

**As of:** {now}; source commit `{source}`. [Checkpoint](../{B}resume/ninth_milestone_checkpoint.json), [ledger snapshot](../{snapshot}); previous report: eighth milestone.

**Verdict:** target resolution UNKNOWN. This repository has neither an independently validated 99-vertex target graph nor a general nonexistence proof. No candidate target resolution is under external review. [Draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3) remains unmerged. This is not a worldwide literature verdict.

**Verified changes:** all seven records are revision1.

| Claim | Exact scope and evidence |
| --- | --- |
{rows}

**Work completed:** three new saved binary24x60 factors pass all1,728 prescribed Gram-entry checks and exact margins. Together with the two freshly checked archived factors, they occupy five disjoint orbits under the specified384 coordinate relabelings. This is neither general graph nonisomorphism nor a census of all factors. Three complete row27 obstruction trees contain655 checked nodes,326 exhaustive splits and329 contradictions. They exclude precisely those three fixed configurations.

For the chosen39vertex core, exact component-kernel identities force every completed36x60 factor column to contain two entries in each of three components. The five saved two-cell factors have respectively3,1,1,1,1 overflow columns, so none extends even by a nonnegative third block. These shorter proofs overlap the existing fixed exclusions and add no further coverage.

The base factor CNF has58,860 variables and203,748 clauses. Its strengthened equivalent has61,296 variables and212,580 clauses, adding180 necessary component equations. Each allows both unknown incidence blocks to vary; neither encodes the residual60vertex graph. Independent encoding checks and separately calibrated complete-factor checkers preceded the native attempts. No valid36x60 factor with the actual research Gram is known; synthetic positive controls are labelled accordingly.

**Execution:** two distinct inputs each received one native attempt, both completed UNKNOWN with exit0. The configured conflict limit was1,000,000; the logs report {runs[0]['reported_conflicts']:,} and {runs[1]['reported_conflicts']:,} conflicts respectively. The second count exceeds the configured limit by two and is preserved as observed. Wrapper wall times are {runs[0]['wrapper_wall_seconds']:.3f}s and {runs[1]['wrapper_wall_seconds']:.3f}s; these are single attempts on different formulas, not a controlled speed comparison. The incomplete traces are574,434,634 and646,423,799 bytes and remain LOCAL_ONLY. Neither is an UNSAT certificate. [Independent run audit](../{args.native_audit}). A fresh observation at {observed} returned `{state}`; the checkpoint includes its exact command and raw logs.

**Coverage:** Overall search coverage: UNKNOWN; no validated denominator. No unrestricted branch is closed. The saved five-factor population is not exhaustive. Ledger population: {len(ledger['claims'])} claims, {record['verified_clear']} VERIFIED/CLEAR and2 CANDIDATE/CLEAR. No claim in this milestone establishes fixed-core nonexistence.

**Best result:** exact short conditional obstructions and independently verified broader factor encodings. No target-level bound or graph was obtained.

**Problems:** the first factor-checker corruption fixture accidentally shared mutable row objects. That calibration failure and its separately frozen correction are retained. New row-wrapper controls were added after the scout, with their timing disclosed. The scout's512,000 annealing swaps and final G01-only integer score24 are unreplayed heuristic telemetry, not certified search coverage. No exact factor was found by that heuristic batch. The UNKNOWN solver traces are retained locally, while exact inputs, logs and receipts are public payload candidates.

**Next experiment:** independently gate and solve the necessary Q1-only binary factor projection with component-capacity inequalities. A satisfying factor would establish only that projection; UNSAT requires full proof replay and would remain conditional on this core. Residual-D completion conditions are being investigated separately and are outside these seven claims. The user's continuation instruction remains active.

**References:** [source commit](https://github.com/ikuto32/conway-99-graph/commit/{source}), [draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3), [artifact catalog](../{B}ninth_artifact_packaging/catalog.json), [reproduction guide](REPRODUCING_20260930_NINTH_WAVE.md). Immutable PUBLIC pointers are set only after remote publication confirmation.
'''
    with (ROOT/'docs/RESEARCH_20260930_NINTH_WAVE.md').open('x', encoding='utf-8', newline='\n') as f:
        f.write(text)
    print(json.dumps(dict(claims=len(ledger['claims']),verified_clear=record['verified_clear'],native_state=state,target_resolution='UNKNOWN')))


if __name__ == '__main__':
    main()
