"""600-second replay of the unchanged independently audited full-moment model."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

import highspy
import numpy as np
from scipy.sparse import load_npz

from theory_20260917_partial_matching_moments import digest, save, exact_bound

ROOT=Path(__file__).resolve().parents[1]
SOURCE="acceleration/results/20260917_partial_matching_moments"
AUDIT="acceleration/results/20260917_independent_review/partial_moments.json"


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",required=True,type=Path)
    args=parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    assert not any(args.out.iterdir())
    files=[SOURCE+"/model.json",SOURCE+"/integer_augmented_csr.npz",SOURCE+"/numeric_lp.json",SOURCE+"/manifest.json",SOURCE+"/highs.log","acceleration/results/20260917_partial_matching_moment_replay240/summary.json","acceleration/results/20260917_partial_matching_moment_replay240/highs.log",AUDIT,"uv.lock",
           "acceleration/theory_20260917_partial_matching_moments.py",Path(__file__).relative_to(ROOT).as_posix()]
    bindings={name:digest(ROOT/name) for name in files}
    audit=json.loads((ROOT/AUDIT).read_bytes())
    assert audit["status"]=="INDEPENDENT_PARTIAL_K_FULL_MOMENT_MODEL_PASS"
    for name in (SOURCE+"/model.json",SOURCE+"/integer_augmented_csr.npz"):
        assert audit["inputs_sha256"][name]==bindings[name]
    save(args.out/"manifest.json",dict(timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
        command_argv=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),python=platform.python_version(),
        highs=highspy.Highs().version(),inputs_sha256=bindings,
        model="PARTIAL_K_FULL_CENTER_STAR_MOMENT_PHASE1_V1",unchanged_integer_model=True,
        scope="Same unfiltered54478 choices;162fixedK and all declared absences; no matching-filter substitution",
        selection="The 240-second run reached iteration19 with primal and dual objectives approaching but no valid exported primal or dual. Its arbitrary-weight support bound was negative. One authorized 600-second rerun seeks completed solver postsolve and useful exact weights; no automatic further retries, guarantee or speed claim. Presolve and dependency-search settings remain HiGHS defaults, whose automatic time allocation can change with solver time_limit.",
        limits=dict(solver_seconds=600,solver="ipm",threads=1,crossover="off",expected_wall="About ten minutes plus setup; solver iteration granularity can exceed cap"),
        acceptance="Only strictly positive exact support-function bound is candidate exclusion; raw objective zero with invalid primal is unusable. Any finite exported row weights may be used algebraically without solver-feasibility assertion.",
        independent_model_gate=bindings[AUDIT],family_exclusion_verified=False,target_resolution=False))
    model=json.loads((ROOT/SOURCE/"model.json").read_bytes())
    A=load_npz(ROOT/SOURCE/"integer_augmented_csr.npz")
    assert list(A.shape)==model["shape"] and A.nnz==model["nonzeros"]
    lp=highspy.HighsLp();lp.num_row_,lp.num_col_=A.shape
    lp.col_cost_=np.array(model["costs"],dtype=float)
    lp.col_lower_=np.zeros(lp.num_col_);lp.col_upper_=np.full(lp.num_col_,highspy.kHighsInf)
    lp.row_lower_=np.array(model["rhs"],dtype=float);lp.row_upper_=lp.row_lower_.copy()
    lp.a_matrix_.format_=highspy.MatrixFormat.kRowwise
    lp.a_matrix_.start_=A.indptr;lp.a_matrix_.index_=A.indices;lp.a_matrix_.value_=A.data.astype(float)
    solver=highspy.Highs()
    for key,value in (("output_flag",True),("threads",1),("solver","ipm"),("run_crossover","off"),("time_limit",600.0),("log_file",str(args.out/"highs.log"))):
        assert solver.setOptionValue(key,value)==highspy.HighsStatus.kOk
    assert solver.passModel(lp)==highspy.HighsStatus.kOk
    start=time.monotonic();status=solver.run();elapsed=time.monotonic()-start
    sol,info=solver.getSolution(),solver.getInfo()
    raw=dict(timestamp=datetime.now(timezone.utc).isoformat(),run_status=str(status),model_status=str(solver.getModelStatus()),
        value_valid=sol.value_valid,dual_valid=sol.dual_valid,raw_info_objective=info.objective_function_value,
        objective_usable=bool(sol.value_valid),solve_seconds=elapsed,
        col_value=list(sol.col_value),col_dual=list(sol.col_dual),row_value=list(sol.row_value),row_dual=list(sol.row_dual),
        invalid_vector_policy="Preserve raw values; invalid flags preclude feasibility claims, but arbitrary finite weights still define a support bound")
    save(args.out/"numeric_lp.json",raw)
    n=model["probability_offsets"][-1]
    weights=np.array(sol.row_dual)
    usable_weights=len(weights)==A.shape[0] and np.all(np.isfinite(weights))
    bound=exact_bound(A[84:1824,:n],A[1824:,:n],np.array(model["rhs"][1824:],dtype=np.int64),model["probability_offsets"],weights) if usable_weights else None
    save(args.out/"exact_support_bound.json",dict(bound=bound,null_reason=None if bound else "No finite full row-weight vector",solver_dual_valid=sol.dual_valid,solver_feasibility_not_required=True))
    assert all(digest(ROOT/name)==h for name,h in bindings.items()),"Input changed"
    result=dict(timestamp=datetime.now(timezone.utc).isoformat(),status="CANDIDATE_SAME_MODEL_600S_REPLAY",
        model_status=str(solver.getModelStatus()),value_valid=sol.value_valid,dual_valid=sol.dual_valid,
        objective=info.objective_function_value if sol.value_valid else None,
        objective_null_reason=None if sol.value_valid else "No valid primal; raw info objective unusable",solve_seconds=elapsed,
        support_bound=None if bound is None else {k:bound[k] for k in ("numerator","denominator","approximate","strictly_positive")},
        output_sha256={p.name:digest(p) for p in args.out.iterdir() if p.is_file()},independent_bound_check_pending=True,
        family_exclusion_verified=False,target_resolution=False)
    save(args.out/"summary.json",result)
    print(json.dumps(result))


if __name__=="__main__":
    main()
