"""One gated2400-second solve of the frozen four-coordinate filtered model."""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import highspy
import numpy as np
from scipy.sparse import load_npz
from theory_20260917_partial_matching_moments import digest,save,exact_bound

ROOT=Path(__file__).resolve().parents[1]
MODEL_PATH="acceleration/results/20260917_four_matching_filtered_moments"
FILTER_PATH="acceleration/results/20260917_four_coordinate_matching_filter/run01"
RESOURCE="acceleration/results/20260917_resume/four_filtered_resource_preflight.json"


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out",type=Path,required=True);p.add_argument("--filter-review",type=Path,required=True);p.add_argument("--model-review",type=Path,required=True)
    args=p.parse_args();out=args.out
    bindings={}
    def bind(path):
        path=Path(path).resolve();name=path.relative_to(ROOT).as_posix();bindings[name]=digest(path)
        return json.loads(path.read_bytes())
    filt=bind(args.filter_review);audit=bind(args.model_review);resource=bind(ROOT/RESOURCE)
    assert "PASS" in filt["status"] and "PASS" in audit["status"]
    def checked_input(report,name):
        hashes={key.replace("\\","/"):value for key,value in report["inputs_sha256"].items()}
        assert hashes[name]==digest(ROOT/name),f"Audit input mismatch: {name}"
    checked_input(filt,FILTER_PATH+"/summary.json")
    for name in ("model.json","integer_augmented_csr.npz"):checked_input(audit,MODEL_PATH+"/"+name)
    model=bind(ROOT/MODEL_PATH/"model.json");manifest=bind(ROOT/MODEL_PATH/"build_manifest.json");bind(ROOT/MODEL_PATH/"build_summary.json")
    assert manifest["solver_preregistration"]["time_limit_seconds"]==2400
    assert resource["free_physical_memory_KiB"]>0 and resource["drive_C_free_bytes"]>0
    for name,h in manifest["inputs_sha256"].items():assert digest(ROOT/name)==h,"Frozen build input changed"
    for name in (MODEL_PATH+"/integer_augmented_csr.npz",Path(__file__).relative_to(ROOT).as_posix(),"acceleration/theory_20260917_partial_matching_moments.py","uv.lock"):
        bindings[name]=digest(ROOT/name)
    out.mkdir(parents=True,exist_ok=True);assert not any(out.iterdir())
    save(out/"manifest.json",dict(timestamp=datetime.now(timezone.utc).isoformat(),
        source_commit=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),command_argv=[sys.executable,*sys.argv],working_directory=str(Path.cwd()),
        python=platform.python_version(),highs=highspy.Highs().version(),inputs_sha256=bindings,
        model=model["model"],scope=manifest["scope"],selection=manifest["selection"],configuration=manifest["solver_preregistration"],
        gate_outcomes=dict(filter=filt["status"],model=audit["status"],resource="Parent authorized single2400-second attempt after recorded RAM/disk observation; resources notreserved"),
        criterion=manifest["acceptance"],single_attempt=True,automatic_retries=False,target_resolution=False))
    A=load_npz(ROOT/MODEL_PATH/"integer_augmented_csr.npz")
    assert list(A.shape)==model["shape"] and A.nnz==model["nonzeros"]
    lp=highspy.HighsLp();lp.num_row_,lp.num_col_=A.shape
    lp.col_cost_=np.array(model["costs"],dtype=float);lp.col_lower_=np.zeros(lp.num_col_);lp.col_upper_=np.full(lp.num_col_,highspy.kHighsInf)
    lp.row_lower_=np.array(model["rhs"],dtype=float);lp.row_upper_=lp.row_lower_.copy()
    lp.a_matrix_.format_=highspy.MatrixFormat.kRowwise
    lp.a_matrix_.start_=A.indptr;lp.a_matrix_.index_=A.indices;lp.a_matrix_.value_=A.data.astype(float)
    solver=highspy.Highs()
    for key,value in (("output_flag",True),("threads",1),("solver","ipm"),("run_crossover","off"),("time_limit",2400.0),("log_file",str(out/"highs.log"))):
        assert solver.setOptionValue(key,value)==highspy.HighsStatus.kOk
    assert solver.passModel(lp)==highspy.HighsStatus.kOk
    start=time.monotonic();status=solver.run();elapsed=time.monotonic()-start
    sol,info=solver.getSolution(),solver.getInfo()
    raw=dict(timestamp=datetime.now(timezone.utc).isoformat(),run_status=str(status),model_status=str(solver.getModelStatus()),
        value_valid=sol.value_valid,dual_valid=sol.dual_valid,raw_info_objective=info.objective_function_value,objective_usable=bool(sol.value_valid),
        solve_seconds=elapsed,col_value=list(sol.col_value),col_dual=list(sol.col_dual),row_value=list(sol.row_value),row_dual=list(sol.row_dual),
        invalid_vector_policy="Invalid vectors are not feasible solutions; arbitrary finite row weights can still yield exact algebraic support bounds")
    save(out/"numeric_lp.json",raw)
    n=model["probability_offsets"][-1];hard=84+len(model["unknown_edges"]);weights=np.array(sol.row_dual)
    bound=exact_bound(A[84:hard,:n],A[hard:,:n],np.array(model["rhs"][hard:],dtype=np.int64),model["probability_offsets"],weights) if len(weights)==A.shape[0] and np.all(np.isfinite(weights)) else None
    save(out/"exact_support_bound.json",dict(bound=bound,null_reason=None if bound else "No finite full row-weight vector",solver_dual_valid=sol.dual_valid,solver_feasibility_not_required=True,
        domain_ids=MODEL_PATH+"/model.json#retained_original_domain_ids",requires_independent_removed_choices_and_raw_neighborhood_bound_review=True))
    chunks=[]
    for artifact in (out/"numeric_lp.json",):
        if artifact.stat().st_size<=10*1024*1024:continue
        parts=[]
        with artifact.open("rb") as source:
            i=0
            while data:=source.read(8*1024*1024):
                name=artifact.name+f".part{i:03d}"
                with (out/name).open("xb") as dest:dest.write(data)
                parts.append(dict(path=name,bytes=len(data),sha256=digest(out/name)));i+=1
        chunks.append(dict(source=artifact.name,source_bytes=artifact.stat().st_size,source_sha256=digest(artifact),source_availability="LOCAL_ONLY",parts=parts))
    save(out/"chunk_manifest.json",dict(schema_version=1,chunk_bytes=8*1024*1024,artifacts=chunks,recovery="Verify parts, concatenate inorder into freshfile, verify fullsize/hash"))
    assert all(digest(ROOT/name)==h for name,h in bindings.items())
    result=dict(timestamp=datetime.now(timezone.utc).isoformat(),status="CANDIDATE_FOUR_COORDINATE_FILTERED_MOMENT_SOLVE",model=model["model"],
        model_status=raw["model_status"],value_valid=sol.value_valid,dual_valid=sol.dual_valid,
        objective=info.objective_function_value if sol.value_valid else None,objective_null_reason=None if sol.value_valid else "No valid primal; rawinfo objective unusable",
        solve_seconds=elapsed,support_bound=None if bound is None else {k:bound[k] for k in ("numerator","denominator","approximate","strictly_positive")},
        retained_probability_choices=n,original_probability_choices=290460,removed_choices=59581,
        output_sha256={f.name:digest(f) for f in out.iterdir() if f.is_file()},independent_bound_review_pending=True,family_exclusion_verified=False,target_resolution=False)
    save(out/"summary.json",result)
    print(json.dumps({k:result[k] for k in ("model_status","value_valid","dual_valid","objective","solve_seconds","support_bound")}))


if __name__=="__main__":main()
