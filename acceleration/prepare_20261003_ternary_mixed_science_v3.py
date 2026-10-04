"""SOURCE ONLY: narrow graph-only conversion and one contained mixed native run.

No controls, builds, automatic retries, seed selection or path loop are launched.
Each mode requires a separately reviewed command and fresh independent gates.
"""
import argparse
import hashlib
import json
import math
import os
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()
SPEC = SELF.with_name(SELF.stem + '_spec.md')
CPP = 'acceleration/hypergraph_ternary_mixed_anneal_20261003_v1.cpp'
CPP_SHA = 'eba379d3993e644084e62eba2153ca4870ff1e93cb64fd4212a383fe60c08b31'
BINARY_SHA = '56e0ecf4295f72a51c58a6957da2d4e32787a2514e38866e41172eb79738cf09'
BUILD_SHA = 'c1c3df1e9d933718c8b48ad94f2d03759bed17df4c5faaaf8b65651a08b928ea'
OBJECTIVE = 'SRG_COMPLETE_TERNARY_PAIR_RESIDUE_V1'
ENGINE_PASS = 'INDEPENDENT_TERNARY_MIXED_ENGINE_V1_CONTROLS_PASS'
SAVED_PASS = 'INDEPENDENT_TERNARY_MIXED_SAVED_OBJECTS_V1_CALIBRATION_PASS'
INPUT_PASS = 'INDEPENDENT_TERNARY_MIXED_GRAPH_ONLY_INPUT_V1_COMPLETE_PASS'
CENSUS_PASS = 'INDEPENDENT_TERNARY_ALL_LINE_CENSUS_V1_COMPLETE_PASS'
CODE = [SELF, SPEC, ROOT/CPP, ROOT/'acceleration/hypergraph_ternary_mixed_anneal_20261003_v1_spec.md',
        ROOT/'acceleration/prepare_20261003_hypergraph_ternary_mixed_v1.py',
        ROOT/'acceleration/prepare_20261003_hypergraph_ternary_mixed_v1_spec.md',
        ROOT/'acceleration/command_deadline.py', ROOT/'acceleration/run_compute_command_v2.py',
        ROOT/'acceleration/native_budget_env_v1/pyproject.toml', ROOT/'acceleration/native_budget_env_v1/uv.lock']


def need(ok, stage):
    if not ok:
        raise ValueError(stage)


def stamp():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def key(path):
    return path.resolve().relative_to(ROOT).as_posix()


def strict_json(path):
    def pairs(items):
        result = {}
        for name, value in items:
            need(name not in result, 'JSON_DUPLICATE')
            result[name] = value
        return result
    return json.loads(path.read_bytes(), object_pairs_hook=pairs,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError('JSON_NONFINITE')))


def save(path, obj):
    with path.open('x', encoding='utf8', newline='\n') as handle:
        json.dump(obj, handle, indent=2, allow_nan=False)
        handle.write('\n')


def graph(rows, n, degree):
    need(type(n) is int and type(degree) is int and (n, degree) in [(9, 2), (12, 2), (99, 7)], 'DOMAIN')
    need(type(rows) is list and len(rows) == n*degree//3, 'TRIPLE_COUNT')
    counts = [0]*n
    masks = [0]*n
    seen = set()
    for row in rows:
        need(type(row) is list and len(row) == 3 and all(type(x) is int and 0 <= x < n for x in row), 'TRIPLE_TYPE')
        need(len(set(row)) == 3, 'TRIPLE_DISTINCT')
        identity = tuple(sorted(row))
        need(identity not in seen, 'TRIPLE_DUPLICATE')
        seen.add(identity)
        for x in row:
            counts[x] += 1
        for i in range(3):
            for j in range(i+1, 3):
                x, y = row[i], row[j]
                need(not ((masks[x] >> y) & 1), 'LINEARITY')
                masks[x] |= 1 << y
                masks[y] |= 1 << x
    need(all(x == degree for x in counts) and all(x.bit_count() == 2*degree for x in masks), 'DEGREE')
    f3 = lam = mu = 0
    residues = [0, 0, 0]
    for i in range(n):
        for j in range(i+1, n):
            adjacent = (masks[i] >> j) & 1
            residual = (masks[i] & masks[j]).bit_count() + adjacent - 2
            residues[residual % 3] += 1
            f3 += int(residual % 3 != 0)
            if adjacent:
                lam += residual*residual
            else:
                mu += residual*residual
    weight = 819820 if (n, degree) == (99, 7) else n*(n-1)//2*(2*degree)**2 + 1
    matrix = (str(n)+'\n'+''.join(''.join(str((row >> j) & 1) for j in range(n))+'\n' for row in masks)).encode('ascii')
    return matrix, dict(F3=f3, E_lambda=lam, E_mu=mu, E=lam+mu, scalar_weight=weight,
                        scalar=weight*f3+lam+mu, residue_population=residues)


def wire(rows, n, degree, matrix_sha):
    graph(rows, n, degree)
    need(type(matrix_sha) is str and len(matrix_sha) == 64 and all(x in '0123456789abcdef' for x in matrix_sha), 'GRAPH_HASH')
    return (f'TERNARY_LINEAR_GRAPH_INPUT_V1\nn {n}\ndegree {degree}\nsource_graph_sha256 {matrix_sha}\ntriples {len(rows)}\n'
            + ''.join(' '.join(map(str, row))+'\n' for row in rows) + 'END\n').encode('ascii')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['project', 'run'])
    parser.add_argument('--seconds', type=float, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--supervision-out', type=Path, required=True)
    parser.add_argument('--source-commit', required=True)
    for name in ['census-gate', 'matrix', 'triples', 'engine-gate', 'saved-gate', 'input-gate', 'wire', 'binary', 'build-manifest']:
        parser.add_argument('--'+name, type=Path)
        parser.add_argument('--'+name+'-sha256')
    for name in ['seed', 'steps', 'mix-steps', 'schedule-steps', 'verify-every', 'checkpoint-every', 'trace-prefix', 'trace-stride', 'address-space-bytes', 'file-bytes']:
        parser.add_argument('--'+name, type=int)
    for name in ['native-seconds', 'temperature-start', 'temperature-end', 'checkpoint-seconds']:
        parser.add_argument('--'+name, type=float)
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='One separately reviewed graph-only conversion or explicit one-native mixed invocation; hashes/preprocessing/exports share this deadline; no retries')
    pins = {}
    out = args.out.resolve()
    need(out.is_relative_to(ROOT) and not out.exists(), 'FRESH_OUTPUT')
    need(os.name == 'posix' and os.geteuid() == 1000, 'LINUX_UID1000')
    out.mkdir(parents=True)

    def pin(path, identity=None):
        need(deadline.status()['remaining_seconds'] > 20 and not deadline.status()['stop_required'], 'DEADLINE_PRESERVE')
        need(path is not None, 'EXPLICIT_INPUT')
        path = path.resolve()
        need(path.is_relative_to(ROOT) and path.is_file(), 'INPUT_PATH')
        actual = sha(path)
        need(identity is None or actual == identity, 'INPUT_HASH')
        name = key(path)
        need(name not in ['CLAIMS.yaml', '.git/index'], 'MUTABLE_INPUT_ROLE')
        need(name not in pins or pins[name] == actual, 'INPUT_CHANGED')
        pins[name] = actual
        return path

    def explicit(name):
        identity = getattr(args, name.replace('-', '_')+'_sha256')
        need(type(identity) is str and len(identity) == 64, 'EXPLICIT_HASH')
        return pin(getattr(args, name.replace('-', '_')), identity)

    def gate(name, status, verifier):
        value = strict_json(explicit(name))
        need(value.get('status') == status and value.get('producer') == '/root/native_driver'
             and value.get('verifier') == verifier and value.get('method') == 'independent_artifact_check'
             and value.get('target_resolution') == 'NONE', 'GATE_HEADER')
        need(type(value.get('inputs_sha256')) is dict and value['inputs_sha256'], 'GATE_INPUTS')
        for path, identity in value['inputs_sha256'].items():
            pin(ROOT/path, identity)
        return value

    try:
        for path in CODE:
            pin(path, CPP_SHA if key(path) == CPP else None)
        manifest = strict_json(pin(args.supervision_out.resolve()/'manifest.json'))
        need(manifest['cwd'] == str(ROOT) and manifest['command'][-len(sys.argv):] == [sys.executable, *sys.argv][1:], 'SUPERVISOR_WORKER')
        need(manifest['seconds'] >= args.seconds+20 and manifest['automatic_retry'] is False
             and manifest['cumulative_across_commands'] is False, 'OUTER_ALLOCATION')
        group = os.getpgid(0)
        guard = [x.decode() for x in (Path('/proc')/str(group)/'cmdline').read_bytes().split(b'\0') if x]
        need(guard and Path(guard[0]).name == 'timeout' and '--signal=KILL' in guard, 'LIVE_SUPPORTED_LINUX_GROUP')
        save(out/'invocation.json', dict(timestamp=stamp(), command=[sys.executable, *sys.argv], cwd=str(ROOT),
            source_context_commit=args.source_commit, software_sha256=dict(pins), observed_euid=os.geteuid(),
            process_group=os.getpgid(0), supervisor_manifest_sha256=sha(args.supervision_out.resolve()/'manifest.json'),
            python=platform.python_version(), historical_native_state_written=False, independent_approval=False))
        if args.mode == 'project':
            checked = gate('census-gate', CENSUS_PASS, '/root/structural')
            for name, expected in [('complete_labelled_proposals', 239085), ('complete_raw_record_fields', 24),
                                   ('complete_parts', 48), ('complete_checkpoints', 48)]:
                need(type(checked.get(name)) is int and checked[name] == expected, 'COMPLETE_CENSUS_SCOPE')
            matrix_path, rows_path = explicit('matrix'), explicit('triples')
            need(checked['inputs_sha256'].get(key(matrix_path)) == sha(matrix_path)
                 and checked['inputs_sha256'].get(key(rows_path)) == sha(rows_path), 'CHECKED_SELECTED_SOURCE')
            selected = checked.get('selected_neighbor')
            need(type(selected) is dict and type(selected.get('proposal_id')) is int, 'CHECKED_SELECTED_OBJECT')
            payload = strict_json(rows_path)
            need(type(payload.get('proposal_id')) is int and payload['proposal_id'] == selected['proposal_id'], 'SELECTED_ID')
            aggregate = checked.get('aggregate')
            need(type(aggregate) is dict and type(aggregate.get('minimum_pair_proposal_ids')) is list
                 and aggregate['minimum_pair_proposal_ids'] and all(type(x) is int for x in aggregate['minimum_pair_proposal_ids'])
                 and selected['proposal_id'] == min(aggregate['minimum_pair_proposal_ids']), 'SELECTED_MINIMUM_TIE')
            rows, n, degree = payload['ordered_triples'], payload['n'], payload['point_degree']
            need((n, degree) == (99, 7), 'TARGET_INPUT_DOMAIN')
            matrix, metrics = graph(rows, n, degree)
            need(matrix == matrix_path.read_bytes(), 'SELECTED_MATRIX_BYTES')
            need(json.dumps(metrics, sort_keys=True) == json.dumps(selected['metrics'], sort_keys=True), 'SELECTED_METRICS')
            need(json.dumps(aggregate.get('minimum_pair')) == json.dumps([metrics['F3'], metrics['E']]), 'SELECTED_MINIMUM_PAIR')
            raw = wire(rows, n, degree, sha(matrix_path))
            (out/'graph_input.txt').write_bytes(raw)
            save(out/'projection.json', dict(schema='TERNARY_MIXED_GRAPH_ONLY_PROJECTION_V1', ordered_triples=rows,
                n=n, point_degree=degree, source_matrix=key(matrix_path), source_matrix_sha256=sha(matrix_path),
                source_triples=key(rows_path), source_triples_sha256=sha(rows_path), selected_proposal_id=selected['proposal_id'],
                metrics=metrics, graph_input_sha256=sha(out/'graph_input.txt'), historical_native_state_written=False,
                rng_or_trajectory_imported=False, independent_approval=False))
            result = dict(status='CANDIDATE_GRAPH_ONLY_WIRE_PENDING_INDEPENDENT_CHECK', metrics=metrics)
        else:
            engine = gate('engine-gate', ENGINE_PASS, '/root/checkpoint_audit')
            saved = gate('saved-gate', SAVED_PASS, '/root/checkpoint_audit')
            checked_input = gate('input-gate', INPUT_PASS, '/root/checkpoint_audit')
            wire_path, binary_path = explicit('wire'), explicit('binary')
            build = strict_json(explicit('build-manifest'))
            need(sha(binary_path) == BINARY_SHA and sha(args.build_manifest.resolve()) == BUILD_SHA
                 and build['source_cpp_sha256'] == CPP_SHA and build['binary_sha256'] == BINARY_SHA, 'EXACT_NATIVE_BUILD')
            for path, identity in build['inputs_sha256'].items():
                pin(ROOT/path, identity)
            need(engine['inputs_sha256'].get(CPP) == CPP_SHA and engine['inputs_sha256'].get(key(binary_path)) == BINARY_SHA
                 and saved['inputs_sha256'].get(CPP) == CPP_SHA and saved['inputs_sha256'].get(key(binary_path)) == BINARY_SHA
                 and saved['inputs_sha256'].get(key(SELF)) == pins[key(SELF)]
                 and saved['inputs_sha256'].get(key(SPEC)) == pins[key(SPEC)]
                 and checked_input['inputs_sha256'].get(key(wire_path)) == sha(wire_path), 'GATE_NATIVE_INPUT')
            integer_fields = ['seed', 'steps', 'mix_steps', 'schedule_steps', 'verify_every', 'checkpoint_every', 'trace_prefix', 'trace_stride', 'address_space_bytes', 'file_bytes']
            for name in integer_fields:
                need(type(getattr(args, name)) is int and 0 <= getattr(args, name) < 2**64, 'EXPLICIT_UINT_CONFIG')
            need(args.steps > 0 and args.schedule_steps > 0 and args.verify_every > 0 and args.checkpoint_every > 0
                 and args.address_space_bytes > 0 and args.file_bytes > 0, 'POSITIVE_CONFIG')
            for name in ['native_seconds', 'temperature_start', 'temperature_end', 'checkpoint_seconds']:
                need(type(getattr(args, name)) is float and math.isfinite(getattr(args, name)) and getattr(args, name) >= 0, 'EXPLICIT_FINITE_CONFIG')
            need(args.native_seconds > 5 and args.checkpoint_seconds > 0, 'NATIVE_PRESERVE')
            source_graph_sha = checked_input.get('source_graph_sha256')
            need(type(source_graph_sha) is str and len(source_graph_sha) == 64
                 and all(x in '0123456789abcdef' for x in source_graph_sha), 'INPUT_SOURCE_GRAPH_HASH')
            allowed = deadline.child_seconds(args.native_seconds, reserve_seconds=30)
            need(allowed >= args.native_seconds, 'EXACT_NATIVE_ALLOCATION')
            native_out = out/'native'
            command = ['/usr/bin/timeout', '--foreground', '--signal=TERM', '--kill-after=5s', f'{allowed:.6f}s',
                       '/usr/bin/prlimit', f'--as={args.address_space_bytes}:{args.address_space_bytes}',
                       f'--fsize={args.file_bytes}:{args.file_bytes}', '--core=0:0', str(binary_path),
                       '--out', str(native_out), '--seconds', f'{allowed-5:.6f}', '--graph-input', str(wire_path),
                       '--source-graph-sha256', source_graph_sha]
            for name in integer_fields[:8] + ['temperature_start', 'temperature_end', 'checkpoint_seconds']:
                command += ['--'+name.replace('_', '-'), str(getattr(args, name))]
            save(out/'native.launch.json', dict(timestamp=stamp(), command=command, deadline=deadline.status(),
                independent_approval=False, source_context_commit=args.source_commit))
            started = time.monotonic()
            with (out/'native.stdout.log').open('xb') as stdout, (out/'native.stderr.log').open('xb') as stderr:
                child = subprocess.Popen(command, cwd=ROOT, stdout=stdout, stderr=stderr)
                need(os.getpgid(child.pid) == os.getpgid(0), 'NATIVE_CHILD_CONTAINED')
                caught = None
                try:
                    code = child.wait(timeout=deadline.child_seconds(allowed+5, reserve_seconds=20))
                except BaseException as error:
                    caught = repr(error)
                    if child.poll() is None:
                        child.terminate()
                        try:
                            child.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            child.kill()
                    code = child.wait(timeout=5)
            save(out/'native.receipt.json', dict(command=command, cwd=str(ROOT), actual_exit_code=code,
                wall_seconds=time.monotonic()-started, child_pid=child.pid, process_group=os.getpgid(0),
                stdout_sha256=sha(out/'native.stdout.log'), stderr_sha256=sha(out/'native.stderr.log'),
                automatic_retries=0, observed_euid=os.geteuid(), error=caught, reaped=True))
            result = dict(status='CANDIDATE_NATIVE_RUN_PENDING_INDEPENDENT_SAVED_OBJECT_CHECK' if code == 0 and caught is None else 'UNKNOWN_NATIVE_NONZERO_PARTIAL_PRESERVED',
                          actual_exit_code=code, native_result=strict_json(native_out/'result.json') if (native_out/'result.json').is_file() else None)
        raw_artifacts = {}
        for path in sorted(out.rglob('*')):
            if path.is_file():
                need(deadline.status()['remaining_seconds'] > 20, 'ARTIFACT_PRESERVE_RESERVE')
                raw_artifacts[key(path)] = dict(sha256=sha(path), bytes=path.stat().st_size)
        result.update(timestamp=stamp(), command=[sys.executable, *sys.argv], inputs_sha256=pins,
                      elapsed_seconds=deadline.status()['elapsed_seconds'], independent_approval=False,
                      target_resolution='NONE', automatic_retries=0, raw_artifacts=raw_artifacts)
        save(out/'summary.json', result)
        print(json.dumps(dict(status=result['status'], summary_sha256=sha(out/'summary.json'))), flush=True)
    except BaseException as error:
        save(out/'failure.json', dict(timestamp=stamp(), error=repr(error), inputs_sha256=pins, deadline=deadline.status(),
            preserved_partial_artifacts=True, independent_approval=False, target_resolution='NONE', automatic_retries=0))
        raise


if __name__ == '__main__':
    main()
