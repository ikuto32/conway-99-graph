"""Independent controls for the source-133 48-vertex pair-upper CNF."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

from scratch_general_e72_source133_hf_pair_sat import (
    INPUT,
    VERTEX_INPUT,
    build_instance,
    normal_pair,
)
from scratch_general_e72_source133_hf_witness_pair_probe import reconstruct


OUTPUT = Path("scratch_general_e72_source133_hf_pair_cnf_audit.json")


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest().upper()


def main():
    dependency_root = str(Path(".deps").resolve())
    if dependency_root not in sys.path:
        sys.path.insert(0, dependency_root)
    from pysat.solvers import Solver

    document = json.loads(INPUT.read_text(encoding="utf-8"))
    vertex_document = json.loads(VERTEX_INPUT.read_text(encoding="utf-8"))
    exceptional = tuple(tuple(row) for row in vertex_document["vertex_order"])
    record = next(row for row in document["frontier"] if row[3] < 4)
    instance = build_instance(exceptional, int(record[0], 16))
    base_clauses = instance["clauses"][
        :instance["base_clause_count_before_pair_upper"]
    ]

    # Decode the independently generated combinatorial witness into every
    # edge/t/orientation variable of the pre-pair CNF, then evaluate clauses.
    vertices, labelled_edges, t_by_support = reconstruct(record, exceptional)
    assert vertices == instance["vertices"]
    index = {vertex: x for x, vertex in enumerate(vertices)}
    indexed_edges = {
        normal_pair(index[left], index[right]) for left, right in labelled_edges
    }
    assignment = set()
    for pair, variable in instance["edge_variables"].items():
        if pair in indexed_edges:
            assignment.add(variable)
    for support, values in t_by_support.items():
        support_vertices = tuple(
            x for x, vertex in enumerate(vertices)
            if tuple(symbol // 2 for symbol in vertex) == support
        )
        assert len(support_vertices) == 4
        for x, value in zip(support_vertices, values):
            assignment.add(instance["t_variables"][(x, value)])
    t_options = record[4][3]
    for bottom, option in zip((2, 3, 4), t_options):
        if option[0] == "H":
            assignment.add(instance["orientation_variables"][bottom])
    base_variables = (
        set(instance["edge_variables"].values())
        | set(instance["t_variables"].values())
        | set(instance["orientation_variables"].values())
    )
    assert all(
        any((literal > 0 and literal in assignment)
            or (literal < 0 and -literal not in assignment)
            for literal in clause)
        for clause in base_clauses
    )
    assert all(abs(literal) in base_variables
               for clause in base_clauses for literal in clause)

    results = {}
    for solver_name in ("cadical195", "glucose4", "minisat22"):
        with Solver(name=solver_name, bootstrap_with=base_clauses) as solver:
            base_answer = solver.solve()
        with Solver(name=solver_name, bootstrap_with=instance["clauses"]) as solver:
            full_answer = solver.solve()
            stats = solver.accum_stats()
        results[solver_name] = {
            "base_without_pair_upper": "SAT" if base_answer else "UNSAT",
            "full_with_pair_upper": "SAT" if full_answer else "UNSAT",
            "full_stats": stats,
        }
        assert base_answer is True
        assert full_answer is False

    result = {
        "status": "INDEPENDENT_CNF_CONTROLS_COMPLETE",
        "inputs": {str(INPUT): sha256(INPUT), str(VERTEX_INPUT): sha256(VERTEX_INPUT)},
        "control_mask_hex": record[0],
        "variables": instance["variables"],
        "base_clauses": len(base_clauses),
        "full_clauses": len(instance["clauses"]),
        "stored_combinatorial_witness_satisfies_every_base_clause": True,
        "solver_crosscheck": results,
        "conclusion": (
            "The H/F, target-load and exceptional-recurrence CNF is SAT, but "
            "the independently direct pair-upper layer makes this control "
            "instance UNSAT in three solver engines."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
