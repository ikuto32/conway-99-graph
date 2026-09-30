"""Cheap exact LP and modular screens of the frozen all-column linear system.

Success criterion: an exact inconsistent modular row would supply a candidate
obstruction for independent review. Otherwise preserve explicit modular
witnesses; these neither solve the binary problem nor close a target branch.
Resource bound: one deterministic elimination for p=2 and p=3, 60s/8GiB.
"""
from datetime import datetime, timezone
from pathlib import Path
import argparse
import hashlib
import json
import platform
import subprocess
import sys
import time
import numpy as np
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT/'acceleration/results/20260930_prism_all_columns/model.json'
MODEL_SHA = 'a801e721a4c03d18e2fa9711a60f053895a4bfb8898b264f5174bcc36265f038'
GATE = ROOT/'acceleration/results/20260930_independent_review/prism_all_columns_cnf/summary.json'
GATE_SHA = '07c589160e930205bc7e42f9524846280b4a8f0573ca9e5dfa06b627a6d115c3'


def h(p):
    with p.open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def save(p, value):
    with p.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, indent=2)
        f.write('\n')


def solve_modular(a, b, prime, deadline):
    # Integer residues remain in 0..p-1; int16 products are at most 4 for p<=3.
    rows, cols = a.shape
    r = np.concatenate([a, b[:, None]], axis=1).astype(np.int16) % prime
    transform = np.eye(rows, dtype=np.int16)
    pivots = []
    top = 0
    with tqdm(total=rows, desc=f'row elimination mod {prime}') as progress:
        for col in range(cols):
            assert time.monotonic() < deadline, '60-second modular screen limit'
            candidates = np.flatnonzero(r[top:, col])
            if not len(candidates):
                continue
            pivot = top+int(candidates[0])
            r[[top, pivot]] = r[[pivot, top]]
            transform[[top, pivot]] = transform[[pivot, top]]
            inverse = pow(int(r[top, col]), -1, prime)
            r[top] = (r[top]*inverse) % prime
            transform[top] = (transform[top]*inverse) % prime
            affected = np.flatnonzero(r[:, col])
            affected = affected[affected != top]
            coeff = r[affected, col].copy()
            r[affected] = (r[affected]-coeff[:, None]*r[top]) % prime
            transform[affected] = (transform[affected]-coeff[:, None]*transform[top]) % prime
            pivots.append(col)
            top += 1
            progress.update(1)
            if top == rows:
                break
    bad = [i for i in range(top, rows) if r[i, -1] != 0]
    if bad:
        i = bad[0]
        return dict(prime=prime, status='INCONSISTENT_CANDIDATE_CERTIFICATE', rank=top,
                    row_combination=transform[i].tolist(), nonzero_rhs=int(r[i, -1]))
    x = [0]*cols
    for i, col in enumerate(pivots):
        x[col] = int(r[i, -1])
    return dict(prime=prime, status='MODULAR_SOLUTION_NOT_BINARY_FACTOR', rank=top, assignment=x)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    assert h(MODEL) == MODEL_SHA and h(GATE) == GATE_SHA
    inputs = [Path(__file__), MODEL, GATE, ROOT/'uv.lock', ROOT/'pyproject.toml']
    save(out/'manifest.json', dict(timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        command=[sys.executable, *sys.argv], cwd=str(ROOT), python=platform.python_version(), numpy=np.__version__,
        inputs_sha256={p.relative_to(ROOT).as_posix(): h(p) for p in inputs},
        question='Can linear congruences mod2/mod3 already exclude the complete six-prism column factor?',
        selection_rule='All 540 frozen one-choice and row-Gram equations; both primes dividing uniform denominator96.',
        success_criterion='An exact nonzero-RHS zero row with replayable input-row combination; independent checking mandatory.',
        limits=dict(seconds=60, memory_bytes=8*1024**3), random_seed=None,
        random_seed_reason='Deterministic elimination, no numerical tolerances.'))
    model = json.loads(MODEL.read_bytes())
    equations = model['counter_rows']
    assert len(equations) == 540
    a = np.zeros((540, 5760), dtype=np.int16)
    b = np.array([row['bound'] for row in equations], dtype=np.int16)
    for i, row in enumerate(equations):
        assert row['equality'] is True
        a[i, np.array(row['inputs'])-1] = 1
    # Exact rational witness: every choice has weight 1/96.
    assert all(len(row['inputs']) == 96*row['bound'] for row in equations)
    save(out/'uniform_rational_witness.json', dict(variables=5760, numerator=1, denominator=96,
        every_linear_equality_satisfied=True, every_weight_strictly_between_zero_and_one=True,
        scope='Continuous one-choice/Gram linear relaxation only; not the auxiliary threshold CNF or binary feasibility.'))
    controls = []
    for prime in (2, 3):
        positive = solve_modular(np.array([[1, 0], [0, 1]], dtype=np.int16), np.array([1, 1], dtype=np.int16), prime, start+60)
        negative = solve_modular(np.array([[1, 1], [1, 1]], dtype=np.int16), np.array([0, 1], dtype=np.int16), prime, start+60)
        assert positive['assignment'] == [1, 1]
        w = negative['row_combination']
        assert sum(w) % prime == 0 and w[1] % prime == negative['nonzero_rhs'] != 0
        controls.append(dict(prime=prime, positive=positive, inconsistent=negative))
    save(out/'controls.json', controls)
    results = []
    for prime in (2, 3):
        result = solve_modular(a, b, prime, start+60)
        if 'assignment' in result:
            x = result['assignment']
            assert all(sum(x[j-1] for j in row['inputs']) % prime == row['bound'] % prime for row in equations)
        else:
            w = result['row_combination']
            assert all(sum(w[i]*int(a[i, j]) for i in range(540)) % prime == 0 for j in range(5760))
            assert sum(w[i]*int(b[i]) for i in range(540)) % prime == result['nonzero_rhs'] != 0
        save(out/f'mod_{prime}.json', result)
        results.append({k: v for k, v in result.items() if k not in ('assignment', 'row_combination')})
    save(out/'summary.json', dict(status='EXACT_LINEAR_SCREENS_PENDING_INDEPENDENT_REVIEW',
        rational_relaxation='FEASIBLE_UNIFORM_1_OVER_96', modular_results=results,
        elapsed_seconds=time.monotonic()-start, floating_point_used=False, independent_approval=False,
        target_resolution=False, outputs_sha256={p.relative_to(ROOT).as_posix(): h(p) for p in out.iterdir() if p.is_file()}))
    print(json.dumps(results))


if __name__ == '__main__':
    main()
