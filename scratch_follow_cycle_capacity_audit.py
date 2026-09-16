"""Independent positive-witness audit, with no producer/max-flow imports."""
from collections import Counter
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent


def main():
    path=HERE/'scratch_follow_cycle_capacity.json'
    saved=json.loads(path.read_bytes())
    labels=sorted((a,b) for a in range(14) for b in range(a+1,14) if a//2!=b//2)
    labels.sort(key=lambda pair:(pair[0]//2,pair[1]//2,*pair))
    supports=[set(label//2 for label in pair) for pair in labels]
    all_possible={pair for pair in combinations(range(84),2) if not supports[pair[0]]&supports[pair[1]]}
    audited=[]
    for record in saved['records']:
        source=HERE/record['input']
        assert sha256(source.read_bytes()).hexdigest()==record['input_sha256']
        known=set(map(tuple,json.loads(source.read_bytes())['overlap_edges_outer_zero_based']))
        outer=[{v if u==x else u for u,v in known if x in (u,v)} for x in range(84)]
        graph=[set() for _ in range(99)]
        def add(u,v): graph[u].add(v);graph[v].add(u)
        for u in range(1,15): add(0,u)
        for u in range(1,15,2): add(u,u+1)
        for u,pair in enumerate(labels):
            for s in pair: add(u+15,s+1)
        for u,v in known: add(u+15,v+15)
        forbidden={tuple(row['edge']):row for row in record['forbidden_single_edge_additions']}
        assert len(forbidden)==len(record['forbidden_single_edge_additions'])
        assert set(forbidden)<=all_possible
        def count_after(u,v,x,y):
            a,b=u+15,v+15
            first=graph[x]|({b} if x==a else {a} if x==b else set())
            second=graph[y]|({b} if y==a else {a} if y==b else set())
            return len(first&second),1 if y in first else 2
        for (u,v),row in forbidden.items():
            x,y=row['violating_graph_pair']
            count,cap=count_after(u,v,x,y)
            assert (count,cap)==(row['common_after'],row['cap_after']) and count>cap
        allowed=all_possible-set(forbidden)
        assert len(allowed)==record['admissible_disjoint_edges']
        for u,v in allowed:
            for x in (u+15,v+15):
                for y in range(99):
                    if y!=x:
                        count,cap=count_after(u,v,x,y)
                        assert count<=cap
        for g,components in enumerate(record['cycles']):
            assert {u for component in components for u in component}=={u for u in range(84) if g in supports[u]}
            assert sum(map(len,components))==24
            for component in components:
                vertex_set=set(component)
                assert len(component)%4==0 and all(len(outer[u]&vertex_set)==2 for u in vertex_set)
                reached={min(vertex_set)}
                while True:
                    enlarged=reached|{v for u in reached for v in outer[u]&vertex_set}
                    if enlarged==reached: break
                    reached=enlarged
                assert reached==vertex_set
        for projection in record['projections']:
            kind=projection['kind'];symbols=projection['classes']
            if kind in ('group','label'):
                a,b=symbols
                ga,gb=(a,b) if kind=='group' else (a//2,b//2)
                classa={u for u in range(84) if (a in supports[u] if kind=='group' else a in labels[u])}
                classb={u for u in range(84) if (b in supports[u] if kind=='group' else b in labels[u])}
                left=sorted(u for u in classa if gb not in supports[u])
                right=sorted(v for v in classb if ga not in supports[v])
                quota=4 if kind=='group' else 2
                ld={u:quota-len(outer[u]&classb) for u in left}
                rd={v:quota-len(outer[v]&classa) for v in right}
            else:
                assert kind in ('group_star','label_star')
                symbol=symbols[0];g=symbol if kind=='group_star' else symbol//2
                left=sorted(u for u in range(84) if (symbol in supports[u] if kind=='group_star' else symbol in labels[u]))
                right=sorted(v for v in range(84) if g not in supports[v])
                ld={u:8 for u in left}
                rd={v:(4 if kind=='group_star' else 2)-len(outer[v]&set(left)) for v in right}
            assert projection['left']==left and projection['right']==right
            assert projection['left_demands']==[ld[u] for u in left]
            assert projection['right_demands']==[rd[v] for v in right]
            selected=list(map(tuple,projection['selected_edges']))
            assert len(selected)==len(set(selected))
            assert all(u in left and v in right and tuple(sorted((u,v))) in allowed for u,v in selected)
            actual_left=Counter(u for u,v in selected);actual_right=Counter(v for u,v in selected)
            assert all(actual_left[u]==ld[u] for u in left) and all(actual_right[v]==rd[v] for v in right)
            assert projection['status']=='PASS' and projection['max_flow']==len(selected)==sum(ld.values())==sum(rd.values())
        weighted_count=0
        for item in record['weighted_cycle_checks']:
            g,mask=item['group'],item['cycle_mask']
            subset={u for i,component in enumerate(record['cycles'][g]) if mask>>i&1 for u in component}
            assert item['vertices']==sorted(subset)
            group_vertices={u for u in range(84) if g in supports[u]}
            bins=Counter()
            for v in set(range(84))-group_vertices:
                weight=len(outer[v]&subset)
                capacity=min(4-len(outer[v]&group_vertices),sum(tuple(sorted((u,v))) in allowed for u in subset))
                bins[weight]+=capacity
            demand=8*len(subset);remaining=demand;minimum=0
            for weight in sorted(bins):
                take=min(remaining,bins[weight]);remaining-=take;minimum+=weight*take
            rhs=sum((1 if v in outer[u] else 2)-len(graph[u+15]&graph[v+15]) for u,v in combinations(sorted(subset),2))
            assert item['demand']==demand and item['capacity']==sum(bins.values())
            assert item['minimum_relaxed_cost']==minimum and item['unfilled_demand']==remaining==0
            assert item['sum_pair_cap_rhs']==rhs and minimum<=rhs and item['status']=='PASS'
            weighted_count+=1
        # Feasible integral degree flows already imply every Hall subset
        # inequality, including the recorded cycle-union subfamily.
        assert not record['cycle_obstructions'] and record['minimum_cycle_union_slack']>=0
        audited.append({'input':source.name,'integer_flow_witnesses':len(record['projections']),
                        'cycle_union_Hall_inequalities_implied':record['cycle_union_inequalities_checked'],
                        'weighted_cycle_capacity_tests':weighted_count,'admissible_edges':len(allowed)})
    output={'status':'INDEPENDENT_CYCLE_CAPACITY_CONTROLS_AUDIT_PASS',
            'input_sha256':sha256(path.read_bytes()).hexdigest(),'records':audited,
            'producer_or_flow_algorithm_imported':False,'scope':'Positive controls for individual necessary projections only; all five fixed overlap assignments remain excluded by stronger independently proved capacity inequalities. No new exclusion or graph.'}
    (HERE/'scratch_follow_cycle_capacity_audit.json').write_text(json.dumps(output,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(output))


if __name__=='__main__': main()
