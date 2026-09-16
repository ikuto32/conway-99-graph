"""Independent exact audit of the E72 fibre-variance kernel census."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path


CATALOG = Path("scratch_general_e72_q3_gram_fast_expansion_macro_catalog.json")
FULL_GRAM = Path("scratch_theory_e72_macro_full_gram.json")
PARAMETRIC = Path("scratch_theory_e72_source332_parametric_gram.json")
REFERENCE = Path("scratch_theory_e72_equitable_kernel_census.json")
NOTE = Path("scratch_theory_e72_equitable_kernel_independent.md")
OUTPUT = Path("scratch_theory_e72_equitable_kernel_independent_audit.json")
SUPPORTS = tuple(itertools.combinations(range(7), 2))


def macro_key(row):
    return (
        int(row["partition_index"]),
        int(row["compression_orbit_index"]),
        int(row["source_row_index"]),
        int(row["state_orbit_number"]),
        int(row["signature_stabilizer_orbit_number"]),
    )


def transpose(matrix):
    return [list(row) for row in zip(*matrix)]


def matmul(left, right):
    return [[sum(left[i][k] * right[k][j] for k in range(len(right)))
             for j in range(len(right[0]))]
            for i in range(len(left))]


def matvec(matrix, vector):
    return [sum(a * b for a, b in zip(row, vector)) for row in matrix]


def exact_rank(matrix):
    rows = [[Fraction(value) for value in row] for row in matrix]
    if not rows:
        return 0
    height, width = len(rows), len(rows[0])
    pivot_row = 0
    for column in range(width):
        pivot = next((r for r in range(pivot_row, height)
                      if rows[r][column]), None)
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        scale = rows[pivot_row][column]
        rows[pivot_row] = [value / scale for value in rows[pivot_row]]
        for r in range(height):
            if r == pivot_row or not rows[r][column]:
                continue
            scale = rows[r][column]
            rows[r] = [a - scale * b for a, b in zip(rows[r], rows[pivot_row])]
        pivot_row += 1
        if pivot_row == height:
            break
    return pivot_row


def column_rank(columns):
    return exact_rank(transpose(columns)) if columns else 0


def build_compression(entry, disjoint_rows):
    exceptional_rows = tuple(entry["exceptional_supports"])
    exceptional_supports = tuple(tuple(item["support"]) for item in exceptional_rows)
    exceptional_set = set(exceptional_supports)
    exceptional_index = {support: i for i, support in enumerate(exceptional_supports)}
    deficits = {tuple(item["support"]): int(item["deficit"])
                for item in exceptional_rows}
    overlap = {tuple(sorted((int(i), int(j)))): int(value)
               for i, j, value in entry["overlap_block_totals"]}
    disjoint = {tuple(sorted((int(i), int(j)))): int(value)
                for i, j, value in disjoint_rows}
    matrix = [[0] * 21 for _ in range(21)]
    for i, support in enumerate(SUPPORTS):
        matrix[i][i] = 2 * (4 - deficits.get(support, 0))
    for i, j in itertools.combinations(range(21), 2):
        left, right = SUPPORTS[i], SUPPORTS[j]
        meeting = bool(set(left) & set(right))
        if left in exceptional_set and right in exceptional_set:
            pair = tuple(sorted((exceptional_index[left], exceptional_index[right])))
            value = (overlap if meeting else disjoint)[pair]
        else:
            value = 0 if meeting else 4
        matrix[i][j] = matrix[j][i] = value
    assert all(sum(row) == 48 for row in matrix)
    return matrix


def build_k4(compression, incidence):
    llt = matmul(incidence, transpose(incidence))
    c2 = matmul(compression, compression)
    return [[192 * int(i == j) + 128 - 4 * compression[i][j]
             - 32 * llt[i][j] - c2[i][j]
             for j in range(21)] for i in range(21)]


def main():
    catalog_raw = CATALOG.read_bytes()
    gram_raw = FULL_GRAM.read_bytes()
    parametric_raw = PARAMETRIC.read_bytes()
    reference_raw = REFERENCE.read_bytes()
    catalog = json.loads(catalog_raw)
    gram = json.loads(gram_raw)
    parametric = json.loads(parametric_raw)
    reference = json.loads(reference_raw)

    # Direct combinatorial reconstruction of M, P, and L.
    outer_vertices = tuple((support_index, a, b)
                           for support_index in range(21)
                           for a in (0, 1) for b in (0, 1))
    M = [[int(vertex[0] == fibre) for fibre in range(21)]
         for vertex in outer_vertices]
    P = []
    for support_index, a, b in outer_vertices:
        support = SUPPORTS[support_index]
        row = [0] * 14
        row[2 * support[0] + a] = 1
        row[2 * support[1] + b] = 1
        P.append(row)
    L = [[int(group in support) for group in range(7)] for support in SUPPORTS]
    mtm = matmul(transpose(M), M)
    assert mtm == [[4 * int(i == j) for j in range(21)] for i in range(21)]
    mtp = matmul(transpose(M), P)
    lhs = matmul(mtp, transpose(mtp))
    rhs = [[8 * value for value in row] for row in matmul(L, transpose(L))]
    assert lhs == rhs
    assert exact_rank(L) == 7
    incidence_columns = transpose(L)

    gram_by_key = {macro_key(row): row for row in gram["rows"]
                   if row["signature_stabilizer_canonical"]}
    reference_by_profile = {
        (tuple(row["key"]), int(row["gram_profile_index"])): row
        for row in reference["rows"]
    }
    records = []
    rejected = []
    source133_checks = []
    for entry in catalog["macro_entries"]:
        if not entry["signature_stabilizer_canonical"]:
            continue
        key = macro_key(entry)
        full = gram_by_key[key]
        if full["unique"]:
            if not full["passes_full_unique_gram_checks"]:
                rejected.append(key)
                continue
            profiles = [full["disjoint_exceptional_block_totals"]]
        else:
            assert int(entry["source_row_index"]) == 332
            profiles = [row["disjoint_exceptional_block_totals"]
                        for row in parametric["feasible_parameters"]]
        for profile_index, profile in enumerate(profiles):
            C = build_compression(entry, profile)
            K4 = build_k4(C, L)
            assert K4 == transpose(K4)
            assert all(value == 0 for column in incidence_columns
                       for value in matvec(K4, column))
            exceptional = {tuple(item["support"])
                           for item in entry["exceptional_supports"]}
            ordinary_indices = [i for i, support in enumerate(SUPPORTS)
                                if support not in exceptional]
            ordinary_units = [tuple(int(i == j) for i in range(21))
                              for j in ordinary_indices]
            assert all(value == 0 for unit in ordinary_units
                       for value in matvec(K4, unit))
            rank_k = exact_rank(K4)
            kernel_dimension = 21 - rank_k
            baseline_rank = column_rank([*incidence_columns, *ordinary_units])
            novel_dimension = kernel_dimension - baseline_rank
            reference_row = reference_by_profile[(key, profile_index)]
            assert C == reference_row["compression"]
            assert kernel_dimension == reference_row["kernel_dimension"]
            assert kernel_dimension - 7 == reference_row["extra_equitable_dimension"]
            assert baseline_rank == reference_row["incidence_plus_ordinary_baseline_rank"]
            assert novel_dimension == reference_row["novel_equitable_dimension"]
            records.append((key, profile_index, kernel_dimension,
                            baseline_rank, novel_dimension,
                            int(entry["signature_orbit_labelled_coverage"])))

            if int(entry["source_row_index"]) == 133:
                A = {(0, i) for i in (2, 3, 4)}
                Bside = {(1, i) for i in (2, 3, 4)}
                cd = tuple(1 if support in A else -1 if support in Bside else 0
                           for support in SUPPORTS)
                f = tuple(int(0 in support) - int(1 in support)
                          for support in SUPPORTS)
                e = tuple(-1 if support in ((0, 5), (0, 6))
                          else 1 if support in ((1, 5), (1, 6)) else 0
                          for support in SUPPORTS)
                assert cd == tuple(x + y for x, y in zip(f, e))
                assert all(not value for value in matvec(K4, cd))
                Ccd = matvec(C, cd)
                assert all(value % 4 == 0 for value in Ccd)
                means = tuple(value // 4 for value in Ccd)
                assert means == tuple(3 * value for value in e)
                source133_checks.append({
                    "key": list(key),
                    "profile_index": profile_index,
                    "kernel_dimension": kernel_dimension,
                    "baseline_rank": baseline_rank,
                    "novel_dimension": novel_dimension,
                    "Bd_fibre_means": list(means),
                })

    assert len(records) == len(reference["rows"]) == 162
    assert len({row[0] for row in records}) == reference["canonical_macros"] == 160
    extra_hist = Counter(row[2] - 7 for row in records)
    novel_hist = Counter(row[4] for row in records)
    assert {str(k): v for k, v in sorted(extra_hist.items())} == reference[
        "extra_dimension_histogram"
    ]
    assert {str(k): v for k, v in sorted(novel_hist.items())} == reference[
        "novel_dimension_after_incidence_and_ordinary_C4_histogram"
    ]
    assert len(source133_checks) == 5
    assert all(row["novel_dimension"] == 0 for row in source133_checks)
    assert {tuple(key) for key in rejected} == {
        tuple(row["key"]) for row in reference["rejected_macros"]
    }

    result = {
        "status": "INDEPENDENT_EXACT_KERNEL_AUDIT_VERIFIED",
        "inputs": {
            str(CATALOG): hashlib.sha256(catalog_raw).hexdigest().upper(),
            str(FULL_GRAM): hashlib.sha256(gram_raw).hexdigest().upper(),
            str(PARAMETRIC): hashlib.sha256(parametric_raw).hexdigest().upper(),
            str(REFERENCE): hashlib.sha256(reference_raw).hexdigest().upper(),
        },
        "structural_matrix_checks": ["M^T M=4I", "M^T PP^T M=8LL^T",
                                     "rank(L)=7"],
        "formula": "4K=192I+128J-4C-32LL^T-C^2",
        "profile_rows": len(records),
        "canonical_macros": len({row[0] for row in records}),
        "extra_dimension_histogram": {str(k): v for k, v in sorted(extra_hist.items())},
        "novel_dimension_after_incidence_and_ordinary_C4_histogram": {
            str(k): v for k, v in sorted(novel_hist.items())
        },
        "profiles_with_novel_directions": sum(value for key, value in novel_hist.items()
                                               if key > 0),
        "source133": {
            "profiles": source133_checks,
            "d_decomposition": "c_d=L*(1,-1,0,0,0,0,0)^T+e_ordinary",
            "interpretation": "kernel constancy is exactly Bd=3e",
        },
        "claim_boundary": (
            "Independent exact rank/formula audit of necessary fibre-constancy "
            "identities; no realizability or exclusion claim."
        ),
        "note": str(NOTE),
        "note_sha256": hashlib.sha256(NOTE.read_bytes()).hexdigest().upper(),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"path": str(OUTPUT), **result}, sort_keys=True))


if __name__ == "__main__":
    main()
