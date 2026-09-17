"""Evaluate one preregistered exact weight transfer on the full new domain."""
from datetime import datetime,timezone
import json
from pathlib import Path
import subprocess
import sys
import numpy as np
from scipy.sparse import load_npz
from theory_20260917_partial_matching_moments import digest,save

ROOT=Path(__file__).resolve().parents[1]
OLD="acceleration/results/20260917_partial_matching_moments/model.json"
CERT="acceleration/results/20260917_partial_matching_moment_replay600/exact_support_bound.json"
NEW="acceleration/results/20260917_two_matching_moments"
OUT=ROOT/"acceleration/results/20260917_two_matching_transferred_certificate"


def main():
    OUT.mkdir(exist_ok=True);assert not any(OUT.iterdir())
    paths=[OLD,CERT,NEW+"/model.json",NEW+"/integer_augmented_csr.npz",NEW+"/build_manifest.json",Path(__file__).relative_to(ROOT).as_posix(),"acceleration/theory_20260917_partial_matching_moments.py","uv.lock"]
    bindings={p:digest(ROOT/p) for p in paths}
    save(OUT/"manifest.json",dict(timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
        command_argv=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),inputs_sha256=bindings,
        selection="Exactly one transfer: same3486 integer momentweights; old1740 reciprocity weights mapped by unordered edge identity;60 newly unknown reciprocity weights0. No sign or weight optimization.",
        arithmetic="Retain old denominator2^20 exactly; recompute new RHS dot product and all89308 column scores/84maxima on new full matrix",
        scope="New two-coordinate family with156fixedK and prescribedzeros; all89308 original domains, nofilter",
        acceptance="Candidate only until independent complete-domain, new-model and raw-neighborhood bound PASS. Strictlypositive bound avoids900-second solve; no automatic inheritance from old proof.",
        solver_run=False,target_resolution=False))
    old=json.loads((ROOT/OLD).read_bytes());cert=json.loads((ROOT/CERT).read_bytes())["bound"]
    new=json.loads((ROOT/NEW/"model.json").read_bytes())
    A=load_npz(ROOT/NEW/"integer_augmented_csr.npz")
    assert digest(ROOT/NEW/"integer_augmented_csr.npz")==new["matrix_sha256"]
    oldq={tuple(e):int(q) for e,q in zip(old["unknown_edges"],cert["reciprocity_weight_numerators"])}
    newedges=list(map(tuple,new["unknown_edges"]))
    assert set(oldq)<=set(newedges) and len(newedges)-len(oldq)==60
    assert old["pair_order"]==new["pair_order"]
    y=np.array(cert["moment_weight_numerators"],dtype=np.int64)
    q=np.array([oldq.get(e,0) for e in newedges],dtype=np.int64)
    scale=cert["denominator"]
    assert len(y)==3486 and np.max(np.abs(y))<=scale
    offsets=new["probability_offsets"];n=offsets[-1];hard=84+len(newedges)
    assert n==89308
    R=A[84:hard,:n];M=A[hard:,:n]
    overflow=int(np.max(np.abs(q),initial=0))*int(abs(R).sum(axis=0).max())+int(np.max(np.abs(y),initial=0))*int(abs(M).sum(axis=0).max())
    assert overflow<2**62
    column=M.T@y+R.T@q
    maxima=[int(max(column[a:b])) for a,b in zip(offsets,offsets[1:])]
    ids=[int(np.argmax(column[a:b])) for a,b in zip(offsets,offsets[1:])]
    rhsdot=sum(int(a)*int(b) for a,b in zip(y,new["rhs"][hard:]))
    numerator=rhsdot-sum(maxima)
    result=dict(timestamp=datetime.now(timezone.utc).isoformat(),status="CANDIDATE_TRANSFERRED_EXACT_BOUND",
        numerator=numerator,denominator=scale,approximate=numerator/scale,strictly_positive=numerator>0,
        moment_weight_numerators=y.tolist(),reciprocity_weight_numerators=q.tolist(),
        transferred_reciprocity_edges=len(oldq),new_zero_weight_edges=[list(e) for e in newedges if e not in oldq],
        rhs_dot_numerator=rhsdot,center_maxima_numerators=maxima,maximizing_new_domain_ids=ids,
        checked_columns=n,checked_centers=84,integer_product_absolute_bound=overflow,
        old_certificate_unchanged=True,independent_new_domain_model_bound_review_pending=True,target_resolution=False)
    assert all(digest(ROOT/p)==h for p,h in bindings.items())
    save(OUT/"certificate.json",result)
    save(OUT/"summary.json",dict(timestamp=result["timestamp"],status="CANDIDATE",numerator=numerator,denominator=scale,
        approximate=numerator/scale,strictly_positive=numerator>0,certificate_sha256=digest(OUT/"certificate.json"),
        manifest_sha256=digest(OUT/"manifest.json"),solver_run=False,independent_review_pending=True,target_resolution=False))
    print(json.dumps({k:result[k] for k in ("numerator","denominator","approximate","strictly_positive")}))


if __name__=="__main__":
    main()
