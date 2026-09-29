"""Frozen four-branch materialization and gated two-at-a-time native runner."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
import json
import platform
import shutil
import subprocess
import sys
import time

import native_20260930_unrestricted_full99 as base
import native_20260930_proof_location as ext4

ROOT = base.ROOT
SPEC = Path(__file__).with_name("native_20260930_four_branch_ext4_spec.md")
RECIPE = ROOT / "acceleration/results/20260930_unrestricted_four_branches/branches.json"
BYTE_CHECKER = ROOT / "acceleration/audit_20260930_four_branch_cnf_bytes_v1.py"
GATES = [
    ("acceleration/results/20260930_native_cli_calibration/summary.json", "f5ff562aff2ec550a97685c7012b302e760314a6f3829d80d022e2a669e680eb", "INDEPENDENT_NATIVE_CADICAL195_CLI_CALIBRATION_PASS"),
    ("acceleration/results/20260930_native_proof_location/summary.json", "d1036cfcbe9b24e0f7ea6e0a3799968a5d9232e8167fb31b224211e5c845c619", "NATIVE_EXT4_PROOF_PATH_CALIBRATION_PASS"),
    ("acceleration/results/20260930_independent_review/unrestricted_full99_cnf/summary.json", "2d6702d0f60341378fcf6b5b0808e6c34ea6a1025775cfae60500626f199ef58", "INDEPENDENT_UNRESTRICTED_FULL99_CNF_ENCODING_PASS"),
    ("acceleration/results/20260930_independent_review/unrestricted_full99_sat_object_calibration/summary.json", "1ae229a3a6a3d7dcf9cbc3c1c9a9a924facb2d5c343bbd683f838e27c8362a4f", "INDEPENDENT_UNRESTRICTED_FULL99_SAT_OBJECT_CHECKER_CALIBRATION_PASS"),
    ("acceleration/results/20260930_independent_review/unrestricted_four_branch_cover/summary.json", "ae44765cab81327f050b27d3ab75e6b952f44d5387a054a38029516e71516d34", "INDEPENDENT_UNRESTRICTED_FOUR_BRANCH_COVER_PASS"),
    ("acceleration/results/20260930_independent_review/four_branch_cnf_bytes_calibration/summary.json", "a0e543b28b27795568c1061c020d5db6385113cff97c397eadf260296042a824", "INDEPENDENT_FOUR_BRANCH_CNF_BYTES_CALIBRATION_PASS"),
]


def bindings():
    result = base.provenance()
    for path, expected, status in GATES:
        base.checked_gate(ROOT / path, expected, status)
        result[path] = expected
    for path in (Path(__file__), SPEC, Path(ext4.__file__), ext4.SPEC, RECIPE, BYTE_CHECKER):
        result[base.key(path)] = base.digest(path)
    base.require(result[base.key(BYTE_CHECKER)] == "b0e84ac2894b9ca10e0af63086131bb2abe61e52ed9222fd54c42bea76156388", "byte checker frozen source")
    return result


def byte_gate(cnf, row, folder):
    report = folder / "independent_cnf_bytes.json"
    coverage_path, coverage_hash, _ = GATES[4]
    command = [sys.executable, BYTE_CHECKER, "--base", base.CNF, "--branch-cnf", cnf,
        "--branch", row["branch"], "--recipe", RECIPE, "--coverage-gate", ROOT / coverage_path,
        "--coverage-gate-sha256", coverage_hash, "--out", report]
    receipt = base.run_record(command, folder / "byte_checker", 60)
    base.require(receipt["actual_exit_code"] == 0, "independent actual-byte gate failed")
    gate = base.checked_gate(report, base.digest(report), "INDEPENDENT_FOUR_BRANCH_CNF_BYTES_PASS")
    base.require(gate["branch_cnf_sha256"] == row["cnf_sha256"] and gate["units"] == row["units"], "branch gate mismatch")
    return {"path": base.key(report), "sha256": base.digest(report), "receipt": receipt}


def materialize(out, records):
    result = []
    for row in records:
        folder = out / row["branch"]
        folder.mkdir()
        cnf = folder / "instance.cnf"
        suffix = base.resolve(row["suffix"])
        base.require(base.digest(suffix) == row["suffix_sha256"], "suffix changed")
        with cnf.open("xb") as destination, base.CNF.open("rb") as source:
            base.require(source.readline() == b"p cnf 1186500 4136454\n", "base header")
            destination.write(b"p cnf 1186500 4136458\n")
            shutil.copyfileobj(source, destination, 1048576)
            destination.write(suffix.read_bytes())
        base.require(base.digest(cnf) == row["cnf_sha256"], "materialized recipe hash")
        checked = byte_gate(cnf, row, folder)
        result.append({"branch": row["branch"], "cnf": base.key(cnf), "cnf_sha256": row["cnf_sha256"],
                       "units": row["units"], "independent_byte_gate": checked})
    return result


def prepared_records(path, records):
    summary = base.read(path)
    base.require(summary["status"] == "FOUR_BRANCH_NATIVE_PREPARATION_PASS", "preparation not passed")
    expected = {row["branch"]: row for row in records}
    base.require([row["branch"] for row in summary["branches"]] == list(expected), "four branches ordered exactly")
    for item in summary["branches"]:
        row = expected[item["branch"]]
        base.require(base.digest(base.resolve(item["cnf"])) == item["cnf_sha256"] == row["cnf_sha256"], "prepared input changed")
        gate = item["independent_byte_gate"]
        base.checked_gate(base.resolve(gate["path"]), gate["sha256"], "INDEPENDENT_FOUR_BRANCH_CNF_BYTES_PASS")
    return summary["branches"]


def solve_one(row, item, out, linux_dir):
    folder = out / row["branch"]
    folder.mkdir()
    cnf = base.resolve(item["cnf"])
    gate = byte_gate(cnf, row, folder)
    # The independent byte gate is freshly replayed before every native call.
    proof_linux = linux_dir + "/" + row["branch"] + ".drat"
    proof = folder / "proof.drat"
    command = ext4.command(300, [base.linux(base.NATIVE), "--no-binary", "-c", "1000000", base.linux(cnf), proof_linux])
    base.save(folder / "launch.json", {"timestamp": datetime.now(timezone.utc).isoformat(), "branch": row["branch"],
        "command": command, "independent_byte_gate": gate, "cnf_sha256": row["cnf_sha256"],
        "ext4_proof": proof_linux, "cwd": str(ROOT), "native_memory_bytes": ext4.AS_LIMIT,
        "proof_file_bytes_cap": ext4.FILE_LIMIT, "native_timeout_seconds": 300, "conflict_limit": 1000000})
    print(json.dumps({"state": "BRANCH_NATIVE_LAUNCHING", "branch": row["branch"]}), flush=True)
    receipt = base.run_record(command, folder / "solver", 320)
    result = {"branch": row["branch"], "native_receipt": receipt, "independent_byte_gate": gate,
              "actual_exit_code": receipt["actual_exit_code"], "raw_sat_status": False,
              "independently_verified_target_resolution": False}
    if receipt["outer_windows_guard_expired"]:
        result["status"] = "UNKNOWN_LINUX_PROCESS_STATE_AFTER_OUTER_GUARD"
        base.save(folder / "summary.json", result)
        return result
    try:
        result["proof_copy"] = ext4.proof_copy(proof_linux, proof, folder / "transfer")
        base.require(proof.stat().st_size <= ext4.FILE_LIMIT, "proof exceeded native file cap")
    except BaseException as error:
        result["proof_copy_failure"] = {"type": type(error).__name__, "message": str(error), "ext4_original_retained": proof_linux}
    raw = (folder / "solver.stdout.log").read_text()
    result["raw_sat_status"] = any(line.strip() == "s SATISFIABLE" for line in raw.splitlines())
    if result["raw_sat_status"]:
        try:
            assignment = base.parse_sat_stdout(raw, 1186500)
            base.save(folder / "parsed_model.json", {"assignment": assignment})
            decoded = base.decode_and_check(assignment)
            decoded["status"] = "CANDIDATE_PENDING_INDEPENDENT_TARGET_CHECK"
            base.save(folder / "decoded_full99.json", decoded)
            values = set(assignment)
            result["producer_branch_units_satisfied"] = all(lit in values for lit in row["units"])
            result["producer_target_check"] = decoded["producer_exact_validation"]
        except BaseException as error:
            result["decode_failure"] = {"type": type(error).__name__, "message": str(error)}
    code = receipt["actual_exit_code"]
    result["status"] = "SAT_CANDIDATE_PENDING_INDEPENDENT_CHECK" if code == 10 else "UNSAT_TRACE_PENDING_INDEPENDENT_REPLAY" if code == 20 else "UNKNOWN_NATIVE_OR_RESOURCE_OUTCOME"
    result["outputs_sha256"] = {base.key(p): base.digest(p) for p in folder.iterdir() if p.is_file()}
    base.save(folder / "summary.json", result)
    print(json.dumps({"state": "BRANCH_NATIVE_RETURNED", "branch": row["branch"], "actual_exit_code": code,
                      "proof_bytes": proof.stat().st_size if proof.exists() else None}), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    for mode in ("prepare", "preflight", "research"):
        group.add_argument("--" + mode, action="store_true")
    parser.add_argument("--prepared", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    pins = bindings()
    records = base.read(RECIPE)["branches"]
    base.require([x["branch"] for x in records] == ["a0", "a1_complement", "a1_cross", "a2_crosses"], "exact branch order")
    items = None if args.prepare else prepared_records(args.prepared, records)
    if args.prepared is not None:
        pins[base.key(args.prepared)] = base.digest(args.prepared)
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    base.save(out / "manifest.json", {"timestamp": datetime.now(timezone.utc).isoformat(),
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "command": [sys.executable, *sys.argv], "cwd": str(ROOT), "python": platform.python_version(),
        "inputs_sha256": pins, "mode": "PREPARE" if args.prepare else "PREFLIGHT" if args.preflight else "RESEARCH",
        "branch_order": [r["branch"] for r in records], "maximum_research_calls": 4 if args.research else 0,
        "concurrency": 2, "native_seconds_each": 300, "conflicts_each": 1000000,
        "native_address_space_each": ext4.AS_LIMIT, "file_bytes_each": ext4.FILE_LIMIT,
        "random_seed": None, "random_seed_null_reason": "Native default retained",
        "limitations": ["Root controls launch; preparation and preflight do not solve research CNFs.",
            "No equality strengthening added; exact four original branch recipes only."]})
    if args.prepare:
        items = materialize(out, records)
        base.save(out / "summary.json", {"status": "FOUR_BRANCH_NATIVE_PREPARATION_PASS", "branches": items,
            "research_calls": 0, "inputs_sha256": pins})
        print(json.dumps({"status": "FOUR_BRANCH_NATIVE_PREPARATION_PASS", "research_calls": 0,
                          "summary_sha256": base.digest(out / "summary.json")}), flush=True)
        return
    if args.preflight:
        base.save(out / "summary.json", {"status": "FOUR_BRANCH_NATIVE_PREFLIGHT_PASS", "research_calls": 0,
                                        "branches": items, "all_gates_checked": True})
        print(json.dumps({"status": "FOUR_BRANCH_NATIVE_PREFLIGHT_PASS", "research_calls": 0}), flush=True)
        return
    base.require(shutil.disk_usage(ROOT).free >= 81 * 1024 ** 3, "Windows free space below conservative81GiB")
    made, linux_dir = ext4.local_capture(["/usr/bin/mktemp", "-d", "/tmp/conway99-four-branch-XXXXXX"], out / "mktemp")
    base.require(linux_dir.startswith("/tmp/conway99-four-branch-") and "\n" not in linux_dir, "unexpected ext4 path")
    mount, mount_text = ext4.local_capture(["/usr/bin/findmnt", "--target", linux_dir, "--output", "TARGET,SOURCE,FSTYPE,OPTIONS", "--noheadings"], out / "filesystem")
    base.require("ext4" in mount_text.split(), "ext4 proof location required")
    free_receipt, free_text = ext4.local_capture(["/usr/bin/df", "--output=avail", "-B1", linux_dir], out / "disk_free")
    base.require(int(free_text.splitlines()[-1]) >= 41 * 1024 ** 3, "ext4 free space below41GiB")
    base.save(out / "workspace.json", {"path": linux_dir, "preserved": True, "mktemp": made, "mount": mount, "disk": free_receipt})
    results = []
    for offset in (0, 2):
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [(row["branch"], executor.submit(solve_one, row, item, out, linux_dir))
                       for row, item in zip(records[offset:offset+2], items[offset:offset+2])]
            for name, future in futures:
                try:
                    result = future.result()
                except BaseException as error:
                    result = {"branch": name, "status": "WORKER_ERROR_REVIEW_RAW_RECEIPTS", "type": type(error).__name__, "message": str(error)}
                    base.save(out / (name + "_worker_failure.json"), result)
                results.append(result)
        if any(r.get("raw_sat_status") or r.get("native_receipt", {}).get("outer_windows_guard_expired")
               or r["status"] == "WORKER_ERROR_REVIEW_RAW_RECEIPTS" or "proof_copy_failure" in r for r in results):
            for row in records[offset+2:]:
                results.append({"branch": row["branch"], "status": "SKIPPED_PENDING_FIRST_BATCH_REVIEW"})
            break
    base.save(out / "summary.json", {"status": "FOUR_BRANCH_NATIVE_RESULTS_PENDING_INDEPENDENT_REVIEW", "branches": results,
        "attempted_solver_calls": sum((out / r["branch"] / "launch.json").exists() for r in records),
        "independently_verified_target_resolution": False, "automatic_retry": False,
        "limitations": ["Unknown/limited calls do not exclude a branch.", "Every UNSAT trace needs independent replay; every SAT object needs independent full99 checking."]})
    print(json.dumps({"status": "FOUR_BRANCH_NATIVE_RESULTS_PENDING_INDEPENDENT_REVIEW", "branch_records": len(results)}), flush=True)


if __name__ == "__main__":
    main()
