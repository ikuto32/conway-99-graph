"""Bind independent local-domain and exact global-linear evidence to the same K."""
import argparse
from hashlib import sha256
import json
from pathlib import Path

from audit_certificate import require


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    require(not args.out.exists(), "Preserve previous evidence binding")
    phase_path = args.directory / "accepted_phase1_intervals_audit.json"
    pair_path = args.directory / "best_pair_independent_audit.json"
    phase, pair = json.loads(phase_path.read_bytes()), json.loads(pair_path.read_bytes())
    require(phase["status"] == "INDEPENDENT_ATOMIC_ACCEPTED_PHASE1_INTERVAL_AUDIT_PASS", "Phase audit incomplete")
    require(pair["status"] == "INDEPENDENT_EXACT_PAIR_DOMAIN_AUDIT_PASS", "Pair audit incomplete")
    require(pair["propagation_status"] == "ARC_CONSISTENT_NONEMPTY" and pair["complete_used_domains_verified"],
            "No independently verified pair closure")
    require(sorted(row["outer_vertex"] for row in pair["independently_reenumerated_domains"]) == list(range(84)),
            "Not all complete domains were checked")
    files = {str(phase_path): digest(phase_path), str(pair_path): digest(pair_path)}
    for bindings in (phase["files_sha256"], phase["sources_sha256"], pair["inputs_sha256"]):
        for name, expected in bindings.items():
            require(digest(Path(name)) == expected, "Bound evidence changed: " + name)
    candidate_path = Path(phase["original_best_candidate_path"])
    candidate_sha = digest(candidate_path)
    require(pair["inputs_sha256"].get(str(candidate_path)) == candidate_sha,
            "Local and global proofs refer to different original candidates")
    require(int(phase["best_exact_lower_bound"]["numerator"]) > 0, "Global linear lower bound is not positive")
    require(phase["best_integer_certificate_rhs"] < 0, "No exact integer contradiction")
    detail_dir = phase_path.parent / (phase_path.stem + "_details")
    cert_path = detail_dir / "best_exact_binary_dual_certificate.json"
    cert_audit_path = detail_dir / "best_exact_binary_dual_audit.json"
    cert, cert_audit = json.loads(cert_path.read_bytes()), json.loads(cert_audit_path.read_bytes())
    require(cert["candidate_sha256"] == candidate_sha and cert["combined_rhs"] == phase["best_integer_certificate_rhs"],
            "Integer certificate candidate/RHS mismatch")
    require(cert_audit["status"] == "INDEPENDENT_INTEGER_FARKAS_AUDIT_PASS" and
            cert_audit["inputs_sha256"].get(str(candidate_path)) == candidate_sha and
            cert_audit["inputs_sha256"].get(str(cert_path)) == digest(cert_path), "Integer certificate audit binding mismatch")
    files.update({str(path): digest(path) for path in (candidate_path, cert_path, cert_audit_path)})
    report = dict(status="INDEPENDENT_ATOMIC_BEST_LOCAL_PASS_GLOBAL_OBSTRUCTION_BOUND",
                  candidate_path=str(candidate_path), candidate_sha256=candidate_sha,
                  all84_complete_local_star_domains_independently_checked=True,
                  exact_pair_arc_consistency="NONEMPTY_FINAL_CLOSURE_INDEPENDENTLY_CHECKED",
                  original_domain_choices=sum(row["domain_size"] for row in pair["independently_reenumerated_domains"]),
                  pair_deletion_events_replayed=pair["events_verified"],
                  best_exact_lower_bound=phase["best_exact_lower_bound"], best_exact_upper_bound=phase["best_exact_upper_bound"],
                  initial_to_best_strict_improvement_certified=phase["initial_to_best_strict_improvement_certified"],
                  best_integer_certificate_rhs=cert["combined_rhs"], files_sha256=files,
                  auditor_sha256=digest(Path(__file__)),
                  scope="One and the same fixed K passes independently complete local pair arc consistency but has no necessary linear completion. This is a method countercontrol, not a graph or global nonexistence theorem.")
    with args.out.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
