"""Exact 42-vertex quotient matrix formulation of the C2 branch.

Each C2-invariant 2x2 outer adjacency block is pI+cX.  This model uses
S=p+c and T=p-c and enforces their two matrix equations directly, halving
the number of pair/common-neighbour product variables compared with the
84-vertex lifted formulation.
"""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

from ortools.sat.python import cp_model


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=float, default=300.0)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--mate-type", choices=("none", "same", "overlap", "disjoint"), default="none")
    ap.add_argument("--log", action="store_true")
    args = ap.parse_args()

    vertices = [(i, j, r) for i in range(7) for j in range(i + 1, 7) for r in range(2)]
    index = {x: k for k, x in enumerate(vertices)}
    n = 42

    # Signed incidence: canonical lift has sign 0 at the lower endpoint and
    # sign r at the upper endpoint.
    h = [[int(g in x[:2]) for g in range(7)] for x in vertices]
    z = []
    for i, j, r in vertices:
        row = [0] * 7
        row[i] = 1
        row[j] = 1 if r == 0 else -1
        z.append(row)

    model = cp_model.CpModel()
    U = {}
    M = {}
    S = {}
    T = {}
    for x, y in itertools.combinations(range(n), 2):
        k = (x, y)
        U[k] = model.new_bool_var("")
        M[k] = model.new_bool_var("")
        S[k] = model.new_int_var(0, 2, "")
        T[k] = model.new_int_var(-1, 1, "")
        # S=0: no block; S=1,T=+/-1: I or X; S=2,T=0: both.
        model.add_allowed_assignments(
            [U[k], M[k], S[k], T[k]],
            [(0, 0, 0, 0), (1, 0, 1, -1), (1, 0, 1, 1), (1, 1, 2, 0)],
        )

    def key(x: int, y: int):
        return (x, y) if x < y else (y, x)

    def var(table, x: int, y: int):
        return table[key(x, y)]

    for x in range(n):
        model.add(sum(var(U, x, y) for y in range(n) if y != x) == 11)
        model.add(sum(var(M, x, y) for y in range(n) if y != x) == 1)
        for g in range(7):
            model.add(sum(var(S, x, y) * h[y][g] for y in range(n) if y != x)
                      == (2 if h[x][g] else 4))
            model.add(sum(var(T, x, y) * z[y][g] for y in range(n) if y != x) == 0)

    x0 = index[(0, 1, 0)]
    mate = {
        "same": index[(0, 1, 1)],
        "overlap": index[(0, 2, 0)],
        "disjoint": index[(2, 3, 0)],
    }
    if args.mate_type != "none":
        model.add(var(M, x0, mate[args.mate_type]) == 1)

    products = 0
    for x, y in itertools.combinations(range(n), 2):
        sp = []
        tp = []
        for w in range(n):
            if w in (x, y):
                continue
            ps = model.new_int_var(0, 4, "")
            pt = model.new_int_var(-1, 1, "")
            model.add_multiplication_equality(ps, [var(S, x, w), var(S, y, w)])
            model.add_multiplication_equality(pt, [var(T, x, w), var(T, y, w)])
            sp.append(ps)
            tp.append(pt)
            products += 2
        d = sum(h[x][g] * h[y][g] for g in range(7))
        chi = sum(z[x][g] * z[y][g] for g in range(7))
        model.add(sum(sp) + var(S, x, y) == 4 - d)
        model.add(sum(tp) + var(T, x, y) == -chi)

    print(json.dumps({
        "event": "built", "mate_type": args.mate_type,
        "block_variables": len(S), "product_variables": products,
        "proto_variables": len(model.proto.variables),
        "proto_constraints": len(model.proto.constraints),
    }), flush=True)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = args.seconds
    solver.parameters.num_search_workers = args.workers
    solver.parameters.log_search_progress = args.log
    status = solver.solve(model)
    result = {
        "mate_type": args.mate_type, "status": solver.status_name(status),
        "wall_seconds": solver.wall_time, "branches": solver.num_branches,
        "conflicts": solver.num_conflicts, "response_stats": solver.response_stats(),
    }
    print(json.dumps(result), flush=True)
    Path(f"scratch_c2_ST_{args.mate_type}_result.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if status not in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        return

    witness = []
    for x, y in itertools.combinations(range(n), 2):
        p = (solver.value(var(S, x, y)) + solver.value(var(T, x, y))) // 2
        c = (solver.value(var(S, x, y)) - solver.value(var(T, x, y))) // 2
        if p or c:
            witness.append([x, y, p, c])
    Path(f"scratch_c2_ST_{args.mate_type}_witness.json").write_text(
        json.dumps({"vertices": vertices, "blocks": witness}, indent=2) + "\n",
        encoding="utf-8")


if __name__ == "__main__":
    main()
