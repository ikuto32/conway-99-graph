"""Dynamic exact factor validation and cheap necessary residual screens."""
from datetime import datetime, timezone
from itertools import combinations, product
from pathlib import Path
import argparse
import copy
import json
import platform
import subprocess
import sys
import time
from theory_20260930_eight_full99_cnf import ResourceCap, digest, save

ROOT = Path(__file__).resolve().parents[1]
THEOREM = ROOT/'acceleration/results/20260930_independent_review/triangle_residual60/summary.json'
THEOREM_SHA = '16120b7fe6a2645b9de8cb81e4eb4c9a6852bad0c513e4978fb116effdab7a73'
SPEC = Path(__file__).with_name('theory_20260930_variable_core_residual_screen_spec.md')


def need(condition, message):
    if not condition:
        raise ValueError(message)


def key(p):
    return Path(p).resolve().relative_to(ROOT).as_posix()


def binary_rect(a, height, width, name):
    need(isinstance(a, list) and len(a) == height and all(isinstance(r, list) and len(r) == width for r in a), name+' shape')
    need(all(type(x) is int and x in (0, 1) for r in a for x in r), name+' binary entries')


def validate_factor(c, f, cell_size=12, research=True):
    need(not research or cell_size == 12, 'research core has12vertices per fibre')
    m = cell_size
    need(m >= 2 and m % 2 == 0, 'positive even fibre size')
    n, width = 3*m, m*(m-2)//2
    binary_rect(c, n, n, 'core')
    binary_rect(f, n, width, 'factor')
    need(all(c[i][i] == 0 for i in range(n)) and all(c[i][j] == c[j][i] for i, j in combinations(range(n), 2)), 'core symmetry and diagonal')
    need(all(sum(c[i][j] for j in range(m*g, m*(g+1))) == 1 for i in range(n) for g in range(3)), 'one core neighbor per fibre')
    need(all(sum(row) == m-2 for row in f), 'exact factor row margins')
    need(all(sum(f[i][d] for i in range(m*g, m*(g+1))) == 2 for g in range(3) for d in range(width)), 'factor fibre-column margins')
    for a in range(n):
        for b in range(n):
            expected = m*int(a == b)-c[a][b]-sum(c[a][k]*c[k][b] for k in range(n))+2-int(a//m == b//m)
            need(sum(f[a][d]*f[b][d] for d in range(width)) == expected, 'exact factor Gram at '+str((a, b)))
    return {'status': 'PRODUCER_EXACT_FACTOR_PREREQUISITES_PASS', 'core_shape': [n, n], 'factor_shape': [n, width],
            'Gram_entries_checked': n*n, 'row_margins_checked': n, 'fibre_column_margins_checked': 3*width,
            'component_restriction_used': False, 'independent_approval': False,
            'research_dimensions': bool(research), 'residual_completion_not_claimed': True}


def quota_interval(allowed_count, ones_count, degree):
    need(0 <= ones_count <= allowed_count and degree >= 0, 'quota dimensions')
    return max(0, degree-(allowed_count-ones_count)), min(degree, ones_count)


def compute_screen(c, f, degree):
    n = len(c)
    need(n > 0 and len(f) == n and f, 'nonempty known part')
    width = len(f[0])
    binary_rect(c, n, n, 'screen core')
    binary_rect(f, n, width, 'screen factor')
    need(type(degree) is int and degree >= 0, 'nonnegative residual degree')
    h = [[2-f[i][y]-sum(c[i][j]*f[j][y] for j in range(n)) for y in range(width)] for i in range(n)]
    t = [[sum(f[i][y]*f[i][z] for i in range(n)) for z in range(width)] for y in range(width)]
    negative = [{'coordinate': i, 'vertex': y, 'value': h[i][y]} for i in range(n) for y in range(width) if h[i][y] < 0]
    excessive = [{'pair': [y, z], 'overlap': t[y][z]} for y, z in combinations(range(width), 2) if t[y][z] > 2]
    allowed, decisions = [[] for _ in range(width)], []
    for y, z in combinations(range(width), 2):
        forward = [i for i in range(n) if f[i][z] > h[i][y]]
        reverse = [i for i in range(n) if f[i][y] > h[i][z]]
        permitted = t[y][z] <= 1 and not forward and not reverse
        decisions.append({'pair': [y, z], 'overlap': t[y][z], 'failed_z_column_at_y': forward,
                          'failed_y_column_at_z': reverse, 'allowed': bool(permitted)})
        if permitted:
            allowed[y].append(z)
            allowed[z].append(y)
    degree_shortages, coordinate_shortages, coordinate_bounds = [], [], []
    for y in range(width):
        neighbors = allowed[y]
        if len(neighbors) < degree:
            degree_shortages.append({'vertex': y, 'allowed_neighbors': neighbors, 'available': len(neighbors), 'required': degree})
        for i in range(n):
            ones = [z for z in neighbors if f[i][z]]
            lower, upper = quota_interval(len(neighbors), len(ones), degree)
            item = {'vertex': y, 'coordinate': i, 'allowed_count': len(neighbors), 'available_ones': len(ones),
                    'lower_for_fixed_degree': lower, 'upper_for_fixed_degree': upper, 'required': h[i][y]}
            coordinate_bounds.append(item)
            if h[i][y] < lower or h[i][y] > upper:
                coordinate_shortages.append({**item, 'one_neighbors': ones,
                    'zero_neighbors': [z for z in neighbors if not f[i][z]],
                    'kind': 'LOWER_BOUND_EXCEEDS_DEMAND' if h[i][y] < lower else 'UPPER_BOUND_BELOW_DEMAND'})
    return {'H': h, 'T': t, 'allowed_edges_by_vertex': allowed, 'allowed_pair_decisions': decisions,
        'residual_degree': degree, 'negative_deficits': negative, 'excessive_column_overlaps': excessive,
        'degree_shortages': degree_shortages, 'coordinate_bounds': coordinate_bounds, 'coordinate_shortages': coordinate_shortages,
        'rejection_found': bool(negative or excessive or degree_shortages or coordinate_shortages),
        'rejection_meaning': 'Producer candidate obstruction to completing exactly this supplied factor; independent checking required.',
        'no_rejection_meaning': 'These necessary local bounds passed; no residual feasibility or graph existence is asserted.'}


def reject(call):
    try:
        call()
    except (ValueError, AssertionError, IndexError, TypeError):
        return True
    raise ValueError('deliberate corruption unexpectedly accepted')


def calibrate(out):
    rook = [[int(i != j and (i//3 == j//3 or i % 3 == j % 3)) for j in range(9)] for i in range(9)]
    need(all(sum(row) == 4 for row in rook), 'known rook degree')
    need(all(sum(rook[i][k]*rook[k][j] for k in range(9)) == 2*int(i == j)-rook[i][j]+2
             for i in range(9) for j in range(9)), 'known exact rook SRG identity')
    # Triangle T={0,1,2}; fibres are{3,6},{4,7},{5,8}; no remaining Y.
    x = [3, 6, 4, 7, 5, 8]
    c = [[rook[a][b] for b in x] for a in x]
    empty_f = [[] for _ in x]
    positive = validate_factor(c, empty_f, 2, research=False)
    faults = []
    bad = copy.deepcopy(c)
    bad[0][0] = 1
    faults.append(reject(lambda: validate_factor(bad, empty_f, 2, False)))
    bad = copy.deepcopy(c)
    bad[0][1] ^= 1
    faults.append(reject(lambda: validate_factor(bad, empty_f, 2, False)))
    bad = copy.deepcopy(c)
    for j in range(6):
        bad[0][j] = bad[j][0] = 0
    faults.append(reject(lambda: validate_factor(bad, empty_f, 2, False)))
    faults.append(reject(lambda: validate_factor(c, [[1] for _ in x], 2, False)))
    faults.append(reject(lambda: validate_factor(c, empty_f, 2, True)))
    # A different real split, without retaining a distinguished T, exercises nonempty residual formulas.
    x, y = list(range(3, 9)), [0, 1, 2]
    c = [[rook[a][b] for b in x] for a in x]
    f = [[rook[a][b] for b in y] for a in x]
    d = [[rook[a][b] for b in y] for a in y]
    screen = compute_screen(c, f, 2)
    need(not screen['rejection_found'], 'nonempty known-valid residual screen')
    h_direct = [[sum(rook[a][b]*rook[b][z] for b in y) for z in y] for a in x]
    t_direct = [[sum(rook[a][u]*rook[a][v] for a in x) for v in y] for u in y]
    need(screen['H'] == h_direct and screen['T'] == t_direct, 'literal omitted-neighbor and known-common counts')
    need(screen['allowed_edges_by_vertex'] == [[1, 2], [0, 2], [0, 1]], 'all actual residual edges retained')
    for yy in range(3):
        actual = [z for z in range(3) if d[yy][z]]
        need(all(sum(f[i][z] for z in actual) == screen['H'][i][yy] for i in range(6)), 'actual residual neighborhood solves every demand')
    bad = copy.deepcopy(f)
    bad[0][0] = 2
    faults.append(reject(lambda: compute_screen(c, bad, 2)))
    for field in ('H', 'T'):
        changed = copy.deepcopy(screen[field])
        changed[0][0] += 1
        faults.append(reject(lambda changed=changed, field=field: need(changed == (h_direct if field == 'H' else t_direct), 'changed screen array')))
    changed_allowed = copy.deepcopy(screen['allowed_edges_by_vertex'])
    changed_allowed[0].remove(1)
    faults.append(reject(lambda: need(1 in changed_allowed[0], 'deleted actual residual edge')))
    quota_cases = 0
    for n in range(7):
        for ones, degree in product(range(n+1), repeat=2):
            bits = [1]*ones+[0]*(n-ones)
            actual = {sum(bits[i] for i in subset) for subset in combinations(range(n), degree)}
            lo, hi = quota_interval(n, ones, degree)
            need(actual == set(range(lo, hi+1)), 'complete fixed-cardinality quota range')
            quota_cases += 1
    faults.append(reject(lambda: need(quota_interval(5, 4, 3) == (0, 3), 'wrong quota lower bound')))
    save(out/'rook_triangle_factor_fixture.json', {'full_valid_adjacency': rook, 'known_indices': [3, 6, 4, 7, 5, 8],
        'core': [[rook[a][b] for b in [3, 6, 4, 7, 5, 8]] for a in [3, 6, 4, 7, 5, 8]], 'factor': empty_f,
        'validation': positive, 'limitation': 'Valid small triangle factor with empty Y; not a target-sized factor.'})
    save(out/'rook_nonempty_residual_fixture.json', {'full_valid_adjacency': rook, 'known_indices': x, 'residual_indices': y,
        'core': c, 'factor': f, 'actual_residual_adjacency': d, 'screen': screen,
        'literal_H': h_direct, 'literal_T': t_direct, 'limitation': 'Nonempty valid generic partition of rook9; not the target triangle-factor dimensions.'})
    return {'status': 'PRODUCER_DYNAMIC_RESIDUAL_SCREEN_CALIBRATION_PASS', 'positive_empty_triangle_factor': True,
        'positive_nonempty_generic_residual': True, 'quota_subset_cases': quota_cases,
        'corruptions_rejected': len(faults), 'research_factor_available': False,
        'research_factor_null_reason': 'No accepted36x60research factor is assumed by calibration.',
        'independent_approval': False, 'solver_calls': 0, 'row_domain_searches': 0}


def provenance(args):
    need(digest(THEOREM) == THEOREM_SHA, 'exact residual theorem gate')
    theorem = json.loads(THEOREM.read_bytes())
    need(theorem['status'] == 'INDEPENDENT_TRIANGLE_RESIDUAL60_EQUIVALENCE_PASS', 'approved conditional residual theorem')
    paths = [Path(__file__), SPEC, THEOREM, ROOT/'uv.lock', ROOT/'pyproject.toml',
             ROOT/'acceleration/theory_20260930_eight_full99_cnf.py']
    return {'timestamp': datetime.now(timezone.utc).isoformat(),
        'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        'command': [sys.executable, *sys.argv], 'working_directory': str(ROOT), 'python': platform.python_version(),
        'uv_version': subprocess.check_output(['uv', '--version'], text=True).strip(),
        'inputs_sha256': {key(p): digest(p) for p in paths},
        'residual_theorem_claim': {'id': 'C-TRIANGLE-FACTOR-RESIDUAL60-COMPLETION-EQUIVALENCE', 'revision': 1},
        'limits': {'seconds': 120, 'memory_bytes': 8*1024**3, 'solver_calls': 0, 'row_domain_searches': 0},
        'random_seed': None, 'random_seed_reason': 'Deterministic integer calculations.'}


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='mode', required=True)
    cal = sub.add_parser('calibrate')
    cal.add_argument('--out', type=Path, required=True)
    sc = sub.add_parser('screen')
    for name in ('factor', 'factor-gate', 'out'):
        sc.add_argument('--'+name, type=Path, required=True)
    sc.add_argument('--factor-gate-sha256', required=True)
    args = ap.parse_args()
    cap = ResourceCap()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    manifest = provenance(args)
    save(out/'manifest.json', manifest)
    if args.mode == 'calibrate':
        result = calibrate(out)
    else:
        need(digest(args.factor_gate) == args.factor_gate_sha256, 'exact factor audit identity')
        gate = json.loads(args.factor_gate.read_bytes())
        need(gate['status'] == 'INDEPENDENT_VARIABLE_CORE_FACTOR_SAT_OBJECT_PASS', 'actual independently accepted arbitrary-core factor')
        raw_hash = digest(args.factor)
        direct_binding = gate.get('inputs_sha256', {}).get(key(args.factor)) == raw_hash
        independent_binding = gate.get('independent_factor_sha256') == raw_hash
        need(direct_binding or independent_binding, 'factor bytes bound to actual independent object audit')
        raw = json.loads(args.factor.read_bytes())
        c, f = raw['core_adjacency'], raw['incidence_matrix']
        validation = validate_factor(c, f)
        screen = compute_screen(c, f, 8)
        save(out/'factor_validation.json', validation)
        save(out/'raw_factor_inputs.json', {'core_adjacency': c, 'incidence_matrix': f,
            'input_artifact_sha256': raw_hash, 'independent_factor_gate_sha256': args.factor_gate_sha256})
        save(out/'screen.json', screen)
        result = {'status': 'CANDIDATE_DYNAMIC_RESIDUAL_SCREEN_COMPLETE', 'independent_approval': False,
            'factor_artifact': key(args.factor), 'factor_sha256': raw_hash, 'factor_gate': key(args.factor_gate),
            'factor_gate_sha256': args.factor_gate_sha256, 'accepted_factor_binding': 'inputs_sha256' if direct_binding else 'independent_factor_sha256',
            'factor_prerequisites_validated': True, 'rejection_found': screen['rejection_found'],
            'negative_deficits': len(screen['negative_deficits']), 'excessive_overlaps': len(screen['excessive_column_overlaps']),
            'allowed_undirected_edges': sum(map(len, screen['allowed_edges_by_vertex']))//2,
            'degree_shortages': len(screen['degree_shortages']), 'coordinate_shortages': len(screen['coordinate_shortages']),
            'screen_outcome': 'NECESSARY_OBSTRUCTION_CANDIDATE' if screen['rejection_found'] else 'NO_OBSTRUCTION_FROM_THESE_BOUNDS',
            'residual_feasibility': 'UNKNOWN', 'solver_calls': 0, 'row_domain_searches': 0,
            'limitations': ['A rejection concerns this exact raw factor only and requires independent witness checking.',
                           'No rejection is not residual feasibility or a target graph.', 'No full residual quadratic constraints were solved.']}
    cap.check()
    result.update(timestamp=datetime.now(timezone.utc).isoformat(), elapsed_seconds=time.monotonic()-cap.start,
                  peak_working_set_bytes=cap.peak_bytes, inputs_sha256=manifest['inputs_sha256'],
                  outputs_sha256={key(p): digest(p) for p in sorted(out.iterdir()) if p.is_file()}, target_resolution=False)
    save(out/'summary.json', result)
    print(json.dumps({k: v for k, v in result.items() if k not in ('inputs_sha256', 'outputs_sha256', 'limitations')}))


if __name__ == '__main__':
    main()
