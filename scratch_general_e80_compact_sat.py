"""Propagation-strong exact SAT model for the five E0=80 local orbits.

Unlike the unrestricted 3,486-edge CNF, the corrected E0=80 classification
leaves 103 variable disjoint-support blocks.  The 67 C4--C4 blocks are
permutation matrices.  The 36 C4--P4 blocks have only a one-sided degree-one
condition at the P4 vertices; BP couples the C4-side row totals across
blocks.  Every BP and common-neighbour equation is encoded exactly.
"""

from __future__ import annotations

import argparse
import itertools
import json
import multiprocessing as mp
import queue
import time
from pathlib import Path

from scratch_general_e80_exact_sat import build as build_orbits
from scratch_general_e80_local_audit import LABELS as LOCAL_LABELS, SUPPORTS
from scratch_general_exact_sat import coordinates, verify


RESULT_PATH = Path("scratch_general_e80_corrected_sat_portfolio.json")


def build_cnf(branch_index: int):
    from pysat.card import CardEnc, EncType
    from pysat.formula import IDPool

    orbit_meta = build_orbits()
    branch = orbit_meta["branches"][branch_index]
    local_edges = {tuple(edge) for edge in branch["local_edges"]}
    labels, index, full_variables, _full_edge = coordinates()
    supports = [tuple(sorted((label[0] // 2, label[1] // 2))) for label in labels]
    signs = [{symbol // 2: symbol % 2 for symbol in label} for label in labels]
    fibres = {
        support: [u for u, value in enumerate(supports) if value == support]
        for support in itertools.combinations(range(7), 2)
    }
    local_global = [index[label] for label in LOCAL_LABELS]
    global_to_local = {u: q for q, u in enumerate(local_global)}
    exceptional = set(tuple(support) for support in SUPPORTS)

    pool = IDPool(start_from=1)
    block_variables = {}
    variable_blocks = []
    for A, B in itertools.combinations(fibres, 2):
        if set(A) & set(B):
            continue
        if A in exceptional and B in exceptional:
            continue
        variable_blocks.append((A, B))
        for u in fibres[A]:
            for v in fibres[B]:
                block_variables[(min(u, v), max(u, v))] = pool.id(("edge", min(u, v), max(u, v)))
    assert len(variable_blocks) == 103 and len(block_variables) == 1648

    def edge(u, v):
        if u > v:
            u, v = v, u
        key = (u, v)
        if key in block_variables:
            return block_variables[key]
        A, B = supports[u], supports[v]
        if u in global_to_local and v in global_to_local:
            pair = tuple(sorted((global_to_local[u], global_to_local[v])))
            return pair in local_edges
        if A == B:
            return sum(signs[u][g] != signs[v][g] for g in A) == 1
        return False

    clauses = []
    permutation_blocks = 0
    one_sided_blocks = 0
    for A, B in variable_blocks:
        if A not in exceptional and B not in exceptional:
            # Both C4 fibres force degree one from both sides.
            permutation_blocks += 1
            for u in fibres[A]:
                row = [edge(u, v) for v in fibres[B]]
                clauses.append(row)
                clauses.extend([-x, -y] for x, y in itertools.combinations(row, 2))
            for v in fibres[B]:
                column = [edge(u, v) for u in fibres[A]]
                clauses.extend([-x, -y] for x, y in itertools.combinations(column, 2))
        else:
            # If H is C4 and L is P4, every vertex of L has exactly one
            # neighbour in H.  A row condition on H is not valid per block.
            one_sided_blocks += 1
            high, low = (A, B) if A not in exceptional else (B, A)
            for v in fibres[low]:
                column = [edge(u, v) for u in fibres[high]]
                clauses.append(column)
                clauses.extend([-x, -y] for x, y in itertools.combinations(column, 2))
    assert permutation_blocks == 67 and one_sided_blocks == 36

    def add_exact(expressions, wanted):
        fixed = sum(value is True for value in expressions)
        lits = [value for value in expressions if type(value) is int]
        assert not any(value is False for value in expressions)
        target = wanted - fixed
        if target < 0 or target > len(lits):
            clauses.append([])
        elif not lits:
            if target:
                clauses.append([])
        else:
            clauses.extend(
                CardEnc.equals(lits, target, vpool=pool, encoding=EncType.seqcounter).clauses
            )

    # Root/inner pair equations BP=PA0.
    for u, label in enumerate(labels):
        own = set(label)
        for symbol in range(14):
            expressions = [
                edge(u, v)
                for v, other in enumerate(labels)
                if u != v and symbol in other and edge(u, v) is not False
            ]
            target = 1 if symbol in own or (symbol ^ 1) in own else 2
            add_exact(expressions, target)

    products = 0
    direct_terms = 0
    constant_terms = 0
    for u, v in itertools.combinations(range(84), 2):
        expressions = []
        uv = edge(u, v)
        if uv is not False:
            expressions.append(uv)
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
                z = pool.id(("and", u, v, w))
                clauses.extend(([-a, -b, z], [a, -z], [b, -z]))
                expressions.append(z)
                products += 1
        target = 2 - len(set(labels[u]) & set(labels[v]))
        add_exact(expressions, target)

    meta = {
        "model": "corrected exact compact E0=80 unrestricted-rooted branch",
        "branch_index": branch_index,
        "branch": branch["branch"],
        "local_orbit_size": branch["orbit_size"],
        "variable_blocks": len(variable_blocks),
        "two_sided_permutation_blocks": permutation_blocks,
        "one_sided_column_one_blocks": one_sided_blocks,
        "edge_variables": len(block_variables),
        "product_variables": products,
        "direct_product_terms": direct_terms,
        "constant_product_terms": constant_terms,
        "variables": pool.top,
        "clauses": len(clauses),
    }
    return clauses, pool.top, block_variables, edge, full_variables, meta


def solve_one(branch_index, out_queue):
    from pysat.solvers import Solver

    started = time.monotonic()
    clauses, _top, block_variables, edge, full_variables, meta = build_cnf(branch_index)
    built = time.monotonic()
    with Solver(name="cadical195", bootstrap_with=clauses) as solver:
        answer = solver.solve()
        model = solver.get_model() if answer else None
        stats = solver.accum_stats()
    record = {
        "branch_index": branch_index,
        "branch": meta["branch"],
        "status": "SAT" if answer else "UNSAT",
        "build_seconds": round(built - started, 3),
        "solve_seconds": round(time.monotonic() - built, 3),
        "meta": meta,
        "stats": stats,
    }
    if model:
        positive = {literal for literal in model if literal > 0}
        selected = set()
        for pair, identifier in full_variables.items():
            value = edge(*pair)
            if value is True or (type(value) is int and value in positive):
                selected.add(identifier)
        checked = verify(selected)
        record["verification"] = {k: v for k, v in checked.items() if k != "edges"}
        record["positive_full_edge_variables"] = sorted(selected) if checked["ok"] else []
    out_queue.put(record)


def run_portfolio(seconds, max_parallel):
    context = mp.get_context("spawn")
    records = {}
    for offset in range(0, 5, max_parallel):
        batch = list(range(offset, min(5, offset + max_parallel)))
        out_queue = context.Queue()
        processes = {}
        for branch_index in batch:
            process = context.Process(target=solve_one, args=(branch_index, out_queue))
            process.start()
            processes[branch_index] = process
        deadline = time.monotonic() + seconds
        while not all(index in records for index in batch):
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            try:
                record = out_queue.get(timeout=min(1.0, remaining))
            except queue.Empty:
                continue
            records[record["branch_index"]] = record
        for branch_index, process in processes.items():
            if process.is_alive():
                process.terminate()
                process.join(10)
            else:
                process.join()
            records.setdefault(branch_index, {
                "branch_index": branch_index,
                "branch": f"e80_o{branch_index:02d}",
                "status": "UNKNOWN",
                "wall_limit_seconds": seconds,
                "exit_code_after_termination": process.exitcode,
            })
    ordered = [records[index] for index in range(5)]
    status = (
        "SAT" if any(row["status"] == "SAT" for row in ordered)
        else "UNSAT" if all(row["status"] == "UNSAT" for row in ordered)
        else "UNKNOWN"
    )
    result = {
        "model": "corrected exact compact E0=80, five exhaustive local orbits",
        "solver": "CaDiCaL 1.9.5 via PySAT",
        "seconds_per_parallel_batch": seconds,
        "max_parallel": max_parallel,
        "coverage_source": "scratch_general_e80_exact_build.json",
        "status": status,
        "records": ordered,
    }
    RESULT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", type=int)
    parser.add_argument("--build-only", action="store_true")
    parser.add_argument("--seconds", type=float, default=0)
    parser.add_argument("--max-parallel", type=int, default=4)
    args = parser.parse_args()
    if args.branch is not None:
        clauses, top, _bv, _edge, _fv, meta = build_cnf(args.branch)
        print(json.dumps(meta), flush=True)
        if not args.build_only:
            out_queue = mp.get_context("spawn").Queue()
            solve_one(args.branch, out_queue)
            print(json.dumps(out_queue.get()), flush=True)
    elif args.seconds > 0:
        result = run_portfolio(args.seconds, min(4, max(1, args.max_parallel)))
        print(json.dumps({
            "status": result["status"],
            "counts": {
                value: sum(row["status"] == value for row in result["records"])
                for value in ("SAT", "UNSAT", "UNKNOWN")
            },
        }), flush=True)
    else:
        parser.error("use --branch or --seconds")


if __name__ == "__main__":
    mp.freeze_support()
    main()
