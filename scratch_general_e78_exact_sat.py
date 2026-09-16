"""Exact compact SAT lift for the four local E0=78 survivor supports.

This model does not normalize any P4 orientation or deficit-two fibre type.
The same-support edge sets are table-constrained to all exact allowed labelled
states, and all low-low blocks remain variable.  Every BP and outer-pair
common-neighbour equation is imposed as an equality.
"""

from __future__ import annotations

import argparse
import itertools
import json
import multiprocessing as mp
import queue
import time
from pathlib import Path

from scratch_general_e78_port_audit import FIBRE_STATES, VERTICES
from scratch_general_exact_sat import coordinates, verify


INPUT_PATH = Path("scratch_general_e78_port_audit.json")
RESULT_PATH = Path("scratch_general_e78_exact_sat_portfolio.json")


def branches():
    source = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    rows = [
        row
        for row in source["rows"]
        if row["locally_port_and_spectral_feasible_assignments"] > 0
    ]
    assert len(rows) == 4
    return rows


def build_cnf(branch_index):
    from pysat.card import CardEnc, EncType
    from pysat.formula import IDPool

    branch = branches()[branch_index]
    labels, _index, full_variables, _full_edge = coordinates()
    supports = [tuple(sorted((label[0] // 2, label[1] // 2))) for label in labels]
    signs = [{symbol // 2: symbol % 2 for symbol in label} for label in labels]
    fibres = {
        support: [u for u, value in enumerate(supports) if value == support]
        for support in itertools.combinations(range(7), 2)
    }
    exceptional = {
        tuple(item["support"]): item["deficit"]
        for item in branch["exceptional_supports"]
    }
    assert sum(exceptional.values()) == 6

    pool = IDPool(start_from=1)
    edge_variables = {}
    variable_blocks = []
    same_fibre_variables = {}

    for support, deficit in exceptional.items():
        vertices = fibres[support]
        for u, v in itertools.combinations(vertices, 2):
            key = (min(u, v), max(u, v))
            same_fibre_variables[key] = pool.id(("edge",) + key)
            edge_variables[key] = same_fibre_variables[key]

    for A, B in itertools.combinations(fibres, 2):
        if set(A) & set(B) and not (A in exceptional and B in exceptional):
            continue
        if set(A).isdisjoint(B) or (A in exceptional and B in exceptional):
            variable_blocks.append((A, B))
            for u in fibres[A]:
                for v in fibres[B]:
                    key = (min(u, v), max(u, v))
                    assert key not in edge_variables
                    edge_variables[key] = pool.id(("edge",) + key)

    def edge(u, v):
        if u > v:
            u, v = v, u
        key = (u, v)
        if key in edge_variables:
            return edge_variables[key]
        A, B = supports[u], supports[v]
        if A == B and A not in exceptional:
            return sum(signs[u][g] != signs[v][g] for g in A) == 1
        return False

    clauses = []

    # Exact labelled fibre-state tables.  Enumerating all forbidden six-bit
    # words gives a small, transparent CNF with no auxiliary selector choice.
    state_table_clauses = 0
    for support, deficit in exceptional.items():
        vertices = fibres[support]
        local_pairs = tuple(itertools.combinations(range(4), 2))
        global_lits = [edge(vertices[u], vertices[v]) for u, v in local_pairs]
        # The local vertex order agrees with (00,01,10,11).
        actual_signs = tuple(
            tuple(signs[vertices[u]][g] for g in support) for u in range(4)
        )
        assert actual_signs == VERTICES
        allowed = {
            tuple(pair in set(state["edges"]) for pair in local_pairs)
            for state in FIBRE_STATES[deficit]
        }
        assert len(allowed) == (4 if deficit == 1 else 7)
        for word in itertools.product((False, True), repeat=6):
            if word in allowed:
                continue
            clauses.append([
                -literal if value else literal
                for literal, value in zip(global_lits, word)
            ])
            state_table_clauses += 1

    permutation_blocks = 0
    one_sided_blocks = 0
    unrestricted_low_low_blocks = 0
    for A, B in variable_blocks:
        if A in exceptional and B in exceptional:
            unrestricted_low_low_blocks += 1
            continue
        if A not in exceptional and B not in exceptional:
            permutation_blocks += 1
            for u in fibres[A]:
                row = [edge(u, v) for v in fibres[B]]
                clauses.append(row)
                clauses.extend([-x, -y] for x, y in itertools.combinations(row, 2))
            for v in fibres[B]:
                column = [edge(u, v) for u in fibres[A]]
                clauses.extend([-x, -y] for x, y in itertools.combinations(column, 2))
        else:
            one_sided_blocks += 1
            high, low = (A, B) if A not in exceptional else (B, A)
            for v in fibres[low]:
                column = [edge(u, v) for u in fibres[high]]
                clauses.append(column)
                clauses.extend([-x, -y] for x, y in itertools.combinations(column, 2))

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
        add_exact(expressions, 2 - len(set(labels[u]) & set(labels[v])))

    meta = {
        "model": "exact compact unrestricted-rooted E0=78 branch",
        "branch_index": branch_index,
        "partition": branch["partition"],
        "compression_orbit_index": branch["orbit_index"],
        "support_orbit_size": branch["support_orbit_size"],
        "exceptional_supports": branch["exceptional_supports"],
        "local_port_feasible_state_assignments": branch[
            "locally_port_and_spectral_feasible_assignments"
        ],
        "same_fibre_edge_variables": len(same_fibre_variables),
        "state_table_clauses": state_table_clauses,
        "variable_blocks": len(variable_blocks),
        "two_sided_permutation_blocks": permutation_blocks,
        "one_sided_column_one_blocks": one_sided_blocks,
        "unrestricted_low_low_blocks": unrestricted_low_low_blocks,
        "edge_variables": len(edge_variables),
        "product_variables": products,
        "direct_product_terms": direct_terms,
        "constant_product_terms": constant_terms,
        "variables": pool.top,
        "clauses": len(clauses),
    }
    return clauses, edge_variables, edge, full_variables, meta


def solve_one(branch_index, out_queue):
    from pysat.solvers import Solver

    started = time.monotonic()
    clauses, edge_variables, edge, full_variables, meta = build_cnf(branch_index)
    built = time.monotonic()
    with Solver(name="cadical195", bootstrap_with=clauses) as solver:
        answer = solver.solve()
        model = solver.get_model() if answer else None
        stats = solver.accum_stats()
    record = {
        "branch_index": branch_index,
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
        record["verification"] = {key: value for key, value in checked.items() if key != "edges"}
        record["positive_full_edge_variables"] = sorted(selected) if checked["ok"] else []
    out_queue.put(record)


def run_portfolio(seconds, max_parallel):
    context = mp.get_context("spawn")
    records = {}
    count = len(branches())
    for offset in range(0, count, max_parallel):
        batch = list(range(offset, min(count, offset + max_parallel)))
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
                "status": "UNKNOWN",
                "wall_limit_seconds": seconds,
                "exit_code_after_termination": process.exitcode,
            })
    ordered = [records[index] for index in range(count)]
    status = (
        "SAT" if any(row["status"] == "SAT" for row in ordered)
        else "UNSAT" if all(row["status"] == "UNSAT" for row in ordered)
        else "UNKNOWN"
    )
    result = {
        "model": "exact compact E0=78, four exhaustive local support branches",
        "solver": "CaDiCaL 1.9.5 via PySAT",
        "seconds_per_parallel_batch": seconds,
        "max_parallel": max_parallel,
        "coverage_source": str(INPUT_PATH),
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
        clauses, _variables, _edge, _full, meta = build_cnf(args.branch)
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
