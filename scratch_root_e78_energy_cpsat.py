"""Optimize all remaining pair residuals inside a fixed E0=78 local orbit.

Unlike the unrestricted 84-vertex energy model, this model fixes every edge
between equal or overlapping support fibres to one audited K2,3 local graph.
Only the 1,680 edges between disjoint support fibres remain as variables.
All BP and all same-fibre equations are hard; cross-fibre residual squares are
the objective.
"""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path
import time

from ortools.sat.python import cp_model

from scratch_fibre_layer_incremental import support_data
from scratch_general_v2_cpsat_energy import M, O, canon, metrics, read_seed


class Saver(cp_model.CpSolverSolutionCallback):
    def __init__(self, variables, fixed_one, scaffold, output, metadata):
        super().__init__()
        self.variables = variables
        self.fixed_one = fixed_one
        self.scaffold = scaffold
        self.output = Path(output)
        self.metadata = metadata
        self.started = time.time()
        self.best = None
        self.solutions = 0

    def on_solution_callback(self):
        self.solutions += 1
        objective = int(round(self.objective_value))
        if self.best is not None and objective >= self.best:
            return
        chosen_local = set(self.fixed_one)
        chosen_local.update(
            pair for pair, var in self.variables.items() if self.value(var)
        )
        chosen = {(O + u, O + v) for u, v in chosen_local}
        info, adj = metrics(self.scaffold, chosen)
        assert info["energy"] == objective
        assert info["io_energy"] == 0 and info["edge_count"] == 693
        assert all(len(row) == 14 for row in adj)
        self.best = objective
        info.update(self.metadata)
        info.update({
            "method": "fixed E0=78 K2,3 orbit, exact BP/fibre layer, CP-SAT full cross-pair energy",
            "cp_sat_objective": objective,
            "cp_sat_best_bound_at_save": self.best_objective_bound,
            "cp_sat_solution_index": self.solutions,
            "elapsed_seconds": time.time() - self.started,
            "valid": objective == 0,
        })
        edges = info.pop("edges")
        info["edges"] = edges
        self.output.write_text(json.dumps(info, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({
            "solution": self.solutions,
            "objective": objective,
            "bound": self.best_objective_bound,
            "bad_pairs": info["bad_pairs"],
            "elapsed": info["elapsed_seconds"],
        }), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--orbit", type=int, default=3)
    parser.add_argument("--rep", type=int, default=6)
    parser.add_argument("--seconds", type=float, default=600.0)
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--seed", type=int, default=7866)
    parser.add_argument("--max-deleted", type=int)
    args = parser.parse_args()

    scaffold, seed_mutable, labels = read_seed(args.input)
    supports_of, fibres = support_data(labels)
    audit = json.loads(Path("scratch_root_e78_p4_local.json").read_text(encoding="utf-8"))
    row = next(r for r in audit["rows"] if r["orbit_index"] == args.orbit)
    representatives = row["canonical_local_graph_representatives"]
    local_graph = representatives[args.rep]
    exceptional = {tuple(support) for support in row["supports"]}
    ordinary = set(fibres) - exceptional
    label_to_vertex = {
        tuple(symbol - 1 for symbol in label): u
        for u, label in enumerate(labels)
    }
    audited_local_edges = {
        canon(label_to_vertex[tuple(left)], label_to_vertex[tuple(right)])
        for left, right in local_graph
    }

    model = cp_model.CpModel()
    variables = {}
    fixed = {}
    for u, v in itertools.combinations(range(M), 2):
        su, sv = supports_of[u], supports_of[v]
        if not set(su) & set(sv):
            variables[(u, v)] = model.NewBoolVar(f"e_{u}_{v}")
        elif su == sv and su in ordinary:
            fixed[(u, v)] = int(len(set(labels[u]) & set(labels[v])) == 1)
        else:
            fixed[(u, v)] = int((u, v) in audited_local_edges)
    assert len(variables) == 1680 and len(fixed) == 1806
    fixed_one = {pair for pair, value in fixed.items() if value}
    assert len(fixed_one) == 90  # E0=78 plus twelve exceptional-overlap edges.

    def edge(u, v):
        pair = canon(u, v)
        return variables[pair] if pair in variables else fixed[pair]

    # BP equations; these imply 504 outer edges and outer degree twelve.
    for u, label in enumerate(labels):
        groups = {(symbol - 1) // 2 for symbol in label}
        for symbol in range(1, 15):
            model.Add(
                sum(edge(u, v) for v, other in enumerate(labels)
                    if u != v and symbol in other)
                == (1 if (symbol - 1) // 2 in groups else 2)
            )

    # Exact linear form of every ordinary-C4 fibre equation.
    for support in ordinary:
        fibre = fibres[support]
        fibre_set = set(fibre)
        for w in range(M):
            if w not in fibre_set:
                model.Add(sum(edge(w, u) for u in fibre) <= 1)

    seed_local = {(u - O, v - O) for u, v in seed_mutable}
    seed_variable = seed_local & set(variables)
    assert seed_local & set(fixed) == fixed_one
    if args.max_deleted is not None:
        model.Add(
            sum(variables[pair] for pair in seed_variable)
            >= len(seed_variable) - args.max_deleted
        )
    for pair, var in variables.items():
        model.AddHint(var, int(pair in seed_variable))

    penalties = []
    products = 0
    hard_p4_pairs = 0
    for u, v in itertools.combinations(range(M), 2):
        # Ordinary C4 pairs are already exact by the fixed square plus the
        # outside-at-most-one family, avoiding unnecessary AND variables.
        if supports_of[u] == supports_of[v] and supports_of[u] in ordinary:
            continue
        constant = len(set(labels[u]) & set(labels[v])) - 2
        direct = edge(u, v)
        if isinstance(direct, int):
            constant += direct
            terms = []
        else:
            terms = [direct]
        for w in range(M):
            if w in (u, v):
                continue
            left, right = edge(u, w), edge(v, w)
            if isinstance(left, int) and isinstance(right, int):
                constant += left * right
            elif isinstance(left, int):
                if left:
                    terms.append(right)
            elif isinstance(right, int):
                if right:
                    terms.append(left)
            else:
                z = model.NewBoolVar(f"z_{u}_{v}_{w}")
                model.AddMultiplicationEquality(z, (left, right))
                terms.append(z)
                products += 1
        residual = model.NewIntVar(-2, 12, f"r_{u}_{v}")
        model.Add(residual == sum(terms) + constant)
        if supports_of[u] == supports_of[v]:
            model.Add(residual == 0)
            hard_p4_pairs += 1
        else:
            penalty = model.NewIntVar(0, 144, f"p_{u}_{v}")
            model.AddMultiplicationEquality(penalty, (residual, residual))
            penalties.append(penalty)
    assert hard_p4_pairs == 36
    model.Minimize(sum(penalties))

    metadata = {
        "orbit": args.orbit,
        "local_representative": args.rep,
        "exceptional_supports": [list(s) for s in sorted(exceptional)],
        "ordinary_c4_fibres": len(ordinary),
        "exceptional_p4_fibres": len(exceptional),
        "variable_edges": len(variables),
        "and_variables": products,
        "objective_pairs": len(penalties),
        "max_deleted_seed_edges": args.max_deleted,
        "source_seed": args.input,
    }
    print(json.dumps(metadata | {
        "seed_energy": metrics(scaffold, seed_mutable)[0]["energy"],
        "time_limit": args.seconds,
        "workers": args.workers,
    }), flush=True)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = args.seconds
    solver.parameters.num_search_workers = args.workers
    solver.parameters.random_seed = args.seed
    solver.parameters.cp_model_presolve = True
    solver.parameters.use_lns = True
    solver.parameters.log_search_progress = True
    saver = Saver(variables, fixed_one, scaffold, args.output, metadata)
    status = solver.Solve(model, saver)
    print(json.dumps({
        "status": solver.StatusName(status),
        "objective": solver.ObjectiveValue(),
        "bound": solver.BestObjectiveBound(),
        "solutions": saver.solutions,
        "wall_seconds": solver.WallTime(),
        "branches": solver.NumBranches(),
        "conflicts": solver.NumConflicts(),
        "output": args.output if saver.best is not None else None,
    }), flush=True)


if __name__ == "__main__":
    main()
