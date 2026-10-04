"""SOURCE ONLY author helpers; no target archive, native call, graph conversion or search.

These same-author tests are calibration evidence only. A separate checker and
ROOT review remain mandatory for the changed scientific wrapper and outputs.
"""
import argparse
import copy
import hashlib
import importlib.util
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'acceleration/prepare_20261003_ternary_mixed_science_v2.py'
SOURCE_SHA = '6e29380cc08766264f4697e175f387443e658010af0fbeb2b49911b1349a7b19'
SPEC = 'acceleration/prepare_20261003_ternary_mixed_science_v2_spec.md'
SPEC_SHA = '491cee55730ca34f1c1c304f7f6128f37d2164bd9a49a3f9deb48f8168b7c3fb'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    with path.open('x', encoding='utf8', newline='\n') as handle:
        json.dump(value, handle, indent=2, allow_nan=False)
        handle.write('\n')


def scalar(rows, n, degree):
    matrix = [[0]*n for _ in range(n)]
    for a, b, c in rows:
        for i, j in [(a, b), (a, c), (b, c)]:
            matrix[i][j] = matrix[j][i] = 1
    residues = [0, 0, 0]
    lam = mu = f3 = 0
    for i in range(n):
        for j in range(i+1, n):
            common = sum(matrix[i][k]*matrix[j][k] for k in range(n))
            residual = common + matrix[i][j] - 2
            residues[residual % 3] += 1
            f3 += int(residual % 3 != 0)
            if matrix[i][j]:
                lam += residual**2
            else:
                mu += residual**2
    weight = {(9, 2): 577, (12, 2): 1057, (99, 7): 819820}[(n, degree)]
    raw = (str(n)+'\n'+''.join(''.join(map(str, row))+'\n' for row in matrix)).encode('ascii')
    return raw, dict(F3=f3, E_lambda=lam, E_mu=mu, E=lam+mu, scalar_weight=weight,
                    scalar=weight*f3+lam+mu, residue_population=residues)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seconds', type=float, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='One small author helper calibration with explicit scalar integer oracle; three generic/explicit initializer fixtures, no historical target input, subprocess or search')
    out = args.out.resolve()
    assert out.is_relative_to(ROOT) and not out.exists()
    out.mkdir(parents=True)
    pins = {SOURCE: SOURCE_SHA, SPEC: SPEC_SHA}
    positives = []
    negatives = []
    try:
        for name, identity in pins.items():
            assert digest(ROOT/name) == identity, 'Frozen source identity'
        loader = importlib.util.spec_from_file_location('mixed_science_exact_v2', ROOT/SOURCE)
        module = importlib.util.module_from_spec(loader)
        loader.loader.exec_module(module)
        rook = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8]]
        cube = [[0,1,2],[0,3,4],[1,5,6],[3,5,7],[2,8,9],[4,8,10],[6,9,11],[7,10,11]]
        target = [[x,x+33,x+66] for x in range(33)]
        target += [[x,(x+1)%99,(x+4)%99] for x in range(99)]
        target += [[x,(x+7)%99,(x+18)%99] for x in range(99)]
        fixtures = [('rook9', rook, 9, 2), ('cube12', cube, 12, 2), ('cyclic99_initializer', target, 99, 7)]
        for label, rows, n, degree in fixtures:
            assert deadline.status()['remaining_seconds'] > 10
            raw, expected = scalar(rows, n, degree)
            actual_raw, actual = module.graph(copy.deepcopy(rows), n, degree)
            assert actual_raw == raw and actual == expected, 'Complete scalar/matrix disagreement'
            matrix_sha = hashlib.sha256(raw).hexdigest()
            expected_wire = (f'TERNARY_LINEAR_GRAPH_INPUT_V1\nn {n}\ndegree {degree}\nsource_graph_sha256 {matrix_sha}\ntriples {len(rows)}\n'
                             + ''.join(' '.join(map(str, row))+'\n' for row in rows)+'END\n').encode('ascii')
            assert module.wire(rows, n, degree, matrix_sha) == expected_wire
            (out/(label+'.adj')).write_bytes(raw)
            (out/(label+'.wire')).write_bytes(expected_wire)
            save(out/(label+'.triples.json'), dict(n=n, point_degree=degree, ordered_triples=rows))
            positives.append(dict(label=label, integer_matrix_entries=n*n, pair_scores=n*(n-1)//2,
                                  metrics=actual, exact_wire_match=True, same_author_oracle=True))
        assert positives[0]['metrics']['F3'] == 0 and positives[0]['metrics']['E'] == 0, 'Known rook identity'
        assert positives[2]['metrics']['scalar_weight'] == 819820
        assert 99*98//2*14**2+1 == 950797 and 950797 != 819820, 'Preserved V1 static counterexample'

        def reject(label, expected, callback, artifact=None):
            observed = None
            try:
                callback()
            except ValueError as error:
                observed = str(error)
            assert observed == expected, (label, expected, observed)
            if artifact is not None:
                save(out/(label+'.json'), artifact)
            negatives.append(dict(label=label, expected_stage=expected, actual_stage=observed))

        for label, n, degree in [('bool_n', True, 2), ('float_n', 9.0, 2), ('negative_n', -9, 2),
                                 ('bool_degree', 9, True), ('float_degree', 9, 2.0), ('wrong_degree', 9, 3)]:
            reject(label, 'DOMAIN', lambda n=n, degree=degree: module.graph(rook, n, degree))
        for label, rows, stage in [('not_list', tuple(rook), 'TRIPLE_COUNT'),
                                   ('short_rows', rook[:-1], 'TRIPLE_COUNT'),
                                   ('extra_rows', rook+[[0,1,2]], 'TRIPLE_COUNT')]:
            reject(label, stage, lambda rows=rows: module.graph(rows, 9, 2))
        for label, value in [('boolean_zero', False), ('boolean_one', True), ('float_zero', 0.0),
                             ('float_one', 1.0), ('negative_point', -1), ('point_range', 9), ('string_point', '0')]:
            rows = copy.deepcopy(rook)
            rows[0][0] = value
            reject(label, 'TRIPLE_TYPE', lambda rows=rows: module.graph(rows, 9, 2), dict(ordered_triples=rows))
        for label, mutation, stage in [('short_triple', lambda rows: rows[0].pop(), 'TRIPLE_TYPE'),
                                        ('repeated_point', lambda rows: rows[0].__setitem__(1,0), 'TRIPLE_DISTINCT'),
                                        ('repeated_triple', lambda rows: rows.__setitem__(1,rows[0][:]), 'TRIPLE_DUPLICATE'),
                                        ('repeated_pair', lambda rows: rows.__setitem__(1,[0,1,3]), 'LINEARITY'),
                                        ('degree_damaged', lambda rows: rows.__setitem__(5,[2,5,7]), 'DEGREE')]:
            rows = copy.deepcopy(rook)
            mutation(rows)
            reject(label, stage, lambda rows=rows: module.graph(rows,9,2), dict(ordered_triples=rows))
        for label, value in [('hash_short', '0'*63), ('hash_upper', 'A'*64), ('hash_invalid', 'z'*64),
                             ('hash_boolean', True), ('hash_integer', 0)]:
            reject(label, 'GRAPH_HASH', lambda value=value: module.wire(rook,9,2,value))
        for label, raw, stage in [('json_duplicate', b'{"x":1,"x":2}', 'JSON_DUPLICATE'),
                                  ('json_nan', b'{"x":NaN}', 'JSON_NONFINITE'),
                                  ('json_infinity', b'{"x":Infinity}', 'JSON_NONFINITE')]:
            path = out/(label+'.raw')
            path.write_bytes(raw)
            reject(label, stage, lambda path=path: module.strict_json(path))
        save(out/'summary.json', dict(status='AUTHOR_TERNARY_MIXED_SCIENCE_V2_HELPERS_PENDING_INDEPENDENT_CHECK',
            timestamp=datetime.now(timezone.utc).isoformat(), producer='/root/native_driver',
            command=[sys.executable,*sys.argv], cwd=str(ROOT), python=platform.python_version(), inputs_sha256=pins,
            positives=positives, negative_records=negatives, positive_count=len(positives), strict_negative_count=len(negatives),
            target_weight_counterexample=950797, correct_target_weight=819820,
            actual_saved_target_input_read=False, native_calls=0, graph_projection_launched=False,
            scientific_launched=False, independent_approval=False, target_resolution='NONE',
            limitations=['Same-author dense scalar oracle and tests only; not independent mathematical checking.',
                        'Gate framing/containment/native execution are not exercised by these pure helper controls.',
                        'Explicit cyclic99 initializer is a fixture, not an SRG candidate or saved historical graph.'], deadline=deadline.status()))
    except BaseException as error:
        save(out/'failure.json', dict(error=repr(error), completed_positives=positives, completed_negatives=negatives,
            deadline=deadline.status(), independent_approval=False, native_calls=0, scientific_launched=False))
        raise


if __name__ == '__main__':
    main()
