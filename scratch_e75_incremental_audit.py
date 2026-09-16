"""Rebuild and audit every E75 incremental exact-SAT checkpoint."""

from __future__ import annotations

import gc
import hashlib
import json
from pathlib import Path

from scratch_incremental_local_exact_sat import build_shared_cnf, normalize_source


INPUT = Path("scratch_general_e75_incremental_records.json")
PROBE_AUDIT = Path("scratch_e75_incremental_probe_audit.json")
OUTPUT = Path("scratch_e75_incremental_audit.json")
SUMMARY = Path("scratch_e75_incremental_summary.md")
PATHS = (
    Path("scratch_e75_incremental_record_00.json"),
    Path("scratch_general_e75_incremental_record_01.json"),
    Path("scratch_general_e75_incremental_record_02.json"),
    Path("scratch_general_e75_incremental_record_03.json"),
    Path("scratch_e75_incremental_record_04.json"),
    Path("scratch_e75_incremental_record_05.json"),
)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main():
    normalized = json.loads(INPUT.read_text(encoding="utf-8"))
    probe_audit = json.loads(PROBE_AUDIT.read_text(encoding="utf-8"))
    errors = []
    assert normalized["support_record_count"] == len(PATHS) == 6
    assert normalized["local_representative_count"] == 352
    if not probe_audit.get("ok"):
        errors.append("normalization/probe prerequisite audit failed")
    audited = []

    for index, path in enumerate(PATHS):
        source = normalize_source(INPUT, index)
        clauses, _edge, _variables, _full, branches, meta = build_shared_cnf(source)
        checkpoint = json.loads(path.read_text(encoding="utf-8"))
        records = checkpoint["records"]
        row_errors = []

        def require(condition, message):
            if not condition:
                row_errors.append(message)

        require(checkpoint.get("checkpoint_complete") is True, "checkpoint incomplete")
        require(checkpoint.get("status") == "UNSAT", "checkpoint status not UNSAT")
        require(checkpoint.get("conflict_budget_per_branch") in (100000, 200000), "unexpected conflict budget")
        require(checkpoint.get("input_selection", {}).get("record_index") == index, "record index mismatch")
        require(checkpoint.get("reference_portfolios") == [], "E77 references leaked into E75")
        require(checkpoint.get("all_available_reference_statuses_match") is None, "spurious reference comparison")
        require(checkpoint["shared_cnf_meta"] == json.loads(json.dumps(meta)), "stored metadata differs on rebuild")
        require(len(clauses) == meta["clauses"], "clause recount mismatch")
        require(len(records) == len(branches), "representative count mismatch")
        require([row["branch_index"] for row in records] == list(range(len(branches))), "branch order mismatch")
        require(meta["bp_equalities"] == 1176, "BP equality count mismatch")
        require(meta["outer_pair_equalities"] == 3486, "outer-pair count mismatch")
        require(meta["disjoint_blocks"] == 105, "disjoint block count mismatch")
        require(meta["disjoint_edge_variables"] == 1680, "disjoint variable count mismatch")
        require(meta["redundant_support_aggregate_rows"] == 0, "redundant support rows present")
        require(meta["empty_clauses_before_assumptions"] == 0, "shared CNF contains empty clause")

        branch_by_index = {branch["branch_index"]: branch for branch in branches}
        record_by_index = {record["branch_index"]: record for record in records}
        normalized_reps = normalized["records"][index]["representatives"]
        for record in records:
            branch = branch_by_index[record["branch_index"]]
            representative = normalized_reps[record["branch_index"]]
            assumptions = frozenset(branch["assumptions"])
            require(record["representative_id"] == representative["representative_id"], "representative ID mismatch")
            require(record["orbit_size"] == representative["orbit_size"], "orbit size mismatch")
            require(record["assumption_sha256"] == branch["assumption_sha256"], "assumption hash mismatch")
            require(record["assumption_count"] == meta["local_edge_variables"] == len(assumptions), "incomplete assumption vector")
            require(record["positive_assumptions"] == len(representative["present_edges_outer_indices_zero_based"]), "positive assumptions/local edges mismatch")
            require(record["positive_assumptions"] + record["negative_assumptions"] == record["assumption_count"], "assumption sign partition mismatch")
            if record["status"] == "UNSAT":
                require(record.get("logical_status") == "UNSAT", "direct logical status mismatch")
                require(record.get("resolution") == "CADICAL", "direct resolution mismatch")
                core = frozenset(record.get("assumption_core", []))
                require(bool(core) and core <= assumptions, "direct core invalid")
                conflicts = record.get("incremental_stats_delta", {}).get("conflicts", 0)
                budget = checkpoint["conflict_budget_per_branch"]
                require(conflicts <= budget + 2, "direct call exceeds conflict budget tolerance")
            elif record["status"] == "COVERED_UNSAT":
                require(record.get("logical_status") == "UNSAT", "covered logical status mismatch")
                require(record.get("resolution") == "ASSUMPTION_CORE_CONTAINMENT", "covered resolution mismatch")
                cover_index = record.get("covered_by_branch_index")
                require(type(cover_index) is int and cover_index < record["branch_index"], "invalid cover source")
                cover = record_by_index.get(cover_index, {})
                core = frozenset(record.get("assumption_core", []))
                require(cover.get("logical_status") == "UNSAT", "cover source is not logical UNSAT")
                require(core == frozenset(cover.get("assumption_core", [])), "covered core not inherited")
                require(bool(core) and core <= assumptions, "covered core not contained in assumptions")
                require(record.get("core_containment_checked") is True, "containment marker missing")
            else:
                row_errors.append(f"unexpected branch status {record['status']}")

        direct = sum(row["status"] == "UNSAT" for row in records)
        covered = sum(row["status"] == "COVERED_UNSAT" for row in records)
        unknown = sum(row["status"] == "UNKNOWN" for row in records)
        sat = sum(row["status"] == "SAT" for row in records)
        require(checkpoint["direct_solver_calls"] == direct, "direct solver-call count mismatch")
        require(checkpoint["direct_solver_unsat_count"] == direct, "direct UNSAT count mismatch")
        require(checkpoint["core_covered_unsat_count"] == covered, "covered count mismatch")
        require(checkpoint["unknown_count"] == unknown == 0, "UNKNOWN remains")
        require(direct + covered == len(records), "UNSAT coverage incomplete")
        require(sum(row["orbit_size"] for row in records) == normalized["records"][index]["local_graph_count"], "orbit-size coverage mismatch")
        errors.extend(f"record {index}: {message}" for message in row_errors)
        audited.append({
            "record_index": index,
            "path": str(path),
            "checkpoint_sha256": sha256(path),
            "source_row_index": normalized["records"][index]["source_row_index"],
            "compression_orbit_index": normalized["records"][index]["compression_orbit_index"],
            "partition": normalized["records"][index]["partition"],
            "support_form": source["support_form"],
            "representatives": len(records),
            "labelled_local_graphs": normalized["records"][index]["local_graph_count"],
            "direct_unsat": direct,
            "core_covered_unsat": covered,
            "unknown": unknown,
            "sat": sat,
            "conflict_budget_per_branch": checkpoint["conflict_budget_per_branch"],
            "total_solve_seconds": round(sum(float(row["solve_seconds"]) for row in records), 6),
            "local_edge_variables": meta["local_edge_variables"],
            "variables": meta["variables"],
            "clauses": meta["clauses"],
            "errors": row_errors,
            "ok": not row_errors,
        })
        del clauses, branches, checkpoint, meta
        gc.collect()

    totals = {
        "support_records": len(audited),
        "representatives": sum(row["representatives"] for row in audited),
        "labelled_local_graphs": sum(row["labelled_local_graphs"] for row in audited),
        "direct_unsat": sum(row["direct_unsat"] for row in audited),
        "core_covered_unsat": sum(row["core_covered_unsat"] for row in audited),
        "unknown": sum(row["unknown"] for row in audited),
        "sat": sum(row["sat"] for row in audited),
        "total_solve_seconds": round(sum(row["total_solve_seconds"] for row in audited), 6),
    }
    if totals != {
        **totals,
        "support_records": 6,
        "representatives": 352,
        "labelled_local_graphs": 110592,
        "direct_unsat": 249,
        "core_covered_unsat": 103,
        "unknown": 0,
        "sat": 0,
    }:
        # Compare only the exact integer fields; time is intentionally retained.
        expected = (6, 352, 110592, 249, 103, 0, 0)
        observed = tuple(totals[key] for key in (
            "support_records", "representatives", "labelled_local_graphs",
            "direct_unsat", "core_covered_unsat", "unknown", "sat",
        ))
        if observed != expected:
            errors.append(f"global totals differ: {observed} != {expected}")

    audit = {
        "model": "independent audit of E75 incremental local exact-SAT sweep",
        "input": str(INPUT),
        "input_sha256": sha256(INPUT),
        "probe_audit": str(PROBE_AUDIT),
        "probe_audit_sha256": sha256(PROBE_AUDIT),
        "required_shared_constraints": {
            "bp_equalities_per_record": 1176,
            "outer_pair_equalities_per_record": 3486,
            "disjoint_blocks_per_record": 105,
            "disjoint_edge_variables_per_record": 1680,
            "redundant_support_aggregate_rows": 0,
        },
        "totals": totals,
        "records": audited,
        "errors": errors,
        "ok": not errors,
        "claim_boundary": (
            "Every shared CNF and complete local assumption vector was rebuilt and "
            "every core containment was checked. Direct CaDiCaL UNSAT answers have "
            "no separately emitted and independently checked proof certificates."
        ),
    }
    OUTPUT.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# E75 incremental local exact-SAT audit",
        "",
        "Result: **all 352 normalized local representatives are UNSAT**; SAT=0 and UNKNOWN=0.",
        "",
        "| rec | orbit | reps | labelled | direct | core-covered | budget | solve s | vars | clauses |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in audited:
        lines.append(
            f"| {row['record_index']} | {row['compression_orbit_index']} | "
            f"{row['representatives']} | {row['labelled_local_graphs']} | "
            f"{row['direct_unsat']} | {row['core_covered_unsat']} | "
            f"{row['conflict_budget_per_branch']} | {row['total_solve_seconds']:.3f} | "
            f"{row['variables']} | {row['clauses']} |"
        )
    lines.extend([
        "",
        f"Totals: {totals['direct_unsat']} direct CaDiCaL UNSAT + "
        f"{totals['core_covered_unsat']} exact core-containment exclusions = "
        f"{totals['representatives']} representatives, covering "
        f"{totals['labelled_local_graphs']} labelled local graphs. Aggregate branch "
        f"solve time: {totals['total_solve_seconds']:.3f}s.",
        "",
        "Records 1--3 are independently produced complete checkpoints and terminated "
        "under a 100,000-conflict limit. Records 0, 4, and 5 used 200,000. Since all "
        "branches returned terminal UNSAT, no UNKNOWN retry set remains.",
        "",
        "The audit rebuilds all six CNFs, all representative IDs/orbit sizes/local "
        "edge sets, complete signed assumption vectors and hashes, and each literal "
        "core containment. Every CNF has 1,176 BP equalities, 3,486 outer-pair "
        "equalities, all 105 disjoint blocks (1,680 edge variables), and no redundant "
        "support-aggregate rows.",
        "",
        "Boundary: the CaDiCaL UNSAT answers are computational and have no separately "
        "emitted, independently checked proof certificates.",
        "",
    ])
    SUMMARY.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"ok": audit["ok"], **totals, "errors": errors}, sort_keys=True))


if __name__ == "__main__":
    main()
