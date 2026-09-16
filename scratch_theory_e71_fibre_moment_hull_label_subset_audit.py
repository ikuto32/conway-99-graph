"""Positive combined controls only; no hull producer, subset enumerator or LP.

The inherited raw witness checker independently reconstructs all 21 coordinates.
Here every used ordered quartet row is additionally checked against its frozen
actual-position label domain. We do not re-audit the eight inherited cuts.
"""

from pathlib import Path
import json

import scratch_theory_e71_fibre_moment_hull_audit as raw

matrices = raw.matrices
COMBINED = Path("scratch_theory_e71_fibre_moment_hull_label_subset_probe.json")
SUBSETS = Path("scratch_theory_e71_label_subset_moment_frontier.json")
OUTPUT = Path("scratch_theory_e71_fibre_moment_hull_label_subset_audit.json")


def main():
    combined, subsets, catalog, mining = map(matrices.read, (COMBINED, SUBSETS, matrices.CATALOG, matrices.MINING))
    for document in (combined, subsets):
        for path, wanted in document["inputs_sha256"].items():
            assert matrices.sha(Path(path)) == wanted, path
    assert combined["status"] == "BOUNDED_LABEL_SUBSET_FIBRE_MOMENT_HULL_INTERSECTION_COMPLETE"
    assert len(combined["rows"]) == 71
    subset_profiles = {(tuple(r["key"]), r["parameter"]): r for r in subsets["profiles"]}
    entries = {matrices.macro_key(r): r for r in catalog["macro_entries"] if r["signature_stabilizer_canonical"]}
    profiles = {(matrices.macro_key(r), r["parameter"]): r for r in mining["profile_rows"]["71"]}
    matrices.ordinary_internal_theorem()
    matrices.fibre_incidence_geometry()
    seen, verified, inherited = set(), [], []
    for record in combined["rows"]:
        key = (tuple(record["key"]), record["parameter"])
        assert key not in seen
        seen.add(key)
        local = subset_profiles[key]
        assert not record["additional_to_label_subset_LP"]
        if local["exact_integer_certificate"] is not None:
            assert record["label_subset_LP_already_certified_infeasible"]
            inherited.append({"key": record["key"], "parameter": record["parameter"]})
            continue
        assert not record["label_subset_LP_already_certified_infeasible"]
        assert local["model"]["pivot_supports"] == [list(matrices.SUPPORTS[i]) for i in record["pivot_indices"]]
        domains = [set(map(tuple, domain)) for domain in local["model"]["domains_by_position"]]
        assert len(domains) == 84
        checked_memberships = 0
        for index, weight in record["exact_feasible_weights"]["nonzero_weights"]:
            source, option = record["variables"][index]
            quartet = record["fibre_options"][source][option]["row_pivots"]
            for corner, row in enumerate(quartet):
                assert tuple(row) in domains[4 * source + corner], (key, source, corner, row)
                checked_memberships += 1
        proof = raw.check(entries[key[0]], profiles[key], record)
        assert checked_memberships == proof["quartet_rows_checked_in_all_21_coordinates"]
        proof["recorded_actual_corner_label_domain_memberships"] = checked_memberships
        verified.append(proof)
    assert len(verified) == 63 and len(inherited) == 8
    assert {key[0] for key in seen} == set(map(tuple, matrices.read(raw.INVENTORY)["remaining_keys"]))
    result = {
        "status": "INDEPENDENT_E71_LABEL_SUBSET_FIBRE_HULL_POSITIVE_CONTROLS_AUDIT_PASS",
        "hull_producer_imported": False, "LP_solver_used": False,
        "subset_enumerator_run": False,
        "inputs_sha256": {str(p): matrices.sha(p) for p in (COMBINED, SUBSETS, raw.INVENTORY, matrices.CATALOG, matrices.MINING, Path(raw.__file__), Path(matrices.__file__))},
        "verified_exact_positive_profiles": len(verified),
        "inherited_cut_profiles_not_reaudited": inherited,
        "additional_exclusions_credited": 0,
        "rows": verified,
        "scope": "Every positively weighted ordered quartet is valid in all 21 raw residual coordinates, has zero fibre sum, exact actual-corner internal degrees, and lies in recorded exact-label position domains. Rational weights give unit mass per fibre and full target Gram. Label-subset domain necessity is an external separately audited input; no 23-vertex enumeration or inherited Farkas replay occurs here. Feasible relaxation controls are not adjacency graphs.",
        "submission_txt_written": False,
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "verified_exact_positive_profiles": 63, "inherited_cut_profiles_not_reaudited": 8, "additional_exclusions_credited": 0}, sort_keys=True))


if __name__ == "__main__":
    main()
