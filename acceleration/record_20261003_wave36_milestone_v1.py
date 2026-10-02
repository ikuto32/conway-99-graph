"""Record the three exact wave36 revisions from the ledger and raw checking records.

Bookkeeping only: no mathematical replay, live process observation or launch.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import validate_claims as registry

ROOT = Path(__file__).resolve().parents[1]
BASE = 'acceleration/results/20261003_wave36_registration02/CLAIMS.before.yaml'
EXPECTED = {
    'C-UNRESTRICTED-ROOTED7-MARKED-REROOT-MEAN-NECESSARY-ENCODING',
    'C-UNRESTRICTED-ROOTED7-PRIMARY-DOMAIN-RATIONAL-FEASIBILITY',
    'C-HYPERGRAPH-WEIGHT60-EXCLUSIVE-SWAP-V2-FINITE-ENGINEERING-CONTROLS',
}
REPORTS = {
    'model': ('acceleration/results/20261002_independent_review/rooted7_unrestricted_model01/summary.json', 'e7631851f9cc5716c9d8a1bf5b30f9a4644d8e2170f116d1bb30378fbeb16d70'),
    'lp': ('acceleration/results/20261003_independent_review/rooted7_unrestricted_lp01/summary.json', '069b8872cccaa08025f537b254db884294b7855743872f1d56ebf1435f96488c'),
    'controls': ('acceleration/results/20261002_independent_review/weight60_controls01/summary.json', '05a8c1e5b0d2df3d937cd1ab47961b17ff37ec2f3d9952a5db0feaf5178ac9f3'),
    'saved_calibration': ('acceleration/results/20261003_independent_review/weight60_saved_calibration03/summary.json', '660e4c420fa7f3f35f8c7291a4100931a7881237f0112c42428d6df9fa1baa07'),
    'publication': ('acceleration/results/20261003_independent_review/wave35_availability01/summary.json', '9abecafe6d14018cac5f70d5046ff11667defc387dab8c3a1709896fdf50bedd'),
}


def need(ok, reason):
    if not ok:
        raise ValueError(reason)


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ledger-sha256', required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    need(out.is_relative_to(ROOT), 'bounded checkpoint')
    raw = (ROOT / 'CLAIMS.yaml').read_bytes()
    need(hashlib.sha256(raw).hexdigest() == args.ledger_sha256, 'exact frozen ledger')
    current = registry.read_ledger(ROOT / 'CLAIMS.yaml')
    baseline = registry.read_ledger(ROOT / BASE)
    prior = {claim['id']: claim for claim in baseline['claims']}
    additions = [claim for claim in current['claims'] if claim['id'] not in prior]
    need(len(prior) == 334 and len(current['claims']) == 337 and {claim['id'] for claim in additions} == EXPECTED, 'exact three-revision population')
    need(all(next(claim for claim in current['claims'] if claim['id'] == cid) == old for cid, old in prior.items()), 'all334 prior material claims unchanged')
    need(all(claim['revision'] == 1 and claim['status'] == 'VERIFIED' and claim['review_state'] == 'CLEAR' and claim['scope']['target_resolution'] == 'NONE' for claim in additions), 'exact narrow independent revisions')
    statuses = dict(Counter(claim['status'] for claim in current['claims']))
    need(statuses == {'VERIFIED': 330, 'CANDIDATE': 3, 'REFUTED': 4}, 'counted states')
    reports = {}
    for label, (name, identity) in REPORTS.items():
        need(sha(ROOT / name) == identity, 'frozen report ' + label)
        reports[label] = json.loads((ROOT / name).read_bytes())
    lp = reports['lp']
    need(lp['complete_case_population'] == lp['complete_exact_primal_cases'] == 10 and lp['complete_exact_farkas_cases'] == 0 and lp['complete_saved_profile_vectors'] == 651 and lp['exclusions'] == 0, 'literal LP population')
    now = datetime.now(timezone.utc).isoformat()
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    checkpoint = dict(timestamp=now, source_commit=commit, source_sha256=sha(Path(__file__)), command=[sys.executable, *sys.argv], cwd=str(ROOT), ledger_sha256=args.ledger_sha256, previous_report='docs/RESEARCH_20261002_THIRTYFIFTH_WAVE.md', claim_records=337, status_counts=statuses, review_state_counts=dict(Counter(claim['review_state'] for claim in current['claims'])), new_claim_revisions=[dict(id=claim['id'], revision=claim['revision'], statement=claim['statement'], scope=claim['scope']) for claim in additions], inputs_sha256={name: identity for name, identity in REPORTS.values()}, target_resolution=current['target']['status'], new_exclusions=0, mathematical_replays=0, overall_search_coverage='UNKNOWN; no validated denominator.', execution_observation=None, execution_observation_reason='This checkpoint generator observes no processes and launches no science; completed engineering receipts and a prospective separately observed pilot are distinct.')
    out.mkdir(parents=True, exist_ok=False)
    (out / 'CLAIMS.yaml').write_bytes(raw)
    (out / 'checkpoint.json').write_text(json.dumps(checkpoint, indent=2) + '\n', encoding='utf8', newline='\n')
    rows = '\n'.join('| ' + claim['id'] + ' r1 | ' + claim['scope']['description'] + ' | [Independent audit](../' + claim['verification'][0]['command_or_audit'] + '). |' for claim in additions)
    text = f'''# Thirty-sixth research milestone, 2026-10-03

Since the [thirty-fifth milestone](RESEARCH_20261002_THIRTYFIFTH_WAVE.md), three exact revisions are newly VERIFIED/CLEAR. The unrestricted seven-vertex necessary count model and all651 rational profile witnesses passed independent checks. The changed construction engine passed complete finite controls. These results add no target graph, general nonexistence proof or exclusion.

**As of:** {now}; source commit `{commit}`; [checkpoint](../{out.relative_to(ROOT).as_posix()}/checkpoint.json); [frozen ledger](../{out.relative_to(ROOT).as_posix()}/CLAIMS.yaml). Previous report: wave35,334 material claims. The date in this title is Japan time; evidence retains its actual timezone.

**Verdict:** target resolution UNKNOWN. This repository has no independently validated target graph or general nonexistence proof and no candidate target resolution pending external review. Literature status remains separate from this repository state. [PR3](https://github.com/ikuto32/conway-99-graph/pull/3) remains draft.

**Verified changes:** all334 prior material claims and checking records are unchanged.

| Claim | Exact scope | Evidence |
| --- | --- | --- |
{rows}

**Work completed:** the new unrestricted operator retains all2770 local seven-vertex classes, including the20 classes removed by the earlier conditional model. Its2810 nonnegative variables,11769 affine equations and89350 term occurrences include variable secondary-edge/nonedge profiles and exact per-vertex prism/mean couplings. It imposes no target automorphism, common secondary profile or prism-free premise. The independent checker reconstructed every column and row and tested known-valid rook controls and243 partitions of the known-valid9-vertex control. This establishes necessity within the recorded scope, without a rank or graph realization claim.

The LP guide produced10 distinct completed evaluations: one global domain lift, one c>=1 lift and eight corners. All10 have independently checked exact nonnegative rational primals and zero Farkas certificates. All651 primary integer parameter triples have full rational count vectors; the separate checker tested7661619 scalar equations and1829310 coordinates. Exactly21 of these supplied vectors are integral, including prism-positive profiles. The other630 supplied vectors being nonintegral does not establish integer infeasibility or exclude an alternative vector. Count vectors have not been realized as graphs.

The weight60 exclusive-selected-point swap engine now permits triples sharing one point when the selected points are exclusive and the new pairs are absent after removal. The objective is `F60=60E_lambda+E_mu`. Its separate implementation checked57 calls:29 successful complete paths and28 designated malformed-input rejections,20992 proposals,328 saved intermediate states,2494 integer pair-cost records and five split/resume identities. All1303 valid overlapping proposals include592 accepted and711 rejected moves with complete rollback checks. A separately frozen40-control saved-object calibration passed before the scientific pilot. These are finite engineering checks; scientific sparse gaps cannot establish an earliest event over a full trajectory.

**Coverage:** the root ledger contains337 material claims:330 VERIFIED/CLEAR,3 CANDIDATE/CLEAR and4 REFUTED/CLEAR. These are scoped claims, not graph counts. The existing fixed-support union remains380 independently checked literal cases of792, with412 unresolved. Overall search coverage: UNKNOWN; no validated denominator.

**Best result:** among the two earlier audited native pilot objects compared in wave35, ordinary squared pair residual `E=3034` remains lower than the weight6 object's `E=3486`. Neither satisfies the integer SRG identity. The new weight60 engine has produced no scientific result at this checkpoint. Its imported graph starts at `F60=7203=60*63+3423`; this is a different objective from `F6`.

**Problems:** original failed disjoint-only weight60 controls, three diagnostic versions and source/checker corrections are retained. Registration01 rejected a schema field shape and atomically left the ledger unchanged; a new binding preserves the original evidence. Schema validation is not mathematical verification. No failed call, nonintegral rational witness or timeout is a nonexistence proof.

**Publication:** the independent [wave35 availability audit](../{REPORTS['publication'][0]}) confirmed198 additional artifact records PUBLIC and one GF3 checkpoint LOCAL_ONLY, while preserving all334 material claims. It authenticated335 immutable Git blobs and decoded five raw models from25 gzip parts. These are byte checks, not mathematical replay. New wave36 evidence remains LOCAL_ONLY pending immutable publication confirmation.

**Execution:** the model/LP/engineering calls and independent checks have completed containment receipts. This milestone generator makes no live process observation. The weight60 scientific pilot is prospective and requires published exact source/gates, a fresh root-WSL worker/resource preflight and its own observed process state. Authorized research remains active.

**Next experiment:** launch the predeclared single weight60 V2 invocation after those gates:100million maximum proposals,seed99032060,600-second outer deadline,550-second wrapper,450-second native guard and445-second cooperative stop, with exact saved checkpoints and a separate literal99-vertex validator. In parallel test normalized mod-2 consistency of the unrestricted operator; any exclusion must have a complete raw XOR witness and independently checked integer normalization. Neither experiment assumes target symmetry.

**References:** [source commit](https://github.com/ikuto32/conway-99-graph/commit/{commit}), [draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3), [compute policy](COMPUTE_POLICY.md), ledger-bound raw audits and [prospective pilot protocol](../acceleration/freeze_20261002_hypergraph_weight60_pilot_plan_v1_spec.md).
'''
    (ROOT / 'docs/RESEARCH_20261003_THIRTYSIXTH_WAVE.md').write_text(text, encoding='utf8', newline='\n')
    need((ROOT / 'CLAIMS.yaml').read_bytes() == raw, 'no concurrent ledger mutation')
    print(json.dumps(dict(status='DATED_WAVE36_MILESTONE_GENERATED', claims=337, verified=330, new_revisions=3, new_exclusions=0, target_resolution=current['target']['status'])))


if __name__ == '__main__':
    main()
