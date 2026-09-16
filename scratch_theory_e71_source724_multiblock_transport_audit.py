"""Producer-independent exact audit of the source-724 transport exclusion.

The 128 overlap products are treated as a frozen, previously audited input.
This script does not import the discovery producer.  It independently
reconstructs every Gram-compatible fibre-degree multiset over those products,
replays the exceptional-vertex transport relaxation, and then replays the
diagonal idempotence equation of the residual -4 projector.
"""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
from functools import lru_cache
import hashlib
import itertools
import json
import os
from pathlib import Path

import scratch_general_e72_q3_fast_expansion as fast
import scratch_theory_e71_defect_rank_probe as defect


CATALOG = defect.CATALOG
MINING = defect.MINING
DEFECT = defect.OUTPUT
LEVERAGE = Path("scratch_theory_e71_projector_leverage_probe.json")
DEGREE_WITNESS = Path("scratch_theory_e71_source724_degree_witness.json")
DISCOVERY = Path("scratch_theory_e71_source724_multiblock_transport.json")
OUTPUT = Path("scratch_theory_e71_source724_multiblock_transport_audit.json")
SUPPORTS = tuple(itertools.combinations(range(7), 2))
UPPER6 = ((0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2))


def atomic_json(path, value):
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def add(left, right):
    return tuple(a + b for a, b in zip(left, right))


def gram6(rows):
    return tuple(sum(row[i] * row[j] for row in rows) for i, j in UPPER6)


@lru_cache(maxsize=None)
def bipartite_masks(left, right):
    left, right = tuple(left), tuple(right)
    answer = []

    def visit(row, remaining, mask):
        if row == 4:
            if not any(remaining):
                answer.append(mask)
            return
        for columns in itertools.combinations(range(4), left[row]):
            after = list(remaining)
            if any(after[column] == 0 for column in columns):
                continue
            for column in columns:
                after[column] -= 1
            if any(value > 3 - row for value in after):
                continue
            visit(row + 1, tuple(after),
                  mask | sum(1 << (4 * row + column) for column in columns))

    visit(0, right, 0)
    return tuple(answer)


def fixed_degree_key(geometry, internal, choices, exceptional):
    mask = internal
    for choice in choices:
        mask |= choice.mask
    adjacency = defect.mask_adjacency(
        len(geometry.vertices), geometry.pair_positions, mask
    )
    fixed = defect.fixed_exceptional_degrees(geometry, adjacency, exceptional)
    key = tuple(tuple(tuple(sorted(row.items())) for row in fibre_rows)
                for fibre_rows in fixed)
    return key, fixed


def ordered_configurations(pattern_row, fixed):
    patterns = pattern_row["patterns"]
    candidates = []
    for local in range(4):
        candidates.append(tuple(
            index for index, pattern in enumerate(patterns)
            if all(int(pattern["exceptional_degrees"][target]) == value
                   for target, value in fixed[local].items())
        ))
    configurations = {}
    for selected in itertools.product(*candidates):
        full = tuple(tuple(patterns[index]["scaled_W_row_on_exceptional"])
                     for index in selected)
        if any(sum(row[column] for row in full) for column in range(len(full[0]))):
            continue
        pivots = tuple(tuple(patterns[index]["pivot_scaled_W_coordinates"])
                       for index in selected)
        degrees = tuple(
            tuple(int(patterns[index]["exceptional_degrees"][target])
                  for index in selected)
            for target in range(len(full[0]))
        )
        value = gram6(pivots)
        configurations.setdefault((value, degrees), {
            "selected": tuple(selected), "gram": value, "degrees": degrees,
        })
    return tuple(configurations.values())


def unordered_configurations(pattern_row):
    patterns = pattern_row["patterns"]
    configurations = {}
    for selected in itertools.combinations_with_replacement(range(len(patterns)), 4):
        full = tuple(tuple(patterns[index]["scaled_W_row_on_exceptional"])
                     for index in selected)
        if any(sum(row[column] for row in full) for column in range(len(full[0]))):
            continue
        pivots = tuple(tuple(patterns[index]["pivot_scaled_W_coordinates"])
                       for index in selected)
        degrees = tuple(
            tuple(int(patterns[index]["exceptional_degrees"][target])
                  for index in selected)
            for target in range(len(full[0]))
        )
        configurations.setdefault((pivots, degrees), {
            "selected": tuple(selected), "gram": gram6(pivots),
        })
    return tuple(configurations.values())


def exceptional_compatible(configurations, exceptional):
    for left, right in itertools.combinations(range(len(exceptional)), 2):
        if set(exceptional[left]) & set(exceptional[right]):
            continue
        if not bipartite_masks(
            configurations[left]["degrees"][right],
            configurations[right]["degrees"][left],
        ):
            return False
    return True


def fixed_edges(entry, geometry, choices, exceptional):
    label_to_vertex = {
        tuple(label): 4 * source + local
        for source, support in enumerate(SUPPORTS)
        for local, label in enumerate(
            (2 * support[0] + a, 2 * support[1] + b)
            for a, b in itertools.product((0, 1), repeat=2)
        )
    }
    edges = set()
    for left, right in entry["internal_edges"]:
        edges.add(tuple(sorted((label_to_vertex[tuple(left)],
                                label_to_vertex[tuple(right)]))))
    for choice in choices:
        for left, right in choice.edges:
            edges.add(tuple(sorted((label_to_vertex[geometry.vertices[left]],
                                    label_to_vertex[geometry.vertices[right]]))))
    return edges


def selected_rows(patterns, exceptional, compression, exceptional_selected,
                  ordinary_selected):
    selected = {}
    for support, indices in zip(exceptional, exceptional_selected):
        selected[support] = tuple(indices)
    ordinary = [support for support in SUPPORTS if support not in set(exceptional)]
    for support, indices in zip(ordinary, ordinary_selected):
        selected[support] = tuple(indices)
    exceptional_index = {support: index for index, support in enumerate(exceptional)}
    degrees, residual = [], []
    for source, support in enumerate(SUPPORTS):
        source_degrees, source_residual = [], []
        for pattern_index in selected[support]:
            pattern = patterns[support]["patterns"][pattern_index]
            row = []
            for target, target_support in enumerate(SUPPORTS):
                if target_support in exceptional_index:
                    row.append(int(pattern["exceptional_degrees"][
                        exceptional_index[target_support]
                    ]))
                else:
                    assert compression[source][target] % 4 == 0
                    row.append(compression[source][target] // 4)
            assert sum(row) == 12
            source_degrees.append(tuple(row))
            source_residual.append(tuple(
                4 * row[target] - compression[source][target]
                for target in range(21)
            ))
        assert len(source_degrees) == 4
        assert all(sum(source_degrees[local][target] for local in range(4))
                   == compression[source][target] for target in range(21))
        degrees.append(tuple(source_degrees))
        residual.append(tuple(source_residual))
    return tuple(degrees), tuple(residual)


def fixed_adjacencies(edge_sets):
    answer = []
    for edges in edge_sets:
        adjacency = [set() for _ in range(84)]
        for left, right in edges:
            adjacency[left].add(right)
            adjacency[right].add(left)
        answer.append(adjacency)
    return tuple(answer)


def exceptional_transport_survivors(degrees, residual, fixed_sets, compression,
                                    K4, pivot_global, exceptional):
    pivot_rows = tuple(tuple(tuple(row[column] for column in pivot_global)
                             for row in fibre) for fibre in residual)
    fixed_adjacency = fixed_adjacencies(fixed_sets)
    passing = set(range(len(fixed_sets)))
    exceptional_global = tuple(SUPPORTS.index(support) for support in exceptional)
    for source in exceptional_global:
        for local in range(4):
            options_by_block = []
            for target in range(21):
                if target == source or set(SUPPORTS[source]) & set(SUPPORTS[target]):
                    continue
                left_margin = tuple(degrees[source][row][target] for row in range(4))
                right_margin = tuple(degrees[target][column][source] for column in range(4))
                values = set()
                for mask in bipartite_masks(left_margin, right_margin):
                    values.add(tuple(
                        sum(pivot_rows[target][column][coordinate]
                            for column in range(4)
                            if (mask >> (4 * local + column)) & 1)
                        for coordinate in range(3)
                    ))
                options_by_block.append(values)
            assert len(options_by_block) == 10
            reachable = {(0, 0, 0)}
            for options in options_by_block:
                reachable = {add(left, right) for left in reachable for right in options}
            rhs = []
            for pivot in pivot_global:
                value = K4[source][pivot]
                value -= sum(
                    residual[source][local][target]
                    * (compression[target][pivot] + 4 * int(target == pivot))
                    for target in range(21)
                )
                rhs.append(value)
            for choice_index in tuple(passing):
                fixed_sum = [0, 0, 0]
                vertex = 4 * source + local
                for neighbor in fixed_adjacency[choice_index][vertex]:
                    for coordinate in range(3):
                        fixed_sum[coordinate] += pivot_rows[neighbor // 4][neighbor % 4][coordinate]
                numerator = tuple(rhs[i] - 4 * fixed_sum[i] for i in range(3))
                required = None
                if all(value % 4 == 0 for value in numerator):
                    required = tuple(value // 4 for value in numerator)
                if required not in reachable:
                    passing.remove(choice_index)
            if not passing:
                return []
    return sorted(passing)


def determinant(matrix):
    matrix = [[Fraction(value) for value in row] for row in matrix]
    answer = Fraction(1)
    for column in range(len(matrix)):
        pivot = next((row for row in range(column, len(matrix))
                      if matrix[row][column]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            matrix[column], matrix[pivot] = matrix[pivot], matrix[column]
            answer = -answer
        scale = matrix[column][column]
        answer *= scale
        matrix[column] = [value / scale for value in matrix[column]]
        for row in range(column + 1, len(matrix)):
            factor = matrix[row][column]
            if factor:
                matrix[row] = [a - factor * b
                               for a, b in zip(matrix[row], matrix[column])]
    return answer


def solve(matrix, target):
    size = len(matrix)
    a = [[Fraction(value) for value in matrix[row]] + [Fraction(target[row])]
         for row in range(size)]
    for column in range(size):
        pivot = next(row for row in range(column, size) if a[row][column])
        a[column], a[pivot] = a[pivot], a[column]
        scale = a[column][column]
        a[column] = [value / scale for value in a[column]]
        for row in range(size):
            if row != column and a[row][column]:
                factor = a[row][column]
                a[row] = [x - factor * y for x, y in zip(a[row], a[column])]
    return tuple(row[-1] for row in a)


def projector_edge_equations(residual, Z):
    rank = defect.rank(Z)
    pivot = next(indices for indices in itertools.combinations(range(21), rank)
                 if determinant([[Z[i][j] for j in indices] for i in indices]))
    minor = [[Z[i][j] for j in pivot] for i in pivot]
    s = [tuple(Z[source][target] - residual[source][local][target]
               for target in range(21))
         for source in range(21) for local in range(4)]
    solutions = [solve(minor, [row[i] for i in pivot]) for row in s]

    def bilinear(left, right):
        return sum(Fraction(s[left][i]) * solutions[right][position]
                   for position, i in enumerate(pivot))

    labels = tuple(
        (2 * support[0] + local // 2, 2 * support[1] + local % 2)
        for support in SUPPORTS for local in range(4)
    )
    diagonal = [40 - bilinear(vertex, vertex) for vertex in range(84)]
    weights = [[Fraction(0) for _ in range(84)] for _ in range(84)]
    targets = []
    for left in range(84):
        sum_squares = Fraction(0)
        for right in range(84):
            if left == right:
                continue
            q = len(set(labels[left]) & set(labels[right]))
            d = sum((value ^ 1) in labels[right] for value in labels[left])
            base = Fraction(4 - 6 * q - 2 * d) - bilinear(left, right)
            weights[left][right] = 8 - base
            sum_squares += base * base
        targets.append((112 * diagonal[left] - diagonal[left] ** 2 - sum_squares) / 32)
    return weights, targets, diagonal, pivot


def projector_norm_survivors(degrees, residual, fixed_sets, candidates,
                             compression, K4, pivot_global, exceptional,
                             weights, targets):
    pivot_rows = tuple(tuple(tuple(row[column] for column in pivot_global)
                             for row in fibre) for fibre in residual)
    fixed_adjacency = fixed_adjacencies(fixed_sets)
    passing = set(candidates)
    exceptional_global = tuple(SUPPORTS.index(support) for support in exceptional)
    for source in exceptional_global:
        for local in range(4):
            vertex = 4 * source + local
            options_by_block = []
            for target in range(21):
                if target == source or set(SUPPORTS[source]) & set(SUPPORTS[target]):
                    continue
                left_margin = tuple(degrees[source][row][target] for row in range(4))
                right_margin = tuple(degrees[target][column][source] for column in range(4))
                values = set()
                for mask in bipartite_masks(left_margin, right_margin):
                    chosen = [column for column in range(4)
                              if (mask >> (4 * local + column)) & 1]
                    values.add(tuple(
                        sum(pivot_rows[target][column][coordinate] for column in chosen)
                        for coordinate in range(3)
                    ) + (sum(weights[vertex][4 * target + column]
                             for column in chosen),))
                options_by_block.append(values)
            reachable = {(Fraction(0),) * 4}
            for options in options_by_block:
                reachable = {add(left, right) for left in reachable for right in options}
            rhs = []
            for pivot_column in pivot_global:
                value = K4[source][pivot_column] - sum(
                    residual[source][local][target]
                    * (compression[target][pivot_column]
                       + 4 * int(target == pivot_column))
                    for target in range(21)
                )
                rhs.append(value)
            for choice_index in tuple(passing):
                fixed_sum = [0, 0, 0]
                fixed_weight = Fraction(0)
                for neighbor in fixed_adjacency[choice_index][vertex]:
                    for coordinate in range(3):
                        fixed_sum[coordinate] += pivot_rows[neighbor // 4][neighbor % 4][coordinate]
                    fixed_weight += weights[vertex][neighbor]
                numerator = tuple(rhs[i] - 4 * fixed_sum[i] for i in range(3))
                required = None
                if all(value % 4 == 0 for value in numerator):
                    required = tuple(Fraction(value // 4) for value in numerator) + (
                        targets[vertex] - fixed_weight,
                    )
                if required not in reachable:
                    passing.remove(choice_index)
            if not passing:
                return []
    return sorted(passing)


def record_key(record):
    return (
        int(record["signature_index"]),
        tuple(tuple(row) for row in record["exceptional_selected_pattern_indices"]),
        tuple(tuple(row) for row in record["ordinary_selected_pattern_indices"]),
    )


def projector_constant_control(witness, compression, Z):
    """Check every scale/sign in the E_-4 formulas on the frozen B control."""
    labels = tuple(
        (2 * support[0] + local // 2, 2 * support[1] + local % 2)
        for support in SUPPORTS for local in range(4)
    )
    L = [[int(label in labels[vertex]) for label in range(14)]
         for vertex in range(84)]
    inverse = [[
        Fraction(11 * int(i == j), 120) - Fraction(1, 240)
        + Fraction(int(i == (j ^ 1)), 120)
        for j in range(14)
    ] for i in range(14)]
    gram = [[sum(L[x][i] * L[x][j] for x in range(84))
             for j in range(14)] for i in range(14)]
    assert [[sum(Fraction(gram[i][k]) * inverse[k][j] for k in range(14))
             for j in range(14)] for i in range(14)] == [
        [Fraction(int(i == j)) for j in range(14)] for i in range(14)
    ]
    H = [[
        Fraction(int(x == y)) - sum(
            Fraction(L[x][i]) * inverse[i][j] * Fraction(L[y][j])
            for i in range(14) for j in range(14)
        )
        for y in range(84)
    ] for x in range(84)]
    assert {H[x][x] for x in range(84)} == {Fraction(5, 6)}
    adjacency = [set() for _ in range(84)]
    for left, right in witness["edge_list_zero_based"]:
        adjacency[left].add(right)
        adjacency[right].add(left)
    assert {len(row) for row in adjacency} == {12}
    # Substitute the *hypothetical SRG* identity BL=2J-L(I+R0)
    # algebraically.  The frozen degree witness need not realize its 14 exact
    # label columns; it is used below only for B_xy and fibre degrees.
    label_rhs = [[2 - L[y][label] - L[y][label ^ 1]
                  for y in range(84)] for label in range(14)]
    correction = [[sum(
        Fraction(L[x][i]) * inverse[i][j] * Fraction(label_rhs[j][y])
        for i in range(14) for j in range(14)
    ) for y in range(84)] for x in range(84)]
    E4 = [[
        (3 * H[x][y] + correction[x][y]
         - int(y in adjacency[x])) / 7
        for y in range(84)
    ] for x in range(84)]
    assert E4 == [list(row) for row in zip(*E4)]
    assert {E4[x][x] for x in range(84)} == {Fraction(5, 14)}
    for x, y in itertools.combinations(range(84), 2):
        q = len(set(labels[x]) & set(labels[y]))
        d = sum((value ^ 1) in labels[y] for value in labels[x])
        edge = int(y in adjacency[x])
        assert 112 * E4[x][y] == 4 - 6 * q - 2 * d - 16 * edge
    compressed = [[sum(E4[x][y] for x in range(4 * G, 4 * G + 4)
                              for y in range(4 * F, 4 * F + 4)) / 4
                   for F in range(21)] for G in range(21)]
    assert compressed == [[Fraction(value, 28) for value in row] for row in Z]
    R = [[0] * 21 for _ in range(84)]
    for x in range(84):
        G = x // 4
        for F in range(21):
            degree = sum(y in adjacency[x] for y in range(4 * F, 4 * F + 4))
            R[x][F] = 4 * degree - compression[G][F]
            e4u = sum(E4[x][y] for y in range(4 * F, 4 * F + 4)) / 2
            assert e4u == Fraction(Z[G][F] - R[x][F], 56)
    return {
        "root_label_Gram_inverse_verified": True,
        "BL_action_symbolically_substituted_entries": 84 * 14,
        "E4_off_diagonal_entries_verified": 84 * 83 // 2,
        "diag_E4": "5/14",
        "U_transpose_E4_U_equals_Z_over_28": True,
        "E4_U_coordinate_formula_verified": 84 * 21,
    }


def main():
    discovery_raw = DISCOVERY.read_bytes()
    discovery = json.loads(discovery_raw)
    for path, expected in discovery["inputs_sha256"].items():
        assert sha256(Path(path)) == expected
    assert discovery["macro_key"] == [724, 1, 0]
    assert discovery["overlap_census"] == {"empty": 512, "gram_unsat": 384, "feasible": 128}

    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    mining = json.loads(MINING.read_text(encoding="utf-8"))
    prior = json.loads(DEFECT.read_text(encoding="utf-8"))
    degree_witness = json.loads(DEGREE_WITNESS.read_text(encoding="utf-8"))
    entry = next(row for row in catalog["macro_entries"]
                 if row["signature_stabilizer_canonical"]
                 and int(row["source_row_index"]) == 724 and int(row["Q"]) == 2)
    key = defect.macro_key(entry)
    profile = next(row for row in mining["profile_rows"]["71"]
                   if defect.macro_key(row) == key)
    structural = next(row for row in prior["rows"] if tuple(row["key"]) == key)
    source = defect.source_row_map(fast)[724]
    geometry = fast.RowGeometry(source)
    oriented = fast.oriented_assignment(geometry, entry["state_indices"])
    internal = fast.internal_mask(geometry, oriented)
    domains = defect.exact_signature_domains(fast, geometry, oriented, entry)
    exceptional = tuple(tuple(row["support"]) for row in entry["exceptional_supports"])
    _a, _b, compression, _c, Z = defect.build_compression(entry, profile)
    patterns = {tuple(row["source_support"]): row
                for row in structural["rank_three_integer_row_patterns"]["by_source_fibre"]}
    pivot_local = structural["rank_three_integer_row_patterns"]["pivot_exceptional_indices"]
    pivot_global = tuple(SUPPORTS.index(exceptional[index]) for index in pivot_local)
    K4 = structural["K4"]
    target_gram = tuple(4 * K4[pivot_global[i]][pivot_global[j]] for i, j in UPPER6)
    projector_constants = projector_constant_control(degree_witness, compression, Z)

    # Decode the frozen 128 feasible products without calling the producer.
    groups = {}
    seen_choices = set()
    for branch in discovery["branch_records"]:
        indices = tuple(branch["choice_indices"])
        assert indices not in seen_choices
        seen_choices.add(indices)
        choices = tuple(domains[group][index] for group, index in enumerate(indices))
        fixed_key, _fixed = fixed_degree_key(geometry, internal, choices, exceptional)
        groups.setdefault(fixed_key, []).append(choices)
    assert len(seen_choices) == 128
    ordered_groups = sorted(groups.items())
    assert [len(choices) for _key, choices in ordered_groups] == [64, 64]

    # Independently reconstruct every one of the 408 complete degree multisets.
    ordinary_supports = tuple(support for support in SUPPORTS
                              if support not in set(exceptional))
    ordinary_domains = {support: unordered_configurations(patterns[support])
                        for support in ordinary_supports}
    assert [len(ordinary_domains[support]) for support in ordinary_supports] == [
        1, 1, 3, 1, 3, 3, 12, 1, 1, 3, 1, 3, 12,
    ]
    ordinary_by_gram = {}
    ordinary_products = 0
    for values in itertools.product(*(ordinary_domains[support]
                                      for support in ordinary_supports)):
        ordinary_products += 1
        total = (0,) * 6
        for config in values:
            total = add(total, config["gram"])
        ordinary_by_gram.setdefault(total, []).append(values)
    assert ordinary_products == 34992

    expected_keys = set()
    for signature_index, (_fixed_key, choices_group) in enumerate(ordered_groups):
        _key2, fixed = fixed_degree_key(
            geometry, internal, choices_group[0], exceptional
        )
        config_domains = tuple(ordered_configurations(patterns[support], fixed[local])
                               for local, support in enumerate(exceptional))
        assert len(list(itertools.product(*config_domains))) == 960
        for exceptional_values in itertools.product(*config_domains):
            if not exceptional_compatible(exceptional_values, exceptional):
                continue
            partial = (0,) * 6
            for config in exceptional_values:
                partial = add(partial, config["gram"])
            needed = tuple(target_gram[i] - partial[i] for i in range(6))
            for ordinary_values in ordinary_by_gram.get(needed, ()):
                expected_keys.add((
                    signature_index,
                    tuple(config["selected"] for config in exceptional_values),
                    tuple(config["selected"] for config in ordinary_values),
                ))
    records = discovery["complete_primary_direction_degree_census"][
        "complete_configuration_records"
    ]
    stored_keys = {record_key(record) for record in records}
    assert len(records) == len(stored_keys) == len(expected_keys) == 408
    assert stored_keys == expected_keys
    assert all(not record["projector_leverage_violations"] for record in records)
    stored_digest = hashlib.sha256(json.dumps(records, sort_keys=True).encode()).hexdigest().upper()
    assert stored_digest == discovery["complete_primary_direction_degree_census"][
        "complete_configuration_records_sha256"
    ]

    # Recompute all 26,112 pointwise decisions and all final projector decisions.
    transport_counts = Counter()
    projector_counts = Counter()
    gram_checks = 0
    first_final_reject = None
    for record in records:
        signature = int(record["signature_index"])
        choices_group = ordered_groups[signature][1]
        fixed_sets = tuple(fixed_edges(entry, geometry, choices, exceptional)
                           for choices in choices_group)
        degrees, residual = selected_rows(
            patterns, exceptional, compression,
            record["exceptional_selected_pattern_indices"],
            record["ordinary_selected_pattern_indices"],
        )
        # Full, not merely pivot, aggregate Gram check.
        actual_gram = [[sum(residual[source][local][i] * residual[source][local][j]
                            for source in range(21) for local in range(4))
                        for j in range(21)] for i in range(21)]
        assert actual_gram == [[4 * value for value in row] for row in K4]
        gram_checks += 1
        transport = exceptional_transport_survivors(
            degrees, residual, fixed_sets, compression, K4, pivot_global, exceptional
        )
        assert transport == record["transport_passing_choice_indices"]
        transport_counts["tested"] += 64
        transport_counts["passed"] += len(transport)
        transport_counts["rejected"] += 64 - len(transport)
        if transport:
            weights, targets, diagonal, projector_pivot = projector_edge_equations(residual, Z)
            assert min(diagonal) >= 0
            final = projector_norm_survivors(
                degrees, residual, fixed_sets, transport, compression, K4,
                pivot_global, exceptional, weights, targets,
            )
            assert final == record["projector_norm_unfiltered_passing_choice_indices"]
            projector_counts["entered"] += len(transport)
            projector_counts["passed"] += len(final)
            projector_counts["rejected"] += len(transport) - len(final)
            if not final and first_final_reject is None:
                first_final_reject = {
                    "signature_index": signature,
                    "transport_candidates": transport,
                    "Z_principal_indices": list(projector_pivot),
                    "minimum_scaled_projector_diagonal": str(min(diagonal)),
                }

    assert transport_counts == Counter(tested=26112, rejected=26096, passed=16)
    assert projector_counts == Counter(entered=16, rejected=16, passed=0)
    producer_counts = discovery["complete_primary_direction_degree_census"]["counts"]
    assert producer_counts["exceptional_transport_overlap_choices_tested"] == 26112
    assert producer_counts["exceptional_transport_overlap_choices_rejected"] == 26096
    assert producer_counts["exceptional_transport_overlap_choices_passed"] == 16
    assert producer_counts["projector_norm_unfiltered_candidate_overlap_choices"] == 16
    assert producer_counts["projector_norm_unfiltered_rejected"] == 16
    assert producer_counts["projector_norm_unfiltered_passed"] == 0

    result = {
        "status": "INDEPENDENT_SOURCE724_MULTIBLOCK_TRANSPORT_AUDIT_PASS",
        "inputs_sha256": {
            str(path): sha256(path) for path in
            (CATALOG, MINING, DEFECT, LEVERAGE, DEGREE_WITNESS, DISCOVERY)
        },
        "producer_imported": False,
        "frozen_overlap_products": 128,
        "fixed_overlap_signatures": 2,
        "overlap_products_per_signature": [64, 64],
        "ordinary_unordered_products_reconstructed": ordinary_products,
        "complete_degree_multisets_reconstructed": len(expected_keys),
        "full_RtR_equals_4K4_checks": gram_checks,
        "projector_constant_control": projector_constants,
        "corrected_projector_leverage_rejections_inside_complete_frontier": 0,
        "overlap_degree_instances": 26112,
        "pointwise_transport": dict(transport_counts),
        "residual_minus4_projector_row_norm": dict(projector_counts),
        "first_final_reject_control": first_final_reject,
        "ordinary_row_permutation_quotient": (
            "For an exceptional source vertex and an ordinary target fibre, a row "
            "permutation simultaneously permutes the target residual vectors and the "
            "four column margins.  Relabelling columns is a bijection of the enumerated "
            "4x4 matrices, so both the 3-vector transport set and the added projector "
            "weight coordinate are invariant."
        ),
        "coverage_conclusion": (
            "Every Gram-compatible degree multiset over every frozen feasible source-724 "
            "overlap product fails a necessary pointwise equation.  Thus macro key "
            "(724,1,0), labelled coverage 32768, is excluded.  This is not an E71-wide "
            "enumeration and makes no claim about the remaining E71 macros."
        ),
        "submission_txt_written": False,
    }
    atomic_json(OUTPUT, result)
    print(json.dumps({"path": str(OUTPUT), **result}, sort_keys=True))


if __name__ == "__main__":
    main()
