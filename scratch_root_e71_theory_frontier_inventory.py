"""Disjoint ledger of independently audited cuts in the frozen 132 frontier.

An inventory replay is not a replacement for the linked mathematical audits.
No E71 local graph, matching, or completion is generated here.
"""

import hashlib
import json
from pathlib import Path


def read(name):
    return json.loads(Path(name).read_text(encoding="utf-8"))


def digest(name):
    return hashlib.sha256(Path(name).read_bytes()).hexdigest().upper()


def main():
    baseline_name = "scratch_theory_e71_equitable_kernel_port_census.json"
    baseline = read(baseline_name)
    retained = {tuple(r["key"]): r for r in baseline["rows"]
                if r["macro_passes_some_full_Gram_profile_kernel_port_CSP"]}
    assert len(retained) == 132
    mass = sum(r["coverage"] for r in retained.values())
    assert mass == 49086464
    cut724_name = "scratch_theory_e71_source724_multiblock_transport_audit.json"
    cut694_name = "scratch_theory_e71_fibre_quartet_audit.json"
    cutlp_name = "scratch_theory_e71_degree_moment_lp_audit.json"
    cutsubset_name = "scratch_theory_e71_label_subset_moment_audit.json"
    cut724, cut694 = read(cut724_name), read(cut694_name)
    cutlp = read(cutlp_name)
    cutsubset = read(cutsubset_name)
    assert cut724["status"] == "INDEPENDENT_SOURCE724_MULTIBLOCK_TRANSPORT_AUDIT_PASS"
    assert cut694["status"] == "INDEPENDENT_E71_FIBRE_QUARTET_SOURCE694_SCALAR_AUDIT_PASS"
    assert cutlp["status"] == "INDEPENDENT_E71_DEGREE_MOMENT_LP_AUDIT_PASS"
    assert cutsubset["status"] == "INDEPENDENT_E71_LABEL_SUBSET_MOMENT_AUDIT_PASS"
    assert not cut724["producer_imported"] and not cut694["producer_imported"]
    assert not cutlp["producer_or_base_imported"] and not cutlp["LP_solver_used"]
    assert not cutsubset["research_producer_imported"] and not cutsubset["LP_solver_used"]
    assert cutsubset["every_full_Gram_profile_directly_certified_for_each_excluded_macro"]
    for certificate in (cut724, cut694, cutlp, cutsubset):
        for path, expected in certificate["inputs_sha256"].items():
            assert digest(path) == expected.upper(), path
    assert cut724["residual_minus4_projector_row_norm"]["passed"] == 0
    assert "(724,1,0)" in cut724["coverage_conclusion"]
    assert "32768" in cut724["coverage_conclusion"]
    cuts = [{"key": [724, 1, 0], "coverage": 32768,
             "audit": cut724_name, "method": "pointwise transport and residual projector row norm"}]
    lp_keys = {tuple(record["key"]) for record in cutlp["excluded_macro_rows"]}
    for record in cut694["rows"]:
        assert record["contradiction"]
        assert record["forced_scalar_total"] == 4
        assert record["Gram_required_scalar_total"] == 52
        assert tuple(record["key"]) in lp_keys
    for record in cutlp["excluded_macro_rows"]:
        cuts.append({"key": record["key"], "coverage": record["coverage"],
                     "audit": cutlp_name, "method": "exact integer quadratic degree-moment Farkas certificate"})
    for record in cutsubset["macro_rows"]:
        cuts.append({"key": record["key"], "coverage": record["coverage"],
                     "audit": cutsubset_name, "method": "23-vertex single-row subset support and exact degree-moment Farkas certificate"})
    keys = {tuple(row["key"]) for row in cuts}
    assert len(keys) == len(cuts) == 73
    for row in cuts:
        assert row["coverage"] == retained[tuple(row["key"])]["coverage"]
    excluded_mass = sum(row["coverage"] for row in cuts)
    remaining = sorted(set(retained) - keys)
    remaining_mass = sum(retained[key]["coverage"] for key in remaining)
    assert excluded_mass == 23068672 and remaining_mass == 26017792
    assert mass == excluded_mass + remaining_mass and len(remaining) == 59
    result = {
        "status": "E71_SCOPED_THEORY_FRONTIER_INVENTORY_PASS",
        "inputs_sha256": {p: digest(p) for p in (baseline_name, cut724_name, cut694_name, cutlp_name, cutsubset_name)},
        "scope": "The frozen 132 kernel-port survivors only; not all E71 local configurations.",
        "baseline_macros": len(retained), "baseline_coverage": mass,
        "audited_cuts": cuts, "excluded_macros": len(cuts),
        "excluded_coverage": excluded_mass,
        "remaining_macros": len(remaining), "remaining_coverage": remaining_mass,
        "remaining_keys": [list(key) for key in remaining],
        "whole_E71_layer_excluded": False, "pointwise_E0_lower_bound": None,
        "E72_inventory_changed": False, "submission_txt_written": False,
    }
    Path("scratch_root_e71_theory_frontier_inventory.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k not in ("remaining_keys", "audited_cuts")}, indent=2))


if __name__ == "__main__":
    main()
