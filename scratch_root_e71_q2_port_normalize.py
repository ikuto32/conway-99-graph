"""Independently normalize and audit the E0=71, Q>=2 port census.

The producer reuses an older engine whose compatibility field names mention
Q>=4.  In this artifact those fields mean Q>=2.  This script recomputes every
Q value and Cartesian-product count from the fibre-state catalogue, checks all
rows (including empty ones), and writes only positive rows in a downstream-
friendly schema.
"""

from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
import os
from pathlib import Path

from scratch_root_e73_q4_port_census import FIBRE_STATES


INPUT = Path("scratch_root_e71_q2_port_census.json")
OUTPUT = Path("scratch_root_e71_q2_port_feasible_states.json")
Q_MIN = 2
LEGACY_NOTE = "legacy Q_at_least_4 field names mean the configured E71 threshold Q>=2"
DIAGONALS = {frozenset((0, 3)), frozenset((1, 2))}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def atomic_json(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def state_q(deficit: int, state_index: int) -> int:
    state = FIBRE_STATES[deficit][state_index]
    return sum(frozenset(edge) in DIAGONALS for edge in state["edges"])


Q_BY_DEFICIT = {
    deficit: tuple(state_q(deficit, index) for index in range(len(FIBRE_STATES[deficit])))
    for deficit in range(1, 5)
}


def product_counts(deficits: list[int]) -> tuple[int, int]:
    histogram = Counter({0: 1})
    for deficit in deficits:
        expanded = Counter()
        for partial_q, partial_count in histogram.items():
            for q in Q_BY_DEFICIT[deficit]:
                expanded[partial_q + q] += partial_count
        histogram = expanded
    full = sum(histogram.values())
    target = sum(count for q, count in histogram.items() if q >= Q_MIN)
    return full, target


def assignment_q(exceptional: list[dict], indices: list[int]) -> int:
    assert len(exceptional) == len(indices)
    return sum(
        Q_BY_DEFICIT[int(item["deficit"])][int(index)]
        for item, index in zip(exceptional, indices)
    )


def blank_aggregate() -> dict:
    return {
        "input_support_orbits": 0,
        "full_labelled_fibre_state_product": 0,
        "Q_at_least_4_assignments_covered": 0,
        "Q_below_4_assignments_excluded": 0,
        "partial_assignment_nodes_tested": 0,
        "Q_at_least_4_assignments_pruned_by_port": 0,
        "locally_port_feasible_support_orbits": 0,
        "locally_port_feasible_Q_at_least_4_assignments": 0,
        "feasible_Q_histogram": Counter(),
    }


def add_row(aggregate: dict, row: dict, histogram: Counter) -> None:
    aggregate["input_support_orbits"] += 1
    for key in (
        "full_labelled_fibre_state_product",
        "Q_at_least_4_assignments_covered",
        "Q_below_4_assignments_excluded",
        "partial_assignment_nodes_tested",
        "Q_at_least_4_assignments_pruned_by_port",
        "locally_port_feasible_Q_at_least_4_assignments",
    ):
        aggregate[key] += int(row[key])
    aggregate["locally_port_feasible_support_orbits"] += bool(
        row["locally_port_feasible_Q_at_least_4_assignments"]
    )
    aggregate["feasible_Q_histogram"].update(histogram)


def normalized_counter(value: dict) -> Counter:
    return Counter({int(key): int(count) for key, count in value.items()})


def compare_aggregate(actual: dict, expected: dict) -> None:
    for key, value in actual.items():
        if key == "feasible_Q_histogram":
            assert value == normalized_counter(expected[key])
        else:
            assert int(value) == int(expected[key])
    assert expected["all_full_product_identities_verified"] is True
    assert expected["all_Q_target_identities_verified"] is True


def main() -> None:
    raw = INPUT.read_bytes()
    source = json.loads(raw)
    assert source["status"] == "COMPLETE"
    assert source["Q_condition"] == "Q>=2"
    assert source["schema_compatibility"] == LEGACY_NOTE
    assert source["input_support_orbits"] == 4398
    assert len(source["rows"]) == 4398

    global_audit = blank_aggregate()
    by_partition: dict[tuple[int, ...], dict] = defaultdict(blank_aggregate)
    positive = []

    for source_row_index, row in enumerate(source["rows"]):
        assert row["full_product_coverage_identity_verified"] is True
        assert row["Q_target_coverage_identity_verified"] is True
        exceptional = row["exceptional_supports"]
        deficits = [int(item["deficit"]) for item in exceptional]
        partition = tuple(int(value) for value in row["partition"])
        assert tuple(sorted(deficits, reverse=True)) == partition

        full, target = product_counts(deficits)
        below = full - target
        states = row["feasible_state_indices"]
        feasible = int(row["locally_port_feasible_Q_at_least_4_assignments"])
        assert feasible == len(states) == len({tuple(state) for state in states})
        q_values = [assignment_q(exceptional, state) for state in states]
        histogram = Counter(q_values)
        assert all(q >= Q_MIN for q in q_values)
        assert histogram == normalized_counter(row["feasible_Q_histogram"])
        assert full == int(row["full_labelled_fibre_state_product"])
        assert target == int(row["Q_at_least_4_assignments_covered"])
        assert below == int(row["Q_below_4_assignments_excluded"])
        pruned = int(row["Q_at_least_4_assignments_pruned_by_port"])
        assert target == pruned + feasible

        direct = row["first_feasible_direct_control"]
        if feasible:
            assert direct is not None
            assert direct["state_indices"] == states[0]
            assert int(direct["Q"]) == q_values[0]
            assert all(direct["closed_Hall_test"])
            assert all(direct["direct_matching_DFS"])
        else:
            assert direct is None

        add_row(global_audit, row, histogram)
        add_row(by_partition[partition], row, histogram)
        if feasible:
            copied = dict(row)
            copied.update({
                "source_row_index": source_row_index,
                "Q_at_least_2_assignments_covered": target,
                "Q_below_2_assignments_excluded": below,
                "Q_at_least_2_assignments_pruned_by_port": pruned,
                "labelled_fibre_state_assignments_covered": target,
                "locally_port_feasible_assignments": feasible,
                "Q_by_feasible_state": q_values,
            })
            positive.append(copied)

    compare_aggregate(global_audit, source["summary"])
    recorded_parts = {tuple(map(int, part["partition"])): part for part in source["by_partition"]}
    assert set(recorded_parts) == set(by_partition)
    for partition, audit in by_partition.items():
        compare_aggregate(audit, recorded_parts[partition])

    global_histogram = global_audit["feasible_Q_histogram"]
    result = {
        "status": "COMPLETE",
        "model": "independently normalized E0=71 selected-root Q>=2 port census",
        "input": str(INPUT),
        "input_sha256": digest(raw),
        "normalizer": str(Path(__file__)),
        "normalizer_sha256": digest(Path(__file__).read_bytes()),
        "Q_condition": "Q>=2",
        "schema_compatibility": LEGACY_NOTE,
        "root_reduction_scope": source["root_reduction_scope"],
        "coverage": {
            "input_support_rows_checked": len(source["rows"]),
            "positive_support_rows_copied": len(positive),
            "empty_support_rows_checked_but_not_copied": len(source["rows"]) - len(positive),
            "state_tuples_copied_exactly": sum(global_histogram.values()),
        },
        "independent_cross_checks": {
            "Q_recomputed_from_fibre_edges": True,
            "Cartesian_products_recomputed_by_convolution": True,
            "all_target_equals_pruned_plus_feasible_identities_verified": True,
            "all_first_survivor_Hall_and_direct_DFS_controls_verified": True,
            "all_partition_and_global_aggregates_matched": True,
            "fibre_state_Q_by_deficit": {
                str(deficit): list(values) for deficit, values in sorted(Q_BY_DEFICIT.items())
            },
        },
        "summary": {
            "input_support_rows": len(source["rows"]),
            "support_rows": len(positive),
            "locally_port_feasible_assignments": sum(global_histogram.values()),
            "feasible_Q_histogram": {
                str(q): count for q, count in sorted(global_histogram.items())
            },
            "Q_at_least_2_assignments_covered": global_audit["Q_at_least_4_assignments_covered"],
            "Q_at_least_2_assignments_pruned_by_port": global_audit["Q_at_least_4_assignments_pruned_by_port"],
        },
        "by_partition": source["by_partition"],
        "rows": positive,
        "claim_boundary": (
            "Necessary E0=71,Q>=2 selected-root branch only; exact independent "
            "normalization, not an E0=71 exclusion."
        ),
    }
    atomic_json(OUTPUT, result)
    print(json.dumps({"path": str(OUTPUT), **result["summary"]}, sort_keys=True))


if __name__ == "__main__":
    main()
