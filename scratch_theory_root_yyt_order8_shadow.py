"""Bind the YY^T off-diagonal shadow to the frozen order-eight layer.

For an off-diagonal YY^T term, omit the unmatched vertex of the common
target triangle.  The remaining target edge, the two disjoint source
triangles, and the two roots use eight vertices.  This file computes the
coefficient of that *shadow* on every one of the 916 Wave147 order-eight
classes.  The true term is the subfamily for which the unique triangle mate
of the target edge is nonadjacent to both roots.

The script also audits the frozen Wave147 coefficient matrices and tests
their entry-vector rank modulo an exact prime.  Full modular row rank is a
rigorous certificate of full rational span (a nonzero minor modulo p is a
nonzero integer minor).  This span statement concerns arbitrary linear
functionals of the moment entries; it does not say that a representing
matrix is PSD, nor does it turn the shadow into the true YY^T entry.
"""

from __future__ import annotations

import gzip
import hashlib
import itertools
import json
from collections import defaultdict
from pathlib import Path


COEFFICIENTS = Path(
    "external_conway99_research/attempts/wave147-alternative-lane/coefficients.json.gz"
)
MARKED_ROWS = Path(
    "external_conway99_research/attempts/wave148-marked-order8/marked-rows.json.gz"
)
FOUR_ROOT_CUT = Path(
    "external_conway99_research/attempts/wave152-four-root-order8/"
    "simplified-mask12-cut.json"
)
OUTPUT = Path("scratch_theory_root_yyt_order8_shadow.json")
PRIME = 1_000_003


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def edge_positions(order: int):
    return {edge: position for position, edge in enumerate(
        itertools.combinations(range(order), 2)
    )}


def adjacency_rows(mask: int, order: int):
    rows = [0] * order
    for (left, right), position in edge_positions(order).items():
        if mask >> position & 1:
            rows[left] |= 1 << right
            rows[right] |= 1 << left
    return tuple(rows)


def locally_pair_upper(mask: int, order: int):
    graph = adjacency_rows(mask, order)
    for left, right in itertools.combinations(range(order), 2):
        common = (graph[left] & graph[right]).bit_count()
        if common > (1 if graph[left] >> right & 1 else 2):
            return False
    return True


def triangles(rows):
    order = len(rows)
    return tuple(
        triple for triple in itertools.combinations(range(order), 3)
        if all(rows[left] >> right & 1
               for left, right in itertools.combinations(triple, 2))
    )


def is_perfect_two_matching(rows, source_triangle, root, target_edge):
    nonroots = tuple(vertex for vertex in source_triangle if vertex != root)
    if any(rows[root] >> target & 1 for target in target_edge):
        return False
    return (
        all(sum(rows[source] >> target & 1 for target in target_edge) == 1
            for source in nonroots)
        and all(sum(rows[source] >> target & 1 for source in nonroots) == 1
                for target in target_edge)
    )


def shadow_count(mask: int, root_edge: bool) -> int:
    """Number of ordered-root, ordered-source shadow configurations."""

    order = 8
    rows = adjacency_rows(mask, order)
    triangle_rows = triangles(rows)
    edges = tuple((left, right)
                  for left, right in itertools.combinations(range(order), 2)
                  if rows[left] >> right & 1)
    count = 0
    vertices = set(range(order))
    for root_left in range(order):
        for root_right in range(order):
            if root_left == root_right:
                continue
            if bool(rows[root_left] >> root_right & 1) != root_edge:
                continue
            for source_left in triangle_rows:
                if root_left not in source_left:
                    continue
                source_left_set = set(source_left)
                for source_right in triangle_rows:
                    if root_right not in source_right:
                        continue
                    source_right_set = set(source_right)
                    if source_left_set & source_right_set:
                        continue
                    used = source_left_set | source_right_set
                    target_vertices = vertices - used
                    if len(target_vertices) != 2:
                        continue
                    target_edge = tuple(sorted(target_vertices))
                    if target_edge not in edges:
                        continue
                    if (is_perfect_two_matching(rows, source_left, root_left,
                                                target_edge)
                            and is_perfect_two_matching(rows, source_right,
                                                        root_right,
                                                        target_edge)):
                        count += 1
    return count


def sparse_modular_basis(vectors, dimension, prime=PRIME):
    """Exact sparse row rank over F_p, with a deterministic pivot order."""

    basis = {}
    processed = 0
    for original in vectors:
        processed += 1
        vector = {index: value % prime for index, value in original.items()
                  if value % prime}
        while vector:
            pivot = min(vector)
            if pivot not in basis:
                inverse = pow(vector[pivot], prime - 2, prime)
                vector = {index: value * inverse % prime
                          for index, value in vector.items() if value % prime}
                basis[pivot] = vector
                break
            factor = vector[pivot]
            pivot_row = basis[pivot]
            for index, value in pivot_row.items():
                updated = (vector.get(index, 0) - factor * value) % prime
                if updated:
                    vector[index] = updated
                else:
                    vector.pop(index, None)
        if len(basis) == dimension:
            break
    return basis, processed


def reduce_modular(vector, basis, prime=PRIME):
    vector = {index: value % prime for index, value in vector.items()
              if value % prime}
    while vector:
        pivot = min(vector)
        if pivot not in basis:
            return vector
        factor = vector[pivot]
        for index, value in basis[pivot].items():
            updated = (vector.get(index, 0) - factor * value) % prime
            if updated:
                vector[index] = updated
            else:
                vector.pop(index, None)
    return vector


def induced_mask(mask, graph_order, vertices):
    source_positions = edge_positions(graph_order)
    value = 0
    for position, (left, right) in enumerate(itertools.combinations(vertices, 2)):
        if mask >> source_positions[tuple(sorted((left, right)))] & 1:
            value |= 1 << position
    return value


def transform_mask(mask, order, permutation):
    positions = edge_positions(order)
    value = 0
    for edge, position in positions.items():
        if mask >> position & 1:
            image = tuple(sorted((permutation[edge[0]], permutation[edge[1]])))
            value |= 1 << positions[image]
    return value


def canonical_four_root_flag(mask):
    return min(mask, transform_mask(mask, 6, (0, 1, 2, 3, 5, 4)))


def selected_four_root_moment_coefficient(mask, root_mask, left_flags,
                                          right_flags):
    """Coefficient of sum_{i in L,j in R} M_tau[i,j] on one H8 class."""

    total = 0
    vertices = tuple(range(8))
    for roots in itertools.permutations(vertices, 4):
        if induced_mask(mask, 8, roots) != root_mask:
            continue
        complement = tuple(vertex for vertex in vertices if vertex not in roots)
        pairs = tuple(itertools.combinations(complement, 2))
        flag_by_pair = tuple(canonical_four_root_flag(
            induced_mask(mask, 8, roots + pair)
        ) for pair in pairs)
        for left_index, left_pair in enumerate(pairs):
            for right_index, right_pair in enumerate(pairs):
                if set(left_pair) | set(right_pair) != set(complement):
                    continue
                if (flag_by_pair[left_index] in left_flags
                        and flag_by_pair[right_index] in right_flags):
                    total += 1
    return total


def entry_vectors(records, matrix_size):
    vectors = defaultdict(dict)
    for class_index, record in enumerate(records):
        for row, column, value in record["upper_entries"]:
            vectors[(int(row), int(column))][class_index] = int(value)
    # Include zero positions only conceptually; they cannot affect rank.
    assert all(0 <= row <= column < matrix_size for row, column in vectors)
    return tuple(vectors[position] for position in sorted(vectors)), tuple(sorted(vectors))


def main():
    with gzip.open(COEFFICIENTS, "rt", encoding="utf-8") as handle:
        coefficients = json.load(handle)
    with gzip.open(MARKED_ROWS, "rt", encoding="utf-8") as handle:
        marked = json.load(handle)
    four_root_cut = json.loads(FOUR_ROOT_CUT.read_text(encoding="utf-8"))

    # One shadow base has four locally admissible completions according to
    # the two source-root adjacency bits of the target-edge triangle mate.
    strict_base_edges = {
        (0, 1), (0, 2), (1, 2), (3, 4), (3, 5), (4, 5),
        (7, 8), (1, 7), (2, 8), (4, 7), (5, 8), (6, 7), (6, 8),
    }
    positions9 = edge_positions(9)
    completion_masks = []
    for left_bit, right_bit in itertools.product((0, 1), repeat=2):
        edges = set(strict_base_edges)
        if left_bit:
            edges.add((0, 6))
        if right_bit:
            edges.add((3, 6))
        mask = sum(1 << positions9[tuple(sorted(edge))] for edge in edges)
        assert locally_pair_upper(mask, 9)
        completion_masks.append({
            "mate_to_source_root_bits": [left_bit, right_bit],
            "labelled_mask": mask,
        })

    class_rows = coefficients["families"]["ordered_edge"]["class_coefficients"]
    class_keys = tuple((int(row["order"]), int(row["canonical_mask"]))
                       for row in class_rows)
    assert len(class_keys) == 21 + 62 + 208 + 916 == 1207
    assert len(set(class_keys)) == len(class_keys)
    order8_masks = tuple(mask for order, mask in class_keys if order == 8)
    assert len(order8_masks) == 916
    assert tuple(mask for order, mask in (
        (int(row["order"]), int(row["canonical_mask"]))
        for row in coefficients["families"]["ordered_nonedge"]["class_coefficients"]
    ) if order == 8) == order8_masks
    assert marked["class_streams"]["8"]["count"] == 916

    shadows = {}
    span_rows = {}
    four_root_specification = {
        "ordered_edge": {
            "root_mask": 12,
            "root_role_edges": [[0, 3], [1, 2]],
            "source_roots": [0, 3],
            "target_edge": [1, 2],
            "left_flag_masks": [17724],
            "right_flag_masks": [29988],
        },
        "ordered_nonedge": {
            "root_mask": 1,
            "root_role_edges": [[0, 1]],
            "source_roots": [2, 3],
            "target_edge": [0, 1],
            "left_flag_masks": [19601, 23697, 23817],
            "right_flag_masks": [28817, 29841, 29961],
        },
    }
    for family, root_edge in (("ordered_edge", True),
                              ("ordered_nonedge", False)):
        family_data = coefficients["families"][family]
        records = family_data["class_coefficients"]
        assert tuple((int(row["order"]), int(row["canonical_mask"]))
                     for row in records) == class_keys
        nonzero = []
        selected_nonzero = []
        specification = four_root_specification[family]
        for mask in order8_masks:
            value = shadow_count(mask, root_edge)
            selected = selected_four_root_moment_coefficient(
                mask,
                specification["root_mask"],
                frozenset(specification["left_flag_masks"]),
                frozenset(specification["right_flag_masks"]),
            )
            assert selected == 2 * value
            if value:
                nonzero.append([mask, value])
                selected_nonzero.append([mask, selected])
        shadows[family] = {
            "nonzero_order8_coefficients": nonzero,
            "nonzero_class_count": len(nonzero),
            "coefficient_sum_over_unlabelled_classes": sum(
                value for _, value in nonzero
            ),
            "maximum_coefficient": max((value for _, value in nonzero), default=0),
            "coefficient_vector_sha256": hashlib.sha256(json.dumps(
                nonzero, separators=(",", ":")
            ).encode()).hexdigest().upper(),
            "four_root_selected_moment_coefficients": selected_nonzero,
            "four_root_identity_checked_on_all_916_classes": True,
            "identity": (
                "selected raw four-root moment entry sum = "
                "2 * ordered-root shadow B_rel"
            ),
        }
        vectors, positions = entry_vectors(records, int(family_data["matrix_size"]))
        basis, processed = sparse_modular_basis(vectors, len(records))
        rank = len(basis)
        pivots = tuple(sorted(basis))
        class_index = {key: index for index, key in enumerate(class_keys)}
        shadow_vector = {
            class_index[(8, mask)]: value for mask, value in nonzero
        }
        shadow_residual = reduce_modular(shadow_vector, basis)
        augmented_rank = rank + bool(shadow_residual)
        augmented_processed = processed + 1
        span_rows[family] = {
            "matrix_size": int(family_data["matrix_size"]),
            "nonzero_upper_entry_vectors": len(vectors),
            "modulus": PRIME,
            "rank_mod_prime": rank,
            "class_dimension": len(records),
            "vectors_processed_until_full_rank_or_exhaustion": processed,
            "full_rational_class_span_certified": rank == len(records),
            "rank_after_appending_shadow_mod_prime": augmented_rank,
            "shadow_in_modular_entry_span": augmented_rank == rank,
            "shadow_modular_residual_support": len(shadow_residual),
            "augmented_vectors_processed": augmented_processed,
            "pivot_class_indices_sha256": hashlib.sha256(json.dumps(
                pivots, separators=(",", ":")
            ).encode()).hexdigest().upper(),
            "position_order_sha256": hashlib.sha256(json.dumps(
                positions, separators=(",", ":")
            ).encode()).hexdigest().upper(),
        }

    result = {
        "status": "YYT_ORDER8_SHADOW_AND_FROZEN_SPAN_AUDIT_COMPLETE",
        "frozen_inputs": {
            "wave147_coefficients": str(COEFFICIENTS),
            "wave147_coefficients_sha256": sha256(COEFFICIENTS),
            "wave148_marked_rows": str(MARKED_ROWS),
            "wave148_marked_rows_sha256": sha256(MARKED_ROWS),
            "wave152_simplified_mask12_cut": str(FOUR_ROOT_CUT),
            "wave152_simplified_mask12_cut_sha256": sha256(FOUR_ROOT_CUT),
            "class_counts_5_6_7_8": [21, 62, 208, 916],
            "class_dimension": len(class_keys),
            "wave148_vertex_rows": len(marked["vertex_rows"]),
            "wave148_ordered_pair_rows": len(marked["ordered_pair_rows"]),
        },
        "shadow_coefficients": shadows,
        "four_root_moment_bridge": four_root_specification,
        "wave147_entry_span": span_rows,
        "exact_identity": (
            "B_rel=sum_K8 b_rel(K)x_K8 = H_rel+R_rel; H_rel is the "
            "ordered adjacent/nonadjacent off-diagonal YYT mass, and R_rel "
            "counts shadows whose unique target-edge triangle mate is "
            "adjacent to at least one root"
        ),
        "consequences": {
            "order8_upper_bound": "0 <= H_rel <= B_rel",
            "strictness_is_locally_admissible": True,
            "strictness_scope": (
                "There are lambda/mu-upper-feasible nine-vertex completions "
                "in which the target-edge mate is adjacent to a source root. "
                "This is not an assertion that such a completion extends to "
                "the target SRG."
            ),
            "locally_admissible_completion_witnesses": completion_masks,
            "why_wave147_span_is_not_closure": (
                "Entry-vector span is only a question about the order-eight "
                "shadow B_rel.  Even an exact rational representation would "
                "supply neither a PSD selector nor the order-nine correction "
                "R_rel.  A modular membership result alone is not promoted "
                "to a rational-span certificate."
            ),
            "first_missing_data": (
                "an order-eight-to-nine extension statistic recording whether "
                "the unique common neighbour completing the marked target "
                "edge is adjacent to neither, exactly one, or both roots"
            ),
            "root_arity_of_missing_statistic": 4,
            "root_description": (
                "ordered roots r,s plus the two pointwise endpoints of the "
                "target edge; the extension vertex must be adjacent to the "
                "edge endpoints and its two root-adjacency bits must be known"
            ),
            "four_root_covariance_relation": (
                "The order-eight shadow is exactly a selected raw second "
                "moment in root mask 12 (adjacent roots) or root mask 1 "
                "(nonadjacent roots).  The true YYT mass additionally "
                "multiplies each root embedding by the 0/1 indicator that "
                "the unique mate of the target edge has root-adjacency bits "
                "00; this is a mixed third moment and is absent from the "
                "four-root covariance block."
            ),
            "mask12_cut_overlap": {
                "shadow_order8_masks": [mask for mask, _ in
                                         shadows["ordered_edge"]["nonzero_order8_coefficients"]],
                "all_three_appear_in_verified_sparse_cut": all(
                    mask in {
                        int(row["canonical_mask"])
                        for row in four_root_cut["cut"]["order8_coefficients"]
                    }
                    for mask, _ in shadows["ordered_edge"]["nonzero_order8_coefficients"]
                ),
                "cut_root_mask": int(four_root_cut["cut"]["root_mask"]),
                "caveat": (
                    "The cut direction uses flags 5428 and 6324, not the "
                    "shadow flags 17724 and 29988; common class support is "
                    "structural overlap, not equality of the two functionals."
                ),
            },
        },
        "scope": (
            "This exhausts the frozen 916 order-eight classes and all 2,414 "
            "Wave147 class coefficient matrices.  Wave148's 944/4,440 rows "
            "extend order seven to eight and therefore do not contain the "
            "required order-eight-to-nine four-root extension statistic."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "edge_shadow_nonzero": shadows["ordered_edge"]["nonzero_class_count"],
        "nonedge_shadow_nonzero": shadows["ordered_nonedge"]["nonzero_class_count"],
        "edge_span_rank": span_rows["ordered_edge"]["rank_mod_prime"],
        "nonedge_span_rank": span_rows["ordered_nonedge"]["rank_mod_prime"],
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
