"""One bounded LP check of the no-block-total fixed-overlap relaxation.

Any emitted witness is reconstructed as exact fractions and checked
against every linear constraint, so numerical feasibility is insufficient.
"""
from collections import Counter
from fractions import Fraction
import json
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE/'.ortools'))
from ortools.linear_solver import pywraplp


def main():
    started = time.monotonic()
    data = json.loads((HERE/'scratch_next_overlap_semantic_map.json').read_bytes())
    groups = [g for g in data['groups'] if g['kind'] != 'block_total']
    solver = pywraplp.Solver.CreateSolver('GLOP')
    solver.SetTimeLimit(30000)
    x = {var: solver.NumVar(0, 1, f'e{var}') for var, u, v in data['edge_variables']}
    for group in groups:
        constraint = solver.Constraint(group['target'] if group['equality'] else -solver.infinity(), group['target'])
        for var in group['terms']:
            constraint.SetCoefficient(x[var], 1)
    status = solver.Solve()
    result = {'status_code':status, 'scope':'Fixed overlap linear relaxation with no disjoint compression totals; continuous edge variables only.'}
    if status == pywraplp.Solver.OPTIMAL:
        for bound in (16, 1000, 1000000, 1000000000):
            rational = {var:Fraction(v.solution_value()).limit_denominator(bound) for var,v in x.items()}
            checked = all(0 <= value <= 1 for value in rational.values())
            for group in groups:
                total = sum(rational[var] for var in group['terms'])
                checked &= total == group['target'] if group['equality'] else total <= group['target']
            if checked:
                result.update(status='EXACT_RATIONAL_LINEAR_RELAXATION_WITNESS',
                              values={str(var):str(value) for var,value in rational.items()},
                              fractional_variables=sum(value.denominator != 1 for value in rational.values()),
                              denominator_histogram=dict(Counter(value.denominator for value in rational.values())),
                              all_linear_constraints_exactly_checked=len(groups))
                break
        else:
            result['status'] = 'NUMERIC_FEASIBLE_EXACT_RECONSTRUCTION_FAILED'
    else:
        result['status'] = 'LP_NOT_FEASIBLE_NO_CERTIFICATE'
    result['elapsed_seconds'] = time.monotonic()-started
    (HERE/'scratch_next_overlap_fractional.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('values','denominator_histogram')}))


if __name__ == '__main__':
    main()
