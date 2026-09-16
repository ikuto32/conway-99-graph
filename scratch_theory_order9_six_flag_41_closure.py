"""Targeted 41-column closure for six variable triangle-rooted flags.

Starting from the certified 35 columns, this lane adds only the two shared
diagonal masks and the four masks in the two minimum cross-deficit pairs.
It does not enumerate an ambient H9 catalogue or continue to R1.
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


OUTPUT = Path("scratch_theory_order9_six_flag_41_closure.json")
R0_CERT = Path("scratch_theory_order9_r0_closure.json")
PROBE37 = Path("scratch_theory_order9_two_mask_diagonal_clique_probe.json")
CROSS_CERT = Path("scratch_theory_order9_cross_x_closure.json")
DECK = Path("scratch_theory_minimal_order9_targeted_deck.json")
WAVE147 = Path(
    "external_conway99_research/attempts/wave147-alternative-lane/"
    "exact-results.json"
)
WAVE163 = Path("scratch_theory_wave163_integral_order8_boundary.json")

FLAGS = (24699, 24939, 25147, 25507, 27179, 27299)
DIAGONAL_MASKS = (46817920192, 56196485312)
CROSS_MASKS = (14681719440, 56449716416, 46748225728, 47606550720)


def sha(path: Path) -> str:
    state = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            state.update(chunk)
    return state.hexdigest()


def save(path: Path, value: object) -> None:
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


def flag_moment(mask: int, order: int) -> list[list[int]]:
    """Raw Gram coefficient on the six fixed rooted order-six flags."""

    graph = base.adjacency(mask, order)
    flag_index = {flag: index for index, flag in enumerate(FLAGS)}
    matrix = [[0] * 6 for _ in range(6)]
    for roots in itertools.permutations(range(order), 3):
        if not all(graph[left] & (1 << right)
                   for left, right in itertools.combinations(roots, 2)):
            continue
        available = tuple(v for v in range(order) if v not in roots)
        occurrences = []
        for free in itertools.combinations(available, 3):
            small = base.induced(mask, order, roots + free)
            key = base.canonical(small, 6, (0, 1, 2))
            if key in flag_index:
                occurrences.append((set(free), flag_index[key]))
        for left, i in occurrences:
            for right, j in occurrences:
                if len(set(roots) | left | right) == order:
                    matrix[i][j] += 1
    return matrix


def add_weighted(total, matrix, count):
    for i in range(len(total)):
        for j in range(len(total)):
            total[i][j] += count * matrix[i][j]


def main() -> None:
    r0 = json.loads(R0_CERT.read_text(encoding="utf-8"))
    probe37 = json.loads(PROBE37.read_text(encoding="utf-8"))
    cross = json.loads(CROSS_CERT.read_text(encoding="utf-8"))
    deck = json.loads(DECK.read_text(encoding="utf-8"))
    frozen = json.loads(WAVE147.read_text(encoding="utf-8"))
    wave163 = json.loads(WAVE163.read_text(encoding="utf-8"))

    projection = deck["T0_all_G_targeted_order9_projection"]
    visible19 = tuple(map(int, projection["visible_19_H9_masks"]))
    fixed19 = tuple(map(int, projection["wave163_visible_19_candidate_counts"]))
    old9 = tuple(map(int, cross["added_nine_masks"]))
    r0seven = tuple(map(int, r0["added_seven_masks"]))
    masks35 = visible19 + old9 + r0seven
    added6 = DIAGONAL_MASKS + CROSS_MASKS
    masks41 = masks35 + added6
    variable_masks = old9 + r0seven + added6
    assert len(set(masks41)) == 41 and len(variable_masks) == 22

    frozen8 = tuple(map(int, frozen["class_streams"]["8"]["canonical_masks"]))
    frozen8_set = set(frozen8)
    x7 = {int(mask): int(value) for mask, value in
          wave163["integral_pseudocount"]["order7_mask_count_pairs"]}
    x8 = {int(mask): int(value) for mask, value in
          wave163["integral_pseudocount"]["order8_mask_count_pairs"]}
    assert len(x7) == 208 and len(x8) == len(frozen8_set) == 916
    assert set(x8) == frozen8_set

    # Exact closure graph after adding the prescribed four cross masks.
    universe35, universe37, universe41 = (set(masks35),
                                          set(masks35 + DIAGONAL_MASKS),
                                          set(masks41))
    closure_rows = []
    closure_edges = []
    for left, right in itertools.combinations_with_replacement(range(6), 2):
        support = base.completion_support(FLAGS[left], FLAGS[right])
        outside = sorted(support - universe41)
        if left != right and not outside:
            closure_edges.append((left, right))
        closure_rows.append({
            "left_flag_index": left,
            "right_flag_index": right,
            "left_flag_mask": FLAGS[left],
            "right_flag_mask": FLAGS[right],
            "support_size": len(support),
            "outside_41_masks": outside,
            "closed_on_41": not outside,
        })
    expected_edges = [(0, 1), (0, 2), (1, 3),
                      (2, 4), (3, 5), (4, 5)]
    assert closure_edges == expected_edges
    assert not any({a, b, c} <= set(pair for edge in closure_edges for pair in edge)
                   and all(tuple(sorted(edge)) in closure_edges
                           for edge in ((a, b), (a, c), (b, c)))
                   for a, b, c in itertools.combinations(range(6), 3))

    # Complete deletion decks of only the four newly added cross masks.
    new_decks = []
    shadow_union = set()
    for mask in CROSS_MASKS:
        assert base.canonical(mask, 9) == mask and base.pair_upper(mask, 9)
        histogram = Counter()
        slots = []
        for removed in range(9):
            raw8, _ = base.delete(mask, 9, removed)
            shadow = base.canonical(raw8, 8)
            assert shadow in frozen8_set
            histogram[shadow] += 1
            shadow_union.add(shadow)
            slots.append({
                "deleted_vertex": removed,
                "canonical_order8_mask": shadow,
                "frozen_order8_index_0_based": frozen8.index(shadow),
                "wave163_order8_count": x8[shadow],
            })
        new_decks.append({
            "canonical_order9_mask": mask,
            "edge_count": mask.bit_count(),
            "degree_sequence": sorted(row.bit_count()
                                      for row in base.adjacency(mask, 9)),
            "deletion_histogram": [[key, value]
                                   for key, value in sorted(histogram.items())],
            "vertex_deletions": slots,
        })
    assert all(x8[shadow] > 0 for shadow in shadow_union)

    # Derive the frozen H6 counts from the H7 deletion relation.
    numerator6 = defaultdict(int)
    for mask7, count in x7.items():
        for removed in range(7):
            raw6, _ = base.delete(mask7, 7, removed)
            numerator6[base.canonical(raw6, 6)] += count
    x6 = {mask: Fraction(value, 93) for mask, value in numerator6.items()}
    assert len(x6) == 62 and all(value.denominator == 1 and value >= 0
                                 for value in x6.values())

    count_vectors = {
        6: x6,
        7: x7,
        8: x8,
        9: {mask: fixed19[index] for index, mask in enumerate(visible19)},
    }
    weighted_by_order = {}
    fixed_base = [[Fraction() for _ in range(6)] for _ in range(6)]
    coefficient_class_checks = 0
    nonzero_records = {}
    for order, counts in count_vectors.items():
        subtotal = [[Fraction() for _ in range(6)] for _ in range(6)]
        records = []
        for mask, count in sorted(counts.items()):
            matrix = flag_moment(mask, order)
            coefficient_class_checks += 1
            if any(any(row) for row in matrix):
                records.append({
                    "canonical_mask": mask,
                    "count": int(count),
                    "upper_entries": [[i, j, matrix[i][j]]
                                      for i in range(6) for j in range(i, 6)
                                      if matrix[i][j]],
                })
            add_weighted(subtotal, matrix, count)
            add_weighted(fixed_base, matrix, count)
        weighted_by_order[str(order)] = [[int(value) for value in row]
                                         for row in subtotal]
        nonzero_records[str(order)] = records
    assert coefficient_class_checks == 62 + 208 + 916 + 19
    assert all(value.denominator == 1 for row in fixed_base for value in row)
    fixed_base_int = [[int(value) for value in row] for row in fixed_base]

    variable_matrices = [flag_moment(mask, 9) for mask in variable_masks]
    natural_indices = (0, 4, 5, 6, 7)
    added6_natural_zero_checks = []
    for mask in added6:
        full = moment_coeff_triangle(mask, 9)
        selected = [[full[i][j] for j in natural_indices]
                    for i in natural_indices]
        assert not any(any(row) for row in selected)
        added6_natural_zero_checks.append(mask)

    # All local H8->H9 extension rows on 41 columns.
    unmarked = defaultdict(lambda: [0] * 41)
    vertex = defaultdict(lambda: [0] * 41)
    pair = defaultdict(lambda: [0] * 41)
    for column, mask9 in enumerate(masks41):
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
            for a in incident:
                for b in incident:
                    if a != b:
                        key = base.canonical(raw8, 8,
                                             (relabel[a], relabel[b]))
                        pair[(shadow, key)][column] += 1

    support_cache = {}

    def local_support(shadow, required):
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
                if image not in universe41 and first_outside is None:
                    first_outside = image
        assert support
        support_cache[cache_key] = support, first_outside
        return support, first_outside

    fixed41 = list(fixed19) + [0] * 22
    row_families = {"unmarked": [], "vertex": [], "ordered_pair": []}

    def common_row(vector, shadow, required, lhs):
        support, outside = local_support(shadow, required)
        fixed_rhs = sum(value * count for value, count in zip(vector, fixed41))
        return {
            "canonical_order8_mask": shadow,
            "wave163_lhs": lhs,
            "fixed19_rhs": fixed_rhs,
            "residual_capacity": lhs - fixed_rhs,
            "variable22_coefficients": sparse(vector[19:]),
            "closed_on_35": support <= universe35,
            "closed_on_37": support <= universe37,
            "closed_on_41": outside is None,
            "support_size": len(support),
            "first_outside_41_mask": outside,
        }

    for shadow, vector in sorted(unmarked.items()):
        row_families["unmarked"].append(common_row(
            vector, shadow, (), 91 * x8[shadow]
        ))
    for (shadow, key), vector in sorted(vertex.items()):
        graph8 = base.adjacency(shadow, 8)
        orbit = tuple(root for root in range(8)
                      if base.canonical(shadow, 8, (root,)) == key)
        degree = graph8[orbit[0]].bit_count()
        row = common_row(vector, shadow, (orbit[0],),
                         len(orbit) * (14 - degree) * x8[shadow])
        row.update({"rooted_key": key})
        row_families["vertex"].append(row)
    for (shadow, key), vector in sorted(pair.items()):
        graph8 = base.adjacency(shadow, 8)
        orbit = tuple((a, b) for a in range(8) for b in range(8) if a != b
                      and base.canonical(shadow, 8, (a, b)) == key)
        a, b = orbit[0]
        adjacent = bool(graph8[a] & (1 << b))
        current = (graph8[a] & graph8[b]).bit_count()
        capacity = (1 if adjacent else 2) - current
        assert capacity > 0
        row = common_row(vector, shadow, tuple(sorted((a, b))),
                         len(orbit) * capacity * x8[shadow])
        row.update({"ordered_pair_rooted_key": key})
        row_families["ordered_pair"].append(row)

    closed_equations = []
    for family, rows in row_families.items():
        for index, row in enumerate(rows):
            if not row["closed_on_41"]:
                continue
            vector = [0] * 22
            for coordinate, value in row["variable22_coefficients"]:
                vector[int(coordinate)] = int(value)
            closed_equations.append((vector, int(row["residual_capacity"]),
                                     family, index))
    unique_closed = sorted({(tuple(vector), rhs)
                            for vector, rhs, _, _ in closed_equations})

    old_witness = list(map(int, r0["exact_integer_T0_projection_witness"]
                           ["counts_old9_then_new7"]))
    candidate = old_witness + [8316, 74844, 8316, 74844, 8316, 66528]
    violations = []
    for family, rows in row_families.items():
        for index, row in enumerate(rows):
            vector = [0] * 22
            for coordinate, value in row["variable22_coefficients"]:
                vector[int(coordinate)] = int(value)
            value = sum(a * b for a, b in zip(vector, candidate))
            residual = int(row["residual_capacity"])
            bad = value != residual if row["closed_on_41"] else value > residual
            if bad:
                violations.append({"family": family, "row": index,
                                   "closed": row["closed_on_41"],
                                   "value": value, "residual": residual,
                                   "coefficients": vector})

    candidate_gram = [[Fraction(value) for value in row]
                      for row in fixed_base_int]
    for count, matrix in zip(candidate, variable_matrices):
        add_weighted(candidate_gram, matrix, count)
    closed_blocks = []
    for left, right in closure_edges:
        block = [[candidate_gram[left][left], candidate_gram[left][right]],
                 [candidate_gram[right][left], candidate_gram[right][right]]]
        determinant = block[0][0] * block[1][1] - block[0][1] ** 2
        closed_blocks.append({
            "flag_indices": [left, right],
            "matrix_at_forced_new6_candidate": [[int(value) for value in row]
                                                 for row in block],
            "determinant_at_forced_new6_candidate": int(determinant),
            "PSD_at_forced_new6_candidate": (
                block[0][0] >= 0 and block[1][1] >= 0 and determinant >= 0
            ),
            "rank": 1,
            "kernel_basis": [[1, -1]],
        })
    assert not violations
    expected_block = [[199584, 199584], [199584, 199584]]
    assert all(row["matrix_at_forced_new6_candidate"] == expected_block
               and row["PSD_at_forced_new6_candidate"]
               and row["determinant_at_forced_new6_candidate"] == 0
               for row in closed_blocks)

    minimum_open_slack = None
    for rows in row_families.values():
        for row in rows:
            if row["closed_on_41"]:
                continue
            vector = [0] * 22
            for coordinate, value in row["variable22_coefficients"]:
                vector[int(coordinate)] = int(value)
            value = sum(a * b for a, b in zip(vector, candidate))
            slack = int(row["residual_capacity"]) - value
            minimum_open_slack = slack if minimum_open_slack is None else min(
                minimum_open_slack, slack
            )

    closed_rank = rank([list(vector) for vector, _ in unique_closed])
    assert closed_rank == 13
    new_closed = [(vector, rhs, family, index)
                  for vector, rhs, family, index in closed_equations
                  if not row_families[family][index]["closed_on_35"]]
    unique_new_closed = sorted({(tuple(vector), rhs)
                                for vector, rhs, _, _ in new_closed})
    assert all(not any(vector[:16]) for vector, _ in unique_new_closed)
    new6_rank = rank([list(vector[16:]) for vector, _ in unique_new_closed])
    assert new6_rank == 6

    degree = Counter()
    for left, right in closure_edges:
        degree[left] += 1
        degree[right] += 1
    assert degree == Counter({index: 2 for index in range(6)})
    off_diagonal_deficits = Counter(
        len(row["outside_41_masks"])
        for row in closure_rows
        if row["left_flag_index"] != row["right_flag_index"]
    )
    assert off_diagonal_deficits == Counter({0: 6, 9: 6, 15: 3})

    variable_matrix_records = [{
        "variable_index": index,
        "canonical_order9_mask": mask,
        "upper_entries": [[left, right, matrix[left][right]]
                          for left in range(6)
                          for right in range(left, 6) if matrix[left][right]],
    } for index, (mask, matrix) in enumerate(zip(variable_masks,
                                                 variable_matrices))]

    result = {
        "status": "exact-41-column-six-flag-blocks-survive",
        "scope": {
            "base_order9_columns": 35,
            "diagonal_columns_carried_from_probe": 2,
            "new_cross_columns": 4,
            "total_order9_columns": 41,
            "ambient_order9_census_generated": False,
            "R1_extension_attempted": False,
            "frozen_order8_classes_regenerated": False,
            "submission_txt_written": False,
        },
        "inputs": {str(path): {"sha256": sha(path)} for path in
                   (R0_CERT, PROBE37, CROSS_CERT, DECK, WAVE147, WAVE163)},
        "six_rooted_flag_masks": list(FLAGS),
        "added_masks": {
            "diagonal_two": list(DIAGONAL_MASKS),
            "cross_four": list(CROSS_MASKS),
        },
        "cross_four_deletion_decks": {
            "slots_checked": 36,
            "distinct_frozen_order8_shadows": len(shadow_union),
            "all_deletions_in_frozen_916": True,
            "all_shadow_Wave163_counts_positive": True,
            "decks": new_decks,
        },
        "closure_graph": {
            "complete_product_scans": len(closure_rows),
            "closed_diagonals": 6,
            "closed_edges": [list(edge) for edge in closure_edges],
            "edge_count": len(closure_edges),
            "degree_sequence": sorted(degree.values()),
            "is_six_cycle": True,
            "triangle_count": 0,
            "maximum_clique_size": 2,
            "maximal_cliques": [list(edge) for edge in closure_edges],
            "off_diagonal_deficit_histogram": {
                str(key): value for key, value in sorted(
                    off_diagonal_deficits.items()
                )
            },
            "rows": closure_rows,
        },
        "six_flag_coefficient_system": {
            "convention": (
                "Raw ordered-triangle-root Gram coefficients, split by "
                "union order."
            ),
            "derived_order6_classes": len(x6),
            "coefficient_class_checks": coefficient_class_checks,
            "nonzero_class_counts_by_order": {
                order: len(rows) for order, rows in nonzero_records.items()
            },
            "weighted_fixed19_matrix_by_order": weighted_by_order,
            "weighted_fixed_orders6_to8_plus_visible19_matrix": fixed_base_int,
            "variable_order9_coefficient_matrices": variable_matrix_records,
            "added_six_have_zero_coefficients_in_prior_natural_five_block": True,
            "natural_zero_checks": added6_natural_zero_checks,
        },
        "targeted_extension_rows": {
            "row_counts": {family: len(rows)
                           for family, rows in row_families.items()},
            "closed_on_41_counts": {
                family: sum(row["closed_on_41"] for row in rows)
                for family, rows in row_families.items()
            },
            "newly_closed_beyond_35_counts": {
                family: sum(row["closed_on_41"] and not row["closed_on_35"]
                            for row in rows)
                for family, rows in row_families.items()
            },
            "unique_nonzero_closed_equations": [
                {"coefficients": list(vector), "rhs": rhs}
                for vector, rhs in unique_closed if any(vector)
            ],
            "closed_equation_rank": closed_rank,
            "new_closed_equation_rank_on_six_new_variables": new6_rank,
            "six_new_counts_uniquely_forced": candidate[-6:],
            "rows": row_families,
        },
        "closed_two_by_two_Gram_blocks": {
            "blocks": closed_blocks,
            "common_matrix": expected_block,
            "all_PSD": True,
            "all_rank": 1,
            "all_determinants": 0,
            "negative_direction": None,
        },
        "exact_integer_T0_projection_witness": {
            "variable_order": {
                "old_extra9": list(old9),
                "R0_seven": list(r0seven),
                "diagonal_two": list(DIAGONAL_MASKS),
                "cross_four": list(CROSS_MASKS),
            },
            "counts": candidate,
            "old_16_counts": candidate[:16],
            "new_six_counts": candidate[-6:],
            "all_nonnegative_integral": True,
            "all_closed_rows_hold": True,
            "all_open_row_slacks_nonnegative": True,
            "minimum_open_row_slack": minimum_open_slack,
            "all_closed_Gram_blocks_PSD": True,
            "prior_natural_five_Gram_unchanged": True,
            "new_congruence_obstruction": None,
        },
        "claim_boundary": {
            "wave163_T0_survives": True,
            "negative_direction_found": False,
            "E0_lower_bound_translation": None,
            "reason": (
                "All six licensed nontrivial blocks collapse to the same "
                "rank-one PSD matrix after the local identities uniquely "
                "fix the six new H9 counts."
            ),
            "branch_stop": (
                "The closure graph is C6, so there is no closed 3x3 block. "
                "Every missing chord still needs at least nine additional "
                "H9 masks; this bounded branch stops before adding them."
            ),
            "qualification": (
                "Open extension-row slacks are checked separately and are "
                "not claimed to arise from one ambient H9 distribution."
            ),
        },
    }
    save(OUTPUT, result)
    print(json.dumps({
        "output": str(OUTPUT),
        "closure_edges": closure_edges,
        "maximum_clique": 2,
        "new_six_counts": candidate[-6:],
        "closed_row_rank": closed_rank,
        "new_six_rank": new6_rank,
        "common_block": expected_block,
        "negative_direction": None,
    }, indent=2))


if __name__ == "__main__":
    main()
