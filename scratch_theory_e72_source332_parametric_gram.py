"""Resolve the sole one-dimensional E72 macro Gram system exactly.

The diagonal and overlap equations leave one rational Gram parameter for
source row 332.  Actual disjoint-fibre block totals are integers in [0, 16].
This script writes the affine solution, enumerates every parameter value
allowed by those integrality/range constraints, and checks PSD and the full
compression row sums using exact ``Fraction`` arithmetic.
"""

from __future__ import annotations

from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path

from scratch_theory_local_psd_filter import bilinear_coefficients
from scratch_theory_unsigned_kernel_filter import (
    nullspace,
    psd_by_principal_minors,
    rref,
)


INPUT = Path("scratch_general_e72_q3_gram_fast_expansion_macro_catalog.json")
OUTPUT = Path("scratch_theory_e72_source332_parametric_gram.json")


def fstr(value: Fraction) -> str:
    return str(value)


def affine_dot(coefficients, constants, directions):
    return (
        sum((a * b for a, b in zip(coefficients, constants)), Fraction(0)),
        sum((a * b for a, b in zip(coefficients, directions)), Fraction(0)),
    )


def matrix_from_parameters(parameters, dimension):
    matrix = [[Fraction(0) for _ in range(dimension)] for _ in range(dimension)]
    positions = [
        (left, right)
        for left in range(dimension)
        for right in range(left, dimension)
    ]
    for value, (left, right) in zip(parameters, positions):
        matrix[left][right] = matrix[right][left] = value
    return matrix


def main():
    raw = INPUT.read_bytes()
    source = json.loads(raw)
    matches = [
        entry for entry in source["macro_entries"]
        if entry["source_row_index"] == 332
        and entry["state_orbit_number"] == 0
        and entry["signature_stabilizer_canonical"]
    ]
    assert len(matches) == 1
    entry = matches[0]
    supports = tuple(tuple(item["support"]) for item in entry["exceptional_supports"])
    deficits = tuple(int(item["deficit"]) for item in entry["exceptional_supports"])
    incidence_t = [
        [int(group in support) for support in supports]
        for group in range(7)
    ]
    basis_columns = nullspace(incidence_t)
    dimension = len(basis_columns)
    W = [
        [basis_columns[column][row] for column in range(dimension)]
        for row in range(len(supports))
    ]
    coefficients = []
    targets = []
    constraint_names = []
    for index, deficit in enumerate(deficits):
        coefficients.append(bilinear_coefficients(W[index], W[index]))
        targets.append(Fraction(2 * deficit))
        constraint_names.append(["diagonal", index])
    overlap = {
        tuple(sorted((int(left), int(right)))): int(value)
        for left, right, value in entry["overlap_block_totals"]
    }
    for pair in sorted(overlap):
        left, right = pair
        coefficients.append(bilinear_coefficients(W[left], W[right]))
        targets.append(Fraction(-overlap[pair]))
        constraint_names.append(["overlap", left, right])

    variable_count = dimension * (dimension + 1) // 2
    augmented = [list(row) + [target] for row, target in zip(coefficients, targets)]
    reduced, pivots_augmented = rref(augmented)
    assert not any(
        all(not value for value in row[:variable_count]) and row[variable_count]
        for row in reduced
    )
    pivots = [value for value in pivots_augmented if value < variable_count]
    free = [value for value in range(variable_count) if value not in pivots]
    assert len(free) == 1
    free_variable = free[0]
    constants = [Fraction(0) for _ in range(variable_count)]
    directions = [Fraction(0) for _ in range(variable_count)]
    directions[free_variable] = 1
    pivot_row = {pivot: row for row, pivot in enumerate(pivots)}
    for pivot in pivots:
        row = reduced[pivot_row[pivot]]
        constants[pivot] = row[variable_count]
        directions[pivot] = -row[free_variable]

    # Verify the symbolic affine solution against every original equation.
    for row, target in zip(coefficients, targets):
        constant, direction = affine_dot(row, constants, directions)
        assert constant == target and direction == 0

    H_constant = matrix_from_parameters(constants, dimension)
    H_direction = matrix_from_parameters(directions, dimension)
    disjoint_affine = []
    for left, right in itertools.combinations(range(len(supports)), 2):
        if set(supports[left]) & set(supports[right]):
            continue
        z_constant, z_direction = affine_dot(
            bilinear_coefficients(W[left], W[right]), constants, directions
        )
        disjoint_affine.append({
            "left": left,
            "right": right,
            "constant": Fraction(4) - z_constant,
            "direction": -z_direction,
        })

    varying = next(item for item in disjoint_affine if item["direction"])
    candidate_parameters = set()
    for block_total in range(17):
        candidate_parameters.add(
            (Fraction(block_total) - varying["constant"]) / varying["direction"]
        )

    feasible = []
    rejected = []
    for parameter in sorted(candidate_parameters):
        block_totals = []
        integral_and_in_range = True
        for item in disjoint_affine:
            value = item["constant"] + item["direction"] * parameter
            block_totals.append([item["left"], item["right"], fstr(value)])
            integral_and_in_range &= value.denominator == 1 and 0 <= value <= 16
        if not integral_and_in_range:
            rejected.append({"parameter": fstr(parameter), "reason": "block_total"})
            continue
        parameters = [a + b * parameter for a, b in zip(constants, directions)]
        H = matrix_from_parameters(parameters, dimension)
        is_psd, minimum_minor, bad_subset = psd_by_principal_minors(H)
        row_sums = []
        lookup = {
            (left, right): Fraction(value)
            for left, right, value in block_totals
        }
        for left, support in enumerate(supports):
            total = Fraction(2 * (4 - deficits[left]))
            exceptional_disjoint = 0
            for right, other in enumerate(supports):
                if left == right:
                    continue
                pair = tuple(sorted((left, right)))
                if set(support) & set(other):
                    total += overlap[pair]
                else:
                    exceptional_disjoint += 1
                    total += lookup[pair]
            total += 4 * (10 - exceptional_disjoint)
            row_sums.append(total)
        record = {
            "parameter": fstr(parameter),
            "H": [[fstr(value) for value in row] for row in H],
            "disjoint_exceptional_block_totals": block_totals,
            "psd": is_psd,
            "minimum_principal_minor": fstr(minimum_minor),
            "first_negative_principal_minor_subset": (
                None if bad_subset is None else list(bad_subset)
            ),
            "complete_compression_row_sums": [fstr(value) for value in row_sums],
            "all_complete_compression_row_sums_48": all(value == 48 for value in row_sums),
        }
        if is_psd and record["all_complete_compression_row_sums_48"]:
            feasible.append(record)
        else:
            record["reason"] = "psd_or_rowsum"
            rejected.append(record)

    result = {
        "status": "EXACT_PARAMETRIC_ENUMERATION_COMPLETE",
        "input": str(INPUT),
        "input_sha256": hashlib.sha256(raw).hexdigest().upper(),
        "macro": {
            "partition_index": entry["partition_index"],
            "compression_orbit_index": entry["compression_orbit_index"],
            "source_row_index": entry["source_row_index"],
            "state_orbit_number": entry["state_orbit_number"],
            "Q": entry["Q"],
            "labelled_coverage": entry["signature_orbit_labelled_coverage"],
        },
        "kernel_dimension": dimension,
        "gram_parameter_count": variable_count,
        "linear_rank": len(pivots),
        "free_variable_index": free_variable,
        "parameter_definition": f"gram_parameter[{free_variable}] = t",
        "parameter_constants": [fstr(value) for value in constants],
        "parameter_directions": [fstr(value) for value in directions],
        "H_constant": [[fstr(value) for value in row] for row in H_constant],
        "H_direction": [[fstr(value) for value in row] for row in H_direction],
        "disjoint_block_affine_forms": [
            {
                "left": item["left"],
                "right": item["right"],
                "form": f"{fstr(item['constant'])} + ({fstr(item['direction'])})*t",
            }
            for item in disjoint_affine
        ],
        "candidate_parameter_count": len(candidate_parameters),
        "feasible_parameter_count": len(feasible),
        "feasible_parameters": feasible,
        "rejected_parameter_count": len(rejected),
        "rejected_parameters": rejected,
        "claim": (
            "Every rational parameter compatible with integral disjoint block totals "
            "in [0,16] is enumerated by one nonconstant affine block total."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "candidate_parameters": len(candidate_parameters),
        "feasible_parameters": len(feasible),
        "values": [row["parameter"] for row in feasible],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
