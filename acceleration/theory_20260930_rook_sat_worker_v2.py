"""SAT-seeking worker without proof logging; exact UNSAT proof replay stays separate."""
from datetime import datetime, timezone
from hashlib import sha256
import argparse
import json
import multiprocessing as mp
from pathlib import Path
import platform
import subprocess
import sys
import time

from theory_20260930_rook_sat_runner import bounded as proof_bounded


def digest(p):
    return sha256(Path(p).read_bytes()).hexdigest()


def save(p, data):
    with Path(p).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(data, stream, indent=2)
        stream.write("\n")


def worker(cnf, out, conflicts, sender):
    out = Path(out)
    start = time.monotonic()
    try:
        import pysat
        from pysat.formula import CNF
        from pysat.solvers import Solver
        formula = CNF(from_file=cnf)
        parsed = time.monotonic()
        with Solver(name="cadical195", bootstrap_with=formula.clauses, with_proof=False) as solver:
            loaded = time.monotonic()
            solver.conf_budget(conflicts)
            answer = solver.solve_limited()
            solved = time.monotonic()
            stats = solver.accum_stats()
            if answer is True:
                save(out / "model.json", {"assignment": solver.get_model()})
        result = {"solver_answer": "SAT_MODEL_UNCHECKED" if answer is True else "UNSAT_NO_PROOF" if answer is False else "UNKNOWN_CONFLICT_CAP",
                  "engine": "cadical195", "pysat_version": pysat.__version__, "with_proof": False,
                  "variables": formula.nv, "clauses": len(formula.clauses), "stats": stats,
                  "parse_seconds": parsed - start, "load_seconds": loaded - parsed, "solve_seconds": solved - loaded,
                  "proof_artifact": None, "proof_artifact_null_reason": "Proof-disabled SAT-seeking invocation; an UNSAT answer needs a separate proof-producing replay."}
        save(out / "worker_result.json", result)
        sender.send(result)
    except BaseException as exc:
        result = {"solver_answer": "UNKNOWN_WORKER_ERROR", "error_type": type(exc).__name__, "message": str(exc), "with_proof": False}
        save(out / "worker_error.json", result)
        sender.send(result)
    finally:
        sender.close()


def bounded(cnf, out, conflicts, seconds):
    context = mp.get_context("spawn")
    receiver, sender = context.Pipe(duplex=False)
    process = context.Process(target=worker, args=(str(Path(cnf).resolve()), str(Path(out).resolve()), conflicts, sender))
    start = time.monotonic()
    process.start()
    sender.close()
    result = None
    terminated_after_result = False
    try:
        if receiver.poll(max(0, seconds - (time.monotonic() - start))):
            try:
                result = receiver.recv()
            except EOFError:
                result = {"solver_answer": "UNKNOWN_WORKER_EOF"}
        else:
            result = {"solver_answer": "UNKNOWN_WALL_CAP"}
    finally:
        if result and result["solver_answer"] != "UNKNOWN_WALL_CAP":
            process.join(max(0, min(5, seconds - (time.monotonic() - start))))
        if process.is_alive():
            terminated_after_result = bool(result and result["solver_answer"] != "UNKNOWN_WALL_CAP")
            process.terminate()
        process.join(5)
        if process.is_alive():
            process.kill()
            process.join(5)
        assert not process.is_alive()
        result = result or {"solver_answer": "UNKNOWN_PARENT_INTERRUPTION"}
        result.update(worker_exit_code=process.exitcode, worker_observed_stopped=True,
                      parent_terminated_after_complete_result=terminated_after_result,
                      wall_seconds=time.monotonic() - start, wall_limit_seconds=seconds, conflict_limit=conflicts)
        receiver.close()
        process.close()
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    checker = Path("build/rook-drat-checker/drat-trim.exe").resolve()
    save(args.out / "manifest.json", {"timestamp": datetime.now(timezone.utc).isoformat(),
         "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
         "command": [sys.executable, *sys.argv], "cwd": str(Path.cwd()), "python": platform.python_version(),
         "input_hashes": {str(p): digest(p) for p in (Path(__file__), Path("acceleration/theory_20260930_rook_sat_runner.py"),
             Path("acceleration/environments/rook-sat/uv.lock"), checker, Path("build/rook-drat-checker/build_receipt.json"))},
         "question": "Calibrate proof-disabled SAT/UNSAT output and a separate complete-proof replay before the new boxed-cut wave.",
         "scope": "Small solver plumbing controls only; no performance guarantee or family exclusion.",
         "limits": {"per_control_seconds": 30, "per_control_conflicts": 10000},
         "configuration_change": "SAT-seeking calls with_proof=False and up-to-five-second normal exit grace; prior frozen worker unchanged.",
         "status": "CANDIDATE_ENGINEERING_CALIBRATION"})
    records = []
    for name, text, expected in (("sat", "p cnf 2 2\n1 2 0\n-1 2 0\n", "SAT_MODEL_UNCHECKED"),
                                 ("unsat", "p cnf 2 4\n1 2 0\n1 -2 0\n-1 2 0\n-1 -2 0\n", "UNSAT_NO_PROOF")):
        folder = args.out / name
        folder.mkdir()
        cnf = folder / "instance.cnf"
        cnf.write_text(text, encoding="ascii", newline="\n")
        result = bounded(cnf, folder, 10000, 30)
        assert result["solver_answer"] == expected
        if name == "sat":
            assignment = set(json.loads((folder / "model.json").read_text())["assignment"])
            assert any(x in assignment for x in (1, 2)) and any(x in assignment for x in (-1, 2))
        records.append({"name": name, **result})
    replay = args.out / "unsat_proof_replay"
    replay.mkdir()
    proof_result = proof_bounded(args.out / "unsat/instance.cnf", replay, 10000, 30)
    assert proof_result["solver_answer"] == "UNSAT_PROOF_UNCHECKED"
    call = [str(checker), str((args.out / "unsat/instance.cnf").resolve()), str((replay / "proof.drat").resolve())]
    checked = subprocess.run(call, capture_output=True, timeout=30)
    (replay / "checker.log").write_bytes(checked.stdout + checked.stderr)
    assert checked.returncode == 0 and b"s VERIFIED" in checked.stdout + checked.stderr
    records.append({"name": "separate_proof_replay", **proof_result, "checker_command": call,
                    "checker_exit_code": checked.returncode, "checker_log_sha256": digest(replay / "checker.log")})
    save(args.out / "controls.json", {"status": "PRODUCER_CALIBRATION_PASS", "records": records,
         "mathematical_verification_of_research_result": False, "independent_review_pending": True})
    print(json.dumps({"status": "PRODUCER_CALIBRATION_PASS", "actual_worker_exit_codes": [row["worker_exit_code"] for row in records]}))


if __name__ == "__main__":
    mp.freeze_support()
    main()
