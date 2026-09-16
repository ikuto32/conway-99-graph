"""Bounded single-fibre incidence lift, no full graph completion."""
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
    ap.add_argument('--source', type=int, default=0)
    ap.add_argument('--seconds', type=float, default=30)
    ap.add_argument('--q16', action='store_true')
    args = ap.parse_args()
    inp = Path('scratch_resume_integral_compression.json')
    data = json.loads(inp.read_text())
    supports = list(map(tuple, data['supports']))
    source = supports[args.source]
    c = data['C'][args.source]
    labels = [(2*a+s, 2*b+t) for a, b in supports
              for s in range(2) for t in range(2)]
    sources = list(range(4*args.source, 4*args.source+4))
    targets = [i for i in range(84) if i not in sources]
    model = cp_model.CpModel()
    x = {(p, y): model.new_bool_var(f'x_{p}_{y}')
         for p in range(4) for y in targets}
    degrees = {}
    for p in range(4):
        model.add(sum(x[p, y] for y in targets) == 12)
        for label in range(14):
            quota = 1 if label//2 in source else 2
            model.add(sum(x[p, y] for y in targets if label in labels[y]) == quota)
        squares = []
        for f in range(21):
            d = model.new_int_var(0, 4, f'd_{p}_{f}')
            model.add(d == sum(x[p, y] for y in targets if y//4 == f))
            degrees[p, f] = d
            if args.q16:
                q = model.new_int_var(0, 16, f'q_{p}_{f}')
                model.add_allowed_assignments([d, q], [(i, i*i) for i in range(5)])
                squares.append(q)
        if args.q16:
            model.add(sum(squares) == 16)
    for f in range(21):
        model.add(sum(degrees[p, f] for p in range(4)) == c[f])
    # A target carrying either sign of a source group can have at most one
    # neighbour among the two source corners carrying a fixed sign there.
    # This is the first-layer-label / target-vertex common-neighbour cap.
    for y in targets:
        for label in range(14):
            incident = [p for p in range(4) if label in labels[sources[p]]]
            if incident:
                cap = 1 if label//2 in supports[y//4] else 2
                model.add(sum(x[p, y] for p in incident) <= cap)
    for p, q in combinations(range(4), 2):
        both = []
        for y in targets:
            b = model.new_bool_var(f'sourcepair_{p}_{q}_{y}')
            model.add_multiplication_equality(b, [x[p, y], x[q, y]])
            both.append(b)
        cap = 2-len(set(labels[sources[p]]) & set(labels[sources[q]]))
        model.add(sum(both) == cap)
    for y, z in combinations(targets, 2):
        both = []
        for p in range(4):
            b = model.new_bool_var(f'targetpair_{p}_{y}_{z}')
            model.add_multiplication_equality(b, [x[p, y], x[p, z]])
            both.append(b)
        cap = 2-len(set(labels[y]) & set(labels[z]))
        model.add(sum(both) <= cap)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = args.seconds
    solver.parameters.num_search_workers = 1
    solver.parameters.random_seed = 1401299
    start = time.monotonic()
    status = solver.solve(model)
    result = {'status': solver.status_name(status), 'model_version': 2,
              'source': list(source),
              'source_index': args.source, 'q16_required': args.q16,
              'elapsed_seconds': time.monotonic()-start,
              'input_sha256': hashlib.sha256(inp.read_bytes()).hexdigest(),
              'scope': 'Single four-vertex fibre neighbour-incidence only. No simultaneous choices for 21 fibres, no B adjacency completion, and no SRG existence or E0 bound.'}
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        result['outer_neighbor_indices'] = [[y for y in targets if solver.value(x[p, y])] for p in range(4)]
        result['degree_rows'] = [[int(solver.value(degrees[p, f])) for f in range(21)] for p in range(4)]
        result['q_values'] = [sum(v*v for v in row) for row in result['degree_rows']]
    suffix = f'f{args.source}' + ('_q16' if args.q16 else '')
    Path(f'scratch_resume_uniform_fibre_incidence_{suffix}.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('outer_neighbor_indices', 'degree_rows')}))


if __name__ == '__main__':
    main()
