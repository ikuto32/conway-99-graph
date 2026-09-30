"""Exact bounded literal-control extension test, with no archive producer imports."""
import argparse, collections, datetime, hashlib, itertools, json, time, traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
W='external_conway99_research/attempts/'
PINS={W+'wave205-nonedge-fourth-trace-proof-a/controls.json':'e52c068f5fdba18110debdd1455195ec22145f07993437b5438e8f77ae03fdcf',
W+'wave205-nonedge-fourth-trace-proof-a/derivation.md':'b7ff8bae8bee7b12776d2ae05d8af771ca23d12d67852c78bdea343d84bf8b50',
W+'wave205-global-fourth-moment-proof-b/derivation.md':'28ad3e3d2bd324e9b7cf5c2d2a7284aa938436f1477c1165ecc948b1edf222c4',
W+'wave205-fourth-trace-hostile-controls/derivation.md':'cd36b734ec9d05827ba06c1423754ecb0f3c903b690dc5f62883f3b5baee460b',
'external_conway99_research/verification/wave205-fourth-trace-globalization-verifier/post_source_result.json':'0e9a1091d3863be3f9b69d1b4903c4d14db2b59f27820cde81906f1fe06459c5',
'acceleration/results/20260930_srg243_residual_fixture/adjacency243.json':'5c7c8268b7d62997b5c87a56b11fd673f3f80fcb029b83816179ee8127b8e0d3'}
def need(q,m):
    if not q:raise ValueError(m)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf8')
def read(p):return json.loads((ROOT/p).read_text(encoding='utf8'))
def bits(n):
    while n:
        v=n&-n;yield v.bit_length()-1;n-=v
def rank(A):
    if not A:return 0
    a=[[x%3 for x in r] for r in A];k=0
    for j in range(len(a[0])):
        p=next((i for i in range(k,len(a)) if a[i][j]),None)
        if p is None:continue
        a[k],a[p]=a[p],a[k];s=pow(a[k][j],-1,3);a[k]=[(x*s)%3 for x in a[k]]
        for i in range(k+1,len(a)):
            if a[i][j]:
                t=a[i][j];a[i]=[(x-t*y)%3 for x,y in zip(a[i],a[k])]
        k+=1
        if k==len(a):break
    return k
def inverse(A):
    n=len(A);a=[[x%3 for x in r]+[int(i==j) for j in range(n)] for i,r in enumerate(A)]
    for j in range(n):
        p=next((i for i in range(j,n) if a[i][j]),None);need(p is not None,'invertible principal block')
        a[j],a[p]=a[p],a[j];s=pow(a[j][j],-1,3);a[j]=[(x*s)%3 for x in a[j]]
        for i in range(n):
            if i!=j and a[i][j]:
                t=a[i][j];a[i]=[(x-t*y)%3 for x,y in zip(a[i],a[j])]
    return [r[n:] for r in a]
def principal(A,r):
    if r==0:return [],[]
    for I in itertools.combinations(range(len(A)),r):
        M=[[A[i][j] for j in I] for i in I]
        if rank(M)==r:return list(I),inverse(M)
    raise ValueError('missing full-rank principal block')
def extension(A,I,inv,c,d=0):
    u=[sum(a*c[j] for a,j in zip(row,I))%3 for row in inv]
    image=[sum(row[j]*v for j,v in zip(I,u))%3 for row in A]
    if image!=[v%3 for v in c]:return False,'GRAM_IMAGE',u
    norm=sum(c[j]*v for j,v in zip(I,u))%3
    if norm!=d%3:return False,'GRAM_NORM',u
    return True,'PASS',u
def gram(rows,triangles):
    return [[sum((rows[u]>>v)&1 for u in a for v in b)%3 for b in triangles] for a in triangles]
def triangles(rows):
    return [(a,b,c) for a in range(len(rows)) for b in bits(rows[a]) if b>a for c in bits(rows[a]&rows[b]) if c>b]
def caps(rows):
    for a,b in itertools.combinations(range(len(rows)),2):
        n=(rows[a]&rows[b]).bit_count();cap=1 if (rows[a]>>b)&1 else 2
        if n>cap:return dict(pair=[a,b],observed=n,cap=cap)
    return None
def prism(rows,ts):
    for i,a in enumerate(ts):
        for b in ts[i+1:]:
            if set(a).isdisjoint(b):
                n=sum((rows[u]>>v)&1 for u in a for v in b)
                if n>2:return dict(triangles=[a,b],cross_edges=n)
    return None
def add_edge(rows,a,b):rows[a]|=1<<b;rows[b]|=1<<a
def add_triangle(base,a,xpair,ypair,orientation):
    rows=base[:]+[0,0];p=len(base);q=p+1
    for u,v in [(a,p),(a,q),(p,q),(p,xpair[0]),(q,xpair[1]),(p,ypair[orientation]),(q,ypair[1-orientation])]:add_edge(rows,u,v)
    return rows,(a,p,q)
def control_base():
    raw=read(W+'wave205-nonedge-fourth-trace-proof-a/controls.json');c=next(c for c in raw['controls'] if c['name']=='t6_h1');conv=raw['vertex_convention']
    labels=sorted(set(['x','y']+sum(conv['x_blocks_without_center']+conv['y_blocks_without_center'],[])));ix={s:i for i,s in enumerate(labels)}
    rows=[0]*len(labels);stars={}
    for center,key in [('x','x_blocks_without_center'),('y','y_blocks_without_center')]:
        stars[center]=[tuple(ix[s] for s in [center]+pair) for pair in conv[key]]
        for t in stars[center]:
            for u,v in itertools.combinations(t,2):add_edge(rows,u,v)
    for u,v in c['exclusive_cross_edges']:add_edge(rows,ix[u],ix[v])
    need(len(rows)==28 and caps(rows) is None,'literal local graph valid')
    T=stars['x']+stars['y'];G=gram(rows,T)
    need([[int(z) for z in r] for r in c['cross_gram_rows']]==[r[7:] for r in G[:7]],'literal cross Gram')
    need(rank(G)==11 and len(triangles(rows))==14,'original rank11 and triangle inventory')
    for center in ['x','y']:
        n=ix[center];need(rows[n].bit_count()==14,'old center degree')
        for v in range(28):
            if v!=n:need((rows[n]&rows[v]).bit_count()==(1 if rows[n]>>v&1 else 2),'old center exact common-neighbour profile')
    need(prism(rows,T) is None,'old prism-free graph')
    return labels,ix,rows,T,G
def controls():
    n=0
    for a,b,d in itertools.product(range(3),repeat=3):
        A=[[a,b],[b,d]];r=rank(A);I,inv=principal(A,r)
        for c in itertools.product(range(3),repeat=2):
            for e in range(3):
                check=extension(A,I,inv,c,e)[0]
                direct=rank([A[i]+[c[i]] for i in range(2)]+[list(c)+[e]])==r
                need(check==direct,'small extension direct-rank control');n+=1
    raw=read('acceleration/results/20260930_srg243_residual_fixture/adjacency243.json');A=raw['adjacency'];rr=[sum(v<<j for j,v in enumerate(row)) for row in A]
    need(len(A)==243 and all(rr[i].bit_count()==22 and not(rr[i]>>i&1) for i in range(243)),'243 generic degree')
    need(all(A[i][j]==A[j][i] and (rr[i]&rr[j]).bit_count()==(1 if A[i][j] else 2) for i,j in itertools.combinations(range(243),2)),'243 generic SRG')
    return dict(exhaustive_small_extension_cases=n,genuine243_generic_srg=True,genuine243_rank11_prism_free_positive=False)
def run(out):
    start=time.monotonic();deadline=start+120;nodes=0;leaves=0;last_save=start
    def budget():
        if time.monotonic()>deadline:raise TimeoutError('120s cooperative allocation')
    for p,h in PINS.items():need(sha(ROOT/p)==h,'input '+p)
    cal=controls();labels,ix,base,T,G=control_base();a=ix['a'];x=ix['x'];y=ix['y'];b=ix['b']
    need(set(bits(base[a]))=={x,y,ix['alpha'],ix['gamma']},'four fixed neighbours of a')
    elig={};deficits={}
    for center in (x,y):
        side=[]
        for v in bits(base[center]):
            if v==a or (base[a]>>v)&1:continue
            d=2-(base[a]&base[v]).bit_count();need(d in (0,1),'old exact a-pair deficit')
            deficits[labels[v]]=d
            if d:side.append(v)
        need(len(side)==10 and b not in side,'ten required unique attachment positions');elig[center]=sorted(side)
    need(set(elig[x]).isdisjoint(elig[y]),'exclusive eligible sides')
    I,inv=principal(G,11)
    # Corruptions are checked independently before enumerating options.
    bad=base[:];add_edge(bad,ix['alpha'],ix['beta']);need(caps(bad) is not None,'corrupted old edge rejected')
    wrong=[r[:] for r in G];wrong[0][0]=1;need(wrong!=gram(base,T),'wrong target Gram rejected')
    duplicate=elig[x][:-1]+[elig[x][0]];need(len(set(duplicate))!=10,'duplicate attachment inventory rejected')
    cal['corruptions_rejected']=['old added edge','wrong target Gram','duplicate attachment label']
    save(out/'controls.json',cal)
    save(out/'literal_control.json',dict(labels=labels,rows=base,triangles=T,gram=G,rank=11,third_center=a,
        eligible_X=elig[x],eligible_Y=elig[y],old_pair_deficits=deficits,principal_indices=I,principal_inverse=inv))
    records=[];options=[];hist=collections.Counter()
    for xp in itertools.combinations(elig[x],2):
        for yp in itertools.combinations(elig[y],2):
            for orient in (0,1):
                budget();rows,tri=add_triangle(base,a,xp,yp,orient)
                rec=dict(id=len(records),x_pair=xp,y_pair=yp,orientation=orient)
                failure=caps(rows)
                if failure:stage='INTEGER_COMMON_CAP';rec['failure']=failure
                else:
                    ts=triangles(rows);failure=prism(rows,ts)
                    if failure:stage='INTEGER_PRISM_CAP';rec['failure']=failure
                    else:
                        c=[sum((rows[u]>>v)&1 for u in t for v in tri)%3 for t in T]
                        ok,stage,u=extension(G,I,inv,c,0);rec.update(gram_column=c,coordinates=u)
                        if ok:
                            rec['status']='RETAINED';options.append(rec)
                if 'status' not in rec:rec['status']=stage
                hist[rec['status']]+=1;records.append(rec)
    need(len(records)==4050,'complete triangle candidate population')
    save(out/'triangle_candidates.json',dict(records=records,first_failure_histogram=dict(hist),retained_ids=[r['id'] for r in options]))
    # Pairwise rank compatibility uses the same full-rank old principal block.
    M=[[G[i][j] for j in I] for i in I]
    def dot(p,q):return sum(p['coordinates'][i]*M[i][j]*q['coordinates'][j] for i in range(11) for j in range(11))%3
    byx={v:[o for o in options if v in o['x_pair']] for v in elig[x]};leaf_failures=collections.Counter();first_leaf_failures={};witness=None
    def check_leaf(chosen):
        rows=base[:];triangles_added=[]
        for o in chosen:rows,t=add_triangle(rows,a,o['x_pair'],o['y_pair'],o['orientation']);triangles_added.append(t)
        need(len(rows)==38,'literal38 union')
        f=caps(rows)
        if f:return 'COMMON_CAP',f
        for center in (x,y,a):
            if rows[center].bit_count()!=14:return 'CENTER_DEGREE',dict(center=center)
            for v in range(38):
                if v!=center and (rows[center]&rows[v]).bit_count()!=(1 if rows[center]>>v&1 else 2):return 'CENTER_COMMON',dict(center=center,vertex=v)
        ts=triangles(rows);f=prism(rows,ts)
        if f:return 'PRISM_CAP',f
        full=gram(rows,ts);r=rank(full)
        if r!=11:return 'ALL_TRIANGLE_GRAM_RANK',dict(rank=r,triangle_count=len(ts))
        return 'PASS',dict(labels=labels+['a_new_'+str(i) for i in range(10)],rows=rows,triangles=ts,gram=full,rank=r,option_ids=[o['id'] for o in chosen],centers=[x,y,a])
    def dfs(chosen,X,Y):
        nonlocal nodes,leaves,last_save,witness
        nodes+=1;budget()
        if time.monotonic()-last_save>5:
            save(out/'progress.json',dict(nodes=nodes,leaves=leaves,elapsed_seconds=time.monotonic()-start,status='RUNNING_CANDIDATE'));last_save=time.monotonic()
        if len(X)==10:
            leaves+=1;stage,data=check_leaf(chosen)
            if stage=='PASS':witness=data;return True
            leaf_failures[stage]+=1;first_leaf_failures.setdefault(stage,dict(option_ids=[o['id'] for o in chosen],failure=data));return False
        v=next(v for v in elig[x] if v not in X)
        for o in byx[v]:
            if X.intersection(o['x_pair']) or Y.intersection(o['y_pair']):continue
            if any(dot(o,p)!=1 for p in chosen):continue
            if dfs(chosen+[o],X|set(o['x_pair']),Y|set(o['y_pair'])):return True
        return False
    timed_out=False
    try:dfs([],set(),set())
    except TimeoutError:timed_out=True
    status='CANDIDATE_THIRD_STAR_WITNESS' if witness else ('PARTIAL_UNKNOWN' if timed_out else 'CANDIDATE_LITERAL_THIRD_STAR_OBSTRUCTION')
    if witness:save(out/'witness.json',witness)
    save(out/'search.json',dict(status=status,nodes=nodes,complete_leaves=leaves,timed_out=timed_out,leaf_failures=dict(leaf_failures),first_leaf_failures=first_leaf_failures))
    source=Path(__file__);spec=source.with_name(source.stem+'_spec.md');inputs=dict(PINS)
    for p in [source,spec]:inputs[p.relative_to(ROOT).as_posix()]=sha(p)
    save(out/'summary.json',dict(schema='WAVE205_LITERAL_THIRD_STAR_V1',status=status,created_at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        inputs_sha256=inputs,outputs_sha256={p.as_posix():sha(p) for p in out.iterdir() if p.is_file()},
        selected_control='t6_h1',third_center='a',triangle_candidates=4050,retained_triangle_options=len(options),candidate_failures=dict(hist),
        nodes=nodes,complete_leaves=leaves,elapsed_seconds=time.monotonic()-start,independent_approval=False,solver_calls=0,
        scope='Only extensions retaining literal induced28-vertex t6_h1, completing the a-star, prism-free and ternary triangle Gram rank11; no whole-branch or target exclusion.'))
    print(json.dumps(dict(status=status,retained=len(options),candidate_failures=dict(hist),nodes=nodes,leaves=leaves,elapsed_seconds=time.monotonic()-start)))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);a=ap.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=False)
    try:run(out)
    except BaseException as e:save(out/'failure.json',dict(error=repr(e),traceback=traceback.format_exc()));raise
if __name__=='__main__':main()
