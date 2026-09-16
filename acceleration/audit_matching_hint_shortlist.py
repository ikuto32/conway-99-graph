"""Independently replay a deterministic two-X matching shortlist and its LPs.

No native generator, search/LP producer, GPU code or optimizer is imported.
The complete family is reused only through its pinned independent report and
byte-identical native payload. Scores remain numerical ranking information.
"""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction
from hashlib import sha256
import json
from math import isfinite
from pathlib import Path
import time

from audit_certificate import full_graph, require
from audit_phase1 import evaluate
from audit_phase1_kkt import inspect_artifact, rational

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "acceleration/results"


def resolve(path):
    path = Path(str(path).replace("\\", "/"))
    return path if path.is_absolute() else ROOT / path


def signature(edges):
    return bytes(value for edge in sorted(map(tuple, edges)) for value in edge)


def edge_hash(sig):
    edges = [[sig[i], sig[i + 1]] for i in range(0, len(sig), 2)]
    return sha256(json.dumps(edges, separators=(",", ":")).encode("ascii")).hexdigest()


def value(record):
    return Fraction(int(record["numerator"]), int(record["denominator"]))


def choose(moves, keys, scores, excluded):
    expanded = [i for i, move in enumerate(moves) if move["changed_edges"] >= 5 or len(move["alternating_cycles"]) > 1]
    eligible = [i for i in expanded if keys[i] not in excluded]
    coordinates = [(m["root_group"], m["matching_class"]) for m in moves]
    partitions = [tuple(sorted(len(c) // 2 for c in m["alternating_cycles"])) for m in moves]
    triples = [(*coordinate, partition) for coordinate, partition in zip(coordinates, partitions)]
    rank = lambda i: (scores[i], i)
    groups, shapes, strata = defaultdict(list), defaultdict(list), defaultdict(list)
    for i in eligible:
        groups[coordinates[i]].append(i)
        shapes[partitions[i]].append(i)
        strata[triples[i]].append(i)
    require(set(groups) == {(g, f"same_{s}") for g in range(7) for s in range(2)}, "Missing eligible coordinate")
    selected, roles = [], {}

    def add(index, role):
        if index not in roles:
            selected.append(index)
            roles[index] = []
        roles[index].append(role)

    for coordinate in sorted(groups):
        add(min(groups[coordinate], key=rank), "coordinate_minimum")
    for partition in sorted(shapes):
        add(min(shapes[partition], key=rank), "global_cycle_partition_minimum")
    represented = {triples[i] for i in selected}
    missing_stratum_minima = [min(indices, key=rank) for triple, indices in strata.items() if triple not in represented]
    for i in sorted(missing_stratum_minima, key=rank):
        if len(selected) >= 32:
            break
        add(i, "unrepresented_coordinate_cycle_partition_minimum")
    require(len(selected) == 32, "Wrong diversity prefix size")
    for i in sorted(eligible, key=rank):
        if len(selected) >= 64:
            break
        if i not in roles:
            add(i, "global_score_fill")
    require(len(selected) == 64, "Insufficient shortlist")
    return selected, roles, coordinates, partitions, expanded, eligible


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--native", type=Path, default=RESULTS / "20260916_whole_matching_qa/all.json")
    parser.add_argument("--score-summary", type=Path, default=RESULTS / "20260916_whole_matching_coordinate_x_diagnostic/summary.json")
    parser.add_argument("--scores", type=Path, default=RESULTS / "20260916_whole_matching_coordinate_x_diagnostic/combined_scores.json")
    parser.add_argument("--initial", type=Path, default=RESULTS / "20260916_two_trade_pilot/best_candidate.json")
    parser.add_argument("--initial-phase1", type=Path, default=RESULTS / "20260916_two_trade_pilot/best_phase1.json")
    parser.add_argument("--previous", type=Path, default=RESULTS / "20260916_whole_matching_pilot")
    parser.add_argument("--family-audit", type=Path, default=RESULTS / "20260916_whole_matching_qa/all_independent_audit.json")
    parser.add_argument("--family-audit-sha256", default="2b74ea6d22cbb5904616536a7e6c60450ed7a613e1c99f3226d1ae4e397d870b")
    args = parser.parse_args()
    require(not args.out.exists(), "Preserve prior shortlist audit")
    started = time.perf_counter()
    hashes = {}

    def bind(path, expected=None):
        path = resolve(path)
        name = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path)
        actual = hashes.get(name)
        if actual is None:
            actual = sha256(path.read_bytes()).hexdigest()
            hashes[name] = actual
        require(expected is None or actual == expected, "Dependency SHA mismatch: " + name)
        return actual

    def load(path):
        bind(path)
        return json.loads(resolve(path).read_bytes())

    summary, manifest = load(args.run / "summary.json"), load(args.run / "manifest.json")
    require(summary["status"] == "BOUNDED_MATCHING_HINT_SHORTLIST_FINISHED" and
            manifest["status"] == "BOUNDED_MATCHING_HINT_SHORTLIST_MANIFEST", "Shortlist is not finalized")
    require(summary["manifest_sha256"] == bind(args.run / "manifest.json") and
            resolve(summary["manifest_path"]).resolve() == (args.run / "manifest.json").resolve(), "Manifest binding mismatch")
    require(summary["inputs_sha256"] == manifest["inputs_sha256"], "Summary input bindings differ")
    for mapping in (manifest["inputs_sha256"], summary["outputs_sha256"]):
        for path, expected in mapping.items():
            bind(path, expected)
    for path in (args.native, args.score_summary, args.scores, args.initial, args.initial_phase1, args.previous / "summary.json"):
        require(manifest["inputs_sha256"].get(resolve(path).relative_to(ROOT).as_posix()) == bind(path),
                "Supplied input is not the bound shortlist input")
    bind(args.family_audit, args.family_audit_sha256)
    family = load(args.family_audit)
    require(family["status"] == "INDEPENDENT_COMPLETE_WHOLE_SAME_SIGN_MATCHING_FAMILY_PASS" and family["selector"] == "all",
            "Wrong reused complete-family proof")
    for path, expected in family["inputs_sha256"].items():
        bind(path, expected)
    family_bound = {resolve(path).resolve(): expected for path, expected in family["inputs_sha256"].items()}
    require(family_bound.get(args.native.resolve()) == bind(args.native) and
            family_bound.get(args.initial.resolve()) == bind(args.initial), "Complete family is bound to a different base or payload")

    prior_summary, prior_audit = load(args.previous / "summary.json"), load(args.previous / "trace_audit.json")
    require(prior_audit["status"] == "INDEPENDENT_WHOLE_MATCHING_TRACE_GRAPH_MODELS_MERITS_SELECTION_AND_NATIVE_GATE_BINDINGS_AUDIT_PASS",
            "Prior search lacks independent trace audit")
    for path, expected in prior_audit["inputs_sha256"].items():
        bind(path, expected)
    paths = sorted((args.previous / "probes").glob("*_candidate.json"))
    require(len(paths) == prior_summary["phase1_evaluations"] == prior_audit["actual_lp_probe_artifacts_checked"] == 129,
            "Prior probe inventory differs")
    excluded, exclusion_rows = set(), []
    for path in paths:
        candidate = load(path)
        sig = signature(candidate["overlap_edges_outer_zero_based"])
        excluded.add(sig)
        exclusion_rows.append(dict(candidate_path=path.resolve().relative_to(ROOT).as_posix(), candidate_sha256=bind(path),
                                   overlap_edges_sha256=edge_hash(sig)))
    require(manifest["excluded"] == exclusion_rows and manifest["previous_candidate_artifacts"] == len(paths) and
            manifest["previous_unique_edge_signatures"] == len(excluded), "Prior-edge exclusion list differs")
    initial, phase = load(args.initial), load(args.initial_phase1)
    initial_sig = signature(initial["overlap_edges_outer_zero_based"])
    require(initial_sig in excluded and phase["overlap_edges_sha256"] == edge_hash(initial_sig), "Initial K/probe mismatch")
    adjacency, unknown = full_graph(initial)
    edges = [list(edge) for edge in sorted((u - 15, v - 15) for u, v in unknown)]
    require(phase["edge_variables"] == edges, "Current X column order differs")
    current_x = phase["numeric_edge_values"]
    require(len(current_x) == 1680 and all(type(x) in (int, float) and isfinite(x) and 0 <= x <= 1 for x in current_x),
            "Invalid current X")
    baseline_candidate = resolve(phase["candidate_path"])
    require(signature(load(baseline_candidate)["overlap_edges_outer_zero_based"]) == initial_sig, "Original baseline candidate differs")
    baseline_audit = inspect_artifact(baseline_candidate, args.initial_phase1)

    score_summary, scores = load(args.score_summary), load(args.scores)
    require(score_summary["status"] == "COORDINATE_X_GPU_RESCORE_AND_INDEPENDENT_SAMPLE_AUDIT_PASS" and
            scores["status"] == "TWO_FEASIBLE_X_NUMERICAL_UPPER_BOUND_RANKING", "Wrong ranking status")
    for mapping in (score_summary["inputs_sha256"], score_summary["outputs_sha256"]):
        for path, expected in mapping.items():
            bind(path, expected)
    coordinate_x = {}
    clipped = 0
    for record in score_summary["coordinate_runs"]:
        matrix, result = load(record["matrix_path"]), load(record["result_path"])
        bind(record["matrix_path"], record["matrix_sha256"])
        bind(record["result_path"], record["result_sha256"])
        coordinate = f"{matrix['root_group']}/{matrix['matching_class']}"
        require(coordinate == record["coordinate"] and coordinate not in coordinate_x and
                result["matrix_sha256"] == record["matrix_sha256"] and matrix["edge_variables"] == edges,
                "Coordinate X source/order mismatch")
        raw = result["primal_values"][:1680]
        require(len(raw) == 1680 and all(type(x) in (int, float) and isfinite(x) for x in raw), "Invalid coordinate X")
        projected = [min(1, max(0, x)) for x in raw]
        clipped += sum(a != b for a, b in zip(raw, projected))
        require(record["clipped_entries"] == sum(a != b for a, b in zip(raw, projected)), "X projection count differs")
        coordinate_x[coordinate] = projected
    require(set(coordinate_x) == {f"{g}/same_{s}" for g in range(7) for s in range(2)}, "Missing coordinate X")

    native = load(args.native)
    options = native.pop("overlap_candidates")
    moves = native["moves"]
    keys = [signature(option) for option in options]
    require(len(options) == len(moves) == family["legal_count"] == 74638 and len(set(keys)) == len(keys), "Family count/identity mismatch")
    for field in ("current_x_total", "coordinate_x_total", "minimum_total"):
        require(type(scores[field]) is list and len(scores[field]) == len(keys) and
                all(type(x) in (int, float) and isfinite(x) and x >= 0 for x in scores[field]), "Invalid score vector")
    require(all(c == min(a, b) for a, b, c in zip(scores["current_x_total"], scores["coordinate_x_total"], scores["minimum_total"])),
            "Combined score differs from minimum")
    selected, roles, coordinates, partitions, expanded, eligible = choose(moves, keys, scores["minimum_total"], excluded)
    require(manifest["expanded_candidates"] == len(expanded) and manifest["eligible_new_candidates"] == len(eligible), "Wrong eligibility counts")
    require(manifest["shortlist_count"] == 64 and manifest["diversity_prefix_count"] == 32 and
            manifest["basis_policy"] == "COLD_IPM_BASIS_NONE" and manifest["seconds_per_lp"] == 30 and
            manifest["tie_break"] == "(minimum_total, native proposal_index)", "Wrong bounded selection policy")
    expected_selection = [dict(selection_order=n, proposal_index=i, selection_roles=roles[i], score=scores["minimum_total"][i],
                               current_x_score=scores["current_x_total"][i], coordinate_x_score=scores["coordinate_x_total"][i],
                               root_group=coordinates[i][0], matching_class=coordinates[i][1], cycle_partition=list(partitions[i]),
                               move=moves[i], overlap_edges_sha256=edge_hash(keys[i])) for n, i in enumerate(selected)]
    require(manifest["selection"] == expected_selection, "Deterministic selection order/roles/metadata differs")
    selected_options = {i: options[i] for i in selected}
    del options
    require(len(summary["records"]) == summary["probes"] == 64, "Wrong actual shortlist size")
    require(len(list((args.run / "probes").glob("*_candidate.json"))) ==
            len(list((args.run / "probes").glob("*_phase1.json"))) == 64, "Unexpected probe files")
    reports, max_score_error = [], 0.0
    for selected_record, record in zip(expected_selection, summary["records"]):
        require(all(record.get(k) == v for k, v in selected_record.items()), "Actual probe selection differs")
        i = record["proposal_index"]
        candidate_path, result_path = resolve(record["candidate_path"]), resolve(record["result_path"])
        stem = f"selection_{record['selection_order']:02d}_index_{i}"
        require(candidate_path.resolve() == (args.run / "probes" / (stem + "_candidate.json")).resolve() and
                result_path.resolve() == (args.run / "probes" / (stem + "_phase1.json")).resolve(), "Probe filename/order differs")
        candidate, result = load(candidate_path), load(result_path)
        bind(candidate_path, record["candidate_sha256"])
        bind(result_path, record["result_sha256"])
        require(signature(candidate["overlap_edges_outer_zero_based"]) == keys[i] and
                candidate["selection"] == selected_record and candidate["native_source_sha256"] == bind(args.native) and
                resolve(candidate["native_source_path"]).resolve() == args.native.resolve() and
                candidate["manifest_sha256"] == bind(args.run / "manifest.json") and
                resolve(candidate["manifest_path"]).resolve() == (args.run / "manifest.json").resolve(), "Candidate provenance mismatch")
        require(result["overlap_edges_sha256"] == edge_hash(keys[i]) and
                resolve(result["candidate_path"]).resolve() == candidate_path.resolve(), "LP attached to wrong K")
        for field in ("numeric_objective", "optimal", "status", "solve_seconds", "elapsed_seconds"):
            require(record[field] == result[field], "LP record differs: " + field)
        require(record["solver_model_status"] == result["primal_model_status"], "LP model status differs")
        for name, expected in result["source_sha256"].items():
            require(Path(name).name == name, "Unexpected LP source path")
            bind(ROOT / "acceleration" / name, expected)
        current = evaluate(candidate, current_x)["total_violation"]
        alternate = evaluate(candidate, coordinate_x[f"{record['root_group']}/{record['matching_class']}"])["total_violation"]
        error = max(abs(current - record["current_x_score"]), abs(alternate - record["coordinate_x_score"]),
                    abs(min(current, alternate) - record["score"]))
        require(error <= 1e-7 * max(1, current, alternate), "Selected two-X GPU score differs from independent full99")
        max_score_error = max(max_score_error, error)
        require(result["optimal"] is True, "This complete-interval report requires a usable near-optimal probe")
        report = inspect_artifact(candidate_path, result_path)
        improvement = value(baseline_audit["exact_dual_lower_bound"]) - value(report["exact_primal_upper_bound"])
        reports.append(dict(proposal_index=i, selection_order=record["selection_order"], candidate_path=record["candidate_path"],
                            result_path=record["result_path"], numeric_objective=record["numeric_objective"],
                            independent_current_x_score=current, independent_coordinate_x_score=alternate,
                            independent_minimum_score=min(current, alternate), score_absolute_error=error,
                            phase1_audit=report, exact_strict_improvement_over_baseline=improvement > 0,
                            exact_improvement_margin=rational(improvement)))
    require(summary["numerically_optimal_count"] == 64 and summary["no_usable_numeric_solution_count"] == 0,
            "Usable probe totals differ")
    numeric_order = sorted(summary["records"], key=lambda row: (row["numeric_objective"], row["proposal_index"]))
    improving = [row for row in numeric_order if row["numeric_objective"] < phase["numeric_objective"]]
    require(summary["best"] == numeric_order[0] and summary["numerically_improving_candidates"] == improving and
            summary["numerical_improvement_count"] == len(improving) and
            summary["baseline_numeric_objective"] == manifest["baseline_numeric_objective"] == phase["numeric_objective"],
            "Best/improving shortlist summary differs")
    require(summary["role_counts"] == dict(Counter(role for row in expected_selection for role in row["selection_roles"])),
            "Selection role totals differ")
    require(summary["native_pair_gates_run"] == 0 and summary["independent_exact_proofs_claimed"] == 0, "Producer scope differs")
    for source in (Path(__file__), ROOT / "acceleration/audit_certificate.py", ROOT / "acceleration/audit_phase1.py", ROOT / "acceleration/audit_phase1_kkt.py"):
        bind(source)
    result = dict(status="INDEPENDENT_MATCHING_HINT_SELECTION_TWO_X_SCORES_AND_EXACT_PHASE1_BOUNDS_AUDIT_PASS",
                  inputs_sha256=hashes, complete_family_proof_reuse="Pinned prior independent proof plus byte-identical base candidate and native all payload",
                  reused_complete_family_legal_finals=family["legal_count"], expanded_candidates=len(expanded), eligible_new_candidates=len(eligible),
                  prior_candidate_signatures_excluded=len(excluded), selected_new_distinct_candidates=64,
                  deterministic_indices_and_roles_replayed=True, selection_roles=summary["role_counts"],
                  selected_two_x_scores_independently_recomputed=128, max_selected_score_absolute_error=max_score_error,
                  coordinate_x_vectors_checked=14, coordinate_x_entries_clipped=clipped,
                  exact_phase1_intervals_checked=64, exact_positive_lower_bounds=sum(r["phase1_audit"]["exact_positive_dual_bound"] for r in reports),
                  baseline_phase1_audit=baseline_audit, baseline_numeric_objective=phase["numeric_objective"],
                  best_proposal_index=numeric_order[0]["proposal_index"], best_numeric_objective=numeric_order[0]["numeric_objective"],
                  exact_strict_improvement_indices=[r["proposal_index"] for r in reports if r["exact_strict_improvement_over_baseline"]],
                  probe_reports=reports, native_pair_or_domain_checks_performed=False, solver_or_producer_imported=False,
                  elapsed_seconds=time.perf_counter() - started,
                  scope="Selection replay and exact fixed-K phase-I bounds for this64-candidate shortlist only. Selected two-X merits independently recalculated; unselected ranking values are bound GPU diagnostics, not exhaustive CPU re-evaluations. Positive lower bounds exclude only their fixed K. An improved merit does not imply pair-AC feasibility or graph completion; no new global coverage or local-optimality claim.")
    with args.out.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("inputs_sha256", "probe_reports", "baseline_phase1_audit")}))


if __name__ == "__main__":
    main()
