"""Independent solver-free fibre-port screen for the E0=76 frontier.

The input is the exact S7 placement/compression audit.  Every locally allowed
labelled graph on each exceptional four-vertex fibre is generated directly
from the root-neighbour BP capacity inequalities, rather than imported from a
previous E0 case.  All Cartesian products are then tested for exact port
matchability, group by group.

This is only a necessary local test.  It neither constructs nor excludes a
full 84-vertex outer graph.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import itertools
import json
from pathlib import Path


DEFAULT_INPUT = Path("scratch_general_e76_compression_audit.json")
DEFAULT_OUTPUT = Path("scratch_root_e76_port_screen.json")
VERTICES = tuple(itertools.product(range(2), repeat=2))
PAIRS = tuple(itertools.combinations(range(4), 2))


def locally_allowed_edges(deficit: int):
    """Enumerate all labelled same-fibre edge sets from the exact BP cap."""
    edge_count = 4 - deficit
    answer = []
    for selected in itertools.combinations(PAIRS, edge_count):
        adjacency = [set() for _ in VERTICES]
        for u, v in selected:
            adjacency[u].add(v)
            adjacency[v].add(u)
        # For each root-neighbour symbol there is room for at most one
        # already supplied common neighbour inside this fibre.
        if not all(
            sum(VERTICES[v][coordinate] == sign for v in adjacency[u]) <= 1
            for u in range(4)
            for coordinate in range(2)
            for sign in range(2)
        ):
            continue
        answer.append(tuple(selected))
    return tuple(answer)


FIBRE_STATES = {
    deficit: locally_allowed_edges(deficit) for deficit in range(1, 5)
}
assert {key: len(value) for key, value in FIBRE_STATES.items()} == {
    1: 4,
    2: 7,
    3: 6,
    4: 1,
}


def fibre_ports(support, selected_edges, fibre_index):
    adjacency = [set() for _ in VERTICES]
    for u, v in selected_edges:
        adjacency[u].add(v)
        adjacency[v].add(u)
    ports = []
    for u, signs in enumerate(VERTICES):
        for coordinate, group in enumerate(support):
            for required_sign in range(2):
                supplied = sum(
                    VERTICES[v][coordinate] == required_sign
                    for v in adjacency[u]
                )
                assert supplied <= 1
                if supplied == 0:
                    ports.append(
                        (group, fibre_index, u, signs[coordinate], required_sign)
                    )
    return tuple(ports)


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
    """Small independent DFS control for the closed-form Hall test."""
    ports = tuple(ports)
    compatible = {
        i: tuple(
            j
            for j in range(len(ports))
            if j != i
            and ports[i][1] != ports[j][1]
            and ports[i][3] == ports[j][4]
            and ports[j][3] == ports[i][4]
        )
        for i in range(len(ports))
    }
    memo = {}

    def visit(remaining):
        if not remaining:
            return True
        if remaining in memo:
            return memo[remaining]
        first = min(
            remaining,
            key=lambda i: sum(j in remaining for j in compatible[i]),
        )
        rest = remaining - {first}
        answer = any(
            visit(frozenset(rest - {other}))
            for other in compatible[first]
            if other in rest
        )
        memo[remaining] = answer
        return answer

    return visit(frozenset(range(len(ports))))


def assignment_ports(exceptional, choices):
    by_group = [[] for _ in range(7)]
    for fibre_index, (item, selected) in enumerate(zip(exceptional, choices)):
        ports = fibre_ports(tuple(item["support"]), selected, fibre_index)
        assert len(ports) == 4 * item["deficit"]
        for port in ports:
            by_group[port[0]].append(port)
    return tuple(tuple(row) for row in by_group)


def support_balance_feasible(exceptional):
    """Orientation-free necessary port balance at each root group.

    A deficit-d fibre contributes exactly 2d ports at each endpoint of its
    support.  Since two ports of the same fibre can never be paired, no one
    incident deficit may exceed the sum of all the others.
    """
    incident = [[] for _ in range(7)]
    for item in exceptional:
        for group in item["support"]:
            incident[group].append(item["deficit"])
    return all(
        not values or max(values) <= sum(values) - max(values)
        for values in incident
    )


def audit_row(row, direct_control_limit):
    exceptional = row["exceptional_supports"]
    domains = tuple(FIBRE_STATES[item["deficit"]] for item in exceptional)
    tested = 1
    for domain in domains:
        tested *= len(domain)
    balanced = support_balance_feasible(exceptional)
    if not balanced:
        return {
            "partition": row["partition"],
            "orbit_index": row["orbit_index"],
            "orbit_size": row["orbit_size"],
            "exceptional_supports": exceptional,
            "support_balance_feasible": False,
            "labelled_fibre_state_assignments": tested,
            "state_assignments_enumerated": 0,
            "locally_port_feasible_assignments": 0,
            "direct_DFS_control_assignments": 0,
            "feasible_port_count_histogram": {},
            "first_feasible": None,
        }
    feasible = 0
    direct_checked = 0
    first = None
    port_histogram = Counter()
    for choices in itertools.product(*domains):
        by_group = assignment_ports(exceptional, choices)
        closed = tuple(group_matchable(ports) for ports in by_group)
        if direct_checked < direct_control_limit:
            direct = tuple(direct_matching_exists(ports) for ports in by_group)
            assert direct == closed
            direct_checked += 1
        if not all(closed):
            continue
        feasible += 1
        counts = tuple(len(ports) for ports in by_group)
        port_histogram[counts] += 1
        if first is None:
            first = {
                "state_indices": [
                    domain.index(choice)
                    for domain, choice in zip(domains, choices)
                ],
                "port_counts_by_group": list(counts),
            }
    return {
        "partition": row["partition"],
        "orbit_index": row["orbit_index"],
        "orbit_size": row["orbit_size"],
        "exceptional_supports": exceptional,
        "support_balance_feasible": True,
        "labelled_fibre_state_assignments": tested,
        "state_assignments_enumerated": tested,
        "locally_port_feasible_assignments": feasible,
        "direct_DFS_control_assignments": direct_checked,
        "feasible_port_count_histogram": {
            ",".join(map(str, key)): value
            for key, value in sorted(port_histogram.items())
        },
        "first_feasible": first,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--direct-controls", type=int, default=8)
    args = parser.parse_args()
    source = json.loads(args.input.read_text(encoding="utf-8"))
    candidates = [
        row for row in source["rows"]
        if row["passes_overlap_and_real_relaxation"]
    ]
    rows = []
    for offset, row in enumerate(candidates):
        result = audit_row(row, args.direct_controls)
        rows.append(result)
        print(json.dumps({
            "offset": offset,
            "partition": result["partition"],
            "orbit_index": result["orbit_index"],
            "tested": result["labelled_fibre_state_assignments"],
            "feasible": result["locally_port_feasible_assignments"],
        }), flush=True)
    grouped = defaultdict(lambda: {
        "input_orbits": 0,
        "support_balance_survivors": 0,
        "domain_assignments": 0,
        "assignments_enumerated": 0,
        "surviving_orbits": 0,
        "feasible_assignments": 0,
    })
    for row in rows:
        key = "+".join(map(str, row["partition"]))
        grouped[key]["input_orbits"] += 1
        grouped[key]["support_balance_survivors"] += row[
            "support_balance_feasible"
        ]
        grouped[key]["domain_assignments"] += row[
            "labelled_fibre_state_assignments"
        ]
        grouped[key]["assignments_enumerated"] += row[
            "state_assignments_enumerated"
        ]
        grouped[key]["surviving_orbits"] += (
            row["locally_port_feasible_assignments"] > 0
        )
        grouped[key]["feasible_assignments"] += row[
            "locally_port_feasible_assignments"
        ]
    result = {
        "model": "independent exhaustive E0=76 labelled fibre-state port screen",
        "input": str(args.input),
        "fibre_state_counts": {
            f"delta{key}": len(value) for key, value in FIBRE_STATES.items()
        },
        "coverage": (
            "all locally allowed labelled fibre states on every solver-free "
            "overlap/rational-real compression survivor"
        ),
        "matching_test": (
            "exact closed-form multipartite/Hall criterion, with bounded "
            "independent matching-DFS controls on every input orbit"
        ),
        "claim_boundary": (
            "Necessary local port matchability only; positive rows are not "
            "full 84-vertex lifts."
        ),
        "input_orbits": len(rows),
        "surviving_orbits": sum(
            row["locally_port_feasible_assignments"] > 0 for row in rows
        ),
        "by_partition": dict(grouped),
        "rows": rows,
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "input_orbits": result["input_orbits"],
        "surviving_orbits": result["surviving_orbits"],
        "by_partition": result["by_partition"],
    }, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
