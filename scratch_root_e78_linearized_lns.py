"""Sequential exact-layer LNS inside one fixed E0=78 K2,3 local orbit."""

from __future__ import annotations

import argparse
import itertools
import json
import math
import random
from pathlib import Path
import time

from ortools.sat.python import cp_model

from scratch_bp_linearized_lns import adjacency, toggle_delta
from scratch_fibre_layer_incremental import layer_diagnostics, support_data
from scratch_general_v2_cpsat_energy import M, O, canon, metrics, read_seed


def structure(labels, fibres, orbit, rep):
    audit = json.loads(Path("scratch_root_e78_p4_local.json").read_text(encoding="utf-8"))
    row = next(r for r in audit["rows"] if r["orbit_index"] == orbit)
    exceptional = {tuple(s) for s in row["supports"]}
    ordinary = set(fibres) - exceptional
    label_to_vertex = {
        tuple(symbol - 1 for symbol in label): u
        for u, label in enumerate(labels)
    }
    audited = {
        canon(label_to_vertex[tuple(left)], label_to_vertex[tuple(right)])
        for left, right in row["canonical_local_graph_representatives"][rep]
    }
    fixed = {}
    variable_pairs = []
    supports_of, _ = support_data(labels)
    for u, v in itertools.combinations(range(M), 2):
        su, sv = supports_of[u], supports_of[v]
        if not set(su) & set(sv):
            variable_pairs.append((u, v))
        elif su == sv and su in ordinary:
            fixed[u, v] = int(len(set(labels[u]) & set(labels[v])) == 1)
        else:
            fixed[u, v] = int((u, v) in audited)
    return supports_of, exceptional, ordinary, tuple(variable_pairs), fixed


def solve_round(scaffold, current, labels, fibres, supports_of, exceptional,
                ordinary, variable_pairs, fixed, min_deleted, max_deleted,
                seconds, workers, rng, noise, gradient_scale, forbidden):
    adj = adjacency(scaffold, current)
    model = cp_model.CpModel()
    x = {pair: model.NewBoolVar(f"e_{pair[0]}_{pair[1]}") for pair in variable_pairs}

    def edge(u, v):
        pair = canon(u, v)
        return x[pair] if pair in x else fixed[pair]

    for u, label in enumerate(labels):
        groups = {(symbol - 1) // 2 for symbol in label}
        for symbol in range(1, 15):
            model.Add(
                sum(edge(u, v) for v, other in enumerate(labels)
                    if u != v and symbol in other)
                == (1 if (symbol - 1) // 2 in groups else 2)
            )
    for support in ordinary:
        fibre = fibres[support]
        fibre_set = set(fibre)
        for w in range(M):
            if w not in fibre_set:
                model.Add(sum(edge(w, u) for u in fibre) <= 1)

    # Exact P4 same-fibre equations.  Fixed local common neighbours and
    # variable disjoint-fibre common neighbours are both included directly.
    for support in exceptional:
        fibre = fibres[support]
        for u, v in itertools.combinations(fibre, 2):
            terms = [edge(u, v)]
            constant = len(set(labels[u]) & set(labels[v]))
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
            model.Add(sum(terms) + constant == 2)

    current_local = {(u - O, v - O) for u, v in current}
    current_variable = current_local & set(variable_pairs)
    overlap = sum(x[pair] for pair in current_variable)
    model.Add(overlap >= len(current_variable) - max_deleted)
    model.Add(overlap <= len(current_variable) - min_deleted)
    for old in forbidden:
        old_local = {(u - O, v - O) for u, v in old} & set(variable_pairs)
        model.Add(sum(x[pair] for pair in old_local) <= len(old_local) - 1)

    coefficients = {}
    for a, b in variable_pairs:
        selected = (a, b) in current_variable
        delta = toggle_delta(adj, O + a, O + b, adding=not selected)
        coefficients[a, b] = -delta if selected else delta
    model.Minimize(sum(
        (gradient_scale * coefficients[pair] + rng.randint(-noise, noise)) * var
        for pair, var in x.items()
    ))
    for pair, var in x.items():
        model.AddHint(var, int(pair in current_variable))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = rng.randrange(1, 2**31)
    status = solver.Solve(model)
    record = {
        "status": solver.StatusName(status),
        "wall": solver.WallTime(),
        "branches": solver.NumBranches(),
        "conflicts": solver.NumConflicts(),
    }
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None, record
    chosen_local = {pair for pair, value in fixed.items() if value}
    chosen_local.update(pair for pair, var in x.items() if solver.Value(var))
    chosen = {(O + u, O + v) for u, v in chosen_local}
    info, adj2 = metrics(scaffold, chosen)
    layer_info, rows = layer_diagnostics(scaffold, chosen, labels, fibres)
    assert info == layer_info and info["io_energy"] == 0
    assert info["edge_count"] == 693 and all(len(a) == 14 for a in adj2)
    assert sum(row["bad"] for row in rows.values()) == 0
    record.update({
        "surrogate": solver.ObjectiveValue(),
        "bound": solver.BestObjectiveBound(),
        "deleted": len(current - chosen),
        "energy": info["energy"],
        "bad_pairs": info["bad_pairs"],
    })
    return chosen, record


def save(path, scaffold, mutable, history, best_round, orbit, rep):
    info, adj = metrics(scaffold, mutable)
    assert info["io_energy"] == 0 and all(len(row) == 14 for row in adj)
    info.update({
        "method": "fixed E0=78 exact-layer sequential linearized LNS",
        "orbit": orbit,
        "local_representative": rep,
        "best_round": best_round,
        "round_history": history,
        "valid": info["energy"] == 0,
    })
    edges = info.pop("edges")
    info["edges"] = edges
    Path(path).write_text(json.dumps(info, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--orbit", type=int, default=3)
    parser.add_argument("--rep", type=int, default=6)
    parser.add_argument("--rounds", type=int, default=100)
    parser.add_argument("--seconds-per-round", type=float, default=2.0)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--max-deleted", type=int, default=16)
    parser.add_argument("--min-deleted", type=int, default=1)
    parser.add_argument("--noise", type=int, default=3)
    parser.add_argument("--gradient-scale", type=int, default=4)
    parser.add_argument("--temperature-high", type=float, default=12.0)
    parser.add_argument("--seed", type=int, default=1)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    scaffold, current, labels = read_seed(args.input)
    supports_of, fibres = support_data(labels)
    supports_of, exceptional, ordinary, variable_pairs, fixed = structure(
        labels, fibres, args.orbit, args.rep
    )
    best = set(current)
    best_energy = metrics(scaffold, best)[0]["energy"]
    best_round = -1
    history = []
    forbidden = []
    started = time.monotonic()
    for round_index in range(args.rounds):
        candidate, record = solve_round(
            scaffold, current, labels, fibres, supports_of, exceptional,
            ordinary, variable_pairs, fixed, args.min_deleted,
            args.max_deleted, args.seconds_per_round, args.workers, rng,
            args.noise, args.gradient_scale, forbidden,
        )
        record["round"] = round_index
        if candidate is None:
            record["accepted"] = False
            history.append(record)
            print(json.dumps(record), flush=True)
            if forbidden:
                forbidden.pop(0)
            continue
        current_energy = metrics(scaffold, current)[0]["energy"]
        candidate_energy = record["energy"]
        phase = (round_index % 10) / 9
        temperature = args.temperature_high * (0.5 / args.temperature_high) ** phase
        accepted = (
            round_index % 10 == 0
            or candidate_energy <= current_energy
            or rng.random() < math.exp(-(candidate_energy - current_energy) / temperature)
        )
        if accepted:
            previous = set(current)
            current = candidate
            forbidden.append(previous)
        else:
            forbidden.append(set(candidate))
        if len(forbidden) > 3:
            del forbidden[:-3]
        if candidate_energy < best_energy:
            best = set(candidate)
            best_energy = candidate_energy
            best_round = round_index
            save(args.output, scaffold, best, history + [record], best_round,
                 args.orbit, args.rep)
        record.update({
            "accepted": accepted,
            "incumbent_energy": metrics(scaffold, current)[0]["energy"],
            "best_energy": best_energy,
            "temperature": temperature,
            "elapsed": time.monotonic() - started,
        })
        history.append(record)
        print(json.dumps(record), flush=True)
    save(args.output, scaffold, best, history, best_round, args.orbit, args.rep)
    print(json.dumps({"final_best": best_energy, "output": args.output}), flush=True)


if __name__ == "__main__":
    main()
