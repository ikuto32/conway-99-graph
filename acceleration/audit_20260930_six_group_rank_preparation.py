"""Independent exact finite preparation for the pending six-group producer review."""
import argparse, hashlib, json, platform, subprocess, sys, time
from collections import Counter
from datetime import datetime,timezone
from itertools import combinations,product
from math import gcd
from pathlib import Path
from tqdm import tqdm
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results';RAW=B/'20260930_hadamard20_support/six_prism.json'
HASH='ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d'
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def write(p,x):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,separators=(',',':'));f.write('\n')
def det(m):
    a=[r[:] for r in m];n=len(a);prev=1;sign=1
    if n==0:return 1
    for k in range(n-1):
        row=next((i for i in range(k,n) if a[i][k]),None)
        if row is None:return 0
        if row!=k:a[k],a[row]=a[row],a[k];sign=-sign
        p=a[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                v=a[i][j]*p-a[i][k]*a[k][j];need(v%prev==0,'Bareiss exact division');a[i][j]=v//prev
            a[i][k]=0
        prev=p
    return sign*a[-1][-1]
def minor(m,rows,cols):return [[m[i][j] for j in cols] for i in rows]
def primitive(v):
    g=gcd(*v);need(g!=0,'nonzero kernel');v=[x//g for x in v]
    return v if next(x for x in v if x)>0 else [-x for x in v]
def classify(H):
    n=6;G=[[sum(row[i]*row[j] for row in H) for j in range(n)] for i in range(n)];d=det(G)
    if d:return dict(rank=6,Gram_determinant=d,basis=list(range(6)),kernel=[])
    for rank in [5,4]:
        for S in combinations(range(n),rank):
            A=minor(G,S,S);d=det(A)
            if not d:continue
            free=[f for f in range(n) if f not in S];kernel=[]
            for f in free:
                # Cramer's rule for the independent Gram columns, checked on H.
                v=[0]*n;v[f]=d
                for j,pos in enumerate(S):
                    replaced=[r[:] for r in A]
                    for i,ri in enumerate(S):replaced[i][j]=G[ri][f]
                    v[pos]=-det(replaced)
                v=primitive(v);need(all(sum(a*b for a,b in zip(row,v))==0 for row in H),'literal independent kernel')
                kernel.append(v)
            return dict(rank=rank,Gram_principal_basis=list(S),Gram_principal_determinant=d,kernel=kernel)
    raise ValueError('six distinct binary points cannot have augmented rank below4')
def controls():
    checked=0;hist=Counter()
    for c in product([-3,-2,-1,1,2,3],repeat=6):
        if sum(c)!=0 or gcd(*c)!=1:continue
        allowed=[z for z in product(range(-2,3),repeat=3) if sum(z)==0 and all(-1<=a*b<=2 for a in c for b in z)]
        if max(map(abs,c))>=2:need(allowed==[(0,0,0)],'primitive large-coefficient integer obstruction')
        else:need(len(allowed)==7,'sign-only line admits six nonzero coefficient triples')
        checked+=1;hist[max(map(abs,c))]+=1
    cube=list(product([0,1],repeat=3));ranks=Counter()
    for subset in combinations(cube,6):
        H=[[1]*6]+list(map(list,zip(*subset)));rank=classify(H)['rank'];need(rank==4,'six3cube vertices have rank4');ranks[rank]+=1
    need(sum(ranks.values())==28,'all3cube sextets')
    return dict(primitive_full_support_six_coefficients_checked=checked,coefficient_maximum_histogram=dict(hist),six_point_cube_controls=dict(ranks))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',required=True,type=Path);a=ap.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.perf_counter()
    try:
        need(sha(RAW)==HASH,'raw support pin');raw=json.loads(RAW.read_bytes());groups=list(dict.fromkeys(tuple(i for i in range(12) if raw['L'][i][d]) for d in range(60)))
        pair_counts=[dict(pair=list(p),groups=[g for g,s in enumerate(groups) if set(p)<=set(s)]) for p in combinations(range(12),2)]
        need(Counter(len(r['groups']) for r in pair_counts)=={0:6,5:60},'no coordinate pair lies in six groups')
        ctrl=controls();write(out/'controls.json',ctrl);records=[];counts=Counter()
        for ids in tqdm(list(combinations(range(20),6)),desc='Independent six-subset Gram ranks',mininterval=1):
            H=[[1]*6]+[[int(a in groups[g]) for g in ids] for a in range(12)];c=classify(H);common=sorted(set.intersection(*(set(groups[g]) for g in ids)))
            need(len(common)<=1,'six-way intersection at most1')
            if c['rank']==6:category='full_rank'
            elif c['rank']==4:category='retained_kernel_dimension_two'
            else:
                v=c['kernel'][0]
                if not all(v):category='kernel_has_zero'
                elif max(map(abs,v))>1:category='kernel_has_large_coefficient'
                else:category='sign_kernel_common_intersection_shortage'
            counts[(c['rank'],category)]+=1;records.append(dict(groups=list(ids),common_support=common,category=category,**c));need(time.perf_counter()-start<120,'audit preparation allocation')
        write(out/'records.json',dict(records=records,complete_population=38760));write(out/'pair_multiplicities.json',pair_counts)
        inputs={p.resolve().relative_to(ROOT).as_posix():sha(p) for p in [RAW,Path(__file__),ROOT/'uv.lock',ROOT/'pyproject.toml']}
        summary=dict(status='INDEPENDENT_SIX_GROUP_RANK_PREPARATION_ONLY',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=inputs,outputs_sha256={p.relative_to(ROOT).as_posix():sha(p) for p in out.iterdir() if p.is_file()},counts=[dict(rank=r,category=c,count=n) for (r,c),n in sorted(counts.items())],elapsed_seconds=time.perf_counter()-start,solver_calls=0,scope='Independent raw computation pending comparison with frozen producer artifacts and complete review binding; not a producer-claim approval.')
        write(out/'summary.json',summary);print(json.dumps(dict(status=summary['status'],counts=summary['counts'],summary_sha256=sha(out/'summary.json'),elapsed_seconds=summary['elapsed_seconds'])))
    except BaseException as e:write(out/'failure.json',dict(error=repr(e)));raise
if __name__=='__main__':main()
