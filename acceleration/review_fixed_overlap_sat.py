"""Tiny-engine and synthetic decode controls; never solve a research CNF."""
import argparse
from contextlib import redirect_stdout
from copy import deepcopy
import io
import json
from pathlib import Path
import sys
import time
from unittest.mock import patch

import run_fixed_overlap_sat as runner

ROOT = Path(__file__).resolve().parents[1]
R = ROOT/'acceleration/results'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    manifest_path = R/'20260916_fixed_overlap_cnf_control/manifest.json'
    audit_path = manifest_path.with_name('independent_audit.json')
    manifest, audit = [json.loads(p.read_bytes()) for p in (manifest_path, audit_path)]
    candidate = json.loads(runner.resolve(manifest['candidate_path']).read_bytes())
    inputs = {runner.key(p): runner.digest(p) for p in (manifest_path, audit_path, Path(__file__),
              ROOT/'acceleration/run_fixed_overlap_sat.py', ROOT/'validate_submission.py')}
    inputs.update(audit['inputs_sha256'])
    outputs, cli, decode = {}, [], []
    def write(path, value):
        runner.save(path, value); outputs[runner.key(path)] = runner.digest(path)
    def cli_run(name, changes=(), positive=False):
        out = args.out/(name+'_must_not_exist')
        argv = ['run_fixed_overlap_sat', '--manifest', str(manifest_path), '--audit', str(audit_path),
                '--out', str(out), '--conflicts', '1000', '--seconds', '5', *changes]
        if positive:
            argv.append('--validate-only')
        captured = io.StringIO()
        try:
            with patch.object(sys, 'argv', argv), patch.object(runner, 'solve_bounded', side_effect=AssertionError('Research CNF solve forbidden')), redirect_stdout(captured):
                runner.main()
        except ValueError as exc:
            require(not positive, 'Positive preflight failed: '+str(exc))
            cli.append(dict(name=name, expected='REJECT', observed='REJECT', reason=str(exc)))
        else:
            require(positive, 'Invalid preflight accepted')
            result = json.loads(captured.getvalue())
            require(result['status'] == 'FIXED_OVERLAP_SAT_READ_ONLY_PREFLIGHT_PASS' and result['solver_invocations'] == 0,
                    'Wrong dry validation result')
            inputs.update(result['inputs_sha256'])
            cli.append(dict(name=name, expected='PASS', observed='PASS'))
        require(not out.exists(), 'Preflight created an output directory')
    cli_run('real_audited_adapter_dry', positive=True)
    cli_run('zero_conflicts', ['--conflicts', '0'])
    cli_run('huge_conflicts', ['--conflicts', str(2**31)])
    cli_run('nonfinite_time', ['--seconds', 'nan'])
    cli_run('zero_time', ['--seconds', '0'])
    cli_run('existing_output', ['--out', str(args.out)])
    for name, mutate in [
        ('wrong_vertex_mapping', lambda d: d['current_to_legacy_vertices'].__setitem__(0, d['current_to_legacy_vertices'][1])),
        ('wrong_fixed_literal', lambda d: d['fixed_units'][0].__setitem__('literal', -d['fixed_units'][0]['literal'])),
        ('wrong_free_domain', lambda d: d['free_edge_variables'].pop()),
        ('symmetry_flag', lambda d: d.__setitem__('no_symmetry_branch_added', False))]:
        obj = deepcopy(manifest); mutate(obj)
        path = args.out/(name+'_manifest.json'); write(path, obj)
        proof = deepcopy(audit)
        del proof['inputs_sha256'][runner.key(manifest_path)]
        proof['inputs_sha256'][runner.key(path)] = runner.digest(path)
        proof_path = args.out/(name+'_audit.json'); write(proof_path, proof)
        cli_run(name, ['--manifest', str(path), '--audit', str(proof_path)])
        cli[-1]['manifest_hash_rebound_to_reach_semantic_guard'] = True
    units, free = runner.expected_fixed_units(candidate)
    base_model = [v if v in units and units[v]['value'] else -v for v in range(1, 3487)]
    checked = runner.decode_and_verify(base_model, candidate)
    require(not checked['valid'] and checked['fixed_edge_mismatch_count'] == 0 and
            checked['legacy_verification']['pairs_checked'] == checked['current_verification']['pairs_checked'] == 4851,
            'Partial-K-only assignment incorrectly accepted')
    decode.append(dict(name='fixed_K_with_all_free_edges_false', valid=False, fixed_mismatches=0,
                       legacy_check=checked['legacy_verification'], current_check=checked['current_verification']))
    flipped = list(base_model); flipped[0] = -flipped[0]
    checked = runner.decode_and_verify(flipped, candidate)
    require(not checked['valid'] and checked['fixed_edge_mismatch_count'] == 1, 'Wrong fixed unit accepted')
    decode.append(dict(name='flipped_fixed_edge', valid=False, fixed_mismatches=1))
    for name, mutate in [('missing_edge_variable', lambda d: d.pop()),
                         ('duplicate_edge_variable', lambda d: d.__setitem__(0, d[1])),
                         ('zero_literal', lambda d: d.__setitem__(0, 0)),
                         ('boolean_literal', lambda d: d.__setitem__(0, True)),
                         ('auxiliary_in_edge_model', lambda d: d.__setitem__(0, 3487))]:
        model = list(base_model); mutate(model)
        try:
            runner.decode_and_verify(model, candidate)
        except ValueError as exc:
            decode.append(dict(name=name, observed='REJECT', reason=str(exc)))
        else:
            raise ValueError('Malformed edge model accepted: '+name)
    sat, unsat = args.out/'tiny_sat.cnf', args.out/'tiny_unsat.cnf'
    with sat.open('x', encoding='ascii') as stream:
        stream.write('p cnf 3 3\n1 0\n-2 0\n2 3 0\n')
    with unsat.open('x', encoding='ascii') as stream:
        stream.write('p cnf 1 2\n1 0\n-1 0\n')
    outputs.update({runner.key(p): runner.digest(p) for p in (sat, unsat)})
    engine = []
    for name, path, seconds, expected in [('tiny_sat', sat, 10, 'SAT_MODEL_UNVALIDATED'),
                                           ('tiny_unsat', unsat, 10, 'UNSAT_UNVERIFIED'),
                                           ('startup_deadline', sat, 1e-9, 'UNKNOWN')]:
        result = runner.solve_bounded(path, 100, seconds)
        require(result['solver_result'] == expected, 'Unexpected tiny solver result: '+name)
        if name == 'tiny_sat':
            require(set(result['edge_model']) == {1, -2, 3}, 'Tiny SAT assignment does not satisfy the formula')
        if name == 'startup_deadline':
            require(result['reason'] == 'WALL_TIME_LIMIT_INCLUDING_PARSE_AND_LOAD' and result['wall_seconds'] < 10,
                    'Wall-time bound not enforced')
        engine.append(dict(name=name, **result))
    require(not (ROOT/'submission.txt').exists() and not list(args.out.glob('validated_graph.json')), 'Unexpected graph publication')
    require(all(runner.digest(name) == expected for name, expected in inputs.items()), 'Frozen input/source changed')
    report = dict(status='FIXED_OVERLAP_SAT_TINY_ENGINE_AND_SYNTHETIC_VALIDATION_CONTROLS_PASS',
                  inputs_sha256=inputs, outputs_sha256=outputs, cli_controls=cli, decode_controls=decode, engine_controls=engine,
                  python_version=sys.version, python_executable=sys.executable,
                  research_CNF_solver_invocations=0, tiny_solver_worker_invocations=3,
                  validated_99_vertex_SAT_positive_available=False, graph_witness_created=False, root_submission_written=False,
                  elapsed_seconds=time.perf_counter()-started,
                  scope='Real fixed-CNF inputs only preflighted; tiny formulas exercise CaDiCaL SAT/UNSAT/deadline. Synthetic full99 models and mapping corruptions are rejected. No research-K solve, checked UNSAT proof or valid99 positive witness is claimed.')
    write(args.out/'report.json', report)
    print(json.dumps({k: report[k] for k in ('status', 'research_CNF_solver_invocations', 'tiny_solver_worker_invocations', 'elapsed_seconds')}))


if __name__ == '__main__':
    main()
