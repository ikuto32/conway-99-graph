"""Bind the independent raw checks to the exact selected population and claims."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import sys

import audit_20260917_fresh_review as check


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--run', type=Path, required=True)
    p.add_argument('--review', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    check.check(not args.out.exists(), 'preserve evidence')
    bindings = {check.key(__file__): check.digest(__file__), check.key(check.__file__): check.digest(check.__file__)}
    def read(p):
        bindings[check.key(p)] = check.digest(p)
        d = json.loads(check.path(p).read_bytes())
        for f, h in d.get('inputs_sha256', {}).items():
            check.check(check.digest(f) == h, 'input changed: '+str(f))
            bindings[check.key(f)] = h
        return d
    m = read(args.run/'manifest.json'); s = read(args.run/'summary.json'); r = read(args.review)
    ranking = read(m['ranking_audit_path'])
    available = [x for x in ranking['records'] if x['available']]
    upper = sorted(available, key=lambda x: (x['best_upper_numeric'], x['proposal_index']))
    lower = sorted(available, key=lambda x: (x['best_lower_numeric'], x['proposal_index']))
    selection = list(dict.fromkeys(x['proposal_index'] for x in upper[:8]+lower[:8]))
    for x in upper:
        if len(selection) == 16:
            break
        if x['proposal_index'] not in selection:
            selection.append(x['proposal_index'])
    check.check(m['selection_mode'] == 'union' and m['max_candidates'] == 16, 'different selection scope')
    check.check(selection == [x['proposal_index'] for x in m['selected_candidates']], 'ranking selection')
    check.check(selection == [x['proposal_index'] for x in s['records']] == [x['proposal_index'] for x in r['records']], 'population mismatch')
    check.check(len(set(selection)) == 16, 'nonunique population')
    graph_keys = []
    for chosen, produced, reviewed in zip(m['selected_candidates'], s['records'], r['records']):
        numeric = read(produced['result_path'])
        candidate = read(chosen['candidate_path'])
        graph_keys.append(tuple(sorted(tuple(e) for e in candidate['overlap_edges_outer_zero_based'])))
        original = read(chosen['ranking_domains_path']); fresh = read(numeric['domains_path'])
        domain_audit = read(numeric['domain_audit_path'])
        check.check(numeric['candidate_sha256'] == chosen['candidate_sha256'] == check.digest(chosen['candidate_path']), 'candidate identity')
        check.check(check.key(numeric['candidate_path']) == check.key(chosen['candidate_path']), 'candidate path')
        check.check([x['outer_vertex'] for x in domain_audit['independently_reenumerated_domains']] == list(range(84)), '84 complete domains')
        check.check(domain_audit['complete_used_domains_verified'] is True and
                    domain_audit['status'] == 'INDEPENDENT_EXACT_PAIR_DOMAIN_AUDIT_PASS', 'fresh completeness audit')
        check.check([x['outer_vertex'] for x in original['domains']] == list(range(84)), 'ranking domain order')
        for old, new in zip(original['domains'], fresh['domains']):
            check.check(set(old['domain_masks_hex']) == set(new['domain_masks_hex']) and
                        len(old['domain_masks_hex']) == len(new['domain_masks_hex']), 'ranking domain set identity')
        check.check(reviewed['result'] == 'INDEPENDENT_RAW_CHECK_PASS' and reviewed['fixed_K_excluded'] is True, 'nonpositive or unchecked case')
    check.check(len(set(graph_keys)) == 16, 'selected labeled graphs are not distinct')
    baseline = read('acceleration/results/20260917_independent_review/baseline_and_matrix.json')
    complete = read('acceleration/results/20260917_independent_review/baseline_fresh_domain_replay.json')
    check.check(complete['status'] == 'INDEPENDENT_EXACT_PAIR_DOMAIN_AUDIT_PASS' and complete['complete_used_domains_verified'] is True,
                'baseline fresh completeness')
    check.check([x['outer_vertex'] for x in complete['independently_reenumerated_domains']] == list(range(84)), 'baseline84')
    best = min(r['records'], key=lambda x: (check.rational(x['exact_upper']), x['proposal_index']))
    improvements = [x['proposal_index'] for x in r['records'] if check.rational(x['exact_upper']) < check.rational(baseline['baseline']['exact_lower'])]
    strictly_worse = [x['proposal_index'] for x in r['records'] if check.rational(x['exact_lower']) > check.rational(baseline['baseline']['exact_upper'])]
    check.check(strictly_worse == selection, 'not all selected intervals strictly above incumbent')
    written = Path('acceleration/results/20260917_independent_review/MATHEMATICAL_AUDIT.md')
    bindings[check.key(written)] = check.digest(written)
    report = dict(status='INDEPENDENT_CLAIM_SCOPE_BINDING_PASS', timestamp=datetime.now(timezone.utc).isoformat(),
                  source_commit=check.SOURCE, command=' '.join(sys.argv), working_directory=str(Path.cwd()), python=platform.python_version(),
                  verifier='independent_verifier agent', inputs_sha256=bindings,
                  claim_bindings=[
                      dict(id='C-STAR-BASELINE-18481', revision=1, recommendation='VERIFIED', review_state='CLEAR',
                           exact_scope='Exact original-star phase-I interval and fixed-K exclusion for raw index18481 artifact only',
                           evidence=['baseline_and_matrix.json', 'baseline_fresh_domain_replay.json', 'MATHEMATICAL_AUDIT.md']),
                      dict(id='C-FRESH-STAR-16-EXCLUSIONS', revision=2, recommendation='VERIFIED', review_state='CLEAR',
                           exact_scope='All sixteen distinct fixed overlap assignments selected by frozen union16 ranking manifest have positive exact original-star lower bounds and no target completion with these fixed edges',
                           selected_indices=selection, evidence=[check.key(args.review), check.key(args.run/'manifest.json'), 'MATHEMATICAL_AUDIT.md']),
                      dict(id='C-FRESH-STAR-16-NO-IMPROVEMENT', revision=1, recommendation='VERIFIED', review_state='CLEAR',
                           exact_scope='Every one of the sixteen selected fixed overlap assignments has its exact original-star lower bound strictly greater than the incumbent18481 exact upper bound; hence no selected assignment improves this relaxed optimum',
                           selected_indices=selection, dependencies=[dict(id='C-STAR-BASELINE-18481', revision=1, relation='uses_result'),
                               dict(id='C-FRESH-STAR-16-EXCLUSIONS', revision=2, relation='verification_dependency')],
                           evidence=[check.key(args.review), 'baseline_and_matrix.json'])],
                  distinct_selected=16, independent_raw_passes=16, complete_domain_vertices_per_candidate=84,
                  exact_strict_improvement_indices=improvements, best=best,
                  exact_intervals_strictly_above_incumbent_indices=strictly_worse,
                  baseline_completeness_execution=dict(
                      command='.\\build\\research-venv\\Scripts\\python.exe acceleration\\audit_goal_theory_pairs.py --candidate acceleration/results/20260916_star_guided_round2/search/probes/selection_03_index_18481_candidate.json --domains acceleration/results/20260916_star_guided_round2/recovered_star_shortlist/index_18481/local/stars.json --pair-certificate acceleration/results/20260916_star_guided_round2/recovered_star_shortlist/index_18481/local/pairs.json --out acceleration/results/20260917_independent_review/baseline_fresh_domain_replay.json --seconds 60',
                      timestamp=None, timestamp_null_reason='Legacy auditor did not serialize wall-clock timestamp; execution observed and reported this session',
                      elapsed_seconds=complete['elapsed_seconds'], actual_result=complete['status'],
                      method='Independent enumeration path versus native producer; repeated execution of preexisting audit code, source separately reviewed'),
                  exact_scope_limit='No symmetry or universe coverage claim; overall search coverage UNKNOWN; no validated denominator.',
                  shared_trusted_components=['Python standard library', 'raw artifact formats', 'existing complete-domain enumeration audit code reviewed in written derivation'],
                  discovery_producer_imported=False, general_nonexistence_proved=False, target_graph_constructed=False)
    check.check(all(check.digest(f) == h for f, h in bindings.items()), 'bound evidence changed')
    args.out.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(dict(status=report['status'], best=best['proposal_index'], strict_improvements=improvements)))


if __name__ == '__main__':
    main()
