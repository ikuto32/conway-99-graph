"""Independent orbit-template and exact matrix audit; no producer imports."""

from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path


CERT = Path("scratch_theory_uniform_e0_zero_degree_moment_control.json")
OUT = Path("scratch_theory_uniform_e0_zero_degree_moment_control_audit.json")
SUPPORTS = tuple(itertools.combinations(range(7), 2))
INDEX = {support: index for index, support in enumerate(SUPPORTS)}


def multiply(a, b):
    columns = tuple(zip(*b))
    return [[sum(x * y for x, y in zip(row, column)) for column in columns] for row in a]


def rational_matrix(values):
    return [[Fraction(value) for value in row] for row in values]


def partial_graph_check(base_source, neighbor_labels):
    labels = tuple((2 * a + i, 2 * b + j) for a, b in SUPPORTS
                   for i, j in itertools.product((0, 1), repeat=2))
    label_index = {frozenset(label): index for index, label in enumerate(labels)}
    source_label = frozenset(2 * group for group in base_source)
    x = 15 + label_index[source_label]
    neighbors = [set() for _ in range(99)]

    def edge(a, b):
        neighbors[a].add(b)
        neighbors[b].add(a)

    for vertex in range(1, 15):
        edge(0, vertex)
    for group in range(7):
        edge(2 * group + 1, 2 * group + 2)
    for index, label in enumerate(labels):
        for root_neighbor in label:
            edge(15 + index, root_neighbor + 1)
    for label in neighbor_labels:
        edge(x, 15 + label_index[frozenset(label)])
    assert all(len(neighbors[vertex]) == 14 for vertex in range(15))
    assert len(neighbors[x]) == 14
    for a, b in itertools.combinations(range(99), 2):
        assert len(neighbors[a] & neighbors[b]) <= (1 if b in neighbors[a] else 2)
    return 99 * 98 // 2


def main():
    cert = json.loads(CERT.read_text(encoding="utf-8"))
    assert cert["supports"] == list(map(list, SUPPORTS))
    base_source = tuple(cert["base_source_support"])
    assert base_source == (0, 1)
    base_neighbors = tuple(map(tuple, cert["base_twelve_neighbor_labels"]))
    base_degree = [0] * 21
    for a, b in base_neighbors:
        assert a // 2 != b // 2
        base_degree[INDEX[tuple(sorted((a // 2, b // 2)))]] += 1
    assert base_degree == cert["base_degree_row"]
    assert Counter(base_degree) == Counter({0: 11, 1: 8, 2: 2})
    checked_partial_pairs = partial_graph_check(base_source, base_neighbors)

    # Independent combinatorial orbit construction: hub + assigned external pair.
    templates = {}
    for source in SUPPORTS:
        external = sorted(set(range(7)) - set(source))
        for hub in external:
            remaining = sorted(set(external) - {hub})
            for first_pair in itertools.combinations(remaining, 2):
                second_pair = tuple(sorted(set(remaining) - set(first_pair)))
                degree = [0] * 21
                for source_group, pair in zip(source, (first_pair, second_pair)):
                    for target_group in pair:
                        degree[INDEX[tuple(sorted((source_group, target_group)))]] = 1
                        degree[INDEX[tuple(sorted((hub, target_group)))]] = 1
                    degree[INDEX[pair]] = 2
                key = (INDEX[source], tuple(degree))
                assert key not in templates
                templates[key] = (hub, first_pair, second_pair)
    assert len(templates) == 21 * 5 * 6 == 630
    assert Fraction(cert["conditional_degree_row_probability"]) == Fraction(1, 30)
    assert Fraction(cert["four_vertices_per_source_aggregate_row_weight"]) == Fraction(2, 15)
    assert Fraction(cert["uniform_group_element_aggregate_weight"]) == Fraction(1, 60)
    assert 630 * Fraction(2, 15) == 84
    emitted = {(INDEX[tuple(row["source_support"])], tuple(row["degree_row"])): row for row in cert["records"]}
    assert len(emitted) == len(cert["records"]) == 630 and set(emitted) == set(templates)

    # Independently count all group images of the base weighted support graph.
    group_histogram = Counter()
    for permutation in itertools.permutations(range(7)):
        source = tuple(sorted((permutation[0], permutation[1])))
        degree = [0] * 21
        for support, value in zip(SUPPORTS, base_degree):
            degree[INDEX[tuple(sorted(permutation[group] for group in support))]] = value
        group_histogram[INDEX[source], tuple(degree)] += 1
    assert set(group_histogram) == set(templates) and set(group_histogram.values()) == {8}
    assert sum(group_histogram.values()) == 5040
    label_realizations = 0
    first_sum = [[0] * 21 for _ in range(21)]
    outer_sum = [[0] * 21 for _ in range(21)]
    for (source_index, degree), row in emitted.items():
        source = SUPPORTS[source_index]
        assert row["multiplicity"] == group_histogram[source_index, degree] == 8
        permutation = row["representative_group_permutation"]
        assert sorted(permutation) == list(range(7))
        assert tuple(sorted((permutation[0], permutation[1]))) == source
        transformed = sorted(tuple(sorted((2 * permutation[a // 2] + a % 2,
                                           2 * permutation[b // 2] + b % 2))) for a, b in base_neighbors)
        assert list(map(list, transformed)) == row["representative_neighbor_labels"]
        for flips in itertools.product((0, 1), repeat=2):
            flip_map = dict(zip(source, flips))
            labels = [tuple(sorted(label ^ flip_map.get(label // 2, 0) for label in pair)) for pair in transformed]
            assert len(labels) == len(set(labels)) == 12
            incidence = Counter(label for pair in labels for label in pair)
            assert all(incidence[label] == (1 if label // 2 in source else 2) for label in range(14))
            observed_degree = [0] * 21
            for a, b in labels:
                observed_degree[INDEX[tuple(sorted((a // 2, b // 2)))]] += 1
            assert observed_degree == list(degree)
            assert observed_degree[source_index] == 0
            label_realizations += 1
        assert sum(degree) == 12 and sum(value * value for value in degree) == 16
        group_totals = [sum(value for support, value in zip(SUPPORTS, degree) if group in support) for group in range(7)]
        assert group_totals == [2 if group in source else 4 for group in range(7)]
        assert sum(value for support, value in zip(SUPPORTS, degree) if len(set(support) & set(source)) == 1) == 4
        assert sum(value for support, value in zip(SUPPORTS, degree) if set(support).isdisjoint(source)) == 8
        for a in range(21):
            first_sum[source_index][a] += degree[a]
            for b in range(21):
                outer_sum[a][b] += degree[a] * degree[b]
    assert label_realizations == 2520
    c = rational_matrix(cert["mean_compression_Cbar"])
    g = rational_matrix(cert["aggregate_second_moment_Gbar"])
    residual = rational_matrix(cert["aggregate_residual_second_moment"])
    assert c == [[Fraction(2 * value, 15) for value in row] for row in first_sum]
    assert g == [[Fraction(2 * value, 15) for value in row] for row in outer_sum]
    identity = [[Fraction(a == b) for b in range(21)] for a in range(21)]
    p0 = [[Fraction(1, 21) for _ in range(21)] for _ in range(21)]
    intersection = [[len(set(a) & set(b)) for b in SUPPORTS] for a in SUPPORTS]
    p6 = [[(intersection[a][b] - 12 * p0[a][b]) / 5 for b in range(21)] for a in range(21)]
    p14 = [[identity[a][b] - p0[a][b] - p6[a][b] for b in range(21)] for a in range(21)]
    projectors = (p0, p6, p14)
    for projector, rank in zip(projectors, (1, 6, 14)):
        assert multiply(projector, projector) == projector
        assert sum(projector[i][i] for i in range(21)) == rank
    for a, b in itertools.combinations(range(3), 2):
        assert multiply(projectors[a], projectors[b]) == [[0] * 21 for _ in range(21)]
    for a in range(21):
        for b in range(21):
            assert c[a][b] == 48 * p0[a][b] - 8 * p6[a][b]
            assert g[a][b] == 576 * p0[a][b] + 16 * p6[a][b] + 48 * p14[a][b]
            assert g[a][b] == 48 * identity[a][b] + 32 - c[a][b] - 8 * intersection[a][b]
            assert residual[a][b] == 768 * p14[a][b]
    c_square = multiply(c, c)
    assert sum(c_square[i][i] for i in range(21)) == 2688
    assert residual == [[16 * g[a][b] - 4 * c_square[a][b] for b in range(21)] for a in range(21)]
    assert all(sum(row) == 48 for row in c) and all(c[i][i] == 0 for i in range(21))
    assert any(value.denominator != 1 for row in c for value in row)
    report = {
        "status": "INDEPENDENT_UNIFORM_E0_ZERO_DEGREE_ROW_CONTROL_AUDIT_PASS",
        "producer_imported": False,
        "certificate_sha256": hashlib.sha256(CERT.read_bytes()).hexdigest(),
        "group_elements_checked": 5040, "independent_hub_pair_templates": 630,
        "conditional_degree_rows_per_source": 30, "orbit_multiplicity": 8,
        "conditional_weight": "1/30", "total_weighted_row_mass": 84,
        "exact_label_realizations_checked_including_four_source_positions": label_realizations,
        "base_one_row_partial_graph_pair_caps_checked": checked_partial_pairs,
        "symmetric_first_moment_entries_checked": 231,
        "symmetric_second_moment_entries_checked": 231,
        "symmetric_residual_moment_entries_checked": 231,
        "compression_projector_multiplicities": [1, 6, 14],
        "trace_Cbar_square": 2688,
        "simultaneous_integral_compression_or_graph_claimed": False,
        "pointwise_E0_lower_bound_claimed": False,
    }
    OUT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
