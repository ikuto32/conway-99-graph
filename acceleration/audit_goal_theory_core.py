"""Check small reciprocal-star cores by independent complete domain enumeration."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import time

from audit_certificate import full_graph,require
from audit_goal_theory_domains import enumerate_direct,AuditCap


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate',type=Path,required=True)
    parser.add_argument('--core',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    require(not args.out.exists(),'Preserve previous core audit')
    started=time.perf_counter()
    data=json.loads(args.core.read_bytes())
    require(data['candidate_sha256']==sha256(args.candidate.read_bytes()).hexdigest(),'Wrong candidate')
    adjacency,unknown=full_graph(json.loads(args.candidate.read_bytes()))
    budget=dict(nodes=0,node_cap=3000000,domain_cap=20000,deadline=started+30)
    vertices=[r['outer_vertex'] for r in data['domains']]
    require(vertices==sorted(set(vertices)) and all(type(u) is int and 0<=u<84 for u in vertices),'Invalid core vertices')
    domains={}
    for row in data['domains']:
        require(row['status']=='COMPLETE' and row['cap_reason'] is None,'Incomplete listed domain')
        actual,nodes=enumerate_direct(adjacency,unknown,row['outer_vertex'],budget)
        require(actual==[int(mask,16) for mask in row['domain_masks_hex']],'Incorrect or incomplete domain')
        domains[row['outer_vertex']]=actual
    active={u:set(range(len(domains[u]))) for u in vertices}
    for event in data['events']:
        require(all(active.values()),'Events after empty domain')
        u,v,value=event['target_vertex'],event['support_vertex'],event['required_edge_value']
        require(u in active and v in active and type(value) is int and value in(0,1),'Event domain')
        require(tuple(sorted((u+15,v+15))) in unknown,'Non-variable edge')
        require(all(((domains[v][i]>>u)&1)==value for i in active[v]),'Unsupported forced edge value')
        removed=sorted(i for i in active[u] if ((domains[u][i]>>v)&1)!=value)
        require(removed and removed==event['removed_domain_ids'] and event['before_count']==len(active[u]),'Invalid deletion')
        active[u].difference_update(removed)
        require(event['after_count']==len(active[u]),'Invalid deletion count')
    require(data['empty_vertex'] in active and not active[data['empty_vertex']],'No empty domain')
    result=dict(status='INDEPENDENT_COMPACT_RECIPROCITY_CORE_AUDIT_PASS',
                inputs_sha256={str(p):sha256(p.read_bytes()).hexdigest() for p in(args.candidate,args.core,Path(__file__),Path(__file__).with_name('audit_goal_theory_domains.py'),Path(__file__).with_name('audit_goal_theory_stars.py'),Path(__file__).with_name('audit_certificate.py'))},
                complete_domains_independently_reenumerated=vertices,domain_sizes={str(u):len(domains[u]) for u in vertices},
                events_verified=len(data['events']),empty_vertex=data['empty_vertex'],independent_nodes=budget['nodes'],
                producer_or_solver_imported=False,elapsed_seconds=time.perf_counter()-started,
                scope='This fixed overlap assignment has no reciprocal choice of the listed locally valid full stars. Not a general E0 or Conway exclusion.')
    with args.out.open('x',encoding='utf-8') as stream:
        stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':
    main()
