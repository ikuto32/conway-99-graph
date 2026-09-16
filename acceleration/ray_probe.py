"""Extract HiGHS' primal infeasibility ray, then independently audit exact weights.

This avoids solving a separate minimum-L1 dual LP. Only an exact checked
certificate constitutes exclusion. The model is the same necessary linear
completion system as linear_probe.py, without disjoint compression totals.
"""
import argparse
from hashlib import sha256
import json
from math import isfinite
from pathlib import Path
import time

import highspy
import numpy as np

from audit_certificate import full_graph, audit
from linear_probe import constraints, reconstruct
from prepare import path_key


def solve(path, seconds=30):
    data = json.loads(path.read_bytes())
    full_graph(data)
    known = set(map(tuple, data['overlap_edges_outer_zero_based']))
    started = time.perf_counter()
    edges, groups, neq, matrix, target = constraints(known)
    lp = highspy.HighsLp()
    lp.num_col_, lp.num_row_ = len(edges), len(groups)
    lp.col_cost_ = np.zeros(len(edges))
    lp.col_lower_, lp.col_upper_ = np.zeros(len(edges)), np.ones(len(edges))
    lp.row_lower_ = np.concatenate([target[:neq], np.full(len(groups)-neq, -highspy.kHighsInf)])
    lp.row_upper_ = target
    lp.a_matrix_.format_ = highspy.MatrixFormat.kRowwise
    lp.a_matrix_.start_, lp.a_matrix_.index_, lp.a_matrix_.value_ = matrix.indptr, matrix.indices, matrix.data
    solver = highspy.Highs()
    for key, value in [('output_flag', False), ('time_limit', seconds), ('threads', 1), ('solver', 'simplex')]:
        if solver.setOptionValue(key, value) != highspy.HighsStatus.kOk:
            raise RuntimeError(f'Invalid HiGHS option {key}')
    if solver.passModel(lp) != highspy.HighsStatus.kOk:
        raise RuntimeError('HiGHS rejected model')
    solve_start = time.perf_counter()
    run_status = solver.run()
    model_status = solver.getModelStatus()
    result = {'status': 'NO_EXACT_CERTIFICATE', 'candidate_path': path_key(path),
              'candidate_sha256': sha256(path.read_bytes()).hexdigest(),
              'producer_sha256': sha256(Path(__file__).read_bytes()).hexdigest(),
              'model_builder_sha256': sha256(Path(__file__).with_name('linear_probe.py').read_bytes()).hexdigest(),
              'highs_version': solver.version(), 'run_status': str(run_status),
              'primal_model_status': str(model_status), 'primal_seconds': time.perf_counter()-solve_start,
              'linear_variables': len(edges), 'linear_constraints': len(groups),
              'disjoint_block_totals_assumed': False, 'time_limit_per_solve_seconds': seconds,
              'scope': 'One complete E0=0 overlap assignment, continuous disjoint-edge necessary relaxation only; no global exclusion.'}
    if model_status == highspy.HighsModelStatus.kInfeasible:
        ray_start = time.perf_counter()
        ray_status, has_ray, ray = solver.getDualRay()
        result.update(ray_status=str(ray_status), ray_exists=bool(has_ray),
                      ray_seconds=time.perf_counter()-ray_start)
        if ray_status == highspy.HighsStatus.kOk and has_ray:
            if len(ray) != len(groups) or not np.all(np.isfinite(ray)):
                raise ValueError('Invalid infeasibility ray')
            magnitude = np.max(np.abs(ray))
            if magnitude > 0:
                # HiGHS row ray is positive for lower-bound rows. Our auditor
                # uses <= inequalities, hence its sign is reversed.
                result.update(reconstruct(groups, edges, -ray/magnitude))
    elif model_status == highspy.HighsModelStatus.kOptimal:
        result.update(status='NUMERICAL_LINEAR_FEASIBILITY_ONLY',
                      numeric_edge_values=list(solver.getSolution().col_value))
    result['elapsed_seconds'] = time.perf_counter()-started
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--seconds', type=float, default=30)
    args = parser.parse_args()
    if not isfinite(args.seconds) or args.seconds <= 0:
        parser.error('--seconds must be finite and positive')
    if args.out.exists():
        raise FileExistsError(args.out)
    result = solve(args.input, args.seconds)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(result, indent=2)+'\n')
    if result['status'] == 'EXACT_INTEGER_WEIGHTED_CAPACITY_CONTRADICTION':
        report = audit(args.input, args.out)
        with args.out.with_name(args.out.stem+'_audit.json').open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(report, indent=2)+'\n')
    print(json.dumps({k: v for k, v in result.items()
                      if k not in ('numeric_edge_values', 'group_multipliers', 'edge_upper_bound_multipliers')}))


if __name__ == '__main__':
    main()
