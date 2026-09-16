"""Small projected certificate for the rejected source-150 Gram profile.

Finds the lexicographically first smallest subset of the 24 fibre-summed
recurrence coordinates whose exact finite Minkowski sum already excludes the
H=[[4,-1,0],[-1,2,-1],[0,-1,2]] target.  This turns the broad tuple-DP
rejection into a compact independently checkable finite table.
"""

from __future__ import annotations

import itertools
import json
from fractions import Fraction

import scratch_theory_e72_source150_fibre_recurrence_filter as recurrence
import scratch_theory_e72_source150_norm_collision_filter as base


H = (
    (Fraction(4), Fraction(-1), Fraction(0)),
    (Fraction(-1), Fraction(2), Fraction(-1)),
    (Fraction(0), Fraction(-1), Fraction(2)),
)
TARGET = (
    144, -24, 36, -156, 36, -24, 36, -36, 24, -24, 24, -36,
    -144, 24, -36, 156, -36, 24, -36, 36, -24, 24, -24, 36,
)
OUTPUT = "scratch_theory_e72_source150_recurrence_certificate.json"


def projected_sum_rows(rows, coordinates):
    states = {(0,) * len(coordinates)}
    history = [1]
    for options in rows:
        projected = {
            tuple(option[index] for index in coordinates)
            for option in options
        }
        states = {
            tuple(left + right for left, right in zip(state, option))
            for state in states for option in projected
        }
        history.append(len(states))
    target = tuple(TARGET[index] for index in coordinates)
    return target in states, states, history


def exact_number(value):
    value = Fraction(value)
    return int(value) if value.denominator == 1 else str(value)


def main():
    exceptional = (
        (0, 2), (0, 3), (0, 4), (0, 5),
        (1, 2), (1, 3), (1, 4), (1, 5),
    )
    ordinary = tuple(item for item in base.ALL_SUPPORTS
                     if item not in exceptional)
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
    ordinary_patterns = {
        support: base.local_vertex_patterns(support, exceptional, ordinary)
        for support in ordinary
    }
    rows = tuple(
        recurrence.ordinary_load_options(
            ordinary_patterns[support][0],
            ordinary_patterns[support][1], vectors, H
        )
        for support in ordinary
    )

    certificate = None
    tested = 0
    for size in range(1, 5):
        for coordinates in itertools.combinations(range(24), size):
            tested += 1
            feasible, states, history = projected_sum_rows(rows, coordinates)
            if not feasible:
                target = tuple(TARGET[index] for index in coordinates)
                # Retain the attainable values nearest to the missing target
                # in L1 distance as a human-readable certificate.
                nearest = sorted(
                    states,
                    key=lambda state: (
                        sum(abs(left - right)
                            for left, right in zip(state, target)), state
                    ),
                )[:50]
                conditional_values = []
                if size == 3:
                    conditional_values = sorted({
                        state[2] for state in states
                        if state[:2] == target[:2]
                    })
                certificate = {
                    "minimum_coordinate_count": size,
                    "coordinates": list(coordinates),
                    "coordinate_labels": [
                        {"exceptional_fibre_index": index // 3,
                         "Gram_covector_coordinate": index % 3}
                        for index in coordinates
                    ],
                    "target": [exact_number(value) for value in target],
                    "attainable_state_count": len(states),
                    "state_count_after_each_of_13_fibres": history,
                    "nearest_attainable_values": [
                        [exact_number(value) for value in state]
                        for state in nearest
                    ],
                    "third_values_when_first_two_equal_target": [
                        exact_number(value) for value in conditional_values
                    ],
                    "projected_options_by_ordinary_support": [
                        {
                            "support": list(support),
                            "options": [
                                [exact_number(value) for value in option]
                                for option in sorted({
                                    tuple(row[index] for index in coordinates)
                                    for row in rows[support_index]
                                })
                            ],
                        }
                        for support_index, support in enumerate(ordinary)
                    ],
                }
                break
        if certificate is not None:
            break
    assert certificate is not None

    result = {
        "status": "EXACT_PROJECTED_RECURRENCE_CERTIFICATE_COMPLETE",
        "Gram_H": [[int(value) for value in row] for row in H],
        "full_target": list(TARGET),
        "ordinary_support_order": [list(value) for value in ordinary],
        "option_counts": [len(value) for value in rows],
        "subsets_tested_through_first_minimal_failure": tested,
        "certificate": certificate,
        "checks": {
            "all_smaller_coordinate_subsets_feasible": True,
            "all_13_ordinary_fibre_options_enumerated": True,
            "SAT_or_SMT_used": False,
        },
    }
    with open(OUTPUT + ".tmp", "w", encoding="utf-8") as handle:
        json.dump(result, handle, separators=(",", ":"))
        handle.write("\n")
    import os
    os.replace(OUTPUT + ".tmp", OUTPUT)
    print(json.dumps({
        "status": result["status"],
        **certificate,
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
