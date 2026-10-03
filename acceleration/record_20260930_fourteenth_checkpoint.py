"""Freeze ledger-backed finite engineering/normalization results, without a target verdict."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
B = 'acceleration/results/20260930_'


def read(p): return json.loads((ROOT / p).read_bytes())
def h(p):
    with (ROOT / p).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()
def save(p, obj):
    with (ROOT / p).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(obj, stream, indent=2)
        stream.write('\n')


def main():
    now = datetime.now(timezone.utc).isoformat()
    source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    raw = (ROOT / 'CLAIMS.yaml').read_bytes()
    ledger = yaml.safe_load(raw)
    registrations = [B + s + '/summary.json' for s in ('fourteenth_gpu_registration', 'fourteenth_pair_modular_registration', 'fourteenth_factor_results_registration')]
    ids = [cid for p in registrations for cid in read(p)['new_claim_ids']]
    claims = [c for c in ledger['claims'] if c['id'] in ids]
    assert len(ids) == len(set(ids)) == len(claims) == 8
    assert len(ledger['claims']) == 138
    assert all(c['status'] == 'VERIFIED' and c['review_state'] == 'CLEAR' and c['revision'] == 1 for c in claims)
    artifacts = {a['id']: a for a in ledger['artifacts']}
    runs = []
    for name, expected_code, outcome in [('variable_core_pair_orbits', 0, 'UNKNOWN_CONFLICT_LIMIT'), ('prism_column_caps', 124, 'UNKNOWN_TIMEOUT')]:
        path = B + name + '_native_pilot/summary.json'
        audit = B + 'independent_review/' + name + '_unknown/summary.json'
        r, a = read(path), read(audit)
        assert r['actual_exit_code'] == expected_code and r['research_calls'] == 1
        assert a['status'].endswith('_PASS'), a['status']
        log = (ROOT / r['receipt']['stdout']).read_text()
        conflicts = re.findall(r'^c conflicts:\s+(\d+)\s', log, re.M)
        assert len(conflicts) == 1 and not re.search(r'^s (?:SATISFIABLE|UNSATISFIABLE)$', log, re.M)
        runs.append(dict(name=name, result=outcome, attempts=1, exit_code=expected_code,
            summary=path, summary_sha256=h(path), audit=audit, audit_sha256=h(audit),
            observed_conflicts=int(conflicts[0]), configured_conflicts=5000000, configured_seconds=900,
            wrapper_wall_seconds=r['receipt']['wall_seconds'], incomplete_trace_bytes=r['proof_copy']['bytes'],
            incomplete_trace_sha256=r['proof_copy']['sha256'], incomplete_trace_availability='LOCAL_ONLY'))
    pilot_path = B + 'independent_review/factor_annealer_pilot/summary.json'
    cooling_path = B + 'independent_review/factor_annealer_cooling_v3/summary.json'
    failure_path = B + 'factor_annealer_cooling/summary.json'
    pilot, cooling, failed = read(pilot_path), read(cooling_path), read(failure_path)
    assert pilot['completed_cases'] == 6 and cooling['stage_counts']['completed'] == 4
    assert failed['completed_new_proposals'] == 0 and failed['errors'] == 2 and failed['skipped_stages'] == 2
    gpu = dict(objective_version=pilot['objective_version'],
        objective_definition='Sum of squared integer residuals of the three cross-fibre 12x12 Gram blocks; minimize over the fixed-core permutation domains.',
        acceptance_method='Floating double exponential simulated annealing guides search; scores below are independently checked exact integers.',
        pilot=dict(completed_cases=pilot['completed_cases'], proposal_records=pilot['saved_proposal_records'],
            chunk_best_states=pilot['chunk_best_states'], final_current_states=pilot['final_current_states'],
            final_best_states=pilot['final_best_states'],
            minima=[dict(label=c['case']['label'], value=c['minimum_saved_score']) for c in pilot['cases']]),
        failed_cooling=dict(attempted_stages=failed['attempted_stages'], completed_stages=failed['completed_stages'],
            errors=failed['errors'], skipped_stages=failed['skipped_stages'], new_proposal_records=0),
        corrected_cooling=dict(completed_stages=cooling['stage_counts']['completed'], proposal_records=cooling['new_saved_proposal_records'],
            continuing_chains=cooling['continued_chain_population'], chunk_best_states=cooling['chunk_best_states'],
            stage_final_current_states=cooling['stage_final_current_states'], stage_final_best_states=cooling['stage_final_best_states'],
            minima=[dict(label=c['case']['label'], initial=c['initial_best_score'], final=c['final_best_score']) for c in cooling['cases']]),
        individual_campaign_transitions_replayed=False, exact_zero_saved_factors=0,
        limitation='Stages and state populations overlap; proposal records are not distinct factors. Positive scores are neither bounds nor exclusions.')
    command = ['wsl.exe', '-d', 'Ubuntu-24.04', '--', 'ps', '-C', 'cadical', '-o', 'pid,etime,pcpu,rss,args']
    observed = datetime.now(timezone.utc).isoformat()
    ps = subprocess.run(command, cwd=ROOT, capture_output=True)
    for channel, content in [('stdout', ps.stdout), ('stderr', ps.stderr)]:
        with (ROOT / (B + 'resume/fourteenth_process_snapshot.' + channel + '.log')).open('xb') as stream:
            stream.write(content)
    state = 'CADICAL_PROCESS_OBSERVED' if ps.returncode == 0 else 'NO_CADICAL_PROCESS_OBSERVED' if ps.returncode == 1 else 'UNKNOWN_OBSERVATION_ERROR'
    snapshot = B + 'resume/claims_at_fourteenth_milestone.yaml'
    with (ROOT / snapshot).open('xb') as stream: stream.write(raw)
    paths = {artifacts[aid]['path'] for c in claims for aid in c['evidence']}
    paths.update(registrations + [snapshot, pilot_path, cooling_path, failure_path, B + 'fourteenth_artifact_packaging/catalog.json'])
    paths.update(p for r in runs for p in (r['summary'], r['audit']))
    record = dict(timestamp=now, source_commit=source, command=[sys.executable, *sys.argv], cwd=str(ROOT),
        previous_report='docs/RESEARCH_20260930_THIRTEENTH_WAVE.md', previous_checkpoint_sha256=h(B + 'resume/thirteenth_milestone_checkpoint.json'),
        target_resolution='UNKNOWN', external_review=None, external_review_null_reason='No internally validated target graph or general nonexistence proof.',
        claim_population=len(ledger['claims']), verified_clear=sum(c['status'] == 'VERIFIED' and c['review_state'] == 'CLEAR' for c in ledger['claims']),
        claim_status_counts=dict(Counter(c['status'] for c in ledger['claims'])), claim_review_counts=dict(Counter(c['review_state'] for c in ledger['claims'])),
        new_verified_ids=ids, native_runs=runs, completed_native_attempts=2, native_SAT_results=0, native_UNSAT_results=0, native_UNKNOWN_results=2,
        gpu=gpu, complete99_graphs=0, independently_validated_new_target_factors=0, new_complete_unsat_traces=0, newly_closed_unrestricted_branches=0,
        coverage='Overall search coverage: UNKNOWN; no validated denominator.',
        execution=dict(observed_at=observed, command=command, exit_code=ps.returncode, state=state,
            stdout_sha256=h(B + 'resume/fourteenth_process_snapshot.stdout.log'), stderr_sha256=h(B + 'resume/fourteenth_process_snapshot.stderr.log'),
            scope='Named cohort searches completed. Any newly observed connected-core experiment belongs to a later cohort.'),
        next_experiment='Run the independently gated fixed-core SAT instances for the four selected connected identity-P cores, with complete object checking before residual completion.',
        evidence_sha256={p: h(p) for p in sorted(paths)})
    save(B + 'resume/fourteenth_milestone_checkpoint.json', record)
    rows = '\n'.join('| `' + c['id'] + '` | ' + c['scope']['description'] + ' [Evidence](../' + artifacts[c['evidence'][0]]['path'] + '). |' for c in claims)
    runrows = '\n'.join('| ' + r['name'] + ' | ' + r['result'] + ' | ' + str(r['observed_conflicts']) + ' | ' + f"{r['wrapper_wall_seconds']:.3f}" + ' |' for r in runs)
    report = f'''# Fourteenth resumed milestone, 2026-09-30 JST

Eight verified claims were added since the [thirteenth milestone](RESEARCH_20260930_THIRTEENTH_WAVE.md): finite GPU calibration and saved-state results, a public-checkpoint repair and its diagnosed failure, ordered-matching-pair normalization, a finite failed modular route, and the six-prism column-cap encoding. No target resolution or exclusion was obtained.

**As of:** {now}; source commit `{source}`. [Checkpoint](../{B}resume/fourteenth_milestone_checkpoint.json), [ledger snapshot](../{snapshot}); previous report: thirteenth milestone.

**Verdict:** target resolution UNKNOWN. This repository has no independently validated target graph or general nonexistence proof. No target resolution is under external review. [Draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3) remains unmerged. This is not a worldwide literature verdict.

**Verified changes:** all eight claims are revision1. Verification applies only to each exact statement and scope.

| Claim | Exact scope and evidence |
| --- | --- |
{rows}

**Work completed:** the ordered-pair reduction checks114,345 second-stage matching transports, covering the108,056,025 labelled ordered matching pairs through the separately checked first-stage normalization. It leaves P arbitrary and assumes no target automorphism. Its114,484-variable,561,121-clause model remains a necessary factor problem without residual D. The fixed six-prism model adds all required Y-column overlap caps and has247,320 variables and920,401 clauses. Independent full decoded-object checking paths were calibrated before either native run.

| Completed native attempt | Result | Observed conflicts | Wrapper seconds |
| --- | --- | ---: | ---: |
{runrows}

Each had one attempt with900 seconds and five million configured conflicts plus memory/file guards. Independent execution audits bind inputs, receipts, logs and the complete retained incomplete trace bytes. Neither trace is a checked UNSAT certificate. Different formulas and stops do not establish a performance comparison.

The initial GPU pilot completed6 cases and saved786,432 proposal records. Independent checking covered48 chunk-best,96 final-current and96 final-best raw states, plus all768 current and768 best checkpoint scores. The first cooling attempt failed in2 stages before any GPU proposals and skipped2 dependent stages: Python tuples did not match lists restored from JSON. The corrected public-resume path passed fresh independent calibration. Corrected cooling completed4 stages and1,048,576 new proposal records across32 continuing chains, with64 chunk-best,64 stage-final-current and64 stage-final-best objects and all1,024 current and1,024 best checkpoint scores independently checked. These overlapping stage populations are not summed; individual campaign transitions were not replayed.

The finite modular route independently reconstructed128 trials over each of GF(2) and GF(3) on the243-vertex fixture. All256 retained the tested mixed-kernel compatibility. This is neither a universal redundancy theorem nor a target exclusion. Original successful perturbation matrices were not saved; the independent reconstruction preserves new vectors and hashes without claiming to authenticate absent originals.

**Coverage:** Overall search coverage: UNKNOWN; no validated denominator. No unrestricted branch or fixed core was excluded. The ledger contains138 claims:136 VERIFIED/CLEAR and2 CANDIDATE/CLEAR.

**Best result:** under `TRIANGLE_FACTOR_CROSS_GRAM_SQUARED_V1`, the exact saved minimum decreased164→134→124 for shift6 and184→146→142 for six-prism. This objective minimizes the sum of squared residuals of three cross-fibre Gram blocks on their fixed permutation domains. These positive heuristic-search scores are not mathematical bounds. Even objective zero would require further constraints and residual completion before yielding a target graph.

**Problems:** both native attempts ended UNKNOWN; no factor was found. Preserved failures include the original CUDA compile error, actual public-resume mismatch, two cap-builder preparation failures, the first pair-audit indexing error, and catalog control-binding omissions. The original premature PUBLIC metadata is retained with an explicit correction. Native binaries and incomplete traces remain LOCAL_ONLY. Large GPU records and cap inputs have lossless public recovery packages after publication. The GF2 conditional lemma and connected-core portfolio belong to a later cohort and are excluded from these totals.

**Execution:** cohort searches completed. Fresh native process observation at {observed}: `{state}`. Exact process logs are saved in the checkpoint; any observed connected-core run belongs to a later cohort. The user's continuation instruction remains active.

**Next experiment:** execute the independently gated necessary-factor SAT instances for the four selected connected identity-P cores. A SAT object requires complete independent clause/raw-factor checks and then residual completion; checked UNSAT would concern only its fixed core.

**References:** [source commit](https://github.com/ikuto32/conway-99-graph/commit/{source}), [draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3), [catalog](../{B}fourteenth_artifact_packaging/catalog.json), [replay guide](REPRODUCING_20260930_FOURTEENTH_WAVE.md). Immutable publication pointers follow remote confirmation.
'''
    with (ROOT / 'docs/RESEARCH_20260930_FOURTEENTH_WAVE.md').open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(report)
    print(json.dumps(dict(claims=138, verified_clear=record['verified_clear'], native_state=state, target_resolution='UNKNOWN')))


if __name__ == '__main__': main()
