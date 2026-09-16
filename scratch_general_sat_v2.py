"""Propagation-strong exact SAT encoding of the unrestricted rooted model.

This is an independent strengthening of ``scratch_general_exact_sat.py``.
The 3,486 edge variables have exactly the same numbering, but every common-
neighbour helper is a *full* Tseitin AND and every outer-pair cardinality is
an explicit equality.  The lower bound for ``>= 2`` is encoded by a linear
monotone threshold circuit rather than by complementing a sequential
``at-most`` counter.

Several inexpensive consequences of BP are repeated deliberately:

* every outer vertex has degree 12, split as two exact-symbol and ten
  exact-symbol-disjoint neighbours;
* every vertex has degree 2 inside each incident support group and degree 4
  into each other support group;
* a same-support diagonal edge excludes all four incident square sides.

All symmetry assumptions are imported from the mechanically audited
triangle-orbit decomposition.  A SAT result is independently expanded to 99
vertices and checked.  This script never writes ``submission.txt``.
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


PREFIX = "scratch_general_sat_v2"
CNF_PATH = Path(f"{PREFIX}.cnf")
BUILD_PATH = Path(f"{PREFIX}_build.json")
BENCH_PATH = Path(f"{PREFIX}_benchmark.json")
PORTFOLIO_PATH = Path(f"{PREFIX}_portfolio.json")


def coordinates():
    labels = [
        pair
        for pair in itertools.combinations(range(14), 2)
        if pair[0] // 2 != pair[1] // 2
    ]
    index = {label: i for i, label in enumerate(labels)}
    variables = {p: n for n, p in enumerate(itertools.combinations(range(84), 2), 1)}
    assert len(labels) == 84 and len(index) == 84 and len(variables) == 3486

    def edge(u: int, v: int) -> int:
        assert u != v
        return variables[(u, v) if u < v else (v, u)]

    return labels, index, variables, edge


def add_atleast_two_linear(
    clauses: list[list[int]], terms: list[int], pool, key: tuple[int, int]
) -> int:
    """Add a linear Tseitin circuit asserting at least two terms are true.

    ``seen1`` and ``seen2`` are exact prefix threshold indicators.  Full
    equivalences prevent auxiliary-variable slack and give useful backwards
    propagation from the asserted final ``seen2`` bit.
    """

    assert len(terms) >= 2 and len(set(terms)) == len(terms)
    seen1 = terms[0]
    # The one-element prefix has no >=2 state; start with the second term.
    seen2 = pool.id(("atleast2", key, 1, 2))
    x = terms[1]
    # seen2 <-> (terms[0] & terms[1])
    clauses.extend(([-seen1, -x, seen2], [seen1, -seen2], [x, -seen2]))
    new_seen1 = pool.id(("atleast2", key, 1, 1))
    # new_seen1 <-> (seen1 | x)
    clauses.extend(([-seen1, new_seen1], [-x, new_seen1], [seen1, x, -new_seen1]))
    seen1 = new_seen1

    for position, x in enumerate(terms[2:], 2):
        new_seen1 = pool.id(("atleast2", key, position, 1))
        new_seen2 = pool.id(("atleast2", key, position, 2))
        # new_seen1 <-> (seen1 | x)
        clauses.extend(([-seen1, new_seen1], [-x, new_seen1], [seen1, x, -new_seen1]))
        # new_seen2 <-> (seen2 | (seen1 & x))
        clauses.extend(
            (
                [-seen2, new_seen2],
                [-seen1, -x, new_seen2],
                [-new_seen2, seen2, seen1],
                [-new_seen2, seen2, x],
            )
        )
        seen1, seen2 = new_seen1, new_seen2
    clauses.append([seen2])
    return 2 * len(terms) - 2


def add_equals_small(
    clauses: list[list[int]], terms: list[int], target: int, pool, CardEnc, EncType,
    key: tuple[int, int]
) -> int:
    """Propagation-complete at-most plus explicit small positive lower bound."""

    before = pool.top
    clauses.extend(
        CardEnc.atmost(terms, target, vpool=pool, encoding=EncType.seqcounter).clauses
    )
    if target == 1:
        clauses.append(list(terms))
    elif target == 2:
        add_atleast_two_linear(clauses, terms, pool, key)
    else:
        raise ValueError(target)
    return pool.top - before


def add_bp_and_redundancies(clauses, labels, edge, pool, CardEnc, EncType):
    counts = {
        "bp_equalities": 0,
        "outer_degree_equalities": 0,
        "exact_symbol_degree_equalities": 0,
        "disjoint_symbol_degree_equalities": 0,
        "group_degree_equalities": 0,
        "fibre_diagonal_exclusion_clauses": 0,
    }

    # Original BP equations.
    for u, label in enumerate(labels):
        own = set(label)
        for symbol in range(14):
            lits = [
                edge(u, v)
                for v, other in enumerate(labels)
                if u != v and symbol in other
            ]
            target = 1 if symbol in own or (symbol ^ 1) in own else 2
            clauses.extend(
                CardEnc.equals(lits, target, vpool=pool, encoding=EncType.seqcounter).clauses
            )
            counts["bp_equalities"] += 1

    # Per-vertex degree and exact-symbol split.  These are consequences of BP,
    # but exposing them directly makes failed partial neighbourhoods visible.
    for u, label in enumerate(labels):
        all_lits = [edge(u, v) for v in range(84) if v != u]
        shared = [
            edge(u, v)
            for v, other in enumerate(labels)
            if u != v and set(label).intersection(other)
        ]
        disjoint = [
            edge(u, v)
            for v, other in enumerate(labels)
            if u != v and not set(label).intersection(other)
        ]
        assert len(shared) == 22 and len(disjoint) == 61
        clauses.extend(
            CardEnc.equals(all_lits, 12, vpool=pool, encoding=EncType.seqcounter).clauses
        )
        clauses.extend(
            CardEnc.equals(shared, 2, vpool=pool, encoding=EncType.seqcounter).clauses
        )
        clauses.extend(
            CardEnc.equals(disjoint, 10, vpool=pool, encoding=EncType.seqcounter).clauses
        )
        counts["outer_degree_equalities"] += 1
        counts["exact_symbol_degree_equalities"] += 1
        counts["disjoint_symbol_degree_equalities"] += 1

        support_groups = {symbol // 2 for symbol in label}
        for group in range(7):
            lits = [
                edge(u, v)
                for v, other in enumerate(labels)
                if u != v and any(symbol // 2 == group for symbol in other)
            ]
            assert len(lits) in (23, 24)
            target = 2 if group in support_groups else 4
            clauses.extend(
                CardEnc.equals(lits, target, vpool=pool, encoding=EncType.seqcounter).clauses
            )
            counts["group_degree_equalities"] += 1

    # Explicit local fibre rule.  For fibre (a,b), the complementary diagonals
    # are (00,11) and (01,10); a selected diagonal isolates both endpoints
    # from the four square sides.
    index = {label: i for i, label in enumerate(labels)}
    for ga, gb in itertools.combinations(range(7), 2):
        a0, a1, b0, b1 = 2 * ga, 2 * ga + 1, 2 * gb, 2 * gb + 1
        p00 = index[(a0, b0)]
        p01 = index[(a0, b1)]
        p10 = index[(a1, b0)]
        p11 = index[(a1, b1)]
        d1, d2 = edge(p00, p11), edge(p01, p10)
        sides = (
            edge(p00, p01),
            edge(p00, p10),
            edge(p11, p01),
            edge(p11, p10),
        )
        for diagonal in (d1, d2):
            for side in sides:
                clauses.append([-diagonal, -side])
                counts["fibre_diagonal_exclusion_clauses"] += 1
    return counts


def build_cnf() -> dict[str, object]:
    from pysat.card import CardEnc, EncType
    from pysat.formula import IDPool

    labels, _index, variables, edge = coordinates()
    pool = IDPool(start_from=len(variables) + 1)
    clauses: list[list[int]] = []
    counts = add_bp_and_redundancies(
        clauses, labels, edge, pool, CardEnc, EncType
    )
    after_linear = len(clauses)

    products = 0
    pair_lower_aux = 0
    target_histogram = {1: 0, 2: 0}
    for u, v in itertools.combinations(range(84), 2):
        terms: list[int] = []
        for w in range(84):
            if w == u or w == v:
                continue
            a, b = edge(u, w), edge(v, w)
            z = pool.id(("and", u, v, w))
            # z <-> (a & b), not merely the forward implication.
            clauses.extend(([-a, -b, z], [a, -z], [b, -z]))
            terms.append(z)
            products += 1
        terms.append(edge(u, v))
        target = 2 - len(set(labels[u]).intersection(labels[v]))
        assert target in (1, 2)
        target_histogram[target] += 1
        before = pool.top
        add_equals_small(clauses, terms, target, pool, CardEnc, EncType, (u, v))
        # Exclude the at-most counter's auxiliary variables from this diagnostic
        # only approximately; the exact total is still captured by pool.top.
        pair_lower_aux += max(0, pool.top - before)

    meta: dict[str, object] = {
        "model": "propagation-strong exact unrestricted rooted SAT v2",
        "edge_variables": len(variables),
        "common_product_variables": products,
        "target_histogram": target_histogram,
        "linear_redundancy_counts": counts,
        "clauses_after_linear_constraints": after_linear,
        "pair_counter_auxiliary_variables": pair_lower_aux,
        "variables": pool.top,
        "clauses": len(clauses),
        "logical_exactness": "full AND equivalences plus explicit per-pair equality",
    }
    with CNF_PATH.open("w", encoding="ascii", newline="\n") as handle:
        handle.write(f"p cnf {pool.top} {len(clauses)}\n")
        for clause in clauses:
            handle.write(" ".join(map(str, clause)) + " 0\n")
    meta["cnf_sha256"] = hashlib.sha256(CNF_PATH.read_bytes()).hexdigest().upper()
    BUILD_PATH.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    return meta


def get_branch_specs():
    from scratch_general_triangle_portfolio import branch_specs

    specs, coverage = branch_specs()
    prior_path = Path("scratch_general_triangle_portfolio.json")
    prior = json.loads(prior_path.read_text(encoding="utf-8"))
    prior_status = {row["branch"]: row["status"] for row in prior["records"]}
    live = [spec for spec in specs if prior_status.get(spec["branch"]) == "UNKNOWN"]
    eliminated = [spec for spec in specs if prior_status.get(spec["branch"]) == "UNSAT"]
    assert len(specs) == 26 and len(live) == 17 and len(eliminated) == 9
    return specs, live, eliminated, coverage


def budget_worker(spec, conflict_budget: int, out_queue) -> None:
    from pysat.formula import CNF
    from pysat.solvers import Solver

    started = time.monotonic()
    formula = CNF(from_file=str(CNF_PATH.resolve()))
    loaded = time.monotonic()
    with Solver(name="cadical195", bootstrap_with=formula.clauses) as solver:
        solver.conf_budget(conflict_budget)
        answer = solver.solve_limited(assumptions=spec["assumptions"])
        model = solver.get_model() if answer is True else None
        stats = solver.accum_stats()
    out_queue.put(
        {
            "branch": spec["branch"],
            "status": "SAT" if answer is True else "UNSAT" if answer is False else "UNKNOWN",
            "conflict_budget": conflict_budget,
            "load_seconds": round(loaded - started, 3),
            "solve_seconds": round(time.monotonic() - loaded, 3),
            "stats": stats,
            "positive_edge_variables": [
                lit for lit in model if 0 < lit <= 3486
            ] if model else [],
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


def run_specs(specs, conflict_budget: int, max_parallel: int, result_path: Path):
    context = mp.get_context("spawn")
    records: dict[str, dict[str, object]] = {}
    verified = None
    for offset in range(0, len(specs), max_parallel):
        batch = specs[offset : offset + max_parallel]
        out_queue = context.Queue()
        processes = {}
        for spec in batch:
            process = context.Process(
                target=budget_worker,
                args=(spec, conflict_budget, out_queue),
                name=f"sat-v2-{spec['branch']}",
            )
            process.start()
            processes[spec["branch"]] = process
        for _ in batch:
            try:
                record = out_queue.get(timeout=3600)
            except queue.Empty:
                break
            records[record["branch"]] = record
            if record["status"] == "SAT":
                checked = verify(set(record["positive_edge_variables"]))
                record["verification"] = {
                    key: value for key, value in checked.items() if key != "edges"
                }
                if checked["ok"]:
                    verified = checked
        for name, process in processes.items():
            process.join(10)
            if process.is_alive():
                process.terminate()
                process.join(10)
            records.setdefault(
                name,
                {"branch": name, "status": "WORKER_FAILURE", "exit_code": process.exitcode},
            )
        if verified is not None:
            break

    ordered = [records.get(spec["branch"], {"branch": spec["branch"], "status": "NOT_RUN_AFTER_SAT"}) for spec in specs]
    summary = {
        "model": "propagation-strong exact unrestricted rooted SAT v2",
        "solver": "CaDiCaL 1.9.5 via PySAT",
        "conflict_budget_per_branch": conflict_budget,
        "max_parallel": max_parallel,
        "branch_count": len(specs),
        "status": (
            "SAT" if verified is not None
            else "UNSAT" if all(row["status"] == "UNSAT" for row in ordered)
            else "UNKNOWN"
        ),
        "records": ordered,
    }
    result_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    if verified is not None:
        Path(f"{PREFIX}_solution.json").write_text(
            json.dumps(verified, indent=2) + "\n", encoding="utf-8"
        )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--benchmark-conflicts", type=int, default=0)
    parser.add_argument("--portfolio-conflicts", type=int, default=0)
    parser.add_argument("--max-parallel", type=int, default=2)
    args = parser.parse_args()
    if args.build:
        started = time.monotonic()
        meta = build_cnf()
        meta["build_seconds"] = round(time.monotonic() - started, 3)
        BUILD_PATH.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(meta, sort_keys=True), flush=True)
    if args.benchmark_conflicts > 0:
        _all, live, _eliminated, _coverage = get_branch_specs()
        # Cover distinct first-level fibre types and distinct triangle-label shapes.
        wanted = {
            "a0__w1_5",
            "a0__w8_10",
            "a1_complement__w1_3",
            "a1_cross__w1_5",
            "a2_crosses__w5_7",
        }
        bench = [spec for spec in live if spec["branch"] in wanted]
        result = run_specs(bench, args.benchmark_conflicts, args.max_parallel, BENCH_PATH)
        print(json.dumps({"benchmark_status": result["status"]}), flush=True)
    if args.portfolio_conflicts > 0:
        _all, live, _eliminated, _coverage = get_branch_specs()
        result = run_specs(live, args.portfolio_conflicts, args.max_parallel, PORTFOLIO_PATH)
        print(json.dumps({"portfolio_status": result["status"]}), flush=True)
    if not args.build and args.benchmark_conflicts <= 0 and args.portfolio_conflicts <= 0:
        parser.error("select --build and/or a solve mode")


if __name__ == "__main__":
    mp.freeze_support()
    main()
