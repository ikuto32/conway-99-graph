"""Higher-accuracy interior-point phase-I; prior producers remain unchanged.

Minimize the UNWEIGHTED sum of absolute quota residuals plus positive
linear-pair-cap residuals, over the 1,680 disjoint-edge variables in [0,1].
Each equality gets positive/negative residual slacks; each upper inequality
gets a nonnegative violation slack. The LP is always feasible. Objective zero
would only indicate numerical feasibility of this necessary relaxation.

Public solve_edges(edges, seconds=30) returns a JSON-serializable dictionary.
solve_edges_with_basis(edges, seconds=30, basis=None) also returns a HiGHS basis
separately; rejected or dimension-incompatible bases safely fall back to cold.
"""
import argparse
from hashlib import sha256
import json
from math import isfinite
from pathlib import Path
import sys
import time

import highspy
import numpy as np
import scipy
from scipy.sparse import coo_matrix, hstack

from audit_certificate import full_graph, require
from linear_probe import constraints


def _source_hash(path):
    return sha256(path.read_bytes()).hexdigest()


def _merit(matrix, target, neq, x):
    residuals = np.asarray(matrix @ x - target)
    quota = np.abs(residuals[:neq])
    caps = np.maximum(residuals[neq:], 0)
    return residuals, {
        'quota_absolute_sum': float(np.sum(quota)),
        'pair_cap_positive_sum': float(np.sum(caps)),
        'total': float(np.sum(quota)+np.sum(caps)),
        'maximum_quota_absolute_residual': float(np.max(quota, initial=0)),
        'maximum_pair_cap_positive_residual': float(np.max(caps, initial=0)),
        'quota_rows_above_1e_7': int(np.count_nonzero(quota > 1e-7)),
        'pair_cap_rows_above_1e_7': int(np.count_nonzero(caps > 1e-7)),
    }


def solve_edges_with_basis(edges, seconds=30, basis=None):
    require(not sys.flags.optimize, 'Run without -O: the frozen matrix builder uses assertions')
    require(type(seconds) in (int, float) and isfinite(seconds) and seconds > 0,
            'seconds must be finite and positive')
    started = time.perf_counter()
    listed = [list(pair) for pair in edges]
    full_graph({'overlap_edges_outer_zero_based': listed})
    known = set(map(tuple, listed))
    ordered = [list(pair) for pair in sorted(known)]
    canonical_bytes = json.dumps(ordered, separators=(',', ':')).encode('ascii')
    columns, groups, neq, matrix, target = constraints(known)
    nx, nr = len(columns), len(groups)
    # Equality: A*x - excess + shortage = b. Cap: A*x - excess <= b.
    # The first nr slacks are excess/violation; the final neq are shortage.
    slack_rows = np.concatenate([np.arange(nr), np.arange(neq)])
    slack_cols = np.arange(nr+neq)
    slack_values = np.concatenate([-np.ones(nr), np.ones(neq)])
    slack_matrix = coo_matrix((slack_values, (slack_rows, slack_cols)),
                              shape=(nr, nr+neq)).tocsr()
    augmented = hstack([matrix, slack_matrix], format='csr')
    total_columns = nx+nr+neq
    lp = highspy.HighsLp()
    lp.num_col_, lp.num_row_ = total_columns, nr
    lp.col_cost_ = np.concatenate([np.zeros(nx), np.ones(nr+neq)])
    lp.col_lower_ = np.zeros(total_columns)
    lp.col_upper_ = np.concatenate([np.ones(nx), np.full(nr+neq, highspy.kHighsInf)])
    lp.row_lower_ = np.concatenate([target[:neq], np.full(nr-neq, -highspy.kHighsInf)])
    lp.row_upper_ = target
    lp.a_matrix_.format_ = highspy.MatrixFormat.kRowwise
    lp.a_matrix_.start_ = augmented.indptr
    lp.a_matrix_.index_ = augmented.indices
    lp.a_matrix_.value_ = augmented.data
    solver = highspy.Highs()
    for option, value in [('output_flag', False), ('time_limit', float(seconds)),
                          ('threads', 1), ('solver', 'ipm'), ('run_crossover', 'off'), ('random_seed', 0),
                          ('ipm_optimality_tolerance', 1e-10),
                          ('primal_feasibility_tolerance', 1e-10),
                          ('dual_feasibility_tolerance', 1e-10)]:
        require(solver.setOptionValue(option, value) == highspy.HighsStatus.kOk,
                f'HiGHS rejected option {option}')
    require(solver.passModel(lp) == highspy.HighsStatus.kOk, 'HiGHS rejected phase-I model')
    basis_accepted = False
    basis_reason = 'NOT_SUPPLIED'
    if basis is not None:
        if (hasattr(basis, 'col_status') and hasattr(basis, 'row_status')
                and len(basis.col_status) == total_columns and len(basis.row_status) == nr):
            basis_accepted = solver.setBasis(basis) == highspy.HighsStatus.kOk
            basis_reason = 'ACCEPTED' if basis_accepted else 'HIGHS_REJECTED_COLD_FALLBACK'
        else:
            basis_reason = 'DIMENSION_MISMATCH_COLD_FALLBACK'
    model_seconds = time.perf_counter()-started
    solve_started = time.perf_counter()
    run_status = solver.run()
    solve_seconds = time.perf_counter()-solve_started
    model_status, solution, info = solver.getModelStatus(), solver.getSolution(), solver.getInfo()
    result = {
        'status': 'PHASE1_NO_USABLE_NUMERICAL_SOLUTION', 'optimal': False,
        'numeric_objective': None, 'numeric_edge_values': None,
        'row_duals': None, 'phase1_multipliers': None, 'residual_breakdown': None,
        'overlap_edges_sha256': sha256(canonical_bytes).hexdigest(),
        'edge_order': 'Lexicographic (u,v), 0 <= u < v < 84, disjoint root supports',
        'edge_variables': [list(pair) for pair in columns],
        'constraint_groups': groups, 'equality_rows': neq, 'pair_cap_rows': nr-neq,
        'disjoint_variables': nx, 'slack_variables': nr+neq, 'total_columns': total_columns,
        'objective_definition': 'sum(abs(quota A*x-b)) + sum(max(0,pair_cap A*x-b)); all weights are 1',
        'row_dual_convention': 'HiGHS signed row marginals; phase1 multiplier y = -row_dual. Equality y in [-1,1], cap y in [0,1].',
        'highs_version': solver.version(), 'numpy_version': np.__version__, 'scipy_version': scipy.__version__,
        'run_status': str(run_status), 'primal_model_status': str(model_status),
        'primal_solution_status': int(info.primal_solution_status),
        'dual_solution_status': int(info.dual_solution_status),
        'simplex_iterations': int(info.simplex_iteration_count),
        'basis_supplied': basis is not None, 'basis_accepted': basis_accepted, 'basis_status': basis_reason,
        'time_limit_seconds': seconds, 'model_build_seconds': model_seconds, 'solve_seconds': solve_seconds,
        'requested_solver_tolerances': dict(ipm_optimality_tolerance=1e-10,
            primal_feasibility_tolerance=1e-10, dual_feasibility_tolerance=1e-10),
        'independent_audit_tolerance_changed': False,
        'disjoint_block_totals_assumed': False,
        'source_sha256': {path.name: _source_hash(path) for path in
                          [Path(__file__), Path(__file__).with_name('linear_probe.py'),
                           Path(__file__).with_name('audit_certificate.py')]},
        'scope': 'Numerical phase-I merit of one fixed complete overlap assignment. Positive or zero floating objectives are not exact exclusion or graph certificates. This is a necessary continuous relaxation only.',
    }
    if (solution.value_valid and len(solution.col_value) == total_columns
            and np.all(np.isfinite(solution.col_value))):
        raw_x = np.asarray(solution.col_value[:nx], dtype=float)
        # A projected X is a valid point of the box even on a limited solve.
        # Its merit is recomputed; projection is never an exact-proof step.
        x = np.clip(raw_x, 0.0, 1.0)
        projection = float(np.max(np.abs(x-raw_x), initial=0))
        residuals, breakdown = _merit(matrix, target, neq, x)
        slack_objective = float(np.sum(solution.col_value[nx:]))
        solver_objective = float(info.objective_function_value)
        if not isfinite(solver_objective):
            solver_objective = None
        numerical_optimal = (model_status == highspy.HighsModelStatus.kOptimal
                             and run_status == highspy.HighsStatus.kOk and projection <= 1e-7
                             and solver_objective is not None
                             and abs(breakdown['total']-solver_objective) <= 1e-6*max(1, abs(solver_objective)))
        result.update(status='PHASE1_NUMERICAL_OPTIMUM' if numerical_optimal else 'PHASE1_NUMERICAL_INCUMBENT',
                      optimal=numerical_optimal, numeric_objective=breakdown['total'],
                      numeric_edge_values=x.tolist(), raw_x_maximum_box_violation=projection,
                      x_projection_maximum=projection, numeric_solver_objective=solver_objective,
                      numeric_slack_objective=slack_objective, row_residuals=residuals.tolist(),
                      residual_breakdown=breakdown)
        if solution.dual_valid and len(solution.row_dual) == nr and np.all(np.isfinite(solution.row_dual)):
            marginals = np.asarray(solution.row_dual, dtype=float)
            y = -marginals
            feasible_y = y.copy()
            feasible_y[:neq] = np.clip(feasible_y[:neq], -1, 1)
            feasible_y[neq:] = np.clip(feasible_y[neq:], 0, 1)
            coefficients = np.asarray(matrix.T @ feasible_y)
            lower = float(-target @ feasible_y + np.sum(np.minimum(coefficients, 0)))
            result.update(row_duals=marginals.tolist(), phase1_multipliers=y.tolist(),
                          box_column_duals=list(solution.col_dual[:nx]),
                          dual_multiplier_projection_maximum=float(np.max(np.abs(feasible_y-y), initial=0)),
                          numerical_dual_lower_bound=lower,
                          numerical_primal_dual_gap=breakdown['total']-lower)
    result['elapsed_seconds'] = time.perf_counter()-started
    saved_basis = solver.getBasis()
    return result, saved_basis if saved_basis.valid else None


def solve_edges(edges, seconds=30):
    """Return phase-I merit and a bounded fractional X; every result is numerical."""
    return solve_edges_with_basis(edges, seconds=seconds)[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--seconds', type=float, default=30)
    args = parser.parse_args()
    require(not args.out.exists(), 'Preserve existing phase-I result')
    raw = args.input.read_bytes()
    result = solve_edges(json.loads(raw)['overlap_edges_outer_zero_based'], args.seconds)
    path = args.input.resolve()
    root = Path(__file__).resolve().parents[1]
    result.update(candidate_path=path.relative_to(root).as_posix() if path.is_relative_to(root) else path.as_posix(),
                  candidate_sha256=sha256(raw).hexdigest())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(result, indent=2, allow_nan=False)+'\n')
    omitted = {'edge_variables', 'constraint_groups', 'numeric_edge_values', 'row_duals',
               'phase1_multipliers', 'row_residuals', 'box_column_duals'}
    print(json.dumps({key: value for key, value in result.items() if key not in omitted}, allow_nan=False))


if __name__ == '__main__':
    main()
