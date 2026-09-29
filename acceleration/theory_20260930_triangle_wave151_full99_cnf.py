"""Build one conditional triangle-root full99 exact-equality CNF; no solver."""
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
import argparse
import json
import platform
import shutil
import subprocess
import sys
import time

from theory_20260930_eight_full99_cnf import Clauses, Encoder, ResourceCap, counter_controls, digest, package, save
from theory_20260930_full_srg_validator import controls as graph_controls

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "acceleration/results/20260930_triangle_partial99/wave151.json"
INPUT_SHA = "688b0255760a57a4cdd39e1ea471a784e3771a13c6fd3a6eb8b3615a7c43f063"
SPEC = Path(__file__).with_name("theory_20260930_triangle_wave151_full99_cnf_spec.md")
ARCHIVE = ROOT / "external_conway99_research"
ARCHIVE_PIN = "85e705cc6c2a14d123120c93a847e30aaab1789e"


def key(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    cap = ResourceCap()
    cap.check()
    if digest(INPUT) != INPUT_SHA:
        raise ValueError("frozen propagated input changed")
    if subprocess.check_output(["git", "-C", str(ARCHIVE), "rev-parse", "HEAD"], text=True).strip() != ARCHIVE_PIN:
        raise ValueError("archive pin changed")
    paths = [Path(__file__), SPEC, INPUT, ROOT / "uv.lock", ROOT / "pyproject.toml",
        ROOT / "acceleration/theory_20260930_eight_full99_cnf.py", ROOT / "acceleration/theory_20260930_full_srg_validator.py",
        ROOT / "acceleration/theory_20260930_triangle_partial99.py", ROOT / "acceleration/theory_20260930_triangle_partial99_spec.md",
        ROOT / "acceleration/results/20260930_triangle_factor_preflight/wave151.json",
        ROOT / "acceleration/results/20260930_triangle_cnf_census/summary.json",
        ARCHIVE / "attempts/wave149-terwilliger-triple/exact-results.json",
        ARCHIVE / "attempts/wave151-triangle-root-factor/exact-results.json"]
    manifest = {"timestamp": datetime.now(timezone.utc).isoformat(),
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "command": [sys.executable, *sys.argv], "cwd": str(ROOT), "python": platform.python_version(),
        "platform": platform.platform(), "uv_version": subprocess.check_output(["uv", "--version"], text=True).strip(),
        "inputs_sha256": {key(path): digest(path) for path in paths}, "archive_repository": "https://github.com/YesterdaysLemon/conway-99-research",
        "archive_commit": ARCHIVE_PIN, "question": "Complete the displayed Wave151 fixed triangle-root/Q1 to a full99target, including residualD.",
        "scope": "One fixed labelled local scaffold/incidence factor only, not universal target coverage.",
        "selection": "The remaining displayed Wave151 Q1 family; separate from the already-run Wave154 family, with no general coverage claim.",
        "limits": {"build_seconds": 120, "working_set_bytes": 8 * 1024 ** 3, "solver_calls": 0},
        "status": "CANDIDATE_CONDITIONAL_ENCODING_BUILD", "independent_propagation_gate_pending": True,
        "independent_encoding_gate_pending": True, "solver_imported": False,
        "target_automorphism_assumed": False, "random_seed": None, "random_seed_null_reason": "Deterministic exact enumeration.",
        "numerical_thresholds": None, "numerical_thresholds_null_reason": "Only Boolean/integer operations.",
        "shared_components": ["Frozen exact AND/threshold producer and calibrated genericSRG validator; not independent review of this model."]}
    save(args.out / "manifest.json", manifest)
    try:
        save(args.out / "counter_controls.json", counter_controls())
        save(args.out / "graph_validator_controls.json", graph_controls())
        raw = json.loads(INPUT.read_bytes())
        assert raw["case"] == "wave151" and raw["status"] == "FIXED_POINT_UNKNOWN" and len(raw["steps"]) == 562
        known = raw["final_adjacency"]
        assert len(known) == 99 and all(len(row) == 99 for row in known)
        assert all(known[u][u] == 0 for u in range(99))
        assert all(known[u][v] == known[v][u] and type(known[u][v]) is int and known[u][v] in (-1, 0, 1)
                   for u in range(99) for v in range(99))
        free = [(u, v) for u, v in combinations(range(99), 2) if known[u][v] == -1]
        assert len(free) == 1928
        edges = [{"id": i, "u": u, "v": v} for i, (u, v) in enumerate(free, 1)]
        adjacency = [[None if value == -1 else bool(value) for value in row] for row in known]
        for item in edges:
            adjacency[item["u"]][item["v"]] = adjacency[item["v"]][item["u"]] = item["id"]
        scope = {"schema": "FIXED_TRIANGLE_Q1_FULL99_SCOPE_V1", "archive_commit": ARCHIVE_PIN,
            "archive_Q1_path": "attempts/wave151-triangle-root-factor/exact-results.json",
            "archive_Q1_key": "exact_partial_factor.Q1", "propagation_artifact": key(INPUT),
            "propagation_sha256": INPUT_SHA, "initial_adjacency_full99": raw["initial_adjacency"],
            "known_adjacency_full99": known, "edge_variables": edges,
            "vertex_labels": {"triangle": [0, 1, 2], "A_groups": [list(range(3 + 12 * g, 15 + 12 * g)) for g in range(3)], "B": list(range(39, 99))},
            "target_automorphism_assumed": False, "unrestricted_coverage_claim": False,
            "forced_steps_count": 562, "scope_approval": "PENDING_INDEPENDENT_PROPAGATION_REVIEW"}
        scope_path = args.out / "scope.json"
        save(scope_path, scope)
        rows, products = [], []
        body_path = args.out / "clauses.body"
        with body_path.open("xb") as body:
            clauses = Clauses(body, cap)
            encoder = Encoder(len(edges), clauses)
            for u in range(99):
                terms = [value for value in adjacency[u] if type(value) is int]
                constant = sum(value is True for value in adjacency[u])
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
                        z = encoder.conjunction(a, b)
                        products.append({"id": z, "left": a, "right": b, "pair": [u, v], "center": w,
                            "first_clause": first, "clause_count": 3})
                        terms.append(z)
                edge = adjacency[u][v]
                if edge is True:
                    constant += 1
                elif type(edge) is int:
                    terms.append(edge)
                residual = 2 - constant
                assert 0 <= residual <= len(terms)
                rows.append(encoder.counter(terms, residual, True,
                    {"kind": "pair_equality", "pair": [u, v], "original_bound": 2, "constant": constant}))
                if number % 1000 == 0:
                    print(json.dumps({"state": "BUILDING_FIXED_TRIANGLE_EXACT_PAIRS", "pairs": number,
                        "variables": encoder.top, "clauses": clauses.count}), flush=True)
                    cap.check()
        cnf = args.out / "instance.cnf"
        with cnf.open("xb") as target, body_path.open("rb") as source:
            target.write(f"p cnf {encoder.top} {clauses.count}\n".encode("ascii"))
            shutil.copyfileobj(source, target, 1048576)
        model = {"schema": "CONDITIONAL_TRIANGLE_FULL99_EXACT_PREFIX_CNF_V1", "scope_path": key(scope_path),
            "scope_sha256": digest(scope_path), "propagation_artifact": key(INPUT), "propagation_sha256": INPUT_SHA,
            "known_adjacency_full99": known, "edge_variables": edges, "product_variables": products, "counter_rows": rows,
            "variables": encoder.top, "clauses": clauses.count, "degree_rows": 99, "pair_equality_rows": 4851,
            "prefix_reference_format": "JSON booleans are constants; positive integers are SAT variable IDs.",
            "gate_clause_order": {"and": ["a -z", "b -z", "-a -b z"], "or": ["-a z", "-b z", "a b -z"],
                "a_or_b_and_c": ["-a z", "-b -c z", "a b -z", "a c -z"]},
            "clauses_constant_folded": True, "row_order": "99degrees then lexicographic4851pairs; product centers ascending before each counter.",
            "target_automorphism_assumed": False, "unrestricted_coverage_claim": False,
            "branch_units": [], "family": "Fixed Wave151 Q1 triangle-root full99 completion"}
        model_path = args.out / "model.json"
        save(model_path, model)
        cap.check()
        packages = [package(path, cap) for path in [cnf, model_path]]
        save(args.out / "artifact_packages.json", {"packages": packages,
            "retrieval": "Concatenate ordered gzip parts; decompress; verify exact raw byte count and SHA256."})
        for path, expected in manifest["inputs_sha256"].items():
            assert digest(ROOT / path) == expected
        actual = {"variables": encoder.top, "clauses": clauses.count, "and_products": len(products), "edge_variables": len(edges)}
        expected = {"variables": 429779, "clauses": 1487778, "and_products": 104098, "edge_variables": 1928}
        assert actual == expected
        files = [path for path in args.out.iterdir() if path.is_file() and path.name != "clauses.body"]
        save(args.out / "summary.json", {"timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "CANDIDATE_CONDITIONAL_TRIANGLE_ENCODING_PENDING_INDEPENDENT_GATES", **actual,
            "prefix_variables": encoder.top - len(edges) - len(products), "degree_rows": 99, "pair_equality_rows": 4851,
            "preflight_counts_match": True, "elapsed_seconds": time.monotonic() - cap.start,
            "peak_working_set_bytes": cap.peak_bytes, "resource_samples": cap.samples,
            "outputs": {path.name: {"sha256": digest(path), "bytes": path.stat().st_size} for path in files},
            "solver_calls": 0, "target_resolution": False, "scope": manifest["scope"],
            "limitations": ["Conditional fixed-family encoding only; no general coverage or nonexistence conclusion.",
                "Input propagation and complete new encoding require separate independent checks before solver use.",
                "Historical unproved UNSAT reports are not premises or certificates."]})
        print(json.dumps({"status": "CANDIDATE_CONDITIONAL_TRIANGLE_ENCODING_PENDING_INDEPENDENT_GATES", **actual,
                          "elapsed_seconds": time.monotonic() - cap.start}), flush=True)
    except BaseException as error:
        save(args.out / "failure.json", {"timestamp": datetime.now(timezone.utc).isoformat(), "type": type(error).__name__,
            "message": str(error), "elapsed_seconds": time.monotonic() - cap.start, "solver_calls": 0,
            "status": "INCOMPLETE_CONDITIONAL_TRIANGLE_BUILD"})
        raise


if __name__ == "__main__":
    main()
