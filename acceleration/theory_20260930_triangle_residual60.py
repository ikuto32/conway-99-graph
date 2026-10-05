"""Candidate exact residual completion equivalence and cheap factor screen.

Preparation only: no actual36x60 factor is assumed or searched. Producer
controls calibrate full block residual identities and a local star predicate.
"""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import json
import platform
import random
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
def need(ok,msg):
    if not ok:raise ValueError(msg)
def h(p):return sha256(Path(p).read_bytes()).hexdigest()
def save(p,obj):
    with p.open('x',encoding='utf-8',newline='\n')as f:json.dump(obj,f,indent=2);f.write('\n')
def tr(a):return list(map(list,zip(*a)))
def mm(a,b):
    bt=tr(b)
    return [[sum(x*y for x,y in zip(row,col))for col in bt]for row in a]
def add(*terms):return [[sum(w*a[i][j]for w,a in terms)for j in range(len(terms[0][1][0]))]for i in range(len(terms[0][1]))]
def eye(n):return [[int(i==j)for j in range(n)]for i in range(n)]
def ones(r,c):return [[1]*c for _ in range(r)]
def symmetric_binary(a):
    n=len(a);return all(len(r)==n for r in a)and all(type(v)is int and v in(0,1)for r in a for v in r)and all(a[i][i]==0 for i in range(n))and all(a[i][j]==a[j][i]for i in range(n)for j in range(n))
def cubic_core(m,matchings,p):
    need(m>0 and m%2==0,'positive even cell size')
    need(all(len(q)==m and sorted(q)==list(range(m))and all(q[i]!=i and q[q[i]]==i for i in range(m))for q in matchings),'three matchings')
    need(len(matchings)==3 and sorted(p)==list(range(m)),'core inputs')
    c=[[0]*(3*m)for _ in range(3*m)]
    def edge(i,j):c[i][j]=c[j][i]=1
    for g in range(3):
        for i in range(m):edge(g*m+i,g*m+matchings[g][i])
    for i in range(m):edge(i,m+i);edge(i,2*m+i);edge(m+i,2*m+p[i])
    r=[[int(i//m==j)for j in range(3)]for i in range(3*m)]
    return c,r
def assemble(c,r,f,d):
    s=len(c);b=len(d);n=3+s+b;a=[[0]*n for _ in range(n)]
    for i,j in combinations(range(3),2):a[i][j]=a[j][i]=1
    for i in range(s):
        for j in range(3):a[3+i][j]=a[j][3+i]=r[i][j]
        for j in range(s):a[3+i][3+j]=c[i][j]
        for j in range(b):a[3+i][3+s+j]=a[3+s+j][3+i]=f[i][j]
    for i in range(b):
        for j in range(b):a[3+s+i][3+s+j]=d[i][j]
    return a
def residual(a,k):return add((1,mm(a,a)),(-(k-2),eye(len(a))),(1,a),(-2,ones(len(a),len(a))))
def expected_blocks(c,r,f,d,k):
    s=len(c);b=len(d);n=3+s+b
    ans=[[0]*n for _ in range(n)]
    K=add((k-2,eye(s)),(-1,c),(-1,mm(c,c)),(2,ones(s,s)),(-1,mm(r,tr(r))))
    xx=add((1,mm(f,tr(f))),(-1,K))
    ty=add((1,mm(tr(r),f)),(-2,ones(3,b)))
    xy=add((1,mm(c,f)),(1,mm(f,d)),(1,f),(-2,ones(s,b)))
    yy=add((1,mm(d,d)),(1,mm(tr(f),f)),(-(k-2),eye(b)),(1,d),(-2,ones(b,b)))
    for i in range(s):
        for j in range(s):ans[3+i][3+j]=xx[i][j]
    for i in range(3):
        for j in range(b):ans[i][3+s+j]=ans[3+s+j][i]=ty[i][j]
    for i in range(s):
        for j in range(b):ans[3+i][3+s+j]=ans[3+s+j][3+i]=xy[i][j]
    for i in range(b):
        for j in range(b):ans[3+s+i][3+s+j]=yy[i][j]
    return ans
def star_data(c,f,degree):
    s=len(c);b=len(f[0]);cf=mm(c,f);overlap=mm(tr(f),f)
    H=[[2-f[i][y]-cf[i][y]for y in range(b)]for i in range(s)]
    negatives=[(i,y,H[i][y])for i in range(s)for y in range(b)if H[i][y]<0]
    excessive=[(y,z,overlap[y][z])for y,z in combinations(range(b),2)if overlap[y][z]>2]
    allowed=[[]for _ in range(b)]
    for y,z in combinations(range(b),2):
        if overlap[y][z]<=1 and all(f[i][z]<=H[i][y]and f[i][y]<=H[i][z]for i in range(s)):
            allowed[y].append(z);allowed[z].append(y)
    shortages=[dict(vertex=y,allowed=len(allowed[y]),required=degree)for y in range(b)if len(allowed[y])<degree]
    coordinate_shortages=[dict(vertex=y,coordinate=i,available=sum(f[i][z]for z in allowed[y]),required=H[i][y])
                          for y in range(b)for i in range(s)if sum(f[i][z]for z in allowed[y])<H[i][y]]
    return dict(H=H,column_overlaps=overlap,allowed_edges_by_vertex=allowed,negative_deficits=negatives,
                excessive_overlaps=excessive,degree_shortages=shortages,coordinate_shortages=coordinate_shortages,
                rejection_found=bool(negatives or excessive or shortages or coordinate_shortages))
def star_pass(data,f,y,neighbors,degree):
    selected=set(neighbors)
    return (len(selected)==degree and y not in selected and selected<=set(data['allowed_edges_by_vertex'][y])
            and all(sum(f[i][z]for z in selected)==data['H'][i][y]for i in range(len(f)))
            and all(data['column_overlaps'][z][w]<=1 for z,w in combinations(selected,2)))
def direct_star(c,f,y,neighbors,degree):
    # Independent literal partial known-edge graph for the generic local star test.
    s=len(c);b=len(f[0]);n=s+b;a=[[0]*n for _ in range(n)]
    for i in range(s):
        for j in range(s):a[i][j]=c[i][j]
        for z in range(b):a[i][s+z]=a[s+z][i]=f[i][z]
    for z in neighbors:a[s+y][s+z]=a[s+z][s+y]=1
    if len(set(neighbors))!=degree or y in neighbors:return False
    if any(sum(a[i][k]*a[j][k]for k in range(n))+a[i][j]>2 for i,j in combinations(range(n),2)):return False
    return all(sum(a[i][k]*a[s+y][k]for k in range(n))+a[i][s+y]==2 for i in range(s))
def analyze_factor(f):
    """Future fixed-shift6 factor API; returns exact cheap rejections only.

    Input is literal36x60 F. A no-rejection result is not feasibility. No
    row enumeration, SAT call or residual graph construction is performed.
    """
    need(len(f)==36 and all(len(row)==60 for row in f),'factor shape')
    need(all(type(x)is int and x in(0,1)for row in f for x in row),'binary factor')
    standard=[i^1 for i in range(12)];c,r=cubic_core(12,[standard]*3,[(i+6)%12 for i in range(12)])
    need(all(sum(row)==10 for row in f),'factor row10')
    need(all(sum(f[12*g+i][y]for i in range(12))==2 for g in range(3)for y in range(60)),'two per fiber per column')
    K=add((12,eye(36)),(-1,c),(-1,mm(c,c)),(2,ones(36,36)),(-1,mm(r,tr(r))))
    need(mm(f,tr(f))==K,'exact prescribed factor Gram')
    return star_data(c,f,8)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True);args=ap.parse_args();out=ROOT/args.out;out.mkdir(parents=True,exist_ok=False)
    inputs={p:h(ROOT/p)for p in [Path(__file__).relative_to(ROOT).as_posix(),'docs/DERIVATION_20260930_TRIANGLE_RESIDUAL60.md','uv.lock','pyproject.toml']}
    save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
         command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=inputs,random_seed=2026093003,
         scope='Conditional preparation only: no target factor available and no expensive search.',
         criteria='Literal full block residual identities and small valid/corrupted controls; candidate theorem pending independent review.'))
    # Generic exact coefficient controls need not satisfy the target identity.
    # They assert equality of full matrix residuals to the derived six blocks.
    rng=random.Random(2026093003);records=[]
    for m,b in [(2,1),(4,7),(6,12),(12,60)]:
        ms=[]
        for _ in range(3):
            order=list(range(m));rng.shuffle(order);q=[0]*m
            for x,y in zip(order[::2],order[1::2]):q[x]=y;q[y]=x
            ms.append(q)
        p=list(range(m));rng.shuffle(p);c,r=cubic_core(m,ms,p)
        f=[[rng.randrange(2)for _ in range(b)]for _ in range(3*m)];d=[[0]*b for _ in range(b)]
        for i,j in combinations(range(b),2):d[i][j]=d[j][i]=rng.randrange(2)
        a=assemble(c,r,f,d);actual=residual(a,m+2);expected=expected_blocks(c,r,f,d,m+2)
        need(actual==expected,'complete block polynomial identity')
        save(out/f'block_control_m{m:02d}.json',dict(m=m,b=b,matchings=ms,permutation=p,C=c,R=r,F=f,D=d,
                                                  complete_adjacency=a,complete_residual=actual,identity_pass=True))
        records.append(dict(m=m,b=b,vertices=len(a),matrix_entries=len(a)**2))
    # A known-valid SRG(9,4,1,2) validates the actual triangle core specialization.
    c,r=cubic_core(2,[[1,0]]*3,[0,1]);rook_core=assemble(c,r,[[]for _ in range(6)],[])
    need(symmetric_binary(rook_core)and all(sum(row)==4 for row in rook_core),'rook valid geometry')
    need(all(x==0 for row in residual(rook_core,4)for x in row),'known-valid rook target identity')
    bad=[row[:]for row in rook_core];bad[3][5]=bad[5][3]=0
    need(any(x!=0 for row in residual(bad,4)for x in row),'corrupt rook identity rejection')
    # A different rook bipartition gives a nonempty3-vertex residual for the
    # generic local-star test; it is explicitly not a target36x60 factor.
    rook=[[int(i!=j and(i//3==j//3 or i%3==j%3))for j in range(9)]for i in range(9)]
    X=list(range(3,9));Y=[0,1,2];c=[[rook[x][z]for z in X]for x in X];f=[[rook[x][y]for y in Y]for x in X]
    sd=star_data(c,f,2);need(not sd['rejection_found'],'rook residual cheap screen positive')
    stars=[]
    for y in range(3):
        for count in range(3):
            for selected in combinations([z for z in range(3)if z!=y],count):
                local=star_pass(sd,f,y,selected,2);literal=direct_star(c,f,y,selected,2)
                need(local==literal,'generic local-star full adjacency equivalence control')
                stars.append(dict(center=y,neighbors=list(selected),accepted=local))
    need(sum(r['accepted']for r in stars)==3,'three positive residual stars')
    bad=json.loads(json.dumps(sd));bad['H'][0][0]+=1
    need(not star_pass(bad,f,0,[1,2],2),'wrong deficit corruption')
    bad=json.loads(json.dumps(sd));bad['allowed_edges_by_vertex'][0].remove(1)
    need(not star_pass(bad,f,0,[1,2],2),'missing allowed edge corruption')
    bad=json.loads(json.dumps(sd));bad['column_overlaps'][1][2]=2
    need(not star_pass(bad,f,0,[1,2],2),'co-neighbor overlap corruption')
    save(out/'generic_star_controls.json',dict(core=c,F=f,derived=sd,complete_star_subsets=stars,
                                              note='Known-valid rook9 bipartition; not a target36x60 incidence factor.'))
    # A sign error in the mixed block must change the complete polynomial residual.
    raw=json.loads((out/'block_control_m12.json').read_bytes());wrong=expected_blocks(raw['C'],raw['R'],raw['F'],raw['D'],14)
    wrong[3][39]+=2*mm(raw['C'],raw['F'])[0][0];wrong[39][3]=wrong[3][39]
    need(wrong!=raw['complete_residual'],'wrong mixed-sign negative')
    summary=dict(status='CANDIDATE_TRIANGLE_RESIDUAL60_EQUIVALENCE_AND_SCREEN',timestamp=datetime.now(timezone.utc).isoformat(),
        claim_id='C-TRIANGLE-FACTOR-RESIDUAL60-COMPLETION-EQUIVALENCE',claim_revision=1,kind='encoding',basis=['DERIVED','COMPUTED'],
        statement='For any specified triangle39core and binary36by60 factor F satisfying the exact factor Gram and two-neighbors-per-fiber column conditions, a symmetric binary zero-diagonal60by60 matrix D completes the99-vertex target if and only if FD=2J-F-CF and D^2+F^TF=12I-D+2J. Its degree8 condition is redundant but may be imposed explicitly.',
        scope='Conditional exact block equivalence for a supplied fully validated factor, without assuming a factor exists. No target automorphism or fixed-core containment premise.',
        independent_verification=None,independent_verification_null_reason='Producer derivation and controls; separate root review required.',
        actual_target_factor_available=False,actual_target_factor_null_reason='The preceding factor experiment has no validated SAT factor to supply.',
        actual_target_residual_search_performed=False,solver_calls=0,
        controls=dict(full_block_identities=records,known_valid_SRG9_triangle_control=True,
                      generic_rook_residual_star_subsets=len(stars),generic_rook_positive_stars=3,
                      corruptions_rejected=['deleted_rook_edge','mixed_block_sign','wrong_star_deficit','missing_allowed_edge','forbidden_co_neighbor_overlap']),
        next_cheap_action='On receipt of an independently validated factor, compute H and F^TF; reject negative deficits, overlaps>2, insufficient symmetric allowed-neighbor degrees or coordinate capacities. Then test each exact8-neighbor domain with forbidden overlap2 co-neighbor pairs, preserving complete certificates if any domain is empty.',
        inputs_sha256=inputs,target_resolution=False,
        limitations=['No factor or residual graph has been constructed or excluded here.',
                     'Nonempty individual row domains do not imply symmetric simultaneous feasibility.',
                     'The row-star relaxation does not include all D^2 equations; the full equivalence requires them.',
                     'Finite controls calibrate implementation, not universal quantification.'])
    summary['artifact_hashes']={p.relative_to(ROOT).as_posix():h(p)for p in sorted(out.iterdir())if p.is_file()}
    save(out/'summary.json',summary);print(json.dumps({'status':summary['status'],'summary_sha256':h(out/'summary.json')}))

if __name__=='__main__':main()
