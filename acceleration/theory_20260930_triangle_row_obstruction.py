"""Direct exact row-domain contradiction with replayable binary proof tree."""
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

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'acceleration/results/20260930_triangle_partial99/wave154.json'
RAW_SHA = 'e8581587313cf8207799dcf781d8469eb66a699687e023faf0a435000ab9f69b'
GATE = ROOT / 'acceleration/results/20260930_independent_review/triangle_q1_partial99/summary.json'
GATE_SHA = 'bad7ddc51101377b8eaa284c650db8adcee5c261a0717073b90fc9e2347d7594'
START = time.monotonic()


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def save(p, obj):
    p.write_text(json.dumps(obj, indent=2) + '\n', encoding='utf-8')


def solve(n, constraints):
    nodes = []
    def rec(values):
        if time.monotonic() - START > 120 or len(nodes) >= 1000000:
            raise TimeoutError('preregistered time/node bound')
        idx = len(nodes)
        node = {'id': idx, 'forces': []}
        nodes.append(node)
        while True:
            changed = False
            for ci, c in enumerate(constraints):
                ones = sum(values[x] == 1 for x in c['variables'])
                free = [x for x in c['variables'] if values[x] == -1]
                lo, hi = c['lower'], c['upper']
                if ones > hi or ones + len(free) < lo:
                    node.update({'status': 'CONFLICT', 'constraint': ci, 'ones': ones, 'free': len(free)})
                    return None, idx
                forced = 0 if ones == hi else (1 if ones + len(free) == lo else None)
                if forced is not None and free:
                    node['forces'].append({'constraint': ci, 'ones_before': ones, 'free_before': free, 'value': forced})
                    for x in free:
                        values[x] = forced
                    changed = True
            if not changed:
                break
        if -1 not in values:
            node.update({'status': 'SAT', 'assignment': values})
            return values, idx
        scores = [0] * n
        for c in constraints:
            free = [x for x in c['variables'] if values[x] == -1]
            for x in free:
                scores[x] += 1000 // max(1, len(free))
        x = max((x for x in range(n) if values[x] == -1), key=lambda x: (scores[x], -x))
        node.update({'status': 'SPLIT', 'variable': x, 'children': []})
        for value in (0, 1):
            copy = values.copy()
            copy[x] = value
            solution, child = rec(copy)
            node['children'].append({'value': value, 'node': child})
            if solution is not None:
                return solution, idx
        return None, idx
    solution, root = rec([-1] * n)
    return {'status': 'UNSAT' if solution is None else 'SAT', 'assignment': solution, 'root': root, 'nodes': nodes}


def controls():
    choices = []
    for mask in range(1, 8):
        vv = [i for i in range(3) if mask & (1 << i)]
        for lo in range(len(vv) + 1):
            for hi in range(lo, len(vv) + 1):
                choices.append({'variables': vv, 'lower': lo, 'upper': hi})
    count, positive, negative = 0, 0, 0
    for a in choices:
        for b in choices:
            cs = [a, b]
            truth = [v for v in product((0, 1), repeat=3) if all(c['lower'] <= sum(v[i] for i in c['variables']) <= c['upper'] for c in cs)]
            got = solve(3, cs)
            assert (got['status'] == 'SAT') == bool(truth)
            if truth:
                assert tuple(got['assignment']) in truth
                positive += 1
            else:
                negative += 1
            count += 1
    return {'systems': count, 'satisfiable': positive, 'unsatisfiable': negative, 'all_match_complete_eight_assignment_truth_table': True, 'independent_review': False}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    assert sha(RAW) == RAW_SHA and sha(GATE) == GATE_SHA
    sources = [RAW, GATE, Path(__file__), Path(__file__).with_name('theory_20260930_triangle_row_obstruction_spec.md'), ROOT / 'uv.lock', ROOT / 'pyproject.toml']
    save(out / 'manifest.json', {'timestamp': datetime.now(timezone.utc).isoformat(), 'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(), 'command': [sys.executable, *sys.argv], 'working_directory': str(ROOT), 'python': platform.python_version(), 'uv_version': subprocess.check_output(['uv', '--version'], text=True).strip(), 'input_hashes': {str(p.relative_to(ROOT).as_posix()): sha(p) for p in sources}, 'limits': {'seconds': 120, 'nodes': 1000000}, 'status': 'CANDIDATE', 'target_resolution': False, 'target_automorphism_assumed': False})
    save(out / 'controls.json', controls())
    known = json.loads(RAW.read_bytes())['final_adjacency']
    u = 29
    variables = [v for v in range(99) if known[u][v] == -1]
    assert len(variables) == 38 and all(v >= 39 for v in variables)
    index = {v: i for i, v in enumerate(variables)}
    constraints = []
    required_degree = 14 - sum(x == 1 for x in known[u])
    constraints.append({'kind': 'degree', 'vertex': u, 'variables': list(range(len(variables))), 'lower': required_degree, 'upper': required_degree})
    for v in range(3, 27):
        assert all(x != -1 for x in known[v])
        constant = sum(known[u][w] == known[v][w] == 1 for w in range(99))
        bound = 2 - known[u][v] - constant
        vv = [index[w] for w in variables if known[v][w] == 1]
        constraints.append({'kind': 'exact_common', 'pair': [u, v], 'known_common': [w for w in range(99) if known[u][w] == known[v][w] == 1], 'variables': vv, 'lower': bound, 'upper': bound})
    for b, c in combinations(variables, 2):
        common = [w for w in range(99) if w != u and known[b][w] == known[c][w] == 1]
        cap = 1 if known[b][c] == 1 else 2
        if len(common) >= cap:
            assert len(common) == cap
            constraints.append({'kind': 'incompatible_pair', 'pair': [b, c], 'known_edge': known[b][c], 'known_common': common, 'variables': [index[b], index[c]], 'lower': 0, 'upper': 1})
    save(out / 'constraints.json', {'vertex': u, 'variables': variables, 'constraints': constraints, 'raw_matrix_path': RAW.relative_to(ROOT).as_posix(), 'raw_matrix_sha256': RAW_SHA, 'scope': 'Necessary projected constraints for this propagated fixed Wave154 family only.'})
    result = solve(len(variables), constraints)
    save(out / 'proof_tree.json', result)
    summary = {'status': 'CANDIDATE_EMPTY_ROW_DOMAIN' if result['status'] == 'UNSAT' else 'CANDIDATE_FEASIBLE_ROW', 'independent_verification': 'PENDING', 'vertex': u, 'variables': len(variables), 'constraints': len(constraints), 'incompatible_pair_constraints': sum(c['kind'] == 'incompatible_pair' for c in constraints), 'result': result['status'], 'tree_nodes': len(result['nodes']), 'splits': sum(n['status'] == 'SPLIT' for n in result['nodes']), 'conflict_leaves': sum(n['status'] == 'CONFLICT' for n in result['nodes']), 'elapsed_seconds': time.monotonic() - START, 'target_resolution': False, 'limitations': ['Fixed Wave154 partial graph and independently forced zeros only.', 'Producer cannot approve its own discovery; raw constraints and complete proof tree require independent review.'], 'output_hashes': {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(out.iterdir()) if p.is_file()}}
    save(out / 'summary.json', summary)
    print(json.dumps({k: v for k, v in summary.items() if k != 'output_hashes'}))


if __name__ == '__main__':
    main()
