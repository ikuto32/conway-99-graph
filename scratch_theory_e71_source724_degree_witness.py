"""Materialize a binary 84-vertex W-degree witness for source 724, Q=2.

This positive control shows exactly where the defect-rank lane stops: the
rooted macro, all fibre block totals, all port choices, vertex degrees, and
the complete equality 16 W^T W=K4 can coexist in a binary outer graph.  The
script also directly reports which stronger SRG pair equations that witness
does not satisfy.
"""

from __future__ import annotations

from collections import Counter
import hashlib
import itertools
import json
import os
from pathlib import Path

import scratch_general_e72_q3_fast_expansion as fast
import scratch_theory_e71_defect_rank_probe as defect
from scratch_general_e78_local_ports_all import forced_c4_support_bp_feasible


CATALOG = defect.CATALOG
MINING = defect.MINING
PROBE = defect.OUTPUT
OUTPUT = Path("scratch_theory_e71_source724_degree_witness.json")
SUPPORTS = defect.SUPPORTS


def atomic_json(path, value):
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def bipartite_matrix(left, right):
    left = tuple(map(int, left))
    right = tuple(map(int, right))
    assert defect.bipartite_graphical(left, right)
    chosen = []

    def visit(row, remaining):
        if row == 4:
            return not any(remaining)
        for columns in itertools.combinations(range(4), left[row]):
            next_remaining = list(remaining)
            if any(next_remaining[column] == 0 for column in columns):
                continue
            for column in columns:
                next_remaining[column] -= 1
            rows_left = 3 - row
            if any(value > rows_left for value in next_remaining):
                continue
            chosen.append(tuple(columns))
            if visit(row + 1, tuple(next_remaining)):
                return True
            chosen.pop()
        return False

    assert visit(0, right)
    return tuple((row, column) for row, columns in enumerate(chosen)
                 for column in columns)


def main():
    catalog_raw = CATALOG.read_bytes()
    mining_raw = MINING.read_bytes()
    probe_raw = PROBE.read_bytes()
    catalog = json.loads(catalog_raw)
    mining = json.loads(mining_raw)
    probe = json.loads(probe_raw)
    entry = next(entry for entry in catalog["macro_entries"]
                 if entry["signature_stabilizer_canonical"]
                 and int(entry["source_row_index"]) == 724
                 and int(entry["Q"]) == 2)
    key = defect.macro_key(entry)
    profile = next(row for row in mining["profile_rows"]["71"]
                   if defect.macro_key(row) == key)
    row = next(row for row in probe["rows"] if tuple(row["key"]) == key)
    feasible_record = row["full_rank_three_degree_CSP_census"][
        "first_by_outcome"
    ]["feasible"]
    witness = feasible_record["witness"]
    exceptional, exceptional_index, C, _C0, _Z = defect.build_compression(
        entry, profile
    )
    exceptional_set = set(exceptional)

    patterns_by_support = {
        tuple(item["source_support"]): item
        for item in row["rank_three_integer_row_patterns"]["by_source_fibre"]
    }
    selected_by_support = {
        tuple(item["support"]): item["selected_pattern_indices"]
        for item in witness["exceptional_fibres"] + witness["ordinary_fibres"]
    }
    assert set(selected_by_support) == set(SUPPORTS)
    assigned = {}
    for source, G in enumerate(SUPPORTS):
        patterns = patterns_by_support[G]["patterns"]
        selected = selected_by_support[G]
        assert len(selected) == 4
        rows = []
        for pattern_index in selected:
            pattern = patterns[pattern_index]
            degrees = []
            for target, F in enumerate(SUPPORTS):
                if F in exceptional_index:
                    degrees.append(pattern["exceptional_degrees"][exceptional_index[F]])
                else:
                    assert C[source][target] % 4 == 0
                    degrees.append(C[source][target] // 4)
            assert sum(degrees) == 12
            rows.append(tuple(degrees))
        assert all(sum(rows[vertex][target] for vertex in range(4)) == C[source][target]
                   for target in range(21))
        assigned[G] = tuple(rows)

    fast.configure_generic(fast.PRESETS["e71gram"])
    _port, grouped = fast.input_rows(fast.PRESETS["e71gram"])
    source_row = next(source for rows in grouped.values() for source, _count in rows
                      if int(source["source_row_index"]) == 724)
    geometry = fast.RowGeometry(source_row)
    oriented = fast.oriented_assignment(geometry, entry["state_indices"])
    domains = defect.exact_signature_domains(fast, geometry, oriented, entry)
    choice_indices = feasible_record["choice_indices"]
    choices = tuple(domains[group][choice_indices[group]] for group in range(7))
    local_overlap_mask = fast.internal_mask(geometry, oriented)
    for choice in choices:
        local_overlap_mask |= choice.mask
    local_overlap_graph = geometry.labelled_edges(local_overlap_mask)
    local_pair_upper = fast.generic.local79.induced_pair_upper(
        geometry.vertices, local_overlap_graph
    )
    local_forced_bp = forced_c4_support_bp_feasible(
        geometry.supports, oriented, local_overlap_graph
    )
    assert local_pair_upper and local_forced_bp

    labels_by_support = {
        support: tuple((2 * support[0] + a, 2 * support[1] + b)
                       for a, b in itertools.product((0, 1), repeat=2))
        for support in SUPPORTS
    }
    label_to_vertex = {
        label: 4 * support_index + local
        for support_index, support in enumerate(SUPPORTS)
        for local, label in enumerate(labels_by_support[support])
    }
    vertex_labels = [labels_by_support[support][local]
                     for support in SUPPORTS for local in range(4)]
    edges = set()

    def add(left, right):
        assert left != right
        edge = tuple(sorted((left, right)))
        assert edge not in edges
        edges.add(edge)

    # Fixed exceptional internal states.
    for left, right in entry["internal_edges"]:
        add(label_to_vertex[tuple(left)], label_to_vertex[tuple(right)])
    # Every ordinary internal fibre is a C4; its orientation is immaterial to W.
    for support_index, support in enumerate(SUPPORTS):
        if support in exceptional_set:
            continue
        vertices = [4 * support_index + local for local in range(4)]
        for left, right in ((0, 1), (1, 3), (3, 2), (2, 0)):
            add(vertices[left], vertices[right])
    # Exact selected port matchings among exceptional fibres.
    for choice in choices:
        for left, right in choice.edges:
            add(label_to_vertex[geometry.vertices[left]],
                label_to_vertex[geometry.vertices[right]])

    # All remaining nonzero cross blocks are disjoint-support bipartite blocks.
    for left_index, right_index in itertools.combinations(range(21), 2):
        G, F = SUPPORTS[left_index], SUPPORTS[right_index]
        if set(G) & set(F):
            assert C[left_index][right_index] == (
                0 if G not in exceptional_set or F not in exceptional_set
                else C[left_index][right_index]
            )
            continue
        left_degrees = tuple(assigned[G][local][right_index] for local in range(4))
        right_degrees = tuple(assigned[F][local][left_index] for local in range(4))
        assert sum(left_degrees) == sum(right_degrees) == C[left_index][right_index]
        for left_local, right_local in bipartite_matrix(left_degrees, right_degrees):
            add(4 * left_index + left_local, 4 * right_index + right_local)

    adjacency = [0] * 84
    for left, right in edges:
        adjacency[left] |= 1 << right
        adjacency[right] |= 1 << left
    degrees = [mask.bit_count() for mask in adjacency]
    assert degrees == [12] * 84
    actual_C = [[0] * 21 for _ in range(21)]
    for left, right in edges:
        G, F = left // 4, right // 4
        if G == F:
            actual_C[G][G] += 2
        else:
            actual_C[G][F] += 1
            actual_C[F][G] += 1
    assert actual_C == C

    R = [[0] * 21 for _ in range(84)]
    for vertex in range(84):
        source = vertex // 4
        for target in range(21):
            block_degree = sum((adjacency[vertex] >> other) & 1
                               for other in range(4 * target, 4 * target + 4))
            R[vertex][target] = 4 * block_degree - C[source][target]
    RtR = defect.matmul(defect.transpose(R), R)
    K4 = row["K4"]
    assert all(RtR[i][j] == 4 * K4[i][j]
               for i in range(21) for j in range(21))

    residual_histogram = Counter()
    positive_violations = []
    for left, right in itertools.combinations(range(84), 2):
        adjacent = (adjacency[left] >> right) & 1
        common_outer = (adjacency[left] & adjacency[right]).bit_count()
        root_overlap = len(set(vertex_labels[left]) & set(vertex_labels[right]))
        target = 2 - root_overlap
        residual = adjacent + common_outer - target
        residual_histogram[residual] += 1
        if residual > 0 and len(positive_violations) < 20:
            positive_violations.append({
                "vertices": [left, right],
                "supports": [list(SUPPORTS[left // 4]), list(SUPPORTS[right // 4])],
                "adjacent": adjacent,
                "common_outer": common_outer,
                "root_overlap": root_overlap,
                "excess": residual,
            })

    result = {
        "status": "EXACT_BINARY_SOURCE724_W_DEGREE_WITNESS_VERIFIED",
        "inputs": {
            str(CATALOG): hashlib.sha256(catalog_raw).hexdigest().upper(),
            str(MINING): hashlib.sha256(mining_raw).hexdigest().upper(),
            str(PROBE): hashlib.sha256(probe_raw).hexdigest().upper(),
        },
        "macro_key": list(key),
        "Q": int(entry["Q"]),
        "coverage_of_macro": int(entry["signature_orbit_labelled_coverage"]),
        "selected_group_choice_indices": choice_indices,
        "outer_vertices": 84,
        "outer_edges": len(edges),
        "all_outer_degrees": 12,
        "compression_C_verified": True,
        "binary_internal_and_port_edges_verified": True,
        "materialized_exceptional_local_pair_upper_verified": local_pair_upper,
        "materialized_exceptional_forced_C4_BP_verified": local_forced_bp,
        "full_defect_Gram_verified": "R^T R=4K4, equivalently 16W^TW=K4",
        "edge_list_zero_based": [list(edge) for edge in sorted(edges)],
        "SRG_pair_equation_residual_histogram": {
            str(value): count for value, count in sorted(residual_histogram.items())
        },
        "positive_pair_upper_violations": sum(
            count for value, count in residual_histogram.items() if value > 0
        ),
        "first_positive_pair_upper_violations": positive_violations,
        "conclusion": (
            "The W/K4 rank, integrality, full block totals, and binary port "
            "conditions alone do not exclude the E0=71,Q=2 source724 macro. "
            "Stronger pair/common-neighbour or cross-root compatibility is required."
        ),
    }
    assert len(edges) == 504
    assert result["positive_pair_upper_violations"] > 0
    atomic_json(OUTPUT, result)
    print(json.dumps({
        "path": str(OUTPUT),
        "status": result["status"],
        "outer_edges": len(edges),
        "positive_pair_upper_violations": result["positive_pair_upper_violations"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
