"""Independent structural/hash audit of the source133 macro-4 DRUP proof."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


BUILD = Path("scratch_root_e72_source133_full_gram_macro_build.json")
SWEEP = Path("scratch_root_e72_source133_branch_sweep_c100000.json")
SOURCE_CNF = Path("scratch_root_e72_source133_full_gram_macro.cnf")
BRANCH_CNF = Path("scratch_root_e72_source133_macro4.cnf")
PRODUCER = Path("scratch_root_e72_source133_macro4_drup.py")
META = Path("scratch_root_e72_source133_macro4_drup.json")
PROOF = Path("scratch_root_e72_source133_macro4.drup")
DRAT = Path("scratch_root_e72_source133_macro4_drat_audit.json")
OUTPUT = Path("scratch_root_e72_source133_macro4_formal_audit.json")
REPORT = Path("scratch_root_e72_source133_macro4_formal_audit.md")
PINNED_DRAT_COMMIT = "2e3b2dc0ecf938addbd779d42877b6ed69d9a985"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def header(line: bytes) -> tuple[int, int]:
    fields = line.split()
    assert fields[:2] == [b"p", b"cnf"] and len(fields) == 4
    return int(fields[2]), int(fields[3])


def main() -> None:
    build = json.loads(BUILD.read_text(encoding="utf-8"))
    sweep = json.loads(SWEEP.read_text(encoding="utf-8"))
    meta = json.loads(META.read_text(encoding="utf-8"))
    drat = json.loads(DRAT.read_text(encoding="utf-8"))

    assert build["status"] == "BUILD_COMPLETE"
    assert build["source_row_index"] == sweep["source_row_index"] == 133
    assert build["cnf"] == str(SOURCE_CNF)
    assert build["cnf_audit"]["sha256"] == sha256(SOURCE_CNF)
    assert build["historical_portfolio_branch_units_applied"] is False
    assert build["overlap_graphs_enumerated"] == 0
    assert build["state_orbit_audit"]["closure_partition_and_orbit_stabilizer_identities_verified"]
    assert build["macro_branches"] == len(build["branches"]) == 5
    assert build["macro_audit"]["full_gram_passing_macro_branches"] == 5
    assert build["macro_audit"]["passing_labelled_state_matching_coverage"] == 2502656

    selectors = [branch["selector"] for branch in build["branches"]]
    assert selectors == list(range(817279, 817284))
    branch = build["branches"][4]
    assert branch["macro_branch_index"] == branch["state_orbit_number"] == 4
    assert branch["state_indices"] == [4, 6, 0, 4, 6, 0]
    assert branch["Q"] == 4
    assert branch["state_orbit_size"] == 48
    assert branch["labelled_state_matching_coverage"] == 12288
    record = next(
        item for item in sweep["records"] if item["macro_branch_index"] == 4
    )
    expected_units = [-selector for selector in selectors[:4]]
    assert record["status"] == "UNSAT"
    assert record["coverage"] == 12288
    assert record["assumption_core"] == expected_units

    # Byte-for-byte derive the branch formula relation without trusting the
    # proof producer: only the DIMACS header and four terminal units may differ.
    selector_disjunctions = 0
    source_payload_lines = 0
    with SOURCE_CNF.open("rb") as source, BRANCH_CNF.open("rb") as derived:
        source_variables, source_clauses = header(source.readline())
        branch_variables, branch_clauses = header(derived.readline())
        assert source_variables == branch_variables == build["cnf_audit"]["declared_variables"]
        assert source_clauses == build["cnf_audit"]["declared_clauses"]
        assert branch_clauses == source_clauses + len(expected_units)
        selector_line = (" ".join(map(str, selectors)) + " 0").encode()
        for source_line in source:
            assert derived.readline() == source_line
            source_payload_lines += 1
            selector_disjunctions += source_line.strip() == selector_line
        tail = [line.strip() for line in derived if line.strip()]
    assert source_payload_lines == source_clauses
    assert selector_disjunctions == 1
    assert tail == [f"{literal} 0".encode() for literal in expected_units]
    # The unique selector disjunction together with -s0..-s3 forces s4; every
    # gated macro-4 clause is therefore active, exactly as in the prior core.

    assert meta["status"] == "UNSAT_PROOF_EMITTED_UNCHECKED"
    assert meta["build"] == str(BUILD) and meta["build_sha256"] == sha256(BUILD)
    assert meta["sweep"] == str(SWEEP) and meta["sweep_sha256"] == sha256(SWEEP)
    assert meta["source_cnf"] == str(SOURCE_CNF)
    assert meta["source_cnf_sha256"] == sha256(SOURCE_CNF)
    assert meta["cnf"] == str(BRANCH_CNF)
    assert meta["cnf_sha256"] == sha256(BRANCH_CNF)
    assert meta["proof"] == str(PROOF)
    assert meta["proof_sha256"] == sha256(PROOF)
    assert meta["macro_branch_index"] == meta["state_orbit_number"] == 4
    assert meta["catalog_labelled_coverage"] == 12288
    assert meta["selectors"] == selectors
    assert meta["assumption_core_units"] == expected_units
    assert meta["variables"] == branch_variables
    assert meta["clauses"] == branch_clauses
    assert meta["terminal_empty_clause_present"] is True
    producer_text = PRODUCER.read_text(encoding="utf-8")
    assert 'ctypes.CDLL("ucrtbase.dll").fflush(None)' in producer_text
    assert "assert flush_return == 0" in producer_text
    assert "cadical195_del(engine.cadical, engine.prfile)" in producer_text

    assert drat["status"] == "DRAT_VERIFIED" and drat["ok"] is True
    assert drat["cnf"] == str(BRANCH_CNF)
    assert drat["cnf_sha256"] == sha256(BRANCH_CNF) == meta["cnf_sha256"]
    assert drat["proof"] == str(PROOF)
    assert drat["proof_sha256"] == sha256(PROOF) == meta["proof_sha256"]
    assert drat["producer_metadata"] == str(META)
    assert drat["producer_metadata_sha256"] == sha256(META)
    assert drat["checker_upstream_commit"] == PINNED_DRAT_COMMIT
    assert "s VERIFIED" in drat["transcript"]

    result = {
        "status": "FORMAL_AUDIT_PASS",
        "scope": "E72 source133 nonregular canonical macro branch 4 only",
        "source_row_index": 133,
        "macro_branch_index": 4,
        "state_orbit_number": 4,
        "Q": 4,
        "state_orbit_size": 48,
        "catalog_labelled_coverage": 12288,
        "branch_isolation": {
            "selectors": selectors,
            "appended_negative_units": expected_units,
            "source_selector_disjunction_occurrences": selector_disjunctions,
            "source_payload_byte_identical": True,
            "derived_tail_exactly_four_core_units": True,
            "selected_selector_forced": selectors[4],
            "prior_assumption_core_equal": True,
        },
        "cnf": {
            "path": str(BRANCH_CNF),
            "sha256": sha256(BRANCH_CNF),
            "variables": branch_variables,
            "clauses": branch_clauses,
            "source_cnf": str(SOURCE_CNF),
            "source_cnf_sha256": sha256(SOURCE_CNF),
        },
        "certificate": {
            "proof": str(PROOF),
            "proof_sha256": sha256(PROOF),
            "proof_lines": meta["proof_lines"],
            "external_checker_status": drat["status"],
            "checker": drat["checker"],
            "checker_sha256": drat["checker_sha256"],
            "checker_upstream_commit": drat["checker_upstream_commit"],
            "ucrt_flush_and_native_solver_finalization_present_in_producer": True,
        },
        "inputs": {
            "build": str(BUILD),
            "build_sha256": sha256(BUILD),
            "sweep": str(SWEEP),
            "sweep_sha256": sha256(SWEEP),
            "producer": str(PRODUCER),
            "producer_sha256": sha256(PRODUCER),
            "metadata": str(META),
            "metadata_sha256": sha256(META),
            "drat_audit": str(DRAT),
            "drat_audit_sha256": sha256(DRAT),
            "macro_catalog": build["macro_audit"]["macro_catalog"],
            "macro_catalog_sha256": build["macro_audit"]["macro_catalog_sha256"],
            "full_gram": build["macro_audit"]["full_gram"],
            "full_gram_sha256": build["macro_audit"]["full_gram_sha256"],
        },
        "logical_conclusion": (
            "The nonregular source133 macro branch 4 has no exact rooted SRG "
            "completion in the encoded model."
        ),
        "claim_boundary": (
            "This checked certificate covers only macro branch 4 (12,288 labelled "
            "coverage). It does not itself exclude source133 branches 0--3. The "
            "upstream census, orbit/canonicalization, full-Gram derivation, and CNF "
            "encoder semantics remain separately audited rather than one formal "
            "derivation from the original SRG axioms."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# E72 source133 macro-4 formal audit\n\n"
        "Status: **FORMAL_AUDIT_PASS**.\n\n"
        "The derived CNF is byte-for-byte the source133 aggregate CNF after its "
        "header, followed only by the four negative selector units in the prior "
        "UNSAT assumption core. The unique five-selector disjunction therefore "
        "forces macro 4. Its 3,128,709-line DRUP certificate was accepted by the "
        "pinned drat-trim checker, excluding 12,288 labelled completions.\n\n"
        "Boundary: this certificate covers macro 4 only; it does not itself exclude "
        "the four regular source133 macros, and upstream semantic bridges remain "
        "separately audited.\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": result["status"],
        "source": 133,
        "branch": 4,
        "coverage": 12288,
        "proof_lines": meta["proof_lines"],
        "drat": drat["status"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
