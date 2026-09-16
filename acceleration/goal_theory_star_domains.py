"""Enumerate complete local star domains, then propagate edge reciprocity.

Explicit caps affect enumeration only. Any cap hit makes the whole result
INCOMPLETE and disables exclusions from domains or propagation.
"""
import argparse
from collections import deque
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import time

from audit_certificate import full_graph, require

LABELS = [(2*a+s, 2*b+t) for a, b in combinations(range(7), 2) for s in range(2) for t in range(2)]


class EnumerationCap(Exception):
    pass


def enumerate_domain(adjacency, unknown, outer, budget):
    u = outer+15
    vertices = [v for v in range(15, 99) if tuple(sorted((u, v))) in unknown
                and all(len(adjacency[v] & adjacency[w]) < (1 if w in adjacency[v] else 2) for w in adjacency[u])]
    demand = [(1 if s+1 in adjacency[u] else 2)-len(adjacency[u] & adjacency[s+1]) for s in range(14)]
    require(sum(demand) == 16 and min(demand) >= 0, 'Unexpected local quotas')
    capacity = [2-int(w in adjacency[u])-len(adjacency[u] & adjacency[w]) if w != u else 0 for w in range(99)]
    resources = [set(adjacency[v]) | {v} for v in vertices]
    conflicts = [{w for w in vertices if w != v and len(adjacency[v] & adjacency[w]) == (1 if w in adjacency[v] else 2)} for v in vertices]
    masks, local_nodes = [], 0

    def visit(chosen, available, remaining, caps):
        nonlocal local_nodes
        budget['nodes'] += 1
        local_nodes += 1
        if budget['nodes'] > budget['node_cap']:
            raise EnumerationCap('GLOBAL_NODE_CAP')
        if budget['nodes'] % 128 == 0 and time.perf_counter() > budget['deadline']:
            raise EnumerationCap('TIME_CAP')
        if not any(remaining):
            if len(masks) >= budget['domain_cap']:
                raise EnumerationCap('PER_VERTEX_DOMAIN_CAP')
            masks.append(sum(1 << (vertices[i]-15) for i in chosen))
            return
        eligible = [i for i in available if all(remaining[s] > 0 for s in LABELS[vertices[i]-15]) and all(caps[w] > 0 for w in resources[i])]
        by_symbol = {s:[i for i in eligible if s in LABELS[vertices[i]-15]] for s,d in enumerate(remaining) if d}
        if any(len(by_symbol[s]) < remaining[s] for s in by_symbol):
            return
        symbol = min(by_symbol, key=lambda s:(len(by_symbol[s])-remaining[s],len(by_symbol[s]),s))
        for selection in combinations(by_symbol[symbol], remaining[symbol]):
            next_remaining, next_caps = remaining[:], caps[:]
            excluded, legal = set(selection), True
            for i in selection:
                if any(vertices[j] in conflicts[i] for j in selection if i != j):
                    legal = False
                    break
                for s in LABELS[vertices[i]-15]:
                    next_remaining[s] -= 1
                    if next_remaining[s] < 0:
                        legal = False
                for w in resources[i]:
                    next_caps[w] -= 1
                    if next_caps[w] < 0:
                        legal = False
                excluded.update(j for j in eligible if vertices[j] in conflicts[i])
            if legal:
                visit(chosen+list(selection), [i for i in eligible if i not in excluded], next_remaining, next_caps)

    reason = None
    try:
        if time.perf_counter() > budget['deadline']:
            raise EnumerationCap('TIME_CAP')
        visit([], list(range(len(vertices))), demand, capacity)
    except EnumerationCap as error:
        reason = str(error)
    require(len(masks) == len(set(masks)), 'Duplicate enumerated star')
    return dict(outer_vertex=outer, status='COMPLETE' if reason is None else 'INCOMPLETE',
                cap_reason=reason, nodes=local_nodes, domain_masks_hex=[hex(mask) for mask in sorted(masks)])


def reciprocal_closure(domains, unknown):
    active = [set(range(len(row))) for row in domains]
    events = []
    queue = deque(range(84))
    queued = set(queue)
    links = {u:[v for v in range(84) if tuple(sorted((u+15,v+15))) in unknown] for u in range(84)}
    while queue:
        v = queue.popleft()
        queued.discard(v)
        if not active[v]:
            return dict(status='EMPTY_DOMAIN', empty_vertex=v, events=events,
                        surviving_domain_ids=[sorted(ids) for ids in active])
        union, intersection = 0, (1 << 84)-1
        for i in active[v]:
            union |= domains[v][i]
            intersection &= domains[v][i]
        for u in links[v]:
            required = 1 if intersection >> u & 1 else (0 if not (union >> u & 1) else None)
            if required is None:
                continue
            removed = sorted(i for i in active[u] if ((domains[u][i] >> v) & 1) != required)
            if removed:
                before_count = len(active[u])
                active[u].difference_update(removed)
                events.append(dict(target_vertex=u, support_vertex=v, required_edge_value=required,
                                   removed_domain_ids=removed, before_count=before_count, after_count=len(active[u])))
                if not active[u]:
                    return dict(status='EMPTY_DOMAIN', empty_vertex=u, events=events,
                                surviving_domain_ids=[sorted(ids) for ids in active])
                if u not in queued:
                    queue.append(u)
                    queued.add(u)
    return dict(status='ARC_CONSISTENT_NONEMPTY', empty_vertex=None, events=events,
                surviving_domain_ids=[sorted(ids) for ids in active])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--candidate', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--seconds', type=float, default=30)
    parser.add_argument('--node-cap', type=int, default=2000000)
    parser.add_argument('--domain-cap', type=int, default=20000)
    args = parser.parse_args()
    require(not args.out.exists(), 'Preserve existing artifact')
    require(args.seconds > 0 and args.node_cap > 0 and args.domain_cap > 0, 'Positive caps required')
    started = time.perf_counter()
    adjacency, unknown = full_graph(json.loads(args.candidate.read_bytes()))
    budget = dict(nodes=0, node_cap=args.node_cap, domain_cap=args.domain_cap, deadline=started+args.seconds)
    records = []
    for outer in range(84):
        record = enumerate_domain(adjacency, unknown, outer, budget)
        records.append(record)
        print(json.dumps({k:v for k,v in record.items() if k != 'domain_masks_hex'} | {'domain_size':len(record['domain_masks_hex'])}), flush=True)
        if record['status'] != 'COMPLETE':
            break
    complete = len(records) == 84 and all(r['status'] == 'COMPLETE' for r in records)
    result = dict(status='COMPLETE_DOMAINS' if complete else 'INCOMPLETE',
        candidate_sha256=sha256(args.candidate.read_bytes()).hexdigest(),
        inputs_sha256={str(p):sha256(p.read_bytes()).hexdigest() for p in (args.candidate,Path(__file__))},
        caps=dict(seconds=args.seconds, global_nodes=args.node_cap, per_vertex_domains=args.domain_cap),
        total_nodes=budget['nodes'], domains=records, complete_domain_enumeration=complete,
        enumeration_seconds=time.perf_counter()-started,
        scope='One fixed complete overlap assignment; no whole-E0 or Conway exclusion. An incomplete domain list can never justify an empty-domain exclusion.')
    if complete:
        result['propagation'] = reciprocal_closure([[int(m,16) for m in r['domain_masks_hex']] for r in records], unknown)
        result['status'] = 'COMPLETE_DOMAINS_RECIPROCITY_' + result['propagation']['status']
    result['elapsed_seconds'] = time.perf_counter()-started
    with args.out.open('x', encoding='utf-8') as stream:
        stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('domains','propagation')}))


if __name__ == '__main__':
    main()
