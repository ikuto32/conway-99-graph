"""Independent CP-SAT cross-check of the three exact E0=77 local lifts."""

from __future__ import annotations

import argparse
import itertools
import json
import time
from pathlib import Path

from scratch_general_exact_sat import coordinates, verify


INPUT = Path("scratch_e77_sat_reps.json")
OUTPUT = Path("scratch_e77_sat_cpsat.json")


def source_data():
    source = json.loads(INPUT.read_text(encoding="utf-8"))
    rows = [row for row in source["rows"] if row["local_orbit_count"]]
    assert source["ok"] and len(rows) == 1 and len(rows[0]["representatives"]) == 3
    return rows[0]


def build_model(branch_index):
    from ortools.sat.python import cp_model

    source = source_data()
    representative = source["representatives"][branch_index]
    labels, label_index, full_variables, _ = coordinates()
    supports = tuple(tuple(symbol // 2 for symbol in label) for label in labels)
    signs = tuple({symbol // 2: symbol % 2 for symbol in label} for label in labels)
    fibres = {
        support: tuple(u for u, value in enumerate(supports) if value == support)
        for support in itertools.combinations(range(7), 2)
    }
    exceptional = frozenset(tuple(support) for support in source["supports"])
    high = frozenset(set(fibres) - set(exceptional))
    fixed_local = frozenset(
        tuple(sorted((label_index[tuple(raw[0])], label_index[tuple(raw[1])])))
        for raw in representative["local_graph_edges"]
    )

    model = cp_model.CpModel()
    variables = {}
    disjoint_blocks = []
    for A, B in itertools.combinations(fibres, 2):
        if not set(A).isdisjoint(B):
            continue
        disjoint_blocks.append((A, B))
        for u in fibres[A]:
            for v in fibres[B]:
                key = tuple(sorted((u, v)))
                variables[key] = model.NewBoolVar(f"e_{key[0]}_{key[1]}")

    def edge(u, v):
        if u == v:
            return 0
        key = tuple(sorted((u, v)))
        if key in variables:
            return variables[key]
        A, B = supports[u], supports[v]
        if A == B:
            if A in exceptional:
                return int(key in fixed_local)
            return int(sum(signs[u][g] != signs[v][g] for g in A) == 1)
        assert set(A) & set(B)
        return int(A in exceptional and B in exceptional and key in fixed_local)

    block_equalities = 0
    for A, B in disjoint_blocks:
        if A in high:
            for v in fibres[B]:
                model.Add(sum(edge(u, v) for u in fibres[A]) == 1)
                block_equalities += 1
        if B in high:
            for u in fibres[A]:
                model.Add(sum(edge(u, v) for v in fibres[B]) == 1)
                block_equalities += 1

    bp_equalities = 0
    for u, own_label in enumerate(labels):
        own = set(own_label)
        for symbol in range(14):
            model.Add(sum(
                edge(u, v)
                for v, other in enumerate(labels)
                if u != v and symbol in other
            ) == (1 if symbol in own or (symbol ^ 1) in own else 2))
            bp_equalities += 1

    product_variables = pair_equalities = 0
    for u, v in itertools.combinations(range(84), 2):
        terms = [edge(u, v)]
        for w in range(84):
            if w in (u, v):
                continue
            a, b = edge(u, w), edge(v, w)
            if isinstance(a, int) and a == 0 or isinstance(b, int) and b == 0:
                continue
            if isinstance(a, int) and a == 1:
                terms.append(b)
            elif isinstance(b, int) and b == 1:
                terms.append(a)
            elif a is b:
                terms.append(a)
            else:
                product = model.NewBoolVar(f"p_{u}_{v}_{w}")
                model.AddMultiplicationEquality(product, (a, b))
                terms.append(product)
                product_variables += 1
        model.Add(sum(terms) == 2 - len(set(labels[u]) & set(labels[v])))
        pair_equalities += 1

    return model, variables, edge, full_variables, {
        "branch_index": branch_index,
        "edge_variables": len(variables),
        "product_variables": product_variables,
        "block_equalities": block_equalities,
        "bp_equalities": bp_equalities,
        "pair_equalities": pair_equalities,
    }


def solve_branch(branch_index, seconds, workers):
    from ortools.sat.python import cp_model

    started = time.monotonic()
    model, _variables, edge, full_variables, meta = build_model(branch_index)
    built = time.monotonic()
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = 7700 + branch_index
    status = solver.Solve(model)
    record = {
        "branch_index": branch_index,
        "status": solver.StatusName(status),
        "build_seconds": round(built - started, 3),
        "solve_seconds": round(time.monotonic() - built, 3),
        "branches": solver.NumBranches(),
        "conflicts": solver.NumConflicts(),
        "wall_time": solver.WallTime(),
        "meta": meta,
        "formal_proof_certificate": None,
    }
    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        selected = set()
        for pair, identifier in full_variables.items():
            value = edge(*pair)
            if isinstance(value, int):
                chosen = bool(value)
            else:
                chosen = bool(solver.Value(value))
            if chosen:
                selected.add(identifier)
        checked = verify(selected)
        record["verification"] = {key: value for key, value in checked.items() if key != "edges"}
        record["positive_full_edge_variables"] = sorted(selected) if checked["ok"] else []
    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seconds", type=float, default=60)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--branch", type=int, choices=range(3))
    args = parser.parse_args()
    branches = [args.branch] if args.branch is not None else list(range(3))
    records = [solve_branch(index, args.seconds, args.workers) for index in branches]
    result = {
        "model": "independent CP-SAT exact E0=77 local-representative lifts",
        "solver": "OR-Tools CP-SAT",
        "seconds_per_branch": args.seconds,
        "workers": args.workers,
        "coverage_source": str(INPUT),
        "status": (
            "SAT" if any(row["status"] in ("FEASIBLE", "OPTIMAL") for row in records)
            else "UNSAT" if len(records) == 3 and all(row["status"] == "INFEASIBLE" for row in records)
            else "UNKNOWN"
        ),
        "proof_status": "no independently checked UNSAT certificate",
        "records": records,
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "records": [
            [row["branch_index"], row["status"], row["solve_seconds"]]
            for row in records
        ],
    }))


if __name__ == "__main__":
    main()
