"""Bounded Rust/CUDA guided search using initial exact pair-support scores.

Initial pair support is only one filtering round, not full arc consistency or
a simultaneous completion. All scores remain heuristic until independently
audited. Accepted overlap states receive separate full-graph validation.
"""
import argparse
import json
from math import log1p
from pathlib import Path
import random
import struct
import time

from audit_certificate import full_graph, require
from guided_overlap import digest, write_json, write_input, invoke
from prepare import path_key

ROOT = Path(__file__).resolve().parents[1]


def signature(edges):
    return tuple(sorted(map(tuple, edges)))


def export_pair_input(path, candidates, results):
    """Little-endian C99PAIR1 with exact full-neighborhood bit rows."""
    require(len(candidates) == len(results), 'Candidate/domain count mismatch')
    with path.open('wb') as stream:
        stream.write(b'C99PAIR1')
        stream.write(struct.pack('<I', len(candidates)))
        for edges, result in zip(candidates, results):
            require(result['complete_domain_enumeration'], 'Cannot score incomplete domains')
            adj, _ = full_graph({'overlap_edges_outer_zero_based': edges})
            domains = result['domains']
            require([row['outer_vertex'] for row in domains] == list(range(84)), 'Domain order mismatch')
            stream.write(struct.pack('<84I', *(len(row['domain_masks_hex']) for row in domains)))
            for u, row in enumerate(domains):
                fixed = sum(1 << v for v in adj[u+15])
                for mask in row['domain_masks_hex']:
                    star = int(mask, 16)
                    require(star >= 0 and star.bit_length() <= 84 and star.bit_count() == 8, 'Invalid star mask')
                    bits = fixed | (star << 15)
                    require(bits.bit_count() == 14, 'Invalid complete neighborhood degree')
                    stream.write(struct.pack('<QQ', bits & ((1 << 64)-1), bits >> 64))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--initial', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--iterations', type=int, default=40)
    parser.add_argument('--neighbors', type=int, default=32)
    parser.add_argument('--seed', type=int, default=20260917)
    parser.add_argument('--gpu', type=Path, default=ROOT/'acceleration/build/star_pair_gpu.exe')
    args = parser.parse_args()
    require(0 < args.iterations <= 1000 and 0 < args.neighbors <= 1000, 'Invalid finite budget')
    require(not args.out.exists(), 'Preserve existing search output')
    args.out.mkdir(parents=True)
    scratch = args.out/'work'
    scratch.mkdir()
    proposal_dir = args.out/'proposals'
    proposal_dir.mkdir()
    native = ROOT/'acceleration/build/star_domains_batch.exe'
    neighbors = ROOT/'acceleration/build/overlap_neighbors.exe'
    sources = [Path(__file__), args.initial, native, neighbors, args.gpu,
               ROOT/'acceleration/guided_overlap.py', ROOT/'acceleration/audit_certificate.py',
               ROOT/'acceleration/prepare.py',
               ROOT/'acceleration/star_domains_batch.rs', ROOT/'acceleration/star_domains.rs',
               ROOT/'acceleration/overlap_neighbors.rs', ROOT/'acceleration/star_pair_gpu.cu']
    bound = {path_key(path): digest(path) for path in sources}
    manifest = dict(inputs_sha256=bound, seed=args.seed, iterations=args.iterations,
                    neighbors_per_iteration=args.neighbors,
                    scope='Initial complete-star pair-support heuristic only; not full arc consistency, simultaneous completion or exhaustive coverage.')
    write_json(args.out/'manifest.json', manifest)
    initial = [list(e) for e in signature(json.loads(args.initial.read_bytes())['overlap_edges_outer_zero_based'])]
    full_graph({'overlap_edges_outer_zero_based': initial})
    generator = random.Random(args.seed)
    work_input, work_output = scratch/'input.txt', scratch/'native.json'
    pair_input, pair_output = scratch/'pairs.bin', scratch/'gpu.json'
    evaluated, capped = 0, 0

    def evaluate(candidates):
        nonlocal evaluated, capped
        write_input(work_input, candidates)
        batch = invoke(native, work_input, work_output, 30, 2000000, 20000)
        results = batch['results']
        require(len(results) == len(candidates), 'Native batch output mismatch')
        evaluated += len(candidates)
        complete = [i for i, result in enumerate(results) if result['complete_domain_enumeration']]
        capped += len(candidates)-len(complete)
        scored = [None]*len(candidates)
        if complete:
            export_pair_input(pair_input, [candidates[i] for i in complete], [results[i] for i in complete])
            gpu = invoke(args.gpu.resolve(), pair_input, pair_output)
            require(gpu['status'] == 'INITIAL_PAIR_SUPPORT_SCORES_ONLY'
                    and gpu['candidate_count'] == len(complete)
                    and len(gpu['results']) == len(complete), 'CUDA candidate output mismatch')
            for local_index, (i, summary) in enumerate(zip(complete, gpu['results'])):
                sizes = [len(row['domain_masks_hex']) for row in results[i]['domains']]
                require(summary['candidate_index'] == local_index and summary['domain_counts'] == sizes,
                        'CUDA candidate order/domain count mismatch')
                live = summary['initial_pair_supported_domain_counts']
                require(len(live) == 84 and all(type(n) is int and 0 <= n <= size for n, size in zip(live, sizes)),
                        'CUDA support count range')
                quality = [sum(size > 0 for size in sizes), sum(size > 0 for size in live),
                           sum(live)/max(1, sum(sizes)), sum(log1p(size) for size in sizes)]
                scored[i] = (quality, results[i], summary)
        return scored

    started = time.perf_counter()
    initial_evaluation = evaluate([initial])[0]
    require(initial_evaluation is not None, 'Initial native enumeration capped')
    current, current_score = initial, initial_evaluation[0]
    best, best_result = initial, initial_evaluation
    visited = {signature(initial)}
    snapshots, records = [initial], []
    stop = 'ITERATION_LIMIT'
    for iteration in range(args.iterations):
        write_input(work_input, [current])
        trade_seed = generator.getrandbits(64)
        proposed = invoke(neighbors, work_input, work_output, args.neighbors, trade_seed)
        proposal_path = proposal_dir/f'iteration_{iteration:04d}.json'
        write_json(proposal_path, proposed)
        options = proposed['overlap_candidates']
        if not options:
            stop = 'NO_LEGAL_TWO_EDGE_MOVE'
            break
        evaluations = evaluate(options)
        ranked = [(result[0], generator.random(), i) for i, result in enumerate(evaluations)
                  if result is not None and signature(options[i]) not in visited]
        if not ranked:
            stop = 'SAMPLED_NEIGHBORS_CAPPED_OR_VISITED'
            break
        quality, _, choice = max(ranked)
        accepted = quality >= current_score or generator.random() < 0.15
        record = dict(iteration=iteration, native_sample_seed=trade_seed,
                      proposal_path=path_key(proposal_path), proposal_sha256=digest(proposal_path),
                      total_legal_trades=proposed['legal_trades'], evaluated_neighbors=len(options),
                      chosen_index=choice, rank=quality, accepted=accepted,
                      removed=proposed['trades'][choice]['removed'], added=proposed['trades'][choice]['added'])
        if accepted:
            candidate = options[choice]
            full_graph({'overlap_edges_outer_zero_based': candidate})
            current, current_score = candidate, quality
            snapshots.append(candidate)
            visited.add(signature(candidate))
            if quality > best_result[0]:
                best, best_result = candidate, evaluations[choice]
        records.append(record)
        write_json(args.out/'best_candidate.json', {'overlap_edges_outer_zero_based': best,
                   'initial_pair_support_rank': best_result[0], 'source_manifest': path_key(args.out/'manifest.json')})
        write_json(args.out/'best_domains_native.json', best_result[1])
        write_json(args.out/'best_gpu_summary.json', best_result[2])
        report = dict(status='SEARCH_IN_PROGRESS', best_rank=best_result[0], current_rank=current_score,
                      evaluated_states=evaluated, capped_states=capped, accepted_moves=len(snapshots)-1,
                      elapsed_seconds=time.perf_counter()-started, records=records,
                      overlap_candidates=snapshots, manifest=manifest)
        write_json(args.out/'summary.json', report)
        print(json.dumps({k:v for k,v in report.items() if k not in ('records','manifest','overlap_candidates')}), flush=True)
    for path in sources:
        require(bound[path_key(path)] == digest(path), 'Input/source changed during search')
    write_json(args.out/'best_candidate.json', {'overlap_edges_outer_zero_based': best,
               'initial_pair_support_rank': best_result[0], 'source_manifest': path_key(args.out/'manifest.json')})
    write_json(args.out/'best_domains_native.json', best_result[1])
    write_json(args.out/'best_gpu_summary.json', best_result[2])
    report = dict(status='BOUNDED_INITIAL_PAIR_SUPPORT_SEARCH_FINISHED', stop_reason=stop,
                  best_rank=best_result[0], initial_rank=initial_evaluation[0], evaluated_states=evaluated,
                  capped_states=capped, accepted_moves=len(snapshots)-1,
                  elapsed_seconds=time.perf_counter()-started, records=records,
                  overlap_candidates=snapshots, manifest=manifest,
                  scope='A necessary-condition heuristic only. Even 84 initially supported vertices do not establish full arc consistency or a completion.')
    write_json(args.out/'summary.json', report)
    print(json.dumps({k:v for k,v in report.items() if k not in ('records','manifest','overlap_candidates')}))


if __name__ == '__main__':
    main()
