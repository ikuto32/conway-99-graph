"""Independent two-trade coupled-search and intermediate-state audit.

No search driver, native generator, phase-I producer, or solver is imported.
Numerical objective agreement is not an optimum or infeasibility certificate.
Native gate records are checked for input, export, hash and status consistency;
this script does not independently establish completeness or pair-AC support.
"""
import argparse
from collections import Counter
from hashlib import sha256
import json
from math import isfinite
from pathlib import Path
import re
import time

from audit_certificate import full_graph, require
from audit_phase1 import evaluate, graph_rows, compare_rows
from audit_phase1_kkt import inspect_artifact

ROOT = Path(__file__).resolve().parents[1]


def resolve(name):
    path = Path(str(name).replace('\\', '/'))
    return path.resolve() if path.is_absolute() else (ROOT/path).resolve()


def signature(edges):
    return tuple(sorted(map(tuple, edges)))


def trade(known, removed, added):
    require(type(removed) is list and type(added) is list and len(removed) == len(added) == 2, 'Trade edge count')
    for edge in removed+added:
        require(type(edge) is list and len(edge) == 2 and all(type(v) is int for v in edge)
                and 0 <= edge[0] < edge[1] < 84, 'Invalid canonical trade edge')
    old, new = set(map(tuple, removed)), set(map(tuple, added))
    require(len(old) == len(new) == 2 and old <= known and not new & known, 'Trade absent/present mismatch')
    endpoints = Counter(v for edge in old for v in edge)
    require(len(endpoints) == 4 and set(endpoints.values()) == {1}
            and endpoints == Counter(v for edge in new for v in edge), 'Trade degree balance')
    return (known-old)|new


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--initial', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), 'Audit output must be new')
    started = time.perf_counter()
    hashes = {}

    def digest(path):
        path = resolve(path)
        value = sha256(path.read_bytes()).hexdigest()
        hashes[path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix()] = value
        return value

    def load(path):
        digest(path)
        return json.loads(resolve(path).read_bytes())

    manifest = load(args.run/'manifest.json')
    summary = load(args.run/'summary.json')
    require(summary['status'] == 'BOUNDED_TWO_TRADE_COUPLED_SEARCH_FINISHED', 'Search is not finished')
    require(summary['manifest'] == manifest, 'External and embedded manifest differ')
    require(manifest['trades_per_move'] == 2, 'Wrong atomic-trade budget')
    for name, expected in manifest['inputs_sha256'].items():
        require(digest(name) == expected, f'Search source/input changed: {name}')
    require(any(resolve(name) == resolve(args.initial) and expected == digest(args.initial)
                for name, expected in manifest['inputs_sha256'].items()), 'Initial input not bound')
    initial = load(args.initial)['overlap_edges_outer_zero_based']
    full_graph({'overlap_edges_outer_zero_based': initial})
    best = load(args.run/'best_candidate.json')
    copied_best = load(args.run/'best_phase1.json')
    probes = {}
    probe_reports = []
    max_error = 0.0
    numeric_unknown = 0
    exact_positive_bounds = 0
    maximum_primal_dual_gap = 0.0
    for path in sorted((args.run/'probes').glob('*_phase1.json')):
        result = load(path)
        candidate_path = resolve(result['candidate_path'])
        candidate = load(candidate_path)
        require(result['candidate_sha256'] == digest(candidate_path), 'Phase-I candidate hash mismatch')
        require(resolve(candidate['source_manifest']) == resolve(args.run/'manifest.json'), 'Probe manifest link mismatch')
        edges = candidate['overlap_edges_outer_zero_based']
        full_graph(candidate)
        canonical = json.dumps([list(edge) for edge in signature(edges)], separators=(',', ':')).encode('ascii')
        require(result['overlap_edges_sha256'] == sha256(canonical).hexdigest(), 'Canonical edge identity mismatch')
        for name, expected in result['source_sha256'].items():
            require(Path(name).name == name and digest(ROOT/'acceleration'/name) == expected, 'Phase-I source changed')
        variables, rows, omitted = graph_rows(candidate)
        require(result['edge_variables'] == [list(edge) for edge in variables], 'Fractional X column order differs')
        compare_rows(result['constraint_groups'], rows)
        value, x = result.get('numeric_objective'), result.get('numeric_edge_values')
        usable = result.get('optimal') is True and type(value) in (int, float) and isfinite(value) and value >= -1e-7
        usable = usable and type(x) is list and len(x) == 1680 and all(type(v) in (int, float) and isfinite(v) and 0 <= v <= 1 for v in x)
        reference = None
        if x is not None:
            reference = evaluate(candidate, x)
            require(type(value) in (int, float) and isfinite(value), 'Merit missing for numeric X')
            error = abs(value-reference['total_violation'])
            require(error <= 1e-7*(1+abs(value)), 'Actual LP merit differs from independent full99 evaluation')
            breakdown = result['residual_breakdown']
            require(abs(breakdown['quota_absolute_sum']-reference['quota_violation']) <= 1e-7*(1+abs(value))
                    and abs(breakdown['pair_cap_positive_sum']-reference['pair_violation']) <= 1e-7*(1+abs(value)),
                    'LP objective components differ')
            max_error = max(max_error, error)
        primal_dual = None
        if usable:
            primal_dual = inspect_artifact(candidate_path, resolve(path))
            exact_positive_bounds += primal_dual['exact_positive_dual_bound']
            maximum_primal_dual_gap = max(maximum_primal_dual_gap,
                                         primal_dual['exact_primal_dual_gap']['approximate'])
        numeric_unknown += not usable
        key = resolve(path)
        probes[key] = {'candidate_signature': signature(edges), 'candidate_path': candidate_path,
                       'objective': value, 'x': x, 'usable': usable}
        probe_reports.append({'result_path': key.relative_to(ROOT).as_posix(),
                              'candidate_sha256': result['candidate_sha256'], 'usable_numerical_optimum': usable,
                              'numeric_objective': value,
                              'independent_objective': reference['total_violation'] if reference else None,
                              'independent_primal_dual_audit': primal_dual})
    require(len(probes) == summary['phase1_evaluations'] and numeric_unknown == summary['numeric_unknown_probes'],
            'Saved probe totals differ from summary')

    def check_probe(record, expected_edges=None):
        path = resolve(record['result_path'])
        require(path in probes, 'Trace references missing LP probe')
        probe = probes[path]
        require(resolve(record['candidate_path']) == probe['candidate_path']
                and record['candidate_sha256'] == digest(probe['candidate_path'])
                and record['result_sha256'] == digest(path), 'Trace LP artifact binding mismatch')
        require(record['objective'] == probe['objective'] and record['usable'] is probe['usable'], 'Trace LP value/status mismatch')
        if expected_edges is not None:
            require(probe['candidate_signature'] == signature(expected_edges), 'Cached/selected probe attached to wrong K')
        return probe

    local_reports = {}
    local_status_counts = Counter()

    def check_local(report, expected_edges):
        require(type(report['passed']) is bool, 'Native gate pass flag must be boolean')
        bound = {key: value for key, value in report.items() if key != 'proposal_index'}
        key = signature(expected_edges)
        if key in local_reports:
            require(bound == local_reports[key], 'Cached local gate report changed')
            return
        for field in ('candidate_input', 'stars_path'):
            sha_field = 'stars_sha256' if field == 'stars_path' else field+'_sha256'
            require(digest(report[field]) == report[sha_field], 'Native gate artifact hash mismatch')
        tokens = resolve(report['candidate_input']).read_text(encoding='ascii').split()
        require(tokens[:2] == ['C99OVERLAPS1', '1'] and len(tokens) == 338, 'Native local candidate format')
        values = list(map(int, tokens[2:]))
        require(signature(zip(values[::2], values[1::2])) == key, 'Native gate attached to wrong candidate')
        stars = load(report['stars_path'])
        require(report['star_status'] == stars['status'], 'Star report status mismatch')
        require(stars['caps'] == {'seconds': 30, 'global_nodes': 2000000, 'per_vertex_domains': 20000},
                'Native star enumeration caps differ')
        if stars['status'] == 'COMPLETE_DOMAINS_RECIPROCITY_ARC_CONSISTENT_NONEMPTY':
            require(stars['complete_domain_enumeration'] is True and len(stars['domains']) == 84,
                    'Native completed-star report inconsistent')
            domains = stars['domains']
            require([row['outer_vertex'] for row in domains] == list(range(84)), 'Star row ordering differs')
            require(all(row['status'] == 'COMPLETE' and row['cap_reason'] is None and row['domain_masks_hex']
                        for row in domains), 'Native completed-star row inconsistent')
            for field in ('domain_input', 'pair_path'):
                sha_field = 'pair_sha256' if field == 'pair_path' else field+'_sha256'
                require(digest(report[field]) == report[sha_field], 'Native pair artifact hash mismatch')
            expected_export = 'C99DOMAINS1 84\n'+''.join(str(len(row['domain_masks_hex']))+' '+
                ' '.join(row['domain_masks_hex'])+'\n' for row in domains)
            require(resolve(report['domain_input']).read_text(encoding='ascii') == expected_export,
                    'Pair input is not the complete original star-domain export')
            pair = load(report['pair_path'])
            require(pair['status'] == report['pair_status'], 'Native pair report status mismatch')
            require(pair['caps'] == {'seconds': 30, 'domain_pairs': 500000000}, 'Native pair caps differ')
            require(report['passed'] is (pair['status'] == 'EXACT_PAIR_DOMAIN_ARC_CONSISTENT_NONEMPTY'),
                    'Native gate incorrectly treated status as pass')
            require(len(pair['surviving_domain_ids']) == 84, 'Native pair survivor dimensions')
            for row, survivors in zip(domains, pair['surviving_domain_ids']):
                require(len(survivors) == len(set(survivors)) and all(type(i) is int and
                        0 <= i < len(row['domain_masks_hex']) for i in survivors), 'Invalid native surviving domain ID')
            if report['passed']:
                require(pair['propagation_status'] == 'ARC_CONSISTENT_NONEMPTY' and pair['cap_reason'] is None
                        and all(pair['surviving_domain_ids']), 'Native complete pair nonempty report inconsistent')
            local_status_counts['pair:'+pair['status']] += 1
        else:
            require(report['passed'] is False and 'pair_path' not in report and 'domain_input' not in report,
                    'Incomplete/empty native stars incorrectly passed or fed to pair filter')
        local_status_counts['star:'+stars['status']] += 1
        local_reports[key] = bound

    current = set(map(tuple, initial))
    snapshots = summary['overlap_candidates']
    require(signature(snapshots[0]) == signature(initial), 'Initial saved snapshot differs')
    initial_probe = probes[resolve(args.run/'probes/initial_phase1.json')]
    require(initial_probe['candidate_signature'] == signature(initial) and initial_probe['usable'], 'Initial probe not usable/bound')
    check_local(summary['initial_native_pair_ac'], initial)
    require(summary['initial_native_pair_ac']['passed'], 'Initial state did not pass native pair gate')
    current_objective = initial_probe['objective']
    best_objective = current_objective
    best_signatures = {signature(initial)}
    accepted = 0
    seen = {signature(initial)}
    all_proposal_graphs = 0
    intermediate_graphs = 0
    final_net_removed_counts = Counter()
    trace_trial_lookups = 0
    checked_gpu_baselines = 0
    checked_gpu_selected = 0
    proposal_files_seen = set()
    for number, record in enumerate(summary['records']):
        require(record['iteration'] == number, 'Iteration sequence mismatch')
        require(type(record['accepted']) is bool, 'Acceptance flag must be boolean')
        previous = check_probe(record['previous_probe'], current)
        require(previous['usable'] and previous['objective'] == current_objective, 'Wrong current LP probe')
        proposal_path = resolve(record['proposal_path'])
        proposal_files_seen.add(proposal_path)
        require(digest(proposal_path) == record['proposal_sha256'], 'Proposal checksum mismatch')
        proposal = load(proposal_path)
        require(proposal['seed'] == record['native_sample_seed'] and proposal['sample_limit'] == manifest['neighbors'],
                'Proposal seed/budget differs')
        options, paths = proposal['overlap_candidates'], proposal['trade_paths']
        require(proposal['status'] == 'BOUNDED_TWO_TRADE_PROPOSALS', 'Wrong native proposal status')
        require(len(options) == len(paths) == proposal['returned_candidates'] <= manifest['neighbors'], 'Proposal counts differ')
        require(len({signature(edges) for edges in options}) == len(options), 'Duplicate proposed candidates')
        for edges, path in zip(options, paths):
            require(type(path) is list and len(path) == 2, 'Proposal does not contain exactly two atomic trades')
            middle = trade(current, path[0]['removed'], path[0]['added'])
            full_graph({'overlap_edges_outer_zero_based': [list(edge) for edge in sorted(middle)]})
            intermediate_graphs += 1
            final = trade(middle, path[1]['removed'], path[1]['added'])
            require(signature(final) == signature(edges), 'Proposed final graph differs from two-trade path')
            net_removed = len(current-final)
            require(net_removed >= 3, 'Two-trade final removes fewer than three original edges')
            final_net_removed_counts[net_removed] += 1
            full_graph({'overlap_edges_outer_zero_based': edges})
            all_proposal_graphs += 1
        score_path = resolve(record['gpu_scores_path'])
        require(digest(score_path) == record['gpu_scores_sha256'], 'GPU score checksum mismatch')
        scores = load(score_path)
        require(scores['status'] == 'NUMERICAL_FIXED_X_PHASE1_HEURISTIC' and len(scores['results']) == len(options)+1,
                'GPU score dimensions/status')
        require([row['candidate_index'] for row in scores['results']] == list(range(len(options)+1)), 'GPU candidate order')
        require(abs(scores['results'][0]['total_violation']-current_objective) <= 1e-7*(1+abs(current_objective)), 'GPU current merit differs')
        checked_gpu_baselines += 1
        selected = record['selected_proposal_indices']
        require(len(selected) == len(set(selected)) == len(record['phase1_trials'])
                and all(type(i) is int and 0 <= i < len(options) for i in selected), 'Selected LP indices malformed')
        order = sorted((scores['results'][i+1]['total_violation'], i) for i, edges in enumerate(options)
                       if signature(edges) not in seen)
        required_best = [i for _, i in order[:manifest['lp_best']]]
        require(selected[:len(required_best)] == required_best, 'GPU-priority LP prefix differs')
        require(len(selected) == min(len(order), manifest['lp_best']+manifest['lp_random']), 'LP probe selection budget differs')
        trial_infos = []
        for index, trial_record in zip(selected, record['phase1_trials']):
            info = check_probe(trial_record, options[index])
            require(signature(options[index]) not in seen, 'Selected an already visited K')
            trial_infos.append(info)
            # Frozen-X scoring uses previous X, while this trial's LP uses its own optimized X.
            frozen = evaluate({'overlap_edges_outer_zero_based': options[index]}, previous['x'])
            native = scores['results'][index+1]
            for component in ('total_violation', 'quota_violation', 'pair_violation'):
                require(abs(native[component]-frozen[component]) <= 1e-7*(1+abs(frozen[component])), 'Selected GPU merit differs from full99')
            checked_gpu_selected += 1
        trace_trial_lookups += len(trial_infos)
        require(record['chosen_index'] in selected, 'Chosen index was not LP probed')
        chosen_position = selected.index(record['chosen_index'])
        chosen = check_probe(record['chosen_probe'], options[record['chosen_index']])
        require(record['chosen_probe'] == record['phase1_trials'][chosen_position], 'Chosen/cache probe record differs')
        require(chosen['usable'], 'Chosen LP is unusable')
        local_checks = record['native_local_checks']
        require(type(record['chosen_passes_native_pair_ac']) is bool, 'Native compatibility flag is not boolean')
        eligible = {index: info['objective'] for index, info in zip(selected, trial_infos)
                    if info['usable'] and info['objective'] <= current_objective+0.5}
        local_passed = False
        for check_number, checked in enumerate(local_checks):
            index = checked['proposal_index']
            require(index in eligible and eligible[index] == min(eligible.values()),
                    'Native gate did not follow actual-objective priority')
            del eligible[index]
            check_local(checked, options[index])
            if checked['passed']:
                require(check_number == len(local_checks)-1 and record['chosen_index'] == index,
                        'Native gate did not stop at first passing candidate')
                local_passed = True
        require(local_passed is record['chosen_passes_native_pair_ac'], 'Chosen native gate pass flag differs')
        if not local_passed:
            require(not eligible and chosen['objective'] == min(info['objective'] for info in trial_infos if info['usable']),
                    'Failed local gate omitted eligible candidates or wrong fallback choice')
        require(record['trade_path'] == paths[record['chosen_index']], 'Chosen two-trade path differs')
        delta = chosen['objective']-current_objective
        require(record['accepted'] or not local_passed or delta > 1e-7, 'Compatible improving trial was unexpectedly rejected')
        require(not record['accepted'] or (local_passed and delta <= 0.5), 'Accepted trial lacks local gate or exceeds escape cap')
        if record['accepted']:
            for move in record['trade_path']:
                current = trade(current, move['removed'], move['added'])
            current_objective = chosen['objective']
            accepted += 1
            require(accepted < len(snapshots) and signature(snapshots[accepted]) == signature(current), 'Accepted snapshot differs')
            require(signature(current) not in seen, 'Repeated accepted K')
            seen.add(signature(current))
            if current_objective < best_objective:
                best_objective, best_signatures = current_objective, {signature(current)}
            elif current_objective == best_objective:
                best_signatures.add(signature(current))
    require(accepted == summary['accepted_moves'] == len(snapshots)-1, 'Accepted snapshot count differs')
    require(summary['accepted_atomic_trades'] == 2*accepted, 'Accepted atomic-trade count differs')
    require(len(local_reports) == summary['local_candidates_checked'], 'Native gate cache count differs')
    require(best['numeric_phase1_objective'] == summary['best_numeric_objective'] == best_objective
            and signature(best['overlap_edges_outer_zero_based']) in best_signatures, 'Best accepted state/objective differs')
    best_probe = check_probe(best['phase1_probe'], best['overlap_edges_outer_zero_based'])
    require(best_probe['usable'] and best_probe['objective'] == best_objective, 'Best probe unusable')
    require(copied_best == load(best['phase1_probe']['result_path']), 'Best LP copy differs from bound original probe')
    terminal = []
    for path in sorted((args.run/'proposals').glob('iteration_*.json')):
        if not re.fullmatch(r'iteration_\d+\.json', path.name) or resolve(path) in proposal_files_seen:
            continue
        proposal = load(path)
        require(int(path.stem.split('_')[1]) == len(summary['records']), 'Unexpected unrecorded proposal iteration')
        require(proposal['status'] == 'BOUNDED_TWO_TRADE_PROPOSALS' and
                len(proposal['overlap_candidates']) == len(proposal['trade_paths']), 'Terminal proposal count/status mismatch')
        require(len({signature(edges) for edges in proposal['overlap_candidates']}) == len(proposal['overlap_candidates']),
                'Duplicate terminal proposal finals')
        for edges, path in zip(proposal['overlap_candidates'], proposal['trade_paths']):
            require(type(path) is list and len(path) == 2, 'Terminal proposal atomic-trade count')
            middle = trade(current, path[0]['removed'], path[0]['added'])
            full_graph({'overlap_edges_outer_zero_based': [list(edge) for edge in sorted(middle)]})
            intermediate_graphs += 1
            final = trade(middle, path[1]['removed'], path[1]['added'])
            require(signature(final) == signature(edges), 'Terminal proposed graph/trade mismatch')
            net_removed = len(current-final)
            require(net_removed >= 3, 'Terminal final removes fewer than three original edges')
            final_net_removed_counts[net_removed] += 1
            full_graph({'overlap_edges_outer_zero_based': edges})
            all_proposal_graphs += 1
        terminal.append(path.name)
    require(all_proposal_graphs == summary['proposal_evaluations'], 'Proposal evaluation count differs')
    require(len(summary['records']) <= manifest['iterations'], 'Exceeded iteration budget')
    require(summary['stop_reason'] in ('ITERATION_LIMIT', 'NUMERICAL_ZERO_DEFECT_REQUIRES_EXACT_VALIDATION',
            'NO_SAMPLED_TWO_TRADE_PATHS', 'SAMPLED_NEIGHBORS_ALREADY_VISITED', 'ALL_SELECTED_PHASE1_PROBES_INCOMPLETE'), 'Unknown stop reason')
    if summary['stop_reason'] == 'ITERATION_LIMIT':
        require(len(summary['records']) == manifest['iterations'], 'Iteration-limit status ended early')
    if summary['stop_reason'] == 'NUMERICAL_ZERO_DEFECT_REQUIRES_EXACT_VALIDATION':
        require(best_objective <= 1e-8, 'False numerical-zero stop')
    if not terminal:
        require(1+trace_trial_lookups-len(probes) == summary['cached_phase1_lookups'], 'Cache lookup count mismatch')
    for source in (Path(__file__), ROOT/'acceleration/audit_phase1.py', ROOT/'acceleration/audit_certificate.py',
                   ROOT/'acceleration/audit_phase1_kkt.py'):
        digest(source)
    result = {'status': 'INDEPENDENT_TWO_TRADE_TRACE_INTERMEDIATE_GRAPHS_NUMERIC_OBJECTIVES_AND_NATIVE_GATE_BINDINGS_AUDIT_PASS',
              'iterations_replayed': len(summary['records']), 'accepted_moves_replayed': accepted,
              'accepted_atomic_trades_replayed': 2*accepted,
              'distinct_accepted_states_including_initial': len(seen), 'proposal_graphs_and_trades_checked': all_proposal_graphs,
              'proposal_intermediate_full99_graphs_checked': intermediate_graphs,
              'atomic_trades_replayed_across_all_proposals': 2*all_proposal_graphs,
              'final_net_removed_original_edge_counts': dict(final_net_removed_counts),
              'actual_lp_probe_artifacts_checked': len(probes), 'numerically_unusable_probe_artifacts': numeric_unknown,
              'all_actual_probe_models_compared_to_full99_semantics': True,
              'usable_probe_rational_primal_dual_intervals_checked': len(probes)-numeric_unknown,
              'actual_probe_exact_positive_dual_lower_bounds': exact_positive_bounds,
              'maximum_exact_primal_dual_gap': maximum_primal_dual_gap,
              'max_actual_objective_absolute_difference': max_error,
              'gpu_baseline_scores_checked': checked_gpu_baselines, 'gpu_selected_frozen_x_scores_checked': checked_gpu_selected,
              'initial_numeric_objective': initial_probe['objective'], 'best_numeric_objective': best_objective,
              'terminal_unrecorded_proposals_checked': terminal, 'probe_records': probe_reports,
              'native_local_candidates_input_export_hash_and_status_checked': len(local_reports),
              'native_local_status_counts': dict(local_status_counts),
              'native_domain_completeness_or_pair_support_independently_replayed': False,
              'cache_hits_reported': summary['cached_phase1_lookups'], 'inputs_sha256': hashes,
              'random_selection_replayed': False, 'exact_optimality_certified': False,
              'positive_exact_dual_bound_certifies_only_its_own_candidate': True,
              'solver_or_search_producer_imported': False, 'elapsed_seconds': time.perf_counter()-started,
              'scope': 'Every sampled proposal two-trade path is independently replayed, with both intermediate and final full99 partial graphs checked. Final states are distinct within each batch and remove at least three original edges. Every actual LP candidate/model/numerical merit is checked. Every usable LP gets exact rational primal/dual bounds; a strictly positive lower bound excludes only its fixed candidate. Accepted-state/cache/best provenance is replayed. Native endpoint local gates are checked for input, export, hash, cap and status consistency only, without independent enumeration or pair-support replay. Intermediate pair AC is not required or claimed. Caps are skips, not exclusions. This is not exhaustive two-trade enumeration, exact optimum, zero-defect exact feasibility, a completed graph, all sampled-neighbor exclusion, or global coverage.'}
    with args.out.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('probe_records', 'inputs_sha256')}))


if __name__ == '__main__':
    main()
