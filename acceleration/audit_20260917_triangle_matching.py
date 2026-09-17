"""Independent graph-mutation and edge-subset matching audit; no producer imports."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path
import platform
import sys
import time

from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[1]
SOURCE = '7518ebcec78589fe7f8b068ee7a1dd87e8bf8d42'
PIN = 'c827ac9b54efcbcab0927ed3c105fe2fae73b1d87225adc71221300b2ee27bba'


def require(ok, msg):
    if not ok:
        raise ValueError(msg)


def path(p):
    p = Path(str(p).replace('\\', '/'))
    return p if p.is_absolute() else ROOT/p


def key(p):
    return path(p).resolve().relative_to(ROOT).as_posix()


def digest(p):
    return sha256(path(p).read_bytes()).hexdigest()


def save(p, d):
    with p.open('x', encoding='utf-8') as f:
        json.dump(d, f, indent=2)
        f.write('\n')


def cap_ok(rows):
    return all((rows[a] & rows[b]).bit_count() <= 2-int(bool(rows[a] & (1 << b)))
               for a, b in combinations(range(len(rows)), 2))


def build(candidate):
    labels = sorted([(a, b) for a in range(14) for b in range(a+1, 14) if a//2 != b//2],
                    key=lambda e: (e[0]//2, e[1]//2, e[0], e[1]))
    rows = [0]*99
    def add(a, b):
        require(a != b and not rows[a] & (1 << b), 'known repeated edge')
        rows[a] |= 1 << b; rows[b] |= 1 << a
    for a in range(1, 15):
        add(0, a)
    for a in range(1, 15):
        if a % 2:
            add(a, a+1)
    for u in range(84):
        for s in labels[u]:
            add(u+15, s+1)
    es = candidate['overlap_edges_outer_zero_based']
    require(len(es) == 168 and len(set(tuple(e) for e in es)) == 168, 'overlap count')
    for a, b in es:
        require(0 <= a < b < 84 and len({x//2 for x in labels[a]} & {x//2 for x in labels[b]}) == 1, 'overlap scope')
        add(a+15, b+15)
    unknown = {(a+15, b+15) for a, b in combinations(range(84), 2)
               if not {x//2 for x in labels[a]} & {x//2 for x in labels[b]}}
    require(len(unknown) == 1680 and list(map(int.bit_count, rows)) == [14]*15+[6]*84 and cap_ok(rows), 'known graph')
    return rows, unknown


def permitted(rows, a, b):
    """Mutate both full99 rows; check every pair whose row changed."""
    require(a != b and not rows[a] & (1 << b), 'edge already present')
    original_a, original_b = rows[a], rows[b]
    rows[a] |= 1 << b; rows[b] |= 1 << a
    valid = all((rows[v] & rows[w]).bit_count() <= 2-int(bool(rows[v] & (1 << w)))
                for v in (a, b) for w in range(len(rows)) if w != v)
    rows[a], rows[b] = original_a, original_b
    return valid


def count_by_edge_subsets(nodes, edges):
    """No memoized vertex recurrence: enumerate edge sets of required size."""
    require(len(nodes) % 2 == 0 and len(set(nodes)) == len(nodes), 'matching vertices')
    available = set(nodes)
    require(all(a != b and a in available and b in available for a, b in edges), 'matching edge scope')
    require(len(edges) == len(set(tuple(sorted(e)) for e in edges)), 'matching duplicate edge')
    masks = [(1 << a) | (1 << b) for a, b in edges]
    target = sum(1 << v for v in nodes)
    required = len(nodes)//2
    count = 0
    for selection in combinations(masks, required):
        union = 0
        for edge in selection:
            if edge & union:
                break
            union |= edge
        else:
            require(union == target, 'matching endpoint coverage')
            count += 1
    return count, comb(len(edges), required) if len(edges) >= required else 0


def audit_record(base, unknown, u, mask_text, raw, domain_id):
    require(raw['domain_id'] == domain_id and raw['mask_hex'] == mask_text, 'domain identity')
    mask = int(mask_text, 16)
    require(mask >= 0 and mask < 1 << 84 and mask.bit_count() == 8, 'domain mask')
    center = u+15
    rows = base[:]
    for v in range(84):
        if mask & (1 << v):
            a, b = sorted((center, v+15))
            require((a, b) in unknown, 'star edge scope')
            rows[a] |= 1 << b; rows[b] |= 1 << a
    require(rows[center].bit_count() == 14 and cap_ok(rows), 'completed star partial caps')
    require(all((rows[center] & rows[s]).bit_count() == 2-int(bool(rows[center] & (1 << s)))
                for s in range(1, 15)), 'completed star quotas')
    neighbors = [v for v in range(99) if rows[center] & (1 << v)]
    forced = [[a, b] for a, b in combinations(neighbors, 2) if rows[a] & (1 << b)]
    used = [v for e in forced for v in e]
    require(len(used) == len(set(used)), 'forced neighborhood is not a matching')
    remaining = [v for v in neighbors if v not in used]
    allowed = [[a, b] for a, b in combinations(remaining, 2) if (a, b) in unknown and permitted(rows, a, b)]
    require(forced == raw['forced_edges_full99'] and remaining == raw['unmatched_vertices_full99'] and
            allowed == raw['allowed_edges_full99'], 'reconstructed internal graph differs')
    count, subsets = count_by_edge_subsets(remaining, allowed)
    require(type(raw['matching_count']) is int and count == raw['matching_count'], 'matching count differs')
    witness = raw['matching_witness_full99']
    if count:
        require(len(witness)*2 == len(remaining) and all(e in allowed for e in witness) and
                sorted(v for e in witness for v in e) == remaining, 'invalid witness')
    else:
        require(witness == [], 'witness for exhausted matching graph')
    return dict(matching_count=count, edge_subsets_checked=subsets, removed=count == 0,
                single_edge_candidates_checked=sum((a, b) in unknown for a, b in combinations(remaining, 2)))


def controls():
    records = []
    for name, nodes, edges, expected in [
        ('K4', list(range(4)), list(combinations(range(4), 2)), 3),
        ('K6', list(range(6)), list(combinations(range(6), 2)), 15),
        ('seven_prescribed_pairs', list(range(14)), [(i, i+1) for i in range(0, 14, 2)], 1),
        ('deleted_prescribed_pair', list(range(14)), [(i, i+1) for i in range(0, 12, 2)], 0),
        ('empty_perfect_matching', [], [], 1),
    ]:
        observed, subsets = count_by_edge_subsets(nodes, edges)
        require(observed == expected, 'matching fixture '+name)
        records.append(dict(name=name, expected=expected, observed=observed, edge_subsets_checked=subsets))
    windmill = [0]*15
    for v in range(1, 15):
        windmill[0] |= 1 << v; windmill[v] |= 1
    require(cap_ok(windmill) and permitted(windmill, 1, 2), 'positive single-edge fixture')
    windmill[1] |= 1 << 2; windmill[2] |= 1 << 1
    require(not permitted(windmill, 1, 3), 'corrupted extra matching edge fixture')
    windmill[1] |= 1 << 3; windmill[3] |= 1 << 1
    require(not cap_ok(windmill), 'corrupted full cap fixture')
    records.append(dict(name='windmill_addition_and_corrupt_second_edge', observed='PASS'))
    return records


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--seconds', type=float, default=600)
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    require(not (args.out/'summary.json').exists(), 'preserve completed audit')
    bindings = {key(__file__): digest(__file__), 'uv.lock': digest('uv.lock')}
    def read(p):
        bindings[key(p)] = digest(p)
        return json.loads(path(p).read_bytes())
    summary = read(args.input/'summary.json')
    require(digest(args.input/'summary.json') == PIN, 'unexpected candidate summary')
    manifest = read(args.input/'manifest.json')
    require(summary['manifest_sha256'] == digest(args.input/'manifest.json'), 'manifest binding')
    for f, h in manifest['inputs_sha256'].items():
        require(digest(f) == h, 'producer input changed: '+str(f)); bindings[key(f)] = h
    def argument(flag):
        return manifest['command'][manifest['command'].index(flag)+1]
    candidate = read(argument('--candidate')); domains = read(argument('--domains'))
    fresh = read('acceleration/results/20260917_independent_review/baseline_fresh_domain_replay.json')
    require(fresh['status'] == 'INDEPENDENT_EXACT_PAIR_DOMAIN_AUDIT_PASS' and fresh['complete_used_domains_verified'] is True,
            'fresh independent baseline completeness')
    fb = {key(f): h for f, h in fresh['inputs_sha256'].items()}
    require(fb[key(argument('--domains'))] == digest(argument('--domains')) and
            fb[key(argument('--candidate'))] == digest(argument('--candidate')), 'fresh completeness binding')
    for f, h in fb.items():
        require(digest(f) == h, 'fresh completeness input changed'); bindings[f] = h
    require([r['outer_vertex'] for r in domains['domains']] == list(range(84)) and
            [r['outer_vertex'] for r in summary['vertices']] == list(range(84)), 'full vertex universe')
    base, unknown = build(candidate)
    control_results = controls()
    raw0 = read(args.input/'vertex_00.json')['results'][0]
    corruption = []
    for name in ('wrong_count', 'missing_allowed_edge', 'invalid_witness', 'wrong_domain_id'):
        changed = deepcopy(raw0)
        if name == 'wrong_count': changed['matching_count'] += 1
        if name == 'missing_allowed_edge': changed['allowed_edges_full99'].pop()
        if name == 'invalid_witness': changed['matching_witness_full99'][0] = [0, 1]
        if name == 'wrong_domain_id': changed['domain_id'] += 1
        try:
            audit_record(base, unknown, 0, domains['domains'][0]['domain_masks_hex'][0], changed, 0)
        except ValueError as e:
            corruption.append(dict(name=name, outcome='REJECT', reason=str(e)))
        else:
            raise ValueError('corrupted raw record accepted: '+name)
    started = time.perf_counter()
    reports = []
    for u in tqdm(range(84), desc='Independent matching audit', unit='vertex'):
        output = args.out/f'vertex_{u:02d}.json'
        rawpath = path(summary['vertices'][u]['output_path'])
        require(digest(rawpath) == summary['vertices'][u]['output_sha256'], 'raw vertex hash')
        raw = read(rawpath)
        if output.exists():
            done = json.loads(output.read_bytes())
            require(done['source_sha256'] == digest(__file__) and done['raw_sha256'] == digest(rawpath), 'resume input/source mismatch')
            reports.append(done)
            continue
        require(raw['outer_vertex'] == u, 'raw vertex')
        masks = domains['domains'][u]['domain_masks_hex']
        require(len(masks) == len(raw['results']) == summary['vertices'][u]['original_choices'], 'star population')
        checked = [audit_record(base, unknown, u, m, r, i) for i, (m, r) in enumerate(zip(masks, raw['results']))]
        removed = [i for i, r in enumerate(checked) if r['removed']]
        survivors = [i for i, r in enumerate(checked) if not r['removed']]
        require(removed == summary['vertices'][u]['removed_domain_ids'] and survivors == summary['vertices'][u]['survivor_domain_ids'], 'partition mismatch')
        done = dict(outer_vertex=u, source_sha256=digest(__file__), raw_sha256=digest(rawpath),
                    original_choices=len(checked), removed_domain_ids=removed, survivor_domain_ids=survivors,
                    edge_subsets_checked=sum(r['edge_subsets_checked'] for r in checked),
                    single_edge_candidates_checked=sum(r['single_edge_candidates_checked'] for r in checked), status='PASS')
        save(output, done); reports.append(done)
        if time.perf_counter()-started > args.seconds:
            print(json.dumps(dict(status='CAPPED_RESUMABLE_NO_CLAIM', completed_vertices=len(reports))))
            return
    original = sum(r['original_choices'] for r in reports)
    removed = sum(len(r['removed_domain_ids']) for r in reports)
    surviving = sum(len(r['survivor_domain_ids']) for r in reports)
    empty = [r['outer_vertex'] for r in reports if not r['survivor_domain_ids']]
    require((original, removed, surviving, empty) == (summary['original_choices'], summary['removed_choices'], summary['surviving_choices'], summary['empty_vertices']), 'summary counts')
    require(all(digest(f) == h for f, h in bindings.items()), 'evidence changed')
    save(args.out/'summary.json', dict(status='INDEPENDENT_EXACT_TRIANGLE_MATCHING_FILTER_PASS',
        claim_binding=dict(id='C-STAR-TRIANGLE-FILTER-18481', revision=1,
            statement='Of the 26250 complete original baseline18481 star choices, exactly6756 have no perfect matching in the individually permissible internal-neighborhood graph;19494 survive and every outer vertex retains choices.',
            recommendation='VERIFIED', scope='Only the named fixed assignment and its complete original star domains; no additional fixed-K or unrestricted exclusion'),
        timestamp=datetime.now(timezone.utc).isoformat(), source_commit=SOURCE, command=[sys.executable]+sys.argv,
        working_directory=str(Path.cwd()), python=platform.python_version(), inputs_sha256=bindings,
        vertex_reports_sha256={key(args.out/f'vertex_{u:02d}.json'): digest(args.out/f'vertex_{u:02d}.json') for u in range(84)},
        original_choices=original, removed_choices=removed, surviving_choices=surviving, empty_vertices=empty,
        edge_subsets_checked=sum(r['edge_subsets_checked'] for r in reports),
        single_edge_candidates_checked=sum(r['single_edge_candidates_checked'] for r in reports),
        controls=control_results, corrupted_raw_controls=corruption, producer_imported=False,
        checking_path='Full99 bitset adjacency independently rebuilt; actual edge mutation checks all endpoint pairs; perfect matchings exhaust fixed-size edge subsets',
        shared_trusted_components=['Python standard library', 'tqdm progress only', 'raw original domain artifact and fresh prior complete-domain audit'],
        limitations=['Permitted edges are individually admissible only; surviving matching may fail simultaneous cap tests or global extension.',
                    'The fixed baseline assignment was already excluded; filter removes local choices, not additional unrestricted graphs.',
                    'No nontrivial automorphism assumed; prescribed root labels and fixed absent overlap/same-fiber edges remain assumptions.'],
        elapsed_seconds=time.perf_counter()-started, target_resolution='UNKNOWN',
        overall_search_coverage='UNKNOWN; no validated denominator'))
    print(json.dumps(dict(status='INDEPENDENT_EXACT_TRIANGLE_MATCHING_FILTER_PASS', original=original, removed=removed, surviving=surviving)))


if __name__ == '__main__':
    main()
