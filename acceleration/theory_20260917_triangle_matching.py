"""Exact necessary matching test inside each saved completed star.

This producer creates candidate evidence, never independently approves it.
It does not change the definition or IDs of the historical star domains.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
from functools import lru_cache
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def stamp():
    return datetime.now(timezone.utc).isoformat()


def save(path, value):
    with path.open('x', encoding='utf-8') as f:
        json.dump(value, f, indent=2)
        f.write('\n')


def vertices(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask -= bit


def add(rows, a, b):
    rows[a] |= 1 << b
    rows[b] |= 1 << a


def caps(rows):
    return all((rows[a] & rows[b]).bit_count() <= 2 - ((rows[a] >> b) & 1)
               for a, b in combinations(range(len(rows)), 2))


def single_edge_allowed(rows, a, b):
    assert a != b and not (rows[a] >> b) & 1
    if (rows[a] & rows[b]).bit_count() > 1:
        return False
    for x, y in ((a, b), (b, a)):
        for z in vertices(rows[x]):
            if (rows[y] & rows[z]).bit_count() >= 2 - ((rows[y] >> z) & 1):
                return False
    return True


def matchings(nodes, edges):
    """Exact subset recurrence; each unordered perfect matching counted once."""
    position = {v: i for i, v in enumerate(nodes)}
    neighbors = [0] * len(nodes)
    for a, b in edges:
        i, j = position[a], position[b]
        neighbors[i] |= 1 << j
        neighbors[j] |= 1 << i

    @lru_cache(None)
    def count(mask):
        if not mask:
            return 1
        first = mask & -mask
        i = first.bit_length() - 1
        rest = mask ^ first
        return sum(count(rest ^ (1 << j)) for j in vertices(neighbors[i] & rest))

    mask = (1 << len(nodes)) - 1
    number = count(mask)
    witness = []
    if number:
        while mask:
            first = mask & -mask
            i = first.bit_length() - 1
            rest = mask ^ first
            j = next(j for j in vertices(neighbors[i] & rest) if count(rest ^ (1 << j)))
            witness.append([nodes[i], nodes[j]])
            mask = rest ^ (1 << j)
    return number, witness


def check_star(rows, unknown, center, mask):
    graph = rows[:]
    for v in vertices(mask):
        add(graph, center, v + 15)
    n = list(vertices(graph[center]))
    assert len(n) == 14
    forced = [(a, b) for a, b in combinations(n, 2) if (graph[a] >> b) & 1]
    used = [v for e in forced for v in e]
    assert len(set(used)) == len(used), 'Input star already violates its adjacent pair caps'
    free = [v for v in n if v not in used]
    allowed = [(a, b) for a, b in combinations(free, 2)
               if (a, b) in unknown and single_edge_allowed(graph, a, b)]
    number, witness = matchings(free, allowed)
    return dict(forced_edges_full99=forced, unmatched_vertices_full99=free,
                allowed_edges_full99=allowed, matching_count=number,
                matching_witness_full99=witness)


def controls():
    nodes = list(range(1, 15))
    pairs = list(zip(nodes[::2], nodes[1::2]))
    assert matchings(nodes, pairs)[0] == 1
    assert matchings(nodes, pairs[:-1])[0] == 0
    assert matchings(list(range(10)), list(combinations(range(10), 2)))[0] == 945
    windmill = [0] * 15
    for v in nodes:
        add(windmill, 0, v)
    assert caps(windmill)
    assert single_edge_allowed(windmill, 1, 2)
    add(windmill, 1, 2)
    assert not single_edge_allowed(windmill, 1, 3)
    bad = windmill[:]
    add(bad, 1, 3)
    assert not caps(bad)
    for a, b in pairs[1:]:
        add(windmill, a, b)
    assert caps(windmill)
    assert all((windmill[v] & windmill[0]).bit_count() == 1 for v in nodes)
    return {'status': 'PRODUCER_CONTROLS_PASS', 'controls': [
        'prescribed 7-edge matching count1', 'one prescribed matching edge removed count0',
        'K10 matching count945', 'windmill partial caps accept before/after completion',
        'second edge at matched neighbor rejected and corrupted graph caps fail'],
        'independent_verification': False}


def build(candidate):
    labels = [(2*a+s, 2*b+t) for a, b in combinations(range(7), 2)
              for s in range(2) for t in range(2)]
    supports = [{a//2, b//2} for a, b in labels]
    rows = [0] * 99
    for v in range(1, 15):
        add(rows, 0, v)
    for a in range(1, 15, 2):
        add(rows, a, a+1)
    for v, pair in enumerate(labels, 15):
        for symbol in pair:
            add(rows, v, symbol+1)
    edges = candidate['overlap_edges_outer_zero_based']
    assert len(edges) == 168 and len({tuple(e) for e in edges}) == 168
    for a, b in edges:
        assert 0 <= a < b < 84 and len(supports[a] & supports[b]) == 1
        add(rows, a+15, b+15)
    assert Counter(map(int.bit_count, rows)) == {14: 15, 6: 84}
    assert caps(rows)
    unknown = {(a+15, b+15) for a, b in combinations(range(84), 2) if not supports[a] & supports[b]}
    assert len(unknown) == 1680
    return rows, unknown


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--candidate', type=Path, required=True)
    p.add_argument('--domains', type=Path, required=True)
    p.add_argument('--domain-audit', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--seconds', type=float, default=300)
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    paths = [args.candidate, args.domains, args.domain_audit, Path(__file__),
             ROOT/'pyproject.toml', ROOT/'uv.lock']
    manifest = dict(schema_version=1, created_at=stamp(),
        source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        working_directory=str(ROOT), command=['uv', 'run', '--frozen', 'python', '-B']+sys.argv,
        python=sys.version, platform=platform.platform(),
        inputs_sha256={str(x): digest(x) for x in paths},
        question='Does every saved locally admissible star admit a perfect matching inside its final 14-neighborhood?',
        scope='Baseline18481 only; all original complete domains, original IDs retained. Already excluded K used to test a new strengthening.',
        selection_rule='All84 domains, ascending outer vertex and original star ID. No post-outcome selection.',
        success='Any zero matching count proves necessity adds information to original star caps/quotas, pending independent checking.',
        falsification='If all matchings exist, this fixed pilot supplies no strict-strengthening witness.',
        acceptance_threshold='exact integer matching_count == 0',
        resource_limit_seconds=args.seconds, random_seed=None,
        random_seed_reason='Deterministic exact enumeration',
        limitations='Allowed single edges are tested separately; a found matching need not satisfy combined partial caps or extend globally.',
        review_state='CANDIDATE_PENDING_INDEPENDENT_REVIEW')
    save(args.out/'manifest.json', manifest)
    save(args.out/'controls.json', controls())
    domain_data, audit = (json.loads(x.read_bytes()) for x in (args.domains, args.domain_audit))
    bound = audit.get('inputs_sha256', {})
    assert digest(args.domains) in bound.values() and digest(args.candidate) in bound.values()
    assert domain_data['complete_domain_enumeration']
    domains = domain_data['domains']
    assert len(domains) == 84 and all(d['status'] == 'COMPLETE' for d in domains)
    graph, unknown = build(json.loads(args.candidate.read_bytes()))
    started = time.perf_counter()
    summary = []
    for u, row in enumerate(tqdm(domains, desc='Exact neighborhood matching', unit='vertex')):
        assert row['outer_vertex'] == u
        records = []
        for domain_id, mask in enumerate(row['domain_masks_hex']):
            if time.perf_counter()-started > args.seconds:
                save(args.out/'incomplete.json', dict(status='INCOMPLETE', completed_vertex_count=len(summary),
                    current_vertex=u, completed_unsealed_stars=len(records), reason='TIME_CAP', timestamp=stamp()))
                return
            result = check_star(graph, unknown, u+15, int(mask, 16))
            result.update(domain_id=domain_id, mask_hex=mask)
            records.append(result)
        path = args.out/f'vertex_{u:02d}.json'
        save(path, dict(outer_vertex=u, results=records))
        removed = [r['domain_id'] for r in records if not r['matching_count']]
        summary.append(dict(outer_vertex=u, original_choices=len(records),
                            removed_domain_ids=removed,
                            survivor_domain_ids=[r['domain_id'] for r in records if r['matching_count']],
                            output_path=str(path), output_sha256=digest(path)))
    save(args.out/'summary.json', dict(status='COMPLETE_MATCHING_FILTER_CANDIDATE', timestamp=stamp(),
        manifest_sha256=digest(args.out/'manifest.json'), controls_sha256=digest(args.out/'controls.json'),
        vertices=summary, original_choices=sum(r['original_choices'] for r in summary),
        removed_choices=sum(len(r['removed_domain_ids']) for r in summary),
        surviving_choices=sum(len(r['survivor_domain_ids']) for r in summary),
        empty_vertices=[r['outer_vertex'] for r in summary if not r['survivor_domain_ids']],
        elapsed_seconds=time.perf_counter()-started, independent_verification=False,
        unrestricted_resolution='UNKNOWN', overall_search_coverage='UNKNOWN; no validated denominator'))


if __name__ == '__main__':
    main()
