"""Audit resumed small5 increments without losing older completed checkpoints.

Only the independent auditor is imported. Frozen producer/solver/runner code
and the live runner manifest are not modified. Its usual independent catalog,
input SHA256, result-row, mode, and complete-macro checks all run unchanged.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import scratch_root_e72_source150_small5_joint_primary_partial_audit as audit


STOPPED = Path("scratch_root_e72_stopped_20260905_1131_small5_manifest.raw.json")
STOPPED_SHA256 = "96F078C8096630187A5523394E96C9BBEF8D9F60937E1F119842C7A9F5D44E65"
LIVE = Path("scratch_root_e72_source150_small5_joint_primary_manifest.json")
UNION = Path("scratch_resume_e72_small5_union_manifest.json")


def sha(data):
    return hashlib.sha256(data).hexdigest().upper()


def main():
    stopped_bytes = STOPPED.read_bytes()
    live_bytes = LIVE.read_bytes()
    assert sha(stopped_bytes) == STOPPED_SHA256
    stopped, live = json.loads(stopped_bytes), json.loads(live_bytes)
    for key in ("macros", "expected_orbits", "solver", "solver_sha256",
                "ordinary_local_pair", "ordinary_local_pair_every_depth",
                "ordinary_joint_map", "node_cap", "joint_map_node_cap",
                "projection", "shard_size", "tasks"):
        assert stopped[key] == live[key], key
    assert live["jobs"] == 1
    union = copy.deepcopy(live)
    union["shards"] = copy.deepcopy(stopped["shards"])
    for key, row in live["shards"].items():
        previous = union["shards"].get(key)
        if previous is not None and previous["status"] == "COMPLETE":
            assert row["status"] == "COMPLETE", (key, row)
            assert previous["sha256"] == row["sha256"], key
            # Keep the original complete checkpoint. All mathematical fields
            # will be rechecked against its file by the independent auditor.
        else:
            union["shards"][key] = copy.deepcopy(row)
    union["resume_union_provenance"] = {
        "stopped_manifest": str(STOPPED), "stopped_manifest_sha256": sha(stopped_bytes),
        "live_manifest": str(LIVE), "live_manifest_snapshot_sha256": sha(live_bytes),
        "purpose": "Monotone union of completed checkpoints across a sequential restart.",
        "producer_or_runner_imported": False,
        "does_not_modify_live_manifest": True,
    }
    audit.foundation.atomic_json(UNION, union)
    audit.MANIFEST = UNION
    audit.main()


if __name__ == "__main__":
    main()
