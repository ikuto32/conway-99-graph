"""Evaluate one certified weighted-capacity cut on an overlap assignment.

Negative score forbids completion with zero same-fiber edges. All unlisted
overlapping-support pairs must be fixed absent: this is not a test on a
partial overlap search prefix. A nonnegative score says only that this one
necessary inequality did not reject the input. The input format is
overlap_edges_outer_zero_based, as in the saved lift.
"""
import argparse
from itertools import combinations
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent


def evaluate(known):
    certificate=json.loads((HERE/'scratch_next_overlap_farkas.json').read_bytes())
    metadata=json.loads((HERE/'scratch_next_overlap_semantic_map.json').read_bytes())
    labels=[(2*a+s,2*b+t) for a,b in combinations(range(7),2) for s in range(2) for t in range(2)]
    supports=[{a//2,b//2} for a,b in labels]
    edges=[(u,v) for u,v in combinations(range(84),2) if not supports[u]&supports[v]]
    variables={pair:i+1 for i,pair in enumerate(edges)}
    rows=[set() for _ in range(84)]
    for u,v in known:
        if type(u) is not int or type(v) is not int or not 0<=u<v<84 or len(supports[u]&supports[v])!=1:
            raise ValueError('input must contain distinct canonical overlapping-support edges')
        rows[u].add(v)
        rows[v].add(u)
    coefficients={e:0 for e in variables.values()}
    rhs=0
    for index,multiplier in certificate['group_multipliers'].items():
        group=metadata['groups'][int(index)]
        if group['kind']=='label_quota':
            u,symbol=group['coordinate']
            rhs+=multiplier*((1 if symbol//2 in supports[u] else 2)-sum(symbol in labels[v] for v in rows[u]))
            for v in range(84):
                key=tuple(sorted((u,v)))
                if key in variables and symbol in labels[v]: coefficients[variables[key]]+=multiplier
        else:
            assert group['kind']=='linear_pair_cap' and multiplier>=0
            u,v=group['coordinate']
            rhs+=multiplier*(2-len(set(labels[u])&set(labels[v]))-int((u,v) in known)-len(rows[u]&rows[v]))
            if (u,v) in variables: coefficients[variables[u,v]]+=multiplier
            for w in rows[u]:
                key=tuple(sorted((v,w)))
                if key in variables: coefficients[variables[key]]+=multiplier
            for w in rows[v]:
                key=tuple(sorted((u,w)))
                if key in variables: coefficients[variables[key]]+=multiplier
    for variable,multiplier in certificate['edge_upper_bound_multipliers'].items():
        assert multiplier>=0
        coefficients[int(variable)]+=multiplier
        rhs+=multiplier
    lower=sum(min(0,value) for value in coefficients.values())
    return {'status':'WEIGHTED_CAPACITY_CUT_EVALUATED','score':rhs-lower,
            'combined_rhs':rhs,'box_lower_bound_for_lhs':lower,
            'excluded_by_this_cut':rhs<lower,
            'scope':'Necessary inequality for this overlap assignment with same-fiber edges absent; does not depend on disjoint compression totals. Passing is not a graph certificate.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path',nargs='?',type=Path,default=HERE/'scratch_resume_overlap_lift.json')
    args=parser.parse_args()
    raw=json.loads(args.path.read_bytes())['overlap_edges_outer_zero_based']
    known=set(map(tuple,raw))
    if len(known)!=len(raw): raise ValueError('duplicate edges')
    print(json.dumps(evaluate(known)))


if __name__=='__main__': main()
