"""Find minimum-support {-1,0,1} moves preserving all rooted BP rows.

For the 84 outer vertices, a signed edge vector ``h`` is a legal linear
move when, for every outer vertex ``u`` and root-neighbour symbol ``s``,

    sum_{v: s in label(v)} h_{uv} = 0.

These are exactly the homogeneous versions of the 1,176 equations BP=PA0.
The optimization below is independent of any incumbent 0/1 graph.  It finds
the smallest support move containing one representative edge of each orbit
of the rooted scaffold group.  A move is only *applicable* to an incumbent
when all -1 cells are present and all +1 cells are absent.
"""

from __future__ import annotations

import argparse
import itertools
import json
import time
from pathlib import Path

from ortools.sat.python import cp_model


INNER = 14
LABELS = [
    pair
    for pair in itertools.combinations(range(INNER), 2)
    if pair[0] // 2 != pair[1] // 2
]
assert len(LABELS) == 84
PAIRS = list(itertools.combinations(range(84), 2))


def pair_class(u: int, v: int) -> str:
    a, b = LABELS[u], LABELS[v]
    exact = len(set(a) & set(b))
    supports = {x // 2 for x in a}, {x // 2 for x in b}
    group_overlap = len(supports[0] & supports[1])
    if group_overlap == 2:
        assert exact in (0, 1)
        return "same_side" if exact == 1 else "same_diagonal"
    if group_overlap == 1:
        assert exact in (0, 1)
        return "overlap_exact" if exact == 1 else "overlap_opposite"
    assert group_overlap == 0 and exact == 0
    return "disjoint"


def representatives() -> dict[str, tuple[int, int]]:
    result: dict[str, tuple[int, int]] = {}
    for pair in PAIRS:
        result.setdefault(pair_class(*pair), pair)
    assert set(result) == {
        "same_side", "same_diagonal", "overlap_exact",
        "overlap_opposite", "disjoint",
    }
    return result


def solve_one(name: str, anchor: tuple[int, int], seconds: float, workers: int) -> dict:
    model = cp_model.CpModel()
    pos = {e: model.NewBoolVar(f"p_{e[0]}_{e[1]}") for e in PAIRS}
    neg = {e: model.NewBoolVar(f"n_{e[0]}_{e[1]}") for e in PAIRS}
    for e in PAIRS:
        model.Add(pos[e] + neg[e] <= 1)

    incident = [[[] for _ in range(INNER)] for _ in range(84)]
    for u, v in PAIRS:
        for symbol in LABELS[v]:
            incident[u][symbol].append((u, v))
        for symbol in LABELS[u]:
            incident[v][symbol].append((u, v))
    for u in range(84):
        for symbol in range(INNER):
            cells = incident[u][symbol]
            model.Add(sum(pos[e] - neg[e] for e in cells) == 0)

    model.Add(pos[anchor] == 1)
    support = sum(pos.values()) + sum(neg.values())
    model.Minimize(support)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = 7301 + list(representatives()).index(name)
    solver.parameters.log_search_progress = False
    started = time.monotonic()
    status = solver.Solve(model)
    record = {
        "class": name,
        "anchor": list(anchor),
        "anchor_labels": [list(LABELS[x]) for x in anchor],
        "status": solver.StatusName(status),
        "wall_seconds": time.monotonic() - started,
        "solver_wall_seconds": solver.WallTime(),
        "objective": None,
        "best_bound": solver.BestObjectiveBound(),
        "positive": [],
        "negative": [],
    }
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        positive = [e for e in PAIRS if solver.Value(pos[e])]
        negative = [e for e in PAIRS if solver.Value(neg[e])]
        record["objective"] = len(positive) + len(negative)
        record["positive"] = [list(e) for e in positive]
        record["negative"] = [list(e) for e in negative]
        record["positive_labels"] = [
            [list(LABELS[u]), list(LABELS[v])] for u, v in positive
        ]
        record["negative_labels"] = [
            [list(LABELS[u]), list(LABELS[v])] for u, v in negative
        ]
        # Independent direct replay of all homogeneous BP rows.
        signed = {e: 1 for e in positive} | {e: -1 for e in negative}
        residuals = []
        for u in range(84):
            for symbol in range(INNER):
                residuals.append(sum(
                    value
                    for (a, b), value in signed.items()
                    if (a == u and symbol in LABELS[b])
                    or (b == u and symbol in LABELS[a])
                ))
        assert set(residuals) == {0}
        assert anchor in positive
        record["replay_all_1176_zero"] = True
    return record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seconds", type=float, default=60.0)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--output", default="scratch_root_bp_kernel_min.json")
    parser.add_argument("--class", dest="only_class")
    args = parser.parse_args()
    reps = representatives()
    if args.only_class:
        if args.only_class not in reps:
            raise SystemExit(f"unknown class {args.only_class!r}; choose from {sorted(reps)}")
        reps = {args.only_class: reps[args.only_class]}
    records = []
    for name, anchor in reps.items():
        rec = solve_one(name, anchor, args.seconds, args.workers)
        records.append(rec)
        print(json.dumps({k: rec[k] for k in (
            "class", "status", "objective", "best_bound", "wall_seconds"
        )}), flush=True)
    payload = {
        "model": "minimum {-1,0,1} homogeneous BP kernel move",
        "outer_vertices": 84,
        "edge_cells": len(PAIRS),
        "bp_rows": 84 * 14,
        "orbit_anchors": {name: list(pair) for name, pair in representatives().items()},
        "records": records,
    }
    Path(args.output).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
