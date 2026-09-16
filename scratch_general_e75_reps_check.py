"""Independent edge-list reconstruction audit of all E0=75 local reps."""

from __future__ import annotations

import itertools
import json
import math
from collections import Counter
from fractions import Fraction
from pathlib import Path

import scratch_general_e75_local_expansion as expansion
import scratch_general_e79_compression_audit as compression_base
import scratch_general_e79_local_audit as local79
from scratch_general_e78_local_ports_all import (
    forced_c4_support_bp_feasible,
    group_matchings,
)


INPUT_PATH = Path("scratch_general_e75_local_graph_reps.json")
PORT_PATH = Path("scratch_general_e75_port_audit.json")
OUTPUT_PATH = Path("scratch_general_e75_reps_check.json")


def key(partition, orbit_index):
    return tuple(sorted(partition, reverse=True)), orbit_index


def masks_and_actions(supports, deficits, vertices):
    pair_positions = tuple(itertools.combinations(range(len(vertices)), 2))
    pair_index = {pair: bit for bit, pair in enumerate(pair_positions)}
    vertex_index = {vertex: index for index, vertex in enumerate(vertices)}

    def graph_mask(graph):
        mask = 0
        for left, right in graph:
            pair = tuple(sorted((vertex_index[left], vertex_index[right])))
            mask |= 1 << pair_index[pair]
        return mask

    weight = dict(zip(supports, deficits))
    used = sorted(set().union(*map(set, supports)))
    actions = set()
    preserving = 0
    for permutation in itertools.permutations(range(7)):
        image_weight = {
            tuple(sorted((permutation[a], permutation[b]))): deficit
            for (a, b), deficit in weight.items()
        }
        if image_weight != weight:
            continue
        preserving += 1
        for flip_bits in itertools.product((0, 1), repeat=len(used)):
            flips = dict(zip(used, flip_bits))
            action = []
            for vertex in vertices:
                image = tuple(
                    sorted(
                        2 * permutation[symbol // 2]
                        + ((symbol % 2) ^ flips.get(symbol // 2, 0))
                        for symbol in vertex
                    )
                )
                action.append(vertex_index[image])
            actions.add(tuple(action))

    def image_masks(graph):
        mask = graph_mask(graph)
        images = set()
        for action in actions:
            work = mask
            image = 0
            while work:
                low = work & -work
                left, right = pair_positions[low.bit_length() - 1]
                image_pair = tuple(sorted((action[left], action[right])))
                image |= 1 << pair_index[image_pair]
                work ^= low
            images.add(image)
        return mask, images

    return graph_mask, image_masks, len(actions), preserving, len(used)


def main():
    source = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    port = json.loads(PORT_PATH.read_text(encoding="utf-8"))
    port_rows = {
        key(row["partition"], row["compression_orbit_index"]): row
        for row in port["rows"]
    }
    checked_rows = []
    total_orbits = 0
    total_raw = 0
    for row in source["support_rows"]:
        supports = tuple(tuple(item["support"]) for item in row["exceptional_supports"])
        deficits = tuple(item["deficit"] for item in row["exceptional_supports"])
        port_row = port_rows[key(deficits, row["compression_orbit_index"])]
        vertices = tuple(
            sorted(
                local79.vertex_label(support, bits)
                for support in supports
                for bits in itertools.product((0, 1), repeat=2)
            )
        )
        graph_mask, image_masks, action_count, preserving, used_groups = masks_and_actions(
            supports, deficits, vertices
        )
        fast_profiles = expansion.build_forced_c4_profiles(supports)
        assert preserving == row["weighted_stabilizer_order"]
        assert action_count == row["symmetry_actions"]
        assert (
            preserving // math.factorial(7 - used_groups) * 2 ** used_groups
            == action_count
        )
        canonical_seen = set()
        orbit_sizes = Counter()
        square_raw = Counter()
        for representative in row["representatives"]:
            graph = frozenset(
                tuple(sorted((tuple(left), tuple(right))))
                for left, right in representative["edges"]
            )
            assert len(graph) == len(representative["edges"])
            assert all(left in vertices and right in vertices for left, right in graph)
            oriented = []
            for support, deficit in zip(supports, deficits):
                fibre_vertices = frozenset(
                    local79.vertex_label(support, bits)
                    for bits in itertools.product((0, 1), repeat=2)
                )
                internal = frozenset(
                    edge
                    for edge in graph
                    if edge[0] in fibre_vertices and edge[1] in fibre_vertices
                )
                matches = [
                    expansion.fibre_variant(support, deficit, state_index)
                    for state_index in range(len(expansion.port75.FIBRE_STATES[deficit]))
                    if expansion.fibre_variant(support, deficit, state_index)["internal"]
                    == internal
                ]
                assert len(matches) == 1
                oriented.append(matches[0])
            oriented = tuple(oriented)
            internal = frozenset(edge for data in oriented for edge in data["internal"])
            overlap = graph - internal
            assert len(overlap) == 18
            assigned_group_edges = set()
            support_of = {
                vertex: support
                for support, data in zip(supports, oriented)
                for vertex in data["vertices"]
            }
            for group in range(7):
                group_edges = frozenset(
                    edge
                    for edge in overlap
                    if group in set(support_of[edge[0]]) & set(support_of[edge[1]])
                )
                assert group_edges in group_matchings(oriented, group)
                assigned_group_edges.update(group_edges)
            assert assigned_group_edges == set(overlap)
            assert local79.induced_pair_upper(vertices, graph)
            assert forced_c4_support_bp_feasible(supports, oriented, graph)
            assert expansion.forced_c4_support_bp_fast(
                supports, oriented, graph, fast_profiles
            )
            fibre_of = {
                vertex: index
                for index, data in enumerate(oriented)
                for vertex in data["vertices"]
            }
            blocks = Counter(
                tuple(sorted((fibre_of[left], fibre_of[right])))
                for left, right in overlap
            )
            m2 = sum(value * value for value in blocks.values())
            assert m2 + Fraction(port_row["disjoint_continuous_minimum"]) <= port_row[
                "joint_square_budget"
            ]
            square_raw[m2] += representative["orbit_size"]
            mask, images = image_masks(graph)
            assert mask == int(representative["mask_hex"], 16)
            assert mask == min(images)
            assert len(images) == representative["orbit_size"]
            assert mask not in canonical_seen
            canonical_seen.add(mask)
            orbit_sizes[len(images)] += 1
        raw = sum(size * multiplicity for size, multiplicity in orbit_sizes.items())
        assert raw == row["raw_survivors"]
        assert len(canonical_seen) == row["orbit_count"]
        assert {str(k): v for k, v in sorted(orbit_sizes.items())} == row[
            "orbit_size_histogram"
        ]
        total_raw += raw
        total_orbits += len(canonical_seen)
        checked_rows.append(
            {
                "partition": row["partition"],
                "compression_orbit_index": row["compression_orbit_index"],
                "weighted_stabilizer_order": preserving,
                "used_root_groups": used_groups,
                "symmetry_actions": action_count,
                "raw_graphs_checked": raw,
                "orbits_checked": len(canonical_seen),
                "orbit_size_histogram": {
                    str(k): v for k, v in sorted(orbit_sizes.items())
                },
                "overlap_square_raw_histogram": {
                    str(k): v for k, v in sorted(square_raw.items())
                },
            }
        )
    assert len(checked_rows) == 6
    assert total_orbits == 352
    assert total_raw == 110592
    result = {
        "status": "VERIFIED",
        "model": "independent edge-list reconstruction audit of every E0=75 local representative",
        "input": str(INPUT_PATH),
        "checks": [
            "valid unique low-vertex edge lists",
            "exactly one allowed induced state in every exceptional fibre",
            "exact 18-edge coordinate-port matching product",
            "induced exceptional-pair upper bound",
            "ordinary-C4 forced support BP by both original and optimized implementations",
            "actual-overlap plus exact-real disjoint spectral bound",
            "canonical minimum and orbit size under weighted stabilizer and bit flips",
            "per-row orbit sizes sum to raw survivor count",
        ],
        "support_rows_checked": len(checked_rows),
        "orbits_checked": total_orbits,
        "raw_graphs_checked": total_raw,
        "rows": checked_rows,
    }
    OUTPUT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("status", "support_rows_checked", "orbits_checked", "raw_graphs_checked")}))


if __name__ == "__main__":
    main()
