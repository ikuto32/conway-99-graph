"""Targeted 35-column closure after adjoining the seven R0 masks.

The order-nine universe is fixed to the preceding 19+9 columns and exactly
the seven masks required by the R0 products.  No ambient H9 census is made;
the frozen order-eight catalogue is read but never regenerated.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import os
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

import scratch_theory_order9_cross_x_closure as base
from scratch_theory_order9_rooted_flag_gram import moment_coeff_triangle


OUTPUT = Path("scratch_theory_order9_r0_closure.json")
PRIOR = Path("scratch_theory_order9_cross_x_closure.json")
DECK = Path("scratch_theory_minimal_order9_targeted_deck.json")
OLD_GRAM = Path("scratch_theory_order9_rooted_flag_gram.json")
WAVE147 = Path(
    "external_conway99_research/attempts/wave147-alternative-lane/"
    "exact-results.json"
)
WAVE163 = Path("scratch_theory_wave163_integral_order8_boundary.json")

NEW_MASKS = (
    1292419201,
    3668590721,
    13610256401,
    14889779459,
    24436319376,
    32214460576,
    35652157569,
)
SELECTED_FULL_INDICES = (0, 4, 5, 6, 7)
FLAG_NAMES = ("R0", "X_0", "X_1", "X_2", "P")


def hash_file(path: Path) -> str:
    state = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            state.update(block)
    return state.hexdigest()


def write_json(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def sparse(vector: list[int]) -> list[list[int]]:
    return [[index, value] for index, value in enumerate(vector) if value]


def rank(matrix: list[list[int]]) -> int:
    if not matrix:
        return 0
    work = [[Fraction(value) for value in row] for row in matrix]
    pivot_row = 0
    for column in range(len(work[0])):
        pivot = next((row for row in range(pivot_row, len(work))
                      if work[row][column]), None)
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        scale = work[pivot_row][column]
        work[pivot_row] = [value / scale for value in work[pivot_row]]
        for row in range(len(work)):
            if row == pivot_row or not work[row][column]:
                continue
            scale = work[row][column]
            work[row] = [value - scale * other for value, other in
                         zip(work[row], work[pivot_row])]
        pivot_row += 1
    return pivot_row


def selected_matrix(mask: int) -> list[list[int]]:
    full = moment_coeff_triangle(mask, 9)
    return [[full[i][j] for j in SELECTED_FULL_INDICES]
            for i in SELECTED_FULL_INDICES]


def upper_entries(matrix: list[list[int]]) -> list[list[int]]:
    return [[i, j, matrix[i][j]]
            for i in range(len(matrix))
            for j in range(i, len(matrix)) if matrix[i][j]]


def main() -> None:
    prior = json.loads(PRIOR.read_text(encoding="utf-8"))
    deck = json.loads(DECK.read_text(encoding="utf-8"))
    old_gram = json.loads(OLD_GRAM.read_text(encoding="utf-8"))
    frozen = json.loads(WAVE147.read_text(encoding="utf-8"))
    wave163 = json.loads(WAVE163.read_text(encoding="utf-8"))

    projection = deck["T0_all_G_targeted_order9_projection"]
    visible19 = tuple(map(int, projection["visible_19_H9_masks"]))
    fixed19 = tuple(map(int, projection["wave163_visible_19_candidate_counts"]))
    old9 = tuple(map(int, prior["added_nine_masks"]))
    masks28 = visible19 + old9
    masks35 = masks28 + NEW_MASKS
    variable_masks = old9 + NEW_MASKS
    assert len(set(masks35)) == 35 and len(variable_masks) == 16

    frozen8 = tuple(map(int, frozen["class_streams"]["8"]["canonical_masks"]))
    frozen8_set = set(frozen8)
    x8 = {int(mask): int(value) for mask, value in
          wave163["integral_pseudocount"]["order8_mask_count_pairs"]}
    assert len(frozen8_set) == len(x8) == 916 and set(x8) == frozen8_set

    # The seven supplied masks are exactly the union of missing R0 products.
    natural = base.natural_flag_masks()
    product_rows = []
    missing_union = set()
    for partner in (0, 4, 5, 6, 7):
        support = base.completion_support(natural[0], natural[partner])
        outside = sorted(support - set(masks28))
        missing_union.update(outside)
        product_rows.append({
            "left_flag": "R0",
            "right_flag": ("R0", "X_0", "X_1", "X_2", "P")[
                (0, 4, 5, 6, 7).index(partner)
            ],
            "outside_28_masks": outside,
            "closed_on_35": support <= set(masks35),
        })
    assert missing_union == set(NEW_MASKS)
    assert all(row["closed_on_35"] for row in product_rows)

    # Complete deletion deck of the new seven into the frozen H8 list.
    new_decks = []
    all_new_shadows = set()
    for index, mask in enumerate(NEW_MASKS):
        assert base.canonical(mask, 9) == mask
        assert base.pair_upper(mask, 9)
        histogram = Counter()
        deletions = []
        for removed in range(9):
            raw8, _ = base.delete(mask, 9, removed)
            shadow = base.canonical(raw8, 8)
            assert shadow in frozen8_set
            histogram[shadow] += 1
            all_new_shadows.add(shadow)
            deletions.append({
                "deleted_vertex": removed,
                "canonical_order8_mask": shadow,
                "frozen_order8_index_0_based": frozen8.index(shadow),
                "wave163_order8_count": x8[shadow],
            })
        new_decks.append({
            "new7_index": index,
            "canonical_order9_mask": mask,
            "edge_count": mask.bit_count(),
            "degree_sequence": sorted(row.bit_count()
                                      for row in base.adjacency(mask, 9)),
            "deletion_histogram": [[key, value]
                                   for key, value in sorted(histogram.items())],
            "vertex_deletions": deletions,
        })

    # Five-flag coefficient matrices on every one of the 35 columns.
    matrices35 = [selected_matrix(mask) for mask in masks35]
    coefficient_records = [{
        "column_index": index,
        "kind": "fixed19" if index < 19 else (
            "old_extra9" if index < 28 else "new_R0_7"
        ),
        "canonical_order9_mask": mask,
        "upper_entries": upper_entries(matrix),
    } for index, (mask, matrix) in enumerate(zip(masks35, matrices35))]

    old_total8 = old_gram["hostile_full_eight_type_zero_fill_control"][
        "matrix"
    ]
    fixed_base = [[int(old_total8[i][j]) for j in SELECTED_FULL_INDICES]
                  for i in SELECTED_FULL_INDICES]
    endpoint_vector = (32, 12, 12, 12, 0)
    ordered_roots = 231 * 6
    endpoint_matrix = [[ordered_roots * endpoint_vector[i] * endpoint_vector[j]
                        for j in range(5)] for i in range(5)]
    gram_equations = []
    for left in range(5):
        for right in range(left, 5):
            coefficients = [matrices35[19 + index][left][right]
                            for index in range(16)]
            rhs = endpoint_matrix[left][right] - fixed_base[left][right]
            if any(coefficients) or rhs:
                gram_equations.append({
                    "entry": [FLAG_NAMES[left], FLAG_NAMES[right]],
                    "coefficients_on_old9_new7": coefficients,
                    "rhs": rhs,
                })

    # All H8->H9 local extension rows on exactly these 35 columns.
    unmarked: dict[int, list[int]] = defaultdict(lambda: [0] * 35)
    vertex: dict[tuple[int, int], list[int]] = defaultdict(lambda: [0] * 35)
    pair: dict[tuple[int, int], list[int]] = defaultdict(lambda: [0] * 35)
    for column, mask9 in enumerate(masks35):
        graph9 = base.adjacency(mask9, 9)
        for removed in range(9):
            raw8, relabel = base.delete(mask9, 9, removed)
            shadow = base.canonical(raw8, 8)
            unmarked[shadow][column] += 1
            incident = tuple(v for v in range(9) if v != removed
                             and graph9[removed] & (1 << v))
            for root in incident:
                key = base.canonical(raw8, 8, (relabel[root],))
                vertex[(shadow, key)][column] += 1
            for left in incident:
                for right in incident:
                    if left != right:
                        key = base.canonical(raw8, 8,
                                             (relabel[left], relabel[right]))
                        pair[(shadow, key)][column] += 1

    universe19, universe28, universe35 = (set(visible19), set(masks28),
                                          set(masks35))
    support_cache = {}

    def local_support(shadow: int, required: tuple[int, ...]):
        cache_key = (shadow, tuple(sorted(required)))
        if cache_key in support_cache:
            return support_cache[cache_key]
        remaining = tuple(v for v in range(8) if v not in required)
        support = set()
        first_outside = None
        for size in range(len(remaining) + 1):
            for extra in itertools.combinations(remaining, size):
                neighborhood = tuple(sorted(required + extra))
                candidate = base.extend(shadow, neighborhood)
                if not base.pair_upper(candidate, 9):
                    continue
                image = base.canonical(candidate, 9)
                support.add(image)
                if image not in universe35 and first_outside is None:
                    first_outside = image
        assert support
        support_cache[cache_key] = support, first_outside
        return support, first_outside

    fixed35 = list(fixed19) + [0] * 16
    row_families = {"unmarked": [], "vertex": [], "ordered_pair": []}

    def row_common(vector, shadow, required, lhs):
        support, outside = local_support(shadow, required)
        fixed_rhs = sum(value * count for value, count in zip(vector, fixed35))
        return {
            "canonical_order8_mask": shadow,
            "wave163_lhs": lhs,
            "fixed19_rhs": fixed_rhs,
            "residual_capacity": lhs - fixed_rhs,
            "variable16_coefficients": sparse(vector[19:]),
            "closed_on_19": support <= universe19,
            "closed_on_28": support <= universe28,
            "closed_on_35": outside is None,
            "support_size": len(support),
            "first_outside_35_mask": outside,
        }

    for shadow, vector in sorted(unmarked.items()):
        row_families["unmarked"].append(row_common(
            vector, shadow, (), 91 * x8[shadow]
        ))
    for (shadow, key), vector in sorted(vertex.items()):
        graph8 = base.adjacency(shadow, 8)
        orbit = tuple(root for root in range(8)
                      if base.canonical(shadow, 8, (root,)) == key)
        degree = graph8[orbit[0]].bit_count()
        row = row_common(vector, shadow, (orbit[0],),
                         len(orbit) * (14 - degree) * x8[shadow])
        row.update({"rooted_key": key, "root_orbit_size": len(orbit),
                    "outside_neighbor_capacity": 14 - degree})
        row_families["vertex"].append(row)
    for (shadow, key), vector in sorted(pair.items()):
        graph8 = base.adjacency(shadow, 8)
        orbit = tuple((left, right)
                      for left in range(8) for right in range(8)
                      if left != right
                      and base.canonical(shadow, 8, (left, right)) == key)
        left, right = orbit[0]
        adjacent = bool(graph8[left] & (1 << right))
        current = (graph8[left] & graph8[right]).bit_count()
        capacity = (1 if adjacent else 2) - current
        assert capacity > 0
        row = row_common(vector, shadow, tuple(sorted((left, right))),
                         len(orbit) * capacity * x8[shadow])
        row.update({
            "ordered_pair_rooted_key": key,
            "ordered_pair_orbit_size": len(orbit),
            "root_relation": "edge" if adjacent else "nonedge",
            "outside_common_neighbor_capacity": capacity,
        })
        row_families["ordered_pair"].append(row)

    closed_rows = [(family, index, row)
                   for family, rows in row_families.items()
                   for index, row in enumerate(rows) if row["closed_on_35"]]
    closed_equations = []
    for family, index, row in closed_rows:
        vector = [0] * 16
        for coordinate, value in row["variable16_coefficients"]:
            vector[int(coordinate)] = int(value)
        closed_equations.append((vector, int(row["residual_capacity"]),
                                 family, index))
    unique_closed = sorted({(tuple(vector), rhs)
                            for vector, rhs, _, _ in closed_equations})

    candidate = [
        0, 0, 25986, 36192, 0, 6792, 10224, 0, 5922,
        0, 26186, 0, 0, 141356, 0, 103818,
    ]
    assert all(value >= 0 and isinstance(value, int) for value in candidate)
    for equation in gram_equations:
        assert sum(value * count for value, count in zip(
            equation["coefficients_on_old9_new7"], candidate
        )) == int(equation["rhs"])

    minimum_open_slack = None
    for family, rows in row_families.items():
        for row in rows:
            vector = [0] * 16
            for coordinate, value in row["variable16_coefficients"]:
                vector[int(coordinate)] = int(value)
            value = sum(a * b for a, b in zip(vector, candidate))
            residual = int(row["residual_capacity"])
            if row["closed_on_35"]:
                assert value == residual
            else:
                assert value <= residual
                slack = residual - value
                minimum_open_slack = slack if minimum_open_slack is None else min(
                    minimum_open_slack, slack
                )

    evaluated_matrix = [[fixed_base[i][j] for j in range(5)]
                        for i in range(5)]
    for count, matrix in zip(candidate, matrices35[19:]):
        for i in range(5):
            for j in range(5):
                evaluated_matrix[i][j] += count * matrix[i][j]
    assert evaluated_matrix == endpoint_matrix
    nonzero_eigenvalue = ordered_roots * sum(value * value
                                              for value in endpoint_vector)
    assert nonzero_eigenvalue == 2018016
    kernel_basis = [
        [3, -8, 0, 0, 0],
        [0, 1, -1, 0, 0],
        [0, 1, 0, -1, 0],
        [0, 0, 0, 0, 1],
    ]
    for vector in kernel_basis:
        assert all(sum(endpoint_matrix[i][j] * vector[j] for j in range(5)) == 0
                   for i in range(5))

    closed_rank = rank([list(vector) for vector, _ in unique_closed])
    unique_gram = sorted({
        (tuple(row["coefficients_on_old9_new7"]), int(row["rhs"]))
        for row in gram_equations
    })
    gram_rank = rank([list(vector) for vector, _ in unique_gram])
    combined_rank = rank(
        [list(vector) for vector, _ in unique_closed]
        + [list(vector) for vector, _ in unique_gram]
    )
    assert (closed_rank, gram_rank, combined_rank) == (7, 4, 9)

    new_closed_equations = sorted({
        (tuple(vector), rhs)
        for vector, rhs, family, index in closed_equations
        if not row_families[family][index]["closed_on_28"] and any(vector)
    })
    assert len(new_closed_equations) == 2

    # C6+2*C7 = (R0-X)+(R0-P), so the R0-X Gram equation is
    # redundant after the new deletion rows and the zero R0-P entry.
    gram_by_entry = {tuple(row["entry"]): row for row in gram_equations}
    r0p = gram_by_entry[("R0", "P")]
    r0x = gram_by_entry[("R0", "X_0")]
    new_vectors = [list(vector) for vector, _ in new_closed_equations]
    new_rhs = [rhs for _, rhs in new_closed_equations]
    c6_index = next(i for i, vector in enumerate(new_vectors) if vector[10])
    c7_index = next(i for i, vector in enumerate(new_vectors) if vector[3])
    dependency_vector = [new_vectors[c6_index][i]
                         + 2 * new_vectors[c7_index][i]
                         - r0p["coefficients_on_old9_new7"][i]
                         for i in range(16)]
    assert dependency_vector == r0x["coefficients_on_old9_new7"]
    assert new_rhs[c6_index] + 2 * new_rhs[c7_index] == (
        int(r0x["rhs"]) + int(r0p["rhs"])
    )

    # Exact next boundary from the complete 74 diagonal support records in
    # the preceding certificate; only set subtraction by the seven new masks
    # is performed here.
    diagonal28 = prior["minimal_next_missing_columns"][
        "all_74_visible_derived_diagonal_scan"
    ]["rows"]
    diagonal35 = []
    for row in diagonal28:
        outside = sorted(set(map(int, row["outside_28_masks"]))
                         - set(NEW_MASKS))
        diagonal35.append({
            "triangle_rooted_flag_mask": int(row["triangle_rooted_flag_mask"]),
            "closed_on_35": not outside,
            "outside_35_count": len(outside),
            "outside_35_masks": outside,
        })
    closed_diagonal = sorted(row["triangle_rooted_flag_mask"]
                             for row in diagonal35 if row["closed_on_35"])
    assert closed_diagonal == sorted(natural[index] for index in (0, 4, 5, 6, 7))
    minimum_open = min(row["outside_35_count"] for row in diagonal35
                       if not row["closed_on_35"])
    minimizers = [row for row in diagonal35
                  if row["outside_35_count"] == minimum_open]
    assert minimum_open == 2
    assert [row["triangle_rooted_flag_mask"] for row in minimizers] == [
        24699, 24939, 25147, 25507, 27179, 27299
    ]
    assert all(row["outside_35_masks"] == [46817920192, 56196485312]
               for row in minimizers)
    natural_r1_remaining = sorted(
        set(prior["minimal_next_missing_columns"]["candidate_rows"][1]
            ["missing_mask_union"]) - set(NEW_MASKS)
    )
    assert len(natural_r1_remaining) == 14

    result = {
        "status": "exact-35-column-R0-closure-survives",
        "scope": {
            "order9_columns": 35,
            "previous_columns": 28,
            "added_R0_columns": 7,
            "ambient_order9_census_generated": False,
            "frozen_order8_classes_regenerated": False,
            "frozen_marked_assets_regenerated": False,
            "submission_txt_written": False,
        },
        "inputs": {str(path): {"sha256": hash_file(path)} for path in
                   (PRIOR, DECK, OLD_GRAM, WAVE147, WAVE163)},
        "added_seven_masks": list(NEW_MASKS),
        "direct_R0_product_closure": product_rows,
        "added_seven_deletion_decks": {
            "slots_checked": 63,
            "all_deletions_in_frozen_916": True,
            "all_shadow_Wave163_counts_positive": all(
                x8[shadow] > 0 for shadow in all_new_shadows
            ),
            "zero_Wave163_order8_shadows": sorted(
                shadow for shadow in all_new_shadows if x8[shadow] == 0
            ),
            "new7_masks_incident_with_zero_shadows": sorted(
                int(deck_row["canonical_order9_mask"])
                for deck_row in new_decks
                if any(int(row["wave163_order8_count"]) == 0
                       for row in deck_row["vertex_deletions"])
            ),
            "same_two_new7_counts_forced_zero_by_deletion": True,
            "distinct_order8_shadows": len(all_new_shadows),
            "decks": new_decks,
        },
        "closed_five_flag_Gram": {
            "flags": list(FLAG_NAMES),
            "endpoint_flag_vector_per_ordered_triangle": list(endpoint_vector),
            "ordered_triangle_roots": ordered_roots,
            "fixed19_lower_order_matrix": fixed_base,
            "coefficient_records_on_35_columns": coefficient_records,
            "equations_on_old9_new7": gram_equations,
            "unique_equation_rank": gram_rank,
            "exact_T0_matrix": endpoint_matrix,
            "direct_witness_evaluation": evaluated_matrix,
            "PSD": True,
            "rank": 1,
            "nonzero_eigenvalue": nonzero_eigenvalue,
            "kernel_basis": kernel_basis,
            "negative_direction": None,
            "forced_zero_new7_indices_by_R0_P": [2, 3],
            "forced_zero_new7_masks_by_R0_P": [NEW_MASKS[2], NEW_MASKS[3]],
        },
        "targeted_extension_rows": {
            "row_counts": {family: len(rows)
                           for family, rows in row_families.items()},
            "closed_on_35_counts": {
                family: sum(row["closed_on_35"] for row in rows)
                for family, rows in row_families.items()
            },
            "newly_closed_beyond_28_counts": {
                family: sum(row["closed_on_35"] and not row["closed_on_28"]
                            for row in rows)
                for family, rows in row_families.items()
            },
            "unique_nonzero_closed_equations": [
                {"coefficients": list(vector), "rhs": rhs}
                for vector, rhs in unique_closed if any(vector)
            ],
            "new_unique_equations_beyond_28": [
                {"coefficients": list(vector), "rhs": rhs}
                for vector, rhs in new_closed_equations
            ],
            "closed_equation_rank": closed_rank,
            "combined_closed_plus_Gram_rank": combined_rank,
            "R0_X_dependency_on_new_rows_and_R0_P": True,
            "rows": row_families,
        },
        "exact_integer_T0_projection_witness": {
            "variable_order": {
                "old_extra9_masks": list(old9),
                "new_R0_7_masks": list(NEW_MASKS),
            },
            "counts_old9_then_new7": candidate,
            "old9_counts": candidate[:9],
            "new7_counts": candidate[9:],
            "all_counts_nonnegative_integral": True,
            "all_Gram_equations_hold": True,
            "all_closed_extension_rows_hold": True,
            "all_open_extension_slacks_nonnegative": True,
            "minimum_open_extension_slack": minimum_open_slack,
            "affine_family": {
                "old_parameters": ["a=e1", "b=e4", "c=e7", "d=e0"],
                "old_coordinates": [
                    "e0=d", "e1=a", "e2=25986-6a-2b",
                    "e3=36192+3a+2b-d", "e4=b", "e5=6792-b",
                    "e6=10224-2b", "e7=c", "e8=5922-3c",
                ],
                "new_parameters": ["g=f0", "h=f5"],
                "new_coordinates_after_nonnegativity_forces_f2=f3=0": [
                    "f0=g", "f1=26186-2h", "f2=0", "f3=0",
                    "f4=141356-6a-4b+2d", "f5=h",
                    "f6=103818-3g-h",
                ],
            },
            "congruence_consequences": [
                "e2 is even", "e6 is even", "f1 is even", "f4 is even"
            ],
            "new_frozen_Wave163_congruence_obstruction": None,
        },
        "next_boundary": {
            "visible_derived_flags_checked": 74,
            "closed_diagonal_flag_masks_on_35": closed_diagonal,
            "current_five_flag_block_is_maximal_on_35_among_these_74": True,
            "minimum_missing_columns_for_any_open_diagonal": minimum_open,
            "minimizing_flag_masks": [row["triangle_rooted_flag_mask"]
                                      for row in minimizers],
            "common_two_missing_diagonal_masks": [46817920192, 56196485312],
            "remaining_masks_to_adjoin_a_natural_R1_flag": natural_r1_remaining,
            "remaining_natural_R1_mask_count": 14,
            "diagonal_rows": diagonal35,
        },
        "claim_boundary": {
            "wave163_T0_survives": True,
            "negative_direction_found": False,
            "E0_lower_bound_translation": None,
            "reason_no_translation": (
                "The exact closed Gram is rank-one PSD and an integral "
                "nonnegative 35-column projection satisfies every licensed "
                "local row."
            ),
            "qualification": (
                "Open-row slacks are checked individually; their realization "
                "by one ambient H9 distribution is not claimed."
            ),
        },
    }
    write_json(OUTPUT, result)
    print(json.dumps({
        "output": str(OUTPUT),
        "new_deletion_slots": 63,
        "new_shadows": len(all_new_shadows),
        "closed_rows": result["targeted_extension_rows"]["closed_on_35_counts"],
        "ranks": {"closed": closed_rank, "Gram": gram_rank,
                  "combined": combined_rank, "PSD": 1},
        "forced_zero_new7_indices": [2, 3],
        "witness_new7": candidate[9:],
        "negative_direction": None,
    }, indent=2))


if __name__ == "__main__":
    main()
