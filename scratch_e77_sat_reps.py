"""Independently generate exhaustive local representatives for E0=77.

The input is the three support orbits surviving the earlier port screen.  This
file independently expands labelled fibre states and simple overlap edges,
checks induced pair upper bounds and the support-count part of BP forced by
all ordinary C4 fibres, and canonicalizes under the exact stabilizer of each
weighted support set together with independent matched-pair sign flips.
"""

from __future__ import annotations

from collections import Counter
import itertools
import json
import math
from pathlib import Path

from scratch_e77_sat_audit import VERTICES, state_table


INPUT = Path("scratch_root_e77_port_screen.json")
OUTPUT = Path("scratch_e77_sat_reps.json")
GROUPS = tuple(range(7))
ALL_SUPPORTS = tuple(itertools.combinations(GROUPS, 2))


def label(support, bits):
    return (2 * support[0] + bits[0], 2 * support[1] + bits[1])


def sign_at(vertex, group):
    for symbol in vertex:
        if symbol // 2 == group:
            return symbol % 2
    raise KeyError(group)


def fibre_data(support, state):
    vertices = tuple(label(support, bits) for bits in VERTICES)
    internal = frozenset(
        tuple(sorted((vertices[u], vertices[v])))
        for u, v in state["edges"]
    )
    neighbours = {vertex: set() for vertex in vertices}
    for u, v in internal:
        neighbours[u].add(v)
        neighbours[v].add(u)
    ports = []
    for vertex in vertices:
        for group in support:
            counts = Counter(sign_at(other, group) for other in neighbours[vertex])
            for needed_sign in (0, 1):
                assert counts[needed_sign] <= 1
                if counts[needed_sign] == 0:
                    ports.append((vertex, group, needed_sign))
    return {"vertices": vertices, "internal": internal, "ports": tuple(ports)}


def group_matchings(oriented, group):
    stubs = []
    for fibre_index, data in enumerate(oriented):
        for vertex, port_group, needed_sign in data["ports"]:
            if port_group == group:
                stubs.append((vertex, fibre_index, needed_sign))
    if not stubs:
        return (frozenset(),)
    candidates = {stub: [] for stub in stubs}
    for left, right in itertools.combinations(stubs, 2):
        u, i, need_u = left
        v, j, need_v = right
        if i == j:
            continue
        if need_u == sign_at(v, group) and need_v == sign_at(u, group):
            candidates[left].append(right)
            candidates[right].append(left)

    answers = set()

    def visit(remaining, used_edges, chosen):
        if not remaining:
            answers.add(frozenset(chosen))
            return
        first = min(remaining, key=lambda item: sum(x in remaining for x in candidates[item]))
        for other in candidates[first]:
            if other not in remaining:
                continue
            vertex_edge = tuple(sorted((first[0], other[0])))
            if vertex_edge in used_edges:
                continue
            visit(
                remaining - {first, other},
                used_edges | {vertex_edge},
                chosen + (vertex_edge,),
            )

    visit(frozenset(stubs), frozenset(), ())
    return tuple(sorted(answers, key=lambda graph: tuple(sorted(graph))))


def neighbour_sets(vertices, graph):
    answer = {vertex: set() for vertex in vertices}
    for u, v in graph:
        answer[u].add(v)
        answer[v].add(u)
    return answer


def induced_pair_upper(vertices, graph):
    neighbours = neighbour_sets(vertices, graph)
    for u, v in itertools.combinations(vertices, 2):
        adjacency = v in neighbours[u]
        common = len(neighbours[u] & neighbours[v])
        target = 2 - len(set(u) & set(v))
        if common + adjacency > target:
            return False
    return True


def forced_c4_support_count_feasible(supports, oriented, graph):
    """Check the exact unsigned BP equations remaining after ordinary C4s.

    Every vertex outside an ordinary C4 fibre and disjoint from its support
    has exactly one neighbour in that fibre; overlap with that C4 is zero.
    Only edge counts into disjoint exceptional fibres remain unknown here.
    """
    exceptional = frozenset(supports)
    support_of = {
        vertex: support
        for support, data in zip(supports, oriented)
        for vertex in data["vertices"]
    }
    vertices = tuple(support_of)
    neighbours = neighbour_sets(vertices, graph)
    for vertex in vertices:
        own = support_of[vertex]
        disjoint_low = tuple(
            support for support in supports if set(support).isdisjoint(own)
        )
        disjoint_high = tuple(
            support
            for support in ALL_SUPPORTS
            if support not in exceptional and set(support).isdisjoint(own)
        )
        local_degree = len(neighbours[vertex])
        remaining_low_degree = 12 - local_degree - len(disjoint_high)
        if not (0 <= remaining_low_degree <= 4 * len(disjoint_low)):
            return False
        wanted = {}
        for group in GROUPS:
            if group in own:
                continue
            local_group = sum(group in support_of[other] for other in neighbours[vertex])
            forced_high_group = sum(group in support for support in disjoint_high)
            wanted[group] = 4 - local_group - forced_high_group
            if wanted[group] < 0:
                return False
        found = False
        for values in itertools.product(range(5), repeat=len(disjoint_low)):
            if sum(values) != remaining_low_degree:
                continue
            if all(
                sum(value for value, support in zip(values, disjoint_low) if group in support)
                == target
                for group, target in wanted.items()
            ):
                found = True
                break
        if not found:
            return False
    return True


def support_stabilizer(supports, deficits):
    wanted = frozenset(zip(supports, deficits))
    return tuple(
        permutation
        for permutation in itertools.permutations(GROUPS)
        if frozenset(
            (tuple(sorted((permutation[a], permutation[b]))), deficit)
            for (a, b), deficit in zip(supports, deficits)
        ) == wanted
    )


def transform_vertex(vertex, permutation, flips):
    return tuple(sorted(
        2 * permutation[symbol // 2] + ((symbol % 2) ^ flips[symbol // 2])
        for symbol in vertex
    ))


def transform_graph(graph, permutation, flips):
    return frozenset(
        tuple(sorted((
            transform_vertex(u, permutation, flips),
            transform_vertex(v, permutation, flips),
        )))
        for u, v in graph
    )


def canonicalize(graph, actions):
    images = [
        tuple(sorted(transform_graph(graph, permutation, flips)))
        for permutation, flips in actions
    ]
    return min(images)


def serialize_graph(graph):
    return [[list(u), list(v)] for u, v in sorted(graph)]


def audit_row(row, domains):
    supports = tuple(tuple(item["support"]) for item in row["exceptional_supports"])
    deficits = tuple(item["deficit"] for item in row["exceptional_supports"])
    stabilizer = support_stabilizer(supports, deficits)
    active_groups = tuple(sorted(set(itertools.chain.from_iterable(supports))))
    flips = []
    for bits in itertools.product((0, 1), repeat=len(active_groups)):
        value = [0] * 7
        for group, bit in zip(active_groups, bits):
            value[group] = bit
        flips.append(tuple(value))
    actions = tuple(itertools.product(stabilizer, flips))

    shape_count = completion_count = pair_count = forced_count = 0
    forced_graphs = []
    for state_indices in itertools.product(*(
        range(len(domains[deficit])) for deficit in deficits
    )):
        oriented = tuple(
            fibre_data(support, domains[deficit][state_index])
            for support, deficit, state_index in zip(supports, deficits, state_indices)
        )
        matchings = tuple(group_matchings(oriented, group) for group in GROUPS)
        count = math.prod(map(len, matchings))
        if not count:
            continue
        shape_count += 1
        completion_count += count
        internal = frozenset(edge for data in oriented for edge in data["internal"])
        vertices = tuple(vertex for data in oriented for vertex in data["vertices"])
        for selected in itertools.product(*matchings):
            overlap = frozenset(edge for part in selected for edge in part)
            graph = internal | overlap
            assert len(graph) == 3 * sum(deficit == 1 for deficit in deficits) + 2 * sum(deficit == 2 for deficit in deficits) + 14
            if not induced_pair_upper(vertices, graph):
                continue
            pair_count += 1
            if not forced_c4_support_count_feasible(supports, oriented, graph):
                continue
            forced_count += 1
            forced_graphs.append(graph)

    representatives = {}
    orbit_multiplicity = Counter()
    for graph in forced_graphs:
        key = canonicalize(graph, actions)
        orbit_multiplicity[key] += 1
        representatives.setdefault(key, frozenset(key))
    assert sum(orbit_multiplicity.values()) == forced_count
    return {
        "partition": list(row["partition"]),
        "source_orbit_index": row["orbit_index"],
        "supports": [list(support) for support in supports],
        "support_stabilizer_order": len(stabilizer),
        "active_sign_flip_count": len(flips),
        "symmetry_action_count": len(actions),
        "port_feasible_shapes": shape_count,
        "exact_overlap_completions": completion_count,
        "after_induced_pair_upper": pair_count,
        "after_forced_c4_support_count": forced_count,
        "local_orbit_count": len(representatives),
        "local_orbit_multiplicities": sorted(orbit_multiplicity.values()),
        "representatives": [
            {
                "representative_index": index,
                "local_graph_edges": serialize_graph(graph),
                "edge_count": len(graph),
                "multiplicity_in_enumeration": orbit_multiplicity[key],
            }
            for index, (key, graph) in enumerate(sorted(representatives.items()))
        ],
    }


def main():
    _by_edges, domains = state_table()
    source = json.loads(INPUT.read_text(encoding="utf-8"))
    rows = [row for row in source["rows"] if row["locally_port_feasible_assignments"]]
    assert len(rows) == 3
    audited = [audit_row(row, domains) for row in rows]
    assert [row["after_forced_c4_support_count"] for row in audited] == [0, 0, 512]
    assert [row["local_orbit_count"] for row in audited] == [0, 0, 3]
    result = {
        "model": "independent exhaustive local E0=77 representative generator",
        "input": str(INPUT),
        "coverage": (
            "all labelled locally admissible fibre states, all distinct-simple-edge "
            "overlap port matchings, exact induced pair upper bounds, and exact unsigned "
            "BP support-count feasibility forced by ordinary C4 fibres"
        ),
        "symmetry": (
            "full S7 support stabilizer times all active matched-pair sign flips; "
            "canonicalization only after exhaustive labelled generation"
        ),
        "claim_boundary": "local necessary conditions only; representatives are not full lifts",
        "rows": audited,
        "surviving_support_orbits": 1,
        "surviving_local_orbits": 3,
        "ok": True,
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": True,
        "forced_counts": [row["after_forced_c4_support_count"] for row in audited],
        "orbit_counts": [row["local_orbit_count"] for row in audited],
        "orbit_multiplicities": audited[-1]["local_orbit_multiplicities"],
    }))


if __name__ == "__main__":
    main()
