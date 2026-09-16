"""Discover exact multi-block transport cuts for source 724 only.

This deliberately reuses the frozen source-724 macro and its 128 feasible
overlap products.  It does not enumerate E0=71 macros or order-eight classes.
"""

from __future__ import annotations

from collections import Counter
from functools import lru_cache
from fractions import Fraction
import hashlib
import itertools
import json
import math
import os
from pathlib import Path

import scratch_general_e72_q3_fast_expansion as fast
import scratch_theory_e71_defect_rank_probe as defect


CATALOG = defect.CATALOG
MINING = defect.MINING
DEFECT = defect.OUTPUT
DEGREE_WITNESS = Path("scratch_theory_e71_source724_degree_witness.json")
LEVERAGE = Path("scratch_theory_e71_projector_leverage_probe.json")
OUTPUT = Path("scratch_theory_e71_source724_multiblock_transport.json")
SUPPORTS = defect.SUPPORTS
UPPER6 = ((0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2))


def atomic_json(path: Path, value) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def transpose(matrix):
    return [list(column) for column in zip(*matrix)]


def matmul(left, right):
    right_t = transpose(right)
    return [[sum(a * b for a, b in zip(row, column)) for column in right_t]
            for row in left]


def add(*matrices):
    return [[sum(matrix[i][j] for matrix in matrices)
             for j in range(len(matrices[0][0]))]
            for i in range(len(matrices[0]))]


def scale(value, matrix):
    return [[value * entry for entry in row] for row in matrix]


def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]


def upper6(matrix):
    return tuple(matrix[i][j] for i, j in UPPER6)


def edge_contribution(left, right):
    return tuple(
        left[i] * right[j] + (left[j] * right[i] if i != j else left[i] * right[j])
        for i, j in UPPER6
    )


def sum6(values):
    result = [0] * 6
    for value in values:
        for i, entry in enumerate(value):
            result[i] += entry
    return tuple(result)


def dot6(left, right):
    return sum(a * b for a, b in zip(left, right))


def primitive(values):
    divisor = 0
    for value in values:
        divisor = math.gcd(divisor, abs(value))
    values = tuple(value // max(1, divisor) for value in values)
    first = next((value for value in values if value), 0)
    return tuple(-value for value in values) if first < 0 else values


@lru_cache(maxsize=None)
def bipartite_masks(left, right):
    """All 4x4 Boolean matrices with the two ordered margins."""
    left = tuple(map(int, left))
    right = tuple(map(int, right))
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
            rows_left = 3 - row
            if any(value > rows_left for value in after):
                continue
            visit(row + 1, tuple(after), mask | sum(1 << (4 * row + c) for c in columns))

    visit(0, right, 0)
    return tuple(answer)


def option_contribution(mask, left_rows, right_rows):
    return sum6(
        edge_contribution(left_rows[row], right_rows[column])
        for row in range(4) for column in range(4)
        if (mask >> (4 * row + column)) & 1
    )


def internal_c4_options(rows):
    # Every labelled 2-regular simple graph on four vertices is K4 minus a
    # perfect matching; there are exactly three.
    all_edges = set(itertools.combinations(range(4), 2))
    matchings = (
        {(0, 1), (2, 3)},
        {(0, 2), (1, 3)},
        {(0, 3), (1, 2)},
    )
    return tuple(sum6(edge_contribution(rows[i], rows[j])
                      for i, j in sorted(all_edges - matching))
                 for matching in matchings)


def fixed_relation_matrices():
    labels = tuple(
        (2 * support[0] + local // 2, 2 * support[1] + local % 2)
        for support in SUPPORTS for local in range(4)
    )
    q = [[len(set(labels[i]) & set(labels[j])) for j in range(84)] for i in range(84)]
    d = [[sum((value ^ 1) in labels[j] for value in labels[i])
          for j in range(84)] for i in range(84)]
    return labels, q, d


def aggregate_by_fibres(matrix):
    return [[sum(matrix[4 * source + i][4 * target + j]
                 for i in range(4) for j in range(4))
             for target in range(21)] for source in range(21)]


def transport_target(compression):
    """Return pivot-free full target R^T B R forced by the rooted SRG."""
    _labels, q, d = fixed_relation_matrices()
    qbar = aggregate_by_fibres(q)
    dbar = aggregate_by_fibres(d)
    i21 = identity(21)
    j21 = [[1] * 21 for _ in range(21)]
    # P^T B^2 P and P^T B^3 P from
    # B^2+B=12I+2J-Q and
    # B^3=13B-12I+18J+2Q+D.
    gram2 = add(scale(48, i21), scale(32, j21), scale(-1, qbar), scale(-1, compression))
    moment3 = add(
        scale(13, compression), scale(-48, i21), scale(288, j21),
        scale(2, qbar), dbar,
    )
    c2 = matmul(compression, compression)
    c3 = matmul(c2, compression)
    target = add(
        scale(16, moment3),
        scale(-4, matmul(gram2, compression)),
        scale(-4, matmul(compression, gram2)),
        c3,
    )
    assert target == transpose(target)
    return target, qbar, dbar, gram2, moment3


def selected_rows(structural, exceptional, compression, witness):
    patterns = {
        tuple(row["source_support"]): row["patterns"]
        for row in structural["rank_three_integer_row_patterns"]["by_source_fibre"]
    }
    selected = {
        tuple(row["support"]): tuple(row["selected_pattern_indices"])
        for row in witness["exceptional_fibres"] + witness["ordinary_fibres"]
    }
    exceptional_index = {support: i for i, support in enumerate(exceptional)}
    degrees = []
    residual = []
    for source, support in enumerate(SUPPORTS):
        source_degrees = []
        source_residual = []
        for pattern_index in selected[support]:
            pattern = patterns[support][pattern_index]
            row = []
            for target, target_support in enumerate(SUPPORTS):
                if target_support in exceptional_index:
                    row.append(int(pattern["exceptional_degrees"][exceptional_index[target_support]]))
                else:
                    assert compression[source][target] % 4 == 0
                    row.append(compression[source][target] // 4)
            assert sum(row) == 12
            source_degrees.append(tuple(row))
            source_residual.append(tuple(4 * row[target] - compression[source][target]
                                         for target in range(21)))
        assert all(sum(source_degrees[local][target] for local in range(4))
                   == compression[source][target] for target in range(21))
        degrees.append(tuple(source_degrees))
        residual.append(tuple(source_residual))
    return tuple(degrees), tuple(residual)


def restrict_residual(residual, pivot_global):
    return tuple(tuple(tuple(row[column] for column in pivot_global) for row in fibre)
                 for fibre in residual)


def fixed_edges(entry, geometry, choices, exceptional):
    label_to_vertex = {
        tuple(label): 4 * support_index + local
        for support_index, support in enumerate(SUPPORTS)
        for local, label in enumerate(
            (2 * support[0] + a, 2 * support[1] + b)
            for a, b in itertools.product((0, 1), repeat=2)
        )
    }
    edges = set()
    for left, right in entry["internal_edges"]:
        edges.add(tuple(sorted((label_to_vertex[tuple(left)], label_to_vertex[tuple(right)]))))
    for choice in choices:
        for left, right in choice.edges:
            edges.add(tuple(sorted((label_to_vertex[geometry.vertices[left]],
                                    label_to_vertex[geometry.vertices[right]]))))
    # Ordinary internal C4s are deliberately left as three-option blocks.
    assert all((left // 4 == right // 4 and SUPPORTS[left // 4] in set(exceptional))
               or set(SUPPORTS[left // 4]) & set(SUPPORTS[right // 4])
               for left, right in edges)
    return edges


def contribution_options(degrees, residual, exceptional, fixed):
    fixed_value = sum6(edge_contribution(residual[left // 4][left % 4],
                                         residual[right // 4][right % 4])
                       for left, right in fixed)
    option_sets = []
    option_meta = []
    exceptional_set = set(exceptional)
    for source, support in enumerate(SUPPORTS):
        if support not in exceptional_set:
            options = tuple(sorted(set(internal_c4_options(residual[source]))))
            option_sets.append(options)
            option_meta.append({"kind": "ordinary_internal_C4", "support": list(support),
                                "options": len(options)})
    for source, target in itertools.combinations(range(21), 2):
        if set(SUPPORTS[source]) & set(SUPPORTS[target]):
            continue
        left_margin = tuple(degrees[source][local][target] for local in range(4))
        right_margin = tuple(degrees[target][local][source] for local in range(4))
        masks = bipartite_masks(left_margin, right_margin)
        assert masks
        options = tuple(sorted(set(option_contribution(
            mask, residual[source], residual[target]) for mask in masks
        )))
        option_sets.append(options)
        option_meta.append({
            "kind": "disjoint_4x4",
            "supports": [list(SUPPORTS[source]), list(SUPPORTS[target])],
            "left_margin": list(left_margin), "right_margin": list(right_margin),
            "binary_matrices": len(masks), "distinct_transport_vectors": len(options),
        })
    assert len(option_sets) == 13 + 105
    return fixed_value, tuple(option_sets), option_meta


def small_directions():
    answer = set()
    for values in itertools.product((-1, 0, 1), repeat=6):
        if not any(values):
            continue
        answer.add(primitive(values))
    return tuple(sorted(answer))


def interval_separators(target, fixed_value, option_sets, directions):
    residual_target = tuple(target[i] - fixed_value[i] for i in range(6))
    separators = []
    for direction in directions:
        target_scalar = dot6(direction, residual_target)
        lower = sum(min(dot6(direction, option) for option in options)
                    for options in option_sets)
        upper = sum(max(dot6(direction, option) for option in options)
                    for options in option_sets)
        if target_scalar < lower or target_scalar > upper:
            gap = lower - target_scalar if target_scalar < lower else target_scalar - upper
            separators.append((gap, direction, target_scalar, lower, upper))
    return sorted(separators, reverse=True)


def one_direction_interval(target, fixed_value, option_sets, direction):
    target_scalar = dot6(direction, tuple(target[i] - fixed_value[i] for i in range(6)))
    lower = sum(min(dot6(direction, option) for option in options)
                for options in option_sets)
    upper = sum(max(dot6(direction, option) for option in options)
                for options in option_sets)
    return target_scalar, lower, upper


def all_unordered_configs(pattern_row):
    """All row-multiset configurations, without the old Gram-key collapse."""
    patterns = pattern_row["patterns"]
    answer = []
    seen = set()
    for selected in itertools.combinations_with_replacement(range(len(patterns)), 4):
        full_rows = tuple(tuple(patterns[index]["scaled_W_row_on_exceptional"])
                          for index in selected)
        if any(sum(row[column] for row in full_rows) != 0
               for column in range(len(full_rows[0]))):
            continue
        pivot_rows = tuple(tuple(patterns[index]["pivot_scaled_W_coordinates"])
                           for index in selected)
        exceptional_degrees = tuple(
            tuple(patterns[index]["exceptional_degrees"][target]
                  for index in selected)
            for target in range(len(full_rows[0]))
        )
        key = (pivot_rows, exceptional_degrees)
        if key in seen:
            continue
        seen.add(key)
        answer.append({
            "selected_pattern_indices": selected,
            "pivot_rows": pivot_rows,
            "exceptional_degrees": exceptional_degrees,
            "pivot_gram6": defect.gram6_from_rows(pivot_rows),
        })
    return tuple(answer)


def config_from_csp(config, pattern_row):
    patterns = pattern_row["patterns"]
    selected = tuple(config["selected_pattern_indices"])
    rows = tuple(tuple(patterns[index]["pivot_scaled_W_coordinates"])
                 for index in selected)
    exceptional_degrees = tuple(
        tuple(patterns[index]["exceptional_degrees"][target] for index in selected)
        for target in range(len(patterns[0]["exceptional_degrees"]))
    )
    assert defect.gram6_from_rows(rows) == tuple(config["pivot_gram6"])
    return {
        "selected_pattern_indices": selected,
        "pivot_rows": rows,
        "exceptional_degrees": exceptional_degrees,
        "pivot_gram6": tuple(config["pivot_gram6"]),
    }


def margin_for(config, source, target, compression, exceptional_index):
    target_support = SUPPORTS[target]
    if target_support in exceptional_index:
        return config["exceptional_degrees"][exceptional_index[target_support]]
    assert compression[source][target] % 4 == 0
    return (compression[source][target] // 4,) * 4


@lru_cache(maxsize=None)
def scalar_block_interval_cached(left_rows, right_rows, left_margin, right_margin, direction):
    masks = bipartite_masks(left_margin, right_margin)
    assert masks
    values = tuple(dot6(direction, option_contribution(mask, left_rows, right_rows))
                   for mask in masks)
    return min(values), max(values)


def config_block_interval(source, left, target, right, compression,
                          exceptional_index, direction):
    return scalar_block_interval_cached(
        tuple(left["pivot_rows"]), tuple(right["pivot_rows"]),
        tuple(margin_for(left, source, target, compression, exceptional_index)),
        tuple(margin_for(right, target, source, compression, exceptional_index)),
        tuple(direction),
    )


def config_internal_interval(config, direction):
    values = tuple(dot6(direction, value)
                   for value in internal_c4_options(config["pivot_rows"]))
    return min(values), max(values)


def fixed_scalar(fixed, configs, direction):
    total = 0
    for left, right in fixed:
        left_row = configs[left // 4]["pivot_rows"][left % 4]
        right_row = configs[right // 4]["pivot_rows"][right % 4]
        total += dot6(direction, edge_contribution(left_row, right_row))
    return total


def matrix_fraction_add(*matrices):
    return [[sum((matrix[i][j] for matrix in matrices), Fraction(0))
             for j in range(len(matrices[0][0]))]
            for i in range(len(matrices[0]))]


def matrix_fraction_scale(value, matrix):
    value = Fraction(value)
    return [[value * entry for entry in row] for row in matrix]


def outer_sum(rows):
    return [[sum(Fraction(row[i]) * row[j] for row in rows)
             for j in range(3)] for i in range(3)]


def principal_psd_3(matrix):
    one = [matrix[i][i] for i in range(3)]
    two = [matrix[i][i] * matrix[j][j] - matrix[i][j] ** 2
           for i in range(3) for j in range(i + 1, 3)]
    determinant = (
        matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
        - matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
        + matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
    )
    return all(value >= 0 for value in (*one, *two, determinant)), one, two, determinant


def show_fraction(value):
    value = Fraction(value)
    return value.numerator if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def show_matrix(matrix):
    return [[show_fraction(value) for value in row] for row in matrix]


def root_incidence_spectral_split(pivot_rows, gram, first_moment):
    """Exact B-eigenspace Gram masses of three residual columns.

    The 14x84 root-label incidence L has LL^T=11I+J-M.  Its mate-even
    sum-zero row space maps to B-eigenvalue -2 (Gram inverse 1/10), and its
    mate-odd row space maps to eigenvalue 0 (Gram inverse 1/12).  The
    orthogonal complement has eigenvalues 3,-4.  R has zero column sums.
    """
    label_sums = [[Fraction(0) for _ in range(3)] for _ in range(14)]
    for source, support in enumerate(SUPPORTS):
        for local, row in enumerate(pivot_rows[source]):
            labels = (2 * support[0] + local // 2, 2 * support[1] + local % 2)
            for label in labels:
                for coordinate in range(3):
                    label_sums[label][coordinate] += row[coordinate]
    assert all(sum(label_sums[label][coordinate] for label in range(14)) == 0
               for coordinate in range(3))
    even_rows = [[label_sums[2 * group][i] + label_sums[2 * group + 1][i]
                  for i in range(3)] for group in range(7)]
    odd_rows = [[label_sums[2 * group][i] - label_sums[2 * group + 1][i]
                 for i in range(3)] for group in range(7)]
    g_minus2 = matrix_fraction_scale(Fraction(1, 20), outer_sum(even_rows))
    g_zero = matrix_fraction_scale(Fraction(1, 24), outer_sum(odd_rows))
    g_total = [[Fraction(gram[i][j]) for j in range(3)] for i in range(3)]
    t_total = [[Fraction(first_moment[i][j]) for j in range(3)] for i in range(3)]
    g_kernel = matrix_fraction_add(
        g_total, matrix_fraction_scale(-1, g_minus2), matrix_fraction_scale(-1, g_zero)
    )
    g_plus3 = matrix_fraction_scale(Fraction(1, 7), matrix_fraction_add(
        t_total, matrix_fraction_scale(2, g_minus2), matrix_fraction_scale(4, g_kernel)
    ))
    g_minus4 = matrix_fraction_add(g_kernel, matrix_fraction_scale(-1, g_plus3))
    masses = {"minus2": g_minus2, "zero": g_zero,
              "plus3": g_plus3, "minus4": g_minus4}
    checks = {name: principal_psd_3(matrix) for name, matrix in masses.items()}
    reconstructed_gram = matrix_fraction_add(*masses.values())
    reconstructed_moment = matrix_fraction_add(
        matrix_fraction_scale(-2, g_minus2),
        matrix_fraction_scale(3, g_plus3),
        matrix_fraction_scale(-4, g_minus4),
    )
    assert reconstructed_gram == g_total
    assert reconstructed_moment == t_total
    return {
        "masses": {name: show_matrix(matrix) for name, matrix in masses.items()},
        "PSD": {name: value[0] for name, value in checks.items()},
        "principal_minors": {
            name: {
                "order1": list(map(show_fraction, value[1])),
                "order2": list(map(show_fraction, value[2])),
                "determinant": show_fraction(value[3]),
            } for name, value in checks.items()
        },
    }


def vector_add3(left, right):
    return tuple(left[i] + right[i] for i in range(3))


def parse_fraction(value):
    return Fraction(str(value))


def leverage_forbidden_patterns(leverage, key):
    """Return the exact row patterns excluded by the two projector caps."""
    row = next(item for item in leverage["rows"] if tuple(item["key"]) == tuple(key))
    forbidden = set()
    values = {}
    for fibre in row["by_source_fibre"]:
        support = tuple(fibre["source_support"])
        for pattern in fibre["patterns"]:
            index = int(pattern["pattern_index"])
            minus4 = parse_fraction(pattern["minus4_leverage"])
            plus3 = parse_fraction(pattern["plus3_leverage"])
            values[(support, index)] = (minus4, plus3)
            if minus4 > 40 or plus3 > Fraction(160, 3):
                forbidden.add((support, index))
    return forbidden, values


def selected_leverage_violations(selected_by_support, forbidden):
    return sorted(
        (support, int(index))
        for support, indices in selected_by_support.items()
        for index in indices
        if (support, int(index)) in forbidden
    )


def flatten4x3(rows):
    return tuple(value for row in rows for value in row)


def vector_add(left, right):
    return tuple(a + b for a, b in zip(left, right))


def vector_subtract(left, right):
    return tuple(a - b for a, b in zip(left, right))


def exact_option_sum_contains(option_sets, target):
    """Exact target membership in a Minkowski sum, with box pruning.

    The option sets are deliberately kept joint across all four vertices of
    one source fibre.  This is the smallest synchronization missing from the
    earlier vertex-by-vertex relaxation.
    """
    option_sets = tuple(
        tuple(sorted(set(options)))
        for options in sorted(option_sets, key=len)
    )
    dimension = len(target)
    suffix_min = [[0] * dimension for _ in range(len(option_sets) + 1)]
    suffix_max = [[0] * dimension for _ in range(len(option_sets) + 1)]
    for index in range(len(option_sets) - 1, -1, -1):
        for coordinate in range(dimension):
            suffix_min[index][coordinate] = (
                suffix_min[index + 1][coordinate]
                + min(option[coordinate] for option in option_sets[index])
            )
            suffix_max[index][coordinate] = (
                suffix_max[index + 1][coordinate]
                + max(option[coordinate] for option in option_sets[index])
            )
    nodes = 0

    @lru_cache(maxsize=None)
    def visit(index, remaining):
        nonlocal nodes
        nodes += 1
        if any(
            remaining[coordinate] < suffix_min[index][coordinate]
            or remaining[coordinate] > suffix_max[index][coordinate]
            for coordinate in range(dimension)
        ):
            return False
        if index == len(option_sets):
            return not any(remaining)
        # Trying close options first is only a speed heuristic; the cached DFS
        # still exhausts every binary block option if necessary.
        ordered = sorted(
            option_sets[index],
            key=lambda option: sum(
                abs(remaining[c] - option[c]) for c in range(dimension)
            ),
        )
        return any(
            visit(index + 1, vector_subtract(remaining, option))
            for option in ordered
        )

    passed = visit(0, tuple(target))
    return passed, nodes, [len(options) for options in option_sets]


def determinant_square(matrix):
    matrix = [[Fraction(value) for value in row] for row in matrix]
    determinant = Fraction(1)
    for column in range(len(matrix)):
        pivot = next((row for row in range(column, len(matrix))
                      if matrix[row][column]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            matrix[column], matrix[pivot] = matrix[pivot], matrix[column]
            determinant = -determinant
        scale = matrix[column][column]
        determinant *= scale
        matrix[column] = [value / scale for value in matrix[column]]
        for row in range(column + 1, len(matrix)):
            if not matrix[row][column]:
                continue
            factor = matrix[row][column]
            matrix[row] = [left - factor * right
                           for left, right in zip(matrix[row], matrix[column])]
    return determinant


def solve_square(matrix, target):
    size = len(matrix)
    augmented = [
        [Fraction(value) for value in matrix[row]] + [Fraction(target[row])]
        for row in range(size)
    ]
    for column in range(size):
        pivot = next(row for row in range(column, size)
                     if augmented[row][column])
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        scale = augmented[column][column]
        augmented[column] = [value / scale for value in augmented[column]]
        for row in range(size):
            if row == column or not augmented[row][column]:
                continue
            factor = augmented[row][column]
            augmented[row] = [left - factor * right
                              for left, right in zip(augmented[row], augmented[column])]
    return tuple(augmented[row][-1] for row in range(size))


def projector_residual_pair_table(residual, z, q, d):
    """Exact 2x2 minors of the residual -4 spectral projector.

    If x lies in fibre G, set s_x=Z_G-R_x.  After scaling by 112,

      diag G_x = 40-s_x Z^+ s_x,
      G_xy = 4-6q_xy-2d_xy-16B_xy-s_x Z^+ s_y.

    The returned two-bit value records whether B_xy=0 and/or B_xy=1
    survives the corresponding principal minor.
    """
    rank = defect.rank(z)
    principal = next(
        indices for indices in itertools.combinations(range(21), rank)
        if determinant_square([[z[i][j] for j in indices] for i in indices])
    )
    principal_matrix = [[z[i][j] for j in principal] for i in principal]
    s_rows = []
    for source in range(21):
        for local in range(4):
            s_rows.append(tuple(z[source][target] - residual[source][local][target]
                                for target in range(21)))
    solutions = [solve_square(principal_matrix, [row[i] for i in principal])
                 for row in s_rows]

    def bilinear(left, right):
        return sum(Fraction(s_rows[left][i]) * solutions[right][position]
                   for position, i in enumerate(principal))

    diagonal = [Fraction(40) - bilinear(vertex, vertex) for vertex in range(84)]
    allowed = [[0] * 84 for _ in range(84)]
    edge_weights = [[Fraction(0) for _ in range(84)] for _ in range(84)]
    edge_targets = [Fraction(0) for _ in range(84)]
    base_off_diagonal = [[Fraction(0) for _ in range(84)] for _ in range(84)]
    categories = Counter()
    first_forced = None
    for left, right in itertools.combinations(range(84), 2):
        product = diagonal[left] * diagonal[right]
        bits = 0
        values = []
        base = Fraction(
            4 - 6 * q[left][right] - 2 * d[left][right]
        ) - bilinear(left, right)
        base_off_diagonal[left][right] = base_off_diagonal[right][left] = base
        edge_weights[left][right] = edge_weights[right][left] = 8 - base
        for adjacency in (0, 1):
            off_diagonal = base - 16 * adjacency
            values.append(off_diagonal)
            if diagonal[left] >= 0 and diagonal[right] >= 0 \
                    and off_diagonal * off_diagonal <= product:
                bits |= 1 << adjacency
        allowed[left][right] = allowed[right][left] = bits
        name = {0: "neither", 1: "only_B0", 2: "only_B1", 3: "both"}[bits]
        categories[name] += 1
        if bits != 3 and first_forced is None:
            first_forced = {
                "vertices": [left, right],
                "supports": [list(SUPPORTS[left // 4]), list(SUPPORTS[right // 4])],
                "locals": [left % 4, right % 4],
                "allowed_bits": bits,
                "diagonal": [show_fraction(diagonal[left]), show_fraction(diagonal[right])],
                "scaled_off_diagonal_B0_B1": list(map(show_fraction, values)),
            }
    for vertex in range(84):
        edge_targets[vertex] = (
            112 * diagonal[vertex] - diagonal[vertex] ** 2
            - sum(base_off_diagonal[vertex][other] ** 2
                  for other in range(84) if other != vertex)
        ) / 32
    return allowed, edge_weights, edge_targets, {
        "Z_rank": rank,
        "principal_indices": list(principal),
        "diagonal_minimum": show_fraction(min(diagonal)),
        "diagonal_zero_count": sum(value == 0 for value in diagonal),
        "pair_domain_histogram": dict(categories),
        "linear_edge_target_denominator_histogram": dict(Counter(
            value.denominator for value in edge_targets
        )),
        "first_restricted_pair": first_forced,
    }


def pair_mask_allowed(mask, source, target, allowed):
    return all(
        allowed[4 * source + row][4 * target + column] &
        (2 if (mask >> (4 * row + column)) & 1 else 1)
        for row in range(4) for column in range(4)
    )


def fixed_projector_pairs_valid(fixed, exceptional, allowed):
    fixed = set(fixed)
    exceptional_set = set(exceptional)
    for left, right in itertools.combinations(range(84), 2):
        source, target = left // 4, right // 4
        known = (
            (source == target and SUPPORTS[source] in exceptional_set)
            or (source != target and bool(set(SUPPORTS[source]) & set(SUPPORTS[target])))
        )
        if not known:
            continue
        adjacency = int((left, right) in fixed)
        if not allowed[left][right] & (2 if adjacency else 1):
            return False
    return True


def projector_block_domain_relaxation(degrees, residual, z, q, d,
                                      fixed_edge_sets, exceptional):
    """Filter every unresolved local block by all residual-projector 2x2 minors."""
    allowed, edge_weights, edge_targets, diagnostics = projector_residual_pair_table(
        residual, z, q, d
    )
    ordinary_failures = []
    exceptional_set = set(exceptional)
    for source, support in enumerate(SUPPORTS):
        if support in exceptional_set:
            continue
        orientations = []
        all_edges = set(itertools.combinations(range(4), 2))
        for missing in (
            {(0, 1), (2, 3)}, {(0, 2), (1, 3)}, {(0, 3), (1, 2)},
        ):
            edges = all_edges - missing
            if all(allowed[4 * source + i][4 * source + j]
                   & (2 if (i, j) in edges else 1)
                   for i, j in all_edges):
                orientations.append(sorted(map(list, edges)))
        if not orientations:
            ordinary_failures.append(list(support))
    empty_blocks = []
    for source, target in itertools.combinations(range(21), 2):
        if set(SUPPORTS[source]) & set(SUPPORTS[target]):
            continue
        left_margin = tuple(degrees[source][row][target] for row in range(4))
        right_margin = tuple(degrees[target][column][source] for column in range(4))
        if not any(pair_mask_allowed(mask, source, target, allowed)
                   for mask in bipartite_masks(left_margin, right_margin)):
            empty_blocks.append([list(SUPPORTS[source]), list(SUPPORTS[target])])
    valid_fixed = [fixed_projector_pairs_valid(fixed, exceptional, allowed)
                   for fixed in fixed_edge_sets]
    diagnostics.update({
        "ordinary_internal_empty_domains": ordinary_failures,
        "disjoint_4x4_empty_domains": empty_blocks,
        "fixed_overlap_choices_tested": len(valid_fixed),
        "fixed_overlap_choices_rejected": sum(not value for value in valid_fixed),
        "fixed_overlap_choices_passed": sum(valid_fixed),
    })
    return allowed, edge_weights, edge_targets, tuple(valid_fixed), diagnostics


def pointwise_transport_relaxation(degrees, residual, pivot_rows, fixed,
                                   compression, K4, pivot_global, exceptional):
    """Per-vertex exact reachable-set relaxation of 4BR=PK4-R(C+4I).

    Each unresolved 4x4 block is enumerated exactly, but different vertices
    may choose inconsistent matrices.  Hence failure is a sound cut and pass
    is only a countercontrol for this relaxation.
    """
    fixed_adjacency = [set() for _ in range(84)]
    for left, right in fixed:
        fixed_adjacency[left].add(right)
        fixed_adjacency[right].add(left)
    exceptional_set = set(exceptional)
    records = []
    all_pass = True
    maximum_reachable = 0
    for vertex in range(84):
        source = vertex // 4
        local = vertex % 4
        fixed_sum = (0, 0, 0)
        for neighbor in fixed_adjacency[vertex]:
            fixed_sum = vector_add3(
                fixed_sum, pivot_rows[neighbor // 4][neighbor % 4]
            )
        option_sets = []
        if SUPPORTS[source] not in exceptional_set:
            option_sets.append(tuple(
                tuple(sum(pivot_rows[source][other][coordinate] for other in selected)
                      for coordinate in range(3))
                for selected in itertools.combinations(
                    [other for other in range(4) if other != local], 2
                )
            ))
        for target in range(21):
            if target == source or set(SUPPORTS[source]) & set(SUPPORTS[target]):
                continue
            left_margin = tuple(degrees[source][row][target] for row in range(4))
            right_margin = tuple(degrees[target][column][source] for column in range(4))
            masks = bipartite_masks(left_margin, right_margin)
            values = set()
            for mask in masks:
                values.add(tuple(
                    sum(pivot_rows[target][column][coordinate]
                        for column in range(4)
                        if (mask >> (4 * local + column)) & 1)
                    for coordinate in range(3)
                ))
            option_sets.append(tuple(sorted(values)))
        assert len(option_sets) == 10 + int(SUPPORTS[source] not in exceptional_set)

        reachable = {(0, 0, 0)}
        for options in option_sets:
            reachable = {vector_add3(value, option)
                         for value in reachable for option in options}
        maximum_reachable = max(maximum_reachable, len(reachable))
        rhs = []
        for pivot in pivot_global:
            value = K4[source][pivot]
            for target in range(21):
                value -= residual[source][local][target] * (
                    compression[target][pivot] + 4 * int(target == pivot)
                )
            rhs.append(value)
        required_free_numerator = tuple(rhs[i] - 4 * fixed_sum[i] for i in range(3))
        passed = all(value % 4 == 0 for value in required_free_numerator)
        required_free = tuple(value // 4 for value in required_free_numerator) if passed else None
        passed = passed and required_free in reachable
        all_pass &= passed
        if not passed or len(records) < 3:
            coordinate_bounds = [
                [min(value[i] for value in reachable), max(value[i] for value in reachable)]
                for i in range(3)
            ]
            records.append({
                "vertex": vertex,
                "support": list(SUPPORTS[source]),
                "local": local,
                "fixed_neighbor_sum": list(fixed_sum),
                "rhs_numerator": rhs,
                "required_free_numerator": list(required_free_numerator),
                "required_free_sum": None if required_free is None else list(required_free),
                "reachable": passed,
                "reachable_set_size": len(reachable),
                "coordinate_bounds": coordinate_bounds,
            })
    return {
        "all_vertices_pass": all_pass,
        "failed_vertices": sum(not row["reachable"] for row in records),
        "maximum_reachable_set_size": maximum_reachable,
        "diagnostic_records": records,
    }


def exceptional_transport_over_all_choices(degrees, residual, pivot_rows,
                                           fixed_edge_sets, compression, K4,
                                           pivot_global, exceptional,
                                           pair_allowed=None,
                                           candidate_indices=None):
    """Test all overlap maps using only exceptional-vertex transport rows.

    Ordinary row permutations merely permute, together, the columns and their
    (margin,residual) labels in every exceptional--ordinary block.  Therefore
    the row-neighbour-sum option set seen from an exceptional vertex depends
    only on the ordinary row multiset, not its displayed ordering.
    """
    fixed_adjacencies = []
    for fixed in fixed_edge_sets:
        adjacency = [set() for _ in range(84)]
        for left, right in fixed:
            adjacency[left].add(right)
            adjacency[right].add(left)
        fixed_adjacencies.append(adjacency)
    passing = set(
        range(len(fixed_edge_sets)) if candidate_indices is None
        else map(int, candidate_indices)
    )
    eliminated_by_vertex = Counter()
    first_failure = None
    exceptional_global = tuple(SUPPORTS.index(support) for support in exceptional)
    for source in exceptional_global:
        for local in range(4):
            vertex = 4 * source + local
            option_sets = []
            for target in range(21):
                if target == source or set(SUPPORTS[source]) & set(SUPPORTS[target]):
                    continue
                left_margin = tuple(degrees[source][row][target] for row in range(4))
                right_margin = tuple(degrees[target][column][source] for column in range(4))
                values = set()
                masks = bipartite_masks(left_margin, right_margin)
                if pair_allowed is not None:
                    masks = tuple(mask for mask in masks
                                  if pair_mask_allowed(mask, source, target, pair_allowed))
                for mask in masks:
                    values.add(tuple(
                        sum(pivot_rows[target][column][coordinate]
                            for column in range(4)
                            if (mask >> (4 * local + column)) & 1)
                        for coordinate in range(3)
                    ))
                option_sets.append(tuple(values))
            assert len(option_sets) == 10
            reachable = {(0, 0, 0)}
            for options in option_sets:
                reachable = {vector_add3(value, option)
                             for value in reachable for option in options}
            rhs = []
            for pivot in pivot_global:
                value = K4[source][pivot]
                for target in range(21):
                    value -= residual[source][local][target] * (
                        compression[target][pivot] + 4 * int(target == pivot)
                    )
                rhs.append(value)
            newly_failed = []
            for choice_index in tuple(passing):
                fixed_sum = (0, 0, 0)
                for neighbor in fixed_adjacencies[choice_index][vertex]:
                    fixed_sum = vector_add3(
                        fixed_sum, pivot_rows[neighbor // 4][neighbor % 4]
                    )
                numerator = tuple(rhs[i] - 4 * fixed_sum[i] for i in range(3))
                required = None
                if all(value % 4 == 0 for value in numerator):
                    required = tuple(value // 4 for value in numerator)
                if required not in reachable:
                    passing.remove(choice_index)
                    newly_failed.append(choice_index)
                    if first_failure is None:
                        first_failure = {
                            "vertex": vertex,
                            "support": list(SUPPORTS[source]),
                            "local": local,
                            "overlap_choice_index": choice_index,
                            "fixed_neighbor_sum": list(fixed_sum),
                            "rhs_numerator": rhs,
                            "required_free_numerator": list(numerator),
                            "required_free_sum": None if required is None else list(required),
                            "reachable_set_size": len(reachable),
                            "coordinate_bounds": [
                                [min(value[i] for value in reachable),
                                 max(value[i] for value in reachable)]
                                for i in range(3)
                            ],
                        }
            if newly_failed:
                eliminated_by_vertex[vertex] += len(newly_failed)
            if not passing:
                break
        if not passing:
            break
    return {
        "overlap_choices": len(fixed_edge_sets),
        "passed": len(passing),
        "rejected": len(fixed_edge_sets) - len(passing),
        "passing_choice_indices": sorted(passing),
        "eliminated_by_first_failing_exceptional_vertex": dict(eliminated_by_vertex),
        "first_failure": first_failure,
    }


def exceptional_transport_with_projector_norm(
    degrees, residual, pivot_rows, fixed_edge_sets, candidate_indices,
    compression, K4, pivot_global, exceptional, pair_allowed,
    projector_edge_weights, projector_edge_targets,
):
    """Pointwise transport plus diag(G4^2)=112 diag(G4).

    The latter is linear in B because B_xy is binary.  For
    a_xy=4-6q_xy-2d_xy-s_x Z^+s_y it reads

      sum_{y~x} (8-a_xy)
        =(112g_x-g_x^2-sum_{y!=x}a_xy^2)/32.

    Every unresolved block is still independent from every other vertex, so
    failure is a necessary-condition cut and passage remains a relaxation.
    """
    fixed_adjacencies = []
    for fixed in fixed_edge_sets:
        adjacency = [set() for _ in range(84)]
        for left, right in fixed:
            adjacency[left].add(right)
            adjacency[right].add(left)
        fixed_adjacencies.append(adjacency)
    passing = set(map(int, candidate_indices))
    initial = len(passing)
    first_failure = None
    exceptional_global = tuple(SUPPORTS.index(support) for support in exceptional)
    for source in exceptional_global:
        for local in range(4):
            vertex = 4 * source + local
            option_sets = []
            for target in range(21):
                if target == source or set(SUPPORTS[source]) & set(SUPPORTS[target]):
                    continue
                left_margin = tuple(degrees[source][row][target] for row in range(4))
                right_margin = tuple(degrees[target][column][source] for column in range(4))
                masks = bipartite_masks(left_margin, right_margin)
                if pair_allowed is not None:
                    masks = tuple(
                        mask for mask in masks
                        if pair_mask_allowed(mask, source, target, pair_allowed)
                    )
                values = set()
                for mask in masks:
                    neighbors = [
                        4 * target + column for column in range(4)
                        if (mask >> (4 * local + column)) & 1
                    ]
                    values.add(tuple(
                        sum(pivot_rows[target][column][coordinate]
                            for column in range(4)
                            if (mask >> (4 * local + column)) & 1)
                        for coordinate in range(3)
                    ) + (sum(projector_edge_weights[vertex][other]
                             for other in neighbors),))
                option_sets.append(tuple(values))
            assert len(option_sets) == 10
            reachable = {(Fraction(0),) * 4}
            for options in option_sets:
                if not options:
                    reachable = set()
                    break
                reachable = {vector_add(value, option)
                             for value in reachable for option in options}

            rhs = []
            for pivot in pivot_global:
                value = K4[source][pivot]
                for target in range(21):
                    value -= residual[source][local][target] * (
                        compression[target][pivot] + 4 * int(target == pivot)
                    )
                rhs.append(value)
            newly_failed = []
            for choice_index in tuple(sorted(passing)):
                fixed_sum = (0, 0, 0)
                fixed_weight = Fraction(0)
                for neighbor in fixed_adjacencies[choice_index][vertex]:
                    fixed_sum = vector_add3(
                        fixed_sum, pivot_rows[neighbor // 4][neighbor % 4]
                    )
                    fixed_weight += projector_edge_weights[vertex][neighbor]
                numerator = tuple(rhs[i] - 4 * fixed_sum[i] for i in range(3))
                required = None
                if all(value % 4 == 0 for value in numerator):
                    required = tuple(Fraction(value // 4) for value in numerator) + (
                        projector_edge_targets[vertex] - fixed_weight,
                    )
                if required not in reachable:
                    passing.remove(choice_index)
                    newly_failed.append(choice_index)
                    if first_failure is None:
                        first_failure = {
                            "vertex": vertex,
                            "support": list(SUPPORTS[source]),
                            "local": local,
                            "overlap_choice_index": choice_index,
                            "required_free_vector": None if required is None else [
                                show_fraction(value) for value in required
                            ],
                            "reachable_set_size": len(reachable),
                            "projector_edge_target": show_fraction(
                                projector_edge_targets[vertex]
                            ),
                        }
            if not passing:
                break
        if not passing:
            break
    return {
        "candidate_overlap_choices": initial,
        "rejected": initial - len(passing),
        "passed": len(passing),
        "passing_choice_indices": sorted(passing),
        "first_failure": first_failure,
    }


def exceptional_fibre_synchronized_transport(
    degrees, residual, pivot_rows, fixed_edge_sets, candidate_indices,
    compression, K4, pivot_global, exceptional, pair_allowed=None,
):
    """Synchronize the four transport rows within each exceptional fibre.

    A single 4x4 binary block must serve all four source vertices.  The older
    pointwise relaxation allowed those four vertices to choose four unrelated
    matrices.  Here every one of the ten disjoint target blocks is enumerated
    as a joint 12-vector and exact target membership is decided by DFS.  Blocks
    shared by two *different* exceptional source fibres are still relaxed
    independently, so rejection is sound and passage is only a countercontrol.
    """
    fixed_adjacencies = []
    for fixed in fixed_edge_sets:
        adjacency = [set() for _ in range(84)]
        for left, right in fixed:
            adjacency[left].add(right)
            adjacency[right].add(left)
        fixed_adjacencies.append(adjacency)

    passing = set(map(int, candidate_indices))
    initial = len(passing)
    nodes = 0
    first_failure = None
    per_source = []
    exceptional_global = tuple(SUPPORTS.index(support) for support in exceptional)
    for source in exceptional_global:
        option_sets = []
        option_metadata = []
        for target in range(21):
            if target == source or set(SUPPORTS[source]) & set(SUPPORTS[target]):
                continue
            left_margin = tuple(degrees[source][row][target] for row in range(4))
            right_margin = tuple(degrees[target][column][source] for column in range(4))
            masks = bipartite_masks(left_margin, right_margin)
            if pair_allowed is not None:
                masks = tuple(mask for mask in masks
                              if pair_mask_allowed(mask, source, target, pair_allowed))
            options = set()
            for mask in masks:
                options.add(tuple(
                    sum(
                        pivot_rows[target][column][coordinate]
                        for column in range(4)
                        if (mask >> (4 * local + column)) & 1
                    )
                    for local in range(4) for coordinate in range(3)
                ))
            option_sets.append(tuple(sorted(options)))
            option_metadata.append({
                "target_support": list(SUPPORTS[target]),
                "binary_matrices": len(masks),
                "joint_vectors": len(options),
            })
        assert len(option_sets) == 10

        rhs_rows = []
        for local in range(4):
            rhs = []
            for pivot in pivot_global:
                value = K4[source][pivot]
                for target in range(21):
                    value -= residual[source][local][target] * (
                        compression[target][pivot] + 4 * int(target == pivot)
                    )
                rhs.append(value)
            rhs_rows.append(tuple(rhs))

        cache = {}
        newly_failed = []
        for choice_index in tuple(sorted(passing)):
            required_rows = []
            integral = True
            for local in range(4):
                vertex = 4 * source + local
                fixed_sum = (0, 0, 0)
                for neighbor in fixed_adjacencies[choice_index][vertex]:
                    fixed_sum = vector_add3(
                        fixed_sum, pivot_rows[neighbor // 4][neighbor % 4]
                    )
                numerator = tuple(
                    rhs_rows[local][coordinate] - 4 * fixed_sum[coordinate]
                    for coordinate in range(3)
                )
                if any(value % 4 for value in numerator):
                    integral = False
                    required_rows.append(None)
                else:
                    required_rows.append(tuple(value // 4 for value in numerator))
            target = None if not integral else flatten4x3(required_rows)
            if target is None:
                passed = False
                local_nodes = 0
                option_sizes = [len(options) for options in option_sets]
            elif target in cache:
                passed, local_nodes, option_sizes = cache[target]
            else:
                passed, local_nodes, option_sizes = exact_option_sum_contains(
                    option_sets, target
                )
                cache[target] = (passed, local_nodes, option_sizes)
                nodes += local_nodes
            if not passed:
                passing.remove(choice_index)
                newly_failed.append(choice_index)
                if first_failure is None:
                    first_failure = {
                        "source_support": list(SUPPORTS[source]),
                        "overlap_choice_index": choice_index,
                        "required_joint_free_sum": None if target is None else list(target),
                        "joint_option_sizes": option_sizes,
                        "DFS_nodes": local_nodes,
                        "block_metadata": option_metadata,
                    }
        per_source.append({
            "source_support": list(SUPPORTS[source]),
            "entered": len(passing) + len(newly_failed),
            "rejected": len(newly_failed),
            "remaining": len(passing),
            "distinct_targets_solved": len(cache),
        })
        if not passing:
            break
    return {
        "candidate_overlap_choices": initial,
        "rejected": initial - len(passing),
        "passed": len(passing),
        "passing_choice_indices": sorted(passing),
        "DFS_nodes": nodes,
        "per_source_fibre": per_source,
        "first_failure": first_failure,
    }


def materialize_first(fixed, degrees):
    edges = set(fixed)
    for source, support in enumerate(SUPPORTS):
        if not any(left // 4 == source for edge in fixed for left in edge):
            # Only ordinary fibres lack fixed internal edges.
            for left, right in ((0, 1), (1, 3), (3, 2), (2, 0)):
                edges.add(tuple(sorted((4 * source + left, 4 * source + right))))
    for source, target in itertools.combinations(range(21), 2):
        if set(SUPPORTS[source]) & set(SUPPORTS[target]):
            continue
        left = tuple(degrees[source][local][target] for local in range(4))
        right = tuple(degrees[target][local][source] for local in range(4))
        mask = bipartite_masks(left, right)[0]
        for i in range(4):
            for j in range(4):
                if (mask >> (4 * i + j)) & 1:
                    edges.add((4 * source + i, 4 * target + j))
    return edges


def graph_diagnostics(edges, residual, target_pivot):
    adjacency = [0] * 84
    actual = [0] * 6
    for left, right in edges:
        adjacency[left] |= 1 << right
        adjacency[right] |= 1 << left
        value = edge_contribution(residual[left // 4][left % 4],
                                  residual[right // 4][right % 4])
        actual = [a + b for a, b in zip(actual, value)]
    triangle_count = sum((adjacency[left] & adjacency[right]).bit_count()
                         for left, right in edges) // 3
    return {
        "edges": len(edges),
        "degree_histogram": dict(Counter(mask.bit_count() for mask in adjacency)),
        "triangles": triangle_count,
        "trace_B3": 6 * triangle_count,
        "pivot_RtBR": actual,
        "pivot_transport_residual": [actual[i] - target_pivot[i] for i in range(6)],
    }


def main():
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    mining = json.loads(MINING.read_text(encoding="utf-8"))
    prior = json.loads(DEFECT.read_text(encoding="utf-8"))
    degree_control = json.loads(DEGREE_WITNESS.read_text(encoding="utf-8"))
    leverage = json.loads(LEVERAGE.read_text(encoding="utf-8"))
    entry = next(row for row in catalog["macro_entries"]
                 if row["signature_stabilizer_canonical"]
                 and int(row["source_row_index"]) == 724 and int(row["Q"]) == 2)
    key = defect.macro_key(entry)
    assert key == (724, 1, 0)
    leverage_forbidden, leverage_values = leverage_forbidden_patterns(leverage, key)
    assert len(leverage_forbidden) == 9
    profile = next(row for row in mining["profile_rows"]["71"]
                   if defect.macro_key(row) == key)
    structural = next(row for row in prior["rows"] if tuple(row["key"]) == key)
    source = defect.source_row_map(fast)[724]
    geometry = fast.RowGeometry(source)
    oriented = fast.oriented_assignment(geometry, entry["state_indices"])
    internal = fast.internal_mask(geometry, oriented)
    domains = defect.exact_signature_domains(fast, geometry, oriented, entry)
    exceptional = tuple(tuple(row["support"]) for row in entry["exceptional_supports"])
    _ex, _ei, compression, _c0, z = defect.build_compression(entry, profile)
    _outer_labels, outer_q, outer_d = fixed_relation_matrices()
    transport, qbar, dbar, gram2, moment3 = transport_target(compression)
    pivot_local = structural["rank_three_integer_row_patterns"]["pivot_exceptional_indices"]
    pivot_global = tuple(SUPPORTS.index(exceptional[index]) for index in pivot_local)
    target_pivot = tuple(transport[pivot_global[i]][pivot_global[j]] for i, j in UPPER6)

    ordinary_reachable, _ordinary_audit = defect.ordinary_gram_reachable(
        structural, exceptional,
        tuple(4 * structural["K4"][pivot_global[i]][pivot_global[j]] for i, j in UPPER6),
    )
    patterns = {tuple(row["source_support"]): row
                for row in structural["rank_three_integer_row_patterns"]["by_source_fibre"]}
    directions = small_directions()
    cache = {}
    feasible_signature_representatives = {}
    feasible_signature_all_choices = {}
    branch_records = []
    outcomes = Counter()
    first_separator = None
    first_interval_control = None
    for choices in itertools.product(*domains):
        mask = internal
        for choice in choices:
            mask |= choice.mask
        adjacency = defect.mask_adjacency(len(geometry.vertices), geometry.pair_positions, mask)
        fixed_degrees = defect.fixed_exceptional_degrees(geometry, adjacency, exceptional)
        fixed_key = tuple(tuple(tuple(sorted(row.items())) for row in fibre_rows)
                          for fibre_rows in fixed_degrees)
        if fixed_key not in cache:
            config_domains = tuple(defect.enumerate_fibre_configurations(
                patterns[support], fixed=fixed_degrees[local]
            ) for local, support in enumerate(exceptional))
            if any(not domain for domain in config_domains):
                cache[fixed_key] = ("empty", None)
            else:
                feasible, _nodes, witness = defect.exceptional_config_csp(
                    exceptional, config_domains, ordinary_reachable,
                    tuple(4 * structural["K4"][pivot_global[i]][pivot_global[j]]
                          for i, j in UPPER6),
                )
                cache[fixed_key] = ("feasible" if feasible else "gram_unsat", witness)
        outcome, witness = cache[fixed_key]
        outcomes[outcome] += 1
        if outcome != "feasible":
            continue
        feasible_signature_representatives.setdefault(fixed_key, choices)
        feasible_signature_all_choices.setdefault(fixed_key, []).append(choices)
        degrees, residual = selected_rows(structural, exceptional, compression, witness)
        witness_selected = {
            tuple(row["support"]): tuple(row["selected_pattern_indices"])
            for row in witness["exceptional_fibres"] + witness["ordinary_fibres"]
        }
        leverage_violations = selected_leverage_violations(
            witness_selected, leverage_forbidden
        )
        pivot_residual = restrict_residual(residual, pivot_global)
        fixed = fixed_edges(entry, geometry, choices, exceptional)
        fixed_value, option_sets, option_meta = contribution_options(
            degrees, pivot_residual, exceptional, fixed
        )
        separators = interval_separators(target_pivot, fixed_value, option_sets, directions)
        pointwise = pointwise_transport_relaxation(
            degrees, residual, pivot_residual, fixed, compression,
            structural["K4"], pivot_global, exceptional,
        )
        deterministic = graph_diagnostics(
            materialize_first(fixed, degrees), pivot_residual, target_pivot
        )
        record = {
            "choice_indices": [domains[group].index(choice) for group, choice in enumerate(choices)],
            "fixed_signature_index": sorted(cache).index(fixed_key),
            "first_degree_configuration_fingerprint": hashlib.sha256(
                json.dumps(witness, sort_keys=True).encode()
            ).hexdigest()[:16],
            "independent_block_option_count_product_decimal_digits": len(str(math.prod(map(len, option_sets)))),
            "small_direction_interval_separated": bool(separators),
            "best_separator": None if not separators else {
                "gap": separators[0][0], "upper6_direction": list(separators[0][1]),
                "target_after_fixed": separators[0][2],
                "interval": [separators[0][3], separators[0][4]],
            },
            "pointwise_transport_relaxation": pointwise,
            "projector_leverage_violations": [
                {"support": list(support), "pattern_index": index}
                for support, index in leverage_violations
            ],
            "deterministic_first_block_completion": deterministic,
        }
        branch_records.append(record)
        if separators and first_separator is None:
            direction = separators[0][1]
            first_separator = {
                **record,
                "fixed_pivot_contribution": list(fixed_value),
                "target_pivot_RtBR": list(target_pivot),
                "option_meta": option_meta,
                "scalar_block_intervals": [
                    [min(dot6(direction, option) for option in options),
                     max(dot6(direction, option) for option in options)]
                    for options in option_sets
                ],
            }
        if not separators and first_interval_control is None:
            first_interval_control = {
                **record,
                "fixed_pivot_contribution": list(fixed_value),
                "target_pivot_RtBR": list(target_pivot),
            }

    assert outcomes == Counter({"empty": 512, "gram_unsat": 384, "feasible": 128})
    assert len(branch_records) == 128
    # Rebind the historical first witness.
    assert branch_records[0]["choice_indices"] == degree_control["selected_group_choice_indices"]

    summary = Counter(record["small_direction_interval_separated"] for record in branch_records)
    pointwise_summary = Counter(
        record["pointwise_transport_relaxation"]["all_vertices_pass"]
        for record in branch_records
    )
    leverage_branch_summary = Counter(
        bool(record["projector_leverage_violations"])
        for record in branch_records
    )

    # Broaden the discovery beyond the canonical first configuration.  For
    # each of the two feasible fixed-overlap signatures enumerate every
    # exceptional-fibre configuration accepted by the exact Gram CSP, and
    # attach the frozen DP's first ordinary-fibre decomposition for its
    # required Gram residue.  This is still a one-sided sample of all ordinary
    # decompositions, but it can supply an honest countercontrol if the first
    # configuration was atypical.
    primary_direction = (1, -1, -1, 1, 1, 0)
    alternative = Counter()
    first_primary_interval_control = None
    first_alternative_reject = None
    per_signature = []
    target_gram = tuple(4 * structural["K4"][pivot_global[i]][pivot_global[j]]
                        for i, j in UPPER6)
    for signature_index, (fixed_key, choices) in enumerate(
        sorted(feasible_signature_representatives.items())
    ):
        adjacency = defect.mask_adjacency(
            len(geometry.vertices), geometry.pair_positions,
            internal | sum((choice.mask for choice in choices), 0),
        )
        fixed_degrees = defect.fixed_exceptional_degrees(geometry, adjacency, exceptional)
        config_domains = tuple(defect.enumerate_fibre_configurations(
            patterns[support], fixed=fixed_degrees[local]
        ) for local, support in enumerate(exceptional))
        signature_counts = Counter()
        for selected_configs in itertools.product(*config_domains):
            signature_counts["exceptional_products"] += 1
            compatible = True
            for left, right in itertools.combinations(range(len(exceptional)), 2):
                if set(exceptional[left]) & set(exceptional[right]):
                    continue
                left_degrees = selected_configs[left]["degrees_by_exceptional_target"][right]
                right_degrees = selected_configs[right]["degrees_by_exceptional_target"][left]
                if not defect.bipartite_graphical(left_degrees, right_degrees):
                    compatible = False
                    break
            if not compatible:
                signature_counts["disjoint_margin_incompatible"] += 1
                continue
            partial = sum6(config["pivot_gram6"] for config in selected_configs)
            needed = tuple(target_gram[i] - partial[i] for i in range(6))
            if needed not in ordinary_reachable:
                signature_counts["ordinary_gram_residue_missing"] += 1
                continue
            signature_counts["accepted_exceptional_configurations"] += 1
            witness = {
                "exceptional_fibres": [{
                    "support": list(exceptional[source]),
                    "selected_pattern_indices": config["selected_pattern_indices"],
                    "pivot_gram6": list(config["pivot_gram6"]),
                } for source, config in enumerate(selected_configs)],
                "ordinary_needed_pivot_gram6": list(needed),
                "ordinary_fibres": ordinary_reachable[needed],
            }
            degrees, residual = selected_rows(structural, exceptional, compression, witness)
            witness_selected = {
                tuple(row["support"]): tuple(row["selected_pattern_indices"])
                for row in witness["exceptional_fibres"] + witness["ordinary_fibres"]
            }
            leverage_violations = selected_leverage_violations(
                witness_selected, leverage_forbidden
            )
            signature_counts[
                "projector_leverage_rejected" if leverage_violations
                else "projector_leverage_passed"
            ] += 1
            pivot_residual = restrict_residual(residual, pivot_global)
            fixed = fixed_edges(entry, geometry, choices, exceptional)
            fixed_value, option_sets, _meta = contribution_options(
                degrees, pivot_residual, exceptional, fixed
            )
            pointwise = pointwise_transport_relaxation(
                degrees, residual, pivot_residual, fixed, compression,
                structural["K4"], pivot_global, exceptional,
            )
            signature_counts[
                "pointwise_transport_passed" if pointwise["all_vertices_pass"]
                else "pointwise_transport_rejected"
            ] += 1
            target_scalar, lower, upper = one_direction_interval(
                target_pivot, fixed_value, option_sets, primary_direction
            )
            if target_scalar < lower or target_scalar > upper:
                signature_counts["primary_direction_rejected"] += 1
                alternative["primary_direction_rejected"] += 1
                if first_alternative_reject is None:
                    first_alternative_reject = {
                        "signature_index": signature_index,
                        "exceptional_selected_pattern_indices": [
                            config["selected_pattern_indices"] for config in selected_configs
                        ],
                        "ordinary_needed_pivot_gram6": list(needed),
                        "target_after_fixed": target_scalar,
                        "interval": [lower, upper],
                    }
            else:
                signature_counts["primary_direction_passed"] += 1
                alternative["primary_direction_passed"] += 1
                if first_primary_interval_control is None:
                    separators = interval_separators(
                        target_pivot, fixed_value, option_sets, directions
                    )
                    first_primary_interval_control = {
                        "signature_index": signature_index,
                        "exceptional_selected_pattern_indices": [
                            config["selected_pattern_indices"] for config in selected_configs
                        ],
                        "ordinary_needed_pivot_gram6": list(needed),
                        "primary_direction": list(primary_direction),
                        "primary_target_after_fixed": target_scalar,
                        "primary_interval": [lower, upper],
                        "separated_by_any_tested_small_direction": bool(separators),
                        "best_other_separator": None if not separators else {
                            "gap": separators[0][0],
                            "upper6_direction": list(separators[0][1]),
                            "target_after_fixed": separators[0][2],
                            "interval": [separators[0][3], separators[0][4]],
                        },
                    }
        per_signature.append({
            "signature_index": signature_index,
            "representative_choice_indices": [
                domains[group].index(choice) for group, choice in enumerate(choices)
            ],
            "counts": dict(signature_counts),
        })

    # Complete degree-configuration quantification for the primary scalar
    # direction.  The ordinary domains are tiny (product 34,992), so retain
    # every row multiset instead of the one-per-Gram-state witness used by the
    # earlier defect DP.  This remains a relaxation over block maps: each
    # block is independently minimized/maximized, which is safe for rejection.
    exceptional_index = {support: index for index, support in enumerate(exceptional)}
    ordinary_indices = tuple(index for index, support in enumerate(SUPPORTS)
                             if support not in exceptional_index)
    ordinary_domains = {
        source: all_unordered_configs(patterns[SUPPORTS[source]])
        for source in ordinary_indices
    }
    assert math.prod(len(ordinary_domains[source]) for source in ordinary_indices) == 34992
    ordinary_by_gram = {}
    ordinary_product_count = 0
    for selected_tuple in itertools.product(*(ordinary_domains[source]
                                               for source in ordinary_indices)):
        ordinary_product_count += 1
        selected = dict(zip(ordinary_indices, selected_tuple))
        gram = sum6(config["pivot_gram6"] for config in selected_tuple)
        lower = upper = 0
        for source, config in selected.items():
            lo, hi = config_internal_interval(config, primary_direction)
            lower += lo
            upper += hi
        for source, target in itertools.combinations(ordinary_indices, 2):
            if set(SUPPORTS[source]) & set(SUPPORTS[target]):
                continue
            lo, hi = config_block_interval(
                source, selected[source], target, selected[target], compression,
                exceptional_index, primary_direction,
            )
            lower += lo
            upper += hi
        ordinary_by_gram.setdefault(gram, []).append((selected_tuple, lower, upper))

    full_counts = Counter()
    full_per_signature = []
    first_full_countercontrol = None
    first_full_reject = None
    first_canonical_pointwise_control = None
    first_canonical_pointwise_reject = None
    first_exceptional_all_choice_control = None
    first_exceptional_all_choice_reject = None
    first_synchronized_fibre_control = None
    first_synchronized_fibre_reject = None
    first_projector_norm_control = None
    first_projector_norm_reject = None
    complete_configuration_records = []
    total_target_scalar = dot6(primary_direction, target_pivot)
    for signature_index, (fixed_key, representative_choices) in enumerate(
        sorted(feasible_signature_representatives.items())
    ):
        all_choices = feasible_signature_all_choices[fixed_key]
        all_fixed_edge_sets = tuple(
            fixed_edges(entry, geometry, choices, exceptional)
            for choices in all_choices
        )
        adjacency = defect.mask_adjacency(
            len(geometry.vertices), geometry.pair_positions,
            internal | sum((choice.mask for choice in representative_choices), 0),
        )
        fixed_degrees = defect.fixed_exceptional_degrees(geometry, adjacency, exceptional)
        config_domains = tuple(defect.enumerate_fibre_configurations(
            patterns[support], fixed=fixed_degrees[local]
        ) for local, support in enumerate(exceptional))
        sig_counts = Counter()
        for selected_configs_raw in itertools.product(*config_domains):
            sig_counts["exceptional_products"] += 1
            compatible = True
            for left, right in itertools.combinations(range(len(exceptional)), 2):
                if set(exceptional[left]) & set(exceptional[right]):
                    continue
                if not defect.bipartite_graphical(
                    selected_configs_raw[left]["degrees_by_exceptional_target"][right],
                    selected_configs_raw[right]["degrees_by_exceptional_target"][left],
                ):
                    compatible = False
                    break
            if not compatible:
                sig_counts["disjoint_margin_incompatible"] += 1
                continue
            partial = sum6(config["pivot_gram6"] for config in selected_configs_raw)
            needed = tuple(target_gram[i] - partial[i] for i in range(6))
            ordinary_solutions = ordinary_by_gram.get(needed, ())
            if not ordinary_solutions:
                sig_counts["ordinary_gram_residue_missing"] += 1
                continue
            exceptional_configs = {
                SUPPORTS.index(exceptional[local]): config_from_csp(
                    config, patterns[exceptional[local]]
                )
                for local, config in enumerate(selected_configs_raw)
            }
            exceptional_lower = exceptional_upper = 0
            exceptional_indices = tuple(sorted(exceptional_configs))
            for source, target in itertools.combinations(exceptional_indices, 2):
                if set(SUPPORTS[source]) & set(SUPPORTS[target]):
                    continue
                lo, hi = config_block_interval(
                    source, exceptional_configs[source], target,
                    exceptional_configs[target], compression, exceptional_index,
                    primary_direction,
                )
                exceptional_lower += lo
                exceptional_upper += hi

            # Fixed overlap contributions can depend on the actual labelled
            # matching even when the degree signature is the same.
            fixed_histogram = Counter()
            for choices in all_choices:
                fixed = fixed_edges(entry, geometry, choices, exceptional)
                fixed_histogram[fixed_scalar(
                    fixed, exceptional_configs, primary_direction
                )] += 1

            for ordinary_tuple, ordinary_lower, ordinary_upper in ordinary_solutions:
                sig_counts["full_degree_configurations_per_overlap_choice"] += 1
                ordinary_configs = dict(zip(ordinary_indices, ordinary_tuple))

                # One canonical local ordering of every ordinary row multiset,
                # tested against the representative overlap product.  Row
                # permutations are not quantified here, so this is a scout,
                # not a whole-configuration exclusion.
                canonical_witness = {
                    "exceptional_fibres": [{
                        "support": list(exceptional[local]),
                        "selected_pattern_indices": list(config["selected_pattern_indices"]),
                        "pivot_gram6": list(config["pivot_gram6"]),
                    } for local, config in enumerate(selected_configs_raw)],
                    "ordinary_needed_pivot_gram6": list(needed),
                    "ordinary_fibres": [{
                        "support": list(SUPPORTS[source]),
                        "selected_pattern_indices": list(ordinary_configs[source]["selected_pattern_indices"]),
                        "pivot_gram6": list(ordinary_configs[source]["pivot_gram6"]),
                    } for source in ordinary_indices],
                }
                canonical_degrees, canonical_residual = selected_rows(
                    structural, exceptional, compression, canonical_witness
                )
                selected_by_support = {
                    tuple(row["support"]): tuple(row["selected_pattern_indices"])
                    for row in (
                        canonical_witness["exceptional_fibres"]
                        + canonical_witness["ordinary_fibres"]
                    )
                }
                leverage_violations = selected_leverage_violations(
                    selected_by_support, leverage_forbidden
                )
                overlap_multiplicity = len(all_choices)
                sig_counts["projector_leverage_overlap_instances_tested"] += overlap_multiplicity
                full_counts["projector_leverage_overlap_instances_tested"] += overlap_multiplicity
                leverage_key = (
                    "projector_leverage_overlap_instances_rejected"
                    if leverage_violations else
                    "projector_leverage_overlap_instances_passed"
                )
                sig_counts[leverage_key] += overlap_multiplicity
                full_counts[leverage_key] += overlap_multiplicity
                canonical_pivot = restrict_residual(canonical_residual, pivot_global)
                canonical_fixed = fixed_edges(
                    entry, geometry, representative_choices, exceptional
                )
                canonical_pointwise = pointwise_transport_relaxation(
                    canonical_degrees, canonical_residual, canonical_pivot,
                    canonical_fixed, compression, structural["K4"],
                    pivot_global, exceptional,
                )
                pointwise_key = (
                    "canonical_pointwise_passed" if canonical_pointwise["all_vertices_pass"]
                    else "canonical_pointwise_rejected"
                )
                sig_counts[pointwise_key] += 1
                full_counts[pointwise_key] += 1
                canonical_record = {
                    "signature_index": signature_index,
                    "exceptional_selected_pattern_indices": [
                        list(config["selected_pattern_indices"])
                        for config in exceptional_configs.values()
                    ],
                    "ordinary_selected_pattern_indices": [
                        list(config["selected_pattern_indices"])
                        for config in ordinary_tuple
                    ],
                    "failed_vertices": canonical_pointwise["failed_vertices"],
                    "first_diagnostic": canonical_pointwise["diagnostic_records"][3]
                    if len(canonical_pointwise["diagnostic_records"]) > 3
                    else canonical_pointwise["diagnostic_records"][0],
                }
                if canonical_pointwise["all_vertices_pass"]:
                    if first_canonical_pointwise_control is None:
                        first_canonical_pointwise_control = canonical_record
                elif first_canonical_pointwise_reject is None:
                    first_canonical_pointwise_reject = canonical_record

                exceptional_all_choices = exceptional_transport_over_all_choices(
                    canonical_degrees, canonical_residual, canonical_pivot,
                    all_fixed_edge_sets, compression, structural["K4"],
                    pivot_global, exceptional,
                )
                sig_counts["exceptional_transport_overlap_choices_tested"] += (
                    exceptional_all_choices["overlap_choices"]
                )
                sig_counts["exceptional_transport_overlap_choices_rejected"] += (
                    exceptional_all_choices["rejected"]
                )
                sig_counts["exceptional_transport_overlap_choices_passed"] += (
                    exceptional_all_choices["passed"]
                )
                full_counts["exceptional_transport_overlap_choices_tested"] += (
                    exceptional_all_choices["overlap_choices"]
                )
                full_counts["exceptional_transport_overlap_choices_rejected"] += (
                    exceptional_all_choices["rejected"]
                )
                full_counts["exceptional_transport_overlap_choices_passed"] += (
                    exceptional_all_choices["passed"]
                )
                exceptional_record = {
                    "signature_index": signature_index,
                    "exceptional_selected_pattern_indices": [
                        list(config["selected_pattern_indices"])
                        for config in exceptional_configs.values()
                    ],
                    "ordinary_selected_pattern_indices": [
                        list(config["selected_pattern_indices"])
                        for config in ordinary_tuple
                    ],
                    **exceptional_all_choices,
                    "projector_leverage_violations": [
                        {"support": list(support), "pattern_index": index}
                        for support, index in leverage_violations
                    ],
                }
                if exceptional_all_choices["passed"]:
                    if first_exceptional_all_choice_control is None:
                        first_exceptional_all_choice_control = exceptional_record
                elif first_exceptional_all_choice_reject is None:
                    first_exceptional_all_choice_reject = exceptional_record

                projector_candidates = (
                    exceptional_all_choices["passing_choice_indices"]
                    if not leverage_violations else []
                )
                projector_diagnostics = None
                projector_norm = {
                    "candidate_overlap_choices": 0,
                    "rejected": 0,
                    "passed": 0,
                    "passing_choice_indices": [],
                    "first_failure": None,
                }
                projector_norm_without_pair_filter = dict(projector_norm)
                pair_allowed = None
                if projector_candidates:
                    (
                        pair_allowed, projector_edge_weights,
                        projector_edge_targets, valid_fixed, projector_diagnostics,
                    ) = projector_block_domain_relaxation(
                        canonical_degrees, canonical_residual, z, outer_q, outer_d,
                        all_fixed_edge_sets, exceptional,
                    )
                    candidates_after_pair_domains = [
                        index for index in projector_candidates if valid_fixed[index]
                    ]
                    sig_counts["projector_pair_candidate_overlap_choices"] += len(
                        projector_candidates
                    )
                    full_counts["projector_pair_candidate_overlap_choices"] += len(
                        projector_candidates
                    )
                    sig_counts["projector_pair_rejected"] += (
                        len(projector_candidates) - len(candidates_after_pair_domains)
                    )
                    full_counts["projector_pair_rejected"] += (
                        len(projector_candidates) - len(candidates_after_pair_domains)
                    )
                    projector_norm = exceptional_transport_with_projector_norm(
                        canonical_degrees, canonical_residual, canonical_pivot,
                        all_fixed_edge_sets, candidates_after_pair_domains,
                        compression, structural["K4"], pivot_global, exceptional,
                        pair_allowed, projector_edge_weights, projector_edge_targets,
                    )
                    projector_norm_without_pair_filter = (
                        exceptional_transport_with_projector_norm(
                            canonical_degrees, canonical_residual, canonical_pivot,
                            all_fixed_edge_sets, projector_candidates,
                            compression, structural["K4"], pivot_global, exceptional,
                            None, projector_edge_weights, projector_edge_targets,
                        )
                    )
                    for name in ("candidate_overlap_choices", "rejected", "passed"):
                        sig_counts[f"projector_norm_{name}"] += projector_norm[name]
                        full_counts[f"projector_norm_{name}"] += projector_norm[name]
                        sig_counts[f"projector_norm_unfiltered_{name}"] += (
                            projector_norm_without_pair_filter[name]
                        )
                        full_counts[f"projector_norm_unfiltered_{name}"] += (
                            projector_norm_without_pair_filter[name]
                        )
                    projector_norm_record = {
                        "signature_index": signature_index,
                        "exceptional_selected_pattern_indices": [
                            list(config["selected_pattern_indices"])
                            for config in exceptional_configs.values()
                        ],
                        "ordinary_selected_pattern_indices": [
                            list(config["selected_pattern_indices"])
                            for config in ordinary_tuple
                        ],
                        "pair_diagnostics": projector_diagnostics,
                        "without_pair_filter": projector_norm_without_pair_filter,
                        **projector_norm,
                    }
                    if projector_norm["passed"]:
                        if first_projector_norm_control is None:
                            first_projector_norm_control = projector_norm_record
                    elif projector_norm["candidate_overlap_choices"]:
                        if first_projector_norm_reject is None:
                            first_projector_norm_reject = projector_norm_record

                synchronized_candidates = projector_norm["passing_choice_indices"]
                synchronized = exceptional_fibre_synchronized_transport(
                    canonical_degrees, canonical_residual, canonical_pivot,
                    all_fixed_edge_sets, synchronized_candidates,
                    compression, structural["K4"], pivot_global, exceptional,
                    pair_allowed=pair_allowed,
                )
                for name in ("candidate_overlap_choices", "rejected", "passed"):
                    sig_counts[f"synchronized_fibre_{name}"] += synchronized[name]
                    full_counts[f"synchronized_fibre_{name}"] += synchronized[name]
                synchronized_record = {
                    "signature_index": signature_index,
                    "exceptional_selected_pattern_indices": [
                        list(config["selected_pattern_indices"])
                        for config in exceptional_configs.values()
                    ],
                    "ordinary_selected_pattern_indices": [
                        list(config["selected_pattern_indices"])
                        for config in ordinary_tuple
                    ],
                    "projector_pair_diagnostics": projector_diagnostics,
                    "projector_norm": projector_norm,
                    **synchronized,
                }
                complete_configuration_records.append({
                    "signature_index": signature_index,
                    "exceptional_selected_pattern_indices": [
                        list(config["selected_pattern_indices"])
                        for config in exceptional_configs.values()
                    ],
                    "ordinary_selected_pattern_indices": [
                        list(config["selected_pattern_indices"])
                        for config in ordinary_tuple
                    ],
                    "overlap_choices": len(all_choices),
                    "transport_passing_choice_indices": exceptional_all_choices[
                        "passing_choice_indices"
                    ],
                    "projector_leverage_violations": [
                        [list(support), index] for support, index in leverage_violations
                    ],
                    "projector_norm_passing_choice_indices": projector_norm[
                        "passing_choice_indices"
                    ],
                    "projector_norm_unfiltered_passing_choice_indices": (
                        projector_norm_without_pair_filter["passing_choice_indices"]
                    ),
                    "projector_norm_first_failure": projector_norm["first_failure"],
                })
                if synchronized["passed"]:
                    if first_synchronized_fibre_control is None:
                        first_synchronized_fibre_control = synchronized_record
                elif synchronized["candidate_overlap_choices"]:
                    if first_synchronized_fibre_reject is None:
                        first_synchronized_fibre_reject = synchronized_record

                cross_lower = cross_upper = 0
                for source, left_config in exceptional_configs.items():
                    for target, right_config in ordinary_configs.items():
                        if set(SUPPORTS[source]) & set(SUPPORTS[target]):
                            continue
                        lo, hi = config_block_interval(
                            source, left_config, target, right_config, compression,
                            exceptional_index, primary_direction,
                        )
                        cross_lower += lo
                        cross_upper += hi
                free_lower = exceptional_lower + ordinary_lower + cross_lower
                free_upper = exceptional_upper + ordinary_upper + cross_upper
                for fixed_value_scalar, multiplicity in fixed_histogram.items():
                    lower = fixed_value_scalar + free_lower
                    upper = fixed_value_scalar + free_upper
                    full_counts["labelled_overlap_degree_configurations_tested"] += multiplicity
                    sig_counts["labelled_overlap_degree_configurations_tested"] += multiplicity
                    if total_target_scalar < lower or total_target_scalar > upper:
                        full_counts["interval_rejected"] += multiplicity
                        sig_counts["interval_rejected"] += multiplicity
                        if first_full_reject is None:
                            first_full_reject = {
                                "signature_index": signature_index,
                                "fixed_scalar": fixed_value_scalar,
                                "free_interval": [free_lower, free_upper],
                                "total_interval": [lower, upper],
                                "target": total_target_scalar,
                                "overlap_multiplicity": multiplicity,
                                "exceptional_selected_pattern_indices": [
                                    list(config["selected_pattern_indices"])
                                    for config in exceptional_configs.values()
                                ],
                                "ordinary_selected_pattern_indices": [
                                    list(config["selected_pattern_indices"])
                                    for config in ordinary_tuple
                                ],
                            }
                    else:
                        full_counts["interval_passed"] += multiplicity
                        sig_counts["interval_passed"] += multiplicity
                        if first_full_countercontrol is None:
                            first_full_countercontrol = {
                                "signature_index": signature_index,
                                "fixed_scalar": fixed_value_scalar,
                                "free_interval": [free_lower, free_upper],
                                "total_interval": [lower, upper],
                                "target": total_target_scalar,
                                "overlap_multiplicity": multiplicity,
                                "exceptional_selected_pattern_indices": [
                                    list(config["selected_pattern_indices"])
                                    for config in exceptional_configs.values()
                                ],
                                "ordinary_selected_pattern_indices": [
                                    list(config["selected_pattern_indices"])
                                    for config in ordinary_tuple
                                ],
                            }
        full_per_signature.append({
            "signature_index": signature_index,
            "overlap_products": len(all_choices),
            "counts": dict(sig_counts),
        })
    result = {
        "status": "SOURCE724_MULTIBLOCK_TRANSPORT_DISCOVERY_COMPLETE",
        "scope": (
            "Source 724 key (724,1,0) only.  Exact identity plus a census of the "
            "canonical first degree configuration attached to each of the 128 "
            "feasible overlap products; this is not full degree-configuration enumeration."
        ),
        "inputs_sha256": {str(path): sha256(path) for path in
                          (CATALOG, MINING, DEFECT, DEGREE_WITNESS, LEVERAGE)},
        "macro_key": list(key),
        "coverage": int(entry["signature_orbit_labelled_coverage"]),
        "overlap_census": dict(outcomes),
        "transport_theorem": {
            "P": "84x21 fibre incidence, P^T P=4I",
            "C": "P^T B P",
            "R": "4 B P-P C (so R=8W)",
            "rooted_equations": [
                "B^2+B=12I+2J-Q",
                "B^3=13B-12I+18J+2Q+D",
            ],
            "compressed_moments": [
                "G2=P^T B^2 P=48I+32J-P^TQP-C",
                "G3=P^T B^3 P=13C-48I+288J+2P^TQP+P^TDP",
            ],
            "identity": "R^T B R=16G3-4G2*C-4C*G2+C^3",
            "strong_pointwise_identity": "4 B R=P K4-R(C+4I)",
            "strong_identity_derivation": (
                "with U=P/2, A0=U^TBU=C/4 and W=(I-UU^T)BU=R/8, "
                "the off-diagonal block of B^2+B=12I+2J-Q is "
                "(I-UU^T)BW=-W(A0+I), while U^TBW=W^TW=K4/16"
            ),
            "edge_sum_form": (
                "for every symmetric L, <L,R^TBR>=2 sum_{xy in E(B)} "
                "R_x^T L R_y"
            ),
            "pivot_global_fibres": [list(SUPPORTS[index]) for index in pivot_global],
            "target_pivot_upper6": list(target_pivot),
            "tr_B3": 840,
            "residual_triangles": 140,
            "multi_block_nature": (
                "each unresolved 4x4 block contributes one vector chosen from a finite "
                "margin-dependent set; the displayed scalar interval is the exact "
                "Minkowski support interval across all 105 disjoint blocks and all 13 "
                "ordinary internal C4 orientations for the fixed degree configuration"
            ),
        },
        "projector_leverage_theorem": {
            "minus4_fibre_compression": "U^T E_-4 U=Z/28",
            "minus4_standard_coordinate_row": "(Z_G-R_x)/56 for x in fibre G",
            "minus4_diagonal": "5/14",
            "necessary_inequality": (
                "(Z_G-R_x) Z^+ (Z_G-R_x)^T <= 40"
            ),
            "warning": (
                "The cross-block-only expression R_x Z^+ R_x^T<=40 is not valid; "
                "the full standard-coordinate row Z_G-R_x is essential."
            ),
            "forbidden_row_patterns": [
                {
                    "support": list(support),
                    "pattern_index": index,
                    "minus4_leverage": show_fraction(leverage_values[(support, index)][0]),
                    "plus3_leverage": show_fraction(leverage_values[(support, index)][1]),
                }
                for support, index in sorted(leverage_forbidden)
            ],
            "first_degree_configurations_rejected": leverage_branch_summary[True],
            "first_degree_configurations_passed": leverage_branch_summary[False],
        },
        "first_degree_configuration_census": {
            "feasible_overlap_products": len(branch_records),
            "directions_tested": len(directions),
            "separated": summary[True],
            "not_separated": summary[False],
            "pointwise_transport_rejected": pointwise_summary[False],
            "pointwise_transport_passed": pointwise_summary[True],
            "warning": (
                "A separated record excludes that displayed complete fibre-degree "
                "configuration for every compatible block map, not the overlap product: "
                "other Gram-compatible degree configurations may exist."
            ),
        },
        "first_exact_separator": first_separator,
        "first_interval_countercontrol": first_interval_control,
        "alternative_degree_configuration_scout": {
            "method": (
                "all accepted exceptional-fibre configurations, paired with the first "
                "ordinary decomposition retained for each exact Gram residue"
            ),
            "primary_upper6_direction": list(primary_direction),
            "counts": dict(alternative),
            "per_fixed_overlap_signature": per_signature,
            "first_reject": first_alternative_reject,
            "first_primary_interval_countercontrol": first_primary_interval_control,
            "scope_warning": (
                "ordinary_reachable retains one decomposition per Gram residue; this scout "
                "does not quantify over every ordinary-fibre decomposition"
            ),
        },
        "complete_primary_direction_degree_census": {
            "ordinary_unordered_domain_sizes": [
                {"support": list(SUPPORTS[source]), "configurations": len(ordinary_domains[source])}
                for source in ordinary_indices
            ],
            "ordinary_products": ordinary_product_count,
            "ordinary_Gram_residues": len(ordinary_by_gram),
            "counts": dict(full_counts),
            "per_fixed_overlap_signature": full_per_signature,
            "first_reject": first_full_reject,
            "first_countercontrol": first_full_countercontrol,
            "canonical_pointwise_ordering_scout": {
                "rejected": full_counts["canonical_pointwise_rejected"],
                "passed": full_counts["canonical_pointwise_passed"],
                "first_reject": first_canonical_pointwise_reject,
                "first_countercontrol": first_canonical_pointwise_control,
                "warning": (
                    "ordinary row multisets are assigned to the four labelled vertices in "
                    "one sorted order; all distinct permutations would be required for a "
                    "complete degree-configuration exclusion"
                ),
            },
            "exceptional_vertex_all_overlap_choice_census": {
                "tested": full_counts["exceptional_transport_overlap_choices_tested"],
                "rejected": full_counts["exceptional_transport_overlap_choices_rejected"],
                "passed": full_counts["exceptional_transport_overlap_choices_passed"],
                "first_fully_rejected_degree_multiset": first_exceptional_all_choice_reject,
                "first_countercontrol": first_exceptional_all_choice_control,
                "ordinary_permutation_invariance": (
                    "For a fixed exceptional vertex, permuting an ordinary fibre's four "
                    "rows permutes both its residual rows and the corresponding column "
                    "margins.  The enumerated neighbour-sum set is unchanged."
                ),
            },
            "projector_leverage_overlap_census": {
                "tested": full_counts["projector_leverage_overlap_instances_tested"],
                "rejected": full_counts["projector_leverage_overlap_instances_rejected"],
                "passed": full_counts["projector_leverage_overlap_instances_passed"],
                "interpretation": (
                    "A row-pattern violation is independent of the unresolved 4x4 maps, "
                    "so its full overlap multiplicity is soundly removed."
                ),
            },
            "exceptional_fibre_synchronized_transport": {
                "entered_after_pointwise_and_leverage": full_counts[
                    "synchronized_fibre_candidate_overlap_choices"
                ],
                "rejected": full_counts["synchronized_fibre_rejected"],
                "passed": full_counts["synchronized_fibre_passed"],
                "first_reject": first_synchronized_fibre_reject,
                "first_countercontrol": first_synchronized_fibre_control,
                "relaxation_boundary": (
                    "All four source rows share each 4x4 block exactly.  A block shared "
                    "by two different exceptional fibres is still allowed to be chosen "
                    "independently in their two tests; passage is therefore not a graph."
                ),
            },
            "residual_projector_pair_and_row_norm_census": {
                "entered_after_transport_and_leverage": full_counts[
                    "projector_pair_candidate_overlap_choices"
                ],
                "pair_domain_rejected": full_counts["projector_pair_rejected"],
                "row_norm_entered": full_counts[
                    "projector_norm_candidate_overlap_choices"
                ],
                "row_norm_rejected": full_counts["projector_norm_rejected"],
                "row_norm_passed": full_counts["projector_norm_passed"],
                "row_norm_without_pair_filter_entered": full_counts[
                    "projector_norm_unfiltered_candidate_overlap_choices"
                ],
                "row_norm_without_pair_filter_rejected": full_counts[
                    "projector_norm_unfiltered_rejected"
                ],
                "row_norm_without_pair_filter_passed": full_counts[
                    "projector_norm_unfiltered_passed"
                ],
                "first_reject": first_projector_norm_reject,
                "first_countercontrol": first_projector_norm_control,
                "identity": (
                    "For G4=112(E_-4-proj(range(E_-4 U))), G4^2=112G4. "
                    "Writing G4_xy=a_xy-16B_xy makes each diagonal equation "
                    "sum_{y~x}(8-a_xy)=(112g_x-g_x^2-sum a_xy^2)/32."
                ),
                "pair_minor": "(a_xy-16B_xy)^2 <= g_x*g_y",
                "scope": (
                    "Only the 16 overlap/degree instances surviving exceptional-vertex "
                    "transport and leverage enter this refinement."
                ),
            },
            "soundness": (
                "Every ordered exceptional configuration and every ordinary row multiset "
                "with the exact pivot Gram are included.  For each, all labelled overlap "
                "products are included and every unresolved block is relaxed independently "
                "to its exact scalar min/max.  Therefore interval rejection is valid for "
                "all binary block maps."
            ),
            "complete_configuration_records": complete_configuration_records,
            "complete_configuration_records_sha256": hashlib.sha256(
                json.dumps(complete_configuration_records, sort_keys=True).encode()
            ).hexdigest().upper(),
        },
        "branch_records": branch_records,
        "conclusion": (
            "The pointwise transport equation and the corrected projector leverage cap are "
            "exact multi-block necessary conditions.  The finite source-724 censuses record "
            "their exact reduction and retain any countercontrol instead of claiming a "
            "source exclusion beyond what was enumerated."
        ),
    }
    atomic_json(OUTPUT, result)
    print(json.dumps({
        "status": result["status"], "overlap_census": dict(outcomes),
        "transport_interval": dict(summary),
        "pointwise_transport": dict(pointwise_summary),
        "projector_leverage_first_configs": dict(leverage_branch_summary),
        "target_pivot": target_pivot,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
