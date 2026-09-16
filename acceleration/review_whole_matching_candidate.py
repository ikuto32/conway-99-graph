"""Independent geometry and returned-X checks for a whole-matching MIP candidate.

The MIP producer and optimization solver are never imported. Numeric MIP status
does not establish a graph, infeasibility, or global optimality.
"""
from collections import Counter
import argparse
from hashlib import sha256
import json
from math import isfinite
from pathlib import Path
import time

from audit_certificate import full_graph, require
from audit_phase1 import evaluate, graph_rows


def geometry(initial, candidate, root_group, matching_class, y_edges, y_values, tolerance=1e-6):
    require(type(root_group) is int and 0 <= root_group < 7, 'Invalid selected root group')
    require(matching_class in ('same_0', 'same_1', 'cross'), 'Invalid selected matching class')
    initial_rows, initial_unknown = full_graph(initial)
    candidate_rows, candidate_unknown = full_graph(candidate)
    original = set(map(tuple, initial['overlap_edges_outer_zero_based']))
    final = set(map(tuple, candidate['overlap_edges_outer_zero_based']))
    labels = [{(s-1)//2: (s-1) % 2 for s in row if 1 <= s <= 14} for row in initial_rows[15:]]
    cohort = [u for u in range(84) if root_group in labels[u] and
              (matching_class == 'cross' or labels[u][root_group] == int(matching_class[-1]))]
    expected_count = 12 if matching_class == 'cross' else 6
    require(len(cohort) == 2*expected_count, 'Unexpected selected matching vertex count')
    allowed = set()
    for u in cohort:
        for v in cohort:
            if u >= v or len(set(labels[u]) & set(labels[v])) != 1:
                continue
            if matching_class == 'cross' and labels[u][root_group] == labels[v][root_group]:
                continue
            allowed.add((u, v))
    old_matching, new_matching = original & allowed, final & allowed
    for matching in (old_matching, new_matching):
        counts = Counter(u for edge in matching for u in edge)
        require(len(matching) == expected_count and set(counts) == set(cohort) and set(counts.values()) == {1},
                'Selected matching is not exactly perfect on its fixed cohort')
    require(original-allowed == final-allowed, 'Candidate changes an edge outside the selected matching')
    require(initial_unknown == candidate_unknown, 'Candidate changes the disjoint-variable universe')
    require(type(y_edges) is list and type(y_values) is list and len(y_edges) == len(y_values), 'Y vector shape')
    require(all(type(edge) is list and len(edge) == 2 and all(type(v) is int for v in edge)
                and tuple(edge) in allowed for edge in y_edges), 'Y variable is outside selected matching domain')
    require(len({tuple(edge) for edge in y_edges}) == len(y_edges), 'Duplicate Y variable coordinate')
    require(all(type(value) in (int, float) and isfinite(value) for value in y_values), 'Nonfinite Y value')
    integrality_error = max((min(abs(value), abs(value-1)) for value in y_values), default=0)
    require(integrality_error <= tolerance, 'Returned Y is not numerically integral')
    selected_y = {tuple(edge) for edge, value in zip(y_edges, y_values) if value > 0.5}
    require(selected_y == new_matching, 'Extracted candidate matching differs from returned Y')
    return {'status': 'INDEPENDENT_FIXED_MATCHING_CANDIDATE_GEOMETRY_PASS',
            'root_group': root_group, 'matching_class': matching_class,
            'matching_vertices': len(cohort), 'matching_edges': expected_count,
            'geometrically_allowed_matching_edges': len(allowed), 'reported_y_variables': len(y_edges),
            'y_covers_all_geometrically_allowed_edges': set(map(tuple, y_edges)) == allowed,
            'checked_y_integrality_max_error': integrality_error, 'checked_y_integrality_tolerance': tolerance,
            'extracted_matching_exact_binary': True,
            'initial_matching_edges': [list(edge) for edge in sorted(old_matching)],
            'selected_matching_edges': [list(edge) for edge in sorted(new_matching)],
            'changed_removed_edges': [list(edge) for edge in sorted(original-final)],
            'changed_added_edges': [list(edge) for edge in sorted(final-original)],
            'changed_only_selected_matching': True,
            'candidate_full99_partial_pair_caps_checked': 4851,
            'unchanged_exact_labeled_graph': initial_rows == candidate_rows,
            'unchanged_disjoint_variable_universe': True}


def returned_merit(candidate, x_columns, x_values, objective, tolerance=1e-6):
    columns, _, _ = graph_rows(candidate)
    require(x_columns == [list(edge) for edge in columns], 'Returned X column ordering differs from full99 model')
    require(type(objective) in (int, float) and isfinite(objective), 'Invalid incumbent objective')
    values = evaluate(candidate, x_values)
    difference = abs(values['total_violation']-objective)
    require(difference <= tolerance*max(1, abs(objective)), 'MIP incumbent objective differs from recomputed phase-I merit')
    return {'status': 'INDEPENDENT_RETURNED_X_PHASE1_MERIT_PASS',
            'quota_violation': values['quota_violation'], 'pair_violation': values['pair_violation'],
            'total_violation': values['total_violation'], 'declared_mip_incumbent_objective': objective,
            'absolute_difference': difference, 'relative_tolerance': tolerance,
            'scope': 'Feasible X and numerical objective agreement only; no MIP optimality or graph-completion claim.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--initial', type=Path, required=True)
    parser.add_argument('--initial-phase1', type=Path)
    parser.add_argument('--result', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), 'Preserve prior independent audit')
    started = time.perf_counter()
    root = Path(__file__).resolve().parents[1]
    hashes = {}

    def resolve(path):
        path = Path(path)
        return path.resolve() if path.is_absolute() else (root/path).resolve()

    def digest(path):
        path = resolve(path)
        value = sha256(path.read_bytes()).hexdigest()
        hashes[path.relative_to(root).as_posix()] = value
        return value

    def load(path):
        digest(path)
        return json.loads(resolve(path).read_bytes())

    def edge_hash(edges):
        canonical = sorted([list(edge) for edge in edges])
        return sha256(json.dumps(canonical, separators=(',', ':')).encode('ascii')).hexdigest()

    result, initial = load(args.result), load(args.initial)
    for section in ('inputs_sha256', 'source_sha256'):
        for name, expected in result[section].items():
            require(digest(name) == expected, 'MIP input/source hash mismatch: '+name)
    require(any(resolve(name) == resolve(args.initial) for name in result['inputs_sha256']), 'Initial candidate not bound')
    require(result['initial_overlap_edges_sha256'] == edge_hash(initial['overlap_edges_outer_zero_based']), 'Initial edge digest mismatch')
    candidate = load(result['candidate_path'])
    require(digest(result['candidate_path']) == result['candidate_sha256'], 'Candidate hash mismatch')
    require(resolve(candidate['source_result']) == resolve(args.result), 'Candidate/result reference mismatch')
    require(candidate['overlap_edges_outer_zero_based'] == result['overlap_edges_outer_zero_based'] ==
            sorted(candidate['overlap_edges_outer_zero_based']), 'Returned candidate edge lists differ or are not canonical')
    require(result['overlap_edges_sha256'] == edge_hash(candidate['overlap_edges_outer_zero_based']), 'Returned edge digest mismatch')
    chosen_y = result['matching_binary_values']
    require(type(chosen_y) is list and all(type(value) is int and value in (0, 1) for value in chosen_y), 'Chosen Y is not exact binary data')
    geometry_report = geometry(initial, candidate, result['root_group'], result['matching_class'],
                               result['matching_variables'], chosen_y, tolerance=0)
    require(result['initial_matching_edges'] == geometry_report['initial_matching_edges'] and
            result['selected_matching_edges'] == geometry_report['selected_matching_edges'], 'Declared matching lists differ')
    require(result['matching_unchanged'] is geometry_report['unchanged_exact_labeled_graph'], 'Unchanged-matching flag differs')
    merit_report = returned_merit(candidate, result['edge_variables'], result['numeric_edge_values'], result['numeric_objective'])
    require(candidate['numeric_phase1_merit'] == result['numeric_objective'], 'Candidate merit metadata differs')
    _, rows, _ = graph_rows(candidate)
    independent = evaluate(candidate, result['numeric_edge_values'])
    coordinates = {'quota': [row['coordinate'] for row in rows if row['equality']],
                   'pair_caps': [row['coordinate'] for row in rows if not row['equality']]}
    require(result['slack_coordinates'] == coordinates, 'MIP residual/slack coordinate ordering differs')
    expected_residuals = {'quota': independent['quota_residuals'], 'pair_caps': independent['pair_residuals']}
    expected_slacks = {'quota_excess': [max(0, value) for value in expected_residuals['quota']],
                       'quota_shortage': [max(0, -value) for value in expected_residuals['quota']],
                       'pair_cap_violation': [max(0, value) for value in expected_residuals['pair_caps']]}
    for declared, truth in ((result['row_residuals'], expected_residuals), (result['numeric_slacks'], expected_slacks)):
        require(set(declared) == set(truth), 'Returned residual/slack fields differ')
        for name, reference in truth.items():
            vector = declared[name]
            require(len(vector) == len(reference) and all(type(a) in (int, float) and isfinite(a) and
                    abs(a-b) <= 1e-7*max(1, abs(b)) for a, b in zip(vector, reference)), 'MIP returned row residual/slack mismatch')
    require(abs(result['residual_breakdown']['quota_absolute_sum']-independent['quota_violation']) <= 1e-6 and
            abs(result['residual_breakdown']['pair_cap_positive_sum']-independent['pair_violation']) <= 1e-6,
            'MIP returned objective breakdown differs')
    initial_x = [0]*1680
    if args.initial_phase1:
        require(any(resolve(name) == resolve(args.initial_phase1) for name in result['inputs_sha256']), 'Initial phase-I X not bound')
        warm = load(args.initial_phase1)
        require(warm['overlap_edges_sha256'] == result['initial_overlap_edges_sha256'], 'Initial X belongs to another K')
        require(warm['edge_variables'] == result['edge_variables'], 'Initial X variable ordering differs')
        initial_x = warm['numeric_edge_values']
    warm_merit = evaluate(initial, initial_x)['total_violation']
    require(abs(warm_merit-result['initial_numeric_objective']) <= 1e-6, 'Initial merit differs')
    require(result['numeric_objective'] <= warm_merit+1e-7, 'Returned point exceeds declared incumbent-retention rule')
    require(result['selected_origin'] in ('INITIAL_INCUMBENT', 'SOLVER_INCUMBENT'), 'Unknown incumbent origin')
    retained = result['selected_origin'] == 'INITIAL_INCUMBENT'
    require(result['retained_initial_incumbent'] is retained, 'Retained-incumbent flag differs')
    require(result['time_limit_reached'] is (result['solver_model_status'] == 'HighsModelStatus.kTimeLimit'), 'Time-limit flag differs')
    require(result['numerical_optimal'] is (result['solver_model_status'] == 'HighsModelStatus.kOptimal' and
            result['solver_run_status'] == 'HighsStatus.kOk' and not retained), 'Numerical-optimal flag inconsistent')
    expected_status = 'NUMERICAL_FIXED_MATCHING_CONTROL' if result['fix_initial'] else 'NUMERICAL_WHOLE_MATCHING_CANDIDATE'
    require(result['status'] == expected_status, 'MIP result status differs')
    raw_y = result['raw_matching_values']
    raw_error = None
    if raw_y is not None:
        require(type(raw_y) is list and len(raw_y) == len(chosen_y) and
                all(type(value) in (int, float) and isfinite(value) for value in raw_y), 'Malformed raw Y')
        raw_error = max(min(abs(value), abs(value-1)) for value in raw_y)
        require(result['raw_solution_values'][1680:1680+len(raw_y)] == raw_y, 'Raw Y does not match raw solution slice')
    if retained:
        require(geometry_report['unchanged_exact_labeled_graph'] and result['numeric_edge_values'] == initial_x,
                'Retained initial point differs from original K or X')
    else:
        require(raw_y is not None and raw_error <= 1e-5 and [round(value) for value in raw_y] == chosen_y,
                'Selected solver Y is not numerically integral or differs from chosen exact Y')
        projected_x = [min(1, max(0, value)) for value in result['raw_solution_values'][:1680]]
        require(projected_x == result['numeric_edge_values'], 'Returned X differs from selected solver X projection')
        require(type(result['numeric_solver_objective']) in (int, float) and isfinite(result['numeric_solver_objective']) and
                merit_report['total_violation'] <= result['numeric_solver_objective']+1e-5*max(1, merit_report['total_violation']),
                'Raw MIP objective underestimates independently recomputed merit')
    if result['fix_initial']:
        require(geometry_report['unchanged_exact_labeled_graph'], 'Fixed-Y control changed K')
    for source in (Path(__file__), Path(__file__).with_name('audit_certificate.py'), Path(__file__).with_name('audit_phase1.py')):
        digest(source)
    report = {'status': 'INDEPENDENT_WHOLE_MATCHING_CANDIDATE_AND_RETURNED_MERIT_AUDIT_PASS',
              'geometry': geometry_report, 'returned_merit': merit_report,
              'raw_solver_y_integrality_error': raw_error, 'selected_origin': result['selected_origin'],
              'solver_status_recorded_not_certified': result['solver_model_status'],
              'raw_solver_objective': result['numeric_solver_objective'],
              'all840_quota_and3486_pair_residuals_and_slacks_recomputed': True,
              'initial_merit_independently_recomputed': warm_merit,
              'inputs_sha256': hashes, 'elapsed_seconds': time.perf_counter()-started,
              'producer_or_solver_imported': False,
              'scope': 'Only the extracted fixed K and returned X are independently checked. Chosen Y is exact binary; raw solver Y is separately reported. MIP feasibility, optimality, gaps and bounds are not independently certified. This does not establish pair AC, a full graph, exclusion, or global coverage.'}
    args.out.write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({key: value for key, value in report.items() if key != 'inputs_sha256'}))


if __name__ == '__main__':
    main()
