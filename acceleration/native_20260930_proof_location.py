"""Calibrate an ext4 native proof path; compare six fixed small control runs."""
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
import argparse
import json
import platform
import statistics
import subprocess
import sys
import time

import native_20260930_unrestricted_full99 as frozen

ROOT = frozen.ROOT
SPEC = Path(__file__).with_name("native_20260930_proof_location_spec.md")
AS_LIMIT = 4294967296
FILE_LIMIT = 10737418240
CAL = ROOT / "acceleration/results/20260930_native_cli_calibration/summary.json"
CAL_SHA = "f5ff562aff2ec550a97685c7012b302e760314a6f3829d80d022e2a669e680eb"


def command(seconds, args, file_limit=FILE_LIMIT):
    return [*frozen.WSL, "/usr/bin/timeout", "--signal=TERM", "--kill-after=5s", f"{seconds}s",
            "/usr/bin/prlimit", f"--as={AS_LIMIT}:{AS_LIMIT}", f"--fsize={file_limit}:{file_limit}",
            "--core=0:0", *args]


def local_capture(args, prefix, guard=30):
    receipt = frozen.run_record([*frozen.WSL, *args], prefix, guard)
    frozen.require(receipt["actual_exit_code"] == 0, "native helper failed: " + str(args))
    return receipt, Path(str(prefix) + ".stdout.log").read_text().strip()


def proof_copy(linux_proof, target, prefix):
    hash_receipt, native_hash = local_capture(["/usr/bin/sha256sum", linux_proof], Path(str(prefix) + "_hash"), 90)
    copy_receipt, _ = local_capture(["/usr/bin/cp", "--", linux_proof, frozen.linux(target)], Path(str(prefix) + "_copy"), 180)
    started = time.monotonic()
    target_hash = frozen.digest(target)
    frozen.require(native_hash.split()[0] == target_hash, "ext4 copy changed proof bytes")
    return {"linux_source": linux_proof, "sha256": target_hash, "bytes": target.stat().st_size,
            "native_hash_receipt": hash_receipt, "copy_receipt": copy_receipt,
            "windows_hash_wall_seconds": time.monotonic() - started}


def check_proof(cnf, proof, prefix, expected):
    receipt = frozen.run_record([frozen.CHECKER, cnf, proof], prefix, 30)
    accepted = receipt["actual_exit_code"] == 0 and "s VERIFIED" in Path(str(prefix) + ".stdout.log").read_text()
    frozen.require(accepted == expected, "DRAT control outcome")
    return {"accepted": accepted, "proof_sha256": frozen.digest(proof), "receipt": receipt}


def solve_control(cnf, folder, location, linux_dir, seconds):
    folder.mkdir()
    destination = str(folder.name) + ".drat"
    proof = folder / "proof.drat"
    linux_proof = linux_dir + "/" + destination if location == "ext4" else frozen.linux(proof)
    receipt = frozen.run_record(command(seconds, [frozen.linux(frozen.NATIVE), "--no-binary", "-c", "1000000",
                               frozen.linux(cnf), linux_proof]), folder / "solver", seconds + 20)
    copied = proof_copy(linux_proof, proof, folder / "transfer") if location == "ext4" else None
    return {"location": location, "native_receipt": receipt, "copy": copied, "proof": frozen.key(proof),
            "proof_sha256": frozen.digest(proof), "proof_bytes": proof.stat().st_size,
            "solver_plus_copy_seconds": receipt["wall_seconds"] + (copied["copy_receipt"]["wall_seconds"] if copied else 0)}


def write_cnf(path, variables, clauses):
    with path.open("x", encoding="ascii", newline="\n") as stream:
        stream.write(f"p cnf {variables} {len(clauses)}\n")
        for clause in clauses:
            stream.write(" ".join(map(str, clause)) + " 0\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    started = time.monotonic()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    frozen.checked_gate(CAL, CAL_SHA, "INDEPENDENT_NATIVE_CADICAL195_CLI_CALIBRATION_PASS")
    bindings = frozen.provenance()
    bindings.update({frozen.key(p): frozen.digest(p) for p in [Path(__file__), SPEC, CAL]})
    frozen.save(out / "manifest.json", {"timestamp": datetime.now(timezone.utc).isoformat(),
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "command": [sys.executable, *sys.argv], "cwd": str(ROOT), "python": platform.python_version(),
        "inputs_sha256": bindings, "research_calls": 0, "scope": "Native path controls only",
        "limits": {"address_space_bytes": AS_LIMIT, "file_bytes": FILE_LIMIT, "comparison_each_seconds": 15,
                   "comparison_calls": 6, "comparison_solver_seconds_total": 90, "overall_seconds": 240}})
    observations = []
    for label, cmd in [("cpu", ["/usr/bin/lscpu"]), ("kernel", ["/usr/bin/uname", "-a"]),
                       ("processes_before", ["/usr/bin/ps", "-eo", "pid,ppid,comm,pcpu,rss,args"])]:
        receipt, _ = local_capture(cmd, out / label)
        observations.append(receipt)
    made, linux_dir = local_capture(["/usr/bin/mktemp", "-d", "/tmp/conway99-native-proof-XXXXXX"], out / "mktemp")
    frozen.require(linux_dir.startswith("/tmp/conway99-native-proof-") and "\n" not in linux_dir, "unexpected ext4 workdir")
    mount, mount_text = local_capture(["/usr/bin/findmnt", "--target", linux_dir, "--output", "TARGET,SOURCE,FSTYPE,OPTIONS", "--noheadings"], out / "filesystem")
    frozen.require("ext4" in mount_text.split(), "new proof directory is not on observed ext4")
    frozen.save(out / "ext4_workspace.json", {"path": linux_dir, "preserved": True, "mktemp": made, "mount": mount})
    limits_receipt = frozen.run_record(command(10, ["/usr/bin/prlimit", "--noheadings", "--raw", "--output", "RESOURCE,SOFT,HARD"]), out / "limits", 30)
    frozen.require(limits_receipt["actual_exit_code"] == 0, "inherited-limit probe")
    limits = {fields[0]: fields[1:] for line in (out / "limits.stdout.log").read_text().splitlines() if (fields := line.split())}
    frozen.require(limits["AS"] == [str(AS_LIMIT)] * 2 and limits["FSIZE"] == [str(FILE_LIMIT)] * 2 and limits["CORE"] == ["0", "0"], "limits not inherited")
    cap = frozen.run_record(command(10, ["/usr/bin/dd", "if=/dev/zero", "of=" + linux_dir + "/cap.bin", "bs=1", "count=17", "status=none"], 16), out / "file_cap", 30)
    _, cap_size = local_capture(["/usr/bin/stat", "--format=%s", linux_dir + "/cap.bin"], out / "file_cap_size")
    frozen.require(cap["actual_exit_code"] not in (0, None) and cap_size == "16", "ext4 fsize enforcement")
    timed = frozen.run_record(command(0.1, ["/usr/bin/sleep", "10"]), out / "timeout", 20)
    frozen.require(timed["actual_exit_code"] == 124, "new wrapper timeout calibration")
    sat_cnf, unsat_cnf = out / "sat.cnf", out / "unsat.cnf"
    sat_clauses = [[1, 2], [-1, 2]]
    write_cnf(sat_cnf, 2, sat_clauses)
    write_cnf(unsat_cnf, 2, [[1, 2], [1, -2], [-1, 2], [-1, -2]])
    sat = solve_control(sat_cnf, out / "sat_ext4", "ext4", linux_dir, 15)
    frozen.require(sat["native_receipt"]["actual_exit_code"] == 10, "ext4 SAT exit")
    sat_model = frozen.parse_sat_stdout((out / "sat_ext4/solver.stdout.log").read_text(), 2)
    frozen.require(frozen.literal_formula_check(sat_clauses, sat_model), "ext4 SAT model")
    corrupted = [(-v if abs(v) == 2 else v) for v in sat_model]
    frozen.require(not frozen.literal_formula_check(sat_clauses, corrupted), "SAT wrong value control")
    unsat = solve_control(unsat_cnf, out / "unsat_ext4", "ext4", linux_dir, 15)
    frozen.require(unsat["native_receipt"]["actual_exit_code"] == 20, "ext4 UNSAT exit")
    proof = frozen.resolve(unsat["proof"])
    frozen.require(any(line.strip() not in ("", "0") and not line.startswith("d ") for line in proof.read_text().splitlines()), "nonempty reasoning required")
    valid = check_proof(unsat_cnf, proof, out / "valid_proof", True)
    bad = out / "invalid_empty_only.drat"
    bad.write_bytes(b"0\n")
    invalid = check_proof(unsat_cnf, bad, out / "invalid_proof", False)
    cnf = out / "pigeonhole9into8.cnf"
    clauses = [[p * 8 + h + 1 for h in range(8)] for p in range(9)]
    clauses += [[-(p * 8 + h + 1), -(q * 8 + h + 1)] for h in range(8) for p, q in combinations(range(9), 2)]
    write_cnf(cnf, 72, clauses)
    frozen.save(out / "comparison_protocol.json", {"cnf_sha256": frozen.digest(cnf), "variables": 72, "clauses": len(clauses),
        "order": ["windows", "ext4", "ext4", "windows", "windows", "ext4"], "repetitions_per_arm": 3,
        "same_input_path": frozen.key(cnf), "same_default_solver_options": True, "seed": None,
        "seed_null_reason": "Native default retained", "process_observation": frozen.key(out / "processes_before.stdout.log")})
    trials = []
    for index, location in enumerate(["windows", "ext4", "ext4", "windows", "windows", "ext4"]):
        if time.monotonic() - started >= 220:
            trials.append({"index": index, "location": location, "status": "SKIPPED_OVERALL_BUDGET"})
            continue
        trial = solve_control(cnf, out / f"trial{index:02d}_{location}", location, linux_dir, 15)
        trial["index"] = index
        trial["status"] = "COMPLETED_UNSAT" if trial["native_receipt"]["actual_exit_code"] == 20 else "INCOMPLETE_NATIVE_OUTCOME"
        if trial["status"] == "COMPLETED_UNSAT":
            trial["proof_check"] = check_proof(cnf, frozen.resolve(trial["proof"]), out / f"trial{index:02d}_checker", True)
        trials.append(trial)
        frozen.save(out / f"trial{index:02d}_record.json", trial)
        print(json.dumps({"trial": index, "location": location, "status": trial["status"], "solver_plus_copy_seconds": trial["solver_plus_copy_seconds"]}), flush=True)
    after, _ = local_capture(["/usr/bin/ps", "-eo", "pid,ppid,comm,pcpu,rss,args"], out / "processes_after")
    medians = {}
    for location in ("windows", "ext4"):
        valid_trials = [t for t in trials if t.get("status") == "COMPLETED_UNSAT" and t["location"] == location]
        medians[location] = {"completed": len(valid_trials), "median_solver_wall_seconds": statistics.median(t["native_receipt"]["wall_seconds"] for t in valid_trials) if valid_trials else None,
            "median_solver_plus_copy_seconds": statistics.median(t["solver_plus_copy_seconds"] for t in valid_trials) if valid_trials else None}
    inputs = {**bindings, **{frozen.key(p): frozen.digest(p) for p in [out / "manifest.json", sat_cnf, unsat_cnf, cnf, out / "comparison_protocol.json"]}}
    frozen.save(out / "summary.json", {"status": "NATIVE_EXT4_PROOF_PATH_CALIBRATION_PASS", "timestamp": datetime.now(timezone.utc).isoformat(),
        "inputs_sha256": inputs, "calibration_source_sha256": frozen.digest(Path(__file__)), "protocol_sha256": frozen.digest(SPEC),
        "ext4_workspace": linux_dir, "observations": observations + [after], "inherited_limits": limits,
        "file_cap": cap, "timeout": timed, "sat_control": sat, "sat_assignment": sat_model,
        "corrupted_sat_assignment": corrupted, "unsat_control": unsat, "valid_proof_check": valid, "corrupt_proof_check": invalid,
        "comparison_trials": trials, "descriptive_medians": medians, "total_wall_seconds": time.monotonic() - started,
        "research_calls": 0, "mathematical_claim_changed": False,
        "shared_components": ["Frozen native CLI parser/provenance/run receipt helpers", "Authenticated native solver and DRAT checker", "Python standard library"],
        "limitations": ["Single small pigeonhole formula, three repetitions per destination, current machine/concurrent workload only.",
                       "Input and stdout stay on Windows; only proof output changes. No research performance or general speedup claim.",
                       "Calibration producer authored this orchestration. Independent branch/object/proof checks remain mandatory."]})
    print(json.dumps({"status": "NATIVE_EXT4_PROOF_PATH_CALIBRATION_PASS", "summary_sha256": frozen.digest(out / "summary.json"), "medians": medians}), flush=True)


if __name__ == "__main__":
    main()
