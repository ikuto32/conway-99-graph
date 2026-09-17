"""Build a new four-coordinate full moment model only; no solver entry point."""
import argparse
from datetime import datetime,timezone
from itertools import combinations
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

import highspy
import numpy as np
import scipy
from scipy.sparse import vstack,hstack,coo_matrix,eye,save_npz,load_npz
from theory_20260917_partial_matching_moments import build,controls,digest,save,exact_bound

ROOT=Path(__file__).resolve().parents[1]
DOMAIN="acceleration/results/20260917_partial_four_matchings"
MODEL="PARTIAL_K_FOUR_SAME_SIGN_COORDINATES_FULL_MOMENT_PHASE1_V1"


def provenance():
    return dict(timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
        command_argv=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),
        python=platform.python_version(),numpy=np.__version__,scipy=scipy.__version__,highs=highspy.Highs().version())


def build_model(out):
    out.mkdir(parents=True,exist_ok=True)
    assert not any(out.iterdir()),"Fresh build directory required"
    bindings={}
    def read(name):
        bindings[name]=digest(ROOT/name)
        return json.loads((ROOT/name).read_bytes())
    manifest=read(DOMAIN+"/manifest.json");summary=read(DOMAIN+"/summary.json")
    assert summary["complete_all_centers"] and summary["complete_domain_choices"]==290460
    tables=[]
    for u in range(84):
        name=f"domain_{u:02d}.json";record=read(DOMAIN+"/"+name)
        assert bindings[DOMAIN+"/"+name]==summary["output_sha256"][name]
        tables.append([int(s,16) for s in record["domain_masks_hex"]])
    for name in (Path(__file__).relative_to(ROOT).as_posix(),"acceleration/theory_20260917_partial_matching_moments.py","uv.lock"):
        bindings[name]=digest(ROOT/name)
    fixed=set(map(tuple,manifest["remaining_fixed_K_edges_outer"]))
    unknown=list(map(tuple,manifest["unknown_edges_outer"]))
    supports=[{2*a+s,2*b+t} for a,b in combinations(range(7),2) for s in (0,1) for t in (0,1)]
    assert len(fixed)==144 and len(unknown)==1920
    save(out/"build_manifest.json",dict(**provenance(),inputs_sha256=bindings,model=MODEL,scope=manifest["scope"],
        question="Does the full moment necessary condition exclude the broader four-coordinate family?",
        equation="sum_(t,S):{v,w} subset N_B_outer(t) union S z_tS + x_vw = 2 - |support(v) intersect support(w)| - B_vw; x uses smaller endpoint for unknown pairs, zero otherwise",
        domain="All290460 new original local stars, no filtering; new sorted-mask domain IDs",
        constraints="84 hard simplices,1920 hard reciprocal marginals,3486 moment equalities with plus/minus L1 phase-I slacks",
        solver_preregistration=None,solver_preregistration_null_reason="No large LP authorized at this build stage; matching-filter review precedes solver selection",
        resource_scope="Build integer model and8MiBcompanion chunks only; no solver execution",
        gates="Build only. Independent new-domain/model reviews and an explicit later resource decision required before any LP",
        criterion="Strictly positive exact support-function lower bound, independently checked, for conditional exclusion. Floatingzero or positive numericalobjective alone inconclusive.",
        exact_weights="Any finite returned row weights; moment weights clipped[-1,1], denominator2^20 rounding, maxima across every new domain; no solver-feasibility assumption required",
        shared_code="Uses prior generic moment matrix builder, controls and support arithmetic; fresh independent reconstruction required",
        controls="All9 rook roots times2fixededge choices:18 positive exact witnesses,36 coefficient/RHS corruptions",
        target_resolution=False))
    started=time.monotonic()
    save(out/"controls.json",controls())
    N,R,M,rhs,offsets,pairs=build(supports,fixed,unknown,tables,progress=True)
    assert all(mask.bit_count()+sum(u in e for e in fixed)==12 for u,table in enumerate(tables) for mask in table)
    hard=84+len(unknown);p=len(pairs);n=offsets[-1]
    A=vstack((N,R,M),format="csr",dtype=np.int64)
    slack=vstack((coo_matrix((hard,2*p),dtype=np.int64),hstack((-eye(p,dtype=np.int64),eye(p,dtype=np.int64)),format="csr")),format="csr")
    augmented=hstack((A,slack),format="csr",dtype=np.int64)
    save_npz(out/"integer_augmented_csr.npz",augmented,compressed=True)
    save(out/"model.json",dict(model=MODEL,shape=list(augmented.shape),nonzeros=augmented.nnz,
        matrix_sha256=digest(out/"integer_augmented_csr.npz"),probability_offsets=offsets,
        fixed_edges=sorted(fixed),unknown_edges=unknown,pair_order=pairs,supports=[sorted(s) for s in supports],
        row_order="84 simplex,1920 reciprocity,3486 moments",column_order="290460 new probabilities by center/mask original order,3486 negative slacks,3486 positive slacks",
        rhs=np.r_[np.ones(84,dtype=np.int64),np.zeros(len(unknown),dtype=np.int64),rhs].tolist(),
        costs=np.r_[np.zeros(n,dtype=np.int64),np.ones(2*p,dtype=np.int64)].tolist(),
        column_lower=0,column_upper=None,column_upper_null_reason="Positive infinity for every column",all_rows_equalities=True))
    chunk_records=[]
    for artifact in (out/"integer_augmented_csr.npz",out/"model.json"):
        if artifact.stat().st_size<=10*1024*1024:
            continue
        parts=[]
        with artifact.open("rb") as source:
            index=0
            while data:=source.read(8*1024*1024):
                name=artifact.name+f".part{index:03d}"
                with (out/name).open("xb") as sink:sink.write(data)
                parts.append(dict(path=name,bytes=len(data),sha256=digest(out/name)))
                index+=1
        chunk_records.append(dict(source=artifact.name,source_bytes=artifact.stat().st_size,source_sha256=digest(artifact),
            source_availability="LOCAL_ONLY",parts=parts,recovery="Concatenate listed part bytes in order into a fresh file, then check source size and SHA256"))
    save(out/"chunk_manifest.json",dict(schema_version=1,chunk_bytes=8*1024*1024,artifacts=chunk_records,
        publication="Large raw files retained locally; only hash-manifest and8MiBparts are intended publication candidates. No publication performed by this tool."))
    assert all(digest(ROOT/name)==h for name,h in bindings.items())
    result=dict(**provenance(),status="CANDIDATE_FOUR_COORDINATE_FULL_MOMENT_BUILD",model=MODEL,
        domain_choices=n,centers=84,reciprocity_rows=len(unknown),moment_rows=p,shape=list(augmented.shape),nonzeros=augmented.nnz,
        elapsed_seconds=time.monotonic()-started,output_sha256={f.name:digest(f) for f in out.iterdir() if f.is_file()},
        solver_launched=False,independent_domain_gate_pending=True,independent_model_gate_pending=True,target_resolution=False)
    save(out/"build_summary.json",result)
    print(json.dumps({k:result[k] for k in ("status","shape","nonzeros","elapsed_seconds","solver_launched")}))


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    build_model(args.out)
