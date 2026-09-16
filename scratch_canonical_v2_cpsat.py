"""CP-SAT cross-check of the canonical C4-fibre permutation model.

The mathematical restriction and the four exhaustive symmetry branches are
the same as in scratch_canonical_v2_sat.py.  This model represents each
four-by-four matching directly by a permutation and uses OR-Tools' parallel
CP-SAT engine.  It is an independent encoding cross-check, not a replacement
for direct verification of a returned 99-vertex graph.
"""

from __future__ import annotations

import argparse
import itertools
import json
import os
import time
from pathlib import Path

from ortools.sat.python import cp_model

from scratch_canonical_v2_sat import (
    BASES,
    FIBRES,
    FIRST_D8_BRANCHES,
    FIRST_NOND8_BRANCHES,
    SECOND_BRANCHES,
    SIGNS,
    SUPPORTS,
    all_permutations,
    compose_perm,
    d8_group,
    double_orbits,
    fixed_r,
    inverse_perm,
    verify,
)


BRANCHES = ("d8_qd8", "d8_qnond8", "nond8_q1", "nond8_q2")
BASE_INDEX = {A: i for i, A in enumerate(BASES)}


def build(stage: str, branch: str):
    if branch not in BRANCHES:
        raise ValueError(f"CP-SAT uses the four exhaustive branches, got {branch!r}")
    model = cp_model.CpModel()
    kg_edges: list[tuple[tuple[int, int], tuple[int, int]]] = []
    forward: dict[tuple[tuple[int, int], tuple[int, int]], list] = {}
    reverse: dict[tuple[tuple[int, int], tuple[int, int]], list] = {}

    for q, A in enumerate(BASES):
        for B in BASES[q + 1:]:
            if set(A).isdisjoint(B):
                key = (A, B)
                kg_edges.append(key)
                f = [model.NewIntVar(0, 3, f"p:{A}:{B}:{s}") for s in range(4)]
                r = [model.NewIntVar(0, 3, f"q:{B}:{A}:{s}") for s in range(4)]
                model.AddInverse(f, r)
                forward[key], reverse[key] = f, r

    def oriented_rows(A: tuple[int, int], B: tuple[int, int]):
        if BASE_INDEX[A] < BASE_INDEX[B]:
            return forward[A, B], reverse[A, B]
        return reverse[B, A], forward[B, A]

    def row_state(x: int, G: tuple[int, int]):
        A = tuple(sorted(SUPPORTS[x]))
        assert set(A).isdisjoint(G)
        out, _back = oriented_rows(A, G)
        a, b = (SIGNS[x][i] for i in A)
        return out[2 * a + b]

    bit_cache: dict[tuple[int, int], object] = {}

    def state_bit(state, pos: int):
        key = (state.Index(), pos)
        if key not in bit_cache:
            bit = model.NewBoolVar(f"bit:{state.Index()}:{pos}")
            if pos == 0:
                other = model.NewBoolVar(f"bit:{state.Index()}:1")
                # Install both coordinates together when possible.
                model.Add(state == 2 * bit + other)
                bit_cache[key] = bit
                bit_cache[state.Index(), 1] = other
            elif (state.Index(), 0) in bit_cache:
                raise AssertionError("unreachable cache state")
            else:
                first = model.NewBoolVar(f"bit:{state.Index()}:0")
                model.Add(state == 2 * first + bit)
                bit_cache[state.Index(), 0] = first
                bit_cache[key] = bit
        return bit_cache[key]

    def coordinate_bit(x: int, G: tuple[int, int], coord: int):
        return state_bit(row_state(x, G), G.index(coord))

    value_cache: dict[tuple[int, int], object] = {}

    def equals_value(state, value: int):
        key = (state.Index(), value)
        if key not in value_cache:
            b = model.NewBoolVar(f"is:{state.Index()}:{value}")
            model.Add(state == value).OnlyEnforceIf(b)
            model.Add(state != value).OnlyEnforceIf(b.Not())
            value_cache[key] = b
        return value_cache[key]

    def d_edge(x: int, y: int):
        A, B = tuple(sorted(SUPPORTS[x])), tuple(sorted(SUPPORTS[y]))
        assert set(A).isdisjoint(B)
        out, _back = oriented_rows(A, B)
        sx = 2 * SIGNS[x][A[0]] + SIGNS[x][A[1]]
        sy = 2 * SIGNS[y][B[0]] + SIGNS[y][B[1]]
        return equals_value(out[sx], sy)

    def equal_states(a, b, tag: str):
        q = model.NewBoolVar(tag)
        model.Add(a == b).OnlyEnforceIf(q)
        model.Add(a != b).OnlyEnforceIf(q.Not())
        return q

    def fix_matching(A, B, p):
        out, _back = oriented_rows(A, B)
        for s, t in enumerate(p):
            model.Add(out[s] == t)

    def require_nond8(A, B):
        out, _back = oriented_rows(A, B)
        model.AddForbiddenAssignments(
            [out[0], out[3]], [(t, t ^ 3) for t in range(4)])

    def require_orbit(A, B, allowed):
        out, _back = oriented_rows(A, B)
        model.AddAllowedAssignments(out, sorted(allowed))

    # The same exhaustive scaffold used by the compact CNF.
    A, B = (0, 1), (2, 3)
    first_d8 = branch in FIRST_D8_BRANCHES
    assert first_d8 or branch in FIRST_NOND8_BRANCHES
    first_rep = (0, 1, 2, 3) if first_d8 else (0, 3, 2, 1)
    fix_matching(A, B, first_rep)
    if not first_d8:
        for U, V in kg_edges:
            require_nond8(U, V)

    assert branch in SECOND_BRANCHES
    C = (4, 5)
    remaining_fibres = ((4, 5), (4, 6), (5, 6))
    if first_d8:
        if branch == "d8_qd8":
            second_rep = (0, 1, 2, 3)
        else:
            second_rep = (0, 1, 3, 2)
            for G in remaining_fibres:
                require_nond8(A, G)
    else:
        H = d8_group()
        t = tuple(first_rep)
        tinv = inverse_perm(t)
        right = {a for a in H
                 if compose_perm(compose_perm(t, a), tinv) in H}
        orbits = double_orbits(right)
        qi = 1 if branch == "nond8_q1" else 2
        second_rep = min(orbits[qi])
        for G in remaining_fibres:
            require_orbit(A, G, orbits[1] | orbits[2])
            if qi == 2:
                require_orbit(A, G, orbits[2])
    fix_matching(A, C, second_rep)
    # Last independent sign flip.
    model.Add(coordinate_bit(FIBRES[A][0], (2, 6), 6) == 0)

    if stage in {"balance", "overlap", "full"}:
        for x in range(84):
            for i in sorted(set(range(7)) - set(SUPPORTS[x])):
                bits = []
                for j in sorted(set(range(7)) - set(SUPPORTS[x]) - {i}):
                    G = tuple(sorted((i, j)))
                    bits.append(coordinate_bit(x, G, i))
                model.Add(sum(bits) == 2)

    equality_count = 0
    overlap_pairs = 0
    disjoint_pairs = 0
    if stage in {"overlap", "full"}:
        for x in range(84):
            for y in range(x + 1, 84):
                if SUPPORTS[x] == SUPPORTS[y] or not (SUPPORTS[x] & SUPPORTS[y]):
                    continue
                complement = sorted(set(range(7)) - set(SUPPORTS[x] | SUPPORTS[y]))
                terms = []
                for G in itertools.combinations(complement, 2):
                    terms.append(equal_states(
                        row_state(x, G), row_state(y, G),
                        f"eqO:{x}:{y}:{G}"))
                    equality_count += 1
                common_symbol = int(any(
                    SIGNS[x][i] == SIGNS[y][i]
                    for i in SUPPORTS[x] & SUPPORTS[y]))
                model.Add(sum(terms) == 2 - common_symbol)
                overlap_pairs += 1

    if stage == "full":
        for x in range(84):
            for y in range(x + 1, 84):
                if not SUPPORTS[x].isdisjoint(SUPPORTS[y]):
                    continue
                terms = [d_edge(x, y)]
                terms.extend(d_edge(z, y) for z in range(84)
                             if SUPPORTS[z] == SUPPORTS[x] and fixed_r(x, z))
                terms.extend(d_edge(x, z) for z in range(84)
                             if SUPPORTS[z] == SUPPORTS[y] and fixed_r(y, z))
                complement = sorted(set(range(7)) - set(SUPPORTS[x] | SUPPORTS[y]))
                for G in itertools.combinations(complement, 2):
                    terms.append(equal_states(
                        row_state(x, G), row_state(y, G),
                        f"eqD:{x}:{y}:{G}"))
                    equality_count += 1
                model.Add(sum(terms) == 2)
                disjoint_pairs += 1

    meta = {
        "ansatz": "canonical-C4-fibre (restricted, not general WLOG)",
        "encoding": "OR-Tools CP-SAT permutation/inverse",
        "stage": stage,
        "branch": branch,
        "kg_edges": len(kg_edges),
        "permutation_state_variables": 8 * len(kg_edges),
        "state_bit_variables": len(bit_cache),
        "edge_indicator_variables": len(value_cache),
        "equality_variables": equality_count,
        "overlap_pairs": overlap_pairs,
        "disjoint_pairs": disjoint_pairs,
    }
    return model, forward, meta


def expanded_graph(solver: cp_model.CpSolver, forward):
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
            if fixed_r(x, y):
                add(15 + x, 15 + y)
                continue
            A, B = tuple(sorted(SUPPORTS[x])), tuple(sorted(SUPPORTS[y]))
            if not set(A).isdisjoint(B):
                continue
            if BASE_INDEX[A] < BASE_INDEX[B]:
                rows = forward[A, B]
                sx = 2 * SIGNS[x][A[0]] + SIGNS[x][A[1]]
                sy = 2 * SIGNS[y][B[0]] + SIGNS[y][B[1]]
            else:
                rows = forward[B, A]
                sx = 2 * SIGNS[y][B[0]] + SIGNS[y][B[1]]
                sy = 2 * SIGNS[x][A[0]] + SIGNS[x][A[1]]
            if solver.Value(rows[sx]) == sy:
                add(15 + x, 15 + y)
    return adj


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=["matching", "balance", "overlap", "full"],
                    default="full")
    ap.add_argument("--branch", choices=BRANCHES, default="d8_qd8")
    ap.add_argument("--seconds", type=float, default=300.0)
    ap.add_argument("--workers", type=int, default=min(32, os.cpu_count() or 1))
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--log", action="store_true")
    args = ap.parse_args()

    t0 = time.time()
    model, forward, meta = build(args.stage, args.branch)
    meta["build_seconds"] = round(time.time() - t0, 3)
    print(json.dumps(meta, indent=2, sort_keys=True), flush=True)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = args.seconds
    solver.parameters.num_search_workers = args.workers
    solver.parameters.random_seed = args.seed
    solver.parameters.log_search_progress = args.log
    solver.parameters.symmetry_level = 3
    status_code = solver.Solve(model)
    status = solver.StatusName(status_code)
    result = {
        "meta": meta,
        "status": status,
        "wall_time": solver.WallTime(),
        "user_time": solver.UserTime(),
        "conflicts": solver.NumConflicts(),
        "branches": solver.NumBranches(),
        "workers": args.workers,
        "seed": args.seed,
        "response_stats": solver.ResponseStats(),
    }
    print(json.dumps({k: result[k] for k in
                      ("status", "wall_time", "conflicts", "branches")},
                     indent=2), flush=True)
    if status_code in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        adj = expanded_graph(solver, forward)
        result["verification"] = verify(adj)
        print(json.dumps(result["verification"], indent=2, sort_keys=True), flush=True)
        if result["verification"]["ok"]:
            result["edges_1_based"] = [
                [u + 1, v + 1]
                for u in range(99) for v in sorted(adj[u]) if u < v]
    stem = f"scratch_canonical_v2_cpsat_{args.stage}_{args.branch}_s{args.seed}.json"
    Path(stem).write_text(json.dumps(result, indent=2, sort_keys=True),
                          encoding="utf-8")


if __name__ == "__main__":
    main()
