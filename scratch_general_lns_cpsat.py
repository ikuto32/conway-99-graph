"""Exact unrestricted objective CP-SAT LNS for the rooted 84-vertex graph.

Unlike the BP-hard experiment, this keeps only the necessary 12-regularity
constraints and minimizes every inner--outer and outer--outer SRG residual.
The incumbent is a fully specified degree-regular graph and is independently
recomputed in every solution callback.
"""

from __future__ import annotations

import itertools
import json
import sys
import time
from pathlib import Path

from ortools.sat.python import cp_model

N, O, M = 99, 15, 84


def canon(u: int, v: int) -> tuple[int, int]:
    return (u, v) if u < v else (v, u)


def labels() -> list[tuple[int, int]]:
    out = []
    for i in range(7):
        for j in range(i + 1, 7):
            for a in range(2):
                for b in range(2):
                    out.append((1 + 2 * i + a, 1 + 2 * j + b))
    assert len(out) == M
    return out


LABEL = labels()


def scaffold() -> set[tuple[int, int]]:
    result: set[tuple[int, int]] = set()
    for c in range(1, 15):
        result.add((0, c))
    for g in range(7):
        result.add((1 + 2 * g, 2 + 2 * g))
    for x, (a, b) in enumerate(LABEL):
        result.add(canon(O + x, a))
        result.add(canon(O + x, b))
    assert len(result) == 189
    return result


SCAFFOLD = scaffold()


def read_seed(path: str) -> set[tuple[int, int]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    edges = {canon(u - 1, v - 1) for u, v in data["edges"]}
    assert len(edges) == 693 and SCAFFOLD <= edges
    mutable = {(u - O, v - O) for u, v in edges if u >= O}
    assert len(mutable) == 504
    return mutable


def metrics(chosen: set[tuple[int, int]]) -> dict[str, object]:
    edges = SCAFFOLD | {(O + u, O + v) for u, v in chosen}
    adj = [set() for _ in range(N)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    assert len(edges) == 693 and all(len(row) == 14 for row in adj)
    energy = io = oo = bad = 0
    max_abs = 0
    hist = {i: 0 for i in range(-14, 15)}
    for u in range(N):
        for v in range(u + 1, N):
            r = len(adj[u] & adj[v]) + (v in adj[u]) - 2
            energy += r * r
            io += (u < O <= v) * r * r
            oo += (u >= O) * r * r
            bad += r != 0
            max_abs = max(max_abs, abs(r))
            hist[r] += 1
    return {
        "energy": energy,
        "recomputed_energy": energy,
        "io_energy": io,
        "oo_energy": oo,
        "bad_pairs": bad,
        "max_abs_residual": max_abs,
        "residual_histogram": {str(k): v for k, v in hist.items() if v},
        "edge_count": len(edges),
        "edges": [[u + 1, v + 1] for u, v in sorted(edges)],
    }


class Saver(cp_model.CpSolverSolutionCallback):
    def __init__(self, variables, output: str, started: float):
        super().__init__()
        self.variables = variables
        self.output = Path(output)
        self.started = started
        self.count = 0
        self.best = None

    def on_solution_callback(self):
        self.count += 1
        claimed = int(round(self.objective_value))
        if self.best is not None and claimed >= self.best:
            return
        chosen = {pair for pair, var in self.variables.items() if self.value(var)}
        info = metrics(chosen)
        assert info["energy"] == claimed
        self.best = claimed
        info.update({
            "cp_sat_objective": claimed,
            "cp_sat_bound": self.best_objective_bound,
            "solution_index": self.count,
            "elapsed_seconds": time.time() - self.started,
        })
        self.output.write_text(json.dumps(info, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"solution": self.count, "objective": claimed,
                          "bound": self.best_objective_bound,
                          "elapsed": info["elapsed_seconds"]}), flush=True)


def main() -> None:
    seed_path = sys.argv[1] if len(sys.argv) > 1 else "scratch_general_lns_best.json"
    output = sys.argv[2] if len(sys.argv) > 2 else "scratch_general_lns_cpsat_best.json"
    seconds = float(sys.argv[3]) if len(sys.argv) > 3 else 180.0
    workers = int(sys.argv[4]) if len(sys.argv) > 4 else 16
    seed = read_seed(seed_path)
    seed_info = metrics(seed)

    model = cp_model.CpModel()
    edge_vars = {
        pair: model.new_bool_var(f"e_{pair[0]}_{pair[1]}")
        for pair in itertools.combinations(range(M), 2)
    }

    def edge(u: int, v: int):
        return edge_vars[canon(u, v)]

    for u in range(M):
        model.add(sum(edge(u, v) for v in range(M) if v != u) == 12)

    penalties = []
    # Inner--outer residuals.  The desired number of outer neighbours bearing
    # coordinate c is 1 for either support group of u and 2 otherwise.
    for u, label in enumerate(LABEL):
        support_groups = {(c - 1) // 2 for c in label}
        for c in range(1, 15):
            target = 1 if (c - 1) // 2 in support_groups else 2
            count = sum(edge(u, v) for v, other in enumerate(LABEL)
                        if v != u and c in other)
            residual = model.new_int_var(-2, 10, f"ri_{u}_{c}")
            model.add(residual == count - target)
            penalty = model.new_int_var(0, 100, f"pi_{u}_{c}")
            model.add_multiplication_equality(penalty, [residual, residual])
            penalties.append(penalty)

    common = {pair: [] for pair in edge_vars}
    products = 0
    for a, b, c in itertools.combinations(range(M), 3):
        eab, eac, ebc = edge(a, b), edge(a, c), edge(b, c)
        for pair, x, y, name in (
            ((a, b), eac, ebc, f"z_{a}_{b}_{c}"),
            ((a, c), eab, ebc, f"z_{a}_{c}_{b}"),
            ((b, c), eab, eac, f"z_{b}_{c}_{a}"),
        ):
            z = model.new_bool_var(name)
            model.add_multiplication_equality(z, [x, y])
            common[pair].append(z)
            products += 1

    for (u, v), x in edge_vars.items():
        fixed_common = len(set(LABEL[u]) & set(LABEL[v]))
        residual = model.new_int_var(-2, 12, f"ro_{u}_{v}")
        model.add(residual == sum(common[(u, v)]) + x + fixed_common - 2)
        penalty = model.new_int_var(0, 144, f"po_{u}_{v}")
        model.add_multiplication_equality(penalty, [residual, residual])
        penalties.append(penalty)

    objective = sum(penalties)
    model.minimize(objective)
    # Demand an actual improvement; the incumbent hint proves the cutoff is
    # only one unit below a feasible objective.
    model.add(objective < int(seed_info["energy"]))
    for pair, var in edge_vars.items():
        model.add_hint(var, int(pair in seed))

    print(json.dumps({"seed": seed_path, "seed_energy": seed_info["energy"],
                      "edge_variables": len(edge_vars), "product_variables": products,
                      "penalties": len(penalties), "seconds": seconds,
                      "workers": workers}), flush=True)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = int(time.time_ns() & 0x7fffffff)
    solver.parameters.cp_model_presolve = True
    solver.parameters.use_lns = True
    solver.parameters.log_search_progress = False
    started = time.time()
    saver = Saver(edge_vars, output, started)
    status = solver.solve(model, saver)
    print(json.dumps({"status": solver.status_name(status),
                      "objective": solver.objective_value,
                      "bound": solver.best_objective_bound,
                      "solutions": saver.count, "wall_seconds": solver.wall_time,
                      "branches": solver.num_branches, "conflicts": solver.num_conflicts,
                      "output": output if saver.count else None}), flush=True)


if __name__ == "__main__":
    main()
