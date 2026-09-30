"""Post-run exhaustive tiny calibration addendum; not independent review."""
from itertools import product
from pathlib import Path
from datetime import datetime,timezone
import argparse
import json
import hashlib
import numpy as np
from theory_20260930_triangle_modular_kernel import nullspace

ROOT=Path(__file__).resolve().parents[1]

def digest(p):
    with p.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    checked=[]
    for prime in(2,3):
        matrices=0;corruptions=0;vectors=list(product(range(prime),repeat=3))
        for values in product(range(prime),repeat=6):
            rows=[values[:3],values[3:]];a=np.array(rows,dtype=np.int64);basis,_=nullspace(a,prime)
            # Independent direct equations for all field vectors; no elimination.
            direct={v for v in vectors if all(sum(x*y for x,y in zip(row,v))%prime==0 for row in rows)}
            span={tuple(int(x)for x in np.array(coeff,dtype=np.int64)@basis%prime)for coeff in product(range(prime),repeat=len(basis))}
            assert span==direct;matrices+=1
            if any(values):
                column=next(j for j in range(3)if any(row[j]for row in rows));bad=[0]*3;bad[column]=1
                assert any(sum(x*y for x,y in zip(row,bad))%prime for row in rows);assert tuple(bad)not in span;corruptions+=1
        checked.append(dict(prime=prime,all_two_by_three_matrices=matrices,each_kernel_checked_by_full_field_vector_enumeration=True,deliberately_false_kernel_vectors_rejected=corruptions))
    inputs=[Path(__file__),ROOT/'acceleration/theory_20260930_triangle_modular_kernel.py',ROOT/'acceleration/results/20260930_triangle_modular_kernel/summary.json']
    report=dict(status='PRODUCER_POST_RUN_MODULAR_KERNEL_CALIBRATION_PASS',timestamp=datetime.now(timezone.utc).isoformat(),checked=checked,inputs_sha256={p.relative_to(ROOT).as_posix():digest(p)for p in inputs},independent_review=False,scope='Post-run exhaustive tiny calibration of the producer nullspace routine; it does not promote any research claim or retroactively change the frozen run protocol.')
    path=args.out/'summary.json'
    with path.open('x',encoding='utf-8')as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps(dict(sha256=digest(path),checked=checked)))

if __name__=='__main__':main()
