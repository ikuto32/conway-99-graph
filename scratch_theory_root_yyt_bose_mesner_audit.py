"""Independent exact audit of the YYT pair/Bose--Mesner note.

This checker does not import either discovery script.  It rebuilds the
34 matching cases, the nine marked order-nine coefficients, the two frozen
order-eight shadow vectors, and the selected four-root moment entries using
only Python's standard library.
"""

from __future__ import annotations

import gzip
import itertools
import json
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path


PAIR = Path("scratch_theory_root_yyt_pair_classification.json")
SHADOW = Path("scratch_theory_root_yyt_order8_shadow.json")
COEFFICIENTS = Path(
    "external_conway99_research/attempts/wave147-alternative-lane/coefficients.json.gz"
)
BOUNDARY = Path("scratch_root_order8_e0_lower_bound_boundary.json")
OUTPUT = Path("scratch_theory_root_yyt_bose_mesner_audit.json")


def pairs(order):
    return tuple(itertools.combinations(range(order), 2))


def norm(left, right):
    return (left, right) if left < right else (right, left)


def rows(order, edges):
    answer = [set() for _ in range(order)]
    for left, right in edges:
        answer[left].add(right)
        answer[right].add(left)
    return tuple(map(frozenset, answer))


def admissible(order, edges):
    graph = rows(order, edges)
    return all(
        len(graph[left] & graph[right]) <= (1 if right in graph[left] else 2)
        for left, right in pairs(order)
    )


def mask_from_edges(order, edges):
    index = {edge: position for position, edge in enumerate(pairs(order))}
    return sum(1 << index[norm(*edge)] for edge in edges)


def edges_from_mask(order, mask):
    return frozenset(edge for position, edge in enumerate(pairs(order))
                     if mask >> position & 1)


def degree_canonical(order, edges):
    graph = rows(order, edges)
    groups = defaultdict(list)
    for vertex in range(order):
        groups[len(graph[vertex])].append(vertex)
    target = 0
    cells = []
    for degree in sorted(groups):
        source = groups[degree]
        images = tuple(range(target, target + len(source)))
        target += len(source)
        cells.append(tuple(
            tuple(zip(source, permutation))
            for permutation in itertools.permutations(images)
        ))
    best = None
    for choice in itertools.product(*cells):
        permutation = [None] * order
        for cell in choice:
            for source, image in cell:
                permutation[source] = image
        value = mask_from_edges(order, (
            norm(permutation[left], permutation[right]) for left, right in edges
        ))
        best = value if best is None else min(best, value)
    assert best is not None
    return best


def triangle_rows(order, edges):
    graph = rows(order, edges)
    return tuple(
        triple for triple in itertools.combinations(range(order), 3)
        if all(right in graph[left]
               for left, right in itertools.combinations(triple, 2))
    )


def x_relation(source, source_root, target, target_root, edges):
    cross = frozenset(norm(left, right) for left in source for right in target
                      if norm(left, right) in edges)
    if len(cross) != 2:
        return False
    used_source = {vertex for edge in cross for vertex in edge if vertex in source}
    used_target = {vertex for edge in cross for vertex in edge if vertex in target}
    return (used_source == set(source) - {source_root}
            and used_target == set(target) - {target_root})


def mark_counts(order, edges):
    graph = rows(order, edges)
    tris = triangle_rows(order, edges)
    result = Counter()
    for root_left, root_right in itertools.combinations(range(order), 2):
        relation = "edge" if root_right in graph[root_left] else "nonedge"
        for left_triangle in tris:
            if root_left not in left_triangle:
                continue
            for right_triangle in tris:
                if root_right not in right_triangle:
                    continue
                if set(left_triangle) & set(right_triangle):
                    continue
                for target in tris:
                    if set(target) & (set(left_triangle) | set(right_triangle)):
                        continue
                    for target_root in target:
                        if (x_relation(left_triangle, root_left, target,
                                       target_root, edges)
                                and x_relation(right_triangle, root_right,
                                               target, target_root, edges)):
                            result[relation] += 1
    return result


def partial_matchings():
    result = []
    for size in range(4):
        for left in itertools.combinations((0, 1, 2), size):
            for right in itertools.combinations((3, 4, 5), size):
                for images in itertools.permutations(right):
                    result.append(frozenset(norm(a, b) for a, b in zip(left, images)))
    assert len(result) == 34
    return tuple(result)


def transform_mask(mask, order, permutation):
    source = edges_from_mask(order, mask)
    return mask_from_edges(order, (
        norm(permutation[left], permutation[right]) for left, right in source
    ))


def induced_mask(mask, graph_order, selected):
    source_edges = edges_from_mask(graph_order, mask)
    return mask_from_edges(len(selected), (
        (left_index, right_index)
        for left_index, left in enumerate(selected)
        for right_index, right in enumerate(selected)
        if left_index < right_index and norm(left, right) in source_edges
    ))


def canonical_flag(mask):
    return min(mask, transform_mask(mask, 6, (0, 1, 2, 3, 5, 4)))


def shadow_count(mask, root_edge):
    graph_edges = edges_from_mask(8, mask)
    graph = rows(8, graph_edges)
    tris = triangle_rows(8, graph_edges)
    count = 0
    universe = set(range(8))
    for root_left in range(8):
        for root_right in range(8):
            if root_left == root_right:
                continue
            if (root_right in graph[root_left]) != root_edge:
                continue
            for left_triangle in tris:
                if root_left not in left_triangle:
                    continue
                for right_triangle in tris:
                    if root_right not in right_triangle:
                        continue
                    if set(left_triangle) & set(right_triangle):
                        continue
                    target = tuple(sorted(universe - set(left_triangle)
                                          - set(right_triangle)))
                    if len(target) != 2 or norm(*target) not in graph_edges:
                        continue
                    okay = True
                    for triangle, root in ((left_triangle, root_left),
                                           (right_triangle, root_right)):
                        nonroots = tuple(vertex for vertex in triangle if vertex != root)
                        okay &= not any(vertex in graph[root] for vertex in target)
                        okay &= all(sum(vertex in graph[source] for vertex in target) == 1
                                    for source in nonroots)
                        okay &= all(sum(vertex in graph[source] for source in nonroots) == 1
                                    for vertex in target)
                    count += bool(okay)
    return count


def four_root_selected(mask, root_mask, left_flags, right_flags):
    total = 0
    vertices = tuple(range(8))
    for roots4 in itertools.permutations(vertices, 4):
        if induced_mask(mask, 8, roots4) != root_mask:
            continue
        complement = tuple(vertex for vertex in vertices if vertex not in roots4)
        free_pairs = tuple(itertools.combinations(complement, 2))
        flag = tuple(canonical_flag(induced_mask(mask, 8, roots4 + free))
                     for free in free_pairs)
        for left_index, left_pair in enumerate(free_pairs):
            for right_index, right_pair in enumerate(free_pairs):
                if set(left_pair) | set(right_pair) != set(complement):
                    continue
                total += (flag[left_index] in left_flags
                          and flag[right_index] in right_flags)
    return total


def main():
    pair_artifact = json.loads(PAIR.read_text(encoding="utf-8"))
    shadow_artifact = json.loads(SHADOW.read_text(encoding="utf-8"))
    boundary = json.loads(BOUNDARY.read_text(encoding="utf-8"))

    # Four possible overlaps of the two source triangles, independently built.
    overlap_failures = 0
    for first, second in itertools.product((0, 1), repeat=2):
        r, p, a, s, b, u, c, d = range(8)
        edges = {norm(r, p), norm(r, a), norm(p, a),
                 norm(s, p), norm(s, b), norm(p, b),
                 norm(u, c), norm(u, d), norm(c, d)}
        edges |= {norm(p, (c, d)[first]), norm(a, (d, c)[first]),
                  norm(p, (c, d)[second]), norm(b, (d, c)[second])}
        overlap_failures += not admissible(8, edges)
    assert overlap_failures == 4

    strict_base = {norm(*edge) for edge in {
        (0, 1), (0, 2), (1, 2), (3, 4), (3, 5), (4, 5),
        (7, 8), (1, 7), (2, 8), (4, 7), (5, 8), (6, 7), (6, 8),
    }}
    strict_completion_masks = []
    for left_bit, right_bit in itertools.product((0, 1), repeat=2):
        edges = set(strict_base)
        if left_bit:
            edges.add(norm(0, 6))
        if right_bit:
            edges.add(norm(3, 6))
        assert admissible(9, edges)
        strict_completion_masks.append(mask_from_edges(9, edges))
    assert strict_completion_masks == [
        64767402243, 64775790851, 64767402275, 64775790883
    ]

    base = frozenset(norm(*edge) for edge in {
        (0, 1), (0, 2), (1, 2), (3, 4), (3, 5), (4, 5),
        (6, 7), (6, 8), (7, 8),
        (1, 7), (2, 8), (4, 7), (5, 8),
    })
    representatives = {}
    feasible_marked = 0
    for matching in partial_matchings():
        edges = base | matching
        if not admissible(9, edges):
            continue
        feasible_marked += 1
        key = degree_canonical(9, edges)
        representatives.setdefault(key, edges)
    assert feasible_marked == 18 and len(representatives) == 9
    rebuilt_types = {}
    for key, edges in representatives.items():
        marks = mark_counts(9, edges)
        rebuilt_types[key] = (marks["edge"], marks["nonedge"])
    stored_types = {
        int(row["degree_cell_canonical_mask"]): (
            int(row["adjacent_root_mark_multiplicity"]),
            int(row["nonadjacent_root_mark_multiplicity"]),
        ) for row in pair_artifact["H9_disjoint_source_types"]
    }
    assert rebuilt_types == stored_types

    with gzip.open(COEFFICIENTS, "rt", encoding="utf-8") as handle:
        coefficient_artifact = json.load(handle)
    order8_masks = tuple(int(row["canonical_mask"])
                         for row in coefficient_artifact["families"]
                         ["ordered_edge"]["class_coefficients"]
                         if int(row["order"]) == 8)
    assert len(order8_masks) == 916
    specifications = {
        "ordered_edge": (True, 12, {17724}, {29988}),
        "ordered_nonedge": (False, 1,
                            {19601, 23697, 23817},
                            {28817, 29841, 29961}),
    }
    rebuilt_shadows = {}
    for family, (root_edge, root_mask, left_flags, right_flags) in specifications.items():
        nonzero = []
        for mask in order8_masks:
            value = shadow_count(mask, root_edge)
            selected = four_root_selected(mask, root_mask, left_flags, right_flags)
            assert selected == 2 * value
            if value:
                nonzero.append([mask, value])
        assert nonzero == shadow_artifact["shadow_coefficients"][family][
            "nonzero_order8_coefficients"
        ]
        rebuilt_shadows[family] = nonzero

    # Exact algebra behind (9)--(10).
    for q2, n_value, a_value in ((0, 0, 0), (33264, 4158, 10000),
                                 (12345, 678, 9012)):
        total = Fraction(3 * q2 - 2 * n_value, 2)
        b_value = total - a_value
        d_value = Fraction(2 * n_value, 99)
        e_value = Fraction(a_value, 693)
        f_value = Fraction(b_value, 4158)
        lambda3 = d_value + 3 * e_value - 4 * f_value
        lambda_minus4 = d_value - 4 * e_value + 3 * f_value
        assert lambda3 == Fraction(22 * a_value - 4 * total + 84 * n_value, 4158)
        assert lambda_minus4 == Fraction(3 * total - 27 * a_value
                                         + 84 * n_value, 4158)

    order8_sector = boundary["direct_E0_second_moment"]["catalogue"]["order8_sector"]
    assert (order8_sector["wave147_degree_cell_mask"],
            order8_sector["coefficient_in_M_E"]) == (127242964, 4)

    result = {
        "status": "INDEPENDENT_YYT_BOSE_MESNER_AUDIT_PASS",
        "order8_overlap_patterns_rejected": overlap_failures,
        "locally_admissible_mate_bit_patterns": 4,
        "partial_matchings": 34,
        "feasible_marked_matchings": feasible_marked,
        "order9_unmarked_types": len(representatives),
        "order9_adjacent_type_coefficients": sorted(
            key for key, coefficient in rebuilt_types.items() if coefficient[0]
        ),
        "order9_nonadjacent_type_coefficients": {
            str(key): coefficient[1] for key, coefficient in sorted(rebuilt_types.items())
            if coefficient[1]
        },
        "frozen_order8_classes_checked": len(order8_masks),
        "order8_shadow_vectors": rebuilt_shadows,
        "four_root_coefficient_identity_checked_for_every_class": True,
        "bose_mesner_fraction_arithmetic_checked": True,
        "support_M2_order8_crosscheck": {
            "mask": 127242964,
            "coefficient": 4,
            "functional_is_distinct_from_YYT": True,
        },
        "scope": (
            "Exact finite and algebraic audit.  It verifies the order-nine "
            "boundary and four-root shadow, but proves no positive E0 bound."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
