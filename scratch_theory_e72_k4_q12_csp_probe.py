"""Diagnostic probe for the dominant E72 K4-support Q=12 macro branch.

This uses the existing exact local objects, but reports only small binary-CSP
statistics intended to expose a human-readable obstruction.  It is not by
itself an exclusion certificate.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import scratch_general_e72_q3_fast_expansion as fast


OUTPUT = Path("scratch_theory_e72_k4_q12_csp_probe.json")


def component_sizes(adjacency):
    unseen = set(range(len(adjacency)))
    answer = []
    while unseen:
        start = min(unseen)
        seen = {start}
        stack = [start]
        while stack:
            vertex = stack.pop()
            for other in adjacency[vertex]:
                if other not in seen:
                    seen.add(other)
                    stack.append(other)
        unseen.difference_update(seen)
        answer.append(len(seen))
    return sorted(answer)


def bipartite(adjacency):
    colours = {}
    for start in range(len(adjacency)):
        if start in colours:
            continue
        colours[start] = 0
        stack = [start]
        while stack:
            vertex = stack.pop()
            for other in adjacency[vertex]:
                if other in colours:
                    if colours[other] == colours[vertex]:
                        return False
                else:
                    colours[other] = 1 - colours[vertex]
                    stack.append(other)
    return True


def graph_invariants(geometry, mask, internal_mask):
    adjacency = [set() for _ in geometry.vertices]
    side_adjacency = [set() for _ in geometry.vertices]
    edges = []
    for bit, (left, right) in enumerate(geometry.pair_positions):
        if not ((mask >> bit) & 1):
            continue
        adjacency[left].add(right)
        adjacency[right].add(left)
        edges.append([list(geometry.vertices[left]), list(geometry.vertices[right])])
        if not ((internal_mask >> bit) & 1):
            side_adjacency[left].add(right)
            side_adjacency[right].add(left)
    assert set(map(len, adjacency)) == {3}
    assert set(map(len, side_adjacency)) == {2}

    common_histogram = Counter()
    four_cycle_numerators = 0
    for left in range(len(adjacency)):
        for right in range(left + 1, len(adjacency)):
            common = len(adjacency[left] & adjacency[right])
            direct = int(right in adjacency[left])
            shared = len(set(geometry.vertices[left]) & set(geometry.vertices[right]))
            common_histogram[(shared, direct, common)] += 1
            four_cycle_numerators += common * (common - 1) // 2
    assert four_cycle_numerators % 2 == 0

    # Exact Gram coordinates in the basis a,b with
    # <a,a>=<b,b>=4, <a,b>=-2 and c=-a-b.
    support_class = {
        (0, 1): (1, 0),
        (2, 3): (1, 0),
        (0, 2): (0, 1),
        (1, 3): (0, 1),
        (0, 3): (-1, -1),
        (1, 2): (-1, -1),
    }
    fibre_vectors = [support_class[support] for support in geometry.supports]
    residual_norm_histogram = Counter()
    residual_vectors = []
    for vertex in range(len(adjacency)):
        x = sum(fibre_vectors[geometry.fibre_index[other]][0] for other in adjacency[vertex])
        y = sum(fibre_vectors[geometry.fibre_index[other]][1] for other in adjacency[vertex])
        norm = 4 * (x * x + y * y - x * y)
        residual_vectors.append([x, y])
        residual_norm_histogram[norm] += 1

    return {
        "component_sizes": component_sizes(adjacency),
        "bipartite": bipartite(adjacency),
        "side_two_factor_cycle_lengths": component_sizes(side_adjacency),
        "four_cycle_count": four_cycle_numerators // 2,
        "pair_common_histogram": [
            {
                "shared_signed_symbols": key[0],
                "direct": key[1],
                "local_common_neighbours": key[2],
                "pair_count": value,
            }
            for key, value in sorted(common_histogram.items())
        ],
        "local_Gram_residual_norm_histogram": {
            str(key): value for key, value in sorted(residual_norm_histogram.items())
        },
        "local_Gram_residual_norm_sum": sum(
            norm * count for norm, count in residual_norm_histogram.items()
        ),
        "local_Gram_residual_vectors_in_vertex_order": residual_vectors,
        "vertex_order": [list(vertex) for vertex in geometry.vertices],
        "edges": edges,
    }


def main():
    preset = fast.PRESETS["e72gram"]
    fast.configure_generic(preset)
    _port, grouped = fast.input_rows(preset)
    source = next(
        row
        for row, _count in grouped[27]
        if row["compression_orbit_index"] == 1
    )
    geometry = fast.RowGeometry(source)
    state = next(item for item in fast.state_orbits(source, geometry) if item["Q"] == 12)
    oriented = fast.oriented_assignment(geometry, state["state_indices"])
    by_group = fast.matching_choices(geometry, oriented, state["state_indices"], {})
    gram = fast.GramSignatureFilter(geometry)
    products, gram_stats = gram.feasible_classes(by_group)
    assert len(products) == 1
    choices = products[0]

    pair_search = fast.PairSearch(
        geometry, oriented, state["internal_mask"], build_bp=True
    )
    raw_counts = [len(values) for values in choices]
    pair_single_counts = [
        sum(pair_search.choice_is_pair_valid_from_base(choice) for choice in values)
        for values in choices
    ]
    pair_csp = fast.ForcedBPCSP(pair_search, choices)
    pair_products, pair_product_stats = pair_csp.signature_class_products()

    # Build the same support-aggregate BP relations without first deleting a
    # group choice merely because that one group plus the internal matching
    # already violates an induced-pair upper bound.
    bp_search = fast.PairSearch(
        geometry, oriented, state["internal_mask"], build_bp=True
    )
    bp_search.choice_is_pair_valid_from_base = lambda _choice: True
    bp_csp = fast.ForcedBPCSP(bp_search, choices)
    bp_products, bp_product_stats = bp_csp.signature_class_products()

    # Every Q=12 BP signature bucket happens to be a singleton.  Materialize
    # the resulting 64 tiny graphs and classify their exact pair violations.
    assert all(
        len(bucket) == 1
        for product in bp_products
        for bucket in product
    )
    bp_masks = []
    violation_histogram = Counter()
    first_violations = []
    per_graph_violation_counts = Counter()
    for product in bp_products:
        mask = state["internal_mask"]
        for bucket in product:
            mask |= bucket[0].mask
        bp_masks.append(mask)
        adjacency = [0] * len(geometry.vertices)
        for bit, (left, right) in enumerate(geometry.pair_positions):
            if (mask >> bit) & 1:
                adjacency[left] |= 1 << right
                adjacency[right] |= 1 << left
        violations = []
        for left in range(len(geometry.vertices)):
            for right in range(left + 1, len(geometry.vertices)):
                direct = (adjacency[left] >> right) & 1
                common = (adjacency[left] & adjacency[right]).bit_count()
                shared = len(set(geometry.vertices[left]) & set(geometry.vertices[right]))
                target = 2 - shared
                if direct + common <= target:
                    continue
                left_fibre = geometry.fibre_index[left]
                right_fibre = geometry.fibre_index[right]
                key = (
                    shared,
                    direct,
                    common,
                    len(set(geometry.supports[left_fibre]) & set(geometry.supports[right_fibre])),
                )
                violation_histogram[key] += 1
                violations.append((left, right, key))
        per_graph_violation_counts[len(violations)] += 1
        if len(first_violations) < 8:
            first_violations.append(
                {
                    "graph_number": len(bp_masks) - 1,
                    "violation_count": len(violations),
                    "first": [
                        {
                            "vertices": [
                                list(geometry.vertices[left]),
                                list(geometry.vertices[right]),
                            ],
                            "supports": [
                                list(geometry.supports[geometry.fibre_index[left]]),
                                list(geometry.supports[geometry.fibre_index[right]]),
                            ],
                            "shared_signed_symbols": key[0],
                            "direct": key[1],
                            "local_common_neighbours": key[2],
                            "support_intersection_size": key[3],
                        }
                        for left, right, key in violations[:4]
                    ],
                }
            )
    assert len(set(bp_masks)) == 64
    bp_orbits = []
    bp_orbit_records = []
    remaining = set(bp_masks)
    while remaining:
        seed = min(remaining)
        orbit = {
            geometry.transform_local_graph(seed, state["internal_mask"], action)
            for action in state["stabilizer"]
        }
        orbit.intersection_update(bp_masks)
        bp_orbits.append(len(orbit))
        bp_orbit_records.append(
            {
                "representative_mask_hex": hex(seed),
                "orbit_size": len(orbit),
                "invariants": graph_invariants(
                    geometry, seed, state["internal_mask"]
                ),
            }
        )
        remaining.difference_update(orbit)

    relation_stats = []
    for left in range(4):
        for right in sorted(pair_csp.neighbours[left]):
            if left >= right:
                continue
            compatible_pairs = sum(
                bool(pair_csp.compatible_mask(left, option, right) & (1 << other))
                for option in range(len(pair_csp.by_group[left]))
                for other in range(len(pair_csp.by_group[right]))
            )
            relation_stats.append(
                {
                    "groups": [left, right],
                    "left_options": len(pair_csp.by_group[left]),
                    "right_options": len(pair_csp.by_group[right]),
                    "compatible_option_pairs": compatible_pairs,
                }
            )

    result = {
        "status": "DIAGNOSTIC_ONLY",
        "branch": {
            "partition_index": 27,
            "compression_orbit_index": 1,
            "source_row_index": source["source_row_index"],
            "supports": [item["support"] for item in source["exceptional_supports"]],
            "state_indices": list(state["state_indices"]),
            "Q": state["Q"],
            "state_orbit_weight": state["weight"],
        },
        "gram_signature": gram_stats,
        "raw_group_choice_counts": raw_counts,
        "single_group_pair_valid_counts": pair_single_counts,
        "pair_prefilter_then_BP": {
            "impossible_at_domain_construction": pair_csp.impossible,
            "signature_products": len(pair_products),
            "statistics": pair_product_stats,
            "relation_statistics": relation_stats,
        },
        "BP_without_pair_prefilter": {
            "impossible_at_domain_construction": bp_csp.impossible,
            "signature_products": len(bp_products),
            "statistics": bp_product_stats,
            "raw_graphs": len(bp_masks),
            "raw_graph_orbit_sizes_under_state_stabilizer": sorted(bp_orbits),
            "raw_graph_orbits": bp_orbit_records,
            "graphs_by_pair_violation_count": {
                str(key): value for key, value in sorted(per_graph_violation_counts.items())
            },
            "pair_violation_type_histogram": [
                {
                    "shared_signed_symbols": key[0],
                    "direct": key[1],
                    "local_common_neighbours": key[2],
                    "support_intersection_size": key[3],
                    "occurrences": value,
                }
                for key, value in sorted(violation_histogram.items())
            ],
            "sample_violations": first_violations,
        },
        "claim_boundary": (
            "Diagnostic decomposition only; a zero signature-product count is "
            "an exact finite CSP result but is not yet presented as an independent proof."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
