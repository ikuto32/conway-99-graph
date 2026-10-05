"""Discovery: exact rooted-six affine dimensions and conditional integer domain.

Reads frozen raw necessary-model rows only. Modular computations guide lifting;
every proposed null vector is checked exactly over Fraction and integer rows.
Prism-free conclusions remain conditional and need separate artifact review.
"""
from __future__ import annotations

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

import numpy as np
from tqdm import tqdm
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT/'acceleration/results/20261002_rooted6_prismfree_rigidity'
INPUTS = {
 'ordered_nonedge_model.json': 'ecf558faa95576b8e76fbc5a62743729a875307eeb99df803c7cb5cdac7b7645',
 'ordered_nonedge_prismfree_rows.json': 'c3d65c00754b4b600140b0723fad42c23748324237ec16d1cdf506d73bc606c2',
 'ordered_nonedge_prismfree_primal.json': '1dadc060d77051baefe10ecc8bea5afc26441c3cfea877f37c6a484ded4fa64b',
}


def need(value, reason):
    if not value:
        raise ValueError(reason)


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def save(path, value):
    with Path(path).open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def read(path):
    return json.loads(Path(path).read_bytes())


def check_deadline(deadline):
    need(not deadline.status()['stop_required'], 'not completed within the allocated budget')


def isprime(n):
    return n >= 2 and all(n % divisor for divisor in range(2, math.isqrt(n)+1))


def echelon(rows, columns, prime, deadline):
    need(prime <= 1000000007 and isprime(prime), 'exact prime and int64 product bound')
    work = np.zeros((len(rows), columns), dtype=np.int64)
    for i, row in enumerate(rows):
        for j, coefficient in row['terms']:
            work[i, j] = coefficient % prime
    pivots, selected_original_rows = [], []
    permutation = list(range(len(rows)))
    rank = 0
    for column in tqdm(range(columns), desc=f'exact echelon mod{prime}', mininterval=5):
        if not column % 32:
            check_deadline(deadline)
        candidates = np.flatnonzero(work[rank:, column])
        if not len(candidates):
            continue
        selected = rank + int(candidates[0])
        work[[rank, selected]] = work[[selected, rank]]
        permutation[rank], permutation[selected] = permutation[selected], permutation[rank]
        work[rank] = work[rank] * pow(int(work[rank, column]), -1, prime) % prime
        if rank + 1 < len(rows):
            # Residues/products < prime^2 <= 1,000,000,014,000,000,049;
            # subtraction cannot overflow signed64.
            work[rank+1:] = (work[rank+1:] - work[rank+1:, column, None] * work[rank]) % prime
        pivots.append(column)
        selected_original_rows.append(permutation[rank])
        rank += 1
    free = sorted(set(range(columns)) - set(pivots))
    vectors = []
    for coordinate in free:
        vector = [0] * columns
        vector[coordinate] = 1
        for i in range(rank-1, -1, -1):
            column = pivots[i]
            # Python integers for dot products; summed terms exceed int64.
            vector[column] = -sum(int(work[i, j]) * vector[j] for j in range(column+1, columns)) % prime
        vectors.append(vector)
    return dict(prime=prime, rank=rank, pivots=pivots, free_coordinates=free,
        independent_original_row_indices=selected_original_rows), vectors


def reconstruct(value, prime):
    if value == 0:
        return Fraction(0)
    bound = math.isqrt(prime//2)
    old, current, old_den, den = prime, value, 0, 1
    while abs(current) > bound:
        quotient = old//current
        old, current = current, old - quotient*current
        old_den, den = den, old_den - quotient*den
    need(den and abs(den) <= bound and math.gcd(current, den) == 1 and
         (current - value*den) % prime == 0, 'bounded rational reconstruction')
    return Fraction(current, den)


def residuals(rows, vector, affine=False):
    return [sum(coefficient * vector[j] for j, coefficient in row['terms']) -
            (row['rhs'] if affine else 0) for row in rows]


def lift(rows, columns, deadline, out, label):
    attempts = []
    for prime in [65521, 1000000007]:
        rank, modular = echelon(rows, columns, prime, deadline)
        try:
            exact = [[reconstruct(value, prime) for value in vector] for vector in modular]
            need(all(not any(residuals(rows, vector)) for vector in exact), 'all exact homogeneous rows')
            for i, free in enumerate(rank['free_coordinates']):
                need([exact[j][free] for j in range(len(exact))] == [Fraction(int(i == j)) for j in range(len(exact))], 'independent free-coordinate minor')
        except ValueError as error:
            attempts.append(dict(prime=prime, rank=rank['rank'], lifting='FAILED', reason=str(error)))
            save(out/f'{label}_lifting_failed_mod{prime}.json', attempts[-1])
            continue
        attempts.append(dict(prime=prime, rank=rank['rank'], lifting='EXACT_ALL_ROWS_PASS'))
        integer = []
        for vector in exact:
            denominator = math.lcm(*(value.denominator for value in vector))
            values = [int(value*denominator) for value in vector]
            common = math.gcd(*values)
            values = [value//common for value in values]
            need(not any(residuals(rows, values)), 'integer null certificate')
            integer.append(values)
        certificate = dict(format='EXACT_ROOTED6_AFFINE_NULLSPACE_V1', label=label,
            rank_lower_bound=rank, rank_upper_bound_from_independent_vectors=columns-len(exact),
            exact_rational_rank=rank['rank'], exact_nullity=len(exact),
            rational_vectors=[[[value.numerator, value.denominator] for value in vector] for vector in exact],
            primitive_integer_vectors=integer, attempts=attempts,
            row_scope='The exact frozen raw necessary-model rows with listed additional conditional rows, not graph realization.')
        need(rank['rank'] == columns-len(exact), 'matching exact rank lower/upper bounds')
        save(out/f'{label}_nullspace.json', certificate)
        return certificate, exact
    raise ValueError('No exact verified lift within declared prime schedule; preserved failed attempts')


def clip(poly, a, b, c):
    if not poly:
        return []
    result = []
    for previous, current in zip(poly[-1:]+poly[:-1], poly):
        before = c + a*previous[0] + b*previous[1]
        after = c + a*current[0] + b*current[1]
        if (before >= 0) != (after >= 0):
            fraction = before/(before-after)
            crossing = tuple(previous[j]+fraction*(current[j]-previous[j]) for j in range(2))
            if not result or crossing != result[-1]:
                result.append(crossing)
        if after >= 0 and (not result or current != result[-1]):
            result.append(current)
    if len(result) > 1 and result[0] == result[-1]:
        result.pop()
    return result


def polygon(vector, basis, free, total, deadline):
    need(len(basis) == 2, 'two-dimensional conditional space')
    origin = [Fraction(value)-sum(Fraction(vector[coordinate])*basis[j][i] for j, coordinate in enumerate(free))
              for i, value in enumerate(vector)]
    poly = [(Fraction(0), Fraction(0)), (Fraction(total), Fraction(0)),
            (Fraction(total), Fraction(total)), (Fraction(0), Fraction(total))]
    inequalities = []
    for i, constant in enumerate(origin):
        a, b = basis[0][i], basis[1][i]
        coefficients = [a, b, constant]
        denominator = math.lcm(*(value.denominator for value in coefficients))
        coefficients = [int(value*denominator) for value in coefficients]
        common = math.gcd(*coefficients)
        if common:
            coefficients = [value//common for value in coefficients]
        if coefficients not in inequalities:
            inequalities.append(coefficients)
            poly = clip(poly, a, b, constant)
        if not i % 32:
            check_deadline(deadline)
    need(poly, 'preserved exact feasible primal implies nonempty conditional domain')
    bounds = [[math.ceil(min(point[j] for point in poly)), math.floor(max(point[j] for point in poly))] for j in range(2)]
    candidates = math.prod(max(0, high-low+1) for low, high in bounds)
    return origin, poly, bounds, inequalities, candidates


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--seconds', type=float, required=True)
    parser.add_argument('--max_integer_attempts', type=int, default=1000000)
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='567variable sparse rooted6 rows; modular timings underseconds, two-stage exact lifting/domain clipping; reserve60seconds.')
    start = time.monotonic()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    try:
        inputs = {}
        for name, wanted in INPUTS.items():
            need(sha(RAW/name) == wanted, 'frozen raw input ' + name)
            inputs[(RAW/name).relative_to(ROOT).as_posix()] = wanted
        for path in [Path(__file__), ROOT/'pyproject.toml', ROOT/'uv.lock', ROOT/'acceleration/command_deadline.py']:
            inputs[path.relative_to(ROOT).as_posix()] = sha(path)
        save(out/'manifest.json', dict(timestamp=datetime.now(timezone.utc).isoformat(),
            source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            command=[sys.executable, *sys.argv], cwd=str(ROOT), inputs_sha256=inputs,
            python_version=platform.python_version(), numpy_version=np.__version__,
            selection_rule='Frozen complete ordered_nonedge rooted6 necessary system, then its single triangular-prism flag zero face.',
            success_criterion='Explicit independent exact null vectors bound rational rank from above; prime elimination bounds it below; exact all-row primal and finite nonnegative domain.',
            falsification_criterion='Any nonzero exact residual, altered input, dependent free-coordinate minor, or missed/invalid domain point vetoes certificate.',
            independent_verification_requirement='Separate implementation reconstructs or checks all rows/vectors/domain; no self approval.',
            scope='Necessary local flag model only; prism-free conditional face does not exclude unrestricted target.',
            max_integer_attempts=args.max_integer_attempts, integer_enumeration_rule='Complete integer bounding rectangle only when at most declared attempt count; otherwise domain only.',
            numerical_acceptance='None: every certificate check uses integer/Fraction arithmetic.'))
        controls = [dict(terms=[[0, 1], [1, 2], [2, -1]], rhs=0), dict(terms=[[0, 2], [1, 4], [2, -2]], rhs=0)]
        rank, mod = echelon(controls, 3, 65521, deadline)
        need(rank['rank'] == 1 and len(mod) == 2, 'rank-deficient positive control')
        exact = [[reconstruct(value, 65521) for value in vector] for vector in mod]
        need(all(not any(residuals(controls, vector)) for vector in exact), 'null-vector positive control')
        bad = list(exact[0]); bad[0] += 1
        need(any(residuals(controls, bad)), 'corrupted null-vector control')
        data = read(RAW/'ordered_nonedge_model.json')
        added = read(RAW/'ordered_nonedge_prismfree_rows.json')
        primal = read(RAW/'ordered_nonedge_prismfree_primal.json')['exact_primal']
        rows, columns = data['equations'], len(data['variables'])
        unrestricted, _ = lift(rows, columns, deadline, out, 'unrestricted_nonedge')
        conditional_rows = [*rows, *added]
        conditional, basis = lift(conditional_rows, columns, deadline, out, 'prismfree_nonedge')
        need(primal is not None and min(primal) >= 0 and not any(residuals(conditional_rows, primal, affine=True)), 'preserved exact nonnegative primal')
        free = conditional['rank_lower_bound']['free_coordinates']
        origin, poly, bounds, inequalities, attempts = polygon(primal, basis, free, math.comb(97, 4), deadline)
        domain = dict(format='EXACT_ROOTED6_PRISMFREE_PARAMETER_DOMAIN_V1',
            free_coordinates=free, free_variables=[data['variables'][j] for j in free],
            parameters='Actual nonnegative integer counts of the two listed flagged induced graph classes per actual ordered nonedge.',
            origin=[ [value.numerator, value.denominator] for value in origin ],
            vertices=[[[value.numerator, value.denominator] for value in point] for point in poly],
            integer_bounding_rectangle=bounds, rectangle_attempts=attempts,
            inequalities_primitive_integer=inequalities, exact_integer_feasible_points=None,
            exact_integer_feasible_points_reason='Not enumerated yet.', graph_realizability_asserted=False)
        save(out/'prismfree_nonedge_domain_initial.json', domain)
        points, nonnegative_attempts, fractional_attempts = [], 0, 0
        if attempts <= args.max_integer_attempts:
            for a in tqdm(range(bounds[0][0], bounds[0][1]+1), desc='exact integer local domain', mininterval=5):
                check_deadline(deadline)
                for b in range(bounds[1][0], bounds[1][1]+1):
                    if not all(x*a+y*b+c >= 0 for x, y, c in inequalities):
                        continue
                    nonnegative_attempts += 1
                    values = [origin[j]+a*basis[0][j]+b*basis[1][j] for j in range(columns)]
                    if any(value.denominator != 1 for value in values):
                        fractional_attempts += 1
                        continue
                    integer_values = [int(value) for value in values]
                    need(min(integer_values) >= 0 and not any(residuals(conditional_rows, integer_values, affine=True)), 'every enumerated exact integer point')
                    points.append([a, b])
            domain.update(exact_integer_feasible_points=points, exact_integer_feasible_points_reason='Complete bounding rectangle independently reproducible from the rational polygon.',
                integer_count_vectors=len(points), nonnegative_rectangle_points=nonnegative_attempts,
                fractional_vectors_rejected=fractional_attempts, complete_integer_domain=True)
        else:
            domain.update(exact_integer_feasible_points_reason='Declared rectangle attempt limit exceeded; complete rational domain only.', complete_integer_domain=False)
        save(out/'prismfree_nonedge_domain.json', domain)
        summary = dict(status='CANDIDATE_EXACT_ROOTED6_PARAMETER_DOMAIN',
            timestamp=datetime.now(timezone.utc).isoformat(), target_resolution='UNKNOWN',
            unrestricted_exact_rank=unrestricted['exact_rational_rank'], unrestricted_exact_nullity=unrestricted['exact_nullity'],
            conditional_exact_rank=conditional['exact_rational_rank'], conditional_exact_nullity=conditional['exact_nullity'],
            conditional_free_variables=domain['free_variables'], complete_integer_domain=domain['complete_integer_domain'],
            integer_count_vectors=domain.get('integer_count_vectors'), integer_count_vectors_reason=domain['exact_integer_feasible_points_reason'],
            scope='Exact frozen necessary linear-system/domain statement only. Additional premise for conditional domain: no induced triangular prism anywhere in the hypothetical graph.',
            graph_realizability_asserted=False, independent_review=None, independent_review_reason='Pending separate artifact/derivation check.',
            elapsed_seconds=time.monotonic()-start, outputs_sha256={path.relative_to(ROOT).as_posix():sha(path) for path in out.iterdir() if path.is_file()})
        save(out/'summary.json', summary)
        print(json.dumps(summary), flush=True)
    except BaseException as error:
        save(out/'failure.json', dict(error=repr(error), elapsed_seconds=time.monotonic()-start, target_resolution='UNKNOWN'))
        raise


if __name__ == '__main__':
    main()
