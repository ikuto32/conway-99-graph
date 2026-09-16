"""Exact local port audit for the all-P4 E0=78 compression branch."""

from __future__ import annotations

import itertools
import json
from pathlib import Path

from scratch_general_e79_lift_orientation_audit import overlap_pattern_count


def main():
    source = json.loads(Path("scratch_root_e78_screen.json").read_text(encoding="utf-8"))
    candidates = [
        row for row in source["passing_rows"]
        if row["partition"] == [1, 1, 1, 1, 1, 1]
    ]
    assert len(candidates) == 34
    rows = []
    for row in candidates:
        supports = tuple(sorted(
            tuple(item["support"]) for item in row["exceptional_supports"]
        ))
        feasible = 0
        patterns = 0
        first = None
        for orientation in itertools.product(range(4), repeat=6):
            count, by_group = overlap_pattern_count(supports, orientation)
            if count:
                feasible += 1
                patterns += count
                if first is None:
                    first = {
                        "orientation": list(orientation),
                        "group_matching_counts": by_group,
                        "pattern_count": count,
                    }
        rows.append({
            "orbit_index": row["orbit_index"],
            "orbit_size": row["orbit_size"],
            "supports": [list(edge) for edge in supports],
            "support_graph": row["exceptional_support_graph"],
            "orientations_checked": 4**6,
            "locally_BP_feasible_orientations": feasible,
            "locally_BP_feasible_overlap_patterns": patterns,
            "first_feasible": first,
        })
        print(json.dumps({
            "orbit": row["orbit_index"],
            "feasible_orientations": feasible,
            "patterns": patterns,
        }), flush=True)
    result = {
        "model": "E0=78 exact local overlap-port audit for deficit partition 1^6",
        "input": "scratch_root_e78_screen.json",
        "method": (
            "all 4^6 P4 missing-side orientations; exact compatible perfect "
            "matching of the two endpoint BP-deficit ports at every group"
        ),
        "claim_boundary": (
            "zero count is a local BP contradiction; positive count is only "
            "a necessary local completion, not an 84-vertex lift"
        ),
        "support_orbits_checked": len(rows),
        "support_orbits_locally_feasible": sum(
            r["locally_BP_feasible_orientations"] > 0 for r in rows
        ),
        "rows": rows,
    }
    Path("scratch_root_e78_p4_ports.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "orbits": len(rows),
        "locally_feasible": result["support_orbits_locally_feasible"],
    }))


if __name__ == "__main__":
    main()
