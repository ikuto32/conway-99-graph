"""Solver-free local audit of the five exceptional P4 fibres at E0=79.

The compression audit leaves twelve S7-orbits of possible exceptional
supports.  This script applies consequences of the *actual* fibre shapes,
which the 21 by 21 compression deliberately forgot.

For completeness it also enumerates every P4 orientation and every possible
overlap-edge completion for the support types which survive the first simple
test.  This is a bounded 20-vertex calculation; it is not a full SAT search.
"""

from __future__ import annotations

import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path


INPUT = Path("scratch_general_e79_compression_audit.json")
OUTPUT = Path("scratch_general_e79_local_audit.json")

GROUPS = range(7)
ALL_SUPPORTS = tuple(itertools.combinations(GROUPS, 2))
ALL_GROUP_PERMS = tuple(itertools.permutations(GROUPS))


def support_key(support):
    return tuple(sorted(support))


def apply_group_perm(support, permutation):
    return support_key((permutation[support[0]], permutation[support[1]]))


def stabilizer(supports):
    wanted = frozenset(supports)
    return tuple(
        permutation
        for permutation in ALL_GROUP_PERMS
        if frozenset(apply_group_perm(edge, permutation) for edge in supports) == wanted
    )


def group_degrees(supports):
    degrees = [0] * 7
    for a, b in supports:
        degrees[a] += 1
        degrees[b] += 1
    return tuple(degrees)


def line_degrees(supports):
    return tuple(
        sum(bool(set(edge) & set(other)) for other in supports if other != edge)
        for edge in supports
    )


def is_bipartite(supports):
    adjacency = [set() for _ in GROUPS]
    for u, v in supports:
        adjacency[u].add(v)
        adjacency[v].add(u)
    colours = {}
    for seed in GROUPS:
        if seed in colours or not adjacency[seed]:
            continue
        colours[seed] = 0
        queue = [seed]
        while queue:
            u = queue.pop()
            for v in adjacency[u]:
                if v not in colours:
                    colours[v] = 1 - colours[u]
                    queue.append(v)
                elif colours[v] == colours[u]:
                    return False
    return True


def all_five_support_sets_audit():
    """Classify all C(21,5) placements, independently of compression orbits."""
    no_leaf = []
    for supports in itertools.combinations(ALL_SUPPORTS, 5):
        degrees = group_degrees(supports)
        if 1 not in degrees:
            no_leaf.append(supports)
    signatures = Counter(tuple(sorted(group_degrees(row), reverse=True)) for row in no_leaf)
    bipartite = [row for row in no_leaf if is_bipartite(row)]
    assert signatures == {
        (3, 3, 2, 2, 0, 0, 0): 210,  # K4-e
        (2, 2, 2, 2, 2, 0, 0): 252,  # C5
    }
    assert not bipartite
    representative_rows = []
    for signature, count in sorted(signatures.items(), reverse=True):
        representative = next(
            row for row in no_leaf
            if tuple(sorted(group_degrees(row), reverse=True)) == signature
        )
        representative_rows.append({
            "degree_sequence": signature,
            "labelled_count": count,
            "representative": representative,
            "stabilizer_order": len(stabilizer(representative)),
            "bipartite": is_bipartite(representative),
        })
    return {
        "all_five_support_sets": len(tuple(itertools.combinations(ALL_SUPPORTS, 5))),
        "fails_degree_one_port_test": 20349 - len(no_leaf),
        "passes_degree_one_port_test": len(no_leaf),
        "passes_degree_one_port_test_orbits": len(signatures),
        "passes_port_bipartiteness_test": len(bipartite),
        "representatives": representative_rows,
    }


def vertex_label(support, bits):
    return tuple(sorted((2 * support[0] + bits[0], 2 * support[1] + bits[1])))


def orientation_data(support, missing_index):
    """Return internal P4 edges, endpoints, and each endpoint's two BP needs."""
    bit_rows = tuple(itertools.product((0, 1), repeat=2))
    vertices = tuple(vertex_label(support, bits) for bits in bit_rows)
    sides = tuple(
        (u, v)
        for u, v in itertools.combinations(range(4), 2)
        if sum(bit_rows[u][axis] != bit_rows[v][axis] for axis in (0, 1)) == 1
    )
    missing = sides[missing_index]
    internal = frozenset(
        tuple(sorted((vertices[u], vertices[v])))
        for u, v in sides
        if (u, v) != missing
    )
    neighbours = {vertex: set() for vertex in vertices}
    for u, v in internal:
        neighbours[u].add(v)
        neighbours[v].add(u)
    endpoints = tuple(vertices[index] for index in missing)
    needs = {}
    for vertex in endpoints:
        signs = {symbol // 2: symbol % 2 for symbol in vertex}
        need = {}
        for group in support:
            seen = Counter(symbol % 2 for other in neighbours[vertex] for symbol in other if symbol // 2 == group)
            missing_signs = [sign for sign in (0, 1) if seen[sign] == 0]
            assert len(missing_signs) == 1
            need[group] = missing_signs[0]
            assert seen[1 - missing_signs[0]] == 1
        needs[vertex] = need
    return {
        "vertices": vertices,
        "internal": internal,
        "endpoints": endpoints,
        "needs": needs,
    }


def sign_at(vertex, group):
    for symbol in vertex:
        if symbol // 2 == group:
            return symbol % 2
    raise KeyError(group)


def perfect_matchings(stubs, candidates):
    """Enumerate perfect matchings of a small compatibility graph."""
    stubs = frozenset(stubs)
    adjacency = defaultdict(list)
    for u, v in candidates:
        adjacency[u].append(v)
        adjacency[v].append(u)

    def visit(remaining, chosen):
        if not remaining:
            yield frozenset(chosen)
            return
        u = min(remaining)
        for v in adjacency[u]:
            if v not in remaining:
                continue
            edge = tuple(sorted((u[0], v[0])))
            yield from visit(remaining - {u, v}, chosen + (edge,))

    yield from visit(stubs, ())


def overlap_completions(supports, oriented):
    """Meet every endpoint's missing BP quota in each of its own groups."""
    by_group = []
    for group in GROUPS:
        incident = [index for index, support in enumerate(supports) if group in support]
        if not incident:
            continue
        stubs = []
        for index in incident:
            for vertex in oriented[index]["endpoints"]:
                stubs.append((vertex, index))
        candidates = []
        for left, right in itertools.combinations(stubs, 2):
            u, i = left
            v, j = right
            if i == j:
                continue
            if oriented[i]["needs"][u][group] != sign_at(v, group):
                continue
            if oriented[j]["needs"][v][group] != sign_at(u, group):
                continue
            candidates.append((left, right))
        matches = tuple(perfect_matchings(stubs, candidates))
        if not matches:
            return
        by_group.append(matches)
    for selections in itertools.product(*by_group):
        combined = frozenset(edge for matching in selections for edge in matching)
        # Five P4 fibres have twenty endpoint/group deficits, two per edge.
        assert len(combined) == 10
        yield combined


def neighbour_sets(vertices, edges):
    neighbours = {vertex: set() for vertex in vertices}
    for u, v in edges:
        neighbours[u].add(v)
        neighbours[v].add(u)
    return neighbours


def induced_pair_upper(vertices, edges):
    neighbours = neighbour_sets(vertices, edges)
    for u, v in itertools.combinations(vertices, 2):
        direct = int(tuple(sorted((u, v))) in edges)
        common = len(neighbours[u] & neighbours[v])
        target = 2 - len(set(u) & set(v))
        if direct + common > target:
            return False
    return True


def exceptional_disjoint_support_feasible(supports, oriented, overlap_edges):
    """Check support-level BP completion after forced ordinary-C4 blocks.

    If F is P4 and G is an ordinary C4 with disjoint support, every vertex of
    F has exactly one neighbour in G.  Thus only a small, exact number of
    neighbours may remain in the exceptional disjoint fibres.  For each
    external group we solve the resulting integer incidence equations.  We
    deliberately ignore signs and actual vertices here, so failure is a
    rigorous obstruction while success is only necessary.
    """
    support_of = {
        vertex: support
        for index, support in enumerate(supports)
        for vertex in oriented[index]["vertices"]
    }
    overlap_neighbours = neighbour_sets(tuple(support_of), overlap_edges)
    details = []
    for index, support in enumerate(supports):
        disjoint_indices = [
            other
            for other, other_support in enumerate(supports)
            if not set(support) & set(other_support)
        ]
        r = len(disjoint_indices)
        for vertex in oriented[index]["vertices"]:
            endpoint = vertex in oriented[index]["endpoints"]
            required_degree = r - 1 if endpoint else r
            if required_degree < 0:
                return False, {
                    "reason": "negative exceptional-disjoint degree",
                    "support": support,
                    "vertex": vertex,
                    "r": r,
                    "required_degree": required_degree,
                }
            external_groups = [group for group in GROUPS if group not in support]
            wanted = {}
            for group in external_groups:
                t = sum(group in supports[other] for other in disjoint_indices)
                o = sum(
                    group in support_of[neighbour]
                    for neighbour in overlap_neighbours[vertex]
                )
                wanted[group] = t - o
                if wanted[group] < 0:
                    return False, {
                        "reason": "overlap already exceeds external-group quota",
                        "support": support,
                        "vertex": vertex,
                        "group": group,
                        "t": t,
                        "o": o,
                    }

            # z_G is the number of neighbours of this vertex in exceptional
            # disjoint fibre G.  A support-level solution is enough here;
            # actual endpoint/sign compatibility would only prune further.
            feasible_rows = []
            for values in itertools.product(range(5), repeat=r):
                if sum(values) != required_degree:
                    continue
                if all(
                    sum(value for value, other in zip(values, disjoint_indices) if group in supports[other])
                    == wanted[group]
                    for group in external_groups
                ):
                    feasible_rows.append(values)
            if not feasible_rows:
                return False, {
                    "reason": "external-group incidence equations infeasible",
                    "support": support,
                    "vertex": vertex,
                    "r": r,
                    "required_degree": required_degree,
                    "wanted_by_group": wanted,
                    "disjoint_exceptional_supports": [supports[other] for other in disjoint_indices],
                }
            details.append((support, vertex, len(feasible_rows)))
    return True, {"row_witness_counts": details}


def edge_mask(vertices, edges):
    positions = {pair: bit for bit, pair in enumerate(itertools.combinations(vertices, 2))}
    mask = 0
    for edge in edges:
        mask |= 1 << positions[tuple(sorted(edge))]
    return mask


def local_actions(supports, vertices):
    """Distinct actions of the support stabilizer and independent symbol flips."""
    used = sorted(set().union(*map(set, supports)))
    index = {vertex: position for position, vertex in enumerate(vertices)}
    actions = set()
    for permutation in stabilizer(supports):
        for flip_values in itertools.product((0, 1), repeat=len(used)):
            flips = dict(zip(used, flip_values))
            image = []
            for vertex in vertices:
                mapped = tuple(
                    sorted(
                        2 * permutation[symbol // 2]
                        + ((symbol % 2) ^ flips.get(symbol // 2, 0))
                        for symbol in vertex
                    )
                )
                image.append(index[mapped])
            actions.add(tuple(image))
    return tuple(sorted(actions))


def transform_mask(mask, action, pair_positions):
    transformed = 0
    while mask:
        low = mask & -mask
        bit = low.bit_length() - 1
        u, v = pair_positions[bit]
        image = tuple(sorted((action[u], action[v])))
        transformed |= 1 << pair_positions.index(image)
        mask ^= low
    return transformed


def canonical_masks(supports, graphs):
    vertices = tuple(
        sorted(
            vertex_label(support, bits)
            for support in supports
            for bits in itertools.product((0, 1), repeat=2)
        )
    )
    pair_positions = tuple(itertools.combinations(range(len(vertices)), 2))
    pair_index = {pair: bit for bit, pair in enumerate(pair_positions)}
    actions = local_actions(supports, vertices)

    # Precompute the induced permutation on the 190 possible edge positions.
    edge_actions = []
    for action in actions:
        edge_actions.append(
            tuple(pair_index[tuple(sorted((action[u], action[v])))] for u, v in pair_positions)
        )

    def transform_fast(mask, edge_action):
        answer = 0
        while mask:
            low = mask & -mask
            bit = low.bit_length() - 1
            answer |= 1 << edge_action[bit]
            mask ^= low
        return answer

    canonical = set()
    for edges in graphs:
        mask = edge_mask(vertices, edges)
        canonical.add(min(transform_fast(mask, action) for action in edge_actions))
    return len(canonical), len(actions)


def enumerate_overlap_local(supports):
    orientations_total = 0
    orientations_with_completion = 0
    completions_total = 0
    pair_upper_graphs = []
    support_feasible_graphs = []
    first_support_obstruction = None
    vertices = tuple(
        sorted(
            vertex_label(support, bits)
            for support in supports
            for bits in itertools.product((0, 1), repeat=2)
        )
    )
    for missing_indices in itertools.product(range(4), repeat=5):
        orientations_total += 1
        oriented = tuple(
            orientation_data(support, missing)
            for support, missing in zip(supports, missing_indices)
        )
        internal = frozenset(edge for data in oriented for edge in data["internal"])
        completed_here = False
        for overlap in overlap_completions(supports, oriented):
            completed_here = True
            completions_total += 1
            graph = internal | overlap
            if induced_pair_upper(vertices, graph):
                pair_upper_graphs.append(graph)
                feasible, detail = exceptional_disjoint_support_feasible(supports, oriented, overlap)
                if feasible:
                    support_feasible_graphs.append(graph)
                elif first_support_obstruction is None:
                    first_support_obstruction = detail
        orientations_with_completion += int(completed_here)

    pair_orbits, action_order = canonical_masks(supports, pair_upper_graphs)
    feasible_orbits, action_order_second = canonical_masks(supports, support_feasible_graphs)
    assert action_order == action_order_second
    return {
        "orientations_total": orientations_total,
        "orientations_with_overlap_completion": orientations_with_completion,
        "overlap_completions": completions_total,
        "after_induced_pair_upper": len(pair_upper_graphs),
        "after_induced_pair_upper_orbits": pair_orbits,
        "after_forced_C4_support_BP": len(support_feasible_graphs),
        "after_forced_C4_support_BP_orbits": feasible_orbits,
        "distinct_local_symmetry_actions": action_order,
        "first_forced_C4_support_BP_obstruction": first_support_obstruction,
    }


def main():
    source = json.loads(INPUT.read_text(encoding="utf-8"))
    survivors = [row for row in source["rows"] if row["passes_compression_square_and_BP"]]
    assert len(survivors) == 12
    rows = []
    labelled_after_no_leaf = 0
    for row in survivors:
        supports = tuple(support_key(item["support"]) for item in row["exceptional_supports"])
        degrees = group_degrees(supports)
        line = line_degrees(supports)
        stab = stabilizer(supports)
        assert len(stab) == row["stabilizer_order"]
        has_leaf = 1 in degrees
        no_disjoint_support = any(value == 4 for value in line)
        stage = "FAIL_OWN_GROUP_OVERLAP" if has_leaf else "ENUMERATE"
        record = {
            "compression_orbit_id": row["orbit_index"],
            "supports": supports,
            "orbit_size": row["orbit_size"],
            "stabilizer_order_checked": len(stab),
            "group_degree_sequence": sorted(degrees, reverse=True),
            "line_degree_sequence": sorted(line, reverse=True),
            "stage": stage,
            "independent_forced_C4_disjoint_degree_obstruction": no_disjoint_support,
        }
        if not has_leaf:
            labelled_after_no_leaf += row["orbit_size"]
        if stage == "ENUMERATE":
            record["bounded_enumeration"] = enumerate_overlap_local(supports)
        rows.append(record)

    counts = Counter(row["stage"] for row in rows)
    final_labelled = sum(
        row["orbit_size"]
        for row in rows
        if row.get("bounded_enumeration", {}).get("after_forced_C4_support_BP", 0)
    )
    result = {
        "model": "solver-free exceptional-P4 local audit at E0=79",
        "all_five_support_sets_audit": all_five_support_sets_audit(),
        "input_compression_orbits": len(survivors),
        "input_labelled_support_sets": sum(row["orbit_size"] for row in rows),
        "stage_counts_by_support_orbit": dict(counts),
        "after_own_group_overlap_support_orbits": sum(not (1 in group_degrees(tuple(support_key(item["support"]) for item in row["exceptional_supports"]))) for row in survivors),
        "after_own_group_overlap_labelled_support_sets": labelled_after_no_leaf,
        "final_local_support_orbits": sum(
            bool(row.get("bounded_enumeration", {}).get("after_forced_C4_support_BP", 0))
            for row in rows
        ),
        "final_local_labelled_support_sets": final_labelled,
        "rows": rows,
        "conclusion": "No placement of five P4 supports passes the exact endpoint-port conditions" if final_labelled == 0 else "local survivors remain",
        "claim_boundary": (
            "The conclusion that E0=79 has exactly five P4 fibres comes from the separate "
            "compression audit.  Conditional on that shape distribution, the audit here checks "
            "all 20349 support placements and is solver-free."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in (
        "input_compression_orbits",
        "input_labelled_support_sets",
        "stage_counts_by_support_orbit",
        "after_own_group_overlap_support_orbits",
        "after_own_group_overlap_labelled_support_sets",
        "final_local_support_orbits",
        "final_local_labelled_support_sets",
        "conclusion",
    )}, indent=2))


if __name__ == "__main__":
    main()
