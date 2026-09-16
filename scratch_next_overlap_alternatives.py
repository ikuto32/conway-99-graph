"""Copy of the overlap-lift model, with bounded sign-orbit exclusions.

Generate one requested candidate index. All old artifacts are read-only.
Each solve has one worker and a hard45-second CP-SAT time limit.
"""
import argparse
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
    parser.add_argument('index',type=int,choices=range(4))
    args=parser.parse_args()
    outpath=HERE/f'scratch_next_overlap_alternatives_r{args.index}.json'
    assert not outpath.exists(), 'do not overwrite or extend an existing candidate run'
    cp=HERE/'scratch_resume_integral_compression.json'
    c=json.loads(cp.read_bytes())['C']
    supports=list(combinations(range(7),2))
    labels=[(2*a+s,2*b+t) for a,b in supports for s in range(2) for t in range(2)]
    model=cp_model.CpModel()
    edges={(u,v):model.new_bool_var(f'e_{u}_{v}') for u,v in combinations(range(84),2)
           if len(set(supports[u//4])&set(supports[v//4]))==1}
    def edge(u,v): return edges.get(tuple(sorted((u,v))))
    for f,h in combinations(range(21),2):
        if set(supports[f])&set(supports[h]):
            model.add(sum(edge(u,v) for u in range(4*f,4*f+4) for v in range(4*h,4*h+4))==c[f][h])
    for u,label in enumerate(labels):
        for symbol in range(14):
            terms=[edge(u,v) for v in range(84) if symbol in labels[v] and edge(u,v) is not None]
            if symbol//2 in supports[u//4]: model.add(sum(terms)==1)
            else: model.add(sum(terms)<=2)
    products=0
    for u,v in combinations(range(84),2):
        terms=[]
        for w in range(84):
            a,b=edge(u,w),edge(v,w)
            if a is not None and b is not None:
                z=model.new_bool_var(f'p_{u}_{v}_{w}')
                model.add_bool_or([a.Not(),b.Not(),z])
                terms.append(z)
                products+=1
        if edge(u,v) is not None: terms.append(edge(u,v))
        model.add(sum(terms)<=2-len(set(labels[u])&set(labels[v])))
    sources=[HERE/'scratch_resume_overlap_lift.json']
    for index in range(args.index):
        path=HERE/f'scratch_next_overlap_alternatives_r{index}.json'
        previous=json.loads(path.read_bytes())
        assert previous['status'] in ('OPTIMAL','FEASIBLE'), 'do not extend UNKNOWN or excluded pool'
        audit=json.loads(path.with_name(path.stem+'_audit.json').read_bytes())
        assert audit['status']=='INDEPENDENT_ALTERNATIVE_OVERLAP_AUDIT_PASS'
        sources.append(path)
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
            transformed=tuple(sorted(tuple(sorted((permutation[u],permutation[v]))) for u,v in original))
            excluded.add(transformed)
    for forbidden in sorted(excluded):
        # Every feasible overlap assignment has168 edges. Consequently
        # this clause excludes exactly the specified complete assignment.
        model.add(sum(edges[pair] for pair in forbidden)<=167)
    solver=cp_model.CpSolver()
    solver.parameters.max_time_in_seconds=45
    solver.parameters.num_search_workers=1
    solver.parameters.random_seed=99300+args.index
    started=time.monotonic()
    status=solver.solve(model)
    result={'status':solver.status_name(status),'index':args.index,'elapsed_seconds':time.monotonic()-started,
            'input_sha256':sha256(cp.read_bytes()).hexdigest(),'excluded_source_hashes':source_hashes,
            'distinct_sign_orbit_assignments_excluded':len(excluded),'edge_variables':len(edges),
            'one_way_products':products,'solver_workers':1,'solver_time_limit_seconds':45,
            'scope':'One overlap candidate at fixed sharp C, excluding original and preceding candidates under128 root-group sign flips; no graph or global exclusion.'}
    if status in (cp_model.OPTIMAL,cp_model.FEASIBLE):
        result['overlap_edges_outer_zero_based']=[list(pair) for pair,var in edges.items() if solver.value(var)]
        assert len(result['overlap_edges_outer_zero_based'])==168
    outpath.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='overlap_edges_outer_zero_based'}))


if __name__=='__main__': main()
