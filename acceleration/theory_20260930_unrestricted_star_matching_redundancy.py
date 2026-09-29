"""Candidate exact local construction and cheap falsification; no solver imports."""
from datetime import datetime, timezone
from functools import lru_cache
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import platform
import random
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'acceleration/results/20260930_unrestricted_star_matching_redundancy/run01'
MODEL = ROOT / 'acceleration/results/20260930_unrestricted_full99_cnf/model.json'
MODEL_SHA = '77089d0a9dd94919bff62aa1e552b758eca061f980524131ad8d1861acce7a8e'
PROOF = ROOT / 'docs/DERIVATION_20260930_UNRESTRICTED_STAR_MATCHING_REDUNDANCY.md'
SEED = 20260930

def h(p):
    obj = sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): obj.update(b)
    return obj.hexdigest()

def write(name, obj):
    p = OUT / name
    with p.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(obj, f, indent=2); f.write('\n')
    return h(p)

def need(condition, message):
    if not condition: raise ValueError(message)

def matching(vertices, allowed):
    @lru_cache(None)
    def visit(mask):
        if not mask: return ()
        i = (mask & -mask).bit_length() - 1
        rest = mask ^ (1 << i)
        for j in range(i + 1, len(vertices)):
            if rest >> j & 1 and allowed(vertices[i], vertices[j]):
                tail = visit(rest ^ (1 << j))
                if tail is not None: return ((vertices[i], vertices[j]),) + tail
        return None
    return visit((1 << len(vertices)) - 1)

def quota(star):
    need(len(star) == 12 and len(set(star)) == 12, 'twelve distinct labels')
    need((0, 2) not in star, 'no self neighbor')
    need(all(a < b and a // 2 != b // 2 for a, b in star), 'scaffold labels')
    degrees = [sum(s in e for e in star) for s in range(14)]
    need(degrees == [1] * 4 + [2] * 10, 'exact fourteen symbol quotas')

def witness(star):
    quota(star)
    left = [e for e in star if not ({0, 2} & set(e))]
    need(len(left) == 10, 'ten residual labels')
    result = matching(left, lambda a, b: not (set(a) & set(b)))
    need(result is not None, 'disjoint-label matching')
    return result

def construct(labels, star, pairs):
    quota(star)
    remaining = {e for e in star if not ({0, 2} & set(e))}
    used = [e for p in pairs for e in p]
    need(len(pairs) == 5 and len(set(used)) == 10 and set(used) == remaining, 'perfect matching coverage')
    need(all(not (set(a) & set(b)) for a, b in pairs), 'disjoint partners')
    index = {p: 15 + i for i, p in enumerate(labels)}
    n = 99
    a = [[0] * n for _ in range(n)]
    def edge(u, v): a[u][v] = a[v][u] = 1
    for s in range(14): edge(0, s + 1)
    for s in range(0, 14, 2): edge(s + 1, s + 2)
    for lab, vertex in index.items():
        for s in lab: edge(vertex, s + 1)
    u = index[(0, 2)]
    for lab in star: edge(u, index[lab])
    for x, y in pairs: edge(index[x], index[y])
    return a, u

def partial_checks(a, u):
    need(len(a) == 99 and all(len(row) == 99 for row in a), '99 shape')
    need(all(type(x) is int and x in (0, 1) for row in a for x in row), 'binary')
    need(all(a[i][i] == 0 for i in range(99)), 'diagonal')
    need(all(a[i][j] == a[j][i] for i, j in combinations(range(99), 2)), 'symmetry')
    rows = [sum(x << j for j, x in enumerate(row)) for row in a]
    need(all(sum(row) <= 14 for row in a), 'partial degree cap')
    for i, j in combinations(range(99), 2):
        need((rows[i] & rows[j]).bit_count() + a[i][j] <= 2, 'partial pair cap')
    neighbors = [i for i in range(99) if a[u][i]]
    need(len(neighbors) == 14, 'center degree')
    need(all(sum(a[x][y] for y in neighbors) == 1 for x in neighbors), 'local seven-edge matching')
    need(all((rows[u] & rows[1 + s]).bit_count() + a[u][1 + s] == 2 for s in range(14)), 'center-inner equalities')

def sample(rng, bits):
    prescribed = [(0, 3), (1, 2), (1, 3)]
    required = [(4, 6)] + [e for e, b in zip(prescribed, bits) if b]
    banned = {(0, 2)} | {e for e, b in zip(prescribed, bits) if not b}
    degrees = [1] * 4 + [2] * 10
    for a, b in required: degrees[a] -= 1; degrees[b] -= 1
    need(min(degrees) >= 0, 'compatible branch quotas')
    stubs = [s for s, d in enumerate(degrees) for _ in range(d)]
    for attempt in range(1, 100001):
        rng.shuffle(stubs)
        extra = [tuple(sorted(stubs[i:i + 2])) for i in range(0, len(stubs), 2)]
        star = required + extra
        if any(a // 2 == b // 2 for a, b in extra) or len(set(star)) != 12 or set(star) & banned: continue
        quota(star)
        return sorted(star), attempt
    raise RuntimeError('sample attempt cap')

def controls(labels):
    k10 = matching(list(range(10)), lambda a, b: True)
    need(k10 is not None, 'K10 known positive')
    need(matching(list(range(10)), lambda a, b: a == 0 or b == 0) is None, 'K1,9 known negative')
    star, _ = sample(random.Random(SEED), [0, 0, 0]); pairs = witness(star)
    a, u = construct(labels, star, pairs); partial_checks(a, u)
    rejected = []
    def reject(name, f):
        try: f()
        except ValueError: rejected.append(name)
        else: raise AssertionError(name + ' accepted')
    reject('missing_star_vertex', lambda: quota(star[:-1]))
    reject('duplicate_matching_endpoint', lambda: construct(labels, star, pairs[:-1] + (pairs[0],)))
    corrupt = [row[:] for row in a]
    lookup = {p: 15 + i for i, p in enumerate(labels)}
    x, y = next((x, y) for x, y in combinations(star, 2) if set(x) & set(y))
    i, j = lookup[x], lookup[y]; corrupt[i][j] = corrupt[j][i] = 1
    reject('overlapping_label_adjacency', lambda: partial_checks(corrupt, u))
    corrupt = [row[:] for row in a]; corrupt[u][u] = 1
    reject('nonzero_diagonal', lambda: partial_checks(corrupt, u))
    return {'K10_positive': True, 'K1_9_negative': True, 'full99_partial_positive': True, 'corruptions_rejected': rejected}

def main():
    start = time.monotonic()
    OUT.mkdir(parents=True, exist_ok=False)
    need(h(MODEL) == MODEL_SHA, 'frozen unrestricted model')
    model = json.loads(MODEL.read_bytes())
    labels = [tuple(p) for p in model['outer_labels']]
    need(len(labels) == 84 and set(labels) == {(a,b) for a,b in combinations(range(14),2) if a//2 != b//2}, 'all outer labels')
    files = [MODEL, PROOF, Path(__file__).resolve(), ROOT / 'uv.lock', ROOT / 'pyproject.toml', ROOT / 'scratch_general_triangle_portfolio.py', ROOT / 'external_conway99_research/attempts/wave149-terwilliger-triple/derivation.md', ROOT / 'external_conway99_research/attempts/wave151-triangle-root-factor/derivation.md', ROOT / 'external_conway99_research/attempts/wave154-triangle-factor-portfolio/derivation.md', ROOT / 'external_conway99_research/attempts/wave171-pq-centered-code/derivation.md']
    write('manifest.json', {'timestamp': datetime.now(timezone.utc).isoformat(), 'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), 'command': [sys.executable, *sys.argv], 'working_directory': str(ROOT), 'python': platform.python_version(), 'seed': SEED, 'resource_wall_seconds': 60, 'sample_limit': 128, 'selection': '32 accepted random-stub quota sets per fixed anchored four-branch pattern, deterministic seed; not exhaustive', 'success': 'All controls reject corruption; every sampled quota set has an exact local matching and raw partial99 cap witness. Universal theorem requires separate written review.', 'inputs_sha256': {p.relative_to(ROOT).as_posix(): h(p) for p in files}})
    calibrated = controls(labels)
    rng = random.Random(SEED)
    records = []
    for name, bits in [('a0',[0,0,0]), ('a1_complement',[0,0,1]), ('a1_cross',[1,0,0]), ('a2_crosses',[1,1,0])]:
        for number in range(32):
            need(time.monotonic() - start < 60, 'wall cap before sample')
            star, attempts = sample(rng, bits); pairs = witness(star)
            a, u = construct(labels, star, pairs); partial_checks(a, u)
            raw_path = None
            if number == 0:
                raw_path = name + '_partial99.json'; write(raw_path, {'known_edge_adjacency': a, 'center': u, 'unknown_entries_interpretation': 'Zeros outside fully specified root scaffold and N(u) are unknown, not asserted absent; all center edges and all N(u) induced edges are fixed.'})
            records.append({'branch': name, 'number': number, 'stub_attempts': attempts, 'star_labels': star, 'matching_labels': pairs, 'raw_fixture': raw_path, 'center_degree': 14, 'center_inner_equalities': 14, 'partial_pair_caps': 4851, 'matching_edges_in_neighborhood': 7})
    write('records.json', records)
    summary = {'status': 'CANDIDATE_UNRESTRICTED_ONE_STAR_MATCHING_REDUNDANCY', 'timestamp': datetime.now(timezone.utc).isoformat(), 'statement': 'Every unrestricted12-outer-neighbor set satisfying the14 center-inner symbol quotas admits an induced7K2 neighborhood and a full99 partial known-edge graph satisfying all pair caps and degree caps.', 'scope': 'One completed star in otherwise unrestricted root scaffold, with optional disjoint-support anchor; no target completion or conditional fixed-family conclusion.', 'independent_verification': None, 'independent_verification_null_reason': 'Discovery and calibration share this producer; independent written/raw review is pending.', 'controls': calibrated, 'sampled_star_sets': len(records), 'unique_sampled_star_sets': len({tuple(map(tuple, r['star_labels'])) for r in records}), 'per_branch': {name: sum(r['branch'] == name for r in records) for name in ['a0','a1_complement','a1_cross','a2_crosses']}, 'stub_pairing_attempts': sum(r['stub_attempts'] for r in records), 'completed_raw_partial_checks': len(records), 'result': 'No one-star obstruction; universal claim remains CANDIDATE pending separate derivation review.', 'wall_seconds': time.monotonic() - start, 'solver_calls': 0, 'overall_search_coverage': 'UNKNOWN; no validated denominator.', 'artifact_hashes': {p.name: h(p) for p in sorted(OUT.iterdir())}, 'limitations': ['Sampled controls are not exhaustive verification.', 'Full99 unknown zero entries are not target nonedges.', 'No novel global constraint beyond target pair equalities is claimed.', 'Additional fixed outer edges and multiple completed stars are outside this redundancy statement.']}
    digest = write('summary.json', summary)
    print(json.dumps({'status': summary['status'], 'sampled': len(records), 'seconds': summary['wall_seconds'], 'summary_sha256': digest}))

if __name__ == '__main__': main()
