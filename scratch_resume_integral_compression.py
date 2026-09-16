"""Bounded endpoint compression control; this does not build an SRG."""
from itertools import combinations
from pathlib import Path
import json
import sys
import time

sys.path.insert(0, str(Path('.ortools').resolve()))
from ortools.sat.python import cp_model

SUPPORTS = list(combinations(range(7), 2))


def main():
    model = cp_model.CpModel()
    variables = {}
    baseline = {}
    for i, j in combinations(range(21), 2):
        variables[i, j] = model.new_bool_var(f'b_{i}_{j}')
        baseline[i, j] = 1 if set(SUPPORTS[i]) & set(SUPPORTS[j]) else 3
    def entry(i, j):
        if i == j:
            return 0
        key = tuple(sorted((i, j)))
        return baseline[key] + variables[key]
    for i, support in enumerate(SUPPORTS):
        model.add(sum(entry(i, j) for j in range(21)) == 48)
        model.add(sum(entry(i, j) for j in range(21)
                      if j != i and set(support) & set(SUPPORTS[j])) == 16)
        for g in range(7):
            model.add(sum(entry(i, j) for j, other in enumerate(SUPPORTS)
                          if g in other) == (8 if g in support else 16))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 45
    solver.parameters.num_search_workers = 1
    solver.parameters.random_seed = 99014
    start = time.monotonic()
    status = solver.solve(model)
    result = {'solver_status': solver.status_name(status),
              'elapsed_seconds': time.monotonic() - start,
              'scope': 'Integral 21x21 compression at E0=0 only; no adjacency B or graph.',
              'supports': SUPPORTS}
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        c = [[0 if i == j else int(solver.value(entry(i, j)))
              for j in range(21)] for i in range(21)]
        result['C'] = c
        result['trace_square'] = sum(x*x for row in c for x in row)
        result['trace_cycle_square'] = result['trace_square'] - 2688
        assert result['trace_square'] == 2772
    Path('scratch_resume_integral_compression.json').write_text(
        json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('C','supports')}))


if __name__ == '__main__':
    main()
