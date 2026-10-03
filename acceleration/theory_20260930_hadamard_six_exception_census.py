"""Producer complete six-subset exact rank and necessary-kernel census."""
from collections import Counter
from datetime import datetime, timezone
from fractions import Fraction
from functools import reduce
from itertools import combinations, product
from math import comb,gcd,lcm
from pathlib import Path
import argparse,gzip,hashlib,json,platform,subprocess,sys,time
from tqdm import tqdm
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'acceleration/results'
RAW=B/'20260930_hadamard20_support/six_prism.json'
MARGINAL=B/'20260930_independent_review/hadamard_few_exception_marginals/summary.json'
PINS={RAW:'ea8b3356fb9790a60bdc57442339099b1052b2a9a1ca95f7f146f71598059b9d',MARGINAL:'6b9512567a77ef3bad2fbb1b581fadb30c486c9ac4151543001705776e0c5df9'}
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
def primitive(v):
    den=lcm(*(x.denominator for x in v));z=[int(x*den) for x in v];div=reduce(gcd,map(abs,z));need(div>0,'nonzero vector');z=[x//div for x in z]
    if next(x for x in z if x)<0:z=[-x for x in z]
    return z
def det(a):
    n=len(a)
    if n==0:return 1
    a=[r[:] for r in a];old=1;sign=1
    for k in range(n-1):
        row=next((r for r in range(k,n) if a[r][k]),None)
        if row is None:return 0
        if row!=k:a[k],a[row]=a[row],a[k];sign=-sign
        pivot=a[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                value=a[i][j]*pivot-a[i][k]*a[k][j];need(value%old==0,'Bareiss exact division');a[i][j]=value//old
        for i in range(k+1,n):a[i][k]=0
        old=pivot
    return sign*a[-1][-1]
def certificate(a):
    n=len(a[0]);basis={};rows=[]
    for i,row in enumerate(a):
        v=list(map(Fraction,row))
        for p,b in sorted(basis.items()):
            if v[p]:
                c=v[p];v=[x-c*y for x,y in zip(v,b)]
        if any(v):
            p=next(j for j,x in enumerate(v) if x);c=v[p];basis[p]=[x/c for x in v];rows.append(i)
    pivots=sorted(basis);free=[i for i in range(n) if i not in basis];null=[]
    for f in free:
        v=[Fraction(0)]*n;v[f]=1
        for p in reversed(pivots):v[p]=-sum(basis[p][j]*v[j] for j in range(p+1,n))
        z=primitive(v);need(all(sum(x*y for x,y in zip(row,z))==0 for row in a),'literal integer null vector');null.append(z)
    minor=[[a[i][j] for j in pivots] for i in rows];d=det(minor);need(d!=0,'rank lower minor')
    return dict(rank=len(pivots),minor_rows=rows,minor_columns=pivots,minor=minor,determinant=d,free_columns=free,integer_null_basis=null)
def egcd(a,b):
    oldr,r=a,b;olds,s=1,0;oldt,t=0,1
    while r:
        q=oldr//r;oldr,r=r,oldr-q*r;olds,s=s,olds-q*s;oldt,t=t,oldt-q*t
    if oldr<0:return -oldr,-olds,-oldt
    return oldr,olds,oldt
def bezout(c):
    total=0;coeff=[0]*len(c)
    for i,x in enumerate(c):
        d,u,v=egcd(total,x);coeff=[u*y for y in coeff];coeff[i]+=v;total=d
    need(total==1 and sum(x*y for x,y in zip(c,coeff))==1,'primitive Bezout identity');return coeff
def classify(cert,common):
    if cert['rank']==6:return 'EXCLUDED_FULL_COLUMN_RANK'
    if cert['rank']<5:return 'RETAINED_KERNEL_DIMENSION_AT_LEAST_TWO'
    c=cert['integer_null_basis'][0]
    if any(x==0 for x in c):return 'EXCLUDED_ZERO_KERNEL_COORDINATE'
    if max(map(abs,c))>=2:return 'EXCLUDED_INTEGER_COEFFICIENT_MAGNITUDE'
    need(sorted(c)==[-1,-1,-1,1,1,1],'full-support sign balance')
    if len(common)<2:return 'EXCLUDED_COMMON_SUPPORT_AT_MOST_ONE'
    return 'RETAINED_FULL_SIGN_KERNEL_COMMON_SUPPORT'
def controls():
    for entries in product(range(2),repeat=9):
        a=[list(entries[3*i:3*i+3]) for i in range(3)];cert=certificate(a)
        rank=0
        for k in (1,2,3):
            if any(det([[a[i][j] for j in cs] for i in rs]) for rs in combinations(range(3),k) for cs in combinations(range(3),k)):rank=k
        need(cert['rank']==rank,'exhaustive tiny minor rank')
    cycle=[[1]*6]+[[int(v in (e,(e+1)%6)) for e in range(6)] for v in range(6)];cc=certificate(cycle);need(cc['rank']==5 and set(cc['integer_null_basis'][0])=={-1,1},'cycle full sign kernel')
    columns=[(0,0,0,0),*(tuple(int(i==j) for i in range(4)) for j in range(4)),(1,1,1,1)]
    simplex=[[1]*6]+[[x[j] for x in columns] for j in range(4)];sc=certificate(simplex);need(sc['rank']==5 and max(map(abs,sc['integer_null_basis'][0]))==3,'large primitive coefficient control')
    rectcols=[(0,0,0,0),(1,0,0,0),(0,1,0,0),(1,1,0,0),(0,0,1,0),(0,0,0,1)];rect=[[1]*6]+[[x[j] for x in rectcols] for j in range(4)];rc=certificate(rect);need(rc['rank']==5 and rc['integer_null_basis'][0].count(0)==2,'zero kernel coordinates')
    cubecols=list(product(range(2),repeat=3))[:6];cube=[[1]*6]+[[x[j] for x in cubecols] for j in range(3)];kc=certificate(cube);need(kc['rank']==4 and classify(kc,[])=='RETAINED_KERNEL_DIMENSION_AT_LEAST_TWO','rank4 retained')
    c=cc['integer_null_basis'][0];b=bezout(c);need(sum(x*y for x,y in zip(c,[b[0]+1,*b[1:]]))!=1,'corrupt Bezout rejected');bad=c.copy();bad[0]+=1;need(any(sum(x*y for x,y in zip(row,bad)) for row in cycle),'corrupt null vector rejected');need(det(cc['minor'])!=cc['determinant']+1,'corrupt determinant rejected')
    for coefficient in (2,-2,3,-3):
        allowed=[z for z in product(range(-3,4),repeat=3) if sum(z)==0 and all(coefficient*x>=-1 for x in z)];need(allowed==[(0,0,0)],'integer one-sided zero obstruction')
    need(all(-1<=x*y<=2 for x in c for y in (-1,0,1)),'full sign count-shape positive')
    return dict(exhaustive_binary3x3_matrices=512,cycle=cc,large_coefficient=sc,zero_coordinates=rc,rank4=kc,primitive_Bezout=b,rejected_controls=['changed_Bezout','changed_null_vector','changed_minor_determinant'],scope='Synthetic matrix/count controls only; no full research factor.')
def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True,type=Path);args=p.parse_args();out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    try:
        for path,digest in PINS.items():need(sha(path)==digest,'pin '+key(path))
        inputs={key(path):digest for path,digest in PINS.items()}
        for path in [Path(__file__),Path(__file__).with_name('theory_20260930_hadamard_six_exception_census_spec.md'),ROOT/'uv.lock',ROOT/'pyproject.toml']:inputs[key(path)]=sha(path)
        save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=inputs,limits=dict(seconds=120,native_solver_calls=0),population=comb(20,6)))
        save(out/'controls.json',controls());raw=json.loads(RAW.read_bytes());groups=list(dict.fromkeys(tuple(a for a in range(12) if raw['L'][a][d]) for d in range(60)));need(len(groups)==20 and comb(len(groups),6)==38760,'complete subset denominator')
        H=[[1]*20]+[[int(a in g) for g in groups] for a in range(12)];save(out/'global_marginal_matrix.json',dict(groups=groups,matrix=H,rows=['leading_one',*range(12)]))
        rank_counts=Counter();classes=Counter();remaining=[];completed=0
        with (out/'all_subsets.jsonl.gz').open('xb') as rawstream:
            with gzip.GzipFile(filename='',mode='wb',fileobj=rawstream,mtime=0) as stream:
                for ids in tqdm(combinations(range(20),6),total=38760,desc='Six-exception exact ranks',mininterval=1):
                    matrix=[[row[g] for g in ids] for row in H];cert=certificate(matrix);common=sorted(set.intersection(*(set(groups[g]) for g in ids)));category=classify(cert,common)
                    record=dict(index=completed,groups=list(ids),certificate=cert,common_support=common,classification=category)
                    if cert['rank']==5:record['primitive_Bezout']=bezout(cert['integer_null_basis'][0])
                    stream.write((json.dumps(record,separators=(',',':'))+'\n').encode());rank_counts[cert['rank']]+=1;classes[category]+=1
                    if category.startswith('RETAINED'):remaining.append(record)
                    completed+=1
                    if completed%1000==0:
                        with (out/'progress.jsonl').open('a',encoding='utf-8',newline='\n') as f:f.write(json.dumps(dict(completed=completed,last_subset=ids,elapsed_seconds=time.monotonic()-start))+'\n')
                        need(time.monotonic()-start<120,'bounded census allocation')
        need(completed==38760,'full exact population')
        save(out/'remaining_candidates.json',dict(records=remaining,count=len(remaining),scope='Necessary subsets only; every kernel-dimension2-or-more case retained without elimination.'))
        summary=dict(status='CANDIDATE_COMPLETE_SIX_EXCEPTION_MARGINAL_CENSUS',timestamp=datetime.now(timezone.utc).isoformat(),inputs_sha256=inputs,outputs_sha256={key(p):sha(p) for p in out.iterdir() if p.is_file()},subset_population=38760,completed=completed,rank_counts=dict(sorted(rank_counts.items())),class_counts=dict(sorted(classes.items())),remaining_necessary_subsets=len(remaining),independent_approval=False,native_solver_calls=0,target_resolution=False,elapsed_seconds=time.monotonic()-start,scope='Exactly six exceptional support groups on one fixedL; full-Gram necessary marginal constraints, no factor/target resolution.',artifact_availability='LOCAL_ONLY')
        save(out/'summary.json',summary);print(json.dumps({k:v for k,v in summary.items() if k not in ('inputs_sha256','outputs_sha256')}))
    except BaseException as e:save(out/'failure.json',dict(error=repr(e),source_sha256=sha(Path(__file__))));raise
if __name__=='__main__':main()
