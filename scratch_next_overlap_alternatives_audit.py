"""Independent stdlib partial-graph/sign-orbit audit of an alternative."""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path

from scratch_next_overlap_cut import evaluate

HERE=Path(__file__).resolve().parent


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('index',type=int,choices=range(4))
    index=parser.parse_args().index
    path=HERE/f'scratch_next_overlap_alternatives_r{index}.json'
    data=json.loads(path.read_bytes())
    assert data['status'] in ('OPTIMAL','FEASIBLE')
    cp=HERE/'scratch_resume_integral_compression.json'
    assert sha256(cp.read_bytes()).hexdigest()==data['input_sha256']
    c=json.loads(cp.read_bytes())['C']
    labels=sorted((a,b) for a in range(14) for b in range(a+1,14) if a//2!=b//2)
    labels.sort(key=lambda x:(x[0]//2,x[1]//2,*x))
    vertex_of={pair:i for i,pair in enumerate(labels)}
    supports=[{a//2,b//2} for a,b in labels]
    known=set(map(tuple,data['overlap_edges_outer_zero_based']))
    assert len(known)==len(data['overlap_edges_outer_zero_based'])==168
    neighbors=[set() for _ in range(99)]
    def put(u,v): neighbors[u].add(v);neighbors[v].add(u)
    for u in range(1,15): put(0,u)
    for u in range(1,15,2): put(u,u+1)
    for u,pair in enumerate(labels):
        for label in pair: put(u+15,label+1)
    totals=Counter()
    outer=[set() for _ in range(84)]
    for u,v in known:
        assert type(u) is int and type(v) is int and 0<=u<v<84 and len(supports[u]&supports[v])==1
        put(u+15,v+15)
        outer[u].add(v);outer[v].add(u)
        totals[u//4,v//4]+=1
    assert all(len(row)==4 for row in outer)
    for f,h in combinations(range(21),2):
        if supports[4*f]&supports[4*h]: assert totals[f,h]==c[f][h]
    for u in range(84):
        for symbol in range(14):
            count=sum(symbol in labels[v] for v in outer[u])
            assert count==1 if symbol//2 in supports[u] else count<=2
    assert all(len(neighbors[u]&neighbors[v])<=(1 if v in neighbors[u] else 2)
               for u,v in combinations(range(99),2))
    source_paths=[HERE/'scratch_resume_overlap_lift.json']+[HERE/f'scratch_next_overlap_alternatives_r{i}.json' for i in range(index)]
    excluded=set()
    for source in source_paths:
        assert data['excluded_source_hashes'][source.name]==sha256(source.read_bytes()).hexdigest()
        source_edges=set(map(tuple,json.loads(source.read_bytes())['overlap_edges_outer_zero_based']))
        for flips in range(128):
            mapping={u:vertex_of[tuple(label^((flips>>(label//2))&1) for label in pair)] for u,pair in enumerate(labels)}
            excluded.add(tuple(sorted(tuple(sorted((mapping[u],mapping[v]))) for u,v in source_edges)))
    assert tuple(sorted(known)) not in excluded
    assert len(excluded)==data['distinct_sign_orbit_assignments_excluded']
    result={'status':'INDEPENDENT_ALTERNATIVE_OVERLAP_AUDIT_PASS','input_sha256':sha256(path.read_bytes()).hexdigest(),
            'candidate_index':index,'overlap_edges':168,'exposed_edges':sum(map(len,neighbors))//2,
            'degree_histogram':dict(Counter(map(len,neighbors))),'pair_caps_checked':4851,
            'sign_orbit_distinct_from_original_and_predecessors':True,
            'excluded_orbit_assignments':len(excluded),'existing_capacity_cut':evaluate(known),
            'scope':'Partial357-edge graph at fixed C; distinct under root-group sign flips only, not all possible isomorphisms. No full graph.'}
    path.with_name(path.stem+'_audit.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result))


if __name__=='__main__': main()
