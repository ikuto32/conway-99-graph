"""Exact fibre-compression placement audit for E0=76 (deficit eight)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import scratch_general_e77_compression_audit as generic


PARTITIONS = (
    (4, 4),
    (4, 3, 1),
    (4, 2, 2),
    (4, 2, 1, 1),
    (4, 1, 1, 1, 1),
    (3, 3, 2),
    (3, 3, 1, 1),
    (3, 2, 2, 1),
    (3, 2, 1, 1, 1),
    (3, 1, 1, 1, 1, 1),
    (2, 2, 2, 2),
    (2, 2, 2, 1, 1),
    (2, 2, 1, 1, 1, 1),
    (2, 1, 1, 1, 1, 1, 1),
    (1, 1, 1, 1, 1, 1, 1, 1),
)
RESULT_PATH = Path("scratch_general_e76_compression_audit.json")
SPECTRAL_UPPER = 4576
DISJOINT_CONSTANT = 3232


def configure_generic():
    generic.PARTITIONS = PARTITIONS
    generic.SPECTRAL_UPPER = SPECTRAL_UPPER
    generic.DISJOINT_CONSTANT = DISJOINT_CONSTANT


def audit(run_integer):
    configure_generic()
    # The free Ritz sum is 38; the square-maximizer is 3^13,-1.
    assert SPECTRAL_UPPER == 16 * (12**2 + 6 * 2**2 + 13 * 3**2 + 1)
    rows, orbit_totals = generic.build_rows(run_integer)
    return {
        "model": "E0=76 exact fibre-compression placement audit",
        "phase": "exact_integer_disjoint" if run_integer else "solver_free_overlap_and_real_relaxation",
        "theorem_inputs": {
            "total_deficit": 8,
            "total_fibre_edges_E0": 76,
            "spectral_D_square_upper": SPECTRAL_UPPER,
            "spectral_maximizing_free_Ritz_multiset": [3] * 13 + [-1],
            "trace_identity": (
                "tr(D^2)=diagonal_square+3232+2*(overlap_square+x_square)"
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
