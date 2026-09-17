"""Exact full99 star validation using the complete set of affected pairs.

Prerequisite B is a symmetric loopless99 graph satisfying all degree and
common-neighbor upper caps. Add only edges x-v, with v in S. A changed two-step
walk either has endpoint x, or has middle x and endpoints v in S and w in N_H(x).
Thus all pair counts outside {x,w} and {v,w}:v in S,w in N_H(x) remain identical
to B. Changed adjacency bounds also have endpoint x. The checker recomputes
every pair in that union from actual mutated bit rows, and checks all changed
degrees plus the14 exact root-neighbor quotas. No sampled pair test is used.
"""
from itertools import combinations
import audit_20260917_partial_matching as full

class StarValidator:
    def __init__(self,rows):
        full.require(len(rows)==99 and all(type(r)is int and 0<=r<1<<99 and not r>>u&1 for u,r in enumerate(rows)),'simple99 rows')
        full.require(all(bool(rows[u]>>v&1)==bool(rows[v]>>u&1)for u,v in combinations(range(99),2))and full.valid(rows),'valid fixed base')
        self.base=tuple(rows)
    def check(self,u,mask):
        if type(u)is not int or not 0<=u<84 or type(mask)is not int or not 0<=mask<1<<84 or mask>>u&1:return False
        x=u+15;selected=[v+15 for v in full.bits(mask)]
        if any(self.base[x]>>v&1 for v in selected):return False
        rows=list(self.base)
        for v in selected:rows[x]|=1<<v;rows[v]|=1<<x
        if rows[x].bit_count()!=14 or any(rows[v].bit_count()>14 for v in selected):return False
        neighbors=full.bits(rows[x]);pairs={tuple(sorted((x,w)))for w in range(99)if x!=w}
        pairs.update(tuple(sorted((v,w)))for v in selected for w in neighbors if v!=w)
        if any((rows[a]&rows[b]).bit_count()>2-int(bool(rows[a]>>b&1))for a,b in pairs):return False
        return all((rows[x]&rows[s]).bit_count()==2-int(bool(rows[x]>>s&1))for s in range(1,15))

def controls(B,labels,unknown,tables):
    validator=StarValidator(B);checks=[]
    for u in(0,12,60):
        pool={v if a==u else a for a,v in unknown if u in(a,v)}
        for i in sorted({0,len(tables[u])//2,len(tables[u])-1}):
            good=tables[u][i];selected=full.bits(good);outside=sorted(pool-set(selected));cases=[('positive',good),('missing_edge',good^(1<<selected[0]))]
            if outside:cases.extend([('extra_edge',good|(1<<outside[0])),('swapped_edge',good^(1<<selected[0])^(1<<outside[0]))])
            for name,mask in cases:
                expected=full.direct(B,labels,u,mask);observed=validator.check(u,mask);full.require(expected==observed,'affected/full pair disagreement')
                if name=='positive':full.require(expected,'positive calibration invalid')
                if name in('missing_edge','extra_edge'):full.require(not expected,'degree corruption accepted')
                checks.append(dict(center=u,original_id=i,case=name,full4851_result=expected,affected_pair_result=observed))
    # Invalid fixed bases must be rejected before unchanged-pair reasoning.
    bad=B.copy();bad[0]|=1
    try:StarValidator(bad)
    except ValueError:checks.append(dict(case='fixed_base_loop',outcome='REJECT'))
    else:raise ValueError('fixed loop accepted')
    return checks
