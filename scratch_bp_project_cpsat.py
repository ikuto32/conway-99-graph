"""Project a low-energy regular candidate onto the exact rooted BP polytope.

The input is a 99-vertex edge JSON produced by the unrestricted local search.
All 3,486 outer-edge variables are constrained by the 1,176 exact rooted
incidence equations.  The objective maximizes overlap with the input outer
edge set (equivalently minimizes Hamming distance, since both have 504 outer
edges).  The projected graph is expanded and independently scored on all
4,851 pairs.  It is only a seed unless that score is zero.
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
    parser.add_argument("--hint")
    parser.add_argument("--lns-only", action="store_true")
    args = parser.parse_args()

    labels = [
        pair
        for pair in itertools.combinations(range(14), 2)
        if pair[0] // 2 != pair[1] // 2
    ]
    pairs = list(itertools.combinations(range(84), 2))
    edge_id = {pair: i + 1 for i, pair in enumerate(pairs)}
    source = json.loads(Path(args.input).read_text(encoding="utf-8"))
    source_outer = set()
    for a, b in source["edges"]:
        if a >= 16 and b >= 16:
            source_outer.add((a - 16, b - 16))
    assert len(source_outer) == 504

    model = cp_model.CpModel()
    x = {pair: model.new_bool_var("") for pair in pairs}

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

    # BP fixes the outer edge count at 504, so maximizing the number of source
    # edges retained is exactly the same as minimizing symmetric difference.
    overlap_terms = []
    for pair, var in x.items():
        selected = pair in source_outer
        if selected:
            overlap_terms.append(var)
    model.add(sum(x.values()) == 504)
    model.maximize(sum(overlap_terms))

    hint_outer = source_outer
    if args.hint:
        hint_payload = json.loads(Path(args.hint).read_text(encoding="utf-8"))
        hint_outer = {
            (a - 16, b - 16)
            for a, b in hint_payload["edges"]
            if a >= 16 and b >= 16
        }
        assert len(hint_outer) == 504
    for pair, var in x.items():
        model.add_hint(var, int(pair in hint_outer))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = args.seconds
    solver.parameters.num_search_workers = args.workers
    solver.parameters.random_seed = args.seed
    solver.parameters.use_lns_only = args.lns_only
    status = solver.solve(model)
    record: dict[str, object] = {
        "status": solver.status_name(status),
        "source": args.input,
        "hint": args.hint,
        "wall_seconds": solver.wall_time,
        "objective": solver.objective_value,
        "best_bound": solver.best_objective_bound,
        "branches": solver.num_branches,
        "conflicts": solver.num_conflicts,
    }
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        Path(args.output).write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(record), flush=True)
        return

    positive = {edge_id[pair] for pair, var in x.items() if solver.value(var)}
    projected_outer = {pair for pair, var in x.items() if solver.value(var)}
    overlap = len(projected_outer.intersection(source_outer))
    record["outer_overlap"] = overlap
    record["outer_hamming_distance"] = len(projected_outer.symmetric_difference(source_outer))
    checked = expand_and_check(labels, edge_id, positive)
    assert checked["edge_count"] == 693
    assert checked["inner_outer_bad_pairs"] == 0
    record["verification"] = {key: value for key, value in checked.items() if key != "edges"}
    payload = {**record, **checked}
    Path(args.output).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(record), flush=True)


if __name__ == "__main__":
    main()
