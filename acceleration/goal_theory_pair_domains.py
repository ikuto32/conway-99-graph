"""Bounded arc consistency using exact completed-neighborhood pair counts.

The input must have independently audited complete local-star domains. A pair
of domains is compatible only when its edge decision reciprocates and its two
full neighborhoods intersect in exactly one or two vertices as required.
"""
import argparse
from collections import deque
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import time

from audit_certificate import full_graph,require


class PairCap(Exception):
    pass


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate',type=Path,required=True)
    parser.add_argument('--domains',type=Path,required=True)
    parser.add_argument('--domain-audit',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--seconds',type=float,default=30)
    parser.add_argument('--pair-cap',type=int,default=10000000)
    args=parser.parse_args()
    require(not args.out.exists(),'Preserve previous pair result')
    require(args.seconds>0 and args.pair_cap>0,'Positive caps required')
    data,audit=(json.loads(p.read_bytes()) for p in(args.domains,args.domain_audit))
    require(audit['status']=='INDEPENDENT_COMPLETE_STAR_DOMAINS_AND_RECIPROCITY_AUDIT_PASS' and audit['complete_domain_enumeration_verified'],'Complete audited domains required')
    require(sha256(args.domains.read_bytes()).hexdigest() in audit['inputs_sha256'].values(),'Audit does not bind domain bytes')
    for name,digest in audit['inputs_sha256'].items():
        require(sha256(Path(name).read_bytes()).hexdigest()==digest,'Domain audit input changed')
    require(data['candidate_sha256']==sha256(args.candidate.read_bytes()).hexdigest(),'Wrong domain candidate')
    adjacency,unknown=full_graph(json.loads(args.candidate.read_bytes()))
    domains=[[int(mask,16) for mask in row['domain_masks_hex']] for row in data['domains']]
    require(len(domains)==84 and all(domains),'All initial domains must be nonempty')
    fixed=[sum(1<<v for v in adjacency[u+15]) for u in range(84)]
    neighborhoods=[[fixed[u] | (mask<<15) for mask in domains[u]] for u in range(84)]
    active=[(1<<len(row))-1 for row in domains]
    pairs=sorted(combinations(range(84),2),key=lambda pair:(len(domains[pair[0]])*len(domains[pair[1]]),pair))
    queue=deque((u,v) for a,b in pairs for u,v in((a,b),(b,a)))
    queued=set(queue)
    relations={}
    events=[]
    started=time.perf_counter()
    deadline=started+args.seconds
    checks=0

    def relation(u,v):
        nonlocal checks
        if (u,v) in relations:
            return relations[u,v]
        left=[0]*len(domains[u])
        right=[0]*len(domains[v])
        for i,nu in enumerate(neighborhoods[u]):
            if time.perf_counter()>deadline:
                raise PairCap('TIME_CAP')
            for j,nv in enumerate(neighborhoods[v]):
                checks+=1
                if checks>args.pair_cap:
                    raise PairCap('DOMAIN_PAIR_CAP')
                edge=(nu>>(v+15))&1
                if edge==((nv>>(u+15))&1) and (nu&nv).bit_count()==2-edge:
                    left[i] |= 1<<j
                    right[j] |= 1<<i
        relations[u,v]=left
        relations[v,u]=right
        return left

    status='ARC_CONSISTENT_NONEMPTY'
    empty=None
    cap_reason=None
    try:
        while queue:
            if time.perf_counter()>deadline:
                raise PairCap('TIME_CAP')
            u,v=queue.popleft()
            queued.discard((u,v))
            support=relation(u,v)
            removed=[i for i in range(len(domains[u])) if (active[u]>>i)&1 and not(support[i]&active[v])]
            if removed:
                before=active[u].bit_count()
                for i in removed:
                    active[u] &= ~(1<<i)
                events.append(dict(target_vertex=u,support_vertex=v,removed_domain_ids=removed,
                                   before_count=before,after_count=active[u].bit_count()))
                if not active[u]:
                    status='EMPTY_DOMAIN'
                    empty=u
                    break
                for w in range(84):
                    if w!=u and (w,u) not in queued:
                        queue.append((w,u))
                        queued.add((w,u))
    except PairCap as error:
        status='INCOMPLETE'
        cap_reason=str(error)
    result=dict(status='EXACT_PAIR_DOMAIN_'+status,complete_initial_domains_audited=True,
        candidate_sha256=sha256(args.candidate.read_bytes()).hexdigest(),
        inputs_sha256={str(p):sha256(p.read_bytes()).hexdigest() for p in(args.candidate,args.domains,args.domain_audit,Path(__file__))},
        caps=dict(seconds=args.seconds,domain_pairs=args.pair_cap),cap_reason=cap_reason,
        propagation_status=status,empty_vertex=empty,events=events,
        surviving_domain_ids=[[i for i in range(len(domains[u])) if(active[u]>>i)&1] for u in range(84)],
        domain_pairs_evaluated=checks,vertex_pair_relations_built=len(relations)//2,
        elapsed_seconds=time.perf_counter()-started,
        scope='Exact full-neighborhood count and reciprocity constraints between stars of one fixed overlap assignment. Arc consistency is necessary, not sufficient for a global simultaneous choice. A cap gives no exclusion.')
    with args.out.open('x',encoding='utf-8') as stream:
        stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in('events','surviving_domain_ids')}|dict(deletion_events=len(events))))


if __name__=='__main__':
    main()
