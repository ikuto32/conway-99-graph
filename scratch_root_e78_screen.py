"""Solver-free first screen of the E0=78 compression placements.

This reuses the exact S7 orbit and overlap-row enumeration from the E79 audit,
but only applies the exact continuous least-norm lower bound to the disjoint
rows.  Passing rows are candidates, not certified integer-feasible lifts.
"""

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
    partition
    for length in range(2, 7)
    for partition in itertools.combinations_with_replacement(range(1, 5), length)
    if sum(partition) == 6
)


def main():
    rows = []
    totals = []
    for ascending in PARTITIONS:
        partition = tuple(reversed(ascending))
        orbits = placement_orbits(partition)
        passing = 0
        overlap_feasible = 0
        for orbit_index, (state, orbit_size) in enumerate(orbits):
            ov = overlap_minimum(state)
            diag = diagonal_square(state)
            # At deficit 6, the disjoint constant is 3360-16*6=3264.
            budget = (4560 - diag - 3264) // 2
            continuous = continuous_disjoint_minimum(state)
            passes = (
                ov["feasible"]
                and ov["minimum_square"] + math.ceil(continuous) <= budget
            )
            overlap_feasible += int(ov["feasible"])
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
                    "continuous_disjoint_minimum": str(continuous),
                    "continuous_ceiling": math.ceil(continuous),
                })
        record = {
            "partition": list(partition),
            "labelled": sum(size for _, size in orbits),
            "orbits": len(orbits),
            "overlap_feasible": overlap_feasible,
            "passes_continuous_screen": passing,
        }
        totals.append(record)
        print(json.dumps(record), flush=True)
    result = {
        "model": "E0=78 solver-free compression continuous screen",
        "spectral_D_square_upper": 4560,
        "total_deficit": 6,
        "claim_boundary": (
            "Exact orbit/overlap enumeration and an exact necessary real "
            "least-norm test only; passing rows need integer and local audits."
        ),
        "totals": totals,
        "passing_rows": rows,
    }
    Path("scratch_root_e78_screen.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"passing_rows": len(rows)}), flush=True)


if __name__ == "__main__":
    main()
