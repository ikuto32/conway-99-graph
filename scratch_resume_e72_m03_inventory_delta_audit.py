"""Independent m03 certificate and sole-macro inventory-delta replay.

No inventory producer, solver, or runner is imported. The established
independent catalog reconstruction supplies the 80 representative identities.
This checks the completed finite-CSP evidence and accounting, not a DRAT proof.
"""

from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path

import scratch_root_e72_source150_small5_aggregate_audit as foundation


BEFORE = Path("scratch_root_e72_complete_coverage_inventory_before_m03.json")
AFTER = Path("scratch_root_e72_complete_coverage_inventory.json")
CERTIFICATE = Path("scratch_root_e72_source150_m03_complete_audit.json")
OUTPUT = Path("scratch_resume_e72_m03_inventory_delta_audit.json")
REPORT = Path("scratch_resume_e72_m03_inventory_delta_audit.md")
BEFORE_SHA256 = "6684BBE651687E627D59DD96CE2896CC4C7B5B603D4D4629FA77D31675B62B5E"
CERTIFICATE_SHA256 = "BAE3C5A09D42C140B3EE16B74FC29F52ADEA59BC5CB71E1F7CED622E8722D37F"
SUPPLEMENT_IDS = [11, 36, 38, 56, 57, 58, 59, 63, 65, 71, 74]


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main():
    before, after, certificate = map(load, (BEFORE, AFTER, CERTIFICATE))
    assert sha(BEFORE) == BEFORE_SHA256
    assert sha(CERTIFICATE) == CERTIFICATE_SHA256
    assert before["status"] == after["status"] == "COMPLETE_E72_COVERAGE_INVENTORY_PASS"
    assert certificate["status"] == "SOURCE150_M03_COMPLETE_INDEPENDENT_AUDIT_PASS"
    assert certificate["source_row_index"] == 150 and certificate["macro"] == [0, 3]
    assert certificate["catalog_orbits"] == 80 and certificate["catalog_coverage"] == 4096
    assert certificate["status_histogram"] == {"UNSAT": 80, "SAT": 0, "UNKNOWN": 0}
    assert certificate["status_mass"] == {"UNSAT": 4096, "SAT": 0, "UNKNOWN": 0}
    assert certificate["evidence_class"] == "exact_solver_free_finite_local_CSP_plus_joint_map_supplement"
    assert certificate["DRAT_certificate_present"] is False
    assert certificate["solver_or_runner_imported"] is False
    representatives = foundation.independently_reconstruct_records()[(0, 3)]
    assert len(representatives) == 80
    assert sum(int(row["orbit_size"]) for row in representatives) == 4096
    assert [row["record_number"] for row in certificate["records"]] == list(range(80))
    assert len({row["mask_hex"] for row in certificate["records"]}) == 80
    for name, expected_hash in certificate["inputs"].items():
        assert sha(Path(name)) == expected_hash
    artifacts = {}
    counts, masses = Counter(), Counter()
    for row, representative in zip(certificate["records"], representatives):
        number = row["record_number"]
        assert row["mask_hex"] == representative["mask_hex"]
        assert row["orbit_size"] == int(representative["orbit_size"])
        assert row["Q"] == int(representative["Q"]) == 8
        assert row["status"] == "UNSAT"
        path = Path(row["artifact"])
        assert sha(path) == row["sha256"]
        if str(path) not in artifacts:
            artifacts[str(path)] = load(path)
        document = artifacts[str(path)]
        assert document["status"] == "EXACT_SYNCHRONIZED_CONFIG_CSP_SLICE_COMPLETE"
        assert document["inputs"] == certificate["inputs"]
        summary = document["summary"]
        assert summary["wanted_macros"] == [[0, 3]]
        assert summary["ordinary_local_pair_filter_enabled"] is True
        assert summary["ordinary_local_pair_every_depth_enabled"] is True
        assert summary["fixed_block_projection"] == []
        assert summary["ordinary_joint_map_unknowns_relaxed_as_pass"] == 0
        if number in SUPPLEMENT_IDS:
            assert row["evidence_mode"] == "joint_map_supplement"
            assert summary["explicit_record_selection"] == [number]
            assert summary["ordinary_joint_map_filter_enabled"] is True
            assert len(document["results"]) == 1
            original = document["results"][0]
        else:
            assert row["evidence_mode"] == "direct_everydepth_local_pair"
            assert [r[0] for r in document["results"]] == list(range(80))
            assert [r[0] for r in document["results"] if r[5] == "SAT"] == SUPPLEMENT_IDS
            original = document["results"][number]
        assert original[:6] == [number, row["mask_hex"], row["orbit_size"], 8, [0, 3], "UNSAT"]
        counts[row["evidence_mode"]] += 1
        masses[row["evidence_mode"]] += row["orbit_size"]
    assert len(artifacts) == 12
    assert counts == {"direct_everydepth_local_pair": 69, "joint_map_supplement": 11}
    assert masses == {"direct_everydepth_local_pair": 3648, "joint_map_supplement": 448}

    expected = deepcopy(before)
    assert str(CERTIFICATE) not in expected["inputs"]
    expected["inputs"][str(CERTIFICATE)] = sha(CERTIFICATE)
    expected["global"]["classified_nonopen_coverage"] += 4096
    expected["global"]["unresolved_or_pending_coverage"] -= 4096
    expected["global"]["exact_executable_non_DRAT_coverage"] += 4096
    index = next(i for i, row in enumerate(expected["buckets"]) if row["name"] == "source150_open")
    expected["buckets"][index]["coverage"] -= 4096
    expected["buckets"].insert(index, {
        "name": "source150_m03_complete_rejected", "coverage": 4096,
        "status": "EXACT_SOLVER_FREE_LOCAL_CSP_PLUS_JOINT_MAP_SUPPLEMENT",
    })
    source = expected["source150"]
    source["m03_complete_additional_rejected_coverage"] = 4096
    source["open_coverage"] -= 4096
    macro = next(row for row in source["macro_rows"] if row["macro"] == [0, 3])
    assert macro == {"macro": [0, 3], "coverage": 4096, "status": "OPEN", "excluded_coverage": 0, "open_coverage": 4096}
    macro.update(status="EXACT_SYNCHRONIZED_LOCAL_CSP_ENUM_REJECTED", excluded_coverage=4096, open_coverage=0)
    source["m03_complete_audit"] = str(CERTIFICATE)
    source["m03_complete_audit_sha256"] = sha(CERTIFICATE)
    assert expected == after, "Unexpected inventory change beyond the sole m(0,3) update"
    for inventory in (before, after):
        buckets, global_row = inventory["buckets"], inventory["global"]
        assert sum(row["coverage"] for row in buckets) == global_row["catalog_coverage"] == 141545472
        drat = sum(row["coverage"] for row in buckets if "DRAT" in row["status"] or row["status"] == "FORMAL_AUDIT_PASS")
        exact = sum(row["coverage"] for row in buckets if row["status"].startswith("EXACT_"))
        terminal = sum(row["coverage"] for row in buckets if row["status"].startswith("TERMINAL_"))
        unresolved = sum(row["coverage"] for row in buckets if row["status"] == "OPEN")
        assert drat == global_row["DRAT_backed_coverage"] == 135098368
        assert terminal == global_row["computational_terminal_UNSAT_without_checked_proof"] == 1163264
        assert exact == global_row["exact_executable_non_DRAT_coverage"]
        assert unresolved == global_row["unresolved_or_pending_coverage"]
        assert drat + exact + terminal == global_row["classified_nonopen_coverage"]
        assert drat + exact + terminal + unresolved == 141545472
        macro_rows = inventory["source150"]["macro_rows"]
        assert sum(row["coverage"] for row in macro_rows) == inventory["source150"]["input_coverage"] == 2244608
        assert all(row["excluded_coverage"] + row["open_coverage"] == row["coverage"] for row in macro_rows)
        assert sum(row["open_coverage"] for row in macro_rows) == inventory["source150"]["open_coverage"]
    assert after["source150"]["open_coverage"] == 28672
    assert after["global"]["unresolved_or_pending_coverage"] == 450560
    assert after["global"]["exact_executable_non_DRAT_coverage"] == 4833280
    result = {
        "status": "INDEPENDENT_E72_M03_ONLY_INVENTORY_DELTA_AUDIT_PASS",
        "inputs_sha256": {str(path): sha(path) for path in (BEFORE, AFTER, CERTIFICATE)},
        "only_changed_macro": [150, 0, 3], "new_exact_non_DRAT_coverage": 4096,
        "independently_reconstructed_catalog_orbits": 80,
        "evidence_mode_counts": dict(counts), "evidence_mode_masses": dict(masses),
        "whole_inventory_equals_expected_single_macro_delta": True,
        "partial_or_supplement_mass_counted_separately": False,
        "DRAT_coverage_unchanged": 135098368,
        "terminal_without_checked_proof_coverage_unchanged": 1163264,
        "total_partition_coverage": 141545472,
        "exact_executable_non_DRAT_coverage_after": 4833280,
        "source150_open_coverage_before_after": [32768, 28672],
        "global_unresolved_coverage_before_after": [454656, 450560],
        "inventory_producer_solver_or_runner_imported": False,
        "central_inventory_written": False,
        "scope": "Independent 80-representative finite-CSP certificate replay and exact whole-document accounting delta. Only complete macro (150,0,3), mass4096, is transferred once. The 448 supplement mass is not separately credited. This is not DRAT or a full E72/Conway nonexistence proof.",
    }
    foundation.atomic_json(OUTPUT, result)
    foundation.atomic_text(REPORT, "\n".join([
        "# m03 complete-macro inventory delta audit", "",
        f"Status: `{result['status']}`.", "",
        "The independent catalog reconstruction verifies all 80 m03 representatives exactly once. The evidence combines 69 direct UNSAT orbits (mass 3,648) with 11 joint-map UNSAT supplements (mass 448). Every representative identity, Q, orbit size, artifact hash, and UNSAT result is checked.", "",
        "The after inventory equals the immutable before inventory plus the sole complete macro (150,0,3) transfer of 4,096. Source150 open coverage changes 32,768 to 28,672; total E72 unresolved coverage changes 454,656 to 450,560. DRAT and terminal-without-proof buckets are unchanged. No partial mass or supplement mass receives separate credit.", "",
        "The certificate is exact finite local CSP evidence, not DRAT, complete E72 exclusion, or a solution of Conway's 99-graph problem.", "",
    ]))
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
