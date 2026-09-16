"""Audit six bounded E75 first-representative exact-SAT probes."""

from __future__ import annotations

import gc
import json
from pathlib import Path

from scratch_incremental_local_exact_sat import build_shared_cnf, normalize_source


FULL_PATH = Path("scratch_general_e75_incremental_records.json")
PROBE_PATH = Path("scratch_general_e75_incremental_probe_records.json")
OUTPUT_PATH = Path("scratch_general_e75_probe_audit.json")
SUMMARY_PATH = Path("scratch_general_e75_probe_summary.md")


def main():
    full_document = json.loads(FULL_PATH.read_text(encoding="utf-8"))
    probe_document = json.loads(PROBE_PATH.read_text(encoding="utf-8"))
    assert full_document["support_record_count"] == 6
    assert full_document["local_representative_count"] == 352
    assert probe_document["status"] == "PROBE_ONLY"
    rows = []
    for index in range(6):
        full = normalize_source(FULL_PATH, index)
        probe = normalize_source(PROBE_PATH, index)
        full_clauses, _edge, _variables, _all, full_branches, full_meta = build_shared_cnf(full)
        probe_clauses, _edge, _variables, _all, probe_branches, probe_meta = build_shared_cnf(probe)
        checkpoint_path = Path(f"scratch_general_e75_probe_record_{index:02d}.json")
        checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        assert len(probe_branches) == 1
        assert probe_branches[0]["assumption_sha256"] == full_branches[0][
            "assumption_sha256"
        ]
        assert probe_branches[0]["assumptions"] == full_branches[0]["assumptions"]
        assert len(probe_clauses) == len(full_clauses)
        assert checkpoint["shared_cnf_meta"] == json.loads(json.dumps(probe_meta))
        meta = checkpoint["shared_cnf_meta"]
        assert meta["redundant_support_aggregate_rows"] == 0
        assert meta["bp_equalities"] == 1176
        assert meta["outer_pair_equalities"] == 3486
        assert meta["disjoint_blocks"] == 105
        assert meta["disjoint_edge_variables"] == 1680
        assert meta["empty_clauses_before_assumptions"] == 0
        assert checkpoint["checkpoint_complete"]
        assert checkpoint["completed_branch_count"] == 1
        record = checkpoint["records"][0]
        assert record["branch_index"] == 0
        assert record["assumption_sha256"] == full_branches[0]["assumption_sha256"]
        assert record["assumption_count"] == meta["local_edge_variables"]
        exceptional_count = len(full["supports_in_fibre_order"])
        assert record["positive_assumptions"] == 4 * exceptional_count + 9
        assert record["status"] in ("UNSAT", "UNKNOWN")
        assert record["formal_proof_certificate"] is None
        rows.append(
            {
                "record_index": index,
                "support_form": full_document["records"][index]["support_form"],
                "partition": full_document["records"][index]["partition"],
                "compression_orbit_index": full_document["records"][index][
                    "compression_orbit_index"
                ],
                "full_representatives": len(full_branches),
                "probe_representative_id": record["representative_id"],
                "probe_assumption_sha256": record["assumption_sha256"],
                "probe_matches_full_first_assumptions": True,
                "status": record["status"],
                "solve_seconds": record["solve_seconds"],
                "conflicts": record["incremental_stats_delta"].get("conflicts"),
                "variables": meta["variables"],
                "clauses": meta["clauses"],
                "local_edge_variables": meta["local_edge_variables"],
                "positive_assumptions": record["positive_assumptions"],
                "redundant_support_aggregate_rows": 0,
            }
        )
        del full_clauses, probe_clauses, full_branches, probe_branches
        gc.collect()
    statuses = {status: sum(row["status"] == status for row in rows) for status in ("UNSAT", "UNKNOWN", "SAT")}
    assert statuses == {"UNSAT": 5, "UNKNOWN": 1, "SAT": 0}
    result = {
        "status": "PROBE_COMPLETE",
        "model": "audit of one exact-SAT probe per E0=75 local support row",
        "full_normalized_input": str(FULL_PATH),
        "probe_normalized_input": str(PROBE_PATH),
        "coverage_warning": (
            "Only the first representative of each support row was solved; "
            "this is not a complete E0=75 exclusion."
        ),
        "conflict_budget_per_probe": 100000,
        "status_counts": statuses,
        "all_probe_assumptions_match_full_first_branch": True,
        "required_shared_constraints": {
            "bp_equalities": 1176,
            "outer_pair_equalities": 3486,
            "disjoint_blocks": 105,
            "disjoint_edge_variables": 1680,
            "redundant_support_aggregate_rows": 0,
        },
        "rows": rows,
        "claim_boundary": "CaDiCaL results have no emitted independently checked proof certificates.",
    }
    OUTPUT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    table = [
        "| record | partition | compression orbit | full reps | status | solve s | conflicts | vars | clauses |",
        "|---:|---|---:|---:|---|---:|---:|---:|---:|",
    ]
    for row in rows:
        table.append(
            f"| {row['record_index']} | {'+'.join(map(str,row['partition']))} | "
            f"{row['compression_orbit_index']} | {row['full_representatives']} | "
            f"{row['status']} | {row['solve_seconds']:.3f} | {row['conflicts']} | "
            f"{row['variables']} | {row['clauses']} |"
        )
    SUMMARY_PATH.write_text(
        "\n".join(
            [
                "# E75 first-representative exact-SAT probes",
                "",
                "Five probes are computationally UNSAT and one reached the 100,000-conflict cap as UNKNOWN. No SAT branch was found.",
                "",
                *table,
                "",
                "Each probe uses the exact shared model with 1,176 BP equalities, 3,486 outer-pair equalities, all 105 disjoint blocks, and zero redundant support-aggregate rows. The signed assumptions exactly equal the first branch in the corresponding full normalized record.",
                "",
                "This covers only 6 of 352 local representatives and is not an E75 exclusion. No UNSAT proof certificate was emitted.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps({"status": result["status"], "status_counts": statuses, "records": len(rows)}))


if __name__ == "__main__":
    main()
