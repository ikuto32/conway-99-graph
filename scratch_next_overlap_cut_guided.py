"""Single45-second overlap run with five compiled exact capacity cuts.

The base is copied from the audited overlap generator. No LP/dual run or
submission export occurs. This script refuses to overwrite a prior result.
"""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import sys
import time

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'.ortools'))
from ortools.sat.python import cp_model


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--compiled-sha256',required=True)
    expected_sha=parser.parse_args().compiled_sha256.lower()
    out=HERE/'scratch_next_overlap_cut_guided.json'
    assert not out.exists(), 'one run only: do not overwrite or extend UNKNOWN'
    compiled_path=HERE/'scratch_next_overlap_cut_compiled.json'
    raw=compiled_path.read_bytes()
    assert sha256(raw).hexdigest()==expected_sha
    compiled=json.loads(raw)
    assert compiled['status']=='EXACT_NO_GAMMA_CAPACITY_POLYNOMIAL_COMPILER_CHECK_PASS'
    assert len(compiled['cuts'])==5
    for name,digest in compiled['input_sha256'].items():
        assert sha256((HERE/name).read_bytes()).hexdigest()==digest
    cp=HERE/'scratch_resume_integral_compression.json'
    c=json.loads(cp.read_bytes())['C']
    supports=list(combinations(range(7),2))
    labels=[(2*a+s,2*b+t) for a,b in supports for s in range(2) for t in range(2)]
    model=cp_model.CpModel()
    edges={(u,v):model.new_bool_var(f'e_{u}_{v}') for u,v in combinations(range(84),2)
           if len(set(supports[u//4])&set(supports[v//4]))==1}
    assert compiled['overlap_variables']==[[i+1,*pair] for i,pair in enumerate(edges)]
    overlap_by_id={i+1:var for i,var in enumerate(edges.values())}
    def edge(u,v): return edges.get(tuple(sorted((u,v))))
    for f,h in combinations(range(21),2):
        if set(supports[f])&set(supports[h]):
            model.add(sum(edge(u,v) for u in range(4*f,4*f+4) for v in range(4*h,4*h+4))==c[f][h])
    for u,label in enumerate(labels):
        for symbol in range(14):
            terms=[edge(u,v) for v in range(84) if symbol in labels[v] and edge(u,v) is not None]
            if symbol//2 in supports[u//4]: model.add(sum(terms)==1)
            else: model.add(sum(terms)<=2)
    products={}
    for u,v in combinations(range(84),2):
        terms=[]
        for w in range(84):
            a,b=edge(u,w),edge(v,w)
            if a is not None and b is not None:
                z=model.new_bool_var(f'p_{u}_{v}_{w}')
                model.add_bool_or([a.Not(),b.Not(),z])
                products[u,v,w]=z
                terms.append(z)
        if edge(u,v) is not None: terms.append(edge(u,v))
        model.add(sum(terms)<=2-len(set(labels[u])&set(labels[v])))
    assert len(products)==compiled['existing_generator_products']==65520
    sources=[HERE/'scratch_resume_overlap_lift.json']+[HERE/f'scratch_next_overlap_alternatives_r{i}.json' for i in range(4)]
    excluded=set()
    source_hashes={}
    for path in sources:
        source_hashes[path.name]=sha256(path.read_bytes()).hexdigest()
        original=set(map(tuple,json.loads(path.read_bytes())['overlap_edges_outer_zero_based']))
        assert len(original)==168
        for mask in range(128):
            permutation=[]
            for u in range(84):
                a,b=supports[u//4]
                s,t=divmod(u%4,2)
                permutation.append(4*(u//4)+2*(s^((mask>>a)&1))+(t^((mask>>b)&1)))
            excluded.add(tuple(sorted(tuple(sorted((permutation[u],permutation[v]))) for u,v in original)))
    assert len(excluded)==640
    for forbidden in sorted(excluded): model.add(sum(edges[pair] for pair in forbidden)<=167)
    modes=Counter()
    used_products=set()
    modeled_cuts=[]
    for cut in compiled['cuts']:
        rhs=cut['R_constant']+sum(weight*overlap_by_id[var] for var,weight in cut['R_linear'])
        for u,v,w,weight in cut['R_products']:
            assert weight<0 and (u,v,w) in products
            rhs+=weight*products[u,v,w]
            used_products.add((u,v,w))
        z_terms=[]
        assert len(cut['w_affine'])==1680
        for row in cut['w_affine']:
            w=row['constant']+sum(weight*overlap_by_id[var] for var,weight in row['terms'])
            assert all(weight>0 for var,weight in row['terms'])
            lo=row['constant']
            hi=lo+sum(weight for var,weight in row['terms'])
            assert (lo,hi)==(row['w_lower'],row['w_upper'])
            assert row['z_upper']==max(0,-lo)
            mode=row['mode']
            modes[mode]+=1
            if mode=='zero':
                assert lo>=0
            elif mode=='affine_negative':
                assert hi<=0
                z_terms.append(-w)
            else:
                assert mode=='exact_max' and lo<0<hi
                z=model.new_int_var(0,row['z_upper'],f'z_{cut["name"]}_{row["disjoint_id"]}')
                model.add_max_equality(z,[0,-w])
                z_terms.append(z)
        z_total=sum(z_terms)
        model.add(rhs+z_total>=0)
        modeled_cuts.append((cut['name'],rhs,z_total))
    assert len(used_products)==compiled['products_used_by_five_cut_union']
    validation=model.validate()
    assert not validation, validation
    provenance={'compiled_sha256':expected_sha,'compiled_input_sha256':compiled['input_sha256'],
                'compression_sha256':sha256(cp.read_bytes()).hexdigest(),
                'excluded_source_hashes':source_hashes,'distinct_sign_images_excluded':640,
                'overlap_edge_variables':1680,'one_way_products':len(products),
                'products_used_by_cuts':len(used_products),'max_modes':dict(modes),
                'capacity_cuts':5,'solver_workers':1,'time_limit_seconds':45,
                'model_validation':'PASS'}
    (HERE/'scratch_next_overlap_cut_guided_model.json').write_text(json.dumps(provenance,indent=2)+'\n',encoding='utf-8')
    solver=cp_model.CpSolver()
    solver.parameters.max_time_in_seconds=45
    solver.parameters.num_search_workers=1
    solver.parameters.random_seed=99450
    started=time.monotonic()
    status=solver.solve(model)
    result={'status':solver.status_name(status),'elapsed_seconds':time.monotonic()-started,**provenance,
            'scope':'One complete overlap assignment at saved sharp C satisfying five unrelabeled no-gamma necessary cuts, with640 known sign images excluded. No graph, LP, dual, or global exclusion.'}
    if status in (cp_model.OPTIMAL,cp_model.FEASIBLE):
        result['overlap_edges_outer_zero_based']=[list(pair) for pair,var in edges.items() if solver.value(var)]
        assert len(result['overlap_edges_outer_zero_based'])==168
        result['modeled_cut_values']=[{'name':name,'R':int(solver.value(rhs)),
                                     'z_total':int(solver.value(z_total)),
                                     'score':int(solver.value(rhs+z_total))}
                                    for name,rhs,z_total in modeled_cuts]
    result['solver_response_stats']=solver.response_stats()
    assert sha256(compiled_path.read_bytes()).hexdigest()==expected_sha
    for name,digest in compiled['input_sha256'].items():
        assert sha256((HERE/name).read_bytes()).hexdigest()==digest
    out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('overlap_edges_outer_zero_based','compiled_input_sha256','solver_response_stats','excluded_source_hashes')}))


if __name__=='__main__': main()
