"""Native-cardinality solver for a rooted, coordinate-perfect outer seed."""

from __future__ import annotations

import itertools
import json

from pysat.solvers import Solver

from scratch_bp_seed import expand_and_check


def main() -> None:
    labels = [
        pair
        for pair in itertools.combinations(range(14), 2)
        if pair[0] // 2 != pair[1] // 2
    ]
    variables = {
        pair: number
        for number, pair in enumerate(itertools.combinations(range(84), 2), 1)
    }
    constraints: list[tuple[list[int], int]] = []
    for u, label in enumerate(labels):
        label_set = set(label)
        for symbol in range(14):
            lits = []
            for v, other in enumerate(labels):
                if u != v and symbol in other:
                    key = (u, v) if u < v else (v, u)
                    lits.append(variables[key])
            target = 1 if symbol in label_set or (symbol ^ 1) in label_set else 2
            constraints.append((lits, target))
    print(json.dumps({"variables": len(variables), "equalities": len(constraints)}), flush=True)
    with Solver(name="minicard") as solver:
        for lits, target in constraints:
            solver.add_atmost(lits, target)
            solver.add_atmost([-lit for lit in lits], len(lits) - target)
        sat = solver.solve()
        print(json.dumps({"result": "SAT" if sat else "UNSAT", "stats": solver.accum_stats()}), flush=True)
        if not sat:
            return
        positive = {lit for lit in solver.get_model() if 0 < lit <= len(variables)}
    result = expand_and_check(labels, variables, positive)
    with open("scratch_bp_seed.json", "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    print(json.dumps({key: result[key] for key in result if key != "edges"}), flush=True)


if __name__ == "__main__":
    main()
