"""Greedily impose exact C4 same-fibre equations on a BP outer graph.

For a support fibre F, fixing its four coordinate-square sides and deleting
its diagonals makes all six equations inside F equivalent to the linear rule
that every vertex outside F has at most one neighbour in F.  Thus this script
contains no product variables.  It is a seed generator, not an E0 bound: a
failed greedy stage only means that the attempted extension was not found.
"""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

from ortools.sat.python import cp_model

from scratch_fibre_layer_incremental import layer_diagnostics, support_data
from scratch_general_v2_cpsat_energy import M, O, canon, metrics, read_seed


def solve(scaffold, current, labels, fibres, c4_supports, max_deleted,
          seconds, workers, random_seed):
    model = cp_model.CpModel()
    pairs = list(itertools.combinations(range(M), 2))
    x = {pair: model.NewBoolVar(f"e_{pair[0]}_{pair[1]}") for pair in pairs}

    def edge(u, v):
        return x[canon(u, v)]

    # Exact rooted inner--outer pair equations (BP equations).
    for u, label in enumerate(labels):
        groups = {(symbol - 1) // 2 for symbol in label}
        for symbol in range(1, 15):
            model.Add(
                sum(edge(u, v) for v, other in enumerate(labels)
                    if u != v and symbol in other)
                == (1 if (symbol - 1) // 2 in groups else 2)
            )

    for support in c4_supports:
        fibre = fibres[support]
        fibre_set = set(fibre)
        # The only possible exact four-edge fibre is its coordinate C4.
        for u, v in itertools.combinations(fibre, 2):
            square_side = len(set(labels[u]) & set(labels[v])) == 1
            model.Add(edge(u, v) == int(square_side))
        # This single family is equivalent to zero external common neighbours
        # for every pair in the C4 (side or diagonal).
        for w in range(M):
            if w not in fibre_set:
                model.Add(sum(edge(w, u) for u in fibre) <= 1)

    current_local = {(u - O, v - O) for u, v in current}
    if max_deleted < 504:
        model.Add(
            sum(x[pair] for pair in current_local) >= 504 - max_deleted
        )
    for pair, var in x.items():
        model.AddHint(var, int(pair in current_local))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = random_seed
    solver.parameters.stop_after_first_solution = True
    solver.parameters.log_search_progress = False
    status = solver.Solve(model)
    record = {
        "status": solver.StatusName(status),
        "wall_seconds": solver.WallTime(),
        "branches": solver.NumBranches(),
        "conflicts": solver.NumConflicts(),
        "c4_count": len(c4_supports),
        "max_deleted": max_deleted,
    }
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None, record
    chosen = {
        (O + u, O + v) for pair, var in x.items()
        if solver.Value(var) for u, v in [pair]
    }
    record["deleted"] = len(current - chosen)
    record["added"] = len(chosen - current)
    return chosen, record


def save(path, scaffold, current, selected, history, labels, fibres):
    info, rows = layer_diagnostics(scaffold, current, labels, fibres)
    assert info["io_energy"] == 0 and info["edge_count"] == 693
    assert all(rows[support]["bad"] == 0 for support in selected)
    info.update({
        "method": "exact BP plus greedily fixed C4 fibres (linear model)",
        "claim_boundary": (
            "seed construction only; a failed stage is not an E0 exclusion"
        ),
        "c4_supports": [list(s) for s in selected],
        "c4_count": len(selected),
        "same_support_bad_total": sum(r["bad"] for r in rows.values()),
        "same_support_energy_total": sum(r["energy"] for r in rows.values()),
        "fibre_diagnostics": {str(k): v for k, v in rows.items()},
        "stage_history": history,
    })
    edges = info.pop("edges")
    info["edges"] = edges
    Path(path).write_text(json.dumps(info, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    parser.add_argument("--target", type=int, default=16)
    parser.add_argument("--seconds", type=float, default=10.0)
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--tries", type=int, default=21)
    parser.add_argument("--seed", type=int, default=1000)
    args = parser.parse_args()

    scaffold, current, labels = read_seed(args.input)
    _supports, fibres = support_data(labels)
    selected = []
    history = []
    save(args.output, scaffold, current, selected, history, labels, fibres)

    while len(selected) < args.target:
        _info, diagnostics = layer_diagnostics(scaffold, current, labels, fibres)
        remaining = [support for support in fibres if support not in selected]
        remaining.sort(key=lambda support: (
            diagnostics[support]["bad"], diagnostics[support]["energy"], support
        ))
        accepted = None
        for support in remaining[:args.tries]:
            for max_deleted in (8, 16, 32, 64, 128, 504):
                candidate, record = solve(
                    scaffold, current, labels, fibres, selected + [support],
                    max_deleted, args.seconds, args.workers,
                    args.seed + len(history) + 1,
                )
                record.update({
                    "candidate_support": list(support),
                    "before_bad": diagnostics[support]["bad"],
                    "before_energy": diagnostics[support]["energy"],
                })
                history.append(record)
                print(json.dumps(record), flush=True)
                if candidate is not None:
                    accepted = support, candidate
                    break
            if accepted is not None:
                break
        if accepted is None:
            print(json.dumps({
                "status": "GREEDY_STAGE_NOT_FOUND",
                "c4_count": len(selected),
            }), flush=True)
            break
        support, current = accepted
        selected.append(support)
        save(args.output, scaffold, current, selected, history, labels, fibres)
        info, rows = layer_diagnostics(scaffold, current, labels, fibres)
        print(json.dumps({
            "checkpoint": len(selected),
            "support": list(support),
            "energy": info["energy"],
            "same_support_bad": sum(r["bad"] for r in rows.values()),
        }), flush=True)


if __name__ == "__main__":
    main()
