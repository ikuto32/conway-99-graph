"""Generic solver-free fibre-port audit for all E0=78 compression survivors.

After the compression/spectral lower-bound audit only the deficit partitions
2+2+1+1, 2+1+1+1+1 and 1^6 survive.  A deficit-one fibre is a P4 (four
labelled orientations).  A deficit-two fibre has exactly seven labelled
possibilities: any two sides of the coordinate square, or both diagonals.

For every support orbit and every labelled fibre-shape assignment, this file
constructs the missing root/inner BP symbol ports and counts their simple
overlap-edge perfect matchings group by group.  It uses no SAT solver and no
disjoint-support or common-neighbour constraints.
"""

from __future__ import annotations

from collections import Counter
import itertools
import json
from pathlib import Path

import scratch_general_e79_local_audit as local79


INPUT = Path("scratch_general_e78_local_compression.json")
OUTPUT = Path("scratch_general_e78_local_ports_all.json")


def fibre_variants(support, deficit):
    bit_rows = tuple(itertools.product((0, 1), repeat=2))
    vertices = tuple(local79.vertex_label(support, bits) for bits in bit_rows)
    sides = tuple(
        (u, v)
        for u, v in itertools.combinations(range(4), 2)
        if sum(bit_rows[u][axis] != bit_rows[v][axis] for axis in (0, 1)) == 1
    )
    diagonals = tuple(
        (u, v)
        for u, v in itertools.combinations(range(4), 2)
        if sum(bit_rows[u][axis] != bit_rows[v][axis] for axis in (0, 1)) == 2
    )
    if deficit == 1:
        edge_index_sets = tuple(
            tuple(index for index in range(4) if index != missing)
            for missing in range(4)
        )
        raw_edges = tuple(tuple(sides[index] for index in indices) for indices in edge_index_sets)
    elif deficit == 2:
        raw_edges = tuple(itertools.combinations(sides, 2)) + (diagonals,)
    else:
        raise ValueError(f"unsupported deficit {deficit}")

    answer = []
    for chosen in raw_edges:
        internal = frozenset(
            tuple(sorted((vertices[u], vertices[v])))
            for u, v in chosen
        )
        neighbours = local79.neighbour_sets(vertices, internal)
        ports = []
        for vertex in vertices:
            for group in support:
                counts = Counter(
                    symbol % 2
                    for other in neighbours[vertex]
                    for symbol in other
                    if symbol // 2 == group
                )
                assert all(counts[sign] <= 1 for sign in (0, 1))
                for sign in (0, 1):
                    if counts[sign] == 0:
                        ports.append((vertex, group, sign))
        assert len(ports) == 4 * deficit
        answer.append({
            "vertices": vertices,
            "internal": internal,
            "ports": tuple(ports),
        })
    assert len(answer) == (4 if deficit == 1 else 7)
    assert len({row["internal"] for row in answer}) == len(answer)
    return tuple(answer)


def group_matchings(oriented, group):
    stubs = []
    for fibre_index, data in enumerate(oriented):
        for vertex, port_group, needed_sign in data["ports"]:
            if port_group == group:
                stubs.append((vertex, fibre_index, needed_sign))
    if not stubs:
        return (frozenset(),)
    candidates = {stub: [] for stub in stubs}
    for left, right in itertools.combinations(stubs, 2):
        u, i, need_u = left
        v, j, need_v = right
        if i == j:
            continue
        if need_u != local79.sign_at(v, group):
            continue
        if need_v != local79.sign_at(u, group):
            continue
        candidates[left].append(right)
        candidates[right].append(left)

    def visit(remaining, used_vertex_edges, selected):
        remaining = frozenset(remaining)
        used_vertex_edges = frozenset(used_vertex_edges)
        if not remaining:
            yield frozenset(selected)
            return
        u = min(remaining, key=lambda stub: sum(v in remaining for v in candidates[stub]))
        for v in candidates[u]:
            if v not in remaining:
                continue
            vertex_edge = tuple(sorted((u[0], v[0])))
            if vertex_edge in used_vertex_edges:
                continue
            yield from visit(
                remaining - {u, v},
                used_vertex_edges | {vertex_edge},
                selected + (vertex_edge,),
            )

    return tuple(visit(stubs, frozenset(), ()))


def forced_c4_support_bp_feasible(supports, oriented, graph):
    """Necessary support-count completion for exceptional disjoint blocks."""
    support_of = {
        vertex: support
        for support, data in zip(supports, oriented)
        for vertex in data["vertices"]
    }
    neighbours = local79.neighbour_sets(tuple(support_of), graph)
    internal_edges = frozenset(edge for data in oriented for edge in data["internal"])
    for fibre_index, (support, data) in enumerate(zip(supports, oriented)):
        disjoint = [
            index for index, other in enumerate(supports)
            if not set(support) & set(other)
        ]
        r = len(disjoint)
        for vertex in data["vertices"]:
            a = sum(tuple(sorted((vertex, other))) in internal_edges for other in data["vertices"] if other != vertex)
            s = sum(bool(set(support) & set(support_of[other])) for other in neighbours[vertex] if support_of[other] != support)
            assert 2 * a + s == 4
            required_degree = r + a - 2
            if required_degree < 0:
                return False
            external_groups = [group for group in local79.GROUPS if group not in support]
            wanted = {}
            for group in external_groups:
                t = sum(group in supports[index] for index in disjoint)
                o = sum(
                    group in support_of[other]
                    for other in neighbours[vertex]
                    if bool(set(support) & set(support_of[other]))
                )
                wanted[group] = t - o
                if wanted[group] < 0:
                    return False
            found = False
            for values in itertools.product(range(5), repeat=r):
                if sum(values) != required_degree:
                    continue
                if all(
                    sum(value for value, index in zip(values, disjoint) if group in supports[index]) == wanted[group]
                    for group in external_groups
                ):
                    found = True
                    break
            if not found:
                return False
    return True


def audit_row(source):
    supports = tuple(tuple(item["support"]) for item in source["exceptional_supports"])
    deficits = tuple(item["deficit"] for item in source["exceptional_supports"])
    choices = tuple(fibre_variants(support, deficit) for support, deficit in zip(supports, deficits))
    tested = 1
    for rows in choices:
        tested *= len(rows)
    feasible_internal = []
    overlap_graphs = []
    spectral_graphs = []
    pair_upper_graphs = []
    forced_c4_bp_graphs = []
    exact_overlap_completions = 0
    completion_histogram = Counter()
    actual_overlap_square_histogram = Counter()
    for oriented in itertools.product(*choices):
        matchings_by_group = []
        product = 1
        for group in local79.GROUPS:
            matches = group_matchings(oriented, group)
            matchings_by_group.append(matches)
            product *= len(matches)
            if not product:
                break
        if not product:
            continue
        internal = frozenset(edge for data in oriented for edge in data["internal"])
        feasible_internal.append(internal)
        exact_overlap_completions += product
        completion_histogram[product] += 1
        vertices = tuple(vertex for data in oriented for vertex in data["vertices"])
        for selected in itertools.product(*matchings_by_group):
            overlap = frozenset(edge for group_edges in selected for edge in group_edges)
            assert len(overlap) == 12
            graph = internal | overlap
            overlap_graphs.append(graph)
            fibre_of = {
                vertex: index
                for index, data in enumerate(oriented)
                for vertex in data["vertices"]
            }
            block_counts = Counter(
                tuple(sorted((fibre_of[u], fibre_of[v])))
                for u, v in overlap
            )
            actual_m2 = sum(value * value for value in block_counts.values())
            actual_overlap_square_histogram[actual_m2] += 1
            if actual_m2 + source["disjoint_integer_square_lower_bound"] > source["joint_square_budget"]:
                continue
            spectral_graphs.append(graph)
            if local79.induced_pair_upper(vertices, graph):
                pair_upper_graphs.append(graph)
                if forced_c4_support_bp_feasible(supports, oriented, graph):
                    forced_c4_bp_graphs.append(graph)
    if feasible_internal:
        shape_orbits, action_count = local79.canonical_masks(supports, feasible_internal)
    else:
        shape_orbits, action_count = 0, None
    if pair_upper_graphs:
        pair_upper_orbits, _ = local79.canonical_masks(supports, pair_upper_graphs)
    else:
        pair_upper_orbits = 0
    if forced_c4_bp_graphs:
        forced_c4_bp_orbits, _ = local79.canonical_masks(supports, forced_c4_bp_graphs)
    else:
        forced_c4_bp_orbits = 0
    if spectral_graphs:
        spectral_orbits, _ = local79.canonical_masks(supports, spectral_graphs)
    else:
        spectral_orbits = 0
    return {
        "compression_orbit_index": source["orbit_index"],
        "partition": deficits,
        "orbit_size": source["orbit_size"],
        "stabilizer_order": source["stabilizer_order"],
        "supports": supports,
        "group_degree_sequence": source["support_graph"]["degree_sequence_on_seven_groups"],
        "overlap_minimum_square": source["overlap"]["minimum_square"],
        "shape_assignments_tested": tested,
        "port_feasible_shape_assignments": len(feasible_internal),
        "port_feasible_shape_orbits": shape_orbits,
        "exact_overlap_edge_completions": exact_overlap_completions,
        "overlap_graphs_enumerated": len(overlap_graphs),
        "actual_overlap_square_histogram": {str(key): value for key, value in sorted(actual_overlap_square_histogram.items())},
        "after_actual_spectral_overlap_bound": len(spectral_graphs),
        "after_actual_spectral_overlap_bound_orbits": spectral_orbits,
        "after_induced_pair_upper": len(pair_upper_graphs),
        "after_induced_pair_upper_orbits": pair_upper_orbits,
        "after_forced_C4_support_BP": len(forced_c4_bp_graphs),
        "after_forced_C4_support_BP_orbits": forced_c4_bp_orbits,
        "completion_count_histogram": {str(key): value for key, value in sorted(completion_histogram.items())},
        "distinct_local_symmetry_actions": action_count,
    }


def main():
    compression = json.loads(INPUT.read_text(encoding="utf-8"))
    source_rows = [
        row for row in compression["rows"]
        if row["status"] == "SURVIVES_REAL_DISJOINT_LOWER_BOUND"
    ]
    assert len(source_rows) == 67
    rows = []
    for offset, source in enumerate(source_rows):
        record = audit_row(source)
        rows.append(record)
        print(json.dumps({"offset": offset, **record}, sort_keys=True), flush=True)
    by_partition = {}
    for partition in ((2, 2, 1, 1), (2, 1, 1, 1, 1), (1, 1, 1, 1, 1, 1)):
        selected = [row for row in rows if tuple(sorted(row["partition"], reverse=True)) == partition]
        by_partition["+".join(map(str, partition))] = {
            "input_support_orbits": len(selected),
            "port_feasible_support_orbits": sum(row["port_feasible_shape_assignments"] > 0 for row in selected),
            "port_feasible_labelled_support_sets": sum(
                row["orbit_size"] for row in selected if row["port_feasible_shape_assignments"] > 0
            ),
            "port_feasible_shape_assignments_on_representatives": sum(
                row["port_feasible_shape_assignments"] for row in selected
            ),
            "port_feasible_shape_orbits_within_support_stabilizers": sum(
                row["port_feasible_shape_orbits"] for row in selected
            ),
        }
    result = {
        "model": "generic solver-free E0=78 exceptional-fibre port audit",
        "input_compression_orbits": len(rows),
        "port_feasible_support_orbits": sum(row["port_feasible_shape_assignments"] > 0 for row in rows),
        "by_partition": by_partition,
        "rows": rows,
        "claim_boundary": (
            "Only exact own-support BP ports and overlap edges are enforced.  Disjoint blocks, "
            "symbol quotas outside each fibre support, and common-neighbour equations remain."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "input_compression_orbits": result["input_compression_orbits"],
        "port_feasible_support_orbits": result["port_feasible_support_orbits"],
        "by_partition": by_partition,
    }, indent=2))


if __name__ == "__main__":
    main()
