"""Enumerate one-cell necessary factors for the conditional rook-nine model.

This is a discovery producer. It never promotes its own output to VERIFIED.
The finite universe is simple spanning two-factors on ten labelled vertices
avoiding the fixed matching (0,1),(2,3),...,(8,9). No graph symmetry is assumed.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
from itertools import combinations, permutations
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

from tqdm import tqdm


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def save(path: Path, obj: object) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(obj, stream, indent=2)
        stream.write("\n")


def factors(vertices: tuple[int, ...]):
    """Unique cycle decomposition: least unused vertex first, canonical direction."""
    if not vertices:
        yield ()
        return
    first, *rest = vertices
    for length in range(3, len(vertices) + 1):
        if len(vertices) - length in (1, 2):
            continue
        for chosen in combinations(rest, length - 1):
            remaining = tuple(v for v in rest if v not in chosen)
            for ordered in permutations(chosen):
                if ordered[0] >= ordered[-1]:
                    continue
                cycle = (first, *ordered)
                if any((cycle[t] ^ 1) == cycle[(t + 1) % length] for t in range(length)):
                    continue
                for suffix in factors(remaining):
                    yield (cycle, *suffix)


def cycle_edges(cycles):
    return sorted(tuple(sorted((cyc[t], cyc[(t + 1) % len(cyc)])))
                  for cyc in cycles for t in range(len(cyc)))


def perfect_matching_away(adjacency):
    def visit(left):
        if not left:
            return []
        first = left[0]
        for other in left[1:]:
            if adjacency[first][other]:
                continue
            tail = visit([v for v in left[1:] if v != other])
            if tail is not None:
                return [(first, other), *tail]
        return None
    return visit(list(range(10)))


def matrix_product(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(len(b)))
             for j in range(len(b[0]))] for i in range(len(a))]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    manifest = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "command": [sys.executable, *sys.argv], "cwd": str(Path.cwd()),
        "versions": {"python": platform.python_version(), "uv": subprocess.check_output(["uv", "--version"], text=True).strip()},
        "input_hashes": {p.as_posix(): digest(p) for p in (Path(__file__), Path("uv.lock"), Path("acceleration/theory_20260930_rook_cell_factors.md"))},
        "question": "Do the one-cell diagonal block equations of the conditional rook-nine representation already contradict integer two-factor structure?",
        "scope": "Only four two-factors on ten labelled vertices; no cross-cell off-diagonal equation or unrestricted target coverage.",
        "selection_rule": "Enumerate all simple two-factors avoiding the fixed internal matching; retain first disjoint triple with a two-factor complement as a local witness.",
        "success_criteria": "Exact factor census and an explicitly verified four-factor partition, or a complete finite exhaustion if no partition exists.",
        "falsification_criteria": "Any wrong degree, repeated edge, forbidden matching edge, or nonzero claimed integer matrix residual rejects the witness.",
        "numeric_thresholds": None, "numeric_thresholds_reason": "All computations use Python integers, no numerical acceptance threshold.",
        "resource_limits": "Fixed finite universe of at most 286884 unfiltered two-factors, no solver or graph search beyond the local factors.",
        "random_seed": None, "random_seed_reason": "Deterministic enumeration.",
        "status": "CANDIDATE", "independent_review_pending": True,
    }
    save(args.out / "manifest.json", manifest)
    allowed = [(i, j) for i in range(10) for j in range(i + 1, 10) if j != (i ^ 1)]
    bit = {edge: 1 << k for k, edge in enumerate(allowed)}
    domain = []
    census = Counter()
    domain_path = args.out / "factor_masks.txt"
    with domain_path.open("x", encoding="ascii", newline="\n") as stream:
        for decomposition in tqdm(factors(tuple(range(10))), desc="Rook-cell factors", unit="factor"):
            mask = sum(bit[e] for e in cycle_edges(decomposition))
            domain.append(mask)
            census[tuple(sorted(map(len, decomposition)))] += 1
            stream.write(f"{mask:010x}\n")
    assert len(domain) == len(set(domain)), "duplicate labelled factor"
    full = (1 << len(allowed)) - 1
    first = domain[0]
    second = next(mask for mask in domain if not mask & first)
    third = next(mask for mask in domain if not mask & (first | second))
    fourth = full ^ (first | second | third)
    assert fourth in set(domain)
    selected = [first, second, third, fourth]
    records = []
    square_sum = [[0] * 10 for _ in range(10)]
    for mask in selected:
        edges = [e for e in allowed if bit[e] & mask]
        c = [[int(v in e) for e in edges] for v in range(10)]
        ct = list(map(list, zip(*c)))
        left = matrix_product(c, ct)
        right = matrix_product(ct, c)
        partner_matching = perfect_matching_away(right)
        assert partner_matching is not None
        assert all(sum(row) == 2 for row in c)
        assert all(sum(row) == 2 for row in ct)
        assert all(left[i][i ^ 1] == 0 for i in range(10))
        assert all(right[i][j] == 0 for i, j in partner_matching)
        for i in range(10):
            for j in range(10):
                square_sum[i][j] += left[i][j]
        records.append({"mask": f"{mask:010x}", "factor_edges": edges,
                        "incidence_block": c, "partner_matching": partner_matching})
    expected = [[8 if i == j else 0 if j == (i ^ 1) else 1 for j in range(10)] for i in range(10)]
    assert square_sum == expected
    witness = {"matching": [[i, i + 1] for i in range(0, 10, 2)],
               "four_factors": records, "sum_C_C_transpose": square_sum,
               "identity": "sum_j C_ij C_ij^T = 7I + J - F_i",
               "claim": "An exact one-cell witness only; not a partial or complete target graph."}
    save(args.out / "local_witness.json", witness)
    summary = {"timestamp": datetime.now(timezone.utc).isoformat(), "status": "CANDIDATE",
               "enumeration_complete": True, "unit": "distinct labelled simple spanning two-factors avoiding five fixed matching edges",
               "labelled_factor_count": len(domain), "counts_by_cycle_partition": {"+".join(map(str, k)): v for k, v in sorted(census.items())},
               "local_four_factor_witness": True, "one_cell_diagonal_residual_zero": True,
               "target_exclusion": False, "target_graph": False, "independent_review_pending": True,
               "wall_seconds": time.monotonic() - started,
               "output_hashes": {p.name: digest(p) for p in (domain_path, args.out / "local_witness.json", args.out / "manifest.json")}}
    save(args.out / "summary.json", summary)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
