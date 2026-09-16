"""Unrestricted CP-SAT optimization of the rooted 84-vertex outer graph.

All 3486 outer edge variables are present.  The 1176 scaffold-coordinate
equations are hard constraints (hence every outer degree is exactly 12), while
the exact sum of squared residuals for all 3486 outer pairs is minimized.  The
model is deliberately general: no automorphism, fibre, Cayley, or voltage
assumption is made.
"""

from __future__ import annotations

import itertools
import json
import sys
import time

from ortools.sat.python import cp_model

N = 99
O = 15
M = 84


def canon(u: int, v: int) -> tuple[int, int]:
    return (u, v) if u < v else (v, u)


def read_seed(path: str):
    data = json.load(open(path, encoding="utf-8"))
    edges = {canon(u - 1, v - 1) for u, v in data["edges"]}
    if len(edges) != 693:
        raise ValueError(f"seed has {len(edges)} unique edges")
    scaffold = {e for e in edges if e[0] < O}
    mutable = {e for e in edges if e[0] >= O}
    labels = []
    for u in range(O, N):
        label = tuple(v for v in range(1, O) if canon(u, v) in scaffold)
        if len(label) != 2:
            raise ValueError(f"outer vertex {u + 1} has scaffold label {label}")
        labels.append(label)
    if len(scaffold) != 189 or len(mutable) != 504:
        raise ValueError((len(scaffold), len(mutable)))
    return scaffold, mutable, labels


def metrics(scaffold, chosen):
    edges = set(scaffold) | set(chosen)
    adj = [set() for _ in range(N)]
    for u, v in edges:
        adj[u].add(v)
        adj[v].add(u)
    energy = io = oo = bad = 0
    max_abs = 0
    for u in range(N):
        for v in range(u + 1, N):
            r = len(adj[u] & adj[v]) + (v in adj[u]) - 2
            p = r * r
            energy += p
            if u < O <= v:
                io += p
            elif u >= O:
                oo += p
            bad += r != 0
            max_abs = max(max_abs, abs(r))
    return {
        "energy": energy,
        "recomputed_energy": energy,
        "io_energy": io,
        "oo_energy": oo,
        "bad_pairs": bad,
        "max_abs_residual": max_abs,
        "edge_count": len(edges),
        "edges": [[u + 1, v + 1] for u, v in sorted(edges)],
    }, adj


class Saver(cp_model.CpSolverSolutionCallback):
    def __init__(self, edge_vars, scaffold, output, started):
        super().__init__()
        self.edge_vars = edge_vars
        self.scaffold = scaffold
        self.output = output
        self.started = started
        self.count = 0
        self.best = None

    def on_solution_callback(self):
        self.count += 1
        objective = int(round(self.objective_value))
        if self.best is not None and objective >= self.best:
            return
        self.best = objective
        chosen = {
            (O + u, O + v)
            for (u, v), var in self.edge_vars.items()
            if self.value(var)
        }
        info, adj = metrics(self.scaffold, chosen)
        assert info["energy"] == objective
        assert info["io_energy"] == 0
        assert info["edge_count"] == 693
        assert all(len(a) == 14 for a in adj)
        info.update(
            {
                "cp_sat_objective": objective,
                "cp_sat_best_bound": self.best_objective_bound,
                "cp_sat_solution_index": self.count,
                "elapsed_seconds": time.time() - self.started,
            }
        )
        # Keep the large edge array last for streaming/non-JSON warm-start
        # readers as well as ordinary JSON consumers.
        serialized_edges = info.pop("edges")
        info["edges"] = serialized_edges
        with open(self.output, "w", encoding="utf-8") as handle:
            json.dump(info, handle, indent=2)
            handle.write("\n")
        print(
            json.dumps(
                {
                    "solution": self.count,
                    "objective": objective,
                    "bound": self.best_objective_bound,
                    "bad_pairs": info["bad_pairs"],
                    "elapsed": info["elapsed_seconds"],
                }
            ),
            flush=True,
        )


def main():
    seed_path = sys.argv[1] if len(sys.argv) > 1 else "scratch_bp_seed.json"
    output = (
        sys.argv[2]
        if len(sys.argv) > 2
        else "scratch_general_v2_cpsat_energy_best.json"
    )
    seconds = float(sys.argv[3]) if len(sys.argv) > 3 else 180.0
    workers = int(sys.argv[4]) if len(sys.argv) > 4 else 32
    max_deleted = int(sys.argv[5]) if len(sys.argv) > 5 else None
    scaffold, seed_mutable, labels = read_seed(seed_path)
    model = cp_model.CpModel()
    edge_vars = {
        (u, v): model.new_bool_var(f"e_{u}_{v}")
        for u, v in itertools.combinations(range(M), 2)
    }

    def edge(u, v):
        return edge_vars[canon(u, v)]

    # Exactly the inner--outer equations. Summing the 14 equations for one u
    # gives twice its outer degree = 24, so no redundant degree row is needed.
    for u, label in enumerate(labels):
        groups = {(c - 1) // 2 for c in label}
        for symbol in range(1, 15):
            incident = [
                edge(u, v)
                for v, other in enumerate(labels)
                if u != v and symbol in other
            ]
            target = 1 if (symbol - 1) // 2 in groups else 2
            model.add(sum(incident) == target)

    # Optional exact-BP neighbourhood around the supplied seed.  Every BP
    # point has 504 edges, so bounding deleted incumbent edges also bounds the
    # number of added edges and the symmetric-difference distance.
    if max_deleted is not None:
        incumbent_pairs = {
            (u - O, v - O) for u, v in seed_mutable
        }
        model.add(sum(edge_vars[pair] for pair in incumbent_pairs) >= 504 - max_deleted)

    common_terms = {pair: [] for pair in edge_vars}
    product_vars = 0
    for a, b, c in itertools.combinations(range(M), 3):
        eab, eac, ebc = edge(a, b), edge(a, c), edge(b, c)
        # Common neighbour c of (a,b), b of (a,c), and a of (b,c).
        for pair, left, right, name in (
            ((a, b), eac, ebc, f"z_{a}_{b}_via_{c}"),
            ((a, c), eab, ebc, f"z_{a}_{c}_via_{b}"),
            ((b, c), eab, eac, f"z_{b}_{c}_via_{a}"),
        ):
            z = model.new_bool_var(name)
            model.add_multiplication_equality(z, [left, right])
            common_terms[pair].append(z)
            product_vars += 1

    penalties = []
    seed_adj = [set() for _ in range(M)]
    for u, v in seed_mutable:
        seed_adj[u - O].add(v - O)
        seed_adj[v - O].add(u - O)
    for (u, v), x in edge_vars.items():
        fixed_common = len(set(labels[u]) & set(labels[v]))
        residual = model.new_int_var(-2, 12, f"r_{u}_{v}")
        model.add(
            residual
            == sum(common_terms[(u, v)]) + x + fixed_common - 2
        )
        penalty = model.new_int_var(0, 144, f"p_{u}_{v}")
        model.add_multiplication_equality(penalty, [residual, residual])
        penalties.append(penalty)
        model.add_hint(x, int(v in seed_adj[u]))
    model.minimize(sum(penalties))

    print(
        json.dumps(
            {
                "edge_vars": len(edge_vars),
                "and_vars": product_vars,
                "pair_penalties": len(penalties),
                "seed": seed_path,
                "seed_energy": metrics(scaffold, seed_mutable)[0]["energy"],
                "time_limit": seconds,
                "workers": workers,
                "max_deleted_seed_edges": max_deleted,
            }
        ),
        flush=True,
    )
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = workers
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.log_search_progress = True
    solver.parameters.cp_model_presolve = True
    solver.parameters.use_lns = True
    solver.parameters.random_seed = int(time.time_ns() & 0x7FFFFFFF)
    started = time.time()
    saver = Saver(edge_vars, scaffold, output, started)
    status = solver.solve(model, saver)
    print(
        json.dumps(
            {
                "status": solver.status_name(status),
                "objective": solver.objective_value,
                "bound": solver.best_objective_bound,
                "solutions": saver.count,
                "wall_seconds": solver.wall_time,
                "branches": solver.num_branches,
                "conflicts": solver.num_conflicts,
                "output": output if saver.count else None,
            }
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
