"""Lean propagation strengthening of the exact rooted SAT model.

Compared with ``scratch_general_exact_sat.py`` this keeps the globally exact
per-pair upper-bound argument and the same sequential counters, but changes
every wedge helper into a full Tseitin AND.  It also exposes the inexpensive
same-fibre diagonal exclusion clauses.  This isolates the value of backwards
AND propagation without the much larger explicit lower-bound circuits in
``scratch_general_sat_v2.py``.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import time
from pathlib import Path

from scratch_general_exact_sat import coordinates


CNF_PATH = Path("scratch_general_sat_hybrid.cnf")
BUILD_PATH = Path("scratch_general_sat_hybrid_build.json")


def build_cnf():
    from pysat.card import CardEnc, EncType
    from pysat.formula import IDPool

    labels, index, variables, edge = coordinates()
    pool = IDPool(start_from=len(variables) + 1)
    clauses: list[list[int]] = []

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

    products = 0
    target_histogram = {1: 0, 2: 0}
    for u, v in itertools.combinations(range(84), 2):
        terms = []
        for w in range(84):
            if w in (u, v):
                continue
            a, b = edge(u, w), edge(v, w)
            z = pool.id(("and", u, v, w))
            clauses.extend(([-a, -b, z], [a, -z], [b, -z]))
            terms.append(z)
            products += 1
        terms.append(edge(u, v))
        target = 2 - len(set(labels[u]).intersection(labels[v]))
        target_histogram[target] += 1
        clauses.extend(
            CardEnc.atmost(terms, target, vpool=pool, encoding=EncType.seqcounter).clauses
        )

    meta = {
        "model": "lean full-AND globally-exact rooted SAT hybrid",
        "logical_exactness": (
            "BP fixes degree 12 and global wedge sum; all per-pair upper bounds "
            "therefore attain equality"
        ),
        "edge_variables": len(variables),
        "common_product_variables": products,
        "fibre_diagonal_exclusion_clauses": fibre_clauses,
        "target_histogram": target_histogram,
        "variables": pool.top,
        "clauses": len(clauses),
    }
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
