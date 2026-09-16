"""Exact SAT search for abelian Cayley SRG(99,14,1,2) candidates.

There are exactly two abelian groups of order 99:

    Z/99Z, and (Z/3Z)^2 x Z/11Z.

For an undirected Cayley graph on an odd-order group, the connection set is
a union of seven inverse pairs.  If x_i selects inverse pair P_i, the SRG
condition is precisely

    # {(a,b) in D^2 : a-b=t} + 1[t in D] = 2       (t != 0).

The products x_i*x_j are Tseitin-linearised and every weighted equality is
encoded as an ordinary exact-cardinality constraint (weights are represented
by repeated literals).  A SAT result is converted to all 693 graph edges and
checked directly before it may be written as ``submission.txt``.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import sys
import time
from pathlib import Path


OUTPUT = Path("scratch_root_abelian_cayley_sat.json")


def atomic_json(path: Path, value) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def group_elements(moduli):
    return tuple(itertools.product(*(range(modulus) for modulus in moduli)))


def add(a, b, moduli):
    return tuple((x + y) % modulus for x, y, modulus in zip(a, b, moduli))


def neg(a, moduli):
    return tuple((-x) % modulus for x, modulus in zip(a, moduli))


def sub(a, b, moduli):
    return add(a, neg(b, moduli), moduli)


def inverse_pairs(moduli):
    zero = tuple(0 for _ in moduli)
    seen = {zero}
    pairs = []
    for element in group_elements(moduli):
        if element in seen:
            continue
        opposite = neg(element, moduli)
        assert opposite != element
        pair = tuple(sorted((element, opposite)))
        pairs.append(pair)
        seen.update(pair)
    pairs.sort()
    assert len(pairs) == 49 and len(seen) == 99
    return tuple(pairs)


def build_formula(moduli):
    dependency_root = str(Path(".deps").resolve())
    if dependency_root not in sys.path:
        sys.path.insert(0, dependency_root)
    from pysat.card import CardEnc, EncType
    from pysat.formula import CNF, IDPool

    pairs = inverse_pairs(moduli)
    pair_of = {
        element: index
        for index, pair in enumerate(pairs)
        for element in pair
    }
    pool = IDPool()
    x = [pool.id(("x", index)) for index in range(49)]
    product = {}
    formula = CNF()

    # Exactly seven inverse pairs gives |D|=14.
    formula.extend(CardEnc.equals(
        lits=x, bound=7, vpool=pool, encoding=EncType.seqcounter
    ).clauses)

    def conjunction(i, j):
        if i == j:
            return x[i]
        key = tuple(sorted((i, j)))
        if key not in product:
            y = pool.id(("and", *key))
            product[key] = y
            formula.append([-y, x[key[0]]])
            formula.append([-y, x[key[1]]])
            formula.append([y, -x[key[0]], -x[key[1]]])
        return product[key]

    target_rows = []
    for target_index, target_pair in enumerate(pairs):
        target = target_pair[0]
        coefficients = {}
        direct_count = 0
        for i, pair_i in enumerate(pairs):
            for j, pair_j in enumerate(pairs):
                count = sum(
                    sub(a, b, moduli) == target
                    for a in pair_i for b in pair_j
                )
                if not count:
                    continue
                direct_count += count
                literal = conjunction(i, j)
                coefficients[literal] = coefficients.get(literal, 0) + count

        # N_target + x_target = 2.  CardEnc is intentionally fed repeated
        # literals: each occurrence is one unit of the integer coefficient.
        coefficients[x[target_index]] = coefficients.get(x[target_index], 0) + 1
        expanded = [
            literal
            for literal, coefficient in sorted(coefficients.items())
            for _ in range(coefficient)
        ]
        # Among the 99 choices of b, b=0 and b=-target are excluded because
        # both factors range over nonzero candidate connection elements.
        assert direct_count == 97
        formula.extend(CardEnc.equals(
            lits=expanded, bound=2, vpool=pool, encoding=EncType.seqcounter
        ).clauses)
        target_rows.append({
            "target": list(target),
            "target_pair_index": target_index,
            "expanded_terms": len(expanded),
            "distinct_monomials": len(coefficients),
            "coefficient_histogram": {
                str(value): list(coefficients.values()).count(value)
                for value in sorted(set(coefficients.values()))
            },
        })

    return formula, pool, pairs, x, product, target_rows


def verify_cayley(moduli, connection):
    elements = group_elements(moduli)
    index = {element: position for position, element in enumerate(elements)}
    adjacency = [set() for _ in elements]
    for vertex, element in enumerate(elements):
        for difference in connection:
            neighbour = index[add(element, difference, moduli)]
            assert neighbour != vertex
            adjacency[vertex].add(neighbour)
    degrees = [len(row) for row in adjacency]
    common_histogram = {"adjacent": {}, "nonadjacent": {}}
    ok = degrees == [14] * 99
    for u in range(99):
        for v in range(u + 1, 99):
            common = len(adjacency[u] & adjacency[v])
            kind = "adjacent" if v in adjacency[u] else "nonadjacent"
            histogram = common_histogram[kind]
            histogram[str(common)] = histogram.get(str(common), 0) + 1
            ok &= common == (1 if kind == "adjacent" else 2)
    edges = [
        (u + 1, v + 1)
        for u in range(99) for v in adjacency[u] if u < v
    ]
    ok &= len(edges) == 693
    return {
        "ok": bool(ok),
        "vertices": 99,
        "edges": len(edges),
        "degree_histogram": {
            str(value): degrees.count(value) for value in sorted(set(degrees))
        },
        "common_neighbour_histogram": common_histogram,
    }, edges


def solve_one(name, moduli, write_submission=False):
    dependency_root = str(Path(".deps").resolve())
    if dependency_root not in sys.path:
        sys.path.insert(0, dependency_root)
    from pysat.solvers import Solver

    started = time.monotonic()
    formula, pool, pairs, x, products, target_rows = build_formula(moduli)
    built = time.monotonic()
    with Solver(name="cadical195", bootstrap_with=formula.clauses) as solver:
        answer = solver.solve()
        stats = solver.accum_stats()
        model = solver.get_model() if answer else None
    solved = time.monotonic()
    status = "SAT" if answer else "UNSAT"
    selected = []
    verification = None
    if model is not None:
        positive = set(literal for literal in model if literal > 0)
        selected = [index for index, variable in enumerate(x) if variable in positive]
        assert len(selected) == 7
        connection = tuple(
            element for index in selected for element in pairs[index]
        )
        verification, edges = verify_cayley(moduli, connection)
        assert verification["ok"]
        if write_submission:
            Path("submission.txt").write_text(
                "".join(f"{{{u}, {v}}}\n" for u, v in edges), encoding="utf-8"
            )
    return {
        "group": name,
        "moduli": list(moduli),
        "status": status,
        "inverse_pairs": len(pairs),
        "selected_inverse_pairs": selected,
        "variables": max(formula.nv, pool.top),
        "clauses": len(formula.clauses),
        "linearised_products": len(products),
        "target_rows": target_rows,
        "build_seconds": round(built - started, 6),
        "solve_seconds": round(solved - built, 6),
        "solver": "CaDiCaL 1.9.5 via PySAT",
        "solver_stats": stats,
        "direct_graph_verification": verification,
        "claim_boundary": (
            "This exhausts undirected Cayley graphs only on the named abelian "
            "group; it does not constrain non-Cayley SRG candidates."
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-submission-if-found", action="store_true")
    args = parser.parse_args()
    cases = (
        ("cyclic_Z99", (99,)),
        ("noncyclic_Z3xZ3xZ11", (3, 3, 11)),
    )
    results = [
        solve_one(name, moduli, args.write_submission_if_found)
        for name, moduli in cases
    ]
    document = {
        "status": "COMPLETE",
        "model": "all abelian Cayley SRG(99,14,1,2) candidates",
        "results": results,
        "any_verified_graph": any(
            row["direct_graph_verification"] is not None for row in results
        ),
        "all_abelian_group_types_of_order_99_covered": True,
    }
    atomic_json(OUTPUT, document)
    print(json.dumps({
        "status": document["status"],
        "results": {row["group"]: row["status"] for row in results},
        "any_verified_graph": document["any_verified_graph"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
