"""Independent replay of the source-724 pair-violation classification."""

from __future__ import annotations

from collections import Counter
import hashlib
import itertools
import json
import os
from pathlib import Path

from scratch_theory_e71_defect_rank_probe import SUPPORTS


WITNESS = Path("scratch_theory_e71_source724_degree_witness.json")
DISCOVERY = Path("scratch_theory_e71_source724_pair_violation_discovery.json")
OUTPUT = Path("scratch_theory_e71_source724_pair_violation_discovery_audit.json")


def atomic_json(path, value):
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def labels(vertex):
    g, h = SUPPORTS[vertex // 4]
    local = vertex % 4
    return 2 * g + local // 2, 2 * h + local % 2


def relation(left, right):
    first, second = SUPPORTS[left // 4], SUPPORTS[right // 4]
    if first == second:
        return "same"
    return "overlap" if set(first) & set(second) else "disjoint"


def refine(adjacency, cells):
    cells = tuple(tuple(cell) for cell in cells if cell)
    while True:
        cell_masks = [sum(1 << vertex for vertex in cell) for cell in cells]
        answer = []
        for cell in cells:
            groups = {}
            for vertex in cell:
                key = tuple((adjacency[vertex] & mask).bit_count()
                            for mask in cell_masks)
                groups.setdefault(key, []).append(vertex)
            answer.extend(tuple(sorted(groups[key])) for key in sorted(groups))
        answer = tuple(answer)
        if answer == cells:
            return answer
        cells = answer


def exact_role_mask(adjacency, role_sizes):
    cells = []
    first = 0
    for size in role_sizes:
        cells.append(tuple(range(first, first + size)))
        first += size

    def encode(order):
        value = 0
        place = 0
        for i, left in enumerate(order):
            for right in order[i + 1:]:
                value |= ((adjacency[left] >> right) & 1) << place
                place += 1
        return value

    def search(partition):
        partition = refine(adjacency, partition)
        split = next((i for i, cell in enumerate(partition) if len(cell) > 1), None)
        if split is None:
            return encode(tuple(cell[0] for cell in partition))
        best = None
        cell = partition[split]
        for chosen in reversed(cell):  # opposite traversal order from producer
            rest = tuple(vertex for vertex in cell if vertex != chosen)
            child = partition[:split] + ((chosen,), rest) + partition[split + 1:]
            candidate = search(child)
            best = candidate if best is None else min(best, candidate)
        return best

    return search(tuple(cells))


def certificate(left, right, selected, full_adjacency):
    selected = tuple(sorted(selected))
    outer = (left, right) + selected
    root_labels = tuple(sorted({item for vertex in outer for item in labels(vertex)}))
    label_position = {item: index + 1 for index, item in enumerate(root_labels)}
    outer_start = len(root_labels) + 1
    n = outer_start + len(outer)
    adjacency = [0] * n

    def add(x, y):
        adjacency[x] |= 1 << y
        adjacency[y] |= 1 << x

    for item in root_labels:
        add(0, label_position[item])
    for x, y in itertools.combinations(root_labels, 2):
        if x // 2 == y // 2:
            add(label_position[x], label_position[y])
    for index, vertex in enumerate(outer):
        for item in labels(vertex):
            add(outer_start + index, label_position[item])
    for i, x in enumerate(outer):
        for j, y in enumerate(outer[i + 1:], i + 1):
            if (full_adjacency[x] >> y) & 1:
                add(outer_start + i, outer_start + j)
    canonical = exact_role_mask(tuple(adjacency), (1, len(root_labels), 2, len(selected)))
    proof_edges = ([] if not ((full_adjacency[left] >> right) & 1)
                   else [(left, right)])
    for common in selected:
        proof_edges.extend(((left, common), (right, common)))
    proof_free = sum(relation(x, y) == "disjoint" for x, y in proof_edges)
    induced_free = sum(
        relation(x, y) == "disjoint" and ((full_adjacency[x] >> y) & 1)
        for x, y in itertools.combinations(outer, 2)
    )
    return {
        "order": n,
        "mask": canonical,
        "root_labels": root_labels,
        "edge_count": sum(mask.bit_count() for mask in adjacency) // 2,
        "proof_free": proof_free,
        "induced_free": induced_free,
    }


def main():
    witness_raw = WITNESS.read_bytes()
    discovery_raw = DISCOVERY.read_bytes()
    witness = json.loads(witness_raw)
    discovery = json.loads(discovery_raw)
    for path, expected in discovery["inputs"].items():
        assert hashlib.sha256(Path(path).read_bytes()).hexdigest().upper() == expected
    adjacency = [0] * 84
    fixed_adjacency = [0] * 84
    for left, right in witness["edge_list_zero_based"]:
        adjacency[left] |= 1 << right
        adjacency[right] |= 1 << left
        if relation(left, right) != "disjoint":
            fixed_adjacency[left] |= 1 << right
            fixed_adjacency[right] |= 1 << left
    assert all(mask.bit_count() == 12 for mask in adjacency)
    rows = [[0] * 21 for _ in range(84)]
    for vertex in range(84):
        for target in range(21):
            rows[vertex][target] = sum(
                (adjacency[vertex] >> other) & 1
                for other in range(4 * target, 4 * target + 4)
            )

    records = {tuple(record["pair"]): record for record in discovery["records"]}
    assert len(records) == 1025
    residual_histogram = Counter()
    order_histogram = Counter()
    positive = set()
    forced = []
    canonical_masks_replayed = 0
    subset_certificates_replayed = 0
    fixed_residual_histogram = Counter()
    for left, right in itertools.combinations(range(84), 2):
        adjacent = (adjacency[left] >> right) & 1
        common_mask = adjacency[left] & adjacency[right]
        root_overlap = len(set(labels(left)) & set(labels(right)))
        residual = adjacent + common_mask.bit_count() - (2 - root_overlap)
        residual_histogram[residual] += 1
        fixed_adj = (fixed_adjacency[left] >> right) & 1
        fixed_residual = fixed_adj + (
            fixed_adjacency[left] & fixed_adjacency[right]
        ).bit_count() - (2 - root_overlap)
        fixed_residual_histogram[fixed_residual] += 1

        block_relation = relation(left, right)
        fixed_adjacent = adjacent if block_relation != "disjoint" else 0
        lower_bound = 0
        for target in range(21):
            dx, dy = rows[left][target], rows[right][target]
            if right // 4 == target:
                dx -= fixed_adjacent
            if left // 4 == target:
                dy -= fixed_adjacent
            available = 4 - int(left // 4 == target) - int(right // 4 == target)
            lower_bound += max(0, dx + dy - available)
        if fixed_adjacent + root_overlap + lower_bound > 2:
            forced.append((left, right))

        if residual <= 0:
            assert (left, right) not in records
            continue
        positive.add((left, right))
        record = records[(left, right)]
        assert record["adjacent"] == adjacent
        assert record["root_overlap"] == root_overlap
        assert record["common_outer"] == common_mask.bit_count()
        assert record["excess"] == residual
        assert record["fibre_relation"] == block_relation
        assert record["fibre_degree_row_common_neighbour_lower_bound"] == lower_bound
        minimum_count = 3 - adjacent - root_overlap
        assert record["minimum_outer_witnesses"] == minimum_count
        common = tuple(vertex for vertex in range(84)
                       if (common_mask >> vertex) & 1)

        independently_best = None
        for selected in itertools.combinations(common, minimum_count):
            check = certificate(left, right, selected, tuple(adjacency))
            subset_certificates_replayed += 1
            key = (check["order"], check["mask"], tuple(selected))
            if independently_best is None or key < independently_best[0]:
                independently_best = key, check
        assert independently_best is not None
        selected = tuple(record["minimum_rooted_certificate"]
                         ["outer_common_witnesses"])
        stored = record["minimum_rooted_certificate"]
        check = certificate(left, right, selected, tuple(adjacency))
        canonical_masks_replayed += 1
        assert independently_best[0] == (check["order"], check["mask"], selected)
        assert stored["order"] == check["order"]
        assert int(stored["canonical_layer_marked_mask_hex"], 16) == check["mask"]
        assert tuple(stored["root_neighbour_labels"]) == check["root_labels"]
        assert stored["induced_edges"] == check["edge_count"]
        assert stored["proof_edges_from_free_disjoint_blocks"] == check["proof_free"]
        assert stored["induced_edges_from_free_disjoint_blocks"] == check["induced_free"]
        assert check["proof_free"] >= 1
        order_histogram[check["order"]] += 1

    assert positive == set(records)
    assert len(positive) == witness["positive_pair_upper_violations"] == 1025
    assert not forced
    expected_residual = {
        int(value): count for value, count in
        discovery["all_pair_residual_histogram"].items()
    }
    assert residual_histogram == expected_residual
    expected_orders = {
        int(value): count for value, count in discovery[
            "classification_histograms"
        ]["minimum_rooted_certificate_order"].items()
    }
    assert order_histogram == expected_orders
    assert min(order_histogram) == 9
    assert not any(residual > 0 for residual in fixed_residual_histogram)
    expected_fixed = {
        int(value): count for value, count in discovery[
            "fixed_local_vs_free_completion"
        ]["all_84_vertex_fixed_internal_and_overlap_residual_histogram"].items()
    }
    assert fixed_residual_histogram == expected_fixed

    result = {
        "status": "SOURCE724_PAIR_VIOLATION_DISCOVERY_INDEPENDENT_AUDIT_PASS",
        "inputs": {
            str(WITNESS): hashlib.sha256(witness_raw).hexdigest().upper(),
            str(DISCOVERY): hashlib.sha256(discovery_raw).hexdigest().upper(),
        },
        "outer_degrees_verified": True,
        "all_discovery_input_hashes_verified": True,
        "all_pairs_replayed": 84 * 83 // 2,
        "positive_violations_replayed": len(positive),
        "minimum_subset_certificates_replayed": subset_certificates_replayed,
        "stored_canonical_masks_replayed": canonical_masks_replayed,
        "minimum_certificate_order_histogram": {
            str(order): count for order, count in sorted(order_histogram.items())
        },
        "degree_row_forced_pair_violations": len(forced),
        "fixed_internal_and_overlap_positive_pair_violations": 0,
        "every_certificate_uses_a_free_disjoint_proof_edge": True,
        "scope_boundary_verified": (
            "The audited input is one deterministic completion, not all 128 "
            "feasible source724 rank-three degree branches."
        ),
    }
    atomic_json(OUTPUT, result)
    print(json.dumps({"path": str(OUTPUT), **result}, sort_keys=True))


if __name__ == "__main__":
    main()
