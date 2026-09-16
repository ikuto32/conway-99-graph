"""Solver-free local fibre-port audit for all E0=77 real-bound survivors."""

from __future__ import annotations

import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path

import scratch_general_e78_port_audit as e78


INPUT_PATH = Path("scratch_general_e77_compression_audit.json")
RESULT_PATH = Path("scratch_general_e77_port_audit.json")


def single_edge_type(pair):
    return "single_side" if pair in e78.SIDES else "single_diagonal"


FIBRE_STATES = {
    1: e78.FIBRE_STATES[1],
    2: e78.FIBRE_STATES[2],
    3: tuple(
        {"edges": (pair,), "type": single_edge_type(pair)}
        for pair in e78.PAIRS
    ),
}
assert tuple(map(len, FIBRE_STATES.values())) == (4, 7, 6)


def assignment_ports(exceptional, choices):
    by_group = [[] for _ in range(7)]
    for fibre_index, (item, choice) in enumerate(zip(exceptional, choices)):
        ports = e78.fibre_ports(tuple(item["support"]), choice["edges"], fibre_index)
        assert len(ports) == 4 * item["deficit"]
        for port in ports:
            by_group[port[0]].append(port)
    return by_group


def audit_row(row):
    exceptional = row["exceptional_supports"]
    domains = [FIBRE_STATES[item["deficit"]] for item in exceptional]
    tested = 1
    for domain in domains:
        tested *= len(domain)
    feasible = 0
    type_histogram = Counter()
    first = None
    for choices in itertools.product(*domains):
        by_group = assignment_ports(exceptional, choices)
        if not all(e78.group_matchable(ports) for ports in by_group):
            continue
        feasible += 1
        types = tuple(choice["type"] for choice in choices)
        type_histogram[types] += 1
        if first is None:
            first = {
                "state_indices": [
                    domain.index(choice) for domain, choice in zip(domains, choices)
                ],
                "types": list(types),
                "port_counts_by_group": [len(ports) for ports in by_group],
                "direct_group_matching_DFS": [
                    e78.direct_matching_exists(ports) for ports in by_group
                ],
            }
            assert all(first["direct_group_matching_DFS"])
    return {
        "partition": row["partition"],
        "orbit_index": row["orbit_index"],
        "support_orbit_size": row["orbit_size"],
        "stabilizer_order": row["stabilizer_order"],
        "exceptional_supports": exceptional,
        "joint_square_budget": row["joint_off_diagonal_square_budget"],
        "overlap_relaxed_minimum_square": row["overlap"]["minimum_square"],
        "disjoint_continuous_minimum": row["disjoint_continuous_minimum"],
        "disjoint_integer": row["disjoint_integer"],
        "labelled_fibre_state_assignments": tested,
        "locally_port_feasible_assignments": feasible,
        "feasible_type_histogram": {
            "|".join(types): count for types, count in sorted(type_histogram.items())
        },
        "first_feasible": first,
    }


def main():
    source = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    rows_in = [
        row for row in source["rows"] if row["passes_overlap_and_real_relaxation"]
    ]
    assert len(rows_in) == 172
    rows = []
    for offset, row in enumerate(rows_in):
        record = audit_row(row)
        rows.append(record)
        if record["locally_port_feasible_assignments"]:
            print(json.dumps({
                "offset": offset,
                "partition": record["partition"],
                "orbit_index": record["orbit_index"],
                "feasible": record["locally_port_feasible_assignments"],
            }), flush=True)
    grouped = defaultdict(lambda: {
        "input_orbits": 0,
        "local_survivor_orbits": 0,
        "labelled_state_assignments_tested": 0,
        "local_feasible_assignments": 0,
    })
    for row in rows:
        key = "+".join(map(str, sorted(row["partition"], reverse=True)))
        grouped[key]["input_orbits"] += 1
        grouped[key]["local_survivor_orbits"] += row["locally_port_feasible_assignments"] > 0
        grouped[key]["labelled_state_assignments_tested"] += row["labelled_fibre_state_assignments"]
        grouped[key]["local_feasible_assignments"] += row["locally_port_feasible_assignments"]
    result = {
        "model": "solver-free local fibre-port audit for E0=77",
        "input": str(INPUT_PATH),
        "input_phase": source["phase"],
        "coverage": (
            "all 172 overlap+exact-real-bound support orbits and every labelled "
            "allowed same-support fibre state; no type/orientation WLOG"
        ),
        "fibre_state_counts": {
            "deficit_1_P4": 4,
            "deficit_2_two_edges": 7,
            "deficit_3_one_edge": 6,
        },
        "matching_test": (
            "exact category/Hall existence condition; the first positive assignment "
            "of every support orbit is independently checked by matching DFS"
        ),
        "input_support_orbits": len(rows),
        "local_survivor_orbits": sum(row["locally_port_feasible_assignments"] > 0 for row in rows),
        "by_partition": dict(grouped),
        "rows": rows,
    }
    RESULT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "input_support_orbits": result["input_support_orbits"],
        "local_survivor_orbits": result["local_survivor_orbits"],
        "by_partition": result["by_partition"],
    }, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
