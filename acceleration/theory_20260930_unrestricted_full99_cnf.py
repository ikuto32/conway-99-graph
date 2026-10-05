"""Build the unrestricted scaffold-only full99 CNF; never invoke a solver."""
from datetime import datetime, timezone
from itertools import combinations
import argparse
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

from theory_20260930_eight_full99_cnf import Clauses, Encoder, ResourceCap, counter_controls, digest, package
from theory_20260930_full_srg_validator import controls as graph_controls


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "acceleration/results/20260917_independent_review/root_scaffold.json"
DERIVATION = AUDIT.with_name("ROOT_SCAFFOLD_DERIVATION.md")
SCOPE = ROOT / "acceleration/results/20260930_unrestricted_full99_preflight_v2/scope.json"
PROTOCOL = Path(__file__).with_name("theory_20260930_unrestricted_full99_cnf_spec.md")


def key(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def save(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    cap = ResourceCap()
    cap.check()
    assert digest(AUDIT) == "e96941c2bc050aad65b67a4f22a8968d588ae4dbe3cd7b7f22bfe84972a963a8"
    assert digest(DERIVATION) == "a45fa5c52f3b348e8fb41b347925a363bb79e4d6389f60f760ec85e6cfe8f077"
    inputs = [Path(__file__), PROTOCOL, AUDIT, DERIVATION, SCOPE,
        ROOT / "acceleration/results/20260930_unrestricted_full99_preflight_v2/summary.json",
        ROOT / "acceleration/theory_20260930_eight_full99_cnf.py",
        ROOT / "acceleration/theory_20260930_full_srg_validator.py",
        ROOT / "acceleration/results/20260930_independent_review/eight_full99_cnf/summary.json",
        ROOT / "acceleration/environments/rook-sat/uv.lock",
        ROOT / "acceleration/environments/rook-sat/pyproject.toml"]
    manifest = {"timestamp": datetime.now(timezone.utc).isoformat(),
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "command": [sys.executable, *sys.argv], "cwd": str(ROOT), "python": platform.python_version(),
        "platform": platform.platform(), "uv_version": subprocess.check_output(["uv", "--version"], text=True).strip(),
        "input_hashes": {key(path): digest(path) for path in inputs},
        "question": "Build an unrestricted root-normalized full99 alternative encoding with all outer pairs free, using fully equivalent direct degree/cap thresholds.",
        "scope": "Only189positive root-scaffold edges and their saturated root/inner incidences fixed; all3486outerpairs free; no target automorphism or selected branch.",
        "limits": {"build_seconds": 120, "working_set_bytes": 8 * 1024 ** 3, "solver_calls": 0},
        "dependencies": [{"id": "C-ROOT-SCAFFOLD-NORMALIZATION", "revision": 1, "relation": "normalization"}],
        "status": "CANDIDATE_UNRESTRICTED_ENCODING_BUILD", "solver_imported": False,
        "cardinality_implementation": "Frozen exact AND and bidirectional prefix threshold helpers; no third-party cardinality generator.",
        "old_model_relation": "Alternative encoding of the same unrestricted root representation; no comparative runtime or novelty claim.",
        "random_seed": None, "random_seed_null_reason": "Deterministic enumeration.",
        "numerical_thresholds": None, "numerical_thresholds_null_reason": "Exact Boolean/integer arithmetic."}
    save(args.out / "manifest.json", manifest)
    try:
        old_audit = json.loads(AUDIT.read_text())
        assert old_audit["status"] == "INDEPENDENT_ROOT_SCAFFOLD_DERIVATION_AND_CALIBRATION_PASS"
        for path, expected in old_audit["inputs_sha256"].items():
            assert digest(ROOT / path) == expected
        save(args.out / "counter_controls.json", counter_controls())
        save(args.out / "graph_validator_controls.json", graph_controls())
        cap.check()
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
        preflight = json.loads(SCOPE.read_text())
        assert known == preflight["known_adjacency_full99"]
        assert edge_variables == preflight["edge_variables"]
        assert len(edge_variables) == 3486 and sum(row.count(1) for row in known) == 378
        assert all(known[u][v] == -1 for u, v in combinations(range(15, 99), 2))
        adjacency = [[bool(value) if value >= 0 else None for value in row] for row in known]
        for item in edge_variables:
            adjacency[item["u"]][item["v"]] = adjacency[item["v"]][item["u"]] = item["id"]
        rows, products = [], []
        body_path = args.out / "clauses.body"
        with body_path.open("xb") as body:
            clauses = Clauses(body, cap)
            encoder = Encoder(3486, clauses)
            for u in range(99):
                terms = [reference for reference in adjacency[u] if type(reference) is int]
                constant = sum(reference is True for reference in adjacency[u])
                rows.append(encoder.counter(terms, 14 - constant, True,
                    {"kind": "degree", "vertex": u, "original_bound": 14, "constant": constant}))
            for number, (u, v) in enumerate(combinations(range(99), 2), 1):
                terms, constant = [], 0
                for w in range(99):
                    if w in (u, v):
                        continue
                    a, b = adjacency[u][w], adjacency[v][w]
                    if a is False or b is False:
                        continue
                    if a is True and b is True:
                        constant += 1
                    elif a is True:
                        terms.append(b)
                    elif b is True:
                        terms.append(a)
                    else:
                        first = clauses.count + 1
                        reference = encoder.conjunction(a, b)
                        products.append({"id": reference, "left": a, "right": b, "pair": [u, v],
                            "center": w, "first_clause": first, "clause_count": 3})
                        terms.append(reference)
                edge_value = adjacency[u][v]
                if edge_value is True:
                    constant += 1
                elif type(edge_value) is int:
                    terms.append(edge_value)
                residual = 2 - constant
                assert residual >= 0
                rows.append(encoder.counter(terms, min(residual, len(terms)), False,
                    {"kind": "pair_cap", "pair": [u, v], "original_bound": 2, "constant": constant,
                     "residual_before_trivial_cap_fold": residual}))
                if number % 500 == 0:
                    print(json.dumps({"state": "BUILDING_UNRESTRICTED_CAPS", "pairs": number,
                        "variables": encoder.top, "clauses": clauses.count}), flush=True)
                    cap.check()
        cnf = args.out / "instance.cnf"
        with cnf.open("xb") as destination, body_path.open("rb") as source:
            destination.write(f"p cnf {encoder.top} {clauses.count}\n".encode("ascii"))
            for chunk in iter(lambda: source.read(1048576), b""):
                destination.write(chunk)
                cap.check()
        model = {"schema": "UNRESTRICTED_FULL99_EXACT_PREFIX_CNF_V1",
            "scope_path": key(SCOPE), "scope_sha256": digest(SCOPE),
            "normalization_dependency": {"id": "C-ROOT-SCAFFOLD-NORMALIZATION", "revision": 1},
            "normalization_audit": key(AUDIT), "normalization_audit_sha256": digest(AUDIT),
            "known_adjacency_full99": known, "outer_labels": labels, "fixed_scaffold_edges": 189,
            "fixed_K_edges": [], "fixed_outer_nonedges": [],
            "unknown_edges_outer": [[u - 15, v - 15] for u, v in combinations(range(15, 99), 2)],
            "edge_variables": edge_variables, "product_variables": products, "counter_rows": rows,
            "variables": encoder.top, "clauses": clauses.count, "degree_rows": 99, "pair_cap_rows": 4851,
            "prefix_reference_format": "JSON booleans are constants; positive integers are SAT variable IDs.",
            "gate_clause_order": {"and": ["a -z", "b -z", "-a -b z"], "or": ["-a z", "-b z", "a b -z"],
                "a_or_b_and_c": ["-a z", "-b -c z", "a b -z", "a c -z"]},
            "clauses_constant_folded": True, "row_order": "99 degrees first; then lexicographic full99 unordered pairs; product centers ascending before each pair counter.",
            "branch_units": [], "target_automorphism_assumed": False}
        model_path = args.out / "model.json"
        save(model_path, model)
        cap.check()
        packages = [package(path, cap) for path in (cnf, model_path)]
        save(args.out / "artifact_packages.json", {"packages": packages,
            "retrieval": "Concatenate ordered gzip parts byte-for-byte, verify compressed SHA256, then decompress and verify raw SHA256."})
        cap.check()
        for path, expected in manifest["input_hashes"].items():
            assert digest(ROOT / path) == expected
        actual = {"variables": encoder.top, "clauses": clauses.count, "products": len(products)}
        expected = {"variables": 1186500, "clauses": 4136454, "products": 285852}
        files = [p for p in args.out.iterdir() if p.is_file() and p.name != "clauses.body"]
        save(args.out / "summary.json", {"timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "CANDIDATE_UNRESTRICTED_ENCODING_PENDING_COMPLETE_GATE", "complete": True,
            **actual, "edge_variables": 3486, "prefix_variables": encoder.top - 3486 - len(products),
            "degree_rows": 99, "pair_cap_rows": 4851, "preflight_expected": expected,
            "preflight_counts_match": actual == expected, "fixed_outer_edges": 0, "fixed_outer_nonedges": 0,
            "solver_calls": 0, "elapsed_seconds": time.monotonic() - cap.start,
            "peak_working_set_bytes": cap.peak_bytes, "resource_samples": cap.samples,
            "outputs": {p.name: {"sha256": digest(p), "bytes": p.stat().st_size} for p in files},
            "target_resolution": False, "new_complete_coverage_and_encoding_review_pending": True,
            "limitations": ["Alternative encoding only; no solver result or mathematical resolution.",
                "Shared frozen helpers do not replace a new complete unrestricted artifact audit.",
                "Prior conditional120K claims remain unchanged and are not broadened."]})
        print(json.dumps({"status": "CANDIDATE_UNRESTRICTED_ENCODING_PENDING_COMPLETE_GATE", **actual,
                          "seconds": time.monotonic() - cap.start}), flush=True)
    except BaseException as error:
        save(args.out / "failure.json", {"timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "INCOMPLETE_UNRESTRICTED_BUILD", "type": type(error).__name__, "message": str(error),
            "elapsed_seconds": time.monotonic() - cap.start, "peak_working_set_bytes": cap.peak_bytes,
            "solver_calls": 0})
        raise


if __name__ == "__main__":
    main()
