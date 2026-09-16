"""Independent OR-Tools cross-check of the three exact E0=77 local lifts."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from scratch_general_e77_exact_sat import source_record
from scratch_general_e78_k23_cpsat import make_model


RESULT_PATH = Path("scratch_general_e77_exact_cpsat.json")


def main():
    from ortools.sat.python import cp_model

    parser = argparse.ArgumentParser()
    parser.add_argument("--seconds", type=float, default=60)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    source = source_record()
    assert source["orbit_count_direct"] == 3
    records = []
    for branch_index in range(3):
        started = time.monotonic()
        model, meta = make_model(
            branch_index, support_form="E77-orbit22", source_override=source
        )
        built = time.monotonic()
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = args.seconds
        solver.parameters.num_search_workers = args.workers
        status = solver.Solve(model)
        records.append({
            "branch_index": branch_index,
            "status": solver.StatusName(status),
            "build_seconds": round(built - started, 3),
            "solve_seconds": round(time.monotonic() - built, 3),
            "meta": meta,
            "branches": solver.NumBranches(),
            "conflicts": solver.NumConflicts(),
        })
        print(json.dumps({
            "branch": branch_index,
            "status": records[-1]["status"],
            "solve_seconds": records[-1]["solve_seconds"],
        }), flush=True)
    result = {
        "model": "independent OR-Tools exact compact E0=77 cross-check",
        "seconds_per_branch": args.seconds,
        "workers": args.workers,
        "coverage_source": "scratch_root_e77_local.json",
        "local_orbit_sizes": source["orbit_sizes"],
        "status": (
            "INFEASIBLE"
            if all(row["status"] == "INFEASIBLE" for row in records)
            else "UNKNOWN"
        ),
        "records": records,
    }
    RESULT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "counts": {
            value: sum(row["status"] == value for row in records)
            for value in ("INFEASIBLE", "UNKNOWN", "MODEL_INVALID")
        },
    }), flush=True)


if __name__ == "__main__":
    main()
