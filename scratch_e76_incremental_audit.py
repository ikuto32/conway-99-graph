"""Independent structural audit of the ten incremental E76 checkpoints."""

from __future__ import annotations

import gc
import hashlib
import json
from pathlib import Path

from scratch_incremental_local_exact_sat import build_shared_cnf, normalize_source


NORMALIZED = Path("scratch_e76_incremental_records.json")
INDEPENDENT = Path("scratch_e76_independent_local.json")
OUTPUT = Path("scratch_e76_incremental_audit.json")
SUMMARY = Path("scratch_e76_incremental_summary.md")
FIXED_CATALOG = Path("scratch_e76_fixed_exact_catalog.json")
FIXED_PORTFOLIO = Path("scratch_e76_fixed_exact_portfolio.json")
FIXED_CHECKPOINT = Path("scratch_e76_fixed_exact_checkpoint.json")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main():
    normalized = json.loads(NORMALIZED.read_text(encoding="utf-8"))
    independent = json.loads(INDEPENDENT.read_text(encoding="utf-8"))
    fixed_catalog = json.loads(FIXED_CATALOG.read_text(encoding="utf-8"))
    fixed_portfolio = json.loads(FIXED_PORTFOLIO.read_text(encoding="utf-8"))
    fixed_checkpoint = json.loads(FIXED_CHECKPOINT.read_text(encoding="utf-8"))
    assert normalized["support_record_count"] == independent["support_orbits_after_forced_BP"] == 10
    assert normalized["local_representative_count"] == independent["local_graph_orbits"] == 311
    assert fixed_catalog["branch_count"] == len(fixed_catalog["branches"]) == 311
    fixed_by_key = {}
    for item in fixed_catalog["branches"]:
        key = (
            int(item["source_row_index"]),
            int(item["compression_orbit_index"]),
            int(item["local_representative_index"]),
        )
        assert key not in fixed_by_key
        fixed_by_key[key] = item
    fixed_status_by_branch = {
        int(branch_index): attempts[-1]["status"]
        for branch_index, attempts in fixed_checkpoint["attempts"].items()
        if attempts
    }
    assert len(fixed_status_by_branch) == 311
    assert fixed_portfolio["cumulative_latest_count"] == 311
    matched_fixed_keys = set()

    audited = []
    global_errors = []
    for index in range(10):
        source = normalize_source(NORMALIZED, index)
        clauses, _edge, _edge_variables, _full_variables, branches, meta = build_shared_cnf(source)
        checkpoint_path = Path(f"scratch_e76_incremental_record_{index:02d}.json")
        checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        errors = []

        def require(condition, message):
            if not condition:
                errors.append(message)

        records = checkpoint["records"]
        require(checkpoint.get("checkpoint_complete") is True, "checkpoint not complete")
        require(checkpoint.get("status") == "UNSAT", "record status is not UNSAT")
        require(checkpoint.get("conflict_budget_per_branch") == 200000, "wrong conflict budget")
        require(checkpoint.get("input_selection", {}).get("record_index") == index, "record index mismatch")
        require(checkpoint.get("reference_portfolios") == [], "E77 references leaked into E76")
        require(checkpoint.get("all_available_reference_statuses_match") is None, "spurious reference match")
        require(len(records) == len(branches), "branch count mismatch")
        require([row["branch_index"] for row in records] == list(range(len(branches))), "branch order mismatch")
        # JSON object keys stringify the integer keys of pair_target_histogram.
        json_meta = json.loads(json.dumps(meta))
        require(checkpoint["shared_cnf_meta"] == json_meta, "stored CNF metadata differs on rebuild")
        require(len(clauses) == meta["clauses"], "clause recount mismatch")
        require(meta["bp_equalities"] == 1176, "BP equality count is not 1176")
        require(meta["outer_pair_equalities"] == 3486, "outer-pair equality count is not 3486")
        require(meta["disjoint_blocks"] == 105, "disjoint block count is not 105")
        require(meta["disjoint_edge_variables"] == 1680, "disjoint variable count is not 1680")
        require(meta["redundant_support_aggregate_rows"] == 0, "redundant support rows present")
        require(meta["empty_clauses_before_assumptions"] == 0, "shared CNF has an empty clause")

        branch_by_index = {row["branch_index"]: row for row in branches}
        record_by_index = {row["branch_index"]: row for row in records}
        for record in records:
            branch = branch_by_index[record["branch_index"]]
            normalized_rep = normalized["records"][index]["representatives"][record["branch_index"]]
            assumptions = frozenset(branch["assumptions"])
            require(record["representative_id"] == normalized_rep["representative_id"], "representative ID mismatch")
            require(record["orbit_size"] == normalized_rep["orbit_size"], "representative orbit size mismatch")
            require(record["assumption_sha256"] == branch["assumption_sha256"], "assumption hash mismatch")
            require(record["assumption_count"] == meta["local_edge_variables"], "incomplete assumptions")
            require(
                record["positive_assumptions"] + record["negative_assumptions"]
                == record["assumption_count"],
                "positive/negative assumption partition mismatch",
            )
            if record["status"] == "UNSAT":
                require(record.get("resolution") == "CADICAL", "direct UNSAT resolution mismatch")
                core = frozenset(record.get("assumption_core", []))
                require(bool(core), "direct UNSAT has empty assumption core")
                require(core <= assumptions, "direct core is not contained in its assumptions")
            elif record["status"] == "COVERED_UNSAT":
                require(
                    record.get("resolution") == "ASSUMPTION_CORE_CONTAINMENT",
                    "covered UNSAT resolution mismatch",
                )
                cover_index = record.get("covered_by_branch_index")
                require(type(cover_index) is int and cover_index < record["branch_index"], "invalid cover source")
                cover = record_by_index.get(cover_index, {})
                core = frozenset(record.get("assumption_core", []))
                require(cover.get("logical_status") == "UNSAT", "cover source is not logical UNSAT")
                require(core == frozenset(cover.get("assumption_core", [])), "covered core not inherited exactly")
                require(core <= assumptions, "cover core not contained in target assumptions")
                require(record.get("core_containment_checked") is True, "containment marker absent")
            else:
                errors.append(f"unexpected branch status {record['status']}")

            fixed_key = (
                int(normalized["records"][index]["source_row_index"]),
                int(normalized["records"][index]["compression_orbit_index"]),
                int(normalized_rep["representative_id"]),
            )
            fixed = fixed_by_key.get(fixed_key)
            require(fixed is not None, "representative key absent from fixed-CNF catalog")
            if fixed is not None:
                matched_fixed_keys.add(fixed_key)
                require(fixed["local_orbit_size"] == normalized_rep["orbit_size"], "fixed catalog orbit size mismatch")
                require(fixed["local_edge_count"] == record["positive_assumptions"], "fixed catalog edge count mismatch")
                require(fixed["partition"] == normalized["records"][index]["partition"], "fixed catalog partition mismatch")
                expected_supports = [
                    {"support": support, "deficit": deficit}
                    for support, deficit in zip(
                        normalized["records"][index]["supports_in_fibre_order"],
                        normalized["records"][index]["deficits_in_support_order"],
                    )
                ]
                actual_supports = [
                    {"support": item["support"], "deficit": item["deficit"]}
                    for item in fixed["exceptional_supports"]
                ]
                require(actual_supports == expected_supports, "fixed catalog support/deficit mismatch")
                fixed_status = fixed_status_by_branch.get(int(fixed["branch_index"]))
                require(fixed_status in ("UNSAT", "UNKNOWN"), "unexpected fixed-CNF status")

        direct = sum(row["status"] == "UNSAT" for row in records)
        covered = sum(row["status"] == "COVERED_UNSAT" for row in records)
        unknown = sum(row["status"] == "UNKNOWN" for row in records)
        solve_seconds = round(sum(float(row["solve_seconds"]) for row in records), 6)
        require(checkpoint["direct_solver_calls"] == direct, "direct call count mismatch")
        require(checkpoint["direct_solver_unsat_count"] == direct, "direct UNSAT count mismatch")
        require(checkpoint["core_covered_unsat_count"] == covered, "covered count mismatch")
        require(checkpoint["unknown_count"] == unknown == 0, "UNKNOWN branch remains")
        require(direct + covered == len(records), "UNSAT coverage is incomplete")
        require(all(
            row["positive_assumptions"] == len(source["representatives"][row["branch_index"]]["present_edges"])
            for row in records
        ), "positive assumption count differs from normalized local edge count")

        row = {
            "record_index": index,
            "source_row_index": normalized["records"][index]["source_row_index"],
            "compression_orbit_index": normalized["records"][index]["compression_orbit_index"],
            "partition": normalized["records"][index]["partition"],
            "support_form": source["support_form"],
            "representatives": len(records),
            "direct_unsat": direct,
            "core_covered_unsat": covered,
            "unknown": unknown,
            "sat": sum(item["status"] == "SAT" for item in records),
            "total_solve_seconds": solve_seconds,
            "variables": meta["variables"],
            "clauses": meta["clauses"],
            "local_edge_variables": meta["local_edge_variables"],
            "checkpoint_sha256": sha256(checkpoint_path),
            "errors": errors,
            "ok": not errors,
        }
        audited.append(row)
        global_errors.extend(f"record {index}: {message}" for message in errors)
        del clauses, branches, meta, checkpoint
        gc.collect()

    totals = {
        "support_records": len(audited),
        "representatives": sum(row["representatives"] for row in audited),
        "direct_unsat": sum(row["direct_unsat"] for row in audited),
        "core_covered_unsat": sum(row["core_covered_unsat"] for row in audited),
        "unknown": sum(row["unknown"] for row in audited),
        "sat": sum(row["sat"] for row in audited),
        "total_solve_seconds": round(sum(row["total_solve_seconds"] for row in audited), 6),
        "labelled_local_graphs_represented": sum(
            int(record["local_graph_count"]) for record in normalized["records"]
        ),
    }
    assert totals["representatives"] == 311
    assert totals["direct_unsat"] + totals["core_covered_unsat"] == 311
    assert totals["unknown"] == totals["sat"] == 0
    if matched_fixed_keys != set(fixed_by_key):
        global_errors.append("incremental/fixed-CNF catalog key sets are not identical")
    result = {
        "model": "independent audit of E76 incremental local exact-SAT sweep",
        "normalized_input": str(NORMALIZED),
        "normalized_input_sha256": sha256(NORMALIZED),
        "independent_source": str(INDEPENDENT),
        "independent_source_sha256": sha256(INDEPENDENT),
        "fixed_cnf_catalog": str(FIXED_CATALOG),
        "fixed_cnf_catalog_sha256": sha256(FIXED_CATALOG),
        "fixed_cnf_portfolio": str(FIXED_PORTFOLIO),
        "fixed_cnf_portfolio_sha256": sha256(FIXED_PORTFOLIO),
        "fixed_cnf_checkpoint": str(FIXED_CHECKPOINT),
        "fixed_cnf_checkpoint_sha256": sha256(FIXED_CHECKPOINT),
        "fixed_cnf_catalog_comparison": {
            "catalog_branches": len(fixed_by_key),
            "keys_matched": len(matched_fixed_keys),
            "portfolio_status_counts_at_audit": {
                status: sum(value == status for value in fixed_status_by_branch.values())
                for status in sorted(set(fixed_status_by_branch.values()))
            },
            "all_fixed_terminal_results_agree": all(
                value == "UNSAT"
                for value in fixed_status_by_branch.values()
                if value != "UNKNOWN"
            ),
        },
        "coverage": independent["coverage"],
        "required_shared_constraints": {
            "bp_equalities_per_record": 1176,
            "outer_pair_equalities_per_record": 3486,
            "disjoint_blocks_per_record": 105,
            "disjoint_edge_variables_per_record": 1680,
            "redundant_support_aggregate_rows": 0,
        },
        "totals": totals,
        "records": audited,
        "errors": global_errors,
        "ok": not global_errors,
        "claim_boundary": (
            "This audit rebuilds every shared CNF and complete assumption vector, "
            "and checks every recorded core-containment deduction. Direct CaDiCaL "
            "UNSAT results do not carry independently checked proof certificates."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    table = [
        "| rec | source row | compression orbit | reps | direct | core-covered | unknown | solve s | vars | clauses |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in audited:
        table.append(
            f"| {row['record_index']} | {row['source_row_index']} | "
            f"{row['compression_orbit_index']} | {row['representatives']} | "
            f"{row['direct_unsat']} | {row['core_covered_unsat']} | "
            f"{row['unknown']} | {row['total_solve_seconds']:.3f} | "
            f"{row['variables']} | {row['clauses']} |"
        )
    summary = "\n".join([
        "# E76 incremental local exact-SAT audit",
        "",
        "Result: **all 311 normalized local representatives are UNSAT**. "
        "There are no SAT or UNKNOWN branches.",
        "",
        *table,
        "",
        f"Totals: {totals['direct_unsat']} direct CaDiCaL UNSAT + "
        f"{totals['core_covered_unsat']} exact assumption-core containments = "
        f"{totals['representatives']} excluded representatives; "
        f"{totals['total_solve_seconds']:.3f} aggregate branch solve seconds.",
        f"The orbit sizes cover {totals['labelled_local_graphs_represented']} labelled "
        "local graphs on the ten canonical support records.",
        "",
        "For every support record the shared instance contains all 1,176 BP "
        "equalities, all 3,486 outer-pair equalities, all 105 disjoint blocks "
        "(1,680 edge variables), and zero redundant support-aggregate rows. "
        "Every local representative fixes every exceptional same/overlap edge "
        "variable by a complete signed assumption vector.",
        "",
        "A `COVERED_UNSAT` row is used only when a previously returned UNSAT "
        "assumption core is literally a subset of the new complete assignment. "
        "The audit reconstructs and checks each such containment.",
        "",
        f"Fixed-CNF catalog crosswalk: all {len(fixed_by_key)} keys "
        "`(source row, compression orbit, local representative ID)` match, including "
        "partition, ordered support/deficit data, orbit size, and local edge count. "
        f"At audit time its portfolio statuses were {result['fixed_cnf_catalog_comparison']['portfolio_status_counts_at_audit']}; "
        "every independently terminal fixed-CNF result agrees.",
        "",
        "Boundary: direct UNSAT answers are computational CaDiCaL results without "
        "separately emitted and checked proof certificates.",
        "",
    ])
    SUMMARY.write_text(summary, encoding="utf-8")
    print(json.dumps({"ok": result["ok"], **totals}, sort_keys=True))


if __name__ == "__main__":
    main()
