"""Exact compact CP-SAT model for the involution (C2) branch.

An involution of a Conway 99-graph has one fixed root.  On its 14 neighbours
it flips each of the seven matched pairs, and therefore sends an outer label
{a,b} to {a^1,b^1}.  The model identifies all outer edge variables under this
action.  An outer vertex and its image are forced nonadjacent: if they were
adjacent, their unique common neighbour would be fixed by the involution, but
the only fixed vertex is the root and the root has no outer neighbours.

The common-neighbour encoding is compact but exact by the same global wedge
count used in scratch_full_cpsat.py.  A returned model is always expanded and
checked on all 99 vertices and 4,851 unordered pairs.
"""

from __future__ import annotations

import argparse
import itertools
import json
import time
from pathlib import Path

from ortools.sat.python import cp_model

from scratch_bp_seed import expand_and_check


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seconds", type=float, default=180.0)
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--log", action="store_true")
    args = parser.parse_args()

    labels = [
        pair
        for pair in itertools.combinations(range(14), 2)
        if pair[0] // 2 != pair[1] // 2
    ]
    label_index = {label: i for i, label in enumerate(labels)}
    tau = [label_index[tuple(sorted((a ^ 1, b ^ 1)))] for a, b in labels]
    assert all(tau[tau[u]] == u and tau[u] != u for u in range(84))

    def pair(u: int, v: int) -> tuple[int, int]:
        return (u, v) if u < v else (v, u)

    def orbit_key(u: int, v: int) -> tuple[int, int]:
        p = pair(u, v)
        q = pair(tau[u], tau[v])
        return min(p, q)

    model = cp_model.CpModel()
    orbit_var: dict[tuple[int, int], cp_model.IntVar] = {}
    for u, v in itertools.combinations(range(84), 2):
        if v == tau[u]:
            continue
        key = orbit_key(u, v)
        if key not in orbit_var:
            orbit_var[key] = model.new_bool_var("")
    assert len(orbit_var) == 1722

    def edge(u: int, v: int) -> cp_model.IntVar | None:
        if v == tau[u]:
            return None  # the forced nonedge u--tau(u)
        return orbit_var[orbit_key(u, v)]

    # Exact rooted coordinate equations BP = P A0.
    for u, label in enumerate(labels):
        label_set = set(label)
        for symbol in range(14):
            terms = []
            for v, other in enumerate(labels):
                if u != v and symbol in other:
                    value = edge(u, v)
                    if value is not None:
                        terms.append(value)
            target = 1 if symbol in label_set or (symbol ^ 1) in label_set else 2
            model.add(sum(terms) == target)

    representatives = []
    fixed_pair_orbits = 0
    for u, v in itertools.combinations(range(84), 2):
        transformed = pair(tau[u], tau[v])
        if pair(u, v) <= transformed:
            representatives.append((u, v))
            fixed_pair_orbits += pair(u, v) == transformed
    assert len(representatives) == 1764
    assert fixed_pair_orbits == 42

    products = 0
    reused_products = 0
    for u, v in representatives:
        terms: list[cp_model.IntVar] = []
        for w in range(84):
            if w == u or w == v:
                continue
            a = edge(u, w)
            b = edge(v, w)
            if a is None or b is None:
                continue
            if a is b:
                terms.append(a)
                reused_products += 1
                continue
            both = model.new_bool_var("")
            model.add_bool_or([~a, ~b, both])
            terms.append(both)
            products += 1
        direct = edge(u, v)
        expression = sum(terms) + (direct if direct is not None else 0)
        target = 2 - len(set(labels[u]).intersection(labels[v]))
        model.add(expression <= target)

    print(
        json.dumps(
            {
                "event": "built",
                "edge_orbit_variables": len(orbit_var),
                "pair_orbits": len(representatives),
                "fixed_pair_orbits": fixed_pair_orbits,
                "product_variables": products,
                "reused_product_literals": reused_products,
                "proto_variables": len(model.proto.variables),
                "proto_constraints": len(model.proto.constraints),
            }
        ),
        flush=True,
    )
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = args.seconds
    solver.parameters.num_search_workers = args.workers
    solver.parameters.log_search_progress = args.log
    status = solver.solve(model)
    record = {
        "status": solver.status_name(status),
        "wall_seconds": solver.wall_time,
        "branches": solver.num_branches,
        "conflicts": solver.num_conflicts,
        "response_stats": solver.response_stats(),
    }
    print(json.dumps(record), flush=True)
    Path("scratch_c2_cpsat_result.json").write_text(
        json.dumps(record, indent=2) + "\n", encoding="utf-8"
    )
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return

    # Give expand_and_check its expected independent edge-ID interface.
    edge_ids = {
        p: i for i, p in enumerate(itertools.combinations(range(84), 2), 1)
    }
    positive = set()
    for (u, v), i in edge_ids.items():
        value = edge(u, v)
        if value is not None and solver.value(value):
            positive.add(i)
    result = expand_and_check(labels, edge_ids, positive)
    assert result["energy"] == 0 and result["bad_pairs"] == 0
    Path("scratch_c2_solution.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({key: result[key] for key in result if key != "edges"}), flush=True)


if __name__ == "__main__":
    main()
