"""Proof-oriented SAT census of C11 equitable quotient matrices.

For a semiregular C11 action on a hypothetical srg(99,14,1,2), the nine
orbits form an equitable partition with a symmetric integral quotient B.
It necessarily satisfies

    B 1 = 14 1,              B^2 + B = 12 I + 22 J,

and Galois conjugacy of the ten nontrivial C11 character blocks forces
trace(B)=10.  This program bit-blasts precisely those conditions.  It is a
much smaller necessary problem than the 99-vertex edge-orbit SAT instance.

All nonlinear products are represented by explicit AND variables.  Weighted
equalities use a deterministic finite-state sum automaton, so the DIMACS can
be checked by an ordinary DRAT checker if it is UNSAT.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import time
from pathlib import Path


CNF_PATH = Path("scratch_root_c11_quotient.cnf")
META_PATH = Path("scratch_root_c11_quotient_build.json")
RESULT_PATH = Path("scratch_root_c11_quotient_sat_result.json")


def atomic_json(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def admissible_row_patterns() -> dict[int, tuple[tuple[int, ...], ...]]:
    """Exhaustively derive the small value domains from the diagonal identity."""

    answer: dict[int, list[tuple[int, ...]]] = {}
    for diagonal in range(0, 11, 2):
        rows = []
        # Sorted off-diagonal entries; every labelled row is a permutation.
        for values in itertools.combinations_with_replacement(range(12), 8):
            if sum(values) + diagonal != 14:
                continue
            if sum(value * value for value in values) + diagonal * diagonal + diagonal != 34:
                continue
            rows.append(tuple(reversed(values)))
        if rows:
            answer[diagonal] = sorted(rows, reverse=True)
    expected = {
        0: [
            (4, 3, 2, 1, 1, 1, 1, 1),
            (4, 2, 2, 2, 2, 1, 1, 0),
            (3, 3, 3, 2, 1, 1, 1, 0),
            (3, 3, 2, 2, 2, 2, 0, 0),
        ],
        2: [
            (4, 2, 2, 1, 1, 1, 1, 0),
            (3, 3, 2, 2, 1, 1, 0, 0),
        ],
        4: [(2, 2, 1, 1, 1, 1, 1, 1)],
    }
    assert answer == expected, answer
    return {key: tuple(value) for key, value in answer.items()}


def add_exactly_one(formula, pool, literals: list[int]) -> None:
    from pysat.card import CardEnc, EncType

    formula.append(literals)
    if len(literals) > 1:
        formula.extend(CardEnc.atmost(
            literals, bound=1, vpool=pool, encoding=EncType.seqcounter
        ).clauses)


def add_weighted_equals(
    formula,
    pool,
    terms: list[tuple[int, int]],
    bound: int,
    tag: tuple,
) -> None:
    """Encode sum(weight * literal) == bound with an exact-sum DFA.

    State ``bound + 1`` is overflow.  Exactly one state is active at every
    layer.  The two guarded transitions from each state make the construction
    equisatisfiable, not merely a one-way relaxation.
    """

    from pysat.card import CardEnc, EncType

    cleaned = []
    constant = 0
    for literal, weight in terms:
        assert literal != 0 and weight >= 0
        if weight == 0:
            continue
        cleaned.append((literal, weight))
    states = [pool.id(("sum", tag, 0, value)) for value in range(bound + 2)]
    formula.append([states[0]])
    for value in range(1, bound + 2):
        formula.append([-states[value]])

    for index, (literal, weight) in enumerate(cleaned, 1):
        following = [
            pool.id(("sum", tag, index, value)) for value in range(bound + 2)
        ]
        # At-most-one plus the forced transition from the unique preceding
        # state gives exactly one following state.
        formula.extend(CardEnc.atmost(
            following, bound=1, vpool=pool, encoding=EncType.seqcounter
        ).clauses)
        overflow = bound + 1
        for value, previous in enumerate(states):
            false_target = following[value]
            true_value = overflow if value == overflow else min(overflow, value + weight)
            true_target = following[true_value]
            formula.append([-previous, literal, false_target])
            formula.append([-previous, -literal, true_target])
        states = following
    formula.append([states[bound]])


def build() -> dict:
    from pysat.formula import CNF, IDPool

    started = time.monotonic()
    patterns = admissible_row_patterns()
    formula = CNF()
    pool = IDPool()

    # The row-pattern lemma proves these are the complete entry domains.
    domains: dict[tuple[int, int], tuple[int, ...]] = {}
    value_var: dict[tuple[int, int, int], int] = {}
    for i in range(9):
        for j in range(i, 9):
            domain = (0, 2, 4) if i == j else (0, 1, 2, 3, 4)
            domains[i, j] = domain
            literals = []
            for value in domain:
                variable = pool.id(("B", i, j, value))
                value_var[i, j, value] = variable
                literals.append(variable)
            add_exactly_one(formula, pool, literals)

    def x(i: int, j: int, value: int) -> int:
        if i > j:
            i, j = j, i
        return value_var[i, j, value]

    def domain(i: int, j: int) -> tuple[int, ...]:
        if i > j:
            i, j = j, i
        return domains[i, j]

    # Row sums and diagonal entries of B^2+B=12I+22J.
    for i in range(9):
        row_terms = []
        square_terms = []
        for j in range(9):
            for value in domain(i, j):
                row_terms.append((x(i, j, value), value))
                square_terms.append((x(i, j, value), value * value))
        for value in domain(i, i):
            square_terms.append((x(i, i, value), value))
        add_weighted_equals(formula, pool, row_terms, 14, ("row", i))
        add_weighted_equals(formula, pool, square_terms, 34, ("diag", i))

    # Trace forced by the rational SRG spectrum and C11 Galois conjugacy.
    trace_terms = [
        (x(i, i, value), value)
        for i in range(9)
        for value in domain(i, i)
    ]
    add_weighted_equals(formula, pool, trace_terms, 10, ("trace",))

    # A harmless symmetry breaker: sort the diagonal entries.
    for i in range(8):
        for left in domain(i, i):
            for right in domain(i + 1, i + 1):
                if left < right:
                    formula.append([-x(i, i, left), -x(i + 1, i + 1, right)])

    product_variables = 0
    # Off-diagonal entries of B^2+B=12I+22J.
    for i in range(9):
        for j in range(i + 1, 9):
            terms = []
            for k in range(9):
                for left in domain(i, k):
                    if left == 0:
                        continue
                    for right in domain(k, j):
                        if right == 0:
                            continue
                        conjunction = pool.id(("product", i, j, k, left, right))
                        first = x(i, k, left)
                        second = x(k, j, right)
                        formula.append([-conjunction, first])
                        formula.append([-conjunction, second])
                        formula.append([conjunction, -first, -second])
                        terms.append((conjunction, left * right))
                        product_variables += 1
            for value in domain(i, j):
                terms.append((x(i, j, value), value))
            add_weighted_equals(formula, pool, terms, 22, ("offdiag", i, j))

    temporary = CNF_PATH.with_suffix(CNF_PATH.suffix + f".{os.getpid()}.tmp")
    formula.to_file(str(temporary))
    temporary.replace(CNF_PATH)
    meta = {
        "status": "BUILT",
        "model": "exact necessary 9x9 integral quotient for semiregular C11",
        "cnf": str(CNF_PATH),
        "cnf_sha256": sha256(CNF_PATH),
        "variables": formula.nv,
        "clauses": len(formula.clauses),
        "product_variables": product_variables,
        "value_variables": {
            f"{i},{j},{value}": variable
            for (i, j, value), variable in value_var.items()
        },
        "row_patterns": {str(key): value for key, value in patterns.items()},
        "constraints": [
            "B symmetric integral",
            "B*1=14*1",
            "B^2+B=12I+22J",
            "trace(B)=10",
            "diagonal sorted as WLOG symmetry breaker",
        ],
        "build_seconds": round(time.monotonic() - started, 6),
        "claim_boundary": (
            "UNSAT excludes only SRG candidates admitting a semiregular C11 action; "
            "SAT supplies only a necessary quotient matrix."
        ),
    }
    atomic_json(META_PATH, meta)
    return meta


def decode(model: list[int], meta: dict) -> list[list[int]]:
    positive = set(model)
    matrix = [[0] * 9 for _ in range(9)]
    variables = meta["value_variables"]
    for i in range(9):
        for j in range(i, 9):
            domain = (0, 2, 4) if i == j else (0, 1, 2, 3, 4)
            chosen = []
            for value in domain:
                variable = variables[f"{i},{j},{value}"]
                if variable in positive:
                    chosen.append(value)
            assert len(chosen) == 1, (i, j, chosen)
            matrix[i][j] = matrix[j][i] = chosen[0]
    return matrix


def verify(matrix: list[list[int]]) -> None:
    assert all(sum(row) == 14 for row in matrix)
    assert sum(matrix[i][i] for i in range(9)) == 10
    assert all(matrix[i][j] == matrix[j][i] for i in range(9) for j in range(9))
    for i in range(9):
        for j in range(9):
            value = sum(matrix[i][k] * matrix[k][j] for k in range(9)) + matrix[i][j]
            assert value == 12 * (i == j) + 22, (i, j, value)


def solve(conflicts: int | None, proof: Path | None) -> dict:
    from pysat.formula import CNF
    from pysat.solvers import Solver

    meta = json.loads(META_PATH.read_text(encoding="utf-8"))
    assert sha256(CNF_PATH) == meta["cnf_sha256"]
    formula = CNF(from_file=str(CNF_PATH))
    started = time.monotonic()
    kwargs = {"name": "cadical195", "bootstrap_with": formula.clauses}
    if proof is not None:
        kwargs["with_proof"] = True
    with Solver(**kwargs) as solver:
        if conflicts is not None:
            solver.conf_budget(conflicts)
            answer = solver.solve_limited()
        else:
            answer = solver.solve()
        stats = solver.accum_stats()
        model = solver.get_model() if answer is True else None
        if answer is False and proof is not None:
            proof_lines = solver.get_proof()
            proof.write_text("\n".join(proof_lines) + "\n", encoding="ascii", newline="\n")
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
        "proof": None if proof is None or answer is not False else str(proof),
        "stats": stats,
        "solve_seconds": round(time.monotonic() - started, 6),
        "matrix": matrix,
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
        print(json.dumps(build(), sort_keys=True), flush=True)
    if args.solve:
        print(json.dumps(solve(args.conflicts, args.proof), sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
