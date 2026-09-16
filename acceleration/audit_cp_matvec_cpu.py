"""Full99 exact dyadic matvec and rational two-step controls of native Rust CP."""
import argparse
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import time

from audit_phase1 import graph_rows

ROOT=Path(__file__).resolve().parents[1]


def require(ok,message):
    if not ok:
        raise ValueError(message)


def key(path):
    return path.resolve().relative_to(ROOT).as_posix()


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def write_new(path,data):
    with path.open("x",encoding="utf-8") as stream:
        stream.write(json.dumps(data,separators=(",",":"),allow_nan=False)+"\n")


def matvec(rows,x):
    return [sum((x[j] for j in row["terms"]),F(0)) for row in rows]


def transpose(rows,y):
    result=[F(0)]*1680
    for row,weight in zip(rows,y):
        for j in row["terms"]:
            result[j]+=weight
    return result


def bounds(rows,x,y):
    residual=[a-row["target"] for a,row in zip(matvec(rows,x),rows)]
    return (sum((abs(v) if i<840 else max(F(0),v) for i,v in enumerate(residual)),F(0)),
            -sum((row["target"]*weight for row,weight in zip(rows,y)),F(0))+
            sum((min(F(0),v) for v in transpose(rows,y)),F(0)))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--controls",type=Path,default=ROOT/"acceleration/results/20260916_phase1_chambolle_pock_cpu/summary.json")
    parser.add_argument("--binary",type=Path,default=ROOT/"acceleration/build/overlap_cp_cpu.exe")
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    require(not args.out.exists(),"Preserve previous audit")
    started=time.perf_counter()
    source_paths=[Path(__file__),ROOT/"acceleration/audit_phase1.py",ROOT/"acceleration/audit_certificate.py",
                  ROOT/"acceleration/overlap_cp_cpu.rs",args.binary,args.controls]
    inputs={key(path):digest(path) for path in source_paths}
    controls=json.loads(args.controls.read_bytes())
    require(controls["status"]=="INDEPENDENT_FULL99_CHAMBOLLE_POCK_CPU_QUALITY_CONTROL_PASS", "Unverified saved controls")
    cases=controls["controls"]
    require(len(cases)==5,"Expected five saved CPU control graphs")
    candidates=[]
    for case in cases:
        path=ROOT/Path(case["candidate_path"].replace("\\","/"))
        require(digest(path)==case["candidate_sha256"],"Control graph binding changed")
        inputs[key(path)]=digest(path)
        candidates.append(json.loads(path.read_bytes()))
    x=[F(i%5,4) for i in range(1680)]
    y=[F((i*5)%17-8,8) if i<840 else F((i*7)%9,8) for i in range(4326)]
    args.out.mkdir(parents=True,exist_ok=False)
    input_path=args.out/"dyadic_controls.txt"
    input_text="C99CP1 5 2\n1 2\n"+" ".join(str(float(v)) for v in x)+"\n"+" ".join(str(float(v)) for v in y)+"\n"
    for candidate in candidates:
        input_text+="\n".join(f"{u} {v}" for u,v in candidate["overlap_edges_outer_zero_based"])+"\n"
    input_path.write_text(input_text,encoding="ascii")
    native_path=args.out/"native.json"
    proc=subprocess.run([str(args.binary),str(input_path),str(native_path),"--vectors"],capture_output=True,text=True,timeout=60)
    require(proc.returncode==0,"Native failed: "+proc.stderr)
    native=json.loads(native_path.read_bytes())
    require(native["status"]=="NUMERICAL_MATRIXFREE_CP_CPU_CONTROL" and native["candidate_count"]==5,"Wrong native result")
    records=[]
    for case,candidate,result in zip(cases,candidates,native["results"]):
        edges,rows,omitted=graph_rows(candidate)
        require(len(edges)==1680 and len(rows)==4326 and len(omitted)==336,"Wrong full99 dimensions")
        require(all(len(row["terms"])==len(set(row["terms"])) for row in rows),"Repeated row column")
        a=matvec(rows,x);at=transpose(rows,y);b=[row["target"] for row in rows]
        require(result["initial_ax"]==list(map(float,a)),"Exact quarter-X forward product differs")
        require(result["initial_at_y"]==list(map(float,at)),"Exact eighth-Y transpose product differs")
        require(result["target_b"]==b,"Exact integer targets differ")
        require(result["row_sums"]==[len(row["terms"]) for row in rows],"Native row incidences differ")
        quota_counts=transpose(rows[:840],[F(1)]*840)
        cap_counts=transpose(rows[840:],[F(1)]*3486)
        require(quota_counts==[4]*1680 and cap_counts==[9]*1680 and result["column_sums"]==[13]*1680,"4quota/9cap column incidence failed")
        require(all(len(row["terms"])==8 for row in rows[:840]) and max(len(row["terms"]) for row in rows[840:])<=9,
                "Row incidence bound failed")
        require(sum(len(row["terms"]) for row in rows)==21840,"Nonzero count failed")
        require(sum((u*v for u,v in zip(x,at)),F(0))==sum((u*v for u,v in zip(y,a)),F(0)),"Exact adjoint identity failed")
        initial=bounds(rows,x,y)
        require(result["initial"]==dict(primal_upper=float(initial[0]),dual_lower=float(initial[1])),"Exact dyadic initial bounds differ")
        current_x=x.copy();current_y=y.copy();xbar=x.copy();xavg=[F(0)]*1680;yavg=[F(0)]*4326
        max_vector_error=0.0;max_bound_error=0.0;best_upper,best_lower=initial
        for step,checkpoint in enumerate(result["checkpoints"],1):
            require(checkpoint["iterations"]==step,"Unexpected checkpoint order")
            axbar=matvec(rows,xbar)
            current_y=[min(F(1),max(F(-1 if i<840 else 0),old+F(9,100)*(value-b[i])))
                       for i,(old,value) in enumerate(zip(current_y,axbar))]
            aty=transpose(rows,current_y)
            next_x=[min(F(1),max(F(0),old-F(9,100)*value)) for old,value in zip(current_x,aty)]
            xbar=[2*new-old for new,old in zip(next_x,current_x)];current_x=next_x
            xavg=[old+(new-old)/step for old,new in zip(xavg,current_x)]
            yavg=[old+(new-old)/step for old,new in zip(yavg,current_y)]
            for name,expected in (("x_last",current_x),("y_last",current_y),("x_average",xavg),("y_average",yavg)):
                require(len(checkpoint[name])==len(expected),"Vector shape mismatch")
                error=max(abs(float(a)-b) for a,b in zip(expected,checkpoint[name]))
                require(error<=1e-12,"Rational CP update differs: "+name)
                max_vector_error=max(max_vector_error,error)
            last=bounds(rows,current_x,current_y);average=bounds(rows,xavg,yavg)
            for name,expected in (("last",last),("average",average)):
                error=max(abs(checkpoint[name]["primal_upper"]-float(expected[0])),abs(checkpoint[name]["dual_lower"]-float(expected[1])))
                require(error<=1e-8,"Rational CP bound differs")
                max_bound_error=max(max_bound_error,error)
            best_upper=min(best_upper,last[0],average[0]);best_lower=max(best_lower,last[1],average[1])
            require(abs(checkpoint["best_upper"]-float(best_upper))<=1e-8 and abs(checkpoint["best_lower"]-float(best_lower))<=1e-8,"Best checkpoint bound differs")
        require(len(result["checkpoints"])==2,"Missing checkpoint")
        records.append(dict(shape=case["shape"],candidate_path=case["candidate_path"],candidate_sha256=case["candidate_sha256"],
                            forward_entries_exact=4326,transpose_entries_exact=1680,target_entries_exact=4326,
                            all_row_column_incidences_exact=True,quota_incidence_per_column=4,cap_incidence_per_column=9,
                            nonzeros=21840,squared_operator_norm_bound=117,exact_adjoint_identity=True,
                            cp_checkpoints=[1,2],cp_reference_step="9/100 exact rational",maximum_cp_vector_error=max_vector_error,
                            maximum_cp_bound_error=max_bound_error))
    require(all(digest(ROOT/path)==expected for path,expected in inputs.items()),"Bound source/input changed during audit")
    report=dict(status="INDEPENDENT_FULL99_DYADIC_MATRIXFREE_MATVEC_AND_RATIONAL_CP_CONTROL_PASS",inputs_sha256=inputs,
                outputs_sha256={key(path):digest(path) for path in (input_path,native_path)},records=records,
                candidate_count=5,forward_entries_exact=5*4326,transpose_entries_exact=5*1680,target_entries_exact=5*4326,
                all_column_incidence_checks=5*1680,full_constraint_matrix_used_only_by_independent_checker=True,
                native_constraint_matrix_materialized=False,native_stderr=proc.stderr.strip(),
                maximum_cp_vector_error=max(row["maximum_cp_vector_error"] for row in records),
                maximum_cp_bound_error=max(row["maximum_cp_bound_error"] for row in records),
                optimizer_or_native_producer_mapping_imported=False,elapsed_seconds=time.perf_counter()-started,
                scope="Five real saved K controls. Initial matvecs/transpose/targets match exactly on quarter-X/eighth-Y. Two native floating CP steps agree with exact rational9/100 recurrence within stated tolerances. No convergence, optimum, infeasibility or completion claim.")
    write_new(args.out/"audit.json",report)
    print(json.dumps({name:report[name] for name in ("status","candidate_count","maximum_cp_vector_error","maximum_cp_bound_error","elapsed_seconds")}))


if __name__=="__main__":
    main()
