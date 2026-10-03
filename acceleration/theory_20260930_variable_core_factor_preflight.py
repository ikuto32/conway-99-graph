"""Cheap exact algebra and actual encoder size preflight; no CNF or solver."""
from datetime import datetime, timezone
from itertools import combinations, product
from pathlib import Path
import argparse
import json
import platform
import random
import subprocess
import sys
import time
from theory_20260930_eight_full99_cnf import Clauses, Encoder, ResourceCap, digest, save

ROOT = Path(__file__).resolve().parents[1]


def key(p):
    return Path(p).resolve().relative_to(ROOT).as_posix()


def calibrate():
    rng = random.Random(20260930)
    checks = []
    for case in range(12):
        matchings = []
        for g in range(3):
            order = list(range(12))
            if g and case:
                rng.shuffle(order)
            mate = [None]*12
            for i in range(0, 12, 2):
                a, b = order[i:i+2]
                mate[a], mate[b] = b, a
            matchings.append(mate)
        perm = list(range(12))
        if case:
            rng.shuffle(perm)
        b = [[0]*36 for _ in range(36)]
        for g, mate in enumerate(matchings):
            for a, c in enumerate(mate):
                b[12*g+a][12*g+c] = 1
        for a in range(12):
            for x, y in ((a, 12+a), (a, 24+a), (12+a, 24+perm[a])):
                b[x][y] = b[y][x] = 1
        raw = [[12*int(i == j)-b[i][j]-sum(b[i][k]*b[k][j] for k in range(36))+2-int(i//12 == j//12)
                for j in range(36)] for i in range(36)]
        predicted = [[None]*36 for _ in range(36)]
        m0, m1, m2 = matchings
        for g, mate in enumerate(matchings):
            for a in range(12):
                for c in range(12):
                    predicted[12*g+a][12*g+c] = 9*int(a == c)+1-int(mate[a] == c)
        for a, c in product(range(12), repeat=2):
            values = [(0, 1, 2-int(a == c)-int(m0[a] == c)-int(m1[a] == c)-int(perm[c] == a)),
                      (0, 2, 2-int(a == c)-int(m0[a] == c)-int(m2[a] == c)-int(perm[a] == c)),
                      (1, 2, 2-int(a == c)-int(perm[a] == c)-int(perm[m1[a]] == c)-int(m2[perm[a]] == c))]
            for g, h, value in values:
                predicted[12*g+a][12*h+c] = predicted[12*h+c][12*g+a] = value
        assert predicted == raw
        changed = [r.copy() for r in predicted]
        changed[0][12] += 1
        assert changed != raw
        checks.append({'case': case, 'matchings': matchings, 'P': perm, 'all_1296_entries_equal': True,
                       'changed_entry_detected': True})
    return {'status': 'PRODUCER_VARIABLE_CORE_FORMULA_FIXTURES_PASS', 'random_seed': 20260930,
            'cases': checks, 'limitations': 'Twelve exact fixtures calibrate formulas; no coverage proof or independent approval.'}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    cap = ResourceCap()
    paths = [Path(__file__), Path(__file__).with_name('theory_20260930_variable_core_factor_preflight_spec.md'),
             ROOT/'uv.lock', ROOT/'pyproject.toml', ROOT/'acceleration/theory_20260930_eight_full99_cnf.py']
    save(out/'manifest.json', {'timestamp': datetime.now(timezone.utc).isoformat(),
        'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        'command': [sys.executable, *sys.argv], 'working_directory': str(ROOT), 'python': platform.python_version(),
        'inputs_sha256': {key(p): digest(p) for p in paths}, 'status': 'CANDIDATE_SIZE_AND_FORMULA_PREFLIGHT',
        'limits': {'seconds': 120, 'memory_bytes': 8*1024**3, 'solver_calls': 0},
        'coverage_gate': None, 'coverage_gate_null_reason': 'Separate normalization derivation and independent coverage audit pending.'})
    save(out/'formula_controls.json', calibrate())
    top = 0

    def fresh():
        nonlocal top
        top += 1
        return top

    f = [[[fresh() for _ in range(60)] for _ in range(12)] for _ in range(2)]
    matchings = []
    for _ in range(2):
        m = [[False]*12 for _ in range(12)]
        for a, b in combinations(range(12), 2):
            m[a][b] = m[b][a] = fresh()
        matchings.append(m)
    p = [[fresh() for _ in range(12)] for _ in range(12)]
    assert top == 1716
    clauses = Clauses(None, cap)
    enc = Encoder(top, clauses)
    populations, products_count = {}, {}

    def eq(terms, bound, kind):
        terms = [x for x in terms if type(x) is int]
        enc.counter(terms, bound, True, {})
        populations[kind] = populations.get(kind, 0)+1

    def both(a, b, kind):
        products_count[kind] = products_count.get(kind, 0)+1
        return enc.conjunction(a, b)

    for m in matchings:
        for row in m:
            eq(row, 1, 'matching_row')
    for a in range(12):
        eq(p[a], 1, 'permutation_row')
        eq([p[b][a] for b in range(12)], 1, 'permutation_column')
    for fibre in f:
        for row in fibre:
            eq(row, 10, 'incidence_row')
        for d in range(60):
            eq([fibre[a][d] for a in range(12)], 2, 'incidence_column')
    edges = list(e for e in combinations(range(12), 2) if e[1] != (e[0]^1))
    for g in range(2):
        for a, b in product(range(12), repeat=2):
            terms = [f[g][b][d] for d, e in enumerate(edges) if a in e]
            terms += [matchings[g][a][b], p[b][a] if g == 0 else p[a][b]]
            eq(terms, 2-int(a == b)-int((a^1) == b), 'C0_cross_Gram')
        for a, b in combinations(range(12), 2):
            terms = [both(f[g][a][d], f[g][b][d], 'within_fibre_incidence') for d in range(60)]
            eq(terms+[matchings[g][a][b]], 1, 'within_fibre_Gram')
    for a, b in product(range(12), repeat=2):
        terms = [both(f[0][a][d], f[1][b][d], 'cross_fibre_incidence') for d in range(60)]
        terms.append(p[a][b])
        terms += [both(matchings[0][a][k], p[k][b], 'M1P') for k in range(12) if k != a]
        terms += [both(p[a][k], matchings[1][k][b], 'PM2') for k in range(12) if k != b]
        eq(terms, 2-int(a == b), 'C1_C2_Gram')
    before = clauses.count
    for d, e in combinations(range(60), 2):
        if set(edges[d]) & set(edges[e]):
            for a, b in product(range(12), repeat=2):
                clauses.emit(-f[0][a][d], -f[0][a][e], -f[1][b][d], -f[1][b][e])
    assert clauses.count-before == 77760 and sum(products_count.values()) == 19728
    assert sum(populations.values()) == 756
    cap.check()
    summary = {'status': 'CANDIDATE_VARIABLE_CORE_FACTOR_SIZE_PREFLIGHT', 'independent_verification': 'PENDING',
        'primary_variables': top, 'incidence_variables': 1440, 'matching_edge_variables': 132, 'permutation_variables': 144,
        'AND_products': products_count, 'counter_population': populations, 'counters': sum(populations.values()),
        'variables': enc.top, 'clauses': clauses.count, 'column_cap_quartic_clauses': 77760,
        'new_CNF_written': False, 'solver_calls': 0, 'component_kernel_assumed': False,
        'elapsed_seconds': time.monotonic()-cap.start, 'peak_working_set_bytes': cap.peak_bytes,
        'outputs_sha256': {key(p): digest(p) for p in out.iterdir() if p.is_file()},
        'limitations': ['Only a deterministic actual-encoder size estimate and twelve exact algebra fixtures.',
                       'Target normalization/coverage and every eventual clause require separate independent review.',
                       'No residual D; even a future SAT factor would not resolve the target.']}
    save(out/'summary.json', summary)
    print(json.dumps(summary))


if __name__ == '__main__':
    main()
