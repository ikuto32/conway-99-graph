"""Build a BP + same-support-pair seed one fibre at a time.

Each accepted checkpoint satisfies exact BP and every pair equation in all
previously selected fibres.  A bounded-Hamming satisfaction model is used at
each stage; every returned graph is independently expanded and checked before
the next fibre is attempted.
"""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

from ortools.sat.python import cp_model

from scratch_general_v2_cpsat_energy import O, M, canon, metrics, read_seed


def support_data(labels):
    supports = [tuple(sorted((symbol - 1) // 2 for symbol in label)) for label in labels]
    fibres = {}
    for u, support in enumerate(supports):
        fibres.setdefault(support, []).append(u)
    assert len(fibres) == 21 and all(len(vs) == 4 for vs in fibres.values())
    return supports, fibres


def layer_diagnostics(scaffold, mutable, labels, fibres):
    info, adj = metrics(scaffold, mutable)
    rows = {}
    for support, fibre in fibres.items():
        residuals = []
        for u, v in itertools.combinations(fibre, 2):
            gu, gv = O + u, O + v
            residuals.append(len(adj[gu] & adj[gv]) + int(gv in adj[gu]) - 2)
        rows[support] = {
            "bad": sum(r != 0 for r in residuals),
            "energy": sum(r * r for r in residuals),
            "residuals": residuals,
        }
    return info, rows


def solve_stage(scaffold, current, labels, fibres, selected, max_deleted,
                seconds, workers, random_seed):
    model = cp_model.CpModel()
    pairs = list(itertools.combinations(range(M), 2))
    x = {pair: model.NewBoolVar(f"e_{pair[0]}_{pair[1]}") for pair in pairs}

    def edge(u, v):
        return x[canon(u, v)]

    for u, label in enumerate(labels):
        groups = {(symbol - 1) // 2 for symbol in label}
        for symbol in range(1, 15):
            model.Add(
                sum(edge(u, v) for v, other in enumerate(labels)
                    if u != v and symbol in other)
                == (1 if (symbol - 1) // 2 in groups else 2)
            )

    products = 0
    for support in selected:
        for u, v in itertools.combinations(fibres[support], 2):
            terms = [edge(u, v)]
            for w in range(M):
                if w in (u, v):
                    continue
                z = model.NewBoolVar(f"z_{u}_{v}_{w}")
                model.AddMultiplicationEquality(z, (edge(u, w), edge(v, w)))
                terms.append(z)
                products += 1
            fixed_common = len(set(labels[u]) & set(labels[v]))
            model.Add(sum(terms) == 2 - fixed_common)

    current_local = {(u - O, v - O) for u, v in current}
    model.Add(sum(x[pair] for pair in current_local) >= 504 - max_deleted)
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
        "seconds": solver.WallTime(),
        "branches": solver.NumBranches(),
        "conflicts": solver.NumConflicts(),
        "selected_fibres": len(selected),
        "products": products,
        "max_deleted": max_deleted,
    }
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None, record
    chosen = {(O + u, O + v) for (u, v), var in x.items() if solver.Value(var)}
    record["deleted"] = len(current - chosen)
    record["added"] = len(chosen - current)
    return chosen, record


def save_checkpoint(path, scaffold, mutable, selected, history, labels, fibres):
    info, rows = layer_diagnostics(scaffold, mutable, labels, fibres)
    assert info["io_energy"] == 0 and info["edge_count"] == 693
    assert all(rows[support]["bad"] == 0 for support in selected)
    info.update({
        "method": "incremental exact BP + same-support fibre equations",
        "selected_fibres": [list(s) for s in selected],
        "selected_count": len(selected),
        "same_support_bad_total": sum(row["bad"] for row in rows.values()),
        "same_support_energy_total": sum(row["energy"] for row in rows.values()),
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
    parser.add_argument("--seconds", type=float, default=8)
    parser.add_argument("--workers", type=int, default=12)
    parser.add_argument("--tries", type=int, default=3)
    parser.add_argument("--seed", type=int, default=1)
    args = parser.parse_args()

    scaffold, current, labels = read_seed(args.input)
    _supports, fibres = support_data(labels)
    selected = []
    history = []
    seed_counter = args.seed
    save_checkpoint(args.output, scaffold, current, selected, history, labels, fibres)

    while len(selected) < 21:
        _info, diagnostics = layer_diagnostics(scaffold, current, labels, fibres)
        remaining = [support for support in fibres if support not in selected]
        remaining.sort(key=lambda support: (
            diagnostics[support]["bad"], diagnostics[support]["energy"], support
        ))
        accepted = None
        # Try the currently easiest few fibres.  The widening Hamming bounds
        # avoid mistaking a too-small neighbourhood for layer infeasibility.
        for support in remaining[: args.tries]:
            for max_deleted in (24, 48, 96, 504):
                seed_counter += 1
                candidate, record = solve_stage(
                    scaffold, current, labels, fibres, selected + [support],
                    max_deleted, args.seconds, args.workers, seed_counter,
                )
                record.update({
                    "candidate_support": list(support),
                    "before_bad": diagnostics[support]["bad"],
                    "before_energy": diagnostics[support]["energy"],
                })
                history.append(record)
                print(json.dumps(record), flush=True)
                if candidate is not None:
                    accepted = (support, candidate)
                    break
            if accepted is not None:
                break
        if accepted is None:
            print(json.dumps({
                "status": "BLOCKED_STAGE_UNKNOWN",
                "selected_count": len(selected),
                "remaining": [list(s) for s in remaining],
            }), flush=True)
            break
        support, current = accepted
        selected.append(support)
        save_checkpoint(args.output, scaffold, current, selected, history, labels, fibres)
        info, diagnostics = layer_diagnostics(scaffold, current, labels, fibres)
        print(json.dumps({
            "checkpoint": len(selected),
            "support": list(support),
            "energy": info["energy"],
            "remaining_same_support_bad": sum(row["bad"] for row in diagnostics.values()),
        }), flush=True)


if __name__ == "__main__":
    main()
