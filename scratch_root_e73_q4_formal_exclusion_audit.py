"""Aggregate, hash-bound formal audit of the E0=73, Q>=4 exclusion.

This audit does not trust the original incremental SAT return codes.  It
rebuilds each shared CNF and every selector/core implication, checks the exact
DIMACS hash, and then binds that formula to a proof accepted by drat-trim.
"""

from __future__ import annotations

import gc
import hashlib
import json
from pathlib import Path

from scratch_incremental_local_exact_sat import build_shared_cnf, normalize_source


INPUT = Path("scratch_general_e73_q4_incremental_snapshot_002_records.json")
OUTPUT = Path("scratch_root_e73_q4_formal_exclusion_audit.json")
SUMMARY = Path("scratch_root_e73_q4_formal_exclusion_audit.md")

PREREQUISITES = {
    "side_bound": Path("scratch_root_side_bound_selfcontained_audit.json"),
    "compression": Path("scratch_root_e73_q4_compression_audit.json"),
    "independent_compression_port": Path("scratch_root_e73_q4_independent_audit.json"),
    "port": Path("scratch_root_e73_q4_port_census.json"),
    "local_expansion": Path("scratch_general_e73_q4_local_expansion.json"),
    "local_representatives": Path("scratch_general_e73_q4_local_graph_reps.json"),
    "local_representative_audit": Path("scratch_root_e73_q4_local_reps_audit.json"),
    "incremental_rebuild_audit": Path("scratch_root_e73_q4_incremental_audit.json"),
}

CHECKPOINTS = (
    Path("scratch_general_e73_q4_snapshot001_record00_sat.json"),
    Path("scratch_general_e73_q4_snapshot001_record01_sat.json"),
    Path("scratch_general_e73_q4_snapshot002_record02_sat.json"),
    Path("scratch_general_e73_q4_snapshot002_record03_sat.json"),
    Path("scratch_general_e73_q4_snapshot002_record04_sat.json"),
    Path("scratch_general_e73_q4_snapshot002_record05_sat.json"),
)

SELECTORS = (
    (Path("scratch_e73_selector_record00.json"), Path("scratch_e73_selector_record00_drat_audit.json")),
    (Path("scratch_e73_selector_record01.json"), Path("scratch_e73_selector_record01_drat_audit.json")),
    (Path("scratch_e73_selector_record02.json"), Path("scratch_e73_selector_record02_drat_audit.json")),
    # The original record03 trace was correctly rejected.  This is the
    # separately regenerated and verified Glucose4 trace.
    (Path("scratch_e73_selector_record03_g4.json"), Path("scratch_e73_selector_record03_g4_drat_audit.json")),
    (Path("scratch_e73_selector_record04.json"), Path("scratch_e73_selector_record04_drat_audit.json")),
    (Path("scratch_e73_selector_record05.json"), Path("scratch_e73_selector_record05_drat_audit.json")),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def expected_dimacs_hash(variables, base_clauses, selectors, cores):
    clause_count = len(base_clauses) + 1 + sum(map(len, cores))
    digest = hashlib.sha256()
    digest.update(f"p cnf {variables} {clause_count}\n".encode("ascii"))
    for clause in base_clauses:
        digest.update((" ".join(map(str, clause)) + " 0\n").encode("ascii"))
    digest.update((" ".join(map(str, selectors)) + " 0\n").encode("ascii"))
    for selector, core in zip(selectors, cores):
        for literal in core:
            digest.update(f"{-selector} {literal} 0\n".encode("ascii"))
    return digest.hexdigest().upper(), clause_count


def require(condition, message, errors):
    if not condition:
        errors.append(message)


def main():
    errors = []
    prereq = {name: load(path) for name, path in PREREQUISITES.items()}
    hashes = {str(path): sha256(path) for path in PREREQUISITES.values()}
    hashes[str(INPUT)] = sha256(INPUT)

    side = prereq["side_bound"]
    compression = prereq["compression"]
    independent = prereq["independent_compression_port"]
    port = prereq["port"]
    expansion = prereq["local_expansion"]
    reps = prereq["local_representatives"]
    rep_audit = prereq["local_representative_audit"]
    incremental = prereq["incremental_rebuild_audit"]
    normalized = load(INPUT)

    require(side.get("ok") is True, "side-bound audit is not ok", errors)
    require(side.get("status") == "LOGIC_AND_ARITHMETIC_VERIFIED", "side-bound audit status", errors)
    require("S(r)<=69" in side.get("conclusion", ""), "side-bound conclusion missing S<=69", errors)
    theorem = compression.get("theorem_inputs", {})
    require(theorem.get("external_premise_required") is False, "external premise used", errors)
    require(theorem.get("total_fibre_edges_E0") == 73, "wrong E0", errors)
    require(theorem.get("required_diagonal_edges_Q") == ">=4", "wrong Q branch", errors)
    require(theorem.get("root_implication") == "E0=73 and S(r)<=69 imply Q=E0-S>=4", "root implication mismatch", errors)

    coverage = compression.get("coverage", {})
    require(compression.get("status") == "COMPLETE", "compression incomplete", errors)
    require(coverage.get("partition_count") == 27, "partition coverage mismatch", errors)
    require(coverage.get("all_labelled_placements") == 79_841_895, "labelled placement count", errors)
    require(coverage.get("all_weighted_S7_orbits_by_Burnside") == 21_699, "S7 orbit count", errors)
    require(coverage.get("labelled_identity_verified") is True, "labelled identity not verified", errors)
    require(coverage.get("orbit_identity_verified") is True, "orbit identity not verified", errors)
    require(coverage.get("all_part_identity_verified") is True, "part identity not verified", errors)
    require(independent.get("ok") is True and independent.get("status") == "INDEPENDENTLY_VERIFIED", "independent compression/port audit failed", errors)

    ps = port.get("summary", {})
    require(port.get("status") == "COMPLETE", "port census incomplete", errors)
    require(ps.get("input_support_orbits") == 295, "port input support count", errors)
    require(ps.get("Q_at_least_4_assignments_covered") == 4_758_382, "Q>=4 coverage count", errors)
    require(ps.get("locally_port_feasible_support_orbits") == 58, "port support survivors", errors)
    require(ps.get("locally_port_feasible_Q_at_least_4_assignments") == 980, "port state survivors", errors)
    require(ps.get("all_full_product_identities_verified") is True, "full product identity", errors)
    require(ps.get("all_Q_target_identities_verified") is True, "Q target identity", errors)

    es = expansion.get("summary", {})
    require(expansion.get("status") == "COMPLETE", "local expansion incomplete", errors)
    require(es.get("support_rows") == 58, "local support rows", errors)
    require(es.get("port_feasible_state_assignments") == 980, "local state count", errors)
    require(es.get("exact_overlap_completions") == 21_061_632, "local completion coverage", errors)
    require(es.get("after_forced_C4_support_BP") == 98_304, "raw local survivors", errors)
    require(es.get("nonempty_support_rows") == 6, "nonempty support rows", errors)
    require(es.get("local_graph_orbits") == 1_804, "local orbit count", errors)
    require(reps.get("status") == "COMPLETE", "representative file incomplete", errors)
    require(reps.get("raw_graphs") == 98_304 and reps.get("local_graph_orbits") == 1_804, "representative totals", errors)
    require(rep_audit.get("status") == "VERIFIED", "representative audit failed", errors)
    require(rep_audit.get("support_rows_checked") == 6, "representative support coverage", errors)
    require(rep_audit.get("orbits_checked") == 1_804, "representative orbit coverage", errors)
    require(rep_audit.get("raw_graphs_checked") == 98_304, "representative raw coverage", errors)
    require(rep_audit.get("all_representatives_have_Q") == 4, "survivor Q value", errors)
    require(incremental.get("ok") is True and incremental.get("status") == "AUDIT_PASS", "incremental rebuild audit failed", errors)
    require(incremental.get("totals", {}).get("support_records") == 6, "incremental support count", errors)
    require(incremental.get("totals", {}).get("representatives") == 1_804, "incremental branch count", errors)
    require(incremental.get("totals", {}).get("labelled_local_graphs") == 98_304, "incremental orbit mass", errors)
    require(normalized.get("support_record_count") == 6, "normalized support count", errors)
    require(normalized.get("local_representative_count") == 1_804, "normalized branch count", errors)
    require(normalized.get("labelled_local_graphs_represented") == 98_304, "normalized orbit mass", errors)

    proof_rows = []
    checker_fingerprints = set()
    seen_branch_keys = set()
    for index, ((meta_path, audit_path), checkpoint_path) in enumerate(zip(SELECTORS, CHECKPOINTS)):
        row_errors = []
        meta = load(meta_path)
        audit = load(audit_path)
        checkpoint = load(checkpoint_path)
        source = normalize_source(INPUT, index)
        base_clauses, _edge, _local, _full, branches, shared_meta = build_shared_cnf(source)
        records = checkpoint.get("records", [])

        require(meta.get("record_index") == index, "metadata record index", row_errors)
        require(meta.get("input_sha256") == sha256(INPUT), "metadata input hash", row_errors)
        require(meta.get("checkpoint_sha256") == sha256(checkpoint_path), "metadata checkpoint hash", row_errors)
        require(checkpoint.get("status") == "UNSAT" and checkpoint.get("checkpoint_complete") is True, "checkpoint not complete UNSAT", row_errors)
        require(len(branches) == len(records) == meta.get("branches_covered"), "branch count mismatch", row_errors)
        require([b["branch_index"] for b in branches] == list(range(len(branches))), "rebuilt branch order", row_errors)
        require([r["branch_index"] for r in records] == list(range(len(records))), "checkpoint branch order", row_errors)

        cores = []
        orbit_mass = 0
        for branch, record in zip(branches, records):
            assumptions = tuple(branch["assumptions"])
            core = tuple(record.get("assumption_core", []))
            require(bool(core), f"branch {branch['branch_index']} empty core", row_errors)
            require(len(core) == len(set(core)), f"branch {branch['branch_index']} duplicate core literal", row_errors)
            require(set(core) <= set(assumptions), f"branch {branch['branch_index']} core not contained", row_errors)
            require(record.get("logical_status") == "UNSAT", f"branch {branch['branch_index']} not logical UNSAT", row_errors)
            require(branch.get("assumption_sha256") == record.get("assumption_sha256"), f"branch {branch['branch_index']} assumption hash", row_errors)
            key = (index, branch["branch_index"])
            require(key not in seen_branch_keys, f"duplicate global branch key {key}", row_errors)
            seen_branch_keys.add(key)
            orbit_mass += int(record["orbit_size"])
            cores.append(core)

        selector_first = shared_meta["variables"] + 1
        selectors = tuple(range(selector_first, selector_first + len(branches)))
        variables = selectors[-1]
        expected_hash, expected_clauses = expected_dimacs_hash(
            variables, base_clauses, selectors, cores
        )
        actual_cnf = Path(meta["cnf"])
        actual_proof = Path(meta["proof"])
        actual_cnf_hash = sha256(actual_cnf)
        actual_proof_hash = sha256(actual_proof)
        require(meta.get("shared_variables") == shared_meta["variables"], "shared variable count", row_errors)
        require(meta.get("variables") == variables, "selector variable count", row_errors)
        require(meta.get("selectors") == len(selectors), "selector count", row_errors)
        require(meta.get("selector_core_implications") == sum(map(len, cores)), "implication count", row_errors)
        require(meta.get("clauses") == expected_clauses, "selector clause count", row_errors)
        require(actual_cnf_hash == expected_hash == meta.get("cnf_sha256"), "rebuilt DIMACS hash mismatch", row_errors)
        require(actual_proof_hash == meta.get("proof_sha256"), "proof hash mismatch", row_errors)
        require(meta.get("terminal_empty_clause_appended_for_external_check") is False, "synthetic empty clause marker", row_errors)
        require(audit.get("ok") is True and audit.get("status") == "DRAT_VERIFIED", "DRAT audit failed", row_errors)
        require(audit.get("return_code") == 0 and "s VERIFIED" in audit.get("transcript", ""), "checker transcript not verified", row_errors)
        require(audit.get("cnf_sha256") == actual_cnf_hash, "audit CNF hash", row_errors)
        require(audit.get("proof_sha256") == actual_proof_hash, "audit proof hash", row_errors)
        require(audit.get("producer_metadata_sha256") == sha256(meta_path), "audit producer hash", row_errors)
        require(orbit_mass == normalized["records"][index]["local_graph_count"], "record orbit mass", row_errors)
        checker_fingerprints.add((
            audit.get("checker_sha256"),
            audit.get("checker_source_sha256"),
            audit.get("checker_upstream_commit"),
        ))

        errors.extend(f"record {index}: {message}" for message in row_errors)
        proof_rows.append({
            "record_index": index,
            "solver": meta.get("solver"),
            "branches": len(branches),
            "labelled_local_graphs": orbit_mass,
            "shared_variables": shared_meta["variables"],
            "selector_variables": len(selectors),
            "variables": variables,
            "clauses": expected_clauses,
            "selector_core_implications": sum(map(len, cores)),
            "cnf": str(actual_cnf),
            "cnf_sha256": actual_cnf_hash,
            "proof": str(actual_proof),
            "proof_sha256": actual_proof_hash,
            "drat_audit": str(audit_path),
            "drat_audit_sha256": sha256(audit_path),
            "ok": not row_errors,
            "errors": row_errors,
        })
        hashes[str(checkpoint_path)] = sha256(checkpoint_path)
        hashes[str(meta_path)] = sha256(meta_path)
        hashes[str(audit_path)] = sha256(audit_path)
        del base_clauses, branches, records, checkpoint, source
        gc.collect()

    require(len(checker_fingerprints) == 1, "proofs used nonuniform checker fingerprints", errors)
    require(len(seen_branch_keys) == 1_804, "global branch key coverage", errors)
    require(sum(row["branches"] for row in proof_rows) == 1_804, "proof branch total", errors)
    require(sum(row["labelled_local_graphs"] for row in proof_rows) == 98_304, "proof orbit mass total", errors)

    result = {
        "status": "FORMAL_COMPUTER_ASSISTED_EXCLUSION_VERIFIED" if not errors else "AUDIT_FAILED",
        "ok": not errors,
        "errors": errors,
        "theorem": (
            "Assuming an srg(99,14,1,2), a root selected by the self-contained "
            "S(r)<=69 theorem cannot have E0=73."
        ),
        "logical_chain": [
            "the trace/triangle argument guarantees a selected root with S(r)<=69",
            "in the E0=73 branch, Q=E0-S implies Q>=4",
            "exhaustive support, fibre-state, matching, spectral, pair, and forced-C4 filters leave exactly 1804 local graph orbits of mass 98304",
            "for every orbit representative, a rebuilt shared exact SRG CNF plus its complete local assignment contains an audited selector core",
            "six exact selector formulas covering all 1804 cores have hash-bound DRUP traces independently accepted by drat-trim",
            "therefore every necessary local representative is impossible, excluding E0=73 for the selected root",
        ],
        "coverage_totals": {
            "deficit_partitions": 27,
            "weighted_support_orbits": 21_699,
            "Q_at_least_4_complete_fibre_state_assignments": 4_758_382,
            "port_feasible_state_assignments": 980,
            "exact_overlap_completions": 21_061_632,
            "raw_local_survivors": 98_304,
            "local_graph_orbits": 1_804,
            "selector_formulas": 6,
            "formally_proved_unsat_branches": 1_804,
        },
        "checker_fingerprint": {
            "binary_sha256": next(iter(checker_fingerprints))[0] if checker_fingerprints else None,
            "source_sha256": next(iter(checker_fingerprints))[1] if checker_fingerprints else None,
            "upstream_commit": next(iter(checker_fingerprints))[2] if checker_fingerprints else None,
            "local_patch_scope": "Windows-only timing/getc_unlocked compatibility; proof logic unchanged",
        },
        "logical_bridge": (
            "For branch i, selector s_i implies every literal of audited core "
            "C_i and at least one selector is true. If shared CNF F plus a "
            "complete assignment A_i were satisfiable, C_i subset A_i would "
            "let us set only s_i=true, satisfying the selector CNF. Its "
            "checked UNSAT proof therefore proves every F and A_i UNSAT."
        ),
        "artifact_sha256": hashes,
        "proof_records": proof_rows,
        "claim_boundary": (
            "This is a certificate-backed exclusion of the selected-root "
            "E0=73 branch. It is not a proof that the full SRG does not exist; "
            "lower E0 branches remain, and higher-branch results require their "
            "own certificate chains before being combined formally."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    SUMMARY.write_text(
        "# Formal E0=73, Q>=4 exclusion audit\n\n"
        f"Status: `{result['status']}`  \n"
        f"Errors: `{len(errors)}`  \n"
        "Covered: `1804` local orbits / `98304` labelled local graphs.  \n"
        "All six selector CNFs were rebuilt byte-for-byte and their hash-bound "
        "proofs were accepted by drat-trim.\n\n"
        "The certified conclusion is only that the self-contained selected root "
        "cannot lie in the E0=73 branch; this does not settle the 99-graph problem.\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": result["status"],
        "errors": len(errors),
        "branches": sum(row["branches"] for row in proof_rows),
        "labelled_local_graphs": sum(row["labelled_local_graphs"] for row in proof_rows),
    }, sort_keys=True))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
