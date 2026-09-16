"""Small exact audit for the triangle-flag union identities.

This checks the finite entrywise polynomials, the canonical seven-vertex
diagonal motif mask, and all displayed coefficient reductions.  It does not
assume or construct an SRG.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path


OUTPUT = Path("scratch_theory_root_flag_union_audit.json")


def mask(edges, permutation):
    pairs = tuple(itertools.combinations(range(7), 2))
    image = {tuple(sorted((permutation[left], permutation[right])))
             for left, right in edges}
    return sum(1 << index for index, edge in enumerate(pairs) if edge in image)


def main():
    # r=0; root triangles 0-1-2 and 0-3-4; diagonal endpoints 5,6.
    h_delta_edges = {
        (0, 1), (0, 2), (1, 2),
        (0, 3), (0, 4), (3, 4),
        (5, 6), (5, 1), (5, 3), (6, 2), (6, 4),
    }
    masks = tuple(mask(h_delta_edges, permutation)
                  for permutation in itertools.permutations(range(7)))
    degrees = [0] * 7
    for left, right in h_delta_edges:
        degrees[left] += 1
        degrees[right] += 1
    assert sorted(degrees, reverse=True) == [4, 3, 3, 3, 3, 3, 3]
    assert min(masks) == 120568

    entry_table = []
    for value in range(3):
        support = (3 * value - value * value) // 2
        diagonal = value * (value - 1) // 2
        assert support == int(value > 0)
        assert diagonal == int(value == 2)
        entry_table.append({"Y": value, "support_Z": support,
                            "diagonal_indicator": diagonal})

    projector_table = []
    for cross_edges, projector_entry in enumerate((1, 0, -1, -2)):
        value = (projector_entry ** 3 + projector_entry ** 2
                 - 2 * projector_entry) // 2
        assert value == int(cross_edges == 2)
        projector_table.append({"cross_edges": cross_edges,
                                "M_entry": projector_entry,
                                "two_edge_indicator": value})
    assert (4 ** 3 + 4 ** 2 - 2 * 4) // 2 == 36

    # Coefficient checks with formal integer samples.
    samples = []
    for n3, diagonal_total in ((0, 0), (3, 0), (3, 2),
                               (705, 0), (705, 2), (705, 17)):
            y_norm = 2 * n3 + 2 * diagonal_total
            e_sum_1 = 8316 - 2 * n3 + diagonal_total
            e_sum_2 = 8316 - 3 * n3 + y_norm // 2
            assert e_sum_1 == e_sum_2
            support_total = 2 * n3 - diagonal_total
            assert e_sum_1 == 8316 - support_total
            samples.append({"n3": n3, "D_total": diagonal_total,
                            "Y_norm_squared": y_norm,
                            "support_total": support_total,
                            "E0_sum": e_sum_1})

    result = {
        "status": "TRIANGLE_FLAG_UNION_IDENTITY_FINITE_AUDIT_PASS",
        "sizes": {"triangles": 231, "flags": 693,
                  "vertices": 99, "flags_per_vertex": 7},
        "H_delta": {"edge_count": len(h_delta_edges),
                    "degree_sequence": sorted(degrees, reverse=True),
                    "canonical_mask": min(masks),
                    "labelled_orbit_size": len(set(masks))},
        "entrywise_Y_table": entry_table,
        "projector_r2_indicator_table": projector_table,
        "formal_coefficient_samples": samples,
        "checks": {
            "canonical_mask_120568": True,
            "Z_equals_indicator_Y_positive_for_Y_0_1_2": True,
            "binomial_Y2_equals_diagonal_indicator": True,
            "Schur_cubic_selects_exactly_r2": True,
            "E0_global_coefficient_reductions": True,
        },
        "scope": "finite algebra audit; graph-theoretic bijections are proved in the note",
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
