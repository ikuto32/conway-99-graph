"""Necessary quotient-matrix search for the C2 automorphism branch.

For a C2-invariant outer graph, write each 2x2 edge block as
``p I + c X`` and put S=p+c.  The 42 quotient vertices are a base edge
of K7 together with a parity bit.  Any Conway graph in this branch must
satisfy

    S^2 + S = 4 J - H H^T + 12 I,
    S H       = 4 J - 2 H,

where H is the 42 by 7 base-edge incidence matrix.  Off diagonal entries
of S are 0, 1, or 2.  The entries equal to 2 form a perfect matching.

This script solves just these necessary conditions.  It supports the three
safe WLOG cases for the matching mate of quotient vertex (01, parity 0):
same base edge, overlapping base edge, or disjoint base edge.
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
    ap.add_argument(
        "--mate-type", choices=("none", "same", "overlap", "disjoint"),
        default="none",
    )
    ap.add_argument("--log", action="store_true")
    args = ap.parse_args()

    vertices = [(i, j, r) for i in range(7) for j in range(i + 1, 7)
                for r in range(2)]
    index = {x: k for k, x in enumerate(vertices)}
    n = len(vertices)
    assert n == 42

    model = cp_model.CpModel()
    support: dict[tuple[int, int], cp_model.IntVar] = {}
    double: dict[tuple[int, int], cp_model.IntVar] = {}
    sval: dict[tuple[int, int], cp_model.LinearExpr] = {}
    for x, y in itertools.combinations(range(n), 2):
        key = (x, y)
        support[key] = model.new_bool_var("")
        double[key] = model.new_bool_var("")
        model.add(double[key] <= support[key])
        sval[key] = support[key] + double[key]

    def key(x: int, y: int) -> tuple[int, int]:
        return (x, y) if x < y else (y, x)

    def u(x: int, y: int):
        return support[key(x, y)]

    def m(x: int, y: int):
        return double[key(x, y)]

    def s(x: int, y: int):
        return sval[key(x, y)]

    # S has row sum 12, with exactly one double entry; equivalently the
    # simple support is 11-regular and the double entries form a 1-factor.
    for x in range(n):
        model.add(sum(u(x, y) for y in range(n) if y != x) == 11)
        model.add(sum(m(x, y) for y in range(n) if y != x) == 1)

    # S H = 4J - 2H.
    for x, (i, j, _r) in enumerate(vertices):
        for g in range(7):
            model.add(
                sum(s(x, y) for y, (a, b, _q) in enumerate(vertices)
                    if y != x and g in (a, b))
                == (2 if g in (i, j) else 4)
            )

    # The three orbits of possible matching mates under 2^6:S7.
    x0 = index[(0, 1, 0)]
    canonical_mate = {
        "same": index[(0, 1, 1)],
        "overlap": index[(0, 2, 0)],
        "disjoint": index[(2, 3, 0)],
    }
    if args.mate_type != "none":
        model.add(m(x0, canonical_mate[args.mate_type]) == 1)

    # Off-diagonal part of S^2+S=4J-HH^T+12I.
    products = 0
    for x, y in itertools.combinations(range(n), 2):
        terms = []
        for z in range(n):
            if z in (x, y):
                continue
            prod = model.new_int_var(0, 4, "")
            model.add_multiplication_equality(prod, [s(x, z), s(y, z)])
            terms.append(prod)
            products += 1
        base_x = set(vertices[x][:2])
        base_y = set(vertices[y][:2])
        target = 4 - len(base_x & base_y)
        model.add(sum(terms) + s(x, y) == target)

    print(json.dumps({
        "event": "built", "mate_type": args.mate_type,
        "edge_pairs": len(sval), "product_variables": products,
        "proto_variables": len(model.proto.variables),
        "proto_constraints": len(model.proto.constraints),
    }), flush=True)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = args.seconds
    solver.parameters.num_search_workers = args.workers
    solver.parameters.log_search_progress = args.log
    status = solver.solve(model)
    result = {
        "mate_type": args.mate_type,
        "status": solver.status_name(status),
        "wall_seconds": solver.wall_time,
        "branches": solver.num_branches,
        "conflicts": solver.num_conflicts,
        "response_stats": solver.response_stats(),
    }
    print(json.dumps(result), flush=True)
    Path(f"scratch_c2_S_{args.mate_type}_result.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return

    matrix = [[0] * n for _ in range(n)]
    for x, y in itertools.combinations(range(n), 2):
        matrix[x][y] = matrix[y][x] = solver.value(s(x, y))
    witness = {"vertices": vertices, "S": matrix}
    Path(f"scratch_c2_S_{args.mate_type}_witness.json").write_text(
        json.dumps(witness, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
