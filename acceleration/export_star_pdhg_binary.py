"""Export audited complete star models to strict little-endian C99SCP01.

Header: magic[8], u32 count, u32 checkpoint_count, u32 checkpoints[].
Per model: u32 N,M,Q,blocks,nnz; u32 offsets[blocks+1];
CSR A rowptr[M+1],indices[nnz] (u32),values[nnz] (f64);
CSR AT rowptr[N+1],indices[nnz] (u32),values[nnz] (f64); f64 b[M].
All CSR rows are sorted and duplicate-free. Native steps are derived from
absolute row/column sums with eta=.9 and one tau per simplex. Cold starts only.
"""
import os
for _name in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS'):
    os.environ[_name]='1'
import argparse
from hashlib import sha256
import json
import math
from pathlib import Path
import struct
import numpy as np
import scipy
from star_marginal_cp_cpu_v2 import build_model, diagonal_steps, numeric_bounds

ROOT=Path(__file__).resolve().parents[1]
HELPER_SHA='6a2823692dfb0baab9b0fdb011f84c6fdda82361d9af01433260020cb19ae65d'
CONVENTION='X_UV_FROM_SMALLER_CURRENT_OUTER_INDEX;RECIPROCITY_SMALLER_MINUS_LARGER'
MAGIC=b'C99SCP01'

def path(p):
    return (ROOT/str(p).replace('\\','/')).resolve()

def key(p):
    return path(p).relative_to(ROOT).as_posix()

def digest(p):
    return sha256(path(p).read_bytes()).hexdigest()

def require(ok,msg):
    if not ok:
        raise ValueError(msg)

def little(array,kind):
    values=np.asarray(array)
    if kind=='<u4':
        require(np.all(values>=0) and np.all(values<=2**32-1) and np.all(values==values.astype(np.uint64)),'Invalid u32 array')
    else:
        require(kind=='<f8' and np.all(np.isfinite(values)),'Invalid f64 array')
    return values.astype(kind,copy=False).tobytes(order='C')

def pack_model(model,Q=1680):
    A=model['A'].copy();AT=model['AT'].copy()
    A.sum_duplicates();A.sort_indices();AT.sum_duplicates();AT.sort_indices()
    M,N=A.shape; blocks=len(model['offsets'])-1; nnz=A.nnz
    require(0<N<=100000 and 0<M<=20000 and 0<=Q<=M and 0<blocks<=128 and 0<nnz<=8000000,'Model limit')
    require(AT.shape==(N,M) and AT.nnz==nnz and A.has_canonical_format and AT.has_canonical_format,'Noncanonical matrices')
    trans=A.transpose().tocsr();trans.sort_indices()
    require(np.array_equal(trans.indptr,AT.indptr) and np.array_equal(trans.indices,AT.indices) and np.array_equal(trans.data,AT.data),'Not exact transpose')
    offsets=np.asarray(model['offsets'])
    require(offsets[0]==0 and offsets[-1]==N and np.all(np.diff(offsets)>0) and np.max(np.diff(offsets))<=8192,'Invalid simplex offsets')
    require(np.all(A.data!=0) and model['b'].shape==(M,),'Invalid zero coefficient/target shape')
    arrays=[('offsets',offsets,'<u4'),('A_rowptr',A.indptr,'<u4'),('A_indices',A.indices,'<u4'),('A_values',A.data,'<f8'),
            ('AT_rowptr',AT.indptr,'<u4'),('AT_indices',AT.indices,'<u4'),('AT_values',AT.data,'<f8'),('b',model['b'],'<f8')]
    chunks=[struct.pack('<5I',N,M,Q,blocks,nnz)]
    positions={};cursor=20
    for label,array,kind in arrays:
        payload=little(array,kind)
        positions[label]=dict(relative_byte_offset=cursor,byte_length=len(payload),sha256=sha256(payload).hexdigest(),dtype=kind)
        chunks.append(payload);cursor+=len(payload)
    tau,sigma=diagonal_steps(model)
    metadata=dict(N=N,M=M,Q=Q,blocks=blocks,nnz=nnz,byte_length=cursor,arrays=positions,
                  offsets=offsets.tolist(),row_abs_sum_max=float(max(model['row_sums'])),col_abs_sum_max=float(max(model['col_sums'])),
                  block_tau=[float(tau[start]) for start in offsets[:-1]],sigma_f64le_sha256=sha256(little(sigma,'<f8')).hexdigest(),
                  canonical_sorted_unique_CSR=True,exact_transpose=True,eta=.9,theta=1)
    return b''.join(chunks),metadata

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--phase',action='append',required=True)
    p.add_argument('--audit',action='append',required=True)
    p.add_argument('--helper-qa',required=True)
    p.add_argument('--checkpoints',default='1,2,10,500,2000')
    p.add_argument('--out',required=True)
    a=p.parse_args()
    out=path(a.out)
    require(not out.exists(),'Fresh output required')
    require(len(a.phase)==len(a.audit) and 1<=len(a.phase)<=256,'Matching phase/audit count1..256 required')
    checkpoints=list(map(int,a.checkpoints.split(',')))
    require(1<=len(checkpoints)<=16 and checkpoints==sorted(set(checkpoints)) and all(1<=i<=20000 for i in checkpoints),'Invalid checkpoint list')
    bindings={}
    def bind(p,expected=None):
        h=digest(p);name=key(p)
        require(expected is None or h==expected,'Changed bound file '+name)
        require(name not in bindings or bindings[name]==h,'Conflicting hash '+name)
        bindings[name]=h
        return h
    def load(p):
        bind(p)
        d=json.loads(path(p).read_bytes())
        for name,h in d.get('inputs_sha256',{}).items():bind(name,h)
        return d
    bind(__file__);bind(ROOT/'acceleration/audit_certificate.py')
    bind(ROOT/'acceleration/star_marginal_cp_cpu_v2.py',HELPER_SHA)
    qa=load(a.helper_qa)
    require(qa['status']=='STAR_SIMPLEX_PDHG_CPU_V2_REFERENCE_WARM_TRANSFER_AND_BOUNDED_QUALITY_CONTROLS_PASS','Missing helper QA')
    require({key(p):h for p,h in qa['inputs_sha256'].items()}.get('acceleration/star_marginal_cp_cpu_v2.py')==HELPER_SHA,'Helper QA association')
    chunks=[MAGIC,struct.pack('<2I',len(a.phase),len(checkpoints)),struct.pack('<'+'I'*len(checkpoints),*checkpoints)]
    cursor=sum(map(len,chunks));cases=[];signatures=set()
    for phase_path,audit_path in zip(a.phase,a.audit):
        phase,audit=load(phase_path),load(audit_path)
        require(audit['status']=='INDEPENDENT_EXACT_STAR_MARGINAL_PHASE1_AUDIT_PASS','Missing exact star audit')
        ab={key(p):h for p,h in audit['inputs_sha256'].items()}
        require(ab.get(key(phase_path))==digest(phase_path),'Audit phase association')
        require(phase['projection_convention']==CONVENTION and phase['original_complete_domains_used'] and not phase['pair_pruned_domains_used'],'Wrong model projection/domain scope')
        for field in ('candidate','domains','domain_audit'):bind(phase[field+'_path'],phase[field+'_sha256'])
        require(ab.get(key(phase['candidate_path']))==phase['candidate_sha256'],'Audit candidate association')
        candidate=load(phase['candidate_path']);stars=load(phase['domains_path']);proof=load(phase['domain_audit_path'])
        signature=tuple(map(tuple,sorted(candidate['overlap_edges_outer_zero_based'])))
        require(signature not in signatures,'Repeated exact candidate');signatures.add(signature)
        require(stars['complete_domain_enumeration'] is True and len(stars['domains'])==84 and all(r['status']=='COMPLETE' for r in stars['domains']),'Incomplete original stars')
        require(proof['status']=='INDEPENDENT_EXACT_PAIR_DOMAIN_AUDIT_PASS' and proof['complete_used_domains_verified'],'Missing independent original domains')
        pb={key(p):h for p,h in proof['inputs_sha256'].items()}
        require(pb.get(key(phase['candidate_path']))==phase['candidate_sha256'] and pb.get(key(phase['domains_path']))==phase['domains_sha256'],'Independent domain association')
        require([r['outer_vertex'] for r in proof['independently_reenumerated_domains']]==list(range(84)),'Missing independent domain rows')
        counts=[len(r['domain_masks_hex']) for r in stars['domains']]
        require(counts==phase['domain_counts']==[r['domain_size'] for r in proof['independently_reenumerated_domains']] and all(counts),'Wrong complete domain counts')
        model=build_model(candidate,stars['domains'])
        require(model['counts'].tolist()==counts and model['A'].nnz+model['A'].shape[1]==phase['matrix_nonzeros'],'Model/source dimensions differ')
        savedp=np.asarray(phase['numeric_probabilities'],dtype=float)
        savedy=np.r_[phase['numeric_reciprocity_duals'],phase['numeric_cap_duals']]
        require(savedp.shape==(model['A'].shape[1],) and savedy.shape==(5166,) and np.all(np.isfinite(savedp)) and np.all(np.isfinite(savedy)),'Bad saved reference vectors')
        check=numeric_bounds(model,savedp,savedy)
        error=max(abs(check['primal_upper_numeric']-phase['numeric_objective']),abs(check['dual_lower_numeric']-phase['numeric_simplex_dual_lower']))
        require(error<1e-8,'Reference model parity failed')
        payload,metadata=pack_model(model)
        cases.append(dict(index=len(cases),phase_path=key(phase_path),phase_sha256=digest(phase_path),audit_path=key(audit_path),audit_sha256=digest(audit_path),
                          candidate_path=key(phase['candidate_path']),candidate_sha256=phase['candidate_sha256'],domains_path=key(phase['domains_path']),domains_sha256=phase['domains_sha256'],
                          domain_audit_path=key(phase['domain_audit_path']),domain_audit_sha256=phase['domain_audit_sha256'],
                          record_byte_offset=cursor,record_sha256=sha256(payload).hexdigest(),reference_numeric_error=error,**metadata))
        chunks.append(payload);cursor+=len(payload)
    require(all(digest(p)==h for p,h in bindings.items()),'Input changed during export preparation')
    out.mkdir(parents=True)
    binary=out/'input.bin'
    with binary.open('xb') as f:
        for chunk in chunks:f.write(chunk)
    manifest=dict(status='AUDITED_COLD_STAR_PDHG_BINARY_EXPORTED',inputs_sha256=bindings,binary_path=key(binary),binary_sha256=digest(binary),binary_bytes=cursor,
                  magic='C99SCP01',byte_order='little',integer_dtype='uint32',real_dtype='float64',candidate_count=len(cases),checkpoints=checkpoints,cases=cases,
                  model_rows='1680 lexicographic disjoint-edge reciprocity rows followed by3486 lexicographic outer-pair caps',
                  model_columns='Original complete star masks, outer vertex0..83, saved sorted masks within each vertex',
                  initialization='Each probability simplex uniform; y=0; pbar=p; averages start atzero beforeiteration1',
                  step_rule='eta=.9; sigma_i=eta/max(1,row_abs_sum_i); tau_j=eta/max(1,max col_abs_sum in its simplex); theta=1',
                  numpy_version=np.__version__,scipy_version=scipy.__version__,LP_runs=0,domain_enumerations=0,GPU_runs=0,exclusion_claims=0)
    with (out/'manifest.json').open('x',encoding='utf-8') as f:json.dump(manifest,f,indent=2);f.write('\n')
    print(json.dumps(dict(status=manifest['status'],candidate_count=len(cases),bytes=cursor,manifest_sha256=digest(out/'manifest.json'))))

if __name__=='__main__':main()
