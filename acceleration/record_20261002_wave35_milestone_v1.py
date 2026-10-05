"""Generate the exact wave35 checkpoint from its ledger and checked artifacts."""
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
BASE = 'acceleration/results/20261002_wave35_registration01/CLAIMS.before.yaml'
EXPECTED = {
    'C-99-LINEAR-TRIPLE-POINTGRAPH-LAMBDA-ZERO-CRITERION',
    'C-HYPERGRAPH-WEIGHTED-PILOT02-EXTRA-TRIANGLE-ROOT-CENSUS',
    'C-UNRESTRICTED-ROOTED6-NONEDGE-INTEGER-DOMAIN',
    'C-UNRESTRICTED-ROOTED6-EDGE-KERNEL-INTEGER-DOMAIN',
    'C-PRISMFREE-ROOTED8-ORIGINAL-LITERAL-GF3-THREE-PRIMALS',
}
REPORTS = {
    'nonedge': 'acceleration/results/20261002_independent_review/rooted6_unrestricted_domain01/summary.json',
    'edge': 'acceleration/results/20261002_independent_review/rooted6_unrestricted_edge_domain01/summary.json',
    'gf3': 'acceleration/results/20261002_independent_review/gf3_full_artifact01/summary.json',
    'census': 'acceleration/results/20261002_independent_review/lambda_phase_structure01/saved_root_census_evidence_v2.json',
    'publication': 'acceleration/results/20261002_independent_review/wave34_availability01/summary.json',
    'execution': 'acceleration/results/20261002_rooted8_gf3_solve_supervision01/summary.json',
    'union': 'acceleration/results/20261002_wave31_registration02/summary.json',
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
    out.mkdir(parents=True, exist_ok=False)
    raw = (ROOT / 'CLAIMS.yaml').read_bytes()
    need(hashlib.sha256(raw).hexdigest() == args.ledger_sha256, 'frozen ledger')
    current = registry.read_ledger(ROOT / 'CLAIMS.yaml')
    baseline = registry.read_ledger(ROOT / BASE)
    prior = {c['id']: c for c in baseline['claims']}
    additions = [c for c in current['claims'] if c['id'] not in prior]
    need(len(prior) == 329 and {c['id'] for c in additions} == EXPECTED, 'exact population and five new scopes')
    need(all(next(c for c in current['claims'] if c['id'] == cid) == old for cid, old in prior.items()), 'previous material records unchanged')
    need(all(c['revision'] == 1 and c['status'] == 'VERIFIED' and c['review_state'] == 'CLEAR' and c['scope']['target_resolution'] == 'NONE' for c in additions), 'exact checked r1 scopes')
    reports = {key: json.loads((ROOT / name).read_bytes()) for key, name in REPORTS.items()}
    gf3, execution, union = [reports[key] for key in ['gf3', 'execution', 'union']]
    need(gf3['status'] == 'INDEPENDENT_ORIGINAL_LITERAL_GF3_THREE_PRIMALS_V1_PASS' and gf3['literal_result']['scalar_raw_row_component_checks'] == 257622 and gf3['profile_domain']['population'] == gf3['profile_domain']['literal_mod3_compatible_profiles'] == 210 and gf3['profile_domain']['excluded_profiles'] == 0 and not gf3['rank_claim'] and not gf3['target_resolution'], 'complete scoped modular certificate')
    need(execution['command_exit_code'] == 0 and execution['cleanup']['reaped'] is True, 'completed execution receipt')
    counts = dict(Counter(c['status'] for c in current['claims']))
    reviews = dict(Counter(c['review_state'] for c in current['claims']))
    need(len(current['claims']) == 334 and counts == {'VERIFIED': 327, 'CANDIDATE': 3, 'REFUTED': 4} and reviews == {'CLEAR': 334}, 'exact frozen ledger totals')
    now = datetime.now(timezone.utc).isoformat()
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    checkpoint = dict(timestamp=now, source_commit=commit, command=[sys.executable, *sys.argv], cwd=str(ROOT), source_sha256=sha(Path(__file__)), ledger_sha256=args.ledger_sha256, previous_report='docs/RESEARCH_20261002_THIRTYFOURTH_WAVE.md', claim_records=334, status_counts=counts, review_counts=reviews, verified_changes=[dict(id=c['id'], revision=c['revision'], statement=c['statement'], scope=c['scope'], evidence=c['evidence']) for c in additions], target_resolution=current['target']['status'], external_review=current['target']['external_review'], literal_population=union['literal_population'], literal_exclusions=union['distinct_literal_exclusions'], unresolved_literal_cases=union['unresolved_literal_cases'], overall_search_coverage='UNKNOWN; no validated denominator.', new_exclusions=0, report_paths=REPORTS, gf3_summary=dict(rows=85874,columns=23019,scalar_checks=257622,compatible_profiles=210,excluded_profiles=0,rank_claim=False), inputs_sha256={name: sha(ROOT / name) for name in [BASE, *REPORTS.values()]}, execution_state='GF3 invocation completed with saved containment receipt. Other process states UNKNOWN: this generator does not observe live processes.', skipped_checks=['No mathematical replay by this generator.', 'No independent rank of the full rooted8 operator.', 'No integer lift, nonnegative rooted8 solution, graph realization or target coverage.', 'No whole construction trajectory replay.', 'No external review or fresh literature audit.'])
    (out / 'CLAIMS.yaml').write_bytes(raw)
    (out / 'checkpoint.json').write_text(json.dumps(checkpoint, indent=2) + '\n', encoding='utf8', newline='\n')
    rows = '\n'.join('| ' + c['id'] + ' r1 | ' + c['scope']['description'] + ' [Audit](../' + c['verification'][0]['command_or_audit'] + '). |' for c in additions)
    text = f'''# Thirty-fifth research milestone, 2026-10-02

Since the [thirty-fourth milestone](RESEARCH_20261002_THIRTYFOURTH_WAVE.md), five exact revisions are newly VERIFIED/CLEAR. They establish unrestricted local integer domains, one linear-triple criterion, one saved graph census and a complete literal mod-3 certificate. No target graph, general nonexistence proof or new exclusion is added.

**As of:** {now}; source commit `{commit}`; [checkpoint](../{out.relative_to(ROOT).as_posix()}/checkpoint.json); [frozen ledger](../{out.relative_to(ROOT).as_posix()}/CLAIMS.yaml). Previous report: wave34, 329 material records.

**Verdict:** target resolution UNKNOWN. This repository has no independently validated target graph or general nonexistence proof. No target-resolution evidence package awaits external review. This is separate from the dated literature audit. [PR3](https://github.com/ikuto32/conway-99-graph/pull/3) remains draft and research remains authorized.

**Verified changes:** all329 previous material records retain their exact statements and checking records.

| Claim | Exact scope and evidence |
| --- | --- |
{rows}

**Work completed:** the complete nonedge local affine domain contains651 necessary integer vectors:210 at c=0,210 at c=1 and231 at c=2. All693 containing-box triples were checked;42 rejected cases are preserved. Eight rational vertices and six literal coordinate facets prove the continuous-domain equivalence. Every accepted vector passes all1445 raw equations. The c=0 face agrees algebraically with the earlier210-profile domain; c=0 at one root does not establish global prism absence.

The ordered-edge local operator has exact rational rank392 and nullity2, established by a new independent prime1009 elimination and two exact integral kernels. Its complete nonnegative integer domain consists of91 vectors with0<=s<=12 and0<=t<=6. Four vertices/facet witnesses and all1099 rows at every vector were checked. The former conditional rigidity theorem supplies no unrestricted rank premise; reuse concerns the separately checked raw operator/geometry artifact only.

The original rooted8 operator produced three complete23019-trit vectors in the saved GF3 invocation. Independent checking validated all85874 original rows, literal content/hash records and257622 scalar row components, and rejected corruption of an actual vector. All210 conditional integer profiles survive, with zero exclusions. No rank, integer lift, nonnegative feasibility or graph realization follows. The494930751-byte native checkpoint remains LOCAL_ONLY and was hash-checked only; it is unnecessary for the mathematical primal-vector certificate.

For99 points and231 linear triples of point degree7, E_lambda=0 is equivalent to having exactly those231 graph triangles. It implies a nonadjacent common-neighbor mean2 at every root, which does not impose mu2 on each pair. The saved weight6 pilot has252 triangles, including21 extras covering53 vertices. It has46 clean roots, but zero of99 roots meet both recorded necessary conditions for direct full warm-scaffold import. That census excludes this import of this object, not a target graph.

**Coverage:**334 material claims:327 VERIFIED/CLEAR,3 CANDIDATE/CLEAR and4 REFUTED/CLEAR. The fixed-support campaign remains{union['distinct_literal_exclusions']} checked literal representative cases of{union['literal_population']}, with{union['unresolved_literal_cases']} unresolved. Necessary local profiles are not graph populations or equal work units. Overall search coverage: UNKNOWN; no validated denominator.

**Best result:** among the two audited native construction pilot objects compared here, the unweighted object has ordinary E=3034. The weight6 object has its own F6=3801=6*63+3423 and ordinary E=3486, which is worse. These comparisons use SRG_SQUARED_PAIR_RESIDUAL_V1 on the same99-point linear-triple domain. Both fail the integer SRG identity. The modular certificates establish finite-field consistency of one conditional necessary operator; they supply no target bound or graph.

**Problems:** the first GF3 wrapper incorrectly demanded a particular solution of an underdetermined control system. The new version checks literal equations; the original failure is preserved. An overbroad lambda-criterion draft was vetoed and narrowed to the exact99-point statement without overwriting the draft. New claim evidence remains LOCAL_ONLY until immutable publication is independently authenticated. Frozen ledger impact review has separate records. No failed checker or timeout is a nonexistence proof.

**Publication:** the [separate wave34 publication audit](AUDIT_20261002_WAVE34_PUBLICATION_CONFIRMED.md) preserves all329 material claims and confirms739 new artifact records PUBLIC, with one native checkpoint retained locally. It authenticated938 stage records/968 distinct Git blobs and losslessly decoded five raw models from25 gzip parts. This is byte authentication, not mathematical replay or a second clean-clone transfer.

**Execution:** the GF3 invocation completed in{execution['elapsed_seconds']:.3f} outer seconds and has a saved reaped process-group receipt. Its161.729 native seconds include checkpoint/output work; no whole-group peak-memory or general performance guarantee is asserted. Domain and census checks completed with their own containment receipts. This generator does not observe other live processes; the milestone does not stop authorized research.

**Next experiment:** build and independently reconstruct the unrestricted rooted7 operator with primary nonedge parameters(c,a,b), variable secondary-edge parameters(s,t), and exact per-vertex prism/mean coupling. It must retain all2770 locally admissible classes and assume no target automorphism or uniform secondary profile. In parallel prepare a new fixed-weight60 construction engine with fresh independent controls; save and check the first lambda-zero object separately if one appears. No scientific approval transfers from the old engine.

**References:** [source commit](https://github.com/ikuto32/conway-99-graph/commit/{commit}), [draft PR3](https://github.com/ikuto32/conway-99-graph/pull/3), [compute policy](COMPUTE_POLICY.md), ledger-bound audits above and raw supervisor records. Schema validation is not mathematical verification.
'''
    (ROOT / 'docs/RESEARCH_20261002_THIRTYFIFTH_WAVE.md').write_text(text, encoding='utf8', newline='\n')
    need((ROOT / 'CLAIMS.yaml').read_bytes() == raw, 'no concurrent ledger change')
    print(json.dumps(dict(status='DATED_WAVE35_MILESTONE_GENERATED', claims=334, verified=327, new_revisions=5, new_exclusions=0, target_resolution=current['target']['status'])))


if __name__ == '__main__':
    main()
