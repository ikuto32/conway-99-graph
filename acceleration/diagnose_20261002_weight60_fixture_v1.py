"""Producer-side exact finite fixture diagnosis, not independent approval."""
import argparse, hashlib, itertools, json, os
from datetime import datetime, timezone
from pathlib import Path
from command_deadline import CommandDeadline

MASK=(1<<64)-1
def rng4(seed):
    state=[]
    for _ in range(4):
        seed=(seed+0x9e3779b97f4a7c15)&MASK;z=seed
        z=((z^(z>>30))*0xbf58476d1ce4e5b9)&MASK
        z=((z^(z>>27))*0x94d049bb133111eb)&MASK
        state.append(z^(z>>31))
    draws=[]
    for _ in range(4):
        x=(state[1]*5)&MASK;result=(((x<<7)|(x>>57))&MASK)*9&MASK
        t=(state[1]<<17)&MASK;state[2]^=state[0];state[3]^=state[1];state[1]^=state[2];state[0]^=state[3]
        state[2]^=t;state[3]=((state[3]<<45)|(state[3]>>19))&MASK
        draws.append(result)
    return draws

def triangle_count(n,edges):
    return sum(all(tuple(sorted(e)) in edges for e in [(a,b),(a,c),(b,c)]) for a,b,c in itertools.combinations(range(n),3))

def score(triples):
    n=max(max(t) for t in triples)+1;adj=[set() for _ in range(n)];count=[0]*n
    for t in triples:
        assert len(set(t))==3
        for v in t:count[v]+=1
        for a,b in itertools.combinations(t,2):
            assert b not in adj[a];adj[a].add(b);adj[b].add(a)
    assert set(count)=={2} and all(len(x)==4 for x in adj)
    el=em=0
    for a,b in itertools.combinations(range(n),2):
        c=len(adj[a]&adj[b]);edge=b in adj[a];r=c+(1 if edge else 0)-2
        if edge:el+=r*r
        else:em+=r*r
    return dict(n=n,lambda_energy=el,mu_energy=em,F60=60*el+em),adj

def main():
    p=argparse.ArgumentParser();p.add_argument('--seconds',type=float,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    deadline=CommandDeadline(a.seconds,allocation_reason='Frozen finite fixture enumeration only:5005six-vertex9edge subsets plus explicitcubeinverse andseed0..9999first-proposal selection; no target scientific search')
    a.out.mkdir(parents=True,exist_ok=False)
    rows=[];transitions=[];pairs=list(itertools.combinations(range(6),2))
    for selected in itertools.combinations(pairs,9):
        assert not deadline.status()['stop_required'];edges=frozenset(selected)
        if any(sum(v in e for e in edges)!=3 for v in range(6)):continue
        rowid=len(rows);tri=triangle_count(6,edges);rows.append(dict(id=rowid,edges=selected,triangles=tri))
        for i,j in itertools.combinations(range(6),2):
            if (i,j) in edges:continue
            ni=[v for v in range(6) if tuple(sorted((i,v))) in edges];nj=[v for v in range(6) if tuple(sorted((j,v))) in edges]
            for u in ni:
                for v in nj:
                    if len({i,j,u,v})!=4:continue
                    additions={tuple(sorted((i,v))),tuple(sorted((j,u)))}
                    if additions&edges:continue
                    changed=edges-{tuple(sorted((i,u))),tuple(sorted((j,v)))}|additions
                    after=triangle_count(6,changed)
                    transitions.append(dict(source=rowid,centers=[i,j],other_ends=[u,v],before_triangles=tri,after_triangles=after))
    initial=[[1,2,7],[0,3,4],[1,5,6],[3,5,7],[2,8,9],[4,8,10],[6,9,11],[0,10,11]]
    before,adj=score(initial);ti,tj,pi,pj=0,7,2,0;x,y=initial[ti][pi],initial[tj][pj]
    others_i=[z for k,z in enumerate(initial[ti]) if k!=pi];others_j=[z for k,z in enumerate(initial[tj]) if k!=pj]
    assert not(set(initial[ti])&set(initial[tj])) and all(z not in adj[y] for z in others_i) and all(z not in adj[x] for z in others_j)
    after=[t[:] for t in initial];after[ti][pi]=y;after[tj][pj]=x;after_score,_=score(after)
    assert before['lambda_energy']>0 and after_score['lambda_energy']==0 and after_score['F60']<before['F60']
    eligible=[]
    for seed in range(10000):
        draws=rng4(seed);ci=draws[0]%8;cj=draws[1]%7;cj+=cj>=ci
        if [ci,cj,draws[2]%3,draws[3]%3]==[ti,tj,pi,pj]:eligible.append(dict(seed=seed,draws=draws))
    assert eligible
    report=dict(schema='WEIGHT60_FINITE_FIXTURE_DIAGNOSIS_V1',timestamp=datetime.now(timezone.utc).isoformat(),producer='/root/native_driver',
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),uid=os.geteuid(),deadline=deadline.status(),
        six_vertex_population=dict(subsets_examined=5005,simple_cubic_graphs=len(rows),graphs=rows,legal_disjoint_center_trades=transitions,
          class_changes=sum(r['before_triangles']!=r['after_triangles'] for r in transitions)),
        new_cube12_control=dict(initial_triples=initial,initial_scores=before,inverse_trade=dict(ti=ti,tj=tj,pi=pi,pj=pj),after_triples=after,after_scores=after_score,
          seed_selection_rule='Lowest seed in frozenrange0..9999whosefirstfourRNGdraws propose exactly this known inverse; engineering control selection only',eligible_seeds=len(eligible),selected=eligible[0]),
        independent_approval=False,target_resolution=False,scope='Complete six-vertex cubic/disjoint-dual-trade finite diagnosis and one12point engineering fixture; no99move-space/target claim')
    with (a.out/'summary.json').open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps(dict(status='PRODUCER_FIXTURE_DIAGNOSIS_PENDING_INDEPENDENT_CHECK',cubic_graphs=len(rows),trades=len(transitions),class_changes=report['six_vertex_population']['class_changes'],new_control=report['new_cube12_control'])))

if __name__=='__main__':main()
