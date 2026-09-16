"""Check all scalar results across the frozen CUDA 256-candidate tile boundary.

Repeat the independently validated five dyadic controls to make257 candidates.
No native producer is imported and no existing artifact is overwritten.
"""
import argparse
from hashlib import sha256
import json
import math
from pathlib import Path
import subprocess
import time

from audit_certificate import full_graph, require


ROOT=Path(__file__).resolve().parents[1]


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def key(path):
    return path.resolve().relative_to(ROOT).as_posix()


def parse(path):
    tokens=path.read_text(encoding="ascii").split()
    require(tokens[0]=="C99CP1","Input header differs")
    count,ncheck=map(int,tokens[1:3])
    checkpoints=list(map(int,tokens[3:3+ncheck]))
    cursor=3+ncheck
    x=list(map(float,tokens[cursor:cursor+1680]));cursor+=1680
    y=list(map(float,tokens[cursor:cursor+4326]));cursor+=4326
    require(len(tokens)==cursor+count*336,"Input token count differs")
    candidates=[]
    for i in range(count):
        endpoints=list(map(int,tokens[cursor+i*336:cursor+(i+1)*336]))
        candidates.append([endpoints[j:j+2] for j in range(0,336,2)])
    return count,checkpoints,x,y,candidates


def scalars(record):
    values=[record["initial"]["primal_upper"],record["initial"]["dual_lower"]]
    for checkpoint in record["checkpoints"]:
        values.extend(checkpoint[part][field] for part in ("last","average") for field in ("primal_upper","dual_lower"))
        values.extend([checkpoint["best_upper"],checkpoint["best_lower"]])
    return values


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    require(not args.out.exists(),"Preserve prior tile-boundary controls")
    args.out.mkdir(parents=True)
    started=time.perf_counter()
    prior_dir=ROOT/"acceleration/results/20260916_cp_native_matvec_qa"
    original_input,original_output,original_audit=[prior_dir/name for name in ("dyadic_controls.txt","native.json","audit.json")]
    executable=ROOT/"acceleration/build/overlap_cp_gpu.exe"
    source=ROOT/"acceleration/overlap_cp_gpu.cu"
    require(digest(executable)=="6ddc99a1fa55fd3880f3ce6d1a50e63d4144c1915e6bf30eb6c18abf25865e6d" and
            digest(source)=="4ae8a33b53df5176eedfd94f950ee9de2a667bcc850e69069af86049b96344a8","Frozen CUDA binding changed")
    prior=json.loads(original_audit.read_bytes())
    require(prior["status"]=="INDEPENDENT_FULL99_DYADIC_MATRIXFREE_MATVEC_AND_RATIONAL_CP_CONTROL_PASS","Original Rust control was not independently validated")
    bindings={key(path):digest(path) for path in (original_input,original_output,original_audit,executable,source,Path(__file__),Path(__file__).with_name("audit_certificate.py"))}
    for field in ("inputs_sha256","outputs_sha256"):
        for name,expected in prior[field].items():
            require(digest(ROOT/name)==expected,"Changed original control dependency: "+name)
            bindings[name]=expected
    count,checkpoints,x,y,candidates=parse(original_input)
    require(count==5 and checkpoints==[1,2],"Unexpected original control dimensions")
    require(all(math.isfinite(v) and 0<=v<=1 and v*4==int(v*4) for v in x),"Original X is not a valid quarter control")
    require(all(math.isfinite(v) and (-1 if i<840 else 0)<=v<=1 and v*8==int(v*8) for i,v in enumerate(y)),"Original Y is not a valid eighth control")
    for candidate in candidates:
        full_graph({"overlap_edges_outer_zero_based":candidate})
    reference=json.loads(original_output.read_bytes())
    require(reference["candidate_count"]==5 and [r["candidate_index"] for r in reference["results"]]==list(range(5)),"Original Rust output ordering differs")
    repeated=[candidates[i%5] for i in range(257)]
    input_path,output_path=args.out/"input.txt",args.out/"gpu.json"
    with input_path.open("x",encoding="ascii",newline="\n") as stream:
        stream.write("C99CP1 257 2\n1 2\n")
        stream.write(" ".join(format(value,".17g") for value in x)+"\n")
        stream.write(" ".join(format(value,".17g") for value in y)+"\n")
        for edges in repeated:
            stream.write(" ".join(str(v) for edge in edges for v in edge)+"\n")
    decoded=parse(input_path)
    require(decoded==(257,[1,2],x,y,repeated),"Independent input readback/order differs")
    completed=subprocess.run([str(executable),str(input_path),str(output_path)],check=True,capture_output=True,text=True)
    actual=json.loads(output_path.read_bytes())
    require(actual["status"]=="NUMERICAL_CHAMBOLLE_POCK_PHASE1_HEURISTIC" and actual["candidate_count"]==257 and actual["checkpoints"]==[1,2],"CUDA output dimensions/status differ")
    require(actual["kernel_launches"]==2 and actual["launch_candidate_batch_limit"]==256,"Tile boundary was not exercised")
    require(actual["tau"]==actual["sigma"]==.09 and actual["theta"]==1,"CP parameters differ")
    require(len(actual["results"])==257 and [r["candidate_index"] for r in actual["results"]]==list(range(257)),"Global output index ordering differs")
    records=[]
    maximum_error=0.0
    for i,result in enumerate(actual["results"]):
        control=i%5
        require([cp["iterations"] for cp in result["checkpoints"]]==[1,2],"Candidate checkpoint order differs")
        require(all(not any(field in cp for field in ("x_last","y_last","x_average","y_average")) for cp in result["checkpoints"]),"Expected scalar-only output")
        got,expected=scalars(result),scalars(reference["results"][control])
        require(len(got)==len(expected)==14 and all(math.isfinite(v) for v in got),"Invalid scalar dimensions/values")
        error=max(abs(a-b) for a,b in zip(got,expected))
        require(error<1e-7,"CUDA scalar differs from independently audited Rust control")
        require(got==scalars(actual["results"][control]),"Repeated candidate produced different CUDA scalar bits")
        maximum_error=max(maximum_error,error)
        records.append(dict(candidate_index=i,original_control_index=control,launch_index=i//256,max_absolute_error=error))
    require(all(digest(ROOT/name)==expected for name,expected in bindings.items()),"Source or original control changed")
    report=dict(status="INDEPENDENT_CP_GPU_257_CANDIDATE_TILE_BOUNDARY_SCALAR_CONTROL_PASS",inputs_sha256=bindings,
                outputs_sha256={key(path):digest(path) for path in (input_path,output_path)},
                original_control_count=5,candidate_count=257,checkpoints=[1,2],
                mapping_rule="Global candidate i repeats independently validated original control i modulo5",
                independently_read_back_input_and_global_output_order=True,full99_unique_control_graphs_checked=5,
                scalar_comparisons=257*14,maximum_absolute_error=maximum_error,absolute_tolerance=1e-7,
                all_same_control_repetitions_bitwise_scalar_identical=True,
                kernel_launches=actual["kernel_launches"],candidate_tile_limit=actual["launch_candidate_batch_limit"],
                boundary_records=[records[i] for i in (254,255,256)],records=records,
                cuda_kernel_seconds=actual["kernel_seconds"],cuda_transfer_and_kernel_seconds=actual["elapsed_seconds"],
                process_stdout=completed.stdout.strip(),elapsed_seconds=time.perf_counter()-started,
                source_mutations=False,new_gpu_invocations=1,native_producer_imported=False,
                scope="Small scalar regression across the actual256candidate CUDA tile boundary, including indices255and256. No full-family rerun, performancebenchmark, proof, or exclusion.")
    with (args.out/"report.json").open("x",encoding="utf-8") as stream:
        stream.write(json.dumps(report,indent=2)+"\n")
    print(json.dumps({field:report[field] for field in ("status","candidate_count","scalar_comparisons","maximum_absolute_error","kernel_launches","cuda_kernel_seconds","elapsed_seconds")}))


if __name__=="__main__":
    main()
