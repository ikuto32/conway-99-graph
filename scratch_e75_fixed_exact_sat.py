"""Independent fixed-local exact SAT portfolio for 352 E0=75 representatives.

The only E75 inputs are the explicit representative edge lists and their
independent reconstruction audit.  Every branch gets a fresh CNF.  This file
does not read or import the shared incremental E75 SAT implementation.
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


SOURCE = Path("scratch_general_e75_local_graph_reps.json")
SOURCE_AUDIT = Path("scratch_general_e75_reps_check.json")
CATALOG = Path("scratch_e75_fixed_exact_catalog.json")
CHECKPOINT = Path("scratch_e75_fixed_exact_checkpoint.json")
PORTFOLIO = Path("scratch_e75_fixed_exact_portfolio.json")
BRANCH_COUNT = 352
RAW_LOCAL_GRAPHS = 110592


def branch_catalog():
    audit = json.loads(SOURCE_AUDIT.read_text(encoding="utf-8"))
    assert audit["status"] == "VERIFIED"
    assert audit["support_rows_checked"] == 6
    assert audit["orbits_checked"] == BRANCH_COUNT
    assert audit["raw_graphs_checked"] == RAW_LOCAL_GRAPHS

    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    assert source["status"] == "COMPLETE"
    assert source["local_graph_orbits"] == BRANCH_COUNT
    assert source["raw_graphs"] == RAW_LOCAL_GRAPHS
    assert len(source["support_rows"]) == 6
    branches = []
    for row_index, row in enumerate(source["support_rows"]):
        for representative_index, representative in enumerate(row["representatives"]):
            branches.append({
                "branch_index": len(branches),
                "source_row_index": row_index,
                "partition": row["partition"],
                "compression_orbit_index": row["compression_orbit_index"],
                "exceptional_supports": row["exceptional_supports"],
                "local_representative_index": representative_index,
                "local_orbit_size": representative["orbit_size"],
                "local_edge_count": len(representative["edges"]),
                "local_mask_hex": representative["mask_hex"],
                "local_edges": representative["edges"],
            })
    assert len(branches) == BRANCH_COUNT
    assert sum(branch["local_orbit_size"] for branch in branches) == RAW_LOCAL_GRAPHS
    return branches


def write_catalog(branches):
    row_counts = Counter(branch["source_row_index"] for branch in branches)
    data = {
        "model": "352 exhaustive independent E0=75 fixed-local branch catalog",
        "source": str(SOURCE),
        "source_audit": str(SOURCE_AUDIT),
        "source_audit_status": "VERIFIED",
        "branch_count": len(branches),
        "covered_labelled_local_graphs": sum(
            row["local_orbit_size"] for row in branches
        ),
        "branches_per_source_row": {
            str(index): row_counts[index] for index in range(6)
        },
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
    assert sum(deficits.values()) == 9
    assert len(exceptional) in (8, 9)

    local_graph_labels = frozenset(
        tuple(sorted((tuple(raw[0]), tuple(raw[1]))))
        for raw in branch["local_edges"]
    )
    assert len(local_graph_labels) == branch["local_edge_count"]
    local_graph = frozenset(
        tuple(sorted((label_index[u], label_index[v])))
        for u, v in local_graph_labels
    )
    assert len(local_graph) == branch["local_edge_count"]

    local_internal_by_support = Counter()
    local_overlap = 0
    for u, v in local_graph:
        A, B = supports[u], supports[v]
        assert A in exceptional and B in exceptional
        if A == B:
            local_internal_by_support[A] += 1
        else:
            assert set(A) & set(B)
            local_overlap += 1
    assert local_overlap == 18
    for support, deficit in deficits.items():
        assert local_internal_by_support[support] == 4 - deficit

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
    assert len(disjoint_blocks) == 105
    assert len(edge_variables) == 1680

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
            return sum(
                signs[u][group] != signs[v][group] for group in A
            ) == 1
        assert set(A) & set(B)
        return key in local_graph

    clauses = []

    def exactly_one(literals):
        assert all(type(value) is int for value in literals)
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

        # An ordinary C4 fibre forces a perfect matching on its side of every
        # disjoint block.  Thus high-high gets both directions, high-low only
        # the rigorously forced high-side direction, and low-low gets none.
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

    # All 84*14 = 1176 BP equations.
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

    # All C(84,2) = 3486 exact outer-pair equations.  Products are encoded
    # by full three-clause equivalences, not one-sided implications.
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

    internal = sum(local_internal_by_support.values())
    assert internal == sum(4 - deficit for deficit in deficits.values())
    assert products == 65520
    assert cardinality_equalities == 1176 + 3486

    meta = {
        "model": "independent fixed-local exact E0=75 CNF",
        "branch_index": branch_index,
        "source_row_index": branch["source_row_index"],
        "partition": branch["partition"],
        "compression_orbit_index": branch["compression_orbit_index"],
        "local_representative_index": branch["local_representative_index"],
        "local_orbit_size": branch["local_orbit_size"],
        "exceptional_fibres": len(exceptional),
        "ordinary_c4_fibres": len(high),
        "total_incident_deficit": sum(deficits.values()),
        "fixed_local_internal_edges": internal,
        "fixed_local_overlap_edges": local_overlap,
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
        record["verification"] = {
            key: value for key, value in checked.items() if key != "edges"
        }
        if checked["ok"]:
            record["positive_full_edge_variables"] = sorted(selected)
            Path(
                f"scratch_e75_fixed_exact_solution_branch{branch_index:03d}.json"
            ).write_text(json.dumps(checked, indent=2) + "\n", encoding="utf-8")
        else:
            record["status"] = "SAT_INVALID"
    out_queue.put(record)


def load_checkpoint():
    if CHECKPOINT.exists():
        data = json.loads(CHECKPOINT.read_text(encoding="utf-8"))
        assert data["catalog_size"] == BRANCH_COUNT
        return data
    return {
        "model": "per-branch checkpoint for independent E0=75 fixed-local SAT",
        "catalog_size": BRANCH_COUNT,
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
                name=f"e75-fixed-{branch_index}",
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
        "model": "independent fixed-local exact SAT portfolio for E0=75",
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
        "cumulative_latest_status_counts": dict(
            Counter(row["status"] for row in latest.values())
        ),
        "all_352_terminal": len(latest) == BRANCH_COUNT and all(
            row["status"] in ("SAT", "UNSAT") for row in latest.values()
        ),
        "proof_status": "no independently checked UNSAT certificates",
        "records": ordered,
    }
    PORTFOLIO.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", type=int, choices=range(BRANCH_COUNT))
    parser.add_argument("--build-only", action="store_true")
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--end", type=int, default=BRANCH_COUNT)
    parser.add_argument("--conflicts", type=int, default=20000)
    parser.add_argument("--wall-seconds", type=float, default=15)
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
        "all_terminal": result["all_352_terminal"],
    }), flush=True)


if __name__ == "__main__":
    mp.freeze_support()
    main()
