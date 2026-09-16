"""Checkpointed count-only labelled fibre-state port census for E0=74.

No Cartesian product of feasible assignments is materialized.  For each root
group, all locally Hall-matchable full assignments are projected to allowed
prefix sets.  A global fixed-order DFS then rejects a subtree as soon as one
endpoint group has no possible local completion.  Exact suffix-product counts
certify ``feasible + pruned == full Cartesian product`` for every support row.

All deficit-three states remain distinct (six state indices), including the
two states having the same aggregate port signature.
"""

from __future__ import annotations

import argparse
import itertools
import json
import os
from collections import defaultdict
from pathlib import Path

import scratch_general_e74_compression as e74
import scratch_general_e75_port_audit as port


INPUT_PATH = Path("scratch_general_e74_compression_audit.json")
OUTPUT_PATH = Path("scratch_general_e74_port_census.json")
FIBRE_STATES = port.FIBRE_STATES
SIGNATURES = port.SIGNATURES
assert tuple(len(FIBRE_STATES[d]) for d in (1, 2, 3)) == (4, 7, 6)
assert len(set(SIGNATURES[3])) == 5 and len(SIGNATURES[3]) == 6


def part_path(partition_index):
    return Path(f"scratch_general_e74_port_census_part_{partition_index:02d}.json")


def atomic_json(path, value):
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def product(values):
    answer = 1
    for value in values:
        answer *= value
    return answer


def source_rows_by_partition():
    e74.configure()
    source = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    assert source["status"] == "COMPLETE"
    assert source["summary"]["final_intersection"] == 249
    partition_to_index = {
        tuple(row["partition"]): row["partition_index"]
        for row in source["by_partition"]
    }
    grouped = defaultdict(list)
    for row in source["rows"]:
        if row["passes_weighted_port_overlap_and_real_relaxation"]:
            grouped[partition_to_index[tuple(row["partition"])]].append(row)
    assert sum(map(len, grouped.values())) == 249
    return source, grouped


def signature_for(support, deficit, state_index, group):
    axis = support.index(group)
    return SIGNATURES[deficit][state_index][axis]


def build_group_lookahead(group, variables, supports, deficits, domains, position):
    """Return all state-index prefixes extendable to a Hall-feasible row."""
    ordered = tuple(sorted(variables, key=position.__getitem__))
    allowed = [set() for _ in range(len(ordered) + 1)]
    full_count = product(len(domains[index]) for index in ordered)
    matchable_count = 0
    for choices in itertools.product(*(domains[index] for index in ordered)):
        signatures = tuple(
            signature_for(supports[index], deficits[index], state_index, group)
            for index, state_index in zip(ordered, choices)
        )
        if not port.group_matchable_signatures(signatures):
            continue
        matchable_count += 1
        for length in range(len(ordered) + 1):
            allowed[length].add(choices[:length])
    # Weighted-port balance guarantees aggregate totals exist, but labelled
    # sign/requirement states can still make a whole support row impossible.
    # Therefore matchable_count=0 is recorded rather than asserted away.
    return {
        "group": group,
        "variables": ordered,
        "full_local_assignments": full_count,
        "matchable_full_local_assignments": matchable_count,
        "allowed_prefix_counts": [len(values) for values in allowed],
        "allowed": allowed,
    }


def audit_row(source):
    exceptional = source["exceptional_supports"]
    supports = tuple(tuple(item["support"]) for item in exceptional)
    deficits = tuple(item["deficit"] for item in exceptional)
    assert all(deficit in (1, 2, 3) for deficit in deficits)
    domains = tuple(tuple(range(len(FIBRE_STATES[d]))) for d in deficits)
    total = product(len(domain) for domain in domains)
    order = port.assignment_order(supports, deficits)
    position = {variable: q for q, variable in enumerate(order)}
    incident = {
        group: tuple(index for index, support in enumerate(supports) if group in support)
        for group in range(7)
    }
    lookahead = {
        group: build_group_lookahead(
            group, variables, supports, deficits, domains, position
        )
        for group, variables in incident.items()
        if variables
    }
    local_rank = {
        (group, variable): rank
        for group, data in lookahead.items()
        for rank, variable in enumerate(data["variables"])
    }
    suffix = [1] * (len(order) + 1)
    for depth in range(len(order) - 1, -1, -1):
        suffix[depth] = suffix[depth + 1] * len(domains[order[depth]])

    assignment = [-1] * len(supports)
    feasible = 0
    pruned = 0
    partial_nodes = 0
    prefix_tests = 0
    first_feasible = None
    pruned_by_group = [0] * 7

    def visit(depth):
        nonlocal feasible, pruned, partial_nodes, prefix_tests, first_feasible
        if depth == len(order):
            feasible += 1
            if first_feasible is None:
                first_feasible = tuple(assignment)
            return
        variable = order[depth]
        for state_index in domains[variable]:
            partial_nodes += 1
            assignment[variable] = state_index
            failed_group = None
            for group in supports[variable]:
                prefix_tests += 1
                data = lookahead[group]
                length = local_rank[(group, variable)] + 1
                prefix = tuple(assignment[index] for index in data["variables"][:length])
                assert all(value >= 0 for value in prefix)
                if prefix not in data["allowed"][length]:
                    failed_group = group
                    break
            if failed_group is None:
                visit(depth + 1)
            else:
                subtree = suffix[depth + 1]
                pruned += subtree
                pruned_by_group[failed_group] += subtree
            assignment[variable] = -1

    visit(0)
    assert feasible + pruned == total
    first_control = (
        port.direct_check_first(exceptional, first_feasible)
        if first_feasible is not None
        else None
    )
    group_records = []
    for group in sorted(lookahead):
        data = lookahead[group]
        group_records.append(
            {
                key: (list(value) if key == "variables" else value)
                for key, value in data.items()
                if key != "allowed"
            }
        )
    return {
        "partition": source["partition"],
        "compression_orbit_index": source["orbit_index"],
        "support_orbit_size": source["orbit_size"],
        "weighted_stabilizer_order": source["weighted_stabilizer_order"],
        "exceptional_supports": exceptional,
        "labelled_fibre_state_assignments_covered": total,
        "locally_port_feasible_assignments": feasible,
        "assignments_pruned_in_subtrees": pruned,
        "coverage_identity_verified": feasible + pruned == total,
        "partial_assignment_nodes_tested": partial_nodes,
        "group_prefix_tests": prefix_tests,
        "assignments_pruned_by_first_failing_group": pruned_by_group,
        "assignment_order": list(order),
        "group_lookahead": group_records,
        "first_feasible_direct_control": first_control,
    }


def summarize(rows):
    return {
        "input_support_orbits": len(rows),
        "labelled_fibre_state_assignments_covered": sum(
            row["labelled_fibre_state_assignments_covered"] for row in rows
        ),
        "partial_assignment_nodes_tested": sum(
            row["partial_assignment_nodes_tested"] for row in rows
        ),
        "assignments_pruned_in_subtrees": sum(
            row["assignments_pruned_in_subtrees"] for row in rows
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
        completed = {row["compression_orbit_index"] for row in result["rows"]}
    else:
        result = {
            "status": "ENUMERATING",
            "model": "count-only exhaustive labelled E0=74 fibre-state port census",
            "partition_index": partition_index,
            "partition": rows_in[0]["partition"] if rows_in else None,
            "input_support_orbits": len(rows_in),
            "fibre_state_counts": {"deficit_1": 4, "deficit_2": 7, "deficit_3": 6},
            "coverage": (
                "all labelled state indices, including all six deficit-three states; "
                "no feasible Cartesian product is materialized; exact suffix-product "
                "subtree counts prove complete coverage"
            ),
            "rows": [],
        }
        completed = set()
        atomic_json(path, result)
    for offset, source_row in enumerate(rows_in):
        if source_row["orbit_index"] in completed:
            continue
        record = audit_row(source_row)
        result["rows"].append(record)
        result["summary"] = summarize(result["rows"])
        atomic_json(path, result)
        print(json.dumps({
            "phase": "row",
            "partition_index": partition_index,
            "offset": offset,
            "compression_orbit_index": source_row["orbit_index"],
            "covered": record["labelled_fibre_state_assignments_covered"],
            "pruned": record["assignments_pruned_in_subtrees"],
            "feasible": record["locally_port_feasible_assignments"],
            "partial_nodes": record["partial_assignment_nodes_tested"],
        }), flush=True)
    assert len(result["rows"]) == len(rows_in)
    assert len({row["compression_orbit_index"] for row in result["rows"]}) == len(rows_in)
    result["status"] = "COMPLETE"
    result["summary"] = summarize(result["rows"])
    atomic_json(path, result)
    return result


def merge():
    _source, grouped = source_rows_by_partition()
    parts = []
    for partition_index in sorted(grouped):
        path = part_path(partition_index)
        part = json.loads(path.read_text(encoding="utf-8"))
        if part["status"] != "COMPLETE":
            raise RuntimeError(f"incomplete {path}: {part['status']}")
        parts.append(part)
    rows = [row for part in parts for row in part["rows"]]
    result = {
        "status": "COMPLETE",
        "model": "merged count-only exhaustive labelled E0=74 fibre-state port census",
        "input": str(INPUT_PATH),
        "input_support_orbits": 249,
        "fibre_state_counts": {"deficit_1": 4, "deficit_2": 7, "deficit_3": 6},
        "matching_test": (
            "exact per-group signature/Hall condition with extendable-prefix lookahead; "
            "first positive assignment of every row checked by direct matching DFS"
        ),
        "coverage": (
            "all labelled state-index assignments, no type/orientation/symmetry WLOG; "
            "each row asserts feasible_count + pruned_suffix_count = full product"
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
    assert result["summary"]["input_support_orbits"] == 249
    assert all(row["coverage_identity_verified"] for row in rows)
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
    selected = sum((
        args.partition_index is not None,
        args.partition_indices is not None,
        args.all,
        args.merge,
    ))
    if selected != 1:
        parser.error("choose exactly one input mode")
    if args.partition_index is not None:
        run_partition(args.partition_index, args.force)
    elif args.partition_indices is not None:
        indices = tuple(int(value) for value in args.partition_indices.split(","))
        if not indices or len(indices) != len(set(indices)):
            parser.error("partition indices must be nonempty and unique")
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
