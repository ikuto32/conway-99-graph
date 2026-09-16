"""Supplement the solver-free E76 local audit with CP-SAT disjoint minima.

This does not replace the solver-free result: the OPTIMAL claims in the input
have no proof certificates.  It only intersects those reported minima with the
already canonical local graph representatives, for a separately labelled
solver-dependent screen.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


LOCAL_PATH = Path("scratch_general_e76_local_expansion.json")
PORT_PATH = Path("scratch_general_e76_port_audit.json")
INTEGER_PATH = Path("scratch_root_e76_disjoint_integer.json")
OUTPUT_PATH = Path("scratch_general_e76_integer_local_filter.json")


def row_key(row):
    # Port/local files list deficits in representative support order, whereas
    # the independent integer file records the canonical integer partition.
    return tuple(sorted(row["partition"], reverse=True)), row["orbit_index"]


def overlap_square(representative, supports):
    support_index = {tuple(support): index for index, support in enumerate(supports)}
    counts = Counter()
    for left, right in representative["edges"]:
        left_support = tuple(sorted((left[0] // 2, left[1] // 2)))
        right_support = tuple(sorted((right[0] // 2, right[1] // 2)))
        left_index = support_index[left_support]
        right_index = support_index[right_support]
        if left_index != right_index:
            counts[tuple(sorted((left_index, right_index)))] += 1
    assert sum(counts.values()) == 16
    return sum(value * value for value in counts.values())


def main():
    local = json.loads(LOCAL_PATH.read_text(encoding="utf-8"))
    port = json.loads(PORT_PATH.read_text(encoding="utf-8"))
    integer = json.loads(INTEGER_PATH.read_text(encoding="utf-8"))
    port_rows = {row_key(row): row for row in port["rows"]}
    integer_rows = {row_key(row): row for row in integer["rows"]}
    rows = []
    for local_row in local["rows"]:
        key = row_key(local_row)
        port_row = port_rows[key]
        integer_row = integer_rows[key]
        minimum_data = integer_row["disjoint_integer"]
        assert minimum_data["status"] == "OPTIMAL"
        assert minimum_data["witness_verified"]
        minimum = minimum_data["minimum_square"]
        budget = port_row["joint_square_budget"]
        kept = []
        rejected = []
        for representative in local_row["local_graph_representatives"]:
            m2 = overlap_square(representative, local_row["supports"])
            record = {
                "mask_hex": representative["mask_hex"],
                "orbit_size": representative["orbit_size"],
                "actual_overlap_square": m2,
            }
            (kept if m2 + minimum <= budget else rejected).append(record)
        raw_before = sum(row["orbit_size"] for row in kept + rejected)
        raw_after = sum(row["orbit_size"] for row in kept)
        assert raw_before == local_row["after_forced_C4_support_BP"]
        rows.append(
            {
                "partition": local_row["partition"],
                "orbit_index": local_row["orbit_index"],
                "supports": local_row["supports"],
                "joint_square_budget": budget,
                "cp_sat_disjoint_minimum": minimum,
                "raw_before_supplemental_filter": raw_before,
                "orbits_before_supplemental_filter": len(kept) + len(rejected),
                "raw_after_supplemental_filter": raw_after,
                "orbits_after_supplemental_filter": len(kept),
                "kept_representatives": kept,
                "rejected_representatives": rejected,
            }
        )
    result = {
        "status": "SOLVER_DEPENDENT_NECESSARY_SCREEN",
        "model": "E0=76 local representatives intersected with CP-SAT disjoint-block minima",
        "inputs": [str(LOCAL_PATH), str(PORT_PATH), str(INTEGER_PATH)],
        "claim_boundary": (
            "The local representatives and their raw orbit sums are exact solver-free "
            "enumeration.  This supplemental intersection relies on CP-SAT OPTIMAL "
            "minimum claims without independently checked proof certificates; it is "
            "not promoted to an analytic exclusion."
        ),
        "support_rows_before": sum(row["raw_before_supplemental_filter"] > 0 for row in rows),
        "local_orbits_before": sum(row["orbits_before_supplemental_filter"] for row in rows),
        "raw_graphs_before": sum(row["raw_before_supplemental_filter"] for row in rows),
        "support_rows_after": sum(row["raw_after_supplemental_filter"] > 0 for row in rows),
        "local_orbits_after": sum(row["orbits_after_supplemental_filter"] for row in rows),
        "raw_graphs_after": sum(row["raw_after_supplemental_filter"] for row in rows),
        "rows": rows,
    }
    OUTPUT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                key: result[key]
                for key in (
                    "support_rows_before",
                    "local_orbits_before",
                    "raw_graphs_before",
                    "support_rows_after",
                    "local_orbits_after",
                    "raw_graphs_after",
                )
            }
        )
    )


if __name__ == "__main__":
    main()
