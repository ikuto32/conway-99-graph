"""SOURCE_ONLY: exact two-vertex Schur tests, not a target or LP checker."""
import argparse
import copy
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import itertools
import json
from math import lcm
from pathlib import Path
import sys

from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = 'acceleration/diagnose_20261004_fixed17_dual_gram_pairs_v1.py'
SPEC = 'acceleration/diagnose_20261004_fixed17_dual_gram_pairs_v1_spec.md'
DATA_ROOT = 'acceleration/results/20261004_fixed17_dual_gram_singletons01/'
DATA = {
    DATA_ROOT + 'summary.json': 'e6d60171fb6d2d8b22e7d1eac02d68972de805ecb56329e77d75a199cb4f4be9',
    DATA_ROOT + 'parsed_input.json': 'fa363f43b1e3de238c330b0b9caaf4e2c61dd8e1f7dc7044d3817b02b3b246b5',
    DATA_ROOT + 'singletons.json': 'feed0822248d1e956246f27f31c16970757dd518fba9695d13e9d71f39c13026',
    DATA_ROOT + 'upper_inverse_certificate.json': '22a7bcd7f178382d7a8893a8acc5f960ba69ac5e2509c2b6175c7ae22cf3c4e5',
    DATA_ROOT + 'lower_inverse_certificate.json': 'f7c98ab5da93ded447730ccdd39aeb247fd51930c6e472d0cebc89231b29703b',
}
GATE_STATUS = 'INDEPENDENT_FIXED17_DUAL_GRAM_SINGLETON_V1_COMPLETE_PASS'
CAL_STATUS = 'FIXED17_DUAL_GRAM_PAIR_V1_AUTHOR_CONTROLS_PASS'
CONTROL_COUNTS = {'positive': 10, 'negative': 41, 'total': 51}
BASE_ROWS = [[0, 1, 2], [0, 3, 4], [0, 5, 6], [1, 7, 9], [1, 8, 10],
             [15, 11, 14], [16, 12, 13], [2, 15, 16], [3, 7, 11],
             [4, 8, 12], [5, 9, 13], [6, 10, 14]]
RECORD_KEYS = {'proposal_id', 'i', 'j', 'left_mask', 'right_mask', 'intersection',
    'upper_left_diagonal', 'upper_right_diagonal', 'upper_cross_0', 'upper_cross_1',
    'lower_left_diagonal', 'lower_right_diagonal', 'lower_cross_0', 'lower_cross_1',
    'upper_bits', 'lower_bits', 'cn_bits', 'combined_bits', 'classification'}
CLASSES = ('incompatible', 'forced_nonadjacent', 'forced_adjacent', 'either')


class Veto(ValueError):
    def __init__(self, stage):
        super().__init__(stage)
        self.stage = stage


def require(ok, stage):
    if not ok:
        raise Veto(stage)


def typed_same(a, b):
    if type(a) is not type(b):
        return False
    if type(a) is dict:
        return set(a) == set(b) and all(typed_same(a[k], b[k]) for k in b)
    if type(a) is list:
        return len(a) == len(b) and all(typed_same(x, y) for x, y in zip(a, b))
    return a == b


def rational(value):
    require(type(value) is str, 'RATIONAL_TYPE')
    try:
        result = F(value)
    except (ValueError, ZeroDivisionError):
        raise Veto('RATIONAL_CANONICAL') from None
    require(str(result) == value, 'RATIONAL_CANONICAL')
    return result


def parse(raw):
    def pairs(xs):
        result = {}
        for k, v in xs:
            require(k not in result, 'JSON_DUPLICATE')
            result[k] = v
        return result
    def constant(_):
        raise Veto('JSON_CONSTANT')
    try:
        return json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)
    except json.JSONDecodeError:
        raise Veto('JSON_SYNTAX') from None


class Budget:
    def __init__(self, seconds):
        self.deadline = CommandDeadline(seconds, allocation_reason=
            'Complete exact integer pair Schur diagnostic and bounded serialization')
    def tick(self):
        state = self.deadline.status()
        require(not state['stop_required'] and state['remaining_seconds'] > 20,
                'SAVE_RESERVE_STOP')


def save(path, value, budget):
    budget.tick()
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')
    budget.tick()


def read_hash(path, digest, budget):
    budget.tick()
    raw = Path(path).read_bytes()
    require(hashlib.sha256(raw).hexdigest() == digest, 'INPUT_HASH')
    budget.tick()
    return parse(raw.decode('utf8'))


def scaled_inverse(payload, name, n):
    require(type(payload) is dict and payload.get('schema') ==
            'EXACT_DUAL_GRAM_INVERSE_LDL_CERTIFICATE_V1', 'INVERSE_SCHEMA')
    require(payload.get('gram') == name, 'INVERSE_GRAM')
    require(type(payload.get('dimension')) is int and payload['dimension'] == n,
            'INVERSE_DIMENSION')
    rows = payload.get('inverse')
    require(type(rows) is list and len(rows) == n and all(
            type(row) is list and len(row) == n for row in rows), 'INVERSE_SHAPE')
    matrix = [[rational(x) for x in row] for row in rows]
    require(all(matrix[i][j] == matrix[j][i] for i in range(n) for j in range(n)),
            'INVERSE_SYMMETRY')
    denominator = lcm(*(x.denominator for row in matrix for x in row))
    integers = [[int(x * denominator) for x in row] for row in matrix]
    return denominator, integers, matrix


def masks_checked(masks, n, count):
    require(type(masks) is list and len(masks) == count, 'MASK_POPULATION')
    require(all(type(x) is int for x in masks), 'MASK_INTEGER')
    require(all(0 <= x < (1 << n) for x in masks), 'MASK_RANGE')
    require(len(set(masks)) == count, 'MASK_DISTINCT')
    require(masks == sorted(masks), 'MASK_ORDER')
    return masks


def dot(x, y):
    return sum(a * b for a, b in zip(x, y))


def multiply(a, x):
    return [dot(row, x) for row in a]


def context(masks, upper, lower):
    d, N, _ = upper
    e, P, _ = lower
    n = len(N)
    vectors = [[(mask >> k) & 1 for k in range(n)] for mask in masks]
    r = [[1 - 9 * x for x in bits] for bits in vectors]
    Nr, Pt = [multiply(N, x) for x in r], [multiply(P, x) for x in vectors]
    return {'masks': masks, 'd': d, 'e': e, 'N': N, 'P': P, 't': vectors,
            'r': r, 'Nr': Nr, 'Pt': Pt,
            'du': [252 * d - dot(x, y) for x, y in zip(r, Nr)],
            'dl': [4 * e - dot(x, y) for x, y in zip(vectors, Pt)]}


def admissible(left, right, cross0, cross1):
    return [a for a, cross in enumerate((cross0, cross1))
            if left >= 0 and right >= 0 and cross * cross <= left * right]


def record(pid, i, j, c):
    d, e = c['d'], c['e']
    upper_cross = dot(c['r'][i], c['Nr'][j])
    lower_cross = dot(c['t'][i], c['Pt'][j])
    uc = [9 * d - upper_cross, 9 * d - 81 * d - upper_cross]
    lc = [-lower_cross, e - lower_cross]
    intersection = (c['masks'][i] & c['masks'][j]).bit_count()
    ub = admissible(c['du'][i], c['du'][j], *uc)
    lb = admissible(c['dl'][i], c['dl'][j], *lc)
    cb = [a for a in (0, 1) if intersection <= (1 if a else 2)]
    both = sorted(set(ub) & set(lb) & set(cb))
    classification = CLASSES[{(): 0, (0,): 1, (1,): 2, (0, 1): 3}[tuple(both)]]
    return dict(proposal_id=pid, i=i, j=j, left_mask=c['masks'][i],
        right_mask=c['masks'][j], intersection=intersection,
        upper_left_diagonal=c['du'][i], upper_right_diagonal=c['du'][j],
        upper_cross_0=uc[0], upper_cross_1=uc[1],
        lower_left_diagonal=c['dl'][i], lower_right_diagonal=c['dl'][j],
        lower_cross_0=lc[0], lower_cross_1=lc[1], upper_bits=ub, lower_bits=lb,
        cn_bits=cb, combined_bits=both, classification=classification)


def checked_record(value, expected):
    require(type(value) is dict and set(value) == RECORD_KEYS, 'RECORD_KEYS')
    for k in RECORD_KEYS - {'upper_bits', 'lower_bits', 'cn_bits', 'combined_bits',
                            'classification'}:
        require(type(value[k]) is int, 'RECORD_INTEGER')
    for k in ('upper_bits', 'lower_bits', 'cn_bits', 'combined_bits'):
        require(type(value[k]) is list and all(type(x) is int and x in (0, 1)
                for x in value[k]), 'RECORD_BITS')
    require(type(value['classification']) is str, 'RECORD_CLASS_TYPE')
    require(typed_same(value, expected), 'RECORD_IDENTITY')


def gate(value, expected):
    require(type(value) is dict and value.get('status') == GATE_STATUS
            and value.get('producer') == '/root/structural'
            and value.get('verifier') == '/root/checkpoint_audit'
            and value.get('method') == 'independent_artifact_check'
            and value.get('target_resolution') == 'NONE'
            and type(value.get('implementation_version')) is int
            and value['implementation_version'] == 1, 'SINGLETON_GATE_HEADER')
    require(type(value.get('inputs_sha256')) is dict and
            all(value['inputs_sha256'].get(p) == h for p, h in expected.items()),
            'SINGLETON_GATE_DIRECT_PINS')
    counts = {'complete_type_records': 472, 'upper_pass': 472, 'lower_pass': 472,
              'combined_pass': 472, 'pairs_enumerated': 0,
              'future_unordered_pairs_including_equal_types': 111628}
    require(type(value.get('outcome')) is dict and all(
            type(value['outcome'].get(k)) is int and value['outcome'][k] == n
            for k, n in counts.items()), 'SINGLETON_GATE_COUNTS')


def calibration_header(cal, software):
    require(type(cal) is dict and cal.get('status') == CAL_STATUS
        and type(cal.get('implementation_version')) is int and cal['implementation_version'] == 1
        and typed_same(cal.get('source_software'), software)
        and cal.get('actual_target_input_read') is False
        and type(cal.get('outcome')) is dict
        and typed_same(cal['outcome'].get('controls'), CONTROL_COUNTS), 'CALIBRATION_HEADER')


def checked_part(part, index, start, stop, expected):
    require(type(part) is dict and set(part) ==
            {'schema', 'part_index', 'start', 'stop', 'count', 'records'}, 'PART_KEYS')
    require(all(type(part[k]) is int for k in ('part_index', 'start', 'stop', 'count')),
            'PART_INTEGER')
    require(part['schema'] == 'DUAL_GRAM_PAIR_PART_V1' and part['part_index'] == index
            and part['start'] == start and part['stop'] == stop
            and part['count'] == stop - start, 'PART_BOUNDARY')
    require(type(part['records']) is list and len(part['records']) == len(expected),
            'PART_RECORD_POPULATION')
    for actual, wanted in zip(part['records'], expected):
        checked_record(actual, wanted)


def checked_checkpoint(actual, wanted):
    require(type(actual) is dict and set(actual) == set(wanted), 'CHECKPOINT_KEYS')
    require(all(type(actual[k]) is int for k in
            ('next_proposal_id', 'total_pair_population', 'part_index')),
            'CHECKPOINT_INTEGER')
    require(type(actual['cumulative_counts']) is dict and all(
            type(x) is int for x in actual['cumulative_counts'].values()),
            'CHECKPOINT_COUNT_INTEGER')
    require(typed_same(actual, wanted), 'CHECKPOINT_IDENTITY')


def stream(out, c, identities, budget, part_size=5000):
    n = len(c['masks'])
    population = n * (n + 1) // 2
    counts = {k: 0 for k in CLASSES}
    counts.update(cn_incompatible=0, additional_gram_incompatible=0,
                  upper_incompatible=0, lower_incompatible=0,
                  equal_type_pairs=0, distinct_type_pairs=0)
    batch, start, part_index, pid = [], 0, 0, 0
    for i in range(n):
        for j in range(i, n):
            budget.tick()
            value = record(pid, i, j, c)
            counts[value['classification']] += 1
            counts['cn_incompatible'] += not value['cn_bits']
            counts['additional_gram_incompatible'] += bool(value['cn_bits']) and not value['combined_bits']
            counts['upper_incompatible'] += not value['upper_bits']
            counts['lower_incompatible'] += not value['lower_bits']
            counts['equal_type_pairs' if i == j else 'distinct_type_pairs'] += 1
            batch.append(value)
            pid += 1
            if len(batch) == part_size or pid == population:
                part = dict(schema='DUAL_GRAM_PAIR_PART_V1', part_index=part_index,
                            start=start, stop=pid, count=len(batch), records=batch)
                save(out / ('part_%03d.json' % part_index), part, budget)
                checkpoint = dict(schema='DUAL_GRAM_PAIR_CHECKPOINT_V1', next_proposal_id=pid,
                    total_pair_population=population, part_index=part_index,
                    cumulative_counts=dict(counts), input_identity_sha256=identities)
                save(out / ('checkpoint_%03d.json' % part_index), checkpoint, budget)
                print(json.dumps({'next_proposal_id': pid, 'population': population,
                                  'parts_saved': part_index + 1}), flush=True)
                batch, start, part_index = [], pid, part_index + 1
    require(pid == population, 'COMPLETE_PAIR_UNIVERSE')
    return dict(complete_pair_records=pid, part_count=part_index,
                checkpoint_count=part_index, counts=counts,
                ordering='i increasing0..count-1; j increasing i..count-1',
                equal_type_means_two_distinct_external_vertices=True)


def fixture_inverse(name, matrix):
    return dict(schema='EXACT_DUAL_GRAM_INVERSE_LDL_CERTIFICATE_V1', gram=name,
                dimension=len(matrix), inverse=[[str(x) for x in row] for row in matrix])


def fraction_reference(pid, i, j, c, ui, li):
    x, y = c['t'][i], c['t'][j]
    b, z = [F(1, 9) - t for t in x], [F(1, 9) - t for t in y]
    qu, qv, cross = dot(b, multiply(ui, b)), dot(z, multiply(ui, z)), dot(b, multiply(ui, z))
    lu, lv, lc = dot(x, multiply(li, x)), dot(y, multiply(li, y)), dot(x, multiply(li, y))
    D, E = 81 * c['d'], c['e']
    result = record(pid, i, j, c)
    for k, v in [('upper_left_diagonal', (F(28, 9) - qu) * D),
                 ('upper_right_diagonal', (F(28, 9) - qv) * D),
                 ('upper_cross_0', (F(1, 9) - cross) * D),
                 ('upper_cross_1', (F(1, 9) - 1 - cross) * D),
                 ('lower_left_diagonal', (4 - lu) * E),
                 ('lower_right_diagonal', (4 - lv) * E),
                 ('lower_cross_0', -lc * E), ('lower_cross_1', (1 - lc) * E)]:
        require(v.denominator == 1, 'REFERENCE_INTEGER_SCALE')
        result[k] = v.numerator
    result['upper_bits'] = [a for a in (0, 1) if qu <= F(28, 9) and qv <= F(28, 9)
        and (F(1, 9) - a - cross) ** 2 <= (F(28, 9) - qu) * (F(28, 9) - qv)]
    result['lower_bits'] = [a for a in (0, 1) if lu <= 4 and lv <= 4
        and (a - lc) ** 2 <= (4 - lu) * (4 - lv)]
    result['combined_bits'] = sorted(set(result['upper_bits']) & set(result['lower_bits']) & set(result['cn_bits']))
    result['classification'] = CLASSES[{(): 0, (0,): 1, (1,): 2, (0, 1): 3}[tuple(result['combined_bits'])]]
    return result


def calibrate(out, budget):
    cases = []
    def case(name, stage, payload, function):
        save(out / (name + '.json'), payload, budget)
        actual = 'PASS'
        try:
            function(copy.deepcopy(payload))
        except Veto as exc:
            actual = exc.stage
        cases.append(dict(name=name, expected_stage=stage, actual_stage=actual))
        require(actual == stage, 'AUTHOR_CONTROL_STAGE_MISMATCH')
    u2 = [[F(int(i == j), 3) - F(1, 87) for j in range(2)] for i in range(2)]
    l2 = [[F(int(i == j), 4) for j in range(2)] for i in range(2)]
    up, lp = fixture_inverse('upper', u2), fixture_inverse('lower', l2)
    U, L = scaled_inverse(up, 'upper', 2), scaled_inverse(lp, 'lower', 2)
    c = context([0, 1, 2, 3], U, L)
    case('positive_upper_scaled', 'PASS', up, lambda p: scaled_inverse(p, 'upper', 2))
    case('positive_lower_scaled', 'PASS', lp, lambda p: scaled_inverse(p, 'lower', 2))
    def grid_check(p):
        ui = [[rational(x) for x in row] for row in p['upper']['inverse']]
        li = [[rational(x) for x in row] for row in p['lower']['inverse']]
        cc = context(p['masks'], scaled_inverse(p['upper'], 'upper', len(ui)),
                     scaled_inverse(p['lower'], 'lower', len(li)))
        for pid, (i, j) in enumerate(itertools.combinations_with_replacement(range(len(p['masks'])), 2)):
            checked_record(record(pid, i, j, cc), fraction_reference(pid, i, j, cc, ui, li))
    case('positive_full_empty2_grid', 'PASS', dict(upper=up, lower=lp, masks=[0, 1, 2, 3]), grid_check)
    u3 = [[F(int(i == j), 4) + F(1, 6) for j in range(3)] for i in range(3)]
    l3 = [[F(int(i == j), 3) - F(1, 18) for j in range(3)] for i in range(3)]
    case('positive_full_triangle_grid', 'PASS', dict(upper=fixture_inverse('upper', u3),
        lower=fixture_inverse('lower', l3), masks=[0, 1, 2, 7]), grid_check)
    u17 = [[F(int(i == j), 3) - F(1, 132) for j in range(17)] for i in range(17)]
    l17 = [[F(int(i == j), 4) for j in range(17)] for i in range(17)]
    case('positive_full17_last_grid', 'PASS', dict(upper=fixture_inverse('upper', u17),
        lower=fixture_inverse('lower', l17), masks=[0, 1, 65536]), grid_check)
    case('positive_upper_boundary', 'PASS', [1, 1, 1, -1], lambda p: require(admissible(*p) == [0, 1], 'BOUNDARY'))
    case('positive_lower_boundary', 'PASS', [0, 0, 0, 1], lambda p: require(admissible(*p) == [0], 'BOUNDARY'))
    fake_gate = dict(status=GATE_STATUS, producer='/root/structural', verifier='/root/checkpoint_audit',
                     method='independent_artifact_check', target_resolution='NONE',
                     implementation_version=1, inputs_sha256={'synthetic': 'pin'},
                     outcome={'complete_type_records': 472, 'upper_pass': 472,
                     'lower_pass': 472, 'combined_pass': 472, 'pairs_enumerated': 0,
                     'future_unordered_pairs_including_equal_types': 111628})
    case('positive_gate', 'PASS', fake_gate, lambda p: gate(p, {'synthetic': 'pin'}))
    fake_cal = dict(status=CAL_STATUS, implementation_version=1,
        source_software={'synthetic': 'pin'}, actual_target_input_read=False,
        outcome={'controls': CONTROL_COUNTS})
    case('positive_calibration_header', 'PASS', fake_cal,
         lambda p: calibration_header(p, {'synthetic': 'pin'}))
    tiny = out / 'synthetic_stream'
    tiny.mkdir()
    stream_result = stream(tiny, c, {'input': 'synthetic'}, budget, part_size=3)
    def stream_check(p):
        require(p['complete_pair_records'] == 10 and p['part_count'] == 4
                and p['checkpoint_count'] == 4, 'STREAM_REFERENCE')
        expected = [fraction_reference(pid, i, j, c, u2, l2) for pid, (i, j) in
                    enumerate(itertools.combinations_with_replacement(range(4), 2))]
        counts = {k: 0 for k in p['counts']}
        for index, start in enumerate(range(0, 10, 3)):
            budget.tick()
            stop = min(start + 3, 10)
            checked_part(parse((tiny / ('part_%03d.json' % index)).read_text(encoding='utf8')),
                         index, start, stop, expected[start:stop])
            for rec in expected[start:stop]:
                counts[rec['classification']] += 1
                counts['cn_incompatible'] += not rec['cn_bits']
                counts['additional_gram_incompatible'] += bool(rec['cn_bits']) and not rec['combined_bits']
                counts['upper_incompatible'] += not rec['upper_bits']
                counts['lower_incompatible'] += not rec['lower_bits']
                counts['equal_type_pairs' if rec['i'] == rec['j'] else 'distinct_type_pairs'] += 1
            wanted = dict(schema='DUAL_GRAM_PAIR_CHECKPOINT_V1', next_proposal_id=stop,
                total_pair_population=10, part_index=index, cumulative_counts=dict(counts),
                input_identity_sha256={'input': 'synthetic'})
            checked_checkpoint(parse((tiny / ('checkpoint_%03d.json' % index)).read_text(encoding='utf8')),
                               wanted)
        require(typed_same(p['counts'], counts), 'STREAM_REFERENCE')
    case('positive_stream', 'PASS', stream_result, stream_check)
    case('rational_bool', 'RATIONAL_TYPE', True, rational)
    case('rational_alias', 'RATIONAL_CANONICAL', '2/2', rational)
    for name, key, value, stage in [('inverse_schema', 'schema', 'wrong', 'INVERSE_SCHEMA'),
        ('inverse_gram', 'gram', 'lower', 'INVERSE_GRAM'),
        ('inverse_dimension_bool', 'dimension', True, 'INVERSE_DIMENSION'),
        ('inverse_dimension_wrong', 'dimension', 3, 'INVERSE_DIMENSION'),
        ('inverse_shape', 'inverse', [['1']], 'INVERSE_SHAPE')]:
        damaged = copy.deepcopy(up); damaged[key] = value
        case(name, stage, damaged, lambda p: scaled_inverse(p, 'upper', 2))
    for name, ix, value, stage in [('inverse_entry_bool', (0, 0), False, 'RATIONAL_TYPE'),
        ('inverse_asymmetric', (0, 1), '0', 'INVERSE_SYMMETRY'),
        ('inverse_last_bool', (1, 1), True, 'RATIONAL_TYPE')]:
        damaged = copy.deepcopy(up); damaged['inverse'][ix[0]][ix[1]] = value
        case(name, stage, damaged, lambda p: scaled_inverse(p, 'upper', 2))
    for name, values, stage in [('mask_bool', [False, 1, 2, 3], 'MASK_INTEGER'),
        ('mask_float', [0.0, 1, 2, 3], 'MASK_INTEGER'), ('mask_negative', [-1, 1, 2, 3], 'MASK_RANGE'),
        ('mask_high', [0, 1, 2, 4], 'MASK_RANGE'), ('mask_duplicate', [0, 1, 1, 3], 'MASK_DISTINCT'),
        ('mask_order', [0, 2, 1, 3], 'MASK_ORDER'), ('mask_short', [0, 1, 2], 'MASK_POPULATION')]:
        case(name, stage, values, lambda p: masks_checked(p, 2, 4))
    baseline = record(0, 0, 0, c)
    for name, key, value, stage in [('record_keys', 'extra', 1, 'RECORD_KEYS'),
        ('record_integer_bool', 'i', False, 'RECORD_INTEGER'),
        ('record_index_wrong', 'proposal_id', 1, 'RECORD_IDENTITY'),
        ('record_bits_bool', 'cn_bits', [False, 1], 'RECORD_BITS'),
        ('record_combined_wrong', 'combined_bits', [], 'RECORD_IDENTITY'),
        ('record_cross_wrong', 'upper_cross_0', baseline['upper_cross_0'] + 1, 'RECORD_IDENTITY'),
        ('record_class_wrong', 'classification', 'incompatible', 'RECORD_IDENTITY')]:
        damaged = copy.deepcopy(baseline); damaged[key] = value
        case(name, stage, damaged, lambda p: checked_record(p, baseline))
    for name, key, value in [('gate_bool_version', 'implementation_version', True),
        ('gate_method', 'method', 'independent_derivation'), ('gate_verifier', 'verifier', '/root/structural'),
        ('gate_status', 'status', 'CANDIDATE')]:
        damaged = copy.deepcopy(fake_gate); damaged[key] = value
        case(name, 'SINGLETON_GATE_HEADER', damaged, lambda p: gate(p, {'synthetic': 'pin'}))
    damaged = copy.deepcopy(fake_gate); damaged['inputs_sha256']['synthetic'] = 'wrong'
    case('gate_pin', 'SINGLETON_GATE_DIRECT_PINS', damaged, lambda p: gate(p, {'synthetic': 'pin'}))
    for name, key, value in [('gate_bool_outcome', 'pairs_enumerated', False),
                             ('gate_incomplete_outcome', 'complete_type_records', 471)]:
        damaged = copy.deepcopy(fake_gate); damaged['outcome'][key] = value
        case(name, 'SINGLETON_GATE_COUNTS', damaged, lambda p: gate(p, {'synthetic': 'pin'}))
    case('json_duplicate', 'JSON_DUPLICATE', '{"x":0,"x":1}', parse)
    case('json_constant', 'JSON_CONSTANT', '{"x":NaN}', parse)
    part = parse((tiny / 'part_000.json').read_text(encoding='utf8'))
    expected_part_records = copy.deepcopy(part['records'])
    for name, key, value, stage in [('part_bool_count', 'count', True, 'PART_INTEGER'),
        ('part_boundary', 'stop', 4, 'PART_BOUNDARY'),
        ('part_drop_record', 'records', expected_part_records[:-1], 'PART_RECORD_POPULATION')]:
        damaged = copy.deepcopy(part); damaged[key] = value
        case(name, stage, damaged, lambda p: checked_part(p, 0, 0, 3, expected_part_records))
    cp = parse((tiny / 'checkpoint_000.json').read_text(encoding='utf8'))
    for name, key, value, stage in [('checkpoint_bool_next', 'next_proposal_id', True, 'CHECKPOINT_INTEGER'),
        ('checkpoint_bool_count', 'cumulative_counts', {**cp['cumulative_counts'], 'either': True}, 'CHECKPOINT_COUNT_INTEGER'),
        ('checkpoint_identity', 'input_identity_sha256', {'input': 'wrong'}, 'CHECKPOINT_IDENTITY')]:
        damaged = copy.deepcopy(cp); damaged[key] = value
        case(name, stage, damaged, lambda p: checked_checkpoint(p, cp))
    damaged = copy.deepcopy(fake_cal); damaged['implementation_version'] = True
    case('calibration_bool_version', 'CALIBRATION_HEADER', damaged,
         lambda p: calibration_header(p, {'synthetic': 'pin'}))
    damaged = copy.deepcopy(fake_cal); damaged['outcome']['controls']['positive'] = True
    case('calibration_bool_count', 'CALIBRATION_HEADER', damaged,
         lambda p: calibration_header(p, {'synthetic': 'pin'}))
    require(len(cases) == 51 and sum(x['expected_stage'] == 'PASS' for x in cases) == 10,
            'CONTROL_COUNTS')
    save(out / 'controls.json', cases, budget)
    return dict(controls=CONTROL_COUNTS, complete_fraction_reference_pairs=26,
                synthetic_stream_pairs=10, actual_target_input_read=False)


def scientific(out, cal, software, args, budget):
    calibration_header(cal, software)
    require(args.singleton_gate is not None and args.singleton_gate_sha256 is not None,
            'SINGLETON_GATE_ARGUMENTS')
    accepted = read_hash(args.singleton_gate, args.singleton_gate_sha256, budget)
    gate(accepted, DATA)
    raw = {p: read_hash(ROOT / p, h, budget) for p, h in DATA.items()}
    decoded = raw[DATA_ROOT + 'parsed_input.json']
    require(decoded.get('schema') == 'FIXED17_DUAL_GRAM_PARSED_INPUT_V1'
            and typed_same(decoded.get('support_vertices'), list(range(17))), 'FIXED_INPUT_HEADER')
    h = [[0] * 17 for _ in range(17)]
    for row in BASE_ROWS:
        for i, j in itertools.combinations(row, 2):
            h[i][j] = h[j][i] = 1
    require(typed_same(decoded.get('induced_adjacency'), h), 'FIXED_INPUT_ALL289')
    masks = masks_checked(decoded.get('ordered_masks'), 17, 472)
    upper = scaled_inverse(raw[DATA_ROOT + 'upper_inverse_certificate.json'], 'upper', 17)
    lower = scaled_inverse(raw[DATA_ROOT + 'lower_inverse_certificate.json'], 'lower', 17)
    c = context(masks, upper, lower)
    old_records = raw[DATA_ROOT + 'singletons.json']
    require(type(old_records) is list and len(old_records) == 472, 'SINGLETON_POPULATION')
    for i, old in enumerate(old_records):
        budget.tick()
        require(type(old.get('index')) is int and old['index'] == i
            and type(old.get('mask')) is int and old['mask'] == masks[i], 'SINGLETON_COORDINATES')
        require(rational(old.get('upper_margin')) == F(c['du'][i], 81 * c['d'])
            and rational(old.get('lower_margin')) == F(c['dl'][i], c['e']), 'SINGLETON_INTEGER_ADAPTER')
    identities = {**DATA, str(args.singleton_gate): args.singleton_gate_sha256}
    save(out / 'scaled_input.json', dict(schema='DUAL_GRAM_PAIR_SCALED_INPUT_V1',
        dimension=17, ordered_masks=masks, induced_adjacency=h,
        upper_denominator=c['d'], upper_numerator=c['N'], lower_denominator=c['e'],
        lower_numerator=c['P'], upper_vectors_r=c['r'], upper_products_Nr=c['Nr'],
        lower_vectors=c['t'], lower_products_Pt=c['Pt'], upper_diagonals=c['du'],
        lower_diagonals=c['dl'], input_identity_sha256=identities,
        inverse_generation_calls=0, original_inverse_identities_authenticated_by_gate=True), budget)
    return stream(out, c, identities, budget)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('mode', choices=['calibrate', 'pairs'])
    ap.add_argument('--seconds', type=float, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--self-sha256', required=True)
    ap.add_argument('--spec-sha256', required=True)
    ap.add_argument('--calibration', type=Path)
    ap.add_argument('--calibration-sha256')
    ap.add_argument('--singleton-gate', type=Path)
    ap.add_argument('--singleton-gate-sha256')
    args = ap.parse_args()
    budget = Budget(args.seconds)
    args.out.mkdir(parents=True, exist_ok=False)
    software = {SELF: args.self_sha256, SPEC: args.spec_sha256}
    try:
        for p, h in software.items():
            budget.tick()
            require(hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == h, 'SOURCE_HASH')
        if args.mode == 'calibrate':
            result = calibrate(args.out, budget)
        else:
            require(args.calibration is not None and args.calibration_sha256 is not None,
                    'CALIBRATION_ARGUMENTS')
            cal = read_hash(args.calibration, args.calibration_sha256, budget)
            result = scientific(args.out, cal, software, args, budget)
        closing = dict(software)
        if args.mode == 'pairs':
            closing.update(DATA)
            closing[str(args.singleton_gate)] = args.singleton_gate_sha256
            closing[str(args.calibration)] = args.calibration_sha256
        for p, h in closing.items():
            budget.tick()
            pp = Path(p) if Path(p).is_absolute() else ROOT / p
            require(hashlib.sha256(pp.read_bytes()).hexdigest() == h, 'CLOSING_INPUT_HASH')
            budget.tick()
        outputs = {}
        for p in sorted(args.out.rglob('*')):
            if p.is_file():
                budget.tick()
                outputs[p.relative_to(args.out).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
                budget.tick()
        summary = dict(status=CAL_STATUS if args.mode == 'calibrate' else
            'CANDIDATE_FIXED17_DUAL_GRAM_PAIR_V1_COMPLETE', implementation_version=1,
            timestamp=datetime.now(timezone.utc).isoformat(),
            producer='/root/structural', command=sys.argv, cwd=str(ROOT),
            source_software=software, actual_target_input_read=args.mode == 'pairs',
            outcome=result, inputs_sha256=closing, outputs_sha256=outputs,
            target_resolution='NONE', independent_approval=False, LP_calls=0,
            inverse_generation_calls=0, pairs_launched=args.mode == 'pairs',
            conditional_fixed_induced17_only=True, complete_ancestor_closure_rehashed=False,
            deadline=budget.deadline.status(), automatic_retry=False,
            durability='Complete part/CP boundaries durable; unexpected exception/hardkill may lose pending suffix')
        save(args.out / 'summary.json', summary, budget)
        return 0
    except Exception as exc:
        failure = dict(status='FAILED_PRESERVED', stage=getattr(exc, 'stage', type(exc).__name__),
                       error=str(exc), deadline=budget.deadline.status(), automatic_retry=False)
        with (args.out / 'failure.json').open('x', encoding='utf8') as f:
            json.dump(failure, f, indent=2)
            f.write('\n')
        raise


if __name__ == '__main__':
    raise SystemExit(main())
