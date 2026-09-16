"""Exact relaxed q-norm/collision filter for all source-332 Gram profiles.

The unique source-332 macro has a four-dimensional circulation space and
three exact Gram profiles t=-1,0,1.  For each of its 215 saved local graph
orbits and each profile, this script enumerates all per-vertex degrees to
the omitted disjoint exceptional blocks allowed by the pointwise root-group
equations and their Gram-forced block totals.  It also enumerates all degree
configurations in the twelve ordinary C4 fibres.  A finite tuple DP matches
the global ||Bc||^2 identity and all nine same-exceptional-fibre collision
totals.  Disjoint exceptional blocks are deliberately relaxed to independent
source-side degree configurations, hence every rejection is sound.  No
SAT/SMT package is used.
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

import scratch_theory_e72_source150_norm_collision_filter as common
from scratch_theory_unsigned_kernel_filter import nullspace


LOCAL = common.LOCAL
PARAMETRIC = Path("scratch_theory_e72_source332_parametric_gram.json")
OUTPUT = Path("scratch_theory_e72_source332_norm_collision_filter.json")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def atomic_json(path, value):
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, separators=(",", ":")) + "\n",
                         encoding="utf-8")
    temporary.replace(path)


def vector_sum(rows, dimension):
    rows = tuple(rows)
    return tuple(sum(row[index] for row in rows)
                 for index in range(dimension))


def scale(value, vector):
    return tuple(value * coordinate for coordinate in vector)


def dot(left, H, right):
    return sum(left[i] * H[i][j] * right[j]
               for i in range(len(left)) for j in range(len(right)))


def ordinary_options(patterns, disjoint, vectors, H):
    dimension = len(H)
    answer = set()
    for indices in itertools.combinations_with_replacement(
        range(len(patterns)), 4
    ):
        if not all(sum(patterns[index][fibre] for index in indices) == 4
                   for fibre in disjoint):
            continue
        norm = Fraction(0)
        collision = [0] * len(vectors)
        for index in indices:
            pattern = patterns[index]
            q = vector_sum(
                (scale(pattern[fibre], vectors[fibre])
                 for fibre in range(len(vectors))), dimension
            )
            norm += dot(q, H, q)
            for fibre, degree in enumerate(pattern):
                collision[fibre] += degree * (degree - 1) // 2
        assert norm.denominator == 1 and norm >= 0
        answer.add((int(norm), tuple(collision)))
    assert answer
    return tuple(sorted(answer))


def exceptional_options(source, fibre_vertices, adjacency, vertices,
                        supports, ordinary_supports, block_totals,
                        vectors, H):
    dimension = len(H)
    pattern_rows = []
    disjoint = None
    residual_rows = []
    for vertex in fibre_vertices:
        patterns, current_disjoint, residual = (
            common.exceptional_vertex_patterns(
                vertex, source, adjacency, vertices, supports,
                ordinary_supports
            )
        )
        if not patterns:
            return (), {
                "empty_vertex": vertex,
                "residual": residual,
            }
        if disjoint is None:
            disjoint = current_disjoint
        assert disjoint == current_disjoint
        pattern_rows.append(patterns)
        residual_rows.append(residual)

    answer = set()
    accepted_products = 0
    products_examined = 0
    support_to_index = {support: index
                        for index, support in enumerate(supports)}
    for chosen in itertools.product(*pattern_rows):
        products_examined += 1
        if not all(
            sum(pattern[target] for pattern in chosen)
            == block_totals[tuple(sorted((source, target)))]
            for target in disjoint
        ):
            continue
        accepted_products += 1
        norm = Fraction(0)
        collision = [0] * len(vectors)
        for vertex, unknown in zip(fibre_vertices, chosen):
            degrees = [0] * len(vectors)
            for other in adjacency[vertex]:
                degrees[support_to_index[common.support(vertices[other])]] += 1
            for target in disjoint:
                degrees[target] = unknown[target]
            q = vector_sum(
                (scale(degrees[target], vectors[target])
                 for target in range(len(vectors))), dimension
            )
            norm += dot(q, H, q)
            for target, degree in enumerate(degrees):
                collision[target] += degree * (degree - 1) // 2
        assert norm.denominator == 1 and norm >= 0
        answer.add((int(norm), tuple(collision)))
    return tuple(sorted(answer)), {
        "products_examined": products_examined,
        "accepted_products": accepted_products,
        "vertex_pattern_counts": [len(row) for row in pattern_rows],
        "residual_rows": residual_rows,
    }


@lru_cache(maxsize=None)
def aggregate_feasible(option_rows, target_norm, target_collision):
    states = {(0, (0,) * len(target_collision))}
    peak = 1
    for options in option_rows:
        following = set()
        for norm, collision in states:
            for add_norm, add_collision in options:
                new_norm = norm + add_norm
                if new_norm > target_norm:
                    continue
                new_collision = tuple(left + right for left, right
                                      in zip(collision, add_collision))
                if any(value > bound for value, bound
                       in zip(new_collision, target_collision)):
                    continue
                following.add((new_norm, new_collision))
        states = following
        peak = max(peak, len(states))
        if not states:
            break
    return ((target_norm, target_collision) in states, peak, len(states))


def main():
    started = time.monotonic()
    document = json.loads(LOCAL.read_text(encoding="utf-8"))
    row = next(
        item for item in document["support_rows"]
        if item["partition"] == [2, 2, 2, 1, 1, 1, 1, 1, 1]
        and item["compression_orbit_index"] == 102
    )
    supports = tuple(tuple(item["support"])
                     for item in row["exceptional_supports"])
    deficits = tuple(int(item["deficit"])
                     for item in row["exceptional_supports"])
    ordinary_supports = tuple(item for item in common.ALL_SUPPORTS
                              if item not in supports)
    support_to_index = {support: index for index, support in enumerate(supports)}
    disjoint_pairs = tuple(
        pair for pair in itertools.combinations(range(len(supports)), 2)
        if not set(supports[pair[0]]) & set(supports[pair[1]])
    )
    assert len(disjoint_pairs) == 18

    incidence_t = [[int(group in support) for support in supports]
                   for group in common.GROUPS]
    basis = nullspace(incidence_t)
    vectors = tuple(tuple(basis[column][row]
                          for column in range(len(basis)))
                    for row in range(len(supports)))
    assert len(basis) == 4
    assert all(vector_sum(
        (vectors[index] for index, support in enumerate(supports)
         if group in support), 4
    ) == (0, 0, 0, 0) for group in common.GROUPS)

    profiles = json.loads(PARAMETRIC.read_text(encoding="utf-8"))[
        "feasible_parameters"
    ]
    assert [profile["parameter"] for profile in profiles] == ["-1", "0", "1"]
    profile_rows = []
    for profile in profiles:
        H = tuple(tuple(Fraction(value) for value in values)
                  for values in profile["H"])
        totals = {
            tuple(sorted((int(left), int(right)))): int(value)
            for left, right, value
            in profile["disjoint_exceptional_block_totals"]
        }
        assert set(totals) == set(disjoint_pairs)
        profile_rows.append((profile["parameter"], H, totals))

    vertices = tuple(
        tuple(sorted((2 * first + bit_first, 2 * second + bit_second)))
        for first, second in supports
        for bit_first, bit_second in itertools.product((0, 1), repeat=2)
    )
    vertex_index = {vertex: index for index, vertex in enumerate(vertices)}
    vertices_by_fibre = tuple(
        tuple(index for index, vertex in enumerate(vertices)
              if common.support(vertex) == support)
        for support in supports
    )
    ordinary_data = {
        support: common.local_vertex_patterns(
            support, supports, ordinary_supports
        )
        for support in ordinary_supports
    }

    ordinary_cache = {}
    feasibility_cache = {}
    per_profile = defaultdict(Counter)
    controls = []
    survivors = []
    empty_exceptional_frontiers = 0
    for representative_number, representative in enumerate(row["representatives"]):
        adjacency = [set() for _ in vertices]
        for edge in representative["edges"]:
            left, right = (vertex_index[tuple(value)] for value in edge)
            adjacency[left].add(right)
            adjacency[right].add(left)

        for parameter, H, block_totals in profile_rows:
            h_key = tuple(map(tuple, H))
            if h_key not in ordinary_cache:
                ordinary_cache[h_key] = tuple(
                    ordinary_options(ordinary_data[support][0],
                                     ordinary_data[support][1], vectors, H)
                    for support in ordinary_supports
                )

            exceptional_rows = []
            exceptional_details = []
            for source, fibre_vertices in enumerate(vertices_by_fibre):
                options, details = exceptional_options(
                    source, fibre_vertices, adjacency, vertices, supports,
                    ordinary_supports, block_totals, vectors, H
                )
                exceptional_rows.append(options)
                exceptional_details.append(details)
            exceptional_rows = tuple(exceptional_rows)
            if any(not options for options in exceptional_rows):
                feasible, peak, final_states = False, 0, 0
                empty_exceptional_frontiers += 1
            else:
                c = tuple(vectors[support_to_index[common.support(vertex)]]
                          for vertex in vertices)
                assert sum(dot(value, H, value) for value in c) == 96
                cBc = 2 * sum(
                    dot(c[vertex_index[tuple(edge[0])]], H,
                        c[vertex_index[tuple(edge[1])]])
                    for edge in representative["edges"]
                )
                cBc += 2 * sum(
                    block_totals[pair]
                    * dot(vectors[pair[0]], H, vectors[pair[1]])
                    for pair in disjoint_pairs
                )
                total_norm = 12 * 96 - cBc
                assert total_norm.denominator == 1 and total_norm >= 0
                total_norm = int(total_norm)
                collision_target = []
                for fibre, fibre_vertices in enumerate(vertices_by_fibre):
                    value = 0
                    for left, right in itertools.combinations(fibre_vertices, 2):
                        value += (
                            2 - len(set(vertices[left]) & set(vertices[right]))
                            - int(right in adjacency[left])
                        )
                    collision_target.append(value)
                collision_target = tuple(collision_target)
                if representative_number == 0:
                    print(json.dumps({
                        "debug_parameter": parameter,
                        "exceptional_option_counts": [
                            len(options) for options in exceptional_rows
                        ],
                        "exceptional_pattern_counts": [
                            details.get("vertex_pattern_counts")
                            for details in exceptional_details
                        ],
                        "ordinary_option_counts": [
                            len(options) for options in ordinary_cache[h_key]
                        ],
                        "total_norm": total_norm,
                        "collision_target": collision_target,
                    }), flush=True)
                cache_key = (h_key, exceptional_rows, total_norm,
                             collision_target)
                if cache_key not in feasibility_cache:
                    option_rows = tuple(sorted(
                        exceptional_rows + ordinary_cache[h_key], key=len
                    ))
                    feasibility_cache[cache_key] = aggregate_feasible(
                        option_rows, total_norm, collision_target
                    )
                feasible, peak, final_states = feasibility_cache[cache_key]

            stats = per_profile[parameter]
            stats["input_orbits"] += 1
            stats["input_mass"] += representative["orbit_size"]
            if feasible:
                stats["passing_orbits"] += 1
                stats["passing_mass"] += representative["orbit_size"]
                survivors.append([
                    parameter, representative["mask_hex"],
                    representative["orbit_size"], representative["Q"],
                ])
            else:
                stats["rejected_orbits"] += 1
                stats["rejected_mass"] += representative["orbit_size"]
            if len(controls) < 18:
                controls.append({
                    "representative_number": representative_number,
                    "parameter": parameter,
                    "exceptional_option_counts": [len(options)
                                                  for options in exceptional_rows],
                    "exceptional_details": exceptional_details,
                    "ordinary_option_counts": [len(options)
                                               for options in ordinary_cache[h_key]],
                    "feasible": feasible,
                    "DP_peak_states": peak,
                    "DP_final_states": final_states,
                })

    summary = {
        "input_local_orbits": len(row["representatives"]),
        "input_local_mass": sum(item["orbit_size"]
                                for item in row["representatives"]),
        "profile_orbit_instances": 3 * len(row["representatives"]),
        "profile_mass_instances": 3 * sum(item["orbit_size"]
                                          for item in row["representatives"]),
        "passing_profile_orbit_instances": len(survivors),
        "passing_profile_mass_instances": sum(item[2] for item in survivors),
        "empty_exceptional_fibre_frontier_instances": empty_exceptional_frontiers,
        "distinct_DP_instances": len(feasibility_cache),
        "elapsed_seconds": round(time.monotonic() - started, 6),
    }
    assert summary["input_local_orbits"] == 215
    assert summary["input_local_mass"] == 131_072
    result = {
        "status": "EXACT_SOURCE332_NORM_COLLISION_RELAXATION_COMPLETE",
        "inputs": {str(path): sha256(path) for path in (LOCAL, PARAMETRIC)},
        "summary": summary,
        "per_parameter": {key: dict(sorted(value.items()))
                          for key, value in sorted(per_profile.items())},
        "ordinary_support_data": {
            str(support): {
                "vertex_pattern_count": len(ordinary_data[support][0]),
                "configuration_counts_by_parameter": [
                    len(ordinary_cache[tuple(map(tuple, H))][index])
                    for _, H, _ in profile_rows
                ],
            }
            for index, support in enumerate(ordinary_supports)
        },
        "controls": controls,
        "survivor_fields": ["parameter", "mask_hex", "orbit_size", "Q"],
        "survivors": survivors,
        "checks": {
            "all_three_exact_parameters_included": True,
            "all_18_disjoint_exceptional_Gram_totals_used": True,
            "exceptional_blocks_relaxed_to_independent_source_degree_rows": True,
            "ordinary_exception_direction_used_is_one_sided_only": True,
            "global_q_norm_and_9_collision_totals_exact": True,
            "SAT_or_SMT_used": False,
        },
        "claim_boundary": (
            "Every rejection is rigorous because all omitted compatibility "
            "conditions only enlarge this finite degree-vector relaxation.  "
            "Passage does not construct labelled blocks or a graph."
        ),
    }
    atomic_json(OUTPUT, result)
    print(json.dumps({"status": result["status"], **summary}, sort_keys=True))


if __name__ == "__main__":
    main()
