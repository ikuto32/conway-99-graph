"""Independent exact exterior-moment artifacts; no producer arithmetic imports."""
import argparse
from collections import Counter
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

ROOT = Path(__file__).resolve().parents[1]
SELF = Path(__file__).resolve()
SPEC = SELF.with_name(SELF.stem + '_spec.md')
PRODUCER = 'acceleration/census_20261003_external_neighborhood_moments_v1.py'
PRODUCER_SHA = 'e700720f74917de035fdd185d6b14cb75e1a6e16c55a2c1b4d250cb30811bc64'
PRODUCER_SPEC_SHA = '16d1eb55661b19f655ee320ec8cf5ccf38557bddf1545061c017fcb731f7effb'
PINS = {
    PRODUCER: PRODUCER_SHA,
    PRODUCER.replace('.py', '_spec.md'): PRODUCER_SPEC_SHA,
    'acceleration/command_deadline.py': '9876cc751a598845e55e27353f68557ff20054c1e2570239b27981ff950ca6b9',
    'acceleration/run_compute_command.py': '593a9feed6250739dc9672338df23ab171fc9a6a6db4196c1feb312efa33957a',
    'pyproject.toml': '273251fecebf5ea3d63cc568193026c684a54a7daf56da318aabbd31fadb8339',
    'uv.lock': 'a6da29ef244bb0e6495d577944880be595a40246938af99c4c4a325ee32122db',
    'docs/CANDIDATE_20261003_SEVENTEEN_POINT_EXTERNAL_NEIGHBOR_MOMENTS_V1.md': '70ef6392e86c6b9a3c9c6eac9b5d72abb9ea25741d3649282f66ac200bb93349',
    'acceleration/results/20261003_seventeen_point_external_moment_design01.json': '584cfbd723ceefe209dbefd00e9a64f403f474249458fe770313f294d194445c',
    'docs/CANDIDATE_20261003_SEVENTEEN_POINT_UNBALANCED_TWELVE_TRIANGLE_CIRCUIT_V1.md': 'f6f9e883b577d6969eafaac9239c37d637804786a08a6b5e676cebe0208e576b',
}
PROFILES = [('single', [0], {0: 4, 1: 4}), ('adjacent', [0, 1], {0: 2, 1: 2, 2: 2, 3: 1}),
            ('nonadjacent', [0, 4], {0: 1, 1: 2, 2: 2, 3: 2}),
            ('row', [0, 1, 2], {1: 2, 2: 2, 4: 2}), ('diagonal', [0, 4, 8], {3: 2, 5: 2, 6: 2})]


def need(ok, stage):
    if not ok:
        raise ValueError(stage)


def same(a, b):
    return json.dumps(a, sort_keys=True, allow_nan=False) == json.dumps(b, sort_keys=True, allow_nan=False)


def tick(deadline):
    s = deadline.status()
    need(not s['stop_required'] and s['remaining_seconds'] > 20, 'SAVE_RESERVE')


def strict_json(raw):
    need(type(raw) is bytes and len(raw) <= 64 * 1024 * 1024, 'JSON_BYTES')
    def pairs(items):
        answer = {}
        for name, value in items:
            need(name not in answer, 'JSON_DUPLICATE')
            answer[name] = value
        return answer
    def constant(_):
        raise ValueError('JSON_NONFINITE')
    return json.loads(raw.decode('utf8'), object_pairs_hook=pairs, parse_constant=constant)


def rational(value):
    need(type(value) is str and len(value) <= 4096
         and re.fullmatch(r'-?(0|[1-9][0-9]*)(/[1-9][0-9]*)?', value) is not None, 'RATIONAL_STRING')
    answer = Fraction(value)
    need(str(answer) == value, 'RATIONAL_CANONICAL')
    return answer


def geometry(h, n, k):
    need(type(h) is list and 0 < len(h) <= 17 and type(n) is int and type(k) is int
         and n >= len(h) and k > 0 and k % 2 == 0, 'PARAMETERS')
    m = len(h)
    need(all(type(row) is list and len(row) == m for row in h), 'H_SHAPE')
    need(all(type(x) is int and x in (0, 1) for row in h for x in row), 'H_BINARY_INTEGER')
    need(all(h[v][v] == 0 for v in range(m)), 'H_DIAGONAL')
    need(all(h[u][v] == h[v][u] for u in range(m) for v in range(m)), 'H_SYMMETRY')
    # Separate adjacency-set intersection path, not the producer's dot-product loop.
    neighborhoods = [{j for j, x in enumerate(row) if x} for row in h]
    c = [[len(neighborhoods[u] & neighborhoods[v]) for v in range(m)] for u in range(m)]
    b = [k - len(row) for row in neighborhoods]
    delta = [[None if u == v else 2 - h[u][v] - c[u][v] for v in range(m)] for u in range(m)]
    need(min(b) >= 0 and all(delta[u][v] >= 0 for u, v in itertools.combinations(range(m), 2)), 'NEGATIVE_DEFICIT')
    return c, b, delta, neighborhoods


def rebuild(h, n, k, deadline):
    c, b, delta, neighborhoods = geometry(h, n, k)
    m = len(h)
    pairs = list(itertools.combinations(range(m), 2))
    labels = [{'kind': 'total'}] + [{'kind': 'vertex', 'vertex': v} for v in range(m)]
    labels += [{'kind': 'pair', 'vertices': list(pair)} for pair in pairs]
    rhs = [n - m] + b + [delta[u][v] for u, v in pairs]
    columns, universe = [], []
    for mask in range(2 ** m):
        if mask % 512 == 0:
            tick(deadline)
        selected = {v for v in range(m) if (mask >> v) & 1}
        reason = 'ELIGIBLE'
        if len(selected) > k:
            reason = 'TARGET_DEGREE_CAPACITY'
        elif any(delta[u][v] == 0 for u, v in itertools.combinations(sorted(selected), 2)):
            reason = 'ZERO_PAIR_DEFICIT'
        else:
            internal_edges = {(u, v) for u, v in itertools.combinations(sorted(selected), 2) if v in neighborhoods[u]}
            incidence = Counter(v for edge in internal_edges for v in edge)
            if any(d > 1 for d in incidence.values()):
                reason = 'NOT_INDUCED_MATCHING'
            elif len(selected) - len(internal_edges) > k // 2:
                reason = 'NEIGHBOR_MATCHING_CAPACITY'
        universe.append({'mask': mask, 'decision': reason})
        if reason == 'ELIGIBLE':
            columns.append({'mask': mask, 'coefficient': [1] + [int(v in selected) for v in range(m)]
                            + [int(u in selected and v in selected) for u, v in pairs]})
    z = [[n - m] + b] + [[b[u]] + [b[u] if u == v else delta[u][v] for v in range(m)] for u in range(m)]
    model = dict(schema='EXTERIOR_NEIGHBOR_MOMENT_MODEL_V1', target_order=n, target_degree=k,
                 adjacent_cn=1, nonadjacent_cn=2, ordered_support_vertices=list(range(m)), induced_adjacency=h,
                 H_squared=c, vertex_rhs=b, pair_deficits=delta, row_labels=labels, right_hand_side=rhs,
                 gram_matrix=z, universe_mask_range=[0, 2 ** m - 1], eligible_type_count=len(columns),
                 decision_counts=dict(Counter(row['decision'] for row in universe)))
    tick(deadline)
    return model, columns, universe


def bilinear(z, u, v):
    return sum(x * z[i][j] * y for i, x in enumerate(u) for j, y in enumerate(v))


def exact_inertia(z, deadline):
    need(type(z) is list and z and all(type(row) is list and len(row) == len(z) for row in z), 'GRAM_SHAPE')
    need(all(type(x) is int for row in z for x in row), 'GRAM_INTEGER')
    need(all(z[i][j] == z[j][i] for i in range(len(z)) for j in range(len(z))), 'GRAM_SYMMETRY')
    # Re-evaluate every form against the original matrix using explicit basis
    # vectors. No producer Schur-complement cache or arithmetic is imported.
    basis = [[Fraction(int(i == j)) for i in range(len(z))] for j in range(len(z))]
    signs = [0, 0, 0]
    leading_positive = []
    negative_seen = False
    while basis:
        tick(deadline)
        diagonal = [bilinear(z, v, v) for v in basis]
        pick = next((i for i, p in enumerate(diagonal) if p), None)
        if pick is None:
            cross = next(((i, j, bilinear(z, basis[i], basis[j])) for i, j in itertools.combinations(range(len(basis)), 2)
                          if bilinear(z, basis[i], basis[j])), None)
            if cross is None:
                signs[2] += len(basis)
                break
            i, j, _ = cross
            u, v = basis[i], basis[j]
            basis[i] = [x + y for x, y in zip(u, v)]
            basis[j] = [x - y for x, y in zip(u, v)]
            negative_seen = True
            continue
        vector = basis.pop(pick)
        p = diagonal[pick]
        signs[0 if p > 0 else 1] += 1
        if p < 0:
            negative_seen = True
        elif not negative_seen:
            leading_positive.append(str(p))
        next_basis = []
        for other in basis:
            factor = bilinear(z, vector, other) / p
            next_basis.append([x - factor * y for x, y in zip(other, vector)])
        basis = next_basis
    return signs, leading_positive


def check_farkas(values, columns, rhs):
    need(type(values) is list and len(values) == len(rhs), 'FARKAS_LENGTH')
    y = [rational(v) for v in values]
    need(sum(v * r for v, r in zip(y, rhs)) < 0, 'FARKAS_RHS_SIGN')
    for column in columns:
        need(sum(v * a for v, a in zip(y, column['coefficient'])) >= 0, 'FARKAS_COLUMN_SIGN')
    return len(columns)


def check_gram(raw, z, deadline, columns=None, rhs=None):
    need(type(raw) is dict, 'GRAM_OBJECT')
    signs, prefix = exact_inertia(z, deadline)
    if raw.get('status') == 'CANDIDATE_EXACT_PSD_CONGRUENCE':
        need(set(raw) == {'status', 'positive_pivots', 'zero_dimension'}, 'GRAM_FIELDS')
        need(signs[1] == 0, 'GRAM_FALSE_PSD')
        need(same(raw['positive_pivots'], prefix), 'GRAM_PIVOTS')
        need(type(raw['zero_dimension']) is int and raw['zero_dimension'] == signs[2], 'GRAM_ZERO_DIMENSION')
    else:
        need(raw.get('status') == 'CANDIDATE_EXACT_NEGATIVE_GRAM_DIRECTION'
             and set(raw) == {'status', 'q', 'quadratic', 'farkas_vector', 'positive_pivots_before_negative'}, 'GRAM_FIELDS')
        need(type(raw['q']) is list and len(raw['q']) == len(z), 'GRAM_Q_LENGTH')
        q = [rational(v) for v in raw['q']]
        value = bilinear(z, q, q)
        need(value < 0 and rational(raw['quadratic']) == value, 'GRAM_NEGATIVE_QUADRATIC')
        expanded = [q[0] ** 2] + [2 * q[0] * x + x ** 2 for x in q[1:]]
        expanded += [2 * x * y for x, y in itertools.combinations(q[1:], 2)]
        need(same(raw['farkas_vector'], list(map(str, expanded))), 'GRAM_SQUARE_EXPANSION')
        need(same(raw['positive_pivots_before_negative'], prefix), 'GRAM_PIVOTS')
        if columns is not None:
            check_farkas(raw['farkas_vector'], columns, rhs)
    return dict(inertia=signs, exact_negative=signs[1] > 0)


def check_primal(raw, columns, rhs):
    need(type(raw) is dict and set(raw) == {'status', 'values', 'integer'}
         and raw['status'] == 'CANDIDATE_EXACT_MOMENT_PRIMAL', 'PRIMAL_OBJECT')
    need(type(raw['values']) is list and len(raw['values']) == len(columns), 'PRIMAL_LENGTH')
    x = [rational(v) for v in raw['values']]
    need(all(v >= 0 for v in x), 'PRIMAL_NONNEGATIVE')
    integer = all(v.denominator == 1 for v in x)
    need(type(raw['integer']) is bool and raw['integer'] == integer, 'PRIMAL_INTEGER_FLAG')
    for i, r in enumerate(rhs):
        need(sum(v * column['coefficient'][i] for v, column in zip(x, columns)) == r, 'PRIMAL_MOMENT')
    return dict(exact_nonnegative_rational=True, integer=integer, complete_moment_rows=len(rhs))


def check_bundle(model, columns, universe, h, n, k, deadline):
    expected, rebuilt, decisions = rebuild(h, n, k, deadline)
    need(type(model) is dict and set(model) == set(expected), 'MODEL_FIELDS')
    for key, value in expected.items():
        need(same(model[key], value), 'MODEL_FIELD:' + key)
    need(type(columns) is list and len(columns) == len(rebuilt), 'TYPE_POPULATION')
    for actual, wanted in zip(columns, rebuilt):
        need(type(actual) is dict and set(actual) == {'mask', 'coefficient'}, 'TYPE_FIELDS')
        need(type(actual['mask']) is int, 'TYPE_MASK_INTEGER')
        need(actual['mask'] == wanted['mask'], 'TYPE_ORDER')
        need(type(actual['coefficient']) is list and len(actual['coefficient']) == len(wanted['coefficient']), 'TYPE_COEFFICIENT_LENGTH')
        need(all(type(v) is int and v in (0, 1) for v in actual['coefficient']), 'TYPE_COEFFICIENT_BINARY')
        need(actual['coefficient'] == wanted['coefficient'], 'TYPE_COEFFICIENT')
    need(type(universe) is list and len(universe) == 2 ** len(h), 'UNIVERSE_POPULATION')
    for actual, wanted in zip(universe, decisions):
        need(type(actual) is dict and set(actual) == {'mask', 'decision'}, 'UNIVERSE_FIELDS')
        need(type(actual['mask']) is int and actual['mask'] == wanted['mask'], 'UNIVERSE_MASK')
        need(actual['decision'] == wanted['decision'], 'UNIVERSE_DECISION')
    return expected, rebuilt


def rook_fixture(selected, deadline):
    points = [(r, c) for r in range(3) for c in range(3)]
    adjacent = lambda u, v: u != v and (points[u][0] == points[v][0] or points[u][1] == points[v][1])
    h = [[int(adjacent(u, v)) for v in selected] for u in selected]
    exterior = Counter(sum(2 ** i for i, u in enumerate(selected) if adjacent(u, z)) for z in range(9) if z not in selected)
    model, columns, universe = rebuild(h, 9, 4, deadline)
    primal = dict(status='CANDIDATE_EXACT_MOMENT_PRIMAL', values=[str(exterior[c['mask']]) for c in columns], integer=True)
    return h, model, columns, universe, primal, dict(exterior)


def check_literal_exterior_primal(primal, columns, exterior):
    need(same(primal['values'], [str(exterior.get(c['mask'], 0)) for c in columns])
         and primal['integer'] is True, 'LITERAL_ROOK_EXTERIOR_PRIMAL')


def own_calibration(out, deadline, save):
    rook = [[int(i != j and (i // 3 == j // 3 or i % 3 == j % 3)) for j in range(9)] for i in range(9)]
    cn, _, _, _ = geometry(rook, 9, 4)
    need(all(cn[i][j] == (4 if i == j else 2 - rook[i][j]) for i in range(9) for j in range(9)), 'OWN_COMPLETE_ROOK_IDENTITY')
    packets = {}
    for name, selected, wanted in PROFILES:
        h, model, columns, universe, primal, exterior = rook_fixture(selected, deadline)
        need(exterior == wanted, 'HANDWRITTEN_ROOK_PROFILE')
        check_bundle(model, columns, universe, h, 9, 4, deadline)
        check_primal(primal, columns, model['right_hand_side'])
        check_literal_exterior_primal(primal, columns, exterior)
        packets[name] = (h, model, columns, universe, primal)
        save(name + '.json', dict(ordered_rook_vertices=selected, model=model, types=columns, universe=universe, primal=primal))
    grams = [([[1, 0], [0, 2]], [2, 0, 0]), ([[0, 1], [1, 0]], [1, 1, 0]),
             ([[1, 0], [0, -1]], [1, 1, 0]), ([[0, 0], [0, 0]], [0, 0, 2])]
    gram_records = [dict(status='CANDIDATE_EXACT_PSD_CONGRUENCE', positive_pivots=['1', '2'], zero_dimension=0),
                    dict(status='CANDIDATE_EXACT_NEGATIVE_GRAM_DIRECTION', q=['1', '-1'], quadratic='-2', farkas_vector=['1', '-1'], positive_pivots_before_negative=[]),
                    dict(status='CANDIDATE_EXACT_NEGATIVE_GRAM_DIRECTION', q=['0', '1'], quadratic='-1', farkas_vector=['0', '1'], positive_pivots_before_negative=['1']),
                    dict(status='CANDIDATE_EXACT_PSD_CONGRUENCE', positive_pivots=[], zero_dimension=2)]
    for (z, wanted), record in zip(grams, gram_records):
        need(exact_inertia(z, deadline)[0] == wanted, 'OWN_GRAM_INERTIA')
        check_gram(record, z, deadline)
    save('gram_inertia_controls.json', [{'matrix': z, 'expected_inertia': wanted, 'record': record}
                                       for (z, wanted), record in zip(grams, gram_records)])
    # A path is pair-eligible but fails the separately required matching test.
    path_model, path_columns, path_universe = rebuild([[0, 1, 0], [1, 0, 1], [0, 1, 0]], 9, 4, deadline)
    need(path_universe[7]['decision'] == 'NOT_INDUCED_MATCHING', 'PATH_MATCHING_DISTINCTION')
    toy_model, toy_columns, _ = rebuild([[0, 1, 1], [1, 0, 1], [1, 1, 0]], 5, 4, deadline)
    check_farkas(['1', '-1', '-1', '-1', '0', '0', '0'], toy_columns, toy_model['right_hand_side'])
    # Abstract exact certificate arithmetic: duplicate columns admit a real primal.
    check_primal(dict(status='CANDIDATE_EXACT_MOMENT_PRIMAL', values=['1/2', '1/2'], integer=False),
                 [{'coefficient': [1]}, {'coefficient': [1]}], [1])
    negatives = []
    h, model, columns, universe, primal = packets['nonadjacent']
    def reject(label, stage, kind, changed, call):
        tick(deadline)
        save('negative_' + label + '.json', dict(kind=kind, payload=changed, expected_stage=stage))
        # Execute the saved JSON payload rather than an unsaved mutation object.
        payload = strict_json((out / ('negative_' + label + '.json')).read_bytes())['payload']
        actual = None
        try:
            call(payload)
        except ValueError as error:
            actual = str(error)
        need(actual == stage, 'CALIBRATION_STAGE:' + label)
        negatives.append(dict(case=label, expected_stage=stage, actual_stage=actual))
    for label, bad, stage in [('bool_h', [[False]], 'H_BINARY_INTEGER'), ('float_h', [[0.0]], 'H_BINARY_INTEGER'),
                             ('loop', [[1]], 'H_DIAGONAL'), ('asymmetry', [[0, 1], [0, 0]], 'H_SYMMETRY'),
                             ('shape', [[0, 1]], 'H_SHAPE')]:
        reject(label, stage, 'h', bad, lambda bad: geometry(bad, 9, 4))
    for label, key, value in [('cn_diagonal', 'H_squared', [[1, 0], [0, 0]]),
                            ('deficit_sign', 'pair_deficits', [[None, -2], [-2, None]]),
                            ('point_order', 'ordered_support_vertices', [1, 0]),
                            ('rhs', 'right_hand_side', [6, 4, 4, 2]),
                            ('gram', 'gram_matrix', [[7, 4, 4], [4, 4, 1], [4, 1, 4]])]:
        bad = copy.deepcopy(model); bad[key] = value
        reject(label, 'MODEL_FIELD:' + key, 'model', bad,
               lambda bad: check_bundle(bad, columns, universe, h, 9, 4, deadline))
    for label, bad, stage in [('empty_type', columns[1:], 'TYPE_POPULATION'), ('eligible_pair', columns[:-1], 'TYPE_POPULATION')]:
        reject(label, stage, 'types', bad, lambda bad: check_bundle(model, bad, universe, h, 9, 4, deadline))
    for label, key, value, stage in [('duplicate_mask', 'mask', 0, 'TYPE_ORDER'),
                                   ('bool_mask', 'mask', True, 'TYPE_MASK_INTEGER'), ('float_mask', 'mask', 1.0, 'TYPE_MASK_INTEGER')]:
        bad = copy.deepcopy(columns); bad[1][key] = value
        reject(label, stage, 'types', bad, lambda bad: check_bundle(model, bad, universe, h, 9, 4, deadline))
    for label, value, stage in [('bool_coefficient', False, 'TYPE_COEFFICIENT_BINARY'),
                              ('float_coefficient', 0.0, 'TYPE_COEFFICIENT_BINARY'), ('wrong_coefficient', 1, 'TYPE_COEFFICIENT')]:
        bad = copy.deepcopy(columns); bad[0]['coefficient'][1] = value
        reject(label, stage, 'types', bad, lambda bad: check_bundle(model, bad, universe, h, 9, 4, deadline))
    reject('omitted_mask', 'UNIVERSE_POPULATION', 'universe', universe[:-1],
           lambda bad: check_bundle(model, columns, bad, h, 9, 4, deadline))
    for label, key, value, stage in [('duplicate_universe_mask', 'mask', 0, 'UNIVERSE_MASK'),
                                   ('bool_universe_mask', 'mask', True, 'UNIVERSE_MASK'),
                                   ('wrong_decision', 'decision', 'ZERO_PAIR_DEFICIT', 'UNIVERSE_DECISION')]:
        bad = copy.deepcopy(universe); bad[1][key] = value
        reject(label, stage, 'universe', bad, lambda bad: check_bundle(model, columns, bad, h, 9, 4, deadline))
    for label, index, value, stage in [('negative_primal', 0, '-1', 'PRIMAL_NONNEGATIVE'),
                                     ('altered_primal', 0, '0', 'PRIMAL_MOMENT'),
                                     ('float_primal', 0, 1.0, 'RATIONAL_STRING')]:
        bad = copy.deepcopy(primal); bad['values'][index] = value
        reject(label, stage, 'primal', bad, lambda bad: check_primal(bad, columns, model['right_hand_side']))
    bad = copy.deepcopy(primal); bad['integer'] = 1
    reject('bool_integer_alias', 'PRIMAL_INTEGER_FLAG', 'primal', bad,
           lambda bad: check_primal(bad, columns, model['right_hand_side']))
    reject('fractional_purported_integer', 'PRIMAL_INTEGER_FLAG', 'primal',
           dict(status='CANDIDATE_EXACT_MOMENT_PRIMAL', values=['1/2', '1/2'], integer=True),
           lambda bad: check_primal(bad, [{'coefficient': [1]}, {'coefficient': [1]}], [1]))
    reject('noncanonical_fraction', 'RATIONAL_CANONICAL', 'rational', '2/4', rational)
    reject('wrong_farkas_rhs', 'FARKAS_RHS_SIGN', 'farkas', ['1', '0', '0', '0'],
           lambda bad: check_farkas(bad, columns, model['right_hand_side']))
    reject('missing_column_inequality', 'FARKAS_COLUMN_SIGN', 'farkas', ['-1', '0', '0', '0'],
           lambda bad: check_farkas(bad, columns, model['right_hand_side']))
    row_h, row_model, row_columns, row_universe, _ = packets['row']
    bad = copy.deepcopy(row_model); bad['row_labels'].pop()
    reject('omitted_zero_row', 'MODEL_FIELD:row_labels', 'model', bad,
           lambda bad: check_bundle(bad, row_columns, row_universe, row_h, 9, 4, deadline))
    psd = dict(status='CANDIDATE_EXACT_PSD_CONGRUENCE', positive_pivots=['1', '2'], zero_dimension=0)
    bad = dict(psd, positive_pivots=['1', '3'])
    reject('forged_pivot', 'GRAM_PIVOTS', 'gram', bad, lambda bad: check_gram(bad, grams[0][0], deadline))
    reject('false_psd', 'GRAM_FALSE_PSD', 'gram', psd, lambda bad: check_gram(bad, grams[1][0], deadline))
    bad = dict(psd, zero_dimension=False)
    reject('bool_zero_dimension', 'GRAM_ZERO_DIMENSION', 'gram', bad, lambda bad: check_gram(bad, grams[0][0], deadline))
    negative = dict(status='CANDIDATE_EXACT_NEGATIVE_GRAM_DIRECTION', q=['1', '-1'], quadratic='-2',
                    farkas_vector=['1', '-1'], positive_pivots_before_negative=[])
    check_gram(negative, grams[1][0], deadline)
    bad = dict(negative, quadratic='2')
    reject('wrong_quadratic', 'GRAM_NEGATIVE_QUADRATIC', 'gram', bad, lambda bad: check_gram(bad, grams[1][0], deadline))
    bad = dict(negative, farkas_vector=['1', '1'])
    reject('wrong_square_expansion', 'GRAM_SQUARE_EXPANSION', 'gram', bad, lambda bad: check_gram(bad, grams[1][0], deadline))
    sparse_controls = []
    for name, selected, exterior in PROFILES:
        if name not in ('row', 'diagonal'):
            continue
        _, _, sparse_columns, _, sparse_primal = packets[name]
        absent = [c['mask'] for c in sparse_columns if c['mask'] not in exterior]
        need(absent and all(sparse_primal['values'][i] == '0'
             for i, c in enumerate(sparse_columns) if c['mask'] in absent), 'SPARSE_ZERO_POSITIVE')
        check_literal_exterior_primal(sparse_primal, sparse_columns, exterior)
        sparse_controls.append(dict(profile=name, absent_masks=absent,
            sparse_counts=[dict(mask=mask, count=count) for mask, count in sorted(exterior.items())],
            primal=sparse_primal, absent_frequency=0))
    save('sparse_zero_frequency_controls.json', sparse_controls)
    row_exterior = next(exterior for name, _, exterior in PROFILES if name == 'row')
    bad = copy.deepcopy(packets['row'][4]); bad['values'][0] = '1'
    reject('altered_zero_frequency_literal', 'LITERAL_ROOK_EXTERIOR_PRIMAL', 'primal', bad,
           lambda bad: check_literal_exterior_primal(bad, row_columns, row_exterior))
    # Strict reader controls are separate saved raw-byte cases.
    for label, raw, stage in [('duplicate_json', b'{"a":0,"a":1}', 'JSON_DUPLICATE'),
                              ('nonfinite_json', b'{"a":NaN}', 'JSON_NONFINITE')]:
        path = out / ('negative_' + label + '.raw.json'); path.write_bytes(raw); tick(deadline)
        observed = None
        try:
            strict_json(path.read_bytes())
        except ValueError as error:
            observed = str(error)
        need(observed == stage, 'CALIBRATION_STAGE:' + label)
        negatives.append(dict(case=label, expected_stage=stage, actual_stage=observed))
    need(len(negatives) == 39 and len(sparse_controls) == 2, 'OWN_CALIBRATION_POPULATION')
    save('controls.json', dict(rook_profiles=5, complete_rook_cn_entries=81, gram_inertia_cases=4, matching_path_case=1,
         exact_farkas_case=1, exact_fractional_primal_case=1, sparse_zero_frequency_cases=2, strict_negative=negatives))
    return dict(rook_profiles=5, complete_rook_cn_entries=81, gram_inertia_cases=4, matching_path_case=1,
                exact_farkas_case=1, exact_fractional_primal_case=1, sparse_zero_frequency_cases=2,
                strict_negative_cases=len(negatives), actual_producer_output_read=False)


def check_producer(args, deadline, read, pin):
    required = ['producer_root', 'producer_plan', 'producer_plan_sha256', 'supervision_out',
                'supervisor_manifest_sha256', 'supervisor_summary_sha256', 'producer_summary_sha256',
                'calibration', 'calibration_sha256']
    need(all(getattr(args, name) is not None for name in required), 'ACTUAL_INPUT_ARGUMENTS')
    calibration = read(args.calibration, args.calibration_sha256)
    need(calibration.get('status') == 'INDEPENDENT_EXTERNAL_NEIGHBOR_MOMENTS_V1_OWN_CALIBRATION_PASS'
         and type(calibration.get('checker_implementation_version')) is int
         and calibration['checker_implementation_version'] == 3
         and calibration.get('producer') == '/root' and calibration.get('verifier') == '/root/native_driver'
         and calibration.get('method') == 'independent_artifact_check' and calibration.get('target_resolution') == 'NONE', 'CALIBRATION_HEADER')
    need(same(calibration.get('checked_scope'), dict(rook_profiles=5, complete_rook_cn_entries=81, gram_inertia_cases=4, matching_path_case=1,
         exact_farkas_case=1, exact_fractional_primal_case=1, sparse_zero_frequency_cases=2,
         strict_negative_cases=39, actual_producer_output_read=False)), 'CALIBRATION_SCOPE')
    need(calibration.get('source_sha256') == hashlib.sha256(SELF.read_bytes()).hexdigest()
         and calibration.get('spec_sha256') == hashlib.sha256(SPEC.read_bytes()).hexdigest(), 'CALIBRATION_SOURCE')
    need(type(calibration.get('inputs_sha256')) is dict and type(calibration.get('outputs_sha256')) is dict, 'CALIBRATION_MAPS')
    for mapping in [calibration['inputs_sha256'], calibration['outputs_sha256']]:
        for name, sha in mapping.items():
            pin(ROOT / name, sha)
    plan = read(args.producer_plan, args.producer_plan_sha256)
    manifest = read(args.supervision_out / 'manifest.json', args.supervisor_manifest_sha256)
    terminal = read(args.supervision_out / 'summary.json', args.supervisor_summary_sha256)
    need(type(plan.get('command')) is list and plan['command'].count('--') == 1, 'PRODUCER_PLAN_COMMAND')
    child = plan['command'][plan['command'].index('--') + 1:]
    need(same(child, plan.get('child_command')) and same(manifest.get('command'), child), 'PRODUCER_CHILD_COMMAND')
    need(manifest.get('source_sha256') == PINS['acceleration/run_compute_command.py'] and manifest.get('cwd') == str(ROOT), 'PRODUCER_SUPERVISOR_SOURCE')
    need(manifest.get('automatic_retry') is False and manifest.get('cumulative_across_commands') is False, 'PRODUCER_NO_RETRY')
    for option, field in [('--seconds', 'seconds'), ('--shutdown-reserve-seconds', 'shutdown_reserve_seconds')]:
        need(option in plan['command'] and type(manifest.get(field)) in (int, float)
             and manifest[field] == float(plan['command'][plan['command'].index(option) + 1]), 'PRODUCER_ALLOCATION')
    need('--out' in plan['command'] and plan['command'][plan['command'].index('--out') + 1]
         == args.supervision_out.resolve().relative_to(ROOT).as_posix(), 'PRODUCER_SUPERVISOR_OUTPUT')
    need(type(terminal.get('command_exit_code')) is int and terminal['command_exit_code'] == 0
         and terminal.get('error') is None and terminal.get('invocation_id') == manifest.get('invocation_id'), 'PRODUCER_TERMINAL')
    cleanup = terminal.get('cleanup')
    need(type(cleanup) is dict and cleanup.get('reaped') is True and cleanup.get('job_active_zero_observed') is True
         and type(cleanup.get('actual_exit_code')) is int and cleanup['actual_exit_code'] == 0
         and cleanup.get('cleanup_errors') == [], 'PRODUCER_CLEANUP')
    packet = args.producer_root.resolve()
    need(packet.is_relative_to(ROOT / 'acceleration/results') and packet.is_dir(), 'PRODUCER_NAMESPACE')
    report = read(packet / 'summary.json', args.producer_summary_sha256)
    expected_mode = 'calibrate' if args.mode == 'producer-controls' else 'seventeen-base'
    need(report.get('schema') == 'EXTERIOR_NEIGHBOR_MOMENT_PRODUCER_V1'
         and report.get('status') == 'CANDIDATE_FINITE_MOMENT_ARTIFACTS_PENDING_INDEPENDENT_CHECK'
         and report.get('producer') == '/root' and report.get('target_resolution') == 'NONE'
         and report.get('independent_approval') is False and report.get('mode') == expected_mode
         and report.get('cwd') == str(ROOT), 'PRODUCER_HEADER')
    need(PRODUCER in child and expected_mode in child and '--out' in child
         and child[child.index('--out') + 1] == packet.relative_to(ROOT).as_posix(), 'PRODUCER_CHILD_SCOPE')
    worker = child[child.index(PRODUCER):]
    need(type(report.get('command')) is list and report['command'][1:] == worker, 'PRODUCER_WORKER_COMMAND')
    software = {name: PINS[name] for name in [PRODUCER, PRODUCER.replace('.py', '_spec.md'),
                                            'acceleration/command_deadline.py', 'pyproject.toml', 'uv.lock']}
    need(same(report.get('inputs_sha256'), software), 'PRODUCER_SOFTWARE_MAP')
    for name, sha in software.items():
        pin(ROOT / name, sha)
    outputs = report.get('outputs_sha256')
    need(type(outputs) is dict and outputs, 'PRODUCER_OUTPUT_MAP')
    actual_files = {p.relative_to(ROOT).as_posix() for p in packet.rglob('*') if p.is_file() and p != packet / 'summary.json'}
    need(set(outputs) == actual_files, 'PRODUCER_FILE_POPULATION')
    for name, sha in outputs.items():
        path = (ROOT / name).resolve()
        need(path.is_relative_to(packet) and type(sha) is str and re.fullmatch('[0-9a-f]{64}', sha), 'PRODUCER_OUTPUT_IDENTITY')
        pin(path, sha)
    expected_files = {'controls.json'}
    cases = []
    for name, selected, wanted in PROFILES:
        h, _, _, _, _, exterior = rook_fixture(selected, deadline)
        need(exterior == wanted, 'INDEPENDENT_ROOK_PROFILE')
        cases.append(check_actual_case(packet / name, h, 9, 4, deadline, read, exterior))
        expected_files |= {name + '/' + suffix for suffix in ['model.json', 'types.json', 'universe.json', 'gram.json', 'primal.json']}
    controls = read(packet / 'controls.json')
    need(type(controls) is dict and set(controls) == {'rook_identity_entries', 'positive_moment_cases', 'gram_cases', 'strict_negative'}, 'AUTHOR_CONTROLS_FIELDS')
    need(type(controls['rook_identity_entries']) is int and controls['rook_identity_entries'] == 81
         and same(controls['positive_moment_cases'], [case['producer_case_result'] for case in cases]), 'AUTHOR_POSITIVE_COUNTS')
    literals = [([[1, 0], [0, 2]], False), ([[0, 1], [1, 0]], True), ([[1, 0], [0, -1]], True), ([[0, 0], [0, 0]], False)]
    need(type(controls['gram_cases']) is list and len(controls['gram_cases']) == 4, 'AUTHOR_GRAM_POPULATION')
    for row, (matrix, negative) in zip(controls['gram_cases'], literals):
        need(type(row) is dict and set(row) == {'matrix', 'expected_negative', 'observed'}
             and same(row['matrix'], matrix) and row['expected_negative'] is negative, 'AUTHOR_GRAM_LITERAL')
        check_gram(row['observed'], matrix, deadline)
    stages = [('bool_matrix', 'MATRIX_BINARY_INTEGER'), ('float_matrix', 'MATRIX_BINARY_INTEGER'),
              ('loop', 'MATRIX_DIAGONAL'), ('asymmetry', 'MATRIX_SYMMETRY'),
              ('negative_primal', 'PRIMAL_NONNEGATIVE'), ('altered_primal', 'PRIMAL_MOMENTS'),
              ('wrong_farkas_rhs', 'FARKAS_RHS_SIGN'), ('wrong_farkas_column', 'FARKAS_COLUMN_SIGN')]
    need(same(controls['strict_negative'], [dict(name=name, expected_stage=stage, actual_stage=stage) for name, stage in stages]), 'AUTHOR_PRECISE_STAGES')
    # Producer did not save damaged inputs for these eight calls. Reconstruct
    # their frozen literal counterparts and disclose that limited replay scope.
    tiny_model, tiny_columns, _ = rebuild([[0]], 9, 4, deadline)
    callbacks = [('H_BINARY_INTEGER', lambda: geometry([[False]], 9, 4)),
                 ('H_BINARY_INTEGER', lambda: geometry([[0.0]], 9, 4)),
                 ('H_DIAGONAL', lambda: geometry([[1]], 9, 4)),
                 ('H_SYMMETRY', lambda: geometry([[0, 1], [0, 0]], 9, 4)),
                 ('PRIMAL_NONNEGATIVE', lambda: check_primal(dict(status='CANDIDATE_EXACT_MOMENT_PRIMAL', values=['-1', '9'], integer=True), tiny_columns, tiny_model['right_hand_side'])),
                 ('PRIMAL_MOMENT', lambda: check_primal(dict(status='CANDIDATE_EXACT_MOMENT_PRIMAL', values=['4', '3'], integer=True), tiny_columns, tiny_model['right_hand_side'])),
                 ('FARKAS_RHS_SIGN', lambda: check_farkas(['1', '0'], tiny_columns, tiny_model['right_hand_side'])),
                 ('FARKAS_COLUMN_SIGN', lambda: check_farkas(['-1', '0'], tiny_columns, tiny_model['right_hand_side']))]
    counterpart_records = []
    for (name, author_stage), (wanted, call) in zip(stages, callbacks):
        actual = None
        try:
            call()
        except ValueError as error:
            actual = str(error)
        need(actual == wanted, 'AUTHOR_COUNTERPART:' + name)
        counterpart_records.append(dict(case=name, author_stage=author_stage, independent_stage=actual,
                                       damaged_input_saved_by_producer=False))
    need(same(report.get('controls'), dict(positive_moment_cases=5, gram_cases=4, strict_negative_cases=8)), 'AUTHOR_SUMMARY_COUNTS')
    science = None
    if args.mode == 'seventeen-base':
        note = pin(ROOT / 'docs/CANDIDATE_20261003_SEVENTEEN_POINT_EXTERNAL_NEIGHBOR_MOMENTS_V1.md').read_text(encoding='utf8')
        table = note.split('The particular base')[1].split('ROOT independently')[0]
        triples = [tuple(map(int, values)) for values in re.findall(r'\((\d+),(\d+),(\d+)\)', table)]
        need(len(triples) == 12, 'BASE_LITERAL_TRIPLES')
        edge_set = set()
        for triple in triples:
            need(len(set(triple)) == 3 and all(0 <= v < 17 for v in triple), 'BASE_TRIPLE_DOMAIN')
            for edge in itertools.combinations(sorted(triple), 2):
                need(edge not in edge_set, 'BASE_REPEATED_PAIR')
                edge_set.add(edge)
        h = [[int(u != v and tuple(sorted((u, v))) in edge_set) for v in range(17)] for u in range(17)]
        science = check_actual_case(packet / 'seventeen_base', h, 99, 14, deadline, read)
        expected_files |= {'seventeen_base/' + name for name in science['case_files']}
        need(same(report.get('scientific_result'), science['producer_case_result']), 'SCIENCE_SUMMARY_RESULT')
    else:
        need(report.get('scientific_result') is None, 'AUTHOR_NO_SCIENCE')
    relative_files = {p.relative_to(packet).as_posix() for p in packet.rglob('*') if p.is_file() and p != packet / 'summary.json'}
    need(relative_files == expected_files, 'EXACT_CASE_FILE_POPULATION')
    tick(deadline)
    return dict(complete_rook_profiles=5, complete_raw_gram_controls=4, exact_author_stage_records=8,
                reconstructed_negative_counterparts=counterpart_records, complete_output_files=len(outputs), science=science, graph_extension_claimed=False,
                scope='One exact induced adjacency only; no compatible-supergraph coverage or target result')


def check_actual_case(folder, h, n, k, deadline, read, exterior=None):
    model = read(folder / 'model.json')
    columns = read(folder / 'types.json')
    universe = read(folder / 'universe.json')
    expected, rebuilt = check_bundle(model, columns, universe, h, n, k, deadline)
    gram = read(folder / 'gram.json')
    gram_result = check_gram(gram, expected['gram_matrix'], deadline, rebuilt, expected['right_hand_side'])
    files = ['model.json', 'types.json', 'universe.json', 'gram.json']
    outcome = dict(name=folder.name, eligible_types=len(rebuilt), universe_masks=2 ** len(h), gram_status=gram['status'])
    primal_result = None
    if (folder / 'primal.json').exists():
        files.append('primal.json')
        primal = read(folder / 'primal.json')
        primal_result = check_primal(primal, rebuilt, expected['right_hand_side'])
        outcome['exact_primal_integer'] = primal_result['integer']
        if exterior is not None:
            check_literal_exterior_primal(primal, rebuilt, exterior)
    else:
        need(exterior is None, 'ROOK_PRIMAL_MISSING')
    if (folder / 'numerical_guidance.json').exists():
        files.append('numerical_guidance.json')
        guidance = read(folder / 'numerical_guidance.json')
        need(type(guidance) is dict and guidance.get('certificate') is False
             and type(guidance.get('status')) is int, 'NUMERICAL_GUIDANCE_NOT_CERTIFICATE')
        outcome['numerical_solver_status_not_a_proof'] = guidance['status']
    tick(deadline)
    return dict(producer_case_result=outcome, case_files=files, rows=len(expected['right_hand_side']),
                complete_induced_products=len(h) ** 2, eligible_types=len(rebuilt), full_mask_universe=2 ** len(h),
                exact_gram=gram_result, exact_primal=primal_result,
                exact_farkas_checked='farkas_vector' in gram, graph_extension_proved=False)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('mode', choices=['own-calibrate', 'producer-controls', 'seventeen-base'])
    p.add_argument('--seconds', type=float, required=True)
    p.add_argument('--out', type=Path, required=True)
    for name in ['producer-root', 'producer-plan', 'supervision-out', 'calibration']:
        p.add_argument('--' + name, type=Path)
        if name != 'producer-root':
            p.add_argument('--' + name + '-sha256')
    p.add_argument('--producer-summary-sha256')
    p.add_argument('--supervisor-manifest-sha256')
    p.add_argument('--supervisor-summary-sha256')
    args = p.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='Independent exact induced exterior moments; all input hashing/JSON/enumeration/rational arithmetic/output inside one invocation')
    out = args.out.resolve()
    need(out.is_relative_to(ROOT / 'acceleration/results') and not out.exists(), 'FRESH_OUTPUT')
    out.mkdir(parents=True)
    pins = {}
    def digest(path):
        tick(deadline)
        h = hashlib.sha256()
        with path.open('rb') as f:
            while block := f.read(1024 * 1024):
                h.update(block); tick(deadline)
        tick(deadline)
        return h.hexdigest()
    def pin(path, wanted=None):
        path = path.resolve()
        need(path.is_relative_to(ROOT) and path.is_file(), 'INPUT_PATH')
        name = path.relative_to(ROOT).as_posix()
        need(name != 'CLAIMS.yaml' and not name.startswith('.git/'), 'MUTABLE_INPUT')
        sha = digest(path)
        need(wanted is None or sha == wanted, 'INPUT_IDENTITY:' + name)
        need(name not in pins or pins[name] == sha, 'INPUT_CHANGED')
        pins[name] = sha
        return path
    def read(path, wanted=None):
        value = strict_json(pin(path, wanted).read_bytes()); tick(deadline)
        return value
    def save(name, value):
        tick(deadline)
        (out / name).write_text(json.dumps(value, allow_nan=False, indent=2) + '\n', encoding='utf8')
        tick(deadline)
    try:
        for name, sha in PINS.items():
            pin(ROOT / name, sha)
        pin(SELF); pin(SPEC)
        if args.mode == 'own-calibrate':
            need(all(getattr(args, name) is None for name in ['producer_root', 'producer_plan', 'supervision_out', 'calibration']), 'OWN_CAL_NO_PRODUCER')
            counts = own_calibration(out, deadline, save)
            status = 'INDEPENDENT_EXTERNAL_NEIGHBOR_MOMENTS_V1_OWN_CALIBRATION_PASS'
        else:
            counts = check_producer(args, deadline, read, pin)
            status = ('INDEPENDENT_EXTERNAL_NEIGHBOR_MOMENTS_V1_PRODUCER_CONTROLS_PASS'
                      if args.mode == 'producer-controls' else 'INDEPENDENT_EXTERNAL_NEIGHBOR_MOMENTS_V1_COMPLETE_PASS')
        for name, sha in list(pins.items()):
            pin(ROOT / name, sha)
        output_hashes = {x.relative_to(ROOT).as_posix(): digest(x) for x in sorted(out.iterdir()) if x.is_file()}
        save('summary.json', dict(status=status, producer='/root', verifier='/root/native_driver', method='independent_artifact_check',
             target_resolution='NONE', timestamp=datetime.now(timezone.utc).isoformat(), command=[sys.executable, *sys.argv],
             source_sha256=pins[SELF.relative_to(ROOT).as_posix()], spec_sha256=pins[SPEC.relative_to(ROOT).as_posix()],
             inputs_sha256=pins, outputs_sha256=output_hashes, checked_scope=counts, independent_producer_imports=0,
             checker_implementation_version=3,
             graph_completion_claimed=False, combined_added_edges_checked=False, floating_status_is_proof=False,
             deadline=deadline.status()))
        tick(deadline)
        return 0
    except BaseException as error:
        if (out / 'summary.json').exists():
            (out / 'summary.json').rename(out / 'summary.not_approved.json')
        (out / 'failure.json').write_text(json.dumps(dict(error=repr(error), inputs_sha256=pins,
            deadline=deadline.status(), automatic_retry=False, outputs_preserved=True, target_resolution='NONE')) + '\n', encoding='utf8')
        raise


if __name__ == '__main__':
    raise SystemExit(main())
