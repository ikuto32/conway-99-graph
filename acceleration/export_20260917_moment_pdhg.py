"""Export new soft-moment/hard-reciprocity PDHG pilots, without old-star flags."""
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[name]='1'
import argparse
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import platform
import struct
import subprocess
import sys
import numpy as np
import scipy
from scipy.sparse import csr_matrix,load_npz,vstack,eye,hstack

ROOT=Path(__file__).resolve().parents[1]
CHECKPOINTS=[1,2,10,100]
MODEL='acceleration/results/20260917_two_matching_moments'
GATES={
 'acceleration/results/20260917_independent_review/two_matching_moments.json':'5af1f353a70a16fc5f915195b911d782e360ffc0690463936b7a9dea983197ed',
 'acceleration/results/20260917_independent_review/two_matchings/summary.json':'f3d2ba90be5e8c27bc64c2e4941174d36fc3ddfcbc29ce25da872df652383acb'}
def digest(p):return sha256(Path(p).read_bytes()).hexdigest()
def save(p,value):
 with p.open('x',encoding='utf-8') as f:json.dump(value,f,indent=2);f.write('\n')
def pack(A,b,offsets,q,out):
 A=csr_matrix(A,dtype=np.float64);A.sum_duplicates();A.eliminate_zeros();A.sort_indices();T=A.T.tocsr();T.sort_indices()
 m,n=A.shape;offsets=np.asarray(offsets);b=np.asarray(b,dtype=np.float64)
 assert 0<n<=1000000 and 0<m<=10000 and 0<=q<=m and A.nnz<=100000000
 assert offsets[0]==0 and offsets[-1]==n and np.all(np.diff(offsets)>0) and max(np.diff(offsets))<=100000
 assert np.isfinite(A.data).all() and np.isfinite(b).all() and b.shape==(m,)
 arrays=[('offsets',offsets,'<u4'),('A_rowptr',A.indptr,'<u4'),('A_indices',A.indices,'<u4'),('A_values',A.data,'<f8'),
 ('AT_rowptr',T.indptr,'<u4'),('AT_indices',T.indices,'<u4'),('AT_values',T.data,'<f8'),('b',b,'<f8')]
 positions={}
 with out.open('xb') as f:
  f.write(b'C99MHP01');f.write(struct.pack('<2I',1,len(CHECKPOINTS)));f.write(struct.pack('<4I',*CHECKPOINTS));f.write(struct.pack('<5I',n,m,q,len(offsets)-1,A.nnz))
  for name,a,dtype in arrays:
   value=np.asarray(a,dtype=dtype).tobytes();positions[name]={'offset':f.tell(),'bytes':len(value),'sha256':sha256(value).hexdigest()};f.write(value)
 return dict(path=out.relative_to(ROOT).as_posix(),sha256=digest(out),bytes=out.stat().st_size,n=n,m=m,q=q,blocks=len(offsets)-1,nnz=A.nnz,arrays=positions)
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);args=parser.parse_args();out=ROOT/args.out
 assert not out.exists();out.mkdir(parents=True)
 bindings={}
 for p,h in GATES.items():assert digest(ROOT/p)==h;bindings[p]=h
 gate=json.loads((ROOT/next(iter(GATES))).read_bytes());assert gate['status']=='INDEPENDENT_TWO_COORDINATE_FULL_MOMENT_MODEL_PASS'
 for name in ('model.json','integer_augmented_csr.npz'):
  p=MODEL+'/'+name;assert digest(ROOT/p)==gate['inputs_sha256'][p];bindings[p]=digest(ROOT/p)
 meta=json.loads((ROOT/MODEL/'model.json').read_bytes());C=load_npz(ROOT/MODEL/'integer_augmented_csr.npz').tocsr()
 offsets=meta['probability_offsets'];n=offsets[-1];hard=84+len(meta['unknown_edges']);q=3486
 assert C.shape==(hard+q,n+2*q) and hard==1884 and n==89308
 # Independently explicit extraction checks: simplex rows, slack signs, zero hard RHS.
 for u,(lo,hi) in enumerate(zip(offsets,offsets[1:])):
  row=C.getrow(u);assert np.array_equal(row.indices,np.arange(lo,hi)) and np.all(row.data==1)
 assert C[:hard,n:].nnz==0
 expected=hstack((-eye(q,dtype=np.int64),eye(q,dtype=np.int64)),format='csr');assert (C[hard:,n:]!=expected).nnz==0
 rhs=np.asarray(meta['rhs']);assert np.all(rhs[:84]==1) and np.all(rhs[84:hard]==0)
 A=vstack((C[hard:,:n],C[84:hard,:n]),format='csr');b=np.r_[rhs[hard:],rhs[84:hard]]
 records={}
 records['two_coordinate']=pack(A,b,offsets,q,out/'two_coordinate.bin')
 records['positive_uniform']=pack([[0,2],[1,-1]],[1,0],[0,2],1,out/'positive_uniform.bin')
 records['unbounded_hard_dual']=pack([[0],[1]],[0,-1],[0,1],1,out/'unbounded_hard_dual.bin')
 # Large-domain projection mechanics only; no graph interpretation.
 records['large_uniform']=pack(csr_matrix((1,45882)),[0],[0,45882],1,out/'large_uniform.bin')
 for p in (Path(__file__),ROOT/'acceleration/moment_pdhg_gpu.cu',ROOT/'acceleration/build_moment_pdhg_gpu.ps1',ROOT/'uv.lock',ROOT/'docs/NEXT_20260917_MOMENT_PDHG_GPU.md'):
  bindings[p.relative_to(ROOT).as_posix()]=digest(p)
 save(out/'manifest.json',dict(status='CANDIDATE_FULL_MOMENT_PDHG_PILOT_EXPORT',timestamp=datetime.now(timezone.utc).isoformat(),
  source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(Path.cwd()),
  python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,inputs_sha256=bindings,records=records,
  magic='C99MHP01',checkpoints=CHECKPOINTS,row_order='3486 soft moments then1800 hard reciprocity;84 simplex rows removed and represented by projection',
  objective='L1 moment residual subject to exact reciprocity and probability simplices',
  steps='eta=.9; sigma=.9/max(1,row_abs_sum); tau per simplex=.9/max(1,maximum column_abs_sum)',
  initialization='uniform per simplex; zero duals; pbar=p; arithmetic running averages of iterates1..k',
  projection='max shift; clamp inactive shifted tails at-1;60 fixed bisections[-1,0];256thread binary-tree sum; no sort',
  restrictions='Only three synthetic cases and existing two-coordinate model100iterations. Six-coordinate launch prohibited pending independent CPU parity.',
  numerical_scores_are_proofs=False,domain_enumerations=0,LP_solves=0,GPU_launches=0))
 print(json.dumps({'manifest_sha256':digest(out/'manifest.json'),'records':{k:{x:r[x] for x in ('n','m','nnz','bytes')} for k,r in records.items()}}))
if __name__=='__main__':main()
