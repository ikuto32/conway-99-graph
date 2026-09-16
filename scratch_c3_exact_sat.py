"""Exact CNF experiment for the fixed-point-free C3 automorphism branch.

Vertices are ``(orbit, phase)`` with 33 orbits and phase in Z/3.  A cross
block is a 3 by 3 circulant and is represented by its three possible phase
shifts.  An orbit itself is either independent or a K3.

The quotient matrix M has diagonal 2 on K3 orbits and 0 otherwise.  For
different orbits, M_ij is the number (0, 1, or 2) of selected phase shifts.
The SRG equation implies

    M^2 + M = 12 I + 6 J.

Consequently the support of M is 12-regular.  At every independent orbit,
the double blocks form a 2-regular graph; a K3 orbit has no double block.
These quotient conditions, including every off-diagonal entry of the matrix
equation, are encoded as redundant propagation constraints.

For every C3-orbit of unordered *distinct* vertex pairs the main encoding
imposes only

    common(u, v) + adjacent(u, v) <= 2.

This is exact, not a relaxation: the quotient row constraints force all 99
degrees to be 14, so the sum of the left hand side over all 4,851 pairs is

    99*C(14,2) + 99*14/2 = 9,702 = 2*C(99,2).

Thus every upper bound is equality.  A satisfying assignment is therefore
an srg(99,14,1,2), and every SAT result is independently expanded and
checked before any witness JSON is written.  This script never writes
``submission.txt``.

The trace restriction gives t in {6,13,20,27} for the number of K3 vertex
orbits.  There are 231 graph triangles; a C3-fixed triangle is exactly one
K3 vertex orbit, so t == 0 (mod 3).  Hence only t=6 and t=27 remain.

For t=27 the double graph is 2-regular on six vertices, hence is C6 or 2C3
up to relabelling.  Both shapes are separate exhaustive branches.  When a
shape is fixed, a lexicographically canonical neighbourhood pattern at
orbit 0 is imposed under the automorphism group of that shape.
"""

from __future__ import annotations

import argparse
import itertools
import json
import multiprocessing as mp
import queue
import time
from collections import Counter
from pathlib import Path
from typing import Callable, Iterable


N_ORBITS = 33
PHASES = 3
N = N_ORBITS * PHASES
BRANCHES = ("t6", "t27_c6", "t27_2c3")


def branch_parameters(branch: str) -> tuple[int, str]:
    if branch == "t6":
        return 6, "free"
    if branch == "t27_c6":
        return 27, "c6"
    if branch == "t27_2c3":
        return 27, "2c3"
    raise ValueError(branch)


class Builder:
    """CNF builder using PySAT's sequential counters."""

    def __init__(self) -> None:
        from pysat.formula import IDPool

        self.pool = IDPool(start_from=1)
        self.clauses: list[list[int]] = []
        self.cardinality_aux = 0

    @property
    def top(self) -> int:
        return self.pool.top

    def var(self, key: object) -> int:
        return self.pool.id(key)

    def add(self, *lits: int) -> None:
        self.clauses.append(list(lits))

    def atmost(self, lits: list[int], bound: int) -> None:
        from pysat.card import CardEnc, EncType

        before = self.pool.top
        encoded = CardEnc.atmost(
            lits=lits, bound=bound, vpool=self.pool,
            encoding=EncType.seqcounter)
        self.clauses.extend(encoded.clauses)
        self.cardinality_aux += self.pool.top - before

    def equals(self, lits: list[int], bound: int) -> None:
        from pysat.card import CardEnc, EncType

        before = self.pool.top
        encoded = CardEnc.equals(
            lits=lits, bound=bound, vpool=self.pool,
            encoding=EncType.seqcounter)
        self.clauses.extend(encoded.clauses)
        self.cardinality_aux += self.pool.top - before


def edge_coordinates(builder: Builder):
    """Allocate the 1,617 edge-orbit variables before all auxiliaries."""
    internal: list[int] = []
    cross: dict[tuple[int, int], tuple[int, int, int]] = {}
    ordered: list[tuple[str, int, int, int, int]] = []

    for i in range(N_ORBITS):
        q = builder.var(("internal", i))
        internal.append(q)
        ordered.append(("internal", i, i, 1, q))
    for i, j in itertools.combinations(range(N_ORBITS), 2):
        xs = tuple(builder.var(("cross", i, j, d)) for d in range(PHASES))
        cross[i, j] = xs
        ordered.extend(("cross", i, j, d, xs[d]) for d in range(PHASES))
    assert builder.top == 1617

    def edge(i: int, a: int, j: int, b: int) -> int:
        if i == j:
            assert a != b
            return internal[i]
        if i < j:
            return cross[i, j][(b - a) % PHASES]
        return cross[j, i][(a - b) % PHASES]

    return internal, cross, ordered, edge


def shape_edges(shape: str, vertices: list[int]) -> set[tuple[int, int]]:
    def key(a: int, b: int) -> tuple[int, int]:
        return (a, b) if a < b else (b, a)

    if shape == "c6":
        return {
            key(vertices[q], vertices[(q + 1) % len(vertices)])
            for q in range(len(vertices))
        }
    if shape == "2c3":
        return {
            key(a, b)
            for tri in (vertices[:3], vertices[3:])
            for a, b in itertools.combinations(tri, 2)
        }
    raise ValueError(shape)


def graph_automorphisms(vertices: list[int], edges: set[tuple[int, int]]) -> list[tuple[int, ...]]:
    """Brute-force the automorphism group of a graph on at most six points."""
    def local_edge(a: int, b: int) -> bool:
        return tuple(sorted((vertices[a], vertices[b]))) in edges

    answer = []
    for p in itertools.permutations(range(len(vertices))):
        if all(
            local_edge(a, b) == local_edge(p[a], p[b])
            for a, b in itertools.combinations(range(len(vertices)), 2)
        ):
            answer.append(p)
    return answer


def canonical_binary_words(group: list[tuple[int, ...]]) -> set[tuple[int, ...]]:
    """Lexicographically least binary word in each permutation orbit."""
    all_words = list(itertools.product(range(2), repeat=len(group[0])))

    def image(word: tuple[int, ...], p: tuple[int, ...]) -> tuple[int, ...]:
        out = [0] * len(word)
        for old, new in enumerate(p):
            out[new] = word[old]
        return tuple(out)

    return {min(image(word, p) for p in group) for word in all_words}


def forbid_noncanonical_words(
    builder: Builder, variables: list[int], allowed: set[tuple[int, ...]]
) -> None:
    for word in itertools.product(range(2), repeat=len(variables)):
        if word in allowed:
            continue
        # Forbid precisely this truth assignment.
        builder.clauses.append([
            -var if value else var for var, value in zip(variables, word)
        ])


def build(
    branch: str, *, full_quotient: bool = True, phase_constraints: bool = True,
    strong_quotient: bool = False,
) -> tuple[Builder, dict[str, object], dict[str, object]]:
    t_value, shape = branch_parameters(branch)
    builder = Builder()
    internal, cross, ordered_edges, edge = edge_coordinates(builder)

    # Fix the K3 vertex orbits first.  This uses only S_33 orbit relabelling.
    for i, var in enumerate(internal):
        builder.add(var if i < t_value else -var)

    support: dict[tuple[int, int], int] = {}
    double: dict[tuple[int, int], int] = {}
    for i, j in itertools.combinations(range(N_ORBITS), 2):
        xs = list(cross[i, j])
        s = builder.var(("support", i, j))
        support[i, j] = s

        # A full K_3,3 block already gives three common neighbours, and is
        # impossible.  A block incident with a K3 orbit has multiplicity <=1.
        builder.add(*[-x for x in xs])
        if i < t_value or j < t_value:
            for x, y in itertools.combinations(xs, 2):
                builder.add(-x, -y)

        # s iff at least one phase shift is present.
        for x in xs:
            builder.add(-x, s)
        builder.add(-s, *xs)

        if i >= t_value and j >= t_value:
            d = builder.var(("double", i, j))
            double[i, j] = d
            # With multiplicity <=2, d iff exactly two shifts are present.
            for x, y in itertools.combinations(xs, 2):
                builder.add(-x, -y, d)
            for x, y in itertools.combinations(xs, 2):
                builder.add(-d, x, y)

    def pair_key(i: int, j: int) -> tuple[int, int]:
        return (i, j) if i < j else (j, i)

    def s_var(i: int, j: int) -> int:
        return support[pair_key(i, j)]

    def d_var(i: int, j: int) -> int | None:
        return double.get(pair_key(i, j))

    def m_components(i: int, j: int) -> list[int]:
        answer = [s_var(i, j)]
        d = d_var(i, j)
        if d is not None:
            answer.append(d)
        return answer

    # Quotient diagonal equations, in their simplest derived form.
    for i in range(N_ORBITS):
        builder.equals([s_var(i, j) for j in range(N_ORBITS) if j != i], 12)
        if i >= t_value:
            builder.equals(
                [d_var(i, j) for j in range(t_value, N_ORBITS) if j != i],
                2,
            )

    # For t=27, fix the two exhaustive isomorphism types of the double graph.
    shape_group_size = None
    canonical_root_words = None
    if shape != "free":
        nontri = list(range(t_value, N_ORBITS))
        chosen = shape_edges(shape, nontri)
        for i, j in itertools.combinations(nontri, 2):
            builder.add(d_var(i, j) if (i, j) in chosen else -d_var(i, j))
        group = graph_automorphisms(nontri, chosen)
        allowed = canonical_binary_words(group)
        forbid_noncanonical_words(
            builder, [s_var(0, j) for j in nontri], allowed)
        shape_group_size = len(group)
        canonical_root_words = len(allowed)

    # Triangle orbit 0 has 12 simple blocks.  Rotate each other C3 orbit so
    # an occupied block has shift zero.  The support constraints make this
    # normalization exact even when the block is absent.
    for j in range(1, N_ORBITS):
        builder.add(-cross[0, j][1])
        builder.add(-cross[0, j][2])

    # Sort orbit-0 neighbours inside freely permutable type classes.  Once a
    # t=27 double-graph shape is fixed, the six non-K3 vertices are instead
    # canonicalized under that shape's automorphism group above.
    sortable_classes = [list(range(1, t_value))]
    if shape == "free":
        sortable_classes.append(list(range(t_value, N_ORBITS)))
    for cls in sortable_classes:
        for a, b in zip(cls, cls[1:]):
            builder.add(-s_var(0, b), s_var(0, a))

    product_cache: dict[tuple[int, int], int] = {}
    exact_product_keys: set[tuple[int, int]] = set()

    def product_lower_bound(a: int, b: int, *, exact: bool = False) -> int:
        """Return z with a & b -> z.

        All uses occur in upper bounds.  The reverse implications would only
        force z back to its minimum value and are therefore redundant.
        """
        if a == b:
            return a
        key = tuple(sorted((a, b)))
        if key not in product_cache:
            z = builder.var(("product",) + key)
            builder.add(-a, -b, z)
            product_cache[key] = z
        if exact and key not in exact_product_keys:
            z = product_cache[key]
            builder.add(-z, a)
            builder.add(-z, b)
            exact_product_keys.add(key)
        return product_cache[key]

    quotient_equations = 0
    quotient_term_histogram: Counter[int] = Counter()
    if full_quotient:
        # Every off-diagonal entry of M^2+M=12I+6J.  Coefficients <=5 are
        # represented by repeated input positions in a sequential counter.
        # scratch_c3_exact_card_audit.py exhaustively audits that convention.
        for i, j in itertools.combinations(range(N_ORBITS), 2):
            terms: list[int] = []
            for k in range(N_ORBITS):
                if k == i or k == j:
                    continue
                for a in m_components(i, k):
                    for b in m_components(k, j):
                        terms.append(product_lower_bound(
                            a, b, exact=strong_quotient))
            coefficient = (2 if i < t_value else 0) + (2 if j < t_value else 0) + 1
            for component in m_components(i, j):
                terms.extend([component] * coefficient)
            # Row sums and the diagonal quotient equations fix the sum of
            # these 528 unordered-pair left sides to 528*6.  Therefore the
            # upper bounds are collectively exact, just as at vertex level.
            if strong_quotient:
                builder.equals(terms, 6)
            else:
                builder.atmost(terms, 6)
            quotient_equations += 1
            quotient_term_histogram[len(terms)] += 1

    # Main phase-level common-neighbour upper bounds.  There is one pair
    # orbit inside every vertex orbit, and three between every two orbits.
    pair_representatives: list[tuple[int, int, int, int]] = []
    phase_products_before = len(product_cache)
    phase_term_histogram: Counter[int] = Counter()
    reused_same_literal = 0
    if phase_constraints:
        for i in range(N_ORBITS):
            pair_representatives.append((i, 0, i, 1))
        for i, j in itertools.combinations(range(N_ORBITS), 2):
            for relative_phase in range(PHASES):
                pair_representatives.append((i, 0, j, relative_phase))
        assert len(pair_representatives) == 1617

        for i, a, j, b in pair_representatives:
            u = PHASES * i + a
            v = PHASES * j + b
            terms: list[int] = []
            for w in range(N):
                if w == u or w == v:
                    continue
                k, c = divmod(w, PHASES)
                left = edge(i, a, k, c)
                right = edge(j, b, k, c)
                if left == right:
                    terms.append(left)
                    reused_same_literal += 1
                else:
                    terms.append(product_lower_bound(left, right))
            terms.append(edge(i, a, j, b))
            builder.atmost(terms, 2)
            phase_term_histogram[len(terms)] += 1

    edge_ids = [row[-1] for row in ordered_edges]
    assert edge_ids == list(range(1, 1618))
    meta: dict[str, object] = {
        "model": "exact fixed-point-free C3 automorphism branch",
        "branch": branch,
        "t": t_value,
        "double_shape": shape,
        "edge_orbit_variables": len(edge_ids),
        "support_variables": len(support),
        "double_variables": len(double),
        "pair_orbits": len(pair_representatives),
        "phase_constraints": phase_constraints,
        "full_quotient": full_quotient,
        "strong_quotient": strong_quotient,
        "quotient_equations": quotient_equations,
        "quotient_term_histogram": dict(sorted(quotient_term_histogram.items())),
        "one_way_product_variables": len(product_cache),
        "exact_product_variables": len(exact_product_keys),
        "one_way_products_before_phase": phase_products_before,
        "phase_reused_same_literal": reused_same_literal,
        "phase_term_histogram": dict(sorted(phase_term_histogram.items())),
        "cardinality_aux_variables": builder.cardinality_aux,
        "variables": builder.top,
        "clauses": len(builder.clauses),
        "shape_automorphism_group_size": shape_group_size,
        "canonical_root_words": canonical_root_words,
        "symmetry": {
            "K3_orbits_first": True,
            "orbit_0_phase_normalized": True,
            "orbit_0_support_sorted_in_free_type_classes": True,
        },
        "exactness": {
            "degree": 14,
            "sum_pair_lhs": 9702,
            "sum_pair_upper_bounds": 9702,
            "sum_quotient_offdiagonal_lhs": 3168,
            "sum_quotient_offdiagonal_upper_bounds": 3168,
        },
    }
    maps = {
        "ordered_edges": ordered_edges,
        "edge": edge,
        "internal": internal,
        "cross": cross,
    }
    return builder, meta, maps


def write_dimacs(path: Path, builder: Builder) -> None:
    with path.open("w", encoding="ascii", newline="\n") as handle:
        handle.write(f"p cnf {builder.top} {len(builder.clauses)}\n")
        for clause in builder.clauses:
            handle.write(" ".join(map(str, clause)) + " 0\n")


def expand_and_verify(positive_edges: set[int], branch: str) -> dict[str, object]:
    t_value, _shape = branch_parameters(branch)
    # Recreate only the deterministic first 1,617 variable IDs.
    internal = list(range(1, 34))
    next_id = 34
    cross: dict[tuple[int, int], tuple[int, int, int]] = {}
    for i, j in itertools.combinations(range(N_ORBITS), 2):
        cross[i, j] = (next_id, next_id + 1, next_id + 2)
        next_id += 3
    assert next_id == 1618

    def edge_id(i: int, a: int, j: int, b: int) -> int:
        if i == j:
            return internal[i]
        if i < j:
            return cross[i, j][(b - a) % PHASES]
        return cross[j, i][(a - b) % PHASES]

    adjacency = [set() for _ in range(N)]
    for u, v in itertools.combinations(range(N), 2):
        i, a = divmod(u, PHASES)
        j, b = divmod(v, PHASES)
        if edge_id(i, a, j, b) in positive_edges:
            adjacency[u].add(v)
            adjacency[v].add(u)

    degrees = [len(row) for row in adjacency]
    failures = []
    residuals: Counter[int] = Counter()
    for u, v in itertools.combinations(range(N), 2):
        adjacent = v in adjacency[u]
        common = len(adjacency[u].intersection(adjacency[v]))
        wanted = 1 if adjacent else 2
        residuals[common - wanted] += 1
        if common != wanted and len(failures) < 20:
            failures.append([u, v, adjacent, common, wanted])

    c3_invariant = all(
        ((v in adjacency[u]) == (((v // 3) * 3 + (v + 1) % 3) in
                                  adjacency[(u // 3) * 3 + (u + 1) % 3]))
        for u, v in itertools.combinations(range(N), 2)
    )
    edges = [
        [u + 1, v + 1]
        for u in range(N) for v in sorted(adjacency[u]) if u < v
    ]
    result: dict[str, object] = {
        "branch": branch,
        "vertices": N,
        "edge_count": len(edges),
        "degree_histogram": dict(sorted(Counter(degrees).items())),
        "residual_histogram": dict(sorted(residuals.items())),
        "bad_pairs": sum(residuals[r] for r in residuals if r),
        "bad_examples": failures,
        "c3_invariant": c3_invariant,
        "K3_orbit_count": sum(internal[i] in positive_edges for i in range(N_ORBITS)),
        "expected_K3_orbit_count": t_value,
        "edges": edges,
    }
    result["ok"] = (
        len(edges) == 693 and degrees == [14] * N and not failures
        and c3_invariant and result["K3_orbit_count"] == t_value
    )
    return result


def verify_quotient(positive_edges: set[int], branch: str) -> dict[str, object]:
    """Independently rebuild M and check every quotient matrix equation."""
    t_value, shape = branch_parameters(branch)
    next_id = 34
    cross: dict[tuple[int, int], tuple[int, int, int]] = {}
    for i, j in itertools.combinations(range(N_ORBITS), 2):
        cross[i, j] = (next_id, next_id + 1, next_id + 2)
        next_id += 3
    assert next_id == 1618

    matrix = [[0] * N_ORBITS for _ in range(N_ORBITS)]
    for i in range(N_ORBITS):
        matrix[i][i] = 2 if i < t_value else 0
    for i, j in itertools.combinations(range(N_ORBITS), 2):
        value = sum(q in positive_edges for q in cross[i, j])
        matrix[i][j] = matrix[j][i] = value

    failures = []
    for i in range(N_ORBITS):
        for j in range(N_ORBITS):
            lhs = sum(matrix[i][k] * matrix[k][j] for k in range(N_ORBITS)) + matrix[i][j]
            rhs = (12 if i == j else 0) + 6
            if lhs != rhs:
                failures.append([i, j, lhs, rhs])

    support_degrees = [
        sum(matrix[i][j] > 0 for j in range(N_ORBITS) if j != i)
        for i in range(N_ORBITS)
    ]
    double_degrees = [
        sum(matrix[i][j] == 2 for j in range(N_ORBITS) if j != i)
        for i in range(t_value, N_ORBITS)
    ]
    actual_shape_edges = {
        (i, j)
        for i, j in itertools.combinations(range(t_value, N_ORBITS), 2)
        if matrix[i][j] == 2
    }
    shape_ok = shape == "free" or actual_shape_edges == shape_edges(
        shape, list(range(t_value, N_ORBITS))
    )
    result: dict[str, object] = {
        "branch": branch,
        "row_sums": [sum(row) for row in matrix],
        "support_degrees": support_degrees,
        "double_degrees": double_degrees,
        "matrix_equation_failures": failures[:20],
        "matrix_equation_bad_entries": len(failures),
        "shape_ok": shape_ok,
        "matrix": matrix,
    }
    result["ok"] = (
        result["row_sums"] == [14] * N_ORBITS
        and support_degrees == [12] * N_ORBITS
        and double_degrees == [2] * (N_ORBITS - t_value)
        and not failures and shape_ok
    )
    return result


def solve_worker(branch: str, cnf_path: str, output_queue) -> None:
    from pysat.formula import CNF
    from pysat.solvers import Solver

    started = time.monotonic()
    formula = CNF(from_file=cnf_path)
    loaded = time.monotonic()
    with Solver(name="cadical195", bootstrap_with=formula.clauses) as solver:
        answer = solver.solve()
        model = solver.get_model() if answer else None
        stats = solver.accum_stats()
    output_queue.put({
        "branch": branch,
        "status": "SAT" if answer else "UNSAT",
        "load_seconds": round(loaded - started, 3),
        "solve_seconds": round(time.monotonic() - loaded, 3),
        "wall_seconds": round(time.monotonic() - started, 3),
        "stats": stats,
        "positive_edge_variables": (
            [lit for lit in model if 0 < lit <= 1617] if model else []
        ),
    })


def file_prefix(quotient_only: bool, strong_quotient: bool) -> str:
    base = "scratch_c3_quotient_exact" if quotient_only else "scratch_c3_exact"
    return base + ("_strong" if strong_quotient else "")


def solve_bounded(
    branch: str, seconds: float, quotient_only: bool, strong_quotient: bool
) -> dict[str, object]:
    prefix = file_prefix(quotient_only, strong_quotient)
    cnf_path = Path(f"{prefix}_{branch}.cnf")
    if not cnf_path.exists():
        raise FileNotFoundError(cnf_path)
    context = mp.get_context("spawn")
    output_queue = context.Queue()
    process = context.Process(
        target=solve_worker,
        args=(branch, str(cnf_path.resolve()), output_queue),
        name=f"c3-exact-{branch}",
    )
    process.start()
    try:
        record = output_queue.get(timeout=seconds)
    except queue.Empty:
        process.terminate()
        process.join(20)
        record = {
            "branch": branch,
            "status": "UNKNOWN",
            "wall_limit_seconds": seconds,
            "exit_code_after_termination": process.exitcode,
        }
    else:
        process.join(20)

    if record["status"] == "SAT":
        if quotient_only:
            verified = verify_quotient(set(record["positive_edge_variables"]), branch)
            record["verification"] = {k: v for k, v in verified.items() if k != "matrix"}
            if verified["ok"]:
                path = Path(f"{prefix}_{branch}_witness.json")
                path.write_text(json.dumps(verified, indent=2) + "\n", encoding="utf-8")
                record["verified_quotient"] = str(path)
        else:
            verified = expand_and_verify(set(record["positive_edge_variables"]), branch)
            record["verification"] = {k: v for k, v in verified.items() if k != "edges"}
            if verified["ok"]:
                path = Path(f"{prefix}_{branch}_solution.json")
                path.write_text(json.dumps(verified, indent=2) + "\n", encoding="utf-8")
                record["verified_witness"] = str(path)

    Path(f"{prefix}_{branch}_cadical195_result.json").write_text(
        json.dumps(record, indent=2) + "\n", encoding="utf-8"
    )
    return record


def build_one(
    branch: str, full_quotient: bool, quotient_only: bool,
    strong_quotient: bool,
) -> dict[str, object]:
    started = time.monotonic()
    builder, meta, _maps = build(
        branch, full_quotient=full_quotient,
        phase_constraints=not quotient_only,
        strong_quotient=strong_quotient)
    meta["build_seconds"] = round(time.monotonic() - started, 3)
    prefix = file_prefix(quotient_only, strong_quotient)
    stem = f"{prefix}_{branch}"
    write_dimacs(Path(stem + ".cnf"), builder)
    Path(stem + "_build.json").write_text(
        json.dumps(meta, indent=2) + "\n", encoding="utf-8"
    )
    return meta


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", choices=BRANCHES)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--solve-seconds", type=float, default=0.0)
    parser.add_argument("--no-full-quotient", action="store_true")
    parser.add_argument("--quotient-only", action="store_true")
    parser.add_argument("--strong-quotient", action="store_true")
    args = parser.parse_args()
    if args.all == (args.branch is not None):
        parser.error("choose exactly one of --branch or --all")
    if not args.build and args.solve_seconds <= 0:
        parser.error("select --build and/or --solve-seconds")

    branches = BRANCHES if args.all else (args.branch,)
    summaries = []
    for branch in branches:
        row: dict[str, object] = {"branch": branch}
        if args.build:
            row["build"] = build_one(
                branch, not args.no_full_quotient, args.quotient_only,
                args.strong_quotient)
            print(json.dumps(row["build"], sort_keys=True), flush=True)
        if args.solve_seconds > 0:
            row["solve"] = solve_bounded(
                branch, args.solve_seconds, args.quotient_only,
                args.strong_quotient)
            print(json.dumps(row["solve"], sort_keys=True), flush=True)
        summaries.append(row)
    summary_name = file_prefix(
        args.quotient_only, args.strong_quotient) + "_summary.json"
    Path(summary_name).write_text(
        json.dumps(summaries, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    mp.freeze_support()
    main()
