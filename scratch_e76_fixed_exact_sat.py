"""Independent fixed-local exact SAT portfolio for 311 E0=76 representatives.

This generalizes the independently written E0=77 compact CNF.  Every branch
is rebuilt from its explicit local edge list; no shared/incremental E76 SAT
implementation is read or imported.  All disjoint-support edges remain
variables, all BP equations and outer-pair equations are exact, and every SAT
answer is expanded and independently checked on 99 vertices.
"""

from __future__ import annotations

import argparse
from collections import Counter
import itertools
import json
import multiprocessing as mp
import queue
import time
from pathlib import Path

from scratch_general_exact_sat import coordinates, verify


SOURCE = Path("scratch_e76_independent_local.json")
CATALOG = Path("scratch_e76_fixed_exact_catalog.json")
CHECKPOINT = Path("scratch_e76_fixed_exact_checkpoint.json")
PORTFOLIO = Path("scratch_e76_fixed_exact_portfolio.json")


def branch_catalog():
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    assert source["ok"] and source["local_graph_orbits"] == 311
    branches = []
    for row_index, row in enumerate(source["rows"]):
        for representative in row["representatives"]:
            branches.append({
                "branch_index": len(branches),
                "source_row_index": row_index,
                "partition": row["partition"],
                "compression_orbit_index": row["compression_orbit_index"],
                "support_orbit_size": row["support_orbit_size"],
                "exceptional_supports": row["exceptional_supports"],
                "local_representative_index": representative["representative_index"],
                "local_orbit_size": representative["local_orbit_size"],
                "local_edge_count": representative["local_edge_count"],
                "local_edges": representative["edges_by_symbol_label"],
            })
    assert len(branches) == 311
    assert sum(branch["local_orbit_size"] for branch in branches) == 68864
    return branches


def write_catalog(branches):
    data = {
        "model": "311 exhaustive independent E0=76 fixed-local branch catalog",
        "source": str(SOURCE),
        "branch_count": len(branches),
        "covered_labelled_local_graphs": sum(row["local_orbit_size"] for row in branches),
        "branches": [
            {key: value for key, value in row.items() if key != "local_edges"}
            for row in branches
        ],
    }
    CATALOG.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def build_cnf(branch_index):
    from pysat.card import CardEnc, EncType
    from pysat.formula import IDPool

    branch = branch_catalog()[branch_index]
    labels, label_index, full_variables, _full_edge = coordinates()
    supports = tuple(tuple(symbol // 2 for symbol in label) for label in labels)
    signs = tuple({symbol // 2: symbol % 2 for symbol in label} for label in labels)
    fibres = {
        support: tuple(u for u, value in enumerate(supports) if value == support)
        for support in itertools.combinations(range(7), 2)
    }
    deficits = {
        tuple(item["support"]): item["deficit"]
        for item in branch["exceptional_supports"]
    }
    exceptional = frozenset(deficits)
    high = frozenset(set(fibres) - set(exceptional))
    local_graph_labels = frozenset(
        tuple(sorted((tuple(raw[0]), tuple(raw[1]))))
        for raw in branch["local_edges"]
    )
    local_graph = frozenset(
        tuple(sorted((label_index[u], label_index[v])))
        for u, v in local_graph_labels
    )
    assert len(local_graph) == branch["local_edge_count"]

    pool = IDPool(start_from=1)
    edge_variables = {}
    disjoint_blocks = []
    for A, B in itertools.combinations(fibres, 2):
        if not set(A).isdisjoint(B):
            continue
        disjoint_blocks.append((A, B))
        for u in fibres[A]:
            for v in fibres[B]:
                key = tuple(sorted((u, v)))
                edge_variables[key] = pool.id(("edge",) + key)
    assert len(disjoint_blocks) == 105 and len(edge_variables) == 1680

    def edge(u, v):
        if u == v:
            return False
        key = tuple(sorted((u, v)))
        if key in edge_variables:
            return edge_variables[key]
        A, B = supports[u], supports[v]
        if A == B:
            if A in exceptional:
                return key in local_graph
            return sum(signs[u][group] != signs[v][group] for group in A) == 1
        assert set(A) & set(B)
        if A in exceptional and B in exceptional:
            return key in local_graph
        return False

    clauses = []

    def exactly_one(literals):
        clauses.append(list(literals))
        clauses.extend([-a, -b] for a, b in itertools.combinations(literals, 2))

    block_types = {"high_high": 0, "high_low": 0, "low_low": 0}
    block_equalities = 0
    for A, B in disjoint_blocks:
        if A in high and B in high:
            block_types["high_high"] += 1
        elif A in high or B in high:
            block_types["high_low"] += 1
        else:
            block_types["low_low"] += 1
        if A in high:
            for v in fibres[B]:
                exactly_one([edge(u, v) for u in fibres[A]])
                block_equalities += 1
        if B in high:
            for u in fibres[A]:
                exactly_one([edge(u, v) for v in fibres[B]])
                block_equalities += 1

    cardinality_equalities = 0

    def add_exact(expressions, wanted):
        nonlocal cardinality_equalities
        fixed = sum(value is True for value in expressions)
        literals = [value for value in expressions if type(value) is int]
        target = wanted - fixed
        cardinality_equalities += 1
        if target < 0 or target > len(literals):
            clauses.append([])
        elif not literals:
            if target:
                clauses.append([])
        else:
            clauses.extend(CardEnc.equals(
                literals,
                target,
                vpool=pool,
                encoding=EncType.seqcounter,
            ).clauses)

    for u, label in enumerate(labels):
        own = set(label)
        for symbol in range(14):
            add_exact(
                [
                    edge(u, v)
                    for v, other in enumerate(labels)
                    if u != v and symbol in other
                ],
                1 if symbol in own or (symbol ^ 1) in own else 2,
            )

    products = direct_terms = constant_terms = 0
    for u, v in itertools.combinations(range(84), 2):
        expressions = [edge(u, v)]
        for w in range(84):
            if w in (u, v):
                continue
            a, b = edge(u, w), edge(v, w)
            if a is False or b is False:
                continue
            if a is True and b is True:
                expressions.append(True)
                constant_terms += 1
            elif a is True:
                expressions.append(b)
                direct_terms += 1
            elif b is True:
                expressions.append(a)
                direct_terms += 1
            elif a == b:
                expressions.append(a)
                direct_terms += 1
            else:
                product = pool.id(("and", u, v, w))
                clauses.extend(([-a, -b, product], [a, -product], [b, -product]))
                expressions.append(product)
                products += 1
        add_exact(expressions, 2 - len(set(labels[u]) & set(labels[v])))

    internal = overlap = 0
    for u, v in local_graph:
        A, B = supports[u], supports[v]
        if A == B:
            internal += 1
        else:
            assert set(A) & set(B)
            overlap += 1
    assert internal == sum(4 - deficit for deficit in deficits.values())
    assert overlap == 16
    assert products == 65520
    assert cardinality_equalities == 1176 + 3486

    meta = {
        "model": "independent fixed-local exact E0=76 CNF",
        "branch_index": branch_index,
        "partition": branch["partition"],
        "compression_orbit_index": branch["compression_orbit_index"],
        "local_representative_index": branch["local_representative_index"],
        "local_orbit_size": branch["local_orbit_size"],
        "exceptional_fibres": len(exceptional),
        "ordinary_c4_fibres": len(high),
        "fixed_local_internal_edges": internal,
        "fixed_local_overlap_edges": overlap,
        "edge_variables": len(edge_variables),
        "product_variables": products,
        "direct_product_terms": direct_terms,
        "constant_product_terms": constant_terms,
        "disjoint_blocks": len(disjoint_blocks),
        "block_types": block_types,
        "ordinary_c4_block_equalities": block_equalities,
        "BP_equalities": 1176,
        "outer_pair_equalities": 3486,
        "cardinality_equalities": cardinality_equalities,
        "variables": pool.top,
        "clauses": len(clauses),
        "redundant_support_aggregate_rows": 0,
    }
    return clauses, edge, full_variables, meta


def worker(branch_index, conflict_budget, out_queue):
    from pysat.solvers import Solver

    started = time.monotonic()
    clauses, edge, full_variables, meta = build_cnf(branch_index)
    built = time.monotonic()
    with Solver(name="cadical195", bootstrap_with=clauses) as solver:
        if conflict_budget > 0:
            solver.conf_budget(conflict_budget)
            answer = solver.solve_limited(expect_interrupt=True)
        else:
            answer = solver.solve()
        model = solver.get_model() if answer is True else None
        stats = solver.accum_stats()
    status = "SAT" if answer is True else "UNSAT" if answer is False else "UNKNOWN"
    record = {
        "branch_index": branch_index,
        "status": status,
        "termination": "solver_answer" if answer is not None else "conflict_budget",
        "conflict_budget": conflict_budget,
        "build_seconds": round(built - started, 3),
        "solve_seconds": round(time.monotonic() - built, 3),
        "meta": meta,
        "stats": stats,
        "formal_proof_certificate": None,
    }
    if model:
        positive = {literal for literal in model if literal > 0}
        selected = set()
        for pair, identifier in full_variables.items():
            value = edge(*pair)
            if value is True or (type(value) is int and value in positive):
                selected.add(identifier)
        checked = verify(selected)
        record["verification"] = {key: value for key, value in checked.items() if key != "edges"}
        if checked["ok"]:
            record["positive_full_edge_variables"] = sorted(selected)
            Path(f"scratch_e76_fixed_exact_solution_branch{branch_index:03d}.json").write_text(
                json.dumps(checked, indent=2) + "\n", encoding="utf-8"
            )
        else:
            record["status"] = "SAT_INVALID"
    out_queue.put(record)


def load_checkpoint():
    if CHECKPOINT.exists():
        data = json.loads(CHECKPOINT.read_text(encoding="utf-8"))
        assert data["catalog_size"] == 311
        return data
    return {
        "model": "per-branch checkpoint for independent E0=76 fixed-local SAT",
        "catalog_size": 311,
        "attempts": {},
    }


def save_checkpoint(data):
    temporary = CHECKPOINT.with_suffix(".tmp")
    temporary.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    temporary.replace(CHECKPOINT)


def add_checkpoint(data, record):
    key = str(record["branch_index"])
    data["attempts"].setdefault(key, []).append(record)
    data["last_update_unix"] = time.time()
    save_checkpoint(data)


def run_portfolio(start, end, conflict_budget, wall_seconds, max_parallel, only_unknown):
    branches = branch_catalog()
    write_catalog(branches)
    checkpoint = load_checkpoint()
    requested = list(range(start, min(end, len(branches))))
    if only_unknown:
        requested = [
            index for index in requested
            if not checkpoint["attempts"].get(str(index))
            or checkpoint["attempts"][str(index)][-1]["status"] == "UNKNOWN"
        ]
    invocation_records = {}
    context = mp.get_context("spawn")
    for offset in range(0, len(requested), max_parallel):
        batch = requested[offset:offset + max_parallel]
        out_queue = context.Queue()
        processes = {}
        for branch_index in batch:
            process = context.Process(
                target=worker,
                args=(branch_index, conflict_budget, out_queue),
                name=f"e76-fixed-{branch_index}",
            )
            process.start()
            processes[branch_index] = process
        deadline = time.monotonic() + wall_seconds
        pending = set(batch)
        while pending:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            try:
                record = out_queue.get(timeout=min(1.0, remaining))
            except queue.Empty:
                continue
            index = record["branch_index"]
            if index not in pending:
                continue
            pending.remove(index)
            invocation_records[index] = record
            add_checkpoint(checkpoint, record)
        for branch_index, process in processes.items():
            if process.is_alive():
                process.terminate()
                process.join(10)
            else:
                process.join()
            if branch_index in pending:
                record = {
                    "branch_index": branch_index,
                    "status": "UNKNOWN",
                    "termination": "wall_limit",
                    "conflict_budget": conflict_budget,
                    "wall_limit_seconds": wall_seconds,
                    "exit_code_after_termination": process.exitcode,
                    "formal_proof_certificate": None,
                }
                invocation_records[branch_index] = record
                add_checkpoint(checkpoint, record)
        counts = Counter(record["status"] for record in invocation_records.values())
        print(json.dumps({
            "completed_through_batch": batch,
            "invocation_completed": len(invocation_records),
            "counts": dict(counts),
        }), flush=True)

    ordered = [invocation_records[index] for index in sorted(invocation_records)]
    latest = {
        int(index): attempts[-1]
        for index, attempts in checkpoint["attempts"].items()
        if attempts
    }
    result = {
        "model": "independent fixed-local exact SAT portfolio for E0=76",
        "solver": "CaDiCaL 1.9.5 via PySAT",
        "catalog": str(CATALOG),
        "checkpoint": str(CHECKPOINT),
        "requested_range": [start, end],
        "conflict_budget_per_branch": conflict_budget,
        "wall_limit_seconds_per_parallel_batch": wall_seconds,
        "max_parallel": max_parallel,
        "only_unknown": only_unknown,
        "invocation_count": len(ordered),
        "invocation_status_counts": dict(Counter(row["status"] for row in ordered)),
        "cumulative_latest_count": len(latest),
        "cumulative_latest_status_counts": dict(Counter(row["status"] for row in latest.values())),
        "all_311_terminal": len(latest) == 311 and all(
            row["status"] in ("SAT", "UNSAT") for row in latest.values()
        ),
        "proof_status": "no independently checked UNSAT certificates",
        "records": ordered,
    }
    PORTFOLIO.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", type=int, choices=range(311))
    parser.add_argument("--build-only", action="store_true")
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--end", type=int, default=311)
    parser.add_argument("--conflicts", type=int, default=20000)
    parser.add_argument("--wall-seconds", type=float, default=12)
    parser.add_argument("--max-parallel", type=int, default=4)
    parser.add_argument("--only-unknown", action="store_true")
    args = parser.parse_args()
    if args.branch is not None:
        clauses, _edge, _full, meta = build_cnf(args.branch)
        print(json.dumps(meta), flush=True)
        if not args.build_only:
            out_queue = mp.get_context("spawn").Queue()
            worker(args.branch, args.conflicts, out_queue)
            print(json.dumps(out_queue.get()), flush=True)
        return
    result = run_portfolio(
        args.start,
        args.end,
        args.conflicts,
        args.wall_seconds,
        min(4, max(1, args.max_parallel)),
        args.only_unknown,
    )
    print(json.dumps({
        "invocation": result["invocation_status_counts"],
        "cumulative": result["cumulative_latest_status_counts"],
        "all_terminal": result["all_311_terminal"],
    }), flush=True)


if __name__ == "__main__":
    mp.freeze_support()
    main()
