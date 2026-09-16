"""Exact restricted order-11 synchronization for one doubled root state.

No general graph class on eleven vertices is generated.  The only objects
enumerated are forced unions consisting of

* two X source triangles through the same doubled root (state D),
* one G or P source triangle through a second root, and
* their common target triangle.

The two D source occurrences delete to two cells of the previously audited
marked order-9 lift.  The resulting incidence matrices synchronize those
two occurrences into one physical doubled event.  All optional edges are
the two source-triangle partial matchings allowed by the SRG pair upper
bounds; these are enumerated and quotiented by the four role symmetries.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import os
from collections import Counter
from fractions import Fraction
from pathlib import Path

from scratch_theory_minimal_order9_mate_lift import (
    adjacency,
    canonical_degree_mask,
    canonical_marked,
    degrees,
    edges_from_mask,
    mask_from_edges,
    normal,
    pair_upper_violations,
)


ORDER9 = Path("scratch_theory_minimal_order9_mate_lift.json")
ORDER9_AUDIT = Path("scratch_theory_minimal_order9_mate_lift_audit.json")
SHADOW = Path("scratch_theory_root_yyt_order8_shadow.json")
PAIR_TYPES = Path("scratch_theory_root_yyt_pair_classification.json")
WAVE159 = Path(
    "external_conway99_research/attempts/wave159-four-root-cut-loop/"
    "exact-witness-after-fifteen-cuts.json"
)
OUTPUT = Path("scratch_theory_one_d_order11_sync_lift.json")

# Canonical labelled role skeleton.
D_ROOT = 0
D_SOURCE_A = (0, 1, 2)
D_SOURCE_B = (0, 3, 4)
OTHER_ROOT = 5
OTHER_SOURCE = (5, 6, 7)
TARGET = (8, 9, 10)
TARGET_MATE = 8
TARGET_EDGE = (9, 10)

FORCED_G = frozenset(normal(*edge) for edge in {
    # The two root triangles which witness one diagonal event.
    (0, 1), (0, 2), (1, 2),
    (0, 3), (0, 4), (3, 4),
    # The other source and target triangles.
    (5, 6), (5, 7), (6, 7),
    (8, 9), (8, 10), (9, 10),
    # Three aligned X matchings to the common target flag.
    (1, 9), (2, 10), (3, 9), (4, 10), (6, 9), (7, 10),
})
FORCED_P = FORCED_G | {normal(5, 8)}


def atomic_json(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def show(value: Fraction) -> int | str:
    return int(value) if value.denominator == 1 else str(value)


def partial_matchings(left, right):
    result = []
    for size in range(4):
        for left_vertices in itertools.combinations(left, size):
            for right_vertices in itertools.combinations(right, size):
                for images in itertools.permutations(right_vertices):
                    result.append(frozenset(
                        normal(source, target)
                        for source, target in zip(left_vertices, images)
                    ))
    assert len(result) == 34 and len(set(result)) == 34
    return tuple(result)


def compose(left, right):
    return tuple(left[right[index]] for index in range(len(left)))


def role_group():
    identity = tuple(range(11))
    swap_d_sources = list(identity)
    swap_d_sources[1], swap_d_sources[3] = 3, 1
    swap_d_sources[2], swap_d_sources[4] = 4, 2
    endpoint_flip = list(identity)
    for left, right in ((1, 2), (3, 4), (6, 7), (9, 10)):
        endpoint_flip[left], endpoint_flip[right] = right, left
    result = frozenset({
        identity,
        tuple(swap_d_sources),
        tuple(endpoint_flip),
        compose(tuple(swap_d_sources), tuple(endpoint_flip)),
    })
    assert len(result) == 4
    return result


def transform_edges(edges, permutation):
    return frozenset(normal(permutation[left], permutation[right])
                     for left, right in edges)


def order9_row_lookup(order9):
    lookup = {}
    rows_by_id = {}
    for row in order9["marked_lift_schema"]["rows"]:
        key = row["canonical_mark_key"]
        marked_key = (
            int(key[0]), int(key[1]), tuple(map(int, key[2])),
            tuple(map(int, key[3])), tuple(map(int, key[4])),
        )
        lookup[(int(row["order8_canonical_mask"]), marked_key)] = row["row_id"]
        rows_by_id[row["row_id"]] = row
    assert len(lookup) == len(rows_by_id) == 11
    return lookup, rows_by_id


def transpose_rows(rows_by_id):
    lookup = {}
    for row in rows_by_id.values():
        key = row["canonical_mark_key"]
        marked_key = (
            int(key[0]), int(key[1]), tuple(map(int, key[2])),
            tuple(map(int, key[3])), tuple(map(int, key[4])),
        )
        lookup[(int(row["order8_canonical_mask"]), marked_key)] = row["row_id"]
    answer = {}
    for row_id, row in rows_by_id.items():
        mark = row["representative_mark"]
        reversed_mark = (
            int(mark[1]), int(mark[0]), tuple(map(int, mark[3])),
            tuple(map(int, mark[2])), tuple(map(int, mark[4])),
        )
        mask = int(row["order8_canonical_mask"])
        canonical_mask, canonical_key = canonical_marked(
            8, edges_from_mask(mask, 8), reversed_mark
        )
        answer[row_id] = lookup[(canonical_mask, canonical_key)]
    assert all(answer[answer[row_id]] == row_id for row_id in answer)
    return answer


def delete_d_source(edges, retained_d_source, removed_vertices, row_lookup):
    """Delete one D source pair, then identify its marked order-9 row."""

    retained = tuple(vertex for vertex in range(11) if vertex not in removed_vertices)
    relabel9 = {vertex: index for index, vertex in enumerate(retained)}
    order9_edges = frozenset(
        normal(relabel9[left], relabel9[right]) for left, right in edges
        if left not in removed_vertices and right not in removed_vertices
    )
    mark9 = (
        relabel9[D_ROOT], relabel9[OTHER_ROOT],
        tuple(sorted(relabel9[vertex] for vertex in retained_d_source)),
        tuple(sorted(relabel9[vertex] for vertex in OTHER_SOURCE)),
        tuple(sorted(relabel9[vertex] for vertex in TARGET_EDGE)),
    )
    mate9 = relabel9[TARGET_MATE]
    retained8 = tuple(vertex for vertex in range(9) if vertex != mate9)
    relabel8 = {vertex: index for index, vertex in enumerate(retained8)}
    order8_edges = frozenset(
        normal(relabel8[left], relabel8[right]) for left, right in order9_edges
        if left != mate9 and right != mate9
    )
    mark8 = (
        relabel8[mark9[0]], relabel8[mark9[1]],
        tuple(sorted(relabel8[vertex] for vertex in mark9[2])),
        tuple(sorted(relabel8[vertex] for vertex in mark9[3])),
        tuple(sorted(relabel8[vertex] for vertex in mark9[4])),
    )
    canonical_mask, canonical_key = canonical_marked(8, order8_edges, mark8)
    row_id = row_lookup[(canonical_mask, canonical_key)]
    return {
        "retained_D_source": "A" if retained_d_source == D_SOURCE_A else "B",
        "removed_vertices": sorted(removed_vertices),
        "order9_row_id": row_id,
        "labelled_order9_mask": mask_from_edges(order9_edges, 9),
        "degree_cell_canonical_order9_mask": canonical_degree_mask(9, order9_edges),
        "order8_canonical_mask_after_mate_deletion": canonical_mask,
    }


def rational_rank(matrix):
    rows = [[Fraction(value) for value in row] for row in matrix]
    rank = 0
    columns = len(rows[0]) if rows else 0
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
        rank += 1
    return rank


def modular_rank(matrix, modulus):
    rows = [[value % modulus for value in row] for row in matrix]
    rank = 0
    columns = len(rows[0]) if rows else 0
    for column in range(columns):
        pivot = next((row for row in range(rank, len(rows)) if rows[row][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inverse = pow(rows[rank][column], -1, modulus)
        rows[rank] = [value * inverse % modulus for value in rows[rank]]
        for row in range(len(rows)):
            if row == rank or not rows[row][column]:
                continue
            scale = rows[row][column]
            rows[row] = [
                (value - scale * pivot_value) % modulus
                for value, pivot_value in zip(rows[row], rows[rank])
            ]
        rank += 1
    return rank


def determinant_bareiss(matrix):
    order = len(matrix)
    if not order:
        return 1
    work = [list(map(int, row)) for row in matrix]
    sign = 1
    previous = 1
    for column in range(order - 1):
        pivot = next((row for row in range(column, order) if work[row][column]), None)
        if pivot is None:
            return 0
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            sign *= -1
        pivot_value = work[column][column]
        for row in range(column + 1, order):
            for target in range(column + 1, order):
                numerator = (work[row][target] * pivot_value
                             - work[row][column] * work[column][target])
                assert numerator % previous == 0
                work[row][target] = numerator // previous
            work[row][column] = 0
        previous = pivot_value
    return sign * work[-1][-1]


def full_minor_gcd(matrix, rank):
    """GCD of full-rank minors after zero rows are removed."""

    active = [row for row in matrix if any(row)]
    assert len(active) == rank
    answer = 0
    nonzero = 0
    for columns in itertools.combinations(range(len(active[0])), rank):
        determinant = determinant_bareiss([
            [row[column] for column in columns] for row in active
        ])
        if determinant:
            nonzero += 1
            answer = math.gcd(answer, abs(determinant))
            if answer == 1:
                break
    return answer, nonzero


def enumerate_types(other_state, row_lookup, rows_by_id):
    assert other_state in ("G", "P")
    left_matchings = partial_matchings(D_SOURCE_A, OTHER_SOURCE)
    right_matchings = partial_matchings(D_SOURCE_B, OTHER_SOURCE)
    forced = FORCED_G if other_state == "G" else FORCED_P
    candidates = {}
    rejected = Counter()
    examined = 0
    for left, right in itertools.product(left_matchings, right_matchings):
        # The shared root edge 0--5 is one graph edge, hence its membership
        # must agree in the two triangle-pair matchings.
        if ((0, 5) in left) != ((0, 5) in right):
            continue
        examined += 1
        edges = forced | left | right
        assert edges not in candidates
        failures = pair_upper_violations(11, edges)
        if failures:
            first = failures[0]
            rejected[(bool(first["adjacent"]), int(first["upper"]),
                      len(first["common_neighbours"]))] += 1
            continue
        deletions = (
            delete_d_source(edges, D_SOURCE_A, {3, 4}, row_lookup),
            delete_d_source(edges, D_SOURCE_B, {1, 2}, row_lookup),
        )
        state_pair = "D" + other_state
        for deletion in deletions:
            assert state_pair in rows_by_id[deletion["order9_row_id"]][
                "allowed_state_pairs"
            ]
        candidates[edges] = deletions
    assert examined == 27 * 27 + 7 * 7 == 778

    actions = role_group()
    remaining = set(candidates)
    types = []
    while remaining:
        representative = min(remaining, key=lambda edges: mask_from_edges(edges, 11))
        orbit = frozenset(transform_edges(representative, action) for action in actions)
        assert orbit <= set(candidates)
        remaining -= orbit
        deletions = candidates[representative]
        incidence = Counter(row["order9_row_id"] for row in deletions)
        assert sum(incidence.values()) == 2
        optional = representative - forced
        root_relation = "ordered_edge" if (0, 5) in representative else "ordered_nonedge"
        type_id = f"{other_state}{'E' if root_relation == 'ordered_edge' else 'N'}{len(types):02d}"
        types.append({
            "type_id": type_id,
            "other_state": other_state,
            "root_relation": root_relation,
            "role_canonical_labelled_order11_mask": mask_from_edges(representative, 11),
            "edge_count": len(representative),
            "degree_sequence": sorted(degrees(11, representative), reverse=True),
            "role_orbit_size": len(orbit),
            "role_stabilizer_size": len(actions) // len(orbit),
            "optional_source_cross_edges": [list(edge) for edge in sorted(optional)],
            "order9_deletions": list(deletions),
            "order9_incidence": [[row_id, value]
                                 for row_id, value in sorted(incidence.items())],
        })
    types.sort(key=lambda row: row["role_canonical_labelled_order11_mask"])
    for index, row in enumerate(types):
        row["type_id"] = f"{other_state}{'E' if row['root_relation'] == 'ordered_edge' else 'N'}{index:02d}"
    assert sum(row["role_orbit_size"] for row in types) == len(candidates)
    return {
        "other_state": other_state,
        "matching_pair_candidates_after_shared_edge_consistency": examined,
        "pair_upper_feasible_labelled_patterns": len(candidates),
        "pair_upper_rejected_labelled_patterns": examined - len(candidates),
        "first_violation_histogram_(adjacent,upper,observed)": {
            str(key): value for key, value in sorted(rejected.items())
        },
        "rooted_role_types": types,
    }


def matrix_summary(census, row_ids, rows_by_id, transpose):
    types = census["rooted_role_types"]
    index = {row_id: position for position, row_id in enumerate(row_ids)}
    matrix = [[0] * len(types) for _ in row_ids]
    for column, row in enumerate(types):
        for row_id, value in row["order9_incidence"]:
            matrix[index[row_id]][column] = int(value)
    assert all(sum(matrix[row][column] for row in range(len(row_ids))) == 2
               for column in range(len(types)))
    rank = rational_rank(matrix)
    active = [row_ids[row] for row in range(len(row_ids)) if any(matrix[row])]
    inactive = [row_id for row_id in row_ids if row_id not in active]
    assert rank == len(active)
    minor_gcd, nonzero_minors = full_minor_gcd(matrix, rank)
    assert minor_gcd == 4
    rank_mod2 = modular_rank(matrix, 2)
    rank_mod3 = modular_rank(matrix, 3)
    assert rank_mod2 == rank - 2 and rank_mod3 == rank

    state_pair = "D" + census["other_state"]
    reverse_pair = census["other_state"] + "D"
    new_zero_left = [
        {"row_id": row_id, "state_pair": state_pair}
        for row_id in inactive
        if state_pair in rows_by_id[row_id]["allowed_state_pairs"]
    ]
    reverse_inactive = [transpose[row_id] for row_id in inactive]
    new_zero_right = [
        {"row_id": row_id, "state_pair": reverse_pair}
        for row_id in reverse_inactive
        if reverse_pair in rows_by_id[row_id]["allowed_state_pairs"]
    ]

    edge_active = [row_id for row_id in active
                   if rows_by_id[row_id]["family"] == "ordered_edge"]
    nonedge_active = [row_id for row_id in active
                      if rows_by_id[row_id]["family"] == "ordered_nonedge"]
    # Every physical one-D tuple supplies its two D occurrences inside one
    # fixed root relation, giving the two exact parity conditions.  Since the
    # full-minor gcd is 4, those index-two conditions are also sufficient for
    # membership in the full integer column lattice.
    for column in range(len(types)):
        edge_sum = sum(matrix[index[row_id]][column] for row_id in edge_active)
        nonedge_sum = sum(matrix[index[row_id]][column] for row_id in nonedge_active)
        assert (edge_sum, nonedge_sum) in ((2, 0), (0, 2))

    if census["other_state"] == "G":
        rational_cone_facets = [
            {
                "relation": "ordered_edge",
                "inequality": "L[E019O0,DG]-L[E515O0,DG] >= 0",
            },
            {
                "relation": "ordered_nonedge",
                "inequality": (
                    "L[N057O0,DG]+L[N060O0,DG]-L[N525O0,DG] >= 0"
                ),
            },
        ]
    else:
        rational_cone_facets = [
            {
                "relation": "ordered_edge",
                "inequality": "L[E019O0,DP]-L[E515O0,DP] >= 0",
            },
            {
                "relation": "ordered_nonedge",
                "inequality": "L[N060O0,DP]-L[N525O0,DP] >= 0",
            },
        ]

    return {
        "row_order": row_ids,
        "column_order": [row["type_id"] for row in types],
        "sparse_columns": [row["order9_incidence"] for row in types],
        "shape": [len(row_ids), len(types)],
        "rank_over_Q": rank,
        "rank_mod_2": rank_mod2,
        "rank_mod_3": rank_mod3,
        "active_rows": active,
        "forced_zero_rows": inactive,
        "every_column_sum": 2,
        "full_rank_minor_gcd": minor_gcd,
        "nonzero_full_rank_minors_checked": nonzero_minors,
        "Smith_invariants_on_active_rows": [1] * (rank - 2) + [2, 2],
        "exact_integer_lattice_conditions": {
            "zero_rows": inactive,
            "edge_active_sum_even": edge_active,
            "nonedge_active_sum_even": nonedge_active,
            "conditions_are_sufficient_for_integer_lattice_membership": True,
        },
        "new_zero_cells_beyond_order9_pair_upper": new_zero_left + new_zero_right,
        "exact_nonnegative_rational_cone_nontrivial_facets": rational_cone_facets,
        "cone_facets_completeness_reason": (
            "Every active row except E515O0 and N525O0 has a doubled unit "
            "column.  The displayed pair columns are the only way to supply "
            "those two exceptional coordinates; after subtracting them, all "
            "remaining nonnegative coordinates use doubled unit columns."
        ),
    }


def main() -> None:
    inputs = (ORDER9, ORDER9_AUDIT, SHADOW, PAIR_TYPES, WAVE159)
    order9 = json.loads(ORDER9.read_text(encoding="utf-8"))
    audit9 = json.loads(ORDER9_AUDIT.read_text(encoding="utf-8"))
    shadow = json.loads(SHADOW.read_text(encoding="utf-8"))
    pair_types = json.loads(PAIR_TYPES.read_text(encoding="utf-8"))
    wave159 = json.loads(WAVE159.read_text(encoding="utf-8"))
    assert order9["status"] == "MINIMAL_ORDER9_MATE_DOUBLED_STATUS_LIFT_PASS"
    assert audit9["status"] == (
        "MINIMAL_ORDER9_MATE_DOUBLED_STATUS_LIFT_INDEPENDENT_AUDIT_PASS"
    )
    assert shadow["status"] == "YYT_ORDER8_SHADOW_AND_FROZEN_SPAN_AUDIT_COMPLETE"
    assert pair_types["status"] == "YYT_OFFDIAGONAL_MARKED_MOTIF_CLASSIFICATION_COMPLETE"

    row_lookup, rows_by_id = order9_row_lookup(order9)
    row_ids = [row["row_id"] for row in order9["marked_lift_schema"]["rows"]]
    transpose = transpose_rows(rows_by_id)
    census_g = enumerate_types("G", row_lookup, rows_by_id)
    census_p = enumerate_types("P", row_lookup, rows_by_id)
    assert census_g["pair_upper_feasible_labelled_patterns"] == 50
    assert len(census_g["rooted_role_types"]) == 17
    assert census_p["pair_upper_feasible_labelled_patterns"] == 18
    assert len(census_p["rooted_role_types"]) == 8
    summary_g = matrix_summary(census_g, row_ids, rows_by_id, transpose)
    summary_p = matrix_summary(census_p, row_ids, rows_by_id, transpose)
    assert summary_g["rank_over_Q"] == 8
    assert summary_p["rank_over_Q"] == 6
    new_zero_cells = (summary_g["new_zero_cells_beyond_order9_pair_upper"]
                      + summary_p["new_zero_cells_beyond_order9_pair_upper"])
    assert len(new_zero_cells) == 10
    assert len({(row["row_id"], row["state_pair"]) for row in new_zero_cells}) == 10

    # Exact T=0 boundary.  All order-eight deletion mass is placed in GG;
    # every one-D cell and every order-11 type variable is zero.  The prior
    # restricted H9 solution supplies the all-G order-nine closure.
    wave_counts = {
        int(record["canonical_mask"]): Fraction(record["count"])
        for record in wave159["x8_support"]
    }
    deletion_rhs = {
        row_id: Fraction(rows_by_id[row_id]["marked_orbit_size"])
        * wave_counts.get(int(rows_by_id[row_id]["order8_canonical_mask"]), Fraction())
        for row_id in row_ids
    }
    h9_solution = [
        Fraction(row["count"]) for row in
        order9["T0_all_G_order9_closure"]["wave159_exact_nonnegative_H9_solution"]
    ]
    assert all(value >= 0 for value in deletion_rhs.values())
    assert all(value >= 0 for value in h9_solution)
    assert sum(deletion_rhs.values(), Fraction()) == 91476
    integer_scale = math.lcm(*(
        [value.denominator for value in deletion_rhs.values()]
        + [value.denominator for value in h9_solution]
    ))
    assert integer_scale > 0
    scaled_deletion = {
        row_id: int(value * integer_scale)
        for row_id, value in deletion_rhs.items()
    }
    scaled_h9 = [int(value * integer_scale) for value in h9_solution]
    assert all(value >= 0 for value in list(scaled_deletion.values()) + scaled_h9)

    result = {
        "status": "ONE_D_ORDER11_SYNCHRONIZATION_LIFT_PASS",
        "inputs": {str(path): sha256(path) for path in inputs},
        "forced_rooted_union": {
            "vertices": {
                "D_root": D_ROOT,
                "D_source_triangles": [list(D_SOURCE_A), list(D_SOURCE_B)],
                "other_root": OTHER_ROOT,
                "other_source_triangle": list(OTHER_SOURCE),
                "target_triangle": list(TARGET),
                "target_mate": TARGET_MATE,
                "target_edge": list(TARGET_EDGE),
            },
            "forced_G_edges": [list(edge) for edge in sorted(FORCED_G)],
            "P_additional_edge": [OTHER_ROOT, TARGET_MATE],
            "optional_edges": (
                "A--other and B--other partial matchings, with the shared "
                "D_root--other_root edge chosen consistently"
            ),
            "candidate_count_per_other_state": 778,
            "role_symmetry_group_order": len(role_group()),
            "role_symmetries": [
                "swap the two D source triangles",
                "simultaneously flip the target-edge endpoints and all three matched source pairs",
            ],
            "completeness": (
                "N(D_root)=7K2 forbids edges between the two D source pairs. "
                "For either D-source/other-source triangle pair, the local "
                "SRG upper bounds force all remaining cross edges to be a "
                "partial matching.  The 34x34 choices with the one shared "
                "edge synchronized are exactly 27^2+7^2=778."
            ),
        },
        "G_census": census_g,
        "P_census": census_p,
        "synchronization_matrices": {
            "DG": summary_g,
            "DP": summary_p,
            "reverse_orientation_row_map": transpose,
            "reverse_equations": (
                "GD and PD use the same columns after applying the displayed "
                "left/right transpose to every order9 row."
            ),
            "physical_multiplicity": (
                "Every column has sum two because one physical D event has "
                "exactly two X source occurrences.  Therefore "
                "sum_i L[i,Db]=2*sum_type Z[type,b] separately on the edge "
                "and nonedge root relations."
            ),
        },
        "dimension_and_zero_cell_audit": {
            "G_labelled_patterns": 50,
            "G_rooted_types": 17,
            "P_labelled_patterns": 18,
            "P_rooted_types": 8,
            "total_restricted_order11_rooted_types": 25,
            "new_order9_state_cells_forced_zero": new_zero_cells,
            "new_zero_cell_count": len(new_zero_cells),
            "no_general_order11_isomorphism_classes_generated": True,
        },
        "T0_exact_boundary": {
            "assignment": {
                "L_GG_by_deletion_row": {
                    row_id: show(value) for row_id, value in deletion_rhs.items()
                },
                "all_other_order9_state_cells": 0,
                "all_one_D_order11_type_variables": 0,
                "H9_X_X_solution": [show(value) for value in h9_solution],
            },
            "checks": {
                "all_order8_deletion_rows": True,
                "all_order9_pair_upper_zero_cells": True,
                "all_one_D_synchronization_rows": True,
                "all_one_D_Farkas_cone_facets": True,
                "restricted_unmarked_H9_bridge": True,
                "coarse_state_Gram": "diag(99792,0,0) is PSD",
                "selected_collision": 0,
            },
            "homogeneous_integer_ray": {
                "scale": integer_scale,
                "scaled_L_GG_by_row": scaled_deletion,
                "scaled_H9_solution": scaled_h9,
                "scaled_total_ordered_shadow_mass": 91476 * integer_scale,
                "all_one_D_variables": 0,
                "T": 0,
                "scope": (
                    "Integer point on the homogenized extension cone; the "
                    "normalization coordinate is scaled as well, so it is not "
                    "asserted to be one 99-vertex graph."
                ),
            },
            "Farkas_LP_conclusion": (
                "The displayed nonnegative feasible point has D=P=T=0. "
                "Consequently no nonnegative linear combination of these "
                "deletion, synchronization, pair-upper-zero, and rational-cone "
                "constraints can prove D>0 or T>0."
            ),
        },
        "streaming_scope": {
            "algorithm": [
                "For each (root,target edge) bucket with y=2, retain its unordered pair of X source flags.",
                "Join it to each distinct-root G/P bucket on the same target edge.",
                "Canonicalize only under the four forced-role symmetries and increment one of the 25 columns.",
                "Emit its two order9 deletion rows; never store unrelated order11 graphs.",
            ],
            "maximum_candidate_patterns_per_state": 778,
            "full_order11_census_performed": False,
            "submission_txt_created": False,
        },
        "lane_conclusion": {
            "exact_new_local_constraints": True,
            "T0_excluded": False,
            "D_or_T_forced_positive": False,
            "next_missing_layer": (
                "Two-D order13 packet synchronization, or a global constraint "
                "which prevents the all-G allocation of every deletion row."
            ),
        },
    }
    atomic_json(OUTPUT, result)
    print(json.dumps({
        "status": result["status"],
        "G_types": len(census_g["rooted_role_types"]),
        "P_types": len(census_p["rooted_role_types"]),
        "new_zero_cells": len(new_zero_cells),
        "T0_excluded": False,
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
