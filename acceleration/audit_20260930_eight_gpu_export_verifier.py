"""Memory-mapped exact export audit; no GPU launch or numerical iteration replay."""
import os
for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[name]='1'
from datetime import datetime,timezone
from hashlib import sha256
import json,sys,struct,subprocess,platform,argparse,time
from pathlib import Path
import numpy as np
import scipy
from scipy.sparse import load_npz,vstack
import audit_20260917_partial_matching as h
import audit_20260917_moment_pdhg_gpu_cpu_parity_v2 as calibrated
ROOT=h.ROOT;OUT=ROOT/'acceleration/results/20260930_independent_review'
def digest(path):
    value=sha256()
    with Path(path).open('rb')as f:
        while b:=f.read(1000003):value.update(b)
    return value.hexdigest()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--model-gate-sha256',required=True);args=parser.parse_args()
    started=datetime.now(timezone.utc).isoformat();tick=time.monotonic();head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();bindings={}
    for path in(__file__,h.__file__,calibrated.__file__,ROOT/'uv.lock'):bindings[h.key(path)]=digest(path)
    def read(p):bindings[h.key(p)]=digest(p);return json.loads(p.read_bytes())
    manifest=read(ROOT/'acceleration/results/20260930_eight_moment_pdhg/export/manifest.json')
    gatepath=OUT/'eight_filtered_moments/summary.json';gate=read(gatepath)
    h.require(digest(gatepath)==args.model_gate_sha256 and gate['status']=='INDEPENDENT_EIGHT_COORDINATE_FILTERED_FULL_MOMENT_MODEL_PASS','exact model gate')
    for f,v in gate['inputs_sha256'].items():h.require(digest(ROOT/f)==v,'model gate input identity');bindings[f]=v
    paritypath=ROOT/'acceleration/results/20260917_independent_review/moment_pdhg_gpu_cpu_parity_v2/summary.json';parity=read(paritypath)
    h.require(digest(paritypath)=='c0ae24550c1f33c1d808107f7aaa9bf49d83d968805f2691a26388b777e2aaf2'and parity['status']=='INDEPENDENT_FULL_MOMENT_GPU_CPU_PARITY_PASS','numerical pilot gate')
    for f,v in manifest['inputs_sha256'].items():h.require(digest(ROOT/f)==v,'manifest binding');bindings[f]=v
    for f in('acceleration/moment_pdhg_gpu.cu','acceleration/build/moment_pdhg_gpu.exe'):
        h.require(manifest['inputs_sha256'][f]==parity['inputs_sha256'][f],'same checked CUDA source/executable')
    model=ROOT/'acceleration/results/20260930_eight_filtered_moments/run01';meta=read(model/'model.json')
    for name in('model.json','integer_augmented_csr.npz'):
        key=h.key(model/name);h.require(digest(model/name)==gate['inputs_sha256'][key],'audited model identity');bindings[key]=digest(model/name)
    C=load_npz(model/'integer_augmented_csr.npz');h.require(C.shape==(5730,1882186) and list(C.shape)==gate['shape'] and C.nnz==gate['nonzeros'],'source geometry')
    nnz=C.nnz-1875214-6972;h.require(0<nnz<2**32,'derived operator nonzero count')
    binary=ROOT/manifest['binary_path'];bindings[h.key(binary)]=digest(binary)
    h.require(bindings[h.key(binary)]==manifest['binary_sha256'] and binary.stat().st_size==manifest['binary_bytes'],'binary identity')
    with binary.open('rb')as f:header=f.read(48)
    h.require(header[:8]==b'C99MHP01','magic');nums=struct.unpack('<10I',header[8:]);h.require(nums==(1,3,1000,5000,10000,1875214,5646,3486,84,nnz),'exact header/checkpoints')
    layout=[('offsets','<u4',85),('A_rowptr','<u4',5647),('A_indices','<u4',nnz),('A_values','<f8',nnz),('AT_rowptr','<u4',1875215),('AT_indices','<u4',nnz),('AT_values','<f8',nnz),('b','<f8',5646)]
    arrays={};pos=48
    for name,dtype,count in layout:
        a=np.memmap(binary,dtype=dtype,mode='r',offset=pos,shape=(count,));value=sha256()
        for j in range(0,count,100003):value.update(a[j:j+100003].tobytes())
        h.require(manifest['arrays'][name]==dict(offset=pos,bytes=a.nbytes,dtype=dtype,sha256=value.hexdigest()),'independent sequential array layout/hash');arrays[name]=a;pos+=a.nbytes
    h.require(pos==binary.stat().st_size,'no trailing or missing bytes')
    offsets=meta['probability_offsets'];h.require(np.array_equal(arrays['offsets'],offsets)and manifest['probability_offsets']==offsets and offsets[-1]==1875214 and len(offsets)==85 and 0<min(np.diff(offsets)) and max(np.diff(offsets))<=100000 and max(np.diff(offsets))==manifest['max_domain'],'all domain offsets')
    n=1875214;hard=2244
    for u,(a,z)in enumerate(zip(offsets,offsets[1:])):
        r=C.getrow(u);h.require(np.array_equal(r.indices,np.arange(a,z))and np.all(r.data==1),'omitted simplex identity')
    h.require(C[:hard,n:].nnz==0,'no hard slacks')
    slacks=C[hard:,n:].tocsc()
    for j in range(6972):
        a,z=slacks.indptr[j:j+2];h.require(z-a==1 and slacks.indices[a]==j%3486 and slacks.data[a]==(-1 if j<3486 else 1),'omitted slack identity')
    expected=vstack([C[hard:,:n],C[84:hard,:n]],format='csr');expected.sum_duplicates();expected.sort_indices();T=expected.T.tocsr();T.sum_duplicates();T.sort_indices()
    def equal(observed,wanted):
        h.require(len(observed)==len(wanted),'array count')
        for j in range(0,len(wanted),100003):h.require(np.array_equal(observed[j:j+100003],wanted[j:j+100003]),'exact every exported entry')
    for prefix,matrix in [('A',expected),('AT',T)]:
        for suffix,attr in[('rowptr','indptr'),('indices','indices'),('values','data')]:equal(arrays[prefix+'_'+suffix],getattr(matrix,attr))
    rhs=np.array(meta['rhs']);h.require(np.all(rhs[:84]==1)and np.all(rhs[84:hard]==0),'omitted simplex/hard RHS');equal(arrays['b'],np.r_[rhs[hard:],rhs[84:hard]])
    h.require(expected.shape==(5646,1875214)and expected.nnz==nnz and manifest['shape']==list(expected.shape)and manifest['q']==3486 and manifest['nnz']==nnz and manifest['blocks']==84 and manifest['checkpoints']==[1000,5000,10000],'retained geometry')
    controls=[]
    pilot=ROOT/'acceleration/results/20260917_moment_pdhg_gpu/pilot'
    fixtures=read(ROOT/'acceleration/results/20260917_moment_pdhg_gpu/export/manifest.json')
    fixture=fixtures['records']['positive_uniform'];positive=ROOT/fixture['path'];bindings[h.key(positive)]=digest(positive)
    h.require(bindings[h.key(positive)]==fixture['sha256'],'calibration positive identity')
    pA,pb,po,pq,pc=calibrated.decode(positive.read_bytes())
    h.require(np.array_equal(pA.toarray(),[[0,2],[1,-1]]) and list(pb)==[1,0] and list(po)==[0,2] and pq==1,'known-valid decoder fixture');controls.append('known_valid_positive_uniform')
    for name in('bad_magic','bad_transpose','domain_out_of_range','trailing_bytes'):
        path=pilot/f'{name}.bin';bindings[h.key(path)]=digest(path)
        try:calibrated.decode(path.read_bytes())
        except(ValueError,AssertionError,RuntimeError,struct.error):controls.append(name)
        else:raise AssertionError('corrupt parser input accepted')
    # A copied first row is enough to calibrate exact comparison's corruption veto.
    for field in('A_indices','A_values','AT_values','b'):
        a=np.array(arrays[field][:10]);bad=a.copy();bad[0]+=1
        try:equal(a,bad)
        except ValueError:controls.append(field+'_entry_corruption')
        else:raise AssertionError('corrupted coefficient accepted')
    h.require(all(digest(ROOT/f)==v for f,v in bindings.items()),'stable inputs')
    report=dict(status='INDEPENDENT_EIGHT_COORDINATE_GPU_EXPORT_MAPPING_PASS',started_at=started,timestamp=datetime.now(timezone.utc).isoformat(),elapsed_seconds=time.monotonic()-tick,source_commit=head,verifier='/root/state_literature_audit independent checking agent',verification_type='Independent complete engineering mapping check',command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,inputs_sha256=bindings,shape=list(expected.shape),nonzeros=expected.nnz,probability_columns=n,soft_rows=3486,hard_rows=2160,probability_blocks=84,all_operator_transpose_offsets_rhs_checked=True,omitted_simplex_and_slack_identities_checked=True,checkpoints=[1000,5000,10000],binary_path=h.key(binary),binary_sha256=bindings[h.key(binary)],artifact_availability='LOCAL_ONLY',retrieval=manifest['retrieval'],controls=controls,producer_imported=False,new_numerical_iteration_replay=False,GPU_launched=False,method='Sequential independent binary layout and memory-mapped arrays; complete exact source row/column extraction and transpose comparison to hash-bound independently reconstructed integer model.',shared_components=['Python standard library','NumPy/SciPy exact sparse operations','previous independent binary parser for corruption controls','prior independently audited eight moment model and four-case CPU parity'],limitations=['Engineering mapping check only; no new numerical performance, convergence, certificate, or target-level mathematical result.','Earlier CPU parity applies to its recorded pilot cases; this does not claim CPU parity for eight-coordinate iterations.'])
    path=OUT/'eight_gpu_export_verifier.json'
    with path.open('x')as f:json.dump(report,f,indent=2)
    print(report['status'],digest(path))
if __name__=='__main__':main()
