"""Sequential linearized LNS constrained to the exact rooted BP polytope.

The full squared common-neighbour objective is quadratic.  At each round this
script computes the exact one-edge toggle delta at the incumbent, uses those
deltas as a linear surrogate, and lets CP-SAT choose a BP-feasible move with a
bounded number of deleted/added edges.  The resulting graph is always scored
against the true 99-vertex objective before it can become the incumbent/best.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import random
import time
from pathlib import Path

from ortools.sat.python import cp_model

from scratch_general_v2_cpsat_energy import N, O, M, canon, metrics, read_seed


def adjacency(scaffold, mutable):
    adj = [set() for _ in range(N)]
    for u, v in scaffold | mutable:
        adj[u].add(v)
        adj[v].add(u)
    return adj


def toggle_delta(adj, u, v, adding):
    sign = 1 if adding else -1
    changes: dict[tuple[int, int], int] = {canon(u, v): sign}
    for w in adj[v]:
        if w != u:
            key = canon(u, w)
            changes[key] = changes.get(key, 0) + sign
    for w in adj[u]:
        if w != v:
            key = canon(v, w)
            changes[key] = changes.get(key, 0) + sign
    delta = 0
    for (a, b), dr in changes.items():
        common = len(adj[a] & adj[b])
        residual = common + int(b in adj[a]) - 2
        delta += (residual + dr) ** 2 - residual**2
    return delta


def solve_surrogate(scaffold, current, labels, min_deleted, max_deleted, seconds, workers,
                    rng, noise, gradient_scale, forbidden):
    adj = adjacency(scaffold, current)
    model = cp_model.CpModel()
    pairs = list(itertools.combinations(range(M), 2))
    x = {pair: model.NewBoolVar(f"e_{pair[0]}_{pair[1]}") for pair in pairs}

    def edge(a, b):
        return x[canon(a, b)]

    for a, label in enumerate(labels):
        groups = {(symbol - 1) // 2 for symbol in label}
        for symbol in range(1, 15):
            model.Add(
                sum(edge(a, b) for b, other in enumerate(labels)
                    if a != b and symbol in other)
                == (1 if (symbol - 1) // 2 in groups else 2)
            )

    current_local = {(u - O, v - O) for u, v in current}
    overlap = sum(x[pair] for pair in current_local)
    model.Add(overlap >= 504 - max_deleted)
    model.Add(overlap <= 504 - min_deleted)

    # Avoid returning the same surrogate optimum on every randomized round.
    # Each forbidden BP point also has 504 edges, so this single inequality is
    # an exact no-good cut for that point.
    for old in forbidden:
        old_local = {(u - O, v - O) for u, v in old}
        model.Add(sum(x[pair] for pair in old_local) <= 503)

    coefficients = {}
    for a, b in pairs:
        u, v = O + a, O + b
        selected = (a, b) in current_local
        delta = toggle_delta(adj, u, v, adding=not selected)
        coefficient = -delta if selected else delta
        coefficients[a, b] = coefficient
    model.Minimize(
        sum((gradient_scale * coefficients[pair] + rng.randint(-noise, noise)) * var
            for pair, var in x.items())
    )
    for pair, var in x.items():
        model.AddHint(var, int(pair in current_local))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = rng.randrange(1, 2**31)
    solver.parameters.log_search_progress = False
    status = solver.Solve(model)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None, {
            "status": solver.StatusName(status),
            "wall": solver.WallTime(),
        }
    chosen = {
        (O + a, O + b) for (a, b), var in x.items() if solver.Value(var)
    }
    deleted = len(current - chosen)
    info, adj2 = metrics(scaffold, chosen)
    assert info["io_energy"] == 0 and info["edge_count"] == 693
    assert all(len(row) == 14 for row in adj2)
    return chosen, {
        "status": solver.StatusName(status),
        "wall": solver.WallTime(),
        "surrogate": solver.ObjectiveValue(),
        "bound": solver.BestObjectiveBound(),
        "deleted": deleted,
        "energy": info["energy"],
        "bad_pairs": info["bad_pairs"],
    }


def save(path, scaffold, mutable, history, best_round):
    info, adj = metrics(scaffold, mutable)
    assert info["io_energy"] == 0 and all(len(row) == 14 for row in adj)
    info["method"] = "exact-BP sequential linearized LNS"
    info["best_round"] = best_round
    info["round_history"] = history
    edges = info.pop("edges")
    info["edges"] = edges
    Path(path).write_text(json.dumps(info, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--rounds", type=int, default=40)
    parser.add_argument("--seconds-per-round", type=float, default=3.0)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--max-deleted", type=int, default=16)
    parser.add_argument("--min-deleted", type=int, default=1)
    parser.add_argument("--noise", type=int, default=3)
    parser.add_argument("--gradient-scale", type=int, default=4)
    parser.add_argument("--temperature-high", type=float, default=16.0)
    parser.add_argument(
        "--forced-jump-period", type=int, default=10,
        help="accept every Nth candidate unconditionally; 0 disables forced jumps",
    )
    parser.add_argument("--seed", type=int, default=1)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    scaffold, current, labels = read_seed(args.input)
    current_info, _ = metrics(scaffold, current)
    assert current_info["io_energy"] == 0
    best = set(current)
    best_energy = current_info["energy"]
    best_round = -1
    history = []
    forbidden = []
    started = time.monotonic()
    for round_index in range(args.rounds):
        candidate, record = solve_surrogate(
            scaffold, current, labels, args.min_deleted, args.max_deleted,
            args.seconds_per_round, args.workers, rng, args.noise,
            args.gradient_scale, forbidden,
        )
        record["round"] = round_index
        if candidate is None:
            record["accepted"] = False
            history.append(record)
            print(json.dumps(record), flush=True)
            # A tight no-good can make a two-second round time out before its
            # first solution.  Drop those diversification cuts and retry from
            # the same exact incumbent on the next round.
            if forbidden:
                forbidden.pop(0)
            continue
        current_energy = metrics(scaffold, current)[0]["energy"]
        candidate_energy = record["energy"]
        phase = (round_index % 10) / 9
        temperature = args.temperature_high * (0.5 / args.temperature_high) ** phase
        accepted = (
            (
                args.forced_jump_period > 0
                and round_index % args.forced_jump_period == 0
            )
            or candidate_energy <= current_energy
            or rng.random() < math.exp(-(candidate_energy - current_energy) / temperature)
        )
        if accepted:
            previous = set(current)
            current = candidate
            # Keep a short tabu queue containing the previous exact BP point,
            # which prevents the surrogate from immediately undoing the move.
            forbidden.append(previous)
        else:
            forbidden.append(set(candidate))
        if len(forbidden) > 3:
            del forbidden[:-3]
        if candidate_energy < best_energy:
            best = set(candidate)
            best_energy = candidate_energy
            best_round = round_index
            save(args.output, scaffold, best, history + [record], best_round)
        record.update({
            "accepted": accepted,
            "incumbent_energy": metrics(scaffold, current)[0]["energy"],
            "best_energy": best_energy,
            "temperature": temperature,
            "elapsed": time.monotonic() - started,
        })
        history.append(record)
        print(json.dumps(record), flush=True)
    save(args.output, scaffold, best, history, best_round)
    print(json.dumps({"final_best": best_energy, "output": args.output}), flush=True)


if __name__ == "__main__":
    main()
