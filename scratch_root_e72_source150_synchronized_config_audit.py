"""Independent audit of the source-150 synchronized-configuration CSP.

The synchronized CSP and global-frontier producers are not imported.  This
audit reconstructs the four ordinary-configuration frontiers, all labelled
one-sided ordinary--exceptional maps, all twelve disjoint exceptional 4x4
blocks with both margins, and an independent complete block DFS for macros
3:0 and 8:0.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

import scratch_root_e72_source150_norm_collision_audit as base


LOCAL = base.LOCAL
CATALOG = base.CATALOG
GRAM = base.GRAM
FIBRE_FILTER = Path("scratch_theory_e72_source150_fibre_recurrence_filter.json")
FIBRE_AUDIT = Path("scratch_root_e72_source150_fibre_recurrence_audit.json")
GLOBAL_SCRIPT = Path("scratch_theory_e72_source150_global_config_census.py")
GLOBAL_OUTPUT = Path("scratch_theory_e72_source150_global_config_census.json")
SYNC_SCRIPT = Path("scratch_theory_e72_source150_synchronized_config_csp.py")
SYNC_OUTPUTS = (
    Path("scratch_theory_e72_source150_synchronized_m30.json"),
    Path("scratch_root_e72_source150_sync_m80.json"),
)
LOCALPAIR_OUTPUTS = (
    Path("scratch_theory_e72_source150_sync_localpair_m30.json"),
    Path("scratch_root_e72_source150_sync_localpair_m80_rebound.json"),
)
OUTPUT = Path("scratch_root_e72_source150_synchronized_config_audit.json")
REPORT = Path("scratch_root_e72_source150_synchronized_config_audit.md")

FRONTIER_MACROS = ((0, 0), (0, 1), (0, 3), (8, 0))
AUDITED_MACROS = ((3, 0), (8, 0))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def add(left, right):
    return tuple(a + b for a, b in zip(left, right))


def subtract(left, right):
    return tuple(a - b for a, b in zip(left, right))


def scale(value, vector):
    return tuple(value * coordinate for coordinate in vector)


def sum_rows(rows, dimension):
    total = (Fraction(0),) * dimension
    for row in rows:
        total = add(total, row)
    return total


def covector(vector, matrix):
    return tuple(
        sum((matrix[row][column] * vector[column]
             for column in range(3)), Fraction(0))
        for row in range(3)
    )


def flatten_covectors(vectors, matrix):
    return tuple(value for vector in vectors
                 for value in covector(vector, matrix))


def ordinary_configurations(patterns, disjoint):
    answer = set()
    for indices in itertools.combinations_with_replacement(
        range(len(patterns)), 4
    ):
        chosen = tuple(patterns[index] for index in indices)
        if all(sum(row[fibre] for row in chosen) == 4
               for fibre in disjoint):
            answer.add(chosen)
    assert answer
    return tuple(sorted(answer))


def configuration_load(configuration, vectors, matrix):
    loads = [[Fraction(0)] * 3 for _ in vectors]
    for pattern in configuration:
        q_value = base.vector_sum(
            scale(pattern[fibre], vectors[fibre])
            for fibre in range(len(vectors))
        )
        for fibre, degree in enumerate(pattern):
            for coordinate in range(3):
                loads[fibre][coordinate] += degree * q_value[coordinate]
    return flatten_covectors(tuple(map(tuple, loads)), matrix)


def independent_frontier(option_rows, target):
    """Exact forward-state DP plus a separately reconstructed backward DAG."""

    dimension = len(target)
    suffix_low = [[Fraction(0)] * dimension
                  for _ in range(len(option_rows) + 1)]
    suffix_high = [[Fraction(0)] * dimension
                   for _ in range(len(option_rows) + 1)]
    for index in range(len(option_rows) - 1, -1, -1):
        for coordinate in range(dimension):
            values = [value[coordinate] for _, value in option_rows[index]]
            suffix_low[index][coordinate] = (
                min(values) + suffix_low[index + 1][coordinate]
            )
            suffix_high[index][coordinate] = (
                max(values) + suffix_high[index + 1][coordinate]
            )

    zero = (Fraction(0),) * dimension
    layers = [{zero}]
    transitions = []
    for index, options in enumerate(option_rows):
        following = set()
        transition_count = 0
        for state in layers[-1]:
            for _, option in options:
                value = add(state, option)
                if all(
                    value[coordinate] + suffix_low[index + 1][coordinate]
                    <= target[coordinate]
                    <= value[coordinate] + suffix_high[index + 1][coordinate]
                    for coordinate in range(dimension)
                ):
                    following.add(value)
                    transition_count += 1
        layers.append(following)
        transitions.append(transition_count)

    viable = {target} if target in layers[-1] else set()
    viable_counts = [0] * (len(option_rows) + 1)
    viable_counts[-1] = len(viable)
    allowed = [set() for _ in option_rows]
    for index in range(len(option_rows) - 1, -1, -1):
        preceding = set()
        for state in viable:
            for config_index, option in option_rows[index]:
                previous = subtract(state, option)
                if previous in layers[index]:
                    preceding.add(previous)
                    allowed[index].add(config_index)
        viable = preceding
        viable_counts[index] = len(viable)

    paths = [(target, ())] if target in layers[-1] else []
    for index in range(len(option_rows) - 1, -1, -1):
        preceding_paths = []
        for state, reverse_path in paths:
            for config_index, option in option_rows[index]:
                previous = subtract(state, option)
                if previous in layers[index]:
                    preceding_paths.append(
                        (previous, reverse_path + (config_index,))
                    )
        paths = preceding_paths
    solutions = {
        tuple(reversed(reverse_path))
        for state, reverse_path in paths if state == zero
    }
    return {
        "solutions": tuple(sorted(solutions)),
        "forward_state_counts": [len(layer) for layer in layers],
        "forward_transition_counts": transitions,
        "backward_viable_state_counts": viable_counts,
        "allowed_config_indices_by_fibre": [sorted(row) for row in allowed],
    }


def exceptional_degrees(
    vertex, source_fibre, adjacency, vertices, exceptional, ordinary,
):
    source_support = exceptional[source_fibre]
    disjoint = tuple(index for index, support in enumerate(exceptional)
                     if set(source_support).isdisjoint(support))
    known = [0] * len(exceptional)
    support_index = {support: index for index, support in enumerate(exceptional)}
    for other in adjacency[vertex]:
        known[support_index[base.support(vertices[other])]] += 1
    assert all(known[target] == 0 for target in disjoint)

    forced_ordinary = [0] * 7
    for support in ordinary:
        if set(source_support).isdisjoint(support):
            for group in support:
                forced_ordinary[group] += 1
    choices = []
    for values in itertools.product(range(5), repeat=len(disjoint)):
        degrees = list(known)
        for target, value in zip(disjoint, values):
            degrees[target] = value
        if all(
            sum(degrees[index] for index, support in enumerate(exceptional)
                if group in support) + forced_ordinary[group]
            == (2 if group in source_support else 4)
            for group in range(7)
        ):
            choices.append(tuple(degrees))
    assert len(choices) == 1
    return choices[0]


@lru_cache(maxsize=None)
def binary_matrices(rows, columns):
    row_options = tuple(
        tuple(sum(1 << column for column in choice)
              for choice in itertools.combinations(range(4), degree))
        for degree in rows
    )
    answer = []
    for selected in itertools.product(*row_options):
        if all(sum((selected[row] >> column) & 1 for row in range(4))
               == columns[column] for column in range(4)):
            answer.append(tuple(
                (row, column) for row in range(4) for column in range(4)
                if (selected[row] >> column) & 1
            ))
    return tuple(answer)


def pair_upper_holds(adjacency, vertices, affected=None):
    if affected is None:
        pairs = itertools.combinations(range(len(vertices)), 2)
    else:
        pairs = {
            tuple(sorted((left, right)))
            for left in affected for right in range(len(vertices))
            if left != right
        }
    for left, right in pairs:
        allowed = (
            2 - len(set(vertices[left]) & set(vertices[right]))
            - int(right in adjacency[left])
        )
        if len(adjacency[left] & adjacency[right]) > allowed:
            return False
    return True


def factor_options(target_fibre, configuration, vectors, matrix):
    repeated = []
    for pattern in configuration:
        q_value = base.vector_sum(
            scale(pattern[fibre], vectors[fibre])
            for fibre in range(len(vectors))
        )
        value = covector(q_value, matrix)
        repeated.extend([value] * pattern[target_fibre])
    assert len(repeated) == 4
    return tuple(sorted({
        tuple(value for row in permutation for value in row)
        for permutation in itertools.permutations(repeated)
    }))


def minkowski(option_rows):
    dimension = len(option_rows[0][0]) if option_rows else 12
    states = {(Fraction(0),) * dimension}
    for options in option_rows:
        states = {add(state, option)
                  for state in states for option in options}
    return frozenset(states)


def balanced_halves(option_rows):
    left, right = [], []
    left_product = right_product = 1
    for options in sorted(option_rows, key=len, reverse=True):
        if left_product <= right_product:
            left.append(options)
            left_product *= len(options)
        else:
            right.append(options)
            right_product *= len(options)
    return minkowski(tuple(left)), minkowski(tuple(right))


def halves_contain(halves, target):
    left, right = halves
    if len(left) > len(right):
        left, right = right, left
    return any(subtract(target, value) in right for value in left)


def solve_independently(
    initial_adjacency, block_rows, node_tables, incident, all_bits, vertices,
    leaf_filter=None,
):
    assignment = [-1] * len(block_rows)
    # Reverse the target producer's final tie break, giving an independent
    # traversal while preserving a useful smallest-domain heuristic.
    order = sorted(
        range(len(block_rows)),
        key=lambda variable: (
            len(block_rows[variable]["options"]),
            len(node_tables[block_rows[variable]["pair"][0]])
            + len(node_tables[block_rows[variable]["pair"][1]]),
            -variable,
        ),
    )
    nodes = 0

    def possible_bits(fibre, active):
        answer = 0
        variables = incident[fibre]
        for choices, bits in node_tables[fibre].items():
            if not bits & active:
                continue
            if all(assignment[variable] < 0
                   or assignment[variable] == choices[position]
                   for position, variable in enumerate(variables)):
                answer |= bits
        return answer & active

    def recurse(depth, adjacency, active):
        nonlocal nodes
        if depth == len(block_rows):
            filtered = active if leaf_filter is None else leaf_filter(
                adjacency, active
            )
            return (bool(filtered),
                    (tuple(assignment), filtered) if filtered else None)
        variable = order[depth]
        endpoints = block_rows[variable]["pair"]
        for option_index, edges in enumerate(block_rows[variable]["options"]):
            nodes += 1
            assignment[variable] = option_index
            bits = active
            for fibre in endpoints:
                bits = possible_bits(fibre, bits)
                if not bits:
                    break
            if not bits:
                assignment[variable] = -1
                continue
            trial = [set(row) for row in adjacency]
            affected = set()
            for left, right in edges:
                trial[left].add(right)
                trial[right].add(left)
                affected.update((left, right))
            if pair_upper_holds(trial, vertices, affected):
                feasible, witness = recurse(depth + 1, trial, bits)
                if feasible:
                    assignment[variable] = -1
                    return True, witness
            assignment[variable] = -1
        return False, None

    feasible, witness = recurse(0, initial_adjacency, all_bits)
    return ("SAT" if feasible else "UNSAT"), witness, nodes, order


def local_pair_feasible_without_label_quotient(
    configuration, fibres, vertices_by_fibre, forbidden_pairs, mapping_cache,
):
    """Exact per-ordinary-fibre mapping CSP, without producer symmetry WLOG."""

    domains = {}
    for fibre in fibres:
        counts = tuple(pattern[fibre] for pattern in configuration)
        if counts not in mapping_cache:
            destinations = tuple(
                position for position, count in enumerate(counts)
                for _ in range(count)
            )
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
                for left, right in itertools.combinations(range(4), 2)
            )
        )
        if not domains[fibre]:
            return False

    order = tuple(sorted(fibres, key=lambda fibre: (len(domains[fibre]), fibre)))
    assignments = {}

    def visit(depth):
        if depth == len(order):
            return True
        fibre = order[depth]
        own = vertices_by_fibre[fibre]
        for mapping in domains[fibre]:
            if any(
                mapping[left] == other_mapping[right]
                and tuple(sorted((own[left], other_vertices[right])))
                in forbidden_pairs
                for other_fibre, other_mapping in assignments.items()
                for other_vertices in (vertices_by_fibre[other_fibre],)
                for left in range(4) for right in range(4)
            ):
                continue
            assignments[fibre] = mapping
            if visit(depth + 1):
                return True
            del assignments[fibre]
        return False

    return visit(0)


def main() -> None:
    local_doc = json.loads(LOCAL.read_text(encoding="utf-8"))
    catalog_doc = json.loads(CATALOG.read_text(encoding="utf-8"))
    gram_doc = json.loads(GRAM.read_text(encoding="utf-8"))
    fibre_doc = json.loads(FIBRE_FILTER.read_text(encoding="utf-8"))
    fibre_audit = json.loads(FIBRE_AUDIT.read_text(encoding="utf-8"))
    global_doc = json.loads(GLOBAL_OUTPUT.read_text(encoding="utf-8"))
    sync_docs = [json.loads(path.read_text(encoding="utf-8"))
                 for path in SYNC_OUTPUTS]
    localpair_docs = [json.loads(path.read_text(encoding="utf-8"))
                      for path in LOCALPAIR_OUTPUTS]

    assert fibre_audit["status"] == "SOURCE150_FIBRE_RECURRENCE_AUDIT_PASS"
    assert global_doc["status"] \
        == "EXACT_GLOBAL_ORDINARY_CONFIG_FRONTIERS_COMPLETE"
    assert all(doc["status"] == "EXACT_SYNCHRONIZED_CONFIG_CSP_SLICE_COMPLETE"
               for doc in sync_docs)
    assert all(doc["status"] == "EXACT_SYNCHRONIZED_CONFIG_CSP_SLICE_COMPLETE"
               for doc in localpair_docs)

    row = next(item for item in local_doc["support_rows"]
               if item["partition"] == [2, 2, 2, 2, 1, 1, 1, 1]
               and item["compression_orbit_index"] == 0)
    exceptional = tuple(tuple(item["support"])
                        for item in row["exceptional_supports"])
    assert exceptional == (
        (0, 2), (0, 3), (0, 4), (0, 5),
        (1, 2), (1, 3), (1, 4), (1, 5),
    )
    ordinary = tuple(support for support in base.ALL_SUPPORTS
                     if support not in exceptional)
    overlap_pairs = tuple(
        pair for pair in itertools.combinations(range(8), 2)
        if not set(exceptional[pair[0]]).isdisjoint(exceptional[pair[1]])
    )
    disjoint_pairs = tuple(
        pair for pair in itertools.combinations(range(8), 2)
        if set(exceptional[pair[0]]).isdisjoint(exceptional[pair[1]])
    )
    assert len(ordinary) == 13
    assert len(overlap_pairs) == 16 and len(disjoint_pairs) == 12
    variable_of_pair = {pair: number for number, pair
                        in enumerate(disjoint_pairs)}
    incident = tuple(tuple(variable_of_pair[pair] for pair in disjoint_pairs
                           if fibre in pair) for fibre in range(8))
    assert all(len(row_) == 3 for row_ in incident)

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
        tuple(sorted((2 * first + first_bit, 2 * second + second_bit)))
        for first, second in exceptional
        for first_bit, second_bit in itertools.product((0, 1), repeat=2)
    )
    vertex_index = {vertex: index for index, vertex in enumerate(vertices)}
    fibre_of = {
        vertex: exceptional.index(base.support(vertex)) for vertex in vertices
    }
    vertices_by_fibre = tuple(
        tuple(index for index, vertex in enumerate(vertices)
              if fibre_of[vertex] == fibre)
        for fibre in range(8)
    )

    catalog = [entry for entry in catalog_doc["macro_entries"]
               if entry["source_row_index"] == 150]
    entry_by_key = {
        base.catalog_key(entry, overlap_pairs): entry for entry in catalog
    }
    assert len(entry_by_key) == 21
    gram_rows = {
        (entry["state_orbit_number"],
         entry["signature_stabilizer_orbit_number"],
         entry["signature_stabilizer_canonical"]): entry
        for entry in gram_doc["rows"] if entry["source_row_index"] == 150
    }

    patterns = {}
    configurations = {}
    for support in ordinary:
        pattern_rows, disjoint, _ = base.ordinary_vertex_patterns(
            support, exceptional, ordinary
        )
        patterns[support] = pattern_rows, disjoint
        configurations[support] = ordinary_configurations(
            pattern_rows, disjoint
        )
    configuration_counts = [len(configurations[support])
                            for support in ordinary]
    assert configuration_counts == [1, 1, 1, 3, 3, 3, 12, 3, 3, 12, 3, 12, 12]

    targets = {}
    for key in fibre_doc["distinct_target_histogram"]:
        macro_text, target_text = key.split(";target=")
        macro = tuple(map(int, macro_text.removeprefix("macro=").split(":")))
        if macro in FRONTIER_MACROS:
            target = tuple(Fraction(value) for value in target_text.split(","))
            if macro in targets:
                assert targets[macro] == target
            targets[macro] = target
    assert set(targets) == set(FRONTIER_MACROS)

    reported_global = {tuple(row_["macro"]): row_
                       for row_ in global_doc["results"]}
    assert set(reported_global) == set(FRONTIER_MACROS)
    frontiers_by_H = {}
    frontier_counts = {}
    for macro in FRONTIER_MACROS:
        gram_candidates = [
            entry for key, entry in gram_rows.items()
            if key[:2] == macro and key[2] is True
        ]
        assert len(gram_candidates) == 1
        matrix = tuple(tuple(Fraction(value) for value in matrix_row)
                       for matrix_row in gram_candidates[0]["unique_H"])
        assert base.exact_psd(matrix)
        option_rows = tuple(tuple(
            (index, configuration_load(configuration, vectors, matrix))
            for index, configuration in enumerate(configurations[support])
        ) for support in ordinary)
        rebuilt = independent_frontier(option_rows, targets[macro])
        reported = reported_global[macro]
        reported_configs = tuple(
            tuple(tuple(tuple(int(value) for value in pattern)
                        for pattern in configuration)
                  for configuration in support_rows)
            for support_rows in reported["configurations"]
        )
        assert reported_configs == tuple(configurations[support]
                                         for support in ordinary)
        assert reported["ordinary_support_order"] == [list(row_) for row_ in ordinary]
        assert reported["configuration_counts"] == configuration_counts
        assert tuple(tuple(Fraction(value) for value in row_)
                     for row_ in reported["Gram_H"]) == matrix
        assert tuple(Fraction(value) for value in reported["target"]) \
            == targets[macro]
        assert reported["solution_path_count"] == len(rebuilt["solutions"])
        assert {tuple(row_) for row_ in reported["configuration_index_solutions"]} \
            == set(rebuilt["solutions"])
        for field in (
            "forward_state_counts", "forward_transition_counts",
            "backward_viable_state_counts",
            "allowed_config_indices_by_fibre",
        ):
            assert reported[field] == rebuilt[field]
        h_key = tuple(map(tuple, matrix))
        if h_key in frontiers_by_H:
            assert frontiers_by_H[h_key] == rebuilt["solutions"]
        else:
            frontiers_by_H[h_key] = rebuilt["solutions"]
        frontier_counts[f"{macro[0]}:{macro[1]}"] = len(rebuilt["solutions"])
    assert frontier_counts == {"0:0": 143, "0:1": 64, "0:3": 2331, "8:0": 380}

    for path, doc, macro in zip(SYNC_OUTPUTS, sync_docs, AUDITED_MACROS):
        assert doc["summary"]["wanted_macros"] == [list(macro)]
        assert doc["summary"]["slice_start"] == 0
        expected_inputs = (LOCAL, CATALOG, GRAM, FIBRE_FILTER, GLOBAL_OUTPUT)
        assert doc["inputs"] == {str(item): sha256(item)
                                 for item in expected_inputs}
    for path, doc, macro in zip(
        LOCALPAIR_OUTPUTS, localpair_docs, AUDITED_MACROS
    ):
        assert doc["summary"]["wanted_macros"] == [list(macro)]
        assert doc["summary"]["slice_start"] == 0
        assert doc["summary"]["ordinary_local_pair_filter_enabled"] is True
        assert doc["checks"]["ordinary_local_pair_residual_zero_filter"] is True
        expected_inputs = (LOCAL, CATALOG, GRAM, FIBRE_FILTER, GLOBAL_OUTPUT)
        assert doc["inputs"] == {str(item): sha256(item)
                                 for item in expected_inputs}

    survivor_masks = {row_[0] for row_ in fibre_doc["survivors"]}
    selected_by_macro = {macro: [] for macro in AUDITED_MACROS}
    for representative in row["representatives"]:
        if representative["mask_hex"] not in survivor_masks:
            continue
        entry = entry_by_key[base.representative_key(
            representative["edges"], fibre_of, overlap_pairs
        )]
        macro = (entry["state_orbit_number"],
                 entry["signature_stabilizer_orbit_number"])
        if macro in selected_by_macro:
            assert entry["signature_stabilizer_canonical"] is True
            selected_by_macro[macro].append((representative, entry))

    reported_by_macro = {
        macro: doc for macro, doc in zip(AUDITED_MACROS, sync_docs)
    }
    localpair_by_macro = {
        macro: doc for macro, doc in zip(AUDITED_MACROS, localpair_docs)
    }
    assert [len(selected_by_macro[macro]) for macro in AUDITED_MACROS] == [76, 56]
    assert [sum(rep["orbit_size"] for rep, _ in selected_by_macro[macro])
            for macro in AUDITED_MACROS] == [16_384, 16_384]

    factor_cache = {}
    halves_cache = {}
    projection_cache = {}
    reproduced_controls = 0
    exceptional_rows_checked = 0
    block_margin_equalities = 0
    all_statuses = {}
    independent_nodes = {}
    localpair_statuses = {}
    localpair_leaf_calls = 0
    localpair_factor_tests = 0
    localpair_factor_cache_hits = 0
    localpair_cache = {}
    mapping_cache = {}

    for macro in AUDITED_MACROS:
        document = reported_by_macro[macro]
        rows = document["results"]
        assert len(rows) == len(selected_by_macro[macro])
        controls = {control["record_number"]: control
                    for control in document["controls"]}
        expected_status = {}
        for number, ((representative, entry), reported_row) in enumerate(
            zip(selected_by_macro[macro], rows)
        ):
            assert reported_row[:5] == [
                number, representative["mask_hex"],
                representative["orbit_size"], representative["Q"], list(macro),
            ]
            gram = gram_rows[macro + (True,)]
            matrix = tuple(tuple(Fraction(value) for value in row_)
                           for row_ in gram["unique_H"])
            h_key = tuple(map(tuple, matrix))
            global_solutions = frontiers_by_H[h_key]
            all_bits = (1 << len(global_solutions)) - 1

            adjacency = [set() for _ in vertices]
            for raw_edge in representative["edges"]:
                left, right = base.edge_key(raw_edge)
                first, second = vertex_index[left], vertex_index[right]
                adjacency[first].add(second)
                adjacency[second].add(first)
            assert pair_upper_holds(adjacency, vertices)

            block_totals = {
                tuple(sorted((int(left), int(right)))): int(value)
                for left, right, value
                in representative["disjoint_Gram_profile"]["targets"]
            }
            assert set(block_totals) == set(disjoint_pairs)
            degree_rows = {}
            for source, fibre_vertices in enumerate(vertices_by_fibre):
                for vertex in fibre_vertices:
                    degree_rows[vertex] = exceptional_degrees(
                        vertex, source, adjacency, vertices, exceptional, ordinary
                    )
                    exceptional_rows_checked += 1

            q_exceptional = []
            for vertex in range(len(vertices)):
                q_exceptional.append(base.vector_sum(
                    scale(degree_rows[vertex][target], vectors[target])
                    for target in range(8)
                ))
            q_exceptional = tuple(q_exceptional)

            base_needed = []
            for fibre, fibre_vertices in enumerate(vertices_by_fibre):
                rows_needed = []
                for vertex in fibre_vertices:
                    known_load = base.vector_sum(
                        q_exceptional[other] for other in adjacency[vertex]
                    )
                    raw = subtract(
                        scale(12, vectors[fibre]),
                        add(q_exceptional[vertex], known_load),
                    )
                    rows_needed.append(covector(raw, matrix))
                base_needed.append(tuple(value for row_value in rows_needed
                                         for value in row_value))

            block_rows = []
            for left_fibre, right_fibre in disjoint_pairs:
                left_vertices = vertices_by_fibre[left_fibre]
                right_vertices = vertices_by_fibre[right_fibre]
                row_degrees = tuple(degree_rows[vertex][right_fibre]
                                    for vertex in left_vertices)
                column_degrees = tuple(degree_rows[vertex][left_fibre]
                                       for vertex in right_vertices)
                assert sum(row_degrees) == sum(column_degrees) \
                    == block_totals[(left_fibre, right_fibre)]
                block_margin_equalities += 2
                options = []
                loads = {left_fibre: [], right_fibre: []}
                for positions in binary_matrices(row_degrees, column_degrees):
                    edges = tuple((left_vertices[row_], right_vertices[column])
                                  for row_, column in positions)
                    trial = [set(neighbours) for neighbours in adjacency]
                    affected = set()
                    for left, right in edges:
                        trial[left].add(right)
                        trial[right].add(left)
                        affected.update((left, right))
                    if not pair_upper_holds(trial, vertices, affected):
                        continue
                    options.append(edges)
                    neighbours = defaultdict(list)
                    for left, right in edges:
                        neighbours[left].append(right)
                        neighbours[right].append(left)
                    for fibre, own_vertices in (
                        (left_fibre, left_vertices),
                        (right_fibre, right_vertices),
                    ):
                        load = []
                        for vertex in own_vertices:
                            value = base.vector_sum(
                                q_exceptional[other]
                                for other in neighbours[vertex]
                            )
                            load.extend(covector(value, matrix))
                        loads[fibre].append(tuple(load))
                assert options
                block_rows.append({
                    "pair": (left_fibre, right_fibre),
                    "options": tuple(options),
                    "loads": {fibre: tuple(values)
                              for fibre, values in loads.items()},
                })

            projection_groups = []
            visible_ordinary = []
            for fibre, support in enumerate(exceptional):
                used = tuple(index for index, ordinary_support in enumerate(ordinary)
                             if set(support).isdisjoint(ordinary_support))
                assert len(used) == 7
                visible_ordinary.append(used)
                projection_key = (h_key, fibre)
                if projection_key not in projection_cache:
                    groups = defaultdict(int)
                    for solution_number, solution in enumerate(global_solutions):
                        projection = tuple(solution[index] for index in used)
                        groups[projection] |= 1 << solution_number
                    projection_cache[projection_key] = tuple(sorted(groups.items()))
                projection_groups.append(projection_cache[projection_key])

            node_tables = []
            unique_target_counts = []
            for fibre in range(8):
                variables = incident[fibre]
                by_target = defaultdict(list)
                for choices in itertools.product(*(
                    range(len(block_rows[variable]["options"]))
                    for variable in variables
                )):
                    supplied = sum_rows((
                        block_rows[variable]["loads"][fibre][choice]
                        for variable, choice in zip(variables, choices)
                    ), 12)
                    target = subtract(base_needed[fibre], supplied)
                    by_target[target].append(tuple(choices))
                unique_target_counts.append(len(by_target))
                table = {}
                used = visible_ordinary[fibre]
                for target, choice_rows in by_target.items():
                    bits = 0
                    for projection, projection_bits in projection_groups[fibre]:
                        key = (h_key, fibre, projection)
                        if key not in halves_cache:
                            factor_rows = []
                            for ordinary_index, config_index in zip(used, projection):
                                factor_key = (h_key, fibre,
                                              ordinary_index, config_index)
                                if factor_key not in factor_cache:
                                    factor_cache[factor_key] = factor_options(
                                        fibre,
                                        configurations[ordinary[ordinary_index]][config_index],
                                        vectors, matrix,
                                    )
                                factor_rows.append(factor_cache[factor_key])
                            halves_cache[key] = balanced_halves(tuple(factor_rows))
                        if halves_contain(halves_cache[key], target):
                            bits |= projection_bits
                    if bits:
                        for choices in choice_rows:
                            table[choices] = bits
                node_tables.append(table)

            if any(not table for table in node_tables):
                status, witness, nodes, order = "UNSAT", None, 0, []
                reason = "empty_synchronized_pointwise_table"
            else:
                status, witness, nodes, order = solve_independently(
                    adjacency, tuple(block_rows), tuple(node_tables), incident,
                    all_bits, vertices,
                )
                reason = "witness" if status == "SAT" \
                    else "simultaneous_CSP_exhausted"
            assert status == reported_row[5]
            assert reason == reported_row[6]
            if status == "SAT":
                assert witness is not None and witness[1]
            else:
                assert witness is None
            expected_status[representative["mask_hex"]] = status
            independent_nodes[representative["mask_hex"]] = nodes

            localpair_row = localpair_by_macro[macro]["results"][number]
            assert localpair_row[:5] == reported_row[:5]
            if status == "UNSAT":
                localpair_status = "UNSAT"
                localpair_reason = reason
                localpair_witness = None
                localpair_nodes = nodes
            else:
                config_choice_groups = []
                for ordinary_index in range(len(ordinary)):
                    groups = defaultdict(int)
                    for solution_number, solution in enumerate(global_solutions):
                        groups[solution[ordinary_index]] |= 1 << solution_number
                    config_choice_groups.append(tuple(sorted(groups.items())))

                def local_pair_filter(complete_adjacency, active_bits):
                    nonlocal localpair_leaf_calls
                    nonlocal localpair_factor_tests
                    nonlocal localpair_factor_cache_hits
                    localpair_leaf_calls += 1
                    bits = active_bits
                    for ordinary_index, ordinary_support in enumerate(ordinary):
                        fibres = tuple(
                            fibre for fibre, support in enumerate(exceptional)
                            if set(support).isdisjoint(ordinary_support)
                        )
                        if not fibres:
                            continue
                        relevant = tuple(
                            vertex for fibre in fibres
                            for vertex in vertices_by_fibre[fibre]
                        )
                        forbidden = set()
                        for left, right in itertools.combinations(relevant, 2):
                            residual = (
                                2
                                - len(set(vertices[left]) & set(vertices[right]))
                                - int(right in complete_adjacency[left])
                                - len(complete_adjacency[left]
                                      & complete_adjacency[right])
                            )
                            assert residual >= 0
                            if residual == 0:
                                forbidden.add((left, right))
                        forbidden = frozenset(forbidden)
                        allowed = 0
                        for config_choice, group_bits in config_choice_groups[
                            ordinary_index
                        ]:
                            if not group_bits & bits:
                                continue
                            cache_key = (ordinary_index, config_choice, forbidden)
                            if cache_key in localpair_cache:
                                localpair_factor_cache_hits += 1
                                feasible = localpair_cache[cache_key]
                            else:
                                localpair_factor_tests += 1
                                feasible = local_pair_feasible_without_label_quotient(
                                    configurations[ordinary[ordinary_index]][
                                        config_choice
                                    ],
                                    fibres, vertices_by_fibre, forbidden,
                                    mapping_cache,
                                )
                                localpair_cache[cache_key] = feasible
                            if feasible:
                                allowed |= group_bits
                        bits &= allowed
                        if not bits:
                            return 0
                    return bits

                localpair_status, localpair_witness, localpair_nodes, _ = (
                    solve_independently(
                        adjacency, tuple(block_rows), tuple(node_tables), incident,
                        all_bits, vertices, local_pair_filter,
                    )
                )
                localpair_reason = (
                    "witness" if localpair_status == "SAT"
                    else "simultaneous_CSP_exhausted"
                )
            assert localpair_status == localpair_row[5]
            assert localpair_reason == localpair_row[6]
            assert localpair_witness is None
            localpair_statuses[representative["mask_hex"]] = localpair_status

            if number in controls:
                control = controls[number]
                assert control["macro"] == list(macro)
                assert control["global_config_solutions"] == len(global_solutions)
                assert control["projection_group_counts"] \
                    == [len(groups) for groups in projection_groups]
                assert control["block_domain_sizes"] \
                    == [len(block["options"]) for block in block_rows]
                assert control["unique_pointwise_targets"] == unique_target_counts
                assert control["node_table_sizes"] \
                    == [len(table) for table in node_tables]
                assert control["status"] == status
                assert control["reason"] == reason
                reproduced_controls += 1

        histogram = Counter(expected_status.values())
        mass = Counter()
        for representative, _ in selected_by_macro[macro]:
            mass[expected_status[representative["mask_hex"]]] \
                += representative["orbit_size"]
        summary = document["summary"]
        assert summary["available_orbits_in_wanted_macros"] \
            == summary["input_orbits"] == len(expected_status)
        assert summary["input_mass"] == sum(mass.values())
        assert summary["status_histogram"] == dict(sorted(histogram.items()))
        assert summary["SAT_mass"] == mass["SAT"]
        assert summary["UNSAT_mass"] == mass["UNSAT"]
        assert summary["UNKNOWN_mass"] == mass["UNKNOWN"] == 0
        expected_macro_stats = {
            "input_orbits": len(expected_status),
            "input_mass": sum(mass.values()),
            "SAT_orbits": histogram["SAT"],
            "SAT_mass": mass["SAT"],
            "UNSAT_orbits": histogram["UNSAT"],
            "UNSAT_mass": mass["UNSAT"],
        }
        assert document["per_macro"][f"{macro[0]}:{macro[1]}"] \
            == dict(sorted(expected_macro_stats.items()))
        all_statuses[macro] = (histogram, mass)

        local_document = localpair_by_macro[macro]
        local_histogram = Counter(localpair_statuses[
            representative["mask_hex"]
        ] for representative, _ in selected_by_macro[macro])
        local_mass = Counter()
        for representative, _ in selected_by_macro[macro]:
            local_mass[localpair_statuses[representative["mask_hex"]]] \
                += representative["orbit_size"]
        assert local_histogram == Counter({"UNSAT": len(expected_status)})
        assert local_mass == Counter({"UNSAT": sum(mass.values())})
        local_summary = local_document["summary"]
        assert local_summary["input_orbits"] == len(expected_status)
        assert local_summary["input_mass"] == sum(mass.values())
        assert local_summary["status_histogram"] == {"UNSAT": len(expected_status)}
        assert local_summary["UNSAT_mass"] == sum(mass.values())
        assert local_summary["SAT_mass"] == local_summary["UNKNOWN_mass"] == 0

    assert exceptional_rows_checked == (76 + 56) * 32
    assert block_margin_equalities == (76 + 56) * 12 * 2
    assert reproduced_controls == 48
    assert all_statuses[(3, 0)][0] == Counter({"UNSAT": 74, "SAT": 2})
    assert all_statuses[(3, 0)][1] == Counter({"UNSAT": 16_000, "SAT": 384})
    assert all_statuses[(8, 0)][0] == Counter({"UNSAT": 33, "SAT": 23})
    assert all_statuses[(8, 0)][1] == Counter({"UNSAT": 10_496, "SAT": 5_888})

    excluded_orbits = sum(all_statuses[macro][0]["UNSAT"]
                          for macro in AUDITED_MACROS)
    excluded_mass = sum(all_statuses[macro][1]["UNSAT"]
                        for macro in AUDITED_MACROS)
    surviving_orbits = sum(all_statuses[macro][0]["SAT"]
                           for macro in AUDITED_MACROS)
    surviving_mass = sum(all_statuses[macro][1]["SAT"]
                         for macro in AUDITED_MACROS)
    assert (excluded_orbits, excluded_mass, surviving_orbits, surviving_mass) \
        == (107, 26_496, 25, 6_272)
    assert len(localpair_statuses) == 132
    assert set(localpair_statuses.values()) == {"UNSAT"}

    input_paths = (
        LOCAL, CATALOG, GRAM, FIBRE_FILTER, FIBRE_AUDIT,
        GLOBAL_SCRIPT, GLOBAL_OUTPUT, SYNC_SCRIPT, *SYNC_OUTPUTS,
        *LOCALPAIR_OUTPUTS,
    )
    result = {
        "status": "SOURCE150_SYNCHRONIZED_LOCALPAIR_AUDIT_PASS",
        "source_row_index": 150,
        "inputs": {str(path): sha256(path) for path in input_paths},
        "global_frontier": {
            "macros": [list(macro) for macro in FRONTIER_MACROS],
            "ordinary_configuration_counts": configuration_counts,
            "solution_path_counts": frontier_counts,
            "all_reported_configurations_and_solution_paths_reconstructed": True,
            "all_forward_and_backward_DP_counts_reconstructed": True,
        },
        "synchronized_CSP": {
            "audited_macros": [list(macro) for macro in AUDITED_MACROS],
            "input_local_orbits": 132,
            "input_labelled_mass": 32_768,
            "UNSAT_local_orbits": excluded_orbits,
            "UNSAT_labelled_mass": excluded_mass,
            "SAT_local_orbits": surviving_orbits,
            "SAT_labelled_mass": surviving_mass,
            "UNKNOWN_local_orbits": 0,
            "per_macro": {
                "3:0": {"input_orbits": 76, "input_mass": 16_384,
                        "UNSAT_orbits": 74, "UNSAT_mass": 16_000,
                        "SAT_orbits": 2, "SAT_mass": 384},
                "8:0": {"input_orbits": 56, "input_mass": 16_384,
                        "UNSAT_orbits": 33, "UNSAT_mass": 10_496,
                        "SAT_orbits": 23, "SAT_mass": 5_888},
            },
            "exceptional_pointwise_degree_rows_checked": exceptional_rows_checked,
            "disjoint_block_margin_equalities_checked": block_margin_equalities,
            "producer_controls_reproduced": reproduced_controls,
            "independent_DFS_traversal_order": True,
            "all_reported_statuses_reproduced": True,
        },
        "ordinary_local_pair_extension": {
            "input_local_orbits": 132,
            "input_labelled_mass": 32_768,
            "UNSAT_local_orbits": 132,
            "UNSAT_labelled_mass": 32_768,
            "SAT_local_orbits": 0,
            "UNKNOWN_local_orbits": 0,
            "macro_3_0_UNSAT_mass": 16_384,
            "macro_8_0_UNSAT_mass": 16_384,
            "independent_leaf_calls": localpair_leaf_calls,
            "independent_factor_tests": localpair_factor_tests,
            "independent_factor_cache_hits": localpair_factor_cache_hits,
            "independent_factor_cache_entries": len(localpair_cache),
            "ordinary_U_label_symmetry_quotient_used_by_audit": False,
            "all_reported_statuses_reproduced": True,
        },
        "soundness": {
            "global_synchronization": (
                "Each bit denotes one common choice of all thirteen ordinary "
                "C4 degree configurations; the same bit is intersected across "
                "all eight exceptional fibres."
            ),
            "ordinary_exceptional_direction": (
                "For every disjoint ordinary/exceptional pair, each exceptional "
                "vertex has degree exactly one into the ordinary C4. The four "
                "ordinary-side degrees are the chosen configuration and may be "
                "0..4; no false converse degree-one condition is imposed."
            ),
            "exceptional_blocks": (
                "Every labelled 4x4 simple matrix with both fixed margins is "
                "enumerated in each of the twelve disjoint exceptional blocks. "
                "The independent DFS checks their simultaneous exceptional-pair "
                "common-neighbour upper bounds."
            ),
            "singular_Gram": (
                "Pointwise vector equations are compared after multiplication "
                "by exact PSD H; H*diff=0 is equality of represented Gram vectors."
            ),
            "ordinary_local_pair_residual": (
                "After fixing the complete exceptional graph, residual capacity "
                "for a pair x,y is 2-|support(x) intersect support(y)|-Axy-"
                "|N_E(x) intersect N_E(y)|. When it is zero, x and y cannot "
                "share an ordinary neighbour. Every allowed one-sided E-to-U "
                "function was enumerated without quotienting U labels."
            ),
            "projection_relaxation": (
                "The mappings witnessing pointwise recurrence and those "
                "witnessing the per-U pair condition are not forced to be the "
                "same. This enlarges feasibility, so an UNSAT conclusion remains "
                "a sound exclusion; passage would not prove realizability."
            ),
        },
        "claim_boundary": (
            "The base synchronized CSP rejects 26,496 labelled mass. Its exact "
            "ordinary-local-pair extension rejects the full 32,768 mass of the "
            "two audited macros, independently replayed here. This "
            "is executable mathematics, not a proof-assistant certificate. A "
            "local SAT status realizes only this subsystem and does not construct "
            "an srg(99,14,1,2)."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text("\n".join([
        "# E72 source150 synchronized-config independent audit",
        "",
        "Status: **SOURCE150_SYNCHRONIZED_LOCALPAIR_AUDIT_PASS**.",
        "",
        "The four ordinary global frontiers were reconstructed exactly, with "
        "solution counts 143, 64, 2,331, and 380. All reported configurations, "
        "solution paths, and forward/backward DP counts agree.",
        "",
        "For macro `(3,0)`, 74 of 76 local orbits (mass 16,000 of 16,384) "
        "are exact local UNSAT. For macro `(8,0)`, 33 of 56 local orbits "
        "(mass 10,496 of 16,384) are exact local UNSAT. Combined, 107 orbits "
        "of labelled mass 26,496 are excluded and 25 orbits of mass 6,272 "
        "remain locally SAT; there are no UNKNOWN cases.",
        "",
        "The audit independently rebuilt all labelled one-sided ordinary--E "
        "maps and all twelve disjoint E--E blocks with both margins, then used "
        "a different complete DFS order. All 132 statuses and 48 producer "
        "controls were reproduced.",
        "",
        "Adding the residual-zero ordinary-local-pair condition excludes all "
        "132 orbits / 32,768 mass in the two macros. The independent audit did "
        "not use the producer's quotient by equal-pattern U labels.",
        "",
        "Boundary: these are exact executable local exclusions, not a formal "
        "proof-assistant certificate. A surviving local CSP witness is not a "
        "99-vertex graph.",
        "",
    ]), encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "input_orbits": 132,
        "UNSAT_orbits": excluded_orbits,
        "base_UNSAT_mass": excluded_mass,
        "base_SAT_orbits": surviving_orbits,
        "base_SAT_mass": surviving_mass,
        "localpair_UNSAT_orbits": 132,
        "localpair_UNSAT_mass": 32_768,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
