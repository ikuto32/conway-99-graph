"""Exact synchronized ordinary-config CSP for source-150 local graphs.

This strengthens ``scratch_theory_e72_source150_pointwise_recurrence_csp``.
The fibre-summed recurrence leaves only 64--2331 common choices of the
thirteen ordinary C4 degree configurations for each surviving Gram profile.
For each exceptional fibre and each choice of its three omitted E--E blocks,
this script computes the bitset of those global configuration choices for
which the four pointwise rows of (B+I)q=12c can be supplied by labelled
one-sided E--ordinary maps.  The eight bitsets must have a common member.

All twelve 4x4 E--E blocks are simultaneously materialized with both margin
sequences, and every exceptional pair common-neighbour upper bound is checked
during DFS.  Ordinary block maps for different exceptional fibres are
independent once their shared ordinary configuration is fixed, so this is
exact for the stated recurrence subsystem.  Pair bounds involving ordinary
vertices and the rest of the graph remain relaxed.  No SAT/SMT is used.
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
import scratch_theory_e72_source150_pointwise_recurrence_csp as relaxed


LOCAL = base.LOCAL
CATALOG = base.CATALOG
GRAM = base.GRAM
FIBRE_FILTER = relaxed.FIBRE_FILTER
CONFIG_FRONTIER = Path("scratch_theory_e72_source150_global_config_census.json")
OUTPUT = Path("scratch_theory_e72_source150_synchronized_config_csp.json")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def atomic_json(path, value):
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, separators=(",", ":")) + "\n",
                         encoding="utf-8")
    temporary.replace(path)


def scale(value, vector):
    return tuple(value * coordinate for coordinate in vector)


def add(left, right):
    return tuple(a + b for a, b in zip(left, right))


def subtract(left, right):
    return tuple(a - b for a, b in zip(left, right))


def sum_rows(rows, dimension=12):
    total = (Fraction(0),) * dimension
    for row in rows:
        total = add(total, row)
    return total


def minkowski(options_rows):
    dimension = len(options_rows[0][0]) if options_rows else 12
    states = {(Fraction(0),) * dimension}
    for options in options_rows:
        states = {add(state, option)
                  for state in states for option in options}
    return frozenset(states)


def conditional_factor_options(target_fibre, configuration, vectors, H):
    return relaxed.ordinary_factor_options(
        target_fibre, (configuration,), vectors, H
    )


def balanced_halves(option_rows):
    left = []
    right = []
    left_product = 1
    right_product = 1
    for options in sorted(option_rows, key=len, reverse=True):
        if left_product <= right_product:
            left.append(options)
            left_product *= len(options)
        else:
            right.append(options)
            right_product *= len(options)
    return minkowski(tuple(left)), minkowski(tuple(right))


def mitm_contains(halves, target):
    left, right = halves
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


def local_ordinary_pair_feasible(configuration, fibres, vertices_by_fibre,
                                 forbidden_pairs, mapping_cache):
    """Can one ordinary fibre realize all its one-sided E maps?

    ``forbidden_pairs`` are exceptional-vertex pairs whose remaining common
    ordinary-neighbour capacity is zero.  The U-side occupancies are the four
    rows of ``configuration``.  Only the forced E->U function direction is
    imposed; no U-side regularity or converse-function assumption is made.
    """

    domains = {}
    for fibre in fibres:
        counts = tuple(pattern[fibre] for pattern in configuration)
        if counts not in mapping_cache:
            destinations = tuple(position for position, count in enumerate(counts)
                                 for _ in range(count))
            assert len(destinations) == 4
            mapping_cache[counts] = tuple(sorted(set(
                itertools.permutations(destinations)
            )))
        own = vertices_by_fibre[fibre]
        domains[fibre] = tuple(
            mapping for mapping in mapping_cache[counts]
            if all(
                mapping[left] != mapping[right]
                or tuple(sorted((own[left], own[right]))) not in forbidden_pairs
                for left in range(4) for right in range(left + 1, 4)
            )
        )
        if not domains[fibre]:
            return False

    order = tuple(sorted(fibres, key=lambda fibre: (len(domains[fibre]), fibre)))

    # Quotient the arbitrary labels of U by permutations preserving every
    # exceptional-degree row of its fixed configuration.
    equal_row_groups = defaultdict(list)
    for position, pattern in enumerate(configuration):
        equal_row_groups[pattern].append(position)
    automorphisms = []
    for images in itertools.product(*(
        tuple(itertools.permutations(group))
        for group in equal_row_groups.values()
    )):
        permutation = list(range(4))
        for group, image in zip(equal_row_groups.values(), images):
            for source, target in zip(group, image):
                permutation[source] = target
        automorphisms.append(tuple(permutation))
    first = order[0]
    first_domain = tuple(
        mapping for mapping in domains[first]
        if mapping == min(
            tuple(permutation[value] for value in mapping)
            for permutation in automorphisms
        )
    )

    assignment = {}

    def visit(depth):
        if depth == len(order):
            return True
        fibre = order[depth]
        own = vertices_by_fibre[fibre]
        domain = first_domain if depth == 0 else domains[fibre]
        for mapping in domain:
            compatible = True
            for other_fibre, other_mapping in assignment.items():
                other = vertices_by_fibre[other_fibre]
                if any(
                    mapping[left] == other_mapping[right]
                    and tuple(sorted((own[left], other[right])))
                    in forbidden_pairs
                    for left in range(4) for right in range(4)
                ):
                    compatible = False
                    break
            if compatible:
                assignment[fibre] = mapping
                if visit(depth + 1):
                    return True
                del assignment[fibre]
        return False

    return visit(0)


def solve(base_adjacency, block_rows, node_tables, incident,
          all_config_bits, vertices, node_cap, leaf_filter=None,
          state_filter=None):
    assignment = [-1] * len(block_rows)
    nodes = 0
    order = sorted(
        range(len(block_rows)),
        key=lambda variable: (
            len(block_rows[variable]["options"]),
            len(node_tables[block_rows[variable]["pair"][0]]),
            len(node_tables[block_rows[variable]["pair"][1]]),
            variable,
        ),
    )

    def possible_bits(fibre, active_bits):
        variables = incident[fibre]
        answer = 0
        for choices, bits in node_tables[fibre].items():
            if not bits & active_bits:
                continue
            if all(assignment[variable] < 0
                   or assignment[variable] == choices[position]
                   for position, variable in enumerate(variables)):
                answer |= bits
        return answer & active_bits

    def recurse(depth, adjacency, active_bits):
        nonlocal nodes
        if node_cap and nodes >= node_cap:
            return "UNKNOWN", None
        if state_filter is not None:
            active_bits = state_filter(adjacency, active_bits)
            if not active_bits:
                return "UNSAT", None
        if depth == len(block_rows):
            bits = active_bits if leaf_filter is None else leaf_filter(
                adjacency, active_bits, tuple(assignment)
            )
            return (("SAT", (tuple(assignment), bits)) if bits
                    else ("UNSAT", None))
        variable = order[depth]
        endpoints = block_rows[variable]["pair"]
        for option_index, edges in enumerate(block_rows[variable]["options"]):
            nodes += 1
            if node_cap and nodes > node_cap:
                return "UNKNOWN", None
            assignment[variable] = option_index
            bits = active_bits
            for fibre in endpoints:
                bits = possible_bits(fibre, bits)
                if not bits:
                    break
            if not bits:
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
            status, witness = recurse(depth + 1, trial, bits)
            if status != "UNSAT":
                assignment[variable] = -1
                return status, witness
            assignment[variable] = -1
        return "UNSAT", None

    status, witness = recurse(0, base_adjacency, all_config_bits)
    return status, witness, nodes, order


def projected_block_problem(block_rows, node_tables, incident, selected):
    """Relax to selected E--E blocks, existentially projecting all others."""

    selected = tuple(selected)
    old_to_new = {old: new for new, old in enumerate(selected)}
    projected_rows = tuple(block_rows[old] for old in selected)
    projected_incident = []
    projected_tables = []
    for fibre, table in enumerate(node_tables):
        old_variables = incident[fibre]
        positions = tuple(
            position for position, variable in enumerate(old_variables)
            if variable in old_to_new
        )
        new_variables = tuple(old_to_new[old_variables[position]]
                              for position in positions)
        projected = defaultdict(int)
        for choices, bits in table.items():
            projected[tuple(choices[position] for position in positions)] |= bits
        projected_incident.append(new_variables)
        projected_tables.append(dict(projected))
    return (projected_rows, tuple(projected_tables),
            tuple(projected_incident))


def first_minimal_block_core(base_adjacency, block_rows, node_tables, incident,
                             all_config_bits, vertices, maximum_size):
    """Find the first cardinality-minimal UNSAT block projection, if small."""

    tests = 0
    nodes = 0
    for size in range(1, min(maximum_size, len(block_rows)) + 1):
        for selected in itertools.combinations(range(len(block_rows)), size):
            projected = projected_block_problem(
                block_rows, node_tables, incident, selected
            )
            status, _witness, used, _order = solve(
                base_adjacency, *projected, all_config_bits, vertices, 0
            )
            tests += 1
            nodes += used
            if status == "UNSAT":
                projections = []
                option_masks_by_block = []
                common_bits = all_config_bits
                for variable in selected:
                    endpoints = block_rows[variable]["pair"]
                    option_rows = []
                    union_bits = 0
                    for option in range(len(block_rows[variable]["options"])):
                        endpoint_bits = []
                        for fibre in endpoints:
                            position = incident[fibre].index(variable)
                            bits = 0
                            for choices, row_bits in node_tables[fibre].items():
                                if choices[position] == option:
                                    bits |= row_bits
                            endpoint_bits.append(bits)
                        allowed = endpoint_bits[0] & endpoint_bits[1]
                        union_bits |= allowed
                        option_rows.append([
                            index for index in range(all_config_bits.bit_length())
                            if allowed >> index & 1
                        ])
                    common_bits &= union_bits
                    option_masks_by_block.append(tuple(
                        sum(1 << index for index in row) for row in option_rows
                    ))
                    projections.append({
                        "block_index": variable,
                        "fibre_pair": list(endpoints),
                        "allowed_global_config_indices_by_block_option": option_rows,
                        "allowed_global_config_union": [
                            index for index in range(all_config_bits.bit_length())
                            if union_bits >> index & 1
                        ],
                    })
                endpoint_list = [endpoint for variable in selected
                                 for endpoint in block_rows[variable]["pair"]]
                independent_endpoints = len(set(endpoint_list)) == len(endpoint_list)
                option_diagnostics = []
                if independent_endpoints:
                    for option_tuple in itertools.product(*(
                        range(len(block_rows[variable]["options"]))
                        for variable in selected
                    )):
                        bits = all_config_bits
                        for masks, option in zip(option_masks_by_block,
                                                 option_tuple):
                            bits &= masks[option]
                        trial = [set(neighbours) for neighbours in base_adjacency]
                        for variable, option in zip(selected, option_tuple):
                            for left, right in block_rows[variable]["options"][option]:
                                trial[left].add(right)
                                trial[right].add(left)
                        violations = []
                        if bits:
                            for left, right in itertools.combinations(
                                    range(len(vertices)), 2):
                                bound = (
                                    2 - len(set(vertices[left])
                                            & set(vertices[right]))
                                    - int(right in trial[left])
                                )
                                common = trial[left] & trial[right]
                                if len(common) > bound:
                                    violations.append({
                                        "vertex_indices": [left, right],
                                        "vertex_labels": [list(vertices[left]),
                                                          list(vertices[right])],
                                        "bound": bound,
                                        "common_neighbour_count": len(common),
                                        "common_neighbour_indices": sorted(common),
                                    })
                        option_diagnostics.append({
                            "block_option_indices": list(option_tuple),
                            "common_global_config_indices": [
                                index for index in range(all_config_bits.bit_length())
                                if bits >> index & 1
                            ],
                            "pair_upper_violations": violations,
                        })
                return {
                    "block_indices": list(selected),
                    "block_fibre_pairs": [list(block_rows[index]["pair"])
                                          for index in selected],
                    "cardinality": size,
                    "subset_tests": tests,
                    "subset_DFS_nodes": nodes,
                    "block_config_projections": projections,
                    "common_global_config_indices_across_block_unions": [
                        index for index in range(all_config_bits.bit_length())
                        if common_bits >> index & 1
                    ],
                    "blocks_have_pairwise_disjoint_endpoint_fibres": (
                        independent_endpoints
                    ),
                    "block_option_diagnostics": option_diagnostics,
                }
    return {
        "block_indices": [],
        "block_fibre_pairs": [],
        "cardinality": None,
        "subset_tests": tests,
        "subset_DFS_nodes": nodes,
        "block_config_projections": [],
        "common_global_config_indices_across_block_unions": [],
        "blocks_have_pairwise_disjoint_endpoint_fibres": None,
        "block_option_diagnostics": [],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--macros", default="3:0,8:0")
    parser.add_argument("--start", type=int, default=0)
    parser.add_argument("--stop", type=int)
    parser.add_argument(
        "--records",
        default="",
        help="comma-separated macro-local record indices (overrides start/stop)",
    )
    parser.add_argument("--node-cap", type=int, default=0)
    parser.add_argument("--ordinary-local-pair", action="store_true")
    parser.add_argument("--ordinary-local-pair-every-depth", action="store_true")
    parser.add_argument("--ordinary-joint-map", action="store_true")
    parser.add_argument("--joint-map-node-cap", type=int, default=0)
    parser.add_argument("--block-core-max-size", type=int, default=0)
    parser.add_argument(
        "--fixed-block-projection",
        default="",
        help=(
            "comma-separated E--E block indices; solve only their exact "
            "existential projection, so UNSAT remains a valid exclusion"
        ),
    )
    parser.add_argument("--output", type=Path, default=OUTPUT)
    arguments = parser.parse_args()
    fixed_block_projection = tuple(
        int(value) for value in arguments.fixed_block_projection.split(",")
        if value
    )
    assert len(set(fixed_block_projection)) == len(fixed_block_projection)
    wanted_macros = {
        tuple(map(int, value.split(":")))
        for value in arguments.macros.split(",") if value
    }
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
    assert all(0 <= value < len(disjoint_pairs)
               for value in fixed_block_projection)
    incident = tuple(
        tuple(variable_of_pair[pair] for pair in disjoint_pairs if fibre in pair)
        for fibre in range(8)
    )

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

    fibre_survivor_masks = {
        item[0] for item in json.loads(
            FIBRE_FILTER.read_text(encoding="utf-8")
        )["survivors"]
    }
    records = []
    for representative in row["representatives"]:
        if representative["mask_hex"] not in fibre_survivor_masks:
            continue
        entry = entry_by_key[base.representative_key(
            representative["edges"], support_to_fibre, overlap_pairs
        )]
        macro = (entry["state_orbit_number"],
                 entry["signature_stabilizer_orbit_number"])
        if macro in wanted_macros:
            records.append((representative, entry, macro))
    requested_records = tuple(
        int(value) for value in arguments.records.split(",") if value
    )
    assert len(set(requested_records)) == len(requested_records)
    if requested_records:
        assert all(0 <= value < len(records) for value in requested_records)
        selected_record_numbers = requested_records
        selected = [records[value] for value in requested_records]
        stop = arguments.stop
    else:
        stop = len(records) if arguments.stop is None else arguments.stop
        selected = records[arguments.start:stop]
        selected_record_numbers = tuple(range(arguments.start, stop))

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

    config_document = json.loads(CONFIG_FRONTIER.read_text(encoding="utf-8"))
    config_by_H = {
        tuple(tuple(Fraction(value) for value in row)
              for row in item["Gram_H"]): item
        for item in config_document["results"]
    }
    conditional_factor_cache = {}
    projection_cache = {}
    mitm_cache = {}
    target_bits_cache = {}

    status_histogram = Counter()
    per_macro = defaultdict(Counter)
    controls = []
    results = []
    membership_tests = 0
    membership_cache_hits = 0
    local_pair_factor_tests = 0
    local_pair_factor_cache_hits = 0
    local_pair_filter_calls = 0
    local_pair_cache = {}
    mapping_cache = {}
    local_pair_terminal_failure_supports = Counter()
    local_pair_config_bits_removed = 0
    joint_map_calls = 0
    joint_map_nodes = 0
    joint_map_unknowns = 0
    block_cores = []

    for offset, (representative, entry, macro) in enumerate(selected):
        record_filter_calls_before = local_pair_filter_calls
        record_factor_tests_before = local_pair_factor_tests
        record_number = selected_record_numbers[offset]
        gram = gram_rows[macro + (
            entry["signature_stabilizer_canonical"],
        )]
        H = tuple(tuple(Fraction(value) for value in row)
                  for row in gram["unique_H"])
        h_key = tuple(map(tuple, H))
        frontier = config_by_H[h_key]
        configurations = tuple(
            tuple(tuple(tuple(int(value) for value in pattern)
                        for pattern in config)
                  for config in row_configs)
            for row_configs in frontier["configurations"]
        )
        global_solutions = tuple(tuple(solution) for solution
                                 in frontier["configuration_index_solutions"])
        all_config_bits = (1 << len(global_solutions)) - 1

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
            rows_needed = []
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
                rows_needed.append(recurrence.covector(raw, H))
            base_needed.append(tuple(value for row_value in rows_needed
                                     for value in row_value))

        block_rows = []
        for pair in disjoint_pairs:
            left_fibre, right_fibre = pair
            left_vertices = vertices_by_fibre[left_fibre]
            right_vertices = vertices_by_fibre[right_fibre]
            rows = tuple(degree_rows[vertex][right_fibre]
                         for vertex in left_vertices)
            columns = tuple(degree_rows[vertex][left_fibre]
                            for vertex in right_vertices)
            assert sum(rows) == sum(columns) == block_totals[pair]
            options = []
            loads = {left_fibre: [], right_fibre: []}
            slacks = graphical.pair_slacks(adjacency, vertices)
            for mask in graphical.matrices_with_margins(rows, columns):
                edges = graphical.matrix_edges(mask, left_vertices, right_vertices)
                if not graphical.single_block_pair_upper(
                    adjacency, slacks, edges
                ):
                    continue
                options.append(edges)
                edge_lookup = defaultdict(list)
                for left, right in edges:
                    edge_lookup[left].append(right)
                    edge_lookup[right].append(left)
                for fibre, own_vertices in (
                    (left_fibre, left_vertices),
                    (right_fibre, right_vertices),
                ):
                    load = []
                    for vertex in own_vertices:
                        value = base.add_vectors(
                            q_exceptional[other]
                            for other in edge_lookup[vertex]
                        )
                        load.extend(recurrence.covector(value, H))
                    loads[fibre].append(tuple(load))
            assert options
            block_rows.append({
                "pair": pair,
                "options": tuple(options),
                "loads": {fibre: tuple(value)
                          for fibre, value in loads.items()},
            })

        # Group the global configuration solutions by the seven config
        # indices visible from each exceptional fibre.
        projection_groups = []
        visible_ordinary = []
        for fibre, support in enumerate(exceptional_supports):
            used = tuple(index for index, ordinary in enumerate(ordinary_supports)
                         if not set(support) & set(ordinary))
            assert len(used) == 7
            visible_ordinary.append(used)
            cache_key = (h_key, fibre)
            if cache_key not in projection_cache:
                groups = defaultdict(int)
                for solution_index, solution in enumerate(global_solutions):
                    projection = tuple(solution[index] for index in used)
                    groups[projection] |= 1 << solution_index
                projection_cache[cache_key] = tuple(sorted(groups.items()))
            projection_groups.append(projection_cache[cache_key])

        node_tables = []
        unique_target_counts = []
        for fibre in range(8):
            variables = incident[fibre]
            choices_by_target = defaultdict(list)
            for choices in itertools.product(*(
                range(len(block_rows[variable]["options"]))
                for variable in variables
            )):
                supplied = sum_rows(
                    block_rows[variable]["loads"][fibre][choice]
                    for variable, choice in zip(variables, choices)
                )
                target = subtract(base_needed[fibre], supplied)
                choices_by_target[target].append(tuple(choices))
            unique_target_counts.append(len(choices_by_target))

            table = {}
            used = visible_ordinary[fibre]
            for target, choice_rows in choices_by_target.items():
                target_key = (h_key, fibre, target)
                if target_key in target_bits_cache:
                    bits = target_bits_cache[target_key]
                else:
                    bits = 0
                    for projection, projection_bits in projection_groups[fibre]:
                        key = (h_key, fibre, projection)
                        if key not in mitm_cache:
                            option_rows = []
                            for ordinary_index, config_index in zip(used, projection):
                                factor_key = (
                                    h_key, fibre, ordinary_index, config_index
                                )
                                if factor_key not in conditional_factor_cache:
                                    conditional_factor_cache[factor_key] = (
                                        conditional_factor_options(
                                            fibre,
                                            configurations[ordinary_index][config_index],
                                            vectors, H,
                                        )
                                    )
                                option_rows.append(
                                    conditional_factor_cache[factor_key]
                                )
                            mitm_cache[key] = balanced_halves(tuple(option_rows))
                        membership_key = (key, target)
                        # Store membership booleans in the same cache with a
                        # tagged key; tuple shapes keep the namespaces disjoint.
                        tagged = ("membership",) + membership_key
                        if tagged in mitm_cache:
                            membership_cache_hits += 1
                            feasible = mitm_cache[tagged]
                        else:
                            membership_tests += 1
                            feasible = mitm_contains(mitm_cache[key], target)
                            mitm_cache[tagged] = feasible
                        if feasible:
                            bits |= projection_bits
                    target_bits_cache[target_key] = bits
                if bits:
                    for choices in choice_rows:
                        table[choices] = bits
            node_tables.append(table)

        # For each ordinary fibre and configuration choice, collect the
        # global-config bitset carrying that choice.  At a complete E--E
        # assignment the optional leaf filter applies the residual-zero
        # exceptional-pair collision condition independently inside U.
        config_choice_bits = []
        for ordinary_index in range(len(ordinary_supports)):
            groups = defaultdict(int)
            for solution_index, solution in enumerate(global_solutions):
                groups[solution[ordinary_index]] |= 1 << solution_index
            config_choice_bits.append(tuple(sorted(groups.items())))

        def ordinary_local_pair_filter(complete_adjacency, active_bits,
                                       _assignment=None):
            nonlocal local_pair_factor_tests, local_pair_factor_cache_hits
            nonlocal local_pair_filter_calls
            nonlocal local_pair_config_bits_removed
            local_pair_filter_calls += 1
            bits = active_bits
            for ordinary_index, ordinary_support in enumerate(ordinary_supports):
                fibres = tuple(
                    fibre for fibre, support in enumerate(exceptional_supports)
                    if not set(support) & set(ordinary_support)
                )
                if not fibres:
                    continue
                relevant_vertices = tuple(
                    vertex for fibre in fibres
                    for vertex in vertices_by_fibre[fibre]
                )
                forbidden = frozenset(
                    (left, right)
                    for left, right in itertools.combinations(relevant_vertices, 2)
                    if (
                        2 - len(set(vertices[left]) & set(vertices[right]))
                        - int(right in complete_adjacency[left])
                        - len(complete_adjacency[left]
                              & complete_adjacency[right])
                    ) == 0
                )
                allowed = 0
                for config_choice, group_bits in config_choice_bits[ordinary_index]:
                    if not group_bits & bits:
                        continue
                    configuration = configurations[ordinary_index][config_choice]
                    cache_key = (ordinary_index, config_choice, forbidden)
                    if cache_key in local_pair_cache:
                        local_pair_factor_cache_hits += 1
                        feasible = local_pair_cache[cache_key]
                    else:
                        local_pair_factor_tests += 1
                        feasible = local_ordinary_pair_feasible(
                            configuration, fibres, vertices_by_fibre,
                            forbidden, mapping_cache,
                        )
                        local_pair_cache[cache_key] = feasible
                    if feasible:
                        allowed |= group_bits
                preceding_bits = bits
                bits &= allowed
                local_pair_config_bits_removed += (
                    preceding_bits.bit_count() - bits.bit_count()
                )
                if not bits:
                    local_pair_terminal_failure_supports[
                        ordinary_support
                    ] += 1
                    return 0
            return bits

        def ordinary_joint_map_filter(complete_adjacency, active_bits,
                                      complete_assignment):
            """Require one common set of U maps for recurrence and collisions."""

            nonlocal joint_map_calls, joint_map_nodes, joint_map_unknowns
            import scratch_theory_e72_source150_map_collision_probe as map_probe

            bits = ordinary_local_pair_filter(
                complete_adjacency, active_bits, complete_assignment
            )
            if not bits:
                return 0
            instance = {
                "assignment": complete_assignment,
                "global_solutions": global_solutions,
                "configurations": configurations,
                "exceptional": exceptional_supports,
                "ordinary": ordinary_supports,
                "vectors": vectors,
                "H": H,
                "vertices": vertices,
                "by_fibre": vertices_by_fibre,
                "adjacency": complete_adjacency,
                "base_needed": tuple(base_needed),
                "block_rows": tuple(
                    (value["pair"], value["options"], value["loads"])
                    for value in block_rows
                ),
            }
            allowed = 0
            for config_index in range(len(global_solutions)):
                bit = 1 << config_index
                if not bits & bit:
                    continue
                joint_map_calls += 1
                result = map_probe.joint_factor_search(
                    instance, config_index, arguments.joint_map_node_cap
                )
                joint_map_nodes += result["nodes"]
                if result["status"] == "UNKNOWN":
                    joint_map_unknowns += 1
                    allowed |= bit
                elif result["status"] == "SAT":
                    allowed |= bit
            return allowed

        if any(not table for table in node_tables):
            status, witness, nodes, order = "UNSAT", None, 0, []
            reason = "empty_synchronized_pointwise_table"
        elif fixed_block_projection:
            projected = projected_block_problem(
                tuple(block_rows), tuple(node_tables), incident,
                fixed_block_projection,
            )
            status, witness, nodes, order = solve(
                adjacency, *projected, all_config_bits, vertices,
                arguments.node_cap,
            )
            reason = (
                "fixed_block_projection_witness" if status == "SAT"
                else "node_cap" if status == "UNKNOWN"
                else "fixed_block_projection_exhausted"
            )
        else:
            status, witness, nodes, order = solve(
                adjacency, tuple(block_rows), tuple(node_tables), incident,
                all_config_bits, vertices, arguments.node_cap,
                (ordinary_joint_map_filter
                 if arguments.ordinary_joint_map else
                 ordinary_local_pair_filter
                 if arguments.ordinary_local_pair else None),
                (ordinary_local_pair_filter
                 if arguments.ordinary_local_pair_every_depth else None),
            )
            reason = (
                "witness" if status == "SAT"
                else "node_cap" if status == "UNKNOWN"
                else "simultaneous_CSP_exhausted"
            )
        status_histogram[status] += 1
        if status == "UNSAT" and arguments.block_core_max_size:
            core = first_minimal_block_core(
                adjacency, tuple(block_rows), tuple(node_tables), incident,
                all_config_bits, vertices, arguments.block_core_max_size,
            )
            core.update({
                "record_number": record_number,
                "macro": list(macro),
                "fibre_supports": [list(support)
                                   for support in exceptional_supports],
            })
            block_cores.append(core)
        stats = per_macro[macro]
        stats["input_orbits"] += 1
        stats["input_mass"] += representative["orbit_size"]
        stats[f"{status}_orbits"] += 1
        stats[f"{status}_mass"] += representative["orbit_size"]
        results.append([
            record_number, representative["mask_hex"],
            representative["orbit_size"], representative["Q"], list(macro),
            status, reason, nodes,
            ([] if witness is None else list(witness[0])),
            ([] if witness is None else [
                index for index in range(len(global_solutions))
                if witness[1] >> index & 1
            ]),
            local_pair_filter_calls - record_filter_calls_before,
            local_pair_factor_tests - record_factor_tests_before,
        ])
        if len(controls) < 24:
            controls.append({
                "record_number": record_number,
                "macro": list(macro),
                "global_config_solutions": len(global_solutions),
                "projection_group_counts": [len(value)
                                            for value in projection_groups],
                "block_domain_sizes": [len(value["options"])
                                       for value in block_rows],
                "unique_pointwise_targets": unique_target_counts,
                "node_table_sizes": [len(value) for value in node_tables],
                "status": status,
                "reason": reason,
                "DFS_nodes": nodes,
                "variable_order": order,
                "witness_config_bit_count": (
                    0 if witness is None else witness[1].bit_count()
                ),
            })

    summary = {
        "wanted_macros": [list(value) for value in sorted(wanted_macros)],
        "available_orbits_in_wanted_macros": len(records),
        "slice_start": arguments.start,
        "slice_stop": stop,
        "explicit_record_selection": list(requested_records),
        "input_orbits": len(selected),
        "input_mass": sum(item[2] for item in results),
        "status_histogram": dict(sorted(status_histogram.items())),
        "SAT_mass": sum(item[2] for item in results if item[5] == "SAT"),
        "UNSAT_mass": sum(item[2] for item in results if item[5] == "UNSAT"),
        "UNKNOWN_mass": sum(item[2] for item in results if item[5] == "UNKNOWN"),
        "membership_tests": membership_tests,
        "membership_cache_hits": membership_cache_hits,
        "conditional_factor_cache_entries": len(conditional_factor_cache),
        "MITM_cache_entries_including_memberships": len(mitm_cache),
        "target_config_bitset_cache_entries": len(target_bits_cache),
        "maximum_DFS_nodes": max((item[7] for item in results), default=0),
        "elapsed_seconds": round(time.monotonic() - started, 6),
        "ordinary_local_pair_filter_enabled": arguments.ordinary_local_pair,
        "ordinary_local_pair_every_depth_enabled": (
            arguments.ordinary_local_pair_every_depth
        ),
        "ordinary_local_pair_filter_calls": local_pair_filter_calls,
        "ordinary_local_pair_factor_tests": local_pair_factor_tests,
        "ordinary_local_pair_factor_cache_hits": local_pair_factor_cache_hits,
        "ordinary_local_pair_cache_entries": len(local_pair_cache),
        "ordinary_local_pair_config_bits_removed": local_pair_config_bits_removed,
        "ordinary_local_pair_terminal_failure_supports": {
            str(list(key)): value for key, value
            in sorted(local_pair_terminal_failure_supports.items())
        },
        "ordinary_joint_map_filter_enabled": arguments.ordinary_joint_map,
        "ordinary_joint_map_calls": joint_map_calls,
        "ordinary_joint_map_nodes": joint_map_nodes,
        "ordinary_joint_map_unknowns_relaxed_as_pass": joint_map_unknowns,
        "small_block_core_probe_enabled": bool(arguments.block_core_max_size),
        "fixed_block_projection": list(fixed_block_projection),
        "small_block_cores_found": sum(
            core["cardinality"] is not None for core in block_cores
        ),
    }
    result = {
        "status": "EXACT_SYNCHRONIZED_CONFIG_CSP_SLICE_COMPLETE",
        "inputs": {str(path): sha256(path) for path in (
            LOCAL, CATALOG, GRAM, FIBRE_FILTER, CONFIG_FRONTIER
        )},
        "summary": summary,
        "per_macro": {f"{key[0]}:{key[1]}": dict(sorted(value.items()))
                      for key, value in sorted(per_macro.items())},
        "controls": controls,
        "result_fields": [
            "macro_local_index", "mask_hex", "orbit_size", "Q", "macro",
            "status", "reason", "DFS_nodes", "witness_block_option_indices",
            "witness_global_configuration_indices",
            "ordinary_local_pair_filter_calls",
            "ordinary_local_pair_new_factor_tests",
        ],
        "results": results,
        "small_block_cores": block_cores,
        "checks": {
            "all_global_fibre_summed_configuration_solutions_used": True,
            "ordinary_configuration_identity_synchronized_across_E_fibres": True,
            "all_labelled_one_sided_E_to_ordinary_maps_enumerated": True,
            "both_margins_in_all_12_EE_blocks": True,
            "all_32_exceptional_pointwise_q_rows": True,
            "all_exceptional_pair_upper_rows": True,
            "fixed_block_projection_is_existential_relaxation": bool(
                fixed_block_projection
            ),
            "ordinary_local_pair_residual_zero_filter": (
                arguments.ordinary_local_pair
                or arguments.ordinary_local_pair_every_depth
                or arguments.ordinary_joint_map
            ),
            "ordinary_joint_maps_share_recurrence_and_collision_witness": (
                arguments.ordinary_joint_map
            ),
            "SAT_or_SMT_used": False,
        },
        "claim_boundary": (
            "UNSAT is an exact local exclusion.  SAT only realizes the "
            "exceptional induced graph and q recurrence with synchronized "
            "ordinary degree configurations; ordinary pair bounds and the "
            "remaining graph are not constructed."
        ),
    }
    atomic_json(arguments.output, result)
    print(json.dumps({"status": result["status"], **summary}, sort_keys=True))


if __name__ == "__main__":
    main()
