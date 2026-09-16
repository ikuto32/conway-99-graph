"""Bounded D-only simultaneous moment model; no adjacency B variables."""
from itertools import combinations
from pathlib import Path
import argparse
import hashlib
import json
import sys
import time
sys.path.insert(0, str(Path('.ortools').resolve()))
from ortools.sat.python import cp_model


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seconds', type=float, default=45)
    args = ap.parse_args()
    inp = Path('scratch_resume_integral_compression.json')
    cc = json.loads(inp.read_text())
    c = cc['C']
    supports = list(map(tuple, cc['supports']))
    g = [[48*int(a == b)+32-c[a][b]-8*len(set(supports[a]) & set(supports[b]))
          for b in range(21)] for a in range(21)]
    model = cp_model.CpModel()
    d, square = {}, {}
    for x in range(84):
        source = supports[x//4]
        for f in range(21):
            d[x, f] = model.new_int_var(0, 0 if f == x//4 else min(2, c[x//4][f]), f'd_{x}_{f}')
            square[x, f] = model.new_int_var(0, 4, f'square_{x}_{f}')
            model.add_allowed_assignments([d[x, f], square[x, f]], [(0, 0), (1, 1), (2, 4)])
        model.add(sum(d[x, f] for f in range(21)) == 12)
        model.add(sum(square[x, f] for f in range(21)) == 16)
        for a in range(7):
            model.add(sum(d[x, f] for f in range(21) if a in supports[f]) == (2 if a in source else 4))
    for s in range(21):
        for f in range(21):
            model.add(sum(d[x, f] for x in range(4*s, 4*s+4)) == c[s][f])
        enc = [sum((3**f)*d[x, f] for f in range(21)) for x in range(4*s, 4*s+4)]
        for p in range(3):
            model.add(enc[p] <= enc[p+1])
    for a in range(21):
        model.add(sum(square[x, a] for x in range(84)) == g[a][a])
        for b in range(a+1, 21):
            products = []
            for x in range(84):
                if x//4 in (a, b):
                    continue
                p = model.new_int_var(0, 4, f'p_{x}_{a}_{b}')
                model.add_multiplication_equality(p, [d[x, a], d[x, b]])
                products.append(p)
            model.add(sum(products) == g[a][b])
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = args.seconds
    solver.parameters.num_search_workers = 1
    solver.parameters.random_seed = 140199
    start = time.monotonic()
    status = solver.solve(model)
    result = {'status': solver.status_name(status), 'elapsed_seconds': time.monotonic()-start,
              'input_sha256': hashlib.sha256(inp.read_bytes()).hexdigest(),
              'scope': 'Simultaneous D-only model with extra q=16 and D<=2 restrictions. UNKNOWN/UNSAT is no E0 or C exclusion. SAT would need independent exact audit and binary fibre-incidence lift.',
              'variables': len(model.proto.variables)}
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        result['D'] = [[solver.value(d[x, f]) for f in range(21)] for x in range(84)]
    Path('scratch_next_degree_gram.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'D'}), flush=True)


if __name__ == '__main__':
    main()
