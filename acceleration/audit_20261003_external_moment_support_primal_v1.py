"""Exact raw-primal certificate checker; no reconstruction-producer imports."""
import argparse
import copy
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import re
import sys

from command_deadline import CommandDeadline
import audit_20261003_external_neighborhood_moments_v3 as Q

ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()
SPEC = SELF.with_name(SELF.stem + '_spec.md')
PRODUCER = 'acceleration/reconstruct_20261003_external_moment_support_primal_v1.py'
PINS = {
    PRODUCER: 'da6e703ca22ad757b1da84bf85ebf9e0e476eb61994b7e2bbbc34c609cb58d9d',
    PRODUCER.replace('.py', '_spec.md'): '8464f400f0f5c2f48bee6b39f0a4da1e7a303600616c5727d48c5c8b5e88e23b',
    'acceleration/audit_20261003_external_neighborhood_moments_v3.py': '4a7f555c18475482dd9575e923f48939ceba165229b10e599358cde8b7f6f90c',
    'acceleration/audit_20261003_external_neighborhood_moments_v3_spec.md': 'a1fc166c2fe77216ca1bfe3ef61edcd59b3e55fa7781f52b8ebc452218114e71',
    'acceleration/command_deadline.py': '9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9',
    'acceleration/run_compute_command.py': '593a9feed6250739dc9672338df23ab171fc9a6a6db4196c1feb312efa33957a',
    'pyproject.toml': '273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339',
    'uv.lock': 'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',
}
BASE = 'acceleration/results/20261003_external_neighborhood_moment_seventeen_base01'
GATE = 'acceleration/results/20261003_independent_review/external_neighborhood_moments_seventeen_base_full01/summary.json'
GATE_SHA = 'af6b7877acb4519ca004707a46b21150d46a63f6ac8b57020656570a56ec099d'
ACCEPTANCE = 'acceleration/results/20261003_external_moment_checker_v3_root_actual17_full_acceptance01.json'
ACCEPTANCE_SHA = '259d4cce6b54d09ddad3b2d786cf24ee9fe1c365a7a5862d86e4c1a0010fdc65'
ORIGINAL = {
    BASE + '/summary.json': '23fc6d633fe626a0a8141d3f974c415b6a559c6b67c60f231de8c412b63672d0',
    BASE + '/seventeen_base/model.json': 'd5f1afaf937b75c22f6e5d5c376a36f55f9326dc131399011a5502598742a3f9',
    BASE + '/seventeen_base/types.json': '4799c4603dc949ace22184c5742816eb0dbfe1bd6ea9b2d0ff407678e13de46a',
    BASE + '/seventeen_base/universe.json': '9fa4a59ef9edab7947ed3eec648a253b74f713dba80bb1f3567de77fb6edf780',
    BASE + '/seventeen_base/numerical_guidance.json': 'ee318f07cc7d7d21c4c232b5ef7bca5c8a0da5e5dc15efa3b2b6c35a581c4461',
}
CAL_STATUS = 'INDEPENDENT_EXTERNAL_MOMENT_SUPPORT_PRIMAL_V1_CALIBRATION_PASS'
FULL_STATUS = 'INDEPENDENT_EXTERNAL_MOMENT_SUPPORT_PRIMAL_V1_COMPLETE_PASS'
need, same, tick, strict_json = Q.need, Q.same, Q.tick, Q.strict_json


def identity_map(mapping, stage):
    need(type(mapping) is dict and mapping, stage)
    for name, sha in mapping.items():
        need(type(name) is str and name and '\\' not in name
             and not name.startswith('/') and ':' not in name
             and all(part not in ('', '.', '..') for part in name.split('/'))
             and name != 'CLAIMS.yaml' and not name.startswith('.git/'), stage)
        need(type(sha) is str and re.fullmatch('[0-9a-f]{64}', sha) is not None, stage)
    return mapping


def original_header(gate):
    need(type(gate) is dict and gate.get('status') == 'INDEPENDENT_EXTERNAL_NEIGHBOR_MOMENTS_V1_COMPLETE_PASS'
         and gate.get('producer') == '/root' and gate.get('verifier') == '/root/native_driver'
         and gate.get('method') == 'independent_artifact_check' and gate.get('target_resolution') == 'NONE'
         and type(gate.get('checker_implementation_version')) is int
         and gate['checker_implementation_version'] == 3, 'ORIGINAL_GATE_HEADER')
    mapping = identity_map(gate.get('inputs_sha256'), 'ORIGINAL_GATE_MAP')
    need(all(mapping.get(name) == sha for name, sha in ORIGINAL.items()), 'ORIGINAL_GATE_BINDING')
    science = gate.get('checked_scope', {}).get('science', {})
    need(type(science) is dict and same({key: science.get(key) for key in
         ['full_mask_universe', 'eligible_types', 'rows', 'complete_induced_products', 'exact_primal']},
         dict(full_mask_universe=131072, eligible_types=534, rows=154,
              complete_induced_products=289, exact_primal=None)), 'ORIGINAL_GATE_SCOPE')
    return mapping


def producer_header(report):
    need(type(report) is dict and report.get('status') == 'CANDIDATE_EXACT_MOMENT_SUPPORT_PRIMAL_V1_PENDING_INDEPENDENT_CHECK'
         and report.get('producer') == '/root/checkpoint_audit'
         and report.get('source_author') == '/root/checkpoint_audit'
         and report.get('independent_verifier_required') == '/root/native_driver'
         and report.get('independent_approval') is False and report.get('mode') == 'reconstruct'
         and report.get('target_resolution') == 'NONE' and report.get('graph_completion_claimed') is False
         and report.get('ledger_index_git_mutations') is False, 'PRODUCER_HEADER')
    need(type(report.get('LP_calls')) is int and report['LP_calls'] == 0
         and type(report.get('model_reenumerations')) is int and report['model_reenumerations'] == 0,
         'PRODUCER_FORBIDDEN_CALLS')
    need(same(report.get('controls'), dict(positive=2, strict_negative=3, total=5)), 'PRODUCER_CONTROL_COUNTS')
    identity_map(report.get('inputs_sha256'), 'PRODUCER_INPUT_MAP')
    identity_map(report.get('outputs_sha256'), 'PRODUCER_OUTPUT_MAP')


def receipt(plan, manifest, terminal, report, packet_name, supervision_name):
    command = plan.get('command')
    need(type(command) is list and all(type(word) is str for word in command)
         and command.count('--') == 1 and command[:3] == [
             'C:/Users/ikuto/projects/conway-99-graph/build/research-venv/Scripts/python.exe',
             '-B', 'acceleration/run_compute_command.py'], 'PLAN_COMMAND')
    child = command[command.index('--') + 1:]
    need(child[:6] == ['C:/Users/ikuto/.local/bin/uv.exe', 'run', '--locked', '--offline', 'python', '-B']
         and same(plan.get('child_argv'), child) and same(plan.get('supervisor_argv'), command)
         and same(manifest.get('command'), child), 'CHILD_COMMAND')
    worker = [PRODUCER, 'reconstruct', '--seconds', '550', '--out', packet_name,
              '--source-sha256', PINS[PRODUCER], '--spec-sha256', PINS[PRODUCER.replace('.py', '_spec.md')],
              '--full-gate', GATE, '--full-gate-sha256', GATE_SHA]
    need(same(child[6:], worker) and type(report.get('command')) is list
         and len(report['command']) == len(worker) + 1 and report['command'][1:] == worker,
         'WORKER_COMMAND')
    need(manifest.get('source_sha256') == PINS['acceleration/run_compute_command.py']
         and manifest.get('cwd') == str(ROOT) and report.get('cwd') == str(ROOT), 'SUPERVISOR_SOURCE_CWD')
    need(manifest.get('automatic_retry') is False and manifest.get('cumulative_across_commands') is False,
         'SUPERVISOR_RETRY')
    for option, key, wanted in [('--seconds', 'seconds', 600),
                                ('--shutdown-reserve-seconds', 'shutdown_reserve_seconds', 20)]:
        expected_count = 2 if option == '--seconds' else 1
        need(command.count(option) == expected_count, 'PLAN_ALLOCATION')
        need(command[command.index(option) + 1] == str(wanted)
             and type(manifest.get(key)) in (int, float) and manifest[key] == wanted, 'PLAN_ALLOCATION')
    need(command[command.index('--out') + 1] == supervision_name, 'SUPERVISOR_OUTPUT')
    need(type(manifest.get('invocation_id')) is str and bool(manifest['invocation_id'])
         and terminal.get('invocation_id') == manifest['invocation_id']
         and type(terminal.get('command_exit_code')) is int and terminal['command_exit_code'] == 0
         and terminal.get('error') is None, 'TERMINAL')
    cleanup = terminal.get('cleanup')
    need(type(cleanup) is dict and cleanup.get('reaped') is True
         and cleanup.get('job_active_zero_observed') is True
         and type(cleanup.get('actual_exit_code')) is int and cleanup['actual_exit_code'] == 0
         and type(cleanup.get('cleanup_errors')) is list and cleanup['cleanup_errors'] == [], 'CLEANUP')
    return child


def candidate_counts(candidate, primal, result):
    keys = {'complete_moment_rows', 'full_primal_coordinates', 'selected_support_columns', 'rank',
            'free_support_variables', 'nonnegative_exact_rational', 'integer', 'nonzero_exact_coordinates'}
    need(type(candidate) is dict and set(candidate) == keys, 'CANDIDATE_FIELDS')
    values = [Q.rational(value) for value in primal['values']]
    expected = dict(complete_moment_rows=154, full_primal_coordinates=534, selected_support_columns=109,
                    nonnegative_exact_rational=True, integer=result['integer'],
                    nonzero_exact_coordinates=sum(value != 0 for value in values))
    need(same({key: candidate[key] for key in expected}, expected), 'CANDIDATE_COUNTS')
    need(type(candidate['rank']) is int and 0 <= candidate['rank'] <= 109
         and type(candidate['free_support_variables']) is int
         and candidate['free_support_variables'] == 109 - candidate['rank'], 'RREF_DECLARED_COUNTS')
    return values


def synthetic_frames():
    child = ['C:/Users/ikuto/.local/bin/uv.exe', 'run', '--locked', '--offline', 'python', '-B',
             PRODUCER, 'reconstruct', '--seconds', '550', '--out', 'acceleration/results/synthetic_primal',
             '--source-sha256', PINS[PRODUCER], '--spec-sha256', PINS[PRODUCER.replace('.py', '_spec.md')],
             '--full-gate', GATE, '--full-gate-sha256', GATE_SHA]
    command = ['C:/Users/ikuto/projects/conway-99-graph/build/research-venv/Scripts/python.exe', '-B',
               'acceleration/run_compute_command.py', '--seconds', '600', '--shutdown-reserve-seconds', '20',
               '--allocation-reason', 'synthetic', '--success-criterion', 'synthetic',
               '--verification-criterion', 'synthetic', '--out', 'acceleration/results/synthetic_supervision', '--'] + child
    plan = dict(command=command, supervisor_argv=command, child_argv=child)
    manifest = dict(command=child, source_sha256=PINS['acceleration/run_compute_command.py'], cwd=str(ROOT),
                    automatic_retry=False, cumulative_across_commands=False, seconds=600,
                    shutdown_reserve_seconds=20, invocation_id='synthetic')
    terminal = dict(invocation_id='synthetic', command_exit_code=0, error=None,
                    cleanup=dict(reaped=True, job_active_zero_observed=True, actual_exit_code=0, cleanup_errors=[]))
    report = dict(status='CANDIDATE_EXACT_MOMENT_SUPPORT_PRIMAL_V1_PENDING_INDEPENDENT_CHECK',
                  producer='/root/checkpoint_audit', source_author='/root/checkpoint_audit',
                  independent_verifier_required='/root/native_driver', independent_approval=False,
                  mode='reconstruct', target_resolution='NONE', graph_completion_claimed=False,
                  ledger_index_git_mutations=False, LP_calls=0, model_reenumerations=0,
                  controls=dict(positive=2, strict_negative=3, total=5), inputs_sha256={'x': 'a' * 64},
                  outputs_sha256={'y': 'b' * 64}, command=['synthetic_python'] + child[6:], cwd=str(ROOT))
    gate = dict(status='INDEPENDENT_EXTERNAL_NEIGHBOR_MOMENTS_V1_COMPLETE_PASS', producer='/root',
                verifier='/root/native_driver', method='independent_artifact_check', target_resolution='NONE',
                checker_implementation_version=3, inputs_sha256=ORIGINAL,
                checked_scope=dict(science=dict(full_mask_universe=131072, eligible_types=534,
                     rows=154, complete_induced_products=289, exact_primal=None)))
    return dict(plan=plan, manifest=manifest, terminal=terminal, report=report, gate=gate)


def own_calibration(deadline, save):
    columns = [{'mask': 0, 'coefficient': [2, 1]}, {'mask': 1, 'coefficient': [1, 2]}]
    rational_primal = dict(status='CANDIDATE_EXACT_MOMENT_PRIMAL', values=['1/3', '1/3'], integer=False)
    positive = []
    for label, raw, rhs in [('fractional', rational_primal, [1, 1]),
         ('integral', dict(status='CANDIDATE_EXACT_MOMENT_PRIMAL', values=['1', '0'], integer=True), [2, 1]),
         ('zero', dict(status='CANDIDATE_EXACT_MOMENT_PRIMAL', values=['0', '0'], integer=True), [0, 0])]:
        result = Q.check_primal(raw, columns, rhs)
        save('positive_' + label + '.json', dict(primal=raw, columns=columns, rhs=rhs, result=result))
        positive.append(label)
    base = synthetic_frames()
    def frame_check(value):
        original_header(value['gate']); producer_header(value['report'])
        receipt(value['plan'], value['manifest'], value['terminal'], value['report'],
                'acceleration/results/synthetic_primal', 'acceleration/results/synthetic_supervision')
    frame_check(base); save('positive_framing.json', base); positive.append('framing')
    zero_primal = dict(status='CANDIDATE_EXACT_MOMENT_PRIMAL', values=['0'] * 534, integer=True)
    zero_counts = dict(complete_moment_rows=154, full_primal_coordinates=534, selected_support_columns=109,
                       rank=0, free_support_variables=109, nonnegative_exact_rational=True,
                       integer=True, nonzero_exact_coordinates=0)
    candidate_counts(zero_counts, zero_primal, dict(integer=True))
    save('positive_candidate_counts.json', dict(candidate=zero_counts, primal=zero_primal,
                                               synthetic_metadata_only=True))
    positive.append('candidate_counts')
    negatives = []
    def reject(label, value, expected, function):
        tick(deadline); save('negative_' + label + '.json', value)
        observed = None
        try:
            function(value)
        except ValueError as error:
            observed = str(error)
        need(observed == expected, 'CONTROL_STAGE:' + label)
        negatives.append(dict(case=label, expected_stage=expected, actual_stage=observed))
    for label, key, value, stage in [
        ('status', 'status', 'PASS', 'PRIMAL_OBJECT'), ('extra', 'extra', 0, 'PRIMAL_OBJECT'),
        ('length', 'values', ['1/3'], 'PRIMAL_LENGTH'), ('float', 'values', [1.0, '1/3'], 'RATIONAL_STRING'),
        ('bool', 'values', [True, '1/3'], 'RATIONAL_STRING'), ('unreduced', 'values', ['2/6', '1/3'], 'RATIONAL_CANONICAL'),
        ('negative_zero', 'values', ['-0', '1/3'], 'RATIONAL_CANONICAL'),
        ('leading_zero', 'values', ['01', '1/3'], 'RATIONAL_STRING'),
        ('zero_denominator', 'values', ['1/0', '1/3'], 'RATIONAL_STRING'),
        ('negative', 'values', ['-1/3', '1/3'], 'PRIMAL_NONNEGATIVE'),
        ('integer_bool_truth', 'integer', True, 'PRIMAL_INTEGER_FLAG'),
        ('integer_numeric', 'integer', 0, 'PRIMAL_INTEGER_FLAG'),
        ('altered_row', 'values', ['0', '1/3'], 'PRIMAL_MOMENT')]:
        raw = copy.deepcopy(rational_primal); raw[key] = value
        reject('primal_' + label, raw, stage, lambda v: Q.check_primal(v, columns, [1, 1]))
    changes = [
        ('gate_status', ['gate', 'status'], 'PASS', 'ORIGINAL_GATE_HEADER'),
        ('gate_producer', ['gate', 'producer'], '/root/checkpoint_audit', 'ORIGINAL_GATE_HEADER'),
        ('gate_verifier', ['gate', 'verifier'], '/root/structural', 'ORIGINAL_GATE_HEADER'),
        ('gate_method', ['gate', 'method'], 'independent_derivation', 'ORIGINAL_GATE_HEADER'),
        ('gate_target', ['gate', 'target_resolution'], 'FOUND', 'ORIGINAL_GATE_HEADER'),
        ('gate_version_bool', ['gate', 'checker_implementation_version'], True, 'ORIGINAL_GATE_HEADER'),
        ('gate_scope_bool', ['gate', 'checked_scope', 'science', 'rows'], True, 'ORIGINAL_GATE_SCOPE'),
        ('gate_literal', ['gate', 'inputs_sha256', BASE + '/seventeen_base/types.json'], 'c' * 64, 'ORIGINAL_GATE_BINDING'),
        ('report_status', ['report', 'status'], 'PASS', 'PRODUCER_HEADER'),
        ('report_role', ['report', 'producer'], '/root/native_driver', 'PRODUCER_HEADER'),
        ('report_approved', ['report', 'independent_approval'], True, 'PRODUCER_HEADER'),
        ('report_LP_bool', ['report', 'LP_calls'], False, 'PRODUCER_FORBIDDEN_CALLS'),
        ('report_model_call', ['report', 'model_reenumerations'], 1, 'PRODUCER_FORBIDDEN_CALLS'),
        ('report_control_float', ['report', 'controls', 'total'], 5.0, 'PRODUCER_CONTROL_COUNTS'),
        ('report_bad_hash', ['report', 'outputs_sha256', 'y'], 'b' * 63, 'PRODUCER_OUTPUT_MAP'),
        ('report_mutable', ['report', 'inputs_sha256'], {'CLAIMS.yaml': 'a' * 64}, 'PRODUCER_INPUT_MAP'),
        ('plan_boundary', ['plan', 'command'], [], 'PLAN_COMMAND'),
        ('child_uv', ['plan', 'child_argv'], [], 'CHILD_COMMAND'),
        ('manifest_child', ['manifest', 'command'], [], 'CHILD_COMMAND'),
        ('worker_summary', ['report', 'command'], [], 'WORKER_COMMAND'),
        ('supervisor_source', ['manifest', 'source_sha256'], 'a' * 64, 'SUPERVISOR_SOURCE_CWD'),
        ('supervisor_cwd', ['manifest', 'cwd'], 'other', 'SUPERVISOR_SOURCE_CWD'),
        ('retry', ['manifest', 'automatic_retry'], True, 'SUPERVISOR_RETRY'),
        ('allocation_bool', ['manifest', 'seconds'], True, 'PLAN_ALLOCATION'),
        ('allocation_float_changed', ['manifest', 'seconds'], 600.5, 'PLAN_ALLOCATION'),
        ('terminal_bool', ['terminal', 'command_exit_code'], False, 'TERMINAL'),
        ('terminal_id', ['terminal', 'invocation_id'], 'other', 'TERMINAL'),
        ('terminal_error', ['terminal', 'error'], 'error', 'TERMINAL'),
        ('reaped', ['terminal', 'cleanup', 'reaped'], False, 'CLEANUP'),
        ('group', ['terminal', 'cleanup', 'job_active_zero_observed'], False, 'CLEANUP'),
        ('cleanup_bool', ['terminal', 'cleanup', 'actual_exit_code'], False, 'CLEANUP'),
        ('cleanup_float', ['terminal', 'cleanup', 'actual_exit_code'], 0.0, 'CLEANUP'),
        ('cleanup_errors', ['terminal', 'cleanup', 'cleanup_errors'], ['error'], 'CLEANUP')]
    for label, path, value, stage in changes:
        frame = copy.deepcopy(base); current = frame
        for key in path[:-1]:
            current = current[key]
        current[path[-1]] = value
        reject(label, frame, stage, frame_check)
    for label, key, value, stage in [
        ('extra', 'extra', 0, 'CANDIDATE_FIELDS'), ('row_bool', 'complete_moment_rows', True, 'CANDIDATE_COUNTS'),
        ('coordinate_float', 'full_primal_coordinates', 534.0, 'CANDIDATE_COUNTS'),
        ('support_float', 'selected_support_columns', 109.0, 'CANDIDATE_COUNTS'),
        ('nonnegative_number', 'nonnegative_exact_rational', 1, 'CANDIDATE_COUNTS'),
        ('wrong_integer', 'integer', False, 'CANDIDATE_COUNTS'),
        ('nonzero_bool', 'nonzero_exact_coordinates', False, 'CANDIDATE_COUNTS'),
        ('rank_bool', 'rank', False, 'RREF_DECLARED_COUNTS'),
        ('rank_float', 'rank', 0.0, 'RREF_DECLARED_COUNTS'),
        ('free_bool', 'free_support_variables', True, 'RREF_DECLARED_COUNTS')]:
        counts = copy.deepcopy(zero_counts); counts[key] = value
        reject('candidate_' + label, counts, stage,
               lambda v: candidate_counts(v, zero_primal, dict(integer=True)))
    for label, raw, stage in [('duplicate_json', b'{"x":0,"x":1}', 'JSON_DUPLICATE'),
                              ('nonfinite_json', b'{"x":NaN}', 'JSON_NONFINITE')]:
        observed = None
        try:
            strict_json(raw)
        except ValueError as error:
            observed = str(error)
        need(observed == stage, 'CONTROL_STAGE:' + label)
        save(label + '.json', dict(raw_utf8=raw.decode('utf8'), expected_stage=stage, actual_stage=observed))
        negatives.append(dict(case=label, expected_stage=stage, actual_stage=observed))
    need(len(positive) == 5 and len(negatives) == 58, 'CONTROL_POPULATION')
    save('controls.json', dict(positive=positive, precise_negative=negatives,
                              actual_producer_output_read=False, actual17_model_read=False))
    return dict(positive_cases=5, precise_negative_cases=58,
                actual_producer_output_read=False, actual17_model_read=False)


def full_check(args, deadline, read, pin):
    required = ['calibration', 'calibration_sha256', 'producer_root', 'producer_summary_sha256',
                'producer_plan', 'producer_plan_sha256', 'supervision_out',
                'supervisor_manifest_sha256', 'supervisor_summary_sha256']
    need(all(getattr(args, key) is not None for key in required), 'FULL_ARGUMENTS')
    cal = read(args.calibration, args.calibration_sha256)
    need(cal.get('status') == CAL_STATUS and cal.get('producer') == '/root/checkpoint_audit'
         and cal.get('verifier') == '/root/native_driver' and cal.get('method') == 'independent_artifact_check'
         and cal.get('target_resolution') == 'NONE' and cal.get('source_sha256') == pin(SELF)[1]
         and cal.get('spec_sha256') == pin(SPEC)[1]
         and same(cal.get('checked_scope'), dict(positive_cases=5, precise_negative_cases=58,
                   actual_producer_output_read=False, actual17_model_read=False)), 'CALIBRATION_HEADER')
    for key in ['inputs_sha256', 'outputs_sha256']:
        for name, sha in identity_map(cal.get(key), 'CALIBRATION_MAP').items():
            pin(ROOT / name, sha)
    gate = read(ROOT / GATE, GATE_SHA)
    closure = original_header(gate)
    for name, sha in closure.items():
        pin(ROOT / name, sha)
    acceptance = read(ROOT / ACCEPTANCE, ACCEPTANCE_SHA)
    need(acceptance.get('schema') == 'ROOT_ACTUAL17_FULL_INDEPENDENT_CHECK_ACCEPTANCE_V1'
         and acceptance.get('outcome') == 'ACCEPT_EXACT_FIXED17_MODEL_AND_POSITIVE_GRAM_ONLY', 'ROOT_ACCEPTANCE')
    plan = read(args.producer_plan, args.producer_plan_sha256)
    manifest = read(args.supervision_out / 'manifest.json', args.supervisor_manifest_sha256)
    terminal = read(args.supervision_out / 'summary.json', args.supervisor_summary_sha256)
    packet = args.producer_root.resolve()
    need(packet.is_relative_to(ROOT / 'acceleration/results') and packet.is_dir()
         and not packet.is_relative_to(ROOT / BASE), 'PRODUCER_NAMESPACE')
    report = read(packet / 'summary.json', args.producer_summary_sha256)
    producer_header(report)
    receipt(plan, manifest, terminal, report, packet.relative_to(ROOT).as_posix(),
            args.supervision_out.resolve().relative_to(ROOT).as_posix())
    for name, sha in report['inputs_sha256'].items():
        pin(ROOT / name, sha)
    need(all(report['inputs_sha256'].get(name) == sha for name, sha in PINS.items()
             if name not in ['acceleration/audit_20261003_external_neighborhood_moments_v3.py',
                             'acceleration/audit_20261003_external_neighborhood_moments_v3_spec.md'])
         and report['inputs_sha256'].get(GATE) == GATE_SHA, 'PRODUCER_REQUIRED_INPUTS')
    need(all(report['inputs_sha256'].get(name) == sha for name, sha in closure.items()), 'PRODUCER_GATE_CLOSURE')
    actual_files = {p.relative_to(ROOT).as_posix() for p in packet.rglob('*')
                    if p.is_file() and p != packet / 'summary.json'}
    need(set(report['outputs_sha256']) == actual_files, 'OUTPUT_POPULATION')
    for name, sha in report['outputs_sha256'].items():
        path = (ROOT / name).resolve()
        need(path.is_relative_to(packet), 'OUTPUT_NAMESPACE'); pin(path, sha)
    note = pin(ROOT / 'docs/CANDIDATE_20261003_SEVENTEEN_POINT_EXTERNAL_NEIGHBOR_MOMENTS_V1.md',
               Q.PINS['docs/CANDIDATE_20261003_SEVENTEEN_POINT_EXTERNAL_NEIGHBOR_MOMENTS_V1.md'])[0].read_text(encoding='utf8')
    table = note.split('The particular base')[1].split('ROOT independently')[0]
    triples = [tuple(map(int, values)) for values in re.findall(r'\((\d+),(\d+),(\d+)\)', table)]
    need(len(triples) == 12 and all(len(set(t)) == 3 and all(0 <= v < 17 for v in t) for t in triples), 'LITERAL_BASE')
    edges = [e for triple in triples for e in itertools.combinations(sorted(triple), 2)]
    need(len(set(edges)) == len(edges), 'LITERAL_BASE_PAIRS')
    h = [[int(u != v and tuple(sorted((u, v))) in set(edges)) for v in range(17)] for u in range(17)]
    model = read(ROOT / (BASE + '/seventeen_base/model.json'), ORIGINAL[BASE + '/seventeen_base/model.json'])
    columns = read(ROOT / (BASE + '/seventeen_base/types.json'), ORIGINAL[BASE + '/seventeen_base/types.json'])
    universe = read(ROOT / (BASE + '/seventeen_base/universe.json'), ORIGINAL[BASE + '/seventeen_base/universe.json'])
    model, columns = Q.check_bundle(model, columns, universe, h, 99, 14, deadline)
    primal = read(packet / 'primal.json')
    result = Q.check_primal(primal, columns, model['right_hand_side']); tick(deadline)
    values = candidate_counts(report.get('exact_candidate'), primal, result)
    guidance = read(ROOT / (BASE + '/seventeen_base/numerical_guidance.json'), ORIGINAL[BASE + '/seventeen_base/numerical_guidance.json'])
    numeric = guidance.get('primal_float64')
    need(type(numeric) is list and len(numeric) == 534, 'ORIGINAL_SUPPORT_LENGTH')
    support = [i for i, value in enumerate(numeric) if value > 0.0]
    need(len(support) == 109 and all(value == 0 for i, value in enumerate(values) if i not in support), 'SUPPORT_EMBEDDING')
    wanted_support = dict(selection_rule='All saved finite numeric values strictly >0.0; no tolerance',
         ordered_type_indices=support, ordered_masks=[columns[i]['mask'] for i in support],
         numeric_values_are_support_guidance_only=True, saved_numeric_values=[numeric[i] for i in support])
    need(same(read(packet / 'support.json'), wanted_support), 'SUPPORT_LITERAL')
    rows = [dict(row=i, label=model['row_labels'][i], computed=str(Fraction(rhs)), rhs=rhs, exactly_equal=True)
            for i, rhs in enumerate(model['right_hand_side'])]
    need(same(read(packet / 'row_checks.json'), rows), 'ROW_RECEIPT')
    candidate = report['exact_candidate']
    expected_files = {'support.json', 'rref.json', 'row_checks.json', 'primal.json', 'controls.json'}
    labels = ['unique_rational', 'free_variable_zero', 'inconsistent_rows', 'negative_solution', 'bool_coefficient']
    expected_files |= {'control_' + label + '.json' for label in labels}
    expected_files |= {'pivot_%03d.json' % rank for rank in range(10, candidate['rank'] + 1, 10)}
    need({p.relative_to(packet).as_posix() for p in packet.rglob('*') if p.is_file() and p != packet / 'summary.json'}
         == expected_files, 'EXACT_PACKET_FILES')
    return dict(complete_mask_decisions=131072, complete_induced_cn_products=289,
                complete_eligible_types=534, complete_moment_equations=154, complete_primal_coordinates=534,
                exact_nonnegative_rational=True, integer=result['integer'],
                nonzero_exact_coordinates=sum(value != 0 for value in values),
                selected_numeric_support_columns=109, complete_packet_files=len(actual_files),
                graph_completion_proved=False, integer_vertex_allocation_proved=False,
                RREF_algorithm_or_rank_independently_replayed=False,
                producer_pivot_and_control_files_authenticated_only=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode', choices=['calibrate', 'full'])
    p.add_argument('--seconds', type=float, required=True)
    p.add_argument('--out', type=Path, required=True)
    for key in ['calibration', 'producer-root', 'producer-plan', 'supervision-out']:
        p.add_argument('--' + key, type=Path)
        if key not in ['producer-root', 'supervision-out']:
            p.add_argument('--' + key + '-sha256')
    for key in ['producer-summary-sha256', 'supervisor-manifest-sha256', 'supervisor-summary-sha256']:
        p.add_argument('--' + key)
    args = p.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='Independent certificate equations and exact artifact/receipt framing; all work inclusive, twenty-second save reserve')
    out = args.out.resolve()
    need(out.is_relative_to(ROOT / 'acceleration/results') and not out.exists(), 'FRESH_OUTPUT')
    out.mkdir(parents=True); pins = {}
    def digest(path):
        tick(deadline); sha = hashlib.sha256()
        with path.open('rb') as stream:
            while block := stream.read(1024 * 1024):
                sha.update(block); tick(deadline)
        tick(deadline); return sha.hexdigest()
    def pin(path, expected=None):
        path = Path(path).resolve()
        need(path.is_relative_to(ROOT) and path.is_file(), 'INPUT_PATH')
        name = path.relative_to(ROOT).as_posix()
        need(name != 'CLAIMS.yaml' and not name.startswith('.git/'), 'MUTABLE_INPUT')
        sha = digest(path)
        need(expected is None or type(expected) is str and sha == expected, 'INPUT_IDENTITY:' + name)
        need(name not in pins or pins[name] == sha, 'INPUT_CHANGED')
        pins[name] = sha; return path, sha
    def read(path, expected=None):
        value = strict_json(pin(path, expected)[0].read_bytes()); tick(deadline); return value
    def save(name, value):
        tick(deadline); raw = (json.dumps(value, allow_nan=False, indent=2) + '\n').encode('utf8'); tick(deadline)
        with (out / name).open('xb') as stream:
            for start in range(0, len(raw), 1024 * 1024):
                stream.write(raw[start:start + 1024 * 1024]); tick(deadline)
        tick(deadline)
    try:
        for name, sha in PINS.items():
            pin(ROOT / name, sha)
        pin(SELF); pin(SPEC)
        if args.mode == 'calibrate':
            need(all(getattr(args, key) is None for key in ['calibration', 'calibration_sha256',
                 'producer_root', 'producer_plan', 'producer_plan_sha256', 'supervision_out',
                 'producer_summary_sha256', 'supervisor_manifest_sha256', 'supervisor_summary_sha256']), 'CAL_NO_ACTUAL_INPUTS')
            scope = own_calibration(deadline, save); status = CAL_STATUS
        else:
            scope = full_check(args, deadline, read, pin); status = FULL_STATUS
        for name, sha in list(pins.items()):
            pin(ROOT / name, sha)
        outputs = {path.relative_to(ROOT).as_posix(): digest(path) for path in sorted(out.iterdir()) if path.is_file()}
        save('summary.json', dict(status=status, producer='/root/checkpoint_audit', verifier='/root/native_driver',
             method='independent_artifact_check', target_resolution='NONE', implementation_version=1,
             timestamp=datetime.now(timezone.utc).isoformat(), command=[sys.executable, *sys.argv],
             source_sha256=pins[SELF.relative_to(ROOT).as_posix()], spec_sha256=pins[SPEC.relative_to(ROOT).as_posix()],
             inputs_sha256=pins, outputs_sha256=outputs, checked_scope=scope,
             shared_checking_core='Unchanged independent Native moment V3 reconstruction and check_primal',
             producer_code_imports=0, mathematical_graph_completion_claimed=False, deadline=deadline.status()))
        tick(deadline); return 0
    except BaseException as error:
        if (out / 'summary.json').exists():
            (out / 'summary.json').rename(out / 'summary.not_approved.json')
        (out / 'failure.json').write_text(json.dumps(dict(error=repr(error), inputs_sha256=pins,
             deadline=deadline.status(), automatic_retry=False, outputs_preserved=True, target_resolution='NONE')) + '\n', encoding='utf8')
        raise


if __name__ == '__main__':
    raise SystemExit(main())
