"""Exact CNF portfolio for the unrestricted rooted 84-vertex reduction.

The fixed scaffold consists of a root, its 14 neighbours (seven matching
pairs), and 84 outer vertices labelled by the non-matching two-subsets of the
14 inner symbols.  Only the 3,486 possible outer edges are variables.

The linear equations B P = P A0 force every outer degree to be 12 and settle
all root/inner pair conditions.  For each outer pair this CNF imposes

  common_outer(u,v) + edge(u,v) <= 2 - |label(u) intersect label(v)|.

The inequalities are exact globally: their left sides sum to
84*C(12,2)+504=6048, exactly their summed right sides.  Product helpers need
only encode edge(u,w)&edge(v,w) -> helper.

Safe symmetry breaking fixes one disjoint-support edge {0,2}--{4,6}.  Such an
edge always exists: if a,s,d count a vertex's neighbours on the same, singly
overlapping, and disjoint two-group supports, BP gives 2a+s=4 and
a+s+d=12, hence d=8+a.  The scaffold stabilizer is transitive on these
ordered edges.  The three other labels on {0,1} x {2,3} give five orbits of
allowed same-support neighbourhoods under the remaining coordinate swap;
the five branch assignments below are exhaustive.

Any SAT assignment is expanded and independently checked on all 99 vertices.
This script deliberately never writes submission.txt.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import multiprocessing as mp
import queue
import time
from pathlib import Path


CNF_PATH = Path("scratch_general_exact.cnf")
BUILD_PATH = Path("scratch_general_exact_build.json")
PORTFOLIO_PATH = Path("scratch_general_exact_portfolio.json")
BRANCHES = ("a0", "a1_complement", "a1_cross", "a2_crosses", "a2_mixed")


def coordinates():
    labels = [
        pair
        for pair in itertools.combinations(range(14), 2)
        if pair[0] // 2 != pair[1] // 2
    ]
    index = {label: i for i, label in enumerate(labels)}
    variables = {p: n for n, p in enumerate(itertools.combinations(range(84), 2), 1)}
    assert len(labels) == 84 and len(variables) == 3486

    def edge(u: int, v: int) -> int:
        return variables[(u, v) if u < v else (v, u)]

    return labels, index, variables, edge


def branch_units(index, edge) -> dict[str, list[int]]:
    u = index[(0, 2)]
    fixed = edge(u, index[(4, 6)])
    x = edge(u, index[(0, 3)])
    y = edge(u, index[(1, 2)])
    complement = edge(u, index[(1, 3)])
    assert len({fixed, x, y, complement}) == 4
    return {
        "a0": [fixed, -x, -y, -complement],
        "a1_complement": [fixed, -x, -y, complement],
        "a1_cross": [fixed, x, -y, -complement],
        "a2_crosses": [fixed, x, y, -complement],
        "a2_mixed": [fixed, x, -y, complement],
    }


def build_cnf() -> dict[str, object]:
    from pysat.card import CardEnc, EncType
    from pysat.formula import IDPool

    labels, index, variables, edge = coordinates()
    pool = IDPool(start_from=len(variables) + 1)
    clauses: list[list[int]] = []

    for u, label in enumerate(labels):
        own = set(label)
        for symbol in range(14):
            lits = [
                edge(u, v)
                for v, other in enumerate(labels)
                if u != v and symbol in other
            ]
            assert len(lits) in (11, 12) and len(lits) == len(set(lits))
            target = 1 if symbol in own or (symbol ^ 1) in own else 2
            clauses.extend(
                CardEnc.equals(lits, target, vpool=pool, encoding=EncType.seqcounter).clauses
            )

    products = 0
    target_histogram = {1: 0, 2: 0}
    for u, v in itertools.combinations(range(84), 2):
        terms = []
        for w in range(84):
            if w == u or w == v:
                continue
            a = edge(u, w)
            b = edge(v, w)
            assert a != b
            z = pool.id(("and", u, v, w))
            clauses.append([-a, -b, z])
            terms.append(z)
            products += 1
        terms.append(edge(u, v))
        target = 2 - len(set(labels[u]).intersection(labels[v]))
        assert target in (1, 2)
        target_histogram[target] += 1
        clauses.extend(
            CardEnc.atmost(terms, target, vpool=pool, encoding=EncType.seqcounter).clauses
        )

    units = branch_units(index, edge)
    meta: dict[str, object] = {
        "model": "exact unrestricted rooted 84-vertex reduction",
        "edge_variables": len(variables),
        "bp_constraints": 84 * 14,
        "outer_pair_constraints": 84 * 83 // 2,
        "target_histogram": target_histogram,
        "product_variables": products,
        "variables": pool.top,
        "clauses": len(clauses),
        "branch_units": units,
        "branches_exhaustive": True,
    }
    with CNF_PATH.open("w", encoding="ascii", newline="\n") as handle:
        handle.write(f"p cnf {pool.top} {len(clauses)}\n")
        for clause in clauses:
            handle.write(" ".join(map(str, clause)) + " 0\n")
    meta["cnf_sha256"] = hashlib.sha256(CNF_PATH.read_bytes()).hexdigest().upper()
    BUILD_PATH.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    return meta


def worker(branch: str, cnf_path: str, units: list[int], out_queue) -> None:
    from pysat.formula import CNF
    from pysat.solvers import Solver

    started = time.monotonic()
    formula = CNF(from_file=cnf_path)
    loaded = time.monotonic()
    with Solver(name="cadical195", bootstrap_with=formula.clauses) as solver:
        answer = solver.solve(assumptions=units)
        model = solver.get_model() if answer else None
        stats = solver.accum_stats()
    out_queue.put(
        {
            "branch": branch,
            "status": "SAT" if answer else "UNSAT",
            "load_seconds": round(loaded - started, 3),
            "solve_seconds": round(time.monotonic() - loaded, 3),
            "stats": stats,
            "positive_edge_variables": [lit for lit in model if 0 < lit <= 3486] if model else [],
        }
    )


def verify(positive: set[int]) -> dict[str, object]:
    from scratch_bp_seed import expand_and_check

    labels, _index, variables, _edge = coordinates()
    result = expand_and_check(labels, variables, positive)
    result["ok"] = (
        result["energy"] == 0
        and result["bad_pairs"] == 0
        and result["edge_count"] == 693
        and result["inner_outer_bad_pairs"] == 0
    )
    return result


def run_portfolio(seconds: float) -> dict[str, object]:
    meta = json.loads(BUILD_PATH.read_text(encoding="utf-8"))
    context = mp.get_context("spawn")
    out_queue = context.Queue()
    processes = {}
    for branch in BRANCHES:
        process = context.Process(
            target=worker,
            args=(branch, str(CNF_PATH.resolve()), meta["branch_units"][branch], out_queue),
            name=f"general-{branch}",
        )
        process.start()
        processes[branch] = process

    deadline = time.monotonic() + seconds
    records: dict[str, dict[str, object]] = {}
    while len(records) < len(BRANCHES):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        try:
            record = out_queue.get(timeout=min(1.0, remaining))
        except queue.Empty:
            continue
        records[str(record["branch"])] = record

    for branch, process in processes.items():
        if process.is_alive():
            process.terminate()
            process.join(10)
        else:
            process.join()
        if branch not in records:
            records[branch] = {
                "branch": branch,
                "status": "UNKNOWN",
                "wall_limit_seconds": seconds,
                "exit_code_after_termination": process.exitcode,
            }

    for branch in BRANCHES:
        record = records[branch]
        if record["status"] == "SAT":
            checked = verify(set(record["positive_edge_variables"]))
            record["verification"] = {k: v for k, v in checked.items() if k != "edges"}
            if checked["ok"]:
                Path("scratch_general_exact_solution.json").write_text(
                    json.dumps(checked, indent=2) + "\n", encoding="utf-8"
                )
            break

    summary = {
        "solver": "CaDiCaL 1.9.5 via PySAT",
        "wall_limit_seconds_per_parallel_branch": seconds,
        "branches_exhaustive": True,
        "status": (
            "SAT" if any(records[b]["status"] == "SAT" for b in BRANCHES)
            else "UNSAT" if all(records[b]["status"] == "UNSAT" for b in BRANCHES)
            else "UNKNOWN"
        ),
        "records": [records[b] for b in BRANCHES],
    }
    PORTFOLIO_PATH.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--solve-seconds", type=float, default=0.0)
    args = parser.parse_args()
    if args.build:
        started = time.monotonic()
        meta = build_cnf()
        meta["build_seconds"] = round(time.monotonic() - started, 3)
        BUILD_PATH.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(meta, sort_keys=True), flush=True)
    if args.solve_seconds > 0:
        print(json.dumps(run_portfolio(args.solve_seconds), sort_keys=True), flush=True)
    if not args.build and args.solve_seconds <= 0:
        parser.error("select --build and/or --solve-seconds")


if __name__ == "__main__":
    mp.freeze_support()
    main()
