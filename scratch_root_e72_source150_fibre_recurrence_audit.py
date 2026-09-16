"""Independent audit of the E72 source150 fibre-summed recurrence filter.

The target implementation is never imported.  Basic source150 parsing and
exact arithmetic come from the separately written root norm/collision audit;
all recurrence loads, exceptional degree rows, tuple sums, and the projected
finite certificate are rebuilt here.
"""

from __future__ import annotations

import itertools
import json
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

import scratch_root_e72_source150_norm_collision_audit as independent


LOCAL = independent.LOCAL
CATALOG = independent.CATALOG
GRAM = independent.GRAM
NORM_AUDIT_SCRIPT = Path("scratch_root_e72_source150_norm_collision_audit.py")
NORM_AUDIT = Path("scratch_root_e72_source150_norm_collision_audit.json")
RECURRENCE_SCRIPT = Path("scratch_theory_e72_source150_fibre_recurrence_filter.py")
RECURRENCE_OUTPUT = Path("scratch_theory_e72_source150_fibre_recurrence_filter.json")
CERTIFICATE_SCRIPT = Path("scratch_theory_e72_source150_recurrence_certificate.py")
CERTIFICATE = Path("scratch_theory_e72_source150_recurrence_certificate.json")
OUTPUT = Path("scratch_root_e72_source150_fibre_recurrence_audit.json")
REPORT = Path("scratch_root_e72_source150_fibre_recurrence_audit.md")


def scale(value, vector):
    return tuple(value * coordinate for coordinate in vector)


def covector(vector, matrix):
    return tuple(sum((matrix[row][column] * vector[column]
                      for column in range(3)), Fraction(0))
                 for row in range(3))


def flatten_covectors(vectors, matrix):
    return tuple(value for vector in vectors
                 for value in covector(vector, matrix))


def matrix_rank(matrix):
    rows = [list(map(Fraction, row)) for row in matrix]
    rank = 0
    columns = len(rows[0]) if rows else 0
    for column in range(columns):
        pivot = next((index for index in range(rank, len(rows))
                      if rows[index][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        divisor = rows[rank][column]
        rows[rank] = [value / divisor for value in rows[rank]]
        for index in range(len(rows)):
            if index == rank or not rows[index][column]:
                continue
            multiple = rows[index][column]
            rows[index] = [left - multiple * right
                           for left, right in zip(rows[index], rows[rank])]
        rank += 1
    return rank


def ordinary_load_options_ordered(patterns, disjoint, vectors, matrix):
    """Enumerate ordered tuples, independently of the target's multisets."""

    answer = set()
    valid_multisets = set()
    for chosen in itertools.product(patterns, repeat=4):
        if any(sum(row[target] for row in chosen) != 4 for target in disjoint):
            continue
        valid_multisets.add(tuple(sorted(chosen)))
        loads = [[Fraction(0)] * 3 for _ in vectors]
        for row in chosen:
            q = independent.vector_sum(
                scale(row[index], vectors[index]) for index in range(len(vectors))
            )
            for source in disjoint:
                for coordinate in range(3):
                    loads[source][coordinate] += row[source] * q[coordinate]
        answer.add(flatten_covectors(tuple(map(tuple, loads)), matrix))
    assert answer
    return tuple(sorted(answer)), len(valid_multisets)


def exceptional_degrees(
    vertex, source_fibre, adjacency, vertices, exceptional, ordinary_supports,
):
    """Solve one exceptional vertex's pointwise root-group equations."""

    source_support = exceptional[source_fibre]
    disjoint = tuple(index for index, target in enumerate(exceptional)
                     if set(source_support).isdisjoint(target))
    known = [0] * len(exceptional)
    for other in adjacency[vertex]:
        known[vertices[other][2]] += 1
    assert all(known[target] == 0 for target in disjoint)

    forced_ordinary = [0] * 7
    disjoint_ordinary_count = 0
    for ordinary in ordinary_supports:
        if set(source_support).isdisjoint(ordinary):
            disjoint_ordinary_count += 1
            for group in ordinary:
                forced_ordinary[group] += 1
    # Ten supports are disjoint from a fixed K7 edge; three are exceptional
    # in this K_{2,4} row, leaving seven ordinary C4 fibres.
    assert disjoint_ordinary_count == 7

    choices = []
    for values in itertools.product(range(5), repeat=len(disjoint)):
        degrees = list(known)
        for target, value in zip(disjoint, values):
            degrees[target] = value
        if all(
            sum(degrees[index] for index, support_ in enumerate(exceptional)
                if group in support_) + forced_ordinary[group]
            == (2 if group in source_support else 4)
            for group in range(7)
        ):
            choices.append(tuple(degrees))
    assert len(choices) == 1
    return choices[0]


def bounded_tuple_sum(option_rows, target):
    """Independent exact Minkowski DP with suffix coordinate intervals."""

    dimension = len(target)
    suffix_bounds = [None] * (len(option_rows) + 1)
    suffix_bounds[-1] = ((Fraction(0),) * dimension,
                         (Fraction(0),) * dimension)
    for index in range(len(option_rows) - 1, -1, -1):
        following_min, following_max = suffix_bounds[index + 1]
        lower = tuple(min(option[coordinate] for option in option_rows[index])
                      + following_min[coordinate]
                      for coordinate in range(dimension))
        upper = tuple(max(option[coordinate] for option in option_rows[index])
                      + following_max[coordinate]
                      for coordinate in range(dimension))
        suffix_bounds[index] = lower, upper

    states = {(Fraction(0),) * dimension}
    peak = 1
    for index, options in enumerate(option_rows):
        lower, upper = suffix_bounds[index + 1]
        following = set()
        for state in states:
            for option in options:
                candidate = tuple(left + right
                                  for left, right in zip(state, option))
                if all(candidate[coordinate] + lower[coordinate]
                       <= target[coordinate]
                       <= candidate[coordinate] + upper[coordinate]
                       for coordinate in range(dimension)):
                    following.add(candidate)
        states = following
        peak = max(peak, len(states))
        if not states:
            break
    return target in states, peak, len(states)


def projected_sum(option_rows, target, coordinates):
    states = {(Fraction(0),) * len(coordinates)}
    history = [1]
    for options in option_rows:
        projected = {
            tuple(option[index] for index in coordinates) for option in options
        }
        states = {
            tuple(left + right for left, right in zip(state, option))
            for state in states for option in projected
        }
        history.append(len(states))
    projected_target = tuple(target[index] for index in coordinates)
    return projected_target in states, states, history


def exact_number(value):
    value = Fraction(value)
    return int(value) if value.denominator == 1 else str(value)


def main() -> None:
    local_doc = json.loads(LOCAL.read_text(encoding="utf-8"))
    catalog_doc = json.loads(CATALOG.read_text(encoding="utf-8"))
    gram_doc = json.loads(GRAM.read_text(encoding="utf-8"))
    norm_audit = json.loads(NORM_AUDIT.read_text(encoding="utf-8"))
    recurrence = json.loads(RECURRENCE_OUTPUT.read_text(encoding="utf-8"))
    certificate = json.loads(CERTIFICATE.read_text(encoding="utf-8"))

    assert norm_audit["status"] == "SOURCE150_NORM_COLLISION_AUDIT_PASS"
    assert norm_audit["filter_result"]["passing_local_orbits"] == 5943
    assert norm_audit["filter_result"]["passing_labelled_mass"] == 2_244_608
    assert recurrence["status"] == "EXACT_FIBRE_SUMMED_Q_RECURRENCE_FILTER_COMPLETE"
    for path in (LOCAL, CATALOG, GRAM):
        assert recurrence["inputs"][str(path)] == independent.sha256(path)

    row = next(item for item in local_doc["support_rows"]
               if item["partition"] == [2, 2, 2, 2, 1, 1, 1, 1]
               and item["compression_orbit_index"] == 0)
    exceptional = tuple(tuple(item["support"])
                        for item in row["exceptional_supports"])
    assert exceptional == (
        (0, 2), (0, 3), (0, 4), (0, 5),
        (1, 2), (1, 3), (1, 4), (1, 5),
    )
    ordinary_supports = tuple(support_ for support_ in independent.ALL_SUPPORTS
                              if support_ not in exceptional)
    overlap_pairs = tuple(pair for pair in itertools.combinations(range(8), 2)
                          if not set(exceptional[pair[0]]).isdisjoint(
                              exceptional[pair[1]]))
    disjoint_pairs = tuple(pair for pair in itertools.combinations(range(8), 2)
                           if set(exceptional[pair[0]]).isdisjoint(
                               exceptional[pair[1]]))
    assert len(ordinary_supports) == 13
    assert len(overlap_pairs) == 16 and len(disjoint_pairs) == 12

    plain_vertices = tuple(
        tuple(sorted((2 * first + first_bit, 2 * second + second_bit)))
        for first, second in exceptional
        for first_bit, second_bit in itertools.product((0, 1), repeat=2)
    )
    fibre_of = {vertex: exceptional.index(independent.support(vertex))
                for vertex in plain_vertices}
    vertices = tuple((vertex[0], vertex[1], fibre_of[vertex])
                     for vertex in plain_vertices)
    vertex_index = {vertex: index for index, vertex in enumerate(plain_vertices)}
    vertices_by_fibre = tuple(
        tuple(index for index, vertex in enumerate(plain_vertices)
              if fibre_of[vertex] == fibre)
        for fibre in range(8)
    )

    catalog = [entry for entry in catalog_doc["macro_entries"]
               if entry["source_row_index"] == 150]
    by_key = {}
    for entry in catalog:
        key = independent.catalog_key(entry, overlap_pairs)
        assert key not in by_key
        by_key[key] = entry
    assert len(by_key) == 21
    gram_rows = {
        (entry["state_orbit_number"],
         entry["signature_stabilizer_orbit_number"],
         entry["signature_stabilizer_canonical"]): entry
        for entry in gram_doc["rows"] if entry["source_row_index"] == 150
    }

    vectors = (
        (Fraction(1), Fraction(1), Fraction(1)),
        (Fraction(-1), Fraction(0), Fraction(0)),
        (Fraction(0), Fraction(-1), Fraction(0)),
        (Fraction(0), Fraction(0), Fraction(-1)),
        (Fraction(-1), Fraction(-1), Fraction(-1)),
        (Fraction(1), Fraction(0), Fraction(0)),
        (Fraction(0), Fraction(1), Fraction(0)),
        (Fraction(0), Fraction(0), Fraction(1)),
    )
    assert independent.vector_sum(vectors) == (0, 0, 0)
    assert all(independent.vector_sum(
        vectors[index] for index, support_ in enumerate(exceptional)
        if group in support_
    ) == (0, 0, 0) for group in range(7))

    ordinary_patterns = {
        ordinary: independent.ordinary_vertex_patterns(
            ordinary, exceptional, ordinary_supports
        )
        for ordinary in ordinary_supports
    }
    ordinary_options = {}
    matrices = {}
    matrix_ranks = {}
    per_macro = defaultdict(Counter)
    target_histogram = Counter()
    target_cache = {}
    survivor_by_mask = {record[0]: record for record in recurrence["survivors"]}
    assert len(survivor_by_mask) == len(recurrence["survivors"])
    controls = {control["record_number"]: control
                for control in recurrence["controls"]}
    assert set(controls) == set(range(30))
    unique_degree_rows_checked = 0
    block_margin_checks = 0

    for number, representative in enumerate(row["representatives"]):
        local_key = independent.representative_key(
            representative["edges"], fibre_of, overlap_pairs
        )
        entry = by_key[local_key]
        assert entry["signature_stabilizer_canonical"]
        macro = (entry["state_orbit_number"],
                 entry["signature_stabilizer_orbit_number"])
        gram = gram_rows[macro + (True,)]
        matrix = tuple(tuple(Fraction(value) for value in matrix_row)
                       for matrix_row in gram["unique_H"])
        matrix_key = tuple(map(tuple, matrix))
        matrices[matrix_key] = matrix
        matrix_ranks[matrix_key] = matrix_rank(matrix)
        assert independent.exact_psd(matrix)

        if matrix_key not in ordinary_options:
            rows = []
            multiset_total = 0
            for ordinary in ordinary_supports:
                patterns, disjoint, _ = ordinary_patterns[ordinary]
                options, multiset_count = ordinary_load_options_ordered(
                    patterns, disjoint, vectors, matrix
                )
                rows.append(options)
                multiset_total += multiset_count
            ordinary_options[matrix_key] = (tuple(rows), multiset_total)
        option_rows, _ = ordinary_options[matrix_key]
        assert [len(options) for options in option_rows] \
            == [1, 1, 1, 3, 3, 3, 11, 3, 3, 11, 3, 11, 11]

        adjacency = [set() for _ in vertices]
        for raw_edge in representative["edges"]:
            left, right = independent.edge_key(raw_edge)
            first, second = vertex_index[left], vertex_index[right]
            assert second not in adjacency[first]
            adjacency[first].add(second)
            adjacency[second].add(first)

        block_totals = {
            tuple(sorted((int(left), int(right)))): int(value)
            for left, right, value
            in representative["disjoint_Gram_profile"]["targets"]
        }
        assert set(block_totals) == set(disjoint_pairs)

        degrees = []
        for vertex in range(len(vertices)):
            source_fibre = vertices[vertex][2]
            degrees.append(exceptional_degrees(
                vertex, source_fibre, adjacency, vertices, exceptional,
                ordinary_supports,
            ))
            unique_degree_rows_checked += 1
        degrees = tuple(degrees)

        # The unique pointwise rows must recover both margins of every one of
        # the twelve unmaterialized Gram blocks.
        for first, second in disjoint_pairs:
            first_margin = sum(degrees[vertex][second]
                               for vertex in vertices_by_fibre[first])
            second_margin = sum(degrees[vertex][first]
                                for vertex in vertices_by_fibre[second])
            assert first_margin == second_margin == block_totals[(first, second)]
            block_margin_checks += 2

        q_exceptional = tuple(
            independent.vector_sum(
                scale(degrees[vertex][target], vectors[target])
                for target in range(8)
            )
            for vertex in range(len(vertices))
        )

        raw_targets = []
        for source_fibre, fibre_vertices in enumerate(vertices_by_fibre):
            rhs = scale(48, vectors[source_fibre])
            q_self = independent.vector_sum(
                q_exceptional[vertex] for vertex in fibre_vertices
            )
            exceptional_load = independent.vector_sum(
                scale(degrees[vertex][source_fibre], q_exceptional[vertex])
                for vertex in range(len(vertices))
            )
            raw_targets.append(tuple(
                rhs[coordinate] - q_self[coordinate]
                - exceptional_load[coordinate]
                for coordinate in range(3)
            ))
        target = flatten_covectors(tuple(raw_targets), matrix)

        cache_key = (matrix_key, target)
        if cache_key not in target_cache:
            target_cache[cache_key] = bounded_tuple_sum(option_rows, target)
        feasible, peak, final_states = target_cache[cache_key]

        stats = per_macro[macro]
        stats["input_orbits"] += 1
        stats["input_mass"] += representative["orbit_size"]
        if feasible:
            stats["passing_orbits"] += 1
            stats["passing_mass"] += representative["orbit_size"]
        else:
            stats["rejected_orbits"] += 1
            stats["rejected_mass"] += representative["orbit_size"]
        target_histogram[(macro, tuple(str(value) for value in target))] += 1

        reported_survivor = survivor_by_mask.get(representative["mask_hex"])
        if feasible:
            assert reported_survivor == [
                representative["mask_hex"], representative["orbit_size"],
                representative["Q"], list(macro),
            ]
        else:
            assert reported_survivor is None

        if number in controls:
            control = controls[number]
            assert control["macro"] == list(macro)
            assert control["target"] == [str(value) for value in target]
            assert control["ordinary_option_counts"] \
                == [len(options) for options in option_rows]
            assert control["feasible"] == feasible
            assert control["DP_peak_states"] == peak
            assert control["DP_final_states"] == final_states

    assert len(matrices) == len(target_cache) == 5
    assert sorted(matrix_ranks.values()) == [2, 3, 3, 3, 3]
    assert unique_degree_rows_checked == 5943 * 32
    assert block_margin_checks == 5943 * 12 * 2

    expected_per_macro = {
        f"{key[0]}:{key[1]}": dict(sorted(stats.items()))
        for key, stats in sorted(per_macro.items())
    }
    assert expected_per_macro == recurrence["per_macro"]
    expected_histogram = {
        f"macro={key[0][0]}:{key[0][1]};target={','.join(key[1])}": value
        for key, value in sorted(target_histogram.items())
    }
    assert expected_histogram == recurrence["distinct_target_histogram"]

    summary = recurrence["summary"]
    assert summary["input_orbits"] == 5943
    assert summary["input_mass"] == 2_244_608
    assert summary["passing_orbits"] == 4935
    assert summary["passing_mass"] == 1_851_392
    assert summary["rejected_orbits"] == 1008
    assert summary["distinct_Gram_H"] == 5
    assert summary["distinct_recurrence_targets"] == 5
    rejected_macros = {
        key for key, stats in per_macro.items() if stats["rejected_orbits"]
    }
    assert rejected_macros == {(0, 2), (3, 2)}
    assert all(per_macro[key]["passing_orbits"] == 0 for key in rejected_macros)
    assert sum(per_macro[key]["rejected_mass"] for key in rejected_macros) \
        == 393_216

    # Independently check the compact three-coordinate obstruction.  This is
    # unbounded Minkowski enumeration, separate from the 24-coordinate DP.
    assert certificate["status"] == "EXACT_PROJECTED_RECURRENCE_CERTIFICATE_COMPLETE"
    certificate_matrix = tuple(tuple(Fraction(value) for value in row_)
                               for row_ in certificate["Gram_H"])
    certificate_target = tuple(Fraction(value)
                               for value in certificate["full_target"])
    assert certificate_matrix in matrices
    assert matrix_rank(certificate_matrix) == 3
    rejected_targets = {
        target for (matrix_key, target), result in target_cache.items()
        if not result[0] and matrix_key == certificate_matrix
    }
    assert rejected_targets == {certificate_target}
    certificate_rows = ordinary_options[certificate_matrix][0]
    assert certificate["ordinary_support_order"] \
        == [list(value) for value in ordinary_supports]
    assert certificate["option_counts"] \
        == [len(options) for options in certificate_rows]

    first_failure = None
    tested = 0
    for size in range(1, 4):
        for coordinates in itertools.combinations(range(24), size):
            tested += 1
            feasible, states, history = projected_sum(
                certificate_rows, certificate_target, coordinates
            )
            if not feasible:
                first_failure = coordinates, states, history
                break
        if first_failure is not None:
            break
    assert tested == certificate["subsets_tested_through_first_minimal_failure"] \
        == 302
    coordinates, states, history = first_failure
    cert = certificate["certificate"]
    assert coordinates == tuple(cert["coordinates"]) == (0, 1, 3)
    projected_target = tuple(certificate_target[index] for index in coordinates)
    assert cert["minimum_coordinate_count"] == 3
    assert cert["target"] == [exact_number(value) for value in projected_target]
    assert cert["attainable_state_count"] == len(states) == 31768
    assert cert["state_count_after_each_of_13_fibres"] == history
    projected_by_support = []
    for support_, options in zip(ordinary_supports, certificate_rows):
        projected_by_support.append({
            "support": list(support_),
            "options": [[exact_number(value) for value in option]
                        for option in sorted({
                            tuple(row[index] for index in coordinates)
                            for row in options
                        })],
        })
    assert cert["projected_options_by_ordinary_support"] == projected_by_support
    nearest = sorted(
        states,
        key=lambda state: (
            sum(abs(left - right) for left, right
                in zip(state, projected_target)), state,
        ),
    )[:50]
    assert cert["nearest_attainable_values"] \
        == [[exact_number(value) for value in state] for state in nearest]
    conditional = sorted({state[2] for state in states
                          if state[:2] == projected_target[:2]})
    assert cert["third_values_when_first_two_equal_target"] \
        == [exact_number(value) for value in conditional]

    result = {
        "status": "SOURCE150_FIBRE_RECURRENCE_AUDIT_PASS",
        "source_row_index": 150,
        "inputs": {str(path): independent.sha256(path) for path in (
            LOCAL, CATALOG, GRAM, NORM_AUDIT_SCRIPT, NORM_AUDIT,
            RECURRENCE_SCRIPT, RECURRENCE_OUTPUT,
            CERTIFICATE_SCRIPT, CERTIFICATE,
        )},
        "coverage": {
            "input_local_orbits": 5943,
            "input_labelled_mass": 2_244_608,
            "passing_local_orbits": 4935,
            "passing_labelled_mass": 1_851_392,
            "rejected_local_orbits": 1008,
            "rejected_labelled_mass": 393_216,
            "fully_rejected_macro_orbits": [[0, 2], [3, 2]],
            "all_other_fifteen_macro_orbits_pass": True,
        },
        "independent_checks": {
            "exceptional_pointwise_degree_rows_unique": unique_degree_rows_checked,
            "disjoint_exceptional_block_margin_equalities": block_margin_checks,
            "ordinary_option_counts": [1, 1, 1, 3, 3, 3, 11, 3, 3, 11, 3, 11, 11],
            "distinct_exact_Gram_matrices": len(matrices),
            "Gram_matrix_ranks": sorted(matrix_ranks.values()),
            "distinct_full_recurrence_DPs": len(target_cache),
            "reported_controls_reproduced_exactly": len(controls),
            "projected_certificate_coordinates": list(coordinates),
            "projected_attainable_states": len(states),
            "all_one_and_two_coordinate_projections_feasible": True,
            "first_lexicographic_three_coordinate_projection_infeasible": True,
        },
        "soundness": {
            "recurrence": (
                "B^2+B=12I+2J-PP^T and sum(c)=P^T c=0 imply "
                "(B+I)q=12c for q=Bc. Summing its four rows over each "
                "exceptional fibre gives the eight audited vector equations."
            ),
            "singular_H": (
                "All five H are exact PSD matrices; their ranks are 2,3,3,3,3. "
                "Every three-coordinate equality is compared after left "
                "multiplication by H. For PSD H, H*diff=0 iff diff represents "
                "the zero Gram vector, so the rank-two case is not overconstrained."
            ),
            "ordinary_exceptional_direction": (
                "For each disjoint ordinary/exceptional block only the forced "
                "exceptional-side degree-one function is used. Its ordinary-side "
                "row degrees lie in 0..4 and sum to four; no ordinary degree-one "
                "converse is assumed."
            ),
            "relaxation_boundary": (
                "The test sums four recurrence rows per exceptional fibre and "
                "forgets labelled bipartite matrices and pointwise recurrence "
                "rows. These omissions enlarge, rather than shrink, feasibility."
            ),
        },
        "claim_boundary": (
            "The 393,216 rejected labelled macro mass is excluded by an exact "
            "finite necessary-condition enumeration, independently replayed and "
            "backed by a 31,768-state projected obstruction. This is not a "
            "proof-assistant certificate. The remaining 1,851,392 source150 mass "
            "is unresolved and no graph is constructed."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text("\n".join([
        "# E72 source150 fibre-recurrence independent audit",
        "",
        "Status: **SOURCE150_FIBRE_RECURRENCE_AUDIT_PASS**.",
        "",
        "The full 5,943-orbit / 2,244,608-mass input was replayed without "
        "importing the recurrence implementation. Exactly 1,008 orbits of mass "
        "393,216 fail; these are the complete macro orbits `(0,2)` and `(3,2)`. "
        "The remaining 4,935 orbits of mass 1,851,392 pass and remain open.",
        "",
        "All 190,176 exceptional pointwise degree rows are unique and recover "
        "both Gram-D margins of all twelve disjoint exceptional blocks. The "
        "thirteen ordinary fibres independently give option counts "
        "`1,1,1,3,3,3,11,3,3,11,3,11,11`.",
        "",
        "One of the five PSD Gram matrices has rank two. Every recurrence "
        "difference is compared as `H*diff=0`; for PSD `H` this is exactly "
        "equality of represented Gram vectors and does not impose spurious "
        "coordinate equality. The ordinary--exceptional condition remains "
        "one-sided: exceptional degree one, ordinary degree 0 through 4.",
        "",
        "The rejected target also has an independently reconstructed minimal "
        "three-coordinate obstruction at coordinates `(0,1,3)`: its projected "
        "Minkowski sum has 31,768 attainable states and omits the target.",
        "",
        "Boundary: this is an exact executable finite-enumeration audit, not a "
        "proof-assistant certificate. It does not resolve the passing mass or "
        "construct an srg(99,14,1,2).",
        "",
    ]), encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "input_orbits": 5943,
        "rejected_orbits": 1008,
        "rejected_mass": 393_216,
        "passing_orbits": 4935,
        "passing_mass": 1_851_392,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
