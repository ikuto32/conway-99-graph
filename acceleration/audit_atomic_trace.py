"""Independent atomic alternating-cycle search, model and native-gate audit.

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
import random
import time

from audit_certificate import full_graph, require
from audit_phase1 import evaluate, graph_rows, compare_rows
from audit_phase1_kkt import inspect_artifact
from audit_atomic_cycle_family import audit as audit_family

ROOT = Path(__file__).resolve().parents[1]


def resolve(name):
    path = Path(str(name).replace('\\', '/'))
    return path.resolve() if path.is_absolute() else (ROOT/path).resolve()


def signature(edges):
    return tuple(sorted(map(tuple, edges)))


def atomic_move(known, move, adjacency):
    """Check one connected alternating cycle without imposing intermediate states."""
    size, group, matching = move['cycle_size'], move['root_group'], move['matching_class']
    require(type(size) is int and size in (3, 4), 'Atomic cycle size')
    require(type(group) is int and 0 <= group < 7, 'Atomic root group')
    require(matching in ('same_0', 'same_1', 'cross'), 'Atomic matching class')
    removed, added = move['removed'], move['added']
    require(type(removed) is list and type(added) is list and len(removed) == len(added) == size, 'Atomic edge count')
    for edge in removed+added:
        require(type(edge) is list and len(edge) == 2 and all(type(v) is int for v in edge)
                and 0 <= edge[0] < edge[1] < 84, 'Invalid canonical atomic edge')
    require(removed == sorted(removed) and added == sorted(added), 'Atomic edge lists are not canonical sorted')
    old, new = set(map(tuple, removed)), set(map(tuple, added))
    require(len(old) == len(new) == size and old <= known and not new & known, 'Atomic absent/present mismatch')
    endpoints = Counter(v for edge in old for v in edge)
    require(len(endpoints) == 2*size and set(endpoints.values()) == {1}
            and endpoints == Counter(v for edge in new for v in edge), 'Atomic matching endpoint/degree balance')
    signs = {}
    for u in endpoints:
        signs_here = [s for s in range(2) if 2*group+s+1 in adjacency[u+15]]
        require(len(signs_here) == 1, 'Atomic endpoint does not belong to declared root group')
        signs[u] = signs_here[0]
    for u, v in old | new:
        require((signs[u] != signs[v]) if matching == 'cross' else
                (signs[u] == signs[v] == int(matching[-1])), 'Atomic edge outside declared matching class')
    cycle = move['alternating_cycle']
    require(type(cycle) is list and len(cycle) == 2*size and all(type(v) is int for v in cycle)
            and len(set(cycle)) == 2*size and set(cycle) == set(endpoints), 'Atomic alternating-cycle vertices')
    cycle_old = {tuple(sorted((cycle[i], cycle[i+1]))) for i in range(0, 2*size, 2)}
    cycle_new = {tuple(sorted((cycle[i], cycle[(i+1) % (2*size)]))) for i in range(1, 2*size, 2)}
    require(cycle_old == old and cycle_new == new, 'Atomic edges are not the declared connected alternating cycle')
    final = (known-old)|new
    require(len(known-final) == len(final-known) == size, 'Atomic net edge difference')
    return final


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
    require(summary['status'] == 'BOUNDED_ATOMIC_CYCLE_COUPLED_SEARCH_FINISHED', 'Search is not finished')
    require(summary['manifest'] == manifest, 'External and embedded manifest differ')
    require(manifest['cycle_size'] in ('3', '4', 'both'), 'Unknown atomic-cycle subfamily')
    allowed_sizes = (3, 4) if manifest['cycle_size'] == 'both' else (int(manifest['cycle_size']),)
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
    trace_trial_lookups = 0
    checked_gpu_baselines = 0
    checked_gpu_selected = 0
    proposal_files_seen = set()
    proposal_cache = {}
    lp_cache = {signature(initial): resolve(args.run/'probes/initial_phase1.json')}
    seen_probe_paths = set(lp_cache.values())
    proposal_occurrences = 0
    reused_batches = 0
    atomic_size_counts = Counter()
    family_reports = []
    accepted_edge_replacements = 0
    generator = random.Random(manifest['seed'])
    for number, record in enumerate(summary['records']):
        require(record['iteration'] == number, 'Iteration sequence mismatch')
        require(type(record['accepted']) is bool, 'Acceptance flag must be boolean')
        previous = check_probe(record['previous_probe'], current)
        require(previous['usable'] and previous['objective'] == current_objective, 'Wrong current LP probe')
        current_key = signature(current)
        require(lp_cache.get(current_key) == resolve(record['previous_probe']['result_path']), 'Current LP differs from chronological cache')
        current_adjacency, _ = full_graph({'overlap_edges_outer_zero_based': [list(edge) for edge in sorted(current)]})
        proposal_path = resolve(record['proposal_path'])
        proposal_files_seen.add(proposal_path)
        require(digest(proposal_path) == record['proposal_sha256'], 'Proposal checksum mismatch')
        proposal = load(proposal_path)
        options, moves = proposal['overlap_candidates'], proposal['moves']
        require(proposal['status'] == 'COMPLETE_ATOMIC_CYCLE_SUBFAMILY_ENUMERATION' and len(options) == len(moves),
                'Atomic proposal status/count differs')
        require(proposal['cycle_size'] == manifest['cycle_size'], 'Native atomic-cycle mode differs from manifest')
        require(len({signature(edges) for edges in options}) == len(options), 'Duplicate proposed candidates')
        score_path = resolve(record['gpu_scores_path'])
        require(type(record['proposal_batch_reused']) is bool and record['proposal_batch_reused'] is (current_key in proposal_cache),
                'Proposal reuse flag differs from chronological state cache')
        batch_binding = (proposal_path, score_path, resolve(record['previous_probe']['result_path']))
        if record['proposal_batch_reused']:
            require(proposal_cache[current_key] == batch_binding, 'Reused batch bound to wrong K or X probe')
            reused_batches += 1
        else:
            require(proposal_path.name == f'iteration_{number:04d}.json', 'Fresh batch filename chronology differs')
            proposal_cache[current_key] = batch_binding
            family_reports.append({'proposal_path': proposal_path.relative_to(ROOT).as_posix(),
                                   'current_phase1_probe': record['previous_probe']['result_path'],
                                   'independent_complete_family_audit': audit_family(
                                       {'overlap_edges_outer_zero_based': [list(edge) for edge in sorted(current)]}, proposal)})
            for edges, move in zip(options, moves):
                require(move['cycle_size'] in allowed_sizes, 'Atomic move outside selected subfamily')
                require(signature(atomic_move(current, move, current_adjacency)) == signature(edges),
                        'Proposed graph differs from atomic alternating-cycle move')
                full_graph({'overlap_edges_outer_zero_based': edges})
                all_proposal_graphs += 1
                atomic_size_counts[move['cycle_size']] += 1
        proposal_occurrences += len(options)
        require(digest(score_path) == record['gpu_scores_sha256'], 'GPU score checksum mismatch')
        scores = load(score_path)
        require(scores['status'] == 'NUMERICAL_FIXED_X_PHASE1_HEURISTIC' and len(scores['results']) == len(options)+1,
                'GPU score dimensions/status')
        require([row['candidate_index'] for row in scores['results']] == list(range(len(options)+1)), 'GPU candidate order')
        require(all(type(row['total_violation']) in (int, float) and isfinite(row['total_violation'])
                    and row['total_violation'] >= 0 for row in scores['results']), 'GPU merit is invalid')
        require(abs(scores['results'][0]['total_violation']-current_objective) <= 1e-7*(1+abs(current_objective)), 'GPU current merit differs')
        checked_gpu_baselines += 1
        selected = record['selected_proposal_indices']
        require(len(selected) == len(set(selected)) == len(record['phase1_trials'])
                and all(type(i) is int and 0 <= i < len(options) for i in selected), 'Selected LP indices malformed')
        eligible_indices = [i for i, edges in enumerate(options) if signature(edges) not in seen]
        order = sorted((scores['results'][i+1]['total_violation'], i) for i in eligible_indices
                       if signature(options[i]) not in lp_cache)
        expected_fresh = [i for _, i in order[:manifest['lp_best']]]
        bucket = lambda i: (moves[i]['root_group'], moves[i]['matching_class'], moves[i]['cycle_size'])
        represented = {bucket(i) for i in expected_fresh}
        best_per_bucket = {}
        for _, index in order:
            key = bucket(index)
            if key not in represented:
                best_per_bucket.setdefault(key, index)
        bucket_keys = sorted(best_per_bucket)
        generator.shuffle(bucket_keys)
        expected_fresh += [best_per_bucket[key] for key in bucket_keys[:manifest['lp_diverse']]]
        remaining = [i for _, i in order if i not in expected_fresh]
        expected_fresh += generator.sample(remaining, min(manifest['lp_random'], len(remaining)))
        cached_eligible = []
        for index in eligible_indices:
            key = signature(options[index])
            if key not in lp_cache:
                continue
            saved = probes[lp_cache[key]]
            local = local_reports.get(key)
            if saved['objective'] <= current_objective+0.5 and (local is None or local['passed']):
                cached_eligible.append((saved['objective'], index))
        expected_cached = [index for _, index in sorted(cached_eligible)[:manifest['cached_best']]]
        require(record['fresh_selected_proposal_indices'] == expected_fresh and
                record['cached_selected_proposal_indices'] == expected_cached and
                selected == expected_fresh+expected_cached, 'Fresh/diverse/random/cached LP selection differs')
        trial_infos = []
        for index, trial_record in zip(selected, record['phase1_trials']):
            info = check_probe(trial_record, options[index])
            require(signature(options[index]) not in seen, 'Selected an already visited K')
            key = signature(options[index])
            result_path = resolve(trial_record['result_path'])
            if index in expected_cached:
                require(lp_cache[key] == result_path and result_path in seen_probe_paths, 'Cached LP references an unevaluated or different result')
            else:
                require(key not in lp_cache and result_path not in seen_probe_paths and
                        result_path == resolve(args.run/'probes'/f'iteration_{number:04d}_choice_{index:04d}_phase1.json'),
                        'Fresh LP is cached or has wrong evaluation chronology')
                seen_probe_paths.add(result_path)
                if info['usable']:
                    lp_cache[key] = result_path
            trial_infos.append(info)
            # Frozen-X scoring uses previous X, while this trial's LP uses its own optimized X.
            frozen = evaluate({'overlap_edges_outer_zero_based': options[index]}, previous['x'])
            native = scores['results'][index+1]
            for component in ('total_violation', 'quota_violation', 'pair_violation'):
                require(abs(native[component]-frozen[component]) <= 1e-7*(1+abs(frozen[component])), 'Selected GPU merit differs from full99')
            checked_gpu_selected += 1
        trace_trial_lookups += len(trial_infos)
        randomized_usable = [(info['objective'], generator.random(), index)
                             for index, info in zip(selected, trial_infos) if info['usable']]
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
        expected_check_order = [index for value, _, index in sorted(randomized_usable) if value <= current_objective+0.5]
        for check_number, checked in enumerate(local_checks):
            index = checked['proposal_index']
            require(check_number < len(expected_check_order) and index == expected_check_order[check_number],
                    'Native gate order differs from objective/tie-break replay')
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
            require(record['chosen_index'] == min(randomized_usable)[2], 'Fallback choice differs from tie-break replay')
        require(record['move'] == moves[record['chosen_index']], 'Chosen atomic cycle differs')
        delta = chosen['objective']-current_objective
        replay_accepted = local_passed and (delta <= 1e-7 or (delta <= 0.5 and generator.random() < 0.1))
        require(record['accepted'] is replay_accepted, 'Acceptance differs from declared numerical/escape policy')
        require(record['accepted'] or not local_passed or delta > 1e-7, 'Compatible improving trial was unexpectedly rejected')
        require(not record['accepted'] or (local_passed and delta <= 0.5), 'Accepted trial lacks local gate or exceeds escape cap')
        if record['accepted']:
            current = atomic_move(current, record['move'], current_adjacency)
            accepted_edge_replacements += record['move']['cycle_size']
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
    require(accepted_edge_replacements == summary['accepted_edge_replacements'], 'Accepted edge-replacement total differs')
    require(len(local_reports) == summary['local_candidates_checked'], 'Native gate cache count differs')
    require(best['numeric_phase1_objective'] == summary['best_numeric_objective'] == best_objective
            and signature(best['overlap_edges_outer_zero_based']) in best_signatures, 'Best accepted state/objective differs')
    best_probe = check_probe(best['phase1_probe'], best['overlap_edges_outer_zero_based'])
    require(best_probe['usable'] and best_probe['objective'] == best_objective, 'Best probe unusable')
    require(copied_best == load(best['phase1_probe']['result_path']), 'Best LP copy differs from bound original probe')
    terminal = []
    terminal_proposal = None
    for path in sorted((args.run/'proposals').glob('iteration_*.json')):
        if not re.fullmatch(r'iteration_\d+\.json', path.name) or resolve(path) in proposal_files_seen:
            continue
        proposal = load(path)
        require(int(path.stem.split('_')[1]) == len(summary['records']), 'Unexpected unrecorded proposal iteration')
        require(proposal['status'] == 'COMPLETE_ATOMIC_CYCLE_SUBFAMILY_ENUMERATION' and
                len(proposal['overlap_candidates']) == len(proposal['moves']), 'Terminal proposal count/status mismatch')
        require(proposal['cycle_size'] == manifest['cycle_size'], 'Terminal native cycle mode differs')
        require(len({signature(edges) for edges in proposal['overlap_candidates']}) == len(proposal['overlap_candidates']),
                'Duplicate terminal atomic finals')
        current_adjacency, _ = full_graph({'overlap_edges_outer_zero_based': [list(edge) for edge in sorted(current)]})
        family_reports.append({'proposal_path': path.resolve().relative_to(ROOT).as_posix(),
                               'current_phase1_probe': str(lp_cache[signature(current)]),
                               'independent_complete_family_audit': audit_family(
                                   {'overlap_edges_outer_zero_based': [list(edge) for edge in sorted(current)]}, proposal)})
        for edges, move in zip(proposal['overlap_candidates'], proposal['moves']):
            require(move['cycle_size'] in allowed_sizes and
                    signature(atomic_move(current, move, current_adjacency)) == signature(edges), 'Terminal proposed atomic cycle mismatch')
            full_graph({'overlap_edges_outer_zero_based': edges})
            all_proposal_graphs += 1
            atomic_size_counts[move['cycle_size']] += 1
        terminal.append(path.name)
        terminal_proposal = proposal
    require(all_proposal_graphs == summary['proposal_evaluations'], 'Proposal evaluation count differs')
    require(len(summary['records']) <= manifest['iterations'], 'Exceeded iteration budget')
    require(summary['stop_reason'] in ('ITERATION_LIMIT', 'NUMERICAL_ZERO_DEFECT_REQUIRES_EXACT_VALIDATION',
            'NO_LEGAL_ATOMIC_CYCLES_IN_SELECTED_SUBFAMILY', 'NO_UNPROBED_OR_ELIGIBLE_CACHED_CYCLE_CANDIDATES',
            'ALL_SELECTED_PHASE1_PROBES_INCOMPLETE'), 'Unknown stop reason')
    terminal_break = summary['stop_reason'] in ('NO_LEGAL_ATOMIC_CYCLES_IN_SELECTED_SUBFAMILY',
                'NO_UNPROBED_OR_ELIGIBLE_CACHED_CYCLE_CANDIDATES', 'ALL_SELECTED_PHASE1_PROBES_INCOMPLETE')
    if terminal_break:
        require(len(summary['records']) < manifest['iterations'], 'Terminal break exceeds iteration budget')
        if terminal_proposal is None:
            require(signature(current) in proposal_cache, 'Missing terminal atomic proposal batch')
            terminal_proposal = load(proposal_cache[signature(current)][0])
            reused_batches += 1
        proposal_occurrences += len(terminal_proposal['overlap_candidates'])
        if summary['stop_reason'] == 'NO_LEGAL_ATOMIC_CYCLES_IN_SELECTED_SUBFAMILY':
            require(not terminal_proposal['overlap_candidates'], 'Nonempty batch mislabeled no legal subfamily cycles')
        elif summary['stop_reason'] == 'NO_UNPROBED_OR_ELIGIBLE_CACHED_CYCLE_CANDIDATES':
            for edges in terminal_proposal['overlap_candidates']:
                key = signature(edges)
                if key in seen:
                    continue
                require(key in lp_cache, 'Unprobed terminal candidate remains')
                require(manifest['cached_best'] == 0 or probes[lp_cache[key]]['objective'] > current_objective+0.5
                        or (key in local_reports and not local_reports[key]['passed']), 'Eligible cached terminal candidate remains')
        else:
            orphan_probes = set(probes)-seen_probe_paths
            require(orphan_probes and all(not probes[path]['usable'] for path in orphan_probes),
                    'All-incomplete terminal break lacks incomplete new probes')
            terminal_keys = {signature(edges) for edges in terminal_proposal['overlap_candidates']}
            for path in orphan_probes:
                require(path.name.startswith(f'iteration_{len(summary["records"]):04d}_choice_') and
                        probes[path]['candidate_signature'] in terminal_keys and
                        probes[path]['candidate_signature'] not in seen, 'Orphan terminal LP is not a current proposal')
    else:
        require(not terminal, 'Unexpected terminal batch for final stop status')
    require(proposal_occurrences == summary['proposal_occurrences'] and reused_batches == summary['cached_proposal_batches'],
            'Proposal occurrence/reuse totals differ')
    if summary['stop_reason'] == 'ITERATION_LIMIT':
        require(len(summary['records']) == manifest['iterations'], 'Iteration-limit status ended early')
    if summary['stop_reason'] == 'NUMERICAL_ZERO_DEFECT_REQUIRES_EXACT_VALIDATION':
        require(best_objective <= 1e-8, 'False numerical-zero stop')
    if not terminal_break:
        require(seen_probe_paths == set(probes), 'Unreferenced actual LP artifacts')
        require(1+trace_trial_lookups-len(probes) == summary['cached_phase1_lookups'], 'Cache lookup count mismatch')
    for source in (Path(__file__), ROOT/'acceleration/audit_phase1.py', ROOT/'acceleration/audit_certificate.py',
                   ROOT/'acceleration/audit_phase1_kkt.py', ROOT/'acceleration/audit_atomic_cycle_family.py'):
        digest(source)
    result = {'status': 'INDEPENDENT_ATOMIC_CYCLE_TRACE_GRAPH_MODELS_MERITS_SELECTION_AND_NATIVE_GATE_BINDINGS_AUDIT_PASS',
              'iterations_replayed': len(summary['records']), 'accepted_moves_replayed': accepted,
              'accepted_edge_replacements_checked': accepted_edge_replacements,
              'distinct_accepted_states_including_initial': len(seen), 'proposal_graphs_and_trades_checked': all_proposal_graphs,
              'atomic_cycle_size_counts': dict(atomic_size_counts),
              'distinct_batches_independently_reenumerated': len(family_reports),
              'complete_family_reports': family_reports,
              'proposal_occurrences_checked': proposal_occurrences,
              'cached_proposal_batches_checked': reused_batches,
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
              'random_selection_and_escape_draws_replayed': True, 'exact_optimality_certified': False,
              'terminal_unrecorded_selection_fully_replayed': not terminal_break,
              'native_complete_subfamily_enumeration_independently_repeated': True,
              'positive_exact_dual_bound_certifies_only_its_own_candidate': True,
              'solver_or_search_producer_imported': False, 'elapsed_seconds': time.perf_counter()-started,
              'scope': 'Every distinct saved atomic proposal is independently checked: equal endpoint sets, degree-one removed/added matchings, declared root/sign class, one connected alternating cycle, exact net edge changes and final full99 partial graph caps. Each distinct native proposal family is completely reenumerated by independent endpoint matching/bijection and exact set equality, only within its stated single-matching single-cycle subfamily. No intermediate swap state is required. LP models/merits and rational primal/dual bounds are checked; a positive lower bound excludes only its fixed candidate. Recorded fresh/diverse/random/cached selection, acceptance and batch/LP cache chronology are replayed. Native endpoint local gates are checked for input, export, hash, cap and status consistency only. Caps are heuristic skips, never exclusions. No exhaustive LP shortlist, exact optimum, full graph or global coverage is claimed.'}
    with args.out.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('probe_records', 'inputs_sha256', 'complete_family_reports')}))


if __name__ == '__main__':
    main()
