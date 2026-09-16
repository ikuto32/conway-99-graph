"""Independent local-representative cross-check of the source133 balance.

For source row 133 put d=+1 on A_i={0,i}, d=-1 on B_i={1,i}
(i=2,3,4), and zero on ordinary fibres.  The exact SRG norm saturation
proved in ``scratch_theory_e72_k23_balance.md`` requires h=Bd to vanish on
68 outer vertices.  Ordinary-fibre values are checked solely from supports.
For each of the 8,060 explicit local graph orbits, the six not-yet-present
disjoint exceptional blocks are then exhaustively completed subject to

* their exact full-Gram totals D=2;
* the existing forced-C4 vertex profiles;
* h=0 at all 24 exceptional vertices; and, in a second pass,
* induced-pair upper after all six blocks are added.

This validates the labelling and exposes exactly how much extra pruning the
new pointwise condition supplies.  Local compatibility is not a proof that a
representative extends to a full SRG.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
from collections import Counter, defaultdict
from pathlib import Path

import scratch_general_e79_local_audit as local79
from scratch_general_e72_q3_disjoint_gram_filter import (
    gram_disjoint_targets,
    overlap_key,
    row_geometry,
)
from scratch_general_e72_source248_local_probe import (
    PairUpperState,
    candidate_domains,
    normal_edge,
    search_blocks,
    vertex_profiles,
)


INPUT_PATH = Path("scratch_general_e72_q3_gram_fast_expansion_part_27_orbit_000.json")
MACRO_PATH = Path("scratch_general_e72_q3_gram_fast_expansion_macro_catalog.json")
THEORY_PATH = Path("scratch_theory_e72_k23_balance_audit.json")
OUTPUT_PATH = Path("scratch_general_e72_source133_balance_crosscheck.json")
SOURCE_ROW_INDEX = 133


def atomic_json(path: Path, value) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def side_of_support(support) -> int:
    support = tuple(support)
    if support in ((0, 2), (0, 3), (0, 4)):
        return 1
    if support in ((1, 2), (1, 3), (1, 4)):
        return -1
    return 0


def internal_key(edges, fibre_of):
    return frozenset(
        edge
        for edge in edges
        if fibre_of[edge[0]] == fibre_of[edge[1]]
    )


def witness_extra_edges(witness, vertices):
    return frozenset(
        normal_edge(vertices[x], vertices[y])
        for _, candidate in witness
        for x, y in candidate[1]
    )


def verify_balance_witness(
    supports,
    vertices,
    fibre_of,
    base_edges,
    extra_edges,
    targets,
    require_pair_upper,
):
    counts = Counter()
    for left, right in extra_edges:
        f, g = fibre_of[left], fibre_of[right]
        assert not (set(supports[f]) & set(supports[g]))
        counts[tuple(sorted((f, g)))] += 1
    assert dict(counts) == targets
    graph = frozenset(base_edges) | frozenset(extra_edges)
    neighbours = local79.neighbour_sets(vertices, graph)
    for vertex in vertices:
        h = sum(side_of_support(supports[fibre_of[other]]) for other in neighbours[vertex])
        assert h == 0
    if require_pair_upper:
        assert local79.induced_pair_upper(vertices, graph)


def run(limit=None) -> None:
    document = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    macro_document = json.loads(MACRO_PATH.read_text(encoding="utf-8"))
    theory = json.loads(THEORY_PATH.read_text(encoding="utf-8"))
    assert document["status"] == "COMPLETE"
    assert theory["status"] == "EXACT_SUPPORT_ARITHMETIC_VERIFIED"
    assert theory["source_row_index"] == SOURCE_ROW_INDEX
    row = document["row"] if "row" in document else document["rows"][0]
    assert row["compression_orbit_index"] == 0
    assert row["partition"] == [2, 2, 2, 2, 2, 2]
    assert row["after_forced_C4_support_BP"] == 2_502_656
    assert row["local_graph_orbits"] == 8_060

    macro_rows = [
        entry
        for entry in macro_document["macro_entries"]
        if entry["source_row_index"] == SOURCE_ROW_INDEX
    ]
    assert len(macro_rows) == 5
    assert all(entry["signature_stabilizer_canonical"] for entry in macro_rows)
    assert sum(entry["signature_orbit_labelled_coverage"] for entry in macro_rows) == 2_502_656

    supports, vertices_by_fibre, fibre_of, W = row_geometry(row)
    assert supports == ((0, 2), (0, 3), (0, 4), (1, 2), (1, 3), (1, 4))
    vertices = tuple(sorted(fibre_of))
    side_by_fibre = tuple(side_of_support(support) for support in supports)
    assert side_by_fibre == (1, 1, 1, -1, -1, -1)

    macro_by_internal = {}
    for entry in macro_rows:
        flattened = frozenset(
            normal_edge(left, right)
            for left, right in entry["internal_edges"]
        )
        assert flattened not in macro_by_internal
        macro_by_internal[flattened] = entry

    # The ordinary-C4 block rule gives these h values pointwise, independent
    # of any local representative or port orientation.
    all_supports = tuple(itertools.combinations(range(7), 2))
    ordinary_support_h = {}
    for support in all_supports:
        if support in supports:
            continue
        disjoint_exceptional = tuple(
            exceptional
            for exceptional in supports
            if not (set(support) & set(exceptional))
        )
        ordinary_support_h[support] = sum(
            side_of_support(exceptional) for exceptional in disjoint_exceptional
        )
    negative = tuple(support for support, h in ordinary_support_h.items() if h == -3)
    positive = tuple(support for support, h in ordinary_support_h.items() if h == 3)
    zero = tuple(support for support, h in ordinary_support_h.items() if h == 0)
    assert negative == ((0, 5), (0, 6))
    assert positive == ((1, 5), (1, 6))
    assert len(zero) == 11
    assert 4 * sum(value * value for value in ordinary_support_h.values()) == 144
    assert 4 * len(zero) + len(vertices) == 68

    representatives = row["local_graph_representatives"]
    if limit is not None:
        representatives = representatives[:limit]
    target_cache = {}
    per_macro = defaultdict(lambda: Counter())
    results = []
    first_balance_witness = {}
    first_pair_witness = {}
    for number, representative in enumerate(representatives):
        base_edges = frozenset(
            normal_edge(left, right) for left, right in representative["edges"]
        )
        macro = macro_by_internal[internal_key(base_edges, fibre_of)]
        macro_number = macro["state_orbit_number"]
        assert representative["Q"] == macro["Q"]

        key = overlap_key(supports, fibre_of, base_edges)
        if key not in target_cache:
            targets, detail = gram_disjoint_targets(row, representative, supports, W)
            assert targets not in (None, False)
            assert set(targets.values()) == {2}
            assert len(targets) == 6
            target_cache[key] = targets
        targets = target_cache[key]

        # Recompute the signed exceptional edge quadratic form from the
        # actual representative.  The missing six cross-side blocks contribute
        # -12, so every representative gives d^T B d = 0 exactly.
        known_signed_edge_sum = sum(
            side_by_fibre[fibre_of[left]] * side_by_fibre[fibre_of[right]]
            for left, right in base_edges
        )
        assert known_signed_edge_sum == 12
        assert 2 * (known_signed_edge_sum - sum(targets.values())) == 0

        profiles, component = vertex_profiles(
            supports, vertices_by_fibre, fibre_of, base_edges
        )
        base_neighbours = local79.neighbour_sets(vertices, base_edges)
        filtered_profiles = {}
        required_degrees = {}
        empty_vertices = []
        for fibre, fibre_vertices in enumerate(vertices_by_fibre):
            sign = side_by_fibre[fibre]
            for vertex in fibre_vertices:
                partial_h = sum(
                    side_by_fibre[fibre_of[other]]
                    for other in base_neighbours[vertex]
                )
                # Every missing disjoint exceptional neighbour has the
                # opposite sign, hence degree = sign*partial_h is exactly the
                # condition that the completed h value vanish.
                required = sign * partial_h
                required_degrees[vertex] = required
                filtered = tuple(
                    option for option in profiles[vertex] if sum(option) == required
                )
                filtered_profiles[vertex] = filtered
                if not filtered:
                    empty_vertices.append(vertex)
        assert sum(required_degrees.values()) == 2 * sum(targets.values())

        balance_witness = pair_witness = None
        balance_nodes = pair_nodes = None
        raw_domain_sizes = pair_domain_sizes = {}
        if not empty_vertices:
            pair_state = PairUpperState(vertices, base_edges)
            raw_domains, pair_domains = candidate_domains(
                supports,
                vertices_by_fibre,
                vertices,
                filtered_profiles,
                component,
                targets,
                pair_state,
            )
            raw_domain_sizes = {block: len(values) for block, values in raw_domains.items()}
            pair_domain_sizes = {block: len(values) for block, values in pair_domains.items()}
            if all(raw_domain_sizes.values()):
                balance_witness, balance_nodes = search_blocks(
                    raw_domains, filtered_profiles
                )
            if all(pair_domain_sizes.values()):
                pair_witness, pair_nodes = search_blocks(
                    pair_domains, filtered_profiles, pair_state
                )

        balance_pass = balance_witness is not None
        pair_pass = pair_witness is not None
        assert not pair_pass or balance_pass
        mass = representative["orbit_size"]
        stats = per_macro[macro_number]
        stats["input_orbits"] += 1
        stats["input_raw_mass"] += mass
        if balance_pass:
            stats["balance_orbits"] += 1
            stats["balance_raw_mass"] += mass
            extra = witness_extra_edges(balance_witness, vertices)
            verify_balance_witness(
                supports, vertices, fibre_of, base_edges, extra, targets, False
            )
            first_balance_witness.setdefault(
                macro_number,
                {
                    "mask_hex": representative["mask_hex"],
                    "base_edges": representative["edges"],
                    "extra_edges": [[list(left), list(right)] for left, right in sorted(extra)],
                },
            )
        if pair_pass:
            stats["pair_orbits"] += 1
            stats["pair_raw_mass"] += mass
            extra = witness_extra_edges(pair_witness, vertices)
            verify_balance_witness(
                supports, vertices, fibre_of, base_edges, extra, targets, True
            )
            first_pair_witness.setdefault(
                macro_number,
                {
                    "mask_hex": representative["mask_hex"],
                    "base_edges": representative["edges"],
                    "extra_edges": [[list(left), list(right)] for left, right in sorted(extra)],
                },
            )
        results.append(
            {
                "representative_number": number,
                "mask_hex": representative["mask_hex"],
                "orbit_size": mass,
                "Q": representative["Q"],
                "state_macro_number": macro_number,
                "required_missing_cross_side_degree_histogram": {
                    str(value): count
                    for value, count in sorted(Counter(required_degrees.values()).items())
                },
                "vertices_with_no_balance_compatible_forced_profile": [
                    list(vertex) for vertex in empty_vertices
                ],
                "balance_completion_exists": balance_pass,
                "balance_DFS_nodes": balance_nodes,
                "balance_plus_pair_upper_completion_exists": pair_pass,
                "balance_plus_pair_DFS_nodes": pair_nodes,
                "raw_block_domain_sizes": {
                    f"{left}-{right}": raw_domain_sizes[(left, right)]
                    for left, right in sorted(raw_domain_sizes)
                },
                "pair_valid_block_domain_sizes": {
                    f"{left}-{right}": pair_domain_sizes[(left, right)]
                    for left, right in sorted(pair_domain_sizes)
                },
            }
        )

    macro_summary = []
    for macro in sorted(macro_rows, key=lambda entry: entry["state_orbit_number"]):
        number = macro["state_orbit_number"]
        stats = per_macro[number]
        macro_summary.append(
            {
                "state_macro_number": number,
                "state_indices": macro["state_indices"],
                "Q": macro["Q"],
                "macro_labelled_coverage": macro["signature_orbit_labelled_coverage"],
                **dict(stats),
                "first_balance_witness": first_balance_witness.get(number),
                "first_balance_plus_pair_witness": first_pair_witness.get(number),
            }
        )

    input_mass = sum(result["orbit_size"] for result in results)
    balance_rows = [result for result in results if result["balance_completion_exists"]]
    pair_rows = [
        result
        for result in results
        if result["balance_plus_pair_upper_completion_exists"]
    ]
    pair_q = Counter()
    for row_result in pair_rows:
        pair_q[row_result["Q"]] += row_result["orbit_size"]
    complete = limit is None
    if complete:
        assert len(results) == 8_060
        assert input_mass == 2_502_656
        assert sum(row["input_orbits"] for row in macro_summary) == 8_060
        assert sum(row["input_raw_mass"] for row in macro_summary) == 2_502_656
        assert len(per_macro) == 5

    result = {
        "status": "COMPLETE" if complete else "PARTIAL_PROBE",
        "scope": "all source133 local graph orbits against pointwise Bd=3e balance",
        "inputs": {
            str(path): sha256(path) for path in (INPUT_PATH, MACRO_PATH, THEORY_PATH)
        },
        "source_row_index": SOURCE_ROW_INDEX,
        "partition_index": 27,
        "compression_orbit_index": 0,
        "support_order": [list(support) for support in supports],
        "ordinary_support_pointwise_h": {
            str(list(support)): value for support, value in ordinary_support_h.items()
        },
        "ordinary_support_audit": {
            "h_minus_3_supports": [list(support) for support in negative],
            "h_plus_3_supports": [list(support) for support in positive],
            "h_zero_supports": [list(support) for support in zero],
            "nonzero_vertices": 16,
            "zero_ordinary_vertices": 44,
            "zero_exceptional_vertices_required": 24,
            "total_zero_vertices_required": 68,
            "forced_h_norm_squared": 144,
        },
        "summary": {
            "state_macros_checked": len(per_macro),
            "local_graph_orbits_checked": len(results),
            "input_raw_orbit_mass": input_mass,
            "balance_compatible_orbits": len(balance_rows),
            "balance_compatible_raw_mass": sum(row["orbit_size"] for row in balance_rows),
            "balance_plus_pair_upper_orbits": len(pair_rows),
            "balance_plus_pair_upper_raw_mass": sum(
                row["orbit_size"] for row in pair_rows
            ),
            "balance_plus_pair_upper_Q_histogram": {
                str(q): value for q, value in sorted(pair_q.items())
            },
            "counterexamples_to_macro_labelling_or_signed_edge_sum": 0,
            "all_positive_witnesses_rechecked_pointwise": True,
            "DFS_has_no_node_or_time_cutoff": True,
        },
        "macro_summary": macro_summary,
        "representatives": results,
        "claim_boundary": (
            "The 68-zero balance is a full-SRG necessary condition.  A local "
            "representative without a compatible completion is excluded; a "
            "passing completion is not a full-SRG construction."
        ),
    }
    atomic_json(OUTPUT_PATH, result)
    print(json.dumps({"status": result["status"], **result["summary"]}), flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    run(args.limit)


if __name__ == "__main__":
    main()
