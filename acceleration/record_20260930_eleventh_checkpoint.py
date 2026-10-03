"""Freeze the eight independently reviewed eleventh-wave claims and run states."""
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
    source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    raw = (ROOT/'CLAIMS.yaml').read_bytes()
    ledger = yaml.safe_load(raw)
    registrations = [B+'eleventh_preparation_registration/summary.json', B+'eleventh_factor_registration/summary.json']
    ids = [cid for p in registrations for cid in read(p)['new_claim_ids']]
    claims = [c for c in ledger['claims'] if c['id'] in ids]
    assert len(ids) == len(claims) == 8
    assert all(c['status'] == 'VERIFIED' and c['review_state'] == 'CLEAR' for c in claims)
    artifacts = {a['id']: a for a in ledger['artifacts']}
    treepath = B+'independent_review/one_c2_extension_rows/summary.json'
    row = read(treepath)
    assert row['verified_UNSAT_rows'] == 11 and row['complete_tree_nodes'] == 1037
    native_specs = [
        ('fixed25', 'triangle_one_c2_row_native_pilot', 10, 'SAT'),
        ('prism_complement_design', 'prism_factor_design_pilot', 20, 'UNSAT_REPLAYED_SCOPED'),
        ('prism_unpaired_design', 'prism_unpaired_design_pilot', 124, 'UNKNOWN_TIMEOUT'),
        ('fixed36_column_caps', 'triangle_column_cap_factor_native_pilot', 0, 'UNKNOWN_CONFLICT_LIMIT'),
    ]
    runs = []
    for name, folder, code, outcome in native_specs:
        p = B+folder+'/summary.json'
        record = read(p)
        receipt = record['receipt']
        assert receipt['actual_exit_code'] == code and record['research_calls'] == 1
        lines = [s for s in (ROOT/receipt['stdout']).read_text().splitlines() if s.startswith('c conflicts:')]
        runs.append(dict(name=name, summary=p, summary_sha256=h(p), actual_exit_code=code,
            result=outcome, attempts=1, wrapper_wall_seconds=receipt['wall_seconds'],
            conflicts=int(lines[0].split()[2]) if len(lines) == 1 else None,
            conflicts_unavailable_reason=None if len(lines) == 1 else 'No unique completed statistics line in saved output.'))
    command = ['wsl.exe', '-d', 'Ubuntu-24.04', '--', 'ps', '-C', 'cadical', '-o', 'pid,etime,pcpu,rss,args']
    observed = datetime.now(timezone.utc).isoformat()
    process = subprocess.run(command, cwd=ROOT, capture_output=True)
    for suffix, content in [('stdout', process.stdout), ('stderr', process.stderr)]:
        with (ROOT/(B+'resume/eleventh_process_snapshot.'+suffix+'.log')).open('xb') as f:
            f.write(content)
    state = 'CADICAL_PROCESS_OBSERVED' if process.returncode == 0 else 'NO_CADICAL_PROCESS_OBSERVED' if process.returncode == 1 else 'UNKNOWN_OBSERVATION_ERROR'
    snapshot = B+'resume/claims_at_eleventh_milestone.yaml'
    with (ROOT/snapshot).open('xb') as f:
        f.write(raw)
    paths = {artifacts[aid]['path'] for c in claims for aid in c['evidence']}
    paths.update([*registrations, snapshot, treepath, B+'eleventh_artifact_packaging/catalog.json'])
    paths.update(r['summary'] for r in runs)
    record = dict(timestamp=now, source_commit=source, command=[sys.executable, *sys.argv], cwd=str(ROOT),
        previous_report='docs/RESEARCH_20260930_TENTH_WAVE.md', previous_checkpoint_sha256=h(B+'resume/tenth_milestone_checkpoint.json'),
        target_resolution='UNKNOWN', external_review=None,
        external_review_reason='No validated target graph or general nonexistence proof in this repository.',
        claim_population=len(ledger['claims']),
        verified_clear=sum(c['status'] == 'VERIFIED' and c['review_state'] == 'CLEAR' for c in ledger['claims']),
        claim_status_counts=dict(Counter(c['status'] for c in ledger['claims'])),
        claim_review_counts=dict(Counter(c['review_state'] for c in ledger['claims'])),
        new_verified_ids=ids, completed_native_attempts=len(runs), native_runs=runs,
        independently_validated_partial_factors=1, partial_factor_shape=[25, 60], complete36_factors=0, complete99_graphs=0,
        complete_unsat_traces_independently_replayed=1,
        row_exclusion=dict(distinct_fixed_configurations=1, row_domains=11, complete_tree_nodes=row['complete_tree_nodes'],
            independently_rejected_fresh_corruptions=len(row['fresh_corruptions_rejected'])),
        newly_closed_unrestricted_branches=0, coverage='Overall search coverage: UNKNOWN; no validated denominator.',
        execution=dict(observed_at=observed, command=command, exit_code=process.returncode, state=state,
            stdout_sha256=h(B+'resume/eleventh_process_snapshot.stdout.log'),
            stderr_sha256=h(B+'resume/eleventh_process_snapshot.stderr.log'),
            scope='All four named native attempts are complete; any newly observed process belongs to subsequent work.'),
        next_experiment='Build and independently audit the arbitrary-core factor model with all matching/permutation choices free and mixed/column caps, then run a bounded native pilot.',
        evidence_sha256={p: h(p) for p in sorted(paths)})
    with (ROOT/(B+'resume/eleventh_milestone_checkpoint.json')).open('x', encoding='utf-8', newline='\n') as f:
        json.dump(record, f, indent=2)
        f.write('\n')
    rows = '\n'.join('| `'+c['id']+'` | '+c['scope']['description']+' [Audit](../'+artifacts[c['evidence'][0]]['path']+'). |' for c in claims)
    runrows = '\n'.join('| '+r['name']+' | '+r['result']+' | '+str(r['conflicts'])+' | '+f"{r['wrapper_wall_seconds']:.3f}"+' |' for r in runs)
    text = f'''# Eleventh resumed milestone, 2026-09-30 JST

Eight independently verified claims were added since the [tenth milestone](RESEARCH_20260930_TENTH_WAVE.md). One native solve produced a valid 25x60 partial factor; eleven exact row proofs excluded that fixed candidate. Separate exact arguments exclude two restricted six-prism construction families. A strengthened full-factor search ended UNKNOWN.

**As of:** {now}; source commit `{source}`. [Checkpoint](../{B}resume/eleventh_milestone_checkpoint.json), [ledger snapshot](../{snapshot}); previous report: tenth milestone.

**Verdict:** target resolution UNKNOWN. This repository has neither an independently validated target graph nor a general nonexistence proof. No target candidate is under external review. [Draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3) remains unmerged. This is not a worldwide literature verdict.

**Verified changes:** all eight claims are revision 1.

| Claim | Exact scope and evidence |
| --- | --- |
{rows}

**Work completed:** one 74,814-variable, 256,151-clause projection returned SAT. Independent checking authenticated the full assignment, every clause, all 625 Gram entries, margins, component capacities and 1,770 column-pair bounds. This yielded one verified 25x60 partial factor. Each of its eleven missing row domains then had a complete contradiction tree; the independent checker covered all 1,037 nodes. These are eleven proofs excluding the same fixed Q1 plus selected C2 row. They do not exclude that Q1 with a different selected row. A smaller equivalent 22,379-variable, 81,366-clause encoding was checked using a restriction of the same assignment; it was not a second SAT discovery or a performance test.

For the six-prism core, one prescribed five-matching, globally complement-paired design returned UNSAT with a complete independently replayed DRAT proof. A separate parity argument excludes global complement pairing for any cell-pattern choices in this core. The broader all-bits-free five-matching design timed out, but an independently derived exact-rank/parity proof later excluded that specific design: eighteen 15x10 integer matrices have rank nine with full-support signed kernels. The UNKNOWN solver trace is not a premise of that proof. The three exclusion statements overlap; their populations are not added.

The full36 model retains both unknown incidence blocks and adds all necessary column-pair caps. Its complete encoding and object-checker gates passed before launch. The run ended at its conflict limit with no factor and no complete proof.

| Native attempt | Outcome | Saved conflict count | Wrapper seconds |
| --- | --- | --- | --- |
{runrows}

These are four attempts in four different models, with different limits recorded in their manifests. Times include each wrapper's recorded boundary and are not a performance comparison. Exactly one native UNSAT trace was independently replayed. The other three traces are SAT-run or incomplete UNKNOWN traces and provide no nonexistence certificate.

**Coverage:** Overall search coverage: UNKNOWN; no validated denominator. No unrestricted branch or complete fixed-core family was excluded. The new ledger population is {len(ledger['claims'])} claims: {record['verified_clear']} VERIFIED/CLEAR and 2 CANDIDATE/CLEAR. Generated, checked and excluded partial objects are overlapping pipeline stages, not separate target coverage.

**Best result:** an exact 25-row partial factor with a complete explanation of its extension failure, plus exact obstructions to two proposed prism construction families. There is no target-wide bound or validated 36-row factor.

**Problems:** capacities and pair caps on a partial factor are insufficient for completion. The strengthened full-factor solve is UNKNOWN. Arbitrary cell-pattern choices remain outside the five-matching design exclusion; none of these constructions is assumed to cover every target. Large incomplete/SAT-run traces remain LOCAL_ONLY. The large clause recipe is recoverable from its public gzip package; availability is recorded separately from mathematical verification.

**Execution:** all four native attempts and all eleven row searches are complete. A fresh observation at {observed} returned `{state}`. Exact process output is pinned in the checkpoint. The user's continuation instruction remains active.

**Next experiment:** allow arbitrary M1, M2 and P in the triangle core, with canonical C0, exact Gram equations, mixed bounds and column-pair caps. Independently establish unrestricted normalization, encoding equivalence and object-checker gates before a new native pilot. A factor would still leave the 60-vertex residual graph unresolved.

**References:** [source commit](https://github.com/ikuto32/conway-99-graph/commit/{source}), [draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3), [catalog](../{B}eleventh_artifact_packaging/catalog.json), [replay guide](REPRODUCING_20260930_ELEVENTH_WAVE.md). Immutable public evidence pointers are recorded after publication confirmation.
'''
    with (ROOT/'docs/RESEARCH_20260930_ELEVENTH_WAVE.md').open('x', encoding='utf-8', newline='\n') as f:
        f.write(text)
    print(json.dumps(dict(claims=len(ledger['claims']), verified_clear=record['verified_clear'], native_state=state, target_resolution='UNKNOWN')))


if __name__ == '__main__':
    main()
