"""Exact fibre-compression placement audit for E0=77 (deficit seven)."""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path

import scratch_general_e79_compression_audit as base


PARTITIONS = (
    (4, 3),
    (4, 2, 1),
    (4, 1, 1, 1),
    (3, 3, 1),
    (3, 2, 2),
    (3, 2, 1, 1),
    (3, 1, 1, 1, 1),
    (2, 2, 2, 1),
    (2, 2, 1, 1, 1),
    (2, 1, 1, 1, 1, 1),
    (1, 1, 1, 1, 1, 1, 1),
)
RESULT_PATH = Path("scratch_general_e77_compression_audit.json")
SPECTRAL_UPPER = 4564
DISJOINT_CONSTANT = 3248


def joint_budget(state):
    numerator = SPECTRAL_UPPER - base.diagonal_square(state) - DISJOINT_CONSTANT
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
            real_lower = math.ceil(continuous)
            real_pass = (
                overlap["feasible"]
                and overlap["minimum_square"] + real_lower <= budget
            )
            disjoint = None
            integer_pass = None
            if run_integer and real_pass:
                disjoint = base.disjoint_integer_minimum(
                    state, budget - overlap["minimum_square"]
                )
                integer_pass = disjoint["status"] in ("OPTIMAL", "FEASIBLE")
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
                "disjoint_continuous_ceiling": real_lower,
                "passes_overlap_and_real_relaxation": real_pass,
                "disjoint_integer": disjoint,
                "passes_compression_square_and_BP": integer_pass,
            }
            if integer_pass:
                total_square = (
                    row["diagonal_square"] + DISJOINT_CONSTANT
                    + 2 * (overlap["minimum_square"] + disjoint["minimum_square"])
                )
                assert total_square <= SPECTRAL_UPPER
                row["verified_total_D_square"] = total_square
            rows.append(row)
    return rows, orbit_totals


def audit(run_integer):
    # Free Ritz sum 77/2: the endpoint maximizer is 3^13,-1/2.
    assert SPECTRAL_UPPER == 16 * (12**2 + 6 * 2**2 + 13 * 3**2) + 4
    rows, orbit_totals = build_rows(run_integer)
    return {
        "model": "E0=77 exact fibre-compression placement audit",
        "phase": "exact_integer_disjoint" if run_integer else "solver_free_overlap_and_real_relaxation",
        "theorem_inputs": {
            "total_deficit": 7,
            "total_fibre_edges_E0": 77,
            "spectral_D_square_upper": SPECTRAL_UPPER,
            "spectral_maximizing_free_Ritz_multiset": [3] * 13 + [-0.5],
            "trace_identity": (
                "tr(D^2)=diagonal_square+3248+2*(overlap_square+x_square)"
            ),
            "BP_overlap_row_sum": "4*delta_F",
            "disjoint_deviation_row_sum": "sum x_FG=2*delta_F for x=4-D",
        },
        "method_audit": {
            "symmetry": "all labelled placements; S7 generator orbits; full 5040 stabilizer check",
            "overlap": "solver-free exhaustive nonnegative-integer recursion",
            "disjoint_real": "exact Fraction least-norm lower bound",
            "disjoint_integer": (
                "not run" if not run_integer else
                "bounded one-worker CP-SAT, positive witnesses directly checked"
            ),
            "claim_boundary": (
                "CP-SAT infeasibility has no proof certificate" if run_integer
                else "this phase contains no solver-dependent exclusion"
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
    summary = {}
    for partition in PARTITIONS:
        selected = [row for row in result["rows"] if tuple(row["partition"]) == partition]
        summary["+".join(map(str, partition))] = {
            "orbits": len(selected),
            "overlap_feasible": sum(row["overlap"]["feasible"] for row in selected),
            "real_pass": sum(row["passes_overlap_and_real_relaxation"] for row in selected),
            "integer_pass": (
                sum(bool(row["passes_compression_square_and_BP"]) for row in selected)
                if args.integer else None
            ),
        }
    print(json.dumps({
        "phase": result["phase"],
        "total_orbits": len(result["rows"]),
        "real_passes": sum(row["passes_overlap_and_real_relaxation"] for row in result["rows"]),
        "integer_passes": (
            sum(bool(row["passes_compression_square_and_BP"]) for row in result["rows"])
            if args.integer else None
        ),
        "summary": summary,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
