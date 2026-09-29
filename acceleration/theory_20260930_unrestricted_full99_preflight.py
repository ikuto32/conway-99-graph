"""No-solver unrestricted full99 scope and exact threshold-size preflight."""
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
import argparse
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

from theory_20260930_eight_full99_cnf import Encoder, Clauses


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "acceleration/results/20260917_independent_review/root_scaffold.json"
DERIVATION = AUDIT.with_name("ROOT_SCAFFOLD_DERIVATION.md")
EXPECTED_AUDIT = "e96941c2bc050aad65b67a4f22a8968d588ae4dbe3cd7b7f22bfe84972a963a8"
EXPECTED_DERIVATION = "a45fa5c52f3b348e8fb41b347925a363bb79e4d6389f60f760ec85e6cfe8f077"


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def key(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def save(path, obj):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(obj, stream, indent=2)
        stream.write("\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    gitlink = subprocess.check_output(["git", "ls-tree", commit, "external_conway99_research"], text=True).strip()
    external_commit = gitlink.split()[2]
    assert external_commit == "85e705cc6c2a14d123120c93a847e30aaab1789e"
    paths = [Path(__file__), AUDIT, DERIVATION,
        ROOT / "acceleration/theory_20260930_eight_full99_cnf.py",
        ROOT / "acceleration/results/20260930_independent_review/eight_full99_cnf/summary.json",
        ROOT / "scratch_general_exact_sat.py", ROOT / "scratch_general_exact.cnf",
        ROOT / "scratch_general_exact_build.json", ROOT / "scratch_general_exact_portfolio.json",
        ROOT / "external_conway99_research/CLAIMS.yaml",
        ROOT / "external_conway99_research/attempts/2026-07-22-compact-sat-encoding.md",
        ROOT / "external_conway99_research/verification/2026-07-22-first-wave-audit.md",
        ROOT / "uv.lock"]
    save(args.out / "manifest.json", {"timestamp": datetime.now(timezone.utc).isoformat(),
        "source_commit": commit, "command": [sys.executable, *sys.argv], "cwd": str(ROOT),
        "python": platform.python_version(), "input_hashes": {key(p): digest(p) for p in paths},
        "question": "Assess unrestricted scaffold-only full99 exact-degree/cap threshold encoding without repeating historical branch solves.",
        "limits": {"wall_seconds": 120, "solver_calls": 0, "full_cnf_builds": 0},
        "selection": "All3486outerpairs free; noKfixed values, no outer absences, no branch/symmetry units.",
        "shared_code": "Counts instantiate only frozen producer threshold templates; this preflight is not an independent encoding audit.",
        "status": "CANDIDATE_ENGINEERING_PREFLIGHT"})
    assert digest(AUDIT) == EXPECTED_AUDIT and digest(DERIVATION) == EXPECTED_DERIVATION
    normalization = json.loads(AUDIT.read_text())
    assert normalization["status"] == "INDEPENDENT_ROOT_SCAFFOLD_DERIVATION_AND_CALIBRATION_PASS"
    assert normalization["claim_id"] == "C-ROOT-SCAFFOLD-NORMALIZATION" and normalization["claim_revision"] == 1
    for name, expected in normalization["inputs_sha256"].items():
        assert digest(ROOT / name) == expected, name
    ledger_bytes = subprocess.check_output(["git", "show", commit + ":CLAIMS.yaml"])
    ledger_text = ledger_bytes.decode("utf-8")
    needle = "- id: C-ROOT-SCAFFOLD-NORMALIZATION\n"
    claim = needle + ledger_text.split(needle, 1)[1].split("\n- id:", 1)[0]
    assert "  status: VERIFIED\n" in claim and "  review_state: CLEAR\n" in claim
    with (args.out / "pinned_normalization_claim.yaml").open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(claim + "\n")
    labels = [(2 * a + s, 2 * b + t) for a, b in combinations(range(7), 2) for s in (0, 1) for t in (0, 1)]
    known = [[0] * 99 for _ in range(99)]
    def edge(u, v, value):
        known[u][v] = known[v][u] = value
    for inner in range(1, 15):
        edge(0, inner, 1)
    for inner in range(1, 15, 2):
        edge(inner, inner + 1, 1)
    for outer, label in enumerate(labels, 15):
        for symbol in label:
            edge(outer, symbol + 1, 1)
    edge_variables = []
    for variable, (u, v) in enumerate(combinations(range(15, 99), 2), 1):
        edge(u, v, -1)
        edge_variables.append({"id": variable, "u": u, "v": v})
    assert len(edge_variables) == 3486
    assert sum(row.count(1) for row in known) == 378
    assert all(known[u][v] == -1 for u, v in combinations(range(15, 99), 2))
    degree_histogram, cap_histogram = Counter(), Counter()
    degrees, caps = [], []
    total_products = 0
    for u in range(99):
        count = known[u].count(-1)
        constant = known[u].count(1)
        bound = 14 - constant
        assert 0 <= bound <= count
        degree_histogram[count, bound] += 1
        degrees.append({"vertex": u, "unknown_terms": count, "constant": constant, "bound": bound})
    for u, v in combinations(range(99), 2):
        constant = int(known[u][v] == 1)
        linear = int(known[u][v] == -1)
        products_here = 0
        for w in range(99):
            a, b = known[u][w], known[v][w]
            if a == 0 or b == 0:
                continue
            if a == b == 1:
                constant += 1
            elif a == b == -1:
                products_here += 1
            else:
                linear += 1
        count = linear + products_here
        residual = 2 - constant
        assert residual >= 0
        bound = min(residual, count)
        cap_histogram[count, bound] += 1
        total_products += products_here
        caps.append({"pair": [u, v], "constant": constant, "linear_terms": linear,
                     "product_terms": products_here, "counter_terms": count, "bound": bound})
    template_records = []
    total_prefix_variables = total_counter_clauses = 0
    for equality, histogram in ((True, degree_histogram), (False, cap_histogram)):
        for (n, bound), multiplicity in sorted(histogram.items()):
            memory = Clauses()
            encoding = Encoder(n, memory)
            encoding.counter(list(range(1, n + 1)), bound, equality, {})
            auxiliary = encoding.top - n
            total_prefix_variables += auxiliary * multiplicity
            total_counter_clauses += memory.count * multiplicity
            template_records.append({"equality": equality, "terms": n, "bound": bound, "rows": multiplicity,
                "prefix_variables_per_row": auxiliary, "clauses_per_row": memory.count})
    assert total_products == 285852
    count_variables = 3486 + total_products + total_prefix_variables
    count_clauses = 3 * total_products + total_counter_clauses
    save(args.out / "scope.json", {"schema": "UNRESTRICTED_ROOT_SCAFFOLD_FULL99_PREFLIGHT_V1",
        "normalization_dependency": {"id": "C-ROOT-SCAFFOLD-NORMALIZATION", "revision": 1, "relation": "normalization"},
        "known_adjacency_full99": known, "outer_labels": labels, "edge_variables": edge_variables,
        "fixed_positive_edges": 189, "fixed_outer_edges": 0, "fixed_outer_nonedges": 0,
        "free_outer_pairs": 3486, "automorphism_assumed": False,
        "branch_units": [], "extra_graph_constraints": [],
        "new_unrestricted_encoding_audit_required": True})
    save(args.out / "constraint_census.json", {"degrees": degrees, "pair_caps": caps, "templates": template_records})
    old = json.loads((ROOT / "scratch_general_exact_build.json").read_text())
    old_run = json.loads((ROOT / "scratch_general_exact_portfolio.json").read_text())
    statuses = Counter(row["status"] for row in old_run["records"])
    assert time.monotonic() - start < 120
    save(args.out / "summary.json", {"timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "CANDIDATE_UNRESTRICTED_SCOPE_AND_SIZE_PREFLIGHT", "source_commit": commit,
        "normalization_claim": {"id": "C-ROOT-SCAFFOLD-NORMALIZATION", "revision": 1,
             "recorded_status": "VERIFIED", "recorded_review_state": "CLEAR",
             "historical_artifacts_hash_rechecked": True, "historical_proof_read": True,
             "fresh_independent_verification_claimed": False},
        "unrestricted_scope": {"fixed_scaffold_edges": 189, "free_outer_pairs": 3486,
            "fixed_outer_edges": 0, "fixed_outer_nonedges": 0, "same_support_outer_pairs_included": 126,
            "branch_or_symmetry_units_added": 0},
        "prospective_encoding": {"primary_variables": 3486, "product_variables": total_products,
            "prefix_variables": total_prefix_variables, "total_variables": count_variables,
            "total_clauses": count_clauses, "degree_rows": 99, "pair_cap_rows": 4851},
        "old_local_repository_base": {"path": "scratch_general_exact.cnf", "variables": old["variables"],
            "clauses": old["clauses"], "bytes": (ROOT / "scratch_general_exact.cnf").stat().st_size,
            "sha256": digest(ROOT / "scratch_general_exact.cnf"),
            "difference": "Old BP/profile equalities and one-way wedge plus sequential counters; proposed direct all99degree/all4851cap model uses fully bidirectional custom prefix gates, no selected branch."},
        "historical_portfolio_only": {"path": "scratch_general_exact_portfolio.json", "recorded_statuses": dict(statuses),
            "recorded_per_parallel_branch_seconds": old_run["wall_limit_seconds_per_parallel_branch"],
            "replayed_now": False, "unsat_proof_available_in_this_record": False,
            "mathematical_exclusion_claimed": False},
        "archive_references": [{"repository": "https://github.com/YesterdaysLemon/conway-99-research",
            "commit": external_commit, "path": "CLAIMS.yaml", "original_claim_id": identifier,
            "fresh_verification_claimed": False} for identifier in ("C-ROOT-001", "C-ENCODING-001")],
        "coverage_status": "Existing every-root normalization has a VERIFIED/CLEAR current claim. A new independent exact-scaffold/encoding equivalence and coverage audit is still required before an unrestricted SAT/UNSAT inference from a new CNF.",
        "solver_calls": 0, "research_cnf_built": False, "elapsed_seconds": time.monotonic() - start,
        "outputs_sha256": {p.name: digest(p) for p in args.out.iterdir() if p.is_file()},
        "target_resolution": "UNKNOWN", "overall_search_coverage": "UNKNOWN; no validated denominator for explored completions."})
    print(json.dumps({"prospective_variables": count_variables, "prospective_clauses": count_clauses,
                      "products": total_products, "prefix": total_prefix_variables,
                      "old_portfolio_recorded_statuses": dict(statuses), "solver_calls": 0}))


if __name__ == "__main__":
    main()
