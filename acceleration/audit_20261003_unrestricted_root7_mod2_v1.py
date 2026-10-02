"""Independent literal content and scalar-certificate checker; no producer imports.

Verifier /root. Reuses only Python, the pinned deadline and supported containment.
No elimination/rank algorithm is shared with the discovery path.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import sys
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
MODEL = 'acceleration/results/20261002_rooted7_unrestricted_extension01/model.json'
MODEL_SHA = '9f636889690071f69ad7a103b02abb2f43a5bbc2d2114c87a779da29c0f647a1'


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def write(path, value):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n')


def reconstruct(raw, width):
    answer = []
    for index, equation in enumerate(raw):
        column_values = [0] * width
        for column, coefficient in equation['terms']:
            require(type(column) is int and 0 <= column < width and type(coefficient) is int, 'strict integer sparse term')
            column_values[column] += coefficient
        rhs = equation['rhs_affine']
        require(len(rhs) == 4 and all(type(value) is int for value in rhs), 'exact four affine RHS components')
        content = 0
        for value in column_values + rhs:
            content = math.gcd(content, value)
        content = abs(content) or 1
        terms = [[column, value // content] for column, value in enumerate(column_values) if value]
        answer.append(dict(original_row=index, positive_integer_content=content, terms=terms, rhs_affine=[value // content for value in rhs]))
    return answer


def check_primal(rows, width, vector, affine):
    require(type(vector) is list and len(vector) == width and all(type(value) is int and value in (0, 1) for value in vector), 'complete strict binary vector')
    require(len(affine) == 4 and all(type(value) is int for value in affine), 'four exact combination coefficients')
    for row in rows:
        lhs = sum(coefficient * vector[column] for column, coefficient in row['terms'])
        rhs = sum(coefficient * value for coefficient, value in zip(affine, row['rhs_affine']))
        require((lhs - rhs) % 2 == 0, 'literal scalar row residual')


def check_relation(rows, width, record):
    chosen = record['original_row_indices']
    require(type(chosen) is list and chosen == sorted(set(chosen)) and len(chosen) > 0 and all(type(value) is int and 0 <= value < len(rows) for value in chosen), 'complete ordered distinct row relation')
    residues = [0] * width
    rhs = [0] * 4
    for index in chosen:
        for column, coefficient in rows[index]['terms']:
            residues[column] += coefficient
        for component in range(4):
            rhs[component] += rows[index]['rhs_affine'][component]
    require(all(value % 2 == 0 for value in residues), 'every literal column cancels')
    result = [value % 2 for value in rhs]
    require(type(record['rhs_affine_residue']) is list and len(record['rhs_affine_residue']) == 4 and all(type(value) is int and value in (0, 1) for value in record['rhs_affine_residue']), 'strict affine residue')
    require(result == record['rhs_affine_residue'] and any(result), 'exact nonzero affine relation')
    return result


def controls():
    positives = negatives = 0
    raw = [dict(terms=[[0, 1], [0, 1], [1, 0]], rhs_affine=[2, 0, 0, 0])]
    rows = reconstruct(raw, 2)
    require(rows == [dict(original_row=0, positive_integer_content=2, terms=[[0, 1]], rhs_affine=[1, 0, 0, 0])], 'positive content control')
    check_primal(rows, 2, [1, 0], [1, 0, 0, 0]); positives += 2
    contradictory = reconstruct([dict(terms=[[0, 1]], rhs_affine=[0, 0, 0, 0]), dict(terms=[[0, 1]], rhs_affine=[1, 0, 0, 0])], 2)
    relation = dict(original_row_indices=[0, 1], rhs_affine_residue=[1, 0, 0, 0])
    check_relation(contradictory, 2, relation); positives += 1
    for vector in ([0, 0], [True, 0], [1], [1, 0, 0], [2, 0]):
        try:
            check_primal(rows, 2, vector, [1, 0, 0, 0])
        except ValueError:
            negatives += 1
        else:
            raise ValueError('corrupt primal accepted')
    for indices, rhs in (([0], [1, 0, 0, 0]), ([0, 0, 1], [1, 0, 0, 0]), ([1, 0], [1, 0, 0, 0]), ([0, 2], [1, 0, 0, 0]), ([0, 1], [0, 0, 0, 0]), ([0, 1], [True, 0, 0, 0])):
        try:
            check_relation(contradictory, 2, dict(original_row_indices=indices, rhs_affine_residue=rhs))
        except ValueError:
            negatives += 1
        else:
            raise ValueError('corrupt relation accepted')
    for field, bad in (('positive_integer_content', 1), ('original_row', 1), ('terms', [[0, 2]]), ('rhs_affine', [0, 0, 0, 0])):
        changed = json.loads(json.dumps(rows)); changed[0][field] = bad
        require(changed != reconstruct(raw, 2), 'corrupt normalization differs'); negatives += 1
    return dict(positive_controls=positives, strict_negative_controls=negatives, checking_path='Dense integer accumulation/content reconstruction plus literal scalar row/column sums; no producer imports, bitset reduction or elimination.', full_producer_output_inspected=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--seconds', type=float, required=True)
    parser.add_argument('--calibrate', action='store_true')
    parser.add_argument('--run', type=Path)
    parser.add_argument('--calibration', type=Path)
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='Independent raw content and complete scalar certificates of small11769row/2810column unrestricted operator; no rank or graph assertion')
    out = args.out.resolve(); require(out.is_relative_to(ROOT), 'bounded output'); out.mkdir(parents=True, exist_ok=False)
    pins = {Path(__file__).relative_to(ROOT).as_posix(): digest(Path(__file__)), 'acceleration/command_deadline.py': digest(ROOT / 'acceleration/command_deadline.py'), 'uv.lock': digest(ROOT / 'uv.lock')}
    calibrated = controls()
    if args.calibrate:
        write(out / 'summary.json', dict(status='INDEPENDENT_UNRESTRICTED_ROOT7_MOD2_CHECKER_V1_CALIBRATION_PASS', verifier='/root', timestamp=datetime.now(timezone.utc).isoformat(), inputs_sha256=pins, **calibrated)); return
    require(args.run is not None and args.calibration is not None, 'explicit raw run and pre-output calibration')
    calibration = json.loads(args.calibration.read_bytes())
    require(calibration['status'] == 'INDEPENDENT_UNRESTRICTED_ROOT7_MOD2_CHECKER_V1_CALIBRATION_PASS' and calibration['inputs_sha256'][Path(__file__).relative_to(ROOT).as_posix()] == digest(Path(__file__)), 'same calibrated source')
    require(digest(ROOT / MODEL) == MODEL_SHA, 'frozen independently necessary raw operator')
    model = json.loads((ROOT / MODEL).read_bytes()); width = len(model['variables'])
    require(width == 2810 and len(model['equations']) == 11769, 'complete dimensions')
    rows = reconstruct(model['equations'], width)
    normalized_path = args.run / 'normalized_literal_rows.jsonl'
    normalized = [json.loads(line) for line in normalized_path.read_text(encoding='utf8').splitlines()]
    for row in normalized:
        require(type(row['original_row']) is int and type(row['positive_integer_content']) is int and row['positive_integer_content'] > 0, 'strict normalization indices/content')
        require(all(type(column) is int and type(value) is int for column, value in row['terms']) and all(type(value) is int for value in row['rhs_affine']), 'strict normalized integer fields')
    require(normalized == rows, 'all original-row contents, combined coefficients and four RHS reconstructed')
    summary = json.loads((args.run / 'summary.json').read_bytes())
    require(summary['normalized_literal_sha256'] == digest(normalized_path), 'raw normalized rows pin')
    checked = row_checks = column_checks = 0
    residues = []
    for entry in summary['nonzero_affine_relation_certificates']:
        path = args.run / entry['path']; require(digest(path) == entry['sha256'], 'literal relation pin')
        record = json.loads(path.read_bytes()); require(record['normalized_literal_sha256'] == digest(normalized_path) and record['columns'] == width and record['rows'] == len(rows), 'relation full scope')
        residue = check_relation(rows, width, record)
        require(entry['rhs_affine_residue'] == residue, 'summary and raw relation agree')
        residues.append(residue); column_checks += width
        pins[path.relative_to(ROOT).as_posix()] = digest(path)
    primals = {}
    for entry in summary['complete_component_primals']:
        path = args.run / entry['path']; require(digest(path) == entry['sha256'], 'literal primal pin')
        lines = path.read_text(encoding='ascii').splitlines(); label = entry['component']
        require(lines[:2] == ['UNRESTRICTED_ROOTED7_GF2_PRIMAL_V1', str(width) + ' ' + label] and len(lines) == 3 and len(lines[2]) == width and set(lines[2]) <= {'0', '1'}, 'complete original binary object')
        affine = [int(component == label) for component in ('const', 'c', 'a', 'b')]
        check_primal(rows, width, [int(value) for value in lines[2]], affine); primals[label] = True; row_checks += len(rows)
        if label == 'const':
            active_column = next(column for row in rows for column, value in row['terms'] if value % 2)
            corrupt = [int(value) for value in lines[2]]; corrupt[active_column] ^= 1
            try:
                check_primal(rows, width, corrupt, affine)
            except ValueError:
                calibrated['strict_negative_controls'] += 1
            else:
                raise ValueError('actual full-width active-coordinate corruption accepted')
        pins[path.relative_to(ROOT).as_posix()] = digest(path)
    if not residues:
        require(primals == {label: True for label in ('const', 'c', 'a', 'b')}, 'all four RHS primals')
    outcomes = json.loads((args.run / 'all651_outcomes.json').read_bytes())
    points = [[c, a, b] for c in range(3) for a in range(21) for b in range((18 + c) // 2 + 1)]
    require([entry['parameters'] for entry in outcomes] == points, 'complete exact651population')
    excluded = 0
    for entry, point in zip(outcomes, points):
        failures = [index for index, residue in enumerate(residues) if sum(value * coefficient for value, coefficient in zip([1, *point], residue)) % 2]
        if failures:
            require(entry['status'] == 'CANDIDATE_EXACT_INTEGER_NECESSARY_PROFILE_EXCLUSION' and entry['first_relation'] == failures[0], 'exact exclusion binding'); excluded += 1
        else:
            require(entry['status'] == 'CANDIDATE_LITERAL_MOD2_COMPATIBLE', 'exact compatible profile')
            if residues:
                path = args.run / entry['certificate']; lines = path.read_text(encoding='ascii').splitlines()
                require(len(lines) == 3 and lines[0] == 'UNRESTRICTED_ROOTED7_GF2_PRIMAL_V1' and len(lines[2]) == width and set(lines[2]) <= {'0', '1'}, 'complete parity primal')
                check_primal(rows, width, [int(value) for value in lines[2]], [1, *point]); row_checks += len(rows)
                pins[path.relative_to(ROOT).as_posix()] = digest(path)
        checked += 1
        require(not deadline.status()['stop_required'], 'allocated check unfinished')
    require(summary['excluded_profiles'] == excluded and summary['compatible_profiles'] == 651 - excluded and summary['rank_asserted'] is False, 'reported exact scope/counts')
    for path in [ROOT / MODEL, args.run / 'summary.json', args.run / 'all651_outcomes.json', normalized_path, args.calibration]:
        pins[path.resolve().relative_to(ROOT).as_posix()] = digest(path)
    write(out / 'summary.json', dict(status='INDEPENDENT_UNRESTRICTED_ROOT7_CONTENT_DIVIDED_MOD2_LITERAL_CHECK_V1_PASS', verifier='/root', producer='/root/structural', timestamp=datetime.now(timezone.utc).isoformat(), command=[sys.executable, *sys.argv], cwd=str(ROOT), inputs_sha256=pins, normalization_rows_checked=len(rows), complete_scalar_primal_row_checks=row_checks, complete_scalar_relation_column_checks=column_checks, profile_population=checked, excluded_profiles=excluded, compatible_profiles=checked-excluded, rank_asserted=False, target_resolution='NONE', shared_components=['Python exact integer runtime, pinned command_deadline/supervisor; prior independent necessity of raw model reused without rederivation.'], limitations=['Modular consistency does not establish nonnegative integer feasibility or graph realization.', 'No elimination or rank reproduced; only full explicit certificate/scalar scope checked.'], deadline=deadline.status(), **{key: value for key, value in calibrated.items() if key != 'full_producer_output_inspected'}))


if __name__ == '__main__':
    main()
