"""Independent full-graph audit and ordered-subset replay of local star claims.

No star producer is imported. Witnesses are added directly to a 99-vertex
adjacency matrix. Exhaustion uses increasing-index neighbor subsets and actual
graph changes, independently of the producer's quota-first resource model.
"""
import argparse
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import time

from audit_certificate import full_graph, require


def bits_to_list(mask):
    answer = []
    while mask:
        bit = mask & -mask
        answer.append(bit.bit_length()-1)
        mask ^= bit
    return answer


def add_checked(rows, u, v):
    old_u, old_v = rows[u], rows[v]
    require(not (old_u >> v & 1), 'Repeated added edge')
    rows[u] |= 1 << v
    rows[v] |= 1 << u
    affected = [(u, v)] + [(u, w) for w in bits_to_list(old_v)] + [(v, w) for w in bits_to_list(old_u)]
    valid = all((rows[a] & rows[b]).bit_count() <= (1 if rows[a] >> b & 1 else 2) for a, b in affected)
    if not valid:
        rows[u], rows[v] = old_u, old_v
    return valid, old_u, old_v


def exhaust(adjacency, unknown, outer):
    u = outer+15
    rows = [sum(1 << v for v in neighbors) for neighbors in adjacency]
    labels = {v: sorted(s-1 for s in adjacency[v] if 1 <= s <= 14) for v in range(15, 99)}
    target = [(1 if s+1 in adjacency[u] else 2)-len(adjacency[u] & adjacency[s+1]) for s in range(14)]
    candidates = []
    for v in range(15, 99):
        if tuple(sorted((u, v))) in unknown:
            legal, old_u, old_v = add_checked(rows, u, v)
            if legal:
                candidates.append(v)
                rows[u], rows[v] = old_u, old_v
    suffix = [[0]*14 for _ in range(len(candidates)+1)]
    for i in range(len(candidates)-1, -1, -1):
        suffix[i] = suffix[i+1][:]
        for s in labels[candidates[i]]:
            suffix[i][s] += 1
    nodes = 0

    def visit(start, chosen, demand):
        nonlocal nodes
        nodes += 1
        if len(chosen) == 8:
            return chosen if all(d == 0 for d in demand) else None
        if len(candidates)-start < 8-len(chosen) or any(d > suffix[start][s] for s, d in enumerate(demand)):
            return None
        for i in range(start, len(candidates)):
            v = candidates[i]
            if any(demand[s] <= 0 for s in labels[v]):
                continue
            legal, old_u, old_v = add_checked(rows, u, v)
            if legal:
                remaining = demand[:]
                for s in labels[v]:
                    remaining[s] -= 1
                result = visit(i+1, chosen+[v-15], remaining)
                rows[u], rows[v] = old_u, old_v
                if result is not None:
                    return result
        return None

    answer = visit(0, [], target)
    return answer, nodes, len(candidates)


def verify_witness(adjacency, unknown, outer, neighbors):
    require(type(neighbors) is list and len(neighbors) == len(set(neighbors)) == 8, 'Eight distinct new neighbors required')
    u = outer+15
    rows = [sum(1 << v for v in adjacent) for adjacent in adjacency]
    for outer_v in neighbors:
        require(type(outer_v) is int and 0 <= outer_v < 84, 'Neighbor range')
        v = outer_v+15
        require(tuple(sorted((u, v))) in unknown, 'Added edge outside disjoint domain')
        rows[u] |= 1 << v
        rows[v] |= 1 << u
    require(rows[u].bit_count() == 14 and sum(r.bit_count() for r in rows) == 730, 'Completed star degrees')
    for a, b in combinations(range(99), 2):
        require((rows[a] & rows[b]).bit_count() <= (1 if rows[a] >> b & 1 else 2), 'Actual graph cap failed')
    for symbol in range(1, 15):
        require((rows[u] & rows[symbol]).bit_count() == (1 if rows[u] >> symbol & 1 else 2), 'Exact root-label quota failed')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--walk', type=Path, default=Path('acceleration/results/20260916_walk_10000.json'))
    parser.add_argument('--control', type=Path, default=Path('acceleration/results/20260916_goal_theory_stars96.json'))
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), 'Preserve prior audit')
    started = time.perf_counter()
    walk, control = (json.loads(p.read_bytes()) for p in (args.walk, args.control))
    for name, digest in control['inputs_sha256'].items():
        require(sha256(Path(name).read_bytes()).hexdigest() == digest, 'Control input/source hash changed')
    witnesses, exhausted = 0, []
    all_pass, rejected = [], []
    for record in control['results']:
        index = record['snapshot_index']
        adjacency, unknown = full_graph({'overlap_edges_outer_zero_based': walk['overlap_candidates'][index]})
        require([row['outer_vertex'] for row in record['stars']] == list(range(84)), 'Star coverage')
        failed = []
        for row in record['stars']:
            u = row['outer_vertex']
            if row['status'] == 'LOCAL_STAR_WITNESS':
                verify_witness(adjacency, unknown, u, row['new_neighbors_outer'])
                witnesses += 1
            else:
                require(row['status'] == 'LOCAL_STAR_EXHAUSTED' and row['new_neighbors_outer'] is None, 'Unknown local status')
                answer, nodes, candidates = exhaust(adjacency, unknown, u)
                require(answer is None, f'False exhaustion at snapshot {index}, vertex {u}: {answer}')
                exhausted.append(dict(snapshot_index=index, outer_vertex=u, ordered_subset_nodes=nodes,
                                      individually_admissible_neighbors=candidates))
                failed.append(u)
        if failed:
            rejected.append(index)
        else:
            all_pass.append(index)
        print(json.dumps(dict(snapshot_index=index, independent_impossible_stars=failed)), flush=True)
    result = dict(status='INDEPENDENT_NONLINEAR_VERTEX_STAR_AUDIT_PASS',
        inputs_sha256={str(p):sha256(p.read_bytes()).hexdigest() for p in (args.walk,args.control,Path(__file__))},
        snapshots_checked=len(control['results']), explicit_star_witnesses_verified=witnesses,
        witness_partial_pair_caps_checked=4851*witnesses, independently_exhausted_stars=len(exhausted),
        rejected_snapshot_indices=rejected, all_local_stars_feasible_snapshot_indices=all_pass,
        independent_exhaustion_details=exhausted, ordered_subset_search_nodes=sum(r['ordered_subset_nodes'] for r in exhausted),
        producer_or_solver_imported=False, elapsed_seconds=time.perf_counter()-started,
        scope='Uniform necessary vertex-star condition; each listed failing fixed overlap assignment is excluded by a complete independent finite local search. Passing stars have explicit separate partial-graph witnesses but need not reciprocate. No all-K or Conway exclusion.')
    with args.out.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'independent_exhaustion_details'}))


if __name__ == '__main__':
    main()
