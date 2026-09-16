"""Independent OR-Tools cross-check of the eight exact E0=78 K2,3 lifts."""

from __future__ import annotations

import argparse
import itertools
import json
import time
from pathlib import Path

from scratch_general_exact_sat import coordinates


INPUT_PATH = Path("scratch_general_e78_local_reps.json")
RESULT_PATH = Path("scratch_general_e78_k23_cpsat.json")


def source_record(support_form="K2,3"):
    source = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    selected = [row for row in source["records"] if row["support_form"] == support_form]
    assert len(selected) == 1
    record = selected[0]
    assert record["orbit_count_direct"] == record["orbit_count_burnside"]
    assert sum(record["orbit_sizes"]) == record["local_graph_count"]
    return record


def make_model(branch_index, support_form="K2,3", source_override=None):
    from ortools.sat.python import cp_model

    model = cp_model.CpModel()
    source = source_record(support_form) if source_override is None else source_override
    representative = source["representatives"][branch_index]
    labels, _index, _full_variables, _full_edge = coordinates()
    supports = [tuple(sorted((label[0] // 2, label[1] // 2))) for label in labels]
    signs = [{symbol // 2: symbol % 2 for symbol in label} for label in labels]
    fibres = {
        support: [u for u, value in enumerate(supports) if value == support]
        for support in itertools.combinations(range(7), 2)
    }
    exceptional = {tuple(support) for support in source["supports_in_fibre_order"]}
    local_vertices = {
        item["outer_index_zero_based"] for item in source["local_vertex_order"]
    }
    local_edges = {
        tuple(sorted(pair))
        for pair in representative["present_edges_outer_indices_zero_based"]
    }

    block_variables = {}
    variable_blocks = []
    for A, B in itertools.combinations(fibres, 2):
        if set(A) & set(B):
            continue
        variable_blocks.append((A, B))
        for u in fibres[A]:
            for v in fibres[B]:
                key = (min(u, v), max(u, v))
                block_variables[key] = model.NewBoolVar(f"e_{key[0]}_{key[1]}")
    assert len(variable_blocks) == 105 and len(block_variables) == 1680

    def edge(u, v):
        if u > v:
            u, v = v, u
        key = (u, v)
        if key in block_variables:
            return block_variables[key]
        A, B = supports[u], supports[v]
        if u in local_vertices and v in local_vertices:
            return int(key in local_edges)
        if A == B:
            return int(sum(signs[u][group] != signs[v][group] for group in A) == 1)
        return 0

    permutation_blocks = 0
    one_sided_blocks = 0
    unrestricted_low_low_blocks = 0
    for A, B in variable_blocks:
        if A in exceptional and B in exceptional:
            unrestricted_low_low_blocks += 1
            continue
        if A not in exceptional and B not in exceptional:
            permutation_blocks += 1
            for u in fibres[A]:
                model.AddExactlyOne(edge(u, v) for v in fibres[B])
            for v in fibres[B]:
                model.AddAtMostOne(edge(u, v) for u in fibres[A])
        else:
            one_sided_blocks += 1
            high, low = (A, B) if A not in exceptional else (B, A)
            for v in fibres[low]:
                model.AddExactlyOne(edge(u, v) for u in fibres[high])
    assert permutation_blocks + one_sided_blocks + unrestricted_low_low_blocks == 105

    # Independently reconstruct the redundant support-aggregate BP rows.
    redundant_total_rows = 0
    forced_block_rows = 0
    for F in sorted(exceptional):
        disjoint_low = [G for G in sorted(exceptional) if set(F).isdisjoint(G)]
        for u in fibres[F]:
            same_degree = sum(edge(u, v) == 1 for v in fibres[F] if v != u)
            overlap_neighbours = [
                v
                for G in exceptional
                if G != F and set(F) & set(G)
                for v in fibres[G]
                if edge(u, v) == 1
            ]
            rows = [[edge(u, v) for v in fibres[G]] for G in disjoint_low]
            required_total = len(disjoint_low) + same_degree - 2
            model.Add(sum(value for row in rows for value in row) == required_total)
            redundant_total_rows += 1
            possibilities = []
            for values in itertools.product(range(5), repeat=len(disjoint_low)):
                if sum(values) != required_total:
                    continue
                if all(
                    sum(
                        value
                        for value, G in zip(values, disjoint_low)
                        if group in G
                    )
                    == sum(group in G for G in disjoint_low)
                    - sum(group in supports[v] for v in overlap_neighbours)
                    for group in range(7)
                    if group not in F
                ):
                    possibilities.append(values)
            assert possibilities
            for q, row in enumerate(rows):
                values = {possibility[q] for possibility in possibilities}
                if len(values) == 1:
                    model.Add(sum(row) == next(iter(values)))
                    forced_block_rows += 1
    assert redundant_total_rows == 4 * len(exceptional)

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
                helper = model.NewBoolVar(f"p_{u}_{v}_{w}")
                model.AddMultiplicationEquality(helper, (a, b))
                terms.append(helper)
                products += 1
        model.Add(sum(terms) == 2 - len(set(labels[u]) & set(labels[v])))

    return model, {
        "branch_index": branch_index,
        "support_form": support_form,
        "local_orbit_size": representative["orbit_size"],
        "canonical_local_mask": representative["canonical_mask_hex_over_C24_2"],
        "edge_variables": len(block_variables),
        "product_variables": products,
        "redundant_support_total_rows": redundant_total_rows,
        "forced_low_low_block_rows": forced_block_rows,
        "proto_variables": len(model.Proto().variables),
        "proto_constraints": len(model.Proto().constraints),
    }


def main():
    from ortools.sat.python import cp_model

    parser = argparse.ArgumentParser()
    parser.add_argument("--seconds", type=float, default=30)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--branch", type=int)
    parser.add_argument("--form", choices=("K2,3", "C6"), default="K2,3")
    args = parser.parse_args()
    records = []
    source = source_record(args.form)
    branch_indices = (
        range(source["orbit_count_direct"])
        if args.branch is None else (args.branch,)
    )
    for branch_index in branch_indices:
        started = time.monotonic()
        model, meta = make_model(branch_index, args.form)
        built = time.monotonic()
        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = args.seconds
        solver.parameters.num_search_workers = args.workers
        status = solver.Solve(model)
        records.append({
            "branch_index": branch_index,
            "status": solver.StatusName(status),
            "build_seconds": round(built - started, 3),
            "solve_seconds": round(time.monotonic() - built, 3),
            "meta": meta,
            "branches": solver.NumBranches(),
            "conflicts": solver.NumConflicts(),
        })
        print(json.dumps({
            "branch": branch_index,
            "status": records[-1]["status"],
            "solve_seconds": records[-1]["solve_seconds"],
        }), flush=True)
    result = {
        "model": f"independent OR-Tools exact compact E0=78 {args.form} cross-check",
        "seconds_per_branch": args.seconds,
        "workers": args.workers,
        "coverage_source": str(INPUT_PATH),
        "status": (
            "INFEASIBLE"
            if all(row["status"] == "INFEASIBLE" for row in records)
            else "UNKNOWN"
        ),
        "records": records,
    }
    stem = "k23" if args.form == "K2,3" else "c6"
    output_path = Path(
        f"scratch_general_e78_{stem}_cpsat.json"
        if args.branch is None
        else f"scratch_general_e78_{stem}_cpsat_branch{args.branch:02d}_retry.json"
    )
    output_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "counts": dict(
            (value, sum(row["status"] == value for row in records))
            for value in ("INFEASIBLE", "UNKNOWN", "MODEL_INVALID")
        ),
    }), flush=True)


if __name__ == "__main__":
    main()
