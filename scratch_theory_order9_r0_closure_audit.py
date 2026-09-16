"""Independent replay of the seven-mask R0 closure certificate.

This module imports no producer.  It reconstructs graph canonicalization,
all 63 new deletion slots, five-flag coefficients, glue supports, and every
touched local H8-to-H9 row directly from the frozen masks.
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


CERTIFICATE = Path("scratch_theory_order9_r0_closure.json")
PRIOR = Path("scratch_theory_order9_cross_x_closure.json")
DECK = Path("scratch_theory_minimal_order9_targeted_deck.json")
OLD_GRAM = Path("scratch_theory_order9_rooted_flag_gram.json")
WAVE147 = Path(
    "external_conway99_research/attempts/wave147-alternative-lane/"
    "exact-results.json"
)
WAVE163 = Path("scratch_theory_wave163_integral_order8_boundary.json")
OUTPUT = Path("scratch_theory_order9_r0_closure_audit.json")


def sha(path: Path) -> str:
    state = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            state.update(chunk)
    return state.hexdigest()


def emit(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


@lru_cache(maxsize=None)
def edges(n: int):
    return tuple(itertools.combinations(range(n), 2))


@lru_cache(maxsize=None)
def bit_of(n: int):
    return {edge: bit for bit, edge in enumerate(edges(n))}


def graph_rows(mask: int, n: int):
    rows = [0] * n
    for bit, (left, right) in enumerate(edges(n)):
        if mask >> bit & 1:
            rows[left] |= 1 << right
            rows[right] |= 1 << left
    return tuple(rows)


def relabel(mask: int, n: int, permutation):
    answer = 0
    target = bit_of(n)
    for bit, (left, right) in enumerate(edges(n)):
        if mask >> bit & 1:
            image = tuple(sorted((permutation[left], permutation[right])))
            answer |= 1 << target[image]
    return answer


@lru_cache(maxsize=None)
def canonical(mask: int, n: int, roots=()):
    graph = graph_rows(mask, n)
    root_set = set(roots)
    cells = defaultdict(list)
    for vertex in range(n):
        if vertex not in root_set:
            signature = (graph[vertex].bit_count(),) + tuple(
                int(bool(graph[vertex] & (1 << root))) for root in roots
            )
            cells[signature].append(vertex)
    signatures = sorted(cells)
    choices = []
    start = len(roots)
    for signature in signatures:
        size = len(cells[signature])
        choices.append(tuple(itertools.permutations(range(start, start + size))))
        start += size
    best = None
    for selected in itertools.product(*choices):
        permutation = [0] * n
        for target, root in enumerate(roots):
            permutation[root] = target
        for signature, targets in zip(signatures, selected):
            for source, target in zip(cells[signature], targets):
                permutation[source] = target
        image = relabel(mask, n, tuple(permutation))
        best = image if best is None else min(best, image)
    assert best is not None
    return best


def delete_vertex(mask: int, n: int, removed: int):
    kept = tuple(v for v in range(n) if v != removed)
    mapping = {old: new for new, old in enumerate(kept)}
    old_bits = bit_of(n)
    answer = 0
    for bit, edge in enumerate(itertools.combinations(kept, 2)):
        if mask >> old_bits[edge] & 1:
            answer |= 1 << bit
    return answer, mapping


def extend_vertex(mask8: int, neighborhood):
    target = bit_of(9)
    answer = 0
    for bit, edge in enumerate(edges(8)):
        if mask8 >> bit & 1:
            answer |= 1 << target[edge]
    for vertex in neighborhood:
        answer |= 1 << target[(vertex, 8)]
    return answer


def locally_upper(mask: int, n: int):
    graph = graph_rows(mask, n)
    if max(row.bit_count() for row in graph) > 14:
        return False
    return all((graph[a] & graph[b]).bit_count()
               <= (1 if graph[a] & (1 << b) else 2)
               for a, b in edges(n))


def flag_kind(graph, roots, free):
    if not all(graph[a] & (1 << b)
               for a, b in itertools.combinations(free, 2)):
        return None
    root_degree = [sum(bool(graph[root] & (1 << vertex)) for vertex in free)
                   for root in roots]
    free_degree = [sum(bool(graph[vertex] & (1 << root)) for root in roots)
                   for vertex in free]
    size = sum(root_degree)
    if size == 0:
        return 0
    if size == 2 and sorted(root_degree) == sorted(free_degree) == [0, 1, 1]:
        return 1 + root_degree.index(0)
    if root_degree == free_degree == [1, 1, 1]:
        return 4
    return None


def five_coefficient_matrix(mask: int):
    graph = graph_rows(mask, 9)
    result = [[0] * 5 for _ in range(5)]
    for roots in itertools.permutations(range(9), 3):
        if not all(graph[a] & (1 << b)
                   for a, b in itertools.combinations(roots, 2)):
            continue
        remaining = tuple(v for v in range(9) if v not in roots)
        flags = []
        for free in itertools.combinations(remaining, 3):
            kind = flag_kind(graph, roots, free)
            if kind is not None:
                flags.append((set(free), kind))
        for left, i in flags:
            for right, j in flags:
                if len(set(roots) | left | right) == 9:
                    result[i][j] += 1
    return result


def natural_flags():
    answer = []
    base_edges = set(edges(3)) | set(itertools.combinations(range(3, 6), 2))
    for kind in range(8):
        chosen = set(base_edges)
        if 1 <= kind <= 3:
            chosen.add((kind - 1, 3))
        elif 4 <= kind <= 6:
            omitted = kind - 4
            kept = [root for root in range(3) if root != omitted]
            chosen.update(((kept[0], 4), (kept[1], 5)))
        elif kind == 7:
            chosen.update(((0, 3), (1, 4), (2, 5)))
        mask = sum(1 << bit_of(6)[tuple(sorted(edge))] for edge in chosen)
        answer.append(canonical(mask, 6, (0, 1, 2)))
    return tuple(answer)


def glued(left: int, right: int, cross_bits: int):
    chosen = set()
    for bit, (a, b) in enumerate(edges(6)):
        if left >> bit & 1:
            chosen.add((a, b))
        if right >> bit & 1:
            chosen.add(tuple(sorted((a if a < 3 else a + 3,
                                     b if b < 3 else b + 3))))
    slots = tuple(itertools.product(range(3, 6), range(6, 9)))
    for bit, edge in enumerate(slots):
        if cross_bits >> bit & 1:
            chosen.add(edge)
    return sum(1 << bit_of(9)[edge] for edge in chosen)


def glue_support(left: int, right: int):
    support = set()
    for cross in range(512):
        mask = glued(left, right, cross)
        if locally_upper(mask, 9):
            support.add(canonical(mask, 9))
    return support


def matrix_rank(matrix):
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


def main() -> None:
    certificate = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    prior = json.loads(PRIOR.read_text(encoding="utf-8"))
    deck = json.loads(DECK.read_text(encoding="utf-8"))
    old_gram = json.loads(OLD_GRAM.read_text(encoding="utf-8"))
    frozen = json.loads(WAVE147.read_text(encoding="utf-8"))
    wave163 = json.loads(WAVE163.read_text(encoding="utf-8"))
    for path in (PRIOR, DECK, OLD_GRAM, WAVE147, WAVE163):
        assert certificate["inputs"][str(path)]["sha256"] == sha(path)

    projection = deck["T0_all_G_targeted_order9_projection"]
    visible = tuple(map(int, projection["visible_19_H9_masks"]))
    fixed19 = tuple(map(int, projection["wave163_visible_19_candidate_counts"]))
    old9 = tuple(map(int, prior["added_nine_masks"]))
    new7 = tuple(map(int, certificate["added_seven_masks"]))
    masks28 = visible + old9
    masks35 = masks28 + new7
    assert len(set(masks35)) == 35 and len(new7) == 7
    frozen8 = tuple(map(int, frozen["class_streams"]["8"]["canonical_masks"]))
    frozen8_set = set(frozen8)
    x8 = {int(mask): int(value) for mask, value in
          wave163["integral_pseudocount"]["order8_mask_count_pairs"]}
    assert len(frozen8_set) == len(x8) == 916 and set(x8) == frozen8_set

    # All 63 deletion slots, without consuming the producer deck.
    histograms = {}
    shadow_union = set()
    zero_shadow_masks = defaultdict(set)
    slots = 0
    for mask in new7:
        assert canonical(mask, 9) == mask and locally_upper(mask, 9)
        histogram = Counter()
        for removed in range(9):
            raw, _ = delete_vertex(mask, 9, removed)
            shadow = canonical(raw, 8)
            assert shadow in frozen8_set
            if x8[shadow] == 0:
                zero_shadow_masks[mask].add(shadow)
            histogram[shadow] += 1
            shadow_union.add(shadow)
            slots += 1
        histograms[mask] = sorted(histogram.items())
    emitted_decks = certificate["added_seven_deletion_decks"]["decks"]
    assert {int(row["canonical_order9_mask"]): [tuple(pair) for pair in
            row["deletion_histogram"]] for row in emitted_decks} == histograms
    assert slots == 63 and len(shadow_union) == 16
    assert {mask: sorted(values) for mask, values in zero_shadow_masks.items()} == {
        13610256401: [58163201, 58167297],
        14889779459: [58163201],
    }
    assert certificate["added_seven_deletion_decks"][
        "zero_Wave163_order8_shadows"
    ] == [58163201, 58167297]

    # Direct five-flag glue closure.
    flags = natural_flags()
    universe28, universe35 = set(masks28), set(masks35)
    outside_union = set()
    for partner in (0, 4, 5, 6, 7):
        support = glue_support(flags[0], flags[partner])
        outside_union.update(support - universe28)
        assert support <= universe35
    assert outside_union == set(new7)

    # Recompute all 35 coefficient matrices and exact endpoint Gram.
    matrices = [five_coefficient_matrix(mask) for mask in masks35]
    records = certificate["closed_five_flag_Gram"][
        "coefficient_records_on_35_columns"
    ]
    for index, (matrix, record) in enumerate(zip(matrices, records)):
        rebuilt = [[0] * 5 for _ in range(5)]
        for left, right, value in record["upper_entries"]:
            rebuilt[int(left)][int(right)] = int(value)
            rebuilt[int(right)][int(left)] = int(value)
        assert int(record["canonical_order9_mask"]) == masks35[index]
        assert rebuilt == matrix

    selected = (0, 4, 5, 6, 7)
    archived8 = old_gram["hostile_full_eight_type_zero_fill_control"]["matrix"]
    fixed_base = [[int(archived8[i][j]) for j in selected] for i in selected]
    endpoint_vector = (32, 12, 12, 12, 0)
    endpoint = [[1386 * endpoint_vector[i] * endpoint_vector[j]
                 for j in range(5)] for i in range(5)]
    assert endpoint == certificate["closed_five_flag_Gram"]["exact_T0_matrix"]
    assert matrix_rank(endpoint) == 1
    assert 1386 * sum(value * value for value in endpoint_vector) == 2018016
    for vector in ((3, -8, 0, 0, 0), (0, 1, -1, 0, 0),
                   (0, 1, 0, -1, 0), (0, 0, 0, 0, 1)):
        assert all(sum(endpoint[i][j] * vector[j] for j in range(5)) == 0
                   for i in range(5))

    witness = list(map(int, certificate[
        "exact_integer_T0_projection_witness"
    ]["counts_old9_then_new7"]))
    assert witness == [0, 0, 25986, 36192, 0, 6792, 10224, 0, 5922,
                       0, 26186, 0, 0, 141356, 0, 103818]
    evaluated = [row[:] for row in fixed_base]
    for count, matrix in zip(witness, matrices[19:]):
        for i in range(5):
            for j in range(5):
                evaluated[i][j] += count * matrix[i][j]
    assert evaluated == endpoint
    # R0-P is a sum of nonnegative H9 contributions.
    assert matrices[19 + 9 + 2][0][4] == 6
    assert matrices[19 + 9 + 3][0][4] == 12
    assert witness[11] == witness[12] == 0

    # Rebuild every touched local extension row.
    unmarked = defaultdict(lambda: [0] * 35)
    one_root = defaultdict(lambda: [0] * 35)
    two_root = defaultdict(lambda: [0] * 35)
    for column, mask in enumerate(masks35):
        graph = graph_rows(mask, 9)
        for removed in range(9):
            raw, mapping = delete_vertex(mask, 9, removed)
            shadow = canonical(raw, 8)
            unmarked[shadow][column] += 1
            incident = tuple(v for v in range(9) if v != removed
                             and graph[removed] & (1 << v))
            for root in incident:
                key = canonical(raw, 8, (mapping[root],))
                one_root[(shadow, key)][column] += 1
            for left in incident:
                for right in incident:
                    if left != right:
                        key = canonical(raw, 8,
                                        (mapping[left], mapping[right]))
                        two_root[(shadow, key)][column] += 1

    universe19 = set(visible)
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
                candidate = extend_vertex(shadow, neighborhood)
                if locally_upper(candidate, 9):
                    image = canonical(candidate, 9)
                    support.add(image)
                    if image not in universe35 and first_outside is None:
                        first_outside = image
        support_cache[cache_key] = support, first_outside
        return support, first_outside

    fixed = list(fixed19) + [0] * 16
    reconstructed = {"unmarked": {}, "vertex": {}, "ordered_pair": {}}

    def make_row(vector, shadow, required, lhs):
        support, outside = local_support(shadow, required)
        fixed_rhs = sum(value * count for value, count in zip(vector, fixed))
        return {
            "variable": vector[19:],
            "fixed_rhs": fixed_rhs,
            "residual": lhs - fixed_rhs,
            "closed19": support <= universe19,
            "closed28": support <= universe28,
            "closed35": outside is None,
            "support_size": len(support),
            "outside": outside,
        }

    for shadow, vector in unmarked.items():
        reconstructed["unmarked"][(shadow,)] = make_row(
            vector, shadow, (), 91 * x8[shadow]
        )
    for (shadow, key), vector in one_root.items():
        graph = graph_rows(shadow, 8)
        orbit = tuple(root for root in range(8)
                      if canonical(shadow, 8, (root,)) == key)
        degree = graph[orbit[0]].bit_count()
        reconstructed["vertex"][(shadow, key)] = make_row(
            vector, shadow, (orbit[0],),
            len(orbit) * (14 - degree) * x8[shadow]
        )
    for (shadow, key), vector in two_root.items():
        graph = graph_rows(shadow, 8)
        orbit = tuple((a, b) for a in range(8) for b in range(8) if a != b
                      and canonical(shadow, 8, (a, b)) == key)
        a, b = orbit[0]
        adjacent = bool(graph[a] & (1 << b))
        current = (graph[a] & graph[b]).bit_count()
        capacity = (1 if adjacent else 2) - current
        reconstructed["ordered_pair"][(shadow, key)] = make_row(
            vector, shadow, tuple(sorted((a, b))),
            len(orbit) * capacity * x8[shadow]
        )

    emitted_rows = certificate["targeted_extension_rows"]["rows"]
    for family, rows in reconstructed.items():
        indexed = {}
        for row in emitted_rows[family]:
            if family == "unmarked":
                key = (int(row["canonical_order8_mask"]),)
            elif family == "vertex":
                key = (int(row["canonical_order8_mask"]), int(row["rooted_key"]))
            else:
                key = (int(row["canonical_order8_mask"]),
                       int(row["ordered_pair_rooted_key"]))
            indexed[key] = row
        assert set(indexed) == set(rows)
        for key, actual in rows.items():
            emitted = indexed[key]
            variable = [0] * 16
            for coordinate, value in emitted["variable16_coefficients"]:
                variable[int(coordinate)] = int(value)
            assert variable == actual["variable"]
            assert int(emitted["fixed19_rhs"]) == actual["fixed_rhs"]
            assert int(emitted["residual_capacity"]) == actual["residual"]
            assert emitted["closed_on_19"] == actual["closed19"]
            assert emitted["closed_on_28"] == actual["closed28"]
            assert emitted["closed_on_35"] == actual["closed35"]
            assert int(emitted["support_size"]) == actual["support_size"]
            assert emitted["first_outside_35_mask"] == actual["outside"]

    row_counts = {family: len(rows) for family, rows in reconstructed.items()}
    closed_counts = {family: sum(row["closed35"] for row in rows.values())
                     for family, rows in reconstructed.items()}
    new_counts = {family: sum(row["closed35"] and not row["closed28"]
                              for row in rows.values())
                  for family, rows in reconstructed.items()}
    assert row_counts == {"unmarked": 56, "vertex": 192, "ordered_pair": 561}
    assert closed_counts == {"unmarked": 0, "vertex": 0, "ordered_pair": 34}
    assert new_counts == {"unmarked": 0, "vertex": 0, "ordered_pair": 3}

    closed_equations = sorted({(tuple(row["variable"]), row["residual"])
                               for rows in reconstructed.values()
                               for row in rows.values() if row["closed35"]})
    gram_equations = [(tuple(row["coefficients_on_old9_new7"]), int(row["rhs"]))
                      for row in certificate["closed_five_flag_Gram"]
                      ["equations_on_old9_new7"]]
    assert matrix_rank([list(vector) for vector, _ in closed_equations]) == 7
    assert matrix_rank([list(vector) for vector, _ in gram_equations]) == 4
    assert matrix_rank([list(vector) for vector, _ in closed_equations]
                       + [list(vector) for vector, _ in gram_equations]) == 9

    minimum_slack = None
    for rows in reconstructed.values():
        for row in rows.values():
            value = sum(a * b for a, b in zip(row["variable"], witness))
            if row["closed35"]:
                assert value == row["residual"]
            else:
                assert value <= row["residual"]
                slack = row["residual"] - value
                minimum_slack = slack if minimum_slack is None else min(
                    minimum_slack, slack
                )
    assert minimum_slack == certificate[
        "exact_integer_T0_projection_witness"
    ]["minimum_open_extension_slack"]

    # Independent 74-diagonal scan for the claim boundary.
    previous_flags = tuple(int(row["triangle_rooted_flag_mask"])
                           for row in old_gram[
                               "complete_visible_support_closure_test"
                           ]["diagonal_rows"])
    assert len(previous_flags) == len(set(previous_flags)) == 74
    diagonal_outside = {flag: sorted(glue_support(flag, flag) - universe35)
                        for flag in previous_flags}
    closed_diagonal = sorted(flag for flag, outside in diagonal_outside.items()
                             if not outside)
    assert closed_diagonal == sorted(flags[index] for index in (0, 4, 5, 6, 7))
    minimum_missing = min(len(outside) for outside in diagonal_outside.values()
                          if outside)
    minimizers = sorted(flag for flag, outside in diagonal_outside.items()
                        if len(outside) == minimum_missing)
    assert minimum_missing == 2
    assert minimizers == [24699, 24939, 25147, 25507, 27179, 27299]
    assert all(diagonal_outside[flag] == [46817920192, 56196485312]
               for flag in minimizers)
    assert certificate["next_boundary"]["remaining_natural_R1_mask_count"] == 14

    result = {
        "status": "independent-35-column-R0-audit-passed",
        "producer_imported": False,
        "certificate_sha256": sha(CERTIFICATE),
        "input_hashes_match": True,
        "added_masks_checked": len(new7),
        "added_vertex_deletions_checked": slots,
        "distinct_frozen_H8_shadows": len(shadow_union),
        "zero_Wave163_H8_shadows": [58163201, 58167297],
        "new7_masks_forced_zero_by_zero_shadows": [13610256401, 14889779459],
        "R0_product_glue_scans": 5,
        "raw_five_flag_H9_matrices_checked": len(matrices),
        "extension_row_counts": row_counts,
        "closed_on_35_counts": closed_counts,
        "newly_closed_beyond_28_counts": new_counts,
        "closed_rank": 7,
        "Gram_rank": 4,
        "combined_rank": 9,
        "integer_witness_replayed_on_every_row": True,
        "forced_zero_new7_indices": [2, 3],
        "visible_derived_diagonals_checked": 74,
        "closed_five_flag_Gram_rank": 1,
        "closed_five_flag_Gram_PSD": True,
        "negative_direction_found": False,
        "submission_txt_written": False,
    }
    emit(OUTPUT, result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
