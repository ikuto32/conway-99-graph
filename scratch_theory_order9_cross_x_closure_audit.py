"""Producer-independent audit of the targeted 28-column X-cross closure.

No producer module is imported.  Canonicalization, all 81 extra deletion
slots, raw flag coefficients, glue supports, and every touched H8->H9 local
extension row are reconstructed directly from masks.
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


CERTIFICATE = Path("scratch_theory_order9_cross_x_closure.json")
DECK = Path("scratch_theory_minimal_order9_targeted_deck.json")
OLD_GRAM = Path("scratch_theory_order9_rooted_flag_gram.json")
WAVE147 = Path(
    "external_conway99_research/attempts/wave147-alternative-lane/"
    "exact-results.json"
)
WAVE163 = Path("scratch_theory_wave163_integral_order8_boundary.json")
OUTPUT = Path("scratch_theory_order9_cross_x_closure_audit.json")


def digest(path: Path) -> str:
    state = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 16), b""):
            state.update(chunk)
    return state.hexdigest()


def save(path: Path, payload: object) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


@lru_cache(maxsize=None)
def pairs(n: int):
    return tuple((a, b) for a in range(n) for b in range(a + 1, n))


@lru_cache(maxsize=None)
def pair_to_bit(n: int):
    return {edge: bit for bit, edge in enumerate(pairs(n))}


def neighbors(mask: int, n: int):
    rows = [0] * n
    for bit, (a, b) in enumerate(pairs(n)):
        if mask >> bit & 1:
            rows[a] |= 1 << b
            rows[b] |= 1 << a
    return tuple(rows)


def permuted(mask: int, n: int, image):
    result = 0
    target = pair_to_bit(n)
    for bit, (a, b) in enumerate(pairs(n)):
        if mask >> bit & 1:
            edge = tuple(sorted((image[a], image[b])))
            result |= 1 << target[edge]
    return result


@lru_cache(maxsize=None)
def rooted_canonical(mask: int, n: int, roots=()):
    graph = neighbors(mask, n)
    root_set = set(roots)
    cells = defaultdict(list)
    for vertex in range(n):
        if vertex in root_set:
            continue
        signature = (graph[vertex].bit_count(),) + tuple(
            int(bool(graph[vertex] & (1 << root))) for root in roots
        )
        cells[signature].append(vertex)
    signatures = sorted(cells)
    target_cells = []
    offset = len(roots)
    for signature in signatures:
        size = len(cells[signature])
        target_cells.append(tuple(itertools.permutations(
            range(offset, offset + size)
        )))
        offset += size
    best = None
    for selected in itertools.product(*target_cells):
        image = [0] * n
        for target, root in enumerate(roots):
            image[root] = target
        for signature, targets in zip(signatures, selected):
            for source, target in zip(cells[signature], targets):
                image[source] = target
        value = permuted(mask, n, tuple(image))
        best = value if best is None else min(best, value)
    assert best is not None
    return best


def remove_vertex(mask: int, n: int, removed: int):
    kept = tuple(vertex for vertex in range(n) if vertex != removed)
    relabel = {old: new for new, old in enumerate(kept)}
    result = 0
    old = pair_to_bit(n)
    for bit, edge in enumerate(itertools.combinations(kept, 2)):
        if mask >> old[edge] & 1:
            result |= 1 << bit
    return result, relabel


def add_vertex(mask8: int, required):
    result = 0
    target = pair_to_bit(9)
    for bit, edge in enumerate(pairs(8)):
        if mask8 >> bit & 1:
            result |= 1 << target[edge]
    for vertex in required:
        result |= 1 << target[(vertex, 8)]
    return result


def upper_admissible(mask: int, n: int):
    graph = neighbors(mask, n)
    if max(row.bit_count() for row in graph) > 14:
        return False
    for a, b in pairs(n):
        cap = 1 if graph[a] & (1 << b) else 2
        if (graph[a] & graph[b]).bit_count() > cap:
            return False
    return True


def x_or_p_kind(graph, roots, free):
    if not all(graph[a] & (1 << b)
               for a, b in itertools.combinations(free, 2)):
        return None
    rd = [sum(bool(graph[root] & (1 << vertex)) for vertex in free)
          for root in roots]
    fd = [sum(bool(graph[vertex] & (1 << root)) for root in roots)
          for vertex in free]
    if sum(rd) == 2 and sorted(rd) == sorted(fd) == [0, 1, 1]:
        return rd.index(0)
    if rd == fd == [1, 1, 1]:
        return 3
    return None


def coefficient_matrix(mask: int):
    graph = neighbors(mask, 9)
    result = [[0] * 4 for _ in range(4)]
    for roots in itertools.permutations(range(9), 3):
        if not all(graph[a] & (1 << b)
                   for a, b in itertools.combinations(roots, 2)):
            continue
        available = tuple(v for v in range(9) if v not in roots)
        occurrences = []
        for free in itertools.combinations(available, 3):
            kind = x_or_p_kind(graph, roots, free)
            if kind is not None:
                occurrences.append((set(free), kind))
        for left, i in occurrences:
            for right, j in occurrences:
                if len(set(roots) | left | right) == 9:
                    result[i][j] += 1
    return result


def natural_flags():
    result = []
    base = set(pairs(3)) | set(itertools.combinations(range(3, 6), 2))
    for kind in range(8):
        chosen = set(base)
        if 1 <= kind <= 3:
            chosen.add((kind - 1, 3))
        elif 4 <= kind <= 6:
            omitted = kind - 4
            kept = [root for root in range(3) if root != omitted]
            chosen.update(((kept[0], 4), (kept[1], 5)))
        elif kind == 7:
            chosen.update(((0, 3), (1, 4), (2, 5)))
        mask = sum(1 << pair_to_bit(6)[tuple(sorted(edge))]
                   for edge in chosen)
        result.append(rooted_canonical(mask, 6, (0, 1, 2)))
    return tuple(result)


def glued(left: int, right: int, cross: int):
    chosen = set()
    for bit, (a, b) in enumerate(pairs(6)):
        if left >> bit & 1:
            chosen.add((a, b))
        if right >> bit & 1:
            chosen.add(tuple(sorted((a if a < 3 else a + 3,
                                     b if b < 3 else b + 3))))
    slots = tuple(itertools.product(range(3, 6), range(6, 9)))
    for bit, edge in enumerate(slots):
        if cross >> bit & 1:
            chosen.add(edge)
    return sum(1 << pair_to_bit(9)[edge] for edge in chosen)


def glue_support(left: int, right: int):
    result = set()
    for cross in range(512):
        mask = glued(left, right, cross)
        if upper_admissible(mask, 9):
            result.add(rooted_canonical(mask, 9))
    return result


def rank(matrix):
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
    deck = json.loads(DECK.read_text(encoding="utf-8"))
    frozen = json.loads(WAVE147.read_text(encoding="utf-8"))
    wave163 = json.loads(WAVE163.read_text(encoding="utf-8"))
    for path in (DECK, OLD_GRAM, WAVE147, WAVE163):
        assert certificate["inputs"][str(path)]["sha256"] == digest(path)

    projection = deck["T0_all_G_targeted_order9_projection"]
    visible = tuple(map(int, projection["visible_19_H9_masks"]))
    fixed19 = tuple(map(int, projection["wave163_visible_19_candidate_counts"]))
    extras = tuple(map(int, certificate["added_nine_masks"]))
    masks = visible + extras
    assert len(visible) == 19 and len(extras) == 9 and len(set(masks)) == 28
    frozen8 = tuple(map(int, frozen["class_streams"]["8"]["canonical_masks"]))
    frozen8_set = set(frozen8)
    x8 = {int(mask): int(value) for mask, value in
          wave163["integral_pseudocount"]["order8_mask_count_pairs"]}
    assert len(frozen8_set) == len(x8) == 916 and set(x8) == frozen8_set

    # Recompute every added deletion without consuming producer deck rows.
    deck_histograms = {}
    slots = 0
    shadows = set()
    for mask in extras:
        assert rooted_canonical(mask, 9) == mask
        assert upper_admissible(mask, 9)
        histogram = Counter()
        for removed in range(9):
            raw, _ = remove_vertex(mask, 9, removed)
            shadow = rooted_canonical(raw, 8)
            assert shadow in frozen8_set
            assert x8[shadow] > 0
            histogram[shadow] += 1
            shadows.add(shadow)
            slots += 1
        deck_histograms[mask] = sorted(histogram.items())
    emitted_decks = certificate["added_nine_deletion_decks"]["decks"]
    assert {int(row["canonical_order9_mask"]): [tuple(pair) for pair in
            row["deletion_histogram"]] for row in emitted_decks} == deck_histograms
    assert slots == 81 and len(shadows) == 24

    # Independently count all 28 raw Gram coefficients.
    matrices = [coefficient_matrix(mask) for mask in masks]
    emitted_records = certificate["minimal_closed_gram_block"][
        "raw_coefficient_records_on_28_columns"
    ]
    for index, (matrix, record) in enumerate(zip(matrices, emitted_records)):
        reconstructed = [[0] * 4 for _ in range(4)]
        for left, right, value in record["upper_entries"]:
            reconstructed[int(left)][int(right)] = int(value)
            reconstructed[int(right)][int(left)] = int(value)
        assert int(record["canonical_order9_mask"]) == masks[index]
        assert reconstructed == matrix
    cross_weights = [matrix[0][1] for matrix in matrices[19:]]
    assert cross_weights == [2, 6, 2, 2, 6, 2, 2, 6, 2]
    assert all(matrix[0][2] == matrix[1][2] == matrix[0][1]
               for matrix in matrices[19:])
    mass = [value // 2 for value in cross_weights]
    assert mass == [1, 3, 1, 1, 3, 1, 1, 3, 1]
    assert 231 * 6 * 12 * 12 == 199584
    assert 199584 - 29352 == 2 * 85116
    exact = [[199584 if i < 3 and j < 3 else 0
              for j in range(4)] for i in range(4)]
    assert certificate["minimal_closed_gram_block"]["exact_T0_matrix"] == exact
    assert rank(exact) == 1
    for vector in ((1, -1, 0, 0), (1, 0, -1, 0), (0, 0, 0, 1)):
        assert all(sum(exact[i][j] * vector[j] for j in range(4)) == 0
                   for i in range(4))

    # Directly replay distinct-X support closure and the next R enlargement.
    flags = natural_flags()
    universe19, universe28 = set(visible), set(masks)
    for left, right in ((4, 5), (4, 6), (5, 6)):
        support = glue_support(flags[left], flags[right])
        assert support - universe19 == set(extras)
        assert support <= universe28
    missing_by_candidate = []
    for candidate in range(4):
        missing = set()
        for partner in (candidate, 4, 5, 6, 7):
            left, right = sorted((candidate, partner))
            missing.update(glue_support(flags[left], flags[right]) - universe28)
        missing_by_candidate.append(sorted(missing))
    assert list(map(len, missing_by_candidate)) == [7, 17, 17, 17]
    assert missing_by_candidate[0] == certificate[
        "minimal_next_missing_columns"
    ]["required_masks"]
    previous_flags = tuple(int(row["triangle_rooted_flag_mask"])
                           for row in json.loads(
                               OLD_GRAM.read_text(encoding="utf-8")
                           )["complete_visible_support_closure_test"]
                           ["diagonal_rows"])
    assert len(previous_flags) == len(set(previous_flags)) == 74
    diagonal_outside = {
        flag: sorted(glue_support(flag, flag) - universe28)
        for flag in previous_flags
    }
    assert sorted(flag for flag, outside in diagonal_outside.items()
                  if not outside) == sorted(flags[4:])
    minimum_diagonal_missing = min(len(outside) for outside in
                                   diagonal_outside.values() if outside)
    diagonal_minimizers = sorted(flag for flag, outside in
                                 diagonal_outside.items()
                                 if len(outside) == minimum_diagonal_missing)
    assert minimum_diagonal_missing == 2
    assert diagonal_minimizers == [24699, 24939, 25147,
                                   25507, 27179, 27299]
    assert all(diagonal_outside[flag] == [46817920192, 56196485312]
               for flag in diagonal_minimizers)
    emitted_diagonal = certificate["minimal_next_missing_columns"][
        "all_74_visible_derived_diagonal_scan"
    ]
    assert int(emitted_diagonal["flags_checked"]) == 74
    assert emitted_diagonal["minimizing_flag_masks"] == diagonal_minimizers
    assert emitted_diagonal["common_two_missing_masks"] == [
        46817920192, 56196485312
    ]

    # Reconstruct all touched deletion-root rows and all local closure scans.
    unmarked = defaultdict(lambda: [0] * 28)
    one_root = defaultdict(lambda: [0] * 28)
    two_root = defaultdict(lambda: [0] * 28)
    for column, mask in enumerate(masks):
        graph = neighbors(mask, 9)
        for removed in range(9):
            raw, relabel = remove_vertex(mask, 9, removed)
            shadow = rooted_canonical(raw, 8)
            unmarked[shadow][column] += 1
            incident = tuple(vertex for vertex in range(9)
                             if vertex != removed
                             and graph[removed] & (1 << vertex))
            for root in incident:
                key = rooted_canonical(raw, 8, (relabel[root],))
                one_root[(shadow, key)][column] += 1
            for a in incident:
                for b in incident:
                    if a != b:
                        key = rooted_canonical(raw, 8,
                                               (relabel[a], relabel[b]))
                        two_root[(shadow, key)][column] += 1

    cache = {}

    def local_support(shadow, required):
        cache_key = (shadow, tuple(sorted(required)))
        if cache_key in cache:
            return cache[cache_key]
        remaining = tuple(v for v in range(8) if v not in required)
        support = set()
        first_outside = None
        for size in range(len(remaining) + 1):
            for extra in itertools.combinations(remaining, size):
                candidate = add_vertex(shadow, tuple(sorted(required + extra)))
                if upper_admissible(candidate, 9):
                    image = rooted_canonical(candidate, 9)
                    support.add(image)
                    if image not in universe28 and first_outside is None:
                        first_outside = image
        cache[cache_key] = support, first_outside
        return support, first_outside

    reconstructed = {"unmarked": {}, "vertex": {}, "ordered_pair": {}}
    fixed = list(fixed19) + [0] * 9

    def row_data(vector, shadow, required, lhs):
        support, outside = local_support(shadow, required)
        fixed_rhs = sum(value * count for value, count in zip(vector, fixed))
        return {
            "extra": vector[19:],
            "fixed_rhs": fixed_rhs,
            "residual": lhs - fixed_rhs,
            "closed19": support <= universe19,
            "closed28": outside is None,
            "support_size": len(support),
            "outside": outside,
        }

    for shadow, vector in unmarked.items():
        reconstructed["unmarked"][(shadow,)] = row_data(
            vector, shadow, (), 91 * x8[shadow]
        )
    for (shadow, key), vector in one_root.items():
        graph = neighbors(shadow, 8)
        orbit = tuple(root for root in range(8)
                      if rooted_canonical(shadow, 8, (root,)) == key)
        degree = graph[orbit[0]].bit_count()
        lhs = len(orbit) * (14 - degree) * x8[shadow]
        reconstructed["vertex"][(shadow, key)] = row_data(
            vector, shadow, (orbit[0],), lhs
        )
    for (shadow, key), vector in two_root.items():
        graph = neighbors(shadow, 8)
        orbit = tuple((a, b) for a in range(8) for b in range(8) if a != b
                      and rooted_canonical(shadow, 8, (a, b)) == key)
        a, b = orbit[0]
        adjacent = bool(graph[a] & (1 << b))
        current = (graph[a] & graph[b]).bit_count()
        capacity = (1 if adjacent else 2) - current
        lhs = len(orbit) * capacity * x8[shadow]
        reconstructed["ordered_pair"][(shadow, key)] = row_data(
            vector, shadow, tuple(sorted((a, b))), lhs
        )

    emitted = certificate["targeted_extension_rows"]["rows"]
    for family in reconstructed:
        indexed = {}
        for row in emitted[family]:
            if family == "unmarked":
                key = (int(row["canonical_order8_mask"]),)
            elif family == "vertex":
                key = (int(row["canonical_order8_mask"]),
                       int(row["rooted_key"]))
            else:
                key = (int(row["canonical_order8_mask"]),
                       int(row["ordered_pair_rooted_key"]))
            indexed[key] = row
        assert set(indexed) == set(reconstructed[family])
        for key, actual in reconstructed[family].items():
            row = indexed[key]
            emitted_extra = [0] * 9
            for index, value in row["extra9_coefficients"]:
                emitted_extra[int(index)] = int(value)
            assert emitted_extra == actual["extra"]
            assert int(row["fixed_visible19_rhs"]) == actual["fixed_rhs"]
            assert int(row["residual_capacity_before_extra9"]) == actual["residual"]
            assert row["closed_on_19"] == actual["closed19"]
            assert row["closed_on_28"] == actual["closed28"]
            assert int(row["support_size"]) == actual["support_size"]
            assert row["first_outside_28_mask"] == actual["outside"]

    counts = {family: len(rows) for family, rows in reconstructed.items()}
    closed = {family: sum(row["closed28"] for row in rows.values())
              for family, rows in reconstructed.items()}
    new_closed = {family: sum(row["closed28"] and not row["closed19"]
                              for row in rows.values())
                  for family, rows in reconstructed.items()}
    assert counts == {"unmarked": 46, "vertex": 165, "ordered_pair": 505}
    assert closed == {"unmarked": 0, "vertex": 0, "ordered_pair": 31}
    assert new_closed == {"unmarked": 0, "vertex": 0, "ordered_pair": 10}

    unique = sorted({(tuple(row["extra"]), row["residual"])
                     for rows in reconstructed.values() for row in rows.values()
                     if row["closed28"] and any(row["extra"])})
    assert len(unique) == rank([list(vector) for vector, _ in unique]) == 5
    assert [sum(vector[index] for vector, _ in unique) // 2
            for index in range(9)] == mass
    assert sum(rhs for _, rhs in unique) // 2 == 85116

    witness = list(map(int, certificate[
        "exact_nonnegative_extension_witness"
    ]["extra9_counts"]))
    assert witness == [0, 0, 25986, 36192, 0, 6792, 10224, 0, 5922]
    assert sum(a * b for a, b in zip(mass, witness)) == 85116
    minimum_slack = None
    for rows in reconstructed.values():
        for row in rows.values():
            value = sum(a * b for a, b in zip(row["extra"], witness))
            if row["closed28"]:
                assert value == row["residual"]
            else:
                assert value <= row["residual"]
                slack = row["residual"] - value
                minimum_slack = slack if minimum_slack is None else min(
                    minimum_slack, slack
                )
    assert minimum_slack == 0
    assert witness[2] % 2 == witness[6] % 2 == 0

    result = {
        "status": "independent-28-column-cross-X-audit-passed",
        "producer_imported": False,
        "certificate_sha256": digest(CERTIFICATE),
        "input_hashes_match": True,
        "added_masks_checked": len(extras),
        "added_vertex_deletions_checked": slots,
        "distinct_frozen_H8_shadows": len(shadows),
        "raw_H9_coefficient_matrices_checked": len(matrices),
        "distinct_X_glue_products_checked": 3,
        "next_flag_enlargement_products_checked": 20,
        "visible_derived_diagonals_checked": 74,
        "minimum_open_diagonal_missing_columns": minimum_diagonal_missing,
        "minimum_next_flag": "R0",
        "minimum_next_missing_H9_columns": len(missing_by_candidate[0]),
        "extension_row_counts": counts,
        "closed_on_28_counts": closed,
        "newly_closed_beyond_19_counts": new_closed,
        "independent_closed_equation_rank": 5,
        "gram_mass_half_sum_replayed": True,
        "witness_replayed_on_every_row": True,
        "exact_T0_Gram_rank": 1,
        "negative_direction_found": False,
        "submission_txt_written": False,
    }
    save(OUTPUT, result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
