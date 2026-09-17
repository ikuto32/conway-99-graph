"""Build a new two-coordinate moment model; solve only behind two independent gates."""
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
DOMAIN="acceleration/results/20260917_partial_two_matchings"
MODEL="PARTIAL_K_TWO_SAME_SIGN_COORDINATES_FULL_MOMENT_PHASE1_V1"


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
    assert summary["complete_all_centers"] and summary["complete_domain_choices"]==89308
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
    assert len(fixed)==156 and len(unknown)==1800
    save(out/"build_manifest.json",dict(**provenance(),inputs_sha256=bindings,model=MODEL,scope=manifest["scope"],
        question="Does the full moment necessary condition exclude the broader two-coordinate family?",
        equation="sum_(t,S):{v,w} subset N_B_outer(t) union S z_tS + x_vw = 2 - |support(v) intersect support(w)| - B_vw; x uses smaller endpoint for unknown pairs, zero otherwise",
        domain="All89308 new original local stars, no filtering; new sorted-mask domain IDs",
        constraints="84 hard simplices,1800 hard reciprocal marginals,3486 moment equalities with plus/minus L1 phase-I slacks",
        solver_preregistration=dict(solver="ipm",threads=1,crossover="off",time_limit_seconds=900,presolve="HiGHS defaults; adaptive sublimits disclosed in log"),
        cap_rationale="Larger new model; earlier one-coordinate model required268.687seconds.900second cap is a bounded exploration, not a runtime prediction or speed claim.",
        gates="Build allowed now; solve prohibited until independent complete new-domain and full new integer model PASS reports bind exact artifacts",
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
        row_order="84 simplex,1800 reciprocity,3486 moments",column_order="89308 new probabilities by center/mask original order,3486 negative slacks,3486 positive slacks",
        rhs=np.r_[np.ones(84,dtype=np.int64),np.zeros(len(unknown),dtype=np.int64),rhs].tolist(),
        costs=np.r_[np.zeros(n,dtype=np.int64),np.ones(2*p,dtype=np.int64)].tolist(),
        column_lower=0,column_upper=None,column_upper_null_reason="Positive infinity for every column",all_rows_equalities=True))
    assert all(digest(ROOT/name)==h for name,h in bindings.items())
    result=dict(**provenance(),status="CANDIDATE_TWO_COORDINATE_FULL_MOMENT_BUILD",model=MODEL,
        domain_choices=n,centers=84,reciprocity_rows=len(unknown),moment_rows=p,shape=list(augmented.shape),nonzeros=augmented.nnz,
        elapsed_seconds=time.monotonic()-started,output_sha256={f.name:digest(f) for f in out.iterdir() if f.is_file()},
        solver_launched=False,independent_domain_gate_pending=True,independent_model_gate_pending=True,target_resolution=False)
    save(out/"build_summary.json",result)
    print(json.dumps({k:result[k] for k in ("status","shape","nonzeros","elapsed_seconds","solver_launched")}))


def solve_model(out,domain_review,model_review):
    assert domain_review and model_review,"Both independent reviews required"
    bindings={}
    for p in (out/"model.json",out/"integer_augmented_csr.npz",out/"build_manifest.json",out/"build_summary.json",domain_review,model_review,
              Path(__file__),ROOT/"acceleration/theory_20260917_partial_matching_moments.py",ROOT/"uv.lock"):
        bindings[p.resolve().relative_to(ROOT).as_posix()]=digest(p)
    d=json.loads(domain_review.read_bytes());r=json.loads(model_review.read_bytes())
    assert "PASS" in d["status"] and "PASS" in r["status"]
    for path in (DOMAIN+"/manifest.json",DOMAIN+"/summary.json"):
        assert d["inputs_sha256"][path]==digest(ROOT/path)
    for name in ("model.json","integer_augmented_csr.npz"):
        path=(out/name).resolve().relative_to(ROOT).as_posix()
        assert r["inputs_sha256"][path]==bindings[path]
    build_record=json.loads((out/"build_manifest.json").read_bytes())
    for path,h in build_record["inputs_sha256"].items():
        assert digest(ROOT/path)==h
    save(out/"solve_manifest.json",dict(**provenance(),inputs_sha256=bindings,model=MODEL,
        approved_domain_review=digest(domain_review),approved_model_review=digest(model_review),
        configuration=build_record["solver_preregistration"],scope=build_record["scope"],criterion=build_record["criterion"],target_resolution=False))
    model=json.loads((out/"model.json").read_bytes());A=load_npz(out/"integer_augmented_csr.npz")
    lp=highspy.HighsLp();lp.num_row_,lp.num_col_=A.shape
    lp.col_cost_=np.array(model["costs"],dtype=float);lp.col_lower_=np.zeros(lp.num_col_);lp.col_upper_=np.full(lp.num_col_,highspy.kHighsInf)
    lp.row_lower_=np.array(model["rhs"],dtype=float);lp.row_upper_=lp.row_lower_.copy()
    lp.a_matrix_.format_=highspy.MatrixFormat.kRowwise
    lp.a_matrix_.start_=A.indptr;lp.a_matrix_.index_=A.indices;lp.a_matrix_.value_=A.data.astype(float)
    solver=highspy.Highs()
    for key,value in (("output_flag",True),("threads",1),("solver","ipm"),("run_crossover","off"),("time_limit",900.0),("log_file",str(out/"highs.log"))):
        assert solver.setOptionValue(key,value)==highspy.HighsStatus.kOk
    assert solver.passModel(lp)==highspy.HighsStatus.kOk
    started=time.monotonic();status=solver.run();elapsed=time.monotonic()-started
    sol,info=solver.getSolution(),solver.getInfo()
    raw=dict(**provenance(),run_status=str(status),model_status=str(solver.getModelStatus()),value_valid=sol.value_valid,dual_valid=sol.dual_valid,
        raw_info_objective=info.objective_function_value,objective_usable=bool(sol.value_valid),solve_seconds=elapsed,
        col_value=list(sol.col_value),col_dual=list(sol.col_dual),row_value=list(sol.row_value),row_dual=list(sol.row_dual),
        invalid_vector_policy="Invalid vectors are not feasible solutions; arbitrary finite weights can still define support bounds")
    save(out/"numeric_lp.json",raw)
    n=model["probability_offsets"][-1];hard=84+len(model["unknown_edges"]);weights=np.array(sol.row_dual)
    bound=exact_bound(A[84:hard,:n],A[hard:,:n],np.array(model["rhs"][hard:],dtype=np.int64),model["probability_offsets"],weights) if len(weights)==A.shape[0] and np.all(np.isfinite(weights)) else None
    save(out/"exact_support_bound.json",dict(bound=bound,null_reason=None if bound else "No finite full row-weight vector",solver_dual_valid=sol.dual_valid,solver_feasibility_not_required=True))
    assert all(digest(ROOT/path)==h for path,h in bindings.items())
    result=dict(**provenance(),status="CANDIDATE_TWO_COORDINATE_FULL_MOMENT_SOLVE",model=MODEL,model_status=raw["model_status"],
        value_valid=sol.value_valid,dual_valid=sol.dual_valid,objective=info.objective_function_value if sol.value_valid else None,
        objective_null_reason=None if sol.value_valid else "No valid primal; raw info objective unusable",solve_seconds=elapsed,
        support_bound=None if bound is None else {k:bound[k] for k in ("numerator","denominator","approximate","strictly_positive")},
        output_sha256={p.name:digest(p) for p in out.iterdir() if p.is_file()},independent_bound_check_pending=True,family_exclusion_verified=False,target_resolution=False)
    save(out/"solve_summary.json",result)
    print(json.dumps({k:result[k] for k in ("model_status","value_valid","dual_valid","objective","solve_seconds","support_bound")}))


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage",choices=("build","solve"),required=True)
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--domain-review",type=Path)
    parser.add_argument("--model-review",type=Path)
    args=parser.parse_args()
    if args.stage=="build":build_model(args.out)
    else:solve_model(args.out,args.domain_review,args.model_review)
