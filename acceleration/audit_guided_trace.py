"""Independently replay guided-search trades and bind final necessary controls.

Heuristic ranking, discarded neighbors and PRNG choices are not proof evidence.
This checker imports neither the driver nor native generators or solvers.
"""
import argparse
from collections import Counter
import copy
from hashlib import sha256
from itertools import combinations
import json
from math import isfinite
from pathlib import Path
import time

from audit_certificate import full_graph, audit as audit_certificate, require

ROOT = Path(__file__).resolve().parents[1]
LABELS = [(a, b) for a, b in combinations(range(14), 2) if a//2 != b//2]
LABELS.sort(key=lambda pair: (pair[0]//2, pair[1]//2, pair))


def resolve(name):
    path = Path(str(name).replace('\\', '/'))
    return path.resolve() if path.is_absolute() else (ROOT/path).resolve()


def signature(listed):
    full_graph({'overlap_edges_outer_zero_based': listed})
    return frozenset(map(tuple, listed))


def trade_edges(listed):
    require(type(listed) is list and len(listed) == 2, 'Expected two trade edges')
    result = set()
    for pair in listed:
        require(type(pair) is list and len(pair) == 2 and all(type(v) is int for v in pair), 'Invalid edge shape')
        u, v = pair
        require(0 <= u < v < 84, 'Invalid edge endpoints')
        result.add((u, v))
    require(len(result) == 2, 'Repeated trade edge')
    return result


def replay(summary, initial, best):
    require(summary['status'] == 'BOUNDED_GUIDED_SEARCH_FINISHED', 'Search is not finished')
    samples, records = summary['overlap_candidates'], summary['records']
    require(type(samples) is list and samples, 'Missing accepted snapshots')
    current = signature(initial)
    require(signature(samples[0]) == current, 'Initial snapshot differs from source')
    seen = {current}
    accepted = 0
    accepted_iterations = []
    for iteration, record in enumerate(records):
        require(type(record['iteration']) is int and record['iteration'] == iteration, 'Trace iteration mismatch')
        require(type(record['accepted']) is bool, 'Invalid acceptance flag')
        count, choice = record['evaluated_neighbors'], record['chosen_index']
        require(type(count) is int and 0 < count <= summary['manifest']['neighbors_per_iteration'], 'Bad sampled count')
        require(type(choice) is int and 0 <= choice < count <= record['total_legal_trades'], 'Bad sampled choice')
        removed, added = trade_edges(record['removed']), trade_edges(record['added'])
        require(removed <= current and not added & current, 'Recorded trade not applicable to current state')
        degrees = Counter(v for edge in removed for v in edge)
        require(len(degrees) == 4 and set(degrees.values()) == {1}
                and degrees == Counter(v for edge in added for v in edge), 'Trade degree balance fails')
        proposed = (current-removed)|added
        signature([list(e) for e in sorted(proposed)])
        if record['accepted']:
            accepted += 1
            require(accepted < len(samples) and signature(samples[accepted]) == proposed, 'Accepted snapshot mismatches trade')
            require(proposed not in seen, 'Accepted state was already visited')
            current = proposed
            seen.add(current)
            accepted_iterations.append(iteration)
    require(accepted == summary['accepted_moves'] == len(samples)-1, 'Accepted count/snapshot schedule mismatch')
    require(len(records) <= summary['manifest']['iterations'], 'Search exceeds iteration budget')
    require(summary['partial_pair_checks'] == len(samples)*4851, 'Reported partial check count mismatch')
    recorded_evaluations = 1+sum(record['evaluated_neighbors'] for record in records)
    if summary['stop_reason'] in ('ITERATION_LIMIT', 'ARC_CONSISTENT_NECESSARY_CONTROL_FOUND', 'NO_LEGAL_TWO_EDGE_MOVE'):
        require(summary['evaluated_states'] == recorded_evaluations, 'Evaluation count mismatch')
    else:
        require(summary['stop_reason'] == 'SAMPLED_NEIGHBORS_CAPPED_OR_ALREADY_VISITED'
                and 0 <= summary['evaluated_states']-recorded_evaluations <= summary['manifest']['neighbors_per_iteration'],
                'Unexpected stop reason or unrecorded final evaluation count')
    best_edges = signature(best['overlap_edges_outer_zero_based'])
    require(best_edges in seen, 'Best candidate is not an accepted snapshot or initial state')
    require(best['rank'] == summary['best_rank'], 'Best rank files disagree')
    rank = best['rank']
    require(type(rank) is list and len(rank) == 5 and all(type(v) in (int, float) and isfinite(v) for v in rank),
            'Malformed heuristic rank')
    require(rank[0] in (0, 1) and 0 <= rank[1] <= 84 and 0 <= rank[2] <= 84
            and 0 <= rank[3] <= 1 and rank[4] >= 0, 'Heuristic rank range')
    if summary['stop_reason'] == 'ARC_CONSISTENT_NECESSARY_CONTROL_FOUND':
        require(rank[0] == 1, 'Arc stop does not match reported native rank')
    best_snapshot = next(i for i, sample in enumerate(samples) if frozenset(map(tuple, sample)) == best_edges)
    if best_snapshot:
        accepted_records = [record for record in records if record['accepted']]
        require(accepted_records[best_snapshot-1]['rank'] == rank, 'Best rank differs from its accepted record')
    # Quota equality also follows from degree plus pair caps; verify it explicitly.
    quotas = 0
    for sample in samples:
        adj, _ = full_graph({'overlap_edges_outer_zero_based': sample})
        for u in range(84):
            support = {s//2 for s in LABELS[u]}
            counts = Counter(s for v in adj[u+15] if v >= 15 for s in LABELS[v-15])
            for symbol in range(14):
                require(counts[symbol] == 1 if symbol//2 in support else counts[symbol] <= 2, 'Root-label quota violation')
                quotas += 1
    return {'trade_records_replayed': len(records), 'accepted_moves_replayed': accepted,
            'accepted_iteration_indices': accepted_iterations, 'partial_graph_snapshots_checked': len(samples),
            'accepted_snapshot_pair_caps_checked': len(samples)*4851, 'label_quotas_checked': quotas,
            'distinct_accepted_states_including_initial': len(seen), 'best_snapshot_index': best_snapshot,
            'recorded_native_evaluations': summary['evaluated_states']}


def domain_sets(report, live=False):
    require(report['complete_domain_enumeration'] is True, 'Native/Python domain enumeration incomplete')
    rows = report['domains']
    require([row['outer_vertex'] for row in rows] == list(range(84)), 'Domain vertex order incomplete')
    decoded = [[int(mask, 16) for mask in row['domain_masks_hex']] for row in rows]
    require(all(len(set(row)) == len(row) for row in decoded), 'Duplicate native/Python domain mask')
    if live:
        ids = report['propagation']['surviving_domain_ids']
        require(len(ids) == 84, 'Incomplete surviving domain list')
        require(all(len(set(selected)) == len(selected) and all(type(i) is int and 0 <= i < len(row) for i in selected)
                    for row, selected in zip(decoded, ids)), 'Invalid surviving domain IDs')
        return [set(row[i] for i in selected) for row, selected in zip(decoded, ids)]
    return list(map(set, decoded))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--initial', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), 'Audit output must be new')
    started = time.perf_counter()
    sources = {}

    def digest(path):
        path = resolve(path)
        value = sha256(path.read_bytes()).hexdigest()
        name = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix()
        sources[name] = value
        return value

    def load(path):
        digest(path)
        return json.loads(resolve(path).read_bytes())

    def bindings(records):
        for name, expected in records.items():
            require(digest(name) == expected, f'Source/input binding changed: {name}')

    def bound(records, path):
        matches = [value for name, value in records.items() if resolve(name) == resolve(path)]
        require(len(matches) == 1 and matches[0] == digest(path), f'Unbound input: {path}')

    summary, manifest, best = [load(args.run/name) for name in ('summary.json', 'manifest.json', 'best_candidate.json')]
    require(summary['manifest'] == manifest, 'External/embedded manifests differ')
    bindings(manifest['inputs_sha256'])
    bound(manifest['inputs_sha256'], args.initial)
    require(resolve(best['source_manifest']) == resolve(args.run/'manifest.json'), 'Best candidate manifest link differs')
    initial = load(args.initial)['overlap_edges_outer_zero_based']
    trace = replay(summary, initial, best)
    negatives = []
    for name in ('wrong_initial', 'wrong_trade', 'wrong_snapshot', 'wrong_accepted_count'):
        corrupted = copy.deepcopy(summary)
        if name == 'wrong_initial':
            corrupted['overlap_candidates'][0] = copy.deepcopy(summary['overlap_candidates'][-1])
        elif name == 'wrong_trade':
            corrupted['records'][0]['removed'] = copy.deepcopy(corrupted['records'][0]['added'])
        elif name == 'wrong_snapshot':
            corrupted['overlap_candidates'][1] = copy.deepcopy(summary['overlap_candidates'][0])
        else:
            corrupted['accepted_moves'] += 1
        try:
            replay(corrupted, initial, best)
        except ValueError:
            negatives.append(name)
        else:
            raise ValueError(f'Corrupted trace accepted: {name}')
    native = load(args.run/'best_domains_native.json')
    python = load(args.run/'best_domains_python.json')
    domain_audit = load(args.run/'best_domains_audit.json')
    bindings(python['inputs_sha256'])
    bindings(domain_audit['inputs_sha256'])
    bound(python['inputs_sha256'], args.run/'best_candidate.json')
    bound(domain_audit['inputs_sha256'], args.run/'best_candidate.json')
    bound(domain_audit['inputs_sha256'], args.run/'best_domains_python.json')
    require(domain_audit['status'] == 'INDEPENDENT_COMPLETE_STAR_DOMAINS_AND_RECIPROCITY_AUDIT_PASS'
            and domain_audit['complete_domain_enumeration_verified'] is True, 'No complete independent domain audit')
    require(domain_sets(native) == domain_sets(python), 'Native/Python complete domain sets differ')
    require(domain_sets(native, True) == domain_sets(python, True), 'Native/Python surviving domain sets differ')
    statuses = [native['propagation']['status'], python['propagation']['status'], domain_audit['propagation_status']]
    require(len(set(statuses)) == 1, 'Propagation statuses differ')
    require(bool(summary['best_rank'][0]) == (statuses[0] == 'ARC_CONSISTENT_NONEMPTY'), 'Best rank first bit contradicts final domain control')
    native_count = sum(map(len, domain_sets(native)))
    surviving_count = sum(map(len, domain_sets(native, True)))
    exact = audit_certificate(resolve(args.run/'best_candidate.json'), resolve(args.run/'best_ray.json'))
    certificate, prior = load(args.run/'best_ray.json'), load(args.run/'best_ray_audit.json')
    bindings(prior['inputs_sha256'])
    bound(prior['inputs_sha256'], args.run/'best_candidate.json')
    bound(prior['inputs_sha256'], args.run/'best_ray.json')
    require(exact['status'] == prior['status'] == 'INDEPENDENT_INTEGER_FARKAS_AUDIT_PASS'
            and exact['combined_rhs'] == prior['combined_rhs'] == certificate['combined_rhs'], 'Final exact exclusion replay failed')
    digest(Path(__file__))
    digest(ROOT/'acceleration/audit_certificate.py')
    result = {'status': 'INDEPENDENT_GUIDED_TRACE_FINAL_DOMAINS_AND_EXACT_EXCLUSION_AUDIT_PASS',
              **trace, 'trace_corruption_controls_rejected': negatives,
              'native_python_complete_domain_sets_compared': 84, 'complete_star_domains': native_count,
              'native_python_surviving_domain_sets_compared': 84, 'surviving_star_domains': surviving_count,
              'independently_audited_propagation_status': statuses[0],
              'best_candidate_exactly_excluded': True, 'fresh_exact_combined_rhs': exact['combined_rhs'],
              'driver_review': {'heuristic_rank_is_not_proof': True, 'pilot_stop_reason_consistent': True,
                                'latent_final_iteration_stop_label_issue': 'A first nonempty result on the last iteration would retain ITERATION_LIMIT; this pilot stops before its limit.',
                                'latent_initial_edge_order_visited_issue': 'Unsorted initial edges can evade order-dependent visited identity; this pilot has no repeated accepted states.'},
              'heuristic_scores_or_random_selection_recomputed': False,
              'solver_or_producer_imported': False, 'inputs_sha256': sources,
              'elapsed_seconds': time.perf_counter()-started,
              'scope': 'Accepted trace and final domain-set equivalence checked. The final state passes the necessary reciprocity control but is exactly excluded by the independent linear certificate. No discarded-neighbor coverage, full completion, or global Conway claim.'}
    with args.out.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'inputs_sha256'}))


if __name__ == '__main__':
    main()
