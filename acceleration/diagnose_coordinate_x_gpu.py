"""Rescore legal whole-matching candidates at saved coordinate-LP X vectors.

The fractional Y is ignored. Each projected X is evaluated with each actual
discrete K in its coordinate using the existing true fixed-K CUDA scorer.
Taking the smaller of two feasible-X defects remains only an upper bound on
the reoptimized defect. No solver is imported or rerun.
"""
import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
import math
from pathlib import Path
import random
import subprocess
import time

from audit_certificate import require
from audit_phase1 import evaluate, graph_rows
from diagnose_whole_matching_gpu_v2 import ROOT, digest, path_key, write_json, write_gpu_input


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--previous", type=Path, required=True)
    parser.add_argument("--sweep", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--sample", type=int, default=32)
    parser.add_argument("--seed", type=int, default=20260928)
    args = parser.parse_args()
    require(not args.out.exists() and args.sample >= 0,"Use a new diagnostic directory")
    args.out.mkdir(parents=True)
    started = time.perf_counter()
    prior = json.loads(args.previous.read_bytes())
    require(prior["status"] == "WHOLE_MATCHING_FIXED_X_GPU_DIAGNOSTIC_AND_INDEPENDENT_SAMPLE_AUDIT_PASS", "Prior diagnostic not PASS")
    bindings = {path_key(args.previous):digest(args.previous),path_key(args.sweep):digest(args.sweep),
                path_key(Path(__file__)):digest(Path(__file__))}
    for field in ("inputs_sha256","outputs_sha256"):
        for name, expected in prior[field].items():
            require(digest(ROOT/name) == expected,"Changed prior diagnostic binding: "+name)
            bindings[name] = expected
    manifest = json.loads((args.previous.parent/"manifest.json").read_bytes())
    proposal_path = next(ROOT/name for name in prior["inputs_sha256"] if name.endswith("whole_matching_qa/all.json"))
    initial_path = next(ROOT/name for name in prior["inputs_sha256"] if name.endswith("two_trade_pilot/best_candidate.json"))
    proposed = json.loads(proposal_path.read_bytes())
    initial = json.loads(initial_path.read_bytes())
    options, moves = proposed["overlap_candidates"],proposed["moves"]
    current = json.loads((args.previous.parent/"all_gpu_scores.json").read_bytes())["results"]
    require(len(options)+1 == len(current) and len(options) == prior["all_noninitial_candidates_scored"],"Prior proposal count changed")
    xedges, _, _ = graph_rows(initial)
    coordinates = defaultdict(list)
    geometry = []
    for i,move in enumerate(moves):
        coordinate = f"{move['root_group']}/{move['matching_class']}"
        coordinates[coordinate].append(i)
        sizes = sorted(len(cycle)//2 for cycle in move["alternating_cycles"])
        geometry.append(dict(coordinate=coordinate,changed_edges=move["changed_edges"],cycle_sizes=sizes,
                             cycle_partition="+".join(map(str,sizes)),extended=len(sizes)>1 or sizes[0]>=5))
    require(len(coordinates) == 14,"Expected fourteen same-sign coordinates")
    sweep = json.loads(args.sweep.read_bytes())
    rows = {f"{r['root_group']}/{r['matching_class']}":r for r in sweep["records"] if r["matching_class"] in ("same_0","same_1")}
    require(set(rows) == set(coordinates),"Coordinate sweep does not cover proposal coordinates")
    executable = ROOT/"acceleration/build/overlap_phase_gpu.exe"
    alternative, vectors, gpu_indices, coordinate_runs = [None]*len(options),{}, {},[]
    produced = []
    total_kernel, total_gpu = 0.0,0.0
    for coordinate, indices in sorted(coordinates.items()):
        record = rows[coordinate]
        result_path,matrix_path = Path(record["result_path"]),Path(record["matrix_path"])
        require(digest(result_path)==record["result_sha256"] and digest(matrix_path)==record["matrix_sha256"],"Sweep artifact SHA mismatch")
        result,matrix = json.loads(result_path.read_bytes()),json.loads(matrix_path.read_bytes())
        require(result["matrix_sha256"] == digest(matrix_path) and result["root_group"]==record["root_group"] and
                result["matching_class"]==record["matching_class"],"Coordinate result binding mismatch")
        require(matrix["edge_variables"] == list(map(list,xedges)) and matrix["col_lower"][:1680]==[0]*1680 and matrix["col_upper"][:1680]==[1]*1680,
                "Coordinate X order/boxes differ from full99 geometry")
        base_bound = any(Path(name).resolve()==initial_path.resolve() and expected==digest(initial_path) for name,expected in matrix["inputs_sha256"].items())
        require(base_bound,"Coordinate LP uses another base K")
        for name,expected in matrix["inputs_sha256"].items():
            require(digest(Path(name))==expected,"Changed coordinate matrix source/input")
            bindings[path_key(Path(name))]=expected
        raw_x = result["primal_values"][:1680]
        require(len(raw_x)==1680 and all(type(v) in (float,int) and math.isfinite(v) for v in raw_x),"Invalid coordinate primal X")
        x = [max(0.0,min(1.0,v)) for v in raw_x]
        adjustments = [abs(v-w) for v,w in zip(raw_x,x)]
        require(max(adjustments)<1e-7,"Coordinate LP X far outside box")
        vectors[coordinate]=x
        bindings[path_key(result_path)],bindings[path_key(matrix_path)] = digest(result_path),digest(matrix_path)
        name=coordinate.replace("/","_")
        input_path,output_path=args.out/f"{name}_input.txt",args.out/f"{name}_gpu.json"
        write_gpu_input(input_path,x,[initial["overlap_edges_outer_zero_based"]]+[options[i] for i in indices])
        completed=subprocess.run([str(executable),str(input_path),str(output_path)],check=True,capture_output=True,text=True)
        gpu=json.loads(output_path.read_bytes())
        require(gpu["status"]=="NUMERICAL_FIXED_X_PHASE1_HEURISTIC" and gpu["candidate_count"]==len(indices)+1 and
                len(gpu["results"])==len(indices)+1,"Coordinate GPU result count/status mismatch")
        require([r["candidate_index"] for r in gpu["results"]]==list(range(len(indices)+1)),"Coordinate GPU index mismatch")
        require(all(all(math.isfinite(r[key]) and r[key]>=0 for key in ("total_violation","quota_violation","pair_violation")) for r in gpu["results"]),"Invalid coordinate GPU merit")
        for local,i in enumerate(indices,1):
            alternative[i]=gpu["results"][local]
            gpu_indices[i]=local
        total_kernel+=gpu["kernel_seconds"]
        total_gpu+=gpu["elapsed_seconds"]
        coordinate_runs.append(dict(coordinate=coordinate,candidate_count=len(indices),result_path=path_key(result_path),result_sha256=digest(result_path),
                                    matrix_path=path_key(matrix_path),matrix_sha256=digest(matrix_path),x_projected_to_box=True,
                                    raw_x_min=min(raw_x),raw_x_max=max(raw_x),clipped_entries=sum(d>0 for d in adjustments),
                                    maximum_box_adjustment=max(adjustments),sum_box_adjustment=sum(adjustments),
                                    coordinate_relaxation_objective_diagnostic_only=result["numeric_objective"],baseline_actual_fixed_k=gpu["results"][0],
                                    minimum_actual_fixed_k=min(r["total_violation"] for r in gpu["results"][1:]),
                                    kernel_seconds=gpu["kernel_seconds"],cuda_process_stdout=completed.stdout.strip()))
        produced.extend([input_path,output_path])
        print(json.dumps(dict(progress="COORDINATE_SCORED",coordinate=coordinate,candidates=len(indices),
                              minimum_actual_fixed_k=coordinate_runs[-1]["minimum_actual_fixed_k"])),flush=True)
    require(all(row is not None for row in alternative),"Unscored proposal")
    totals=[min(current[i+1]["total_violation"],alternative[i]["total_violation"]) for i in range(len(options))]
    ordered=sorted(range(len(options)),key=lambda i:(totals[i],i))
    old_ordered=sorted(range(len(options)),key=lambda i:(current[i+1]["total_violation"],i))
    old_rank={i:j+1 for j,i in enumerate(old_ordered)}
    rank={i:j+1 for j,i in enumerate(ordered)}
    def record(i):
        return dict(proposal_index=i,combined_rank=rank[i],current_x_rank=old_rank[i],**geometry[i],
                    current_x_score=current[i+1]["total_violation"],coordinate_x_score=alternative[i]["total_violation"],
                    minimum_score=totals[i],winner="coordinate_x" if alternative[i]["total_violation"]<current[i+1]["total_violation"] else "current_x")
    shape_indices=defaultdict(list)
    for i,g in enumerate(geometry):
        shape_indices[g["cycle_partition"]].append(i)
    shape_best={shape:min(indices,key=lambda i:(totals[i],i)) for shape,indices in shape_indices.items()}
    coordinate_best={coordinate:min(indices,key=lambda i:(totals[i],i)) for coordinate,indices in coordinates.items()}
    random_indices=random.Random(args.seed).sample(range(len(options)),min(args.sample,len(options)))
    checked=sorted(set(ordered[:20])|set(shape_best.values())|set(coordinate_best.values())|set(random_indices))
    summary_metrics=dict(candidate_count=len(options),coordinate_x_strictly_better_count=sum(alternative[i]["total_violation"]<current[i+1]["total_violation"]-1e-8 for i in range(len(options))),
                         top20=[record(i) for i in ordered[:20]],best_per_cycle_partition={shape:record(i) for shape,i in sorted(shape_best.items())},
                         best_per_coordinate={coordinate:record(i) for coordinate,i in sorted(coordinate_best.items())},
                         top_k_shapes={str(k):dict(Counter(geometry[i]["cycle_partition"] for i in ordered[:k])) for k in (20,100,1000)},
                         current_x_global_min=current[old_ordered[0]+1]["total_violation"],combined_global_min=totals[ordered[0]],
                         seed=args.seed,random_sample_indices=random_indices,checked_proposal_indices=checked)
    combined_path=args.out/"combined_scores.json"
    write_json(combined_path,dict(status="TWO_FEASIBLE_X_NUMERICAL_UPPER_BOUND_RANKING",proposal_order="Same indices as bound native batch",
                                 current_x_total=[r["total_violation"] for r in current[1:]],coordinate_x_total=[r["total_violation"] for r in alternative],minimum_total=totals))
    produced.append(combined_path)
    write_json(args.out/"ranking.json",dict(status="ALTERNATIVE_X_RANKING_READY_INDEPENDENT_SAMPLE_CHECK_PENDING",**summary_metrics))
    produced.append(args.out/"ranking.json")
    print(json.dumps(dict(progress="COMBINED_RANKING_READY",global_best=record(ordered[0]),coordinate_x_better=summary_metrics["coordinate_x_strictly_better_count"])),flush=True)
    # For each selected K, validate the actual coordinate-X result even if the
    # current-X point won the minimum. Its current-X parity is separately checked.
    comparison_started=time.perf_counter()
    controls=[]
    max_residual,max_component=0.0,0.0
    for coordinate,indices in sorted(coordinates.items()):
        selected=[i for i in checked if geometry[i]["coordinate"]==coordinate]
        name=coordinate.replace("/","_")
        input_path,output_path=args.out/f"{name}_checked_input.txt",args.out/f"{name}_checked_gpu.json"
        write_gpu_input(input_path,vectors[coordinate],[initial["overlap_edges_outer_zero_based"]]+[options[i] for i in selected])
        subprocess.run([str(executable),str(input_path),str(output_path),"--residuals"],check=True,capture_output=True,text=True)
        gpu=json.loads(output_path.read_bytes())
        require(gpu["candidate_count"]==len(selected)+1 and len(gpu["results"])==len(selected)+1,"Wrong coordinate residual control count")
        baseline=next(run["baseline_actual_fixed_k"] for run in coordinate_runs if run["coordinate"]==coordinate)
        for local,i in enumerate([None]+selected):
            edges=initial["overlap_edges_outer_zero_based"] if i is None else options[i]
            expected=evaluate({"overlap_edges_outer_zero_based":edges},vectors[coordinate])
            actual=gpu["results"][local]
            require(actual["candidate_index"]==local,"Coordinate residual control order mismatch")
            original=baseline if i is None else alternative[i]
            require(all(actual[k]==original[k] for k in ("total_violation","quota_violation","pair_violation","quota_max_abs","pair_max_positive")),"Subset/fullbatch coordinate score mismatch")
            residual_error=max(max(abs(a-b) for a,b in zip(actual[field],expected[field])) for field in ("quota_residuals","pair_residuals"))
            require(len(actual["quota_residuals"])==840 and len(actual["pair_residuals"])==3486,"Wrong residual lengths")
            component_error=max(abs(actual[field]-expected[field]) for field in ("total_violation","quota_violation","pair_violation"))
            require(residual_error<1e-10 and component_error<1e-8,"Independent coordinate-X fixed-K evaluation mismatch")
            max_residual,max_component=max(max_residual,residual_error),max(max_component,component_error)
            control=dict(coordinate=coordinate,proposal_index=i,max_row_error=residual_error,max_component_error=component_error)
            if i is not None:
                original_phase=json.loads((ROOT/manifest["x_frozen_from"]).read_bytes())
                old_expected=evaluate({"overlap_edges_outer_zero_based":edges},original_phase["numeric_edge_values"])
                old_error=max(abs(current[i+1][key]-old_expected[key]) for key in ("total_violation","quota_violation","pair_violation"))
                require(old_error<1e-8,"Independent original-X objective mismatch on alternative shortlist")
                control["current_x_max_component_error"]=old_error
            controls.append(control)
        produced.extend([input_path,output_path])
    require(all(digest(ROOT/name)==expected for name,expected in bindings.items()),"Input or source changed during rescore")
    report=dict(status="COORDINATE_X_GPU_RESCORE_AND_INDEPENDENT_SAMPLE_AUDIT_PASS",inputs_sha256=bindings,
                outputs_sha256={path_key(path):digest(path) for path in produced},coordinate_runs=coordinate_runs,
                **summary_metrics,reference_controls=controls,independent_full99_evaluations=len(controls)+len(checked),
                coordinate_x_all4326_residual_controls=len(controls),original_x_additional_objective_controls=len(checked),
                own_label_zero_term_quotas_checked_per_reference=336,max_residual_absolute_difference=max_residual,
                max_objective_component_absolute_difference=max_component,cuda_kernel_seconds=total_kernel,cuda_transfer_and_kernel_seconds=total_gpu,
                reference_and_subset_cuda_seconds=time.perf_counter()-comparison_started,elapsed_seconds=time.perf_counter()-started,
                solver_reruns=0,fractional_y_used_as_candidate=False,
                scope="Each actual discrete K is scored at its coordinate's saved projected feasible X. Minimum of current-X and coordinate-X defects is still only a numerical upper bound on the reoptimized phase-I optimum, never an exclusion. Neither fractional-Y objective nor numerical optimality is used as proof. Independent validation is restricted to the reported subset.")
    write_json(args.out/"summary.json",report)
    print(json.dumps({key:report[key] for key in ("status","candidate_count","coordinate_x_strictly_better_count","combined_global_min","independent_full99_evaluations","max_residual_absolute_difference","max_objective_component_absolute_difference","elapsed_seconds")}))


if __name__=="__main__":
    main()
