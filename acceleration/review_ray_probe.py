"""Capture the actual HiGHS model and check semantic rows and status handling.

This deliberately imports the producer as the target under review. The separate
integer-certificate auditor still imports no producer or solver implementation.
"""
import argparse
from collections import Counter
from itertools import combinations
import json
from pathlib import Path
from types import SimpleNamespace

import highspy
import numpy as np

from audit_certificate import audit, full_graph, graph_constraint, require
from prepare import digest, path_key
import ray_probe


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), 'Review output must be new')
    producer = Path(ray_probe.__file__)
    producer_before = digest(producer)
    captured = {}
    real_highs = highspy.Highs

    class CaptureHighs:
        def __init__(self):
            self.solver = real_highs()

        def __getattr__(self, name):
            return getattr(self.solver, name)

        def passModel(self, model):
            captured['model'] = model
            return self.solver.passModel(model)

    try:
        highspy.Highs = CaptureHighs
        actual = ray_probe.solve(args.candidate, 30)
    finally:
        highspy.Highs = real_highs
    require(actual['status'] == 'EXACT_INTEGER_WEIGHTED_CAPACITY_CONTRADICTION',
            'Review fixture must reproduce an exact ray certificate')
    certificate_path = args.out.with_name(args.out.stem+'_reproduction.json')
    require(not certificate_path.exists(), 'Reproduction output must be new')
    certificate_path.write_text(json.dumps(actual, indent=2)+'\n', encoding='utf-8')
    exact = audit(args.candidate, certificate_path)
    require(exact['status'] == 'INDEPENDENT_INTEGER_FARKAS_AUDIT_PASS', 'Independent reproduction audit failed')

    lp = captured['model']
    adjacency, unknown = full_graph(json.loads(args.candidate.read_bytes()))
    edges = sorted(unknown)
    require(lp.num_col_ == len(edges) == 1680, 'Wrong column count')
    require(list(lp.col_cost_) == [0.0]*1680, 'Objective is not zero feasibility')
    require(list(lp.col_lower_) == [0.0]*1680 and list(lp.col_upper_) == [1.0]*1680,
            'Wrong variable bounds')
    require(not list(lp.integrality_), 'Model unexpectedly requests integrality')
    require(lp.a_matrix_.format_ == highspy.MatrixFormat.kRowwise, 'CSR not marked rowwise')
    coordinates = [('label_quota', [u, s]) for u in range(84) for s in range(14)]
    coordinates += [('linear_pair_cap', list(pair)) for pair in combinations(range(84), 2)]
    row = 0
    equality_count = 0
    omitted = Counter()
    starts, indices, values = lp.a_matrix_.start_, lp.a_matrix_.index_, lp.a_matrix_.value_
    require(len(starts) == lp.num_row_+1 and starts[0] == 0
            and starts[-1] == len(indices) == len(values), 'Malformed CSR sizes')
    for kind, coordinate in coordinates:
        terms, rhs = graph_constraint(adjacency, unknown, kind, coordinate)
        if not terms:
            require(rhs == 0 if kind == 'label_quota' else rhs >= 0, 'Nontrivial row omitted')
            omitted[kind] += 1
            continue
        actual_terms = Counter()
        for j in range(starts[row], starts[row+1]):
            require(0 <= indices[j] < len(edges) and values[j] == 1.0, 'Wrong native matrix entry')
            actual_terms[edges[indices[j]]] += int(values[j])
        require(actual_terms == terms and lp.row_upper_[row] == rhs, f'Semantic CSR mismatch at row {row}')
        if kind == 'label_quota':
            require(lp.row_lower_[row] == rhs, 'Equality lower bound differs')
            equality_count += 1
        else:
            require(lp.row_lower_[row] == -highspy.kHighsInf, 'Inequality unexpectedly has lower bound')
        row += 1
    require(row == lp.num_row_, 'Extra native rows')

    checks = []

    def branch(name, model_status, ray_mode='missing', expected='NO_EXACT_CERTIFICATE', failure=False):
        class ControlledHighs:
            def setOptionValue(self, key, value):
                return highspy.HighsStatus.kError if ray_mode == 'option_error' else highspy.HighsStatus.kOk

            def passModel(self, model):
                self.model = model
                return highspy.HighsStatus.kError if ray_mode == 'model_error' else highspy.HighsStatus.kOk

            def run(self):
                return highspy.HighsStatus.kWarning

            def getModelStatus(self):
                return model_status

            def version(self):
                return 'controlled-review-double'

            def getSolution(self):
                return SimpleNamespace(col_value=[0.0]*self.model.num_col_)

            def getDualRay(self):
                n = self.model.num_row_
                if ray_mode == 'missing':
                    return highspy.HighsStatus.kOk, False, np.zeros(n)
                if ray_mode == 'error':
                    return highspy.HighsStatus.kError, True, np.ones(n)
                if ray_mode == 'wrong_length':
                    return highspy.HighsStatus.kOk, True, np.zeros(n-1)
                if ray_mode == 'nonfinite':
                    return highspy.HighsStatus.kOk, True, np.full(n, np.nan)
                if ray_mode == 'wrong_sign':
                    return highspy.HighsStatus.kOk, True, np.ones(n)
                return highspy.HighsStatus.kOk, True, np.zeros(n)
        try:
            highspy.Highs = ControlledHighs
            result = ray_probe.solve(args.candidate, 30)
        except (ValueError, RuntimeError) as error:
            require(failure, f'Unexpected branch error: {name}: {error}')
            checks.append({'name': name, 'rejected': True, 'error': str(error)})
        else:
            require(not failure and result['status'] == expected, f'Bad producer status for {name}')
            require('group_multipliers' not in result, 'Noncertificate branch contains proof multipliers')
            checks.append({'name': name, 'status': result['status']})
        finally:
            highspy.Highs = real_highs

    branch('time_limit', highspy.HighsModelStatus.kTimeLimit)
    branch('unknown', highspy.HighsModelStatus.kUnknown)
    branch('unbounded_or_infeasible', highspy.HighsModelStatus.kUnboundedOrInfeasible)
    branch('numeric_optimal_only', highspy.HighsModelStatus.kOptimal, expected='NUMERICAL_LINEAR_FEASIBILITY_ONLY')
    branch('infeasible_without_ray', highspy.HighsModelStatus.kInfeasible)
    branch('ray_error', highspy.HighsModelStatus.kInfeasible, 'error')
    branch('zero_ray', highspy.HighsModelStatus.kInfeasible, 'zero')
    branch('wrong_sign_ray', highspy.HighsModelStatus.kInfeasible, 'wrong_sign')
    branch('wrong_length_ray', highspy.HighsModelStatus.kInfeasible, 'wrong_length', failure=True)
    branch('nonfinite_ray', highspy.HighsModelStatus.kInfeasible, 'nonfinite', failure=True)
    branch('option_error', highspy.HighsModelStatus.kUnknown, 'option_error', failure=True)
    branch('model_error', highspy.HighsModelStatus.kUnknown, 'model_error', failure=True)
    require(digest(producer) == producer_before, 'Producer changed during review')
    sources = [args.candidate, certificate_path, producer, Path(__file__),
               producer.with_name('linear_probe.py'), producer.with_name('audit_certificate.py')]
    result = {
        'status': 'INDEPENDENT_HIGHS_RAY_MODEL_STATUS_AND_EXACT_CERTIFICATE_REVIEW_PASS',
        'captured_actual_highs_model': True, 'model_rows_compared': row,
        'label_equalities': equality_count, 'pair_inequalities': row-equality_count,
        'all_semantic_coordinates_checked': len(coordinates), 'omitted_tautologies': dict(omitted),
        'variables': len(edges), 'variable_bounds': [0, 1], 'integrality_requested': False,
        'actual_highs_version': actual['highs_version'],
        'exact_reproduction_audit': exact, 'status_controls': checks,
        'inputs_sha256': {path_key(path): digest(path) for path in sources},
        'source_references': ['https://ergo-code.github.io/HiGHS/dev/structures/classes/HighsLp/',
                              'https://ergo-code.github.io/HiGHS/dev/interfaces/c_api/'],
        'scope': 'Producer model and status-flow review on one candidate, plus controlled failure branches. Exact reproduction accepted only by the independent producer-free integer auditor. No global exclusion or numerical feasibility certificate.',
    }
    with args.out.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
