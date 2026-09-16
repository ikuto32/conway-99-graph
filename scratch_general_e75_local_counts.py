"""Exact overlap-matching completion counts for E0=75 port survivors."""

from __future__ import annotations

import argparse
import functools
import json
import os
from collections import Counter
from pathlib import Path

import scratch_general_e75_port_audit as port75


INPUT_PATH = Path("scratch_general_e75_port_audit.json")
OUTPUT_PATH = Path("scratch_general_e75_local_completion_counts.json")
MODEL_E0 = 75
EXPECTED_SUPPORT_ROWS = 50
EXPECTED_STATE_ASSIGNMENTS = 2380


def part_path(partition_index):
    return Path(f"scratch_general_e75_local_count_part_{partition_index:02d}.json")


def atomic_json(path, value):
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


@functools.lru_cache(maxsize=None)
def signature_matching_count(canonical_signatures):
    """Count labelled perfect matchings of ports with same-fibre forbidden."""
    stubs = []
    categories = ((0, 0), (0, 1), (1, 0), (1, 1))
    for fibre, signature in enumerate(canonical_signatures):
        for multiplicity, (sigma, required) in zip(signature, categories):
            for copy in range(multiplicity):
                stubs.append((fibre, sigma, required, copy))
    assert len(stubs) % 2 == 0
    candidates = []
    for q, (fibre, sigma, required, _copy) in enumerate(stubs):
        row = 0
        for r, (other_fibre, other_sigma, other_required, _other_copy) in enumerate(stubs):
            if q == r or fibre == other_fibre:
                continue
            if sigma == other_required and other_sigma == required:
                row |= 1 << r
        candidates.append(row)

    @functools.lru_cache(maxsize=None)
    def visit(mask):
        if not mask:
            return 1
        indices = [q for q in range(len(stubs)) if mask & (1 << q)]
        first = min(indices, key=lambda q: (candidates[q] & mask).bit_count())
        choices = candidates[first] & mask & ~(1 << first)
        answer = 0
        while choices:
            low = choices & -choices
            answer += visit(mask & ~(1 << first) & ~low)
            choices ^= low
        return answer

    return visit((1 << len(stubs)) - 1)


def group_signatures(exceptional, state_indices, group):
    rows = []
    for item, state_index in zip(exceptional, state_indices):
        support = tuple(item["support"])
        if group not in support:
            continue
        axis = support.index(group)
        rows.append(port75.SIGNATURES[item["deficit"]][state_index][axis])
    return tuple(sorted(rows))


def assignment_diagonal_count(exceptional, state_indices):
    diagonal_pairs = {frozenset((0, 3)), frozenset((1, 2))}
    return sum(
        frozenset(edge) in diagonal_pairs
        for item, state_index in zip(exceptional, state_indices)
        for edge in port75.FIBRE_STATES[item["deficit"]][state_index]["edges"]
    )


def audit_row(row):
    exceptional = row["exceptional_supports"]
    histogram = Counter()
    group_count_histograms = [Counter() for _ in range(7)]
    total = 0
    maximum = 0
    first = None
    state_q_histogram = Counter()
    completion_q_histogram = Counter()
    for state_indices in row["feasible_state_indices"]:
        q_value = assignment_diagonal_count(exceptional, state_indices)
        state_q_histogram[q_value] += 1
        counts = tuple(
            signature_matching_count(group_signatures(exceptional, state_indices, group))
            for group in range(7)
        )
        assert all(counts)
        completion_count = 1
        for count in counts:
            completion_count *= count
        total += completion_count
        completion_q_histogram[q_value] += completion_count
        maximum = max(maximum, completion_count)
        histogram[completion_count] += 1
        for group, count in enumerate(counts):
            group_count_histograms[group][count] += 1
        if first is None:
            first = {
                "state_indices": state_indices,
                "exact_matching_counts_by_group": list(counts),
                "completion_product": completion_count,
            }
    return {
        "partition": row["partition"],
        "compression_orbit_index": row["compression_orbit_index"],
        "support_orbit_size": row["support_orbit_size"],
        "weighted_stabilizer_order": row["weighted_stabilizer_order"],
        "exceptional_supports": row["exceptional_supports"],
        "port_feasible_state_assignments": row["locally_port_feasible_assignments"],
        "exact_overlap_completions": total,
        "maximum_completions_for_one_state": maximum,
        "completion_count_histogram": {
            str(key): value for key, value in sorted(histogram.items())
        },
        "group_matching_count_histograms": [
            {str(key): value for key, value in sorted(histogram.items())}
            for histogram in group_count_histograms
        ],
        "state_Q_histogram": {
            str(key): value for key, value in sorted(state_q_histogram.items())
        },
        "completion_Q_histogram": {
            str(key): value for key, value in sorted(completion_q_histogram.items())
        },
        "conditional_priority_Q_at_least_5_states": sum(
            value for key, value in state_q_histogram.items() if key >= 5
        ),
        "conditional_priority_Q_at_least_5_completions": sum(
            value for key, value in completion_q_histogram.items() if key >= 5
        ),
        "first_state_count_control": first,
    }


def rows_by_partition():
    source = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    assert source["status"] == "COMPLETE"
    positive = [row for row in source["rows"] if row["locally_port_feasible_assignments"]]
    assert len(positive) == EXPECTED_SUPPORT_ROWS
    grouped = {}
    for part in source["by_partition"]:
        grouped[part["partition_index"]] = []
    for row in positive:
        # Only these seven partition indices reached the compression frontier.
        partition_index = next(
            part["partition_index"]
            for part in source["by_partition"]
            if part["partition"] == row["partition"]
        )
        grouped[partition_index].append(row)
    return source, {index: rows for index, rows in grouped.items() if rows}


def summarize(rows):
    state_q = Counter()
    completion_q = Counter()
    for row in rows:
        state_q.update({int(key): value for key, value in row["state_Q_histogram"].items()})
        completion_q.update({int(key): value for key, value in row["completion_Q_histogram"].items()})
    return {
        "support_rows": len(rows),
        "port_feasible_state_assignments": sum(
            row["port_feasible_state_assignments"] for row in rows
        ),
        "exact_overlap_completions": sum(row["exact_overlap_completions"] for row in rows),
        "maximum_per_support_row": max(
            (row["exact_overlap_completions"] for row in rows), default=0
        ),
        "state_Q_histogram": {
            str(key): value for key, value in sorted(state_q.items())
        },
        "completion_Q_histogram": {
            str(key): value for key, value in sorted(completion_q.items())
        },
        "conditional_priority_Q_at_least_5_states": sum(
            value for key, value in state_q.items() if key >= 5
        ),
        "conditional_priority_Q_at_least_5_completions": sum(
            value for key, value in completion_q.items() if key >= 5
        ),
    }


def run_partition(partition_index, force=False):
    _source, grouped = rows_by_partition()
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
            "status": "COUNTING",
            "model": f"checkpointed exact E0={MODEL_E0} overlap-matching completion counts",
            "partition_index": partition_index,
            "partition": rows_in[0]["partition"] if rows_in else None,
            "rows": [],
        }
        completed = set()
        atomic_json(path, result)
    for offset, row in enumerate(rows_in):
        if row["compression_orbit_index"] in completed:
            continue
        record = audit_row(row)
        result["rows"].append(record)
        result["summary"] = summarize(result["rows"])
        atomic_json(path, result)
        print(
            json.dumps(
                {
                    "partition_index": partition_index,
                    "offset": offset,
                    "compression_orbit_index": record["compression_orbit_index"],
                    "states": record["port_feasible_state_assignments"],
                    "completions": record["exact_overlap_completions"],
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
    _source, grouped = rows_by_partition()
    parts = []
    for partition_index in sorted(grouped):
        path = part_path(partition_index)
        if not path.exists():
            raise RuntimeError(f"missing {path}")
        part = json.loads(path.read_text(encoding="utf-8"))
        if part["status"] != "COMPLETE":
            raise RuntimeError(f"incomplete {path}: {part['status']}")
        parts.append(part)
    rows = [row for part in parts for row in part["rows"]]
    result = {
        "status": "COMPLETE",
        "model": f"exact E0={MODEL_E0} overlap-matching completion counts",
        "input": str(INPUT_PATH),
        "method": (
            "exact memoized perfect-matching count on labelled BP ports at each "
            "root group; counts multiply because the seven port sets are disjoint"
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
        "distinct_group_signature_counts_cached": signature_matching_count.cache_info().currsize,
        "rows": rows,
    }
    assert result["summary"]["support_rows"] == EXPECTED_SUPPORT_ROWS
    assert (
        result["summary"]["port_feasible_state_assignments"]
        == EXPECTED_STATE_ASSIGNMENTS
    )
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
        parser.error("choose exactly one mode")
    if args.partition_index is not None:
        run_partition(args.partition_index, args.force)
    elif args.partition_indices is not None:
        for index in (int(value) for value in args.partition_indices.split(",")):
            run_partition(index, args.force)
    elif args.all:
        _source, grouped = rows_by_partition()
        for index in sorted(grouped):
            run_partition(index, args.force)
    else:
        merge()


if __name__ == "__main__":
    main()
