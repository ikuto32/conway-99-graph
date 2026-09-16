"""Exact CNF/SAT experiment for the complete C2 automorphism branch.

The 84 outer vertices are the non-matching two-subsets of the 14 symbols
around a fixed root.  The involution sends

    tau({a,b}) = {a xor 1, b xor 1}.

Outer edge variables are identified under tau and u--tau(u) is a forced
nonedge.  The BP=P*A0 equations force every outer degree to be 12.  For one
representative of every tau-orbit of outer pairs this encoding requires

    common_outer(u,v) + edge(u,v)
        <= 2 - |label(u) intersect label(v)|.

This upper-bound encoding is exact globally: the left side sums to
84*C(12,2)+504=6048, while the right side sums to
2*C(84,2)-14*C(12,2)=6048.  Product indicators therefore need only the
one-way implication edge(u,w) & edge(v,w) -> product.

Safe symmetry breaking fixes a disjoint-support edge {0,2}--{4,6}.  Indeed,
for any outer u, if a,s,d count its neighbours with the same, one shared,
and disjoint coordinate supports, the four on-support BP equations give
2a+s=4 and degree 12 gives d=8+a.  The rooted coordinate group centralizes
tau and is transitive on ordered disjoint-support edges.  The two possible
same-support neighbours of {0,2} can be swapped by the stabilizer, so the
three branches a0/a1/a2 are exhaustive (with a normalized polarity at a1).

Any SAT model is expanded and checked independently on all 99 vertices and
4,851 pairs.  This script never creates submission.txt.
"""

from __future__ import annotations

import argparse
import itertools
import json
import multiprocessing as mp
import queue
import time
from pathlib import Path


CNF_PATH = Path("scratch_c2_exact.cnf")
BUILD_PATH = Path("scratch_c2_exact_build.json")
PORTFOLIO_PATH = Path("scratch_c2_exact_portfolio.json")
BRANCHES = ("a0", "a1", "a2")


def coordinates():
    labels = [p for p in itertools.combinations(range(14), 2)
              if p[0] // 2 != p[1] // 2]
    index = {label: i for i, label in enumerate(labels)}
    tau = [index[tuple(sorted((a ^ 1, b ^ 1)))] for a, b in labels]
    assert len(labels) == 84
    assert all(tau[tau[u]] == u and tau[u] != u for u in range(84))
    return labels, index, tau


def edge_variables(tau: list[int]):
    def pair(u: int, v: int) -> tuple[int, int]:
        return (u, v) if u < v else (v, u)

    def key(u: int, v: int) -> tuple[int, int]:
        return min(pair(u, v), pair(tau[u], tau[v]))

    variables: dict[tuple[int, int], int] = {}
    for u, v in itertools.combinations(range(84), 2):
        if v == tau[u]:
            continue
        q = key(u, v)
        if q not in variables:
            variables[q] = len(variables) + 1
    assert len(variables) == 1722

    def edge(u: int, v: int) -> int | None:
        if u == v or v == tau[u]:
            return None
        return variables[key(u, v)]

    return variables, edge


def branch_units(index: dict[tuple[int, int], int], edge) -> dict[str, list[int]]:
    u = index[(0, 2)]
    fixed = edge(u, index[(4, 6)])
    x = edge(u, index[(0, 3)])
    y = edge(u, index[(1, 2)])
    assert fixed is not None and x is not None and y is not None
    assert len({fixed, x, y}) == 3
    return {
        "a0": [fixed, -x, -y],
        "a1": [fixed, x, -y],
        "a2": [fixed, x, y],
    }


def build_cnf(path: Path = CNF_PATH) -> dict[str, object]:
    from pysat.card import CardEnc, EncType
    from pysat.formula import IDPool

    labels, index, tau = coordinates()
    variables, edge = edge_variables(tau)
    pool = IDPool(start_from=len(variables) + 1)
    clauses: list[list[int]] = []

    bp_constraints = 0
    for u, label in enumerate(labels):
        own = set(label)
        for symbol in range(14):
            lits = []
            for v, other in enumerate(labels):
                if u != v and symbol in other:
                    value = edge(u, v)
                    if value is not None:
                        lits.append(value)
            assert len(lits) in (10, 11, 12)
            assert len(lits) == len(set(lits))
            target = 1 if symbol in own or (symbol ^ 1) in own else 2
            clauses.extend(CardEnc.equals(
                lits=lits, bound=target, vpool=pool,
                encoding=EncType.seqcounter).clauses)
            bp_constraints += 1

    representatives = []
    fixed_pair_orbits = 0
    for u, v in itertools.combinations(range(84), 2):
        p = (u, v)
        q = tuple(sorted((tau[u], tau[v])))
        if p <= q:
            representatives.append(p)
            fixed_pair_orbits += p == q
    assert len(representatives) == 1764 and fixed_pair_orbits == 42

    products = 0
    skipped = 0
    targets = {1: 0, 2: 0}
    max_terms = 0
    for u, v in representatives:
        terms: list[int] = []
        for w in range(84):
            if w == u or w == v:
                continue
            a, b = edge(u, w), edge(v, w)
            if a is None or b is None:
                skipped += 1
                continue
            assert a != b
            z = pool.id(("and", u, v, w))
            clauses.append([-a, -b, z])
            terms.append(z)
            products += 1
        direct = edge(u, v)
        if direct is not None:
            terms.append(direct)
        target = 2 - len(set(labels[u]).intersection(labels[v]))
        assert target in (1, 2)
        targets[target] += 1
        max_terms = max(max_terms, len(terms))
        clauses.extend(CardEnc.atmost(
            lits=terms, bound=target, vpool=pool,
            encoding=EncType.seqcounter).clauses)

    units = branch_units(index, edge)
    meta: dict[str, object] = {
        "model": "exact complete C2 automorphism branch",
        "edge_orbit_variables": len(variables),
        "bp_constraints": bp_constraints,
        "pair_orbits": len(representatives),
        "fixed_pair_orbits": fixed_pair_orbits,
        "pair_target_histogram": targets,
        "product_variables": products,
        "skipped_forced_products": skipped,
        "max_pair_terms": max_terms,
        "variables": pool.top,
        "clauses": len(clauses),
        "branch_units": units,
        "symmetry_breaking": {
            "fixed_disjoint_edge": [[0, 2], [4, 6]],
            "same_support_count_branches": list(BRANCHES),
            "exhaustive": True,
        },
    }
    with path.open("w", encoding="ascii", newline="\n") as handle:
        handle.write(f"p cnf {pool.top} {len(clauses)}\n")
        for clause in clauses:
            handle.write(" ".join(map(str, clause)) + " 0\n")
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
    out_queue.put({
        "branch": branch,
        "status": "SAT" if answer else "UNSAT",
        "load_seconds": round(loaded - started, 3),
        "solve_seconds": round(time.monotonic() - loaded, 3),
        "wall_seconds": round(time.monotonic() - started, 3),
        "stats": stats,
        "positive_edge_variables": (
            [lit for lit in model if 0 < lit <= 1722] if model else []),
    })


def verify_edge_model(positive: set[int]) -> dict[str, object]:
    from scratch_bp_seed import expand_and_check

    labels, _index, tau = coordinates()
    _variables, edge = edge_variables(tau)
    physical = {}
    for u, v in itertools.combinations(range(84), 2):
        value = edge(u, v)
        physical[u, v] = value if value is not None else 0
    result = expand_and_check(labels, physical, positive)
    result["c2_invariant"] = all(
        ((edge(u, v) or 0) in positive)
        == ((edge(tau[u], tau[v]) or 0) in positive)
        for u, v in itertools.combinations(range(84), 2))
    result["forced_tau_pairs_absent"] = all(
        physical[min(u, tau[u]), max(u, tau[u])] not in positive
        for u in range(84))
    result["ok"] = (
        result["energy"] == 0 and result["bad_pairs"] == 0
        and result["edge_count"] == 693 and result["c2_invariant"]
        and result["forced_tau_pairs_absent"])
    return result


def run_portfolio(seconds: float, cnf_path: Path = CNF_PATH):
    meta = json.loads(BUILD_PATH.read_text(encoding="utf-8"))
    units = meta["branch_units"]
    context = mp.get_context("spawn")
    out_queue = context.Queue()
    processes = {}
    for branch in BRANCHES:
        p = context.Process(target=worker,
                            args=(branch, str(cnf_path.resolve()),
                                  units[branch], out_queue),
                            name=f"c2-{branch}")
        p.start()
        processes[branch] = p

    deadline = time.monotonic() + seconds
    records = {}
    while len(records) < len(BRANCHES):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        try:
            record = out_queue.get(timeout=min(1.0, remaining))
        except queue.Empty:
            continue
        records[record["branch"]] = record

    for branch, process in processes.items():
        if process.is_alive():
            process.terminate()
            process.join(10)
        else:
            process.join()
        if branch not in records:
            records[branch] = {
                "branch": branch, "status": "UNKNOWN",
                "wall_limit_seconds": seconds,
                "exit_code_after_termination": process.exitcode,
            }

    for branch in BRANCHES:
        record = records[branch]
        if record["status"] == "SAT":
            verified = verify_edge_model(set(record["positive_edge_variables"]))
            record["verification"] = {
                k: v for k, v in verified.items() if k != "edges"}
            if verified["ok"]:
                Path("scratch_c2_exact_solution.json").write_text(
                    json.dumps(verified, indent=2) + "\n", encoding="utf-8")
            break

    status = ("SAT" if any(records[b]["status"] == "SAT" for b in BRANCHES)
              else "UNSAT" if all(records[b]["status"] == "UNSAT"
                                   for b in BRANCHES)
              else "UNKNOWN")
    summary = {
        "solver": "CaDiCaL 1.9.5 via PySAT",
        "wall_limit_seconds_per_parallel_branch": seconds,
        "branches_exhaustive": True,
        "status": status,
        "records": [records[b] for b in BRANCHES],
    }
    PORTFOLIO_PATH.write_text(json.dumps(summary, indent=2) + "\n",
                              encoding="utf-8")
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
        BUILD_PATH.write_text(json.dumps(meta, indent=2) + "\n",
                              encoding="utf-8")
        print(json.dumps(meta, sort_keys=True), flush=True)
    if args.solve_seconds > 0:
        print(json.dumps(run_portfolio(args.solve_seconds), sort_keys=True),
              flush=True)
    if not args.build and args.solve_seconds <= 0:
        parser.error("select --build and/or --solve-seconds")


if __name__ == "__main__":
    mp.freeze_support()
    main()
