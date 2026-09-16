"""Emit an externally checkable DRUP proof for source-133 macro 4."""

from __future__ import annotations

import ctypes
import hashlib
import json
import os
import shutil
import sys
import time
from pathlib import Path


BUILD = Path("scratch_root_e72_source133_full_gram_macro_build.json")
SWEEP = Path("scratch_root_e72_source133_branch_sweep_c100000.json")
CNF_OUTPUT = Path("scratch_root_e72_source133_macro4.cnf")
PROOF_OUTPUT = Path("scratch_root_e72_source133_macro4.drup")
META_OUTPUT = Path("scratch_root_e72_source133_macro4_drup.json")


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def read_header(path):
    with Path(path).open("rb") as handle:
        fields = handle.readline().split()
    assert fields[:2] == [b"p", b"cnf"] and len(fields) == 4
    return int(fields[2]), int(fields[3])


def main():
    dependency_root = str(Path(".deps").resolve())
    if dependency_root not in sys.path:
        sys.path.insert(0, dependency_root)
    import pysat.solvers as solver_module
    from pysat.formula import CNF
    from pysat.solvers import Solver

    started = time.monotonic()
    build = json.loads(BUILD.read_text(encoding="utf-8"))
    sweep = json.loads(SWEEP.read_text(encoding="utf-8"))
    assert build["source_row_index"] == sweep["source_row_index"] == 133
    source_cnf = Path(build["cnf"])
    assert sha256(source_cnf) == build["cnf_audit"]["sha256"]
    record = next(row for row in sweep["records"]
                  if row["state_orbit_number"] == 4)
    assert record["status"] == "UNSAT" and record["coverage"] == 12_288
    branches = build["branches"]
    selectors = [row["selector"] for row in branches]
    assert selectors == list(range(817_279, 817_284))
    core = tuple(record["assumption_core"])
    assert core == tuple(-selector for selector in selectors[:4])
    assert selectors[4] not in set(map(abs, core))

    variables, source_clauses = read_header(source_cnf)
    assert variables == build["cnf_audit"]["declared_variables"]
    assert source_clauses == build["cnf_audit"]["declared_clauses"]
    temporary_cnf = CNF_OUTPUT.with_suffix(CNF_OUTPUT.suffix + f".{os.getpid()}.tmp")
    with source_cnf.open("rb") as source, temporary_cnf.open("wb") as target:
        source_header = source.readline().split()
        assert source_header == [
            b"p", b"cnf", str(variables).encode(), str(source_clauses).encode()
        ]
        target.write(f"p cnf {variables} {source_clauses + len(core)}\n".encode())
        shutil.copyfileobj(source, target, length=1 << 20)
        for literal in core:
            target.write(f"{literal} 0\n".encode())
    temporary_cnf.replace(CNF_OUTPUT)
    assert read_header(CNF_OUTPUT) == (variables, source_clauses + len(core))
    built = time.monotonic()

    formula = CNF(from_file=str(CNF_OUTPUT))
    assert formula.nv == variables and len(formula.clauses) == source_clauses + len(core)
    solver = Solver(name="cadical195", bootstrap_with=formula.clauses, with_proof=True)
    answer = solver.solve()
    solved = time.monotonic()
    stats = solver.accum_stats()
    engine = solver.solver
    flush_return = ctypes.CDLL("ucrtbase.dll").fflush(None)
    assert flush_return == 0
    solver_module.pysolvers.cadical195_del(engine.cadical, engine.prfile)
    engine.cadical = None
    engine.prfile.seek(0)
    raw_proof = engine.prfile.read()
    proof = Solver._proof_bin2text(bytearray(raw_proof).strip()) if answer is False else None
    engine.prfile.close()
    engine.prfile = None
    solver.delete()
    assert answer is False and proof is not None
    assert any(line.strip() == "0" for line in proof)
    temporary_proof = PROOF_OUTPUT.with_suffix(
        PROOF_OUTPUT.suffix + f".{os.getpid()}.tmp"
    )
    with temporary_proof.open("w", encoding="ascii", newline="\n") as handle:
        for line in proof:
            handle.write(line.rstrip() + "\n")
    temporary_proof.replace(PROOF_OUTPUT)
    result = {
        "status": "UNSAT_PROOF_EMITTED_UNCHECKED",
        "model": "source133 full-SRG full-Gram macro 4 isolated by assumption core",
        "build": str(BUILD),
        "build_sha256": sha256(BUILD),
        "sweep": str(SWEEP),
        "sweep_sha256": sha256(SWEEP),
        "source_cnf": str(source_cnf),
        "source_cnf_sha256": sha256(source_cnf),
        "macro_branch_index": 4,
        "state_orbit_number": 4,
        "state_indices": branches[4]["state_indices"],
        "Q": branches[4]["Q"],
        "catalog_labelled_coverage": record["coverage"],
        "selectors": selectors,
        "assumption_core_units": list(core),
        "logical_bridge": (
            "The source CNF contains an at-least-one clause on the five macro "
            "selectors.  Units disabling selectors 0..3 therefore force "
            "selector 4; the earlier assumption core proves these four units "
            "already suffice for UNSAT."
        ),
        "variables": variables,
        "clauses": len(formula.clauses),
        "solver": "CaDiCaL 1.9.5 via PySAT",
        "solver_stats": stats,
        "build_seconds": round(built - started, 6),
        "solve_seconds": round(solved - built, 6),
        "proof_lines": len(proof),
        "terminal_empty_clause_present": True,
        "cnf": str(CNF_OUTPUT),
        "cnf_sha256": sha256(CNF_OUTPUT),
        "proof": str(PROOF_OUTPUT),
        "proof_sha256": sha256(PROOF_OUTPUT),
        "proof_checked": False,
        "claim_boundary": (
            "This certificate covers only the nonregular source133 macro 4. "
            "The four regular macros are excluded by the separate exhaustive "
            "48-vertex local census."
        ),
    }
    META_OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "clauses": result["clauses"],
        "proof_lines": result["proof_lines"],
        "solve_seconds": result["solve_seconds"],
    }, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
