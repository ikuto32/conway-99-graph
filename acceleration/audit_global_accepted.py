"""Independently certify phase-I intervals along an accepted overlap-search path."""
import argparse
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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    started = time.perf_counter()
    require(not args.out.exists(), "Preserve previous accepted-path audit")
    summary_path = args.directory / "summary.json"
    summary = json.loads(summary_path.read_bytes())
    require(summary["status"] == "BOUNDED_GLOBAL_DEFECT_SEARCH_FINISHED", "Search not finalized")
    records = summary["records"]
    require(records, "Empty search trace")
    outdir = args.out.parent / (args.out.stem + "_details")
    outdir.mkdir(parents=True, exist_ok=False)
    files = {str(summary_path): digest(summary_path)}
    audits, candidate_edges = {}, {}

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
    initial_audit, current_edges = inspect(current, "initial")
    current_audit = initial_audit
    accepted = []
    for record in records:
        previous = record["previous_probe"]
        require(previous == current, "Accepted-path continuity mismatch")
        if not record["accepted"]:
            continue
        chosen = record["chosen_probe"]
        next_audit, next_edges = inspect(chosen, f"accepted_{len(accepted):02d}")
        removed, added = set(map(tuple, record["removed"])), set(map(tuple, record["added"]))
        require(removed <= current_edges and not added & current_edges, "Invalid accepted trade")
        require(current_edges - removed | added == next_edges, "Trade does not produce chosen graph")
        difference = value(current_audit["exact_dual_lower_bound"]) - value(next_audit["exact_primal_upper_bound"])
        require(difference > 0, "Accepted move has no certified strict phase-I improvement")
        accepted.append(dict(iteration=record["iteration"], candidate_path=chosen["candidate_path"],
                             phase1_path=chosen["result_path"], previous_dual_lower=current_audit["exact_dual_lower_bound"],
                             next_primal_upper=next_audit["exact_primal_upper_bound"],
                             guaranteed_objective_decrease=rational(difference),
                             removed=record["removed"], added=record["added"]))
        current, current_edges, current_audit = chosen, next_edges, next_audit
    require(len(accepted) == summary["accepted_moves"], "Accepted count mismatch")
    best_phase_path, best_candidate_path = args.directory / "best_phase1.json", args.directory / "best_candidate.json"
    require(digest(best_phase_path) == current["result_sha256"], "Best phase-I copy differs from final accepted result")
    best_phase, best_candidate = json.loads(best_phase_path.read_bytes()), json.loads(best_candidate_path.read_bytes())
    full_graph(best_candidate)
    require(set(map(tuple, best_candidate["overlap_edges_outer_zero_based"])) == current_edges,
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
    improvement = value(initial_audit["exact_dual_lower_bound"]) - value(current_audit["exact_primal_upper_bound"])
    report = dict(status="INDEPENDENT_ACCEPTED_PHASE1_PATH_EXACT_IMPROVEMENT_AUDIT_PASS",
                  accepted_moves_checked=len(accepted), distinct_phase1_audits=len(audits),
                  initial_exact_lower_bound=initial_audit["exact_dual_lower_bound"],
                  final_exact_upper_bound=current_audit["exact_primal_upper_bound"],
                  final_exact_lower_bound=current_audit["exact_dual_lower_bound"],
                  certified_total_objective_decrease_at_least=rational(improvement),
                  every_accepted_move_strictly_improves_exact_optimal_merit=True,
                  original_best_candidate_path=str(original_candidate_path),
                  best_wrapper_same_edges_as_original_candidate=True,
                  best_integer_certificate_rhs=cert["combined_rhs"],
                  accepted=accepted, files_sha256=files,
                  sources_sha256={str(path): digest(path) for path in
                                  (Path(__file__), Path(__file__).with_name("audit_phase1_kkt.py"),
                                   Path(__file__).with_name("audit_certificate.py"))},
                  elapsed_seconds=time.perf_counter()-started,
                  scope="Exact necessary-relaxation merit improvement and exact fixed-best-K exclusion. Rejected probes/GPU scoring are audited separately. No graph completion or global nonexistence.")
    write_new(args.out, report)
    print(json.dumps({key: val for key, val in report.items() if key not in ("accepted", "files_sha256", "sources_sha256")}))


if __name__ == "__main__":
    main()
