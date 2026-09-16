"""Exact invariant probe for the six surviving Q=6 local K4 orbits."""

from __future__ import annotations

from collections import Counter
import itertools
import json
from pathlib import Path


INPUT = Path("scratch_general_e72_q3_gram_fast_expansion_part_27_orbit_001.json")
OUTPUT = Path("scratch_theory_e72_k4_q6_probe.json")
SUPPORTS = tuple(itertools.combinations(range(4), 2))
OPPOSITE = (((0, 1), (2, 3)), ((0, 2), (1, 3)), ((0, 3), (1, 2)))
COORD = {
    (0, 1): (1, 0), (2, 3): (1, 0),
    (0, 2): (0, 1), (1, 3): (0, 1),
    (0, 3): (-1, -1), (1, 2): (-1, -1),
}


def support(vertex):
    return tuple(sorted(symbol // 2 for symbol in vertex))


def inner(left, right):
    x, y = left
    u, v = right
    return 4 * x * u - 2 * x * v - 2 * y * u + 4 * y * v


def components(adjacency):
    unseen = set(adjacency)
    sizes = []
    while unseen:
        start = min(unseen)
        seen = {start}
        stack = [start]
        while stack:
            vertex = stack.pop()
            for other in adjacency[vertex]:
                if other not in seen:
                    seen.add(other)
                    stack.append(other)
        unseen.difference_update(seen)
        sizes.append(len(seen))
    return sorted(sizes)


def record(rep):
    edges = [tuple(map(tuple, edge)) for edge in rep["edges"]]
    vertices = sorted({vertex for edge in edges for vertex in edge})
    adjacency = {vertex: set() for vertex in vertices}
    for left, right in edges:
        adjacency[left].add(right)
        adjacency[right].add(left)
    assert set(map(len, adjacency.values())) == {3}

    internal = [edge for edge in edges if support(edge[0]) == support(edge[1])]
    internal_by_support = {F: [] for F in SUPPORTS}
    for edge in internal:
        internal_by_support[support(edge[0])].append(edge)
    fibre_types = {}
    for F, values in internal_by_support.items():
        assert len(values) == 2
        shared = {len(set(left) & set(right)) for left, right in values}
        assert len(shared) == 1
        fibre_types[F] = "opposite_sides" if shared == {1} else "two_diagonals"
    assert Counter(fibre_types.values()) == Counter({"opposite_sides": 3, "two_diagonals": 3})

    n = {
        vertex: {F: sum(support(other) == F for other in adjacency[vertex]) for F in SUPPORTS}
        for vertex in vertices
    }
    local_collision = sum(
        value * (value - 1) // 2
        for row in n.values() for value in row.values()
    )
    assert local_collision == 0
    opposite_witnesses = {
        pair: sum(n[vertex][pair[0]] * n[vertex][pair[1]] for vertex in vertices)
        for pair in OPPOSITE
    }
    residuals = {}
    residual_norms = Counter()
    for vertex in vertices:
        value = (
            sum(COORD[support(other)][0] for other in adjacency[vertex]),
            sum(COORD[support(other)][1] for other in adjacency[vertex]),
        )
        residuals[vertex] = value
        residual_norms[inner(value, value)] += 1

    side_adjacency = {vertex: set() for vertex in vertices}
    for left, right in edges:
        if set(left) & set(right):
            side_adjacency[left].add(right)
            side_adjacency[right].add(left)
    assert set(map(len, side_adjacency.values())) == {2}
    return {
        "mask_hex": rep["mask_hex"],
        "orbit_size": rep["orbit_size"],
        "opposite_side_supports": [list(F) for F in SUPPORTS if fibre_types[F] == "opposite_sides"],
        "diagonal_supports": [list(F) for F in SUPPORTS if fibre_types[F] == "two_diagonals"],
        "local_component_sizes": components(adjacency),
        "side_two_factor_cycle_lengths": components(side_adjacency),
        "local_same_fibre_collision": local_collision,
        "local_opposite_pair_witnesses": [
            {"pair": [list(F) for F in pair], "count": opposite_witnesses[pair]}
            for pair in OPPOSITE
        ],
        "local_Gram_residual_norm_histogram": {
            str(key): value for key, value in sorted(residual_norms.items())
        },
        "local_Gram_residual_norm_sum": sum(key * value for key, value in residual_norms.items()),
        "local_Gram_residual_vectors": [
            {"vertex": list(vertex), "value": list(residuals[vertex])}
            for vertex in vertices
        ],
    }


def main():
    source = json.loads(INPUT.read_text(encoding="utf-8"))["rows"][0]
    rows = [record(rep) for rep in source["local_graph_representatives"] if rep["Q"] == 6]
    assert len(rows) == 6 and sum(row["orbit_size"] for row in rows) == 768
    result = {
        "status": "EXACT_LOCAL_INVARIANTS",
        "input": str(INPUT),
        "scope": "six pair-and-forced-BP-feasible Q=6 local orbits on source row 134",
        "orbit_count": len(rows),
        "labelled_graph_count": sum(row["orbit_size"] for row in rows),
        "rows": rows,
        "claim_boundary": "No full-graph exclusion is asserted by this diagnostic.",
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps([
        {
            "orbit_size": row["orbit_size"],
            "side_supports": row["opposite_side_supports"],
            "O": [item["count"] for item in row["local_opposite_pair_witnesses"]],
            "q2": row["local_Gram_residual_norm_histogram"],
            "qnorm": row["local_Gram_residual_norm_sum"],
        }
        for row in rows
    ], indent=2))


if __name__ == "__main__":
    main()
