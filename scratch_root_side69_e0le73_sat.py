"""Search the rooted exact CNF with S<=69 and E0<=73.

The side bound is supplied by ``scratch_root_side_bound_selfcontained.md``.
The additional E0 bound uses the independently audited computational
eliminations of E0=74,...,84.  Those solver negatives have no DRAT/LRAT proof
certificates, so this is a search-strengthening rather than a formal theorem.
A SAT answer is always decoded and checked directly on all 99 vertices.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

from scratch_general_exact_sat import coordinates, verify
from scratch_general_triangle_portfolio import branch_specs
from scratch_root_side_bound_sat import header, sha256


INPUT_CNF = Path("scratch_root_side_le69.cnf")
INPUT_META = Path("scratch_root_side_le69_build.json")
OUTPUT_CNF = Path("scratch_root_side69_e0le73.cnf")
OUTPUT_META = Path("scratch_root_side69_e0le73_build.json")
PORTFOLIO = Path("scratch_root_side69_e0le73_portfolio.json")


def local_variables() -> list[int]:
    labels, _index, variables, _edge = coordinates()
    result = []
    for (u, v), variable in variables.items():
        supports_u = tuple(sorted(symbol // 2 for symbol in labels[u]))
        supports_v = tuple(sorted(symbol // 2 for symbol in labels[v]))
        if supports_u == supports_v:
            result.append(variable)
    assert len(result) == 21 * 6 == 126
    assert len(set(result)) == len(result)
    return sorted(result)


def build() -> dict:
    from pysat.card import CardEnc, EncType

    input_meta = json.loads(INPUT_META.read_text(encoding="utf-8"))
    input_hash = sha256(INPUT_CNF)
    assert input_hash == input_meta["cnf_sha256"]
    input_variables, input_clauses = header(INPUT_CNF)
    assert (input_variables, input_clauses) == (
        input_meta["variables"], input_meta["clauses"]
    )

    local = local_variables()
    card = CardEnc.atmost(
        local, bound=73, top_id=input_variables, encoding=EncType.seqcounter
    )
    variables = max(input_variables, card.nv)
    clauses = input_clauses + len(card.clauses)
    with OUTPUT_CNF.open("w", encoding="ascii", newline="\n") as target:
        target.write(f"p cnf {variables} {clauses}\n")
        with INPUT_CNF.open("r", encoding="ascii") as source:
            next(source)
            for line in source:
                target.write(line)
        for clause in card.clauses:
            target.write(" ".join(map(str, clause)) + " 0\n")
    assert header(OUTPUT_CNF) == (variables, clauses)
    assert sum(1 for _ in OUTPUT_CNF.open("r", encoding="ascii")) == clauses + 1

    source_proof = Path("scratch_root_side_bound_selfcontained.json")
    proof_payload = json.loads(source_proof.read_text(encoding="utf-8"))
    assert proof_payload["status"] == "ARITHMETIC_VERIFIED"
    assert proof_payload["prism_and_root_side"]["some_root_side_ceiling"] == 69

    result = {
        "status": "BUILT_SEARCH_STRENGTHENING",
        "model": "exact rooted CNF with S<=69 and computational E0<=73",
        "input_cnf": str(INPUT_CNF),
        "input_cnf_sha256": input_hash,
        "side_bound_source": str(source_proof),
        "side_bound_source_sha256": hashlib.sha256(
            source_proof.read_bytes()
        ).hexdigest().upper(),
        "side_bound": 69,
        "e0_bound": 73,
        "e0_variable_count": len(local),
        "e0_variables": local,
        "cardinality_encoding": "PySAT sequential counter",
        "added_variables": variables - input_variables,
        "added_clauses": len(card.clauses),
        "variables": variables,
        "clauses": clauses,
        "cnf_sha256": sha256(OUTPUT_CNF),
        "computational_premises": [
            "audited exclusions of rooted E0=75,...,84",
            "audited terminal UNSAT for all 188 E0=74,Q>=5 local orbits",
        ],
        "proof_certificate_for_computational_premises": False,
        "claim_boundary": (
            "This CNF is a candidate-search restriction. SAT is accepted only "
            "after direct 99-vertex verification. UNSAT is not a formal "
            "nonexistence proof because inherited solver negatives have no "
            "DRAT/LRAT certificates."
        ),
    }
    OUTPUT_META.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def sweep(conflicts: int) -> dict:
    from pysat.formula import CNF
    from pysat.solvers import Solver

    meta = json.loads(OUTPUT_META.read_text(encoding="utf-8"))
    assert sha256(OUTPUT_CNF) == meta["cnf_sha256"]
    specs, coverage = branch_specs()
    formula = CNF(from_file=str(OUTPUT_CNF))
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
                "status": (
                    "SAT" if answer is True else
                    "UNSAT" if answer is False else "UNKNOWN"
                ),
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
                Path("scratch_root_side69_e0le73_solution.json").write_text(
                    json.dumps(verified, indent=2) + "\n", encoding="utf-8"
                )
                break
            PORTFOLIO.write_text(json.dumps({
                "status": "IN_PROGRESS", "records": records,
            }, indent=2) + "\n", encoding="utf-8")
    counts = {
        status: sum(row["status"] == status for row in records)
        for status in ("SAT", "UNSAT", "UNKNOWN")
    }
    status = (
        "SAT" if counts["SAT"] else
        "UNSAT" if len(records) == len(specs) and counts["UNSAT"] == len(specs)
        else "UNKNOWN"
    )
    result = {
        "status": status,
        "model": meta["model"],
        "cnf": str(OUTPUT_CNF),
        "cnf_sha256": meta["cnf_sha256"],
        "conflict_budget_per_branch": conflicts,
        "solver": "CaDiCaL 1.9.5 via one incremental PySAT instance",
        "coverage": coverage,
        "counts": counts,
        "elapsed_seconds": time.monotonic() - started,
        "records": records,
        "claim_boundary": meta["claim_boundary"],
    }
    PORTFOLIO.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--sweep", action="store_true")
    parser.add_argument("--conflicts", type=int, default=20_000)
    args = parser.parse_args()
    if args.build or not OUTPUT_CNF.exists():
        print(json.dumps(build(), sort_keys=True), flush=True)
    if args.sweep:
        result = sweep(args.conflicts)
        print(json.dumps({"status": result["status"], "counts": result["counts"]}))


if __name__ == "__main__":
    main()
