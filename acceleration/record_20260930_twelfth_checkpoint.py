"""Freeze universal-factor and complete-column claims, with two UNKNOWN runs."""
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
B = 'acceleration/results/20260930_'


def read(p):
    return json.loads((ROOT/p).read_bytes())


def h(p):
    with (ROOT/p).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def main():
    now = datetime.now(timezone.utc).isoformat()
    source = subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip()
    raw = (ROOT/'CLAIMS.yaml').read_bytes()
    ledger = yaml.safe_load(raw)
    registrations = [B+'twelfth_preparation_registration/summary.json',
                     B+'prism_all_columns_registration/summary.json', B+'prism_linear_witness_registration/summary.json']
    ids = [cid for p in registrations for cid in read(p)['new_claim_ids']]
    claims = [c for c in ledger['claims'] if c['id'] in ids]
    assert len(ids) == len(claims) == 4
    assert all(c['status'] == 'VERIFIED' and c['review_state'] == 'CLEAR' for c in claims)
    artifacts = {a['id']: a for a in ledger['artifacts']}
    runs = []
    for name, code, outcome in [('variable_core_factor', 0, 'UNKNOWN_CONFLICT_LIMIT'),
                                 ('prism_all_columns', 124, 'UNKNOWN_TIMEOUT')]:
        path = B+name+'_native_pilot/summary.json'
        r = read(path)
        assert r['actual_exit_code'] == code and r['research_calls'] == 1
        lines = [s for s in (ROOT/r['receipt']['stdout']).read_text().splitlines() if s.startswith('c conflicts:')]
        runs.append(dict(name=name, result=outcome, native_exit_code=code, attempts=1,
            summary=path, summary_sha256=h(path), wrapper_wall_seconds=r['receipt']['wall_seconds'],
            configured_conflicts=1000000, configured_seconds=300,
            observed_conflicts=int(lines[0].split()[2]) if len(lines) == 1 else None,
            observed_conflicts_null_reason=None if len(lines) == 1 else 'No unique final conflict statistic saved.',
            incomplete_trace_bytes=r['proof_copy']['bytes'], incomplete_trace_sha256=r['proof_copy']['sha256']))
    command = ['wsl.exe','-d','Ubuntu-24.04','--','ps','-C','cadical','-o','pid,etime,pcpu,rss,args']
    observed = datetime.now(timezone.utc).isoformat()
    process = subprocess.run(command, cwd=ROOT, capture_output=True)
    for suffix, content in [('stdout', process.stdout), ('stderr', process.stderr)]:
        with (ROOT/(B+'resume/twelfth_process_snapshot.'+suffix+'.log')).open('xb') as f:
            f.write(content)
    state = 'CADICAL_PROCESS_OBSERVED' if process.returncode == 0 else 'NO_CADICAL_PROCESS_OBSERVED' if process.returncode == 1 else 'UNKNOWN_OBSERVATION_ERROR'
    snapshot = B+'resume/claims_at_twelfth_milestone.yaml'
    with (ROOT/snapshot).open('xb') as f:
        f.write(raw)
    paths = {artifacts[a]['path'] for c in claims for a in c['evidence']}
    paths.update([*registrations, snapshot, B+'twelfth_artifact_packaging/catalog.json'])
    paths.update(r['summary'] for r in runs)
    record = dict(timestamp=now, source_commit=source, command=[sys.executable, *sys.argv], cwd=str(ROOT),
        previous_report='docs/RESEARCH_20260930_ELEVENTH_WAVE.md', previous_checkpoint_sha256=h(B+'resume/eleventh_milestone_checkpoint.json'),
        target_resolution='UNKNOWN', external_review=None, external_review_reason='No validated target graph or general nonexistence proof in this repository.',
        claim_population=len(ledger['claims']), verified_clear=sum(c['status'] == 'VERIFIED' and c['review_state'] == 'CLEAR' for c in ledger['claims']),
        claim_status_counts=dict(Counter(c['status'] for c in ledger['claims'])),
        claim_review_counts=dict(Counter(c['review_state'] for c in ledger['claims'])), new_verified_ids=ids,
        completed_native_attempts=2, native_runs=runs, native_SAT_results=0, native_UNSAT_results=0,
        native_UNKNOWN_results=2, independently_validated_new_factors=0, complete99_graphs=0,
        new_complete_unsat_traces=0, newly_closed_unrestricted_branches=0,
        column_model_population=dict(canonical_columns=60, choices_per_column=96, distinct_choices=5760,
            exact_equations=540, primary_equation_incidence_entries=80640),
        linear_relaxation_witnesses=dict(rational=1, modulo2=1, modulo3=1, independent_equations_per_witness=540,
            same_binary_solution_implied=False, rank_claim=None, rank_claim_null_reason='Producer modular-rank telemetry is not promoted.'),
        coverage='Overall search coverage: UNKNOWN; no validated denominator.',
        execution=dict(observed_at=observed, command=command, exit_code=process.returncode, state=state,
            stdout_sha256=h(B+'resume/twelfth_process_snapshot.stdout.log'), stderr_sha256=h(B+'resume/twelfth_process_snapshot.stderr.log'),
            scope='The two named attempts have completed; any observed process belongs to a later experiment.'),
        next_experiment='Independently audit and test coordinate relabelling reductions: first-column choice for the six-prism model and eleven M1 orbit representatives for the arbitrary-core model.',
        evidence_sha256={p:h(p) for p in sorted(paths)})
    with (ROOT/(B+'resume/twelfth_milestone_checkpoint.json')).open('x', encoding='utf-8', newline='\n') as f:
        json.dump(record, f, indent=2)
        f.write('\n')
    claimrows = '\n'.join('| `'+c['id']+'` | '+c['scope']['description']+' [Audit](../'+artifacts[c['evidence'][0]]['path']+'). |' for c in claims)
    runrows = '\n'.join('| '+r['name']+' | '+r['result']+' | '+str(r['observed_conflicts'])+' | '+f"{r['wrapper_wall_seconds']:.3f}"+' |' for r in runs)
    text = f'''# Twelfth resumed milestone, 2026-09-30 JST

Four independently verified claims were added since the [eleventh milestone](RESEARCH_20260930_ELEVENTH_WAVE.md). The triangle-factor normalization and its necessary CNF now cover arbitrary target cores. A separate six-prism encoding covers every column pattern for that fixed core. Exact rational and modular witnesses show why three linear relaxations cannot exclude that model. Both native pilots ended UNKNOWN.

**As of:** {now}; source commit `{source}`. [Checkpoint](../{B}resume/twelfth_milestone_checkpoint.json), [ledger snapshot](../{snapshot}); previous report: eleventh milestone.

**Verdict:** target resolution UNKNOWN. This repository has no independently validated target graph or general nonexistence proof. No target resolution is under external review. [Draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3) remains unmerged. This is not a worldwide literature verdict.

**Verified changes:** all four claims are revision 1.

| Claim | Scope and evidence |
| --- | --- |
{claimrows}

**Work completed:** the universal derivation starts with any edge and its unique triangle. Relabelling makes M0 standard and two cross matchings identity, while M1, M2 and P remain arbitrary. The 60 C0 columns are bijectively the nonmatching coordinate pairs. No prism-free, commuting-matching, symmetric-P or automorphism restriction is introduced. The 110,904-variable, 518,160-clause model encodes all Gram equations, margins, mixed bounds and column-pair bounds. Independent checking reconstructed every clause and calibrated the raw-object path. A SAT factor would still omit the residual 60-vertex graph.

The separate fixed six-prism model retains all 96 possible column supports for each of 60 canonical columns: 5,760 distinct choices. The independent reviewer enumerated all 46,656 component-label states to establish the complete domain, checked all 540 exact equations and every one of 874,800 clauses. Its 245,880-variable formula encodes abstract Gram factors; outside-column bounds and residual D are absent. This removes the earlier five-matching and complement-pairing restrictions only within the specified core.

| Native attempt | Result | Saved conflicts | Wrapper seconds |
| --- | --- | --- | --- |
{runrows}

Each model had one attempt with a 300-second limit and 1,000,000 configured conflicts, with additional memory/file guards. These are single-run measurements in different models, not a speed comparison. Neither produced a factor or complete proof. Independent run audits authenticate inputs, actual outcomes and complete hashes of the retained incomplete traces; hashing an incomplete trace is not proof checking.

The 540 primary linear equations admit the exact rational vector with every coordinate 1/96 in [0,1]. Two separate saved residue vectors satisfy their reductions modulo 2 and modulo 3. Direct independent evaluation checked every equation and rejected fourteen altered witnesses. These three witnesses belong to different domains and are not combined into a binary solution. Modular rank reported by the producer remains unpromoted telemetry.

**Coverage:** Overall search coverage: UNKNOWN; no validated denominator. Universal encoding coverage means every target supplies a model; it is not a completed exhaustive search. No unrestricted branch or complete fixed-core family was excluded. Ledger population: {len(ledger['claims'])} claims, {record['verified_clear']} VERIFIED/CLEAR and 2 CANDIDATE/CLEAR.

**Best result:** independently verified universal necessary encoding and complete coverage of the fixed six-prism column domain. No validated full factor, new graph candidate or target-wide bound was obtained.

**Problems:** both native outcomes are UNKNOWN. The linear rational/modular relaxations are feasible and therefore cannot alone prove the integer model impossible. The initial variable-core checker expected an obsolete metadata key and stopped; its original failure and corrected checker are preserved. The independent all-column audit explicitly binds the transitive validator import omitted by the producer manifest. Large raw CNF/model files have authenticated gzip recovery, while incomplete native traces remain LOCAL_ONLY.

**Execution:** both named native attempts are complete. Fresh observation at {observed}: `{state}`. Exact command and logs are in the checkpoint; an observed later process does not reopen either completed attempt. The user's continuation instruction remains active.

**Next experiment:** independently establish and test two coordinate relabelling reductions: one first-column choice for the six-prism formula, and eleven first-matching orbit representatives for the arbitrary-core formula. These must preserve all target coverage without assuming a target automorphism.

**References:** [source commit](https://github.com/ikuto32/conway-99-graph/commit/{source}), [draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3), [catalog](../{B}twelfth_artifact_packaging/catalog.json), [replay guide](REPRODUCING_20260930_TWELFTH_WAVE.md). Public evidence pointers are bound after immutable remote publication is confirmed.
'''
    with (ROOT/'docs/RESEARCH_20260930_TWELFTH_WAVE.md').open('x', encoding='utf-8', newline='\n') as f:
        f.write(text)
    print(json.dumps(dict(claims=len(ledger['claims']), verified_clear=record['verified_clear'], native_state=state, target_resolution='UNKNOWN')))


if __name__ == '__main__':
    main()
