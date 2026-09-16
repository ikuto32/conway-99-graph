"""Bridge all source-133 macro coverage to its two exclusion proofs."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


REGULAR_LEDGER = Path(
    "scratch_general_e72_source133_regular_exclusion_audit.json"
)
REGULAR_SAT = Path(
    "scratch_general_e72_source133_pair_category_exclusion_audit.json"
)
REGULAR_ENUM = Path("scratch_theory_e72_k23_final_uu_enum.json")
MACRO4 = Path("scratch_root_e72_source133_macro4_formal_audit.json")
ASSUMPTIONS = Path(
    "scratch_root_e72_source133_local_assumption_manifest.json"
)
OUTPUT = Path("scratch_root_e72_source133_complete_exclusion_audit.json")


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest().upper()


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main():
    ledger = load(REGULAR_LEDGER)
    sat = load(REGULAR_SAT)
    enum = load(REGULAR_ENUM)
    macro4 = load(MACRO4)
    assumptions = load(ASSUMPTIONS)

    assert ledger["source_row_index"] == 133
    coverage = ledger["coverage"]
    assert coverage["all_five_macros_catalog_labelled_coverage"] == 2_502_656
    assert coverage["four_regular_macros_excluded_labelled_coverage"] == 2_490_368
    assert coverage["remaining_nonregular_macro4_catalog_labelled_coverage"] == 12_288
    assert 2_490_368 + 12_288 == 2_502_656

    assert sat["status"] == "EXACT_COMPUTATIONAL_FINITE_CATEGORY_EXCLUSION"
    assert sat["summary"]["input_orbits"] == 5_138
    assert sat["summary"]["input_mass"] == 1_129_056
    assert sat["summary"]["UNSAT_orbits"] == 5_138
    assert sat["summary"]["UNSAT_mass"] == 1_129_056
    assert sat["summary"]["SAT_orbits"] == 0

    assert enum["status"] == "EXACT_SOLVER_FREE_REGULAR_EXCLUSION_COMPLETE"
    assert enum["coverage"] == {
        "stage_one_regular_masks": 5_138,
        "stage_one_survivors": 81,
        "stage_two_survivors": 1,
        "stage_three_survivors": 0,
    }
    ee_cross = load(Path("scratch_theory_e72_k23_ee_cross_enum.json"))
    assert ee_cross["input_orbits"] == 81
    assert ee_cross["input_mass"] == 9_952
    assert ee_cross["passing_orbits"] == 1
    assert ee_cross["passing_mass"] == 16
    assert enum["input_stage_two_survivor"][1] == 16
    assert enum["EE_compatible_profile_triples_after_within_UU"] == 0
    assert enum["fully_UU_overlap_compatible_explicit_map_triples"] == 0

    assert macro4["status"] == "FORMAL_AUDIT_PASS"
    assert macro4["source_row_index"] == 133
    assert macro4["macro_branch_index"] == 4
    assert macro4["catalog_labelled_coverage"] == 12_288
    assert macro4["certificate"]["external_checker_status"] == "DRAT_VERIFIED"
    assert macro4["branch_isolation"]["selected_selector_forced"] == 817_283
    assert macro4["branch_isolation"]["source_payload_byte_identical"]

    summary = assumptions["summary"]
    assert assumptions["status"] == "FULL_SRG_ASSUMPTION_MANIFEST_COMPLETE"
    assert summary["records"] == 5_286
    assert summary["orbit_mass"] == 1_167_072
    assert summary["regular_local_UNSAT_records"] == 5_138
    assert summary["regular_local_UNSAT_mass"] == 1_129_056
    assert summary["macro4_formally_excluded_records"] == 148
    assert summary["macro4_formally_excluded_mass"] == 38_016
    assert 5_138 + 148 == 5_286
    assert 1_129_056 + 38_016 == 1_167_072
    assert len(assumptions["records"]) == 5_286
    assert all(len(row[5]) == 276 for row in assumptions["records"])

    macro_ledger = ledger["macro_ledger"]
    assert [row["state_macro_number"] for row in macro_ledger] == list(range(5))
    assert sum(row["catalog_labelled_coverage"] for row in macro_ledger) == 2_502_656
    assert sum(
        row["catalog_labelled_coverage"] for row in macro_ledger[:4]
    ) == 2_490_368
    assert macro_ledger[4]["catalog_labelled_coverage"] == 12_288
    for row in macro_ledger[:4]:
        macro = str(row["state_macro_number"])
        sat_row = sat["per_macro"][macro]
        assert row["after_exception_recurrence_and_pair_exact_orbits"] == sat_row["input_orbits"]
        assert row["after_exception_recurrence_and_pair_exact_mass"] == sat_row["input_mass"]
        assert sat_row["UNSAT_orbits"] == sat_row["input_orbits"]
        assert sat_row["UNSAT_mass"] == sat_row["input_mass"]

    dependencies = (
        REGULAR_LEDGER, REGULAR_SAT, REGULAR_ENUM,
        Path("scratch_theory_e72_k23_ee_cross_enum.json"),
        Path("scratch_theory_e72_k23_opposite_collision_enum.py"),
        Path("scratch_theory_e72_k23_ee_cross_enum.py"),
        Path("scratch_theory_e72_k23_final_uu_enum.py"),
        MACRO4, ASSUMPTIONS,
    )
    output = {
        "status": "SOURCE133_COMPLETE_EXCLUSION_AUDIT_PASS",
        "source_row_index": 133,
        "partition_index": 27,
        "input_sha256": {str(path): sha256(path) for path in dependencies},
        "catalog_coverage_partition": {
            "regular_macros_0_to_3": 2_490_368,
            "nonregular_macro_4": 12_288,
            "total": 2_502_656,
            "disjoint_and_complete": True,
        },
        "canonical_local_frontier": {
            "regular_records": 5_138,
            "regular_orbit_mass": 1_129_056,
            "macro4_records": 148,
            "macro4_orbit_mass": 38_016,
            "total_records": 5_286,
            "total_orbit_mass": 1_167_072,
            "full_SRG_edge_assumptions_per_record": 276,
            "assumption_manifest": str(ASSUMPTIONS),
        },
        "regular_exclusion": {
            "scope": "macros 0,1,2,3",
            "solver_free_stages_orbits": [5_138, 81, 1, 0],
            "solver_free_stages_mass": [1_129_056, 9_952, 16, 0],
            "independent_SAT_replay_UNSAT_orbits": 5_138,
            "independent_SAT_replay_UNSAT_mass": 1_129_056,
            "fixed_pair_category_policy": sat["policy_by_macro"],
            "ordered_SAT_instance_manifest_sha256": sat[
                "ordered_instance_manifest_sha256"
            ],
        },
        "macro4_exclusion": {
            "scope": "nonregular macro 4",
            "selected_full_SRG_selector": 817_283,
            "catalog_labelled_coverage": 12_288,
            "completed_local_records": 148,
            "completed_local_orbit_mass": 38_016,
            "cnf_sha256": macro4["cnf"]["sha256"],
            "drup_sha256": macro4["certificate"]["proof_sha256"],
            "external_checker_status": "DRAT_VERIFIED",
        },
        "checks": {
            "catalog_macro_partition_exact": True,
            "canonical_local_frontier_partition_exact": True,
            "regular_solver_free_zero_survivors": True,
            "regular_independent_SAT_zero_survivors": True,
            "regular_two_methods_agree": True,
            "macro4_selector_isolation_exact": True,
            "macro4_external_DRAT_check_passed": True,
            "every_local_record_has_full_SRG_edge_assumptions": True,
        },
        "logical_conclusion": (
            "Every one of the five canonical source-133 macro branches is "
            "excluded: regular macros 0--3 by exact solver-free local map "
            "enumeration (independently confirmed by finite SAT), and "
            "nonregular macro 4 by a checked full-SRG DRUP certificate."
        ),
        "claim_boundary": (
            "The regular proof is an exact standard-library finite enumeration, "
            "not a DRAT certificate.  The macro-4 DRUP is formally checked.  "
            "Upstream support/Gram/catalog completeness remains covered by its "
            "separate audited artifacts."
        ),
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": output["status"],
        "catalog_coverage": output["catalog_coverage_partition"],
        "regular_solver_free": output["regular_exclusion"]["solver_free_stages_orbits"],
        "macro4": output["macro4_exclusion"]["external_checker_status"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
