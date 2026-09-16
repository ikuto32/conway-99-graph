"""Second-generation SAT experiment for the canonical C4-fibre ansatz.

This is deliberately a *restricted* Conway-99 experiment.  The C4 inside
each four-vertex fibre is an extra ansatz; it is not known to be WLOG for a
general srg(99,14,1,2).

Relative to scratch_canonical_blocksat.py this version

* shares two output bits per directed permutation row and uses an 8-clause
  equality gadget (rather than 16 cell-level clauses),
* removes the complementary duplicate of every sign-balance equation,
* omits redundant column-at-least-one clauses in permutation matrices,
* exhausts a safe D8-double-orbit normalization of two S4 matchings.

At the first matching there are two exhaustive families:

``d8``
    Some matching is a C4 automorphism.  Move that KG(7,2) edge to
    01--23 and normalize the matching to the identity.

``nond8``
    No matching is a C4 automorphism.  Normalize 01--23 to a representative
    of the other D8 double coset and require every matching to be non-D8.

The residual action on a second matching splits ``d8`` into ``d8_qd8`` and
``d8_qnond8``.  In the ``nond8`` family all matchings are non-D8; its two
remaining second-matching orbits are ``nond8_q1`` and ``nond8_q2``.  These
four branches are exhaustive.  UNSAT of all four settles only this canonical
ansatz.
Any SAT result is expanded to 99 vertices and checked from scratch.
No code in this file writes submission.txt.
"""

from __future__ import annotations

import argparse
import itertools
import json
import threading
import time
from collections import Counter
from pathlib import Path


BASES = list(itertools.combinations(range(7), 2))
VERTS = [(i, j, a, b) for i, j in BASES for a in range(2) for b in range(2)]
VID = {v: q for q, v in enumerate(VERTS)}
FIBRES: dict[tuple[int, int], list[int]] = {
    ij: [VID[(ij[0], ij[1], a, b)] for a in range(2) for b in range(2)]
    for ij in BASES
}
SUPPORTS = [frozenset(v[:2]) for v in VERTS]
SIGNS = [{v[0]: v[2], v[1]: v[3]} for v in VERTS]


def fixed_r(x: int, y: int) -> bool:
    """The fixed C4 edge inside one fibre."""
    if SUPPORTS[x] != SUPPORTS[y]:
        return False
    return sum(SIGNS[x][i] != SIGNS[y][i] for i in SUPPORTS[x]) == 1


class CNF:
    def __init__(self) -> None:
        self.nvars = 0
        self.clauses: list[list[int]] = []

    def var(self) -> int:
        self.nvars += 1
        return self.nvars

    def add(self, *lits: int) -> None:
        self.clauses.append(list(lits))

    def at_most_one(self, xs: list[int]) -> None:
        for a, b in itertools.combinations(xs, 2):
            self.add(-a, -b)

    def exactly_one(self, xs: list[int]) -> None:
        self.clauses.append(xs[:])
        self.at_most_one(xs)

    def exact(self, xs: list[int], k: int) -> None:
        """Propagation-strong subset encoding; all uses have len(xs) <= 8."""
        n = len(xs)
        if not 0 <= k <= n:
            self.add()
            return
        for ss in itertools.combinations(xs, k + 1):
            self.clauses.append([-x for x in ss])
        for ss in itertools.combinations(xs, n - k + 1):
            self.clauses.append(list(ss))


def transform_vertex(x: int, coord_perm: tuple[int, ...]) -> int:
    """Image of an outside vertex under a permutation of the 7 coordinates."""
    image_signs = {coord_perm[i]: a for i, a in SIGNS[x].items()}
    i, j = sorted(image_signs)
    return VID[(i, j, image_signs[i], image_signs[j])]


def add_lex_leader(
    c: CNF,
    ordered_vars: list[int],
    image_vars: list[int],
) -> int:
    """Encode ordered_vars <=lex image_vars, with False < True.

    Equal coordinates are dropped first.  Prefix variables are full
    equivalences, not one-way hints, so every forbidden first 1/0 mismatch is
    excluded.  Returns the number of auxiliary variables introduced.
    """
    pairs = [(x, y) for x, y in zip(ordered_vars, image_vars) if x != y]
    if not pairs:
        return 0
    made = 0
    prefix: int | None = None
    for q, (x, y) in enumerate(pairs):
        if prefix is None:
            c.add(-x, y)
        else:
            c.add(-prefix, -x, y)
        if q == len(pairs) - 1:
            break
        nxt = c.var()
        made += 1
        if prefix is None:
            # nxt <=> (x == y)
            c.add(-nxt, -x, y)
            c.add(-nxt, x, -y)
            c.add(-x, -y, nxt)
            c.add(x, y, nxt)
        else:
            # nxt <=> prefix & (x == y)
            c.add(-nxt, prefix)
            c.add(-nxt, -x, y)
            c.add(-nxt, x, -y)
            c.add(-prefix, -x, -y, nxt)
            c.add(-prefix, x, y, nxt)
        prefix = nxt
    return made


FIRST_D8_BRANCHES = {"d8", "d8_qd8", "d8_qnond8"}
FIRST_NOND8_BRANCHES = {
    "nond8", "nond8_q1", "nond8_q2",
}
SECOND_BRANCHES = {
    "d8_qd8", "d8_qnond8", "nond8_q1", "nond8_q2",
}


def all_permutations() -> list[tuple[int, ...]]:
    return list(itertools.permutations(range(4)))


def compose_perm(p: tuple[int, ...], q: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(p[q[i]] for i in range(4))


def inverse_perm(p: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(p.index(i) for i in range(4))


def d8_group() -> set[tuple[int, ...]]:
    translations = [tuple(i ^ t for i in range(4)) for t in range(4)]
    swap = (0, 2, 1, 3)
    return set(translations) | {compose_perm(swap, t) for t in translations}


def double_orbits(right: set[tuple[int, ...]]) -> list[set[tuple[int, ...]]]:
    """Orbits H p right, where H=D8 acts on the target states."""
    left = d8_group()
    unseen = set(all_permutations())
    answer = []
    while unseen:
        rep = min(unseen)
        orbit = {
            compose_perm(compose_perm(h, rep), k)
            for h in left for k in right
        }
        answer.append(orbit)
        unseen -= orbit
    return answer


def build(stage: str, branch: str, lex: bool = True):
    c = CNF()
    dvar: dict[tuple[int, int], int] = {}
    kg_edges: list[tuple[tuple[int, int], tuple[int, int]]] = []
    for q, A in enumerate(BASES):
        for B in BASES[q + 1 :]:
            if set(A).isdisjoint(B):
                kg_edges.append((A, B))
                for x in FIBRES[A]:
                    for y in FIBRES[B]:
                        dvar[min(x, y), max(x, y)] = c.var()

    def dv(x: int, y: int) -> int:
        return dvar[min(x, y), max(x, y)]

    def row(x: int, G: tuple[int, int]) -> list[int]:
        assert SUPPORTS[x].isdisjoint(G)
        return [dv(x, z) for z in FIBRES[G]]

    # Four exactly-one rows give four selected cells.  Column at-most-one then
    # implies (and is smaller than explicitly encoding) column exactly-one.
    for A, B in kg_edges:
        for x in FIBRES[A]:
            c.exactly_one(row(x, B))
        for y in FIBRES[B]:
            c.at_most_one(row(y, A))

    def fix_matching(A: tuple[int, int], B: tuple[int, int],
                     perm: tuple[int, ...] | list[int]) -> None:
        for s, t in enumerate(perm):
            c.add(dv(FIBRES[A][s], FIBRES[B][t]))

    def require_nond8(A: tuple[int, int], B: tuple[int, int]) -> None:
        # A permutation of the square is in D8 iff it maps the opposite pair
        # (state 0,state 3) to an opposite pair.
        for t in range(4):
            c.add(-dv(FIBRES[A][0], FIBRES[B][t]),
                  -dv(FIBRES[A][3], FIBRES[B][t ^ 3]))

    def require_orbit(A: tuple[int, int], B: tuple[int, int],
                      allowed: set[tuple[int, ...]]) -> None:
        # With row/column permutation constraints, four negative literals
        # forbid exactly one S4 permutation.
        for p in all_permutations():
            if p not in allowed:
                c.add(*[-dv(FIBRES[A][s], FIBRES[B][p[s]])
                        for s in range(4)])

    scaffold_clauses_before = len(c.clauses)
    if branch != "none":
        A, B = (0, 1), (2, 3)
        # Representatives of the two D8 \\ S4 / D8 double cosets.
        first_d8 = branch in FIRST_D8_BRANCHES
        if not first_d8 and branch not in FIRST_NOND8_BRANCHES:
            raise ValueError(f"unknown symmetry branch {branch!r}")
        first_rep = (0, 1, 2, 3) if first_d8 else (0, 3, 2, 1)
        fix_matching(A, B, first_rep)

        if not first_d8:
            # If there is any D8 matching, the first family covers the model
            # after moving that KG edge to 01--23.  Consequently the other
            # exhaustive family may require all 105 matchings to be non-D8.
            for U, V in kg_edges:
                require_nond8(U, V)

        if branch in SECOND_BRANCHES:
            C = (4, 5)
            remaining_fibres = ((4, 5), (4, 6), (5, 6))
            if first_d8:
                # The diagonal D8 stabilizer of the identity on 01--23 and
                # the independent D8 on C give two double orbits for 01--C.
                if branch == "d8_qd8":
                    second_rep = (0, 1, 2, 3)
                else:
                    second_rep = (0, 1, 3, 2)
                    # Use residual S3 to choose a non-D8 member among the
                    # three remaining-coordinate fibres.  This branch is
                    # reached only if none of the three is D8.
                    for G in remaining_fibres:
                        require_nond8(A, G)
            else:
                H = d8_group()
                t = tuple(first_rep)
                tinv = inverse_perm(t)
                # Projection to the 01 states of the stabilizer of t under
                # D8 x D8.  It has order four for the non-D8 representative.
                right = {
                    a for a in H
                    if compose_perm(compose_perm(t, a), tinv) in H
                }
                orbits = double_orbits(right)
                assert [len(o) for o in orbits] == [8, 8, 8]
                qi = {"nond8_q1": 1, "nond8_q2": 2}[branch]
                second_rep = min(orbits[qi])
                # Hierarchical use of residual S3: choose the lowest orbit
                # occurring among 45,46,56 and move it to 45.
                if qi >= 1:
                    for G in remaining_fibres:
                        require_orbit(A, G, orbits[1] | orbits[2])
                if qi >= 2:
                    for G in remaining_fibres:
                        require_orbit(A, G, orbits[2])
            fix_matching(A, C, second_rep)

            # Only the sign flip of coordinate 6 is still unused.  Normalize
            # the 6-sign of the selected neighbour of state 00 in fibre 26.
            x0 = FIBRES[A][0]
            G = (2, 6)
            c.add(dv(x0, FIBRES[G][0]), dv(x0, FIBRES[G][2]))
        else:
            # Lightweight normalization retained for the two coarse/debug
            # branches.
            x0 = FIBRES[(0, 1)][0]
            for k in (4, 5, 6):
                G = (2, k)
                c.add(dv(x0, FIBRES[G][0]), dv(x0, FIBRES[G][2]))

    scaffold_clauses = len(c.clauses) - scaffold_clauses_before

    lex_aux = 0
    lex_generators = 0
    if lex and branch in {"d8", "nond8"}:
        # The scaffold leaves S3 on coordinates 4,5,6.  A lexicographically
        # least member of every residual orbit satisfies these generator
        # inequalities, hence both constraints are WLOG.
        ordered = list(range(1, len(dvar) + 1))
        for a, b in ((4, 5), (5, 6)):
            p = list(range(7))
            p[a], p[b] = p[b], p[a]
            perm7 = tuple(p)
            image = []
            for (x, y), _var in sorted(dvar.items(), key=lambda kv: kv[1]):
                xx, yy = transform_vertex(x, perm7), transform_vertex(y, perm7)
                image.append(dvar[min(xx, yy), max(xx, yy)])
            lex_aux += add_lex_leader(c, ordered, image)
            lex_generators += 1

    # Boolean output coordinates of every directed permutation row.  Under
    # exactly-one(row), one output bit is the OR of precisely two cells.
    bit_cache: dict[tuple[int, tuple[int, int], int], int] = {}

    def selected_bit(x: int, G: tuple[int, int], coord: int) -> int:
        key = (x, G, coord)
        if key not in bit_cache:
            assert coord in G and SUPPORTS[x].isdisjoint(G)
            y = c.var()
            ones = [dv(x, z) for z in FIBRES[G] if SIGNS[z][coord] == 1]
            assert len(ones) == 2
            for cell in ones:
                c.add(-cell, y)
            c.add(-y, *ones)
            bit_cache[key] = y
        return bit_cache[key]

    neq = 0

    def equality(x: int, y: int, G: tuple[int, int]) -> int:
        """q iff the two selected two-bit states in G are equal."""
        nonlocal neq
        q = c.var()
        neq += 1
        abits = [selected_bit(x, G, i) for i in G]
        bbits = [selected_bit(y, G, i) for i in G]
        # q implies equality of each output bit.
        for a, b in zip(abits, bbits):
            c.add(-q, -a, b)
            c.add(-q, a, -b)
        # Each of the four equal two-bit words implies q.
        for word in itertools.product(range(2), repeat=2):
            clause = [q]
            for value, a, b in zip(word, abits, bbits):
                clause.append(-a if value else a)
                clause.append(-b if value else b)
            c.clauses.append(clause)
        return q

    if stage in {"balance", "overlap", "full"}:
        for x in range(84):
            for i in sorted(set(range(7)) - set(SUPPORTS[x])):
                # There are four relevant target fibres and one selected
                # state in each.  Exactly two 1-signs automatically means
                # exactly two 0-signs, so the old second equation was
                # redundant.
                bits = []
                for j in sorted(set(range(7)) - set(SUPPORTS[x]) - {i}):
                    G = tuple(sorted((i, j)))
                    bits.append(selected_bit(x, G, i))
                assert len(bits) == 4
                c.exact(bits, 2)

    overlap_pairs = 0
    disjoint_pairs = 0
    if stage in {"overlap", "full"}:
        for x in range(84):
            for y in range(x + 1, 84):
                if SUPPORTS[x] == SUPPORTS[y] or not (SUPPORTS[x] & SUPPORTS[y]):
                    continue
                complement = sorted(set(range(7)) - set(SUPPORTS[x] | SUPPORTS[y]))
                ys = [equality(x, y, G)
                      for G in itertools.combinations(complement, 2)]
                assert len(ys) == 6
                common_symbol = int(any(
                    SIGNS[x][i] == SIGNS[y][i]
                    for i in SUPPORTS[x] & SUPPORTS[y]
                ))
                c.exact(ys, 2 - common_symbol)
                overlap_pairs += 1

    if stage == "full":
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
                terms.extend(equality(x, y, G)
                             for G in itertools.combinations(complement, 2))
                assert len(terms) == 8
                c.exact(terms, 2)
                disjoint_pairs += 1

    meta = {
        "ansatz": "canonical-C4-fibre (restricted, not general WLOG)",
        "stage": stage,
        "branch": branch,
        "lex": bool(lex_generators),
        "lex_requested": lex,
        "variables": c.nvars,
        "clauses": len(c.clauses),
        "d_variables": len(dvar),
        "equality_variables": neq,
        "selected_bit_variables": len(bit_cache),
        "lex_aux_variables": lex_aux,
        "lex_generators": lex_generators,
        "scaffold_clauses": scaffold_clauses,
        "kg_edges": len(kg_edges),
        "overlap_pairs": overlap_pairs,
        "disjoint_pairs": disjoint_pairs,
    }
    return c, dvar, meta


def expanded_graph(model: list[int], dvar: dict[tuple[int, int], int]):
    positive = {q for q in model if q > 0}
    adj = [set() for _ in range(99)]

    def add(u: int, v: int) -> None:
        adj[u].add(v)
        adj[v].add(u)

    sym = {(i, a): 1 + 2 * i + a for i in range(7) for a in range(2)}
    for q in sym.values():
        add(0, q)
    for i in range(7):
        add(sym[i, 0], sym[i, 1])
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
    histogram: Counter[tuple[bool, int]] = Counter()
    failures = []
    for u in range(99):
        for v in range(u + 1, 99):
            common = len(adj[u] & adj[v])
            edge = v in adj[u]
            histogram[edge, common] += 1
            wanted = 1 if edge else 2
            if common != wanted and len(failures) < 20:
                failures.append([u, v, edge, common, wanted])
    return {
        "edges": sum(degrees) // 2,
        "degree_histogram": dict(sorted(Counter(degrees).items())),
        "pair_histogram": {str(k): v for k, v in sorted(histogram.items())},
        "failures": failures,
        "ok": degrees == [14] * 99 and not failures,
    }


def write_dimacs(path: Path, c: CNF) -> None:
    with path.open("w", encoding="ascii") as f:
        f.write(f"p cnf {c.nvars} {len(c.clauses)}\n")
        for clause in c.clauses:
            f.write(" ".join(map(str, clause)) + " 0\n")


def solve_pysat(c: CNF, solver_name: str, seconds: float, conflicts: int):
    from pysat.solvers import Solver

    with Solver(name=solver_name, bootstrap_with=c.clauses) as solver:
        if conflicts > 0:
            solver.conf_budget(conflicts)
        timer = None
        if seconds > 0:
            # Some PySAT backends (notably CaDiCaL 1.9.5) implement conflict
            # budgets but explicitly do not implement asynchronous interrupt.
            # Detect that here instead of silently letting a Timer exception
            # leave an allegedly wall-limited run unbounded.
            try:
                solver.interrupt()
                solver.clear_interrupt()
            except NotImplementedError as exc:
                raise ValueError(
                    f"solver {solver_name!r} has no asynchronous wall-time "
                    "interrupt; use --conflicts or an external watchdog"
                ) from exc
            timer = threading.Timer(seconds, solver.interrupt)
            timer.daemon = True
            timer.start()
        try:
            answer = solver.solve_limited(expect_interrupt=True)
        finally:
            if timer is not None:
                timer.cancel()
        model = solver.get_model() if answer is True else None
        stats = solver.accum_stats()
    return answer, model, stats


def audit_double_cosets() -> dict:
    """Machine-check the two S4 double cosets used by the scaffold."""
    perms = all_permutations()
    d8 = d8_group()
    reps = [(0, 1, 2, 3), (0, 3, 2, 1)]
    cosets = []
    for rep in reps:
        cosets.append({compose_perm(compose_perm(a, rep), b)
                       for a in d8 for b in d8})
    t = reps[1]
    tinv = inverse_perm(t)
    right = {a for a in d8
             if compose_perm(compose_perm(t, a), tinv) in d8}
    second_nond8_orbits = double_orbits(right)
    return {
        "s4_size": len(perms),
        "d8_size": len(d8),
        "double_coset_sizes": [len(x) for x in cosets],
        "disjoint": not (cosets[0] & cosets[1]),
        "cover_s4": set(perms) == cosets[0] | cosets[1],
        "d8_characterization_ok": all(
            ((p[0] ^ p[3]) == 3) == (p in d8) for p in perms
        ),
        "nond8_stabilizer_projection_size": len(right),
        "second_nond8_orbit_sizes": [len(o) for o in second_nond8_orbits],
        "second_nond8_orbits_cover_s4": (
            set().union(*second_nond8_orbits) == set(perms)
            and sum(map(len, second_nond8_orbits)) == len(perms)
        ),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["matching", "balance", "overlap", "full"],
                    default="full")
    ap.add_argument(
        "--branch",
        choices=["none", "d8", "nond8", "d8_qd8", "d8_qnond8",
                 "nond8_q1", "nond8_q2"],
        default="d8_qd8")
    ap.add_argument("--solver", default="cadical195")
    ap.add_argument("--time-limit", type=float, default=0.0,
                    help="wall seconds; 0 means no limit")
    ap.add_argument("--conflicts", type=int, default=0,
                    help="conflict budget; 0 means no budget")
    ap.add_argument("--no-lex", action="store_true")
    ap.add_argument("--dump", action="store_true")
    ap.add_argument("--build-only", action="store_true")
    args = ap.parse_args()

    audit = audit_double_cosets()
    if not all((audit["disjoint"], audit["cover_s4"],
                audit["d8_characterization_ok"],
                audit["second_nond8_orbits_cover_s4"])):
        raise AssertionError(audit)

    t0 = time.time()
    c, dvar, meta = build(args.stage, args.branch, not args.no_lex)
    meta["build_seconds"] = round(time.time() - t0, 3)
    meta["symmetry_audit"] = audit
    print(json.dumps(meta, indent=2, sort_keys=True), flush=True)

    stem = f"scratch_canonical_v2_{args.stage}_{args.branch}"
    if args.dump:
        write_dimacs(Path(stem + ".cnf"), c)
    if args.build_only:
        Path(stem + "_build.json").write_text(
            json.dumps(meta, indent=2, sort_keys=True), encoding="utf-8")
        return

    t1 = time.time()
    answer, model, stats = solve_pysat(
        c, args.solver, args.time_limit, args.conflicts)
    elapsed = round(time.time() - t1, 3)
    status = "SAT" if answer is True else "UNSAT" if answer is False else "UNKNOWN"
    result = {
        "meta": meta,
        "solver": args.solver,
        "status": status,
        "solve_seconds": elapsed,
        "solver_stats": stats,
    }
    print(json.dumps({k: result[k] for k in
                      ("solver", "status", "solve_seconds", "solver_stats")},
                     indent=2, sort_keys=True), flush=True)

    if model is not None:
        check = verify(expanded_graph(model, dvar))
        result["verification"] = check
        positive = {lit for lit in model if lit > 0}
        result["selected_D_edges"] = [
            list(edge) for edge, var in dvar.items() if var in positive
        ]
        print(json.dumps(check, indent=2, sort_keys=True), flush=True)
        if check["ok"]:
            adj = expanded_graph(model, dvar)
            result["edges_1_based"] = [
                [u + 1, v + 1]
                for u in range(99) for v in sorted(adj[u]) if u < v
            ]
    Path(stem + f"_{args.solver}_result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")


if __name__ == "__main__":
    main()
