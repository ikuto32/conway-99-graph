"""An exact averaged E0=0 degree-row control, not a graph construction.

The finite S7 orbit is a symmetrization of one explicit twelve-neighbour
row. It never enumerates a lower-E0 completion layer.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path


OUT = Path("scratch_theory_uniform_e0_zero_degree_moment_control.json")
SUPPORTS = tuple(itertools.combinations(range(7), 2))
SUPPORT_INDEX = {support: index for index, support in enumerate(SUPPORTS)}
BASE_SOURCE = (0, 1)
BASE_NEIGHBORS = (
    (0, 4), (1, 6), (2, 8), (3, 10),
    (4, 6), (5, 7), (8, 10), (9, 11),
    (5, 12), (7, 12), (9, 13), (11, 13),
)


def frac_matrix(matrix):
    return [[str(Fraction(value)) for value in row] for row in matrix]


def main():
    orbit = {}
    base_degree = [0] * 21
    for left, right in BASE_NEIGHBORS:
        base_degree[SUPPORT_INDEX[tuple(sorted((left // 2, right // 2)))]] += 1
    assert sum(base_degree) == 12 and sum(value * value for value in base_degree) == 16
    assert base_degree[SUPPORT_INDEX[BASE_SOURCE]] == 0
    for permutation in itertools.permutations(range(7)):
        source = tuple(sorted(permutation[group] for group in BASE_SOURCE))
        neighbor_labels = tuple(sorted(tuple(sorted((2 * permutation[a // 2] + a % 2,
                                                      2 * permutation[b // 2] + b % 2)))
                                       for a, b in BASE_NEIGHBORS))
        assert len(neighbor_labels) == len(set(neighbor_labels)) == 12
        incidence = Counter(label for pair in neighbor_labels for label in pair)
        assert all(incidence[label] == (1 if label // 2 in source else 2) for label in range(14))
        degree = [0] * 21
        for a, b in neighbor_labels:
            degree[SUPPORT_INDEX[tuple(sorted((a // 2, b // 2)))]] += 1
        key = (SUPPORT_INDEX[source], tuple(degree))
        if key not in orbit:
            orbit[key] = {"multiplicity": 0, "representative_group_permutation": list(permutation),
                          "representative_neighbor_labels": list(map(list, neighbor_labels))}
        orbit[key]["multiplicity"] += 1
    assert len(orbit) == 630
    assert set(row["multiplicity"] for row in orbit.values()) == {8}
    source_histogram = Counter(source for source, degree in orbit)
    assert source_histogram == Counter({source: 30 for source in range(21)})
    mean = [[Fraction(0) for _ in range(21)] for _ in range(21)]
    second = [[Fraction(0) for _ in range(21)] for _ in range(21)]
    records = []
    for (source, degree), record in sorted(orbit.items()):
        weight = Fraction(record["multiplicity"], 60)
        for i in range(21):
            mean[source][i] += weight * degree[i]
            for j in range(21):
                second[i][j] += weight * degree[i] * degree[j]
        records.append({"source_support": list(SUPPORTS[source]), "degree_row": list(degree), **record})
    expected_mean = [[Fraction(0) if i == j else Fraction(8 if set(a) & set(b) else 16, 5)
                      for j, b in enumerate(SUPPORTS)] for i, a in enumerate(SUPPORTS)]
    expected_second = [[48 * int(i == j) + 32 - expected_mean[i][j]
                        - 8 * len(set(a) & set(b)) for j, b in enumerate(SUPPORTS)]
                       for i, a in enumerate(SUPPORTS)]
    assert mean == expected_mean and second == expected_second
    residual_moment_scaled25 = [[0] * 21 for _ in range(21)]
    for (source, degree), record in orbit.items():
        residual5 = [20 * degree[i] - int(5 * mean[source][i]) for i in range(21)]
        assert sum(value * value for value in residual5) == 3200
        assert all(sum(residual5[i] for i, support in enumerate(SUPPORTS) if group in support) == 0
                   for group in range(7))
        for i in range(21):
            for j in range(21):
                residual_moment_scaled25[i][j] += record["multiplicity"] * residual5[i] * residual5[j]
    residual_moment = [[Fraction(value, 1500) for value in row] for row in residual_moment_scaled25]
    mean_square = [[sum(mean[i][k] * mean[k][j] for k in range(21)) for j in range(21)] for i in range(21)]
    expected_residual = [[16 * second[i][j] - 4 * mean_square[i][j] for j in range(21)] for i in range(21)]
    assert residual_moment == expected_residual
    result = {
        "status": "EXACT_UNIFORM_E0_ZERO_AVERAGED_DEGREE_ROW_CONTROL_PASS",
        "scope": {
            "E0": 0, "control_type": "symmetrized marginal integer degree-row distribution",
            "simultaneous_integral_C_or_B_realized": False,
            "pointwise_matrix_moment_equation_for_one_D_claimed": False,
            "lower_E0_completion_layer_enumerated": False,
            "graph_construction_claimed": False,
        },
        "supports": list(map(list, SUPPORTS)),
        "base_source_support": list(BASE_SOURCE), "base_degree_row": base_degree,
        "base_twelve_neighbor_labels": list(map(list, BASE_NEIGHBORS)),
        "group_action": "All5040 permutations of the7 root-neighbour pairs, preserving within-pair bits",
        "group_elements": 5040, "degree_orbit_size": 630,
        "degree_rows_per_source": 30, "degree_orbit_multiplicity": 8,
        "conditional_degree_row_probability": "1/30",
        "four_vertices_per_source_aggregate_row_weight": "2/15",
        "uniform_group_element_aggregate_weight": "1/60",
        "base_row_sum": 12, "base_row_square_sum": 16,
        "base_group_degrees": [2, 2, 4, 4, 4, 4, 4],
        "mean_compression_Cbar": frac_matrix(mean),
        "aggregate_second_moment_Gbar": frac_matrix(second),
        "aggregate_residual_second_moment": frac_matrix(residual_moment),
        "mean_compression_spectrum": [[48, 1], [-8, 6], [0, 14]],
        "second_moment_spectrum": [[576, 1], [16, 6], [48, 14]],
        "mean_K4_spectrum": [[0, 7], [192, 14]],
        "records": records,
        "claim_boundary": (
            "The averaged first and second degree moments, exact per-row integrality, "
            "zero own-fibre degree, and all14 rootlabel quotas allow E0=0. "
            "The compression is fractional. Shared undirected edge variables and "
            "the covariance of a simultaneously integral compression are omitted."
        ),
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUT), "degree_orbit_size": len(orbit),
                      "rows_per_source": 30, "all_second_moment_entries_match": True,
                      "Cbar_trace": str(sum(mean[i][i] for i in range(21)))}, indent=2))


if __name__ == "__main__":
    main()
