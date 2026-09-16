"""Exact compact SAT lift of the three surviving E0=77 local graph orbits."""

from __future__ import annotations

import argparse
import itertools
import json
import multiprocessing as mp
import queue
import time
from pathlib import Path

import scratch_general_e78_k23_sat as compact
from scratch_general_e79_local_audit import local_actions, vertex_label
from scratch_general_exact_sat import coordinates, verify


INPUT_PATH = Path("scratch_root_e77_local.json")
RESULT_PATH = Path("scratch_general_e77_exact_sat_portfolio.json")


def source_record():
    source = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    rows = [row for row in source["rows"] if row["after_forced_C4_support_BP"]]
    assert len(rows) == 1
    row = rows[0]
    assert row["partition"] == [1] * 7
    assert row["after_forced_C4_support_BP"] == 512
    assert row["after_forced_C4_support_BP_orbits"] == 3
    supports = tuple(tuple(support) for support in row["supports"])
    vertices = tuple(sorted(
        vertex_label(support, bits)
        for support in supports
        for bits in itertools.product((0, 1), repeat=2)
    ))
    assert len(vertices) == 28
    vertex_position = {vertex: q for q, vertex in enumerate(vertices)}
    labels, outer_index, _variables, _edge = coordinates()
    actions = local_actions(supports, vertices)
    assert len(actions) == row["distinct_local_symmetry_actions"] == 256

    representatives = []
    orbit_sets = []
    for representative_id, raw_graph in enumerate(row["canonical_local_graph_representatives"]):
        graph = {
            tuple(sorted((tuple(left), tuple(right))))
            for left, right in raw_graph
        }
        assert len(graph) == 35
        local_graph = frozenset(
            tuple(sorted((vertex_position[u], vertex_position[v]))) for u, v in graph
        )
        images = set()
        for action in actions:
            images.add(frozenset(
                tuple(sorted((action[u], action[v]))) for u, v in local_graph
            ))
        orbit_sets.append(images)
        representatives.append({
            "representative_id": representative_id,
            "orbit_size": len(images),
            "canonical_mask_hex_over_C24_2": f"E77-local-rep-{representative_id}",
            "present_edges_outer_indices_zero_based": [
                list(sorted((outer_index[u], outer_index[v]))) for u, v in sorted(graph)
            ],
        })
    assert all(orbit_sets[i].isdisjoint(orbit_sets[j]) for i, j in itertools.combinations(range(3), 2))
    assert sum(map(len, orbit_sets)) == 512
    local_vertex_order = [
        {
            "symbol_label": list(vertex),
            "outer_index_zero_based": outer_index[vertex],
        }
        for vertex in vertices
    ]
    assert {tuple(labels[item["outer_index_zero_based"]]) for item in local_vertex_order} == set(vertices)
    return {
        "support_form": "E77-orbit22",
        "supports_in_fibre_order": [list(support) for support in supports],
        "local_vertex_order": local_vertex_order,
        "local_graph_count": 512,
        "local_present_edge_count": 35,
        "orbit_count_direct": 3,
        "orbit_count_burnside": 3,
        "orbit_sizes": [rep["orbit_size"] for rep in representatives],
        "representatives": representatives,
    }


def build_cnf(branch_index):
    source = source_record()
    clauses, edge, full_variables, meta = compact.build_cnf(branch_index, source)
    meta.update({
        "model": "exact compact unrestricted-rooted E0=77 local orbit",
        "coverage_source": str(INPUT_PATH),
        "local_graph_count": source["local_graph_count"],
        "local_orbit_count": source["orbit_count_direct"],
        "all_local_orbit_sizes": source["orbit_sizes"],
    })
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


def run_portfolio(seconds):
    context = mp.get_context("spawn")
    out_queue = context.Queue()
    processes = {}
    for branch_index in range(3):
        process = context.Process(target=solve_one, args=(branch_index, out_queue))
        process.start()
        processes[branch_index] = process
    deadline = time.monotonic() + seconds
    records = {}
    while len(records) < 3:
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
    ordered = [records[q] for q in range(3)]
    status = (
        "SAT" if any(row["status"] == "SAT" for row in ordered)
        else "UNSAT" if all(row["status"] == "UNSAT" for row in ordered)
        else "UNKNOWN"
    )
    result = {
        "model": "exact compact E0=77, three exhaustive local graph orbits",
        "solver": "CaDiCaL 1.9.5 via PySAT",
        "seconds": seconds,
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
    parser.add_argument("--seconds", type=float, default=60)
    args = parser.parse_args()
    if args.branch is not None:
        _clauses, _edge, _full, meta = build_cnf(args.branch)
        print(json.dumps(meta), flush=True)
        if not args.build_only:
            out_queue = mp.get_context("spawn").Queue()
            solve_one(args.branch, out_queue)
            print(json.dumps(out_queue.get()), flush=True)
    else:
        result = run_portfolio(args.seconds)
        print(json.dumps({
            "status": result["status"],
            "counts": {
                value: sum(row["status"] == value for row in result["records"])
                for value in ("SAT", "UNSAT", "UNKNOWN")
            },
        }), flush=True)


if __name__ == "__main__":
    mp.freeze_support()
    main()
