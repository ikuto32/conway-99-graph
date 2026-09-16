"""Clean-room audit of the unmatched-slot localizer certificate.

The producer is never imported.  This script reconstructs the flag control
from its explicit cyclic formulas, proves PSD through a sum-of-squares
identity, and computes the rational rank by independent exact elimination.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path


EXPECTED = Path("scratch_theory_flag_support_unmatched_localizer.json")
WAVE205_CERT = Path(
    "external_conway99_research/attempts/"
    "wave205-fourth-trace-hostile-controls/certificate.json"
)
WAVE205_EXACT = Path(
    "external_conway99_research/attempts/"
    "wave205-global-fourth-moment-proof-b/exact-results.json"
)
WAVE147 = Path(
    "external_conway99_research/verification/"
    "wave147-pair-root-order8/verification-results.json"
)
WAVE148 = Path(
    "external_conway99_research/verification/"
    "wave148-marked-order8/verification-results.json"
)
ORDER8_BOUNDARY = Path("scratch_root_order8_e0_lower_bound_boundary.json")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rational_rank(matrix: list[list[int]]) -> int:
    """Forward-only exact elimination, separate from the producer's RREF."""
    work = [[Fraction(value) for value in row] for row in matrix]
    rank = 0
    width = len(work[0])
    for column in range(width):
        pivot = next(
            (row for row in range(rank, len(work)) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        pivot_value = work[rank][column]
        for row in range(rank + 1, len(work)):
            if work[row][column] == 0:
                continue
            factor = work[row][column] / pivot_value
            for target in range(column, width):
                work[row][target] -= factor * work[rank][target]
        rank += 1
        if rank == len(work):
            break
    return rank


def modular_rank(matrix: list[list[int]], prime: int) -> int:
    work = [[value % prime for value in row] for row in matrix]
    rank = 0
    for column in range(len(work[0])):
        pivot = next(
            (row for row in range(rank, len(work)) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        inverse = pow(work[rank][column], prime - 2, prime)
        for row in range(rank + 1, len(work)):
            if work[row][column] == 0:
                continue
            factor = work[row][column] * inverse % prime
            work[row] = [
                (left - factor * right) % prime
                for left, right in zip(work[row], work[rank])
            ]
        rank += 1
        if rank == len(work):
            break
    return rank


def reconstruct() -> tuple[list[list[int]], list[list[int]]]:
    # Triangle (h,i) has slot a at point (a,i+a*h), flattened as 33*a+j.
    blocks = []
    for h in range(7):
        for i in range(33):
            blocks.append(tuple(33 * a + (i + a * h) % 33 for a in range(3)))
    assert len(set(blocks)) == 231
    owner = [None] * 693
    for triangle, vertices in enumerate(blocks):
        for slot, vertex in enumerate(vertices):
            owner[3 * triangle + slot] = vertex

    neighbors = [set() for _ in range(693)]

    def add(left: int, right: int) -> None:
        assert left != right
        neighbors[left].add(right)
        neighbors[right].add(left)

    difference_sets = (
        (1, 2, 4, 5, 6),
        (3, 7, 9, 10, 11),
        (8, 12, 13, 14, 15, 16),
    )
    for h, i, slot in itertools.product(range(7), range(33), range(3)):
        source = 3 * (33 * h + i) + slot
        for delta in difference_sets[slot]:
            target = 3 * (33 * h + (i + delta) % 33) + slot
            add(source, target)
    for h, i in itertools.product(range(7), range(33)):
        source_triangle = 33 * h + i
        next_h = (h + 1) % 7
        add(3 * source_triangle,
            3 * (33 * next_h + (i + 3) % 33))
        add(3 * source_triangle + 1,
            3 * (33 * next_h + (i + 7) % 33) + 1)
    assert Counter(map(len, neighbors)) == Counter({12: 693})

    y = [[0] * 693 for _ in range(99)]
    for source in range(693):
        for target in neighbors[source]:
            y[owner[source]][target] += 1
    collapsed = [[sum(row[3 * t:3 * t + 3]) for t in range(231)] for row in y]
    return y, collapsed


def audit() -> dict:
    expected = json.loads(EXPECTED.read_text(encoding="utf-8"))
    frozen = expected["frozen_inputs"]
    observed_hashes = {
        "wave205_certificate_sha256": sha(WAVE205_CERT),
        "wave205_exact_results_sha256": sha(WAVE205_EXACT),
        "wave147_results_sha256": sha(WAVE147),
        "wave148_results_sha256": sha(WAVE148),
        "order8_boundary_sha256": sha(ORDER8_BOUNDARY),
    }
    assert all(frozen[key] == value for key, value in observed_hashes.items())

    wave205 = json.loads(WAVE205_EXACT.read_text(encoding="utf-8"))
    wave147 = json.loads(WAVE147.read_text(encoding="utf-8"))
    wave148 = json.loads(WAVE148.read_text(encoding="utf-8"))
    assert wave205["actual_incidence_factorization"]["star_pair_feature_control"][
        "star_pair_feature_rank"
    ] == 99
    positive = wave205["positive_control"]
    assert positive["fourth_trace_diagonal_zero"] is True
    assert positive["fourth_trace_matrix_rank"] == 9
    assert wave147["class_streams"]["8"]["count"] == 916
    assert wave147["artifact"]["deletion_rows"] == 208
    assert wave147["artifact"]["total_class_matrix_records"] == 2414
    assert wave148["complete_row_comparison"]["vertex_rows"] == 944
    assert wave148["complete_row_comparison"]["ordered_pair_rows"] == 4440

    # Exhaust the complete three-slot alphabet independently.
    minima = []
    for mass in range(7):
        states = [p for p in itertools.product((0, 1, 2), repeat=3)
                  if sum(p) == mass]
        values = [sum(value == 2 for value in p) for p in states]
        minima.append(min(values))
        for p, collision in zip(states, values):
            square = sum(value * value for value in p)
            support = sum(value != 0 for value in p)
            assert collision == (square - mass) // 2 == mass - support
            # Exact SOS: 3||p||^2-(1^T p)^2.
            sos = (p[0] - p[1]) ** 2 + (p[1] - p[2]) ** 2 + (p[2] - p[0]) ** 2
            assert 3 * square - mass * mass == sos >= 0
    assert minima == [0, 0, 0, 0, 1, 2, 3]
    assert minima == expected["slot_basis_search"]["minimum_collision_by_mass"]

    y, collapsed = reconstruct()
    assert Counter(value for row in y for value in row) == Counter({0: 60291, 1: 8316})
    assert {sum(row) for row in y} == {84}
    assert {sum(value != 0 for value in row) for row in y} == {84}
    assert Counter(value for row in collapsed for value in row) == Counter(
        {0: 14553, 1: 8316}
    )
    collision = [sum(value * (value - 1) // 2 for value in row) for row in y]
    assert set(collision) == {0}

    kernel = []
    for left in range(99):
        row = []
        for right in range(99):
            same = sum(a * b for a, b in zip(y[left], y[right]))
            all_slots = sum(a * b for a, b in zip(collapsed[left], collapsed[right]))
            row.append(3 * same - all_slots)
        kernel.append(row)
    assert {kernel[i][i] for i in range(99)} == {168}
    rank_q = rational_rank(kernel)
    ranks_p = [modular_rank(kernel, prime) for prime in (101, 103, 107)]
    assert rank_q == 94 and ranks_p == [94, 94, 94]
    assert rank_q == expected["strict_positive_T0_control"]["three_Lambda"][
        "rank_over_Q"
    ]

    # The block form is PSD without numerical eigenvalues: for v, put
    # z_(U,u)=sum_r v_r Y[r,(U,u)] and sum the three pairwise squares in U.
    # Positive diagonal plus D=0 is the needed hostile positivity control.
    rhs = [sum(value * value for value in row) - 3 * sum(row)
           for row in collapsed]
    assert set(rhs) == {-168}
    assert all(6 * collision[r] >= rhs[r] for r in range(99))

    return {
        "status": "INDEPENDENT_EXACT_UNMATCHED_SLOT_LOCALIZER_AUDIT_PASS",
        "producer_imported": False,
        "frozen_hashes_match": True,
        "slot_states_checked": 27,
        "minimum_collision_by_mass": minima,
        "psd_sum_of_squares": (
            "3||p||^2-(1^T p)^2=(p0-p1)^2+(p1-p2)^2+(p2-p0)^2"
        ),
        "control": {
            "Y_row_sum": 84,
            "Y_row_support": 84,
            "D_row": 0,
            "three_Lambda_diagonal": 168,
            "three_Lambda_rank_over_Q": rank_q,
            "three_Lambda_ranks_mod_101_103_107": ranks_p,
            "six_D_bound_rhs_numerator": -168,
        },
        "wave205_scope": {
            "rank_U": 99,
            "hostile_H_rank": 9,
            "hostile_H_diagonal_zero": True,
            "H_is_not_a_real_psd_gram": (
                "nonzero symmetric zero-diagonal H has an indefinite nonzero "
                "2-by-2 principal block under the canonical real residue lift"
            ),
        },
        "conclusion": (
            "the slot-centering contraction has the correct sign but is strict "
            "on every control diagonal while D=0; rank and PSD alone cannot "
            "prove a positive D or support-13/support-12 bound"
        ),
        "submission_created": False,
    }


if __name__ == "__main__":
    print(json.dumps(audit(), separators=(",", ":")))
