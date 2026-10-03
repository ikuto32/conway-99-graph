"""Freeze a ledger-derived report of completed fixed-family proofs and local checks."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
B = 'acceleration/results/20260930_'
OUT = ROOT/(B+'resume')

def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

def read(path):
    return json.loads((ROOT/path).read_bytes())

def save(path, obj):
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(obj, stream, indent=2)
        stream.write('\n')

def main():
    now = datetime.now(timezone.utc).isoformat()
    source = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    raw = (ROOT/'CLAIMS.yaml').read_bytes()
    ledger = yaml.safe_load(raw)
    registration = read(B+'seventh_registration/summary.json')
    ids = registration['new_claim_ids']
    claims = [c for c in ledger['claims'] if c['id'] in ids]
    assert len(claims) == 10 and all(c['status'] == 'VERIFIED' and c['review_state'] == 'CLEAR' for c in claims)
    assert ledger['target']['status'] == 'UNKNOWN'
    snapshot = OUT/'claims_at_seventh_milestone.yaml'
    with snapshot.open('xb') as handle:
        handle.write(raw)
    command = ['wsl.exe', '-d', 'Ubuntu-24.04', '--', 'ps', '-C', 'cadical', '-o', 'pid,etime,pcpu,rss,args']
    observed_at = datetime.now(timezone.utc).isoformat()
    process = subprocess.run(command, cwd=ROOT, capture_output=True)
    assert process.returncode == 1, 'Do not claim no live solver without the expected fresh observation'
    for suffix, content in [('stdout', process.stdout), ('stderr', process.stderr)]:
        (OUT/('seventh_native_process_snapshot.'+suffix+'.log')).write_bytes(content)
    runs = []
    for label, folder, audit in [
        ('Wave154', 'triangle_native_pilot', 'triangle_wave154_unsat'),
        ('Wave151', 'wave151_triangle_native_pilot', 'triangle_wave151_unsat'),
    ]:
        summary = read(B+folder+'/summary.json')
        gate_path = B+'independent_review/'+audit+'/summary.json'
        gate = read(gate_path)
        assert summary['actual_exit_code'] == gate['solver_actual_exit_code'] == 20
        assert gate['status'].endswith('_UNSAT_PASS')
        proof = ROOT/(B+folder+'/main/proof.drat')
        assert digest(proof) == gate['proof_sha256'] and proof.stat().st_size == gate['proof_bytes']
        runs.append(dict(fixed_configuration=label, result='INDEPENDENTLY_CHECKED_FIXED_FAMILY_UNSAT',
            native_exit_code=20, variables=gate['variables'], clauses=gate['clauses'],
            proof_path=proof.relative_to(ROOT).as_posix(), proof_sha256=gate['proof_sha256'], proof_bytes=gate['proof_bytes'],
            audit=gate_path, audit_sha256=digest(ROOT/gate_path),
            run_summary=B+folder+'/summary.json', run_summary_sha256=digest(ROOT/(B+folder+'/summary.json')),
            unrestricted_target_resolution=False))
    joint = read(B+'independent_review/joint_two_star_domains/summary.json')
    transport = read(B+'independent_review/nogood36_anchor_transport/summary.json')
    artifacts = {a['id']: a for a in ledger['artifacts']}
    paths = {artifacts[aid]['path'] for c in claims for aid in c['evidence']}
    paths.update([B+'seventh_registration/summary.json', B+'seventh_artifact_packaging/catalog.json',
                  snapshot.relative_to(ROOT).as_posix()])
    for row in runs:
        paths.update([row['audit'], row['proof_path'], row['run_summary']])
    record = dict(timestamp=now, source_commit=source, command=[sys.executable, *sys.argv], cwd=str(ROOT),
        previous_report='docs/RESEARCH_20260930_SIXTH_WAVE.md',
        previous_checkpoint_sha256=digest(OUT/'sixth_milestone_checkpoint.json'),
        target_resolution='UNKNOWN', external_review=None,
        external_review_reason='No internally validated target graph or unrestricted nonexistence proof in this repository.',
        claim_population=len(ledger['claims']), claim_status_counts=dict(Counter(c['status'] for c in ledger['claims'])),
        claim_review_counts=dict(Counter(c['review_state'] for c in ledger['claims'])),
        verified_clear=sum(c['status'] == 'VERIFIED' and c['review_state'] == 'CLEAR' for c in ledger['claims']),
        new_verified_ids=ids, native_wave=dict(selected_fixed_configurations=2, attempted_evaluations=2,
            completed_evaluations=2, independently_checked_fixed_instance_unsat=2, sat_candidates=0,
            timeouts=0, errors=0, unrestricted_branches_closed=0, results=runs),
        joint_local_counts=joint['counts'], local_stages=joint['stages'],
        clause_transport_counts=transport['checks'],
        coverage='Overall search coverage: UNKNOWN; no validated denominator.',
        execution=dict(solver_state='NO_CADICAL_PROCESS_OBSERVED', observed_at=observed_at,
            command=command, exit_code=process.returncode,
            stdout_sha256=digest(OUT/'seventh_native_process_snapshot.stdout.log'),
            stderr_sha256=digest(OUT/'seventh_native_process_snapshot.stderr.log'),
            subsequent_work='Separate candidate matching-pair census and direct row-obstruction analysis are not included in verified milestone totals.'),
        next_experiment='Derive and independently check a direct row-domain obstruction for the fixed Wave154 factor; independently check the new matching-pair orbit census before any broader core classification.',
        evidence_sha256={p: digest(ROOT/p) for p in sorted(paths)})
    save(OUT/'seventh_milestone_checkpoint.json', record)
    rows = '\n'.join('| `'+c['id']+'` | '+c['scope']['description']+' [Audit](../'+artifacts[c['evidence'][0]]['path']+'). |' for c in claims)
    text = f'''# Seventh resumed milestone, 2026-09-30 JST

Ten verified records were added since the [sixth milestone](RESEARCH_20260930_SIXTH_WAVE.md). Complete independently replayed proofs exclude the two exact archived Wave151 and Wave154 triangle/Q1 configurations. The new local clauses and local-consistency results retain their narrower recorded scopes.

**As of:** {now}; source commit `{source}`. [Checkpoint](../{B}resume/seventh_milestone_checkpoint.json), [ledger snapshot](../{B}resume/claims_at_seventh_milestone.yaml), previous report: sixth milestone.

**Verdict:** target resolution UNKNOWN. No independently validated target graph or unrestricted nonexistence proof is available in this repository; no candidate target resolution is under external review. Draft [PR3](https://github.com/ikuto32/conway-99-graph/pull/3) remains unmerged. This is not a claim about the current worldwide literature.

**Verified changes:** all ten new records are revision 1.

| Claim | Exact scope and evidence |
| --- | --- |
{rows}

**Work completed:** two selected fixed configurations, two attempted and completed native evaluations, two independently checked complete UNSAT proofs, zero SAT candidates and zero timeouts/errors. These are not two unrestricted branches and their graph populations have not been counted or proved disjoint. The exact CNFs have 429,476 variables / 1,486,729 clauses (Wave154) and 429,779 variables / 1,487,778 clauses (Wave151). Both complete ASCII DRAT traces, native receipts and independent checker controls are retained.

The separate local pipeline has 32 sampled two-star witnesses, all independently checked. Four of these witnesses each have 61 individually enumerated outside-vertex domains: 244 case/vertex domains, 297,024 candidate patterns and 64,436 surviving patterns. All individual domains are nonempty; their simultaneous compatibility remains UNKNOWN. These pipeline populations overlap and must not be added.

One positive-edge configuration yields a verified 36-literal nogood. Its finite raw domain has 460 patterns, each independently rejected by a necessary pair cap. All 192 specified anchor-fixing relabelings were checked and yield 192 distinct clause images; this is not a census of target automorphisms. The single-star redundancy theorem is established by independent derivation; its 128 sampled controls are not the universal proof.

**Coverage:** Overall search coverage: UNKNOWN; no validated denominator. No nontrivial target automorphism is assumed. No unrestricted canonical branch is closed. Ledger population: {len(ledger['claims'])} records, {record['verified_clear']} VERIFIED/CLEAR and 2 CANDIDATE/CLEAR.

**Best result:** complete replayable fixed-family exclusion proofs, together with valid clauses for the exact unrestricted encoding. No comparable new numerical bound or full target witness was produced. The earlier unrestricted SAT equivalence remains unresolved.

**Problems:** the node-capped coupled-domain search remains UNKNOWN. Initial single-star audit label ordering, clause-newline comparison, transport syntax and producer control failures are preserved with their corrections; none is a target refutation. The modular preflight observations are not promoted. Native/checker binaries remain LOCAL_ONLY with public build provenance. New matching-pair census and extracted row-core analyses remain separate candidates outside these totals.

**Execution:** both native runs ended. A fresh observation at {observed_at} found no CaDiCaL process; this saved observation is not a live status promise. New structural work continues under the user's resume instruction, and no external blocker is recorded.

**Next experiment:** check a direct finite row-domain obstruction suggested by the Wave154 proof core, then use the independently audited matching-pair census to guide broader triangle-core work. Neither step assumes a target automorphism.

**References:** [source commit](https://github.com/ikuto32/conway-99-graph/commit/{source}), [draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3), [artifact catalog](../{B}seventh_artifact_packaging/catalog.json), [reproduction guide](REPRODUCING_20260930_SEVENTH_WAVE.md). PUBLIC availability is recorded only after exact immutable publication is confirmed.
'''
    with (ROOT/'docs/RESEARCH_20260930_SEVENTH_WAVE.md').open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(text)
    print(json.dumps({'timestamp': now, 'claims': len(ledger['claims']), 'verified_clear': record['verified_clear'], 'fixed_proofs': 2, 'target_resolution': 'UNKNOWN'}))

if __name__ == '__main__':
    main()
