"""Project a candidate onto BP plus all 126 same-support pair equations."""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

from ortools.sat.python import cp_model

from scratch_general_v2_cpsat_energy import O, M, canon, metrics, read_seed


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--seconds", type=float, default=120)
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--satisfaction", action="store_true")
    args = parser.parse_args()

    scaffold, incumbent, labels = read_seed(args.input)
    model = cp_model.CpModel()
    pairs = list(itertools.combinations(range(M), 2))
    x = {pair: model.NewBoolVar(f"e_{pair[0]}_{pair[1]}") for pair in pairs}

    def edge(u, v):
        return x[canon(u, v)]

    # Exact BP rows.
    for u, label in enumerate(labels):
        groups = {(symbol - 1) // 2 for symbol in label}
        for symbol in range(1, 15):
            model.Add(
                sum(edge(u, v) for v, other in enumerate(labels)
                    if u != v and symbol in other)
                == (1 if (symbol - 1) // 2 in groups else 2)
            )

    supports = [tuple(sorted((symbol - 1) // 2 for symbol in label)) for label in labels]
    fibres = {
        support: [u for u, value in enumerate(supports) if value == support]
        for support in sorted(set(supports))
    }
    products = 0
    constrained_pairs = 0
    for fibre in fibres.values():
        assert len(fibre) == 4
        for u, v in itertools.combinations(fibre, 2):
            terms = [edge(u, v)]
            for w in range(M):
                if w in (u, v):
                    continue
                z = model.NewBoolVar(f"z_{u}_{v}_{w}")
                model.AddMultiplicationEquality(z, (edge(u, w), edge(v, w)))
                terms.append(z)
                products += 1
            fixed_common = len(set(labels[u]) & set(labels[v]))
            model.Add(sum(terms) == 2 - fixed_common)
            constrained_pairs += 1
    assert constrained_pairs == 126 and products == 126 * 82

    incumbent_local = {(u - O, v - O) for u, v in incumbent}
    overlap = sum(x[pair] for pair in incumbent_local)
    if not args.satisfaction:
        model.Maximize(overlap)
    for pair, var in x.items():
        model.AddHint(var, int(pair in incumbent_local))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = args.seconds
    solver.parameters.num_search_workers = args.workers
    solver.parameters.random_seed = args.seed
    solver.parameters.log_search_progress = True
    status = solver.Solve(model)
    record = {
        "status": solver.StatusName(status),
        "mode": "satisfaction" if args.satisfaction else "maximize_overlap",
        "source": args.input,
        "wall_seconds": solver.WallTime(),
        "objective_overlap": solver.ObjectiveValue(),
        "best_bound_overlap": solver.BestObjectiveBound(),
        "products": products,
        "same_support_pair_equations": constrained_pairs,
        "branches": solver.NumBranches(),
        "conflicts": solver.NumConflicts(),
    }
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        chosen = {(O + u, O + v) for (u, v), var in x.items() if solver.Value(var)}
        info, adj = metrics(scaffold, chosen)
        assert info["io_energy"] == 0 and info["edge_count"] == 693
        assert all(len(row) == 14 for row in adj)
        layer_bad = 0
        for fibre in fibres.values():
            for u, v in itertools.combinations(fibre, 2):
                gu, gv = O + u, O + v
                residual = len(adj[gu] & adj[gv]) + int(gv in adj[gu]) - 2
                layer_bad += residual != 0
        assert layer_bad == 0
        record["outer_overlap"] = len(chosen & incumbent)
        record["outer_hamming_distance"] = len(chosen ^ incumbent)
        record["same_support_bad_pairs"] = layer_bad
        record.update(info)
    Path(args.output).write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in record.items() if k != "edges"}), flush=True)


if __name__ == "__main__":
    main()
