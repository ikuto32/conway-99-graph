"""Exact rooted SAT model strengthened by the 140-triangle decomposition.

The baseline CNF remains present verbatim.  In addition, each possible
all-outer triangle receives one variable.  Every actual outer triangle has
three pairwise exact-symbol-disjoint labels; every exact-symbol-disjoint edge
belongs to exactly one such triangle; and a triple containing a shared-symbol
pair cannot be a triangle.  These are direct consequences of lambda=1 and
the fixed inner scaffold, and are linked to edge variables by full Tseitin
equivalences.

The script builds an instance only and never writes ``submission.txt``.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import time
from pathlib import Path

from scratch_general_exact_sat import coordinates


CNF_PATH = Path("scratch_general_sat_triangles.cnf")
BUILD_PATH = Path("scratch_general_sat_triangles_build.json")


def build_cnf():
    from pysat.card import CardEnc, EncType
    from pysat.formula import IDPool

    labels, index, variables, edge = coordinates()
    label_sets = [set(label) for label in labels]
    pool = IDPool(start_from=len(variables) + 1)
    clauses: list[list[int]] = []

    # BP=P A0.
    for u, label in enumerate(labels):
        own = set(label)
        for symbol in range(14):
            lits = [
                edge(u, v)
                for v, other in enumerate(labels)
                if u != v and symbol in other
            ]
            target = 1 if symbol in own or (symbol ^ 1) in own else 2
            clauses.extend(
                CardEnc.equals(lits, target, vpool=pool, encoding=EncType.seqcounter).clauses
            )

    # Cheap explicit version of the fibre diagonal-isolation consequence.
    fibre_clauses = 0
    for ga, gb in itertools.combinations(range(7), 2):
        a0, a1, b0, b1 = 2 * ga, 2 * ga + 1, 2 * gb, 2 * gb + 1
        p00, p01 = index[(a0, b0)], index[(a0, b1)]
        p10, p11 = index[(a1, b0)], index[(a1, b1)]
        diagonals = (edge(p00, p11), edge(p01, p10))
        sides = (
            edge(p00, p01), edge(p00, p10),
            edge(p11, p01), edge(p11, p10),
        )
        for diagonal in diagonals:
            for side in sides:
                clauses.append([-diagonal, -side])
                fibre_clauses += 1

    # Baseline common-neighbour upper bounds.  They are collectively exact by
    # the fixed degree/global-sum argument.
    products = 0
    target_histogram = {1: 0, 2: 0}
    for u, v in itertools.combinations(range(84), 2):
        terms = []
        for w in range(84):
            if w in (u, v):
                continue
            a, b = edge(u, w), edge(v, w)
            z = pool.id(("and", u, v, w))
            clauses.append([-a, -b, z])
            terms.append(z)
            products += 1
        terms.append(edge(u, v))
        target = 2 - len(label_sets[u].intersection(label_sets[v]))
        target_histogram[target] += 1
        clauses.extend(
            CardEnc.atmost(terms, target, vpool=pool, encoding=EncType.seqcounter).clauses
        )

    # Triangle variables and full edge links.
    triangle_by_pair: dict[tuple[int, int], list[int]] = {
        pair: []
        for pair in itertools.combinations(range(84), 2)
        if label_sets[pair[0]].isdisjoint(label_sets[pair[1]])
    }
    triangle_variables = 0
    forbidden_triangle_clauses = 0
    for u, v, w in itertools.combinations(range(84), 3):
        pairwise_disjoint = (
            label_sets[u].isdisjoint(label_sets[v])
            and label_sets[u].isdisjoint(label_sets[w])
            and label_sets[v].isdisjoint(label_sets[w])
        )
        euv, euw, evw = edge(u, v), edge(u, w), edge(v, w)
        if not pairwise_disjoint:
            clauses.append([-euv, -euw, -evw])
            forbidden_triangle_clauses += 1
            continue
        t = pool.id(("triangle", u, v, w))
        # t <-> euv & euw & evw.
        clauses.extend(
            ([-euv, -euw, -evw, t], [euv, -t], [euw, -t], [evw, -t])
        )
        triangle_variables += 1
        triangle_by_pair[(u, v)].append(t)
        triangle_by_pair[(u, w)].append(t)
        triangle_by_pair[(v, w)].append(t)

    triangle_pair_histogram: dict[int, int] = {}
    triangle_pair_counter_aux = 0
    for (u, v), terms in triangle_by_pair.items():
        triangle_pair_histogram[len(terms)] = triangle_pair_histogram.get(len(terms), 0) + 1
        # Exactly one incident triangle iff this disjoint-label edge is selected.
        # t -> edge is already in each full conjunction; the long clause is
        # edge -> OR(t), and the counter prevents two triangles on one edge.
        clauses.append([-edge(u, v)] + terms)
        before = pool.top
        clauses.extend(
            CardEnc.atmost(terms, 1, vpool=pool, encoding=EncType.seqcounter).clauses
        )
        triangle_pair_counter_aux += pool.top - before

    meta = {
        "model": "exact unrestricted rooted SAT with explicit triangle decomposition",
        "logical_exactness": "baseline exact CNF plus only implied triangle constraints",
        "edge_variables": len(variables),
        "common_product_variables": products,
        "target_histogram": target_histogram,
        "triangle_variables": triangle_variables,
        "triangle_pair_candidate_histogram": triangle_pair_histogram,
        "triangle_pair_counter_auxiliary_variables": triangle_pair_counter_aux,
        "forbidden_triangle_clauses": forbidden_triangle_clauses,
        "fibre_diagonal_exclusion_clauses": fibre_clauses,
        "variables": pool.top,
        "clauses": len(clauses),
    }
    assert triangle_variables == 35560
    assert len(triangle_by_pair) == 2562
    assert forbidden_triangle_clauses + triangle_variables == 84 * 83 * 82 // 6
    with CNF_PATH.open("w", encoding="ascii", newline="\n") as handle:
        handle.write(f"p cnf {pool.top} {len(clauses)}\n")
        for clause in clauses:
            handle.write(" ".join(map(str, clause)) + " 0\n")
    meta["cnf_sha256"] = hashlib.sha256(CNF_PATH.read_bytes()).hexdigest().upper()
    BUILD_PATH.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    return meta


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    args = parser.parse_args()
    if not args.build:
        parser.error("select --build")
    started = time.monotonic()
    meta = build_cnf()
    meta["build_seconds"] = round(time.monotonic() - started, 3)
    BUILD_PATH.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(meta, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
