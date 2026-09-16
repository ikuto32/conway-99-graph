"""Exact abstract T=0 control for the triangle-flag support lane.

This is deliberately not an SRG construction.  It simultaneously realizes
the 99 root blocks, 231 distinct linear triangle triples, a 12-regular flag
matching X with a simple 36-regular triangle quotient K2, and binary Y=F^T X
with row support 84.  It also realizes the endpoint entry alphabet and all
row/diagonal moments of the integral triangle projector, including the
entrywise Schur selector for K2.  The full projector equation and the SRG
common-neighbour equations are checked and reported as the missing gates.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


OUTPUT = Path("scratch_theory_flag_support_endpoint_control.json")

ROOTS = 99
TRIANGLES = 231
FLAGS = 693

DSETS = (
    frozenset((1, 2, 4, 5, 6)),
    frozenset((3, 7, 9, 10, 11)),
    frozenset((8, 12, 13, 14, 15, 16)),
)

R0_GENERATORS = (
    (1, 1), (1, 2), (1, 4), (1, 5),
    (1, 8), (1, 9), (1, 10), (1, 11),
    (2, 1), (2, 3), (2, 6), (2, 7),
    (2, 8), (2, 9), (2, 11), (2, 12),
)


def root_id(layer: int, coordinate: int) -> int:
    return 33 * layer + coordinate % 33


def triangle_id(parallel_class: int, coordinate: int) -> int:
    return 33 * parallel_class + coordinate % 33


def flag_id(triangle: int, slot: int) -> int:
    return 3 * triangle + slot


def pair(left: int, right: int) -> tuple[int, int]:
    assert left != right
    return (left, right) if left < right else (right, left)


def build_triangles() -> list[tuple[int, int, int]]:
    # Seven parallel classes on Z_33 x {0,1,2}.
    return [
        tuple(root_id(slot, coordinate + slot * parallel_class)
              for slot in range(3))
        for parallel_class in range(7)
        for coordinate in range(33)
    ]


def build_x_edges() -> set[tuple[int, int]]:
    edges: set[tuple[int, int]] = set()

    # All pairs inside a parallel class, partitioned among the three slots.
    for parallel_class in range(7):
        for coordinate in range(33):
            source_triangle = triangle_id(parallel_class, coordinate)
            for slot, differences in enumerate(DSETS):
                for difference in differences:
                    target_triangle = triangle_id(
                        parallel_class, coordinate + difference
                    )
                    edges.add(pair(flag_id(source_triangle, slot),
                                   flag_id(target_triangle, slot)))

    # Two further 2-factors on triangle blocks, assigned to slots zero and one.
    for parallel_class in range(7):
        for coordinate in range(33):
            source = triangle_id(parallel_class, coordinate)
            next_class = (parallel_class + 1) % 7
            target0 = triangle_id(next_class, coordinate + 3)
            target1 = triangle_id(next_class, coordinate + 7)
            edges.add(pair(flag_id(source, 0), flag_id(target0, 0)))
            edges.add(pair(flag_id(source, 1), flag_id(target1, 1)))
    return edges


def quotient_edges(x_edges: set[tuple[int, int]]) -> set[tuple[int, int]]:
    return {pair(left // 3, right // 3) for left, right in x_edges}


def generator_edges(delta: int, shift: int) -> set[tuple[int, int]]:
    return {
        pair(
            triangle_id(parallel_class, coordinate),
            triangle_id((parallel_class + delta) % 7, coordinate + shift),
        )
        for parallel_class in range(7)
        for coordinate in range(33)
    }


def common_neighbour_histogram(adjacency: list[set[int]]) -> tuple[Counter, Counter]:
    adjacent = Counter()
    nonadjacent = Counter()
    for left in range(len(adjacency)):
        for right in range(left + 1, len(adjacency)):
            value = len(adjacency[left] & adjacency[right])
            (adjacent if right in adjacency[left] else nonadjacent)[value] += 1
    return adjacent, nonadjacent


def main() -> None:
    blocks = build_triangles()
    assert len(blocks) == TRIANGLES
    assert len(set(blocks)) == TRIANGLES

    root_triangles = [[] for _ in range(ROOTS)]
    triangle_intersections = [set() for _ in range(TRIANGLES)]
    shadow = [set() for _ in range(ROOTS)]
    for triangle, block in enumerate(blocks):
        assert len(set(block)) == 3
        for root in block:
            root_triangles[root].append(triangle)
        for left_index in range(3):
            for right_index in range(left_index + 1, 3):
                left, right = block[left_index], block[right_index]
                shadow[left].add(right)
                shadow[right].add(left)
    assert {len(items) for items in root_triangles} == {7}
    assert {len(items) for items in shadow} == {14}
    assert all(len(set(root_triangles[left]) & set(root_triangles[right])) <= 1
               for left in range(ROOTS) for right in range(left + 1, ROOTS))

    for left in range(TRIANGLES):
        left_set = set(blocks[left])
        for right in range(left + 1, TRIANGLES):
            if left_set & set(blocks[right]):
                triangle_intersections[left].add(right)
                triangle_intersections[right].add(left)
    assert {len(items) for items in triangle_intersections} == {18}

    x_edges = build_x_edges()
    assert len(x_edges) == 4158
    x_neighbours = [set() for _ in range(FLAGS)]
    for left, right in x_edges:
        x_neighbours[left].add(right)
        x_neighbours[right].add(left)
    assert {len(items) for items in x_neighbours} == {12}

    k2 = quotient_edges(x_edges)
    assert len(k2) == len(x_edges)  # one unmatched-flag edge per triangle pair
    k2_neighbours = [set() for _ in range(TRIANGLES)]
    for left, right in k2:
        assert not (set(blocks[left]) & set(blocks[right]))
        k2_neighbours[left].add(right)
        k2_neighbours[right].add(left)
    assert {len(items) for items in k2_neighbours} == {36}

    # F maps a flag to its incident root.
    flag_root = [0] * FLAGS
    for triangle, block in enumerate(blocks):
        for slot, root in enumerate(block):
            flag_root[flag_id(triangle, slot)] = root

    # Y=F^T X, represented densely because its entry alphabet is central here.
    y = [[0] * FLAGS for _ in range(ROOTS)]
    for source in range(FLAGS):
        root = flag_root[source]
        for target in x_neighbours[source]:
            y[root][target] += 1
    y_entry_counts = Counter(value for row in y for value in row)
    assert set(y_entry_counts) == {0, 1}
    assert {sum(row) for row in y} == {84}
    assert {sum(value > 0 for value in row) for row in y} == {84}
    assert {
        sum(y[root][flag] for root in range(ROOTS))
        for flag in range(FLAGS)
    } == {12}

    # H=YY^T, calculated as support intersections (Y is binary here).
    y_support = [{index for index, value in enumerate(row) if value} for row in y]
    h = [[len(y_support[left] & y_support[right]) for right in range(ROOTS)]
         for left in range(ROOTS)]
    assert {h[root][root] for root in range(ROOTS)} == {84}
    assert {sum(row) for row in h} == {1008}
    h_total = sum(map(sum, h))
    h_offdiag_unordered = sum(
        h[left][right]
        for left in range(ROOTS) for right in range(left + 1, ROOTS)
    )
    assert h_total == 99792
    assert h_offdiag_unordered == 45738
    beta_edge = sum(
        h[left][right]
        for left in range(ROOTS) for right in range(left + 1, ROOTS)
        if right in shadow[left]
    )
    beta_nonedge = h_offdiag_unordered - beta_edge
    assert beta_edge == 0
    assert beta_nonedge == 45738

    # Wave205's t=N K2 N^T inflates both unmatched flags to their full
    # triangle triples.  It is recorded separately from YY^T.
    t_matrix = [[
        sum(pair(t, u) in k2
            for t in root_triangles[left] for u in root_triangles[right]
            if t != u)
        for right in range(ROOTS)]
        for left in range(ROOTS)
    ]
    assert {sum(row) for row in t_matrix} == {756}
    t_nonedge_row_sums = [
        sum(t_matrix[left][right]
            for right in range(ROOTS)
            if right != left and right not in shadow[left])
        for left in range(ROOTS)
    ]

    # Formal endpoint integral-projector alphabet M=4I+R0-K2.
    r0: set[tuple[int, int]] = set()
    for generator in R0_GENERATORS:
        new_edges = generator_edges(*generator)
        assert len(new_edges) == TRIANGLES
        assert not (r0 & new_edges)
        r0 |= new_edges
    assert len(r0) == 3696
    assert not (r0 & k2)
    assert all(not (set(blocks[left]) & set(blocks[right])) for left, right in r0)
    r0_neighbours = [set() for _ in range(TRIANGLES)]
    for left, right in r0:
        r0_neighbours[left].add(right)
        r0_neighbours[right].add(left)
    assert {len(items) for items in r0_neighbours} == {32}

    matrix = [[0] * TRIANGLES for _ in range(TRIANGLES)]
    for triangle in range(TRIANGLES):
        matrix[triangle][triangle] = 4
    for left, right in r0:
        matrix[left][right] = matrix[right][left] = 1
    for left, right in k2:
        matrix[left][right] = matrix[right][left] = -1

    assert {sum(row) for row in matrix} == {0}
    assert {sum(value * value for value in row) for row in matrix} == {84}
    matrix_row_profiles = Counter(tuple(Counter(row).get(value, 0)
                                        for value in (-1, 0, 1, 4))
                                  for row in matrix)
    assert matrix_row_profiles == Counter({(36, 162, 32, 1): TRIANGLES})

    schur = lambda value: (value ** 3 + value ** 2 - 2 * value) // 2
    for left in range(TRIANGLES):
        for right in range(TRIANGLES):
            selected = schur(matrix[left][right]) - 36 * (left == right)
            assert selected == int(left != right and pair(left, right) in k2)

    # The diagonal/trace pieces of M^2=21M pass, while the full equation does not.
    residual_histogram = Counter()
    first_projector_failure = None
    residual_frobenius_squared = 0
    for left in range(TRIANGLES):
        for right in range(TRIANGLES):
            residual = sum(matrix[left][middle] * matrix[middle][right]
                           for middle in range(TRIANGLES)) - 21 * matrix[left][right]
            residual_histogram[residual] += 1
            residual_frobenius_squared += residual * residual
            if residual and first_projector_failure is None:
                first_projector_failure = [left, right, residual]
    assert residual_histogram[0] >= TRIANGLES  # every diagonal is zero
    assert first_projector_failure is not None

    # The actual projector also obeys N M N^T=27I-9A+J.  Report this gate.
    transport_mismatch = Counter()
    first_transport_failure = None
    for left in range(ROOTS):
        for right in range(ROOTS):
            actual = sum(matrix[t][u]
                         for t in root_triangles[left]
                         for u in root_triangles[right])
            target = 28 if left == right else (-8 if right in shadow[left] else 1)
            difference = actual - target
            transport_mismatch[difference] += 1
            if difference and first_transport_failure is None:
                first_transport_failure = [left, right, actual, target, difference]
    assert first_transport_failure is not None

    adjacent_cn, nonadjacent_cn = common_neighbour_histogram(shadow)
    assert adjacent_cn != Counter({1: 693}) or nonadjacent_cn != Counter({2: 4158})

    actual_triangle_cross_profile = []
    actual_triangle_cross_global = Counter()
    for left in range(TRIANGLES):
        profile = Counter()
        for right in range(TRIANGLES):
            if right == left or right in triangle_intersections[left]:
                continue
            cross_edges = sum(v in shadow[u]
                              for u in blocks[left] for v in blocks[right])
            profile[cross_edges] += 1
            if left < right:
                actual_triangle_cross_global[cross_edges] += 1
        actual_triangle_cross_profile.append(profile)

    # Endpoint Bose--Mesner scalar window from YY^T.  The control passes it.
    n3 = 4158
    q2 = 231 * 12 * 12
    n_value = n3
    a_bounds = (3 * q2 // 11 - 4 * n_value, q2 // 6 + 3 * n_value)
    b_bounds = (4 * q2 // 3 - 4 * n_value,
                27 * q2 // 22 + 3 * n_value)
    assert a_bounds[0] <= beta_edge <= a_bounds[1]
    assert b_bounds[0] <= beta_nonedge <= b_bounds[1]

    result = {
        "status": "EXACT_ABSTRACT_FLAG_SUPPORT_T0_CONTROL_PASS",
        "scope": {
            "realizes": [
                "99 root blocks of seven flags",
                "231 distinct linear triangle triples",
                "14-regular triangle-shadow graph",
                "12-regular binary flag matching X",
                "simple 36-regular formal triangle quotient K2",
                "one abstract unmatched-flag edge above each formal K2 edge",
                "Y=F^T X in {0,1} with row support 84 and column sum 12",
                "formal endpoint triangle relation profile (a0,a1,a2,a3)=(32,144,36,0)",
                "formal M alphabet, row moments, and exact Schur selector K2",
                "YY^T positivity and numerical passage of the endpoint aggregate/Bose--Mesner scalar windows",
            ],
            "does_not_realize": [
                "M^2=21M",
                "N M N^T=27I-9A+J",
                "the SRG lambda/mu common-neighbour equations",
                "K2 as the actual two-cross-edge relation of the shadow graph",
                "a graph srg(99,14,1,2)",
            ],
        },
        "sizes": {
            "roots": ROOTS,
            "triangles": TRIANGLES,
            "flags": FLAGS,
            "root_degree_in_triangle_design": 7,
            "triangle_intersection_degree": 18,
            "shadow_degree": 14,
            "X_degree": 12,
            "X_edges": len(x_edges),
            "K2_degree": 36,
            "K2_edges": len(k2),
        },
        "formula": {
            "roots": "(a,j) in Z_3 x Z_33",
            "triangles": "T_(h,i)={(a,i+a*h):a=0,1,2}, h=0..6, i in Z_33",
            "same_class_slot_difference_sets": [sorted(values) for values in DSETS],
            "cross_slot_0": "(h,i)--(h+1,i+3)",
            "cross_slot_1": "(h,i)--(h+1,i+7)",
            "R0_generators": [list(item) for item in R0_GENERATORS],
        },
        "Y": {
            "entry_histogram": {str(k): v for k, v in sorted(y_entry_counts.items())},
            "row_sum_set": sorted({sum(row) for row in y}),
            "row_support_set": sorted({len(items) for items in y_support}),
            "column_sum_set": sorted({sum(y[root][flag] for root in range(ROOTS))
                                       for flag in range(FLAGS)}),
            "formal_E0_row_set": [0],
        },
        "YYT": {
            "diagonal_set": sorted({h[root][root] for root in range(ROOTS)}),
            "row_sum_set": sorted({sum(row) for row in h}),
            "entry_histogram": {str(k): v for k, v in sorted(Counter(
                h[left][right]
                for left in range(ROOTS) for right in range(left, ROOTS)
            ).items())},
            "total_mass": h_total,
            "unordered_offdiagonal_mass": h_offdiag_unordered,
            "shadow_edge_split": beta_edge,
            "shadow_nonedge_split": beta_nonedge,
            "endpoint_Bose_Mesner_windows": {
                "edge": list(a_bounds),
                "nonedge": list(b_bounds),
            },
        },
        "Wave205_t_equals_NK2NT": {
            "row_sum_set": sorted({sum(row) for row in t_matrix}),
            "adjacent_entry_histogram": {
                str(k): v for k, v in sorted(Counter(
                    t_matrix[left][right]
                    for left in range(ROOTS) for right in range(left + 1, ROOTS)
                    if right in shadow[left]
                ).items())
            },
            "nonadjacent_entry_histogram": {
                str(k): v for k, v in sorted(Counter(
                    t_matrix[left][right]
                    for left in range(ROOTS) for right in range(left + 1, ROOTS)
                    if right not in shadow[left]
                ).items())
            },
            "nonadjacent_row_sum_set": sorted(set(t_nonedge_row_sums)),
            "passes_target_endpoint_nonedge_rowsum_588":
                set(t_nonedge_row_sums) == {588},
            "scope": (
                "This abstract control is not an SRG and is not claimed to "
                "satisfy the Wave205 two-star theorem."
            ),
        },
        "formal_M": {
            "row_profile_order_-1_0_1_4": [36, 162, 32, 1],
            "row_sum": 0,
            "row_square_sum": 84,
            "trace_M": 924,
            "trace_M2": 19404,
            "trace_identity_21_trace_M": 21 * 924,
            "Schur_selector_K2": True,
            "projector_residual_histogram": {
                str(k): v for k, v in sorted(residual_histogram.items())
            },
            "projector_residual_frobenius_squared": residual_frobenius_squared,
            "first_projector_failure": first_projector_failure,
            "transport_mismatch_histogram": {
                str(k): v for k, v in sorted(transport_mismatch.items())
            },
            "first_transport_failure": first_transport_failure,
        },
        "shadow_common_neighbours": {
            "adjacent": {str(k): v for k, v in sorted(adjacent_cn.items())},
            "nonadjacent": {str(k): v for k, v in sorted(nonadjacent_cn.items())},
        },
        "actual_shadow_triangle_cross_edges": {
            "global_disjoint_pair_histogram": {
                str(k): v for k, v in sorted(actual_triangle_cross_global.items())
            },
            "per_triangle_profile_histogram": {
                json.dumps(dict(profile), separators=(",", ":")): count
                for profile, count in Counter(
                    tuple(sorted(item.items())) for item in actual_triangle_cross_profile
                ).items()
            },
            "K2_edges_with_exactly_two_actual_cross_edges": sum(
                sum(v in shadow[u] for u in blocks[left] for v in blocks[right]) == 2
                for left, right in k2
            ),
            "warning": (
                "The control's formal K2 is an unmatched-flag matching relation, "
                "but it is not the actual two-cross-edge relation of its non-SRG "
                "shadow graph."
            ),
        },
        "conclusion": (
            "The listed flag/root/triple/margin/support/Schur-row-moment data "
            "alone admit E0=0.  Any positive pointwise E0 bound must use at "
            "least the missing off-diagonal projector/incidence-transport or "
            "full SRG compatibility; this artifact is not a Conway graph."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
