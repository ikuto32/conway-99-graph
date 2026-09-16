"""Run a DIMACS instance with a selected PySAT backend.

This is a thin reproducible runner.  A SAT model is written only to the
explicit --model path; UNKNOWN is represented by externally stopping the
process, never as UNSAT.
"""

from __future__ import annotations

import argparse
import json
import time

from pysat.formula import CNF
from pysat.solvers import Solver


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("cnf")
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--model")
    args = parser.parse_args()

    started = time.monotonic()
    formula = CNF(from_file=args.cnf)
    loaded = time.monotonic()
    print(
        json.dumps(
            {
                "event": "loaded",
                "variables": formula.nv,
                "clauses": len(formula.clauses),
                "seconds": round(loaded - started, 3),
                "solver": args.solver,
            }
        ),
        flush=True,
    )
    with Solver(name=args.solver, bootstrap_with=formula.clauses) as solver:
        result = solver.solve()
        ended = time.monotonic()
        record = {
            "event": "result",
            "result": "SAT" if result else "UNSAT",
            "seconds": round(ended - started, 3),
            "solver": args.solver,
            "stats": solver.accum_stats(),
        }
        print(json.dumps(record, sort_keys=True), flush=True)
        if result and args.model:
            model = solver.get_model()
            with open(args.model, "w", encoding="utf-8") as handle:
                json.dump(
                    {
                        "cnf": args.cnf,
                        "solver": args.solver,
                        "positive_variables": [lit for lit in model if lit > 0],
                    },
                    handle,
                    indent=2,
                )
                handle.write("\n")


if __name__ == "__main__":
    main()
