"""Exact GF2 necessary-integrality screen for every frozen210 local profile.

Sparse raw rows are encoded in Python integer bitsets. Any zero-left-side
relation retains a complete original-row XOR witness, replayable independently.
No floating arithmetic, LP status, target symmetry or graph feasibility claim.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

from tqdm import tqdm
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT/'acceleration/results/20261002_rooted7_extension_model/model.json'
MODEL_SHA = '21eb899c3606727ef4e452d518316957cf9eb76e5e85c5a79af82421f4004595'


def need(value, reason):
    if not value:
        raise ValueError(reason)


def save(path, value):
    with Path(path).open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, indent=2); stream.write('\n')


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def encode(row, columns):
    bits = 0
    for j, coefficient in row['terms']:
        if coefficient % 2:
            bits ^= 1 << j
    for j, coefficient in enumerate(row['rhs_affine']):
        if coefficient % 2:
            bits ^= 1 << (columns+j)
    return bits


def certificates(rows, columns, deadline):
    pivots, relations = {}, {}
    left_mask = (1 << columns)-1
    for i, row in enumerate(tqdm(rows, desc='complete GF2 row reduction', mininterval=5)):
        bits, witness = encode(row, columns), 1 << i
        while bits & left_mask:
            first = (bits & left_mask)&-(bits & left_mask)
            pivot = first.bit_length()-1
            if pivot not in pivots:
                pivots[pivot] = (bits, witness)
                break
            old_bits, old_witness = pivots[pivot]
            bits ^= old_bits; witness ^= old_witness
        else:
            rhs = bits >> columns
            if rhs and rhs not in relations:
                indices = [j for j in range(len(rows)) if witness >> j & 1]
                exact = 0
                for j in indices:
                    exact ^= encode(rows[j], columns)
                need(exact == bits and not exact & left_mask, 'all raw parity certificate columns')
                relations[rhs] = dict(rhs_affine_mod2=[rhs >> j & 1 for j in range(3)],
                    xor_original_row_indices=indices, reduced_left_all_zero=True)
        if not i % 256:
            need(not deadline.status()['stop_required'], 'not completed within the allocated budget')
    return len(pivots), list(relations.values())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--seconds', type=float, required=True)
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='11749 sparseGF2rows2766columns Pythonbitsets and210points; smallexactcomputation withcompleteXORcertificates.')
    out = args.out.resolve(); out.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    try:
        need(sha(MODEL) == MODEL_SHA, 'exact frozenroot7necessary model')
        manifest = dict(timestamp=datetime.now(timezone.utc).isoformat(), source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            command=[sys.executable, *sys.argv], cwd=str(ROOT), inputs_sha256={MODEL.relative_to(ROOT).as_posix():MODEL_SHA, Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
            selection='All210 profiles a0..20,b0..9, no omissions.', scope='Conditional prismfree rooted7 integercount necessary model.',
            success_criterion='Complete GF2reduction with exact originalrow XOR certificates for all nonzero reduced parameter relations; evaluateall210.',
            falsification_criterion='Any raw column parity orRHS mismatch, missed selectedcase or badcontrol vetoes result.',
            independent_verification_requirement='Separate implementation replays every rawXOR witness and modelderivation/coverage before promotion.')
        save(out/'manifest.json', manifest)
        positive = [dict(terms=[[0,1],[1,1]], rhs_affine=[1,0,0]), dict(terms=[[0,1],[1,1]], rhs_affine=[1,0,0])]
        need(certificates(positive, 2, deadline)[1] == [], 'consistent positive paritycontrol')
        negative = [positive[0], dict(terms=[[0,1],[1,1]], rhs_affine=[0,0,0])]
        _, control = certificates(negative, 2, deadline)
        need(len(control) == 1 and control[0]['rhs_affine_mod2'] == [1,0,0] and control[0]['xor_original_row_indices'] == [0,1], 'inconsistent exact paritycontrol')
        model = json.loads(MODEL.read_bytes()); rows=model['equations']; columns=len(model['variables'])
        rank, relations = certificates(rows, columns, deadline)
        save(out/'gf2_relations.json', relations)
        outcomes = []
        for a in range(21):
            for b in range(10):
                violated = [j for j, relation in enumerate(relations)
                    if sum(value*coefficient for value, coefficient in zip([1,a,b], relation['rhs_affine_mod2'])) % 2]
                outcomes.append(dict(parameters=[a,b], outcome='REJECTED_NECESSARY_INTEGER_EXTENSION' if violated else 'SURVIVES_GF2',
                    first_violated_certificate=None if not violated else violated[0]))
        save(out/'all210_outcomes.json', outcomes)
        summary = dict(status='CANDIDATE_EXACT_ROOTED7_GF2_SCREEN', timestamp=datetime.now(timezone.utc).isoformat(),
            matrix_columns=columns, matrix_rows=len(rows), exact_gf2_rank=rank,
            distinct_nonzero_affine_relations=len(relations), selected=210, completed=210,
            rejected=sum(row['outcome'] != 'SURVIVES_GF2' for row in outcomes),
            survivors=sum(row['outcome'] == 'SURVIVES_GF2' for row in outcomes),
            target_resolution='UNKNOWN', independent_review=None, independent_review_reason='Raw certificates and freshmodelcoverage pending separate audit.',
            limitations=['Conditional necessary integer extension only; surviving parity classes are not graph feasibility.', 'Finite XOR witnesses require independent replay and modelcoverage/derivation check before any exclusion.'],
            elapsed_seconds=time.monotonic()-start,
            outputs_sha256={path.relative_to(ROOT).as_posix():sha(path) for path in out.iterdir() if path.is_file()})
        save(out/'summary.json', summary); print(json.dumps(summary), flush=True)
    except BaseException as error:
        save(out/'failure.json', dict(error=repr(error), elapsed_seconds=time.monotonic()-start, target_resolution='UNKNOWN')); raise


if __name__ == '__main__':
    main()
