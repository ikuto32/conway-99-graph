"""Solver-free compression audit for total fibre deficit six (E0=78).

This reuses only the elementary K7 support utilities from the E0=79 audit.
All nine deficit partitions (parts at most four) are enumerated modulo S7.
For every orbit, the nonnegative integral overlap-block row equations are
solved exactly by recursion.  No SAT/CP-SAT solver is called.

The disjoint-block calculation reported here is only the exact *real*
least-norm lower bound.  Thus a row marked as surviving is merely not yet
excluded, while every exclusion is rigorous given the compression formulas.
"""

from __future__ import annotations

from collections import Counter
import json
import math
from pathlib import Path

import scratch_general_e79_compression_audit as base


OUTPUT = Path("scratch_general_e78_local_compression.json")
PARTITIONS = (
    (4, 2),
    (4, 1, 1),
    (3, 3),
    (3, 2, 1),
    (3, 1, 1, 1),
    (2, 2, 2),
    (2, 2, 1, 1),
    (2, 1, 1, 1, 1),
    (1, 1, 1, 1, 1, 1),
)


def spectral_square_upper_e78():
    # Fixed Ritz values: 12,-2^6.  The other fourteen lie in [-4,3]
    # and sum to E0/2=39.  Their convex square maximum is 3^13,0^1.
    return 16 * (12 * 12 + 6 * 2 * 2 + 13 * 3 * 3)


def audit():
    spectral_upper = spectral_square_upper_e78()
    assert spectral_upper == 4560
    rows = []
    summaries = {}
    for partition in PARTITIONS:
        assert sum(partition) == 6 and max(partition) <= 4
        orbits = base.placement_orbits(partition)
        counters = Counter()
        labelled = Counter()
        overlap_histogram = Counter()
        joint_margin_histogram = Counter()
        for orbit_index, (state, orbit_size) in enumerate(orbits):
            stabilizer_order = sum(
                base.apply_group_permutation(state, permutation) == state
                for permutation in base.ALL_GROUP_PERMUTATIONS
            )
            assert stabilizer_order * orbit_size == 5040
            overlap_result = base.overlap_minimum(state)
            diagonal = base.diagonal_square(state)
            # At total deficit six, sum_{F<G} x_FG=6, hence the constant
            # disjoint contribution to tr(D^2) is
            #   2*(105*16 - 8*6) = 3264.
            numerator = spectral_upper - diagonal - 3264
            joint_budget = math.floor(numerator / 2)
            disjoint_real = base.continuous_disjoint_minimum(state)
            disjoint_integer_lower = math.ceil(disjoint_real)
            overlap_feasible = overlap_result["feasible"]
            lower_joint = (
                None if not overlap_feasible
                else overlap_result["minimum_square"] + disjoint_integer_lower
            )
            survives_lower_bound = overlap_feasible and lower_joint <= joint_budget
            reason = (
                "OVERLAP_INFEASIBLE" if not overlap_feasible
                else "SPECTRAL_LOWER_BOUND" if not survives_lower_bound
                else "SURVIVES_REAL_DISJOINT_LOWER_BOUND"
            )
            counters[reason] += 1
            labelled[reason] += orbit_size
            if overlap_feasible:
                overlap_histogram[overlap_result["minimum_square"]] += 1
                joint_margin_histogram[joint_budget - lower_joint] += 1
            rows.append({
                "partition": partition,
                "orbit_index": orbit_index,
                "orbit_size": orbit_size,
                "stabilizer_order": stabilizer_order,
                "exceptional_supports": base.state_description(state),
                "support_graph": base.support_graph_signature(state),
                "diagonal_square": diagonal,
                "joint_square_budget": joint_budget,
                "overlap": overlap_result,
                "disjoint_real_minimum": str(disjoint_real),
                "disjoint_integer_square_lower_bound": disjoint_integer_lower,
                "joint_square_lower_bound": lower_joint,
                "spectral_margin_after_lower_bound": (
                    None if lower_joint is None else joint_budget - lower_joint
                ),
                "status": reason,
            })
        key = "+".join(map(str, partition))
        summaries[key] = {
            "partition": partition,
            "labelled_placements": sum(orbit_size for _, orbit_size in orbits),
            "S7_orbits": len(orbits),
            "orbit_status_counts": dict(counters),
            "labelled_status_counts": dict(labelled),
            "overlap_minimum_square_histogram_by_orbit": {
                str(value): count for value, count in sorted(overlap_histogram.items())
            },
            "spectral_margin_histogram_by_orbit": {
                str(value): count for value, count in sorted(joint_margin_histogram.items())
            },
        }
        print(json.dumps({"partition": partition, **summaries[key]}, sort_keys=True), flush=True)

    assert sum(summary["labelled_placements"] for summary in summaries.values()) == 229789
    result = {
        "model": "solver-free E0=78 compression overlap audit",
        "total_deficit": 6,
        "spectral_D_square_upper": spectral_upper,
        "trace_formula": "tr(D^2)=sum_F(8-2delta_F)^2+3264+2*(M2+X2)",
        "partitions": summaries,
        "totals": {
            "labelled_placements": sum(summary["labelled_placements"] for summary in summaries.values()),
            "S7_orbits": sum(summary["S7_orbits"] for summary in summaries.values()),
            "overlap_infeasible_orbits": sum(summary["orbit_status_counts"].get("OVERLAP_INFEASIBLE", 0) for summary in summaries.values()),
            "spectral_lower_bound_excluded_orbits": sum(summary["orbit_status_counts"].get("SPECTRAL_LOWER_BOUND", 0) for summary in summaries.values()),
            "surviving_orbits": sum(summary["orbit_status_counts"].get("SURVIVES_REAL_DISJOINT_LOWER_BOUND", 0) for summary in summaries.values()),
        },
        "rows": rows,
        "claim_boundary": (
            "S7 enumeration and overlap minima are exact solver-free computations. "
            "The disjoint term is only its exact real least-norm lower bound, rounded up; "
            "surviving rows have not been checked for an integral disjoint solution."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main():
    result = audit()
    print(json.dumps(result["totals"], indent=2))


if __name__ == "__main__":
    main()
