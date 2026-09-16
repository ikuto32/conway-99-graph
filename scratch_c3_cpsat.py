"""Exact CP-SAT feasibility model for the fixed-point-free C3 branch.

An order-three automorphism of a hypothetical srg(99,14,1,2) is known to be
fixed-point-free.  Label vertices (orbit, phase), with 33 orbits and phases in
Z/3.  This script identifies edge and unordered-pair variables under the
phase shift.

Only upper bounds

    common(u,v) + adjacent(u,v) <= 2

are encoded.  They are nevertheless exact once every degree is 14: the sum
of all actual common-neighbour counts is 99*C(14,2)=9009, exactly the sum of
the right-hand sides over all unordered pairs.  Product helper literals need
only the implication edge(u,w) & edge(v,w) -> helper.

The number t of 3-vertex orbits inducing K3 is one of 6, 13, 20, 27.  This
follows by taking the trace of A times the automorphism on the 3- and
(-4)-eigenspaces.  For each t we safely put those K3 orbits first.  Since
orbit 0 is a triangle, it meets exactly 12 other orbits in invariant perfect
matchings; independent phase rotations and permutations within the K3 and
independent-orbit classes put those matchings into a canonical initial block.

Any feasible result is expanded and independently checked on all 4,851
unordered vertex pairs before a witness file is written.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import itertools
import json
from pathlib import Path

from ortools.sat.python import cp_model


N_ORBITS = 33
PHASES = 3
N = N_ORBITS * PHASES
T_VALUES = (6, 13, 20, 27)


def tau(v: int, power: int = 1) -> int:
    orbit, phase = divmod(v, PHASES)
    return PHASES * orbit + (phase + power) % PHASES


def pair(u: int, v: int) -> tuple[int, int]:
    return (u, v) if u < v else (v, u)


def orbit_key(u: int, v: int) -> tuple[int, int]:
    return min(pair(tau(u, p), tau(v, p)) for p in range(PHASES))


def expand_and_check(selected_keys: set[tuple[int, int]]) -> dict[str, object]:
    adjacency = [set() for _ in range(N)]
    for u, v in itertools.combinations(range(N), 2):
        if orbit_key(u, v) in selected_keys:
            adjacency[u].add(v)
            adjacency[v].add(u)

    degrees = [len(row) for row in adjacency]
    histogram: dict[str, int] = {}
    bad = []
    energy = 0
    for u, v in itertools.combinations(range(N), 2):
        adjacent = v in adjacency[u]
        common = len(adjacency[u].intersection(adjacency[v]))
        target = 1 if adjacent else 2
        residual = common - target
        histogram[str(residual)] = histogram.get(str(residual), 0) + 1
        energy += residual * residual
        if residual:
            bad.append((u, v, adjacent, common, target))

    edges = [
        (u + 1, v + 1)
        for u, v in itertools.combinations(range(N), 2)
        if v in adjacency[u]
    ]
    assert len(edges) == len(set(edges))
    return {
        "vertices": N,
        "edges_count": len(edges),
        "degree_min": min(degrees),
        "degree_max": max(degrees),
        "energy": energy,
        "bad_pairs": len(bad),
        "residual_histogram": histogram,
        "bad_examples": bad[:20],
        "edges": edges,
    }


def solve_branch(t_value: int, seconds: float, workers: int, log: bool) -> dict[str, object]:
    assert t_value in T_VALUES
    model = cp_model.CpModel()

    keys = sorted({orbit_key(u, v) for u, v in itertools.combinations(range(N), 2)})
    assert len(keys) == 1617
    edge_var = {key: model.new_bool_var("") for key in keys}

    def edge(u: int, v: int) -> cp_model.IntVar:
        return edge_var[orbit_key(u, v)]

    # There are exactly t K3 orbits; S_33 lets us put them first.
    for orbit in range(N_ORBITS):
        model.add(edge(PHASES * orbit, PHASES * orbit + 1) == (orbit < t_value))

    # One degree equation per vertex orbit suffices by C3 invariance.
    for orbit in range(N_ORBITS):
        u = PHASES * orbit
        model.add(sum(edge(u, v) for v in range(N) if v != u) == 14)

    # Canonicalize all edges from triangle orbit 0.  Two vertices of this K3
    # already have their third vertex as their unique common neighbour, so an
    # outside vertex cannot meet two of them.  Each other orbit is therefore
    # empty or a perfect matching.  Rotate its phase to make that matching
    # phase-preserving, and sort occupied orbits within the two orbit classes.
    connection = []
    for orbit in range(1, N_ORBITS):
        base = PHASES * orbit
        c = edge(0, base)
        connection.append(c)
        model.add(edge(0, base + 1) == 0)
        model.add(edge(0, base + 2) == 0)
    model.add(sum(connection) == 12)
    for start, stop in ((1, t_value), (t_value, N_ORBITS)):
        for orbit in range(start, stop - 1):
            model.add(edge(0, PHASES * orbit) >= edge(0, PHASES * (orbit + 1)))

    representatives = []
    for u, v in itertools.combinations(range(N), 2):
        if pair(u, v) == orbit_key(u, v):
            representatives.append((u, v))
    assert len(representatives) == 1617

    products = 0
    reused = 0
    for u, v in representatives:
        terms: list[cp_model.IntVar] = []
        for w in range(N):
            if w == u or w == v:
                continue
            a = edge(u, w)
            b = edge(v, w)
            if a is b:
                terms.append(a)
                reused += 1
            else:
                both = model.new_bool_var("")
                model.add_bool_or([~a, ~b, both])
                terms.append(both)
                products += 1
        model.add(sum(terms) + edge(u, v) <= 2)

    build = {
        "event": "built",
        "t": t_value,
        "edge_orbit_variables": len(edge_var),
        "pair_orbits": len(representatives),
        "product_variables": products,
        "reused_product_literals": reused,
        "proto_variables": len(model.proto.variables),
        "proto_constraints": len(model.proto.constraints),
    }
    print(json.dumps(build), flush=True)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_search_workers = workers
    solver.parameters.log_search_progress = log
    status = solver.solve(model)
    record: dict[str, object] = {
        **build,
        "status": solver.status_name(status),
        "wall_seconds": solver.wall_time,
        "branches": solver.num_branches,
        "conflicts": solver.num_conflicts,
        "response_stats": solver.response_stats(),
    }
    result_path = Path(f"scratch_c3_cpsat_t{t_value}_result.json")
    result_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in record.items() if k != "response_stats"}), flush=True)

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        selected = {key for key, var in edge_var.items() if solver.value(var)}
        checked = expand_and_check(selected)
        assert checked["energy"] == 0
        assert checked["bad_pairs"] == 0
        assert checked["edges_count"] == 693
        assert checked["degree_min"] == checked["degree_max"] == 14
        witness_path = Path(f"scratch_c3_solution_t{t_value}.json")
        witness_path.write_text(json.dumps(checked, indent=2) + "\n", encoding="utf-8")
        record["verified_witness"] = str(witness_path)
    return record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--t", type=int, choices=T_VALUES)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--seconds", type=float, default=180.0)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--log", action="store_true")
    args = parser.parse_args()
    if args.all == (args.t is not None):
        parser.error("choose exactly one of --t or --all")

    if args.t is not None:
        solve_branch(args.t, args.seconds, args.workers, args.log)
        return

    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(solve_branch, t, args.seconds, args.workers, args.log): t
            for t in T_VALUES
        }
        records = []
        for future in concurrent.futures.as_completed(futures):
            records.append(future.result())
    records.sort(key=lambda row: int(row["t"]))
    Path("scratch_c3_cpsat_summary.json").write_text(
        json.dumps(records, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
