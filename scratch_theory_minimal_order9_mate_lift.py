"""Restricted marked order-9 lift for the edge-fibre selector.

This is deliberately *not* a census of all graphs on nine vertices.  It
starts with the nine frozen Wave147 order-eight classes which occur in the
two-root shadow, keeps the two source flags and the target edge marked, and
adds only the unique triangle mate of that edge.  The mate bits and the
three possible nonzero root states

    G=(m,Y,s)=(0,1,0), D=(0,2,1), P=(1,1,1)

are enough to recover s[r,e]s[t,e] exactly from occurrence counts.  A D tag
is a status tag (its second source flag is outside the nine displayed
vertices); the file records the precise order-11/13 synchronization which
would be needed to turn those tags into ordinary unmarked graph columns.

The producer also closes the T=0, all-G face against the already audited
nine X-X H9 types.  This gives genuine order-8-to-9 deletion equations and
tests the Wave159 endpoint without generating any new ambient graph class.
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
from pathlib import Path


OUTPUT = Path("scratch_theory_minimal_order9_mate_lift.json")
COEFFICIENTS = Path(
    "external_conway99_research/attempts/wave147-alternative-lane/"
    "coefficients.json.gz"
)
MARKED_ROWS = Path(
    "external_conway99_research/attempts/wave148-marked-order8/"
    "marked-rows.json.gz"
)
SHADOW = Path("scratch_theory_root_yyt_order8_shadow.json")
PAIR_TYPES = Path("scratch_theory_root_yyt_pair_classification.json")
AUGMENTED = Path("scratch_theory_root_yyt_augmented_relation.json")
BOUNDARY = Path("scratch_theory_edge_shadow_lower_coupling_boundary.json")
WAVE159 = Path(
    "external_conway99_research/attempts/wave159-four-root-cut-loop/"
    "exact-witness-after-fifteen-cuts.json"
)

STATES = {
    "G": {"mate_bit": 0, "Yhat": 1, "selected": 0,
          "meaning": "one good X source flag"},
    "D": {"mate_bit": 0, "Yhat": 2, "selected": 1,
          "meaning": "two good X source flags (diagonal/doubled)"},
    "P": {"mate_bit": 1, "Yhat": 1, "selected": 1,
          "meaning": "one prism source flag"},
}


def atomic_json(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def show_fraction(value: Fraction) -> int | str:
    return int(value) if value.denominator == 1 else str(value)


def normal(left: int, right: int) -> tuple[int, int]:
    return (left, right) if left < right else (right, left)


def edge_positions(order: int) -> dict[tuple[int, int], int]:
    return {
        edge: bit for bit, edge in enumerate(itertools.combinations(range(order), 2))
    }


def edges_from_mask(mask: int, order: int) -> frozenset[tuple[int, int]]:
    return frozenset(
        edge for edge, bit in edge_positions(order).items() if (mask >> bit) & 1
    )


def mask_from_edges(edges: set[tuple[int, int]] | frozenset[tuple[int, int]],
                    order: int) -> int:
    positions = edge_positions(order)
    return sum(1 << positions[normal(*edge)] for edge in edges)


def adjacency(order: int, edges: frozenset[tuple[int, int]]):
    rows = [set() for _ in range(order)]
    for left, right in edges:
        rows[left].add(right)
        rows[right].add(left)
    return tuple(frozenset(row) for row in rows)


def triangles(order: int, edges: frozenset[tuple[int, int]]):
    graph = adjacency(order, edges)
    return tuple(
        triple for triple in itertools.combinations(range(order), 3)
        if all(right in graph[left] for left, right in itertools.combinations(triple, 2))
    )


def pair_upper_violations(order: int, edges: frozenset[tuple[int, int]]):
    graph = adjacency(order, edges)
    answer = []
    for left, right in itertools.combinations(range(order), 2):
        common = sorted(graph[left] & graph[right])
        target = 1 if right in graph[left] else 2
        if len(common) > target:
            answer.append({
                "pair": [left, right],
                "adjacent": right in graph[left],
                "common_neighbours": common,
                "upper": target,
            })
    return answer


def degrees(order: int, edges: frozenset[tuple[int, int]]):
    answer = [0] * order
    for left, right in edges:
        answer[left] += 1
        answer[right] += 1
    return tuple(answer)


def degree_cell_permutations(order: int, edges: frozenset[tuple[int, int]]):
    """Wave147 degree-cell permutations, as source-to-target maps."""

    groups: dict[int, list[int]] = defaultdict(list)
    for vertex, degree in enumerate(degrees(order, edges)):
        groups[degree].append(vertex)
    start = 0
    choices = []
    for degree in sorted(groups):
        sources = groups[degree]
        targets = tuple(range(start, start + len(sources)))
        start += len(sources)
        choices.append(tuple(
            dict(zip(sources, images)) for images in itertools.permutations(targets)
        ))
    for selection in itertools.product(*choices):
        permutation = [None] * order
        for partial in selection:
            for source, target in partial.items():
                permutation[source] = target
        yield tuple(permutation)


def transform_edges(edges: frozenset[tuple[int, int]], permutation):
    return frozenset(normal(permutation[left], permutation[right])
                     for left, right in edges)


def transform_mark(mark, permutation):
    root_left, root_right, source_left, source_right, target_edge = mark
    return (
        permutation[root_left],
        permutation[root_right],
        tuple(sorted(permutation[vertex] for vertex in source_left)),
        tuple(sorted(permutation[vertex] for vertex in source_right)),
        tuple(sorted(permutation[vertex] for vertex in target_edge)),
    )


def canonical_degree_mask(order: int, edges: frozenset[tuple[int, int]]) -> int:
    return min(mask_from_edges(transform_edges(edges, permutation), order)
               for permutation in degree_cell_permutations(order, edges))


def canonical_marked(order: int, edges: frozenset[tuple[int, int]], mark):
    """Canonical graph mask and canonical marked-orbit key."""

    candidates = []
    best_mask = None
    for permutation in degree_cell_permutations(order, edges):
        transformed = transform_edges(edges, permutation)
        mask = mask_from_edges(transformed, order)
        if best_mask is None or mask < best_mask:
            best_mask = mask
            candidates = [transform_mark(mark, permutation)]
        elif mask == best_mask:
            candidates.append(transform_mark(mark, permutation))
    assert best_mask is not None and candidates
    return best_mask, min(candidates)


def automorphisms(order: int, edges: frozenset[tuple[int, int]]):
    degree_groups: dict[int, list[int]] = defaultdict(list)
    for vertex, degree in enumerate(degrees(order, edges)):
        degree_groups[degree].append(vertex)
    result = []
    groups = tuple(degree_groups[degree] for degree in sorted(degree_groups))
    for choices in itertools.product(*(
            tuple(itertools.permutations(group)) for group in groups)):
        permutation = list(range(order))
        for sources, images in zip(groups, choices):
            for source, image in zip(sources, images):
                permutation[source] = image
        if transform_edges(edges, permutation) == edges:
            result.append(tuple(permutation))
    return tuple(result)


def is_two_cross_matching(graph, source, root, target_edge):
    nonroots = tuple(vertex for vertex in source if vertex != root)
    if any(target in graph[root] for target in target_edge):
        return False
    return (
        all(sum(target in graph[vertex] for target in target_edge) == 1
            for vertex in nonroots)
        and all(sum(target in graph[vertex] for vertex in nonroots) == 1
                for target in target_edge)
    )


def shadow_embeddings(mask: int, root_edge: bool):
    order = 8
    edges = edges_from_mask(mask, order)
    graph = adjacency(order, edges)
    triangle_rows = triangles(order, edges)
    vertices = set(range(order))
    answer = []
    for root_left in range(order):
        for root_right in range(order):
            if root_left == root_right:
                continue
            if (root_right in graph[root_left]) != root_edge:
                continue
            for source_left in triangle_rows:
                if root_left not in source_left:
                    continue
                for source_right in triangle_rows:
                    if root_right not in source_right:
                        continue
                    if set(source_left) & set(source_right):
                        continue
                    target_edge = tuple(sorted(
                        vertices - set(source_left) - set(source_right)
                    ))
                    if len(target_edge) != 2 or target_edge[1] not in graph[target_edge[0]]:
                        continue
                    if (is_two_cross_matching(graph, source_left, root_left, target_edge)
                            and is_two_cross_matching(
                                graph, source_right, root_right, target_edge
                            )):
                        answer.append((root_left, root_right, tuple(source_left),
                                       tuple(source_right), target_edge))
    return tuple(answer)


def marked_orbits(mask: int, root_edge: bool):
    edges = edges_from_mask(mask, 8)
    embeddings = set(shadow_embeddings(mask, root_edge))
    actions = automorphisms(8, edges)
    result = []
    while embeddings:
        representative = min(embeddings)
        orbit = frozenset(transform_mark(representative, action) for action in actions)
        assert orbit <= embeddings
        embeddings -= orbit
        canonical_mask, canonical_key = canonical_marked(8, edges, representative)
        assert canonical_mask == mask
        result.append({
            "representative": representative,
            "members": orbit,
            "canonical_key": canonical_key,
            "orbit_size": len(orbit),
            "stabilizer_size": len(actions) // len(orbit),
        })
    result.sort(key=lambda row: row["canonical_key"])
    return tuple(result), len(actions)


def mate_extension(mask: int, mark, left_bit: int, right_bit: int):
    edges = set(edges_from_mask(mask, 8))
    mate = 8
    edges.add(normal(mate, mark[4][0]))
    edges.add(normal(mate, mark[4][1]))
    if left_bit:
        edges.add(normal(mate, mark[0]))
    if right_bit:
        edges.add(normal(mate, mark[1]))
    edges = frozenset(edges)
    return edges, mask_from_edges(edges, 9)


def is_x_relation(source, unmatched_source, target, unmatched_target, edges):
    cross = {
        normal(left, right) for left in source for right in target
        if normal(left, right) in edges
    }
    source_used = {vertex for edge in cross for vertex in edge if vertex in source}
    target_used = {vertex for edge in cross for vertex in edge if vertex in target}
    return (
        len(cross) == 2
        and source_used == set(source) - {unmatched_source}
        and target_used == set(target) - {unmatched_target}
    )


def ordered_xx_marks(edges: frozenset[tuple[int, int]]):
    """All ordered X-X marks on one of the frozen H9 representatives."""

    graph_triangles = triangles(9, edges)
    answer = []
    for root_left in range(9):
        for root_right in range(9):
            if root_left == root_right:
                continue
            for source_left in graph_triangles:
                if root_left not in source_left:
                    continue
                for source_right in graph_triangles:
                    if root_right not in source_right or set(source_left) & set(source_right):
                        continue
                    for target in graph_triangles:
                        if set(target) & (set(source_left) | set(source_right)):
                            continue
                        for mate in target:
                            if (is_x_relation(source_left, root_left, target, mate, edges)
                                    and is_x_relation(
                                        source_right, root_right, target, mate, edges
                                    )):
                                answer.append((root_left, root_right, source_left,
                                               source_right, target, mate))
    return tuple(answer)


def delete_marked_mate(edges, marked):
    root_left, root_right, source_left, source_right, target, mate = marked
    kept = tuple(vertex for vertex in range(9) if vertex != mate)
    relabel = {vertex: index for index, vertex in enumerate(kept)}
    deleted_edges = frozenset(
        normal(relabel[left], relabel[right]) for left, right in edges
        if left != mate and right != mate
    )
    target_edge = tuple(vertex for vertex in target if vertex != mate)
    mark = (
        relabel[root_left], relabel[root_right],
        tuple(sorted(relabel[vertex] for vertex in source_left)),
        tuple(sorted(relabel[vertex] for vertex in source_right)),
        tuple(sorted(relabel[vertex] for vertex in target_edge)),
    )
    return deleted_edges, mark


def rref(matrix, right_hand_side):
    rows = [
        [Fraction(value) for value in row] + [Fraction(value)]
        for row, value in zip(matrix, right_hand_side)
    ]
    rank = 0
    pivots = []
    columns = len(matrix[0]) if matrix else 0
    for column in range(columns):
        pivot = next((row for row in range(rank, len(rows)) if rows[row][column]), None)
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
        pivots.append(column)
        rank += 1
    inconsistent = [
        row for row in rows if not any(row[:-1]) and row[-1]
    ]
    return rows, tuple(pivots), tuple(inconsistent)


def main() -> None:
    inputs = (COEFFICIENTS, MARKED_ROWS, SHADOW, PAIR_TYPES,
              AUGMENTED, BOUNDARY, WAVE159)
    input_hashes = {str(path): sha256(path) for path in inputs}
    with gzip.open(COEFFICIENTS, "rt", encoding="utf-8") as handle:
        coefficients = json.load(handle)
    with gzip.open(MARKED_ROWS, "rt", encoding="utf-8") as handle:
        marked_rows = json.load(handle)
    shadow = json.loads(SHADOW.read_text(encoding="utf-8"))
    pair_types = json.loads(PAIR_TYPES.read_text(encoding="utf-8"))
    augmented = json.loads(AUGMENTED.read_text(encoding="utf-8"))
    boundary = json.loads(BOUNDARY.read_text(encoding="utf-8"))
    wave159 = json.loads(WAVE159.read_text(encoding="utf-8"))
    assert shadow["status"] == "YYT_ORDER8_SHADOW_AND_FROZEN_SPAN_AUDIT_COMPLETE"
    assert pair_types["status"] == "YYT_OFFDIAGONAL_MARKED_MOTIF_CLASSIFICATION_COMPLETE"
    assert augmented["status"] == "AUGMENTED_FLAG_RELATION_AND_BAD_MATE_CAPACITY_PASS"
    assert boundary["status"] == "EDGE_SHADOW_LOWER_COUPLING_EXACT_BOUNDARY_COMPLETE"

    edge_records = coefficients["families"]["ordered_edge"]["class_coefficients"]
    nonedge_records = coefficients["families"]["ordered_nonedge"]["class_coefficients"]
    keys = tuple((int(row["order"]), int(row["canonical_mask"])) for row in edge_records)
    assert keys == tuple((int(row["order"]), int(row["canonical_mask"]))
                         for row in nonedge_records)
    assert len(keys) == 1207 and len(set(keys)) == 1207
    order8_masks = tuple(mask for order, mask in keys if order == 8)
    assert len(order8_masks) == 916
    order8_index = {mask: index for index, mask in enumerate(order8_masks)}
    full_index = {key: index for index, key in enumerate(keys)}
    assert marked_rows["class_streams"]["8"]["count"] == 916

    state_pairs = []
    for left, right in itertools.product(STATES, repeat=2):
        y_product = STATES[left]["Yhat"] * STATES[right]["Yhat"]
        selector = Fraction(
            STATES[left]["selected"] * STATES[right]["selected"], y_product
        )
        state_pairs.append({
            "pair": left + right,
            "mate_bits": [STATES[left]["mate_bit"], STATES[right]["mate_bit"]],
            "occurrences_per_physical_root_pair": y_product,
            "selected_pair_weight_per_occurrence": show_fraction(selector),
            "bad_mate_occurrence": bool(
                STATES[left]["mate_bit"] or STATES[right]["mate_bit"]
            ),
            "smallest_explicit_union_order": (
                9 + 2 * (left == "D") + 2 * (right == "D")
            ),
        })

    lift_rows = []
    marked_key_to_row = {}
    visible_type_weight = Counter()
    raw_orbit_cells = allowed_orbit_cells = 0
    raw_slot_cells = allowed_slot_cells = 0
    raw_visible_slots = allowed_visible_slots = 0
    forbidden_by_family = Counter()
    for family, root_edge in (("ordered_edge", True), ("ordered_nonedge", False)):
        shadow_coefficients = shadow["shadow_coefficients"][family][
            "nonzero_order8_coefficients"
        ]
        for mask, expected_coefficient in shadow_coefficients:
            mask = int(mask)
            expected_coefficient = int(expected_coefficient)
            assert mask in order8_index
            orbits, automorphism_group_size = marked_orbits(mask, root_edge)
            assert sum(row["orbit_size"] for row in orbits) == expected_coefficient
            for orbit_index, orbit in enumerate(orbits):
                representative = orbit["representative"]
                extensions = []
                feasibility = {}
                for left_bit, right_bit in itertools.product((0, 1), repeat=2):
                    extension_edges, extension_mask = mate_extension(
                        mask, representative, left_bit, right_bit
                    )
                    violations = pair_upper_violations(9, extension_edges)
                    # The target edge has exactly its newly adjoined mate as a
                    # common neighbour inside the marked extension.
                    extension_graph = adjacency(9, extension_edges)
                    target_edge = representative[4]
                    assert extension_graph[target_edge[0]] & extension_graph[target_edge[1]] == {8}
                    assert mask_from_edges(frozenset(
                        edge for edge in extension_edges if 8 not in edge
                    ), 8) == mask
                    key = f"{left_bit}{right_bit}"
                    feasibility[key] = not violations
                    if not violations:
                        visible = canonical_degree_mask(9, extension_edges)
                        visible_type_weight[visible] += orbit["orbit_size"]
                        allowed_visible_slots += orbit["orbit_size"]
                    else:
                        visible = canonical_degree_mask(9, extension_edges)
                    raw_visible_slots += orbit["orbit_size"]
                    extensions.append({
                        "mate_bits": [left_bit, right_bit],
                        "labelled_order9_mask": extension_mask,
                        "degree_cell_canonical_order9_mask": visible,
                        "deletes_to_order8_mask": mask,
                        "pair_upper_feasible": not violations,
                        "violations": violations,
                    })

                allowed_states = []
                forbidden_states = []
                variables = []
                row_id = f"{family[8].upper()}{order8_index[mask]:03d}O{orbit_index}"
                for pair in state_pairs:
                    state = pair["pair"]
                    bit_key = "".join(map(str, pair["mate_bits"]))
                    variable_id = f"L_{row_id}_{state}"
                    record = {"variable": variable_id, **pair}
                    if feasibility[bit_key]:
                        allowed_states.append(state)
                        variables.append(record)
                        allowed_orbit_cells += 1
                        allowed_slot_cells += orbit["orbit_size"]
                    else:
                        forbidden_states.append(state)
                        forbidden_by_family[family] += 1
                    raw_orbit_cells += 1
                    raw_slot_cells += orbit["orbit_size"]

                canonical_key = orbit["canonical_key"]
                assert (mask, canonical_key) not in marked_key_to_row
                marked_key_to_row[(mask, canonical_key)] = len(lift_rows)
                lift_rows.append({
                    "row_id": row_id,
                    "family": family,
                    "root_relation": "edge" if root_edge else "nonedge",
                    "order8_canonical_mask": mask,
                    "order8_column_index_0_based": order8_index[mask],
                    "full_1207_column_index_0_based": full_index[(8, mask)],
                    "shadow_coefficient_for_class": expected_coefficient,
                    "automorphism_group_size": automorphism_group_size,
                    "marked_orbit_index": orbit_index,
                    "marked_orbit_size": orbit["orbit_size"],
                    "marked_stabilizer_size": orbit["stabilizer_size"],
                    "canonical_mark_key": [
                        canonical_key[0], canonical_key[1],
                        list(canonical_key[2]), list(canonical_key[3]),
                        list(canonical_key[4]),
                    ],
                    "representative_mark": [
                        representative[0], representative[1],
                        list(representative[2]), list(representative[3]),
                        list(representative[4]),
                    ],
                    "deletion_equation": (
                        f"sum_state L[{row_id},state]="
                        f"{orbit['orbit_size']}*x8[{mask}]"
                    ),
                    "allowed_state_pairs": allowed_states,
                    "forbidden_state_pairs_by_pair_upper": forbidden_states,
                    "allowed_variables": variables,
                    "mate_bit_extensions": extensions,
                })

    assert len(lift_rows) == 11
    assert raw_orbit_cells == 11 * 9 == 99
    assert allowed_orbit_cells == 82
    assert raw_slot_cells == 20 * 9 == 180
    assert allowed_slot_cells == 158
    assert raw_visible_slots == 20 * 4 == 80
    assert allowed_visible_slots == 66
    assert len(visible_type_weight) == 19
    assert all("GG" in row["allowed_state_pairs"] for row in lift_rows)

    # Close the all-G face against the already frozen nine H9 X-X types.
    h9_types = pair_types["H9_disjoint_source_types"]
    incidence = [[0] * len(h9_types) for _ in lift_rows]
    h9_mark_audit = []
    for h9_index, h9 in enumerate(h9_types):
        edges = frozenset(normal(*edge) for edge in h9["representative_edges"])
        marked = ordered_xx_marks(edges)
        expected = 2 * (
            int(h9["adjacent_root_mark_multiplicity"])
            + int(h9["nonadjacent_root_mark_multiplicity"])
        )
        assert len(marked) == expected
        relation_histogram = Counter()
        for mark9 in marked:
            relation_histogram[
                "ordered_edge" if normal(mark9[0], mark9[1]) in edges
                else "ordered_nonedge"
            ] += 1
            deleted_edges, deleted_mark = delete_marked_mate(edges, mark9)
            deleted_mask, deleted_key = canonical_marked(
                8, deleted_edges, deleted_mark
            )
            row_index = marked_key_to_row[(deleted_mask, deleted_key)]
            incidence[row_index][h9_index] += 1
        h9_mark_audit.append({
            "h9_index": h9_index,
            "degree_cell_canonical_mask": int(h9["degree_cell_canonical_mask"]),
            "ordered_xx_marks": len(marked),
            "ordered_relation_histogram": dict(relation_histogram),
        })
    assert [sum(incidence[row][column] for row in range(len(lift_rows)))
            for column in range(len(h9_types))] == [
        row["ordered_xx_marks"] for row in h9_mark_audit
    ]
    for row, coefficients_row in zip(lift_rows, incidence):
        row["T0_GG_unmarked_H9_coefficients"] = [
            [index, value] for index, value in enumerate(coefficients_row) if value
        ]

    zero_rhs = [Fraction(0)] * len(lift_rows)
    _, pivots, inconsistent = rref(incidence, zero_rhs)
    assert not inconsistent and len(pivots) == 9

    wave_counts = {
        int(record["canonical_mask"]): Fraction(record["count"])
        for record in wave159["x8_support"]
    }
    deletion_rhs = [
        Fraction(row["marked_orbit_size"]) * wave_counts.get(
            int(row["order8_canonical_mask"]), Fraction()
        )
        for row in lift_rows
    ]
    reduced, pivots, inconsistent = rref(incidence, deletion_rhs)
    assert not inconsistent and pivots == tuple(range(9))
    h9_solution = [Fraction(0)] * 9
    for row in reduced:
        pivot = next((column for column, value in enumerate(row[:-1]) if value), None)
        if pivot is not None:
            assert row[pivot] == 1
            h9_solution[pivot] = row[-1]
    assert all(value >= 0 for value in h9_solution)
    assert all(
        sum(Fraction(value) * h9_solution[column]
            for column, value in enumerate(coefficients_row)) == rhs
        for coefficients_row, rhs in zip(incidence, deletion_rhs)
    )

    ordered_by_relation = {
        family: sum(
            rhs for row, rhs in zip(lift_rows, deletion_rhs)
            if row["family"] == family
        )
        for family in ("ordered_edge", "ordered_nonedge")
    }
    assert sum(ordered_by_relation.values(), Fraction()) == 91476
    assert ordered_by_relation["ordered_edge"] / 2 == Fraction(
        augmented["wave159_boundary_evaluation"]["beta_e"]
    )
    assert ordered_by_relation["ordered_nonedge"] / 2 == Fraction(
        augmented["wave159_boundary_evaluation"]["beta_n"]
    )

    # Coarse 3x3 state Gram.  If N_a is the total number of physical
    # (root,target-edge) incidences in state a, then
    # C_aa=L_aa+y_a^2 N_a and C_ab=L_ab.  It is sum_e z_e z_e^T and PSD.
    state_order = ("G", "D", "P")
    endpoint_incidence = {"G": 8316, "D": 0, "P": 0}
    endpoint_lift = [[Fraction(0) for _ in state_order] for _ in state_order]
    endpoint_lift[0][0] = sum(ordered_by_relation.values(), Fraction())
    endpoint_gram = [row[:] for row in endpoint_lift]
    for index, state in enumerate(state_order):
        endpoint_gram[index][index] += (
            STATES[state]["Yhat"] ** 2 * endpoint_incidence[state]
        )
    assert endpoint_gram == [
        [Fraction(99792), Fraction(0), Fraction(0)],
        [Fraction(0), Fraction(0), Fraction(0)],
        [Fraction(0), Fraction(0), Fraction(0)],
    ]

    congruences = []
    for row, coefficient_row in zip(lift_rows, incidence):
        nonzero = [(index, value) for index, value in enumerate(coefficient_row) if value]
        if len(nonzero) != 1:
            continue
        h9_index, coefficient = nonzero[0]
        orbit_size = int(row["marked_orbit_size"])
        divisor = math.gcd(orbit_size, coefficient)
        x_divisor = coefficient // divisor
        h_divisor = orbit_size // divisor
        if x_divisor > 1 or h_divisor > 1:
            congruences.append({
                "row_id": row["row_id"],
                "equation": (
                    f"{orbit_size}*x8[{row['order8_canonical_mask']}]="
                    f"{coefficient}*h9[{h9_index}]"
                ),
                "necessary_at_T0": {
                    "x8_divisible_by": x_divisor,
                    "h9_divisible_by": h_divisor,
                },
            })

    result = {
        "status": "MINIMAL_ORDER9_MATE_DOUBLED_STATUS_LIFT_PASS",
        "inputs": input_hashes,
        "frozen_dimensions": {
            "class_orders": [5, 6, 7, 8],
            "class_columns_per_root_relation": len(keys),
            "order8_columns_per_root_relation": len(order8_masks),
            "ordered_edge_matrix_size": int(
                coefficients["families"]["ordered_edge"]["matrix_size"]
            ),
            "ordered_nonedge_matrix_size": int(
                coefficients["families"]["ordered_nonedge"]["matrix_size"]
            ),
            "marked_vertex_rows": len(marked_rows["vertex_rows"]),
            "marked_ordered_pair_rows": len(marked_rows["ordered_pair_rows"]),
            "order8_columns_touched_by_this_lift": 9,
        },
        "rooted_state_definition": {
            "target": (
                "For target edge e with unique triangle mate u, a root r has "
                "m=1[r~u], y=Yhat[r,e], and s=m*y+binom(y,2)."
            ),
            "states": STATES,
            "state_pairs": state_pairs,
            "sufficient_statistic_statement": (
                "On the proved nonzero domain {(0,1),(0,2),(1,1)}, the state "
                "label is equivalent to (m,y), hence determines s.  If L_ab "
                "counts ordered source-occurrence pairs, then an ordered "
                "physical selected pair contributes y_a*y_b occurrences and "
                "is recovered with weight s_a*s_b/(y_a*y_b)."
            ),
        },
        "marked_lift_schema": {
            "variable": "L[family,K8,marked_orbit,state_left,state_right]",
            "variable_semantics": (
                "Number of ordered marked source-occurrence pairs whose mate "
                "extension has the stated physical root statuses."
            ),
            "deletion_rows": len(lift_rows),
            "raw_orbit_state_dimension": raw_orbit_cells,
            "pair_upper_allowed_orbit_state_dimension": allowed_orbit_cells,
            "raw_marked_slot_state_dimension": raw_slot_cells,
            "pair_upper_allowed_marked_slot_state_dimension": allowed_slot_cells,
            "visible_mate_bit_templates_before_pair_upper": raw_visible_slots,
            "visible_mate_bit_templates_after_pair_upper": allowed_visible_slots,
            "distinct_visible_degree_cell_order9_masks_after_pair_upper": len(
                visible_type_weight
            ),
            "visible_order9_type_marked_weights": [
                [mask, weight] for mask, weight in sorted(visible_type_weight.items())
            ],
            "forbidden_orbit_state_cells_by_family": dict(forbidden_by_family),
            "exact_functionals": {
                "ordered_bad_mate_shadow_R_rel": (
                    "sum L_ab over state pairs containing P"
                ),
                "unordered_selected_collision_K_rel": (
                    "(1/2) sum_ab s_a*s_b/(y_a*y_b) L_ab"
                ),
                "state_Gram": (
                    "C_ab=sum_rel L_ab for a!=b; "
                    "C_aa=sum_rel L_aa+y_a^2*N_a; C is PSD"
                ),
            },
            "rows": lift_rows,
        },
        "multiplicity_and_deletion_audit": {
            "all_916_frozen_order8_columns_checked_by_parent_shadow": True,
            "nonzero_shadow_columns": 9,
            "ordered_marked_embeddings": 20,
            "marked_automorphism_orbits": len(lift_rows),
            "orbit_sizes_sum_to_each_frozen_shadow_coefficient": True,
            "orbit_stabilizer_product_equals_automorphism_group_size": True,
            "all_variable_ids_unique": len({
                variable["variable"] for row in lift_rows
                for variable in row["allowed_variables"]
            }) == allowed_orbit_cells,
            "every_extension_deletes_to_its_exact_frozen_K8": True,
            "unique_target_edge_mate_inside_every_extension": True,
            "pair_upper_checked_on_every_mate_bit_extension": True,
        },
        "T0_all_G_order9_closure": {
            "premises": [
                "T=0 implies D_*=0 and P=0",
                "therefore every nonzero root-edge state is G=(0,1,0)",
            ],
            "frozen_H9_types": len(h9_types),
            "H9_incidence_matrix_shape": [len(lift_rows), len(h9_types)],
            "H9_incidence_rank_over_Q": len(pivots),
            "H9_mark_audit": h9_mark_audit,
            "incidence_rows": [
                {
                    "row_id": row["row_id"],
                    "marked_orbit_size_times_x8": (
                        f"{row['marked_orbit_size']}*x8[{row['order8_canonical_mask']}]"
                    ),
                    "H9_coefficients": row["T0_GG_unmarked_H9_coefficients"],
                }
                for row in lift_rows
            ],
            "wave159_exact_nonnegative_H9_solution": [
                {
                    "h9_index": index,
                    "degree_cell_canonical_mask": int(
                        h9_types[index]["degree_cell_canonical_mask"]
                    ),
                    "count": show_fraction(value),
                }
                for index, value in enumerate(h9_solution)
            ],
            "wave159_ordered_shadow_mass": {
                family: show_fraction(value)
                for family, value in ordered_by_relation.items()
            },
            "wave159_total_ordered_shadow_mass": 91476,
            "wave159_selected_collision_from_lift": 0,
            "wave159_state_incidence_G_D_P": endpoint_incidence,
            "wave159_coarse_state_Gram_G_D_P": [
                [show_fraction(value) for value in row] for row in endpoint_gram
            ],
            "wave159_coarse_state_Gram_PSD_rank": 1,
            "integer_T0_congruences_from_unmarked_H9_closure": congruences,
            "conclusion": (
                "The exact Wave159 rational endpoint extends through every "
                "deletion row, all local pair-upper zero cells, the restricted "
                "unmarked H9 incidence bridge, and the coarse 3x3 PSD state "
                "Gram.  Thus this minimal lift gives no positive T lower bound."
            ),
        },
        "streaming_and_scope_boundary": {
            "exact_streaming_algorithm": [
                "Bucket augmented source flags by (root,target_edge), obtaining y.",
                "Read the unique target-edge mate adjacency bit m and map each nonzero bucket to G,D,P.",
                "For every ordered pair of distinct root buckets and every Cartesian source-occurrence pair, canonicalize its deleted K8 marked orbit and increment L.",
            ],
            "why_no_full_order9_census_is_needed": (
                "Only 9 of 916 K8 columns, 11 marked deletion orbits, and 82 "
                "locally allowed tagged cells occur."
            ),
            "doubled_status_visibility_boundary": (
                "D and G have the same mate bit and therefore the same induced "
                "nine-vertex graph.  Certifying one D tag adds the other two "
                "vertices of its second source triangle; DG/DP needs order 11 "
                "and DD needs order 13.  The tag lift is an exact sufficient "
                "statistic for s, but its nonnegative deletion rows alone are "
                "not sufficient for realization by one graph."
            ),
            "physical_synchronization": (
                "For each state pair ab, actual occurrence totals come in "
                "Cartesian packets of size y_a*y_b.  Global divisibility is "
                "necessary; packet compatibility across marked orbits is the "
                "first missing order-11/13 constraint."
            ),
            "full_order9_class_census_performed": False,
            "frozen_916_or_2414_resources_regenerated": False,
            "submission_txt_created": False,
        },
        "lane_conclusion": {
            "new_exact_local_zero_cells": raw_orbit_cells - allowed_orbit_cells,
            "new_weighted_marked_zero_cells": raw_slot_cells - allowed_slot_cells,
            "T0_excluded": False,
            "positive_T_lower_bound_obtained": False,
            "useful_new_integer_information": (
                "The all-G unmarked H9 bridge supplies the displayed exact "
                "divisibility conditions for an actual integer T=0 graph."
            ),
        },
    }
    atomic_json(OUTPUT, result)
    print(json.dumps({
        "status": result["status"],
        "deletion_rows": len(lift_rows),
        "allowed_tagged_cells": allowed_orbit_cells,
        "visible_order9_types": len(visible_type_weight),
        "T0_H9_rank": len(pivots),
        "T0_excluded": False,
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
