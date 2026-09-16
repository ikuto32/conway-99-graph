"""Exact overlap-edge expansion of the three E0=77 port survivors."""

from __future__ import annotations

from collections import Counter
import itertools
import json
from pathlib import Path

import scratch_general_e79_local_audit as local79
from scratch_general_e78_local_ports_all import (
    fibre_variants,
    forced_c4_support_bp_feasible,
    group_matchings,
)
from scratch_root_e78_p4_local import canonical_representatives


def main():
    port = json.loads(Path("scratch_root_e77_port_screen.json").read_text(encoding="utf-8"))
    integer = json.loads(Path("scratch_root_e77_integer.json").read_text(encoding="utf-8"))
    integer_map = {
        (tuple(row["partition"]), row["orbit_index"]): row
        for row in integer["rows"] if row["passes_integer_screen"]
    }
    sources = [r for r in port["rows"] if r["locally_port_feasible_assignments"]]
    assert len(sources) == 3
    output = []
    for source in sources:
        key = (tuple(source["partition"]), source["orbit_index"])
        compression = integer_map[key]
        supports = tuple(tuple(item["support"]) for item in source["exceptional_supports"])
        deficits = tuple(item["deficit"] for item in source["exceptional_supports"])
        domains = tuple(
            fibre_variants(support, deficit)
            for support, deficit in zip(supports, deficits)
        )
        shape_count = completions = spectral = pair_upper = forced_bp = 0
        completion_hist = Counter()
        square_hist = Counter()
        forced_graphs = []
        first_forced = None
        for oriented in itertools.product(*domains):
            by_group = tuple(
                group_matchings(oriented, group) for group in local79.GROUPS
            )
            count = 1
            for choices in by_group:
                count *= len(choices)
            if not count:
                continue
            shape_count += 1
            completions += count
            completion_hist[count] += 1
            internal = frozenset(
                edge for data in oriented for edge in data["internal"]
            )
            vertices = tuple(vertex for data in oriented for vertex in data["vertices"])
            fibre_of = {
                vertex: index
                for index, data in enumerate(oriented)
                for vertex in data["vertices"]
            }
            for selected in itertools.product(*by_group):
                overlap = frozenset(
                    edge for group_edges in selected for edge in group_edges
                )
                assert len(overlap) == 14
                block_counts = Counter(
                    tuple(sorted((fibre_of[u], fibre_of[v])))
                    for u, v in overlap
                )
                m2 = sum(value * value for value in block_counts.values())
                square_hist[m2] += 1
                if (
                    m2 + compression["disjoint_integer"]["minimum_square"]
                    > compression["joint_square_budget"]
                ):
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
                if first_forced is None:
                    first_forced = [[list(u), list(v)] for u, v in sorted(graph)]
        if forced_graphs:
            orbit_count, action_count = local79.canonical_masks(
                supports, forced_graphs
            )
            representatives = canonical_representatives(supports, forced_graphs)
            assert len(representatives) == orbit_count
        else:
            orbit_count, action_count = 0, None
            representatives = []
        row = {
            "partition": list(deficits),
            "orbit_index": source["orbit_index"],
            "supports": [list(s) for s in supports],
            "shape_assignments_with_ports": shape_count,
            "exact_overlap_completions": completions,
            "completion_count_histogram": dict(sorted(completion_hist.items())),
            "actual_overlap_square_histogram": dict(sorted(square_hist.items())),
            "after_actual_spectral_bound": spectral,
            "after_induced_pair_upper": pair_upper,
            "after_forced_C4_support_BP": forced_bp,
            "after_forced_C4_support_BP_orbits": orbit_count,
            "distinct_local_symmetry_actions": action_count,
            "canonical_local_graph_representatives": representatives,
            "first_forced_graph": first_forced,
        }
        output.append(row)
        print(json.dumps(row | {"first_forced_graph": bool(first_forced)}), flush=True)
    result = {
        "model": "independent exact local overlap expansion of E0=77 port survivors",
        "inputs": ["scratch_root_e77_port_screen.json", "scratch_root_e77_integer.json"],
        "claim_boundary": (
            "Exact local and support-count necessities only; positive graphs "
            "are not full 84-vertex lifts."
        ),
        "rows": output,
    }
    Path("scratch_root_e77_local.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
