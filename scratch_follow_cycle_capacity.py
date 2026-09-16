"""Exact group/label-pair flow and group-star cycle capacity controls.

All arithmetic and max-flow operations are stdlib/integer. This checks
necessary projections of a prescribed complete E0=0 overlap assignment;
passing projections are not simultaneous edge assignments or a graph.
"""
from collections import Counter, deque
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import time

HERE=Path(__file__).resolve().parent


def max_flow(left,right,ld,rd,allowed):
    vertices=[None]+left+right+[None]
    source,sink=0,len(vertices)-1
    li={u:i+1 for i,u in enumerate(left)}
    ri={v:len(left)+1+i for i,v in enumerate(right)}
    adj=[[] for _ in vertices]
    def add(a,b,capacity):
        adj[a].append([b,capacity,len(adj[b])])
        adj[b].append([a,0,len(adj[a])-1])
        return len(adj[a])-1
    for u in left: add(source,li[u],ld[u])
    refs={}
    for u in left:
        for v in right:
            if tuple(sorted((u,v))) in allowed: refs[u,v]=(li[u],add(li[u],ri[v],1))
    for v in right: add(ri[v],sink,rd[v])
    value=0
    while True:
        parent={source:None}
        queue=deque([source])
        while queue and sink not in parent:
            u=queue.popleft()
            for index,(v,capacity,_) in enumerate(adj[u]):
                if capacity and v not in parent:
                    parent[v]=(u,index);queue.append(v)
        if sink not in parent: break
        capacity=10**9
        cursor=sink
        while cursor!=source:
            u,index=parent[cursor];capacity=min(capacity,adj[u][index][1]);cursor=u
        cursor=sink
        while cursor!=source:
            u,index=parent[cursor]
            v,_,reverse=adj[u][index]
            adj[u][index][1]-=capacity;adj[v][reverse][1]+=capacity;cursor=u
        value+=capacity
    selected=[[u,v] for (u,v),(a,index) in refs.items() if adj[a][index][1]==0]
    return value,selected,[u for u in left if li[u] in parent],[v for v in right if ri[v] in parent]


def inspect(path):
    raw=path.read_bytes()
    data=json.loads(raw)
    labels=[(2*a+s,2*b+t) for a,b in combinations(range(7),2) for s in range(2) for t in range(2)]
    supports=[{a//2,b//2} for a,b in labels]
    known=set(map(tuple,data['overlap_edges_outer_zero_based']))
    assert len(known)==168
    outer=[set() for _ in range(84)]
    graph=[set() for _ in range(99)]
    def put(u,v): graph[u].add(v);graph[v].add(u)
    for v in range(1,15): put(0,v)
    for v in range(1,15,2): put(v,v+1)
    for u,pair in enumerate(labels):
        for symbol in pair: put(u+15,symbol+1)
    for u,v in known:
        assert len(supports[u]&supports[v])==1
        outer[u].add(v);outer[v].add(u);put(u+15,v+15)
    assert all(len(row)==4 for row in outer)
    common={(u,v):len(graph[u]&graph[v]) for u,v in combinations(range(99),2)}
    assert all(count<=(1 if v in graph[u] else 2) for (u,v),count in common.items())
    possible={pair for pair in combinations(range(84),2) if not supports[pair[0]]&supports[pair[1]]}
    allowed=set()
    forbidden=[]
    for u,v in sorted(possible):
        a,b=u+15,v+15
        affected={(a,b)}
        affected|={tuple(sorted((a,w))) for w in graph[b]}
        affected|={tuple(sorted((b,w))) for w in graph[a]}
        obstruction=None
        for x,y in sorted(affected):
            count=common[x,y]
            if (x,y)!=(a,b):
                count+=int(x==a and y in graph[b] or y==a and x in graph[b])
                count+=int(x==b and y in graph[a] or y==b and x in graph[a])
            cap=1 if (x,y)==(a,b) or y in graph[x] else 2
            if count>cap:
                obstruction={'edge':[u,v],'violating_graph_pair':[x,y],'common_after':count,'cap_after':cap}
                break
        if obstruction: forbidden.append(obstruction)
        else: allowed.add((u,v))
    cycles=[]
    for g in range(7):
        remaining={u for u in range(84) if g in supports[u]}
        components=[]
        while remaining:
            root=min(remaining)
            reached={root};queue=[root]
            while queue:
                u=queue.pop()
                row={v for v in outer[u] if g in supports[v]}
                assert len(row)==2
                for v in row-reached: reached.add(v);queue.append(v)
            assert len(reached)%4==0
            components.append(sorted(reached));remaining-=reached
        cycles.append(components)
    projections=[]
    cycle_inequalities=0
    cycle_minimum_slack=None
    cycle_obstructions=[]
    for kind in ('group','label'):
        count=7 if kind=='group' else 14
        def members(symbol):
            return {u for u in range(84) if (symbol in supports[u] if kind=='group' else symbol in labels[u])}
        for a,b in combinations(range(count),2):
            ga,gb=(a,b) if kind=='group' else (a//2,b//2)
            if ga==gb: continue
            classa,classb=members(a),members(b)
            left=sorted(u for u in classa if gb not in supports[u])
            right=sorted(v for v in classb if ga not in supports[v])
            target=4 if kind=='group' else 2
            ld={u:target-len(outer[u]&classb) for u in left}
            rd={v:target-len(outer[v]&classa) for v in right}
            assert all(value>=0 for value in list(ld.values())+list(rd.values()))
            total_left,total_right=sum(ld.values()),sum(rd.values())
            flow,selection,cutleft,cutright=max_flow(left,right,ld,rd,allowed)
            row={'kind':kind,'classes':[a,b],'left':left,'right':right,
                 'left_demands':[ld[u] for u in left],'right_demands':[rd[v] for v in right],
                 'total_left':total_left,'total_right':total_right,'max_flow':flow,
                 'selected_edges':selection,'status':'PASS' if flow==total_left==total_right else 'FAIL'}
            if row['status']=='FAIL':
                row['cut_left']=cutleft;row['cut_right']=cutright
                row['hall_lhs']=sum(ld[u] for u in cutleft)
                row['hall_rhs']=sum(rd[v] for v in cutright)+sum(tuple(sorted((u,v))) in allowed for u in cutleft for v in right if v not in cutright)
            projections.append(row)
            if kind=='group':
                for source_group,other_group,source_side,other_side,demands,capacities in (
                        (ga,gb,left,right,ld,rd),(gb,ga,right,left,rd,ld)):
                    components=cycles[source_group]
                    for mask in range(1,1<<len(components)):
                        subset={u for i,component in enumerate(components) if mask>>i&1 for u in component}&set(source_side)
                        demand=sum(demands[u] for u in subset)
                        capacity=sum(min(capacities[v],sum(tuple(sorted((u,v))) in allowed for u in subset)) for v in other_side)
                        slack=capacity-demand
                        cycle_inequalities+=1
                        cycle_minimum_slack=slack if cycle_minimum_slack is None else min(cycle_minimum_slack,slack)
                        if slack<0:
                            cycle_obstructions.append({'source_group':source_group,'other_group':other_group,'cycle_mask':mask,
                                                       'left_vertices':sorted(subset),'demand':demand,'capacity':capacity})
    for kind in ('group_star','label_star'):
        count=7 if kind=='group_star' else 14
        for symbol in range(count):
            g=symbol if kind=='group_star' else symbol//2
            left=sorted(u for u in range(84) if (g in supports[u] if kind=='group_star' else symbol in labels[u]))
            right=sorted(v for v in range(84) if g not in supports[v])
            ld={u:8 for u in left}
            rd={v:(4 if kind=='group_star' else 2)-len(outer[v]&set(left)) for v in right}
            flow,selection,cutleft,cutright=max_flow(left,right,ld,rd,allowed)
            row={'kind':kind,'classes':[symbol],'left':left,'right':right,
                 'left_demands':[ld[u] for u in left],'right_demands':[rd[v] for v in right],
                 'total_left':sum(ld.values()),'total_right':sum(rd.values()),'max_flow':flow,
                 'selected_edges':selection,'status':'PASS' if flow==sum(ld.values())==sum(rd.values()) else 'FAIL'}
            if row['status']=='FAIL':
                row['cut_left']=cutleft;row['cut_right']=cutright
                row['hall_lhs']=sum(ld[u] for u in cutleft)
                row['hall_rhs']=sum(rd[v] for v in cutright)+sum(tuple(sorted((u,v))) in allowed for u in cutleft for v in right if v not in cutright)
            projections.append(row)
    weighted_cycle_checks=[]
    for g,components in enumerate(cycles):
        group_vertices={u for u in range(84) if g in supports[u]}
        outside=set(range(84))-group_vertices
        for mask in range(1,1<<len(components)):
            subset={u for i,component in enumerate(components) if mask>>i&1 for u in component}
            rhs=sum(2-len(set(labels[u])&set(labels[v]))-int((min(u,v),max(u,v)) in known)-len(outer[u]&outer[v])
                    for u,v in combinations(sorted(subset),2))
            capacities={v:min(4-len(outer[v]&group_vertices),sum(tuple(sorted((u,v))) in allowed for u in subset)) for v in outside}
            weights={v:len(outer[v]&subset) for v in outside}
            demand=8*len(subset)
            remaining=demand
            cost=0
            allocation=[]
            for v in sorted(outside,key=lambda v:(weights[v],v)):
                amount=min(remaining,capacities[v]);remaining-=amount;cost+=weights[v]*amount
                if amount: allocation.append([v,amount])
            weighted_cycle_checks.append({'group':g,'cycle_mask':mask,'vertices':sorted(subset),'demand':demand,
                                           'capacity':sum(capacities.values()),'unfilled_demand':remaining,
                                           'minimum_relaxed_cost':cost,'sum_pair_cap_rhs':rhs,
                                           'status':'PASS' if remaining==0 and cost<=rhs else 'FAIL',
                                           'greedy_allocation':allocation})
    return {'input':path.name,'input_sha256':sha256(raw).hexdigest(),
            'admissible_disjoint_edges':len(allowed),'forbidden_single_edge_additions':forbidden,
            'cycles':cycles,'projection_status_histogram':dict(Counter(p['status'] for p in projections)),
            'projection_kind_counts':dict(Counter(p['kind'] for p in projections)),
            'projections':projections,'cycle_union_inequalities_checked':cycle_inequalities,
            'minimum_cycle_union_slack':cycle_minimum_slack,'cycle_obstructions':cycle_obstructions,
            'weighted_cycle_checks':weighted_cycle_checks,
            'weighted_cycle_status_histogram':dict(Counter(row['status'] for row in weighted_cycle_checks))}


def main():
    started=time.monotonic()
    paths=[HERE/'scratch_resume_overlap_lift.json']+[HERE/f'scratch_next_overlap_alternatives_r{i}.json' for i in range(4)]
    records=[inspect(path) for path in paths]
    result={'status':'EXACT_CYCLE_AND_CLASS_PAIR_CAPACITY_PROJECTIONS_COMPLETE',
            'records':records,'elapsed_seconds':time.monotonic()-started,
            'scope':'Necessary bipartite degree-flow projections for complete E0=0 overlap K, using root-label quotas and single-edge pair-cap exclusions; independent projection solutions are not simultaneous X or a graph.'}
    (HERE/'scratch_follow_cycle_capacity.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':result['status'],'elapsed_seconds':result['elapsed_seconds'],
                      'records':[{k:v for k,v in r.items() if k not in ('cycles','projections','forbidden_single_edge_additions','weighted_cycle_checks')}
                                 for r in records]}))


if __name__=='__main__': main()
