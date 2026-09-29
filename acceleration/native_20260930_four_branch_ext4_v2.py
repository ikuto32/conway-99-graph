"""Composed equality-plus-branch CNFs and explicitly gated native orchestration."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
import json
import platform
import shutil
import subprocess
import sys

import native_20260930_unrestricted_full99 as base
import native_20260930_proof_location as ext4
import native_20260930_four_branch_ext4 as original

ROOT = base.ROOT
SPEC = Path(__file__).with_name("native_20260930_four_branch_ext4_v2_spec.md")
EQUALITY = ROOT / "acceleration/results/20260930_unrestricted_pair_equalities/run01/pair_equalities.units.cnfpart"
EQUALITY_SHA = "78b5be7dcbcee5e6593ffd8a047f88228f0383da70d0ebab5261348716466b95"
EQUALITY_GATE = ROOT / "acceleration/results/20260930_independent_review/unrestricted_pair_equalities_v2/summary.json"
EQUALITY_GATE_SHA = "1ebbff5e7313a97de6ce86aef3a9047ef856aae7ef0e8b1258eec216f1840237"
CHECKER = ROOT / "acceleration/audit_20260930_strengthened_four_branch_bytes_v1.py"
HEADER = b"p cnf 1186500 4141120\n"


def checked_inputs(args, final):
    inputs = original.bindings()
    equality = base.checked_gate(EQUALITY_GATE, EQUALITY_GATE_SHA, "INDEPENDENT_UNRESTRICTED_PAIR_EQUALITY_UNITS_PASS")
    base.require(base.digest(EQUALITY) == EQUALITY_SHA == equality["suffix_sha256"], "exact equality suffix")
    base.require(equality["base_cnf_sha256"] == base.CNF_SHA and equality["clauses"] == 4141116 and len(equality["unit_literals"]) == 4662, "equality gate counts")
    calibration = base.checked_gate(args.byte_checker_gate, args.byte_checker_gate_sha256,
                                   "INDEPENDENT_STRENGTHENED_FOUR_BRANCH_CNF_BYTES_CALIBRATION_PASS")
    base.require(calibration["inputs_sha256"][base.key(CHECKER)] == base.digest(CHECKER), "composed byte checker calibration source")
    for path in [Path(__file__), SPEC, EQUALITY, EQUALITY_GATE, CHECKER, args.byte_checker_gate,
                 Path(original.__file__), original.SPEC]:
        inputs[base.key(path)] = base.digest(path)
    if final:
        base.require(args.object_gate_status and args.object_gate_status.startswith("INDEPENDENT_")
                     and args.object_gate_status.endswith("CALIBRATION_PASS"), "augmented object calibration status")
        base.checked_gate(args.object_gate, args.object_gate_sha256, args.object_gate_status)
        composition = base.checked_gate(args.composition_gate, args.composition_gate_sha256,
                                         "INDEPENDENT_STRENGTHENED_FOUR_BRANCH_COMPOSITION_PASS")
        base.require(composition["inputs_sha256"][base.key(args.prepared)] == base.digest(args.prepared), "composition gate binds preparation")
        for path in [args.object_gate, args.composition_gate, args.prepared]:
            inputs[base.key(path)] = base.digest(path)
    return inputs


def composed_recipe(row):
    suffix = base.resolve(row["suffix"])
    base.require(base.digest(suffix) == row["suffix_sha256"], "original suffix identity")
    digest = sha256(HEADER)
    with base.CNF.open("rb") as stream:
        base.require(stream.readline() == b"p cnf 1186500 4136454\n", "base header")
        for block in iter(lambda: stream.read(1048576), b""):
            digest.update(block)
    digest.update(EQUALITY.read_bytes())
    digest.update(suffix.read_bytes())
    return {"branch": row["branch"], "pattern_xyz": row["pattern_xyz"], "branch_units": row["units"],
            "base_cnf": base.key(base.CNF), "base_cnf_sha256": base.CNF_SHA,
            "equality_suffix": base.key(EQUALITY), "equality_suffix_sha256": EQUALITY_SHA,
            "equality_units_count": 4662, "original_branch_suffix": row["suffix"],
            "original_branch_suffix_sha256": row["suffix_sha256"], "original_branch_cnf_sha256": row["cnf_sha256"],
            "variables": 1186500, "clauses": 4141120, "cnf_sha256": digest.hexdigest(),
            "recipe": "Replace base header exactly; copy complete base body; append equality suffix, then original four-unit suffix."}


def byte_gate(cnf, row, folder):
    gate_path = folder / "independent_composed_bytes.json"
    cover, cover_hash, _ = original.GATES[4]
    command = [sys.executable, CHECKER, "--base", base.CNF, "--branch-cnf", cnf, "--branch", row["branch"],
        "--recipe", original.RECIPE, "--coverage-gate", ROOT / cover, "--coverage-gate-sha256", cover_hash,
        "--equality-suffix", EQUALITY, "--equality-gate", EQUALITY_GATE, "--equality-gate-sha256", EQUALITY_GATE_SHA,
        "--out", gate_path]
    receipt = base.run_record(command, folder / "independent_byte_checker", 60)
    base.require(receipt["actual_exit_code"] == 0, "independent composed byte checker failed")
    gate = base.checked_gate(gate_path, base.digest(gate_path), "INDEPENDENT_STRENGTHENED_FOUR_BRANCH_CNF_BYTES_PASS")
    base.require(gate["branch_cnf_sha256"] == row["cnf_sha256"] and gate["units"] == row["branch_units"], "composed gate exact branch")
    base.require(gate["equality_suffix_sha256"] == EQUALITY_SHA and gate["equality_units_count"] == 4662, "composed equality binding")
    return {"path": base.key(gate_path), "sha256": base.digest(gate_path), "receipt": receipt}


def prepare(out, inputs):
    records = [composed_recipe(row) for row in base.read(original.RECIPE)["branches"]]
    recipes = out / "recipes.json"
    base.save(recipes, {"schema": "EQUALITY_STRENGTHENED_FOUR_BRANCH_RECIPES_V1", "branches": records,
        "status": "CANDIDATE_COMPOSITION_PENDING_ROOT_REVIEW", "solver_calls": 0,
        "coverage_gate": original.GATES[4][0], "coverage_gate_sha256": original.GATES[4][1],
        "equality_gate": base.key(EQUALITY_GATE), "equality_gate_sha256": EQUALITY_GATE_SHA})
    results = []
    for row in records:
        folder = out / row["branch"]
        folder.mkdir()
        cnf = folder / "instance.cnf"
        with cnf.open("xb") as target, base.CNF.open("rb") as source:
            base.require(source.readline() == b"p cnf 1186500 4136454\n", "base header")
            target.write(HEADER)
            shutil.copyfileobj(source, target, 1048576)
            target.write(EQUALITY.read_bytes())
            target.write(base.resolve(row["original_branch_suffix"]).read_bytes())
        base.require(base.digest(cnf) == row["cnf_sha256"], "composed recipe hash mismatch")
        gate = byte_gate(cnf, row, folder)
        results.append({"branch": row["branch"], "cnf": base.key(cnf), "cnf_sha256": row["cnf_sha256"],
                        "recipe": row, "independent_byte_gate": gate})
    base.save(out / "summary.json", {"status": "STRENGTHENED_FOUR_BRANCH_PREPARATION_PASS", "inputs_sha256": inputs,
        "recipes": base.key(recipes), "recipes_sha256": base.digest(recipes), "branches": results,
        "research_calls": 0, "composition_review_pending": True, "augmented_sat_gate_required_before_launch": True})
    print(json.dumps({"status": "STRENGTHENED_FOUR_BRANCH_PREPARATION_PASS", "summary_sha256": base.digest(out / "summary.json"), "research_calls": 0}), flush=True)


def load_prepared(path):
    report = base.read(path)
    base.require(report["status"] == "STRENGTHENED_FOUR_BRANCH_PREPARATION_PASS", "not a strengthened preparation")
    base.require(base.digest(base.resolve(report["recipes"])) == report["recipes_sha256"], "recipes changed")
    expected = [composed_recipe(row) for row in base.read(original.RECIPE)["branches"]]
    actual = base.read(base.resolve(report["recipes"]))["branches"]
    base.require(actual == expected, "all composed recipes match exact originals and equality suffix")
    base.require([r["branch"] for r in report["branches"]] == [r["branch"] for r in expected], "ordered branch population")
    for row, item in zip(expected, report["branches"]):
        base.require(item["recipe"] == row and base.digest(base.resolve(item["cnf"])) == row["cnf_sha256"], "prepared CNF changed")
        gate = item["independent_byte_gate"]
        base.checked_gate(base.resolve(gate["path"]), gate["sha256"], "INDEPENDENT_STRENGTHENED_FOUR_BRANCH_CNF_BYTES_PASS")
    return report["branches"]


def solve_one(item, out, linux_dir):
    row = item["recipe"]
    folder = out / row["branch"]
    folder.mkdir()
    cnf = base.resolve(item["cnf"])
    gate = byte_gate(cnf, row, folder)
    proof_linux = linux_dir + "/" + row["branch"] + ".drat"
    proof = folder / "proof.drat"
    command = ext4.command(300, [base.linux(base.NATIVE), "--no-binary", "-c", "1000000", base.linux(cnf), proof_linux])
    base.save(folder / "launch.json", {"timestamp": datetime.now(timezone.utc).isoformat(), "branch": row["branch"],
        "command": command, "independent_byte_gate": gate, "cnf_sha256": row["cnf_sha256"], "ext4_proof": proof_linux,
        "limits": {"native_seconds": 300, "conflicts": 1000000, "address_space_bytes": ext4.AS_LIMIT, "file_bytes": ext4.FILE_LIMIT}})
    print(json.dumps({"state": "STRENGTHENED_BRANCH_NATIVE_LAUNCHING", "branch": row["branch"]}), flush=True)
    receipt = base.run_record(command, folder / "solver", 320)
    result = {"branch": row["branch"], "native_receipt": receipt, "actual_exit_code": receipt["actual_exit_code"],
              "independent_byte_gate": gate, "raw_sat_status": False, "independently_verified_target_resolution": False}
    if receipt["outer_windows_guard_expired"]:
        result["status"] = "UNKNOWN_LINUX_PROCESS_STATE_AFTER_OUTER_GUARD"
        base.save(folder / "summary.json", result)
        return result
    try:
        result["proof_copy"] = ext4.proof_copy(proof_linux, proof, folder / "transfer")
        base.require(proof.stat().st_size <= ext4.FILE_LIMIT, "proof exceeded declared cap")
    except BaseException as error:
        result["proof_copy_failure"] = {"type": type(error).__name__, "message": str(error), "ext4_original_retained": proof_linux}
    raw = (folder / "solver.stdout.log").read_text()
    result["raw_sat_status"] = any(line.strip() == "s SATISFIABLE" for line in raw.splitlines())
    if result["raw_sat_status"]:
        try:
            assignment = base.parse_sat_stdout(raw, 1186500)
            base.save(folder / "parsed_model.json", {"assignment": assignment})
            decoded = base.decode_and_check(assignment)
            decoded["status"] = "CANDIDATE_PENDING_INDEPENDENT_AUGMENTED_TARGET_CHECK"
            base.save(folder / "decoded_full99.json", decoded)
            values = set(assignment)
            equality_units = base.read(EQUALITY_GATE)["unit_literals"]
            result["producer_all_added_units_satisfied"] = all(v in values for v in [*equality_units, *row["branch_units"]])
            result["producer_target_check"] = decoded["producer_exact_validation"]
        except BaseException as error:
            result["decode_failure"] = {"type": type(error).__name__, "message": str(error)}
    code = receipt["actual_exit_code"]
    result["status"] = "SAT_CANDIDATE_PENDING_INDEPENDENT_CHECK" if code == 10 else "UNSAT_TRACE_PENDING_INDEPENDENT_REPLAY" if code == 20 else "UNKNOWN_NATIVE_OR_RESOURCE_OUTCOME"
    result["outputs_sha256"] = {base.key(p): base.digest(p) for p in folder.iterdir() if p.is_file()}
    base.save(folder / "summary.json", result)
    print(json.dumps({"state": "STRENGTHENED_BRANCH_NATIVE_RETURNED", "branch": row["branch"], "actual_exit_code": code,
                      "proof_bytes": proof.stat().st_size if proof.exists() else None}), flush=True)
    return result


def research(out, items):
    base.require(shutil.disk_usage(ROOT).free >= 81 * 1024 ** 3, "Windows free space below81GiB")
    made, linux_dir = ext4.local_capture(["/usr/bin/mktemp", "-d", "/tmp/conway99-strengthened-four-XXXXXX"], out / "mktemp")
    base.require(linux_dir.startswith("/tmp/conway99-strengthened-four-") and "\n" not in linux_dir, "fresh ext4 path")
    mount, mount_text = ext4.local_capture(["/usr/bin/findmnt", "--target", linux_dir, "--output", "TARGET,SOURCE,FSTYPE,OPTIONS", "--noheadings"], out / "filesystem")
    base.require("ext4" in mount_text.split(), "ext4 filesystem required")
    disk, free_text = ext4.local_capture(["/usr/bin/df", "--output=avail", "-B1", linux_dir], out / "disk_free")
    base.require(int(free_text.splitlines()[-1]) >= 41 * 1024 ** 3, "ext4 free space below41GiB")
    base.save(out / "workspace.json", {"path": linux_dir, "preserved": True, "mktemp": made, "mount": mount, "disk": disk})
    results = []
    for offset in (0, 2):
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [(row["branch"], executor.submit(solve_one, row, out, linux_dir)) for row in items[offset:offset+2]]
            for name, future in futures:
                try:
                    result = future.result()
                except BaseException as error:
                    result = {"branch": name, "status": "WORKER_ERROR_REVIEW_RAW_RECEIPTS", "type": type(error).__name__, "message": str(error)}
                    base.save(out / (name + "_worker_failure.json"), result)
                results.append(result)
        if any(r.get("raw_sat_status") or r.get("native_receipt", {}).get("outer_windows_guard_expired")
               or r["status"] == "WORKER_ERROR_REVIEW_RAW_RECEIPTS" or "proof_copy_failure" in r for r in results):
            results.extend({"branch": item["branch"], "status": "SKIPPED_PENDING_FIRST_BATCH_REVIEW"} for item in items[offset+2:])
            break
    base.save(out / "summary.json", {"status": "STRENGTHENED_FOUR_BRANCH_RESULTS_PENDING_INDEPENDENT_REVIEW", "branches": results,
        "attempted_solver_calls": sum((out / item["branch"] / "launch.json").exists() for item in items),
        "independently_verified_target_resolution": False, "automatic_retry": False,
        "limitations": ["Every raw SAT/UNSAT result requires its separate independent object/trace check.", "Unknown and limited runs do not exclude branches."]})


def main():
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group(required=True)
    for mode in ("prepare", "preflight", "research"):
        modes.add_argument("--" + mode, action="store_true")
    for name in ("out", "prepared", "byte-checker-gate", "object-gate", "composition-gate"):
        parser.add_argument("--" + name, type=Path, required=name in ("out", "byte-checker-gate"))
    for name in ("byte-checker-gate-sha256", "object-gate-sha256", "object-gate-status", "composition-gate-sha256"):
        parser.add_argument("--" + name, required=name == "byte-checker-gate-sha256")
    args = parser.parse_args()
    inputs = checked_inputs(args, final=not args.prepare)
    items = None if args.prepare else load_prepared(args.prepared)
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    base.save(out / "manifest.json", {"timestamp": datetime.now(timezone.utc).isoformat(),
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "command": [sys.executable, *sys.argv], "cwd": str(ROOT), "python": platform.python_version(), "inputs_sha256": inputs,
        "mode": "PREPARE" if args.prepare else "PREFLIGHT" if args.preflight else "RESEARCH",
        "maximum_research_calls": 4 if args.research else 0, "concurrency": 2,
        "native_seconds_each": 300, "conflicts_each": 1000000, "native_address_space_each": ext4.AS_LIMIT,
        "file_bytes_each": ext4.FILE_LIMIT, "random_seed": None, "random_seed_null_reason": "Native default unchanged",
        "scope": "Original unrestrictedbase+4662entailed equalityunits+four canonical branchunits."})
    if args.prepare:
        prepare(out, inputs)
    elif args.preflight:
        base.save(out / "summary.json", {"status": "STRENGTHENED_FOUR_BRANCH_PREFLIGHT_PASS", "research_calls": 0,
                                        "all_gates_checked": True, "branches": items})
        print(json.dumps({"status": "STRENGTHENED_FOUR_BRANCH_PREFLIGHT_PASS", "research_calls": 0}), flush=True)
    else:
        research(out, items)


if __name__ == "__main__":
    main()
