"""Exact support-level q-norm/collision filter for E72 source row 150.

For every stored 32-vertex exceptional local graph this audit reconstructs
its unique Gram representation and the Gram-forced totals of the twelve
not-yet-realized disjoint exceptional blocks.  It exhausts the possible
per-vertex degree vectors of both the eight exceptional fibres and the
thirteen ordinary C4 fibres.  The resulting exact q=Bc norm contributions
and same-exceptional-fibre collision contributions must sum to the global
spectral/collision targets.  The exceptional block enumeration deliberately
forgets bipartite graphical compatibility, so it is a relaxation and every
rejection remains rigorous.  Only explicit small integer tuples are
enumerated; no SAT/SMT package is used.
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


LOCAL = Path(
    "scratch_general_e72_q3_gram_frontier_disjoint_gram_filtered_reps.json"
)
CATALOG = Path("scratch_general_e72_q3_gram_fast_expansion_macro_catalog.json")
GRAM = Path("scratch_theory_e72_macro_full_gram.json")
OUTPUT = Path("scratch_theory_e72_source150_norm_collision_filter.json")
GROUPS = tuple(range(7))
ALL_SUPPORTS = tuple(itertools.combinations(GROUPS, 2))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def atomic_json(path, value):
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, separators=(",", ":")) + "\n",
                         encoding="utf-8")
    temporary.replace(path)


def support(vertex):
    return tuple(sorted(symbol // 2 for symbol in vertex))


def normal_edge(edge):
    return tuple(sorted(tuple(vertex) for vertex in edge))


def parse_fraction(value):
    return Fraction(value)


def dot(left, matrix, right):
    return sum(
        left[i] * matrix[i][j] * right[j]
        for i in range(len(left)) for j in range(len(right))
    )


def add_vectors(rows):
    rows = tuple(rows)
    if not rows:
        return (Fraction(0), Fraction(0), Fraction(0))
    return tuple(sum(row[index] for row in rows) for index in range(3))


def entry_key(entry, exceptional_supports, overlap_pairs):
    internal = tuple(sorted(normal_edge(edge) for edge in entry["internal_edges"]))
    overlap = {
        tuple(pair[:2]): int(pair[2]) for pair in entry["overlap_block_totals"]
    }
    return internal, tuple(overlap[pair] for pair in overlap_pairs)


def representative_key(edges, fibre_index, overlap_pairs):
    internal = []
    totals = Counter()
    for edge in edges:
        left, right = map(tuple, edge)
        left_fibre = fibre_index[support(left)]
        right_fibre = fibre_index[support(right)]
        if left_fibre == right_fibre:
            internal.append(normal_edge(edge))
        else:
            totals[tuple(sorted((left_fibre, right_fibre)))] += 1
    return tuple(sorted(internal)), tuple(totals[pair] for pair in overlap_pairs)


def local_vertex_patterns(ordinary_support, exceptional_supports,
                          ordinary_supports):
    disjoint = tuple(
        index for index, fibre in enumerate(exceptional_supports)
        if not (set(ordinary_support) & set(fibre))
    )
    required = tuple(
        (2 if group in ordinary_support else 4)
        - 2 * int(group in ordinary_support)
        - sum(
            group in other for other in ordinary_supports
            if not (set(ordinary_support) & set(other))
        )
        for group in GROUPS
    )
    answer = []
    for values in itertools.product(range(5), repeat=len(disjoint)):
        row = [0] * len(exceptional_supports)
        for index, value in zip(disjoint, values):
            row[index] = value
        if all(
            sum(row[index] for index, fibre in enumerate(exceptional_supports)
                if group in fibre) == required[group]
            for group in GROUPS
        ):
            answer.append(tuple(row))
    assert answer
    return tuple(answer), disjoint, required


def fibre_options(patterns, disjoint, vectors, H):
    """All unordered four-vertex degree configurations in one C4 fibre."""

    answer = set()
    for indices in itertools.combinations_with_replacement(
        range(len(patterns)), 4
    ):
        if not all(
            sum(patterns[index][fibre] for index in indices) == 4
            for fibre in disjoint
        ):
            continue
        collision = tuple(
            sum(patterns[index][fibre] * (patterns[index][fibre] - 1) // 2
                for index in indices)
            for fibre in range(len(vectors))
        )
        norm = Fraction(0)
        for index in indices:
            q = add_vectors(
                tuple(
                    patterns[index][fibre] * coordinate
                    for coordinate in vectors[fibre]
                )
                for fibre in range(len(vectors))
            )
            norm += dot(q, H, q)
        assert norm.denominator == 1 and norm >= 0
        answer.add((int(norm), collision))
    assert answer
    return tuple(sorted(answer))


def exceptional_vertex_patterns(vertex, source_fibre, adjacency,
                                vertices, exceptional_supports,
                                ordinary_supports):
    """Possible degrees from one exceptional vertex to disjoint E fibres."""

    source_support = exceptional_supports[source_fibre]
    disjoint = tuple(
        index for index, target in enumerate(exceptional_supports)
        if not (set(source_support) & set(target))
    )
    known = [0] * len(GROUPS)
    for other in adjacency[vertex]:
        for group in support(vertices[other]):
            known[group] += 1

    # Every disjoint ordinary C4 supplies exactly one neighbour to this
    # exceptional vertex.  This is the forced direction of the ordinary-C4
    # external-collision lemma; no converse regularity is assumed.
    forced_ordinary = [0] * len(GROUPS)
    for ordinary in ordinary_supports:
        if set(source_support) & set(ordinary):
            continue
        for group in ordinary:
            forced_ordinary[group] += 1

    residual = tuple(
        (2 if group in source_support else 4)
        - known[group] - forced_ordinary[group]
        for group in GROUPS
    )
    answer = []
    for values in itertools.product(range(5), repeat=len(disjoint)):
        row = [0] * len(exceptional_supports)
        for index, value in zip(disjoint, values):
            row[index] = value
        if all(
            sum(row[index] for index, target in enumerate(
                exceptional_supports) if group in target) == residual[group]
            for group in GROUPS
        ):
            answer.append(tuple(row))
    return tuple(answer), disjoint, residual


def exceptional_fibre_options(source_fibre, fibre_vertices, adjacency,
                              vertices, exceptional_supports,
                              ordinary_supports, block_totals, vectors, H):
    """Relaxed exact row-degree configurations for one exceptional fibre.

    The four source vertices are distinguished.  We impose every pointwise
    root-group equation and every Gram-forced block total.  We do not demand
    that the independently selected row degrees and the target-side row
    degrees come from the same 4x4 simple bipartite matrix.  Omitting that
    condition only enlarges the feasible set.
    """

    pattern_rows = []
    disjoint = None
    residual_rows = []
    for vertex in fibre_vertices:
        patterns, current_disjoint, residual = exceptional_vertex_patterns(
            vertex, source_fibre, adjacency, vertices,
            exceptional_supports, ordinary_supports
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
    products_examined = 0
    for chosen in itertools.product(*pattern_rows):
        products_examined += 1
        if not all(
            sum(row[target] for row in chosen)
            == block_totals[tuple(sorted((source_fibre, target)))]
            for target in disjoint
        ):
            continue
        norm = Fraction(0)
        collision = [0] * len(exceptional_supports)
        for vertex, unknown in zip(fibre_vertices, chosen):
            degrees = [0] * len(exceptional_supports)
            for other in adjacency[vertex]:
                degrees[
                    exceptional_supports.index(support(vertices[other]))
                ] += 1
            for target in disjoint:
                degrees[target] = unknown[target]
            q = add_vectors(
                tuple(degrees[target] * coordinate
                      for coordinate in vectors[target])
                for target in range(len(exceptional_supports))
            )
            norm += dot(q, H, q)
            for target, degree in enumerate(degrees):
                collision[target] += degree * (degree - 1) // 2
        assert norm.denominator == 1 and norm >= 0
        answer.add((int(norm), tuple(collision)))
    return tuple(sorted(answer)), {
        "products_examined": products_examined,
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
                new_collision = tuple(
                    left + right
                    for left, right in zip(collision, add_collision)
                )
                if any(value > bound
                       for value, bound in zip(new_collision, target_collision)):
                    continue
                following.add((new_norm, new_collision))
        states = following
        peak = max(peak, len(states))
        if not states:
            break
    target = (target_norm, target_collision)
    return target in states, peak, len(states)


def main():
    started = time.monotonic()
    local_document = json.loads(LOCAL.read_text(encoding="utf-8"))
    row = next(
        item for item in local_document["support_rows"]
        if item["partition"] == [2, 2, 2, 2, 1, 1, 1, 1]
        and item["compression_orbit_index"] == 0
    )
    exceptional_supports = tuple(
        tuple(item["support"]) for item in row["exceptional_supports"]
    )
    assert exceptional_supports == (
        (0, 2), (0, 3), (0, 4), (0, 5),
        (1, 2), (1, 3), (1, 4), (1, 5),
    )
    ordinary_supports = tuple(
        item for item in ALL_SUPPORTS if item not in exceptional_supports
    )
    fibre_index = {fibre: index
                   for index, fibre in enumerate(exceptional_supports)}
    overlap_pairs = tuple(
        pair for pair in itertools.combinations(range(8), 2)
        if set(exceptional_supports[pair[0]])
        & set(exceptional_supports[pair[1]])
    )

    catalog = [
        entry for entry in json.loads(CATALOG.read_text(encoding="utf-8"))[
            "macro_entries"
        ] if entry["source_row_index"] == 150
    ]
    gram_rows = {
        (entry["state_orbit_number"],
         entry["signature_stabilizer_orbit_number"],
         entry["signature_stabilizer_canonical"]): entry
        for entry in json.loads(GRAM.read_text(encoding="utf-8"))["rows"]
        if entry["source_row_index"] == 150
    }
    entry_by_key = {}
    for entry in catalog:
        key = entry_key(entry, exceptional_supports, overlap_pairs)
        assert key not in entry_by_key
        entry_by_key[key] = entry
    assert len(entry_by_key) == 21

    # Nullspace coordinates in the exact convention used by the Gram audit.
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
    assert all(add_vectors(vectors[index] for index, fibre in enumerate(
        exceptional_supports) if group in fibre) == (0, 0, 0)
        for group in GROUPS)

    local_data = {}
    for ordinary in ordinary_supports:
        local_data[ordinary] = local_vertex_patterns(
            ordinary, exceptional_supports, ordinary_supports
        )

    vertices = tuple(
        tuple(sorted((2 * first + bit_first, 2 * second + bit_second)))
        for first, second in exceptional_supports
        for bit_first, bit_second in itertools.product((0, 1), repeat=2)
    )
    vertex_index = {vertex: index for index, vertex in enumerate(vertices)}
    vertices_by_fibre = {
        fibre: tuple(index for index, vertex in enumerate(vertices)
                     if support(vertex) == fibre)
        for fibre in exceptional_supports
    }

    ordinary_option_cache = {}
    exceptional_option_cache = {}
    feasibility_cache = {}
    per_macro = defaultdict(Counter)
    target_histogram = Counter()
    survivors = []
    controls = []
    for number, representative in enumerate(row["representatives"]):
        key = representative_key(
            representative["edges"], fibre_index, overlap_pairs
        )
        entry = entry_by_key[key]
        gram_key = (
            entry["state_orbit_number"],
            entry["signature_stabilizer_orbit_number"],
            entry["signature_stabilizer_canonical"],
        )
        gram = gram_rows[gram_key]
        assert gram["unique"] and gram["passes_full_unique_gram_checks"]
        H = tuple(tuple(parse_fraction(value) for value in values)
                  for values in gram["unique_H"])
        h_key = tuple(tuple(value for value in values) for values in H)
        if h_key not in ordinary_option_cache:
            ordinary_option_cache[h_key] = tuple(
                fibre_options(local_data[ordinary][0],
                              local_data[ordinary][1], vectors, H)
                for ordinary in ordinary_supports
            )
        ordinary_option_rows = ordinary_option_cache[h_key]

        adjacency = [set() for _ in vertices]
        for edge in representative["edges"]:
            left, right = (vertex_index[tuple(value)] for value in edge)
            adjacency[left].add(right)
            adjacency[right].add(left)
        c = tuple(vectors[fibre_index[support(vertex)]] for vertex in vertices)
        assert sum(dot(value, H, value) for value in c) == 96

        disjoint_pairs = tuple(
            pair for pair in itertools.combinations(range(8), 2)
            if not (set(exceptional_supports[pair[0]])
                    & set(exceptional_supports[pair[1]]))
        )
        disjoint_targets = {
            tuple(sorted((int(left), int(right)))): int(value)
            for left, right, value
            in representative["disjoint_Gram_profile"]["targets"]
        }
        assert set(disjoint_targets) == set(disjoint_pairs)

        exceptional_cache_key = (
            h_key,
            tuple(tuple(sorted(neighbours)) for neighbours in adjacency),
            tuple(disjoint_targets[pair] for pair in disjoint_pairs),
        )
        if exceptional_cache_key not in exceptional_option_cache:
            exceptional_rows = []
            exceptional_details = []
            for source_fibre, fibre in enumerate(exceptional_supports):
                options, details = exceptional_fibre_options(
                    source_fibre, vertices_by_fibre[fibre], adjacency,
                    vertices, exceptional_supports, ordinary_supports,
                    disjoint_targets, vectors, H
                )
                exceptional_rows.append(options)
                exceptional_details.append(details)
            exceptional_option_cache[exceptional_cache_key] = (
                tuple(exceptional_rows), tuple(exceptional_details)
            )
        exceptional_option_rows, exceptional_details = (
            exceptional_option_cache[exceptional_cache_key]
        )

        cBc = 2 * sum(
            dot(c[vertex_index[tuple(edge[0])]], H,
                c[vertex_index[tuple(edge[1])]])
            for edge in representative["edges"]
        )
        cBc += 2 * sum(
            disjoint_targets[pair]
            * dot(vectors[pair[0]], H, vectors[pair[1]])
            for pair in disjoint_pairs
        )
        total_norm = 12 * 96 - cBc
        assert total_norm.denominator == 1 and total_norm >= 0
        total_norm = int(total_norm)

        collision_target = []
        for fibre in exceptional_supports:
            value = 0
            for left, right in itertools.combinations(vertices_by_fibre[fibre], 2):
                value += (
                    2 - len(set(vertices[left]) & set(vertices[right]))
                    - int(right in adjacency[left])
                )
            collision_target.append(value)
        collision_target = tuple(collision_target)
        target = (h_key, exceptional_option_rows, total_norm,
                  collision_target)
        target_histogram[(total_norm, collision_target)] += 1
        if target not in feasibility_cache:
            option_rows = tuple(sorted(
                exceptional_option_rows + ordinary_option_rows,
                key=len,
            ))
            feasibility_cache[target] = aggregate_feasible(
                option_rows, total_norm, collision_target
            )
        feasible, peak, final_states = feasibility_cache[target]

        macro = (entry["state_orbit_number"],
                 entry["signature_stabilizer_orbit_number"])
        stats = per_macro[macro]
        stats["input_orbits"] += 1
        stats["input_mass"] += representative["orbit_size"]
        if feasible:
            stats["passing_orbits"] += 1
            stats["passing_mass"] += representative["orbit_size"]
            survivors.append([
                representative["mask_hex"], representative["orbit_size"],
                representative["Q"], list(macro), total_norm,
                list(collision_target),
            ])
        else:
            stats["rejected_orbits"] += 1
            stats["rejected_mass"] += representative["orbit_size"]
        if len(controls) < 25:
            controls.append({
                "record_number": number,
                "macro": list(macro),
                "Gram_H": [[str(value) for value in values] for values in H],
                "total_q_norm_target": total_norm,
                "collision_target": list(collision_target),
                "exceptional_fibre_option_counts": [
                    len(options) for options in exceptional_option_rows
                ],
                "exceptional_fibre_details": exceptional_details,
                "feasible": feasible,
                "DP_peak_states": peak,
                "DP_final_states": final_states,
            })

    summary = {
        "input_local_orbits": len(row["representatives"]),
        "input_labelled_mass": sum(
            representative["orbit_size"]
            for representative in row["representatives"]
        ),
        "passing_local_orbits": len(survivors),
        "passing_labelled_mass": sum(record[1] for record in survivors),
        "rejected_local_orbits": (
            len(row["representatives"]) - len(survivors)
        ),
        "distinct_Gram_H": len(ordinary_option_cache),
        "distinct_exceptional_degree_frontiers": len(exceptional_option_cache),
        "distinct_norm_collision_targets": len(feasibility_cache),
        "elapsed_seconds": round(time.monotonic() - started, 6),
    }
    assert summary["input_local_orbits"] == 5_943
    assert summary["input_labelled_mass"] == 2_244_608
    result = {
        "status": "EXACT_SUPPORT_NORM_COLLISION_FILTER_COMPLETE",
        "inputs": {str(path): sha256(path)
                   for path in (LOCAL, CATALOG, GRAM)},
        "summary": summary,
        "per_macro": {
            f"{key[0]}:{key[1]}": dict(sorted(value.items()))
            for key, value in sorted(per_macro.items())
        },
        "ordinary_support_data": {
            str(ordinary): {
                "vertex_patterns": len(local_data[ordinary][0]),
                "fibre_configurations_by_Gram_H": [
                    len(ordinary_option_cache[h_key][
                        ordinary_supports.index(ordinary)
                    ])
                    for h_key in ordinary_option_cache
                ],
                "required_exceptional_group_counts": list(local_data[ordinary][2]),
            }
            for ordinary in ordinary_supports
        },
        "target_histogram": {
            f"norm={norm};collision={','.join(map(str, collision))}": count
            for (norm, collision), count in sorted(target_histogram.items())
        },
        "controls": controls,
        "survivor_fields": [
            "mask_hex", "orbit_size", "Q", "macro_state_and_signature",
            "total_q_norm_target", "collision_target_by_exceptional_fibre",
        ],
        "survivors": survivors,
        "checks": {
            "all_5943_local_orbits_classified_to_one_Gram_macro": True,
            "all_12_disjoint_exceptional_block_totals_used": True,
            "exceptional_disjoint_blocks_relaxed_to_row_degree_vectors": True,
            "total_q_norm_12_times_96_minus_c0_B_c0": True,
            "pointwise_root_group_identity_exact": True,
            "all_exceptional_and_ordinary_per_vertex_degree_vectors_enumerated": True,
            "all_four_vertex_column_sum_configurations_enumerated": True,
            "collision_totals_kept_per_exceptional_fibre": True,
            "SAT_or_SMT_used": False,
        },
        "claim_boundary": (
            "A rejection is an exact necessary-condition impossibility.  "
            "Exceptional disjoint blocks are relaxed to independent source-"
            "fibre row-degree configurations, so any true labelled block is "
            "included.  Passing does not supply compatible 4x4 blocks, "
            "labelled exception-to-ordinary maps, cross-fibre pair bounds, "
            "q-recurrence rows, or the remaining graph."
        ),
    }
    atomic_json(OUTPUT, result)
    print(json.dumps({"status": result["status"], **summary}, sort_keys=True))


if __name__ == "__main__":
    main()
