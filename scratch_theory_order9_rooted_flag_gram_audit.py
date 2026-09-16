"""Independent replay of the 19-column rooted-flag Gram calculation.

No producer module is imported.  Graph canonicalization, the two-root and
three-root coefficient counts, the 74-flag closure scan, and all exact PSD
checks are reconstructed here.
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


CERTIFICATE = Path("scratch_theory_order9_rooted_flag_gram.json")
DECK = Path("scratch_theory_minimal_order9_targeted_deck.json")
WAVE163 = Path("scratch_theory_wave163_integral_order8_boundary.json")
WAVE147 = Path(
    "external_conway99_research/attempts/wave147-alternative-lane/"
    "exact-results.json"
)
OUTPUT = Path("scratch_theory_order9_rooted_flag_gram_audit.json")


def file_hash(path: Path):
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            value.update(chunk)
    return value.hexdigest()


def save(path: Path, payload: object):
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


@lru_cache(maxsize=None)
def all_pairs(n):
    return tuple((a, b) for a in range(n) for b in range(a + 1, n))


@lru_cache(maxsize=None)
def pair_index(n):
    return {pair: index for index, pair in enumerate(all_pairs(n))}


def neighbor_bits(mask, n):
    answer = [0] * n
    for index, (a, b) in enumerate(all_pairs(n)):
        if mask >> index & 1:
            answer[a] |= 1 << b
            answer[b] |= 1 << a
    return tuple(answer)


def relabel_mask(mask, n, permutation):
    answer = 0
    target = pair_index(n)
    for index, (a, b) in enumerate(all_pairs(n)):
        if mask >> index & 1:
            edge = tuple(sorted((permutation[a], permutation[b])))
            answer |= 1 << target[edge]
    return answer


@lru_cache(maxsize=None)
def rooted_minimum(mask, n, roots=()):
    graph = neighbor_bits(mask, n)
    root_set = set(roots)
    cells = defaultdict(list)
    for vertex in range(n):
        if vertex not in root_set:
            cells[(graph[vertex].bit_count(),) + tuple(
                int(bool(graph[vertex] & (1 << root))) for root in roots
            )].append(vertex)
    signatures = sorted(cells)
    target_cells = []
    next_target = len(roots)
    for signature in signatures:
        size = len(cells[signature])
        targets = tuple(range(next_target, next_target + size))
        next_target += size
        target_cells.append(tuple(itertools.permutations(targets)))
    best = None
    for selected in itertools.product(*target_cells):
        permutation = [0] * n
        for target, root in enumerate(roots):
            permutation[root] = target
        for signature, targets in zip(signatures, selected):
            for source, target in zip(cells[signature], targets):
                permutation[source] = target
        image = relabel_mask(mask, n, permutation)
        best = image if best is None else min(best, image)
    assert best is not None
    return best


def vertex_deleted(mask, n, removed):
    keep = tuple(v for v in range(n) if v != removed)
    old_positions = pair_index(n)
    result = 0
    for bit, edge in enumerate(itertools.combinations(keep, 2)):
        if mask >> old_positions[edge] & 1:
            result |= 1 << bit
    return result


def induced_subgraph(mask, n, vertices):
    graph = neighbor_bits(mask, n)
    old_to_new = {old: new for new, old in enumerate(vertices)}
    result = 0
    target = pair_index(len(vertices))
    for a, b in itertools.combinations(vertices, 2):
        if graph[a] & (1 << b):
            image = tuple(sorted((old_to_new[a], old_to_new[b])))
            result |= 1 << target[image]
    return result


def locally_upper(mask, n):
    graph = neighbor_bits(mask, n)
    for a, b in all_pairs(n):
        bound = 1 if graph[a] & (1 << b) else 2
        if (graph[a] & graph[b]).bit_count() > bound:
            return False
    return True


NAMES = ("R0", "R1_0", "R1_1", "R1_2",
         "X_0", "X_1", "X_2", "P")


def matching_kind(graph, roots, free):
    if not all(graph[a] & (1 << b)
               for a, b in itertools.combinations(free, 2)):
        return None
    root_degree = [sum(bool(graph[r] & (1 << v)) for v in free)
                   for r in roots]
    free_degree = [sum(bool(graph[v] & (1 << r)) for r in roots)
                   for v in free]
    size = sum(root_degree)
    if size == 0:
        return 0
    if size == 1 and sorted(root_degree) == sorted(free_degree) == [0, 0, 1]:
        return 1 + root_degree.index(1)
    if size == 2 and sorted(root_degree) == sorted(free_degree) == [0, 1, 1]:
        return 4 + root_degree.index(0)
    if root_degree == free_degree == [1, 1, 1]:
        return 7
    return None


def canonical_natural_flags():
    flags = []
    base = set(all_pairs(3)) | set(itertools.combinations(range(3, 6), 2))
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
        mask = sum(1 << pair_index(6)[tuple(sorted(edge))] for edge in chosen)
        flags.append(rooted_minimum(mask, 6, (0, 1, 2)))
    return tuple(flags)


def glue(left, right, cross_mask):
    edge_set = set()
    for index, (a, b) in enumerate(all_pairs(6)):
        if left >> index & 1:
            edge_set.add((a, b))
        if right >> index & 1:
            image_a = a if a < 3 else a + 3
            image_b = b if b < 3 else b + 3
            edge_set.add(tuple(sorted((image_a, image_b))))
    cross_edges = tuple(itertools.product(range(3, 6), range(6, 9)))
    for index, edge in enumerate(cross_edges):
        if cross_mask >> index & 1:
            edge_set.add(edge)
    return sum(1 << pair_index(9)[edge] for edge in edge_set)


def support(left, right):
    result = Counter()
    for cross in range(512):
        mask = glue(left, right, cross)
        if locally_upper(mask, 9):
            result[rooted_minimum(mask, 9)] += 1
    assert result
    return result


def triangle_coeff(mask, n):
    graph = neighbor_bits(mask, n)
    result = [[0] * 8 for _ in range(8)]
    for roots in itertools.permutations(range(n), 3):
        if not all(graph[a] & (1 << b)
                   for a, b in itertools.combinations(roots, 2)):
            continue
        available = tuple(v for v in range(n) if v not in roots)
        flags = []
        for free in itertools.combinations(available, 3):
            kind = matching_kind(graph, roots, free)
            if kind is not None:
                flags.append((set(free), kind))
        for left, i in flags:
            for right, j in flags:
                if len(set(roots) | left | right) == n:
                    result[i][j] += 1
    return result


def edge_coeff(mask, n, edge_flag_to_kind):
    graph = neighbor_bits(mask, n)
    result = [[0] * 8 for _ in range(8)]
    for roots in itertools.permutations(range(n), 2):
        if not graph[roots[0]] & (1 << roots[1]):
            continue
        available = tuple(v for v in range(n) if v not in roots)
        flags = []
        for free in itertools.combinations(available, 4):
            common = [v for v in free
                      if graph[roots[0]] & (1 << v)
                      and graph[roots[1]] & (1 << v)]
            if len(common) != 1:
                continue
            small = induced_subgraph(mask, n, roots + free)
            key = rooted_minimum(small, 6, (0, 1))
            if key in edge_flag_to_kind:
                flags.append((set(free), edge_flag_to_kind[key]))
        for left, i in flags:
            for right, j in flags:
                if len(set(roots) | left | right) == n:
                    result[i][j] += 1
    return result


def from_upper(entries):
    matrix = [[0] * 8 for _ in range(8)]
    for left, right, value in entries:
        matrix[int(left)][int(right)] = int(value)
        matrix[int(right)][int(left)] = int(value)
    return matrix


def det(matrix):
    if len(matrix) == 1:
        return Fraction(matrix[0][0])
    return sum(
        (-1) ** column * Fraction(matrix[0][column])
        * det([row[:column] + row[column + 1:] for row in matrix[1:]])
        for column in range(len(matrix))
    )


def main():
    certificate = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    deck = json.loads(DECK.read_text(encoding="utf-8"))
    wave163 = json.loads(WAVE163.read_text(encoding="utf-8"))
    wave147 = json.loads(WAVE147.read_text(encoding="utf-8"))
    for path in (DECK, WAVE163, WAVE147):
        assert certificate["inputs"][str(path)]["sha256"] == file_hash(path)

    projection = deck["T0_all_G_targeted_order9_projection"]
    visible = tuple(map(int, projection["visible_19_H9_masks"]))
    visible_set = set(visible)
    q19 = tuple(map(Fraction, projection["wave163_visible_19_candidate_counts"]))
    x7 = {int(mask): int(value) for mask, value in
          wave163["integral_pseudocount"]["order7_mask_count_pairs"]}
    x8 = {int(mask): int(value) for mask, value in
          wave163["integral_pseudocount"]["order8_mask_count_pairs"]}
    frozen8 = set(map(int, wave147["class_streams"]["8"]["canonical_masks"]))
    assert len(x7) == 208 and len(x8) == len(frozen8) == 916
    assert set(x8) == frozen8

    numerator6 = defaultdict(int)
    for mask, count in x7.items():
        for removed in range(7):
            key = rooted_minimum(vertex_deleted(mask, 7, removed), 6)
            numerator6[key] += count
    x6 = {mask: Fraction(value, 93) for mask, value in numerator6.items()}
    assert len(x6) == 62
    assert all(value.denominator == 1 and value >= 0 for value in x6.values())
    assert sum(x6.values()) == 1120529256
    emitted6 = {
        int(mask): Fraction(value) for mask, value in
        certificate["count_vectors"]["derived_order6_mask_count_pairs"]
    }
    assert x6 == emitted6

    natural = canonical_natural_flags()
    assert list(natural) == certificate["flag_family"][
        "triangle_rooted_order6_masks"
    ]
    edge_flags = tuple(rooted_minimum(mask, 6, (0, 1)) for mask in natural)
    assert len(set(edge_flags)) == 8
    assert list(edge_flags) == certificate["flag_family"][
        "edge_rooted_order6_masks_with_unique_mate_free"
    ]

    # Re-extract all visible-derived rooted flags without using producer data.
    extracted = set()
    for mask in visible:
        graph = neighbor_bits(mask, 9)
        for roots in itertools.permutations(range(9), 3):
            if not all(graph[a] & (1 << b)
                       for a, b in itertools.combinations(roots, 2)):
                continue
            available = tuple(v for v in range(9) if v not in roots)
            for free in itertools.combinations(available, 3):
                small = induced_subgraph(mask, 9, roots + free)
                extracted.add(rooted_minimum(small, 6, (0, 1, 2)))
    assert len(extracted) == 74

    emitted_diagonal = {
        int(row["triangle_rooted_flag_mask"]): row
        for row in certificate["complete_visible_support_closure_test"]
        ["diagonal_rows"]
    }
    closed_diagonal = set()
    for flag in sorted(extracted):
        completion = support(flag, flag)
        closed = set(completion) <= visible_set
        row = emitted_diagonal[flag]
        assert int(row["locally_admissible_labelled_completions"]) == sum(
            completion.values()
        )
        assert int(row["canonical_completion_support_size"]) == len(completion)
        assert row["closed_on_visible_19"] == closed
        if closed:
            closed_diagonal.add(flag)
    assert closed_diagonal == set(natural[4:])

    emitted_pairs = {
        (row["left_flag"], row["right_flag"]): row
        for row in certificate["complete_visible_support_closure_test"]
        ["pair_closure_rows"]
    }
    closed_pair_names = set()
    outside_union = set()
    for left in range(4, 8):
        for right in range(left, 8):
            completion = support(natural[left], natural[right])
            outside = sorted(set(completion) - visible_set)
            row = emitted_pairs[(NAMES[left], NAMES[right])]
            assert int(row["locally_admissible_labelled_completions"]) == sum(
                completion.values()
            )
            assert row["outside_visible_support"] == outside
            assert row["closed_on_visible_19"] == (not outside)
            if not outside:
                closed_pair_names.add((NAMES[left], NAMES[right]))
            elif left != right and left < 7 and right < 7:
                outside_union.update(outside)
    assert len(outside_union) == 9
    assert closed_pair_names == {
        ("X_0", "X_0"), ("X_1", "X_1"), ("X_2", "X_2"),
        ("X_0", "P"), ("X_1", "P"), ("X_2", "P"), ("P", "P"),
    }

    # Independently reproduce every coefficient record and both root models.
    count_vectors = {
        6: x6,
        7: x7,
        8: x8,
        9: {mask: q19[index] for index, mask in enumerate(visible)},
    }
    edge_index = {mask: kind for kind, mask in enumerate(edge_flags)}
    emitted_records = certificate["coefficient_matrices"][
        "nonzero_class_records_by_union_order"
    ]
    total = [[Fraction() for _ in range(8)] for _ in range(8)]
    totals_by_order = {}
    class_checks = 0
    nonzero_records = {}
    for order, counts in count_vectors.items():
        expected_records = {
            int(row["canonical_mask"]): row
            for row in emitted_records[str(order)]
        }
        found_nonzero = set()
        subtotal = [[Fraction() for _ in range(8)] for _ in range(8)]
        for mask, count in sorted(counts.items()):
            first = triangle_coeff(mask, order)
            second = edge_coeff(mask, order, edge_index)
            assert first == second
            class_checks += 1
            if any(any(row) for row in first):
                found_nonzero.add(mask)
                assert from_upper(expected_records[mask]["upper_entries"]) == first
                assert Fraction(expected_records[mask][
                    "count_at_wave163_visible19_point"
                ]) == count
            for i in range(8):
                for j in range(8):
                    value = Fraction(count) * first[i][j]
                    subtotal[i][j] += value
                    total[i][j] += value
        assert found_nonzero == set(expected_records)
        nonzero_records[order] = len(found_nonzero)
        totals_by_order[order] = subtotal
        assert [[int(value) for value in row] for row in subtotal] == (
            certificate["coefficient_matrices"]["weighted_matrix_by_union_order"]
            [str(order)]
        )
    assert class_checks == 62 + 208 + 916 + 19
    assert nonzero_records == {6: 4, 7: 0, 8: 13, 9: 19}
    emitted_total = certificate["hostile_full_eight_type_zero_fill_control"][
        "matrix"
    ]
    assert [[int(value) for value in row] for row in total] == emitted_total

    # Exact S3-block PSD replay.
    a, b1, b2 = total[0][0], total[0][1], total[0][4]
    d1, o1 = total[1][1], total[1][2]
    d2, o2 = total[4][4], total[4][5]
    same, other = total[1][4], total[1][5]
    trivial = [
        [a, 3 * b1, 3 * b2],
        [3 * b1, 3 * (d1 + 2 * o1), 3 * (same + 2 * other)],
        [3 * b2, 3 * (same + 2 * other), 3 * (d2 + 2 * o2)],
    ]
    standard = [[d1 - o1, same - other],
                [same - other, d2 - o2]]
    trivial_minors = [trivial[0][0],
                      det([row[:2] for row in trivial[:2]]), det(trivial)]
    standard_minors = [standard[0][0], det(standard)]
    assert all(value > 0 for value in trivial_minors + standard_minors)
    control = certificate["hostile_full_eight_type_zero_fill_control"]
    assert list(map(Fraction, control[
        "trivial_block_leading_principal_minors"
    ])) == trivial_minors
    assert list(map(Fraction, control[
        "standard_block_leading_principal_minors"
    ])) == standard_minors

    # The three licensed principal blocks and the 21 exact rows.
    for x_index in (4, 5, 6):
        block = [[total[x_index][x_index], total[x_index][7]],
                 [total[7][x_index], total[7][7]]]
        assert block == [[199584, 0], [0, 0]]
        assert det(block) == 0
    representative_strata = {}
    for order, matrix in totals_by_order.items():
        representative_strata[str(order)] = [
            [int(matrix[6][6]), int(matrix[6][7])],
            [int(matrix[7][6]), int(matrix[7][7])],
        ]
    assert representative_strata == certificate["exact_closed_PSD_blocks"][
        "representative_X2_P_union_order_strata"
    ]

    closed_rows = [row for row in projection["rows"]["ordered_pair"]
                   if row["closed_on_visible_19"]]
    assert len(closed_rows) == 21
    for row in closed_rows:
        rhs = sum(q19[int(index)] * int(coefficient)
                  for index, coefficient in row["visible_19_H9_coefficients"])
        assert rhs == int(row["wave163_lhs"])
    assert all(value >= 0 and value.denominator == 1 for value in q19)

    result = {
        "status": "independent-rooted-flag-gram-audit-passed",
        "producer_imported": False,
        "certificate_sha256": file_hash(CERTIFICATE),
        "input_hashes_match": True,
        "derived_order6_classes_checked": len(x6),
        "visible_derived_triangle_rooted_flags_checked": len(extracted),
        "diagonal_completion_scans": len(extracted),
        "closed_diagonal_flags": ["X_0", "X_1", "X_2", "P"],
        "closed_pair_completion_scans": 10,
        "outside_cross_X_masks": len(outside_union),
        "two_root_three_root_class_coefficient_checks": class_checks,
        "nonzero_coefficient_records": nonzero_records,
        "licensed_closed_blocks_checked": 3,
        "licensed_block_matrix": [[199584, 0], [0, 0]],
        "full_eight_type_control_rank": 7,
        "full_eight_type_control_PSD": True,
        "closed_linear_rows_checked": len(closed_rows),
        "negative_direction_found": False,
        "submission_txt_written": False,
    }
    save(OUTPUT, result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
