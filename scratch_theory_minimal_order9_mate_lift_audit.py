"""Independent replay of the restricted marked mate/status lift.

The audit intentionally does not import the producer.  It reconstructs the
twenty ordered shadow marks, their automorphism orbits, all four visible mate
extensions, and the T=0 X-X incidence matrix directly from edge sets.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import os
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path


ARTIFACT = Path("scratch_theory_minimal_order9_mate_lift.json")
SHADOW = Path("scratch_theory_root_yyt_order8_shadow.json")
PAIR_TYPES = Path("scratch_theory_root_yyt_pair_classification.json")
WAVE159 = Path(
    "external_conway99_research/attempts/wave159-four-root-cut-loop/"
    "exact-witness-after-fifteen-cuts.json"
)
OUTPUT = Path("scratch_theory_minimal_order9_mate_lift_audit.json")


def atomic_json(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def norm(left: int, right: int) -> tuple[int, int]:
    return min(left, right), max(left, right)


def positions(order: int):
    return {edge: bit for bit, edge in enumerate(itertools.combinations(range(order), 2))}


def decode(mask: int, order: int):
    return frozenset(edge for edge, bit in positions(order).items() if mask >> bit & 1)


def encode(edges, order: int):
    table = positions(order)
    return sum(1 << table[norm(*edge)] for edge in edges)


def graph(order: int, edges):
    rows = [set() for _ in range(order)]
    for left, right in edges:
        rows[left].add(right)
        rows[right].add(left)
    return tuple(frozenset(row) for row in rows)


def triangle_rows(order: int, edges):
    rows = graph(order, edges)
    return tuple(
        triple for triple in itertools.combinations(range(order), 3)
        if all(right in rows[left] for left, right in itertools.combinations(triple, 2))
    )


def valid_two_matching(rows, source, root, target):
    others = [vertex for vertex in source if vertex != root]
    return (
        all(vertex not in rows[root] for vertex in target)
        and sorted(sum(vertex in rows[source_vertex] for vertex in target)
                   for source_vertex in others) == [1, 1]
        and sorted(sum(source_vertex in rows[vertex] for source_vertex in others)
                   for vertex in target) == [1, 1]
    )


def enumerate_base_marks(mask: int, adjacent: bool):
    edges = decode(mask, 8)
    rows = graph(8, edges)
    tris = triangle_rows(8, edges)
    vertices = set(range(8))
    answer = []
    for left in range(8):
        for right in range(8):
            if left == right or ((right in rows[left]) != adjacent):
                continue
            for source_left in tris:
                if left not in source_left:
                    continue
                for source_right in tris:
                    if right not in source_right or set(source_left) & set(source_right):
                        continue
                    target = tuple(sorted(vertices - set(source_left) - set(source_right)))
                    if len(target) != 2 or target[1] not in rows[target[0]]:
                        continue
                    if (valid_two_matching(rows, source_left, left, target)
                            and valid_two_matching(rows, source_right, right, target)):
                        answer.append((left, right, tuple(source_left),
                                       tuple(source_right), target))
    return frozenset(answer)


def mark_tuple(stored):
    return (int(stored[0]), int(stored[1]), tuple(map(int, stored[2])),
            tuple(map(int, stored[3])), tuple(map(int, stored[4])))


def move_mark(mark, permutation):
    return (
        permutation[mark[0]], permutation[mark[1]],
        tuple(sorted(permutation[vertex] for vertex in mark[2])),
        tuple(sorted(permutation[vertex] for vertex in mark[3])),
        tuple(sorted(permutation[vertex] for vertex in mark[4])),
    )


def automorphisms(mask: int):
    edges = decode(mask, 8)
    rows = graph(8, edges)
    degrees = [len(row) for row in rows]
    groups = defaultdict(list)
    for vertex, degree in enumerate(degrees):
        groups[degree].append(vertex)
    blocks = tuple(groups[degree] for degree in sorted(groups))
    answer = []
    for choices in itertools.product(*(
            tuple(itertools.permutations(block)) for block in blocks)):
        permutation = list(range(8))
        for source_block, image_block in zip(blocks, choices):
            for source, image in zip(source_block, image_block):
                permutation[source] = image
        image_edges = frozenset(norm(permutation[left], permutation[right])
                                for left, right in edges)
        if image_edges == edges:
            answer.append(tuple(permutation))
    return tuple(answer)


def violations(order: int, edges):
    rows = graph(order, edges)
    result = []
    for left, right in itertools.combinations(range(order), 2):
        common = sorted(rows[left] & rows[right])
        upper = 1 if right in rows[left] else 2
        if len(common) > upper:
            result.append((left, right, tuple(common), upper))
    return tuple(result)


def degree_mask(order: int, edges):
    rows = graph(order, edges)
    groups = defaultdict(list)
    for vertex, row in enumerate(rows):
        groups[len(row)].append(vertex)
    target = 0
    blocks = []
    for degree in sorted(groups):
        source = groups[degree]
        destinations = tuple(range(target, target + len(source)))
        target += len(source)
        blocks.append((source, destinations))
    best = None
    for choices in itertools.product(*(
            tuple(itertools.permutations(destinations))
            for _, destinations in blocks)):
        permutation = list(range(order))
        for (sources, _), destinations in zip(blocks, choices):
            for source, destination in zip(sources, destinations):
                permutation[source] = destination
        value = encode((norm(permutation[left], permutation[right])
                        for left, right in edges), order)
        best = value if best is None else min(best, value)
    return best


def canonical_mark(order: int, edges, mark):
    rows = graph(order, edges)
    groups = defaultdict(list)
    for vertex, row in enumerate(rows):
        groups[len(row)].append(vertex)
    target = 0
    blocks = []
    for degree in sorted(groups):
        sources = groups[degree]
        destinations = tuple(range(target, target + len(sources)))
        target += len(sources)
        blocks.append((sources, destinations))
    best = None
    for choices in itertools.product(*(
            tuple(itertools.permutations(destinations))
            for _, destinations in blocks)):
        permutation = list(range(order))
        for (sources, _), destinations in zip(blocks, choices):
            for source, destination in zip(sources, destinations):
                permutation[source] = destination
        candidate = (encode((norm(permutation[left], permutation[right])
                             for left, right in edges), order),
                     move_mark(mark, permutation))
        best = candidate if best is None else min(best, candidate)
    return best


def x_relation(source, source_root, target, mate, edges):
    cross = {norm(left, right) for left in source for right in target
             if norm(left, right) in edges}
    used_source = {vertex for edge in cross for vertex in edge if vertex in source}
    used_target = {vertex for edge in cross for vertex in edge if vertex in target}
    return (len(cross) == 2
            and used_source == set(source) - {source_root}
            and used_target == set(target) - {mate})


def all_xx_marks(edges):
    tris = triangle_rows(9, edges)
    answer = []
    for root_left in range(9):
        for root_right in range(9):
            if root_left == root_right:
                continue
            for source_left in tris:
                if root_left not in source_left:
                    continue
                for source_right in tris:
                    if root_right not in source_right or set(source_left) & set(source_right):
                        continue
                    for target in tris:
                        if set(target) & (set(source_left) | set(source_right)):
                            continue
                        for mate in target:
                            if (x_relation(source_left, root_left, target, mate, edges)
                                    and x_relation(source_right, root_right,
                                                   target, mate, edges)):
                                answer.append((root_left, root_right, source_left,
                                               source_right, target, mate))
    return tuple(answer)


def delete_mate(edges, record):
    root_left, root_right, source_left, source_right, target, mate = record
    keep = [vertex for vertex in range(9) if vertex != mate]
    relabel = {vertex: index for index, vertex in enumerate(keep)}
    reduced_edges = frozenset(norm(relabel[left], relabel[right])
                              for left, right in edges if mate not in (left, right))
    reduced_mark = (
        relabel[root_left], relabel[root_right],
        tuple(sorted(relabel[vertex] for vertex in source_left)),
        tuple(sorted(relabel[vertex] for vertex in source_right)),
        tuple(sorted(relabel[vertex] for vertex in target if vertex != mate)),
    )
    return reduced_edges, reduced_mark


def matrix_rank(matrix):
    rows = [[Fraction(value) for value in row] for row in matrix]
    rank = 0
    for column in range(len(rows[0])):
        pivot = next((row for row in range(rank, len(rows)) if rows[row][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][column]
        rows[rank] = [value / scale for value in rows[rank]]
        for row in range(len(rows)):
            if row != rank and rows[row][column]:
                scale = rows[row][column]
                rows[row] = [left - scale * right
                             for left, right in zip(rows[row], rows[rank])]
        rank += 1
    return rank


def main() -> None:
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    shadow = json.loads(SHADOW.read_text(encoding="utf-8"))
    pair_types = json.loads(PAIR_TYPES.read_text(encoding="utf-8"))
    wave = json.loads(WAVE159.read_text(encoding="utf-8"))
    assert data["status"] == "MINIMAL_ORDER9_MATE_DOUBLED_STATUS_LIFT_PASS"
    rows = data["marked_lift_schema"]["rows"]

    expected_coefficients = {
        family: {int(mask): int(value) for mask, value in
                 shadow["shadow_coefficients"][family]["nonzero_order8_coefficients"]}
        for family in ("ordered_edge", "ordered_nonedge")
    }
    seen_marks = {}
    allowed_cells = raw_slots = allowed_slots = 0
    visible = Counter()
    for row in rows:
        family = row["family"]
        mask = int(row["order8_canonical_mask"])
        representative = mark_tuple(row["representative_mark"])
        base_marks = enumerate_base_marks(mask, family == "ordered_edge")
        assert representative in base_marks
        actions = automorphisms(mask)
        orbit = frozenset(move_mark(representative, action) for action in actions)
        assert orbit <= base_marks
        assert len(orbit) == int(row["marked_orbit_size"])
        assert len(actions) == int(row["automorphism_group_size"])
        assert len(orbit) * int(row["marked_stabilizer_size"]) == len(actions)
        seen_marks.setdefault((family, mask), set()).update(orbit)

        feasibility = {}
        for extension in row["mate_bit_extensions"]:
            left_bit, right_bit = map(int, extension["mate_bits"])
            edges = set(decode(mask, 8))
            edges.update((norm(8, representative[4][0]),
                          norm(8, representative[4][1])))
            if left_bit:
                edges.add(norm(8, representative[0]))
            if right_bit:
                edges.add(norm(8, representative[1]))
            edges = frozenset(edges)
            direct_violations = violations(9, edges)
            assert encode(edges, 9) == int(extension["labelled_order9_mask"])
            assert degree_mask(9, edges) == int(
                extension["degree_cell_canonical_order9_mask"]
            )
            assert encode((edge for edge in edges if 8 not in edge), 8) == mask
            target = representative[4]
            assert graph(9, edges)[target[0]] & graph(9, edges)[target[1]] == {8}
            assert bool(direct_violations) != bool(extension["pair_upper_feasible"])
            feasibility[f"{left_bit}{right_bit}"] = not direct_violations
            if not direct_violations:
                visible[int(extension["degree_cell_canonical_order9_mask"])] += len(orbit)

        direct_allowed = []
        for left, right in itertools.product("GDP", repeat=2):
            bit_key = f"{int(left == 'P')}{int(right == 'P')}"
            if feasibility[bit_key]:
                direct_allowed.append(left + right)
                allowed_slots += len(orbit)
            raw_slots += len(orbit)
            left_state = data["rooted_state_definition"]["states"][left]
            right_state = data["rooted_state_definition"]["states"][right]
            expected_weight = Fraction(
                int(left_state["selected"]) * int(right_state["selected"]),
                int(left_state["Yhat"]) * int(right_state["Yhat"]),
            )
            stored = next(record for record in data["rooted_state_definition"][
                "state_pairs"] if record["pair"] == left + right)
            assert Fraction(stored["selected_pair_weight_per_occurrence"]) == expected_weight
        assert direct_allowed == row["allowed_state_pairs"]
        allowed_cells += len(direct_allowed)

    for (family, mask), marked in seen_marks.items():
        complete = enumerate_base_marks(mask, family == "ordered_edge")
        assert marked == set(complete)
        assert len(marked) == expected_coefficients[family][mask]
    assert len(rows) == 11 and sum(map(len, seen_marks.values())) == 20
    assert allowed_cells == 82 and raw_slots == 180 and allowed_slots == 158
    assert dict(sorted(visible.items())) == {
        int(mask): int(weight) for mask, weight in
        data["marked_lift_schema"]["visible_order9_type_marked_weights"]
    }

    # Rebuild the all-G unmarked H9 incidence matrix by deleting each
    # explicitly marked mate and classifying the remaining marked K8.
    marked_lookup = {}
    for index, row in enumerate(rows):
        base_edges = decode(int(row["order8_canonical_mask"]), 8)
        representative = mark_tuple(row["representative_mark"])
        key = canonical_mark(8, base_edges, representative)
        assert key not in marked_lookup
        marked_lookup[key] = index
    h9_rows = pair_types["H9_disjoint_source_types"]
    incidence = [[0] * len(h9_rows) for _ in rows]
    for column, h9 in enumerate(h9_rows):
        edges = frozenset(norm(*edge) for edge in h9["representative_edges"])
        marks = all_xx_marks(edges)
        expected = 2 * (int(h9["adjacent_root_mark_multiplicity"])
                        + int(h9["nonadjacent_root_mark_multiplicity"]))
        assert len(marks) == expected
        for record in marks:
            reduced_edges, reduced_mark = delete_mate(edges, record)
            row = marked_lookup[canonical_mark(8, reduced_edges, reduced_mark)]
            incidence[row][column] += 1
    stored_incidence = [
        [next((int(value) for stored_column, value in
               row["T0_GG_unmarked_H9_coefficients"]
               if int(stored_column) == column), 0)
         for column in range(len(h9_rows))]
        for row in rows
    ]
    assert incidence == stored_incidence
    assert matrix_rank(incidence) == 9

    wave_counts = {int(row["canonical_mask"]): Fraction(row["count"])
                   for row in wave["x8_support"]}
    right_hand_side = [int(row["marked_orbit_size"])
                       * wave_counts.get(int(row["order8_canonical_mask"]), Fraction())
                       for row in rows]
    solution = [Fraction(row["count"]) for row in
                data["T0_all_G_order9_closure"][
                    "wave159_exact_nonnegative_H9_solution"]]
    assert all(value >= 0 for value in solution)
    assert [sum(Fraction(value) * solution[column]
                for column, value in enumerate(matrix_row))
            for matrix_row in incidence] == right_hand_side
    ordered_mass = sum(right_hand_side, Fraction())
    assert ordered_mass == 91476
    gram = [[Fraction(0) for _ in range(3)] for _ in range(3)]
    gram[0][0] = ordered_mass + 8316
    assert gram == [[99792, 0, 0], [0, 0, 0], [0, 0, 0]]
    assert all(gram[index][index] >= 0 for index in range(3))

    result = {
        "status": "MINIMAL_ORDER9_MATE_DOUBLED_STATUS_LIFT_INDEPENDENT_AUDIT_PASS",
        "input_sha256": {
            str(path): sha256(path) for path in (ARTIFACT, SHADOW, PAIR_TYPES, WAVE159)
        },
        "ordered_shadow_marks_rebuilt": sum(map(len, seen_marks.values())),
        "marked_automorphism_orbits_rebuilt": len(rows),
        "raw_tagged_orbit_cells": len(rows) * 9,
        "allowed_tagged_orbit_cells": allowed_cells,
        "raw_tagged_marked_slots": raw_slots,
        "allowed_tagged_marked_slots": allowed_slots,
        "visible_order9_types": len(visible),
        "T0_H9_incidence_shape": [len(incidence), len(incidence[0])],
        "T0_H9_incidence_rank_over_Q": matrix_rank(incidence),
        "T0_exact_nonnegative_solution_replayed": True,
        "T0_ordered_shadow_mass": int(ordered_mass),
        "T0_selected_collision": 0,
        "T0_state_Gram": [
            [int(value) if value.denominator == 1 else str(value) for value in row]
            for row in gram
        ],
        "T0_excluded": False,
        "checks": {
            "base_mark_enumeration_independent": True,
            "automorphism_orbits_partition_every_mark": True,
            "all_four_mate_bits_rebuilt_per_orbit": True,
            "all_deletion_masks_exact": True,
            "all_pair_upper_cells_rebuilt": True,
            "all_G_H9_deletion_incidence_rebuilt": True,
            "producer_not_imported": True,
        },
        "scope": (
            "This replays the restricted marked extension and its T=0 face. "
            "It neither enumerates all order-nine classes nor certifies a "
            "doubled-status packet as an induced order-nine graph."
        ),
    }
    atomic_json(OUTPUT, result)
    print(json.dumps({
        "status": result["status"],
        "marks": result["ordered_shadow_marks_rebuilt"],
        "allowed_cells": allowed_cells,
        "T0_excluded": False,
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
