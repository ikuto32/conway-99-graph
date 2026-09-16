"""Aggregate formal-certificate audit for the E72,Q>=3 small snapshot.

For each of the three surviving support records, independently rebuild the
shared exact CNF, complete branch assumptions, selector clause, and every
selector-to-core implication.  The reconstructed DIMACS hash must equal the
formula checked by the pinned drat-trim executable.  The local enumeration
coverage is hash-bound to ``scratch_root_e72_q3_small_audit.json``.
"""

from __future__ import annotations

import gc
import hashlib
import json
from pathlib import Path

from scratch_incremental_local_exact_sat import build_shared_cnf, normalize_source


INPUT = Path("scratch_general_e72_q3_incremental_small_records.json")
SMALL_AUDIT = Path("scratch_root_e72_q3_small_audit.json")
SMALL_AUDIT_SCRIPT = Path("scratch_root_e72_q3_small_audit.py")
SELECTOR_SCRIPT = Path("scratch_e73_selector_drup.py")
CHECK_SCRIPT = Path("scratch_check_drat.py")
OUTPUT = Path("scratch_root_e72_q3_small_formal_audit.json")
SUMMARY = Path("scratch_root_e72_q3_small_formal_audit.md")
CHECKPOINTS = (
    Path("scratch_general_e72_q3_small_record00_sat_merged.json"),
    Path("scratch_general_e72_q3_small_record01_sat.json"),
    Path("scratch_general_e72_q3_small_record02_sat.json"),
)
PREFIXES = tuple(Path(f"scratch_e72_small_selector_record{index:02d}") for index in range(3))
EXPECTED_BRANCHES = (224, 272, 88)
EXPECTED_LABELLED = (8192, 8192, 8192)
EXPECTED_CHECKER_SHA256 = "10D317DF526C36453986EF09495864BCABD9D02D72D7B772EE78F07939870620"
EXPECTED_CHECKER_SOURCE_SHA256 = "57DF8EFD73FC4FD81C4F255A8A7A1659C80C73AB0829CC8194A65F3432CD3E88"
EXPECTED_CHECKER_COMMIT = "2e3b2dc0ecf938addbd779d42877b6ed69d9a985"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def atomic_json(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def reconstructed_dimacs_sha256(variables: int, clauses: list[list[int]]) -> str:
    digest = hashlib.sha256()
    digest.update(f"p cnf {variables} {len(clauses)}\n".encode("ascii"))
    for clause in clauses:
        digest.update(" ".join(map(str, clause)).encode("ascii"))
        digest.update(b" 0\n")
    return digest.hexdigest().upper()


def audit_record(record_index: int, checkpoint_path: Path, prefix: Path,
                 normalized: dict) -> dict:
    meta_path = prefix.with_suffix(".json")
    cnf_path = prefix.with_suffix(".cnf")
    proof_path = prefix.with_suffix(".drup")
    drat_path = Path(str(prefix) + "_drat_audit.json")
    producer = json.loads(meta_path.read_text(encoding="utf-8"))
    drat = json.loads(drat_path.read_text(encoding="utf-8"))
    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    source = normalize_source(INPUT, record_index)
    clauses, _edge, _variables, _full, branches, shared_meta = build_shared_cnf(source)
    records = checkpoint["records"]

    assert checkpoint["status"] == "UNSAT" and checkpoint["checkpoint_complete"] is True
    assert len(records) == len(branches) == EXPECTED_BRANCHES[record_index]
    assert [row["branch_index"] for row in records] == list(range(len(records)))
    assert sum(int(row["orbit_size"]) for row in records) == EXPECTED_LABELLED[record_index]
    assert source["declared_orbit_count"] == len(branches)
    assert source["local_graph_count"] == EXPECTED_LABELLED[record_index]

    selector_first = shared_meta["variables"] + 1
    selectors = list(range(selector_first, selector_first + len(branches)))
    clauses.append(selectors)
    distinct_cores = set()
    implication_count = 0
    core_size_histogram = {}
    for index, (branch, record, selector) in enumerate(zip(branches, records, selectors)):
        assert branch["branch_index"] == record["branch_index"] == index
        assert branch["representative_id"] == record["representative_id"]
        assert branch["orbit_size"] == record["orbit_size"]
        assert branch["assumption_sha256"] == record["assumption_sha256"]
        assumptions = frozenset(branch["assumptions"])
        core = tuple(map(int, record["assumption_core"]))
        assert core and len(core) == len(set(core)) and set(core) <= assumptions
        assert record["logical_status"] == "UNSAT"
        assert record["status"] in ("UNSAT", "COVERED_UNSAT")
        assert record.get("formal_proof_certificate") is None
        distinct_cores.add(tuple(sorted(core)))
        core_size_histogram[len(core)] = core_size_histogram.get(len(core), 0) + 1
        for literal in core:
            clauses.append([-selector, literal])
            implication_count += 1

    variables = selectors[-1]
    rebuilt_cnf_hash = reconstructed_dimacs_sha256(variables, clauses)
    actual_cnf_hash = sha256(cnf_path)
    actual_proof_hash = sha256(proof_path)
    assert rebuilt_cnf_hash == actual_cnf_hash

    assert producer["status"] == "UNSAT_PROOF_EMITTED_UNCHECKED"
    assert producer["record_index"] == record_index
    assert producer["input"] == str(INPUT)
    assert producer["input_sha256"] == sha256(INPUT)
    assert producer["checkpoint"] == str(checkpoint_path)
    assert producer["checkpoint_sha256"] == sha256(checkpoint_path)
    assert producer["branches_covered"] == len(branches)
    assert producer["labelled_local_graphs_covered"] == EXPECTED_LABELLED[record_index]
    assert producer["selectors"] == len(selectors)
    assert producer["distinct_assumption_cores"] == len(distinct_cores)
    assert producer["selector_core_implications"] == implication_count
    assert producer["shared_variables"] == shared_meta["variables"]
    assert producer["variables"] == variables
    assert producer["clauses"] == len(clauses)
    assert producer["solver"] == "cadical195"
    assert producer["c_stdio_flush_return"] == 0
    assert producer["terminal_empty_clause_present"] is True
    assert producer["terminal_empty_clause_appended_for_external_check"] is False
    assert producer["proof_checked"] is False
    assert producer["cnf"] == str(cnf_path) and producer["cnf_sha256"] == actual_cnf_hash
    assert producer["proof"] == str(proof_path) and producer["proof_sha256"] == actual_proof_hash

    assert drat["status"] == "DRAT_VERIFIED" and drat["ok"] is True
    assert drat["return_code"] == 0 and "s VERIFIED" in drat["transcript"]
    assert drat["cnf"] == str(cnf_path) and drat["cnf_sha256"] == actual_cnf_hash
    assert drat["proof"] == str(proof_path) and drat["proof_sha256"] == actual_proof_hash
    assert drat["producer_metadata"] == str(meta_path)
    assert drat["producer_metadata_sha256"] == sha256(meta_path)
    assert drat["checker_sha256"] == EXPECTED_CHECKER_SHA256
    assert drat["checker_source_sha256"] == EXPECTED_CHECKER_SOURCE_SHA256
    assert drat["checker_upstream_commit"] == EXPECTED_CHECKER_COMMIT

    result = {
        "record_index": record_index,
        "support_form": source["support_form"],
        "branches": len(branches),
        "labelled_local_graphs": EXPECTED_LABELLED[record_index],
        "distinct_assumption_cores": len(distinct_cores),
        "selector_core_implications": implication_count,
        "core_size_histogram": {
            str(size): count for size, count in sorted(core_size_histogram.items())
        },
        "variables": variables,
        "clauses": len(clauses),
        "cnf": str(cnf_path),
        "cnf_sha256": actual_cnf_hash,
        "cnf_rebuilt_byte_for_byte": True,
        "proof": str(proof_path),
        "proof_sha256": actual_proof_hash,
        "proof_bytes": proof_path.stat().st_size,
        "proof_lines": producer["proof_lines"],
        "producer_metadata": str(meta_path),
        "producer_metadata_sha256": sha256(meta_path),
        "checkpoint": str(checkpoint_path),
        "checkpoint_sha256": sha256(checkpoint_path),
        "drat_audit": str(drat_path),
        "drat_audit_sha256": sha256(drat_path),
        "drat_status": drat["status"],
        "checker_elapsed_seconds": drat["elapsed_seconds"],
        "ok": True,
    }
    del clauses, branches
    gc.collect()
    return result


def main() -> None:
    selector_source = SELECTOR_SCRIPT.read_text(encoding="utf-8")
    assert "ucrtbase.dll" in selector_source
    assert "fflush(None)" in selector_source
    assert "cadical195_del" in selector_source
    assert "terminal_empty_clause_appended_for_external_check\": False" in selector_source

    normalized = json.loads(INPUT.read_text(encoding="utf-8"))
    small = json.loads(SMALL_AUDIT.read_text(encoding="utf-8"))
    assert normalized["support_record_count"] == 3
    assert normalized["local_representative_count"] == 584
    assert normalized["labelled_local_graphs_represented"] == 24576
    assert small["status"] == "AUDIT_PASS" and small["ok"] is True
    assert small["all_584_representatives_computationally_unsat"] is True
    assert small["representative_audit"]["support_records"] == 3
    assert small["representative_audit"]["representatives"] == 584
    assert small["representative_audit"]["labelled_local_graphs"] == 24576
    assert small["merged_sat_totals"] == {
        "support_records": 3,
        "representatives": 584,
        "labelled_local_graphs": 24576,
        "direct_unsat": 554,
        "core_covered_unsat": 30,
        "unknown": 0,
        "sat": 0,
    }
    input_hash_entry = next(
        row for row in small["inputs"] if row["path"] == str(INPUT)
    )
    assert input_hash_entry["sha256"] == sha256(INPUT)
    for checkpoint in CHECKPOINTS:
        if checkpoint == CHECKPOINTS[0]:
            assert small["deep_replacement"]["merged_checkpoint"] == str(checkpoint)
            assert small["deep_replacement"]["merged_checkpoint_sha256"] == sha256(checkpoint)
        else:
            original_entry = next(
                row for row in small["inputs"] if row["path"] == str(checkpoint)
            )
            assert original_entry["sha256"] == sha256(checkpoint)

    records = [
        audit_record(index, checkpoint, PREFIXES[index], normalized)
        for index, checkpoint in enumerate(CHECKPOINTS)
    ]
    assert sum(row["branches"] for row in records) == 584
    assert sum(row["labelled_local_graphs"] for row in records) == 24576
    assert all(row["drat_status"] == "DRAT_VERIFIED" for row in records)

    total_proof_bytes = sum(row["proof_bytes"] for row in records)
    total_proof_lines = sum(row["proof_lines"] for row in records)
    result = {
        "status": "FORMAL_AUDIT_PASS",
        "model": "hash-bound DRUP certification of all E72,Q>=3 small-snapshot exact-SAT branches",
        "local_completeness_anchor": {
            "audit": str(SMALL_AUDIT),
            "audit_sha256": sha256(SMALL_AUDIT),
            "audit_script": str(SMALL_AUDIT_SCRIPT),
            "audit_script_sha256": sha256(SMALL_AUDIT_SCRIPT),
            "status": small["status"],
            "completed_partition_indices": small["scope"]["completed_partition_indices"],
            "support_records": 3,
            "representatives": 584,
            "labelled_local_graphs": 24576,
        },
        "normalized_representatives": str(INPUT),
        "normalized_representatives_sha256": sha256(INPUT),
        "selector_producer": str(SELECTOR_SCRIPT),
        "selector_producer_sha256": sha256(SELECTOR_SCRIPT),
        "proof_check_driver": str(CHECK_SCRIPT),
        "proof_check_driver_sha256": sha256(CHECK_SCRIPT),
        "proof_flush_controls": {
            "ucrt_fflush_present": True,
            "explicit_cadical195_delete_present": True,
            "all_flush_returns_zero": all(
                json.loads(prefix.with_suffix(".json").read_text(encoding="utf-8"))[
                    "c_stdio_flush_return"
                ] == 0 for prefix in PREFIXES
            ),
            "no_terminal_empty_clause_synthesized": True,
        },
        "checker": {
            "sha256": EXPECTED_CHECKER_SHA256,
            "source_sha256": EXPECTED_CHECKER_SOURCE_SHA256,
            "upstream_commit": EXPECTED_CHECKER_COMMIT,
            "all_three_invocations_returned_verified": True,
        },
        "coverage": {
            "support_records": 3,
            "selector_formulas": 3,
            "branches_formally_covered": 584,
            "labelled_local_graphs_covered": 24576,
            "total_proof_bytes": total_proof_bytes,
            "total_proof_lines": total_proof_lines,
        },
        "records": records,
        "logical_bridge": (
            "For every complete local assignment A_i, the independently rebuilt "
            "checkpoint core C_i is nonempty and C_i subseteq A_i. If shared CNF "
            "F plus A_i were satisfiable, setting selector s_i true would satisfy "
            "F, the selector disjunction, and every implication s_i -> literal in "
            "C_i. Each externally DRAT-verified selector CNF is UNSAT, so every "
            "covered F plus A_i is UNSAT."
        ),
        "all_selector_cnfs_rebuilt_byte_for_byte": True,
        "all_selector_proofs_drat_verified": True,
        "ok": True,
        "claim_boundary": (
            "The DRUP/DRAT checks formally certify the exact-SAT exclusion of the "
            "584 representatives hash-bound to the completed eleven-partition local "
            "snapshot. Correctness still depends on the audited encoder and local "
            "reduction, and the remaining E72 partitions are outside this artifact."
        ),
    }
    atomic_json(OUTPUT, result)

    lines = [
        "# E72 Q>=3 small-snapshot formal certificate audit",
        "",
        "Status: **FORMAL_AUDIT_PASS**.",
        "",
        "| record | branches | labelled | clauses | proof lines | checker |",
        "|---:|---:|---:|---:|---:|---|",
    ]
    for row in records:
        lines.append(
            f"| {row['record_index']} | {row['branches']} | "
            f"{row['labelled_local_graphs']} | {row['clauses']} | "
            f"{row['proof_lines']} | {row['drat_status']} |"
        )
    lines.extend([
        "",
        f"All {sum(row['branches'] for row in records)} local representatives "
        f"({sum(row['labelled_local_graphs'] for row in records)} labelled local "
        "graphs) are covered. Each selector CNF was independently rebuilt byte for "
        "byte from the shared exact CNF and audited assumption cores before binding "
        "it to the checked proof hash.",
        "",
        "The producer used the explicit UCRT flush and native CaDiCaL finalization; "
        "all proofs contained solver-emitted terminal empty clauses. The pinned "
        f"checker is upstream commit `{EXPECTED_CHECKER_COMMIT}` and returned "
        "`s VERIFIED` for all three formulas.",
        "",
        "Boundary: this formally certifies the 584 exact-SAT branches in the eleven "
        "completed small partitions. It does not cover the remaining E72 partitions.",
        "",
    ])
    SUMMARY.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        **result["coverage"],
        "all_selector_proofs_drat_verified": True,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
