"""Sequential, resumable sweep of the six normalized E75 support records."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from scratch_incremental_local_exact_sat import (
    atomic_write_json,
    normalize_source,
    solve_incrementally,
)


INPUT = Path("scratch_general_e75_incremental_records.json")
MASTER = Path("scratch_e75_incremental_sweep.json")
RECORD_COUNT = 6
EXPECTED_REPRESENTATIVES = 352


def record_path(index):
    # Records 1--3 were completed by the independent general worker before
    # this sequential sweep reached them.  Adopt those immutable checkpoints
    # instead of copying or rewriting them.
    if index in (1, 2, 3):
        return Path(f"scratch_general_e75_incremental_record_{index:02d}.json")
    return Path(f"scratch_e75_incremental_record_{index:02d}.json")


def record_summary(index):
    path = record_path(index)
    if not path.exists():
        return {
            "record_index": index, "path": str(path), "status": "NOT_STARTED",
            "checkpoint_complete": False, "completed": 0, "total": None,
            "direct_solver_calls": 0, "direct_solver_unsat_count": 0,
            "core_covered_unsat_count": 0, "unknown_count": 0,
            "sat_count": 0, "total_solve_seconds": 0,
        }
    document = json.loads(path.read_text(encoding="utf-8"))
    records = document.get("records", [])
    return {
        "record_index": index,
        "path": str(path),
        "support_form": document.get("support_form"),
        "status": document.get("status", "BUILD_ONLY"),
        "checkpoint_complete": document.get("checkpoint_complete", False),
        "completed": document.get("completed_branch_count", 0),
        "total": document.get("shared_cnf_meta", {}).get("representative_count"),
        "direct_solver_calls": document.get("direct_solver_calls", 0),
        "direct_solver_unsat_count": document.get("direct_solver_unsat_count", 0),
        "core_covered_unsat_count": document.get("core_covered_unsat_count", 0),
        "unknown_count": document.get("unknown_count", 0),
        "sat_count": sum(row.get("status") == "SAT" for row in records),
        "conflict_budget_per_branch": document.get("conflict_budget_per_branch"),
        "total_solve_seconds": round(sum(
            float(row.get("solve_seconds", 0)) for row in records
        ), 6),
    }


def update_master(input_path, conflict_budget):
    rows = [record_summary(index) for index in range(RECORD_COUNT)]
    completed_records = sum(bool(row["checkpoint_complete"]) for row in rows)
    result = {
        "model": "E75 incremental local exact-SAT sweep checkpoint",
        "input": str(input_path),
        "requested_conflict_budget_per_branch": conflict_budget,
        "budget_note": (
            "records 1--3 are adopted complete checkpoints that terminated UNSAT "
            "under 100000 conflicts; records 0,4,5 used the requested 200000"
        ),
        "support_record_count": RECORD_COUNT,
        "completed_support_record_count": completed_records,
        "completed_representative_count": sum(row["completed"] for row in rows),
        "known_total_representative_count": sum(row["total"] or 0 for row in rows),
        "expected_total_representative_count": EXPECTED_REPRESENTATIVES,
        "total_solve_seconds": round(sum(row["total_solve_seconds"] for row in rows), 6),
        "status": (
            "SAT" if any(row["sat_count"] for row in rows)
            else "UNSAT" if completed_records == RECORD_COUNT and all(
                row["status"] == "UNSAT" for row in rows
            )
            else "UNKNOWN" if completed_records == RECORD_COUNT
            else "IN_PROGRESS"
        ),
        "records": rows,
    }
    atomic_write_json(MASTER, result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=INPUT)
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--stop", type=int, default=RECORD_COUNT)
    parser.add_argument("--conflict-budget", type=int, default=200_000)
    args = parser.parse_args()
    if not (0 <= args.start <= args.stop <= RECORD_COUNT):
        raise ValueError(f"require 0 <= start <= stop <= {RECORD_COUNT}")

    for index in range(args.start, args.stop):
        path = record_path(index)
        previous = json.loads(path.read_text(encoding="utf-8")) if path.exists() else None
        if previous and previous.get("checkpoint_complete"):
            print(json.dumps({
                "event": "record_skip_complete", "record_index": index,
                "status": previous["status"],
            }), flush=True)
            update_master(args.input, args.conflict_budget)
            if previous["status"] == "SAT" and any(
                row.get("verified_srg") for row in previous.get("records", [])
            ):
                break
            continue

        source = normalize_source(args.input, index)
        result = solve_incrementally(
            source,
            conflict_budget=max(0, args.conflict_budget),
            checkpoint_path=path,
            resume=bool(previous and previous.get("support_form")),
        )
        atomic_write_json(path, result)
        master = update_master(args.input, args.conflict_budget)
        print(json.dumps({
            "event": "record_complete", "record_index": index,
            "record_status": result["status"], "sweep_status": master["status"],
            "direct_solver_calls": result["direct_solver_calls"],
            "core_covered_unsat_count": result["core_covered_unsat_count"],
            "unknown_count": result["unknown_count"],
        }, sort_keys=True), flush=True)
        verified = [
            row for row in result["records"]
            if row["status"] == "SAT" and row.get("verified_srg")
        ]
        if verified:
            print(json.dumps({
                "event": "verified_sat_stop", "record_index": index,
                "branch_indices": [row["branch_index"] for row in verified],
            }), flush=True)
            break

    final = update_master(args.input, args.conflict_budget)
    print(json.dumps({
        "event": "sweep_yield", "status": final["status"],
        "completed_records": final["completed_support_record_count"],
        "completed_representatives": final["completed_representative_count"],
    }, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
