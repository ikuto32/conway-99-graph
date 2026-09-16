"""Reproducible conflict-budget runner for rooted general SAT encodings."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from scratch_general_triangle_portfolio import branch_specs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("cnf")
    parser.add_argument("branch")
    parser.add_argument("--conflicts", type=int, required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--solver", default="cadical195")
    args = parser.parse_args()

    from pysat.formula import CNF
    from pysat.solvers import Solver

    specs, _coverage = branch_specs()
    matches = [spec for spec in specs if spec["branch"] == args.branch]
    if len(matches) != 1:
        raise ValueError(f"unknown/nonunique branch: {args.branch}")
    spec = matches[0]

    started = time.monotonic()
    formula = CNF(from_file=args.cnf)
    loaded = time.monotonic()
    with Solver(name=args.solver, bootstrap_with=formula.clauses) as solver:
        solver.conf_budget(args.conflicts)
        answer = solver.solve_limited(assumptions=spec["assumptions"])
        model = solver.get_model() if answer is True else None
        stats = solver.accum_stats()
    ended = time.monotonic()
    result = {
        "cnf": str(Path(args.cnf)),
        "branch": args.branch,
        "solver": args.solver,
        "conflict_budget": args.conflicts,
        "status": "SAT" if answer is True else "UNSAT" if answer is False else "UNKNOWN",
        "load_seconds": round(loaded - started, 3),
        "solve_seconds": round(ended - loaded, 3),
        "stats": stats,
        "positive_edge_variables": [lit for lit in model if 0 < lit <= 3486] if model else [],
    }
    Path(args.output).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
