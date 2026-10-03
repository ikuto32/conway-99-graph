"""Independent exact dense matrix path for finite two-line swap controls.

V1 calibrates complete rook9 proposals BEFORE any warm239085 proposal output.
No producer imports, bitset scores, optimizer or random moves.
"""
import argparse
from collections import Counter
import copy
from datetime import datetime, timezone
import hashlib
import itertools
import json
from pathlib import Path
import platform
import subprocess
import sys
import numpy as np
from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]


def need(ok, why):
    if not ok:
        raise ValueError(why)


def adjacency(n, degree, triples):
    need(type(n) is int and n in (9, 12, 99) and degree == (7 if n == 99 else 2), 'exact point domain')
    need(len(triples) * 3 == n * degree, 'complete triple population')
    a = np.zeros((n, n), dtype=np.int64)
    incidences = [0] * n
    for triple in triples:
        need(len(triple) == 3 and len(set(triple)) == 3 and
             all(type(v) is int and 0 <= v < n for v in triple), 'distinct literal triple labels')
        for v in triple:
            incidences[v] += 1
        for u, v in itertools.combinations(triple, 2):
            need(a[u, v] == 0, 'linear incidence')
            a[u, v] = a[v, u] = 1
    need(incidences == [degree] * n, 'complete point degrees')
    return a


def energy(a, cn, root):
    n = len(a)
    ii, jj = np.triu_indices(n, 1)
    edges = a[ii, jj] == 1
    lam = int(np.sum((cn[ii[edges], jj[edges]] - 1) ** 2, dtype=np.int64))
    mu = int(np.sum((cn[ii[~edges], jj[~edges]] - 2) ** 2, dtype=np.int64))
    outsiders = (a[root] == 0)
    outsiders[root] = False
    row = int(np.sum((cn[root, outsiders] - 2) ** 2, dtype=np.int64))
    return lam, mu, row


def classify(a, cn, triples, i, j, ix, jy, root, baseline):
    need(0 <= i < j < len(triples) and ix in range(3) and jy in range(3), 'canonical proposal indices')
    old = [list(triples[i]), list(triples[j])]
    p, q = old[0][ix], old[1][jy]
    proposed = copy.deepcopy(old)
    proposed[0][ix], proposed[1][jy] = q, p
    if p in old[1] or q in old[0]:
        return dict(valid=False, invalid_reason='exclusive-selection', old_triples=old,
                    new_triples=proposed)
    new_a = a.copy()
    for triple in old:
        for u, v in itertools.combinations(triple, 2):
            need(new_a[u, v] == 1, 'all removed old pairs present')
            new_a[u, v] = new_a[v, u] = 0
    for triple in proposed:
        for u, v in itertools.combinations(triple, 2):
            if new_a[u, v]:
                return dict(valid=False, invalid_reason='new-pair-already-present',
                            old_triples=old, new_triples=proposed)
            new_a[u, v] = new_a[v, u] = 1
    d = new_a - a
    changed = np.flatnonzero(np.any(d != 0, axis=1))
    # Both endpoints of every changed edge belong to changed. All other rows
    # are identical, so every outside/outside scalar dot product is unchanged.
    need(np.all(np.sum(new_a, axis=1) == np.sum(a, axis=1)), 'exact adjacency degrees preserved')
    new_cn = cn.copy()
    block = new_a[changed] @ new_a
    new_cn[changed, :] = block
    new_cn[:, changed] = block.T
    el, em, er = energy(new_a, new_cn, root)
    ii, jj = np.triu_indices(len(a), 1)
    toggles = [[int(u), int(v), int(d[u, v])] for u, v in zip(ii, jj) if d[u, v]]
    return dict(valid=True, invalid_reason=None, old_triples=old, new_triples=proposed,
                net_adjacency_toggles=toggles, delta_lambda=el-baseline[0], delta_mu=em-baseline[1],
                new_lambda=el, new_mu=em, root_row_residual_delta=er-baseline[2],
                new_matrix=new_a, new_cn=new_cn)


def strict_reject(records, label, call):
    try:
        call()
    except ValueError as exc:
        records.append(dict(case=label, diagnostic=str(exc)))
    else:
        raise ValueError('corrupt control accepted: ' + label)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--seconds', type=float, required=True)
    args = ap.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='Complete135 rook9 swap matrix controls and strict corruptions;60worker90outer30shutdown no scientific census')
    out = args.out.resolve()
    need(out.is_relative_to(ROOT), 'workspace output')
    out.mkdir(parents=True, exist_ok=False)
    triples = [list(range(3*r, 3*r+3)) for r in range(3)] + [[c, c+3, c+6] for c in range(3)]
    a = adjacency(9, 2, triples)
    cn = a @ a
    expected_a = np.asarray([[int(i != j and (i//3 == j//3 or i%3 == j%3)) for j in range(9)]
                             for i in range(9)], dtype=np.int64)
    need(np.array_equal(a, expected_a), 'known complete rook adjacency')
    need(all(int(cn[i, j]) == (4 if i == j else 1 if a[i, j] else 2)
             for i in range(9) for j in range(9)), 'known exact rook SRG identity')
    baseline = energy(a, cn, 0)
    need(baseline == (0, 0, 0), 'known rook zero components')
    records, counts = [], Counter()
    valid_overlap = 0
    for pair, (i, j) in enumerate(itertools.combinations(range(6), 2)):
        for ix in range(3):
            for jy in range(3):
                rec = classify(a, cn, triples, i, j, ix, jy, 0, baseline)
                rec.update(proposal_id=9*pair+3*ix+jy, i=i, j=j, ix=ix, jy=jy)
                counts['valid' if rec['valid'] else rec['invalid_reason']] += 1
                if rec['valid']:
                    current = [row[:] for row in triples]
                    current[i], current[j] = rec['new_triples']
                    rebuilt = adjacency(9, 2, current)
                    # Calibrate affected-row proof against full integer matrix
                    # multiplication and literal scalar loops on EVERY valid move.
                    full = rebuilt @ rebuilt
                    scalar = [[sum(int(rebuilt[u, k]) * int(rebuilt[k, v]) for k in range(9))
                               for v in range(9)] for u in range(9)]
                    need(np.array_equal(rebuilt, rec['new_matrix']) and np.array_equal(full, rec['new_cn'])
                         and np.array_equal(full, scalar), 'complete full-matrix delta control')
                    need(energy(rebuilt, full, 0) == (rec['new_lambda'], rec['new_mu'],
                         rec['root_row_residual_delta']), 'complete component/root delta control')
                    valid_overlap += bool(set(triples[i]) & set(triples[j]))
                    rec.pop('new_matrix'); rec.pop('new_cn')
                records.append(rec)
    need(len(records) == 135 and [r['proposal_id'] for r in records] == list(range(135)), 'complete135 labelled proposals')
    need(valid_overlap > 0 and all(counts[key] > 0 for key in
         ('valid', 'exclusive-selection', 'new-pair-already-present')), 'positive overlap and both invalid paths')
    negatives = []
    for label, damaged in [('missing_triple', triples[:-1]), ('duplicate_triple', triples[:-1]+[triples[0]]),
                           ('bad_label', [[99,1,2], *triples[1:]]),
                           ('bool_label', [[False,1,2], *triples[1:]])]:
        strict_reject(negatives, label, lambda damaged=damaged: adjacency(9, 2, damaged))
    strict_reject(negatives, 'wrong_degree', lambda: adjacency(9, 7, triples))
    strict_reject(negatives, 'same_triple_proposal', lambda: classify(a, cn, triples, 0, 0, 0, 0, 0, baseline))
    strict_reject(negatives, 'out_of_range_index', lambda: classify(a, cn, triples, 0, 1, 3, 0, 0, baseline))
    need(not deadline.status()['stop_required'], 'not completed within allocated budget')
    path = out / 'rook135_records.json'
    path.write_text(json.dumps(records, indent=2)+'\n', encoding='utf8', newline='\n')
    def digest(p):
        return hashlib.sha256(p.read_bytes()).hexdigest()
    source = Path(__file__)
    spec = source.with_name(source.stem+'_spec.md')
    report = dict(status='INDEPENDENT_TWO_LINE_DENSE_DELTA_V1_PREOUTPUT_CALIBRATION_PASS',
                  timestamp=datetime.now(timezone.utc).isoformat(), verifier='/root',
                  command=[sys.executable, *sys.argv], cwd=str(ROOT), python=platform.python_version(),
                  numpy=np.__version__, source_commit=subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
                  complete_rook_proposals=135, counts=dict(counts), valid_overlapping=valid_overlap,
                  complete_fullmatrix_comparisons=counts['valid'], strict_corruptions=negatives,
                  producer_census_output_inspected=False, scientific_census_launches=0,
                  integer_range_bound='n<=99; CN<=99; total unweighted pair energy<=4851*99^2; signed intermediate and sums far below2^63.',
                  shared_components=['NumPy fixed-width integer arithmetic with explicit size bounds and full literal scalar calibration; pinned deadline and Python runtime.', 'No producer/native/parser/scorer imports.'],
                  inputs_outputs_sha256={p.relative_to(ROOT).as_posix():digest(p) for p in
                  [source,spec,path,ROOT/'pyproject.toml',ROOT/'uv.lock',ROOT/'acceleration/command_deadline.py']},
                  limitations=['Finite rook calibration only; no scientific239085 census outcome or whole algorithm formalization.', 'A new complete output checker version will bind producer source/interface and actual warm artifacts.'],
                  target_resolution='NONE', deadline=deadline.status())
    (out/'summary.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8',newline='\n')
    print(json.dumps(dict(status=report['status'], counts=dict(counts), valid_overlapping=valid_overlap)))


if __name__ == '__main__':
    main()
