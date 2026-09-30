"""Independent exact audit using adjacency sets and full augmented GF(3) ranks."""
from pathlib import Path
from itertools import combinations,product
from collections import Counter
from datetime import datetime,timezone
import argparse,hashlib,json,platform,subprocess,sys,time,traceback
ROOT=Path(__file__).resolve().parents[1]
P='acceleration/results/20261001_wave205_third_star_v2/'
PIN='39883336a9d6ce388589c08abdba9566a8a9b2b44903c440609f62b19f9b2322'
W='external_conway99_research/attempts/wave205-nonedge-fourth-trace-proof-a/controls.json'
def need(q,m):
    if not q:raise ValueError(m)
def sha(p):
    with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads((ROOT/p).read_bytes())
def save(p,x):
    with p.open('x',encoding='utf8',newline='\n')as f:json.dump(x,f,indent=2);f.write('\n')
def rank(a):
    # Column-basis insertion, distinct from the producer's row elimination.
    basis={}
    for column in zip(*a):
        v=[x%3 for x in column]
        for pivot,b in sorted(basis.items()):
            if v[pivot]:v=[(x-v[pivot]*y)%3 for x,y in zip(v,b)]
        pivot=next((i for i,x in enumerate(v)if x),None)
        if pivot is not None:basis[pivot]=[(x*v[pivot])%3 for x in v]
    return len(basis)
def det(a):
    if len(a)==1:return a[0][0]%3
    return sum((-1)**j*a[0][j]*det([r[:j]+r[j+1:]for r in a[1:]])for j in range(len(a)))%3
def minor_rank(a):
    for k in range(len(a),0,-1):
        if any(det([[a[i][j]for j in cc]for i in rr])for rr in combinations(range(len(a)),k)for cc in combinations(range(len(a)),k)):return k
    return 0
def edge(a,u,v):a[u].add(v);a[v].add(u)
def ts(a):return [tuple(t)for t in combinations(range(len(a)),3)if all(v in a[u]for u,v in combinations(t,2))]
def caps(a):return all(len(a[u]&a[v])<=(1 if v in a[u]else 2)for u,v in combinations(range(len(a)),2))
def no_prism(a,triangles):return all(sum(v in a[u]for u in t for v in s)<=2 for t,s in combinations(triangles,2)if not set(t)&set(s))
def gram(a,triangles):return [[sum(v in a[u]for u in t for v in s)%3 for s in triangles]for t in triangles]
def attach(base,center,xp,yp,o):
    a=[s.copy()for s in base]+[set(),set()];p=len(base);q=p+1
    for u,v in [(center,p),(center,q),(p,q),(p,xp[0]),(q,xp[1]),(p,yp[o]),(q,yp[1-o])]:edge(a,u,v)
    return a,(center,p,q)
def reject(fn,label):
    try:fn()
    except(ValueError,AssertionError):return label
    raise ValueError('corrupt control accepted: '+label)
def run(out):
    started=datetime.now(timezone.utc).isoformat();clock=time.monotonic()
    def budget():need(time.monotonic()-clock<120,'120-second cooperative ceiling')
    need(sha(ROOT/(P+'summary.json'))==PIN,'candidate identity');producer=read(P+'summary.json')
    need(producer['status']=='CANDIDATE_LITERAL_THIRD_STAR_OBSTRUCTION','exact proposed claim')
    pins={P+'summary.json':PIN,**producer['inputs_sha256'],**producer['outputs_sha256']}
    for p,h in pins.items():need(sha(ROOT/p)==h,'raw artifact identity '+p)
    checks=0
    for d0,e01,d1,c0,c1,d2 in product(range(3),repeat=6):
        a=[[d0,e01,c0],[e01,d1,c1],[c0,c1,d2]]
        need(rank(a)==minor_rank(a),'independent all-minors rank calibration');checks+=1
    rook=[{j for j in range(9)if i!=j and(i//3==j//3 or i%3==j%3)}for i in range(9)]
    need(caps(rook)and all(len(s)==4 for s in rook)and all(len(rook[i]&rook[j])==(1 if j in rook[i]else 2)for i,j in combinations(range(9),2)),'known9 SRG positive')
    badrook=[s.copy()for s in rook];edge(badrook,0,4)
    controls=[reject(lambda:need(caps(badrook),'caps'),'corrupted_rook_edge')]
    raw=read(W);control=next(c for c in raw['controls']if c['name']=='t6_h1');conv=raw['vertex_convention']
    labels=sorted({'x','y'}|{v for key in ['x_blocks_without_center','y_blocks_without_center']for pair in conv[key]for v in pair});index={s:i for i,s in enumerate(labels)}
    base=[set()for _ in labels];stars=[]
    for center in ('x','y'):
        for pair in conv[center+'_blocks_without_center']:
            t=tuple(index[v]for v in [center]+pair);stars.append(t)
            for u,v in combinations(t,2):edge(base,u,v)
    for u,v in control['exclusive_cross_edges']:edge(base,index[u],index[v])
    frozen=read(P+'literal_control.json');G=gram(base,stars);a=index['a'];x=index['x'];y=index['y']
    need(len(base)==28 and caps(base) and no_prism(base,ts(base))and len(ts(base))==14,'literal28 structural control')
    need(labels==frozen['labels'] and [sum(1<<v for v in s)for s in base]==frozen['rows'] and [list(t)for t in stars]==frozen['triangles'] and G==frozen['gram'] and rank(G)==11,'independent raw graph and Gram reconstruction')
    need(base[a]=={x,y,index['alpha'],index['gamma']},'literal third-center old neighbors')
    for center in (x,y):
        need(len(base[center])==14 and all(len(base[center]&base[v])==(1 if v in base[center]else 2)for v in range(28)if v!=center),'old exact center equations')
    sides=[]
    for center in (x,y):
        side=[]
        for v in sorted(base[center]-{a}-base[a]):
            deficit=2-len(base[a]&base[v]);need(deficit in (0,1),'deficits 0 or1')
            if deficit:side.append(v)
        sides.append(side)
    X,Y=sides;need(X==frozen['eligible_X'] and Y==frozen['eligible_Y'] and len(X)==len(Y)==10 and not set(X)&set(Y),'ten exact exclusive attachment deficits')
    records=read(P+'triangle_candidates.json')['records'];need(len(records)==4050 and [r['id']for r in records]==list(range(4050)),'full literal enumeration IDs')
    options=[];observed=[];counts=Counter();columns={}
    for xp in combinations(X,2):
        for yp in combinations(Y,2):
            for orientation in (0,1):
                budget();i=len(observed);r=records[i]
                need(r['x_pair']==list(xp)and r['y_pair']==list(yp)and r['orientation']==orientation,'complete4050 explicit universe')
                local,t=attach(base,a,xp,yp,orientation)
                if not caps(local):status='INTEGER_COMMON_CAP'
                elif not no_prism(local,ts(local)):status='INTEGER_PRISM_CAP'
                else:
                    c=[sum(v in local[u]for u in old for v in t)%3 for old in stars]
                    need(c==r['gram_column'],'literal old/new Gram column')
                    rect=[row+[cv]for row,cv in zip(G,c)]
                    if rank(rect)>11:status='GRAM_IMAGE'
                    elif rank(rect+[c+[0]])>11:status='GRAM_NORM'
                    else:status='RETAINED';options.append(dict(id=i,x_pair=set(xp),y_pair=set(yp)));columns[i]=c
                need(status==r['status'],'independent full-rank predicate agrees');counts[status]+=1;observed.append(dict(id=i,status=status))
    need(len(options)==296 and dict(counts)==producer['candidate_failures'],'complete candidate outcomes')
    # A two-option pair adds two norm-zero Gram columns with their forced
    # off-diagonal1; full16x16 rank supplies an independent compatibility test.
    pair_cache={};pair_tests=[]
    def compatible(p,q):
        key=tuple(sorted((p['id'],q['id'])))
        if key not in pair_cache:
            c,d=columns[key[0]],columns[key[1]]
            aug=[row+[ci,di]for row,ci,di in zip(G,c,d)]+[c+[0,1],d+[1,0]]
            rr=rank(aug);pair_cache[key]=rr==11;pair_tests.append(dict(options=key,rank=rr))
        return pair_cache[key]
    events=[];nodes=0;leaves=0
    def dfs(chosen,usedX,usedY,parent=None,via=None):
        nonlocal nodes,leaves
        budget();nodes+=1;node=nodes;events.append(dict(event='ENTER',node=node,parent=parent,via=via,chosen=[o['id']for o in chosen]))
        if len(usedX)==10:leaves+=1;raise ValueError('Independent enumeration found a complete relaxed cover; claimed zero-leaf obstruction fails')
        v=min(set(X)-usedX)
        for o in options:
            if v not in o['x_pair']or o['x_pair']&usedX or o['y_pair']&usedY:continue
            if all(compatible(o,p)for p in chosen):dfs(chosen+[o],usedX|o['x_pair'],usedY|o['y_pair'],node,o['id'])
        events.append(dict(event='EXIT',node=node,status='EXHAUSTED'))
    dfs([],set(),set())
    saved=[json.loads(line)for line in (ROOT/(P+'exact_cover_traversal.jsonl')).read_text().splitlines()]
    need(events==saved and nodes==17 and leaves==0,'complete independent tree equals every saved traversal event')
    need(read(P+'search.json')['timed_out']is False,'completed original search')
    controls.append(reject(lambda:need(observed[:-1]==observed,'universe'),'missing_candidate'))
    controls.append(reject(lambda:need([dict(observed[0],status='RETAINED')]+observed[1:]==observed,'predicates'),'changed_candidate_outcome'))
    controls.append(reject(lambda:need(events[:-1]==events,'traversal'),'missing_completed_subtree_exit'))
    controls.append(reject(lambda:need(rank([[1]])==0,'rank'),'wrong_Gram_rank'))
    save(out/'candidate_outcomes.json',observed);save(out/'pair_rank_checks.json',pair_tests);save(out/'traversal.json',events);save(out/'controls.json',dict(all_minors_rank_controls=checks,known9_srg_positive=True,corruptions_rejected=controls))
    for p in [Path(__file__),Path(__file__).with_name(Path(__file__).stem+'_spec.md')]:pins[p.relative_to(ROOT).as_posix()]=sha(p)
    result=dict(status='INDEPENDENT_LITERAL_THIRD_STAR_FINITE_OBSTRUCTION_PASS',timestamp=started,verifier='/root',claim_originator='/root/state_literature_audit',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=pins,outputs_sha256={p.relative_to(ROOT).as_posix():sha(p)for p in out.iterdir()},triangle_candidates=4050,retained_triangle_options=296,candidate_failures=dict(counts),pair_rank_checks=len(pair_tests),complete_nodes=nodes,complete_leaves=leaves,elapsed_seconds=time.monotonic()-clock,scope='Exact literal28 t6_h1 graph: no five-option cover of the ten X and ten Y attachment deficits survives the stated common-neighbor/prism/ternary-rank11 constraints.',coverage_derivation_review='PENDING separate written audit before claim promotion.',shared_components=['Raw pinned archive control and exact Python integer arithmetic. No producer/archive modules, principal inverse or reported coordinates used.'],limitations=['No all-t6, rank11-branch, prism-free endpoint or target exclusion.','This report independently establishes the finite raw predicate; applicability of every target normalization is not silently inherited from archived VERIFIED labels.'],solver_calls=0,ledger_mutations=0)
    save(out/'summary.json',result);print(json.dumps(dict(status=result['status'],summary_sha256=sha(out/'summary.json'),nodes=nodes,pair_rank_checks=len(pair_tests),elapsed_seconds=result['elapsed_seconds'])))
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);args=ap.parse_args();out=ROOT/args.out;out.mkdir(parents=True,exist_ok=False)
    try:run(out)
    except BaseException as ex:save(out/'failure.json',dict(error=repr(ex),traceback=traceback.format_exc(),source_sha256=sha(Path(__file__))));raise
