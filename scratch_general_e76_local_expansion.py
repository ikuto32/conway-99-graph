"""Exact overlap expansion and local necessary checks for E0=76 survivors."""

from __future__ import annotations

import argparse
import itertools
import json
from collections import Counter
from fractions import Fraction
from pathlib import Path

import scratch_general_e79_local_audit as local79
from scratch_general_e78_local_ports_all import (
    fibre_variants,
    forced_c4_support_bp_feasible,
    group_matchings,
)


PORT_INPUT = Path("scratch_general_e76_port_audit.json")
OUTPUT_PATH = Path("scratch_general_e76_local_expansion.json")
COUNT_PATH = Path("scratch_general_e76_local_completion_counts.json")
PARTIAL_PATH = Path("scratch_general_e76_local_expansion_partial.json")
REP_PATH = Path("scratch_general_e76_local_graph_reps.json")


def parse_fraction(value):
    return Fraction(value)


def weighted_local_actions(supports, deficits, vertices):
    """Actions preserving the *weighted* exceptional-support assignment."""
    weight = dict(zip(supports, deficits))
    used = sorted(set().union(*map(set, supports)))
    index = {vertex: position for position, vertex in enumerate(vertices)}
    actions = set()
    for permutation in local79.ALL_GROUP_PERMS:
        image_weight = {
            local79.apply_group_perm(support, permutation): deficit
            for support, deficit in weight.items()
        }
        if image_weight != weight:
            continue
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


def orbit_representatives(supports, deficits, graphs):
    """Partition a closed graph set into exact local-symmetry orbits.

    This applies each group element only once per orbit, rather than once per
    input graph.  The closure assertion is also an independent audit that all
    labelled orientations and overlap matchings really were enumerated.
    """
    vertices = tuple(
        sorted(
            local79.vertex_label(support, bits)
            for support in supports
            for bits in itertools.product((0, 1), repeat=2)
        )
    )
    pair_positions = tuple(itertools.combinations(range(len(vertices)), 2))
    pair_index = {pair: bit for bit, pair in enumerate(pair_positions)}
    vertex_index = {vertex: index for index, vertex in enumerate(vertices)}
    actions = weighted_local_actions(supports, deficits, vertices)
    edge_actions = tuple(
        tuple(
            pair_index[tuple(sorted((action[u], action[v])))]
            for u, v in pair_positions
        )
        for action in actions
    )

    def to_mask(edges):
        mask = 0
        for left, right in edges:
            pair = tuple(sorted((vertex_index[left], vertex_index[right])))
            mask |= 1 << pair_index[pair]
        return mask

    def transform(mask, edge_action):
        answer = 0
        work = mask
        while work:
            low = work & -work
            answer |= 1 << edge_action[low.bit_length() - 1]
            work ^= low
        return answer

    def edge_list(mask):
        answer = []
        work = mask
        while work:
            low = work & -work
            u, v = pair_positions[low.bit_length() - 1]
            answer.append([list(vertices[u]), list(vertices[v])])
            work ^= low
        return answer

    masks = [to_mask(graph) for graph in graphs]
    graph_set = set(masks)
    assert len(graph_set) == len(masks), "duplicate labelled local graphs"
    remaining = set(graph_set)
    representatives = []
    while remaining:
        seed = min(remaining)
        orbit = {transform(seed, action) for action in edge_actions}
        assert orbit <= graph_set, "enumerated graph set is not symmetry-closed"
        assert seed == min(orbit)
        remaining.difference_update(orbit)
        representatives.append(
            {
                "mask_hex": hex(seed),
                "orbit_size": len(orbit),
                "edges": edge_list(seed),
            }
        )
    assert sum(row["orbit_size"] for row in representatives) == len(graph_set)
    return representatives, len(actions), len(graph_set)


def audit_row(source, expand):
    supports = tuple(tuple(item["support"]) for item in source["exceptional_supports"])
    deficits = tuple(item["deficit"] for item in source["exceptional_supports"])
    domains = tuple(
        fibre_variants(support, deficit)
        for support, deficit in zip(supports, deficits)
    )
    shape_count = 0
    completions = 0
    maximum_completion = 0
    completion_histogram = Counter()
    actual_square_histogram = Counter()
    spectral = 0
    pair_upper = 0
    forced_bp = 0
    forced_graphs = []
    for oriented in itertools.product(*domains):
        by_group = tuple(group_matchings(oriented, group) for group in local79.GROUPS)
        count = 1
        for choices in by_group:
            count *= len(choices)
        if not count:
            continue
        shape_count += 1
        completions += count
        maximum_completion = max(maximum_completion, count)
        completion_histogram[count] += 1
        if not expand:
            continue
        internal = frozenset(edge for data in oriented for edge in data["internal"])
        vertices = tuple(vertex for data in oriented for vertex in data["vertices"])
        fibre_of = {
            vertex: index
            for index, data in enumerate(oriented)
            for vertex in data["vertices"]
        }
        for selected in itertools.product(*by_group):
            overlap = frozenset(edge for group_edges in selected for edge in group_edges)
            assert len(overlap) == 16
            block_counts = Counter(
                tuple(sorted((fibre_of[u], fibre_of[v]))) for u, v in overlap
            )
            m2 = sum(value * value for value in block_counts.values())
            actual_square_histogram[m2] += 1
            # Use only the exact real least-norm disjoint lower bound here;
            # no CP-SAT negative result enters the local coverage.
            if m2 + parse_fraction(source["disjoint_continuous_minimum"]) > source["joint_square_budget"]:
                continue
            spectral += 1
            graph = internal | overlap
            if not local79.induced_pair_upper(vertices, graph):
                continue
            pair_upper += 1
            if not forced_c4_support_bp_feasible(supports, oriented, graph):
                continue
            forced_bp += 1
            forced_graphs.append(graph)
    orbit_count = None
    action_count = None
    graph_representatives = []
    distinct_forced_graphs = None
    if expand and forced_graphs:
        graph_representatives, action_count, distinct_forced_graphs = orbit_representatives(
            supports, deficits, forced_graphs
        )
        orbit_count = len(graph_representatives)
    elif expand:
        orbit_count, action_count = 0, None
        distinct_forced_graphs = 0
    return {
        "partition": list(deficits),
        "orbit_index": source["orbit_index"],
        "support_orbit_size": source["support_orbit_size"],
        "supports": [list(support) for support in supports],
        "port_feasible_shape_assignments": shape_count,
        "exact_overlap_completions": completions,
        "maximum_completions_for_one_shape": maximum_completion,
        "completion_count_histogram": {
            str(key): value for key, value in sorted(completion_histogram.items())
        },
        "expanded": expand,
        "actual_overlap_square_histogram": {
            str(key): value for key, value in sorted(actual_square_histogram.items())
        },
        "after_exact_real_spectral_bound": spectral if expand else None,
        "after_induced_pair_upper": pair_upper if expand else None,
        "after_forced_C4_support_BP": forced_bp if expand else None,
        "after_forced_C4_support_BP_orbits": orbit_count,
        "distinct_local_symmetry_actions": action_count,
        "distinct_after_forced_C4_support_BP_graphs": distinct_forced_graphs,
        "local_graph_orbit_size_histogram": {
            str(key): value
            for key, value in sorted(
                Counter(row["orbit_size"] for row in graph_representatives).items()
            )
        },
        "local_graph_representatives": graph_representatives,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--expand", action="store_true")
    parser.add_argument("--max-completions", type=int, default=0)
    args = parser.parse_args()
    source = json.loads(PORT_INPUT.read_text(encoding="utf-8"))
    rows_in = [row for row in source["rows"] if row["locally_port_feasible_assignments"]]
    assert len(rows_in) == 21
    count_rows = [audit_row(row, False) for row in rows_in]
    total_completions = sum(row["exact_overlap_completions"] for row in count_rows)
    if not args.expand:
        result = {
            "model": "E0=76 exact local overlap completion counts",
            "support_orbits": len(count_rows),
            "total_exact_overlap_completions": total_completions,
            "rows": count_rows,
        }
        COUNT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({
            "support_orbits": len(count_rows),
            "total_exact_overlap_completions": total_completions,
            "maximum_per_support": max(row["exact_overlap_completions"] for row in count_rows),
        }), flush=True)
        return
    if args.max_completions and total_completions > args.max_completions:
        raise RuntimeError(
            f"refusing expansion of {total_completions} completions above limit {args.max_completions}"
        )
    rows = []
    for offset, row in enumerate(rows_in):
        record = audit_row(row, True)
        rows.append(record)
        PARTIAL_PATH.write_text(
            json.dumps(
                {
                    "status": "PARTIAL",
                    "completed_offsets": len(rows),
                    "total_offsets": len(rows_in),
                    "rows": rows,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        print(json.dumps({
            "offset": offset,
            "partition": record["partition"],
            "orbit_index": record["orbit_index"],
            "completions": record["exact_overlap_completions"],
            "pair_upper": record["after_induced_pair_upper"],
            "forced_bp": record["after_forced_C4_support_BP"],
            "orbits": record["after_forced_C4_support_BP_orbits"],
        }), flush=True)
    result = {
        "model": "solver-free exact E0=76 overlap/local expansion",
        "input": str(PORT_INPUT),
        "coverage": (
            "all exact overlap completions of all 1207 fibre states on all 21 "
            "port-feasible support orbits"
        ),
        "spectral_filter": "exact-real least-norm lower bound only; no integer-solver exclusion",
        "support_orbits": len(rows),
        "total_exact_overlap_completions": total_completions,
        "final_local_support_orbits": sum(row["after_forced_C4_support_BP"] > 0 for row in rows),
        "final_local_graph_orbits": sum(row["after_forced_C4_support_BP_orbits"] for row in rows),
        "rows": rows,
    }
    OUTPUT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    rep_result = {
        "model": "exact canonical local graph representatives for E0=76",
        "input": str(OUTPUT_PATH),
        "vertex_label": (
            "a low vertex is the sorted pair [2*g_a+bit_a, 2*g_b+bit_b] "
            "on its two root-neighbour groups"
        ),
        "coverage": (
            "one explicit edge-list representative for every orbit surviving "
            "the exact-real spectral, induced-pair-upper, and forced-C4 BP filters"
        ),
        "checks": (
            "for every support row the labelled graph set is invariant under "
            "the full support stabilizer times independent used-group bit flips, "
            "has no duplicates, and orbit sizes sum to the raw survivor count"
        ),
        "support_rows": [
            {
                "partition": row["partition"],
                "orbit_index": row["orbit_index"],
                "supports": row["supports"],
                "raw_survivors": row["after_forced_C4_support_BP"],
                "symmetry_actions": row["distinct_local_symmetry_actions"],
                "orbit_count": row["after_forced_C4_support_BP_orbits"],
                "orbit_size_histogram": row["local_graph_orbit_size_histogram"],
                "representatives": row["local_graph_representatives"],
            }
            for row in rows
            if row["after_forced_C4_support_BP"]
        ],
    }
    assert sum(row["orbit_count"] for row in rep_result["support_rows"]) == result[
        "final_local_graph_orbits"
    ]
    REP_PATH.write_text(json.dumps(rep_result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "support_orbits": result["support_orbits"],
        "total_exact_overlap_completions": total_completions,
        "final_local_support_orbits": result["final_local_support_orbits"],
        "final_local_graph_orbits": result["final_local_graph_orbits"],
    }), flush=True)


if __name__ == "__main__":
    main()
