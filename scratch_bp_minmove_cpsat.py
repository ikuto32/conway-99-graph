"""Find a smallest nontrivial move inside the exact rooted BP polytope.

This diagnostic keeps all 1,176 inner--outer common-neighbour equations exact.
Starting from a BP-feasible 504-edge outer graph, it minimizes the number of
deleted incumbent edges while forbidding the incumbent itself.  Because every
feasible point has 504 edges, twice that objective is the edge-set Hamming
distance.  A small optimum supplies a move generator for BP-preserving search.
"""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

from ortools.sat.python import cp_model

from scratch_bp_seed import expand_and_check


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--seconds", type=float, default=120.0)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--seed", type=int, default=1)
    args = parser.parse_args()

    labels = [
        pair
        for pair in itertools.combinations(range(14), 2)
        if pair[0] // 2 != pair[1] // 2
    ]
    pairs = list(itertools.combinations(range(84), 2))
    edge_id = {pair: i + 1 for i, pair in enumerate(pairs)}
    payload = json.loads(Path(args.input).read_text(encoding="utf-8"))
    incumbent = {
        (a - 16, b - 16)
        for a, b in payload["edges"]
        if a >= 16 and b >= 16
    }
    assert len(incumbent) == 504

    model = cp_model.CpModel()
    x = {pair: model.new_bool_var(f"e_{pair[0]}_{pair[1]}") for pair in pairs}

    def edge(u: int, v: int):
        return x[(u, v) if u < v else (v, u)]

    for u, label in enumerate(labels):
        own = set(label)
        for symbol in range(14):
            terms = [
                edge(u, v)
                for v, other in enumerate(labels)
                if u != v and symbol in other
            ]
            target = 1 if symbol in own or (symbol ^ 1) in own else 2
            model.add(sum(terms) == target)

    model.add(sum(x.values()) == 504)
    overlap = sum(x[pair] for pair in incumbent)
    model.add(overlap <= 503)
    model.maximize(overlap)
    for pair, var in x.items():
        model.add_hint(var, int(pair in incumbent))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = args.seconds
    solver.parameters.num_search_workers = args.workers
    solver.parameters.random_seed = args.seed
    solver.parameters.log_search_progress = True
    status = solver.solve(model)
    record: dict[str, object] = {
        "status": solver.status_name(status),
        "input": args.input,
        "wall_seconds": solver.wall_time,
        "objective_overlap": solver.objective_value,
        "best_bound_overlap": solver.best_objective_bound,
        "branches": solver.num_branches,
        "conflicts": solver.num_conflicts,
    }
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        chosen = {pair for pair, var in x.items() if solver.value(var)}
        record["deleted_edges"] = sorted([list(pair) for pair in incumbent - chosen])
        record["added_edges"] = sorted([list(pair) for pair in chosen - incumbent])
        record["hamming_distance"] = len(chosen ^ incumbent)
        checked = expand_and_check(
            labels, edge_id, {edge_id[pair] for pair in chosen}
        )
        assert checked["edge_count"] == 693
        assert checked["inner_outer_bad_pairs"] == 0
        record["verification"] = {
            key: value for key, value in checked.items() if key != "edges"
        }
        record.update(checked)
    Path(args.output).write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in record.items() if key != "edges"}), flush=True)


if __name__ == "__main__":
    main()
