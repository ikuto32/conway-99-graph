"""Cheap exact falsification screen for one frozen coefficient transfer; no LP."""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
from tqdm import tqdm
import theory_20260917_triangle_matching as matching

BASE = Path('acceleration/results/20260930_eight_domains/run01')
OLD = Path('acceleration/results/20260917_partial_six_matchings')
CERT = Path('acceleration/results/20260917_six_moment_pdhg/run01/certificates/10000_last.json')


def digest(p):
    return sha256(Path(p).read_bytes()).hexdigest()


def save(p, x):
    with p.open('x', encoding='utf-8') as f:
        json.dump(x, f, indent=2)
        f.write('\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    bindings = {}

    def read(p):
        bindings[p.as_posix()] = digest(p)
        return json.loads(p.read_bytes())

    new, old, cert = read(BASE/'manifest.json'), read(OLD/'manifest.json'), read(CERT)
    tables = [read(BASE/f'domain_{u:02d}.json') for u in range(84)]
    for p in (Path(__file__), Path(matching.__file__), Path('uv.lock')):
        bindings[p.as_posix()] = digest(p)
    save(args.out/'manifest.json', dict(timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        command=[sys.executable, *sys.argv], working_directory=str(Path.cwd()), python=platform.python_version(),
        inputs_sha256=bindings, scope=new['scope'], question='Can the strongest saved six-coordinate coefficient vector exclude the eight-coordinate matching-filtered model after zero-extension?',
        selection='One frozen 10000-last coefficient vector. At each center select first 256 sorted domain masks plus the saved old maximizer embedding. Score each exactly, then descend score/originalID until one necessary-matching survivor is found.',
        success='84 matching survivors whose summed exact column score is >= the exact RHS dot product refute positivity of this transferred support bound, even before complete maximization.',
        failure='Missing survivor or sum below RHS is inconclusive; no feasibility or exclusion follows.',
        limits={'seconds': 120, 'scored_masks_per_center': 257}, numerical_settings='Integer sums only, denominator 1048576; no tolerances.',
        random_seed=None, random_seed_null_reason='Deterministic preselected screen.',
        independent_review=False, LP_ran=False, target_resolution=False))
    save(args.out/'controls.json', matching.controls())
    start = time.monotonic()
    pairs = list(combinations(range(84), 2))
    y = dict(zip(pairs, cert['moment_weight_numerators']))
    oldq = dict(zip(map(tuple, old['unknown_edges_outer']), cert['reciprocity_weight_numerators']))
    edges = list(map(tuple, new['unknown_edges_outer']))
    q = {e: oldq.get(e, 0) for e in edges}
    fixed = set(map(tuple, new['remaining_fixed_K_edges_outer']))
    labels = [(2*a+s, 2*b+t) for a, b in combinations(range(7), 2) for s in (0, 1) for t in (0, 1)]
    known = [set() for _ in range(84)]
    rows = [0]*99
    for v in range(1, 15):
        matching.add(rows, 0, v)
    for v in range(1, 15, 2):
        matching.add(rows, v, v+1)
    for u, pair in enumerate(labels, 15):
        for s in pair:
            matching.add(rows, u, s+1)
    for a, b in fixed:
        known[a].add(b)
        known[b].add(a)
        matching.add(rows, a+15, b+15)
    unknown = {(a+15, b+15) for a, b in edges}
    rhs = [2-len(set(labels[a]) & set(labels[b]))-int((a,b) in fixed) for a,b in pairs]
    dot = sum(y[e]*v for e,v in zip(pairs,rhs))
    records, evaluated, matching_attempts = [], 0, 0
    for u in tqdm(range(84), desc='Frozen-weight falsification screen', unit='center'):
        assert time.monotonic()-start < 120, '120-second screen cap'
        record = tables[u]
        selected_ids = sorted(set(range(min(256, record['domain_size']))) | {record['old_to_new_domain_ids'][cert['first_argmax_original_ids'][u]]})
        scored = []
        for i in selected_ids:
            mask = int(record['domain_masks_hex'][i], 16)
            chosen = set(matching.vertices(mask))
            full = sorted(known[u] | chosen)
            assert len(full) == 12 and not known[u] & chosen
            score = sum(y[e] for e in combinations(full, 2))
            for v in chosen:
                score += y[u,v]+q[u,v] if u < v else -q[v,u]
            scored.append((score, i, mask))
        evaluated += len(scored)
        selected = None
        for score, i, mask in sorted(scored, key=lambda x: (-x[0], x[1])):
            witness = matching.check_star(rows, unknown, u+15, mask)
            matching_attempts += 1
            if witness['matching_count']:
                selected = dict(outer_vertex=u, original_id=i, mask_hex=hex(mask), score_numerator=score, matching=witness)
                break
        if selected is None:
            break
        records.append(selected)
        save(args.out/f'center_{u:02d}.json', selected)
    total = sum(r['score_numerator'] for r in records)
    assert all(digest(p) == h for p,h in bindings.items())
    result = dict(timestamp=datetime.now(timezone.utc).isoformat(), status='CANDIDATE_EXACT_TRANSFER_FALSIFICATION_SCREEN',
        completed_centers=len(records), sampled_local_choices=evaluated, matching_attempts=matching_attempts,
        rhs_dot_numerator=dot, witness_sum_numerator=total, support_bound_upper_numerator=dot-total,
        denominator=cert['denominator'], transferred_positive_bound_refuted=len(records)==84 and total>=dot,
        elapsed_seconds=time.monotonic()-start, records=records, independent_review=False,
        limitations=['This only tests one transferred coefficient vector; no optimization or complete maximization.',
                    'Selected stars need not agree with each other or extend to a graph.',
                    'Matching edges are individually admissible; a simultaneous matching is not claimed valid.'],
        target_resolution=False, output_sha256={p.name:digest(p) for p in args.out.iterdir() if p.is_file()})
    save(args.out/'summary.json', result)
    print(json.dumps({k:v for k,v in result.items() if k not in ('records','output_sha256')}))


if __name__ == '__main__':
    main()
