"""One-worker checkpointed joint-map supplement for the exact 11 m03 local-SAT records."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


SOLVER = Path("scratch_theory_e72_source150_synchronized_config_csp.py")
SOLVER_SHA256 = "BE279135FF346E8CB22BEE5DB5DB4D4807D4C2FDE858FC53382BA1D8DBA21C6F"
DIRECT = Path("scratch_theory_e72_source150_sync_localpair_everydepth_m03_full.json")
DIRECT_SHA256 = "2126D7F6A3FA61D10ACD8F79E3C6B11FECEF72DB769FAE4709071579859633E3"
AUDIT = Path("scratch_root_e72_source150_m03_everydepth_full_audit.json")
RECORDS = (11, 36, 38, 56, 57, 58, 59, 63, 65, 71, 74)
MANIFEST = Path("scratch_root_e72_source150_m03_joint_supplement_manifest.json")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path, document):
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def validate(path, number, expected):
    document = load(path)
    assert document["status"] == "EXACT_SYNCHRONIZED_CONFIG_CSP_SLICE_COMPLETE"
    summary = document["summary"]
    assert summary["wanted_macros"] == [[0, 3]]
    assert summary["available_orbits_in_wanted_macros"] == 80
    assert summary["explicit_record_selection"] == [number]
    assert summary["input_orbits"] == 1
    for flag in ("ordinary_local_pair_filter_enabled", "ordinary_local_pair_every_depth_enabled", "ordinary_joint_map_filter_enabled"):
        assert summary[flag] is True
    assert summary["ordinary_joint_map_unknowns_relaxed_as_pass"] == 0
    assert summary["fixed_block_projection"] == []
    assert len(document["results"]) == 1
    row = document["results"][0]
    assert row[:5] == [number, expected["mask_hex"], expected["orbit_size"], 8, [0, 3]]
    assert row[5] in {"UNSAT", "SAT", "UNKNOWN"}
    assert summary["input_mass"] == expected["orbit_size"]
    assert summary["status_histogram"] == {row[5]: 1}
    for status in ("SAT", "UNSAT", "UNKNOWN"):
        assert summary[f"{status}_mass"] == (expected["orbit_size"] if row[5] == status else 0)
    return {"status": "COMPLETE", "path": str(path), "sha256": digest(path),
            "record_number": number, "result_status": row[5], "orbit_size": expected["orbit_size"],
            "DFS_nodes": row[7], "elapsed_seconds": summary["elapsed_seconds"],
            "ordinary_joint_map_calls": summary["ordinary_joint_map_calls"],
            "ordinary_joint_map_nodes": summary["ordinary_joint_map_nodes"]}


def main():
    assert digest(SOLVER) == SOLVER_SHA256
    assert digest(DIRECT) == DIRECT_SHA256
    audit = load(AUDIT)
    assert audit["status"] == "SOURCE150_M03_EVERYDEPTH_FULL_CATALOG_AUDIT_PASS"
    assert tuple(audit["SAT_record_numbers"]) == RECORDS
    assert audit["source_sha256"] == DIRECT_SHA256
    expected = {row["record_number"]: row for row in audit["SAT_survivors"]}
    assert set(expected) == set(RECORDS)
    assert sum(row["orbit_size"] for row in expected.values()) == 448
    manifest = {
        "status": "RUNNING", "source_row_index": 150, "macro": [0, 3],
        "solver": str(SOLVER), "solver_sha256": SOLVER_SHA256,
        "runner_sha256": digest(Path(__file__)), "source_sha256": DIRECT_SHA256,
        "direct_audit": str(AUDIT), "direct_audit_sha256": digest(AUDIT),
        "records": list(RECORDS), "input_orbits": 11, "input_mass": 448,
        "jobs": 1, "node_cap": 0, "joint_map_node_cap": 0,
        "ordinary_local_pair": True, "ordinary_local_pair_every_depth": True,
        "ordinary_joint_map": True, "projection": [], "started_unix": time.time(),
        "record_results": {},
    }
    atomic_json(MANIFEST, manifest)
    for number in RECORDS:
        path = Path(f"scratch_theory_e72_source150_sync_jointmap_m03_sat_r{number}.json")
        if path.exists():
            record = validate(path, number, expected[number])
            record["mode"] = "validated_existing"
        else:
            command = [sys.executable, str(SOLVER), "--macros", "0:3", "--records", str(number),
                       "--ordinary-local-pair", "--ordinary-local-pair-every-depth", "--ordinary-joint-map",
                       "--node-cap", "0", "--joint-map-node-cap", "0", "--output", str(path)]
            completed = subprocess.run(command, text=True, capture_output=True, check=False)
            if completed.returncode:
                manifest["status"] = "FAILED"
                manifest["record_results"][str(number)] = {"status": "FAILED", "returncode": completed.returncode,
                                                           "stdout_tail": completed.stdout[-4000:],
                                                           "stderr_tail": completed.stderr[-4000:]}
                atomic_json(MANIFEST, manifest)
                raise SystemExit(completed.returncode)
            record = validate(path, number, expected[number])
            record["mode"] = "executed"
        manifest["record_results"][str(number)] = record
        atomic_json(MANIFEST, manifest)
        print(json.dumps(record, separators=(",", ":")), flush=True)
    manifest["status"] = "COMPLETE"
    manifest["finished_unix"] = time.time()
    atomic_json(MANIFEST, manifest)
    print(json.dumps({"status": "COMPLETE", "records": 11, "mass": 448, "manifest": str(MANIFEST)}, separators=(",", ":")), flush=True)


if __name__ == "__main__":
    main()
