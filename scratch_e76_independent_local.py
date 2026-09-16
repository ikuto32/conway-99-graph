"""Independent exact local-edge expansion for the E0=76 port survivors.

Only the previously created independent E76 artifacts and the compression
JSON are used.  No general/root E76 port or local-expansion implementation is
read or imported.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from fractions import Fraction
from functools import lru_cache
import itertools
import json
import math
from pathlib import Path

from scratch_e76_independent_port import (
    VERTICES,
    build_state_domains,
    exact_matching_count,
)


BALANCE = Path("scratch_e76_independent_balance.json")
PORT = Path("scratch_e76_independent_port.json")
COMPRESSION = Path("scratch_general_e76_compression_audit.json")
OUTPUT = Path("scratch_e76_independent_local.json")
ALL_SUPPORTS = tuple(itertools.combinations(range(7), 2))


def vertex_label(support, local_vertex):
    bits = VERTICES[local_vertex]
    return (2 * support[0] + bits[0], 2 * support[1] + bits[1])


def global_state_data(support, state):
    vertices = tuple(vertex_label(support, u) for u in range(4))
    internal = frozenset(
        tuple(sorted((vertices[u], vertices[v])))
        for u, v in state["edges"]
    )
    return {"vertices": vertices, "internal": internal}


def enumerate_group_matchings(supports, deficits, domains, group):
    incident = tuple(
        (index, support.index(group))
        for index, support in enumerate(supports)
        if group in support
    )
    ranges = tuple(range(len(domains[deficits[index]])) for index, _axis in incident)
    table = {}
    for restriction in itertools.product(*ranges):
        ports = []
        for (fibre_index, axis), state_index in zip(incident, restriction):
            state = domains[deficits[fibre_index]][state_index]
            for local_vertex, actual, needed in state["ports_by_axis"][axis]:
                ports.append((
                    fibre_index,
                    local_vertex,
                    actual,
                    needed,
                    vertex_label(supports[fibre_index], local_vertex),
                ))
        compact_ports = tuple(port[:4] for port in ports)
        wanted_count = exact_matching_count(compact_ports)
        size = len(ports)
        adjacency = [0] * size
        graph_edge = {}
        endpoint_multiplicity = Counter()
        for left, right in itertools.combinations(range(size), 2):
            fibre_u, local_u, actual_u, need_u, label_u = ports[left]
            fibre_v, local_v, actual_v, need_v, label_v = ports[right]
            if fibre_u == fibre_v or need_u != actual_v or need_v != actual_u:
                continue
            adjacency[left] |= 1 << right
            adjacency[right] |= 1 << left
            edge = tuple(sorted((label_u, label_v)))
            graph_edge[(left, right)] = edge
            endpoint_multiplicity[
                tuple(sorted(((fibre_u, local_u), (fibre_v, local_v))))
            ] += 1
        assert max(endpoint_multiplicity.values(), default=0) <= 1

        @lru_cache(maxsize=None)
        def visit(mask):
            if mask == 0:
                return (frozenset(),)
            choices = []
            probe = mask
            while probe:
                bit = probe & -probe
                u = bit.bit_length() - 1
                available = adjacency[u] & mask
                choices.append((available.bit_count(), u, available))
                probe ^= bit
            degree, u, available = min(choices)
            if degree == 0:
                return ()
            answers = set()
            base = mask & ~(1 << u)
            while available:
                bit = available & -available
                v = bit.bit_length() - 1
                pair = (u, v) if u < v else (v, u)
                for suffix in visit(base & ~(1 << v)):
                    answers.add(suffix | {graph_edge[pair]})
                available ^= bit
            return tuple(sorted(answers, key=lambda graph: tuple(sorted(graph))))

        matchings = visit((1 << size) - 1)
        assert len(matchings) == wanted_count
        table[restriction] = matchings
    return {"group": group, "incident": incident, "table": table}


def neighbour_sets(vertices, graph):
    answer = {vertex: set() for vertex in vertices}
    for u, v in graph:
        answer[u].add(v)
        answer[v].add(u)
    return answer


def induced_pair_upper(vertices, graph):
    neighbours = neighbour_sets(vertices, graph)
    for u, v in itertools.combinations(vertices, 2):
        if (
            len(neighbours[u] & neighbours[v])
            + int(v in neighbours[u])
            > 2 - len(set(u) & set(v))
        ):
            return False
    return True


def forced_c4_support_bp_feasible(supports, graph):
    """Unsigned BP feasibility after all ordinary C4 contributions."""
    exceptional = frozenset(supports)
    support_of = {
        vertex_label(support, local): support
        for support in supports
        for local in range(4)
    }
    vertices = tuple(support_of)
    neighbours = neighbour_sets(vertices, graph)
    for vertex in vertices:
        own = support_of[vertex]
        # Own-support signed quotas must already be exactly filled locally.
        for group in own:
            for symbol in (2 * group, 2 * group + 1):
                if sum(symbol in other for other in neighbours[vertex]) != 1:
                    return False

        disjoint_low = tuple(
            support for support in supports if set(support).isdisjoint(own)
        )
        disjoint_high = tuple(
            support
            for support in ALL_SUPPORTS
            if support not in exceptional and set(support).isdisjoint(own)
        )
        remaining_low_degree = 12 - len(neighbours[vertex]) - len(disjoint_high)
        if not 0 <= remaining_low_degree <= 4 * len(disjoint_low):
            return False
        wanted_by_group = {}
        for group in range(7):
            if group in own:
                continue
            local_count = sum(group in support_of[other] for other in neighbours[vertex])
            high_count = sum(group in support for support in disjoint_high)
            wanted_by_group[group] = 4 - local_count - high_count
            if wanted_by_group[group] < 0:
                return False
        found = False
        for values in itertools.product(range(5), repeat=len(disjoint_low)):
            if sum(values) != remaining_low_degree:
                continue
            if all(
                sum(
                    value
                    for value, support in zip(values, disjoint_low)
                    if group in support
                ) == wanted
                for group, wanted in wanted_by_group.items()
            ):
                found = True
                break
        if not found:
            return False
    return True


def support_actions(supports, deficits, vertices, pair_to_bit):
    weighted = frozenset(zip(supports, deficits))
    stabilizer = tuple(
        permutation
        for permutation in itertools.permutations(range(7))
        if frozenset(
            (tuple(sorted((permutation[a], permutation[b]))), deficit)
            for (a, b), deficit in zip(supports, deficits)
        ) == weighted
    )
    active = tuple(sorted(set(itertools.chain.from_iterable(supports))))
    flips = []
    for bits in itertools.product((0, 1), repeat=len(active)):
        value = [0] * 7
        for group, bit in zip(active, bits):
            value[group] = bit
        flips.append(tuple(value))
    vertex_index = {vertex: index for index, vertex in enumerate(vertices)}
    bit_maps = []
    for permutation, flip in itertools.product(stabilizer, flips):
        image = []
        for vertex in vertices:
            transformed = tuple(sorted(
                2 * permutation[symbol // 2]
                + ((symbol % 2) ^ flip[symbol // 2])
                for symbol in vertex
            ))
            image.append(vertex_index[transformed])
        mapping = [0] * len(pair_to_bit)
        for (u, v), source_bit in pair_to_bit.items():
            target = tuple(sorted((image[u], image[v])))
            mapping[source_bit] = pair_to_bit[target]
        bit_maps.append(tuple(mapping))
    # Inactive group flips were omitted because they act trivially locally.
    # Permutations among multiple inactive groups can still induce the same
    # local action, so quotient that harmless kernel explicitly.
    distinct_bit_maps = tuple(sorted(set(bit_maps)))
    return stabilizer, flips, distinct_bit_maps


def encode_graph(graph, vertex_index, pair_to_bit):
    mask = 0
    for u, v in graph:
        pair = tuple(sorted((vertex_index[u], vertex_index[v])))
        mask |= 1 << pair_to_bit[pair]
    return mask


def transform_mask(mask, bit_map):
    answer = 0
    probe = mask
    while probe:
        bit = probe & -probe
        source = bit.bit_length() - 1
        answer |= 1 << bit_map[source]
        probe ^= bit
    return answer


def decode_graph(mask, vertices, bit_pairs):
    edges = []
    probe = mask
    while probe:
        bit = probe & -probe
        position = bit.bit_length() - 1
        u, v = bit_pairs[position]
        edges.append((vertices[u], vertices[v]))
        probe ^= bit
    return tuple(sorted(edges))


def orbit_representatives(masks, bit_maps):
    all_masks = frozenset(masks)
    remaining = set(all_masks)
    answer = []
    while remaining:
        seed = min(remaining)
        images = frozenset(transform_mask(seed, mapping) for mapping in bit_maps)
        assert images <= all_masks
        representative = min(images)
        answer.append({
            "mask": representative,
            "orbit_size": len(images),
        })
        remaining.difference_update(images)
    assert sum(row["orbit_size"] for row in answer) == len(all_masks)
    return sorted(answer, key=lambda row: row["mask"])


def audit_row(balance_row, port_row, compression_row, domains):
    supports = tuple(tuple(item["support"]) for item in balance_row["exceptional_supports"])
    deficits = tuple(item["deficit"] for item in balance_row["exceptional_supports"])
    group_data = tuple(
        enumerate_group_matchings(supports, deficits, domains, group)
        for group in range(7)
    )
    global_states = tuple(
        tuple(global_state_data(support, state) for state in domains[deficit])
        for support, deficit in zip(supports, deficits)
    )
    ranges = tuple(range(len(states)) for states in global_states)
    vertices = tuple(sorted(
        vertex_label(support, local)
        for support in supports
        for local in range(4)
    ))
    vertex_index = {vertex: index for index, vertex in enumerate(vertices)}
    bit_pairs = tuple(itertools.combinations(range(len(vertices)), 2))
    pair_to_bit = {pair: index for index, pair in enumerate(bit_pairs)}

    budget = compression_row["joint_off_diagonal_square_budget"]
    real_lower = Fraction(compression_row["disjoint_continuous_minimum"])
    compression_overlap_minimum = compression_row["overlap"]["minimum_square"]
    fibre_of = {
        vertex_label(support, local): index
        for index, support in enumerate(supports)
        for local in range(4)
    }
    stages = Counter()
    block_square_histogram = Counter()
    real_square_histogram = Counter()
    pair_square_histogram = Counter()
    forced_square_histogram = Counter()
    forced_masks = set()

    for assignment in itertools.product(*ranges):
        options = []
        for data in group_data:
            restriction = tuple(assignment[index] for index, _axis in data["incident"])
            matches = data["table"][restriction]
            if not matches:
                break
            options.append(matches)
        else:
            internal = frozenset(
                edge
                for fibre_index, state_index in enumerate(assignment)
                for edge in global_states[fibre_index][state_index]["internal"]
            )
            for selected in itertools.product(*options):
                overlap = frozenset(edge for group_edges in selected for edge in group_edges)
                assert len(overlap) == 16
                stages["exact_overlap_completions"] += 1
                counts = Counter(
                    tuple(sorted((fibre_of[u], fibre_of[v]))) for u, v in overlap
                )
                block_square = sum(value * value for value in counts.values())
                assert block_square >= compression_overlap_minimum
                block_square_histogram[block_square] += 1
                if Fraction(block_square) + real_lower > budget:
                    continue
                stages["after_exact_real_disjoint_bound"] += 1
                real_square_histogram[block_square] += 1
                graph = internal | overlap
                if not induced_pair_upper(vertices, graph):
                    continue
                stages["after_induced_pair_upper"] += 1
                pair_square_histogram[block_square] += 1
                if not forced_c4_support_bp_feasible(supports, graph):
                    continue
                stages["after_ordinary_c4_support_BP"] += 1
                forced_square_histogram[block_square] += 1
                mask = encode_graph(graph, vertex_index, pair_to_bit)
                assert mask.bit_count() == len(graph)
                forced_masks.add(mask)

    assert stages["exact_overlap_completions"] == port_row["exact_matching_completion_sum"]
    assert len(forced_masks) == stages["after_ordinary_c4_support_BP"]
    if forced_masks:
        stabilizer, flips, bit_maps = support_actions(
            supports, deficits, vertices, pair_to_bit
        )
        orbit_rows = orbit_representatives(forced_masks, bit_maps)
    else:
        stabilizer, flips, bit_maps, orbit_rows = (), (), (), []

    labels84 = tuple(
        pair
        for pair in itertools.combinations(range(14), 2)
        if pair[0] // 2 != pair[1] // 2
    )
    outer_index = {label: index for index, label in enumerate(labels84)}
    representatives = []
    for index, orbit in enumerate(orbit_rows):
        graph = decode_graph(orbit["mask"], vertices, bit_pairs)
        representatives.append({
            "representative_index": index,
            "local_orbit_size": orbit["orbit_size"],
            "local_edge_count": len(graph),
            "edges_by_symbol_label": [[list(u), list(v)] for u, v in graph],
            "edges_by_outer_index_zero_based": [
                [outer_index[u], outer_index[v]] for u, v in graph
            ],
        })

    return {
        "partition": list(balance_row["partition"]),
        "deficits_in_support_order": list(deficits),
        "compression_orbit_index": balance_row["orbit_index"],
        "support_orbit_size": balance_row["orbit_size"],
        "exceptional_supports": balance_row["exceptional_supports"],
        "joint_square_budget": budget,
        "exact_real_disjoint_lower": str(real_lower),
        "compression_overlap_minimum": compression_overlap_minimum,
        "stages": dict(stages),
        "actual_block_square_histogram": dict(sorted(block_square_histogram.items())),
        "after_real_square_histogram": dict(sorted(real_square_histogram.items())),
        "after_pair_square_histogram": dict(sorted(pair_square_histogram.items())),
        "after_forced_BP_square_histogram": dict(sorted(forced_square_histogram.items())),
        "distinct_forced_local_graphs": len(forced_masks),
        "weighted_support_stabilizer_order": len(stabilizer) if forced_masks else None,
        "active_sign_flip_count": len(flips) if forced_masks else None,
        "distinct_local_symmetry_actions": len(bit_maps) if forced_masks else None,
        "local_graph_orbits": len(representatives),
        "local_orbit_sizes": [row["local_orbit_size"] for row in representatives],
        "representatives": representatives,
    }


def main():
    domains = build_state_domains()
    balance = json.loads(BALANCE.read_text(encoding="utf-8"))
    port = json.loads(PORT.read_text(encoding="utf-8"))
    compression = json.loads(COMPRESSION.read_text(encoding="utf-8"))
    assert balance["ok"] and port["ok"]
    port_map = {
        (tuple(row["partition"]), row["orbit_index"]): row
        for row in port["rows"]
    }
    compression_map = {
        (tuple(row["partition"]), row["orbit_index"]): row
        for row in compression["rows"]
    }
    rows = []
    for offset, balance_row in enumerate(balance["balanced_survivors"]):
        key = (tuple(balance_row["partition"]), balance_row["orbit_index"])
        row = audit_row(
            balance_row,
            port_map[key],
            compression_map[key],
            domains,
        )
        rows.append(row)
        print(json.dumps({
            "offset": offset,
            "partition": row["partition"],
            "orbit": row["compression_orbit_index"],
            **row["stages"],
            "local_orbits": row["local_graph_orbits"],
        }), flush=True)

    result = {
        "model": "independent exact local-edge expansion for E0=76",
        "inputs": [str(BALANCE), str(PORT), str(COMPRESSION)],
        "coverage": (
            "all 130560 exact labelled overlap-port matchings; actual block-square, "
            "exact Fraction disjoint real bound, induced pair upper bound, and "
            "ordinary-C4 unsigned BP support feasibility"
        ),
        "symmetry": (
            "full weighted-support S7 stabilizer times every active coordinate flip; "
            "orbit closure explicitly checked against the full survivor set"
        ),
        "claim_boundary": (
            "local necessary conditions only; signed BP completion, disjoint blocks, "
            "and full common-neighbour equalities remain"
        ),
        "input_support_orbits": len(rows),
        "exact_overlap_completions": sum(
            row["stages"].get("exact_overlap_completions", 0) for row in rows
        ),
        "after_exact_real_disjoint_bound": sum(
            row["stages"].get("after_exact_real_disjoint_bound", 0) for row in rows
        ),
        "after_induced_pair_upper": sum(
            row["stages"].get("after_induced_pair_upper", 0) for row in rows
        ),
        "after_ordinary_c4_support_BP": sum(
            row["stages"].get("after_ordinary_c4_support_BP", 0) for row in rows
        ),
        "support_orbits_after_forced_BP": sum(
            row["stages"].get("after_ordinary_c4_support_BP", 0) > 0 for row in rows
        ),
        "local_graph_orbits": sum(row["local_graph_orbits"] for row in rows),
        "rows": rows,
        "existing_E76_local_expansion_read_or_imported": False,
        "ok": True,
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": True,
        "exact": result["exact_overlap_completions"],
        "after_real": result["after_exact_real_disjoint_bound"],
        "after_pair": result["after_induced_pair_upper"],
        "after_BP": result["after_ordinary_c4_support_BP"],
        "support_survivors": result["support_orbits_after_forced_BP"],
        "local_orbits": result["local_graph_orbits"],
    }))


if __name__ == "__main__":
    main()
