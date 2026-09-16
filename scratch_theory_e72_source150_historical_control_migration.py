"""Metadata-only JSON migration for the historical six-profile controls.

The byte-identical snapshot has already been created. No central inventory,
runner, solver or immutable graph-search certificate is read or written here.
"""

import hashlib
import json
from pathlib import Path

SNAPSHOT = Path("scratch_root_e72_complete_coverage_inventory_before_m10.json")
OLD_INPUT = "scratch_root_e72_complete_coverage_inventory.json"
APPLICABILITY = Path("scratch_theory_e72_source150_degree_moment_applicability.json")
LABEL = Path("scratch_theory_e72_source150_label_subset_probe.json")
OUTPUT = Path("scratch_theory_e72_source150_historical_control_migration.json")
EXPECTED = "651115B9B9443E8CC4A6C732E14BC50AC959C7D8C087BCD0967D6CF11928E0D0"
SCOPE = "Only six historically OPEN source150 compressed profiles frozen in the before_m10 inventory snapshot, total coverage40960. These historical controls make no claim about current open status. Six small LP feasibility checks, no E72 completion solver or graph search launched or restarted."


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def payload_hash(document):
    payload = {key: value for key, value in document.items() if key not in ("inputs_sha256", "scope")}
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest().upper()


def main():
    assert sha(SNAPSHOT) == EXPECTED
    applicability = json.loads(APPLICABILITY.read_text(encoding="utf-8"))
    label = json.loads(LABEL.read_text(encoding="utf-8"))
    applicability_old_hash = sha(APPLICABILITY)
    label_old_hash = sha(LABEL)
    assert label["inputs_sha256"][str(APPLICABILITY)] == applicability_old_hash
    payload_before = {str(APPLICABILITY): payload_hash(applicability), str(LABEL): payload_hash(label)}
    manifest = applicability["inputs_sha256"]
    assert manifest.pop(OLD_INPUT) == EXPECTED
    manifest[str(SNAPSHOT)] = EXPECTED
    applicability["scope"] = SCOPE
    APPLICABILITY.write_text(json.dumps(applicability, indent=2) + "\n", encoding="utf-8")
    label["inputs_sha256"][str(APPLICABILITY)] = sha(APPLICABILITY)
    LABEL.write_text(json.dumps(label, indent=2) + "\n", encoding="utf-8")
    payload_after = {str(path): payload_hash(json.loads(path.read_text(encoding="utf-8"))) for path in (APPLICABILITY, LABEL)}
    assert payload_before == payload_after
    result = {"status": "E72_HISTORICAL_SIX_CONTROL_METADATA_MIGRATION_PASS",
              "snapshot": str(SNAPSHOT), "snapshot_sha256": EXPECTED,
              "applicability_input_path_rebound_from": OLD_INPUT,
              "applicability_input_path_rebound_to": str(SNAPSHOT),
              "applicability_scope_rebound_to_historical": True,
              "changed_artifact_sha256": {str(APPLICABILITY): {"before": applicability_old_hash, "after": sha(APPLICABILITY)},
                                          str(LABEL): {"before": label_old_hash, "after": sha(LABEL)}},
              "all_non_metadata_payloads_sha256_before": payload_before,
              "all_non_metadata_payloads_sha256_after": payload_after,
              "all_non_metadata_payloads_unchanged": True,
              "central_inventory_or_runner_or_solver_or_m10_certificate_touched": False}
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
