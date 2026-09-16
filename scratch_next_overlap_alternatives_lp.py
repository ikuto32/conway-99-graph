"""Bounded continuous completion relaxation for one audited alternative."""
import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
import json
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
    audit=json.loads(path.with_name(path.stem+'_audit.json').read_bytes())
    assert audit['status']=='INDEPENDENT_ALTERNATIVE_OVERLAP_AUDIT_PASS'
    assert audit['input_sha256']==sha256(path.read_bytes()).hexdigest()
    if audit['existing_capacity_cut']['excluded_by_this_cut']:
        raise ValueError('already excluded by exact cut; no LP run needed')
    known=set(map(tuple,json.loads(path.read_bytes())['overlap_edges_outer_zero_based']))
    labels=[(2*a+s,2*b+t) for a,b in combinations(range(7),2) for s in range(2) for t in range(2)]
    supports=[{a//2,b//2} for a,b in labels]
    outer=[set() for _ in range(84)]
    for u,v in known: outer[u].add(v);outer[v].add(u)
    candidates=[pair for pair in combinations(range(84),2) if not supports[pair[0]]&supports[pair[1]]]
    candidate_set=set(candidates)
    constraints=[]
    for u in range(84):
        for symbol in range(14):
            target=(1 if symbol//2 in supports[u] else 2)-sum(symbol in labels[v] for v in outer[u])
            terms=[tuple(sorted((u,v))) for v in range(84) if symbol in labels[v] and tuple(sorted((u,v))) in candidate_set]
            constraints.append((terms,target,True))
    for u,v in combinations(range(84),2):
        target=2-len(set(labels[u])&set(labels[v]))-int((u,v) in known)-len(outer[u]&outer[v])
        terms=[(u,v)] if (u,v) in candidate_set else []
        terms += [tuple(sorted((v,w))) for w in outer[u] if tuple(sorted((v,w))) in candidate_set]
        terms += [tuple(sorted((u,w))) for w in outer[v] if tuple(sorted((u,w))) in candidate_set]
        assert len(terms)==len(set(terms))
        constraints.append((terms,target,False))
    solver=pywraplp.Solver.CreateSolver('GLOP')
    solver.SetTimeLimit(30000)
    x={pair:solver.NumVar(0,1,f'e{pair[0]}_{pair[1]}') for pair in candidates}
    for terms,target,equality in constraints:
        row=solver.Constraint(target if equality else -solver.infinity(),target)
        for pair in terms: row.SetCoefficient(x[pair],1)
    started=time.monotonic()
    status=solver.Solve()
    result={'candidate_index':index,'candidate_sha256':sha256(path.read_bytes()).hexdigest(),
            'status_code':status,'solver_elapsed_seconds':time.monotonic()-started,
            'linear_constraints':len(constraints),'disjoint_block_totals_assumed':False,
            'status':('LP_INFEASIBLE_NO_CHECKED_PROOF' if status==pywraplp.Solver.INFEASIBLE else
                      'LP_ABNORMAL_NO_CONCLUSION' if status==pywraplp.Solver.ABNORMAL else 'LP_UNKNOWN'),
            'scope':'Continuous unknown disjoint edges only; one fixed audited overlap assignment. No full graph or certified infeasibility unless a separate exact certificate is checked.'}
    if status==pywraplp.Solver.OPTIMAL:
        for bound in (16,1000,1000000,1000000000):
            rational={pair:Fraction(v.solution_value()).limit_denominator(bound) for pair,v in x.items()}
            valid=all(0<=v<=1 for v in rational.values())
            for terms,target,equality in constraints:
                total=sum(rational[pair] for pair in terms)
                valid &= total==target if equality else total<=target
            if valid:
                result.update(status='EXACT_RATIONAL_LINEAR_RELAXATION_WITNESS',
                              fractional_edges=sum(v.denominator!=1 for v in rational.values()),
                              denominator_histogram=dict(Counter(v.denominator for v in rational.values())),
                              disjoint_edge_values=[[u,v,str(rational[u,v])] for u,v in candidates])
                break
        else: result['status']='NUMERIC_LP_FEASIBLE_EXACT_RECONSTRUCTION_FAILED'
    path.with_name(path.stem+'_lp.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('disjoint_edge_values','denominator_histogram')}))


if __name__=='__main__': main()
