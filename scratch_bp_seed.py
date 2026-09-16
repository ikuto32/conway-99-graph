"""Construct an outer graph satisfying every rooted linear incidence equation.

The result is only a seed: it fixes all degrees and every condition involving
the root or one of its 14 neighbours.  Outer/outer common-neighbour equations
are verified and reported but are not asserted by this model.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path

import pycosat


ROOT = 0
INNER0 = 1
OUTER0 = 15


def exactly(clauses: list[list[int]], lits: list[int], value: int) -> None:
    if value == 1:
        clauses.append(lits[:])
        clauses.extend([-a, -b] for a, b in itertools.combinations(lits, 2))
    elif value == 2:
        # At least two: excluding any one literal must leave a true literal.
        for omitted in range(len(lits)):
            clauses.append(lits[:omitted] + lits[omitted + 1 :])
        # At most two.
        clauses.extend([-a, -b, -c] for a, b, c in itertools.combinations(lits, 3))
    else:
        raise ValueError(value)


def build() -> tuple[list[tuple[int, int]], dict[tuple[int, int], int], list[list[int]]]:
    labels = [
        pair
        for pair in itertools.combinations(range(14), 2)
        if pair[0] // 2 != pair[1] // 2
    ]
    assert len(labels) == 84
    variables: dict[tuple[int, int], int] = {}
    for u, v in itertools.combinations(range(84), 2):
        variables[u, v] = len(variables) + 1
    clauses: list[list[int]] = []
    for u, label in enumerate(labels):
        label_set = set(label)
        for symbol in range(14):
            lits = []
            for v, other in enumerate(labels):
                if u != v and symbol in other:
                    key = (u, v) if u < v else (v, u)
                    lits.append(variables[key])
            target = 1 if symbol in label_set or (symbol ^ 1) in label_set else 2
            exactly(clauses, lits, target)
    return labels, variables, clauses


def expand_and_check(
    labels: list[tuple[int, int]],
    variables: dict[tuple[int, int], int],
    positive: set[int],
) -> dict[str, object]:
    adj = [set() for _ in range(99)]

    def edge(u: int, v: int) -> None:
        adj[u].add(v)
        adj[v].add(u)

    for symbol in range(14):
        edge(ROOT, INNER0 + symbol)
    for group in range(7):
        edge(INNER0 + 2 * group, INNER0 + 2 * group + 1)
    for u, label in enumerate(labels):
        vertex = OUTER0 + u
        edge(vertex, INNER0 + label[0])
        edge(vertex, INNER0 + label[1])
    for (u, v), var in variables.items():
        if var in positive:
            edge(OUTER0 + u, OUTER0 + v)

    degrees = [len(row) for row in adj]
    edges = [(u + 1, v + 1) for u in range(99) for v in adj[u] if u < v]
    energy = 0
    bad = 0
    inner_outer_bad = 0
    outer_outer_energy = 0
    for u in range(99):
        for v in range(u + 1, 99):
            common = len(adj[u] & adj[v])
            residual = common + int(v in adj[u]) - 2
            energy += residual * residual
            bad += residual != 0
            if (1 <= u < 15 and v >= 15) or (1 <= v < 15 and u >= 15):
                inner_outer_bad += residual != 0
            if u >= 15 and v >= 15:
                outer_outer_energy += residual * residual
    assert degrees == [14] * 99
    assert len(edges) == 693
    assert inner_outer_bad == 0
    return {
        "edge_count": len(edges),
        "degree_histogram": {"14": 99},
        "energy": energy,
        "outer_outer_energy": outer_outer_energy,
        "bad_pairs": bad,
        "inner_outer_bad_pairs": inner_outer_bad,
        "edges": edges,
    }


def main() -> None:
    labels, variables, clauses = build()
    print(json.dumps({"variables": len(variables), "clauses": len(clauses)}), flush=True)
    with Path("scratch_bp_seed.cnf").open("w", encoding="ascii", newline="\n") as handle:
        handle.write(f"p cnf {len(variables)} {len(clauses)}\n")
        for clause in clauses:
            handle.write(" ".join(map(str, clause)) + " 0\n")
    model = pycosat.solve(clauses)
    if not isinstance(model, list):
        print(model)
        return
    result = expand_and_check(labels, variables, {lit for lit in model if lit > 0})
    Path("scratch_bp_seed.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in result if key != "edges"}), flush=True)


if __name__ == "__main__":
    main()
