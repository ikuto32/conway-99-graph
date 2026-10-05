"""Supplementary controls for the new resource-bounded row solver wrapper."""
from datetime import datetime, timezone
from itertools import product
from pathlib import Path
import hashlib
import json
import subprocess
import sys
from theory_20260930_triangle_q1_binary_scout import row_solve
from theory_20260930_eight_full99_cnf import ResourceCap

ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'acceleration/results/20260930_triangle_q1_binary_scout/supplemental_row_controls.json'
assert not out.exists()
cap=ResourceCap();choices=[]
for mask in range(1,8):
    vv=[i for i in range(3) if mask&(1<<i)]
    for lo in range(len(vv)+1):
        for hi in range(lo,len(vv)+1):choices.append({'variables':vv,'lower':lo,'upper':hi})
counts={'SAT':0,'UNSAT':0}
for a in choices:
    for b in choices:
        cs=[a,b]
        truth=[v for v in product((0,1),repeat=3) if all(c['lower']<=sum(v[x] for x in c['variables'])<=c['upper'] for c in cs)]
        result=row_solve(3,cs,cap)
        assert result['status']==('SAT' if truth else 'UNSAT')
        if truth:assert tuple(result['assignment']) in truth
        counts[result['status']]+=1
source=ROOT/'acceleration/theory_20260930_triangle_q1_binary_scout.py'
data={'status':'PRODUCER_BOUNDED_ROW_SOLVER_CALIBRATION_PASS','timestamp':datetime.now(timezone.utc).isoformat(),'command':[sys.executable,*sys.argv],'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'producer_source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'controls_source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'systems_checked':sum(counts.values()),'outcomes':counts,'control_method':'Every ordered pair of0/1sum interval constraints on all nonempty subsets of3bits compared to all8assignments.','independent_verification':False,'calibration_scope_correction':'Initial scout controls exercised the frozen predecessor row solver, not the newly bounded wrapper. This supplement directly exercises that wrapper after the2.375second scout. All original source, controls and research artifacts remain unchanged; this is additional producer calibration, not independent approval.'}
out.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'path':out.relative_to(ROOT).as_posix(),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'systems':sum(counts.values())}))
