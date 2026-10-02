"""Independent complete exact checker for the rejected codomain-isotropy step."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / 'docs/AUDIT_20261003_REJECTED_INCIDENCE_RANK_V1.md'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def rank(rows):
    pivots = {}
    for initial in rows:
        value = initial
        while value:
            bit = value.bit_length() - 1
            if bit not in pivots:
                pivots[bit] = value
                break
            value ^= pivots[bit]
    return len(pivots)


def transpose(rows, columns):
    return [sum(((row >> j) & 1) << i for i, row in enumerate(rows))
            for j in range(columns)]


def multiply(left, right, columns):
    right_columns = transpose(right, columns)
    return [sum(((row & col).bit_count() & 1) << j
                for j, col in enumerate(right_columns)) for row in left]


def gram(rows):
    return [sum(((a & b).bit_count() & 1) << j for j, b in enumerate(rows))
            for a in rows]


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + '\n', encoding='utf8')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--seconds', type=float, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='Exact99x231 generic projection/factor counterexample; independent scalarGF2 matrix products and elimination,30outer20worker10reserve')
    started = time.monotonic()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    try:
        identity = [1 << i for i in range(99)]
        projection = []
        for i in range(99):
            if i >= 81:
                projection.append(0)
            else:
                block_start = 3 * (i // 3)
                projection.append(sum(1 << j for j in range(block_start, block_start + 3) if j != i))
        complement = [a ^ b for a, b in zip(identity, projection)]
        columns = [sum(1 << j for j in range(3 * k, 3 * k + 3)) for k in range(27)]
        columns += [1 << i for i in range(81, 99)]
        even_vectors = [(1 << (3*k+i)) | (1 << (3*k+2)) for k in range(27) for i in (0, 1)]
        for vector in even_vectors:
            columns.extend([vector, vector])
        columns.extend([0] * (231 - len(columns)))
        factor = transpose(columns, 99)
        image = multiply(projection, factor, 231)
        need(len(factor) == 99 and len(columns) == 231, 'exact raw dimensions')
        need(all(not ((row >> i) & 1) for i, row in enumerate(projection)), 'symmetric projection has zero diagonal')
        need(projection == transpose(projection, 99), 'projection symmetry')
        need(multiply(projection, projection, 99) == projection, 'idempotent projection')
        need(multiply(complement, complement, 99) == complement, 'idempotent complement')
        need(multiply(projection, complement, 99) == [0] * 99, 'complementary projectors')
        need(gram(factor) == complement, 'complete scalar BB^T equals M')
        need(gram(image) == [0] * 99, 'complete scalar CC^T zero')
        ranks = dict(P=rank(projection), M=rank(complement), B=rank(factor), C=rank(image))
        need(ranks == dict(P=54, M=45, B=99, C=54), 'independent exact ranks')
        need(rank(multiply(projection, factor, 231)) > rank(projection)//2, 'literal falsification of rejected codomain rank inference')
        changed_columns = list(columns)
        changed_columns[45] ^= 1
        changed_factor = transpose(changed_columns, 99)
        need(gram(changed_factor) != complement, 'corrupted duplicate-column fixture rejects claimed factorization')
        changed_projection = list(projection)
        changed_projection[0] ^= 1
        need(multiply(changed_projection, changed_projection, 99) != changed_projection, 'corrupted projection rejects idempotence')
        toy = [sum(1 << j for j in (i, i + 54)) for i in range(54)]
        need(rank(toy) == 54 and gram(toy) == [0] * 54, 'independent I54-I54 positive control')
        need(not deadline.status()['stop_required'], 'contained calculation completed within allowance')
        save(out/'raw_counterexample.json', dict(format='GENERIC_BINARY_PROJECTION_FACTOR_COUNTEREXAMPLE_V1', arithmetic='GF(2)', dimensions=dict(vertices=99, factor_columns=231), P_row_bitsets=[str(x) for x in projection], M_row_bitsets=[str(x) for x in complement], B_column_bitsets=[str(x) for x in columns], C_row_bitsets=[str(x) for x in image]))
        pins = {p.relative_to(ROOT).as_posix(): digest(p) for p in [Path(__file__), SPEC, ROOT/'uv.lock', ROOT/'pyproject.toml', ROOT/'acceleration/command_deadline.py', ROOT/'acceleration/run_compute_command.py']}
        save(out/'summary.json', dict(status='INDEPENDENT_REJECTED_CODOMAIN_ISOTROPY_COUNTEREXAMPLE_PASS', timestamp=datetime.now(timezone.utc).isoformat(), source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(), command=[sys.executable,*sys.argv], cwd=str(ROOT), python_version=platform.python_version(), inputs_sha256=pins, counterexample_sha256=digest(out/'raw_counterexample.json'), ranks=ranks, exact_checked_identities=['P symmetric, diagonalzero, P^2=P','M=I+P, M^2=M, PM=0','BB^T=M','C=PB, CC^T=0','rank(P)=54,rank(M)=45,rank(B)=99,rank(C)=54'], controls=['I54-I54 has rank54 and zero Gram','Changed duplicate factor column breaks BB^T=M','Changed projection diagonal breaks P^2=P'], refuted_statement='For every factor B of a rank45 complementary projector M, C=(I-M)B and CC^T=0 imply rank(C)<=27 because the codomain has dimension54.', rejected_argument_originator='/root/structural', raw_counterexample_originator='/root', verifier='/root/structural', shared_code='No producer code imported; only budget/deadline helper and standard library. Independent scalar dot-product matrix multiplication and integer-bitset row elimination.', target_bound_status='UNKNOWN', mathematical_scope='Generic binary projection/factor implication only. Synthetic B contains columns of weights0,1,2,3 and does not satisfy the actual linear3uniform7regular triangle-incidence domain. No refutation of a target-specific rank72 statement, existence or nonexistence.', target_resolution=False, elapsed_seconds=time.monotonic()-started, deadline=deadline.status()))
    except Exception as error:
        save(out/'failure.json', dict(error=repr(error), elapsed_seconds=time.monotonic()-started, all_outputs_preserved=True))
        raise


if __name__ == '__main__':
    main()
