"""Bounded mechanical audit of structural facts in the rooted 84-vertex model.

This does not solve a SAT instance.  It enumerates the locally possible
four-vertex fibre graphs and checks which normalized triangle branches are
already inconsistent with the BP coordinate equations.
"""

from __future__ import annotations

import itertools
import json

from scratch_general_exact_sat import coordinates
from scratch_general_triangle_portfolio import branch_specs


def fibre_orbits():
    vertices = tuple(itertools.product((0, 1), repeat=2))
    edges = tuple(itertools.combinations(range(4), 2))

    transforms = []
    for swap in (False, True):
        for flip0, flip1 in itertools.product((0, 1), repeat=2):
            image = []
            for a, b in vertices:
                if swap:
                    a, b = b, a
                image.append(vertices.index((a ^ flip0, b ^ flip1)))
            transforms.append(tuple(image))
    assert len(set(transforms)) == 8

    def locally_allowed(mask: int) -> bool:
        # Each of the four symbols in the support has BP target one.
        for u, (a, b) in enumerate(vertices):
            neighbours = [
                vertices[v]
                for bit, (x, y) in enumerate(edges)
                if mask >> bit & 1
                for v in ([y] if x == u else [x] if y == u else [])
            ]
            for coordinate in (0, 1):
                for value in (0, 1):
                    if sum(v[coordinate] == value for v in neighbours) > 1:
                        return False
        return True

    def image_mask(mask: int, transform) -> int:
        answer = 0
        for bit, (u, v) in enumerate(edges):
            if mask >> bit & 1:
                pair = tuple(sorted((transform[u], transform[v])))
                answer |= 1 << edges.index(pair)
        return answer

    allowed = {mask for mask in range(1 << len(edges)) if locally_allowed(mask)}
    unseen = set(allowed)
    orbits = []
    while unseen:
        representative = min(unseen)
        orbit = {image_mask(representative, transform) for transform in transforms}
        assert orbit <= allowed
        unseen -= orbit
        selected = [edges[bit] for bit in range(6) if representative >> bit & 1]
        cross = sum(
            sum(vertices[u][i] != vertices[v][i] for i in (0, 1)) == 1
            for u, v in selected
        )
        diagonal = len(selected) - cross
        degrees = sorted(
            [sum(u in edge for edge in selected) for u in range(4)], reverse=True
        )
        orbits.append(
            {
                "representative_edges": selected,
                "orbit_size": len(orbit),
                "edge_count": len(selected),
                "cross_edges_C": cross,
                "diagonal_edges_Q": diagonal,
                "degree_sequence": degrees,
            }
        )
    return len(allowed), sorted(orbits, key=lambda row: (row["edge_count"], row["diagonal_edges_Q"], row["degree_sequence"]))


def bp_consistent_assumptions(units, variables, labels) -> bool:
    positives = {literal for literal in units if literal > 0}
    negatives = {-literal for literal in units if literal < 0}
    if positives & negatives:
        return False
    inverse = {identifier: pair for pair, identifier in variables.items()}
    forced_neighbours = [set() for _ in labels]
    for identifier in positives:
        u, v = inverse[identifier]
        forced_neighbours[u].add(v)
        forced_neighbours[v].add(u)
    for u, own_label in enumerate(labels):
        own = set(own_label)
        for symbol in range(14):
            target = 1 if symbol in own or (symbol ^ 1) in own else 2
            used = sum(symbol in labels[v] for v in forced_neighbours[u])
            if used > target:
                return False
    return True


def main():
    labels, _index, variables, _edge = coordinates()
    pair_targets = {1: 0, 2: 0}
    for u, v in itertools.combinations(range(84), 2):
        pair_targets[2 - len(set(labels[u]) & set(labels[v]))] += 1
    assert pair_targets == {1: 924, 2: 2562}
    assert sum(target * count for target, count in pair_targets.items()) == 6048
    assert 84 * (12 * 11 // 2) + (84 * 12 // 2) == 6048

    allowed_count, orbits = fibre_orbits()
    specs, coverage = branch_specs()
    viable = [
        spec["branch"]
        for spec in specs
        if bp_consistent_assumptions(spec["assumptions"], variables, labels)
    ]
    eliminated = [spec["branch"] for spec in specs if spec["branch"] not in viable]
    assert len(specs) == 26 and len(viable) == 17 and len(eliminated) == 9

    result = {
        "global_exactness_audit": {
            "pair_target_histogram": pair_targets,
            "sum_pair_targets": 6048,
            "sum_edge_plus_two_path_terms_at_degree_12": 6048,
        },
        "same_support_fibres": {
            "locally_allowed_labelled_graphs": allowed_count,
            "D8_orbit_count": len(orbits),
            "orbits": orbits,
            "rule": "a diagonal edge isolates both endpoints inside its fibre; otherwise the fibre is a subgraph of C4",
        },
        "group_classes": {
            "class_size": 24,
            "internal_degree": 2,
            "outside_to_class_degree": 4,
            "cycle_lengths_divisible_by": 4,
            "explanation": "on the class, every vertex has one neighbour with the same group-symbol and one with its mate",
        },
        "triangle_portfolio": {
            "original_orbit_branches": len(specs),
            "BP_feasible_orbit_branches": len(viable),
            "BP_inconsistent_orbit_branches": len(eliminated),
            "viable": viable,
            "eliminated": eliminated,
            "per_base_orbits_before_BP_filter": {
                base: row["orbit_count"] for base, row in coverage.items()
            },
        },
        "outer_adjacency_spectrum": {
            "12": 1,
            "3": 40,
            "0": 7,
            "-2": 6,
            "-4": 30,
        },
    }
    with open("scratch_general_structural_audit.json", "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
