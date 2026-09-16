"""Generic bounded 26-branch sweep for a rooted exact CNF variant."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import time

from scratch_general_exact_sat import verify
from scratch_general_triangle_portfolio import branch_specs


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cnf", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--conflicts", type=int, required=True)
    parser.add_argument("--solver", default="cadical300")
    args = parser.parse_args()

    from pysat.formula import CNF
    from pysat.solvers import Solver

    path = Path(args.cnf)
    output = Path(args.output)
    specs, coverage = branch_specs()
    started = time.monotonic()
    formula = CNF(from_file=str(path))
    loaded = time.monotonic()
    records = []
    verified = None
    with Solver(name=args.solver, bootstrap_with=formula.clauses) as solver:
        for index, spec in enumerate(specs):
            before = solver.accum_stats()
            tick = time.monotonic()
            solver.conf_budget(args.conflicts)
            answer = solver.solve_limited(assumptions=spec["assumptions"])
            after = solver.accum_stats()
            record = {
                "branch_index": index,
                "branch": spec["branch"],
                "base": spec["base"],
                "w_label": spec["w_label"],
                "orbit_size": spec["orbit_size"],
                "assumptions": spec["assumptions"],
                "status": "SAT" if answer is True else "UNSAT" if answer is False else "UNKNOWN",
                "solve_seconds": round(time.monotonic() - tick, 6),
                "stats_delta": {
                    key: after.get(key, 0) - before.get(key, 0)
                    for key in set(before) | set(after)
                },
            }
            records.append(record)
            print(json.dumps(record, sort_keys=True), flush=True)
            if answer is True:
                positive = {lit for lit in solver.get_model() if 0 < lit <= 3486}
                verified = verify(positive)
                record["verification"] = {
                    key: value for key, value in verified.items() if key != "edges"
                }
                if not verified["ok"]:
                    raise AssertionError(record["verification"])
                solution_path = output.with_name(output.stem + "_solution.json")
                solution_path.write_text(json.dumps(verified, indent=2) + "\n", encoding="utf-8")
                break
            output.write_text(json.dumps({
                "status": "IN_PROGRESS", "records": records,
            }, indent=2) + "\n", encoding="utf-8")
    counts = {
        status: sum(row["status"] == status for row in records)
        for status in ("SAT", "UNSAT", "UNKNOWN")
    }
    status = (
        "SAT" if counts["SAT"] else
        "UNSAT" if len(records) == len(specs) and counts["UNSAT"] == len(specs)
        else "UNKNOWN"
    )
    result = {
        "status": status,
        "cnf": str(path),
        "cnf_sha256": digest(path),
        "solver": args.solver,
        "conflict_budget_per_branch": args.conflicts,
        "load_seconds": round(loaded - started, 6),
        "elapsed_seconds": round(time.monotonic() - started, 6),
        "branches_exhaustive": True,
        "coverage": coverage,
        "counts": counts,
        "records": records,
        "claim_boundary": (
            "SAT is accepted only after direct verification. Solver-terminal UNSAT "
            "records have no independently checked proof certificates."
        ),
    }
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "counts": counts}), flush=True)


if __name__ == "__main__":
    main()
