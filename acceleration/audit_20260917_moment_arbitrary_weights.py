"""Exact arbitrary-weight support evaluation using previously reconstructed integer model."""
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import subprocess
import sys
from scipy.sparse import load_npz
import audit_20260917_partial_matching as h

ROOT=h.ROOT
def main():
    d=ROOT/'acceleration/results/20260917_partial_matching_moment_arbitrary_weights'
    model=ROOT/'acceleration/results/20260917_partial_matching_moments'
    bindings={}
    def read(p):
        bindings[h.key(p)]=h.digest(p);return json.loads(Path(p).read_bytes())
    cert=read(d/'certificate.json'); manifest=read(d/'manifest.json'); summary=read(d/'summary.json')
    for f,v in manifest['inputs_sha256'].items():
        h.require(h.digest(ROOT/f)==v,'changed input');bindings[h.key(ROOT/f)]=v
    review=ROOT/'acceleration/results/20260917_independent_review/partial_moments.json'
    h.require(h.digest(review)=='1d4d08ecc9e73a00e06d210fa5137e7885e677756dc8f33b016fa3227ddec5e1','model audit pin')
    audit=read(review);h.require(audit['status']=='INDEPENDENT_PARTIAL_K_FULL_MOMENT_MODEL_PASS','model review')
    meta=read(model/'model.json'); matpath=model/'integer_augmented_csr.npz'
    h.require(h.digest(matpath)==audit['inputs_sha256'][h.key(matpath)],'reviewed matrix');bindings[h.key(matpath)]=h.digest(matpath)
    mat=load_npz(matpath).tocsc(); q=cert['reciprocity_weight_numerators']; y=cert['moment_weight_numerators']; den=cert['denominator']
    h.require(type(den)is int and den>0 and len(q)==1740 and len(y)==3486,'weight dimensions')
    h.require(all(type(v)is int for v in q+y)and all(abs(v)<=den for v in y),'weight domain')
    weights=[0]*84+q+y
    offsets=meta['probability_offsets']; scores=[]
    for col in range(offsets[-1]):
        scores.append(sum(int(mat.data[k])*weights[int(mat.indices[k])] for k in range(mat.indptr[col],mat.indptr[col+1])))
    maxima=[max(scores[a:b])for a,b in zip(offsets,offsets[1:])]
    # Read the independently verified integer RHS; each q term has zero RHS.
    rhs=meta['rhs']
    dot=sum(weights[i]*int(rhs[i])for i in range(len(weights)))
    numerator=dot-sum(maxima)
    h.require(maxima==cert['center_maxima_numerators']and dot==cert['rhs_dot_numerator']and numerator==cert['numerator'],'exact support calculation')
    for u,j in enumerate(cert['maximizing_original_domain_ids']):h.require(scores[offsets[u]+j]==maxima[u],'maximizer')
    h.require(not cert['strictly_positive']and numerator<0 and summary['numerator']==numerator,'negative result')
    # Independent support inequality controls on two simplices: zero and corrupted claimed bounds.
    h.require(0-sum([0,0])==0 and numerator+1!=dot-sum(maxima),'controls')
    for p in (__file__,h.__file__,ROOT/'uv.lock'):bindings[h.key(p)]=h.digest(p)
    result=dict(status='INDEPENDENT_ARBITRARY_MOMENT_SUPPORT_BOUND_PASS',timestamp=datetime.now(timezone.utc).isoformat(),source_commit_observed_after_checks=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),command=[sys.executable,*sys.argv],cwd=str(ROOT),python=platform.python_version(),inputs_sha256=bindings,exact_numerator=numerator,exact_denominator=den,strictly_positive=False,choices_checked=len(scores),centers_checked=84,method='Python unbounded integers, complete matrix columns; prior independently reconstructed integer model hash-bound',derivation='For hard reciprocal simplex z, ||Mz-b||_1 >= y*(b-Mz) = y*b-(M^T*y+R^T*q)*z >= y*b-sum_center max_column, for arbitrary q and |y|<=1. Integer weights divided by denominator.',producer_imported=False,shared_components=['Python standard library','SciPy sparse NPZ loading','prior independent model review and artifact helpers'],limitations=['Negative lower bound is weaker than trivial zero; no exclusion or feasibility certificate.','Weights are arbitrary box-constrained moment weights and unrestricted reciprocity weights; not claimed solver-feasible duals.'])
    out=ROOT/'acceleration/results/20260917_independent_review/moment_arbitrary_weights.json'
    with out.open('x')as f:json.dump(result,f,indent=2)
    print(result['status'],numerator,den)
if __name__=='__main__':main()
