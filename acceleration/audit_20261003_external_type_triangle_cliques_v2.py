"""Independent complete saved-vector triangle diagnostic; no producer imports."""
import argparse
import copy
import hashlib
import io
import json
import math
import re
import sys
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()
SPEC = SELF.with_name(SELF.stem + '_spec.md')
PRODUCER = 'acceleration/survey_20261003_external_type_triangle_cliques_v2.py'
PRODUCER_SPEC = PRODUCER.replace('.py', '_spec.md')
PYTHON = 'C:/Users/ikuto/projects/conway-99-graph/build/research-venv/Scripts/python.exe'
UV = 'C:/Users/ikuto/.local/bin/uv.exe'
SUP = 'acceleration/run_compute_command.py'
PINS = {
    PRODUCER: 'be5edffa96cd9619eab5a6976b4a786b89631aa63e6685c04cf6a01471fd979c',
    PRODUCER_SPEC: 'b0c0ceecbee43cdbd32a3735981b6d6e0c53fd7c202be1e1ecdc852ae8a681f2',
    'acceleration/command_deadline.py': '9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9',
    SUP: '593a9feed6250739dc9672338df23ab171fc9a6a6db4196c1feb312efa33957a',
    'pyproject.toml': '273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339',
    'uv.lock': 'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',
}
MODEL = 'acceleration/results/20261003_external_moment_triple_lp01/triple_system.json'
PRIMAL = 'acceleration/results/20261003_external_moment_triple_lp01/triple_primal.json'
TYPES = 'acceleration/results/20261003_external_moment_outside_cn_filter01/types.json'
LEMMA = 'acceleration/results/20261003_independent_review/exterior_type_pair_triple_caps01/summary.json'
FIXED = {
    MODEL: '6226df2a75d8bf296b77f8e636a8e3fc5d1764d378dd7779cd08bad2d9a4c792',
    PRIMAL: 'e311192634b43b00e5c0b2e4d34cff62bcb38aaa59de1aae91450b5e004218da',
    TYPES: '87d0272e244f60f1eefa06d3a0b2d0179a275791f7bb586992b16f648595bad2',
    LEMMA: 'd3e2f27aca979839edb3e612cd825d2cce18346d81ca2bfa868e86b6b1baffee',
}
CAL = 'INDEPENDENT_EXTERNAL_TYPE_TRIANGLE_CLIQUES_V1_CALIBRATION_PASS'
CONTROLS = 'INDEPENDENT_EXTERNAL_TYPE_TRIANGLE_CLIQUES_V1_CONTROLS_PASS'
FULL = 'INDEPENDENT_EXTERNAL_TYPE_TRIANGLE_CLIQUES_V1_COMPLETE_PASS'
PRIMAL_GATE = 'INDEPENDENT_TRIPLE_CAPPED_EXTERNAL_MOMENT_CERTIFICATE_V1_COMPLETE_PASS'
PRIMAL_SOFTWARE = {
    'acceleration/audit_20261003_triple_capped_external_moment_certificate_v2.py': '6e292f9a127f29e6be210a0d8d2527c3021d9fc03aa2e19a071c857b42594963',
    'acceleration/audit_20261003_triple_capped_external_moment_certificate_v2_spec.md': '1a7d9915fa70ae381861fbf8acb41b431d148f4f58abba283dc4005fe1d213f0',
}
MEANING = ('Violations separate this exact rational point from necessary realizable-type clique inequalities; '
           'no whole-system infeasibility or target exclusion')


def need(condition, stage):
    if not condition:
        raise ValueError(stage)


def same(a, b):
    if type(a) is not type(b):
        return False
    if type(a) is dict:
        return set(a) == set(b) and all(same(a[k], b[k]) for k in a)
    if type(a) is list:
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    return a == b


def tick(deadline):
    state = deadline.status()
    need(not state['stop_required'] and state['remaining_seconds'] > 20, 'SAVE_RESERVE')


def strict_json(raw):
    need(type(raw) is bytes and len(raw) <= 64 * 1024**2, 'JSON_BYTES')
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, 'JSON_DUPLICATE')
            result[key] = value
        return result
    def nonfinite(_):
        raise ValueError('JSON_NONFINITE')
    return json.loads(raw.decode('utf8'), object_pairs_hook=pairs, parse_constant=nonfinite)


def fractions(raw, count):
    need(type(raw) is list and len(raw) == count, 'WEIGHT_SHAPE')
    values = []
    for text in raw:
        need(type(text) is str, 'WEIGHT_STRING')
        try:
            value = Fraction(text)
        except (ValueError, ZeroDivisionError):
            raise ValueError('WEIGHT_CANONICAL') from None
        need(str(value) == text, 'WEIGHT_CANONICAL')
        need(value >= 0, 'WEIGHT_NONNEGATIVE')
        values.append(value)
    return values


def sets_from_masks(masks, m):
    need(type(m) is int and 3 <= m <= 17, 'DOMAIN_INTEGER')
    need(type(masks) is list and all(type(mask) is int and 0 <= mask < 2**m for mask in masks), 'MASK_INTEGER')
    need(masks == sorted(set(masks)), 'MASK_ORDER')
    # Literal membership sets, distinct from the producer bit_count/intersection path.
    return [frozenset(u for u in range(m) if (mask // 2**u) % 2) for mask in masks]


def population(masks, weights, m):
    types = sets_from_masks(masks, m)
    values = fractions(weights, len(masks))
    return [dict(column=i, mask=masks[i], cardinality=len(types[i]), weight=str(values[i]))
            for i in range(len(masks)) if len(types[i]) >= 3 and values[i] > 0]


def compare_population(raw, masks, weights, m):
    expected = population(masks, weights, m)
    need(type(raw) is dict and set(raw) == {'source_first_columns', 'positive_exact_threshold', 'minimum_type_size', 'records'}, 'POPULATION_FIELDS')
    need(same([raw['source_first_columns'], raw['positive_exact_threshold'], raw['minimum_type_size']],
              [len(masks), '0', 3]), 'POPULATION_CRITERION')
    need(same(raw['records'], expected), 'POSITIVE_POPULATION')
    return expected


def common_cuts(masks, values, slacks, m, deadline):
    types = sets_from_masks(masks, m)
    need(len(values) == len(types), 'CUT_VALUE_SHAPE')
    need(type(slacks) is list and len(slacks) == math.comb(m, 3), 'CUT_SLACK_SHAPE')
    rows = []
    for a in range(m - 2):
        for b in range(a + 1, m - 1):
            for c in range(b + 1, m):
                tick(deadline)
                q = {a, b, c}
                total = sum((values[j] for j in range(len(types)) if q <= types[j]), Fraction(0))
                row = len(rows)
                need(total <= 1 and total + slacks[row] == 1, 'ORIGINAL_TRIPLE_SLACK')
                rows.append(dict(row=row, Q=[a, b, c], sum=str(total), slack=str(slacks[row]), holds=True))
    return rows


def compare_cuts(raw, expected):
    need(type(raw) is list and len(raw) == len(expected), 'CUT_POPULATION')
    for observed, wanted in zip(raw, expected):
        need(type(observed) is dict and set(observed) == set(wanted), 'CUT_FIELDS')
        need(same([observed['row'], observed['Q']], [wanted['row'], wanted['Q']]), 'CUT_IDENTITY')
        need(same(observed, wanted), 'CUT_VALUE')


class Records:
    """One JSON object per newline, strict final EOF; no retained large stream."""
    def __init__(self, stream, deadline):
        self.stream, self.deadline, self.count = stream, deadline, 0

    def expect(self, wanted, stage):
        tick(self.deadline)
        raw = self.stream.readline(1024**2 + 1)
        need(raw and len(raw) <= 1024**2 and raw.endswith(b'\n'), stage + '_ROW')
        observed = strict_json(raw)
        need(type(observed) is dict and set(observed) == set(wanted), stage + '_FIELDS')
        need(same(observed, wanted), stage + '_VALUE')
        self.count += 1

    def finish(self, stage):
        tick(self.deadline)
        need(self.stream.read(1) == b'', stage + '_EXTRA')


def check_streams(selected, m, pair_reader, triangle_reader, violation_reader, deadline):
    types = sets_from_masks([r['mask'] for r in selected], m)
    weights = fractions([r['weight'] for r in selected], len(selected))
    n, edges, pair_bad = len(types), 0, 0
    incompatible = [[False] * n for _ in range(n)]
    for i in range(n - 1):
        for j in range(i + 1, n):
            tick(deadline)
            overlap = len(types[i].intersection(types[j]))
            edge = overlap >= 3
            total = weights[i] + weights[j]
            pair_reader.expect(dict(positions=[i, j], columns=[selected[i]['column'], selected[j]['column']],
                intersection_cardinality=overlap, incompatible=edge, weights=[str(weights[i]), str(weights[j])],
                exact_sum=str(total), pair_inequality_violated=edge and total > 1), 'PAIR')
            incompatible[i][j] = edge
            edges += int(edge)
            pair_bad += int(edge and total > 1)
    triangles, violations, maximum, visited = 0, 0, None, 0
    # Direct complete i<j<k loops, not the producer's neighbor-set intersection.
    for i in range(n - 2):
        for j in range(i + 1, n - 1):
            for k in range(j + 1, n):
                tick(deadline)
                visited += 1
                if not (incompatible[i][j] and incompatible[i][k] and incompatible[j][k]):
                    continue
                total = weights[i] + weights[j] + weights[k]
                wanted = dict(positions=[i, j, k], columns=[selected[t]['column'] for t in (i, j, k)],
                    masks=[selected[t]['mask'] for t in (i, j, k)], weights=[str(weights[t]) for t in (i, j, k)],
                    exact_sum=str(total), threshold='1', violated=total > 1)
                triangle_reader.expect(wanted, 'TRIANGLE')
                triangles += 1
                maximum = total if maximum is None or total > maximum else maximum
                if total > 1:
                    violation_reader.expect(wanted, 'VIOLATION')
                    violations += 1
    need(visited == math.comb(n, 3), 'COMPLETE_THREE_SUBSETS')
    for reader, stage in [(pair_reader, 'PAIR'), (triangle_reader, 'TRIANGLE'), (violation_reader, 'VIOLATION')]:
        reader.finish(stage)
    return dict(positive_types=n, unordered_pairs=math.comb(n, 2), incompatible_pairs=edges,
                violated_incompatible_pairs=pair_bad, all_three_subsets=visited, triangle_cliques=triangles,
                violated_triangle_cliques=violations, maximum_triangle_sum=None if maximum is None else str(maximum))


def in_memory_fixture(masks, weights, m, deadline):
    selected = population(masks, weights, m)
    types = sets_from_masks(masks, m)
    pairs, triangles, violations = [], [], []
    # This small fixture writer uses only literal sets; the checker consumes actual JSONL bytes.
    for i in range(len(selected)):
        for j in range(i + 1, len(selected)):
            a, b = selected[i], selected[j]
            overlap = len(types[a['column']] & types[b['column']])
            total = Fraction(a['weight']) + Fraction(b['weight'])
            pairs.append(dict(positions=[i, j], columns=[a['column'], b['column']], intersection_cardinality=overlap,
                incompatible=overlap >= 3, weights=[a['weight'], b['weight']], exact_sum=str(total),
                pair_inequality_violated=overlap >= 3 and total > 1))
            for k in range(j + 1, len(selected)):
                c = selected[k]
                if min(overlap, len(types[a['column']] & types[c['column']]), len(types[b['column']] & types[c['column']])) < 3:
                    continue
                total3 = total + Fraction(c['weight'])
                record = dict(positions=[i, j, k], columns=[x['column'] for x in (a, b, c)], masks=[x['mask'] for x in (a, b, c)],
                    weights=[x['weight'] for x in (a, b, c)], exact_sum=str(total3), threshold='1', violated=total3 > 1)
                triangles.append(record)
                if total3 > 1:
                    violations.append(copy.deepcopy(record))
    return dict(population=selected, pairs=pairs, triangles=triangles, violations=violations)


def memory_check(packet, m, deadline):
    def reader(key):
        raw = ''.join(json.dumps(r, separators=(',', ':')) + '\n' for r in packet[key]).encode('utf8')
        return Records(io.BytesIO(raw), deadline)
    return check_streams(packet['population'], m, reader('pairs'), reader('triangles'), reader('violations'), deadline)


def primal_header(raw):
    need(type(raw) is dict and raw.get('status') == PRIMAL_GATE and raw.get('producer') == '/root/checkpoint_audit'
         and raw.get('verifier') == '/root/structural' and raw.get('method') == 'independent_artifact_check'
         and raw.get('target_resolution') == 'NONE' and type(raw.get('implementation_version')) is int
         and raw['implementation_version'] == 2, 'EXACT_PRIMAL_GATE_HEADER')
    outcome = raw.get('outcome')
    need(type(outcome) is dict and outcome.get('certificate_kind') == 'primal'
         and all(type(outcome.get(k)) is int and outcome[k] == v for k, v in
             [('rows', 834), ('variables', 1152), ('original_variables', 472), ('original_equations', 154), ('triple_caps', 680)]),
         'EXACT_PRIMAL_GATE_SCOPE')


def primal_source(raw):
    need(type(raw.get('software')) is dict and type(raw.get('inputs_sha256')) is dict
         and all(raw['software'].get(k) == v and raw['inputs_sha256'].get(k) == v for k, v in PRIMAL_SOFTWARE.items()),
         'EXACT_PRIMAL_GATE_SOURCE')


def identity_map(raw, stage):
    need(type(raw) is dict and bool(raw), stage)
    for name, sha in raw.items():
        need(type(name) is str and '\\' not in name and ':' not in name and not name.startswith('/')
             and all(p not in ('', '.', '..') for p in name.split('/')) and name != 'CLAIMS.yaml'
             and not name.startswith('.git/') and type(sha) is str and re.fullmatch('[0-9a-f]{64}', sha), stage)
    return raw


def checker_applicability(raw, software, status):
    need(type(raw) is dict and raw.get('status') == status and raw.get('producer') == '/root/checkpoint_audit'
         and raw.get('verifier') == '/root/native_driver' and raw.get('method') == 'independent_artifact_check'
         and raw.get('target_resolution') == 'NONE' and type(raw.get('implementation_version')) is int and raw['implementation_version'] == 2
         and raw.get('source_sha256') == software[SELF.relative_to(ROOT).as_posix()]
         and raw.get('spec_sha256') == software[SPEC.relative_to(ROOT).as_posix()]
         and type(raw.get('inputs_sha256')) is dict
         and all(raw['inputs_sha256'].get(k) == v for k, v in software.items()), 'CHECKER_GATE_SOURCE')


def producer_header(raw, mode):
    need(type(raw) is dict and raw.get('status') == ('EXTERNAL_TYPE_TRIANGLE_CLIQUES_V1_AUTHOR_CALIBRATION_PASS'
         if mode == 'calibrate' else 'CANDIDATE_EXTERNAL_TYPE_TRIANGLE_CLIQUES_V1_COMPLETE')
         and raw.get('producer') == '/root/checkpoint_audit' and raw.get('independent_verifier_required') == '/root/native_driver'
         and raw.get('target_resolution') == 'NONE' and raw.get('source_sha256') == PINS[PRODUCER]
         and raw.get('spec_sha256') == PINS[PRODUCER_SPEC], 'PRODUCER_HEADER')
    need(all(type(raw.get(k)) is int and raw[k] == 0 for k in ('LP_calls', 'RREF_calls'))
         and raw.get('actual_primal_read') is (mode == 'survey') and raw.get('full_trajectory_or_graph_claim') is False, 'PRODUCER_SCOPE')
    need(mode != 'calibrate' or raw.get('outcome') is None, 'CALIBRATION_NOT_SURVEY')
    identity_map(raw.get('inputs_sha256'), 'PRODUCER_INPUT_MAP')
    identity_map(raw.get('outputs_sha256'), 'PRODUCER_OUTPUT_MAP')


def runtime(frames, mode, packet, supervision):
    plan, manifest, terminal, report = (frames[k] for k in ('plan', 'manifest', 'terminal', 'report'))
    profile = plan.get('calibration') if mode == 'calibrate' and 'command' not in plan else plan
    need(type(profile) is dict, 'PLAN_PROFILE')
    command = profile.get('command')
    need(type(command) is list and all(type(w) is str for w in command) and command.count('--') == 1
         and command[:2] == [PYTHON, SUP], 'PLAN_COMMAND')
    child = command[command.index('--') + 1:]
    need(child[:8] == [UV, 'run', '--locked', '--offline', '--python', PYTHON, PYTHON, '-B'], 'CHILD_PREFIX')
    need(same(profile.get('child_argv'), child) and same(manifest.get('command'), child), 'CHILD_COMMAND')
    expected = [PRODUCER, mode, '--seconds', '150' if mode == 'calibrate' else '550', '--out', packet,
                '--source-sha256', PINS[PRODUCER], '--spec-sha256', PINS[PRODUCER_SPEC]]
    if mode == 'survey':
        # The six dynamic path/hash words come from the actual reviewed literal vector, never fabricated endpoints.
        need(len(child) == 30 and child[18::2] == ['--calibration', '--calibration-sha256', '--full-gate',
             '--full-gate-sha256', '--root-full-acceptance', '--root-full-acceptance-sha256'], 'WORKER_OPTIONS')
        need(all(type(w) is str and w for w in child[19::2]), 'WORKER_OPTIONS')
        expected += child[18:]
    need(same(child[8:], expected), 'WORKER_COMMAND')
    need(same(profile.get('worker_argv'), [PYTHON, '-B', *expected]), 'WORKER_VECTOR')
    need(type(report.get('command')) is list and len(report['command']) == len(expected) + 1
         and type(report['command'][0]) is str and Path(report['command'][0]).resolve() == Path(PYTHON).resolve()
         and same(report['command'][1:], expected), 'REPORT_COMMAND')
    outer = 180 if mode == 'calibrate' else 600
    need(command[:6] == [PYTHON, SUP, '--seconds', str(outer), '--shutdown-reserve-seconds', '20']
         and command.count('--out') == 2 and command[command.index('--out') + 1] == supervision, 'PLAN_ALLOCATION')
    need(type(manifest.get('schema_version')) is int and manifest['schema_version'] == 1
         and manifest.get('source_sha256') == PINS[SUP] and manifest.get('cwd') == str(ROOT), 'SUPERVISOR_IDENTITY')
    need(manifest.get('automatic_retry') is False and manifest.get('cumulative_across_commands') is False, 'SUPERVISOR_RETRY')
    need(type(manifest.get('seconds')) in (int, float) and manifest['seconds'] == outer
         and type(manifest.get('shutdown_reserve_seconds')) in (int, float) and manifest['shutdown_reserve_seconds'] == 20, 'SUPERVISOR_ALLOCATION')
    need(type(manifest.get('invocation_id')) is str and re.fullmatch('[0-9a-f]{32}', manifest['invocation_id'])
         and terminal.get('invocation_id') == manifest['invocation_id'], 'INVOCATION')
    need(terminal.get('status') == 'COMMAND_COMPLETED_VERIFICATION_PENDING' and terminal.get('stop_reason') == 'COMMAND_EXITED'
         and type(terminal.get('command_exit_code')) is int and terminal['command_exit_code'] == 0
         and terminal.get('error') is None and terminal.get('deadline_reached') is False, 'TERMINAL')
    need(type(terminal.get('elapsed_seconds')) in (int, float) and math.isfinite(terminal['elapsed_seconds'])
         and 0 <= terminal['elapsed_seconds'] <= outer, 'TERMINAL_ELAPSED')
    cleanup = terminal.get('cleanup')
    need(type(cleanup) is dict and cleanup.get('reaped') is True and cleanup.get('job_active_zero_observed') is True
         and type(cleanup.get('actual_exit_code')) is int and cleanup['actual_exit_code'] == 0
         and type(cleanup.get('cleanup_errors')) is list and cleanup['cleanup_errors'] == [], 'CLEANUP')
    return child


def synthetic_runtime(mode):
    packet, supervision = 'acceleration/results/synthetic_triangle_packet', 'acceleration/results/synthetic_triangle_supervision'
    worker = [PYTHON, '-B', PRODUCER, mode, '--seconds', '150' if mode == 'calibrate' else '550', '--out', packet,
              '--source-sha256', PINS[PRODUCER], '--spec-sha256', PINS[PRODUCER_SPEC]]
    if mode == 'survey':
        for label in ('calibration', 'full-gate', 'root-full-acceptance'):
            worker += ['--' + label, 'acceleration/results/synthetic_' + label + '.json', '--' + label + '-sha256', 'a' * 64]
    child = [UV, 'run', '--locked', '--offline', '--python', PYTHON, *worker]
    outer = 180 if mode == 'calibrate' else 600
    command = [PYTHON, SUP, '--seconds', str(outer), '--shutdown-reserve-seconds', '20', '--allocation-reason', 'synthetic',
        '--success-criterion', 'synthetic', '--verification-criterion', 'synthetic', '--out', supervision, '--', *child]
    report = dict(command=[PYTHON, *worker[2:]])
    manifest = dict(schema_version=1, command=child, source_sha256=PINS[SUP], cwd=str(ROOT), seconds=outer,
        shutdown_reserve_seconds=20, automatic_retry=False, cumulative_across_commands=False, invocation_id='a' * 32)
    terminal = dict(invocation_id='a' * 32, status='COMMAND_COMPLETED_VERIFICATION_PENDING', stop_reason='COMMAND_EXITED',
        command_exit_code=0, error=None, deadline_reached=False, elapsed_seconds=1.0,
        cleanup=dict(reaped=True, job_active_zero_observed=True, actual_exit_code=0, cleanup_errors=[]))
    return dict(plan=dict(command=command, child_argv=child, worker_argv=worker), manifest=manifest, terminal=terminal, report=report)


def own_controls(deadline, save):
    positives, negatives = [], []
    def positive(label, raw, result):
        save('positive_' + label + '.json', dict(payload=raw, observed=result, synthetic=True))
        positives.append(dict(case=label, expected_stage='PASS', actual_stage='PASS'))
    hand_cases = [
        ('pairwise_without_common_Q', [63, 455, 504], ['1/2'] * 3, 1, 1, '3/2'),
        ('exact_one', [63, 455, 504], ['1/3'] * 3, 1, 0, '1'),
        ('below_one', [63, 455, 504], ['1/4'] * 3, 1, 0, '3/4'),
        ('one_edge', [7, 15, 28], ['1/2'] * 3, 0, 0, None),
        ('small_zero', [1, 7, 63, 455, 504], ['99', '0', '1/2', '1/2', '1/2'], 1, 1, '3/2'),
        ('empty', [], [], 0, 0, None),
    ]
    packets = {}
    for label, masks, weights, triangles, bad, maximum in hand_cases:
        packet = in_memory_fixture(masks, weights, 9, deadline)
        counts = memory_check(packet, 9, deadline)
        need(same([counts['triangle_cliques'], counts['violated_triangle_cliques'], counts['maximum_triangle_sum']],
                  [triangles, bad, maximum]), 'HAND_EXPECTATION')
        positive(label, dict(masks=masks, weights=weights, packet=packet), counts)
        packets[label] = packet
    cuts = common_cuts([0, 7], [Fraction(0), Fraction(0)], [Fraction(1)] * 680, 17, deadline)
    compare_cuts(cuts, cuts)
    need(len(cuts) == 680 and cuts[0]['Q'] == [0, 1, 2] and cuts[-1]['Q'] == [14, 15, 16], 'HAND_680_ORDER')
    positive('all680_zero', dict(masks=[0, 7], weights=['0', '0'], slacks=['1'] * 680), cuts)
    header = dict(status=PRIMAL_GATE, producer='/root/checkpoint_audit', verifier='/root/structural', method='independent_artifact_check',
        target_resolution='NONE', implementation_version=2, outcome=dict(certificate_kind='primal', rows=834, variables=1152,
        original_variables=472, original_equations=154, triple_caps=680), software=PRIMAL_SOFTWARE.copy(), inputs_sha256=PRIMAL_SOFTWARE.copy())
    primal_header(header); primal_source(header)
    positive('primal_header', header, dict(accepted=True))
    for mode in ('calibrate', 'survey'):
        frames = synthetic_runtime(mode)
        runtime(frames, mode, 'acceleration/results/synthetic_triangle_packet', 'acceleration/results/synthetic_triangle_supervision')
        positive('runtime_' + mode, frames, dict(accepted=True))
    software = dict(PINS)
    software[SELF.relative_to(ROOT).as_posix()] = 'a' * 64
    software[SPEC.relative_to(ROOT).as_posix()] = 'b' * 64
    own_gate = dict(status=CAL, producer='/root/checkpoint_audit', verifier='/root/native_driver', method='independent_artifact_check',
        target_resolution='NONE', implementation_version=2, source_sha256='a' * 64, spec_sha256='b' * 64, inputs_sha256=software.copy())
    checker_applicability(own_gate, software, CAL)
    positive('own_calibration_source_snapshot', own_gate, dict(accepted=True, software_snapshot_members=8,
             own_summary_not_required_in_its_own_input_map=True))
    alias_control = copy.deepcopy(packets['pairwise_without_common_Q'])
    original_triangles = copy.deepcopy(alias_control['triangles'])
    alias_control['violations'][0]['weights'] = ['1/3'] * 3
    need(same(alias_control['triangles'], original_triangles), 'INDEPENDENT_FIXTURE_OBJECTS')
    positive('independent_violation_fixture_objects',
             dict(original_triangle_table=original_triangles, after_mutation_triangle_table=alias_control['triangles'],
                  mutated_violation_table=alias_control['violations']), dict(triangle_table_unchanged=True))
    def reject(label, payload, stage, action):
        try:
            action(payload)
        except ValueError as error:
            observed = str(error)
            need(observed == stage, 'CONTROL_STAGE:' + label + ':' + observed)
        else:
            raise ValueError('CONTROL_FALSE_ACCEPT:' + label)
        save('negative_' + label + '.json', dict(payload=payload, expected_stage=stage, actual_stage=observed, synthetic=True))
        negatives.append(dict(case=label, expected_stage=stage, actual_stage=observed))
    for label, masks, stage in [('bool_mask', [True], 'MASK_INTEGER'), ('float_mask', [7.0], 'MASK_INTEGER'),
        ('duplicate_mask', [7, 7], 'MASK_ORDER'), ('reverse_mask', [15, 7], 'MASK_ORDER'), ('outside_mask', [512], 'MASK_INTEGER')]:
        reject(label, masks, stage, lambda v: population(v, ['1'] * len(v), 9))
    for label, weights, stage in [('bool_weight', [True], 'WEIGHT_STRING'), ('float_weight', [0.5], 'WEIGHT_STRING'),
        ('unreduced', ['2/4'], 'WEIGHT_CANONICAL'), ('negative', ['-1'], 'WEIGHT_NONNEGATIVE'),
        ('zero_denominator', ['1/0'], 'WEIGHT_CANONICAL'), ('wrong_length', [], 'WEIGHT_SHAPE')]:
        reject(label, weights, stage, lambda v: population([7], v, 9))
    for label, m in [('bool_domain', True), ('float_domain', 9.0), ('large_domain', 18)]:
        reject(label, m, 'DOMAIN_INTEGER', lambda v: population([], [], v))
    base = packets['pairwise_without_common_Q']
    for label, key, index, field, value, stage in [
        ('pair_bool_intersection', 'pairs', 0, 'intersection_cardinality', True, 'PAIR_VALUE'),
        ('pair_float_position', 'pairs', 0, 'positions', [0.0, 1], 'PAIR_VALUE'),
        ('pair_wrong_columns', 'pairs', 2, 'columns', [0, 2], 'PAIR_VALUE'),
        ('pair_wrong_edge', 'pairs', 0, 'incompatible', False, 'PAIR_VALUE'),
        ('pair_wrong_sum', 'pairs', 2, 'exact_sum', '1/2', 'PAIR_VALUE'),
        ('pair_threshold_equal', 'pairs', 0, 'pair_inequality_violated', True, 'PAIR_VALUE'),
        ('triangle_late_id', 'triangles', 0, 'positions', [0, 1, 3], 'TRIANGLE_VALUE'),
        ('triangle_wrong_mask', 'triangles', 0, 'masks', [63, 455, 503], 'TRIANGLE_VALUE'),
        ('triangle_wrong_sum', 'triangles', 0, 'exact_sum', '1', 'TRIANGLE_VALUE'),
        ('triangle_threshold', 'triangles', 0, 'threshold', '3/2', 'TRIANGLE_VALUE'),
        ('triangle_flag', 'triangles', 0, 'violated', False, 'TRIANGLE_VALUE'),
        ('violation_wrong_weights', 'violations', 0, 'weights', ['1/3'] * 3, 'VIOLATION_VALUE')]:
        bad = copy.deepcopy(base); bad[key][index][field] = value
        reject(label, bad, stage, lambda v: memory_check(v, 9, deadline))
    for label, key, action, stage in [('pair_missing_last', 'pairs', 'pop', 'PAIR_ROW'),
        ('triangle_missing', 'triangles', 'pop', 'TRIANGLE_ROW'), ('violation_missing', 'violations', 'pop', 'VIOLATION_ROW'),
        ('pair_duplicate', 'pairs', 'append', 'PAIR_EXTRA'), ('triangle_duplicate', 'triangles', 'append', 'TRIANGLE_EXTRA'),
        ('violation_duplicate', 'violations', 'append', 'VIOLATION_EXTRA')]:
        bad = copy.deepcopy(base)
        if action == 'pop': bad[key].pop()
        else: bad[key].append(copy.deepcopy(bad[key][-1]))
        reject(label, bad, stage, lambda v: memory_check(v, 9, deadline))
    equal = copy.deepcopy(packets['exact_one']); equal['violations'] = copy.deepcopy(equal['triangles'])
    reject('equal_one_extra_violation', equal, 'VIOLATION_EXTRA', lambda v: memory_check(v, 9, deadline))
    raw_population = dict(source_first_columns=3, positive_exact_threshold='0', minimum_type_size=3, records=base['population'])
    for label, field, value, stage in [('population_bool_count', 'source_first_columns', True, 'POPULATION_CRITERION'),
        ('population_missing', 'records', base['population'][:-1], 'POSITIVE_POPULATION'),
        ('population_reverse', 'records', list(reversed(base['population'])), 'POSITIVE_POPULATION')]:
        bad = copy.deepcopy(raw_population); bad[field] = value
        reject(label, bad, stage, lambda v: compare_population(v, [63, 455, 504], ['1/2'] * 3, 9))
    for label, index, field, value, stage in [('cut_last_Q', 679, 'Q', [13, 15, 16], 'CUT_IDENTITY'),
        ('cut_bool_row', 0, 'row', False, 'CUT_IDENTITY'), ('cut_float_sum', 0, 'sum', 0.0, 'CUT_VALUE'),
        ('cut_wrong_slack', 679, 'slack', '0', 'CUT_VALUE'), ('cut_integer_holds', 0, 'holds', 1, 'CUT_VALUE')]:
        bad = copy.deepcopy(cuts); bad[index][field] = value
        reject(label, bad, stage, lambda v: compare_cuts(v, cuts))
    reject('cut_missing_last', cuts[:-1], 'CUT_POPULATION', lambda v: compare_cuts(v, cuts))
    for label, field, value, stage in [('gate_legacy_method', 'method', 'independent_derivation', 'EXACT_PRIMAL_GATE_HEADER'),
        ('gate_bool_version', 'implementation_version', True, 'EXACT_PRIMAL_GATE_HEADER'),
        ('gate_wrong_verifier', 'verifier', '/root/native_driver', 'EXACT_PRIMAL_GATE_HEADER')]:
        bad = copy.deepcopy(header); bad[field] = value
        reject(label, bad, stage, primal_header)
    for label, field, value in [('gate_farkas', 'certificate_kind', 'farkas'), ('gate_bool_rows', 'rows', True),
                                ('gate_float_variables', 'variables', 1152.0), ('gate_old_equations', 'original_equations', 153)]:
        bad = copy.deepcopy(header); bad['outcome'][field] = value
        reject(label, bad, 'EXACT_PRIMAL_GATE_SCOPE', primal_header)
    for label, root, field, value, stage in [
        ('runtime_source', 'manifest', 'source_sha256', 'b' * 64, 'SUPERVISOR_IDENTITY'),
        ('runtime_bool_schema', 'manifest', 'schema_version', True, 'SUPERVISOR_IDENTITY'),
        ('runtime_cwd', 'manifest', 'cwd', 'elsewhere', 'SUPERVISOR_IDENTITY'),
        ('runtime_retry', 'manifest', 'automatic_retry', 0, 'SUPERVISOR_RETRY'),
        ('runtime_bool_seconds', 'manifest', 'seconds', True, 'SUPERVISOR_ALLOCATION'),
        ('runtime_changed_invocation', 'terminal', 'invocation_id', 'b' * 32, 'INVOCATION'),
        ('runtime_bool_exit', 'terminal', 'command_exit_code', False, 'TERMINAL'),
        ('runtime_deadline', 'terminal', 'deadline_reached', True, 'TERMINAL'),
        ('runtime_float_inf', 'terminal', 'elapsed_seconds', 'inf', 'TERMINAL_ELAPSED')]:
        bad = synthetic_runtime('calibrate'); bad[root][field] = value
        reject(label, bad, stage, lambda v: runtime(v, 'calibrate', 'acceleration/results/synthetic_triangle_packet', 'acceleration/results/synthetic_triangle_supervision'))
    for label, field, value in [('cleanup_bool_exit', 'actual_exit_code', False), ('cleanup_reaped_int', 'reaped', 1),
                              ('cleanup_active_int', 'job_active_zero_observed', 1), ('cleanup_errors', 'cleanup_errors', ['error'])]:
        bad = synthetic_runtime('calibrate'); bad['terminal']['cleanup'][field] = value
        reject(label, bad, 'CLEANUP', lambda v: runtime(v, 'calibrate', 'acceleration/results/synthetic_triangle_packet', 'acceleration/results/synthetic_triangle_supervision'))
    for label, bad, stage in [('duplicate_json', b'{"x":0,"x":1}', 'JSON_DUPLICATE'), ('nonfinite_json', b'{"x":NaN}', 'JSON_NONFINITE')]:
        reject(label, dict(raw=bad.decode('utf8')), stage, lambda v: strict_json(v['raw'].encode('utf8')))
    for label, field, value in [('own_gate_wrong_source', 'source_sha256', 'c' * 64), ('own_gate_bool_version', 'implementation_version', True)]:
        bad = copy.deepcopy(own_gate); bad[field] = value
        reject(label, bad, 'CHECKER_GATE_SOURCE', lambda v: checker_applicability(v, software, CAL))
    bad = copy.deepcopy(own_gate); bad['inputs_sha256'].pop(SUP)
    reject('own_gate_missing_software_pin', bad, 'CHECKER_GATE_SOURCE', lambda v: checker_applicability(v, software, CAL))
    for label, mapping, key in [('primal_old_source', 'software', next(iter(PRIMAL_SOFTWARE))),
                              ('primal_missing_spec_pin', 'inputs_sha256', list(PRIMAL_SOFTWARE)[1])]:
        bad = copy.deepcopy(header); bad[mapping][key] = 'c' * 64
        reject(label, bad, 'EXACT_PRIMAL_GATE_SOURCE', primal_source)
    need(len(positives) == 12 and len(negatives) == 69, 'OWN_CONTROL_POPULATION')
    save('controls.json', dict(positive=positives, precise_negative=negatives, actual_producer_packet_read=False,
         actual_scientific_primal_read=False, LP_calls=0, RREF_calls=0))
    return dict(positive_cases=12, precise_negative_cases=69, synthetic_all680_cut_rows=680,
                actual_producer_packet_read=False, actual_scientific_primal_read=False)


def replay_producer_controls(packet, read, deadline, save):
    rows = []
    for label, masks, weights, triangles, bad, maximum in [
        ('pairwise_without_common_Q', [63, 455, 504], ['1/2'] * 3, 1, 1, '3/2'),
        ('exact_one_not_violated', [63, 455, 504], ['1/3'] * 3, 1, 0, '1'),
        ('below_one', [63, 455, 504], ['1/4'] * 3, 1, 0, '3/4'),
        ('one_edge_not_triangle', [7, 15, 28], ['1/2'] * 3, 0, 0, None),
        ('small_and_zero_excluded', [1, 7, 63, 455, 504], ['99', '0', '1/2', '1/2', '1/2'], 1, 1, '3/2')]:
        raw = read(packet / ('control_' + label + '.json'))
        need(type(raw) is dict and set(raw) == {'masks', 'weights', 'result', 'synthetic'} and raw['synthetic'] is True
             and same(raw['masks'], masks) and same(raw['weights'], weights), 'AUTHOR_POSITIVE_PAYLOAD')
        wanted = population(masks, weights, 9)
        need(type(raw['result']) is dict and set(raw['result']) == {'population', 'pairs', 'triangles', 'violations', 'counts'}
             and same(raw['result']['population'], wanted), 'AUTHOR_POSITIVE_POPULATION')
        result = memory_check(raw['result'], 9, deadline)
        need(same(raw['result']['counts'], result) and same([result['triangle_cliques'], result['violated_triangle_cliques'], result['maximum_triangle_sum']],
             [triangles, bad, maximum]), 'AUTHOR_POSITIVE_COUNTS')
        rows.append(dict(case=label, expected_stage='PASS', actual_stage='PASS'))
    cuts = read(packet / 'control_pairwise_without_common_Q_cuts.json')
    types = sets_from_masks([63, 455, 504], 9)
    totals = []
    for a in range(7):
        for b in range(a + 1, 8):
            for c in range(b + 1, 9):
                tick(deadline)
                totals.append(str(sum((Fraction(1, 2) for t in types if {a, b, c} <= t), Fraction(0))))
    need(same(cuts, dict(all84_Q_sums=totals, maximum='1', common_intersection_size=0)), 'AUTHOR_84_COMMON_Q')
    primal_header(read(packet / 'control_genuine_primal_header.json'))
    rows.append(dict(case='genuine_primal_header', expected_stage='PASS', actual_stage='PASS'))
    cases = [('bool_mask', [True], 'MASK_INTEGER', 'mask'), ('float_mask', [7.0], 'MASK_INTEGER', 'mask'),
        ('duplicate_mask', [7, 7], 'MASK_ORDER', 'mask'), ('reverse_masks', [15, 7], 'MASK_ORDER', 'mask'),
        ('out_of_domain', [512], 'MASK_INTEGER', 'mask'), ('float_weight', [1.0], 'WEIGHT_STRING', 'weight'),
        ('bool_weight', [True], 'WEIGHT_STRING', 'weight'), ('unreduced_weight', ['2/4'], 'WEIGHT_CANONICAL', 'weight'),
        ('negative_weight', ['-1'], 'WEIGHT_NONNEGATIVE', 'weight'), ('wrong_weight_count', [], 'WEIGHT_SHAPE', 'weight')]
    for label, payload, stage, kind in cases:
        raw = read(packet / ('control_' + label + '.json'))
        need(same(raw, dict(payload=payload, expected_stage=stage, actual_stage=stage, synthetic=True)), 'AUTHOR_NEGATIVE_PAYLOAD')
        try:
            if kind == 'mask': population(payload, ['1'] * len(payload), 9)
            else: population([7], payload, 9)
        except ValueError as error:
            need(str(error) == stage, 'AUTHOR_NEGATIVE_STAGE')
        else:
            raise ValueError('AUTHOR_NEGATIVE_ACCEPTED')
        rows.append(dict(case=label, expected_stage=stage, actual_stage=stage))
    for label, stage in [('legacy_method', 'EXACT_PRIMAL_GATE_HEADER'), ('dual_not_primal', 'EXACT_PRIMAL_GATE_SCOPE'),
                         ('bool_dimension', 'EXACT_PRIMAL_GATE_SCOPE')]:
        raw = read(packet / ('control_' + label + '.json'))
        need(type(raw) is dict and set(raw) == {'payload', 'expected_stage', 'actual_stage', 'synthetic'}
             and raw['synthetic'] is True and raw['expected_stage'] == stage and raw['actual_stage'] == stage, 'AUTHOR_GATE_NEGATIVE')
        try: primal_header(raw['payload'])
        except ValueError as error: need(str(error) == stage, 'AUTHOR_NEGATIVE_STAGE')
        else: raise ValueError('AUTHOR_NEGATIVE_ACCEPTED')
        rows.append(dict(case=label, expected_stage=stage, actual_stage=stage))
    control = read(packet / 'controls.json')
    need(same(control, dict(positive=6, precise_negative=13, total=19, records=rows, actual_primal_read=False)), 'AUTHOR_CONTROL_TABLE')
    save('independent_author_control_stages.json', rows)
    return dict(positive_cases=6, precise_negative_cases=13, complete_synthetic_Q_rows=84, complete_payload_files=21,
                actual_scientific_primal_read=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['calibrate', 'producer-controls', 'full'])
    parser.add_argument('--seconds', type=float, required=True)
    parser.add_argument('--out', type=Path, required=True)
    for name in ('calibration', 'producer-root', 'producer-plan', 'supervision-out', 'producer-controls'):
        parser.add_argument('--' + name, type=Path)
        if name not in ('producer-root', 'supervision-out'): parser.add_argument('--' + name + '-sha256')
    for name in ('producer-summary-sha256', 'supervisor-manifest-sha256', 'supervisor-summary-sha256'):
        parser.add_argument('--' + name)
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='Independent saved-vector complete pairs/direct three-subsets/680 exact cuts; all authentication and outputs inside invocation with20save')
    out = args.out.resolve()
    need(out.is_relative_to(ROOT / 'acceleration/results') and not out.exists(), 'FRESH_OUTPUT')
    out.mkdir(parents=True)
    pins = {}
    def digest(path):
        tick(deadline); h = hashlib.sha256()
        with path.open('rb') as stream:
            while block := stream.read(1024**2): h.update(block); tick(deadline)
        tick(deadline); return h.hexdigest()
    def pin(path, expected=None):
        path = Path(path).resolve()
        need(path.is_relative_to(ROOT) and path.is_file() and not path.is_symlink(), 'INPUT_PATH')
        name = path.relative_to(ROOT).as_posix()
        need(name != 'CLAIMS.yaml' and not name.startswith('.git/'), 'MUTABLE_INPUT')
        observed = digest(path)
        need(expected is None or type(expected) is str and re.fullmatch('[0-9a-f]{64}', expected) and expected == observed, 'INPUT_IDENTITY')
        need(name not in pins or pins[name] == observed, 'INPUT_CHANGED')
        pins[name] = observed
        return path
    def read(path, expected=None):
        value = strict_json(pin(path, expected).read_bytes()); tick(deadline); return value
    def mapped(raw):
        for name, sha in identity_map(raw, 'IDENTITY_MAP').items(): pin(ROOT / name, sha)
    def save(name, value):
        tick(deadline); raw = (json.dumps(value, indent=2, allow_nan=False) + '\n').encode('utf8'); tick(deadline)
        with (out / name).open('xb') as stream:
            for offset in range(0, len(raw), 1024**2): stream.write(raw[offset:offset + 1024**2]); tick(deadline)
        tick(deadline)
    def checker_gate(path, sha, status):
        raw = read(path, sha)
        checker_applicability(raw, software, status)
        mapped(raw['inputs_sha256']); mapped(raw['outputs_sha256'])
        return raw
    try:
        for name, sha in PINS.items(): pin(ROOT / name, sha)
        pin(SELF); pin(SPEC)
        software = pins.copy()  # Snapshot BEFORE adding an own-calibration summary; it cannot contain itself.
        if args.mode == 'calibrate':
            need(all(v is None for k, v in vars(args).items() if k not in ('mode', 'seconds', 'out')), 'CAL_NO_ACTUAL_ARGUMENTS')
            scope = own_controls(deadline, save); status = CAL
        else:
            need(all(getattr(args, k) is not None for k in ('calibration', 'calibration_sha256', 'producer_root', 'producer_plan',
                 'producer_plan_sha256', 'supervision_out', 'producer_summary_sha256', 'supervisor_manifest_sha256', 'supervisor_summary_sha256')), 'ACTUAL_ARGUMENTS')
            own = checker_gate(args.calibration, args.calibration_sha256, CAL)
            need(same(own.get('checked_scope'), dict(positive_cases=12, precise_negative_cases=69, synthetic_all680_cut_rows=680,
                 actual_producer_packet_read=False, actual_scientific_primal_read=False)), 'OWN_CALIBRATION_SCOPE')
            mode = 'calibrate' if args.mode == 'producer-controls' else 'survey'
            packet, supervision = args.producer_root.resolve(), args.supervision_out.resolve()
            need(packet.is_relative_to(ROOT / 'acceleration/results') and packet.is_dir() and packet != out
                 and supervision.is_relative_to(ROOT / 'acceleration/results') and supervision.is_dir(), 'PRODUCER_NAMESPACE')
            report = read(packet / 'summary.json', args.producer_summary_sha256); producer_header(report, mode)
            plan = read(args.producer_plan, args.producer_plan_sha256)
            frames = dict(plan=plan, report=report,
                manifest=read(supervision / 'manifest.json', args.supervisor_manifest_sha256),
                terminal=read(supervision / 'summary.json', args.supervisor_summary_sha256))
            child = runtime(frames, mode, packet.relative_to(ROOT).as_posix(), supervision.relative_to(ROOT).as_posix())
            mapped(report['inputs_sha256'])
            need(all(report['inputs_sha256'].get(k) == v for k, v in PINS.items() if k != SUP), 'PRODUCER_SOFTWARE_BINDING')
            control_labels = ['pairwise_without_common_Q', 'pairwise_without_common_Q_cuts', 'exact_one_not_violated',
                'below_one', 'one_edge_not_triangle', 'small_and_zero_excluded', 'genuine_primal_header', 'bool_mask',
                'float_mask', 'duplicate_mask', 'reverse_masks', 'out_of_domain', 'float_weight', 'bool_weight',
                'unreduced_weight', 'negative_weight', 'wrong_weight_count', 'legacy_method', 'dual_not_primal', 'bool_dimension']
            names = {'control_' + label + '.json' for label in control_labels} | {'controls.json'}
            if mode == 'survey': names |= {'positive_types.json', 'all680_common_Q_caps.json', 'all_pairs.jsonl', 'all_triangle_cliques.jsonl', 'all_violations.jsonl'}
            need({p.relative_to(packet).as_posix() for p in packet.rglob('*') if p.is_file()} == names | {'summary.json'}
                 and set(report['outputs_sha256']) == names, 'OUTPUT_POPULATION')
            for name, sha in report['outputs_sha256'].items(): pin(packet / name, sha)
            replay = replay_producer_controls(packet, read, deadline, save)
            need(same(report.get('controls'), read(packet / 'controls.json')['records']), 'REPORT_CONTROLS')
            if mode == 'calibrate':
                need(args.producer_controls is None and args.producer_controls_sha256 is None
                     and not any(k in report['inputs_sha256'] for k in FIXED), 'CONTROLS_NO_SCIENCE')
                scope, status = replay, CONTROLS
            else:
                need(args.producer_controls is not None and args.producer_controls_sha256 is not None, 'CONTROLS_GATE_REQUIRED')
                controls = checker_gate(args.producer_controls, args.producer_controls_sha256, CONTROLS)
                need(same(controls.get('checked_scope'), replay), 'CONTROLS_GATE_SCOPE')
                options = dict(zip(child[18::2], child[19::2]))
                gate = read(ROOT / options['--full-gate'], options['--full-gate-sha256']); primal_header(gate); primal_source(gate)
                mapped(gate['inputs_sha256']); mapped(gate['outputs_sha256'])
                need(all(report['inputs_sha256'].get(k) == v for mapping in (gate['inputs_sha256'], gate['outputs_sha256'])
                         for k, v in mapping.items()), 'SURVEY_PRIMAL_CLOSURE')
                need(all(gate['inputs_sha256'].get(k) == v and report['inputs_sha256'].get(k) == v for k, v in FIXED.items()), 'PRIMAL_DIRECT_PINS')
                review = read(ROOT / options['--root-full-acceptance'], options['--root-full-acceptance-sha256'])
                need(review.get('full_report_sha256') == options['--full-gate-sha256'] and review.get('target_resolution') == 'NONE', 'ROOT_ACCEPTANCE_BINDING')
                producer_cal = read(ROOT / options['--calibration'], options['--calibration-sha256'])
                producer_header(producer_cal, 'calibrate')
                need(same(producer_cal.get('controls'), report['controls']), 'PRODUCER_CAL_APPLICABILITY')
                need(all(producer_cal['inputs_sha256'].get(k) == v for k, v in PINS.items() if k != SUP), 'PRODUCER_CAL_SOFTWARE')
                mapped(producer_cal['inputs_sha256'])
                for name, sha in identity_map(producer_cal['outputs_sha256'], 'PRODUCER_CAL_OUTPUTS').items():
                    pin((ROOT / options['--calibration']).parent / name, sha)
                for label in ('calibration', 'full-gate', 'root-full-acceptance'):
                    need(report['inputs_sha256'].get(options['--' + label]) == options['--' + label + '-sha256'], 'SURVEY_ANTECEDENT_BINDING')
                model, primal, typed = (read(ROOT / name, FIXED[name]) for name in (MODEL, PRIMAL, TYPES))
                need(type(model) is dict and model.get('schema') == 'TRIPLE_CAPPED_EXTERNAL_MOMENT_SYSTEM_V1'
                     and same([model.get(k) for k in ('original_variables', 'original_equations', 'slack_variables', 'rows', 'variables', 'support_vertices')],
                              [472, 154, 680, 834, 1152, list(range(17))]), 'MODEL_SCOPE')
                need(type(typed) is list and len(typed) == 472 and all(type(t) is dict and set(t) == {'mask', 'coefficient'} for t in typed), 'TYPE_POPULATION')
                masks = [t['mask'] for t in typed]; types = sets_from_masks(masks, 17)
                need(same(model.get('ordered_masks'), masks), 'MODEL_MASK_ORDER')
                for row, selected in zip(typed, types):
                    tick(deadline)
                    coefficient = [1] + [int(u in selected) for u in range(17)]
                    coefficient += [int(u in selected and v in selected) for u in range(16) for v in range(u + 1, 17)]
                    need(same(row['coefficient'], coefficient), 'TYPE_COEFFICIENT')
                need(type(primal) is dict and primal.get('schema') == 'TRIPLE_CAPPED_EXTERNAL_MOMENT_EXACT_PRIMAL_V1', 'PRIMAL_SCHEMA')
                values = fractions(primal.get('values'), 1152)
                selected = compare_population(read(packet / 'positive_types.json'), masks, list(map(str, values[:472])), 17)
                cuts = common_cuts(masks, values[:472], values[472:], 17, deadline)
                compare_cuts(read(packet / 'all680_common_Q_caps.json'), cuts)
                with (packet / 'all_pairs.jsonl').open('rb') as pairs, (packet / 'all_triangle_cliques.jsonl').open('rb') as triangles, (packet / 'all_violations.jsonl').open('rb') as violations:
                    counts = check_streams(selected, 17, Records(pairs, deadline), Records(triangles, deadline), Records(violations, deadline), deadline)
                outcome = dict(**counts, original_common_Q_cuts_checked=680, triangle_threshold='strictly greater than1',
                    all_matches_retained=True, maximum_cliques_enumerated=False,
                    original_primal_gate_sha256=options['--full-gate-sha256'], meaning=MEANING)
                need(same(report.get('outcome'), outcome), 'SURVEY_OUTCOME')
                save('independent_complete_counts.json', outcome)
                save('independent_all680_common_Q_caps.json', cuts)
                scope = dict(source_types=472, full_canonical_rational_coordinates=1152, complete_common_Q_cuts=680,
                    complete_type_coefficients=472 * 154, producer_controls=replay, complete_survey=outcome,
                    all_three_subsets_visited=True, all_streams_end_exactly=True, only_saved_vector_diagnostic=True,
                    whole_system_infeasibility_claimed=False, graph_or_target_claimed=False)
                status = FULL
        for name, sha in list(pins.items()): pin(ROOT / name, sha)
        outputs = {p.relative_to(ROOT).as_posix(): digest(p) for p in sorted(out.iterdir()) if p.is_file()}
        save('summary.json', dict(status=status, timestamp=datetime.now(timezone.utc).isoformat(), producer='/root/checkpoint_audit',
            verifier='/root/native_driver', method='independent_artifact_check', target_resolution='NONE', implementation_version=2,
            command=[sys.executable, *sys.argv], source_sha256=software[SELF.relative_to(ROOT).as_posix()],
            spec_sha256=software[SPEC.relative_to(ROOT).as_posix()], inputs_sha256=pins, outputs_sha256=outputs,
            checked_scope=scope, producer_code_imports=0, LP_calls=0, RREF_calls=0,
            shared_origins=['Pair/triple necessity is the previously independently written d3e lemma; this checker does not reprove it',
                'Protocol/source contract was whole-read; arithmetic uses literal sets and direct triple loops, never producer functions'],
            no_automatic_retry=True, no_graph_feasibility_or_target_claim=True, deadline=deadline.status()))
        tick(deadline)
        return 0
    except BaseException as error:
        if (out / 'summary.json').exists(): (out / 'summary.json').rename(out / 'summary.not_approved.json')
        (out / 'failure.json').write_text(json.dumps(dict(error=repr(error), inputs_sha256=pins, deadline=deadline.status(),
            automatic_retry=False, partial_outputs_preserved=True, no_infeasibility_inference=True), indent=2, allow_nan=False) + '\n', encoding='utf8')
        raise


if __name__ == '__main__':
    raise SystemExit(main())
