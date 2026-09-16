"""Independent finite audit: set graphs and all rooted relabellings.

Imports neither the producer nor any project graph-encoding helper.  The
universal assertion is proved in the note, not inferred from the rook test.
"""

import hashlib
import itertools as it
import json
from pathlib import Path


PAIRS = tuple(it.combinations(range(6), 2))
FLAGS = (24699, 24939, 25147, 25507, 27179, 27299)


def edge(a, b):
    return tuple(sorted((a, b)))


def decode(mask):
    return {pair for bit, pair in enumerate(PAIRS) if mask & (1 << bit)}


def orbit(edges):
    return {
        frozenset(edge(perm[a], perm[b]) for a, b in edges)
        for free in it.permutations((3, 4, 5))
        for perm in [(0, 1, 2) + free]
    }


def admissible(edges):
    neighbors = [{b if a == v else a for a, b in edges if v in (a, b)}
                 for v in range(6)]
    return all(len(neighbors[a] & neighbors[b]) <= (1 if (a, b) in edges else 2)
               for a, b in PAIRS)


def main():
    source = Path("scratch_theory_six_flag_uniformity.json")
    data = json.loads(source.read_text(encoding="utf-8"))
    flag_orbits = [orbit(decode(mask)) for mask in FLAGS]
    assert all(not (left & right) for left, right in it.combinations(flag_orbits, 2))
    assert len(data["templates"]) == 6
    template_count = 0
    for (a, b), record in zip(it.permutations(range(3), 2), data["templates"]):
        expected = {(0, 1), (0, 2), (1, 2), (3, 4), (4, 5),
                    edge(a, 3), edge(a, 4), edge(b, 5)}
        assert record["ordered_pair"] == [a, b]
        assert decode(record["raw_mask"]) == expected
        matches = [i for i, choices in enumerate(flag_orbits)
                   if frozenset(expected) in choices]
        assert len(matches) == 1 and FLAGS[matches[0]] == record["rooted_mask"]
        missing = sorted(set(PAIRS) - expected)
        survivors = []
        for size in range(len(missing) + 1):
            for extra in it.combinations(missing, size):
                template_count += 1
                if admissible(expected | set(extra)):
                    survivors.append(extra)
        assert survivors == [()]
        assert record["supergraphs_tested"] == 128
        assert record["only_pair_upper_supergraph_is_original"] is True

    # A different graph representation, with exhaustive induced-subset tests
    # and a separate direct construction for the claimed bijection.
    vertices = tuple(it.product(range(3), repeat=2))
    adj = {v: {w for w in vertices if w != v and (v[0] == w[0] or v[1] == w[1])}
           for v in vertices}
    assert {len(adj[v]) for v in vertices} == {4}
    assert all(len(adj[v] & adj[w]) == (1 if w in adj[v] else 2)
               for v, w in it.combinations(vertices, 2))
    rows = []
    bijections_checked = 0
    for roots in it.permutations(vertices, 3):
        if not all(b in adj[a] for a, b in it.combinations(roots, 2)):
            continue
        occurrences = [set() for _ in FLAGS]
        for free in it.combinations(sorted(set(vertices) - set(roots)), 3):
            labels = roots + free
            induced = frozenset((a, b) for a, b in PAIRS if labels[b] in adj[labels[a]])
            for i, choices in enumerate(flag_orbits):
                if induced in choices:
                    occurrences[i].add(frozenset(free))
        for record in data["templates"]:
            ai, bi = record["ordered_pair"]
            a, b = roots[ai], roots[bi]
            constructed = set()
            for v in adj[a] - set(roots):
                common = adj[a] & adj[v]
                second = (adj[b] & adj[v]) - {a}
                assert len(common) == len(second) == 1
                u, w = next(iter(common)), next(iter(second))
                assert len(set(roots) | {u, v, w}) == 6
                constructed.add(frozenset((u, v, w)))
                bijections_checked += 1
            index = FLAGS.index(record["rooted_mask"])
            assert constructed == occurrences[index] and len(constructed) == 2
        rows.append([len(occ) for occ in occurrences])
    assert rows == [[2] * 6] * 36
    gram = [[sum(row[i] * row[j] for row in rows) for j in range(6)]
            for i in range(6)]
    assert data["rook9_calibration"] == {
        "ordered_triangles": 36, "count_each_flag": 2, "Gram": gram}
    assert gram == [[144] * 6] * 6
    assert data["target"] == {"ordered_triangles": 99 * 14,
                              "count_each_flag": 14 - 2,
                              "complete_Gram_entry": 99 * 14 * (14 - 2) ** 2,
                              "requires_T_zero": False, "E0_lower_bound": None}
    closure_edges = ((0, 1), (0, 2), (1, 3), (2, 4), (3, 5), (4, 5))
    reached = {0}
    for _ in range(6):
        reached |= {v for pair in closure_edges if reached.intersection(pair) for v in pair}
    assert reached == set(range(6))
    result = {
        "status": "INDEPENDENT_SIX_FLAG_UNIFORMITY_FINITE_AUDIT_PASS",
        "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "templates": 6, "supergraphs_checked": template_count,
        "rook_ordered_triangles": len(rows), "bijections_checked": bijections_checked,
        "closure_graph_connected": True, "requires_T_zero": False,
        "universal_proof_location": "scratch_theory_six_flag_uniformity.md",
        "E0_lower_bound": None, "producer_imported": False,
        "frozen_order8_classes_regenerated": False,
    }
    Path("scratch_theory_six_flag_uniformity_audit.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
