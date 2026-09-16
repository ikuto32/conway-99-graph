"""Exact fibre-compression placement audit for E0=78 (deficit six).

The orbit and overlap routines are the generic, already-audited routines
from scratch_general_e79_compression_audit.  This entry point changes every
deficit-dependent constant and can run either the solver-free overlap/real
relaxation phase or the exact bounded-integer disjoint phase.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path

import scratch_general_e79_compression_audit as base


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
RESULT_PATH = Path("scratch_general_e78_compression_audit.json")
SPECTRAL_UPPER = 4560
DISJOINT_CONSTANT = 3264


def joint_budget(state):
    diagonal = base.diagonal_square(state)
    numerator = SPECTRAL_UPPER - diagonal - DISJOINT_CONSTANT
    assert numerator % 2 == 0
    return numerator // 2


def build_rows(run_integer):
    rows = []
    orbit_totals = {}
    for partition in PARTITIONS:
        orbits = base.placement_orbits(partition)
        orbit_totals[str(partition)] = {
            "orbit_count": len(orbits),
            "labelled_count": sum(size for _state, size in orbits),
        }
        for orbit_index, (state, orbit_size) in enumerate(orbits):
            stabilizer_order = sum(
                base.apply_group_permutation(state, permutation) == state
                for permutation in base.ALL_GROUP_PERMUTATIONS
            )
            assert orbit_size * stabilizer_order == 5040
            overlap = base.overlap_minimum(state)
            budget = joint_budget(state)
            continuous = base.continuous_disjoint_minimum(state)
            continuous_lower = math.ceil(continuous)
            real_relaxation_passes = (
                overlap["feasible"]
                and overlap["minimum_square"] + continuous_lower <= budget
            )
            disjoint = None
            passes = None
            if run_integer and real_relaxation_passes:
                x_budget = budget - overlap["minimum_square"]
                disjoint = base.disjoint_integer_minimum(state, x_budget)
                passes = (
                    disjoint["status"] in ("OPTIMAL", "FEASIBLE")
                    and overlap["minimum_square"] + disjoint["minimum_square"] <= budget
                )
            row = {
                "partition": list(partition),
                "orbit_index": orbit_index,
                "orbit_size": orbit_size,
                "stabilizer_order": stabilizer_order,
                "exceptional_supports": base.state_description(state),
                "exceptional_support_graph": base.support_graph_signature(state),
                "diagonal_square": base.diagonal_square(state),
                "joint_off_diagonal_square_budget": budget,
                "overlap": overlap,
                "disjoint_continuous_minimum": str(continuous),
                "disjoint_continuous_ceiling": continuous_lower,
                "passes_overlap_and_real_relaxation": real_relaxation_passes,
                "disjoint_integer": disjoint,
                "passes_compression_square_and_BP": passes,
            }
            if passes:
                total_square = (
                    row["diagonal_square"]
                    + DISJOINT_CONSTANT
                    + 2 * (overlap["minimum_square"] + disjoint["minimum_square"])
                )
                assert total_square <= SPECTRAL_UPPER
                row["verified_total_D_square"] = total_square
            rows.append(row)
    return rows, orbit_totals


def audit(run_integer):
    # The 14 free Ritz values have sum 39 and lie in [-4,3].  Their maximum
    # square sum is 13*3^2+0^2=117.
    assert SPECTRAL_UPPER == 16 * (12**2 + 6 * 2**2 + 13 * 3**2)
    rows, orbit_totals = build_rows(run_integer)
    return {
        "model": "E0=78 exact fibre-compression placement audit",
        "phase": "exact_integer_disjoint" if run_integer else "solver_free_overlap_and_real_relaxation",
        "theorem_inputs": {
            "total_deficit": 6,
            "total_fibre_edges_E0": 78,
            "spectral_D_square_upper": SPECTRAL_UPPER,
            "spectral_maximizing_free_Ritz_multiset": [3] * 13 + [0],
            "trace_identity": (
                "tr(D^2)=diagonal_square+3264+2*(overlap_square+x_square)"
            ),
            "BP_overlap_row_sum": "4*delta_F",
            "disjoint_deviation_row_sum": "sum x_FG=2*delta_F for x=4-D",
        },
        "method_audit": {
            "symmetry": (
                "Every labelled placement is generated; S7 orbits use all six adjacent "
                "transpositions; orbit-stabilizer is rechecked against all 5040 permutations."
            ),
            "overlap": "solver-free exhaustive nonnegative-integer recursion",
            "disjoint_real": "exact Fraction least-norm value, rounded up only as a necessary bound",
            "disjoint_integer": (
                "not run" if not run_integer else
                "bounded one-worker CP-SAT; every positive witness directly checked by the imported routine"
            ),
        },
        "orbit_totals": orbit_totals,
        "rows": rows,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--integer", action="store_true")
    args = parser.parse_args()
    result = audit(args.integer)
    RESULT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    counts = Counter()
    for row in result["rows"]:
        key = tuple(row["partition"])
        counts[(key, "orbits")] += 1
        counts[(key, "overlap_feasible")] += int(row["overlap"]["feasible"])
        counts[(key, "real_pass")] += int(row["passes_overlap_and_real_relaxation"])
        if args.integer:
            counts[(key, "integer_pass")] += int(bool(row["passes_compression_square_and_BP"]))
    print(json.dumps({
        "phase": result["phase"],
        "total_orbits": len(result["rows"]),
        "real_passes": sum(row["passes_overlap_and_real_relaxation"] for row in result["rows"]),
        "integer_passes": (
            sum(bool(row["passes_compression_square_and_BP"]) for row in result["rows"])
            if args.integer else None
        ),
        "counts": {str(key): value for key, value in counts.items()},
    }, sort_keys=True))


if __name__ == "__main__":
    main()
