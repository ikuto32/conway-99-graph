"""Independent edge-list/orbit audit of every E0=73, Q>=4 local representative.

This deliberately reconstructs each exceptional-fibre state, every overlap
matching, the two local feasibility filters, and the complete symmetry orbit
from the stored edge lists.  It does not trust the producer's masks or orbit
sizes.  The only imported routines are the already separately tested primitive
catalogues/filters used throughout the E75--E73 pipeline.
"""

from __future__ import annotations

import itertools
import json
import math
from collections import Counter
from fractions import Fraction
from pathlib import Path

import scratch_general_e75_local_expansion as expansion
import scratch_general_e73_q4_local_expansion as e73_config
import scratch_general_e79_local_audit as local79
from scratch_general_e78_local_ports_all import (
    forced_c4_support_bp_feasible,
    group_matchings,
)


INPUT_PATH = Path("scratch_general_e73_q4_local_graph_reps.json")
PORT_PATH = Path("scratch_general_e73_q4_port_feasible_states.json")
OUTPUT_PATH = Path("scratch_root_e73_q4_local_reps_audit.json")
FIBRE_BIT_ROWS = tuple(itertools.product((0, 1), repeat=2))
FIBRE_DIAGONALS = frozenset(
    pair
    for pair in itertools.combinations(range(4), 2)
    if all(FIBRE_BIT_ROWS[pair[0]][axis] != FIBRE_BIT_ROWS[pair[1]][axis]
           for axis in (0, 1))
)


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
    # Configure the generic E75 engine with E73 paths and constants before any
    # catalogue helper is used.
    e73_config.configure()
    source = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    port = json.loads(PORT_PATH.read_text(encoding="utf-8"))
    port_rows = {
        key(row["partition"], row["compression_orbit_index"]): row
        for row in port["rows"]
    }
    checked_rows = []
    total_orbits = 0
    total_raw = 0
    all_canonical_keys = set()
    for row in source["support_rows"]:
        supports = tuple(tuple(item["support"]) for item in row["exceptional_supports"])
        deficits = tuple(item["deficit"] for item in row["exceptional_supports"])
        assert sum(deficits) == 11
        port_row = port_rows[key(deficits, row["compression_orbit_index"])]
        vertices = tuple(
            sorted(
                local79.vertex_label(support, bits)
                for support in supports
                for bits in itertools.product((0, 1), repeat=2)
            )
        )
        _graph_mask, image_masks, action_count, preserving, used_groups = (
            masks_and_actions(supports, deficits, vertices)
        )
        fast_profiles = expansion.build_forced_c4_profiles(supports)
        assert preserving == row["weighted_stabilizer_order"]
        assert action_count == row["symmetry_actions"]
        assert preserving // math.factorial(7 - used_groups) * 2 ** used_groups == action_count
        canonical_seen = set()
        orbit_union = set()
        orbit_sizes = Counter()
        square_raw = Counter()
        q_raw = Counter()
        for representative in row["representatives"]:
            graph = frozenset(
                tuple(sorted((tuple(left), tuple(right))))
                for left, right in representative["edges"]
            )
            assert len(graph) == len(representative["edges"])
            assert all(left in vertices and right in vertices for left, right in graph)
            oriented = []
            q_value = 0
            for support, deficit in zip(supports, deficits):
                fibre_vertices = frozenset(
                    local79.vertex_label(support, bits)
                    for bits in itertools.product((0, 1), repeat=2)
                )
                internal = frozenset(
                    edge for edge in graph
                    if edge[0] in fibre_vertices and edge[1] in fibre_vertices
                )
                matches = [
                    expansion.fibre_variant(support, deficit, state_index)
                    for state_index in range(len(expansion.port75.FIBRE_STATES[deficit]))
                    if expansion.fibre_variant(support, deficit, state_index)["internal"] == internal
                ]
                assert len(matches) == 1
                oriented.append(matches[0])
                raw_state = expansion.port75.FIBRE_STATES[deficit][matches[0]["state_index"]]
                q_value += sum(tuple(edge) in FIBRE_DIAGONALS for edge in raw_state["edges"])
            oriented = tuple(oriented)
            assert q_value == representative["Q"] == 4
            internal = frozenset(edge for data in oriented for edge in data["internal"])
            overlap = graph - internal
            assert len(overlap) == 22
            assert len(internal) == 4 * len(supports) - 11
            assigned_group_edges = set()
            support_of = {
                vertex: support
                for support, data in zip(supports, oriented)
                for vertex in data["vertices"]
            }
            for group in range(7):
                group_edges = frozenset(
                    edge for edge in overlap
                    if group in set(support_of[edge[0]]) & set(support_of[edge[1]])
                )
                assert group_edges in group_matchings(oriented, group)
                assigned_group_edges.update(group_edges)
            assert assigned_group_edges == set(overlap)
            assert local79.induced_pair_upper(vertices, graph)
            assert forced_c4_support_bp_feasible(supports, oriented, graph)
            assert expansion.forced_c4_support_bp_fast(supports, oriented, graph, fast_profiles)
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
            assert m2 + Fraction(port_row["disjoint_continuous_minimum"]) <= port_row["joint_square_budget"]
            mask, images = image_masks(graph)
            assert mask == int(representative["mask_hex"], 16)
            assert mask == min(images)
            assert len(images) == representative["orbit_size"]
            assert mask not in canonical_seen
            assert not (orbit_union & images)
            canonical_seen.add(mask)
            orbit_union.update(images)
            orbit_sizes[len(images)] += 1
            square_raw[m2] += len(images)
            q_raw[q_value] += len(images)
            intrinsic = (tuple(sorted(deficits, reverse=True)), row["compression_orbit_index"], mask)
            assert intrinsic not in all_canonical_keys
            all_canonical_keys.add(intrinsic)
        raw = len(orbit_union)
        assert raw == row["raw_survivors"]
        assert raw == sum(size * multiplicity for size, multiplicity in orbit_sizes.items())
        assert len(canonical_seen) == row["orbit_count"]
        assert {str(k): v for k, v in sorted(orbit_sizes.items())} == row["orbit_size_histogram"]
        total_raw += raw
        total_orbits += len(canonical_seen)
        checked_rows.append({
            "partition": row["partition"],
            "compression_orbit_index": row["compression_orbit_index"],
            "weighted_stabilizer_order": preserving,
            "used_root_groups": used_groups,
            "symmetry_actions": action_count,
            "raw_graphs_checked": raw,
            "orbits_checked": len(canonical_seen),
            "orbit_size_histogram": {str(k): v for k, v in sorted(orbit_sizes.items())},
            "overlap_square_raw_histogram": {str(k): v for k, v in sorted(square_raw.items())},
            "Q_raw_histogram": {str(k): v for k, v in sorted(q_raw.items())},
        })
    assert len(checked_rows) == 6
    assert total_orbits == 1804
    assert total_raw == 98304
    result = {
        "status": "VERIFIED",
        "model": "independent edge-list/orbit audit of every E0=73,Q>=4 local representative",
        "input": str(INPUT_PATH),
        "checks": [
            "valid unique exceptional-vertex edge lists",
            "exactly one allowed state in every exceptional fibre",
            "exact 22-edge coordinate-port matching product",
            "induced exceptional-pair upper bound",
            "ordinary-C4 forced support BP by original and optimized implementations",
            "actual overlap plus exact-real disjoint spectral bound",
            "canonical minimum, disjoint orbits, and exact orbit size under full residual symmetry",
            "per-row orbit union equals raw survivor count",
        ],
        "support_rows_checked": len(checked_rows),
        "orbits_checked": total_orbits,
        "raw_graphs_checked": total_raw,
        "all_representatives_have_Q": 4,
        "rows": checked_rows,
    }
    OUTPUT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        key: result[key]
        for key in ("status", "support_rows_checked", "orbits_checked", "raw_graphs_checked")
    }))


if __name__ == "__main__":
    main()
