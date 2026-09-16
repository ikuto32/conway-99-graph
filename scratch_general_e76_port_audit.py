"""Solver-free weighted-port and labelled fibre-state audit for E0=76."""

from __future__ import annotations

import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path

import scratch_general_e77_port_audit as e77
import scratch_general_e78_port_audit as e78


INPUT_PATH = Path("scratch_general_e76_compression_audit.json")
RESULT_PATH = Path("scratch_general_e76_port_audit.json")
FIBRE_STATES = dict(e77.FIBRE_STATES)
FIBRE_STATES[4] = ({"edges": (), "type": "empty"},)
assert tuple(len(FIBRE_STATES[q]) for q in range(1, 5)) == (4, 7, 6, 1)


def weighted_port_balance(exceptional):
    """Necessary no-within-fibre matching capacity at all seven groups."""
    details = []
    for group in range(7):
        incident = [
            item["deficit"] for item in exceptional if group in item["support"]
        ]
        if not incident:
            continue
        total = sum(incident)
        maximum = max(incident)
        details.append({
            "group": group,
            "incident_deficits": incident,
            "balanced": 2 * maximum <= total,
        })
        if 2 * maximum > total:
            return False, details
    return True, details


def assignment_ports(exceptional, choices):
    by_group = [[] for _ in range(7)]
    for fibre_index, (item, choice) in enumerate(zip(exceptional, choices)):
        ports = e78.fibre_ports(tuple(item["support"]), choice["edges"], fibre_index)
        assert len(ports) == 4 * item["deficit"]
        per_group = Counter(port[0] for port in ports)
        assert all(per_group[group] == 2 * item["deficit"] for group in item["support"])
        for port in ports:
            by_group[port[0]].append(port)
    return by_group


def audit_row(row):
    exceptional = row["exceptional_supports"]
    balanced, balance_details = weighted_port_balance(exceptional)
    if not balanced:
        return {
            "partition": row["partition"],
            "orbit_index": row["orbit_index"],
            "support_orbit_size": row["orbit_size"],
            "exceptional_supports": exceptional,
            "weighted_port_balance": False,
            "first_balance_obstruction": next(
                item for item in balance_details if not item["balanced"]
            ),
            "labelled_fibre_state_assignments": 0,
            "locally_port_feasible_assignments": 0,
        }
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
            direct = [e78.direct_matching_exists(ports) for ports in by_group]
            assert all(direct)
            first = {
                "state_indices": [
                    domain.index(choice) for domain, choice in zip(domains, choices)
                ],
                "types": list(types),
                "port_counts_by_group": [len(ports) for ports in by_group],
                "direct_group_matching_DFS": direct,
            }
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
        "weighted_port_balance": True,
        "labelled_fibre_state_assignments": tested,
        "locally_port_feasible_assignments": feasible,
        "feasible_type_histogram": {
            "|".join(types): count for types, count in sorted(type_histogram.items())
        },
        "first_feasible": first,
    }


def main():
    source = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    input_rows = [
        row for row in source["rows"] if row["passes_overlap_and_real_relaxation"]
    ]
    assert len(input_rows) == 639
    rows = []
    for offset, row in enumerate(input_rows):
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
        "weighted_balance_orbits": 0,
        "state_assignments_checked": 0,
        "local_survivor_orbits": 0,
        "local_feasible_assignments": 0,
    })
    for row in rows:
        key = "+".join(map(str, sorted(row["partition"], reverse=True)))
        grouped[key]["input_orbits"] += 1
        grouped[key]["weighted_balance_orbits"] += row["weighted_port_balance"]
        grouped[key]["state_assignments_checked"] += row["labelled_fibre_state_assignments"]
        grouped[key]["local_survivor_orbits"] += row["locally_port_feasible_assignments"] > 0
        grouped[key]["local_feasible_assignments"] += row["locally_port_feasible_assignments"]
    result = {
        "model": "solver-free weighted and labelled local port audit for E0=76",
        "input": str(INPUT_PATH),
        "coverage": (
            "all 639 overlap+exact-real-bound support orbits; weighted balance is "
            "analytic; every labelled allowed fibre state is checked on the 36 survivors"
        ),
        "weighted_balance_lemma": (
            "a deficit-d fibre contributes exactly 2d ports at each endpoint group; "
            "ports cannot pair within a fibre, so max incident d <= sum of the others"
        ),
        "fibre_state_counts": {str(q): len(FIBRE_STATES[q]) for q in range(1, 5)},
        "input_support_orbits": len(rows),
        "weighted_balance_support_orbits": sum(row["weighted_port_balance"] for row in rows),
        "local_survivor_orbits": sum(row["locally_port_feasible_assignments"] > 0 for row in rows),
        "by_partition": dict(grouped),
        "rows": rows,
    }
    assert result["weighted_balance_support_orbits"] == 36
    RESULT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "input_support_orbits": result["input_support_orbits"],
        "weighted_balance_support_orbits": result["weighted_balance_support_orbits"],
        "local_survivor_orbits": result["local_survivor_orbits"],
        "by_partition": result["by_partition"],
    }, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
