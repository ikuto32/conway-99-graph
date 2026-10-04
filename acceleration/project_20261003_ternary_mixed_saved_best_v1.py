"""Source-only lossless graph projection from an independently checked saved BEST.

This emits only ordered construction triples and their matrix identity. It does
not create native state, copy RNG/counters, resume a trajectory or launch native.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import sys
from datetime import datetime, timezone

from command_deadline import CommandDeadline
from prepare_20261003_ternary_mixed_science_v3 import graph, wire, strict_json

ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()
SPEC = SELF.with_name(SELF.stem + '_spec.md')
SCI = 'acceleration/prepare_20261003_ternary_mixed_science_v3.py'
SCI_SHA = 'd1e25078b03719a957e51efb5cbc78f15bf1f8ed1f8039f398285f4a7508927a'
SCI_SPEC_SHA = 'c2045026b6ead1e545ed93b1d48fe6e8ea6cbe80ca090f6fedda1965ed7cde64'
SAVED = 'acceleration/audit_20261003_ternary_mixed_saved_objects_v4.py'
SAVED_SHA = '0a5399036b97a1d1386bdf5a26e63af537f689421567e36596929a9e2d3a6f2c'
SAVED_SPEC_SHA = '80ad0f20610024f363a034c29f23e93e86fd86a46ef0ba2eddf8efb03d62a7b5'
HISTORICAL_SCI = 'acceleration/prepare_20261003_ternary_mixed_science_v2.py'
HISTORICAL_SCI_SHA = '6e29380cc08766264f4697e175f387443e658010af0fbeb2b49911b1349a7b19'
HISTORICAL_SPEC_SHA = '491cee55730ca34f1c1c304f7f6128f37d2164bd9a49a3f9deb48f8168b7c3fb'
HEADER = ['HYPERGRAPH_TERNARY_MIXED_STATE_V1',
          'objective SRG_COMPLETE_TERNARY_PAIR_RESIDUE_V1',
          'move_kernel ALL_LINE_EXCLUSIVE_SWAP_TERNARY_V1',
          'distribution ALL_LABELLED_LINES_REJECTION_BOUNDED_XOSHIRO256SS_V1']


def need(ok, stage):
    if not ok:
        raise ValueError(stage)


def same(a, b):
    return json.dumps(a, sort_keys=True, allow_nan=False) == json.dumps(b, sort_keys=True, allow_nan=False)


def identity(value):
    return type(value) is str and re.fullmatch(r'[0-9a-f]{64}', value) is not None


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def extract_best(raw):
    """Read literal BEST fields only; the prerequisite gate checks the whole state."""
    need(type(raw) is bytes and len(raw) <= 1024*1024, 'STATE_BYTES')
    try:
        text = raw.decode('ascii')
    except UnicodeDecodeError as error:
        raise ValueError('STATE_ASCII') from error
    need(text.endswith('\n') and '\r' not in text, 'STATE_NEWLINE')
    lines = text.splitlines()
    need(lines[:4] == HEADER and lines[-1:] == ['END'], 'STATE_HEADER')

    def field(name):
        locations = [i for i, line in enumerate(lines) if line == name or line.startswith(name+' ')]
        need(len(locations) == 1, 'BEST_FIELD_UNIQUE:'+name)
        i = locations[0]
        words = lines[i].split(' ')
        need(words[0] == name and len(words) > 1 and all(words), 'BEST_FIELD_LAYOUT:'+name)
        return i, words[1:]

    def uint(words, count, stage):
        need(len(words) == count and all(re.fullmatch(r'0|[1-9][0-9]*', x) for x in words), stage)
        values = [int(x) for x in words]
        need(all(x < 2**64 for x in values), stage)
        return values

    n = uint(field('n')[1], 1, 'BEST_DOMAIN_INTEGER')[0]
    degree = uint(field('degree')[1], 1, 'BEST_DOMAIN_INTEGER')[0]
    need((n, degree) in [(9, 2), (12, 2), (99, 7)], 'BEST_DOMAIN')
    at, words = field('best')
    count = uint(words, 1, 'BEST_COUNT_INTEGER')[0]
    need(count == n*degree//3 and at+count < len(lines), 'BEST_COUNT')
    rows = [uint(line.split(' '), 3, 'BEST_ROW_INTEGER') for line in lines[at+1:at+1+count]]
    values = uint(field('best_metrics')[1], 7, 'BEST_METRIC_INTEGER')
    f3, lam, mu, q0, q1, q2, scalar = values
    weight = 819820 if (n, degree) == (99, 7) else n*(n-1)//2*(2*degree)**2+1
    recorded = dict(F3=f3, E_lambda=lam, E_mu=mu, E=lam+mu,
                    scalar_weight=weight, scalar=scalar, residue_population=[q0, q1, q2])
    matrix, metrics = graph(rows, n, degree)
    need(same(recorded, metrics), 'BEST_METRICS')
    return n, degree, rows, matrix, metrics


def saved_relation(report, state_name, state_sha, matrix_name, matrix_sha, metrics):
    need(type(report) is dict and same({k: report.get(k) for k in
         ['status', 'producer', 'verifier', 'method', 'target_resolution']},
         dict(status='INDEPENDENT_TERNARY_MIXED_SAVED_OBJECTS_V1_COMPLETE_PASS',
              producer='/root/native_driver', verifier='/root/checkpoint_audit',
              method='independent_artifact_check', target_resolution='NONE')), 'SAVED_HEADER')
    need(type(report.get('checker_implementation_version')) is int
         and report['checker_implementation_version'] == 4
         and report.get('source_sha256') == SAVED_SHA and report.get('spec_sha256') == SAVED_SPEC_SHA,
         'SAVED_IMPLEMENTATION')
    inputs = report.get('inputs_sha256')
    need(type(inputs) is dict and inputs and all(type(k) is str and identity(v) for k, v in inputs.items()), 'SAVED_INPUTS')
    need(inputs.get(state_name) == state_sha and inputs.get(matrix_name) == matrix_sha, 'SAVED_BEST_IDENTITIES')
    need(state_name.endswith('/native/final.state') and matrix_name == state_name[:-len('final.state')]+'best.adj',
         'FINAL_BEST_SOURCE_PAIR')
    need(inputs.get(SAVED) == SAVED_SHA and inputs.get(SAVED.replace('.py', '_spec.md')) == SAVED_SPEC_SHA
         and inputs.get(HISTORICAL_SCI) == HISTORICAL_SCI_SHA
         and inputs.get(HISTORICAL_SCI.replace('.py', '_spec.md')) == HISTORICAL_SPEC_SHA, 'SAVED_ANCESTRY')
    scope = report.get('saved_raw_scope')
    need(type(scope) is dict and same(scope.get('best'), metrics), 'SAVED_BEST_METRICS')
    for name in ['saved_state_files', 'complete_current_best_matrix_observations', 'complete_scalar_matrix_products']:
        need(type(scope.get(name)) is int and scope[name] > 0, 'SAVED_COMPLETE_SCOPE:'+name)
    need(type(scope.get('authenticated_native_reported_proposals')) is int
         and scope['authenticated_native_reported_proposals'] > 0, 'SAVED_COMPLETE_SCOPE:proposals')
    return inputs


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seconds', type=float, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--supervision-out', type=Path, required=True)
    parser.add_argument('--source-commit', required=True)
    for name in ['saved-full-gate', 'state', 'matrix']:
        parser.add_argument('--'+name, type=Path, required=True)
        parser.add_argument('--'+name+'-sha256', required=True)
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='One lossless saved BEST graph projection; complete prerequisite hashing and output preservation share this invocation; no native, resume or retries')
    need(os.name == 'posix' and os.geteuid() == 1000, 'LINUX_UID1000')
    out = args.out.resolve()
    need(out.is_relative_to(ROOT) and not out.exists(), 'FRESH_OUTPUT')
    out.mkdir(parents=True)
    pins = {}

    def pin(path, expected=None):
        need(deadline.status()['remaining_seconds'] > 20 and not deadline.status()['stop_required'], 'SAVE_RESERVE')
        path = path.resolve()
        need(path.is_relative_to(ROOT) and path.is_file(), 'INPUT_PATH')
        name = path.relative_to(ROOT).as_posix()
        need(name not in ['CLAIMS.yaml', '.git/index'], 'MUTABLE_INPUT_ROLE')
        actual = digest(path)
        need(expected is None or identity(expected) and actual == expected, 'INPUT_IDENTITY:'+name)
        need(name not in pins or pins[name] == actual, 'INPUT_CHANGED')
        pins[name] = actual
        return path

    def save(name, value):
        with (out/name).open('x', encoding='utf8', newline='\n') as stream:
            json.dump(value, stream, indent=2, allow_nan=False)
            stream.write('\n')

    try:
        for path, expected in [(SELF, None), (SPEC, None), (ROOT/SCI, SCI_SHA),
            (ROOT/SCI.replace('.py', '_spec.md'), SCI_SPEC_SHA),
            (ROOT/'acceleration/command_deadline.py', None), (ROOT/'acceleration/run_compute_command_v2.py', None)]:
            pin(path, expected)
        runtime = strict_json(pin(args.supervision_out.resolve()/'manifest.json'))
        need(runtime['cwd'] == str(ROOT) and runtime['command'][-len(sys.argv):] == [sys.executable, *sys.argv][1:], 'SUPERVISOR_WORKER')
        need(runtime['seconds'] >= args.seconds+20 and runtime['automatic_retry'] is False
             and runtime['cumulative_across_commands'] is False, 'OUTER_ALLOCATION')
        group = os.getpgid(0)
        guard = [x.decode() for x in (Path('/proc')/str(group)/'cmdline').read_bytes().split(b'\0') if x]
        need(guard and Path(guard[0]).name == 'timeout' and '--signal=KILL' in guard, 'LIVE_SUPPORTED_LINUX_GROUP')
        report_path = pin(args.saved_full_gate, args.saved_full_gate_sha256)
        state = pin(args.state, args.state_sha256)
        matrix_path = pin(args.matrix, args.matrix_sha256)
        n, degree, rows, matrix, metrics = extract_best(state.read_bytes())
        need((n, degree) == (99, 7), 'ACTUAL_TARGET_DOMAIN')
        need(matrix == matrix_path.read_bytes(), 'BEST_MATRIX_BYTES')
        report = strict_json(report_path)
        closure = saved_relation(report, state.relative_to(ROOT).as_posix(), pins[state.relative_to(ROOT).as_posix()],
            matrix_path.relative_to(ROOT).as_posix(), pins[matrix_path.relative_to(ROOT).as_posix()], metrics)
        for name, value in closure.items():
            pin(ROOT/name, value)
        source = digest(matrix_path)
        raw = wire(rows, n, degree, source)
        (out/'graph_input.txt').write_bytes(raw)
        projection = dict(schema='TERNARY_MIXED_SAVED_BEST_GRAPH_ONLY_PROJECTION_V1', input_implementation_version=2,
            source_state=state.relative_to(ROOT).as_posix(), source_state_sha256=digest(state), source_kind='final.best',
            source_matrix=matrix_path.relative_to(ROOT).as_posix(), source_matrix_sha256=source,
            prerequisite_saved_full_report=report_path.relative_to(ROOT).as_posix(), prerequisite_saved_full_sha256=digest(report_path),
            n=n, point_degree=degree, ordered_triples=rows, metrics=metrics, graph_input_sha256=digest(out/'graph_input.txt'),
            history_rng_counters_imported=False, native_state_written=False, native_calls=0, independent_approval=False,
            retained_construction_triples_are_all_graph_triangles_claimed=False,
            historical_ancestry_role='Complete prerequisite closure retains historical SCI2/spec formatter ancestry; no old input checker approval of this new implementation.')
        save('projection.json', projection)
        for path in [state, matrix_path, report_path]:
            need(digest(path) == pins[path.relative_to(ROOT).as_posix()], 'SOURCE_CLOSING_STABILITY')
        outputs = {path.relative_to(ROOT).as_posix(): dict(sha256=digest(path), bytes=path.stat().st_size)
                   for path in sorted(out.iterdir()) if path.is_file()}
        save('summary.json', dict(status='CANDIDATE_SAVED_BEST_GRAPH_ONLY_WIRE_PENDING_INDEPENDENT_CHECK',
            producer='/root/native_driver', timestamp=datetime.now(timezone.utc).isoformat(), command=[sys.executable, *sys.argv],
            cwd=str(ROOT), python=platform.python_version(), source_context_commit=args.source_commit,
            observed_euid=os.geteuid(), process_group=group, inputs_sha256=pins, raw_artifacts=outputs,
            metrics=metrics, native_calls=0, native_state_written=False, history_rng_counters_imported=False,
            independent_approval=False, target_resolution='NONE', deadline=deadline.status()))
    except BaseException as error:
        save('failure.json', dict(error=repr(error), inputs_sha256=pins, deadline=deadline.status(),
            outputs_preserved=True, automatic_retry=False, native_calls=0, independent_approval=False))
        raise


if __name__ == '__main__':
    main()
