"""Generate an unrestricted 84-vertex IO-perfect warm start with PicoSAT.

Variables are all C(84,2) possible outer--outer edges.  For every outer
vertex x and each of the fourteen scaffold coordinates c, the number of
neighbours of x whose label contains c is fixed to 1 or 2.  These are exactly
the 14*84 inner--outer common-neighbour equations.  Summing them for a fixed x
also proves degree(x)=12, since every selected neighbour contributes its two
coordinates and the right hand sides sum to 24.

This model makes no symmetry, fibre, Cayley, or voltage assumption.
"""

from __future__ import annotations

import itertools
import json
import sys
import time

try:
    from pysat.solvers import Solver
    from pysat.card import CardEnc, EncType
except ImportError:  # A small fallback kept for the cached lightweight env.
    Solver = None
    import pycosat

N = 99
OUTER0 = 15  # zero-based outer vertices are 15..98


def labels():
    ans = []
    for i in range(7):
        for j in range(i + 1, 7):
            for a in range(2):
                for b in range(2):
                    ans.append((1 + 2 * i + a, 1 + 2 * j + b))
    assert len(ans) == 84
    return ans


LABEL = labels()
PAIRS = list(itertools.combinations(range(84), 2))
VAR = {pair: k + 1 for k, pair in enumerate(PAIRS)}


def edge_var(x: int, y: int) -> int:
    if x > y:
        x, y = y, x
    return VAR[(x, y)]


def add_exact(
    cnf: list[list[int]], lits: list[int], target: int, top_id: int
) -> int:
    """Exact cardinality, with disjoint sequential-counter auxiliaries."""
    n = len(lits)
    assert 0 <= target <= n
    if Solver is not None:
        enc = CardEnc.equals(
            lits=lits, bound=target, top_id=top_id, encoding=EncType.seqcounter
        )
        cnf.extend(enc.clauses)
        return enc.nv
    # at most target
    for subset in itertools.combinations(lits, target + 1):
        cnf.append([-x for x in subset])
    # at least target
    for subset in itertools.combinations(lits, n - target + 1):
        cnf.append(list(subset))
    return top_id


def scaffold_edges():
    e = set()

    def add(u, v):
        if u > v:
            u, v = v, u
        e.add((u, v))

    for s in range(14):
        add(0, 1 + s)
    for i in range(7):
        add(1 + 2 * i, 2 + 2 * i)
    for x, (c, d) in enumerate(LABEL):
        add(OUTER0 + x, c)
        add(OUTER0 + x, d)
    assert len(e) == 189
    return e


def metrics(edges):
    adj = [set() for _ in range(N)]
    for u, v in edges:
        assert u != v and v not in adj[u]
        adj[u].add(v)
        adj[v].add(u)
    energy = io = oo = bad = 0
    max_abs = 0
    for u in range(N):
        for v in range(u + 1, N):
            r = len(adj[u] & adj[v]) + (v in adj[u]) - 2
            p = r * r
            energy += p
            if u < OUTER0 <= v:
                io += p
            elif u >= OUTER0:
                oo += p
            bad += r != 0
            max_abs = max(max_abs, abs(r))
    return {
        "energy": energy,
        "recomputed_energy": energy,
        "io_energy": io,
        "oo_energy": oo,
        "bad_pairs": bad,
        "max_abs_residual": max_abs,
        "edge_count": len(edges),
    }, adj


def main():
    output = sys.argv[1] if len(sys.argv) > 1 else "scratch_general_v2_io_sat_seed.json"
    cnf = []
    constraints = 0
    top_id = len(PAIRS)
    for x in range(84):
        support_groups = {(LABEL[x][0] - 1) // 2, (LABEL[x][1] - 1) // 2}
        for c in range(1, 15):
            ys = [y for y in range(84) if y != x and c in LABEL[y]]
            target = 1 if (c - 1) // 2 in support_groups else 2
            assert len(ys) in (11, 12)
            top_id = add_exact(
                cnf, [edge_var(x, y) for y in ys], target, top_id
            )
            constraints += 1
    print(
        f"edge_vars={len(PAIRS)} total_vars={top_id} clauses={len(cnf)} exact_constraints={constraints}",
        file=sys.stderr,
        flush=True,
    )
    started = time.time()
    if Solver is not None:
        with Solver(name="cadical195", bootstrap_with=cnf) as solver:
            sat = solver.solve()
            model = solver.get_model() if sat else "UNSAT"
    else:
        model = pycosat.solve(cnf, vars=top_id, verbose=1)
    elapsed = time.time() - started
    if not isinstance(model, list):
        raise SystemExit(f"solver result={model!r} elapsed={elapsed:.3f}s")
    chosen = {lit for lit in model if lit > 0}
    edges = scaffold_edges()
    for k, (x, y) in enumerate(PAIRS, 1):
        if k in chosen:
            u, v = OUTER0 + x, OUTER0 + y
            edges.add((u, v) if u < v else (v, u))
    info, adj = metrics(edges)
    assert info["edge_count"] == 693
    assert info["io_energy"] == 0
    assert all(len(a) == 14 for a in adj)
    info.update(
        {
            "sat_variables": len(PAIRS),
            "sat_total_variables": top_id,
            "sat_clauses": len(cnf),
            "sat_exact_constraints": constraints,
            "solve_seconds": elapsed,
            "edges": [[u + 1, v + 1] for u, v in sorted(edges)],
        }
    )
    with open(output, "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2)
        f.write("\n")
    print(
        f"SAT elapsed={elapsed:.3f}s edges={info['edge_count']} "
        f"energy={info['energy']} io={info['io_energy']} oo={info['oo_energy']} "
        f"bad={info['bad_pairs']} output={output}"
    )


if __name__ == "__main__":
    main()
