"""Broaden frozen rook-star CNF by freeing the four right internal matchings."""
from datetime import datetime, timezone
import gzip
import json
from itertools import combinations
from pathlib import Path
import platform
import subprocess
import sys
import time
import argparse

from theory_20260930_rook_window_sat import controls, digest, encode, save, write_cnf


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    inputs = [Path(__file__), Path("acceleration/theory_20260930_rook_window_sat.py"),
              Path("acceleration/theory_20260930_rook_free_internal_sat.md"), args.input, Path("uv.lock")]
    save(args.out / "manifest.json", {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "command": [sys.executable, *sys.argv], "cwd": str(Path.cwd()), "python": platform.python_version(),
        "input_hashes": {p.as_posix(): digest(p) for p in inputs},
        "question": "Can the exact central factor star extend locally when all four right internal matchings are free?",
        "scope": "780 independent edge variables; central matching and four central incidence blocks fixed. All right-cell internal matchings and cross blocks free subject to exact block degrees and all known common-neighbor caps.",
        "resource_limits": {"maximum_variables": 32000, "maximum_clauses": 4000000,
                            "future_solver_wall_seconds": 300, "future_solver_conflicts": 1000000},
        "selection_rule": "Broaden only the four previously fixed right internal matchings; preserve the raw central star.",
        "success_criteria": "Fresh independent encoding gate, then independently checked local SAT object or exact scoped DRAT proof.",
        "status": "CANDIDATE", "independent_review_pending": True, "solver_launched": False,
    })
    calibration = controls(args.out)
    star = json.loads(args.input.read_text())
    known = [[0] * 50 for _ in range(50)]
    def edge(u, v, value):
        known[u][v] = known[v][u] = value
    for u, v in star["matching"]:
        edge(u, v, 1)
    for cell, item in enumerate(star["four_factors"], 1):
        for u, row in enumerate(item["incidence_block"]):
            for v, value in enumerate(row):
                if value:
                    edge(u, cell * 10 + v, 1)
    for u in range(10, 50):
        for v in range(u + 1, 50):
            edge(u, v, -1)
    def degrees(adj):
        rows = []
        for ca, cb in combinations(range(1, 5), 2):
            value = 2 if (ca, cb) in ((1, 4), (2, 3)) else 1
            for u in range(ca * 10, ca * 10 + 10):
                rows.append({"variables": [adj[u][v] for v in range(cb * 10, cb * 10 + 10)], "value": value, "label": [ca, cb, "row", u]})
            for v in range(cb * 10, cb * 10 + 10):
                rows.append({"variables": [adj[u][v] for u in range(ca * 10, ca * 10 + 10)], "value": value, "label": [ca, cb, "column", v]})
        for cell in range(1, 5):
            for u in range(cell * 10, cell * 10 + 10):
                rows.append({"variables": [adj[u][v] for v in range(cell * 10, cell * 10 + 10) if v != u],
                             "value": 1, "label": [cell, "internal", u]})
        return rows
    shared = [[int(u != v and u // 10 == v // 10) for v in range(50)] for u in range(50)]
    model, clauses = encode(known, shared, degrees)
    assert len(model["edge_variables"]) == 780 and len(model["degree_constraints"]) == 160
    assert model["variables"] <= 32000 and len(clauses) <= 4000000
    model["cell_rook_coordinates"] = [[0, 0], [1, 1], [1, 2], [2, 1], [2, 2]]
    model["right_internal_matchings_free"] = True
    save(args.out / "model.json", model)
    write_cnf(args.out / "instance.cnf", model["variables"], clauses)
    for name in ("instance.cnf", "model.json"):
        with (args.out / name).open("rb") as source, (args.out / (name + ".gz")).open("xb") as target:
            with gzip.GzipFile(fileobj=target, mode="wb", mtime=0) as compressed:
                for block in iter(lambda: source.read(1024 * 1024), b""):
                    compressed.write(block)
    save(args.out / "controls.json", calibration)
    files = [p for p in args.out.iterdir() if p.is_file()]
    save(args.out / "summary.json", {"timestamp": datetime.now(timezone.utc).isoformat(), "status": "CANDIDATE",
         "variables": model["variables"], "edge_variables": 780, "product_variables": len(model["products"]),
         "clauses": len(clauses), "pair_constraints": 1225, "degree_constraints": 160,
         "independent_review_pending": True, "solver_launched": False, "elapsed_seconds": time.monotonic() - start,
         "outputs": {p.name: {"sha256": digest(p), "bytes": p.stat().st_size} for p in files}})
    print(json.dumps({"variables": model["variables"], "clauses": len(clauses), "elapsed_seconds": time.monotonic() - start}, indent=2))


if __name__ == "__main__":
    main()
