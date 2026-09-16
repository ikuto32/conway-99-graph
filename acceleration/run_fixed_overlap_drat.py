"""New bounded proof-producing CaDiCaL195 runner; no UNSAT claim without DRAT.

Preserves the earlier SAT runner and reuses only its frozen input preflight.
SAT output remains unvalidated here. Conflict/time caps give UNKNOWN.
"""
import argparse
import ctypes
import json
import multiprocessing as mp
from math import isfinite
import os
from pathlib import Path
import sys
import time

from run_fixed_overlap_sat import ROOT, DEPS, require, resolve, key, digest, save, preflight


def proof_worker(cnf_path, proof_path, conflicts, sender):
    started = time.monotonic()
    try:
        sys.path.insert(0, str(DEPS))
        import pysat
        import pysat.solvers as solver_module
        from pysat.formula import CNF
        from pysat.solvers import Solver
        formula = CNF(from_file=str(cnf_path))
        parsed = time.monotonic()
        with Solver(name='cadical195', bootstrap_with=formula.clauses, with_proof=True) as solver:
            loaded = time.monotonic()
            solver.conf_budget(conflicts)
            answer = solver.solve_limited()
            solved = time.monotonic()
            stats = solver.accum_stats()
            lines = None
            if answer is False:
                # On this pinned Windows PySAT build public get_proof reads
                # before native C stdio is flushed. Finalize the native solver
                # while keeping its Python proof handle open, as in the existing
                # scratch_root_exact_cnf_drup.py. Never synthesize an empty clause.
                engine = solver.solver
                flush = ctypes.CDLL('ucrtbase.dll' if os.name == 'nt' else None).fflush(None)
                require(flush == 0, 'C proof-stream flush failed')
                solver_module.pysolvers.cadical195_del(engine.cadical, engine.prfile)
                engine.cadical = None
                engine.prfile.seek(0)
                raw_proof = engine.prfile.read()
                lines = Solver._proof_bin2text(bytearray(raw_proof))
                engine.prfile.close()
                engine.prfile = None
                require(type(lines) is list and all(type(line) is str for line in lines), 'Missing proof log')
                with Path(proof_path).open('x', encoding='ascii', newline='\n') as stream:
                    for line in lines:
                        stream.write(line+'\n')
        sender.send(dict(solver_result='UNSAT_PROOF_UNCHECKED' if answer is False else 'SAT_MODEL_UNVALIDATED' if answer is True else 'UNKNOWN',
                         proof_created=answer is False, proof_lines=len(lines) if lines is not None else 0,
                         native_proof_finalized_before_read=answer is False, terminal_empty_clause_synthesized=False,
                         declared_variables=formula.nv, clauses=len(formula.clauses), stats=stats,
                         pysat_version=pysat.__version__, parse_seconds=parsed-started,
                         load_seconds=loaded-parsed, solve_seconds=solved-loaded))
    except BaseException as exc:
        sender.send(dict(solver_result='UNKNOWN', reason='PROOF_WORKER_ERROR', error_type=type(exc).__name__, message=str(exc)))
    finally:
        sender.close()


def produce_bounded(cnf, proof, conflicts, seconds):
    require(not resolve(proof).exists(), 'Preserve existing proof')
    require(type(conflicts) is int and 0 < conflicts <= 2**31-1 and type(seconds) in (int, float)
            and isfinite(seconds) and seconds > 0, 'Positive finite limits required')
    context = mp.get_context('spawn')
    receiver, sender = context.Pipe(duplex=False)
    process = context.Process(target=proof_worker, args=(str(resolve(cnf)), str(resolve(proof)), conflicts, sender))
    started = time.monotonic()
    process.start(); sender.close()
    result = None
    try:
        if receiver.poll(max(0, seconds-(time.monotonic()-started))):
            try:
                result = receiver.recv()
            except EOFError:
                result = dict(solver_result='UNKNOWN', reason='WORKER_EXIT_WITHOUT_RESULT')
        else:
            result = dict(solver_result='UNKNOWN', reason='WALL_TIME_LIMIT_INCLUDING_PARSE_LOAD_PROOF')
    finally:
        if result is not None and not result.get('reason', '').startswith('WALL_TIME_LIMIT'):
            process.join(.2)
        if process.is_alive():
            process.terminate()
        process.join(5)
        if process.is_alive():
            process.kill(); process.join(5)
        require(not process.is_alive(), 'Proof worker could not be stopped')
        result = result or dict(solver_result='UNKNOWN', reason='PARENT_INTERRUPTED')
        result.update(worker_exit_code=process.exitcode, conflict_budget=conflicts,
                      wall_limit_seconds=seconds, wall_seconds=time.monotonic()-started)
        receiver.close(); process.close()
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--audit', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--conflicts', type=int, required=True)
    parser.add_argument('--seconds', type=float, required=True)
    args = parser.parse_args()
    checked = preflight(args)
    checked['inputs_sha256'][key(Path(__file__))] = digest(Path(__file__))
    args.out.mkdir(parents=True, exist_ok=False)
    proof = args.out/'proof.drat'
    raw = produce_bounded(checked['manifest']['cnf_path'], proof, args.conflicts, args.seconds)
    require(all(digest(p) == h for p, h in checked['inputs_sha256'].items()), 'Proof-producing input/source changed')
    result = dict(status=raw['solver_result'], inputs_sha256=checked['inputs_sha256'], solver_record=raw,
                  cnf_path=checked['manifest']['cnf_path'], cnf_sha256=checked['manifest']['cnf_sha256'],
                  candidate_path=checked['manifest']['candidate_path'], candidate_sha256=checked['manifest']['candidate_sha256'],
                  proof_path=key(proof) if proof.exists() else None, proof_sha256=digest(proof) if proof.exists() else None,
                  verified=False, fixed_K_excluded_by_this_run=False, graph_witness_created=False,
                  general_nonexistence_proved=False, scope='Proof production only. Requires separate bound DRAT audit; SAT/caps/errors are not a graph witness or exclusion.')
    save(args.out/'proof_generation.json', result)
    print(json.dumps({k: result[k] for k in ('status', 'proof_path', 'proof_sha256')}), flush=True)


if __name__ == '__main__':
    mp.freeze_support()
    main()
