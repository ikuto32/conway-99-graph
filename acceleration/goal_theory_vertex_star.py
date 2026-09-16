"""Exact one-vertex nonlinear completion control for complete overlap inputs.

A full graph must admit each independently completed outer-vertex star. This
control couples every root-label quota and partial common-neighbor cap while
adding all eight missing edges at once. Local witnesses need not reciprocate.
"""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import time

from audit_certificate import full_graph, require

LABELS = [(2*a+s, 2*b+t) for a, b in combinations(range(7), 2) for s in range(2) for t in range(2)]


def complete_star(adjacency, unknown, outer):
    u = outer + 15
    vertices = [v for v in range(15, 99) if tuple(sorted((u, v))) in unknown
                and all(len(adjacency[v] & adjacency[w]) < (1 if w in adjacency[v] else 2)
                        for w in adjacency[u])]
    # Exact pair(u, root-label) equations determine all eight new neighbors.
    demand = [(1 if s+1 in adjacency[u] else 2) - len(adjacency[u] & adjacency[s+1]) for s in range(14)]
    require(sum(demand) == 16 and min(demand) >= 0, 'Unexpected star demand')
    capacity = [2-int(w in adjacency[u])-len(adjacency[u] & adjacency[w]) if w != u else 0 for w in range(99)]
    resources = []
    conflicts = []
    for v in vertices:
        # Adding u-v creates one common neighbor for pair(u,w), w in N_K(v),
        # and changes pair(u,v)'s admissible count from two to one.
        resources.append(set(adjacency[v]) | {v})
        conflicts.append({w for w in vertices if w != v and
            len(adjacency[v] & adjacency[w]) == (1 if w in adjacency[v] else 2)})
    nodes = 0

    def search(chosen, available, remaining, caps):
        nonlocal nodes
        nodes += 1
        if sum(remaining) == 0:
            return chosen
        eligible = [i for i in available if all(remaining[s] > 0 for s in LABELS[vertices[i]-15])
                    and all(caps[w] > 0 for w in resources[i])]
        by_symbol = {s: [i for i in eligible if s in LABELS[vertices[i]-15]] for s, d in enumerate(remaining) if d}
        if any(len(by_symbol[s]) < remaining[s] for s in by_symbol):
            return None
        symbol = min(by_symbol, key=lambda s: (len(by_symbol[s])-remaining[s], len(by_symbol[s]), s))
        for selection in combinations(by_symbol[symbol], remaining[symbol]):
            next_remaining, next_caps = remaining[:], caps[:]
            excluded, legal = set(selection), True
            for i in selection:
                if any(vertices[j] in conflicts[i] for j in selection if i != j):
                    legal = False
                    break
                for s in LABELS[vertices[i]-15]:
                    next_remaining[s] -= 1
                    if next_remaining[s] < 0:
                        legal = False
                for w in resources[i]:
                    next_caps[w] -= 1
                    if next_caps[w] < 0:
                        legal = False
                excluded.update(j for j in eligible if vertices[j] in conflicts[i])
            if legal:
                result = search(chosen+list(selection), [i for i in eligible if i not in excluded], next_remaining, next_caps)
                if result is not None:
                    return result
        return None

    answer = search([], list(range(len(vertices))), demand, capacity)
    return {'outer_vertex': outer, 'nodes': nodes,
            'status': 'LOCAL_STAR_WITNESS' if answer is not None else 'LOCAL_STAR_EXHAUSTED',
            'new_neighbors_outer': None if answer is None else sorted(vertices[i]-15 for i in answer)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--walk', type=Path, default=Path('acceleration/results/20260916_walk_10000.json'))
    parser.add_argument('--summary', type=Path, default=Path('acceleration/results/20260916_final_bank/summary.json'))
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--limit', type=int, default=0)
    args = parser.parse_args()
    require(not args.out.exists(), 'Preserve previous output')
    started = time.perf_counter()
    walk, summary = (json.loads(p.read_bytes()) for p in (args.walk, args.summary))
    indices = summary['remaining_snapshot_indices']
    if args.limit:
        indices = indices[:args.limit]
    rows = []
    for index in indices:
        candidate = {'overlap_edges_outer_zero_based': walk['overlap_candidates'][index]}
        adjacency, unknown = full_graph(candidate)
        stars = [complete_star(adjacency, unknown, u) for u in range(84)]
        row = {'snapshot_index': index, 'stars': stars, 'histogram': dict(Counter(r['status'] for r in stars)),
               'search_nodes': sum(r['nodes'] for r in stars)}
        rows.append(row)
        print(json.dumps({k:v for k,v in row.items() if k != 'stars'}), flush=True)
    result = {'status': 'EXACT_INDEPENDENT_VERTEX_STAR_CONTROLS_COMPLETED',
              'inputs_sha256': {str(p): sha256(p.read_bytes()).hexdigest() for p in (args.walk, args.summary, Path(__file__))},
              'snapshot_count': len(rows), 'star_count': 84*len(rows), 'results': rows,
              'elapsed_seconds': time.perf_counter()-started,
              'scope': 'Each star uses one fixed complete overlap assignment; independent star witnesses need not share edge decisions. No full graph or uniform exclusion.'}
    with args.out.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'results'}))


if __name__ == '__main__':
    main()
