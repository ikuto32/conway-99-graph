"""Normalize and independently cross-check the E72 Q>=3 port census.

The source census reuses an E73 implementation whose historical JSON field
names contain ``Q_at_least_4`` and ``Q_below_4``.  In every E72 artifact those
legacy names mean the configured threshold Q>=3 and Q<3, respectively.  This
normalizer retains the legacy fields for traceability and adds unambiguous
Q>=3 aliases for downstream programs.

All input support rows, including rows with no port-feasible state, are
checked.  Q values and target-cardinality identities are recomputed from the
fibre-state catalogue rather than trusted from the recorded histograms.
"""

from __future__ import annotations

import hashlib
import json
import os
from collections import Counter, defaultdict
from pathlib import Path

from scratch_root_e73_q4_port_census import FIBRE_STATES


INPUT = Path("scratch_root_e72_q3_port_census.json")
OUTPUT = Path("scratch_general_e72_q3_port_feasible_states.json")
Q_MIN = 3
LEGACY_NOTE = (
    "legacy fields whose names contain Q_at_least_4 or Q_below_4 mean the "
    "configured threshold Q>=3 or Q<3 in this E72 artifact"
)
DIAGONAL_PAIRS = {frozenset((0, 3)), frozenset((1, 2))}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def atomic_json(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def state_q(deficit: int, state_index: int) -> int:
    state = FIBRE_STATES[deficit][state_index]
    return sum(frozenset(edge) in DIAGONAL_PAIRS for edge in state["edges"])


Q_BY_DEFICIT = {
    deficit: tuple(
        state_q(deficit, state_index)
        for state_index in range(len(FIBRE_STATES[deficit]))
    )
    for deficit in range(1, 5)
}


def assignment_q(exceptional_supports: list[dict], state_indices: list[int]) -> int:
    assert len(exceptional_supports) == len(state_indices)
    answer = 0
    for exceptional, state_index in zip(exceptional_supports, state_indices):
        deficit = int(exceptional["deficit"])
        assert 1 <= deficit <= 4
        assert 0 <= state_index < len(Q_BY_DEFICIT[deficit])
        answer += Q_BY_DEFICIT[deficit][state_index]
    return answer


def product_and_target_count(deficits: list[int]) -> tuple[int, int]:
    """Recompute the full product and the number of assignments with Q>=3."""
    histogram = Counter({0: 1})
    for deficit in deficits:
        expanded = Counter()
        for partial_q, partial_count in histogram.items():
            for q in Q_BY_DEFICIT[deficit]:
                expanded[partial_q + q] += partial_count
        histogram = expanded
    return sum(histogram.values()), sum(
        count for q, count in histogram.items() if q >= Q_MIN
    )


def normalized_partition_rows(source: dict, partition_audit: dict) -> list[dict]:
    answer = []
    seen = set()
    for part in source["by_partition"]:
        partition = tuple(int(value) for value in part["partition"])
        seen.add(partition)
        audit = partition_audit[partition]
        for key in (
            "input_support_orbits",
            "full_labelled_fibre_state_product",
            "Q_at_least_4_assignments_covered",
            "Q_below_4_assignments_excluded",
            "partial_assignment_nodes_tested",
            "Q_at_least_4_assignments_pruned_by_port",
            "locally_port_feasible_support_orbits",
            "locally_port_feasible_Q_at_least_4_assignments",
        ):
            assert audit[key] == int(part[key])
        assert audit["feasible_Q_histogram"] == Counter(
            {int(q): int(count) for q, count in part["feasible_Q_histogram"].items()}
        )
        assert part["all_full_product_identities_verified"] is True
        assert part["all_Q_target_identities_verified"] is True
        normalized = dict(part)
        normalized["Q_at_least_3_assignments_covered"] = part[
            "Q_at_least_4_assignments_covered"
        ]
        normalized["Q_below_3_assignments_excluded"] = part[
            "Q_below_4_assignments_excluded"
        ]
        normalized["Q_at_least_3_assignments_pruned_by_port"] = part[
            "Q_at_least_4_assignments_pruned_by_port"
        ]
        normalized["locally_port_feasible_assignments"] = part[
            "locally_port_feasible_Q_at_least_4_assignments"
        ]
        answer.append(normalized)
    assert seen == set(partition_audit)
    return answer


def main() -> None:
    raw = INPUT.read_bytes()
    source = json.loads(raw)
    summary = source["summary"]
    assert source["status"] == "COMPLETE"
    assert source["Q_condition"] == "Q>=3"
    assert source["schema_compatibility"] == LEGACY_NOTE
    assert summary["all_full_product_identities_verified"] is True
    assert summary["all_Q_target_identities_verified"] is True
    assert len(source["rows"]) == source["input_support_orbits"]
    assert len(source["rows"]) == summary["input_support_orbits"]

    positive_rows = []
    global_q = Counter()
    partition_audit = defaultdict(
        lambda: {
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
    )
    recomputed_full_product = 0
    recomputed_target = 0
    recomputed_pruned = 0

    for source_row_index, row in enumerate(source["rows"]):
        assert row["full_product_coverage_identity_verified"] is True
        assert row["Q_target_coverage_identity_verified"] is True
        partition = tuple(int(value) for value in row["partition"])

        exceptional = row["exceptional_supports"]
        deficits = [int(item["deficit"]) for item in exceptional]
        assert tuple(sorted(deficits, reverse=True)) == partition
        full_product, target_count = product_and_target_count(deficits)
        excluded_count = full_product - target_count
        feasible_states = row["feasible_state_indices"]
        feasible_count = int(row["locally_port_feasible_Q_at_least_4_assignments"])
        assert len(feasible_states) == feasible_count
        assert len({tuple(state) for state in feasible_states}) == feasible_count

        q_values = [assignment_q(exceptional, state) for state in feasible_states]
        recomputed_histogram = Counter(q_values)
        recorded_histogram = Counter(
            {int(q): int(count) for q, count in row["feasible_Q_histogram"].items()}
        )
        assert recomputed_histogram == recorded_histogram
        assert all(q >= Q_MIN for q in q_values)

        assert full_product == int(row["full_labelled_fibre_state_product"])
        assert target_count == int(row["Q_at_least_4_assignments_covered"])
        assert excluded_count == int(row["Q_below_4_assignments_excluded"])
        pruned = int(row["Q_at_least_4_assignments_pruned_by_port"])
        assert target_count == pruned + feasible_count

        part_audit = partition_audit[partition]
        part_audit["input_support_orbits"] += 1
        part_audit["full_labelled_fibre_state_product"] += full_product
        part_audit["Q_at_least_4_assignments_covered"] += target_count
        part_audit["Q_below_4_assignments_excluded"] += excluded_count
        part_audit["partial_assignment_nodes_tested"] += int(
            row["partial_assignment_nodes_tested"]
        )
        part_audit["Q_at_least_4_assignments_pruned_by_port"] += pruned
        part_audit["locally_port_feasible_support_orbits"] += bool(feasible_count)
        part_audit["locally_port_feasible_Q_at_least_4_assignments"] += feasible_count
        part_audit["feasible_Q_histogram"].update(recomputed_histogram)

        direct = row["first_feasible_direct_control"]
        if feasible_count:
            assert direct is not None
            assert direct["state_indices"] == feasible_states[0]
            assert int(direct["Q"]) == q_values[0]
            assert all(direct["closed_Hall_test"])
            assert all(direct["direct_matching_DFS"])
        else:
            assert direct is None

        recomputed_full_product += full_product
        recomputed_target += target_count
        recomputed_pruned += pruned
        global_q.update(recomputed_histogram)

        if not feasible_count:
            continue
        normalized = dict(row)
        normalized["source_row_index"] = source_row_index
        normalized["Q_at_least_3_assignments_covered"] = target_count
        normalized["Q_below_3_assignments_excluded"] = excluded_count
        normalized["Q_at_least_3_assignments_pruned_by_port"] = pruned
        normalized["labelled_fibre_state_assignments_covered"] = target_count
        normalized["locally_port_feasible_assignments"] = feasible_count
        normalized["Q_by_feasible_state"] = q_values
        positive_rows.append(normalized)

    recorded_global_q = Counter(
        {int(q): int(count) for q, count in summary["feasible_Q_histogram"].items()}
    )
    assert global_q == recorded_global_q
    assert len(positive_rows) == int(summary["locally_port_feasible_support_orbits"])
    assert sum(len(row["feasible_state_indices"]) for row in positive_rows) == int(
        summary["locally_port_feasible_Q_at_least_4_assignments"]
    )
    assert recomputed_full_product == int(summary["full_labelled_fibre_state_product"])
    assert recomputed_target == int(summary["Q_at_least_4_assignments_covered"])
    assert recomputed_pruned == int(summary["Q_at_least_4_assignments_pruned_by_port"])
    assert recomputed_target - recomputed_pruned == sum(global_q.values())

    by_partition = normalized_partition_rows(source, partition_audit)
    script_raw = Path(__file__).read_bytes()
    result = {
        "status": "COMPLETE",
        "model": "exact E0=72 root-side Q>=3 port-state compatibility normalization",
        "inputs": [str(INPUT)],
        "input_sha256": sha256_bytes(raw),
        "normalizer": str(Path(__file__)),
        "normalizer_sha256": sha256_bytes(script_raw),
        "Q_condition": "Q>=3",
        "schema_compatibility": LEGACY_NOTE,
        "root_reduction_scope": source["root_reduction_scope"],
        "claim_boundary": (
            "Necessary E0=72,Q>=3 selected-root branch only; exact port census "
            "normalization, not an E0=72 exclusion."
        ),
        "coverage": {
            "input_support_rows_checked": len(source["rows"]),
            "positive_support_rows_copied": len(positive_rows),
            "state_tuples_copied_exactly": sum(global_q.values()),
            "empty_support_rows_checked_but_not_copied": (
                len(source["rows"]) - len(positive_rows)
            ),
            "no_WLOG_beyond_weighted_S7_quotient_in_input": True,
        },
        "independent_cross_checks": {
            "Q_recomputed_from_fibre_state_edges": True,
            "all_feasible_state_tuples_unique_within_rows": True,
            "all_feasible_states_satisfy_Q_at_least_3": True,
            "all_full_Cartesian_products_recomputed": True,
            "all_Q_at_least_3_target_counts_recomputed_by_convolution": True,
            "all_target_equals_pruned_plus_feasible_identities_verified": True,
            "all_first_survivor_Hall_and_direct_DFS_controls_verified": True,
            "all_partition_aggregates_recomputed_and_matched": True,
            "aggregate_counts_match_source_summary": True,
            "fibre_state_Q_by_deficit_and_state_index": {
                str(deficit): list(values)
                for deficit, values in sorted(Q_BY_DEFICIT.items())
            },
        },
        "summary": {
            "input_support_rows": len(source["rows"]),
            "support_rows": len(positive_rows),
            "full_labelled_fibre_state_product": recomputed_full_product,
            "Q_at_least_3_assignments_covered": recomputed_target,
            "Q_at_least_3_assignments_pruned_by_port": recomputed_pruned,
            "feasible_state_assignments": sum(global_q.values()),
            "feasible_Q_histogram": {
                str(q): count for q, count in sorted(global_q.items())
            },
        },
        "source_provenance": {
            "compression_input": source["input"],
            "compression_input_sha256": source["input_sha256"],
        },
        "by_partition": by_partition,
        "rows": positive_rows,
    }
    atomic_json(OUTPUT, result)
    print(json.dumps({"path": str(OUTPUT), "status": "COMPLETE", **result["summary"]}))


if __name__ == "__main__":
    main()
