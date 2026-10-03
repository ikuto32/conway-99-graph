"""Bounded exact completion of two frozen opposite-cell degree-two blocks."""
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


def save(p, data):
    with p.open("x", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def digest(p):
    return sha256(p.read_bytes()).hexdigest()


def violation_if_added(rows, u, v):
    if (rows[u] >> v) & 1:
        raise ValueError("edge already present")
    shared = (rows[u] & rows[v]).bit_count() + int(u // 10 == v // 10)
    if shared > 1:
        return {"violating_pair": [u, v], "common_after": shared, "cap_after": 1}
    for endpoint, other in ((u, v), (v, u)):
        rest = rows[endpoint]
        while rest:
            bit = rest & -rest
            w = bit.bit_length() - 1
            rest -= bit
            common = (rows[other] & rows[w]).bit_count() + int(other // 10 == w // 10) + 1
            cap = 2 - ((rows[other] >> w) & 1)
            if common > cap:
                return {"violating_pair": [other, w], "common_after": common, "cap_after": cap}
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    save(args.out / "manifest.json", {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "command": [sys.executable, *sys.argv], "cwd": str(Path.cwd()), "python": platform.python_version(),
        "input_hashes": {p.as_posix(): digest(p) for p in (Path(__file__), args.input, Path("uv.lock"))},
        "question": "Can the two opposite right-cell degree-two blocks complete the frozen 50-vertex window without exceeding any target common-neighbor count?",
        "scope": "Only the exact saved central star, all internal matchings, and four already-chosen perfect matchings. There are 200 candidate new edges in two disjoint cell pairs, each requiring a 2-regular bipartite block. Remaining 40 external vertices are absent; passing is only local necessity.",
        "selection_rule": "First reject single edges whose addition violates a monotone common-neighbor upper bound, then depth-first search row neighbor pairs in lexicographic order, with most-constrained-row ordering.",
        "success_criteria": "A complete 2-regular pair of blocks passing every integer cap; first witness stops search.",
        "falsification_criteria": "A row with fewer than two individually possible edges is an exact exclusion of this frozen window; otherwise only complete DFS exhaustion excludes it.",
        "resource_limits": {"nodes": 1000000, "wall_seconds": 120, "stop_on_first_witness": True},
        "numeric_thresholds": None, "numeric_thresholds_reason": "Exact bit counts and integer degree capacities.",
        "status": "CANDIDATE", "independent_review_pending": True,
    })
    data = json.loads(args.input.read_text())
    base = [int(row, 16) for row in data["external_adjacency_rows_hex"]]
    possible = {}
    rejected = []
    for ca, cb in ((1, 4), (2, 3)):
        for u in range(ca * 10, ca * 10 + 10):
            possible[u] = []
            for v in range(cb * 10, cb * 10 + 10):
                failure = violation_if_added(base, u, v)
                if failure:
                    rejected.append({"edge": [u, v], **failure})
                else:
                    possible[u].append(v)
    row_obstructions = [{"vertex": u, "possible_neighbors": vs, "required_degree_in_block": 2}
                        for u, vs in possible.items() if len(vs) < 2]
    save(args.out / "single_edge_filter.json", {
        "possible_columns_by_row": possible, "rejected_edges": rejected,
        "rejection_reason": "Adding more edges cannot reduce a known common-neighbor count or increase its allowed cap.",
        "row_obstructions": row_obstructions})
    start = time.monotonic()
    nodes = 0
    truncated = False
    answer = None
    if not row_obstructions:
        row_order = sorted(possible, key=lambda u: (len(possible[u]), u))
        rows = base.copy()
        capacities = {v: 2 for v in [*range(40, 50), *range(30, 40)]}
        selected = []
        def dfs(level):
            nonlocal nodes, truncated, answer
            if nodes >= 1000000 or time.monotonic() - start >= 120:
                truncated = True
                return False
            nodes += 1
            if level == len(row_order):
                assert not any(capacities.values())
                answer = {"new_edges": selected.copy(), "external_adjacency_rows_hex": [f"{row:013x}" for row in rows]}
                return True
            u = row_order[level]
            for vs in combinations([v for v in possible[u] if capacities[v]], 2):
                inserted = []
                for v in vs:
                    if violation_if_added(rows, u, v):
                        break
                    rows[u] |= 1 << v
                    rows[v] |= 1 << u
                    capacities[v] -= 1
                    selected.append([u, v])
                    inserted.append(v)
                valid = len(inserted) == 2
                if valid:
                    for v, capacity in capacities.items():
                        if capacity > sum(v in possible[w] for w in row_order[level + 1:]):
                            valid = False
                            break
                if valid and dfs(level + 1):
                    return True
                for v in reversed(inserted):
                    rows[u] ^= 1 << v
                    rows[v] ^= 1 << u
                    capacities[v] += 1
                    selected.pop()
                if truncated:
                    return False
            return False
        dfs(0)
    if answer:
        save(args.out / "window_witness.json", answer)
    summary = {"timestamp": datetime.now(timezone.utc).isoformat(), "status": "CANDIDATE", "independent_review_pending": True,
               "candidate_edges": 200, "single_edges_rejected": len(rejected), "single_edges_retained": sum(map(len, possible.values())),
               "row_obstruction_count": len(row_obstructions), "dfs_nodes": nodes, "dfs_truncated": truncated,
               "window_witness": answer is not None, "fixed_window_exclusion_candidate": bool(row_obstructions) or (answer is None and not truncated),
               "stop_reason": "ROW_DEGREE_OBSTRUCTION" if row_obstructions else "FIRST_WINDOW_WITNESS" if answer else "RESOURCE_CAP" if truncated else "EXHAUSTIVE_DFS",
               "elapsed_seconds": time.monotonic() - start, "target_exclusion": False,
               "filter_sha256": digest(args.out / "single_edge_filter.json")}
    save(args.out / "summary.json", summary)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
