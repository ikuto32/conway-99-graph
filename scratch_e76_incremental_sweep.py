"""Run the ten normalized E76 support records with durable checkpoints.

Each support record gets its own JSON file.  The exact solver updates that
file after every local representative, so an interrupted record can be
continued with ``--resume``.  Completed record files are skipped.  A compact
master checkpoint is refreshed after every support record.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from scratch_incremental_local_exact_sat import (
    atomic_write_json,
    normalize_source,
    solve_incrementally,
)


INPUT = Path("scratch_e76_incremental_records.json")
MASTER = Path("scratch_e76_incremental_sweep.json")


def record_path(index):
    return Path(f"scratch_e76_incremental_record_{index:02d}.json")


def read_record_summary(index):
    path = record_path(index)
    if not path.exists():
        return {
            "record_index": index,
            "path": str(path),
            "status": "NOT_STARTED",
            "completed": 0,
            "total": None,
        }
    document = json.loads(path.read_text(encoding="utf-8"))
    solve_seconds = sum(
        float(row.get("solve_seconds", 0)) for row in document.get("records", [])
    )
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
        "total_solve_seconds": round(solve_seconds, 6),
    }


def update_master(input_path, conflict_budget):
    rows = [read_record_summary(index) for index in range(10)]
    completed_records = sum(bool(row.get("checkpoint_complete")) for row in rows)
    completed_representatives = sum(row.get("completed", 0) for row in rows)
    total_representatives = sum(row.get("total") or 0 for row in rows)
    result = {
        "model": "E76 incremental local exact-SAT sweep checkpoint",
        "input": str(input_path),
        "conflict_budget_per_branch": conflict_budget,
        "support_record_count": 10,
        "completed_support_record_count": completed_records,
        "completed_representative_count": completed_representatives,
        "known_total_representative_count": total_representatives,
        "expected_total_representative_count": 311,
        "total_solve_seconds": round(sum(
            row.get("total_solve_seconds", 0) for row in rows
        ), 6),
        "status": (
            "SAT" if any(row["status"] == "SAT" for row in rows)
            else "UNSAT" if completed_records == 10 and all(
                row["status"] == "UNSAT" for row in rows
            )
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
    parser.add_argument("--stop", type=int, default=10)
    parser.add_argument("--conflict-budget", type=int, default=200_000)
    args = parser.parse_args()
    if not (0 <= args.start <= args.stop <= 10):
        raise ValueError("require 0 <= start <= stop <= 10")

    for index in range(args.start, args.stop):
        path = record_path(index)
        previous = None
        if path.exists():
            previous = json.loads(path.read_text(encoding="utf-8"))
        if previous and previous.get("checkpoint_complete"):
            print(json.dumps({
                "event": "record_skip_complete",
                "record_index": index,
                "status": previous["status"],
            }), flush=True)
            update_master(args.input, args.conflict_budget)
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
            "event": "record_complete",
            "record_index": index,
            "record_status": result["status"],
            "sweep_status": master["status"],
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
                "event": "verified_sat_stop",
                "record_index": index,
                "branch_indices": [row["branch_index"] for row in verified],
            }), flush=True)
            break

    final = update_master(args.input, args.conflict_budget)
    print(json.dumps({
        "event": "sweep_yield",
        "status": final["status"],
        "completed_records": final["completed_support_record_count"],
        "completed_representatives": final["completed_representative_count"],
    }, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
