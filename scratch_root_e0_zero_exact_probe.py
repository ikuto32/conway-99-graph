"""Targeted exact-CNF probe of the single rooted E0=0 local condition.

This is not an exhaustive E0<=71 sweep.  It reuses the independently checked
unrestricted rooted CNF and adds the 126 unit assumptions saying that every
edge inside each of the 21 four-vertex support fibres is absent.  A fixed
disjoint-support edge is a safe symmetry normalization.

UNSAT without a proof trace is only a finite-computational result; UNKNOWN is
only a diagnostic.  A SAT result is expanded through the existing independent
99-vertex verifier and is never written to submission.txt automatically.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import time
from pathlib import Path


OUTPUT_PATH = Path("scratch_root_e0_zero_exact_probe.json")
ENCODINGS = {
    "v1": (
        Path("scratch_general_exact.cnf"),
        Path("scratch_general_exact_build.json"),
        "91D22E62625E1221DD46B819E89494DB8141DD4DDC9A06F13B9ABDB530B83242",
    ),
    "v2": (
        Path("scratch_general_sat_v2.cnf"),
        Path("scratch_general_sat_v2_build.json"),
        "A8F13D204400C41D4724EC97EA98D84CA616939A9F878C42D5219553664E0A81",
    ),
}


def coordinates():
    labels = [
        pair
        for pair in itertools.combinations(range(14), 2)
        if pair[0] // 2 != pair[1] // 2
    ]
    index = {label: position for position, label in enumerate(labels)}
    variables = {
        pair: identifier
        for identifier, pair in enumerate(itertools.combinations(range(84), 2), 1)
    }

    def edge(left: int, right: int) -> int:
        return variables[tuple(sorted((left, right)))]

    return labels, index, variables, edge


def e0_zero_assumptions() -> tuple[list[int], dict[str, object]]:
    labels, index, variables, edge = coordinates()
    fibres: dict[tuple[int, int], list[int]] = {}
    for vertex, label in enumerate(labels):
        support = tuple(sorted((label[0] // 2, label[1] // 2)))
        fibres.setdefault(support, []).append(vertex)
    assert len(fibres) == 21 and all(len(vertices) == 4 for vertices in fibres.values())
    same_fibre = sorted(
        edge(left, right)
        for vertices in fibres.values()
        for left, right in itertools.combinations(vertices, 2)
    )
    assert len(same_fibre) == len(set(same_fibre)) == 126

    # Any outer vertex has at least eight disjoint-support neighbours.  The
    # scaffold stabilizer is transitive on ordered disjoint-support pairs.
    fixed_left = index[(0, 2)]
    fixed_right = index[(4, 6)]
    fixed_disjoint_edge = edge(fixed_left, fixed_right)
    assert fixed_disjoint_edge not in same_fibre
    assumptions = [fixed_disjoint_edge] + [-literal for literal in same_fibre]
    return assumptions, {
        "outer_labels": len(labels),
        "edge_variables": len(variables),
        "support_fibres": len(fibres),
        "same_fibre_edges_forbidden": len(same_fibre),
        "fixed_disjoint_edge_variable": fixed_disjoint_edge,
        "assumption_count": len(assumptions),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--conflicts", type=int, default=100_000)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--output", type=Path, default=OUTPUT_PATH)
    parser.add_argument("--encoding", choices=tuple(ENCODINGS), default="v1")
    args = parser.parse_args()

    cnf_path, build_path, expected_sha256 = ENCODINGS[args.encoding]
    assert cnf_path.is_file() and build_path.is_file()
    digest = hashlib.sha256(cnf_path.read_bytes()).hexdigest().upper()
    assert digest == expected_sha256
    build = json.loads(build_path.read_text(encoding="utf-8"))
    assert build["cnf_sha256"] == expected_sha256
    assumptions, assumption_meta = e0_zero_assumptions()

    from pysat.formula import CNF
    from pysat.solvers import Solver

    started = time.monotonic()
    formula = CNF(from_file=str(cnf_path))
    loaded = time.monotonic()
    with Solver(name=args.solver, bootstrap_with=formula.clauses) as solver:
        propagation_ok, propagated = solver.propagate(assumptions=assumptions)
        if propagation_ok:
            solver.conf_budget(args.conflicts)
            answer = solver.solve_limited(assumptions=assumptions)
        else:
            answer = False
        model = solver.get_model() if answer is True else None
        stats = solver.accum_stats()
    finished = time.monotonic()

    result: dict[str, object] = {
        "status": "SAT" if answer is True else "UNSAT" if answer is False else "UNKNOWN",
        "scope": "single exact rooted E0=0 branch; not an E0<=71 layer sweep",
        "encoding": args.encoding,
        "cnf": str(cnf_path),
        "cnf_sha256": digest,
        "solver": args.solver,
        "conflict_budget": args.conflicts,
        "propagation_ok": propagation_ok,
        "propagated_literal_count": len(propagated),
        "load_seconds": round(loaded - started, 3),
        "solve_seconds": round(finished - loaded, 3),
        "assumptions": assumption_meta,
        "stats": stats,
        "proof_artifact": None,
        "claim_boundary": (
            "UNSAT is not promoted to a formal theorem without DRAT/LRAT; "
            "UNKNOWN is not evidence of satisfiability."
        ),
    }
    if model is not None:
        positive = {literal for literal in model if 0 < literal <= 3486}
        from scratch_general_exact_sat import verify

        checked = verify(positive)
        result["verification"] = {key: value for key, value in checked.items() if key != "edges"}
        result["positive_edge_variables"] = sorted(positive) if checked["ok"] else []
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
