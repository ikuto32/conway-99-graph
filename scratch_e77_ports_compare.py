"""Cross-label comparison of the two E0=77 orbit-22 local quotients."""

from __future__ import annotations

import json
from pathlib import Path

import scratch_e77_ports_audit as audit


def local_id(decoded):
    i, si, j, sj = decoded
    return audit.vertex_id(
        audit.SUPPORT_INDEX[(i, j)], audit.BIT_INDEX[(si, sj)]
    )


def decoded_edges(edges):
    return tuple(sorted(
        tuple(sorted((local_id(u), local_id(v)))) for u, v in edges
    ))


def main():
    ours = json.loads(Path("scratch_e77_ports_audit.json").read_text(encoding="utf-8"))
    row = next(item for item in ours["local_survivors"] if item["orbit_index"] == 22)
    state = [0] * 21
    for u, v, deficit in row["support"]["weighted_edges"]:
        state[audit.SUPPORT_INDEX[(u, v)]] = deficit
    state = tuple(state)
    exceptional_vertices = tuple(
        audit.vertex_id(i, local)
        for i, deficit in enumerate(state) if deficit
        for local in range(4)
    )
    actions = {}
    for permutation in audit.support_stabilizer(state):
        for flip_mask in range(128):
            mapping = audit.outer_vertex_map(permutation, flip_mask)
            actions.setdefault(
                tuple(mapping[v] for v in exceptional_vertices), mapping
            )
    actions = tuple(actions.values())

    def canonical(edges):
        return min(audit.transform_edges(edges, action) for action in actions)

    our_orbits = {
        canonical(decoded_edges(item["representative_edges"])): item["size"]
        for item in row["after_forced_ordinary_C4_support_BP_quotient"]["orbits"]
    }

    reference = json.loads(
        Path("scratch_general_e77_local_reps.json").read_text(encoding="utf-8")
    )["record"]
    symbol_by_outer = {
        item["outer_index_zero_based"]: tuple(item["symbol_label"])
        for item in reference["local_vertex_order"]
    }

    def reference_vertex(outer):
        left, right = symbol_by_outer[outer]
        i, si = divmod(left, 2)
        j, sj = divmod(right, 2)
        return audit.vertex_id(
            audit.SUPPORT_INDEX[(i, j)], audit.BIT_INDEX[(si, sj)]
        )

    reference_orbits = {}
    for item in reference["representatives"]:
        edges = tuple(sorted(
            tuple(sorted((reference_vertex(u), reference_vertex(v))))
            for u, v in item["present_edges_outer_indices_zero_based"]
        ))
        reference_orbits[canonical(edges)] = item["orbit_size"]

    result = {
        "model": "cross-label exact comparison of E0=77 orbit-22 local quotients",
        "effective_action_order": len(actions),
        "ours_graph_count": sum(our_orbits.values()),
        "reference_graph_count": reference["local_graph_count"],
        "ours_orbit_sizes": sorted(our_orbits.values()),
        "reference_orbit_sizes": sorted(reference_orbits.values()),
        "canonical_orbit_dictionaries_equal": our_orbits == reference_orbits,
        "ok": (
            our_orbits == reference_orbits
            and sum(our_orbits.values()) == reference["local_graph_count"] == 512
        ),
    }
    Path("scratch_e77_ports_compare.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
