"""Incremental per-selector sweep of a built E72 full-Gram macro CNF."""

from __future__ import annotations

import argparse
from collections import Counter
import json
import os
from pathlib import Path
import sys
import time

from scratch_general_exact_sat import verify


def atomic_json(path: Path, value) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def delta(before, after):
    return {
        key: int(after.get(key, 0)) - int(before.get(key, 0))
        for key in sorted(set(before) | set(after))
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-row-index", type=int, required=True)
    parser.add_argument("--conflicts", type=int, default=100_000)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--order", choices=("catalog", "small-coverage", "large-coverage"),
        default="catalog",
    )
    args = parser.parse_args()
    dependency_root = str(Path(".deps").resolve())
    if dependency_root not in sys.path:
        sys.path.insert(0, dependency_root)
    from pysat.formula import CNF
    from pysat.solvers import Solver

    build_path = Path(
        f"scratch_root_e72_source{args.source_row_index}_full_gram_macro_build.json"
    )
    build = json.loads(build_path.read_text(encoding="utf-8"))
    branches = list(build["branches"])
    if args.order != "catalog":
        branches.sort(
            key=lambda row: row["labelled_state_matching_coverage"],
            reverse=args.order == "large-coverage",
        )
    selectors = tuple(int(row["selector"]) for row in build["branches"])
    assert len(selectors) == len(set(selectors))
    output = args.output or Path(
        f"scratch_root_e72_source{args.source_row_index}_branch_sweep_c{args.conflicts}.json"
    )
    started = time.monotonic()
    formula = CNF(from_file=build["cnf"])
    loaded = time.monotonic()
    records = []
    solution = None
    with Solver(name="cadical195", bootstrap_with=formula.clauses) as solver:
        solver_loaded = time.monotonic()
        for branch in branches:
            selector = int(branch["selector"])
            assumptions = [
                value if value == selector else -value for value in selectors
            ]
            before = solver.accum_stats()
            branch_started = time.monotonic()
            if args.conflicts:
                solver.conf_budget(args.conflicts)
                answer = solver.solve_limited(
                    assumptions=assumptions, expect_interrupt=True
                )
            else:
                answer = solver.solve(assumptions=assumptions)
            after = solver.accum_stats()
            status = "SAT" if answer is True else "UNSAT" if answer is False else "UNKNOWN"
            record = {
                "macro_branch_index": branch["macro_branch_index"],
                "state_orbit_number": branch["state_orbit_number"],
                "signature_stabilizer_orbit_number": branch["signature_stabilizer_orbit_number"],
                "Q": branch["Q"],
                "coverage": branch["labelled_state_matching_coverage"],
                "status": status,
                "solve_seconds": round(time.monotonic() - branch_started, 6),
                "stats_delta": delta(before, after),
            }
            if answer is False:
                core = solver.get_core() or []
                assert core and set(core) <= set(assumptions)
                record["assumption_core"] = core
            elif answer is True:
                model = solver.get_model()
                positive = {literal for literal in model if 0 < literal <= 3486}
                checked = verify(positive)
                record["direct_99_vertex_verification"] = {
                    key: value for key, value in checked.items() if key != "edges"
                }
                assert checked["ok"]
                solution = checked
            records.append(record)
            result = {
                "status": "SAT" if solution else "IN_PROGRESS",
                "source_row_index": args.source_row_index,
                "build": str(build_path),
                "cnf": build["cnf"],
                "solver": "CaDiCaL 1.9.5 via PySAT assumptions",
                "conflict_budget_per_branch": args.conflicts or None,
                "parse_seconds": round(loaded - started, 6),
                "solver_load_seconds": round(solver_loaded - loaded, 6),
                "completed": len(records),
                "branches": len(branches),
                "counts": dict(Counter(row["status"] for row in records)),
                "records": records,
            }
            atomic_json(output, result)
            print(json.dumps({
                "branch": record["macro_branch_index"],
                "Q": record["Q"],
                "status": status,
                "seconds": record["solve_seconds"],
                "conflicts": record["stats_delta"].get("conflicts", 0),
            }), flush=True)
            if solution:
                atomic_json(
                    Path(f"scratch_root_e72_source{args.source_row_index}_verified_solution.json"),
                    solution,
                )
                break
    complete = len(records) == len(branches) or solution is not None
    result["status"] = (
        "SAT" if solution else "UNSAT"
        if complete and all(row["status"] == "UNSAT" for row in records)
        else "UNKNOWN" if complete else "IN_PROGRESS"
    )
    result["excluded_coverage"] = sum(
        row["coverage"] for row in records if row["status"] == "UNSAT"
    )
    result["claim_boundary"] = (
        "Per-branch solver UNSAT is computational until a checked proof is emitted."
    )
    atomic_json(output, result)
    print(json.dumps({
        "status": result["status"],
        "counts": result["counts"],
        "excluded_coverage": result["excluded_coverage"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
