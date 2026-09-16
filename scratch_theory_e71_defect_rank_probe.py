"""Exact equitability-defect probe for the sharp E0=71 Gram profiles.

This is a one-root, solver-free calculation.  It reconstructs the complete
21-fibre compression C from the overlap macro and its exact full-Gram
completion, then forms

    Z = C0-C,
    K4 = 192 I + 128 J - 4 C - 32 L L^T - C^2
       = 28 Z - Z^2 = 16 W^T W,

where Q=M/2 and W=(I-QQ^T)BQ.  Exact kernels give pointwise linear degree
relations that every binary 84-vertex outer graph must obey.  The script
also measures how much of every diagonal entry of K4 remains after the
smallest possible four-vertex block-degree variance is charged.

The target rows are source 2601 (the arithmetic-sharp rank-three profile)
and source 724 (the Q=2 control).  No full 99-vertex SAT is run.
"""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
import hashlib
import itertools
import json
import math
import os
from pathlib import Path

from scratch_theory_unsigned_kernel_filter import nullspace, rref


CATALOG = Path("scratch_root_e71_q2_gram_fast_expansion_macro_catalog.json")
MINING = Path("scratch_theory_e71_e72_e0_moment_mining.json")
OUTPUT = Path("scratch_theory_e71_defect_rank_probe.json")
ORDER8_BOUNDARY = Path("scratch_root_order8_e0_lower_bound_boundary.json")
SUPPORTS = tuple(itertools.combinations(range(7), 2))
TARGETS = (724, 2601)


def selected_macro(row) -> bool:
    source = int(row["source_row_index"])
    return source == 2601 or (source == 724 and int(row["Q"] if "Q" in row else row["Q_diagonals"]) == 2)


def atomic_json(path: Path, value) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def matmul(left, right):
    return [[sum(left[i][k] * right[k][j] for k in range(len(right)))
             for j in range(len(right[0]))]
            for i in range(len(left))]


def matvec(matrix, vector):
    return [sum(a * b for a, b in zip(row, vector)) for row in matrix]


def transpose(matrix):
    return [list(row) for row in zip(*matrix)]


def rank(matrix) -> int:
    if not matrix:
        return 0
    _reduced, pivots = rref([[Fraction(value) for value in row] for row in matrix])
    return len(pivots)


def column_rank(columns) -> int:
    return rank(transpose(columns)) if columns else 0


def primitive(vector):
    vector = [Fraction(value) for value in vector]
    scale = 1
    for value in vector:
        scale = math.lcm(scale, value.denominator)
    values = [int(value * scale) for value in vector]
    divisor = 0
    for value in values:
        divisor = math.gcd(divisor, abs(value))
    assert divisor
    values = [value // divisor for value in values]
    first = next(value for value in values if value)
    if first < 0:
        values = [-value for value in values]
    return tuple(values)


def macro_key(row):
    return (
        int(row["source_row_index"]),
        int(row["state_orbit_number"]),
        int(row["signature_stabilizer_orbit_number"]),
    )


def build_compression(entry, profile):
    exceptional = tuple(tuple(item["support"]) for item in entry["exceptional_supports"])
    exceptional_index = {support: index for index, support in enumerate(exceptional)}
    deficits = {tuple(item["support"]): int(item["deficit"])
                for item in entry["exceptional_supports"]}
    overlap = {tuple(sorted((int(left), int(right)))): int(value)
               for left, right, value in entry["overlap_block_totals"]}
    disjoint = {tuple(sorted((int(left), int(right)))): int(value)
                for left, right, value in profile["disjoint_D"]}
    C = [[0] * 21 for _ in range(21)]
    C0 = [[0] * 21 for _ in range(21)]
    for left, F in enumerate(SUPPORTS):
        C0[left][left] = 8
        C[left][left] = 2 * (4 - deficits.get(F, 0))
        for right in range(left + 1, 21):
            G = SUPPORTS[right]
            meeting = bool(set(F) & set(G))
            base = 0 if meeting else 4
            C0[left][right] = C0[right][left] = base
            if F in exceptional_index and G in exceptional_index:
                pair = tuple(sorted((exceptional_index[F], exceptional_index[G])))
                value = (overlap if meeting else disjoint)[pair]
            else:
                value = base
            C[left][right] = C[right][left] = value
    assert all(sum(row) == 48 for row in C)
    Z = [[C0[i][j] - C[i][j] for j in range(21)] for i in range(21)]
    return exceptional, exceptional_index, C, C0, Z


def internal_degrees(entry, exceptional):
    vertices = {
        support: tuple((2 * support[0] + a, 2 * support[1] + b)
                       for a, b in itertools.product((0, 1), repeat=2))
        for support in exceptional
    }
    edges = [(tuple(left), tuple(right)) for left, right in entry["internal_edges"]]
    result = {}
    used = set()
    for support in exceptional:
        degree = {vertex: 0 for vertex in vertices[support]}
        vertex_set = set(degree)
        for edge_index, (left, right) in enumerate(edges):
            if left in vertex_set or right in vertex_set:
                assert left in vertex_set and right in vertex_set
                degree[left] += 1
                degree[right] += 1
                used.add(edge_index)
        result[support] = tuple(degree[vertex] for vertex in vertices[support])
    assert len(used) == len(edges)
    return result


def degree_variance(total: int, degrees) -> int:
    assert sum(degrees) == total and len(degrees) == 4
    numerator = sum((4 * value - total) ** 2 for value in degrees)
    assert numerator % 4 == 0
    return numerator // 4


def cross_degree_moments(total: int):
    histogram = Counter()
    witnesses = {}
    for degrees in itertools.product(range(5), repeat=4):
        if sum(degrees) != total:
            continue
        value = degree_variance(total, degrees)
        histogram[value] += 1
        witnesses.setdefault(value, degrees)
    return histogram, witnesses


def polynomial_zero(matrix, roots):
    size = len(matrix)
    result = [[int(i == j) for j in range(size)] for i in range(size)]
    for root in roots:
        factor = [[matrix[i][j] - root * int(i == j) for j in range(size)]
                  for i in range(size)]
        result = matmul(result, factor)
    return all(value == 0 for row in result for value in row)


def independent_rows(matrix, wanted):
    rows = []
    current = 0
    for row in matrix:
        new = rank([*rows, row])
        if new > current:
            rows.append(list(map(Fraction, row)))
            current = new
            if current == wanted:
                return rows
    raise AssertionError("insufficient row rank")


def solve_square(matrix, target):
    size = len(matrix)
    augmented = [list(map(Fraction, matrix[row])) + [Fraction(target[row])]
                 for row in range(size)]
    reduced, pivots = rref(augmented)
    assert pivots[:size] == list(range(size))
    assert all(reduced[row][column] == int(row == column)
               for row in range(size) for column in range(size))
    return [reduced[row][-1] for row in range(size)]


def enumerate_row_patterns(C, K4, exceptional):
    """Enumerate every integer degree row compatible with rank-three W."""
    exceptional_global = [SUPPORTS.index(support) for support in exceptional]
    KE = [[K4[left][right] for right in exceptional_global]
          for left in exceptional_global]
    basis = independent_rows(KE, 3)
    pivots = next(
        columns for columns in itertools.combinations(range(len(exceptional)), 3)
        if rank([[basis[row][column] for column in columns] for row in range(3)]) == 3
    )
    pivot_matrix_transpose = [
        [basis[row][column] for row in range(3)] for column in pivots
    ]
    ordinary_global = [index for index in range(21) if index not in exceptional_global]
    all_rows = []
    for source, G in enumerate(SUPPORTS):
        baseline = [C[source][target] for target in exceptional_global]
        allowed_pivot_values = [
            tuple(4 * degree - baseline[column] for degree in range(5))
            for column in pivots
        ]
        patterns = []
        for pivot_values in itertools.product(*allowed_pivot_values):
            coefficients = solve_square(pivot_matrix_transpose, pivot_values)
            residual = [
                sum(coefficients[row] * basis[row][column] for row in range(3))
                for column in range(len(exceptional))
            ]
            if any(value.denominator != 1 for value in residual):
                continue
            residual = tuple(map(int, residual))
            degrees = []
            valid = True
            for value, total in zip(residual, baseline):
                numerator = value + total
                if numerator % 4:
                    valid = False
                    break
                degree = numerator // 4
                if not 0 <= degree <= 4:
                    valid = False
                    break
                degrees.append(degree)
            if not valid:
                continue
            ordinary_degrees = []
            for target in ordinary_global:
                assert C[source][target] % 4 == 0
                ordinary_degrees.append(C[source][target] // 4)
            if sum(degrees) + sum(ordinary_degrees) != 12:
                continue
            patterns.append({
                "exceptional_degrees": degrees,
                "scaled_W_row_on_exceptional": list(residual),
                "pivot_scaled_W_coordinates": list(pivot_values),
            })
        assert len({tuple(row["exceptional_degrees"]) for row in patterns}) == len(patterns)
        all_rows.append({
            "source_support": list(G),
            "patterns": patterns,
            "pattern_count": len(patterns),
        })
    return {
        "exceptional_basis_rows": [[int(value) for value in row] for row in basis],
        "pivot_exceptional_indices": list(pivots),
        "pivot_supports": [list(exceptional[index]) for index in pivots],
        "by_source_fibre": all_rows,
        "pattern_count_histogram": dict(Counter(
            str(row["pattern_count"]) for row in all_rows
        )),
    }


def rank_three_characteristic(matrix):
    """Return the exact cubic carrying the three nonzero eigenvalues."""
    size = len(matrix)
    square = matmul(matrix, matrix)
    cube = matmul(square, matrix)
    p1 = sum(matrix[i][i] for i in range(size))
    p2 = sum(square[i][i] for i in range(size))
    p3 = sum(cube[i][i] for i in range(size))
    e2 = (p1 * p1 - p2) // 2
    e3 = (p3 - p1 * p2 + e2 * p1) // 3
    assert 2 * e2 == p1 * p1 - p2
    assert 3 * e3 == p3 - p1 * p2 + e2 * p1
    # Since the remaining eigenvalues are zero, A obeys
    # A(A^3-e1 A^2+e2 A-e3 I)=0 exactly.
    fourth = matmul(cube, matrix)
    assert all(
        fourth[i][j] - p1 * cube[i][j] + e2 * square[i][j]
        - e3 * matrix[i][j] == 0
        for i in range(size) for j in range(size)
    )
    integer_roots = []
    for root in range(1, max(2, p1 + 1)):
        if root ** 3 - p1 * root ** 2 + e2 * root - e3 == 0:
            integer_roots.append(root)
    factorization = None
    if integer_roots:
        root = integer_roots[0]
        # Synthetic division by x-root.
        quadratic_b = root - p1
        quadratic_c = e3 // root
        assert root * quadratic_c == e3
        assert quadratic_c - root * quadratic_b == e2
        factorization = {
            "integer_linear_root": root,
            "remaining_quadratic": [1, quadratic_b, quadratic_c],
            "quadratic_discriminant": quadratic_b * quadratic_b - 4 * quadratic_c,
        }
    return {
        "trace": p1,
        "trace_square": p2,
        "trace_cube": p3,
        "nonzero_characteristic_coefficients": [1, -p1, e2, -e3],
        "factorization": factorization,
    }


def novel_exceptional_kernel(K4, exceptional_index):
    indices = tuple(sorted(exceptional_index.values(), key=lambda local: SUPPORTS.index(
        next(support for support, index in exceptional_index.items() if index == local)
    )))
    # Local exceptional order is the catalogue order; retain it in the result.
    indices = tuple(range(len(exceptional_index)))
    global_indices = [SUPPORTS.index(support) for support in exceptional_index]
    KE = [[K4[left][right] for right in global_indices] for left in global_indices]
    kernel = nullspace([[Fraction(value) for value in row] for row in KE])
    incidence_columns = [
        tuple(Fraction(int(group in support)) for support in exceptional_index)
        for group in range(7)
    ]
    span = []
    current = 0
    for column in incidence_columns:
        new = column_rank([*span, column])
        if new > current:
            span.append(column)
            current = new
    incidence_rank = current
    novel = []
    for candidate in kernel:
        new = column_rank([*span, candidate])
        if new == current:
            continue
        assert new == current + 1
        span.append(tuple(candidate))
        current = new
        novel.append(primitive(candidate))
    assert current == len(kernel)
    return KE, incidence_rank, tuple(novel)


def bipartite_graphical(left, right) -> bool:
    """Exact Gale--Ryser test for a 4 by 4 zero-one block."""
    left = sorted(map(int, left), reverse=True)
    right = sorted(map(int, right), reverse=True)
    if any(value < 0 or value > 4 for value in (*left, *right)):
        return False
    if sum(left) != sum(right):
        return False
    return all(sum(left[:k]) <= sum(min(k, value) for value in right)
               for k in range(1, 5))


def mask_adjacency(size, pair_positions, mask):
    adjacency = [0] * size
    for bit, (left, right) in enumerate(pair_positions):
        if (mask >> bit) & 1:
            adjacency[left] |= 1 << right
            adjacency[right] |= 1 << left
    return adjacency


def degree_to_fibre(adjacency, vertex, fibre, fibre_index):
    return sum((adjacency[vertex] >> other) & 1
               for other, target in enumerate(fibre_index) if target == fibre)


def source_row_map(fast):
    preset = fast.PRESETS["e71gram"]
    fast.configure_generic(preset)
    _port, grouped = fast.input_rows(preset)
    return {
        int(source["source_row_index"]): source
        for rows in grouped.values() for source, _count in rows
        if int(source["source_row_index"]) in TARGETS
    }


def exact_signature_domains(fast, geometry, oriented, entry):
    by_group = fast.matching_choices(
        geometry, oriented, entry["state_indices"], {}
    )
    gram = fast.GramSignatureFilter(geometry)
    expected = {
        int(row["group"]): tuple(map(int, row["block_counts"]))
        for row in entry["group_signature_classes"]
    }
    domains = tuple(
        tuple(choice for choice in by_group[group]
              if gram.signature(group, choice) == expected[group])
        for group in range(7)
    )
    assert [len(domain) for domain in domains] == [
        int(row["matching_choice_count"])
        for row in entry["group_signature_classes"]
    ]
    assert math.prod(map(len, domains)) == int(entry["matching_completion_weight_per_state"])
    return domains


def local_novel_relation_census(fast, source, entry, profile, structural_row):
    """Use source2601's novel relation on A,B,C and close the B--C block."""
    if int(entry["source_row_index"]) != 2601:
        return None
    geometry = fast.RowGeometry(source)
    oriented = fast.oriented_assignment(geometry, entry["state_indices"])
    assert fast.internal_mask(geometry, oriented) == int(entry["internal_mask_hex"], 16)
    domains = exact_signature_domains(fast, geometry, oriented, entry)
    exceptional = tuple(tuple(item["support"]) for item in entry["exceptional_supports"])
    relation = structural_row["novel_pointwise_relations"]
    assert len(relation) == 1
    coefficients = tuple(relation[0]["exceptional_coefficients"])
    assert [(exceptional[i], value) for i, value in enumerate(coefficients) if value] == [
        ((0, 2), 2), ((0, 4), 1), ((1, 2), 1)
    ]
    A, Bside, Cside = (exceptional.index(support)
                       for support in ((0, 2), (0, 4), (1, 2)))
    _exceptional, _index, compression, _C0, _Z = build_compression(entry, profile)
    global_B = SUPPORTS.index((0, 4))
    global_C = SUPPORTS.index((1, 2))
    block_total = compression[global_B][global_C]
    means = relation[0]["fibre_means_Bd"]
    internal = fast.internal_mask(geometry, oriented)
    fibre_vertices = [
        tuple(index for index, fibre in enumerate(geometry.fibre_index) if fibre == target)
        for target in range(len(exceptional))
    ]
    counters = Counter()
    required_pairs = Counter()
    first_failure = {}
    first_survivor = None
    for choices in itertools.product(*domains):
        counters["products"] += 1
        mask = internal
        for choice in choices:
            mask |= choice.mask
        adjacency = mask_adjacency(len(geometry.vertices), geometry.pair_positions, mask)

        bad_A = []
        for vertex in fibre_vertices[A]:
            observed = sum(
                coefficients[target] * degree_to_fibre(
                    adjacency, vertex, target, geometry.fibre_index
                )
                for target in range(len(exceptional)) if coefficients[target]
            )
            if observed != means[SUPPORTS.index((0, 2))]:
                bad_A.append((vertex, observed))
        if bad_A:
            counters["fails_pointwise_A"] += 1
            first_failure.setdefault("pointwise_A", {
                "choice_indices": [domains[group].index(choice)
                                   for group, choice in enumerate(choices)],
                "bad_vertices_and_values": [list(item) for item in bad_A],
            })
            continue
        counters["passes_pointwise_A"] += 1

        left_degrees = []
        for vertex in fibre_vertices[Bside]:
            known = (
                2 * degree_to_fibre(adjacency, vertex, A, geometry.fibre_index)
                + degree_to_fibre(adjacency, vertex, Bside, geometry.fibre_index)
            )
            left_degrees.append(means[global_B] - known)
        right_degrees = []
        for vertex in fibre_vertices[Cside]:
            known = (
                2 * degree_to_fibre(adjacency, vertex, A, geometry.fibre_index)
                + degree_to_fibre(adjacency, vertex, Cside, geometry.fibre_index)
            )
            right_degrees.append(means[global_C] - known)
        degree_key = (tuple(left_degrees), tuple(right_degrees))
        required_pairs[degree_key] += 1
        if sum(left_degrees) != block_total or sum(right_degrees) != block_total:
            counters["fails_BC_total"] += 1
            first_failure.setdefault("BC_total", {
                "left_degrees": left_degrees,
                "right_degrees": right_degrees,
                "required_total": block_total,
            })
            continue
        if not bipartite_graphical(left_degrees, right_degrees):
            counters["fails_BC_graphical"] += 1
            first_failure.setdefault("BC_graphical", {
                "left_degrees": left_degrees,
                "right_degrees": right_degrees,
            })
            continue
        counters["passes_closed_ABC_degree_CSP"] += 1
        if first_survivor is None:
            first_survivor = {
                "choice_indices": [domains[group].index(choice)
                                   for group, choice in enumerate(choices)],
                "required_BC_left_degrees": left_degrees,
                "required_BC_right_degrees": right_degrees,
            }
    assert counters["products"] == int(entry["matching_completion_weight_per_state"])
    assert counters["products"] == sum(
        counters[key] for key in (
            "fails_pointwise_A", "fails_BC_total", "fails_BC_graphical",
            "passes_closed_ABC_degree_CSP",
        )
    )
    return {
        "exact_signature_domain_sizes": list(map(len, domains)),
        "counters": dict(counters),
        "required_BC_degree_pair_histogram": [
            {
                "left": list(left),
                "right": list(right),
                "products": count,
                "graphical": bipartite_graphical(left, right),
            }
            for (left, right), count in sorted(required_pairs.items())
        ],
        "first_failures": first_failure,
        "first_survivor": first_survivor,
        "interpretation": (
            "The novel kernel equation is completely local on fibre A={0,2}; "
            "on B={0,4} and C={1,2} it uniquely prescribes both degree sides "
            "of their one disjoint 4x4 binary block."
        ),
    }


def gram6_from_rows(rows):
    return tuple(
        sum(row[left] * row[right] for row in rows)
        for left in range(3) for right in range(left, 3)
    )


def add6(left, right):
    return tuple(a + b for a, b in zip(left, right))


def subtract6(left, right):
    return tuple(a - b for a, b in zip(left, right))


def diagonal_positions6():
    return (0, 3, 5)


def enumerate_fibre_configurations(pattern_row, fixed=None, unordered=False):
    """Four W-row patterns summing to zero within one source fibre."""
    patterns = pattern_row["patterns"]
    if fixed is None:
        candidates = [tuple(range(len(patterns))) for _ in range(4)]
    else:
        assert len(fixed) == 4
        candidates = []
        for vertex in range(4):
            candidates.append(tuple(
                index for index, pattern in enumerate(patterns)
                if all(pattern["exceptional_degrees"][target] == value
                       for target, value in fixed[vertex].items())
            ))
    configurations = {}
    iterator = (itertools.combinations_with_replacement(range(len(patterns)), 4)
                if unordered else itertools.product(*candidates))
    for selected in iterator:
        residuals = [patterns[index]["scaled_W_row_on_exceptional"]
                     for index in selected]
        if any(sum(row[column] for row in residuals) != 0
               for column in range(len(residuals[0]))):
            continue
        pivot_rows = [patterns[index]["pivot_scaled_W_coordinates"]
                      for index in selected]
        gram = gram6_from_rows(pivot_rows)
        degrees_by_target = tuple(
            tuple(patterns[index]["exceptional_degrees"][target]
                  for index in selected)
            for target in range(len(residuals[0]))
        )
        key = (gram, degrees_by_target if not unordered else ())
        configurations.setdefault(key, {
            "selected_pattern_indices": list(selected),
            "pivot_gram6": gram,
            "degrees_by_exceptional_target": degrees_by_target,
        })
    return tuple(configurations.values())


def ordinary_gram_reachable(structural_row, exceptional, target_gram):
    patterns_by_support = {
        tuple(row["source_support"]): row
        for row in structural_row["rank_three_integer_row_patterns"]["by_source_fibre"]
    }
    ordinary = [support for support in SUPPORTS if support not in set(exceptional)]
    reachable = {(0, 0, 0, 0, 0, 0): []}
    audit = []
    diagonal_positions = diagonal_positions6()
    for support in ordinary:
        configs = enumerate_fibre_configurations(
            patterns_by_support[support], unordered=True
        )
        gram_values = {config["pivot_gram6"] for config in configs}
        config_by_gram = {}
        for config in configs:
            config_by_gram.setdefault(config["pivot_gram6"], config)
        next_reachable = {}
        for partial, partial_witness in reachable.items():
            for gram, config in config_by_gram.items():
                combined = add6(partial, gram)
                if all(combined[index] <= target_gram[index]
                       for index in diagonal_positions):
                    next_reachable.setdefault(combined, [
                        *partial_witness,
                        {
                            "support": list(support),
                            "selected_pattern_indices": config[
                                "selected_pattern_indices"
                            ],
                            "pivot_gram6": list(gram),
                        },
                    ])
        assert next_reachable
        audit.append({
            "source_support": list(support),
            "row_patterns": patterns_by_support[support]["pattern_count"],
            "zero_sum_configuration_count": len(configs),
            "distinct_pivot_gram_contributions": len(gram_values),
            "reachable_partial_gram_count": len(next_reachable),
        })
        reachable = next_reachable
    return reachable, audit


def fixed_exceptional_degrees(geometry, adjacency, exceptional):
    fibre_vertices = [
        tuple(index for index, fibre in enumerate(geometry.fibre_index) if fibre == source)
        for source in range(len(exceptional))
    ]
    fixed = []
    for source, G in enumerate(exceptional):
        rows = []
        for vertex in fibre_vertices[source]:
            row = {}
            for target, F in enumerate(exceptional):
                if source == target or set(G) & set(F):
                    row[target] = degree_to_fibre(
                        adjacency, vertex, target, geometry.fibre_index
                    )
            rows.append(row)
        fixed.append(tuple(rows))
    return tuple(fixed)


def exceptional_config_csp(exceptional, domains, ordinary_reachable, target_gram):
    """Select one four-row configuration per exceptional fibre."""
    disjoint_neighbors = {
        source: tuple(target for target in range(len(exceptional))
                      if target != source
                      and not (set(exceptional[source]) & set(exceptional[target])))
        for source in range(len(exceptional))
    }
    order = sorted(range(len(exceptional)),
                   key=lambda source: (len(domains[source]),
                                       -len(disjoint_neighbors[source])))
    selected = {}
    nodes = 0
    ordinary_needed = None
    diagonal_positions = diagonal_positions6()

    def visit(depth, partial):
        nonlocal nodes, ordinary_needed
        nodes += 1
        if depth == len(order):
            needed = subtract6(target_gram, partial)
            if needed in ordinary_reachable:
                ordinary_needed = needed
                return True
            return False
        source = order[depth]
        for config in domains[source]:
            compatible = True
            for other in disjoint_neighbors[source]:
                if other not in selected:
                    continue
                left = config["degrees_by_exceptional_target"][other]
                right = selected[other]["degrees_by_exceptional_target"][source]
                if not bipartite_graphical(left, right):
                    compatible = False
                    break
            if not compatible:
                continue
            combined = add6(partial, config["pivot_gram6"])
            if any(combined[index] > target_gram[index]
                   for index in diagonal_positions):
                continue
            selected[source] = config
            if visit(depth + 1, combined):
                return True
            selected.pop(source)
        return False

    feasible = visit(0, (0, 0, 0, 0, 0, 0))
    witness = None
    if feasible:
        witness = {
            "exceptional_fibres": [{
                "support": list(exceptional[source]),
                "selected_pattern_indices": selected[source]["selected_pattern_indices"],
                "pivot_gram6": list(selected[source]["pivot_gram6"]),
            }
            for source in range(len(exceptional))
            ],
            "ordinary_needed_pivot_gram6": list(ordinary_needed),
            "ordinary_fibres": ordinary_reachable[ordinary_needed],
        }
    return feasible, nodes, witness


def full_rank_three_degree_csp_census(fast, source, entry, profile, structural_row):
    geometry = fast.RowGeometry(source)
    oriented = fast.oriented_assignment(geometry, entry["state_indices"])
    internal = fast.internal_mask(geometry, oriented)
    domains = exact_signature_domains(fast, geometry, oriented, entry)
    exceptional = tuple(tuple(item["support"]) for item in entry["exceptional_supports"])
    pivot_local = structural_row["rank_three_integer_row_patterns"][
        "pivot_exceptional_indices"
    ]
    pivot_global = [SUPPORTS.index(exceptional[index]) for index in pivot_local]
    K4 = structural_row["K4"]
    target_gram = tuple(
        4 * K4[pivot_global[left]][pivot_global[right]]
        for left in range(3) for right in range(left, 3)
    )
    ordinary_reachable, ordinary_audit = ordinary_gram_reachable(
        structural_row, exceptional, target_gram
    )
    patterns_by_support = {
        tuple(row["source_support"]): row
        for row in structural_row["rank_three_integer_row_patterns"]["by_source_fibre"]
    }
    signature_cache = {}
    counters = Counter()
    first = {}
    domain_histograms = [Counter() for _ in exceptional]
    for choices in itertools.product(*domains):
        counters["overlap_products"] += 1
        mask = internal
        for choice in choices:
            mask |= choice.mask
        adjacency = mask_adjacency(len(geometry.vertices), geometry.pair_positions, mask)
        fixed = fixed_exceptional_degrees(geometry, adjacency, exceptional)
        fixed_key = tuple(
            tuple(tuple(sorted(row.items())) for row in fibre_rows)
            for fibre_rows in fixed
        )
        if fixed_key not in signature_cache:
            config_domains = tuple(
                enumerate_fibre_configurations(
                    patterns_by_support[support], fixed=fixed[local]
                )
                for local, support in enumerate(exceptional)
            )
            for local, values in enumerate(config_domains):
                domain_histograms[local][len(values)] += 1
            if any(not values for values in config_domains):
                outcome = (False, 0, None, "empty_fibre_configuration_domain")
            else:
                feasible, nodes, witness = exceptional_config_csp(
                    exceptional, config_domains, ordinary_reachable, target_gram
                )
                outcome = (feasible, nodes, witness,
                           "feasible" if feasible else "global_gram_or_graphical_unsat")
            signature_cache[fixed_key] = outcome
        feasible, nodes, witness, reason = signature_cache[fixed_key]
        counters[reason] += 1
        counters["csp_nodes_over_distinct_signatures"] += (
            nodes if counters[reason] and fixed_key in signature_cache else 0
        )
        if reason not in first:
            first[reason] = {
                "choice_indices": [domains[group].index(choice)
                                   for group, choice in enumerate(choices)],
                "csp_nodes": nodes,
                "witness": witness,
            }
    # Recompute node total without multiplying cached signatures by products.
    node_total = sum(value[1] for value in signature_cache.values())
    counters["csp_nodes_over_distinct_signatures"] = node_total
    return {
        "target_pivot_gram6_for_scaled_rows": list(target_gram),
        "ordinary_fibres": len(SUPPORTS) - len(exceptional),
        "ordinary_final_reachable_gram_count": len(ordinary_reachable),
        "ordinary_DP_audit": ordinary_audit,
        "distinct_fixed_overlap_degree_signatures": len(signature_cache),
        "exceptional_configuration_domain_size_histograms": [
            {
                "support": list(exceptional[local]),
                "histogram_over_distinct_signatures": dict(sorted(hist.items())),
            }
            for local, hist in enumerate(domain_histograms)
        ],
        "counters": dict(counters),
        "first_by_outcome": first,
        "claim": (
            "Exact existence CSP for 84-vertex fibre-to-fibre degree rows: "
            "all rows lie in im(W^T), every fibre sums to its C row, the full "
            "rank-three defect Gram is met, fixed internal/overlap degrees are "
            "respected, and every unresolved exceptional disjoint block has "
            "graphical 4x4 binary degree sequences."
        ),
    }


def overlap_degree_sequence(geometry, choice, source_fibre, target_fibre):
    adjacency = mask_adjacency(
        len(geometry.vertices), geometry.pair_positions, choice.mask
    )
    vertices = tuple(index for index, fibre in enumerate(geometry.fibre_index)
                     if fibre == source_fibre)
    return tuple(degree_to_fibre(
        adjacency, vertex, target_fibre, geometry.fibre_index
    ) for vertex in vertices)


def source2601_short_kernel_certificate(fast, source, entry, profile, structural_row):
    if int(entry["source_row_index"]) != 2601:
        return None
    geometry = fast.RowGeometry(source)
    oriented = fast.oriented_assignment(geometry, entry["state_indices"])
    domains = exact_signature_domains(fast, geometry, oriented, entry)
    exceptional = tuple(tuple(item["support"]) for item in entry["exceptional_supports"])
    A, D = (exceptional.index(support) for support in ((0, 2), (1, 4)))
    Bside, Cside = (exceptional.index(support) for support in ((0, 4), (1, 2)))
    global_A, global_D = (SUPPORTS.index(support) for support in ((0, 2), (1, 4)))
    kernel_vector = [0] * 21
    kernel_vector[global_A] = 1
    kernel_vector[global_D] = -1
    K4 = structural_row["K4"]
    assert all(value == 0 for value in matvec(K4, kernel_vector))
    _exceptional, _index, compression, _C0, _Z = build_compression(entry, profile)

    contradictions = []
    for source_local in (Bside, Cside):
        G = exceptional[source_local]
        assert compression[SUPPORTS.index(G)][global_A] == 2
        assert compression[SUPPORTS.index(G)][global_D] == 2
        target_rows = []
        for target_local in (A, D):
            target = exceptional[target_local]
            common = set(G) & set(target)
            assert len(common) == 1
            group = next(iter(common))
            sequences = {
                overlap_degree_sequence(
                    geometry, choice, source_local, target_local
                )
                for choice in domains[group]
            }
            # Signature choices change partners, never the set of port stubs.
            assert len(sequences) == 1
            target_rows.append({
                "target_support": list(target),
                "shared_group": group,
                "degree_sequence_for_every_group_choice": list(next(iter(sequences))),
                "group_choice_count": len(domains[group]),
            })
        left = tuple(target_rows[0]["degree_sequence_for_every_group_choice"])
        right = tuple(target_rows[1]["degree_sequence_for_every_group_choice"])
        assert left != right
        contradictions.append({
            "source_support": list(G),
            "equal_block_totals": 2,
            "kernel_forces_pointwise": "deg(x,{0,2})=deg(x,{1,4})",
            "port_incidence": target_rows,
            "mismatching_vertex_count": sum(a != b for a, b in zip(left, right)),
            "contradiction": True,
        })
    return {
        "kernel_vector_by_support": [
            {"support": list(SUPPORTS[index]), "coefficient": value}
            for index, value in enumerate(kernel_vector) if value
        ],
        "K4_times_kernel_vector_is_zero": True,
        "pointwise_formula": (
            "4*(deg(x,A)-deg(x,D))=C[G,A]-C[G,D]; "
            "for G in {B,C}, both totals are 2, so the degrees must agree"
        ),
        "contradictory_source_fibres": contradictions,
        "all_overlap_products_excluded_without_enumerating_partners": int(
            entry["matching_completion_weight_per_state"]
        ),
        "labelled_macro_coverage_excluded": int(entry["signature_orbit_labelled_coverage"]),
        "status": "EXACT_POINTWISE_KERNEL_PORT_CONTRADICTION",
    }


def analyze(entry, profile):
    exceptional, exceptional_index, C, C0, Z = build_compression(entry, profile)
    incidence = [[int(group in support) for group in range(7)] for support in SUPPORTS]
    LLt = matmul(incidence, transpose(incidence))
    C2 = matmul(C, C)
    Z2 = matmul(Z, Z)
    K4 = [[192 * int(i == j) + 128 - 4 * C[i][j] - 32 * LLt[i][j] - C2[i][j]
           for j in range(21)] for i in range(21)]
    assert K4 == [[28 * Z[i][j] - Z2[i][j] for j in range(21)] for i in range(21)]
    assert rank(Z) == rank(K4) == 3
    z_characteristic = rank_three_characteristic(Z)
    k4_characteristic = rank_three_characteristic(K4)

    KE, incidence_rank, novel = novel_exceptional_kernel(K4, exceptional_index)
    row_patterns = enumerate_row_patterns(C, K4, exceptional)
    global_exceptional = [SUPPORTS.index(support) for support in exceptional]
    novel_rows = []
    for vector in novel:
        extended = [0] * 21
        for local, global_index in enumerate(global_exceptional):
            extended[global_index] = vector[local]
        rhs = matvec(C, extended)
        assert all(value % 4 == 0 for value in rhs)
        novel_rows.append({
            "exceptional_coefficients": list(vector),
            "coefficients_by_support": [
                {"support": list(support), "coefficient": value}
                for support, value in zip(exceptional, vector) if value
            ],
            "fibre_means_Bd": [value // 4 for value in rhs],
        })

    internal = internal_degrees(entry, exceptional)
    column_slacks = []
    for target, F in enumerate(SUPPORTS):
        contributions = []
        for source, G in enumerate(SUPPORTS):
            total = C[source][target]
            if source == target:
                if F in internal:
                    degrees = internal[F]
                else:
                    degrees = (2, 2, 2, 2)
                value = degree_variance(total, degrees)
                kind = "internal-fixed"
            else:
                histogram, witnesses = cross_degree_moments(total)
                value = min(histogram)
                degrees = witnesses[value]
                kind = "cross-minimum"
            contributions.append({
                "source_support": list(G),
                "block_total": total,
                "minimum_or_fixed_contribution": value,
                "witness_degrees": list(degrees),
                "kind": kind,
            })
        lower = sum(item["minimum_or_fixed_contribution"] for item in contributions)
        diagonal = K4[target][target]
        assert diagonal >= lower
        column_slacks.append({
            "target_support": list(F),
            "K4_diagonal": diagonal,
            "blockwise_variance_lower_bound": lower,
            "slack": diagonal - lower,
            "zero_slack_forces_every_cross_block_balanced": diagonal == lower,
            "positive_contributions": [item for item in contributions
                                       if item["minimum_or_fixed_contribution"]],
        })

    return {
        "key": list(macro_key(entry)),
        "Q": int(entry["Q"]),
        "coverage": int(entry["signature_orbit_labelled_coverage"]),
        "exceptional_supports": [list(support) for support in exceptional],
        "deficits": [int(item["deficit"]) for item in entry["exceptional_supports"]],
        "internal_degrees": [
            {"support": list(support), "degrees": list(internal[support])}
            for support in exceptional
        ],
        "Z_rank": rank(Z),
        "Z_nonzero_characteristic": z_characteristic,
        "K4_rank": rank(K4),
        "K4_nonzero_characteristic": k4_characteristic,
        "identity_K4_equals_28Z_minus_Z2": True,
        "exceptional_K4_kernel_dimension": len(exceptional) - rank(KE),
        "restricted_unsigned_incidence_rank": incidence_rank,
        "novel_exceptional_kernel_dimension": len(novel),
        "novel_pointwise_relations": novel_rows,
        "rank_three_integer_row_patterns": row_patterns,
        "column_variance_slacks": column_slacks,
        "zero_slack_column_count": sum(row["slack"] == 0 for row in column_slacks),
        "total_diagonal_slack": sum(row["slack"] for row in column_slacks),
        "K4": K4,
        "Z": Z,
    }


def main():
    import scratch_general_e72_q3_fast_expansion as fast

    catalog_raw = CATALOG.read_bytes()
    mining_raw = MINING.read_bytes()
    order8_boundary_raw = ORDER8_BOUNDARY.read_bytes()
    catalog = json.loads(catalog_raw)
    mining = json.loads(mining_raw)
    order8_boundary = json.loads(order8_boundary_raw)
    assert order8_boundary["status"] == "ORDER8_E0_POSITIVE_LOWER_BOUND_BOUNDARY_PASS"
    entries = {
        macro_key(entry): entry
        for entry in catalog["macro_entries"]
        if entry["signature_stabilizer_canonical"]
        and selected_macro(entry)
    }
    profiles = {
        macro_key(row): row
        for row in mining["profile_rows"]["71"]
        if selected_macro(row)
    }
    assert entries.keys() == profiles.keys()
    sources = source_row_map(fast)
    assert set(sources) == set(TARGETS)
    rows = []
    for key in sorted(entries):
        row = analyze(entries[key], profiles[key])
        row["local_novel_relation_census"] = local_novel_relation_census(
            fast, sources[key[0]], entries[key], profiles[key], row
        )
        row["full_rank_three_degree_CSP_census"] = full_rank_three_degree_csp_census(
            fast, sources[key[0]], entries[key], profiles[key], row
        )
        row["source2601_short_kernel_certificate"] = source2601_short_kernel_certificate(
            fast, sources[key[0]], entries[key], profiles[key], row
        )
        rows.append(row)
    result = {
        "status": "EXACT_E71_DEFECT_RANK_STRUCTURAL_PROBE_COMPLETE",
        "inputs": {
            str(CATALOG): hashlib.sha256(catalog_raw).hexdigest().upper(),
            str(MINING): hashlib.sha256(mining_raw).hexdigest().upper(),
            str(ORDER8_BOUNDARY): hashlib.sha256(order8_boundary_raw).hexdigest().upper(),
        },
        "formulae": {
            "Q": "M/2",
            "W": "(I-Q*Q^T)*B*Q",
            "K4": "16*W^T*W=192I+128J-4C-32LL^T-C^2=28Z-Z^2",
            "scaled_row": "8*W[x,F]=4*deg(x,F)-C[G,F] for x in fibre G",
            "kernel_consequence": "c in ker(K4) => sum_F c_F deg(x,F)=(C*c)_G/4 pointwise",
        },
        "rows": rows,
        "summary": {
            "macros": len(rows),
            "source_histogram": dict(Counter(str(row["key"][0]) for row in rows)),
            "novel_dimension_histogram": dict(Counter(
                str(row["novel_exceptional_kernel_dimension"]) for row in rows
            )),
            "Z_characteristic_histogram": dict(Counter(
                ",".join(map(str, row["Z_nonzero_characteristic"][
                    "nonzero_characteristic_coefficients"
                ])) for row in rows
            )),
            "source2601_overlap_products": sum(
                row["local_novel_relation_census"]["counters"]["products"]
                for row in rows if row["local_novel_relation_census"] is not None
            ),
            "source2601_closed_ABC_degree_CSP_survivors": sum(
                row["local_novel_relation_census"]["counters"][
                    "passes_closed_ABC_degree_CSP"
                ] for row in rows if row["local_novel_relation_census"] is not None
            ),
            "full_rank_three_degree_CSP_feasible_overlap_products": sum(
                row["full_rank_three_degree_CSP_census"]["counters"].get(
                    "feasible", 0
                ) for row in rows
            ),
            "full_rank_three_degree_CSP_total_overlap_products": sum(
                row["full_rank_three_degree_CSP_census"]["counters"][
                    "overlap_products"
                ] for row in rows
            ),
            "source2601_short_certificate_excluded_coverage": sum(
                row["source2601_short_kernel_certificate"][
                    "labelled_macro_coverage_excluded"
                ] for row in rows
                if row["source2601_short_kernel_certificate"] is not None
            ),
        },
        "order8_coefficient_matrix_index_audit": {
            "verified_resource_counts": order8_boundary["verified_resource_counts"],
            "exact_pseudowitness_sum_E0": order8_boundary[
                "exact_rational_pseudowitness"
            ]["sum_E0_from_affine_formula"],
            "conclusion": (
                "No positive E0 lower bound, including the source2601 defect "
                "certificate, can be a conic consequence of the existing "
                "pair-root order-8 coefficient matrices and marked rows alone. "
                "The short certificate simultaneously compares four root groups "
                "and belongs to the root-conditioned/full-four-root compatibility "
                "lane, not to a single one of the 2414 class matrices."
            ),
            "full_four_root_blocks_remain_candidate": True,
        },
        "claim_boundary": (
            "Exact necessary 84-vertex degree relations and block-variance bounds; "
            "this structural pass alone does not assert realization or exclusion."
        ),
    }
    atomic_json(OUTPUT, result)
    print(json.dumps({"path": str(OUTPUT), **result["summary"]}, sort_keys=True))


if __name__ == "__main__":
    main()
