"""Exact rooted CP-SAT model for srg(99,14,1,2).

The root scaffold is fixed without loss of generality.  The only primary
variables are the 3,486 possible edges of the 84-vertex outer graph.  Linear
incidence constraints enforce every equation involving one of the 14 inner
vertices.  Boolean products then enforce every outer/outer common-neighbour
equation.  Any FEASIBLE result is expanded and checked from scratch before an
edge list is saved; UNKNOWN is never treated as evidence of infeasibility.
"""

from __future__ import annotations

import argparse
import itertools
import json
import time
from pathlib import Path

from ortools.sat.python import cp_model

from scratch_bp_seed import expand_and_check


def edge_var(edge: list[list[cp_model.IntVar | None]], u: int, v: int) -> cp_model.IntVar:
    if u > v:
        u, v = v, u
    value = edge[u][v]
    assert value is not None
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seconds", type=float, default=180.0)
    parser.add_argument("--workers", type=int, default=32)
    parser.add_argument("--seed", default="scratch_bp_seed.json")
    parser.add_argument("--log", action="store_true")
    parser.add_argument("--compact", action="store_true")
    args = parser.parse_args()

    labels = [
        pair
        for pair in itertools.combinations(range(14), 2)
        if pair[0] // 2 != pair[1] // 2
    ]
    assert len(labels) == 84
    model = cp_model.CpModel()
    edge: list[list[cp_model.IntVar | None]] = [[None] * 84 for _ in range(84)]
    edge_ids: dict[tuple[int, int], int] = {}
    for index, (u, v) in enumerate(itertools.combinations(range(84), 2), 1):
        edge[u][v] = model.new_bool_var("")
        edge_ids[u, v] = index

    # B P = P A_0.  Summing these 14 equations for a fixed row also forces
    # the outer degree to 12, since every neighbour label has two symbols.
    for u, label in enumerate(labels):
        label_set = set(label)
        for symbol in range(14):
            terms = [
                edge_var(edge, u, v)
                for v, other in enumerate(labels)
                if u != v and symbol in other
            ]
            target = 1 if symbol in label_set or (symbol ^ 1) in label_set else 2
            model.add(sum(terms) == target)

    products = 0
    for u in range(84):
        lu = set(labels[u])
        for v in range(u + 1, 84):
            common_terms = []
            for w in range(84):
                if w == u or w == v:
                    continue
                a = edge_var(edge, u, w)
                b = edge_var(edge, v, w)
                both = model.new_bool_var("")
                if not args.compact:
                    model.add_implication(both, a)
                    model.add_implication(both, b)
                model.add_bool_or([~a, ~b, both])
                common_terms.append(both)
                products += 1
            target = 2 - len(lu.intersection(labels[v]))
            expression = sum(common_terms) + edge_var(edge, u, v)
            # With BP enforced, every row has degree 12.  Hence the global
            # sum of actual outer common-neighbour counts is 84*C(12,2),
            # exactly the sum of these targets (5544).  In compact mode the
            # one-way wedge clauses plus all upper bounds are therefore exact:
            # no row can be strictly below target unless another exceeds it.
            model.add(expression <= target if args.compact else expression == target)

    hinted = 0
    seed_path = Path(args.seed)
    if seed_path.exists():
        seed = json.loads(seed_path.read_text(encoding="utf-8"))
        selected = {
            (a - 16, b - 16)
            for a, b in seed.get("edges", [])
            if a >= 16 and b >= 16
        }
        for u, v in itertools.combinations(range(84), 2):
            model.add_hint(edge_var(edge, u, v), int((u, v) in selected))
            hinted += 1

    built = time.monotonic()
    print(
        json.dumps(
            {
                "event": "built",
                "edge_variables": len(edge_ids),
                "product_variables": products,
                "hints": hinted,
                "compact": args.compact,
                "model_proto_variables": len(model.proto.variables),
                "model_proto_constraints": len(model.proto.constraints),
            }
        ),
        flush=True,
    )
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = args.seconds
    solver.parameters.num_search_workers = args.workers
    solver.parameters.log_search_progress = args.log
    solver.parameters.cp_model_presolve = True
    status = solver.solve(model)
    record = {
        "event": "result",
        "status": solver.status_name(status),
        "build_seconds": round(built - globals().get("STARTED", built), 3),
        "solve_wall_seconds": solver.wall_time,
        "branches": solver.num_branches,
        "conflicts": solver.num_conflicts,
    }
    print(json.dumps(record), flush=True)
    Path("scratch_full_cpsat_result.json").write_text(
        json.dumps(record, indent=2) + "\n", encoding="utf-8"
    )
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return

    positive = {
        edge_ids[u, v]
        for u, v in itertools.combinations(range(84), 2)
        if solver.value(edge_var(edge, u, v))
    }
    result = expand_and_check(labels, edge_ids, positive)
    assert result["energy"] == 0
    assert result["bad_pairs"] == 0
    Path("scratch_full_cpsat_solution.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({key: result[key] for key in result if key != "edges"}), flush=True)


STARTED = time.monotonic()
if __name__ == "__main__":
    main()
