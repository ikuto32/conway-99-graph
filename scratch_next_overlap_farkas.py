"""Extract an exact weighted-capacity contradiction for the fixed overlap."""
from fractions import Fraction
from functools import reduce
import json
from math import gcd, lcm
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'.ortools'))
from ortools.linear_solver import pywraplp


def main():
    started=time.monotonic()
    data=json.loads((HERE/'scratch_next_overlap_semantic_map.json').read_bytes())
    groups=[(i,g) for i,g in enumerate(data['groups']) if g['kind']!='block_total' and g['terms']]
    edge_ids=[var for var,u,v in data['edge_variables']]
    solver=pywraplp.Solver.CreateSolver('GLOP')
    solver.SetTimeLimit(30000)
    y={}
    variables=[]
    for i,g in groups:
        plus=solver.NumVar(0,solver.infinity(),f'p{i}')
        minus=solver.NumVar(0,solver.infinity(),f'n{i}') if g['equality'] else None
        y[i]=(plus,minus)
        variables.append(plus)
        if minus is not None: variables.append(minus)
    upper={e:solver.NumVar(0,solver.infinity(),f'b{e}') for e in edge_ids}
    variables.extend(upper.values())
    rows={e:solver.Constraint(0,solver.infinity()) for e in edge_ids}
    rhs=solver.Constraint(-solver.infinity(),-1)
    objective=solver.Objective()
    for v in variables: objective.SetCoefficient(v,1)
    objective.SetMinimization()
    for i,g in groups:
        plus,minus=y[i]
        rhs.SetCoefficient(plus,g['target'])
        if minus is not None: rhs.SetCoefficient(minus,-g['target'])
        for e in g['terms']:
            rows[e].SetCoefficient(plus,1)
            if minus is not None: rows[e].SetCoefficient(minus,-1)
    for e,var in upper.items():
        rows[e].SetCoefficient(var,1)
        rhs.SetCoefficient(var,1)
    status=solver.Solve()
    result={'status_code':status,'scope':'Linear necessary conditions of one fixed overlap assignment, independent of disjoint compression totals.'}
    if status==pywraplp.Solver.OPTIMAL:
        for denominator in (100,1000,10000,1000000,100000000):
            # A common denominator permits exact finite rounding. Any
            # resulting negative edge coefficient is repaired using its
            # valid upper bound x_e<=1, which increases the RHS explicitly.
            weights={i:Fraction(round((plus.solution_value()-(minus.solution_value() if minus else 0))*denominator),denominator)
                     for i,(plus,minus) in y.items()}
            upperweights={e:Fraction(max(0,round(v.solution_value()*denominator)),denominator) for e,v in upper.items()}
            coeffs={e:upperweights[e] for e in edge_ids}
            target=sum(upperweights.values())
            valid=all(v>=0 for v in upperweights.values())
            for i,g in groups:
                if not g['equality']: valid &= weights[i]>=0
                target+=weights[i]*g['target']
                for e in g['terms']: coeffs[e]+=weights[i]
            for e,value in coeffs.items():
                if value<0:
                    upperweights[e]-=value
                    target-=value
                    coeffs[e]=Fraction(0)
            if valid and target<0 and all(v>=0 for v in coeffs.values()):
                scale=reduce(lcm,(v.denominator for v in list(weights.values())+list(upperweights.values())),1)
                integers={i:int(v*scale) for i,v in weights.items() if v}
                upperintegers={e:int(v*scale) for e,v in upperweights.items() if v}
                divisor=reduce(gcd,[abs(v) for v in list(integers.values())+list(upperintegers.values())])
                integers={i:v//divisor for i,v in integers.items()}
                upperintegers={e:v//divisor for e,v in upperintegers.items()}
                result.update(status='EXACT_INTEGER_WEIGHTED_CAPACITY_CONTRADICTION',
                              group_multipliers={str(i):v for i,v in integers.items()},
                              edge_upper_bound_multipliers={str(i):v for i,v in upperintegers.items()},
                              combined_rhs=str(target*scale/divisor),
                              nonzero_edge_coefficients={str(e):str(v*scale/divisor) for e,v in coeffs.items() if v},
                              support_size=len(integers),upper_bound_support_size=len(upperintegers))
                break
        else: result['status']='NUMERIC_FARKAS_EXACT_RECONSTRUCTION_FAILED'
    else: result['status']='NO_FARKAS_CERTIFICATE'
    result['elapsed_seconds']=time.monotonic()-started
    (HERE/'scratch_next_overlap_farkas.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('group_multipliers','edge_upper_bound_multipliers','nonzero_edge_coefficients')}))


if __name__=='__main__': main()
