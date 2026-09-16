"""Corrected conditional rooted SAT experiment with at most 69 fibre sides.

This file is deliberately separate from the quarantined low-E0 experiment.
For a root r, ``S(r)`` counts only the four square-side positions in each of
the 21 same-support fibres.  It does *not* count the two fibre diagonals.

The internal double count gives ``sum_r S(r) = 6 P``.  If one additionally
accepts the external, independently published project premises
``n3 >= 708`` and ``n3 + 3 P = 4158``, then some root has ``S(r) <= 69``.
Accordingly, a negative solve is conditional on those external premises.
Any positive solve is unconditional after the full 99-vertex verifier.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

from scratch_general_exact_sat import coordinates, verify
from scratch_general_triangle_portfolio import branch_specs


BASE_CNF = Path("scratch_general_exact.cnf")
BASE_META = Path("scratch_general_exact_build.json")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def header(path: Path) -> tuple[int, int]:
    with path.open("r", encoding="ascii") as handle:
        fields = handle.readline().split()
    if len(fields) != 4 or fields[:2] != ["p", "cnf"]:
        raise ValueError(fields)
    return int(fields[2]), int(fields[3])


def side_variables() -> list[int]:
    labels, _index, variables, _edge = coordinates()
    result = []
    for (u, v), variable in variables.items():
        supports_u = tuple(sorted(symbol // 2 for symbol in labels[u]))
        supports_v = tuple(sorted(symbol // 2 for symbol in labels[v]))
        same_fibre = supports_u == supports_v
        exact_overlap = len(set(labels[u]) & set(labels[v]))
        if same_fibre and exact_overlap == 1:
            result.append(variable)
    assert len(result) == 21 * 4 == 84
    assert len(set(result)) == len(result)
    return sorted(result)


def diagonal_variables() -> list[int]:
    labels, _index, variables, _edge = coordinates()
    result = []
    for (u, v), variable in variables.items():
        supports_u = tuple(sorted(symbol // 2 for symbol in labels[u]))
        supports_v = tuple(sorted(symbol // 2 for symbol in labels[v]))
        if supports_u == supports_v and not set(labels[u]) & set(labels[v]):
            result.append(variable)
    assert len(result) == 21 * 2 == 42
    return sorted(result)


def build(bound: int, output: Path, metadata_path: Path) -> dict:
    from pysat.card import CardEnc, EncType

    if bound != 69:
        raise ValueError(
            "the external n3/P premise used here derives only the bound 69"
        )
    base_meta = json.loads(BASE_META.read_text(encoding="utf-8"))
    base_hash = sha256(BASE_CNF)
    assert base_hash == base_meta["cnf_sha256"]
    base_variables, base_clauses = header(BASE_CNF)
    assert (base_variables, base_clauses) == (
        base_meta["variables"], base_meta["clauses"]
    )

    sides = side_variables()
    diagonals = diagonal_variables()
    assert not set(sides) & set(diagonals)
    card = CardEnc.atmost(
        sides, bound=bound, top_id=base_variables, encoding=EncType.seqcounter
    )
    variables = max(base_variables, card.nv)
    clauses = base_clauses + len(card.clauses)
    with output.open("w", encoding="ascii", newline="\n") as target:
        target.write(f"p cnf {variables} {clauses}\n")
        with BASE_CNF.open("r", encoding="ascii") as source:
            next(source)
            for line in source:
                target.write(line)
        for clause in card.clauses:
            target.write(" ".join(map(str, clause)) + " 0\n")
    assert header(output) == (variables, clauses)
    assert sum(1 for _ in output.open("r", encoding="ascii")) == clauses + 1

    metadata = {
        "status": "BUILT",
        "model": "exact rooted CNF plus corrected conditional side-edge bound",
        "base_cnf": str(BASE_CNF),
        "base_cnf_sha256": base_hash,
        "external_premises_not_replayed_here": [
            "n3 >= 708", "n3 + 3 P = 4158",
        ],
        "internal_bridge": "sum over roots of S(r) = 6 P",
        "derived_root_choice": "some root has S(r) <= 69",
        "encoded_quantity": "S(r): same-fibre square sides only",
        "bound": bound,
        "side_variable_count": len(sides),
        "diagonal_variable_count_excluded_from_cardinality": len(diagonals),
        "side_variables": sides,
        "diagonal_variables_not_bounded": diagonals,
        "cardinality_encoding": "PySAT sequential counter",
        "added_variables": variables - base_variables,
        "added_clauses": len(card.clauses),
        "variables": variables,
        "clauses": clauses,
        "cnf_sha256": sha256(output),
        "claim_boundary": (
            "UNSAT would be conditional on the two external n3/P premises; "
            "SAT is accepted only after direct verification of all 99 vertices."
        ),
    }
    metadata_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return metadata


def sweep(cnf_path: Path, meta_path: Path, output: Path, conflicts: int) -> dict:
    from pysat.formula import CNF
    from pysat.solvers import Solver

    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    assert sha256(cnf_path) == meta["cnf_sha256"]
    specs, coverage = branch_specs()
    formula = CNF(from_file=str(cnf_path))
    records = []
    verified = None
    started = time.monotonic()
    with Solver(name="cadical195", bootstrap_with=formula.clauses) as solver:
        for index, spec in enumerate(specs):
            before = solver.accum_stats()
            tick = time.monotonic()
            solver.conf_budget(conflicts)
            answer = solver.solve_limited(assumptions=spec["assumptions"])
            after = solver.accum_stats()
            record = {
                "branch_index": index,
                "branch": spec["branch"],
                "base": spec["base"],
                "w_label": spec["w_label"],
                "orbit_size": spec["orbit_size"],
                "assumptions": spec["assumptions"],
                "status": "SAT" if answer is True else "UNSAT" if answer is False else "UNKNOWN",
                "solve_seconds": time.monotonic() - tick,
                "stats_delta": {
                    key: after.get(key, 0) - before.get(key, 0)
                    for key in set(before) | set(after)
                },
            }
            records.append(record)
            print(json.dumps(record, sort_keys=True), flush=True)
            if answer is True:
                model = solver.get_model()
                positive = {lit for lit in model if 0 < lit <= 3486}
                verified = verify(positive)
                record["verification"] = {
                    key: value for key, value in verified.items() if key != "edges"
                }
                if not verified["ok"]:
                    raise AssertionError(record["verification"])
                Path(f"scratch_root_side_le{meta['bound']}_solution.json").write_text(
                    json.dumps(verified, indent=2) + "\n", encoding="utf-8"
                )
                break
            output.write_text(json.dumps({
                "status": "IN_PROGRESS", "records": records,
            }, indent=2) + "\n", encoding="utf-8")
    counts = {
        status: sum(r["status"] == status for r in records)
        for status in ("SAT", "UNSAT", "UNKNOWN")
    }
    overall = (
        "SAT" if counts["SAT"] else
        "UNSAT" if len(records) == len(specs) and counts["UNSAT"] == len(specs) else
        "UNKNOWN"
    )
    result = {
        "status": overall,
        "model": meta["model"],
        "cnf": str(cnf_path),
        "cnf_sha256": meta["cnf_sha256"],
        "bound": meta["bound"],
        "external_premises_not_replayed_here": meta["external_premises_not_replayed_here"],
        "solver": "CaDiCaL 1.9.5 via one incremental PySAT instance",
        "conflict_budget_per_branch": conflicts,
        "branches_exhaustive_under_external_premises": True,
        "coverage": coverage,
        "counts": counts,
        "elapsed_seconds": time.monotonic() - started,
        "records": records,
        "claim_boundary": meta["claim_boundary"],
    }
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bound", type=int, default=69)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--sweep", action="store_true")
    parser.add_argument("--conflicts", type=int, default=5000)
    args = parser.parse_args()
    cnf = Path(f"scratch_root_side_le{args.bound}.cnf")
    meta = Path(f"scratch_root_side_le{args.bound}_build.json")
    portfolio = Path(f"scratch_root_side_le{args.bound}_portfolio.json")
    if args.build or not cnf.exists():
        print(json.dumps(build(args.bound, cnf, meta), sort_keys=True), flush=True)
    if args.sweep:
        result = sweep(cnf, meta, portfolio, args.conflicts)
        print(json.dumps({"status": result["status"], "counts": result["counts"]}), flush=True)


if __name__ == "__main__":
    main()
