"""Independently replay a bounded initial-pair-support guided overlap search.

Imports only the full-graph validator, never the search driver, neighbor
generator, native enumerator or CUDA scorer. Every persisted proposal receives
a complete 99-vertex partial-graph check. Rank bookkeeping is replayed but its
heuristic values, sampling optimality and global coverage are not certified.
"""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from math import isfinite, log1p
from pathlib import Path
import time

from audit_certificate import full_graph, require

ROOT = Path(__file__).resolve().parents[1]
LABELS = [(2*a+s, 2*b+t) for a, b in combinations(range(7), 2)
          for s in range(2) for t in range(2)]


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def resolve(name):
    path = Path(str(name).replace('\\', '/'))
    return path.resolve() if path.is_absolute() else (ROOT/path).resolve()


def path_key(path):
    path = path.resolve()
    return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix()


def integer(value, minimum=0):
    return type(value) is int and value >= minimum


def edges(listed, count):
    require(type(listed) is list and len(listed) == count, 'Wrong edge count')
    result = set()
    for pair in listed:
        require(type(pair) is list and len(pair) == 2 and all(type(v) is int for v in pair), 'Bad edge')
        u, v = pair
        require(0 <= u < v < 84 and (u, v) not in result, 'Invalid or repeated edge')
        result.add((u, v))
    return result


def checked_graph(listed):
    known = edges(listed, 168)
    adjacency, unknown = full_graph({'overlap_edges_outer_zero_based': listed})
    require(len(unknown) == 1680, 'Unexpected disjoint-edge domain')
    for u in range(84):
        counts = Counter(symbol for v in adjacency[u+15] if v >= 15 for symbol in LABELS[v-15])
        support = {symbol//2 for symbol in LABELS[u]}
        for symbol in range(14):
            require(counts[symbol] == 1 if symbol//2 in support else counts[symbol] <= 2,
                    f'Root-label quota mismatch at {u},{symbol}')
    return known


def trade_from(known, trade):
    removed, added = edges(trade['removed'], 2), edges(trade['added'], 2)
    require(removed <= known and not (added & known), 'Trade removes absent or adds present edges')
    endpoints = Counter(v for edge in removed for v in edge)
    require(len(endpoints) == 4 and set(endpoints.values()) == {1}
            and endpoints == Counter(v for edge in added for v in edge), 'Trade does not preserve four endpoint degrees')
    return known-removed | added


def rank(value):
    require(type(value) is list and len(value) == 4, 'Wrong heuristic rank shape')
    require(all(integer(v) for v in value[:2]) and 0 <= value[1] <= value[0] <= 84, 'Invalid vertex counts in rank')
    require(all(type(v) in (int, float) and isfinite(v) for v in value[2:]), 'Nonfinite heuristic rank')
    require(0 <= value[2] <= 1 and value[3] >= 0, 'Invalid fraction or domain mass')
    return value


def compression(known):
    return tuple(sorted(Counter(tuple(sorted((u//4, v//4))) for u, v in known).items()))


def audit(directory, initial_path):
    started = time.perf_counter()
    manifest_path, summary_path = directory/'manifest.json', directory/'summary.json'
    manifest, summary = (json.loads(p.read_bytes()) for p in (manifest_path, summary_path))
    require(summary.get('status') == 'BOUNDED_INITIAL_PAIR_SUPPORT_SEARCH_FINISHED', 'Search has not finished')
    require(summary['manifest'] == manifest, 'Embedded manifest mismatch')
    require(integer(manifest['iterations'], 1) and integer(manifest['neighbors_per_iteration'], 1), 'Invalid finite search budget')
    require(type(manifest['seed']) is int, 'Invalid random seed')
    source_paths = {}
    for name, expected in manifest['inputs_sha256'].items():
        path = resolve(name)
        require(path not in source_paths and digest(path) == expected, f'Stale or repeated source hash: {name}')
        source_paths[path] = expected
    require(initial_path.resolve() in source_paths, 'Initial candidate is not bound by the manifest')
    initial_data = json.loads(initial_path.read_bytes())
    initial = checked_graph(initial_data['overlap_edges_outer_zero_based'])
    current = initial.copy()
    current_rank = rank(summary['initial_rank'])
    best, best_rank = initial.copy(), current_rank
    records, snapshots = summary['records'], summary['overlap_candidates']
    require(type(records) is list and len(records) <= manifest['iterations'], 'Too many search iterations')
    require(type(snapshots) is list and snapshots and edges(snapshots[0], 168) == initial, 'Wrong initial snapshot')
    proposal_files = sorted((directory/'proposals').glob('iteration_*.json'))
    require(len(proposal_files) in (len(records), len(records)+1), 'Proposal/record count mismatch')
    if summary['stop_reason'] == 'ITERATION_LIMIT':
        require(len(records) == manifest['iterations'] and len(proposal_files) == len(records), 'Iteration-limit accounting mismatch')
    else:
        require(summary['stop_reason'] in ('NO_LEGAL_TWO_EDGE_MOVE', 'SAMPLED_NEIGHBORS_CAPPED_OR_VISITED')
                and len(proposal_files) == len(records)+1, 'Invalid terminal proposal record')
    accepted, proposed_count, recorded_choices = 0, 0, 0
    graph_checks = 1
    proposal_bindings = {}
    accepted_states = {tuple(sorted(initial))}
    compressions = {compression(initial)}
    for iteration, proposal_path in enumerate(proposal_files):
        require(proposal_path.name == f'iteration_{iteration:04d}.json', 'Proposal sequence gap')
        proposal = json.loads(proposal_path.read_bytes())
        listed, trades = proposal['overlap_candidates'], proposal['trades']
        require(type(listed) is list and type(trades) is list and len(listed) == len(trades), 'Proposal/trade count mismatch')
        require(integer(proposal['legal_trades']) and integer(proposal['sample_limit'], 1)
                and proposal['sample_limit'] == manifest['neighbors_per_iteration']
                and len(listed) == min(proposal['sample_limit'], proposal['legal_trades']), 'Proposal sample size mismatch')
        require(integer(proposal['seed']) and proposal['seed'] < 2**64, 'Invalid proposal seed')
        candidates = []
        for candidate, trade in zip(listed, trades):
            observed = checked_graph(candidate)
            graph_checks += 1
            require(observed == trade_from(current, trade), f'Proposal differs from its trade at iteration {iteration}')
            candidates.append(observed)
        require(len({tuple(sorted(candidate)) for candidate in candidates}) == len(candidates), 'Duplicate proposed graph')
        proposed_count += len(candidates)
        proposal_bindings[path_key(proposal_path)] = digest(proposal_path)
        if iteration == len(records):
            if summary['stop_reason'] == 'NO_LEGAL_TWO_EDGE_MOVE':
                require(not candidates, 'No-move stop has proposed candidates')
            else:
                require(candidates, 'Capped/visited stop requires an evaluated proposal batch')
            continue
        record = records[iteration]
        require(record['iteration'] == iteration and record['native_sample_seed'] == proposal['seed'], 'Iteration/seed mismatch')
        require(resolve(record['proposal_path']) == proposal_path.resolve()
                and record['proposal_sha256'] == digest(proposal_path), 'Chosen-record proposal hash mismatch')
        require(record['total_legal_trades'] == proposal['legal_trades']
                and record['evaluated_neighbors'] == len(candidates), 'Recorded proposal size mismatch')
        choice = record['chosen_index']
        require(integer(choice) and choice < len(candidates), 'Invalid chosen candidate')
        require(edges(record['removed'], 2) == edges(trades[choice]['removed'], 2)
                and edges(record['added'], 2) == edges(trades[choice]['added'], 2), 'Chosen trade mismatch')
        recorded_choices += 1
        quality = rank(record['rank'])
        require(type(record['accepted']) is bool, 'Invalid acceptance flag')
        if not record['accepted']:
            require(quality < current_rank, 'Driver rejected a nondecreasing heuristic rank')
            continue
        current, current_rank = candidates[choice], quality
        signature = tuple(sorted(current))
        require(signature not in accepted_states, 'Accepted a previously visited graph')
        accepted_states.add(signature)
        compressions.add(compression(current))
        accepted += 1
        require(accepted < len(snapshots) and edges(snapshots[accepted], 168) == current, 'Accepted snapshot differs from replay')
        if quality > best_rank:
            best, best_rank = current.copy(), quality
    require(len(snapshots) == accepted+1 and summary['accepted_moves'] == accepted, 'Accepted-move accounting mismatch')
    require(summary['evaluated_states'] == proposed_count+1, 'Evaluated-state count differs from persisted proposals')
    require(integer(summary['capped_states']) and summary['capped_states'] <= summary['evaluated_states'], 'Invalid cap counter')
    require(rank(summary['best_rank']) == best_rank, 'Best-rank bookkeeping mismatch')
    best_path = directory/'best_candidate.json'
    best_data = json.loads(best_path.read_bytes())
    require(checked_graph(best_data['overlap_edges_outer_zero_based']) == best, 'Best candidate is not the replayed best accepted state')
    graph_checks += 1
    require(rank(best_data['initial_pair_support_rank']) == best_rank
            and resolve(best_data['source_manifest']) == manifest_path.resolve(), 'Best-candidate provenance mismatch')
    domains_path, gpu_path = directory/'best_domains_native.json', directory/'best_gpu_summary.json'
    domain_data, gpu = (json.loads(p.read_bytes()) for p in (domains_path, gpu_path))
    require(domain_data['complete_domain_enumeration'] is True
            and [row['outer_vertex'] for row in domain_data['domains']] == list(range(84)), 'Retained best domains are incomplete')
    require(all(row['status'] == 'COMPLETE' and row['cap_reason'] is None for row in domain_data['domains']), 'Retained best domain cap')
    sizes = [len(row['domain_masks_hex']) for row in domain_data['domains']]
    live = gpu['initial_pair_supported_domain_counts']
    require(gpu['domain_counts'] == sizes and len(live) == 84
            and all(integer(value) and value <= size for value, size in zip(live, sizes)), 'Retained best CUDA count mismatch')
    recomputed_rank = [sum(size > 0 for size in sizes), sum(size > 0 for size in live),
                       sum(live)/max(1, sum(sizes)), sum(log1p(size) for size in sizes)]
    require(recomputed_rank == best_rank, 'Retained best rank formula differs')
    artifacts = [initial_path, manifest_path, summary_path, best_path, domains_path, gpu_path,
                 Path(__file__), Path(__file__).with_name('audit_certificate.py')]
    return {'status': 'INDEPENDENT_GUIDED_PAIR_PROPOSALS_AND_TRACE_AUDIT_PASS',
            'persisted_proposal_batches_checked': len(proposal_files), 'all_proposed_graphs_checked': proposed_count,
            'full_99_vertex_graph_checks': graph_checks, 'partial_pair_caps_checked': graph_checks*4851,
            'root_label_quotas_checked': graph_checks*84*14, 'recorded_choices_checked': recorded_choices,
            'accepted_trades_replayed': accepted, 'accepted_snapshots_matched': len(snapshots),
            'distinct_accepted_states': len(accepted_states), 'distinct_accepted_compressions': len(compressions),
            'best_candidate_matches_replay': True, 'recorded_rank_bookkeeping_replayed': True,
            'retained_best_rank_formula_recomputed': True, 'heuristic_score_values_independently_verified': False,
            'complete_star_domains_independently_reenumerated': False, 'native_sampling_or_rng_replayed': False,
            'all_legal_trade_counts_recomputed': False, 'cap_counter_independently_recomputed': False,
            'all_initial_and_proposed_graphs_checked': True, 'exhaustive_search_claim': False,
            'manifest_source_sha256_verified': {path_key(path): value for path, value in source_paths.items()},
            'inputs_sha256': {path_key(path): digest(path) for path in artifacts} | proposal_bindings,
            'elapsed_seconds': time.perf_counter()-started,
            'scope': 'Every stored sampled candidate and accepted state is a valid E0=0 partial graph, every proposed two-edge trade and accepted snapshot matches replay, and the saved best follows recorded heuristic ranks. No heuristic optimality, exhaustive coverage, full arc consistency or graph-completion claim.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory', type=Path, required=True)
    parser.add_argument('--initial', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), 'Preserve existing audit')
    result = audit(args.directory, args.initial)
    with args.out.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('inputs_sha256', 'manifest_source_sha256_verified')}))


if __name__ == '__main__':
    main()
