"""Independent CPU PDHG with sorted-threshold simplex projection; numerical audit only."""
import os
for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[name]='1'
from datetime import datetime,timezone
import json,struct,sys,subprocess,platform,time
from pathlib import Path
import numpy as np
import scipy
from scipy.sparse import csr_matrix,load_npz,vstack
from tqdm import tqdm
import audit_20260917_partial_matching as h
ROOT=h.ROOT;D=ROOT/'acceleration/results/20260917_moment_pdhg_gpu';OUT=ROOT/'acceleration/results/20260917_independent_review/moment_pdhg_gpu_cpu_parity'
VTOL=1e-8;STOL=1e-7

def decode(data):
    h.require(data[:8]==b'C99MHP01','magic');pos=8
    def ints(n):
        nonlocal pos
        value=struct.unpack_from('<'+'I'*n,data,pos);pos+=4*n;return value
    models,ncheck=ints(2);h.require(models==1 and 0<ncheck<=16,'model/checkpoint count');cp=ints(ncheck)
    h.require(list(cp)==sorted(set(cp))and 0<cp[0]<=cp[-1]<=100000,'checkpoints')
    n,m,q,blocks,nnz=ints(5);h.require(0<n<=1000000 and 0<m<=10000 and q<=m and 0<blocks<=128 and nnz<=100000000,'dimensions')
    def array(dtype,count):
        nonlocal pos
        out=np.frombuffer(data,dtype=dtype,count=count,offset=pos).copy();pos+=out.nbytes;return out
    offsets=array('<u4',blocks+1);h.require(offsets[0]==0 and offsets[-1]==n and all(0<int(b)-int(a)<=100000 for a,b in zip(offsets,offsets[1:])),'offsets')
    def matrix(rows,cols):
        rp=array('<u4',rows+1);ci=array('<u4',nnz);values=array('<f8',nnz)
        h.require(rp[0]==0 and rp[-1]==nnz and np.all(rp[1:]>=rp[:-1])and np.all(ci<cols)and np.isfinite(values).all()and np.all(values!=0),'CSR arrays')
        A=csr_matrix((values,ci,rp),shape=(rows,cols));h.require(A.has_canonical_format,'canonical sparse arrays');return A
    A=matrix(m,n);AT=matrix(n,m);b=array('<f8',m)
    h.require(np.isfinite(b).all()and pos==len(data),'finite targets/exact end')
    T=A.T.tocsr();h.require(np.array_equal(T.indptr,AT.indptr)and np.array_equal(T.indices,AT.indices)and np.array_equal(T.data,AT.data),'exact transpose')
    return A,b,offsets,q,cp

def project(v):
    # KKT threshold from sorted prefix sums, independent of GPU bisection/reduction.
    ordered=np.sort(v)[::-1];prefix=np.cumsum(ordered)-1;good=ordered>prefix/np.arange(1,len(v)+1);rho=np.flatnonzero(good)[-1]
    return np.maximum(v-prefix[rho]/(rho+1),0)

def diagnostics(A,b,offsets,q,p,y):
    residual=A@p-b;cost=A.T@y
    return dict(soft_moment_L1_diagnostic=float(np.abs(residual[:q]).sum()),hard_reciprocity_L1=float(np.abs(residual[q:]).sum()),hard_reciprocity_Linf=float(np.max(np.abs(residual[q:]),initial=0)),simplex_Linf=max(abs(float(p[a:z].sum())-1)for a,z in zip(offsets,offsets[1:])),dual_support_lower_numeric=float(sum(np.min(cost[a:z])for a,z in zip(offsets,offsets[1:]))-b@y))

def main():
    OUT.mkdir(exist_ok=False);bindings={};started=time.monotonic()
    def read(p):bindings[h.key(p)]=h.digest(p);return json.loads(p.read_bytes())
    prereg=dict(timestamp=datetime.now(timezone.utc).isoformat(),question='Do the four frozen100-iteration pilot runs match an independently implemented CPU operator and sorted projection?',scope='Three synthetic inputs and one audited89308-column two-coordinate model; checkpoints1,2,10,100; allfive saved vectors and both metric groups.',vector_absolute_Linf_tolerance=VTOL,scalar_absolute_tolerance=STOL,selection='All four recorded cases, no omissions',resource_limit_seconds=300,acceptance='Exact export mapping and transpose; every checkpoint within fixed tolerances; positive/corrupt controls pass',limitations='Floating agreement is engineering verification only, not a certificate or proof of arbitrary-run stability.',source_sha256=h.digest(__file__))
    with(OUT/'preregistration.json').open('x')as f:json.dump(prereg,f,indent=2)
    manifest=read(D/'export/manifest.json');run=read(D/'pilot/summary.json')
    for d in(manifest,read(D/'pilot/manifest.json')):
        for f,v in d.get('inputs_sha256',{}).items():h.require(h.digest(ROOT/f)==v,'input binding');bindings[f]=v
    for f,v in run['output_sha256'].items():h.require(h.digest(D/'pilot'/f)==v,'run output binding');bindings[h.key(D/'pilot'/f)]=v
    gate=read(ROOT/'acceleration/results/20260917_independent_review/two_matching_moments.json');h.require(h.digest(ROOT/'acceleration/results/20260917_independent_review/two_matching_moments.json')=='5af1f353a70a16fc5f915195b911d782e360ffc069f0463936b7a9dea983197ed'.replace('f046','046'),'audited model gate')
    modelroot=ROOT/'acceleration/results/20260917_two_matching_moments';meta=read(modelroot/'model.json')
    for name in('model.json','integer_augmented_csr.npz'):h.require(h.digest(modelroot/name)==gate['inputs_sha256'][h.key(modelroot/name)],'exact earlier model');bindings[h.key(modelroot/name)]=h.digest(modelroot/name)
    C=load_npz(modelroot/'integer_augmented_csr.npz');n=meta['probability_offsets'][-1];hard=1884
    expected=vstack([C[hard:,:n],C[84:hard,:n]],format='csr');expected.sort_indices();expectedb=np.array(meta['rhs'][hard:]+meta['rhs'][84:hard])
    projectioncontrols=[]
    for v,w in[(np.array([0.,0.]),[.5,.5]),(np.array([3.,-1.]),[1.,0.]),(np.array([2.]),[1.]),(np.zeros(45882),np.full(45882,1/45882))]:
        result=project(v);h.require(np.max(np.abs(result-w))<1e-12 and abs(result.sum()-1)<1e-10,'known projection');projectioncontrols.append(len(v))
    rejected=[]
    for name in('bad_magic','bad_transpose','domain_out_of_range','trailing_bytes'):
        try:decode((D/'pilot'/f'{name}.bin').read_bytes())
        except (AssertionError,ValueError,RuntimeError,struct.error):rejected.append(name)
        else:raise AssertionError('corrupted input accepted '+name)
    records=[]
    for name,record in manifest['records'].items():
        pth=ROOT/record['path'];bindings[h.key(pth)]=h.digest(pth);h.require(bindings[h.key(pth)]==record['sha256'],'binary identity')
        A,b,offsets,q,cps=decode(pth.read_bytes())
        if name=='two_coordinate':
            h.require(A.shape==expected.shape and q==3486 and list(offsets)==meta['probability_offsets']and np.array_equal(b,expectedb),'full moment export row/offset mapping')
            for field in('indptr','indices','data'):h.require(np.array_equal(getattr(A,field),getattr(expected,field)),'every exported coefficient '+field)
        else:
            if name=='positive_uniform':wanted=csr_matrix([[0.,2.],[1.,-1.]]);bb=[1,0];off=[0,2]
            elif name=='unbounded_hard_dual':wanted=csr_matrix([[0.],[1.]]);bb=[0,-1];off=[0,1]
            elif name=='large_uniform':wanted=csr_matrix((1,45882));bb=[0];off=[0,45882]
            else:raise AssertionError('unexpected case')
            h.require(A.shape==wanted.shape and (A!=wanted).nnz==0 and list(b)==bb and list(offsets)==off and q==1,'synthetic case identity')
        sigma=.9/np.maximum(1,np.asarray(abs(A).sum(axis=1)).ravel());columns=np.asarray(abs(A).sum(axis=0)).ravel();tau=np.empty(A.shape[1]);p=np.empty(A.shape[1])
        for a,z in zip(offsets,offsets[1:]):tau[a:z]=.9/max(1,max(columns[a:z]));p[a:z]=1/(z-a)
        pb=p.copy();y=np.zeros(A.shape[0]);psum=np.zeros_like(p);ysum=np.zeros_like(y);checks=[]
        for iteration in tqdm(range(1,101),desc='Independent CPU '+name,unit='iteration'):
            h.require(time.monotonic()-started<300,'audit cap')
            y+=sigma*(A@pb-b);y[:q]=np.clip(y[:q],-1,1);trial=p-tau*(A.T@y);new=np.empty_like(p)
            for a,z in zip(offsets,offsets[1:]):new[a:z]=project(trial[a:z])
            pb=2*new-p;p=new;psum+=p;ysum+=y;pa=psum/iteration;ya=ysum/iteration
            if iteration not in cps:continue
            gpu=read(D/'pilot'/f'{name}_{iteration}.json');h.require(gpu['iterations']==iteration and gpu['numerical_scores_are_proofs']is False,'checkpoint semantics')
            vectors=dict(p_last=p,pbar_last=pb,y_last=y,p_average=pa,y_average=ya);errors={}
            for k,v in vectors.items():
                observed=np.asarray(gpu[k]);h.require(observed.shape==v.shape and np.isfinite(observed).all(),'finite vectors');err=float(np.max(np.abs(v-observed)));errors[k]=err;h.require(err<=VTOL,'vector parity '+name+' '+k)
                bad=observed.copy();bad[0]+=100*VTOL;h.require(np.max(np.abs(v-bad))>VTOL,'corrupted vector check')
            scalarerrors={}
            for mode,pp,yy in[('last',p,y),('average',pa,ya)]:
                metrics=diagnostics(A,b,offsets,q,pp,yy);h.require(gpu[mode]['primal_upper']is None,'false upper label')
                scalarerrors[mode]={k:abs(v-gpu[mode][k])for k,v in metrics.items()};h.require(max(scalarerrors[mode].values())<=STOL,'scalar parity')
                h.require(np.min(pp)>=0 and metrics['simplex_Linf']<1e-9 and np.max(abs(yy[:q]))<=1,'CPU domain')
            np.savez_compressed(OUT/f'{name}_{iteration}_cpu.npz',**vectors)
            checks.append(dict(iteration=iteration,vector_absolute_Linf_errors=errors,scalar_absolute_errors=scalarerrors))
        if name=='unbounded_hard_dual':h.require(abs(y[1]-180)<VTOL and y[1]>1,'hard dual not clipped')
        records.append(dict(case=name,shape=list(A.shape),checkpoints=checks))
    for pth in(__file__,h.__file__,ROOT/'uv.lock',OUT/'preregistration.json'):bindings[h.key(pth)]=h.digest(pth)
    h.require(all(h.digest(ROOT/f)==v for f,v in bindings.items()),'immutable input end check')
    report=dict(status='INDEPENDENT_FULL_MOMENT_GPU_CPU_PARITY_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,inputs_sha256=bindings,records=records,vector_tolerance=VTOL,scalar_tolerance=STOL,projection_controls=projectioncontrols,corrupted_binary_inputs_rejected=rejected,corrupted_vector_controls=True,all_serialized_coefficients_mapped_to_prior_audited_model=True,producer_imported=False,method='Independent binary reader; exact sparse export/transpose comparison; NumPy/SciPy CPU updates with sort-based KKT simplex projection and arithmetic sums of iterates; every vector entry and diagnostic at all16case-checkpoints.',shared_components=['Python standard library','NumPy/SciPy numerical sparse multiplication','prior independent artifact hashing helper and exact model audit','tqdm'],limitations=['Numerical engineering parity on exactly four100iteration inputs only.','No floating score is a graph, exact certificate, primal upper bound, or mathematical resolution.','No claim about six-coordinate behavior, arbitrary iteration counts, certified floating error, or speedup.'],output_sha256={p.name:h.digest(p)for p in OUT.glob('*_cpu.npz')})
    path=OUT/'summary.json'
    with path.open('x')as f:json.dump(report,f,indent=2)
    print(report['status'],h.digest(path))
if __name__=='__main__':main()
