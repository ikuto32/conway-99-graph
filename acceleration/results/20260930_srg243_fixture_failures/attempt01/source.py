"""Exact ternary syndrome SRG243 and nonempty triangle/residual fixture producer."""
from datetime import datetime,timezone
from itertools import combinations,product
from pathlib import Path
import argparse
import hashlib
import json
import platform
import subprocess
import sys
import time
from tqdm import tqdm

ROOT=Path(__file__).resolve().parents[1]

def need(condition,message):
    if not condition:raise ValueError(message)
def save(p,data):
    with p.open('x',encoding='utf-8')as f:json.dump(data,f,indent=2);f.write('\n')
def sha(p):
    with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def relative(p):return p.resolve().relative_to(ROOT).as_posix()

def polynomial_division(f,g):
    remainder=[x%3 for x in f];quotient=[0]*max(1,len(f)-len(g)+1)
    need(g[-1]==1,'monic divisor')
    for i in range(len(remainder)-1,len(g)-2,-1):
        coefficient=remainder[i];position=i-len(g)+1;quotient[position]=coefficient
        for j,value in enumerate(g):remainder[position+j]=(remainder[position+j]-coefficient*value)%3
    return quotient,remainder[:len(g)-1]

def syndromes(g):
    result=[]
    for i in range(11):
        f=[0]*max(6,i+1);f[i]=1
        _,r=polynomial_division(f,g);result.append(r)
    return result

def error_syndromes(s):
    records=[dict(error=[],syndrome=[0]*5)]
    for i in range(11):
        for value in(1,2):records.append(dict(error=[[i,value]],syndrome=[value*x%3 for x in s[i]]))
    for i,j in combinations(range(11),2):
        for a,b in product((1,2),repeat=2):records.append(dict(error=[[i,a],[j,b]],syndrome=[(a*x+b*y)%3 for x,y in zip(s[i],s[j])]))
    return records

def srg_check(a,n,k):
    need(len(a)==n and all(len(r)==n and all(type(x)is int and x in(0,1)for x in r)for r in a),'literal binary square shape')
    need(all(a[i][i]==0 and sum(a[i])==k for i in range(n)),'zero diagonal and degree')
    need(all(a[i][j]==a[j][i]for i,j in combinations(range(n),2)),'symmetry')
    masks=[sum(x<<j for j,x in enumerate(row))for row in a]
    for i in range(n):
        for j in range(n):need((masks[i]&masks[j]).bit_count()==(k-2)*int(i==j)-a[i][j]+2,'exact integer SRG square')
    return dict(vertices=n,degree=k,lambda_value=1,mu=2,ordered_square_entries=n*n,symmetry_pairs=n*(n-1)//2,arithmetic='Python integer bitset intersections')

def calibrate():
    rook=[[int(i!=j and(i//3==j//3 or i%3==j%3))for j in range(9)]for i in range(9)]
    positive=srg_check(rook,9,4);rejected=[]
    for label in ['edge_deletion','one_sided_edge','loop','Boolean_entry','wrong_degree']:
        bad=[r[:]for r in rook]
        if label=='edge_deletion':bad[0][1]=bad[1][0]=0
        elif label=='one_sided_edge':bad[0][1]=0
        elif label=='loop':bad[0][0]=1
        elif label=='Boolean_entry':bad[0][0]=False
        try:srg_check(bad,9,5 if label=='wrong_degree'else4)
        except ValueError:rejected.append(label)
        else:raise ValueError('corruption accepted '+label)
    return dict(positive=positive,corrupted_controls_rejected=rejected)

def extract(a):
    edge=next((i,j)for i,j in combinations(range(len(a)),2)if a[i][j])
    common=[r for r in range(len(a))if a[edge[0]][r]and a[edge[1]][r]]
    need(len(common)==1,'unique root triangle');triangle=[*edge,common[0]]
    fibres=[[r for r in range(len(a))if r not in triangle and a[t][r]]for t in triangle]
    need([len(x)for x in fibres]==[20]*3 and len(set(sum(fibres,[])))==60,'three disjoint20fibres')
    matching0=[(u,v)for u,v in combinations(fibres[0],2)if a[u][v]]
    need(len(matching0)==10 and len(set(sum(([u,v]for u,v in matching0),[])))==20,'first perfect matching')
    fibres[0]=sum(([u,v]for u,v in matching0),[])
    for g in(1,2):
        reordered=[]
        for u in fibres[0]:
            possible=[v for v in fibres[g]if a[u][v]];need(len(possible)==1,'cross perfect matching');reordered.append(possible[0])
        need(len(set(reordered))==20,'cross matching bijection');fibres[g]=reordered
    fixed=triangle+sum(fibres,[]);outside=sorted(set(range(len(a)))-set(fixed))
    labels=[list(p)for p in combinations(range(20),2)if p[1]!=(p[0]^1)]
    mapping={}
    for y in outside:
        pair=tuple(i for i,u in enumerate(fibres[0])if a[u][y]);need(len(pair)==2 and pair not in mapping,'unique two-row C0 support');mapping[pair]=y
    need(set(mapping)==set(map(tuple,labels))and len(outside)==180,'canonical all180nonmatching pairs')
    outside=[mapping[tuple(p)]for p in labels];order=fixed+outside
    need(len(set(order))==243,'full relabelling bijection')
    core=[[a[u][v]for v in fixed]for u in fixed]
    c=[row[3:]for row in core[3:]]
    f=[[a[u][v]for v in outside]for u in sum(fibres,[])]
    d=[[a[u][v]for v in outside]for u in outside]
    need(all(sum(row)==18 for row in f),'factor row weight18')
    need(all(sum(f[r][j]for r in range(20*g,20*g+20))==2 for g in range(3)for j in range(180)),'two per cell')
    need(all(sum(row)==16 for row in d),'residual degree16')
    fmasks=[sum(x<<j for j,x in enumerate(row))for row in f]
    dmasks=[sum(x<<j for j,x in enumerate(row))for row in d]
    cols=[sum(f[r][j]<<r for r in range(60))for j in range(180)]
    for r in range(60):
        for s in range(60):
            need((fmasks[r]&fmasks[s]).bit_count()==20*int(r==s)-core[r+3][s+3]+2-sum(core[r+3][z]*core[s+3][z]for z in range(63)),'factor Gram block')
        for j in range(180):need((fmasks[r]&dmasks[j]).bit_count()==2-f[r][j]-sum(c[r][s]*f[s][j]for s in range(60)),'mixed residual equation')
    for i in range(180):
        for j in range(180):need((dmasks[i]&dmasks[j]).bit_count()+(cols[i]&cols[j]).bit_count()==20*int(i==j)-d[i][j]+2,'residual square equation')
    matchings=[]
    for g in range(3):
        matchings.append([next(j for j in range(20)if core[3+20*g+i][3+20*g+j])for i in range(20)])
    cross12=[next(j for j in range(20)if core[23+i][43+j])for i in range(20)]
    return dict(label='CANDIDATE_SRG243_NONEMPTY_RESIDUAL_POSITIVE_CONTROL_NOT_CONWAY99',parameters=dict(v=243,k=22,lambda_value=1,mu=2),
      original_triangle=triangle,original_fibres=fibres,original_outside_vertices=outside,canonical_order_original_vertex_ids=order,
      canonical_C0_pairs=labels,core_adjacency63=core,cubic_core60=c,internal_matchings=matchings,cross01=list(range(20)),cross02=list(range(20)),cross12=cross12,
      factor60x180=f,residual180x180=d,producer_checks=dict(factor_Gram_entries=3600,mixed_equation_entries=10800,residual_equation_entries=32400,residual_degree=16,factor_row_weight=18,cell_column_weight=2),
      target99_graph=False,independent_approval=False)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    out=args.out.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    inputs=[Path(__file__),Path(__file__).with_name('theory_20260930_srg243_residual_fixture_spec.md'),ROOT/'uv.lock',ROOT/'pyproject.toml']
    save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],working_directory=str(ROOT),python=platform.python_version(),uv=subprocess.check_output(['uv','--version'],text=True).strip(),inputs_sha256={relative(p):sha(p)for p in inputs},
      question='Construct a nonempty triangle/residual positive-control fixture at(243,22,1,2).',selection='All243monic degree5GF3polynomials, first exact divisor with injective243weight<=2syndromes.',limits=dict(seconds=120,solver_calls=0),seed=None,seed_null_reason='Deterministic exact enumeration.',scope='Validation fixture only, not a Conway99candidate or novelty claim.',independent_approval=False))
    save(out/'controls.json',calibrate())
    divs=[];selected=None
    for coefficients in tqdm(list(product(range(3),repeat=5)),desc='monic GF3 degree5 polynomials'):
        need(time.monotonic()-start<120,'120-second cap')
        g=[*coefficients,1];q,r=polynomial_division([2]+[0]*10+[1],g)
        if any(r):continue
        s=syndromes(g);errors=error_syndromes(s);unique=len({tuple(e['syndrome'])for e in errors})
        divs.append(dict(coefficients_low_to_high=g,quotient_low_to_high=q,weight_le2_count=len(errors),distinct_syndromes=unique))
        if unique==243 and selected is None:selected=(g,s,errors)
    need(selected is not None,'no qualifying polynomial');g,s,errors=selected
    save(out/'polynomial_census.json',dict(enumerated_monic_polynomials=243,divisors=divs,selected_polynomial=g,selection='First qualifying coefficient tuple in lexicographic low-to-high order.'))
    save(out/'syndrome_certificate.json',dict(polynomial_low_to_high=g,coordinate_syndromes=s,all_weight_le2_errors=errors,vector_encoding='Base3 integer with coordinate0 least significant.'))
    points=[[(number//3**i)%3 for i in range(5)]for number in range(243)]
    differences={tuple(value*x%3 for x in syndrome)for syndrome in s for value in(1,2)}
    need(len(differences)==22 and(0,0,0,0,0)not in differences,'22nonzero differences')
    a=[[int(tuple((y-x)%3 for x,y in zip(u,v))in differences)for v in points]for u in points]
    checks=srg_check(a,243,22)
    save(out/'adjacency243.json',dict(label='CANDIDATE_POSITIVE_CONTROL_ONLY_NOT_CONWAY99',parameters=dict(v=243,k=22,lambda_value=1,mu=2),vertex_vectors=points,adjacency=a,producer_exact_checks=checks,independent_approval=False))
    save(out/'triangle_blocks.json',extract(a))
    need(time.monotonic()-start<120,'120-second cap')
    save(out/'summary.json',dict(status='CANDIDATE_SRG243_NONEMPTY_RESIDUAL_FIXTURE',parameters=[243,22,1,2],selected_polynomial=g,exact_producer_graph_check=checks,factor_dimensions=[60,180],residual_dimensions=[180,180],independent_approval=False,target99_resolution=False,novelty_claimed=False,elapsed_seconds=time.monotonic()-start,
      artifact_hashes={relative(p):sha(p)for p in out.iterdir()if p.is_file()},limitations=['Positive-control family only, not target evidence.','Producer checks are not independent approval.','The243residual coefficient20 anddegree16 are distinct from Conway99coefficient12 anddegree8.']))
    print(json.dumps(dict(status='CANDIDATE_SRG243_NONEMPTY_RESIDUAL_FIXTURE',polynomial=g,elapsed_seconds=time.monotonic()-start)))

if __name__=='__main__':main()
