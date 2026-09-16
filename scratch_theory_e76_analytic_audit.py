"""Exact arithmetic audit for scratch_theory_e76_analytic.md."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path


OUTPUT = Path("scratch_theory_e76_analytic_audit.json")
SUPPORTS = tuple(itertools.combinations(range(7), 2))
INDEX = {support: i for i, support in enumerate(SUPPORTS)}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def fibre_capacity_audit():
    # (name, deficit, Q)
    types = (
        ("C4", 0, 0),
        ("P4", 1, 0),
        ("two_sides", 2, 0),
        ("two_diagonals", 2, 2),
        ("one_side", 3, 0),
        ("one_diagonal", 3, 1),
        ("empty", 4, 0),
    )
    states = {(0, 0, (0,) * len(types))}
    for _ in range(21):
        following = set()
        for deficit, Q, counts in states:
            for index, (_name, d, q) in enumerate(types):
                if deficit + d > 8:
                    continue
                changed = list(counts)
                changed[index] += 1
                following.add((deficit + d, Q + q, tuple(changed)))
        states = following
    candidates = [state for state in states if state[0] == 8 and state[1] >= 7]
    assert len(candidates) == 1
    deficit, Q, counts = candidates[0]
    assert deficit == 8 and Q == 8
    assert counts[0] == 17 and counts[3] == 4 and sum(counts) == 21
    return {
        "fibre_types": [list(row) for row in types],
        "deficit_8_Q_at_least_7_type_count_vectors": [list(counts)],
        "forced_Q": Q,
        "forced_two_diagonal_fibres": 4,
    }


def support_and_compression_audit():
    cycle = ((0, 1), (1, 2), (2, 3), (0, 3))
    signs = {(0, 1): 1, (1, 2): -1, (2, 3): 1, (0, 3): -1}
    w = [signs.get(support, 0) for support in SUPPORTS]
    delta = [2 if support in signs else 0 for support in SUPPORTS]
    Z = [[4 * w[i] * w[j] for j in range(21)] for i in range(21)]
    D = [[0] * 21 for _ in range(21)]
    for i, F in enumerate(SUPPORTS):
        for j, G in enumerate(SUPPORTS):
            if i == j:
                D[i][j] = 8 - 2 * delta[i]
            elif set(F).intersection(G):
                D[i][j] = -Z[i][j]
            else:
                D[i][j] = 4 - Z[i][j]
    assert all(sum(row) == 48 for row in D)
    assert [sum(D[i][j] * w[j] for j in range(21)) for i in range(21)] == [
        -4 * value for value in w
    ]
    assert all(
        sum(Z[i][j] * int(group in SUPPORTS[j]) for j in range(21)) == 0
        for i in range(21) for group in range(7)
    )
    eigen_quadratic = sum(w[i] * D[i][j] * w[j] for i in range(21) for j in range(21))
    assert eigen_quadratic == -16
    return {
        "cycle_supports": [list(edge) for edge in cycle],
        "cycle_signs": [signs[edge] for edge in cycle],
        "Z_rank_one_formula": "Z_ij=4*w_i*w_j",
        "D_row_sums": sorted(set(sum(row) for row in D)),
        "Dw": [-4 * value for value in w],
        "wTDw": eigen_quadratic,
    }


def category_audit():
    exceptional = {(0, 1), (1, 2), (2, 3), (0, 3)}
    high = set(SUPPORTS) - exceptional
    cycle_groups = {0, 1, 2, 3}
    outside_groups = {4, 5, 6}
    chords = {edge for edge in high if set(edge) <= cycle_groups}
    outside = {edge for edge in high if set(edge) <= outside_groups}
    spokes = high - chords - outside
    assert (len(chords), len(spokes), len(outside)) == (2, 12, 3)
    signs = {(0, 1): 1, (1, 2): -1, (2, 3): 1, (0, 3): -1}
    rows = []
    for name, collection in (("chord", chords), ("spoke", spokes), ("outside", outside)):
        for support in sorted(collection):
            disjoint = [F for F in exceptional if not set(F).intersection(support)]
            rows.append({
                "kind": name,
                "support": list(support),
                "disjoint_exceptional_count": len(disjoint),
                "disjoint_exceptional_sign_sum": sum(signs[F] for F in disjoint),
            })
    assert all(row["disjoint_exceptional_count"] == 0 for row in rows if row["kind"] == "chord")
    assert all(
        row["disjoint_exceptional_count"] == 2 and row["disjoint_exceptional_sign_sum"] == 0
        for row in rows if row["kind"] == "spoke"
    )
    assert all(
        row["disjoint_exceptional_count"] == 4 and row["disjoint_exceptional_sign_sum"] == 0
        for row in rows if row["kind"] == "outside"
    )
    return {"counts": {"chords": 2, "spokes": 12, "outside": 3}, "rows": rows}


def occupancy_audit():
    spoke_rows = []
    for a in range(3):
        b = 2 - a
        q = a - b
        collision = a * (a - 1) // 2 + b * (b - 1) // 2
        assert q * q // 4 == collision
        spoke_rows.append({"occupancies": [a, b], "q": q, "q_square_over_4": q * q // 4,
                           "collision": collision})

    outside_rows = []
    equality_rows = []
    for values in itertools.product(range(5), repeat=4):
        if sum(values) != 4:
            continue
        positive = values[0] + values[1]
        q = 2 * positive - 4
        collision = sum(value * (value - 1) // 2 for value in values)
        difference = q * q // 4 - collision
        assert difference <= 2
        row = {"occupancies": list(values), "q": q, "collision": collision, "difference": difference}
        outside_rows.append(row)
        if difference == 2:
            equality_rows.append(row)
            assert positive in (0, 4)
            occupied = values[:2] if positive == 4 else values[2:]
            assert sorted(occupied) == [2, 2]
    assert len(outside_rows) == 35
    assert len(equality_rows) == 2
    assert all(abs(row["q"]) == 4 for row in equality_rows)
    parity_sums = sorted(set(sum(values) for values in itertools.product((-4, 4), repeat=3)))
    assert 0 not in parity_sums
    return {
        "spoke_profiles": spoke_rows,
        "outside_profile_count": len(outside_rows),
        "outside_equality_profiles": equality_rows,
        "three_signed_fours_possible_sums": parity_sums,
    }


def main():
    capacity = fibre_capacity_audit()
    compression = support_and_compression_audit()
    categories = category_audit()
    occupancy = occupancy_audit()
    # Exact scalar checks in the residual-vector proof.
    c_norm = 16
    c_B_c = -16
    c_B2_c = 12 * c_norm - c_B_c
    q_norm = c_B2_c + 2 * c_B_c + c_norm
    assert c_B2_c == 208 and q_norm == 192
    U_total = q_norm // 4
    collision_total = 4 * 6
    outside_vertex_count = categories["counts"]["outside"] * 4
    assert U_total - collision_total == outside_vertex_count * 2
    result = {
        "status": "EXACT_ARITHMETIC_VERIFIED",
        "model": "analytic selected-root E0=76 exclusion",
        "fibre_capacity": capacity,
        "support_and_compression": compression,
        "ordinary_support_categories": categories,
        "occupancy_inequalities": occupancy,
        "residual_norm": {
            "c_norm_square": c_norm,
            "cTBc": c_B_c,
            "cTB2c": c_B2_c,
            "q_norm_square": q_norm,
            "sum_q_square_over_4": U_total,
        },
        "collision_equalities": {
            "per_exceptional_two_diagonal_fibre": 6,
            "all_four_exceptional_fibres": collision_total,
            "outside_vertex_count": outside_vertex_count,
            "maximum_total_outside_excess": outside_vertex_count * 2,
            "equality_forced": True,
            "spokes_q_zero_forced": True,
            "outside_q_absolute_value_four_forced": True,
        },
        "chord_contradiction": (
            "Bq at a chord vertex is the sum of three values in {+4,-4}, "
            "which is nonzero, while Bq=12c requires zero."
        ),
        "conclusion": "The selected root cannot have E0=76.",
    }
    result["audit_script_sha256"] = sha256(Path(__file__))
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "q_norm_square": q_norm,
                      "outside_equality_profiles": len(occupancy["outside_equality_profiles"])}))


if __name__ == "__main__":
    main()
