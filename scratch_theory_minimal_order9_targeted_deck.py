"""Targeted deletion deck for the 19 visible H9 masks.

This producer deliberately reads the frozen Wave147/Wave148 catalogues.  It
does not regenerate either catalogue and it does not enumerate ambient H9
classes.  Its only order-nine inputs are the 19 masks already published by
``scratch_theory_minimal_order9_mate_lift``.

There are four independent outputs in the one JSON certificate:

* every one-vertex deletion of the 19 unmarked masks;
* every role-labelled deletion of the 33 feasible mate-bit templates;
* the exact map of the resulting H8 shadows into the frozen marked rows;
* the order-8-to-9 unmarked/vertex/pair extension inequalities restricted to
  the nine all-G variables at the Wave163 integral T=0 pseudopoint.

For the last item, omitted H9 columns are retained as a nonnegative slack.
The file therefore never promotes a targeted deck into a complete H9 census.
It also supplies an exact first/second-moment outside-neighbourhood witness
for each of the 19 masks.
"""

from __future__ import annotations

import gzip
import hashlib
import itertools
import json
import math
import os
from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache
from pathlib import Path


OUTPUT = Path("scratch_theory_minimal_order9_targeted_deck.json")
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
def edge_list(order: int) -> tuple[tuple[int, int], ...]:
    return tuple(itertools.combinations(range(order), 2))


@lru_cache(maxsize=None)
def edge_positions(order: int) -> dict[tuple[int, int], int]:
    return {edge: bit for bit, edge in enumerate(edge_list(order))}


def adjacency(mask: int, order: int) -> tuple[int, ...]:
    rows = [0] * order
    for bit, (left, right) in enumerate(edge_list(order)):
        if (mask >> bit) & 1:
            rows[left] |= 1 << right
            rows[right] |= 1 << left
    return tuple(rows)


def transform(mask: int, order: int, permutation: tuple[int, ...]) -> int:
    positions = edge_positions(order)
    answer = 0
    for bit, (left, right) in enumerate(edge_list(order)):
        if (mask >> bit) & 1:
            image = tuple(sorted((permutation[left], permutation[right])))
            answer |= 1 << positions[image]
    return answer


@lru_cache(maxsize=None)
def canonical_rooted(mask: int, order: int,
                     roots: tuple[int, ...] = ()) -> int:
    """Degree/signature-cell canonical form, with ordered roots fixed."""

    rows = adjacency(mask, order)
    root_set = set(roots)
    groups: dict[tuple[int, ...], list[int]] = defaultdict(list)
    for vertex in range(order):
        if vertex in root_set:
            continue
        signature = (
            rows[vertex].bit_count(),
            *(int(bool(rows[vertex] & (1 << root))) for root in roots),
        )
        groups[signature].append(vertex)
    choices = []
    start = len(roots)
    for signature in sorted(groups):
        sources = groups[signature]
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
        if best is None or candidate < best:
            best = candidate
    assert best is not None
    return best


def delete_vertex(mask: int, order: int,
                  deleted: int) -> tuple[int, dict[int, int]]:
    kept = tuple(vertex for vertex in range(order) if vertex != deleted)
    relabel = {old: new for new, old in enumerate(kept)}
    source_positions = edge_positions(order)
    answer = 0
    for target_bit, (left, right) in enumerate(itertools.combinations(kept, 2)):
        if (mask >> source_positions[(left, right)]) & 1:
            answer |= 1 << target_bit
    return answer, relabel


def extend_vertex(mask8: int, neighbors: tuple[int, ...]) -> int:
    answer = 0
    positions9 = edge_positions(9)
    for bit, edge in enumerate(edge_list(8)):
        if (mask8 >> bit) & 1:
            answer |= 1 << positions9[edge]
    for vertex in neighbors:
        answer |= 1 << positions9[(vertex, 8)]
    return answer


def pair_upper_ok(mask: int, order: int) -> bool:
    rows = adjacency(mask, order)
    for left, right in edge_list(order):
        common = (rows[left] & rows[right]).bit_count()
        target = 1 if rows[left] & (1 << right) else 2
        if common > target:
            return False
    return all(row.bit_count() <= 14 for row in rows)


def sparse(values: list[int]) -> list[list[int]]:
    return [[index, value] for index, value in enumerate(values) if value]


def rref_unique(matrix: list[list[int]], rhs: list[int], columns: int):
    rows = [
        [Fraction(value) for value in row] + [Fraction(value)]
        for row, value in zip(matrix, rhs)
    ]
    rank = 0
    pivots = []
    for column in range(columns):
        pivot = next(
            (row for row in range(rank, len(rows)) if rows[row][column]), None
        )
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][column]
        rows[rank] = [entry / scale for entry in rows[rank]]
        for row in range(len(rows)):
            if row == rank or not rows[row][column]:
                continue
            scale = rows[row][column]
            rows[row] = [
                entry - scale * pivot_entry
                for entry, pivot_entry in zip(rows[row], rows[rank])
            ]
        pivots.append(column)
        rank += 1
    assert rank == columns
    assert all(any(row[:-1]) or not row[-1] for row in rows)
    solution = [Fraction() for _ in range(columns)]
    for row, column in enumerate(pivots):
        solution[column] = rows[row][-1]
    return rank, solution


def matrix_rank(matrix: list[list[int]]) -> int:
    if not matrix:
        return 0
    rows = [[Fraction(value) for value in row] for row in matrix]
    rank = 0
    for column in range(len(rows[0])):
        pivot = next(
            (row for row in range(rank, len(rows)) if rows[row][column]), None
        )
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][column]
        rows[rank] = [value / scale for value in rows[rank]]
        for row in range(len(rows)):
            if row == rank or not rows[row][column]:
                continue
            scale = rows[row][column]
            rows[row] = [
                value - scale * pivot_value
                for value, pivot_value in zip(rows[row], rows[rank])
            ]
        rank += 1
    return rank


def show(value: Fraction | int) -> int | str:
    value = Fraction(value)
    return int(value) if value.denominator == 1 else str(value)


def outside_pattern_witness(mask: int) -> dict:
    """Solve the exact 0/1 first- and second-moment system on 90 points.

    A pattern S is the neighbourhood, inside the fixed H9, of one external
    vertex.  Pair residuals are at most two, so their support is decomposed
    into clique patterns.  Singleton and empty patterns then fill the first
    moments and the total number of external vertices.
    """

    rows = adjacency(mask, 9)
    pairs = edge_list(9)
    pair_index = {pair: index for index, pair in enumerate(pairs)}
    residual_degree = tuple(14 - row.bit_count() for row in rows)
    residual_pair = tuple(
        (1 if rows[left] & (1 << right) else 2)
        - (rows[left] & rows[right]).bit_count()
        for left, right in pairs
    )
    assert min(residual_pair) >= 0

    cliques = []
    for subset in range(1, 1 << 9):
        vertices = tuple(v for v in range(9) if subset & (1 << v))
        if len(vertices) < 2:
            continue
        covered = tuple(
            pair_index[pair] for pair in itertools.combinations(vertices, 2)
        )
        if all(residual_pair[index] for index in covered):
            cliques.append((subset, covered, vertices))
    by_pair = [[] for _ in pairs]
    for clique in cliques:
        for index in clique[1]:
            by_pair[index].append(clique)
    for choices in by_pair:
        choices.sort(key=lambda item: (-len(item[1]), item[0]))

    failed = set()

    def search(pair_need, used, incidence, selected):
        if not any(pair_need):
            singles = sum(
                residual_degree[v] - incidence[v] for v in range(9)
            )
            total = used + singles
            return (selected, incidence, total) if total <= 90 else None
        state = (pair_need, used, incidence)
        if state in failed:
            return None
        constrained = []
        for index, need in enumerate(pair_need):
            if not need:
                continue
            choices = [
                clique for clique in by_pair[index]
                if all(pair_need[pair] for pair in clique[1])
                and all(incidence[v] < residual_degree[v]
                        for v in clique[2])
            ]
            constrained.append((len(choices), index, choices))
        _, _, choices = min(constrained)
        for subset, covered, vertices in choices:
            next_need = list(pair_need)
            for index in covered:
                next_need[index] -= 1
            next_incidence = list(incidence)
            for vertex in vertices:
                next_incidence[vertex] += 1
            answer = search(
                tuple(next_need), used + 1, tuple(next_incidence),
                selected + (subset,),
            )
            if answer is not None:
                return answer
        failed.add(state)
        return None

    answer = search(residual_pair, 0, (0,) * 9, ())
    assert answer is not None
    selected, incidence, used = answer
    pattern_count = Counter(selected)
    for vertex in range(9):
        missing = residual_degree[vertex] - incidence[vertex]
        if missing:
            pattern_count[1 << vertex] += missing
    pattern_count[0] += 90 - used

    # Producer-side exact check.
    assert sum(pattern_count.values()) == 90
    assert tuple(
        sum(count for subset, count in pattern_count.items()
            if subset & (1 << vertex))
        for vertex in range(9)
    ) == residual_degree
    assert tuple(
        sum(count for subset, count in pattern_count.items()
            if subset & (1 << left) and subset & (1 << right))
        for left, right in pairs
    ) == residual_pair
    return {
        "internal_degrees": [row.bit_count() for row in rows],
        "residual_degrees": list(residual_degree),
        "residual_pair_common_neighbors": list(residual_pair),
        "nonzero_pattern_counts": [
            [subset, count] for subset, count in sorted(pattern_count.items())
            if count
        ],
        "external_vertices": 90,
        "feasible": True,
    }


def role_map(mark) -> dict[int, list[str]]:
    root_left, root_right, source_left, source_right, target_edge = mark
    result: dict[int, list[str]] = defaultdict(list)
    for vertex in source_left:
        result[vertex].append("source_left")
    for vertex in source_right:
        result[vertex].append("source_right")
    for vertex in target_edge:
        result[vertex].append("target_edge")
        result[vertex].append("target_triangle")
    result[8].extend(("mate", "target_triangle"))
    result[root_left].append("root_left")
    result[root_right].append("root_right")
    return {vertex: sorted(labels) for vertex, labels in result.items()}


def marked_coefficients(mask8: int, vertex_lookup: dict,
                        pair_lookup: dict) -> tuple[Counter, Counter]:
    """Enumerate the frozen marked H7->H8 coefficients for one H8."""

    rows8 = adjacency(mask8, 8)
    vertex_coefficients = Counter()
    pair_coefficients = Counter()
    for deleted in range(8):
        mask7, relabel = delete_vertex(mask8, 8, deleted)
        canonical7 = canonical_rooted(mask7, 7)
        neighbors = tuple(
            vertex for vertex in range(8)
            if vertex != deleted and rows8[deleted] & (1 << vertex)
        )
        for root in neighbors:
            key = canonical_rooted(mask7, 7, (relabel[root],))
            row = vertex_lookup[key]
            # The frozen order-seven stream uses its published representative,
            # not necessarily the minimum integer in our degree-cell labelling.
            assert canonical_rooted(int(row["order7_mask"]), 7) == canonical7
            vertex_coefficients[row["row_id"]] += 1
        for left in neighbors:
            for right in neighbors:
                if left == right:
                    continue
                key = canonical_rooted(
                    mask7, 7, (relabel[left], relabel[right])
                )
                row = pair_lookup[key]
                assert canonical_rooted(int(row["order7_mask"]), 7) == canonical7
                pair_coefficients[row["row_id"]] += 1
    return vertex_coefficients, pair_coefficients


def main() -> None:
    mate = json.loads(MATE.read_text(encoding="utf-8"))
    frozen = json.loads(WAVE147.read_text(encoding="utf-8"))
    marked = json.loads(gzip.decompress(MARKED.read_bytes()).decode("utf-8"))
    wave163 = json.loads(WAVE163.read_text(encoding="utf-8"))
    coefficients = json.loads(
        gzip.decompress(COEFFICIENTS.read_bytes()).decode("utf-8")
    )

    classes8 = tuple(
        int(mask) for mask in frozen["class_streams"]["8"]["canonical_masks"]
    )
    classes8_set = set(classes8)
    classes7 = tuple(
        int(row["order7_mask"])
        for row in coefficients["order7_to_order8_deletion_equations"]
    )
    assert len(classes7) == 208 and len(classes8) == 916
    assert len(marked["vertex_rows"]) == 944
    assert len(marked["ordered_pair_rows"]) == 4440

    visible_pairs = mate["marked_lift_schema"][
        "visible_order9_type_marked_weights"
    ]
    visible_masks = tuple(int(pair[0]) for pair in visible_pairs)
    assert len(visible_masks) == len(set(visible_masks)) == 19

    unmarked_decks = []
    shadows = set()
    for index, mask9 in enumerate(visible_masks):
        deletions = []
        histogram = Counter()
        for deleted in range(9):
            raw8, _ = delete_vertex(mask9, 9, deleted)
            canonical8 = canonical_rooted(raw8, 8)
            assert canonical8 in classes8_set
            histogram[canonical8] += 1
            shadows.add(canonical8)
            deletions.append({
                "deleted_vertex": deleted,
                "raw_order8_mask": raw8,
                "canonical_order8_mask": canonical8,
                "frozen_order8_index_0_based": classes8.index(canonical8),
            })
        unmarked_decks.append({
            "visible_h9_index": index,
            "canonical_order9_mask": mask9,
            "edge_count": mask9.bit_count(),
            "degree_sequence": sorted(
                row.bit_count() for row in adjacency(mask9, 9)
            ),
            "deletion_histogram": [
                [mask, count] for mask, count in sorted(histogram.items())
            ],
            "vertex_deletions": deletions,
        })
    assert len(shadows) == 39

    vertex_lookup = {int(row["rooted_key"]): row
                     for row in marked["vertex_rows"]}
    pair_lookup = {int(row["rooted_key"]): row
                   for row in marked["ordered_pair_rows"]}
    assert len(vertex_lookup) == 944 and len(pair_lookup) == 4440
    vertex_by_id = {row["row_id"]: row for row in marked["vertex_rows"]}
    pair_by_id = {row["row_id"]: row for row in marked["ordered_pair_rows"]}

    shadow_maps = []
    touched_vertex = set()
    touched_pair = set()
    for shadow in sorted(shadows):
        vertex_coeff, pair_coeff = marked_coefficients(
            shadow, vertex_lookup, pair_lookup
        )
        # Compare to the frozen columns, not just their support.
        for row_id, coefficient in vertex_coeff.items():
            stored = dict(vertex_by_id[row_id][
                "terms_order8_mask_coefficient"
            ]).get(str(shadow))
            if stored is None:
                stored = dict(vertex_by_id[row_id][
                    "terms_order8_mask_coefficient"
                ]).get(shadow, 0)
            assert int(stored) == coefficient
        for row_id, coefficient in pair_coeff.items():
            stored = dict(pair_by_id[row_id][
                "terms_order8_mask_coefficient"
            ]).get(str(shadow))
            if stored is None:
                stored = dict(pair_by_id[row_id][
                    "terms_order8_mask_coefficient"
                ]).get(shadow, 0)
            assert int(stored) == coefficient
        expected_vertex = {
            row["row_id"]: int(dict(row["terms_order8_mask_coefficient"])
                               .get(str(shadow),
                                    dict(row["terms_order8_mask_coefficient"])
                                    .get(shadow, 0)))
            for row in marked["vertex_rows"]
        }
        expected_pair = {
            row["row_id"]: int(dict(row["terms_order8_mask_coefficient"])
                               .get(str(shadow),
                                    dict(row["terms_order8_mask_coefficient"])
                                    .get(shadow, 0)))
            for row in marked["ordered_pair_rows"]
        }
        expected_vertex = Counter({k: v for k, v in expected_vertex.items() if v})
        expected_pair = Counter({k: v for k, v in expected_pair.items() if v})
        assert vertex_coeff == expected_vertex
        assert pair_coeff == expected_pair
        touched_vertex.update(vertex_coeff)
        touched_pair.update(pair_coeff)
        shadow_maps.append({
            "canonical_order8_mask": shadow,
            "vertex_marked_rows": sorted(vertex_coeff.items()),
            "ordered_pair_marked_rows": sorted(pair_coeff.items()),
        })

    # Every feasible labelled template, including all non-mate deletion slots.
    role_templates = []
    mate_slots = 0
    nonmate_slots = 0
    for row in mate["marked_lift_schema"]["rows"]:
        mark = row["representative_mark"]
        roles = role_map(mark)
        for extension in row["mate_bit_extensions"]:
            if not extension["pair_upper_feasible"]:
                continue
            labelled9 = int(extension["labelled_order9_mask"])
            visible9 = int(extension["degree_cell_canonical_order9_mask"])
            assert visible9 in visible_masks
            deletions = []
            for deleted in range(9):
                raw8, relabel = delete_vertex(labelled9, 9, deleted)
                canonical8 = canonical_rooted(raw8, 8)
                assert canonical8 in shadows
                survives = deleted == 8
                if survives:
                    mate_slots += 1
                    assert canonical8 == int(row["order8_canonical_mask"])
                else:
                    nonmate_slots += 1
                deletions.append({
                    "deleted_vertex": deleted,
                    "deleted_roles": roles[deleted],
                    "canonical_order8_mask": canonical8,
                    "full_original_X_X_flag_survives": survives,
                    "mate_delete_row_id": row["row_id"] if survives else None,
                    "surviving_roles": [
                        {
                            "original_vertex": vertex,
                            "order8_vertex": relabel[vertex],
                            "roles": roles[vertex],
                        }
                        for vertex in range(9) if vertex != deleted
                    ],
                    "frozen_nested_map_order8_mask": canonical8,
                })
            role_templates.append({
                "source_row_id": row["row_id"],
                "mate_bits": extension["mate_bits"],
                "labelled_order9_mask": labelled9,
                "visible_canonical_order9_mask": visible9,
                "vertex_deletions": deletions,
            })
    assert len(role_templates) == 33
    assert mate_slots == 33 and nonmate_slots == 264

    # Verify the frozen marked identities at the Wave163 integer point.
    x7 = {int(mask): int(count) for mask, count in
          wave163["integral_pseudocount"]["order7_mask_count_pairs"]}
    x8 = {int(mask): int(count) for mask, count in
          wave163["integral_pseudocount"]["order8_mask_count_pairs"]}
    vertex_residuals = []
    for row in marked["vertex_rows"]:
        lhs = int(row["lhs_coefficient"]) * x7[int(row["order7_mask"])]
        rhs = sum(int(coefficient) * x8[int(mask)]
                  for mask, coefficient in
                  row["terms_order8_mask_coefficient"])
        vertex_residuals.append(lhs - rhs)
    pair_residuals = []
    for row in marked["ordered_pair_rows"]:
        lhs = int(row["lhs_coefficient"]) * x7[int(row["order7_mask"])]
        rhs = sum(int(coefficient) * x8[int(mask)]
                  for mask, coefficient in
                  row["terms_order8_mask_coefficient"])
        pair_residuals.append(lhs - rhs)
    assert not any(vertex_residuals) and not any(pair_residuals)

    # Recover the Wave163 all-G H9 point from the eleven exact mate rows.
    t0 = mate["T0_all_G_order9_closure"]
    t0_masks = tuple(
        int(row["degree_cell_canonical_mask"])
        for row in t0["H9_mark_audit"]
    )
    assert len(t0_masks) == 9
    mate_by_id = {
        row["row_id"]: row for row in mate["marked_lift_schema"]["rows"]
    }
    matrix = []
    rhs = []
    for incidence in t0["incidence_rows"]:
        vector = [0] * 9
        for index, coefficient in incidence["H9_coefficients"]:
            vector[int(index)] = int(coefficient)
        source = mate_by_id[incidence["row_id"]]
        matrix.append(vector)
        rhs.append(
            int(source["marked_orbit_size"])
            * x8[int(source["order8_canonical_mask"])]
        )
    rank, h9 = rref_unique(matrix, rhs, 9)
    assert all(value.denominator == 1 and value >= 0 for value in h9)

    # Targeted projections of the genuine order-8-to-9 extension equations.
    # Coefficients are first formed on all 19 visible unmarked masks.  The
    # Wave163 candidate then places the nine all-G counts in their matching
    # columns and zero in the other ten visible columns.
    unmarked_coeff: dict[int, list[int]] = defaultdict(lambda: [0] * 19)
    vertex_coeff: dict[tuple[int, int], list[int]] = defaultdict(
        lambda: [0] * 19
    )
    pair_coeff: dict[tuple[int, int], list[int]] = defaultdict(
        lambda: [0] * 19
    )
    for hindex, mask9 in enumerate(visible_masks):
        rows9 = adjacency(mask9, 9)
        for deleted in range(9):
            raw8, relabel = delete_vertex(mask9, 9, deleted)
            canonical8 = canonical_rooted(raw8, 8)
            unmarked_coeff[canonical8][hindex] += 1
            neighbors = tuple(
                vertex for vertex in range(9)
                if vertex != deleted and rows9[deleted] & (1 << vertex)
            )
            for root in neighbors:
                key = canonical_rooted(raw8, 8, (relabel[root],))
                vertex_coeff[(canonical8, key)][hindex] += 1
            for left in neighbors:
                for right in neighbors:
                    if left == right:
                        continue
                    key = canonical_rooted(
                        raw8, 8, (relabel[left], relabel[right])
                    )
                    pair_coeff[(canonical8, key)][hindex] += 1

    visible_index = {mask: index for index, mask in enumerate(visible_masks)}
    t0_visible_indices = tuple(visible_index[mask] for mask in t0_masks)
    visible_candidate = [Fraction() for _ in range(19)]
    for t0_index, index19 in enumerate(t0_visible_indices):
        visible_candidate[index19] = h9[t0_index]

    extension_support_cache = {}

    def extension_support(mask8: int, required: tuple[int, ...]):
        """All locally pair-upper extensions for one rooted H8 orbit.

        Only the 2^(8-|required|) possible neighbourhoods of the new vertex
        are inspected.  This is a local completeness check for a targeted
        shadow, not an ambient H9 class census.
        """

        cache_key = (mask8, tuple(sorted(required)))
        if cache_key in extension_support_cache:
            return extension_support_cache[cache_key]
        remaining = tuple(v for v in range(8) if v not in required)
        support = set()
        omitted = None
        for extra_count in range(len(remaining) + 1):
            for extra in itertools.combinations(remaining, extra_count):
                neighbors = tuple(sorted(required + extra))
                candidate = extend_vertex(mask8, neighbors)
                if not pair_upper_ok(candidate, 9):
                    continue
                canonical9 = canonical_rooted(candidate, 9)
                support.add(canonical9)
                if canonical9 not in visible_masks and omitted is None:
                    omitted = {
                        "new_vertex_neighbors_in_canonical_H8": list(neighbors),
                        "omitted_canonical_order9_mask": canonical9,
                    }
        assert support
        answer = (tuple(sorted(support)), omitted)
        extension_support_cache[cache_key] = answer
        return answer

    def base_row(mask8, coefficients19, required):
        support, omitted = extension_support(mask8, required)
        all_g_coefficients = [coefficients19[index]
                              for index in t0_visible_indices]
        targeted = sum(
            visible_candidate[index] * coefficient
            for index, coefficient in enumerate(coefficients19)
        )
        return {
            "visible_19_H9_coefficients": sparse(coefficients19),
            "all_G_9_H9_coefficients": sparse(all_g_coefficients),
            "wave163_visible_19_candidate_rhs": show(targeted),
            "locally_admissible_extension_support_size": len(support),
            "closed_on_visible_19": omitted is None,
            "closed_support_visible_H9_indices": (
                [visible_index[mask] for mask in support]
                if omitted is None else None
            ),
            "omitted_extension_witness": omitted,
        }, targeted

    extension_rows = {"unmarked": [], "vertex": [], "ordered_pair": []}
    for mask8, coefficients19 in sorted(unmarked_coeff.items()):
        lhs = 91 * x8[mask8]
        common, targeted = base_row(mask8, coefficients19, ())
        slack = Fraction(lhs) - targeted
        assert slack >= 0 and slack.denominator == 1
        extension_rows["unmarked"].append({
            "canonical_order8_mask": mask8,
            "lhs_multiplier": 91,
            "wave163_lhs": lhs,
            "omitted_nonnegative_slack": show(slack),
            **common,
        })

    for (mask8, key), coefficients19 in sorted(vertex_coeff.items()):
        rows8 = adjacency(mask8, 8)
        roots = tuple(
            root for root in range(8)
            if canonical_rooted(mask8, 8, (root,)) == key
        )
        assert roots
        degree = rows8[roots[0]].bit_count()
        assert all(rows8[root].bit_count() == degree for root in roots)
        capacity = 14 - degree
        lhs = len(roots) * capacity * x8[mask8]
        common, targeted = base_row(mask8, coefficients19, (roots[0],))
        slack = Fraction(lhs) - targeted
        assert slack >= 0 and slack.denominator == 1
        extension_rows["vertex"].append({
            "canonical_order8_mask": mask8,
            "rooted_key": key,
            "root_orbit_size": len(roots),
            "internal_degree": degree,
            "outside_neighbor_capacity": capacity,
            "wave163_lhs": lhs,
            "omitted_nonnegative_slack": show(slack),
            **common,
        })

    for (mask8, key), coefficients19 in sorted(pair_coeff.items()):
        rows8 = adjacency(mask8, 8)
        pairs = tuple(
            (left, right)
            for left in range(8) for right in range(8) if left != right
            if canonical_rooted(mask8, 8, (left, right)) == key
        )
        assert pairs
        left, right = pairs[0]
        adjacent = bool(rows8[left] & (1 << right))
        common = (rows8[left] & rows8[right]).bit_count()
        capacity = (1 if adjacent else 2) - common
        assert capacity > 0
        lhs_multiplier = len(pairs) * capacity
        lhs = lhs_multiplier * x8[mask8]
        row_common, targeted = base_row(
            mask8, coefficients19, tuple(sorted((left, right)))
        )
        slack = Fraction(lhs) - targeted
        assert slack >= 0 and slack.denominator == 1
        coefficient_gcd = 0
        for coefficient in coefficients19:
            coefficient_gcd = math.gcd(coefficient_gcd, coefficient)
        congruence_modulus = coefficient_gcd // math.gcd(
            coefficient_gcd, lhs_multiplier
        )
        extension_rows["ordered_pair"].append({
            "canonical_order8_mask": mask8,
            "ordered_pair_rooted_key": key,
            "ordered_pair_orbit_size": len(pairs),
            "root_relation": "edge" if adjacent else "nonedge",
            "internal_common_neighbors": common,
            "outside_common_neighbor_capacity": capacity,
            "lhs_multiplier": lhs_multiplier,
            "wave163_lhs": lhs,
            "omitted_nonnegative_slack": show(slack),
            "visible_coefficient_gcd": coefficient_gcd,
            "necessary_x8_congruence_modulus_if_closed": (
                congruence_modulus if row_common["closed_on_visible_19"]
                else None
            ),
            **row_common,
        })

    flat_rows = [row for family in extension_rows.values() for row in family]
    tight = [row for row in flat_rows
             if int(row["omitted_nonnegative_slack"]) == 0]
    positive_tight = [row for row in tight if int(row["wave163_lhs"]) > 0]
    family_tight = {
        family: sum(int(row["omitted_nonnegative_slack"]) == 0
                    for row in rows)
        for family, rows in extension_rows.items()
    }
    family_positive_tight = {
        family: sum(
            int(row["omitted_nonnegative_slack"]) == 0
            and int(row["wave163_lhs"]) > 0
            for row in rows
        )
        for family, rows in extension_rows.items()
    }
    closed_pair_rows = [
        row for row in extension_rows["ordered_pair"]
        if row["closed_on_visible_19"]
    ]
    assert all(int(row["omitted_nonnegative_slack"]) == 0
               for row in closed_pair_rows)
    assert not any(row["closed_on_visible_19"]
                   for row in extension_rows["unmarked"])
    assert not any(row["closed_on_visible_19"]
                   for row in extension_rows["vertex"])
    mate_shadow_masks = {
        int(row["order8_canonical_mask"])
        for row in mate["marked_lift_schema"]["rows"]
    }
    nonmate_closed_rows = [
        row for row in closed_pair_rows
        if int(row["canonical_order8_mask"]) not in mate_shadow_masks
    ]
    closed_matrix19 = [
        [dict(row["visible_19_H9_coefficients"]).get(index, 0)
         for index in range(19)]
        for row in closed_pair_rows
    ]
    closed_matrix_GG = [
        [vector[index] for index in t0_visible_indices]
        for vector in closed_matrix19
    ]
    forced_zero_visible_indices = sorted({
        index
        for row, vector in zip(closed_pair_rows, closed_matrix19)
        if int(row["omitted_nonnegative_slack"]) == 0
        for index, coefficient in enumerate(vector)
        if coefficient and not visible_candidate[index]
    })
    other_visible_indices = sorted(
        set(range(19)) - set(t0_visible_indices)
    )
    assert set(other_visible_indices) <= set(forced_zero_visible_indices)
    congruence_rows = [
        row for row in closed_pair_rows
        if int(row["necessary_x8_congruence_modulus_if_closed"]) > 1
    ]
    # The only modulus is the already-published x8[110787152] parity row.
    assert {
        (int(row["canonical_order8_mask"]),
         int(row["necessary_x8_congruence_modulus_if_closed"]))
        for row in congruence_rows
    } == {(110787152, 2)}
    closed_rank19 = matrix_rank(closed_matrix19)
    closed_rank_GG = matrix_rank(closed_matrix_GG)
    combined_GG_rank = matrix_rank(matrix + closed_matrix_GG)
    unique_closed_coefficient_rows = len({
        tuple(vector) for vector in closed_matrix19
    })
    assert len(closed_pair_rows) == 21
    assert len(nonmate_closed_rows) == 8
    assert closed_rank19 == 11
    assert closed_rank_GG == combined_GG_rank == rank == 9
    assert unique_closed_coefficient_rows == 14

    outside_witnesses = [
        {
            "visible_h9_index": index,
            "canonical_order9_mask": mask,
            **outside_pattern_witness(mask),
        }
        for index, mask in enumerate(visible_masks)
    ]

    result = {
        "status": "proved-targeted-deck-survives",
        "scope": {
            "ambient_order9_census_generated": False,
            "frozen_order8_classes_regenerated": False,
            "marked_identities_regenerated": False,
            "visible_order9_masks_only": 19,
            "submission_txt_written": False,
        },
        "inputs": {
            str(path): {"sha256": sha256(path)}
            for path in (MATE, WAVE147, COEFFICIENTS, MARKED, WAVE163)
        },
        "frozen_dimensions": {
            "order7_classes": len(classes7),
            "order8_classes": len(classes8),
            "marked_vertex_rows": len(marked["vertex_rows"]),
            "marked_ordered_pair_rows": len(marked["ordered_pair_rows"]),
        },
        "unmarked_targeted_deck": {
            "visible_order9_masks": len(visible_masks),
            "vertex_deletion_slots": 19 * 9,
            "distinct_frozen_order8_shadows": len(shadows),
            "all_shadows_in_frozen_916": True,
            "decks": unmarked_decks,
        },
        "role_preserving_targeted_deck": {
            "feasible_labelled_templates": len(role_templates),
            "all_vertex_deletion_slots": len(role_templates) * 9,
            "mate_deletion_slots": mate_slots,
            "nonmate_deletion_slots": nonmate_slots,
            "full_original_X_X_flag_survives_only_mate_deletion": True,
            "reason": (
                "The two disjoint source triangles and the target triangle "
                "partition all nine displayed vertices.  Deleting any "
                "non-mate removes a required source/root/target role; deleting "
                "the mate alone leaves the marked target edge used by the 11 "
                "published rows."
            ),
            "templates": role_templates,
        },
        "frozen_marked_identity_map": {
            "semantics": (
                "For each of the 39 H8 shadows, delete a second vertex and "
                "retain one marked neighbor or an ordered pair of marked "
                "common-neighbors.  The resulting coefficient is compared "
                "exactly with the frozen Wave148 H7-to-H8 row."
            ),
            "distinct_shadow_columns": len(shadow_maps),
            "touched_marked_vertex_rows": len(touched_vertex),
            "touched_marked_ordered_pair_rows": len(touched_pair),
            "all_recomputed_shadow_coefficients_match_frozen_rows": True,
            "wave163_all_944_vertex_identities_hold": True,
            "wave163_all_4440_pair_identities_hold": True,
            "shadow_maps": shadow_maps,
        },
        "T0_all_G_targeted_order9_projection": {
            "H9_masks": list(t0_masks),
            "visible_19_H9_masks": list(visible_masks),
            "all_G_indices_in_visible_19": list(t0_visible_indices),
            "mate_delete_matrix_shape": [len(matrix), 9],
            "mate_delete_rank_over_Q": rank,
            "wave163_unique_H9_counts": [show(value) for value in h9],
            "wave163_visible_19_candidate_counts": [
                show(value) for value in visible_candidate
            ],
            "all_counts_nonnegative_integral": True,
            "extension_identity_semantics": (
                "Each row is a genuine order-8-to-9 counting identity after "
                "adding any omitted H9 columns.  Coefficients of all 19 visible "
                "masks are displayed.  A local 2^(8-r) neighbourhood scan "
                "proves exactly which rooted-pair rows close on those 19; an "
                "open row retains its omitted columns as nonnegative slack."
            ),
            "row_counts": {family: len(rows)
                           for family, rows in extension_rows.items()},
            "all_projected_slacks_nonnegative_integral": True,
            "tight_row_counts": family_tight,
            "positive_lhs_tight_row_counts": family_positive_tight,
            "positive_lhs_tight_rows_force_all_omitted_extensions_zero": len(
                positive_tight
            ),
            "closed_pair_rooted_rows_on_visible_19": len(closed_pair_rows),
            "unique_closed_pair_coefficient_equations": (
                unique_closed_coefficient_rows
            ),
            "closed_pair_matrix_rank_on_visible_19": closed_rank19,
            "closed_pair_matrix_rank_on_all_G_9": closed_rank_GG,
            "combined_mate_and_closed_pair_rank_on_all_G_9": (
                combined_GG_rank
            ),
            "new_all_G_rank_beyond_mate_delete": combined_GG_rank - rank,
            "closed_rows_from_nonmate_shadow_classes": len(
                nonmate_closed_rows
            ),
            "distinct_nonmate_shadow_classes_in_closed_rows": sorted({
                int(row["canonical_order8_mask"])
                for row in nonmate_closed_rows
            }),
            "forced_zero_visible_19_indices_at_wave163": (
                forced_zero_visible_indices
            ),
            "forced_zero_visible_19_masks_at_wave163": [
                visible_masks[index] for index in forced_zero_visible_indices
            ],
            "all_ten_non_all_G_visible_columns_forced_zero": True,
            "closed_row_congruences": [
                {
                    "canonical_order8_mask": int(
                        row["canonical_order8_mask"]
                    ),
                    "modulus": int(
                        row["necessary_x8_congruence_modulus_if_closed"]
                    ),
                    "already_present_in_mate_delete_lane": True,
                }
                for row in congruence_rows
            ],
            "rows": extension_rows,
        },
        "outside_neighborhood_first_second_moment_feasibility": {
            "system": [
                "sum_S n_S = 90",
                "sum_{S contains i} n_S = 14-d_H(i)",
                "sum_{S contains i,j} n_S = lambda_or_mu-c_H(i,j)",
                "n_S are nonnegative integers for S subset of the 9 vertices",
            ],
            "all_19_feasible": True,
            "witnesses": outside_witnesses,
            "scope_boundary": (
                "This is exactly the requested one-level neighbourhood-pattern "
                "test.  It does not assert that the remaining degrees and pair "
                "conditions inside the 90 external vertices can be completed."
            ),
        },
        "logical_conclusion": {
            "closed_pair_exact_rows_total": len(closed_pair_rows),
            "closed_exact_rows_from_nonmate_deletion_shadows": len(
                nonmate_closed_rows
            ),
            "new_independent_rank_on_the_nine_GG_variables": 0,
            "new_congruences_certified": 0,
            "new_visible_non_all_G_zero_cells_at_wave163": len(
                other_visible_indices
            ),
            "positive_lhs_zero_slack_rows": len(positive_tight),
            "wave163_nonnegative_targeted_extension_survives": True,
            "qualification": (
                "All 21 closed pair-rooted identities hold exactly.  The ten "
                "visible columns outside the all-G nine are forced to zero, "
                "while the nine all-G values remain the nonnegative integral "
                "mate-delete solution.  Open unmarked/vertex/pair rows use one "
                "projected nonnegative omitted-column slack each; simultaneous "
                "ambient realization of those open-row slacks is not claimed."
            ),
            "exact_boundary": (
                "No unmarked or vertex-rooted extension row closes on the 19. "
                "Exactly 21 ordered-pair-rooted rows do close; 8 use shadows "
                "absent from the mate-delete list.  Their GG restriction adds "
                "no rank to the already full-rank 11-by-9 mate system.  Their "
                "only nontrivial x8 congruence is the already-known parity of "
                "x8[110787152]."
            ),
        },
    }
    atomic_json(OUTPUT, result)
    print(json.dumps({
        "output": str(OUTPUT),
        "visible_masks": len(visible_masks),
        "shadows": len(shadows),
        "role_templates": len(role_templates),
        "touched_vertex_rows": len(touched_vertex),
        "touched_pair_rows": len(touched_pair),
        "T0_h9": [show(value) for value in h9],
        "extension_rows": {family: len(rows)
                           for family, rows in extension_rows.items()},
        "tight": family_tight,
        "positive_tight": family_positive_tight,
        "outside_feasible": len(outside_witnesses),
    }, indent=2))


if __name__ == "__main__":
    main()
