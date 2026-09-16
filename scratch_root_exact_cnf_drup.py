"""Emit a proof from an already hash-bound terminal exact-CNF checkpoint."""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import sys
import time


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cnf", type=Path, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--prefix", type=Path, required=True)
    parser.add_argument("--model-label", required=True)
    parser.add_argument("--solver", default="cadical195")
    args = parser.parse_args()

    dependency_root = str(Path(".deps").resolve())
    if dependency_root not in sys.path:
        sys.path.insert(0, dependency_root)
    import pysat.solvers as solver_module
    from pysat.formula import CNF
    from pysat.solvers import Solver

    checkpoint = json.loads(args.checkpoint.read_text(encoding="utf-8"))
    assert checkpoint["status"] == "UNSAT"
    if "termination" in checkpoint:
        assert checkpoint["termination"] == "solver_answer"
    else:
        assert checkpoint.get("checkpoint_complete") is True
        assert checkpoint.get("unknown") == checkpoint.get("sat") == 0
        assert checkpoint.get("records")
        assert all(row["status"] == "UNSAT" for row in checkpoint["records"])
    assert checkpoint["cnf_sha256"] == sha256(args.cnf)
    started = time.monotonic()
    formula = CNF(from_file=str(args.cnf))
    loaded = time.monotonic()
    solver = Solver(name=args.solver, bootstrap_with=formula.clauses, with_proof=True)
    answer = solver.solve()
    solved = time.monotonic()
    stats = solver.accum_stats()

    engine = solver.solver
    binary_proof = False
    if os.name == "nt":
        c_stdio_flush_return = ctypes.CDLL("ucrtbase.dll").fflush(None)
    else:
        c_stdio_flush_return = ctypes.CDLL(None).fflush(None)
    assert c_stdio_flush_return == 0
    if args.solver == "cadical195":
        solver_module.pysolvers.cadical195_del(engine.cadical, engine.prfile)
        engine.cadical = None
        binary_proof = True
    elif args.solver == "glucose4":
        solver_module.pysolvers.glucose41_del(engine.glucose)
        engine.glucose = None
    elif args.solver == "glucose42":
        solver_module.pysolvers.glucose421_del(engine.glucose)
        engine.glucose = None
    else:
        raise ValueError("proof-safe finalization is implemented only for cadical195/glucose4/glucose42")
    engine.prfile.seek(0)
    raw_proof = engine.prfile.read()
    if answer is False and binary_proof:
        proof = Solver._proof_bin2text(bytearray(raw_proof).strip())
    elif answer is False:
        proof = [line.rstrip().decode("ascii") for line in raw_proof.splitlines()]
    else:
        proof = None
    engine.prfile.close()
    engine.prfile = None
    solver.delete()
    assert answer is False and proof is not None
    terminal_empty_clause_present = any(line.strip() == "0" for line in proof)

    proof_path = args.prefix.with_suffix(".drup")
    meta_path = args.prefix.with_suffix(".json")
    temporary = proof_path.with_suffix(proof_path.suffix + f".{os.getpid()}.tmp")
    with temporary.open("w", encoding="ascii", newline="\n") as handle:
        for line in proof:
            handle.write(line.rstrip() + "\n")
    temporary.replace(proof_path)
    result = {
        "status": "UNSAT_PROOF_EMITTED_UNCHECKED",
        "model": args.model_label,
        "cnf": str(args.cnf),
        "cnf_sha256": sha256(args.cnf),
        "checkpoint": str(args.checkpoint),
        "checkpoint_sha256": sha256(args.checkpoint),
        "variables": formula.nv,
        "clauses": len(formula.clauses),
        "solver": args.solver,
        "solver_stats": stats,
        "c_stdio_flush_return": c_stdio_flush_return,
        "parse_seconds": round(loaded - started, 6),
        "solve_seconds": round(solved - loaded, 6),
        "proof": str(proof_path),
        "proof_sha256": sha256(proof_path),
        "proof_lines": len(proof),
        "terminal_empty_clause_present": terminal_empty_clause_present,
        "terminal_empty_clause_appended_for_external_check": False,
        "proof_checked": False,
    }
    meta_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "variables": result["variables"],
        "clauses": result["clauses"],
        "solve_seconds": result["solve_seconds"],
        "proof_lines": result["proof_lines"],
        "terminal_empty_clause_present": result["terminal_empty_clause_present"],
    }, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
