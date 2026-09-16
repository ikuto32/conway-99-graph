"""Exact labelled ordinary-map collision probe for source-150 survivors.

This file starts from a witness of the synchronized exceptional-block CSP.
For the selected exceptional completion and global ordinary configuration it
keeps the actual one-sided maps E_f -> U, rather than only their q-loads.
It first enumerates, fibre by fibre, all seven-map tuples satisfying the four
pointwise rows of (B+I)q=12c.  A later stage combines those tuples subject to
the exceptional-pair common-neighbour capacities.  No converse regularity of
an E--U block is used: every exceptional vertex has one image in U, while the
four U-side occupancies may be 0,...,4 as prescribed by its configuration.
"""

from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

import scratch_theory_e72_source150_disjoint_graphical_filter as graphical
import scratch_theory_e72_source150_fibre_recurrence_filter as recurrence
import scratch_theory_e72_source150_norm_collision_filter as base


FIBRE_FILTER = Path("scratch_theory_e72_source150_fibre_recurrence_filter.json")
CONFIG_FRONTIER = Path("scratch_theory_e72_source150_global_config_census.json")


def scale(value, vector):
    return tuple(value * coordinate for coordinate in vector)


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def zero(n):
    return (Fraction(0),) * n


def mapping_options(configuration, target_fibre, vectors, H):
    """Return (map, flattened q-load) for one labelled E_f -> U map."""

    destinations = []
    q_rows = []
    for position, pattern in enumerate(configuration):
        destinations.extend([position] * pattern[target_fibre])
        q = base.add_vectors(
            scale(pattern[fibre], vectors[fibre])
            for fibre in range(len(vectors))
        )
        q_rows.append(recurrence.covector(q, H))
    assert len(destinations) == 4
    answer = []
    for mapping in sorted(set(itertools.permutations(destinations))):
        load = tuple(value for destination in mapping
                     for value in q_rows[destination])
        answer.append((mapping, load))
    return tuple(answer)


def enumerate_fibre_solutions(option_rows, target):
    """Meet-in-the-middle exact enumeration of map-index tuples."""

    split = len(option_rows) // 2

    def half(rows):
        groups = defaultdict(list)
        for choices in itertools.product(*(range(len(row)) for row in rows)):
            value = zero(len(target))
            for row, choice in zip(rows, choices):
                value = add(value, row[choice][1])
            groups[value].append(choices)
        return groups

    left = half(option_rows[:split])
    right = half(option_rows[split:])
    solutions = []
    for value, left_choices in left.items():
        complement = sub(target, value)
        for first in left_choices:
            for second in right.get(complement, ()):
                solutions.append(first + second)
    return tuple(solutions), (sum(map(len, left.values())),
                              sum(map(len, right.values())),
                              len(left), len(right))


def pair_capacities(instance):
    """Remaining capacity for common ordinary neighbours of each E pair."""

    adjacency = instance["adjacency"]
    vertices = instance["vertices"]
    answer = {}
    for left in range(len(vertices)):
        for right in range(left + 1, len(vertices)):
            value = (2 - len(set(vertices[left]) & set(vertices[right]))
                     - int(right in adjacency[left])
                     - len(adjacency[left] & adjacency[right]))
            assert value >= 0
            answer[left, right] = value
    return answer


def local_ordinary_factor_count(instance, global_config_index):
    """Count each U factor after same-U exceptional-pair upper bounds.

    Counts are quotiented by permutations of U vertices carrying identical
    exceptional-degree rows.  This quotient is only a difficulty diagnostic;
    the later global search must retain representatives and multiplicities are
    irrelevant to feasibility.
    """

    config_solution = instance["global_solutions"][global_config_index]
    capacities = pair_capacities(instance)
    answer = []
    for ordinary_index, ordinary_support in enumerate(instance["ordinary"]):
        fibres = tuple(fibre for fibre, support in enumerate(
            instance["exceptional"]) if not set(support) & set(ordinary_support))
        if not fibres:
            continue
        config = instance["configurations"][ordinary_index][
            config_solution[ordinary_index]]
        domains = {}
        for fibre in fibres:
            own = instance["by_fibre"][fibre]
            rows = mapping_options(config, fibre, instance["vectors"], instance["H"])
            domains[fibre] = tuple(
                row for row in rows
                if all(row[0][a] != row[0][b]
                       or capacities[tuple(sorted((own[a], own[b])))] >= 1
                       for a in range(4) for b in range(a + 1, 4))
            )
        order = tuple(sorted(fibres, key=lambda f: (len(domains[f]), f)))

        # Residual automorphisms of the fixed sorted multiset configuration.
        groups = defaultdict(list)
        for position, pattern in enumerate(config):
            groups[pattern].append(position)
        automorphisms = []
        for choices in itertools.product(*(
            tuple(itertools.permutations(group)) for group in groups.values()
        )):
            permutation = list(range(4))
            for group, image in zip(groups.values(), choices):
                for source, target in zip(group, image):
                    permutation[source] = target
            automorphisms.append(tuple(permutation))

        first = order[0]
        first_representatives = []
        seen = set()
        for row in domains[first]:
            mapping = row[0]
            orbit = {tuple(permutation[value] for value in mapping)
                     for permutation in automorphisms}
            canonical = min(orbit)
            if canonical == mapping and canonical not in seen:
                first_representatives.append(row)
                seen.add(canonical)
        assignment = {}
        count = 0

        def compatible(fibre, mapping):
            own = instance["by_fibre"][fibre]
            for other_fibre, other_mapping in assignment.items():
                other = instance["by_fibre"][other_fibre]
                for left in range(4):
                    for right in range(4):
                        if mapping[left] == other_mapping[right] and not capacities[
                            tuple(sorted((own[left], other[right])))
                        ]:
                            return False
            return True

        def visit(depth):
            nonlocal count
            if depth == len(order):
                count += 1
                return
            fibre = order[depth]
            rows = first_representatives if depth == 0 else domains[fibre]
            for mapping, _ in rows:
                if compatible(fibre, mapping):
                    assignment[fibre] = mapping
                    visit(depth + 1)
                    del assignment[fibre]

        visit(0)
        answer.append({"ordinary_index": ordinary_index,
                       "support": list(ordinary_support),
                       "incident_fibres": list(fibres),
                       "mapping_domain_sizes_after_same_fibre_upper": [
                           len(domains[fibre]) for fibre in fibres],
                       "position_automorphism_order": len(automorphisms),
                       "quotient_local_joint_count": count})
    return answer


def ordinary_targets(instance):
    answer = []
    for fibre in range(8):
        supplied = zero(12)
        for variable, (_, _, loads) in enumerate(instance["block_rows"]):
            if fibre in loads:
                supplied = add(
                    supplied, loads[fibre][instance["assignment"][variable]]
                )
        answer.append(sub(instance["base_needed"][fibre], supplied))
    return tuple(answer)


def joint_ordinary_factor_options(instance, global_config_index):
    """Materialize each U's map factor, modulo harmless U-label symmetry."""

    config_solution = instance["global_solutions"][global_config_index]
    capacities = pair_capacities(instance)
    factors = []
    for ordinary_index, ordinary_support in enumerate(instance["ordinary"]):
        fibres = tuple(fibre for fibre, support in enumerate(
            instance["exceptional"]) if not set(support) & set(ordinary_support))
        if not fibres:
            continue
        configuration = instance["configurations"][ordinary_index][
            config_solution[ordinary_index]]
        domains = {}
        for fibre in fibres:
            own = instance["by_fibre"][fibre]
            rows = mapping_options(
                configuration, fibre, instance["vectors"], instance["H"]
            )
            domains[fibre] = tuple(
                row for row in rows
                if all(
                    row[0][left] != row[0][right]
                    or capacities[tuple(sorted((own[left], own[right])))] >= 1
                    for left in range(4) for right in range(left + 1, 4)
                )
            )
            if not domains[fibre]:
                return ()
        order = tuple(sorted(fibres, key=lambda f: (len(domains[f]), f)))

        groups = defaultdict(list)
        for position, pattern in enumerate(configuration):
            groups[pattern].append(position)
        automorphisms = []
        for choices in itertools.product(*(
            tuple(itertools.permutations(group)) for group in groups.values()
        )):
            permutation = list(range(4))
            for group, image in zip(groups.values(), choices):
                for source, target in zip(group, image):
                    permutation[source] = target
            automorphisms.append(tuple(permutation))
        first = order[0]
        first_domain = tuple(
            row for row in domains[first]
            if row[0] == min(tuple(permutation[value] for value in row[0])
                             for permutation in automorphisms)
        )
        assignment = {}
        signatures = set()

        def visit(depth):
            if depth == len(order):
                loads = tuple((fibre, assignment[fibre][1]) for fibre in fibres)
                collisions = []
                all_vertices = tuple(
                    (fibre, local, instance["by_fibre"][fibre][local])
                    for fibre in fibres for local in range(4)
                )
                for index, (fibre, local, vertex) in enumerate(all_vertices):
                    mapping = assignment[fibre][0]
                    for other_fibre, other_local, other_vertex in all_vertices[index + 1:]:
                        if mapping[local] == assignment[other_fibre][0][other_local]:
                            pair = tuple(sorted((vertex, other_vertex)))
                            assert capacities[pair] >= 1
                            collisions.append(pair)
                signatures.add((loads, tuple(collisions)))
                return
            fibre = order[depth]
            own = instance["by_fibre"][fibre]
            rows = first_domain if depth == 0 else domains[fibre]
            for row in rows:
                mapping = row[0]
                if any(
                    mapping[left] == other_row[0][right]
                    and not capacities[tuple(sorted((
                        own[left], instance["by_fibre"][other_fibre][right]
                    )))]
                    for other_fibre, other_row in assignment.items()
                    for left in range(4) for right in range(4)
                ):
                    continue
                assignment[fibre] = row
                visit(depth + 1)
                del assignment[fibre]

        visit(0)
        factors.append({
            "ordinary_index": ordinary_index,
            "support": ordinary_support,
            "fibres": fibres,
            "options": tuple(sorted(signatures)),
        })
    return tuple(factors)


def joint_factor_search(instance, global_config_index, node_cap=0):
    """Exact U-factor DFS: pointwise recurrence plus cumulative E-pair upper."""

    capacities = pair_capacities(instance)
    targets = ordinary_targets(instance)
    factors = joint_ordinary_factor_options(instance, global_config_index)
    if not factors:
        return {"status": "UNSAT", "reason": "empty_local_factor", "nodes": 0}
    order = tuple(sorted(range(len(factors)),
                         key=lambda i: (len(factors[i]["options"]),
                                        factors[i]["ordinary_index"])))
    ordered = tuple(factors[index] for index in order)

    # Exact per-exceptional-fibre suffix reachable load sets.  Correlations
    # between different fibres are relaxed here, hence membership is a sound
    # pruning condition and the explicit DFS still decides the joint system.
    suffix = [[None] * 8 for _ in range(len(ordered) + 1)]
    for fibre in range(8):
        suffix[-1][fibre] = frozenset((zero(12),))
    suffix_sizes = []
    for depth in range(len(ordered) - 1, -1, -1):
        factor = ordered[depth]
        for fibre in range(8):
            contributions = {
                dict(loads).get(fibre, zero(12))
                for loads, _ in factor["options"]
            }
            suffix[depth][fibre] = frozenset(
                add(contribution, following)
                for contribution in contributions
                for following in suffix[depth + 1][fibre]
            )
        suffix_sizes.append([len(suffix[depth][fibre]) for fibre in range(8)])
    suffix_sizes.reverse()

    pair_list = tuple(itertools.combinations(range(32), 2))
    pair_index = {pair: index for index, pair in enumerate(pair_list)}
    cap_rows = tuple(capacities[pair] for pair in pair_list)
    collision_counts = [0] * len(pair_list)
    loads = [zero(12) for _ in range(8)]
    assignment = [-1] * len(ordered)
    nodes = 0

    def visit(depth):
        nonlocal nodes
        if node_cap and nodes >= node_cap:
            return "UNKNOWN"
        if depth == len(ordered):
            return "SAT" if tuple(loads) == targets else "UNSAT"
        factor = ordered[depth]
        for option_index, (load_rows, collisions) in enumerate(factor["options"]):
            nodes += 1
            if node_cap and nodes > node_cap:
                return "UNKNOWN"
            indices = tuple(pair_index[pair] for pair in collisions)
            if any(collision_counts[index] >= cap_rows[index] for index in indices):
                continue
            changed = []
            feasible = True
            for fibre, contribution in load_rows:
                previous = loads[fibre]
                loads[fibre] = add(previous, contribution)
                changed.append((fibre, previous))
            for fibre in range(8):
                if sub(targets[fibre], loads[fibre]) not in suffix[depth + 1][fibre]:
                    feasible = False
                    break
            if feasible:
                for index in indices:
                    collision_counts[index] += 1
                assignment[depth] = option_index
                status = visit(depth + 1)
                if status != "UNSAT":
                    return status
                assignment[depth] = -1
                for index in indices:
                    collision_counts[index] -= 1
            for fibre, previous in changed:
                loads[fibre] = previous
        return "UNSAT"

    status = visit(0)
    return {
        "status": status,
        "reason": "witness" if status == "SAT" else (
            "node_cap" if status == "UNKNOWN" else "joint_factor_DFS_exhausted"
        ),
        "nodes": nodes,
        "factor_order": [factor["ordinary_index"] for factor in ordered],
        "factor_option_counts": [len(factor["options"]) for factor in ordered],
        "suffix_reachable_sizes": suffix_sizes,
        "witness_option_indices_in_factor_order": (
            list(assignment) if status == "SAT" else []
        ),
    }


def build_instance(witness_path):
    witness_document = json.loads(Path(witness_path).read_text(encoding="utf-8"))
    witness_row = next(row for row in witness_document["results"]
                       if row[5] == "SAT")
    record_number, mask_hex, _, _, macro_list = witness_row[:5]
    assignment = tuple(witness_row[8])
    config_indices = tuple(witness_row[9])
    assert assignment and config_indices
    macro = tuple(macro_list)

    document = json.loads(base.LOCAL.read_text(encoding="utf-8"))
    row = next(item for item in document["support_rows"]
               if item["partition"] == [2, 2, 2, 2, 1, 1, 1, 1]
               and item["compression_orbit_index"] == 0)
    exceptional = tuple(tuple(item["support"])
                        for item in row["exceptional_supports"])
    ordinary = tuple(item for item in base.ALL_SUPPORTS
                     if item not in exceptional)
    support_to_fibre = {support: index for index, support in enumerate(exceptional)}
    overlap_pairs = tuple(pair for pair in itertools.combinations(range(8), 2)
                          if set(exceptional[pair[0]]) & set(exceptional[pair[1]]))
    disjoint_pairs = tuple(pair for pair in itertools.combinations(range(8), 2)
                           if not set(exceptional[pair[0]]) & set(exceptional[pair[1]]))

    catalog = [entry for entry in json.loads(base.CATALOG.read_text(
        encoding="utf-8"))["macro_entries"] if entry["source_row_index"] == 150]
    entry_by_key = {base.entry_key(entry, exceptional, overlap_pairs): entry
                    for entry in catalog}
    representatives = []
    survivor_masks = {item[0] for item in json.loads(FIBRE_FILTER.read_text(
        encoding="utf-8"))["survivors"]}
    for representative in row["representatives"]:
        if representative["mask_hex"] not in survivor_masks:
            continue
        entry = entry_by_key[base.representative_key(
            representative["edges"], support_to_fibre, overlap_pairs)]
        if (entry["state_orbit_number"],
                entry["signature_stabilizer_orbit_number"]) == macro:
            representatives.append((representative, entry))
    representative, entry = representatives[record_number]
    assert representative["mask_hex"] == mask_hex

    gram = next(item for item in json.loads(base.GRAM.read_text(
        encoding="utf-8"))["rows"]
                if item["source_row_index"] == 150
                and (item["state_orbit_number"],
                     item["signature_stabilizer_orbit_number"]) == macro
                and item["signature_stabilizer_canonical"] ==
                entry["signature_stabilizer_canonical"])
    H = tuple(tuple(Fraction(value) for value in row_value)
              for row_value in gram["unique_H"])
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
        for first, second in exceptional
        for bit_first, bit_second in itertools.product((0, 1), repeat=2)
    )
    vertex_index = {vertex: index for index, vertex in enumerate(vertices)}
    by_fibre = tuple(tuple(index for index, vertex in enumerate(vertices)
                           if base.support(vertex) == support)
                     for support in exceptional)
    adjacency = [set() for _ in vertices]
    for edge in representative["edges"]:
        left, right = (vertex_index[tuple(value)] for value in edge)
        adjacency[left].add(right)
        adjacency[right].add(left)

    block_totals = {tuple(sorted((int(left), int(right)))): int(value)
                    for left, right, value
                    in representative["disjoint_Gram_profile"]["targets"]}
    degree_rows = {}
    for source, fibre_vertices in enumerate(by_fibre):
        for vertex in fibre_vertices:
            patterns, _, _ = base.exceptional_vertex_patterns(
                vertex, source, adjacency, vertices, exceptional, ordinary)
            assert len(patterns) == 1
            degree_rows[vertex] = patterns[0]

    q_exceptional = []
    for vertex in range(len(vertices)):
        degrees = [0] * 8
        for other in adjacency[vertex]:
            degrees[support_to_fibre[base.support(vertices[other])]] += 1
        source = support_to_fibre[base.support(vertices[vertex])]
        for target in range(8):
            if not set(exceptional[source]) & set(exceptional[target]):
                degrees[target] = degree_rows[vertex][target]
        q_exceptional.append(base.add_vectors(
            scale(degrees[target], vectors[target]) for target in range(8)))
    q_exceptional = tuple(q_exceptional)
    base_needed = []
    for fibre, fibre_vertices in enumerate(by_fibre):
        needed = []
        for vertex in fibre_vertices:
            known = base.add_vectors(q_exceptional[other]
                                     for other in adjacency[vertex])
            raw = tuple(12 * vectors[fibre][coordinate]
                        - q_exceptional[vertex][coordinate] - known[coordinate]
                        for coordinate in range(3))
            needed.extend(recurrence.covector(raw, H))
        base_needed.append(tuple(needed))

    block_rows = []
    for pair in disjoint_pairs:
        left_fibre, right_fibre = pair
        left_vertices, right_vertices = by_fibre[left_fibre], by_fibre[right_fibre]
        rows = tuple(degree_rows[v][right_fibre] for v in left_vertices)
        columns = tuple(degree_rows[v][left_fibre] for v in right_vertices)
        options = []
        loads = {left_fibre: [], right_fibre: []}
        slacks = graphical.pair_slacks(adjacency, vertices)
        for matrix in graphical.matrices_with_margins(rows, columns):
            edges = graphical.matrix_edges(matrix, left_vertices, right_vertices)
            if not graphical.single_block_pair_upper(adjacency, slacks, edges):
                continue
            options.append(edges)
            lookup = defaultdict(list)
            for left, right in edges:
                lookup[left].append(right)
                lookup[right].append(left)
            for fibre, own_vertices in ((left_fibre, left_vertices),
                                        (right_fibre, right_vertices)):
                load = []
                for vertex in own_vertices:
                    value = base.add_vectors(q_exceptional[x]
                                             for x in lookup[vertex])
                    load.extend(recurrence.covector(value, H))
                loads[fibre].append(tuple(load))
        block_rows.append((pair, tuple(options),
                           {f: tuple(v) for f, v in loads.items()}))
    assert len(block_rows) == len(assignment) == 12
    for (_, options, _), choice in zip(block_rows, assignment):
        for left, right in options[choice]:
            adjacency[left].add(right)
            adjacency[right].add(left)

    frontier = next(item for item in json.loads(CONFIG_FRONTIER.read_text(
        encoding="utf-8"))["results"]
                    if tuple(tuple(Fraction(value) for value in r)
                             for r in item["Gram_H"]) == H)
    configurations = tuple(
        tuple(tuple(tuple(int(value) for value in pattern) for pattern in config)
              for config in rows) for rows in frontier["configurations"])
    global_solutions = tuple(tuple(x) for x in
                             frontier["configuration_index_solutions"])

    return {
        "record_number": record_number, "mask_hex": mask_hex,
        "macro": macro, "assignment": assignment,
        "config_indices": config_indices, "global_solutions": global_solutions,
        "configurations": configurations, "exceptional": exceptional,
        "ordinary": ordinary, "vectors": vectors, "H": H,
        "vertices": vertices, "by_fibre": by_fibre,
        "adjacency": adjacency, "base_needed": tuple(base_needed),
        "block_rows": tuple(block_rows),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("witness", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--config-index", type=int)
    parser.add_argument("--joint-search", action="store_true")
    parser.add_argument("--joint-only", action="store_true")
    parser.add_argument("--node-cap", type=int, default=0)
    arguments = parser.parse_args()
    instance = build_instance(arguments.witness)
    report = {"status": "FIBRE_MAP_SOLUTION_CENSUS_COMPLETE",
              "witness": str(arguments.witness),
              "record_number": instance["record_number"],
              "mask_hex": instance["mask_hex"],
              "macro": list(instance["macro"]), "configurations": []}
    selected_configs = (instance["config_indices"] if arguments.config_index is None
                        else (arguments.config_index,))
    assert all(index in instance["config_indices"] for index in selected_configs)
    for config_index in selected_configs:
        solution = instance["global_solutions"][config_index]
        option_rows_by_fibre = []
        fibre_counts = []
        fibre_solutions = []
        for fibre, support in (() if arguments.joint_only else
                               enumerate(instance["exceptional"])):
            used = tuple(index for index, ordinary in enumerate(instance["ordinary"])
                         if not set(support) & set(ordinary))
            option_rows = tuple(mapping_options(
                instance["configurations"][ordinary_index][solution[ordinary_index]],
                fibre, instance["vectors"], instance["H"])
                                for ordinary_index in used)
            supplied = zero(12)
            for variable, (_, _, loads) in enumerate(instance["block_rows"]):
                if fibre in loads:
                    supplied = add(supplied,
                                   loads[fibre][instance["assignment"][variable]])
            target = sub(instance["base_needed"][fibre], supplied)
            solutions, stats = enumerate_fibre_solutions(option_rows, target)
            capacities = pair_capacities(instance)
            own = instance["by_fibre"][fibre]
            same_fibre_solutions = tuple(
                choices for choices in solutions
                if all(
                    sum(option_rows[position][choice][0][left]
                        == option_rows[position][choice][0][right]
                        for position, choice in enumerate(choices))
                    <= capacities[tuple(sorted((own[left], own[right])))]
                    for left in range(4) for right in range(left + 1, 4)
                )
            )
            option_rows_by_fibre.append((used, option_rows))
            fibre_solutions.append(same_fibre_solutions)
            fibre_counts.append({"fibre": fibre,
                                 "ordinary_support_indices": list(used),
                                 "map_domain_sizes": [len(x) for x in option_rows],
                                 "MITM": list(stats),
                                 "solution_count": len(solutions),
                                 "after_same_fibre_cumulative_pair_upper":
                                 len(same_fibre_solutions)})
        report["configurations"].append({
            "global_configuration_index": config_index,
            "fibre_solution_counts": fibre_counts,
            "raw_independent_solution_product": __import__("math").prod(
                len(x) for x in fibre_solutions) if fibre_solutions else None,
            "local_ordinary_factor_counts": (
                None if arguments.joint_only else
                local_ordinary_factor_count(instance, config_index)
            ),
            "joint_factor_search": (
                joint_factor_search(instance, config_index, arguments.node_cap)
                if arguments.joint_search else None
            ),
        })
    output = arguments.output or arguments.witness.with_name(
        arguments.witness.stem + "_map_census.json")
    output.write_text(json.dumps(report, separators=(",", ":")) + "\n",
                      encoding="utf-8")
    print(json.dumps(report, separators=(",", ":")))


if __name__ == "__main__":
    main()
