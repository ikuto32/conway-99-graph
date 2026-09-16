"""Run a bounded alternate PySAT backend on an existing exact CNF."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import time

from scratch_general_exact_sat import verify


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def atomic_json(path: Path, value) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cnf", type=Path, required=True)
    parser.add_argument("--solver", required=True)
    parser.add_argument("--conflicts", type=int, default=1_000_000)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--lean-source-row-index", type=int)
    args = parser.parse_args()
    dependency_root = str(Path(".deps").resolve())
    if dependency_root not in sys.path:
        sys.path.insert(0, dependency_root)
    from pysat.formula import CNF
    from pysat.solvers import Solver

    started = time.monotonic()
    formula = CNF(from_file=str(args.cnf))
    parsed = time.monotonic()
    with Solver(name=args.solver, bootstrap_with=formula.clauses) as solver:
        loaded = time.monotonic()
        if args.conflicts:
            solver.conf_budget(args.conflicts)
            answer = solver.solve_limited(expect_interrupt=True)
        else:
            answer = solver.solve()
        solved = time.monotonic()
        try:
            stats = solver.accum_stats()
        except NotImplementedError:
            stats = {"unavailable": True}
        model = solver.get_model() if answer is True else None
    status = "SAT" if answer is True else "UNSAT" if answer is False else "UNKNOWN"
    verification = None
    if model is not None:
        if args.lean_source_row_index is None:
            positive = {literal for literal in model if 0 < literal <= 3486}
        else:
            from scratch_root_e72_full_gram_macro_lean_sat import translate_sat_model
            positive = translate_sat_model(args.lean_source_row_index, model)
        verification = verify(positive)
        assert verification["ok"]
        atomic_json(args.output.with_name(args.output.stem + "_solution.json"), verification)
    result = {
        "status": status,
        "cnf": str(args.cnf),
        "cnf_sha256": sha256(args.cnf),
        "declared_variables": formula.nv,
        "clauses": len(formula.clauses),
        "solver": args.solver,
        "conflict_budget": args.conflicts or None,
        "parse_seconds": round(parsed - started, 6),
        "solver_load_seconds": round(loaded - parsed, 6),
        "solve_seconds": round(solved - loaded, 6),
        "solver_stats": stats,
        "lean_source_row_index": args.lean_source_row_index,
        "direct_99_vertex_verification": (
            None if verification is None
            else {key: value for key, value in verification.items() if key != "edges"}
        ),
        "formal_proof_certificate": None,
        "claim_boundary": "A negative result is computational until a proof is checked.",
    }
    atomic_json(args.output, result)
    print(json.dumps({
        "status": status,
        "solver": args.solver,
        "solve_seconds": result["solve_seconds"],
        "stats": stats,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
