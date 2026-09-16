"""Compact block-SAT encoding of the canonical C4-fibre ansatz.

Compared with scratch_canonical_sat.py, a common neighbour through a
four-state intermediary fibre is represented by one equality variable,
not four separate conjunction variables.  The incident edge rows are
one-hot, so equality has a particularly small exact encoding.
"""

from __future__ import annotations

import argparse
import itertools
import json
import time
from pathlib import Path

import pycosat

from scratch_canonical_sat import (
    BASES,
    FIBRES,
    SIGNS,
    SUPPORTS,
    VERTS,
    expanded_graph,
    fixed_r,
    verify,
)


class SmallCNF:
    def __init__(self) -> None:
        self.nvars = 0
        self.clauses: list[list[int]] = []
        self.names: dict[int, str] = {}

    def var(self, name: str) -> int:
        self.nvars += 1
        self.names[self.nvars] = name
        return self.nvars

    def add(self, *lits: int) -> None:
        self.clauses.append(list(lits))

    def exact(self, xs: list[int], k: int) -> None:
        """Naive but propagation-strong encoding; here len(xs) <= 8."""
        n = len(xs)
        if k < 0 or k > n:
            self.add()
            return
        # At most k: every (k+1)-subset contains a false literal.
        for ss in itertools.combinations(xs, k + 1):
            self.clauses.append([-x for x in ss])
        # At least k: every (n-k+1)-subset contains a true literal.
        for ss in itertools.combinations(xs, n - k + 1):
            self.clauses.append(list(ss))


def build(stage: str):
    c = SmallCNF()
    dvar: dict[tuple[int, int], int] = {}
    kg_edges: list[tuple[tuple[int, int], tuple[int, int]]] = []
    for q, A in enumerate(BASES):
        for B in BASES[q + 1 :]:
            if set(A).isdisjoint(B):
                kg_edges.append((A, B))
                for x in FIBRES[A]:
                    for y in FIBRES[B]:
                        dvar[min(x, y), max(x, y)] = c.var(f"D:{x}:{y}")

    def dv(x: int, y: int) -> int:
        return dvar[min(x, y), max(x, y)]

    def row(x: int, G: tuple[int, int]) -> list[int]:
        assert SUPPORTS[x].isdisjoint(G)
        return [dv(x, z) for z in FIBRES[G]]

    # Perfect matchings: rows and columns are one-hot.
    for A, B in kg_edges:
        for x in FIBRES[A]:
            c.exact(row(x, B), 1)
        for y in FIBRES[B]:
            c.exact(row(y, A), 1)

    # y <=> the one-hot choices a and b select the same state of G.
    neq = 0

    def equality(a: list[int], b: list[int], name: str) -> int:
        nonlocal neq
        assert len(a) == len(b) == 4
        y = c.var(name)
        neq += 1
        for t in range(4):
            c.add(-a[t], -b[t], y)
        for t in range(4):
            for s in range(4):
                if t != s:
                    c.add(-y, -a[t], -b[s])
        return y

    # Fixed-neighbour versus outside-vertex equations (the sign balance).
    if stage in {"balance", "overlap", "full"}:
        for x in range(84):
            for i in sorted(set(range(7)) - set(SUPPORTS[x])):
                for a in range(2):
                    xs = []
                    for j in sorted(set(range(7)) - set(SUPPORTS[x]) - {i}):
                        G = tuple(sorted((i, j)))
                        for z in FIBRES[G]:
                            if SIGNS[z][i] == a:
                                xs.append(dv(x, z))
                    assert len(xs) == 8
                    c.exact(xs, 2)

    overlap_pairs = 0
    disjoint_pairs = 0
    if stage in {"overlap", "full"}:
        # Pairs from overlapping, distinct fibres.  The only possible common
        # outside neighbours lie in the six fibres disjoint from their union.
        for x in range(84):
            for y in range(x + 1, 84):
                if SUPPORTS[x] == SUPPORTS[y] or not (SUPPORTS[x] & SUPPORTS[y]):
                    continue
                complement = sorted(set(range(7)) - set(SUPPORTS[x] | SUPPORTS[y]))
                ys = []
                for G in itertools.combinations(complement, 2):
                    ys.append(equality(row(x, G), row(y, G), f"eqO:{x}:{y}:{G}"))
                assert len(ys) == 6
                common_symbol = int(any(
                    i in SIGNS[y] and SIGNS[x][i] == SIGNS[y][i]
                    for i in SUPPORTS[x] & SUPPORTS[y]
                ))
                c.exact(ys, 2 - common_symbol)
                overlap_pairs += 1

    if stage == "full":
        # Pairs from disjoint fibres.  Four local terms go through one of the
        # endpoint fibres, three equality terms go through the remaining
        # disjoint fibres, and the last term is the direct adjacency.  Their
        # sum is exactly two (A^2 + A = 12I + 2J - B^T B off diagonal).
        for x in range(84):
            for y in range(x + 1, 84):
                if not SUPPORTS[x].isdisjoint(SUPPORTS[y]):
                    continue
                terms = [dv(x, y)]
                terms.extend(dv(z, y) for z in range(84)
                             if SUPPORTS[z] == SUPPORTS[x] and fixed_r(x, z))
                terms.extend(dv(x, z) for z in range(84)
                             if SUPPORTS[z] == SUPPORTS[y] and fixed_r(y, z))
                complement = sorted(set(range(7)) - set(SUPPORTS[x] | SUPPORTS[y]))
                for G in itertools.combinations(complement, 2):
                    terms.append(equality(row(x, G), row(y, G),
                                          f"eqD:{x}:{y}:{G}"))
                assert len(terms) == 8
                c.exact(terms, 2)
                disjoint_pairs += 1

    meta = {
        "stage": stage,
        "variables": c.nvars,
        "clauses": len(c.clauses),
        "d_variables": len(dvar),
        "equality_variables": neq,
        "kg_edges": len(kg_edges),
        "overlap_pairs": overlap_pairs,
        "disjoint_pairs": disjoint_pairs,
    }
    return c, dvar, meta


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["matching", "balance", "overlap", "full"],
                    default="full")
    ap.add_argument("--dump", action="store_true")
    args = ap.parse_args()
    t0 = time.time()
    c, dvar, meta = build(args.stage)
    meta["build_seconds"] = round(time.time() - t0, 3)
    print(json.dumps(meta, indent=2, sort_keys=True), flush=True)
    if args.dump:
        path = Path(f"scratch_canonical_{args.stage}.cnf")
        with path.open("w", encoding="ascii") as f:
            f.write(f"p cnf {c.nvars} {len(c.clauses)}\n")
            for clause in c.clauses:
                f.write(" ".join(map(str, clause)) + " 0\n")
    t1 = time.time()
    ans = pycosat.solve(c.clauses, vars=c.nvars, verbose=1)
    elapsed = round(time.time() - t1, 3)
    print("solve_result", ans if isinstance(ans, str) else "SAT", flush=True)
    print("solve_seconds", elapsed, flush=True)
    result = {"meta": meta, "solve_result": ans if isinstance(ans, str) else "SAT",
              "solve_seconds": elapsed}
    if isinstance(ans, list):
        check = verify(expanded_graph(ans, dvar))
        result["verification"] = check
        print(json.dumps(check, indent=2, sort_keys=True), flush=True)
        positive = {q for q in ans if q > 0}
        result["selected_D_edges"] = [list(k) for k, q in dvar.items() if q in positive]
    Path(f"scratch_canonical_{args.stage}_result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
