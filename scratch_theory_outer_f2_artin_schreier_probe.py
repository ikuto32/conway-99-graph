"""Exact GF(2) probe for the rooted outer equation B^2+B=Q_line.

This is a scoped algebraic diagnostic.  It constructs only the fixed
84-vertex line-graph scaffold K_14-7K_2 and does not enumerate any E0 layer.
"""

from __future__ import annotations

import json
from pathlib import Path


def gf2_rank(rows: list[int]) -> int:
    rows = rows[:]
    rank = 0
    while rows:
        pivot = max(rows)
        if pivot == 0:
            break
        bit = pivot.bit_length() - 1
        rows.remove(pivot)
        for i, row in enumerate(rows):
            if (row >> bit) & 1:
                rows[i] = row ^ pivot
        rank += 1
    return rank


def matmul(a: list[int], b: list[int], n: int) -> list[int]:
    # Rows are n-bit integers.  XOR rows of b selected by a's row.
    out: list[int] = []
    for row in a:
        value = 0
        x = row
        while x:
            low = x & -x
            value ^= b[low.bit_length() - 1]
            x ^= low
        out.append(value & ((1 << n) - 1))
    return out


def main() -> None:
    labels = [(i, j) for i in range(14) for j in range(i + 1, 14) if j != (i ^ 1)]
    assert len(labels) == 84
    q: list[int] = []
    for i, e in enumerate(labels):
        row = 0
        for j, f in enumerate(labels):
            if i != j and set(e) & set(f):
                row |= 1 << j
        q.append(row)

    powers = [q]
    ranks = [gf2_rank(q)]
    while ranks[-1] != 0:
        powers.append(matmul(powers[-1], q, 84))
        ranks.append(gf2_rank(powers[-1]))
    nullities = [84 - r for r in ranks]

    # For nilpotent Q, the number of Jordan blocks of size exactly k follows
    # from successive nullities.  Pad once Q^k=0.
    ns = [0] + nullities
    increments = [ns[i] - ns[i - 1] for i in range(1, len(ns))]
    increments.append(0)
    exact_blocks = {
        str(k): increments[k - 1] - increments[k]
        for k in range(1, len(increments))
        if increments[k - 1] - increments[k]
    }

    block_sizes: list[int] = []
    for key, count in exact_blocks.items():
        block_sizes.extend([int(key)] * count)
    reachable = {0}
    for size in block_sizes:
        reachable |= {x + size for x in tuple(reachable)}

    q2 = matmul(q, q, 84)
    b0 = [x ^ y for x, y in zip(q, q2)]
    b0_square_plus_b0 = [x ^ y for x, y in zip(matmul(b0, b0, 84), b0)]
    symmetric_b0 = all(((b0[i] >> j) & 1) == ((b0[j] >> i) & 1)
                       for i in range(84) for j in range(84))

    result = {
        "status": "OUTER_F2_ARTIN_SCHREIER_PROBE_COMPLETE",
        "vertices": 84,
        "q_row_weights": sorted({row.bit_count() for row in q}),
        "q_power_ranks": ranks,
        "q_power_nullities": ns[1:],
        "q_nilpotency_index": len(ranks),
        "q_jordan_blocks": exact_blocks,
        "known_B_generalized_one_dimension": 40,
        "block_assignment_dimension_40_possible": 40 in reachable,
        "reachable_assignment_dimensions": sorted(reachable),
        "explicit_artin_schreier_control": {
            "formula": "B0=Q+Q^2 over GF(2)",
            "B0_squared_plus_B0_equals_Q": b0_square_plus_b0 == q,
            "symmetric": symmetric_b0,
            "zero_diagonal": all(((b0[i] >> i) & 1) == 0 for i in range(84)),
            "row_weights": sorted({row.bit_count() for row in b0}),
            "qualification": "B0 is not asserted to have the target integer spectrum or to lift to a graph.",
        },
        "claim_boundary": (
            "A feasible block assignment is only a Jordan-form compatibility "
            "control; it is not a binary symmetric adjacency realization."
        ),
    }
    Path("scratch_theory_outer_f2_artin_schreier_probe.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
