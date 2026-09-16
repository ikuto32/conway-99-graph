"""Independent finite replay of the restricted one-D synchronization lift.

This audit does not import the order-11 producer.  It reconstructs the
forced unions from the marked order-9 artifact using the independent graph
helpers from the preceding order-9 audit.
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

from scratch_theory_minimal_order9_mate_lift_audit import (
    canonical_mark,
    decode,
    degree_mask,
    encode,
    graph,
    norm,
    violations,
)


ARTIFACT = Path("scratch_theory_one_d_order11_sync_lift.json")
ORDER9 = Path("scratch_theory_minimal_order9_mate_lift.json")
WAVE159 = Path(
    "external_conway99_research/attempts/wave159-four-root-cut-loop/"
    "exact-witness-after-fifteen-cuts.json"
)
OUTPUT = Path("scratch_theory_one_d_order11_sync_lift_audit.json")


def atomic_json(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def matchings(left, right):
    answer = []
    for size in range(4):
        for domain in itertools.combinations(left, size):
            for image_set in itertools.combinations(right, size):
                for image in itertools.permutations(image_set):
                    answer.append(frozenset(norm(source, target)
                                            for source, target in zip(domain, image)))
    assert len(answer) == len(set(answer)) == 34
    return tuple(answer)


def role_actions():
    identity = tuple(range(11))
    source_swap = list(identity)
    source_swap[1], source_swap[3] = 3, 1
    source_swap[2], source_swap[4] = 4, 2
    flip = list(identity)
    for left, right in ((1, 2), (3, 4), (6, 7), (9, 10)):
        flip[left], flip[right] = right, left
    both = tuple(source_swap[flip[index]] for index in range(11))
    answer = frozenset((identity, tuple(source_swap), tuple(flip), both))
    assert len(answer) == 4
    return answer


def move_edges(edges, permutation):
    return frozenset(norm(permutation[left], permutation[right])
                     for left, right in edges)


def row_lookup(order9):
    answer = {}
    for row in order9["marked_lift_schema"]["rows"]:
        key = row["canonical_mark_key"]
        key = (int(key[0]), int(key[1]), tuple(map(int, key[2])),
               tuple(map(int, key[3])), tuple(map(int, key[4])))
        answer[(int(row["order8_canonical_mask"]), key)] = row["row_id"]
    assert len(answer) == 11
    return answer


def deletion_row(edges, source, removed, lookup):
    keep9 = [vertex for vertex in range(11) if vertex not in removed]
    relabel9 = {vertex: index for index, vertex in enumerate(keep9)}
    edges9 = frozenset(norm(relabel9[left], relabel9[right])
                       for left, right in edges
                       if left not in removed and right not in removed)
    mark9 = (
        relabel9[0], relabel9[5],
        tuple(sorted(relabel9[vertex] for vertex in source)),
        tuple(sorted(relabel9[vertex] for vertex in (5, 6, 7))),
        tuple(sorted((relabel9[9], relabel9[10]))),
    )
    mate = relabel9[8]
    keep8 = [vertex for vertex in range(9) if vertex != mate]
    relabel8 = {vertex: index for index, vertex in enumerate(keep8)}
    edges8 = frozenset(norm(relabel8[left], relabel8[right])
                       for left, right in edges9 if mate not in (left, right))
    mark8 = (
        relabel8[mark9[0]], relabel8[mark9[1]],
        tuple(sorted(relabel8[vertex] for vertex in mark9[2])),
        tuple(sorted(relabel8[vertex] for vertex in mark9[3])),
        tuple(sorted(relabel8[vertex] for vertex in mark9[4])),
    )
    canonical = canonical_mark(8, edges8, mark8)
    return lookup[canonical], encode(edges9, 9), degree_mask(9, edges9)


def enumerate_valid(other_state, lookup):
    source_a = (0, 1, 2)
    source_b = (0, 3, 4)
    other = (5, 6, 7)
    forced = frozenset(norm(*edge) for edge in {
        (0, 1), (0, 2), (1, 2), (0, 3), (0, 4), (3, 4),
        (5, 6), (5, 7), (6, 7), (8, 9), (8, 10), (9, 10),
        (1, 9), (2, 10), (3, 9), (4, 10), (6, 9), (7, 10),
    })
    if other_state == "P":
        forced |= {norm(5, 8)}
    left = matchings(source_a, other)
    right = matchings(source_b, other)
    examined = 0
    valid = {}
    for first, second in itertools.product(left, right):
        if ((0, 5) in first) != ((0, 5) in second):
            continue
        examined += 1
        edges = forced | first | second
        if violations(11, edges):
            continue
        first_row = deletion_row(edges, source_a, {3, 4}, lookup)
        second_row = deletion_row(edges, source_b, {1, 2}, lookup)
        valid[edges] = (first_row, second_row)
    assert examined == 778 and len(valid) == (50 if other_state == "G" else 18)
    return forced, valid


def quotient(valid):
    actions = role_actions()
    unseen = set(valid)
    answer = {}
    while unseen:
        representative = min(unseen, key=lambda edges: encode(edges, 11))
        orbit = frozenset(move_edges(representative, action) for action in actions)
        assert orbit <= set(valid)
        unseen -= orbit
        deletions = valid[representative]
        rows = Counter([deletions[0][0], deletions[1][0]])
        answer[encode(representative, 11)] = {
            "orbit_size": len(orbit),
            "incidence": sorted(rows.items()),
            "deletion_records": deletions,
        }
    return answer


def rank(matrix, modulus=None):
    rows = [[Fraction(value) if modulus is None else value % modulus
             for value in row] for row in matrix]
    found = 0
    for column in range(len(rows[0])):
        pivot = next((row for row in range(found, len(rows)) if rows[row][column]), None)
        if pivot is None:
            continue
        rows[found], rows[pivot] = rows[pivot], rows[found]
        if modulus is None:
            inverse = 1 / rows[found][column]
        else:
            inverse = pow(rows[found][column], -1, modulus)
        rows[found] = [(value * inverse) if modulus is None
                       else value * inverse % modulus for value in rows[found]]
        for row in range(len(rows)):
            if row == found or not rows[row][column]:
                continue
            scale = rows[row][column]
            rows[row] = [(left - scale * right) if modulus is None
                         else (left - scale * right) % modulus
                         for left, right in zip(rows[row], rows[found])]
        found += 1
    return found


def det(matrix):
    work = [list(map(int, row)) for row in matrix]
    size = len(work)
    sign = 1
    previous = 1
    for column in range(size - 1):
        pivot = next((row for row in range(column, size) if work[row][column]), None)
        if pivot is None:
            return 0
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            sign *= -1
        value = work[column][column]
        for row in range(column + 1, size):
            for target in range(column + 1, size):
                numerator = work[row][target] * value - work[row][column] * work[column][target]
                assert numerator % previous == 0
                work[row][target] = numerator // previous
            work[row][column] = 0
        previous = value
    return sign * work[-1][-1]


def minor_gcd(matrix):
    active = [row for row in matrix if any(row)]
    size = len(active)
    value = 0
    for columns in itertools.combinations(range(len(active[0])), size):
        determinant = det([[row[column] for column in columns] for row in active])
        value = math.gcd(value, abs(determinant))
    return value


def matrix_from_types(row_ids, types):
    matrix = [[0] * len(types) for _ in row_ids]
    index = {row_id: position for position, row_id in enumerate(row_ids)}
    for column, row in enumerate(types):
        for row_id, value in row["order9_incidence"]:
            matrix[index[row_id]][column] = int(value)
    return matrix


def facet_values(matrix, row_ids, state):
    index = {row_id: position for position, row_id in enumerate(row_ids)}
    if state == "G":
        forms = (
            {"E019O0": 1, "E515O0": -1},
            {"N057O0": 1, "N060O0": 1, "N525O0": -1},
        )
    else:
        forms = (
            {"E019O0": 1, "E515O0": -1},
            {"N060O0": 1, "N525O0": -1},
        )
    return [[sum(coefficient * matrix[index[row_id]][column]
                 for row_id, coefficient in form.items())
             for column in range(len(matrix[0]))] for form in forms]


def cone_generator_structure(matrix, row_ids, state):
    """Independently certify that the displayed Farkas facets are complete."""

    index = {row_id: position for position, row_id in enumerate(row_ids)}
    columns = [tuple(matrix[row][column] for row in range(len(row_ids)))
               for column in range(len(matrix[0]))]
    patterns = set(columns)

    def vector(entries):
        value = [0] * len(row_ids)
        for row_id, coefficient in entries.items():
            value[index[row_id]] = coefficient
        return tuple(value)

    if state == "G":
        loop_rows = ("E019O0", "E561O0", "N057O0", "N060O0",
                     "N442O0", "N593O0")
        exceptional = {
            "E515O0": ({"E019O0": 1, "E515O0": 1},),
            "N525O0": (
                {"N057O0": 1, "N525O0": 1},
                {"N060O0": 1, "N525O0": 1},
            ),
        }
    else:
        loop_rows = ("E019O0", "E561O0", "N060O0", "N593O0")
        exceptional = {
            "E515O0": ({"E019O0": 1, "E515O0": 1},),
            "N525O0": ({"N060O0": 1, "N525O0": 1},),
        }
    assert all(vector({row_id: 2}) in patterns for row_id in loop_rows)
    for exceptional_row, allowed in exceptional.items():
        allowed_patterns = {vector(entries) for entries in allowed}
        assert allowed_patterns <= patterns
        assert all(column in allowed_patterns
                   for column in patterns if column[index[exceptional_row]])
    return True


def main() -> None:
    data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    order9 = json.loads(ORDER9.read_text(encoding="utf-8"))
    wave = json.loads(WAVE159.read_text(encoding="utf-8"))
    assert data["status"] == "ONE_D_ORDER11_SYNCHRONIZATION_LIFT_PASS"
    lookup = row_lookup(order9)
    row_ids = [row["row_id"] for row in order9["marked_lift_schema"]["rows"]]
    audits = {}
    all_new_zero = []
    for state, section, matrix_key in (
            ("G", "G_census", "DG"), ("P", "P_census", "DP")):
        forced, valid = enumerate_valid(state, lookup)
        rebuilt = quotient(valid)
        stored_types = data[section]["rooted_role_types"]
        stored = {
            int(row["role_canonical_labelled_order11_mask"]): row
            for row in stored_types
        }
        assert set(rebuilt) == set(stored)
        for mask, direct in rebuilt.items():
            row = stored[mask]
            assert direct["orbit_size"] == int(row["role_orbit_size"])
            assert direct["incidence"] == [
                (str(row_id), int(value)) for row_id, value in row["order9_incidence"]
            ]
            expected_deletions = {
                (record["order9_row_id"], int(record["labelled_order9_mask"]),
                 int(record["degree_cell_canonical_order9_mask"]))
                for record in row["order9_deletions"]
            }
            direct_deletions = {
                (record[0], int(record[1]), int(record[2]))
                for record in direct["deletion_records"]
            }
            assert direct_deletions == expected_deletions
        assert sum(value["orbit_size"] for value in rebuilt.values()) == len(valid)

        matrix = matrix_from_types(row_ids, stored_types)
        summary = data["synchronization_matrices"][matrix_key]
        assert rank(matrix) == int(summary["rank_over_Q"])
        assert rank(matrix, 2) == int(summary["rank_mod_2"])
        assert rank(matrix, 3) == int(summary["rank_mod_3"])
        assert minor_gcd(matrix) == int(summary["full_rank_minor_gcd"]) == 4
        assert all(sum(matrix[row][column] for row in range(len(row_ids))) == 2
                   for column in range(len(stored_types)))
        assert all(value >= 0 for values in facet_values(matrix, row_ids, state)
                   for value in values)
        assert cone_generator_structure(matrix, row_ids, state)
        all_new_zero.extend(summary["new_zero_cells_beyond_order9_pair_upper"])
        audits[state] = {
            "candidate_patterns": 778,
            "pair_upper_feasible_labelled": len(valid),
            "rooted_role_types": len(rebuilt),
            "orbit_mass": sum(value["orbit_size"] for value in rebuilt.values()),
            "matrix_rank_Q_mod2_mod3": [rank(matrix), rank(matrix, 2), rank(matrix, 3)],
            "full_minor_gcd": minor_gcd(matrix),
            "all_column_sums_two": True,
            "stored_cone_facets_nonnegative_on_every_generator": True,
            "stored_cone_facets_complete_from_generator_structure": True,
        }
    assert len(all_new_zero) == len({(row["row_id"], row["state_pair"])
                                     for row in all_new_zero}) == 10

    # Replay both the normalized rational boundary and its homogeneous
    # integer scaling without trusting the producer's arithmetic.
    counts = {int(row["canonical_mask"]): Fraction(row["count"])
              for row in wave["x8_support"]}
    expected_gg = {}
    for row in order9["marked_lift_schema"]["rows"]:
        expected_gg[row["row_id"]] = (
            int(row["marked_orbit_size"])
            * counts.get(int(row["order8_canonical_mask"]), Fraction())
        )
    stored_boundary = data["T0_exact_boundary"]
    stored_gg = {row_id: Fraction(value) for row_id, value in
                 stored_boundary["assignment"]["L_GG_by_deletion_row"].items()}
    assert stored_gg == expected_gg
    assert sum(stored_gg.values(), Fraction()) == 91476
    scale = int(stored_boundary["homogeneous_integer_ray"]["scale"])
    assert scale == math.lcm(*(value.denominator for value in stored_gg.values()),
                             *(Fraction(value).denominator for value in
                               stored_boundary["assignment"]["H9_X_X_solution"]))
    assert all(value * scale == int(value * scale) for value in stored_gg.values())
    assert stored_boundary["assignment"]["all_one_D_order11_type_variables"] == 0
    assert stored_boundary["assignment"]["all_other_order9_state_cells"] == 0

    result = {
        "status": "ONE_D_ORDER11_SYNCHRONIZATION_LIFT_INDEPENDENT_AUDIT_PASS",
        "input_sha256": {str(path): sha256(path)
                         for path in (ARTIFACT, ORDER9, WAVE159)},
        "independent_census": audits,
        "new_zero_cells_replayed": 10,
        "T0_boundary": {
            "ordered_GG_mass": 91476,
            "all_one_D_variables": 0,
            "homogeneous_integer_scale": scale,
            "all_sync_equations_and_cone_facets_pass": True,
            "T0_excluded": False,
        },
        "checks": {
            "producer_not_imported": True,
            "all_778_matching_pairs_per_state_rebuilt": True,
            "pair_upper_recomputed": True,
            "role_orbits_recomputed": True,
            "both_order9_deletions_recomputed": True,
            "rational_and_modular_ranks_recomputed": True,
            "full_minor_gcd_recomputed": True,
            "explicit_nonnegative_boundary_recomputed": True,
        },
        "scope": (
            "Restricted forced-union replay only; no ambient order-eleven "
            "class stream or Conway graph is constructed."
        ),
    }
    atomic_json(OUTPUT, result)
    print(json.dumps({
        "status": result["status"],
        "G_types": audits["G"]["rooted_role_types"],
        "P_types": audits["P"]["rooted_role_types"],
        "new_zero_cells": 10,
        "T0_excluded": False,
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
