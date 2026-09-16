"""Independently replay an overlap trade trace, checking every intermediate graph.

Pair caps need rechecking only for pairs with an endpoint whose adjacency row
changed. Every other pair has both rows and adjacency unchanged. Stored samples
also receive the existing independent full 99-vertex graph check.
"""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scratch_next_overlap_alternatives_farkas_audit import build_graph


def require(condition, message):
    if not condition:
        raise ValueError(message)


def audit(path, compression_path):
    require(not sys.flags.optimize, 'Run without -O: independent snapshot checker uses assertions')
    started = time.perf_counter()
    data = json.loads(path.read_bytes())
    compression = json.loads(compression_path.read_bytes())['C']
    labels = [(a, b) for a, b in combinations(range(14), 2) if a//2 != b//2]
    labels.sort(key=lambda pair: (pair[0]//2, pair[1]//2, pair))
    supports = [{s//2 for s in pair} for pair in labels]

    def edges(listed, expected_count):
        require(type(listed) is list and len(listed) == expected_count, 'Wrong edge count')
        result = set()
        for pair in listed:
            require(type(pair) is list and len(pair) == 2, 'Invalid edge shape')
            u, v = pair
            require(type(u) is int and type(v) is int and 0 <= u < v < 84,
                    'Invalid canonical endpoints')
            require(len(supports[u] & supports[v]) == 1, 'Edge is not of overlap support type')
            result.add((u, v))
        require(len(result) == expected_count, 'Duplicate edge')
        return result

    def blocks(selected):
        return Counter(tuple(sorted((u//4, v//4))) for u, v in selected)

    samples, sample_steps, trace = data['overlap_candidates'], data['candidate_steps'], data['trade_trace']
    require(type(data['completed_steps']) is int and data['completed_steps'] == len(trace),
            'Completed step count mismatch')
    require(type(data['steps']) is int and 0 <= len(trace) <= data['steps'], 'Requested step count mismatch')
    require(len(samples) == len(sample_steps) > 0, 'Snapshot count mismatch')
    require(all(type(s) is int for s in sample_steps) and sample_steps[0] == 0
            and sample_steps[-1] == len(trace), 'Snapshot endpoints mismatch')
    require(all(a < b for a, b in zip(sample_steps, sample_steps[1:])), 'Snapshot steps not increasing')
    require(type(data['sample_stride']) is int and data['sample_stride'] > 0, 'Invalid sample stride')
    expected_steps = list(range(0, len(trace)+1, data['sample_stride']))
    if expected_steps[-1] != len(trace):
        expected_steps.append(len(trace))
    require(sample_steps == expected_steps, 'Snapshot schedule mismatch')
    expected_samples = {step: edges(sample, 168) for step, sample in zip(sample_steps, samples)}
    known = set(expected_samples[0])
    initial_totals = blocks(known)
    compression_checks = 0
    require(len(compression) == 21 and all(len(row) == 21 for row in compression), 'Bad compression dimensions')
    for a, b in combinations(range(21), 2):
        if supports[4*a] & supports[4*b]:
            require(initial_totals[a, b] == compression[a][b], 'Initial compression mismatch')
            compression_checks += 1
    adj, unknown = build_graph({'overlap_edges_outer_zero_based': sorted(known)})
    rows = [sum(1 << v for v in neighbors) for neighbors in adj]
    outer_neighbors = [set(v-15 for v in adj[u+15] if v >= 15) for u in range(84)]
    quota_checks = 0

    def check_vertex(u):
        nonlocal quota_checks
        require(len(outer_neighbors[u]) == 4 and rows[u+15].bit_count() == 6,
                f'Degree mismatch at outer vertex {u}')
        counts = Counter(symbol for v in outer_neighbors[u] for symbol in labels[v])
        for symbol in range(14):
            valid = counts[symbol] == 1 if symbol//2 in supports[u] else counts[symbol] <= 2
            require(valid, f'Label quota mismatch at outer vertex {u}, symbol {symbol}')
            quota_checks += 1

    for u in range(84):
        check_vertex(u)
    snapshots_checked = 1
    incremental_pairs_checked = 0
    unique_states = {tuple(sorted(known))}
    for number, record in enumerate(trace, 1):
        require(record['step'] == number, f'Trace step mismatch at {number}')
        removed, added = edges(record['removed'], 2), edges(record['added'], 2)
        require(removed <= known and not (added & known), f'Invalid edge replacement at {number}')
        old_degrees = Counter(v for edge in removed for v in edge)
        require(len(old_degrees) == 4 and all(count == 1 for count in old_degrees.values()),
                f'Trade does not have four distinct vertices at {number}')
        require(old_degrees == Counter(v for edge in added for v in edge),
                f'Degree balance fails at {number}')
        require(blocks(removed) == blocks(added), f'Compression block balance fails at {number}')
        known.difference_update(removed)
        known.update(added)
        for selected, add in ((removed, False), (added, True)):
            for u, v in selected:
                for a, b in ((u, v), (v, u)):
                    if add:
                        outer_neighbors[a].add(b)
                        rows[a+15] |= 1 << (b+15)
                    else:
                        outer_neighbors[a].remove(b)
                        rows[a+15] &= ~(1 << (b+15))
        changed = set(old_degrees)
        changed_global = {u+15 for u in changed}
        for u in changed:
            check_vertex(u)
        for u in changed_global:
            for v in range(99):
                if v == u or (v in changed_global and v < u):
                    continue
                common = (rows[u] & rows[v]).bit_count()
                cap = 1 if rows[u] & (1 << v) else 2
                require(common <= cap, f'Partial pair cap fails at step {number}, pair {u},{v}')
                incremental_pairs_checked += 1
        unique_states.add(tuple(sorted(known)))
        if number in expected_samples:
            require(known == expected_samples[number], f'Snapshot mismatch at step {number}')
            snapshot_adj, snapshot_unknown = build_graph({'overlap_edges_outer_zero_based': sorted(known)})
            require(unknown == snapshot_unknown, 'Unknown support domain changed')
            require(rows == [sum(1 << v for v in neighbors) for neighbors in snapshot_adj],
                    f'Incremental adjacency disagrees with full graph at step {number}')
            require(blocks(known) == initial_totals, f'Full compression check failed at {number}')
            snapshots_checked += 1
    sources = [path, compression_path, Path(__file__), ROOT/'scratch_next_overlap_alternatives_farkas_audit.py']
    return {
        'status': 'INDEPENDENT_RUST_WALK_TRACE_AND_COMPRESSION_AUDIT_PASS',
        'steps_verified': len(trace), 'snapshots_verified': snapshots_checked,
        'distinct_intermediate_states': len(unique_states),
        'incremental_partial_pair_caps_checked': incremental_pairs_checked,
        'full_snapshot_pair_caps_checked': 4851*snapshots_checked,
        'label_quotas_checked': quota_checks,
        'initial_overlap_compression_entries_checked': compression_checks,
        'degree_and_compression_preserving_trades_checked': len(trace),
        'overlap_edges': 168, 'exposed_graph_edges': 357, 'unknown_disjoint_edges': len(unknown),
        'elapsed_seconds': time.perf_counter()-started,
        'rust_or_walk_producer_imported': False, 'solver_used': False,
        'legal_alternative_counts_or_rng_selection_rechecked': False,
        'inputs_sha256': {str(p.relative_to(ROOT) if p.is_absolute() else p): sha256(p.read_bytes()).hexdigest()
                          for p in sources},
        'scope': 'Every recorded trade preserves degree, overlap compression, label quotas, and all partial graph pair caps; stored snapshots match replay. Does not verify alternative counts or RNG selection. No disjoint completion or Conway existence/exclusion claim.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('trace', type=Path)
    parser.add_argument('--compression', type=Path, default=ROOT/'scratch_resume_integral_compression.json')
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), f'Output already exists: {args.out}')
    result = audit(args.trace, args.compression)
    args.out.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
