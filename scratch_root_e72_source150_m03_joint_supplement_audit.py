"""Independent singleton supplement coverage audit and complete m03 certificate."""

from collections import Counter
import hashlib
import json
from pathlib import Path

import scratch_root_e72_source150_small5_aggregate_audit as foundation


DIRECT = Path("scratch_theory_e72_source150_sync_localpair_everydepth_m03_full.json")
DIRECT_SHA256 = "2126D7F6A3FA61D10ACD8F79E3C6B11FECEF72DB769FAE4709071579859633E3"
DIRECT_AUDIT = Path("scratch_root_e72_source150_m03_everydepth_full_audit.json")
SOLVER = Path("scratch_theory_e72_source150_synchronized_config_csp.py")
SOLVER_SHA256 = "BE279135FF346E8CB22BEE5DB5DB4D4807D4C2FDE858FC53382BA1D8DBA21C6F"
RUNNER = Path("scratch_root_e72_source150_m03_joint_supplement_runner.py")
MANIFEST = Path("scratch_root_e72_source150_m03_joint_supplement_manifest.json")
RECORDS = (11, 36, 38, 56, 57, 58, 59, 63, 65, 71, 74)
OUTPUT = Path("scratch_root_e72_source150_m03_joint_supplement_audit.json")
COMPLETE = Path("scratch_root_e72_source150_m03_complete_audit.json")


def main():
    assert foundation.sha256(DIRECT) == DIRECT_SHA256
    assert foundation.sha256(SOLVER) == SOLVER_SHA256
    records = foundation.independently_reconstruct_records()
    reps = records[(0, 3)]
    assert len(reps) == 80 and sum(int(row["orbit_size"]) for row in reps) == 4096
    assert {int(row["Q"]) for row in reps} == {8}
    base_inputs = (foundation.LOCAL, foundation.CATALOG, foundation.GRAM,
                   foundation.FIBRE_FILTER, foundation.CONFIG_FRONTIER)
    inputs = {str(path): foundation.sha256(path) for path in base_inputs}
    direct = foundation.load(DIRECT)
    assert direct["status"] == "EXACT_SYNCHRONIZED_CONFIG_CSP_SLICE_COMPLETE"
    assert direct["inputs"] == inputs
    assert [row[0] for row in direct["results"]] == list(range(80))
    direct_hist, direct_mass = Counter(), Counter()
    for row in direct["results"]:
        _number, representative = foundation.verify_result(row, (0, 3), records)
        direct_hist[row[5]] += 1
        direct_mass[row[5]] += int(representative["orbit_size"])
    assert direct_hist == {"UNSAT": 69, "SAT": 11}
    assert direct_mass == {"UNSAT": 3648, "SAT": 448}
    assert tuple(row[0] for row in direct["results"] if row[5] == "SAT") == RECORDS
    direct_audit = foundation.load(DIRECT_AUDIT)
    assert direct_audit["status"] == "SOURCE150_M03_EVERYDEPTH_FULL_CATALOG_AUDIT_PASS"
    assert direct_audit["source_sha256"] == DIRECT_SHA256
    assert tuple(direct_audit["SAT_record_numbers"]) == RECORDS
    manifest_bytes = MANIFEST.read_bytes()
    manifest = json.loads(manifest_bytes)
    assert manifest["status"] in {"RUNNING", "COMPLETE", "FAILED"}
    assert manifest["solver_sha256"] == SOLVER_SHA256
    assert manifest["runner_sha256"] == foundation.sha256(RUNNER)
    assert manifest["source_sha256"] == DIRECT_SHA256
    assert manifest["direct_audit_sha256"] == foundation.sha256(DIRECT_AUDIT)
    assert tuple(manifest["records"]) == RECORDS
    assert manifest["node_cap"] == manifest["joint_map_node_cap"] == 0
    assert manifest["jobs"] == 1 and manifest["projection"] == []
    assert manifest["input_orbits"] == 11 and manifest["input_mass"] == 448
    for flag in ("ordinary_local_pair", "ordinary_local_pair_every_depth", "ordinary_joint_map"):
        assert manifest[flag] is True
    assert set(map(int, manifest["record_results"])) <= set(RECORDS)
    supplement = {}
    failures = []
    histogram, masses = Counter(), Counter()
    for key, checkpoint in manifest["record_results"].items():
        number = int(key)
        if checkpoint["status"] != "COMPLETE":
            failures.append({"record_number": number, "checkpoint": checkpoint})
            continue
        path = Path(f"scratch_theory_e72_source150_sync_jointmap_m03_sat_r{number}.json")
        digest = foundation.sha256(path)
        assert checkpoint["path"] == str(path) and checkpoint["sha256"] == digest
        document = foundation.load(path)
        assert document["status"] == "EXACT_SYNCHRONIZED_CONFIG_CSP_SLICE_COMPLETE"
        assert document["inputs"] == inputs
        summary = document["summary"]
        assert summary["wanted_macros"] == [[0, 3]]
        assert summary["available_orbits_in_wanted_macros"] == 80
        assert summary["explicit_record_selection"] == [number]
        assert summary["input_orbits"] == 1 and summary["fixed_block_projection"] == []
        for flag in ("ordinary_local_pair_filter_enabled", "ordinary_local_pair_every_depth_enabled", "ordinary_joint_map_filter_enabled"):
            assert summary[flag] is True
        assert summary["ordinary_joint_map_unknowns_relaxed_as_pass"] == 0
        assert len(document["results"]) == 1
        row = document["results"][0]
        got_number, representative = foundation.verify_result(row, (0, 3), records)
        assert got_number == number
        status, mass = str(row[5]), int(representative["orbit_size"])
        assert status == checkpoint["result_status"]
        assert summary["status_histogram"] == {status: 1}
        assert summary["input_mass"] == mass == checkpoint["orbit_size"]
        for candidate_status in ("SAT", "UNSAT", "UNKNOWN"):
            assert summary[f"{candidate_status}_mass"] == (mass if status == candidate_status else 0)
        histogram[status] += 1
        masses[status] += mass
        supplement[number] = {"record_number": number, "mask_hex": representative["mask_hex"],
                              "orbit_size": mass, "Q": 8, "status": status,
                              "artifact": str(path), "sha256": digest,
                              "reason": row[6], "DFS_nodes": row[7],
                              "elapsed_seconds": summary["elapsed_seconds"]}
    all_audited = set(supplement) == set(RECORDS)
    closed = all_audited and histogram == {"UNSAT": 11} and masses == {"UNSAT": 448}
    result = {
        "status": "SOURCE150_M03_JOINT_SUPPLEMENT_CHECKPOINT_AUDIT_PASS",
        "source_sha256": DIRECT_SHA256, "direct_audit_sha256": foundation.sha256(DIRECT_AUDIT),
        "solver_sha256": SOLVER_SHA256, "runner_sha256": foundation.sha256(RUNNER),
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest().upper(), "inputs": inputs,
        "solver_or_runner_imported": False, "expected_records": list(RECORDS),
        "audited_singletons": len(supplement), "missing_records": sorted(set(RECORDS) - set(supplement)),
        "status_histogram": {s: histogram[s] for s in ("UNSAT", "SAT", "UNKNOWN")},
        "status_mass": {s: masses[s] for s in ("UNSAT", "SAT", "UNKNOWN")},
        "failed_checkpoints": failures, "all_singletons_audited": all_audited,
        "whole_macro_excluded": closed, "partial_macro_credit_authorized": False,
        "records": [supplement[number] for number in sorted(supplement)],
    }
    if closed:
        final_records = []
        for number, direct_row in enumerate(direct["results"]):
            if direct_row[5] == "UNSAT":
                final_records.append({"record_number": number, "mask_hex": reps[number]["mask_hex"],
                                      "orbit_size": int(reps[number]["orbit_size"]), "Q": 8,
                                      "status": "UNSAT", "artifact": str(DIRECT), "sha256": DIRECT_SHA256,
                                      "evidence_mode": "direct_everydepth_local_pair"})
            else:
                final_records.append({**supplement[number], "evidence_mode": "joint_map_supplement"})
        assert [row["record_number"] for row in final_records] == list(range(80))
        assert sum(row["orbit_size"] for row in final_records) == 4096
        certificate = {
            "status": "SOURCE150_M03_COMPLETE_INDEPENDENT_AUDIT_PASS",
            "source_row_index": 150, "macro": [0, 3], "Q": 8,
            "catalog_orbits": 80, "catalog_coverage": 4096,
            "status_histogram": {"UNSAT": 80, "SAT": 0, "UNKNOWN": 0},
            "status_mass": {"UNSAT": 4096, "SAT": 0, "UNKNOWN": 0},
            "direct_UNSAT_orbits": 69, "supplement_UNSAT_orbits": 11,
            "inputs": inputs, "direct_result_sha256": DIRECT_SHA256,
            "direct_audit_sha256": foundation.sha256(DIRECT_AUDIT),
            "solver_sha256": SOLVER_SHA256, "supplement_runner_sha256": foundation.sha256(RUNNER),
            "auditor_sha256": foundation.sha256(Path(__file__)),
            "coverage_checks": {"independent_catalog_reconstruction": True,
                                "all_80_records_exactly_once": True,
                                "all_representative_masks_Q_orbit_sizes_checked": True,
                                "only_direct_SAT_records_supplemented": True},
            "records": final_records, "solver_or_runner_imported": False,
            "evidence_class": "exact_solver_free_finite_local_CSP_plus_joint_map_supplement",
            "DRAT_certificate_present": False,
            "claim_boundary": "Only the complete source150 macro (0,3) is excluded. Local-SAT records were not credited until their exact joint-map supplement was UNSAT. This does not exclude all source150 or E0=72 and makes no DRAT claim.",
        }
        if COMPLETE.exists():
            assert foundation.load(COMPLETE) == certificate
        else:
            foundation.atomic_json(COMPLETE, certificate)
        result["complete_macro_certificate"] = {"path": str(COMPLETE), "sha256": foundation.sha256(COMPLETE)}
    foundation.atomic_json(OUTPUT, result)
    print(json.dumps({key: result[key] for key in ("status", "audited_singletons", "missing_records",
                                                  "status_histogram", "status_mass", "whole_macro_excluded")}, separators=(",", ":")))
    if closed:
        print(json.dumps(result["complete_macro_certificate"], separators=(",", ":")))


if __name__ == "__main__":
    main()
