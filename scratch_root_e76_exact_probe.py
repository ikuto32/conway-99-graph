"""Probe one independently audited E0=76 local orbit with the exact CNF."""

from __future__ import annotations

import argparse
import itertools
import json
import time
from pathlib import Path

import scratch_general_e78_k23_sat as compact
from scratch_general_e79_local_audit import vertex_label
from scratch_general_exact_sat import coordinates, verify


INPUT = Path("scratch_e76_independent_local.json")


def source_record(active_row):
    source = json.loads(INPUT.read_text(encoding="utf-8"))
    rows = [row for row in source["rows"] if row["distinct_forced_local_graphs"]]
    if not 0 <= active_row < len(rows):
        raise ValueError(f"row {active_row} outside 0..{len(rows) - 1}")
    row = rows[active_row]
    supports = tuple(
        tuple(item["support"]) for item in row["exceptional_supports"]
    )
    labels, outer_index, _variables, _edge = coordinates()
    vertices = tuple(sorted(
        vertex_label(support, bits)
        for support in supports
        for bits in itertools.product((0, 1), repeat=2)
    ))
    assert {tuple(labels[outer_index[vertex]]) for vertex in vertices} == set(vertices)
    representatives = [
        {
            "representative_id": rep["representative_index"],
            "orbit_size": rep["local_orbit_size"],
            "canonical_mask_hex_over_C24_2": (
                f"E76-row{active_row}-rep{rep['representative_index']}"
            ),
            "present_edges_outer_indices_zero_based": rep[
                "edges_by_outer_index_zero_based"
            ],
        }
        for rep in row["representatives"]
    ]
    assert len(representatives) == row["local_graph_orbits"]
    assert sum(rep["orbit_size"] for rep in representatives) == row[
        "distinct_forced_local_graphs"
    ]
    edge_counts = {rep["local_edge_count"] for rep in row["representatives"]}
    assert len(edge_counts) == 1
    return {
        "support_form": (
            f"E76-{'+'.join(map(str, sorted(row['partition'], reverse=True)))}"
            f"-orbit{row['compression_orbit_index']}"
        ),
        "supports_in_fibre_order": [list(support) for support in supports],
        "local_vertex_order": [
            {
                "symbol_label": list(vertex),
                "outer_index_zero_based": outer_index[vertex],
            }
            for vertex in vertices
        ],
        "local_graph_count": row["distinct_forced_local_graphs"],
        "local_present_edge_count": next(iter(edge_counts)),
        "orbit_count_direct": len(representatives),
        "orbit_sizes": [rep["orbit_size"] for rep in representatives],
        "representatives": representatives,
        "source_row": {
            "active_row": active_row,
            "partition": row["partition"],
            "compression_orbit_index": row["compression_orbit_index"],
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--row", type=int, required=True)
    parser.add_argument("--rep", type=int, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    source = source_record(args.row)
    if not 0 <= args.rep < len(source["representatives"]):
        raise ValueError(
            f"rep {args.rep} outside 0..{len(source['representatives']) - 1}"
        )
    started = time.monotonic()
    clauses, edge, full_variables, meta = compact.build_cnf(args.rep, source)
    built = time.monotonic()
    from pysat.solvers import Solver
    with Solver(name="cadical195", bootstrap_with=clauses) as solver:
        answer = solver.solve()
        model = solver.get_model() if answer else None
        stats = solver.accum_stats()
    solved = time.monotonic()
    record = {
        "row": args.row,
        "rep": args.rep,
        "source": source["source_row"],
        "status": "SAT" if answer else "UNSAT",
        "build_seconds": round(built - started, 3),
        "solve_seconds": round(solved - built, 3),
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
        record["verification"] = {
            key: value for key, value in checked.items() if key != "edges"
        }
        if checked["ok"]:
            record["verified_edges"] = checked["edges"]
    if args.output:
        args.output.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "row": args.row,
        "rep": args.rep,
        "status": record["status"],
        "build_seconds": record["build_seconds"],
        "solve_seconds": record["solve_seconds"],
        "conflicts": stats.get("conflicts"),
        "decisions": stats.get("decisions"),
        "verification_ok": record.get("verification", {}).get("ok"),
    }), flush=True)


if __name__ == "__main__":
    main()
