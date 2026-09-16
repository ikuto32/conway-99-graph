"""Synchronize q-norm/collision moments with source-150 config frontiers.

The fibre-summed recurrence leaves 64--2331 common choices of the thirteen
ordinary C4 degree configurations.  This script retains their identities and
requires the same global choice to supply the exact remaining ||Bc||^2 and
nine (here eight) same-exceptional-fibre collision totals after the fixed
exceptional degree rows are subtracted.  No labelled E--ordinary maps are
needed for these moments.  No SAT/SMT package is used.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import os
import time
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

import scratch_theory_e72_source150_fibre_recurrence_filter as recurrence
import scratch_theory_e72_source150_norm_collision_filter as base


LOCAL = base.LOCAL
CATALOG = base.CATALOG
GRAM = base.GRAM
CONFIG = Path("scratch_theory_e72_source150_global_config_census.json")
OUTPUT = Path("scratch_theory_e72_source150_global_config_moment_filter.json")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def atomic_json(path, value):
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, separators=(",", ":")) + "\n",
                         encoding="utf-8")
    temporary.replace(path)


def scale(value, vector):
    return tuple(value * coordinate for coordinate in vector)


def configuration_moment(configuration, vectors, H):
    norm = Fraction(0)
    collision = [0] * len(vectors)
    for pattern in configuration:
        q = base.add_vectors(scale(pattern[fibre], vectors[fibre])
                             for fibre in range(len(vectors)))
        norm += base.dot(q, H, q)
        for fibre, degree in enumerate(pattern):
            collision[fibre] += degree * (degree - 1) // 2
    assert norm.denominator == 1
    return int(norm), tuple(collision)


def main():
    started = time.monotonic()
    document = json.loads(LOCAL.read_text(encoding="utf-8"))
    row = next(
        item for item in document["support_rows"]
        if item["partition"] == [2, 2, 2, 2, 1, 1, 1, 1]
        and item["compression_orbit_index"] == 0
    )
    supports = tuple(tuple(item["support"])
                     for item in row["exceptional_supports"])
    ordinary_supports = tuple(item for item in base.ALL_SUPPORTS
                              if item not in supports)
    support_to_fibre = {support: index for index, support in enumerate(supports)}
    overlap_pairs = tuple(
        pair for pair in itertools.combinations(range(8), 2)
        if set(supports[pair[0]]) & set(supports[pair[1]])
    )
    disjoint_pairs = tuple(
        pair for pair in itertools.combinations(range(8), 2)
        if not set(supports[pair[0]]) & set(supports[pair[1]])
    )
    catalog = [entry for entry in json.loads(
        CATALOG.read_text(encoding="utf-8")
    )["macro_entries"] if entry["source_row_index"] == 150]
    entry_by_key = {
        base.entry_key(entry, supports, overlap_pairs): entry
        for entry in catalog
    }
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
        for first, second in supports
        for bit_first, bit_second in itertools.product((0, 1), repeat=2)
    )
    vertex_index = {vertex: index for index, vertex in enumerate(vertices)}
    vertices_by_fibre = tuple(
        tuple(index for index, vertex in enumerate(vertices)
              if base.support(vertex) == support)
        for support in supports
    )

    config_rows = {}
    for item in json.loads(CONFIG.read_text(encoding="utf-8"))["results"]:
        H = tuple(tuple(Fraction(value) for value in row)
                  for row in item["Gram_H"])
        configurations = tuple(
            tuple(tuple(tuple(int(value) for value in pattern)
                        for pattern in config)
                  for config in support_rows)
            for support_rows in item["configurations"]
        )
        moments = tuple(
            tuple(configuration_moment(config, vectors, H)
                  for config in support_rows)
            for support_rows in configurations
        )
        signature_to_bits = defaultdict(int)
        solutions = item["configuration_index_solutions"]
        for solution_index, solution in enumerate(solutions):
            norm = 0
            collision = [0] * 8
            for support_index, config_index in enumerate(solution):
                add_norm, add_collision = moments[support_index][config_index]
                norm += add_norm
                collision = [left + right for left, right
                             in zip(collision, add_collision)]
            signature_to_bits[(norm, tuple(collision))] |= 1 << solution_index
        config_rows[H] = {
            "solution_count": len(solutions),
            "signature_to_bits": dict(signature_to_bits),
            "signature_histogram": {
                signature: bits.bit_count()
                for signature, bits in signature_to_bits.items()
            },
        }

    per_macro = defaultdict(Counter)
    signature_histogram = Counter()
    controls = []
    survivors = []
    for number, representative in enumerate(row["representatives"]):
        entry = entry_by_key[base.representative_key(
            representative["edges"], support_to_fibre, overlap_pairs
        )]
        macro = (entry["state_orbit_number"],
                 entry["signature_stabilizer_orbit_number"])
        gram = gram_rows[macro + (
            entry["signature_stabilizer_canonical"],
        )]
        H = tuple(tuple(Fraction(value) for value in row)
                  for row in gram["unique_H"])
        # The H* rows were already excluded and have no surviving global
        # configuration frontier.
        if H not in config_rows:
            feasible_bits = 0
            required = None
        else:
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
            degree_rows = {}
            for source, fibre_vertices in enumerate(vertices_by_fibre):
                for vertex in fibre_vertices:
                    patterns, _, _ = base.exceptional_vertex_patterns(
                        vertex, source, adjacency, vertices, supports,
                        ordinary_supports
                    )
                    assert len(patterns) == 1
                    degree_rows[vertex] = patterns[0]

            q_exceptional = []
            collision_exceptional = [0] * 8
            for vertex in range(len(vertices)):
                degrees = [0] * 8
                for other in adjacency[vertex]:
                    degrees[support_to_fibre[base.support(vertices[other])]] += 1
                source = support_to_fibre[base.support(vertices[vertex])]
                for target in range(8):
                    if not set(supports[source]) & set(supports[target]):
                        degrees[target] = degree_rows[vertex][target]
                q_exceptional.append(base.add_vectors(
                    scale(degrees[target], vectors[target])
                    for target in range(8)
                ))
                for target, degree in enumerate(degrees):
                    collision_exceptional[target] += degree * (degree - 1) // 2
            exceptional_norm = sum(base.dot(value, H, value)
                                   for value in q_exceptional)
            assert exceptional_norm.denominator == 1

            c = tuple(vectors[support_to_fibre[base.support(vertex)]]
                      for vertex in vertices)
            cBc = 2 * sum(
                base.dot(c[vertex_index[tuple(edge[0])]], H,
                         c[vertex_index[tuple(edge[1])]])
                for edge in representative["edges"]
            )
            cBc += 2 * sum(
                block_totals[pair]
                * base.dot(vectors[pair[0]], H, vectors[pair[1]])
                for pair in disjoint_pairs
            )
            total_norm = 12 * 96 - cBc
            assert total_norm.denominator == 1
            total_collision = tuple(
                sum(
                    2 - len(set(vertices[left]) & set(vertices[right]))
                    - int(right in adjacency[left])
                    for left, right in itertools.combinations(fibre_vertices, 2)
                )
                for fibre_vertices in vertices_by_fibre
            )
            required = (
                int(total_norm - exceptional_norm),
                tuple(left - right for left, right
                      in zip(total_collision, collision_exceptional)),
            )
            assert required[0] >= 0 and all(value >= 0 for value in required[1])
            feasible_bits = config_rows[H]["signature_to_bits"].get(required, 0)
            signature_histogram[(macro, required, feasible_bits.bit_count())] += 1

        stats = per_macro[macro]
        stats["input_orbits"] += 1
        stats["input_mass"] += representative["orbit_size"]
        if feasible_bits:
            stats["passing_orbits"] += 1
            stats["passing_mass"] += representative["orbit_size"]
            survivors.append([
                representative["mask_hex"], representative["orbit_size"],
                representative["Q"], list(macro), feasible_bits.bit_count(),
            ])
        else:
            stats["rejected_orbits"] += 1
            stats["rejected_mass"] += representative["orbit_size"]
        if len(controls) < 30:
            controls.append({
                "record_number": number,
                "macro": list(macro),
                "required_ordinary_signature": (
                    None if required is None
                    else [required[0], list(required[1])]
                ),
                "passing_global_config_solutions": feasible_bits.bit_count(),
            })

    summary = {
        "input_orbits": len(row["representatives"]),
        "input_mass": sum(item["orbit_size"] for item in row["representatives"]),
        "passing_orbits": len(survivors),
        "passing_mass": sum(item[1] for item in survivors),
        "rejected_orbits": len(row["representatives"]) - len(survivors),
        "distinct_required_signatures": len(signature_histogram),
        "elapsed_seconds": round(time.monotonic() - started, 6),
    }
    result = {
        "status": "EXACT_GLOBAL_CONFIG_MOMENT_FILTER_COMPLETE",
        "inputs": {str(path): sha256(path)
                   for path in (LOCAL, CATALOG, GRAM, CONFIG)},
        "summary": summary,
        "per_macro": {f"{key[0]}:{key[1]}": dict(sorted(value.items()))
                      for key, value in sorted(per_macro.items())},
        "configuration_signature_histograms": {
            str([[int(value) for value in row] for row in H]): {
                f"norm={signature[0]};collision={','.join(map(str, signature[1]))}": count
                for signature, count in sorted(data["signature_histogram"].items())
            }
            for H, data in config_rows.items()
        },
        "controls": controls,
        "survivor_fields": [
            "mask_hex", "orbit_size", "Q", "macro",
            "passing_global_config_solution_count",
        ],
        "survivors": survivors,
        "checks": {
            "global_configuration_identity_synchronized": True,
            "total_q_norm_exact": True,
            "all_same_exceptional_fibre_collision_totals_exact": True,
            "disjoint_EE_degree_rows_unique": True,
            "ordinary_exception_direction_used_is_one_sided_only": True,
            "SAT_or_SMT_used": False,
        },
        "claim_boundary": (
            "A rejection is exact for the combined fibre-summed recurrence "
            "and moment subsystem.  Passing does not construct labelled "
            "blocks or the rest of the graph."
        ),
    }
    atomic_json(OUTPUT, result)
    print(json.dumps({"status": result["status"], **summary}, sort_keys=True))


if __name__ == "__main__":
    main()
