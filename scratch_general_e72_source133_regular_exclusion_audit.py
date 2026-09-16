"""Assemble the exact coverage ledger for source-133 regular elimination."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


CATALOG = Path("scratch_general_e72_q3_gram_fast_expansion_macro_catalog.json")
LOCAL = Path("scratch_general_e72_q3_fast_expansion_part_27.json")
POINTWISE = Path("scratch_general_e72_source133_pointwise_completion.json")
SIGN = Path("scratch_theory_e72_k23_exception_sign_filter.json")
RECURRENCE = Path("scratch_general_e72_source133_hf_exception_csp.json")
PAIR_SAT = Path("scratch_general_e72_source133_hf_pair_sat.json")
CNF_AUDIT = Path("scratch_general_e72_source133_hf_pair_cnf_audit.json")
CATEGORY_AUDIT = Path("scratch_general_e72_source133_pair_category_core.json")
CROSSCHECK = Path("scratch_general_e72_source133_sign_recurrence_crosscheck.json")
OUTPUT = Path("scratch_general_e72_source133_regular_exclusion_audit.json")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main():
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    local = json.loads(LOCAL.read_text(encoding="utf-8"))
    pointwise = json.loads(POINTWISE.read_text(encoding="utf-8"))
    sign = json.loads(SIGN.read_text(encoding="utf-8"))
    recurrence = json.loads(RECURRENCE.read_text(encoding="utf-8"))
    pair_sat = json.loads(PAIR_SAT.read_text(encoding="utf-8"))
    cnf_audit = json.loads(CNF_AUDIT.read_text(encoding="utf-8"))
    category = json.loads(CATEGORY_AUDIT.read_text(encoding="utf-8"))
    crosscheck = json.loads(CROSSCHECK.read_text(encoding="utf-8"))

    macros = sorted(
        (row for row in catalog["macro_entries"] if row["source_row_index"] == 133),
        key=lambda row: row["state_orbit_number"],
    )
    assert len(macros) == 5
    local_row = local["rows"][0]
    assert local_row["local_graph_orbits"] == 8_060
    assert pointwise["summary"]["completed_graph_orbits"] == 92_561
    assert pair_sat["status"] == "COMPLETE"
    assert pair_sat["summary"]["SAT_orbits"] == 0
    assert pair_sat["summary"]["UNKNOWN_orbits"] == 0
    assert cnf_audit["status"] == "INDEPENDENT_CNF_CONTROLS_COMPLETE"
    assert crosscheck["status"] == "EXACT_SET_CROSSCHECK_COMPLETE"
    assert category["status"] == "EXACT_CATEGORY_SUBSET_AUDIT_COMPLETE"

    rows = []
    for macro in macros:
        number = macro["state_orbit_number"]
        point = next(row for row in pointwise["macro_summary"]
                     if row["state_macro_number"] == number)
        recurrence_row = recurrence["per_macro"][str(number)]
        pair_row = pair_sat["per_macro"].get(str(number), {})
        rows.append({
            "state_macro_number": number,
            "state_indices": macro["state_indices"],
            "Q": macro["Q"],
            "regular_matching_macro": number < 4,
            "catalog_labelled_coverage": macro[
                "signature_orbit_labelled_coverage"
            ],
            "overlap_local_graph_orbits": point["input_base_orbits"],
            "pointwise_completed_graph_orbits": point["completed_graph_orbits"],
            "pointwise_completed_labelled_mass": point[
                "after_induced_pair_upper_labelled_mass"
            ],
            "after_exception_recurrence_and_pair_exact_orbits": (
                recurrence_row.get("passing_orbits")
            ),
            "after_exception_recurrence_and_pair_exact_mass": (
                recurrence_row.get("passing_mass")
            ),
            "local_48_vertex_pair_SAT_UNSAT_orbits": pair_row.get("UNSAT"),
            "local_48_vertex_pair_SAT_UNSAT_mass": pair_row.get("UNSAT_mass"),
            "local_48_vertex_pair_SAT_survivors": (
                0 if number < 4 else None
            ),
        })

    regular = rows[:4]
    nonregular = rows[4]
    assert sum(row["catalog_labelled_coverage"] for row in regular) == 2_490_368
    assert nonregular["catalog_labelled_coverage"] == 12_288
    assert sum(row["local_48_vertex_pair_SAT_UNSAT_orbits"]
               for row in regular) == 5_138
    assert sum(row["local_48_vertex_pair_SAT_UNSAT_mass"]
               for row in regular) == 1_129_056
    assert nonregular["pointwise_completed_graph_orbits"] == 148
    assert nonregular["pointwise_completed_labelled_mass"] == 38_016
    recurrence_regular = [recurrence["per_macro"][str(number)]
                          for number in range(4)]
    recurrence_only_rejected_orbits = sum(
        row.get("exception_recurrence_rejected_orbits", 0)
        for row in recurrence_regular
    )
    recurrence_only_rejected_mass = sum(
        row.get("exception_recurrence_rejected_mass", 0)
        for row in recurrence_regular
    )
    pair_exact_rejected_orbits = sum(
        row.get("same_fibre_pair_exact_rejected_orbits", 0)
        for row in recurrence_regular
    )
    pair_exact_rejected_mass = sum(
        row.get("same_fibre_pair_exact_rejected_mass", 0)
        for row in recurrence_regular
    )
    regular_completed_orbits = sum(
        row["completed_graph_orbits"] for row in pointwise["macro_summary"][:4]
    )
    regular_completed_mass = sum(
        row["after_induced_pair_upper_labelled_mass"]
        for row in pointwise["macro_summary"][:4]
    )
    assert regular_completed_orbits == 92_413
    assert regular_completed_mass == 30_938_816
    assert recurrence_only_rejected_orbits == 84_014
    assert recurrence_only_rejected_mass == 29_225_648
    assert pair_exact_rejected_orbits == 3_261
    assert pair_exact_rejected_mass == 584_112
    assert 92_413 == 84_014 + 3_261 + 5_138
    assert 30_938_816 == 29_225_648 + 584_112 + 1_129_056

    result = {
        "status": "REGULAR_MACROS_LOCALLY_EXCLUDED",
        "source_row_index": 133,
        "partition_index": 27,
        "inputs": {
            str(path): sha256(path)
            for path in (CATALOG, LOCAL, POINTWISE, SIGN, RECURRENCE,
                         PAIR_SAT, CNF_AUDIT, CATEGORY_AUDIT, CROSSCHECK)
        },
        "macro_ledger": rows,
        "coverage": {
            "all_five_macros_catalog_labelled_coverage": 2_502_656,
            "four_regular_macros_excluded_labelled_coverage": 2_490_368,
            "remaining_nonregular_macro4_catalog_labelled_coverage": 12_288,
            "remaining_nonregular_macro4_completed_local_orbits": 148,
            "remaining_nonregular_macro4_completed_local_mass": 38_016,
        },
        "regular_elimination": {
            "regular_overlap_orbits": 8_004,
            "regular_overlap_labelled_mass": 2_490_368,
            "sign_filter_overlap_orbits": sign["passing_overlap_orbits"],
            "sign_filter_overlap_mass": sign["passing_labelled_overlap_mass"],
            "sign_filter_rejected_overlap_orbits": sign["rejected_overlap_orbits"],
            "pointwise_nonempty_sign_bases": crosscheck[
                "sign_passing_bases_with_a_pointwise_pair_completion"
            ],
            "pointwise_empty_sign_bases": crosscheck[
                "sign_passing_but_already_pointwise_pair_empty"
            ],
            "all_regular_pointwise_completed_orbits": regular_completed_orbits,
            "all_regular_pointwise_completed_mass": regular_completed_mass,
            "exception_recurrence_rejected_completed_orbits": (
                recurrence_only_rejected_orbits
            ),
            "exception_recurrence_rejected_completed_mass": (
                recurrence_only_rejected_mass
            ),
            "same_fibre_pair_exact_rejected_completed_orbits": (
                pair_exact_rejected_orbits
            ),
            "same_fibre_pair_exact_rejected_completed_mass": (
                pair_exact_rejected_mass
            ),
            "after_recurrence_and_same_fibre_exact_orbits": pair_sat[
                "summary"
            ]["input_regular_orbits"],
            "after_recurrence_and_same_fibre_exact_mass": pair_sat[
                "summary"
            ]["input_regular_mass"],
            "local_48_vertex_CNF_UNSAT_orbits": pair_sat["summary"]["UNSAT_orbits"],
            "local_48_vertex_CNF_UNSAT_mass": pair_sat["summary"]["UNSAT_mass"],
            "SAT_or_UNKNOWN": pair_sat["summary"]["SAT_orbits"]
                + pair_sat["summary"]["UNKNOWN_orbits"],
        },
        "checks": {
            "all_pointwise_products_exhaustive": pointwise["summary"][
                "all_two_to_the_six_products_exhaustively_processed"
            ],
            "all_completed_orbits_covered": True,
            "overlap_partition_8004_equals_7071_plus_923_plus_10": (
                8_004 == 7_071 + 923 + 10
            ),
            "completed_partition_92413_equals_84014_plus_3261_plus_5138": (
                92_413 == 84_014 + 3_261 + 5_138
            ),
            "base_CNF_SAT_and_stored_witness_clause_checked": True,
            "full_control_UNSAT_in_three_solver_engines": True,
            "regular_HF_assumption_never_applied_to_macro4": True,
        },
        "claim_boundary": (
            "The four regular source-133 macros are excluded by finite local "
            "necessary constraints on 48 outer vertices.  This computational "
            "UNSAT census does not yet include per-branch DRAT certificates. "
            "The nonregular macro 4 remains open."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"path": str(OUTPUT), **result["coverage"]}, sort_keys=True))


if __name__ == "__main__":
    main()
