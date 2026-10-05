"""Bounded local SAT / exact Boolean-box Gram loop with independent gates."""
from datetime import datetime, timezone
from hashlib import sha256
import argparse
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

from theory_20260930_rook_sat_worker_v2 import bounded
from theory_20260930_rook_sat_runner import bounded as proof_bounded


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "acceleration/results/20260930_rook_free_internal_sat/instance.cnf"
MODEL = ROOT / "acceleration/results/20260930_rook_free_internal_sat/model.json"
ENCODING_AUDIT = ROOT / "acceleration/results/20260930_rook_free_internal_sat/independent_cnf_encoding.json"
ENCODING_AUDIT_SHA = "a74e821f70680187e0ee14fb956d51928e6aa9517acc1bc0186448b32c985ba0"
INITIAL_CHECKPOINT = ROOT / "acceleration/results/20260930_rook_box_batch01/accepted_checkpoint.json"
INITIAL_GATE = ROOT / "acceleration/results/20260930_independent_review/rook_box_collection01.json"
SAT_CHECKER = ROOT / "acceleration/audit_20260930_rook_box_augmented_sat_v1.py"
CUT_CHECKER = ROOT / "acceleration/audit_20260930_gram_box_nogood_v1.py"
SUPPORT_CHECKER = ROOT / "acceleration/audit_20260930_gram_nogood_v1.py"
BOX_PRODUCER = ROOT / "acceleration/theory_20260930_rook_gram_box_cut.py"
GRAM = ROOT / "acceleration/theory_20260930_rook_gram_falsifier.py"
MINIMIZE = ROOT / "acceleration/theory_20260930_rook_gram_minimize.py"
ROOT_PYTHON = ROOT / "build/research-venv/Scripts/python.exe"


def digest(p):
    return sha256(Path(p).read_bytes()).hexdigest()


def key(p):
    p = Path(p).resolve()
    return p.relative_to(ROOT).as_posix() if p.is_relative_to(ROOT) else p.as_posix()


def save(p, data):
    with Path(p).open("x", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def read(p):
    return json.loads(Path(p).read_text())


def cut_record(certificate_path, audit_path):
    certificate, audit = read(certificate_path), read(audit_path)
    assert audit["status"] == "INDEPENDENT_TARGET_GRAM_BOX_NOGOOD_PASS"
    assert audit["certificate_sha256"] == digest(certificate_path)
    assert audit["base_cnf_sha256"] == digest(BASE)
    assert audit["encoding_model_sha256"] == digest(MODEL)
    assert audit["verified_clause"] == certificate["nogood_clause"]
    return {"certificate": key(certificate_path), "certificate_sha256": digest(certificate_path),
            "audit": key(audit_path), "audit_sha256": digest(audit_path), "clause": audit["verified_clause"]}


def materialize(path, cuts):
    with BASE.open("rb") as source, path.open("xb") as output:
        header = source.readline().decode("ascii").split()
        assert header == ["p", "cnf", "30420", "3689820"]
        output.write(f"p cnf 30420 {3689820 + len(cuts)}\n".encode("ascii"))
        for block in iter(lambda: source.read(1024 * 1024), b""):
            output.write(block)
        for record in cuts:
            output.write((" ".join(map(str, record["clause"])) + " 0\n").encode("ascii"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--resume", type=Path)
    args = parser.parse_args()
    args.out = args.out.resolve()
    args.out.mkdir(parents=True, exist_ok=False)
    assert digest(BASE) == "ed9d0e102b16481fdbcecef34240b5be2b8a357af8c219606bb688dcb5fe9403"
    assert digest(ENCODING_AUDIT) == ENCODING_AUDIT_SHA
    assert digest(INITIAL_GATE) == "b5a8ab884c157f40b32a4ebacf747e0d12596b0fb0ca01d3203fafd9dcf21cfd"
    gate = read(INITIAL_GATE)
    assert gate["status"] == "INDEPENDENT_TARGET_GRAM_BOX_COLLECTION_PASS"
    assert gate["inputs_sha256"][key(INITIAL_CHECKPOINT)] == digest(INITIAL_CHECKPOINT)
    previous = read(args.resume or INITIAL_CHECKPOINT)
    cuts = [cut_record(ROOT / row["certificate"], ROOT / row["audit"]) for row in previous["ordered_cuts"]]
    assert cuts == previous["ordered_cuts"]
    import pysat
    import pysolvers
    source_files = [Path(__file__), ROOT / "acceleration/theory_20260930_rook_sat_runner.py",
        ROOT / "acceleration/theory_20260930_rook_sat_worker_v2.py",
        ROOT / "acceleration/theory_20260930_rook_box_lazy_loop_spec.md", GRAM, MINIMIZE, SAT_CHECKER, CUT_CHECKER,
        SUPPORT_CHECKER, BOX_PRODUCER,
        ROOT / "acceleration/audit_20260930_rook_free_internal_cnf_v1.py",
        ROOT / "acceleration/audit_20260930_rook_free_internal_certificate_v1.py",
        ROOT / "acceleration/environments/rook-sat/uv.lock", ROOT / "acceleration/environments/rook-sat/pyproject.toml",
        ROOT / "acceleration/results/20260930_rook_solver_v2_calibration/controls.json",
        ROOT / "acceleration/results/20260930_rook_box_checker_controls/summary.json",
        BASE, MODEL, ENCODING_AUDIT, INITIAL_CHECKPOINT, INITIAL_GATE]
    if args.resume:
        source_files.append(args.resume)
    save(args.out / "manifest.json", {"timestamp": datetime.now(timezone.utc).isoformat(),
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "command": [sys.executable, *sys.argv], "cwd": str(ROOT), "python": platform.python_version(),
        "pysat_version": pysat.__version__, "native_module_path": pysolvers.__file__,
        "native_module_sha256": digest(pysolvers.__file__), "input_hashes": {key(p): digest(p) for p in source_files},
        "scope": "One exact central-factor star, with 780 free right-cell edges and independently checked necessary Gram Boolean-box nogoods.",
        "question": "Do repeated stronger Boolean-box Gram cuts exclude the fixed-star local model or leave a local Gram survivor?",
        "selection_rule": "Fresh deterministic-default CaDiCaL195 model at each exact base-plus-ordered-cut CNF; greedy support reduction then exact maximizing-box literal removal for each negative G direction.",
        "solver_configuration_change": "with_proof=False for SAT seeking; any UNSAT answer triggers a fresh with_proof=True replay on the identical CNF within the same remaining budget. Both calls count. No unproved UNSAT promotion.",
        "limits": {"solver_rounds": 10, "cumulative_solver_process_seconds": 180, "per_round_seconds": 60,
                   "per_round_conflicts": 1000000, "overall_seconds": 600},
        "success_criteria": "Only independently checked localSAT/cut records are used; UNSAT requires separate proof replay before promotion.",
        "stop_criteria": "UNKNOWN/error/verifier veto, uncheckedUNSAT, localGram survivor, unsupportedGram obstruction, or budget.",
        "status": "CANDIDATE", "self_promotion": False, "independent_code_execution_is_not_external_review": True})
    started = time.monotonic()
    consumed = 0.0
    records = []
    counters = {"solver_rounds": 0, "proof_replay_calls": 0, "unproved_unsat_answers": 0,
                "independent_local_sat_passes": 0, "negative_gram_windows": 0,
                "new_independently_checked_cuts": 0, "unchecked_unsat_proofs": 0, "unknown_solver_results": 0}
    stop_reason = "ROUND_CAP"
    def checkpoint(number, state):
        save(args.out / f"checkpoint_{number:02d}.json", {"timestamp": datetime.now(timezone.utc).isoformat(),
             "state": state, "ordered_cuts": cuts, "counters": counters.copy(), "round_records": records.copy(),
             "cumulative_solver_process_seconds": consumed, "overall_seconds": time.monotonic() - started,
             "resume_note": "Supply this file to --resume with a fresh output directory for a separately budgeted wave. No solver stack is preserved."})
    def command(command, out, seconds=120):
        remaining = 600 - (time.monotonic() - started)
        if remaining <= 1:
            raise TimeoutError("overall wave limit")
        call_start = time.monotonic()
        try:
            run = subprocess.run([str(x) for x in command], cwd=ROOT, capture_output=True, timeout=min(seconds, remaining))
            code = run.returncode
            stdout, stderr = run.stdout, run.stderr
        except subprocess.TimeoutExpired as exc:
            code, stdout, stderr = None, exc.stdout or b"", exc.stderr or b""
        out.with_suffix(".stdout.log").write_bytes(stdout)
        out.with_suffix(".stderr.log").write_bytes(stderr)
        save(out.with_suffix(".receipt.json"), {"command": [str(x) for x in command], "working_directory": str(ROOT),
             "exit_code": code, "wall_seconds": time.monotonic() - call_start,
             "stdout_sha256": digest(out.with_suffix(".stdout.log")), "stderr_sha256": digest(out.with_suffix(".stderr.log"))})
        if code != 0:
            raise RuntimeError(f"subprocess failure or timeout; exit={code}: {command[1]}")
    checkpoint(0, "READY_WITH_NINE_INDEPENDENT_BOX_CUTS" if not args.resume else "READY_FROM_CHECKED_BOX_CUT_CHECKPOINT")
    try:
        for round_index in range(1, 11):
            if consumed >= 178:
                stop_reason = "CUMULATIVE_SOLVER_TIME_CAP"
                break
            if time.monotonic() - started >= 598:
                stop_reason = "OVERALL_WALL_CAP"
                break
            folder = args.out / f"round_{round_index:02d}"
            folder.mkdir()
            cnf = folder / "instance.cnf"
            materialize(cnf, cuts)
            cut_path = folder / "ordered_cuts.json"
            save(cut_path, cuts)
            record = {"round": round_index, "cnf": key(cnf), "cnf_sha256": digest(cnf),
                      "ordered_cuts": key(cut_path), "ordered_cuts_sha256": digest(cut_path),
                      "variables": 30420, "clauses": 3689820 + len(cuts), "mathematical_cuts": len(cuts)}
            save(folder / "instance_record.json", record)
            solver_out = folder / "solver"
            solver_out.mkdir()
            print(json.dumps({"round": round_index, "state": "SOLVER_LAUNCHING", "cuts": len(cuts)}), flush=True)
            limit = min(60, 180 - consumed - 1, 600 - (time.monotonic() - started) - 1)
            if limit <= 0:
                stop_reason = "RESOURCE_CAP_BEFORE_SOLVER"
                break
            answer = bounded(cnf, solver_out, 1000000, limit)
            consumed += answer["wall_seconds"]
            counters["solver_rounds"] += 1
            save(solver_out / "receipt.json", {"timestamp": datetime.now(timezone.utc).isoformat(), **answer,
                 "cnf_sha256": record["cnf_sha256"], "scope": "Exact augmented local-window CNF; mathematical status is unapproved."})
            record["solver_answer"] = answer["solver_answer"]
            records.append(record)
            if answer["solver_answer"] == "UNSAT_NO_PROOF":
                counters["unproved_unsat_answers"] += 1
                replay_limit = min(60, 180 - consumed - 1, 600 - (time.monotonic() - started) - 1)
                stop_reason = "UNSAT_UNPROVEN_NO_REPLAY_BUDGET"
                if replay_limit > 1:
                    replay_out = folder / "proof_replay"
                    replay_out.mkdir()
                    replay = proof_bounded(cnf, replay_out, 1000000, replay_limit)
                    consumed += replay["wall_seconds"]
                    counters["proof_replay_calls"] += 1
                    save(replay_out / "receipt.json", {"timestamp": datetime.now(timezone.utc).isoformat(), **replay,
                         "cnf_sha256": record["cnf_sha256"], "scope": "Identical augmented local-window CNF replay; proof remains unapproved."})
                    record["proof_replay_answer"] = replay["solver_answer"]
                    if replay["solver_answer"] == "UNSAT_PROOF_UNCHECKED":
                        counters["unchecked_unsat_proofs"] += 1
                        stop_reason = "UNSAT_PROOF_PENDING_INDEPENDENT_REPLAY"
                    elif replay["solver_answer"] == "SAT_MODEL_UNCHECKED":
                        stop_reason = "INCONSISTENT_SOLVER_ANSWERS"
                    else:
                        stop_reason = "UNSAT_UNPROVEN_REPLAY_INCOMPLETE"
                checkpoint(round_index, stop_reason)
                break
            if answer["solver_answer"] != "SAT_MODEL_UNCHECKED":
                counters["unknown_solver_results"] += 1
                stop_reason = "UNKNOWN_SOLVER_RESULT"
                checkpoint(round_index, stop_reason)
                break
            sat_out = folder / "independent_sat"
            command([ROOT_PYTHON, SAT_CHECKER, "--base-cnf", BASE, "--augmented-cnf", cnf, "--model", MODEL,
                     "--assignment", solver_out / "model.json", "--ordered-cuts", cut_path,
                     "--encoding-audit", ENCODING_AUDIT, "--encoding-audit-sha256", ENCODING_AUDIT_SHA,
                     "--out", sat_out], folder / "sat_check", seconds=120)
            sat_report = read(sat_out / "summary.json")
            assert sat_report["status"] == "INDEPENDENT_BOX_AUGMENTED_ROOK_WINDOW_SAT_PASS"
            counters["independent_local_sat_passes"] += 1
            graph = sat_out / "independent_full59.json"
            record.update(sat_audit=key(sat_out / "summary.json"), sat_audit_sha256=digest(sat_out / "summary.json"),
                          graph=key(graph), graph_sha256=digest(graph))
            gram_out = folder / "gram"
            command([sys.executable, GRAM, "--input", graph, "--out", gram_out], folder / "gram_run")
            gram = read(gram_out / "result.json")
            negative = next(row["result"] for row in gram["tests"] if row["matrix"] == "27I-9A+J")
            if negative["psd"]:
                stop_reason = "GRAM_OBSTRUCTION_REQUIRES_NEW_CUT_KIND" if gram["extension_obstruction_candidate"] else "LOCAL_GRAM_SURVIVOR"
                checkpoint(round_index, stop_reason)
                break
            counters["negative_gram_windows"] += 1
            minimized = folder / "minimized"
            command([sys.executable, MINIMIZE, "--graph", graph, "--certificate", gram_out / "result.json",
                     "--encoding-model", MODEL, "--cnf", BASE, "--out", minimized], folder / "minimize_run")
            support_certificate = minimized / "certificate.json"
            support_audit = folder / "independent_support_nogood.json"
            command([ROOT_PYTHON, SUPPORT_CHECKER, "--graph", graph, "--certificate", support_certificate, "--model", MODEL,
                     "--cnf", BASE, "--encoding-audit", ENCODING_AUDIT, "--encoding-audit-sha256", ENCODING_AUDIT_SHA,
                     "--out", support_audit, "--clause", minimized / "nogood.clause"], folder / "support_cut_check")
            box_out = folder / "boxed"
            command([sys.executable, BOX_PRODUCER, "--certificate", support_certificate,
                     "--prior-audit", support_audit, "--out", box_out], folder / "box_producer")
            certificate = box_out / "certificate.json"
            cut_audit = folder / "independent_box_nogood.json"
            command([ROOT_PYTHON, CUT_CHECKER, "--graph", graph, "--certificate", certificate, "--model", MODEL,
                     "--cnf", BASE, "--encoding-audit", ENCODING_AUDIT, "--encoding-audit-sha256", ENCODING_AUDIT_SHA,
                     "--out", cut_audit, "--clause", box_out / "nogood.clause"], folder / "box_cut_check")
            addition = cut_record(certificate, cut_audit)
            assert set(addition["clause"]) not in [set(old["clause"]) for old in cuts]
            cuts.append(addition)
            counters["new_independently_checked_cuts"] += 1
            record.update(sat_audit=key(sat_out / "summary.json"), sat_audit_sha256=digest(sat_out / "summary.json"),
                          graph=key(graph), graph_sha256=digest(graph), next_cut_audit=key(cut_audit),
                          next_cut_audit_sha256=digest(cut_audit), next_cut_literals=len(addition["clause"]))
            checkpoint(round_index, "READY_WITH_NEXT_INDEPENDENT_CUT")
            print(json.dumps({"round": round_index, "state": "LOCAL_SAT_FALSIFIED_CUT_CHECKED",
                              "new_cut_literals": len(addition["clause"]), "cumulative_solver_seconds": consumed}), flush=True)
    except BaseException as exc:
        stop_reason = "VERIFIER_VETO_OR_EXECUTION_ERROR"
        save(args.out / "failure.json", {"timestamp": datetime.now(timezone.utc).isoformat(),
             "type": type(exc).__name__, "message": str(exc), "completed_counters": counters})
        checkpoint(99, stop_reason)
    save(args.out / "final_checkpoint.json", {"timestamp": datetime.now(timezone.utc).isoformat(),
         "state": stop_reason, "ordered_cuts": cuts, "counters": counters, "round_records": records,
         "cumulative_solver_process_seconds": consumed, "overall_seconds": time.monotonic() - started,
         "resume_note": "A fresh output plus --resume this file starts a separately budgeted wave from all accepted cuts; no live process/solver stack is implied."})
    save(args.out / "summary.json", {"timestamp": datetime.now(timezone.utc).isoformat(), "status": "CANDIDATE_RECORDS_PENDING_ROOT_REVIEW",
         "stop_reason": stop_reason, "counts": counters, "initial_cuts": len(cuts) - counters["new_independently_checked_cuts"],
         "accepted_cuts_at_end": len(cuts), "cumulative_solver_process_seconds": consumed,
         "overall_seconds": time.monotonic() - started, "target_graph": False, "target_nonexistence": False,
         "coverage": "UNKNOWN; one fixed-central-star model only; no target-wide denominator.",
         "no_research_process_left_by_this_script": True})
    print(json.dumps({"stop_reason": stop_reason, "counts": counters, "accepted_cuts": len(cuts), "solver_seconds": consumed}), flush=True)


if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()
    main()
