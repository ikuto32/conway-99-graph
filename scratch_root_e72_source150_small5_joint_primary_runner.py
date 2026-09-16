"""Checkpointed exact joint-map primary sweep for five source150 macros."""

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
MANIFEST = Path("scratch_root_e72_source150_small5_joint_primary_manifest.json")
EXPECTED = {
    (1, 0): 96,
    (3, 3): 116,
    (9, 0): 52,
    (10, 0): 63,
    (11, 0): 73,
}
SHARD_SIZE = 8
TASKS = tuple(
    (macro, start, min(start + SHARD_SIZE, count))
    for macro, count in EXPECTED.items()
    for start in range(0, count, SHARD_SIZE)
)


def macro_tag(macro: tuple[int, int]) -> str:
    return f"m{macro[0]}{macro[1]}"


def output_path(macro: tuple[int, int], start: int, stop: int) -> Path:
    return Path(
        "scratch_theory_e72_source150_sync_jointprimary_small5_"
        f"{macro_tag(macro)}_r{start}_{stop}.json"
    )


def task_key(macro: tuple[int, int], start: int, stop: int) -> str:
    return f"{macro[0]}:{macro[1]}:{start}:{stop}"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def atomic_json(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def validate(path: Path, macro: tuple[int, int], start: int, stop: int):
    document = json.loads(path.read_text(encoding="utf-8"))
    assert document["status"] == "EXACT_SYNCHRONIZED_CONFIG_CSP_SLICE_COMPLETE"
    summary = document["summary"]
    assert summary["wanted_macros"] == [list(macro)]
    assert summary["available_orbits_in_wanted_macros"] == EXPECTED[macro]
    assert summary["slice_start"] == start
    assert summary["slice_stop"] == stop
    assert summary["explicit_record_selection"] == []
    assert summary["input_orbits"] == stop - start
    assert summary["ordinary_local_pair_filter_enabled"] is True
    assert summary["ordinary_local_pair_every_depth_enabled"] is True
    assert summary["ordinary_joint_map_filter_enabled"] is True
    assert summary["ordinary_joint_map_unknowns_relaxed_as_pass"] == 0
    assert summary["fixed_block_projection"] == []
    record_numbers = [int(row[0]) for row in document["results"]]
    assert record_numbers == list(range(start, stop))
    assert len(record_numbers) == len(set(record_numbers))
    return {
        "status": "COMPLETE",
        "macro": list(macro),
        "path": str(path),
        "sha256": sha256(path),
        "records": len(record_numbers),
        "input_mass": int(summary["input_mass"]),
        "status_histogram": summary["status_histogram"],
        "SAT_mass": int(summary["SAT_mass"]),
        "UNSAT_mass": int(summary["UNSAT_mass"]),
        "UNKNOWN_mass": int(summary["UNKNOWN_mass"]),
        "maximum_DFS_nodes": int(summary["maximum_DFS_nodes"]),
        "solver_elapsed_seconds": float(summary["elapsed_seconds"]),
        "ordinary_joint_map_calls": int(summary["ordinary_joint_map_calls"]),
        "ordinary_joint_map_nodes": int(summary["ordinary_joint_map_nodes"]),
    }


def run_one(macro: tuple[int, int], start: int, stop: int):
    path = output_path(macro, start, stop)
    if path.exists():
        return macro, start, stop, validate(path, macro, start, stop), "validated_existing"
    command = [
        sys.executable,
        str(SOLVER),
        "--macros", f"{macro[0]}:{macro[1]}",
        "--start", str(start),
        "--stop", str(stop),
        "--ordinary-local-pair",
        "--ordinary-local-pair-every-depth",
        "--ordinary-joint-map",
        "--output", str(path),
    ]
    started = time.monotonic()
    completed = subprocess.run(
        command, text=True, capture_output=True, check=False
    )
    wall_seconds = time.monotonic() - started
    if completed.returncode != 0:
        return macro, start, stop, {
            "status": "FAILED",
            "macro": list(macro),
            "path": str(path),
            "returncode": completed.returncode,
            "wall_seconds": wall_seconds,
            "stdout_tail": completed.stdout[-4000:],
            "stderr_tail": completed.stderr[-4000:],
        }, "executed"
    record = validate(path, macro, start, stop)
    record.update({
        "returncode": completed.returncode,
        "wall_seconds": wall_seconds,
        "stdout_tail": completed.stdout[-4000:],
        "stderr_tail": completed.stderr[-4000:],
    })
    return macro, start, stop, record, "executed"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--jobs", type=int, default=8)
    arguments = parser.parse_args()
    assert 1 <= arguments.jobs <= len(TASKS)
    manifest = {
        "status": "RUNNING",
        "macros": [list(macro) for macro in EXPECTED],
        "expected_orbits": {
            f"{macro[0]}:{macro[1]}": count
            for macro, count in EXPECTED.items()
        },
        "solver": str(SOLVER),
        "solver_sha256": sha256(SOLVER),
        "ordinary_local_pair": True,
        "ordinary_local_pair_every_depth": True,
        "ordinary_joint_map": True,
        "node_cap": 0,
        "joint_map_node_cap": 0,
        "projection": [],
        "shard_size": SHARD_SIZE,
        "tasks": [[list(macro), start, stop] for macro, start, stop in TASKS],
        "jobs": arguments.jobs,
        "started_unix": time.time(),
        "shards": {},
    }
    atomic_json(MANIFEST, manifest)
    failure = False
    with concurrent.futures.ThreadPoolExecutor(max_workers=arguments.jobs) as pool:
        futures = {
            pool.submit(run_one, macro, start, stop): (macro, start, stop)
            for macro, start, stop in TASKS
        }
        for future in concurrent.futures.as_completed(futures):
            macro, start, stop = futures[future]
            try:
                got_macro, got_start, got_stop, record, mode = future.result()
                assert (got_macro, got_start, got_stop) == (macro, start, stop)
            except Exception as error:
                record = {
                    "status": "FAILED",
                    "macro": list(macro),
                    "path": str(output_path(macro, start, stop)),
                    "exception": repr(error),
                }
                mode = "runner_exception"
            record["mode"] = mode
            manifest["shards"][task_key(macro, start, stop)] = record
            failure |= record["status"] != "COMPLETE"
            atomic_json(MANIFEST, manifest)
            print(json.dumps({
                "macro": list(macro), "range": [start, stop], **record
            }, separators=(",", ":")))
    manifest["finished_unix"] = time.time()
    manifest["wall_seconds"] = manifest["finished_unix"] - manifest["started_unix"]
    manifest["status"] = "FAILED" if failure else "COMPLETE"
    atomic_json(MANIFEST, manifest)
    if failure:
        raise SystemExit(1)
    print(json.dumps({
        "status": manifest["status"],
        "macros": [list(macro) for macro in EXPECTED],
        "shards": len(TASKS),
        "manifest": str(MANIFEST),
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
