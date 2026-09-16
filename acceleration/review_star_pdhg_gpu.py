"""Independent binary parsing and cold-CPU references for the CUDA prototype.

No exporter/LP producer imports. Real CPU replays use the exact canonical CSR
bytes presented to CUDA. Tolerances are declared here before GPU execution.
Tiny generic models additionally use a rational simplex/KKT recurrence.
"""
import os
for _name in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS'):
    os.environ[_name]='1'
import argparse
from fractions import Fraction
from hashlib import sha256
import json
import math
from pathlib import Path
import struct
import subprocess
import time
import numpy as np
from scipy.sparse import csr_matrix
from star_marginal_cp_cpu_v2 import product_simplex_projection

ROOT=Path(__file__).resolve().parents[1]
HELPER_SHA='6a2823692dfb0baab9b0fdb011f84c6fdda82361d9af01433260020cb19ae65d'
SHORT_VECTOR_ATOL=2e-11
SHORT_SCALAR_ATOL=2e-8
LONG_VECTOR_ATOL=2e-9
LONG_SCALAR_ATOL=2e-6
TINY_VECTOR_ATOL=2e-13
TINY_SCALAR_ATOL=2e-12

def path(p):return (ROOT/str(p).replace('\\','/')).resolve()
def key(p):return path(p).relative_to(ROOT).as_posix()
def digest(p):return sha256(path(p).read_bytes()).hexdigest()
def require(ok,msg):
    if not ok:raise ValueError(msg)
def dump(p,d):
    with path(p).open('x',encoding='utf-8') as f:json.dump(d,f,indent=2,allow_nan=False);f.write('\n')
def bindings_for(*files):return {key(p):digest(p) for p in files}
def verify_bindings(d):
    for p,h in d.get('inputs_sha256',{}).items():require(digest(p)==h,'Changed bound file '+key(p))

def parse_binary(filename):
    data=path(filename).read_bytes(); cursor=0
    require(len(data)<=2*1024**3,'Input exceeds2GiB')
    def read(kind,n):
        nonlocal cursor
        size=np.dtype(kind).itemsize*n
        require(cursor+size<=len(data),'Truncated binary')
        v=np.frombuffer(data,dtype=kind,count=n,offset=cursor).copy();cursor+=size
        return v
    require(data[:8]==b'C99SCP01','Wrong binary magic');cursor=8
    count,check_count=map(int,read('<u4',2))
    require(1<=count<=256 and 1<=check_count<=16,'Header limits')
    checks=list(map(int,read('<u4',check_count)))
    require(checks==sorted(set(checks)) and 1<=checks[0]<=checks[-1]<=20000,'Bad checkpoints')
    models=[];totals=[0,0,0]
    for _ in range(count):
        start=cursor; N,M,Q,B,nnz=map(int,read('<u4',5))
        require(0<N<=100000 and 0<M<=20000 and 0<=Q<=M and 0<B<=128 and 0<nnz<=8000000,'Record dimensions')
        totals=[x+y for x,y in zip(totals,(N,M,nnz))]
        require(totals[0]<=2000000 and totals[1]<=1000000 and totals[2]<=64000000,'Aggregate limits')
        offsets=read('<u4',B+1).astype(np.int64)
        require(offsets[0]==0 and offsets[-1]==N and np.all(np.diff(offsets)>0) and max(np.diff(offsets))<=8192,'Bad offsets')
        def csr(rows,cols):
            ptr=read('<u4',rows+1).astype(np.int64);ind=read('<u4',nnz).astype(np.int64);val=read('<f8',nnz)
            require(ptr[0]==0 and ptr[-1]==nnz and np.all(np.diff(ptr)>=0),'Bad CSR row pointers')
            require(np.all(ind<cols) and np.all(np.isfinite(val)) and np.all(val!=0),'Bad CSR index/value')
            require(all(np.all(np.diff(ind[a:b])>0) for a,b in zip(ptr[:-1],ptr[1:])),'Unsorted/duplicate CSR columns')
            return csr_matrix((val,ind,ptr),shape=(rows,cols))
        A=csr(M,N);AT=csr(N,M);b=read('<f8',M)
        require(np.all(np.isfinite(b)),'Nonfinite targets')
        trans=A.transpose().tocsr();trans.sort_indices()
        require(np.array_equal(trans.indptr,AT.indptr) and np.array_equal(trans.indices,AT.indices) and np.array_equal(trans.data,AT.data),'Not exact transpose')
        rows=np.asarray(abs(A).sum(axis=1)).ravel();cols=np.asarray(abs(A).sum(axis=0)).ravel()
        require(np.all(np.isfinite(rows)) and np.all(np.isfinite(cols)),'Overflowed absolute sums')
        sigma=.9/np.maximum(1,rows);tau=np.empty(N)
        for a,bound in zip(offsets[:-1],offsets[1:]):tau[a:bound]=.9/max(1,float(max(cols[a:bound])))
        models.append(dict(A=A,AT=AT,b=b,Q=Q,offsets=offsets,sigma=sigma,tau=tau,start=start,end=cursor,record_sha256=sha256(data[start:cursor]).hexdigest()))
    require(cursor==len(data),'Trailing bytes')
    return checks,models

def bounds(model,p,y):
    Q=model['Q'];r=model['A']@p-model['b'];c=model['AT']@y
    upper=float(abs(r[:Q]).sum()+np.maximum(r[Q:],0).sum())
    lower=sum(float(min(c[a:b])) for a,b in zip(model['offsets'][:-1],model['offsets'][1:]))-float(model['b']@y)
    return dict(primal_upper_numeric=upper,dual_lower_numeric=lower,numeric_gap=upper-lower)

def exact_project(z):
    # Independent rational support enumeration, only tiny domains <=3 here.
    for mask in range(1,1<<len(z)):
        active=[i for i in range(len(z)) if mask>>i&1]
        theta=(sum(z[i] for i in active)-1)/len(active)
        if all((z[i]>theta)==bool(mask>>i&1) for i in range(len(z))):
            return [max(Fraction(0),v-theta) for v in z]
    raise ValueError('Tiny exact projection has no support')

def rational_reference(model,checkpoints):
    A=[[Fraction(v) for v in row] for row in model['A'].toarray().tolist()]
    b=[Fraction(v) for v in model['b']];M=len(A);N=len(A[0]);Q=model['Q']
    offsets=list(map(int,model['offsets']));sigma=[Fraction(9,10)/max(1,sum(map(abs,row))) for row in A]
    column=[sum(abs(A[i][j]) for i in range(M)) for j in range(N)]
    tau=[Fraction(0)]*N;p=[Fraction(0)]*N
    for a,z in zip(offsets[:-1],offsets[1:]):
        tau[a:z]=[Fraction(9,10)/max(1,max(column[a:z]))]*(z-a);p[a:z]=[Fraction(1,z-a)]*(z-a)
    pb=p[:];y=[Fraction(0)]*M;pa=[Fraction(0)]*N;ya=[Fraction(0)]*M;records={}
    for it in range(1,max(checkpoints)+1):
        ny=[min(Fraction(1),max(Fraction(-1 if i<Q else 0),y[i]+sigma[i]*(sum(A[i][j]*pb[j] for j in range(N))-b[i]))) for i in range(M)]
        trial=[p[j]-tau[j]*sum(A[i][j]*ny[i] for i in range(M)) for j in range(N)]
        new=[]
        for a,z in zip(offsets[:-1],offsets[1:]):new+=exact_project(trial[a:z])
        pb=[2*v-old for v,old in zip(new,p)];p,y=new,ny
        pa=[old+(v-old)/it for old,v in zip(pa,p)];ya=[old+(v-old)/it for old,v in zip(ya,y)]
        if it in checkpoints:records[it]={k:np.array(list(map(float,v))) for k,v in [('p_last',p),('pbar_last',pb),('y_last',y),('p_average',pa),('y_average',ya)]}
    return records

def write_tiny(directory):
    out=path(directory);require(not out.exists(),'Fresh tiny directory required');out.mkdir(parents=True)
    definitions=[('two_simplexes',[[1,-1,0,0],[0,0,1,-1],[1,0,1,0]],[0,0,.5],[0,2,4],2),
                 ('one_inequality',[[1,2,-1]],[.25],[0,3],0),
                 ('negative_equality',[[1,2,-1]],[2],[0,3],1),
                 ('empty_row',[[1,-1],[0,0]],[0,1],[0,2],1)]
    chunks=[b'C99SCP01',struct.pack('<5I',len(definitions),3,1,2,10)]
    for name,rows,b,offsets,Q in definitions:
        A=csr_matrix(np.asarray(rows,dtype=float));AT=A.transpose().tocsr();AT.sort_indices()
        N=A.shape[1];M=A.shape[0]
        chunks.append(struct.pack('<5I',N,M,Q,len(offsets)-1,A.nnz));chunks.append(np.array(offsets,dtype='<u4').tobytes())
        for matrix in (A,AT):
            for data,dtype in [(matrix.indptr,'<u4'),(matrix.indices,'<u4'),(matrix.data,'<f8')]:chunks.append(np.asarray(data,dtype=dtype).tobytes())
        chunks.append(np.asarray(b,dtype='<f8').tobytes())
    binary=out/'input.bin';binary.write_bytes(b''.join(chunks))
    dump(out/'manifest.json',dict(status='SYNTHETIC_COLD_STAR_PDHG_TINY_INPUT',inputs_sha256=bindings_for(__file__,ROOT/'acceleration/star_marginal_cp_cpu_v2.py'),binary_path=key(binary),binary_sha256=digest(binary),cases=[dict(name=r[0]) for r in definitions],candidate_count=len(definitions),checkpoints=[1,2,10],scope='Synthetic saddle models only; no99vertex graph claim'))

def prepare(manifest_path,out):
    out=path(out);require(not out.exists(),'Fresh reference directory required')
    manifest=json.loads(path(manifest_path).read_bytes());verify_bindings(manifest)
    require(manifest['status'] in ('AUDITED_COLD_STAR_PDHG_BINARY_EXPORTED','SYNTHETIC_COLD_STAR_PDHG_TINY_INPUT'),'Wrong input manifest')
    require(digest(manifest['binary_path'])==manifest['binary_sha256'],'Wrong binary hash')
    require(digest(ROOT/'acceleration/star_marginal_cp_cpu_v2.py')==HELPER_SHA,'Changed CPU helper')
    checkpoints,models=parse_binary(manifest['binary_path'])
    require(checkpoints==manifest['checkpoints'] and len(models)==manifest['candidate_count'],'Header/manifest mismatch')
    synthetic=manifest['status']=='SYNTHETIC_COLD_STAR_PDHG_TINY_INPUT';out.mkdir(parents=True)
    inputs=bindings_for(__file__,ROOT/'acceleration/star_marginal_cp_cpu_v2.py',manifest_path,manifest['binary_path']);inputs.update(manifest['inputs_sha256'])
    results=[];started=time.perf_counter()
    for i,m in enumerate(models):
        if not synthetic:
            declared=manifest['cases'][i]
            require(m['record_sha256']==declared['record_sha256'] and m['start']==declared['record_byte_offset'],'Model/manifest record association')
            require(sha256(m['sigma'].astype('<f8').tobytes()).hexdigest()==declared['sigma_f64le_sha256'],'Exported step sigma differs')
            require([float(m['tau'][a]) for a in m['offsets'][:-1]]==declared['block_tau'],'Exported block steps differ')
        offsets=m['offsets'];counts=np.diff(offsets);N=m['A'].shape[1];M=m['A'].shape[0]
        p=np.repeat(1.0/counts,counts);pb=p.copy();y=np.zeros(M);pa=np.zeros(N);ya=np.zeros(M)
        initial=bounds(m,p,y);upper=initial['primal_upper_numeric'];lower=initial['dual_lower_numeric'];records=[];arrays={};tick=time.perf_counter()
        rational=rational_reference(m,checkpoints) if synthetic else None
        box=np.r_[np.full(m['Q'],-1.0),np.zeros(M-m['Q'])]
        for it in range(1,max(checkpoints)+1):
            ny=np.clip(y+m['sigma']*(m['A']@pb-m['b']),box,1)
            new=product_simplex_projection(p-m['tau']*(m['AT']@ny),offsets)
            pb,p,y=2*new-p,new,ny;pa+=(p-pa)/it;ya+=(y-ya)/it
            if it not in checkpoints:continue
            values=dict(p_last=p,pbar_last=pb,y_last=y,p_average=pa,y_average=ya)
            require(all(np.all(np.isfinite(v)) for v in values.values()),'Nonfinite CPU iterate')
            err=max(abs(float(p[a:b].sum())-1) for a,b in zip(offsets[:-1],offsets[1:]))
            require(err<1e-10 and np.min(p)>=0,'CPU simplex invariant')
            last,average=bounds(m,p,y),bounds(m,pa,ya)
            upper=min(upper,last['primal_upper_numeric'],average['primal_upper_numeric']);lower=max(lower,last['dual_lower_numeric'],average['dual_lower_numeric'])
            rational_error={k:float(max(abs(v-rational[it][k]))) for k,v in values.items()} if synthetic else None
            if synthetic:require(max(rational_error.values())<=TINY_VECTOR_ATOL,'Tiny exact rational/CPU mismatch')
            for label,value in values.items():arrays[f'iteration_{it}_{label}']=value.copy()
            records.append(dict(iterations=it,last=last,average=average,best_upper_numeric=upper,best_lower_numeric=lower,simplex_max_error=err,rational_reference_errors=rational_error))
        vectors=out/f'case_{i}_vectors.npz';np.savez_compressed(vectors,**arrays)
        results.append(dict(candidate_index=i,n_variables=N,n_rows=M,n_equalities=m['Q'],domain_counts=counts.tolist(),initial=initial,checkpoints=records,vectors_path=key(vectors),vectors_sha256=digest(vectors),elapsed_seconds=time.perf_counter()-tick))
        print(json.dumps(dict(cpu_case=i,seconds=results[-1]['elapsed_seconds'],last_upper=records[-1]['last']['primal_upper_numeric'])),flush=True)
    result=dict(status='CANONICAL_CSR_COLD_CPU_REFERENCE_SAVED',inputs_sha256=inputs,input_manifest_path=key(manifest_path),input_manifest_sha256=digest(manifest_path),binary_path=manifest['binary_path'],binary_sha256=manifest['binary_sha256'],synthetic_rational_controls=synthetic,results=results,checkpoints=checkpoints,
                tolerances=dict(short_vector_abs=SHORT_VECTOR_ATOL,short_scalar_abs=SHORT_SCALAR_ATOL,long_vector_abs=LONG_VECTOR_ATOL,long_scalar_abs=LONG_SCALAR_ATOL,tiny_vector_abs=TINY_VECTOR_ATOL,tiny_scalar_abs=TINY_SCALAR_ATOL),elapsed_seconds=time.perf_counter()-started,scope='Float64 cold recurrence on exact exported canonical CSR order; no bitwise equivalence claim to older unsorted matrices. Numerical controls are not proofs or exclusions.')
    dump(out/'reference.json',result)

def compare(reference_path,gpu_path,gpu_source,gpu_binary,out):
    require(not path(out).exists(),'Preserve prior parity audit')
    ref=json.loads(path(reference_path).read_bytes());verify_bindings(ref)
    gpu=json.loads(path(gpu_path).read_bytes())
    require(ref['status']=='CANONICAL_CSR_COLD_CPU_REFERENCE_SAVED','Bad CPU reference')
    require(len(gpu['results'])==len(ref['results']) and gpu['eta']==.9 and gpu['theta']==1 and gpu['numerical_scores_are_proofs'] is False,'Wrong GPU output geometry/scope')
    inputs=bindings_for(__file__,reference_path,gpu_path,gpu_source,gpu_binary);inputs.update(ref['inputs_sha256'])
    errors=[]
    for expected,actual in zip(ref['results'],gpu['results']):
        for name in ('candidate_index','n_variables','n_rows','n_equalities','domain_counts'):require(expected[name]==actual[name],'GPU record mismatch '+name)
        require(digest(expected['vectors_path'])==expected['vectors_sha256'],'Changed CPU vectors');inputs[key(expected['vectors_path'])]=expected['vectors_sha256']
        with np.load(path(expected['vectors_path'])) as vectors:
            init_error=max(abs(actual['initial'][k]-v) for k,v in expected['initial'].items())
            require(init_error<=SHORT_SCALAR_ATOL,'Initial scalar mismatch')
            require([r['iterations'] for r in actual['checkpoints']]==ref['checkpoints'],'Wrong GPU checkpoint order')
            for truth,record in zip(expected['checkpoints'],actual['checkpoints']):
                it=truth['iterations'];tiny=ref['synthetic_rational_controls']
                vt=TINY_VECTOR_ATOL if tiny else SHORT_VECTOR_ATOL if it<=10 else LONG_VECTOR_ATOL
                st=TINY_SCALAR_ATOL if tiny else SHORT_SCALAR_ATOL if it<=10 else LONG_SCALAR_ATOL
                component={}
                for name in ('p_last','pbar_last','y_last','p_average','y_average'):
                    exact=vectors[f'iteration_{it}_{name}'];value=np.asarray(record[name],dtype=float)
                    require(value.shape==exact.shape and np.all(np.isfinite(value)),'Malformed GPU vector '+name)
                    error=float(max(abs(exact-value)));component[name]=error
                    require(error<=vt,f'GPU vector mismatch candidate{expected["candidate_index"]} step{it} {name}: {error}>{vt}')
                scalar={}
                for point in ('last','average'):
                    for name,v in truth[point].items():
                        require(math.isfinite(record[point][name]),'Nonfinite GPU scalar')
                        error=abs(record[point][name]-v);scalar[point+'.'+name]=error
                        require(error<=st,'GPU scalar mismatch '+point+'.'+name)
                for name in ('best_upper_numeric','best_lower_numeric'):
                    error=abs(record[name]-truth[name]);scalar[name]=error;require(error<=st,'Best checkpoint score mismatch')
                errors.append(dict(candidate_index=expected['candidate_index'],iterations=it,vector_errors=component,scalar_errors=scalar,vector_tolerance=vt,scalar_tolerance=st))
    report=dict(status='COLD_STAR_CUDA_CANONICAL_CPU_COMPONENTWISE_PARITY_PASS',inputs_sha256=inputs,comparisons=errors,
                max_vector_error=max(v for r in errors for v in r['vector_errors'].values()),max_scalar_error=max(v for r in errors for v in r['scalar_errors'].values()),
                tolerance_policy='Declared before GPU runs, absolute/componentwise, zero relative tolerance; no post-failure relaxation',
                graph_or_exclusion_claims=False,scope='CPU/GPU recurrence parity on these exact inputs only; tiny rational control errors are additionally stored in the CPU reference.')
    dump(out,report);print(json.dumps(dict(status=report['status'],vector_error=report['max_vector_error'],scalar_error=report['max_scalar_error'],sha256=digest(out))))

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='mode',required=True)
    q=sub.add_parser('tiny');q.add_argument('--out',required=True)
    q=sub.add_parser('prepare');q.add_argument('--manifest',required=True);q.add_argument('--out',required=True)
    q=sub.add_parser('compare');q.add_argument('--reference',required=True);q.add_argument('--gpu-output',required=True);q.add_argument('--gpu-source',required=True);q.add_argument('--gpu-binary',required=True);q.add_argument('--out',required=True)
    a=p.parse_args()
    if a.mode=='tiny':write_tiny(a.out)
    elif a.mode=='prepare':prepare(a.manifest,a.out)
    else:compare(a.reference,a.gpu_output,a.gpu_source,a.gpu_binary,a.out)

if __name__=='__main__':main()
