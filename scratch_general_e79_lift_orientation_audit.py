"""Exact local P4-orientation audit for the E0=79 fibre classification.

Input: the twelve support representatives retained by
scratch_general_e79_compression_audit.json.  The computation makes no WLOG
choice of a P4 orientation: all 4^5 missing-side choices are checked.

For a P4 fibre on support {g,h}, encode its missing square edge by
(varying group, sign at the fixed group).  Its two endpoints need one
overlap neighbour through each support group.  A port records the endpoint's
sign at that group and the sign required on its neighbour.  The script
enumerates compatible perfect matchings of these ports separately at every
base group.  It also quotients all 1024 orientations by the exact setwise
support stabilizer in S7 together with all 2^7 coordinate flips.
"""

from __future__ import annotations

import itertools
import json
from collections import Counter
from pathlib import Path


INPUT_PATH = Path("scratch_general_e79_compression_audit.json")
RESULT_PATH = Path("scratch_general_e79_lift_orientation_audit.json")


def transform_support(edge, permutation):
    return tuple(sorted(permutation[x] for x in edge))


def stabilizer_permutations(supports):
    support_set = set(supports)
    return [
        permutation
        for permutation in itertools.permutations(range(7))
        if {transform_support(edge, permutation) for edge in supports} == support_set
    ]


def action_maps(supports, stabilizer):
    """Return the distinct actions of Stab_S7(H) semidirect C2^7."""
    position = {edge: i for i, edge in enumerate(supports)}
    actions = set()
    for permutation in stabilizer:
        for flip_mask in range(1 << 7):
            action = []
            for edge in supports:
                target = transform_support(edge, permutation)
                target_position = position[target]
                code_map = []
                for code in range(4):
                    varying_index, fixed_sign = divmod(code, 2)
                    varying_group = permutation[edge[varying_index]]
                    fixed_group = permutation[edge[1 - varying_index]]
                    target_varying_index = target.index(varying_group)
                    target_sign = fixed_sign ^ ((flip_mask >> fixed_group) & 1)
                    code_map.append(2 * target_varying_index + target_sign)
                action.append((target_position, tuple(code_map)))
            actions.add(tuple(action))
    return tuple(sorted(actions))


def apply_action(state, action):
    image = [None] * len(state)
    for old_position, code in enumerate(state):
        new_position, code_map = action[old_position]
        image[new_position] = code_map[code]
    assert all(value is not None for value in image)
    return tuple(image)


def orientation_orbits(actions):
    remaining = set(itertools.product(range(4), repeat=5))
    sizes = []
    while remaining:
        seed = min(remaining)
        orbit = {apply_action(seed, action) for action in actions}
        assert seed in orbit and orbit <= remaining
        remaining.difference_update(orbit)
        sizes.append(len(orbit))
    assert sum(sizes) == 4**5
    return sorted(sizes)


def fibre_endpoints(edge, code):
    """Return endpoint sign maps for the missing side of one P4."""
    varying_index, fixed_sign = divmod(code, 2)
    varying_group = edge[varying_index]
    fixed_group = edge[1 - varying_index]
    return (
        {varying_group: 0, fixed_group: fixed_sign},
        {varying_group: 1, fixed_group: fixed_sign},
    )


def audit_port_formula():
    """Derive the two endpoint deficits directly from the four square labels."""
    for edge in itertools.combinations(range(7), 2):
        for code in range(4):
            varying_index, fixed_sign = divmod(code, 2)
            varying_group = edge[varying_index]
            vertices = tuple(itertools.product(range(2), repeat=2))
            missing = {
                signs
                for signs in vertices
                if signs[1 - varying_index] == fixed_sign
            }
            for signs in missing:
                neighbours = []
                for other in vertices:
                    distance = sum(a != b for a, b in zip(signs, other))
                    if distance != 1 or {signs, other} == missing:
                        continue
                    neighbours.append(other)
                assert len(neighbours) == 1
                endpoint_signs = dict(zip(edge, signs))
                deficits = []
                for coordinate_index, group in enumerate(edge):
                    for symbol_sign in range(2):
                        count = sum(
                            other[coordinate_index] == symbol_sign
                            for other in neighbours
                        )
                        if count == 0:
                            deficits.append((group, symbol_sign))
                        else:
                            assert count == 1
                assert len(deficits) == 2
                expected = {
                    (
                        group,
                        port(endpoint_signs, varying_group, group)[1],
                    )
                    for group in edge
                }
                assert set(deficits) == expected


def port(endpoint_signs, varying_group, group):
    sigma = endpoint_signs[group]
    required = 1 - sigma if group == varying_group else sigma
    return sigma, required


def perfect_matching_count(ports):
    """Count compatible matchings; ports from one fibre cannot pair."""
    if not ports:
        return 1

    def compatible(left, right):
        fibre_l, _endpoint_l, sigma_l, required_l = left
        fibre_r, _endpoint_r, sigma_r, required_r = right
        return (
            fibre_l != fibre_r
            and sigma_r == required_l
            and sigma_l == required_r
        )

    def visit(remaining):
        if not remaining:
            return 1
        left = remaining[0]
        total = 0
        for q in range(1, len(remaining)):
            if compatible(left, remaining[q]):
                total += visit(remaining[1:q] + remaining[q + 1 :])
        return total

    return visit(tuple(ports))


def overlap_pattern_count(supports, state):
    ports_by_group = [[] for _ in range(7)]
    for fibre_index, (edge, code) in enumerate(zip(supports, state)):
        varying_index, _fixed_sign = divmod(code, 2)
        varying_group = edge[varying_index]
        for endpoint_index, endpoint_signs in enumerate(fibre_endpoints(edge, code)):
            for group in edge:
                sigma, required = port(endpoint_signs, varying_group, group)
                ports_by_group[group].append(
                    (fibre_index, endpoint_index, sigma, required)
                )
    group_counts = [perfect_matching_count(ports) for ports in ports_by_group]
    product = 1
    for value in group_counts:
        product *= value
    return product, group_counts


def graph_properties(supports):
    degrees = [0] * 7
    adjacency = [set() for _ in range(7)]
    for u, v in supports:
        degrees[u] += 1
        degrees[v] += 1
        adjacency[u].add(v)
        adjacency[v].add(u)
    nonzero = [value for value in degrees if value]
    colour = {}
    bipartite = True
    for seed in range(7):
        if not adjacency[seed] or seed in colour:
            continue
        colour[seed] = 0
        stack = [seed]
        while stack:
            u = stack.pop()
            for v in adjacency[u]:
                if v not in colour:
                    colour[v] = 1 - colour[u]
                    stack.append(v)
                elif colour[v] == colour[u]:
                    bipartite = False
    return {
        "degree_sequence": sorted(nonzero, reverse=True),
        "minimum_nonzero_degree": min(nonzero),
        "has_leaf": 1 in nonzero,
        "bipartite": bipartite,
    }


def main():
    audit_port_formula()
    source = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    rows = [
        row
        for row in source["rows"]
        if row.get("passes_compression_square_and_BP")
    ]
    assert len(rows) == 12
    output_rows = []
    for row in rows:
        supports = tuple(
            sorted(tuple(item["support"]) for item in row["exceptional_supports"])
        )
        assert len(supports) == 5
        stabilizer = stabilizer_permutations(supports)
        assert len(stabilizer) == row["stabilizer_order"]
        actions = action_maps(supports, stabilizer)
        orbit_sizes = orientation_orbits(actions)
        feasible_orientations = 0
        total_overlap_patterns = 0
        positive_pattern_histogram = Counter()
        first_feasible = None
        for state in itertools.product(range(4), repeat=5):
            pattern_count, group_counts = overlap_pattern_count(supports, state)
            if pattern_count:
                feasible_orientations += 1
                total_overlap_patterns += pattern_count
                positive_pattern_histogram[pattern_count] += 1
                if first_feasible is None:
                    first_feasible = {
                        "orientation": list(state),
                        "group_matching_counts": group_counts,
                    }
        properties = graph_properties(supports)
        output_rows.append(
            {
                "orbit_index": row["orbit_index"],
                "support_orbit_size": row["orbit_size"],
                "supports": [list(edge) for edge in supports],
                "support_stabilizer_order": len(stabilizer),
                "distinct_orientation_actions": len(actions),
                "orientation_orbit_count": len(orbit_sizes),
                "orientation_orbit_size_histogram": {
                    str(size): count
                    for size, count in sorted(Counter(orbit_sizes).items())
                },
                "orientation_orbit_size_sum": sum(orbit_sizes),
                "graph_properties": properties,
                "all_orientations_checked": 4**5,
                "locally_BP_feasible_orientations": feasible_orientations,
                "locally_BP_feasible_overlap_patterns": total_overlap_patterns,
                "positive_pattern_count_histogram": {
                    str(value): count
                    for value, count in sorted(positive_pattern_histogram.items())
                },
                "first_feasible": first_feasible,
            }
        )
    assert all(row["locally_BP_feasible_orientations"] == 0 for row in output_rows)
    result = {
        "model": "exact local P4 orientation and overlap-port audit at E0=79",
        "input": str(INPUT_PATH),
        "orientation_encoding": (
            "code=2*d+s: missing side varies support coordinate d and has "
            "fixed-coordinate sign s"
        ),
        "symmetry": (
            "all setwise S7 support stabilizers times all 2^7 coordinate flips; "
            "actions deduplicated before orbit enumeration"
        ),
        "local_constraint": (
            "each P4 endpoint has one exact BP deficit through each support group; "
            "ports are exhaustively perfect-matched with mutual sign compatibility"
        ),
        "port_formula_direct_square_audit": True,
        "support_orbits_checked": len(output_rows),
        "orientation_assignments_per_orbit": 4**5,
        "status": "ALL_12_LOCALLY_INFEASIBLE",
        "rows": output_rows,
    }
    RESULT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "rows": [
            {
                "id": row["orbit_index"],
                "orientation_orbits": row["orientation_orbit_count"],
                "feasible": row["locally_BP_feasible_orientations"],
            }
            for row in output_rows
        ],
    }))


if __name__ == "__main__":
    main()
