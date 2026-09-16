"""Emit a DRUP trace for one terminal source-332 Gram profile selector."""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import time


BUILD = Path("scratch_root_e72_source332_parametric_profiles_build.json")
SWEEP = Path(
    "scratch_root_e72_source332_parametric_profiles_branches_c1000000.json"
)
T0_SCREEN = Path("scratch_root_e72_source332_profile_t0_c3000000.json")
SOURCE_CNF = Path("scratch_root_e72_source332_parametric_profiles.cnf")


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
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile-index", type=int, choices=(0, 1, 2), required=True)
    args = parser.parse_args()
    profile_index = args.profile_index
    tag = {0: "tminus1", 1: "t0", 2: "tplus1"}[profile_index]
    cnf_output = Path(f"scratch_root_e72_source332_profile_{tag}.cnf")
    proof_output = Path(f"scratch_root_e72_source332_profile_{tag}.drup")
    meta_output = Path(f"scratch_root_e72_source332_profile_{tag}_drup.json")

    dependency_root = str(Path(".deps").resolve())
    if dependency_root not in sys.path:
        sys.path.insert(0, dependency_root)
    import pysat.solvers as solver_module
    from pysat.formula import CNF
    from pysat.solvers import Solver

    started = time.monotonic()
    build = json.loads(BUILD.read_text(encoding="utf-8"))
    sweep = json.loads(SWEEP.read_text(encoding="utf-8"))
    assert build["source_row_index"] == 332
    assert build["profile_parameters"] == [-1, 0, 1]
    assert build["profile_branch_count"] == 3
    assert build["macro_labelled_coverage"] == 131_072
    assert build["checks"]["profile_selectors_exactly_one"]
    assert build["checks"]["profile_graph_sets_pairwise_disjoint"]
    assert sha256(SOURCE_CNF) == build["cnf_audit"]["sha256"]
    profile = build["profiles"][profile_index]
    selector = int(profile["selector"])
    parameter = int(profile["parameter_t"])
    assert parameter == profile_index - 1
    if profile_index == 1:
        screen_path = T0_SCREEN
        record = json.loads(screen_path.read_text(encoding="utf-8"))
        assert record["status"] == "UNSAT"
        assert record["parameter_t"] == 0
        assert record["selector_unit"] == selector
    else:
        screen_path = SWEEP
        record = next(
            row for row in sweep["records"]
            if row["gram_profile_index"] == profile_index
        )
        assert record["status"] == "UNSAT"
        assert record["selector"] == selector
        assert record["assumption_core"] == [selector]

    variables, source_clauses = read_header(SOURCE_CNF)
    assert variables == build["cnf_audit"]["declared_variables"]
    assert source_clauses == build["cnf_audit"]["declared_clauses"]
    temporary_cnf = cnf_output.with_suffix(cnf_output.suffix + f".{os.getpid()}.tmp")
    with SOURCE_CNF.open("rb") as source, temporary_cnf.open("wb") as target:
        header = source.readline().split()
        assert header == [
            b"p", b"cnf", str(variables).encode(), str(source_clauses).encode()
        ]
        target.write(f"p cnf {variables} {source_clauses + 1}\n".encode())
        shutil.copyfileobj(source, target, length=1 << 20)
        target.write(f"{selector} 0\n".encode())
    temporary_cnf.replace(cnf_output)
    assert read_header(cnf_output) == (variables, source_clauses + 1)
    built = time.monotonic()

    formula = CNF(from_file=str(cnf_output))
    assert formula.nv == variables
    assert len(formula.clauses) == source_clauses + 1
    solver = Solver(
        name="cadical195", bootstrap_with=formula.clauses, with_proof=True
    )
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
    proof = (
        Solver._proof_bin2text(bytearray(raw_proof).strip())
        if answer is False else None
    )
    engine.prfile.close()
    engine.prfile = None
    solver.delete()
    assert answer is False and proof is not None
    assert any(line.strip() == "0" for line in proof)
    temporary_proof = proof_output.with_suffix(
        proof_output.suffix + f".{os.getpid()}.tmp"
    )
    with temporary_proof.open("w", encoding="ascii", newline="\n") as handle:
        for line in proof:
            handle.write(line.rstrip() + "\n")
    temporary_proof.replace(proof_output)

    result = {
        "status": "UNSAT_PROOF_EMITTED_UNCHECKED",
        "model": "source332 exact full-SRG isolated parametric Gram profile",
        "source_row_index": 332,
        "gram_profile_index": profile_index,
        "parameter_t": parameter,
        "selector_unit": selector,
        "macro_labelled_coverage_shared_across_profiles": 131_072,
        "coverage_not_claimed_for_single_profile": True,
        "build": str(BUILD),
        "build_sha256": sha256(BUILD),
        "terminal_screen": str(screen_path),
        "terminal_screen_sha256": sha256(screen_path),
        "source_cnf": str(SOURCE_CNF),
        "source_cnf_sha256": sha256(SOURCE_CNF),
        "derived_cnf_construction": (
            "byte-identical source payload followed by the positive profile "
            "selector unit, with clause count increased by one"
        ),
        "variables": variables,
        "clauses": len(formula.clauses),
        "solver": "CaDiCaL 1.9.5 via PySAT",
        "solver_stats": stats,
        "build_seconds": round(built - started, 6),
        "solve_seconds": round(solved - built, 6),
        "c_stdio_flush_return": flush_return,
        "proof_lines": len(proof),
        "terminal_empty_clause_present": True,
        "cnf": str(cnf_output),
        "cnf_sha256": sha256(cnf_output),
        "proof": str(proof_output),
        "proof_sha256": sha256(proof_output),
        "proof_checked": False,
        "claim_boundary": (
            "This proof covers one of three mutually exclusive Gram profiles. "
            "The shared macro coverage must not be credited until all profiles "
            "are excluded."
        ),
    }
    meta_output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "parameter_t": parameter,
        "solve_seconds": result["solve_seconds"],
        "proof_lines": result["proof_lines"],
    }, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
