"""Audit E75 normalization and the six existing first-representative probes."""

from __future__ import annotations

import gc
import hashlib
import json
from pathlib import Path

from scratch_incremental_local_exact_sat import build_shared_cnf, normalize_source


FULL = Path("scratch_general_e75_incremental_records.json")
PROBES = Path("scratch_general_e75_incremental_probe_records.json")
OUTPUT = Path("scratch_e75_incremental_probe_audit.json")
SUMMARY = Path("scratch_e75_incremental_probe_audit_summary.md")

PREREQUISITES = {
    "compression": (Path("scratch_general_e75_compression_audit.json"), "COMPLETE"),
    "port": (Path("scratch_general_e75_port_audit.json"), "COMPLETE"),
    "port_group": (Path("scratch_general_e75_port_group_check.json"), "VERIFIED"),
    "representatives": (Path("scratch_general_e75_reps_check.json"), "VERIFIED"),
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def json_form(value):
    return json.loads(json.dumps(value))


def structural_meta(meta):
    ignored = {
        "input", "input_selection", "support_form", "representative_count",
        "branch_assumption_summaries",
    }
    return {key: value for key, value in json_form(meta).items() if key not in ignored}


def main():
    errors = []

    def require(condition, message):
        if not condition:
            errors.append(message)

    prerequisites = {}
    for name, (path, wanted) in PREREQUISITES.items():
        document = json.loads(path.read_text(encoding="utf-8"))
        prerequisites[name] = {
            "path": str(path), "sha256": sha256(path),
            "status": document.get("status"), "required_status": wanted,
        }
        require(document.get("status") == wanted, f"{name} prerequisite not {wanted}")

    full_document = json.loads(FULL.read_text(encoding="utf-8"))
    probe_document = json.loads(PROBES.read_text(encoding="utf-8"))
    require(full_document.get("status") == "COMPLETE", "normalized input incomplete")
    require(full_document.get("support_record_count") == 6, "support record count mismatch")
    require(full_document.get("local_representative_count") == 352, "representative count mismatch")
    require(full_document.get("labelled_local_graphs_represented") == 110592, "labelled count mismatch")
    require(probe_document.get("support_record_count") == 6, "probe record count mismatch")

    rows = []
    for index in range(6):
        full_source = normalize_source(FULL, index)
        probe_source = normalize_source(PROBES, index)
        full_clauses, _edge, _variables, _full, full_branches, full_meta = build_shared_cnf(full_source)
        probe_clauses, _edge2, _variables2, _full2, probe_branches, probe_meta = build_shared_cnf(probe_source)
        path = Path(f"scratch_general_e75_probe_record_{index:02d}.json")
        prior = json.loads(path.read_text(encoding="utf-8"))
        row_errors = []

        def row_require(condition, message):
            if not condition:
                row_errors.append(message)

        row_require(len(probe_branches) == 1, "probe does not contain one branch")
        row_require(full_branches[0]["assumptions"] == probe_branches[0]["assumptions"], "first assumptions differ")
        row_require(full_branches[0]["assumption_sha256"] == probe_branches[0]["assumption_sha256"], "first hash differs")
        row_require(structural_meta(full_meta) == structural_meta(probe_meta), "full/probe structural metadata differ")
        row_require(len(full_clauses) == len(probe_clauses), "full/probe clause count differs")
        row_require(prior["shared_cnf_meta"] == json_form(probe_meta), "stored probe metadata differs on rebuild")
        row_require(len(prior["records"]) == 1, "stored probe result branch count differs")
        stored = prior["records"][0]
        rebuilt = probe_branches[0]
        row_require(stored["representative_id"] == rebuilt["representative_id"] == 0, "probe representative ID mismatch")
        row_require(stored["orbit_size"] == rebuilt["orbit_size"], "probe orbit size mismatch")
        row_require(stored["assumption_sha256"] == rebuilt["assumption_sha256"], "stored assumption hash mismatch")
        row_require(stored["assumption_count"] == probe_meta["local_edge_variables"], "incomplete probe assumptions")
        row_require(stored["positive_assumptions"] + stored["negative_assumptions"] == stored["assumption_count"], "probe sign count mismatch")
        row_require(probe_meta["bp_equalities"] == 1176, "BP count mismatch")
        row_require(probe_meta["outer_pair_equalities"] == 3486, "outer-pair count mismatch")
        row_require(probe_meta["disjoint_edge_variables"] == 1680, "disjoint variable count mismatch")
        row_require(probe_meta["redundant_support_aggregate_rows"] == 0, "redundant support rows present")
        row_require(probe_meta["empty_clauses_before_assumptions"] == 0, "empty clause in shared CNF")
        errors.extend(f"record {index}: {message}" for message in row_errors)
        rows.append({
            "record_index": index,
            "support_form": full_source["support_form"],
            "representatives": len(full_branches),
            "labelled_local_graphs": full_document["records"][index]["local_graph_count"],
            "local_edge_variables": full_meta["local_edge_variables"],
            "variables": full_meta["variables"],
            "clauses": full_meta["clauses"],
            "first_representative_id": rebuilt["representative_id"],
            "first_orbit_size": rebuilt["orbit_size"],
            "first_assumption_sha256": rebuilt["assumption_sha256"],
            "existing_probe_status": stored["status"],
            "existing_probe_conflicts": stored["incremental_stats_delta"]["conflicts"],
            "probe_result_sha256": sha256(path),
            "errors": row_errors,
            "ok": not row_errors,
        })
        del full_clauses, probe_clauses, full_branches, probe_branches, full_meta, probe_meta
        gc.collect()

    audit = {
        "model": "E75 generic incremental normalization and probe audit",
        "prerequisites": prerequisites,
        "normalized_input": str(FULL),
        "normalized_input_sha256": sha256(FULL),
        "probe_input": str(PROBES),
        "probe_input_sha256": sha256(PROBES),
        "support_records": len(rows),
        "representatives": sum(row["representatives"] for row in rows),
        "labelled_local_graphs": sum(row["labelled_local_graphs"] for row in rows),
        "rows": rows,
        "errors": errors,
        "ok": not errors,
        "claim_boundary": (
            "This validates reconstruction coverage, exact normalization, shared-CNF "
            "metadata, and first-representative assumption hashes; it does not turn "
            "solver UNSAT answers into proof-certified results."
        ),
    }
    OUTPUT.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# E75 incremental normalization / probe audit",
        "",
        f"Status: **{'OK' if audit['ok'] else 'FAILED'}**. The six support records contain "
        f"{audit['representatives']} orbit representatives covering "
        f"{audit['labelled_local_graphs']} labelled local graphs.",
        "",
        "| rec | reps | labelled | local vars | vars | clauses | probe status | hash |",
        "|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['record_index']} | {row['representatives']} | "
            f"{row['labelled_local_graphs']} | {row['local_edge_variables']} | "
            f"{row['variables']} | {row['clauses']} | {row['existing_probe_status']} | "
            f"`{row['first_assumption_sha256'][:16]}...` |"
        )
    lines.extend([
        "",
        "For every record, rebuilding the one-representative probe reproduces its "
        "entire stored model metadata and assumption hash. Rebuilding the complete "
        "record has identical structural metadata; only the declared input and "
        "representative-summary fields differ.",
        "",
        "All prerequisite reconstruction audits have their required COMPLETE/VERIFIED "
        "status. Every shared CNF has all 1,176 BP equalities, all 3,486 outer-pair "
        "equalities, 1,680 disjoint edge variables, and no redundant support rows.",
        "",
        "Boundary: direct UNSAT results remain computational unless accompanied by a "
        "separately emitted and independently checked proof certificate.",
        "",
    ])
    SUMMARY.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({
        "ok": audit["ok"], "records": audit["support_records"],
        "representatives": audit["representatives"],
        "labelled_local_graphs": audit["labelled_local_graphs"],
        "errors": errors,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
