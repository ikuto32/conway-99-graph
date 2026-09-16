"""Build a selector cover for one E73 support record and emit a DRUP proof.

For branch i, the audited checkpoint supplies an UNSAT assumption core C_i
contained in the complete local assignment A_i.  Introduce selector s_i,
impose (s_i -> literal) for every literal in C_i, and require at least one
selector.  UNSAT of this single formula certifies every A_i at once.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import time

from scratch_incremental_local_exact_sat import build_shared_cnf, normalize_source


INPUT = Path("scratch_general_e73_q4_incremental_snapshot_002_records.json")
CHECKPOINTS = (
    Path("scratch_general_e73_q4_snapshot001_record00_sat.json"),
    Path("scratch_general_e73_q4_snapshot001_record01_sat.json"),
    Path("scratch_general_e73_q4_snapshot002_record02_sat.json"),
    Path("scratch_general_e73_q4_snapshot002_record03_sat.json"),
    Path("scratch_general_e73_q4_snapshot002_record04_sat.json"),
    Path("scratch_general_e73_q4_snapshot002_record05_sat.json"),
)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def write_cnf(path, variables, clauses):
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="ascii", newline="\n") as handle:
        handle.write(f"p cnf {variables} {len(clauses)}\n")
        for clause in clauses:
            handle.write(" ".join(map(str, clause)) + " 0\n")
    temporary.replace(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--record-index", type=int, required=True)
    parser.add_argument("--prefix", required=True)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--input", type=Path, default=INPUT)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument(
        "--model-label",
        default="selector-core cover of one E73,Q>=4 support record",
    )
    args = parser.parse_args()
    if args.record_index < 0:
        parser.error("record index out of range")
    if args.checkpoint is None and args.record_index >= len(CHECKPOINTS):
        parser.error("record index out of range for the default checkpoints")

    import pysat.solvers as solver_module
    from pysat.solvers import Solver

    started = time.monotonic()
    input_path = args.input
    checkpoint_path = args.checkpoint or CHECKPOINTS[args.record_index]
    source = normalize_source(input_path, args.record_index)
    clauses, _edge, _local, _full, branches, shared_meta = build_shared_cnf(source)
    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    records = checkpoint["records"]
    assert checkpoint["status"] == "UNSAT" and checkpoint["checkpoint_complete"]
    assert len(records) == len(branches)

    selector_first = shared_meta["variables"] + 1
    selectors = list(range(selector_first, selector_first + len(branches)))
    clauses.append(selectors)
    distinct_cores = set()
    implication_count = 0
    for index, (branch, record, selector) in enumerate(zip(branches, records, selectors)):
        assert branch["branch_index"] == record["branch_index"] == index
        assumptions = frozenset(branch["assumptions"])
        core = tuple(record["assumption_core"])
        assert core and len(core) == len(set(core)) and set(core) <= assumptions
        distinct_cores.add(tuple(sorted(core)))
        for literal in core:
            clauses.append([-selector, literal])
            implication_count += 1

    prefix = Path(args.prefix)
    cnf_path = prefix.with_suffix(".cnf")
    proof_path = prefix.with_suffix(".drup")
    meta_path = prefix.with_suffix(".json")
    variables = selectors[-1]
    write_cnf(cnf_path, variables, clauses)
    built = time.monotonic()
    solver = Solver(name=args.solver, bootstrap_with=clauses, with_proof=True)
    answer = solver.solve()
    solved = time.monotonic()
    stats = solver.accum_stats()
    # These solvers flush their C stdio proof streams only when the native
    # solver is deleted.  PySAT's public get_proof() reads before that flush,
    # while its public delete() immediately closes the temporary file.  Finalize
    # the native object first, then read the still-open file handle explicitly.
    engine = solver.solver
    binary_proof = False
    if os.name == "nt":
        # Glucose leaves the last stdio buffer (often including the empty
        # clause) pending after solve().  Flush the UCRT used by the PySAT
        # extension before touching the Python temporary-file handle.
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
        raise ValueError(
            "proof-safe explicit finalization is implemented only for "
            "cadical195, glucose4, and glucose42"
        )
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
    # Never synthesize an empty clause: a solver status is not a proof.  The
    # external checker must be able to derive a terminal empty clause actually
    # emitted by the proof-producing solver.
    terminal_empty_clause_present = any(line.strip() == "0" for line in proof)
    temporary = proof_path.with_suffix(proof_path.suffix + ".tmp")
    with temporary.open("w", encoding="ascii", newline="\n") as handle:
        for line in proof:
            handle.write(line.rstrip() + "\n")
    temporary.replace(proof_path)
    result = {
        "status": "UNSAT_PROOF_EMITTED_UNCHECKED",
        "model": args.model_label,
        "record_index": args.record_index,
        "input": str(input_path),
        "input_sha256": sha256(input_path),
        "checkpoint": str(checkpoint_path),
        "checkpoint_sha256": sha256(checkpoint_path),
        "branches_covered": len(branches),
        "labelled_local_graphs_covered": sum(record["orbit_size"] for record in records),
        "selectors": len(selectors),
        "distinct_assumption_cores": len(distinct_cores),
        "selector_core_implications": implication_count,
        "shared_variables": shared_meta["variables"],
        "variables": variables,
        "clauses": len(clauses),
        "solver": args.solver,
        "solver_stats": stats,
        "c_stdio_flush_return": c_stdio_flush_return,
        "build_seconds": round(built - started, 6),
        "solve_seconds": round(solved - built, 6),
        "proof_lines": len(proof),
        "terminal_empty_clause_present": terminal_empty_clause_present,
        "terminal_empty_clause_appended_for_external_check": False,
        "cnf": str(cnf_path),
        "cnf_sha256": sha256(cnf_path),
        "proof": str(proof_path),
        "proof_sha256": sha256(proof_path),
        "proof_checked": False,
        "logical_bridge": (
            "If shared CNF plus complete assignment A_i were satisfiable, set "
            "selector s_i=true and all other selectors false. Since audited "
            "core C_i is a subset of A_i, this would satisfy the selector CNF, "
            "contradicting its certified UNSAT."
        ),
    }
    meta_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
