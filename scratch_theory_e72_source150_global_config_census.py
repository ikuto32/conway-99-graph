"""Exact global ordinary-configuration frontier for source 150.

The fibre-summed recurrence filter retained four Gram target types.  This
script keeps the identity of each of the 1/3/11 ordinary C4 configurations
and counts every common choice across all thirteen ordinary fibres that
meets all eight summed recurrence rows.  These small frontiers are intended
for the subsequent pointwise recurrence CSP.  No SAT/SMT package is used.
"""

from __future__ import annotations

import itertools
import json
import os
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

import scratch_theory_e72_source150_fibre_recurrence_filter as recurrence
import scratch_theory_e72_source150_norm_collision_filter as base
import scratch_theory_e72_source150_pointwise_recurrence_csp as pointwise


GRAM = base.GRAM
FIBRE_RESULT = pointwise.FIBRE_FILTER
OUTPUT = Path("scratch_theory_e72_source150_global_config_census.json")
MACROS = ((0, 0), (0, 1), (0, 3), (8, 0))


def scale(value, vector):
    return tuple(value * coordinate for coordinate in vector)


def configuration_load(configuration, vectors, H):
    loads = [[Fraction(0), Fraction(0), Fraction(0)] for _ in vectors]
    for pattern in configuration:
        q = base.add_vectors(scale(pattern[fibre], vectors[fibre])
                             for fibre in range(len(vectors)))
        for fibre, degree in enumerate(pattern):
            for coordinate in range(3):
                loads[fibre][coordinate] += degree * q[coordinate]
    return recurrence.flatten_covectors(tuple(map(tuple, loads)), H)


def exact_frontier(option_rows, target):
    dimension = len(target)
    suffix_min = [[Fraction(0)] * dimension
                  for _ in range(len(option_rows) + 1)]
    suffix_max = [[Fraction(0)] * dimension
                  for _ in range(len(option_rows) + 1)]
    for index in range(len(option_rows) - 1, -1, -1):
        for coordinate in range(dimension):
            values = [load[coordinate] for _, load in option_rows[index]]
            suffix_min[index][coordinate] = (
                min(values) + suffix_min[index + 1][coordinate]
            )
            suffix_max[index][coordinate] = (
                max(values) + suffix_max[index + 1][coordinate]
            )

    layers = [{(Fraction(0),) * dimension: 1}]
    transition_counts = []
    for index, options in enumerate(option_rows):
        following = defaultdict(int)
        transitions = 0
        for state, multiplicity in layers[-1].items():
            for _, option in options:
                value = tuple(left + right for left, right
                              in zip(state, option))
                if all(
                    value[coordinate] + suffix_min[index + 1][coordinate]
                    <= target[coordinate]
                    <= value[coordinate] + suffix_max[index + 1][coordinate]
                    for coordinate in range(dimension)
                ):
                    following[value] += multiplicity
                    transitions += 1
        layers.append(dict(following))
        transition_counts.append(transitions)
    count = layers[-1].get(target, 0)

    # Backward projection: retain exactly the config indices participating
    # in some complete path, without listing exponentially duplicate paths.
    viable_states = {target}
    allowed_indices = [set() for _ in option_rows]
    viable_state_counts = [0] * (len(option_rows) + 1)
    viable_state_counts[-1] = 1
    for index in range(len(option_rows) - 1, -1, -1):
        preceding = set()
        for state in viable_states:
            for config_index, option in option_rows[index]:
                previous = tuple(left - right for left, right
                                 in zip(state, option))
                if previous in layers[index]:
                    preceding.add(previous)
                    allowed_indices[index].add(config_index)
        viable_states = preceding
        viable_state_counts[index] = len(viable_states)
    assert (count == 0) == (not viable_states)
    paths = [(target, ())]
    for index in range(len(option_rows) - 1, -1, -1):
        preceding_paths = []
        for state, reverse_path in paths:
            for config_index, option in option_rows[index]:
                previous = tuple(left - right for left, right
                                 in zip(state, option))
                if previous in layers[index]:
                    preceding_paths.append((
                        previous, reverse_path + (config_index,)
                    ))
        paths = preceding_paths
    solutions = [list(reversed(reverse_path))
                 for state, reverse_path in paths
                 if state == (Fraction(0),) * len(target)]
    assert len(solutions) == count
    return {
        "solution_path_count": count,
        "forward_state_counts": [len(layer) for layer in layers],
        "forward_transition_counts": transition_counts,
        "backward_viable_state_counts": viable_state_counts,
        "allowed_config_indices_by_fibre": [sorted(row)
                                             for row in allowed_indices],
        "configuration_index_solutions": solutions,
    }


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
    ordinary_data = {
        support: base.local_vertex_patterns(support, exceptional, ordinary)
        for support in ordinary
    }
    configurations = {
        support: pointwise.ordinary_configurations(
            ordinary_data[support][0], ordinary_data[support][1]
        )
        for support in ordinary
    }

    gram_document = json.loads(GRAM.read_text(encoding="utf-8"))
    H_by_macro = {}
    for macro in MACROS:
        rows = [entry for entry in gram_document["rows"]
                if entry["source_row_index"] == 150
                and (entry["state_orbit_number"],
                     entry["signature_stabilizer_orbit_number"]) == macro
                and entry["signature_stabilizer_canonical"]]
        assert len(rows) == 1
        H_by_macro[macro] = tuple(tuple(Fraction(value) for value in row)
                                  for row in rows[0]["unique_H"])

    fibre_document = json.loads(FIBRE_RESULT.read_text(encoding="utf-8"))
    target_by_macro = {}
    for key in fibre_document["distinct_target_histogram"]:
        macro_text, target_text = key.split(";target=")
        macro = tuple(map(int, macro_text.removeprefix("macro=").split(":")))
        if macro in MACROS:
            target_by_macro[macro] = tuple(Fraction(value)
                                           for value in target_text.split(","))
    assert set(target_by_macro) == set(MACROS)

    results = []
    for macro in MACROS:
        H = H_by_macro[macro]
        option_rows = []
        configuration_rows = []
        for support in ordinary:
            configs = configurations[support]
            loads = [(index, configuration_load(config, vectors, H))
                     for index, config in enumerate(configs)]
            option_rows.append(tuple(loads))
            configuration_rows.append([
                [[int(value) for value in pattern] for pattern in config]
                for config in configs
            ])
        frontier = exact_frontier(tuple(option_rows), target_by_macro[macro])
        results.append({
            "macro": list(macro),
            "Gram_H": [[int(value) for value in row] for row in H],
            "target": [int(value) for value in target_by_macro[macro]],
            "ordinary_support_order": [list(value) for value in ordinary],
            "configuration_counts": [len(value) for value in configuration_rows],
            "configurations": configuration_rows,
            **frontier,
        })

    result = {
        "status": "EXACT_GLOBAL_ORDINARY_CONFIG_FRONTIERS_COMPLETE",
        "results": results,
        "checks": {
            "all_four_surviving_Gram_target_types_included": True,
            "configuration_identity_retained": True,
            "all_eight_fibre_summed_recurrence_rows_exact": True,
            "backward_projection_to_complete_paths_exact": True,
            "SAT_or_SMT_used": False,
        },
    }
    temporary = OUTPUT.with_suffix(OUTPUT.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(result, separators=(",", ":")) + "\n",
                         encoding="utf-8")
    temporary.replace(OUTPUT)
    print(json.dumps({
        "status": result["status"],
        "frontiers": [{
            "macro": row["macro"],
            "solution_path_count": row["solution_path_count"],
            "forward_state_counts": row["forward_state_counts"],
            "allowed_config_counts": [len(value) for value
                                      in row["allowed_config_indices_by_fibre"]],
        } for row in results],
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
