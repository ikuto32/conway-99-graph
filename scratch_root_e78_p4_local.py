"""Extend the E0=78 all-P4 port survivors through exact local checks."""

from __future__ import annotations

import itertools
import json
from pathlib import Path

from scratch_general_e79_local_audit import (
    GROUPS,
    canonical_masks,
    exceptional_disjoint_support_feasible,
    edge_mask,
    induced_pair_upper,
    local_actions,
    orientation_data,
    perfect_matchings,
    sign_at,
    support_key,
    vertex_label,
)


def canonical_representatives(supports, graphs):
    vertices = tuple(sorted(
        vertex_label(support, bits)
        for support in supports
        for bits in itertools.product((0, 1), repeat=2)
    ))
    pair_positions = tuple(itertools.combinations(range(len(vertices)), 2))
    pair_index = {pair: bit for bit, pair in enumerate(pair_positions)}
    actions = local_actions(supports, vertices)
    edge_actions = [
        tuple(
            pair_index[tuple(sorted((action[u], action[v])))]
            for u, v in pair_positions
        )
        for action in actions
    ]

    def transform(mask, action):
        answer = 0
        while mask:
            low = mask & -mask
            bit = low.bit_length() - 1
            answer |= 1 << action[bit]
            mask ^= low
        return answer

    representatives = set()
    for graph in graphs:
        mask = edge_mask(vertices, graph)
        representatives.add(min(transform(mask, action) for action in edge_actions))
    decoded = []
    for mask in sorted(representatives):
        edges = []
        for bit, (u, v) in enumerate(pair_positions):
            if (mask >> bit) & 1:
                edges.append([list(vertices[u]), list(vertices[v])])
        decoded.append(edges)
    return decoded


def overlap_completions(supports, oriented):
    by_group = []
    for group in GROUPS:
        incident = [i for i, support in enumerate(supports) if group in support]
        if not incident:
            continue
        stubs = []
        for i in incident:
            for vertex in oriented[i]["endpoints"]:
                stubs.append((vertex, i))
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
        assert len(combined) == 2 * len(supports)
        yield combined


def main():
    source = json.loads(Path("scratch_root_e78_p4_ports.json").read_text(encoding="utf-8"))
    candidates = [r for r in source["rows"] if r["locally_BP_feasible_orientations"]]
    assert len(candidates) == 3
    output = []
    for row in candidates:
        supports = tuple(tuple(edge) for edge in row["supports"])
        vertices = tuple(sorted(
            vertex_label(support, bits)
            for support in supports
            for bits in itertools.product((0, 1), repeat=2)
        ))
        orientations_with_completion = 0
        completions = 0
        pair_upper = 0
        support_feasible = 0
        support_feasible_graphs = []
        first_feasible = None
        first_obstruction = None
        for missing in itertools.product(range(4), repeat=6):
            oriented = tuple(
                orientation_data(support, code)
                for support, code in zip(supports, missing)
            )
            internal = frozenset(
                edge for data in oriented for edge in data["internal"]
            )
            completed_here = False
            for overlap in overlap_completions(supports, oriented):
                completed_here = True
                completions += 1
                graph = internal | overlap
                if not induced_pair_upper(vertices, graph):
                    continue
                pair_upper += 1
                feasible, detail = exceptional_disjoint_support_feasible(
                    supports, oriented, overlap
                )
                if not feasible:
                    if first_obstruction is None:
                        first_obstruction = detail
                    continue
                support_feasible += 1
                support_feasible_graphs.append(graph)
                if first_feasible is None:
                    first_feasible = {
                        "orientation": list(missing),
                        "local_edges": [list(edge) for edge in sorted(graph)],
                        "support_level_detail": detail,
                    }
            orientations_with_completion += int(completed_here)
        feasible_orbits, action_order = canonical_masks(
            supports, support_feasible_graphs
        )
        representatives = canonical_representatives(
            supports, support_feasible_graphs
        )
        assert len(representatives) == feasible_orbits
        out = {
            "orbit_index": row["orbit_index"],
            "supports": row["supports"],
            "orientations_checked": 4**6,
            "orientations_with_overlap_completion": orientations_with_completion,
            "overlap_completions": completions,
            "after_induced_pair_upper": pair_upper,
            "after_forced_C4_support_BP": support_feasible,
            "after_forced_C4_support_BP_orbits": feasible_orbits,
            "distinct_local_symmetry_actions": action_order,
            "canonical_local_graph_representatives": representatives,
            "first_support_obstruction": first_obstruction,
            "first_feasible": first_feasible,
        }
        output.append(out)
        print(json.dumps(out | {"first_feasible": bool(first_feasible)}), flush=True)
    result = {
        "model": "E0=78 exact local audit of the three all-P4 port survivors",
        "input": "scratch_root_e78_p4_ports.json",
        "claim_boundary": (
            "All enumerated constraints are necessary. A zero count excludes "
            "the support orbit; a positive count remains only a local seed."
        ),
        "rows": output,
    }
    Path("scratch_root_e78_p4_local.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
