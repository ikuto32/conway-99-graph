"""QUARANTINED: an unsound proposed low-E0 conditioning experiment.

The prism bijection counts only the four side positions in each fibre, while
E0 and this script's 126 variables count all six positions, including two
allowed diagonals. Thus the external prism bound does not imply E0<=69.

The generated scratch_root_e0_le69.cnf was never solved. main() now refuses
all execution so this unsupported restriction cannot accidentally be used.
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


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def fibre_edge_variables() -> list[int]:
    labels, _index, variables, _edge = coordinates()
    result = []
    for (u, v), variable in variables.items():
        support_u = tuple(sorted(symbol // 2 for symbol in labels[u]))
        support_v = tuple(sorted(symbol // 2 for symbol in labels[v]))
        if support_u == support_v:
            result.append(variable)
    assert len(result) == 21 * 6 == 126
    assert len(result) == len(set(result))
    return sorted(result)


def read_header(path: Path) -> tuple[int, int]:
    with path.open("r", encoding="ascii") as handle:
        fields = handle.readline().split()
    if len(fields) != 4 or fields[:2] != ["p", "cnf"]:
        raise ValueError(f"bad DIMACS header: {fields}")
    return int(fields[2]), int(fields[3])


def build(bound: int, output: Path, metadata: Path) -> dict[str, object]:
    from pysat.card import CardEnc, EncType

    if not 0 <= bound <= 84:
        raise ValueError(bound)
    base_meta = json.loads(BASE_META.read_text(encoding="utf-8"))
    base_hash = file_sha256(BASE_CNF)
    if base_hash != base_meta["cnf_sha256"]:
        raise AssertionError((base_hash, base_meta["cnf_sha256"]))
    base_variables, base_clauses = read_header(BASE_CNF)
    if (base_variables, base_clauses) != (
        base_meta["variables"], base_meta["clauses"]
    ):
        raise AssertionError("base DIMACS metadata mismatch")

    fibre_variables = fibre_edge_variables()
    card = CardEnc.atmost(
        fibre_variables,
        bound=bound,
        top_id=base_variables,
        encoding=EncType.seqcounter,
    )
    new_variables = max(base_variables, card.nv)
    new_clauses = base_clauses + len(card.clauses)
    with output.open("w", encoding="ascii", newline="\n") as target:
        target.write(f"p cnf {new_variables} {new_clauses}\n")
        with BASE_CNF.open("r", encoding="ascii") as source:
            next(source)
            for line in source:
                target.write(line)
        for clause in card.clauses:
            target.write(" ".join(map(str, clause)) + " 0\n")

    actual_variables, actual_clauses = read_header(output)
    line_count = sum(1 for _ in output.open("r", encoding="ascii"))
    if (actual_variables, actual_clauses) != (new_variables, new_clauses):
        raise AssertionError("written header mismatch")
    if line_count != new_clauses + 1:
        raise AssertionError((line_count, new_clauses))
    record = {
        "model": "exact rooted CNF plus conditional low-E0 cardinality",
        "base_cnf": str(BASE_CNF),
        "base_cnf_sha256": base_hash,
        "external_premise": "n3>=708 and n3+3P=4158",
        "internal_bridge": "sum_r E0(r)=6P",
        "bound": bound,
        "fibre_edge_variable_count": len(fibre_variables),
        "fibre_edge_variables": fibre_variables,
        "cardinality_encoding": "PySAT sequential counter",
        "added_variables": new_variables - base_variables,
        "added_clauses": len(card.clauses),
        "variables": new_variables,
        "clauses": new_clauses,
        "dimacs_line_count": line_count,
        "cnf_sha256": file_sha256(output),
        "claim_boundary": (
            "Negative results are conditional on the external n3 bound; "
            "SAT witnesses are always checked directly."
        ),
    }
    metadata.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record


def sweep(
    cnf_path: Path,
    metadata_path: Path,
    output: Path,
    conflict_budget: int,
) -> dict[str, object]:
    from pysat.formula import CNF
    from pysat.solvers import Solver

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if file_sha256(cnf_path) != metadata["cnf_sha256"]:
        raise AssertionError("conditioned CNF hash mismatch")
    specs, coverage = branch_specs()
    started = time.monotonic()
    formula = CNF(from_file=str(cnf_path))
    loaded = time.monotonic()
    records = []
    verified = None
    with Solver(name="cadical195", bootstrap_with=formula.clauses) as solver:
        for branch_index, spec in enumerate(specs):
            before = solver.accum_stats()
            solve_started = time.monotonic()
            solver.conf_budget(conflict_budget)
            answer = solver.solve_limited(assumptions=spec["assumptions"])
            after = solver.accum_stats()
            model = solver.get_model() if answer is True else None
            record = {
                "branch_index": branch_index,
                "branch": spec["branch"],
                "base": spec["base"],
                "w_label": spec["w_label"],
                "orbit_size": spec["orbit_size"],
                "assumptions": spec["assumptions"],
                "status": (
                    "SAT" if answer is True else "UNSAT" if answer is False else "UNKNOWN"
                ),
                "solve_seconds": round(time.monotonic() - solve_started, 3),
                "stats_delta": {
                    key: after.get(key, 0) - before.get(key, 0)
                    for key in set(before) | set(after)
                },
            }
            records.append(record)
            output.write_text(json.dumps({
                "model": metadata["model"],
                "bound": metadata["bound"],
                "conflict_budget_per_branch": conflict_budget,
                "status": "IN_PROGRESS",
                "completed": len(records),
                "total": len(specs),
                "records": records,
            }, indent=2) + "\n", encoding="utf-8")
            print(json.dumps(record, sort_keys=True), flush=True)
            if answer is True:
                positive = {lit for lit in model if 0 < lit <= 3486}
                verified = verify(positive)
                record["verification"] = {
                    key: value for key, value in verified.items() if key != "edges"
                }
                if not verified["ok"]:
                    raise AssertionError(record["verification"])
                witness_path = Path(f"scratch_root_e0_le{metadata['bound']}_solution.json")
                witness_path.write_text(
                    json.dumps(verified, indent=2) + "\n", encoding="utf-8"
                )
                break

    counts = {
        status: sum(record["status"] == status for record in records)
        for status in ("SAT", "UNSAT", "UNKNOWN")
    }
    status = (
        "SAT" if counts["SAT"]
        else "UNSAT" if len(records) == len(specs) and counts["UNSAT"] == len(specs)
        else "UNKNOWN"
    )
    result = {
        "model": metadata["model"],
        "cnf": str(cnf_path),
        "cnf_sha256": metadata["cnf_sha256"],
        "bound": metadata["bound"],
        "external_premise": metadata["external_premise"],
        "conflict_budget_per_branch": conflict_budget,
        "solver": "CaDiCaL 1.9.5 via one incremental PySAT instance",
        "load_seconds": round(loaded - started, 3),
        "solve_seconds": round(time.monotonic() - loaded, 3),
        "branches_exhaustive_under_premise": True,
        "branch_count": len(specs),
        "coverage": coverage,
        "status": status,
        "counts": counts,
        "records": records,
        "claim_boundary": metadata["claim_boundary"],
    }
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    raise SystemExit(
        "QUARANTINED: prism counting bounds fibre side edges S, not "
        "E0=S+diagonal edges; the proposed E0<=69 restriction is unsupported"
    )
    parser = argparse.ArgumentParser()
    parser.add_argument("--bound", type=int, default=69)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--sweep", action="store_true")
    parser.add_argument("--conflicts", type=int, default=2000)
    args = parser.parse_args()
    cnf = Path(f"scratch_root_e0_le{args.bound}.cnf")
    metadata = Path(f"scratch_root_e0_le{args.bound}_build.json")
    output = Path(f"scratch_root_e0_le{args.bound}_portfolio.json")
    if args.build or not cnf.exists():
        print(json.dumps(build(args.bound, cnf, metadata), sort_keys=True), flush=True)
    if args.sweep:
        result = sweep(cnf, metadata, output, args.conflicts)
        print(json.dumps({"status": result["status"], "counts": result["counts"]}), flush=True)


if __name__ == "__main__":
    main()
