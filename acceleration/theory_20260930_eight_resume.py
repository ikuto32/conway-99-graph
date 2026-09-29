"""Checkpoint-aware continuation of the frozen conditional eight-coordinate domains."""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
from importlib.metadata import version
from itertools import combinations
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time

from tqdm import tqdm
from theory_20260917_partial_matching import add, valid, direct_subset_ok, members, Cap
from theory_20260917_six_coordinate_enumerator import enumerate_star_retained

OLD = Path('acceleration/results/20260917_partial_eight_matchings')
PROTOCOL = Path('docs/NEXT_20260930_EIGHT_COORDINATE_CONTINUATION.md')


def digest(p):
    return sha256(Path(p).read_bytes()).hexdigest()


def read(p):
    return json.loads(Path(p).read_bytes())


def save(p, x):
    with Path(p).open('x', encoding='utf-8') as f:
        json.dump(x, f, indent=2)
        f.write('\n')


def stamp():
    return datetime.now(timezone.utc).isoformat()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    stop = read(OLD / 'STOP_RECORD.json')
    # Original receipt must also be byte-identical to the immutable source commit.
    committed = subprocess.check_output(['git', 'show', '90f1a32de21faea3519c3635677d5739f86ad734:' + (OLD / 'STOP_RECORD.json').as_posix()])
    assert committed == (OLD / 'STOP_RECORD.json').read_bytes()
    bindings = {(OLD / 'STOP_RECORD.json').as_posix(): digest(OLD / 'STOP_RECORD.json')}
    for p, h in stop['artifact_sha256'].items():
        assert digest(p) == h, p
        bindings[Path(p).as_posix()] = h
    old = read(OLD / 'manifest.json')
    for p, h in old['inputs_sha256'].items():
        assert digest(p) == h, p
        bindings[Path(p).as_posix()] = h
    for p in [Path(__file__), PROTOCOL, Path('uv.lock'), Path('acceleration/theory_20260917_six_coordinate_enumerator.py'), Path('acceleration/theory_20260917_partial_matching.py')]:
        bindings[p.as_posix()] = digest(p)
    checkpoint = read(OLD / 'checkpoint_17.json')
    records = []
    for record in checkpoint['completed_centers']:
        p = Path(record['path'])
        assert digest(p) == record['sha256']
        target = args.out / p.name
        shutil.copyfile(p, target)
        records.append({**record, 'path': target.as_posix(), 'reused_from': p.as_posix()})
    assert len(records) == 17 and sum(r['domain_size'] for r in records) == 996947
    labels = [(2*a+s, 2*b+t) for a, b in combinations(range(7), 2) for s in (0, 1) for t in (0, 1)]
    rows = [0]*99
    for v in range(1, 15):
        add(rows, 0, v)
    for v in range(1, 15, 2):
        add(rows, v, v+1)
    for v, pair in enumerate(labels, 15):
        for s in pair:
            add(rows, v, s+1)
    for u, v in old['remaining_fixed_K_edges_outer']:
        add(rows, u+15, v+15)
    assert valid(rows)
    unknown = old['unknown_edges_outer']
    order = old['enumeration_order']
    converted = [[int(x, 16) for x in read(OLD/f'embedding_{u:02d}.json')['new_masks_hex']] for u in range(84)]
    assert sum(map(len, converted)) == 879449
    manifest = {k: old[k] for k in ['domain', 'scope', 'enumeration_order', 'remaining_fixed_K_edges_outer', 'removed_edges_outer', 'freed_legal_matching_edges_outer', 'unknown_edges_outer', 'missing_neighbors']}
    manifest.update(timestamp=stamp(), source_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        command_argv=[sys.executable, *sys.argv], working_directory=str(Path.cwd()), python=platform.python_version(),
        versions={'tqdm': version('tqdm'), 'uv': subprocess.check_output(['uv', '--version'], text=True).strip()},
        inputs_sha256=bindings, resumed_complete_centers=17, resumed_choices=996947,
        limits={'enumeration_seconds': 1800, 'nodes': 300000000, 'per_center_domains': 1000000, 'total_domains': 10000000},
        random_seed=None, random_seed_null_reason='Deterministic exhaustive branching.',
        numerical_settings=None, numerical_settings_null_reason='Exact Python integer bitsets; no floating-point acceptance.',
        hardware={'platform': platform.platform(), 'processor': platform.processor()},
        shared_code='Frozen producer retained-partial enumerator and graph helpers; independent checker required.',
        independent_review=False, LP_ran=False, target_resolution=False)
    save(args.out/'manifest.json', manifest)
    controls = []
    for control in read(OLD/'controls.json')['positive_corrupt_controls']:
        u = control['outer_vertex']
        pool = control['pool']
        budget = dict(deadline=time.monotonic()+60, nodes=0, node_cap=1000000, domain_cap=100000, total_cap=1000000, complete_choices=0)
        actual, _, _ = enumerate_star_retained(rows, labels, unknown, u, budget, dict(masks=[], nodes=0), restricted=set(pool))
        expected = sorted(sum(1 << v for v in subset) for subset in combinations(pool, 14-rows[u+15].bit_count()) if direct_subset_ok(rows, labels, u, subset))
        assert actual == expected == [int(x, 16) for x in control['accepted_masks_hex']] and actual
        corrupt = actual[0] ^ (actual[0] & -actual[0])
        assert not direct_subset_ok(rows, labels, u, list(members(corrupt)))
        controls.append(dict(outer_vertex=u, brute_force_agreement=True, missing_edge_rejected=True, choices=len(actual)))
    save(args.out/'controls.json', {'records': controls, 'independent_verification': False})
    start = time.monotonic()
    budget = dict(deadline=start+1800, nodes=0, node_cap=300000000, domain_cap=1000000, total_cap=10000000, complete_choices=996947)
    complete = {r['outer_vertex'] for r in records}
    incomplete = None
    for u in tqdm([u for u in order if u not in complete], desc='Continue eight-coordinate domains', unit='center'):
        state = dict(masks=[], nodes=0)
        try:
            masks, nodes, candidates = enumerate_star_retained(rows, labels, unknown, u, budget, state)
        except (Cap, KeyboardInterrupt) as exc:
            p = args.out/f'partial_domain_{u:02d}.json'
            save(p, dict(outer_vertex=u, complete=False, domain_masks_hex=[hex(x) for x in sorted(state['masks'])],
                         cap_trigger_mask_hex=hex(state['cap_trigger_mask']) if 'cap_trigger_mask' in state else None,
                         search_nodes=state['nodes'], reason=type(exc).__name__+': '+str(exc)))
            incomplete = dict(outer_vertex=u, path=p.as_posix(), sha256=digest(p), reason=type(exc).__name__+': '+str(exc))
            break
        lookup = {m: i for i, m in enumerate(masks)}
        mapping = [lookup[m] for m in converted[u]]
        assert len(mapping) == len(set(mapping))
        p = args.out/f'domain_{u:02d}.json'
        save(p, dict(outer_vertex=u, domain=old['domain'], status='CANDIDATE_COMPLETE_EIGHT_COORDINATE_DOMAIN',
                     domain_size=len(masks), domain_masks_hex=[hex(m) for m in masks], missing_neighbor_count=14-rows[u+15].bit_count(),
                     allowed_single_neighbors=candidates, search_nodes=nodes, old_to_new_domain_ids=mapping, old_embedded_choices=len(mapping)))
        budget['complete_choices'] += len(masks)
        records.append(dict(outer_vertex=u, domain_size=len(masks), search_nodes=nodes, old_embedded_choices=len(mapping), path=p.as_posix(), sha256=digest(p), reused_from=None))
        save(args.out/f'checkpoint_{len(records):02d}.json', dict(timestamp=stamp(), completed_centers=records, complete_domain_choices=budget['complete_choices'], new_search_nodes=budget['nodes'], elapsed_seconds=time.monotonic()-start))
    for p, h in bindings.items():
        assert digest(p) == h, p
    summary = dict(timestamp=stamp(), status='CANDIDATE_EIGHT_COORDINATE_DOMAIN_CONTINUATION', domain=old['domain'], scope=old['scope'],
                   complete_all_centers=len(records)==84 and incomplete is None, completed_centers=len(records),
                   reused_centers=17, newly_completed_centers=len(records)-17, complete_domain_choices=budget['complete_choices'],
                   old_choices_located_in_complete_domains=sum(r['old_embedded_choices'] for r in records),
                   largest_completed_domain=max(r['domain_size'] for r in records), domains=records, incomplete=incomplete,
                   new_search_nodes=budget['nodes'], enumeration_seconds=time.monotonic()-start,
                   independent_domain_review=False, LP_ran=False, exclusion_claimed=False, target_resolution=False,
                   output_sha256={p.name: digest(p) for p in args.out.iterdir() if p.is_file()})
    save(args.out/'summary.json', summary)
    print(json.dumps({k: v for k, v in summary.items() if k not in ('domains', 'output_sha256')}))


if __name__ == '__main__':
    main()
