"""Producer-independent audit of the targeted 41-column six-flag lane."""

from __future__ import annotations

import hashlib
import itertools
import json
import os
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

from scratch_theory_order9_r0_closure_audit import (
    canonical,
    delete_vertex,
    extend_vertex,
    graph_rows,
    glue_support,
    locally_upper,
    matrix_rank,
    natural_flags,
)


CERTIFICATE = Path("scratch_theory_order9_six_flag_41_closure.json")
R0_CERT = Path("scratch_theory_order9_r0_closure.json")
PROBE37 = Path("scratch_theory_order9_two_mask_diagonal_clique_probe.json")
CROSS_CERT = Path("scratch_theory_order9_cross_x_closure.json")
DECK = Path("scratch_theory_minimal_order9_targeted_deck.json")
WAVE147 = Path(
    "external_conway99_research/attempts/wave147-alternative-lane/"
    "exact-results.json"
)
WAVE163 = Path("scratch_theory_wave163_integral_order8_boundary.json")
OUTPUT = Path("scratch_theory_order9_six_flag_41_closure_audit.json")


def sha(path: Path) -> str:
    state = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            state.update(chunk)
    return state.hexdigest()


def save(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def induced(mask: int, order: int, chosen):
    graph = graph_rows(mask, order)
    target_edges = tuple(itertools.combinations(range(len(chosen)), 2))
    target_bits = {edge: bit for bit, edge in enumerate(target_edges)}
    answer = 0
    for left in range(len(chosen)):
        for right in range(left + 1, len(chosen)):
            if graph[chosen[left]] & (1 << chosen[right]):
                answer |= 1 << target_bits[(left, right)]
    return answer


def family_moment(mask: int, order: int, flag_masks):
    index = {flag: position for position, flag in enumerate(flag_masks)}
    graph = graph_rows(mask, order)
    size = len(flag_masks)
    matrix = [[0] * size for _ in range(size)]
    for roots in itertools.permutations(range(order), 3):
        if not all(graph[a] & (1 << b)
                   for a, b in itertools.combinations(roots, 2)):
            continue
        available = tuple(v for v in range(order) if v not in roots)
        occurrences = []
        for free in itertools.combinations(available, 3):
            small = induced(mask, order, roots + free)
            key = canonical(small, 6, (0, 1, 2))
            if key in index:
                occurrences.append((set(free), index[key]))
        for left, i in occurrences:
            for right, j in occurrences:
                if len(set(roots) | left | right) == order:
                    matrix[i][j] += 1
    return matrix


def add(total, matrix, weight):
    for i in range(len(total)):
        for j in range(len(total)):
            total[i][j] += weight * matrix[i][j]


def matrix_from_upper(entries, size):
    answer = [[0] * size for _ in range(size)]
    for left, right, value in entries:
        answer[int(left)][int(right)] = int(value)
        answer[int(right)][int(left)] = int(value)
    return answer


def main() -> None:
    certificate = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    r0 = json.loads(R0_CERT.read_text(encoding="utf-8"))
    probe37 = json.loads(PROBE37.read_text(encoding="utf-8"))
    cross = json.loads(CROSS_CERT.read_text(encoding="utf-8"))
    deck = json.loads(DECK.read_text(encoding="utf-8"))
    frozen = json.loads(WAVE147.read_text(encoding="utf-8"))
    wave163 = json.loads(WAVE163.read_text(encoding="utf-8"))
    for path in (R0_CERT, PROBE37, CROSS_CERT, DECK, WAVE147, WAVE163):
        assert certificate["inputs"][str(path)]["sha256"] == sha(path)

    projection = deck["T0_all_G_targeted_order9_projection"]
    visible = tuple(map(int, projection["visible_19_H9_masks"]))
    fixed19 = tuple(map(int, projection["wave163_visible_19_candidate_counts"]))
    old9 = tuple(map(int, cross["added_nine_masks"]))
    r0seven = tuple(map(int, r0["added_seven_masks"]))
    flags = tuple(map(int, certificate["six_rooted_flag_masks"]))
    diagonal2 = tuple(map(int, certificate["added_masks"]["diagonal_two"]))
    cross4 = tuple(map(int, certificate["added_masks"]["cross_four"]))
    masks35 = visible + old9 + r0seven
    masks41 = masks35 + diagonal2 + cross4
    variables = old9 + r0seven + diagonal2 + cross4
    universe35, universe37, universe41 = (set(masks35),
                                          set(masks35 + diagonal2),
                                          set(masks41))
    assert len(flags) == 6 and len(masks41) == len(set(masks41)) == 41

    frozen8 = tuple(map(int, frozen["class_streams"]["8"]["canonical_masks"]))
    frozen8_set = set(frozen8)
    x7 = {int(mask): int(value) for mask, value in
          wave163["integral_pseudocount"]["order7_mask_count_pairs"]}
    x8 = {int(mask): int(value) for mask, value in
          wave163["integral_pseudocount"]["order8_mask_count_pairs"]}
    assert len(x7) == 208 and len(x8) == len(frozen8_set) == 916

    # Four new masks and all 36 deletions.
    shadows = set()
    for mask in cross4:
        assert canonical(mask, 9) == mask and locally_upper(mask, 9)
        for removed in range(9):
            raw, _ = delete_vertex(mask, 9, removed)
            shadow = canonical(raw, 8)
            assert shadow in frozen8_set and x8[shadow] > 0
            shadows.add(shadow)
    assert len(shadows) == certificate["cross_four_deletion_decks"][
        "distinct_frozen_order8_shadows"
    ]

    # Full closure graph replay.
    edges = []
    emitted_rows = {(int(row["left_flag_index"]),
                     int(row["right_flag_index"])): row
                    for row in certificate["closure_graph"]["rows"]}
    deficit = Counter()
    for left, right in itertools.combinations_with_replacement(range(6), 2):
        support = glue_support(flags[left], flags[right])
        outside = sorted(support - universe41)
        row = emitted_rows[(left, right)]
        assert row["outside_41_masks"] == outside
        assert int(row["support_size"]) == len(support)
        if left != right:
            deficit[len(outside)] += 1
            if not outside:
                edges.append((left, right))
    assert edges == [(0, 1), (0, 2), (1, 3), (2, 4), (3, 5), (4, 5)]
    assert deficit == Counter({0: 6, 9: 6, 15: 3})
    assert not any(all(tuple(sorted(edge)) in edges
                       for edge in ((a, b), (a, c), (b, c)))
                   for a, b, c in itertools.combinations(range(6), 3))

    # Frozen H6 reconstruction and all 1,205 coefficient matrices.
    numerator6 = defaultdict(int)
    for mask, count in x7.items():
        for removed in range(7):
            raw, _ = delete_vertex(mask, 7, removed)
            numerator6[canonical(raw, 6)] += count
    x6 = {mask: Fraction(value, 93) for mask, value in numerator6.items()}
    assert len(x6) == 62 and all(value.denominator == 1 for value in x6.values())
    count_vectors = {
        6: x6, 7: x7, 8: x8,
        9: {mask: fixed19[index] for index, mask in enumerate(visible)},
    }
    total = [[Fraction() for _ in range(6)] for _ in range(6)]
    by_order = {}
    class_checks = 0
    nonzero_counts = {}
    for order, counts in count_vectors.items():
        subtotal = [[Fraction() for _ in range(6)] for _ in range(6)]
        nonzero = 0
        for mask, count in sorted(counts.items()):
            matrix = family_moment(mask, order, flags)
            class_checks += 1
            nonzero += int(any(any(row) for row in matrix))
            add(subtotal, matrix, count)
            add(total, matrix, count)
        by_order[str(order)] = [[int(value) for value in row]
                                for row in subtotal]
        nonzero_counts[str(order)] = nonzero
    assert class_checks == 1205
    emitted_coefficients = certificate["six_flag_coefficient_system"]
    assert by_order == emitted_coefficients["weighted_fixed19_matrix_by_order"]
    assert nonzero_counts == emitted_coefficients["nonzero_class_counts_by_order"]
    assert [[int(value) for value in row] for row in total] == (
        emitted_coefficients["weighted_fixed_orders6_to8_plus_visible19_matrix"]
    )

    variable_matrices = [family_moment(mask, 9, flags) for mask in variables]
    records = emitted_coefficients["variable_order9_coefficient_matrices"]
    for matrix, record, mask in zip(variable_matrices, records, variables):
        assert int(record["canonical_order9_mask"]) == mask
        assert matrix_from_upper(record["upper_entries"], 6) == matrix
    selected_natural = tuple(natural_flags()[index] for index in (0, 4, 5, 6, 7))
    for mask in diagonal2 + cross4:
        assert not any(any(row) for row in family_moment(mask, 9,
                                                         selected_natural))

    # All touched local extension rows.
    unmarked = defaultdict(lambda: [0] * 41)
    one_root = defaultdict(lambda: [0] * 41)
    two_root = defaultdict(lambda: [0] * 41)
    for column, mask in enumerate(masks41):
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
            for a in incident:
                for b in incident:
                    if a != b:
                        key = canonical(raw, 8, (mapping[a], mapping[b]))
                        two_root[(shadow, key)][column] += 1

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
                candidate = extend_vertex(shadow, tuple(sorted(required + extra)))
                if locally_upper(candidate, 9):
                    image = canonical(candidate, 9)
                    support.add(image)
                    if image not in universe41 and first_outside is None:
                        first_outside = image
        support_cache[cache_key] = support, first_outside
        return support, first_outside

    fixed = list(fixed19) + [0] * 22
    rows = {"unmarked": {}, "vertex": {}, "ordered_pair": {}}

    def row_data(vector, shadow, required, lhs):
        support, outside = local_support(shadow, required)
        fixed_rhs = sum(value * count for value, count in zip(vector, fixed))
        return {"variable": vector[19:], "fixed": fixed_rhs,
                "residual": lhs - fixed_rhs,
                "closed35": support <= universe35,
                "closed37": support <= universe37,
                "closed41": outside is None,
                "support_size": len(support), "outside": outside}

    for shadow, vector in unmarked.items():
        rows["unmarked"][(shadow,)] = row_data(
            vector, shadow, (), 91 * x8[shadow]
        )
    for (shadow, key), vector in one_root.items():
        graph = graph_rows(shadow, 8)
        orbit = tuple(root for root in range(8)
                      if canonical(shadow, 8, (root,)) == key)
        degree = graph[orbit[0]].bit_count()
        rows["vertex"][(shadow, key)] = row_data(
            vector, shadow, (orbit[0],),
            len(orbit) * (14 - degree) * x8[shadow]
        )
    for (shadow, key), vector in two_root.items():
        graph = graph_rows(shadow, 8)
        orbit = tuple((a, b) for a in range(8) for b in range(8) if a != b
                      and canonical(shadow, 8, (a, b)) == key)
        a, b = orbit[0]
        adjacent = bool(graph[a] & (1 << b))
        common = (graph[a] & graph[b]).bit_count()
        capacity = (1 if adjacent else 2) - common
        rows["ordered_pair"][(shadow, key)] = row_data(
            vector, shadow, tuple(sorted((a, b))),
            len(orbit) * capacity * x8[shadow]
        )

    emitted_families = certificate["targeted_extension_rows"]["rows"]
    for family, reconstructed in rows.items():
        indexed = {}
        for row in emitted_families[family]:
            if family == "unmarked":
                key = (int(row["canonical_order8_mask"]),)
            elif family == "vertex":
                key = (int(row["canonical_order8_mask"]), int(row["rooted_key"]))
            else:
                key = (int(row["canonical_order8_mask"]),
                       int(row["ordered_pair_rooted_key"]))
            indexed[key] = row
        assert set(indexed) == set(reconstructed)
        for key, actual in reconstructed.items():
            emitted = indexed[key]
            vector = [0] * 22
            for coordinate, value in emitted["variable22_coefficients"]:
                vector[int(coordinate)] = int(value)
            assert vector == actual["variable"]
            assert int(emitted["fixed19_rhs"]) == actual["fixed"]
            assert int(emitted["residual_capacity"]) == actual["residual"]
            assert emitted["closed_on_35"] == actual["closed35"]
            assert emitted["closed_on_37"] == actual["closed37"]
            assert emitted["closed_on_41"] == actual["closed41"]
            assert int(emitted["support_size"]) == actual["support_size"]
            assert emitted["first_outside_41_mask"] == actual["outside"]

    row_counts = {family: len(family_rows) for family, family_rows in rows.items()}
    closed_counts = {family: sum(row["closed41"] for row in family_rows.values())
                     for family, family_rows in rows.items()}
    new_counts = {family: sum(row["closed41"] and not row["closed35"]
                              for row in family_rows.values())
                  for family, family_rows in rows.items()}
    assert row_counts == {"unmarked": 81, "vertex": 269, "ordered_pair": 757}
    assert closed_counts == {"unmarked": 0, "vertex": 0, "ordered_pair": 58}
    assert new_counts == {"unmarked": 0, "vertex": 0, "ordered_pair": 24}

    closed_equations = sorted({(tuple(row["variable"]), row["residual"])
                               for family_rows in rows.values()
                               for row in family_rows.values() if row["closed41"]})
    assert matrix_rank([list(vector) for vector, _ in closed_equations]) == 13
    new_equations = [(vector[16:], rhs) for vector, rhs in closed_equations
                     if not any(vector[:16]) and any(vector[16:])]
    assert matrix_rank([list(vector) for vector, _ in new_equations]) == 6

    witness = list(map(int, certificate[
        "exact_integer_T0_projection_witness"
    ]["counts"]))
    assert witness[-6:] == [8316, 74844, 8316, 74844, 8316, 66528]
    minimum_slack = None
    for family_rows in rows.values():
        for row in family_rows.values():
            value = sum(a * b for a, b in zip(row["variable"], witness))
            if row["closed41"]:
                assert value == row["residual"]
            else:
                assert value <= row["residual"]
                slack = row["residual"] - value
                minimum_slack = slack if minimum_slack is None else min(
                    minimum_slack, slack
                )

    gram = [[Fraction(value) for value in row] for row in total]
    for count, matrix in zip(witness, variable_matrices):
        add(gram, matrix, count)
    common_block = [[199584, 199584], [199584, 199584]]
    for left, right in edges:
        block = [[int(gram[left][left]), int(gram[left][right])],
                 [int(gram[right][left]), int(gram[right][right])]]
        assert block == common_block
        assert block[0][0] * block[1][1] - block[0][1] ** 2 == 0

    result = {
        "status": "independent-41-column-six-flag-audit-passed",
        "producer_imported": False,
        "certificate_sha256": sha(CERTIFICATE),
        "input_hashes_match": True,
        "cross_masks_checked": len(cross4),
        "cross_mask_deletions_checked": 36,
        "closure_products_checked": 21,
        "closure_graph": "C6",
        "maximum_clique_size": 2,
        "frozen_coefficient_class_checks": class_checks,
        "extension_row_counts": row_counts,
        "closed_on_41_counts": closed_counts,
        "newly_closed_beyond_35_counts": new_counts,
        "closed_equation_rank": 13,
        "new_six_count_rank": 6,
        "new_six_counts": witness[-6:],
        "integer_witness_replayed_on_every_row": True,
        "closed_two_by_two_blocks_checked": len(edges),
        "common_closed_block": common_block,
        "all_closed_blocks_rank_one_PSD": True,
        "negative_direction_found": False,
        "ambient_order9_census_generated": False,
        "R1_extension_attempted": False,
        "submission_txt_written": False,
    }
    save(OUTPUT, result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
