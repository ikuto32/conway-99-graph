"""Bounded reoptimization of64 new expanded matching moves ranked by two fixed Xs."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from math import isfinite
from pathlib import Path
import time

from phase1_probe_ipm import solve_edges_with_basis

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "acceleration/results"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def key(path):
    return path.resolve().relative_to(ROOT).as_posix()


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def signature(edges):
    return tuple(sorted(tuple(edge) for edge in edges))


def edge_hash(edges):
    return sha256(json.dumps(signature(edges), separators=(",", ":")).encode("ascii")).hexdigest()


def write_new(path, data):
    with path.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(data, separators=(",", ":"), allow_nan=False) + "\n")


def resolve(path):
    p = Path(path.replace("\\", "/"))
    return p if p.is_absolute() else ROOT / p


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--native", type=Path, default=RESULTS/"20260916_whole_matching_qa/all.json")
    parser.add_argument("--score-summary", type=Path, default=RESULTS/"20260916_whole_matching_coordinate_x_diagnostic/summary.json")
    parser.add_argument("--scores", type=Path, default=RESULTS/"20260916_whole_matching_coordinate_x_diagnostic/combined_scores.json")
    parser.add_argument("--previous", type=Path, default=RESULTS/"20260916_whole_matching_pilot")
    parser.add_argument("--initial", type=Path, default=RESULTS/"20260916_two_trade_pilot/best_candidate.json")
    parser.add_argument("--initial-phase1", type=Path, default=RESULTS/"20260916_two_trade_pilot/best_phase1.json")
    args = parser.parse_args()
    require(not args.out.exists(), "Preserve previous shortlist output")
    started = time.perf_counter()
    inputs = {}

    def bind(path, expected=None):
        actual = digest(path)
        require(expected is None or actual==expected, "Hash mismatch: " + str(path))
        inputs[key(path)] = actual
        return actual

    for path in [args.native,args.score_summary,args.scores,args.initial,args.initial_phase1,
                 args.previous/"summary.json",Path(__file__),ROOT/"acceleration/phase1_probe_ipm.py",
                 ROOT/"acceleration/linear_probe.py",ROOT/"acceleration/audit_certificate.py"]:
        bind(path)
    score_summary = json.loads(args.score_summary.read_bytes())
    require(score_summary["status"]=="COORDINATE_X_GPU_RESCORE_AND_INDEPENDENT_SAMPLE_AUDIT_PASS", "Unverified score summary")
    score_bindings = {key(resolve(path)): value for group in ("inputs_sha256","outputs_sha256")
                      for path,value in score_summary[group].items()}
    require(score_bindings[key(args.native)] == inputs[key(args.native)] and
            score_bindings[key(args.scores)] == inputs[key(args.scores)] and
            score_bindings[key(args.initial)] == inputs[key(args.initial)], "Score/native/base association mismatch")
    for path,expected in score_bindings.items():
        bind(resolve(path),expected)
    data = json.loads(args.native.read_bytes())
    require(data["status"]=="COMPLETE_WHOLE_SAME_SIGN_MATCHING_SUBFAMILY_ENUMERATION", "Incomplete native batch")
    scores = json.loads(args.scores.read_bytes())
    require(scores["status"]=="TWO_FEASIBLE_X_NUMERICAL_UPPER_BOUND_RANKING", "Unexpected score payload")
    minimum = scores["minimum_total"]
    size = len(data["overlap_candidates"])
    require(size==74638 and len(data["moves"])==size and
            all(len(scores[name])==size for name in ("minimum_total","current_x_total","coordinate_x_total")), "Wrong proposal/score size")
    require(all(type(x) in (int,float) and isfinite(x) and x>=0 for name in
                ("minimum_total","current_x_total","coordinate_x_total") for x in scores[name]), "Invalid numerical score")
    require(all(minimum[i]==min(scores["current_x_total"][i],scores["coordinate_x_total"][i]) for i in range(size)),
            "Combined score is not the declared minimum")
    prior = json.loads((args.previous/"summary.json").read_bytes())
    require(prior["status"]=="BOUNDED_WHOLE_MATCHING_COUPLED_SEARCH_FINISHED", "Previous pilot unfinished")
    paths = sorted((args.previous/"probes").glob("*_candidate.json"))
    require(len(paths)==prior["phase1_evaluations"]==129, "Unexpected prior probe inventory")
    excluded, excluded_rows = set(), []
    for path in paths:
        edges = json.loads(path.read_bytes())["overlap_edges_outer_zero_based"]
        excluded.add(signature(edges))
        excluded_rows.append(dict(candidate_path=key(path),candidate_sha256=bind(path),overlap_edges_sha256=edge_hash(edges)))
    initial = json.loads(args.initial.read_bytes())["overlap_edges_outer_zero_based"]
    initial_phase = json.loads(args.initial_phase1.read_bytes())
    require(signature(initial) in excluded, "Previous initial graph missing")
    require(initial_phase["overlap_edges_sha256"]==edge_hash(initial), "Initial phase-I graph association mismatch")
    baseline = initial_phase["numeric_objective"]
    partitions = [tuple(sorted(len(cycle)//2 for cycle in move["alternating_cycles"])) for move in data["moves"]]
    coordinates = [(move["root_group"],move["matching_class"]) for move in data["moves"]]
    triples = [(*coordinates[i],partitions[i]) for i in range(size)]
    expanded = [i for i,move in enumerate(data["moves"]) if move["changed_edges"]>=5 or len(move["alternating_cycles"])>1]
    eligible = [i for i in expanded if signature(data["overlap_candidates"][i]) not in excluded]
    ordered = sorted(eligible,key=lambda i:(minimum[i],i))
    selected, roles = [], {}

    def add(index, role):
        if index not in roles:
            selected.append(index)
            roles[index] = []
        roles[index].append(role)

    for coordinate in sorted(set(coordinates[i] for i in eligible)):
        add(next(i for i in ordered if coordinates[i]==coordinate),"coordinate_minimum")
    require(len(selected)==14, "Missing same-sign coordinate")
    for partition in sorted(set(partitions[i] for i in eligible)):
        add(next(i for i in ordered if partitions[i]==partition),"global_cycle_partition_minimum")
    represented = {triples[i] for i in selected}
    for i in ordered:
        if len(selected)>=32:
            break
        if triples[i] not in represented:
            add(i,"unrepresented_coordinate_cycle_partition_minimum")
            represented.add(triples[i])
    require(len(selected)==32, "Insufficient representative strata")
    for i in ordered:
        if len(selected)>=64:
            break
        if i not in roles:
            add(i,"global_score_fill")
    require(len(selected)==64 and len(set(selected))==64, "Wrong shortlist count")
    selected_signatures = {signature(data["overlap_candidates"][i]) for i in selected}
    require(len(selected_signatures)==64 and not selected_signatures & excluded, "Duplicate or previously evaluated candidate")
    selection = [dict(selection_order=n,proposal_index=i,selection_roles=roles[i],score=minimum[i],
                      current_x_score=scores["current_x_total"][i],coordinate_x_score=scores["coordinate_x_total"][i],
                      root_group=coordinates[i][0],matching_class=coordinates[i][1],cycle_partition=list(partitions[i]),
                      move=data["moves"][i],overlap_edges_sha256=edge_hash(data["overlap_candidates"][i]))
                 for n,i in enumerate(selected)]
    args.out.mkdir(parents=True,exist_ok=False)
    (args.out/"probes").mkdir()
    manifest = dict(status="BOUNDED_MATCHING_HINT_SHORTLIST_MANIFEST",inputs_sha256=inputs,
                    seconds_per_lp=30,shortlist_count=64,diversity_prefix_count=32,basis_policy="COLD_IPM_BASIS_NONE",
                    baseline_numeric_objective=baseline,expanded_candidates=len(expanded),eligible_new_candidates=len(eligible),
                    previous_candidate_artifacts=len(paths),previous_unique_edge_signatures=len(excluded),excluded=excluded_rows,
                    selection=selection,tie_break="(minimum_total, native proposal_index)",
                    selection_policy="Coordinate minima then cycle-partition minima; append unrepresented coordinate/partition minima until32 total; global-score fill to64. Multi-role minima evaluated once.",
                    scope="Numerical fixed-K phase-I reoptimization only. Neither score ranking nor positive/zero LP objective certifies exclusion, feasibility, pair-AC pass or graph completion.")
    write_new(args.out/"manifest.json",manifest)
    results, outputs = [], {key(args.out/"manifest.json"):digest(args.out/"manifest.json")}
    for chosen in selection:
        i = chosen["proposal_index"]
        stem = f"selection_{chosen['selection_order']:02d}_index_{i}"
        candidate_path = args.out/"probes"/(stem+"_candidate.json")
        result_path = args.out/"probes"/(stem+"_phase1.json")
        write_new(candidate_path,dict(overlap_edges_outer_zero_based=data["overlap_candidates"][i],
                                     native_source_path=key(args.native),native_source_sha256=inputs[key(args.native)],
                                     selection=chosen,manifest_path=key(args.out/"manifest.json"),
                                     manifest_sha256=outputs[key(args.out/"manifest.json")]))
        result,_unused_basis = solve_edges_with_basis(data["overlap_candidates"][i],seconds=30,basis=None)
        result.update(candidate_path=key(candidate_path),candidate_sha256=digest(candidate_path))
        require(result["overlap_edges_sha256"]==chosen["overlap_edges_sha256"], "LP graph differs from selection")
        for name,expected in result["source_sha256"].items():
            require(inputs[key(ROOT/"acceleration"/name)]==expected, "LP source changed during run")
        write_new(result_path,result)
        outputs[key(candidate_path)] = digest(candidate_path)
        outputs[key(result_path)] = digest(result_path)
        record = dict(**chosen,candidate_path=key(candidate_path),candidate_sha256=digest(candidate_path),
                      result_path=key(result_path),result_sha256=digest(result_path),numeric_objective=result["numeric_objective"],
                      optimal=result["optimal"],status=result["status"],solver_model_status=result["primal_model_status"],
                      solve_seconds=result["solve_seconds"],elapsed_seconds=result["elapsed_seconds"])
        results.append(record)
        if len(results)%8==0:
            usable=[r["numeric_objective"] for r in results if r["numeric_objective"] is not None]
            print(json.dumps(dict(completed=len(results),total=64,best_numeric_objective=min(usable,default=None))),flush=True)
    require(all(digest(resolve(path))==expected for path,expected in inputs.items()), "Bound input changed during run")
    usable = sorted((record for record in results if record["numeric_objective"] is not None),
                    key=lambda record:(record["numeric_objective"],record["proposal_index"]))
    improved = [record for record in usable if record["numeric_objective"]<baseline]
    summary = dict(status="BOUNDED_MATCHING_HINT_SHORTLIST_FINISHED",inputs_sha256=inputs,outputs_sha256=outputs,
                   manifest_path=key(args.out/"manifest.json"),manifest_sha256=digest(args.out/"manifest.json"),
                   probes=len(results),numerically_optimal_count=sum(record["optimal"] for record in results),
                   no_usable_numeric_solution_count=len(results)-len(usable),baseline_numeric_objective=baseline,
                   best=usable[0] if usable else None,numerically_improving_candidates=improved,
                   numerical_improvement_count=len(improved),records=results,native_pair_gates_run=0,
                   independent_exact_proofs_claimed=0,elapsed_seconds=time.perf_counter()-started,
                   role_counts=dict(Counter(role for record in selection for role in record["selection_roles"])),
                   scope=manifest["scope"])
    write_new(args.out/"summary.json",summary)
    print(json.dumps(dict(status=summary["status"],probes=64,numerically_optimal_count=summary["numerically_optimal_count"],
                         best_numeric_objective=usable[0]["numeric_objective"] if usable else None,
                         numerical_improvement_count=len(improved),elapsed_seconds=summary["elapsed_seconds"])),flush=True)


if __name__ == "__main__":
    main()
