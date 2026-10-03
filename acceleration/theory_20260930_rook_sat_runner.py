"""Proof-preserving bounded CaDiCaL195 pilot; all solver conclusions unapproved."""
from datetime import datetime, timezone
from hashlib import sha256
import argparse
import ctypes
import json
import multiprocessing as mp
import os
from pathlib import Path
import platform
import subprocess
import sys
import time


def digest(p):
    return sha256(p.read_bytes()).hexdigest()


def save(p, data):
    with p.open("x", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def solve_worker(cnf, out, conflicts, sender):
    start = time.monotonic()
    out = Path(out)
    try:
        import pysat
        import pysat.solvers as solver_module
        from pysat.formula import CNF
        from pysat.solvers import Solver
        formula = CNF(from_file=cnf)
        parsed = time.monotonic()
        with Solver(name="cadical195", bootstrap_with=formula.clauses, with_proof=True) as solver:
            loaded = time.monotonic()
            solver.conf_budget(conflicts)
            answer = solver.solve_limited()
            solved = time.monotonic()
            stats = solver.accum_stats()
            record = {"solver_answer": "SAT_MODEL_UNCHECKED" if answer is True else "UNSAT_PROOF_UNCHECKED" if answer is False else "UNKNOWN_CONFLICT_CAP",
                      "pysat_version": pysat.__version__, "engine": "cadical195", "variables": formula.nv,
                      "clauses": len(formula.clauses), "stats": stats, "parse_seconds": parsed - start,
                      "load_seconds": loaded - parsed, "solve_seconds": solved - loaded}
            if answer is True:
                save(out / "model.json", {"assignment": solver.get_model()})
            elif answer is False:
                # Windows-native proof streams must be finalized before read;
                # this procedure follows the repository's preserved runner.
                engine = solver.solver
                if ctypes.CDLL("ucrtbase.dll" if os.name == "nt" else None).fflush(None) != 0:
                    raise RuntimeError("C stdio flush failed")
                solver_module.pysolvers.cadical195_del(engine.cadical, engine.prfile)
                engine.cadical = None
                engine.prfile.seek(0)
                native = engine.prfile.read()
                lines = Solver._proof_bin2text(bytearray(native))
                engine.prfile.close()
                engine.prfile = None
                if not isinstance(lines, list) or not all(isinstance(line, str) for line in lines):
                    raise RuntimeError("native proof conversion did not return text lines")
                with (out / "proof.drat").open("x", encoding="ascii", newline="\n") as f:
                    for line in lines:
                        f.write(line + "\n")
                record.update(proof_lines=len(lines), proof_sha256=digest(out / "proof.drat"),
                              proof_stream_finalized=True, synthesized_empty_clause=False)
        save(out / "worker_result.json", record)
        sender.send(record)
    except BaseException as exc:
        record = {"solver_answer": "UNKNOWN_WORKER_ERROR", "error_type": type(exc).__name__, "message": str(exc)}
        save(out / "worker_error.json", record)
        sender.send(record)
    finally:
        sender.close()


def bounded(cnf, out, conflicts, seconds):
    context = mp.get_context("spawn")
    receiver, sender = context.Pipe(duplex=False)
    process = context.Process(target=solve_worker, args=(str(cnf.resolve()), str(out.resolve()), conflicts, sender))
    start = time.monotonic()
    process.start()
    sender.close()
    result = None
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
            process.join(0.2)
        if process.is_alive():
            process.terminate()
        process.join(5)
        if process.is_alive():
            process.kill()
            process.join(5)
        if process.is_alive():
            raise RuntimeError("worker did not stop")
        if result is None:
            result = {"solver_answer": "UNKNOWN_PARENT_INTERRUPTION"}
        result.update(worker_exit_code=process.exitcode, worker_observed_stopped=True,
                      wall_seconds=time.monotonic() - start, wall_limit_seconds=seconds, conflict_limit=conflicts)
        receiver.close()
        process.close()
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--cnf", type=Path)
    parser.add_argument("--encoding-model", type=Path)
    parser.add_argument("--audit", type=Path)
    parser.add_argument("--calibration-only", action="store_true")
    args = parser.parse_args()
    if not args.calibration_only and not all((args.cnf, args.encoding_model, args.audit)):
        parser.error("main pilot requires --cnf, --encoding-model, and independent --audit")
    import pysat
    import pysolvers
    args.out.mkdir(parents=True, exist_ok=False)
    base = [Path(__file__), Path("acceleration/environments/rook-sat/uv.lock"),
            Path("acceleration/environments/rook-sat/pyproject.toml"), Path("tools/drat-trim/drat-trim.exe"), Path("tools/drat-trim/drat-trim.c")]
    if not args.calibration_only:
        base.extend((args.cnf, args.encoding_model, args.audit))
    save(args.out / "manifest.json", {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "command": [sys.executable, *sys.argv], "cwd": str(Path.cwd()), "python": platform.python_version(),
        "pysat_version": pysat.__version__, "native_module_path": pysolvers.__file__,
        "native_module_sha256": digest(Path(pysolvers.__file__)),
        "input_hashes": {p.as_posix(): digest(p) for p in base},
        "scope": "Solver/proof producer only; main CNF is a fixed-star local rook window, not target-level nonexistence.",
        "question": "Can CaDiCaL195 resolve the independently reviewed fixed-star local CNF within the predeclared cap?",
        "resource_limits": {"main_wall_seconds_including_parse_load_proof": 300, "main_conflicts": 1000000,
                            "per_calibration_wall_seconds": 30},
        "success_criteria": "SAT requires independent decoded-window checking; UNSAT requires independent encoding and raw DRAT replay before promotion.",
        "falsification_criteria": "Reject broken SAT/UNSAT controls and require rejection of a deliberately invalid empty-only proof.",
        "solver_seed": None, "solver_seed_reason": "Default engine configuration; no seed option changed.",
        "status": "CANDIDATE", "independent_review_pending": True,
    })
    cases = [("sat", "p cnf 2 2\n1 2 0\n-1 2 0\n", "SAT_MODEL_UNCHECKED"),
             ("unsat", "p cnf 2 4\n1 2 0\n1 -2 0\n-1 2 0\n-1 -2 0\n", "UNSAT_PROOF_UNCHECKED")]
    controls = []
    checker = Path("tools/drat-trim/drat-trim.exe").resolve()
    for name, cnf_text, expected in cases:
        out = args.out / ("control_" + name)
        out.mkdir()
        (out / "instance.cnf").write_text(cnf_text, encoding="ascii", newline="\n")
        result = bounded(out / "instance.cnf", out, 10000, 30)
        assert result["solver_answer"] == expected, result
        if name == "sat":
            assignment = set(json.loads((out / "model.json").read_text())["assignment"])
            assert (1 in assignment or 2 in assignment) and (-1 in assignment or 2 in assignment)
        else:
            for label, proof in (("valid", out / "proof.drat"), ("corrupt", out / "corrupt.drat")):
                if label == "corrupt":
                    proof.write_text("0\n", encoding="ascii", newline="\n")
                call = [str(checker), str((out / "instance.cnf").resolve()), str(proof.resolve())]
                run = subprocess.run(call, capture_output=True, timeout=30)
                (out / (label + "_checker.log")).write_bytes(run.stdout + run.stderr)
                accepted = b"s VERIFIED" in run.stdout + run.stderr
                assert accepted == (label == "valid"), {"label": label, "code": run.returncode}
                result[label + "_checker"] = {"command": call, "exit_code": run.returncode, "accepted": accepted,
                                                 "log_sha256": digest(out / (label + "_checker.log"))}
        controls.append({"name": name, **result})
    save(args.out / "controls.json", controls)
    if args.calibration_only:
        print(json.dumps({"calibration": "PASS", "main_launched": False}))
        return
    out = args.out / "main"
    out.mkdir()
    save(out / "started.json", {"timestamp": datetime.now(timezone.utc).isoformat(), "cnf_sha256": digest(args.cnf),
         "audit_sha256": digest(args.audit), "gate": "Independent audit supplied and recorded; orchestration must assess its exact scope.",
         "state": "LAUNCHING"})
    result = bounded(args.cnf, out, 1000000, 300)
    if result["solver_answer"] == "SAT_MODEL_UNCHECKED":
        model = json.loads(args.encoding_model.read_text())
        selected = set(json.loads((out / "model.json").read_text())["assignment"])
        graph = [row.copy() for row in model["known_adjacency"]]
        for entry in model["edge_variables"]:
            u, v = entry["u"], entry["v"]
            graph[u][v] = graph[v][u] = int(entry["id"] in selected)
        save(out / "decoded_local_adjacency.json", {"adjacency": graph,
             "cell_rook_coordinates": model["cell_rook_coordinates"], "status": "UNVERIFIED_LOCAL_WINDOW"})
    save(out / "receipt.json", {"timestamp": datetime.now(timezone.utc).isoformat(), **result,
         "cnf_sha256": digest(args.cnf), "scope": "Only the exact fixed-star local-window CNF.",
         "independent_review_pending": True, "target_graph": False, "target_nonexistence": False})
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    mp.freeze_support()
    main()
