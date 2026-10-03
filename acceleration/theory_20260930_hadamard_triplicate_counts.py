"""Candidate exact marginal and local-triplet projections; no SAT/LP solve."""
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path
import argparse
import hashlib
import json
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
B = 'acceleration/results/20260930_'
RAW = B + 'hadamard20_support/six_prism.json'
PINS = {RAW: 'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',
        B + 'independent_review/hadamard20_support_v2/summary.json': 'a8477256446e3e402a2a21241dc383a515162dc9c8c07a9a8e26326c07b0f58f',
        B + 'independent_review/hadamard_six_prism_column_order/summary.json': '0ce1be9ca11a3e860aa97791cfb4f42c1660d937a69ac7a9b7d96ca37640c9d2'}


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(p):
    with Path(p).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def save(p, x):
    with p.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(x, f, indent=2)
        f.write('\n')


def rref(a):
    m, n = len(a), len(a[0])
    r = [[Fraction(v) for v in row] for row in a]
    u = [[Fraction(i == j) for j in range(m)] for i in range(m)]
    pivots, ops = [], []
    for j in range(n):
        k = next((k for k in range(len(pivots), m) if r[k][j]), None)
        if k is None:
            continue
        p = len(pivots)
        if k != p:
            r[k], r[p], u[k], u[p] = r[p], r[k], u[p], u[k]
            ops.append(['swap', k, p])
        f = r[p][j]
        r[p] = [x / f for x in r[p]]
        u[p] = [x / f for x in u[p]]
        ops.append(['scale', p, str(1 / f)])
        for k in range(m):
            if k == p or not r[k][j]:
                continue
            f = r[k][j]
            r[k] = [x - f * y for x, y in zip(r[k], r[p])]
            u[k] = [x - f * y for x, y in zip(u[k], u[p])]
            ops.append(['add', k, p, str(-f)])
        pivots.append(j)
    need([[sum(u[i][k] * a[k][j] for k in range(m)) for j in range(n)] for i in range(m)] == r, 'literal row transform')
    return dict(rank=len(pivots), pivot_columns=pivots, rref=[[str(x) for x in row] for row in r],
                left_transform=[[str(x) for x in row] for row in u], operations=ops)


def check_kernel(a, v):
    need(len(v) == len(a[0]) and any(v), 'nonzero kernel shape')
    need(all(sum(x * y for x, y in zip(row, v)) == 0 for row in a), 'integer kernel equations')


def word_rows(w):
    need(len(w) == 6 and sorted(w) == [0, 0, 1, 1, 2, 2], 'balanced six-colouring')
    return [6 * g + i for i, g in enumerate(w)]


def literal_triple(words):
    need(len(words) == 3 and len({tuple(w) for w in words}) == 3, 'three distinct words')
    rows = [set(word_rows(w)) for w in words]
    need(all(len(a & b) <= 2 for a, b in combinations(rows, 2)), 'three outside column caps')
    for i, j in combinations(range(18), 2):
        observed = sum(i in r and j in r for r in rows)
        bound = 0 if i % 6 == j % 6 else (1 if i // 6 == j // 6 else 2)
        need(observed <= bound, 'local literal Gram cap')
    return dict(words=[list(w) for w in words], rows=[sorted(r) for r in rows],
                overlaps=[len(a & b) for a, b in combinations(rows, 2)],
                colour_counts=[[sum(w[i] == g for w in words) for g in range(3)] for i in range(6)])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    timestamp = datetime.now(timezone.utc).isoformat()
    pins = {}
    corruptions = []

    def reject(name, fn):
        try:
            fn()
        except ValueError:
            corruptions.append(name)
        else:
            raise AssertionError('corruption accepted: ' + name)

    try:
        for path, expected in PINS.items():
            need(digest(ROOT / path) == expected, 'frozen input ' + path)
            pins[path] = expected
        for path in ['acceleration/theory_20260930_hadamard_triplicate_counts.py', 'acceleration/theory_20260930_hadamard_triplicate_counts_spec.md', 'uv.lock', 'pyproject.toml']:
            pins[path] = digest(ROOT / path)
        need(rref([[1, 0], [0, 1]])['rank'] == 2 and rref([[1, 1], [2, 2]])['rank'] == 1, 'known exact ranks')
        check_kernel([[1, 1], [2, 2]], [1, -1])
        reject('wrong_kernel', lambda: check_kernel([[1, 1]], [1, 1]))
        reject('zero_kernel', lambda: check_kernel([[1, 1]], [0, 0]))
        reject('bad_word_value', lambda: word_rows([0, 0, 1, 1, 2, 3]))
        reject('bad_word_margin', lambda: word_rows([0, 0, 0, 1, 2, 2]))
        base = (0, 0, 1, 1, 2, 2)
        cyclic_control = literal_triple([tuple((x + s) % 3 for x in base) for s in range(3)])
        reject('duplicate_word', lambda: literal_triple([base, base, tuple((x + 1) % 3 for x in base)]))
        reject('repeated_Gram_pair', lambda: literal_triple([base, (0, 0, 1, 2, 1, 2), (1, 1, 2, 2, 0, 0)]))
        raw = json.loads((ROOT / RAW).read_bytes())
        supports = [[a for a in range(12) if raw['L'][a][d]] for d in range(60)]
        need(raw['support_columns'] == supports, 'raw support reconstruction')
        distinct = []
        groups = []
        for d, s in enumerate(supports):
            if s not in distinct:
                distinct.append(s)
                groups.append([j for j, t in enumerate(supports) if t == s])
        need(len(groups) == 20 and all(len(g) == 3 for g in groups), 'twenty triplicate supports')
        need(all(len(s) == 6 and len({a // 2 for a in s}) == 6 for s in distinct), 'support picks one matching endpoint')
        words = sorted(w for w in product(range(3), repeat=6) if all(w.count(g) == 2 for g in range(3)))
        need(len(words) == 90, 'complete90 balanced words')
        for d in range(60):
            need([o['fibres_by_sorted_coordinate'] for o in raw['column_colour_options'][d]] == [list(w) for w in words], 'raw domain alignment')
        marginals = []
        for a in range(12):
            indices = [p for p, s in enumerate(distinct) if a in s]
            others = [b for b in range(12) if b // 2 != a // 2]
            matrix = [[1] * 10] + [[int(b in distinct[p]) for p in indices] for b in others]
            need(len(indices) == 10 and all(sum(row) == 5 for row in matrix[1:]), 'marginal incidence parameters')
            cert = rref(matrix)
            tested = 0
            witness = None
            for v in product([-1, 0, 1], repeat=10):
                tested += 1
                if any(v) and all(sum(x * y for x, y in zip(row, v)) == 0 for row in matrix):
                    check_kernel(matrix, v)
                    witness = list(v)
                    break
            need(witness is not None, 'bounded marginal kernel witness found')
            counts = [[1 + v, 1 - v, 1] for v in witness]
            need(all(sum(t) == 3 and min(t) >= 0 and max(t) <= 3 for t in counts), 'three-fibre counts bounds')
            for g in range(3):
                need([sum(row[j] * counts[j][g] for j in range(10)) for row in matrix] == [10] + [5] * 10, 'exact marginal count equations')
            marginals.append(dict(coordinate=a, groups=indices, other_coordinates=others, matrix=matrix, rhs=[10] + [5] * 10,
                                  elimination=cert, kernel_witness=witness, colour_counts=counts, enumerated_vectors=tested))
            need(time.monotonic() - started < 60, '60second resource limit')
        # Exact cap test with bitsets, calibrated separately against literal matrices.
        pair_index = {(a, b, g, h): i for i, (a, b, g, h) in enumerate((a, b, g, h) for a, b in combinations(range(6), 2) for g in range(3) for h in range(3))}
        rowmasks, within, cross = [], [], []
        for w in words:
            rowmasks.append(sum(1 << r for r in word_rows(w)))
            within.append(sum(1 << pair_index[a, b, w[a], w[b]] for a, b in combinations(range(6), 2) if w[a] == w[b]))
            cross.append(sum(1 << pair_index[a, b, w[a], w[b]] for a, b in combinations(range(6), 2) if w[a] != w[b]))
        compatible = [[not (within[i] & within[j]) and (rowmasks[i] & rowmasks[j]).bit_count() <= 2 for j in range(90)] for i in range(90)]
        survivors, balanced, cyclic = [], [], []
        profile_counts = Counter()
        coordinate_count_witness = {}
        first_unbalanced = first_balanced_noncyclic = None
        examined = 0
        for i, j, k in combinations(range(90), 3):
            examined += 1
            if not (compatible[i][j] and compatible[i][k] and compatible[j][k]) or cross[i] & cross[j] & cross[k]:
                continue
            triple = [words[i], words[j], words[k]]
            cc = [tuple(sum(w[a] == g for w in triple) for g in range(3)) for a in range(6)]
            survivor = [i, j, k]
            survivors.append(survivor)
            profile = tuple(sorted(tuple(sorted(v)) for v in cc))
            profile_counts[str(profile)] += 1
            for a, vector in enumerate(cc):
                coordinate_count_witness.setdefault((a, vector), survivor)
            isbalanced = all(v == (1, 1, 1) for v in cc)
            iscyclic = set(triple) == {tuple((x + s) % 3 for x in triple[0]) for s in range(3)}
            if isbalanced:
                balanced.append(survivor)
            if iscyclic:
                cyclic.append(survivor)
            if not isbalanced and first_unbalanced is None:
                first_unbalanced = dict(option_indices=survivor, **literal_triple(triple))
            if isbalanced and not iscyclic and first_balanced_noncyclic is None:
                first_balanced_noncyclic = dict(option_indices=survivor, **literal_triple(triple))
        need(examined == 117480, 'entire increasing triple universe')
        need(time.monotonic() - started < 60, '60second resource limit')
        # Every aggregate-coordinate marginal witness has local cap-compatible
        # triplet realizations separately, with no asserted agreement elsewhere.
        for record in marginals:
            local = []
            for p, counts in zip(record['groups'], record['colour_counts']):
                pos = distinct[p].index(record['coordinate'])
                triple = coordinate_count_witness.get((pos, tuple(counts)))
                need(triple is not None, 'marginal vector locally realizable')
                obj = literal_triple([words[t] for t in triple])
                need(obj['colour_counts'][pos] == counts, 'raw local witness realizes count')
                local.append(dict(group=p, coordinate_position=pos, option_indices=triple, local_check=obj))
            record['separate_local_realizations'] = local
        controls = dict(known_rank_controls=2, kernel_positive=True, cyclic_local_positive=cyclic_control, corruptions=corruptions)
        save(out / 'controls.json', controls)
        save(out / 'marginal_certificates.json', marginals)
        save(out / 'local_triples.json', dict(words=[list(w) for w in words], examined=examined, survivors=survivors, balanced=balanced, cyclic=cyclic,
                                            count_profile_histogram=dict(profile_counts), first_unbalanced=first_unbalanced, first_balanced_noncyclic=first_balanced_noncyclic))
        outputs = {str(p.relative_to(ROOT)).replace('\\', '/'): digest(p) for p in sorted(out.glob('*.json'))}
        summary = dict(status='CANDIDATE_EXACT_TRIPLICATE_PROJECTION_RESULTS', timestamp=timestamp, finished_at=datetime.now(timezone.utc).isoformat(),
                       source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), command=[sys.executable, *sys.argv], cwd=str(ROOT),
                       python=platform.python_version(), inputs_sha256=pins, outputs_sha256=outputs,
                       marginal_cases=12, marginal_ranks=[r['elimination']['rank'] for r in marginals], marginal_nonconstant_witnesses=len(marginals),
                       local_triple_universe=examined, local_cap_survivors=len(survivors), coordinatewise_balanced_survivors=len(balanced), cyclic_survivors=len(cyclic),
                       independent_approval=False, claim_status='CANDIDATE', target_resolution=False, full_factor_balance_implication='UNKNOWN',
                       limitations=['Nonconstant marginal witnesses refute only uniqueness in this necessary projection, not full-Gram necessity.',
                                    'A local triple witness is not a full factor. Separate local realizations for a marginal vector need not agree on other coordinates.',
                                    'Exact local Gram/Y-cap conditions only; all interactions between different support groups are omitted.',
                                    'The cyclic subclass UNSAT is not used as a premise and cyclicity is not imposed.',
                                    'Bounded archive keyword search found related general incidence-code/moment work, not an identical saved-L count model; no novelty claim.'],
                       wall_seconds=time.monotonic()-started)
        save(out / 'summary.json', summary)
        print(json.dumps({k: summary[k] for k in ['status', 'marginal_ranks', 'local_cap_survivors', 'coordinatewise_balanced_survivors', 'cyclic_survivors', 'wall_seconds']}))
    except BaseException as exc:
        save(out / 'failure.json', dict(error=repr(exc), elapsed_seconds=time.monotonic()-started))
        raise


if __name__ == '__main__':
    main()
