"""Independent native CLI calibration plus gated unrestricted SAT orchestration.

Runs under the pinned Windows uv environment; no new Linux Python workflow.
"""
from datetime import datetime, timezone
from hashlib import sha256
import argparse
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / "build/research-cadical195/source/build/cadical"
NATIVE_SHA = "021e58781c761296b436cfbdf49507ff290db175f67e5609bf6f41e4cc62d0b7"
BUILD = ROOT / "acceleration/results/20260930_native_cadical195_build"
CHECKER = ROOT / "build/rook-drat-checker/drat-trim.exe"
CHECKER_SHA = "23d1613cb0b1ed491f4e723ff82492a8be6c349c2426d440412842c5246b90ac"
CNF = ROOT / "acceleration/results/20260930_unrestricted_full99_cnf/instance.cnf"
CNF_SHA = "7029f5c0965d0121aec6ce24db2b9a3d2e201e85b72c8ef51595c63bb62b2138"
MODEL = ROOT / "acceleration/results/20260930_unrestricted_full99_cnf/model.json"
MODEL_SHA = "77089d0a9dd94919bff62aa1e552b758eca061f980524131ad8d1861acce7a8e"
PROTOCOL = Path(__file__).with_name("native_20260930_unrestricted_full99_spec.md")
MEMORY_LIMIT = 8589934592
FILE_LIMIT = 10737418240
WSL = ["wsl.exe", "--distribution", "Ubuntu-24.04", "--exec"]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(path):
    result = sha256()
    with Path(path).open("rb") as source:
        for block in iter(lambda: source.read(1048576), b""):
            result.update(block)
    return result.hexdigest()


def key(path):
    path = Path(path).resolve()
    return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix()


def resolve(path):
    path = Path(path)
    return path if path.is_absolute() else ROOT / path


def linux(path):
    path = Path(path).resolve()
    require(path.is_relative_to(ROOT), "WSL path must remain in project")
    return "/mnt/" + path.drive[0].lower() + path.as_posix()[2:]


def save(path, obj):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(obj, stream, indent=2)
        stream.write("\n")


def read(path):
    return json.loads(Path(path).read_text())


def run_record(command, prefix, guard):
    stdout_path = Path(str(prefix) + ".stdout.log")
    stderr_path = Path(str(prefix) + ".stderr.log")
    started = time.monotonic()
    with stdout_path.open("xb") as stdout, stderr_path.open("xb") as stderr:
        try:
            result = subprocess.run([str(x) for x in command], cwd=ROOT, stdout=stdout, stderr=stderr, timeout=guard)
            exit_code, guard_expired = result.returncode, False
        except subprocess.TimeoutExpired:
            exit_code, guard_expired = None, True
    receipt = {"timestamp": datetime.now(timezone.utc).isoformat(), "command": [str(x) for x in command],
        "cwd": str(ROOT), "actual_exit_code": exit_code, "outer_windows_guard_expired": guard_expired,
        "outer_windows_guard_seconds": guard, "wall_seconds": time.monotonic() - started,
        "stdout": key(stdout_path), "stdout_sha256": digest(stdout_path),
        "stderr": key(stderr_path), "stderr_sha256": digest(stderr_path),
        "linux_process_state": "UNKNOWN_AFTER_OUTER_GUARD" if guard_expired else "WRAPPED_COMMAND_RETURNED",
        "exit_interpretation": {"10": "native SAT", "20": "native UNSAT", "0": "native UNKNOWN or non-solver success",
            "124": "GNU timeout deadline", "137": "forced kill; inspect stderr and receipt"}}
    save(Path(str(prefix) + ".receipt.json"), receipt)
    return receipt


def limited_command(seconds, command, file_limit=FILE_LIMIT):
    return [*WSL, "/usr/bin/timeout", "--signal=TERM", "--kill-after=5s", str(seconds) + "s",
        "/usr/bin/prlimit", f"--as={MEMORY_LIMIT}:{MEMORY_LIMIT}", f"--fsize={file_limit}:{file_limit}",
        "--core=0:0", *command]


def solver_command(cnf, proof, seconds, conflicts):
    return limited_command(seconds, [linux(NATIVE), "--no-binary", "-c", str(conflicts), linux(cnf), linux(proof)])


def parse_sat_stdout(text, variables):
    status, assignment, seen, terminated = [], [], set(), False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("s "):
            status.append(line)
        if not line.startswith("v "):
            continue
        for token in line[2:].split():
            try:
                value = int(token)
            except ValueError:
                raise ValueError("noninteger model literal") from None
            require(not terminated, "tokens after model terminator")
            if value == 0:
                terminated = True
                continue
            require(1 <= abs(value) <= variables, "model variable out of range")
            require(abs(value) not in seen, "duplicate/conflicting model variable")
            seen.add(abs(value))
            assignment.append(value)
    require(status == ["s SATISFIABLE"], "unique SAT status required")
    require(terminated, "model terminator missing")
    require(len(assignment) == variables and seen == set(range(1, variables + 1)), "incomplete model")
    return assignment


def literal_formula_check(clauses, assignment):
    truth = {abs(x): x > 0 for x in assignment}
    return all(any(truth[abs(x)] == (x > 0) for x in clause) for clause in clauses)


def parser_controls():
    positive = "c fixture\ns SATISFIABLE\nv 1\nv -2 3 0\n"
    require(parse_sat_stdout(positive, 3) == [1, -2, 3], "split-line parser positive")
    bad_cases = {
        "duplicate": "s SATISFIABLE\nv 1 -2 3 1 0\n", "conflict": "s SATISFIABLE\nv 1 -1 -2 3 0\n",
        "missing": "s SATISFIABLE\nv 1 -2 0\n", "out_of_range": "s SATISFIABLE\nv 1 -2 4 0\n",
        "no_terminator": "s SATISFIABLE\nv 1 -2 3\n", "after_terminator": "s SATISFIABLE\nv 1 -2 3 0 1\n",
        "wrong_status": "s UNSATISFIABLE\nv 1 -2 3 0\n", "duplicate_status": "s SATISFIABLE\ns SATISFIABLE\nv 1 -2 3 0\n",
        "noninteger": "s SATISFIABLE\nv 1 nope 3 0\n"}
    rejected = []
    for name, value in bad_cases.items():
        try:
            parse_sat_stdout(value, 3)
        except ValueError as error:
            rejected.append({"name": name, "reason": str(error), "fixture": value})
        else:
            raise ValueError("parser corruption accepted: " + name)
    return {"positive_fixture": positive, "positive_assignment": [1, -2, 3], "rejected": rejected}


def provenance():
    require(digest(NATIVE) == NATIVE_SHA, "native binary hash")
    require(digest(CHECKER) == CHECKER_SHA, "authenticated checker hash")
    require(digest(CNF) == CNF_SHA and digest(MODEL) == MODEL_SHA, "unrestricted input hashes")
    build_manifest, build_receipt = read(BUILD / "manifest.json"), read(BUILD / "receipt.json")
    require(build_manifest["upstream_commit"] == "146207318796f094dcded87349a64f0c6927309e", "upstream commit")
    require(build_receipt["native_sha256"] == NATIVE_SHA and build_receipt["source_changes"] == [], "build receipt")
    require(digest(BUILD / "cadical-1.9.5-source.tar.gz") == build_manifest["source_archive_sha256"] ==
            build_receipt["source_archive_sha256"], "source archive identity")
    for record in build_receipt["records"]:
        require(record["exit_code"] == 0 and digest(BUILD / (record["name"] + ".log")) == record["log_sha256"], "build log changed")
    inputs = [Path(__file__), PROTOCOL, CNF, MODEL, NATIVE, CHECKER,
        ROOT / "uv.lock", BUILD / "manifest.json", BUILD / "receipt.json", BUILD / "cadical-1.9.5-source.tar.gz",
        ROOT / "build/rook-drat-checker/build_manifest.json", ROOT / "build/rook-drat-checker/build_receipt.json"]
    inputs += [BUILD / (record["name"] + ".log") for record in build_receipt["records"]]
    return {key(path): digest(path) for path in inputs}


def calibrate(args):
    args.out.mkdir(parents=True, exist_ok=False)
    bindings = provenance()
    save(args.out / "manifest.json", {"timestamp": datetime.now(timezone.utc).isoformat(),
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "command": [sys.executable, *sys.argv], "cwd": str(ROOT), "python": platform.python_version(),
        "inputs_sha256": bindings, "question": "Independently calibrate native CLI assignments, direct DRAT, exit codes and resource wrappers before research.",
        "scope": "Tiny native formulas and engineering controls only", "research_calls": 0})
    inspections = []
    for name, command in (("native_short_help", [*WSL, linux(NATIVE), "-h"]),
        ("native_full_help", [*WSL, linux(NATIVE), "--help"]),
        ("native_version", [*WSL, linux(NATIVE), "--version"]),
        ("native_build", [*WSL, linux(NATIVE), "--build"]),
        ("timeout_version", [*WSL, "/usr/bin/timeout", "--version"]),
        ("timeout_help", [*WSL, "/usr/bin/timeout", "--help"]),
        ("prlimit_version", [*WSL, "/usr/bin/prlimit", "--version"]),
        ("prlimit_help", [*WSL, "/usr/bin/prlimit", "--help"])):
        receipt = run_record(command, args.out / name, 20)
        require(receipt["actual_exit_code"] == 0, "inspection failure")
        inspections.append(receipt)
    full_help = (args.out / "native_full_help.stdout.log").read_text()
    require("-c <limit>" in full_help and "--no-binary" in full_help and "DRAT" in full_help, "expected CLI options not supported")
    require((args.out / "native_version.stdout.log").read_text().strip() == "1.9.5", "native version")
    inherited = run_record(limited_command(10, ["/usr/bin/prlimit", "--noheadings", "--raw", "--output=RESOURCE,SOFT,HARD"]),
                           args.out / "inherited_limits", 30)
    require(inherited["actual_exit_code"] == 0, "limit inspection")
    limits = {row.split()[0]: row.split()[1:] for row in (args.out / "inherited_limits.stdout.log").read_text().splitlines()}
    require(limits["AS"] == [str(MEMORY_LIMIT)] * 2 and limits["FSIZE"] == [str(FILE_LIMIT)] * 2 and limits["CORE"] == ["0", "0"], "inherited exact limits")
    cap_file = args.out / "file_cap_probe.bin"
    cap_receipt = run_record(limited_command(10, ["/usr/bin/dd", "if=/dev/zero", "of=" + linux(cap_file), "bs=1", "count=17", "status=none"], 16),
                             args.out / "file_cap_probe", 30)
    require(cap_receipt["actual_exit_code"] != 0 and cap_file.stat().st_size == 16, "file cap not enforced")
    timeout_receipt = run_record([*WSL, "/usr/bin/timeout", "--signal=TERM", "--kill-after=1s", "0.1s", "/usr/bin/sleep", "10"],
                                 args.out / "timeout_probe", 20)
    require(timeout_receipt["actual_exit_code"] == 124 and timeout_receipt["wall_seconds"] < 10, "GNU timeout control")
    save(args.out / "parser_controls.json", parser_controls())
    cases = []
    for name, text, expected in (("sat", "p cnf 2 2\n1 2 0\n-1 2 0\n", 10),
            ("unsat", "p cnf 2 4\n1 2 0\n1 -2 0\n-1 2 0\n-1 -2 0\n", 20)):
        folder = args.out / name
        folder.mkdir()
        cnf, proof = folder / "instance.cnf", folder / "proof.drat"
        cnf.write_text(text, encoding="ascii", newline="\n")
        receipt = run_record(solver_command(cnf, proof, 30, 10000), folder / "solver", 50)
        require(receipt["actual_exit_code"] == expected, "native SAT/UNSAT exit convention")
        require(proof.exists() and proof.stat().st_size <= FILE_LIMIT, "direct proof file presence/size")
        stdout = (folder / "solver.stdout.log").read_text()
        if name == "sat":
            assignment = parse_sat_stdout(stdout, 2)
            require(literal_formula_check([[1, 2], [-1, 2]], assignment), "native SAT assignment invalid")
            wrong = [v if abs(v) != 2 else -v for v in assignment]
            require(not literal_formula_check([[1, 2], [-1, 2]], wrong), "flipped required SAT literal accepted")
            save(folder / "parsed_model.json", {"assignment": assignment})
            extra = {"complete_assignment_checked": True, "corrupted_required_literal_rejected": wrong}
        else:
            require([line.strip() for line in stdout.splitlines() if line.startswith("s ")] == ["s UNSATISFIABLE"], "UNSAT output status")
            lines = proof.read_text().splitlines()
            require(any(line.strip() != "0" and not line.startswith("d") for line in lines), "proof must include nonempty reasoning")
            invalid = folder / "empty_only_invalid.drat"
            invalid.write_text("0\n", encoding="ascii", newline="\n")
            checks = []
            for label, artifact, expected_accept in (("valid", proof, True), ("empty_only", invalid, False)):
                checked = run_record([str(CHECKER), str(cnf.resolve()), str(artifact.resolve())], folder / (label + "_checker"), 30)
                text_out = (folder / (label + "_checker.stdout.log")).read_bytes() + (folder / (label + "_checker.stderr.log")).read_bytes()
                accepted = checked["actual_exit_code"] == 0 and b"s VERIFIED" in text_out
                require(accepted == expected_accept, "native DRAT control")
                checks.append({"name": label, "accepted": accepted, "proof_sha256": digest(artifact), "receipt": checked})
            extra = {"nonempty_reasoning_present": True, "proof_checks": checks}
        cases.append({"name": name, "cnf_sha256": digest(cnf), "proof_sha256": digest(proof),
                      "native_receipt": receipt, **extra})
    inputs = {**bindings, key(args.out / "manifest.json"): digest(args.out / "manifest.json"),
              key(args.out / "parser_controls.json"): digest(args.out / "parser_controls.json")}
    save(args.out / "summary.json", {"timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "INDEPENDENT_NATIVE_CADICAL195_CLI_CALIBRATION_PASS", "verifier": "/root/structural_attack, independently checking root-produced native build",
        "inputs_sha256": inputs, "orchestrator_sha256": digest(Path(__file__)), "protocol_sha256": digest(PROTOCOL),
        "native_sha256": NATIVE_SHA, "checker_sha256": CHECKER_SHA, "native_cases": cases,
        "inspection_receipts": inspections, "inherited_limits": limits, "file_cap_receipt": cap_receipt,
        "timeout_receipt": timeout_receipt, "native_actual_exit_codes": [r["native_receipt"]["actual_exit_code"] for r in cases],
        "research_calls": 0, "target_resolution": False, "proof_of_research_instance": False,
        "shared_components": ["Official native solver and root-built authenticated DRAT checker; exact binary hashes bound", "Python standard library"],
        "limitations": ["Tiny calibration establishes this recorded tool path only; no native solver correctness proof or research performance guarantee.",
            "Official source build was not independently recompiled by this calibration; archive, compiler/build logs and resulting binary identity were checked."]})
    print(json.dumps({"status": "INDEPENDENT_NATIVE_CADICAL195_CLI_CALIBRATION_PASS", "native_exits": [10, 20],
                      "summary_sha256": digest(args.out / "summary.json"), "research_calls": 0}), flush=True)


def checked_gate(path, expected_hash, expected_status):
    require(path and expected_hash and digest(path) == expected_hash, "gate file/hash")
    gate = read(path)
    require(gate["status"] == expected_status, "unexpected gate status")
    for name, expected in gate["inputs_sha256"].items():
        require(digest(resolve(name)) == expected, "changed gate input: " + name)
    return gate


def preflight(args):
    bindings = provenance()
    native = checked_gate(args.native_gate, args.native_gate_sha256, "INDEPENDENT_NATIVE_CADICAL195_CLI_CALIBRATION_PASS")
    require(native["orchestrator_sha256"] == digest(Path(__file__)) and native["protocol_sha256"] == digest(PROTOCOL), "calibration/source changed")
    encoding = checked_gate(args.encoding_gate, args.encoding_gate_sha256, "INDEPENDENT_UNRESTRICTED_FULL99_CNF_ENCODING_PASS")
    require(encoding["inputs_sha256"][key(CNF)] == CNF_SHA and encoding["inputs_sha256"][key(MODEL)] == MODEL_SHA, "encoding input binding")
    require(args.object_gate_status.startswith("INDEPENDENT_UNRESTRICTED") and args.object_gate_status.endswith("PASS"), "unrestricted object control gate expected")
    checked_gate(args.object_gate, args.object_gate_sha256, args.object_gate_status)
    for path in (args.native_gate, args.encoding_gate, args.object_gate):
        bindings[key(path)] = digest(path)
    free = shutil.disk_usage(ROOT).free
    require(free >= 11 * 1024 ** 3, "less than11GiB free for bounded proof output")
    return bindings, free


def decode_and_check(assignment):
    model = read(MODEL)
    require(model["variables"] == len(assignment) == 1186500, "model dimensions")
    values = {abs(v): int(v > 0) for v in assignment}
    a = [row.copy() for row in model["known_adjacency_full99"]]
    for edge in model["edge_variables"]:
        u, v, variable = edge["u"], edge["v"], edge["id"]
        a[u][v] = a[v][u] = values[variable]
    errors = []
    require(len(a) == 99 and all(len(row) == 99 for row in a), "decoded shape")
    require(all(type(x) is int and x in (0, 1) for row in a for x in row), "decoded binary entries")
    for u in range(99):
        if a[u][u] != 0 or sum(a[u]) != 14:
            errors.append(["diagonal_or_degree", u])
        for v in range(u + 1, 99):
            if a[u][v] != a[v][u]:
                errors.append(["symmetry", u, v])
            common = sum(a[u][w] * a[w][v] for w in range(99))
            if common != 2 - a[u][v]:
                errors.append(["common_count", u, v, common])
    return {"adjacency_full99": a, "producer_exact_validation": {"valid": not errors, "vertices": 99,
        "pairs": 4851, "error_count": len(errors), "first_errors": errors[:12]},
        "independent_checker_required": True, "encoding_model_sha256": MODEL_SHA}


def research_or_preflight(args):
    bindings, free = preflight(args)
    args.out.mkdir(parents=True, exist_ok=False)
    folder = args.out / "main"
    command = solver_command(CNF, folder / "proof.drat", 300, 1000000)
    save(args.out / "manifest.json", {"timestamp": datetime.now(timezone.utc).isoformat(),
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "command": [sys.executable, *sys.argv], "cwd": str(ROOT), "python": platform.python_version(),
        "inputs_sha256": bindings, "research_command": command, "disk_free_bytes_before_call": free,
        "limits": {"gnu_timeout_seconds": 300, "kill_after_seconds": 5, "native_conflicts": 1000000,
            "address_space_bytes_soft_hard": MEMORY_LIMIT, "file_bytes_soft_hard": FILE_LIMIT, "core_bytes": 0},
        "scope": "Unrestricted normalized target: all3486outerpairs free, only189root-scaffold edges fixed, no automorphism.",
        "mode": "RESEARCH" if args.research else "PREFLIGHT_ONLY", "random_seed": None,
        "random_seed_null_reason": "Native defaults; no seed option changed.", "proof_encoding": "ASCII DRAT directly to disk"})
    if not args.research:
        save(args.out / "summary.json", {"status": "NATIVE_UNRESTRICTED_RESEARCH_PREFLIGHT_PASS", "research_calls": 0,
             "all_three_gates_checked": True, "proposed_command": command})
        print(json.dumps({"status": "NATIVE_UNRESTRICTED_RESEARCH_PREFLIGHT_PASS", "research_calls": 0}), flush=True)
        return
    folder.mkdir()
    print(json.dumps({"state": "NATIVE_UNRESTRICTED_SOLVER_LAUNCHING", "seconds": 300,
        "memory_bytes": MEMORY_LIMIT, "max_proof_bytes": FILE_LIMIT}), flush=True)
    receipt = run_record(command, folder / "solver", 320)
    raw_stdout = (folder / "solver.stdout.log").read_text(errors="strict")
    artifacts = [folder / "solver.stdout.log", folder / "solver.stderr.log", folder / "solver.receipt.json"]
    graph_valid = None
    if any(line.strip() == "s SATISFIABLE" for line in raw_stdout.splitlines()):
        try:
            assignment = parse_sat_stdout(raw_stdout, 1186500)
            parsed = folder / "parsed_model.json"
            save(parsed, {"assignment": assignment})
            artifacts.append(parsed)
            decoded = decode_and_check(assignment)
            decoded["status"] = "CANDIDATE_PENDING_INDEPENDENT_FULL99_OBJECT_CHECK"
            decoded_path = folder / "decoded_full99.json"
            save(decoded_path, decoded)
            artifacts.append(decoded_path)
            graph_valid = decoded["producer_exact_validation"]["valid"]
        except BaseException as error:
            save(folder / "parse_or_decode_failure.json", {"type": type(error).__name__, "message": str(error),
                "raw_stdout_preserved": True, "actual_native_receipt_unchanged": True})
    proof = folder / "proof.drat"
    if proof.exists():
        artifacts.append(proof)
        require(proof.stat().st_size <= FILE_LIMIT, "proof exceeded declared kernel file cap")
    code = receipt["actual_exit_code"]
    interpreted = "SAT_RAW_UNCHECKED" if code == 10 else "UNSAT_PROOF_UNCHECKED" if code == 20 else "UNKNOWN_NATIVE" if code == 0 else "UNKNOWN_LIMIT_OR_ENGINEERING_OUTCOME"
    save(args.out / "summary.json", {"timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "NATIVE_SOLVER_ARTIFACTS_PENDING_INDEPENDENT_REVIEW", "actual_exit_code": code,
        "interpreted_result": interpreted, "receipt": key(folder / "solver.receipt.json"),
        "native_process_wall_seconds": receipt["wall_seconds"], "linux_process_state": receipt["linux_process_state"],
        "research_calls": 1, "producer_valid_graph": graph_valid,
        "producer_valid_graph_null_reason": "No complete parsed/decoded SAT object." if graph_valid is None else None,
        "raw_artifacts": {key(p): {"sha256": digest(p), "bytes": p.stat().st_size} for p in artifacts},
        "independently_verified_target_resolution": False, "automatic_retry": False,
        "limitations": ["SAT needs the separately authored complete CNF/object check; UNSAT needs independent authenticated proof replay.",
            "Timeout/error outcomes do not establish infeasibility. Raw proof preservation is not proof completeness."]})
    print(json.dumps({"actual_exit_code": code, "interpreted_result": interpreted,
        "producer_valid_graph": graph_valid, "proof_bytes": proof.stat().st_size if proof.exists() else None}), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--calibrate", action="store_true")
    mode.add_argument("--preflight", action="store_true")
    mode.add_argument("--research", action="store_true")
    parser.add_argument("--native-gate", type=Path)
    parser.add_argument("--native-gate-sha256")
    parser.add_argument("--encoding-gate", type=Path)
    parser.add_argument("--encoding-gate-sha256")
    parser.add_argument("--object-gate", type=Path)
    parser.add_argument("--object-gate-sha256")
    parser.add_argument("--object-gate-status")
    args = parser.parse_args()
    if args.calibrate:
        calibrate(args)
    else:
        research_or_preflight(args)


if __name__ == "__main__":
    main()
