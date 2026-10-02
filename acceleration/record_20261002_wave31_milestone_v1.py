"""Generate a dated milestone from the exact ledger and saved registration report.

Metadata only. This does not replay proofs or observe live scientific processes.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import yaml

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    ledger_bytes = (ROOT/'CLAIMS.yaml').read_bytes()
    ledger = yaml.safe_load(ledger_bytes)
    registration_path = 'acceleration/results/20261002_wave31_registration02/summary.json'
    registration_bytes = (ROOT/registration_path).read_bytes()
    report = json.loads(registration_bytes)
    if hashlib.sha256(ledger_bytes).hexdigest() != report['ledger_sha256']:
        raise ValueError('Exact registered milestone ledger required')
    counts = dict(Counter(c['status'] for c in ledger['claims']))
    if counts != report['status_counts'] or len(ledger['claims']) != report['claim_records']:
        raise ValueError('Generated counts disagree with saved registration')
    selected = {c['id']: c for c in ledger['claims'] if c['id'] in report['new_claim_ids']}
    if len(selected) != 4 or any(c['status'] != 'VERIFIED' or c['review_state'] != 'CLEAR' for c in selected.values()):
        raise ValueError('Exact four scoped additions required')
    timestamp = datetime.now(timezone.utc).isoformat()
    checkpoint = dict(timestamp=timestamp, source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        command_argv=[str(Path(__file__).resolve()), '--out', str(args.out)],
        registry_sha256=report['ledger_sha256'], registration_path=registration_path,
        registration_sha256=hashlib.sha256(registration_bytes).hexdigest(),
        claim_records=len(ledger['claims']), status_counts=counts,
        verified_changes=[dict(id=c['id'],revision=c['revision'],scope=c['scope'],evidence=c['evidence']) for c in selected.values()],
        target_resolution=ledger['target']['status'], external_review=ledger['target']['external_review'],
        literal_population=report['literal_population'], literal_exclusions=report['distinct_literal_exclusions'],
        unresolved_literal_cases=report['unresolved_literal_cases'],
        overall_search_coverage='UNKNOWN; no validated denominator.',
        execution_state='UNKNOWN; this metadata generator does not observe live processes.',
        artifact_availability='LOCAL_ONLY pending separate immutable publication and full checking-closure recovery.',
        skipped_checks=['This generator performs no mathematical replay; full historical transitive hashes are not rechecked.'])
    (out/'checkpoint.json').write_text(json.dumps(checkpoint,indent=2)+'\n',encoding='utf8',newline='\n')
    (out/'CLAIMS.yaml').write_bytes(ledger_bytes)
    rows=[]
    descriptions = {
        report['new_claim_ids'][0]: ('64 literal fixed-support Gram instances; complete proof replay; no whole-support conclusion.', 'batch05_proofs01'),
        report['new_claim_ids'][1]: ('All 2,414 stored coefficient matrices and 272,054 nonzero upper entries; class catalogue completeness unproved.', None),
        report['new_claim_ids'][2]: ('One integer vector satisfies all 4,543 selected equations and two exact rank-one PSD blocks; no graph construction.', 'order8_null01'),
        report['new_claim_ids'][3]: ('Pinned driver tiny positive/corrupted controls and observed local descendant cleanup; finite engineering scope.', 'policy_driver_calibration02')}
    for cid,c in selected.items():
        description,audit=descriptions[cid]
        evidence = '../acceleration/results/20261002_independent_review/'+audit+'/summary.json' if audit else '../acceleration/results/20261002_wave147_all_coefficients/summary.json'
        rows.append(f'| {cid} r{c["revision"]} | {description} [Audit]({evidence}). |')
    text=f'''# Thirty-first research milestone, 2026-10-02

Four scoped claims are newly VERIFIED/CLEAR since the [October 1 stop checkpoint](STOP_20261001_EIGHT_COORDINATE.md). Batch05 adds 64 distinct literal exclusions with complete independently replayed proofs. The structural witness and coefficient audit add no exclusions.

**As of:** {timestamp}; source commit `{checkpoint['source_commit']}`; [checkpoint](../{out.relative_to(ROOT).as_posix()}/checkpoint.json); [frozen ledger](../{out.relative_to(ROOT).as_posix()}/CLAIMS.yaml); [previous report](STOP_20261001_EIGHT_COORDINATE.md).

**Verdict:** target resolution UNKNOWN. The repository has no independently validated target graph or general nonexistence proof. No target-resolution artifact has been submitted for external review. This dated repository verdict does not describe the entire world's literature. PR3 remains draft.

**Verified changes:** all four additions are revision 1; the preceding 308 claim records retain their statements and verification records.

| Claim | Exact checked scope |
| --- | --- |
{chr(10).join(rows)}

**Work completed:** batch05 reused 64 previously built and encoding-checked formulas; 64 native attempts completed with raw UNSAT outcomes and all 64 complete traces passed the independent checker. There were zero SAT, UNKNOWN or errored evaluations in this batch. Its complete proofs contain {report['new_complete_proof_bytes']:,} bytes. The independently checked encoding and proof paths are separate; public recovery of the entire raw checking closure has not yet been established.

The saved-report identity and disjoint-union calculation gives {report['distinct_literal_exclusions']} distinct checked literal cases among the frozen {report['literal_population']} fixed-support campaign representatives, with {report['unresolved_literal_cases']} unresolved. These pipeline populations overlap and are not summed. No labelled-image expansion is applied to the new cases. [Registration and union record](../{registration_path}).

**Coverage:** {len(ledger['claims'])} current claim records: {counts['VERIFIED']} VERIFIED/CLEAR, {counts['CANDIDATE']} CANDIDATE/CLEAR and {counts['REFUTED']} REFUTED/CLEAR. Overall search coverage: UNKNOWN; no validated denominator. The 380/792 fraction measures literal campaign case count only, not graphs, difficulty or remaining runtime.

**Best result:** the prior fixed-support lower bound of eight unbalanced groups is unchanged. The exact order-eight aggregate witness has N3 count 4158 and rank-one PSD contractions of dimensions 66 and 87; it shows this selected relaxation still admits that endpoint. It is not an adjacency matrix or an existence certificate.

**Problems:** public replay of new raw formula/proof closures remains unestablished. The complete stored-coefficient check does not enumerate the class universe afresh. Structural root-flag rigidity work remains CANDIDATE pending its separate audit and is outside this cutoff. The first proof-calibration control was vetoed because its expected-invalid prefix was actually valid; original source and failed report are retained, and the new checker version passed genuine corrupted controls. The first registration used a wrong expected status string and stopped before modifying the ledger; the failed version and record are preserved. Several producer/setup failures are recorded rather than erased.

**Execution:** the batch05 solver and full proof replay completed with observed empty contained process groups. This generator makes no current live-process claim; execution state outside those dated receipts is UNKNOWN. This milestone does not stop the user-authorized research.

**Next experiment:** independently calibrate a new DRAT-state parser, extract a candidate restart state from the preserved unrestricted 300-second partial trace, and run a separately allocated proof-producing continuation if independent artifact checks approve the transform. Any exclusion must pass a complete concatenated proof against the original unrestricted CNF; a restarted assignment must independently satisfy the original formula and full graph validator.

**References:** [source commit](https://github.com/ikuto32/conway-99-graph/commit/{checkpoint['source_commit']}), [draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3), [policy-aware resume](RESUME_20261002_POLICY_AWARE.md), [structural derivation](DERIVATION_20261002_ORDER8_MARKED_ENDPOINT.md), [dated literature search](LITERATURE_20261002_STRUCTURAL_REFRESH.md). Raw availability labels remain separate from successful historical checks.
'''
    destination=ROOT/'docs/RESEARCH_20261002_THIRTYFIRST_WAVE.md'
    with destination.open('x',encoding='utf8',newline='\n') as stream:
        stream.write(text)
    print(json.dumps(dict(status='MILESTONE_METADATA_GENERATED',checkpoint=str(out/'checkpoint.json'),claims=len(ledger['claims']),target_resolution=ledger['target']['status'])))


if __name__=='__main__':
    main()
