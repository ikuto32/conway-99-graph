"""Exact support-only consequences of the rooted compression PSD matrix.

For the 21 fibre supports F (the edges of K7), put delta_F=4-e_F and let
R be the normalized fibre compression.  If P_f is the orthogonal projector
away from the fixed 12 and -2^6 eigenspaces, then

    Z = 4 * (3 P_f - R|_{P_f})

is positive semidefinite.  Direct evaluation of the two fixed projectors
gives

    Z_FF = 2 delta_F,
    Z_FG = -D_FG       when F,G overlap,
    Z_FG = 4-D_FG      when F,G are disjoint.

Moreover Z L=0, where L is the (unsigned) edge--vertex incidence matrix of
K7.  Rows with delta_F=0 vanish by positive semidefiniteness, so on the
exceptional supports every Gram vector is nonzero and their unsigned sum at
each group is zero.

This script applies only the resulting *support and diagonal* condition.  It
uses exact Fraction Gaussian elimination: if W spans ker(L^T), every such Z
has form W H W^T with H PSD, and diag(Z)=2 delta becomes a rational linear
system in the symmetric entries of H.  Inconsistent systems are rigorous
support exclusions.  When H is unique, all principal minors are checked
exactly to decide PSD.  Underdetermined consistent systems are conservatively
left undecided.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
import itertools
import json
from pathlib import Path


def rref(matrix):
    a = [[Fraction(value) for value in row] for row in matrix]
    if not a:
        return a, []
    rows = len(a)
    cols = len(a[0])
    pivots = []
    row = 0
    for col in range(cols):
        pivot = next((i for i in range(row, rows) if a[i][col]), None)
        if pivot is None:
            continue
        a[row], a[pivot] = a[pivot], a[row]
        scale = a[row][col]
        a[row] = [value / scale for value in a[row]]
        for i in range(rows):
            if i == row or not a[i][col]:
                continue
            scale = a[i][col]
            a[i] = [x - scale * y for x, y in zip(a[i], a[row])]
        pivots.append(col)
        row += 1
        if row == rows:
            break
    return a, pivots


def nullspace(matrix):
    """Return a column basis for the rational right kernel."""
    if not matrix:
        return []
    reduced, pivots = rref(matrix)
    cols = len(matrix[0])
    free = [col for col in range(cols) if col not in pivots]
    basis = []
    for free_col in free:
        vector = [Fraction(0) for _ in range(cols)]
        vector[free_col] = 1
        for row, pivot_col in enumerate(pivots):
            vector[pivot_col] = -reduced[row][free_col]
        basis.append(vector)
    return basis


def linear_system_status(coefficients, targets):
    augmented = [list(row) + [target] for row, target in zip(coefficients, targets)]
    reduced, pivots_aug = rref(augmented)
    variables = len(coefficients[0]) if coefficients else 0
    inconsistent = any(
        all(not value for value in row[:variables]) and row[variables]
        for row in reduced
    )
    if inconsistent:
        return {"consistent": False, "rank": None, "solution_dimension": None}
    pivots = [pivot for pivot in pivots_aug if pivot < variables]
    dimension = variables - len(pivots)
    result = {
        "consistent": True,
        "rank": len(pivots),
        "solution_dimension": dimension,
    }
    if dimension == 0:
        solution = [Fraction(0) for _ in range(variables)]
        for row_index, pivot in enumerate(pivots):
            solution[pivot] = reduced[row_index][variables]
        result["unique_solution"] = solution
    return result


def determinant(matrix):
    a = [[Fraction(value) for value in row] for row in matrix]
    n = len(a)
    answer = Fraction(1)
    for col in range(n):
        pivot = next((row for row in range(col, n) if a[row][col]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != col:
            a[col], a[pivot] = a[pivot], a[col]
            answer = -answer
        value = a[col][col]
        answer *= value
        for row in range(col + 1, n):
            if not a[row][col]:
                continue
            scale = a[row][col] / value
            for j in range(col + 1, n):
                a[row][j] -= scale * a[col][j]
    return answer


def psd_by_principal_minors(matrix):
    n = len(matrix)
    minimum = None
    bad_subset = None
    for size in range(1, n + 1):
        for subset in itertools.combinations(range(n), size):
            minor = [[matrix[i][j] for j in subset] for i in subset]
            value = determinant(minor)
            if minimum is None or value < minimum:
                minimum = value
            if value < 0:
                bad_subset = subset
                return False, minimum, bad_subset
    return True, minimum if minimum is not None else Fraction(0), bad_subset


def analyze_support(exceptional):
    supports = [tuple(item["support"]) for item in exceptional]
    deficits = [int(item["deficit"]) for item in exceptional]
    m = len(supports)
    incidence_t = [
        [int(group in support) for support in supports]
        for group in range(7)
    ]
    basis_columns = nullspace(incidence_t)
    d = len(basis_columns)
    # W has one row per exceptional support and one column per kernel basis vector.
    W = [[basis_columns[j][i] for j in range(d)] for i in range(m)]
    pairs = [(a, b) for a in range(d) for b in range(a, d)]
    coefficients = []
    for row in W:
        coefficients.append([
            row[a] * row[b] * (1 if a == b else 2)
            for a, b in pairs
        ])
    status = linear_system_status(coefficients, [2 * value for value in deficits])
    result = {
        "exceptional_support_count": m,
        "unsigned_incidence_kernel_dimension": d,
        "gram_diagonal_system_consistent": status["consistent"],
        "gram_parameter_count": len(pairs),
        "gram_diagonal_system_rank": status["rank"],
        "gram_diagonal_solution_dimension": status["solution_dimension"],
    }
    if status.get("unique_solution") is not None:
        H = [[Fraction(0) for _ in range(d)] for _ in range(d)]
        for value, (a, b) in zip(status["unique_solution"], pairs):
            H[a][b] = H[b][a] = value
        is_psd, minimum_minor, bad_subset = psd_by_principal_minors(H)
        Z = [
            [
                sum(W[i][a] * H[a][b] * W[j][b]
                    for a in range(d) for b in range(d))
                for j in range(m)
            ]
            for i in range(m)
        ]
        assert [Z[i][i] for i in range(m)] == [2 * value for value in deficits]
        result.update({
            "unique_gram_parameter_matrix": [[str(value) for value in row] for row in H],
            "unique_Z_matrix": [[str(value) for value in row] for row in Z],
            "unique_gram_parameter_matrix_psd": is_psd,
            "minimum_checked_principal_minor": str(minimum_minor),
            "first_negative_principal_minor_subset": (
                None if bad_subset is None else list(bad_subset)
            ),
        })
    result["passes_exact_support_diagonal_psd_test"] = (
        status["consistent"] and result.get("unique_gram_parameter_matrix_psd", True)
    )
    return result


def audit(source_path):
    source = json.loads(source_path.read_text(encoding="utf-8"))
    output_rows = []
    for index, row in enumerate(source["rows"]):
        result = analyze_support(row["exceptional_supports"])
        result.update({
            "source_row_index": index,
            "partition": row["partition"],
            "orbit_index": row["orbit_index"],
            "orbit_size": row["orbit_size"],
        })
        output_rows.append(result)
    passing = [row for row in output_rows if row["passes_exact_support_diagonal_psd_test"]]
    inconsistent = [row for row in output_rows if not row["gram_diagonal_system_consistent"]]
    unique_nonpsd = [
        row for row in output_rows
        if row.get("unique_gram_parameter_matrix_psd") is False
    ]
    return {
        "model": "exact support-diagonal PSD filter from Z=4(3P_f-R_f)",
        "source": str(source_path),
        "derivation": {
            "Z_diagonal": "2*delta_F",
            "Z_overlap": "-D_FG",
            "Z_disjoint": "4-D_FG",
            "psd": True,
            "kernel": "Z L=0 for the unsigned K7 edge--group incidence L",
            "factorization": "Z=W H W^T, H positive semidefinite, columns(W)=ker(L^T)",
        },
        "scope_warning": (
            "Underdetermined consistent diagonal systems are retained; passing this "
            "filter does not assert that a full PSD or graph completion exists."
        ),
        "counts": {
            "input_rows": len(output_rows),
            "inconsistent_diagonal_systems": len(inconsistent),
            "unique_but_non_psd_systems": len(unique_nonpsd),
            "passing_or_undecided_rows": len(passing),
            "passing_or_undecided_labelled_weight": sum(row["orbit_size"] for row in passing),
        },
        "kernel_dimension_histogram": {
            str(value): sum(row["unsigned_incidence_kernel_dimension"] == value for row in output_rows)
            for value in sorted({row["unsigned_incidence_kernel_dimension"] for row in output_rows})
        },
        "solution_dimension_histogram": {
            str(value): sum(row["gram_diagonal_solution_dimension"] == value for row in output_rows)
            for value in sorted({
                row["gram_diagonal_solution_dimension"]
                for row in output_rows
                if row["gram_diagonal_solution_dimension"] is not None
            })
        },
        "rows": output_rows,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = audit(args.source)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["counts"], sort_keys=True))


if __name__ == "__main__":
    main()
