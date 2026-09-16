"""Independent audit of the preserved one-neighbourhood E0=0 control.

Only stdlib; no producer code is imported or executed. Labels, skeleton,
and one row are reconstructed independently. Matching counts use both a
subset dynamic program and canonical permutations, rather than the
producer's recursive matching generator. Adjacencies use Python sets.
"""

from collections import Counter
from functools import lru_cache
from hashlib import sha256
from itertools import combinations, permutations
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
CONTROL = HERE / "scratch_theory_uniform_e0_zero_degree_moment_control.json"
WITNESS = HERE / "scratch_theory_uniform_e0_zero_one_neighborhood_matching.json"
PRODUCER = HERE / "scratch_theory_uniform_e0_zero_one_neighborhood_matching.py"
OUT = HERE / "scratch_resume_neighborhood_audit.json"


def edge_set(items):
    result = set()
    for item in items:
        assert len(item) == 2
        a, b = item
        assert type(a) is int and type(b) is int and 0 <= a < b < 99
        assert (a, b) not in result
        result.add((a, b))
    return result


def adjacency(edges):
    neighbors = [set() for _ in range(99)]
    for a, b in edges:
        neighbors[a].add(b)
        neighbors[b].add(a)
    return neighbors


def cap_histogram(edges):
    neighbors = adjacency(edges)
    histogram = Counter()
    for a in range(99):
        assert len(neighbors[a]) <= 14
        for b in range(a):
            common = len(neighbors[a].intersection(neighbors[b]))
            adjacent = b in neighbors[a]
            assert common <= (1 if adjacent else 2), (a, b, common)
            histogram[f"{'edge' if adjacent else 'unassigned_or_absent'}:{common}"] += 1
    return dict(sorted(histogram.items()))


def matching_count(vertices, allowed):
    """Subset dynamic programming, independent of witness enumeration."""
    @lru_cache(None)
    def count(subset):
        if not subset:
            return 1
        first, *tail = subset
        return sum(count(tuple(v for v in tail if v != partner))
                   for partner in tail if (first, partner) in allowed)
    return count(tuple(sorted(vertices)))


def canonical_matchings(vertices):
    """Filter permutations using pair orientations and increasing first endpoints."""
    first, *tail = sorted(vertices)
    for perm in permutations(tail):
        pairs = ((first, perm[0]),) + tuple(zip(perm[1::2], perm[2::2]))
        if any(a >= b for a, b in pairs):
            continue
        starts = [a for a, b in pairs[1:]]
        if starts != sorted(starts):
            continue
        yield frozenset(pairs)


def main():
    original_hashes = {path.name: sha256(path.read_bytes()).hexdigest()
                       for path in (CONTROL, WITNESS, PRODUCER)}
    control = json.loads(CONTROL.read_text(encoding="utf-8"))
    witness = json.loads(WITNESS.read_text(encoding="utf-8"))
    assert witness["input_control_sha256"] == original_hashes[CONTROL.name]

    # Rebuild the vertex map by sorting label pairs by their two groups,
    # then their exact labels. This derives the producer's numbering.
    labels = sorted((a, b) for a in range(14) for b in range(a + 1, 14)
                    if a // 2 != b // 2)
    labels.sort(key=lambda pair: (pair[0] // 2, pair[1] // 2, *pair))
    assert len(labels) == 84
    assert labels == [tuple(pair) for pair in witness["all_84_second_layer_labels"]]
    vertex_of = {label: i + 15 for i, label in enumerate(labels)}
    label_of = {i + 15: label for i, label in enumerate(labels)}
    source_label = (0, 2)
    source = vertex_of[source_label]
    expected_labels = ((0, 4), (1, 6), (2, 8), (3, 10),
                       (4, 6), (5, 7), (8, 10), (9, 11),
                       (5, 12), (7, 12), (9, 13), (11, 13))
    assert control["base_source_support"] == [0, 1]
    assert {tuple(pair) for pair in control["base_twelve_neighbor_labels"]} == set(expected_labels)
    assert witness["source_vertex"] == source
    assert witness["source_label"] == list(source_label)

    skeleton = {(0, vertex) for vertex in range(1, 15)}
    skeleton |= {(vertex, vertex + 1) for vertex in range(1, 15, 2)}
    skeleton |= {(label + 1, vertex) for vertex, pair in label_of.items() for label in pair}
    assert len(skeleton) == 189
    source_outer = {vertex_of[label] for label in expected_labels}
    base = skeleton | {(min(source, v), max(source, v)) for v in source_outer}
    assert len(base) == 201
    assert base == edge_set(witness["base_fixed_edges"])
    added = edge_set(witness["added_five_matching_edges"])
    assert len(added) == 5 and not (added & base)
    complete = base | added
    assert complete == edge_set(witness["complete_exposed_edge_set"])
    assert len(complete) == 206
    for a, b in complete:
        if a >= 15 and b >= 15:
            assert tuple(t // 2 for t in label_of[a]) != tuple(t // 2 for t in label_of[b])

    neighbors = adjacency(complete)
    source_neighbors = neighbors[source]
    assert len(source_neighbors) == 14
    assert sorted(source_neighbors) == witness["source_neighborhood"]
    neighborhood_edges = {edge for edge in complete if set(edge) <= source_neighbors}
    assert len(neighborhood_edges) == 7
    assert neighborhood_edges == edge_set(witness["source_neighborhood_seven_edges"])
    assert all(len(neighbors[v] & source_neighbors) == 1 for v in source_neighbors)
    assert [[[ *label_of[a]], [*label_of[b]]] for a, b in witness["added_five_matching_edges"]] == witness["added_matching_neighbor_labels"]
    remaining = sorted(v for v in source_outer if set(label_of[v]).isdisjoint(source_label))
    assert len(remaining) == 10
    assert Counter(v for edge in added for v in edge) == Counter(remaining)
    all_pairs = set(combinations(remaining, 2))
    allowed = {(a, b) for a, b in all_pairs
               if set(label_of[a]).isdisjoint(label_of[b])
               and {t // 2 for t in label_of[a]} != {t // 2 for t in label_of[b]}}
    assert added <= allowed
    all_count = matching_count(remaining, all_pairs)
    restricted_count = matching_count(remaining, allowed)
    assert all_count == 945 and restricted_count == 286
    counts = Counter()
    seen = set()
    passing = set()
    for matching in canonical_matchings(remaining):
        assert matching not in seen
        seen.add(matching)
        counts["all"] += 1
        if not matching <= allowed:
            continue
        counts["restricted"] += 1
        cap_histogram(base | matching)
        counts["all_pair_caps_pass"] += 1
        passing.add(matching)
    assert counts == {"all": 945, "restricted": 286, "all_pair_caps_pass": 286}
    assert frozenset(added) in passing
    assert witness["discovery_counts"] == {
        "ten_vertex_perfect_matchings_tested": all_count,
        "respecting_label_and_fibre_restrictions": restricted_count,
        "passing_all_partial_pair_caps": counts["all_pair_caps_pass"],
    }

    # Root, first layer, and source already have full rows. Every pair of
    # these 16 vertices therefore has its exact common-neighbour count.
    closed = set(range(15)) | {source}
    assert all(len(neighbors[v]) == 14 for v in closed)
    for a, b in combinations(sorted(closed), 2):
        assert len(neighbors[a] & neighbors[b]) == (1 if b in neighbors[a] else 2)
    shared_label_edges = {edge for edge in complete if min(edge) >= 15
                          and set(label_of[edge[0]]) & set(label_of[edge[1]])}
    disjoint_label_edges = {edge for edge in complete if min(edge) >= 15} - shared_label_edges
    triangles = [triple for triple in combinations(sorted(source_neighbors | {source}), 3)
                 if all(edge in disjoint_label_edges for edge in combinations(triple, 2))]
    assert len(shared_label_edges) == 2 and len(disjoint_label_edges) == 15
    assert len(triangles) == 5 and all(source in triangle for triangle in triangles)
    for path in (CONTROL, WITNESS, PRODUCER):
        assert sha256(path.read_bytes()).hexdigest() == original_hashes[path.name]
    result = {
        "status": "INDEPENDENT_ONE_NEIGHBORHOOD_AUDIT_PASS",
        "input_sha256": original_hashes,
        "auditor_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
        "vertex_numbering": "zero-based: root=0, first layer=1..14, second layer=15..98",
        "source_vertex": source,
        "rooted_skeleton_edges": 189,
        "one_source_row_base_edges": 201,
        "exposed_edges": len(complete),
        "source_neighborhood_edges": [list(e) for e in sorted(neighborhood_edges)],
        "degree_histogram": dict(sorted(Counter(map(len, neighbors)).items())),
        "matching_counts": dict(counts),
        "subset_dp_counts": {"all": all_count, "restricted": restricted_count},
        "all_4851_pair_cap_histogram": cap_histogram(complete),
        "closed_rows": sorted(closed),
        "closed_row_pairs_exact": 120,
        "exposed_second_layer_edge_types": {"shared_root_label": 2, "disjoint_root_labels": 15},
        "five_disjoint_label_triangles_at_source": [list(triple) for triple in triangles],
        "scope": {
            "one_fixed_source_row_and_its_seven_neighborhood_edges": True,
            "all_preserved_input_bytes_unchanged": True,
            "producer_imported_or_executed": False,
            "full_SRG_constructed": False,
            "existence_of_any_completion_established": False,
            "all_other_second_layer_rows_completed": False,
            "uniform_positive_E0_bound_or_macro_exclusion": False,
            "lower_layer_exhaustive_enumeration": False,
        },
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
