"""Small raw-product calibration before optimizing the conditional root8 model.

Own labelled adjacency-set/counting path, no producer imports. This producer's
calibration is not an independent review or a catalogue/model coverage proof.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
from functools import lru_cache
import hashlib
from itertools import combinations, permutations
import json
from pathlib import Path
import subprocess
import sys
import time

from command_deadline import CommandDeadline

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT/'acceleration/results/20261002_rooted8_universal5_product_model02'
MODEL_SHA = 'a2162b5edc4eb68952cc9887156c5d0cd731aaaf9a6b5f94f446174b9d10528b'


def need(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@lru_cache(None)
def canonical(n, mask):
    pairs = list(combinations(range(n), 2))
    original = {pair for bit, pair in enumerate(pairs) if mask >> bit & 1}
    best = None
    for free in permutations(range(2, n)):
        order = (0, 1, *free)
        value = sum(1 << bit for bit, (u, v) in enumerate(pairs)
                    if tuple(sorted((order[u], order[v]))) in original)
        best = value if best is None else min(best, value)
    return best


def count_flags(adj, root, h):
    result = Counter()
    external = sorted(set(range(len(adj))) - set(root))
    pairs = list(combinations(range(h), 2))
    for subset in combinations(external, h-2):
        order = (*root, *subset)
        mask = sum(1 << bit for bit, (u, v) in enumerate(pairs)
                   if order[v] in adj[order[u]])
        result[canonical(h, mask)] += 1
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--seconds', type=float, required=True)
    args = parser.parse_args()
    deadline = CommandDeadline(args.seconds, allocation_reason='Direct Petersen60-root raw product calibration and corrupted coefficient/count controls before optimization')
    start = time.monotonic()
    args.out.mkdir(parents=True, exist_ok=False)
    need(sha(RAW/'model.json') == MODEL_SHA, 'frozen exact model')
    model = json.loads((RAW/'model.json').read_bytes())
    products = json.loads((RAW/'product_rows.json').read_bytes())
    adj = [set() for _ in range(10)]
    for u in range(5):
        for v in [(u+1) % 5, u+5]:
            adj[u].add(v); adj[v].add(u)
        v = (u+2) % 5+5
        adj[u+5].add(v); adj[v].add(u+5)
    need(all(len(neighbors) == 3 for neighbors in adj), 'Petersen regularity')
    need(all(len(adj[u] & adj[v]) == (0 if v in adj[u] else 1)
             for u, v in combinations(range(10), 2)), 'Petersen exact SRG fixture')
    totals = {}
    for h in range(5, 9):
        free = set(range(h-2))
        triples = list(map(set, combinations(free, 3)))
        total = sum(first | second == free for first in triples for second in triples)
        need(total == {5:1, 6:12, 7:30, 8:20}[h], 'ordered subset union total')
        totals[h] = total
    roots = 0; mutations = []
    variables = model['variables']
    for u in range(10):
        for v in range(10):
            if u == v or v in adj[u]:
                continue
            need(not deadline.status()['stop_required'], 'not completed within allocated budget')
            flags = {h:count_flags(adj, (u, v), h) for h in range(5, 9)}
            values = [flags[variable[0]][variable[1]] if isinstance(variable[0], int) else 0 for variable in variables]
            for row in products:
                first, second = row['rooted5_masks']
                target = flags[5][first]*flags[5][second]*(1 if first == second else 2)
                known = sum(coefficient*flags[6][mask] for mask, coefficient in row['known_root6_coefficients'])+(flags[5][first] if first == second else 0)
                lhs = sum(coefficient*values[j] for j, coefficient in row['terms'])+known
                need(lhs == target, 'complete direct raw-product fixture')
                if not mutations:
                    chosen = next((j for j, _ in row['terms'] if values[j]), None)
                    if chosen is not None:
                        changed_coefficient_lhs = sum((coefficient+(j == chosen))*values[j] for j, coefficient in row['terms'])+known
                        need(changed_coefficient_lhs != target, 'actual changed coefficient rejected')
                        changed_values = list(values); changed_values[chosen] += 1
                        changed_count_lhs = sum(coefficient*changed_values[j] for j, coefficient in row['terms'])+known
                        need(changed_count_lhs != target, 'actual changed count rejected')
                        mutations.append(dict(root=[u,v], row_pair=[first,second], variable_index=chosen,
                                              changed_coefficient_residual=changed_coefficient_lhs-target,
                                              changed_count_residual=changed_count_lhs-target))
            roots += 1
    need(roots == 60 and len(mutations) == 1, 'complete fixture population and corruption controls')
    report = dict(status='RAW_ROOTED8_PRODUCT_CALIBRATION_PASS', timestamp=datetime.now(timezone.utc).isoformat(),
                  source_commit=subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
                  command=[sys.executable,*sys.argv], cwd=str(ROOT), elapsed_seconds=time.monotonic()-start,
                  input_sha256={str(path.relative_to(ROOT)):sha(path) for path in [RAW/'model.json',RAW/'product_rows.json',Path(__file__),ROOT/'uv.lock',ROOT/'pyproject.toml']},
                  fixture='srg(10,3,0,1) Petersen; direct unordered free-subset counts at all60 ordered nonedges',
                  rooted_flag_orders=[5,6,7,8], product_rows_per_root=len(products), roots_checked=roots,
                  complete_row_checks=roots*len(products), ordered_union_totals=totals, corruption_controls=mutations,
                  method='Adjacency sets and all free permutations implemented here; no producer imports.',
                  verifier_role='Discovery agent calibration; not independent approval.',
                  limitations='Finite fixture calibration only; no target model derivation, catalogue completeness, optimizer verdict or graph feasibility approval.')
    with (args.out/'summary.json').open('x', encoding='utf8', newline='\n') as stream:
        json.dump(report, stream, indent=2); stream.write('\n')
    print(json.dumps(report), flush=True)


if __name__ == '__main__':
    main()
