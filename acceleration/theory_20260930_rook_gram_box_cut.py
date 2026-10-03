"""Candidate shorter exact Gram nogood by maximizing over freed Boolean edges.

The input certificate must already have an independent Gram/support audit.
This producer never approves its own new cut; a new checking path is required.
"""
from datetime import datetime, timezone
from hashlib import sha256
import argparse
import json
from pathlib import Path
import platform
import subprocess
import sys


def digest(p):
    return sha256(Path(p).read_bytes()).hexdigest()


def save(p, value):
    with Path(p).open("x", encoding="utf-8", newline="\n") as f:
        json.dump(value, f, indent=2)
        f.write("\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--certificate", type=Path, required=True)
    parser.add_argument("--prior-audit", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    save(args.out / "manifest.json", {"timestamp": datetime.now(timezone.utc).isoformat(),
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "command": [sys.executable, *sys.argv], "cwd": str(Path.cwd()), "python": platform.python_version(),
        "input_hashes": {p.as_posix(): digest(p) for p in (Path(__file__), args.certificate, args.prior_audit, Path("uv.lock"))},
        "question": "Can a prior exact negative Gram quadratic remain negative while some supporting Boolean edge values are free?",
        "scope": "One fixed central-factor model and one independently checked Gram vector. New clause must receive a fresh independent audit before use.",
        "selection_rule": "For each nonzero variable coefficient c and current value a, freeing that edge raises the box maximum by max(0,c*(1-2a)). Free ascending gains, breaking ties by variable ID, while the new maximum stays strictly negative.",
        "success_criteria": "Exact global Boolean-box upper bound is negative and the new clause has no more literals than its parent support clause.",
        "falsification_criteria": "Any nonnegative upper bound or prior-audit/hash mismatch rejects the proposed cut.",
        "resource_limits": "One finite certificate, at most780variable coefficients; no solver or floating arithmetic.",
        "status": "CANDIDATE", "independent_review_pending": True, "sat_launch_authorized_by_this_run": False})
    certificate = json.loads(args.certificate.read_text())
    audit = json.loads(args.prior_audit.read_text())
    assert audit["status"] == "INDEPENDENT_TARGET_GRAM_NOGOOD_PASS"
    assert audit["certificate_sha256"] == digest(args.certificate)
    assert audit["verified_clause"] == certificate["nogood_clause"]
    constant = certificate["linear_quadratic_constant"]
    rows = certificate["nonzero_variable_coefficients"]
    current = constant + sum(row["coefficient"] * row["value_in_rejected_graph"] for row in rows)
    assert current == certificate["quadratic_value"] < 0
    decisions = []
    for row in rows:
        gain = max(0, row["coefficient"] * (1 - 2 * row["value_in_rejected_graph"]))
        decisions.append({**row, "maximum_gain_if_freed": gain})
    decisions.sort(key=lambda row: (row["maximum_gain_if_freed"], row["variable"]))
    upper = current
    for row in decisions:
        free = upper + row["maximum_gain_if_freed"] < 0
        row["free"] = free
        if free:
            upper += row["maximum_gain_if_freed"]
    decisions.sort(key=lambda row: row["variable"])
    reconstructed = constant + sum(max(0, row["coefficient"]) if row["free"] else row["coefficient"] * row["value_in_rejected_graph"] for row in decisions)
    assert upper == reconstructed < 0
    fixed = [row for row in decisions if not row["free"]]
    clause = [-row["variable"] if row["value_in_rejected_graph"] else row["variable"] for row in fixed]
    assert len(clause) <= len(certificate["nogood_clause"])
    result = {"status": "CANDIDATE", "independent_review_pending": True, "cut_kind": "GRAM_BOOLEAN_BOX_MAXIMUM",
        "parent_certificate": args.certificate.as_posix(), "parent_certificate_sha256": digest(args.certificate),
        "parent_independent_audit": args.prior_audit.as_posix(), "parent_independent_audit_sha256": digest(args.prior_audit),
        "graph_sha256": certificate["graph_sha256"], "encoding_model_sha256": certificate["encoding_model_sha256"],
        "base_cnf_sha256": certificate["base_cnf_sha256"], "matrix": certificate["matrix"],
        "integer_negative_vector": certificate["integer_negative_vector"], "quadratic_value_at_parent_graph": current,
        "linear_quadratic_constant": constant, "variable_coefficients_and_free_choices": decisions,
        "global_boolean_box_upper_bound": upper, "nogood_clause": clause,
        "parent_clause_length": len(certificate["nogood_clause"]), "nogood_clause_length": len(clause),
        "soundness": "Fixing only the listed clause variables to their parent values leaves the Gram quadratic at most the displayed negative bound over every assignment of all other Boolean edges. Hence a target extension must flip at least one listed value.",
        "scope": "A necessary cut for extensions of the fixed central star; no full target or family exclusion is claimed."}
    save(args.out / "certificate.json", result)
    (args.out / "nogood.clause").write_text(" ".join(map(str, clause)) + " 0\n", encoding="ascii", newline="\n")
    print(json.dumps({"parent_literals": result["parent_clause_length"], "new_literals": len(clause),
                      "exact_box_upper_bound": upper, "certificate_sha256": digest(args.out / "certificate.json")}))


if __name__ == "__main__":
    main()
