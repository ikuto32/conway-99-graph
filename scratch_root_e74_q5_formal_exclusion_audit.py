"""Hash-bound formal audit of the selected-root E0=74 exclusion.

The older E74 search correctly described Q>=5 as a conditional subcase.
The self-contained root-side theorem now supplies that condition: for its
selected root, Q=E0-S and S<=69, hence E0=74 implies Q>=5.  This program
checks that bridge, the exhaustive solver-free census, and an independently
checked selector-DRUP certificate covering every surviving local orbit.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scratch_incremental_local_exact_sat import build_shared_cnf, normalize_source


INPUT = Path("scratch_general_e74_q5_incremental_records.json")
CHECKPOINT = Path("scratch_general_e74_q5_incremental_sat.json")
META = Path("scratch_e74_q5_selector_record00.json")
DRAT = Path("scratch_e74_q5_selector_record00_drat_audit.json")
OUTPUT = Path("scratch_root_e74_q5_formal_exclusion_audit.json")
SUMMARY = Path("scratch_root_e74_q5_formal_exclusion_audit.md")

PREREQUISITES = {
    "side_bound": Path("scratch_root_side_bound_selfcontained_audit.json"),
    "compression": Path("scratch_general_e74_compression_audit.json"),
    "port": Path("scratch_general_e74_port_census.json"),
    "independent_port": Path("scratch_e74_independent_port_audit.json"),
    "local_expansion": Path("scratch_general_e74_q5_local_expansion.json"),
    "local_representatives": Path("scratch_general_e74_q5_local_graph_reps.json"),
    "independent_local": Path("scratch_e74_independent_q5_audit.json"),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def require(condition, message, errors):
    if not condition:
        errors.append(message)


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


def main():
    errors = []
    data = {name: load(path) for name, path in PREREQUISITES.items()}
    hashes = {str(path): sha256(path) for path in PREREQUISITES.values()}
    normalized = load(INPUT)
    checkpoint = load(CHECKPOINT)
    meta = load(META)
    drat = load(DRAT)
    for path in (INPUT, CHECKPOINT, META, DRAT):
        hashes[str(path)] = sha256(path)

    side = data["side_bound"]
    require(side.get("ok") is True, "side-bound audit is not ok", errors)
    require(side.get("status") == "LOGIC_AND_ARITHMETIC_VERIFIED", "side-bound audit status", errors)
    require("S(r)<=69" in side.get("conclusion", ""), "side-bound conclusion lacks S(r)<=69", errors)

    compression = data["compression"]
    theorem = compression.get("theorem_inputs", {})
    cs = compression.get("summary", {})
    require(compression.get("status") == "COMPLETE", "compression incomplete", errors)
    require(theorem.get("total_deficit") == 10, "wrong total deficit", errors)
    require(theorem.get("total_fibre_edges_E0") == 74, "wrong E0", errors)
    require(compression.get("labelled_placements") == 28_929_495, "labelled compression coverage", errors)
    require(compression.get("placement_orbits") == 8_680, "compression orbit coverage", errors)
    require(cs.get("filter_rows_complete") == 8_680, "compression rows incomplete", errors)
    require(cs.get("final_intersection") == 249, "compression survivor count", errors)

    port = data["port"]
    ps = port.get("summary", {})
    require(port.get("status") == "COMPLETE", "port census incomplete", errors)
    require(port.get("input_support_orbits") == 249, "port input supports", errors)
    require(ps.get("labelled_fibre_state_assignments_covered") == 134_371_022, "port state coverage", errors)
    require(ps.get("locally_port_feasible_support_orbits") == 175, "port support survivors", errors)
    require(ps.get("locally_port_feasible_assignments") == 29_203, "port state survivors", errors)

    independent_port = data["independent_port"]
    ipc = independent_port.get("coverage", {})
    ipx = independent_port.get("exact_overlap_completions", {})
    require(independent_port.get("ok") is True, "independent port audit failed", errors)
    require(ipc.get("coverage_identity_verified") is True, "independent port identity", errors)
    require(ipc.get("input_support_rows") == 249, "independent support coverage", errors)
    require(ipc.get("labelled_state_assignments_covered") == 134_371_022, "independent state coverage", errors)
    require(ipx.get("Q_at_least_5_states") == 89, "independent Q>=5 states", errors)
    require(ipx.get("Q_at_least_5_completions") == 1_461_248, "independent Q>=5 completions", errors)

    expansion = data["local_expansion"]
    es = expansion.get("summary", {})
    require(expansion.get("status") == "COMPLETE", "local expansion incomplete", errors)
    require(expansion.get("Q_condition") == "Q>=5", "wrong local Q condition", errors)
    require(es.get("support_rows") == 11, "local support rows", errors)
    require(es.get("port_feasible_state_assignments") == 89, "local state count", errors)
    require(es.get("exact_overlap_completions") == 1_461_248, "local completion coverage", errors)
    require(es.get("after_forced_C4_support_BP") == 16_384, "raw local survivors", errors)
    require(es.get("nonempty_support_rows") == 1, "nonempty local supports", errors)
    require(es.get("local_graph_orbits") == 188, "local orbit count", errors)
    require(es.get("forced_BP_Q_histogram") == {"8": 16_384}, "final Q histogram", errors)

    reps = data["local_representatives"]
    require(reps.get("status") == "COMPLETE", "representatives incomplete", errors)
    require(reps.get("raw_graphs") == 16_384, "representative orbit mass", errors)
    require(reps.get("local_graph_orbits") == 188, "representative count", errors)
    independent_local = data["independent_local"]
    ilc = independent_local.get("solver_free_counts", {})
    ila = independent_local.get("assumption_audit", {})
    require(independent_local.get("ok") is True, "independent local audit failed", errors)
    require(ilc.get("independent_Q_at_least_5_states") == 89, "independent local state count", errors)
    require(ilc.get("independent_Q_at_least_5_matching_completions") == 1_461_248, "independent local completions", errors)
    require(ilc.get("final_raw_local_graphs") == 16_384, "independent raw survivors", errors)
    require(ilc.get("local_graph_orbits") == 188, "independent orbit count", errors)
    require(ilc.get("orbit_weight_sum") == 16_384, "independent orbit mass", errors)
    require(ila.get("branches") == 188, "independent assumption coverage", errors)
    require(ila.get("recorded_cores_are_subsets_of_full_branch_assumptions") == 188, "independent core containment", errors)

    require(normalized.get("support_record_count") == 1, "normalized support count", errors)
    require(normalized.get("local_representative_count") == 188, "normalized branch count", errors)
    require(normalized.get("labelled_local_graphs_represented") == 16_384, "normalized orbit mass", errors)
    require(checkpoint.get("status") == "UNSAT", "checkpoint status", errors)
    require(checkpoint.get("checkpoint_complete") is True, "checkpoint incomplete", errors)
    require(checkpoint.get("completed_branch_count") == 188, "checkpoint branch count", errors)
    require(checkpoint.get("unknown_count") == 0, "checkpoint has unknowns", errors)

    source = normalize_source(INPUT, 0)
    base_clauses, _edge, _local, _full, branches, shared_meta = build_shared_cnf(source)
    records = checkpoint.get("records", [])
    require(len(branches) == len(records) == 188, "rebuilt branch coverage", errors)
    require([b["branch_index"] for b in branches] == list(range(188)), "rebuilt branch order", errors)
    require([r["branch_index"] for r in records] == list(range(188)), "checkpoint branch order", errors)

    cores = []
    orbit_mass = 0
    for branch, record in zip(branches, records):
        assumptions = tuple(branch["assumptions"])
        core = tuple(record.get("assumption_core", []))
        idx = branch["branch_index"]
        require(bool(core), f"branch {idx}: empty core", errors)
        require(len(core) == len(set(core)), f"branch {idx}: duplicate core literal", errors)
        require(set(core) <= set(assumptions), f"branch {idx}: core not contained", errors)
        require(record.get("logical_status") == "UNSAT", f"branch {idx}: not UNSAT", errors)
        require(branch.get("assumption_sha256") == record.get("assumption_sha256"), f"branch {idx}: assumption hash", errors)
        orbit_mass += int(record["orbit_size"])
        cores.append(core)
    require(orbit_mass == 16_384, "checkpoint orbit mass", errors)

    selector_first = shared_meta["variables"] + 1
    selectors = tuple(range(selector_first, selector_first + len(branches)))
    variables = selectors[-1]
    rebuilt_hash, rebuilt_clauses = expected_dimacs_hash(variables, base_clauses, selectors, cores)
    actual_cnf = Path(meta["cnf"])
    actual_proof = Path(meta["proof"])
    cnf_hash = sha256(actual_cnf)
    proof_hash = sha256(actual_proof)
    require(meta.get("input_sha256") == sha256(INPUT), "selector input hash", errors)
    require(meta.get("checkpoint_sha256") == sha256(CHECKPOINT), "selector checkpoint hash", errors)
    require(meta.get("branches_covered") == 188, "selector branch count", errors)
    require(meta.get("labelled_local_graphs_covered") == 16_384, "selector orbit mass", errors)
    require(meta.get("shared_variables") == shared_meta["variables"], "shared variable count", errors)
    require(meta.get("variables") == variables, "total variable count", errors)
    require(meta.get("clauses") == rebuilt_clauses, "clause count", errors)
    require(meta.get("selectors") == 188, "selector count", errors)
    require(meta.get("selector_core_implications") == sum(map(len, cores)), "core implication count", errors)
    require(cnf_hash == rebuilt_hash == meta.get("cnf_sha256"), "rebuilt DIMACS hash", errors)
    require(proof_hash == meta.get("proof_sha256"), "proof hash", errors)
    require(meta.get("terminal_empty_clause_appended_for_external_check") is False, "synthetic empty clause marker", errors)
    require(drat.get("ok") is True and drat.get("status") == "DRAT_VERIFIED", "DRAT audit failed", errors)
    require(drat.get("return_code") == 0 and "s VERIFIED" in drat.get("transcript", ""), "DRAT transcript", errors)
    require(drat.get("cnf_sha256") == cnf_hash, "DRAT CNF hash", errors)
    require(drat.get("proof_sha256") == proof_hash, "DRAT proof hash", errors)
    require(drat.get("producer_metadata_sha256") == sha256(META), "DRAT metadata hash", errors)

    result = {
        "status": "FORMAL_COMPUTER_ASSISTED_EXCLUSION_VERIFIED" if not errors else "AUDIT_FAILED",
        "ok": not errors,
        "errors": errors,
        "theorem": "Assuming an srg(99,14,1,2), the root selected by the self-contained S(r)<=69 theorem cannot have E0=74.",
        "root_bridge": "For the selected root Q=E0-S, so E0=74 and S<=69 imply Q>=5.",
        "logical_chain": [
            "the trace/triangle argument guarantees a root with S(r)<=69",
            "E0=74 therefore forces Q>=5",
            "complete compression and independent port/local audits cover every Q>=5 state and leave 188 local graph orbits of mass 16384",
            "the exact SRG CNF plus each complete local assignment is covered by a selector/core implication",
            "the rebuilt selector CNF is byte-for-byte hash identical to the formula whose DRUP trace drat-trim verified",
            "therefore all necessary local representatives are impossible",
        ],
        "coverage_totals": {
            "labelled_deficit_placements": 28_929_495,
            "weighted_support_orbits": 8_680,
            "compression_survivors": 249,
            "labelled_fibre_state_assignments": 134_371_022,
            "Q_at_least_5_port_feasible_states": 89,
            "exact_overlap_completions": 1_461_248,
            "raw_local_survivors": 16_384,
            "local_graph_orbits": 188,
            "formally_proved_unsat_branches": 188,
        },
        "selector_formula": {
            "shared_variables": shared_meta["variables"],
            "selectors": len(selectors),
            "variables": variables,
            "clauses": rebuilt_clauses,
            "core_implications": sum(map(len, cores)),
            "cnf": str(actual_cnf),
            "cnf_sha256": cnf_hash,
            "proof": str(actual_proof),
            "proof_sha256": proof_hash,
            "drat_audit": str(DRAT),
            "drat_audit_sha256": sha256(DRAT),
        },
        "checker_fingerprint": {
            "binary_sha256": drat.get("checker_sha256"),
            "source_sha256": drat.get("checker_source_sha256"),
            "upstream_commit": drat.get("checker_upstream_commit"),
            "local_patch_scope": drat.get("checker_local_patch"),
        },
        "artifact_sha256": hashes,
        "claim_boundary": "This excludes only the selected-root E0=74 branch; lower E0 branches remain.",
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    SUMMARY.write_text(
        "# Formal E0=74, Q>=5 exclusion audit\n\n"
        f"Status: `{result['status']}`  \n"
        f"Errors: `{len(errors)}`  \n"
        "Covered: `188` local orbits / `16384` labelled local graphs.  \n"
        "The selector CNF was rebuilt byte-for-byte and its hash-bound DRUP "
        "proof was accepted by drat-trim.\n\n"
        "The certified conclusion is that the self-contained selected root "
        "cannot have E0=74; lower E0 branches remain.\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "status": result["status"],
        "errors": len(errors),
        "branches": len(branches),
        "labelled_local_graphs": orbit_mass,
    }, sort_keys=True))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
