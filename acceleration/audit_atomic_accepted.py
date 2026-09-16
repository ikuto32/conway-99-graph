"""Independent atomic-cycle coupled-search intervals, allowing recorded uphill moves.

Native local-pass statuses are checked as gates here. The best candidate's
complete-domain and pair proof must additionally be replayed independently;
no native gate is promoted to a proof by this phase-I path audit.
"""
import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import time

from audit_certificate import audit as audit_integer, full_graph, require
from audit_phase1_kkt import inspect_artifact, exact_integer_certificate, rational


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def value(record):
    return Fraction(int(record["numerator"]), int(record["denominator"]))


def write_new(path, data):
    with path.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(data, indent=2, allow_nan=False) + "\n")


def check_alternating_cycle(move):
    cycle_size = move["cycle_size"]
    require(type(cycle_size) is int and cycle_size in (3, 4), "Unsupported atomic cycle size")
    removed, added = set(map(tuple, move["removed"])), set(map(tuple, move["added"]))
    require(len(removed) == len(added) == len(move["removed"]) == len(move["added"]) == cycle_size,
            "Wrong atomic edge count or repeated edges")
    require(all(type(u) is int and type(v) is int and 0 <= u < v < 84 for u, v in removed | added),
            "Invalid atomic edge coordinate")
    require(not removed & added, "Old and new matching edges overlap")
    degree_before = Counter(vertex for edge in removed for vertex in edge)
    degree_after = Counter(vertex for edge in added for vertex in edge)
    require(degree_before == degree_after and set(degree_before.values()) == {1},
            "Atomic replacement is not a matching on the same endpoints")
    cycle = move["alternating_cycle"]
    require(type(cycle) is list and all(type(v) is int for v in cycle)
            and len(cycle) == 2*cycle_size and len(set(cycle)) == len(cycle)
            and set(cycle) == set(degree_before), "Invalid alternating cycle vertices")
    require({tuple(sorted(cycle[i:i+2])) for i in range(0, len(cycle), 2)} == removed,
            "Alternating cycle old edges mismatch")
    require({tuple(sorted((cycle[i], cycle[(i+1)%len(cycle)]))) for i in range(1, len(cycle), 2)} == added,
            "Alternating cycle new edges mismatch")
    return removed, added, set(degree_before)


def check_atomic_geometry(current_edges, next_edges, move):
    removed, added, vertices = check_alternating_cycle(move)
    root_group, matching_class = move["root_group"], move["matching_class"]
    require(type(root_group) is int and 0 <= root_group < 7, "Invalid matching root group")
    require(matching_class in ("same_0", "same_1", "cross"), "Invalid matching class")
    require(removed <= current_edges and not added & current_edges, "Invalid accepted atomic cycle")
    require(current_edges - removed | added == next_edges, "Atomic cycle does not produce chosen graph")
    adjacency, _ = full_graph({"overlap_edges_outer_zero_based": [list(edge) for edge in sorted(current_edges)]})
    root_labels = {u: {v-1 for v in adjacency[u+15] if 1 <= v <= 14} for u in vertices}
    for u, v in removed | added:
        shared_groups = {s//2 for s in root_labels[u]} & {s//2 for s in root_labels[v]}
        require(shared_groups == {root_group}, "Atomic edge leaves the recorded root matching")
        signs = [next(s%2 for s in root_labels[w] if s//2 == root_group) for w in (u, v)]
        actual_class = "cross" if signs[0] != signs[1] else "same_" + str(signs[0])
        require(actual_class == matching_class, "Atomic edge changes matching sign class")
    full_graph({"overlap_edges_outer_zero_based": [list(edge) for edge in sorted(next_edges)]})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    started = time.perf_counter()
    require(not args.out.exists(), "Preserve previous accepted-path audit")
    summary_path = args.directory / "summary.json"
    summary = json.loads(summary_path.read_bytes())
    require(summary["status"] == "BOUNDED_ATOMIC_CYCLE_COUPLED_SEARCH_FINISHED", "Search not finalized")
    records = summary["records"]
    require(records, "Empty search trace")
    outdir = args.out.parent / (args.out.stem + "_details")
    outdir.mkdir(parents=True, exist_ok=False)
    files = {str(summary_path): digest(summary_path)}
    audits, candidate_edges = {}, {}

    def native_gate(gate):
        require(gate["passed"] is True, "Native gate did not pass")
        require(gate["star_status"] == "COMPLETE_DOMAINS_RECIPROCITY_ARC_CONSISTENT_NONEMPTY",
                "Incomplete/empty star gate")
        require(gate["pair_status"] == "EXACT_PAIR_DOMAIN_ARC_CONSISTENT_NONEMPTY",
                "Incomplete/empty pair gate")
        for pathkey, hashkey in (("candidate_input", "candidate_input_sha256"),
                                 ("stars_path", "stars_sha256"), ("pair_path", "pair_sha256"),
                                 ("domain_input", "domain_input_sha256")):
            path = Path(gate[pathkey])
            require(digest(path) == gate[hashkey], "Native gate input/output SHA mismatch")
            files[str(path)] = digest(path)
        stars = json.loads(Path(gate["stars_path"]).read_bytes())
        pairs = json.loads(Path(gate["pair_path"]).read_bytes())
        require(stars["status"] == gate["star_status"] and pairs["status"] == gate["pair_status"],
                "Native gate status differs from source artifact")

    def inspect(probe, name):
        candidate_path, result_path = Path(probe["candidate_path"]), Path(probe["result_path"])
        require(digest(candidate_path) == probe["candidate_sha256"], "Trace candidate SHA mismatch")
        require(digest(result_path) == probe["result_sha256"], "Trace phase-I SHA mismatch")
        result = json.loads(result_path.read_bytes())
        require(result["candidate_path"] == str(candidate_path).replace("\\", "/"), "Original candidate path mismatch")
        require(result["numeric_objective"] == probe["objective"], "Trace objective mismatch")
        candidate = json.loads(candidate_path.read_bytes())
        edges = set(map(tuple, candidate["overlap_edges_outer_zero_based"]))
        candidate_edges[str(candidate_path)] = edges
        if str(result_path) not in audits:
            audit = inspect_artifact(candidate_path, result_path)
            audit_path = outdir / (name + "_phase1_audit.json")
            write_new(audit_path, audit)
            files.update({str(path): digest(path) for path in (candidate_path, result_path, audit_path)})
            audits[str(result_path)] = audit
        return audits[str(result_path)], edges

    current = records[0]["previous_probe"]
    native_gate(summary["initial_native_pair_ac"])
    initial_audit, current_edges = inspect(current, "initial")
    current_audit = initial_audit
    accepted = []
    for record in records:
        previous = record["previous_probe"]
        require(previous == current, "Accepted-path continuity mismatch")
        if not record["accepted"]:
            continue
        chosen = record["chosen_probe"]
        require(record["chosen_passes_native_pair_ac"] is True, "Accepted move lacks local pass")
        gates = [gate for gate in record["native_local_checks"]
                 if gate["proposal_index"] == record["chosen_index"]]
        require(len(gates) == 1, "Missing or ambiguous accepted native gate")
        native_gate(gates[0])
        next_audit, next_edges = inspect(chosen, f"accepted_{len(accepted):02d}")
        move = record["move"]
        check_atomic_geometry(current_edges, next_edges, move)
        difference = value(current_audit["exact_dual_lower_bound"]) - value(next_audit["exact_primal_upper_bound"])
        uphill = value(next_audit["exact_dual_lower_bound"]) - value(current_audit["exact_primal_upper_bound"])
        require(chosen["objective"] - current["objective"] <= 0.5, "Accepted move exceeds uphill allowance")
        accepted.append(dict(iteration=record["iteration"], candidate_path=chosen["candidate_path"],
                             phase1_path=chosen["result_path"], previous_dual_lower=current_audit["exact_dual_lower_bound"],
                             next_primal_upper=next_audit["exact_primal_upper_bound"],
                             guaranteed_objective_decrease=rational(difference),
                             exact_change_classification="STRICT_IMPROVEMENT" if difference > 0 else
                                 "STRICT_UPHILL" if uphill > 0 else "INTERVALS_OVERLAP",
                             guaranteed_uphill_increase=rational(uphill) if uphill > 0 else None,
                             move=move))
        current, current_edges, current_audit = chosen, next_edges, next_audit
    require(len(accepted) == summary["accepted_moves"], "Accepted count mismatch")
    edge_replacements = sum(row["move"]["cycle_size"] for row in accepted)
    require(summary["accepted_edge_replacements"] == edge_replacements, "Accepted edge-replacement count mismatch")
    best_phase_path, best_candidate_path = args.directory / "best_phase1.json", args.directory / "best_candidate.json"
    best_phase, best_candidate = json.loads(best_phase_path.read_bytes()), json.loads(best_candidate_path.read_bytes())
    best_probe = best_candidate["phase1_probe"]
    require(digest(best_phase_path) == best_probe["result_sha256"], "Best phase-I copy differs from original probe")
    require(str(Path(best_probe["result_path"])) in audits, "Best candidate was not on the accepted path")
    best_audit, best_edges = inspect(best_probe, "best")
    path_objectives = [records[0]["previous_probe"]["objective"]] + [
        row["chosen_probe"]["objective"] for row in records if row["accepted"]]
    require(best_probe["objective"] == min(path_objectives), "Best is not the accepted-path numeric minimum")
    full_graph(best_candidate)
    require(set(map(tuple, best_candidate["overlap_edges_outer_zero_based"])) == best_edges,
            "Best candidate wrapper graph differs from original phase-I candidate")
    original_candidate_path = Path(best_phase["candidate_path"])
    require(digest(original_candidate_path) == best_phase["candidate_sha256"], "Best phase-I original candidate mismatch")
    require(summary["best_numeric_objective"] == best_phase["numeric_objective"], "Best summary objective mismatch")
    cert = exact_integer_certificate(json.loads(original_candidate_path.read_bytes()), best_phase,
                                     best_phase["candidate_sha256"])
    cert_path = outdir / "best_exact_binary_dual_certificate.json"
    write_new(cert_path, cert)
    cert_audit_path = outdir / "best_exact_binary_dual_audit.json"
    cert_audit = audit_integer(original_candidate_path, cert_path)
    write_new(cert_audit_path, cert_audit)
    files.update({str(path): digest(path) for path in (best_phase_path, best_candidate_path, cert_path, cert_audit_path)})
    improvement = value(initial_audit["exact_dual_lower_bound"]) - value(best_audit["exact_primal_upper_bound"])
    report = dict(status="INDEPENDENT_ATOMIC_ACCEPTED_PHASE1_INTERVAL_AUDIT_PASS",
                  accepted_moves_checked=len(accepted), distinct_phase1_audits=len(audits),
                  atomic_cycles_independently_checked=len(accepted),
                  accepted_edge_replacements_checked=edge_replacements,
                  intermediate_graphs_required_or_claimed=False,
                  initial_exact_lower_bound=initial_audit["exact_dual_lower_bound"],
                  best_exact_upper_bound=best_audit["exact_primal_upper_bound"],
                  best_exact_lower_bound=best_audit["exact_dual_lower_bound"],
                  certified_total_objective_decrease_at_least=rational(improvement),
                  initial_to_best_strict_improvement_certified=improvement > 0,
                  strict_improvement_moves=sum(row["exact_change_classification"] == "STRICT_IMPROVEMENT" for row in accepted),
                  strict_uphill_moves=sum(row["exact_change_classification"] == "STRICT_UPHILL" for row in accepted),
                  interval_overlap_moves=sum(row["exact_change_classification"] == "INTERVALS_OVERLAP" for row in accepted),
                  native_pass_gates_are_independent_proofs=False,
                  original_best_candidate_path=str(original_candidate_path),
                  best_wrapper_same_edges_as_original_candidate=True,
                  best_integer_certificate_rhs=cert["combined_rhs"],
                  accepted=accepted, files_sha256=files,
                  sources_sha256={str(path): digest(path) for path in
                                  (Path(__file__), Path(__file__).with_name("audit_phase1_kkt.py"),
                                   Path(__file__).with_name("audit_certificate.py"))},
                  elapsed_seconds=time.perf_counter()-started,
                  scope="Exact necessary-relaxation merit intervals and fixed-best-K exclusion. Native pass gates are checked as provenance, not independently reenumerated here. Final pair proof, rejected probes and GPU trace have separate audits. No graph completion or global nonexistence.")
    write_new(args.out, report)
    print(json.dumps({key: val for key, val in report.items() if key not in ("accepted", "files_sha256", "sources_sha256")}))


if __name__ == "__main__":
    main()
