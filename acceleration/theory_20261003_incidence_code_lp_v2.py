"""Small numerical guide with complete rational dual certificates for binary codes.

For a binary linear length99 code whose nonzero weights are even36..60 only.
This is a conditional code-size bound, never graph nonexistence. A separate
implementation must check the certificate and its target interpretation.
"""
import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import platform
import subprocess
import sys
import time
import highspy
import numpy as np
from scipy.sparse import csr_matrix
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
WEIGHTS = list(range(36, 61, 2))
AUDIT = 'acceleration/results/20261003_independent_review/incidence_griesmer01/summary.json'
AUDIT_SHA = 'f6d37038fa7f5969331e8d7ee9490bdcc6ebda09b3a0770b7a99dea298a9c59b'


def need(ok, why):
    if not ok:
        raise ValueError(why)


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, data):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(data, stream, indent=2)
        stream.write('\n')


def kraw(n, j, w):
    return sum((-1) ** s * math.comb(w, s) * math.comb(n - w, j - s)
               for s in range(max(0, j - (n - w)), min(j, w) + 1))


def frac(value):
    return [value.numerator, value.denominator]


def exact_check(n, weights, y):
    need(len(y) == n and all(value >= 0 for value in y), 'complete nonnegative dual')
    lhs = [-sum(y[j - 1] * Fraction(kraw(n, j, w), math.comb(n, j))
                for j in range(1, n + 1)) for w in weights]
    need(all(value >= 1 for value in lhs), 'all exact positive-weight dual inequalities')
    return Fraction(1) + sum(y), lhs


def controls():
    # Length3 full binary code: K_n=(-1)^w, with all weights1..3;
    # use all j with y_j=comb(3,j), giving sum_j y_j*(-K_j/comb)=1.
    y = [Fraction(math.comb(3, j)) for j in range(1, 4)]
    bound, lhs = exact_check(3, [1, 2, 3], y)
    need(bound == 8 and lhs == [1, 1, 1], 'full binary positive bound')
    negatives = []
    for label, changed in [('negative', [-y[0], *y[1:]]),
                           ('truncated', y[:-1]), ('zero', [Fraction(0)] * 3),
                           ('insufficient', [value / 2 for value in y])]:
        try:
            exact_check(3, [1, 2, 3], changed)
        except ValueError as exc:
            negatives.append(dict(case=label, diagnostic=str(exc)))
        else:
            raise ValueError('corrupt dual accepted')
    # Direct character sum independently agrees with every small Krawtchouk.
    checked = 0
    for n in range(1, 7):
        for w in range(n + 1):
            x = (1 << w) - 1
            for j in range(n + 1):
                value = sum((-1) ** ((x & u).bit_count())
                            for u in range(1 << n) if u.bit_count() == j)
                need(value == kraw(n, j, w), 'literal character-polynomial control')
                checked += 1
    return dict(positive_exact_bound=8, strict_negative_controls=negatives,
                complete_small_character_checks=checked,
                timing='Before target guide/model/certificate inspection',
                limitation='Finite controls only; independent certificate path required.')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--seconds', type=float, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='One13row99column code-bound dual guide; <=30s numerical guide, reserve30s for exact certificate/checkpoint and shutdown;90worker inside120outer.')
    out = args.out.resolve()
    need(out.is_relative_to(ROOT), 'workspace output')
    out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    cal = controls()
    save(out / 'controls.json', cal)
    need(sha(ROOT / AUDIT) == AUDIT_SHA, 'separate incidence interpretation audit')
    n = 99
    # Rows are allowed nonzero weights; columns are positive character degrees.
    coefficients = [[-Fraction(kraw(n, j, w), math.comb(n, j))
                     for j in range(1, n + 1)] for w in WEIGHTS]
    save(out / 'exact_model.json', dict(length=n, nonzero_weights=WEIGHTS,
         degrees=list(range(1, 100)), coefficient_pairs=[[frac(c) for c in row] for row in coefficients],
         rhs=[1] * len(WEIGHTS), direction='minimize sum y_j; y>=0; G*y>=1'))
    matrix = csr_matrix(np.asarray([[float(value) for value in row] for row in coefficients]))
    original_numeric = matrix.data.copy()
    matrix.data[np.abs(matrix.data) < 1e-11] = 0.0
    matrix.eliminate_zeros()
    save(out / 'numeric_input_metadata.json', dict(absolute_truncation_threshold=1e-11,
         removed_small_coefficients=int(np.count_nonzero(np.abs(original_numeric) < 1e-11)),
         scope='Numerical guide only; complete exact original coefficients decide certificates.'))
    lp = highspy.HighsLp()
    lp.num_col_, lp.num_row_ = n, len(WEIGHTS)
    lp.col_cost_, lp.col_lower_, lp.col_upper_ = np.ones(n), np.zeros(n), np.full(n, highspy.kHighsInf)
    lp.row_lower_, lp.row_upper_ = np.ones(len(WEIGHTS)), np.full(len(WEIGHTS), highspy.kHighsInf)
    lp.a_matrix_.format_ = highspy.MatrixFormat.kRowwise
    lp.a_matrix_.start_, lp.a_matrix_.index_, lp.a_matrix_.value_ = matrix.indptr, matrix.indices, matrix.data
    solver = highspy.Highs()
    guide_seconds = deadline.child_seconds(30, reserve_seconds=30)
    for name, value in [('threads', 1), ('random_seed', 0), ('solver', 'simplex'),
                        ('output_flag', False), ('small_matrix_value', 1e-12), ('time_limit', guide_seconds),
                        ('primal_feasibility_tolerance', 1e-10), ('dual_feasibility_tolerance', 1e-10)]:
        need(solver.setOptionValue(name, value) == highspy.HighsStatus.kOk, 'explicit solver option ' + name)
    pass_status = solver.passModel(lp)
    save(out / 'numeric_pass_status.json', dict(status=str(pass_status)))
    need(pass_status == highspy.HighsStatus.kOk, 'guide input accepted')
    guide_started = time.monotonic()
    run_status = solver.run()
    numeric = list(solver.getSolution().col_value)
    record = dict(run_status=str(run_status), model_status=str(solver.getModelStatus()),
                  elapsed=time.monotonic() - guide_started, allocation=guide_seconds,
                  objective=solver.getObjectiveValue(), values=numeric)
    save(out / 'numerical_guide.json', record)
    candidate, attempts = None, []
    if len(numeric) == n and all(math.isfinite(v) for v in numeric):
        for max_denominator in [1000, 1000000, 1000000000]:
            need(not deadline.status()['stop_required'], 'not completed within allocated budget')
            y = [Fraction(max(0.0, v)).limit_denominator(max_denominator) for v in numeric]
            lhs = [sum(value * c for value, c in zip(y, row)) for row in coefficients]
            minimum = min(lhs)
            attempts.append(dict(max_denominator=max_denominator, exact_minimum=frac(minimum)))
            if minimum <= 0:
                continue
            normalized = [value / minimum for value in y]
            bound, checked_lhs = exact_check(n, WEIGHTS, normalized)
            # A binary linear code's size is an integral power of two. Exact only.
            maximum_dimension = 0
            while Fraction(1 << (maximum_dimension + 1)) <= bound:
                maximum_dimension += 1
            candidate = dict(schema='BINARY_CODE_COMPLETE_RATIONAL_DUAL_V1', length=n,
                             nonzero_weights=WEIGHTS, degrees=list(range(1, 100)),
                             dual_pairs=[frac(value) for value in normalized],
                             lhs_pairs=[frac(value) for value in checked_lhs],
                             exact_size_upper=frac(bound), maximum_linear_dimension=maximum_dimension,
                             conditional_incidence_rank_lower=99 - maximum_dimension,
                             source_rounded_denominator_limit=max_denominator,
                             normalization_minimum=frac(minimum),
                             status='CANDIDATE_PENDING_INDEPENDENT_CERTIFICATE_AND_DERIVATION_CHECK',
                             optimum_asserted=False, target_resolution='NONE')
            save(out / 'certificate.json', candidate)
            break
    pins = {p.relative_to(ROOT).as_posix(): sha(p) for p in
            [Path(__file__), ROOT / 'acceleration/theory_20261003_incidence_code_lp_v2_spec.md',
             ROOT / AUDIT, ROOT / 'pyproject.toml', ROOT / 'uv.lock',
             ROOT / 'acceleration/command_deadline.py', out / 'controls.json',
             out / 'exact_model.json', out / 'numerical_guide.json', out / 'numeric_input_metadata.json', out / 'numeric_pass_status.json']}
    if candidate:
        pins[(out / 'certificate.json').relative_to(ROOT).as_posix()] = sha(out / 'certificate.json')
    save(out / 'summary.json', dict(status='CANDIDATE_EXACT_DUAL' if candidate else 'UNKNOWN_NO_EXACT_DUAL',
         timestamp=datetime.now(timezone.utc).isoformat(), command=[sys.executable, *sys.argv], cwd=str(ROOT),
         source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
         python=platform.python_version(), highspy=solver.version(), numpy=np.__version__,
         inputs_outputs_sha256=pins, selected_code_domain=dict(length=99, nonzero_weights=WEIGHTS),
         attempted_guides=1, completed_guides=1, exact_candidate_certificates=int(candidate is not None),
         candidate=candidate, lift_attempts=attempts, elapsed_seconds=time.monotonic() - started,
         deadline=deadline.status(), target_resolution='NONE', graph_searches=0,
         limitations=['No code construction, optimality or rank upper bound.',
                     'Numerical guide is not a certificate; exact rational dual awaits independent implementation.',
                     'A rank lower bound alone does not exclude the target.']))
    print(json.dumps(dict(status='CANDIDATE_EXACT_DUAL' if candidate else 'UNKNOWN_NO_EXACT_DUAL',
          dimension=None if candidate is None else candidate['maximum_linear_dimension'],
          rank_lower=None if candidate is None else candidate['conditional_incidence_rank_lower'],
          target_resolution='NONE')))


if __name__ == '__main__':
    main()
