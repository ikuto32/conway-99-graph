"""Audit the exceptional q-signatures on the source-133 compact frontier.

For a regular source-133 macro, every exceptional vertex x in A_i or B_i
has q_x = eps_x w_i, eps_x in {-1,+1}.  This script extracts that sign with
exact integer coordinates and inventories the signatures which the later
ordinary-layer H/F CSP has to process.
"""

from __future__ import annotations

import hashlib
import json
import os
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path


INPUT = Path("scratch_general_e72_source133_pointwise_frontier.json")
OUTPUT = Path("scratch_general_e72_source133_hf_signature_audit.json")
REGULAR_MACROS = frozenset(range(4))
U = {2: (1, 0), 3: (0, 1), 4: (-1, -1)}


def atomic_json(path: Path, value) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def add(left, right):
    return left[0] + right[0], left[1] + right[1]


def subtract(left, right):
    return left[0] - right[0], left[1] - right[1]


def negate(value):
    return -value[0], -value[1]


def support(vertex):
    return tuple(sorted(symbol // 2 for symbol in vertex))


def q_signature(vertices, pair_positions, mask):
    neighbours = [set() for _ in vertices]
    for bit, (left, right) in enumerate(pair_positions):
        if (mask >> bit) & 1:
            neighbours[left].add(right)
            neighbours[right].add(left)
    signs = []
    per_fibre = defaultdict(list)
    for x, vertex in enumerate(vertices):
        fibre = support(vertex)
        root, bottom = fibre
        q = (0, 0)
        for y in neighbours[x]:
            other_root, other_bottom = support(vertices[y])
            vector = U[other_bottom]
            if other_root == 1:
                vector = negate(vector)
            q = add(q, vector)
        complement = tuple(value for value in U if value != bottom)
        w = subtract(U[complement[0]], U[complement[1]])
        if q == w:
            eps = 1
        elif q == negate(w):
            eps = -1
        else:
            raise AssertionError((vertex, fibre, q, w))
        signs.append(eps)
        per_fibre[fibre].append(eps)
    assert len(per_fibre) == 6
    assert all(sorted(values) == [-1, -1, 1, 1]
               for values in per_fibre.values())
    return tuple(signs)


def run() -> None:
    document = json.loads(INPUT.read_text(encoding="utf-8"))
    vertices = tuple(tuple(vertex) for vertex in document["vertex_order"])
    pair_positions = tuple(combinations(range(len(vertices)), 2))
    by_macro = defaultdict(Counter)
    labelled_mass_by_signature = Counter()
    orbit_count_by_signature = Counter()
    for row in document["representatives"]:
        macro = int(row[3])
        if macro not in REGULAR_MACROS:
            continue
        signature = q_signature(vertices, pair_positions, int(row[0], 16))
        key = (macro, signature)
        by_macro[macro][signature] += 1
        orbit_count_by_signature[key] += 1
        labelled_mass_by_signature[key] += int(row[1])

    signature_rows = []
    for (macro, signature), orbit_count in sorted(
        orbit_count_by_signature.items(), key=lambda item: (item[0][0], item[0][1])
    ):
        signature_rows.append({
            "state_macro_number": macro,
            "eps_bits_hex": hex(sum((value > 0) << i
                                      for i, value in enumerate(signature))),
            "completed_graph_orbits": orbit_count,
            "labelled_orbit_mass": labelled_mass_by_signature[(macro, signature)],
        })

    result = {
        "status": "EXACT_SIGNATURE_AUDIT_COMPLETE",
        "input": str(INPUT),
        "input_sha256": sha256(INPUT),
        "eps_convention": (
            "u2=(1,0),u3=(0,1),u4=(-1,-1); w_i=u_j-u_k for sorted "
            "complement {j,k}; bit1 means q_x=+w_i"
        ),
        "regular_macros": sorted(REGULAR_MACROS),
        "vertices": [list(vertex) for vertex in vertices],
        "summary": {
            "regular_completed_graph_orbits": sum(orbit_count_by_signature.values()),
            "regular_labelled_orbit_mass": sum(labelled_mass_by_signature.values()),
            "distinct_(macro,eps)_signatures": len(signature_rows),
            "distinct_eps_signatures_ignoring_macro": len({
                signature for _macro, signature in orbit_count_by_signature
            }),
            "per_macro_distinct_eps_signatures": {
                str(macro): len(by_macro[macro]) for macro in sorted(by_macro)
            },
        },
        "signatures": signature_rows,
        "checks": {
            "all_exceptional_q_vectors_are_signed_w_i": True,
            "each_exceptional_fibre_has_two_positive_and_two_negative_eps": True,
        },
    }
    assert result["summary"]["regular_completed_graph_orbits"] == 92_413
    assert result["summary"]["regular_labelled_orbit_mass"] == 30_938_816
    atomic_json(OUTPUT, result)
    print(json.dumps(result["summary"], sort_keys=True), flush=True)


if __name__ == "__main__":
    run()
