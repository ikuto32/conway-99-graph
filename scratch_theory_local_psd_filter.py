"""Exact PSD-compression filter for materialized rooted local graphs.

This strengthens ``scratch_theory_unsigned_kernel_filter.py`` by adding the
known overlap-block totals of each local representative.  It is purely exact
rational linear algebra; only a unique Gram-parameter solution is rejected
for non-PSDness.  A consistent underdetermined solution is retained.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import itertools
import json
from pathlib import Path

from scratch_theory_unsigned_kernel_filter import (
    linear_system_status,
    nullspace,
    psd_by_principal_minors,
)


def bilinear_coefficients(left, right):
    d = len(left)
    values = []
    for a in range(d):
        for b in range(a, d):
            if a == b:
                values.append(left[a] * right[a])
            else:
                values.append(left[a] * right[b] + left[b] * right[a])
    return values


def analyze_representative(support_row, representative):
    exceptional = support_row["exceptional_supports"]
    supports = [tuple(item["support"]) for item in exceptional]
    support_index = {support: i for i, support in enumerate(supports)}
    deficits = [int(item["deficit"]) for item in exceptional]
    incidence_t = [
        [int(group in support) for support in supports]
        for group in range(7)
    ]
    basis_columns = nullspace(incidence_t)
    d = len(basis_columns)
    W = [[basis_columns[j][i] for j in range(d)] for i in range(len(supports))]
    coefficients = []
    targets = []
    constraint_names = []
    for i, deficit in enumerate(deficits):
        coefficients.append(bilinear_coefficients(W[i], W[i]))
        targets.append(Fraction(2 * deficit))
        constraint_names.append(["diagonal", i])

    overlap_counts = {}
    for raw_left, raw_right in representative["edges"]:
        left_support = tuple(sorted(value // 2 for value in raw_left))
        right_support = tuple(sorted(value // 2 for value in raw_right))
        if left_support == right_support:
            continue
        if not set(left_support).intersection(right_support):
            # Local expansion does not intend to fix disjoint-fibre blocks.
            continue
        key = tuple(sorted((support_index[left_support], support_index[right_support])))
        overlap_counts[key] = overlap_counts.get(key, 0) + 1

    for i, j in itertools.combinations(range(len(supports)), 2):
        if not set(supports[i]).intersection(supports[j]):
            continue
        value = overlap_counts.get((i, j), 0)
        coefficients.append(bilinear_coefficients(W[i], W[j]))
        targets.append(Fraction(-value))
        constraint_names.append(["overlap", i, j])

    status = linear_system_status(coefficients, targets)
    result = {
        "kernel_dimension": d,
        "linear_constraints": len(coefficients),
        "gram_parameter_count": d * (d + 1) // 2,
        "consistent": status["consistent"],
        "solution_dimension": status["solution_dimension"],
        "overlap_block_totals": [
            [i, j, overlap_counts.get((i, j), 0)]
            for i, j in itertools.combinations(range(len(supports)), 2)
            if set(supports[i]).intersection(supports[j])
        ],
    }
    if status.get("unique_solution") is not None:
        H = [[Fraction(0) for _ in range(d)] for _ in range(d)]
        pairs = [(a, b) for a in range(d) for b in range(a, d)]
        for value, (a, b) in zip(status["unique_solution"], pairs):
            H[a][b] = H[b][a] = value
        is_psd, minimum_minor, bad_subset = psd_by_principal_minors(H)
        result.update({
            "unique_solution_psd": is_psd,
            "unique_solution": [[str(value) for value in row] for row in H],
            "minimum_checked_principal_minor": str(minimum_minor),
            "first_negative_principal_minor_subset": (
                None if bad_subset is None else list(bad_subset)
            ),
        })
    result["passes_or_undecided"] = (
        status["consistent"] and result.get("unique_solution_psd", True)
    )
    return result


def audit(source_path):
    source = json.loads(source_path.read_text(encoding="utf-8"))
    rows = []
    for support_row_index, support_row in enumerate(source["support_rows"]):
        for representative_index, representative in enumerate(support_row["representatives"]):
            result = analyze_representative(support_row, representative)
            result.update({
                "support_row_index": support_row_index,
                "partition": support_row["partition"],
                "compression_orbit_index": support_row["compression_orbit_index"],
                "representative_index": representative_index,
                "local_orbit_size": representative["orbit_size"],
                "Q": representative["Q"],
            })
            rows.append(result)
    passing = [row for row in rows if row["passes_or_undecided"]]
    return {
        "model": "exact local overlap-block filter from the PSD matrix Z=4(3P_f-R_f)",
        "source": str(source_path),
        "counts": {
            "input_representatives": len(rows),
            "inconsistent": sum(not row["consistent"] for row in rows),
            "unique_non_psd": sum(row.get("unique_solution_psd") is False for row in rows),
            "passing_or_undecided": len(passing),
        },
        "by_support_row": [
            {
                "support_row_index": index,
                "input": sum(row["support_row_index"] == index for row in rows),
                "passing_or_undecided": sum(
                    row["support_row_index"] == index and row["passes_or_undecided"]
                    for row in rows
                ),
            }
            for index in range(len(source["support_rows"]))
        ],
        "scope_warning": (
            "Passing representatives satisfy only an aggregate necessary PSD condition; "
            "no full graph extension is asserted."
        ),
        "rows": rows,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = audit(args.source)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"counts": result["counts"], "by_support_row": result["by_support_row"]}))


if __name__ == "__main__":
    main()
