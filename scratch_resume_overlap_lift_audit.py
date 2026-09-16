"""Solver-free direct partial-graph audit, independent of overlap producer."""
from collections import Counter
from itertools import combinations
from pathlib import Path
import hashlib
import json


def main():
    path = Path('scratch_resume_overlap_lift.json')
    raw = path.read_bytes()
    data = json.loads(raw)
    cp = Path('scratch_resume_integral_compression.json')
    assert data['input_sha256'] == hashlib.sha256(cp.read_bytes()).hexdigest()
    c = json.loads(cp.read_bytes())['C']
    supports = list(combinations(range(7), 2))
    labels = [(2*a+s, 2*b+t) for a, b in supports for s in range(2) for t in range(2)]
    edges = set()
    for pair in data['overlap_edges_outer_zero_based']:
        assert len(pair) == 2 and all(type(x) is int and 0 <= x < 84 for x in pair)
        u, v = pair
        assert u < v and (u, v) not in edges
        assert len(set(supports[u//4]) & set(supports[v//4])) == 1
        edges.add((u, v))
    assert len(edges) == 168
    outer = [set() for _ in range(84)]
    for u, v in edges:
        outer[u].add(v)
        outer[v].add(u)
    assert all(len(row) == 4 for row in outer)
    totals = [[0]*21 for _ in range(21)]
    for u, v in edges:
        totals[u//4][v//4] += 1
        totals[v//4][u//4] += 1
    for f, h in combinations(range(21), 2):
        if set(supports[f]) & set(supports[h]):
            assert totals[f][h] == c[f][h]
    for u in range(84):
        for symbol in range(14):
            count = sum(symbol in labels[v] for v in outer[u])
            assert count == 1 if symbol//2 in supports[u//4] else count <= 2
    adj = [set() for _ in range(99)]
    def put(u, v):
        adj[u].add(v)
        adj[v].add(u)
    for s in range(14):
        put(0, s+1)
    for g in range(7):
        put(2*g+1, 2*g+2)
    for x, label in enumerate(labels):
        for s in label:
            put(x+15, s+1)
    for u, v in edges:
        put(u+15, v+15)
    hist = Counter()
    for u, v in combinations(range(99), 2):
        common = len(adj[u] & adj[v])
        is_edge = v in adj[u]
        assert common <= (1 if is_edge else 2), (u, v, common)
        hist[str((int(is_edge), common))] += 1
    cycles = []
    for g in range(7):
        vertices = {x for x in range(84) if g in supports[x//4]}
        rows = {x: outer[x] & vertices for x in vertices}
        assert all(len(row) == 2 for row in rows.values())
        remaining = set(vertices)
        sizes = []
        while remaining:
            start = min(remaining)
            stack, reached = [start], {start}
            while stack:
                x = stack.pop()
                for y in rows[x]-reached:
                    reached.add(y)
                    stack.append(y)
            assert len(reached) % 4 == 0
            sizes.append(len(reached))
            remaining -= reached
        cycles.append(sorted(sizes))
    output = {'status': 'INDEPENDENT_SIMULTANEOUS_OVERLAP_LIFT_AUDIT_PASS',
              'input_sha256': hashlib.sha256(raw).hexdigest(),
              'overlap_edges': 168, 'exposed_graph_edges': sum(map(len, adj))//2,
              'degree_histogram': dict(sorted(Counter(map(len, adj)).items())),
              'pair_cap_histogram': dict(hist), 'group_cycle_lengths': cycles,
              'scope': 'Partial357-edge graph, degrees14 on15 vertices and6 on84 vertices. The336 disjoint-support edges are not supplied. No full SRG.'}
    assert output['exposed_graph_edges'] == 357
    Path('scratch_resume_overlap_lift_audit.json').write_text(json.dumps(output, indent=2)+'\n')
    print(json.dumps(output))


if __name__ == '__main__':
    main()
