"""Exact support bound from arbitrary saved finite row weights, independent of solver flags."""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import platform
import subprocess
import sys

import numpy as np
from scipy.sparse import load_npz

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "acceleration/results/20260917_partial_matching_moments"


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def save(path,value):
    with path.open("x",encoding="utf-8") as f:
        json.dump(value,f,indent=2)
        f.write("\n")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    assert not any(args.out.iterdir())
    files=[SOURCE+"/model.json",SOURCE+"/integer_augmented_csr.npz",SOURCE+"/numeric_lp.json",SOURCE+"/manifest.json","uv.lock",Path(__file__).relative_to(ROOT).as_posix()]
    bindings={name:digest(ROOT/name) for name in files}
    save(args.out/"manifest.json",dict(timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
        command_argv=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),inputs_sha256=bindings,
        selection="Preserved raw 60-second moment-run row_dual entries, irrespective of false dual_valid flag; no feasibility assumption",
        procedure="Round reciprocity weights to nearest denominator2^20 integer; clip moment weights to[-1,1] then round; support-bound all54478 choices exactly",
        formula="(y*b - sum_t max_S(M^T*y+R^T*q)_tS)/2^20 with integer q,y and abs(y)<=2^20",
        threshold="Strictly positive exact numerator is candidate conditional exclusion pending independent checking",
        scope="Frozen one-coordinate partial-K family;162K edges and prescribed zeros, no filtering",solver_rerun=False))
    model=json.loads((ROOT/SOURCE/"model.json").read_bytes())
    raw=json.loads((ROOT/SOURCE/"numeric_lp.json").read_bytes())
    matrix=load_npz(ROOT/SOURCE/"integer_augmented_csr.npz")
    assert digest(ROOT/SOURCE/"integer_augmented_csr.npz")==model["matrix_sha256"]
    n=model["probability_offsets"][-1]
    R=matrix[84:1824,:n]; M=matrix[1824:,:n]
    weights=np.array(raw["row_dual"],dtype=float)
    assert len(weights)==5310 and np.all(np.isfinite(weights))
    scale=1<<20
    q=np.rint(weights[84:1824]*scale)
    y=np.rint(np.clip(weights[1824:],-1,1)*scale)
    overflow_limit=(int(np.max(np.abs(q),initial=0))*int(abs(R).sum(axis=0).max())+scale*int(abs(M).sum(axis=0).max()))
    assert overflow_limit<2**62
    q,y=q.astype(np.int64),y.astype(np.int64)
    column=M.T@y+R.T@q
    offsets=model["probability_offsets"]
    maxima=[int(max(column[a:b])) for a,b in zip(offsets,offsets[1:])]
    maximizing_ids=[int(np.argmax(column[a:b])) for a,b in zip(offsets,offsets[1:])]
    rhs=model["rhs"][1824:]
    linear=sum(int(a)*int(b) for a,b in zip(y,rhs))
    numerator=linear-sum(maxima)
    result=dict(timestamp=datetime.now(timezone.utc).isoformat(),status="CANDIDATE_EXACT_SUPPORT_BOUND",
        formula="L1 moment optimum >= (y*b-sum center maxima)/denominator on hard reciprocal simplices",
        denominator=scale,numerator=numerator,approximate=numerator/scale,strictly_positive=numerator>0,
        moment_weight_numerators=y.tolist(),reciprocity_weight_numerators=q.tolist(),
        rhs_dot_numerator=linear,center_maxima_numerators=maxima,maximizing_original_domain_ids=maximizing_ids,
        checked_domain_choices=n,checked_centers=84,integer_product_absolute_bound=overflow_limit,
        input_solver_dual_valid=raw["dual_valid"],weights_are_solver_feasible_claimed=False,
        independent_verification=False,target_resolution=False,
        limitation="The solver flags are irrelevant to the algebraic support bound; domain completeness, model necessity and arithmetic still require independent review.")
    assert all(digest(ROOT/name)==expected for name,expected in bindings.items())
    save(args.out/"certificate.json",result)
    save(args.out/"summary.json",dict(timestamp=result["timestamp"],numerator=numerator,denominator=scale,
        approximate=numerator/scale,strictly_positive=numerator>0,certificate_sha256=digest(args.out/"certificate.json"),
        manifest_sha256=digest(args.out/"manifest.json"),status="CANDIDATE",family_exclusion_verified=False,target_resolution=False))
    print(json.dumps({k:result[k] for k in ("numerator","denominator","approximate","strictly_positive")}))


if __name__=="__main__":
    main()
