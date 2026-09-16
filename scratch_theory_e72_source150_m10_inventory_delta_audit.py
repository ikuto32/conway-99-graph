"""Independent before/after inventory comparison; no inventory producer import.

Verifies only the exact expected metadata and coverage delta. It does not
replace the separate immutable 96-record local-CSP certificate audit.
"""

from copy import deepcopy
import hashlib
import json
from pathlib import Path

BEFORE = Path("scratch_root_e72_complete_coverage_inventory_before_m10.json")
AFTER = Path("scratch_root_e72_complete_coverage_inventory.json")
M10 = Path("scratch_root_e72_source150_small5_joint_primary_m10_complete_audit.json")
OUTPUT = Path("scratch_theory_e72_source150_m10_inventory_delta_audit.json")


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main():
    before, after, m10 = map(read, (BEFORE, AFTER, M10))
    assert sha(BEFORE) == "651115B9B9443E8CC4A6C732E14BC50AC959C7D8C087BCD0967D6CF11928E0D0"
    assert before["status"] == after["status"] == "COMPLETE_E72_COVERAGE_INVENTORY_PASS"
    assert m10["status"] == "SOURCE150_SINGLE_MACRO_JOINT_PRIMARY_INDEPENDENT_AUDIT_PASS"
    assert m10["source_row_index"] == 150 and m10["macro"] == [1, 0]
    assert m10["catalog_orbits"] == 96 and m10["catalog_coverage"] == 8192
    assert m10["status_histogram"] == {"UNSAT": 96, "SAT": 0, "UNKNOWN": 0}
    assert m10["status_mass"] == {"UNSAT": 8192, "SAT": 0, "UNKNOWN": 0}
    assert m10["evidence_class"] == "exact_solver_free_finite_local_CSP" and m10["DRAT_certificate_present"] is False
    expected = deepcopy(before)
    assert str(M10) not in expected["inputs"]
    expected["inputs"][str(M10)] = sha(M10)
    expected["global"]["classified_nonopen_coverage"] += 8192
    expected["global"]["unresolved_or_pending_coverage"] -= 8192
    expected["global"]["exact_executable_non_DRAT_coverage"] += 8192
    index = next(i for i, row in enumerate(expected["buckets"]) if row["name"] == "source150_open")
    expected["buckets"][index]["coverage"] -= 8192
    expected["buckets"].insert(index, {"name": "source150_m10_joint_primary_rejected", "coverage": 8192,
                                       "status": "EXACT_SOLVER_FREE_LOCAL_CSP_JOINT_MAP_PRIMARY"})
    source = expected["source150"]
    source["m10_joint_primary_additional_rejected_coverage"] = 8192
    source["open_coverage"] -= 8192
    macro = next(row for row in source["macro_rows"] if row["macro"] == [1, 0])
    assert macro == {"macro": [1, 0], "coverage": 8192, "status": "OPEN", "excluded_coverage": 0, "open_coverage": 8192}
    macro.update(status="EXACT_SYNCHRONIZED_LOCAL_CSP_ENUM_REJECTED", excluded_coverage=8192, open_coverage=0)
    source["m10_joint_primary_audit"] = str(M10)
    source["m10_joint_primary_audit_sha256"] = sha(M10)
    assert expected == after, "Unexpected inventory change outside the sole m(1,0) update"
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
    assert after["source150"]["open_coverage"] == 32768
    assert after["global"]["unresolved_or_pending_coverage"] == 454656
    assert after["global"]["exact_executable_non_DRAT_coverage"] == 4829184
    result = {"status": "INDEPENDENT_E72_M10_ONLY_INVENTORY_DELTA_AUDIT_PASS",
              "inputs_sha256": {str(path): sha(path) for path in (BEFORE, AFTER, M10)},
              "only_changed_macro": [150, 1, 0], "new_exact_non_DRAT_coverage": 8192,
              "whole_inventory_equals_expected_single_macro_delta": True,
              "DRAT_coverage_unchanged": 135098368, "terminal_without_checked_proof_coverage_unchanged": 1163264,
              "total_partition_coverage": 141545472,
              "exact_executable_non_DRAT_coverage_after": 4829184,
              "source150_open_coverage_before_after": [40960, 32768],
              "global_unresolved_coverage_before_after": [462848, 454656],
              "scope": "Independent read-only comparison and recomputation of every coverage bucket. The entire after document equals the before document plus the explicitly enumerated m(1,0) metadata, sole macro transition, and 8192-class exact-CSP transfer. The separate immutable local-CSP certificate supplies branch soundness; this audit does not rerun those 96 searches.",
              "central_inventory_written": False}
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
