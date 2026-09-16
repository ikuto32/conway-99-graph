"""Bounded heuristic search for overlap assignments passing star reciprocity.

Native generators and domain enumerators propose/rank neighbors. Every accepted
state is independently checked as a partial graph. Heuristic ranks certify
nothing; even an arc-consistent result requires separate exact completion work.
"""
import argparse
from hashlib import sha256
from itertools import combinations
import json
from math import log1p
from pathlib import Path
import random
import subprocess
import time

from audit_certificate import full_graph, require
from prepare import path_key

ROOT = Path(__file__).resolve().parents[1]
SUPPORTS = [set((a, b)) for a, b in combinations(range(7), 2) for _ in range(4)]
LINKS = [[v for v in range(84) if not SUPPORTS[u] & SUPPORTS[v]] for u in range(84)]


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def write_json(path, data):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(data, indent=2)+'\n', encoding='utf-8')
    temporary.replace(path)


def write_input(path, candidates):
    path.write_text('C99OVERLAPS1 '+str(len(candidates))+'\n'+''.join(
        ''.join(f'{u} {v}\n' for u, v in edges) for edges in candidates), encoding='ascii')


def invoke(executable, input_path, output_path, *args):
    # Only this explicit scratch output is replaced, never an input or archive.
    if output_path.exists():
        output_path.unlink()
    process = subprocess.run([str(executable), str(input_path), str(output_path), *map(str, args)],
                             text=True, capture_output=True, timeout=90)
    require(process.returncode == 0, f'Native command failed: {process.stderr}')
    return json.loads(output_path.read_bytes())


def rank(result):
    if not result['complete_domain_enumeration']:
        return None
    domains = [[int(mask, 16) for mask in row['domain_masks_hex']] for row in result['domains']]
    require(len(domains) == 84, 'Incomplete native vertex list')
    sizes = [len(row) for row in domains]
    unions, intersections = [], []
    for row in domains:
        union, intersection = 0, (1 << 84)-1
        for mask in row:
            union |= mask
            intersection &= mask
        unions.append(union)
        intersections.append(intersection)
    supported = []
    for u, row in enumerate(domains):
        # Initial pairwise supports only; no rank value is a feasibility claim.
        if any(not domains[v] for v in LINKS[u]):
            supported.append(0)
            continue
        ones = sum(1 << v for v in LINKS[u] if intersections[v] >> u & 1)
        zeros = sum(1 << v for v in LINKS[u] if not (unions[v] >> u & 1))
        supported.append(sum(mask & ones == ones and not mask & zeros for mask in row))
    nonempty = result['propagation']['status'] == 'ARC_CONSISTENT_NONEMPTY'
    return [int(nonempty), sum(size > 0 for size in sizes), sum(size > 0 for size in supported),
            sum(supported)/max(1, sum(sizes)), sum(log1p(size) for size in sizes)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--initial', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--iterations', type=int, default=40)
    parser.add_argument('--neighbors', type=int, default=32)
    parser.add_argument('--seed', type=int, default=20260916)
    parser.add_argument('--batch', type=Path)
    args = parser.parse_args()
    require(0 < args.iterations <= 1000 and 0 < args.neighbors <= 1000, 'Invalid finite search budget')
    require(not args.out.exists(), 'Preserve previous search; use a fresh output directory')
    args.out.mkdir(parents=True)
    scratch = args.out/'work'
    scratch.mkdir()
    native = ROOT/'acceleration/build/star_domains.exe'
    neighbors = ROOT/'acceleration/build/overlap_neighbors.exe'
    sources = [Path(__file__), args.initial, native, neighbors,
               ROOT/'acceleration/star_domains.rs', ROOT/'acceleration/overlap_neighbors.rs',
               ROOT/'acceleration/audit_certificate.py']
    if args.batch:
        sources.extend([args.batch, ROOT/'acceleration/star_domains_batch.rs'])
    bound = {path_key(path): digest(path) for path in sources}
    manifest = dict(inputs_sha256=bound, seed=args.seed, iterations=args.iterations,
                    neighbors_per_iteration=args.neighbors,
                    scope='A finite guided local search only. Ranks and nonempty arc consistency certify no completion.')
    write_json(args.out/'manifest.json', manifest)
    initial = json.loads(args.initial.read_bytes())['overlap_edges_outer_zero_based']
    full_graph({'overlap_edges_outer_zero_based': initial})
    current = initial
    generator = random.Random(args.seed)
    started = time.perf_counter()
    work_input, work_output = scratch/'input.txt', scratch/'output.json'
    write_input(work_input, [initial])
    current_result = invoke(native, work_input, work_output, 30, 2000000, 20000)
    current_rank = rank(current_result)
    require(current_rank is not None, 'Initial complete-domain enumeration capped')
    best, best_rank, best_result = initial, current_rank, current_result
    visited = {tuple(map(tuple, initial))}
    records = []
    evaluations, capped, accepted = 1, 0, 0
    snapshots = [initial]
    stop = 'ITERATION_LIMIT'
    for iteration in range(args.iterations):
        if best_rank[0]:
            stop = 'ARC_CONSISTENT_NECESSARY_CONTROL_FOUND'
            break
        write_input(work_input, [current])
        trade_seed = generator.getrandbits(64)
        proposed = invoke(neighbors, work_input, work_output, args.neighbors, trade_seed)
        options = proposed['overlap_candidates']
        if not options:
            stop = 'NO_LEGAL_TWO_EDGE_MOVE'
            break
        if args.batch:
            write_input(work_input, options)
            results = invoke(args.batch, work_input, work_output, 30, 2000000, 20000)['results']
            require(len(results) == len(options), 'Native batch count mismatch')
        else:
            results = []
            for candidate in options:
                write_input(work_input, [candidate])
                results.append(invoke(native, work_input, work_output, 30, 2000000, 20000))
        evaluations += len(options)
        ranked = []
        for i, result in enumerate(results):
            quality = rank(result)
            if quality is None:
                capped += 1
            elif tuple(map(tuple, options[i])) not in visited:
                ranked.append((quality, generator.random(), i))
        if not ranked:
            stop = 'SAMPLED_NEIGHBORS_CAPPED_OR_ALREADY_VISITED'
            break
        ranked.sort(reverse=True)
        chosen_rank, _, choice = ranked[0]
        # A small, recorded escape probability prevents monotone trapping.
        accept = chosen_rank >= current_rank or generator.random() < 0.15
        record = dict(iteration=iteration, native_sample_seed=trade_seed,
                      total_legal_trades=proposed['legal_trades'], evaluated_neighbors=len(options),
                      chosen_index=choice, rank=chosen_rank, accepted=accept,
                      removed=proposed['trades'][choice]['removed'], added=proposed['trades'][choice]['added'])
        if accept:
            candidate = options[choice]
            full_graph({'overlap_edges_outer_zero_based': candidate})
            current, current_rank, current_result = candidate, chosen_rank, results[choice]
            visited.add(tuple(map(tuple, candidate)))
            snapshots.append(candidate)
            accepted += 1
            if current_rank > best_rank:
                best, best_rank, best_result = current, current_rank, current_result
                write_json(args.out/'best_candidate.json', {'overlap_edges_outer_zero_based': best,
                           'rank': best_rank, 'iteration': iteration, 'source_manifest': path_key(args.out/'manifest.json')})
                write_json(args.out/'best_domains_native.json', best_result)
        records.append(record)
        report = dict(status='SEARCH_IN_PROGRESS', best_rank=best_rank, current_rank=current_rank,
                      evaluated_states=evaluations, capped_states=capped, accepted_moves=accepted,
                      elapsed_seconds=time.perf_counter()-started, records=records,
                      overlap_candidates=snapshots, manifest=manifest)
        write_json(args.out/'summary.json', report)
        print(json.dumps({k:v for k,v in report.items() if k not in ('records','manifest','overlap_candidates')}), flush=True)
    for path in sources:
        require(bound[path_key(path)] == digest(path), 'Source or input changed during search')
    write_json(args.out/'best_candidate.json', {'overlap_edges_outer_zero_based': best, 'rank': best_rank,
               'source_manifest': path_key(args.out/'manifest.json')})
    write_json(args.out/'best_domains_native.json', best_result)
    report = dict(status='BOUNDED_GUIDED_SEARCH_FINISHED', stop_reason=stop,
                  best_rank=best_rank, evaluated_states=evaluations, capped_states=capped,
                  accepted_moves=accepted, partial_pair_checks=(accepted+1)*4851,
                  elapsed_seconds=time.perf_counter()-started, records=records,
                  overlap_candidates=snapshots, manifest=manifest,
                  scope='Necessary-condition heuristic search only; independently check final domains and full completion separately.')
    write_json(args.out/'summary.json', report)
    print(json.dumps({k:v for k,v in report.items() if k not in ('records','manifest','overlap_candidates')}))


if __name__ == '__main__':
    main()
