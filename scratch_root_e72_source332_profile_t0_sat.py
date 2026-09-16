"""Staged exact SAT screen for the remaining source-332 t=0 profile."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import time

from scratch_general_exact_sat import verify
import scratch_root_e72_full_gram_macro_sat as generic


BUILD = Path("scratch_root_e72_source332_parametric_profiles_build.json")
SOURCE_CNF = Path("scratch_root_e72_source332_parametric_profiles.cnf")
CNF_OUTPUT = Path("scratch_root_e72_source332_profile_t0.cnf")


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


def derive(build):
    assert build["status"] == "BUILD_COMPLETE"
    assert build["profile_parameters"] == [-1, 0, 1]
    assert build["checks"]["all_three_integral_PSD_profiles_included"]
    profile = build["profiles"][1]
    assert profile["gram_profile_index"] == 1
    assert profile["parameter_t"] == 0
    selector = int(profile["selector"])
    assert sha256(SOURCE_CNF) == build["cnf_audit"]["sha256"]
    variables, clauses = read_header(SOURCE_CNF)
    temporary = CNF_OUTPUT.with_suffix(CNF_OUTPUT.suffix + f".{os.getpid()}.tmp")
    with SOURCE_CNF.open("rb") as source, temporary.open("wb") as target:
        header = source.readline().split()
        assert header == [
            b"p", b"cnf", str(variables).encode(), str(clauses).encode()
        ]
        target.write(f"p cnf {variables} {clauses + 1}\n".encode())
        shutil.copyfileobj(source, target, length=1 << 20)
        target.write(f"{selector} 0\n".encode())
    temporary.replace(CNF_OUTPUT)
    assert read_header(CNF_OUTPUT) == (variables, clauses + 1)
    return selector, variables, clauses + 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--conflicts", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    assert args.conflicts > 0

    dependency_root = str(Path(".deps").resolve())
    if dependency_root not in sys.path:
        sys.path.insert(0, dependency_root)
    from pysat.formula import CNF
    from pysat.solvers import Solver

    started = time.monotonic()
    build = json.loads(BUILD.read_text(encoding="utf-8"))
    selector, variables, clauses = derive(build)
    derived = time.monotonic()
    formula = CNF(from_file=str(CNF_OUTPUT))
    assert formula.nv == variables and len(formula.clauses) == clauses
    parsed = time.monotonic()
    with Solver(name="cadical195", bootstrap_with=formula.clauses) as solver:
        loaded = time.monotonic()
        solver.conf_budget(args.conflicts)
        answer = solver.solve_limited(expect_interrupt=True)
        finished = time.monotonic()
        stats = solver.accum_stats()
        status = "SAT" if answer is True else "UNSAT" if answer is False else "UNKNOWN"
        verification = None
        if answer is True:
            positive = {
                literal for literal in solver.get_model()
                if 0 < literal <= 3_486
            }
            verification = verify(positive)
            assert verification["ok"]
    result = {
        "status": status,
        "model": "source332 exact full-SRG isolated t=0 Gram profile",
        "source_row_index": 332,
        "parameter_t": 0,
        "selector_unit": selector,
        "macro_labelled_coverage_shared_across_profiles": 131_072,
        "coverage_not_claimed_until_t0_is_excluded": True,
        "conflict_budget": args.conflicts,
        "solver": "CaDiCaL 1.9.5 via PySAT",
        "build": str(BUILD),
        "build_sha256": sha256(BUILD),
        "source_cnf": str(SOURCE_CNF),
        "source_cnf_sha256": sha256(SOURCE_CNF),
        "cnf": str(CNF_OUTPUT),
        "cnf_sha256": sha256(CNF_OUTPUT),
        "variables": variables,
        "clauses": clauses,
        "derive_seconds": round(derived - started, 6),
        "parse_seconds": round(parsed - derived, 6),
        "solver_load_seconds": round(loaded - parsed, 6),
        "solve_seconds": round(finished - loaded, 6),
        "elapsed_seconds": round(time.monotonic() - started, 6),
        "solver_stats": stats,
        "direct_99_vertex_verification": (
            {key: value for key, value in verification.items() if key != "edges"}
            if verification is not None else None
        ),
        "formal_proof_certificate": None,
        "claim_boundary": (
            "UNKNOWN leaves t=0 open. UNSAT remains computational until an "
            "externally checked proof is emitted."
        ),
    }
    generic.atomic_json(args.output, result)
    print(json.dumps({
        "status": status,
        "conflicts": stats.get("conflicts", 0),
        "solve_seconds": result["solve_seconds"],
    }, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
