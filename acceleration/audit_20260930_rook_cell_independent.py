"""Independent exact audit of raw rook-cell witness and optional factor census.

No research producer, numerical library, or prior graph checker is imported.
Census completeness uses subset path counts and set partitions, not the
producer's permutation/cycle enumeration. Reports refuse existing paths.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import copy
from datetime import datetime, timezone
from functools import cache
import hashlib
from importlib.metadata import version
import itertools
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

from tqdm import tqdm


def require(condition, why):
    if not condition:
        raise ValueError(why)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def perfect_matching(pairs, n):
    require(len(pairs) * 2 == n, "wrong matching cardinality")
    require(all(len(p) == 2 and all(type(v) is int for v in p) for p in pairs), "bad matching pairs")
    require(sorted(v for p in pairs for v in p) == list(range(n)), "matching is not a partition")
    return {tuple(sorted(p)) for p in pairs}


def factor_type(mask, edges, n):
    require(type(mask) is int and 0 <= mask < 1 << len(edges), "mask outside allowed universe")
    require(mask.bit_count() == n, "wrong factor edge cardinality")
    adjacency = [set() for _ in range(n)]
    selected = set()
    while mask:
        least = mask & -mask
        u, v = edges[least.bit_length() - 1]
        mask -= least
        adjacency[u].add(v)
        adjacency[v].add(u)
        selected.add((u, v))
    require(all(len(row) == 2 for row in adjacency), "factor has wrong degree")
    unseen = set(range(n))
    sizes = []
    while unseen:
        todo = [unseen.pop()]
        size = 0
        while todo:
            u = todo.pop()
            size += 1
            neighbors = adjacency[u] & unseen
            unseen.difference_update(neighbors)
            todo.extend(neighbors)
        require(size >= 3, "short factor component")
        sizes.append(size)
    return tuple(sorted(sizes)), selected


def gram(matrix):
    return [[sum(x * y for x, y in zip(row, other)) for other in matrix]
            for row in matrix]


def check_witness(raw):
    n = 10
    forbidden = perfect_matching(raw["matching"], n)
    edges = [p for p in itertools.combinations(range(n), 2) if p not in forbidden]
    require(len(raw["four_factors"]) == 4, "need four factors")
    covered = set()
    total = [[0] * n for _ in range(n)]
    partitions = []
    for factor in raw["four_factors"]:
        typ, selected = factor_type(int(factor["mask"], 16), edges, n)
        listed = factor["factor_edges"]
        require(len(listed) == n and len({tuple(p) for p in listed}) == n, "bad edge listing")
        require({tuple(p) for p in listed} == selected, "mask/edge listing mismatch")
        require(not covered & selected, "factors overlap")
        covered |= selected
        matrix = factor["incidence_block"]
        require(len(matrix) == n and all(len(row) == n for row in matrix), "wrong incidence shape")
        require(all(type(x) is int and x in (0, 1) for row in matrix for x in row), "nonbinary incidence")
        require(all(sum(row) == 2 for row in matrix), "wrong incidence row sum")
        transpose = list(map(list, zip(*matrix)))
        require(all(sum(row) == 2 for row in transpose), "wrong incidence column sum")
        require([{i for i, x in enumerate(col) if x} for col in transpose]
                == [set(p) for p in listed], "columns are not declared edge incidences")
        g = gram(matrix)
        require(all(g[i][j] == (2 if i == j else int(tuple(sorted((i, j))) in selected))
                    for i in range(n) for j in range(n)), "wrong individual Gram matrix")
        right = perfect_matching(factor["partner_matching"], n)
        right_gram = gram(transpose)
        require(all(right_gram[u][v] == 0 for u, v in right), "right matching forms a triangle")
        for i in range(n):
            for j in range(n):
                total[i][j] += g[i][j]
        partitions.append(list(typ))
    require(covered == set(edges), "incomplete factor partition")
    expected = [[7 * (i == j) + 1 - int(tuple(sorted((i, j))) in forbidden)
                 for j in range(n)] for i in range(n)]
    require(total == expected, "nonzero diagonal-block residual")
    require(raw["sum_C_C_transpose"] == total, "saved total does not reproduce")
    return {"identity": "sum C_j C_j^T = 7 I + J - F", "matrix_entries_checked": n * n,
            "factor_cycle_partitions": partitions, "right_matchings_checked": 4,
            "residual_nonzero_count": 0}


def cycle_counts(n, forbidden):
    """Hamilton cycles on every vertex subset, via rooted directed paths / 2."""
    result = {}
    for root in range(n):
        paths = defaultdict(int)
        paths[(1 << root, root)] = 1
        for subset in range(1 << root, 1 << n):
            if not subset & (1 << root) or subset & ((1 << root) - 1):
                continue
            if subset.bit_count() >= 3:
                oriented = sum(paths[(subset, end)] for end in range(root + 1, n)
                               if subset & (1 << end) and (root, end) not in forbidden)
                require(oriented % 2 == 0, "cycle reversal pairing failed")
                result[subset] = oriented // 2
            for end in range(root, n):
                count = paths.get((subset, end), 0)
                if not count:
                    continue
                for following in range(root + 1, n):
                    if (not subset & (1 << following)
                            and tuple(sorted((end, following))) not in forbidden):
                        paths[(subset | (1 << following), following)] += count
    return result


def independent_factor_counts(n, forbidden):
    cycles = cycle_counts(n, forbidden)

    @cache
    def partitions(remaining):
        if not remaining:
            return {(): 1}
        anchor = remaining & -remaining
        result = Counter()
        subset = remaining
        while subset:
            if subset & anchor and cycles.get(subset, 0):
                for signature, count in partitions(remaining ^ subset).items():
                    result[tuple(sorted((subset.bit_count(), *signature)))] += cycles[subset] * count
            subset = (subset - 1) & remaining
        return dict(result)

    return partitions((1 << n) - 1)


def check_census(lines, expected, n=10, progress=False):
    forbidden = {(i, i + 1) for i in range(0, n, 2)}
    edges = [p for p in itertools.combinations(range(n), 2) if p not in forbidden]
    seen = set()
    counts = Counter()
    for line in tqdm(lines, desc="independent raw factor validation", disable=not progress):
        mask = int(line.strip(), 16)
        require(mask not in seen, "duplicate raw factor")
        seen.add(mask)
        signature, _ = factor_type(mask, edges, n)
        counts[signature] += 1
    require(dict(counts) == expected, "raw census differs from independent exact counts")
    return {"factor_count": len(seen), "counts_by_cycle_partition": {
        "+".join(map(str, key)): value for key, value in sorted(counts.items())}}


def rejection(label, callback):
    try:
        callback()
    except (ValueError, TypeError, KeyError) as exc:
        return {"label": label, "outcome": "REJECTED_AS_REQUIRED", "reason": str(exc)}
    raise AssertionError(f"corrupted control accepted: {label}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    started = time.perf_counter()
    input_dir = Path(args.input)
    raw = json.loads((input_dir / "local_witness.json").read_text())
    controls = []
    witness = check_witness(raw)
    for label, mutate in [
        ("missing factor edge", lambda w: w["four_factors"][0]["factor_edges"].pop()),
        ("changed incidence entry", lambda w: w["four_factors"][0]["incidence_block"][0].__setitem__(0, 0)),
        ("overlapping factors", lambda w: w["four_factors"].__setitem__(1, copy.deepcopy(w["four_factors"][0]))),
        ("matching repeated vertex", lambda w: w["matching"][0].__setitem__(0, 2)),
        ("wrong recorded matrix", lambda w: w["sum_C_C_transpose"][0].__setitem__(0, 9)),
        ("right matching triangle", lambda w: w["four_factors"][0].__setitem__("partner_matching", [[0,1],[2,3],[4,5],[6,7],[8,9]])),
    ]:
        damaged = copy.deepcopy(raw)
        mutate(damaged)
        controls.append(rejection(label, lambda damaged=damaged: check_witness(damaged)))
    known = {3: {(3,): 1}, 4: {(4,): 3}, 5: {(5,): 12}, 6: {(3,3): 10, (6,): 60}}
    for n, expected in known.items():
        require(independent_factor_counts(n, set()) == expected, f"complete K{n} control failed")
    complete10 = {(10,):181440, (3,7):43200, (4,6):37800, (5,5):18144, (3,3,4):6300}
    require(independent_factor_counts(10, set()) == complete10, "K10 factorial-formula control failed")
    forbidden = {(i, i + 1) for i in range(0, 10, 2)}
    expected = independent_factor_counts(10, forbidden)
    lines = (input_dir / "factor_masks.txt").read_text().splitlines()
    census = check_census(lines, expected, progress=True)
    controls.append(rejection("duplicate factor list", lambda: check_census([lines[0], lines[0]], expected)))
    controls.append(rejection("missing factors", lambda: check_census([lines[0]], expected)))
    controls.append(rejection("out-of-domain bit", lambda: check_census([hex(1 << 40)[2:]], expected)))
    source_commit = subprocess.run(["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True).stdout.strip()
    inputs = [input_dir / name for name in ["manifest.json", "summary.json", "factor_masks.txt", "local_witness.json"]]
    inputs += [Path("acceleration/theory_20260930_rook_cell_factors.md"), Path("uv.lock"),
               Path("acceleration/results/20260917_independent_review/rook_regular_set_recheck.json")]
    report = {
        "schema_version": 1, "status": "PASS", "timestamp": datetime.now(timezone.utc).isoformat(),
        "verifier": "Codex subagent /root/state_literature_audit",
        "source_commit": source_commit, "command_argv": [sys.executable, *sys.argv],
        "working_directory": str(Path.cwd()),
        "versions": {"python": platform.python_version(), "tqdm": version("tqdm")},
        "checker_sha256": digest(__file__), "input_hashes": {str(p).replace("\\", "/"): digest(p) for p in inputs},
        "witness": witness, "independent_census": census,
        "positive_count_controls": {"K3": 1, "K4": 3, "K5": 12, "K6": 70, "K10":286884},
        "corrupted_controls": controls,
        "claim_bindings": [
            {"id": "C-ROOK-CELL-LOCAL-FACTOR-COMPATIBILITY", "revision": 1,
             "statement": "For every target containing an induced rook9, at each ten-vertex outside cell the four degree-two incidence blocks necessarily obey sum C_j C_j^T=7I+J-F, and the pinned raw witness satisfies this identity with simple binary degree-two blocks and compatible individual right-cell perfect matchings.",
             "scope": "Necessity conditional on rook9 containment, and satisfiability of this one-cell subsystem only."},
            {"id": "C-ROOK-CELL-TWO-FACTOR-CENSUS", "revision": 1,
             "statement": "Exactly 89000 labelled simple spanning two-factors of K10 avoid the fixed matching {(0,1),(2,3),(4,5),(6,7),(8,9)}, and the pinned factor_masks.txt contains each exactly once.",
             "scope": "Complete finite labelled local two-factor universe; not a target graph universe."}
        ],
        "independence": ["No producer or repository research modules imported.",
                         "Raw incidence matrices are multiplied with Python integer dot products.",
                         "Census uses subset Hamilton-path DP and anchored set partition convolution; all raw masks are separately validated.",
                         "Shared trusted components: Python standard library and tqdm progress only; prior verified rook encoding supplies the conditional premise."],
        "limitations": ["No complete H, cross-cell consistency, off-diagonal H^2 equations, target spectrum, target graph, or exclusion is established.",
                        "The local witness does not establish that any rook-containing target exists.",
                        "No nontrivial automorphism assumption; no target-wide coverage measure.",
                        "The written necessity derivation is separate from finite calibration fixtures."],
        "wall_seconds": time.perf_counter() - started
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(report, handle, indent=2)
        handle.write("\n")
    print(json.dumps({"status": "PASS", "witness": witness, "census": census,
                      "corrupted_controls": len(controls), "report": str(out), "sha256": digest(out)}))


if __name__ == "__main__":
    main()
