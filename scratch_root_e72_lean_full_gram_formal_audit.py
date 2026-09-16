"""Generic rebuild/hash audit for a lean E72 full-Gram aggregate DRUP proof.

The certificate formally refutes the emitted CNF.  The audit also replays the
deterministic support-specific lift and binds it to the upstream census/Gram
artifacts by hash; those upstream semantic bridges are explicitly not promoted
to an end-to-end formal theorem here.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path

import scratch_root_e72_full_gram_macro_lean_sat as macro


PINNED_DRAT_COMMIT = "2e3b2dc0ecf938addbd779d42877b6ed69d9a985"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def audit(source: int, checkpoint_path: Path) -> dict:
    stem = f"scratch_root_e72_source{source}_lean_full_gram_macro"
    build_path = Path(f"{stem}_build.json")
    proof_meta_path = Path(f"{stem}_proof.json")
    drat_audit_path = Path(f"{stem}_proof_drat_audit.json")
    output_path = Path(f"scratch_root_e72_source{source}_formal_audit.json")
    report_path = Path(f"scratch_root_e72_source{source}_formal_audit.md")

    old_build_hash = sha256(build_path)
    old_build = json.loads(build_path.read_text(encoding="utf-8"))
    cnf_path = Path(old_build["cnf"])
    old_cnf_hash = sha256(cnf_path)

    rebuilt = macro.build(source, redundant_bp=False)
    assert sha256(build_path) == old_build_hash
    assert sha256(cnf_path) == old_cnf_hash
    assert json.loads(json.dumps(rebuilt)) == old_build
    assert rebuilt["status"] == "BUILD_COMPLETE"
    assert rebuilt["source_row_index"] == source
    assert rebuilt["unused_placeholder_assumptions_applied"] is False
    assert rebuilt["redundant_BP_consequence_layer_enabled"] is False
    assert rebuilt["redundant_BP_consequence_equalities"] == 0
    assert rebuilt["overlap_graphs_enumerated"] == 0
    assert rebuilt["selector_at_least_one_clauses"] == 1

    orbit = rebuilt["state_orbit_audit"]
    macros = rebuilt["macro_audit"]
    assert orbit["closure_partition_and_orbit_stabilizer_identities_verified"]
    assert rebuilt["macro_branches"] == len(rebuilt["branches"])
    assert rebuilt["macro_branches"] == macros["full_gram_passing_macro_branches"]
    assert macros["full_gram_rejected_macro_branches"] == 0
    coverage = macros["passing_labelled_state_matching_coverage"]
    assert coverage > 0
    assert sum(
        branch["labelled_state_matching_coverage"]
        for branch in rebuilt["branches"]
    ) == coverage

    exceptional = tuple(
        tuple(item["support"]) for item in rebuilt["exceptional_supports"]
    )
    expected_pairs = set(itertools.combinations(range(len(exceptional)), 2))
    for branch in rebuilt["branches"]:
        overlap = {
            (left, right) for left, right, _value in branch["overlap_block_totals"]
        }
        disjoint = {
            (left, right) for left, right, _value in branch["disjoint_block_totals"]
        }
        complete = {
            (left, right)
            for left, right, _value in branch["all_exceptional_block_totals"]
        }
        assert overlap.isdisjoint(disjoint)
        assert overlap | disjoint == complete == expected_pairs
        assert all(
            set(exceptional[left]) & set(exceptional[right])
            for left, right in overlap
        )
        assert all(
            not (set(exceptional[left]) & set(exceptional[right]))
            for left, right in disjoint
        )
        assert all(
            0 <= value <= 16
            for _left, _right, value in branch["all_exceptional_block_totals"]
        )
        assert branch["block_cardinality_equalities"] == len(expected_pairs)

    checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    assert checkpoint["source_row_index"] == source
    assert checkpoint["status"] == "UNSAT"
    assert checkpoint["mode"] == "aggregate"
    assert checkpoint["checkpoint_complete"] is True
    assert checkpoint["macro_branches"] == rebuilt["macro_branches"]
    assert checkpoint["direct_unsat"] == 1
    assert checkpoint["unknown"] == checkpoint["sat"] == 0
    assert checkpoint["terminal_labelled_state_matching_coverage"] == coverage
    assert checkpoint["total_labelled_state_matching_coverage"] == coverage
    assert len(checkpoint["records"]) == 1
    assert checkpoint["records"][0]["status"] == "UNSAT"
    assert checkpoint["cnf_sha256"] == old_cnf_hash
    assert checkpoint["build_sha256"] == old_build_hash

    proof = json.loads(proof_meta_path.read_text(encoding="utf-8"))
    drat = json.loads(drat_audit_path.read_text(encoding="utf-8"))
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
    assert drat["checker_upstream_commit"] == PINNED_DRAT_COMMIT

    result = {
        "status": "FORMAL_AUDIT_PASS",
        "scope": f"E72 source row {source} lean full-Gram-passing canonical macros",
        "source_row_index": source,
        "port_feasible_labelled_states": orbit["feasible_labelled_states"],
        "state_orbits": orbit["state_orbits"],
        "canonical_full_gram_macro_branches": rebuilt["macro_branches"],
        "labelled_state_matching_coverage": coverage,
        "exceptional_fibres": len(exceptional),
        "all_exceptional_block_totals_fixed_per_branch": True,
        "overlap_graphs_explicitly_enumerated_by_sat_lift": 0,
        "unused_placeholder_assumptions_applied": False,
        "redundant_BP_consequence_layer_enabled": False,
        "deterministic_builder_replay": {
            "build_byte_identical": True,
            "cnf_byte_identical": True,
        },
        "cnf": {
            "path": str(cnf_path),
            "sha256": old_cnf_hash,
            "variables": proof["variables"],
            "clauses": proof["clauses"],
        },
        "checkpoint": {
            "path": str(checkpoint_path),
            "sha256": sha256(checkpoint_path),
            "conflict_budget_per_call": checkpoint["conflict_budget_per_call"],
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
            "build": str(build_path),
            "build_sha256": old_build_hash,
            "macro_catalog": macros["macro_catalog"],
            "macro_catalog_sha256": macros["macro_catalog_sha256"],
            "full_gram": macros["full_gram"],
            "full_gram_sha256": macros["full_gram_sha256"],
            "proof_producer": "scratch_root_exact_cnf_drup.py",
            "proof_producer_sha256": sha256(Path("scratch_root_exact_cnf_drup.py")),
            "proof_metadata": str(proof_meta_path),
            "proof_metadata_sha256": sha256(proof_meta_path),
            "drat_audit": str(drat_audit_path),
            "drat_audit_sha256": sha256(drat_audit_path),
        },
        "logical_conclusion": (
            "No exact rooted completion exists in any encoded full-Gram-feasible "
            f"canonical macro branch of E72 source row {source}."
        ),
        "claim_boundary": (
            "The exact CNF/DRUP contradiction is externally machine checked. "
            "The upstream E72 port census, orbit/canonicalization completeness, "
            "full-Gram derivation, and shared/cardinality encoder semantics remain "
            "executable/theory audits rather than one end-to-end formal proof from "
            "the original SRG axioms."
        ),
    }
    output_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    report_path.write_text(
        f"# E72 source-row {source} formal audit\n\n"
        "Status: **FORMAL_AUDIT_PASS**.\n\n"
        f"{rebuilt['macro_branches']:,} canonical full-Gram macro branch(es), "
        f"covering {coverage:,} labelled state/matching completions, were encoded "
        "without overlap-graph enumeration. "
        f"The exact CNF has {proof['variables']:,} variables and "
        f"{proof['clauses']:,} clauses. Its {proof['proof_lines']:,}-line DRUP "
        "certificate was accepted by the pinned drat-trim checker.\n\n"
        "Boundary: the checked contradiction is conditional on the separately "
        "audited upstream census, canonical macro completeness, full-Gram bridge, "
        "and encoder semantics; it is not an end-to-end formal proof of the whole "
        "Conway 99-graph problem.\n",
        encoding="utf-8",
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-row-index", type=int, required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    args = parser.parse_args()
    result = audit(args.source_row_index, args.checkpoint)
    print(json.dumps({
        "status": result["status"],
        "source": result["source_row_index"],
        "branches": result["canonical_full_gram_macro_branches"],
        "coverage": result["labelled_state_matching_coverage"],
        "proof_lines": result["certificate"]["proof_lines"],
        "drat": result["certificate"]["external_checker_status"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
