"""Independent finite audit for the three E0=77 port-screen survivors.

This deliberately does not import the routines that produced
``scratch_root_e77_port_screen.json``.  It checks the four/four-vertex fibre
state table directly from the local BP capacities and outer-pair inequality,
checks the weighted support orbits under S_7, and re-enumerates every labelled
state assignment with an exact simple-edge port matching DFS.
"""

from __future__ import annotations

from collections import Counter, defaultdict
import itertools
import json
from pathlib import Path


INPUT = Path("scratch_root_e77_port_screen.json")
OUTPUT = Path("scratch_e77_sat_audit.json")
VERTICES = tuple(itertools.product((0, 1), repeat=2))
PAIRS = tuple(itertools.combinations(range(4), 2))
SIDES = tuple(
    pair
    for pair in PAIRS
    if sum(VERTICES[pair[0]][q] != VERTICES[pair[1]][q] for q in range(2)) == 1
)
DIAGONALS = tuple(pair for pair in PAIRS if pair not in SIDES)


def locally_admissible(selected: frozenset[tuple[int, int]]) -> bool:
    # BP gives capacity one for each (support coordinate, required sign) bin.
    for u in range(4):
        for coordinate in range(2):
            for required_sign in (0, 1):
                used = sum(
                    tuple(sorted((u, v))) in selected
                    and VERTICES[v][coordinate] == required_sign
                    for v in range(4)
                    if v != u
                )
                if used > 1:
                    return False

    # Every fixed internal common neighbour is also an outer common neighbour.
    # Hence it cannot exceed 2-|label intersection|-adjacency.
    for u, v in PAIRS:
        common = sum(
            tuple(sorted((u, w))) in selected
            and tuple(sorted((v, w))) in selected
            for w in range(4)
            if w not in (u, v)
        )
        adjacency = (u, v) in selected
        intersection = sum(VERTICES[u][q] == VERTICES[v][q] for q in range(2))
        if common + adjacency > 2 - intersection:
            return False
    return True


def state_table():
    by_edges: dict[int, list[dict[str, object]]] = defaultdict(list)
    for bits in itertools.product((0, 1), repeat=6):
        selected = frozenset(pair for pair, bit in zip(PAIRS, bits) if bit)
        if locally_admissible(selected):
            by_edges[len(selected)].append({
                "edges": tuple(sorted(selected)),
                "bit_word": bits,
            })
    # E0 deficit is 4 minus the number of same-fibre edges.
    delta1 = by_edges[3]
    delta2 = by_edges[2]
    assert len(delta1) == 4
    assert all(set(state["edges"]).issubset(SIDES) for state in delta1)
    assert len(delta2) == 7
    assert Counter(
        "two_diagonals"
        if set(state["edges"]) == set(DIAGONALS)
        else "adjacent_sides"
        if len(set(tuple(state["edges"])[0]) & set(tuple(state["edges"])[1])) == 1
        else "opposite_sides"
        for state in delta2
    ) == Counter({"adjacent_sides": 4, "opposite_sides": 2, "two_diagonals": 1})
    return by_edges, {1: tuple(delta1), 2: tuple(delta2)}


def fibre_ports(support, selected, fibre_index):
    adjacency = [set() for _ in range(4)]
    for u, v in selected:
        adjacency[u].add(v)
        adjacency[v].add(u)
    ports = []
    for u, signs in enumerate(VERTICES):
        for coordinate, group in enumerate(support):
            for required_sign in (0, 1):
                count = sum(
                    VERTICES[v][coordinate] == required_sign
                    for v in adjacency[u]
                )
                assert count <= 1
                if count == 0:
                    ports.append((group, fibre_index, u, signs[coordinate], required_sign))
    return ports


def simple_matching_count(ports):
    """Count port matchings whose matched vertex pairs are distinct edges."""
    ports = tuple(ports)
    memo = {}

    def compatible(a, b):
        return a[1] != b[1] and a[3] == b[4] and b[3] == a[4]

    def visit(indices, used_edges):
        key = (indices, tuple(sorted(used_edges)))
        if key in memo:
            return memo[key]
        if not indices:
            return 1
        first = indices[0]
        total = 0
        for position, other in enumerate(indices[1:], 1):
            if not compatible(ports[first], ports[other]):
                continue
            endpoint_a = (ports[first][1], ports[first][2])
            endpoint_b = (ports[other][1], ports[other][2])
            edge = tuple(sorted((endpoint_a, endpoint_b)))
            if edge in used_edges:
                continue
            total += visit(
                indices[1:position] + indices[position + 1 :],
                used_edges | {edge},
            )
        memo[key] = total
        return total

    return visit(tuple(range(len(ports))), frozenset())


def canonical_weighted_support(exceptional):
    weight = {
        tuple(item["support"]): item["deficit"]
        for item in exceptional
    }
    words = []
    for permutation in itertools.permutations(range(7)):
        words.append(tuple(
            weight.get(tuple(sorted((permutation[u], permutation[v]))), 0)
            for u, v in itertools.combinations(range(7), 2)
        ))
    canonical = min(words)
    orbit_size = len(set(words))
    return canonical, orbit_size


def audit_row(row, domains):
    exceptional = row["exceptional_supports"]
    assert sum(item["deficit"] for item in exceptional) == 7
    assert len({tuple(item["support"]) for item in exceptional}) == len(exceptional)
    assert all(
        list(itertools.combinations(range(7), 2))[item["support_index"]]
        == tuple(item["support"])
        for item in exceptional
    )

    positive = []
    total = 1
    for item in exceptional:
        total *= len(domains[item["deficit"]])
    for state_indices in itertools.product(*(
        range(len(domains[item["deficit"]])) for item in exceptional
    )):
        by_group = [[] for _ in range(7)]
        for fibre_index, (item, state_index) in enumerate(zip(exceptional, state_indices)):
            state = domains[item["deficit"]][state_index]
            for port in fibre_ports(tuple(item["support"]), state["edges"], fibre_index):
                by_group[port[0]].append(port)
        counts = tuple(simple_matching_count(group) for group in by_group)
        if all(counts):
            positive.append({
                "state_indices": state_indices,
                "matching_counts_by_group": counts,
                "matching_product": __import__("math").prod(counts),
            })
    canonical, orbit_size = canonical_weighted_support(exceptional)
    assert total == row["labelled_fibre_state_assignments"]
    assert len(positive) == row["locally_port_feasible_assignments"] == 16
    assert orbit_size == row["orbit_size"]
    return {
        "partition": row["partition"],
        "orbit_index": row["orbit_index"],
        "exceptional_supports": exceptional,
        "weighted_support_canonical_word": canonical,
        "independent_orbit_size": orbit_size,
        "labelled_state_assignments": total,
        "simple_port_feasible_assignments": len(positive),
        "matching_product_min": min(item["matching_product"] for item in positive),
        "matching_product_max": max(item["matching_product"] for item in positive),
        "positive_assignments": positive,
    }


def main():
    by_edges, domains = state_table()
    source = json.loads(INPUT.read_text(encoding="utf-8"))
    rows = [row for row in source["rows"] if row["locally_port_feasible_assignments"]]
    assert len(rows) == 3
    expected_keys = {
        ((2, 1, 1, 1, 1, 1), 0),
        ((1, 1, 1, 1, 1, 1, 1), 2),
        ((1, 1, 1, 1, 1, 1, 1), 22),
    }
    assert {(tuple(row["partition"]), row["orbit_index"]) for row in rows} == expected_keys
    audited = [audit_row(row, domains) for row in rows]
    assert len({tuple(row["weighted_support_canonical_word"]) for row in audited}) == 3
    result = {
        "model": "independent E0=77 fibre-state/support/simple-port audit",
        "input": str(INPUT),
        "local_state_enumeration": {
            "all_admissible_counts_by_edge_count": {
                str(count): len(states) for count, states in sorted(by_edges.items())
            },
            "delta1_count": len(domains[1]),
            "delta1_classification": "four labelled P4 states (three cube sides)",
            "delta2_count": len(domains[2]),
            "delta2_type_counts": {
                "adjacent_sides": 4,
                "opposite_sides": 2,
                "two_diagonals": 1,
            },
            "derivation": "all 64 edge subsets; BP bin capacity and pair upper bounds only",
        },
        "support_survivor_count": len(audited),
        "support_orbits_pairwise_distinct": True,
        "port_matching": "exact DFS with distinct simple edges; no closed-form Hall shortcut",
        "rows": audited,
        "ok": True,
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": True,
        "state_counts": [len(domains[1]), len(domains[2])],
        "survivors": [(row["partition"], row["orbit_index"]) for row in audited],
        "positive_assignments": [row["simple_port_feasible_assignments"] for row in audited],
        "matching_product_ranges": [
            [row["matching_product_min"], row["matching_product_max"]]
            for row in audited
        ],
    }))


if __name__ == "__main__":
    main()
