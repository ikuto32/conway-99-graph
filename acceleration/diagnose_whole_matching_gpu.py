"""Score a whole same-sign matching batch at a frozen feasible X vector.

All scores are numerical ranking heuristics, never exclusions or reoptimized
phase-I objectives. An independent full99 evaluator checks the baseline, top
twenty, each coordinate best, and a fixed random sample, including all residuals.
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

from audit_certificate import full_graph, require
from audit_phase1 import evaluate, graph_rows


ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def path_key(path):
    return path.resolve().relative_to(ROOT).as_posix()


def write_json(path, value):
    with path.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(value, separators=(",", ":"))+"\n")


def signature(edges):
    pairs = [tuple(edge) for edge in edges]
    require(len(pairs) == 168 and len(set(pairs)) == 168 and
            all(len(edge) == 2 and all(type(v) is int for v in edge) and 0 <= edge[0] < edge[1] < 84 for edge in pairs),
            "Invalid canonical overlap candidate")
    return tuple(sorted(pairs))


def topology(initial, candidate, move, labels):
    removed, added = set(initial)-set(candidate), set(candidate)-set(initial)
    require(removed and len(removed) == len(added) == move["changed_edges"] and
            sorted(removed) == list(map(tuple, move["removed"])) and sorted(added) == list(map(tuple, move["added"])),
            "Native matching diff mismatch")
    group, kind = move["root_group"], move["matching_class"]
    require(type(group) is int and 0 <= group < 7 and kind in ("same_0", "same_1"), "Wrong move coordinate")
    sign = int(kind[-1])
    for u,v in removed|added:
        require(set(labels[u]) & set(labels[v]) == {group} and labels[u][group] == labels[v][group] == sign,
                "Move changes an edge outside its same-sign matching")
    red, blue = {}, {}
    for edges, adjacency in ((removed, red), (added, blue)):
        for u,v in edges:
            require(u not in adjacency and v not in adjacency, "Changed matching endpoints repeated")
            adjacency[u], adjacency[v] = v,u
    require(set(red) == set(blue), "Changed matching endpoint sets differ")
    remaining, cycles = set(red), []
    while remaining:
        start, cycle = min(remaining), []
        u = start
        while True:
            require(u in remaining, "Alternating component failed to close")
            cycle.append(u)
            remaining.remove(u)
            v = red[u]
            require(v in remaining, "Repeated alternating vertex")
            cycle.append(v)
            remaining.remove(v)
            u = blue[v]
            if u == start:
                break
        cycles.append(cycle)
    require(cycles == move["alternating_cycles"], "Native alternating cycle decomposition differs")
    sizes = sorted(len(cycle)//2 for cycle in cycles)
    require(all(k >= 2 for k in sizes) and sum(sizes) <= 6, "Unexpected whole-matching symmetric difference")
    if len(sizes) > 1:
        category = "multiple_alternating_cycles"
    elif sizes[0] in (3,4):
        category = "single_atomic_3_or_4"
    elif sizes[0] == 2:
        category = "single_two_edge_swap"
    else:
        category = "single_atomic_5_or_6"
    return dict(root_group=group, matching_class=kind, changed_edges=len(removed), cycle_sizes=sizes,
                category=category, outside_atomic3_4=not (len(sizes) == 1 and sizes[0] in (3,4)),
                newly_beyond_single_2_3_4=len(sizes)>1 or sizes[0]>=5)


def write_gpu_input(path, x, candidates):
    with path.open("x", encoding="ascii", newline="\n") as stream:
        stream.write(f"C99GLOBAL1 {len(candidates)}\n")
        stream.write(" ".join(format(value,".17g") for value in x)+"\n")
        for candidate in candidates:
            stream.write(" ".join(str(v) for edge in candidate for v in edge)+"\n")


def summarize(indices, scores):
    values = sorted(scores[i+1]["total_violation"] for i in indices)
    require(values, "Empty diagnostic group")
    def percentile(p):
        position = (len(values)-1)*p
        lo, hi = math.floor(position), math.ceil(position)
        return values[lo]+(values[hi]-values[lo])*(position-lo)
    best = min(indices, key=lambda i:(scores[i+1]["total_violation"], i))
    return dict(count=len(values), minimum=values[0], p10=percentile(.1), median=percentile(.5),
                p90=percentile(.9), maximum=values[-1], best_proposal_index=best)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--initial", type=Path, required=True)
    parser.add_argument("--phase1", type=Path, required=True)
    parser.add_argument("--proposals", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--sample", type=int, default=32)
    parser.add_argument("--seed", type=int, default=20260927)
    args = parser.parse_args()
    require(not args.out.exists() and args.sample >= 0, "Use a new output directory and nonnegative sample")
    args.out.mkdir(parents=True)
    started = time.perf_counter()
    executable = ROOT/"acceleration/build/overlap_phase_gpu.exe"
    sources = [args.initial,args.phase1,args.proposals,Path(__file__),executable,
               ROOT/"acceleration/overlap_phase_gpu.cu", ROOT/"acceleration/audit_phase1.py",
               ROOT/"acceleration/audit_certificate.py",ROOT/"acceleration/overlap_matching_neighbors.rs",
               ROOT/"acceleration/build/overlap_matching_neighbors.exe"]
    bindings = {path_key(path):digest(path) for path in sources}
    candidate = json.loads(args.initial.read_bytes())
    initial = signature(candidate["overlap_edges_outer_zero_based"])
    graph, _ = full_graph(candidate)
    labels = [{(s-1)//2:(s-1)%2 for s in graph[u+15] if 1 <= s <= 14} for u in range(84)]
    phase = json.loads(args.phase1.read_bytes())
    x = phase["numeric_edge_values"]
    require(len(x) == 1680 and all(type(v) in (int,float) and math.isfinite(v) and 0 <= v <= 1 for v in x), "Invalid strict-box X")
    edge_order, _, _ = graph_rows(candidate)
    require(phase["edge_variables"] == list(map(list,edge_order)), "X column order differs from independent full99 geometry")
    phase_candidate = Path(phase["candidate_path"])
    require(digest(phase_candidate) == phase["candidate_sha256"] and signature(json.loads(phase_candidate.read_bytes())["overlap_edges_outer_zero_based"]) == initial,
            "Phase-I vector bound to a different labeled graph")
    bindings[path_key(phase_candidate)] = digest(phase_candidate)
    proposed = json.loads(args.proposals.read_bytes())
    require(proposed["status"] == "COMPLETE_WHOLE_SAME_SIGN_MATCHING_SUBFAMILY_ENUMERATION", "Unexpected native batch status")
    options = [signature(edges) for edges in proposed["overlap_candidates"]]
    require(len(options) == len(proposed["moves"]) and 0 < len(options) < 100000 and len(set(options)) == len(options) and initial not in options,
            "Invalid native candidate count, duplicates, or included base")
    geometries = [topology(initial, edges, move, labels) for edges,move in zip(options,proposed["moves"])]
    coordinates = defaultdict(list)
    categories = defaultdict(list)
    changed_counts = defaultdict(list)
    cycle_types = defaultdict(list)
    for i, geometry in enumerate(geometries):
        coordinates[f"{geometry['root_group']}/{geometry['matching_class']}"].append(i)
        categories[geometry["category"]].append(i)
        changed_counts[str(geometry["changed_edges"])].append(i)
        cycle_types["+".join(map(str,geometry["cycle_sizes"]))].append(i)
    require(len(coordinates) == 14, "Diagnostic batch does not cover all fourteen same-sign coordinates")
    manifest = dict(status="WHOLE_MATCHING_FIXED_X_DIAGNOSTIC_INPUTS", inputs_sha256=bindings,
                    candidate_count=len(options), seed=args.seed, random_sample_requested=args.sample,
                    proposal_index_to_gpu_candidate_index="i -> i+1; index0 is the unchanged baseline",
                    x_frozen_from=path_key(args.phase1), native_family_completeness_independently_audited_here=False,
                    scope="Numerical upper bounds on reoptimized phase-I defect used only for ranking. No exclusion or completion claims.")
    write_json(args.out/"manifest.json", manifest)
    all_input, all_output = args.out/"all_input.txt", args.out/"all_gpu_scores.json"
    write_gpu_input(all_input,x,[initial]+options)
    gpu_run = subprocess.run([str(executable),str(all_input),str(all_output)],check=True,capture_output=True,text=True)
    gpu = json.loads(all_output.read_bytes())
    require(gpu["status"] == "NUMERICAL_FIXED_X_PHASE1_HEURISTIC" and gpu["candidate_count"] == len(options)+1,
            "Wrong GPU output status/count")
    scores = gpu["results"]
    require(len(scores) == len(options)+1 and [r["candidate_index"] for r in scores] == list(range(len(scores))), "Wrong GPU output order")
    require(all(all(math.isfinite(r[key]) and r[key]>=0 for key in ("total_violation","quota_violation","pair_violation")) for r in scores), "Invalid GPU score")
    ordered = sorted(range(len(options)),key=lambda i:(scores[i+1]["total_violation"],i))
    rank = {i:j+1 for j,i in enumerate(ordered)}
    coordinate_best = {key:min(indices,key=lambda i:(scores[i+1]["total_violation"],i)) for key,indices in coordinates.items()}

    def selected_record(i):
        return dict(proposal_index=i, global_rank=rank[i],gpu_candidate_index=i+1,
                    canonical_overlap_edges_sha256=sha256(json.dumps(options[i],separators=(",", ":")).encode()).hexdigest(),
                    **geometries[i], **{key:scores[i+1][key] for key in ("total_violation","quota_violation","pair_violation")})

    top20 = [selected_record(i) for i in ordered[:20]]
    statistics = dict(by_coordinate={key:summarize(indices,scores) for key,indices in sorted(coordinates.items())},
                      by_move_category={key:summarize(indices,scores) for key,indices in sorted(categories.items())},
                      by_changed_edge_count={key:summarize(indices,scores) for key,indices in sorted(changed_counts.items())},
                      by_cycle_sizes={key:summarize(indices,scores) for key,indices in sorted(cycle_types.items())},
                      top_k_categories={str(k):dict(Counter(geometries[i]["category"] for i in ordered[:k])) for k in (20,100,1000)},
                      strict_fixed_x_improvements_over_baseline=sum(r["total_violation"] < scores[0]["total_violation"]-1e-8 for r in scores[1:]))
    for grouping in ("by_coordinate","by_move_category","by_changed_edge_count","by_cycle_sizes"):
        for group in statistics[grouping].values():
            group["best_global_rank"] = rank[group["best_proposal_index"]]
    statistics["atomic_comparison_scope"] = "Same-sign coordinates only. Single connected3/4cycles are the intersection with the previously tested atomic3/4 move type; seven cross coordinates are absent from this whole-matching batch."
    shortlist = dict(status="NUMERICAL_RANKING_READY_INDEPENDENT_SAMPLE_CHECK_PENDING",baseline=scores[0],top20=top20,
                     coordinate_best={key:selected_record(i) for key,i in sorted(coordinate_best.items())},statistics=statistics)
    write_json(args.out/"ranking.json",shortlist)
    print(json.dumps(dict(progress="RANKING_READY", candidate_count=len(options),baseline=scores[0]["total_violation"],
                          top=top20[0],cuda_kernel_seconds=gpu["kernel_seconds"])),flush=True)
    random_sample = random.Random(args.seed).sample(range(len(options)),min(args.sample,len(options)))
    checked = sorted(set(ordered[:20])|set(coordinate_best.values())|set(random_sample))
    sample_input,sample_output = args.out/"checked_input.txt",args.out/"checked_gpu_residuals.json"
    write_gpu_input(sample_input,x,[initial]+[options[i] for i in checked])
    subprocess.run([str(executable),str(sample_input),str(sample_output),"--residuals"],check=True,capture_output=True,text=True)
    sample_gpu = json.loads(sample_output.read_bytes())
    require(sample_gpu["status"] == gpu["status"] and sample_gpu["candidate_count"] == len(checked)+1 and
            len(sample_gpu["results"]) == len(checked)+1,"Wrong checked subset")
    baseline_reference = None
    records = []
    max_residual, max_score = 0.0,0.0
    reference_started = time.perf_counter()
    for subset_index, proposal_index in enumerate([None]+checked):
        edges = initial if proposal_index is None else options[proposal_index]
        expected = evaluate({"overlap_edges_outer_zero_based":edges},x)
        actual = sample_gpu["results"][subset_index]
        original = scores[0 if proposal_index is None else proposal_index+1]
        require(actual["candidate_index"] == subset_index, "Checked subset order mismatch")
        errors = []
        for field,length in (("quota_residuals",840),("pair_residuals",3486)):
            require(len(actual[field]) == length, "Wrong residual dimensions")
            errors.append(max(abs(a-b) for a,b in zip(actual[field],expected[field])))
        residual_error = max(errors)
        component_error = max(abs(actual[field]-expected[field]) for field in ("total_violation","quota_violation","pair_violation"))
        require(all(actual[field] == original[field] for field in ("total_violation","quota_violation","pair_violation","quota_max_abs","pair_max_positive")),
                "Subset and full-batch GPU results differ")
        require(residual_error < 1e-10 and component_error < 1e-8,"Independent full99 residual comparison failed")
        require(abs(actual["quota_max_abs"]-max(map(abs,expected["quota_residuals"]))) < 1e-10 and
                abs(actual["pair_max_positive"]-max(0,max(expected["pair_residuals"]))) < 1e-10,"GPU maxima differ")
        max_residual,max_score = max(max_residual,residual_error),max(max_score,component_error)
        records.append(dict(proposal_index=proposal_index,gpu_subset_index=subset_index,max_residual_error=residual_error,max_component_error=component_error))
        if proposal_index is None:
            baseline_reference = {key:expected[key] for key in ("total_violation","quota_violation","pair_violation")}
            require(abs(expected["total_violation"]-phase["numeric_objective"])<1e-7,"Baseline phase-I merit differs")
    produced = [args.out/name for name in ("manifest.json","all_input.txt","all_gpu_scores.json","ranking.json","checked_input.txt","checked_gpu_residuals.json")]
    require(all(digest(ROOT/path)==expected for path,expected in bindings.items()),"Source/input changed during diagnostic")
    report = dict(status="WHOLE_MATCHING_FIXED_X_GPU_DIAGNOSTIC_AND_INDEPENDENT_SAMPLE_AUDIT_PASS",
                  inputs_sha256=bindings,outputs_sha256={path_key(path):digest(path) for path in produced},
                  all_noninitial_candidates_scored=len(options),all_candidate_diff_geometry_checked=True,
                  baseline=scores[0],baseline_independent_reference=baseline_reference,
                  candidate_full99_numeric_reference_count=len(checked)+1,
                  selection_rule="Unchanged baseline + top20 + each of14coordinate best + fixed-seed uniform sample, deduplicated",
                  top20_indices=ordered[:20],coordinate_best_indices=coordinate_best,random_sample_indices=random_sample,
                  checked_proposal_indices=checked,reference_records=records,
                  all840_quota_and3486_pair_residuals_compared_for_each_checked_candidate=True,
                  own_label_zero_term_quotas_independently_verified_per_checked_candidate=336,
                  independent_full99_label_and_pair_coordinates_per_checked_candidate=4662,
                  max_residual_absolute_difference=max_residual,max_objective_component_absolute_difference=max_score,
                  top20=top20,coordinate_best={key:selected_record(i) for key,i in sorted(coordinate_best.items())},statistics=statistics,
                  cuda_kernel_seconds=gpu["kernel_seconds"],cuda_transfer_and_kernel_seconds=gpu["elapsed_seconds"],
                  cuda_process_stdout=gpu_run.stdout.strip(),python_reference_seconds=time.perf_counter()-reference_started,
                  elapsed_seconds=time.perf_counter()-started,all_candidate_full99_caps_checked_by_existing_native_scorer=True,
                  native_family_completeness_independently_audited_here=False,
                  scope="Fixed-X double-precision ranking only. F_K(X) upper-bounds the reoptimized phase-I minimum and cannot exclude a candidate. The full candidate family is scored, while independent full99 residual validation covers only the explicitly listed subset. No LP optimality, full-family independent legality/exhaustion, or Conway completion claim.")
    write_json(args.out/"summary.json",report)
    print(json.dumps({key:report[key] for key in ("status","all_noninitial_candidates_scored","candidate_full99_numeric_reference_count",
                    "max_residual_absolute_difference","max_objective_component_absolute_difference","elapsed_seconds")}))


if __name__ == "__main__":
    main()
