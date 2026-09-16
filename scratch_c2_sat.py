"""Exact SAT encoding of the full C2 involution branch.

Quotient vertices are the 42 triples (i,j,r), where r is the relative sign
of a root-label and the involution complements both signs.  For each pair of
quotient vertices p and c select the identity/crossed C2-invariant matching.
The encoding uses one-way conjunction witnesses plus small at-most counters;
rooted degree equations make the common-neighbour upper bounds exact by the
global wedge count.  Any SAT model is nevertheless expanded and checked.
"""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

from scratch_bp_seed import expand_and_check


class CNF:
    def __init__(self) -> None:
        self.nvars = 0
        self.clauses: list[list[int]] = []

    def var(self) -> int:
        self.nvars += 1
        return self.nvars

    def add(self, *lits: int) -> None:
        self.clauses.append(list(lits))

    def at_most(self, xs: list[int], k: int) -> None:
        """Sinz sequential counter for literals (not just variables)."""
        n = len(xs)
        if k < 0:
            self.add()
            return
        if k == 0:
            for x in xs:
                self.add(-x)
            return
        if k >= n:
            return
        aux = [[self.var() for _ in range(k)] for _ in range(n - 1)]
        for i in range(n - 1):
            self.add(-xs[i], aux[i][0])
        for i in range(1, n - 1):
            self.add(-aux[i - 1][0], aux[i][0])
            for j in range(1, k):
                self.add(-xs[i], -aux[i - 1][j - 1], aux[i][j])
                self.add(-aux[i - 1][j], aux[i][j])
        for i in range(1, n):
            self.add(-xs[i], -aux[i - 1][k - 1])

    def at_least_small(self, xs: list[int], k: int) -> None:
        assert k in (1, 2)
        if k == 1:
            self.clauses.append(xs[:])
        else:
            # At least two iff deleting any one literal leaves a true one.
            for i in range(len(xs)):
                self.clauses.append(xs[:i] + xs[i + 1 :])

    def exact_small(self, xs: list[int], k: int) -> None:
        self.at_most(xs, k)
        self.at_least_small(xs, k)

    def write(self, path: Path) -> None:
        with path.open("w", encoding="ascii") as f:
            f.write(f"p cnf {self.nvars} {len(self.clauses)}\n")
            for clause in self.clauses:
                f.write(" ".join(map(str, clause)) + " 0\n")


def build(mate_type: str):
    quotient = [(i, j, r) for i in range(7) for j in range(i + 1, 7) for r in range(2)]
    qid = {x: k for k, x in enumerate(quotient)}
    c = CNF()
    pvar = {}
    cvar = {}
    for x, y in itertools.combinations(range(42), 2):
        pvar[x, y] = c.var()
        cvar[x, y] = c.var()

    def key(x: int, y: int):
        return (x, y) if x < y else (y, x)

    def p(x: int, y: int):
        return pvar[key(x, y)]

    def cross(x: int, y: int):
        return cvar[key(x, y)]

    def signs(x: int):
        i, j, r = quotient[x]
        return {i: 0, j: r}

    # BP=P A0: it is enough to impose the canonical lift of each quotient
    # row; its tau image gives the complementary equations.
    for x, (i, j, _r) in enumerate(quotient):
        for g in range(7):
            for epsilon in range(2):
                terms = []
                for y in range(42):
                    if y == x or g not in quotient[y][:2]:
                        continue
                    if signs(y)[g] == epsilon:
                        terms.append(p(x, y))
                    else:
                        terms.append(cross(x, y))
                c.exact_small(terms, 1 if g in (i, j) else 2)

    # q[x,y] iff both invariant matchings are selected.  The q-edges are a
    # perfect matching, equivalent to the x--tau(x) common-neighbour rule.
    double = {}
    for x, y in itertools.combinations(range(42), 2):
        q = c.var()
        double[x, y] = q
        c.add(-q, p(x, y))
        c.add(-q, cross(x, y))
        c.add(-p(x, y), -cross(x, y), q)
    for x in range(42):
        c.exact_small([double[key(x, y)] for y in range(42) if y != x], 1)

    x0 = qid[(0, 1, 0)]
    canonical_mate = {
        "same": qid[(0, 1, 1)],
        "overlap": qid[(0, 2, 0)],
        "disjoint": qid[(2, 3, 0)],
    }
    if mate_type != "none":
        c.add(double[key(x0, canonical_mate[mate_type])])

    products = 0

    def lower_and(a: int, b: int) -> int:
        nonlocal products
        q = c.var()
        c.add(-a, -b, q)
        products += 1
        return q

    # Two lift orientations for every distinct quotient pair.  Each upper
    # bound is exact collectively because BP fixes all 84 outer degrees at 12
    # and hence fixes the global sum of wedges.
    for x, y in itertools.combinations(range(42), 2):
        same_terms = [p(x, y)]
        cross_terms = [cross(x, y)]
        for w in range(42):
            if w in (x, y):
                continue
            same_terms.append(lower_and(p(x, w), p(y, w)))
            same_terms.append(lower_and(cross(x, w), cross(y, w)))
            cross_terms.append(lower_and(p(x, w), cross(y, w)))
            cross_terms.append(lower_and(cross(x, w), p(y, w)))
        sx, sy = signs(x), signs(y)
        shared = set(sx) & set(sy)
        s_same = sum(sx[g] == sy[g] for g in shared)
        s_cross = sum(sx[g] != sy[g] for g in shared)
        c.at_most(same_terms, 2 - s_same)
        c.at_most(cross_terms, 2 - s_cross)

    meta = {
        "mate_type": mate_type,
        "variables": c.nvars,
        "clauses": len(c.clauses),
        "block_boolean_variables": 2 * len(pvar),
        "double_variables": len(double),
        "product_variables": products,
    }
    return c, meta


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mate-type", choices=("none", "same", "overlap", "disjoint"), default="none")
    ap.add_argument("--output")
    args = ap.parse_args()
    c, meta = build(args.mate_type)
    out = Path(args.output or f"scratch_c2_{args.mate_type}.cnf")
    c.write(out)
    Path(str(out) + ".json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({**meta, "output": str(out)}, indent=2), flush=True)


if __name__ == "__main__":
    main()
