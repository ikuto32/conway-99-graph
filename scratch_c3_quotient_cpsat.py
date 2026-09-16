"""Necessary quotient model for the fixed-point-free C3 branch.

For the 33 C3 vertex orbits, let M be the adjacency action on vectors that
are constant on each orbit.  Its diagonal is 2 on a K3 orbit and 0 otherwise;
an off-diagonal entry is the number (0, 1, or 2) of invariant matchings
between two orbits.  Multiplicity 3 is impossible, and multiplicity 2 occurs
only between non-K3 orbits.  The SRG equation gives

    M^2 + M = 12 I + 6 J.

Every row of the support of M has degree 12.  On the non-K3 vertices, the
multiplicity-2 edges form a 2-regular graph.  This model imposes all of those
conditions exactly.  It is necessary, but not sufficient: a feasible M still
needs compatible Z/3 phases (handled by scratch_c3_cpsat.py).
"""

from __future__ import annotations

import argparse
import concurrent.futures
import itertools
import json
from pathlib import Path

from ortools.sat.python import cp_model


T_VALUES = (6, 27)
N = 33


def solve(t_value: int, seconds: float, workers: int, shape: str, log: bool) -> dict[str, object]:
    assert t_value in T_VALUES
    if t_value != 27 and shape != "free":
        raise ValueError("a fixed double-edge shape is implemented only for t=27")

    model = cp_model.CpModel()
    pairs = list(itertools.combinations(range(N), 2))
    support = {p: model.new_bool_var("") for p in pairs}
    double: dict[tuple[int, int], cp_model.IntVar | int] = {}
    for i, j in pairs:
        if i >= t_value and j >= t_value:
            double[i, j] = model.new_bool_var("")
            model.add(double[i, j] <= support[i, j])
        else:
            double[i, j] = 0

    def key(i: int, j: int) -> tuple[int, int]:
        return (i, j) if i < j else (j, i)

    def x(i: int, j: int) -> cp_model.IntVar:
        return support[key(i, j)]

    def y(i: int, j: int) -> cp_model.IntVar | int:
        return double[key(i, j)]

    def m(i: int, j: int):
        return x(i, j) + y(i, j)

    for i in range(N):
        model.add(sum(x(i, j) for j in range(N) if j != i) == 12)
        if i >= t_value:
            model.add(sum(y(i, j) for j in range(t_value, N) if j != i) == 2)

    # Orbit 0 is a K3.  Its support neighbours can be sorted inside any class
    # whose full symmetric group is still available.  Once a non-K3 2-factor
    # shape is fixed below, only that shape's automorphism group remains, so
    # sorting all non-K3 vertices would be an UNSAFE extra restriction.
    sortable_classes = [(1, t_value)]
    if shape == "free":
        sortable_classes.append((t_value, N))
    for start, stop in sortable_classes:
        for j in range(start, stop - 1):
            model.add(x(0, j) >= x(0, j + 1))

    # For t=27 there are only six non-K3 vertices.  A simple 2-regular graph
    # on six vertices is, up to relabelling, C6 or two disjoint triangles.
    if shape != "free":
        verts = list(range(27, 33))
        chosen: set[tuple[int, int]] = set()
        if shape == "c6":
            for a, b in zip(verts, verts[1:] + verts[:1]):
                chosen.add(key(a, b))
        elif shape == "2c3":
            for tri in (verts[:3], verts[3:]):
                chosen.update(key(a, b) for a, b in itertools.combinations(tri, 2))
        else:
            raise ValueError(shape)
        for i, j in itertools.combinations(verts, 2):
            model.add(y(i, j) == ((i, j) in chosen))

    products = 0
    for i, j in pairs:
        terms = []
        for k in range(N):
            if k == i or k == j:
                continue
            product = model.new_int_var(0, 4, "")
            model.add_multiplication_equality(product, [m(i, k), m(k, j)])
            terms.append(product)
            products += 1
        diagonal_i = 2 if i < t_value else 0
        diagonal_j = 2 if j < t_value else 0
        model.add(sum(terms) + (diagonal_i + diagonal_j + 1) * m(i, j) == 6)

    build: dict[str, object] = {
        "event": "built",
        "t": t_value,
        "shape": shape,
        "support_variables": len(support),
        "double_variables": sum(not isinstance(v, int) for v in double.values()),
        "product_variables": products,
        "proto_variables": len(model.proto.variables),
        "proto_constraints": len(model.proto.constraints),
    }
    print(json.dumps(build), flush=True)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_search_workers = workers
    solver.parameters.log_search_progress = log
    status = solver.solve(model)
    record: dict[str, object] = {
        **build,
        "status": solver.status_name(status),
        "wall_seconds": solver.wall_time,
        "branches": solver.num_branches,
        "conflicts": solver.num_conflicts,
        "response_stats": solver.response_stats(),
    }
    suffix = f"_t{t_value}_{shape}"
    Path(f"scratch_c3_quotient{suffix}_result.json").write_text(
        json.dumps(record, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({k: v for k, v in record.items() if k != "response_stats"}), flush=True)

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        matrix = [[0] * N for _ in range(N)]
        for i in range(N):
            matrix[i][i] = 2 if i < t_value else 0
        for i, j in pairs:
            value = solver.value(x(i, j)) + (
                solver.value(y(i, j)) if not isinstance(y(i, j), int) else 0
            )
            matrix[i][j] = matrix[j][i] = value

        # Independent integer verification of every entry of M^2+M.
        for i in range(N):
            for j in range(N):
                lhs = sum(matrix[i][k] * matrix[k][j] for k in range(N)) + matrix[i][j]
                rhs = (12 if i == j else 0) + 6
                assert lhs == rhs, (i, j, lhs, rhs)
        witness = {**record, "matrix": matrix}
        path = Path(f"scratch_c3_quotient{suffix}_witness.json")
        path.write_text(json.dumps(witness, indent=2) + "\n", encoding="utf-8")
        record["verified_quotient"] = str(path)
    return record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--t", type=int, choices=T_VALUES)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--shape", choices=("free", "c6", "2c3"), default="free")
    parser.add_argument("--seconds", type=float, default=180.0)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--log", action="store_true")
    args = parser.parse_args()
    if args.all == (args.t is not None):
        parser.error("choose exactly one of --t or --all")
    if args.t is not None:
        solve(args.t, args.seconds, args.workers, args.shape, args.log)
        return

    tasks = ((6, "free"), (27, "c6"), (27, "2c3"))
    with concurrent.futures.ProcessPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(solve, t, args.seconds, args.workers, shape, args.log): (t, shape)
            for t, shape in tasks
        }
        records = [future.result() for future in concurrent.futures.as_completed(futures)]
    records.sort(key=lambda row: (int(row["t"]), str(row["shape"])))
    Path("scratch_c3_quotient_summary.json").write_text(
        json.dumps(records, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
