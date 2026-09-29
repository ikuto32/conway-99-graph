"""No-file exact prefix encoder census for the two propagated full99 families."""
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
import json
import subprocess
import sys
import time

from theory_20260930_eight_full99_cnf import Clauses, Encoder, ResourceCap, digest, save

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "acceleration/results/20260930_triangle_cnf_census"
PARTIAL = ROOT / "acceleration/results/20260930_triangle_partial99"


class CountBytes:
    def __init__(self):
        self.bytes = 0

    def write(self, value):
        self.bytes += len(value)


def main():
    OUT.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    cap = ResourceCap()
    paths = [PARTIAL / "wave151.json", PARTIAL / "wave154.json"]
    frozen = ROOT / "acceleration/theory_20260930_eight_full99_cnf.py"
    save(OUT / "manifest.json", {"timestamp": datetime.now(timezone.utc).isoformat(),
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "command": [sys.executable, *sys.argv], "cwd": str(ROOT), "resource_seconds": 120,
        "input_hashes": {p.relative_to(ROOT).as_posix(): digest(p) for p in [*paths, frozen, Path(__file__), ROOT / "uv.lock"]},
        "scope": "Engineering size census only, two propagated conditional99families; no solve and no independent propagation approval",
        "selection": "Both saved families, no after-result selection", "counter_semantics": "exact degree14 and exact common+Auv=2 for every pair, all gates bidirectional",
        "sink": "Count DIMACS body bytes while discarding clause text; do not create a research CNF", "solver_calls": 0,
        "shared_components": ["Frozen producer exact threshold helpers, not an independent encoding review"]})
    results = []
    for path in paths:
        raw = json.loads(path.read_bytes())
        known = raw["final_adjacency"]
        free = [(u, v) for u, v in combinations(range(99), 2) if known[u][v] == -1]
        adjacency = [[None if x == -1 else bool(x) for x in row] for row in known]
        for variable, (u, v) in enumerate(free, 1):
            adjacency[u][v] = adjacency[v][u] = variable
        sink = CountBytes()
        clauses = Clauses(sink, cap)
        encoder = Encoder(len(free), clauses)
        products = 0
        degree_rows = pair_rows = 0
        for u in range(99):
            terms = [value for value in adjacency[u] if type(value) is int]
            constant = sum(value is True for value in adjacency[u])
            encoder.counter(terms, 14 - constant, True, {"kind": "degree"})
            degree_rows += 1
        for u, v in combinations(range(99), 2):
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
                    terms.append(encoder.conjunction(a, b))
                    products += 1
            edge = adjacency[u][v]
            if edge is True:
                constant += 1
            elif type(edge) is int:
                terms.append(edge)
            encoder.counter(terms, 2 - constant, True, {"kind": "exact_pair"})
            pair_rows += 1
        result = {"case": raw["case"], "input": path.relative_to(ROOT).as_posix(), "input_sha256": digest(path),
            "primary_edges": len(free), "and_products": products, "prefix_variables": encoder.top - len(free) - products,
            "total_variables": encoder.top, "clauses": clauses.count, "dimacs_body_bytes": sink.bytes,
            "degree_rows": degree_rows, "pair_rows": pair_rows, "actual_cnf_saved": False, "solver_calls": 0,
            "scope": "Conditional completion of one fixed triangle-root Q1, including residualD."}
        results.append(result)
        cap.check()
    save(OUT / "summary.json", {"status": "CANDIDATE_EXACT_ENCODER_SIZE_CENSUS", "cases": results,
        "elapsed_seconds": time.monotonic() - started, "peak_memory_bytes": cap.peak_bytes,
        "solver_calls": 0, "independent_verification": False, "target_resolution": "UNKNOWN"})
    print(json.dumps({"cases": results, "elapsed_seconds": time.monotonic() - started}, indent=2))


if __name__ == "__main__":
    main()
