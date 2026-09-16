"""Independent-backend solve check for the fixed-rep6 exact DIMACS file."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import time


CNF_PATH = Path("scratch_fibre_e78_rep6_exact.cnf")
BUILD_PATH = Path("scratch_fibre_e78_rep6_exact_build.json")
MAP_PATH = Path("scratch_fibre_e78_rep6_exact_map.json")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--solver", default="cadical300")
    args = parser.parse_args()
    output = Path(f"scratch_fibre_e78_rep6_exact_crosscheck_{args.solver}.json")

    from pysat.formula import CNF
    from pysat.solvers import Solver

    raw = CNF_PATH.read_bytes()
    digest = hashlib.sha256(raw).hexdigest().upper()
    build = json.loads(BUILD_PATH.read_text(encoding="utf-8"))
    assert digest == build["cnf_sha256"]
    phase_data = json.loads(MAP_PATH.read_text(encoding="utf-8"))

    started = time.monotonic()
    formula = CNF(from_file=str(CNF_PATH))
    loaded = time.monotonic()
    with Solver(name=args.solver, bootstrap_with=formula.clauses) as solver:
        del formula
        solver.set_phases(phase_data["seed_edge_phases"])
        solve_started = time.monotonic()
        answer = solver.solve()
        solved = time.monotonic()
        stats = solver.accum_stats()
        model = solver.get_model() if answer else None
    record = {
        "solver": args.solver,
        "status": "SAT" if answer is True else "UNSAT",
        "phase": "all 1680 disjoint-support primary variables from audited energy-3148 seed",
        "cnf_sha256": digest,
        "variables": build["primary_plus_aux_variables"],
        "clauses": build["clauses"],
        "load_seconds": round(loaded - started, 3),
        "solve_seconds": round(solved - solve_started, 3),
        "wall_seconds": round(solved - started, 3),
        "stats": stats,
        "positive_model_literals": sum(lit > 0 for lit in model or []),
    }
    output.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record), flush=True)


if __name__ == "__main__":
    main()
