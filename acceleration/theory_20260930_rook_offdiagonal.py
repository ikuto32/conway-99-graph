"""Exact necessary off-diagonal pair tests of the frozen rook-cell witness.

Discovery only; reports CANDIDATE. Exhaustive permutation domains are retained
as raw lists, so an independent path can check them and the coverage argument.
"""
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import argparse
import json
import platform
import subprocess
import sys
import time


def save(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2)
        stream.write("\n")


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    save(args.out / "manifest.json", {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "command": [sys.executable, *sys.argv], "cwd": str(Path.cwd()),
        "python": platform.python_version(),
        "inputs": {p.as_posix(): digest(p) for p in (Path(__file__), args.input, Path("uv.lock"))},
        "question": "Can every adjacent pair of right cells of the frozen one-cell factor witness pass all known length-two path upper bounds?",
        "scope": "A specific frozen star of four incidence blocks and five internal matchings, with right cells (1,1),(1,2),(2,1),(2,2), respectively. Only each three-cell induced subproblem is tested. This is not all one-cell stars or all rook-containing targets.",
        "selection_rule": "All four rook-adjacent right-cell pairs in lexicographic order; enumerate all 10! perfect matchings for each, using exact sound partial constraints.",
        "success_or_falsification": "Empty domain rejects only the frozen star; otherwise raw perfect matchings witness survival of the separate pair tests. Pairwise survival does not establish a joint completion.",
        "resource_limits": "Four domains, each bounded by 10! permutations. No numerical solver, randomness, or time-based pruning.",
        "thresholds": None, "thresholds_reason": "Integer exact comparisons only.",
        "status": "CANDIDATE", "independent_review_pending": True,
    })
    witness = json.loads(args.input.read_text())
    blocks = [record["incidence_block"] for record in witness["four_factors"]]
    mates = []
    for record in witness["four_factors"]:
        f = [None] * 10
        for x, y in record["partner_matching"]:
            f[x], f[y] = y, x
        assert None not in f
        mates.append(f)
    coordinates = [(1, 1), (1, 2), (2, 1), (2, 2)]
    results = []
    for j, k in combinations(range(4), 2):
        if not any(a == b for a, b in zip(coordinates[j], coordinates[k])):
            continue
        c, d = blocks[j], blocks[k]
        f, g = mates[j], mates[k]
        middle = [[sum(c[x][y] * d[x][z] for x in range(10)) for z in range(10)] for y in range(10)]
        # For p(y)=z, these are precisely the pair constraints independent of
        # other entries of p. The other nonedge constraint can only conflict
        # when a matching pair maps to a matching pair.
        allowed = []
        for y in range(10):
            choices = []
            for z in range(10):
                if max(middle[y][z], middle[f[y]][z], middle[y][g[z]]) > 1:
                    continue
                if any(c[x ^ 1][y] + c[x][f[y]] + d[x][z] > 2 - c[x][y] for x in range(10)):
                    continue
                if any(d[x ^ 1][z] + d[x][g[z]] + c[x][y] > 2 - d[x][z] for x in range(10)):
                    continue
                choices.append(z)
            allowed.append(choices)
        # Always assign one complete internal matching pair at a time. This
        # permits the remaining two-term test to be checked without guessing.
        pairs = []
        seen = set()
        for y in range(10):
            if y not in seen:
                pairs.append((y, f[y]))
                seen.update(pairs[-1])
        pairs.sort(key=lambda pair: len(allowed[pair[0]]) * len(allowed[pair[1]]))
        current = [-1] * 10
        domains = []
        nodes = [0] * 6
        def visit(level, used):
            nodes[level] += 1
            if level == 5:
                domains.append(current.copy())
                return
            y, yy = pairs[level]
            for z in allowed[y]:
                if (1 << z) & used:
                    continue
                for zz in allowed[yy]:
                    if zz == z or (1 << zz) & used:
                        continue
                    if zz == g[z] and (middle[y][zz] or middle[yy][z]):
                        continue
                    current[y], current[yy] = z, zz
                    visit(level + 1, used | (1 << z) | (1 << zz))
                    current[y] = current[yy] = -1
        visit(0, 0)
        path = args.out / f"pair_{j}_{k}.json"
        payload = {"right_cell_indices": [j, k], "coordinates": [coordinates[j], coordinates[k]],
                   "allowed_unary_columns": allowed, "assignment_pairs": pairs,
                   "search_nodes_by_assigned_pair_count": nodes, "complete_domain": True,
                   "permutation_count": len(domains), "permutations": domains}
        save(path, payload)
        results.append({"pair": [j, k], "permutation_count": len(domains), "artifact": path.as_posix(), "sha256": digest(path)})
        print(json.dumps(results[-1]), flush=True)
    save(args.out / "summary.json", {"timestamp": datetime.now(timezone.utc).isoformat(),
         "status": "CANDIDATE", "independent_review_pending": True,
         "population": "four rook-adjacent right-cell pairs in one frozen star", "completed_pairs": len(results),
         "empty_domains": sum(row["permutation_count"] == 0 for row in results), "pair_results": results,
         "scope_exclusion_candidate": any(row["permutation_count"] == 0 for row in results),
         "target_exclusion": False, "elapsed_seconds": time.monotonic() - start})


if __name__ == "__main__":
    main()
