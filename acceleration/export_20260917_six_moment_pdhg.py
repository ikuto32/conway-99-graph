"""Deterministically recover a LOCAL_ONLY C99MHP01 six-coordinate input."""
import os
for _k in ('OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','OMP_NUM_THREADS'):os.environ[_k]='1'
import argparse
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import platform
import struct
import subprocess
import sys
import time
import numpy as np
import scipy
from scipy.sparse import load_npz,vstack,eye,hstack

ROOT=Path(__file__).resolve().parents[1]
MODEL='acceleration/results/20260917_six_filtered_moments'
REVIEW='acceleration/results/20260917_independent_review/six_filtered_moments.json'
REVIEW_SHA='f27467b03a34fe3ea3adec4e537585e71d5697f4e63562cdd43d7e6822c8f3e7'
PROTOCOL='docs/NEXT_20260917_SIX_MOMENT_PDHG.md'
CHECKPOINTS=[1000,5000,10000]
def digest(p):
 h=sha256()
 with Path(p).open('rb') as f:
  while b:=f.read(8<<20):h.update(b)
 return h.hexdigest()
def save(p,d):
 with p.open('x',encoding='utf-8') as f:json.dump(d,f,indent=2);f.write('\n')
def confined(p):
 p=(ROOT/p).resolve();assert p.is_relative_to(ROOT);return p
def load_checked_model():
 assert digest(ROOT/REVIEW)==REVIEW_SHA
 review=json.loads((ROOT/REVIEW).read_bytes());assert review['status']=='INDEPENDENT_SIX_COORDINATE_FILTERED_FULL_MOMENT_MODEL_PASS'
 bindings={REVIEW:REVIEW_SHA}
 for name in ('model.json','integer_augmented_csr.npz'):
  key=MODEL+'/'+name;assert digest(ROOT/key)==review['inputs_sha256'][key];bindings[key]=digest(ROOT/key)
 meta=json.loads((ROOT/MODEL/'model.json').read_bytes());C=load_npz(ROOT/MODEL/'integer_augmented_csr.npz').tocsr()
 assert C.shape==(5610,719693) and C.nnz==59380799 and np.all(np.isin(C.data,[-1,1]))
 offsets=meta['probability_offsets'];assert len(offsets)==85 and offsets[0]==0 and offsets[-1]==712721 and max(np.diff(offsets))<=45882
 assert len(meta['unknown_edges'])==2040 and len(meta['retained_original_domain_ids'])==84
 assert all(len(ids)==b-a for ids,a,b in zip(meta['retained_original_domain_ids'],offsets,offsets[1:]))
 for u,(a,b) in enumerate(zip(offsets,offsets[1:])):
  r=C.getrow(u);assert np.array_equal(r.indices,np.arange(a,b)) and np.all(r.data==1)
 hard=2124;n=712721;q=3486
 assert C[:hard,n:].nnz==0
 expected=hstack((-eye(q,dtype=np.int8),eye(q,dtype=np.int8)),format='csr');assert (C[hard:,n:]!=expected).nnz==0
 rhs=np.array(meta['rhs'],dtype=np.int64);assert np.all(rhs[:84]==1) and np.all(rhs[84:hard]==0)
 return meta,C,bindings
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--binary',required=True);a=p.parse_args()
 out=confined(a.out);binary=confined(a.binary);assert not out.exists() and not binary.exists()
 out.mkdir(parents=True);binary.parent.mkdir(parents=True,exist_ok=True)
 started=time.monotonic();meta,C,bindings=load_checked_model();load_seconds=time.monotonic()-started
 transform=time.monotonic();n=712721;q=3486;hard=2124
 A=vstack((C[hard:,:n],C[84:hard,:n]),format='csr');A.sum_duplicates();A.sort_indices();AT=A.T.tocsr();AT.sort_indices()
 assert A.shape==(5526,n) and A.nnz==58661106 and AT.has_canonical_format and A.has_canonical_format
 rhs=np.array(meta['rhs'],dtype=np.int64);b=np.r_[rhs[hard:],rhs[84:hard]];offsets=np.array(meta['probability_offsets'],dtype=np.int64)
 transform_seconds=time.monotonic()-transform;arrays={};write_started=time.monotonic()
 with binary.open('xb') as f:
  f.write(b'C99MHP01');f.write(struct.pack('<2I',1,3));f.write(struct.pack('<3I',*CHECKPOINTS));f.write(struct.pack('<5I',n,5526,q,84,A.nnz))
  for name,values,dtype in [('offsets',offsets,'<u4'),('A_rowptr',A.indptr,'<u4'),('A_indices',A.indices,'<u4'),('A_values',A.data,'<f8'),
    ('AT_rowptr',AT.indptr,'<u4'),('AT_indices',AT.indices,'<u4'),('AT_values',AT.data,'<f8'),('b',b,'<f8')]:
   begin=f.tell();h=sha256()
   for j in range(0,len(values),1<<20):
    block=np.asarray(values[j:j+(1<<20)],dtype=dtype).tobytes();f.write(block);h.update(block)
   arrays[name]=dict(offset=begin,bytes=f.tell()-begin,dtype=dtype,sha256=h.hexdigest())
 serialization_seconds=time.monotonic()-write_started
 for key in (Path(__file__).relative_to(ROOT).as_posix(),PROTOCOL,'acceleration/moment_pdhg_gpu.cu','acceleration/build/moment_pdhg_gpu.exe','uv.lock'):
  bindings[key]=digest(ROOT/key)
 binary_hash=digest(binary)
 record=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
  command=[sys.executable,*sys.argv],cwd=str(Path.cwd()),python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,
  status='PREPARED_SIX_COORDINATE_FULL_MOMENT_PDHG_EXPORT',inputs_sha256=bindings,model=meta['model'],model_scope='Exactly712721independently retained original IDs from six-coordinate family; no new enumeration/filtering',
  shape=list(A.shape),nnz=A.nnz,q=q,blocks=84,max_domain=int(max(np.diff(offsets))),checkpoints=CHECKPOINTS,
  probability_offsets=offsets.tolist(),retained_original_ids_binding=bindings[MODEL+'/model.json'],
  binary_path=binary.relative_to(ROOT).as_posix(),binary_sha256=binary_hash,binary_bytes=binary.stat().st_size,
  artifact_availability='LOCAL_ONLY',retrieval='Run this hash-bound exporter with fresh --out/--binary; restored audited NPZ uses existing chunk_manifest and generic restorer. Compare binary_sha256; JSON manifest timestamps/path may differ.',
  arrays=arrays,magic='C99MHP01',row_order='3486soft moments then2040hard reciprocal equalities',column_order=meta['column_order'].split(',3486')[0],
  initialization='cold uniform simplices and zero duals',steps='Frozen CUDA eta=.9 theta=1 diagonal steps; no tuning',
  timing=dict(model_hash_load_validation_seconds=load_seconds,operator_and_transpose_seconds=transform_seconds,serialization_seconds=serialization_seconds,total_export_seconds=time.monotonic()-started),
  GPU_launched=False,exact_certificates_attempted=0,numerical_scores_are_proofs=False)
 save(out/'manifest.json',record)
 print(json.dumps({k:record[k] for k in ('status','shape','nnz','binary_bytes','binary_sha256','timing')}))
if __name__=='__main__':main()
