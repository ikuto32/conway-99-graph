"""Explore compression-eigenvector residuals on the surviving E74 local reps.

Diagnostic only: it records exact local values and does not claim an
exclusion.
"""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path


SOURCE = Path("scratch_general_e74_q5_local_graph_reps.json")
OUTPUT = Path("scratch_theory_e74_residual_probe.json")


def main():
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    row = source["support_rows"][0]
    supports = [tuple(item["support"]) for item in row["exceptional_supports"]]
    # Eigenvectors of the unique Z matrix, in this support order.
    vectors = {
        "z14_R_minus_half": (1, -1, 0, -1, 1, 0),
        "z6_R_three_halves": (1, 1, -2, -1, -1, 2),
    }
    weight_maps = {
        name: {support: value for support, value in zip(supports, values)}
        for name, values in vectors.items()
    }
    summaries = {name: Counter() for name in vectors}
    examples = {}
    for rep_index, rep in enumerate(row["representatives"]):
        vertices = sorted({tuple(v) for edge in rep["edges"] for v in edge})
        adjacency = {vertex: set() for vertex in vertices}
        for raw_u, raw_v in rep["edges"]:
            u, v = tuple(raw_u), tuple(raw_v)
            adjacency[u].add(v)
            adjacency[v].add(u)
        for name, weights in weight_maps.items():
            c = {
                vertex: weights[tuple(sorted(symbol // 2 for symbol in vertex))]
                for vertex in vertices
            }
            # For theta=-1/2 use 2(B-theta I)c=2Bc+c.
            # For theta=3/2 use 2(B-theta I)c=2Bc-3c.
            shift = 1 if name == "z14_R_minus_half" else -3
            q = {
                vertex: 2 * sum(c[neighbour] for neighbour in adjacency[vertex]) + shift * c[vertex]
                for vertex in vertices
            }
            by_support = tuple(
                tuple(sorted(q[v] for v in vertices
                             if tuple(sorted(symbol // 2 for symbol in v)) == support))
                for support in supports
            )
            summaries[name][by_support] += 1
            examples.setdefault((name, by_support), rep_index)
    result = {
        "status": "DIAGNOSTIC_ONLY",
        "source": str(SOURCE),
        "support_order": [list(value) for value in supports],
        "vectors": {name: list(value) for name, value in vectors.items()},
        "local_residual_pattern_counts": {
            name: [
                {"pattern": [list(block) for block in pattern], "representative_count": count,
                 "first_representative_index": examples[name, pattern]}
                for pattern, count in sorted(counter.items())
            ]
            for name, counter in summaries.items()
        },
        "claim_boundary": "High-fibre residual coordinates are not fixed here; no exclusion is asserted.",
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({name: len(counter) for name, counter in summaries.items()}))


if __name__ == "__main__":
    main()
