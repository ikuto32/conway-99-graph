"""Independent exact support arithmetic for the unsuccessful 240-second replay."""
from datetime import datetime,timezone
import json
from pathlib import Path
import platform
import subprocess
import sys
from scipy.sparse import load_npz
import audit_20260917_partial_matching as h

def main():
    root=h.ROOT;d=root/'acceleration/results/20260917_partial_matching_moment_replay240';bindings={}
    def read(p):bindings[h.key(p)]=h.digest(p);return json.loads(Path(p).read_bytes())
    manifest=read(d/'manifest.json');summary=read(d/'summary.json');raw=read(d/'numeric_lp.json');envelope=read(d/'exact_support_bound.json');cert=envelope['bound']
    for f,v in manifest['inputs_sha256'].items():h.require(h.digest(root/f)==v,'changed input');bindings[h.key(root/f)]=v
    for f,v in summary['output_sha256'].items():h.require(h.digest(d/f)==v,'changed output');bindings[h.key(d/f)]=v
    p=root/'acceleration/results/20260917_independent_review/partial_moments.json'
    h.require(h.digest(p)=='1d4d08ecc9e73a00e06d210fa5137e7885e677756dc8f33b016fa3227ddec5e1','model audit');audit=read(p)
    model=root/'acceleration/results/20260917_partial_matching_moments';meta=read(model/'model.json');p=model/'integer_augmented_csr.npz'
    h.require(h.digest(p)==audit['inputs_sha256'][h.key(p)],'integer matrix');bindings[h.key(p)]=h.digest(p);A=load_npz(p).tocsc()
    q=cert['reciprocity_weight_numerators'];y=cert['moment_weight_numerators'];scale=cert['denominator']
    h.require(type(scale)is int and scale>0 and len(q)==1740 and len(y)==3486 and all(type(v)is int for v in q+y)and all(abs(v)<=scale for v in y),'arbitrary weight domain')
    weights=[0]*84+q+y;offsets=meta['probability_offsets'];scores=[]
    for col in range(offsets[-1]):scores.append(sum(int(A.data[k])*weights[int(A.indices[k])]for k in range(A.indptr[col],A.indptr[col+1])))
    maxima=[max(scores[a:b])for a,b in zip(offsets,offsets[1:])];dot=sum(int(v)*w for v,w in zip(meta['rhs'],weights));num=dot-sum(maxima)
    h.require(maxima==cert['center_maxima_numerators']and num==cert['numerator']and num<0 and not cert['strictly_positive'],'exact bound')
    h.require(raw['value_valid']is False and raw['dual_valid']is False and summary['objective']is None,'failed solver interpretation')
    for p in(__file__,h.__file__,root/'uv.lock'):bindings[h.key(p)]=h.digest(p)
    report=dict(status='INDEPENDENT_MOMENT_REPLAY240_ARBITRARY_BOUND_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit_observed_after_checks=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(root),python=platform.python_version(),inputs_sha256=bindings,numerator=num,denominator=scale,strictly_positive=False,checked_columns=len(scores),checked_centers=84,solver_valid_primal=False,solver_valid_dual=False,method='Complete unbounded Python integer dot products and simplex maxima using independently reconstructed hash-bound model.',derivation='For arbitrary q and box-constrained y, hard reciprocity Rz=0 and per-center simplices give ||Mz-b||1 >= y*b-(M^T*y+R^T*q)z >= y*b-sum maxima. Solver validity flags are unnecessary for this support inequality.',shared_components=['Python standard library','SciPy sparse loading','prior independent model review and artifact helpers'],producer_imported=False,limitations=['Negative bound weaker than trivial zero; no exclusion, primal feasibility or solver dual feasibility.','No independent solver repetition.'])
    p=root/'acceleration/results/20260917_independent_review/moment_replay240.json'
    with p.open('x')as f:json.dump(report,f,indent=2)
    print(report['status'],num,scale)
if __name__=='__main__':main()
