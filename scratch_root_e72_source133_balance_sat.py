"""Add the source-133 Gram-saturation pointwise balance to its macro CNF.

For the exceptional K_{2,3}, write A_i={0,i}, B_i={1,i}, i=2,3,4,
and let d be +1 on A and -1 on B.  Let e be +1 on {1,5},{1,6},
-1 on {0,5},{0,6}, and zero elsewhere.  The exact Gram-saturation argument
in ``scratch_theory_e72_k23_balance.md`` gives the two pointwise identities

    B d = 3 e,             B e = 2 d + e.

The first includes the 68 zero A/B balances.  This script encodes both
identities on top of the full-Gram macro selector CNF.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
from pathlib import Path
import shutil
import sys
import time

from scratch_general_exact_sat import coordinates, verify


SOURCE_CNF = Path("scratch_root_e72_source133_full_gram_macro.cnf")
SOURCE_BUILD = Path("scratch_root_e72_source133_full_gram_macro_build.json")
THEORY_AUDIT = Path("scratch_theory_e72_k23_balance_audit.json")
OUTPUT_CNF = Path("scratch_root_e72_source133_balance.cnf")
BUILD_OUTPUT = Path("scratch_root_e72_source133_balance_build.json")
BITS = tuple(itertools.product((0, 1), repeat=2))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def atomic_json(path: Path, value) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def local_label(support, bits):
    return tuple(sorted((2 * support[0] + bits[0], 2 * support[1] + bits[1])))


def build():
    dependency_root = str(Path(".deps").resolve())
    if dependency_root not in sys.path:
        sys.path.insert(0, dependency_root)
    from pysat.card import CardEnc, EncType
    from pysat.formula import IDPool

    source_build_raw = SOURCE_BUILD.read_bytes()
    source_build = json.loads(source_build_raw)
    assert source_build["source_row_index"] == 133
    assert Path(source_build["cnf"]) == SOURCE_CNF
    assert sha256(SOURCE_CNF) == source_build["cnf_audit"]["sha256"]
    theory = None
    if THEORY_AUDIT.exists():
        theory = json.loads(THEORY_AUDIT.read_text(encoding="utf-8"))
        assert theory["status"] in (
            "EXACT_SUPPORT_ARITHMETIC_VERIFIED",
            "EXACT_ARITHMETIC_VERIFIED",
            "INDEPENDENT_EXACT_VERIFIED",
        )

    labels, index, variables, edge = coordinates()
    del index
    A_labels = tuple(
        local_label((0, group), bits)
        for group in (2, 3, 4) for bits in BITS
    )
    B_labels = tuple(
        local_label((1, group), bits)
        for group in (2, 3, 4) for bits in BITS
    )
    assert len(A_labels) == len(set(A_labels)) == 12
    assert len(B_labels) == len(set(B_labels)) == 12
    assert not (set(A_labels) & set(B_labels))
    label_index = {label: position for position, label in enumerate(labels)}
    A = tuple(label_index[label] for label in A_labels)
    B = tuple(label_index[label] for label in B_labels)
    top_outside_supports = frozenset({(0, 5), (0, 6), (1, 5), (1, 6)})
    balanced_vertices = [
        x for x, label in enumerate(labels)
        if tuple(sorted(symbol // 2 for symbol in label)) not in top_outside_supports
    ]
    excluded_vertices = sorted(set(range(84)) - set(balanced_vertices))
    assert len(balanced_vertices) == 68 and len(excluded_vertices) == 16
    E_minus_labels = tuple(
        local_label(support, bits)
        for support in ((0, 5), (0, 6)) for bits in BITS
    )
    E_plus_labels = tuple(
        local_label(support, bits)
        for support in ((1, 5), (1, 6)) for bits in BITS
    )
    E_minus = tuple(label_index[label] for label in E_minus_labels)
    E_plus = tuple(label_index[label] for label in E_plus_labels)
    assert len(E_minus) == len(E_plus) == 8
    assert not (set(E_minus) & set(E_plus))

    old_variables = int(source_build["cnf_audit"]["declared_variables"])
    old_clauses = int(source_build["cnf_audit"]["declared_clauses"])
    pool = IDPool(start_from=old_variables + 1)
    clauses = []
    arity_histogram = {}
    constraint_rows = []

    def add_signed_neighbour_row(name, x, positive_vertices, negative_vertices, rhs):
        positive_literals = tuple(edge(x, y) for y in positive_vertices if y != x)
        negative_literals = tuple(edge(x, y) for y in negative_vertices if y != x)
        assert not (set(positive_literals) & set(negative_literals))
        # sum(P)-sum(N)=rhs iff sum(P)+sum(not N)=|N|+rhs.
        literals = [*positive_literals, *(-value for value in negative_literals)]
        bound = len(negative_literals) + rhs
        assert 0 <= bound <= len(literals)
        encoded = CardEnc.equals(
            lits=literals,
            bound=bound,
            vpool=pool,
            encoding=EncType.seqcounter,
        ).clauses
        clauses.extend(encoded)
        arity_histogram[str(len(literals))] = arity_histogram.get(str(len(literals)), 0) + 1
        constraint_rows.append({
            "identity": name,
            "vertex_index": x,
            "label": list(labels[x]),
            "positive_terms": len(positive_literals),
            "negative_terms": len(negative_literals),
            "rhs": rhs,
            "bound": bound,
            "encoding_clauses": len(encoded),
        })

    # B d = 3 e.  Encoding all 84 rows makes the already forced top rows
    # explicit and gives the sequential counters useful propagation support.
    for x in range(84):
        rhs = 3 if x in E_plus else -3 if x in E_minus else 0
        add_signed_neighbour_row("Bd=3e", x, A, B, rhs)
    # B e = 2 d + e, a second exact consequence of the saturated norm.
    for x in range(84):
        d_value = 1 if x in A else -1 if x in B else 0
        e_value = 1 if x in E_plus else -1 if x in E_minus else 0
        add_signed_neighbour_row("Be=2d+e", x, E_plus, E_minus, 2 * d_value + e_value)
    assert len(constraint_rows) == 168
    variables_total = max(old_variables, pool.top)
    clauses_total = old_clauses + len(clauses)
    temporary = OUTPUT_CNF.with_suffix(OUTPUT_CNF.suffix + f".{os.getpid()}.tmp")
    with SOURCE_CNF.open("rb") as source, temporary.open("wb") as target:
        header = source.readline().split()
        assert header == [
            b"p", b"cnf", str(old_variables).encode(), str(old_clauses).encode()
        ]
        target.write(f"p cnf {variables_total} {clauses_total}\n".encode("ascii"))
        shutil.copyfileobj(source, target, length=1 << 20)
        for clause in clauses:
            target.write((" ".join(map(str, clause)) + " 0\n").encode("ascii"))
    temporary.replace(OUTPUT_CNF)
    result = {
        "status": "BUILD_COMPLETE",
        "model": "source133 full-Gram macro CNF plus pointwise A/B balance",
        "source_cnf": str(SOURCE_CNF),
        "source_cnf_sha256": sha256(SOURCE_CNF),
        "source_build": str(SOURCE_BUILD),
        "source_build_sha256": hashlib.sha256(source_build_raw).hexdigest().upper(),
        "theory_audit": str(THEORY_AUDIT) if THEORY_AUDIT.exists() else None,
        "theory_audit_sha256": sha256(THEORY_AUDIT) if THEORY_AUDIT.exists() else None,
        "balanced_vertices": len(balanced_vertices),
        "excluded_top_outside_vertices": len(excluded_vertices),
        "top_outside_supports": [list(value) for value in sorted(top_outside_supports)],
        "balance_arity_histogram": arity_histogram,
        "signed_neighbour_identity_rows": constraint_rows,
        "Bd_equals_3e_rows": 84,
        "Be_equals_2d_plus_e_rows": 84,
        "added_auxiliary_variables": variables_total - old_variables,
        "added_clauses": len(clauses),
        "variables": variables_total,
        "clauses": clauses_total,
        "cnf": str(OUTPUT_CNF),
        "cnf_sha256": sha256(OUTPUT_CNF),
        "macro_branches": source_build["macro_branches"],
        "labelled_coverage": source_build["macro_audit"]["passing_labelled_state_matching_coverage"],
        "claim_boundary": (
            "Soundness of the 68 balance equations is supplied by the separately "
            "audited source-133 Gram-saturation lemma."
        ),
    }
    atomic_json(BUILD_OUTPUT, result)
    return result


def solve(conflicts: int, output: Path):
    dependency_root = str(Path(".deps").resolve())
    if dependency_root not in sys.path:
        sys.path.insert(0, dependency_root)
    from pysat.formula import CNF
    from pysat.solvers import Solver

    build_doc = build()
    started = time.monotonic()
    formula = CNF(from_file=str(OUTPUT_CNF))
    loaded = time.monotonic()
    with Solver(name="cadical195", bootstrap_with=formula.clauses) as solver:
        if conflicts:
            solver.conf_budget(conflicts)
            answer = solver.solve_limited(expect_interrupt=True)
        else:
            answer = solver.solve()
        solved = time.monotonic()
        stats = solver.accum_stats()
        model = solver.get_model() if answer is True else None
    status = "SAT" if answer is True else "UNSAT" if answer is False else "UNKNOWN"
    verification = None
    if model is not None:
        positive = {literal for literal in model if 0 < literal <= 3486}
        verification = verify(positive)
        assert verification["ok"]
        atomic_json(Path("scratch_root_e72_source133_balance_verified_solution.json"), verification)
    result = {
        "status": status,
        "model": build_doc["model"],
        "build": str(BUILD_OUTPUT),
        "build_sha256": sha256(BUILD_OUTPUT),
        "cnf": str(OUTPUT_CNF),
        "cnf_sha256": build_doc["cnf_sha256"],
        "solver": "CaDiCaL 1.9.5 via PySAT",
        "conflict_budget": conflicts or None,
        "parse_seconds": round(loaded - started, 6),
        "solve_seconds": round(solved - loaded, 6),
        "solver_stats": stats,
        "macro_branches": build_doc["macro_branches"],
        "labelled_coverage": build_doc["labelled_coverage"],
        "direct_99_vertex_verification": (
            None if verification is None
            else {key: value for key, value in verification.items() if key != "edges"}
        ),
        "formal_proof_certificate": None,
    }
    atomic_json(output, result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--solve", action="store_true")
    parser.add_argument("--conflicts", type=int, default=1_000_000)
    parser.add_argument(
        "--output", type=Path,
        default=Path("scratch_root_e72_source133_balance_c1000000.json"),
    )
    args = parser.parse_args()
    if args.solve:
        result = solve(args.conflicts, args.output)
        print(json.dumps({
            "status": result["status"],
            "solve_seconds": result["solve_seconds"],
            "stats": result["solver_stats"],
            "coverage": result["labelled_coverage"],
        }, sort_keys=True))
    elif args.build:
        result = build()
        print(json.dumps({
            "status": result["status"],
            "variables": result["variables"],
            "clauses": result["clauses"],
            "added_clauses": result["added_clauses"],
        }, sort_keys=True))
    else:
        parser.error("choose --build or --solve")


if __name__ == "__main__":
    main()
