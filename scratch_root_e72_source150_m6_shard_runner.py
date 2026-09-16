"""Checkpointed runner for the complete source150 macro (6,0) CSP sweep."""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


SOLVER = Path("scratch_theory_e72_source150_synchronized_config_csp.py")
MANIFEST = Path("scratch_root_e72_source150_m6_shard_run_manifest.json")
MACRO = (6, 0)
SHARDS = (
    (0, 128),
    (128, 256),
    (256, 384),
    (384, 512),
    (512, 640),
    (640, 704),
)


def output_path(start: int, stop: int) -> Path:
    return Path(
        f"scratch_theory_e72_source150_sync_localpair_m60_r{start}_{stop}.json"
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def atomic_json(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def validate(path: Path, start: int, stop: int) -> dict[str, object]:
    document = json.loads(path.read_text(encoding="utf-8"))
    assert document["status"] == "EXACT_SYNCHRONIZED_CONFIG_CSP_SLICE_COMPLETE"
    summary = document["summary"]
    assert summary["wanted_macros"] == [list(MACRO)]
    assert int(summary["available_orbits_in_wanted_macros"]) == 704
    assert int(summary["slice_start"]) == start
    assert int(summary["slice_stop"]) == stop
    assert int(summary["input_orbits"]) == stop - start
    assert summary["ordinary_local_pair_filter_enabled"] is True
    assert summary["ordinary_local_pair_every_depth_enabled"] is False
    assert summary["fixed_block_projection"] == []
    records = [int(row[0]) for row in document["results"]]
    assert records == list(range(start, stop))
    assert len(records) == len(set(records))
    return {
        "status": "COMPLETE",
        "path": str(path),
        "sha256": sha256(path),
        "records": len(records),
        "input_mass": int(summary["input_mass"]),
        "status_histogram": summary["status_histogram"],
        "SAT_mass": int(summary["SAT_mass"]),
        "UNSAT_mass": int(summary["UNSAT_mass"]),
        "UNKNOWN_mass": int(summary["UNKNOWN_mass"]),
        "maximum_DFS_nodes": int(summary["maximum_DFS_nodes"]),
        "solver_elapsed_seconds": float(summary["elapsed_seconds"]),
    }


def run_one(start: int, stop: int):
    path = output_path(start, stop)
    if path.exists():
        return start, stop, validate(path, start, stop), "validated_existing"
    command = [
        sys.executable,
        str(SOLVER),
        "--macros", "6:0",
        "--start", str(start),
        "--stop", str(stop),
        "--ordinary-local-pair",
        "--output", str(path),
    ]
    started = time.monotonic()
    completed = subprocess.run(
        command, text=True, capture_output=True, check=False
    )
    elapsed = time.monotonic() - started
    if completed.returncode != 0:
        return start, stop, {
            "status": "FAILED",
            "path": str(path),
            "returncode": completed.returncode,
            "wall_seconds": elapsed,
            "stdout_tail": completed.stdout[-4000:],
            "stderr_tail": completed.stderr[-4000:],
        }, "executed"
    record = validate(path, start, stop)
    record.update({
        "returncode": completed.returncode,
        "wall_seconds": elapsed,
        "stdout_tail": completed.stdout[-4000:],
        "stderr_tail": completed.stderr[-4000:],
    })
    return start, stop, record, "executed"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--jobs", type=int, default=3)
    arguments = parser.parse_args()
    assert 1 <= arguments.jobs <= len(SHARDS)
    manifest = {
        "status": "RUNNING",
        "macro": list(MACRO),
        "solver": str(SOLVER),
        "solver_sha256": sha256(SOLVER),
        "ordinary_local_pair": True,
        "node_cap": 0,
        "shard_ranges": [list(shard) for shard in SHARDS],
        "jobs": arguments.jobs,
        "started_unix": time.time(),
        "shards": {},
    }
    atomic_json(MANIFEST, manifest)
    failure = False
    with concurrent.futures.ThreadPoolExecutor(max_workers=arguments.jobs) as pool:
        futures = {
            pool.submit(run_one, start, stop): (start, stop)
            for start, stop in SHARDS
        }
        for future in concurrent.futures.as_completed(futures):
            start, stop = futures[future]
            try:
                got_start, got_stop, record, mode = future.result()
                assert (got_start, got_stop) == (start, stop)
            except Exception as error:  # retained in checkpoint; then fail hard
                record = {
                    "status": "FAILED",
                    "path": str(output_path(start, stop)),
                    "exception": repr(error),
                }
                mode = "runner_exception"
            record["mode"] = mode
            manifest["shards"][f"{start}:{stop}"] = record
            failure |= record["status"] != "COMPLETE"
            atomic_json(MANIFEST, manifest)
            print(json.dumps({"range": [start, stop], **record}, separators=(",", ":")))
    manifest["finished_unix"] = time.time()
    manifest["wall_seconds"] = manifest["finished_unix"] - manifest["started_unix"]
    manifest["status"] = "FAILED" if failure else "COMPLETE"
    atomic_json(MANIFEST, manifest)
    if failure:
        raise SystemExit(1)
    print(json.dumps({
        "status": manifest["status"],
        "macro": list(MACRO),
        "shards": len(SHARDS),
        "manifest": str(MANIFEST),
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
