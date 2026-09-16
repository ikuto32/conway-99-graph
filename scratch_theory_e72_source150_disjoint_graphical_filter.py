"""Exact 4x4 graphical filter for source-150 disjoint exceptional blocks.

The fast E72 frontier stores the induced graph on the eight exceptional
fibres only on internal and overlapping-support blocks.  Full Gram fixes the
edge total in each of the twelve omitted disjoint-support blocks.  Pointwise
root-group counts actually fix the four row degrees on both ends of each
omitted block.  This script enumerates every 4x4 simple bipartite matrix with
those two degree sequences and applies all pair-common-neighbour upper bounds
visible from the known graph plus that one block.  Blocks are tested one at a
time, so passage is only a relaxation.  No SAT/SMT package is used.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import os
import time
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path

import scratch_theory_e72_source150_norm_collision_filter as base


LOCAL = base.LOCAL
OUTPUT = Path("scratch_theory_e72_source150_disjoint_graphical_filter.json")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def atomic_json(path, value):
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, separators=(",", ":")) + "\n",
                         encoding="utf-8")
    temporary.replace(path)


@lru_cache(maxsize=None)
def matrices_with_margins(rows, columns):
    """All 16-bit matrices with prescribed labelled row/column degrees."""

    row_masks = tuple(
        sum(1 << column for column in choice)
        for choice in itertools.combinations(range(4), rows[0])
    )
    choices = [row_masks]
    for degree in rows[1:]:
        choices.append(tuple(
            sum(1 << column for column in choice)
            for choice in itertools.combinations(range(4), degree)
        ))
    answer = []
    for selected in itertools.product(*choices):
        if all(sum((selected[row] >> column) & 1 for row in range(4))
                   == columns[column] for column in range(4)):
            answer.append(sum(selected[row] << (4 * row)
                              for row in range(4)))
    return tuple(answer)


def matrix_edges(mask, left_vertices, right_vertices):
    return tuple(
        (left_vertices[row], right_vertices[column])
        for row in range(4) for column in range(4)
        if (mask >> (4 * row + column)) & 1
    )


def pair_upper_holds(adjacency, vertices):
    for left, right in itertools.combinations(range(len(vertices)), 2):
        bound = (
            2 - len(set(vertices[left]) & set(vertices[right]))
            - int(right in adjacency[left])
        )
        if len(adjacency[left] & adjacency[right]) > bound:
            return False
    return True


def pair_slacks(adjacency, vertices):
    answer = {}
    for left, right in itertools.combinations(range(len(vertices)), 2):
        bound = (
            2 - len(set(vertices[left]) & set(vertices[right]))
            - int(right in adjacency[left])
        )
        answer[(left, right)] = (
            bound - len(adjacency[left] & adjacency[right])
        )
        assert answer[(left, right)] >= 0
    return answer


def single_block_pair_upper(adjacency, slacks, edges):
    """Incremental exact pair-upper test after adding one omitted block."""

    new_neighbours = defaultdict(set)
    edge_set = set()
    for left, right in edges:
        new_neighbours[left].add(right)
        new_neighbours[right].add(left)
        edge_set.add(tuple(sorted((left, right))))

    increments = Counter()
    # A newly inserted edge z--u makes z a new common witness for u and
    # every old neighbour of z.  Two new neighbours of z also gain z.
    for witness, new_rows in new_neighbours.items():
        for new_vertex in new_rows:
            for old_vertex in adjacency[witness]:
                if new_vertex != old_vertex:
                    increments[tuple(sorted((new_vertex, old_vertex)))] += 1
        for left, right in itertools.combinations(sorted(new_rows), 2):
            increments[(left, right)] += 1

    # A new adjacency lowers its allowed outer-common-neighbour count by one.
    for pair in set(increments) | edge_set:
        if increments[pair] + int(pair in edge_set) > slacks[pair]:
            return False
    return True


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
        item for item in base.ALL_SUPPORTS
        if item not in exceptional_supports
    )
    vertices = tuple(
        tuple(sorted((2 * first + bit_first, 2 * second + bit_second)))
        for first, second in exceptional_supports
        for bit_first, bit_second in itertools.product((0, 1), repeat=2)
    )
    vertex_index = {vertex: index for index, vertex in enumerate(vertices)}
    fibre_index = {fibre: index
                   for index, fibre in enumerate(exceptional_supports)}
    vertices_by_fibre = tuple(
        tuple(index for index, vertex in enumerate(vertices)
              if base.support(vertex) == fibre)
        for fibre in exceptional_supports
    )
    disjoint_pairs = tuple(
        pair for pair in itertools.combinations(range(8), 2)
        if not (set(exceptional_supports[pair[0]])
                & set(exceptional_supports[pair[1]]))
    )
    assert len(disjoint_pairs) == 12

    per_option_histogram = Counter()
    product_histogram = Counter()
    per_Q = defaultdict(Counter)
    controls = []
    survivors = []
    rejected_empty_margin = 0
    rejected_pair_upper = 0

    for number, representative in enumerate(row["representatives"]):
        adjacency = [set() for _ in vertices]
        for edge in representative["edges"]:
            left, right = (vertex_index[tuple(value)] for value in edge)
            adjacency[left].add(right)
            adjacency[right].add(left)
        assert pair_upper_holds(adjacency, vertices)
        slacks = pair_slacks(adjacency, vertices)

        block_totals = {
            tuple(sorted((int(left), int(right)))): int(value)
            for left, right, value
            in representative["disjoint_Gram_profile"]["targets"]
        }
        degree_rows = {}
        for source, fibre_vertices in enumerate(vertices_by_fibre):
            for vertex in fibre_vertices:
                patterns, disjoint, _ = base.exceptional_vertex_patterns(
                    vertex, source, adjacency, vertices,
                    exceptional_supports, ordinary_supports
                )
                assert len(patterns) == 1
                degree_rows[vertex] = patterns[0]

        option_counts = []
        reason = None
        for left_fibre, right_fibre in disjoint_pairs:
            left_vertices = vertices_by_fibre[left_fibre]
            right_vertices = vertices_by_fibre[right_fibre]
            rows = tuple(degree_rows[vertex][right_fibre]
                         for vertex in left_vertices)
            columns = tuple(degree_rows[vertex][left_fibre]
                            for vertex in right_vertices)
            assert sum(rows) == sum(columns) == block_totals[
                (left_fibre, right_fibre)
            ]
            raw = matrices_with_margins(rows, columns)
            if not raw:
                reason = "empty_margin"
                break
            valid = []
            for mask in raw:
                edges = matrix_edges(mask, left_vertices, right_vertices)
                if single_block_pair_upper(adjacency, slacks, edges):
                    valid.append(mask)
            if not valid:
                reason = "single_block_pair_upper"
                break
            option_counts.append(len(valid))
            per_option_histogram[(len(raw), len(valid))] += 1

        qstats = per_Q[representative["Q"]]
        qstats["input_orbits"] += 1
        qstats["input_mass"] += representative["orbit_size"]
        if reason is None:
            product = 1
            for count in option_counts:
                product *= count
            product_histogram[product] += 1
            qstats["passing_orbits"] += 1
            qstats["passing_mass"] += representative["orbit_size"]
            survivors.append([
                representative["mask_hex"], representative["orbit_size"],
                representative["Q"], option_counts, product,
            ])
        else:
            qstats["rejected_orbits"] += 1
            qstats["rejected_mass"] += representative["orbit_size"]
            if reason == "empty_margin":
                rejected_empty_margin += 1
            else:
                rejected_pair_upper += 1
        if len(controls) < 25:
            controls.append({
                "record_number": number,
                "mask_hex": representative["mask_hex"],
                "reason": reason,
                "option_counts_before_first_failure": option_counts,
            })

    summary = {
        "input_orbits": len(row["representatives"]),
        "input_mass": sum(item["orbit_size"] for item in row["representatives"]),
        "passing_orbits": len(survivors),
        "passing_mass": sum(item[1] for item in survivors),
        "rejected_empty_margin_orbits": rejected_empty_margin,
        "rejected_single_block_pair_upper_orbits": rejected_pair_upper,
        "distinct_margin_pairs": matrices_with_margins.cache_info().currsize,
        "elapsed_seconds": round(time.monotonic() - started, 6),
    }
    assert summary["input_orbits"] == 5943
    assert summary["input_mass"] == 2_244_608
    result = {
        "status": "EXACT_DISJOINT_BLOCK_GRAPHICAL_RELAXATION_COMPLETE",
        "inputs": {str(LOCAL): sha256(LOCAL)},
        "summary": summary,
        "per_Q": {str(key): dict(sorted(value.items()))
                  for key, value in sorted(per_Q.items())},
        "block_option_histogram_raw_then_pair_filtered": {
            f"{raw}:{valid}": count
            for (raw, valid), count in sorted(per_option_histogram.items())
        },
        "product_histogram_for_survivors": {
            str(key): value for key, value in sorted(product_histogram.items())
        },
        "controls": controls,
        "survivor_fields": [
            "mask_hex", "orbit_size", "Q",
            "valid_option_count_for_each_of_12_blocks", "option_product",
        ],
        "survivors": survivors,
        "checks": {
            "all_exceptional_vertex_degree_patterns_unique": True,
            "both_labelled_margin_sequences_imposed_per_block": True,
            "all_4x4_simple_matrices_with_those_margins_enumerated": True,
            "all_pair_upper_rows_checked_for_known_graph_plus_each_block": True,
            "ordinary_exception_direction_used_is_one_sided_only": True,
            "SAT_or_SMT_used": False,
        },
        "claim_boundary": (
            "A rejection is rigorous.  Passage only means each omitted block "
            "can separately be realized with its two degree sequences and "
            "the pair upper bounds visible one block at a time.  Simultaneous "
            "compatibility and pair witnesses involving two omitted blocks "
            "are not checked."
        ),
    }
    atomic_json(OUTPUT, result)
    print(json.dumps({"status": result["status"], **summary}, sort_keys=True))


if __name__ == "__main__":
    main()
