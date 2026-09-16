"""Verify an exact pair-count support core using complete independent searches."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import time

from audit_certificate import full_graph,require
from audit_goal_theory_domains import enumerate_direct


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate',type=Path,required=True)
    parser.add_argument('--core',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    require(not args.out.exists(),'Preserve previous core audit')
    started=time.perf_counter()
    data=json.loads(args.core.read_bytes())
    require(data['candidate_sha256']==sha256(args.candidate.read_bytes()).hexdigest(),'Candidate binding')
    adjacency,unknown=full_graph(json.loads(args.candidate.read_bytes()))
    vertices=[r['outer_vertex'] for r in data['domains']]
    require(vertices==sorted(set(vertices)) and all(type(u) is int and 0<=u<84 for u in vertices),'Invalid vertex list')
    budget=dict(nodes=0,node_cap=3000000,domain_cap=20000,deadline=started+30)
    neighborhoods={}
    for record in data['domains']:
        u=record['outer_vertex']
        require(record['status']=='COMPLETE' and record['cap_reason'] is None,'Incomplete core domain')
        actual,nodes=enumerate_direct(adjacency,unknown,u,budget)
        require(actual==[int(m,16) for m in record['domain_masks_hex']],'Incomplete or incorrect domain')
        neighborhoods[u]=[adjacency[u+15]|{v+15 for v in range(84) if mask>>v&1} for mask in actual]
    u=data['center']
    require(u in neighborhoods and neighborhoods[u],'Invalid center domain')
    remaining=set(range(len(neighborhoods[u])))
    checked=[]
    seen=set()
    for relation in data['relations']:
        v=relation['neighbor']
        require(v in neighborhoods and v!=u and v not in seen,'Invalid relation neighbor')
        seen.add(v)
        actual=[]
        for i,nu in enumerate(neighborhoods[u]):
            for j,nv in enumerate(neighborhoods[v]):
                adjacent=v+15 in nu
                if adjacent==(u+15 in nv) and len(nu&nv)==(1 if adjacent else 2):
                    actual.append([i,j,int(adjacent)])
        supported=sorted({i for i,j,e in actual})
        require(actual==relation['compatible_domain_pairs'] and supported==relation['center_supported_domain_ids'],'Wrong pair relation')
        disjoint=tuple(sorted((u+15,v+15))) in unknown
        require(relation['disjoint_support_variable_edge'] is disjoint,'Wrong pair type')
        remaining.intersection_update(supported)
        checked.append(dict(center=u,neighbor=v,domain_pairs_checked=len(neighborhoods[u])*len(neighborhoods[v]),
                            compatible_pairs=len(actual),center_support_ids=supported,
                            adjacency_values=sorted({e for i,j,e in actual}),disjoint_support_pair=disjoint))
    require(not remaining and data['center_support_intersection']==[],'No support contradiction')
    result=dict(status='INDEPENDENT_EXACT_PAIR_SUPPORT_CORE_AUDIT_PASS',
        inputs_sha256={str(p):sha256(p.read_bytes()).hexdigest() for p in(args.candidate,args.core,Path(__file__),Path(__file__).with_name('audit_goal_theory_domains.py'),Path(__file__).with_name('audit_goal_theory_stars.py'),Path(__file__).with_name('audit_certificate.py'))},
        independently_complete_domain_sizes={str(u):len(rows) for u,rows in neighborhoods.items()},
        relations=checked,independent_domain_search_nodes=budget['nodes'],producer_or_solver_imported=False,
        elapsed_seconds=time.perf_counter()-started,
        scope='Three or more individually complete star domains need not have a jointly compatible center choice. This exact finite core excludes only its bound fixed overlap assignment.')
    with args.out.open('x',encoding='utf-8') as stream:
        stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':
    main()
