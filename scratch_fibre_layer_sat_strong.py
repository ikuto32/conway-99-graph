"""Exact SAT model for BP plus the 126 same-support outer-pair equations.

Only this intermediate layer is asserted.  A disjoint-support edge is fixed
without loss of generality, and the four possible incident same-fibre
patterns (plus one deliberately retained propagation-impossible pattern)
form exhaustive safe branches.  Every wedge helper is a full Tseitin AND.

Any SAT model is expanded to the fixed 99-vertex scaffold and independently
checked for BP, degree, and all 126 requested pair equations.  It is only a
partial-layer seed, so this script never writes ``submission.txt``.
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


PREFIX = "scratch_fibre_layer_sat_strong"
CNF_PATH = Path(f"{PREFIX}.cnf")
BUILD_PATH = Path(f"{PREFIX}_build.json")
PORTFOLIO_PATH = Path(f"{PREFIX}_portfolio.json")
SOLUTION_PATH = Path(f"{PREFIX}_solution.json")
BRANCHES = ("a0", "a1_complement", "a1_cross", "a2_crosses", "a2_mixed")


def coordinates():
    labels = [
        pair
        for pair in itertools.combinations(range(14), 2)
        if pair[0] // 2 != pair[1] // 2
    ]
    index = {label: i for i, label in enumerate(labels)}
    variables = {pair: number for number, pair in enumerate(itertools.combinations(range(84), 2), 1)}

    def edge(u, v):
        assert u != v
        return variables[(u, v) if u < v else (v, u)]

    assert len(labels) == 84 and len(index) == 84 and len(variables) == 3486
    return labels, index, variables, edge


def branch_units(index, edge):
    # BP alone guarantees every outer vertex has at least eight neighbours on
    # disjoint supports.  The scaffold group is transitive on ordered pairs of
    # labels with four distinct support groups, so fixing this edge is WLOG.
    u = index[(0, 2)]
    fixed = edge(u, index[(4, 6)])
    x = edge(u, index[(0, 3)])
    y = edge(u, index[(1, 2)])
    diagonal = edge(u, index[(1, 3)])
    return {
        "a0": [fixed, -x, -y, -diagonal],
        "a1_complement": [fixed, -x, -y, diagonal],
        "a1_cross": [fixed, x, -y, -diagonal],
        "a2_crosses": [fixed, x, y, -diagonal],
        # Retained to let the solver independently expose its BP contradiction.
        "a2_mixed": [fixed, x, -y, diagonal],
    }


def add_bp_exact(clauses, lits, target):
    """Direct exact-1/exact-2 CNF for BP rows of length at most 12."""
    assert len(lits) in (11, 12) and len(set(lits)) == len(lits)
    if target == 1:
        clauses.append(list(lits))
        clauses.extend([-a, -b] for a, b in itertools.combinations(lits, 2))
    elif target == 2:
        # At least two: deleting any single literal still leaves a true one.
        for omitted in range(len(lits)):
            clauses.append(lits[:omitted] + lits[omitted + 1 :])
        clauses.extend([-a, -b, -c] for a, b, c in itertools.combinations(lits, 3))
    else:
        raise ValueError(target)


def add_layer_exact(clauses, terms, target, pool, CardEnc, EncType):
    """Exact cardinality 1/2 for 83 terms, with a compact sequential upper bound."""
    clauses.extend(CardEnc.atmost(terms, target, vpool=pool, encoding=EncType.seqcounter).clauses)
    if target == 1:
        clauses.append(list(terms))
    elif target == 2:
        # At least two iff, for every possible omitted term, one of the others
        # is true.  This uses no auxiliary variables and only 83 long clauses.
        for omitted in range(len(terms)):
            clauses.append(terms[:omitted] + terms[omitted + 1 :])
    else:
        raise ValueError(target)


def build():
    from pysat.card import CardEnc, EncType
    from pysat.formula import IDPool

    labels, index, variables, edge = coordinates()
    label_sets = [set(label) for label in labels]
    pool = IDPool(start_from=3487)
    clauses = []

    bp_histogram = {1: 0, 2: 0}
    for u, label in enumerate(labels):
        own_groups = {symbol // 2 for symbol in label}
        for symbol in range(14):
            lits = [edge(u, v) for v, other in enumerate(labels) if u != v and symbol in other]
            target = 1 if symbol // 2 in own_groups else 2
            add_bp_exact(clauses, lits, target)
            bp_histogram[target] += 1

    products = 0
    layer_histogram = {1: 0, 2: 0}
    fibre_pairs = []
    for support in itertools.combinations(range(7), 2):
        fibre = [
            u for u, label in enumerate(labels)
            if tuple(sorted(symbol // 2 for symbol in label)) == support
        ]
        assert len(fibre) == 4
        for u, v in itertools.combinations(fibre, 2):
            terms = [edge(u, v)]
            for w in range(84):
                if w in (u, v):
                    continue
                a, b = edge(u, w), edge(v, w)
                z = pool.id(("and", u, v, w))
                clauses.extend(([-a, -b, z], [a, -z], [b, -z]))
                terms.append(z)
                products += 1
            target = 2 - len(label_sets[u].intersection(label_sets[v]))
            add_layer_exact(clauses, terms, target, pool, CardEnc, EncType)
            layer_histogram[target] += 1
            fibre_pairs.append((u, v, target))

    units = branch_units(index, edge)
    meta = {
        "model": "BP plus all 126 exact same-support outer-pair equations",
        "edge_variables": len(variables),
        "bp_equations": sum(bp_histogram.values()),
        "bp_target_histogram": bp_histogram,
        "same_support_pair_equations": len(fibre_pairs),
        "same_support_target_histogram": layer_histogram,
        "full_and_variables": products,
        "variables": pool.top,
        "clauses": len(clauses),
        "fixed_disjoint_edge_symmetry_is_safe": True,
        "branch_units": units,
        "branches_exhaustive": True,
    }
    assert products == 126 * 82
    assert layer_histogram == {1: 84, 2: 42}
    with CNF_PATH.open("w", encoding="ascii", newline="\n") as handle:
        handle.write(f"p cnf {pool.top} {len(clauses)}\n")
        for clause in clauses:
            handle.write(" ".join(map(str, clause)) + " 0\n")
    meta["cnf_sha256"] = hashlib.sha256(CNF_PATH.read_bytes()).hexdigest().upper()
    BUILD_PATH.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    return meta


def worker(branch, cnf_path, assumptions, out_queue):
    from pysat.formula import CNF
    from pysat.solvers import Solver

    started = time.monotonic()
    formula = CNF(from_file=cnf_path)
    loaded = time.monotonic()
    with Solver(name="cadical300", bootstrap_with=formula.clauses) as solver:
        answer = solver.solve(assumptions=assumptions)
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


def verify_layer(positive):
    from scratch_bp_seed import expand_and_check

    labels, _index, variables, _edge = coordinates()
    expanded = expand_and_check(labels, variables, positive)
    adjacency = [set() for _ in range(99)]
    for u, v in expanded["edges"]:
        u -= 1
        v -= 1
        adjacency[u].add(v)
        adjacency[v].add(u)
    bad = []
    for support in itertools.combinations(range(7), 2):
        fibre = [
            u for u, label in enumerate(labels)
            if tuple(sorted(symbol // 2 for symbol in label)) == support
        ]
        for u, v in itertools.combinations(fibre, 2):
            gu, gv = 15 + u, 15 + v
            value = len(adjacency[gu].intersection(adjacency[gv])) + int(gv in adjacency[gu])
            if value != 2:
                bad.append((u, v, value))
    result = {
        "bp_verified_by_inner_outer_bad_pairs": expanded["inner_outer_bad_pairs"] == 0,
        "all_degrees_14": expanded["degree_histogram"] == {"14": 99},
        "edge_count": expanded["edge_count"],
        "same_support_pairs_checked": 126,
        "same_support_bad_pairs": len(bad),
        "full_srg_energy_not_asserted": expanded["energy"],
        "full_srg_bad_pairs_not_asserted": expanded["bad_pairs"],
        "ok": expanded["inner_outer_bad_pairs"] == 0 and not bad,
        "edges": expanded["edges"],
    }
    return result


def run_portfolio(seconds, max_parallel):
    meta = json.loads(BUILD_PATH.read_text(encoding="utf-8"))
    context = mp.get_context("spawn")
    records = {}
    verified = None
    specs = [(branch, meta["branch_units"][branch]) for branch in BRANCHES]
    for offset in range(0, len(specs), max_parallel):
        batch = specs[offset : offset + max_parallel]
        out_queue = context.Queue()
        processes = {}
        for branch, assumptions in batch:
            process = context.Process(
                target=worker,
                args=(branch, str(CNF_PATH.resolve()), assumptions, out_queue),
            )
            process.start()
            processes[branch] = process
        deadline = time.monotonic() + seconds
        while not all(branch in records for branch, _ in batch):
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            try:
                row = out_queue.get(timeout=min(1.0, remaining))
            except queue.Empty:
                continue
            records[row["branch"]] = row
            if row["status"] == "SAT":
                checked = verify_layer(set(row["positive_edge_variables"]))
                row["verification"] = {key: value for key, value in checked.items() if key != "edges"}
                if checked["ok"] and verified is None:
                    verified = checked
                    SOLUTION_PATH.write_text(json.dumps(checked, indent=2) + "\n", encoding="utf-8")
        for branch, process in processes.items():
            if process.is_alive():
                process.terminate()
                process.join(10)
            else:
                process.join()
            records.setdefault(branch, {"branch": branch, "status": "UNKNOWN", "wall_limit_seconds": seconds})
        if verified is not None:
            break
    for branch in BRANCHES:
        records.setdefault(branch, {"branch": branch, "status": "NOT_RUN_AFTER_VERIFIED_SAT"})
    ordered = [records[branch] for branch in BRANCHES]
    result = {
        "model": meta["model"],
        "solver": "CaDiCaL 3.0 via PySAT",
        "wall_limit_seconds_per_batch": seconds,
        "max_parallel": max_parallel,
        "branches_exhaustive": True,
        "status": "SAT" if verified is not None else "UNSAT" if all(row["status"] == "UNSAT" for row in ordered) else "UNKNOWN",
        "records": ordered,
    }
    PORTFOLIO_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--solve-seconds", type=float, default=0)
    parser.add_argument("--max-parallel", type=int, default=4)
    args = parser.parse_args()
    if args.build:
        started = time.monotonic()
        meta = build()
        meta["build_seconds"] = round(time.monotonic() - started, 3)
        BUILD_PATH.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(meta, sort_keys=True), flush=True)
    if args.solve_seconds > 0:
        result = run_portfolio(args.solve_seconds, args.max_parallel)
        print(json.dumps({"status": result["status"], "records": [(r["branch"], r["status"]) for r in result["records"]]}), flush=True)
    if not args.build and args.solve_seconds <= 0:
        parser.error("select --build and/or --solve-seconds")


if __name__ == "__main__":
    mp.freeze_support()
    main()
