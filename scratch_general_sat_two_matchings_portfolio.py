"""Persistent-worker bounded portfolio for the 445 live two-matching branches."""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import time
from pathlib import Path

from scratch_general_exact_sat import verify
from scratch_general_sat_two_matchings import make_specs


DEFAULT_OUTPUT = "scratch_general_sat_two_matchings_portfolio.json"


def worker(worker_id, cnf_path, specs, conflict_budget, out_queue):
    from pysat.formula import CNF
    from pysat.solvers import Solver

    started = time.monotonic()
    formula = CNF(from_file=cnf_path)
    loaded = time.monotonic()
    rows = []
    previous = {"restarts": 0, "conflicts": 0, "decisions": 0, "propagations": 0}
    with Solver(name="cadical300", bootstrap_with=formula.clauses) as solver:
        for spec in specs:
            before = time.monotonic()
            solver.conf_budget(conflict_budget)
            answer = solver.solve_limited(assumptions=spec["assumptions"])
            cumulative = solver.accum_stats()
            delta = {key: cumulative.get(key, 0) - previous.get(key, 0) for key in cumulative}
            previous = cumulative
            model = solver.get_model() if answer is True else None
            rows.append(
                {
                    "branch": spec["branch"],
                    "parent": spec["parent"],
                    "status": "SAT" if answer is True else "UNSAT" if answer is False else "UNKNOWN",
                    "solve_seconds": round(time.monotonic() - before, 3),
                    "stats_delta": delta,
                    "positive_edge_variables": [lit for lit in model if 0 < lit <= 3486] if model else [],
                }
            )
            if answer is True:
                break
    out_queue.put(
        {
            "worker": worker_id,
            "load_seconds": round(loaded - started, 3),
            "wall_seconds": round(time.monotonic() - started, 3),
            "records": rows,
        }
    )


def run(cnf_path, conflict_budget, max_parallel, output):
    specs, coverage = make_specs()
    screen = json.loads(Path("scratch_general_sat_two_matchings_screen.json").read_text(encoding="utf-8"))
    live = {row["branch"] for row in screen["records"] if row["status"] == "LIVE"}
    specs = [spec for spec in specs if spec["branch"] in live]
    assert len(specs) == 445
    assignments = [specs[offset::max_parallel] for offset in range(max_parallel)]
    context = mp.get_context("spawn")
    out_queue = context.Queue()
    processes = []
    for worker_id, assignment in enumerate(assignments):
        process = context.Process(
            target=worker,
            args=(worker_id, str(Path(cnf_path).resolve()), assignment, conflict_budget, out_queue),
        )
        process.start()
        processes.append(process)
    worker_rows = [out_queue.get(timeout=7200) for _ in processes]
    for process in processes:
        process.join(10)
        if process.is_alive():
            process.terminate()
            process.join(10)

    by_name = {
        row["branch"]: row
        for worker_row in worker_rows
        for row in worker_row["records"]
    }
    verified = None
    for row in by_name.values():
        if row["status"] == "SAT":
            checked = verify(set(row["positive_edge_variables"]))
            row["verification"] = {key: value for key, value in checked.items() if key != "edges"}
            if checked["ok"]:
                verified = checked
                Path("scratch_general_sat_two_matchings_solution.json").write_text(
                    json.dumps(checked, indent=2) + "\n", encoding="utf-8"
                )

    ordered = [
        by_name.get(spec["branch"], {"branch": spec["branch"], "status": "NOT_RUN_AFTER_SAT"})
        for spec in specs
    ]
    result = {
        "cnf": cnf_path,
        "solver": "CaDiCaL 3.0 via PySAT persistent workers",
        "conflict_budget_per_branch": conflict_budget,
        "max_parallel": max_parallel,
        "branch_count": len(specs),
        "branches_exhaustive_after_propagation_screen": True,
        "coverage": coverage,
        "status": "SAT" if verified is not None else "UNSAT" if all(row["status"] == "UNSAT" for row in ordered) else "UNKNOWN",
        "counts": {
            status: sum(row["status"] == status for row in ordered)
            for status in ("SAT", "UNSAT", "UNKNOWN", "NOT_RUN_AFTER_SAT")
        },
        "workers": worker_rows,
        "records": ordered,
    }
    Path(output).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("cnf")
    parser.add_argument("--conflicts", type=int, required=True)
    parser.add_argument("--max-parallel", type=int, default=2)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if not 1 <= args.max_parallel <= 4:
        parser.error("--max-parallel must be 1..4")
    result = run(args.cnf, args.conflicts, args.max_parallel, args.output)
    print(json.dumps({"status": result["status"], "counts": result["counts"]}), flush=True)


if __name__ == "__main__":
    mp.freeze_support()
    main()
