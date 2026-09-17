"""Bind independent same-sign star certificates to the exact near-zero shortlist."""
import argparse
from fractions import Fraction
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone

import audit_20260917_fresh_review as raw


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--round', type=Path, required=True)
    p.add_argument('--review', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    args = p.parse_args()
    raw.check(not args.out.exists(), 'preserve evidence')
    started = time.perf_counter()
    bindings = {}
    def bind(p, expected=None):
        k = raw.key(p)
        if k not in bindings: bindings[k] = raw.digest(p)
        raw.check(expected is None or bindings[k] == expected, 'input hash differs: '+k)
        return bindings[k]
    def read(p):
        bind(p)
        d = json.loads(raw.path(p).read_bytes())
        for f, h in d.get('inputs_sha256', {}).items(): bind(f, h)
        return d
    bind(__file__); bind(raw.__file__); bind('uv.lock')
    m = read(args.round/'star_shortlist/manifest.json')
    s = read(args.round/'star_shortlist/summary.json')
    search = read(args.round/'search/summary.json')
    audit = read(args.round/'search/audit.json')
    checkpoint = read(args.round/'checkpoint.json')
    reviewed = read(args.review)
    family = read(args.round/'family/all.json')
    family_audit = read(args.round/'family/independent_audit.json')
    baseline = read('acceleration/results/20260917_independent_review/baseline_and_matrix.json')['baseline']
    for f, h in checkpoint['direct_artifacts_sha256'].items(): bind(f, h)
    raw.check(family_audit['status'] == 'INDEPENDENT_COMPLETE_WHOLE_SAME_SIGN_MATCHING_FAMILY_PASS' and
              family_audit['final_labeled_edge_set_equality_checked'] is True, 'complete independently checked family')
    family_bindings = {raw.key(f): h for f, h in family_audit['inputs_sha256'].items()}
    raw.check(family_bindings[raw.key(args.round/'family/all.json')] == bind(args.round/'family/all.json'), 'family audit association')
    for k in ('raw_including_initial', 'unchanged_count', 'cap_rejected_count', 'legal_count'):
        raw.check(family[k] == family_audit[k] == sum(x[k] for x in family_audit['by_class']), 'family partition '+k)
    raw.check(family['legal_count'] == len(family['overlap_candidates']) == len(family['moves']) == 81000, 'family inventory')
    raw.check(audit['status'] == 'INDEPENDENT_CP_MATCHING_SEARCH_AUDIT_PASS' and
              audit['actual_LP_exact_intervals_checked'] == len(audit['probe_reports']) == len(search['records']) == 64,
              '64 edge LP audit records')
    raw.check(len({x['proposal_index'] for x in search['records']}) == len({x['proposal_index'] for x in audit['probe_reports']}) == 64, '64 distinct indices')
    by_index = {x['proposal_index']: x for x in search['records']}
    eligible = []
    for row in audit['probe_reports']:
        source = by_index[row['proposal_index']]
        raw.check(raw.key(row['candidate_path']) == raw.key(source['candidate_path']) and
                  raw.key(row['result_path']) == raw.key(source['result_path']), 'edge audit candidate/result association')
        edge_audit = row['phase1_audit']
        raw.check(edge_audit['status'] == 'INDEPENDENT_PHASE1_GRAPH_MODEL_PRIMAL_DUAL_AUDIT_PASS' and
                  edge_audit['all_graph_rows_checked'] is True, 'edge interval audit status')
        bound = {raw.key(f): h for f, h in edge_audit['inputs_sha256'].items()}
        raw.check(bound[raw.key(row['candidate_path'])] == bind(row['candidate_path'], source['candidate_sha256']) and
                  bound[raw.key(row['result_path'])] == bind(row['result_path'], source['result_sha256']), 'edge interval raw binding')
        lower, upper = raw.rational(edge_audit['exact_dual_lower_bound']), raw.rational(edge_audit['exact_primal_upper_bound'])
        raw.check(lower <= upper and upper >= 0, 'invalid edge interval')
        if lower <= 0 and upper <= Fraction(1, 100000000):
            eligible.append((upper, row['proposal_index'], lower))
    eligible.sort()
    selection = [i for upper, i, lower in eligible]
    raw.check(selection == [x['proposal_index'] for x in m['selected_candidates']] ==
              [x['proposal_index'] for x in s['records']] == [x['proposal_index'] for x in reviewed['records']], 'complete near-zero selection')
    raw.check(len(selection) == 13 and m['eligible_candidates'] == 13 and m['max_candidates'] >= 13 and
              m['unselected_eligible_indices'] == s['unselected_eligible_indices'] == checkpoint['unselected_eligible_indices'] == [], 'unselected eligible cases')
    raw.check(raw.rational(m['baseline_exact_lower']) == raw.rational(baseline['exact_lower']) and
              raw.rational(m['baseline_exact_upper']) == raw.rational(baseline['exact_upper']), 'baseline exact interval identity')
    graph_keys = []
    for chosen, result, checked in zip(m['selected_candidates'], s['records'], reviewed['records']):
        i = chosen['proposal_index']
        candidate = read(chosen['candidate_path']); numeric = read(result['result_path'])
        raw.check(candidate['overlap_edges_outer_zero_based'] == family['overlap_candidates'][i], 'candidate not indicated family member')
        graph_keys.append(tuple(tuple(e) for e in candidate['overlap_edges_outer_zero_based']))
        raw.check(numeric['candidate_sha256'] == bind(chosen['candidate_path'], chosen['candidate_sha256']) and
                  raw.key(numeric['candidate_path']) == raw.key(chosen['candidate_path']), 'raw third audit candidate association')
        domains = read(numeric['domains_path']); complete = read(numeric['domain_audit_path'])
        raw.check(complete['status'] == 'INDEPENDENT_EXACT_PAIR_DOMAIN_AUDIT_PASS' and complete['complete_used_domains_verified'] is True and
                  [x['outer_vertex'] for x in complete['independently_reenumerated_domains']] == list(range(84)), '84 complete original domains')
        raw.check(numeric['original_complete_domains_used'] is True and numeric['pair_pruned_domains_used'] is False and
                  domains['complete_domain_enumeration'] is True, 'unchanged original star objective scope')
        raw.check(checked['result'] == 'INDEPENDENT_RAW_CHECK_PASS' and checked['fixed_K_excluded'] is True and
                  raw.rational(checked['exact_lower']) > raw.rational(baseline['exact_upper']), 'positive exact bound / no improvement')
        raw.check(raw.rational(result['exact_lower']) == raw.rational(checked['exact_lower']) and
                  raw.rational(result['exact_upper']) == raw.rational(checked['exact_upper']), 'saved interval consistency')
    raw.check(len(set(graph_keys)) == 13, 'distinct selected labeled graphs')
    for key_, expected in [('family_legal_candidates', 81000), ('CP_LP_artifacts', 64), ('near_zero_eligible', 13),
                           ('star_evaluated_candidates', 13), ('exact_star_exclusions', 13), ('exact_star_improvement_count', 0)]:
        raw.check(checkpoint[key_] == expected, 'checkpoint count '+key_)
    raw.check(checkpoint['star_records'] == s['records'] and checkpoint['current_star_best_changed'] is False and
              checkpoint['current_star_marginal_best']['proposal_index'] == 18481 and checkpoint['pending_completion_work'] is None,
              'checkpoint current-star state')
    best = min(reviewed['records'], key=lambda r: (raw.rational(r['exact_upper']), r['proposal_index']))
    raw.check(all(raw.digest(f) == h for f, h in bindings.items()), 'bound evidence changed')
    report = dict(status='INDEPENDENT_SAME13_SELECTION_SCOPE_AND_INTERVAL_COMPARISON_PASS',
        timestamp=datetime.now(timezone.utc).isoformat(), source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=raw.ROOT, text=True).strip(),
        command=[sys.executable]+sys.argv, working_directory=str(Path.cwd()), python=platform.python_version(), inputs_sha256=bindings,
        claim_bindings=[dict(id='C-SAME-STAR-13-EXCLUSIONS', revision=1, recommendation='VERIFIED',
                            scope='Exactly the13 distinct labeled assignments listed here, each with positive independent exact original-star lower bound; no target completion of these fixed assignments under prescribed absent edges', indices=selection),
                        dict(id='C-SAME-STAR-13-NO-IMPROVEMENT', revision=1, recommendation='VERIFIED',
                            scope='All13 selected original-star lower bounds strictly exceed incumbent18481 original-star upper bound; no selected assignment improves this objective', indices=selection,
                            dependencies=[dict(id='C-STAR-BASELINE-18481', revision=1, relation='uses_result'), dict(id='C-SAME-STAR-13-EXCLUSIONS', revision=1, relation='verification_dependency')])],
        family_counts={k: family_audit[k] for k in ('raw_including_initial', 'unchanged_count', 'cap_rejected_count', 'legal_count', 'unrestricted_matchings_independently_enumerated')},
        family_count_scope='One same-sign matching coordinate replaced at a time,14 coordinates of this fixed baseline; count reused from freshly independently enumerated family report, source reviewed, not reenumerated here',
        coarse_candidates=search['coarse_candidate_count'], refined_candidates=search['refined_candidate_count'], edge_LP_cases=64,
        eligible_cases=13, selected_distinct_labeled_graphs=13, unselected_eligible_cases=0, independent_raw_passes=13, best=best,
        selection_threshold='Exact edge lower <=0 and0<=exact edge upper<=1/100000000; sorted exact upper then proposal index',
        selection_intervals_recomputed_here=False, selection_interval_dependency='Hash-bound full99 independent edge-LP audits in search/audit.json; this checker redoes selection arithmetic, not all64 edge audits',
        checkpoint_scope='Direct115 artifacts and requested current-star/round state checked; inherited6686-reference inventory and unrelated old-edge best are not reapproved as mathematics',
        shared_trusted_components=['Python standard library','new third-path checker arithmetic utilities','previous independent complete-domain and family auditors'],
        producer_imported=False, target_resolution='UNKNOWN', overall_search_coverage='UNKNOWN; no validated denominator', elapsed_seconds=time.perf_counter()-started)
    with args.out.open('x', encoding='utf-8') as f:
        json.dump(report, f, indent=2); f.write('\n')
    print(json.dumps(dict(status=report['status'], best_index=best['proposal_index'], family=family['legal_count'], selected=len(selection))))


if __name__ == '__main__':
    main()
