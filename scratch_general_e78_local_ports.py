"""Bounded P4 endpoint-port audit for the all-P4 E0=78 branch.

The compression audit has a (1,1,1,1,1,1) branch: six exceptional fibres,
each an induced P4.  For each surviving support orbit this script enumerates
all 4^6 P4 orientations.  It checks, group by group, whether the missing
root/inner BP symbol quotas can be paired by overlap edges.  Groups are
independent at this stage, so the product of their perfect-matching counts is
the exact number of overlap-edge completions.  No SAT solver is used.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path

import scratch_general_e79_local_audit as local79


INPUT = Path("scratch_general_e78_local_compression.json")
OUTPUT = Path("scratch_general_e78_local_ports.json")


def matching_count_for_group(supports, oriented, group):
    incident = [index for index, support in enumerate(supports) if group in support]
    if not incident:
        return 1
    stubs = []
    for index in incident:
        for vertex in oriented[index]["endpoints"]:
            stubs.append((vertex, index))
    adjacency = {stub: [] for stub in stubs}
    for left, right in itertools.combinations(stubs, 2):
        u, i = left
        v, j = right
        if i == j:
            continue
        if oriented[i]["needs"][u][group] != local79.sign_at(v, group):
            continue
        if oriented[j]["needs"][v][group] != local79.sign_at(u, group):
            continue
        adjacency[left].append(right)
        adjacency[right].append(left)

    memo = {}

    def count(remaining):
        remaining = frozenset(remaining)
        if not remaining:
            return 1
        if remaining in memo:
            return memo[remaining]
        u = min(remaining)
        answer = sum(
            count(remaining - {u, v})
            for v in adjacency[u]
            if v in remaining
        )
        memo[remaining] = answer
        return answer

    return count(stubs)


def audit_supports(supports):
    feasible_internal_graphs = []
    orientation_count = 0
    overlap_completion_count = 0
    matching_product_histogram = {}
    for missing in itertools.product(range(4), repeat=6):
        oriented = tuple(
            local79.orientation_data(support, choice)
            for support, choice in zip(supports, missing)
        )
        counts = tuple(
            matching_count_for_group(supports, oriented, group)
            for group in local79.GROUPS
        )
        product = 1
        for value in counts:
            product *= value
        if not product:
            continue
        orientation_count += 1
        overlap_completion_count += product
        matching_product_histogram[str(product)] = matching_product_histogram.get(str(product), 0) + 1
        feasible_internal_graphs.append(
            frozenset(edge for data in oriented for edge in data["internal"])
        )
    orbit_count, action_count = local79.canonical_masks(supports, feasible_internal_graphs)
    return {
        "orientations_tested": 4 ** 6,
        "port_feasible_orientations": orientation_count,
        "port_feasible_orientation_orbits": orbit_count,
        "exact_overlap_edge_completions": overlap_completion_count,
        "matching_product_histogram": matching_product_histogram,
        "distinct_local_symmetry_actions": action_count,
    }


def main():
    compression = json.loads(INPUT.read_text(encoding="utf-8"))
    source_rows = [
        row for row in compression["rows"]
        if tuple(row["partition"]) == (1, 1, 1, 1, 1, 1)
        and row["status"] == "SURVIVES_REAL_DISJOINT_LOWER_BOUND"
    ]
    assert len(source_rows) == 34
    rows = []
    for offset, source in enumerate(source_rows):
        supports = tuple(tuple(item["support"]) for item in source["exceptional_supports"])
        audit = audit_supports(supports)
        record = {
            "compression_orbit_index": source["orbit_index"],
            "orbit_size": source["orbit_size"],
            "stabilizer_order": source["stabilizer_order"],
            "supports": supports,
            "group_degree_sequence": source["support_graph"]["degree_sequence_on_seven_groups"],
            "overlap_minimum_square": source["overlap"]["minimum_square"],
            **audit,
        }
        rows.append(record)
        print(json.dumps({"offset": offset, **record}, sort_keys=True), flush=True)
    result = {
        "model": "solver-free P4 endpoint-port audit for E0=78 partition 1^6",
        "input_compression_orbits": len(rows),
        "port_feasible_support_orbits": sum(row["port_feasible_orientations"] > 0 for row in rows),
        "port_infeasible_support_orbits": sum(row["port_feasible_orientations"] == 0 for row in rows),
        "port_feasible_labelled_support_sets": sum(
            row["orbit_size"] for row in rows if row["port_feasible_orientations"] > 0
        ),
        "total_port_feasible_orientations_on_representatives": sum(
            row["port_feasible_orientations"] for row in rows
        ),
        "total_orientation_orbits_within_support_stabilizers": sum(
            row["port_feasible_orientation_orbits"] for row in rows
        ),
        "rows": rows,
        "claim_boundary": (
            "This is an exact bounded port-feasibility calculation only.  It does not "
            "enforce disjoint blocks, common-neighbour equations, or integral spectral lifts."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in result if key not in ("rows", "claim_boundary", "model")}, indent=2))


if __name__ == "__main__":
    main()
