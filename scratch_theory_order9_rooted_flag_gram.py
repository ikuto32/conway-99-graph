"""Small rooted-flag Gram matrices supported by the 19 visible H9 masks.

The target type is an ordered triangle (c,d,m).  An order-six flag adds a
second triangle S.  Pair-upper admissibility makes the cross graph a
matching, giving the eight natural flag types R0, R1_0..R1_2, X_0..X_2, P.
Here X_j is a two-edge matching whose unmatched target root is j, and P is a
perfect matching.

Two equivalent presentations are constructed:

* three roots: the ordered target triangle is fixed;
* two roots: only the ordered edge (c,d) is fixed and its unique triangle
  mate m is carried as a free vertex of every flag.

The latter flags nominally have four free vertices, but any two copies share
the unique mate, so their actual union has order at most nine.  The producer
uses only the frozen H7/H8 counts and the 19 H9 columns.  It never enumerates
ambient H9 classes or regenerates the frozen 916 H8 classes.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import os
from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache
from pathlib import Path


OUTPUT = Path("scratch_theory_order9_rooted_flag_gram.json")
DECK = Path("scratch_theory_minimal_order9_targeted_deck.json")
WAVE163 = Path("scratch_theory_wave163_integral_order8_boundary.json")
WAVE147 = Path(
    "external_conway99_research/attempts/wave147-alternative-lane/"
    "exact-results.json"
)


def sha256(path: Path) -> str:
    state = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            state.update(block)
    return state.hexdigest()


def atomic_json(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


@lru_cache(maxsize=None)
def edges(order: int):
    return tuple(itertools.combinations(range(order), 2))


@lru_cache(maxsize=None)
def positions(order: int):
    return {edge: index for index, edge in enumerate(edges(order))}


def adjacency(mask: int, order: int):
    rows = [0] * order
    for bit, (left, right) in enumerate(edges(order)):
        if mask & (1 << bit):
            rows[left] |= 1 << right
            rows[right] |= 1 << left
    return tuple(rows)


def transform(mask: int, order: int, permutation):
    target = positions(order)
    answer = 0
    for bit, (left, right) in enumerate(edges(order)):
        if mask & (1 << bit):
            image = tuple(sorted((permutation[left], permutation[right])))
            answer |= 1 << target[image]
    return answer


@lru_cache(maxsize=None)
def canonical(mask: int, order: int, roots: tuple[int, ...] = ()):
    graph = adjacency(mask, order)
    root_set = set(roots)
    cells = defaultdict(list)
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
        candidate = transform(mask, order, permutation)
        best = candidate if best is None else min(best, candidate)
    assert best is not None
    return best


def delete(mask: int, order: int, removed: int):
    kept = tuple(vertex for vertex in range(order) if vertex != removed)
    source = positions(order)
    answer = 0
    for bit, pair in enumerate(itertools.combinations(kept, 2)):
        if mask & (1 << source[pair]):
            answer |= 1 << bit
    return answer


def induced(mask: int, order: int, chosen: tuple[int, ...]):
    graph = adjacency(mask, order)
    relabel = {old: new for new, old in enumerate(chosen)}
    answer = 0
    target = positions(len(chosen))
    for left, right in itertools.combinations(chosen, 2):
        if graph[left] & (1 << right):
            answer |= 1 << target[tuple(sorted((relabel[left], relabel[right])))]
    return answer


def pair_upper(mask: int, order: int):
    graph = adjacency(mask, order)
    return all(
        (graph[left] & graph[right]).bit_count()
        <= (1 if graph[left] & (1 << right) else 2)
        for left, right in edges(order)
    )


FLAG_NAMES = (
    "R0", "R1_0", "R1_1", "R1_2",
    "X_0", "X_1", "X_2", "P",
)


def relation_type(graph, roots, free):
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
    if cross_edges == 0:
        return 0
    if (cross_edges == 1 and sorted(root_degrees) == [0, 0, 1]
            and sorted(free_degrees) == [0, 0, 1]):
        return 1 + root_degrees.index(1)
    if (cross_edges == 2 and sorted(root_degrees) == [0, 1, 1]
            and sorted(free_degrees) == [0, 1, 1]):
        return 4 + root_degrees.index(0)
    if root_degrees == [1, 1, 1] and free_degrees == [1, 1, 1]:
        return 7
    return None


def flag_masks():
    """Canonical rooted masks for the eight matching relations."""

    root_triangle = set(itertools.combinations(range(3), 2))
    free_triangle = set(itertools.combinations(range(3, 6), 2))
    answer = []
    for index in range(8):
        graph_edges = set(root_triangle | free_triangle)
        if 1 <= index <= 3:
            root = index - 1
            graph_edges.add((root, 3))
        elif 4 <= index <= 6:
            unmatched = index - 4
            matched_roots = [root for root in range(3) if root != unmatched]
            graph_edges.add(tuple(sorted((matched_roots[0], 4))))
            graph_edges.add(tuple(sorted((matched_roots[1], 5))))
        elif index == 7:
            graph_edges.update(((0, 3), (1, 4), (2, 5)))
        mask = sum(1 << positions(6)[tuple(sorted(edge))]
                   for edge in graph_edges)
        answer.append(canonical(mask, 6, (0, 1, 2)))
    assert len(set(answer)) == 8
    return tuple(answer)


def edge_rooted_flag_masks(triangle_masks):
    # Forget that root 2 is labelled; it is intrinsically the unique common
    # neighbor of ordered roots 0,1 in each of these flags.
    return tuple(canonical(mask, 6, (0, 1)) for mask in triangle_masks)


def extract_triangle_rooted_flags(visible_masks):
    result = set()
    for mask in visible_masks:
        graph = adjacency(mask, 9)
        for roots in itertools.permutations(range(9), 3):
            if not all(graph[left] & (1 << right)
                       for left, right in itertools.combinations(roots, 2)):
                continue
            available = tuple(vertex for vertex in range(9)
                              if vertex not in roots)
            for free in itertools.combinations(available, 3):
                small = induced(mask, 9, roots + free)
                result.add(canonical(small, 6, (0, 1, 2)))
    return tuple(sorted(result))


def glue_flags(left_flag: int, right_flag: int, cross_bits: int):
    """Glue two triangle-rooted order-six flags to labelled order nine."""

    answer_edges = set()
    for bit, (left, right) in enumerate(edges(6)):
        if left_flag & (1 << bit):
            answer_edges.add((left, right))
        if right_flag & (1 << bit):
            image_left = left if left < 3 else left + 3
            image_right = right if right < 3 else right + 3
            answer_edges.add(tuple(sorted((image_left, image_right))))
    cross = tuple(itertools.product(range(3, 6), range(6, 9)))
    for bit, edge in enumerate(cross):
        if cross_bits & (1 << bit):
            answer_edges.add(edge)
    return sum(1 << positions(9)[edge] for edge in answer_edges)


def completion_support(left_flag: int, right_flag: int):
    labelled = 0
    support = Counter()
    for cross_bits in range(1 << 9):
        mask = glue_flags(left_flag, right_flag, cross_bits)
        if not pair_upper(mask, 9):
            continue
        labelled += 1
        support[canonical(mask, 9)] += 1
    assert labelled
    return labelled, support


def moment_coeff_triangle(mask: int, order: int):
    graph = adjacency(mask, order)
    matrix = [[0] * 8 for _ in range(8)]
    for roots in itertools.permutations(range(order), 3):
        if not all(graph[left] & (1 << right)
                   for left, right in itertools.combinations(roots, 2)):
            continue
        flags = []
        available = tuple(vertex for vertex in range(order)
                          if vertex not in roots)
        for free in itertools.combinations(available, 3):
            kind = relation_type(graph, roots, free)
            if kind is not None:
                flags.append((free, kind))
        for left, left_kind in flags:
            for right, right_kind in flags:
                if len(set(roots) | set(left) | set(right)) == order:
                    matrix[left_kind][right_kind] += 1
    return matrix


def moment_coeff_edge(mask: int, order: int, edge_flag_index):
    """Independent two-root enumeration with the mate carried as free."""

    graph = adjacency(mask, order)
    matrix = [[0] * 8 for _ in range(8)]
    for roots in itertools.permutations(range(order), 2):
        if not graph[roots[0]] & (1 << roots[1]):
            continue
        available = tuple(vertex for vertex in range(order)
                          if vertex not in roots)
        flags = []
        for free4 in itertools.combinations(available, 4):
            mates = [
                vertex for vertex in free4
                if graph[roots[0]] & (1 << vertex)
                and graph[roots[1]] & (1 << vertex)
            ]
            if len(mates) != 1:
                continue
            chosen = roots + tuple(free4)
            small = induced(mask, order, chosen)
            key = canonical(small, 6, (0, 1))
            if key in edge_flag_index:
                flags.append((free4, edge_flag_index[key]))
        for left, left_kind in flags:
            for right, right_kind in flags:
                if len(set(roots) | set(left) | set(right)) == order:
                    matrix[left_kind][right_kind] += 1
    return matrix


def upper_entries(matrix):
    return [
        [left, right, int(matrix[left][right])]
        for left in range(len(matrix))
        for right in range(left, len(matrix))
        if matrix[left][right]
    ]


def add_weighted(total, matrix, weight):
    for left in range(len(total)):
        for right in range(len(total)):
            total[left][right] += Fraction(weight) * matrix[left][right]


def determinant(matrix):
    if len(matrix) == 1:
        return Fraction(matrix[0][0])
    answer = Fraction()
    for column, value in enumerate(matrix[0]):
        minor = [row[:column] + row[column + 1:] for row in matrix[1:]]
        answer += (-1) ** column * Fraction(value) * determinant(minor)
    return answer


def show(value):
    value = Fraction(value)
    return int(value) if value.denominator == 1 else str(value)


def matrix_show(matrix):
    return [[show(value) for value in row] for row in matrix]


def main() -> None:
    deck = json.loads(DECK.read_text(encoding="utf-8"))
    wave163 = json.loads(WAVE163.read_text(encoding="utf-8"))
    wave147 = json.loads(WAVE147.read_text(encoding="utf-8"))
    projection = deck["T0_all_G_targeted_order9_projection"]
    visible = tuple(map(int, projection["visible_19_H9_masks"]))
    visible_set = set(visible)
    q19 = tuple(map(Fraction, projection["wave163_visible_19_candidate_counts"]))
    assert len(visible) == len(q19) == 19
    assert all(value >= 0 and value.denominator == 1 for value in q19)

    # Consume, but do not regenerate, all frozen H7/H8 counts.
    x7 = {int(mask): int(count) for mask, count in
          wave163["integral_pseudocount"]["order7_mask_count_pairs"]}
    x8 = {int(mask): int(count) for mask, count in
          wave163["integral_pseudocount"]["order8_mask_count_pairs"]}
    frozen8 = tuple(map(int,
        wave147["class_streams"]["8"]["canonical_masks"]
    ))
    assert len(x7) == 208 and len(x8) == len(frozen8) == 916
    assert set(x8) == set(frozen8)

    # Derive the order-six vector by the exact 6->7 deletion identity.
    x6_numerators = defaultdict(int)
    for mask7, count in x7.items():
        for removed in range(7):
            shadow = canonical(delete(mask7, 7, removed), 6)
            x6_numerators[shadow] += count
    x6 = {
        mask: Fraction(numerator, 93)
        for mask, numerator in x6_numerators.items()
    }
    assert len(x6) == 62
    assert all(value.denominator == 1 and value >= 0 for value in x6.values())
    assert sum(x6.values()) == 1120529256

    natural_masks = flag_masks()
    edge_masks = edge_rooted_flag_masks(natural_masks)
    assert len(set(edge_masks)) == 8
    edge_flag_index = {mask: index for index, mask in enumerate(edge_masks)}
    visible_derived_flags = extract_triangle_rooted_flags(visible)
    assert len(visible_derived_flags) == 74
    assert set(natural_masks) <= set(visible_derived_flags)

    # Complete diagonal closure test on all 74 visible-derived flags.
    diagonal_rows = []
    closed_diagonal = []
    for flag in visible_derived_flags:
        labelled, support = completion_support(flag, flag)
        outside = sorted(set(support) - visible_set)
        closed = not outside
        if closed:
            closed_diagonal.append(flag)
        diagonal_rows.append({
            "triangle_rooted_flag_mask": flag,
            "locally_admissible_labelled_completions": labelled,
            "canonical_completion_support_size": len(support),
            "closed_on_visible_19": closed,
            "visible_support": sorted(set(support) & visible_set) if closed else None,
            "first_outside_visible_mask": outside[0] if outside else None,
        })
    expected_closed = {
        natural_masks[4], natural_masks[5], natural_masks[6], natural_masks[7]
    }
    assert set(closed_diagonal) == expected_closed

    # Pair closure between the only four flags with a closed diagonal.
    special_indices = (4, 5, 6, 7)
    closure_edges = []
    closed_pairs = set()
    for left_position, left in enumerate(special_indices):
        for right in special_indices[left_position:]:
            labelled, support = completion_support(
                natural_masks[left], natural_masks[right]
            )
            outside = sorted(set(support) - visible_set)
            closed = not outside
            if closed:
                closed_pairs.add((left, right))
            closure_edges.append({
                "left_flag": FLAG_NAMES[left],
                "right_flag": FLAG_NAMES[right],
                "locally_admissible_labelled_completions": labelled,
                "canonical_support_size": len(support),
                "visible_support_size": len(set(support) & visible_set),
                "outside_visible_support": outside,
                "closed_on_visible_19": closed,
            })
    maximal_closed_blocks = []
    for subset_bits in range(1, 1 << len(special_indices)):
        subset = [special_indices[index] for index in range(4)
                  if subset_bits & (1 << index)]
        if not all((min(left, right), max(left, right)) in closed_pairs
                   for left in subset for right in subset):
            continue
        if any(
            set(subset) < set(larger)
            for larger_bits in range(1, 1 << len(special_indices))
            for larger in [[special_indices[index] for index in range(4)
                            if larger_bits & (1 << index)]]
            if all((min(left, right), max(left, right)) in closed_pairs
                   for left in larger for right in larger)
        ):
            continue
        maximal_closed_blocks.append(tuple(subset))
    maximal_closed_blocks = sorted(set(maximal_closed_blocks))
    assert maximal_closed_blocks == [(4, 7), (5, 7), (6, 7)]

    # Exact coefficient matrices on orders 6,7,8 and the 19 visible H9 masks.
    coefficient_records = {}
    totals_by_order = {}
    total8 = [[Fraction() for _ in range(8)] for _ in range(8)]
    count_vectors = {
        6: x6,
        7: x7,
        8: x8,
        9: {mask: q19[index] for index, mask in enumerate(visible)},
    }
    two_root_equal_checks = 0
    for order, counts in count_vectors.items():
        records = []
        subtotal = [[Fraction() for _ in range(8)] for _ in range(8)]
        for mask, count in sorted(counts.items()):
            triangle_matrix = moment_coeff_triangle(mask, order)
            edge_matrix = moment_coeff_edge(mask, order, edge_flag_index)
            assert triangle_matrix == edge_matrix
            two_root_equal_checks += 1
            if any(any(row) for row in triangle_matrix):
                records.append({
                    "canonical_mask": mask,
                    "count_at_wave163_visible19_point": show(count),
                    "upper_entries": upper_entries(triangle_matrix),
                })
            add_weighted(subtotal, triangle_matrix, count)
            add_weighted(total8, triangle_matrix, count)
        coefficient_records[str(order)] = records
        totals_by_order[str(order)] = matrix_show(subtotal)

    expected_total = [
        [173448, 180048, 180048, 180048, 52372, 52372, 52372, 0],
        [180048, 375672, 230868, 230868, 130580, 107622, 107622, 0],
        [180048, 230868, 375672, 230868, 107622, 130580, 107622, 0],
        [180048, 230868, 230868, 375672, 107622, 107622, 130580, 0],
        [52372, 130580, 107622, 107622, 199584, 29352, 29352, 0],
        [52372, 107622, 130580, 107622, 29352, 199584, 29352, 0],
        [52372, 107622, 107622, 130580, 29352, 29352, 199584, 0],
        [0, 0, 0, 0, 0, 0, 0, 0],
    ]
    assert total8 == [[Fraction(value) for value in row]
                      for row in expected_total]

    # S3 isotypic exact PSD certificate for the hostile full eight-type
    # zero-fill control.  This matrix is not claimed closed on the 19.
    a = total8[0][0]
    b1 = total8[0][1]
    b2 = total8[0][4]
    d1, o1 = total8[1][1], total8[1][2]
    d2, o2 = total8[4][4], total8[4][5]
    same, different = total8[1][4], total8[1][5]
    trivial = [
        [a, 3 * b1, 3 * b2],
        [3 * b1, 3 * (d1 + 2 * o1), 3 * (same + 2 * different)],
        [3 * b2, 3 * (same + 2 * different), 3 * (d2 + 2 * o2)],
    ]
    standard = [
        [d1 - o1, same - different],
        [same - different, d2 - o2],
    ]
    trivial_leading = [
        trivial[0][0],
        determinant([row[:2] for row in trivial[:2]]),
        determinant(trivial),
    ]
    standard_leading = [standard[0][0], determinant(standard)]
    assert all(value > 0 for value in trivial_leading + standard_leading)

    # The three exact closed principal blocks are identical rank-one matrices.
    exact_blocks = []
    for x_index, p_index in maximal_closed_blocks:
        principal = [
            [total8[x_index][x_index], total8[x_index][p_index]],
            [total8[p_index][x_index], total8[p_index][p_index]],
        ]
        assert principal == [[Fraction(199584), Fraction()],
                             [Fraction(), Fraction()]]
        exact_blocks.append({
            "flags": [FLAG_NAMES[x_index], FLAG_NAMES[p_index]],
            "matrix": matrix_show(principal),
            "leading_entry": show(principal[0][0]),
            "determinant": show(determinant(principal)),
            "rank": 1,
            "PSD": True,
        })

    # Per-union-order contribution for a representative X/P block.
    representative = (6, 7)
    block_strata = {}
    for order, matrix in totals_by_order.items():
        block_strata[order] = [
            [matrix[representative[0]][representative[0]],
             matrix[representative[0]][representative[1]]],
            [matrix[representative[1]][representative[0]],
             matrix[representative[1]][representative[1]]],
        ]
    assert block_strata == {
        "6": [[16632, 0], [0, 0]],
        "7": [[0, 0], [0, 0]],
        "8": [[0, 0], [0, 0]],
        "9": [[182952, 0], [0, 0]],
    }

    # Consume the 21 exact rows and nonnegativity at the same witness.
    closed_rows = [
        row for row in projection["rows"]["ordered_pair"]
        if row["closed_on_visible_19"]
    ]
    assert len(closed_rows) == 21
    for row in closed_rows:
        rhs = sum(q19[int(index)] * int(coefficient)
                  for index, coefficient in row["visible_19_H9_coefficients"])
        assert rhs == int(row["wave163_lhs"])
    forced_zero = set(map(int,
        projection["forced_zero_visible_19_indices_at_wave163"]
    ))
    all_g = set(map(int, projection["all_G_indices_in_visible_19"]))
    assert set(range(19)) - all_g <= forced_zero

    result = {
        "status": "exact-rooted-flag-gram-control-passes",
        "scope": {
            "visible_order9_columns": 19,
            "ambient_order9_census_generated": False,
            "frozen_order8_classes_regenerated": False,
            "submission_txt_written": False,
        },
        "inputs": {
            str(path): {"sha256": sha256(path)}
            for path in (DECK, WAVE163, WAVE147)
        },
        "count_vectors": {
            "derived_order6_mask_count_pairs": [
                [mask, show(count)] for mask, count in sorted(x6.items())
            ],
            "order6_sum": show(sum(x6.values())),
            "order7_classes_consumed": len(x7),
            "order8_classes_consumed": len(x8),
            "visible_order9_masks": list(visible),
            "visible_order9_candidate_counts": [show(value) for value in q19],
        },
        "flag_family": {
            "names": list(FLAG_NAMES),
            "semantics": {
                "R0": "zero-edge cross matching",
                "R1_j": "one-edge matching incident with target root j",
                "X_j": "two-edge matching with target root j unmatched",
                "P": "three-edge perfect matching (triangular prism)",
            },
            "triangle_rooted_order6_masks": list(natural_masks),
            "edge_rooted_order6_masks_with_unique_mate_free": list(edge_masks),
            "two_root_three_root_coefficient_matrices_equal": True,
            "coefficientwise_equal_class_checks": two_root_equal_checks,
            "visible_derived_triangle_rooted_order6_flags": len(
                visible_derived_flags
            ),
        },
        "complete_visible_support_closure_test": {
            "all_74_diagonal_products_checked": True,
            "closed_diagonal_flag_masks": sorted(closed_diagonal),
            "closed_diagonal_flag_names": [
                FLAG_NAMES[index] for index in special_indices
            ],
            "diagonal_rows": diagonal_rows,
            "pair_closure_rows": closure_edges,
            "maximal_closed_principal_blocks": [
                [FLAG_NAMES[index] for index in block]
                for block in maximal_closed_blocks
            ],
            "largest_closed_block_size": 2,
            "outside_masks_needed_by_each_Xj_Xk_cross_entry": 9,
        },
        "coefficient_matrices": {
            "convention": (
                "Raw integral Gram: sum over ordered root embeddings of "
                "z(root) z(root)^T.  A coefficient at union order s counts "
                "ordered flag pairs whose vertex union is the whole H_s."
            ),
            "nonzero_class_records_by_union_order": coefficient_records,
            "weighted_matrix_by_union_order": totals_by_order,
        },
        "exact_closed_PSD_blocks": {
            "blocks": exact_blocks,
            "representative_X2_P_union_order_strata": block_strata,
            "all_pass": True,
            "negative_direction_found": False,
        },
        "hostile_full_eight_type_zero_fill_control": {
            "meaning": (
                "Set every non-visible H9 coefficient to zero even in the "
                "three X_j-X_k cross entries which are not closed.  This is "
                "stronger than the licensed 19-column principal-block test "
                "and is recorded only as a counter-control."
            ),
            "matrix": matrix_show(total8),
            "S3_trivial_congruence_block": matrix_show(trivial),
            "S3_standard_block_multiplicity_two": matrix_show(standard),
            "trivial_block_leading_principal_minors": [
                show(value) for value in trivial_leading
            ],
            "standard_block_leading_principal_minors": [
                show(value) for value in standard_leading
            ],
            "rank": 7,
            "PSD": True,
        },
        "closed_rows_and_nonnegativity": {
            "closed_rows_checked": len(closed_rows),
            "all_closed_rows_hold": True,
            "all_19_counts_nonnegative_integral": True,
            "all_ten_non_all_G_visible_columns_forced_zero": True,
        },
        "exact_boundary": {
            "wave163_visible_H9_extension_passes_every_licensed_PSD": True,
            "separating_negative_direction": None,
            "minimal_counter_control": (
                "The complete 8-type zero-fill matrix is already PSD of rank "
                "7.  Within all 74 visible-derived triangle-rooted order-six "
                "flags, the largest principal blocks whose order-nine support "
                "is contained in the 19 masks have size two and are the three "
                "isomorphic {X_j,P} blocks."
            ),
            "first_missing_data": [
                "At the same union order 9, any block containing two distinct "
                "X_j needs 9 additional locally admissible H9 masks outside "
                "the visible 19.",
                "If H9 support must remain fixed to the 19, a generic two-root "
                "order-six flag without the shared unique mate first has a "
                "diagonal of union order 10.",
                "For triangle-rooted square Grams, increasing from three to "
                "four free vertices raises the next diagonal union order to "
                "11; this is also the first order at which one doubled D "
                "source can be displayed explicitly.",
            ],
        },
    }
    atomic_json(OUTPUT, result)
    print(json.dumps({
        "output": str(OUTPUT),
        "visible_derived_flags": len(visible_derived_flags),
        "closed_diagonal_flags": [FLAG_NAMES[index]
                                  for index in special_indices],
        "maximal_closed_blocks": result[
            "complete_visible_support_closure_test"
        ]["maximal_closed_principal_blocks"],
        "exact_block": exact_blocks[0]["matrix"],
        "full_control_rank": 7,
        "closed_rows": len(closed_rows),
        "negative_direction": None,
    }, indent=2))


if __name__ == "__main__":
    main()
