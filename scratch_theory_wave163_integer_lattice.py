#!/usr/bin/env python3
"""Exact integer-lattice lift of the Wave163 count-slack control.

This script starts from the already frozen eight-dimensional nullspace.  It
intersects Z^8 with every order-8 and induced order-7 integrality congruence,
then imposes the endpoint normalization and the active nonnegative face.  A
small-dimensional exact LLL/Babai search looks for an integral pseudocount
near the known rational, compressed-positive-definite control.

It does not regenerate any locally admissible classes or identities.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Sequence


ROOT = Path(__file__).resolve().parent
KERNEL = ROOT / "scratch_theory_wave163_coupled_kernel_basis.json.gz"
CONTROL = ROOT / "scratch_theory_wave163_count_slack_exact_control.json"
COEFFICIENT_ARCHIVE = (
    ROOT / "external_conway99_research/attempts/wave147-alternative-lane/coefficients.json.gz"
)
OUTPUT = ROOT / "scratch_theory_wave163_integer_lattice.json"
PARAMETER_SCALE = 1_247_400
H_DELTA_MASK = 120568


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_gzip_json(path: Path) -> dict:
    with gzip.open(path, "rt", encoding="ascii") as handle:
        return json.load(handle)


def fstr(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def xgcd(left: int, right: int) -> tuple[int, int, int]:
    """Return nonnegative gcd and Bezout coefficients."""
    old_r, r = left, right
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_s, s = s, old_s - quotient * s
        old_t, t = t, old_t - quotient * t
    if old_r < 0:
        old_r, old_s, old_t = -old_r, -old_s, -old_t
    return old_r, old_s, old_t


def dot(left: Sequence[int | Fraction], right: Sequence[int | Fraction]) -> int | Fraction:
    return sum((x * y for x, y in zip(left, right, strict=True)), 0)


def mat_vec(matrix: Sequence[Sequence[int | Fraction]], vector: Sequence[int | Fraction]) -> list[int | Fraction]:
    return [dot(row, vector) for row in matrix]


def columns_to_rows(columns: Sequence[Sequence[int]]) -> list[list[int]]:
    return [list(row) for row in zip(*columns, strict=True)]


def rows_to_columns(rows: Sequence[Sequence[int]]) -> list[list[int]]:
    return [list(column) for column in zip(*rows, strict=True)]


def combine_columns(matrix: Sequence[Sequence[int]], transform: Sequence[Sequence[int]]) -> list[list[int]]:
    """Return matrix * transform, both represented by ordinary rows."""
    return [
        [sum(row[k] * transform[k][j] for k in range(len(transform))) for j in range(len(transform[0]))]
        for row in matrix
    ]


def unimodular_gcd_transform(row: Sequence[int]) -> tuple[list[list[int]], int]:
    """Construct V unimodular with row*V=(gcd(row),0,...,0)."""
    size = len(row)
    transform = [[int(i == j) for j in range(size)] for i in range(size)]
    reduced = list(map(int, row))
    for column in range(1, size):
        left, right = reduced[0], reduced[column]
        if right == 0:
            continue
        divisor, s, t = xgcd(left, right)
        require(divisor > 0, "zero gcd in nonzero two-column reduction")
        two = ((s, -right // divisor), (t, left // divisor))
        old0 = [transform[i][0] for i in range(size)]
        oldj = [transform[i][column] for i in range(size)]
        for i in range(size):
            transform[i][0] = old0[i] * two[0][0] + oldj[i] * two[1][0]
            transform[i][column] = old0[i] * two[0][1] + oldj[i] * two[1][1]
        reduced[0], reduced[column] = divisor, 0
    if reduced[0] < 0:
        for i in range(size):
            transform[i][0] *= -1
        reduced[0] *= -1
    check = [sum(row[i] * transform[i][j] for i in range(size)) for j in range(size)]
    require(check == [reduced[0]] + [0] * (size - 1), "gcd transform verification failed")
    return transform, reduced[0]


def nearest_integer(value: Fraction) -> int:
    floor = value.numerator // value.denominator
    if value - floor < Fraction(1, 2):
        return floor
    return floor + 1


def gram_schmidt(columns: Sequence[Sequence[int]]) -> tuple[list[list[Fraction]], list[list[Fraction]], list[Fraction]]:
    size = len(columns)
    stars: list[list[Fraction]] = []
    mu = [[Fraction(0) for _ in range(size)] for _ in range(size)]
    norms: list[Fraction] = []
    for i, column in enumerate(columns):
        star = list(map(Fraction, column))
        for j in range(i):
            require(norms[j] > 0, "dependent lattice basis")
            mu[i][j] = Fraction(dot(column, stars[j]), norms[j])
            star = [value - mu[i][j] * old for value, old in zip(star, stars[j], strict=True)]
        norm = Fraction(dot(star, star))
        require(norm > 0, "dependent lattice basis after Gram-Schmidt")
        stars.append(star)
        norms.append(norm)
    return stars, mu, norms


def lll_reduce(columns: Sequence[Sequence[int]], delta: Fraction = Fraction(3, 4)) -> list[list[int]]:
    """Exact LLL for a full-column-rank integer basis in ambient dimension <=8."""
    basis = [list(map(int, column)) for column in columns]
    if len(basis) <= 1:
        return basis
    stars, mu, norms = gram_schmidt(basis)
    k = 1
    while k < len(basis):
        for j in range(k - 1, -1, -1):
            quotient = nearest_integer(mu[k][j])
            if quotient:
                basis[k] = [x - quotient * y for x, y in zip(basis[k], basis[j], strict=True)]
                stars, mu, norms = gram_schmidt(basis)
        if norms[k] >= (delta - mu[k][k - 1] * mu[k][k - 1]) * norms[k - 1]:
            k += 1
        else:
            basis[k], basis[k - 1] = basis[k - 1], basis[k]
            stars, mu, norms = gram_schmidt(basis)
            k = max(1, k - 1)
    return basis


def lattice_intersect_congruence(
    basis_columns: Sequence[Sequence[int]], coefficient: Sequence[int], modulus: int
) -> tuple[list[list[int]], int]:
    """Intersect B Z^n with coefficient*t=0 mod modulus."""
    require(modulus > 0, "nonpositive modulus")
    row_on_basis = [int(dot(coefficient, column)) for column in basis_columns]
    common = math.gcd(modulus, *row_on_basis)
    index = modulus // common
    if index == 1:
        return [list(column) for column in basis_columns], 1
    transform, divisor = unimodular_gcd_transform(row_on_basis)
    require(math.gcd(modulus, divisor) == common, "congruence index mismatch")
    for row in transform:
        row[0] *= index
    basis_rows = columns_to_rows(basis_columns)
    updated = rows_to_columns(combine_columns(basis_rows, transform))
    updated = lll_reduce(updated)
    for column in updated:
        require(dot(coefficient, column) % modulus == 0, "updated lattice violates congruence")
    return updated, index


def determinant_bareiss(rows: Sequence[Sequence[int]]) -> int:
    work = [list(map(int, row)) for row in rows]
    size = len(work)
    sign = 1
    denominator = 1
    for pivot in range(size - 1):
        if work[pivot][pivot] == 0:
            swap = next((row for row in range(pivot + 1, size) if work[row][pivot]), None)
            require(swap is not None, "singular determinant input")
            work[pivot], work[swap] = work[swap], work[pivot]
            sign *= -1
        value = work[pivot][pivot]
        for row in range(pivot + 1, size):
            for column in range(pivot + 1, size):
                numerator = work[row][column] * value - work[row][pivot] * work[pivot][column]
                require(numerator % denominator == 0, "Bareiss exact division failed")
                work[row][column] = numerator // denominator
        denominator = value
    return sign * work[-1][-1]


def solve_affine_equations(
    basis_columns: Sequence[Sequence[int]], equations: Sequence[tuple[Sequence[int], int]]
) -> tuple[list[int], list[list[int]], list[int]]:
    """Solve equations on BZ^n, returning one point and a kernel basis."""
    ambient = len(basis_columns[0])
    particular = [0] * ambient
    directions = [list(column) for column in basis_columns]
    divisors = []
    for coefficient, rhs in equations:
        residual = rhs - int(dot(coefficient, particular))
        row = [int(dot(coefficient, column)) for column in directions]
        transform, divisor = unimodular_gcd_transform(row)
        require(divisor > 0 and residual % divisor == 0, "affine equation has no lattice solution")
        transformed = rows_to_columns(combine_columns(columns_to_rows(directions), transform))
        multiplier = residual // divisor
        particular = [x + multiplier * y for x, y in zip(particular, transformed[0], strict=True)]
        directions = transformed[1:]
        divisors.append(divisor)
        require(dot(coefficient, particular) == rhs, "affine particular check failed")
        require(all(dot(coefficient, column) == 0 for column in directions), "affine kernel check failed")
        directions = lll_reduce(directions)
    return particular, directions, divisors


def babai_nearest(particular: Sequence[int], directions: Sequence[Sequence[int]], target: Sequence[Fraction]) -> tuple[list[int], list[int]]:
    basis = lll_reduce(directions)
    stars, _, norms = gram_schmidt(basis)
    residual = [Fraction(t) - p for t, p in zip(target, particular, strict=True)]
    coefficients = [0] * len(basis)
    for index in range(len(basis) - 1, -1, -1):
        value = Fraction(dot(residual, stars[index]), norms[index])
        coefficient = nearest_integer(value)
        coefficients[index] = coefficient
        residual = [x - coefficient * y for x, y in zip(residual, basis[index], strict=True)]
    point = list(particular)
    for coefficient, column in zip(coefficients, basis, strict=True):
        point = [x + coefficient * y for x, y in zip(point, column, strict=True)]
    return point, coefficients


def ldlt_positive_definite(matrix: Sequence[Sequence[Fraction]]) -> list[Fraction]:
    size = len(matrix)
    lower = [[Fraction(0) for _ in range(size)] for _ in range(size)]
    diagonal = [Fraction(0)] * size
    for i in range(size):
        lower[i][i] = 1
        diagonal[i] = matrix[i][i] - sum(lower[i][k] ** 2 * diagonal[k] for k in range(i))
        require(diagonal[i] > 0, f"nonpositive compressed LDL pivot {i}")
        for row in range(i + 1, size):
            residual = matrix[row][i] - sum(lower[row][k] * lower[i][k] * diagonal[k] for k in range(i))
            lower[row][i] = residual / diagonal[i]
    return diagonal


def class_streams(payload: dict) -> dict[int, tuple[int, ...]]:
    families = []
    for name in ("ordered_edge", "ordered_nonedge"):
        streams = {order: [] for order in range(5, 9)}
        for record in payload["families"][name]["class_coefficients"]:
            streams[int(record["order"])].append(int(record["canonical_mask"]))
        families.append({order: tuple(values) for order, values in streams.items()})
    require(families[0] == families[1], "family class streams differ")
    require(tuple(len(families[0][order]) for order in range(5, 9)) == (21, 62, 208, 916), "class census drift")
    return families[0]


def main() -> int:
    kernel = load_gzip_json(KERNEL)
    control = load_json(CONTROL)
    coefficients = load_gzip_json(COEFFICIENT_ARCHIVE)

    nullspace = [[Fraction(0) for _ in range(8)] for _ in range(917)]
    for column, entries in enumerate(kernel["universal_nullspace_basis_sparse"]):
        for row, value in entries:
            nullspace[int(row)][column] = Fraction(value)
    free_columns = list(map(int, kernel["universal_free_columns"]))
    require(all(nullspace[free_columns[i]][j] == int(i == j) for i in range(8) for j in range(8)), "free identity drift")

    streams = class_streams(coefficients)
    index7 = {mask: index for index, mask in enumerate(streams[7])}
    index8 = {mask: index for index, mask in enumerate(streams[8])}
    deletion: list[dict[int, int] | None] = [None] * 208
    for record in coefficients["order7_to_order8_deletion_equations"]:
        require(int(record["left_multiplier"]) == 92, "deletion multiplier drift")
        deletion[index7[int(record["order7_mask"])]] = {
            index8[int(mask)]: int(multiplicity)
            for mask, multiplicity in record["terms_order8_mask_multiplicity"]
        }
    require(all(row is not None for row in deletion), "missing deletion row")
    x8_forms = nullspace[1:]
    x7_forms = []
    for row in deletion:
        assert row is not None
        x7_forms.append([
            sum((Fraction(mult) * x8_forms[column][j] for column, mult in row.items()), Fraction(0)) / 92
            for j in range(8)
        ])

    # The free coordinates force t in Z^8.  Intersect with all remaining
    # rational-count integrality conditions, recording the exact index growth.
    lattice = [[int(i == j) for i in range(8)] for j in range(8)]
    steps = []
    for family, forms in (("x8", x8_forms), ("x7", x7_forms)):
        for row_index, form in enumerate(forms):
            denominator = math.lcm(*(value.denominator for value in form))
            coefficient = [int(value * denominator) for value in form]
            lattice, index = lattice_intersect_congruence(lattice, coefficient, denominator)
            if index > 1:
                steps.append({"family": family, "row": row_index, "modulus": denominator, "index": index})
    determinant = abs(determinant_bareiss(columns_to_rows(lattice)))
    require(determinant == math.prod(step["index"] for step in steps), "lattice index product mismatch")

    # Normalization and the unique nonstructural active count face.
    endpoint_equation = ([0, 0, -1, 3, 1, 0, 0, 0], PARAMETER_SCALE)
    active_face_equation = ([0, 0, 0, 0, 0, 0, 0, 1], 964_656)
    particular, directions, affine_divisors = solve_affine_equations(
        lattice, (endpoint_equation, active_face_equation)
    )
    require(len(directions) == 6, "affine dimension drift")

    target = [Fraction(value) for value in control["certificate"]["t_free_x8_coordinates"]]
    candidate, babai_coefficients = babai_nearest(particular, directions, target)

    augmented = [Fraction(dot(row, candidate)) for row in nullspace]
    require(augmented[0] == 1, "candidate normalization failed")
    require(all(value.denominator == 1 for value in augmented), "nonintegral order-8 candidate")
    x8 = augmented[1:]
    x7 = [Fraction(dot(row, candidate)) for row in x7_forms]
    require(all(value.denominator == 1 for value in x7), "nonintegral order-7 candidate")

    qmap = [[Fraction(value) for value in row] for row in kernel["compressed_quotient_map_57_by_8"]]
    scales = {
        int(root): [Fraction(value) for value in values]
        for root, values in control["certificate"]["direction_column_scales"].items()
    }
    matrices = {}
    diagonals = {}
    offset = 0
    for root, size in ((3, 6), (12, 8)):
        matrix = [[Fraction(0) for _ in range(size)] for _ in range(size)]
        for left in range(size):
            for right in range(left, size):
                raw = Fraction(dot(qmap[offset], candidate))
                value = raw / (scales[root][left] * scales[root][right])
                matrix[left][right] = matrix[right][left] = value
                offset += 1
        matrices[root] = matrix
        diagonals[root] = ldlt_positive_definite(matrix)
    require(offset == 57, "compressed quotient offset drift")

    certificate = {
        "t_integral_free_x8_coordinates": candidate,
        "target_rational_t": list(map(fstr, target)),
        "candidate_minus_target": list(map(fstr, [Fraction(x) - y for x, y in zip(candidate, target, strict=True)])),
        "endpoint_equation": "-t2+3*t3+t4=1247400",
        "active_face_equation": "t7=964656",
        "all_x8_integral": True,
        "all_x7_integral": True,
        "all_x8_nonnegative": all(value >= 0 for value in x8),
        "all_x7_nonnegative": all(value >= 0 for value in x7),
        "x8_negative_indices": [index for index, value in enumerate(x8) if value < 0],
        "x7_negative_indices": [index for index, value in enumerate(x7) if value < 0],
        "x8_zero_indices": [index for index, value in enumerate(x8) if value == 0],
        "x7_zero_indices": [index for index, value in enumerate(x7) if value == 0],
        "minimum_positive_x8": str(min(value for value in x8 if value > 0)),
        "minimum_positive_x7": str(min(value for value in x7 if value > 0)),
        "sum_x8": str(sum(x8)),
        "sum_x7": str(sum(x7)),
        "H_delta_count": str(x7[index7[H_DELTA_MASK]]),
        "compressed_positive_definite": True,
        "compressed_ldlt_positive_diagonals": {
            str(root): list(map(fstr, diagonals[root])) for root in (3, 12)
        },
        "babai_coefficients_in_reduced_affine_basis": babai_coefficients,
    }
    result = {
        "format": "wave163-integer-lattice-control-v1",
        "claim_label": (
            "EXACT_INTEGRAL_COMPRESSED_PRIMAL_FEASIBLE"
            if certificate["all_x8_nonnegative"] and certificate["all_x7_nonnegative"]
            else "EXACT_INTEGRAL_AFFINE_LATTICE_POINT_BUT_COUNT_NEGATIVE"
        ),
        "inputs_sha256": {
            path.name if path.parent == ROOT else str(path.relative_to(ROOT)): sha256_file(path)
            for path in (KERNEL, CONTROL, COEFFICIENT_ARCHIVE)
        },
        "integrality_lattice": {
            "ambient_dimension": 8,
            "nontrivial_congruence_steps": len(steps),
            "step_records": steps,
            "index_in_Z8": str(determinant),
            "reduced_basis_columns": lattice,
            "affine_equation_divisors": affine_divisors,
            "affine_dimension_after_endpoint_and_face": 6,
            "affine_particular_point": particular,
            "reduced_affine_direction_columns": directions,
        },
        "certificate": certificate,
        "scope_boundary": {
            "full_four_root_blocks": "NOT_TESTED",
            "graph_realizability": "NOT_CLAIMED",
            "integer_counts_are_not_graph_realization": True,
            "Conway_99": "UNKNOWN",
        },
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(OUTPUT),
        "claim_label": result["claim_label"],
        "lattice_index": str(determinant),
        "congruence_steps": len(steps),
        "x8_negative": len(certificate["x8_negative_indices"]),
        "x7_negative": len(certificate["x7_negative_indices"]),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
