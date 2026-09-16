"""Solver-free pointwise-q CSP for the remaining source-150 frontier.

For every surviving local orbit this script:

* enumerates every labelled 4x4 matrix in the twelve disjoint exceptional
  blocks with both pointwise margin sequences;
* computes q=Bc on all exceptional vertices (fixed by those margins);
* enumerates, separately for each exceptional fibre, every possible
  pointwise q-load supplied by its seven disjoint ordinary C4 fibres; and
* imposes the four pointwise rows of (B+I)q=12c as a local constraint on the
  three disjoint exceptional blocks incident with that fibre.

The ordinary configuration chosen for a fibre is intentionally allowed to
differ when viewed from different exceptional fibres.  This is a relaxation,
so local-CSP rejection is rigorous.  Surviving local block assignments are
then checked simultaneously against every exceptional pair common-neighbour
upper bound.  No SAT/SMT package is used.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import time
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

import scratch_theory_e72_source150_disjoint_graphical_filter as graphical
import scratch_theory_e72_source150_fibre_recurrence_filter as recurrence
import scratch_theory_e72_source150_norm_collision_filter as base


LOCAL = base.LOCAL
CATALOG = base.CATALOG
GRAM = base.GRAM
FIBRE_FILTER = Path("scratch_theory_e72_source150_fibre_recurrence_filter.json")
OUTPUT = Path("scratch_theory_e72_source150_pointwise_recurrence_csp.json")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def atomic_json(path, value):
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, separators=(",", ":")) + "\n",
                         encoding="utf-8")
    temporary.replace(path)


def scale(value, vector):
    return tuple(value * coordinate for coordinate in vector)


def subtract(left, right):
    return tuple(a - b for a, b in zip(left, right))


def add(left, right):
    return tuple(a + b for a, b in zip(left, right))


def exact_number(value):
    value = Fraction(value)
    return int(value) if value.denominator == 1 else str(value)


def ordinary_configurations(patterns, disjoint):
    answer = set()
    for indices in itertools.combinations_with_replacement(
        range(len(patterns)), 4
    ):
        if all(sum(patterns[index][fibre] for index in indices) == 4
               for fibre in disjoint):
            answer.add(tuple(patterns[index] for index in indices))
    assert answer
    return tuple(sorted(answer))


def ordinary_factor_options(target_fibre, configurations, vectors, H):
    """Four labelled E-vertex loads supplied by one ordinary fibre."""

    answer = set()
    for configuration in configurations:
        repeated = []
        for pattern in configuration:
            q = base.add_vectors(
                scale(pattern[fibre], vectors[fibre])
                for fibre in range(len(vectors))
            )
            q_covector = recurrence.covector(q, H)
            repeated.extend([q_covector] * pattern[target_fibre])
        assert len(repeated) == 4
        for assigned in set(itertools.permutations(repeated)):
            answer.add(tuple(value for vector in assigned for value in vector))
    assert answer
    return tuple(sorted(answer))


def minkowski_sum(option_rows):
    if not option_rows:
        return {(Fraction(0),) * 12}, [1]
    states = {(Fraction(0),) * len(option_rows[0][0])}
    history = [1]
    for options in option_rows:
        states = {
            add(state, option) for state in states for option in options
        }
        history.append(len(states))
    return states, history


def build_ordinary_load_sets(ordinary_supports, ordinary_data,
                             exceptional_supports, vectors, H):
    configurations = {
        support: ordinary_configurations(
            ordinary_data[support][0], ordinary_data[support][1]
        )
        for support in ordinary_supports
    }
    load_sets = []
    details = []
    for target_fibre, target_support in enumerate(exceptional_supports):
        rows = []
        used = []
        for support in ordinary_supports:
            if set(target_support) & set(support):
                continue
            options = ordinary_factor_options(
                target_fibre, configurations[support], vectors, H
            )
            rows.append(options)
            used.append((support, len(options)))
        assert len(rows) == 7
        # Meet in the middle.  Materializing the full seven-factor sum can
        # be much larger than either half, while membership is all the local
        # CSP needs.  Greedily balance the raw domain products.
        left_rows = []
        right_rows = []
        left_product = 1
        right_product = 1
        for options in sorted(rows, key=len, reverse=True):
            if left_product <= right_product:
                left_rows.append(options)
                left_product *= len(options)
            else:
                right_rows.append(options)
                right_product *= len(options)
        left_states, left_history = minkowski_sum(tuple(left_rows))
        right_states, right_history = minkowski_sum(tuple(right_rows))
        load_sets.append((frozenset(left_states), frozenset(right_states)))
        details.append({
            "target_fibre": target_fibre,
            "ordinary_factor_option_counts": [
                [list(support), count] for support, count in used
            ],
            "left_Minkowski_state_history": left_history,
            "right_Minkowski_state_history": right_history,
            "left_states": len(left_states),
            "right_states": len(right_states),
        })
    return tuple(load_sets), tuple(details)


def ordinary_load_contains(meet_in_middle, target):
    left, right = meet_in_middle
    if len(left) > len(right):
        left, right = right, left
    return any(subtract(target, value) in right for value in left)


def pair_upper_affected(current, trial, affected, vertices):
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


def solve_block_csp(base_adjacency, block_rows, node_constraints,
                    incident, vertices, node_cap):
    """Backtracking with exact local recurrence tables and pair upper."""

    variable_count = len(block_rows)
    assignment = [-1] * variable_count
    nodes = 0
    # A variable order by domain size, then by the product of its endpoint
    # local table sizes.  This is deterministic and leaves no semantic gap.
    order = sorted(
        range(variable_count),
        key=lambda variable: (
            len(block_rows[variable]["options"]),
            len(node_constraints[block_rows[variable]["pair"][0]]),
            len(node_constraints[block_rows[variable]["pair"][1]]),
            variable,
        ),
    )

    def node_has_extension(fibre):
        variables = incident[fibre]
        for allowed in node_constraints[fibre]:
            if all(assignment[variable] < 0
                   or assignment[variable] == allowed[position]
                   for position, variable in enumerate(variables)):
                return True
        return False

    def recurse(depth, adjacency):
        nonlocal nodes
        if node_cap and nodes >= node_cap:
            return "UNKNOWN", None
        if depth == variable_count:
            return "SAT", tuple(assignment)
        variable = order[depth]
        pair = block_rows[variable]["pair"]
        for option_index, edges in enumerate(block_rows[variable]["options"]):
            nodes += 1
            if node_cap and nodes > node_cap:
                return "UNKNOWN", None
            assignment[variable] = option_index
            if not node_has_extension(pair[0]) or not node_has_extension(pair[1]):
                assignment[variable] = -1
                continue
            trial = [set(neighbours) for neighbours in adjacency]
            affected = set()
            for left, right in edges:
                trial[left].add(right)
                trial[right].add(left)
                affected.add(left)
                affected.add(right)
            if not pair_upper_affected(adjacency, trial, affected, vertices):
                assignment[variable] = -1
                continue
            status, witness = recurse(depth + 1, trial)
            if status != "UNSAT":
                assignment[variable] = -1
                return status, witness
            assignment[variable] = -1
        return "UNSAT", None

    status, witness = recurse(0, base_adjacency)
    return status, witness, nodes, order


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--stop", type=int)
    parser.add_argument("--indices")
    parser.add_argument("--node-cap", type=int, default=0)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    arguments = parser.parse_args()
    started = time.monotonic()

    document = json.loads(LOCAL.read_text(encoding="utf-8"))
    row = next(
        item for item in document["support_rows"]
        if item["partition"] == [2, 2, 2, 2, 1, 1, 1, 1]
        and item["compression_orbit_index"] == 0
    )
    exceptional_supports = tuple(tuple(item["support"])
                                 for item in row["exceptional_supports"])
    ordinary_supports = tuple(item for item in base.ALL_SUPPORTS
                              if item not in exceptional_supports)
    support_to_fibre = {support: index for index, support
                        in enumerate(exceptional_supports)}
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
    variable_of_pair = {pair: index for index, pair in enumerate(disjoint_pairs)}
    incident = tuple(
        tuple(variable_of_pair[pair] for pair in disjoint_pairs if fibre in pair)
        for fibre in range(8)
    )
    assert all(len(row) == 3 for row in incident)

    catalog = [entry for entry in json.loads(
        CATALOG.read_text(encoding="utf-8")
    )["macro_entries"] if entry["source_row_index"] == 150]
    entry_by_key = {
        base.entry_key(entry, exceptional_supports, overlap_pairs): entry
        for entry in catalog
    }
    gram_rows = {
        (entry["state_orbit_number"],
         entry["signature_stabilizer_orbit_number"],
         entry["signature_stabilizer_canonical"]): entry
        for entry in json.loads(GRAM.read_text(encoding="utf-8"))["rows"]
        if entry["source_row_index"] == 150
    }
    rejected_masks = {
        item["mask_hex"] for item in row["representatives"]
    } - {
        item[0] for item in json.loads(
            FIBRE_FILTER.read_text(encoding="utf-8")
        )["survivors"]
    }
    assert len(rejected_masks) == 1008

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
              if base.support(vertex) == support)
        for support in exceptional_supports
    )
    ordinary_data = {
        support: base.local_vertex_patterns(
            support, exceptional_supports, ordinary_supports
        )
        for support in ordinary_supports
    }

    ordinary_load_cache = {}
    records = [item for item in row["representatives"]
               if item["mask_hex"] not in rejected_masks]
    assert len(records) == 4935
    stop = len(records) if arguments.stop is None else arguments.stop
    if arguments.indices:
        requested_indices = tuple(int(value) for value
                                  in arguments.indices.split(","))
        selected_indexed = tuple((index, records[index])
                                 for index in requested_indices)
    else:
        selected_indexed = tuple(enumerate(
            records[arguments.start:stop], start=arguments.start
        ))
    status_histogram = Counter()
    per_macro = defaultdict(Counter)
    results = []
    controls = []

    for record_number, representative in selected_indexed:
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
        h_key = tuple(map(tuple, H))
        if h_key not in ordinary_load_cache:
            ordinary_load_cache[h_key] = build_ordinary_load_sets(
                ordinary_supports, ordinary_data, exceptional_supports,
                vectors, H
            )
        ordinary_load_sets, ordinary_details = ordinary_load_cache[h_key]

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
                    vertex, source, adjacency, vertices,
                    exceptional_supports, ordinary_supports
                )
                assert len(patterns) == 1
                degree_rows[vertex] = patterns[0]

        q_exceptional = []
        for vertex in range(len(vertices)):
            degrees = [0] * 8
            for other in adjacency[vertex]:
                degrees[support_to_fibre[base.support(vertices[other])]] += 1
            source = support_to_fibre[base.support(vertices[vertex])]
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

        base_needed = []
        for fibre, fibre_vertices in enumerate(vertices_by_fibre):
            rows = []
            for vertex in fibre_vertices:
                known_load = base.add_vectors(
                    q_exceptional[other] for other in adjacency[vertex]
                )
                raw = tuple(
                    12 * vectors[fibre][coordinate]
                    - q_exceptional[vertex][coordinate]
                    - known_load[coordinate]
                    for coordinate in range(3)
                )
                rows.append(recurrence.covector(raw, H))
            base_needed.append(tuple(value for row_value in rows
                                     for value in row_value))

        block_rows = []
        for pair in disjoint_pairs:
            left_fibre, right_fibre = pair
            left_vertices = vertices_by_fibre[left_fibre]
            right_vertices = vertices_by_fibre[right_fibre]
            margins_left = tuple(degree_rows[vertex][right_fibre]
                                 for vertex in left_vertices)
            margins_right = tuple(degree_rows[vertex][left_fibre]
                                  for vertex in right_vertices)
            assert sum(margins_left) == sum(margins_right) == block_totals[pair]
            options = []
            loads = {left_fibre: [], right_fibre: []}
            slacks = graphical.pair_slacks(adjacency, vertices)
            for mask in graphical.matrices_with_margins(
                margins_left, margins_right
            ):
                edges = graphical.matrix_edges(mask, left_vertices, right_vertices)
                if not graphical.single_block_pair_upper(
                    adjacency, slacks, edges
                ):
                    continue
                options.append(edges)
                for fibre, own_vertices, other_fibre in (
                    (left_fibre, left_vertices, right_fibre),
                    (right_fibre, right_vertices, left_fibre),
                ):
                    edge_lookup = defaultdict(list)
                    for left, right in edges:
                        edge_lookup[left].append(right)
                        edge_lookup[right].append(left)
                    fibre_load = []
                    for vertex in own_vertices:
                        value = base.add_vectors(
                            q_exceptional[other]
                            for other in edge_lookup[vertex]
                        )
                        fibre_load.extend(recurrence.covector(value, H))
                    loads[fibre].append(tuple(fibre_load))
            assert options
            block_rows.append({
                "pair": pair,
                "options": tuple(options),
                "loads": {fibre: tuple(rows)
                          for fibre, rows in loads.items()},
            })

        node_constraints = []
        local_product_counts = []
        for fibre in range(8):
            variables = incident[fibre]
            allowed = []
            products = 1
            for variable in variables:
                products *= len(block_rows[variable]["options"])
            local_product_counts.append(products)
            for choices in itertools.product(*(
                range(len(block_rows[variable]["options"]))
                for variable in variables
            )):
                supplied = (Fraction(0),) * 12
                for variable, option in zip(variables, choices):
                    supplied = add(
                        supplied,
                        block_rows[variable]["loads"][fibre][option],
                    )
                needed = subtract(base_needed[fibre], supplied)
                if ordinary_load_contains(ordinary_load_sets[fibre], needed):
                    allowed.append(tuple(choices))
            node_constraints.append(tuple(allowed))

        if any(not allowed for allowed in node_constraints):
            status, witness, nodes, order = "UNSAT", None, 0, []
            reason = "empty_local_pointwise_recurrence_table"
        else:
            status, witness, nodes, order = solve_block_csp(
                adjacency, tuple(block_rows), tuple(node_constraints),
                incident, vertices, arguments.node_cap
            )
            reason = (
                "simultaneous_CSP_exhausted" if status == "UNSAT"
                else "witness" if status == "SAT" else "node_cap"
            )
        status_histogram[status] += 1
        stats = per_macro[macro]
        stats["input_orbits"] += 1
        stats["input_mass"] += representative["orbit_size"]
        stats[f"{status}_orbits"] += 1
        stats[f"{status}_mass"] += representative["orbit_size"]
        results.append([
            record_number, representative["mask_hex"],
            representative["orbit_size"], representative["Q"], list(macro),
            status, reason, nodes,
        ])
        if len(controls) < 30:
            controls.append({
                "record_number": record_number,
                "macro": list(macro),
                "block_domain_sizes": [len(row["options"])
                                       for row in block_rows],
                "local_product_counts": local_product_counts,
                "local_allowed_counts": [len(row)
                                         for row in node_constraints],
                "status": status,
                "reason": reason,
                "DFS_nodes": nodes,
                "variable_order": order,
                "ordinary_load_details": ordinary_details,
            })

    summary = {
        "source150_fibre_recurrence_survivors": len(records),
        "slice_start": arguments.start,
        "slice_stop": stop,
        "input_orbits": len(selected_indexed),
        "input_mass": sum(item[2] for item in results),
        "status_histogram": dict(sorted(status_histogram.items())),
        "SAT_mass": sum(item[2] for item in results if item[5] == "SAT"),
        "UNSAT_mass": sum(item[2] for item in results if item[5] == "UNSAT"),
        "UNKNOWN_mass": sum(item[2] for item in results if item[5] == "UNKNOWN"),
        "distinct_Gram_H": len(ordinary_load_cache),
        "maximum_DFS_nodes": max((item[7] for item in results), default=0),
        "elapsed_seconds": round(time.monotonic() - started, 6),
    }
    result = {
        "status": "EXACT_POINTWISE_RECURRENCE_CSP_SLICE_COMPLETE",
        "inputs": {str(path): sha256(path)
                   for path in (LOCAL, CATALOG, GRAM, FIBRE_FILTER)},
        "summary": summary,
        "per_macro": {f"{key[0]}:{key[1]}": dict(sorted(value.items()))
                      for key, value in sorted(per_macro.items())},
        "controls": controls,
        "result_fields": [
            "survivor_index", "mask_hex", "orbit_size", "Q", "macro",
            "status", "reason", "DFS_nodes",
        ],
        "results": results,
        "checks": {
            "both_margin_sequences_exact_in_all_12_disjoint_blocks": True,
            "exceptional_pair_upper_checked_incrementally": True,
            "pointwise_q_recurrence_all_32_exceptional_vertices": True,
            "ordinary_fibre_configuration_synchronization_relaxed_between_E_fibres": True,
            "ordinary_exception_direction_used_is_one_sided_only": True,
            "UNSAT_only_after_empty_exact_table_or_exhaustive_DFS": True,
            "SAT_or_SMT_used": False,
        },
        "claim_boundary": (
            "UNSAT is rigorous.  SAT means only this relaxed local system has "
            "a witness; each ordinary fibre was allowed a different degree "
            "configuration for different exceptional target fibres."
        ),
    }
    atomic_json(arguments.output, result)
    print(json.dumps({"status": result["status"], **summary}, sort_keys=True))


if __name__ == "__main__":
    main()
