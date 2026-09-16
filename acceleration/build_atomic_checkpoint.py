"""Index completed atomic-cycle evidence, checking hashes but rerunning no searches."""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re

from build_global_checkpoint import require

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "acceleration/results"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), "Never overwrite a prior checkpoint")
    previous_path = RESULTS / "20260916_global_checkpoint.json"
    previous_bytes = previous_path.read_bytes()
    previous_sha = sha256(previous_bytes).hexdigest()
    require(previous_sha == "57ff51628e6fb2f44797a6d88f35fbee60e0aa4bc795f884337680d5dd3fb4f2", "Unexpected previous checkpoint")
    previous = json.loads(previous_bytes)
    verified, direct, statuses = {}, {}, {}

    def resolve(name):
        path = Path(name)
        if not path.is_absolute():
            path = ROOT / path
            if not path.exists() and len(Path(name).parts) == 1:
                path = ROOT / "acceleration" / name
        return path

    def key(path):
        path = path.resolve()
        return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix()

    def digest(path):
        path = resolve(str(path))
        name = key(path)
        if name not in verified:
            require(path.is_file(), "Missing bound artifact: " + name)
            verified[name] = sha256(path.read_bytes()).hexdigest()
        return verified[name]

    def bindings(data):
        if isinstance(data, dict):
            for field, value in data.items():
                if field in ("inputs_sha256", "files_sha256", "sources_sha256", "source_sha256") and isinstance(value, dict):
                    for name, expected in value.items():
                        require(isinstance(expected, str) and re.fullmatch(r"[0-9a-fA-F]{64}", expected), "Malformed hash")
                        require(digest(resolve(name)) == expected.lower(), "Changed referenced artifact: " + name)
                else:
                    bindings(value)
        elif isinstance(data, list):
            for value in data:
                bindings(value)

    def read(path, status=None):
        data = json.loads(path.read_bytes())
        if status:
            require(data.get("status") == status, "Unexpected/incomplete report: " + str(path))
        bindings(data)
        direct[key(path)] = digest(path)
        if "status" in data:
            statuses[key(path)] = data["status"]
        return data

    qa = read(RESULTS / "20260916_atomic_cycle_qa/qa.json", "ATOMIC_CYCLE_NATIVE_QA_PASS")
    legal_qa = read(RESULTS / "20260916_atomic_cycle_qa/both_audit.json", "INDEPENDENT_COMPLETE_ATOMIC_CYCLE_FAMILY_PASS")
    math = read(RESULTS / "20260916_atomic_matching_math.json", "INDEPENDENT_MATCHING_DECOMPOSITION_AND_ABSTRACT_CYCLE_COUNT_PASS")
    geometry = read(RESULTS / "20260916_atomic_geometry_auditor_qa.json", "ATOMIC_GEOMETRY_AUDITOR_REAL_CONTROL_AND_CORRUPTION_CHECKS_PASS")
    require(all(row["rejected"] for row in qa["native_negative_controls"] + qa["independent_audit_negative_controls"]),
            "An atomic generator negative control failed")
    require(len(geometry["corruption_rejections"]) == 10 and legal_qa["legal_cycles"] == 16299,
            "Unexpected atomic controls")
    seed_path = resolve(previous["current_best"]["best_original_candidate_path"])
    require(digest(seed_path) == previous["current_best"]["best_original_candidate_sha256"], "Previous best changed")
    seed_edges = set(map(tuple, json.loads(seed_path.read_bytes())["overlap_edges_outer_zero_based"]))
    prior_7605 = next(row for row in previous["runs"] if row["run"] == "coupled_continue")
    old_endpoint_path = resolve(prior_7605["best_original_candidate_path"])
    require(digest(old_endpoint_path) == prior_7605["best_original_candidate_sha256"], "Historical escape endpoint changed")
    old_endpoint_edges = set(map(tuple, json.loads(old_endpoint_path.read_bytes())["overlap_edges_outer_zero_based"]))
    runs = []
    for name in ("atomic3_pilot", "atomic4_pilot", "atomic_both_pilot"):
        directory = RESULTS / ("20260916_" + name)
        summary = read(directory / "summary.json", "BOUNDED_ATOMIC_CYCLE_COUPLED_SEARCH_FINISHED")
        manifest = read(directory / "manifest.json")
        trace = read(directory / "trace_audit.json", "INDEPENDENT_ATOMIC_CYCLE_TRACE_GRAPH_MODELS_MERITS_SELECTION_AND_NATIVE_GATE_BINDINGS_AUDIT_PASS")
        interval = read(directory / "accepted_phase1_intervals_audit.json", "INDEPENDENT_ATOMIC_ACCEPTED_PHASE1_INTERVAL_AUDIT_PASS")
        pair = read(directory / "best_pair_independent_audit.json", "INDEPENDENT_EXACT_PAIR_DOMAIN_AUDIT_PASS")
        combined = read(directory / "best_combined_evidence.json", "INDEPENDENT_ATOMIC_BEST_LOCAL_PASS_GLOBAL_OBSTRUCTION_BOUND")
        best = read(directory / "best_candidate.json")
        best_phase = read(directory / "best_phase1.json")
        require(set(map(tuple, best["overlap_edges_outer_zero_based"])) == seed_edges,
                "Unexpected new best requires reassessing checkpoint state")
        require(combined["candidate_sha256"] == best_phase["candidate_sha256"] == digest(resolve(best_phase["candidate_path"])),
                "Best candidate proof binding differs")
        require(summary["best_numeric_objective"] == trace["best_numeric_objective"] == previous["current_best"]["best_numeric_merit"],
                "Unexpected changed merit")
        require(interval["initial_to_best_strict_improvement_certified"] is False, "Unexpected improvement claim")
        require(pair["evidence_method"] == "PRIOR_INDEPENDENT_PROOF_PLUS_EXACT_LABELED_GRAPH_IDENTITY"
                and pair["new_domain_enumeration_nodes"] == 0 and pair["same_exact_phase1_optimum"],
                "Unexpected domain-proof reuse status")
        counts = (("proposal_evaluations", "proposal_graphs_and_trades_checked"),
                  ("proposal_occurrences", "proposal_occurrences_checked"),
                  ("cached_proposal_batches", "cached_proposal_batches_checked"),
                  ("phase1_evaluations", "actual_lp_probe_artifacts_checked"),
                  ("accepted_moves", "accepted_moves_replayed"),
                  ("accepted_edge_replacements", "accepted_edge_replacements_checked"))
        require(all(summary[a] == trace[b] for a,b in counts), "Trace and search counts disagree")
        family_records = []
        for record in trace["complete_family_reports"]:
            family = record["independent_complete_family_audit"]
            require(family["status"] == "INDEPENDENT_COMPLETE_ATOMIC_CYCLE_FAMILY_PASS", "Incomplete family comparison")
            family_records.append(dict(proposal_path=record["proposal_path"], cycle_size=family["cycle_size"],
                                       raw_cycles=family["raw_cycles"], legal_cycles=family["legal_cycles"]))
        require(len(family_records) == trace["distinct_batches_independently_reenumerated"] and
                sum(row["legal_cycles"] for row in family_records) == summary["proposal_evaluations"],
                "Distinct proposal-family counts disagree")
        require(trace["actual_probe_exact_positive_dual_lower_bounds"] == summary["phase1_evaluations"],
                "An indexed actual probe lacks positive exact dual evidence")
        terminal_probe = summary["records"][0]["previous_probe"]
        for row in summary["records"]:
            if row["accepted"]:
                terminal_probe = row["chosen_probe"]
        terminal_path = resolve(terminal_probe["candidate_path"])
        require(digest(terminal_path) == terminal_probe["candidate_sha256"], "Terminal candidate changed")
        terminal_edges = set(map(tuple, json.loads(terminal_path.read_bytes())["overlap_edges_outer_zero_based"]))
        runs.append(dict(run=name, cycle_size=manifest["cycle_size"], iterations=len(summary["records"]),
                         actual_lp_artifacts=summary["phase1_evaluations"], cached_lp_lookups=summary["cached_phase1_lookups"],
                         proposal_finals_across_distinct_batches=summary["proposal_evaluations"],
                         proposal_occurrences_including_batch_reuse=summary["proposal_occurrences"],
                         cached_proposal_batches=summary["cached_proposal_batches"], complete_families=family_records,
                         accepted_moves=summary["accepted_moves"], accepted_edge_replacements=summary["accepted_edge_replacements"],
                         strict_improvement_moves=interval["strict_improvement_moves"], strict_uphill_moves=interval["strict_uphill_moves"],
                         exact_uphill_bounds=[row["guaranteed_uphill_increase"] for row in interval["accepted"]
                                             if row["exact_change_classification"] == "STRICT_UPHILL"],
                         best_unchanged_exact_labeled_seed=True, best_numeric_merit=summary["best_numeric_objective"],
                         terminal_numeric_merit=terminal_probe["objective"],
                         terminal_matches_historical7605_seed=terminal_edges == old_endpoint_edges,
                         elapsed_search_seconds=summary["elapsed_seconds"],
                         independent_best_pair_evidence="Prior independent84-domain/pair proof plus exact labeled graph identity; no duplicate enumeration",
                         all_actual_lp_artifacts_have_exact_positive_dual_bound=True,
                         random_selection_and_escape_draws_replayed=trace["random_selection_and_escape_draws_replayed"],
                         limits={field: manifest[field] for field in ("iterations", "lp_best", "lp_diverse", "lp_random", "seconds_per_lp")},
                         native_gate_status_counts=trace["native_local_status_counts"]))
    require([row["accepted_moves"] for row in runs] == [0,0,1] and
            [row["strict_uphill_moves"] for row in runs] == [0,0,1], "Unexpected accepted research outcome")
    require(not (ROOT / "submission.txt").exists(), "Unexpected submission artifact")
    require(previous_path.read_bytes() == previous_bytes, "Previous checkpoint changed during indexing")
    direct[key(previous_path)] = digest(previous_path)
    direct[key(Path(__file__))] = digest(Path(__file__))
    direct[key(Path(__file__).with_name("build_global_checkpoint.py"))] = digest(Path(__file__).with_name("build_global_checkpoint.py"))
    current = dict(previous["current_best"])
    current.update(unchanged_through_atomic_runs=True, exact_phase1_optimum_change_from_previous_checkpoint=0,
                   full_pair_ac_surviving_choices=13665, no_graph_completion=True)
    result = dict(status="HASH_VERIFIED_ATOMIC_RESEARCH_CHECKPOINT", schema_version=1,
                  created_utc=datetime.now(timezone.utc).isoformat(), goal=dict(active=True, complete=False,
                  objective=previous["goal"]["objective"], state_authority="Parent research task remains active; this index does not mutate orchestrator state"),
                  graph_constructed=False, general_nonexistence_proved=False, submission_txt_exists=False,
                  previous_global_checkpoint_preserved=dict(path=key(previous_path), sha256=previous_sha),
                  current_best=current, runs=runs,
                  controls=dict(abstract_matching_math=math["abstract_controls"],
                                complete_native_vs_independent_family_seed_counts=qa["modes"],
                                native_negative_controls=len(qa["native_negative_controls"]),
                                independent_enumerator_negative_controls=len(qa["independent_audit_negative_controls"]),
                                atomic_geometry_negative_controls=len(geometry["corruption_rejections"])),
                  artifact_totals=dict(actual_lp_artifacts=sum(row["actual_lp_artifacts"] for row in runs),
                                       proposal_finals_across_batch_artifacts=sum(row["proposal_finals_across_distinct_batches"] for row in runs),
                                       proposal_occurrences_with_reuse=sum(row["proposal_occurrences_including_batch_reuse"] for row in runs),
                                       counts_overlap_between_runs_and_are_not_unique_K=True),
                  scopes_and_limits=dict(
                      complete_subfamily_geometry="All raw single-matching alternating3/4-edge cycles for each saved distinct batch state are independently reenumerated; only that declared subfamily is covered",
                      complete_lp_evaluation_of_families=False, all_family_local_minimum_or_plateau_proved=False,
                      full_conway_or_E0_exhaustive_coverage=False, best_merit_improved=False,
                      frozen_X_scores="Numerical upper bounds for heuristic selection; large values cannot rule out reoptimized improvements",
                      exact_positive_dual_bounds="Exclude only their own fixed K; repeated artifacts do not add unique coverage",
                      numeric_exact_optimum_claimed=False, exact_rational_bounds_and_recorded_uphill_claimed=True,
                      accepted_endpoint_pair_gate="Native complete-domain/pair pass; only best geometry is independently established/reused in dedicated evidence",
                      intermediate_atomic_swap_graphs_required=False,
                      native_star_limits=dict(seconds=30, global_nodes=2000000, per_vertex_domains=20000),
                      native_pair_limits=dict(seconds=30, compatibility_checks=500000000, process_timeout_seconds=40),
                      caps="INCOMPLETE/UNKNOWN; never proof of rejection or unavailable local pass",
                      central_E72_inventory_changed=False),
                  direct_artifacts_sha256=direct, report_statuses=statuses,
                  referenced_files_sha256=verified, verified_referenced_file_count=len(verified),
                  indexing_only_no_numeric_or_domain_reruns=True)
    with args.out.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(json.dumps(dict(status=result["status"], verified_files=len(verified), direct_artifacts=len(direct),
                          actual_lp_artifacts=result["artifact_totals"]["actual_lp_artifacts"],
                          output_sha256=sha256(args.out.read_bytes()).hexdigest())))


if __name__ == "__main__":
    main()
