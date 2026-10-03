"""Calibrated, independently gated full99 proof-producing solver orchestration."""
from datetime import datetime, timezone
from hashlib import sha256
import argparse
import json
import multiprocessing
from pathlib import Path
import platform
import subprocess
import sys
import time

from theory_20260930_rook_sat_runner import bounded
from theory_20260930_eight_full99_cnf import decode, package, ResourceCap


ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "acceleration/results/20260930_eight_full99_cnf"
CNF = DIRECTORY / "instance.cnf"
MODEL = DIRECTORY / "model.json"
CNF_SHA = "f247be8432d69f4feec037833a6923ef623e20c0aa0dbdea77fd13ec218d095b"
MODEL_SHA = "f2b7a649e74aa476380e14066239a188a2d2122d2ba1cc6e330e9a094d2cc0ee"
CHECKER = ROOT / "build/rook-drat-checker/drat-trim.exe"
CHECKER_SHA = "23d1613cb0b1ed491f4e723ff82492a8be6c349c2426d440412842c5246b90ac"
PROTOCOL = Path(__file__).with_name("theory_20260930_eight_full99_solver_spec.md")


def digest(path):
    value = sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            value.update(block)
    return value.hexdigest()


def key(path):
    path = Path(path).resolve()
    return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)


def save(path, obj):
    with Path(path).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(obj, stream, indent=2)
        stream.write("\n")


def read(path):
    return json.loads(Path(path).read_text())


def common_manifest(args):
    import pysat
    import pysat.formula
    import pysat.solvers
    import pysolvers
    paths = [Path(__file__), PROTOCOL, CNF, MODEL,
        ROOT / "acceleration/theory_20260930_eight_full99_cnf.py",
        ROOT / "acceleration/theory_20260930_full_srg_validator.py",
        ROOT / "acceleration/theory_20260930_rook_sat_runner.py",
        ROOT / "acceleration/environments/rook-sat/uv.lock",
        ROOT / "acceleration/environments/rook-sat/pyproject.toml",
        CHECKER, ROOT / "build/rook-drat-checker/build_receipt.json",
        ROOT / "build/rook-drat-checker/build_manifest.json",
        Path(pysat.__file__), Path(pysat.formula.__file__), Path(pysat.solvers.__file__), Path(pysolvers.__file__)]
    assert digest(CNF) == CNF_SHA and digest(MODEL) == MODEL_SHA
    assert digest(CHECKER) == CHECKER_SHA
    return {"timestamp": datetime.now(timezone.utc).isoformat(),
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "command": [sys.executable, *sys.argv], "cwd": str(ROOT), "python": platform.python_version(),
        "platform": platform.platform(), "pysat_version": pysat.__version__,
        "native_module_path": str(pysolvers.__file__), "native_module_sha256": digest(pysolvers.__file__),
        "solver": "CaDiCaL195 via pinned python-sat1.9.dev15 native module", "with_proof": True,
        "checker": "drat-trim from source-authenticated separate build; exact provenance in hash-bound build manifest/receipt",
        "input_hashes": {key(p): digest(p) for p in paths},
        "limits": {"research_solver_process_seconds": 300, "research_conflicts": 1000000,
                   "calibration_call_seconds": 30, "post_solver_packaging_seconds": 120},
        "seed": None, "seed_null_reason": "Default solver options; no seed overridden.",
        "scope": "Only the exact120fixedK eight-coordinate full99 family, with2160free edges and prescribed absences.",
        "status": "CANDIDATE_ORCHESTRATION", "external_review": False}


def raw_formula_valid(formula, assignment):
    values = {abs(x): x > 0 for x in assignment}
    return all(any(values.get(abs(x)) == (x > 0) for x in row) for row in formula)


def calibrate(args, manifest):
    records = []
    for name, text, expected in (("sat", "p cnf 2 2\n1 2 0\n-1 2 0\n", "SAT_MODEL_UNCHECKED"),
                                ("unsat", "p cnf 2 4\n1 2 0\n1 -2 0\n-1 2 0\n-1 -2 0\n", "UNSAT_PROOF_UNCHECKED")):
        folder = args.out / name
        folder.mkdir()
        cnf = folder / "instance.cnf"
        cnf.write_text(text, encoding="ascii", newline="\n")
        result = bounded(cnf, folder, 10000, 30)
        save(folder / "receipt.json", result)
        assert result["solver_answer"] == expected
        record = {"name": name, "result": result, "cnf_sha256": digest(cnf)}
        if name == "sat":
            assignment = read(folder / "model.json")["assignment"]
            assert len(assignment) == 2 and {abs(x) for x in assignment} == {1, 2}
            assert raw_formula_valid([[1, 2], [-1, 2]], assignment)
            wrong = [-1, -2]
            assert not raw_formula_valid([[1, 2], [-1, 2]], wrong)
            record["positive_assignment_passed"] = True
            record["corrupt_assignment_rejected"] = wrong
        else:
            (folder / "invalid_empty_only.drat").write_text("0\n", encoding="ascii", newline="\n")
            checks = []
            for label, proof, accepted_expected in (("valid", folder / "proof.drat", True),
                    ("invalid_empty_only", folder / "invalid_empty_only.drat", False)):
                call = [str(CHECKER), str(cnf.resolve()), str(proof.resolve())]
                started = time.monotonic()
                check = subprocess.run(call, cwd=ROOT, capture_output=True, timeout=30)
                log = folder / (label + "_checker.log")
                log.write_bytes(check.stdout + check.stderr)
                accepted = check.returncode == 0 and b"s VERIFIED" in check.stdout + check.stderr
                assert accepted == accepted_expected
                checks.append({"name": label, "command": call, "cwd": str(ROOT),
                    "actual_exit_code": check.returncode, "accepted": accepted,
                    "wall_seconds": time.monotonic() - started, "proof_sha256": digest(proof),
                    "log_sha256": digest(log)})
            record["checker_controls"] = checks
        records.append(record)
    save(args.out / "controls.json", {"timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "PRODUCER_FULL99_SOLVER_CALIBRATION_PASS", "research_solver_calls": 0,
        "orchestrator_sha256": digest(Path(__file__)), "protocol_sha256": digest(PROTOCOL),
        "manifest_sha256": digest(args.out / "manifest.json"), "records": records,
        "actual_worker_exit_codes": [r["result"]["worker_exit_code"] for r in records],
        "independent_review": False, "calibration_is_not_research_verification": True})
    print(json.dumps({"status": "PRODUCER_FULL99_SOLVER_CALIBRATION_PASS", "research_solver_calls": 0,
                      "actual_worker_exit_codes": [r["result"]["worker_exit_code"] for r in records]}), flush=True)


def gate(args):
    assert args.encoding_audit and args.encoding_audit_sha256 and args.calibration
    assert digest(args.encoding_audit) == args.encoding_audit_sha256
    audit = read(args.encoding_audit)
    assert audit["status"] == "INDEPENDENT_EIGHT_FULL99_CNF_ENCODING_PASS"
    bindings = audit["inputs_sha256"]
    normalized = {key(Path(p) if Path(p).is_absolute() else ROOT / p): h for p, h in bindings.items()}
    for path, expected in ((CNF, CNF_SHA), (MODEL, MODEL_SHA)):
        assert normalized[key(path)] == expected == digest(path)
    for path, expected in normalized.items():
        source = Path(path) if Path(path).is_absolute() else ROOT / path
        assert digest(source) == expected, path
    calibration = read(args.calibration)
    assert calibration["status"] == "PRODUCER_FULL99_SOLVER_CALIBRATION_PASS"
    assert calibration["research_solver_calls"] == 0
    assert calibration["orchestrator_sha256"] == digest(Path(__file__))
    assert calibration["protocol_sha256"] == digest(PROTOCOL)
    calibration_manifest = args.calibration.with_name("manifest.json")
    assert digest(calibration_manifest) == calibration["manifest_sha256"]
    for path, expected in read(calibration_manifest)["input_hashes"].items():
        source = Path(path) if Path(path).is_absolute() else ROOT / path
        assert digest(source) == expected, path


def research(args, manifest):
    gate(args)
    folder = args.out / "main"
    folder.mkdir()
    save(folder / "started.json", {"timestamp": datetime.now(timezone.utc).isoformat(),
        "state": "LAUNCHING", "cnf_sha256": CNF_SHA, "model_sha256": MODEL_SHA,
        "encoding_audit": key(args.encoding_audit), "encoding_audit_sha256": digest(args.encoding_audit),
        "calibration": key(args.calibration), "calibration_sha256": digest(args.calibration),
        "solver_process_seconds": 300, "conflicts": 1000000})
    print(json.dumps({"state": "LAUNCHING_PROOF_ENABLED_FULL99_PILOT", "seconds": 300, "conflicts": 1000000}), flush=True)
    result = bounded(CNF, folder, 1000000, 300)
    save(folder / "receipt.json", {"timestamp": datetime.now(timezone.utc).isoformat(), **result,
        "cnf_sha256": CNF_SHA, "model_sha256": MODEL_SHA,
        "actual_process_result_preserved": True, "independent_review_pending": True,
        "scope": manifest["scope"], "target_resolution": False})
    artifacts = []
    candidate = None
    # Raw complete artifacts remain checkable even if the native process failed
    # to deliver a normal post-cleanup receipt. Never rewrite the actual result.
    if (folder / "model.json").exists():
        assignment_path = folder / "model.json"
        artifacts.append(assignment_path)
        try:
            assignment = read(assignment_path)["assignment"]
            decoded = decode(read(MODEL), assignment)
            decoded.update(status="CANDIDATE_TARGET_GRAPH_PENDING_INDEPENDENT_CHECK" if decoded["producer_validation"]["valid"] else "INVALID_PRODUCER_DECODE",
                           assignment_sha256=digest(assignment_path), encoding_model_sha256=MODEL_SHA,
                           actual_worker_answer=result["solver_answer"], independent_review=False)
            graph_path = folder / "decoded_full99.json"
            save(graph_path, decoded)
            artifacts.append(graph_path)
            candidate = decoded["producer_validation"]["valid"]
        except BaseException as exc:
            save(folder / "decode_failure.json", {"type": type(exc).__name__, "message": str(exc),
                 "assignment_sha256": digest(assignment_path), "independent_check_pending": True})
    if (folder / "proof.drat").exists():
        artifacts.append(folder / "proof.drat")
    packages = []
    try:
        packaging_cap = ResourceCap()
        for path in artifacts:
            packages.append(package(path, packaging_cap))
        save(args.out / "artifact_packages.json", {"packages": packages,
             "instruction": "Concatenate ordered gzip parts byte-for-byte, verify compressed hash, decompress and verify raw hash.",
             "raw_artifacts_retained": True})
    except BaseException as exc:
        save(args.out / "packaging_failure.json", {"type": type(exc).__name__, "message": str(exc),
             "raw_artifacts_retained": True, "packages_completed": packages})
    save(args.out / "summary.json", {"timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "CANDIDATE_SOLVER_ARTIFACTS_PENDING_INDEPENDENT_REVIEW", "actual_solver_answer": result["solver_answer"],
        "actual_worker_exit_code": result["worker_exit_code"], "worker_observed_stopped": result["worker_observed_stopped"],
        "solver_process_seconds": result["wall_seconds"], "research_solver_calls": 1,
        "raw_artifacts": {key(p): {"sha256": digest(p), "bytes": p.stat().st_size} for p in artifacts},
        "producer_valid_target_graph": candidate, "producer_valid_target_graph_null_reason": "No complete decodable raw model." if candidate is None else None,
        "independently_verified_target_graph": False, "independently_verified_exclusion": False,
        "scope": manifest["scope"], "overall_search_coverage": "UNKNOWN; no validated unrestricted denominator.",
        "no_solver_process_left_running": True})
    print(json.dumps({"actual_solver_answer": result["solver_answer"], "actual_worker_exit_code": result["worker_exit_code"],
                      "producer_valid_graph": candidate, "raw_artifact_count": len(artifacts)}), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--calibrate", action="store_true")
    parser.add_argument("--calibration", type=Path)
    parser.add_argument("--encoding-audit", type=Path)
    parser.add_argument("--encoding-audit-sha256")
    args = parser.parse_args()
    if not args.calibrate:
        gate(args)
    args.out.mkdir(parents=True, exist_ok=False)
    manifest = common_manifest(args)
    if not args.calibrate:
        manifest["input_hashes"].update({key(args.calibration): digest(args.calibration),
             key(args.encoding_audit): digest(args.encoding_audit)})
    manifest["mode"] = "TINY_CALIBRATION_ONLY" if args.calibrate else "ONE_GATED_RESEARCH_CALL"
    save(args.out / "manifest.json", manifest)
    if args.calibrate:
        calibrate(args, manifest)
    else:
        research(args, manifest)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
