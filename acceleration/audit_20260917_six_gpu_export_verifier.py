"""Memory-mapped exact export audit; no GPU launch or numerical iteration replay."""
import os
for name in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[name]='1'
from datetime import datetime,timezone
from hashlib import sha256
import json,sys,struct,subprocess,platform
from pathlib import Path
import numpy as np
import scipy
from scipy.sparse import load_npz,vstack
import audit_20260917_partial_matching as h
import audit_20260917_moment_pdhg_gpu_cpu_parity_v2 as calibrated
ROOT=h.ROOT;OUT=ROOT/'acceleration/results/20260917_independent_review'
def digest(path):
    value=sha256()
    with Path(path).open('rb')as f:
        while b:=f.read(1000003):value.update(b)
    return value.hexdigest()
def main():
    bindings={}
    def read(p):bindings[h.key(p)]=digest(p);return json.loads(p.read_bytes())
    manifest=read(ROOT/'acceleration/results/20260917_six_moment_pdhg/export/manifest.json')
    gatepath=OUT/'six_filtered_moments.json';gate=read(gatepath)
    h.require(digest(gatepath)=='f27467b03a34fe3ea3adec4e537585e71d5697f4e63562cdd43d7e6822c8f3e7','exact model gate')
    paritypath=OUT/'moment_pdhg_gpu_cpu_parity_v2/summary.json';parity=read(paritypath)
    h.require(digest(paritypath)=='c0ae24550c1f33c1d808107f7aaa9bf49d83d968805f2691a26388b777e2aaf2'and parity['status']=='INDEPENDENT_FULL_MOMENT_GPU_CPU_PARITY_PASS','numerical pilot gate')
    for f,v in manifest['inputs_sha256'].items():h.require(digest(ROOT/f)==v,'manifest binding');bindings[f]=v
    for f in('acceleration/moment_pdhg_gpu.cu','acceleration/build/moment_pdhg_gpu.exe'):
        h.require(manifest['inputs_sha256'][f]==parity['inputs_sha256'][f],'same checked CUDA source/executable')
    model=ROOT/'acceleration/results/20260917_six_filtered_moments';meta=read(model/'model.json')
    for name in('model.json','integer_augmented_csr.npz'):
        key=h.key(model/name);h.require(digest(model/name)==gate['inputs_sha256'][key],'audited model identity');bindings[key]=digest(model/name)
    C=load_npz(model/'integer_augmented_csr.npz');h.require(C.shape==(5610,719693)and C.nnz==59380799,'source geometry')
    binary=ROOT/manifest['binary_path'];bindings[h.key(binary)]=digest(binary)
    h.require(bindings[h.key(binary)]==manifest['binary_sha256']=='e9d2f28a3804ffe5473eb6f86bcb6a3a97d492940c413eaa6de5c028c8e34b1b'and binary.stat().st_size==manifest['binary_bytes']==1410784136,'binary identity')
    with binary.open('rb')as f:header=f.read(48)
    h.require(header[:8]==b'C99MHP01','magic');nums=struct.unpack('<10I',header[8:]);h.require(nums==(1,3,1000,5000,10000,712721,5526,3486,84,58661106),'exact header/checkpoints')
    layout=[('offsets','<u4',85),('A_rowptr','<u4',5527),('A_indices','<u4',58661106),('A_values','<f8',58661106),('AT_rowptr','<u4',712722),('AT_indices','<u4',58661106),('AT_values','<f8',58661106),('b','<f8',5526)]
    arrays={};pos=48
    for name,dtype,count in layout:
        a=np.memmap(binary,dtype=dtype,mode='r',offset=pos,shape=(count,));value=sha256()
        for j in range(0,count,100003):value.update(a[j:j+100003].tobytes())
        h.require(manifest['arrays'][name]==dict(offset=pos,bytes=a.nbytes,dtype=dtype,sha256=value.hexdigest()),'independent sequential array layout/hash');arrays[name]=a;pos+=a.nbytes
    h.require(pos==binary.stat().st_size,'no trailing or missing bytes')
    offsets=meta['probability_offsets'];h.require(np.array_equal(arrays['offsets'],offsets)and manifest['probability_offsets']==offsets and offsets[-1]==712721 and len(offsets)==85 and max(np.diff(offsets))==37053,'all domain offsets')
    n=712721;hard=2124
    for u,(a,z)in enumerate(zip(offsets,offsets[1:])):
        r=C.getrow(u);h.require(np.array_equal(r.indices,np.arange(a,z))and np.all(r.data==1),'omitted simplex identity')
    h.require(C[:hard,n:].nnz==0,'no hard slacks')
    slacks=C[hard:,n:].tocsc()
    for j in range(6972):
        a,z=slacks.indptr[j:j+2];h.require(z-a==1 and slacks.indices[a]==j%3486 and slacks.data[a]==(-1 if j<3486 else 1),'omitted slack identity')
    expected=vstack([C[hard:,:n],C[84:hard,:n]],format='csr');expected.sort_indices();T=expected.T.tocsr();T.sort_indices()
    def equal(observed,wanted):
        h.require(len(observed)==len(wanted),'array count')
        for j in range(0,len(wanted),100003):h.require(np.array_equal(observed[j:j+100003],wanted[j:j+100003]),'exact every exported entry')
    for prefix,matrix in [('A',expected),('AT',T)]:
        for suffix,attr in[('rowptr','indptr'),('indices','indices'),('values','data')]:equal(arrays[prefix+'_'+suffix],getattr(matrix,attr))
    rhs=np.array(meta['rhs']);h.require(np.all(rhs[:84]==1)and np.all(rhs[84:hard]==0),'omitted simplex/hard RHS');equal(arrays['b'],np.r_[rhs[hard:],rhs[84:hard]])
    h.require(expected.shape==(5526,712721)and expected.nnz==58661106 and manifest['shape']==list(expected.shape)and manifest['q']==3486,'retained geometry')
    controls=[]
    pilot=ROOT/'acceleration/results/20260917_moment_pdhg_gpu/pilot'
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
    for path in(__file__,h.__file__,calibrated.__file__,ROOT/'uv.lock'):bindings[h.key(path)]=digest(path)
    h.require(all(digest(ROOT/f)==v for f,v in bindings.items()),'stable inputs')
    report=dict(status='INDEPENDENT_SIX_COORDINATE_GPU_EXPORT_MAPPING_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,inputs_sha256=bindings,shape=list(expected.shape),nonzeros=expected.nnz,probability_columns=n,soft_rows=3486,hard_rows=2040,probability_blocks=84,all_operator_transpose_offsets_rhs_checked=True,omitted_simplex_and_slack_identities_checked=True,checkpoints=[1000,5000,10000],binary_path=h.key(binary),binary_sha256=bindings[h.key(binary)],artifact_availability='LOCAL_ONLY',retrieval=manifest['retrieval'],controls=controls,producer_imported=False,new_numerical_iteration_replay=False,GPU_launched=False,method='Sequential independent binary layout and memory-mapped arrays; complete exact source row/column extraction and transpose comparison to hash-bound independently reconstructed integer model.',shared_components=['Python standard library','NumPy/SciPy exact sparse operations','previous independent binary parser for corruption controls','prior independently audited six moment model and four-case CPU parity'],limitations=['Engineering mapping check only; no new numerical performance, convergence, certificate, or target-level mathematical result.','Earlier CPU parity applies to its recorded pilot cases; this does not claim CPU parity for six-coordinate iterations.'])
    path=OUT/'six_gpu_export_verifier.json'
    with path.open('x')as f:json.dump(report,f,indent=2)
    print(report['status'],digest(path))
if __name__=='__main__':main()
