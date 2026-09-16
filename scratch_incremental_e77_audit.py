"""Rebuild and audit the finalized E77 incremental validation artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from scratch_incremental_local_exact_sat import build_shared_cnf, normalize_source


SOURCE = Path("scratch_general_e77_local_reps.json")
RESULT = Path("scratch_incremental_e77_exact_sat.json")
PORT_AUDIT = Path("scratch_e77_ports_audit.json")
OUTPUT = Path("scratch_incremental_e77_audit.json")
SUMMARY = Path("scratch_incremental_e77_exact_sat_summary.md")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main():
    source = normalize_source(SOURCE)
    clauses, _edge, _variables, _full, branches, meta = build_shared_cnf(source)
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    errors = []

    def require(condition, message):
        if not condition:
            errors.append(message)

    require(result["status"] == "UNSAT", "overall status is not UNSAT")
    require(result.get("checkpoint_complete") is True, "checkpoint is incomplete")
    require(result.get("all_available_reference_statuses_match") is True, "reference mismatch")
    require(result["shared_cnf_meta"] == json.loads(json.dumps(meta)), "rebuild metadata mismatch")
    require(len(clauses) == meta["clauses"], "clause recount mismatch")
    require(meta["representative_count"] == len(branches) == 3, "representative count mismatch")
    require(meta["local_edge_variables"] == 202, "local variable count mismatch")
    require(meta["bp_equalities"] == 1176, "BP count mismatch")
    require(meta["outer_pair_equalities"] == 3486, "outer-pair count mismatch")
    require(meta["redundant_support_aggregate_rows"] == 0, "redundant support rows present")
    require(meta["empty_clauses_before_assumptions"] == 0, "shared empty clause present")
    require(len(result["records"]) == 3, "result branch count mismatch")
    for branch, record in zip(branches, result["records"]):
        assumptions = frozenset(branch["assumptions"])
        core = frozenset(record.get("assumption_core", []))
        require(record["branch_index"] == branch["branch_index"], "branch order mismatch")
        require(record["representative_id"] == branch["representative_id"], "representative ID mismatch")
        require(record["orbit_size"] == branch["orbit_size"], "orbit size mismatch")
        require(record["assumption_sha256"] == branch["assumption_sha256"], "assumption hash mismatch")
        require(record["assumption_count"] == len(assumptions) == 202, "incomplete assumption vector")
        require(record["positive_assumptions"] == 35, "positive assumption count mismatch")
        require(record["negative_assumptions"] == 167, "negative assumption count mismatch")
        require(record["status"] == record["logical_status"] == "UNSAT", "branch not direct UNSAT")
        require(record["resolution"] == "CADICAL", "branch was not solved directly")
        require(bool(core) and core <= assumptions, "invalid assumption core")

    references = result["reference_portfolios"]
    require(len(references) == 2, "expected two reference portfolios")
    require(all(
        list(reference["branch_statuses"].values()) == ["UNSAT", "UNSAT", "UNSAT"]
        for reference in references
    ), "reference branch statuses differ")
    port_audit = json.loads(PORT_AUDIT.read_text(encoding="utf-8"))
    # The port audit and normalized E77 record independently agree on the
    # 512 labelled local graphs and three orbit sizes 256,128,128.
    orbit_sizes = [record["orbit_size"] for record in result["records"]]
    require(orbit_sizes == [256, 128, 128], "E77 orbit sizes mismatch")
    require(sum(orbit_sizes) == 512, "E77 labelled local count mismatch")
    port_orbit22 = [
        row for row in port_audit["local_survivors"] if row["orbit_index"] == 22
    ]
    require(len(port_orbit22) == 1, "port audit has no unique orbit-22 row")
    if len(port_orbit22) == 1:
        quotient = port_orbit22[0]["after_forced_ordinary_C4_support_BP_quotient"]
        require(port_orbit22[0]["after_forced_ordinary_C4_support_BP"] == 512, "port audit final count mismatch")
        require(quotient["orbit_count"] == 3, "port audit quotient count mismatch")
        require([row["size"] for row in quotient["orbits"]] == orbit_sizes, "port/incremental orbit size mismatch")

    audit = {
        "model": "audit of finalized E77 incremental exact-SAT validation",
        "source": str(SOURCE),
        "source_sha256": digest(SOURCE),
        "result": str(RESULT),
        "result_sha256": digest(RESULT),
        "port_audit": str(PORT_AUDIT),
        "port_audit_sha256": digest(PORT_AUDIT),
        "support_form": source["support_form"],
        "labelled_local_graphs": sum(orbit_sizes),
        "local_orbits": len(orbit_sizes),
        "orbit_sizes": orbit_sizes,
        "shared_cnf_meta": meta,
        "records": [{
            "branch_index": record["branch_index"],
            "orbit_size": record["orbit_size"],
            "assumption_sha256": record["assumption_sha256"],
            "positive_assumptions": record["positive_assumptions"],
            "negative_assumptions": record["negative_assumptions"],
            "status": record["status"],
            "solve_seconds": record["solve_seconds"],
            "conflicts": record["incremental_stats_delta"]["conflicts"],
            "assumption_core_size": record["assumption_core_size"],
        } for record in result["records"]],
        "reference_portfolios": references,
        "errors": errors,
        "ok": not errors,
        "claim_boundary": (
            "The shared CNF and complete assumption vectors were rebuilt and "
            "checked; direct CaDiCaL UNSAT answers have no independently checked "
            "proof certificates."
        ),
    }
    OUTPUT.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")

    rows = []
    for record in audit["records"]:
        rows.append(
            f"| {record['branch_index']} | {record['orbit_size']} | "
            f"{record['positive_assumptions']} / {record['negative_assumptions']} | "
            f"{record['conflicts']} | {record['solve_seconds']:.3f} | "
            f"{record['assumption_core_size']} | {record['status']} |"
        )
    summary = "\n".join([
        "# E77 validation of the incremental local-representative exact SAT base",
        "",
        "Result: all three E77 orbit-22 local representatives are direct CaDiCaL "
        "UNSAT in one shared solver instance, agreeing branch-for-branch with both "
        "older independent portfolios.",
        "",
        "| branch | orbit size | assumptions (+/-) | conflicts | solve s | core | status |",
        "|---:|---:|---:|---:|---:|---:|---|",
        *rows,
        "",
        "The three orbit sizes 256, 128, 128 cover all 512 labelled local graphs "
        "retained by the separate E77 port audit.",
        "",
        f"Shared model: {meta['variables']} variables, {meta['clauses']} clauses, "
        f"{meta['local_edge_variables']} exceptional same/overlap edge variables, "
        f"{meta['disjoint_edge_variables']} disjoint edge variables, "
        f"{meta['bp_equalities']} BP equalities, and "
        f"{meta['outer_pair_equalities']} outer-pair equalities. Redundant "
        "support-aggregate rows: 0.",
        "",
        "Every branch fixes all 202 local variables by 35 positive and 167 negative "
        "assumptions. The audit rebuilds their hashes and checks every returned "
        "assumption core is a subset of its full assignment.",
        "",
        "Boundary: these are computational UNSAT answers without separately emitted "
        "and independently checked proof certificates.",
        "",
        "Artifacts: `scratch_incremental_local_exact_sat.py`, "
        "`scratch_incremental_e77_exact_sat.json`, "
        "`scratch_incremental_e77_audit.json`, and this summary.",
        "",
    ])
    SUMMARY.write_text(summary, encoding="utf-8")
    print(json.dumps({"ok": audit["ok"], "errors": errors}, sort_keys=True))


if __name__ == "__main__":
    main()
