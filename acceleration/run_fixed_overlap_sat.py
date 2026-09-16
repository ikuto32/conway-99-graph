"""Bounded CaDiCaL195 runner for independently audited fixed-overlap CNF.

SAT is published only after pure full-graph and fixed-K checks. UNSAT without
a separately checked proof is unverified; a deadline or conflict cap is
UNKNOWN. No automatic submission or goal-state change is made.
"""
import argparse
from hashlib import sha256
from itertools import combinations
import json
from math import isfinite
import multiprocessing as mp
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
DEPS = ROOT/'.deps'
sys.path.insert(0, str(ROOT))
from validate_submission import verify_edges

VALIDATOR_SHA256 = '92cb7b04ffd32e70f74b372f8d8578b1a364bbf22c6924c8ad6f80c41a5a21a3'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def resolve(name):
    path = Path(str(name).replace('\\', '/'))
    return path.resolve() if path.is_absolute() else (ROOT/path).resolve()


def key(path):
    path = resolve(path)
    return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix()


def digest(path):
    value = sha256()
    with resolve(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b''):
            value.update(chunk)
    return value.hexdigest()


def save(path, value):
    with path.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(value, indent=2, allow_nan=False)+'\n')


def labels_and_mapping():
    legacy = [p for p in combinations(range(14), 2) if p[0]//2 != p[1]//2]
    current = sorted(legacy, key=lambda p: (p[0]//2, p[1]//2, p))
    mapping = [legacy.index(p) for p in current]
    inverse = [current.index(p) for p in legacy]
    return legacy, current, mapping, inverse


def expected_fixed_units(candidate):
    legacy, current, mapping, inverse = labels_and_mapping()
    edges = candidate['overlap_edges_outer_zero_based']
    require(type(edges) is list and len(edges) == 168 and all(type(e) is list and len(e) == 2 and
            all(type(v) is int for v in e) and 0 <= e[0] < e[1] < 84 for e in edges), 'Invalid fixed-K edge list')
    known = set(map(tuple, edges))
    require(len(known) == 168, 'Duplicate fixed-K edge')
    variables = {p: i for i, p in enumerate(combinations(range(84), 2), 1)}
    units, free = {}, []
    for u, v in combinations(range(84), 2):
        variable = variables[tuple(sorted((mapping[u], mapping[v])))]
        shared = {s//2 for s in current[u]} & {s//2 for s in current[v]}
        if shared:
            value = (u, v) in known
            require(not value or len(shared) == 1, 'Known edge is not a valid overlap edge')
            units[variable] = dict(current_edge=[u, v], legacy_edge=sorted((mapping[u], mapping[v])),
                                   variable=variable, value=value, literal=variable if value else -variable)
        else:
            require((u, v) not in known, 'A free disjoint edge was declared fixed present')
            free.append(variable)
    require(len(units) == 1806 and len(free) == 1680 and sum(r['value'] for r in units.values()) == 168,
            'Fixed/free edge partition differs')
    return units, sorted(free)


def decode_and_verify(edge_model, candidate):
    """Decode all legacy edge variables; do not import the CNF adapter."""
    require(type(edge_model) is list and len(edge_model) == 3486 and all(type(v) is int and v != 0 for v in edge_model),
            'Solver model must explicitly assign all 3486 outer-edge variables')
    require({abs(v) for v in edge_model} == set(range(1, 3487)), 'Repeated, missing or out-of-range edge variable')
    values = {abs(v): v > 0 for v in edge_model}
    legacy, current, mapping, inverse = labels_and_mapping()
    edges = {(1, s+2) for s in range(14)} | {(s+2, s+3) for s in range(0, 14, 2)}
    for u, symbols in enumerate(legacy):
        edges.update((symbol+2, u+16) for symbol in symbols)
    for variable, (u, v) in enumerate(combinations(range(84), 2), 1):
        if values[variable]:
            edges.add((u+16, v+16))
    edges = sorted(edges)
    verification = verify_edges(edges)
    require(verification['degrees_checked'] == 99 and verification['pairs_checked'] == 4851,
            'Full graph validator did not check all vertices/pairs')
    units, free = expected_fixed_units(candidate)
    mismatches = [v for v, row in units.items() if values[v] != row['value']]
    # Return the same graph under the current outer-label ordering as a second
    # independently checked representation, not just a declared permutation.
    def to_current(vertex):
        return vertex if vertex <= 15 else inverse[vertex-16]+16
    current_edges = sorted(tuple(sorted((to_current(u), to_current(v)))) for u, v in edges)
    current_verification = verify_edges(current_edges)
    require(current_verification['valid'] == verification['valid'], 'Relabeling changed graph validity')
    valid = verification['valid'] and current_verification['valid'] and not mismatches
    return dict(valid=valid, legacy_edges_one_based=[list(e) for e in edges],
                current_edges_one_based=[list(e) for e in current_edges],
                legacy_verification=verification, current_verification=current_verification,
                fixed_edge_variables_checked=1806, fixed_edge_mismatch_count=len(mismatches),
                fixed_edge_mismatches_shown=mismatches[:10], free_edge_variables=1680,
                current_to_legacy_vertices=mapping, legacy_to_current_vertices=inverse)


def solver_worker(cnf_path, conflicts, sender):
    """Only this spawned process imports or runs PySAT; it writes no files."""
    started = time.monotonic()
    try:
        sys.path.insert(0, str(DEPS))
        import pysat
        from pysat.formula import CNF
        from pysat.solvers import Solver
        formula = CNF(from_file=str(cnf_path))
        parsed = time.monotonic()
        with Solver(name='cadical195', bootstrap_with=formula.clauses) as solver:
            loaded = time.monotonic()
            solver.conf_budget(conflicts)
            answer = solver.solve_limited()
            solved = time.monotonic()
            model = solver.get_model() if answer is True else None
            stats = solver.accum_stats()
        sender.send(dict(solver_result='SAT_MODEL_UNVALIDATED' if answer is True else 'UNSAT_UNVERIFIED' if answer is False else 'UNKNOWN',
                         edge_model=[v for v in model if abs(v) <= 3486] if model is not None else None,
                         declared_variables=formula.nv, clauses=len(formula.clauses), pysat_version=pysat.__version__,
                         parse_seconds=parsed-started, load_seconds=loaded-parsed, solve_seconds=solved-loaded, stats=stats))
    except BaseException as exc:
        sender.send(dict(solver_result='UNKNOWN', reason='WORKER_ERROR', error_type=type(exc).__name__, message=str(exc)))
    finally:
        sender.close()


def solve_bounded(cnf_path, conflicts, seconds):
    require(type(conflicts) is int and 0 < conflicts <= 2**31-1 and type(seconds) in (float, int) and isfinite(seconds) and seconds > 0,
            'Positive conflict and wall-time limits are required')
    context = mp.get_context('spawn')
    receiver, sender = context.Pipe(duplex=False)
    process = context.Process(target=solver_worker, args=(str(resolve(cnf_path)), conflicts, sender), name='fixed-K-cadical195')
    started = time.monotonic()
    process.start()
    sender.close()
    result = None
    try:
        if receiver.poll(max(0, seconds-(time.monotonic()-started))):
            try:
                result = receiver.recv()
            except EOFError:
                result = dict(solver_result='UNKNOWN', reason='WORKER_EXIT_WITHOUT_RESULT')
        else:
            result = dict(solver_result='UNKNOWN', reason='WALL_TIME_LIMIT_INCLUDING_PARSE_AND_LOAD')
    finally:
        if result is not None and result.get('reason') != 'WALL_TIME_LIMIT_INCLUDING_PARSE_AND_LOAD':
            process.join(0.2)
        if process.is_alive():
            process.terminate()
        process.join(5)
        if process.is_alive():
            process.kill()
            process.join(5)
        require(not process.is_alive(), 'SAT worker could not be stopped')
        result = result or dict(solver_result='UNKNOWN', reason='PARENT_INTERRUPTED')
        result.update(worker_exit_code=process.exitcode, wall_seconds=time.monotonic()-started,
                      conflict_budget=conflicts, wall_limit_seconds=seconds)
        receiver.close()
        process.close()
    return result


def preflight(args):
    require(not args.out.exists(), 'Preserve prior SAT output; choose a fresh directory')
    require(args.out.resolve().is_relative_to(ROOT), 'Output must be within the workspace')
    require(type(args.conflicts) is int and 0 < args.conflicts <= 2**31-1 and isfinite(args.seconds) and args.seconds > 0, 'Positive bounded budgets required')
    require(sys.version_info[:2] == (3, 12), 'Installed PySAT native module requires CPython3.12; use .venv/Scripts/python.exe')
    manifest_path, audit_path = resolve(args.manifest), resolve(args.audit)
    manifest, audit = (json.loads(p.read_bytes()) for p in (manifest_path, audit_path))
    require(manifest['status'] == 'FIXED_OVERLAP_CNF_ADAPTER_COMPLETE' and
            audit['status'] == 'INDEPENDENT_FIXED_OVERLAP_CNF_MAPPING_AUDIT_PASS', 'Adapter/independent audit missing')
    inputs = {}
    def bind(name, expected=None):
        label = key(name)
        if label not in inputs:
            inputs[label] = digest(name)
        require(expected is None or inputs[label] == expected, 'Changed SAT input: '+label)
        return inputs[label]
    bind(manifest_path); bind(audit_path)
    audit_bindings = {key(name): expected for name, expected in audit['inputs_sha256'].items()}
    require(audit_bindings.get(key(manifest_path)) == bind(manifest_path), 'Audit is not bound to adapter manifest')
    for mapping in (audit_bindings, manifest['inputs_sha256']):
        for name, expected in mapping.items():
            bind(name, expected)
    for stem in ('candidate', 'base_cnf', 'cnf'):
        path = resolve(manifest[stem+'_path'])
        require(audit_bindings.get(key(path)) == manifest[stem+'_sha256'], 'Audit does not bind '+stem)
        bind(path, manifest[stem+'_sha256'])
    candidate = json.loads(resolve(manifest['candidate_path']).read_bytes())
    units, free = expected_fixed_units(candidate)
    _legacy, _current, mapping, inverse = labels_and_mapping()
    require(manifest['current_to_legacy_vertices'] == mapping and manifest['legacy_to_current_vertices'] == inverse,
            'Adapter/current vertex ordering differs')
    declared = manifest['fixed_units']
    require(type(declared) is list and len(declared) == 1806 and len({r['variable'] for r in declared}) == 1806,
            'Wrong fixed unit inventory')
    require(all(row == units.get(row['variable']) for row in declared), 'Adapter fixed-unit semantics differ')
    require(type(manifest['free_edge_variables']) is list and sorted(manifest['free_edge_variables']) == free,
            'Adapter free-edge domain differs')
    require(manifest['no_symmetry_branch_added'] is True and manifest['edge_variables'] == 3486,
            'Unexpected adapter symmetry/edge-variable scope')
    for path in [Path(__file__), ROOT/'validate_submission.py', DEPS/'pysat/__init__.py', DEPS/'pysat/formula.py', DEPS/'pysat/solvers.py']:
        bind(path)
    require(bind(ROOT/'validate_submission.py') == VALIDATOR_SHA256, 'Pure graph validator changed')
    binaries = list(DEPS.glob('pysolvers*.pyd'))
    require(len(binaries) == 1, 'Ambiguous/missing PySAT native module')
    bind(binaries[0])
    return dict(manifest=manifest, candidate=candidate, inputs_sha256=inputs,
                manifest_path=key(manifest_path), manifest_sha256=bind(manifest_path),
                audit_path=key(audit_path), audit_sha256=bind(audit_path))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--audit', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--conflicts', type=int, required=True)
    parser.add_argument('--seconds', type=float, required=True)
    parser.add_argument('--validate-only', action='store_true')
    args = parser.parse_args()
    checked = preflight(args)
    if args.validate_only:
        print(json.dumps(dict(status='FIXED_OVERLAP_SAT_READ_ONLY_PREFLIGHT_PASS',
                             inputs_sha256=checked['inputs_sha256'], fixed_variables=1806, free_variables=1680,
                             solver_invocations=0, output_created=False)), flush=True)
        return
    args.out.mkdir(parents=True, exist_ok=False)
    bound = {k: v for k, v in checked.items() if k not in ('candidate', 'manifest')}
    save(args.out/'runner_manifest.json', dict(status='FIXED_OVERLAP_SAT_RUN_MANIFEST', **bound,
         solver='cadical195', conflict_budget=args.conflicts, wall_limit_seconds=args.seconds,
         wall_limit_scope='One spawned worker including Python startup, CNF parse, solver load and solve',
         negative_results_are_proofs=False, writes_root_submission=False))
    raw = solve_bounded(checked['manifest']['cnf_path'], args.conflicts, args.seconds)
    edge_model = raw.pop('edge_model', None)
    require(all(digest(name) == expected for name, expected in checked['inputs_sha256'].items()), 'Input/source changed during SAT run')
    status, verification, witness = raw['solver_result'], None, None
    if status == 'SAT_MODEL_UNVALIDATED':
        try:
            decoded = decode_and_verify(edge_model, checked['candidate'])
        except ValueError as exc:
            decoded = dict(valid=False, rejection_reason=str(exc))
        verification = {k: v for k, v in decoded.items() if not k.endswith('edges_one_based')}
        if decoded['valid']:
            require(decoded['legacy_verification']['edge_count'] == 693 and decoded['current_verification']['edge_count'] == 693,
                    'Unexpected SAT witness size')
            witness_path = args.out/'validated_graph.json'
            save(witness_path, dict(status='INDEPENDENTLY_VALIDATED_FIXED_K_SRG_99_14_1_2_WITNESS', **bound,
                                   **decoded, no_submission_written=True))
            witness = dict(path=key(witness_path), sha256=digest(witness_path))
            status = 'SAT_INDEPENDENTLY_VALIDATED_GRAPH'
        else:
            status = 'INVALID_SAT_MODEL'
    report = dict(status=status, **bound, solver='cadical195', solver_record=raw,
                  direct_graph_verification=verification, validated_witness=witness,
                  formal_unsat_proof=None, fixed_K_excluded_by_this_run=False, general_nonexistence_proved=False,
                  root_submission_written=False, goal_marked_complete=False,
                  scope='SAT requires independent full99 and exact fixed-edge identity. UNSAT, caps, timeouts and errors provide no exclusion without separately checked proof.')
    save(args.out/'result.json', report)
    print(json.dumps(dict(status=status, witness=witness, wall_seconds=raw['wall_seconds'])), flush=True)


if __name__ == '__main__':
    mp.freeze_support()
    main()
