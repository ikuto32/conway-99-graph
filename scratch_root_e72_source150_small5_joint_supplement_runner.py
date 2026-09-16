"""Run exact synchronized ordinary-map supplements for direct SAT rows only."""

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

import scratch_root_e72_source150_small5_shard_runner as direct


SOLVER = direct.SOLVER
DIRECT_MANIFEST = direct.MANIFEST
MANIFEST = Path("scratch_root_e72_source150_small5_joint_supplement_manifest.json")


def output_path(macro: tuple[int, int]) -> Path:
    return Path(
        "scratch_theory_e72_source150_sync_jointmap_small5_"
        f"{direct.macro_tag(macro)}_localSAT.json"
    )


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def atomic_json(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def direct_sat_records():
    manifest = json.loads(DIRECT_MANIFEST.read_text(encoding="utf-8"))
    assert manifest["status"] == "COMPLETE"
    assert manifest["solver_sha256"] == sha256(SOLVER)
    records = {macro: [] for macro in direct.EXPECTED}
    unknown = []
    for macro, start, stop in direct.TASKS:
        path = direct.output_path(macro, start, stop)
        checkpoint = manifest["shards"][direct.task_key(macro, start, stop)]
        assert checkpoint["sha256"] == sha256(path)
        document = json.loads(path.read_text(encoding="utf-8"))
        for result in document["results"]:
            if result[5] == "SAT":
                records[macro].append(int(result[0]))
            elif result[5] == "UNKNOWN":
                unknown.append((macro, int(result[0])))
            else:
                assert result[5] == "UNSAT"
    assert not unknown, f"direct UNKNOWN records cannot be supplemented: {unknown}"
    return {macro: tuple(sorted(values)) for macro, values in records.items()}


def validate(path: Path, macro: tuple[int, int], records: tuple[int, ...]):
    document = json.loads(path.read_text(encoding="utf-8"))
    assert document["status"] == "EXACT_SYNCHRONIZED_CONFIG_CSP_SLICE_COMPLETE"
    summary = document["summary"]
    assert summary["wanted_macros"] == [list(macro)]
    assert summary["available_orbits_in_wanted_macros"] == direct.EXPECTED[macro]
    assert summary["explicit_record_selection"] == list(records)
    assert summary["input_orbits"] == len(records)
    assert summary["ordinary_joint_map_filter_enabled"] is True
    assert summary["ordinary_joint_map_unknowns_relaxed_as_pass"] == 0
    assert summary["fixed_block_projection"] == []
    assert [int(row[0]) for row in document["results"]] == list(records)
    return {
        "status": "COMPLETE",
        "path": str(path),
        "sha256": sha256(path),
        "records": list(records),
        "input_mass": int(summary["input_mass"]),
        "status_histogram": summary["status_histogram"],
        "SAT_mass": int(summary["SAT_mass"]),
        "UNSAT_mass": int(summary["UNSAT_mass"]),
        "UNKNOWN_mass": int(summary["UNKNOWN_mass"]),
        "maximum_DFS_nodes": int(summary["maximum_DFS_nodes"]),
        "solver_elapsed_seconds": float(summary["elapsed_seconds"]),
    }


def run_one(macro: tuple[int, int], records: tuple[int, ...]):
    if not records:
        return macro, {
            "status": "NO_DIRECT_SAT_INPUT",
            "records": [],
            "input_mass": 0,
            "status_histogram": {},
            "SAT_mass": 0,
            "UNSAT_mass": 0,
            "UNKNOWN_mass": 0,
        }, "not_needed"
    path = output_path(macro)
    if path.exists():
        return macro, validate(path, macro, records), "validated_existing"
    command = [
        sys.executable,
        str(SOLVER),
        "--macros", f"{macro[0]}:{macro[1]}",
        "--records", ",".join(map(str, records)),
        "--ordinary-joint-map",
        "--output", str(path),
    ]
    started = time.monotonic()
    completed = subprocess.run(
        command, text=True, capture_output=True, check=False
    )
    wall_seconds = time.monotonic() - started
    if completed.returncode != 0:
        return macro, {
            "status": "FAILED",
            "path": str(path),
            "records": list(records),
            "returncode": completed.returncode,
            "wall_seconds": wall_seconds,
            "stdout_tail": completed.stdout[-4000:],
            "stderr_tail": completed.stderr[-4000:],
        }, "executed"
    result = validate(path, macro, records)
    result.update({
        "returncode": completed.returncode,
        "wall_seconds": wall_seconds,
        "stdout_tail": completed.stdout[-4000:],
        "stderr_tail": completed.stderr[-4000:],
    })
    return macro, result, "executed"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--jobs", type=int, default=3)
    arguments = parser.parse_args()
    assert 1 <= arguments.jobs <= len(direct.EXPECTED)
    sat_records = direct_sat_records()
    manifest = {
        "status": "RUNNING",
        "solver": str(SOLVER),
        "solver_sha256": sha256(SOLVER),
        "direct_manifest": str(DIRECT_MANIFEST),
        "direct_manifest_sha256": sha256(DIRECT_MANIFEST),
        "ordinary_joint_map": True,
        "node_cap": 0,
        "projection": [],
        "direct_sat_records": {
            f"{macro[0]}:{macro[1]}": list(records)
            for macro, records in sat_records.items()
        },
        "jobs": arguments.jobs,
        "started_unix": time.time(),
        "macros": {},
    }
    atomic_json(MANIFEST, manifest)
    failure = False
    with concurrent.futures.ThreadPoolExecutor(max_workers=arguments.jobs) as pool:
        futures = {
            pool.submit(run_one, macro, records): macro
            for macro, records in sat_records.items()
        }
        for future in concurrent.futures.as_completed(futures):
            macro = futures[future]
            try:
                got_macro, record, mode = future.result()
                assert got_macro == macro
            except Exception as error:
                record = {"status": "FAILED", "exception": repr(error)}
                mode = "runner_exception"
            record["mode"] = mode
            key = f"{macro[0]}:{macro[1]}"
            manifest["macros"][key] = record
            failure |= record["status"] == "FAILED"
            atomic_json(MANIFEST, manifest)
            print(json.dumps({
                "macro": list(macro), **record
            }, separators=(",", ":")))
    manifest["finished_unix"] = time.time()
    manifest["wall_seconds"] = manifest["finished_unix"] - manifest["started_unix"]
    manifest["status"] = "FAILED" if failure else "COMPLETE"
    atomic_json(MANIFEST, manifest)
    if failure:
        raise SystemExit(1)
    print(json.dumps({
        "status": manifest["status"],
        "manifest": str(MANIFEST),
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
