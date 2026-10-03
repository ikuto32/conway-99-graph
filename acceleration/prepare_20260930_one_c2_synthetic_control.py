"""Synthetic25row positive for validator calibration; NOT research Gram."""
from datetime import datetime,timezone
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'acceleration/results/20260930_independent_review/triangle_q1_capacity_sat_object/independent_factor.json'
SOURCE_SHA='f979e59f10f89678f640664d33bda296531058109d31d3117b73239edd470d88'
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    assert digest(SOURCE)==SOURCE_SHA
    factor=json.loads(SOURCE.read_bytes());c=factor['incidence_matrix'];components=factor['components']
    component=next(group for group in components if 24 in group)
    allowed=[d for d in range(60) if sum(c[r][d] for r in component if r<24)<2]
    compatible={d:{e for e in allowed if e!=d and sum(c[r][d]*c[r][e] for r in range(24))<2} for d in allowed}
    nodes=0
    def find(chosen,candidates):
        nonlocal nodes
        nodes+=1
        if len(chosen)==10:return chosen
        if len(chosen)+len(candidates)<10:return None
        if nodes%1000==0:assert time.monotonic()-start<10
        candidates=sorted(candidates)
        for i,d in enumerate(candidates):
            answer=find(chosen+[d],set(candidates[i+1:])&compatible[d])
            if answer is not None:return answer
        return None
    chosen=find([],set(allowed));assert chosen is not None
    raw=[row[:] for row in c]+[[int(d in chosen) for d in range(60)]]
    assert len(raw)==25 and all(sum(row)==10 for row in raw)
    assert all(sum(raw[r][d] for r in range(f,f+12))==2 for f in (0,12) for d in range(60))
    assert all(sum(raw[r][d] for r in group if r<25)<=2 for group in components for d in range(60))
    assert all(sum(raw[r][d]*raw[r][e] for r in range(25))<=2 for d in range(60) for e in range(d+1,60))
    gram=[[sum(raw[a][d]*raw[b][d] for d in range(60)) for b in range(25)] for a in range(25)]
    out={'status':'SYNTHETIC_VALIDATOR_CONTROL_NOT_RESEARCH_FACTOR','timestamp':datetime.now(timezone.utc).isoformat(),'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'command':[sys.executable,*sys.argv],'working_directory':str(ROOT),'inputs_sha256':{SOURCE.relative_to(ROOT).as_posix():SOURCE_SHA,Path(__file__).relative_to(ROOT).as_posix():digest(__file__),'uv.lock':digest(ROOT/'uv.lock')},'incidence_matrix':raw,'own_target_gram':gram,'components':components,'chosen_extra_row_columns':chosen,'allowed_column_count':len(allowed),'search_nodes':nodes,'elapsed_seconds':time.monotonic()-start,'limitations':['Gram is computed from this synthetic matrix; it is not the research25x25Gram.','Only a positive calibration fixture, no target or fixed-core extension construction claim.']}
    p=args.out/'fixture.json';p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'sha256':digest(p),'nodes':nodes}))
if __name__=='__main__':main()
