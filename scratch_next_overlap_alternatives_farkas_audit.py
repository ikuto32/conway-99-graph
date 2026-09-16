"""Independently check integer completion obstructions from a partial graph.

The checker builds the 99-vertex fixed graph and derives constraints from
its adjacency sets. It imports neither the producer nor a numerical solver.
"""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path


def build_graph(data):
    labels = [(a, b) for a in range(14) for b in range(a+1, 14) if a//2 != b//2]
    labels.sort(key=lambda pair: (pair[0]//2, pair[1]//2, pair))
    adj = [set() for _ in range(99)]
    def put(u, v):
        adj[u].add(v)
        adj[v].add(u)
    for symbol in range(14):
        put(0, symbol+1)
    for symbol in range(0, 14, 2):
        put(symbol+1, symbol+2)
    for u, pair in enumerate(labels, 15):
        for symbol in pair:
            put(u, symbol+1)
    edges = data['overlap_edges_outer_zero_based']
    assert len(edges) == len({tuple(pair) for pair in edges}) == 168
    for pair in edges:
        assert len(pair) == 2
        u, v = pair
        assert type(u) is int and type(v) is int and 0 <= u < v < 84
        assert len({s//2 for s in labels[u]} & {s//2 for s in labels[v]}) == 1
        put(u+15, v+15)
    assert Counter(map(len, adj)) == {14: 15, 6: 84}
    assert all(len(adj[u] & adj[v]) <= (1 if v in adj[u] else 2)
               for u, v in combinations(range(99), 2))
    unknown = { (u+15, v+15) for u, v in combinations(range(84), 2)
                if not ({s//2 for s in labels[u]} & {s//2 for s in labels[v]}) }
    assert len(unknown) == 1680
    return adj, unknown


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('index', type=int, choices=range(4))
    index = parser.parse_args().index
    path = Path(f'scratch_next_overlap_alternatives_r{index}.json')
    certificate_path = path.with_name(path.stem+'_farkas.json')
    data, certificate = json.loads(path.read_bytes()), json.loads(certificate_path.read_bytes())
    assert certificate['candidate_sha256'] == sha256(path.read_bytes()).hexdigest()
    adj, unknown = build_graph(data)
    coefficients = dict.fromkeys(unknown, 0)
    target = 0
    group_counts = Counter()
    seen = set()
    for record in certificate['group_multipliers']:
        kind, coordinate, multiplier = record['kind'], record['coordinate'], record['multiplier']
        assert type(multiplier) is int and multiplier != 0
        assert len(coordinate) == 2 and all(type(value) is int for value in coordinate)
        key = kind, tuple(coordinate)
        assert key not in seen
        seen.add(key)
        terms = Counter()
        if kind == 'label_quota':
            outer, symbol = coordinate
            assert 0 <= outer < 84 and 0 <= symbol < 14
            u, v = outer+15, symbol+1
            rhs = (1 if v in adj[u] else 2)-len(adj[u] & adj[v])
            for w in adj[v]:
                pair = tuple(sorted((u, w)))
                if pair in unknown:
                    terms[pair] += 1
        else:
            assert kind == 'linear_pair_cap' and multiplier >= 0
            a, b = coordinate
            assert 0 <= a < b < 84
            u, v = a+15, b+15
            rhs = 2-int(v in adj[u])-len(adj[u] & adj[v])
            if (u, v) in unknown:
                terms[u, v] += 1
            for fixed, changing in ((u, v), (v, u)):
                for w in adj[fixed]:
                    pair = tuple(sorted((changing, w)))
                    if pair in unknown:
                        terms[pair] += 1
        target += multiplier*rhs
        for pair, multiplicity in terms.items():
            coefficients[pair] += multiplier*multiplicity
        group_counts[kind] += 1
    upper_seen = set()
    for record in certificate['edge_upper_bound_multipliers']:
        pair, multiplier = record['edge'], record['multiplier']
        assert len(pair) == 2 and all(type(value) is int for value in pair)
        assert type(multiplier) is int and multiplier > 0
        global_pair = tuple(value+15 for value in pair)
        assert global_pair in unknown and global_pair not in upper_seen
        upper_seen.add(global_pair)
        coefficients[global_pair] += multiplier
        target += multiplier
    assert all(type(value) is int and value >= 0 for value in coefficients.values())
    assert target < 0
    assert int(certificate['combined_rhs']) == target
    result = {
        'status': 'INDEPENDENT_ALTERNATIVE_INTEGER_FARKAS_AUDIT_PASS',
        'candidate_index': index,
        'inputs_sha256': {str(p): sha256(p.read_bytes()).hexdigest() for p in (path, certificate_path)},
        'exposed_graph_edges': sum(map(len, adj))//2,
        'partial_pair_caps_checked': 4851,
        'disjoint_unknowns': len(unknown),
        'group_counts': dict(group_counts),
        'upper_bound_count': len(upper_seen),
        'positive_coefficients': sum(value > 0 for value in coefficients.values()),
        'combined_rhs': target,
        'solver_or_producer_imported': False,
        'scope': 'An exact contradiction for real disjoint-edge completions in [0,1] of this complete overlap assignment, with same-fibre edges absent. No disjoint compression totals assumed; no global E0 or Conway exclusion.',
    }
    path.with_name(path.stem+'_farkas_audit.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
