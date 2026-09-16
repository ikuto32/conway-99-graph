"""Generic independent fixed-local exact SAT runner for completed E0=74 rows.

The input is any committed E74 local-expansion JSON containing explicit
``local_graph_representatives``.  Every branch is rebuilt as a fresh CNF: all
1,806 non-disjoint outer pairs are constants from the local graph/ordinary
C4 scaffold and all 1,680 disjoint pairs are variables.  No shared incremental
implementation is imported.  The default source is completed part 19; the
same runner accepts part 20 without code changes.
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


DEFAULT_SOURCE = Path("scratch_general_e74_local_expansion_part_19.json")


def artifact_paths(tag):
    stem = f"scratch_e74_independent_{tag}_fixed_exact"
    return {
        "catalog": Path(stem + "_catalog.json"),
        "checkpoint": Path(stem + "_checkpoint.json"),
        "portfolio": Path(stem + "_portfolio.json"),
        "solution_stem": stem + "_solution_branch",
    }


def branch_catalog(source_path):
    source = json.loads(Path(source_path).read_text(encoding="utf-8"))
    branches = []
    for row_index, row in enumerate(source["rows"]):
        representatives = row.get("local_graph_representatives", ())
        for representative_index, representative in enumerate(representatives):
            branches.append({
                "branch_index": len(branches),
                "source_row_index": row_index,
                "partition": row["partition"],
                "compression_orbit_index": row["compression_orbit_index"],
                "exceptional_supports": row["exceptional_supports"],
                "local_representative_index": representative_index,
                "local_orbit_size": representative["orbit_size"],
                "local_mask_hex": representative["mask_hex"],
                "Q": representative.get("Q"),
                "local_edges": representative["edges"],
            })
    return branches


def write_catalog(source_path, branches, path):
    data = {
        "model": "independent generic E0=74 fixed-local exact branch catalog",
        "source": str(source_path),
        "branch_count": len(branches),
        "covered_labelled_local_graphs": sum(
            branch["local_orbit_size"] for branch in branches
        ),
        "branches": [
            {key: value for key, value in branch.items() if key != "local_edges"}
            for branch in branches
        ],
    }
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def build_cnf(source_path, branch_index):
    from pysat.card import CardEnc, EncType
    from pysat.formula import IDPool

    branch = branch_catalog(source_path)[branch_index]
    labels, label_index, full_variables, _full_edge = coordinates()
    supports = tuple(tuple(symbol // 2 for symbol in label) for label in labels)
    signs = tuple({symbol // 2: symbol % 2 for symbol in label} for label in labels)
    fibres = {
        support: tuple(index for index, value in enumerate(supports) if value == support)
        for support in itertools.combinations(range(7), 2)
    }
    deficits = {
        tuple(item["support"]): item["deficit"]
        for item in branch["exceptional_supports"]
    }
    exceptional = frozenset(deficits)
    ordinary = frozenset(set(fibres) - set(exceptional))
    assert sum(deficits.values()) == 10
    local_graph = frozenset(
        tuple(sorted((label_index[tuple(raw_u)], label_index[tuple(raw_v)])))
        for raw_u, raw_v in branch["local_edges"]
    )
    assert len(local_graph) == len(branch["local_edges"])

    internal_by_support = Counter()
    overlap = 0
    for u, v in local_graph:
        A, B = supports[u], supports[v]
        assert A in exceptional and B in exceptional
        if A == B:
            internal_by_support[A] += 1
        else:
            assert set(A) & set(B)
            overlap += 1
    assert overlap == 20
    assert all(internal_by_support[support] == 4 - deficit
               for support, deficit in deficits.items())
    internal = sum(internal_by_support.values())
    assert len(local_graph) == internal + overlap

    pool = IDPool(start_from=1)
    edge_variables = {}
    disjoint_blocks = []
    for A, B in itertools.combinations(fibres, 2):
        if not set(A).isdisjoint(B):
            continue
        disjoint_blocks.append((A, B))
        for u in fibres[A]:
            for v in fibres[B]:
                pair = tuple(sorted((u, v)))
                edge_variables[pair] = pool.id(("edge",) + pair)
    assert len(disjoint_blocks) == 105 and len(edge_variables) == 1680

    def edge(u, v):
        if u == v:
            return False
        pair = tuple(sorted((u, v)))
        if pair in edge_variables:
            return edge_variables[pair]
        A, B = supports[u], supports[v]
        if A == B:
            if A in exceptional:
                return pair in local_graph
            return sum(signs[u][group] != signs[v][group] for group in A) == 1
        assert set(A) & set(B)
        return pair in local_graph

    fixed_values = [
        edge(u, v) for u, v in itertools.combinations(range(84), 2)
        if tuple(sorted((u, v))) not in edge_variables
    ]
    assert len(fixed_values) == 1806
    assert all(type(value) is bool for value in fixed_values)

    clauses = []

    def exactly_one(literals):
        literals = tuple(literals)
        assert len(literals) == 4 and all(type(value) is int for value in literals)
        clauses.append(list(literals))
        clauses.extend([-left, -right]
                       for left, right in itertools.combinations(literals, 2))

    block_types = Counter()
    block_equalities = 0
    for A, B in disjoint_blocks:
        if A in ordinary and B in ordinary:
            block_types["ordinary_ordinary"] += 1
        elif A in ordinary or B in ordinary:
            block_types["ordinary_exceptional"] += 1
        else:
            block_types["exceptional_exceptional"] += 1
        if A in ordinary:
            for v in fibres[B]:
                exactly_one(edge(u, v) for u in fibres[A])
                block_equalities += 1
        if B in ordinary:
            for u in fibres[A]:
                exactly_one(edge(u, v) for v in fibres[B])
                block_equalities += 1

    cardinality_equalities = 0
    empty_clauses = 0

    def add_exact(expressions, wanted):
        nonlocal cardinality_equalities, empty_clauses
        fixed = sum(value is True for value in expressions)
        literals = [value for value in expressions if type(value) is int]
        target = wanted - fixed
        cardinality_equalities += 1
        if target < 0 or target > len(literals):
            clauses.append([])
            empty_clauses += 1
        elif not literals:
            if target:
                clauses.append([])
                empty_clauses += 1
        else:
            clauses.extend(CardEnc.equals(
                literals, target, vpool=pool, encoding=EncType.seqcounter
            ).clauses)

    for u, label in enumerate(labels):
        own = set(label)
        for symbol in range(14):
            add_exact(
                [edge(u, v) for v, other in enumerate(labels)
                 if u != v and symbol in other],
                1 if symbol in own or (symbol ^ 1) in own else 2,
            )

    product_variables = direct_terms = constant_terms = 0
    for u, v in itertools.combinations(range(84), 2):
        expressions = [edge(u, v)]
        for w in range(84):
            if w in (u, v):
                continue
            left, right = edge(u, w), edge(v, w)
            if left is False or right is False:
                continue
            if left is True and right is True:
                expressions.append(True)
                constant_terms += 1
            elif left is True:
                expressions.append(right)
                direct_terms += 1
            elif right is True:
                expressions.append(left)
                direct_terms += 1
            elif left == right:
                expressions.append(left)
                direct_terms += 1
            else:
                helper = pool.id(("and", u, v, w))
                clauses.extend(([-left, -right, helper],
                                [left, -helper], [right, -helper]))
                expressions.append(helper)
                product_variables += 1
        add_exact(expressions, 2 - len(set(labels[u]) & set(labels[v])))
    assert cardinality_equalities == 1176 + 3486
    assert product_variables == 65520

    meta = {
        "model": "independent generic E0=74 fixed-local exact CNF",
        "branch_index": branch_index,
        "source_row_index": branch["source_row_index"],
        "partition": branch["partition"],
        "compression_orbit_index": branch["compression_orbit_index"],
        "local_representative_index": branch["local_representative_index"],
        "local_orbit_size": branch["local_orbit_size"],
        "Q": branch["Q"],
        "exceptional_fibres": len(exceptional),
        "ordinary_c4_fibres": len(ordinary),
        "fixed_non_disjoint_outer_pairs": len(fixed_values),
        "fixed_non_disjoint_true_edges": sum(fixed_values),
        "fixed_non_disjoint_false_edges": len(fixed_values) - sum(fixed_values),
        "fixed_local_internal_edges": internal,
        "fixed_local_overlap_edges": overlap,
        "disjoint_edge_variables": len(edge_variables),
        "product_variables": product_variables,
        "direct_product_terms": direct_terms,
        "constant_product_terms": constant_terms,
        "disjoint_blocks": len(disjoint_blocks),
        "block_types": dict(block_types),
        "ordinary_c4_block_equalities": block_equalities,
        "BP_equalities": 1176,
        "outer_pair_equalities": 3486,
        "cardinality_equalities": cardinality_equalities,
        "empty_clauses_before_solving": empty_clauses,
        "redundant_support_aggregate_rows": 0,
        "variables": pool.top,
        "clauses": len(clauses),
    }
    return clauses, edge, full_variables, meta


def worker(source_path, tag, branch_index, conflict_budget, out_queue):
    from pysat.solvers import Solver

    started = time.monotonic()
    clauses, edge, full_variables, meta = build_cnf(source_path, branch_index)
    built = time.monotonic()
    with Solver(name="cadical195", bootstrap_with=clauses) as solver:
        solver.conf_budget(conflict_budget)
        answer = solver.solve_limited(expect_interrupt=True)
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
            paths = artifact_paths(tag)
            Path(paths["solution_stem"] + f"{branch_index:04d}.json").write_text(
                json.dumps(checked, indent=2) + "\n", encoding="utf-8"
            )
        else:
            record["status"] = "SAT_INVALID"
    out_queue.put(record)


def load_checkpoint(path, source_path, catalog_size):
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["source"] == str(source_path)
        assert data["catalog_size"] == catalog_size
        return data
    return {
        "model": "checkpoint for independent generic E0=74 fixed-local SAT",
        "source": str(source_path),
        "catalog_size": catalog_size,
        "attempts": {},
    }


def save_checkpoint(path, data):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def run(args):
    source_path = Path(args.source)
    paths = artifact_paths(args.tag)
    branches = branch_catalog(source_path)
    write_catalog(source_path, branches, paths["catalog"])
    checkpoint = load_checkpoint(paths["checkpoint"], source_path, len(branches))
    requested = list(range(max(0, args.start), min(args.end, len(branches))))
    if args.only_unknown:
        requested = [
            index for index in requested
            if not checkpoint["attempts"].get(str(index))
            or checkpoint["attempts"][str(index)][-1]["status"] == "UNKNOWN"
        ]
    context = mp.get_context("spawn")
    invocation = {}
    for offset in range(0, len(requested), args.max_parallel):
        batch = requested[offset:offset + args.max_parallel]
        out_queue = context.Queue()
        processes = {}
        for branch_index in batch:
            process = context.Process(
                target=worker,
                args=(source_path, args.tag, branch_index, args.conflicts, out_queue),
            )
            process.start()
            processes[branch_index] = process
        deadline = time.monotonic() + args.wall_seconds
        pending = set(batch)
        while pending and time.monotonic() < deadline:
            try:
                record = out_queue.get(timeout=min(1, deadline - time.monotonic()))
            except queue.Empty:
                continue
            index = record["branch_index"]
            if index in pending:
                pending.remove(index)
                invocation[index] = record
                checkpoint["attempts"].setdefault(str(index), []).append(record)
                checkpoint["last_update_unix"] = time.time()
                save_checkpoint(paths["checkpoint"], checkpoint)
        for index, process in processes.items():
            if process.is_alive():
                process.terminate()
                process.join(10)
            else:
                process.join()
            if index in pending:
                record = {
                    "branch_index": index,
                    "status": "UNKNOWN",
                    "termination": "wall_limit",
                    "conflict_budget": args.conflicts,
                    "wall_limit_seconds": args.wall_seconds,
                    "formal_proof_certificate": None,
                }
                invocation[index] = record
                checkpoint["attempts"].setdefault(str(index), []).append(record)
                save_checkpoint(paths["checkpoint"], checkpoint)
        print(json.dumps({
            "batch": batch,
            "completed": len(invocation),
            "counts": dict(Counter(row["status"] for row in invocation.values())),
        }), flush=True)

    latest = {int(index): attempts[-1]
              for index, attempts in checkpoint["attempts"].items() if attempts}
    result = {
        "model": "independent generic E0=74 fixed-local exact SAT portfolio",
        "source": str(source_path),
        "tag": args.tag,
        "catalog": str(paths["catalog"]),
        "checkpoint": str(paths["checkpoint"]),
        "catalog_size": len(branches),
        "catalog_labelled_weight": sum(row["local_orbit_size"] for row in branches),
        "invocation_count": len(invocation),
        "invocation_status_counts": dict(Counter(
            row["status"] for row in invocation.values()
        )),
        "cumulative_latest_count": len(latest),
        "cumulative_latest_status_counts": dict(Counter(
            row["status"] for row in latest.values()
        )),
        "all_catalog_branches_terminal": len(latest) == len(branches) and all(
            row["status"] in ("SAT", "UNSAT") for row in latest.values()
        ),
        "conflict_budget": args.conflicts,
        "wall_seconds_per_batch": args.wall_seconds,
        "only_unknown": args.only_unknown,
        "proof_boundary": "solver-terminal statuses; no checked UNSAT certificates",
        "records": [invocation[index] for index in sorted(invocation)],
    }
    paths["portfolio"].write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default=str(DEFAULT_SOURCE))
    parser.add_argument("--tag", default="part19")
    parser.add_argument("--branch", type=int)
    parser.add_argument("--build-only", action="store_true")
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--end", type=int, default=10**9)
    parser.add_argument("--conflicts", type=int, default=20000)
    parser.add_argument("--wall-seconds", type=float, default=25)
    parser.add_argument("--max-parallel", type=int, default=4)
    parser.add_argument("--only-unknown", action="store_true")
    args = parser.parse_args()
    args.max_parallel = min(4, max(1, args.max_parallel))
    if args.branch is not None:
        clauses, _edge, _full, meta = build_cnf(Path(args.source), args.branch)
        print(json.dumps(meta), flush=True)
        if not args.build_only:
            out_queue = mp.get_context("spawn").Queue()
            worker(Path(args.source), args.tag, args.branch, args.conflicts, out_queue)
            print(json.dumps(out_queue.get()), flush=True)
        return
    result = run(args)
    print(json.dumps({
        "invocation": result["invocation_status_counts"],
        "cumulative": result["cumulative_latest_status_counts"],
        "all_terminal": result["all_catalog_branches_terminal"],
    }), flush=True)


if __name__ == "__main__":
    mp.freeze_support()
    main()
