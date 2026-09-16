"""Cross-check v2 WLOG scaffolds against the original cell-level CNF.

This intentionally keeps the 16-clause one-hot equality gadgets and both
sign-balance equations from scratch_canonical_blocksat.py.  Only the d-variable
scaffold clauses are copied from v2.  It therefore checks that the fast UNSAT
result is not an artefact of the new output-bit gadgets.
"""

from __future__ import annotations

import argparse
import json
import time

from pysat.solvers import Solver

from scratch_canonical_blocksat import build as build_original
from scratch_canonical_v2_sat import build as build_v2


BRANCHES = ("d8_qd8", "d8_qnond8", "nond8_q1", "nond8_q2")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--branch", choices=BRANCHES, required=True)
    ap.add_argument("--conflicts", type=int, default=1_000_000)
    args = ap.parse_args()

    old, old_dvar, old_meta = build_original("full")
    plain, plain_dvar, _ = build_v2("matching", "none", lex=False)
    fixed, fixed_dvar, _ = build_v2("matching", args.branch, lex=False)
    assert old_dvar == plain_dvar == fixed_dvar
    base = {tuple(clause) for clause in plain.clauses}
    scaffold = [clause for clause in fixed.clauses if tuple(clause) not in base]
    assert scaffold and all(abs(lit) <= 1680 for cl in scaffold for lit in cl)
    old.clauses.extend(scaffold)

    t0 = time.time()
    with Solver(name="cadical195", bootstrap_with=old.clauses) as solver:
        solver.conf_budget(args.conflicts)
        answer = solver.solve_limited()
        stats = solver.accum_stats()
    result = {
        "branch": args.branch,
        "encoding": "original 16-clause cell equality + v2 d-only scaffold",
        "variables": old.nvars,
        "clauses": len(old.clauses),
        "scaffold_clauses": len(scaffold),
        "status": "SAT" if answer is True else "UNSAT" if answer is False else "UNKNOWN",
        "seconds": round(time.time() - t0, 3),
        "solver_stats": stats,
        "original_meta": old_meta,
    }
    print(json.dumps(result, indent=2, sort_keys=True), flush=True)
    with open(f"scratch_canonical_v2_crosscheck_{args.branch}.json", "w",
              encoding="utf-8") as f:
        json.dump(result, f, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
