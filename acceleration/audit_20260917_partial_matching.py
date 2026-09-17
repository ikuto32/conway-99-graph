"""Independent fixed-label multiway enumeration of partial-K local domains."""
from datetime import datetime,timezone
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import platform
import sys
import time
from tqdm import tqdm

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'acceleration/results/20260917_partial_matching'
O=ROOT/'acceleration/results/20260917_independent_review/partial_matching'
def require(ok,msg):
    if not ok:raise ValueError(msg)
def digest(p):return sha256(Path(p).read_bytes()).hexdigest()
def key(p):return Path(p).resolve().relative_to(ROOT).as_posix()
def bits(m):return [i for i in range(m.bit_length())if m>>i&1]
def valid(rows):return all(r.bit_count()<=14 for r in rows)and all((rows[u]&rows[v]).bit_count()<=2-int(bool(rows[u]>>v&1))for u,v in combinations(range(99),2))
def add(rows,u,v):rows[u]|=1<<v;rows[v]|=1<<u

def enumerate_all(B,labels,unknown,u,deadline,nodecap,restricted=None):
    x=u+15;need=14-B[x].bit_count();pool=sorted(v if a==u else a for a,v in unknown if u in (a,v))
    if restricted is not None:pool=[v for v in pool if v in restricted]
    single=[]
    for v in pool:
        trial=B.copy();add(trial,x,v+15)
        if valid(trial):single.append(v)
    demands=tuple(2-int(bool(B[x]>>(s+1)&1))-(B[x]&B[s+1]).bit_count()for s in range(14))
    capacity=[99 if w==x else 2-int(bool(B[x]>>w&1))-(B[x]&B[w]).bit_count()for w in range(99)]
    resources={v:bits(B[v+15]|(1<<(v+15)))for v in single}
    forbidden={v:{w for w in single if w!=v and (B[v+15]&B[w+15]).bit_count()>=2-int(bool(B[v+15]>>(w+15)&1))}for v in single}
    found=[];nodes=0
    def walk(pool,chosen,demands,capacity):
        nonlocal nodes
        nodes+=1
        if nodes>nodecap or nodes%1024==0 and time.monotonic()>deadline:raise RuntimeError('independent enumeration resource cap')
        if not any(demands):
            require(len(chosen)==need,'completed chosen size');found.append(sum(1<<v for v in chosen));return
        pool=[v for v in pool if all(demands[s]>0 for s in labels[v])and all(capacity[w]>0 for w in resources[v])]
        for s,n in enumerate(demands):
            if sum(s in labels[v]for v in pool)<n:return
        s=next(i for i,n in enumerate(demands)if n)
        # Multiway branch on the complete demanded subset of the first
        # unsatisfied label. No producer MRV/binary include-exclude search.
        options=[v for v in pool if s in labels[v]]
        rest=[v for v in pool if s not in labels[v]]
        for group in combinations(options,demands[s]):
            if any(w in forbidden[v]for v,w in combinations(group,2)):continue
            d=list(demands);c=capacity.copy()
            for v in group:
                for t in labels[v]:d[t]-=1
                for w in resources[v]:c[w]-=1
            if min(d)<0 or min(c)<0:continue
            blocked=set().union(*(forbidden[v]for v in group))
            walk([v for v in rest if v not in blocked],chosen+group,tuple(d),c)
    walk(single,(),demands,capacity)
    require(len(found)==len(set(found)),'enumeration duplicates')
    return sorted(found),nodes,single

def direct(B,labels,u,mask):
    r=B.copy();x=u+15
    for v in bits(mask):add(r,x,v+15)
    return r[x].bit_count()==14 and valid(r)and all((r[x]&r[s+1]).bit_count()==2-int(bool(r[x]>>(s+1)&1))for s in range(14))

def main():
    O.mkdir(exist_ok=True);require(not(O/'summary.json').exists(),'preserve audit');bindings={}
    def read(p):
        bindings[key(p)]=digest(p);d=json.loads(Path(p).read_bytes())
        if isinstance(d,dict):
            for f,h in d.get('inputs_sha256',{}).items():require(digest(ROOT/f)==h,'input changed');bindings[f]=h
        return d
    for p in (__file__,ROOT/'uv.lock'):bindings[key(p)]=digest(p)
    manifest=read(D/'manifest.json');summary=read(D/'summary.json');caps=read(D/'linear_caps.json')
    basepath=next(f for f in manifest['inputs_sha256']if f.endswith('_candidate.json'));oldpath=next(f for f in manifest['inputs_sha256']if f.endswith('/stars.json'))
    candidate=read(ROOT/basepath);old=read(ROOT/oldpath)
    labels=[(2*a+s,2*b+t)for a,b in combinations(range(7),2)for s in range(2)for t in range(2)]
    support=[{s//2 for s in p}for p in labels];affected=[u for u,p in enumerate(labels)if 0 in p]
    Y={p for p in combinations(affected,2)if len(support[p[0]]&support[p[1]])==1};K=set(map(tuple,candidate['overlap_edges_outer_zero_based']));removed=K&Y;fixed=K-removed
    require(len(Y)==60 and len(removed)==6 and len(fixed)==162,'coordinate sizes')
    require(sorted(map(list,removed))==manifest['removed_edges_outer']and sorted(map(list,fixed))==manifest['remaining_fixed_K_edges_outer']and sorted(map(list,Y))==manifest['freed_legal_matching_edges_outer']and affected==manifest['affected_outer_vertices'],'scope coordinate identity')
    B=[0]*99
    for v in range(1,15):add(B,0,v)
    for v in range(1,15,2):add(B,v,v+1)
    for u,p in enumerate(labels,15):
        for s in p:add(B,u,s+1)
    for u,v in fixed:add(B,u+15,v+15)
    unknown=sorted(Y|{(u,v)for u,v in combinations(range(84),2)if not support[u]&support[v]})
    require(valid(B)and len(unknown)==1740 and len(fixed)==162 and len(Y)==60 and len(affected)==12,'partial graph universe')
    require(caps['variable_edges']==list(map(list,unknown)),'linear variable inventory')
    # Independent derivative (BE+EB+E)_ab for each sparse unit edge E.
    for (u,v),saved in zip(combinations(range(84),2),caps['caps']):
        terms=[];a,b=u+15,v+15
        for i,(p,q)in enumerate(unknown):
            P,Q=p+15,q+15
            coefficient=int((u,v)==(p,q))
            coefficient+=int(bool(B[a]>>P&1))*(b==Q)+int(bool(B[a]>>Q&1))*(b==P)
            coefficient+=(a==P)*int(bool(B[Q]>>b&1))+(a==Q)*int(bool(B[P]>>b&1))
            if coefficient:terms.append([i,coefficient])
        require(saved==dict(pair=[u,v],rhs=2-int(bool(B[a]>>b&1))-(B[a]&B[b]).bit_count(),terms=terms),'exact derivative cap row')
    require(len(caps['caps'])==3486,'cap population')
    started=time.monotonic();deadline=started+600
    audit_manifest=dict(timestamp=datetime.now(timezone.utc).isoformat(),question='Complete exact local domains and1740-variable/3486cap model on frozen one-freed-coordinate scope',
        source_commit=manifest['source_commit'],inputs_sha256=bindings,command=[sys.executable]+sys.argv,python=platform.python_version(),
        selection='All84centers; deterministic first unsatisfied root label, enumerate full demanded subsets',limits=dict(seconds=600,nodes_per_center=5000000),
        acceptance='Exact full set equality, no timeout or truncation; direct partial graph androot quotas; no numerical proof threshold')
    (O/'manifest.json').open('x').write(json.dumps(audit_manifest,indent=2)+'\n')
    reports=[];tables=[]
    for u in tqdm(range(84),desc='Independent partialK domains',unit='center'):
        saved=read(D/f'domain_{u:02d}.json');found,nodes,single=enumerate_all(B,labels,unknown,u,deadline,5000000)
        expected=sorted(int(s,16)for s in saved['domain_masks_hex'])
        require(found==expected and len(found)==saved['domain_size']and single==saved['allowed_single_neighbors'],'complete domain equality')
        require(saved['missing_neighbor_count']==(9 if u in affected else 8),'missing neighbor count')
        # Direct full99 verification for every claimed leaf; no resource-formula trust alone.
        require(all(direct(B,labels,u,m)for m in found),'direct full99 leaf rejection')
        oldmasks=[int(s,16)for s in old['domains'][u]['domain_masks_hex']]
        extra=sum(1<<v for a,v in removed if a==u)+sum(1<<a for a,v in removed if v==u)
        found_set=set(found)
        require(all((m|extra)in found_set for m in oldmasks),'historical embedding')
        row=dict(outer_vertex=u,complete_domain_size=len(found),independent_search_nodes=nodes,direct_full99_leaves=len(found),historical_embedded=len(oldmasks))
        reports.append(row);tables.append(found);(O/f'vertex_{u:02d}.json').open('x').write(json.dumps(row,indent=2)+'\n')
    controls=[]
    for u in (0,2):
        selected=bits(tables[u][0]);pool=sorted(selected+[v for v in bits(tables[u][-1])if v not in selected][:12-len(selected)])
        need=14-B[u+15].bit_count();brute=sorted(sum(1<<v for v in group)for group in combinations(pool,need)if direct(B,labels,u,sum(1<<v for v in group)))
        actual,_,_=enumerate_all(B,labels,unknown,u,deadline,5000000,set(pool));require(brute==actual,'independent restricted exhaustive control')
        controls.append(dict(outer_vertex=u,restricted_pool=pool,subsets_checked=len(list(combinations(pool,need))),valid_count=len(brute),outcome='PASS'))
    require(not direct(B,labels,0,0),'corrupt empty star accepted')
    controls.append(dict(name='zero_mask_missing_degree',outcome='REJECT'))
    require(all(digest(ROOT/f)==h for f,h in bindings.items()),'inputs changed')
    total=sum(map(len,tables));require(total==summary['new_domain_choices']==54478,'domain total')
    result=dict(status='INDEPENDENT_PARTIAL_K_DOMAINS_AND_LINEAR_CAPS_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=manifest['source_commit'],
        inputs_sha256=bindings,command=[sys.executable]+sys.argv,working_directory=str(Path.cwd()),python=platform.python_version(),
        claim_id='C-PARTIAL-K-ONE-COORDINATE-DOMAINS',claim_revision=1,recommendation='VERIFIED',records=reports,domain_choices=total,centers=84,
        variable_edges=1740,freed_matching_edges=60,fixed_K_edges=162,linear_caps=3486,controls=controls,
        scope='Exactly prescribed162positiveKedges and all same-fibre/unlisted-other-coordinate absences; only one60edge matching coordinate and1680disjoint edges unfixed',
        objective='PARTIAL_K_STAR_RECIPROCITY_CAP_PHASE1_V1',different_domain_from_original_star=True,producer_imported=False,
        limitations=['No LP exact feasibility or exclusion established','No whole-target coverage or nonexistence','Saved floating objective is diagnostic only','Solver matrix serialization not available; linear caps checked exactly, saved primal point requires separate audit'],
        target_resolution='UNKNOWN',elapsed_seconds=time.monotonic()-started)
    (O/'summary.json').open('x').write(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(status=result['status'],choices=total,sha256=digest(O/'summary.json'))))

if __name__=='__main__':main()
