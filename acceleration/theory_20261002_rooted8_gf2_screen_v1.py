"""Exact GF2 necessary-integrality screen for every frozen210 local profile.

Sparse raw rows are encoded in Python integer bitsets. Any zero-left-side
relation retains a complete original-row XOR witness, replayable independently.
No floating arithmetic, LP status, target symmetry or graph feasibility claim.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import gzip
import json
from pathlib import Path
import subprocess
import sys
import time

from tqdm import tqdm
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT/'acceleration/results/20261002_rooted8_universal5_product_model02/model.json'
MODEL_SHA = 'a2162b5edc4eb68952cc9887156c5d0cd731aaaf9a6b5f94f446174b9d10528b'


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


def ordinary_replay(rows, columns, indices, expected_rhs):
    """Complete scalar coefficient sums, without packed-bitset encoding."""
    products=[0]*columns;parameters=[0]*3
    for i in indices:
        for j,coefficient in rows[i]['terms']:
            products[j]=(products[j]+coefficient)%2
        for j,coefficient in enumerate(rows[i]['rhs_affine']):
            parameters[j]=(parameters[j]+coefficient)%2
    return not any(products) and parameters==expected_rhs


def certificates(rows, columns, deadline, checkpoint=None):
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
                need(ordinary_replay(rows,columns,indices,[rhs>>j&1 for j in range(3)]),
                     'complete independent-arithmetic scalar original-row parity replay')
                relations[rhs] = dict(rhs_affine_mod2=[rhs >> j & 1 for j in range(3)],
                    xor_original_row_indices=indices, reduced_left_all_zero=True)
        if not i % 256:
            if deadline.status()['remaining_seconds'] < 30 or deadline.status()['stop_required']:
                if checkpoint is not None:
                    value=dict(format='ROOTED8_GF2_ELIMINATION_STOP_CHECKPOINT_V1',processed_rows=i+1,
                               matrix_rows=len(rows),matrix_columns=columns,model_sha256=MODEL_SHA,
                               source_sha256=sha(Path(__file__)),
                               pivots=[[j,hex(bits),hex(witness)] for j,(bits,witness) in sorted(pivots.items())],
                               relations={str(rhs):record for rhs,record in relations.items()},
                               partial_only=True,automatic_resume=False,
                               restart='Resume support requires unchanged source/model and independent replay of saved pivots; no complete reduction asserted.')
                    with gzip.open(checkpoint,'xt',encoding='utf8') as stream:
                        json.dump(value,stream);stream.write('\n')
                raise TimeoutError('not completed within the allocated budget; exact processed-prefix checkpoint preserved')
    return len(pivots), list(relations.values())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--seconds', type=float, required=True)
    parser.add_argument('--controls-only', action='store_true')
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='85874 sparse GF2 rows23019columns Python bitsets and210points; original-row XOR witnesses,30-second partial-checkpoint reserve.')
    out = args.out.resolve(); out.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    try:
        need(sha(MODEL) == MODEL_SHA, 'exact frozen root8 conditional model')
        manifest = dict(timestamp=datetime.now(timezone.utc).isoformat(), source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
            command=[sys.executable, *sys.argv], cwd=str(ROOT), inputs_sha256={MODEL.relative_to(ROOT).as_posix():MODEL_SHA, Path(__file__).relative_to(ROOT).as_posix():sha(Path(__file__))},
            selection='All210 profiles a0..20,b0..9, no omissions.', scope='Conditional prismfree rooted8 integercount model; complete model necessity pending independent audit.',
            success_criterion='Complete GF2reduction with exact originalrow XOR certificates for all nonzero reduced parameter relations; evaluateall210.',
            falsification_criterion='Any raw column parity orRHS mismatch, missed selectedcase or badcontrol vetoes result.',
            independent_verification_requirement='Separate implementation replays every rawXOR witness and modelderivation/coverage before promotion.')
        save(out/'manifest.json', manifest)
        positive = [dict(terms=[[0,1],[1,1]], rhs_affine=[1,0,0]), dict(terms=[[0,1],[1,1]], rhs_affine=[1,0,0])]
        need(certificates(positive, 2, deadline)[1] == [], 'consistent positive paritycontrol')
        negative = [positive[0], dict(terms=[[0,1],[1,1]], rhs_affine=[0,0,0])]
        _, control = certificates(negative, 2, deadline)
        need(len(control) == 1 and control[0]['rhs_affine_mod2'] == [1,0,0] and control[0]['xor_original_row_indices'] == [0,1], 'inconsistent exact paritycontrol')
        need(ordinary_replay(negative,2,[0,1],[1,0,0]),'complete ordinary replay positivecontrol')
        need(not ordinary_replay(negative,2,[0],[1,0,0]),'changed witness rejected')
        need(not ordinary_replay(negative,2,[0,1],[0,0,0]),'changed RHS certificate rejected')
        corrupt=[negative[0],dict(terms=[[0,2],[1,1]],rhs_affine=[0,0,0])]
        need(not ordinary_replay(corrupt,2,[0,1],[1,0,0]),'changed raw coefficient rejected')
        save(out/'controls.json',dict(consistent_and_inconsistent_controls_pass=True,changed_witness_rejected=True,
                                     changed_rhs_rejected=True,changed_raw_coefficient_rejected=True,
                                     scalar_original_row_replay=True,controls_only=args.controls_only))
        if args.controls_only:
            save(out/'summary.json',dict(status='ROOTED8_GF2_CONTROLS_PASS',elapsed_seconds=time.monotonic()-start,
                                        source_sha256=sha(Path(__file__)),model_sha256=MODEL_SHA,
                                        mathematical_scope='Engineering controls only; complete target/model reduction not executed.'))
            return
        model = json.loads(MODEL.read_bytes()); rows=model['equations']; columns=len(model['variables'])
        rank, relations = certificates(rows, columns, deadline,out/'stopped_elimination_checkpoint.json.gz')
        save(out/'gf2_relations.json', relations)
        outcomes = []
        for a in range(21):
            for b in range(10):
                violated = [j for j, relation in enumerate(relations)
                    if sum(value*coefficient for value, coefficient in zip([1,a,b], relation['rhs_affine_mod2'])) % 2]
                outcomes.append(dict(parameters=[a,b], outcome='REJECTED_NECESSARY_INTEGER_EXTENSION' if violated else 'SURVIVES_GF2',
                    first_violated_certificate=None if not violated else violated[0]))
        save(out/'all210_outcomes.json', outcomes)
        summary = dict(status='CANDIDATE_EXACT_ROOTED8_GF2_SCREEN', timestamp=datetime.now(timezone.utc).isoformat(),
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
