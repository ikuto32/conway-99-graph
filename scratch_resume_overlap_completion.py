"""Bounded exact completion of ONE prescribed partial graph/compression.

Never interprets failure of this fixed choice as global nonexistence.
Writes a candidate JSON only; submission export requires separate checking.
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
    lift_path = Path('scratch_resume_overlap_lift.json')
    c_path = Path('scratch_resume_integral_compression.json')
    cdata = json.loads(c_path.read_bytes())
    data = json.loads(lift_path.read_bytes())
    assert data['input_sha256'] == hashlib.sha256(c_path.read_bytes()).hexdigest()
    supports = list(combinations(range(7), 2))
    labels = [(2*a+s, 2*b+t) for a, b in supports for s in range(2) for t in range(2)]
    known = set(map(tuple, data['overlap_edges_outer_zero_based']))
    c = cdata['C']
    model = cp_model.CpModel()
    variables = {(u, v): model.new_bool_var(f'e_{u}_{v}')
                 for u, v in combinations(range(84), 2)
                 if not (set(supports[u//4]) & set(supports[v//4]))}
    def edge(u, v):
        key = tuple(sorted((u, v)))
        return variables[key] if key in variables else int(key in known)
    for f, h in combinations(range(21), 2):
        if not (set(supports[f]) & set(supports[h])):
            model.add(sum(edge(u, v) for u in range(4*f, 4*f+4)
                          for v in range(4*h, 4*h+4)) == c[f][h])
    for u in range(84):
        for symbol in range(14):
            quota = 1 if symbol//2 in supports[u//4] else 2
            model.add(sum(edge(u, v) for v in range(84)
                          if symbol in labels[v]) == quota)
    for u, v in combinations(range(84), 2):
        terms = [edge(u, v)]
        for w in range(84):
            a, b = edge(u, w), edge(v, w)
            if isinstance(a, int):
                if a:
                    terms.append(b)
            elif isinstance(b, int):
                if b:
                    terms.append(a)
            else:
                p = model.new_bool_var(f'p_{u}_{v}_{w}')
                model.add_bool_or([a.Not(), b.Not(), p])
                terms.append(p)
        model.add(sum(terms) <= 2-len(set(labels[u]) & set(labels[v])))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 45
    solver.parameters.num_search_workers = 1
    solver.parameters.random_seed = 14099
    start = time.monotonic()
    status = solver.solve(model)
    result = {'status': solver.status_name(status), 'elapsed_seconds': time.monotonic()-start,
              'lift_sha256': hashlib.sha256(lift_path.read_bytes()).hexdigest(),
              'compression_sha256': hashlib.sha256(c_path.read_bytes()).hexdigest(),
              'scope': 'Exact completion of one prescribed168-edge overlap graph and one C only; not all E0=0 compressions. UNSAT has no independent proof certificate.'}
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        out = known | {pair for pair, var in variables.items() if solver.value(var)}
        full = {(1, s+2) for s in range(14)}
        full |= {(2*g+2, 2*g+3) for g in range(7)}
        full |= {(s+2, x+16) for x, label in enumerate(labels) for s in label}
        full |= {(u+16, v+16) for u, v in out}
        adj = [set() for _ in range(100)]
        for u, v in full:
            adj[u].add(v)
            adj[v].add(u)
        assert len(full) == 693 and all(len(adj[x]) == 14 for x in range(1, 100))
        assert all(len(adj[u]&adj[v]) == (1 if v in adj[u] else 2)
                   for u, v in combinations(range(1, 100), 2))
        result['edges'] = sorted(map(list, full))
        result['internal_validation'] = 'PASS_ALL_SRG_CONDITIONS'
    Path('scratch_resume_overlap_completion.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'edges'}))


if __name__ == '__main__':
    main()
