"""Independently combine local-star exhaustion and exact ray proofs for wide101.

Only recorded snapshots are covered. No solver or star producer is imported.
At least one failed star is freshly exhausted for every star-covered snapshot;
every other snapshot receives a fresh integer-certificate audit.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import time

from audit_certificate import audit, full_graph, require
from audit_goal_theory_stars import exhaust

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT/'acceleration/results'


def resolve(name):
    path = Path(str(name).replace('\\', '/'))
    return path.resolve() if path.is_absolute() else (ROOT/path).resolve()


def key(path):
    path = path.resolve()
    return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=RESULTS/'20260916_wide101_coverage_audit.json')
    args = parser.parse_args()
    require(not args.out.exists(), 'Coverage output must be new')
    started = time.perf_counter()
    sources = {}

    def digest(path):
        path = resolve(path)
        value = sha256(path.read_bytes()).hexdigest()
        sources[key(path)] = value
        return value

    def load(path):
        path = resolve(path)
        digest(path)
        return json.loads(path.read_bytes())

    def bindings(records):
        for name, expected in records.items():
            require(digest(resolve(name)) == expected, f'Input/source hash mismatch: {name}')

    def bound(records, path):
        path = resolve(path)
        matches = [value for name, value in records.items() if resolve(name) == path]
        require(len(matches) == 1 and matches[0] == digest(path), f'Missing binding: {path}')

    walk_path = RESULTS/'20260916_wide_walk_2000.json'
    walk_audit_path = RESULTS/'20260916_wide_walk_2000_audit.json'
    star_path = RESULTS/'20260916_goal_theory_wide_stars100.json'
    star_audit_path = RESULTS/'20260916_goal_theory_wide_stars100_audit.json'
    historical_summary_path = RESULTS/'20260916_wide_bank/summary.json'
    historical_summary_hash = digest(historical_summary_path)
    walk, walk_audit = load(walk_path), load(walk_audit_path)
    require(walk_audit['status'] == 'INDEPENDENT_VARIABLE_COMPRESSION_WALK_AUDIT_PASS', 'Wrong walk audit status')
    bindings(walk_audit['inputs_sha256'])
    bound(walk_audit['inputs_sha256'], walk_path)
    candidates = walk['overlap_candidates']
    require(len(candidates) == len(walk['candidate_steps']) == 101, 'Expected 101 wide snapshots')
    require(walk['overlap_block_totals_fixed'] is False, 'Expected variable-compression walk')
    # Full semantic validation on all snapshots also rejects duplicate/malformed edges.
    graphs = [full_graph({'overlap_edges_outer_zero_based': edges}) for edges in candidates]
    expected_edges = [set(map(tuple, edges)) for edges in candidates]
    star, star_audit = load(star_path), load(star_audit_path)
    require(star['status'] == 'EXACT_INDEPENDENT_VERTEX_STAR_CONTROLS_COMPLETED', 'Wrong star control status')
    require(star_audit['status'] == 'INDEPENDENT_NONLINEAR_VERTEX_STAR_AUDIT_PASS', 'Wrong star audit status')
    bindings(star['inputs_sha256'])
    bindings(star_audit['inputs_sha256'])
    bound(star['inputs_sha256'], walk_path)
    bound(star_audit['inputs_sha256'], walk_path)
    bound(star_audit['inputs_sha256'], star_path)
    require(sorted(row['snapshot_index'] for row in star['results']) == list(range(1, 101)),
            'Star controls must cover snapshots 1 through 100 exactly once')
    star_rows = {row['snapshot_index']: row for row in star['results']}
    star_indices = star_audit['rejected_snapshot_indices']
    require(len(star_indices) == len(set(star_indices)) == 55, 'Expected 55 independently rejected star snapshots')
    fresh_records = {}
    star_nodes = 0
    for index in sorted(star_indices):
        rows = star_rows[index]['stars']
        require([row['outer_vertex'] for row in rows] == list(range(84)), 'Incomplete star vertex list')
        failed = [row['outer_vertex'] for row in rows
                  if row['status'] == 'LOCAL_STAR_EXHAUSTED' and row['new_neighbors_outer'] is None]
        require(failed, f'No failed star recorded for snapshot {index}')
        outer = min(failed)
        require(any(row['snapshot_index'] == index and row['outer_vertex'] == outer
                    for row in star_audit['independent_exhaustion_details']), 'Missing prior independent star replay')
        answer, nodes, eligible = exhaust(*graphs[index], outer)
        require(answer is None, f'False star exhaustion at snapshot {index}, outer vertex {outer}')
        star_nodes += nodes
        fresh_records[index] = {'snapshot_index': index, 'walk_step': walk['candidate_steps'][index],
                               'method': 'INDEPENDENT_LOCAL_STAR_EXHAUSTION', 'outer_vertex': outer,
                               'ordered_subset_search_nodes': nodes, 'individually_admissible_neighbors': eligible,
                               'control_path': key(star_path), 'prior_audit_path': key(star_audit_path)}

    def certificate(index, candidate_path, certificate_path, audit_path, require_walk_metadata=True):
        require(index not in fresh_records, f'Duplicate coverage for snapshot {index}')
        candidate_path, certificate_path, audit_path = map(resolve, (candidate_path, certificate_path, audit_path))
        candidate, proof, prior = load(candidate_path), load(certificate_path), load(audit_path)
        full_graph(candidate)
        require(set(map(tuple, candidate['overlap_edges_outer_zero_based'])) == expected_edges[index],
                f'Certificate candidate differs from wide snapshot {index}')
        require(resolve(proof['candidate_path']) == candidate_path, 'Certificate candidate path mismatch')
        require(proof['candidate_sha256'] == digest(candidate_path), 'Certificate candidate hash mismatch')
        if require_walk_metadata:
            require(candidate['snapshot_index'] == index and candidate['walk_sha256'] == digest(walk_path),
                    'Candidate metadata differs from walk snapshot')
            if 'walk_path' in candidate:
                require(resolve(candidate['walk_path']) == walk_path, 'Candidate walk path mismatch')
            if 'walk_audit_sha256' in candidate:
                require(candidate['walk_audit_sha256'] == digest(walk_audit_path), 'Candidate walk audit hash mismatch')
            require(proof['producer_sha256'] == digest(ROOT/'acceleration/ray_probe.py'), 'Ray producer source changed')
            require(proof['model_builder_sha256'] == digest(ROOT/'acceleration/linear_probe.py'), 'LP row builder changed')
        require(prior['status'] == 'INDEPENDENT_INTEGER_FARKAS_AUDIT_PASS', 'Missing prior exact audit')
        bindings(prior['inputs_sha256'])
        bound(prior['inputs_sha256'], candidate_path)
        bound(prior['inputs_sha256'], certificate_path)
        require(prior['auditor_sha256'] == digest(ROOT/'acceleration/audit_certificate.py'), 'Prior auditor changed')
        fresh = audit(candidate_path, certificate_path)
        require(fresh['status'] == 'INDEPENDENT_INTEGER_FARKAS_AUDIT_PASS', 'Fresh exact audit failed')
        for field, value in prior.items():
            if field != 'inputs_sha256':
                require(fresh[field] == value, f'Fresh exact audit differs: {field}')
        fresh_records[index] = {'snapshot_index': index, 'walk_step': walk['candidate_steps'][index],
                               'method': 'INDEPENDENT_INTEGER_FARKAS_REPLAY', 'combined_rhs': fresh['combined_rhs'],
                               'candidate_path': key(candidate_path), 'certificate_path': key(certificate_path),
                               'prior_audit_path': key(audit_path), 'group_counts': fresh['group_counts'],
                               'upper_bound_count': fresh['upper_bound_count']}

    certificate(0, ROOT/'scratch_follow_overlap_walk.json', RESULTS/'20260916_walk_highs.json',
                RESULTS/'20260916_walk_highs_audit.json', False)
    for index in (15, 37, 100):
        prefix = RESULTS/f'20260916_wide_probes/candidate_{index}'
        certificate(index, prefix.with_suffix('.json'), prefix.with_name(prefix.name+'_ray.json'),
                    prefix.with_name(prefix.name+'_ray_audit.json'))
    remaining_dir = RESULTS/'20260916_wide_remaining_rays'
    manifest = load(remaining_dir/'manifest.json')
    summary = load(remaining_dir/'summary.json')
    require(summary['status'] == 'COMPLETE' and summary['manifest'] == manifest, 'Incomplete or unbound ray sweep')
    require(resolve(manifest['walk_path']) == walk_path and manifest['walk_sha256'] == digest(walk_path),
            'Ray sweep uses a different walk')
    require(manifest['ray_producer_sha256'] == digest(ROOT/'acceleration/ray_probe.py'), 'Sweep producer hash mismatch')
    remaining = sorted(set(range(101))-set(fresh_records))
    require(len(remaining) == 42 and sorted(manifest['selected_indices']) == remaining,
            'Ray sweep indices do not equal the 42 remaining snapshots')
    require(sorted(row['index'] for row in summary['records']) == remaining, 'Sweep record indices missing/repeated')
    for record in summary['records']:
        certificate(record['index'], record['candidate'], record['certificate'], record['audit'])
    require(sorted(fresh_records) == list(range(101)), 'Snapshot coverage incomplete')
    require(digest(historical_summary_path) == historical_summary_hash, 'Historical summary changed')
    for source in (Path(__file__), ROOT/'acceleration/audit_certificate.py', ROOT/'acceleration/audit_goal_theory_stars.py'):
        digest(source)
    result = {
        'status': 'INDEPENDENT_WIDE_101_SNAPSHOT_COMPLETE_EXCLUSION_AUDIT_PASS',
        'walk_path': key(walk_path), 'stored_snapshots': 101, 'covered_snapshot_indices': list(range(101)),
        'uncovered_snapshot_indices': [], 'overlap_block_totals_fixed': False,
        'freshly_exhausted_local_stars': 55, 'star_search_nodes': star_nodes,
        'freshly_replayed_exact_integer_certificates': 46,
        'snapshot_partial_graphs_checked': 101, 'snapshot_partial_pair_caps_checked': 101*4851,
        'historical_summary_preserved': key(historical_summary_path),
        'records': [fresh_records[i] for i in range(101)], 'inputs_sha256': sources,
        'solver_or_producer_imported': False, 'elapsed_seconds': time.perf_counter()-started,
        'scope': 'Exactly the 101 stored snapshots of this bounded variable-compression walk are independently excluded. This is not coverage of all 2001 intermediate walk states, all overlap compressions, all E0=0 assignments, or Conway99. No global existence or impossibility claim.',
    }
    with args.out.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('records', 'inputs_sha256', 'covered_snapshot_indices')}))


if __name__ == '__main__':
    main()
