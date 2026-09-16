"""Stdlib-only exact Farkas certificate audit, deriving all terms from K."""
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent


def main():
    cp=HERE/'scratch_next_overlap_farkas.json'
    result=json.loads(cp.read_bytes())
    assert result['status']=='EXACT_INTEGER_WEIGHTED_CAPACITY_CONTRADICTION'
    mp=HERE/'scratch_next_overlap_semantic_map.json'
    metadata=json.loads(mp.read_bytes())
    lp=HERE/'scratch_resume_overlap_lift.json'
    known=set(map(tuple,json.loads(lp.read_bytes())['overlap_edges_outer_zero_based']))
    labels=sorted((a,b) for a in range(14) for b in range(a+1,14) if a//2!=b//2)
    labels.sort(key=lambda pair:(pair[0]//2,pair[1]//2,*pair))
    supports=[{a//2,b//2} for a,b in labels]
    pairs=[pair for pair in combinations(range(84),2) if not supports[pair[0]]&supports[pair[1]]]
    var_of={pair:i+1 for i,pair in enumerate(pairs)}
    assert metadata['edge_variables']==[[v,*pair] for pair,v in var_of.items()]
    adjacent=[{v if u==x else u for u,v in known if x in (u,v)} for x in range(84)]
    coefficients=Counter()
    target=0
    records=[]
    for index,multiplier in result['group_multipliers'].items():
        assert type(multiplier) is int and multiplier!=0
        group=metadata['groups'][int(index)]
        if group['kind']=='label_quota':
            u,symbol=group['coordinate']
            bound=(1 if symbol//2 in supports[u] else 2)-sum(symbol in labels[v] for v in adjacent[u])
            terms=[var for (a,b),var in var_of.items()
                   if a==u and symbol in labels[b] or b==u and symbol in labels[a]]
            assert group['equality']
        else:
            assert group['kind']=='linear_pair_cap' and multiplier>0 and not group['equality']
            u,v=group['coordinate']
            bound=2-len(set(labels[u])&set(labels[v]))-int((u,v) in known)-len(adjacent[u]&adjacent[v])
            terms=[]
            for (a,b),var in var_of.items():
                multiplicity=int((a,b)==(u,v))
                multiplicity+=int(a==v and b in adjacent[u] or b==v and a in adjacent[u])
                multiplicity+=int(a==u and b in adjacent[v] or b==u and a in adjacent[v])
                terms += [var]*multiplicity
        assert sorted(terms)==sorted(group['terms']) and bound==group['target']
        for var in terms: coefficients[var]+=multiplier
        target+=multiplier*bound
        records.append({'kind':group['kind'],'coordinate':group['coordinate'],
                        'multiplier':multiplier,'bound':bound,'rhs_contribution':multiplier*bound})
    for var,multiplier in result['edge_upper_bound_multipliers'].items():
        assert 1<=int(var)<=len(pairs) and type(multiplier) is int and multiplier>0
        coefficients[int(var)]+=multiplier
        target+=multiplier
    assert all(coefficients[var]>=0 for var in range(1,len(pairs)+1))
    assert target<0 and str(target)==result['combined_rhs']
    assert {str(var):str(c) for var,c in coefficients.items() if c}==result['nonzero_edge_coefficients']
    output={'status':'INDEPENDENT_EXACT_FIXED_OVERLAP_CAPACITY_CONTRADICTION_PASS',
            'scope':'The prescribed overlap assignment has no nonnegative real disjoint-edge completion satisfying label quotas, linear pair caps, and edge upper bounds. No disjoint C totals are assumed; no global E0 exclusion.',
            'group_multiplier_histogram':dict(Counter(r['kind'] for r in records)),
            'nonzero_group_multipliers':len(records),
            'nonzero_edge_upper_bound_multipliers':len(result['edge_upper_bound_multipliers']),
            'combined_lhs_nonnegative':True,'combined_rhs':target,
            'positive_lhs_coefficients':sum(c>0 for c in coefficients.values()),
            'quota_vertices_used':sorted({r['coordinate'][0] for r in records if r['kind']=='label_quota'}),
            'constraint_vertices_used':sorted({v for r in records for v in
                 (r['coordinate'] if r['kind']=='linear_pair_cap' else [r['coordinate'][0]])}),
            'integer_multiplier_range':[min(r['multiplier'] for r in records),max(r['multiplier'] for r in records)],
            'semantic_constraints':records,
            'sha256':{p.name:sha256(p.read_bytes()).hexdigest() for p in (cp,mp,lp,Path(__file__))}}
    (HERE/'scratch_next_overlap_farkas_audit.json').write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in output.items() if k not in ('semantic_constraints','sha256')}))


if __name__=='__main__': main()
