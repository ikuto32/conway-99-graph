"""Intersect stored exact-label domains with attainable fibre moment hulls.

The expensive local subset calculations are frozen inputs and never rerun.
No adjacency completion is generated. Caps are inherited from the raw hull.
"""

import json
from pathlib import Path

import scratch_theory_e71_fibre_moment_hull_probe as hull


SUBSETS = Path("scratch_theory_e71_label_subset_moment_frontier.json")
RAW_HULL = Path("scratch_theory_e71_fibre_moment_hull_remaining.json")
OUTPUT = Path("scratch_theory_e71_fibre_moment_hull_label_subset_probe.json")


def main():
    subset, raw, catalog, mining = map(hull.exact.read, (SUBSETS, RAW_HULL, hull.exact.CATALOG, hull.exact.MINING))
    assert subset["status"] == "E71_EXACT_LABEL_SUBSET_MOMENT_PROBE_COMPLETE"
    assert subset["all_remaining_requested"]
    by_profile = {(tuple(r["key"]), r["parameter"]): r for r in subset["profiles"]}
    entries = {hull.exact.macro_key(r): r for r in catalog["macro_entries"] if r["signature_stabilizer_canonical"]}
    profiles = {(hull.exact.macro_key(r), r["parameter"]): r for r in mining["profile_rows"]["71"]}
    records = []
    for original in raw["rows"]:
        key = (tuple(original["key"]), original["parameter"])
        local = by_profile[key]
        expected_supports = [list(hull.exact.SUPPORTS[i]) for i in original["pivot_indices"]]
        assert local["model"]["pivot_supports"] == expected_supports
        result = hull.analyze(entries[key[0]], profiles[key], local["model"]["domains_by_position"])
        result["label_subset_LP_already_certified_infeasible"] = local["exact_integer_certificate"] is not None
        result["additional_to_label_subset_LP"] = (
            (result.get("exact_Farkas_certificate") is not None or result["status"] == "EMPTY_FIBRE_EXACT_CANDIDATE")
            and local["exact_integer_certificate"] is None)
        records.append(result)
        print(json.dumps({"key": result["key"], "parameter": result["parameter"],
                          "status": result["status"], "LP_status": result.get("LP_status"),
                          "exact_Farkas": result.get("exact_Farkas_certificate") is not None,
                          "additional": result["additional_to_label_subset_LP"],
                          "columns": result.get("variable_count")}), flush=True)
    assert len(records) == 71
    result = {"status": "BOUNDED_LABEL_SUBSET_FIBRE_MOMENT_HULL_INTERSECTION_COMPLETE",
              "inputs_sha256": {str(p): hull.exact.sha(p) for p in (SUBSETS, RAW_HULL, hull.exact.CATALOG, hull.exact.MINING, Path(hull.__file__))},
              "scope": "Same 71 raw-LP-passing profiles in 65 residual macros; stored per-position label-subset domains plus attainable zero-sum four-row fibre moments. No subset or adjacency completion re-enumeration.",
              "rows": records,
              "summary": {"profiles": len(records),
                          "complete_profiles": sum(r["status"] == "COMPLETE_FIBRE_MOMENT_HULL_MODEL" for r in records),
                          "empty_fibre_profiles": sum(r["status"] == "EMPTY_FIBRE_EXACT_CANDIDATE" for r in records),
                          "capped_profiles": sum(r["status"] == "CAPPED_NO_EXCLUSION" for r in records),
                          "exact_Farkas_profiles": sum(r.get("exact_Farkas_certificate") is not None for r in records),
                          "additional_to_label_subset_LP_profiles": sum(r["additional_to_label_subset_LP"] for r in records),
                          "exact_feasible_profiles": sum(r.get("exact_feasible_weights") is not None for r in records)},
              "requires_independent_audit_before_credit": True, "submission_txt_written": False}
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
