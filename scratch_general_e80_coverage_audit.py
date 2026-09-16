"""Independent bounded coverage audit for the corrected E0=80 portfolios."""

from __future__ import annotations

from collections import Counter
from functools import lru_cache
import itertools
import json
import math

from scratch_general_e80_exact_sat import (
    graph_orbits,
    residual_transforms,
    survivor_graphs,
    transform_graph,
)


SUPPORTS = tuple(itertools.combinations(range(7), 2))


def min_uniform_square(graph_edges, vertex_count, demand):
    graph_edges = tuple(graph_edges)

    @lru_cache(None)
    def visit(position, residual):
        if position == len(graph_edges):
            return 0 if not any(residual) else math.inf
        u, v = graph_edges[position]
        answer = math.inf
        for value in range(min(residual[u], residual[v]) + 1):
            changed = list(residual)
            changed[u] -= value
            changed[v] -= value
            answer = min(answer, value * value + visit(position + 1, tuple(changed)))
        return answer

    return visit(0, (demand,) * vertex_count)


def classify_exceptional_supports():
    accepted = []
    rejected = Counter()
    for chosen in itertools.combinations(range(21), 4):
        overlap = []
        disjoint = []
        for i, j in itertools.combinations(range(4), 2):
            target = overlap if set(SUPPORTS[chosen[i]]) & set(SUPPORTS[chosen[j]]) else disjoint
            target.append((i, j))
        overlap_square = min_uniform_square(overlap, 4, 4)
        disjoint_square = min_uniform_square(disjoint, 4, 2)
        if overlap_square == math.inf or disjoint_square == math.inf:
            rejected["row_infeasible"] += 1
            continue
        # For E0=80: fixed diagonal/base contribution is 4528, while the
        # compression spectral upper bound on tr(D^2) is 4576.
        d_square = 4528 + 2 * (overlap_square + disjoint_square)
        if d_square > 4576:
            rejected["square_bound"] += 1
            continue
        overlap_degrees = sorted(Counter(u for edge in overlap for u in edge).values())
        disjoint_degrees = sorted(Counter(u for edge in disjoint for u in edge).values())
        assert len(overlap) == 4 and overlap_degrees == [2, 2, 2, 2]
        assert len(disjoint) == 2 and disjoint_degrees == [1, 1, 1, 1]
        assert overlap_square == 16 and disjoint_square == 8 and d_square == 4576
        accepted.append(chosen)
    # Choose four group vertices and one of the three undirected 4-cycles.
    assert len(accepted) == math.comb(7, 4) * 3 == 105
    return accepted, rejected


def burnside_audit():
    graphs, _descriptors = survivor_graphs()
    transforms = residual_transforms()
    fixed_counts = [
        sum(transform_graph(graph, transform) == graph for graph in graphs)
        for transform in transforms
    ]
    assert sum(fixed_counts) % len(transforms) == 0
    burnside_orbits = sum(fixed_counts) // len(transforms)
    orbits, _ = graph_orbits(graphs)
    sizes = sorted(len(orbit) for _representative, orbit in orbits)
    assert burnside_orbits == len(orbits) == 5
    assert sizes == [16, 16, 32, 32, 32] and sum(sizes) == len(graphs) == 128
    return {
        "survivors": len(graphs),
        "group_size": len(transforms),
        "burnside_fixed_sum": sum(fixed_counts),
        "burnside_orbit_count": burnside_orbits,
        "orbit_sizes": sizes,
        "fixed_count_histogram": dict(sorted(Counter(fixed_counts).items())),
    }


def main():
    accepted, rejected = classify_exceptional_supports()
    exceptional = set(accepted[0])
    high = set(range(21)) - exceptional
    hh = hl = ll = 0
    for u, v in itertools.combinations(range(21), 2):
        if set(SUPPORTS[u]) & set(SUPPORTS[v]):
            continue
        if u in high and v in high:
            hh += 1
        elif u in exceptional and v in exceptional:
            ll += 1
        else:
            hl += 1
    assert (hh, hl, ll) == (67, 36, 2)
    result = {
        "E0_80_classification": {
            "all_four_support_subsets_checked": math.comb(21, 4),
            "accepted_support_sets": len(accepted),
            "accepted_formula": "C(7,4)*3 = 105 group 4-cycles",
            "rejected": dict(rejected),
            "compression_D_square_upper": 4576,
            "accepted_overlap_graph": "C4, weight 2 on every edge",
            "accepted_disjoint_graph": "2K2, weight 2 on every edge",
        },
        "normalized_variable_blocks": {
            "C4_C4_two_sided_permutations": hh,
            "C4_P4_one_sided_column_one": hl,
            "P4_P4_fixed_disjoint_blocks": ll,
            "total_disjoint_support_blocks": hh + hl + ll,
        },
        "local_orbit_crosscheck": burnside_audit(),
        "coverage_conclusion": "105 support placements form one S7 orbit; 128 labelled local graphs form five exhaustive residual orbits",
    }
    with open("scratch_general_e80_coverage_audit.json", "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
