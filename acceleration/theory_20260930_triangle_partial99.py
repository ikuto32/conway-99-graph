"""Exact unit propagation on two fixed triangle-root partial99 matrices."""
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from hashlib import sha256
import json
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
PRE = ROOT / "acceleration/results/20260930_triangle_factor_preflight"
OUT = ROOT / "acceleration/results/20260930_triangle_partial99"
SPEC = Path(__file__).with_name("theory_20260930_triangle_partial99_spec.md")


def save(path, obj):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(obj, stream, indent=2)
        stream.write("\n")


def h(path):
    return sha256(path.read_bytes()).hexdigest()


def propagate(initial, k, lam, mu, max_rounds=30, deadline=None):
    a = [row.copy() for row in initial]
    n = len(a)
    steps = []
    def force(u, v, value, rule, witness):
        if a[u][v] == value:
            return
        if a[u][v] != -1 or u == v:
            raise ValueError("propagation attempted inconsistent assignment")
        a[u][v] = a[v][u] = value
        steps.append({"edge": [min(u, v), max(u, v)], "value": value, "rule": rule, "witness": witness})
    def finish(status, round_id, failure=None):
        return {"status": status, "rounds": round_id, "steps": steps, "final_adjacency": a,
                "failure": failure, "failure_null_reason": "No contradiction found within saved scan." if failure is None else None,
                "remaining_unknown_edges": sum(a[u][v] == -1 for u in range(n) for v in range(u + 1, n))}
    for round_id in range(1, max_rounds + 1):
        if deadline is not None and time.monotonic() >= deadline:
            return finish("TIME_LIMIT_UNKNOWN", round_id - 1)
        before = len(steps)
        for u in range(n):
            ones = sum(x == 1 for x in a[u])
            missing = [v for v in range(n) if a[u][v] == -1]
            if ones > k or ones + len(missing) < k:
                return finish("CANDIDATE_EXACT_PROPAGATION_CONTRADICTION", round_id,
                              {"rule": "degree_interval", "vertex": u, "lower": ones, "upper": ones + len(missing), "required": k})
            if ones == k or ones + len(missing) == k:
                value = int(ones != k)
                for v in missing:
                    force(u, v, value, "degree_bound", {"vertex": u, "required": k})
        for u in range(n):
            for v in range(u + 1, n):
                known = [w for w in range(n) if a[u][w] == a[v][w] == 1]
                possible = [w for w in range(n) if a[u][w] != 0 and a[v][w] != 0]
                low, high = len(known), len(possible)
                if a[u][v] == -1:
                    choices = [value for value, target in [(0, mu), (1, lam)] if low <= target <= high]
                    if not choices:
                        return finish("CANDIDATE_EXACT_PROPAGATION_CONTRADICTION", round_id,
                                      {"rule": "no_pair_adjacency_possible", "pair": [u, v], "lower": low, "upper": high})
                    if len(choices) == 1:
                        force(u, v, choices[0], "adjacency_from_common_interval", {"pair": [u, v]})
                if a[u][v] == -1:
                    continue
                required = lam if a[u][v] else mu
                if low > required or high < required:
                    return finish("CANDIDATE_EXACT_PROPAGATION_CONTRADICTION", round_id,
                                  {"rule": "common_interval", "pair": [u, v], "lower": low, "upper": high, "required": required})
                if low == required:
                    for w in possible:
                        if a[u][w] == 1 and a[v][w] == -1:
                            force(v, w, 0, "common_lower_tight", {"pair": [u, v], "center": w})
                        elif a[v][w] == 1 and a[u][w] == -1:
                            force(u, w, 0, "common_lower_tight", {"pair": [u, v], "center": w})
                if high == required:
                    for w in possible:
                        if a[u][w] == -1:
                            force(u, w, 1, "common_upper_tight", {"pair": [u, v], "center": w})
                        if a[v][w] == -1:
                            force(v, w, 1, "common_upper_tight", {"pair": [u, v], "center": w})
        if len(steps) == before:
            return finish("FIXED_POINT_UNKNOWN", round_id)
    return finish("ROUND_LIMIT_UNKNOWN", max_rounds)


def controls():
    fixtures = []
    fixtures.append(("C5", [[int((u-v) % 5 in (1, 4)) for v in range(5)] for u in range(5)], 2, 0, 1))
    sets = list(combinations(range(5), 2))
    fixtures.append(("Petersen", [[int(set(u).isdisjoint(v)) for v in sets] for u in sets], 3, 0, 1))
    fixtures.append(("rook9", [[int(u != v and (u // 3 == v // 3 or u % 3 == v % 3)) for v in range(9)] for u in range(9)], 4, 1, 2))
    records = []
    for name, a, k, lam, mu in fixtures:
        masked = [row.copy() for row in a]
        masked[0][1] = masked[1][0] = -1
        result = propagate(masked, k, lam, mu)
        if result["status"] != "FIXED_POINT_UNKNOWN" or result["final_adjacency"] != a:
            raise ValueError("known-valid masked fixture failed")
        corrupted = [row.copy() for row in a]
        corrupted[0][1] = corrupted[1][0] = 1 - a[0][1]
        bad = propagate(corrupted, k, lam, mu)
        if bad["status"] != "CANDIDATE_EXACT_PROPAGATION_CONTRADICTION":
            raise ValueError("corrupted complete fixture accepted")
        records.append({"name": name, "masked_restored": True, "corrupt_rejected": True, "corrupt_failure": bad["failure"]})
    return records


def make_initial(raw):
    a = [[0] * 99 for _ in range(99)]
    def edge(u, v, value=1):
        a[u][v] = a[v][u] = value
    for u, v in combinations(range(3), 2):
        edge(u, v)
    for group in range(3):
        for u in range(12):
            edge(group, 3 + 12 * group + u)
            edge(3 + 12 * group + u, 3 + 12 * group + (u ^ 1))
    for u in range(12):
        edge(3 + u, 15 + u)
        edge(3 + u, 27 + u)
        edge(15 + u, 27 + (u + 6) % 12)
    for u in range(24):
        for d in range(60):
            edge(3 + u, 39 + d, raw["C01"][u][d])
    for u in range(12):
        for d in range(60):
            edge(27 + u, 39 + d, -1)
    for u, v in combinations(range(60), 2):
        edge(39 + u, 39 + v, -1)
    return a


def main():
    started = time.monotonic()
    OUT.mkdir(parents=True, exist_ok=False)
    paths = [PRE / "wave151.json", PRE / "wave154.json"]
    save(OUT / "manifest.json", {"timestamp": datetime.now(timezone.utc).isoformat(),
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "command": [sys.executable, *sys.argv], "cwd": str(ROOT), "resource_seconds": 120, "round_limit_each": 30,
        "inputs_sha256": {p.relative_to(ROOT).as_posix(): h(p) for p in [*paths, Path(__file__), SPEC, ROOT / "uv.lock"]},
        "selection": "Both displayed archived Q1 cases, no selection after results", "solver_calls": 0})
    save(OUT / "controls.json", controls())
    summaries = []
    for path in paths:
        raw = json.loads(path.read_bytes())
        initial = make_initial(raw)
        result = propagate(initial, 14, 1, 2, deadline=started + 120)
        final = result["final_adjacency"]
        result.update({"case": raw["case"], "initial_adjacency": initial, "target_parameters": [99, 14, 1, 2],
            "scope": "This fixed triangle-root scaffold and exact displayed Q1 only", "independent_review": False,
            "initial_unknown_edges": 2490,
            "remaining_C2_unknown": sum(final[u][v] == -1 for u in range(27, 39) for v in range(39, 99)),
            "remaining_D_unknown": sum(final[u][v] == -1 for u in range(39, 99) for v in range(u + 1, 99))})
        artifact = OUT / (raw["case"] + ".json")
        save(artifact, result)
        summaries.append({"case": raw["case"], "artifact": artifact.relative_to(ROOT).as_posix(), "sha256": h(artifact),
            "status": result["status"], "forced_edges": len(result["steps"]), "rounds": result["rounds"],
            "remaining_C2_unknown": result["remaining_C2_unknown"], "remaining_D_unknown": result["remaining_D_unknown"],
            "failure": result["failure"]})
    save(OUT / "summary.json", {"status": "CANDIDATE_PARTIAL99_PROPAGATION_COMPLETE", "cases": summaries,
        "elapsed_seconds": time.monotonic() - started, "solver_calls": 0, "target_resolution": "UNKNOWN", "independent_approval": False})
    print(json.dumps({"cases": summaries, "elapsed_seconds": time.monotonic() - started}, indent=2))


if __name__ == "__main__":
    main()
