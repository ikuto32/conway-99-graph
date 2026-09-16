"""Exact 28-column closure of the distinct-X triangle-flag products.

This is a deliberately targeted order-nine computation.  Its H9 universe is
the 19 masks in the archived mate lift plus the nine masks already identified
as the complete missing support of X_j X_k (j != k).  It reads the frozen
Wave147/Wave163 streams, and neither regenerates the 916 H8 catalogue nor
enumerates an ambient H9 census.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import os
from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache
from pathlib import Path


OUTPUT = Path("scratch_theory_order9_cross_x_closure.json")
DECK = Path("scratch_theory_minimal_order9_targeted_deck.json")
OLD_GRAM = Path("scratch_theory_order9_rooted_flag_gram.json")
WAVE147 = Path(
    "external_conway99_research/attempts/wave147-alternative-lane/"
    "exact-results.json"
)
WAVE163 = Path("scratch_theory_wave163_integral_order8_boundary.json")

EXTRA_MASKS = (
    1452696264,
    3667223248,
    3669518466,
    6091774020,
    10042630856,
    14681708612,
    36940436610,
    61422027409,
    61424673410,
)
FLAG_NAMES = ("X_0", "X_1", "X_2", "P")


def atomic_json(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


@lru_cache(maxsize=None)
def edges(order: int) -> tuple[tuple[int, int], ...]:
    return tuple(itertools.combinations(range(order), 2))


@lru_cache(maxsize=None)
def positions(order: int) -> dict[tuple[int, int], int]:
    return {edge: index for index, edge in enumerate(edges(order))}


def adjacency(mask: int, order: int) -> tuple[int, ...]:
    rows = [0] * order
    for bit, (left, right) in enumerate(edges(order)):
        if mask & (1 << bit):
            rows[left] |= 1 << right
            rows[right] |= 1 << left
    return tuple(rows)


def transform(mask: int, order: int, permutation: tuple[int, ...]) -> int:
    target = positions(order)
    answer = 0
    for bit, (left, right) in enumerate(edges(order)):
        if mask & (1 << bit):
            image = tuple(sorted((permutation[left], permutation[right])))
            answer |= 1 << target[image]
    return answer


@lru_cache(maxsize=None)
def canonical(mask: int, order: int, roots: tuple[int, ...] = ()) -> int:
    graph = adjacency(mask, order)
    root_set = set(roots)
    cells: dict[tuple[int, ...], list[int]] = defaultdict(list)
    for vertex in range(order):
        if vertex in root_set:
            continue
        signature = (
            graph[vertex].bit_count(),
            *(int(bool(graph[vertex] & (1 << root))) for root in roots),
        )
        cells[signature].append(vertex)
    choices = []
    start = len(roots)
    for signature in sorted(cells):
        sources = cells[signature]
        targets = tuple(range(start, start + len(sources)))
        start += len(sources)
        choices.append(tuple(
            tuple(zip(sources, image))
            for image in itertools.permutations(targets)
        ))
    best = None
    for selected in itertools.product(*choices):
        permutation = [0] * order
        for target, root in enumerate(roots):
            permutation[root] = target
        for cell in selected:
            for source, target in cell:
                permutation[source] = target
        candidate = transform(mask, order, tuple(permutation))
        best = candidate if best is None else min(best, candidate)
    assert best is not None
    return best


def delete(mask: int, order: int, removed: int) -> tuple[int, dict[int, int]]:
    kept = tuple(vertex for vertex in range(order) if vertex != removed)
    relabel = {old: new for new, old in enumerate(kept)}
    source = positions(order)
    answer = 0
    for bit, pair in enumerate(itertools.combinations(kept, 2)):
        if mask & (1 << source[pair]):
            answer |= 1 << bit
    return answer, relabel


def induced(mask: int, order: int, chosen: tuple[int, ...]) -> int:
    graph = adjacency(mask, order)
    answer = 0
    target = positions(len(chosen))
    for left_index, left in enumerate(chosen):
        for right_index in range(left_index + 1, len(chosen)):
            right = chosen[right_index]
            if graph[left] & (1 << right):
                answer |= 1 << target[(left_index, right_index)]
    return answer


def extend(mask8: int, neighbors: tuple[int, ...]) -> int:
    answer = 0
    target = positions(9)
    for bit, edge in enumerate(edges(8)):
        if mask8 & (1 << bit):
            answer |= 1 << target[edge]
    for vertex in neighbors:
        answer |= 1 << target[(vertex, 8)]
    return answer


def pair_upper(mask: int, order: int) -> bool:
    graph = adjacency(mask, order)
    if any(row.bit_count() > 14 for row in graph):
        return False
    return all(
        (graph[left] & graph[right]).bit_count()
        <= (1 if graph[left] & (1 << right) else 2)
        for left, right in edges(order)
    )


def relation_type(graph: tuple[int, ...], roots: tuple[int, ...],
                  free: tuple[int, ...]) -> int | None:
    if not all(graph[left] & (1 << right)
               for left, right in itertools.combinations(free, 2)):
        return None
    root_degrees = [
        sum(bool(graph[root] & (1 << vertex)) for vertex in free)
        for root in roots
    ]
    free_degrees = [
        sum(bool(graph[vertex] & (1 << root)) for root in roots)
        for vertex in free
    ]
    cross_edges = sum(root_degrees)
    if (cross_edges == 2 and sorted(root_degrees) == [0, 1, 1]
            and sorted(free_degrees) == [0, 1, 1]):
        return root_degrees.index(0)
    if root_degrees == [1, 1, 1] and free_degrees == [1, 1, 1]:
        return 3
    return None


def moment_coeff(mask: int, order: int) -> list[list[int]]:
    """Raw ordered-root coefficient matrix for X_0,X_1,X_2,P."""

    graph = adjacency(mask, order)
    matrix = [[0] * 4 for _ in range(4)]
    for roots in itertools.permutations(range(order), 3):
        if not all(graph[left] & (1 << right)
                   for left, right in itertools.combinations(roots, 2)):
            continue
        available = tuple(vertex for vertex in range(order)
                          if vertex not in roots)
        flags = []
        for free in itertools.combinations(available, 3):
            kind = relation_type(graph, roots, free)
            if kind is not None:
                flags.append((free, kind))
        for left, left_kind in flags:
            for right, right_kind in flags:
                if len(set(roots) | set(left) | set(right)) == order:
                    matrix[left_kind][right_kind] += 1
    return matrix


def upper_entries(matrix: list[list[int]]) -> list[list[int]]:
    return [
        [left, right, matrix[left][right]]
        for left in range(len(matrix))
        for right in range(left, len(matrix))
        if matrix[left][right]
    ]


def natural_flag_masks() -> tuple[int, ...]:
    """The eight R0,R1_j,X_j,P order-six triangle-rooted flags."""

    answer = []
    base = set(itertools.combinations(range(3), 2))
    base.update(itertools.combinations(range(3, 6), 2))
    for kind in range(8):
        chosen = set(base)
        if 1 <= kind <= 3:
            chosen.add((kind - 1, 3))
        elif 4 <= kind <= 6:
            omitted = kind - 4
            retained = [root for root in range(3) if root != omitted]
            chosen.update(((retained[0], 4), (retained[1], 5)))
        elif kind == 7:
            chosen.update(((0, 3), (1, 4), (2, 5)))
        mask = sum(1 << positions(6)[tuple(sorted(edge))] for edge in chosen)
        answer.append(canonical(mask, 6, (0, 1, 2)))
    assert len(set(answer)) == 8
    return tuple(answer)


def glue_flags(left_flag: int, right_flag: int, cross_bits: int) -> int:
    chosen = set()
    for bit, (left, right) in enumerate(edges(6)):
        if left_flag & (1 << bit):
            chosen.add((left, right))
        if right_flag & (1 << bit):
            image_left = left if left < 3 else left + 3
            image_right = right if right < 3 else right + 3
            chosen.add(tuple(sorted((image_left, image_right))))
    cross = tuple(itertools.product(range(3, 6), range(6, 9)))
    for bit, edge in enumerate(cross):
        if cross_bits & (1 << bit):
            chosen.add(edge)
    return sum(1 << positions(9)[edge] for edge in chosen)


def completion_support(left_flag: int, right_flag: int) -> set[int]:
    support = set()
    for cross_bits in range(1 << 9):
        mask = glue_flags(left_flag, right_flag, cross_bits)
        if pair_upper(mask, 9):
            support.add(canonical(mask, 9))
    assert support
    return support


def sparse(vector: list[int]) -> list[list[int]]:
    return [[index, value] for index, value in enumerate(vector) if value]


def matrix_rank(matrix: list[list[int]]) -> int:
    if not matrix:
        return 0
    rows = [[Fraction(value) for value in row] for row in matrix]
    rank = 0
    for column in range(len(rows[0])):
        pivot = next((row for row in range(rank, len(rows))
                      if rows[row][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][column]
        rows[rank] = [value / scale for value in rows[rank]]
        for row in range(len(rows)):
            if row == rank or not rows[row][column]:
                continue
            scale = rows[row][column]
            rows[row] = [value - scale * pivot_value
                         for value, pivot_value in zip(rows[row], rows[rank])]
        rank += 1
    return rank


def main() -> None:
    deck = json.loads(DECK.read_text(encoding="utf-8"))
    old_gram = json.loads(OLD_GRAM.read_text(encoding="utf-8"))
    frozen = json.loads(WAVE147.read_text(encoding="utf-8"))
    wave163 = json.loads(WAVE163.read_text(encoding="utf-8"))
    projection = deck["T0_all_G_targeted_order9_projection"]

    visible = tuple(map(int, projection["visible_19_H9_masks"]))
    q19 = tuple(map(int, projection["wave163_visible_19_candidate_counts"]))
    masks28 = visible + EXTRA_MASKS
    assert len(visible) == 19 and len(set(masks28)) == 28
    frozen8 = tuple(map(int, frozen["class_streams"]["8"]["canonical_masks"]))
    frozen8_set = set(frozen8)
    assert len(frozen8_set) == 916
    x8 = {int(mask): int(count) for mask, count in
          wave163["integral_pseudocount"]["order8_mask_count_pairs"]}
    assert set(x8) == frozen8_set

    # Complete extra-nine unmarked deletion deck into the frozen H8 stream.
    extra_decks = []
    for extra_index, mask in enumerate(EXTRA_MASKS):
        assert canonical(mask, 9) == mask
        assert pair_upper(mask, 9)
        histogram = Counter()
        deletion_rows = []
        for removed in range(9):
            raw8, _ = delete(mask, 9, removed)
            shadow = canonical(raw8, 8)
            assert shadow in frozen8_set
            histogram[shadow] += 1
            deletion_rows.append({
                "deleted_vertex": removed,
                "canonical_order8_mask": shadow,
                "frozen_order8_index_0_based": frozen8.index(shadow),
                "wave163_order8_count": x8[shadow],
            })
        extra_decks.append({
            "extra_index": extra_index,
            "canonical_order9_mask": mask,
            "edge_count": mask.bit_count(),
            "degree_sequence": sorted(row.bit_count()
                                      for row in adjacency(mask, 9)),
            "deletion_histogram": [[key, value]
                                   for key, value in sorted(histogram.items())],
            "vertex_deletions": deletion_rows,
        })

    # Direct coefficient matrices.  The old 19-column evaluation is consumed
    # only as a drift check; every added coefficient is recomputed here.
    records28 = []
    matrices28 = []
    for index, mask in enumerate(masks28):
        matrix = moment_coeff(mask, 9)
        matrices28.append(matrix)
        records28.append({
            "column_index": index,
            "kind": "visible19" if index < 19 else "extra9",
            "canonical_order9_mask": mask,
            "upper_entries": upper_entries(matrix),
        })
    old_full = old_gram["hostile_full_eight_type_zero_fill_control"]["matrix"]
    old_block = [[int(old_full[i][j]) for j in (4, 5, 6, 7)]
                 for i in (4, 5, 6, 7)]
    assert old_block == [
        [199584, 29352, 29352, 0],
        [29352, 199584, 29352, 0],
        [29352, 29352, 199584, 0],
        [0, 0, 0, 0],
    ]
    extra_cross_weights = []
    for matrix in matrices28[19:]:
        weight = matrix[0][1]
        assert weight in (2, 6)
        assert matrix[0][2] == matrix[1][2] == weight
        assert all(matrix[i][i] == 0 for i in range(4))
        assert all(matrix[i][3] == matrix[3][i] == 0 for i in range(4))
        extra_cross_weights.append(weight)
    assert extra_cross_weights == [2, 6, 2, 2, 6, 2, 2, 6, 2]

    # At T=0 every target triangle has q=12 and P=0.  There are 231
    # (unordered) target triangles and six root orderings.  Hence every X_j
    # count is 12 at each ordered root, and the exact Gram is 1386*12^2 J_3.
    ordered_triangle_roots = 231 * 6
    gram_entry = ordered_triangle_roots * 12 * 12
    missing_cross = gram_entry - old_block[0][1]
    assert gram_entry == 199584 and missing_cross == 170232
    mass_coefficients = [weight // 2 for weight in extra_cross_weights]
    mass_rhs = missing_cross // 2
    assert mass_coefficients == [1, 3, 1, 1, 3, 1, 1, 3, 1]
    assert mass_rhs == 85116
    exact_matrix = [[gram_entry if i < 3 and j < 3 else 0
                     for j in range(4)] for i in range(4)]

    # A direct glue scan certifies that these are exactly (not merely some of)
    # the missing columns for all three distinct-X products.  It also locates
    # the smallest next enlargement of the now closed four-flag block.
    natural = natural_flag_masks()
    cross_support_records = []
    outside_cross_union = set()
    for left, right in ((4, 5), (4, 6), (5, 6)):
        support = completion_support(natural[left], natural[right])
        outside = sorted(support - set(visible))
        assert set(outside) == set(EXTRA_MASKS)
        assert support <= set(masks28)
        outside_cross_union.update(outside)
        cross_support_records.append({
            "left_flag": ("X_0", "X_1", "X_2")[left - 4],
            "right_flag": ("X_0", "X_1", "X_2")[right - 4],
            "canonical_support_size": len(support),
            "outside_visible19_masks": outside,
            "closed_on_28": True,
        })
    assert outside_cross_union == set(EXTRA_MASKS)

    full_names = ("R0", "R1_0", "R1_1", "R1_2",
                  "X_0", "X_1", "X_2", "P")
    next_candidates = []
    for candidate in range(4):
        missing = set()
        product_rows = []
        for partner in (candidate, 4, 5, 6, 7):
            left, right = sorted((candidate, partner))
            support = completion_support(natural[left], natural[right])
            outside = sorted(support - set(masks28))
            missing.update(outside)
            product_rows.append({
                "partner": full_names[partner],
                "outside_28_masks": outside,
            })
        next_candidates.append({
            "candidate_flag": full_names[candidate],
            "additional_masks_needed": len(missing),
            "missing_mask_union": sorted(missing),
            "product_rows": product_rows,
        })
    assert [row["additional_masks_needed"] for row in next_candidates] == [
        7, 17, 17, 17
    ]
    next_missing = next_candidates[0]["missing_mask_union"]
    assert next_missing == [
        1292419201, 3668590721, 13610256401, 14889779459,
        24436319376, 32214460576, 35652157569,
    ]
    derived_flags74 = tuple(int(row["triangle_rooted_flag_mask"])
                            for row in old_gram[
                                "complete_visible_support_closure_test"
                            ]["diagonal_rows"])
    assert len(derived_flags74) == len(set(derived_flags74)) == 74
    diagonal_scan74 = []
    for flag in derived_flags74:
        support = completion_support(flag, flag)
        outside = sorted(support - set(masks28))
        diagonal_scan74.append({
            "triangle_rooted_flag_mask": flag,
            "closed_on_28": not outside,
            "outside_28_count": len(outside),
            "outside_28_masks": outside,
        })
    closed_diagonal74 = sorted(row["triangle_rooted_flag_mask"]
                               for row in diagonal_scan74
                               if row["closed_on_28"])
    assert closed_diagonal74 == sorted(natural[4:])
    minimum_open_diagonal = min(row["outside_28_count"]
                                for row in diagonal_scan74
                                if not row["closed_on_28"])
    minimum_open_rows = [row for row in diagonal_scan74
                         if row["outside_28_count"] == minimum_open_diagonal]
    assert minimum_open_diagonal == 2
    assert [row["triangle_rooted_flag_mask"] for row in minimum_open_rows] == [
        24699, 24939, 25147, 25507, 27179, 27299
    ]
    assert all(row["outside_28_masks"] == [46817920192, 56196485312]
               for row in minimum_open_rows)

    # Targeted H8->H9 rows on all 28 columns.  Enumerating possible
    # neighbourhoods of a single ninth vertex is only a local closure test.
    unmarked: dict[int, list[int]] = defaultdict(lambda: [0] * 28)
    vertex: dict[tuple[int, int], list[int]] = defaultdict(lambda: [0] * 28)
    pair: dict[tuple[int, int], list[int]] = defaultdict(lambda: [0] * 28)
    for column, mask9 in enumerate(masks28):
        graph9 = adjacency(mask9, 9)
        for removed in range(9):
            raw8, relabel = delete(mask9, 9, removed)
            shadow = canonical(raw8, 8)
            unmarked[shadow][column] += 1
            neighbors = tuple(vertex9 for vertex9 in range(9)
                              if vertex9 != removed
                              and graph9[removed] & (1 << vertex9))
            for root in neighbors:
                key = canonical(raw8, 8, (relabel[root],))
                vertex[(shadow, key)][column] += 1
            for left in neighbors:
                for right in neighbors:
                    if left == right:
                        continue
                    key = canonical(raw8, 8,
                                    (relabel[left], relabel[right]))
                    pair[(shadow, key)][column] += 1

    universe28 = set(masks28)
    support_cache: dict[tuple[int, tuple[int, ...]], tuple[set[int], int | None]] = {}

    def extension_support(mask8: int, required: tuple[int, ...]):
        cache_key = (mask8, tuple(sorted(required)))
        if cache_key in support_cache:
            return support_cache[cache_key]
        remaining = tuple(vertex8 for vertex8 in range(8)
                          if vertex8 not in required)
        support = set()
        first_outside = None
        for size in range(len(remaining) + 1):
            for extra in itertools.combinations(remaining, size):
                neighbors = tuple(sorted(required + extra))
                candidate = extend(mask8, neighbors)
                if not pair_upper(candidate, 9):
                    continue
                image = canonical(candidate, 9)
                support.add(image)
                if image not in universe28 and first_outside is None:
                    first_outside = image
        assert support
        support_cache[cache_key] = (support, first_outside)
        return support, first_outside

    row_families: dict[str, list[dict]] = {
        "unmarked": [], "vertex": [], "ordered_pair": []
    }
    fixed28 = list(q19) + [0] * 9

    def common_row(vector: list[int], shadow: int,
                   required: tuple[int, ...], lhs: int) -> dict:
        support, outside = extension_support(shadow, required)
        fixed_rhs = sum(vector[index] * fixed28[index]
                        for index in range(28))
        extra_vector = vector[19:]
        return {
            "canonical_order8_mask": shadow,
            "wave163_lhs": lhs,
            "fixed_visible19_rhs": fixed_rhs,
            "residual_capacity_before_extra9": lhs - fixed_rhs,
            "extra9_coefficients": sparse(extra_vector),
            "closed_on_19": support <= set(visible),
            "closed_on_28": outside is None,
            "support_size": len(support),
            "first_outside_28_mask": outside,
        }

    for shadow, vector in sorted(unmarked.items()):
        lhs = 91 * x8[shadow]
        row_families["unmarked"].append(common_row(vector, shadow, (), lhs))
    for (shadow, key), vector in sorted(vertex.items()):
        graph8 = adjacency(shadow, 8)
        orbit = tuple(root for root in range(8)
                      if canonical(shadow, 8, (root,)) == key)
        degree = graph8[orbit[0]].bit_count()
        lhs = len(orbit) * (14 - degree) * x8[shadow]
        row = common_row(vector, shadow, (orbit[0],), lhs)
        row.update({
            "rooted_key": key,
            "root_orbit_size": len(orbit),
            "outside_neighbor_capacity": 14 - degree,
        })
        row_families["vertex"].append(row)
    for (shadow, key), vector in sorted(pair.items()):
        graph8 = adjacency(shadow, 8)
        orbit = tuple((left, right)
                      for left in range(8) for right in range(8)
                      if left != right
                      and canonical(shadow, 8, (left, right)) == key)
        left, right = orbit[0]
        adjacent = bool(graph8[left] & (1 << right))
        common = (graph8[left] & graph8[right]).bit_count()
        capacity = (1 if adjacent else 2) - common
        assert capacity > 0
        lhs = len(orbit) * capacity * x8[shadow]
        row = common_row(vector, shadow, tuple(sorted((left, right))), lhs)
        row.update({
            "ordered_pair_rooted_key": key,
            "ordered_pair_orbit_size": len(orbit),
            "root_relation": "edge" if adjacent else "nonedge",
            "outside_common_neighbor_capacity": capacity,
        })
        row_families["ordered_pair"].append(row)

    # The exact integer witness below is verified against every row.  Keeping
    # it in the certificate (instead of trusting an optimizer transcript)
    # makes the feasibility claim replayable with the Python standard library.
    witness = [0, 0, 25986, 36192, 0, 6792, 10224, 0, 5922]

    # Replay the witness without trusting the solver status.
    assert sum(a * b for a, b in zip(mass_coefficients, witness)) == mass_rhs
    exact_rows = []
    open_min_slack = None
    for family, rows in row_families.items():
        for row_index, row in enumerate(rows):
            coefficients = [0] * 9
            for index, value in row["extra9_coefficients"]:
                coefficients[int(index)] = int(value)
            value = sum(a * b for a, b in zip(coefficients, witness))
            residual = int(row["residual_capacity_before_extra9"])
            if row["closed_on_28"]:
                assert value == residual
                exact_rows.append((family, row_index, coefficients, residual))
            else:
                assert value <= residual
                slack = residual - value
                open_min_slack = slack if open_min_slack is None else min(
                    open_min_slack, slack
                )
    closed_matrix = [row[2] for row in exact_rows]
    closed_augmented_rank = matrix_rank(
        [row + [rhs] for row, rhs in
         [(record[2], record[3]) for record in exact_rows]]
    ) if exact_rows else 0
    unique_nonzero_closed = sorted({
        (tuple(record[2]), record[3])
        for record in exact_rows if any(record[2])
    })
    expected_unique_equations = [
        ((0, 0, 0, 0, 2, 2, 0, 0, 0), 13584),
        ((0, 0, 0, 0, 2, 0, 1, 0, 0), 10224),
        ((0, 0, 0, 0, 0, 0, 0, 6, 2), 11844),
        ((0, 6, 1, 0, 2, 0, 0, 0, 0), 25986),
        ((2, 0, 1, 2, 0, 0, 1, 0, 0), 108594),
    ]
    assert sorted(expected_unique_equations) == unique_nonzero_closed
    # The Gram mass row is exactly one half of these five undivided rows.
    assert [sum(row[0][index] for row in unique_nonzero_closed) // 2
            for index in range(9)] == mass_coefficients
    assert sum(row[1] for row in unique_nonzero_closed) // 2 == mass_rhs

    result = {
        "status": "exact-28-column-cross-X-closure-survives",
        "scope": {
            "order9_columns": 28,
            "original_visible_columns": 19,
            "added_columns": 9,
            "ambient_order9_census_generated": False,
            "frozen_order8_classes_regenerated": False,
            "submission_txt_written": False,
        },
        "inputs": {str(path): {"sha256": sha256(path)}
                   for path in (DECK, OLD_GRAM, WAVE147, WAVE163)},
        "added_nine_masks": list(EXTRA_MASKS),
        "added_nine_deletion_decks": {
            "slots_checked": 81,
            "all_deletions_in_frozen_916": True,
            "distinct_order8_shadows": len({
                row["canonical_order8_mask"]
                for deck_row in extra_decks
                for row in deck_row["vertex_deletions"]
            }),
            "decks": extra_decks,
        },
        "minimal_closed_gram_block": {
            "flags": list(FLAG_NAMES),
            "raw_coefficient_records_on_28_columns": records28,
            "direct_distinct_X_completion_scans": cross_support_records,
            "extra9_cross_weights": extra_cross_weights,
            "old_visible19_zero_fill_matrix": old_block,
            "endpoint_facts": {
                "unordered_target_triangles": 231,
                "ordered_target_triangle_roots": ordered_triangle_roots,
                "q_of_every_triangle": 12,
                "P_of_every_ordered_triangle_root": 0,
            },
            "extra_count_equation": {
                "coefficients": mass_coefficients,
                "rhs": mass_rhs,
                "undivided_cross_coefficients": extra_cross_weights,
                "undivided_rhs": missing_cross,
            },
            "exact_T0_matrix": exact_matrix,
            "PSD": True,
            "rank": 1,
            "kernel_basis": [
                [1, -1, 0, 0],
                [1, 0, -1, 0],
                [0, 0, 0, 1],
            ],
            "negative_direction": None,
        },
        "minimal_next_missing_columns": {
            "meaning": (
                "Additional H9 masks required to adjoin one more natural "
                "matching flag to the closed {X_0,X_1,X_2,P} block."
            ),
            "candidate_rows": next_candidates,
            "minimum_candidate": "R0",
            "minimum_additional_column_count": 7,
            "required_masks": next_missing,
            "smallest_integer_mask": next_missing[0],
            "all_74_visible_derived_diagonal_scan": {
                "flags_checked": 74,
                "closed_diagonals": closed_diagonal74,
                "minimum_missing_columns_for_any_open_diagonal": 2,
                "minimizing_flag_masks": [
                    row["triangle_rooted_flag_mask"]
                    for row in minimum_open_rows
                ],
                "common_two_missing_masks": [46817920192, 56196485312],
                "rows": diagonal_scan74,
            },
            "scope_note": (
                "The two common masks are the smallest next diagonal data "
                "need among all 74 previously extracted flags.  To adjoin "
                "one complete natural matching flag to the existing block, "
                "R0 is cheaper than any R1_j and requires the seven masks "
                "listed above."
            ),
        },
        "targeted_extension_rows": {
            "row_counts": {family: len(rows)
                           for family, rows in row_families.items()},
            "closed_on_28_counts": {
                family: sum(row["closed_on_28"] for row in rows)
                for family, rows in row_families.items()
            },
            "newly_closed_beyond_19_counts": {
                family: sum(row["closed_on_28"] and not row["closed_on_19"]
                            for row in rows)
                for family, rows in row_families.items()
            },
            "closed_extra_coefficient_rank": matrix_rank(closed_matrix),
            "closed_augmented_rank": closed_augmented_rank,
            "five_unique_nonzero_equations": [
                {"coefficients": list(coefficients), "rhs": rhs}
                for coefficients, rhs in unique_nonzero_closed
            ],
            "gram_mass_is_half_sum_of_five_equations": True,
            "rows": row_families,
        },
        "exact_nonnegative_extension_witness": {
            "extra9_counts": witness,
            "all_integral_nonnegative": True,
            "gram_mass_holds": True,
            "all_closed_rows_hold": True,
            "all_open_row_slacks_nonnegative": True,
            "minimum_open_row_slack": open_min_slack,
        },
        "exact_boundary": {
            "wave163_T0_survives": True,
            "negative_direction_found": False,
            "closed_affine_integer_family": {
                "free_parameters": ["a=e1", "b=e4", "c=e7", "d=e0"],
                "coordinates": [
                    "e0=d",
                    "e1=a",
                    "e2=25986-6a-2b",
                    "e3=36192+3a+2b-d",
                    "e4=b",
                    "e5=6792-b",
                    "e6=10224-2b",
                    "e7=c",
                    "e8=5922-3c",
                ],
                "nonnegative_parameter_region": [
                    "a,b,c,d are nonnegative integers",
                    "3a+b<=12993",
                    "b<=5112",
                    "c<=1974",
                    "d<=36192+3a+2b",
                ],
            },
            "congruence_consequences": ["e2 is even", "e6 is even"],
            "new_frozen_Wave163_congruence_obstruction": None,
            "qualification": (
                "The witness certifies the 28-column projection only; open "
                "extension-row slacks are not asserted to arise from one "
                "simultaneous ambient H9 distribution."
            ),
        },
    }
    atomic_json(OUTPUT, result)
    print(json.dumps({
        "output": str(OUTPUT),
        "extra_deletions": 81,
        "extra_shadows": result["added_nine_deletion_decks"][
            "distinct_order8_shadows"
        ],
        "cross_weights": extra_cross_weights,
        "exact_matrix": exact_matrix,
        "closed_rows": result["targeted_extension_rows"][
            "closed_on_28_counts"
        ],
        "witness": witness,
    }, indent=2))


if __name__ == "__main__":
    main()
