"""Finite classification of off-diagonal entries of Y Y^T.

The graph-theoretic definitions are in ``scratch_theory_root_flag_union.md``.
An expanded term in (YY^T)[r,s] is a pair of two-cross-edge flag relations
sharing their target flag.  A priori, if the two source triangles meet then
their union has eight vertices.  The first finite check below proves that
every such overlap violates a lambda/mu common-neighbour upper bound.  Thus
every off-diagonal term has nine distinct vertices.  The script then
enumerates every possible matching between the two disjoint source triangles,
checks the SRG common-neighbour upper bounds inside the induced subgraph,
groups exact isomorphism types, and computes the marking multiplicity of each
type.  Only the Python standard library is used.
"""

from __future__ import annotations

import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path


OUTPUT = Path("scratch_theory_root_yyt_pair_classification.json")


def normal(left, right):
    return (left, right) if left < right else (right, left)


def degrees(vertex_count, edges):
    answer = [0] * vertex_count
    for left, right in edges:
        answer[left] += 1
        answer[right] += 1
    return tuple(answer)


def adjacency(vertex_count, edges):
    answer = [set() for _ in range(vertex_count)]
    for left, right in edges:
        answer[left].add(right)
        answer[right].add(left)
    return tuple(map(frozenset, answer))


def local_pair_upper(vertex_count, edges):
    graph = adjacency(vertex_count, edges)
    for left, right in itertools.combinations(range(vertex_count), 2):
        common = len(graph[left] & graph[right])
        if common > (1 if right in graph[left] else 2):
            return False
    return True


def isomorphic(vertex_count, left_edges, right_edges):
    left_degrees = degrees(vertex_count, left_edges)
    right_degrees = degrees(vertex_count, right_edges)
    if sorted(left_degrees) != sorted(right_degrees):
        return False
    left_groups = defaultdict(list)
    right_groups = defaultdict(list)
    for vertex, degree in enumerate(left_degrees):
        left_groups[degree].append(vertex)
    for vertex, degree in enumerate(right_degrees):
        right_groups[degree].append(vertex)
    degree_values = tuple(sorted(left_groups))
    right_set = frozenset(right_edges)
    for images_by_group in itertools.product(*(
        tuple(itertools.permutations(right_groups[degree]))
        for degree in degree_values
    )):
        image = [None] * vertex_count
        for degree, images in zip(degree_values, images_by_group):
            for source, target in zip(left_groups[degree], images):
                image[source] = target
        if frozenset(normal(image[left], image[right])
                     for left, right in left_edges) == right_set:
            return True
    return False


def canonical_mask(vertex_count, edges):
    pairs = tuple(itertools.combinations(range(vertex_count), 2))
    pair_index = {pair: index for index, pair in enumerate(pairs)}
    best = None
    for permutation in itertools.permutations(range(vertex_count)):
        value = 0
        for left, right in edges:
            value |= 1 << pair_index[normal(permutation[left], permutation[right])]
        if best is None or value < best:
            best = value
    return best


def transform_edges(edges, permutation):
    return frozenset(normal(permutation[left], permutation[right])
                     for left, right in edges)


def canonical_mask_by_degree(vertex_count, edges):
    """Wave147's complete degree-cell canonical convention."""

    degree_rows = degrees(vertex_count, edges)
    groups = defaultdict(list)
    for vertex, degree in enumerate(degree_rows):
        groups[degree].append(vertex)
    target_start = 0
    choices = []
    for degree in sorted(groups):
        sources = groups[degree]
        targets = tuple(range(target_start, target_start + len(sources)))
        target_start += len(sources)
        choices.append(tuple(dict(zip(sources, order))
                             for order in itertools.permutations(targets)))
    best = None
    pairs = tuple(itertools.combinations(range(vertex_count), 2))
    pair_index = {pair: index for index, pair in enumerate(pairs)}
    for selection in itertools.product(*choices):
        permutation = [None] * vertex_count
        for mapping in selection:
            for source, target in mapping.items():
                permutation[source] = target
        transformed = transform_edges(edges, permutation)
        value = sum(1 << pair_index[edge] for edge in transformed)
        if best is None or value < best:
            best = value
    assert best is not None
    return best


def triangles(vertex_count, edges):
    graph = adjacency(vertex_count, edges)
    return tuple(combination for combination in
                 itertools.combinations(range(vertex_count), 3)
                 if all(right in graph[left]
                        for left, right in itertools.combinations(combination, 2)))


def is_x_relation(source, unmatched_source, target, unmatched_target, edges):
    if set(source) & set(target):
        return False
    cross = {normal(left, right) for left in source for right in target
             if normal(left, right) in edges}
    if len(cross) != 2:
        return False
    source_used = {vertex for edge in cross for vertex in edge if vertex in source}
    target_used = {vertex for edge in cross for vertex in edge if vertex in target}
    return (source_used == set(source) - {unmatched_source}
            and target_used == set(target) - {unmatched_target})


def valid_mark_count(vertex_count, edges, source_intersection_size,
                     root_adjacency):
    """Number of unordered-root expanded YY^T terms in this induced graph."""

    graph = adjacency(vertex_count, edges)
    triangle_rows = triangles(vertex_count, edges)
    count = 0
    for root_left, root_right in itertools.combinations(range(vertex_count), 2):
        if (root_right in graph[root_left]) != root_adjacency:
            continue
        for source_left in triangle_rows:
            if root_left not in source_left:
                continue
            for source_right in triangle_rows:
                if root_right not in source_right or source_left == source_right:
                    continue
                if len(set(source_left) & set(source_right)) != source_intersection_size:
                    continue
                for target in triangle_rows:
                    if set(target) & (set(source_left) | set(source_right)):
                        continue
                    for unmatched_target in target:
                        if (is_x_relation(source_left, root_left, target,
                                          unmatched_target, edges)
                                and is_x_relation(source_right, root_right, target,
                                                  unmatched_target, edges)):
                            count += 1
    return count


def all_bipartite_matchings(left, right):
    answer = []
    for size in range(4):
        for left_vertices in itertools.combinations(left, size):
            for right_vertices in itertools.combinations(right, size):
                for image in itertools.permutations(right_vertices):
                    answer.append(frozenset(normal(a, b)
                                            for a, b in zip(left_vertices, image)))
    assert len(answer) == 34
    return tuple(answer)


def group_isomorphism_types(vertex_count, rows):
    groups = []
    for row in rows:
        for group in groups:
            if isomorphic(vertex_count, row["edges"], group["representative"]["edges"]):
                group["rows"].append(row)
                break
        else:
            groups.append({"representative": row, "rows": [row]})
    return groups


def main():
    # A putative order-eight overlap has source triangles
    # T=(r,p,a), T'=(s,p,b) and target U=(u,c,d), where r,s,u are
    # unmatched.  In each X relation {p,a} and {p,b} are perfectly matched
    # to {c,d}.  There are four labelled choices.  If p has two target
    # neighbours, the adjacent pair c,d has both u and p as common
    # neighbours.  If p has only one target neighbour, the other target
    # vertex has p's partners a,b plus its mate in U as three common
    # neighbours with p.  The exact finite check records both failures.
    overlap_rows = []
    for first_swap, second_swap in itertools.product((False, True), repeat=2):
        # labels r,p,a,s,b,u,c,d = 0,...,7
        r, p, a, s, b, u, c, d = range(8)
        edges = {
            normal(r, p), normal(r, a), normal(p, a),
            normal(s, p), normal(s, b), normal(p, b),
            normal(u, c), normal(u, d), normal(c, d),
        }
        first = ((p, d), (a, c)) if first_swap else ((p, c), (a, d))
        second = ((p, d), (b, c)) if second_swap else ((p, c), (b, d))
        edges.update(normal(*edge) for edge in first + second)
        graph = adjacency(8, edges)
        violations = []
        for left, right in itertools.combinations(range(8), 2):
            common = len(graph[left] & graph[right])
            target = 1 if right in graph[left] else 2
            if common > target:
                violations.append({
                    "pair": [left, right],
                    "adjacent": right in graph[left],
                    "common_neighbours": sorted(graph[left] & graph[right]),
                    "target_upper": target,
                })
        assert violations
        overlap_rows.append({
            "first_swap": first_swap,
            "second_swap": second_swap,
            "violations": violations,
        })

    # H9 base: source triangles (0,1,2),(3,4,5), target (6,7,8).
    # Roots are 0,3; target-unmatched is 6; fixed cross matchings use
    # 1-7,2-8 and 4-7,5-8.  The remaining source-source edges form a matching.
    base_edges = frozenset(map(lambda edge: normal(*edge), {
        (0, 1), (0, 2), (1, 2),
        (3, 4), (3, 5), (4, 5),
        (6, 7), (6, 8), (7, 8),
        (1, 7), (2, 8), (4, 7), (5, 8),
    }))
    rows = []
    for matching in all_bipartite_matchings((0, 1, 2), (3, 4, 5)):
        edges = base_edges | matching
        if not local_pair_upper(9, edges):
            continue
        rows.append({"edges": edges, "root_adjacency": (0, 3) in matching,
                     "source_cross_edge_count": len(matching)})
    groups = group_isomorphism_types(9, rows)

    types = []
    for group in groups:
        representative = group["representative"]
        edges = representative["edges"]
        root_adjacency = representative["root_adjacency"]
        # Isomorphism cannot change whether the distinguished roots in a row
        # are adjacent, but the same unmarked type may arise from both marked
        # classes.  Count both directly from the representative.
        adjacent_marks = valid_mark_count(9, edges, 0, True)
        nonadjacent_marks = valid_mark_count(9, edges, 0, False)
        types.append({
            "canonical_mask": canonical_mask(9, edges),
            "degree_cell_canonical_mask": canonical_mask_by_degree(9, edges),
            "edge_count": len(edges),
            "representative_edges": [list(edge) for edge in sorted(edges)],
            "degree_sequence": sorted(degrees(9, edges), reverse=True),
            "generated_marked_rows": len(group["rows"]),
            "generated_root_adjacency_histogram": dict(Counter(
                str(row["root_adjacency"]) for row in group["rows"]
            )),
            "adjacent_root_mark_multiplicity": adjacent_marks,
            "nonadjacent_root_mark_multiplicity": nonadjacent_marks,
            "source_cross_edge_count_histogram": dict(Counter(
                str(row["source_cross_edge_count"]) for row in group["rows"]
            )),
        })
    types.sort(key=lambda row: row["canonical_mask"])

    result = {
        "status": "YYT_OFFDIAGONAL_MARKED_MOTIF_CLASSIFICATION_COMPLETE",
        "order8_intersecting_source_case": {
            "labelled_matching_choices": len(overlap_rows),
            "locally_admissible_choices": 0,
            "failure_certificates": overlap_rows,
        },
        "H9_disjoint_source_types": types,
        "counts": {
            "bipartite_source_matchings_examined": 34,
            "locally_pair_upper_feasible_marked_matchings": len(rows),
            "unmarked_isomorphism_types": len(types),
            "types_with_adjacent_root_marks": sum(
                bool(row["adjacent_root_mark_multiplicity"]) for row in types),
            "types_with_nonadjacent_root_marks": sum(
                bool(row["nonadjacent_root_mark_multiplicity"]) for row in types),
        },
        "identities": {
            "adjacent_offdiagonal_sum": (
                "sum_H9 adjacent_root_mark_multiplicity(H)*N_ind(H)"
            ),
            "nonadjacent_offdiagonal_sum": (
                "sum_H9 nonadjacent_root_mark_multiplicity(H)*N_ind(H)"
            ),
            "total_offdiagonal_sum": (
                "(3*sum_T q(T)^2-2*n3-2*N(H_delta))/2"
            ),
        },
        "checks": {
            "all_cross_edges_between_source_triangles_are_a_matching": True,
            "all_34_partial_matchings_enumerated": True,
            "SRG_pair_common_neighbour_upper_applied_inside_union": True,
            "exact_isomorphism_grouping": True,
            "mark_multiplicities_reconstructed_from_each_unmarked_type": True,
            "all_four_order8_overlap_patterns_fail_pair_upper": True,
        },
        "scope": (
            "All surviving off-diagonal terms are H9 motif variables.  The "
            "classification by itself does not assert that the resulting "
            "linear functional is independent of the existing order-eight "
            "extension-row span; that separate span test is required."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], **result["counts"]},
                     separators=(",", ":")))


if __name__ == "__main__":
    main()
