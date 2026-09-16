"""Coverage and result audit for the independent E0=76 fixed CNF portfolio."""

from __future__ import annotations

from collections import Counter, defaultdict
import json
from pathlib import Path


SOURCE = Path("scratch_e76_independent_local.json")
LOCAL_AUDIT = Path("scratch_e76_independent_local_audit.json")
CATALOG = Path("scratch_e76_fixed_exact_catalog.json")
CHECKPOINT = Path("scratch_e76_fixed_exact_checkpoint.json")
PORTFOLIO = Path("scratch_e76_fixed_exact_portfolio.json")
OUTPUT = Path("scratch_e76_fixed_exact_audit.json")


def main():
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    local_audit = json.loads(LOCAL_AUDIT.read_text(encoding="utf-8"))
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    checkpoint = json.loads(CHECKPOINT.read_text(encoding="utf-8"))
    portfolio = json.loads(PORTFOLIO.read_text(encoding="utf-8"))
    assert source["ok"] and local_audit["ok"]
    assert catalog["branch_count"] == checkpoint["catalog_size"] == 311
    assert catalog["covered_labelled_local_graphs"] == 68864

    expected = []
    for row_index, row in enumerate(source["rows"]):
        for representative in row["representatives"]:
            expected.append({
                "source_row_index": row_index,
                "partition": row["partition"],
                "compression_orbit_index": row["compression_orbit_index"],
                "support_orbit_size": row["support_orbit_size"],
                "exceptional_supports": row["exceptional_supports"],
                "local_representative_index": representative["representative_index"],
                "local_orbit_size": representative["local_orbit_size"],
                "local_edge_count": representative["local_edge_count"],
            })
    assert len(expected) == 311
    assert sum(row["local_orbit_size"] for row in expected) == 68864
    for index, (wanted, actual) in enumerate(zip(expected, catalog["branches"])):
        assert actual["branch_index"] == index
        assert all(actual[key] == value for key, value in wanted.items())

    assert set(checkpoint["attempts"]) == {str(index) for index in range(311)}
    first_status = Counter()
    second_status = Counter()
    latest_status = Counter()
    termination = Counter()
    attempt_histogram = Counter()
    total_solve_seconds = total_build_seconds = 0.0
    total_conflicts = 0
    branch_groups = defaultdict(lambda: {
        "branches": 0,
        "labelled_local_graphs": 0,
        "first_UNSAT": 0,
        "first_UNKNOWN": 0,
        "final_UNSAT": 0,
    })
    for index in range(311):
        attempts = checkpoint["attempts"][str(index)]
        attempt_histogram[len(attempts)] += 1
        assert len(attempts) in (1, 2)
        assert attempts[0]["conflict_budget"] == 20000
        first_status[attempts[0]["status"]] += 1
        termination[(attempts[0]["status"], attempts[0]["termination"])] += 1
        if len(attempts) == 2:
            assert attempts[0]["status"] == "UNKNOWN"
            assert attempts[0]["termination"] == "conflict_budget"
            assert attempts[1]["conflict_budget"] == 200000
            second_status[attempts[1]["status"]] += 1
        latest = attempts[-1]
        latest_status[latest["status"]] += 1
        assert latest["status"] == "UNSAT"
        assert latest["termination"] == "solver_answer"
        assert latest["formal_proof_certificate"] is None
        meta = latest["meta"]
        assert meta["branch_index"] == index
        assert meta["edge_variables"] == 1680
        assert meta["product_variables"] == 65520
        assert meta["disjoint_blocks"] == 105
        assert meta["BP_equalities"] == 1176
        assert meta["outer_pair_equalities"] == 3486
        assert meta["cardinality_equalities"] == 4662
        assert meta["fixed_local_overlap_edges"] == 16
        assert meta["block_types"]["high_high"] + meta["block_types"]["high_low"] + meta["block_types"]["low_low"] == 105
        assert meta["ordinary_c4_block_equalities"] == (
            8 * meta["block_types"]["high_high"]
            + 4 * meta["block_types"]["high_low"]
        )
        assert meta["redundant_support_aggregate_rows"] == 0
        catalog_row = catalog["branches"][index]
        assert (
            meta["partition"],
            meta["compression_orbit_index"],
            meta["local_representative_index"],
            meta["local_orbit_size"],
        ) == (
            catalog_row["partition"],
            catalog_row["compression_orbit_index"],
            catalog_row["local_representative_index"],
            catalog_row["local_orbit_size"],
        )
        group_key = (
            "+".join(map(str, catalog_row["partition"])),
            catalog_row["compression_orbit_index"],
        )
        grouped = branch_groups[group_key]
        grouped["branches"] += 1
        grouped["labelled_local_graphs"] += catalog_row["local_orbit_size"]
        grouped["first_UNSAT"] += attempts[0]["status"] == "UNSAT"
        grouped["first_UNKNOWN"] += attempts[0]["status"] == "UNKNOWN"
        grouped["final_UNSAT"] += latest["status"] == "UNSAT"
        for attempt in attempts:
            total_solve_seconds += attempt.get("solve_seconds", 0.0)
            total_build_seconds += attempt.get("build_seconds", 0.0)
            total_conflicts += attempt.get("stats", {}).get("conflicts", 0)

    assert first_status == Counter({"UNSAT": 188, "UNKNOWN": 123})
    assert second_status == Counter({"UNSAT": 123})
    assert latest_status == Counter({"UNSAT": 311})
    assert attempt_histogram == Counter({1: 188, 2: 123})
    assert termination == Counter({
        ("UNSAT", "solver_answer"): 188,
        ("UNKNOWN", "conflict_budget"): 123,
    })
    assert portfolio["all_311_terminal"]
    assert portfolio["cumulative_latest_status_counts"] == {"UNSAT": 311}
    assert not list(Path(".").glob("scratch_e76_fixed_exact_solution_branch*.json"))

    result = {
        "model": "independent coverage/result audit of E0=76 fixed-local exact SAT",
        "catalog": {
            "branches": 311,
            "support_branches": len(branch_groups),
            "covered_labelled_local_graphs": 68864,
            "all_explicit_representatives_mapped_once": True,
        },
        "model_invariants_on_every_latest_branch": {
            "disjoint_edge_variables": 1680,
            "AND_products": 65520,
            "BP_equalities": 1176,
            "outer_pair_equalities": 3486,
            "fixed_local_overlap_edges": 16,
            "ordinary_C4_block_rule_checked": True,
            "redundant_support_aggregate_rows": 0,
        },
        "attempts": {
            "total": sum(length * count for length, count in attempt_histogram.items()),
            "one_attempt_branches": attempt_histogram[1],
            "two_attempt_branches": attempt_histogram[2],
            "first_pass": dict(first_status),
            "second_pass": dict(second_status),
            "latest": dict(latest_status),
            "termination": {
                f"{status}:{reason}": count
                for (status, reason), count in sorted(termination.items())
            },
            "sum_build_seconds": round(total_build_seconds, 3),
            "sum_solve_seconds": round(total_solve_seconds, 3),
            "sum_conflicts": total_conflicts,
        },
        "by_support_branch": [
            {
                "partition": key[0],
                "compression_orbit_index": key[1],
                **values,
            }
            for key, values in sorted(branch_groups.items())
        ],
        "SAT_count": 0,
        "UNKNOWN_count": 0,
        "UNSAT_count": 311,
        "formal_UNSAT_certificates": 0,
        "claim_boundary": (
            "all 311 exhaustive fixed-local branches are computationally UNSAT; "
            "no independently checked proof certificates were produced"
        ),
        "ok": True,
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": True,
        "catalog": result["catalog"],
        "first": result["attempts"]["first_pass"],
        "second": result["attempts"]["second_pass"],
        "latest": result["attempts"]["latest"],
    }))


if __name__ == "__main__":
    main()
