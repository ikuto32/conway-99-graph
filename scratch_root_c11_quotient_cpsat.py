"""Exact integer quotient search for a semiregular C11 automorphism.

If a putative graph has nine vertex orbits of length 11, its equitable
quotient B is a symmetric 9 by 9 nonnegative integer matrix.  The SRG matrix
identity gives

    B^2 + B = 12 I + 22 J,   B 1 = 14 1.

The diagonal entries are even because they are degrees of undirected
circulant graphs of odd order.  This script searches precisely those integer
conditions.  Passage is only a necessary quotient condition.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import time
from pathlib import Path


OUTPUT = Path("scratch_root_c11_quotient_cpsat.json")


def atomic_json(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def verify(matrix: list[list[int]]) -> dict:
    n = 9
    errors = []
    if len(matrix) != n or any(len(row) != n for row in matrix):
        errors.append("shape")
        return {"ok": False, "errors": errors}
    if any(matrix[i][j] != matrix[j][i] for i in range(n) for j in range(n)):
        errors.append("symmetry")
    if any(not (0 <= matrix[i][j] <= 11) for i in range(n) for j in range(n)):
        errors.append("bounds")
    if any(matrix[i][i] % 2 for i in range(n)):
        errors.append("diagonal parity")
    if any(sum(row) != 14 for row in matrix):
        errors.append("row sums")
    square = [
        [sum(matrix[i][k] * matrix[k][j] for k in range(n)) for j in range(n)]
        for i in range(n)
    ]
    if any(
        square[i][j] + matrix[i][j] != 12 * (i == j) + 22
        for i in range(n) for j in range(n)
    ):
        errors.append("quadratic identity")
    trace = sum(matrix[i][i] for i in range(n))
    if trace not in (10, 24, 38):
        errors.append("trace spectrum")
    return {
        "ok": not errors,
        "errors": errors,
        "trace": trace,
        "row_square_controls": [
            sum(value * value for value in matrix[i]) + matrix[i][i]
            for i in range(n)
        ],
    }


def solve(time_limit: float, enumerate_limit: int) -> dict:
    from ortools.sat.python import cp_model

    started = time.monotonic()
    model = cp_model.CpModel()
    B = [[None for _ in range(9)] for _ in range(9)]
    for i in range(9):
        for j in range(i, 9):
            variable = model.NewIntVar(0, 10 if i == j else 11, f"b_{i}_{j}")
            B[i][j] = B[j][i] = variable
            if i == j:
                model.AddAllowedAssignments([variable], [[value] for value in range(0, 11, 2)])
    for row in B:
        model.Add(sum(row) == 14)

    # The diagonal part of B^2+B=12I+22J leaves only seven unordered row
    # patterns.  Stating the exact labelled table removes weak nonlinear
    # propagation without changing the model.
    row_patterns = {
        0: (
            (3, 3, 2, 2, 2, 2, 0, 0),
            (3, 3, 3, 2, 1, 1, 1, 0),
            (4, 2, 2, 2, 2, 1, 1, 0),
            (4, 3, 2, 1, 1, 1, 1, 1),
        ),
        2: (
            (3, 3, 2, 2, 1, 1, 0, 0),
            (4, 2, 2, 1, 1, 1, 1, 0),
        ),
        4: ((2, 2, 1, 1, 1, 1, 1, 1),),
    }
    allowed_rows = []
    for diagonal, patterns in row_patterns.items():
        for pattern in patterns:
            for labelled in set(itertools.permutations(pattern)):
                allowed_rows.append((diagonal,) + labelled)
    for i in range(9):
        model.AddAllowedAssignments(
            [B[i][i]] + [B[i][j] for j in range(9) if j != i],
            allowed_rows,
        )

    product_count = 0
    for i in range(9):
        for j in range(i, 9):
            products = []
            for k in range(9):
                product = model.NewIntVar(0, 121, f"p_{i}_{j}_{k}")
                model.AddMultiplicationEquality(product, [B[i][k], B[k][j]])
                products.append(product)
                product_count += 1
            model.Add(sum(products) + B[i][j] == 12 * (i == j) + 22)

    trace = model.NewIntVar(0, 90, "trace")
    model.Add(trace == sum(B[i][i] for i in range(9)))
    # Rational eigenvalues and Galois conjugacy of all ten nontrivial C11
    # character blocks force the invariant quotient multiplicities to be
    # 3^4 and (-4)^4, hence trace(B)=10.
    model.Add(trace == 10)

    # Quotient orbit labels are arbitrary.  Ordering diagonal entries is a
    # safe first symmetry breaker and leaves all isomorphism types covered.
    for i in range(8):
        model.Add(B[i][i] >= B[i + 1][i + 1])

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_search_workers = 1 if enumerate_limit else 16
    solver.parameters.random_seed = 1
    solutions = []

    if enumerate_limit:
        class Collector(cp_model.CpSolverSolutionCallback):
            def on_solution_callback(self) -> None:
                matrix = [[self.Value(B[i][j]) for j in range(9)] for i in range(9)]
                checked = verify(matrix)
                assert checked["ok"], checked
                solutions.append({"matrix": matrix, "verification": checked})
                if len(solutions) >= enumerate_limit:
                    self.StopSearch()

        callback = Collector()
        status_code = solver.SearchForAllSolutions(model, callback)
    else:
        status_code = solver.Solve(model)
        if status_code in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            matrix = [[solver.Value(B[i][j]) for j in range(9)] for i in range(9)]
            checked = verify(matrix)
            assert checked["ok"], checked
            solutions.append({"matrix": matrix, "verification": checked})

    status = solver.StatusName(status_code)
    result = {
        "status": status,
        "model": "necessary equitable quotient for a semiregular C11 action",
        "equations": ["B symmetric", "B*1=14*1", "B^2+B=12I+22J"],
        "diagonal_domain": [0, 2, 4, 6, 8, 10],
        "trace_domain_before_C11_Galois": [10, 24, 38],
        "trace_forced_by_C11_Galois": 10,
        "exact_labelled_row_table_size": len(allowed_rows),
        "symmetry_breaking": "diagonal entries nonincreasing",
        "integer_variables_B": 45,
        "multiplication_helpers": product_count,
        "time_limit_seconds": time_limit,
        "enumerate_limit": enumerate_limit,
        "wall_seconds": round(time.monotonic() - started, 6),
        "solver_wall_seconds": solver.WallTime(),
        "conflicts": solver.NumConflicts(),
        "branches": solver.NumBranches(),
        "solution_count": len(solutions),
        "solutions": solutions,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest().upper(),
        "claim_boundary": (
            "These are necessary quotient matrices only. INFEASIBLE would "
            "exclude the semiregular C11 class computationally; FEASIBLE does "
            "not construct a graph."
        ),
    }
    atomic_json(OUTPUT, result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seconds", type=float, default=300.0)
    parser.add_argument("--enumerate-limit", type=int, default=0)
    args = parser.parse_args()
    result = solve(args.seconds, args.enumerate_limit)
    print(json.dumps({
        key: result[key]
        for key in ("status", "solution_count", "wall_seconds", "conflicts", "branches")
    }, sort_keys=True))


if __name__ == "__main__":
    main()
