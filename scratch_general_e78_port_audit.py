"""Solver-free local overlap-port audit for E0=78 compression survivors.

All labelled same-support fibre states are enumerated: four P4 states for
deficit one, and the six two-side states plus the two-diagonal state for
deficit two.  No orientation or fibre-type WLOG assumption is used.
"""

from __future__ import annotations

import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path


INPUT_PATH = Path("scratch_general_e78_compression_audit.json")
RESULT_PATH = Path("scratch_general_e78_port_audit.json")
VERTICES = tuple(itertools.product(range(2), repeat=2))
PAIRS = tuple(itertools.combinations(range(4), 2))
SIDES = tuple(
    pair
    for pair in PAIRS
    if sum(a != b for a, b in zip(VERTICES[pair[0]], VERTICES[pair[1]])) == 1
)
DIAGONALS = tuple(pair for pair in PAIRS if pair not in SIDES)
assert len(SIDES) == 4 and len(DIAGONALS) == 2


def state_type(selected):
    if set(selected) == set(DIAGONALS):
        return "two_diagonals"
    degrees = [0] * 4
    for u, v in selected:
        degrees[u] += 1
        degrees[v] += 1
    return "adjacent_sides" if max(degrees) == 2 else "opposite_sides"


FIBRE_STATES = {
    1: tuple(
        {"edges": tuple(sorted(selected)), "type": "P4"}
        for selected in itertools.combinations(SIDES, 3)
    ),
    2: tuple(
        [
            {"edges": tuple(sorted(selected)), "type": state_type(selected)}
            for selected in itertools.combinations(SIDES, 2)
        ]
        + [{"edges": tuple(sorted(DIAGONALS)), "type": "two_diagonals"}]
    ),
}
assert len(FIBRE_STATES[1]) == 4 and len(FIBRE_STATES[2]) == 7


def fibre_ports(support, selected_edges, fibre_index):
    adjacency = [set() for _ in range(4)]
    for u, v in selected_edges:
        adjacency[u].add(v)
        adjacency[v].add(u)
    ports = []
    for u, signs in enumerate(VERTICES):
        for coordinate, group in enumerate(support):
            for required_sign in range(2):
                count = sum(
                    VERTICES[v][coordinate] == required_sign
                    for v in adjacency[u]
                )
                assert count <= 1
                if count == 0:
                    ports.append(
                        (group, fibre_index, u, signs[coordinate], required_sign)
                    )
    # Four overlap incidences per unit deficit.
    return ports


def same_type_matchable(ports):
    total = len(ports)
    if total % 2:
        return False
    by_fibre = Counter(port[1] for port in ports)
    return not by_fibre or max(by_fibre.values()) <= total // 2


def cross_type_matchable(left, right):
    if len(left) != len(right):
        return False
    total = len(right)
    left_by_fibre = Counter(port[1] for port in left)
    right_by_fibre = Counter(port[1] for port in right)
    # Hall's only nontrivial subsets are those contained in one forbidden
    # diagonal fibre block.  Applying it from the left is sufficient.
    return all(
        count <= total - right_by_fibre[fibre]
        for fibre, count in left_by_fibre.items()
    )


def group_matchable(ports):
    categories = defaultdict(list)
    for item in ports:
        _group, _fibre, _vertex, sigma, required = item
        categories[(sigma, required)].append(item)
    return (
        same_type_matchable(categories[(0, 0)])
        and same_type_matchable(categories[(1, 1)])
        and cross_type_matchable(categories[(0, 1)], categories[(1, 0)])
    )


def direct_matching_exists(ports):
    """Independent small backtracking control for the closed-form test."""
    ports = tuple(ports)

    def compatible(a, b):
        return (
            a[1] != b[1]
            and a[3] == b[4]
            and b[3] == a[4]
        )

    memo = {}

    def visit(remaining):
        if not remaining:
            return True
        if remaining in memo:
            return memo[remaining]
        first = remaining[0]
        for q in range(1, len(remaining)):
            if compatible(first, remaining[q]) and visit(
                remaining[1:q] + remaining[q + 1 :]
            ):
                memo[remaining] = True
                return True
        memo[remaining] = False
        return False

    return visit(tuple(range(len(ports)))) if False else _direct_ports(ports, compatible)


def _direct_ports(ports, compatible):
    memo = {}

    def visit(indices):
        if not indices:
            return True
        if indices in memo:
            return memo[indices]
        first = indices[0]
        answer = any(
            compatible(ports[first], ports[other])
            and visit(indices[1:q] + indices[q + 1 :])
            for q, other in enumerate(indices[1:], 1)
        )
        memo[indices] = answer
        return answer

    return visit(tuple(range(len(ports))))


def matching_cost_profile(ports):
    """Enumerate exact matchings, grouped by sum of squared block totals."""
    ports = tuple(ports)
    profile = Counter()

    def compatible(a, b):
        return (
            a[1] != b[1]
            and a[3] == b[4]
            and b[3] == a[4]
        )

    def visit(indices, block_counts):
        if not indices:
            cost = sum(value * value for value in block_counts.values())
            profile[cost] += 1
            return
        first = indices[0]
        for q, other in enumerate(indices[1:], 1):
            if not compatible(ports[first], ports[other]):
                continue
            pair = tuple(sorted((ports[first][1], ports[other][1])))
            block_counts[pair] += 1
            visit(indices[1:q] + indices[q + 1 :], block_counts)
            block_counts[pair] -= 1
            if not block_counts[pair]:
                del block_counts[pair]

    visit(tuple(range(len(ports))), Counter())
    return profile


def assignment_ports(exceptional, choices):
    by_group = [[] for _ in range(7)]
    for fibre_index, (item, choice) in enumerate(zip(exceptional, choices)):
        ports = fibre_ports(tuple(item["support"]), choice["edges"], fibre_index)
        assert len(ports) == 4 * item["deficit"]
        for port in ports:
            by_group[port[0]].append(port)
    return by_group


def audit_row(row):
    exceptional = row["exceptional_supports"]
    domains = [FIBRE_STATES[item["deficit"]] for item in exceptional]
    total = 1
    for domain in domains:
        total *= len(domain)
    feasible = 0
    spectral_feasible = 0
    type_histogram = Counter()
    spectral_type_histogram = Counter()
    first = None
    first_spectral = None
    direct_controls = 0
    for choices in itertools.product(*domains):
        by_group = assignment_ports(exceptional, choices)
        closed = [group_matchable(ports) for ports in by_group]
        if all(closed):
            # Cross-check every positive group by an independent matching DFS.
            direct = [direct_matching_exists(ports) for ports in by_group]
            direct_controls += 1
            assert direct == closed
            feasible += 1
            types = tuple(choice["type"] for choice in choices)
            type_histogram[types] += 1
            profiles = [matching_cost_profile(ports) for ports in by_group]
            assert all(profiles)
            overlap_minimum = sum(min(profile) for profile in profiles)
            overlap_minimum_count = 1
            total_overlap_matchings = 1
            for profile in profiles:
                overlap_minimum_count *= profile[min(profile)]
                total_overlap_matchings *= sum(profile.values())
            disjoint_minimum = row["disjoint_integer"]["minimum_square"]
            joint_budget = row["joint_off_diagonal_square_budget"]
            passes_spectral = overlap_minimum + disjoint_minimum <= joint_budget
            if passes_spectral:
                spectral_feasible += 1
                spectral_type_histogram[types] += 1
                if first_spectral is None:
                    first_spectral = {
                        "state_indices": [domain.index(choice) for domain, choice in zip(domains, choices)],
                        "types": list(types),
                        "minimum_overlap_square": overlap_minimum,
                        "minimum_overlap_matching_count": overlap_minimum_count,
                        "all_overlap_matching_count": total_overlap_matchings,
                        "disjoint_minimum_square": disjoint_minimum,
                        "joint_square_budget": joint_budget,
                    }
            if first is None:
                first = {
                    "state_indices": [domain.index(choice) for domain, choice in zip(domains, choices)],
                    "types": list(types),
                    "port_counts_by_group": [len(ports) for ports in by_group],
                }
    return {
        "partition": row["partition"],
        "orbit_index": row["orbit_index"],
        "support_orbit_size": row["orbit_size"],
        "exceptional_supports": exceptional,
        "labelled_fibre_state_assignments": total,
        "locally_port_feasible_assignments": feasible,
        "locally_port_and_spectral_feasible_assignments": spectral_feasible,
        "positive_assignments_direct_DFS_checked": direct_controls,
        "feasible_type_histogram": {
            "|".join(types): count for types, count in sorted(type_histogram.items())
        },
        "spectral_feasible_type_histogram": {
            "|".join(types): count
            for types, count in sorted(spectral_type_histogram.items())
        },
        "first_feasible": first,
        "first_spectral_feasible": first_spectral,
    }


def main():
    source = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    assert source["phase"] == "exact_integer_disjoint"
    compression_rows = [
        row for row in source["rows"] if row["passes_compression_square_and_BP"]
    ]
    assert len(compression_rows) == 50
    rows = [audit_row(row) for row in compression_rows]
    result = {
        "model": "solver-free local overlap-port audit for E0=78",
        "input": str(INPUT_PATH),
        "fibre_state_counts": {"deficit_1_P4": 4, "deficit_2": 7},
        "deficit_2_types": {
            "adjacent_sides": 4,
            "opposite_sides": 2,
            "two_diagonals": 1,
        },
        "coverage": (
            "all labelled fibre states on every exact-integer compression survivor; "
            "no local orientation or type normalization"
        ),
        "matching_test": (
            "closed-form complete-multipartite/Hall test; every positive assignment "
            "cross-checked groupwise by independent exact matching DFS"
        ),
        "compression_survivor_orbits": len(rows),
        "local_survivor_orbits": sum(row["locally_port_feasible_assignments"] > 0 for row in rows),
        "local_and_spectral_survivor_orbits": sum(
            row["locally_port_and_spectral_feasible_assignments"] > 0 for row in rows
        ),
        "rows": rows,
    }
    RESULT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    grouped = defaultdict(lambda: {
        "orbits": 0,
        "port_survivors": 0,
        "port_assignments": 0,
        "spectral_survivors": 0,
        "spectral_assignments": 0,
    })
    for row in rows:
        key = "+".join(map(str, row["partition"]))
        grouped[key]["orbits"] += 1
        grouped[key]["port_survivors"] += row["locally_port_feasible_assignments"] > 0
        grouped[key]["port_assignments"] += row["locally_port_feasible_assignments"]
        grouped[key]["spectral_survivors"] += (
            row["locally_port_and_spectral_feasible_assignments"] > 0
        )
        grouped[key]["spectral_assignments"] += (
            row["locally_port_and_spectral_feasible_assignments"]
        )
    print(json.dumps({
        "compression_orbits": len(rows),
        "local_survivor_orbits": result["local_survivor_orbits"],
        "local_and_spectral_survivor_orbits": result["local_and_spectral_survivor_orbits"],
        "by_partition": dict(grouped),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
