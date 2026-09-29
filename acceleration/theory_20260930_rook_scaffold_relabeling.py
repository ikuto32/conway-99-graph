"""Exact bounded census of relabelings of the designated fixed rook scaffold."""
from datetime import datetime, timezone
from hashlib import sha256
from itertools import permutations, product
import argparse
import json
from pathlib import Path
import platform
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "acceleration/results/20260930_rook_free_internal_sat/model.json"
STAR = ROOT / "acceleration/results/20260930_rook_cell_factors/local_witness.json"


def digest(path):
    return sha256(Path(path).read_bytes()).hexdigest()


def save(path, obj):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(obj, stream, indent=2)
        stream.write("\n")


def check_map(full, known, edges, degree_signatures, shared):
    assert len(full) == 59 and sorted(full) == list(range(59)), "not a full59 bijection"
    assert sorted(full[:9]) == list(range(9)), "core not preserved"
    for u in range(59):
        for v in range(59):
            assert known[u][v] == known[full[u]][full[v]], "known/free adjacency mismatch"
    emap = {}
    for (u, v), variable in edges.items():
        mapped = tuple(sorted((full[u + 9] - 9, full[v + 9] - 9)))
        assert mapped in edges, "free edge not preserved"
        emap[variable] = edges[mapped]
    assert sorted(emap.values()) == list(range(1, 781)), "edge map not bijective"
    transformed = {(value, tuple(sorted(emap[v] for v in variables))) for value, variables in degree_signatures}
    assert transformed == degree_signatures, "block degree signatures not preserved"
    for u in range(50):
        for v in range(50):
            assert shared[u][v] == shared[full[u + 9] - 9][full[v + 9] - 9], "core common-neighbor ownership mismatch"
    return [emap[v] for v in range(1, 781)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--wave02-summary", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    wave = json.loads(args.wave02_summary.read_text())
    assert wave["no_research_process_left_by_this_script"] is True
    assert digest(MODEL) == "26908e992235e307cfc6145275deb3d2765a930c7c59a774c9a7bc42f2f0f95e"
    assert digest(STAR) == "da71c5381af0a68f8a7e7dea36535b92cbcfc67d95e3b57d6cc3591dd1dda33f"
    inputs = [Path(__file__), Path(__file__).with_name("theory_20260930_rook_scaffold_relabeling_spec.md"),
              MODEL, STAR, args.wave02_summary, ROOT / "uv.lock"]
    save(args.out / "manifest.json", {"timestamp": datetime.now(timezone.utc).isoformat(),
         "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
         "command": [sys.executable, *sys.argv], "cwd": str(ROOT), "python": platform.python_version(),
         "input_hashes": {str(p): digest(p) for p in inputs},
         "question": "Find all accepted relabelings in the frozen 3840 central matching permutations times 8 rook-core maps.",
         "scope": "Designated core and central cell preserved; one fixed central scaffold, no assumed target automorphism.",
         "limits": {"central_permutations": 3840, "core_maps": 8, "pair_tests": 30720, "wall_seconds": 60},
         "status": "CANDIDATE", "independent_review_pending": True})
    model = json.loads(MODEL.read_text())
    star = json.loads(STAR.read_text())
    coordinates = [tuple(x) for x in model["cell_rook_coordinates"]]
    coordinate_cell = {x: i for i, x in enumerate(coordinates)}
    columns = []
    for block in star["four_factors"]:
        matrix = block["incidence_block"]
        supports = [tuple(u for u in range(10) if matrix[u][v]) for v in range(10)]
        assert len(set(supports)) == 10 and all(len(s) == 2 for s in supports)
        columns.append(supports)
    known = [[0] * 59 for _ in range(59)]
    for u in range(9):
        for v in range(9):
            known[u][v] = int(u != v and (u // 3 == v // 3 or u % 3 == v % 3))
    for u in range(50):
        owner = coordinates[u // 10][0] * 3 + coordinates[u // 10][1]
        known[owner][u + 9] = known[u + 9][owner] = 1
        for v in range(50):
            known[u + 9][v + 9] = model["known_adjacency"][u][v]
    edges = {(row["u"], row["v"]): row["id"] for row in model["edge_variables"]}
    degrees = {(row["value"], tuple(sorted(row["variables"]))) for row in model["degree_constraints"]}
    shared = model["shared_core_common_neighbors"]
    cores = []
    for row_swap, column_swap, transpose in product((False, True), repeat=3):
        core = []
        for u in range(9):
            r, c = divmod(u, 3)
            r = 3 - r if row_swap and r else r
            c = 3 - c if column_swap and c else c
            if transpose:
                r, c = c, r
            core.append(3 * r + c)
        cells = [coordinate_cell[divmod(core[3 * r + c], 3)] for r, c in coordinates]
        cores.append((core, cells))
    accepted = []
    tested = 0
    start = time.monotonic()
    stop = "COMPLETE"
    for pair_order in permutations(range(5)):
        for flips in product((0, 1), repeat=5):
            central = [2 * pair_order[u // 2] + ((u % 2) ^ flips[u // 2]) for u in range(10)]
            for core, cells in cores:
                if time.monotonic() - start >= 60:
                    stop = "WALL_CAP_PARTIAL"
                    break
                tested += 1
                external = central.copy()
                compatible = True
                for source_cell in range(1, 5):
                    target_cell = cells[source_cell]
                    lookup = {support: j for j, support in enumerate(columns[target_cell - 1])}
                    mapped = [tuple(sorted(central[u] for u in support)) for support in columns[source_cell - 1]]
                    if any(support not in lookup for support in mapped):
                        compatible = False
                        break
                    external.extend(target_cell * 10 + lookup[support] for support in mapped)
                if compatible:
                    full = core + [u + 9 for u in external]
                    edge_map = check_map(full, known, edges, degrees, shared)
                    accepted.append({"central": central, "core": core, "cells": cells,
                                     "full59": full, "edge_variable_map": edge_map})
            if stop != "COMPLETE":
                break
        if stop != "COMPLETE":
            break
    controls = {}
    identity = list(range(59))
    controls["identity_passed"] = check_map(identity, known, edges, degrees, shared) == list(range(1, 781))
    for name, bad in (("duplicate_vertex", identity[:58] + [57]),
                      ("wrong_central_swap", [*range(9), 11, 10, 9, *range(12, 59)]),
                      ("wrong_right_swap", [*range(19), 20, 19, *range(21, 59)])):
        try:
            check_map(bad, known, edges, degrees, shared)
        except AssertionError as exc:
            controls[name] = {"rejected": True, "reason": str(exc)}
        else:
            raise AssertionError(f"corruption accepted: {name}")
    maps = {tuple(row["full59"]) for row in accepted}
    assert len(maps) == len(accepted), "duplicate accepted pair"
    assert tuple(identity) in maps
    closure = all(tuple(left[right[v]] for v in range(59)) in maps for left in maps for right in maps)
    if stop == "COMPLETE":
        assert tested == 30720 and closure
    save(args.out / "accepted_relabelings.json", {"maps": accepted})
    save(args.out / "summary.json", {"timestamp": datetime.now(timezone.utc).isoformat(),
         "status": "CANDIDATE_PENDING_INDEPENDENT_AUDIT", "stop_reason": stop,
         "tested_pairs": tested, "frozen_universe_pairs": 30720, "accepted_maps": len(accepted),
         "elapsed_seconds": time.monotonic() - start, "closure_on_observed_maps": closure,
         "controls": controls, "raw_maps_sha256": digest(args.out / "accepted_relabelings.json"),
         "clause_transport_performed": False, "target_resolution": False})
    print(json.dumps({"stop": stop, "tested": tested, "accepted": len(accepted), "seconds": time.monotonic() - start}))


if __name__ == "__main__":
    main()
