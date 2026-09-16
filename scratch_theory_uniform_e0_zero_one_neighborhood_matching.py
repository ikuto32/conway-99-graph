"""One fixed control only: complete N(x) to seven disjoint edges."""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path


INPUT = Path("scratch_theory_uniform_e0_zero_degree_moment_control.json")
OUT = Path("scratch_theory_uniform_e0_zero_one_neighborhood_matching.json")


def perfect_matchings(vertices):
    if not vertices:
        yield ()
        return
    first = vertices[0]
    for index in range(1, len(vertices)):
        for remaining in perfect_matchings(vertices[1:index] + vertices[index + 1:]):
            yield ((first, vertices[index]),) + remaining


def main():
    control = json.loads(INPUT.read_text(encoding="utf-8"))
    supports = tuple(itertools.combinations(range(7), 2))
    labels = tuple((2 * a + i, 2 * b + j) for a, b in supports
                   for i, j in itertools.product((0, 1), repeat=2))
    index = {label: 15 + vertex for vertex, label in enumerate(labels)}
    source_label = tuple(2 * group for group in control["base_source_support"])
    x = index[source_label]
    fixed = {tuple(sorted((0, label + 1))) for label in range(14)}
    fixed.update((2 * group + 1, 2 * group + 2) for group in range(7))
    fixed.update(tuple(sorted((vertex, label + 1))) for pair, vertex in index.items() for label in pair)
    outer = tuple(index[tuple(pair)] for pair in control["base_twelve_neighbor_labels"])
    fixed.update(tuple(sorted((x, vertex))) for vertex in outer)
    remaining = tuple(vertex for vertex in outer if set(labels[vertex - 15]).isdisjoint(source_label))
    assert len(remaining) == 10
    total = permitted = locally_permitted = 0
    witness = None
    for matching in perfect_matchings(remaining):
        total += 1
        if any((a - 15) // 4 == (b - 15) // 4
               or set(labels[a - 15]) & set(labels[b - 15]) for a, b in matching):
            continue
        permitted += 1
        exposed = fixed | {tuple(sorted(edge)) for edge in matching}
        rows = [0] * 99
        for a, b in exposed:
            rows[a] |= 1 << b
            rows[b] |= 1 << a
        if not all((rows[a] & rows[b]).bit_count() <= (1 if rows[a] >> b & 1 else 2)
                   for a, b in itertools.combinations(range(99), 2)):
            continue
        locally_permitted += 1
        if witness is None:
            witness = matching
    assert total == 945 and permitted == locally_permitted == 286
    assert witness is not None
    exposed = fixed | {tuple(sorted(edge)) for edge in witness}
    neighbors_x = {b if a == x else a for a, b in exposed if x in (a, b)}
    neighborhood_edges = sorted((a, b) for a, b in exposed if a in neighbors_x and b in neighbors_x)
    assert len(neighbors_x) == 14 and len(neighborhood_edges) == 7
    assert all(sum(vertex in edge for edge in neighborhood_edges) == 1 for vertex in neighbors_x)
    result = {
        "status": "ONE_E0_ZERO_ROW_CONTROL_NEIGHBORHOOD_MATCHING_FOUND",
        "input_control_sha256": hashlib.sha256(INPUT.read_bytes()).hexdigest(),
        "zero_based_vertex_convention": "0 root;1..14 first-neighbour labels0..13;15..98 ordered support corners",
        "source_vertex": x, "source_label": list(source_label),
        "all_84_second_layer_labels": list(map(list, labels)),
        "base_fixed_edges": list(map(list, sorted(fixed))),
        "added_five_matching_edges": list(map(list, witness)),
        "added_matching_neighbor_labels": [[list(labels[a - 15]), list(labels[b - 15])] for a, b in witness],
        "complete_exposed_edge_set": list(map(list, sorted(exposed))),
        "source_neighborhood": sorted(neighbors_x),
        "source_neighborhood_seven_edges": list(map(list, neighborhood_edges)),
        "discovery_counts": {"ten_vertex_perfect_matchings_tested": total,
                             "respecting_label_and_fibre_restrictions": permitted,
                             "passing_all_partial_pair_caps": locally_permitted},
        "scope": {
            "one_fixed_base_control_only": True,
            "source_neighborhood_is_exactly_7K2": True,
            "all_same_fibre_second_layer_edges_absent": True,
            "other_cross_fibre_edges_unassigned": True,
            "full_SRG_constructed": False,
            "new_E0_bound_or_macro_exclusion": False,
            "sealed_uniform_control_modified": False,
        },
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUT), "exposed_edges": len(exposed),
                      "source_neighborhood_edges": len(neighborhood_edges),
                      "discovery_counts": result["discovery_counts"]}, indent=2))


if __name__ == "__main__":
    main()
