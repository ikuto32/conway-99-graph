"""Six previously variable flags have k-2 occurrences at every root triangle.

The algebraic proof is recorded in the companion note.  This file checks
all absent-edge perturbations of the six induced templates and calibrates
the occurrence bijection on the 3-by-3 rook graph.  No H8 census is used.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path

import scratch_theory_order9_cross_x_closure as encoding


FLAGS = (24699, 24939, 25147, 25507, 27179, 27299)


def main():
    templates = []
    for a, b in itertools.permutations(range(3), 2):
        chosen = {(0, 1), (0, 2), (1, 2), (3, 4), (4, 5)}
        chosen.update(tuple(sorted(edge)) for edge in ((a, 3), (a, 4), (b, 5)))
        raw = sum(1 << encoding.positions(6)[edge] for edge in chosen)
        canonical = encoding.canonical(raw, 6, (0, 1, 2))
        assert canonical in FLAGS and encoding.pair_upper(raw, 6)
        missing = [edge for edge in encoding.edges(6) if edge not in chosen]
        surviving_supergraphs = []
        for bits in range(1 << len(missing)):
            graph = raw | sum(1 << encoding.positions(6)[edge]
                              for i, edge in enumerate(missing) if bits >> i & 1)
            if encoding.pair_upper(graph, 6):
                surviving_supergraphs.append(bits)
        assert surviving_supergraphs == [0]
        templates.append({"ordered_pair": [a, b], "raw_mask": raw,
                          "rooted_mask": canonical,
                          "supergraphs_tested": 1 << len(missing),
                          "only_pair_upper_supergraph_is_original": True})
    assert sorted(row["rooted_mask"] for row in templates) == list(FLAGS)

    points = tuple(itertools.product(range(3), repeat=2))
    graph = [sum(1 << j for j, q in enumerate(points) if i != j
                 and (p[0] == q[0] or p[1] == q[1]))
             for i, p in enumerate(points)]
    assert {row.bit_count() for row in graph} == {4}
    assert all((graph[i] & graph[j]).bit_count() == (1 if graph[i] >> j & 1 else 2)
               for i, j in itertools.combinations(range(9), 2))
    root_rows = []
    for roots in itertools.permutations(range(9), 3):
        if not all(graph[a] >> b & 1 for a, b in itertools.combinations(roots, 2)):
            continue
        counts = [0] * 6
        remaining = [v for v in range(9) if v not in roots]
        for free in itertools.combinations(remaining, 3):
            chosen = roots + free
            mask = sum(1 << bit for bit, (i, j) in enumerate(encoding.edges(6))
                       if graph[chosen[i]] >> chosen[j] & 1)
            key = encoding.canonical(mask, 6, (0, 1, 2))
            if key in FLAGS:
                counts[FLAGS.index(key)] += 1
        assert counts == [2] * 6
        root_rows.append(counts)
    assert len(root_rows) == 36
    gram = [[sum(row[i] * row[j] for row in root_rows) for j in range(6)]
            for i in range(6)]
    assert gram == [[144] * 6 for _ in range(6)]

    result = {
        "status": "SIX_FLAG_UNIFORMITY_FINITE_CHECKS_PASS",
        "theorem": "Each of the six flags occurs k-2 times per ordered triangle in any srg(n,k,1,2).",
        "templates": templates,
        "target": {"ordered_triangles": 1386, "count_each_flag": 12,
                   "complete_Gram_entry": 199584,
                   "requires_T_zero": False, "E0_lower_bound": None},
        "rook9_calibration": {"ordered_triangles": 36, "count_each_flag": 2,
                              "Gram": gram},
        "frozen_order8_classes_regenerated": False,
        "submission_txt_written": False,
    }
    Path("scratch_theory_six_flag_uniformity.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items()
                      if key not in {"templates", "rook9_calibration"}}, indent=2))


if __name__ == "__main__":
    main()
