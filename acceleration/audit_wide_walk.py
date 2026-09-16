"""Replay a variable-compression overlap walk using full 99-vertex graph checks.

Every intermediate graph, including unsaved states, is rebuilt by the independent
standard-library certificate checker. Overlap block totals are measured, not
constrained. This validates an E0=0 necessary-condition search and no completion.
"""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import time

from audit_certificate import full_graph, require

ROOT = Path(__file__).resolve().parents[1]


def key(path):
    path = path.resolve()
    return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix()


def edge_set(listed, count):
    require(type(listed) is list and len(listed) == count, 'Wrong edge count')
    result = set()
    for pair in listed:
        require(type(pair) is list and len(pair) == 2 and all(type(v) is int for v in pair), 'Invalid edge')
        u, v = pair
        require(0 <= u < v < 84 and (u, v) not in result, 'Invalid or duplicate edge')
        result.add((u, v))
    return result


def blocks(known):
    return Counter(tuple(sorted((u//4, v//4))) for u, v in known)


def audit(path, initial_path):
    started = time.perf_counter()
    raw = path.read_bytes()
    data = json.loads(raw)
    require(data.get('overlap_block_totals_fixed') is False, 'Expected explicitly variable compression')
    samples, sample_steps, trace = data['overlap_candidates'], data['candidate_steps'], data['trade_trace']
    require(len(samples) == len(sample_steps) > 0, 'Invalid snapshot count')
    require(type(data['steps']) is int and 0 <= len(trace) <= data['steps'], 'Invalid requested step count')
    require(type(data['completed_steps']) is int and data['completed_steps'] == len(trace), 'Invalid trace length')
    require(all(type(step) is int for step in sample_steps) and sample_steps[0] == 0
            and sample_steps[-1] == len(trace) and all(a < b for a, b in zip(sample_steps, sample_steps[1:])),
            'Invalid snapshot steps')
    require(type(data['sample_stride']) is int and data['sample_stride'] > 0, 'Invalid sampling stride')
    schedule = list(range(0, len(trace)+1, data['sample_stride']))
    if schedule[-1] != len(trace):
        schedule.append(len(trace))
    require(sample_steps == schedule, 'Snapshot schedule mismatch')
    expected = {step: edge_set(sample, 168) for step, sample in zip(sample_steps, samples)}
    known = expected[0].copy()
    initial = json.loads(initial_path.read_bytes())['overlap_edges_outer_zero_based']
    require(known == edge_set(initial, 168), 'Initial source differs from walk start')
    labels = [(a, b) for a, b in combinations(range(14), 2) if a//2 != b//2]
    labels.sort(key=lambda pair: (pair[0]//2, pair[1]//2, pair))
    supports = [{s//2 for s in pair} for pair in labels]
    initial_blocks = blocks(known)
    signatures, states = set(), set()
    changes, partial_graphs, own_quotas = 0, 0, 0
    snapshot_records = []
    previous_blocks = initial_blocks
    for step in range(len(trace)+1):
        if step:
            record = trace[step-1]
            require(record['step'] == step, 'Trace step mismatch')
            removed, added = edge_set(record['removed'], 2), edge_set(record['added'], 2)
            require(removed <= known and not (added & known), 'Illegal replacement')
            endpoints = Counter(v for edge in removed for v in edge)
            require(len(endpoints) == 4 and set(endpoints.values()) == {1}
                    and endpoints == Counter(v for edge in added for v in edge), 'Trade changes a degree')
            known.difference_update(removed)
            known.update(added)
        adjacency, unknown = full_graph({'overlap_edges_outer_zero_based': [list(edge) for edge in sorted(known)]})
        require(len(unknown) == 1680, 'Disjoint domain changed')
        partial_graphs += 1
        for u in range(84):
            neighbors = [v-15 for v in adjacency[u+15] if v >= 15]
            require(len(neighbors) == 4, 'Overlap degree is not four')
            for symbol in range(14):
                count = sum(symbol in labels[v] for v in neighbors)
                require(count == 1 if symbol//2 in supports[u] else count <= 2, 'Root-label quota failed')
                own_quotas += 1
        current_blocks = blocks(known)
        if current_blocks != previous_blocks:
            changes += 1
        previous_blocks = current_blocks
        signatures.add(tuple(sorted(current_blocks.items())))
        states.add(tuple(sorted(known)))
        if step in expected:
            require(known == expected[step], 'Snapshot differs from replay')
            delta = sum(abs(current_blocks[pair]-initial_blocks[pair]) for pair in set(current_blocks)|set(initial_blocks))
            snapshot_records.append({'step': step, 'overlap_compression_l1_from_initial': delta,
                                     'edges_changed_from_initial': len(known.symmetric_difference(expected[0]))})
    sources = [path, initial_path, Path(__file__), ROOT/'acceleration/audit_certificate.py',
               ROOT/'acceleration/overlap_wide_walk.rs', ROOT/'acceleration/build/overlap_wide_walk.exe']
    return {'status': 'INDEPENDENT_VARIABLE_COMPRESSION_WALK_AUDIT_PASS',
            'steps_verified': len(trace), 'snapshots_verified': len(samples),
            'full_intermediate_graphs_checked': partial_graphs,
            'partial_pair_caps_checked': partial_graphs*4851, 'label_quotas_checked': own_quotas,
            'distinct_intermediate_states': len(states), 'distinct_overlap_compressions': len(signatures),
            'compression_changing_steps': changes, 'snapshot_records': snapshot_records,
            'overlap_block_totals_fixed': False, 'same_fibre_edges_absent': True,
            'seed': data['seed'], 'requested_steps': data['steps'],
            'legal_alternative_counts_or_rng_selection_rechecked': False,
            'inputs_sha256': {key(p): sha256(p.read_bytes()).hexdigest() for p in sources},
            'elapsed_seconds': time.perf_counter()-started,
            'scope': 'Bounded local E0=0 search across different overlapping compression totals. Every full intermediate 99-vertex partial graph obeys degree, root-label quota and pair caps. No disjoint completion, SRG witness or exhaustive exclusion.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('walk', type=Path)
    parser.add_argument('--initial', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), 'Output already exists')
    result = audit(args.walk, args.initial)
    with args.out.open('x', encoding='utf-8') as output:
        output.write(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('snapshot_records', 'inputs_sha256')}))


if __name__ == '__main__':
    main()
