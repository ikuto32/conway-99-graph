"""Exact fibre-summed q-recurrence filter for E72 source row 150.

Let c be constant on the eight exceptional fibres with the three-coordinate
Gram-circulation vectors and zero on the thirteen ordinary C4 fibres, and put
q=Bc.  Since sum(c)=0 and P^T c=0, the outer identity gives

    (B+I)q = 12c.

Pointwise root-group counts uniquely fix q on all 32 exceptional vertices,
even before the twelve disjoint exceptional blocks are materialized.  After
summing the recurrence over the four vertices of each exceptional fibre,
all exceptional-neighbour terms are fixed by the two labelled margin
sequences of those blocks.  Each ordinary C4 has only 1, 3, or 11 possible
unordered exceptional-degree configurations.  This script exhausts their
contributions to the eight summed recurrence rows using a finite tuple DP.

For a singular Gram matrix H, vector equality is tested after multiplication
by H.  Since H is positive semidefinite, H(a-b)=0 is exactly equality of the
represented Gram vectors.  No SAT/SMT package is used.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import os
import time
from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

import scratch_theory_e72_source150_norm_collision_filter as base


LOCAL = base.LOCAL
CATALOG = base.CATALOG
GRAM = base.GRAM
OUTPUT = Path("scratch_theory_e72_source150_fibre_recurrence_filter.json")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def atomic_json(path, value):
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, separators=(",", ":")) + "\n",
                         encoding="utf-8")
    temporary.replace(path)


def scale(value, vector):
    return tuple(value * coordinate for coordinate in vector)


def covector(vector, H):
    return tuple(
        sum(H[row][column] * vector[column] for column in range(3))
        for row in range(3)
    )


def flatten_covectors(vectors, H):
    return tuple(value for vector in vectors for value in covector(vector, H))


def ordinary_load_options(patterns, disjoint, vectors, H):
    """All eight-fibre load tuples from one ordinary four-vertex fibre."""

    answer = set()
    for indices in itertools.combinations_with_replacement(
        range(len(patterns)), 4
    ):
        if not all(
            sum(patterns[index][fibre] for index in indices) == 4
            for fibre in disjoint
        ):
            continue
        loads = [[Fraction(0), Fraction(0), Fraction(0)]
                 for _ in vectors]
        for index in indices:
            pattern = patterns[index]
            q = base.add_vectors(
                scale(pattern[fibre], vectors[fibre])
                for fibre in range(len(vectors))
            )
            for fibre in disjoint:
                for coordinate in range(3):
                    loads[fibre][coordinate] += pattern[fibre] * q[coordinate]
        answer.add(flatten_covectors(tuple(map(tuple, loads)), H))
    assert answer
    return tuple(sorted(answer))


@lru_cache(maxsize=None)
def tuple_sum_feasible(option_rows, target):
    """Exact finite DP, with safe suffix coordinate bounds."""

    dimension = len(target)
    suffix_min = [[Fraction(0)] * dimension
                  for _ in range(len(option_rows) + 1)]
    suffix_max = [[Fraction(0)] * dimension
                  for _ in range(len(option_rows) + 1)]
    for index in range(len(option_rows) - 1, -1, -1):
        for coordinate in range(dimension):
            values = [row[coordinate] for row in option_rows[index]]
            suffix_min[index][coordinate] = (
                min(values) + suffix_min[index + 1][coordinate]
            )
            suffix_max[index][coordinate] = (
                max(values) + suffix_max[index + 1][coordinate]
            )

    states = {(Fraction(0),) * dimension}
    peak = 1
    for index, options in enumerate(option_rows):
        following = set()
        for state in states:
            for option in options:
                value = tuple(left + right
                              for left, right in zip(state, option))
                if all(
                    value[coordinate] + suffix_min[index + 1][coordinate]
                    <= target[coordinate]
                    <= value[coordinate] + suffix_max[index + 1][coordinate]
                    for coordinate in range(dimension)
                ):
                    following.add(value)
        states = following
        peak = max(peak, len(states))
        if not states:
            break
    return target in states, peak, len(states)


def main():
    started = time.monotonic()
    document = json.loads(LOCAL.read_text(encoding="utf-8"))
    row = next(
        item for item in document["support_rows"]
        if item["partition"] == [2, 2, 2, 2, 1, 1, 1, 1]
        and item["compression_orbit_index"] == 0
    )
    exceptional_supports = tuple(
        tuple(item["support"]) for item in row["exceptional_supports"]
    )
    ordinary_supports = tuple(
        item for item in base.ALL_SUPPORTS if item not in exceptional_supports
    )
    fibre_index = {fibre: index
                   for index, fibre in enumerate(exceptional_supports)}
    overlap_pairs = tuple(
        pair for pair in itertools.combinations(range(8), 2)
        if set(exceptional_supports[pair[0]])
        & set(exceptional_supports[pair[1]])
    )
    disjoint_pairs = tuple(
        pair for pair in itertools.combinations(range(8), 2)
        if not set(exceptional_supports[pair[0]])
        & set(exceptional_supports[pair[1]])
    )

    catalog = [
        entry for entry in json.loads(CATALOG.read_text(encoding="utf-8"))[
            "macro_entries"
        ] if entry["source_row_index"] == 150
    ]
    entry_by_key = {
        base.entry_key(entry, exceptional_supports, overlap_pairs): entry
        for entry in catalog
    }
    assert len(entry_by_key) == 21
    gram_rows = {
        (entry["state_orbit_number"],
         entry["signature_stabilizer_orbit_number"],
         entry["signature_stabilizer_canonical"]): entry
        for entry in json.loads(GRAM.read_text(encoding="utf-8"))["rows"]
        if entry["source_row_index"] == 150
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
    vertices = tuple(
        tuple(sorted((2 * first + bit_first, 2 * second + bit_second)))
        for first, second in exceptional_supports
        for bit_first, bit_second in itertools.product((0, 1), repeat=2)
    )
    vertex_index = {vertex: index for index, vertex in enumerate(vertices)}
    vertices_by_fibre = tuple(
        tuple(index for index, vertex in enumerate(vertices)
              if base.support(vertex) == fibre)
        for fibre in exceptional_supports
    )
    ordinary_patterns = {
        ordinary: base.local_vertex_patterns(
            ordinary, exceptional_supports, ordinary_supports
        )
        for ordinary in ordinary_supports
    }

    ordinary_option_cache = {}
    target_cache = {}
    per_macro = defaultdict(Counter)
    target_histogram = Counter()
    controls = []
    survivors = []

    for number, representative in enumerate(row["representatives"]):
        key = base.representative_key(
            representative["edges"], fibre_index, overlap_pairs
        )
        entry = entry_by_key[key]
        macro = (entry["state_orbit_number"],
                 entry["signature_stabilizer_orbit_number"])
        gram_key = macro + (entry["signature_stabilizer_canonical"],)
        gram = gram_rows[gram_key]
        H = tuple(tuple(Fraction(value) for value in values)
                  for values in gram["unique_H"])
        h_key = tuple(map(tuple, H))
        if h_key not in ordinary_option_cache:
            ordinary_option_cache[h_key] = tuple(
                ordinary_load_options(
                    ordinary_patterns[ordinary][0],
                    ordinary_patterns[ordinary][1], vectors, H
                )
                for ordinary in ordinary_supports
            )

        adjacency = [set() for _ in vertices]
        for edge in representative["edges"]:
            left, right = (vertex_index[tuple(value)] for value in edge)
            adjacency[left].add(right)
            adjacency[right].add(left)
        block_totals = {
            tuple(sorted((int(left), int(right)))): int(value)
            for left, right, value
            in representative["disjoint_Gram_profile"]["targets"]
        }
        assert set(block_totals) == set(disjoint_pairs)

        degree_rows = {}
        for source, fibre_vertices in enumerate(vertices_by_fibre):
            for vertex in fibre_vertices:
                patterns, _, _ = base.exceptional_vertex_patterns(
                    vertex, source, adjacency, vertices,
                    exceptional_supports, ordinary_supports
                )
                assert len(patterns) == 1
                degree_rows[vertex] = patterns[0]

        q_exceptional = []
        for vertex in range(len(vertices)):
            degrees = [0] * 8
            for other in adjacency[vertex]:
                degrees[fibre_index[base.support(vertices[other])]] += 1
            source = fibre_index[base.support(vertices[vertex])]
            for target in range(8):
                if not set(exceptional_supports[source]) & set(
                    exceptional_supports[target]
                ):
                    degrees[target] = degree_rows[vertex][target]
            q_exceptional.append(base.add_vectors(
                scale(degrees[target], vectors[target])
                for target in range(8)
            ))
        q_exceptional = tuple(q_exceptional)

        targets = []
        for source, fibre_vertices in enumerate(vertices_by_fibre):
            left = scale(48, vectors[source])
            q_self = base.add_vectors(q_exceptional[x]
                                      for x in fibre_vertices)
            exceptional_load_rows = []
            for y in range(len(vertices)):
                target_fibre = fibre_index[base.support(vertices[y])]
                if target_fibre == source or set(
                    exceptional_supports[source]
                ) & set(exceptional_supports[target_fibre]):
                    multiplicity = sum(y in adjacency[x]
                                       for x in fibre_vertices)
                else:
                    multiplicity = degree_rows[y][source]
                exceptional_load_rows.append(
                    scale(multiplicity, q_exceptional[y])
                )
            exceptional_load = base.add_vectors(exceptional_load_rows)
            targets.append(tuple(
                left[index] - q_self[index] - exceptional_load[index]
                for index in range(3)
            ))
        target = flatten_covectors(tuple(targets), H)
        target_histogram[(macro, tuple(str(value) for value in target))] += 1
        cache_key = (h_key, target)
        if cache_key not in target_cache:
            target_cache[cache_key] = tuple_sum_feasible(
                ordinary_option_cache[h_key], target
            )
        feasible, peak, final_states = target_cache[cache_key]

        stats = per_macro[macro]
        stats["input_orbits"] += 1
        stats["input_mass"] += representative["orbit_size"]
        if feasible:
            stats["passing_orbits"] += 1
            stats["passing_mass"] += representative["orbit_size"]
            survivors.append([
                representative["mask_hex"], representative["orbit_size"],
                representative["Q"], list(macro),
            ])
        else:
            stats["rejected_orbits"] += 1
            stats["rejected_mass"] += representative["orbit_size"]
        if len(controls) < 30:
            controls.append({
                "record_number": number,
                "macro": list(macro),
                "target": [str(value) for value in target],
                "ordinary_option_counts": [
                    len(options) for options in ordinary_option_cache[h_key]
                ],
                "feasible": feasible,
                "DP_peak_states": peak,
                "DP_final_states": final_states,
            })

    summary = {
        "input_orbits": len(row["representatives"]),
        "input_mass": sum(item["orbit_size"] for item in row["representatives"]),
        "passing_orbits": len(survivors),
        "passing_mass": sum(item[1] for item in survivors),
        "rejected_orbits": len(row["representatives"]) - len(survivors),
        "distinct_Gram_H": len(ordinary_option_cache),
        "distinct_recurrence_targets": len(target_cache),
        "elapsed_seconds": round(time.monotonic() - started, 6),
    }
    assert summary["input_orbits"] == 5943
    assert summary["input_mass"] == 2_244_608
    result = {
        "status": "EXACT_FIBRE_SUMMED_Q_RECURRENCE_FILTER_COMPLETE",
        "inputs": {str(path): sha256(path)
                   for path in (LOCAL, CATALOG, GRAM)},
        "summary": summary,
        "per_macro": {
            f"{key[0]}:{key[1]}": dict(sorted(value.items()))
            for key, value in sorted(per_macro.items())
        },
        "distinct_target_histogram": {
            f"macro={key[0][0]}:{key[0][1]};target={','.join(key[1])}": value
            for key, value in sorted(target_histogram.items())
        },
        "controls": controls,
        "survivor_fields": [
            "mask_hex", "orbit_size", "Q", "macro_state_and_signature",
        ],
        "survivors": survivors,
        "checks": {
            "all_12_disjoint_exceptional_block_totals_used": True,
            "all_exceptional_vertex_degree_patterns_unique": True,
            "exceptional_q_values_fixed_before_block_materialization": True,
            "all_13_ordinary_fibre_degree_configurations_enumerated": True,
            "recurrence_summed_over_each_of_8_exceptional_fibres": True,
            "singular_Gram_equality_tested_modulo_kernel_via_H": True,
            "ordinary_exception_direction_used_is_one_sided_only": True,
            "SAT_or_SMT_used": False,
        },
        "claim_boundary": (
            "A rejection is rigorous.  Passage supplies only the eight "
            "fibre-summed exceptional rows of (B+I)q=12c; pointwise rows, "
            "labelled 4x4 blocks, pair bounds, and the rest of the graph are "
            "not constructed."
        ),
    }
    atomic_json(OUTPUT, result)
    print(json.dumps({"status": result["status"], **summary}, sort_keys=True))


if __name__ == "__main__":
    main()
