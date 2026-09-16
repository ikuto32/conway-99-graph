"""Checkpointed exhaustive labelled fibre-state port audit for E0=75."""

from __future__ import annotations

import argparse
import itertools
import json
import os
from collections import Counter, defaultdict
from pathlib import Path

import scratch_general_e77_port_audit as e77
import scratch_general_e78_port_audit as e78


INPUT_PATH = Path("scratch_general_e75_compression_audit.json")
OUTPUT_PATH = Path("scratch_general_e75_port_audit.json")
FIBRE_STATES = e77.FIBRE_STATES
assert tuple(len(FIBRE_STATES[d]) for d in (1, 2, 3)) == (4, 7, 6)


def part_path(partition_index):
    return Path(f"scratch_general_e75_port_part_{partition_index:02d}.json")


def atomic_json(path, value):
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def state_signature(deficit, state_index, axis):
    state = FIBRE_STATES[deficit][state_index]
    ports = e78.fibre_ports((0, 1), state["edges"], 0)
    counts = Counter(
        (sigma, required)
        for group, _fibre, _vertex, sigma, required in ports
        if group == axis
    )
    signature = tuple(
        counts[category] for category in ((0, 0), (0, 1), (1, 0), (1, 1))
    )
    assert sum(signature) == 2 * deficit
    return signature


SIGNATURES = {
    deficit: tuple(
        tuple(state_signature(deficit, state_index, axis) for axis in (0, 1))
        for state_index in range(len(FIBRE_STATES[deficit]))
    )
    for deficit in (1, 2, 3)
}


def group_matchable_signatures(rows):
    """Exact Hall test from per-fibre (sigma,required) multiplicities."""
    if not rows:
        return True
    totals = tuple(sum(row[q] for row in rows) for q in range(4))
    # Same categories (0,0) and (1,1) are complete multipartite matchings.
    if totals[0] % 2 or 2 * max(row[0] for row in rows) > totals[0]:
        return False
    if totals[3] % 2 or 2 * max(row[3] for row in rows) > totals[3]:
        return False
    # Cross categories (0,1) and (1,0) form a bipartite graph with only the
    # same-fibre diagonal blocks forbidden.
    if totals[1] != totals[2]:
        return False
    return all(row[1] <= totals[2] - row[2] for row in rows)


def assignment_order(supports, deficits):
    """Greedily close low-degree group constraints early."""
    incident = {
        group: {index for index, support in enumerate(supports) if group in support}
        for group in range(7)
    }
    remaining = set(range(len(supports)))
    assigned = set()
    order = []
    while remaining:
        def score(index):
            endpoints = supports[index]
            closes = sum((incident[g] - {index}) <= assigned for g in endpoints)
            progress = sum(
                len(incident[g] & assigned) / len(incident[g]) for g in endpoints
            )
            return (
                closes,
                progress,
                -len(FIBRE_STATES[deficits[index]]),
                -index,
            )

        chosen = max(remaining, key=score)
        order.append(chosen)
        assigned.add(chosen)
        remaining.remove(chosen)
    assert sorted(order) == list(range(len(supports)))
    return tuple(order)


def direct_check_first(exceptional, assignment):
    choices = tuple(
        FIBRE_STATES[item["deficit"]][state_index]
        for item, state_index in zip(exceptional, assignment)
    )
    by_group = e77.assignment_ports(exceptional, choices)
    closed = [e78.group_matchable(ports) for ports in by_group]
    direct = [e78.direct_matching_exists(ports) for ports in by_group]
    assert closed == direct
    assert all(closed)
    return {
        "state_indices": list(assignment),
        "types": [choice["type"] for choice in choices],
        "port_counts_by_group": [len(ports) for ports in by_group],
        "closed_Hall_test": closed,
        "direct_matching_DFS": direct,
    }


def audit_row(source):
    exceptional = source["exceptional_supports"]
    supports = tuple(tuple(item["support"]) for item in exceptional)
    deficits = tuple(item["deficit"] for item in exceptional)
    domains = tuple(range(len(FIBRE_STATES[deficit])) for deficit in deficits)
    total = math_product(len(domain) for domain in domains)
    order = assignment_order(supports, deficits)
    position = {variable: q for q, variable in enumerate(order)}
    incident = {
        group: tuple(index for index, support in enumerate(supports) if group in support)
        for group in range(7)
    }
    closing = defaultdict(list)
    for group, variables in incident.items():
        if variables:
            closing[max(position[index] for index in variables)].append(group)
    suffix = [1] * (len(order) + 1)
    for q in range(len(order) - 1, -1, -1):
        suffix[q] = suffix[q + 1] * len(domains[order[q]])
    assignment = [-1] * len(supports)
    feasible = []
    pruned_assignments = 0
    tested_partial_nodes = 0

    def signature_for(index, group):
        axis = supports[index].index(group)
        return SIGNATURES[deficits[index]][assignment[index]][axis]

    def visit(depth):
        nonlocal pruned_assignments, tested_partial_nodes
        if depth == len(order):
            feasible.append(tuple(assignment))
            return
        variable = order[depth]
        for state_index in domains[variable]:
            tested_partial_nodes += 1
            assignment[variable] = state_index
            valid = True
            for group in closing[depth]:
                rows = tuple(signature_for(index, group) for index in incident[group])
                if not group_matchable_signatures(rows):
                    valid = False
                    break
            if valid:
                visit(depth + 1)
            else:
                pruned_assignments += suffix[depth + 1]
            assignment[variable] = -1

    visit(0)
    assert len(feasible) + pruned_assignments == total
    type_histogram = Counter(
        tuple(
            FIBRE_STATES[deficit][state_index]["type"]
            for deficit, state_index in zip(deficits, assignment_row)
        )
        for assignment_row in feasible
    )
    first = direct_check_first(exceptional, feasible[0]) if feasible else None
    return {
        "partition": source["partition"],
        "compression_orbit_index": source["orbit_index"],
        "support_orbit_size": source["orbit_size"],
        "weighted_stabilizer_order": source["weighted_stabilizer_order"],
        "exceptional_supports": exceptional,
        "joint_square_budget": source["joint_off_diagonal_square_budget"],
        "overlap_relaxed_minimum_square": source["overlap"]["minimum_square"],
        "disjoint_continuous_minimum": source["disjoint_continuous_minimum"],
        "labelled_fibre_state_assignments_covered": total,
        "partial_assignment_nodes_tested": tested_partial_nodes,
        "assignments_pruned_in_subtrees": pruned_assignments,
        "assignment_order": list(order),
        "locally_port_feasible_assignments": len(feasible),
        "feasible_type_histogram": {
            "|".join(types): count for types, count in sorted(type_histogram.items())
        },
        "first_feasible_direct_control": first,
        "feasible_state_indices": [list(row) for row in feasible],
    }


def math_product(values):
    answer = 1
    for value in values:
        answer *= value
    return answer


def source_rows_by_partition():
    source = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    assert source["status"] == "COMPLETE"
    rows = [
        row
        for row in source["rows"]
        if row["passes_weighted_port_overlap_and_real_relaxation"]
    ]
    assert len(rows) == 96
    answer = defaultdict(list)
    partition_to_index = {
        tuple(row["partition"]): row["partition_index"]
        for row in source["by_partition"]
    }
    for row in rows:
        answer[partition_to_index[tuple(row["partition"])]].append(row)
    return source, answer


def summarize(rows):
    return {
        "input_support_orbits": len(rows),
        "labelled_fibre_state_assignments_covered": sum(
            row["labelled_fibre_state_assignments_covered"] for row in rows
        ),
        "locally_port_feasible_support_orbits": sum(
            row["locally_port_feasible_assignments"] > 0 for row in rows
        ),
        "locally_port_feasible_assignments": sum(
            row["locally_port_feasible_assignments"] for row in rows
        ),
    }


def run_partition(partition_index, force=False):
    _source, grouped = source_rows_by_partition()
    rows_in = grouped.get(partition_index, [])
    path = part_path(partition_index)
    if path.exists() and not force:
        result = json.loads(path.read_text(encoding="utf-8"))
        if result["status"] == "COMPLETE":
            print(json.dumps({"phase": "resume", "partition_index": partition_index, "status": "COMPLETE"}), flush=True)
            return result
        completed_keys = {
            row["compression_orbit_index"] for row in result["rows"]
        }
    else:
        result = {
            "status": "ENUMERATING",
            "model": "checkpointed exhaustive labelled E0=75 fibre-state port audit",
            "partition_index": partition_index,
            "partition": rows_in[0]["partition"] if rows_in else None,
            "input_support_orbits": len(rows_in),
            "coverage": (
                "every labelled allowed fibre state; partial DFS prunes a subtree "
                "only after a complete root-group Hall constraint fails"
            ),
            "rows": [],
        }
        completed_keys = set()
        atomic_json(path, result)
    for offset, source_row in enumerate(rows_in):
        if source_row["orbit_index"] in completed_keys:
            continue
        record = audit_row(source_row)
        result["rows"].append(record)
        result["summary"] = summarize(result["rows"])
        atomic_json(path, result)
        print(
            json.dumps(
                {
                    "phase": "row",
                    "partition_index": partition_index,
                    "offset": offset,
                    "compression_orbit_index": source_row["orbit_index"],
                    "covered": record["labelled_fibre_state_assignments_covered"],
                    "feasible": record["locally_port_feasible_assignments"],
                    "partial_nodes": record["partial_assignment_nodes_tested"],
                }
            ),
            flush=True,
        )
    assert len(result["rows"]) == len(rows_in)
    result["status"] = "COMPLETE"
    result["summary"] = summarize(result["rows"])
    atomic_json(path, result)
    return result


def merge():
    source, grouped = source_rows_by_partition()
    parts = []
    for partition_index in sorted(grouped):
        path = part_path(partition_index)
        if not path.exists():
            raise RuntimeError(f"missing {path}")
        result = json.loads(path.read_text(encoding="utf-8"))
        if result["status"] != "COMPLETE":
            raise RuntimeError(f"incomplete {path}: {result['status']}")
        parts.append(result)
    rows = [row for part in parts for row in part["rows"]]
    result = {
        "status": "COMPLETE",
        "model": "merged exhaustive labelled E0=75 fibre-state port audit",
        "input": str(INPUT_PATH),
        "input_support_orbits": 96,
        "fibre_state_counts": {"deficit_1": 4, "deficit_2": 7, "deficit_3": 6},
        "matching_test": (
            "exact category/Hall condition at each root group; first positive "
            "assignment of every row independently checked by direct matching DFS"
        ),
        "coverage": (
            "all labelled state assignments; no type, orientation, or symmetry WLOG; "
            "subtree counts certify full Cartesian-product coverage"
        ),
        "summary": summarize(rows),
        "by_partition": [
            {
                "partition_index": part["partition_index"],
                "partition": part["partition"],
                **part["summary"],
                "artifact": str(part_path(part["partition_index"])),
            }
            for part in parts
        ],
        "rows": rows,
    }
    assert result["summary"]["input_support_orbits"] == 96
    atomic_json(OUTPUT_PATH, result)
    print(json.dumps({"status": result["status"], **result["summary"]}), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--partition-index", type=int)
    parser.add_argument("--partition-indices", type=str)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--merge", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    selected = sum(
        (
            args.partition_index is not None,
            args.partition_indices is not None,
            args.all,
            args.merge,
        )
    )
    if selected != 1:
        parser.error("choose exactly one input mode")
    if args.partition_index is not None:
        run_partition(args.partition_index, args.force)
    elif args.partition_indices is not None:
        indices = tuple(int(value) for value in args.partition_indices.split(","))
        for index in indices:
            run_partition(index, args.force)
    elif args.all:
        _source, grouped = source_rows_by_partition()
        for index in sorted(grouped):
            run_partition(index, args.force)
    else:
        merge()


if __name__ == "__main__":
    main()
