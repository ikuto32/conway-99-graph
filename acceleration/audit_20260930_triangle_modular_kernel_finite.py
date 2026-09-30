"""Independent finite-field reconstruction/checking of the bounded failed route."""
from copy import deepcopy
from datetime import datetime,timezone
from hashlib import file_digest,sha256
from itertools import product
from pathlib import Path
import argparse
import json
import platform
import random
import subprocess
import sys
import time
from tqdm import tqdm

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'acceleration/results/20260930_triangle_modular_kernel/summary.json'
POST=ROOT/'acceleration/results/20260930_triangle_modular_kernel_controls/summary.json'
FIX=ROOT/'acceleration/results/20260930_srg243_residual_fixture/triangle_blocks.json'
FIX_GATE=ROOT/'acceleration/results/20260930_independent_review/srg243_residual_fixture/summary.json'
PROOF=ROOT/'docs/AUDIT_20260930_TRIANGLE_MODULAR_KERNEL_FINITE.md'
PINS={RUN:'70a7c9600ac6283f7593e93e91920024258fa527733e515a12a0e9d2a07b01ee',POST:'c3f17ead26ee9f0533f1dca8a58d651f39af67273a7e23522a33766302406f01',FIX:'3f8dfa3803d6a5db8146dd24a0857477e1aa061ab10dac0f9e6e564aabc86439',FIX_GATE:'28bbd97b8e69515c3eb0345e5aa2db12debfaa8a44e83b2e3487342104c5d50e'}

def need(b,s):
    if not b:raise ValueError(s)
def digest(p):
    with p.open('rb') as f:return file_digest(f,'sha256').hexdigest()
def key(p):return p.resolve().relative_to(ROOT).as_posix()
def read(p):return json.loads(p.read_bytes())
def save(p,x):
    with p.open('x',encoding='utf-8',newline='\n') as f:json.dump(x,f,indent=2);f.write('\n')
def array_hash(x):return sha256(json.dumps(x,separators=(',',':')).encode('ascii')).hexdigest()
def transpose(a):return [list(x) for x in zip(*a)]

def kernel(matrix,p):
    need(p in (2,3),'supported prime');need(matrix and len({len(r) for r in matrix})==1,'rectangular nonempty matrix')
    a=[[int(x)%p for x in r] for r in matrix];m=len(a);n=len(a[0]);pivot_columns=[];rank=0
    for col in range(n):
        choices=[r for r in range(rank,m) if a[r][col]]
        if not choices:continue
        chosen=choices[-1];a[rank],a[chosen]=a[chosen],a[rank]
        inverse=1 if a[rank][col]==1 else 2
        a[rank]=[(x*inverse)%p for x in a[rank]]
        for r in range(rank+1,m):
            coefficient=a[r][col]
            if coefficient:a[r]=[(x-coefficient*y)%p for x,y in zip(a[r],a[rank])]
        pivot_columns.append(col);rank+=1
        if rank==m:break
    free=[j for j in range(n) if j not in pivot_columns];basis=[]
    for j in free:
        v=[0]*n;v[j]=1
        for r in range(rank-1,-1,-1):
            col=pivot_columns[r];v[col]=-sum(a[r][k]*v[k] for k in range(col+1,n))%p
        basis.append(v)
    return basis,pivot_columns

def planes(rows,p):
    return [[sum(1<<i for i,x in enumerate(row) if x%p==value) for value in range(1,p)] for row in rows]
def dot(a,b,p):
    if p==2:return (a[0]&b[0]).bit_count()%2
    return ((a[0]&b[0]).bit_count()+2*(a[0]&b[1]).bit_count()+2*(a[1]&b[0]).bit_count()+(a[1]&b[1]).bit_count())%3

def direct_kernel(a,v,p):return all(sum(x*y for x,y in zip(row,v))%p==0 for row in a)

def calibration():
    result=[]
    for p in (2,3):
        vectors=list(product(range(p),repeat=3));false=0;count=0
        for entries in product(range(p),repeat=6):
            a=[entries[:3],entries[3:]];basis,pivots=kernel(a,p)
            brute={v for v in vectors if direct_kernel(a,v,p)}
            span={tuple(sum(t*x for t,x in zip(coef,column))%p for column in zip(*basis)) if basis else (0,0,0) for coef in product(range(p),repeat=len(basis))}
            need(brute==span and len(pivots)+len(basis)==3,'complete small kernel calibration')
            if any(entries):
                j=next(j for j in range(3) if any(row[j] for row in a));v=[0]*3;v[j]=1;need(not direct_kernel(a,v,p),'false unit kernel vector');false+=1
            count+=1
        result.append(dict(prime=p,all_two_by_three_matrices=count,each_kernel_checked_by_full_field_vector_enumeration=True,deliberately_false_kernel_vectors_rejected=false))
    return result

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();inputs={}
    for p,h in PINS.items():need(digest(p)==h,'input pin');inputs[key(p)]=h
    run=read(RUN);post=read(POST)
    for x in [run,post]:
        for p,h in x['inputs_sha256'].items():need(digest(ROOT/p)==h,'producer input identity');inputs[p]=h
    for p,h in run['outputs_sha256'].items():need(digest(ROOT/p)==h,'producer output identity');inputs[p]=h
    for p in [Path(__file__),PROOF,ROOT/'.gitmodules',ROOT/'uv.lock',ROOT/'pyproject.toml']:inputs[key(p)]=digest(p)
    need(post['independent_review'] is False and post['status']=='PRODUCER_POST_RUN_MODULAR_KERNEL_CALIBRATION_PASS','preserve post-run calibration status')
    controls=calibration();need(controls==post['checked'],'independent exhaustive controls reproduce post-run reported population')
    raw=read(FIX);c=raw['cubic_core60'];f=raw['factor60x180'];d=raw['residual180x180'];n=20;rows=60;cols=180
    need(len(c)==rows and all(len(r)==rows for r in c) and len(f)==rows and all(len(r)==cols for r in f) and len(d)==cols and all(len(r)==cols for r in d),'saved dimensions')
    need(all(type(x)is int and x in (0,1) for a in (c,f,d) for row in a for x in row),'strict binary fixture')
    cn=[{j for j,v in enumerate(r) if v} for r in c];fn=[{j for j,v in enumerate(r) if v} for r in f];ft=transpose(f);fc=[{i for i,v in enumerate(r) if v} for r in ft];dn=[{j for j,v in enumerate(r) if v} for r in d]
    k=[[20*int(i==j)-c[i][j]-len(cn[i]&cn[j])+2-int(i//20==j//20) for j in range(rows)] for i in range(rows)]
    h=[[2-f[i][j]-sum(f[t][j] for t in cn[i]) for j in range(cols)] for i in range(rows)]
    need(all(len(fn[i]&fn[j])==k[i][j] for i in range(rows) for j in range(rows)),'literal exact243 Gram')
    need(all(len(fn[i]&dn[j])==h[i][j] for i in range(rows) for j in range(cols)),'literal exact243 mixed FD')
    need(all(len(dn[i]&dn[j])+len(fc[i]&fc[j])==20*int(i==j)-d[i][j]+2 for i in range(cols) for j in range(cols)),'literal exact243 residual quadratic')
    need(all(sum(r)==18 for r in f) and all(sum(f[g*20+i][j] for i in range(20))==2 for g in range(3) for j in range(cols)),'exact243 margins')
    rng=random.Random(20260930);results=[];perturbations=[];basis_records=[];negative=[]
    def reject(label,call):
        try:call()
        except (ValueError,IndexError,KeyError,TypeError):negative.append(label)
        else:raise AssertionError('corruption accepted '+label)
    corrupt_h=deepcopy(h);corrupt_h[0][0]+=1;reject('changed_integer_rhs',lambda:need(all(len(fn[i]&dn[j])==corrupt_h[i][j] for i in range(rows) for j in range(cols)),'known residual mixed equality'))
    for p,reported in zip((2,3),run['results'],strict=True):
        need(reported['prime']==p and len(reported['attempts'])==128 and reported['counterexample'] is None,'frozen finite population')
        left,pivots=kernel(transpose(f),p);right,right_pivots=kernel(f+[[1]*cols],p)
        need((len(pivots),len(left))==(reported['base_modular_row_rank'],reported['base_left_kernel_dimension']),'exact base rank')
        need(all(direct_kernel(transpose(f),w,p) and direct_kernel(transpose(h),w,p) for w in left),'base exact modular compatibility')
        need(all(direct_kernel(f+[[1]*cols],v,p) for v in right),'entire base right kernel')
        basis_records.append(dict(prime=p,left_basis=left,right_basis=right,left_pivot_columns=pivots,right_pivot_columns=right_pivots,free_coordinate_basis_order='Ascending free columns of canonical reduced row space; derived by distinct forward elimination/back-substitution.'))
        # Changed RHS must break an explicit exact left-kernel witness.
        witness=next(w for w in left if any(w));coordinate=next(i for i,x in enumerate(witness) if x);bad=deepcopy(h);bad[coordinate][0]+=1
        reject(f'changed_modular_rhs_p{p}',lambda bad=bad,witness=witness,p=p:need(direct_kernel(transpose(bad),witness,p),'modular left-kernel RHS compatibility'))
        attempt_records=[]
        for trial in tqdm(range(128),desc=f'Independent modular reconstruction GF{p}'):
            for selection in range(100):
                coeff=[rng.randrange(p) for _ in right];v=[sum(a*b for a,b in zip(coeff,col))%p for col in zip(*right)]
                if any(v) and sum(x*x for x in v)%p==0:break
            else:raise ValueError('protocol exhausted100isotropic draws')
            u=[]
            for g in range(3):
                values=[rng.randrange(p) for _ in range(19)];u+=values+[-sum(values)%p]
            need(direct_kernel(f,v,p) and sum(v)%p==0 and sum(x*x for x in v)%p==0 and all(sum(u[g*20:(g+1)*20])%p==0 for g in range(3)),'every perturbation premise')
            ff=[[(f[i][j]+u[i]*v[j])%p for j in range(cols)] for i in range(rows)]
            hh=[[(2-ff[i][j]-sum(ff[t][j] for t in cn[i]))%p for j in range(cols)] for i in range(rows)]
            pp=planes(ff,p)
            need(all(dot(pp[i],pp[j],p)==k[i][j]%p for i in range(rows) for j in range(rows)),'all modular Gram entries')
            need(all(sum(r)%p==18%p for r in ff) and all(sum(ff[g*20+i][j] for i in range(20))%p==2%p for g in range(3) for j in range(cols)),'all modular margins')
            ll,piv=kernel(transpose(ff),p);lp=planes(ll,p);fp=planes(transpose(ff),p);hp=planes(transpose(hh),p)
            need(all(dot(w,col,p)==0 for w in lp for col in fp),'complete computed left-kernel vectors')
            failures=sum(dot(w,col,p)!=0 for w in lp for col in hp)
            outcome=dict(trial=trial,modular_row_rank=len(piv),left_kernel_dimension=len(ll),mixed_kernel_failures=failures)
            need(outcome==reported['attempts'][trial] and failures==0,'independent finite outcome matches saved summary')
            attempt_records.append(outcome)
            perturbations.append(dict(prime=p,trial=trial,isotropic_draws=selection+1,u=u,v=v,factor_sha256=array_hash(ff),rhs_sha256=array_hash(hh),canonical_left_basis_sha256=array_hash(ll),result=outcome,hash_serialization='ASCII compact JSON nested integer arrays'))
            if trial==0:
                bv=v[:];bv[0]=(bv[0]+1)%p;reject(f'changed_right_kernel_p{p}',lambda bv=bv,p=p:need(direct_kernel(f,bv,p),'right kernel'))
                bu=u[:];bu[0]=(bu[0]+1)%p;reject(f'changed_fibre_sum_p{p}',lambda bu=bu,p=p:need(all(sum(bu[g*20:(g+1)*20])%p==0 for g in range(3)),'fibre sum'))
                bw=ll[0][:];bw[0]=(bw[0]+1)%p;reject(f'changed_left_vector_p{p}',lambda bw=bw,ff=ff,p=p:need(direct_kernel(transpose(ff),bw,p),'left kernel'))
                reject(f'wrong_rank_p{p}',lambda piv=piv,outcome=outcome:need(len(piv)==outcome['modular_row_rank']+1,'rank'))
        need(reported['result']=='NO_COUNTEREXAMPLE_IN_FROZEN128_PERTURBATIONS','finite interpretation')
        hashes=[x['factor_sha256'] for x in perturbations if x['prime']==p]
        results.append(dict(prime=p,base_row_rank=len(pivots),base_left_kernel_dimension=len(left),attempts=128,distinct_reconstructed_factors=len(set(hashes)),ranks=sorted({x['modular_row_rank'] for x in attempt_records}),left_kernel_dimensions=sorted({x['left_kernel_dimension'] for x in attempt_records}),mixed_kernel_failure_trials=0,all128_Gram_and_margin_checks=True))
    rook=[[int(i!=j and (i//3==j//3 or i%3==j%3)) for j in range(9)] for i in range(9)]
    need(all(sum(rook[i][k]*rook[k][j] for k in range(9))==2*int(i==j)-rook[i][j]+2 for i in range(9) for j in range(9)),'exact small positive control')
    save(args.out/'reconstructed_bases.json',basis_records);save(args.out/'reconstructed_perturbations.json',perturbations);save(args.out/'controls.json',dict(exhaustive_tiny=controls,rook9_identity_entries=81,exact243=dict(Gram_entries=3600,mixed_entries=10800,quadratic_entries=32400),fresh_corruptions_rejected=negative))
    archive=ROOT/'external_conway99_research';commit=subprocess.check_output(['git','-C',str(archive),'rev-parse','HEAD'],text=True).strip();need(commit=='85e705cc6c2a14d123120c93a847e30aaab1789e','pinned archive commit')
    record=dict(status='INDEPENDENT_FINITE_MODULAR_KERNEL_FAILED_ROUTE_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=inputs,claim_id='C-FINITE-243-MODULAR-KERNEL-PERTURBATION-ROUTE',claim_revision=1,exact_statement='The deterministic seed20260930 protocol reconstructed independently on the pinned243 fixture yields128 trials overGF2 and128 overGF3; all preserve modular Gram/margins and all retain left-kernel compatibility with their own mixed RHS. These outcomes agree with all saved trial summaries. No other perturbation or binary/graph feasibility statement is asserted.',results=results,checking_path='Independent integer echelon/back-substitution; distinct last-row pivots; bit-plane exact Gram and kernel products; no producer imports. Shared Python random.Random draw implementation is needed for exact protocol reconstruction.',missing_original_artifact_limitation='Original successful u/v and factor matrices/hashes were not saved; the new audit retains exact reconstructed vectors and matrix hashes, without retroactively claiming original-matrix artifact authentication.',producer_post_run_calibration_timing_preserved=True,artifact_availability='LOCAL_ONLY',retrieval='All new replay inputs are the bound repository fixture/source/seed plus reconstructed_bases.json and reconstructed_perturbations.json; public availability follows repository publication, not this local run.',archive_overlap=dict(repository='https://github.com/YesterdaysLemon/conway-99-research.git',commit=commit,path='attempts/wave58-cross-incidence-rank/derivation.md',sections='1–2, prior real Gram/kernel identities and attribution to Wave36',scope='Historical document is conditional on prism-free endpoint; that assumption is not imported.',novelty_claim=False),limitations=['Finite fields only; GF3 matrices need not be binary.','Compatibility permits arbitrary field-valued D, not symmetric binary residuals.','No counterexample among256 attempts is not a universal implication theorem.','Fixture parameters243 are not the Conway99 target.','No rank novelty, target exclusion, SAT call or target graph produced.'],solver_calls=0,target_resolution=False,elapsed_seconds=time.monotonic()-start,outputs_sha256={key(p):digest(p) for p in args.out.iterdir() if p.is_file()})
    save(args.out/'summary.json',record);print(json.dumps(dict(status=record['status'],summary_sha256=digest(args.out/'summary.json'),elapsed_seconds=record['elapsed_seconds'])))

if __name__=='__main__':main()
