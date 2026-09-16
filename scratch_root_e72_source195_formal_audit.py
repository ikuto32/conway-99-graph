"""Rebuild- and hash-bound audit for the source195 lean full-Gram DRUP proof."""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

import scratch_root_e72_full_gram_macro_lean_sat as macro


SOURCE = 195
BUILD = Path("scratch_root_e72_source195_lean_full_gram_macro_build.json")
CHECKPOINT = Path(
    "scratch_root_e72_source195_lean_full_gram_macro_aggregate_c100000.json"
)
PROOF_META = Path("scratch_root_e72_source195_lean_full_gram_macro_proof.json")
DRAT_AUDIT = Path(
    "scratch_root_e72_source195_lean_full_gram_macro_proof_drat_audit.json"
)
OUTPUT = Path("scratch_root_e72_source195_formal_audit.json")
REPORT = Path("scratch_root_e72_source195_formal_audit.md")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def main() -> None:
    old_build_hash = sha256(BUILD)
    old_build = json.loads(BUILD.read_text(encoding="utf-8"))
    old_cnf = Path(old_build["cnf"])
    old_cnf_hash = sha256(old_cnf)

    # Replay the complete deterministic construction.  This deliberately uses
    # the lean shared builder without the optional redundant BP consequence layer.
    rebuilt = macro.build(SOURCE, redundant_bp=False)
    assert sha256(BUILD) == old_build_hash
    assert sha256(old_cnf) == old_cnf_hash
    # ``build`` retains a few tuples in memory, while JSON necessarily reloads
    # them as lists.  Byte-identical emitted JSON/CNF plus JSON-normalized object
    # equality is the intended deterministic replay criterion.
    assert json.loads(json.dumps(rebuilt)) == old_build
    assert rebuilt["status"] == "BUILD_COMPLETE"
    assert rebuilt["unused_placeholder_assumptions_applied"] is False
    assert rebuilt["redundant_BP_consequence_layer_enabled"] is False
    assert rebuilt["redundant_BP_consequence_equalities"] == 0
    assert rebuilt["overlap_graphs_enumerated"] == 0

    orbit = rebuilt["state_orbit_audit"]
    macros = rebuilt["macro_audit"]
    assert orbit["feasible_labelled_states"] == 8
    assert orbit["state_orbits"] == 1
    assert orbit["closure_partition_and_orbit_stabilizer_identities_verified"]
    assert macros["all_catalog_entries_for_source"] == 1
    assert macros["canonical_catalog_entries_for_source"] == 1
    assert macros["full_gram_canonical_rows_for_source"] == 1
    assert macros["full_gram_passing_macro_branches"] == 1
    assert macros["full_gram_rejected_macro_branches"] == 0
    assert macros["passing_labelled_state_matching_coverage"] == 262144
    assert rebuilt["macro_branches"] == len(rebuilt["branches"]) == 1

    exceptional = tuple(tuple(item["support"]) for item in rebuilt["exceptional_supports"])
    expected_pairs = set(itertools.combinations(range(len(exceptional)), 2))
    assert len(exceptional) == 8 and len(expected_pairs) == 28
    branch = rebuilt["branches"][0]
    overlap = {(left, right) for left, right, _value in branch["overlap_block_totals"]}
    disjoint = {(left, right) for left, right, _value in branch["disjoint_block_totals"]}
    complete = {
        (left, right)
        for left, right, _value in branch["all_exceptional_block_totals"]
    }
    assert overlap.isdisjoint(disjoint)
    assert overlap | disjoint == complete == expected_pairs
    assert all(set(exceptional[left]) & set(exceptional[right]) for left, right in overlap)
    assert all(not (set(exceptional[left]) & set(exceptional[right])) for left, right in disjoint)
    assert all(
        0 <= value <= 16
        for _left, _right, value in branch["all_exceptional_block_totals"]
    )
    assert branch["block_cardinality_equalities"] == 28
    assert branch["labelled_state_matching_coverage"] == 262144

    checkpoint = json.loads(CHECKPOINT.read_text(encoding="utf-8"))
    assert checkpoint["status"] == "UNSAT"
    assert checkpoint["checkpoint_complete"] is True
    assert checkpoint["macro_branches"] == 1
    assert checkpoint["direct_unsat"] == 1
    assert checkpoint["unknown"] == checkpoint["sat"] == 0
    assert checkpoint["terminal_labelled_state_matching_coverage"] == 262144
    assert checkpoint["total_labelled_state_matching_coverage"] == 262144
    assert len(checkpoint["records"]) == 1
    assert checkpoint["records"][0]["status"] == "UNSAT"
    assert checkpoint["cnf_sha256"] == rebuilt["cnf_audit"]["sha256"] == old_cnf_hash
    assert checkpoint["build_sha256"] == old_build_hash

    proof = json.loads(PROOF_META.read_text(encoding="utf-8"))
    drat = json.loads(DRAT_AUDIT.read_text(encoding="utf-8"))
    assert proof["status"] == "UNSAT_PROOF_EMITTED_UNCHECKED"
    assert proof["cnf_sha256"] == old_cnf_hash
    assert proof["variables"] == rebuilt["cnf_audit"]["declared_variables"]
    assert proof["clauses"] == rebuilt["cnf_audit"]["declared_clauses"]
    assert proof["terminal_empty_clause_present"] is True
    assert proof["terminal_empty_clause_appended_for_external_check"] is False
    assert sha256(Path(proof["proof"])) == proof["proof_sha256"]
    assert drat["status"] == "DRAT_VERIFIED" and drat["ok"] is True
    assert drat["cnf_sha256"] == proof["cnf_sha256"]
    assert drat["proof_sha256"] == proof["proof_sha256"]
    assert drat["checker_upstream_commit"] == (
        "2e3b2dc0ecf938addbd779d42877b6ed69d9a985"
    )

    result = {
        "status": "FORMAL_AUDIT_PASS",
        "scope": "E72 source row 195 lean full-Gram-passing canonical macros",
        "source_row_index": SOURCE,
        "port_feasible_labelled_states": 8,
        "state_orbits": 1,
        "canonical_full_gram_macro_branches": 1,
        "labelled_state_matching_coverage": 262144,
        "overlap_graphs_explicitly_enumerated_by_sat_lift": 0,
        "all_28_exceptional_block_totals_fixed": True,
        "unused_placeholder_assumptions_applied": False,
        "redundant_BP_consequence_layer_enabled": False,
        "deterministic_builder_replay": {
            "build_byte_identical": True,
            "cnf_byte_identical": True,
        },
        "cnf": {
            "path": str(old_cnf),
            "sha256": old_cnf_hash,
            "variables": rebuilt["cnf_audit"]["declared_variables"],
            "clauses": rebuilt["cnf_audit"]["declared_clauses"],
        },
        "checkpoint": {
            "path": str(CHECKPOINT),
            "sha256": sha256(CHECKPOINT),
            "status": checkpoint["status"],
            "conflicts": checkpoint["records"][0]["stats_delta"]["conflicts"],
        },
        "certificate": {
            "proof": proof["proof"],
            "proof_sha256": proof["proof_sha256"],
            "proof_lines": proof["proof_lines"],
            "external_checker_status": drat["status"],
            "checker": drat["checker"],
            "checker_sha256": drat["checker_sha256"],
            "checker_upstream_commit": drat["checker_upstream_commit"],
        },
        "inputs": {
            "builder_script": Path(macro.__file__).name,
            "builder_script_sha256": sha256(Path(macro.__file__)),
            "build": str(BUILD),
            "build_sha256": old_build_hash,
            "macro_catalog": macros["macro_catalog"],
            "macro_catalog_sha256": macros["macro_catalog_sha256"],
            "full_gram": macros["full_gram"],
            "full_gram_sha256": macros["full_gram_sha256"],
            "proof_producer": "scratch_root_exact_cnf_drup.py",
            "proof_producer_sha256": sha256(Path("scratch_root_exact_cnf_drup.py")),
            "proof_metadata": str(PROOF_META),
            "proof_metadata_sha256": sha256(PROOF_META),
            "drat_audit": str(DRAT_AUDIT),
            "drat_audit_sha256": sha256(DRAT_AUDIT),
        },
        "logical_conclusion": (
            "No exact rooted completion exists in the sole full-Gram-feasible "
            "canonical macro branch of E72 source row 195."
        ),
        "claim_boundary": (
            "The exact CNF/DRUP contradiction is externally machine checked. "
            "The upstream E72 port census, orbit/canonicalization completeness, "
            "full-Gram derivation, and the semantic correctness of the shared and "
            "cardinality encoders remain executable/theory audits rather than one "
            "end-to-end formal proof from the original SRG axioms."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(
        "# E72 source-row 195 formal audit\n\n"
        "Status: **FORMAL_AUDIT_PASS**.\n\n"
        "The sole canonical full-Gram macro branch covers 262,144 labelled "
        "state/matching completions. It was encoded without overlap-graph "
        f"enumeration as an exact CNF with {proof['variables']:,} variables and "
        f"{proof['clauses']:,} clauses. Its {proof['proof_lines']:,}-line DRUP "
        "certificate was accepted by the pinned drat-trim checker.\n\n"
        "Boundary: the checked contradiction is conditional on the separately "
        "audited upstream census, canonical macro completeness, full-Gram bridge, "
        "and encoder semantics; this is not yet an end-to-end formal proof of the "
        "whole Conway 99-graph problem.\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": result["status"],
        "macro_branches": result["canonical_full_gram_macro_branches"],
        "coverage": result["labelled_state_matching_coverage"],
        "proof_lines": result["certificate"]["proof_lines"],
        "drat": result["certificate"]["external_checker_status"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
