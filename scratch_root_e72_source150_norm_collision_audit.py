"""Independent audit of the corrected E72 source150 norm/collision filter.

This file intentionally does not import the filter implementation.  It
rebuilds the source-row/canonical-macro correspondence, checks the exact Gram
algebra, enumerates the ordinary-fibre degree multisets with ordered products,
enumerates exceptional-fibre row degrees with a staged DP, and independently
replays the final norm/collision subset-sum test.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path


LOCAL = Path("scratch_general_e72_q3_gram_frontier_disjoint_gram_filtered_reps.json")
CATALOG = Path("scratch_general_e72_q3_gram_fast_expansion_macro_catalog.json")
GRAM = Path("scratch_theory_e72_macro_full_gram.json")
FILTER_SCRIPT = Path("scratch_theory_e72_source150_norm_collision_filter.py")
FILTER_OUTPUT = Path("scratch_theory_e72_source150_norm_collision_filter.json")
REMAINING = Path("scratch_general_e72_remaining_frontier_audit.json")
OUTPUT = Path("scratch_root_e72_source150_norm_collision_audit.json")
REPORT = Path("scratch_root_e72_source150_norm_collision_audit.md")

GROUPS = tuple(range(7))
ALL_SUPPORTS = tuple(itertools.combinations(GROUPS, 2))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def support(vertex) -> tuple[int, int]:
    return tuple(sorted(int(symbol) // 2 for symbol in vertex))


def edge_key(edge) -> tuple[tuple[int, int], tuple[int, int]]:
    return tuple(sorted(tuple(map(int, vertex)) for vertex in edge))


def dot(left, matrix, right) -> Fraction:
    return sum(
        (left[i] * matrix[i][j] * right[j]
         for i in range(len(left)) for j in range(len(right))),
        Fraction(0),
    )


def vector_sum(rows, dimension=3):
    rows = tuple(rows)
    return tuple(sum((row[index] for row in rows), Fraction(0))
                 for index in range(dimension))


def determinant(matrix) -> Fraction:
    size = len(matrix)
    if size == 0:
        return Fraction(1)
    if size == 1:
        return matrix[0][0]
    return sum(
        ((-1) ** column) * matrix[0][column] * determinant([
            row[:column] + row[column + 1:] for row in matrix[1:]
        ])
        for column in range(size)
    )


def exact_psd(matrix) -> bool:
    assert all(matrix[i][j] == matrix[j][i]
               for i in range(len(matrix)) for j in range(len(matrix)))
    for size in range(1, len(matrix) + 1):
        for subset in itertools.combinations(range(len(matrix)), size):
            principal = [[matrix[i][j] for j in subset] for i in subset]
            if determinant(principal) < 0:
                return False
    return True


def catalog_key(entry, overlap_pairs):
    internal = tuple(sorted(edge_key(edge) for edge in entry["internal_edges"]))
    overlap = {
        tuple(sorted((int(left), int(right)))): int(value)
        for left, right, value in entry["overlap_block_totals"]
    }
    assert set(overlap) == set(overlap_pairs)
    return internal, tuple(overlap[pair] for pair in overlap_pairs)


def representative_key(edges, fibre_of, overlap_pairs):
    internal = []
    overlap = Counter()
    for raw_edge in edges:
        left, right = edge_key(raw_edge)
        assert left != right and left in fibre_of and right in fibre_of
        first, second = fibre_of[left], fibre_of[right]
        if first == second:
            internal.append((left, right))
        else:
            pair = tuple(sorted((first, second)))
            assert pair in overlap_pairs, "stored local graph contains an unmaterialized disjoint edge"
            overlap[pair] += 1
    return tuple(sorted(internal)), tuple(overlap[pair] for pair in overlap_pairs)


def ordinary_vertex_patterns(ordinary, exceptional, ordinary_supports):
    """Independently solve the seven pointwise root-group equations."""

    disjoint = tuple(index for index, fibre in enumerate(exceptional)
                     if set(ordinary).isdisjoint(fibre))
    residual = []
    for group in GROUPS:
        target = 2 if group in ordinary else 4
        internal_c4 = 2 if group in ordinary else 0
        ordinary_matchings = sum(
            int(group in other) for other in ordinary_supports
            if set(ordinary).isdisjoint(other)
        )
        residual.append(target - internal_c4 - ordinary_matchings)
    answer = []
    for values in itertools.product(range(5), repeat=len(disjoint)):
        degrees = [0] * len(exceptional)
        for target, value in zip(disjoint, values):
            degrees[target] = value
        if all(sum(degrees[index] for index, fibre in enumerate(exceptional)
                   if group in fibre) == residual[group]
               for group in GROUPS):
            answer.append(tuple(degrees))
    assert answer
    return tuple(answer), disjoint, tuple(residual)


def ordinary_fibre_options_ordered(patterns, disjoint, vectors, matrix):
    """Use ordered 4-tuples, unlike the filter's multiset enumeration."""

    answer = set()
    valid_degree_multisets = set()
    for chosen in itertools.product(patterns, repeat=4):
        if any(sum(row[target] for row in chosen) != 4 for target in disjoint):
            continue
        # Ordering four vertices is immaterial to these two aggregate values.
        valid_degree_multisets.add(tuple(sorted(chosen)))
        collision = tuple(sum(row[target] * (row[target] - 1) // 2
                              for row in chosen)
                          for target in range(len(vectors)))
        norm = Fraction(0)
        for row in chosen:
            q = vector_sum((tuple(row[index] * coordinate
                                  for coordinate in vectors[index])
                            for index in range(len(vectors))))
            norm += dot(q, matrix, q)
        assert norm.denominator == 1 and norm >= 0
        answer.add((int(norm), collision))
    assert answer
    return tuple(sorted(answer)), len(valid_degree_multisets)


def exceptional_fibre_options_dp(
    source_fibre, fibre_vertices, adjacency, vertices, exceptional,
    ordinary_supports, block_totals, vectors, matrix,
):
    """Stage the four distinguished vertices instead of taking a product."""

    source_support = exceptional[source_fibre]
    disjoint = tuple(index for index, target in enumerate(exceptional)
                     if set(source_support).isdisjoint(target))
    target_columns = tuple(block_totals[tuple(sorted((source_fibre, target)))]
                           for target in disjoint)
    vertex_choices = []
    residual_rows = []
    pattern_counts = []

    for vertex in fibre_vertices:
        known_degrees = [0] * len(exceptional)
        for other in adjacency[vertex]:
            known_degrees[vertices[other][2]] += 1
        assert all(known_degrees[target] == 0 for target in disjoint)

        forced_ordinary = [0] * len(GROUPS)
        for ordinary in ordinary_supports:
            if set(source_support).isdisjoint(ordinary):
                for group in ordinary:
                    forced_ordinary[group] += 1
        residual = tuple(
            (2 if group in source_support else 4)
            - sum(known_degrees[index] for index, fibre in enumerate(exceptional)
                  if group in fibre)
            - forced_ordinary[group]
            for group in GROUPS
        )
        residual_rows.append(residual)

        choices = []
        for values in itertools.product(range(5), repeat=len(disjoint)):
            degrees = list(known_degrees)
            for target, value in zip(disjoint, values):
                degrees[target] = value
            if not all(sum(degrees[index] for index, fibre in enumerate(exceptional)
                           if group in fibre)
                       == (2 if group in source_support else 4)
                          - forced_ordinary[group]
                       for group in GROUPS):
                continue
            q = vector_sum((tuple(degrees[index] * coordinate
                                  for coordinate in vectors[index])
                            for index in range(len(vectors))))
            norm = dot(q, matrix, q)
            assert norm.denominator == 1 and norm >= 0
            collision = tuple(value * (value - 1) // 2 for value in degrees)
            choices.append((tuple(values), int(norm), collision))
        assert choices
        vertex_choices.append(tuple(choices))
        pattern_counts.append(len(choices))

    zero_collision = (0,) * len(exceptional)
    states = {((0,) * len(disjoint), 0, zero_collision)}
    for choices in vertex_choices:
        following = set()
        for columns, norm, collision in states:
            for values, add_norm, add_collision in choices:
                new_columns = tuple(left + right
                                    for left, right in zip(columns, values))
                if any(value > target for value, target
                       in zip(new_columns, target_columns)):
                    continue
                following.add((
                    new_columns,
                    norm + add_norm,
                    tuple(left + right for left, right
                          in zip(collision, add_collision)),
                ))
        states = following
        if not states:
            break
    options = tuple(sorted((norm, collision)
                           for columns, norm, collision in states
                           if columns == target_columns))
    return options, {
        "products_examined": __import__("math").prod(pattern_counts),
        "vertex_pattern_counts": pattern_counts,
        "residual_rows": [list(row) for row in residual_rows],
    }


def aggregate_dp(option_rows, target_norm, target_collision):
    states = {(0, (0,) * len(target_collision))}
    peak = 1
    for options in sorted(option_rows, key=len):
        following = set()
        for norm, collision in states:
            for add_norm, add_collision in options:
                new_norm = norm + add_norm
                if new_norm > target_norm:
                    continue
                new_collision = tuple(left + right for left, right
                                      in zip(collision, add_collision))
                if any(value > target for value, target
                       in zip(new_collision, target_collision)):
                    continue
                following.add((new_norm, new_collision))
        states = following
        peak = max(peak, len(states))
        if not states:
            break
    return (target_norm, target_collision) in states, peak, len(states)


def main() -> None:
    local_doc = json.loads(LOCAL.read_text(encoding="utf-8"))
    catalog_doc = json.loads(CATALOG.read_text(encoding="utf-8"))
    gram_doc = json.loads(GRAM.read_text(encoding="utf-8"))
    filter_doc = json.loads(FILTER_OUTPUT.read_text(encoding="utf-8"))
    remaining_doc = json.loads(REMAINING.read_text(encoding="utf-8"))

    assert filter_doc["status"] == "EXACT_SUPPORT_NORM_COLLISION_FILTER_COMPLETE"
    for path in (LOCAL, CATALOG, GRAM):
        assert filter_doc["inputs"][str(path)] == sha256(path)

    source_inventory = next(row for row in remaining_doc["source_rows"]
                            if row["source_row_index"] == 150)
    row = next(
        item for item in local_doc["support_rows"]
        if item["partition"] == source_inventory["partition"]
        and item["compression_orbit_index"]
            == source_inventory["compression_orbit_index"]
    )
    exceptional = tuple(tuple(item["support"])
                        for item in row["exceptional_supports"])
    expected_exceptional = (
        (0, 2), (0, 3), (0, 4), (0, 5),
        (1, 2), (1, 3), (1, 4), (1, 5),
    )
    assert exceptional == expected_exceptional
    assert [item["deficit"] for item in row["exceptional_supports"]] \
        == [2, 2, 1, 1, 2, 2, 1, 1]
    assert row["support_orbit_size"] == source_inventory["support_orbit_size"]
    assert len(row["representatives"]) == row["orbit_count"] == 5943
    assert len({record["mask_hex"] for record in row["representatives"]}) == 5943
    assert sum(record["orbit_size"] for record in row["representatives"]) \
        == row["raw_survivors"] == 2_244_608

    ordinary_supports = tuple(support_ for support_ in ALL_SUPPORTS
                              if support_ not in exceptional)
    assert len(ordinary_supports) == 13
    overlap_pairs = tuple(pair for pair in itertools.combinations(range(8), 2)
                          if not set(exceptional[pair[0]]).isdisjoint(
                              exceptional[pair[1]]))
    disjoint_pairs = tuple(pair for pair in itertools.combinations(range(8), 2)
                           if set(exceptional[pair[0]]).isdisjoint(
                               exceptional[pair[1]]))
    assert len(overlap_pairs) == 16 and len(disjoint_pairs) == 12

    vertices_plain = tuple(
        tuple(sorted((2 * first + first_bit, 2 * second + second_bit)))
        for first, second in exceptional
        for first_bit, second_bit in itertools.product((0, 1), repeat=2)
    )
    assert len(vertices_plain) == len(set(vertices_plain)) == 32
    fibre_of = {vertex: exceptional.index(support(vertex))
                for vertex in vertices_plain}
    # Store the fibre index with each vertex so inner loops need no lookup.
    vertices = tuple((vertex[0], vertex[1], fibre_of[vertex])
                     for vertex in vertices_plain)
    vertex_index = {vertex: index for index, vertex in enumerate(vertices_plain)}
    vertices_by_fibre = tuple(
        tuple(index for index, vertex in enumerate(vertices_plain)
              if fibre_of[vertex] == fibre)
        for fibre in range(8)
    )
    assert all(len(indices) == 4 for indices in vertices_by_fibre)

    catalog = [entry for entry in catalog_doc["macro_entries"]
               if entry["source_row_index"] == 150]
    assert len(catalog) == 21
    by_local_key = {}
    for entry in catalog:
        key = catalog_key(entry, overlap_pairs)
        assert key not in by_local_key
        by_local_key[key] = entry
    canonical_catalog = [entry for entry in catalog
                         if entry["signature_stabilizer_canonical"]]
    assert len(canonical_catalog) == 17
    assert sum(entry["signature_orbit_labelled_coverage"]
               for entry in canonical_catalog) == 2_244_608

    gram_rows = {
        (entry["state_orbit_number"],
         entry["signature_stabilizer_orbit_number"],
         entry["signature_stabilizer_canonical"]): entry
        for entry in gram_doc["rows"] if entry["source_row_index"] == 150
    }
    assert len(gram_rows) == 21

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
    assert vector_sum(vectors) == (0, 0, 0)
    for group in GROUPS:
        assert vector_sum(vectors[index] for index, fibre in enumerate(exceptional)
                          if group in fibre) == (0, 0, 0)

    # Check all 21 action copies, not merely the 17 canonical rows reached by
    # stored local representatives.
    matrices = {}
    canonical_matrices = {}
    gram_checks = 0
    for entry in catalog:
        gram_key = (
            entry["state_orbit_number"],
            entry["signature_stabilizer_orbit_number"],
            entry["signature_stabilizer_canonical"],
        )
        gram = gram_rows[gram_key]
        assert gram["unique"] and gram["passes_full_unique_gram_checks"]
        matrix = tuple(tuple(Fraction(value) for value in row_)
                       for row_ in gram["unique_H"])
        assert exact_psd(matrix) and gram["unique_H_psd"]
        matrices[tuple(tuple(value for value in row_) for row_ in matrix)] = matrix
        if entry["signature_stabilizer_canonical"]:
            canonical_matrices[
                tuple(tuple(value for value in row_) for row_ in matrix)
            ] = matrix
        deficits = tuple(int(item["deficit"])
                         for item in entry["exceptional_supports"])
        assert all(dot(vectors[index], matrix, vectors[index]) == 2 * deficits[index]
                   for index in range(8))
        overlap = {tuple(sorted((int(left), int(right)))): int(value)
                   for left, right, value in entry["overlap_block_totals"]}
        disjoint = {tuple(sorted((int(left), int(right)))): Fraction(value)
                    for left, right, value
                    in gram["disjoint_exceptional_block_totals"]}
        assert set(overlap) == set(overlap_pairs)
        assert set(disjoint) == set(disjoint_pairs)
        for pair, value in overlap.items():
            assert dot(vectors[pair[0]], matrix, vectors[pair[1]]) == -value
        for pair, value in disjoint.items():
            assert value.denominator == 1 and 0 <= value <= 16
            assert dot(vectors[pair[0]], matrix, vectors[pair[1]]) == 4 - value
        assert 4 * sum(dot(vector, matrix, vector) for vector in vectors) == 96
        assert all(Fraction(value) == 48
                   for value in gram["complete_compression_row_sums"])
        gram_checks += 1
    # One noncanonical action copy uses a sixth coordinate presentation; the
    # stored canonical local representatives encounter precisely five.
    assert len(matrices) == 6 and len(canonical_matrices) == 5 \
        and gram_checks == 21

    ordinary_patterns = {}
    ordinary_options = {}
    ordinary_matrix_order = tuple(canonical_matrices)
    ordinary_function_blocks = 0
    ordinary_degree_multisets_checked = 0
    for ordinary in ordinary_supports:
        patterns, disjoint, residual = ordinary_vertex_patterns(
            ordinary, exceptional, ordinary_supports
        )
        ordinary_patterns[ordinary] = (patterns, disjoint, residual)
        ordinary_function_blocks += len(disjoint)
        assert all(all(0 <= degree <= 4 for degree in pattern)
                   for pattern in patterns)
        for matrix_key, matrix in canonical_matrices.items():
            options, multiset_count = ordinary_fibre_options_ordered(
                patterns, disjoint, vectors, matrix
            )
            assert multiset_count >= len(options)
            ordinary_degree_multisets_checked += multiset_count
            ordinary_options[(ordinary, matrix_key)] = options
        reported = filter_doc["ordinary_support_data"][str(ordinary)]
        assert reported["vertex_patterns"] == len(patterns)
        assert reported["required_exceptional_group_counts"] == list(residual)
        independent_counts = sorted(
            len(ordinary_options[(ordinary, matrix_key)])
            for matrix_key in ordinary_matrix_order
        )
        assert sorted(reported["fibre_configurations_by_Gram_H"]) \
            == independent_counts
    assert ordinary_function_blocks == sum(
        1 for ordinary in ordinary_supports for target in exceptional
        if set(ordinary).isdisjoint(target)
    )

    survivor_by_mask = {row_[0]: row_ for row_ in filter_doc["survivors"]}
    assert len(survivor_by_mask) == len(filter_doc["survivors"]) == 5943
    reported_controls = {control["record_number"]: control
                         for control in filter_doc["controls"]}
    assert set(reported_controls) == set(range(25))

    per_macro = defaultdict(Counter)
    target_histogram = Counter()
    exceptional_cache = {}
    aggregate_cache = {}
    canonical_keys_seen = set()
    adjacency_keys = set()
    all_feasible = True
    pointwise_vertex_rows = 0
    full_compression_checks = 0

    for number, representative in enumerate(row["representatives"]):
        key = representative_key(representative["edges"], fibre_of, overlap_pairs)
        assert key in by_local_key
        entry = by_local_key[key]
        assert entry["signature_stabilizer_canonical"]
        canonical_keys_seen.add(key)
        assert representative["Q"] == entry["Q"]
        gram_key = (
            entry["state_orbit_number"],
            entry["signature_stabilizer_orbit_number"], True,
        )
        gram = gram_rows[gram_key]
        matrix = tuple(tuple(Fraction(value) for value in row_)
                       for row_ in gram["unique_H"])
        matrix_key = tuple(tuple(value for value in row_) for row_ in matrix)

        adjacency = [set() for _ in vertices]
        for raw_edge in representative["edges"]:
            left, right = edge_key(raw_edge)
            first, second = vertex_index[left], vertex_index[right]
            assert second not in adjacency[first]
            adjacency[first].add(second)
            adjacency[second].add(first)
        adjacency_key = tuple(tuple(sorted(row_)) for row_ in adjacency)
        adjacency_keys.add((matrix_key, adjacency_key))

        deficits = [int(item["deficit"]) for item in row["exceptional_supports"]]
        for fibre, indices in enumerate(vertices_by_fibre):
            internal_edges = sum(
                1 for left, right in itertools.combinations(indices, 2)
                if right in adjacency[left]
            )
            assert internal_edges == 4 - deficits[fibre]

        block_totals = {
            tuple(sorted((int(left), int(right)))): int(value)
            for left, right, value
            in representative["disjoint_Gram_profile"]["targets"]
        }
        assert set(block_totals) == set(disjoint_pairs)
        gram_totals = {
            tuple(sorted((int(left), int(right)))): int(Fraction(value))
            for left, right, value
            in gram["disjoint_exceptional_block_totals"]
        }
        assert block_totals == gram_totals

        exceptional_rows = []
        exceptional_details = []
        for source_fibre, indices in enumerate(vertices_by_fibre):
            cache_key = (
                matrix_key, source_fibre,
                tuple(tuple(sum(1 for other in adjacency[vertex]
                                if vertices[other][2] == target)
                            for target in range(8)) for vertex in indices),
                tuple(block_totals[tuple(sorted((source_fibre, target)))]
                      for target in range(8)
                      if set(exceptional[source_fibre]).isdisjoint(
                          exceptional[target])),
            )
            if cache_key not in exceptional_cache:
                exceptional_cache[cache_key] = exceptional_fibre_options_dp(
                    source_fibre, indices, adjacency, vertices, exceptional,
                    ordinary_supports, block_totals, vectors, matrix,
                )
            options, details = exceptional_cache[cache_key]
            assert options
            exceptional_rows.append(options)
            exceptional_details.append(details)
            pointwise_vertex_rows += 4

        # Independently form the full 8x8 exceptional compression matrix.
        known_totals = Counter()
        for raw_edge in representative["edges"]:
            left, right = edge_key(raw_edge)
            first, second = fibre_of[left], fibre_of[right]
            if first != second:
                known_totals[tuple(sorted((first, second)))] += 1
        compression = [[0] * 8 for _ in range(8)]
        for fibre, indices in enumerate(vertices_by_fibre):
            compression[fibre][fibre] = 2 * sum(
                1 for left, right in itertools.combinations(indices, 2)
                if right in adjacency[left]
            )
        for pair in overlap_pairs:
            compression[pair[0]][pair[1]] = compression[pair[1]][pair[0]] \
                = known_totals[pair]
        for pair in disjoint_pairs:
            compression[pair[0]][pair[1]] = compression[pair[1]][pair[0]] \
                = block_totals[pair]

        cBc = sum(Fraction(compression[left][right])
                  * dot(vectors[left], matrix, vectors[right])
                  for left in range(8) for right in range(8))
        edge_form = 2 * sum(
            dot(vectors[fibre_of[edge_key(edge)[0]]], matrix,
                vectors[fibre_of[edge_key(edge)[1]]])
            for edge in representative["edges"]
        ) + 2 * sum(
            block_totals[pair] * dot(vectors[pair[0]], matrix, vectors[pair[1]])
            for pair in disjoint_pairs
        )
        assert cBc == edge_form
        target_norm = Fraction(12 * 96) - cBc
        assert target_norm.denominator == 1 and target_norm >= 0
        target_norm = int(target_norm)
        full_compression_checks += 1

        target_collision = []
        for indices in vertices_by_fibre:
            total = 0
            for left, right in itertools.combinations(indices, 2):
                common_roots = len(set(vertices_plain[left]) & set(vertices_plain[right]))
                total += 2 - common_roots - int(right in adjacency[left])
            target_collision.append(total)
        target_collision = tuple(target_collision)

        option_rows = tuple(exceptional_rows) + tuple(
            ordinary_options[(ordinary, matrix_key)] for ordinary in ordinary_supports
        )
        aggregate_key = (option_rows, target_norm, target_collision)
        if aggregate_key not in aggregate_cache:
            aggregate_cache[aggregate_key] = aggregate_dp(
                option_rows, target_norm, target_collision
            )
        feasible, peak, final_states = aggregate_cache[aggregate_key]
        all_feasible &= feasible

        macro = (entry["state_orbit_number"],
                 entry["signature_stabilizer_orbit_number"])
        stats = per_macro[macro]
        stats["input_orbits"] += 1
        stats["input_mass"] += representative["orbit_size"]
        if feasible:
            stats["passing_orbits"] += 1
            stats["passing_mass"] += representative["orbit_size"]
        else:
            stats["rejected_orbits"] += 1
            stats["rejected_mass"] += representative["orbit_size"]
        target_histogram[(target_norm, target_collision)] += 1

        reported = survivor_by_mask.get(representative["mask_hex"])
        assert feasible and reported is not None, (
            number, representative["mask_hex"], feasible,
            reported is not None, [len(options) for options in option_rows],
            target_norm, target_collision,
        )
        assert reported == [
            representative["mask_hex"], representative["orbit_size"],
            representative["Q"], list(macro), target_norm,
            list(target_collision),
        ]

        if number in reported_controls:
            control = reported_controls[number]
            assert control["macro"] == list(macro)
            assert control["Gram_H"] == [[str(value) for value in matrix_row]
                                           for matrix_row in matrix]
            assert control["total_q_norm_target"] == target_norm
            assert control["collision_target"] == list(target_collision)
            assert control["exceptional_fibre_option_counts"] \
                == [len(options) for options in exceptional_rows]
            assert control["exceptional_fibre_details"] == exceptional_details
            assert control["feasible"] == feasible
            assert control["DP_peak_states"] == peak
            assert control["DP_final_states"] == final_states

    assert canonical_keys_seen == {catalog_key(entry, overlap_pairs)
                                   for entry in canonical_catalog}
    assert len(adjacency_keys) == 5943
    assert all_feasible and len(aggregate_cache) == 5
    assert pointwise_vertex_rows == 5943 * 8 * 4
    assert full_compression_checks == 5943

    expected_per_macro = {
        f"{key[0]}:{key[1]}": dict(sorted(stats.items()))
        for key, stats in sorted(per_macro.items())
    }
    assert expected_per_macro == filter_doc["per_macro"]
    expected_targets = {
        f"norm={norm};collision={','.join(map(str, collision))}": count
        for (norm, collision), count in sorted(target_histogram.items())
    }
    assert expected_targets == filter_doc["target_histogram"]

    summary = filter_doc["summary"]
    assert summary["input_local_orbits"] == summary["passing_local_orbits"] == 5943
    assert summary["input_labelled_mass"] == summary["passing_labelled_mass"] \
        == 2_244_608
    assert summary["rejected_local_orbits"] == 0
    assert summary["distinct_Gram_H"] == len(canonical_matrices) == 5
    assert summary["distinct_exceptional_degree_frontiers"] == 5943
    assert summary["distinct_norm_collision_targets"] == len(aggregate_cache) == 5

    result = {
        "status": "SOURCE150_NORM_COLLISION_AUDIT_PASS",
        "source_row_index": 150,
        "inputs": {str(path): sha256(path) for path in (
            LOCAL, CATALOG, GRAM, FILTER_SCRIPT, FILTER_OUTPUT, REMAINING
        )},
        "coverage": {
            "canonical_macro_orbits": len(canonical_catalog),
            "local_graph_orbits": 5943,
            "labelled_mass": 2_244_608,
            "all_local_masks_unique": True,
            "all_local_orbits_classified_to_exactly_one_canonical_macro": True,
            "per_macro_counts_and_mass_match": True,
        },
        "independent_recomputation": {
            "Gram_action_rows_checked": gram_checks,
            "distinct_exact_Gram_matrices_on_canonical_representatives": len(
                canonical_matrices
            ),
            "distinct_coordinate_presentations_across_all_action_rows": len(
                matrices
            ),
            "disjoint_exceptional_pairs_per_profile": len(disjoint_pairs),
            "ordinary_fibres": len(ordinary_supports),
            "ordinary_exceptional_function_blocks": ordinary_function_blocks,
            "ordinary_degree_multisets_checked_across_Gram_matrices": (
                ordinary_degree_multisets_checked
            ),
            "exceptional_pointwise_vertex_rows_checked": pointwise_vertex_rows,
            "full_exceptional_compressions_checked": full_compression_checks,
            "distinct_global_DP_instances": len(aggregate_cache),
            "all_DP_instances_feasible": all_feasible,
            "reported_controls_reproduced_exactly": len(reported_controls),
        },
        "formula_checks": {
            "kernel_vectors_sum_zero": True,
            "kernel_vectors_annihilate_all_seven_support_incidence_rows": True,
            "all_H_PSD_by_exact_principal_minors": True,
            "Gram_diagonals_equal_twice_internal_deficit": True,
            "overlap_Z_equals_negative_block_total": True,
            "all_twelve_disjoint_Z_equal_four_minus_block_total": True,
            "c0_norm_squared_is_96": True,
            "q_norm_target_is_12_times_96_minus_c0_B_c0": True,
            "same_fibre_collision_target_uses_B_squared_plus_B_identity": True,
        },
        "relaxation_direction": {
            "ordinary_to_exceptional": (
                "Every exceptional vertex has degree one into each disjoint "
                "ordinary C4. Hence the four ordinary-side row degrees are only "
                "required to lie in 0..4 and sum to four; no converse degree-one "
                "condition is imposed on an ordinary vertex."
            ),
            "exceptional_to_exceptional": (
                "Each source fibre obeys all four pointwise group equations and "
                "each Gram D block total. Source-side and target-side row vectors "
                "are combined independently without a common 4x4 simple matrix, "
                "which is a superset of realizable blocks."
            ),
            "collision": (
                "The six same-fibre pair equations are summed per source fibre; "
                "forgetting the six individual equalities enlarges feasibility."
            ),
        },
        "filter_result": {
            "passing_local_orbits": 5943,
            "passing_labelled_mass": 2_244_608,
            "rejected_local_orbits": 0,
            "rejected_labelled_mass": 0,
            "logical_status": "NO_EXCLUSION_SOURCE150_REMAINS_OPEN",
        },
        "claim_boundary": (
            "The independent replay validates the corrected necessary-condition "
            "filter and its coverage, but every input passes. It therefore proves "
            "no source150 branch UNSAT and constructs no graph. The calculation "
            "is an exact executable audit, not a proof-assistant certificate."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    REPORT.write_text("\n".join([
        "# E72 source150 norm/collision independent audit",
        "",
        "Status: **SOURCE150_NORM_COLLISION_AUDIT_PASS**.",
        "",
        "The corrected filter's complete input is independently recovered: "
        "5,943 local-graph orbits, labelled mass 2,244,608, partitioned among "
        "17 canonical macro orbits. All 21 action copies of the five exact Gram "
        "matrices satisfy the diagonal, overlap, twelve disjoint-block, PSD, and "
        "compression-row checks.",
        "",
        "The replay uses ordered ordinary-fibre products and a staged "
        "exceptional-row DP, rather than importing the filter. It reproduces all "
        "25 controls and all five global norm/collision DP instances exactly.",
        "",
        "The ordinary--exceptional rule is one-sided: each exceptional vertex "
        "chooses one neighbour in a disjoint ordinary C4, while an ordinary "
        "vertex may receive 0 through 4 such neighbours. The twelve disjoint "
        "exceptional blocks retain their exact Gram totals but deliberately drop "
        "common 4x4-matrix compatibility. Both omissions enlarge the feasible "
        "set, so a rejection would be safe.",
        "",
        "Result: all 5,943 orbits pass. Thus this corrected artifact makes no "
        "source150 exclusion; the full 2,244,608 mass remains open. This is an "
        "exact executable audit, not a proof-assistant certificate.",
        "",
    ]), encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "local_orbits": 5943,
        "labelled_mass": 2_244_608,
        "global_DP_instances": len(aggregate_cache),
        "rejected": 0,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
