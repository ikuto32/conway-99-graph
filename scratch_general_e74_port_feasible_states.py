"""Materialize only the 29,203 E0=74 port-feasible state assignments.

The 134,371,022-input Cartesian product remains count-only in the census.
This companion reruns the exact prefix DFS and stores only its feasible leaves,
checking every per-support count against the independently committed census.
"""

from __future__ import annotations

import argparse
import json
import os
from collections import Counter
from pathlib import Path

import scratch_general_e74_compression as e74
import scratch_general_e74_port_census as census
import scratch_general_e75_port_audit as port


COMPRESSION_PATH = Path("scratch_general_e74_compression_audit.json")
CENSUS_PATH = Path("scratch_general_e74_port_census.json")
OUTPUT_PATH = Path("scratch_general_e74_port_feasible_states.json")


def part_path(partition_index):
    return Path(f"scratch_general_e74_port_feasible_part_{partition_index:02d}.json")


def atomic_json(path, value):
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def source_maps():
    e74.configure()
    compression = json.loads(COMPRESSION_PATH.read_text(encoding="utf-8"))
    audited = json.loads(CENSUS_PATH.read_text(encoding="utf-8"))
    assert compression["status"] == audited["status"] == "COMPLETE"
    partition_index = {
        tuple(part["partition"]): part["partition_index"]
        for part in compression["by_partition"]
    }
    compression_rows = {
        (partition_index[tuple(row["partition"])], row["orbit_index"]): row
        for row in compression["rows"]
        if row["passes_weighted_port_overlap_and_real_relaxation"]
    }
    census_rows = {
        (partition_index[tuple(row["partition"])], row["compression_orbit_index"]): row
        for row in audited["rows"]
    }
    assert len(compression_rows) == len(census_rows) == 249
    assert compression_rows.keys() == census_rows.keys()
    grouped = {}
    for key, row in census_rows.items():
        if row["locally_port_feasible_assignments"]:
            grouped.setdefault(key[0], []).append((compression_rows[key], row))
    assert sum(len(rows) for rows in grouped.values()) == 175
    return compression, audited, grouped


def enumerate_feasible(source):
    exceptional = source["exceptional_supports"]
    supports = tuple(tuple(item["support"]) for item in exceptional)
    deficits = tuple(item["deficit"] for item in exceptional)
    domains = tuple(tuple(range(len(port.FIBRE_STATES[d]))) for d in deficits)
    order = port.assignment_order(supports, deficits)
    position = {variable: q for q, variable in enumerate(order)}
    incident = {
        group: tuple(index for index, support in enumerate(supports) if group in support)
        for group in range(7)
    }
    lookahead = {
        group: census.build_group_lookahead(
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
    assignment = [-1] * len(supports)
    feasible = []

    def visit(depth):
        if depth == len(order):
            # An independent full-row control before committing the leaf.
            for group, variables in incident.items():
                signatures = tuple(
                    census.signature_for(
                        supports[index], deficits[index], assignment[index], group
                    )
                    for index in variables
                )
                assert port.group_matchable_signatures(signatures)
            feasible.append(tuple(assignment))
            return
        variable = order[depth]
        for state_index in domains[variable]:
            assignment[variable] = state_index
            valid = True
            for group in supports[variable]:
                data = lookahead[group]
                length = local_rank[(group, variable)] + 1
                prefix = tuple(assignment[index] for index in data["variables"][:length])
                if prefix not in data["allowed"][length]:
                    valid = False
                    break
            if valid:
                visit(depth + 1)
            assignment[variable] = -1

    visit(0)
    return feasible


def state_diagonal_count(exceptional, state_indices):
    diagonal_pairs = {frozenset((0, 3)), frozenset((1, 2))}
    answer = 0
    for item, state_index in zip(exceptional, state_indices):
        state = port.FIBRE_STATES[item["deficit"]][state_index]
        answer += sum(frozenset(edge) in diagonal_pairs for edge in state["edges"])
    return answer


def summarize(rows):
    q_histogram = Counter()
    for row in rows:
        q_histogram.update(
            {int(q): count for q, count in row["feasible_Q_histogram"].items()}
        )
    return {
        "support_rows": len(rows),
        "feasible_state_assignments": sum(
            row["locally_port_feasible_assignments"] for row in rows
        ),
        "feasible_Q_histogram": {
            str(q): count for q, count in sorted(q_histogram.items())
        },
        "conditional_priority_Q_at_least_5": sum(
            count for q, count in q_histogram.items() if q >= 5
        ),
    }


def run_partition(partition_index, force=False):
    _compression, _audited, grouped = source_maps()
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
            "model": "E0=74 materialized feasible fibre-state leaves only",
            "partition_index": partition_index,
            "partition": rows_in[0][0]["partition"] if rows_in else None,
            "rows": [],
        }
        completed = set()
        atomic_json(path, result)
    for offset, (source, expected) in enumerate(rows_in):
        if source["orbit_index"] in completed:
            continue
        feasible = enumerate_feasible(source)
        expected_count = expected["locally_port_feasible_assignments"]
        assert len(feasible) == expected_count
        assert len(set(feasible)) == expected_count
        q_values = [
            state_diagonal_count(source["exceptional_supports"], assignment)
            for assignment in feasible
        ]
        q_histogram = Counter(q_values)
        record = {
            "partition": source["partition"],
            "compression_orbit_index": source["orbit_index"],
            "support_orbit_size": source["orbit_size"],
            "weighted_stabilizer_order": source["weighted_stabilizer_order"],
            "exceptional_supports": source["exceptional_supports"],
            "joint_square_budget": source["joint_off_diagonal_square_budget"],
            "overlap_relaxed_minimum_square": source["overlap"]["minimum_square"],
            "disjoint_continuous_minimum": source["disjoint_continuous_minimum"],
            "labelled_fibre_state_assignments_covered": expected[
                "labelled_fibre_state_assignments_covered"
            ],
            "locally_port_feasible_assignments": expected_count,
            "feasible_state_indices": [list(row) for row in feasible],
            "Q_by_feasible_state": q_values,
            "feasible_Q_histogram": {
                str(q): count for q, count in sorted(q_histogram.items())
            },
            "conditional_priority_Q_at_least_5": sum(
                count for q, count in q_histogram.items() if q >= 5
            ),
        }
        result["rows"].append(record)
        result["summary"] = summarize(result["rows"])
        atomic_json(path, result)
        print(json.dumps({
            "partition_index": partition_index,
            "offset": offset,
            "compression_orbit_index": source["orbit_index"],
            "feasible": expected_count,
        }), flush=True)
    assert len(result["rows"]) == len(rows_in)
    result["status"] = "COMPLETE"
    result["summary"] = summarize(result["rows"])
    atomic_json(path, result)
    return result


def merge():
    _compression, _audited, grouped = source_maps()
    parts = []
    for index in sorted(grouped):
        part = json.loads(part_path(index).read_text(encoding="utf-8"))
        if part["status"] != "COMPLETE":
            raise RuntimeError(f"incomplete {part_path(index)}")
        parts.append(part)
    rows = [row for part in parts for row in part["rows"]]
    result = {
        "status": "COMPLETE",
        "model": "E0=74 explicit port-feasible labelled fibre-state leaves",
        "inputs": [str(COMPRESSION_PATH), str(CENSUS_PATH)],
        "coverage": (
            "only feasible leaves are stored; every per-row count is independently "
            "regenerated and matched to the count-only 134,371,022-tuple census"
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
    assert result["summary"]["support_rows"] == 175
    assert result["summary"]["feasible_state_assignments"] == 29203
    assert sum(result["summary"]["feasible_Q_histogram"].values()) == 29203
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
    selected = sum((args.partition_index is not None, args.partition_indices is not None, args.all, args.merge))
    if selected != 1:
        parser.error("choose exactly one input mode")
    if args.partition_index is not None:
        run_partition(args.partition_index, args.force)
    elif args.partition_indices is not None:
        for index in (int(value) for value in args.partition_indices.split(",")):
            run_partition(index, args.force)
    elif args.all:
        _compression, _audited, grouped = source_maps()
        for index in sorted(grouped):
            run_partition(index, args.force)
    else:
        merge()


if __name__ == "__main__":
    main()
