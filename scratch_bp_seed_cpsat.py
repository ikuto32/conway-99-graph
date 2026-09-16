"""CP-SAT construction of a rooted outer graph satisfying BP = P A0."""

from __future__ import annotations

import itertools
import json

from ortools.sat.python import cp_model

from scratch_bp_seed import expand_and_check


def main() -> None:
    labels = [
        pair
        for pair in itertools.combinations(range(14), 2)
        if pair[0] // 2 != pair[1] // 2
    ]
    model = cp_model.CpModel()
    variables = {
        pair: model.new_bool_var(f"e_{pair[0]}_{pair[1]}")
        for pair in itertools.combinations(range(84), 2)
    }
    for u, label in enumerate(labels):
        label_set = set(label)
        for symbol in range(14):
            lits = []
            for v, other in enumerate(labels):
                if u != v and symbol in other:
                    key = (u, v) if u < v else (v, u)
                    lits.append(variables[key])
            target = 1 if symbol in label_set or (symbol ^ 1) in label_set else 2
            model.add(sum(lits) == target)
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 32
    solver.parameters.max_time_in_seconds = 120.0
    status = solver.solve(model)
    status_name = solver.status_name(status)
    print(
        json.dumps(
            {
                "status": status_name,
                "wall_seconds": solver.wall_time,
                "branches": solver.num_branches,
                "conflicts": solver.num_conflicts,
            }
        ),
        flush=True,
    )
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return
    edge_ids = {pair: i for i, pair in enumerate(variables, 1)}
    positive = {edge_ids[pair] for pair, var in variables.items() if solver.value(var)}
    result = expand_and_check(labels, edge_ids, positive)
    with open("scratch_bp_seed.json", "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    print(json.dumps({key: result[key] for key in result if key != "edges"}), flush=True)


if __name__ == "__main__":
    main()
