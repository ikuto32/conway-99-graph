"""Generate a dated milestone from frozen claims and complete saved run records."""
import argparse, hashlib, json, subprocess, sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
import validate_claims as registry

ROOT = Path(__file__).resolve().parents[1]
BASE = 'acceleration/results/20261002_wave34_registration01/CLAIMS.before.yaml'
OBJECT = 'acceleration/results/20261002_independent_review/hypergraph_weighted_pilot02/best_object_evidence.json'
SAVED = 'acceleration/results/20261002_independent_review/hypergraph_weighted_pilot02/summary.json'
NATIVE = 'acceleration/results/20261002_hypergraph_weighted_pilot02/native/result.json'
PARITY = 'acceleration/results/20261002_independent_review/normalized_gf2_full_artifact01/summary.json'
MEANS = 'acceleration/results/20261002_independent_review/rooted6_means02/summary.json'
PUBLIC = 'acceleration/results/20261002_wave33_public_confirmation02/receipt.json'
UNION = 'acceleration/results/20261002_wave31_registration02/summary.json'


def need(ok, why):
    if not ok:
        raise ValueError(why)


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--ledger-sha256', required=True)
    args = ap.parse_args()
    out = args.out.resolve()
    need(out.is_relative_to(ROOT), 'workspace checkpoint')
    out.mkdir(parents=True, exist_ok=False)
    need(sha(ROOT / 'CLAIMS.yaml') == args.ledger_sha256, 'exact frozen current ledger')
    data, previous = registry.read_ledger(ROOT / 'CLAIMS.yaml'), registry.read_ledger(ROOT / BASE)
    prior = {c['id']: c for c in previous['claims']}
    current = {c['id']: c for c in data['claims']}
    need(len(prior) == 324 and all(current[cid] == claim for cid, claim in prior.items()), 'all324 previous material records unchanged')
    additions = [c for c in data['claims'] if c['id'] not in prior]
    need(len(additions) == 5 and all(c['status'] == 'VERIFIED' and c['review_state'] == 'CLEAR' and c['scope']['target_resolution'] == 'NONE' for c in additions), 'five exact scoped new revisions')
    names = [OBJECT, SAVED, NATIVE, PARITY, MEANS, PUBLIC, UNION]
    reports = {name: json.loads((ROOT / name).read_bytes()) for name in names}
    obj, saved, native, parity, means, publication, union = [reports[name] for name in names]
    diagnostics = obj['exact_diagnostics']
    need(diagnostics['weighted_energy'] == 3801 and diagnostics['lambda_energy'] == 63 and diagnostics['mu_energy'] == 3423 and diagnostics['base_energy'] == 3486 and diagnostics['srg_valid'] is False, 'exact saved non-SRG graph')
    need(native['proposals_this_invocation'] == 20000000 and native['stop_reason'] == 'REQUESTED_STEPS_COMPLETE', 'native-reported trajectory scope')
    need(parity['status'] == 'INDEPENDENT_NORMALIZED_GF2_THREE_FULL_PRIMALS_PASS' and parity['rows_normalization_checked'] == 85874 and parity['full_scalar_row_component_checks'] == 257622 and parity['rank_claim'] is False and parity['target_resolution'] is False, 'complete literal scalar parity certificate')
    need(means['status'] == 'INDEPENDENT_ROOTED6_PER_VERTEX_GLOBAL_MEANS_V2_PASS' and means['derived_conditional_root7_rows'] == means['saved_corners_passing_derived_rows'] == 4 and means['profiles_excluded'] == 0 and means['prism_absence_status'] == 'UNKNOWN', 'separate universal/conditional identities and no exclusion')
    counts = dict(Counter(c['status'] for c in data['claims']))
    reviews = dict(Counter(c['review_state'] for c in data['claims']))
    need(counts == dict(VERIFIED=322, CANDIDATE=3, REFUTED=4) and reviews == dict(CLEAR=329), 'frozen record counts')
    now = datetime.now(timezone.utc).isoformat()
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    checkpoint = dict(timestamp=now, source_commit=commit, source_sha256=sha(Path(__file__)), command=[sys.executable, *sys.argv], cwd=str(ROOT), registry_sha256=args.ledger_sha256, previous_report='docs/RESEARCH_20261002_THIRTYTHIRD_WAVE.md', claim_records=len(data['claims']), status_counts=counts, review_counts=reviews, verified_changes=[dict(id=c['id'], revision=c['revision'], statement=c['statement'], scope=c['scope'], evidence=c['evidence']) for c in additions], target_resolution=data['target']['status'], external_review=data['target']['external_review'], literal_population=union['literal_population'], literal_exclusions=union['distinct_literal_exclusions'], unresolved_literal_cases=union['unresolved_literal_cases'], overall_search_coverage='UNKNOWN; no validated denominator.', weighted_saved_object=diagnostics, weighted_execution=dict(native_reported_proposals=20000000, native_elapsed_seconds=native['elapsed_seconds'], saved_state_files=saved['saved_state_files'], saved_unique_steps=saved['saved_unique_steps'], complete_integer_saved_objects=saved['complete_integer_saved_objects'], sparse_selected_records=saved['sparse_selected_records'], full_anchored_proposals_replayed=saved['full_anchored_proposals_replayed'], unreplayed_sparse_records=saved['unreplayed_sparse_records'], full_trajectory_checked=saved['full_trajectory_checked']), parity=dict(raw_rows=85874, columns=23019, full_scalar_component_checks=257622, profile_population=210, excluded=0, rank_claim=False, normalization_contents={'1':82003,'2':3842,'4':29}), mean_scope=dict(universal_prism_count_corrections=True, conditional_prism_absence='UNKNOWN', new_necessary_rows=4, saved_corners_checked=4, saved_corners_passed=4, exclusions=0), publication=dict(publication_commit=publication['publication_commit'], availability_records_changed=len(publication['changed_artifact_ids']), raw_population=publication['raw_population'], independent_transition_review='PENDING; see separate audit records'), execution_state='Completed saved invocations have individual shutdown receipts; other current process states UNKNOWN because this generator is not a live monitor.', inputs_sha256={name:sha(ROOT / name) for name in [BASE, *names]}, skipped_checks=['No mathematical replay by this generator.', 'No whole20million-proposal trajectory replay.', 'No independent rank or integer-lift proof.', 'No complete historical transitive artifact audit.', 'No external target-resolution review.'])
    (out / 'CLAIMS.yaml').write_bytes((ROOT / 'CLAIMS.yaml').read_bytes())
    (out / 'checkpoint.json').write_text(json.dumps(checkpoint, indent=2) + '\n', encoding='utf8', newline='\n')
    rows = '\n'.join('| ' + c['id'] + ' r1 | ' + c['scope']['description'] + ' [Audit](../' + c['verification'][0]['command_or_audit'] + '). |' for c in additions)
    text = f'''# Thirty-fourth research milestone, 2026-10-02

Since the [thirty-third milestone](RESEARCH_20261002_THIRTYTHIRD_WAVE.md), five exact revisions are newly VERIFIED/CLEAR. They record a saved weighted-search object, finite engineering controls, complete literal parity witnesses, universal counting identities and conditional necessary rows. No target graph, general nonexistence proof or new exclusion is added.

**As of:** {now}; source commit `{commit}`; [checkpoint](../{out.relative_to(ROOT).as_posix()}/checkpoint.json); [frozen ledger](../{out.relative_to(ROOT).as_posix()}/CLAIMS.yaml). Previous report: thirty-third milestone, 324 material records.

**Verdict:** target resolution UNKNOWN. This repository has neither an independently validated target graph nor a general nonexistence proof. No target-resolution artifact has been submitted for external review. This verdict is separate from the dated literature audit. [PR3](https://github.com/ikuto32/conway-99-graph/pull/3) remains draft; research authorization remains active.

**Verified changes:** all 324 prior material records retain their exact statements and checks. New revisions have the following scopes.

| Claim | Exact scope and evidence |
| --- | --- |
{rows}

**Work completed:** the weighted pilot reported 20,000,000 proposals in {native['elapsed_seconds']:.3f} native seconds. Independent checking verified {saved['saved_state_files']} saved states at {saved['saved_unique_steps']} distinct steps and {saved['complete_integer_saved_objects']} complete current/best objects. It replayed {saved['full_anchored_proposals_replayed']} anchored sparse proposals among {saved['sparse_selected_records']} saved records; {saved['unreplayed_sparse_records']} gap records remain unreplayed. The full trajectory and its native counter are not independently certified.

For the fixed rooted8 operator, all 85,874 literal rows were divided by their exact positive integer content. The content census is 82,003 rows of content 1, 3,842 of content 2 and 29 of content 4. Three complete 23,019-coordinate binary vectors passed all 257,622 independent scalar row/component checks. They provide a parity solution for every integer pair (a,b), including all 210 frozen profiles. Zero profiles are excluded. No rank, integer lift, nonnegative solution or graph realization follows. The 343,414,964-byte native resume checkpoint remains LOCAL_ONLY and was hash-checked only; it is unnecessary for checking the three-vector mathematical certificate.

An independent ordered-wedge/marked-four-cycle derivation establishes, for every finite simple srg(n,k,1,2) with nonedges and every vertex u,
`sum_v a(u,v) + 2*T_u = k*(k-2)` and
`sum_v b(u,v) + T_u = n-k-1`, where sums range over nonneighbors of u and T_u counts induced prism sixsets containing u. Global summation gives corrections 12T and 6T. No prism absence or target symmetry is assumed. Written bijections establish the theorem; finite checks on rook9/243 and nonzero raw shapes calibrate it. Under the UNKNOWN prism-free target premise, per-vertex means are (2,1). Four resulting root7 equations are necessary under that premise, and all four already saved exact corners satisfy them. Their rational interpolation family is therefore not excluded by these rows.

**Coverage:** 329 material claim records: 322 VERIFIED/CLEAR, three CANDIDATE/CLEAR and four REFUTED/CLEAR. The fixed-support campaign remains at {union['distinct_literal_exclusions']} checked literal cases among {union['literal_population']}, leaving {union['unresolved_literal_cases']} unresolved. Those units are literal representative cases, not graphs or equal work. Overall search coverage: UNKNOWN; no validated denominator.

**Best result:** for fixed objective `SRG_LAMBDA_WEIGHTED_PAIR_RESIDUAL_V1`, F=6E_lambda+E_mu, the new saved graph has F=3801, E_lambda=63 and E_mu=3423. It is 99-vertex 14-regular and a point graph of 231 linear triples, but fails the target integer identity at 4,814 ordered entries. Its ordinary objective `SRG_SQUARED_PAIR_RESIDUAL_V1` is E=3486, worse than the previous saved E=3034. Weighted and ordinary objectives are distinct; the new graph is not a target construction or performance guarantee.

**Problems:** publication setup01 had a mistyped frozen-ledger CLI hash and was rejected before publication checks; unchanged-source setup02 read the frozen record field. Normalized preflight01 could not observe all Linux executable identities, and explicit-root preflight02 hit Git ownership protection; preflight03 used root observation plus a process-scoped safe.directory for this exact workspace, while science used the calibrated user context. Both setup failures are preserved. Registration02/v7 rejected nested shared-component metadata; registration03/v8 admitted only the exact bound adapter and retained its rich original scope. Registration04/v8 rejected a conditional statement against the universal report headline; registration05/v9 admitted only the two frozen means bindings, preserving the schema kind-spelling correction. No failed attempt mutated material claims. Independent publication/ledger transition reviews remain pending in separate records; checker failures cannot count as approval or theorem refutation.

**Publication:** {len(publication['changed_artifact_ids'])} new wave33 artifact availability records were authenticated against [immutable public commit]({ 'https://github.com/ikuto32/conway-99-graph/commit/' + publication['publication_commit'] }). Five raw models totaling 184,494,332 bytes recover losslessly from 25 gzip parts totaling 6,873,080 bytes. This was byte recovery, not a mathematical replay. New wave34 evidence is still LOCAL_ONLY until a separate immutable publication audit. Historical transitive gate closure and platform binaries have separate availability.

**Execution:** the weighted pilot and normalized solve have completed, with independently checked outputs and saved contained shutdown receipts. Mean-check invocations are complete. This dated generator does not observe other live processes. Reaching the milestone does not stop authorized research.

**Next experiment:** a newly implemented and independently gated packed calculation modulo 3 on the same necessary integer operator, emitting three complete primal vectors or an original-row coefficient relation. Divisors 1,2,4 are units modulo 3; the engineering controls must distinguish this from division by a factor of 3. Any profile exclusion remains local and conditional on its recorded graph-necessity premise. Preserve all failures, checkpoint on stop and admit no rank claim without a rank certificate.

**References:** [source commit](https://github.com/ikuto32/conway-99-graph/commit/{commit}), [draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3), [compute policy](COMPUTE_POLICY.md), the ledger-bound audits above and saved supervisor manifests. Schema/CI checks are engineering controls, not mathematical verification.
'''
    (ROOT / 'docs/RESEARCH_20261002_THIRTYFOURTH_WAVE.md').write_text(text, encoding='utf8', newline='\n')
    print(json.dumps(dict(status='DATED_WAVE34_MILESTONE_GENERATED', claims=329, verified=322, new_revisions=5, new_exclusions=0, target_resolution=data['target']['status'])))


if __name__ == '__main__':
    main()
