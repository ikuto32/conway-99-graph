"""Find every Gram macro direction whose fibrewise variance is forced to zero.

Let M be the 84-by-21 fibre indicator matrix, B the outer adjacency matrix,
and C=M^T B M the complete fibre compression (diagonal 2e_F, off-diagonal
block totals D_FG).  For d=M c, the SRG identity gives

  ||B d||^2 = 48||c||^2 + 32(sum c)^2 - c^T C c - 8||L^T c||^2,

where L is the unsigned K7 edge--vertex incidence matrix.  The sum of the
squared fibre means of Bd is ||C c||^2/4.  Their difference is the quadratic
form

  K = 48 I + 32 J - C - 8 L L^T - C^2/4.

For any actual graph this is a sum of within-fibre squared deviations.  Thus
every exact c in ker(K) forces Bd to be pointwise constant on each fibre,
with value (C c)_F/4.  The seven incidence-column directions merely restate
the standard degree/symbol BP equations.  This census reports all additional
directions for every canonical E72 full-Gram profile.
"""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
import hashlib
import itertools
import json
import math
from pathlib import Path

from scratch_theory_unsigned_kernel_filter import nullspace, rref


CATALOG = Path("scratch_general_e72_q3_gram_fast_expansion_macro_catalog.json")
FULL_GRAM = Path("scratch_theory_e72_macro_full_gram.json")
PARAMETRIC = Path("scratch_theory_e72_source332_parametric_gram.json")
OUTPUT = Path("scratch_theory_e72_equitable_kernel_census.json")
SUPPORTS = tuple(itertools.combinations(range(7), 2))


def macro_key(entry):
    return (
        int(entry["partition_index"]),
        int(entry["compression_orbit_index"]),
        int(entry["source_row_index"]),
        int(entry["state_orbit_number"]),
        int(entry["signature_stabilizer_orbit_number"]),
    )


def rank_of_columns(columns):
    if not columns:
        return 0
    rows = [[column[row] for column in columns] for row in range(len(columns[0]))]
    _reduced, pivots = rref(rows)
    return len(pivots)


def primitive_integer_vector(vector):
    denominators = [value.denominator for value in vector]
    multiple = 1
    for denominator in denominators:
        multiple = math.lcm(multiple, denominator)
    integers = [int(value * multiple) for value in vector]
    divisor = 0
    for value in integers:
        divisor = math.gcd(divisor, abs(value))
    assert divisor
    integers = [value // divisor for value in integers]
    first = next(value for value in integers if value)
    if first < 0:
        integers = [-value for value in integers]
    return tuple(integers)


def compression(entry, disjoint_rows):
    exceptional_rows = tuple(entry["exceptional_supports"])
    exceptional_supports = tuple(tuple(item["support"]) for item in exceptional_rows)
    exceptional_index = {support: index for index, support in enumerate(exceptional_supports)}
    exceptional = frozenset(exceptional_supports)
    deficits = {
        tuple(item["support"]): int(item["deficit"])
        for item in exceptional_rows
    }
    overlap = {
        tuple(sorted((int(left), int(right)))): int(value)
        for left, right, value in entry["overlap_block_totals"]
    }
    disjoint = {
        tuple(sorted((int(left), int(right)))): int(value)
        for left, right, value in disjoint_rows
    }
    C = [[Fraction(0) for _ in SUPPORTS] for _ in SUPPORTS]
    for i, support in enumerate(SUPPORTS):
        C[i][i] = 2 * (4 - deficits.get(support, 0))
    for i, j in itertools.combinations(range(21), 2):
        left, right = SUPPORTS[i], SUPPORTS[j]
        meeting = bool(set(left) & set(right))
        if left in exceptional and right in exceptional:
            pair = tuple(sorted((exceptional_index[left], exceptional_index[right])))
            table = overlap if meeting else disjoint
            assert pair in table
            value = table[pair]
        else:
            value = 0 if meeting else 4
        C[i][j] = C[j][i] = value
    assert all(sum(row) == 48 for row in C)
    return C


def matmul(left, right):
    return [
        [
            sum((left[i][k] * right[k][j] for k in range(len(right))), Fraction(0))
            for j in range(len(right[0]))
        ]
        for i in range(len(left))
    ]


def matvec(matrix, vector):
    return [
        sum((value * coefficient for value, coefficient in zip(row, vector)), Fraction(0))
        for row in matrix
    ]


def analyze(entry, disjoint_rows, profile_index):
    C = compression(entry, disjoint_rows)
    incidence = [
        [Fraction(int(group in support)) for group in range(7)]
        for support in SUPPORTS
    ]
    incidence_columns = [tuple(column) for column in zip(*incidence)]
    LLt = matmul(incidence, [list(row) for row in zip(*incidence)])
    C2 = matmul(C, C)
    K = [
        [
            Fraction(48 * (i == j) + 32) - C[i][j] - 8 * LLt[i][j] - C2[i][j] / 4
            for j in range(21)
        ]
        for i in range(21)
    ]
    kernel = nullspace(K)
    assert all(
        not value
        for column in incidence_columns
        for value in matvec(K, column)
    )
    assert rank_of_columns(incidence_columns) == 7
    span = list(incidence_columns)
    current_rank = 7
    extra = []
    for candidate in kernel:
        new_rank = rank_of_columns([*span, candidate])
        if new_rank == current_rank:
            continue
        assert new_rank == current_rank + 1
        span.append(tuple(candidate))
        current_rank = new_rank
        vector = primitive_integer_vector(candidate)
        rhs = matvec(C, vector)
        # Scale the primitive c further if needed so every fibre mean is integral.
        mean_denominator = 1
        for value in rhs:
            mean_denominator = math.lcm(mean_denominator, (value / 4).denominator)
        if mean_denominator > 1:
            vector = tuple(mean_denominator * value for value in vector)
            rhs = matvec(C, vector)
        means = tuple(value / 4 for value in rhs)
        assert all(value.denominator == 1 for value in means)
        extra.append({
            "coefficients": list(vector),
            "fibre_means_Bd": [int(value) for value in means],
            "coefficient_l1": sum(abs(value) for value in vector),
            "coefficient_max_abs": max(abs(value) for value in vector),
            "nonzero_coefficients": sum(value != 0 for value in vector),
            "nonzero_fibre_means": sum(value != 0 for value in means),
        })
    assert len(kernel) == current_rank

    # The SAT builders already encode the pointwise equations for each
    # ordinary C4 fibre, as well as the seven BP incidence directions.  Test
    # whether the kernel contains anything beyond that established baseline.
    exceptional = frozenset(
        tuple(item["support"]) for item in entry["exceptional_supports"]
    )
    ordinary_indices = [
        index for index, support in enumerate(SUPPORTS) if support not in exceptional
    ]
    ordinary_units = []
    for index in ordinary_indices:
        unit = tuple(Fraction(int(position == index)) for position in range(21))
        assert all(not value for value in matvec(K, unit))
        ordinary_units.append(unit)
    baseline_span = [*incidence_columns, *ordinary_units]
    baseline_rank = rank_of_columns(baseline_span)
    novel = []
    current_novel_rank = baseline_rank
    for candidate in kernel:
        new_rank = rank_of_columns([*baseline_span, candidate])
        if new_rank == current_novel_rank:
            continue
        assert new_rank == current_novel_rank + 1
        baseline_span.append(tuple(candidate))
        current_novel_rank = new_rank
        vector = primitive_integer_vector(candidate)
        rhs = matvec(C, vector)
        mean_denominator = 1
        for value in rhs:
            mean_denominator = math.lcm(mean_denominator, (value / 4).denominator)
        if mean_denominator > 1:
            vector = tuple(mean_denominator * value for value in vector)
            rhs = matvec(C, vector)
        means = tuple(value / 4 for value in rhs)
        assert all(value.denominator == 1 for value in means)
        novel.append({
            "coefficients": list(vector),
            "fibre_means_Bd": [int(value) for value in means],
            "coefficient_l1": sum(abs(value) for value in vector),
            "coefficient_max_abs": max(abs(value) for value in vector),
            "nonzero_coefficients": sum(value != 0 for value in vector),
            "nonzero_fibre_means": sum(value != 0 for value in means),
        })
    assert current_novel_rank == len(kernel)
    return {
        "key": list(macro_key(entry)),
        "source_row_index": int(entry["source_row_index"]),
        "partition_index": int(entry["partition_index"]),
        "Q": int(entry["Q"]),
        "gram_profile_index": profile_index,
        "labelled_coverage": int(entry["signature_orbit_labelled_coverage"]),
        "kernel_dimension": len(kernel),
        "standard_incidence_dimension": 7,
        "extra_equitable_dimension": len(extra),
        "extra_directions": extra,
        "ordinary_unit_directions": len(ordinary_units),
        "incidence_plus_ordinary_baseline_rank": baseline_rank,
        "novel_equitable_dimension": len(novel),
        "novel_directions": novel,
        "compression": [[int(value) for value in row] for row in C],
    }


def main():
    catalog_raw = CATALOG.read_bytes()
    gram_raw = FULL_GRAM.read_bytes()
    parametric_raw = PARAMETRIC.read_bytes()
    catalog = json.loads(catalog_raw)
    gram = json.loads(gram_raw)
    parametric = json.loads(parametric_raw)
    gram_by_key = {
        macro_key(row): row for row in gram["rows"]
        if row["signature_stabilizer_canonical"]
    }
    rows = []
    rejected = []
    for entry in catalog["macro_entries"]:
        if not entry["signature_stabilizer_canonical"]:
            continue
        full = gram_by_key[macro_key(entry)]
        if full["unique"]:
            if not full["passes_full_unique_gram_checks"]:
                rejected.append({
                    "key": list(macro_key(entry)),
                    "coverage": int(entry["signature_orbit_labelled_coverage"]),
                })
                continue
            profiles = [full["disjoint_exceptional_block_totals"]]
        else:
            assert int(entry["source_row_index"]) == 332
            profiles = [
                row["disjoint_exceptional_block_totals"]
                for row in parametric["feasible_parameters"]
            ]
        for profile_index, profile in enumerate(profiles):
            rows.append(analyze(entry, profile, profile_index))

    extra_histogram = Counter(row["extra_equitable_dimension"] for row in rows)
    novel_histogram = Counter(row["novel_equitable_dimension"] for row in rows)
    macro_keys_with_extra = {tuple(row["key"]) for row in rows if row["extra_equitable_dimension"]}
    # Do not triple-count a parametric macro's labelled coverage.
    coverage_by_key = {
        macro_key(entry): int(entry["signature_orbit_labelled_coverage"])
        for entry in catalog["macro_entries"] if entry["signature_stabilizer_canonical"]
    }
    source_summary = []
    for source_index in sorted({row["source_row_index"] for row in rows}):
        source_rows = [row for row in rows if row["source_row_index"] == source_index]
        keys = {tuple(row["key"]) for row in source_rows}
        extra_keys = {tuple(row["key"]) for row in source_rows if row["extra_equitable_dimension"]}
        source_summary.append({
            "source_row_index": source_index,
            "profile_rows": len(source_rows),
            "canonical_macros": len(keys),
            "macros_with_extra_equitable_directions": len(extra_keys),
            "labelled_coverage": sum(coverage_by_key[key] for key in keys),
            "coverage_with_extra_equitable_directions": sum(
                coverage_by_key[key] for key in extra_keys
            ),
            "maximum_extra_dimension": max(
                row["extra_equitable_dimension"] for row in source_rows
            ),
        })
    result = {
        "status": "EXACT_EQUITABLE_KERNEL_CENSUS_COMPLETE",
        "inputs": {
            str(CATALOG): hashlib.sha256(catalog_raw).hexdigest().upper(),
            str(FULL_GRAM): hashlib.sha256(gram_raw).hexdigest().upper(),
            str(PARAMETRIC): hashlib.sha256(parametric_raw).hexdigest().upper(),
        },
        "formula": "K=48I+32J-C-8LL^T-C^2/4",
        "proof_rule": (
            "c in ker(K) makes the sum of 21 within-fibre variances of Bd zero, "
            "so (Bd)_x=(Cc)_F/4 for every x in fibre F"
        ),
        "profile_rows": len(rows),
        "canonical_macros": len({tuple(row["key"]) for row in rows}),
        "rejected_macros": rejected,
        "extra_dimension_histogram": {
            str(key): value for key, value in sorted(extra_histogram.items())
        },
        "novel_dimension_after_incidence_and_ordinary_C4_histogram": {
            str(key): value for key, value in sorted(novel_histogram.items())
        },
        "macros_with_extra_equitable_directions": len(macro_keys_with_extra),
        "labelled_coverage_with_extra_equitable_directions": sum(
            coverage_by_key[key] for key in macro_keys_with_extra
        ),
        "source_summary": source_summary,
        "rows": rows,
        "claim_boundary": (
            "This census derives necessary pointwise linear equations; it does not "
            "by itself assert realizability or nonexistence of a macro."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "profiles": result["profile_rows"],
        "macros": result["canonical_macros"],
        "with_extra": result["macros_with_extra_equitable_directions"],
        "coverage": result["labelled_coverage_with_extra_equitable_directions"],
        "histogram": result["extra_dimension_histogram"],
        "novel_histogram": result[
            "novel_dimension_after_incidence_and_ordinary_C4_histogram"
        ],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
