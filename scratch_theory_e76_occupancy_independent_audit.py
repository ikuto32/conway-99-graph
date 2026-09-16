"""Independent exhaustive occupancy audit for the E0=76 equality step.

This file imports no project module.  It enumerates the integer occupancy
matrices by which four vertices from each exceptional fibre can attach to a
four-vertex ordinary fibre.  A dynamic program across the 12 spoke and three
outside fibres verifies directly that per-exceptional collision totals six
and total residual norm 192 force zero residual on every spoke and absolute
residual four on every outside vertex.
"""

from __future__ import annotations

from collections import defaultdict
import itertools
import json
from pathlib import Path


OUTPUT = Path("scratch_theory_e76_occupancy_independent_audit.json")


def compositions(total, length):
    if length == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for tail in compositions(total - first, length - 1):
            yield (first,) + tail


def collision(values):
    return sum(value * (value - 1) // 2 for value in values)


def spoke_signatures(left, right):
    """One ordinary fibre disjoint from exceptional fibres left,right."""
    signatures = set()
    for a in compositions(4, 4):
        b = tuple(2 - value for value in a)
        if min(b) < 0 or sum(b) != 4:
            continue
        q = tuple(x - y for x, y in zip(a, b))
        U = sum(value * value for value in q) // 4
        collisions = [0, 0, 0, 0]
        collisions[left] = collision(a)
        collisions[right] = collision(b)
        assert U == sum(collisions)
        signatures.add((tuple(collisions), U, all(value == 0 for value in q)))
    return tuple(sorted(signatures))


def outside_signatures():
    """One ordinary fibre disjoint from all four exceptional fibres."""
    signatures = set()
    rows = tuple(compositions(4, 4))
    matrix_count = 0
    for first in rows:
        for second in rows:
            for third in rows:
                residual = tuple(4-first[i]-second[i]-third[i] for i in range(4))
                if min(residual) < 0 or sum(residual) != 4:
                    continue
                matrix = (first, second, third, residual)
                matrix_count += 1
                assert all(sum(matrix[f][x] for f in range(4)) == 4 for x in range(4))
                q = tuple(
                    matrix[0][x] + matrix[2][x] - matrix[1][x] - matrix[3][x]
                    for x in range(4)
                )
                assert sum(q) == 0
                U = sum(value * value for value in q) // 4
                collisions = tuple(collision(row) for row in matrix)
                rigid = all(abs(value) == 4 for value in q)
                signatures.add((collisions, U, rigid))
    assert matrix_count > 0
    assert all(U - sum(collisions) <= 8 for collisions, U, _rigid in signatures)
    return tuple(sorted(signatures)), matrix_count


def advance(states, signatures, kind):
    following = {}
    for (collisions, U), flags in states.items():
        for increments, add_U, rigid in signatures:
            next_collisions = tuple(a + b for a, b in zip(collisions, increments))
            next_U = U + add_U
            if max(next_collisions) > 6 or next_U > 48:
                continue
            spoke_nonzero, outside_nonrigid = flags
            if kind == "spoke":
                spoke_nonzero = spoke_nonzero or not rigid
            else:
                outside_nonrigid = outside_nonrigid or not rigid
            key = (next_collisions, next_U)
            previous = following.get(key, (False, False))
            following[key] = (
                previous[0] or spoke_nonzero,
                previous[1] or outside_nonrigid,
            )
    return following


def main():
    # Exceptional signs around the C4 are +,-,+,-.  Each adjacent pair of
    # exceptional fibres occurs in three spoke supports.
    spoke_pairs = ((0, 1), (1, 2), (2, 3), (3, 0))
    spoke_catalogues = {pair: spoke_signatures(*pair) for pair in spoke_pairs}
    outside, outside_matrix_count = outside_signatures()

    states = {((0, 0, 0, 0), 0): (False, False)}
    stage_counts = []
    for pair in spoke_pairs:
        for _ in range(3):
            states = advance(states, spoke_catalogues[pair], "spoke")
            stage_counts.append(len(states))
    for _ in range(3):
        states = advance(states, outside, "outside")
        stage_counts.append(len(states))

    target = ((6, 6, 6, 6), 48)
    assert target in states
    bad_flags = states[target]
    # The OR flags say whether *some* path to the target was bad.  Both must
    # remain false, so every path has the forced rigidity.
    assert bad_flags == (False, False)
    result = {
        "status": "INDEPENDENT_EXHAUSTIVE_OCCUPANCY_VERIFIED",
        "imports_project_code": False,
        "spoke_signature_counts": {
            f"{left}-{right}": len(spoke_catalogues[left, right])
            for left, right in spoke_pairs
        },
        "outside_contingency_matrices_enumerated": outside_matrix_count,
        "outside_distinct_signatures": len(outside),
        "dynamic_program_stage_state_counts": stage_counts,
        "target": {"collisions_per_exceptional_fibre": [6, 6, 6, 6],
                   "sum_q_square_over_4": 48},
        "target_reachable": True,
        "any_target_path_with_nonzero_spoke_q": bad_flags[0],
        "any_target_path_with_outside_abs_q_not_four": bad_flags[1],
        "conclusion": (
            "Every target occupancy has q=0 on all spoke vertices and "
            "|q|=4 on all outside vertices."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
