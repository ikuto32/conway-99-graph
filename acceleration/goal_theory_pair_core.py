"""Extract a small center-star support-intersection obstruction."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

from audit_certificate import full_graph,require


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate',type=Path,required=True)
    parser.add_argument('--domains',type=Path,required=True)
    parser.add_argument('--center',type=int,required=True)
    parser.add_argument('--neighbors',type=int,nargs='+',required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    require(not args.out.exists(),'Preserve previous core')
    data=json.loads(args.domains.read_bytes())
    adjacency,unknown=full_graph(json.loads(args.candidate.read_bytes()))
    vertices=sorted(set([args.center]+args.neighbors))
    require(len(vertices)==1+len(args.neighbors) and all(0<=u<84 for u in vertices),'Invalid core vertices')
    masks={u:[int(m,16) for m in data['domains'][u]['domain_masks_hex']] for u in vertices}
    rows={u:[sum(1<<v for v in adjacency[u+15])|(m<<15) for m in masks[u]] for u in vertices}
    relations=[]
    remaining=set(range(len(masks[args.center])))
    for v in args.neighbors:
        u=args.center
        pairs=[]
        for i,nu in enumerate(rows[u]):
            for j,nv in enumerate(rows[v]):
                edge=(nu>>(v+15))&1
                if edge==((nv>>(u+15))&1) and (nu&nv).bit_count()==2-edge:
                    pairs.append([i,j,edge])
        support=sorted({i for i,j,e in pairs})
        remaining.intersection_update(support)
        relations.append(dict(neighbor=v,compatible_domain_pairs=pairs,center_supported_domain_ids=support,
                              disjoint_support_variable_edge=tuple(sorted((u+15,v+15))) in unknown))
    require(not remaining,'Selected support sets do not contradict')
    result=dict(status='EXACT_COMPLETED_NEIGHBORHOOD_SUPPORT_INTERSECTION_CORE',
        candidate_sha256=sha256(args.candidate.read_bytes()).hexdigest(),center=args.center,
        domains=[data['domains'][u] for u in vertices],relations=relations,center_support_intersection=[],
        inputs_sha256={str(p):sha256(p.read_bytes()).hexdigest() for p in(args.candidate,args.domains,Path(__file__))},
        scope='Complete local-star choices at the center have disjoint support sets under exact final pair-count conditions. This excludes only the specified fixed overlap assignment.')
    with args.out.open('x',encoding='utf-8') as stream:
        stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(center=args.center,vertices=vertices,domain_sizes={u:len(masks[u]) for u in vertices},relations=relations)))


if __name__=='__main__':
    main()
