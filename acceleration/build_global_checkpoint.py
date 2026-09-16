"""Build a new immutable global-search index by checking saved evidence hashes.

This performs no solver calls, domain enumeration, or new numerical experiments.
"""
import argparse
from datetime import datetime, timezone
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def q(record):
    return Fraction(int(record["numerator"]), int(record["denominator"]))


def rational(value):
    return dict(numerator=str(value.numerator), denominator=str(value.denominator), approximate=float(value))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), "Never overwrite a historical checkpoint")
    verified = {}
    direct = {}
    statuses = {}
    root = ROOT / "acceleration/results"
    old_index = root / "20260916_goal_checkpoint.json"
    old_bytes = old_index.read_bytes()

    def key(path):
        path = path.resolve()
        return path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else path.as_posix()

    def resolve(name):
        path = Path(name)
        if not path.is_absolute():
            path = ROOT / path
            if not path.exists() and len(Path(name).parts) == 1:
                path = ROOT / "acceleration" / name
        return path

    def hash_file(path):
        path = resolve(str(path))
        name = key(path)
        if name not in verified:
            require(path.is_file(), "Missing referenced file: " + name)
            verified[name] = sha256(path.read_bytes()).hexdigest()
        return verified[name]

    def check_bindings(value):
        if isinstance(value, dict):
            for field, data in value.items():
                if field in ("inputs_sha256", "files_sha256", "sources_sha256", "source_sha256") and isinstance(data, dict):
                    for name, expected in data.items():
                        require(isinstance(expected, str) and re.fullmatch(r"[0-9a-fA-F]{64}", expected),
                                "Malformed digest in " + field)
                        require(hash_file(resolve(name)) == expected.lower(), "SHA mismatch: " + name)
                else:
                    check_bindings(data)
        elif isinstance(value, list):
            for item in value:
                check_bindings(item)

    def read(path, expected_status=None):
        data = json.loads(path.read_bytes())
        if expected_status:
            require(data.get("status") == expected_status, "Unexpected report status: " + str(path))
        check_bindings(data)
        direct[key(path)] = hash_file(path)
        if "status" in data:
            statuses[key(path)] = data["status"]
        return data

    run_names = ("global_pilot", "coupled_pilot", "coupled_alt", "coupled_continue", "two_trade_pilot")
    records = []
    for name in run_names:
        directory = root / ("20260916_" + name)
        two, global_only = name == "two_trade_pilot", name == "global_pilot"
        summary = read(directory / "summary.json", "BOUNDED_TWO_TRADE_COUPLED_SEARCH_FINISHED" if two else
                       "BOUNDED_GLOBAL_DEFECT_SEARCH_FINISHED" if global_only else "BOUNDED_COUPLED_GLOBAL_DEFECT_SEARCH_FINISHED")
        read(directory / "manifest.json")
        trace = read(directory / "trace_audit.json", "INDEPENDENT_TWO_TRADE_TRACE_INTERMEDIATE_GRAPHS_NUMERIC_OBJECTIVES_AND_NATIVE_GATE_BINDINGS_AUDIT_PASS" if two else
                     "INDEPENDENT_GLOBAL_TRACE_PROPOSALS_AND_NUMERIC_OBJECTIVES_AUDIT_PASS" if global_only else
                     "INDEPENDENT_COUPLED_TRACE_PROPOSALS_NUMERIC_OBJECTIVES_AND_NATIVE_GATE_BINDINGS_AUDIT_PASS")
        phase = read(directory / ("accepted_phase1_audit.json" if global_only else "accepted_phase1_intervals_audit.json"),
                     "INDEPENDENT_ACCEPTED_PHASE1_PATH_EXACT_IMPROVEMENT_AUDIT_PASS" if global_only else
                     "INDEPENDENT_TWO_TRADE_ACCEPTED_PHASE1_INTERVAL_AUDIT_PASS" if two else
                     "INDEPENDENT_COUPLED_ACCEPTED_PHASE1_INTERVAL_AUDIT_PASS")
        best = read(directory / "best_candidate.json")
        best_phase = read(directory / "best_phase1.json")
        require(hash_file(resolve(best_phase["candidate_path"])) == best_phase["candidate_sha256"], "Best original candidate hash mismatch")
        require(summary["best_numeric_objective"] == trace["best_numeric_objective"] == best_phase["numeric_objective"],
                "Best objective summaries disagree")
        require(summary["proposal_evaluations"] == trace["proposal_graphs_and_trades_checked"] and
                summary["phase1_evaluations"] == trace["actual_lp_probe_artifacts_checked"] and
                summary["accepted_moves"] == trace["accepted_moves_replayed"], "Trace counts disagree")
        lower = phase["final_exact_lower_bound"] if global_only else phase["best_exact_lower_bound"]
        upper = phase["final_exact_upper_bound"] if global_only else phase["best_exact_upper_bound"]
        require(q(lower) > 0 and q(lower) <= q(upper), "Invalid best merit interval")
        record = dict(run=name, directory=key(directory), initial_numeric_merit=trace["initial_numeric_objective"],
                      best_numeric_merit=summary["best_numeric_objective"], best_exact_interval=dict(lower=lower, upper=upper),
                      iterations=len(summary["records"]), proposal_artifacts=summary["proposal_evaluations"],
                      actual_lp_artifacts=summary["phase1_evaluations"], cached_lp_lookups=summary["cached_phase1_lookups"],
                      accepted_moves=summary["accepted_moves"], elapsed_search_seconds=summary["elapsed_seconds"],
                      exact_positive_lower_bound_probe_artifacts=trace["actual_probe_exact_positive_dual_lower_bounds"],
                      native_local_gate_status_counts=trace.get("native_local_status_counts"),
                      exact_accepted_change_counts=dict(strict_improvement=phase.get("strict_improvement_moves", summary["accepted_moves"]),
                                                       strict_uphill=phase.get("strict_uphill_moves", 0),
                                                       overlapping_intervals=phase.get("interval_overlap_moves", 0)),
                      limits={key_: summary["manifest"][key_] for key_ in
                              ("iterations", "neighbors", "lp_best", "lp_random", "seconds_per_lp")},
                      best_original_candidate_path=best_phase["candidate_path"],
                      best_original_candidate_sha256=best_phase["candidate_sha256"],
                      best_pair_ac_independently_nonempty=False)
        if two:
            require(summary["accepted_atomic_trades"] == trace["accepted_atomic_trades_replayed"] ==
                    phase["accepted_atomic_trades_checked"], "Atomic trade counts differ")
            record["accepted_atomic_trades"] = summary["accepted_atomic_trades"]
        if not global_only:
            combined = read(directory / "best_combined_evidence.json",
                            "INDEPENDENT_TWO_TRADE_BEST_LOCAL_PASS_GLOBAL_OBSTRUCTION_BOUND" if two else
                            "INDEPENDENT_COUPLED_BEST_LOCAL_PASS_GLOBAL_OBSTRUCTION_BOUND")
            pair = read(directory / "best_pair_independent_audit.json", "INDEPENDENT_EXACT_PAIR_DOMAIN_AUDIT_PASS")
            require(combined["candidate_sha256"] == best_phase["candidate_sha256"] and
                    pair["propagation_status"] == "ARC_CONSISTENT_NONEMPTY" and
                    len(pair["independently_reenumerated_domains"]) == 84, "Best local proof binding mismatch")
            pair_inputs = [(resolve(path), digest) for path, digest in pair["inputs_sha256"].items()
                           if path.endswith("_pairs.json")]
            require(len(pair_inputs) == 1, "Ambiguous native pair proof input")
            native_pair = json.loads(pair_inputs[0][0].read_bytes())
            require(hash_file(pair_inputs[0][0]) == pair_inputs[0][1], "Native pair proof hash mismatch")
            record.update(best_pair_ac_independently_nonempty=True,
                          original_complete_star_choices=combined["original_domain_choices"],
                          final_pair_ac_choices=sum(map(len, native_pair["surviving_domain_ids"])),
                          pair_deletion_events_independently_replayed=pair["events_verified"],
                          exact_best_integer_rhs=combined["best_integer_certificate_rhs"])
        else:
            record.update(exact_best_integer_rhs=phase["best_integer_certificate_rhs"],
                          local_condition_note="This unfiltered pilot's best has no independent nonempty-pair claim in this index.")
        records.append(record)

    barrier_dir = root / "20260916_two_trade_intermediate"
    barrier = read(barrier_dir / "barrier_audit.json", "EXACT_RECORDED_ORDER_MERIT_BARRIER_CHECK_PASS")
    intermediate = read(barrier_dir / "summary.json", "ACCEPTED_TWO_TRADE_INTERMEDIATE_NATIVE_CHECK_FINISHED")
    intermediate_phase = read(barrier_dir / "phase1_audit.json", "INDEPENDENT_PHASE1_GRAPH_MODEL_PRIMAL_DUAL_AUDIT_PASS")
    require(q(barrier["intermediate_lower"]) == q(intermediate_phase["exact_dual_lower_bound"]) and
            q(barrier["intermediate_upper"]) == q(intermediate_phase["exact_primal_upper_bound"]), "Barrier interval mismatch")
    require(q(barrier["intermediate_lower"]) - q(barrier["initial_upper"]) == q(barrier["guaranteed_first_step_increase"])
            > Fraction(1, 2), "Recorded first step barrier not proved")
    require(barrier["intermediate_pair_ac"] == "NATIVE_NONEMPTY_NOT_INDEPENDENTLY_REPLAYED", "Intermediate proof scope changed")
    require(intermediate["pair_status"] == "ARC_CONSISTENT_NONEMPTY", "Intermediate native pair status mismatch")
    current = records[-1]
    require(current["final_pair_ac_choices"] == 13665 and current["best_numeric_merit"] == 7.332122013712173,
            "Current best differs from expected finalized run")
    require(current["best_numeric_merit"] == min(record["best_numeric_merit"] for record in records), "Not best indexed merit")
    require(not (ROOT / "submission.txt").exists(), "Unexpected submission artifact; reassess checkpoint claims")
    initial_lower = read(root / "20260916_global_pilot/accepted_phase1_audit.json")["initial_exact_lower_bound"]
    direct[key(old_index)] = hash_file(old_index)
    direct[key(Path(__file__))] = hash_file(Path(__file__))
    require(old_index.read_bytes() == old_bytes, "Historical goal checkpoint changed during indexing")
    output = dict(status="HASH_VERIFIED_GLOBAL_RESEARCH_CHECKPOINT", schema_version=1,
                  created_utc=datetime.now(timezone.utc).isoformat(),
                  goal=dict(active=True, complete=False,
                            objective="Construct an independently verified srg(99,14,1,2) or prove general nonexistence",
                            state_authority="Parent task explicitly retains the active research goal; this index does not change orchestrator state"),
                  graph_constructed=False, general_nonexistence_proved=False, exhaustive_coverage=False,
                  submission_txt_exists=False, previous_goal_checkpoint_preserved=dict(path=key(old_index), sha256=hash_file(old_index)),
                  initial_numeric_merit=22.22012043066488, initial_exact_lower_bound=initial_lower,
                  current_best=current, current_best_merit_zero=False,
                  certified_initial_to_current_merit_decrease_at_least=rational(q(initial_lower)-q(current["best_exact_interval"]["upper"])),
                  runs=records,
                  recorded_two_trade_barrier=dict(report=key(barrier_dir / "barrier_audit.json"),
                      intermediate_exact_interval=dict(lower=barrier["intermediate_lower"], upper=barrier["intermediate_upper"]),
                      exact_first_step_increase_at_least=barrier["guaranteed_first_step_increase"],
                      single_trade_acceptance_allowance=0.5, intermediate_native_pair_ac="NONEMPTY",
                      intermediate_pair_ac_independently_replayed=False,
                      scope="Only the recorded ordering crosses this merit barrier; no all-path obstruction is claimed."),
                  limits_and_scope=dict(
                      sampled_search_only=True, random_choice_sequence_replayed=False,
                      all_sampled_proposals_lp_solved=False, reported_counts_are_artifacts_not_unique_K=True,
                      native_star_limits=dict(seconds=30, global_nodes=2000000, per_vertex_domains=20000),
                      native_pair_limits=dict(seconds=30, compatibility_checks=500000000, process_timeout_seconds=40),
                      independent_best_pair_limits=dict(seconds=30, global_domain_nodes=3000000, per_vertex_domains=20000),
                      caps_mean="INCOMPLETE/UNKNOWN; no infeasibility or unavailable local pass is credited",
                      best_pair_audits_hit_caps=False,
                      native_gates_of_other_states="Input/hash/status consistency checked, without independent complete-domain/AC replay",
                      two_trade_sampling="Bounded nonuniform intermediate branches; endpoints remove at least three original edges; not exhaustive",
                      phase1_exact_optimum_claimed=False,
                      exact_intervals_claimed=True,
                      numeric_merit_alone_proves_infeasibility=False,
                      integer_certificates_scope="Only each fixed complete overlap assignment; all indexed best candidates still excluded",
                      pair_ac_scope="Complete local domain support, not a simultaneous graph assignment",
                      fixed_graph_model="168 fixed overlap edges, absent other overlap/same-fibre edges, 1680 disjoint variables in[0,1]; no disjoint compression totals",
                      central_E72_inventory_changed=False),
                  direct_artifacts_sha256=direct, report_statuses=statuses,
                  referenced_files_sha256=verified, verified_referenced_file_count=len(verified),
                  indexing_only_no_new_numeric_or_domain_search=True)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(output, indent=2, allow_nan=False) + "\n")
    print(json.dumps(dict(status=output["status"], referenced_files=len(verified), direct_artifacts=len(direct),
                          current_best=current["best_numeric_merit"], pair_choices=current["final_pair_ac_choices"],
                          output_sha256=sha256(args.out.read_bytes()).hexdigest())))


if __name__ == "__main__":
    main()
