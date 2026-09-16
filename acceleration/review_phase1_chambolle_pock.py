"""Independent full99 CPU quality control for approximate phase-I reoptimization.

No optimization producer is imported and no LP is solved. Exact reference
intervals are reused only after checking their candidate/result/source hashes.
Chambolle-Pock iterates and their reported bounds remain numerical diagnostics.
"""
import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import time

import numpy as np
import scipy
from scipy.sparse import csr_matrix

from audit_certificate import require
from audit_phase1 import graph_rows, evaluate


ROOT=Path(__file__).resolve().parents[1]
STEPS=(500,2000,10000)


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def path_key(path):
    return path.resolve().relative_to(ROOT).as_posix()


def write_json(path,value):
    with path.open("x",encoding="utf-8") as stream:
        stream.write(json.dumps(value,separators=(",",":"))+"\n")


def partition(base, edges):
    current=set(map(tuple,edges))
    removed,added=base-current,current-base
    if not removed:
        require(not added,"Initial candidate edge identity mismatch")
        return []
    red,blue={},{}
    for pairs,adj in ((removed,red),(added,blue)):
        for u,v in pairs:
            require(u not in adj and v not in adj,"Selected control is not a whole matching move")
            adj[u],adj[v]=v,u
    require(set(red)==set(blue),"Changed endpoint sets differ")
    left=set(red)
    sizes=[]
    while left:
        first=u=min(left)
        length=0
        while True:
            require(u in left and red[u] in left,"Broken alternating component")
            left.remove(u)
            left.remove(red[u])
            length+=1
            u=blue[red[u]]
            if u==first:
                break
        sizes.append(length)
    return sorted(sizes)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace-audit",type=Path,required=True)
    parser.add_argument("--warm-phase1",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    require(not args.out.exists(),"Preserve previous study")
    args.out.mkdir(parents=True)
    started=time.perf_counter()
    bindings={path_key(path):digest(path) for path in (args.trace_audit,args.warm_phase1,Path(__file__),
               ROOT/"acceleration/audit_phase1.py",ROOT/"acceleration/audit_certificate.py")}
    trace=json.loads(args.trace_audit.read_bytes())
    require(trace["status"]=="INDEPENDENT_WHOLE_MATCHING_TRACE_GRAPH_MODELS_MERITS_SELECTION_AND_NATIVE_GATE_BINDINGS_AUDIT_PASS", "Expected independently audited reference probes")
    warm=json.loads(args.warm_phase1.read_bytes())
    warm_candidate_path=Path(warm["candidate_path"])
    require(digest(warm_candidate_path)==warm["candidate_sha256"],"Warm candidate SHA differs")
    warm_candidate=json.loads(warm_candidate_path.read_bytes())
    base=set(map(tuple,warm_candidate["overlap_edges_outer_zero_based"]))
    warm_x=np.asarray(warm["numeric_edge_values"],dtype=np.float64)
    require(warm_x.shape==(1680,) and np.all(np.isfinite(warm_x)) and np.all((warm_x>=0)&(warm_x<=1)),"Invalid warm X")
    expected_edges,warm_rows,_=graph_rows(warm_candidate)
    require(warm["edge_variables"]==list(map(list,expected_edges)),"Warm X column ordering mismatch")
    warm_duals={(row["kind"],tuple(row["coordinate"])):value for row,value in zip(warm["constraint_groups"],warm["phase1_multipliers"])}
    bindings[path_key(warm_candidate_path)]=digest(warm_candidate_path)
    controls_by_shape={}
    for probe in trace["probe_records"]:
        if not probe["usable_numerical_optimum"]:
            continue
        result_path=Path(probe["result_path"])
        result=json.loads(result_path.read_bytes())
        candidate_path=Path(result["candidate_path"])
        candidate=json.loads(candidate_path.read_bytes())
        shape=partition(base,candidate["overlap_edges_outer_zero_based"])
        key="+".join(map(str,shape)) if shape else "baseline"
        if key not in ("baseline","2+2","5","6","2+4"):
            continue
        if key not in controls_by_shape or probe["numeric_objective"]<controls_by_shape[key]["probe"]["numeric_objective"]:
            controls_by_shape[key]=dict(probe=probe,candidate_path=candidate_path,result_path=result_path,candidate=candidate,shape=shape)
    require(set(controls_by_shape)=={"baseline","2+2","5","6","2+4"},"Saved probes lack a requested extended shape")
    outputs=[]
    reports=[]
    for key in ("baseline","2+2","5","6","2+4"):
        selected=controls_by_shape[key]
        probe,candidate=selected["probe"],selected["candidate"]
        reference=probe["independent_primal_dual_audit"]
        require(reference["status"]=="INDEPENDENT_PHASE1_GRAPH_MODEL_PRIMAL_DUAL_AUDIT_PASS","Reference exact interval was not independently audited")
        for name,expected in reference["inputs_sha256"].items():
            path=Path(name)
            require(digest(path)==expected,"Reference candidate/result binding changed")
            bindings[path_key(path)]=expected
        require(digest(ROOT/"acceleration/audit_phase1_kkt.py")==reference["auditor_sha256"] and
                digest(ROOT/"acceleration/audit_certificate.py")==reference["graph_auditor_sha256"],"Reference auditor changed")
        bindings["acceleration/audit_phase1_kkt.py"]=reference["auditor_sha256"]
        lower_ref=reference["exact_dual_lower_bound"]
        upper_ref=reference["exact_primal_upper_bound"]
        ref_lower=Fraction(int(lower_ref["numerator"]),int(lower_ref["denominator"]))
        ref_upper=Fraction(int(upper_ref["numerator"]),int(upper_ref["denominator"]))
        require(ref_lower<=ref_upper,"Invalid exact reference interval")
        edges,rows,omitted=graph_rows(candidate)
        require(edges==expected_edges and len(omitted)==336,"Changed graph coordinate geometry")
        row_ids,col_ids=[],[]
        for i,row in enumerate(rows):
            require(len(row["terms"])==len(set(row["terms"])),"Unexpected duplicate row term")
            row_ids.extend([i]*len(row["terms"]))
            col_ids.extend(row["terms"])
        A=csr_matrix((np.ones(len(col_ids),dtype=np.float64),(row_ids,col_ids)),shape=(4326,1680))
        AT=A.transpose().tocsr()
        b=np.asarray([row["target"] for row in rows],dtype=np.float64)
        row_sums=np.asarray(A.sum(axis=1)).ravel()
        col_sums=np.asarray(A.sum(axis=0)).ravel()
        quota_cols=np.asarray(A[:840].sum(axis=0)).ravel()
        cap_cols=np.asarray(A[840:].sum(axis=0)).ravel()
        require(np.all(quota_cols==4) and np.all(cap_cols==9) and np.all(col_sums==13),"Column incidence bound failed")
        require(np.all(row_sums[:840]==8) and np.max(row_sums[840:])<=9 and A.nnz==21840,"Row bound or nonzero count failed")
        norm_squared_bound=int(np.max(row_sums)*np.max(col_sums))
        require(norm_squared_bound<=117 and Fraction(9,100)**2*norm_squared_bound<1,"Unsafe Chambolle-Pock step")
        y_lower=np.r_[np.full(840,-1.0),np.zeros(3486)]
        reused_y=np.asarray([warm_duals.get((row["kind"],tuple(row["coordinate"])),0.0) for row in rows],dtype=np.float64)
        reused_y=np.clip(reused_y,y_lower,1.0)
        case=dict(shape=key,cycle_sizes=selected["shape"],candidate_path=path_key(selected["candidate_path"]),
                  candidate_sha256=digest(selected["candidate_path"]),reference_result_path=path_key(selected["result_path"]),
                  exact_reference_interval=dict(lower=lower_ref,upper=upper_ref),
                  independent_matrix=dict(rows=4326,columns=1680,nonzeros=A.nnz,quota_rows=840,pair_rows=3486,
                    omitted_zero_own_label_rows=336,column_absolute_sum_histogram=dict(Counter(map(int,col_sums))),
                    row_absolute_sum_histogram=dict(Counter(map(int,row_sums))),quota_column_incidence=4,pair_column_incidence=9,
                    norm_squared_upper_bound=norm_squared_bound,stepsize_product_times_norm_squared=.09*.09*norm_squared_bound),runs=[])

        def numeric_bounds(x,y):
            residual=A@x-b
            primal=float(np.abs(residual[:840]).sum()+np.maximum(residual[840:],0).sum())
            dual=float(-b@y+np.minimum(AT@y,0).sum())
            require(primal+1e-7>=float(ref_lower) and dual-1e-7<=float(ref_upper) and dual<=primal+1e-7,
                    "Numerical CP bounds contradict independent exact LP interval")
            return dict(primal_upper_numeric=primal,dual_lower_numeric=dual,numeric_gap=primal-dual,
                        upper_excess_over_reference_upper=primal-float(ref_upper),lower_shortfall_from_reference_lower=float(ref_lower)-dual)

        def independent_check(x,y,actual):
            reference_primal=evaluate(candidate,x.tolist())["total_violation"]
            coefficients=[0.0]*1680
            rhs=0.0
            for row,weight in zip(rows,y.tolist()):
                rhs+=row["target"]*weight
                for column in row["terms"]:
                    coefficients[column]+=weight
            reference_dual=-rhs+sum(min(0,value) for value in coefficients)
            error=max(abs(reference_primal-actual["primal_upper_numeric"]),abs(reference_dual-actual["dual_lower_numeric"]))
            require(error<1e-8,"Independent full99 scalar bounds differ from sparse implementation")
            return error

        for initialization,y0 in (("zero_dual",np.zeros(4326)),("current_dual",reused_y)):
            x=warm_x.copy()
            y=y0.copy()
            xbar=x.copy()
            xavg=np.zeros(1680)
            yavg=np.zeros(4326)
            initial_bounds=numeric_bounds(x,y)
            best_upper=initial_bounds["primal_upper_numeric"]
            best_lower=initial_bounds["dual_lower_numeric"]
            checkpoints=[]
            computation_seconds=0.0
            segment_started=time.perf_counter()
            vectors=[]
            for step in range(1,STEPS[-1]+1):
                y=np.clip(y+.09*(A@xbar-b),y_lower,1.0)
                xnew=np.clip(x-.09*(AT@y),0.0,1.0)
                xbar=2*xnew-x
                x=xnew
                xavg+=(x-xavg)/step
                yavg+=(y-yavg)/step
                if step in STEPS:
                    computation_seconds+=time.perf_counter()-segment_started
                    require(np.all(np.isfinite(x)) and np.all(np.isfinite(y)) and np.all((x>=0)&(x<=1)) and np.all((y>=y_lower)&(y<=1)),"Nonfinite or infeasible iterate")
                    last=numeric_bounds(x,y)
                    average=numeric_bounds(xavg,yavg)
                    error=max(independent_check(x,y,last),independent_check(xavg,yavg,average))
                    best_upper=min(best_upper,last["primal_upper_numeric"],average["primal_upper_numeric"])
                    best_lower=max(best_lower,last["dual_lower_numeric"],average["dual_lower_numeric"])
                    checkpoint=dict(iterations=step,last=last,ergodic_average=average,
                                    best_upper_over_initial_and_checked_points=best_upper,best_lower_over_initial_and_checked_points=best_lower,
                                    best_checked_numeric_gap=best_upper-best_lower,independent_bound_scalar_error=error,
                                    iteration_computation_seconds=computation_seconds)
                    checkpoints.append(checkpoint)
                    vectors.append(dict(iterations=step,x_last=x.tolist(),y_last=y.tolist(),x_average=xavg.tolist(),y_average=yavg.tolist()))
                    print(json.dumps(dict(shape=key,initialization=initialization,iterations=step,reference=float(ref_upper),
                                          start_upper=initial_bounds["primal_upper_numeric"],last_upper=last["primal_upper_numeric"],last_lower=last["dual_lower_numeric"],
                                          average_upper=average["primal_upper_numeric"],best_upper=best_upper)),flush=True)
                    segment_started=time.perf_counter()
            vector_path=args.out/f"{key.replace('+','_')}_{initialization}_iterates.json"
            write_json(vector_path,dict(shape=key,initialization=initialization,checkpoints=vectors))
            outputs.append(vector_path)
            case["runs"].append(dict(initialization=initialization,initial_bounds=initial_bounds,checkpoints=checkpoints,
                                     saved_iterates_path=path_key(vector_path),saved_iterates_sha256=digest(vector_path),
                                     improvement_at10000=initial_bounds["primal_upper_numeric"]-best_upper))
        reports.append(case)
    require(all(digest(ROOT/name)==expected for name,expected in bindings.items()),"Study inputs/source changed")
    report=dict(status="INDEPENDENT_FULL99_CHAMBOLLE_POCK_CPU_QUALITY_CONTROL_PASS",inputs_sha256=bindings,
                outputs_sha256={path_key(path):digest(path) for path in outputs},controls=reports,
                selection_rule="Unchanged baseline and the lowest saved audited numerical optimum in each of cycle partitions2+2,5,6,2+4 among whole-matching pilot probes; no LP reruns.",
                control_count=len(reports),initializations=["current X +zero dual","current X +clipped current dual"],
                checkpoints=list(STEPS),tau=.09,sigma=.09,theta=1,
                scipy_version=scipy.__version__,numpy_version=np.__version__,float_type="float64",
                operator_squared_norm_uniform_upper_bound=117,step_product_upper_bound=.9477,
                lp_solver_reruns=0,optimization_producer_imported=False,cp_numeric_values_used_as_proof=False,
                reference_exact_audited_intervals_reused=True,
                independent_full99_checkpoints_compared=len(reports)*2*len(STEPS)*2,
                elapsed_seconds=time.perf_counter()-started,
                primary_algorithm_reference="https://link.springer.com/article/10.1007/s10851-010-0251-1",
                scope="Bounded numerical algorithm quality study on five explicitly selected labeled graphs. CP floating primal/dual evaluations are diagnostics only, not certificates or exclusion decisions. No GPU implementation or full-family approximate optimization was performed.")
    write_json(args.out/"summary.json",report)
    print(json.dumps({key:report[key] for key in ("status","control_count","operator_squared_norm_uniform_upper_bound","independent_full99_checkpoints_compared","elapsed_seconds")}))


if __name__=="__main__":
    main()
