"""Independent solver-free continuous compression screen for E0=77."""

from __future__ import annotations

import itertools
import json
import math
from pathlib import Path

from scratch_general_e79_compression_audit import (
    continuous_disjoint_minimum,
    diagonal_square,
    overlap_minimum,
    placement_orbits,
    state_description,
    support_graph_signature,
)


PARTITIONS = tuple(
    tuple(reversed(p))
    for length in range(2, 8)
    for p in itertools.combinations_with_replacement(range(1, 5), length)
    if sum(p) == 7
)


def main():
    rows = []
    totals = []
    for partition in PARTITIONS:
        orbits = placement_orbits(partition)
        overlap_ok = passing = 0
        for orbit_index, (state, orbit_size) in enumerate(orbits):
            ov = overlap_minimum(state)
            diag = diagonal_square(state)
            # tr(D^2)<=4564 and disjoint constant 3360-16*7=3248.
            budget = (4564 - diag - 3248) // 2
            real_min = continuous_disjoint_minimum(state)
            passes = (
                ov["feasible"]
                and ov["minimum_square"] + math.ceil(real_min) <= budget
            )
            overlap_ok += int(ov["feasible"])
            passing += int(passes)
            if passes:
                rows.append({
                    "partition": list(partition),
                    "orbit_index": orbit_index,
                    "orbit_size": orbit_size,
                    "exceptional_supports": state_description(state),
                    "exceptional_support_graph": support_graph_signature(state),
                    "diagonal_square": diag,
                    "joint_square_budget": budget,
                    "overlap_minimum_square": ov["minimum_square"],
                    "overlap_minimizers": ov["stored_minimizers"],
                    "continuous_disjoint_minimum": str(real_min),
                    "continuous_ceiling": math.ceil(real_min),
                })
        summary = {
            "partition": list(partition),
            "labelled": sum(size for _, size in orbits),
            "orbits": len(orbits),
            "overlap_feasible": overlap_ok,
            "passes_continuous_screen": passing,
        }
        totals.append(summary)
        print(json.dumps(summary), flush=True)
    result = {
        "model": "independent E0=77 solver-free compression continuous screen",
        "total_deficit": 7,
        "spectral_D_square_upper": 4564,
        "disjoint_constant": 3248,
        "claim_boundary": "necessary exact real screen only; integer/local lift not asserted",
        "totals": totals,
        "passing_rows": rows,
    }
    Path("scratch_root_e77_screen.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "total_orbits": sum(row["orbits"] for row in totals),
        "passing_rows": len(rows),
    }), flush=True)


if __name__ == "__main__":
    main()
