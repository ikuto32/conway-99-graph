"""Bounded layout-only CUDA comparison: saved QA,257boundary,512Kx500steps.

Preserves both implementations and all earlier artifacts. Timings are paired
measurements of the same explicit512-candidate batch, not a full-family claim.
"""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import statistics
import subprocess
import time

from audit_certificate import full_graph, require
from review_cp_gpu_tile_boundary import parse, scalars


ROOT=Path(__file__).resolve().parents[1]


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def key(path):
    return path.resolve().relative_to(ROOT).as_posix()


def save(path,value):
    with path.open("x",encoding="utf-8") as stream:
        stream.write(json.dumps(value,indent=2)+"\n")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    require(not args.out.exists(),"Preserve previous layout comparison")
    args.out.mkdir(parents=True)
    started=time.perf_counter()
    source_old=ROOT/"acceleration/overlap_cp_gpu.cu"
    source_new=ROOT/"acceleration/overlap_cp_gpu_layout_v2.cu"
    binary_old=ROOT/"acceleration/build/overlap_cp_gpu.exe"
    binary_new=ROOT/"acceleration/build/overlap_cp_gpu_layout_v2.exe"
    qa_dir=ROOT/"acceleration/results/20260916_cp_gpu_layout_v2_controls"
    qa_path=qa_dir/"audit.json"
    tile_dir=ROOT/"acceleration/results/20260916_cp_gpu_tile_boundary"
    tile_report_path,tile_input=tile_dir/"report.json",tile_dir/"input.txt"
    family_dir=ROOT/"acceleration/results/20260916_whole_matching_qa"
    family_path,family_audit_path=family_dir/"all.json",family_dir/"all_independent_audit.json"
    reference_path=ROOT/"acceleration/results/20260916_cp_native_matvec_qa/native.json"
    paths=[source_old,source_new,binary_old,binary_new,Path(__file__),Path(__file__).with_name("review_cp_gpu_tile_boundary.py"),
           Path(__file__).with_name("audit_certificate.py"),qa_path,tile_report_path,tile_input,family_path,family_audit_path,reference_path,
           ROOT/"acceleration/build_overlap_cp_gpu_layout_v2.ps1"]
    bindings={key(path):digest(path) for path in paths}
    require(digest(source_old)=="4ae8a33b53df5176eedfd94f950ee9de2a667bcc850e69069af86049b96344a8" and
            digest(binary_old)=="6ddc99a1fa55fd3880f3ce6d1a50e63d4144c1915e6bf30eb6c18abf25865e6d","Original CUDA version changed")
    require(digest(source_new)=="43b1452adee28f01f90e227875f7d08bab6dad8141041c2036945fcd122cc389" and
            digest(binary_new)=="42dbd7ea8f41d9b195d4bfb2c900e5edcd6feec8dd58b9d68f777bca889c065e","Frozen layout version changed")
    qa=json.loads(qa_path.read_bytes())
    require(qa["status"]=="INDEPENDENT_CP_GPU_SAVED_CPU_AND_DIRECT_SHORT_REPLAY_AUDIT_PASS","Layout version lacks positive independent QA")
    tile_report=json.loads(tile_report_path.read_bytes())
    require(tile_report["status"]=="INDEPENDENT_CP_GPU_257_CANDIDATE_TILE_BOUNDARY_SCALAR_CONTROL_PASS","Original tile boundary was not audited")
    family_audit=json.loads(family_audit_path.read_bytes())
    require(family_audit["status"]=="INDEPENDENT_COMPLETE_WHOLE_SAME_SIGN_MATCHING_FAMILY_PASS","Benchmark family not independently checked")
    for payload in (qa,tile_report,family_audit):
        for field in ("inputs_sha256","outputs_sha256"):
            for name,expected in payload.get(field,{}).items():
                path=Path(name)
                if not path.is_absolute():path=ROOT/path
                require(digest(path)==expected,"Changed reference dependency: "+name)
                bindings[key(path)]=expected
    old_text,new_text=source_old.read_text(),source_new.read_text()
    extract=lambda text,start,end:text[text.index(start):text.index(end,text.index(start))]
    require(extract(old_text,"__global__ void cp_kernel","\nint main")==extract(new_text,"__global__ void cp_kernel","\nint main"),"CP kernel recurrence/synchronization changed")
    require(extract(old_text,"    for(int candidate=0;candidate<count;++candidate)","    CUDA(cudaSetDevice(0))")==
            extract(new_text,"    for(int candidate=0;candidate<count;++candidate)","    CUDA(cudaSetDevice(0))"),"Input graph/RHS validation changed")
    outputs=[]
    tile_output=args.out/"tile257_gpu.json"
    subprocess.run([str(binary_new),str(tile_input),str(tile_output)],check=True,capture_output=True,text=True)
    tiled=json.loads(tile_output.read_bytes())
    original=json.loads(reference_path.read_bytes())
    require(tiled["candidate_count"]==257 and tiled["kernel_launches"]==2 and tiled["checkpoints"]==[1,2] and
            [r["candidate_index"] for r in tiled["results"]]==list(range(257)),"Layout tile dimensions/order differ")
    tile_max=0.0
    for i,result in enumerate(tiled["results"]):
        require([p["iterations"] for p in result["checkpoints"]]==[1,2],"Layout tile checkpoint order differs")
        got,expected=scalars(result),scalars(original["results"][i%5])
        require(len(got)==len(expected)==14,"Layout tile scalar count differs")
        error=max(abs(a-b) for a,b in zip(got,expected))
        require(error<1e-7,"Layout tile differs from audited Rust scalars")
        require(got==scalars(tiled["results"][i%5]),"Repeated layout tile scalar bits differ")
        tile_max=max(tile_max,error)
    outputs.append(tile_output)
    family=json.loads(family_path.read_bytes())
    count=len(family["overlap_candidates"])
    indices=[i*(count-1)//511 for i in range(512)]
    require(len(set(indices))==512,"Benchmark candidate sample repeats an index")
    selected=[family["overlap_candidates"][i] for i in indices]
    for candidate in selected:full_graph({"overlap_edges_outer_zero_based":candidate})
    initialization=qa_dir/"long_current_dual_input.txt"
    _,_,x,y,_=parse(initialization)
    bindings[key(initialization)]=digest(initialization)
    benchmark_input=args.out/"benchmark512_input.txt"
    with benchmark_input.open("x",encoding="ascii",newline="\n") as stream:
        stream.write("C99CP1 512 1\n500\n")
        stream.write(" ".join(format(v,".17g") for v in x)+"\n")
        stream.write(" ".join(format(v,".17g") for v in y)+"\n")
        for candidate in selected:stream.write(" ".join(str(v) for edge in candidate for v in edge)+"\n")
    require(parse(benchmark_input)==(512,[500],x,y,selected),"Benchmark readback differs")
    outputs.append(benchmark_input)
    runs=[]
    reference_results=None
    max_pair_difference=0.0
    all_bits_identical=True
    # Reverse the middle pair to reduce a consistent ordering advantage.
    for run_index,version in enumerate(("old","layout_v2","layout_v2","old","old","layout_v2")):
        binary=binary_old if version=="old" else binary_new
        output=args.out/f"benchmark_{run_index}_{version}.json"
        wall=time.perf_counter()
        result=subprocess.run([str(binary),str(benchmark_input),str(output)],check=True,capture_output=True,text=True)
        wall=time.perf_counter()-wall
        payload=json.loads(output.read_bytes())
        require(payload["candidate_count"]==512 and payload["checkpoints"]==[500] and payload["kernel_launches"]==2 and
                len(payload["results"])==512 and [r["candidate_index"] for r in payload["results"]]==list(range(512)),"Benchmark dimensions/order differ")
        values=[scalars(record) for record in payload["results"]]
        require(all(len(v)==8 for v in values),"Benchmark scalar count differs")
        if reference_results is None:reference_results=values
        difference=max(abs(a-b) for actual,expected in zip(values,reference_results) for a,b in zip(actual,expected))
        require(difference<1e-9,"Old/layout benchmark scalar parity failed")
        max_pair_difference=max(max_pair_difference,difference)
        all_bits_identical &= values==reference_results
        runs.append(dict(run_index=run_index,version=version,kernel_seconds=payload["kernel_seconds"],
                         cuda_transfer_and_kernel_seconds=payload["elapsed_seconds"],process_wall_seconds=wall,
                         scalar_error_against_first_original_run=difference,stdout=result.stdout.strip()))
        outputs.append(output)
        print(json.dumps(runs[-1]),flush=True)
    medians={version:{field:statistics.median(r[field] for r in runs if r["version"]==version)
                     for field in ("kernel_seconds","cuda_transfer_and_kernel_seconds","process_wall_seconds")}
             for version in ("old","layout_v2")}
    ratios={field:medians["old"][field]/medians["layout_v2"][field] for field in medians["old"]}
    require(all(digest(ROOT/name)==expected for name,expected in bindings.items()),"Bound input/source changed")
    report=dict(status="CP_CUDA_LAYOUT_V2_NUMERICAL_PARITY_AND_PAIRED_BENCHMARK_PASS",inputs_sha256=bindings,
                outputs_sha256={key(path):digest(path) for path in outputs},
                unchanged_recurrence_and_synchronization_source_span=True,unchanged_graph_validation_and_rhs_source_span=True,
                geometry_change="Constant table contents moved to readonlyglobal loads; only72bytes of uniform pointers remainconstant. Quota gathers use slot-major indexing. Values,iterationarithmetic,blocksize256,sharedlayout,stepsizes andoutputschema unchanged.",
                independent_saved_cpu_controls=dict(path=key(qa_path),sha256=digest(qa_path),vector_entries=qa["numeric_vector_entries_compared"],max_vector_error=qa["max_vector_absolute_error"],max_scalar_error=qa["max_scalar_absolute_error"]),
                tile_boundary=dict(candidate_count=257,checkpoints=[1,2],scalar_comparisons=3598,max_error_vs_saved_rust=tile_max,repeated_controls_bitwise_equal=True,kernel_launches=2),
                benchmark=dict(candidate_count=512,iterations=500,selection="512 evenly spaced unique native indices across the independently audited74,638-candidate originalbest family",native_indices=indices,
                               paired_runs=runs,median_seconds=medians,old_over_new_speed_ratios=ratios,scalar_comparisons_per_run=4096,
                               maximum_old_new_scalar_error=max_pair_difference,all_outputs_bitwise_scalar_identical=all_bits_identical,
                               new_gpu_runs=6,clock_or_power_lock_applied=False),
                recommendation="Layoutderivative is supported for integration after independentQA; timing improvement is limitedto this measured512candidatebatch." if ratios["kernel_seconds"]>1.1 else "No material kernel speedup established onthisbatch; retainoriginalforproduction.",
                no_frozen_source_or_binary_changed=True,total_new_gpu_invocations_here=7,elapsed_seconds=time.perf_counter()-started,
                scope="Numericalparity andboundedpairedperformancecontrol only. No fullfamilyoptimization, LPsolverrun, exclusion, orgraphcompletion; broadperformance maydiffer.")
    save(args.out/"report.json",report)
    print(json.dumps(dict(status=report["status"],speed_ratios=ratios,scalar_error=max_pair_difference,elapsed_seconds=report["elapsed_seconds"])))


if __name__=="__main__":main()
