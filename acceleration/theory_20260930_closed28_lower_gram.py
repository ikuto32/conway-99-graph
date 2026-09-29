"""Cheap complementary A+4I eigenvalue screen; numerical results are not proofs."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
from datetime import datetime,timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import time
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'acceleration/results/20260930_closed28_lower_gram'
def h(p):return sha256(p.read_bytes()).hexdigest()
def save(p,v):
    with p.open('x',encoding='utf-8')as f:json.dump(v,f,indent=2)

def main():
    OUT.mkdir(exist_ok=False)
    files=sorted((ROOT/'acceleration/results/20260930_closed28_sos').glob('center_*.json'));assert len(files)==84
    manifest=dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(Path.cwd()),
        question='Do any of the frozen closed28 matching-specific graphs violate the complementary necessary lower Gram condition A+4I PSD?',
        scope='Exactly all 2688 raw graphs in the frozen 84-file screen; no all-matching or star exclusion follows.',selection='All 84 files and all 32 saved cases per file in file order; no selection by earlier scores.',
        negative_signal_threshold=-1e-8,resource_limit_seconds=60,success='A negative eigenvalue signal triggers a separately preserved exact certificate investigation, never automatic promotion.',
        numerical_zero_is_certificate=False,inputs_sha256={p.relative_to(ROOT).as_posix():h(p) for p in files},source_sha256=h(Path(__file__)),numpy=np.__version__)
    save(OUT/'manifest.json',manifest)
    # A known positive windmill and an exactly negative star validate the screen.
    a=np.zeros((15,15),dtype=np.int64)
    for j in range(1,15):a[0,j]=a[j,0]=1
    for j in range(1,15,2):a[j,j+1]=a[j+1,j]=1
    assert np.linalg.eigvalsh(a+4*np.eye(15))[0]>0
    bad=np.zeros((18,18),dtype=np.int64);bad[0,1:]=bad[1:,0]=1
    w=np.array([-4]+[1]*17,dtype=np.int64);assert int(w@(bad+4*np.eye(18,dtype=np.int64))@w)==-4
    assert np.linalg.eigvalsh(bad+4*np.eye(18))[0]<-1e-8
    save(OUT/'controls.json',dict(windmill_positive=True,star18_negative_signal=True,star18_exact_integer_quadratic=-4))
    start=time.monotonic();records=[];signals=[];minimum=None;attempted=0
    for path in files:
        data=json.loads(path.read_bytes());assert len(data['cases'])==32
        batch=[]
        for case in data['cases']:
            if time.monotonic()-start>=60:break
            rows=[int(x,16) for x in case['adjacency_rows_hex']]
            a=np.array([[(r>>j)&1 for j in range(28)] for r in rows],dtype=np.int64)
            assert np.array_equal(a,a.T) and not np.diag(a).any()
            values=np.linalg.eigvalsh(a+4*np.eye(28));lo=float(values[0]);attempted+=1
            minimum=lo if minimum is None else min(minimum,lo)
            row=dict(outer_vertex=case['outer_vertex'],original_id=case['original_id'],minimum_eigenvalue=lo,negative_signal=lo<-1e-8)
            batch.append(row)
            if row['negative_signal']:
                signals.append(row)
                if len(signals)==1:save(OUT/'first_negative_raw.json',case)
        records.extend(batch)
        save(OUT/path.name,dict(source_sha256=h(path),records=batch))
        if len(batch)<32:break
    save(OUT/'summary.json',dict(status='CANDIDATE_NUMERICAL_LOWER_GRAM_SCREEN',timestamp=datetime.now(timezone.utc).isoformat(),attempted=attempted,population=2688,unattempted=2688-attempted,negative_signals=len(signals),minimum_numeric=minimum,exact_negative_certificates=0,numerical_threshold=-1e-8,elapsed_seconds=time.monotonic()-start,independent_check_pending=True,target_resolution=False))
    print(json.dumps(dict(attempted=attempted,signals=len(signals),minimum_numeric=minimum,exact_negative_certificates=0)))

if __name__=='__main__':main()
