"""Bounded search for a complete local rook window with cheap row pruning.

No sampled failure is an exclusion. Exact DFS is used only to complete each
sampled four-permutation window. The resource cap applies to the entire run.
"""
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import argparse
import json
import platform
import random
import subprocess
import sys
import time

from tqdm import tqdm
from theory_20260930_rook_complete_window import violation_if_added


def digest(p):
    return sha256(p.read_bytes()).hexdigest()


def save(p, data):
    with p.open("x", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--star", type=Path, required=True)
    parser.add_argument("--pairs", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    pair_indices = [(0, 1), (0, 2), (1, 3), (2, 3)]
    files = [args.pairs / f"pair_{a}_{b}.json" for a, b in pair_indices]
    save(args.out / "manifest.json", {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "command": [sys.executable, *sys.argv], "cwd": str(Path.cwd()), "python": platform.python_version(),
        "input_hashes": {p.as_posix(): digest(p) for p in [Path(__file__), Path("acceleration/theory_20260930_rook_complete_window.py"), args.star, *files, Path("uv.lock")]},
        "question": "Does the stronger fixed-star local model admit a 50-external-vertex window with every selected cell-to-cell degree and common-neighbor upper bound?",
        "scope": "One fixed factor star and its fixed internal matchings. Four perfect matchings are sampled; the two missing degree-two blocks are completed by exact DFS when single-edge row/column capacity tests permit. This does not cover all stars or prove global feasibility.",
        "selection_rule": "Python Random seed 2026093001 samples four pair-domain indices independently; reject all-pair cap failures, then single-edge row/column degree obstructions; solve remaining two blocks by exact DFS.",
        "success_criteria": "One full 50-vertex local adjacency satisfying prescribed block degrees and all pair common-neighbor caps; emit raw complete local adjacency.",
        "falsification_criteria": "Reject any sampled window with cap excess or any required row/column with fewer than two individually admissible edges; all such rejections concern only that sample.",
        "resource_limits": {"wall_seconds": 120, "attempt_cap": 10000000, "per_window_dfs_node_cap": 100000, "stop_on_first_complete_window": True},
        "numeric_thresholds": None, "numeric_thresholds_reason": "Exact integer bit counts, no numerical threshold.",
        "random_seed": 2026093001, "status": "CANDIDATE", "independent_review_pending": True,
    })
    star = json.loads(args.star.read_text())
    domains = [json.loads(p.read_text())["permutations"] for p in files]
    base = [0] * 50
    def edge(rows, u, v):
        rows[u] |= 1 << v
        rows[v] |= 1 << u
    for u, v in star["matching"]:
        edge(base, u, v)
    for cell, item in enumerate(star["four_factors"], 1):
        for u, v in item["partner_matching"]:
            edge(base, cell * 10 + u, cell * 10 + v)
        for u, row in enumerate(item["incidence_block"]):
            for v, value in enumerate(row):
                if value:
                    edge(base, u, cell * 10 + v)
    start = time.monotonic()
    rng = random.Random(2026093001)
    counts = {"attempts": 0, "cap_rejections": 0, "cap_survivors": 0,
              "capacity_rejections": 0, "capacity_survivors": 0,
              "dfs_completed_without_witness": 0, "dfs_node_cap": 0,
              "dfs_wall_cap": 0, "dfs_nodes": 0, "completed_local_witnesses": 0}
    best_capacity = -1
    best_record = None
    progress = tqdm(total=10000000, desc="Pruned local rook draws", unit="draw", mininterval=10)
    def all_caps(rows):
        for u in range(50):
            for v in range(u + 1, 50):
                if (rows[u] & rows[v]).bit_count() + int(u // 10 == v // 10) > 2 - ((rows[u] >> v) & 1):
                    return False
        return True
    while counts["attempts"] < 10000000 and time.monotonic() - start < 120:
        indices = [rng.randrange(len(domain)) for domain in domains]
        rows = base.copy()
        for (a, b), domain, index in zip(pair_indices, domains, indices):
            for u, v in enumerate(domain[index]):
                edge(rows, (a + 1) * 10 + u, (b + 1) * 10 + v)
        counts["attempts"] += 1
        progress.update(1)
        if not all_caps(rows):
            counts["cap_rejections"] += 1
            continue
        counts["cap_survivors"] += 1
        possible = {}
        columns = [*range(30, 40), *range(40, 50)]
        for ca, cb in ((1, 4), (2, 3)):
            for u in range(ca * 10, ca * 10 + 10):
                possible[u] = [v for v in range(cb * 10, cb * 10 + 10)
                               if violation_if_added(rows, u, v) is None]
        met = sum(len(vs) >= 2 for vs in possible.values()) + sum(sum(v in vs for vs in possible.values()) >= 2 for v in columns)
        if met > best_capacity:
            best_capacity = met
            best_record = {"attempt": counts["attempts"], "indices": indices,
                           "rows_and_columns_meeting_necessary_degree_two": met, "total_rows_and_columns": 40,
                           "possible_columns_by_row": possible, "external_adjacency_rows_hex": [f"{row:013x}" for row in rows]}
            save(args.out / f"capacity_best_{met:02d}.json", best_record)
        if met < 40:
            counts["capacity_rejections"] += 1
            continue
        counts["capacity_survivors"] += 1
        row_order = sorted(possible, key=lambda u: (len(possible[u]), u))
        capacity = {v: 2 for v in columns}
        node_count = 0
        outcome = "EXHAUSTED"
        selected = []
        def dfs(level):
            nonlocal node_count, outcome
            if node_count >= 100000:
                outcome = "NODE_CAP"
                return False
            if time.monotonic() - start >= 120:
                outcome = "WALL_CAP"
                return False
            node_count += 1
            if level == 20:
                assert not any(capacity.values()) and all_caps(rows)
                outcome = "WITNESS"
                return True
            u = row_order[level]
            for vs in combinations([v for v in possible[u] if capacity[v]], 2):
                inserted = []
                for v in vs:
                    if violation_if_added(rows, u, v):
                        break
                    edge(rows, u, v)
                    inserted.append(v)
                    selected.append([u, v])
                    capacity[v] -= 1
                valid = len(inserted) == 2 and all(cap <= sum(v in possible[w] for w in row_order[level + 1:]) for v, cap in capacity.items())
                if valid and dfs(level + 1):
                    return True
                for v in reversed(inserted):
                    rows[u] ^= 1 << v
                    rows[v] ^= 1 << u
                    capacity[v] += 1
                    selected.pop()
                if outcome in ("NODE_CAP", "WALL_CAP"):
                    return False
            return False
        dfs(0)
        counts["dfs_nodes"] += node_count
        if outcome == "WITNESS":
            counts["completed_local_witnesses"] += 1
            save(args.out / "complete_window.json", {"attempt": counts["attempts"], "indices": indices,
                 "new_edges": selected, "external_adjacency_rows_hex": [f"{row:013x}" for row in rows],
                 "full_local_adjacency": [[(row >> v) & 1 for v in range(50)] for row in rows]})
            break
        counts[{"EXHAUSTED": "dfs_completed_without_witness", "NODE_CAP": "dfs_node_cap", "WALL_CAP": "dfs_wall_cap"}[outcome]] += 1
        if outcome == "WALL_CAP":
            break
    progress.close()
    save(args.out / "resume_state.json", {"rng_state": rng.getstate(), "counts": counts, "best_capacity": best_capacity,
         "restart_note": "RNG state and counters saved at draw boundary. A DFS interrupted by wall cap is not stack-resumable and must be rerun from its frozen draw if needed."})
    summary = {"timestamp": datetime.now(timezone.utc).isoformat(), "status": "CANDIDATE", "independent_review_pending": True,
               "counts": counts, "best_capacity": best_capacity, "capacity_population": "40 rows and columns in the two missing blocks for one sampled window",
               "elapsed_seconds": time.monotonic() - start,
               "stop_reason": "FIRST_COMPLETE_WINDOW" if counts["completed_local_witnesses"] else "ATTEMPT_CAP" if counts["attempts"] == 10000000 else "WALL_CAP",
               "scope_exclusion": False, "target_graph": False, "target_exclusion": False,
               "distinct_assignments": None, "distinct_assignments_reason": "Attempts may repeat; uniqueness not recorded."}
    save(args.out / "summary.json", summary)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
