"""Bounded necessary-condition audit for the exceptional E0=80 case.

The compression argument forces seventeen C4 fibres and four P4 fibres.
Equality forces the four exceptional supports to form a support-cycle.  The
group 2-factor equations then leave only P4 orientations and six two-point
matching choices.  This script enumerates all 4^4 * 2^6 = 16,384 labelled
local graphs and applies necessary BP and common-neighbour upper bounds on
the induced 16 vertices.  Surviving rows are not claimed extendible.
"""

from __future__ import annotations

import itertools
import json


SUPPORTS = ((0, 1), (1, 2), (2, 3), (0, 3))
ADJACENT = ((0, 1), (1, 2), (2, 3), (3, 0))
OPPOSITE = ((0, 2), (1, 3))


def fibre_labels(support):
    g, h = support
    return tuple((2 * g + a, 2 * h + b) for a, b in itertools.product((0, 1), repeat=2))


LABELS = tuple(label for support in SUPPORTS for label in fibre_labels(support))


def fibre_data(fibre, missing_side):
    offset = 4 * fibre
    bits = tuple(itertools.product((0, 1), repeat=2))
    sides = [
        (u, v)
        for u, v in itertools.combinations(range(4), 2)
        if sum(bits[u][i] != bits[v][i] for i in (0, 1)) == 1
    ]
    missing = sides[missing_side]
    edges = {
        tuple(sorted((offset + u, offset + v)))
        for u, v in sides
        if (u, v) != missing
    }
    endpoints = tuple(offset + u for u in missing)
    centres = tuple(offset + u for u in range(4) if u not in missing)
    return edges, endpoints, centres


def add_matching(edges, left, right, crossed):
    order = right[::-1] if crossed else right
    for u, v in zip(left, order):
        edges.add(tuple(sorted((u, v))))


def necessary_checks(edges):
    neighbours = [set() for _ in LABELS]
    for u, v in edges:
        neighbours[u].add(v)
        neighbours[v].add(u)

    for u, own_label in enumerate(LABELS):
        own = set(own_label)
        for symbol in range(8):
            target = 1 if symbol in own or (symbol ^ 1) in own else 2
            if sum(symbol in LABELS[v] for v in neighbours[u]) > target:
                return False, "BP"

    for u, v in itertools.combinations(range(16), 2):
        edge = int(v in neighbours[u])
        common_inside = len(neighbours[u] & neighbours[v])
        target = 2 - len(set(LABELS[u]) & set(LABELS[v]))
        if edge + common_inside > target:
            return False, "pair_upper"
    return True, "ok"


def main():
    counts = {"total": 0, "BP": 0, "pair_upper": 0, "ok": 0}
    survivors = []
    for orientations in itertools.product(range(4), repeat=4):
        base_edges = set()
        endpoints = []
        centres = []
        for fibre, missing in enumerate(orientations):
            local_edges, local_endpoints, local_centres = fibre_data(fibre, missing)
            base_edges |= local_edges
            endpoints.append(local_endpoints)
            centres.append(local_centres)
        for matching_bits in itertools.product((0, 1), repeat=6):
            counts["total"] += 1
            edges = set(base_edges)
            for bit, (left, right) in zip(matching_bits[:4], ADJACENT):
                add_matching(edges, endpoints[left], endpoints[right], bit)
            for bit, (left, right) in zip(matching_bits[4:], OPPOSITE):
                add_matching(edges, centres[left], centres[right], bit)
            assert len(edges) == 24
            ok, reason = necessary_checks(edges)
            counts[reason] += 1
            if ok and len(survivors) < 32:
                survivors.append(
                    {
                        "orientations": orientations,
                        "matching_bits": matching_bits,
                        "edges": sorted(edges),
                    }
                )
    result = {
        "model": "necessary induced-16 audit for E0=80 equality case",
        "supports": SUPPORTS,
        "counts": counts,
        "stored_survivors": survivors,
        "conclusion": (
            "locally impossible" if counts["ok"] == 0 else
            "local necessary conditions do not eliminate E0=80"
        ),
    }
    with open("scratch_general_e80_local_audit.json", "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)
        handle.write("\n")
    print(json.dumps({"counts": counts, "conclusion": result["conclusion"]}))


if __name__ == "__main__":
    main()
