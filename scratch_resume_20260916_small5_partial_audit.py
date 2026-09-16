"""Audit completed small-five checkpoints without trusting a live-run status.

Only a fully covered, all-UNSAT macro is eligible for macro-level exclusion.
No producer or solver code is imported. The frozen independent catalog
reconstruction is shared with the established full aggregate audit.
"""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import time

import scratch_root_e72_source150_small5_aggregate_audit as foundation


EXPECTED = {
    (1, 0): (96, 8192, 4),
    (3, 3): (116, 8192, 4),
    (9, 0): (52, 4096, 8),
    (10, 0): (63, 8192, 4),
    (11, 0): (73, 8192, 4),
}
TASKS = tuple(
    (macro, start, min(start + 8, count))
    for macro, (count, _mass, _q) in EXPECTED.items()
    for start in range(0, count, 8)
)
MANIFEST = Path("scratch_root_e72_source150_small5_joint_primary_manifest.json")
SOLVER = Path("scratch_theory_e72_source150_synchronized_config_csp.py")
RUNNER = Path("scratch_root_e72_source150_small5_joint_primary_runner.py")
OUTPUT = Path("scratch_resume_20260916_small5_partial_audit.json")
SOLVER_SHA256 = "BE279135FF346E8CB22BEE5DB5DB4D4807D4C2FDE858FC53382BA1D8DBA21C6F"
RUNNER_SHA256 = "4A6AE54851BB2B8702BD1A78AC2EC83800BEEDD2F72B051B6BC71595AEC732CB"


def freeze_closed_macro(row, records, audited_shards, base_hashes):
    """Emit an immutable complete-macro certificate, independent of live state."""
    macro = tuple(row["macro"])
    if not row["macro_exclusion_eligible"]:
        return None
    shards = [item for item in audited_shards
              if item["task"].startswith(f"{macro[0]}:{macro[1]}:")]
    by_number = {}
    for shard in shards:
        _a, _b, start, stop = map(int, shard["task"].split(":"))
        for number in range(start, stop):
            assert number not in by_number
            by_number[number] = shard
    assert set(by_number) == set(range(EXPECTED[macro][0]))
    record_evidence = []
    for number, representative in enumerate(records[macro]):
        shard = by_number[number]
        record_evidence.append({
            "record_number": number, "mask_hex": representative["mask_hex"],
            "orbit_size": int(representative["orbit_size"]),
            "Q": int(representative["Q"]), "status": "UNSAT",
            "artifact": shard["path"], "sha256": shard["sha256"],
        })
    certificate = {
        "status": "SOURCE150_SINGLE_MACRO_JOINT_PRIMARY_INDEPENDENT_AUDIT_PASS",
        "source_row_index": 150, "macro": list(macro), "Q": row["Q"],
        "catalog_orbits": row["expected_records"], "catalog_coverage": row["expected_mass"],
        "status_histogram": {"UNSAT": row["expected_records"], "SAT": 0, "UNKNOWN": 0},
        "status_mass": {"UNSAT": row["expected_mass"], "SAT": 0, "UNKNOWN": 0},
        "solver_sha256": SOLVER_SHA256, "runner_sha256": RUNNER_SHA256,
        "audit_source_sha256": foundation.sha256(Path(__file__)),
        "foundation_sha256": foundation.sha256(Path(foundation.__file__)),
        "inputs": base_hashes,
        "mode": {"ordinary_local_pair": True, "ordinary_local_pair_every_depth": True,
                 "ordinary_joint_map": True, "node_cap": 0, "joint_map_node_cap": 0,
                 "ordinary_joint_map_unknowns_relaxed_as_pass": 0, "projection": []},
        "coverage_checks": {"independent_catalog_reconstruction": True,
                            "record_numbers_exactly_once": True,
                            "representative_masks_Q_orbit_sizes_checked": True,
                            "all_records_UNSAT": True, "no_missing_records": True},
        "solver_or_runner_imported": False,
        "evidence_class": "exact_solver_free_finite_local_CSP",
        "DRAT_certificate_present": False,
        "shards": sorted(shards, key=lambda item: int(item["task"].split(":")[2])),
        "records": record_evidence,
        "claim_boundary": "Only this full source150 macro is excluded. This certificate does not exclude all source150 or E0=72 and makes no DRAT claim. It has no dependency on the mutable live manifest or partial audit JSON.",
    }
    path = Path(f"scratch_resume_20260916_small5_m{macro[0]}{macro[1]}_complete_audit.json")
    if path.exists():
        assert foundation.load(path) == certificate
    else:
        foundation.atomic_json(path, certificate)
    return {"macro": list(macro), "path": str(path), "sha256": foundation.sha256(path),
            "catalog_orbits": row["expected_records"], "catalog_coverage": row["expected_mass"]}


def main() -> None:
    started = time.monotonic()
    manifest_bytes = MANIFEST.read_bytes()
    manifest = json.loads(manifest_bytes)
    assert manifest["status"] in {"RUNNING", "COMPLETE", "FAILED"}
    assert manifest["solver"] == str(SOLVER)
    assert manifest["solver_sha256"] == foundation.sha256(SOLVER) == SOLVER_SHA256
    assert foundation.sha256(RUNNER) == RUNNER_SHA256
    assert manifest["macros"] == [list(macro) for macro in EXPECTED]
    for flag in ("ordinary_local_pair", "ordinary_local_pair_every_depth", "ordinary_joint_map"):
        assert manifest[flag] is True
    assert manifest["node_cap"] == manifest["joint_map_node_cap"] == 0
    assert manifest["projection"] == []
    assert manifest["tasks"] == [[list(macro), start, stop] for macro, start, stop in TASKS]
    assert manifest["expected_orbits"] == {f"{m[0]}:{m[1]}": v[0] for m, v in EXPECTED.items()}
    task_by_key = {f"{m[0]}:{m[1]}:{s}:{t}": (m, s, t) for m, s, t in TASKS}
    assert set(manifest["shards"]) <= set(task_by_key)
    records = foundation.independently_reconstruct_records()
    for macro, (count, mass, q) in EXPECTED.items():
        assert len(records[macro]) == count
        assert sum(int(r["orbit_size"]) for r in records[macro]) == mass
        assert {int(r["Q"]) for r in records[macro]} == {q}
    base_inputs = (foundation.LOCAL, foundation.CATALOG, foundation.GRAM,
                   foundation.FIBRE_FILTER, foundation.CONFIG_FRONTIER)
    base_hashes = {str(path): foundation.sha256(path) for path in base_inputs}
    seen = {m: set() for m in EXPECTED}
    hist = {m: Counter() for m in EXPECTED}
    masses = {m: Counter() for m in EXPECTED}
    audited_shards = []
    failed_shards = []
    for key, checkpoint in manifest["shards"].items():
        macro, start, stop = task_by_key[key]
        if checkpoint["status"] != "COMPLETE":
            failed_shards.append({"task": key, "checkpoint": checkpoint})
            continue
        path = Path(f"scratch_theory_e72_source150_sync_jointprimary_small5_m{macro[0]}{macro[1]}_r{start}_{stop}.json")
        assert checkpoint["path"] == str(path)
        assert checkpoint["sha256"] == foundation.sha256(path)
        document = foundation.load(path)
        assert document["inputs"] == base_hashes
        assert document["status"] == "EXACT_SYNCHRONIZED_CONFIG_CSP_SLICE_COMPLETE"
        summary = document["summary"]
        assert summary["wanted_macros"] == [list(macro)]
        assert summary["available_orbits_in_wanted_macros"] == EXPECTED[macro][0]
        assert summary["slice_start"] == start and summary["slice_stop"] == stop
        assert summary["explicit_record_selection"] == []
        assert summary["input_orbits"] == stop - start
        assert summary["fixed_block_projection"] == []
        for flag in ("ordinary_local_pair_filter_enabled", "ordinary_local_pair_every_depth_enabled", "ordinary_joint_map_filter_enabled"):
            assert summary[flag] is True
        assert summary["ordinary_joint_map_unknowns_relaxed_as_pass"] == 0
        assert [int(row[0]) for row in document["results"]] == list(range(start, stop))
        shard_hist, shard_mass = Counter(), Counter()
        for row in document["results"]:
            number, representative = foundation.verify_result(row, macro, records)
            assert number not in seen[macro]
            seen[macro].add(number)
            status, mass = str(row[5]), int(representative["orbit_size"])
            hist[macro][status] += 1
            masses[macro][status] += mass
            shard_hist[status] += 1
            shard_mass[status] += mass
        assert dict(shard_hist) == summary["status_histogram"] == checkpoint["status_histogram"]
        assert sum(shard_mass.values()) == summary["input_mass"] == checkpoint["input_mass"]
        for status in ("SAT", "UNSAT", "UNKNOWN"):
            assert shard_mass[status] == summary[f"{status}_mass"] == checkpoint[f"{status}_mass"]
        audited_shards.append({
            "task": key, "path": str(path), "sha256": checkpoint["sha256"],
            "records": stop - start, "status_histogram": dict(shard_hist),
            "status_mass": dict(shard_mass), "elapsed_seconds": summary["elapsed_seconds"],
        })
    per_macro = []
    for macro, (count, mass, q) in EXPECTED.items():
        full = seen[macro] == set(range(count))
        eligible = full and hist[macro]["UNSAT"] == count and masses[macro]["UNSAT"] == mass
        per_macro.append({
            "macro": list(macro), "Q": q, "expected_records": count,
            "expected_mass": mass, "audited_records": len(seen[macro]),
            "missing_records": sorted(set(range(count)) - seen[macro]),
            "status_histogram": dict(hist[macro]), "status_mass": dict(masses[macro]),
            "all_records_audited": full, "macro_exclusion_eligible": eligible,
        })
    result = {
        "status": "SOURCE150_SMALL5_PARTIAL_CHECKPOINT_AUDIT_PASS",
        "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest().upper(),
        "producer_status": manifest["status"],
        "producer_status_is_not_liveness_evidence": True,
        "solver_sha256": foundation.sha256(SOLVER), "input_sha256": base_hashes,
        "solver_or_runner_imported": False, "expected_shards": len(TASKS),
        "audited_shards": len(audited_shards), "failed_shards": failed_shards,
        "audited_records": sum(len(s) for s in seen.values()),
        "audited_UNSAT_mass": sum(c["UNSAT"] for c in masses.values()),
        "macro_exclusion_eligible_mass": sum(r["expected_mass"] for r in per_macro if r["macro_exclusion_eligible"]),
        "all_five_macros_excluded": all(r["macro_exclusion_eligible"] for r in per_macro),
        "per_macro": per_macro, "shards": audited_shards,
        "claim_boundary": "Checkpoint audit only. A partial macro remains open in the central macro inventory. UNSAT status is hash-bound finite-CSP evidence, not a DRAT certificate.",
        "audit_elapsed_seconds": time.monotonic() - started,
    }
    result["complete_macro_certificates"] = [
        certificate for row in per_macro
        if (certificate := freeze_closed_macro(row, records, audited_shards, base_hashes)) is not None
    ]
    foundation.atomic_json(OUTPUT, result)
    print(json.dumps({k: result[k] for k in ("status", "audited_shards", "audited_records", "audited_UNSAT_mass", "macro_exclusion_eligible_mass", "all_five_macros_excluded", "audit_elapsed_seconds")}, separators=(",", ":")))


if __name__ == "__main__":
    main()
