"""Six frozen exact support attempts from saved PDHG duals; producer only."""
import argparse
from datetime import datetime,timezone
from fractions import Fraction
import json
import math
from pathlib import Path
import subprocess
import sys
import numpy as np
from scipy.sparse import csr_matrix
from export_20260917_six_moment_pdhg import ROOT,MODEL,CHECKPOINTS,digest,save,confined,load_checked_model

D=1<<20
def quantize(dual,q):
 assert len(dual)>=q and all(math.isfinite(float(x)) for x in dual)
 weights=[round(-Fraction.from_float(float(x))*D) for x in dual]
 weights[:q]=[min(D,max(-D,w)) for w in weights[:q]]
 return weights[:q],weights[q:]
def evaluate(M,R,rhs,offsets,original_ids,y,q):
 assert M.shape[0]==len(y)==len(rhs) and R.shape[0]==len(q) and M.shape[1]==R.shape[1]==offsets[-1]
 mc=int(np.asarray(abs(M).sum(axis=0),dtype=np.int64).max(initial=0));rc=int(np.asarray(abs(R).sum(axis=0),dtype=np.int64).max(initial=0))
 guard=max(map(abs,y),default=0)*mc+max(map(abs,q),default=0)*rc
 assert guard<2**62 and all(abs(w)<2**62 for w in y+q),'int64 guard failure; no product evaluated'
 columns=M.T@np.asarray(y,dtype=np.int64)+R.T@np.asarray(q,dtype=np.int64)
 maxima=[];argmax=[];old=[]
 for ids,a,b in zip(original_ids,offsets,offsets[1:]):
  j=int(np.argmax(columns[a:b]));maxima.append(int(columns[a+j]));argmax.append(j);old.append(ids[j])
 total=sum(int(v)*int(w) for v,w in zip(rhs,y));numerator=total-sum(maxima)
 return dict(denominator=D,numerator=numerator,approximate=numerator/D,moment_rhs_dot_numerator=total,
  sum_center_maxima_numerator=sum(maxima),moment_weight_numerators=y,reciprocity_weight_numerators=q,
  center_maxima_numerators=maxima,first_argmax_retained_ids=argmax,first_argmax_original_ids=old,
  int64_absolute_product_guard=guard,strictly_positive=numerator>0,independent_raw_check_pending=True)
def controls():
 assert quantize([.5/D,1.5/D,2.5/D,-.5/D,-1.5/D,-2.5/D],6)[0]==[0,-2,-2,0,2,2]
 assert quantize([-2.,2.,3.],2)==([D,-D],[-3*D])
 M=csr_matrix([[0,2]],dtype=np.int8);R=csr_matrix((0,2),dtype=np.int8)
 positive=evaluate(M,R,[3],[0,2],[[7,9]],[D],[]);assert positive['numerator']==D and positive['first_argmax_original_ids']==[9]
 feasible=evaluate(M,R,[1],[0,2],[[7,9]],[D],[]);assert feasible['numerator']==-D
 negative=[]
 for name,call in [('nonfinite',lambda:quantize([float('nan')],1)),('overflow',lambda:evaluate(M,R,[3],[0,2],[[7,9]],[2**62],[])),('wrong_dimension',lambda:evaluate(M,R,[3],[0,2],[[7,9]],[],[]))]:
  try:call()
  except (AssertionError,ValueError):negative.append(name)
  else:raise AssertionError(name+' accepted')
 return dict(status='SIX_GPU_SUPPORT_PRODUCER_CONTROLS_PASS',exact_rounding_ties_to_even=True,sign_clip_and_unbounded_q=True,
  positive_numerator=D,feasible_nonpositive_numerator=-D,corruptions_rejected=negative,independent_verification=False)
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--checkpoints-dir');p.add_argument('--controls-only',action='store_true');a=p.parse_args()
 out=confined(a.out);assert not out.exists();out.mkdir(parents=True);save(out/'controls.json',controls())
 if a.controls_only:return
 assert a.checkpoints_dir;directory=confined(a.checkpoints_dir);meta,C,bindings=load_checked_model();n=712721;hard=2124
 M=C[hard:,:n];R=C[84:hard,:n];rhs=meta['rhs'][hard:];offsets=meta['probability_offsets'];ids=meta['retained_original_domain_ids']
 for path in (Path(__file__),ROOT/'acceleration/export_20260917_six_moment_pdhg.py',directory/'manifest.json',directory/'receipt.json'):
  bindings[path.relative_to(ROOT).as_posix()]=digest(path)
 save(out/'manifest.json',dict(timestamp=datetime.now(timezone.utc).isoformat(),source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
  command=[sys.executable,*sys.argv],cwd=str(Path.cwd()),inputs_sha256=bindings,attempt_order=[[c,k] for c in CHECKPOINTS for k in ('last','average')],
  quantization='Negative saved binary64 rational, nearest integer ties-to-even at D2^20; moment clip±D; q unbounded',
  scope=meta['model'],arithmetic='int64 sparse products with prior guard<2^62; Python integer final sum',independent_check_pending=True))
 attempts=[]
 for cp in CHECKPOINTS:
  path=directory/f'six_{cp}.json';d=None
  if path.exists():
   try:
    d=json.loads(path.read_bytes());assert d['iterations']==cp and d['status']=='NUMERICAL_FULL_MOMENT_PDHG_CHECKPOINT'
   except Exception as e:d=None;parse_error=repr(e)
  else:parse_error='Checkpoint absent (cap/failure); no invented weights'
  for kind in ('last','average'):
   record=dict(iterations=cp,iterate=kind,checkpoint_path=path.relative_to(ROOT).as_posix(),checkpoint_sha256=digest(path) if path.exists() else None)
   if d is None:record.update(status='SKIPPED_MISSING_OR_INVALID_CHECKPOINT',reason=parse_error)
   else:
    try:
     dual=d['y_'+kind];assert len(dual)==5526;y,q=quantize(dual,3486)
     record.update(evaluate(M,R,rhs,offsets,ids,y,q),status='CANDIDATE_EXACT_SIX_COORDINATE_SUPPORT_ATTEMPT')
    except Exception as e:record.update(status='FAILED_EXACT_SUPPORT_ATTEMPT',reason=repr(e))
   target=out/f'{cp}_{kind}.json';save(target,record);attempts.append(dict(path=target.relative_to(ROOT).as_posix(),sha256=digest(target),iterations=cp,iterate=kind,status=record['status'],numerator=record.get('numerator')))
   print(json.dumps(attempts[-1]),flush=True)
 save(out/'summary.json',dict(status='SIX_FROZEN_GPU_SUPPORT_ATTEMPTS_RECORDED',attempts=attempts,denominator=D,
  positive_attempts=sum(r['numerator'] is not None and r['numerator']>0 for r in attempts),attempt_population=6,
  independent_raw_check_pending=True,target_resolution=False,all_failed_and_nonpositive_attempts_retained=True))
if __name__=='__main__':main()
