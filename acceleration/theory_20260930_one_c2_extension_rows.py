"""Eleven exact single-row domains relative to a fixed verified 25-row object."""
from datetime import datetime, timezone
from itertools import combinations, product
from pathlib import Path
import argparse
import hashlib
import json
import platform
import subprocess
import sys
import time
from theory_20260930_eight_full99_cnf import ResourceCap
from theory_20260930_triangle_q1_binary_scout import row_solve

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT/'acceleration/results/20260930_triangle_one_c2_row_native_pilot/main/decoded_factor.json'
GATE = ROOT/'acceleration/results/20260930_independent_review/triangle_one_c2_row_sat_object/summary.json'
SCOPE = ROOT/'acceleration/results/20260930_triangle_joint_factor_cnf/scope.json'
PINS = {
    RAW: 'e81ee7f51591ee2de265ddf9d64892fa7bad9fe176502a450cc6db29c304263c',
    GATE: 'e4693a9bb52831e26ecdeb350565123df4cac58917a66db4762ea31e161809b1',
    SCOPE: '51d5f51ba4177d41247239fc2d7a3753b26150e9660960b7452f38e304d731d0',
}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def key(p):
    return Path(p).resolve().relative_to(ROOT).as_posix()


def save(p, obj):
    p.write_text(json.dumps(obj, indent=2)+'\n', encoding='utf-8')


def exact_common(known, u, v, variables):
    assert all(x >= 0 for x in known[v]) and known[u][v] in (0, 1)
    common = [w for w in range(len(known)) if known[u][w] == known[v][w] == 1]
    bound = 2-known[u][v]-len(common)
    return {'kind': 'exact_common', 'pair': [u, v], 'known_common': common,
            'variables': [i for i, w in enumerate(variables) if known[v][w] == 1],
            'lower': bound, 'upper': bound}


def constraints(known, u):
    vv = [v for v in range(99) if known[u][v] == -1]
    assert vv == list(range(39, 99))
    cs = [{'kind': 'degree', 'vertex': u, 'variables': list(range(60)), 'lower': 10, 'upper': 10}]
    for v in range(3, 28):
        cs.append(exact_common(known, u, v, vv))
    for i, j in combinations(range(60), 2):
        a, b = vv[i], vv[j]
        common = [w for w in range(99) if w != u and known[a][w] == known[b][w] == 1]
        bound = 1 if known[a][b] == 1 else 2
        if len(common) >= bound:
            assert len(common) == bound
            cs.append({'kind': 'incompatible_pair', 'pair': [a, b], 'known_edge': known[a][b],
                       'known_common': common, 'variables': [i, j], 'lower': 0, 'upper': 1})
    return vv, cs


def controls(cap):
    choices = []
    for mask in range(1, 8):
        vv = [i for i in range(3) if mask & (1 << i)]
        for lo in range(len(vv)+1):
            for hi in range(lo, len(vv)+1):
                choices.append({'variables': vv, 'lower': lo, 'upper': hi})
    counts = {'SAT': 0, 'UNSAT': 0}
    for a, b in product(choices, repeat=2):
        cs = [a, b]
        truth = [v for v in product((0, 1), repeat=3) if all(c['lower'] <= sum(v[x] for x in c['variables']) <= c['upper'] for c in cs)]
        result = row_solve(3, cs, cap)
        assert result['status'] == ('SAT' if truth else 'UNSAT')
        if truth:
            assert tuple(result['assignment']) in truth
        counts[result['status']] += 1
    toy = [[0]*10 for _ in range(10)]
    for a, b, value in [(0, 1, 1), (0, 2, 1), (1, 2, 1), (1, 4, 1), (1, 6, 1), (1, 9, 1)]:
        toy[a][b] = toy[b][a] = value
    vv = list(range(4, 10))
    for w in vv:
        toy[0][w] = toy[w][0] = -1
    c = exact_common(toy, 0, 1, vv)
    changed = {**c, 'lower': c['lower']+1, 'upper': c['upper']+1}
    disagreements = 0
    for bits in product((0, 1), repeat=6):
        row = toy[0].copy()
        for w, value in zip(vv, bits):
            row[w] = value
        direct = sum(row[w]*toy[1][w] for w in range(10)) == 2-toy[0][1]
        assert direct == (c['lower'] <= sum(bits[i] for i in c['variables']) <= c['upper'])
        disagreements += direct != (changed['lower'] <= sum(bits[i] for i in changed['variables']) <= changed['upper'])
    assert disagreements > 0
    return {'status': 'PRODUCER_EXTENDED_ROW_CONTROLS_PASS', 'row_truth_systems': sum(counts.values()),
            'row_outcomes': counts, 'literal_common_completion_cases': 64,
            'changed_common_bound_detected_cases': disagreements, 'independent_approval': False}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    cap = ResourceCap()
    for p, h in PINS.items():
        assert sha(p) == h
    gate = json.loads(GATE.read_bytes())
    assert gate['status'] == 'INDEPENDENT_TRIANGLE_ONE_C2_ROW_SAT_OBJECT_PASS'
    assert gate['inputs_sha256'][key(RAW)] == PINS[RAW]
    paths = [Path(__file__), Path(__file__).with_name('theory_20260930_one_c2_extension_rows_spec.md'), *PINS,
             ROOT/'uv.lock', ROOT/'pyproject.toml', ROOT/'acceleration/theory_20260930_triangle_q1_binary_scout.py',
             ROOT/'acceleration/theory_20260930_eight_full99_cnf.py']
    save(out/'manifest.json', {'timestamp': datetime.now(timezone.utc).isoformat(),
        'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        'command': [sys.executable, *sys.argv], 'working_directory': str(ROOT), 'python': platform.python_version(),
        'uv_version': subprocess.check_output(['uv', '--version'], text=True).strip(),
        'inputs_sha256': {key(p): sha(p) for p in paths},
        'limits': {'row_seconds': 2, 'row_nodes': 20000, 'rows': 11, 'total_seconds': 120, 'memory_bytes': 8*1024**3},
        'status': 'CANDIDATE_ROW_EXTENSION_TEST', 'scope': 'One fixed Q1 and one fixed C2 row; other rows tested separately.',
        'shared_code': 'Previously calibrated bounded recursion; new exact-common builder includes row27.',
        'random_seed': None, 'random_seed_reason': 'Deterministic exact branching.'})
    save(out/'controls.json', controls(cap))
    raw, scope = json.loads(RAW.read_bytes()), json.loads(SCOPE.read_bytes())
    c = raw['incidence_matrix']
    assert len(c) == 25 and all(len(r) == 60 for r in c)
    core, known = scope['core'], [[0]*99 for _ in range(99)]

    def edge(a, b, value=1):
        known[a][b] = known[b][a] = value

    for a, b in combinations(range(3), 2):
        edge(a, b)
    for g, m in enumerate(core['internal_matchings']):
        for i, j in enumerate(m):
            edge(g, 3+12*g+i)
            edge(3+12*g+i, 3+12*g+j)
    for i, j in enumerate(core['F01']):
        edge(3+i, 15+j)
    for i, j in enumerate(core['F02']):
        edge(3+i, 27+j)
    for i, j in enumerate(core['P12']):
        edge(15+i, 27+j)
    for a in range(25):
        for d in range(60):
            edge(3+a, 39+d, c[a][d])
    for a in range(28, 39):
        for b in range(39, 99):
            edge(a, b, -1)
    for a, b in combinations(range(39, 99), 2):
        edge(a, b, -1)
    neighbors = [{i for i, x in enumerate(row) if x == 1} for row in known]
    failures = [(a, b) for a, b in combinations(range(99), 2)
                if len(neighbors[a] & neighbors[b])+(known[a][b] == 1) > 2]
    assert not failures
    save(out/'raw99.json', {'known_adjacency': known, 'Q1': raw['Q1'], 'fixed_C2_coordinate': 0,
        'fixed_C2_row': c[24], 'factor_input_sha256': PINS[RAW], 'known_one_pair_caps_pass': True,
        'unknown_C2_entries': 660, 'unknown_BB_entries': 1770, 'propagated_assignments_used': 0})
    outcomes = []
    for u in range(28, 39):
        cap.check()
        vv, cs = constraints(known, u)
        tree = row_solve(60, cs, cap)
        if tree['status'] == 'SAT':
            assert all(cn['lower'] <= sum(tree['assignment'][i] for i in cn['variables']) <= cn['upper'] for cn in cs)
        filename = 'row_%02d.json' % u
        save(out/filename, {'vertex': u, 'variables': vv, 'constraints': cs, 'proof': tree})
        outcomes.append({'vertex': u, 'status': tree['status'], 'nodes': len(tree['nodes']),
                         'artifact': key(out/filename), 'sha256': sha(out/filename)})
    summary = {'status': 'CANDIDATE_ELEVEN_ROW_DOMAINS_COMPLETE', 'independent_verification': 'PENDING',
        'attempted_rows': len(outcomes), 'sat_rows': sum(x['status'] == 'SAT' for x in outcomes),
        'unsat_rows': sum(x['status'] == 'UNSAT' for x in outcomes),
        'unknown_rows': sum(x['status'] == 'UNKNOWN' for x in outcomes), 'outcomes': outcomes,
        'fixed_25_row_candidate_exclusion': any(x['status'] == 'UNSAT' for x in outcomes),
        'all_Q1_or_C2_choices_excluded': False, 'joint_C2_feasibility': 'UNKNOWN', 'target_resolution': False,
        'elapsed_seconds': time.monotonic()-cap.start, 'peak_working_set_bytes': cap.peak_bytes,
        'output_hashes': {key(p): sha(p) for p in sorted(out.iterdir()) if p.is_file()}}
    save(out/'summary.json', summary)
    print(json.dumps({k: v for k, v in summary.items() if k not in ('output_hashes', 'outcomes')}))


if __name__ == '__main__':
    main()
