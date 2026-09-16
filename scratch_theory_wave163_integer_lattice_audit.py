#!/usr/bin/env python3
"""Clean-room audit of the Wave163 integral compressed control.

No discovery module is imported.  Besides reconstructing every count and
compressed matrix, this verifier proves completeness of the saved integrality
lattice: its columns satisfy every congruence and its determinant equals an
independently computed prime-primary image order.
"""

from __future__ import annotations

import gzip
import hashlib
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Sequence


ROOT = Path(__file__).resolve().parent
CERTIFICATE = ROOT / "scratch_theory_wave163_integer_lattice.json"
KERNEL = ROOT / "scratch_theory_wave163_coupled_kernel_basis.json.gz"
CONTROL = ROOT / "scratch_theory_wave163_count_slack_exact_control.json"
BASE_AUDIT = ROOT / "scratch_theory_wave163_coupled_pencil_independent_audit.json"
COEFFICIENT_ARCHIVE = (
    ROOT / "external_conway99_research/attempts/wave147-alternative-lane/coefficients.json.gz"
)
OUTPUT = ROOT / "scratch_theory_wave163_integer_lattice_audit.json"
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


def dot(left: Sequence[int | Fraction], right: Sequence[int | Fraction]) -> int | Fraction:
    return sum((x * y for x, y in zip(left, right, strict=True)), 0)


def determinant_fraction(rows: Sequence[Sequence[int | Fraction]]) -> Fraction:
    work = [list(map(Fraction, row)) for row in rows]
    size = len(work)
    require(all(len(row) == size for row in work), "determinant input not square")
    result = Fraction(1)
    for column in range(size):
        pivot = next((row for row in range(column, size) if work[row][column]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            work[pivot], work[column] = work[column], work[pivot]
            result *= -1
        value = work[column][column]
        result *= value
        for row in range(column + 1, size):
            if not work[row][column]:
                continue
            factor = work[row][column] / value
            for entry in range(column + 1, size):
                work[row][entry] -= factor * work[column][entry]
    return result


def inverse_fraction(rows: Sequence[Sequence[int]]) -> list[list[Fraction]]:
    size = len(rows)
    work = [list(map(Fraction, row)) + [Fraction(int(i == j)) for j in range(size)] for i, row in enumerate(rows)]
    for column in range(size):
        pivot = next((row for row in range(column, size) if work[row][column]), None)
        require(pivot is not None, "singular inverse input")
        work[pivot], work[column] = work[column], work[pivot]
        value = work[column][column]
        work[column] = [entry / value for entry in work[column]]
        for row in range(size):
            if row == column or not work[row][column]:
                continue
            factor = work[row][column]
            work[row] = [left - factor * right for left, right in zip(work[row], work[column], strict=True)]
    return [row[size:] for row in work]


def factor_integer(value: int) -> dict[int, int]:
    require(value > 0, "factorization input nonpositive")
    result = {}
    divisor = 2
    while divisor * divisor <= value:
        while value % divisor == 0:
            result[divisor] = result.get(divisor, 0) + 1
            value //= divisor
        divisor = 3 if divisor == 2 else divisor + 2
    if value > 1:
        result[value] = result.get(value, 0) + 1
    return result


def pvaluation(value: int, prime: int, cap: int) -> int:
    value %= prime**cap
    if value == 0:
        return cap
    valuation = 0
    while value % prime == 0:
        value //= prime
        valuation += 1
    return valuation


def primary_smith_valuations(matrix: Sequence[Sequence[int]], prime: int, exponent: int) -> list[int]:
    """Diagonal valuations over Z/(p^exponent), using unit row/column moves."""
    modulus = prime**exponent
    work = [[int(value) % modulus for value in row] for row in matrix]
    rows = len(work)
    columns = len(work[0])
    valuations = []
    pivot_index = 0
    while pivot_index < min(rows, columns):
        choice = None
        best = exponent
        for row in range(pivot_index, rows):
            for column in range(pivot_index, columns):
                valuation = pvaluation(work[row][column], prime, exponent)
                if valuation < best:
                    best = valuation
                    choice = (row, column)
        if choice is None:
            break
        row, column = choice
        work[pivot_index], work[row] = work[row], work[pivot_index]
        for old_row in work:
            old_row[pivot_index], old_row[column] = old_row[column], old_row[pivot_index]
        power = prime**best
        unit = (work[pivot_index][pivot_index] // power) % modulus
        inverse = pow(unit, -1, modulus)
        work[pivot_index] = [(value * inverse) % modulus for value in work[pivot_index]]
        require(work[pivot_index][pivot_index] == power, "primary pivot normalization failed")
        reduced_modulus = prime ** (exponent - best)
        for other in range(rows):
            if other == pivot_index:
                continue
            entry = work[other][pivot_index]
            require(entry % power == 0, "primary row entry has smaller valuation")
            multiplier = (entry // power) % reduced_modulus
            work[other] = [
                (left - multiplier * right) % modulus
                for left, right in zip(work[other], work[pivot_index], strict=True)
            ]
        for other in range(columns):
            if other == pivot_index:
                continue
            entry = work[pivot_index][other]
            require(entry % power == 0, "primary column entry has smaller valuation")
            multiplier = (entry // power) % reduced_modulus
            for old_row in work:
                old_row[other] = (old_row[other] - multiplier * old_row[pivot_index]) % modulus
        require(
            all(work[row][pivot_index] == 0 for row in range(rows) if row != pivot_index)
            and all(work[pivot_index][column] == 0 for column in range(columns) if column != pivot_index),
            "primary diagonal clearing failed",
        )
        valuations.append(best)
        pivot_index += 1
    return valuations


def class_streams(payload: dict) -> dict[int, tuple[int, ...]]:
    families = []
    for name in ("ordered_edge", "ordered_nonedge"):
        streams = {order: [] for order in range(5, 9)}
        for record in payload["families"][name]["class_coefficients"]:
            streams[int(record["order"])].append(int(record["canonical_mask"]))
        families.append({order: tuple(values) for order, values in streams.items()})
    require(families[0] == families[1], "family streams differ")
    require(tuple(len(families[0][order]) for order in range(5, 9)) == (21, 62, 208, 916), "frozen census drift")
    return families[0]


def main() -> int:
    artifact = load_json(CERTIFICATE)
    kernel = load_gzip_json(KERNEL)
    control = load_json(CONTROL)
    base_audit = load_json(BASE_AUDIT)
    coefficients = load_gzip_json(COEFFICIENT_ARCHIVE)
    require(artifact["claim_label"] == "EXACT_INTEGRAL_COMPRESSED_PRIMAL_FEASIBLE", "certificate claim drift")
    require(base_audit["claim_label"] == "VERIFIED_SCOPED_COMPRESSED_CONIC_NULL", "base audit claim drift")
    for path in (KERNEL, CONTROL, COEFFICIENT_ARCHIVE):
        key = path.name if path.parent == ROOT else str(path.relative_to(ROOT))
        require(artifact["inputs_sha256"][key] == sha256_file(path), f"input binding drift: {key}")

    nullspace = [[Fraction(0) for _ in range(8)] for _ in range(917)]
    for column, entries in enumerate(kernel["universal_nullspace_basis_sparse"]):
        for row, value in entries:
            nullspace[int(row)][column] = Fraction(value)
    free_columns = list(map(int, kernel["universal_free_columns"]))
    require(len(free_columns) == 8, "free column count drift")
    require(all(nullspace[free_columns[i]][j] == int(i == j) for i in range(8) for j in range(8)), "free identity failed")

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
    all_forms = x8_forms + x7_forms

    # Independent finite-abelian image calculation.  If D clears all
    # denominators, count integrality is C*t=0 mod D.  Prime-primary Smith
    # valuations give the exact index of this kernel in Z^8.
    common_denominator = math.lcm(*(value.denominator for row in all_forms for value in row))
    congruence_matrix = [[int(common_denominator * value) for value in row] for row in all_forms]
    primary = {}
    independently_computed_index = 1
    for prime, exponent in factor_integer(common_denominator).items():
        valuations = primary_smith_valuations(congruence_matrix, prime, exponent)
        image_exponent = sum(exponent - value for value in valuations)
        independently_computed_index *= prime**image_exponent
        primary[str(prime)] = {
            "modulus_exponent": exponent,
            "nonzero_smith_valuations": valuations,
            "image_order_exponent": image_exponent,
        }

    lattice_columns = [list(map(int, column)) for column in artifact["integrality_lattice"]["reduced_basis_columns"]]
    require(len(lattice_columns) == 8 and all(len(column) == 8 for column in lattice_columns), "lattice basis shape drift")
    lattice_rows = [list(row) for row in zip(*lattice_columns, strict=True)]
    lattice_determinant = abs(determinant_fraction(lattice_rows))
    require(lattice_determinant.denominator == 1, "nonintegral lattice determinant")
    require(int(lattice_determinant) == independently_computed_index, "lattice index not independently minimal")
    require(str(int(lattice_determinant)) == artifact["integrality_lattice"]["index_in_Z8"], "stored lattice index drift")
    require(
        all(Fraction(dot(form, column)).denominator == 1 for form in all_forms for column in lattice_columns),
        "saved lattice is not contained in count-integrality kernel",
    )

    # Check that the stored affine directions give the full, not merely a
    # finite-index, homogeneous solution lattice in coordinates of L.
    inverse_lattice = inverse_fraction(lattice_rows)
    particular = list(map(int, artifact["integrality_lattice"]["affine_particular_point"]))
    direction_columns = [list(map(int, column)) for column in artifact["integrality_lattice"]["reduced_affine_direction_columns"]]
    particular_coordinates = [Fraction(dot(row, particular)) for row in inverse_lattice]
    coordinate_columns = [[Fraction(dot(row, column)) for row in inverse_lattice] for column in direction_columns]
    require(all(value.denominator == 1 for value in particular_coordinates), "particular point not in full lattice")
    require(all(value.denominator == 1 for column in coordinate_columns for value in column), "direction not in full lattice")
    coordinate_columns_int = [[int(value) for value in column] for column in coordinate_columns]
    endpoint_coeff = [0, 0, -1, 3, 1, 0, 0, 0]
    face_coeff = [0, 0, 0, 0, 0, 0, 0, 1]
    equation_rows = [
        [int(dot(coefficient, column)) for column in lattice_columns]
        for coefficient in (endpoint_coeff, face_coeff)
    ]
    equation_gram = [
        [Fraction(dot(left, right)) for right in equation_rows]
        for left in equation_rows
    ]
    require(determinant_fraction(equation_gram) != 0, "affine equation rank below two")
    require(
        dot(endpoint_coeff, particular) == PARAMETER_SCALE and dot(face_coeff, particular) == 964_656,
        "affine particular equations failed",
    )
    require(
        all(dot(coefficient, column) == 0 for coefficient in (endpoint_coeff, face_coeff) for column in direction_columns),
        "affine direction equation failed",
    )
    # A rank-six sublattice of Z^8 is saturated iff the gcd of all maximal
    # minors is one.  Saturation plus the same rational kernel proves equality.
    coordinate_rows = [list(row) for row in zip(*coordinate_columns_int, strict=True)]
    maximal_minors = []
    for selected in itertools.combinations(range(8), 6):
        minor = [coordinate_rows[row] for row in selected]
        maximal_minors.append(abs(int(determinant_fraction(minor))))
    saturation_gcd = math.gcd(*maximal_minors)
    require(saturation_gcd == 1, "affine homogeneous basis is not saturated")
    require(any(value for value in maximal_minors), "affine homogeneous rank below six")

    certificate = artifact["certificate"]
    candidate = list(map(int, certificate["t_integral_free_x8_coordinates"]))
    coefficients_babai = list(map(int, certificate["babai_coefficients_in_reduced_affine_basis"]))
    rebuilt_candidate = list(particular)
    for multiplier, column in zip(coefficients_babai, direction_columns, strict=True):
        rebuilt_candidate = [x + multiplier * y for x, y in zip(rebuilt_candidate, column, strict=True)]
    require(candidate == rebuilt_candidate, "candidate affine decomposition failed")
    require(dot(endpoint_coeff, candidate) == PARAMETER_SCALE, "candidate endpoint equation failed")
    require(dot(face_coeff, candidate) == 964_656, "candidate active face equation failed")

    augmented = [Fraction(dot(row, candidate)) for row in nullspace]
    require(augmented[0] == 1, "augmented constant failed")
    x8 = augmented[1:]
    x7 = [Fraction(dot(row, candidate)) for row in x7_forms]
    require(all(value.denominator == 1 and value >= 0 for value in x8), "order-8 integral nonnegativity failed")
    require(all(value.denominator == 1 and value >= 0 for value in x7), "order-7 integral nonnegativity failed")
    require(sum(x8) == math.comb(99, 8), "order-8 total failed")
    require(sum(x7) == math.comb(99, 7), "order-7 total failed")
    zero8 = [index for index, value in enumerate(x8) if value == 0]
    zero7 = [index for index, value in enumerate(x7) if value == 0]
    require(zero8 == list(map(int, certificate["x8_zero_indices"])), "order-8 zero support drift")
    require(zero7 == list(map(int, certificate["x7_zero_indices"])), "order-7 zero support drift")
    require(min(value for value in x8 if value > 0) == Fraction(certificate["minimum_positive_x8"]), "minimum x8 drift")
    require(min(value for value in x7 if value > 0) == Fraction(certificate["minimum_positive_x7"]), "minimum x7 drift")
    require(x7[index7[H_DELTA_MASK]] == 0, "H_delta is nonzero")

    # Sylvester's criterion independently certifies the two compressed blocks.
    qmap = [[Fraction(value) for value in row] for row in kernel["compressed_quotient_map_57_by_8"]]
    scales = {
        int(root): [Fraction(value) for value in values]
        for root, values in control["certificate"]["direction_column_scales"].items()
    }
    leading_minors = {}
    ldlt_ratios = {}
    offset = 0
    for root, size in ((3, 6), (12, 8)):
        matrix = [[Fraction(0) for _ in range(size)] for _ in range(size)]
        for left in range(size):
            for right in range(left, size):
                value = Fraction(dot(qmap[offset], candidate)) / (scales[root][left] * scales[root][right])
                matrix[left][right] = matrix[right][left] = value
                offset += 1
        minors = [determinant_fraction([row[:order] for row in matrix[:order]]) for order in range(1, size + 1)]
        require(all(value > 0 for value in minors), f"root {root} fails Sylvester positivity")
        pivots = [minors[0]] + [minors[index] / minors[index - 1] for index in range(1, size)]
        require(list(map(fstr, pivots)) == certificate["compressed_ldlt_positive_diagonals"][str(root)], "stored LDL pivot drift")
        leading_minors[str(root)] = list(map(fstr, minors))
        ldlt_ratios[str(root)] = list(map(fstr, pivots))
    require(offset == 57, "compressed quotient offset drift")

    result = {
        "format": "wave163-integer-lattice-control-independent-audit-v1",
        "claim_label": "INDEPENDENT_EXACT_INTEGRAL_COMPRESSED_FEASIBILITY_PASS",
        "inputs_sha256": {
            path.name if path.parent == ROOT else str(path.relative_to(ROOT)): sha256_file(path)
            for path in (CERTIFICATE, KERNEL, CONTROL, BASE_AUDIT, COEFFICIENT_ARCHIVE)
        },
        "frozen_census": {"order7": 208, "order8": 916},
        "integrality_lattice_audit": {
            "common_congruence_denominator": common_denominator,
            "prime_primary_smith_data": primary,
            "independent_kernel_index": str(independently_computed_index),
            "saved_basis_absolute_determinant": str(int(lattice_determinant)),
            "basis_satisfies_all_1124_count_congruences": True,
            "therefore_saved_basis_is_full_integrality_kernel": True,
        },
        "affine_lattice_audit": {
            "endpoint_equation": "-t2+3*t3+t4=1247400",
            "active_face_equation": "t7=964656",
            "dimension": 6,
            "maximal_minor_gcd_in_integrality_lattice_coordinates": saturation_gcd,
            "full_affine_solution_lattice_verified": True,
            "candidate_decomposition_verified": True,
        },
        "count_audit": {
            "all_order8_nonnegative_integers": True,
            "all_order7_nonnegative_integers": True,
            "order8_zero_indices": zero8,
            "order7_zero_indices": zero7,
            "order7_zero_masks": [streams[7][index] for index in zero7],
            "minimum_positive_order8": str(min(value for value in x8 if value > 0)),
            "minimum_positive_order7": str(min(value for value in x7 if value > 0)),
            "sum_order8": str(sum(x8)),
            "sum_order7": str(sum(x7)),
            "H_delta_count": "0",
            "endpoint_n3": 4158,
            "endpoint_prism_count_from_n3_plus_3P_equals_4158": "0",
            "sum_E0_from_6P_plus_H_delta": "0",
        },
        "compressed_psd_audit": {
            "method": "Sylvester leading-principal-minor criterion over Q",
            "root3_and_root12_all_leading_minors_positive": True,
            "leading_principal_minors": leading_minors,
            "successive_minor_ratios_match_stored_ldlt_pivots": ldlt_ratios,
        },
        "scope_boundary": {
            "integer_pseudocounts_are_not_a_graph": True,
            "full_four_root_covariance_blocks": "NOT_TESTED",
            "higher_order_or_realizability_constraints": "NOT_TESTED",
            "positive_E0_lower_bound_from_this_restricted_lane": "IMPOSSIBLE",
            "Conway_99": "UNKNOWN",
        },
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("INDEPENDENT_EXACT_INTEGRAL_COMPRESSED_FEASIBILITY_PASS")
    print(json.dumps({
        "output": str(OUTPUT),
        "common_denominator": common_denominator,
        "integrality_lattice_index": str(independently_computed_index),
        "prime_primary": primary,
        "affine_saturation_gcd": saturation_gcd,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
