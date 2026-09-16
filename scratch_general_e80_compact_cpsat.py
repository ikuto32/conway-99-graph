"""Corrected independent OR-Tools cross-check of five exact E0=80 branches.

C4--P4 blocks carry only the P4-side degree-one equations.  They are not
incorrectly promoted to two-sided permutation matrices.
"""

from __future__ import annotations

import argparse
import itertools
import json
import time
from pathlib import Path

from scratch_general_e80_exact_sat import build as build_orbits
from scratch_general_e80_local_audit import LABELS as LOCAL_LABELS, SUPPORTS
from scratch_general_exact_sat import coordinates


RESULT_PATH = Path("scratch_general_e80_corrected_cpsat.json")


def make_model(branch_index):
    from ortools.sat.python import cp_model

    model = cp_model.CpModel()
    orbit_meta = build_orbits()
    branch = orbit_meta["branches"][branch_index]
    local_edges = {tuple(edge) for edge in branch["local_edges"]}
    labels, index, _full_variables, _full_edge = coordinates()
    supports = [tuple(sorted((label[0] // 2, label[1] // 2))) for label in labels]
    signs = [{symbol // 2: symbol % 2 for symbol in label} for label in labels]
    fibres = {
        support: [u for u, value in enumerate(supports) if value == support]
        for support in itertools.combinations(range(7), 2)
    }
    local_global = [index[label] for label in LOCAL_LABELS]
    global_to_local = {u: q for q, u in enumerate(local_global)}
    exceptional = set(tuple(support) for support in SUPPORTS)

    block_variables = {}
    variable_blocks = []
    for A, B in itertools.combinations(fibres, 2):
        if set(A) & set(B) or (A in exceptional and B in exceptional):
            continue
        variable_blocks.append((A, B))
        for u in fibres[A]:
            for v in fibres[B]:
                key = (min(u, v), max(u, v))
                block_variables[key] = model.NewBoolVar(f"e_{key[0]}_{key[1]}")

    def edge(u, v):
        if u > v:
            u, v = v, u
        if (u, v) in block_variables:
            return block_variables[u, v]
        A, B = supports[u], supports[v]
        if u in global_to_local and v in global_to_local:
            return int(tuple(sorted((global_to_local[u], global_to_local[v]))) in local_edges)
        if A == B:
            return int(sum(signs[u][g] != signs[v][g] for g in A) == 1)
        return 0

    for A, B in variable_blocks:
        if A not in exceptional and B not in exceptional:
            for u in fibres[A]:
                model.AddExactlyOne(edge(u, v) for v in fibres[B])
            for v in fibres[B]:
                model.AddAtMostOne(edge(u, v) for u in fibres[A])
        else:
            high, low = (A, B) if A not in exceptional else (B, A)
            for v in fibres[low]:
                model.AddExactlyOne(edge(u, v) for u in fibres[high])

    for u, label in enumerate(labels):
        own = set(label)
        for symbol in range(14):
            terms = [edge(u, v) for v, other in enumerate(labels) if u != v and symbol in other]
            target = 1 if symbol in own or (symbol ^ 1) in own else 2
            model.Add(sum(terms) == target)

    products = 0
    for u, v in itertools.combinations(range(84), 2):
        terms = [edge(u, v)]
        for w in range(84):
            if w in (u, v):
                continue
            a, b = edge(u, w), edge(v, w)
            if isinstance(a, int) and isinstance(b, int):
                terms.append(a * b)
            elif isinstance(a, int):
                if a:
                    terms.append(b)
            elif isinstance(b, int):
                if b:
                    terms.append(a)
            elif a is b:
                terms.append(a)
            else:
                z = model.NewBoolVar(f"p_{u}_{v}_{w}")
                model.AddMultiplicationEquality(z, (a, b))
                terms.append(z)
                products += 1
        target = 2 - len(set(labels[u]) & set(labels[v]))
        model.Add(sum(terms) == target)

    return model, {
        "branch_index": branch_index,
        "branch": branch["branch"],
        "edge_variables": len(block_variables),
        "product_variables": products,
        "proto_variables": len(model.Proto().variables),
        "proto_constraints": len(model.Proto().constraints),
    }


def main():
    from ortools.sat.python import cp_model

    parser = argparse.ArgumentParser()
    parser.add_argument("--seconds", type=float, default=30)
    parser.add_argument("--workers", type=int, default=4)
    args = parser.parse_args()
    records = []
    for branch_index in range(5):
        started = time.monotonic()
        model, meta = make_model(branch_index)
        built = time.monotonic()
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = args.seconds
        solver.parameters.num_search_workers = args.workers
        status = solver.Solve(model)
        records.append({
            "branch_index": branch_index,
            "branch": meta["branch"],
            "status": solver.StatusName(status),
            "build_seconds": round(built - started, 3),
            "solve_seconds": round(time.monotonic() - built, 3),
            "meta": meta,
            "branches": solver.NumBranches(),
            "conflicts": solver.NumConflicts(),
        })
    result = {
        "model": "corrected independent OR-Tools exact compact E0=80 cross-check",
        "seconds_per_branch": args.seconds,
        "workers": args.workers,
        "status": (
            "INFEASIBLE" if all(row["status"] == "INFEASIBLE" for row in records)
            else "UNKNOWN"
        ),
        "records": records,
    }
    RESULT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "records": [(r["branch"], r["status"], r["solve_seconds"]) for r in records]}), flush=True)


if __name__ == "__main__":
    main()
