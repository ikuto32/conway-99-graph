"""Independent set-neighborhood and odd-component check of positive clauses."""
from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import platform
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
DIR=ROOT/'acceleration/results/20260917_matching_cut'

def require(ok,msg):
    if not ok: raise ValueError(msg)

def digest(p): return sha256(Path(p).read_bytes()).hexdigest()
def key(p): return Path(p).resolve().relative_to(ROOT).as_posix()
def edges(value):
    require(all(len(e)==2 and all(type(v)is int and 0<=v<99 for v in e) and e[0]!=e[1] for e in value),'edge format')
    e={tuple(sorted(x)) for x in value}
    require(len(e)==len(value),'repeated edge')
    return e

def scaffold():
    e={(0,v) for v in range(1,15)}|{(v,v+1) for v in range(1,15,2)}
    labels=[(2*a+s,2*b+t) for a,b in combinations(range(7),2) for s in range(2) for t in range(2)]
    e|={(s+1,u) for u,pair in enumerate(labels,15) for s in pair}
    require(len(e)==189,'scaffold count')
    return e

def neighborhoods(e):
    n=[set() for _ in range(99)]
    for u,v in e: n[u].add(v);n[v].add(u)
    return n

def valid(n):
    return max(map(len,n))<=14 and all(len(n[u]&n[v])<=2-int(v in n[u]) for u,v in combinations(range(99),2))

def permissive(e,x):
    n=neighborhoods(e);require(valid(n),'positive prerequisites already invalid')
    hood=sorted(n[x]);require(len(hood)==14,'center not fully determined')
    forced={p for p in combinations(hood,2) if p in e}
    used=[v for p in forced for v in p];require(len(used)==len(set(used)),'forced edges not matching')
    free=sorted(set(hood)-set(used));allowed=set()
    for p in combinations(free,2):
        trial=[s.copy() for s in n];a,b=p;trial[a].add(b);trial[b].add(a)
        if valid(trial):allowed.add(p)
    return n,hood,forced,free,allowed

def components(nodes,e):
    remaining=set(nodes);result=[]
    while remaining:
        part={min(remaining)}
        while True:
            growth={v for a,b in e for u,v in ((a,b),(b,a)) if u in part and v in remaining}
            if growth<=part:break
            part|=growth
        result.append(sorted(part));remaining-=part
    return sorted(result)

def perfect_exists(nodes,e):
    # All reachable vertex subsets via an edge-by-edge subset DP; no
    # recursive least-unmatched-vertex matching search from the producer.
    where={v:i for i,v in enumerate(nodes)};reachable={0}
    for u,v in sorted(e):
        mask=(1<<where[u])|(1<<where[v])
        reachable|={s|mask for s in list(reachable) if not s&mask}
    return (1<<len(nodes))-1 in reachable

def check_record(r):
    core=edges(r['retained_K_edges_full99']);star=edges(r['center_star_edges_full99']);x=r['center_full99']
    require(x==r['outer_vertex']+15 and len(star)==8 and all(x in p for p in star),'center/star')
    protected=edges(r['protected_center_K_edges_full99'])
    require(protected=={p for p in core if x in p} and len(protected)==4,'protected center prerequisites')
    require(not(core&star) and not((core|star)&scaffold()) and r['negative_K_literals']==[],'positive literal scope')
    literal=core|star
    require(edges(r['cut']['positive_full99_edge_literals'])==literal and r['cut']['rhs']==len(literal)-1 and
            r['cut']['sense']=='<=' and r['cut']['coefficients']=='all1','clause identity')
    n,hood,forced,free,allowed=permissive(scaffold()|literal,x)
    g=r['reduced_graph']
    require(hood==r['all14_center_neighbors_full99']==g['neighborhood'] and forced==edges(g['forced_edges']) and
            free==g['free_vertices'] and allowed==edges(g['possible_edges']) and g['matching_exists']is False,'permissive graph differs')
    blocked={tuple(b['edge']):b['reason'] for b in g['blocked_edges']}
    require(len(blocked)==len(g['blocked_edges']) and set(blocked)==set(combinations(free,2))-allowed,'blocked partition')
    for (a,b),reason in blocked.items():
        trial=[s.copy() for s in n];trial[a].add(b);trial[b].add(a)
        if reason['kind']=='pair_cap':
            u,v=reason['pair'];common=sorted(trial[u]&trial[v]);bound=2-int(v in trial[u])
            require(common==reason['common_vertices'] and bound==reason['bound'] and len(common)>bound,'false explicit pair blocker')
        elif reason['kind']=='degree':
            u=reason['vertex'];require(u in (a,b) and sorted(n[u])==reason['present_neighbors'] and len(trial[u])>14,'false degree blocker')
        else:raise ValueError('unknown blocker')
    w=r['odd_component_certificate'];separator=set(w['separator'])
    require(separator<=set(free) and len(separator)==len(w['separator']),'separator scope')
    comps=components(set(free)-separator,allowed);odd=sum(len(c)%2 for c in comps)
    require(comps==sorted(w['components']) and odd==w['odd_component_count'] and len(separator)==w['separator_size'] and
            odd-len(separator)==w['deficiency']>0,'invalid parity obstruction')
    require(not perfect_exists(free,allowed),'edge-subset DP found perfect matching')
    return dict(outer_vertex=r['outer_vertex'],domain_id=r['domain_id'],positive_K_literals=len(core),positive_clause_literals=len(literal),
                free_vertices=len(free),allowed_pairs=len(allowed),blocked_pairs=len(blocked),separator_size=len(separator),odd_components=odd)

def main():
    started=time.perf_counter();bindings={}
    def read(p):
        p=Path(p);bindings[key(p)]=digest(p);return json.loads(p.read_bytes())
    out=ROOT/'acceleration/results/20260917_independent_review/matching_positive_cuts_recheck.json';require(not out.exists(),'preserve audit')
    for p in (__file__,ROOT/'docs/THEORY_20260917_MATCHING_CUT.md',ROOT/'uv.lock'):bindings[key(p)]=digest(p)
    manifest=read(DIR/'manifest.json');summary=read(DIR/'summary.json')
    require(digest(DIR/'manifest.json')==summary['manifest_sha256'],'manifest identity')
    for f,h in manifest['inputs_sha256'].items():
        require(digest(ROOT/f)==h,'input identity '+f);bindings[f]=h
    controls=[]
    for name,n,e,want in [('K4',list(range(4)),set(combinations(range(4),2)),True),
                           ('two_odd_components',list(range(6)),{(0,1),(1,2),(0,2),(3,4),(4,5),(3,5)},False),
                           ('repaired_bridge',list(range(6)),{(0,1),(1,2),(0,2),(3,4),(4,5),(3,5),(2,3)},True),('empty',[],set(),True)]:
        require(perfect_exists(n,e)==want,'matching control '+name);controls.append(dict(name=name,outcome='PASS'))
    results=[]
    for r in summary['records']:
        name=f"vertex_{r['outer_vertex']:02d}_domain_{r['domain_id']}.json"
        raw=read(DIR/name);require(raw==r and digest(DIR/name)==summary['result_artifacts_sha256'][name],'raw summary binding')
        results.append(check_record(raw))
    require(len(results)==summary['attempted_stars']==summary['successful_lifts']==16 and summary['failed_lifts']==0,'pilot inventory')
    for name in ('delete_center_prerequisite','delete_positive_clause_literal','forge_blocker','forge_separator','add_permissive_edge'):
        bad=deepcopy(summary['records'][0])
        if name=='delete_center_prerequisite':bad['retained_K_edges_full99'].pop(0)
        if name=='delete_positive_clause_literal':bad['cut']['positive_full99_edge_literals'].pop()
        if name=='forge_blocker':bad['reduced_graph']['blocked_edges'][0]['reason']['common_vertices']=[]
        if name=='forge_separator':bad['odd_component_certificate']['separator']=[]
        if name=='add_permissive_edge':bad['reduced_graph']['possible_edges'].append(bad['reduced_graph']['blocked_edges'][0]['edge'])
        try:check_record(bad)
        except ValueError as e:controls.append(dict(name=name,outcome='REJECT',reason=str(e)))
        else:raise ValueError('corruption accepted '+name)
    require(all(digest(ROOT/f)==h for f,h in bindings.items()),'input changed during review')
    result=dict(status='INDEPENDENT_POSITIVE_MATCHING_CUTS_PASS',claim_id='C-MATCHING-POSITIVE-CUTS-16',claim_revision=1,
        timestamp=datetime.now(timezone.utc).isoformat(),source_commit=manifest['source_commit'],inputs_sha256=bindings,
        verifier='independent_verifier agent; standalone set implementation, no producer imports',method='Complete full99 pair-cap checking after every possible free-neighbor insertion; exact separator components and independent edge-subset DP',
        command=[sys.executable]+sys.argv,working_directory=str(Path.cwd()),python=platform.python_version(),
        statement='For each of the16 hash-bound literal sets L, every srg(99,14,1,2) containing the fixed189 positive labeled root-scaffold edges satisfies sum(A_ab for ab in L)<=|L|-1, with every other adjacency unrestricted.',
        records=results,controls=controls,producer_imported=False,shared_trusted_components=['Python standard library','explicit fixed scaffold labeling'],
        assumptions=['fixed189 positive root-scaffold edges','target SRG degree14,lambda1,mu2'],
        limitations=['No complete overlap assignment newly excluded; clauses remain conditional','No minimal-core or greedy-search replay claim','Historical domain choice provenance and empirical containment not required for clause validity and not rechecked here','No target-wide coverage or nonexistence claim'],
        target_resolution='UNKNOWN',elapsed_seconds=time.perf_counter()-started)
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(status=result['status'],clauses=16,sha256=digest(out))))

if __name__=='__main__':main()
