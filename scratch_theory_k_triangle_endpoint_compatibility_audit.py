"""Independent finite replay; the producer and its helpers are not imported."""

from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path


CERT = Path("scratch_theory_k_triangle_endpoint_compatibility.json")
OUT = Path("scratch_theory_k_triangle_endpoint_compatibility_audit.json")
FROZEN = Path("external_conway99_research/attempts/wave147-alternative-lane/exact-results.json")
COUNTS = Path("scratch_theory_wave163_integral_order8_boundary.json")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def edge_set(mask: int, order: int) -> set[frozenset[int]]:
    return {frozenset(pair) for bit, pair in
            enumerate(itertools.combinations(range(order), 2)) if mask >> bit & 1}


def triangle_sets(edges: set[frozenset[int]], order: int) -> list[frozenset[int]]:
    return [frozenset(t) for t in itertools.combinations(range(order), 3)
            if all(frozenset(pair) in edges for pair in itertools.combinations(t, 2))]


def k_endpoints(edges: set[frozenset[int]], first: frozenset[int],
                second: frozenset[int]) -> tuple[int, int] | None:
    if first & second:
        return None
    cross = [edge for edge in edges if len(edge & first) == 1
             and len(edge & second) == 1]
    if len(cross) != 2 or cross[0] & cross[1]:
        return None
    used = cross[0] | cross[1]
    return next(iter(first - used)), next(iter(second - used))


def overlap_coefficients(edges: set[frozenset[int]]) -> tuple[int, int]:
    counts = [0, 0]
    for triple in itertools.combinations(triangle_sets(edges, 8), 3):
        if len(frozenset.union(*triple)) != 8:
            continue
        for centre_index in range(3):
            centre = triple[centre_index]
            outer = [triple[i] for i in range(3) if i != centre_index]
            if len(outer[0] & outer[1]) != 1:
                continue
            first = k_endpoints(edges, centre, outer[0])
            second = k_endpoints(edges, centre, outer[1])
            if first is not None and second is not None:
                counts[int(first[0] != second[0])] += 1
    return tuple(counts)


def local_upper(edges: set[frozenset[int]], order: int) -> bool:
    neighbors = [{other for other in range(order)
                  if frozenset((vertex, other)) in edges}
                 for vertex in range(order)]
    return all(len(neighbors[a] & neighbors[b]) <=
               (1 if frozenset((a, b)) in edges else 2)
               for a, b in itertools.combinations(range(order), 2))


def has_prism(edges: set[frozenset[int]], order: int) -> bool:
    for a, b in itertools.combinations(triangle_sets(edges, order), 2):
        if a & b:
            continue
        degrees = Counter()
        cross_count = 0
        for edge in edges:
            if len(edge & a) == len(edge & b) == 1:
                degrees.update(edge)
                cross_count += 1
        if cross_count == 3 and all(degrees[v] == 1 for v in a | b):
            return True
    return False


def audit_three_triangles(scan: dict) -> dict[str, int]:
    blocks = tuple(map(frozenset, scan["specified_triangles"]))
    assert blocks == tuple(map(frozenset, ((0, 1, 2), (3, 4, 5), (6, 7, 8))))
    internal = {frozenset(e) for block in blocks
                for e in itertools.combinations(block, 2)}
    options = []
    pairs = tuple(itertools.combinations(range(3), 2))
    for a, b in pairs:
        possible = tuple(frozenset(pair) for pair in
                         itertools.product(sorted(blocks[a]), sorted(blocks[b])))
        options.append(tuple(frozenset(matching)
                             for matching in itertools.combinations(possible, 2)
                             if not matching[0] & matching[1]))
    assert all(len(values) == 18 for values in options)
    histogram = Counter()
    for selected in itertools.product(*options):
        edges = internal | set().union(*selected)
        colours = [[] for _ in range(3)]
        for a, b in pairs:
            ends = k_endpoints(edges, blocks[a], blocks[b])
            assert ends is not None
            colours[a].append(ends[0])
            colours[b].append(ends[1])
        same = sum(len(set(colour)) == 1 for colour in colours)
        if not local_upper(edges, 9):
            outcome = "local_upper_fails"
        elif has_prism(edges, 9):
            outcome = "contains_prism"
        else:
            outcome = "local_upper_and_prism_free"
        histogram[(same, outcome)] += 1
    emitted = {(int(row["same_endpoint_corners"]), row["outcome"]):
               int(row["labeled_assignments"]) for row in scan["histogram"]}
    assert histogram == emitted
    assert sum(histogram.values()) == scan["complete_labeled_assignments"] == 5832
    assert histogram[3, "contains_prism"] == 108
    assert histogram[3, "local_upper_and_prism_free"] == 0
    assert set(scan["prism_free_local_controls"]) == {"0", "1", "2"}
    for key, control in scan["prism_free_local_controls"].items():
        edges = {frozenset(edge) for edge in control["edges"]}
        assert len(edges) == 15 and internal <= edges
        assert local_upper(edges, 9) and not has_prism(edges, 9)
        rows = [sum(1 << other for other in range(9)
                    if frozenset((vertex, other)) in edges) for vertex in range(9)]
        assert rows == control["rows"]
        colours = [[] for _ in blocks]
        for a, b in pairs:
            ua, ub = k_endpoints(edges, blocks[a], blocks[b])
            colours[a].append(ua)
            colours[b].append(ub)
        assert colours == control["endpoint_colours"]
        assert sum(len(set(values)) == 1 for values in colours) == int(key)
    return {"labeled_assignments": 5832, "prism_free_controls": 3,
            "locally_admissible_three_compatible_corners_all_prisms": 108}


def audit_signed_control(control: dict) -> dict[str, int]:
    size = int(control["vertex_count"])
    assert size == 231 and control["centre"] == 0
    positive = {tuple(edge) for edge in control["plus_relation_edges"]}
    negative = {tuple(edge) for edge in control["minus_relation_K_edges"]}
    assert len(positive) == len(control["plus_relation_edges"]) == 3696
    assert len(negative) == len(control["minus_relation_K_edges"]) == 4158
    assert not positive & negative
    matrix = [[4 * int(a == b) for b in range(size)] for a in range(size)]
    for value, edges in ((1, positive), (-1, negative)):
        for a, b in edges:
            assert 0 <= a < b < size
            matrix[a][b] = matrix[b][a] = value
    for row in matrix:
        assert Counter(row) == Counter({4: 1, 1: 32, -1: 36, 0: 162})
        assert sum(row) == 0
    nonzero = largest = 0
    for a in range(size):
        for b in range(a, size):
            residual = sum(x * y for x, y in zip(matrix[a], matrix[b])) - 21 * matrix[a][b]
            if a == 0:
                assert residual == 0
            if residual:
                nonzero += 1
                largest = max(largest, abs(residual))
    assert nonzero == control["full_projector_residual_upper_triangle_nonzero_count"]
    assert largest == control["full_projector_residual_maximum_absolute_entry"]
    assert nonzero > 0 and control["full_M2_equals_21M"] is False
    neighbors = {v for v in range(size) if matrix[0][v] == -1}
    colours = list(map(set, control["centre_endpoint_colour_classes"]))
    assert all(len(block) == 12 for block in colours)
    assert set.union(*colours) == neighbors and sum(map(len, colours)) == len(neighbors)
    assert not any(matrix[a][b] == -1 for a, b in itertools.combinations(neighbors, 2))
    same_hist = Counter(matrix[a][b] for block in colours
                        for a, b in itertools.combinations(block, 2))
    assert sum(same_hist.values()) == 198
    assert dict(sorted(same_hist.items())) == {
        int(key): value for key, value in control["centre_same_colour_relation_histogram"].items()}
    assert control["K_triangles_through_centre"] == 0
    return {"row_profiles_checked": size, "projector_upper_triangle_entries_checked":
            size * (size + 1) // 2, "nonzero_noncentre_residuals": nonzero}


def main() -> None:
    cert = json.loads(CERT.read_text(encoding="utf-8"))
    for name, value in cert["inputs_sha256"].items():
        assert digest(Path(name)) == value
    frozen = json.loads(FROZEN.read_text(encoding="utf-8"))
    counts = json.loads(COUNTS.read_text(encoding="utf-8"))
    masks = list(map(int, frozen["class_streams"]["8"]["canonical_masks"]))
    vector = {int(mask): int(count) for mask, count in
              counts["integral_pseudocount"]["order8_mask_count_pairs"]}
    assert len(masks) == len(set(masks)) == len(vector) == 916
    assert set(masks) == set(vector)
    active = []
    weighted = [0, 0]
    for mask in masks:
        same, different = overlap_coefficients(edge_set(mask, 8))
        if same:
            assert mask == 57358896 and same == 1 and different == 0
            edges = edge_set(mask, 8)
            roles = []
            for centre in triangle_sets(edges, 8):
                for outer in itertools.combinations(triangle_sets(edges, 8), 2):
                    if len(outer[0] & outer[1]) != 1:
                        continue
                    first = k_endpoints(edges, centre, outer[0])
                    second = k_endpoints(edges, centre, outer[1])
                    if first is not None and second is not None and first[0] == second[0]:
                        root = next(iter(outer[0] & outer[1]))
                        assert first[1] == second[1] == root
                        roles.append((centre, root, first[0]))
            assert len(roles) == 1
        if same or different:
            active.append([mask, vector[mask], same, different])
        weighted[0] += vector[mask] * same
        weighted[1] += vector[mask] * different
    overlap = cert["frozen_order8_overlap_count"]
    assert active == overlap["active_rows_mask_count_role_multiplicities"]
    assert weighted == [0, 10758]
    assert overlap["same_colour_pairwise_disjoint_outer_triangles"] == 231 * 3 * 66
    assert overlap["different_colour_pairwise_disjoint_outer_triangles"] == 231 * 432 - weighted[1]
    local = audit_signed_control(cert["exact_local_control"])
    scan = audit_three_triangles(cert["targeted_three_triangle_scan"])
    assert cert["claim_boundary"]["full_M2_implication_tested"] is False
    assert cert["claim_boundary"]["endpoint_excluded"] is False
    report = {
        "status": "INDEPENDENT_K_TRIANGLE_ENDPOINT_COMPATIBILITY_AUDIT_PASS",
        "producer_imported": False,
        "certificate_sha256": digest(CERT),
        "input_hashes_match": True,
        "frozen_masks_checked": 916,
        "active_overlap_classes": len(active),
        "weighted_same_and_different_overlap": weighted,
        "unique_same_overlap_role_is_one_Y_entry_equal_to_two": True,
        "signed_relation_control": local,
        "targeted_three_triangle_scan": scan,
        "full_M2_implication_or_SRG_exclusion_claimed": False,
    }
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
