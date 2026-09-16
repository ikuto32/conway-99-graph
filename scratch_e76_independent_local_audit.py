"""Mechanical audit of the independent E0=76 local and integer artifacts."""

from __future__ import annotations

from collections import Counter
import itertools
import json
from pathlib import Path


LOCAL = Path("scratch_e76_independent_local.json")
INTEGER = Path("scratch_e76_independent_integer.json")
OUTPUT = Path("scratch_e76_independent_local_audit.json")
SUPPORTS = tuple(itertools.combinations(range(7), 2))
LABELS = tuple(
    pair
    for pair in itertools.combinations(range(14), 2)
    if pair[0] // 2 != pair[1] // 2
)
LABEL_INDEX = {label: index for index, label in enumerate(LABELS)}
DISJOINT_PAIRS = tuple(
    pair
    for pair in itertools.combinations(range(21), 2)
    if set(SUPPORTS[pair[0]]).isdisjoint(SUPPORTS[pair[1]])
)


def audit_representative(representative, exceptional_items):
    exceptional = {
        tuple(item["support"]): item["deficit"] for item in exceptional_items
    }
    raw_edges = representative["edges_by_symbol_label"]
    edges = frozenset(
        tuple(sorted((tuple(raw[0]), tuple(raw[1])))) for raw in raw_edges
    )
    assert len(edges) == len(raw_edges) == representative["local_edge_count"]
    expected_indices = [
        [LABEL_INDEX[u], LABEL_INDEX[v]] for u, v in sorted(edges)
    ]
    assert expected_indices == representative["edges_by_outer_index_zero_based"]
    internal_counts = Counter()
    overlap = []
    vertices = set()
    for u, v in edges:
        vertices.update((u, v))
        A = tuple(symbol // 2 for symbol in u)
        B = tuple(symbol // 2 for symbol in v)
        assert A in exceptional and B in exceptional
        if A == B:
            internal_counts[A] += 1
        else:
            assert set(A) & set(B)
            overlap.append((u, v))
    assert all(internal_counts[support] == 4 - deficit for support, deficit in exceptional.items())
    assert len(overlap) == 16
    assert len(edges) == sum(4 - deficit for deficit in exceptional.values()) + 16

    all_vertices = tuple(
        label
        for support in exceptional
        for label in LABELS
        if tuple(symbol // 2 for symbol in label) == support
    )
    assert len(all_vertices) == 4 * len(exceptional)
    neighbours = {vertex: set() for vertex in all_vertices}
    for u, v in edges:
        neighbours[u].add(v)
        neighbours[v].add(u)
    for u, v in itertools.combinations(all_vertices, 2):
        assert (
            len(neighbours[u] & neighbours[v]) + int(v in neighbours[u])
            <= 2 - len(set(u) & set(v))
        )
    block_counts = Counter(
        tuple(sorted((
            tuple(symbol // 2 for symbol in u),
            tuple(symbol // 2 for symbol in v),
        )))
        for u, v in overlap
    )
    block_square = sum(value * value for value in block_counts.values())
    return block_square


def main():
    local = json.loads(LOCAL.read_text(encoding="utf-8"))
    integer = json.loads(INTEGER.read_text(encoding="utf-8"))
    assert local["ok"] and integer["ok"]
    assert (
        local["exact_overlap_completions"],
        local["after_exact_real_disjoint_bound"],
        local["after_induced_pair_upper"],
        local["after_ordinary_c4_support_BP"],
        local["support_orbits_after_forced_BP"],
        local["local_graph_orbits"],
    ) == (130560, 130560, 109696, 68864, 10, 311)

    representative_count = 0
    raw_orbit_sum = 0
    local_key_map = {}
    for row in local["rows"]:
        key = (tuple(row["partition"]), row["compression_orbit_index"])
        local_key_map[key] = row
        representatives = row["representatives"]
        assert len(representatives) == row["local_graph_orbits"]
        assert sum(rep["local_orbit_size"] for rep in representatives) == row["distinct_forced_local_graphs"]
        assert row["distinct_forced_local_graphs"] == row["stages"].get("after_ordinary_c4_support_BP", 0)
        seen = set()
        for representative in representatives:
            square = audit_representative(representative, row["exceptional_supports"])
            signature = tuple(
                tuple(tuple(endpoint) for endpoint in edge)
                for edge in representative["edges_by_symbol_label"]
            )
            assert signature not in seen
            seen.add(signature)
            assert str(square) in row["after_forced_BP_square_histogram"]
        representative_count += len(representatives)
        raw_orbit_sum += sum(rep["local_orbit_size"] for rep in representatives)
    assert representative_count == 311 and raw_orbit_sum == 68864

    integer_representatives = 0
    integer_raw = 0
    for row in integer["rows"]:
        key = (tuple(row["partition"]), row["compression_orbit_index"])
        local_row = local_key_map[key]
        solved = row["disjoint_integer"]
        assert solved["status"] == "OPTIMAL"
        values = {pair: 0 for pair in DISJOINT_PAIRS}
        for left, right, value in solved["witness_nonzero"]:
            pair = (left, right)
            assert pair in values and values[pair] == 0
            values[pair] = value
        deficits = [0] * 21
        for item in row["exceptional_supports"]:
            deficits[item["support_index"]] = item["deficit"]
        row_sums = [
            sum(value for pair, value in values.items() if support in pair)
            for support in range(21)
        ]
        objective = sum(value * value for value in values.values())
        assert row_sums == [2 * deficit for deficit in deficits]
        assert row_sums == solved["witness_row_sums"]
        assert objective == solved["minimum_square"]
        assert all(-12 <= value <= 4 for value in values.values())
        assert solved["witness_directly_verified"]
        assert solved["agrees_with_compression_minimum"]

        kept = row["representatives_after_integer_bound"]
        assert len(kept) == row["local_orbits_after_integer_bound"]
        assert sum(rep["local_orbit_size"] for rep in kept) == row["raw_local_graphs_after_integer_bound"]
        for representative in kept:
            square = audit_representative(representative, row["exceptional_supports"])
            assert square == representative["actual_overlap_block_square"]
            assert square + objective == representative["integer_plus_overlap_square"]
            assert square + objective <= row["joint_square_budget"]
        # In this run the integer minimum causes no additional local removal.
        assert len(kept) == local_row["local_graph_orbits"]
        assert row["raw_local_graphs_after_integer_bound"] == local_row["distinct_forced_local_graphs"]
        integer_representatives += len(kept)
        integer_raw += row["raw_local_graphs_after_integer_bound"]
    assert integer_representatives == 311 and integer_raw == 68864

    result = {
        "model": "mechanical independent-output audit for E0=76 local expansion",
        "stage_totals_verified": True,
        "all_311_explicit_representatives_verified": True,
        "each_support_orbit_sum_covers_raw_survivors": True,
        "raw_survivor_total": raw_orbit_sum,
        "all_10_integer_witnesses_directly_reverified": True,
        "integer_bound_removed_no_local_graphs": True,
        "formal_solver_certificates": None,
        "ok": True,
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
