"""Classify the pair-upper failures in the source-724 degree witness.

This is deliberately a *boundary* experiment.  The input is one completely
materialised binary 84-vertex graph satisfying the source-724 fibre totals and
the defect Gram identity.  It is not an enumeration of the whole macro.

For every positive SRG pair residual we record

* exceptional/ordinary and same/overlap/disjoint fibre type;
* a small port-degree type for both endpoints;
* the minimum number of outer common witnesses needed for a contradiction;
* a minimum-order induced rooted, layer-marked certificate; and
* how many of the certificate's proof edges came from freely materialised
  disjoint-support blocks.

We also test the strongest elementary one-pair pigeonhole consequence of the
fixed fibre degree rows.  Its failure to reject any pair is an exact statement
about this degree witness and prevents us from mislabelling the 1,025 failures
of one greedy completion as a universal macro cut.
"""

from __future__ import annotations

from collections import Counter
from functools import lru_cache
import hashlib
import itertools
import json
import os
from pathlib import Path

from scratch_theory_e71_defect_rank_probe import CATALOG, SUPPORTS


WITNESS = Path("scratch_theory_e71_source724_degree_witness.json")
OUTPUT = Path("scratch_theory_e71_source724_pair_violation_discovery.json")
DEFECT_PROBE = Path("scratch_theory_e71_defect_rank_probe.json")
ORDER8_BOUNDARY = Path("scratch_root_order8_e0_lower_bound_boundary.json")
YYT_SHADOW = Path("scratch_theory_root_yyt_order8_shadow.json")
FOUR_ROOT_DERIVATION = Path(
    "external_conway99_research/attempts/wave152-four-root-order8/derivation.md"
)
WAVE159_README = Path(
    "external_conway99_research/attempts/wave159-four-root-cut-loop/README.md"
)


def atomic_json(path: Path, value) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def vertex_label(vertex: int) -> tuple[int, int]:
    support = SUPPORTS[vertex // 4]
    local = vertex % 4
    return 2 * support[0] + local // 2, 2 * support[1] + local % 2


def fibre_relation(left: int, right: int) -> str:
    left_support = SUPPORTS[left // 4]
    right_support = SUPPORTS[right // 4]
    if left_support == right_support:
        return "same"
    if set(left_support) & set(right_support):
        return "overlap"
    return "disjoint"


def refine_partition(adjacency: tuple[int, ...], partition):
    """Canonical equitable refinement of an ordered colour partition."""
    partition = tuple(tuple(cell) for cell in partition if cell)
    while True:
        masks = tuple(sum(1 << vertex for vertex in cell) for cell in partition)
        refined = []
        changed = False
        for cell in partition:
            buckets = {}
            for vertex in cell:
                signature = tuple((adjacency[vertex] & mask).bit_count()
                                  for mask in masks)
                buckets.setdefault(signature, []).append(vertex)
            if len(buckets) > 1:
                changed = True
            for signature in sorted(buckets):
                refined.append(tuple(sorted(buckets[signature])))
        refined = tuple(refined)
        if not changed:
            return refined
        partition = refined


def adjacency_mask(adjacency: tuple[int, ...], order: tuple[int, ...]) -> int:
    answer = 0
    bit = 0
    for row in range(len(order)):
        for column in range(row + 1, len(order)):
            if (adjacency[order[row]] >> order[column]) & 1:
                answer |= 1 << bit
            bit += 1
    return answer


def coloured_canonical_mask(adjacency: tuple[int, ...], roles: tuple[int, ...]):
    """Exact canonical mask under permutations preserving the four roles.

    Roles are root, root-neighbour, marked endpoint, and selected common
    witness.  Individualisation/refinement keeps this exact without requiring
    n! brute force on certificates of order up to sixteen.
    """
    initial = tuple(tuple(vertex for vertex, role in enumerate(roles)
                          if role == colour)
                    for colour in sorted(set(roles)))
    visited = 0

    @lru_cache(maxsize=None)
    def visit(partition):
        nonlocal visited
        visited += 1
        partition = refine_partition(adjacency, partition)
        split = next((index for index, cell in enumerate(partition)
                      if len(cell) > 1), None)
        if split is None:
            order = tuple(cell[0] for cell in partition)
            return adjacency_mask(adjacency, order), order
        cell = partition[split]
        best = None
        for vertex in cell:
            remainder = tuple(other for other in cell if other != vertex)
            child = partition[:split] + ((vertex,), remainder) + partition[split + 1:]
            candidate = visit(child)
            if best is None or candidate[0] < best[0]:
                best = candidate
        assert best is not None
        return best

    mask, order = visit(initial)
    return mask, order, visited


def rooted_certificate(left, right, witnesses, adjacency, labels):
    witnesses = tuple(sorted(witnesses))
    outer = (left, right) + witnesses
    root_labels = tuple(sorted({label for vertex in outer for label in labels[vertex]}))
    label_index = {label: 1 + index for index, label in enumerate(root_labels)}
    first_outer = 1 + len(root_labels)
    order = 1 + len(root_labels) + len(outer)
    local_adjacency = [0] * order

    def add(x, y):
        local_adjacency[x] |= 1 << y
        local_adjacency[y] |= 1 << x

    for label in root_labels:
        add(0, label_index[label])
    for first, second in itertools.combinations(root_labels, 2):
        if first // 2 == second // 2:
            add(label_index[first], label_index[second])
    for outer_index, vertex in enumerate(outer):
        local_vertex = first_outer + outer_index
        for label in labels[vertex]:
            add(local_vertex, label_index[label])
    for first_index, first in enumerate(outer):
        for second_index in range(first_index + 1, len(outer)):
            second = outer[second_index]
            if (adjacency[first] >> second) & 1:
                add(first_outer + first_index, first_outer + second_index)

    roles = ((0,) + (1,) * len(root_labels) + (2, 2)
             + (3,) * len(witnesses))
    mask, canonical_order, search_nodes = coloured_canonical_mask(
        tuple(local_adjacency), roles
    )
    proof_edges = []
    if (adjacency[left] >> right) & 1:
        proof_edges.append((left, right))
    for witness in witnesses:
        assert (adjacency[left] >> witness) & 1
        assert (adjacency[right] >> witness) & 1
        proof_edges.extend(((left, witness), (right, witness)))
    proof_free = sum(fibre_relation(x, y) == "disjoint"
                     for x, y in proof_edges)
    induced_free = sum(
        fibre_relation(x, y) == "disjoint"
        and ((adjacency[x] >> y) & 1)
        for x, y in itertools.combinations(outer, 2)
    )
    return {
        "order": order,
        "root_neighbour_vertices": len(root_labels),
        "outer_common_witnesses": list(witnesses),
        "root_neighbour_labels": list(root_labels),
        "canonical_layer_marked_mask_hex": hex(mask),
        "induced_edges": sum(value.bit_count() for value in local_adjacency) // 2,
        "canonical_search_nodes": search_nodes,
        "proof_edges_from_free_disjoint_blocks": proof_free,
        "induced_edges_from_free_disjoint_blocks": induced_free,
        "support_groups_used": len({label // 2 for label in root_labels}),
        "canonical_vertex_order_debug": list(canonical_order),
    }


def main():
    witness_raw = WITNESS.read_bytes()
    catalog_raw = CATALOG.read_bytes()
    defect_probe_raw = DEFECT_PROBE.read_bytes()
    boundary_raw = ORDER8_BOUNDARY.read_bytes()
    shadow_raw = YYT_SHADOW.read_bytes()
    four_root_raw = FOUR_ROOT_DERIVATION.read_bytes()
    wave159_raw = WAVE159_README.read_bytes()
    witness = json.loads(witness_raw)
    catalog = json.loads(catalog_raw)
    defect_probe = json.loads(defect_probe_raw)
    entry = next(
        row for row in catalog["macro_entries"]
        if row["signature_stabilizer_canonical"]
        and int(row["source_row_index"]) == 724
        and int(row["Q"]) == 2
    )
    assert tuple(witness["macro_key"]) == (724, 1, 0)
    probe_row = next(row for row in defect_probe["rows"]
                     if tuple(row["key"]) == (724, 1, 0))
    probe_counters = probe_row["full_rank_three_degree_CSP_census"]["counters"]
    assert probe_counters["overlap_products"] == 1024
    assert probe_counters["feasible"] == 128
    exceptional = {tuple(item["support"])
                   for item in entry["exceptional_supports"]}
    labels = tuple(vertex_label(vertex) for vertex in range(84))
    adjacency = [0] * 84
    for left, right in witness["edge_list_zero_based"]:
        adjacency[left] |= 1 << right
        adjacency[right] |= 1 << left
    assert [mask.bit_count() for mask in adjacency] == [12] * 84
    fixed_adjacency = [0] * 84
    for left, right in witness["edge_list_zero_based"]:
        if fibre_relation(left, right) == "disjoint":
            continue
        fixed_adjacency[left] |= 1 << right
        fixed_adjacency[right] |= 1 << left
    fixed_local_residual_histogram = Counter()
    for left, right in itertools.combinations(range(84), 2):
        adjacent = (fixed_adjacency[left] >> right) & 1
        root_overlap = len(set(labels[left]) & set(labels[right]))
        residual = adjacent + (fixed_adjacency[left] & fixed_adjacency[right]).bit_count() \
            - (2 - root_overlap)
        fixed_local_residual_histogram[residual] += 1
    assert not sum(count for residual, count in fixed_local_residual_histogram.items()
                   if residual > 0)

    block_degrees = []
    for vertex in range(84):
        block_degrees.append(tuple(
            (adjacency[vertex] & sum(1 << other
                                     for other in range(4 * target, 4 * target + 4))).bit_count()
            for target in range(21)
        ))

    def vertex_kind(vertex):
        return "E" if SUPPORTS[vertex // 4] in exceptional else "O"

    def port_type(vertex):
        source = vertex // 4
        support = SUPPORTS[source]
        rows = block_degrees[vertex]
        port_by_group = []
        for group in support:
            port_by_group.append(sum(
                rows[target]
                for target, target_support in enumerate(SUPPORTS)
                if target != source and group in target_support
            ))
        disjoint_exceptional = sum(
            rows[target] for target, target_support in enumerate(SUPPORTS)
            if not (set(support) & set(target_support))
            and target_support in exceptional
        )
        disjoint_ordinary = sum(
            rows[target] for target, target_support in enumerate(SUPPORTS)
            if not (set(support) & set(target_support))
            and target_support not in exceptional
        )
        return (
            f"{vertex_kind(vertex)}:a={rows[source]}:"
            f"p={','.join(map(str, sorted(port_by_group)))}:"
            f"dE={disjoint_exceptional}:dO={disjoint_ordinary}"
        )

    coarse_histogram = Counter()
    endpoint_kind_relation_histogram = Counter()
    local_pair_type_histogram = Counter()
    port_pair_histogram = Counter()
    minimum_order_histogram = Counter()
    certificate_type_histogram = Counter()
    proof_free_histogram = Counter()
    induced_free_histogram = Counter()
    common_witness_type_histogram = Counter()
    common_fibre_pattern_histogram = Counter()
    collision_above_row_lower_bound_histogram = Counter()
    adjacency_histogram = Counter()
    root_overlap_histogram = Counter()
    minimum_witness_count_histogram = Counter()
    records = []
    all_pair_residual = Counter()
    degree_row_forced = []
    positive_pairs = []

    for left, right in itertools.combinations(range(84), 2):
        adjacent = (adjacency[left] >> right) & 1
        common_mask = adjacency[left] & adjacency[right]
        common_outer = common_mask.bit_count()
        root_overlap = len(set(labels[left]) & set(labels[right]))
        residual = adjacent + common_outer - (2 - root_overlap)
        all_pair_residual[residual] += 1

        relation = fibre_relation(left, right)
        # Exact conservative lower bound on common outer neighbours obtained
        # solely from the two fixed fibre-degree rows.  For a disjoint block,
        # adjacency is still a free binary decision and is therefore minimised
        # to zero.  Same/overlap adjacency is already locally fixed.
        fixed_adjacent = adjacent if relation != "disjoint" else 0
        row_lower_bound = 0
        per_fibre_lower_bound = []
        for target in range(21):
            left_size = block_degrees[left][target]
            right_size = block_degrees[right][target]
            if right // 4 == target:
                left_size -= fixed_adjacent
            if left // 4 == target:
                right_size -= fixed_adjacent
            universe = 4 - int(left // 4 == target) - int(right // 4 == target)
            target_lower_bound = max(0, left_size + right_size - universe)
            per_fibre_lower_bound.append(target_lower_bound)
            row_lower_bound += target_lower_bound
        forced_excess = fixed_adjacent + root_overlap + row_lower_bound - 2
        if forced_excess > 0:
            degree_row_forced.append((left, right, forced_excess))

        if residual <= 0:
            continue
        positive_pairs.append((left, right))
        endpoint_kinds = "".join(sorted((vertex_kind(left), vertex_kind(right))))
        local_relation = relation
        if relation == "same":
            first_local, second_local = left % 4, right % 4
            distance = ((first_local // 2) != (second_local // 2)) + (
                (first_local % 2) != (second_local % 2)
            )
            local_relation += ":side" if distance == 1 else ":diagonal"
        elif relation == "overlap":
            local_relation += ":same-root-label" if root_overlap else ":cross-root-label"
        else:
            local_relation += ":edge" if adjacent else ":nonedge"

        minimum_witnesses = 3 - adjacent - root_overlap
        common_vertices = tuple(vertex for vertex in range(84)
                                if (common_mask >> vertex) & 1)
        assert 1 <= minimum_witnesses <= 3
        assert len(common_vertices) >= minimum_witnesses
        best = None
        for selected in itertools.combinations(common_vertices, minimum_witnesses):
            certificate = rooted_certificate(
                left, right, selected, tuple(adjacency), labels
            )
            key = (
                certificate["order"],
                int(certificate["canonical_layer_marked_mask_hex"], 16),
                tuple(selected),
            )
            if best is None or key < best[0]:
                best = key, certificate
        assert best is not None
        certificate = best[1]

        witness_types = Counter()
        for common in common_vertices:
            witness_types[
                f"{vertex_kind(common)}:"
                f"{fibre_relation(left, common)}/"
                f"{fibre_relation(right, common)}"
            ] += 1
        witness_type_key = ",".join(
            f"{kind}x{count}" for kind, count in sorted(witness_types.items())
        )
        common_by_fibre = []
        abstract_common_fibre_pattern = []
        for target, target_support in enumerate(SUPPORTS):
            target_mask = sum(1 << vertex
                              for vertex in range(4 * target, 4 * target + 4))
            count = (common_mask & target_mask).bit_count()
            if not count:
                continue
            target_kind = "E" if target_support in exceptional else "O"
            endpoint_relations = sorted((
                f"{vertex_kind(left)}:{fibre_relation(left, 4 * target)}",
                f"{vertex_kind(right)}:{fibre_relation(right, 4 * target)}",
            ))
            common_by_fibre.append({
                "target_support": list(target_support),
                "target_kind": target_kind,
                "common_neighbours": count,
                "degree_row_lower_bound": per_fibre_lower_bound[target],
                "endpoint_relations": endpoint_relations,
            })
            abstract_common_fibre_pattern.append(
                f"{target_kind}({'+'.join(endpoint_relations)}):"
                f"{count}/{per_fibre_lower_bound[target]}"
            )
        abstract_common_fibre_pattern.sort()
        common_fibre_pattern_key = ",".join(abstract_common_fibre_pattern)
        coarse_key = (
            f"{endpoint_kinds}|{relation}|adj={adjacent}|"
            f"root={root_overlap}|common={common_outer}|excess={residual}"
        )
        port_key = " || ".join(sorted((port_type(left), port_type(right))))
        certificate_key = (
            f"n={certificate['order']}|N={certificate['root_neighbour_vertices']}|"
            f"m={minimum_witnesses}|mask={certificate['canonical_layer_marked_mask_hex']}"
        )
        coarse_histogram[coarse_key] += 1
        endpoint_kind_relation_histogram[f"{endpoint_kinds}|{relation}"] += 1
        local_pair_type_histogram[local_relation] += 1
        port_pair_histogram[port_key] += 1
        minimum_order_histogram[certificate["order"]] += 1
        certificate_type_histogram[certificate_key] += 1
        proof_free_histogram[certificate["proof_edges_from_free_disjoint_blocks"]] += 1
        induced_free_histogram[certificate["induced_edges_from_free_disjoint_blocks"]] += 1
        common_witness_type_histogram[witness_type_key] += 1
        common_fibre_pattern_histogram[common_fibre_pattern_key] += 1
        collision_above_row_lower_bound_histogram[
            common_outer - row_lower_bound
        ] += 1
        adjacency_histogram[adjacent] += 1
        root_overlap_histogram[root_overlap] += 1
        minimum_witness_count_histogram[minimum_witnesses] += 1
        records.append({
            "pair": [left, right],
            "supports": [list(SUPPORTS[left // 4]), list(SUPPORTS[right // 4])],
            "root_neighbour_labels": [list(labels[left]), list(labels[right])],
            "endpoint_kinds": endpoint_kinds,
            "fibre_relation": relation,
            "local_pair_type": local_relation,
            "adjacent": adjacent,
            "root_overlap": root_overlap,
            "common_outer": common_outer,
            "excess": residual,
            "minimum_outer_witnesses": minimum_witnesses,
            "endpoint_port_types": [port_type(left), port_type(right)],
            "common_witness_type_multiset": dict(sorted(witness_types.items())),
            "common_neighbours_by_fibre": common_by_fibre,
            "fibre_degree_row_common_neighbour_lower_bound": row_lower_bound,
            "common_neighbours_above_fibre_degree_row_lower_bound": (
                common_outer - row_lower_bound
            ),
            "fibre_degree_row_forced_excess": forced_excess,
            "minimum_rooted_certificate": certificate,
        })

    assert len(records) == witness["positive_pair_upper_violations"] == 1025
    assert not degree_row_forced
    assert sum(minimum_order_histogram.values()) == 1025
    assert sum(coarse_histogram.values()) == 1025
    assert all(record["minimum_rooted_certificate"][
        "proof_edges_from_free_disjoint_blocks"] >= 1 for record in records)

    def sorted_histogram(counter):
        return {str(key): value for key, value in sorted(
            counter.items(), key=lambda item: (-item[1], str(item[0]))
        )}

    result = {
        "status": "SOURCE724_SINGLE_WITNESS_PAIR_VIOLATION_CLASSIFICATION_COMPLETE",
        "scope_boundary": (
            "This classifies one deterministic binary completion of one of the "
            "128 feasible rank-three degree CSP branches.  It is not a proof "
            "that the source724 macro is impossible."
        ),
        "inputs": {
            str(WITNESS): hashlib.sha256(witness_raw).hexdigest().upper(),
            str(CATALOG): hashlib.sha256(catalog_raw).hexdigest().upper(),
            str(DEFECT_PROBE): hashlib.sha256(defect_probe_raw).hexdigest().upper(),
            str(ORDER8_BOUNDARY): hashlib.sha256(boundary_raw).hexdigest().upper(),
            str(YYT_SHADOW): hashlib.sha256(shadow_raw).hexdigest().upper(),
            str(FOUR_ROOT_DERIVATION): hashlib.sha256(four_root_raw).hexdigest().upper(),
            str(WAVE159_README): hashlib.sha256(wave159_raw).hexdigest().upper(),
        },
        "macro_key": list(witness["macro_key"]),
        "macro_coverage": int(witness["coverage_of_macro"]),
        "selected_group_choice_indices": witness["selected_group_choice_indices"],
        "whole_macro_rank_three_boundary": {
            "overlap_products": probe_counters["overlap_products"],
            "empty_fibre_configuration_domain": probe_counters[
                "empty_fibre_configuration_domain"
            ],
            "global_gram_or_graphical_unsat": probe_counters[
                "global_gram_or_graphical_unsat"
            ],
            "feasible_overlap_products": probe_counters["feasible"],
            "distinct_fixed_overlap_degree_signatures": probe_row[
                "full_rank_three_degree_CSP_census"
            ]["distinct_fixed_overlap_degree_signatures"],
            "Z_rank": probe_row["Z_rank"],
            "K4_rank": probe_row["K4_rank"],
            "novel_exceptional_kernel_dimension": probe_row[
                "novel_exceptional_kernel_dimension"
            ],
            "scope": (
                "The classified graph is the first stored feasible branch and "
                "one deterministic disjoint-block completion; the other feasible "
                "overlap products and degree configurations were not enumerated."
            ),
            "universal_single_pair_cut_found": False,
            "macro_coverage_excluded_by_this_discovery": 0,
        },
        "outer_graph": {"vertices": 84, "edges": 504, "degree": 12},
        "exceptional_supports": [list(support) for support in sorted(exceptional)],
        "positive_pair_upper_violations": len(records),
        "all_pair_residual_histogram": sorted_histogram(all_pair_residual),
        "classification_histograms": {
            "endpoint_and_fibre_type": sorted_histogram(coarse_histogram),
            "endpoint_kind_and_fibre_relation": sorted_histogram(
                endpoint_kind_relation_histogram
            ),
            "local_pair_type": sorted_histogram(local_pair_type_histogram),
            "endpoint_port_type_pair": sorted_histogram(port_pair_histogram),
            "common_witness_type_multiset": sorted_histogram(
                common_witness_type_histogram
            ),
            "common_fibre_collision_pattern_count_over_lower_bound": sorted_histogram(
                common_fibre_pattern_histogram
            ),
            "common_neighbours_above_degree_row_lower_bound": sorted_histogram(
                collision_above_row_lower_bound_histogram
            ),
            "adjacency": sorted_histogram(adjacency_histogram),
            "root_neighbour_overlap": sorted_histogram(root_overlap_histogram),
            "minimum_outer_witness_count": sorted_histogram(
                minimum_witness_count_histogram
            ),
            "minimum_rooted_certificate_order": sorted_histogram(
                minimum_order_histogram
            ),
            "minimum_rooted_certificate_type": sorted_histogram(
                certificate_type_histogram
            ),
            "proof_edges_from_free_disjoint_blocks": sorted_histogram(
                proof_free_histogram
            ),
            "induced_edges_from_free_disjoint_blocks": sorted_histogram(
                induced_free_histogram
            ),
        },
        "fixed_fibre_degree_row_pair_test": {
            "pairs_tested": 84 * 83 // 2,
            "forced_positive_pair_upper_violations": len(degree_row_forced),
            "formula": (
                "LB(x,y)=sum_H max(0,d'_x(H)+d'_y(H)-|H\\{x,y}|); "
                "fixed_adj+root_overlap+LB>2 would be a universal one-pair cut"
            ),
            "result": (
                "No pair is excluded by the fixed fibre-degree rows alone, "
                "even after removing endpoints from each candidate fibre."
            ),
        },
        "fixed_local_vs_free_completion": {
            "input_exceptional_local_pair_upper_passed": bool(
                witness["materialized_exceptional_local_pair_upper_verified"]
            ),
            "all_84_vertex_fixed_internal_and_overlap_residual_histogram": (
                sorted_histogram(fixed_local_residual_histogram)
            ),
            "all_84_vertex_fixed_internal_and_overlap_positive_violations": 0,
            "violations_with_no_free_disjoint_proof_edge": sum(
                record["minimum_rooted_certificate"]
                ["proof_edges_from_free_disjoint_blocks"] == 0
                for record in records
            ),
            "interpretation": (
                "Every minimum certificate uses at least one edge chosen in a "
                "free disjoint-support block.  The failures are completion-"
                "dependent, not already present in the fixed local port graph."
            ),
        },
        "order8_boundary": {
            "minimum_certificate_order": min(minimum_order_histogram),
            "certificates_of_order_at_most_8": sum(
                count for order, count in minimum_order_histogram.items()
                if order <= 8
            ),
            "mask_convention": (
                "Exact canonical adjacency mask preserving four roles: root, "
                "root-neighbour layer, marked endpoint pair, common witnesses."
            ),
            "conclusion": (
                "No failure of this witness is exposed by an induced rooted "
                "certificate on at most eight vertices.  Thus it cannot be "
                "identified directly with a single order-8 marked-pair class."
            ),
        },
        "four_root_mask_3_12_comparison": {
            "endpoint_root_label_incidence_shapes": {
                "one_shared_root_neighbour_label_P3_analogue": (
                    root_overlap_histogram[1]
                ),
                "zero_shared_root_neighbour_labels_2K2_analogue": (
                    root_overlap_histogram[0]
                ),
            },
            "Wave152_mask_3": "four fixed roots with edges (0,1),(0,2)",
            "Wave152_mask_12": "four fixed roots with edges (0,3),(1,2)",
            "exact_boundary": (
                "The P3/2K2 language above describes intersections of the two "
                "endpoint incidence-label pairs.  Wave152 masks 3 and 12 encode "
                "actual induced adjacencies among four fixed graph vertices.  "
                "There is no canonical fourth root or adjacency-preserving lift "
                "from a source724 endpoint pair, so this is only a shape analogy, "
                "not an equality of covariance coordinates or cuts."
            ),
            "known_order8_masks_are_a_different_space": (
                "The E0 adjacent-side pair uses degree-cell mask 127242964 "
                "(global mask 14333541); neither is four-root mask 3 or 12."
            ),
        },
        "records": records,
        "conclusion": (
            "The 1,025 violations are real and have explicit small certificates, "
            "but all depend on freely chosen disjoint-block edges and none is "
            "forced by the source724 degree rows through one pair pigeonhole "
            "condition.  This witness is a boundary counterexample to the defect-"
            "rank/port conditions, not a solver-free exclusion of the full macro."
        ),
    }
    atomic_json(OUTPUT, result)
    print(json.dumps({
        "path": str(OUTPUT),
        "status": result["status"],
        "violations": len(records),
        "minimum_order_histogram": result["classification_histograms"]
        ["minimum_rooted_certificate_order"],
        "certificate_types": len(certificate_type_histogram),
        "max_canonical_search_nodes": max(
            record["minimum_rooted_certificate"]["canonical_search_nodes"]
            for record in records
        ),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
