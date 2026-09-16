"""Independent normalization and local-condition check of E76 representatives."""

from __future__ import annotations

import itertools
import json
import math
from collections import Counter
from fractions import Fraction
from pathlib import Path

import scratch_general_e79_local_audit as local79
from scratch_general_e78_local_ports_all import (
    fibre_variants,
    forced_c4_support_bp_feasible,
    group_matchings,
)


INPUT_PATH = Path("scratch_general_e76_local_graph_reps.json")
PORT_PATH = Path("scratch_general_e76_port_audit.json")
OUTPUT_PATH = Path("scratch_general_e76_reps_check.json")


def key(partition, orbit_index):
    return tuple(sorted(partition, reverse=True)), orbit_index


def weighted_group_permutations(supports, deficits):
    weighted = dict(zip(supports, deficits))
    return tuple(
        permutation
        for permutation in itertools.permutations(range(7))
        if {
            tuple(sorted((permutation[a], permutation[b]))): weight
            for (a, b), weight in weighted.items()
        }
        == weighted
    )


def graph_mask(vertices, graph):
    positions = {
        pair: index for index, pair in enumerate(itertools.combinations(range(len(vertices)), 2))
    }
    indices = {vertex: index for index, vertex in enumerate(vertices)}
    mask = 0
    for left, right in graph:
        pair = tuple(sorted((indices[left], indices[right])))
        mask |= 1 << positions[pair]
    return mask


def image_masks(supports, deficits, vertices, graph):
    used = sorted(set().union(*map(set, supports)))
    indices = {vertex: index for index, vertex in enumerate(vertices)}
    pair_positions = tuple(itertools.combinations(range(len(vertices)), 2))
    pair_index = {pair: bit for bit, pair in enumerate(pair_positions)}
    base_mask = graph_mask(vertices, graph)
    images = set()
    for permutation in weighted_group_permutations(supports, deficits):
        for bits in itertools.product((0, 1), repeat=len(used)):
            flips = dict(zip(used, bits))
            vertex_action = []
            for vertex in vertices:
                mapped = tuple(
                    sorted(
                        2 * permutation[symbol // 2]
                        + ((symbol % 2) ^ flips.get(symbol // 2, 0))
                        for symbol in vertex
                    )
                )
                vertex_action.append(indices[mapped])
            image = 0
            work = base_mask
            while work:
                low = work & -work
                u, v = pair_positions[low.bit_length() - 1]
                image_pair = tuple(sorted((vertex_action[u], vertex_action[v])))
                image |= 1 << pair_index[image_pair]
                work ^= low
            images.add(image)
    return images


def main():
    source = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    port = json.loads(PORT_PATH.read_text(encoding="utf-8"))
    port_rows = {
        key(row["partition"], row["orbit_index"]): row
        for row in port["rows"]
    }
    checked_rows = []
    total_orbits = 0
    total_raw = 0
    for row in source["support_rows"]:
        supports = tuple(tuple(support) for support in row["supports"])
        deficits = tuple(row["partition"])
        port_row = port_rows[key(deficits, row["orbit_index"])]
        vertices = tuple(
            sorted(
                local79.vertex_label(support, bits)
                for support in supports
                for bits in itertools.product((0, 1), repeat=2)
            )
        )
        domains = tuple(
            fibre_variants(support, deficit)
            for support, deficit in zip(supports, deficits)
        )
        canonical_seen = set()
        orbit_size_histogram = Counter()
        overlap_square_histogram = Counter()
        for representative in row["representatives"]:
            graph = frozenset(
                tuple(sorted((tuple(left), tuple(right))))
                for left, right in representative["edges"]
            )
            assert len(graph) == len(representative["edges"])
            assert all(left in vertices and right in vertices for left, right in graph)
            oriented = []
            for support, domain in zip(supports, domains):
                fibre_vertices = frozenset(
                    local79.vertex_label(support, bits)
                    for bits in itertools.product((0, 1), repeat=2)
                )
                internal = frozenset(
                    edge for edge in graph if edge[0] in fibre_vertices and edge[1] in fibre_vertices
                )
                matches = [choice for choice in domain if choice["internal"] == internal]
                assert len(matches) == 1
                oriented.append(matches[0])
            oriented = tuple(oriented)
            internal = frozenset(edge for choice in oriented for edge in choice["internal"])
            overlap = graph - internal
            assert len(overlap) == 16
            # Reconstruct the exact coordinate-matching product independently.
            for group in range(7):
                group_edges = frozenset(
                    edge
                    for edge in overlap
                    if group in {
                        symbol // 2 for symbol in edge[0]
                    }
                    & {symbol // 2 for symbol in edge[1]}
                )
                assert group_edges in group_matchings(oriented, group)
            assert local79.induced_pair_upper(vertices, graph)
            assert forced_c4_support_bp_feasible(supports, oriented, graph)
            fibre_of = {
                vertex: index
                for index, choice in enumerate(oriented)
                for vertex in choice["vertices"]
            }
            blocks = Counter(
                tuple(sorted((fibre_of[left], fibre_of[right])))
                for left, right in overlap
            )
            m2 = sum(value * value for value in blocks.values())
            assert m2 + Fraction(port_row["disjoint_continuous_minimum"]) <= port_row[
                "joint_square_budget"
            ]
            overlap_square_histogram[m2] += representative["orbit_size"]
            images = image_masks(supports, deficits, vertices, graph)
            mask = graph_mask(vertices, graph)
            assert mask == int(representative["mask_hex"], 16)
            assert mask == min(images)
            assert len(images) == representative["orbit_size"]
            assert mask not in canonical_seen
            canonical_seen.add(mask)
            orbit_size_histogram[len(images)] += 1
        raw = sum(
            int(size) * multiplicity
            for size, multiplicity in orbit_size_histogram.items()
        )
        assert raw == row["raw_survivors"]
        assert len(canonical_seen) == row["orbit_count"]
        assert {str(k): v for k, v in sorted(orbit_size_histogram.items())} == row[
            "orbit_size_histogram"
        ]
        total_orbits += len(canonical_seen)
        total_raw += raw
        checked_rows.append(
            {
                "partition": list(deficits),
                "orbit_index": row["orbit_index"],
                "weighted_group_stabilizer_order": len(
                    weighted_group_permutations(supports, deficits)
                ),
                "used_groups": len(set().union(*map(set, supports))),
                "local_symmetry_actions_expected": row["symmetry_actions"],
                "orbits_checked": len(canonical_seen),
                "raw_graphs_checked": raw,
                "orbit_size_histogram": {
                    str(k): v for k, v in sorted(orbit_size_histogram.items())
                },
                "overlap_square_raw_histogram": {
                    str(k): v for k, v in sorted(overlap_square_histogram.items())
                },
            }
        )
        assert (
            checked_rows[-1]["weighted_group_stabilizer_order"]
            // math.factorial(7 - checked_rows[-1]["used_groups"])
            * 2 ** checked_rows[-1]["used_groups"]
            == row["symmetry_actions"]
        )
    assert total_orbits == 311
    assert total_raw == 68864
    result = {
        "status": "VERIFIED",
        "model": "independent normalization/local-condition audit of E0=76 representative JSON",
        "input": str(INPUT_PATH),
        "checks": [
            "edge-list uniqueness and vertex membership",
            "one allowed labelled fibre state in each support fibre",
            "exact 16-edge coordinate-port matching product",
            "induced common-neighbour pair upper bound",
            "forced ordinary-C4 support BP equations",
            "exact-real joint-square necessary bound",
            "canonical minimum and exact orbit size under weighted support stabilizer and bit flips",
            "per-row orbit sizes sum to raw survivor count",
        ],
        "support_rows_checked": len(checked_rows),
        "orbits_checked": total_orbits,
        "raw_graphs_checked": total_raw,
        "rows": checked_rows,
    }
    OUTPUT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("status", "support_rows_checked", "orbits_checked", "raw_graphs_checked")}))


if __name__ == "__main__":
    main()
