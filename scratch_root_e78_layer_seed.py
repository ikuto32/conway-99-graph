"""Lift one E0=78 all-P4 local seed through BP and fibre-pair equations.

The input local graph fixes every edge whose support fibres overlap.  The
remaining variables join disjoint supports.  Fifteen ordinary fibres are
fixed C4s with their exact linear outside-at-most-one rule; all six equations
inside each exceptional P4 are also imposed exactly.
"""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

from ortools.sat.python import cp_model

from scratch_fibre_layer_incremental import layer_diagnostics, support_data
from scratch_general_v2_cpsat_energy import M, O, canon, metrics, read_seed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--orbit", type=int, choices=(3, 19), required=True)
    parser.add_argument("--rep", type=int, default=0)
    parser.add_argument("--input", default="scratch_bp_linearized_v2_best.json")
    parser.add_argument("--output", required=True)
    parser.add_argument("--seconds", type=float, default=120.0)
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--seed", type=int, default=7801)
    args = parser.parse_args()

    scaffold, current, labels = read_seed(args.input)
    supports_of, fibres = support_data(labels)
    audit = json.loads(Path("scratch_root_e78_p4_local.json").read_text(encoding="utf-8"))
    row = next(r for r in audit["rows"] if r["orbit_index"] == args.orbit)
    representatives = row["canonical_local_graph_representatives"]
    if not 0 <= args.rep < len(representatives):
        raise ValueError(
            f"rep {args.rep} outside 0..{len(representatives) - 1}"
        )
    exceptional = {tuple(support) for support in row["supports"]}
    ordinary = set(fibres) - exceptional

    label_to_vertex = {
        tuple(symbol - 1 for symbol in label): u
        for u, label in enumerate(labels)
    }
    local_edges = {
        canon(label_to_vertex[tuple(left)], label_to_vertex[tuple(right)])
        for left, right in representatives[args.rep]
    }

    model = cp_model.CpModel()
    pairs = list(itertools.combinations(range(M), 2))
    x = {pair: model.NewBoolVar(f"e_{pair[0]}_{pair[1]}") for pair in pairs}

    def edge(u, v):
        return x[canon(u, v)]

    for u, label in enumerate(labels):
        groups = {(symbol - 1) // 2 for symbol in label}
        for symbol in range(1, 15):
            model.Add(
                sum(edge(u, v) for v, other in enumerate(labels)
                    if u != v and symbol in other)
                == (1 if (symbol - 1) // 2 in groups else 2)
            )

    # All same/overlapping-support edges are determined by the local graph;
    # ordinary fibres contribute their unique coordinate C4s.
    for u, v in pairs:
        su, sv = supports_of[u], supports_of[v]
        if not set(su) & set(sv):
            continue
        if su == sv and su in ordinary:
            value = int(len(set(labels[u]) & set(labels[v])) == 1)
        else:
            value = int((u, v) in local_edges)
        model.Add(x[(u, v)] == value)

    # Exact same-fibre equations for every ordinary C4 are linear.
    for support in ordinary:
        fibre = fibres[support]
        fibre_set = set(fibre)
        for w in range(M):
            if w not in fibre_set:
                model.Add(sum(edge(w, u) for u in fibre) <= 1)

    # For a P4, present edges require zero outside common neighbours.  Its
    # missing side and two diagonals require a small exact AND sum.
    product_count = 0
    for support in exceptional:
        fibre = fibres[support]
        for u, v in itertools.combinations(fibre, 2):
            fixed_common = len(set(labels[u]) & set(labels[v]))
            fixed_edge = int((u, v) in local_edges)
            target_outer_common = 2 - fixed_common - fixed_edge
            internal_common = sum(
                canon(u, w) in local_edges and canon(v, w) in local_edges
                for w in fibre if w not in (u, v)
            )
            outside_target = target_outer_common - internal_common
            assert outside_target in (0, 1)
            outside = [w for w in range(M) if w not in fibre]
            if outside_target == 0:
                for w in outside:
                    model.Add(edge(u, w) + edge(v, w) <= 1)
            else:
                products = []
                for w in outside:
                    z = model.NewBoolVar(f"z_{u}_{v}_{w}")
                    model.AddMultiplicationEquality(z, (edge(u, w), edge(v, w)))
                    products.append(z)
                    product_count += 1
                model.Add(sum(products) == 1)

    current_local = {(u - O, v - O) for u, v in current}
    for pair, var in x.items():
        model.AddHint(var, int(pair in current_local))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = args.seconds
    solver.parameters.num_search_workers = args.workers
    solver.parameters.random_seed = args.seed
    solver.parameters.stop_after_first_solution = True
    solver.parameters.log_search_progress = False
    status = solver.Solve(model)
    record = {
        "status": solver.StatusName(status),
        "wall_seconds": solver.WallTime(),
        "branches": solver.NumBranches(),
        "conflicts": solver.NumConflicts(),
        "orbit": args.orbit,
        "local_representative": args.rep,
        "ordinary_c4_fibres": len(ordinary),
        "exceptional_p4_fibres": len(exceptional),
        "product_variables": product_count,
    }
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        chosen = {
            (O + u, O + v) for pair, var in x.items()
            if solver.Value(var) for u, v in [pair]
        }
        info, adj = metrics(scaffold, chosen)
        layer_info, fibre_rows = layer_diagnostics(
            scaffold, chosen, labels, fibres
        )
        assert info == layer_info
        assert info["edge_count"] == 693 and info["io_energy"] == 0
        assert all(len(a) == 14 for a in adj)
        assert sum(r["bad"] for r in fibre_rows.values()) == 0
        info.update({
            "method": "E0=78 all-P4 local seed lifted through BP and all same-fibre equations",
            "claim_boundary": "necessary layer seed only; cross-fibre pair equations remain unchecked",
            "orbit": args.orbit,
            "local_representative": args.rep,
            "exceptional_supports": [list(s) for s in sorted(exceptional)],
            "same_support_bad_total": 0,
            "same_support_energy_total": 0,
            "solver": record,
        })
        edges = info.pop("edges")
        info["edges"] = edges
        Path(args.output).write_text(
            json.dumps(info, indent=2) + "\n", encoding="utf-8"
        )
        record.update({
            "energy": info["energy"],
            "bad_pairs": info["bad_pairs"],
            "output": args.output,
        })
    print(json.dumps(record), flush=True)


if __name__ == "__main__":
    main()
