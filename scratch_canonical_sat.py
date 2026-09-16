"""SAT test for the canonical C4-fibre ansatz for the Conway 99-graph.

Only the 84 vertices outside a fixed vertex and its 14 neighbours are
variables here.  A vertex is (ij, a, b), where ij is a two-subset of
seven matched pairs and a,b are signs.  Every four-vertex fibre ij has
the fixed C4 given by Hamming-distance one.  Between disjoint fibres
(edges of KG(7,2)) the variable graph is required to be a perfect
matching.  All remaining pairs are nonedges.

The CNF below imposes *all* common-neighbour equations involving an
outside vertex, including the equations with the 14 neighbours of the
fixed vertex.  A returned model is independently expanded to the full
99-vertex graph and checked directly.
"""

from __future__ import annotations

import argparse
import itertools
import json
import time
from collections import Counter
from pathlib import Path

import pycosat


class CNF:
    def __init__(self) -> None:
        self.nvars = 0
        self.clauses: list[list[int]] = []
        self.var_names: dict[int, str] = {}

    def var(self, name: str) -> int:
        self.nvars += 1
        self.var_names[self.nvars] = name
        return self.nvars

    def add(self, *lits: int) -> None:
        self.clauses.append(list(lits))

    def at_most(self, xs: list[int], k: int, tag: str) -> None:
        """Sinz sequential-counter encoding of sum(xs) <= k."""
        n = len(xs)
        if k < 0:
            self.add()
            return
        if n <= k:
            return
        if k == 0:
            for x in xs:
                self.add(-x)
            return
        # s[i,j] is a one-way sequential counter, with i=0..n-2 and
        # j=0..k-1.  The standard implication encoding is sufficient.
        s = [[self.var(f"sc:{tag}:{i}:{j}") for j in range(k)]
             for i in range(n - 1)]
        for i in range(n - 1):
            self.add(-xs[i], s[i][0])
        for i in range(1, n - 1):
            self.add(-s[i - 1][0], s[i][0])
        for j in range(1, k):
            for i in range(1, n - 1):
                self.add(-xs[i], -s[i - 1][j - 1], s[i][j])
                self.add(-s[i - 1][j], s[i][j])
        for i in range(1, n):
            self.add(-xs[i], -s[i - 1][k - 1])

    def exact(self, xs: list[int], k: int, tag: str) -> None:
        """Compact encodings for the only cardinalities used here (0,1,2)."""
        n = len(xs)
        if not 0 <= k <= n:
            self.add()
            return
        if k == 0:
            for x in xs:
                self.add(-x)
            return
        if k == n:
            for x in xs:
                self.add(x)
            return
        # At least one.
        self.clauses.append(xs[:])
        if k == 1:
            # Pairwise is smaller for the ubiquitous four-variable matchings;
            # sequential is smaller for the common-neighbour equations.
            if n <= 6:
                for a, b in itertools.combinations(xs, 2):
                    self.add(-a, -b)
            else:
                self.at_most(xs, 1, tag)
            return
        if k == 2:
            # Given at least one, these clauses force every selected literal
            # to have a second selected literal.
            for i, x in enumerate(xs):
                self.clauses.append([-x] + xs[:i] + xs[i + 1 :])
            self.at_most(xs, 2, tag)
            return
        raise ValueError(f"unsupported exact cardinality {k}")


BASES = list(itertools.combinations(range(7), 2))

# Vertex record is (base_i, base_j, sign_i, sign_j), with base_i < base_j.
VERTS = [(i, j, a, b) for i, j in BASES for a in range(2) for b in range(2)]
VID = {v: q for q, v in enumerate(VERTS)}
FIBRES: dict[tuple[int, int], list[int]] = {
    ij: [VID[(ij[0], ij[1], a, b)] for a in range(2) for b in range(2)]
    for ij in BASES
}


def support(x: int) -> frozenset[int]:
    v = VERTS[x]
    return frozenset(v[:2])


SUPPORTS = [support(x) for x in range(84)]


def signs(x: int) -> dict[int, int]:
    i, j, a, b = VERTS[x]
    return {i: a, j: b}


SIGNS = [signs(x) for x in range(84)]


def fixed_r(x: int, y: int) -> bool:
    """The fixed C4 edge inside one fibre."""
    if SUPPORTS[x] != SUPPORTS[y]:
        return False
    sx, sy = SIGNS[x], SIGNS[y]
    return sum(sx[i] != sy[i] for i in SUPPORTS[x]) == 1


def build_cnf(stage: str = "full"):
    cnf = CNF()

    # One possible D-edge variable for every pair of states in every
    # unordered adjacent pair of KG(7,2) fibres.
    dvar: dict[tuple[int, int], int] = {}
    disjoint_fibre_pairs = []
    for fi, A in enumerate(BASES):
        for B in BASES[fi + 1 :]:
            if set(A).isdisjoint(B):
                disjoint_fibre_pairs.append((A, B))
                for x in FIBRES[A]:
                    for y in FIBRES[B]:
                        dvar[(min(x, y), max(x, y))] = cnf.var(f"D:{x}:{y}")

    def edge_status(x: int, y: int):
        """Return True/False for fixed status, or a positive SAT literal."""
        if x == y:
            return False
        key = (min(x, y), max(x, y))
        if key in dvar:
            return dvar[key]
        return fixed_r(x, y)

    # D induces a perfect matching on every KG edge.
    for p, (A, B) in enumerate(disjoint_fibre_pairs):
        for x in FIBRES[A]:
            cnf.exact([dvar[(min(x, y), max(x, y))] for y in FIBRES[B]],
                      1, f"pm:{p}:A:{x}")
        for y in FIBRES[B]:
            cnf.exact([dvar[(min(x, y), max(x, y))] for x in FIBRES[A]],
                      1, f"pm:{p}:B:{y}")

    # Equations for a 14-neighbour symbol versus an outside vertex.
    # For every base coordinate absent from x, its four D-neighbours whose
    # fibres contain that coordinate must split 2+2 between the two signs.
    if stage in {"balance", "overlap", "full"}:
        for x in range(84):
            absent = sorted(set(range(7)) - set(SUPPORTS[x]))
            for i in absent:
                for a in range(2):
                    lits = []
                    for y in range(84):
                        if i in SUPPORTS[y] and SIGNS[y][i] == a:
                            st = edge_status(x, y)
                            if isinstance(st, int) and not isinstance(st, bool):
                                lits.append(st)
                    # Four disjoint fibres, two target states in each.
                    assert len(lits) == 8
                    cnf.exact(lits, 2, f"bal:{x}:{i}:{a}")

    aux_cache: dict[tuple[int, int], int] = {}

    def conjunction(a: int, b: int) -> int:
        # Sharing identical products between equations is harmless and cuts
        # the CNF substantially.  The inputs are always positive edge vars.
        key = (min(a, b), max(a, b))
        if key not in aux_cache:
            t = cnf.var(f"and:{key[0]}:{key[1]}")
            aux_cache[key] = t
            cnf.add(-a, -b, t)
            cnf.add(a, -t)
            cnf.add(b, -t)
        return aux_cache[key]

    def common_terms(x: int, y: int):
        constant = 0
        terms: list[int] = []
        for z in range(84):
            if z == x or z == y:
                continue
            a, b = edge_status(x, z), edge_status(y, z)
            if a is False or b is False:
                continue
            if a is True and b is True:
                constant += 1
            elif a is True:
                assert isinstance(b, int) and not isinstance(b, bool)
                terms.append(b)
            elif b is True:
                assert isinstance(a, int) and not isinstance(a, bool)
                terms.append(a)
            else:
                assert isinstance(a, int) and not isinstance(a, bool)
                assert isinstance(b, int) and not isinstance(b, bool)
                terms.append(conjunction(a, b))
        return constant, terms

    pair_kinds = Counter()
    if stage in {"overlap", "full"}:
        for x in range(84):
            for y in range(x + 1, 84):
                same_fibre = SUPPORTS[x] == SUPPORTS[y]
                overlap = bool(SUPPORTS[x] & SUPPORTS[y])
                if stage == "overlap" and (same_fibre or not overlap):
                    continue

                # Number of common vertices among the fixed 14 neighbours.
                common_symbols = len(
                    {(i, a) for i, a in SIGNS[x].items()}
                    & {(i, a) for i, a in SIGNS[y].items()}
                )
                direct = edge_status(x, y)
                const_cn, terms = common_terms(x, y)
                if isinstance(direct, int) and not isinstance(direct, bool):
                    # CN_H + CN_fixed14 + adjacency = 2.
                    terms.append(direct)
                    rhs = 2 - common_symbols - const_cn
                    kind = "disjoint"
                else:
                    rhs = 2 - common_symbols - int(direct) - const_cn
                    if same_fibre:
                        kind = "same"
                    elif overlap:
                        kind = "overlap"
                    else:
                        kind = "forbidden-disjoint"
                pair_kinds[(kind, rhs, len(terms), const_cn)] += 1
                cnf.exact(terms, rhs, f"cn:{x}:{y}")

    meta = {
        "stage": stage,
        "base_fibres": len(BASES),
        "outside_vertices": len(VERTS),
        "kg_edges": len(disjoint_fibre_pairs),
        "d_variables": len(dvar),
        "variables": cnf.nvars,
        "clauses": len(cnf.clauses),
        "and_variables": len(aux_cache),
        "pair_kinds": {str(k): v for k, v in sorted(pair_kinds.items(), key=str)},
    }
    return cnf, dvar, edge_status, meta


def expanded_graph(model: list[int], dvar: dict[tuple[int, int], int]):
    """Expand a satisfying assignment to vertices 0..98 for direct checking."""
    positive = {q for q in model if q > 0}
    adj = [set() for _ in range(99)]

    def add(u: int, v: int) -> None:
        adj[u].add(v)
        adj[v].add(u)

    root = 0
    # Fixed root neighbourhood: symbols (base,sign) map to 1..14.
    sym = {(i, a): 1 + 2 * i + a for i in range(7) for a in range(2)}
    for q in sym.values():
        add(root, q)
    for i in range(7):
        add(sym[i, 0], sym[i, 1])

    # Outside vertices map to 15..98.
    for x in range(84):
        X = 15 + x
        for i, a in SIGNS[x].items():
            add(X, sym[i, a])
    for x in range(84):
        for y in range(x + 1, 84):
            key = (x, y)
            if fixed_r(x, y) or (key in dvar and dvar[key] in positive):
                add(15 + x, 15 + y)
    return adj


def verify(adj: list[set[int]]) -> dict:
    degrees = [len(a) for a in adj]
    histogram = Counter()
    failures = []
    for u in range(99):
        for v in range(u + 1, 99):
            c = len(adj[u] & adj[v])
            histogram[(v in adj[u], c)] += 1
            wanted = 1 if v in adj[u] else 2
            if c != wanted and len(failures) < 20:
                failures.append((u, v, v in adj[u], c, wanted))
    return {
        "edges": sum(degrees) // 2,
        "degree_histogram": dict(sorted(Counter(degrees).items())),
        "pair_histogram": {str(k): v for k, v in sorted(histogram.items())},
        "failures": failures,
        "ok": degrees == [14] * 99 and not failures,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["matching", "balance", "overlap", "full"],
                    default="full")
    ap.add_argument("--dump", action="store_true", help="write scratch_canonical.cnf")
    args = ap.parse_args()

    t0 = time.time()
    cnf, dvar, _, meta = build_cnf(args.stage)
    meta["build_seconds"] = round(time.time() - t0, 3)
    print(json.dumps(meta, indent=2, sort_keys=True))
    if args.dump:
        path = Path("scratch_canonical.cnf")
        with path.open("w", encoding="ascii") as f:
            f.write(f"p cnf {cnf.nvars} {len(cnf.clauses)}\n")
            for clause in cnf.clauses:
                f.write(" ".join(map(str, clause)) + " 0\n")

    t1 = time.time()
    ans = pycosat.solve(cnf.clauses, vars=cnf.nvars, verbose=1)
    print("solve_result", ans if isinstance(ans, str) else "SAT")
    print("solve_seconds", round(time.time() - t1, 3))
    if isinstance(ans, list):
        adj = expanded_graph(ans, dvar)
        result = verify(adj)
        print(json.dumps(result, indent=2, sort_keys=True))
        # Keep any candidate away from submission.txt as requested.
        edges = [(u + 1, v + 1) for u in range(99) for v in adj[u] if u < v]
        Path("scratch_canonical_candidate.json").write_text(
            json.dumps({"verify": result, "edges": edges}, indent=2),
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
