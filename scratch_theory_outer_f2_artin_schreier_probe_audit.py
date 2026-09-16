"""Independent set-row replay of the outer GF(2) diagnostic."""

from __future__ import annotations

import json
from pathlib import Path


def product(a: list[set[int]], b: list[set[int]]) -> list[set[int]]:
    out = []
    for row in a:
        acc: set[int] = set()
        for k in row:
            acc.symmetric_difference_update(b[k])
        out.append(acc)
    return out


def rank(rows: list[set[int]]) -> int:
    pivots: dict[int, set[int]] = {}
    for source in rows:
        row = set(source)
        while row:
            p = max(row)
            if p not in pivots:
                pivots[p] = row
                break
            row.symmetric_difference_update(pivots[p])
    return len(pivots)


def main() -> None:
    labels = [(a, b) for a in range(14) for b in range(a + 1, 14) if b != (a ^ 1)]
    q = [
        {j for j, f in enumerate(labels) if i != j and (e[0] in f or e[1] in f)}
        for i, e in enumerate(labels)
    ]
    q2 = product(q, q)
    q3 = product(q2, q)
    assert [rank(q), rank(q2), rank(q3)] == [12, 6, 0]
    assert all(not row for row in q3)

    b0 = [x ^ y for x, y in zip(q, q2)]
    lhs = [x ^ y for x, y in zip(product(b0, b0), b0)]
    assert lhs == q
    assert all(i not in b0[i] for i in range(84))
    assert all((j in b0[i]) == (i in b0[j]) for i in range(84) for j in range(84))
    assert {len(row) for row in b0} == {22}

    # Nullity increments 72,6,6 give 66 blocks of size one and six of size
    # three.  The 66 singleton blocks alone allow a 40-dimensional root
    # assignment for x^2+x, so the target 40/44 characteristic split is not
    # rejected at Jordan-form level.
    result = {
        "status": "INDEPENDENT_OUTER_F2_ARTIN_SCHREIER_AUDIT_PASS",
        "producer_imported": False,
        "q_power_ranks": [12, 6, 0],
        "q_jordan_blocks": {"1": 66, "3": 6},
        "dimension_40_assignment_possible": True,
        "explicit_symmetric_zero_diagonal_control": True,
        "control_row_weight": 22,
        "E0_lower_bound": None,
    }
    Path("scratch_theory_outer_f2_artin_schreier_probe_audit.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
