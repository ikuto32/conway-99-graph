"""Bounded joint witness search in a frozen necessary rook-cell relaxation."""
from datetime import datetime, timezone
from hashlib import sha256
import argparse
import json
from pathlib import Path
import platform
import random
import subprocess
import sys
import time

from tqdm import trange


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
    pairs = [(0, 1), (0, 2), (1, 3), (2, 3)]
    paths = [args.pairs / f"pair_{j}_{k}.json" for j, k in pairs]
    save(args.out / "manifest.json", {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "command": [sys.executable, *sys.argv], "cwd": str(Path.cwd()), "python": platform.python_version(),
        "input_hashes": {p.as_posix(): digest(p) for p in [Path(__file__), args.star, *paths, Path("uv.lock")]},
        "question": "Does a joint assignment of all four rook-adjacent right-cell permutations survive the full known common-neighbor upper bounds of the frozen 50-external-vertex relaxation?",
        "scope": "One frozen central star; four cross blocks sampled from the complete pair domains. Unassigned cross edges and other external cells remain missing. No exclusion follows from sample failure.",
        "selection_rule": "Python Random seed 20260930 independently samples one index from each saved complete pair domain; first all-cap witness is retained.",
        "success_criteria": "Every pair of the 50 external vertices has at most 2-A_uv known common neighbors, including its shared rook neighbor when in one cell.",
        "falsification_criteria": "Any excess known common-neighbor count rejects that sample, even if earlier three-cell tests passed.",
        "resource_limits": {"attempt_cap": 100000, "wall_seconds_cap": 120, "stop_on_first_witness": True},
        "numeric_thresholds": None, "reason": "Integer bit counts only.", "random_seed": 20260930,
        "status": "CANDIDATE", "independent_review_pending": True,
    })
    star = json.loads(args.star.read_text())
    domains = [json.loads(p.read_text())["permutations"] for p in paths]
    base = [0] * 50
    def edge(rows, i, j):
        rows[i] |= 1 << j
        rows[j] |= 1 << i
    for i, j in star["matching"]:
        edge(base, i, j)
    for k, item in enumerate(star["four_factors"]):
        offset = 10 * (k + 1)
        for i, j in item["partner_matching"]:
            edge(base, offset + i, offset + j)
        for i, row in enumerate(item["incidence_block"]):
            for j, value in enumerate(row):
                if value:
                    edge(base, i, offset + j)
    start = time.monotonic()
    rng = random.Random(20260930)
    failures = {}
    answer = None
    attempts = 0
    for attempt in trange(100000, desc="Joint rook-cap samples", unit="sample"):
        if time.monotonic() - start >= 120:
            break
        indices = [rng.randrange(len(domain)) for domain in domains]
        rows = base.copy()
        for (j, k), domain, index in zip(pairs, domains, indices):
            for y, z in enumerate(domain[index]):
                edge(rows, 10 * (j + 1) + y, 10 * (k + 1) + z)
        attempts += 1
        first_failure = None
        for i in range(50):
            for j in range(i + 1, 50):
                common = (rows[i] & rows[j]).bit_count() + int(i // 10 == j // 10)
                threshold = 2 - ((rows[i] >> j) & 1)
                if common > threshold:
                    first_failure = (i // 10, j // 10)
                    break
            if first_failure is not None:
                break
        if first_failure is None:
            answer = {"attempt": attempts, "indices": indices,
                      "permutations": [domain[index] for domain, index in zip(domains, indices)],
                      "external_adjacency_rows_hex": [f"{row:013x}" for row in rows]}
            save(args.out / "joint_witness.json", answer)
            break
        key = f"{first_failure[0]}-{first_failure[1]}"
        failures[key] = failures.get(key, 0) + 1
        if attempts % 10000 == 0:
            save(args.out / f"checkpoint_{attempts}.json", {"attempts": attempts, "rng_state": rng.getstate(), "rejections_by_first_cell_pair": failures, "elapsed_seconds": time.monotonic() - start})
    summary = {"timestamp": datetime.now(timezone.utc).isoformat(), "status": "CANDIDATE", "independent_review_pending": True,
               "attempts": attempts, "distinct_assignments": None, "distinct_assignments_reason": "Draws may repeat; only attempts counted.",
               "elapsed_seconds": time.monotonic() - start, "witness_found": answer is not None,
               "stop_reason": "FIRST_LOCAL_WITNESS" if answer else "ATTEMPT_CAP" if attempts == 100000 else "WALL_CAP",
               "rejections_by_first_cell_pair": failures, "target_graph": False, "target_exclusion": False,
               "proof_of_relaxation_infeasibility": False}
    if answer:
        summary["witness_sha256"] = digest(args.out / "joint_witness.json")
    save(args.out / "summary.json", summary)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
