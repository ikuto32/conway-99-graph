"""Exact compact SAT lift of the eight E0=78 K2,3 local graph orbits."""

from __future__ import annotations

import argparse
import itertools
import json
import multiprocessing as mp
import queue
import time
from pathlib import Path

from scratch_general_exact_sat import coordinates, verify


INPUT_PATH = Path("scratch_general_e78_local_reps.json")
RESULT_PATH = Path("scratch_general_e78_k23_sat_portfolio.json")


def source_record():
    source = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    records = [row for row in source["records"] if row["support_form"] == "K2,3"]
    assert len(records) == 1
    record = records[0]
    assert record["local_graph_count"] == 512
    assert record["orbit_count_direct"] == record["orbit_count_burnside"] == 8
    assert sum(record["orbit_sizes"]) == 512
    return record


def build_cnf(branch_index, source_override=None):
    from pysat.card import CardEnc, EncType
    from pysat.formula import IDPool

    source = source_record() if source_override is None else source_override
    representative = source["representatives"][branch_index]
    labels, _index, full_variables, _full_edge = coordinates()
    supports = [tuple(sorted((label[0] // 2, label[1] // 2))) for label in labels]
    signs = [{symbol // 2: symbol % 2 for symbol in label} for label in labels]
    fibres = {
        support: [u for u, value in enumerate(supports) if value == support]
        for support in itertools.combinations(range(7), 2)
    }
    exceptional = {tuple(support) for support in source["supports_in_fibre_order"]}
    local_vertices = {
        item["outer_index_zero_based"] for item in source["local_vertex_order"]
    }
    assert local_vertices == {
        u for support in exceptional for u in fibres[support]
    }
    local_edges = {
        tuple(sorted(pair))
        for pair in representative["present_edges_outer_indices_zero_based"]
    }
    assert len(local_edges) == source.get("local_present_edge_count", len(local_edges))

    pool = IDPool(start_from=1)
    block_variables = {}
    variable_blocks = []
    for A, B in itertools.combinations(fibres, 2):
        if set(A) & set(B):
            continue
        variable_blocks.append((A, B))
        for u in fibres[A]:
            for v in fibres[B]:
                key = (min(u, v), max(u, v))
                block_variables[key] = pool.id(("edge",) + key)
    assert len(variable_blocks) == 105 and len(block_variables) == 1680

    def edge(u, v):
        if u > v:
            u, v = v, u
        key = (u, v)
        if key in block_variables:
            return block_variables[key]
        A, B = supports[u], supports[v]
        if u in local_vertices and v in local_vertices:
            return key in local_edges
        if A == B:
            return sum(signs[u][group] != signs[v][group] for group in A) == 1
        return False

    clauses = []
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

    # Redundant but exact support-aggregate consequences of BP for the six
    # exceptional disjoint blocks.  They considerably strengthen propagation.
    # A low vertex has one neighbour in every ordinary disjoint C4 fibre.
    support_row_constraints = 0
    forced_low_block_rows = 0
    for F in sorted(exceptional):
        disjoint_low = [G for G in sorted(exceptional) if set(F).isdisjoint(G)]
        r = len(disjoint_low)
        for u in fibres[F]:
            same_degree = sum(edge(u, v) is True for v in fibres[F] if v != u)
            overlap_neighbours = [
                v
                for G in exceptional
                if G != F and set(F) & set(G)
                for v in fibres[G]
                if edge(u, v) is True
            ]
            required_total = r + same_degree - 2
            rows = [
                [edge(u, v) for v in fibres[G]] for G in disjoint_low
            ]
            add_exact([literal for row in rows for literal in row], required_total)
            support_row_constraints += 1
            external_groups = [group for group in range(7) if group not in F]
            possibilities = []
            for values in itertools.product(range(5), repeat=r):
                if sum(values) != required_total:
                    continue
                valid = True
                for group in external_groups:
                    t = sum(group in G for G in disjoint_low)
                    o = sum(group in supports[v] for v in overlap_neighbours)
                    if sum(value for value, G in zip(values, disjoint_low) if group in G) != t - o:
                        valid = False
                        break
                if valid:
                    possibilities.append(values)
            assert possibilities
            for q, row in enumerate(rows):
                values = {possibility[q] for possibility in possibilities}
                if len(values) == 1:
                    add_exact(row, next(iter(values)))
                    forced_low_block_rows += 1

    for u, label in enumerate(labels):
        own = set(label)
        for symbol in range(14):
            expressions = [
                edge(u, v)
                for v, other in enumerate(labels)
                if u != v and symbol in other and edge(u, v) is not False
            ]
            add_exact(expressions, 1 if symbol in own or (symbol ^ 1) in own else 2)

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
                helper = pool.id(("and", u, v, w))
                clauses.extend(([-a, -b, helper], [a, -helper], [b, -helper]))
                expressions.append(helper)
                products += 1
        add_exact(expressions, 2 - len(set(labels[u]) & set(labels[v])))

    meta = {
        "model": "exact compact unrestricted-rooted E0=78 K2,3 local orbit",
        "branch_index": branch_index,
        "local_orbit_size": representative["orbit_size"],
        "canonical_local_mask": representative["canonical_mask_hex_over_C24_2"],
        "local_present_edges": len(local_edges),
        "variable_blocks": len(variable_blocks),
        "two_sided_permutation_blocks": permutation_blocks,
        "one_sided_column_one_blocks": one_sided_blocks,
        "unrestricted_low_low_disjoint_blocks": unrestricted_low_low_blocks,
        "redundant_support_row_constraints": support_row_constraints,
        "forced_low_low_block_row_constraints": forced_low_block_rows,
        "edge_variables": len(block_variables),
        "product_variables": products,
        "direct_product_terms": direct_terms,
        "constant_product_terms": constant_terms,
        "variables": pool.top,
        "clauses": len(clauses),
    }
    return clauses, edge, full_variables, meta


def solve_one(branch_index, out_queue):
    from pysat.solvers import Solver

    started = time.monotonic()
    clauses, edge, full_variables, meta = build_cnf(branch_index)
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
        selected = {
            identifier
            for pair, identifier in full_variables.items()
            if edge(*pair) is True
            or (type(edge(*pair)) is int and edge(*pair) in positive)
        }
        checked = verify(selected)
        record["verification"] = {key: value for key, value in checked.items() if key != "edges"}
        record["positive_full_edge_variables"] = sorted(selected) if checked["ok"] else []
    out_queue.put(record)


def run_portfolio(seconds, max_parallel):
    context = mp.get_context("spawn")
    records = {}
    count = 8
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
        "model": "exact compact E0=78 K2,3, eight exhaustive local graph orbits",
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
        _clauses, _edge, _full, meta = build_cnf(args.branch)
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
