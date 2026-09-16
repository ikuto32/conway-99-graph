"""Solver-free DFS for the twelve source-150 disjoint E--E blocks.

This is an exploratory strengthening of the independent-block graphical
filter.  It realizes all twelve 4x4 blocks simultaneously and maintains all
outer pair-common-neighbour upper bounds on the 32 exceptional vertices.
The search stops at the first witness for each stored local orbit.  A node
cap is available only as an explicit UNKNOWN outcome; UNSAT is reported only
after exhaustive DFS.
"""

from __future__ import annotations

import argparse
import itertools
import json
import time
from collections import Counter

import scratch_theory_e72_source150_disjoint_graphical_filter as graph
import scratch_theory_e72_source150_norm_collision_filter as base


def affected_pair_upper(adjacency, trial, affected, vertices):
    pairs = set()
    for left in affected:
        for right in range(len(vertices)):
            if left != right:
                pairs.add(tuple(sorted((left, right))))
    for left, right in pairs:
        bound = (
            2 - len(set(vertices[left]) & set(vertices[right]))
            - int(right in trial[left])
        )
        if len(trial[left] & trial[right]) > bound:
            return False
    return True


def first_completion(adjacency, block_rows, vertices, node_cap):
    nodes = 0
    # Small domains first.  Ties prioritize blocks touching many other
    # low-domain blocks only implicitly; this simple order is deterministic.
    block_rows = tuple(sorted(block_rows, key=lambda row: (len(row[2]), row[0])))

    def recurse(depth, current):
        nonlocal nodes
        if node_cap and nodes >= node_cap:
            return "UNKNOWN", None
        if depth == len(block_rows):
            return "SAT", current
        _, _, options = block_rows[depth]
        saw_unknown = False
        for edges in options:
            nodes += 1
            if node_cap and nodes > node_cap:
                return "UNKNOWN", None
            trial = [set(neighbours) for neighbours in current]
            affected = set()
            for left, right in edges:
                trial[left].add(right)
                trial[right].add(left)
                affected.add(left)
                affected.add(right)
            if not affected_pair_upper(current, trial, affected, vertices):
                continue
            status, witness = recurse(depth + 1, trial)
            if status == "SAT":
                return status, witness
            if status == "UNKNOWN":
                saw_unknown = True
                break
        return ("UNKNOWN", None) if saw_unknown else ("UNSAT", None)

    status, witness = recurse(0, adjacency)
    return status, witness, nodes, [len(row[2]) for row in block_rows]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--stop", type=int, default=100)
    parser.add_argument("--node-cap", type=int, default=100000)
    arguments = parser.parse_args()
    started = time.monotonic()

    document = json.loads(base.LOCAL.read_text(encoding="utf-8"))
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
    disjoint_pairs = tuple(
        pair for pair in itertools.combinations(range(8), 2)
        if not set(exceptional_supports[pair[0]])
        & set(exceptional_supports[pair[1]])
    )

    records = row["representatives"][arguments.start:arguments.stop]
    histogram = Counter()
    results = []
    for offset, representative in enumerate(records):
        adjacency = [set() for _ in vertices]
        for edge in representative["edges"]:
            left, right = (vertex_index[tuple(value)] for value in edge)
            adjacency[left].add(right)
            adjacency[right].add(left)
        targets = {
            tuple(sorted((int(left), int(right)))): int(value)
            for left, right, value
            in representative["disjoint_Gram_profile"]["targets"]
        }
        degrees = {}
        for source, fibre_vertices in enumerate(vertices_by_fibre):
            for vertex in fibre_vertices:
                patterns, _, _ = base.exceptional_vertex_patterns(
                    vertex, source, adjacency, vertices,
                    exceptional_supports, ordinary_supports
                )
                assert len(patterns) == 1
                degrees[vertex] = patterns[0]

        block_rows = []
        for left_fibre, right_fibre in disjoint_pairs:
            left_vertices = vertices_by_fibre[left_fibre]
            right_vertices = vertices_by_fibre[right_fibre]
            rows = tuple(degrees[vertex][right_fibre]
                         for vertex in left_vertices)
            columns = tuple(degrees[vertex][left_fibre]
                            for vertex in right_vertices)
            assert sum(rows) == sum(columns) == targets[
                (left_fibre, right_fibre)
            ]
            options = []
            slacks = graph.pair_slacks(adjacency, vertices)
            for mask in graph.matrices_with_margins(rows, columns):
                edges = graph.matrix_edges(mask, left_vertices, right_vertices)
                if graph.single_block_pair_upper(adjacency, slacks, edges):
                    options.append(edges)
            assert options
            block_rows.append(((left_fibre, right_fibre),
                               (rows, columns), tuple(options)))

        status, witness, nodes, domains = first_completion(
            adjacency, tuple(block_rows), vertices, arguments.node_cap
        )
        histogram[status] += 1
        results.append({
            "record_number": arguments.start + offset,
            "mask_hex": representative["mask_hex"],
            "orbit_size": representative["orbit_size"],
            "Q": representative["Q"],
            "status": status,
            "nodes": nodes,
            "sorted_domain_sizes": domains,
        })

    print(json.dumps({
        "slice": [arguments.start, arguments.stop],
        "node_cap": arguments.node_cap,
        "status_histogram": dict(histogram),
        "node_histogram": dict(Counter(item["nodes"] for item in results)),
        "maximum_nodes": max((item["nodes"] for item in results), default=0),
        "elapsed_seconds": round(time.monotonic() - started, 6),
        "results": results,
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
