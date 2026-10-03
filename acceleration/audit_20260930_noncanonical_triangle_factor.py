"""Independent raw incidence check allowing an arbitrary outside-column order.

The only normalization is an explicitly checked bijection of the complete
first-fibre nonmatching-edge catalog. This module imports independent checking
code only; no discovery or encoding producer is imported.
"""
from itertools import combinations
import audit_20260930_variable_core_factor_object as base

def need(x,s):
    if not x:raise ValueError(s)

def canonicalize_and_check(core,factor,research=True):
    size=len(core);need(size%3==0 and size>0,'three equal nonempty fibres')
    n=size//3;width=n*(n-2)//2
    need(not research or n==12,'research core has exactly36 rows')
    need(len(core)==size and all(len(row)==size and all(type(x)is int and x in (0,1) for x in row)
         for row in core),'literal binary square core')
    need(all(core[i][i]==0 and all(core[i][j]==core[j][i] for j in range(size)) for i in range(size)),
         'symmetric zero-diagonal core')
    need(len(factor)==size and all(len(row)==width and all(type(x)is int and x in (0,1) for x in row)
         for row in factor),'literal binary incidence dimensions')
    need(all(core[a][b]==int(b==(a^1)) for a in range(n) for b in range(n)),'standard first matching')
    for g in (1,2):need(all(core[a][g*n+b]==int(a==b) for a in range(n) for b in range(n)),
                        'canonical first cross matchings')
    expected=list(combinations(range(n),2));expected=[pair for pair in expected if pair[1]!=(pair[0]^1)]
    columns=[tuple(a for a in range(n) if factor[a][d]) for d in range(width)]
    need(all(len(pair)==2 for pair in columns) and len(set(columns))==width and set(columns)==set(expected),
         'complete bijective first-fibre nonmatching-pair catalog')
    old_index={pair:d for d,pair in enumerate(columns)}
    new_to_old=[old_index[pair] for pair in expected]
    need(sorted(new_to_old)==list(range(width)),'explicit outside-label permutation')
    canonical=[[row[d] for d in new_to_old] for row in factor]
    m1=[row[n:2*n] for row in core[n:2*n]]
    m2=[row[2*n:] for row in core[2*n:]]
    p=[row[2*n:] for row in core[n:2*n]]
    checked=base.raw_factor(m1,m2,p,canonical,research=research)
    need(checked['core_adjacency']==core,'complete raw-core equality after decode')
    inverse=[None]*width
    for new,old in enumerate(new_to_old):inverse[old]=new
    need([[row[inverse[d]] for d in range(width)] for row in canonical]==factor,'complete factor relabel and inverse')
    return dict(raw_incidence_matrix=factor,canonical_new_to_raw_old_column=new_to_old,
                raw_old_to_canonical_new_column=inverse,canonical_factor=checked,
                normalization='Outside labels only; explicit bijective C0 catalog ordering.',target_graph=False)
