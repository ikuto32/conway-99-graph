"""Independently exhaust star domains and replay reciprocal-edge deletions.

Uses actual graph mutation and ordered neighbor subsets, never importing the
domain producer or its propagation code. Caps return an INCOMPLETE audit and
do not validate a contradiction.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import time

from audit_certificate import full_graph, require
from audit_goal_theory_stars import add_checked


class AuditCap(Exception):
    pass


def enumerate_direct(adjacency, unknown, outer, budget):
    u = outer+15
    rows = [sum(1 << v for v in neighbors) for neighbors in adjacency]
    labels = {v:sorted(s-1 for s in adjacency[v] if 1 <= s <= 14) for v in range(15,99)}
    target = [(1 if s+1 in adjacency[u] else 2)-len(adjacency[u]&adjacency[s+1]) for s in range(14)]
    candidates = []
    for v in range(15,99):
        if tuple(sorted((u,v))) in unknown:
            legal, old_u, old_v = add_checked(rows,u,v)
            if legal:
                candidates.append(v)
                rows[u], rows[v] = old_u, old_v
    suffix = [[0]*14 for _ in range(len(candidates)+1)]
    for i in range(len(candidates)-1,-1,-1):
        suffix[i] = suffix[i+1][:]
        for s in labels[candidates[i]]:
            suffix[i][s] += 1
    masks = []
    local_nodes = 0

    def visit(start, chosen_mask, count, demand):
        nonlocal local_nodes
        budget['nodes'] += 1
        local_nodes += 1
        if budget['nodes'] > budget['node_cap']:
            raise AuditCap('GLOBAL_NODE_CAP')
        if budget['nodes'] % 128 == 0 and time.perf_counter() > budget['deadline']:
            raise AuditCap('TIME_CAP')
        if count == 8:
            if not any(demand):
                if len(masks) >= budget['domain_cap']:
                    raise AuditCap('PER_VERTEX_DOMAIN_CAP')
                masks.append(chosen_mask)
            return
        if len(candidates)-start < 8-count or any(d > suffix[start][s] for s,d in enumerate(demand)):
            return
        for i in range(start,len(candidates)):
            v = candidates[i]
            if any(demand[s] <= 0 for s in labels[v]):
                continue
            legal, old_u, old_v = add_checked(rows,u,v)
            if legal:
                remaining = demand[:]
                for s in labels[v]:
                    remaining[s] -= 1
                visit(i+1, chosen_mask | (1 << (v-15)), count+1, remaining)
                rows[u], rows[v] = old_u, old_v

    if time.perf_counter() > budget['deadline']:
        raise AuditCap('TIME_CAP')
    visit(0,0,0,target)
    require(len(masks) == len(set(masks)), 'Independent duplicate star')
    return sorted(masks), local_nodes


def replay(domains, unknown, propagation):
    active = [set(range(len(row))) for row in domains]
    deleted = 0
    for event in propagation['events']:
        require(all(active), 'Propagation continued after empty domain')
        u, v, value = event['target_vertex'], event['support_vertex'], event['required_edge_value']
        require(type(u) is int and type(v) is int and type(value) is int and value in (0,1), 'Invalid event fields')
        require(tuple(sorted((u+15,v+15))) in unknown, 'Propagation outside disjoint domain')
        require(all(((domains[v][i] >> u)&1) == value for i in active[v]), 'Support does not force this edge value')
        expected = sorted(i for i in active[u] if ((domains[u][i] >> v)&1) != value)
        require(expected and expected == event['removed_domain_ids'], 'Incorrect domain deletion')
        require(event['before_count'] == len(active[u]), 'Incorrect before count')
        active[u].difference_update(expected)
        require(event['after_count'] == len(active[u]), 'Incorrect after count')
        deleted += len(expected)
    require([sorted(row) for row in active] == propagation['surviving_domain_ids'], 'Final active domains differ')
    empty = [u for u in range(84) if not active[u]]
    if propagation['status'] == 'EMPTY_DOMAIN':
        require(propagation['empty_vertex'] in empty, 'No claimed empty domain')
    else:
        require(propagation['status'] == 'ARC_CONSISTENT_NONEMPTY' and not empty and propagation['empty_vertex'] is None, 'Invalid propagation status')
        for a,b in unknown:
            u,v = a-15,b-15
            allowed_u = {int(bool(domains[u][i] & (1 << v))) for i in active[u]}
            allowed_v = {int(bool(domains[v][i] & (1 << u))) for i in active[v]}
            require(allowed_u == allowed_v, 'Reciprocal arc is not consistent')
    return dict(events_verified=len(propagation['events']), domain_values_removed=deleted,
                empty_vertices=empty, final_domain_sizes=[len(row) for row in active])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate',type=Path,required=True)
    parser.add_argument('--domains',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--seconds',type=float,default=30)
    parser.add_argument('--node-cap',type=int,default=3000000)
    parser.add_argument('--domain-cap',type=int,default=20000)
    args = parser.parse_args()
    require(not args.out.exists(), 'Preserve previous audit')
    started = time.perf_counter()
    saved = json.loads(args.domains.read_bytes())
    require(saved['candidate_sha256'] == sha256(args.candidate.read_bytes()).hexdigest(), 'Candidate mismatch')
    for name,digest in saved['inputs_sha256'].items():
        require(sha256(Path(name).read_bytes()).hexdigest() == digest, 'Input or producer source changed')
    result = dict(inputs_sha256={str(p):sha256(p.read_bytes()).hexdigest() for p in
        (args.candidate,args.domains,Path(__file__),Path(__file__).with_name('audit_goal_theory_stars.py'),Path(__file__).with_name('audit_certificate.py'))},
        producer_or_solver_imported=False, complete_domain_enumeration_verified=False,
        scope='One fixed complete overlap assignment; an incomplete audit proves no exclusion. Complete domains plus independently valid reciprocal-edge deletions can exclude only this fixed assignment.')
    if not saved['complete_domain_enumeration']:
        require(saved['status'] == 'INCOMPLETE' and 'propagation' not in saved, 'Incomplete domains were used for propagation')
        result['status'] = 'INCOMPLETE_PRODUCER_NO_EXCLUSION'
    else:
        adjacency,unknown = full_graph(json.loads(args.candidate.read_bytes()))
        require([r['outer_vertex'] for r in saved['domains']] == list(range(84)), 'Incomplete vertex domain list')
        budget = dict(nodes=0,node_cap=args.node_cap,domain_cap=args.domain_cap,deadline=started+args.seconds)
        independently_completed = []
        domains = []
        try:
            for record in saved['domains']:
                u = record['outer_vertex']
                require(record['status'] == 'COMPLETE' and record['cap_reason'] is None, 'Producer vertex incomplete')
                actual,nodes = enumerate_direct(adjacency,unknown,u,budget)
                claimed = [int(mask,16) for mask in record['domain_masks_hex']]
                require(actual == claimed, f'Full star domain mismatch at {u}')
                domains.append(actual)
                independently_completed.append(dict(outer_vertex=u,domain_size=len(actual),ordered_subset_nodes=nodes))
        except AuditCap as error:
            result.update(status='INCOMPLETE_INDEPENDENT_AUDIT_NO_EXCLUSION',cap_reason=str(error))
        else:
            result.update(status='INDEPENDENT_COMPLETE_STAR_DOMAINS_AND_RECIPROCITY_AUDIT_PASS',
                          complete_domain_enumeration_verified=True, propagation_status=saved['propagation']['status'],
                          propagation=replay(domains,unknown,saved['propagation']))
        result.update(independent_domain_records=independently_completed,independent_search_nodes=budget['nodes'])
    result['elapsed_seconds'] = time.perf_counter()-started
    with args.out.open('x',encoding='utf-8') as stream:
        stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('independent_domain_records','propagation')}))


if __name__ == '__main__':
    main()
