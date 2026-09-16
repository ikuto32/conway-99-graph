"""Strengthen the exact C11 quotient CNF with the exhaustive row table.

The base quotient CNF already implies the seven row multisets through its row
sum and diagonal-square equations.  Repeating that finite consequence with
selector-gated cardinalities gives the SAT solver substantially more local
propagation while preserving exactly the same quotient matrices.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from collections import Counter
from pathlib import Path

from scratch_root_c11_quotient_sat import (
    CNF_PATH as BASE_CNF,
    META_PATH as BASE_META,
    add_exactly_one,
    admissible_row_patterns,
    atomic_json,
    verify,
)


CNF_PATH = Path("scratch_root_c11_quotient_rowtable.cnf")
META_PATH = Path("scratch_root_c11_quotient_rowtable_build.json")
RESULT_PATH = Path("scratch_root_c11_quotient_rowtable_result.json")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def build() -> dict:
    from pysat.card import CardEnc, EncType
    from pysat.formula import CNF, IDPool

    started = time.monotonic()
    base_meta = json.loads(BASE_META.read_text(encoding="utf-8"))
    assert sha256(BASE_CNF) == base_meta["cnf_sha256"]
    formula = CNF(from_file=str(BASE_CNF))
    base_variables = formula.nv
    base_clauses = len(formula.clauses)
    pool = IDPool(start_from=base_variables + 1)
    value_variables = base_meta["value_variables"]

    def x(i: int, j: int, value: int) -> int:
        if i > j:
            i, j = j, i
        return int(value_variables[f"{i},{j},{value}"])

    types = []
    for diagonal, patterns in admissible_row_patterns().items():
        for pattern in patterns:
            counts = Counter(pattern)
            types.append({
                "diagonal": diagonal,
                "pattern": list(pattern),
                "counts": [counts[value] for value in range(5)],
            })
    assert len(types) == 7

    row_selectors = []
    gated_cardinality_clauses = 0
    for i in range(9):
        selectors = [pool.id(("row_type", i, kind)) for kind in range(len(types))]
        add_exactly_one(formula, pool, selectors)
        row_selectors.append(selectors)
        cross = [j for j in range(9) if j != i]
        for selector, row_type in zip(selectors, types):
            formula.append([-selector, x(i, i, row_type["diagonal"])])
            for value, wanted in enumerate(row_type["counts"]):
                literals = [x(i, j, value) for j in cross]
                encoded = CardEnc.equals(
                    literals,
                    bound=wanted,
                    vpool=pool,
                    encoding=EncType.seqcounter,
                ).clauses
                formula.extend([[-selector, *clause] for clause in encoded])
                gated_cardinality_clauses += len(encoded)

    temporary = CNF_PATH.with_suffix(CNF_PATH.suffix + f".{os.getpid()}.tmp")
    formula.to_file(str(temporary))
    temporary.replace(CNF_PATH)
    meta = {
        "status": "BUILT",
        "model": "exact necessary C11 quotient with redundant exhaustive row table",
        "base_cnf": str(BASE_CNF),
        "base_cnf_sha256": base_meta["cnf_sha256"],
        "cnf": str(CNF_PATH),
        "cnf_sha256": sha256(CNF_PATH),
        "base_variables": base_variables,
        "base_clauses": base_clauses,
        "variables": formula.nv,
        "clauses": len(formula.clauses),
        "row_types": types,
        "row_type_selectors": row_selectors,
        "gated_cardinality_clauses": gated_cardinality_clauses,
        "value_variables": value_variables,
        "build_seconds": round(time.monotonic() - started, 6),
        "redundancy_justification": (
            "The seven multisets are the exhaustive nonnegative integer solutions "
            "of sum(row)=14 and sum(row^2)+B_ii=34 with even B_ii."
        ),
        "claim_boundary": base_meta["claim_boundary"],
    }
    atomic_json(META_PATH, meta)
    return meta


def decode(model: list[int], meta: dict) -> list[list[int]]:
    positive = set(model)
    variables = meta["value_variables"]
    matrix = [[0] * 9 for _ in range(9)]
    for i in range(9):
        for j in range(i, 9):
            domain = (0, 2, 4) if i == j else (0, 1, 2, 3, 4)
            chosen = [
                value for value in domain
                if int(variables[f"{i},{j},{value}"]) in positive
            ]
            assert len(chosen) == 1, (i, j, chosen)
            matrix[i][j] = matrix[j][i] = chosen[0]
    return matrix


def solve(conflicts: int | None, proof: Path | None) -> dict:
    from pysat.formula import CNF
    from pysat.solvers import Solver

    meta = json.loads(META_PATH.read_text(encoding="utf-8"))
    assert sha256(CNF_PATH) == meta["cnf_sha256"]
    formula = CNF(from_file=str(CNF_PATH))
    started = time.monotonic()
    with Solver(
        name="cadical195",
        bootstrap_with=formula.clauses,
        with_proof=proof is not None,
    ) as solver:
        if conflicts is None:
            answer = solver.solve()
        else:
            solver.conf_budget(conflicts)
            answer = solver.solve_limited()
        stats = solver.accum_stats()
        model = solver.get_model() if answer is True else None
        if answer is False and proof is not None:
            lines = solver.get_proof()
            proof.write_text("\n".join(lines) + "\n", encoding="ascii", newline="\n")
    status = "SAT" if answer is True else "UNSAT" if answer is False else "UNKNOWN"
    matrix = None
    if model is not None:
        matrix = decode(model, meta)
        verify(matrix)
    result = {
        "status": status,
        "cnf": str(CNF_PATH),
        "cnf_sha256": meta["cnf_sha256"],
        "solver": "CaDiCaL 1.9.5 via PySAT",
        "conflict_budget": conflicts,
        "stats": stats,
        "solve_seconds": round(time.monotonic() - started, 6),
        "matrix": matrix,
        "proof": None if proof is None or answer is not False else str(proof),
        "claim_boundary": meta["claim_boundary"],
    }
    atomic_json(RESULT_PATH, result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--solve", action="store_true")
    parser.add_argument("--conflicts", type=int)
    parser.add_argument("--proof", type=Path)
    args = parser.parse_args()
    if args.build or (args.solve and not CNF_PATH.exists()):
        built = build()
        print(json.dumps({
            key: built[key]
            for key in ("status", "variables", "clauses", "cnf_sha256", "build_seconds")
        }, sort_keys=True), flush=True)
    if args.solve:
        print(json.dumps(solve(args.conflicts, args.proof), sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
