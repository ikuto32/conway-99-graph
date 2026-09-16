"""Independent set-based pair-domain proof replay with complete local searches.

No pair producer is imported. For a contradiction, independently re-enumerate
every domain used by a deletion. Full neighborhoods are ordinary Python sets,
and compatibility is derived directly from adjacency and exact intersections.
"""
import argparse
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import time

from audit_certificate import full_graph,require
from audit_goal_theory_domains import enumerate_direct,AuditCap


def compatible(u,nu,v,nv):
    edge=v+15 in nu
    return edge==(u+15 in nv) and len(nu&nv)==(1 if edge else 2)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate',type=Path,required=True)
    parser.add_argument('--domains',type=Path,required=True)
    parser.add_argument('--pair-certificate',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--seconds',type=float,default=30)
    args=parser.parse_args()
    require(not args.out.exists(),'Preserve previous audit')
    started=time.perf_counter()
    saved=json.loads(args.domains.read_bytes())
    proof=json.loads(args.pair_certificate.read_bytes())
    candidate_digest=sha256(args.candidate.read_bytes()).hexdigest()
    require(saved.get('candidate_sha256',candidate_digest)==candidate_digest,'Wrong domain candidate')
    require(proof.get('candidate_sha256',candidate_digest)==candidate_digest,'Wrong proof candidate')
    for name,digest in proof.get('inputs_sha256',{}).items():
        require(sha256(Path(name).read_bytes()).hexdigest()==digest,'Pair certificate input changed')
    adjacency,unknown=full_graph(json.loads(args.candidate.read_bytes()))
    domains=[[int(mask,16) for mask in row['domain_masks_hex']] for row in saved['domains']]
    require(len(domains)==84,'Expected84 domains')
    status=proof['propagation_status']
    result=dict(inputs_sha256={str(p):sha256(p.read_bytes()).hexdigest() for p in(args.candidate,args.domains,args.pair_certificate,Path(__file__),Path(__file__).with_name('audit_goal_theory_domains.py'),Path(__file__).with_name('audit_goal_theory_stars.py'),Path(__file__).with_name('audit_certificate.py'))},
        producer_or_solver_imported=False,complete_used_domains_verified=False,
        scope='Fixed overlap assignment only. Exact reciprocal completed-neighborhood pair counts are necessary. Nonempty arc consistency is not a simultaneous graph choice; incomplete audits give no exclusion.')
    if status=='INCOMPLETE':
        result['status']='INCOMPLETE_PAIR_SEARCH_NO_EXCLUSION'
    else:
        require(status in('EMPTY_DOMAIN','ARC_CONSISTENT_NONEMPTY'),'Unknown propagation status')
        used=sorted({v for event in proof['events'] for v in(event['target_vertex'],event['support_vertex'])})
        if status=='EMPTY_DOMAIN':
            used=sorted(set(used)|{proof['empty_vertex']})
        else:
            used=list(range(84))
        require(all(type(v) is int and 0<=v<84 for v in used),'Invalid proof vertices')
        budget=dict(nodes=0,node_cap=3000000,domain_cap=20000,deadline=started+args.seconds)
        complete=[]
        try:
            for u in used:
                actual,nodes=enumerate_direct(adjacency,unknown,u,budget)
                require(actual==domains[u],f'Incomplete or invalid domain {u}')
                complete.append(dict(outer_vertex=u,domain_size=len(actual),nodes=nodes))
            neighborhoods={u:[adjacency[u+15] | {v+15 for v in range(84) if mask>>v&1} for mask in domains[u]] for u in used}
            active=[set(range(len(row))) for row in domains]
            checks=0
            for event in proof['events']:
                u,v=event['target_vertex'],event['support_vertex']
                require(u!=v and active[v],'Invalid/vacuous supporting domain')
                removed=[]
                for i in sorted(active[u]):
                    has_support=False
                    for j in sorted(active[v]):
                        checks+=1
                        if compatible(u,neighborhoods[u][i],v,neighborhoods[v][j]):
                            has_support=True
                            break
                    if not has_support:
                        removed.append(i)
                require(removed and removed==event['removed_domain_ids'],'Unsound or incomplete pair deletion')
                require(event['before_count']==len(active[u]),'Invalid before count')
                active[u].difference_update(removed)
                require(event['after_count']==len(active[u]),'Invalid after count')
                if time.perf_counter()>budget['deadline']:
                    raise AuditCap('TIME_CAP')
            require([sorted(ids) for ids in active]==proof['surviving_domain_ids'],'Incorrect final domain IDs')
            if status=='EMPTY_DOMAIN':
                require(not active[proof['empty_vertex']],'No final empty domain')
            else:
                require(all(active),'Claimed nonempty closure has empty domain')
                for a,b in combinations(range(84),2):
                    for u,v in((a,b),(b,a)):
                        for i in active[u]:
                            require(any(compatible(u,neighborhoods[u][i],v,neighborhoods[v][j]) for j in active[v]),'Pair closure is not arc consistent')
                    if time.perf_counter()>budget['deadline']:
                        raise AuditCap('TIME_CAP')
        except AuditCap as error:
            result.update(status='INCOMPLETE_PAIR_AUDIT_NO_EXCLUSION',cap_reason=str(error))
        else:
            result.update(status='INDEPENDENT_EXACT_PAIR_DOMAIN_AUDIT_PASS',complete_used_domains_verified=True,
                          propagation_status=status,events_verified=len(proof['events']),
                          empty_vertex=proof['empty_vertex'],set_based_compatibility_checks=checks)
        result.update(independently_reenumerated_domains=complete,independent_domain_search_nodes=budget['nodes'])
    result['elapsed_seconds']=time.perf_counter()-started
    with args.out.open('x',encoding='utf-8') as stream:
        stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':
    main()
