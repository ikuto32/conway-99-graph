"""Extract a small reciprocal-domain contradiction from an audited trace."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

from audit_certificate import require


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--domains',type=Path,required=True)
    parser.add_argument('--audit',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args = parser.parse_args()
    require(not args.out.exists(),'Preserve existing core')
    data,audit = (json.loads(p.read_bytes()) for p in (args.domains,args.audit))
    require(audit['status']=='INDEPENDENT_COMPLETE_STAR_DOMAINS_AND_RECIPROCITY_AUDIT_PASS' and audit['complete_domain_enumeration_verified'],'Complete-domain audit required')
    require(sha256(args.domains.read_bytes()).hexdigest() in audit['inputs_sha256'].values(),'Domain audit binding')
    for name,digest in audit['inputs_sha256'].items():
        require(sha256(Path(name).read_bytes()).hexdigest()==digest,'Changed audit input')
    require(data['propagation']['status']=='EMPTY_DOMAIN','No contradiction')
    domains = [[int(m,16) for m in r['domain_masks_hex']] for r in data['domains']]
    events = data['propagation']['events']
    owner = {(e['target_vertex'],i):n for n,e in enumerate(events) for i in e['removed_domain_ids']}
    empty = data['propagation']['empty_vertex']
    pending = [owner[empty,i] for i in range(len(domains[empty]))]
    needed = set()
    while pending:
        n = pending.pop()
        if n in needed:
            continue
        needed.add(n)
        e = events[n]
        u,v,value = e['target_vertex'],e['support_vertex'],e['required_edge_value']
        for i,mask in enumerate(domains[v]):
            if ((mask>>u)&1)!=value:
                require(owner[v,i]<n,'Noncausal deletion support')
                pending.append(owner[v,i])
    vertices = sorted({v for n in needed for v in (events[n]['target_vertex'],events[n]['support_vertex'])})
    active = {u:set(range(len(domains[u]))) for u in vertices}
    core_events = []
    for n in sorted(needed):
        e = events[n]
        u,v,value = e['target_vertex'],e['support_vertex'],e['required_edge_value']
        require(active[v] and all(((domains[v][i]>>u)&1)==value for i in active[v]),'Core support lost')
        removed = sorted(i for i in active[u] if ((domains[u][i]>>v)&1)!=value)
        if not removed:
            continue
        before = len(active[u])
        active[u].difference_update(removed)
        core_events.append(dict(target_vertex=u,support_vertex=v,required_edge_value=value,
                                removed_domain_ids=removed,before_count=before,after_count=len(active[u])))
        if not active[u]:
            empty = u
            break
    require(not active[empty],'Core no longer contradicts')
    result = dict(status='COMPLETE_STAR_DOMAIN_RECIPROCITY_CORE',candidate_sha256=data['candidate_sha256'],
                  domains=[data['domains'][u] for u in vertices],events=core_events,empty_vertex=empty,
                  source_event_indices=sorted(needed),
                  inputs_sha256={str(p):sha256(p.read_bytes()).hexdigest() for p in(args.domains,args.audit,Path(__file__))},
                  scope='A compact contradiction using only listed complete local-star domains and edge reciprocity. No claim that every overlap assignment contains this obstruction.')
    with args.out.open('x',encoding='utf-8') as stream:
        stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(vertices=vertices,domain_sizes=[len(domains[u]) for u in vertices],events=len(core_events),empty_vertex=empty)))


if __name__=='__main__':
    main()
