"""Simultaneous overlapping-support lift of one fixed compression, bounded.

Only the 168 overlapping-support edges are chosen; disjoint-support edges
remain unassigned. This is not a full SRG search or a lower-layer census.
"""
from itertools import combinations
from pathlib import Path
import hashlib
import json
import sys
import time

sys.path.insert(0, str(Path('.ortools').resolve()))
from ortools.sat.python import cp_model


def main():
    inp = Path('scratch_resume_integral_compression.json')
    data = json.loads(inp.read_bytes())
    supports = list(combinations(range(7), 2))
    labels = [(2*a+s, 2*b+t) for a, b in supports
              for s in range(2) for t in range(2)]
    c = data['C']
    model = cp_model.CpModel()
    edges = {(u, v): model.new_bool_var(f'e_{u}_{v}')
             for u, v in combinations(range(84), 2)
             if len(set(supports[u//4]) & set(supports[v//4])) == 1}
    def edge(u, v):
        return edges.get(tuple(sorted((u, v))))
    for f, h in combinations(range(21), 2):
        if set(supports[f]) & set(supports[h]):
            model.add(sum(edge(u, v) for u in range(4*f, 4*f+4)
                          for v in range(4*h, 4*h+4)) == c[f][h])
    for u, label in enumerate(labels):
        for symbol in range(14):
            terms = [edge(u, v) for v in range(84)
                     if symbol in labels[v] and edge(u, v) is not None]
            if symbol//2 in supports[u//4]:
                model.add(sum(terms) == 1)
            else:
                model.add(sum(terms) <= 2)
    products = 0
    for u, v in combinations(range(84), 2):
        terms = []
        for w in range(84):
            a, b = edge(u, w), edge(v, w)
            if a is not None and b is not None:
                z = model.new_bool_var(f'p_{u}_{v}_{w}')
                model.add_bool_or([a.Not(), b.Not(), z])
                terms.append(z)
                products += 1
        pair_edge = edge(u, v)
        if pair_edge is not None:
            terms.append(pair_edge)
        model.add(sum(terms) <= 2-len(set(labels[u]) & set(labels[v])))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 45
    solver.parameters.num_search_workers = 1
    solver.parameters.random_seed = 99142
    started = time.monotonic()
    status = solver.solve(model)
    result = {'status': solver.status_name(status),
              'elapsed_seconds': time.monotonic()-started,
              'input_sha256': hashlib.sha256(inp.read_bytes()).hexdigest(),
              'edge_variables': len(edges), 'one_way_products': products,
              'scope': 'All seven group-star 2-factors on the same84 vertices; disjoint edges unassigned. No graph completion or E0 exclusion.'}
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        result['overlap_edges_outer_zero_based'] = [list(pair) for pair, var in edges.items()
                                                  if solver.value(var)]
        assert len(result['overlap_edges_outer_zero_based']) == 168
    Path('scratch_resume_overlap_lift.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'overlap_edges_outer_zero_based'}))


if __name__ == '__main__':
    main()
