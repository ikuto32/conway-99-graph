"""Hash- and count-audit the ordered E72 lean full-Gram breadth screen."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


# The order is the two screening batches requested by the coordinator.  Rank is
# from scratch_general_e72_remaining_frontier_priority.md; source162 was an
# explicit extra request and is not a row of that frozen ranking.
REQUESTED = [
    (181, 3, 1048576, "UNKNOWN"),
    (182, 4, 1048576, "UNKNOWN"),
    (194, 6, 524288, "UNKNOWN"),
    (177, 5, 524288, "UNKNOWN"),
    (524, 7, 442368, "UNKNOWN"),
    (587, 8, 327680, "UNKNOWN"),
    (195, 9, 262144, "UNSAT"),
    (172, 10, 200704, "UNKNOWN"),
    (193, 11, 200704, "UNKNOWN"),
    (197, 12, 196608, "UNKNOWN"),
    (562, 14, 196608, "UNKNOWN"),
    (553, 13, 196608, "UNKNOWN"),
    # source332 appears below as a documented skip.
    (302, 16, 131072, "UNKNOWN"),
    (162, None, 98304, "UNSAT"),
    (611, 18, 98304, "UNKNOWN"),
    (291, 20, 65536, "UNSAT"),
    (137, 19, 65536, "UNKNOWN"),
    (335, 22, 65536, "UNSAT"),
    (331, 21, 65536, "UNKNOWN"),
    (610, 23, 57344, "UNKNOWN"),
    (196, 26, 40960, "UNKNOWN"),
    (159, 24, 40960, "UNSAT"),
    (168, 25, 40960, "UNSAT"),
]

OUTPUT = Path("scratch_root_e72_full_gram_breadth_audit.json")
REPORT = Path("scratch_root_e72_full_gram_breadth_audit.md")
PRIORITY = Path("scratch_general_e72_remaining_frontier_priority.md")
PARAMETRIC_332 = Path("scratch_theory_e72_source332_parametric_gram.json")
SOURCE133_REGULAR = Path("scratch_general_e72_source133_regular_exclusion_audit.json")
SOURCE133_SOLVER_FREE = Path("scratch_root_e72_source133_solver_free_chain_audit.json")
SOURCE133_MACRO4_FORMAL = Path("scratch_root_e72_source133_macro4_formal_audit.json")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def main() -> None:
    rows = []
    for sequence, (source, rank, expected_coverage, expected_status) in enumerate(
        REQUESTED, start=1
    ):
        stem = f"scratch_root_e72_source{source}_lean_full_gram_macro"
        build_path = Path(f"{stem}_build.json")
        cnf_path = Path(f"{stem}.cnf")
        screen_path = Path(f"{stem}_aggregate_c100000.json")
        build = json.loads(build_path.read_text(encoding="utf-8"))
        screen = json.loads(screen_path.read_text(encoding="utf-8"))

        assert build["status"] == "BUILD_COMPLETE"
        assert build["source_row_index"] == screen["source_row_index"] == source
        assert build["cnf"] == str(cnf_path)
        assert build["unused_placeholder_assumptions_applied"] is False
        assert build["redundant_BP_consequence_layer_enabled"] is False
        assert build["overlap_graphs_enumerated"] == 0
        assert screen["mode"] == "aggregate"
        assert screen["checkpoint_complete"] is True
        assert screen["conflict_budget_per_call"] == 100000
        assert screen["macro_branches"] == build["macro_branches"]
        assert len(screen["records"]) == 1
        assert screen["records"][0]["status"] == screen["status"] == expected_status
        assert screen["sat"] == 0
        assert screen["total_labelled_state_matching_coverage"] == expected_coverage
        assert build["macro_audit"]["passing_labelled_state_matching_coverage"] == expected_coverage
        assert screen["build_sha256"] == sha256(build_path)
        assert screen["cnf_sha256"] == sha256(cnf_path)
        terminal = expected_coverage if expected_status == "UNSAT" else 0
        assert screen["terminal_labelled_state_matching_coverage"] == terminal

        latest = screen
        latest_path = screen_path
        million_path = Path(f"{stem}_aggregate_c1000000.json")
        if million_path.exists():
            million = json.loads(million_path.read_text(encoding="utf-8"))
            assert million["source_row_index"] == source
            assert million["mode"] == "aggregate"
            assert million["checkpoint_complete"] is True
            assert million["conflict_budget_per_call"] == 1000000
            assert million["status"] == "UNSAT"
            assert million["direct_unsat"] == 1
            assert million["unknown"] == million["sat"] == 0
            assert million["total_labelled_state_matching_coverage"] == expected_coverage
            assert million["terminal_labelled_state_matching_coverage"] == expected_coverage
            assert million["build_sha256"] == sha256(build_path)
            assert million["cnf_sha256"] == sha256(cnf_path)
            latest = million
            latest_path = million_path

        formal_path = Path(f"scratch_root_e72_source{source}_formal_audit.json")
        formal = None
        if formal_path.exists():
            candidate = json.loads(formal_path.read_text(encoding="utf-8"))
            assert candidate["status"] == "FORMAL_AUDIT_PASS"
            assert candidate["source_row_index"] == source
            assert candidate["labelled_state_matching_coverage"] == expected_coverage
            assert candidate["cnf"]["sha256"] == sha256(cnf_path)
            formal = {
                "path": str(formal_path),
                "sha256": sha256(formal_path),
                "status": candidate["status"],
                "proof_sha256": candidate["certificate"]["proof_sha256"],
                "checker_status": candidate["certificate"]["external_checker_status"],
            }

        record = screen["records"][0]
        latest_record = latest["records"][0]
        rows.append({
            "screen_sequence": sequence,
            "source_row_index": source,
            "frozen_priority_rank": rank,
            "requested_extra_not_in_frozen_ranking": rank is None,
            "partition": build["partition"],
            "compression_orbit_index": build["compression_orbit_index"],
            "port_feasible_labelled_states": build["state_orbit_audit"]["feasible_labelled_states"],
            "state_orbits": build["state_orbit_audit"]["state_orbits"],
            "macro_branches": build["macro_branches"],
            "coverage": expected_coverage,
            "cnf_variables": build["cnf_audit"]["declared_variables"],
            "cnf_clauses": build["cnf_audit"]["declared_clauses"],
            "cnf_sha256": sha256(cnf_path),
            "c100000": {
                "path": str(screen_path),
                "sha256": sha256(screen_path),
                "status": screen["status"],
                "conflicts": record["stats_delta"]["conflicts"],
                "solve_seconds": record["solve_seconds"],
            },
            "latest_terminal_search": {
                "path": str(latest_path),
                "sha256": sha256(latest_path),
                "conflict_budget": latest["conflict_budget_per_call"],
                "status": latest["status"],
                "conflicts": latest_record["stats_delta"]["conflicts"],
                "solve_seconds": latest_record["solve_seconds"],
            },
            "formal_certificate": formal,
        })

    skip = {
        "source_row_index": 332,
        "frozen_priority_rank": 17,
        "coverage": 131072,
        "status": "SKIPPED_BY_UNIQUE_GRAM_BUILDER",
        "reason": (
            "The unique-full-Gram generic builder rejects the sole one-dimensional "
            "Gram family. Source332 requires the three separately derived integral "
            "profiles t=-1,0,1 to be selector-branched; silently choosing one would "
            "be incomplete."
        ),
        "parametric_gram": str(PARAMETRIC_332),
        "parametric_gram_sha256": sha256(PARAMETRIC_332),
        "profiles_required": 3,
    }
    assert not Path("scratch_root_e72_source332_lean_full_gram_macro.cnf").exists()

    source133_regular = json.loads(SOURCE133_REGULAR.read_text(encoding="utf-8"))
    source133_solver_free = json.loads(SOURCE133_SOLVER_FREE.read_text(encoding="utf-8"))
    source133_macro4 = json.loads(SOURCE133_MACRO4_FORMAL.read_text(encoding="utf-8"))
    assert source133_regular["status"] == "REGULAR_MACROS_LOCALLY_EXCLUDED"
    assert source133_regular["source_row_index"] == 133
    regular_coverage = source133_regular["coverage"][
        "four_regular_macros_excluded_labelled_coverage"
    ]
    assert regular_coverage == 2490368
    assert source133_regular["regular_elimination"]["local_48_vertex_CNF_UNSAT_orbits"] == 5138
    assert source133_regular["regular_elimination"]["SAT_or_UNKNOWN"] == 0
    assert source133_solver_free["status"] == "SOLVER_FREE_CHAIN_AUDIT_PASS"
    assert source133_solver_free["source_row_index"] == 133
    assert source133_solver_free["coverage_chain"]["orbits"] == [5138, 81, 1, 0]
    assert source133_solver_free["coverage_chain"]["labelled_mass"] == [1129056, 9952, 16, 0]
    assert source133_solver_free["coverage_chain"]["catalog_macro_coverage"] == regular_coverage
    assert source133_solver_free["independent_sat_crosscheck"]["result_agrees"] is True
    assert source133_macro4["status"] == "FORMAL_AUDIT_PASS"
    assert source133_macro4["source_row_index"] == 133
    assert source133_macro4["macro_branch_index"] == 4
    assert source133_macro4["catalog_labelled_coverage"] == 12288
    assert source133_macro4["certificate"]["external_checker_status"] == "DRAT_VERIFIED"
    assert regular_coverage + source133_macro4["catalog_labelled_coverage"] == 2502656
    source133_inventory = {
        "source_row_index": 133,
        "frozen_priority_rank": 1,
        "catalog_labelled_coverage": 2502656,
        "regular_macros_0_through_3": {
            "status": source133_solver_free["status"],
            "coverage": regular_coverage,
            "local_48_vertex_unsat_orbits": 5138,
            "solver_free_orbit_chain": [5138, 81, 1, 0],
            "formal_proof_status": "EXACT_EXECUTABLE_ENUM_NOT_PROOF_ASSISTANT_CERTIFIED",
            "solver_free_audit": str(SOURCE133_SOLVER_FREE),
            "solver_free_audit_sha256": sha256(SOURCE133_SOLVER_FREE),
            "prior_sat_ledger": str(SOURCE133_REGULAR),
            "prior_sat_ledger_sha256": sha256(SOURCE133_REGULAR),
        },
        "nonregular_macro_4": {
            "status": source133_macro4["status"],
            "coverage": source133_macro4["catalog_labelled_coverage"],
            "formal_proof_status": source133_macro4["certificate"][
                "external_checker_status"
            ],
            "audit": str(SOURCE133_MACRO4_FORMAL),
            "audit_sha256": sha256(SOURCE133_MACRO4_FORMAL),
            "proof_sha256": source133_macro4["certificate"]["proof_sha256"],
        },
        "coverage_partition_verified": True,
        "boundary": (
            "Macro 4 has an externally checked full exact-CNF certificate. The "
            "four regular macros are independently excluded by an exact solver-free "
            "finite-map enumeration (and agree with the SAT census), but this is "
            "not a proof-assistant kernel certificate."
        ),
    }

    total_screened = sum(row["coverage"] for row in rows)
    c100k_terminal = sum(
        row["coverage"] for row in rows if row["c100000"]["status"] == "UNSAT"
    )
    latest_terminal = sum(
        row["coverage"]
        for row in rows
        if row["latest_terminal_search"]["status"] == "UNSAT"
    )
    formal_coverage = sum(
        row["coverage"] for row in rows if row["formal_certificate"] is not None
    )
    assert all(row["c100000"]["status"] in {"UNSAT", "UNKNOWN"} for row in rows)
    assert not any(row["c100000"]["status"] == "SAT" for row in rows)

    result = {
        "status": "BREADTH_AUDIT_PASS",
        "model": "lean selector-gated exact E72 full-Gram macro aggregate",
        "priority_source": str(PRIORITY),
        "priority_source_sha256": sha256(PRIORITY),
        "screen_conflict_budget_per_source": 100000,
        "screened_source_rows": len(rows),
        "screened_coverage": total_screened,
        "c100000_terminal_unsat_rows": sum(
            row["c100000"]["status"] == "UNSAT" for row in rows
        ),
        "c100000_terminal_unsat_coverage": c100k_terminal,
        "c100000_unknown_rows": sum(
            row["c100000"]["status"] == "UNKNOWN" for row in rows
        ),
        "sat_rows": 0,
        "latest_terminal_unsat_rows": sum(
            row["latest_terminal_search"]["status"] == "UNSAT" for row in rows
        ),
        "latest_terminal_unsat_coverage": latest_terminal,
        "formally_certified_rows_at_audit_time": sum(
            row["formal_certificate"] is not None for row in rows
        ),
        "formally_certified_coverage_at_audit_time": formal_coverage,
        "source332": skip,
        "related_exclusions_outside_breadth_screen": {
            "source133": source133_inventory,
        },
        "rows": rows,
        "claim_boundary": (
            "UNKNOWN is not evidence of satisfiability. UNSAT search checkpoints "
            "are computational unless a formal_certificate is attached. Even a "
            "checked CNF certificate remains conditional on separately audited "
            "census, canonicalization, full-Gram, and encoder semantic bridges."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# E72 lean full-Gram breadth audit",
        "",
        "Status: **BREADTH_AUDIT_PASS**.",
        "",
        f"At c100k, {len(rows)} source rows covering {total_screened:,} labelled "
        f"macro completions were screened: {result['c100000_terminal_unsat_rows']} "
        f"terminal UNSAT ({c100k_terminal:,} coverage), "
        f"{result['c100000_unknown_rows']} UNKNOWN, and no SAT.",
        "",
        "| seq | rank | source | macros | coverage | c100k | conflicts | latest | formal |",
        "|---:|---:|---:|---:|---:|:---|---:|:---|:---|",
    ]
    for row in rows:
        rank = "extra" if row["frozen_priority_rank"] is None else str(row["frozen_priority_rank"])
        formal = "VERIFIED" if row["formal_certificate"] else "-"
        lines.append(
            f"| {row['screen_sequence']} | {rank} | {row['source_row_index']} | "
            f"{row['macro_branches']} | {row['coverage']:,} | "
            f"{row['c100000']['status']} | {row['c100000']['conflicts']:,} | "
            f"{row['latest_terminal_search']['status']} | {formal} |"
        )
    lines.extend([
        "",
        "Source332 was intentionally skipped: its one-dimensional Gram family has "
        "three admissible integral profiles (t=-1,0,1), which the unique-Gram "
        "builder cannot safely select.",
        "",
        "Related source133 inventory (outside this c100k screen): regular macros "
        "0--3 contribute 2,490,368 coverage and are excluded by an exact solver-free "
        "5,138 -> 81 -> 1 -> 0 finite-map chain; nonregular macro 4 contributes "
        "12,288 and has a DRAT-VERIFIED full exact-CNF certificate. These sum to "
        "the complete 2,502,656 source133 catalog coverage. The solver-free part is "
        "an executable enumeration, not a proof-assistant kernel certificate.",
        "",
        "Boundary: UNKNOWN is not a feasibility result. A terminal search result is "
        "computational until its CNF proof is externally checked, and all CNF "
        "results remain conditional on the upstream semantic bridges.",
        "",
    ])
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "rows": len(rows),
        "coverage": total_screened,
        "c100k_unsat_rows": result["c100000_terminal_unsat_rows"],
        "latest_unsat_rows": result["latest_terminal_unsat_rows"],
        "formal_rows": result["formally_certified_rows_at_audit_time"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
