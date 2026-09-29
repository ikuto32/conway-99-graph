"""Gated single-call native pilot for the fixed Wave151 full99 family."""
from datetime import datetime, timezone
from pathlib import Path
import argparse
import json
import platform
import shutil
import subprocess
import sys

import native_20260930_unrestricted_full99 as helper
import native_20260930_proof_location as ext4

ROOT = helper.ROOT
DATA = ROOT / "acceleration/results/20260930_triangle_wave151_full99_cnf"
CNF, MODEL, SCOPE = DATA / "instance.cnf", DATA / "model.json", DATA / "scope.json"
CNF_SHA = "24d6b14e08fcd10f390edf462f75a6bc160c91c863448adf72d076f2297fc27e"
MODEL_SHA = "e688c04d330cb1470af19dd1590960c9ddc0c9b7f71c718de2db5358ae1668f7"
SCOPE_SHA = "f593054838b96460b2b62b187966696696173d3bc915c7e6e33779c56b05f508"
PROP = ROOT / "acceleration/results/20260930_triangle_partial99/wave151.json"
PROP_SHA = "688b0255760a57a4cdd39e1ea471a784e3771a13c6fd3a6eb8b3615a7c43f063"
SPEC = Path(__file__).with_name("native_20260930_wave151_triangle_full99_spec.md")
ENGINEERING_GATES = [
    ("acceleration/results/20260930_native_cli_calibration/summary.json", "f5ff562aff2ec550a97685c7012b302e760314a6f3829d80d022e2a669e680eb", "INDEPENDENT_NATIVE_CADICAL195_CLI_CALIBRATION_PASS"),
    ("acceleration/results/20260930_native_proof_location/summary.json", "d1036cfcbe9b24e0f7ea6e0a3799968a5d9232e8167fb31b224211e5c845c619", "NATIVE_EXT4_PROOF_PATH_CALIBRATION_PASS")]


def preflight(args):
    bindings = {}
    for path, expected in [(CNF, CNF_SHA), (MODEL, MODEL_SHA), (SCOPE, SCOPE_SHA), (PROP, PROP_SHA),
                           (helper.NATIVE, helper.NATIVE_SHA), (helper.CHECKER, helper.CHECKER_SHA)]:
        helper.require(helper.digest(path) == expected, "exact input/native identity: " + helper.key(path))
        bindings[helper.key(path)] = expected
    for name, expected, status in ENGINEERING_GATES:
        helper.checked_gate(ROOT / name, expected, status)
        bindings[name] = expected
    propagation = helper.checked_gate(args.propagation_gate, args.propagation_gate_sha256,
                                     "INDEPENDENT_TRIANGLE_Q1_PARTIAL99_PROPAGATION_PASS")
    helper.require(propagation["inputs_sha256"][helper.key(PROP)] == PROP_SHA, "propagation gate binds selected raw family")
    encoding = helper.checked_gate(args.encoding_gate, args.encoding_gate_sha256,
                                  "INDEPENDENT_CONDITIONAL_WAVE151_TRIANGLE_FULL99_CNF_ENCODING_PASS")
    for path, expected in [(CNF, CNF_SHA), (MODEL, MODEL_SHA), (SCOPE, SCOPE_SHA)]:
        helper.require(encoding["inputs_sha256"][helper.key(path)] == expected, "new conditional encoding gate binding")
    obj = helper.checked_gate(args.object_gate, args.object_gate_sha256,
                              "INDEPENDENT_WAVE151_TRIANGLE_FULL99_SAT_OBJECT_CHECKER_CALIBRATION_PASS")
    for path, expected in [(CNF, CNF_SHA), (MODEL, MODEL_SHA)]:
        helper.require(obj["inputs_sha256"][helper.key(path)] == expected, "new conditional object checker gate binding")
    for path in [Path(__file__), SPEC, Path(helper.__file__), Path(ext4.__file__), ext4.SPEC,
                 args.propagation_gate, args.encoding_gate, args.object_gate, ROOT / "uv.lock", ROOT / "pyproject.toml"]:
        bindings[helper.key(path)] = helper.digest(path)
    model = helper.read(MODEL)
    helper.require(model["schema"] == "CONDITIONAL_TRIANGLE_FULL99_EXACT_PREFIX_CNF_V1"
                   and model["variables"] == 429779 and model["clauses"] == 1487778, "dedicated conditional model schema/counts")
    helper.require(model["scope_sha256"] == SCOPE_SHA and model["propagation_sha256"] == PROP_SHA
                   and model["target_automorphism_assumed"] is False and model["unrestricted_coverage_claim"] is False,
                   "scope metadata")
    with CNF.open("rb") as stream:
        helper.require(stream.readline() == b"p cnf 429779 1487778\n", "exact conditional DIMACS header")
    return bindings


def decode(assignment):
    model = helper.read(MODEL)
    helper.require(len(assignment) == model["variables"] == 429779, "complete conditional assignment length")
    values = {abs(lit): int(lit > 0) for lit in assignment}
    graph = [row.copy() for row in model["known_adjacency_full99"]]
    for item in model["edge_variables"]:
        u, v = item["u"], item["v"]
        graph[u][v] = graph[v][u] = values[item["id"]]
    failures = []
    helper.require(len(graph) == 99 and all(len(row) == 99 for row in graph), "decoded shape")
    helper.require(all(type(value) is int and value in (0, 1) for row in graph for value in row), "decoded binary entries")
    for u in range(99):
        if graph[u][u] != 0 or sum(graph[u]) != 14:
            failures.append(["diagonal_degree", u])
        for v in range(u + 1, 99):
            if graph[u][v] != graph[v][u]:
                failures.append(["symmetry", u, v])
            common = sum(graph[u][w] * graph[w][v] for w in range(99))
            if common != 2 - graph[u][v]:
                failures.append(["common", u, v, common])
    return {"status": "CANDIDATE_PENDING_INDEPENDENT_CONDITIONAL_TARGET_CHECK", "adjacency_full99": graph,
        "encoding_model_sha256": MODEL_SHA, "scope_sha256": SCOPE_SHA,
        "producer_exact_check": {"valid": not failures, "error_count": len(failures), "first_errors": failures[:12]},
        "independent_approval": False}


def run(args):
    bindings = preflight(args)
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    host_free = shutil.disk_usage(ROOT).free
    helper.require(host_free >= 21 * 1024 ** 3, "host free space below21GiB")
    mount, mount_text = ext4.local_capture(["/usr/bin/findmnt", "--target", "/tmp", "--output", "TARGET,SOURCE,FSTYPE,OPTIONS", "--noheadings"], out / "filesystem")
    helper.require("ext4" in mount_text.split(), "calibrated ext4 proof filesystem required")
    disk, disk_text = ext4.local_capture(["/usr/bin/df", "--output=avail", "-B1", "/tmp"], out / "disk_free")
    helper.require(int(disk_text.splitlines()[-1]) >= 11 * 1024 ** 3, "ext4 free space below11GiB")
    helper.save(out / "manifest.json", {"timestamp": datetime.now(timezone.utc).isoformat(),
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "command": [sys.executable, *sys.argv], "cwd": str(ROOT), "python": platform.python_version(),
        "inputs_sha256": bindings, "mode": "PREFLIGHT_ONLY" if args.preflight else "RESEARCH",
        "scope": "One fixed Wave151 triangle-root/Q1 full99 completion, not unrestricted target coverage",
        "limits": {"native_seconds": 300, "conflicts": 1000000, "address_space_bytes": ext4.AS_LIMIT,
                   "file_bytes": ext4.FILE_LIMIT, "kill_after_seconds": 5, "outer_windows_guard_seconds": 320},
        "disk_free_host": host_free, "filesystem_receipt": mount, "ext4_disk_receipt": disk,
        "random_seed": None, "random_seed_null_reason": "Native default retained",
        "shared_components": ["Frozen native parser, subprocess receipt and ext4 proof-copy helpers", "Calibrated pristine native executable and authenticated checker"],
        "old_scope_reused_as_mathematical_premise": False})
    if args.preflight:
        helper.save(out / "summary.json", {"status": "CONDITIONAL_TRIANGLE_NATIVE_PREFLIGHT_PASS", "research_calls": 0,
            "new_propagation_encoding_object_gates_checked": True, "source_sha256": helper.digest(Path(__file__)),
            "scope": "Fixed Wave151 only", "native_call_launched": False})
        print(json.dumps({"status": "CONDITIONAL_TRIANGLE_NATIVE_PREFLIGHT_PASS", "research_calls": 0}), flush=True)
        return
    made, linux_dir = ext4.local_capture(["/usr/bin/mktemp", "-d", "/tmp/conway99-triangle-XXXXXX"], out / "mktemp")
    helper.require(linux_dir.startswith("/tmp/conway99-triangle-") and "\n" not in linux_dir, "exclusive proof directory")
    helper.save(out / "workspace.json", {"path": linux_dir, "preserved": True, "mktemp": made})
    folder = out / "main"
    folder.mkdir()
    linux_proof = linux_dir + "/proof.drat"
    command = ext4.command(300, [helper.linux(helper.NATIVE), "--no-binary", "-c", "1000000", helper.linux(CNF), linux_proof])
    helper.save(folder / "launch.json", {"timestamp": datetime.now(timezone.utc).isoformat(), "command": command,
        "cnf_sha256": CNF_SHA, "model_sha256": MODEL_SHA, "ext4_proof": linux_proof})
    print(json.dumps({"state": "CONDITIONAL_TRIANGLE_NATIVE_LAUNCHING", "variables": 429779, "clauses": 1487778, "native_seconds": 300}), flush=True)
    receipt = helper.run_record(command, folder / "solver", 320)
    result = {"actual_exit_code": receipt["actual_exit_code"], "receipt": receipt, "research_calls": 1,
        "status": "CONDITIONAL_NATIVE_ARTIFACTS_PENDING_INDEPENDENT_REVIEW", "target_resolution": False,
        "scope": "One fixed triangle-root/Q1 family only", "automatic_retry": False}
    if not receipt["outer_windows_guard_expired"]:
        try:
            result["proof_copy"] = ext4.proof_copy(linux_proof, folder / "proof.drat", folder / "transfer")
            helper.require((folder / "proof.drat").stat().st_size <= ext4.FILE_LIMIT, "proof file cap")
        except BaseException as error:
            result["proof_copy_failure"] = {"type": type(error).__name__, "message": str(error), "linux_original_retained": linux_proof}
        stdout = (folder / "solver.stdout.log").read_text()
        if any(line.strip() == "s SATISFIABLE" for line in stdout.splitlines()):
            try:
                assignment = helper.parse_sat_stdout(stdout, 429779)
                helper.save(folder / "parsed_model.json", {"assignment": assignment})
                decoded = decode(assignment)
                helper.save(folder / "decoded_full99.json", decoded)
                result["producer_target_check"] = decoded["producer_exact_check"]
            except BaseException as error:
                result["parse_decode_failure"] = {"type": type(error).__name__, "message": str(error)}
    else:
        result["linux_process_state"] = "UNKNOWN_AFTER_OUTER_GUARD"
    code = receipt["actual_exit_code"]
    result["interpreted_result"] = "SAT_RAW_UNCHECKED" if code == 10 else "UNSAT_TRACE_UNCHECKED" if code == 20 else "UNKNOWN_NATIVE_OR_RESOURCE_OUTCOME"
    result["outputs_sha256"] = {helper.key(path): helper.digest(path) for path in folder.iterdir() if path.is_file()}
    result["limitations"] = ["SAT requires the dedicated independent429779variable/full99 object path; UNSAT requires complete authenticated trace replay.",
                             "A checked UNSAT would exclude only this fixed family, without unrestricted coverage."]
    helper.save(out / "summary.json", result)
    print(json.dumps({"actual_exit_code": code, "interpreted_result": result["interpreted_result"], "research_calls": 1}), flush=True)


def main():
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--preflight", action="store_true")
    modes.add_argument("--research", action="store_true")
    for name in ("out", "propagation-gate", "encoding-gate", "object-gate"):
        parser.add_argument("--" + name, type=Path, required=True)
    for name in ("propagation-gate-sha256", "encoding-gate-sha256", "object-gate-sha256"):
        parser.add_argument("--" + name, required=True)
    run(parser.parse_args())


if __name__ == "__main__":
    main()
