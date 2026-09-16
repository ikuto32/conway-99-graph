"""Emit exact canonical local representatives for the surviving E0=78 ports.

The two support types are K2,3 and C6.  We regenerate every bounded local
graph, quotient by the full induced action of the setwise S7 support
stabilizer and independent symbol flips, and verify coverage both directly
and with Burnside's lemma.  No SAT solver is used.
"""

from __future__ import annotations

from collections import Counter
import itertools
import json
from pathlib import Path

import scratch_general_e79_local_audit as local79
import scratch_general_e78_local_ports_all as ports
from scratch_general_exact_sat import coordinates


COMPRESSION = Path("scratch_general_e78_local_compression.json")
PORT_RESULT = Path("scratch_general_e78_local_ports_all.json")
OUTPUT = Path("scratch_general_e78_local_reps.json")


def enumerate_graphs(source):
    supports = tuple(tuple(item["support"]) for item in source["exceptional_supports"])
    choices = tuple(ports.fibre_variants(support, 1) for support in supports)
    answer = set()
    for oriented in itertools.product(*choices):
        by_group = tuple(ports.group_matchings(oriented, group) for group in local79.GROUPS)
        if any(not rows for rows in by_group):
            continue
        internal = frozenset(edge for data in oriented for edge in data["internal"])
        vertices = tuple(vertex for data in oriented for vertex in data["vertices"])
        for selected in itertools.product(*by_group):
            overlap = frozenset(edge for group_edges in selected for edge in group_edges)
            assert len(overlap) == 12
            graph = internal | overlap
            if not local79.induced_pair_upper(vertices, graph):
                continue
            if not ports.forced_c4_support_bp_feasible(supports, oriented, graph):
                continue
            answer.add(graph)
    return supports, answer


def action_data(supports, graphs):
    vertices = tuple(sorted({vertex for graph in graphs for edge in graph for vertex in edge}))
    assert len(vertices) == 24
    vertex_index = {vertex: index for index, vertex in enumerate(vertices)}
    pairs = tuple(itertools.combinations(range(24), 2))
    pair_index = {pair: index for index, pair in enumerate(pairs)}

    def mask_of(graph):
        mask = 0
        for u, v in graph:
            pair = tuple(sorted((vertex_index[u], vertex_index[v])))
            mask |= 1 << pair_index[pair]
        return mask

    def graph_of(mask):
        answer = set()
        while mask:
            low = mask & -mask
            bit = low.bit_length() - 1
            u, v = pairs[bit]
            answer.add(tuple(sorted((vertices[u], vertices[v]))))
            mask ^= low
        return frozenset(answer)

    vertex_actions = local79.local_actions(supports, vertices)
    edge_actions = tuple(
        tuple(pair_index[tuple(sorted((action[u], action[v])))] for u, v in pairs)
        for action in vertex_actions
    )

    def transform(mask, edge_action):
        result = 0
        while mask:
            low = mask & -mask
            bit = low.bit_length() - 1
            result |= 1 << edge_action[bit]
            mask ^= low
        return result

    universe = {mask_of(graph) for graph in graphs}
    assert len(universe) == len(graphs)

    # Direct invariance under every enumerated group action.
    for action in edge_actions:
        assert {transform(mask, action) for mask in universe} == universe

    unseen = set(universe)
    orbits = []
    while unseen:
        seed = min(unseen)
        orbit = {transform(seed, action) for action in edge_actions}
        assert orbit <= unseen
        canonical = min(orbit)
        assert canonical == seed
        fixed = sum(transform(canonical, action) == canonical for action in edge_actions)
        assert fixed * len(orbit) == len(edge_actions)
        orbits.append({
            "canonical_mask": canonical,
            "orbit": orbit,
            "orbit_size": len(orbit),
            "representative_action_stabilizer_order": fixed,
            "graph": graph_of(canonical),
        })
        unseen -= orbit

    # Independent orbit count by Burnside's lemma.
    fixed_sum = sum(
        sum(transform(mask, action) == mask for mask in universe)
        for action in edge_actions
    )
    assert fixed_sum % len(edge_actions) == 0
    burnside_orbits = fixed_sum // len(edge_actions)
    assert burnside_orbits == len(orbits)
    assert sum(row["orbit_size"] for row in orbits) == len(universe)
    return vertices, edge_actions, orbits, burnside_orbits


def serialize_representative(orbit_id, orbit, supports, vertices, outer_index, variables):
    graph = orbit["graph"]
    local_index = {vertex: index for index, vertex in enumerate(vertices)}
    support_of = {vertex: tuple(symbol // 2 for symbol in vertex) for vertex in vertices}
    present_local = sorted(tuple(sorted((local_index[u], local_index[v]))) for u, v in graph)
    present_outer = sorted(tuple(sorted((outer_index[u], outer_index[v]))) for u, v in graph)
    fixed_absent = []
    for u, v in itertools.combinations(vertices, 2):
        if not (set(support_of[u]) & set(support_of[v])):
            continue
        edge = tuple(sorted((u, v)))
        if edge not in graph:
            fixed_absent.append(tuple(sorted((outer_index[u], outer_index[v]))))
    block_counts = Counter(
        tuple(sorted((supports.index(support_of[u]), supports.index(support_of[v]))))
        for u, v in graph
        if support_of[u] != support_of[v]
    )
    assert len(graph) == 30
    assert sum(value * value for value in block_counts.values()) in (18, 24)
    return {
        "representative_id": orbit_id,
        "canonical_mask_hex_over_C24_2": hex(orbit["canonical_mask"]),
        "orbit_size": orbit["orbit_size"],
        "representative_action_stabilizer_order": orbit["representative_action_stabilizer_order"],
        "present_edge_count": len(graph),
        "present_edges_local_indices": [list(edge) for edge in present_local],
        "present_edges_symbol_labels": [[list(u), list(v)] for u, v in sorted(graph)],
        "present_edges_outer_indices_zero_based": [list(edge) for edge in present_outer],
        "present_edges_graph_vertices_one_based": [[u + 16, v + 16] for u, v in present_outer],
        "positive_general_cnf_edge_variables": [variables[edge] for edge in present_outer],
        "fixed_absent_nondisjoint_outer_pairs_zero_based": [list(edge) for edge in fixed_absent],
        "negative_general_cnf_edge_variables": [-variables[edge] for edge in fixed_absent],
        "overlap_block_counts_by_support_index": [
            [u, v, value] for (u, v), value in sorted(block_counts.items())
        ],
        "overlap_square_M2": sum(value * value for value in block_counts.values()),
    }


def main():
    compression = json.loads(COMPRESSION.read_text(encoding="utf-8"))
    prior = json.loads(PORT_RESULT.read_text(encoding="utf-8"))
    target_meta = [
        row for row in prior["rows"]
        if row["after_forced_C4_support_BP"] > 0
    ]
    assert {(row["compression_orbit_index"], row["after_forced_C4_support_BP"]) for row in target_meta} == {(3, 512), (19, 128)}
    compression_rows = {
        row["orbit_index"]: row
        for row in compression["rows"]
        if tuple(row["partition"]) == (1, 1, 1, 1, 1, 1)
    }
    labels, outer_index, variables, _edge = coordinates()
    records = []
    for meta in sorted(target_meta, key=lambda row: row["compression_orbit_index"]):
        source = compression_rows[meta["compression_orbit_index"]]
        supports, graphs = enumerate_graphs(source)
        assert len(graphs) == meta["after_forced_C4_support_BP"]
        vertices, actions, orbits, burnside = action_data(supports, graphs)
        expected_orbits = meta["after_forced_C4_support_BP_orbits"]
        assert len(orbits) == burnside == expected_orbits
        support_form = "K2,3" if len(graphs) == 512 else "C6"
        vertex_records = []
        for local, vertex in enumerate(vertices):
            zero = outer_index[vertex]
            vertex_records.append({
                "local_index": local,
                "symbol_label": list(vertex),
                "support": [symbol // 2 for symbol in vertex],
                "signs": [symbol % 2 for symbol in vertex],
                "outer_index_zero_based": zero,
                "graph_vertex_one_based": zero + 16,
            })
        reps = [
            serialize_representative(index, orbit, supports, vertices, outer_index, variables)
            for index, orbit in enumerate(orbits)
        ]
        assert sum(row["orbit_size"] for row in reps) == len(graphs)
        records.append({
            "support_form": support_form,
            "compression_orbit_index": meta["compression_orbit_index"],
            "supports_in_fibre_order": [list(support) for support in supports],
            "support_stabilizer_order_in_S7": source["stabilizer_order"],
            "distinct_induced_stabilizer_flip_actions": len(actions),
            "local_vertex_order": vertex_records,
            "local_graph_count": len(graphs),
            "orbit_count_direct": len(orbits),
            "orbit_count_burnside": burnside,
            "orbit_sizes": [row["orbit_size"] for row in reps],
            "orbit_sizes_sum": sum(row["orbit_size"] for row in reps),
            "representatives": reps,
            "coverage_verified": True,
        })
        print(json.dumps({
            "support_form": support_form,
            "graphs": len(graphs),
            "actions": len(actions),
            "orbits": len(orbits),
            "orbit_sizes": [row["orbit_size"] for row in reps],
            "burnside": burnside,
        }), flush=True)
    result = {
        "model": "exact canonical local representatives for E0=78 K2,3 and C6",
        "vertex_encoding": (
            "symbol labels are unordered pairs from 0..13; support is symbol//2; "
            "outer_index follows scratch_general_exact_sat.coordinates(); one-based graph "
            "vertex is outer_index+16 (vertices 1..15 are root/inner)."
        ),
        "canonical_encoding": (
            "bit i corresponds to the i-th lexicographic pair from combinations(range(24),2) "
            "in local_vertex_order; representatives minimize this integer under all induced actions."
        ),
        "records": records,
        "global_coverage_verified": all(row["coverage_verified"] for row in records),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
