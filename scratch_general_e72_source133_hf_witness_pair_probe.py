"""Direct pair-upper probe of stored source-133 H/F CSP witnesses.

This reconstructs the 24 bottom--outside ordinary vertices, their six fixed
C4s, and every exceptional-to-U edge in the exact witness saved by
``scratch_general_e72_source133_hf_exception_csp.py``.  It is a direct audit
of those witnesses.  Failure of the stored witness alone does not reject its
exceptional mask, since another CSP witness may still pass; the output states
this distinction explicitly.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import os
from collections import Counter, defaultdict
from pathlib import Path

import scratch_general_e79_local_audit as local79


INPUT = Path("scratch_general_e72_source133_hf_exception_csp.json")
OUTPUT = Path("scratch_general_e72_source133_hf_witness_pair_probe.json")
BOTTOM = (2, 3, 4)
OUTSIDE = (5, 6)
BITS = tuple(itertools.product((0, 1), repeat=2))
SIDES = tuple(
    pair for pair in itertools.combinations(range(4), 2)
    if sum(BITS[pair[0]][axis] != BITS[pair[1]][axis]
           for axis in (0, 1)) == 1
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def atomic_json(path: Path, value) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, separators=(",", ":")) + "\n",
                         encoding="utf-8")
    temporary.replace(path)


def local_label(support, bits):
    return tuple(sorted((2 * support[0] + bits[0],
                         2 * support[1] + bits[1])))


def normal_edge(left, right):
    return tuple(sorted((tuple(left), tuple(right))))


def exceptional_edges(vertex_order, mask):
    pairs = tuple(itertools.combinations(range(len(vertex_order)), 2))
    return {
        normal_edge(vertex_order[left], vertex_order[right])
        for bit, (left, right) in enumerate(pairs) if (mask >> bit) & 1
    }


def reconstruct(record, exceptional_vertices):
    mask_hex, _mass, _q, macro, detail = record
    assert macro < 4 and detail is not None
    _option_counts, _orientations, _joint_count, t_options, map_rows = detail
    t_by_support = {}
    for bottom, option in zip(BOTTOM, t_options):
        _type5, t5, t6 = option
        t_by_support[(bottom, 5)] = tuple(t5)
        t_by_support[(bottom, 6)] = tuple(t6)
    u_vertices = {
        support: tuple(local_label(support, bits) for bits in BITS)
        for support in itertools.product(BOTTOM, OUTSIDE)
    }
    vertices = tuple(exceptional_vertices) + tuple(
        vertex for support in sorted(u_vertices)
        for vertex in u_vertices[support]
    )
    assert len(vertices) == len(set(vertices)) == 48
    edges = exceptional_edges(exceptional_vertices, int(mask_hex, 16))
    for support, fibre_vertices in u_vertices.items():
        del support
        for left, right in SIDES:
            edges.add(normal_edge(fibre_vertices[left], fibre_vertices[right]))
    exceptional_by_support = defaultdict(list)
    for vertex in exceptional_vertices:
        exceptional_by_support[tuple(symbol // 2 for symbol in vertex)].append(vertex)
    exceptional_by_support = {
        support: tuple(row) for support, row in exceptional_by_support.items()
    }
    assert all(len(row) == 4 for row in exceptional_by_support.values())
    for row in map_rows:
        fibre_raw, left_bottom, map_left5, map_left6, right_bottom, map_right5, map_right6 = row
        fibre = tuple(fibre_raw)
        sources = exceptional_by_support[fibre]
        for target_bottom, mapping5, mapping6 in (
            (left_bottom, map_left5, map_left6),
            (right_bottom, map_right5, map_right6),
        ):
            for outside, mapping in ((5, mapping5), (6, mapping6)):
                targets = u_vertices[(target_bottom, outside)]
                for source_index, target_index in enumerate(mapping):
                    edges.add(normal_edge(sources[source_index], targets[target_index]))
    assert len(edges) == 48 + 6 * 4 + 24 * 4
    return vertices, frozenset(edges), t_by_support


def first_pair_failure(vertices, edges):
    neighbours = local79.neighbour_sets(vertices, edges)
    for left, right in itertools.combinations(vertices, 2):
        direct = int(right in neighbours[left])
        common = len(neighbours[left] & neighbours[right])
        target = 2 - len(set(left) & set(right))
        if direct + common > target:
            return {
                "left": list(left),
                "right": list(right),
                "direct": direct,
                "common": common,
                "target": target,
            }
    return None


def run() -> None:
    document = json.loads(INPUT.read_text(encoding="utf-8"))
    exceptional_vertices = tuple(tuple(value) for value in json.loads(
        Path("scratch_general_e72_source133_pointwise_frontier.json").read_text(
            encoding="utf-8"
        )
    )["vertex_order"])
    per_macro = defaultdict(Counter)
    passing = []
    first_failures = []
    for record in document["frontier"]:
        macro = record[3]
        if macro == 4:
            continue
        vertices, edges, _t = reconstruct(record, exceptional_vertices)
        failure = first_pair_failure(vertices, edges)
        stats = per_macro[macro]
        stats["stored_witnesses_checked"] += 1
        stats["stored_witness_mass"] += record[1]
        if failure is None:
            assert local79.induced_pair_upper(vertices, edges)
            stats["stored_witness_pair_upper_pass"] += 1
            stats["stored_witness_pair_upper_pass_mass"] += record[1]
            passing.append(record)
        else:
            stats["stored_witness_pair_upper_fail"] += 1
            stats["stored_witness_pair_upper_fail_mass"] += record[1]
            if len(first_failures) < 20:
                first_failures.append({
                    "mask_hex": record[0],
                    "state_macro_number": macro,
                    "failure": failure,
                })
    summary = {
        "stored_witnesses_checked": sum(
            row["stored_witnesses_checked"] for row in per_macro.values()
        ),
        "stored_witness_mass": sum(
            row["stored_witness_mass"] for row in per_macro.values()
        ),
        "stored_witness_pair_upper_pass": len(passing),
        "stored_witness_pair_upper_pass_mass": sum(row[1] for row in passing),
        "stored_witness_pair_upper_fail": sum(
            row["stored_witness_pair_upper_fail"] for row in per_macro.values()
        ),
        "stored_witness_pair_upper_fail_mass": sum(
            row["stored_witness_pair_upper_fail_mass"] for row in per_macro.values()
        ),
    }
    assert summary["stored_witnesses_checked"] == 5_138
    assert summary["stored_witness_mass"] == 1_129_056
    result = {
        "status": "DIRECT_STORED_WITNESS_PROBE_COMPLETE",
        "input": str(INPUT),
        "input_sha256": sha256(INPUT),
        "summary": summary,
        "per_macro": {
            str(macro): dict(sorted(row.items()))
            for macro, row in sorted(per_macro.items())
        },
        "first_failures": first_failures,
        "pair_upper_passing_stored_witnesses": passing,
        "claim_boundary": (
            "Passing is an explicit compatible 48-vertex witness.  Failure "
            "does not reject an exceptional mask because only one of its "
            "possibly many exact H/F CSP witnesses was materialized."
        ),
    }
    atomic_json(OUTPUT, result)
    print(json.dumps(summary, sort_keys=True), flush=True)


if __name__ == "__main__":
    run()
