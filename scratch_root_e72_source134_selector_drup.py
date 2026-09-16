"""Emit one externally checkable selector proof for E72 source row 134.

The input checkpoint supplies five assumption cores, one for every exact
residual-symmetry orbit of the 181 feasible internal states.  Selector s_i
implies core C_i and at least one selector is true.  A DRUP proof of the
resulting single CNF therefore certifies all five branches simultaneously.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import time


BUILD = Path("scratch_root_e72_source134_state_build.json")
CHECKPOINT = Path("scratch_root_e72_source134_state_c1000000.json")
PREFIX = Path("scratch_root_e72_source134_selector")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def write_cnf(path: Path, variables: int, clauses) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    with temporary.open("w", encoding="ascii", newline="\n") as handle:
        handle.write(f"p cnf {variables} {len(clauses)}\n")
        for clause in clauses:
            handle.write(" ".join(map(str, clause)) + " 0\n")
    temporary.replace(path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", type=Path, default=BUILD)
    parser.add_argument("--checkpoint", type=Path, default=CHECKPOINT)
    parser.add_argument("--prefix", type=Path, default=PREFIX)
    parser.add_argument("--solver", default="cadical195")
    args = parser.parse_args()

    dependency_root = str(Path(".deps").resolve())
    import sys
    if dependency_root not in sys.path:
        sys.path.insert(0, dependency_root)
    import pysat.solvers as solver_module
    from pysat.formula import CNF
    from pysat.solvers import Solver

    started = time.monotonic()
    build = json.loads(args.build.read_text(encoding="utf-8"))
    checkpoint = json.loads(args.checkpoint.read_text(encoding="utf-8"))
    macro_cnf = Path(build["macro_cnf"])
    assert sha256(macro_cnf) == build["macro_cnf_sha256"]
    assert checkpoint["status"] == "UNSAT" and checkpoint["checkpoint_complete"]
    assert checkpoint["unknown"] == checkpoint["sat"] == 0
    assert checkpoint["direct_unsat"] == 5
    assert checkpoint["labelled_states_covered"] == 181
    branches = build["branches"]
    records = checkpoint["records"]
    assert len(branches) == len(records) == 5

    formula = CNF(from_file=str(macro_cnf))
    assert formula.nv == build["macro_cnf_audit"]["declared_variables"]
    assert len(formula.clauses) == build["macro_cnf_audit"]["declared_clauses"]
    selectors = list(range(formula.nv + 1, formula.nv + 1 + len(branches)))
    clauses = formula.clauses
    clauses.append(selectors)
    distinct_cores = set()
    implication_count = 0
    core_rows = []
    for index, (branch, record, selector) in enumerate(zip(branches, records, selectors)):
        assert branch["branch_index"] == record["branch_index"] == index
        assert record["status"] == record["logical_status"] == "UNSAT"
        assumptions = tuple(branch["assumptions"])
        assumption_set = frozenset(assumptions)
        core = tuple(record["assumption_core"])
        assert core and len(core) == len(set(core))
        assert set(core) <= assumption_set
        assert record["assumption_core_size"] == len(core)
        distinct_cores.add(tuple(sorted(core)))
        for literal in core:
            clauses.append([-selector, literal])
            implication_count += 1
        core_rows.append({
            "branch_index": index,
            "state_indices": branch["state_indices"],
            "state_orbit_size": branch["state_orbit_size"],
            "Q": branch["Q"],
            "selector": selector,
            "assumption_count": len(assumptions),
            "core_size": len(core),
            "core": list(core),
            "core_is_subset_of_complete_assumptions": True,
        })
    assert sum(row["state_orbit_size"] for row in core_rows) == 181

    cnf_path = args.prefix.with_suffix(".cnf")
    proof_path = args.prefix.with_suffix(".drup")
    meta_path = args.prefix.with_suffix(".json")
    write_cnf(cnf_path, selectors[-1], clauses)
    built = time.monotonic()

    solver = Solver(name=args.solver, bootstrap_with=clauses, with_proof=True)
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
    temporary = proof_path.with_suffix(proof_path.suffix + f".{os.getpid()}.tmp")
    with temporary.open("w", encoding="ascii", newline="\n") as handle:
        for line in proof:
            handle.write(line.rstrip() + "\n")
    temporary.replace(proof_path)

    result = {
        "status": "UNSAT_PROOF_EMITTED_UNCHECKED",
        "model": "one-hot-at-least-one selector core cover of E72 source row 134",
        "build": str(args.build),
        "build_sha256": sha256(args.build),
        "checkpoint": str(args.checkpoint),
        "checkpoint_sha256": sha256(args.checkpoint),
        "macro_cnf": str(macro_cnf),
        "macro_cnf_sha256": sha256(macro_cnf),
        "state_orbits_covered": len(branches),
        "labelled_internal_states_covered": 181,
        "labelled_state_matching_coverage": build["macro_layer_audit"]["catalog_exact_overlap_completion_coverage"],
        "selectors": len(selectors),
        "selector_policy": "at least one; mutual exclusion is unnecessary",
        "distinct_assumption_cores": len(distinct_cores),
        "selector_core_implications": implication_count,
        "core_rows": core_rows,
        "variables": selectors[-1],
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
            "Every one of the 181 feasible labelled internal states is symmetry-equivalent "
            "to one of five complete assignments A_i.  If macro CNF plus A_i were "
            "satisfiable, selecting s_i would satisfy this selector CNF because its "
            "certified core literals C_i are a subset of A_i."
        ),
        "claim_boundary": (
            "This proof covers source row 134 and the unique Gram macro signature only; "
            "the state/support/Gram exhaustiveness bridge is audited separately."
        ),
    }
    meta_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "variables": result["variables"],
        "clauses": result["clauses"],
        "proof_lines": result["proof_lines"],
        "terminal_empty_clause_present": result["terminal_empty_clause_present"],
        "solve_seconds": result["solve_seconds"],
    }, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
