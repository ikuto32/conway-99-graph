"""Exact minimal unmatched-slot localizer and its scoped no-go control.

This script performs no graph/SAT enumeration.  It reads only frozen Wave205
and Wave147/148 summaries, constructs the previously specified 99-root
abstract flag control, and checks the smallest target-slot-centering PSD
localizer.  It prints a JSON certificate; it does not create submission.txt.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter
from fractions import Fraction
from math import gcd, lcm
from pathlib import Path


ROOTS = 99
TRIANGLES = 231
FLAGS = 693

WAVE205_CERT = Path(
    "external_conway99_research/attempts/"
    "wave205-fourth-trace-hostile-controls/certificate.json"
)
WAVE205_EXACT = Path(
    "external_conway99_research/attempts/"
    "wave205-global-fourth-moment-proof-b/exact-results.json"
)
WAVE205_PROJECTION_AUDIT = Path(
    "scratch_theory_flag_support_wave205_control_projection_independent_audit.json"
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

DSETS = (
    frozenset((1, 2, 4, 5, 6)),
    frozenset((3, 7, 9, 10, 11)),
    frozenset((8, 12, 13, 14, 15, 16)),
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def root_id(layer: int, coordinate: int) -> int:
    return 33 * layer + coordinate % 33


def triangle_id(parallel_class: int, coordinate: int) -> int:
    return 33 * parallel_class + coordinate % 33


def flag_id(triangle: int, slot: int) -> int:
    return 3 * triangle + slot


def pair(left: int, right: int) -> tuple[int, int]:
    if left == right:
        raise AssertionError("loop")
    return (left, right) if left < right else (right, left)


def build_blocks() -> list[tuple[int, int, int]]:
    return [
        tuple(
            root_id(slot, coordinate + slot * parallel_class)
            for slot in range(3)
        )
        for parallel_class in range(7)
        for coordinate in range(33)
    ]


def build_x_edges() -> set[tuple[int, int]]:
    edges: set[tuple[int, int]] = set()
    for parallel_class in range(7):
        for coordinate in range(33):
            source = triangle_id(parallel_class, coordinate)
            for slot, differences in enumerate(DSETS):
                for difference in differences:
                    target = triangle_id(
                        parallel_class, coordinate + difference
                    )
                    edges.add(
                        pair(flag_id(source, slot), flag_id(target, slot))
                    )
    for parallel_class in range(7):
        for coordinate in range(33):
            source = triangle_id(parallel_class, coordinate)
            target0 = triangle_id(
                (parallel_class + 1) % 7, coordinate + 3
            )
            target1 = triangle_id(
                (parallel_class + 1) % 7, coordinate + 7
            )
            edges.add(pair(flag_id(source, 0), flag_id(target0, 0)))
            edges.add(pair(flag_id(source, 1), flag_id(target1, 1)))
    return edges


def rank_mod(matrix: list[list[int]], prime: int) -> int:
    work = [[entry % prime for entry in row] for row in matrix]
    row = 0
    for column in range(len(work[0])):
        pivot = next(
            (index for index in range(row, len(work)) if work[index][column]),
            None,
        )
        if pivot is None:
            continue
        work[row], work[pivot] = work[pivot], work[row]
        inverse = pow(work[row][column], -1, prime)
        work[row] = [(inverse * value) % prime for value in work[row]]
        for index in range(len(work)):
            if index == row or work[index][column] == 0:
                continue
            multiple = work[index][column]
            work[index] = [
                (left - multiple * right) % prime
                for left, right in zip(work[index], work[row])
            ]
        row += 1
        if row == len(work):
            break
    return row


def primitive_integer_nullspace(matrix: list[list[int]]) -> list[list[int]]:
    """Return a deterministic primitive Z-basis of the rational nullspace."""
    work = [[Fraction(entry) for entry in row] for row in matrix]
    pivots: list[int] = []
    pivot_row = 0
    width = len(work[0])
    for column in range(width):
        source = next(
            (index for index in range(pivot_row, len(work))
             if work[index][column]),
            None,
        )
        if source is None:
            continue
        work[pivot_row], work[source] = work[source], work[pivot_row]
        pivot = work[pivot_row][column]
        work[pivot_row] = [value / pivot for value in work[pivot_row]]
        for index in range(len(work)):
            if index == pivot_row or work[index][column] == 0:
                continue
            multiple = work[index][column]
            work[index] = [
                left - multiple * right
                for left, right in zip(work[index], work[pivot_row])
            ]
        pivots.append(column)
        pivot_row += 1
        if pivot_row == len(work):
            break
    free = [column for column in range(width) if column not in pivots]
    basis = []
    for free_column in free:
        vector = [Fraction(0) for _ in range(width)]
        vector[free_column] = 1
        for row, pivot_column in enumerate(pivots):
            vector[pivot_column] = -work[row][free_column]
        denominator = 1
        for value in vector:
            denominator = lcm(denominator, value.denominator)
        integers = [int(value * denominator) for value in vector]
        divisor = 0
        for value in integers:
            divisor = gcd(divisor, abs(value))
        integers = [value // divisor for value in integers]
        first = next(value for value in integers if value)
        if first < 0:
            integers = [-value for value in integers]
        basis.append(integers)
    return basis


def dot(left: list[int], right: list[int]) -> int:
    return sum(a * b for a, b in zip(left, right))


def local_slot_basis() -> dict:
    grouped: dict[int, list[dict]] = {value: [] for value in range(7)}
    for vector in itertools.product(range(3), repeat=3):
        mass = sum(vector)
        square = sum(value * value for value in vector)
        support = sum(value > 0 for value in vector)
        collision = sum(value * (value - 1) // 2 for value in vector)
        assert collision == (square - mass) // 2 == mass - support
        assert 3 * square - mass * mass >= 0
        assert collision >= max(0, mass - 3)
        grouped[mass].append(
            {
                "p": list(vector),
                "square": square,
                "support": support,
                "collision": collision,
            }
        )
    table = []
    for mass, records in grouped.items():
        collisions = [record["collision"] for record in records]
        if not collisions:
            continue
        minimum = min(collisions)
        witnesses = [
            record["p"] for record in records if record["collision"] == minimum
        ]
        assert minimum == max(0, mass - 3)
        table.append(
            {
                "mass": mass,
                "minimum_collision": minimum,
                "witness": min(witnesses),
                "state_count": len(records),
            }
        )
    return {
        "states_checked": 27,
        "mass_range": [0, 6],
        "integer_envelope": "d(p)>=max(0,m(p)-3)",
        "table": table,
        "symmetric_quadratic_psd_cone": (
            "a*I+b*J is PSD iff a>=0 and a+3b>=0"
        ),
        "optimal_nontrivial_boundary_ray": "3*I-J",
        "quadratic_bound": "6*d(p)>=m(p)^2-3*m(p)",
        "optimality_reason": (
            "averaging any canonical quadratic slot form over S3 preserves "
            "PSD; for a*I+b*J, minimizing b/a subject to PSD gives b/a=-1/3"
        ),
    }


def build_control() -> dict:
    blocks = build_blocks()
    assert len(blocks) == TRIANGLES and len(set(blocks)) == TRIANGLES
    flag_root = [0] * FLAGS
    root_blocks = [[] for _ in range(ROOTS)]
    for triangle, block in enumerate(blocks):
        for slot, root in enumerate(block):
            flag_root[flag_id(triangle, slot)] = root
            root_blocks[root].append(triangle)
    assert {len(items) for items in root_blocks} == {7}

    edges = build_x_edges()
    assert len(edges) == 4158
    neighbors = [set() for _ in range(FLAGS)]
    for left, right in edges:
        neighbors[left].add(right)
        neighbors[right].add(left)
    assert {len(items) for items in neighbors} == {12}

    # Y=F^T X and M=Y C, where C is the flag-to-triangle collapse.
    y = [[0] * FLAGS for _ in range(ROOTS)]
    for source, targets in enumerate(neighbors):
        root = flag_root[source]
        for target in targets:
            y[root][target] += 1
    assert {value for row in y for value in row} == {0, 1}
    assert {sum(row) for row in y} == {84}
    m = [
        [sum(row[3 * triangle:3 * triangle + 3]) for triangle in range(TRIANGLES)]
        for row in y
    ]

    h_same = [[dot(y[left], y[right]) for right in range(ROOTS)]
              for left in range(ROOTS)]
    h_all = [[dot(m[left], m[right]) for right in range(ROOTS)]
             for left in range(ROOTS)]
    centered = [
        [3 * h_same[left][right] - h_all[left][right]
         for right in range(ROOTS)]
        for left in range(ROOTS)
    ]
    assert all(
        centered[left][right] == centered[right][left]
        for left in range(ROOTS) for right in range(ROOTS)
    )

    # Entrywise replay of Y (direct sum_U (3I_3-J_3)) Y^T.
    for left in range(ROOTS):
        for right in range(ROOTS):
            replay = 0
            for triangle in range(TRIANGLES):
                lp = y[left][3 * triangle:3 * triangle + 3]
                rp = y[right][3 * triangle:3 * triangle + 3]
                replay += 3 * dot(lp, rp) - sum(lp) * sum(rp)
            assert replay == centered[left][right]

    modular_ranks = {
        str(prime): rank_mod(centered, prime)
        for prime in (101, 103, 107)
    }
    centered_rank_lower = max(modular_ranks.values())
    nullspace = primitive_integer_nullspace(centered)
    assert all(all(dot(row, vector) == 0 for row in centered)
               for vector in nullspace)
    assert rank_mod(nullspace, 101) == len(nullspace)
    centered_rank = ROOTS - len(nullspace)
    assert centered_rank == centered_rank_lower
    collision_rows = [
        sum(value * (value - 1) // 2 for value in row) for row in y
    ]
    assert set(collision_rows) == {0}
    inequality_rhs_numerators = [
        sum(value * value for value in row) - 3 * sum(value for value in row)
        for row in m
    ]
    assert all(6 * collision_rows[root] >= inequality_rhs_numerators[root]
               for root in range(ROOTS))

    return {
        "roots": ROOTS,
        "triangles": TRIANGLES,
        "flags": FLAGS,
        "X_degree": 12,
        "Y_entry_alphabet": [0, 1],
        "Y_row_sum_set": sorted({sum(row) for row in y}),
        "Y_row_support_set": sorted({sum(value > 0 for value in row) for row in y}),
        "D_row_set": sorted(set(collision_rows)),
        "formal_E0_row_set": [84 - sum(value > 0 for value in row) for row in y[:1]],
        "M_equals_YC_entry_histogram": {
            str(key): value
            for key, value in sorted(Counter(value for row in m for value in row).items())
        },
        "M_row_square_sum_histogram": {
            str(key): value
            for key, value in sorted(Counter(sum(value * value for value in row)
                                             for row in m).items())
        },
        "six_D_lower_bound_rhs_numerator_histogram": {
            str(key): value
            for key, value in sorted(Counter(inequality_rhs_numerators).items())
        },
        "three_Lambda_equals_3YYT_minus_MMT": {
            "diagonal_histogram": {
                str(key): value for key, value in sorted(Counter(
                    centered[index][index] for index in range(ROOTS)
                ).items())
            },
            "entry_histogram_upper_triangle": {
                str(key): value for key, value in sorted(Counter(
                    centered[left][right]
                    for left in range(ROOTS) for right in range(left, ROOTS)
                ).items())
            },
            "rank_mod_primes": modular_ranks,
            "rational_rank": centered_rank,
            "primitive_integer_nullity": len(nullspace),
            "nullspace_basis_sha256": hashlib.sha256(
                json.dumps(nullspace, separators=(",", ":")).encode("ascii")
            ).hexdigest(),
            "nullspace_basis_l1_norms": [sum(map(abs, vector))
                                           for vector in nullspace],
            "nullspace_basis_max_abs": [max(map(abs, vector))
                                          for vector in nullspace],
            "positive_definite_over_Q": centered_rank == ROOTS,
            "proof": (
                "3I_3-J_3 is PSD on every target triangle; modular rank is "
                "a rational lower bound and the explicit independent integer "
                "nullspace basis supplies the matching upper bound"
            ),
        },
        "scope_failures": [
            "formal K2 is not the actual two-cross relation of the shadow",
            "the integral projector and transport equations fail",
            "the shadow is not srg(99,14,1,2)",
        ],
    }


def frozen_inputs() -> dict:
    wave205 = json.loads(WAVE205_EXACT.read_text(encoding="utf-8"))
    projection = json.loads(WAVE205_PROJECTION_AUDIT.read_text(encoding="utf-8"))
    wave147 = json.loads(WAVE147.read_text(encoding="utf-8"))
    wave148 = json.loads(WAVE148.read_text(encoding="utf-8"))
    boundary = json.loads(ORDER8_BOUNDARY.read_text(encoding="utf-8"))
    certificate = json.loads(WAVE205_CERT.read_text(encoding="utf-8"))
    assert len(certificate["blocks"]) == 231
    assert projection["certificate_sha256"] == digest(WAVE205_CERT)
    assert wave205["actual_incidence_factorization"]["star_pair_feature_control"][
        "star_pair_feature_rank"
    ] == 99
    assert wave205["positive_control"]["fourth_trace_matrix_rank"] == 9
    assert wave205["positive_control"]["fourth_trace_diagonal_zero"] is True
    assert wave147["class_streams"]["8"]["count"] == 916
    assert wave147["artifact"]["deletion_rows"] == 208
    assert wave147["artifact"]["total_class_matrix_records"] == 2414
    assert wave148["complete_row_comparison"]["vertex_rows"] == 944
    assert wave148["complete_row_comparison"]["ordered_pair_rows"] == 4440
    # The already-audited boundary is read, not regenerated.
    assert boundary["status"].endswith("PASS")
    return {
        "sha256": {
            str(path): digest(path)
            for path in (
                WAVE205_CERT,
                WAVE205_EXACT,
                WAVE205_PROJECTION_AUDIT,
                WAVE147,
                WAVE148,
                ORDER8_BOUNDARY,
            )
        },
        "wave205": {
            "field": 3,
            "K_D_index": "((T,U),(R,S))",
            "K_D_entry": "D[T,R]D[R,U]D[U,S]D[S,T]",
            "U_index": "(x,(T,U))",
            "U_entry": "B[x,T]B[x,U]",
            "rank_U": 99,
            "hostile_fourth_trace_rank": 9,
            "hostile_fourth_trace_diagonal_zero": True,
            "real_psd_warning": (
                "a nonzero symmetric real lift with zero diagonal is indefinite "
                "on a 2-by-2 principal block; H=U K_D U^T is an F3 form, "
                "not a real PSD Gram"
            ),
        },
        "frozen_order8": {
            "classes": 916,
            "deletion_rows": 208,
            "marked_vertex_rows": 944,
            "marked_pair_rows": 4440,
            "coefficient_matrices": 2414,
            "regenerated": False,
        },
    }


def main() -> None:
    result = {
        "status": "EXACT_MINIMAL_UNMATCHED_SLOT_LOCALIZER_BOUNDARY_PASS",
        "exact_indices": {
            "sets": (
                "V:99 points, T:231 triangles, F={(T,t):t in T}:693 flags"
            ),
            "L": (
                "L[T,U]=1 iff T,U are disjoint with two cross edges; over F3 "
                "L=2*(D^(o2)-D) on the endpoint alphabet"
            ),
            "W": (
                "W[r,T,U]=B[r,T]L[T,U](1-(A B)[r,U]); this is one iff r is "
                "the unmatched source point of the L-pair"
            ),
            "X": "X[(T,r),(U,u)]=W[r,T,U]W[u,U,T]",
            "Y": "Y[r,(U,u)]=sum_T X[(T,r),(U,u)]",
            "C": "C[(U,u),R]=1 iff U=R (flag-to-triangle collapse)",
            "M": "M=Y C, so M[r,U]=sum_u Y[r,(U,u)]=sum_T W[r,T,U]",
            "Khat": (
                "Khat[(r,T),(s,T');U]=W[r,T,U]W[s,T',U]"
            ),
            "Theta": (
                "Theta[r,s]=sum_(U,T,T') Khat[(r,T),(s,T');U]=(M M^T)[r,s]"
            ),
            "same_slot_gram": "G_=Y Y^T",
            "all_slot_gram": "G_triangle=M M^T=Y C C^T Y^T",
            "minimal_cross_root_localizer": (
                "3 Lambda=3G_-G_triangle=Y(3I_693-C C^T)Y^T >= 0"
            ),
            "pointwise_contraction": (
                "6D(r)>=sum_U M[r,U]^2-3(84-S(r))"
            ),
            "integer_strengthening": (
                "D(r)>=sum_U max(0,M[r,U]-3)"
            ),
        },
        "slot_basis_search": local_slot_basis(),
        "frozen_inputs": frozen_inputs(),
        "strict_positive_T0_control": build_control(),
        "boundary": {
            "correct_direction_found": True,
            "proves_support_13_or_12": False,
            "reason": (
                "the contraction needs a new lower bound on sum_U M[r,U]^2 "
                "or on masses M[r,U]>=4; total mass and all Wave205 t-moments "
                "only recover 84-S(r)"
            ),
            "rank_no_go": (
                "the source star-pair feature has rank 99, and the unmatched "
                "localizer has strictly positive diagonal and rational rank 94 "
                "at formal E0=0; PSD positivity does not force D(r)>0"
            ),
            "order_boundary": (
                "diagonal root contractions reduce to order-at-most-eight, but "
                "the cross-root entries retain a shared target mate and reach "
                "order nine; the frozen order-eight package has no complete "
                "matrix evaluation of Lambda"
            ),
            "next_missing_invariant": (
                "a graph-specific concentration lower bound for the one-sided "
                "unmatched masses M[r,U], or the sparse marked order-nine "
                "cross-root entries of Lambda"
            ),
            "submission_created": False,
        },
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
