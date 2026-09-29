"""Bounded greedy support reduction and candidate exact Gram-support nogood."""
from datetime import datetime, timezone
import argparse
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

from theory_20260930_rook_gram_falsifier import digest, exact_test, load_graph, quadratic, save


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--graph", type=Path, required=True)
    parser.add_argument("--certificate", type=Path, required=True)
    parser.add_argument("--encoding-model", type=Path, required=True)
    parser.add_argument("--cnf", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    inputs = [Path(__file__), Path("acceleration/theory_20260930_rook_gram_falsifier.py"), args.graph,
              args.certificate, args.encoding_model, args.cnf, Path("uv.lock")]
    save(args.out / "manifest.json", {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "command": [sys.executable, *sys.argv], "cwd": str(Path.cwd()), "python": platform.python_version(),
        "input_hashes": {p.as_posix(): digest(p) for p in inputs},
        "question": "Can deletion of principal Gram rows shrink the exact negative-direction support and the corresponding sound assignment-blocking clause?",
        "scope": "One independently decoded local59 graph and the fixed780-edge model. A resulting nogood is necessary for any target extension, not a proof of family nonexistence.",
        "selection_rule": "Try support vertices in descending full59 index, so right-cell vertices are attempted first. Keep a deletion only when fresh exact rational elimination proves the remaining principal matrix indefinite. Repeat up to three passes or until no deletion.",
        "resource_limits": {"wall_seconds": 120, "passes": 3},
        "success_criteria": "Emit an explicit integer vector with directly computed negative v^T(27I-9A+J)v, then block only current values of encoding variables with nonzero quadratic coefficients.",
        "falsification_criteria": "Reject any nonnegative final quadratic, malformed mapping, or mismatch between the full quadratic and reconstructed coefficient sum.",
        "status": "CANDIDATE", "independent_review_pending": True,
        "no_sat_launch": True,
    })
    graph = load_graph(args.graph)
    gram = [[27 * int(u == v) - 9 * graph[u][v] + 1 for v in range(59)] for u in range(59)]
    original = next(row["result"] for row in json.loads(args.certificate.read_text())["tests"] if row["matrix"] == "27I-9A+J")
    assert quadratic(gram, original["integer_negative_vector"]) == original["quadratic_value"] < 0
    support = original["support"].copy()
    history = []
    start = time.monotonic()
    stopped_by_cap = False
    for pass_index in range(3):
        changed = False
        for vertex in sorted(support, reverse=True):
            if time.monotonic() - start >= 120:
                stopped_by_cap = True
                break
            candidate = [v for v in support if v != vertex]
            submatrix = [[gram[u][v] for v in candidate] for u in candidate]
            result = exact_test(submatrix, len(candidate))
            record = {"pass": pass_index + 1, "attempted_deletion": vertex,
                      "before_size": len(support), "remaining_psd": result["psd"], "deletion_retained": not result["psd"]}
            if not result["psd"]:
                support = candidate
                changed = True
                record["negative_value_on_remaining"] = result["quadratic_value"]
            history.append(record)
        if stopped_by_cap or not changed:
            break
    result = exact_test([[gram[u][v] for v in support] for u in support], len(support))
    assert not result["psd"]
    vector = [0] * 59
    for u, coefficient in zip(support, result["integer_negative_vector"]):
        vector[u] = coefficient
    value = quadratic(gram, vector)
    assert value == result["quadratic_value"] < 0
    model = json.loads(args.encoding_model.read_text())
    variable_edges = {(entry["u"] + 9, entry["v"] + 9): entry["id"] for entry in model["edge_variables"]}
    coefficients = []
    clause = []
    constant = 27 * sum(x * x for x in vector) + sum(vector) ** 2
    for u in range(59):
        for v in range(u + 1, 59):
            coefficient = -18 * vector[u] * vector[v]
            variable = variable_edges.get((u, v))
            if variable is None:
                constant += coefficient * graph[u][v]
            elif coefficient:
                coefficients.append({"variable": variable, "edge_full59": [u, v],
                                     "coefficient": coefficient, "value_in_rejected_graph": graph[u][v]})
                clause.append(-variable if graph[u][v] else variable)
    assert constant + sum(row["coefficient"] * row["value_in_rejected_graph"] for row in coefficients) == value
    assert len(clause) == len(set(clause))
    certificate = {"status": "CANDIDATE", "independent_review_pending": True,
        "graph_sha256": digest(args.graph), "encoding_model_sha256": digest(args.encoding_model),
        "base_cnf_sha256": digest(args.cnf), "matrix": "27I-9A+J", "integer_negative_vector": vector,
        "support": [i for i, x in enumerate(vector) if x], "quadratic_value": value,
        "linear_quadratic_constant": constant, "nonzero_variable_coefficients": coefficients,
        "nogood_clause": clause, "nogood_clause_length": len(clause),
        "soundness": "Any assignment preserving every recorded variable value leaves this integer quadratic unchanged and negative. A true target principal Gram must be PSD, so at least one of these values must flip.",
        "scope": "Necessary cut for extensions of the exact central star; no assumption on graph automorphism, no target-level resolution."}
    save(args.out / "certificate.json", certificate)
    save(args.out / "deletion_history.json", history)
    (args.out / "nogood.clause").write_text(" ".join(map(str, clause)) + " 0\n", encoding="ascii", newline="\n")
    summary = {"timestamp": datetime.now(timezone.utc).isoformat(), "status": "CANDIDATE", "independent_review_pending": True,
        "original_support_size": len(original["support"]), "final_support_size": len(certificate["support"]),
        "deletion_attempts": len(history), "retained_deletions": sum(row["deletion_retained"] for row in history),
        "quadratic_value": value, "nogood_clause_length": len(clause),
        "elapsed_seconds": time.monotonic() - start, "wall_cap_hit": stopped_by_cap,
        "certificate_sha256": digest(args.out / "certificate.json"), "target_exclusion": False, "sat_launched": False}
    save(args.out / "summary.json", summary)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
