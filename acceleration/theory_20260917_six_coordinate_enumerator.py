"""Retained-partial adaptation of the frozen partial-K star enumerator.

Same disclosed exact pruning algorithm; independent completeness review needed.
"""
import time
from theory_20260917_partial_matching import add, valid, members, Cap


def enumerate_star_retained(rows,labels,unknown,outer,budget,state,restricted=None):
    center=outer+15;count_needed=14-rows[center].bit_count()
    candidates=sorted(v if u==outer else u for u,v in unknown if outer in(u,v))
    if restricted is not None:candidates=[v for v in candidates if v in restricted]
    legal=[]
    for v in candidates:
        trial=rows[:];add(trial,center,v+15)
        if valid(trial):legal.append(v)
    candidates=legal;n=len(candidates);state['candidates']=candidates
    demands=[2-int(bool(rows[center]>>(s+1)&1))-(rows[center]&rows[s+1]).bit_count() for s in range(14)]
    assert sum(demands)==2*count_needed and min(demands)>=0
    caps=[2-int(bool(rows[center]>>w&1))-(rows[center]&rows[w]).bit_count() if w!=center else 99 for w in range(99)]
    by_label=[sum(1<<i for i,v in enumerate(candidates) if s in labels[v]) for s in range(14)]
    resources=[list(members(rows[v+15]|(1<<(v+15)))) for v in candidates]
    by_resource=[sum(1<<i for i,r in enumerate(resources) if w in r) for w in range(99)]
    conflicts=[sum(1<<j for j,w in enumerate(candidates) if i!=j and
                   (rows[v+15]&rows[w+15]).bit_count()>=2-int(bool(rows[v+15]>>(w+15)&1)))
               for i,v in enumerate(candidates)]
    masks=state['masks'];local_nodes=0
    def visit(available,chosen,remaining,capacity):
        nonlocal local_nodes
        local_nodes+=1;budget['nodes']+=1;state['nodes']=local_nodes
        if budget['nodes']>budget['node_cap']:raise Cap('GLOBAL_NODE_CAP')
        if local_nodes%128==0 and time.monotonic()>=budget['deadline']:raise Cap('TIME_CAP')
        if not any(remaining):
            assert chosen.bit_count()==count_needed
            if len(masks)>=budget['domain_cap']:
                state['cap_trigger_mask']=chosen;raise Cap('PER_VERTEX_DOMAIN_CAP')
            if budget['complete_choices']+len(masks)>=budget['total_cap']:
                state['cap_trigger_mask']=chosen;raise Cap('TOTAL_DOMAIN_CAP')
            masks.append(chosen);return
        choices=[]
        for s,need in enumerate(remaining):
            number=(available&by_label[s]).bit_count()
            if number<need:return
            if need:choices.append((number-need,number,s))
        _,_,symbol=min(choices);options=available&by_label[symbol]
        first=options&-options;i=first.bit_length()-1;rest=available^first;v=candidates[i]
        if all(remaining[s]>0 for s in labels[v]) and all(capacity[w]>0 for w in resources[i]):
            next_remaining=remaining[:];next_capacity=capacity[:];next_available=rest&~conflicts[i]
            for s in labels[v]:
                next_remaining[s]-=1
                if next_remaining[s]==0:next_available&=~by_label[s]
            for w in resources[i]:
                next_capacity[w]-=1
                if next_capacity[w]==0:next_available&=~by_resource[w]
            visit(next_available,chosen|(1<<v),next_remaining,next_capacity)
        visit(rest,chosen,remaining,capacity)
    available=(1<<n)-1
    for s in range(14):
        if demands[s]==0:available&=~by_label[s]
    for w in range(99):
        if caps[w]==0:available&=~by_resource[w]
    visit(available,0,demands,caps)
    assert len(masks)==len(set(masks))
    return sorted(masks),local_nodes,candidates
