"""One30-second exact-capacity-certificate attempt for an alternative."""
import argparse
from fractions import Fraction
from functools import reduce
from hashlib import sha256
from itertools import combinations
import json
from math import gcd, lcm
from pathlib import Path
import sys
import time

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'.ortools'))
from ortools.linear_solver import pywraplp


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('index',type=int,choices=range(4))
    index=parser.parse_args().index
    path=HERE/f'scratch_next_overlap_alternatives_r{index}.json'
    lp=json.loads(path.with_name(path.stem+'_lp.json').read_bytes())
    assert lp['status'] in ('LP_INFEASIBLE_NO_CHECKED_PROOF','LP_ABNORMAL_NO_CONCLUSION')
    known=set(map(tuple,json.loads(path.read_bytes())['overlap_edges_outer_zero_based']))
    labels=[(2*a+s,2*b+t) for a,b in combinations(range(7),2) for s in range(2) for t in range(2)]
    supports=[{a//2,b//2} for a,b in labels]
    outer=[set() for _ in range(84)]
    for u,v in known: outer[u].add(v);outer[v].add(u)
    edgepairs=[pair for pair in combinations(range(84),2) if not supports[pair[0]]&supports[pair[1]]]
    variables={pair:i for i,pair in enumerate(edgepairs)}
    groups=[]
    for u in range(84):
        for symbol in range(14):
            terms=[variables[tuple(sorted((u,v)))] for v in range(84)
                   if symbol in labels[v] and tuple(sorted((u,v))) in variables]
            if terms:
                target=(1 if symbol//2 in supports[u] else 2)-sum(symbol in labels[v] for v in outer[u])
                groups.append({'kind':'label_quota','coordinate':[u,symbol],'terms':terms,'target':target,'equality':True})
    for u,v in combinations(range(84),2):
        target=2-len(set(labels[u])&set(labels[v]))-int((u,v) in known)-len(outer[u]&outer[v])
        terms=[variables[u,v]] if (u,v) in variables else []
        terms += [variables[tuple(sorted((v,w)))] for w in outer[u] if tuple(sorted((v,w))) in variables]
        terms += [variables[tuple(sorted((u,w)))] for w in outer[v] if tuple(sorted((u,w))) in variables]
        if terms: groups.append({'kind':'linear_pair_cap','coordinate':[u,v],'terms':terms,'target':target,'equality':False})
    solver=pywraplp.Solver.CreateSolver('GLOP')
    solver.SetTimeLimit(30000)
    positive=[solver.NumVar(0,solver.infinity(),f'p{i}') for i in range(len(groups))]
    negative={i:solver.NumVar(0,solver.infinity(),f'n{i}') for i,g in enumerate(groups) if g['equality']}
    upper=[solver.NumVar(0,solver.infinity(),f'b{i}') for i in range(len(edgepairs))]
    coefficients=[solver.Constraint(0,solver.infinity()) for _ in edgepairs]
    rhs=solver.Constraint(-solver.infinity(),-1)
    objective=solver.Objective()
    for variable in positive+list(negative.values())+upper: objective.SetCoefficient(variable,1)
    objective.SetMinimization()
    for i,group in enumerate(groups):
        rhs.SetCoefficient(positive[i],group['target'])
        if i in negative: rhs.SetCoefficient(negative[i],-group['target'])
        for e in group['terms']:
            coefficients[e].SetCoefficient(positive[i],1)
            if i in negative: coefficients[e].SetCoefficient(negative[i],-1)
    for e,var in enumerate(upper): coefficients[e].SetCoefficient(var,1);rhs.SetCoefficient(var,1)
    started=time.monotonic()
    status=solver.Solve()
    result={'status':'NO_EXACT_CERTIFICATE','solver_status_code':status,'candidate_index':index,
            'preceding_primal_status':lp['status'],
            'candidate_sha256':sha256(path.read_bytes()).hexdigest(),'time_limit_seconds':30,
            'scope':'One complete overlap assignment, no disjoint compression totals. An exact certificate excludes only that assignment and its relabelings.'}
    if status==pywraplp.Solver.OPTIMAL:
        for denominator in (100,1000,10000,1000000,100000000):
            weights=[Fraction(round((positive[i].solution_value()-(negative[i].solution_value() if i in negative else 0))*denominator),denominator)
                     for i in range(len(groups))]
            bounds=[Fraction(max(0,round(var.solution_value()*denominator)),denominator) for var in upper]
            co=list(bounds)
            target=sum(bounds)
            valid=True
            for i,group in enumerate(groups):
                if not group['equality']: valid &= weights[i]>=0
                target+=weights[i]*group['target']
                for e in group['terms']: co[e]+=weights[i]
            for e,value in enumerate(co):
                if value<0: bounds[e]-=value;target-=value;co[e]=Fraction(0)
            if valid and target<0:
                scale=reduce(lcm,(v.denominator for v in weights+bounds),1)
                integer_weights=[int(v*scale) for v in weights]
                integer_bounds=[int(v*scale) for v in bounds]
                divisor=reduce(gcd,[abs(v) for v in integer_weights+integer_bounds if v])
                records=[{'kind':g['kind'],'coordinate':g['coordinate'],'multiplier':integer_weights[i]//divisor}
                         for i,g in enumerate(groups) if integer_weights[i]]
                bound_records=[{'edge':list(edgepairs[e]),'multiplier':v//divisor} for e,v in enumerate(integer_bounds) if v]
                result.update(status='EXACT_INTEGER_WEIGHTED_CAPACITY_CONTRADICTION',
                              group_multipliers=records,edge_upper_bound_multipliers=bound_records,
                              combined_rhs=int(target*scale/divisor),
                              group_support_size=len(records),upper_bound_support_size=len(bound_records),
                              positive_combined_coefficients=sum(v>0 for v in co),
                              producer_exact_integer_check=True)
                break
    result['elapsed_seconds']=time.monotonic()-started
    path.with_name(path.stem+'_farkas.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('group_multipliers','edge_upper_bound_multipliers')}))


if __name__=='__main__': main()
