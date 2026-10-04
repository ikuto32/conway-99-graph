"""SOURCE_ONLY: exact fixed-induced17 upper/lower Gram singleton diagnostic.

No work occurs on import. This producer is new; old LP/type gates authenticate
literal inputs, not this implementation. A different verifier is required.
"""
from __future__ import annotations

import argparse
import copy
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import itertools
import json
from pathlib import Path
import sys

from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SELF = 'acceleration/diagnose_20261004_fixed17_dual_gram_singletons_v1.py'
SPEC = 'acceleration/diagnose_20261004_fixed17_dual_gram_singletons_v1_spec.md'
MODEL = 'acceleration/results/20261003_external_moment_outside_cn_filter01/filtered_system.json'
TYPES = 'acceleration/results/20261003_external_moment_outside_cn_filter01/types.json'
GATE = 'acceleration/results/20261003_independent_review/external_moment_outside_cn_filter_full01/summary.json'
EXPECTED = {
    MODEL: 'c628c76325d5b49106740bce7c6d3b72bc7728fdc78d85437ad484f3afbd7306',
    TYPES: '87d0272e244f60f1eefa06d3a0b2d0179a275791f7bb586992b16f648595bad2',
    GATE: '50b096b69decdea439097199cdb93a00f4c67de8653c224cbd90312dfcf2620a',
}
CAL_STATUS = 'FIXED17_DUAL_GRAM_SINGLETON_V1_AUTHOR_CONTROLS_PASS'
FULL_STATUS = 'CANDIDATE_FIXED17_DUAL_GRAM_SINGLETON_V1_COMPLETE'
CONTROL_COUNTS = dict(positive=15, strict_negative=37, total=52,
                      all_expected_actual_match=True, fixture_n=2,
                      complete_fixture_types=4)
# Literal original fixed-base coordinates, not a graph enumeration PID.
BASE_ROWS = [[0, 1, 2], [0, 3, 4], [0, 5, 6], [1, 7, 9], [1, 8, 10],
             [15, 11, 14], [16, 12, 13], [2, 15, 16], [3, 7, 11],
             [4, 8, 12], [5, 9, 13], [6, 10, 14]]


class Veto(ValueError):
    def __init__(self, stage):
        super().__init__(stage)
        self.stage = stage


def require(ok, stage):
    if not ok:
        raise Veto(stage)


def exact_int(value, stage):
    require(type(value) is int, stage)
    return value


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
        q = F(value)
    except (ValueError, ZeroDivisionError):
        raise Veto('RATIONAL_CANONICAL') from None
    require(str(q) == value, 'RATIONAL_CANONICAL')
    return q


def no_duplicates(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, 'JSON_DUPLICATE')
        result[key] = value
    return result


def parse(raw):
    def bad_constant(_):
        raise Veto('JSON_CONSTANT')
    try:
        return json.loads(raw, object_pairs_hook=no_duplicates,
                          parse_constant=bad_constant)
    except json.JSONDecodeError:
        raise Veto('JSON_SYNTAX') from None


class Budget:
    def __init__(self, seconds):
        self.deadline = CommandDeadline(seconds, allocation_reason=
            'Exact rational inverse/LDL products and complete singleton records, including I/O')

    def tick(self):
        s = self.deadline.status()
        require(not s['stop_required'] and s['remaining_seconds'] > 20,
                'SAVE_RESERVE_STOP')


def hash_read(path, expected, budget):
    budget.tick()
    data = (ROOT / path).read_bytes()
    require(hashlib.sha256(data).hexdigest() == expected, 'INPUT_HASH')
    budget.tick()
    return parse(data.decode('utf8'))


def save(path, value, budget):
    budget.tick()
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')
    budget.tick()


def serial(matrix):
    return [[str(x) for x in row] for row in matrix]


def product(a, b, budget):
    n = len(a)
    require(n > 0 and len(b) == n and all(len(r) == n for r in a + b),
            'MATRIX_SHAPE')
    result = []
    for i in range(n):
        budget.tick()
        result.append([sum((a[i][k] * b[k][j] for k in range(n)), F(0))
                       for j in range(n)])
    return result


def identity(n):
    return [[F(int(i == j)) for j in range(n)] for i in range(n)]


def inverse(a, budget):
    n = len(a)
    aug = [list(row) + identity(n)[i] for i, row in enumerate(a)]
    for k in range(n):
        budget.tick()
        pivot = next((i for i in range(k, n) if aug[i][k]), None)
        require(pivot is not None, 'INVERSE_SINGULAR')
        aug[k], aug[pivot] = aug[pivot], aug[k]
        p = aug[k][k]
        aug[k] = [x / p for x in aug[k]]
        for i in range(n):
            if i != k:
                c = aug[i][k]
                if c:
                    aug[i] = [x - c * y for x, y in zip(aug[i], aug[k])]
    return [row[n:] for row in aug]


def check_inverse(a, inv, budget):
    left = product(a, inv, budget)
    right = product(inv, a, budget)
    require(left == identity(len(a)) and right == identity(len(a)),
            'INVERSE_IDENTITY')
    return left, right


def ldl(a, budget):
    n = len(a)
    require(n > 0 and all(len(r) == n for r in a), 'MATRIX_SHAPE')
    require(all(a[i][j] == a[j][i] for i in range(n) for j in range(n)),
            'MATRIX_SYMMETRY')
    lower, diagonal = identity(n), []
    for j in range(n):
        budget.tick()
        pivot = a[j][j] - sum((lower[j][k] ** 2 * diagonal[k]
                              for k in range(j)), F(0))
        require(pivot > 0, 'GRAM_NOT_POSITIVE_DEFINITE')
        diagonal.append(pivot)
        for i in range(j + 1, n):
            lower[i][j] = (a[i][j] - sum((lower[i][k] * lower[j][k] * diagonal[k]
                                        for k in range(j)), F(0))) / pivot
    rebuilt = [[sum((lower[i][k] * diagonal[k] * lower[j][k]
                     for k in range(n)), F(0)) for j in range(n)] for i in range(n)]
    require(rebuilt == a, 'LDL_IDENTITY')
    budget.tick()
    return lower, diagonal, rebuilt


def geometry(h, n):
    require(type(h) is list and len(h) == n and n > 0 and
            all(type(r) is list and len(r) == n for r in h), 'H_SHAPE')
    require(all(type(x) is int for row in h for x in row), 'H_INTEGER')
    require(all(x in (0, 1) for row in h for x in row), 'H_BINARY')
    require(all(h[i][i] == 0 for i in range(n)), 'H_DIAGONAL')
    require(all(h[i][j] == h[j][i] for i in range(n) for j in range(n)),
            'H_SYMMETRY')
    return [[F(3 * int(i == j) - h[i][j]) + F(1, 9)
             for j in range(n)] for i in range(n)], [
        [F(4 * int(i == j) + h[i][j]) for j in range(n)] for i in range(n)]


def decode_types(rows, n, expected_count):
    require(type(rows) is list and len(rows) == expected_count, 'TYPE_POPULATION')
    pairs = list(itertools.combinations(range(n), 2))
    masks = []
    for row in rows:
        require(type(row) is dict and set(row) == {'mask', 'coefficient'}, 'TYPE_KEYS')
        m = exact_int(row['mask'], 'MASK_INTEGER')
        require(0 <= m < (1 << n), 'MASK_RANGE')
        require(not masks or m > masks[-1], 'MASK_ORDER')
        c = row['coefficient']
        require(type(c) is list and len(c) == 1 + n + len(pairs), 'COEFFICIENT_SHAPE')
        require(all(type(x) is int for x in c), 'COEFFICIENT_INTEGER')
        bits = [(m >> i) & 1 for i in range(n)]
        require(c == [1] + bits + [bits[i] * bits[j] for i, j in pairs],
                'COEFFICIENT_IDENTITY')
        masks.append(m)
    return masks


def gate(g, expected):
    require(type(g) is dict and g.get('status') ==
            'INDEPENDENT_EXTERNAL_MOMENT_OUTSIDE_CN_FILTER_V1_COMPLETE_PASS'
            and g.get('producer') == '/root/checkpoint_audit'
            and g.get('verifier') == '/root/native_driver'
            and g.get('method') == 'independent_artifact_check'
            and type(g.get('implementation_version')) is int
            and g['implementation_version'] == 1
            and g.get('target_resolution') == 'NONE', 'GATE_HEADER')
    require(type(g.get('inputs_sha256')) is dict and
            all(g['inputs_sha256'].get(p) == h for p, h in expected.items()),
            'GATE_DIRECT_PINS')


def vector_product(a, x):
    return [sum((a[i][j] * x[j] for j in range(len(x))), F(0))
            for i in range(len(x))]


def pair_bits(qu, qv, cross, lu, lv, lower_cross, intersection):
    upper, lower, cn = [], [], []
    for a in (0, 1):
        if qu <= F(28, 9) and qv <= F(28, 9) and (
                F(1, 9) - a - cross) ** 2 <= (F(28, 9) - qu) * (F(28, 9) - qv):
            upper.append(a)
        if lu <= 4 and lv <= 4 and (a - lower_cross) ** 2 <= (4 - lu) * (4 - lv):
            lower.append(a)
        if intersection <= (1 if a else 2):
            cn.append(a)
    return upper, lower, cn, sorted(set(upper) & set(lower) & set(cn))


def singleton(index, mask, upper_inverse, lower_inverse):
    n = len(upper_inverse)
    bits = [(mask >> i) & 1 for i in range(n)]
    b = [F(1, 9) - x for x in bits]
    ux, lx = vector_product(upper_inverse, b), vector_product(lower_inverse, bits)
    q = sum((x * y for x, y in zip(b, ux)), F(0))
    l = sum((x * y for x, y in zip(bits, lx)), F(0))
    rules = pair_bits(q, q, q, l, l, l, sum(bits))
    return dict(index=index, mask=mask, bits=bits, upper_vector=[str(x) for x in b],
                upper_inverse_product=[str(x) for x in ux], upper_q=str(q),
                upper_margin=str(F(28, 9) - q), upper_pass=q <= F(28, 9),
                lower_inverse_product=[str(x) for x in lx], lower_q=str(l),
                lower_margin=str(4 - l), lower_pass=l <= 4,
                singleton_pass=q <= F(28, 9) and l <= 4,
                equal_type_distinct_vertices_upper_bits=rules[0],
                equal_type_distinct_vertices_lower_bits=rules[1],
                equal_type_distinct_vertices_cn_bits=rules[2],
                equal_type_distinct_vertices_combined_bits=rules[3])


def check_record(r, index, mask, ui, li):
    expected = singleton(index, mask, ui, li)
    require(type(r) is dict and set(r) == set(expected), 'RECORD_KEYS')
    for key in ('index', 'mask'):
        exact_int(r[key], 'RECORD_INTEGER')
    for key in ('upper_pass', 'lower_pass', 'singleton_pass'):
        require(type(r[key]) is bool, 'RECORD_BOOLEAN')
    for key in ('upper_q', 'lower_q', 'upper_margin', 'lower_margin'):
        rational(r[key])
    for key in ('bits', 'equal_type_distinct_vertices_upper_bits',
                'equal_type_distinct_vertices_lower_bits', 'equal_type_distinct_vertices_cn_bits',
                'equal_type_distinct_vertices_combined_bits'):
        require(type(r[key]) is list and all(type(x) is int for x in r[key]),
                'RECORD_BITS_INTEGER')
    require(r == expected, 'RECORD_IDENTITY')


def fixture_types(n, masks):
    return [dict(mask=m, coefficient=[1] + [(m >> i) & 1 for i in range(n)] +
                 [((m >> i) & 1) * ((m >> j) & 1)
                  for i, j in itertools.combinations(range(n), 2)]) for m in masks]


def calibration_header(calibration, software):
    require(type(calibration) is dict and calibration.get('status') == CAL_STATUS
            and type(calibration.get('implementation_version')) is int
            and calibration['implementation_version'] == 1
            and typed_same(calibration.get('source_software'), software)
            and calibration.get('actual_target_input_read') is False
            and typed_same(calibration.get('controls'), CONTROL_COUNTS),
            'CALIBRATION_HEADER')


def fixed_base(h):
    expected = [[0] * 17 for _ in range(17)]
    for row in BASE_ROWS:
        for i, j in itertools.combinations(row, 2):
            expected[i][j] = expected[j][i] = 1
    require(h == expected, 'FIXED_BASE_ALL289')
    # Row indices are the four positive A-B-free rows in their literal order.
    pa = [[0, 1], [2, 3]]
    pb = [[0, 2], [1, 3]]
    pr = [[0, 3], [1, 2]]
    require(len({tuple(tuple(p) for p in m) for m in [pa, pb, pr]}) == 3,
            'FIXED_BASE_CLASS_IV')
    return dict(literal_twelve_rows=BASE_ROWS, positive_row_order=BASE_ROWS[8:],
                centers=[0, 1], common_center_neighbor=2, bridge_endpoints=[15, 16],
                free_sides=[[11, 14], [12, 13]], PA=pa, PB=pb, PR=pr,
                partition_pattern='all three distinct: class IV',
                all289_literal_edge_union_entries_compared=True,
                enumeration_PID_not_used=True)


def controls(out, budget):
    records = []

    def case(name, expected, payload, action):
        save(out / (name + '.json'), payload, budget)
        try:
            action(payload)
            actual = 'PASS'
        except Veto as e:
            actual = e.stage
        records.append(dict(case=name, expected_stage=expected, actual_stage=actual))
        require(actual == expected, 'CONTROL_STAGE_MISMATCH')

    h = [[0, 0], [0, 0]]
    u, l = geometry(h, 2)
    ui, li = inverse(u, budget), inverse(l, budget)
    require(ui == [[F(28, 87), F(-1, 87)], [F(-1, 87), F(28, 87)]], 'HAND_UPPER')
    require(li == [[F(1, 4), F(0)], [F(0), F(1, 4)]], 'HAND_LOWER')
    hand = [singleton(i, m, ui, li) for i, m in enumerate(range(4))]
    require([r['upper_q'] for r in hand] == ['2/261', '68/261', '68/261', '128/261'], 'HAND_Q')
    case('positive_inverse', 'PASS', serial(ui),
         lambda p: check_inverse(u, [[rational(x) for x in row] for row in p], budget))
    case('positive_lower_inverse', 'PASS', serial(li),
         lambda p: check_inverse(l, [[rational(x) for x in row] for row in p], budget))
    case('positive_ldl', 'PASS', serial(u), lambda p: ldl([[rational(x) for x in row] for row in p], budget))
    case('positive_types', 'PASS', fixture_types(2, range(4)), lambda p: decode_types(p, 2, 4))
    case('positive_record', 'PASS', hand[1], lambda p: check_record(p, 1, 1, ui, li))
    for name, q, lq, bit, channel in (
            ('upper_nonadj_boundary', F(29, 18), F(0), 0, 0),
            ('upper_adj_boundary', F(10, 9), F(0), 1, 0),
            ('lower_nonadj_boundary', F(0), F(2), 0, 1),
            ('lower_adj_boundary', F(0), F(5, 2), 1, 1)):
        case('positive_' + name, 'PASS', dict(q=str(q), l=str(lq), bit=bit, channel=channel),
             lambda p: require(p['bit'] in pair_bits(rational(p['q']), rational(p['q']),
                rational(p['q']), rational(p['l']), rational(p['l']), rational(p['l']), 0)[p['channel']], 'HAND_THRESHOLD'))
    fake = dict(status='INDEPENDENT_EXTERNAL_MOMENT_OUTSIDE_CN_FILTER_V1_COMPLETE_PASS',
                producer='/root/checkpoint_audit', verifier='/root/native_driver',
                method='independent_artifact_check', implementation_version=1,
                target_resolution='NONE', inputs_sha256={'model': 'a', 'types': 'b'})
    case('positive_gate', 'PASS', fake, lambda p: gate(p, {'model': 'a', 'types': 'b'}))
    # ROOT suggested this hand fixture; it is shared author engineering evidence.
    tri_u, tri_l = geometry([[0, 1, 1], [1, 0, 1], [1, 1, 0]], 3)
    tri_ui = [[F(int(i == j), 4) + F(1, 6) for j in range(3)] for i in range(3)]
    tri_li = [[F(int(i == j), 3) - F(1, 18) for j in range(3)] for i in range(3)]

    def triangle_inverse(p):
        for name, matrix in [('upper', tri_u), ('lower', tri_l)]:
            actual = [[rational(x) for x in row] for row in p[name]]
            check_inverse(matrix, actual, budget)
            ldl(matrix, budget)

    case('positive_triangle_inverse', 'PASS', dict(upper=serial(tri_ui), lower=serial(tri_li)), triangle_inverse)

    def triangle_q(p):
        for i, r in enumerate(p):
            mask = (0, 1, 2, 4)[i]
            check_record(r, i, mask, tri_ui, tri_li)
        require(p[0]['upper_q'] == '1/36' and p[0]['lower_q'] == '0' and
                all(r['upper_q'] == '5/18' and r['lower_q'] == '5/18' for r in p[1:]), 'HAND_TRIANGLE_Q')

    case('positive_triangle_q', 'PASS', [singleton(i, m, tri_ui, tri_li)
         for i, m in enumerate((0, 1, 2, 4))], triangle_q)
    synthetic_u, synthetic_l = geometry([[0] * 17 for _ in range(17)], 17)
    synthetic_ui = [[F(int(i == j), 3) - F(1, 132) for j in range(17)] for i in range(17)]
    synthetic_li = [[F(int(i == j), 4) for j in range(17)] for i in range(17)]

    def full_products(p):
        for name, matrix in [('upper', synthetic_u), ('lower', synthetic_l)]:
            inv = [[rational(x) for x in row] for row in p[name]]
            check_inverse(matrix, inv, budget)
            ldl(matrix, budget)

    case('positive_synthetic17_products', 'PASS', dict(upper=serial(synthetic_ui), lower=serial(synthetic_li)), full_products)

    def last_type(p):
        check_record(p, 0, 1 << 16, synthetic_ui, synthetic_li)
        require(p['upper_q'] == '32/99' and p['lower_q'] == '1/4', 'HAND_LAST_Q')

    case('positive_last_coordinate17', 'PASS', singleton(0, 1 << 16, synthetic_ui, synthetic_li), last_type)
    fake_cal = dict(status=CAL_STATUS, implementation_version=1,
                    source_software={'synthetic_source': 'synthetic_hash'},
                    actual_target_input_read=False, controls=copy.deepcopy(CONTROL_COUNTS))
    case('positive_calibration_header', 'PASS', fake_cal,
         lambda p: calibration_header(p, {'synthetic_source': 'synthetic_hash'}))
    for name, damage, stage in (
            ('h_bool', [[False, 0], [0, 0]], 'H_INTEGER'),
            ('h_float', [[0.0, 0], [0, 0]], 'H_INTEGER'),
            ('h_shape', [[0]], 'H_SHAPE'),
            ('h_diagonal', [[1, 0], [0, 0]], 'H_DIAGONAL'),
            ('h_asymmetric', [[0, 1], [0, 0]], 'H_SYMMETRY'),
            ('h_nonbinary', [[0, 2], [2, 0]], 'H_BINARY')):
        case(name, stage, damage, lambda p: geometry(p, 2))
    base = fixture_types(2, [0, 1])
    for name, field, value, stage in (
            ('mask_bool', 'mask', False, 'MASK_INTEGER'),
            ('mask_float', 'mask', 0.0, 'MASK_INTEGER'),
            ('mask_negative', 'mask', -1, 'MASK_RANGE'),
            ('mask_high', 'mask', 4, 'MASK_RANGE'),
            ('coefficient_bool', 'coefficient', [True, 0, 0, 0], 'COEFFICIENT_INTEGER'),
            ('coefficient_wrong', 'coefficient', [0, 0, 0, 0], 'COEFFICIENT_IDENTITY'),
            ('coefficient_short', 'coefficient', [1], 'COEFFICIENT_SHAPE')):
        damaged = copy.deepcopy(base)
        damaged[0][field] = value
        case(name, stage, damaged, lambda p: decode_types(p, 2, 2))
    duplicate = copy.deepcopy(base); duplicate[1] = copy.deepcopy(duplicate[0])
    case('mask_duplicate', 'MASK_ORDER', duplicate, lambda p: decode_types(p, 2, 2))
    case('mask_reversed', 'MASK_ORDER', list(reversed(base)), lambda p: decode_types(p, 2, 2))
    case('type_population', 'TYPE_POPULATION', base[:1], lambda p: decode_types(p, 2, 2))
    extra = copy.deepcopy(base); extra[0]['extra'] = 1
    case('type_keys', 'TYPE_KEYS', extra, lambda p: decode_types(p, 2, 2))
    for name, p, stage in (('fraction_bool', True, 'RATIONAL_TYPE'),
                           ('fraction_float', 0.0, 'RATIONAL_TYPE'),
                           ('fraction_alias', '2/2', 'RATIONAL_CANONICAL')):
        case(name, stage, p, rational)
    wrong = serial(ui); wrong[1][1] = '0'
    case('inverse_wrong_last', 'INVERSE_IDENTITY', wrong,
         lambda p: check_inverse(u, [[rational(x) for x in row] for row in p], budget))
    case('ldl_indefinite', 'GRAM_NOT_POSITIVE_DEFINITE', [['1', '-3/4', '-3/4'], ['-3/4', '1', '-3/4'], ['-3/4', '-3/4', '1']],
         lambda p: ldl([[rational(x) for x in row] for row in p], budget))
    case('ldl_zero', 'GRAM_NOT_POSITIVE_DEFINITE', [['0']], lambda p: ldl([[rational(x) for x in row] for row in p], budget))
    for name, key, value, stage in (
            ('record_bool_index', 'index', True, 'RECORD_INTEGER'),
            ('record_integer_flag', 'singleton_pass', 1, 'RECORD_BOOLEAN'),
            ('record_wrong_q', 'upper_q', '0', 'RECORD_IDENTITY'),
            ('record_wrong_margin', 'lower_margin', '0', 'RECORD_IDENTITY'),
            ('record_bool_bits', 'bits', [True, 0], 'RECORD_BITS_INTEGER')):
        damaged = copy.deepcopy(hand[1]); damaged[key] = value
        case(name, stage, damaged, lambda p: check_record(p, 1, 1, ui, li))
    for name, key, value in (('gate_status', 'status', 'CANDIDATE'),
                             ('gate_verifier', 'verifier', '/root/structural'),
                             ('gate_bool_version', 'implementation_version', True),
                             ('gate_method', 'method', 'independent_derivation')):
        damaged = copy.deepcopy(fake); damaged[key] = value
        case(name, 'GATE_HEADER', damaged, lambda p: gate(p, {'model': 'a', 'types': 'b'}))
    damaged = copy.deepcopy(fake); damaged['inputs_sha256']['model'] = 'x'
    case('gate_direct_pin', 'GATE_DIRECT_PINS', damaged, lambda p: gate(p, {'model': 'a', 'types': 'b'}))
    case('json_duplicate', 'JSON_DUPLICATE', '{"a":0,"a":1}', parse)
    case('json_nonfinite', 'JSON_CONSTANT', '{"a":NaN}', parse)
    bad_cal = copy.deepcopy(fake_cal); bad_cal['controls']['positive'] = 15.0
    case('calibration_float_count', 'CALIBRATION_HEADER', bad_cal,
         lambda p: calibration_header(p, {'synthetic_source': 'synthetic_hash'}))
    bad_cal = copy.deepcopy(fake_cal); bad_cal['controls']['all_expected_actual_match'] = 1
    case('calibration_integer_flag', 'CALIBRATION_HEADER', bad_cal,
         lambda p: calibration_header(p, {'synthetic_source': 'synthetic_hash'}))
    require(len(records) == CONTROL_COUNTS['total'], 'CONTROL_POPULATION')
    save(out / 'controls.json', records, budget)
    return copy.deepcopy(CONTROL_COUNTS)


def scientific(out, calibration, budget):
    calibration_header(calibration, SOFTWARE)
    model = hash_read(MODEL, EXPECTED[MODEL], budget)
    rows = hash_read(TYPES, EXPECTED[TYPES], budget)
    accepted = hash_read(GATE, EXPECTED[GATE], budget)
    gate(accepted, {MODEL: EXPECTED[MODEL], TYPES: EXPECTED[TYPES]})
    require(model.get('schema') == 'OUTSIDE_VERTEX_CN_FILTERED_MOMENT_SYSTEM_V1'
            and all(type(model.get(k)) is int and model[k] == v for k, v in
                [('target_order', 99), ('target_degree', 14), ('adjacent_cn', 1),
                 ('nonadjacent_cn', 2), ('eligible_type_count', 472)]), 'MODEL_HEADER')
    vertices = model.get('ordered_support_vertices')
    require(type(vertices) is list and all(type(v) is int for v in vertices)
            and vertices == list(range(17)), 'SUPPORT_ORDER')
    labels = [{'kind': 'total'}] + [{'kind': 'vertex', 'vertex': i} for i in range(17)] + [
        {'kind': 'pair', 'vertices': [i, j]} for i, j in itertools.combinations(range(17), 2)]
    require(typed_same(model.get('row_labels'), labels), 'ROW_LABELS')
    h = model.get('induced_adjacency')
    u, l = geometry(h, 17)
    base_identity = fixed_base(h)
    masks = decode_types(rows, 17, 472)
    save(out / 'parsed_input.json', dict(schema='FIXED17_DUAL_GRAM_PARSED_INPUT_V1',
        support_vertices=vertices, induced_adjacency=h, ordered_masks=masks,
        exact_class_IV_identity=base_identity,
        authenticated_eligible_universe_only=True, complete_all17bit_masks_reenumerated=False), budget)
    matrices = {}
    for name, a in [('upper', u), ('lower', l)]:
        low, diag, rebuilt = ldl(a, budget)
        inv = inverse(a, budget)
        left, right = check_inverse(a, inv, budget)
        matrices[name] = inv
        save(out / (name + '_inverse_certificate.json'), dict(
            schema='EXACT_DUAL_GRAM_INVERSE_LDL_CERTIFICATE_V1', gram=name, dimension=17,
            matrix=serial(a), inverse=serial(inv), left_product=serial(left), right_product=serial(right),
            unit_lower_factor=serial(low), positive_diagonal_pivots=[str(x) for x in diag],
            ldl_reconstruction=serial(rebuilt), all_left_right_289_entries_exact=True,
            positive_definite_exact=True), budget)
    records = []
    for i, mask in enumerate(masks):
        budget.tick()
        r = singleton(i, mask, matrices['upper'], matrices['lower'])
        check_record(r, i, mask, matrices['upper'], matrices['lower'])
        records.append(r)
        if (i + 1) % 32 == 0:
            save(out / ('checkpoint_%03d.json' % (i + 1)), dict(
                schema='DUAL_GRAM_SINGLETON_PREFIX_V1', next_index=i + 1,
                records=records[-32:], inputs_sha256=EXPECTED), budget)
    save(out / 'singletons.json', records, budget)
    save(out / 'checkpoint_472.json', dict(schema='DUAL_GRAM_SINGLETON_PREFIX_V1',
        next_index=472, records=records[-24:], inputs_sha256=EXPECTED), budget)
    return dict(complete_type_records=len(records), upper_pass=sum(r['upper_pass'] for r in records),
                lower_pass=sum(r['lower_pass'] for r in records),
                combined_pass=sum(r['singleton_pass'] for r in records),
                eliminated_by_upper=[r['index'] for r in records if not r['upper_pass']],
                eliminated_by_lower=[r['index'] for r in records if not r['lower_pass']],
                pairs_enumerated=0, future_unordered_pairs_including_equal_types=111628)


SOFTWARE = {}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('mode', choices=['calibrate', 'singletons'])
    ap.add_argument('--seconds', required=True, type=float)
    ap.add_argument('--out', required=True, type=Path)
    ap.add_argument('--self-sha256', required=True)
    ap.add_argument('--spec-sha256', required=True)
    ap.add_argument('--calibration', type=Path)
    ap.add_argument('--calibration-sha256')
    args = ap.parse_args()
    budget = Budget(args.seconds)
    out = args.out.resolve()
    require(not out.exists(), 'OUTPUT_EXISTS')
    out.mkdir(parents=True)
    try:
        for path, h in {SELF: args.self_sha256, SPEC: args.spec_sha256}.items():
            budget.tick()
            require(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == h, 'SOFTWARE_HASH')
            SOFTWARE[path] = h
        if args.mode == 'calibrate':
            result = controls(out, budget)
            status = CAL_STATUS
        else:
            require(args.calibration is not None and args.calibration_sha256 is not None,
                    'CALIBRATION_REQUIRED')
            budget.tick()
            data = args.calibration.read_bytes()
            require(hashlib.sha256(data).hexdigest() == args.calibration_sha256, 'CALIBRATION_HASH')
            result = scientific(out, parse(data.decode('utf8')), budget)
            status = FULL_STATUS
        budget.tick()
        closing = dict(SOFTWARE)
        if args.mode == 'singletons':
            closing.update(EXPECTED)
            closing[str(args.calibration)] = args.calibration_sha256
        for name, expected in closing.items():
            budget.tick()
            require(hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected,
                    'CLOSING_INPUT_HASH')
            budget.tick()
        outputs = {}
        for path in sorted(out.iterdir()):
            budget.tick()
            require(path.is_file(), 'OUTPUT_TREE')
            outputs[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
        summary = dict(status=status, implementation_version=1,
            timestamp=datetime.now(timezone.utc).isoformat(), producer='/root/structural',
            independent_approval=False, target_resolution='NONE',
            command=sys.argv, cwd=str(ROOT), source_software=SOFTWARE,
            actual_target_input_read=args.mode == 'singletons',
            fixed_induced17_only=args.mode == 'singletons',
            controls=result if args.mode == 'calibrate' else None,
            outcome=result if args.mode == 'singletons' else None,
            inputs_sha256=EXPECTED if args.mode == 'singletons' else {},
            outputs_sha256=outputs, mathematical_claim_status='CANDIDATE',
            closing_direct_pin_hashes_checked=True,
            complete_ancestor_evidence_closure_rehashed=False,
            LP_calls=0, RREF_calls=0, inverse_algorithm='exact Fraction Gauss-Jordan',
            positivity_certificate='exact unpivoted symmetric LDL with strictly positive pivots',
            pairs_automatically_launched=False, deadline=budget.deadline.status(),
            durability='Completed32-record boundaries and final24 saved; exception/hardkill does not guarantee pending suffix.')
        save(out / 'summary.json', summary, budget)
        return 0
    except BaseException as exc:
        payload = dict(status='FAILED_OR_NOT_COMPLETED_WITH_ALLOCATED_BUDGET',
                       stage=getattr(exc, 'stage', type(exc).__name__), reason=str(exc),
                       target_resolution='NONE', provisional_summary_is_not_a_gate=True,
                       pending_suffix_saved=False, automatic_retry=False,
                       deadline=budget.deadline.status())
        try:
            with (out / 'failure.json').open('x', encoding='utf8') as stream:
                json.dump(payload, stream, indent=2)
        except OSError:
            pass
        raise


if __name__ == '__main__':
    raise SystemExit(main())
