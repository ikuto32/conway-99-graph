"""Recover all Gram-implied exceptional block totals for E72 macros.

The fast macro census fixes the fibre diagonals and every overlapping
exceptional block total.  Those linear equations often determine the Gram
parameter matrix completely.  In that case this audit computes, exactly,
the still-unmaterialized disjoint-exceptional totals D_FG=4-Z_FG and checks
integrality, range, PSD, and the complete compression row sums.
"""

from __future__ import annotations

from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path

from scratch_theory_local_psd_filter import bilinear_coefficients
from scratch_theory_unsigned_kernel_filter import (
    linear_system_status,
    nullspace,
    psd_by_principal_minors,
)


INPUT = Path("scratch_general_e72_q3_gram_fast_expansion_macro_catalog.json")
OUTPUT = Path("scratch_theory_e72_macro_full_gram.json")


def dot_bilinear(coefficients, parameters):
    return sum((a * b for a, b in zip(coefficients, parameters)), Fraction(0))


def analyze(entry):
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
    for index, deficit in enumerate(deficits):
        coefficients.append(bilinear_coefficients(W[index], W[index]))
        targets.append(Fraction(2 * deficit))
    overlap = {
        tuple(sorted((int(left), int(right)))): int(value)
        for left, right, value in entry["overlap_block_totals"]
    }
    expected_overlap_pairs = {
        (left, right)
        for left, right in itertools.combinations(range(len(supports)), 2)
        if set(supports[left]) & set(supports[right])
    }
    assert set(overlap) == expected_overlap_pairs
    for pair in sorted(overlap):
        left, right = pair
        coefficients.append(bilinear_coefficients(W[left], W[right]))
        targets.append(Fraction(-overlap[pair]))
    status = linear_system_status(coefficients, targets)
    result = {
        "partition_index": entry["partition_index"],
        "compression_orbit_index": entry["compression_orbit_index"],
        "source_row_index": entry["source_row_index"],
        "state_orbit_number": entry["state_orbit_number"],
        "signature_stabilizer_orbit_number": entry["signature_stabilizer_orbit_number"],
        "signature_stabilizer_canonical": entry["signature_stabilizer_canonical"],
        "Q": entry["Q"],
        "signature_orbit_labelled_coverage": entry["signature_orbit_labelled_coverage"],
        "kernel_dimension": dimension,
        "gram_parameter_count": dimension * (dimension + 1) // 2,
        "linear_constraints": len(coefficients),
        "consistent": status["consistent"],
        "solution_dimension": status["solution_dimension"],
        "unique": status.get("unique_solution") is not None,
    }
    if status.get("unique_solution") is None:
        result["passes_full_unique_gram_checks"] = status["consistent"]
        return result

    parameters = status["unique_solution"]
    H = [[Fraction(0) for _ in range(dimension)] for _ in range(dimension)]
    positions = [
        (left, right)
        for left in range(dimension)
        for right in range(left, dimension)
    ]
    for value, (left, right) in zip(parameters, positions):
        H[left][right] = H[right][left] = value
    is_psd, minimum_minor, bad_subset = psd_by_principal_minors(H)
    z_matrix = []
    for left in range(len(supports)):
        row = []
        for right in range(len(supports)):
            row.append(dot_bilinear(
                bilinear_coefficients(W[left], W[right]), parameters
            ))
        z_matrix.append(row)

    disjoint = []
    values_integral = True
    values_in_range = True
    for left, right in itertools.combinations(range(len(supports)), 2):
        if set(supports[left]) & set(supports[right]):
            assert z_matrix[left][right] == -overlap[(left, right)]
            continue
        value = Fraction(4) - z_matrix[left][right]
        values_integral &= value.denominator == 1
        values_in_range &= 0 <= value <= 16
        disjoint.append([left, right, str(value)])

    row_sums = []
    for left, support in enumerate(supports):
        total = Fraction(2 * (4 - deficits[left]))
        exceptional_disjoint = 0
        for right, other in enumerate(supports):
            if left == right:
                continue
            if set(support) & set(other):
                total += overlap[tuple(sorted((left, right)))]
            else:
                exceptional_disjoint += 1
                total += Fraction(4) - z_matrix[left][right]
        # K7 has ten supports disjoint from a fixed support. Every ordinary
        # disjoint fibre contributes a four-edge block.
        total += 4 * (10 - exceptional_disjoint)
        row_sums.append(total)
    row_sums_48 = all(value == 48 for value in row_sums)
    passes = is_psd and values_integral and values_in_range and row_sums_48
    result.update({
        "unique_H": [[str(value) for value in row] for row in H],
        "unique_H_psd": is_psd,
        "minimum_principal_minor": str(minimum_minor),
        "first_negative_principal_minor_subset": (
            None if bad_subset is None else list(bad_subset)
        ),
        "disjoint_exceptional_block_totals": disjoint,
        "all_disjoint_totals_integral": values_integral,
        "all_disjoint_totals_in_0_16": values_in_range,
        "complete_compression_row_sums": [str(value) for value in row_sums],
        "all_complete_compression_row_sums_48": row_sums_48,
        "passes_full_unique_gram_checks": passes,
    })
    return result


def main():
    raw = INPUT.read_bytes()
    source = json.loads(raw)
    rows = [analyze(entry) for entry in source["macro_entries"]]
    canonical = [row for row in rows if row["signature_stabilizer_canonical"]]
    unique = [row for row in canonical if row["unique"]]
    result = {
        "status": "COMPLETE",
        "model": "exact full exceptional-block Gram recovery for E72 macro branches",
        "input": str(INPUT),
        "input_sha256": hashlib.sha256(raw).hexdigest().upper(),
        "method": (
            "solve diagonal and all overlapping Z=W H W^T equations over Fraction; "
            "when H is unique, recover every disjoint D_FG=4-Z_FG"
        ),
        "summary": {
            "input_macro_entries": len(rows),
            "canonical_macro_entries": len(canonical),
            "unique_gram_canonical_entries": len(unique),
            "underdetermined_canonical_entries": sum(not row["unique"] for row in canonical),
            "unique_entries_passing_integrality_range_psd_rowsum": sum(
                row["passes_full_unique_gram_checks"] for row in unique
            ),
            "unique_entries_rejected": sum(
                not row["passes_full_unique_gram_checks"] for row in unique
            ),
            "unique_labelled_coverage": sum(
                row["signature_orbit_labelled_coverage"] for row in unique
            ),
            "underdetermined_labelled_coverage": sum(
                row["signature_orbit_labelled_coverage"]
                for row in canonical if not row["unique"]
            ),
        },
        "rows": rows,
        "claim_boundary": (
            "Underdetermined Gram systems are retained. Block totals alone do not "
            "assert a vertex-level graph extension."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
