"""Independent catalog/coverage audit of the completed m(0,3) local-pair sweep."""

from collections import Counter
import json
from pathlib import Path

import scratch_root_e72_source150_small5_aggregate_audit as foundation


MACRO = (0, 3)
DIRECT = Path("scratch_theory_e72_source150_sync_localpair_everydepth_m03_full.json")
DIRECT_SHA256 = "2126D7F6A3FA61D10ACD8F79E3C6B11FECEF72DB769FAE4709071579859633E3"
SOLVER = Path("scratch_theory_e72_source150_synchronized_config_csp.py")
SOLVER_SHA256 = "BE279135FF346E8CB22BEE5DB5DB4D4807D4C2FDE858FC53382BA1D8DBA21C6F"
SAT_RECORDS = (11, 36, 38, 56, 57, 58, 59, 63, 65, 71, 74)
OUTPUT = Path("scratch_root_e72_source150_m03_everydepth_full_audit.json")
REPORT = Path("scratch_root_e72_source150_m03_everydepth_full_audit.md")


def main():
    assert foundation.sha256(DIRECT) == DIRECT_SHA256
    assert foundation.sha256(SOLVER) == SOLVER_SHA256
    records = foundation.independently_reconstruct_records()
    representatives = records[MACRO]
    assert len(representatives) == 80
    assert sum(int(row["orbit_size"]) for row in representatives) == 4096
    assert {int(row["Q"]) for row in representatives} == {8}
    base_inputs = (foundation.LOCAL, foundation.CATALOG, foundation.GRAM,
                   foundation.FIBRE_FILTER, foundation.CONFIG_FRONTIER)
    base_hashes = {str(path): foundation.sha256(path) for path in base_inputs}
    document = foundation.load(DIRECT)
    assert document["status"] == "EXACT_SYNCHRONIZED_CONFIG_CSP_SLICE_COMPLETE"
    assert document["inputs"] == base_hashes
    summary = document["summary"]
    assert summary["wanted_macros"] == [[0, 3]]
    assert summary["available_orbits_in_wanted_macros"] == 80
    assert summary["slice_start"] == 0 and summary["slice_stop"] == 80
    assert summary["explicit_record_selection"] == []
    assert summary["input_orbits"] == 80 and summary["input_mass"] == 4096
    assert summary["ordinary_local_pair_filter_enabled"] is True
    assert summary["ordinary_local_pair_every_depth_enabled"] is True
    assert summary["ordinary_joint_map_filter_enabled"] is False
    assert summary["ordinary_joint_map_calls"] == summary["ordinary_joint_map_nodes"] == 0
    assert summary["ordinary_joint_map_unknowns_relaxed_as_pass"] == 0
    assert summary["fixed_block_projection"] == []
    assert [int(row[0]) for row in document["results"]] == list(range(80))
    histogram, masses = Counter(), Counter()
    evidence = []
    for row in document["results"]:
        number, representative = foundation.verify_result(row, MACRO, records)
        status, mass = str(row[5]), int(representative["orbit_size"])
        assert status in {"SAT", "UNSAT"}
        if status == "SAT":
            assert row[6] == "witness"
            assert len(row[8]) == 12 and len(row[9]) > 0
        else:
            assert row[6] in {"simultaneous_CSP_exhausted", "empty_synchronized_pointwise_table"}
        histogram[status] += 1
        masses[status] += mass
        evidence.append({"record_number": number, "mask_hex": representative["mask_hex"],
                         "Q": 8, "orbit_size": mass, "status": status,
                         "reason": row[6], "DFS_nodes": int(row[7])})
    assert histogram == {"UNSAT": 69, "SAT": 11}
    assert masses == {"UNSAT": 3648, "SAT": 448}
    assert dict(histogram) == summary["status_histogram"]
    for status in ("SAT", "UNSAT", "UNKNOWN"):
        assert masses[status] == summary[f"{status}_mass"]
    survivors = [row for row in evidence if row["status"] == "SAT"]
    assert tuple(row["record_number"] for row in survivors) == SAT_RECORDS
    assert len({row["mask_hex"] for row in survivors}) == 11
    model_paths = (
        SOLVER, Path("scratch_theory_e72_source150_norm_collision_filter.py"),
        Path("scratch_theory_e72_source150_fibre_recurrence_filter.py"),
        Path("scratch_theory_e72_source150_pointwise_recurrence_csp.py"),
        Path("scratch_theory_e72_source150_disjoint_graphical_filter.py"),
    )
    result = {
        "status": "SOURCE150_M03_EVERYDEPTH_FULL_CATALOG_AUDIT_PASS",
        "source_row_index": 150, "macro": [0, 3], "Q": 8,
        "catalog_orbits": 80, "catalog_coverage": 4096,
        "source_artifact": str(DIRECT), "source_sha256": DIRECT_SHA256,
        "inputs": base_hashes,
        "current_model_code_sha256": {str(path): foundation.sha256(path) for path in model_paths},
        "execution_time_solver_digest_embedded_in_result": False,
        "current_solver_sha256": SOLVER_SHA256,
        "source_digest_scope": "Current solver is checked against the pre-existing fixed small-five solver hash. The direct result embeds data-input hashes, not an execution-time code digest.",
        "solver_or_runner_imported": False,
        "auditor_sha256": foundation.sha256(Path(__file__)),
        "foundation_sha256": foundation.sha256(Path(foundation.__file__)),
        "mode": {"ordinary_local_pair": True, "ordinary_local_pair_every_depth": True,
                 "ordinary_joint_map": False, "projection": []},
        "status_histogram": {s: histogram[s] for s in ("UNSAT", "SAT", "UNKNOWN")},
        "status_mass": {s: masses[s] for s in ("UNSAT", "SAT", "UNKNOWN")},
        "SAT_record_numbers": list(SAT_RECORDS), "SAT_survivors": survivors,
        "records": evidence,
        "coverage_checks": {"independent_catalog_reconstruction": True,
                            "record_numbers_exactly_once": True,
                            "all_representative_masks_Q_orbit_sizes_checked": True,
                            "survivor_mass_exactly_448": True},
        "whole_macro_excluded": False, "DRAT_certificate_present": False,
        "claim_boundary": "The 69 exhaustive local-CSP UNSAT cases cover mass3648; 11 local-SAT cases of mass448 remain open and do not constitute an SRG. Only these exact 11 cases are licensed inputs to the joint-map supplement.",
    }
    foundation.atomic_json(OUTPUT, result)
    foundation.atomic_text(REPORT, "# Source150 m(0,3) every-depth coverage audit\n\n"
                           "Status: `SOURCE150_M03_EVERYDEPTH_FULL_CATALOG_AUDIT_PASS`.\n\n"
                           "All 80 catalog orbits / labelled mass 4,096 were checked exactly once. "
                           "There are 69 exact local-CSP UNSAT records / mass 3,648 and "
                           "11 local-SAT records / mass 448. UNKNOWN is zero.\n\n"
                           f"Joint-map supplement record IDs: `{','.join(map(str, SAT_RECORDS))}`.\n\n"
                           "Each representative mask, Q=8, orbit size, result status, input hash, "
                           "and the frozen direct-result SHA is checked by independent catalog "
                           "reconstruction. The current solver digest is pinned; the direct output "
                           "itself contains data-input hashes, not an execution-time code digest.\n\n"
                           "This is not a whole-macro exclusion or a DRAT certificate. Local-SAT "
                           "cases remain open until a further necessary-condition contradiction or "
                           "a verified full graph is supplied.\n")
    print(json.dumps({"status": result["status"], "UNSAT_orbits": 69, "UNSAT_mass": 3648,
                      "SAT_orbits": 11, "SAT_mass": 448, "SAT_record_numbers": list(SAT_RECORDS),
                      "source_sha256": DIRECT_SHA256}, separators=(",", ":")))


if __name__ == "__main__":
    main()
