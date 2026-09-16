"""Evaluate the full residual -4 projector on the stored source-724 degree configuration.

This is a diagnostic on one of the 128 rank-three configurations, not a
whole-macro exclusion.  Unlike the previously materialized arbitrary
disjoint-block graph, the `neither adjacency value allowed` count below is
independent of how those blocks are realized.
"""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
import hashlib
import itertools
import json
import os
from pathlib import Path


WITNESS = Path("scratch_theory_e71_source724_degree_witness.json")
PROBE = Path("scratch_theory_e71_defect_rank_probe.json")
OUTPUT = Path("scratch_theory_e71_source724_projector_residual_probe.json")
SUPPORTS = tuple(itertools.combinations(range(7), 2))


def inverse(matrix):
    size = len(matrix)
    work = [
        [Fraction(value) for value in matrix[row]]
        + [Fraction(int(row == column)) for column in range(size)]
        for row in range(size)
    ]
    for column in range(size):
        pivot = next(row for row in range(column, size) if work[row][column])
        work[column], work[pivot] = work[pivot], work[column]
        scale = work[column][column]
        work[column] = [value / scale for value in work[column]]
        for row in range(size):
            if row == column or not work[row][column]:
                continue
            scale = work[row][column]
            work[row] = [
                left - scale * right
                for left, right in zip(work[row], work[column])
            ]
    return [row[size:] for row in work]


def determinant(matrix):
    work = [[Fraction(value) for value in row] for row in matrix]
    answer = Fraction(1)
    for column in range(len(work)):
        pivot = next(
            (row for row in range(column, len(work)) if work[row][column]), None
        )
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            answer = -answer
        scale = work[column][column]
        answer *= scale
        for row in range(column + 1, len(work)):
            if not work[row][column]:
                continue
            ratio = work[row][column] / scale
            for target in range(column, len(work)):
                work[row][target] -= ratio * work[column][target]
    return answer


def atomic_json(path, value):
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def main():
    witness_raw = WITNESS.read_bytes()
    probe_raw = PROBE.read_bytes()
    witness = json.loads(witness_raw)
    probe = json.loads(probe_raw)
    profile = next(row for row in probe["rows"] if tuple(row["key"]) == (724, 1, 0))
    Z = [[int(value) for value in row] for row in profile["Z"]]
    pivot = next(
        indices
        for indices in itertools.combinations(range(21), 3)
        if determinant([[Z[i][j] for j in indices] for i in indices])
    )
    inverse_minor = inverse([[Z[i][j] for j in pivot] for i in pivot])

    adjacency = [0] * 84
    for left, right in witness["edge_list_zero_based"]:
        adjacency[left] |= 1 << right
        adjacency[right] |= 1 << left
    C = [[0] * 21 for _ in range(21)]
    for left, right in witness["edge_list_zero_based"]:
        G, F = left // 4, right // 4
        if G == F:
            C[G][G] += 2
        else:
            C[G][F] += 1
            C[F][G] += 1
    R = [[0] * 21 for _ in range(84)]
    for vertex in range(84):
        G = vertex // 4
        for F in range(21):
            degree = sum(
                (adjacency[vertex] >> other) & 1
                for other in range(4 * F, 4 * F + 4)
            )
            R[vertex][F] = 4 * degree - C[G][F]
    s = [
        [Z[vertex // 4][column] - R[vertex][column] for column in range(21)]
        for vertex in range(84)
    ]

    def bilinear(left, right):
        l = [Fraction(left[index]) for index in pivot]
        r = [Fraction(right[index]) for index in pivot]
        return sum(
            l[i] * inverse_minor[i][j] * r[j]
            for i in range(3)
            for j in range(3)
        )

    labels = tuple(
        (2 * i + a, 2 * j + b)
        for i, j in SUPPORTS
        for a, b in itertools.product((0, 1), repeat=2)
    )
    diagonal = [Fraction(40) - bilinear(row, row) for row in s]
    assert min(diagonal) >= 0
    domains = Counter()
    chosen_bad = 0
    neither_pairs = []
    pair_rows = []
    scaled_residual = [[Fraction(0) for _ in range(84)] for _ in range(84)]
    for vertex in range(84):
        scaled_residual[vertex][vertex] = diagonal[vertex]
    for left, right in itertools.combinations(range(84), 2):
        q = len(set(labels[left]) & set(labels[right]))
        d = sum(1 for value in labels[left] if (value ^ 1) in labels[right])
        h = bilinear(s[left], s[right])
        values = []
        determinants = []
        for edge in (0, 1):
            off_diagonal = Fraction(4 - 6 * q - 2 * d - 16 * edge) - h
            det = diagonal[left] * diagonal[right] - off_diagonal**2
            determinants.append(det)
            if det >= 0:
                values.append(edge)
        domain = "neither" if not values else "both" if len(values) == 2 else f"only_{values[0]}"
        domains[domain] += 1
        chosen = (adjacency[left] >> right) & 1
        chosen_bad += int(chosen not in values)
        chosen_off_diagonal = (
            Fraction(4 - 6 * q - 2 * d - 16 * chosen) - h
        )
        scaled_residual[left][right] = chosen_off_diagonal
        scaled_residual[right][left] = chosen_off_diagonal
        if not values and len(neither_pairs) < 40:
            neither_pairs.append(
                {
                    "vertices": [left, right],
                    "supports": [list(SUPPORTS[left // 4]), list(SUPPORTS[right // 4])],
                    "local_indices": [left % 4, right % 4],
                    "q": q,
                    "d": d,
                    "diagonal": [str(diagonal[left]), str(diagonal[right])],
                    "h": str(h),
                    "determinants_for_B_0_1": [str(value) for value in determinants],
                }
            )
        pair_rows.append((left, right, domain))

    idempotent_diagonal_residuals = []
    for vertex in range(84):
        square_diagonal = sum(value * value for value in scaled_residual[vertex])
        idempotent_diagonal_residuals.append(
            square_diagonal - 112 * scaled_residual[vertex][vertex]
        )
    idempotent_histogram = Counter(map(str, idempotent_diagonal_residuals))

    result = {
        "status": "EXACT_SOURCE724_FIRST_CONFIG_PROJECTOR_RESIDUAL_PROBE",
        "inputs": {
            str(WITNESS): hashlib.sha256(witness_raw).hexdigest().upper(),
            str(PROBE): hashlib.sha256(probe_raw).hexdigest().upper(),
        },
        "macro_key": [724, 1, 0],
        "configuration_scope": "first stored one of 128 rank-three feasible configurations",
        "projector": {
            "definition": "G4=112*(E_-4-proj_range(E_-4 U))",
            "diagonal": "40-s_x Z^+ s_x with s_x=Z_G-R_x",
            "off_diagonal": "4-6q_xy-2d_xy-16B_xy-s_x Z^+ s_y",
            "necessary_condition": "G4 is positive semidefinite of rank at most 27",
        },
        "diagonal_minimum": str(min(diagonal)),
        "diagonal_maximum": str(max(diagonal)),
        "pair_adjacency_domain_histogram": dict(sorted(domains.items())),
        "pairs_with_neither_adjacency_value_allowed": domains["neither"],
        "chosen_materialization_pair_violations": chosen_bad,
        "scaled_projector_diagonal_idempotence": {
            "required_equation": "diag(G4^2-112G4)=0",
            "residual_histogram": dict(sorted(idempotent_histogram.items())),
            "zero_vertices": sum(value == 0 for value in idempotent_diagonal_residuals),
        },
        "first_neither_pairs": neither_pairs,
        "configuration_conclusion": (
            "CONFIGURATION_EXCLUDED_INDEPENDENT_OF_DISJOINT_BLOCK_REALIZATION"
            if domains["neither"]
            else "PAIRWISE_PROJECTOR_MINORS_DO_NOT_EXCLUDE_THIS_CONFIGURATION"
        ),
        "claim_boundary": (
            "This concerns one stored degree configuration only. It does not exclude "
            "the other 127 configurations or the whole source-724 macro."
        ),
        "submission_txt_written": False,
    }
    atomic_json(OUTPUT, result)
    print(
        json.dumps(
            {
                "path": str(OUTPUT),
                "status": result["status"],
                "domains": result["pair_adjacency_domain_histogram"],
                "chosen_bad": chosen_bad,
                "idempotent_diagonal_zero_vertices": sum(
                    value == 0 for value in idempotent_diagonal_residuals
                ),
                "conclusion": result["configuration_conclusion"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
