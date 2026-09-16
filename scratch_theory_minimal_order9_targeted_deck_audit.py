"""Independent audit of the targeted 19-mask H9 deletion deck.

This verifier intentionally does not import the producer.  It reconstructs
the graph encodings, canonical forms, deletion coefficients, frozen marked
row map, all-G solution, and the 21 locally closed rooted-pair rows directly
from the published inputs and the emitted JSON certificate.
"""

from __future__ import annotations

import gzip
import hashlib
import itertools
import json
import os
from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache
from pathlib import Path


CERTIFICATE = Path("scratch_theory_minimal_order9_targeted_deck.json")
MATE = Path("scratch_theory_minimal_order9_mate_lift.json")
WAVE147 = Path(
    "external_conway99_research/attempts/wave147-alternative-lane/"
    "exact-results.json"
)
COEFFICIENTS = Path(
    "external_conway99_research/attempts/wave147-alternative-lane/"
    "coefficients.json.gz"
)
MARKED = Path(
    "external_conway99_research/attempts/wave148-marked-order8/"
    "marked-rows.json.gz"
)
WAVE163 = Path("scratch_theory_wave163_integral_order8_boundary.json")
OUTPUT = Path("scratch_theory_minimal_order9_targeted_deck_audit.json")


def digest(path: Path) -> str:
    state = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            state.update(chunk)
    return state.hexdigest()


def write_json(path: Path, data: object) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


@lru_cache(maxsize=None)
def pairs(n: int):
    return tuple((a, b) for a in range(n) for b in range(a + 1, n))


@lru_cache(maxsize=None)
def positions(n: int):
    return {edge: index for index, edge in enumerate(pairs(n))}


def rows_of(mask: int, n: int):
    rows = [0] * n
    for index, (a, b) in enumerate(pairs(n)):
        if mask & (1 << index):
            rows[a] |= 1 << b
            rows[b] |= 1 << a
    return tuple(rows)


def permuted(mask: int, n: int, image: list[int]):
    result = 0
    target = positions(n)
    for index, (a, b) in enumerate(pairs(n)):
        if mask & (1 << index):
            edge = tuple(sorted((image[a], image[b])))
            result |= 1 << target[edge]
    return result


@lru_cache(maxsize=None)
def rooted_form(mask: int, n: int, fixed: tuple[int, ...] = ()):
    graph = rows_of(mask, n)
    fixed_set = set(fixed)
    cells = defaultdict(list)
    for vertex in range(n):
        if vertex in fixed_set:
            continue
        cells[(graph[vertex].bit_count(),) + tuple(
            int(bool(graph[vertex] & (1 << root))) for root in fixed
        )].append(vertex)
    products = []
    next_label = len(fixed)
    for signature in sorted(cells):
        sources = cells[signature]
        targets = tuple(range(next_label, next_label + len(sources)))
        next_label += len(sources)
        products.append(tuple(itertools.permutations(targets)))
    minimum = None
    for target_cells in itertools.product(*products):
        image = [0] * n
        for label, vertex in enumerate(fixed):
            image[vertex] = label
        for signature, targets in zip(sorted(cells), target_cells):
            for source, target in zip(cells[signature], targets):
                image[source] = target
        candidate = permuted(mask, n, image)
        minimum = candidate if minimum is None else min(minimum, candidate)
    assert minimum is not None
    return minimum


def remove(mask: int, n: int, deleted: int):
    kept = [v for v in range(n) if v != deleted]
    relabel = {old: new for new, old in enumerate(kept)}
    source = positions(n)
    answer = 0
    for bit, (a, b) in enumerate(itertools.combinations(kept, 2)):
        if mask & (1 << source[(a, b)]):
            answer |= 1 << bit
    return answer, relabel


def add(mask8: int, neighborhood: tuple[int, ...]):
    answer = 0
    p9 = positions(9)
    for bit, edge in enumerate(pairs(8)):
        if mask8 & (1 << bit):
            answer |= 1 << p9[edge]
    for vertex in neighborhood:
        answer |= 1 << p9[(vertex, 8)]
    return answer


def upper_admissible(mask: int, n: int):
    graph = rows_of(mask, n)
    if any(row.bit_count() > 14 for row in graph):
        return False
    return all(
        (graph[a] & graph[b]).bit_count()
        <= (1 if graph[a] & (1 << b) else 2)
        for a, b in pairs(n)
    )


def rank_q(matrix):
    if not matrix:
        return 0
    work = [[Fraction(value) for value in row] for row in matrix]
    pivot_row = 0
    for column in range(len(work[0])):
        pivot = next(
            (row for row in range(pivot_row, len(work))
             if work[row][column]), None
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        divisor = work[pivot_row][column]
        work[pivot_row] = [value / divisor for value in work[pivot_row]]
        for row in range(len(work)):
            if row == pivot_row or not work[row][column]:
                continue
            factor = work[row][column]
            work[row] = [
                x - factor * y for x, y in zip(work[row], work[pivot_row])
            ]
        pivot_row += 1
    return pivot_row


def solve_full_rank(matrix, rhs):
    augmented = [
        [Fraction(value) for value in row] + [Fraction(value)]
        for row, value in zip(matrix, rhs)
    ]
    pivot_row = 0
    pivots = []
    for column in range(len(matrix[0])):
        pivot = next(
            (row for row in range(pivot_row, len(augmented))
             if augmented[row][column]), None
        )
        if pivot is None:
            continue
        augmented[pivot_row], augmented[pivot] = (
            augmented[pivot], augmented[pivot_row]
        )
        divisor = augmented[pivot_row][column]
        augmented[pivot_row] = [
            value / divisor for value in augmented[pivot_row]
        ]
        for row in range(len(augmented)):
            if row == pivot_row or not augmented[row][column]:
                continue
            factor = augmented[row][column]
            augmented[row] = [
                x - factor * y
                for x, y in zip(augmented[row], augmented[pivot_row])
            ]
        pivots.append(column)
        pivot_row += 1
    assert pivot_row == len(matrix[0])
    assert all(any(row[:-1]) or not row[-1] for row in augmented)
    answer = [Fraction() for _ in matrix[0]]
    for row, column in enumerate(pivots):
        answer[column] = augmented[row][-1]
    return answer


def main() -> None:
    cert = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    mate = json.loads(MATE.read_text(encoding="utf-8"))
    wave147 = json.loads(WAVE147.read_text(encoding="utf-8"))
    marked = json.loads(gzip.decompress(MARKED.read_bytes()).decode("utf-8"))
    wave163 = json.loads(WAVE163.read_text(encoding="utf-8"))
    coefficients = json.loads(
        gzip.decompress(COEFFICIENTS.read_bytes()).decode("utf-8")
    )

    for path in (MATE, WAVE147, COEFFICIENTS, MARKED, WAVE163):
        assert cert["inputs"][str(path)]["sha256"] == digest(path)

    classes8 = tuple(map(int,
        wave147["class_streams"]["8"]["canonical_masks"]
    ))
    classes7 = tuple(
        int(row["order7_mask"])
        for row in coefficients["order7_to_order8_deletion_equations"]
    )
    assert (len(classes7), len(classes8), len(marked["vertex_rows"]),
            len(marked["ordered_pair_rows"])) == (208, 916, 944, 4440)
    class8_set = set(classes8)
    visible = tuple(
        int(row[0]) for row in mate["marked_lift_schema"]
        ["visible_order9_type_marked_weights"]
    )
    assert len(visible) == len(set(visible)) == 19

    # Reconstruct all 171 unmarked deletions and their 39 frozen shadows.
    emitted_decks = cert["unmarked_targeted_deck"]["decks"]
    assert len(emitted_decks) == 19
    shadows = set()
    deletion_slots = 0
    for hindex, mask9 in enumerate(visible):
        row = emitted_decks[hindex]
        assert int(row["canonical_order9_mask"]) == mask9
        histogram = Counter()
        assert len(row["vertex_deletions"]) == 9
        for deleted, item in enumerate(row["vertex_deletions"]):
            raw8, _ = remove(mask9, 9, deleted)
            canonical8 = rooted_form(raw8, 8)
            assert item == {
                "deleted_vertex": deleted,
                "raw_order8_mask": raw8,
                "canonical_order8_mask": canonical8,
                "frozen_order8_index_0_based": classes8.index(canonical8),
            }
            assert canonical8 in class8_set
            histogram[canonical8] += 1
            shadows.add(canonical8)
            deletion_slots += 1
        assert row["deletion_histogram"] == [
            [mask, count] for mask, count in sorted(histogram.items())
        ]
    assert deletion_slots == 171 and len(shadows) == 39

    # Reconstruct the 33 labelled templates and all 297 role deletions.
    emitted_templates = cert["role_preserving_targeted_deck"]["templates"]
    expected_templates = []
    for source in mate["marked_lift_schema"]["rows"]:
        for extension in source["mate_bit_extensions"]:
            if extension["pair_upper_feasible"]:
                expected_templates.append((source, extension))
    assert len(expected_templates) == len(emitted_templates) == 33
    mate_deletions = nonmate_deletions = 0
    for emitted, (source, extension) in zip(
            emitted_templates, expected_templates):
        labelled9 = int(extension["labelled_order9_mask"])
        assert emitted["source_row_id"] == source["row_id"]
        assert emitted["mate_bits"] == extension["mate_bits"]
        assert int(emitted["labelled_order9_mask"]) == labelled9
        assert int(emitted["visible_canonical_order9_mask"]) == int(
            extension["degree_cell_canonical_order9_mask"]
        )
        assert len(emitted["vertex_deletions"]) == 9
        for deleted, item in enumerate(emitted["vertex_deletions"]):
            raw8, relabel = remove(labelled9, 9, deleted)
            shadow = rooted_form(raw8, 8)
            assert int(item["canonical_order8_mask"]) == shadow
            assert int(item["frozen_nested_map_order8_mask"]) == shadow
            surviving = item["full_original_X_X_flag_survives"]
            assert surviving == (deleted == 8)
            assert item["mate_delete_row_id"] == (
                source["row_id"] if deleted == 8 else None
            )
            emitted_vertices = {
                int(row["original_vertex"]): int(row["order8_vertex"])
                for row in item["surviving_roles"]
            }
            assert emitted_vertices == relabel
            if deleted == 8:
                mate_deletions += 1
                assert shadow == int(source["order8_canonical_mask"])
            else:
                nonmate_deletions += 1
    assert (mate_deletions, nonmate_deletions) == (33, 264)

    # Independently enumerate each shadow's marked H7->H8 coefficients.
    vertex_lookup = {int(row["rooted_key"]): row
                     for row in marked["vertex_rows"]}
    pair_lookup = {int(row["rooted_key"]): row
                   for row in marked["ordered_pair_rows"]}
    vertex_by_id = {row["row_id"]: row for row in marked["vertex_rows"]}
    pair_by_id = {row["row_id"]: row
                  for row in marked["ordered_pair_rows"]}
    emitted_shadow_maps = {
        int(row["canonical_order8_mask"]): row
        for row in cert["frozen_marked_identity_map"]["shadow_maps"]
    }
    touched_v = set()
    touched_p = set()
    marked_events_v = marked_events_p = 0
    for mask8 in sorted(shadows):
        graph8 = rows_of(mask8, 8)
        vc = Counter()
        pc = Counter()
        for deleted in range(8):
            mask7, relabel = remove(mask8, 8, deleted)
            canonical7 = rooted_form(mask7, 7)
            neighborhood = [
                v for v in range(8)
                if v != deleted and graph8[deleted] & (1 << v)
            ]
            for root in neighborhood:
                key = rooted_form(mask7, 7, (relabel[root],))
                frozen_row = vertex_lookup[key]
                assert rooted_form(int(frozen_row["order7_mask"]), 7) == canonical7
                vc[frozen_row["row_id"]] += 1
                marked_events_v += 1
            for a in neighborhood:
                for b in neighborhood:
                    if a == b:
                        continue
                    key = rooted_form(mask7, 7, (relabel[a], relabel[b]))
                    frozen_row = pair_lookup[key]
                    assert rooted_form(int(frozen_row["order7_mask"]), 7) == canonical7
                    pc[frozen_row["row_id"]] += 1
                    marked_events_p += 1
        emitted = emitted_shadow_maps[mask8]
        assert emitted["vertex_marked_rows"] == [
            [row_id, count] for row_id, count in sorted(vc.items())
        ]
        assert emitted["ordered_pair_marked_rows"] == [
            [row_id, count] for row_id, count in sorted(pc.items())
        ]
        frozen_v = Counter({
            row_id: int(dict(row["terms_order8_mask_coefficient"])
                        .get(mask8, 0))
            for row_id, row in vertex_by_id.items()
            if int(dict(row["terms_order8_mask_coefficient"])
                   .get(mask8, 0))
        })
        frozen_p = Counter({
            row_id: int(dict(row["terms_order8_mask_coefficient"])
                        .get(mask8, 0))
            for row_id, row in pair_by_id.items()
            if int(dict(row["terms_order8_mask_coefficient"])
                   .get(mask8, 0))
        })
        assert vc == frozen_v
        assert pc == frozen_p
        touched_v.update(vc)
        touched_p.update(pc)
    assert (len(touched_v), len(touched_p)) == (196, 598)

    x7 = {int(mask): int(count) for mask, count in
          wave163["integral_pseudocount"]["order7_mask_count_pairs"]}
    x8 = {int(mask): int(count) for mask, count in
          wave163["integral_pseudocount"]["order8_mask_count_pairs"]}
    for row in marked["vertex_rows"]:
        lhs = int(row["lhs_coefficient"]) * x7[int(row["order7_mask"])]
        rhs = sum(int(c) * x8[int(mask)]
                  for mask, c in row["terms_order8_mask_coefficient"])
        assert lhs == rhs
    for row in marked["ordered_pair_rows"]:
        lhs = int(row["lhs_coefficient"]) * x7[int(row["order7_mask"])]
        rhs = sum(int(c) * x8[int(mask)]
                  for mask, c in row["terms_order8_mask_coefficient"])
        assert lhs == rhs

    # Solve the 11-by-9 mate equations independently.
    t0_data = mate["T0_all_G_order9_closure"]
    t0_masks = tuple(
        int(row["degree_cell_canonical_mask"])
        for row in t0_data["H9_mark_audit"]
    )
    mate_rows = {row["row_id"]: row
                 for row in mate["marked_lift_schema"]["rows"]}
    mate_matrix, mate_rhs = [], []
    for equation in t0_data["incidence_rows"]:
        vector = [0] * 9
        for index, coefficient in equation["H9_coefficients"]:
            vector[int(index)] = int(coefficient)
        source = mate_rows[equation["row_id"]]
        mate_matrix.append(vector)
        mate_rhs.append(
            int(source["marked_orbit_size"])
            * x8[int(source["order8_canonical_mask"])]
        )
    h9 = solve_full_rank(mate_matrix, mate_rhs)
    assert h9 == list(map(Fraction,
        cert["T0_all_G_targeted_order9_projection"]
        ["wave163_unique_H9_counts"]
    ))
    assert h9 == list(map(Fraction,
        [2335, 7119, 15108, 19217, 0, 0, 1197, 762, 0]
    ))

    # Reconstruct all 19-column order-8-to-9 coefficient rows.
    unmarked = defaultdict(lambda: [0] * 19)
    vertices = defaultdict(lambda: [0] * 19)
    ordered_pairs = defaultdict(lambda: [0] * 19)
    for hindex, mask9 in enumerate(visible):
        graph9 = rows_of(mask9, 9)
        for deleted in range(9):
            mask8, relabel = remove(mask9, 9, deleted)
            canonical8 = rooted_form(mask8, 8)
            unmarked[canonical8][hindex] += 1
            neighborhood = [
                v for v in range(9)
                if v != deleted and graph9[deleted] & (1 << v)
            ]
            for root in neighborhood:
                key = rooted_form(mask8, 8, (relabel[root],))
                vertices[(canonical8, key)][hindex] += 1
            for a in neighborhood:
                for b in neighborhood:
                    if a != b:
                        key = rooted_form(mask8, 8, (relabel[a], relabel[b]))
                        ordered_pairs[(canonical8, key)][hindex] += 1

    projection = cert["T0_all_G_targeted_order9_projection"]
    emitted_rows = projection["rows"]
    assert tuple(projection["H9_masks"]) == t0_masks
    index19 = {mask: index for index, mask in enumerate(visible)}
    candidate = [Fraction() for _ in range(19)]
    for index, mask in enumerate(t0_masks):
        candidate[index19[mask]] = h9[index]
    assert candidate == list(map(Fraction,
        projection["wave163_visible_19_candidate_counts"]
    ))

    closed_vectors = []
    closed_nonmate = 0
    closed_rows = 0
    forced_zero = set()
    mate_shadows = {
        int(row["order8_canonical_mask"])
        for row in mate["marked_lift_schema"]["rows"]
    }

    def sparse_to_vector(data):
        vector = [0] * 19
        for index, coefficient in data:
            vector[int(index)] = int(coefficient)
        return vector

    def verify_open_witness(mask8, required, emitted):
        witness = emitted["omitted_extension_witness"]
        assert witness is not None
        neighborhood = tuple(witness["new_vertex_neighbors_in_canonical_H8"])
        assert set(required) <= set(neighborhood)
        candidate9 = add(mask8, neighborhood)
        assert upper_admissible(candidate9, 9)
        canonical9 = rooted_form(candidate9, 9)
        assert canonical9 == int(witness["omitted_canonical_order9_mask"])
        assert canonical9 not in visible

    assert len(emitted_rows["unmarked"]) == len(unmarked) == 39
    for emitted in emitted_rows["unmarked"]:
        mask8 = int(emitted["canonical_order8_mask"])
        vector = sparse_to_vector(emitted["visible_19_H9_coefficients"])
        assert vector == unmarked[mask8]
        lhs = 91 * x8[mask8]
        rhs = sum(value * coefficient
                  for value, coefficient in zip(candidate, vector))
        assert lhs == int(emitted["wave163_lhs"])
        assert rhs == Fraction(emitted["wave163_visible_19_candidate_rhs"])
        assert lhs - rhs == Fraction(emitted["omitted_nonnegative_slack"])
        assert not emitted["closed_on_visible_19"]
        verify_open_witness(mask8, (), emitted)

    assert len(emitted_rows["vertex"]) == len(vertices) == 136
    for emitted in emitted_rows["vertex"]:
        mask8 = int(emitted["canonical_order8_mask"])
        key = int(emitted["rooted_key"])
        vector = sparse_to_vector(emitted["visible_19_H9_coefficients"])
        assert vector == vertices[(mask8, key)]
        graph8 = rows_of(mask8, 8)
        roots = [v for v in range(8)
                 if rooted_form(mask8, 8, (v,)) == key]
        degree = graph8[roots[0]].bit_count()
        lhs = len(roots) * (14 - degree) * x8[mask8]
        rhs = sum(value * coefficient
                  for value, coefficient in zip(candidate, vector))
        assert lhs == int(emitted["wave163_lhs"])
        assert lhs - rhs == Fraction(emitted["omitted_nonnegative_slack"])
        assert not emitted["closed_on_visible_19"]
        verify_open_witness(mask8, (roots[0],), emitted)

    assert len(emitted_rows["ordered_pair"]) == len(ordered_pairs) == 398
    for emitted in emitted_rows["ordered_pair"]:
        mask8 = int(emitted["canonical_order8_mask"])
        key = int(emitted["ordered_pair_rooted_key"])
        vector = sparse_to_vector(emitted["visible_19_H9_coefficients"])
        assert vector == ordered_pairs[(mask8, key)]
        graph8 = rows_of(mask8, 8)
        roots = [(a, b) for a in range(8) for b in range(8) if a != b
                 and rooted_form(mask8, 8, (a, b)) == key]
        a, b = roots[0]
        common = (graph8[a] & graph8[b]).bit_count()
        capacity = (1 if graph8[a] & (1 << b) else 2) - common
        lhs = len(roots) * capacity * x8[mask8]
        rhs = sum(value * coefficient
                  for value, coefficient in zip(candidate, vector))
        assert lhs == int(emitted["wave163_lhs"])
        assert lhs - rhs == Fraction(emitted["omitted_nonnegative_slack"])
        required = tuple(sorted((a, b)))
        if emitted["closed_on_visible_19"]:
            closed_rows += 1
            closed_vectors.append(vector)
            if mask8 not in mate_shadows:
                closed_nonmate += 1
            support = set()
            remaining = [v for v in range(8) if v not in required]
            for bits in range(1 << len(remaining)):
                neighborhood = tuple(sorted(required + tuple(
                    remaining[i] for i in range(len(remaining))
                    if bits & (1 << i)
                )))
                candidate9 = add(mask8, neighborhood)
                if upper_admissible(candidate9, 9):
                    support.add(rooted_form(candidate9, 9))
            assert support <= set(visible)
            assert sorted(index19[mask] for mask in support) == emitted[
                "closed_support_visible_H9_indices"
            ]
            assert lhs == rhs
            for index, coefficient in enumerate(vector):
                if coefficient and not candidate[index]:
                    forced_zero.add(index)
        else:
            verify_open_witness(mask8, required, emitted)

    assert (closed_rows, closed_nonmate, rank_q(closed_vectors)) == (21, 8, 11)
    gg_columns = [index19[mask] for mask in t0_masks]
    closed_gg = [[row[index] for index in gg_columns]
                 for row in closed_vectors]
    assert rank_q(closed_gg) == rank_q(mate_matrix) == 9
    assert rank_q(mate_matrix + closed_gg) == 9
    other_columns = set(range(19)) - set(gg_columns)
    assert other_columns <= forced_zero
    assert sorted(forced_zero) == projection[
        "forced_zero_visible_19_indices_at_wave163"
    ]

    # Validate all 19 nonnegative integer outside-neighbourhood witnesses.
    moment_data = cert[
        "outside_neighborhood_first_second_moment_feasibility"
    ]
    assert moment_data["all_19_feasible"]
    assert len(moment_data["witnesses"]) == 19
    pattern_entries = 0
    for index, (mask9, witness) in enumerate(
            zip(visible, moment_data["witnesses"])):
        assert int(witness["visible_h9_index"]) == index
        assert int(witness["canonical_order9_mask"]) == mask9
        counts = {int(pattern): int(count)
                  for pattern, count in witness["nonzero_pattern_counts"]}
        assert all(count > 0 for count in counts.values())
        assert sum(counts.values()) == 90
        graph9 = rows_of(mask9, 9)
        first = tuple(
            sum(count for pattern, count in counts.items()
                if pattern & (1 << vertex))
            for vertex in range(9)
        )
        expected_first = tuple(14 - row.bit_count() for row in graph9)
        assert first == expected_first
        second = tuple(
            sum(count for pattern, count in counts.items()
                if pattern & (1 << a) and pattern & (1 << b))
            for a, b in pairs(9)
        )
        expected_second = tuple(
            (1 if graph9[a] & (1 << b) else 2)
            - (graph9[a] & graph9[b]).bit_count()
            for a, b in pairs(9)
        )
        assert second == expected_second
        pattern_entries += len(counts)

    audit = {
        "status": "independent-audit-passed",
        "producer_imported": False,
        "certificate_sha256": digest(CERTIFICATE),
        "input_hashes_match": True,
        "unmarked_vertex_deletions_checked": deletion_slots,
        "distinct_frozen_order8_shadows": len(shadows),
        "labelled_role_deletions_checked": mate_deletions + nonmate_deletions,
        "mate_deletions": mate_deletions,
        "nonmate_deletions": nonmate_deletions,
        "marked_vertex_events_reconstructed": marked_events_v,
        "marked_pair_events_reconstructed": marked_events_p,
        "touched_frozen_vertex_rows": len(touched_v),
        "touched_frozen_pair_rows": len(touched_p),
        "all_frozen_944_plus_4440_identities_checked_at_wave163": True,
        "wave163_all_G_H9_solution": [int(value) for value in h9],
        "order8_to_order9_rows_checked": {
            "unmarked": len(unmarked),
            "vertex": len(vertices),
            "ordered_pair": len(ordered_pairs),
        },
        "closed_pair_rows_exhaustively_checked": closed_rows,
        "closed_pair_rows_from_nonmate_shadows": closed_nonmate,
        "closed_matrix_rank_visible19": rank_q(closed_vectors),
        "closed_matrix_rank_GG9": rank_q(closed_gg),
        "forced_zero_visible_columns": sorted(forced_zero),
        "all_ten_non_GG_visible_columns_forced_zero": True,
        "outside_pattern_witnesses_checked": 19,
        "outside_pattern_nonzero_entries_checked": pattern_entries,
        "submission_txt_written": False,
    }
    write_json(OUTPUT, audit)
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
