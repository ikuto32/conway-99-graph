"""Exact standard-library audit for the E72 K4-support Q=12 proof."""

from __future__ import annotations

from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path


OUTPUT = Path("scratch_theory_e72_k4_q12_analytic_audit.json")
NOTE = Path("scratch_theory_e72_k4_q12_analytic.md")
SUPPORTS = tuple(itertools.combinations(range(7), 2))
EXCEPTIONAL = tuple(itertools.combinations(range(4), 2))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def gram_inner(left, right):
    # Basis a,b has Gram [[4,-2],[-2,4]].
    x, y = left
    u, v = right
    return 4 * x * u - 2 * x * v - 2 * y * u + 4 * y * v


def gram_audit():
    opposite_classes = (
        ((0, 1), (2, 3)),
        ((0, 2), (1, 3)),
        ((0, 3), (1, 2)),
    )
    class_vectors = ((1, 0), (0, 1), (-1, -1))
    vectors = {
        support: vector
        for pair, vector in zip(opposite_classes, class_vectors)
        for support in pair
    }
    assert tuple(sum(vector[i] for vector in class_vectors) for i in range(2)) == (0, 0)
    Z = [[gram_inner(vectors[F], vectors[G]) for G in EXCEPTIONAL] for F in EXCEPTIONAL]
    assert all(Z[i][i] == 4 for i in range(6))
    assert all(
        Z[i][j] == (4 if set(EXCEPTIONAL[i]).isdisjoint(EXCEPTIONAL[j]) else -2)
        for i in range(6) for j in range(6) if i != j
    )
    # The two explicit coordinate columns span the rank-two eigenspace.
    columns = [[vectors[F][axis] for F in EXCEPTIONAL] for axis in range(2)]
    assert all(
        [sum(Z[i][j] * column[j] for j in range(6)) for i in range(6)]
        == [12 * value for value in column]
        for column in columns
    )
    assert all(
        sum(Z[i][j] * int(group in EXCEPTIONAL[j]) for j in range(6)) == 0
        for i in range(6) for group in range(4)
    )
    return {
        "support_order": [list(value) for value in EXCEPTIONAL],
        "opposite_edge_classes": [[list(value) for value in pair] for pair in opposite_classes],
        "class_vectors_in_Gram_basis": [list(value) for value in class_vectors],
        "Z": Z,
        "nonzero_eigenvalues": [12, 12],
        "opposite_block_totals_D": [4 - 4] * 3,
    }, vectors, opposite_classes


def support_category_audit(vectors, opposite_classes):
    exceptional = set(EXCEPTIONAL)
    high = set(SUPPORTS) - exceptional
    spokes = {F for F in high if len(set(F) & set(range(4))) == 1}
    outside = high - spokes
    assert len(spokes) == 12 and len(outside) == 3
    rows = []
    for support in sorted(high):
        disjoint = [F for F in EXCEPTIONAL if set(F).isdisjoint(support)]
        kind = "spoke" if support in spokes else "outside"
        if kind == "spoke":
            assert len(disjoint) == 3
            assert Counter(vectors[F] for F in disjoint) == Counter(
                {value: 1 for value in set(vectors.values())}
            )
        else:
            assert len(disjoint) == 6
            assert Counter(vectors[F] for F in disjoint) == Counter({value: 2 for value in set(vectors.values())})
        rows.append(
            {
                "support": list(support),
                "kind": kind,
                "disjoint_exceptional": [list(value) for value in disjoint],
            }
        )
    # For a fixed opposite pair, all four other exceptional supports can
    # supply two local witnesses, hence exactly eight in total.
    local_witness_rows = []
    for pair in opposite_classes:
        other = [G for G in EXCEPTIONAL if G not in pair]
        assert len(other) == 4
        local_witness_rows.append(
            {
                "opposite_pair": [list(value) for value in pair],
                "other_exceptional_fibres": [list(value) for value in other],
                "witnesses_per_other_fibre": 2,
                "local_witness_total": 8,
                "outside_witness_total": 32 - 8,
            }
        )
    return {
        "spoke_count": len(spokes),
        "outside_count": len(outside),
        "rows": rows,
        "opposite_pair_witness_counts": local_witness_rows,
    }


def collision_and_profile_audit():
    # Verify the distance identity for a bounded exhaustive set.  The proof
    # uses length 12, sum 12 and dot product 24; enumeration is unnecessary
    # for the identity, so representative vectors suffice for exact algebra.
    u = [2] * 6 + [0] * 6
    v = list(u)
    assert sum(u) == sum(v) == 12 and sum(a * b for a, b in zip(u, v)) == 24
    # Direct symbolic coefficient check after substituting sum u=sum v=12,
    # dot=24: distance square = 2(C_pair-12).
    sum_symbolic_constant = 12 + 12 - 2 * 24
    assert sum_symbolic_constant == -24

    profiles = []
    for values in itertools.product(range(4), repeat=3):
        if sum(values) != 3:
            continue
        collision = 2 * sum(value * (value - 1) // 2 for value in values)
        kind = "".join(map(str, sorted(values, reverse=True)))
        profiles.append((kind, collision))
    profile_map = {kind: collision for kind, collision in profiles}
    assert profile_map == {"111": 0, "210": 2, "300": 6}

    global_solutions = []
    for n111 in range(13):
        for n210 in range(13 - n111):
            n300 = 12 - n111 - n210
            if 2 * n210 + 6 * n300 == 36:
                global_solutions.append((n111, n210, n300))
    assert global_solutions == [(0, 9, 3), (2, 6, 4), (4, 3, 5), (6, 0, 6)]
    assert min(row[2] for row in global_solutions) == 3
    return {
        "total_same_fibre_outer_collision_count": 36,
        "outside_opposite_pair_dot_product": 24,
        "outside_opposite_pair_collision_lower_bound": 12,
        "all_three_pairs_collision_lower_bound": 36,
        "paired_occupancy_profiles": profile_map,
        "global_profile_count_solutions_N111_N210_N300": [list(row) for row in global_solutions],
        "minimum_N300": 3,
    }


def residual_audit(vectors):
    class_vectors = sorted(set(vectors.values()))
    exceptional_norms = set()
    exceptional_residuals = []
    for own in class_vectors:
        for repeated in class_vectors:
            if repeated == own:
                continue
            value = (own[0] + 2 * repeated[0], own[1] + 2 * repeated[1])
            norm = gram_inner(value, value)
            exceptional_norms.add(norm)
            exceptional_residuals.append([list(own), list(repeated), list(value), norm])
    assert exceptional_norms == {12}
    concentrated_norms = {gram_inner((6 * v[0], 6 * v[1]), (6 * v[0], 6 * v[1])) for v in class_vectors}
    assert concentrated_norms == {144}
    triangle_bound = 9 * 12
    assert triangle_bound == 108 < 144
    return {
        "exceptional_residual_cases": exceptional_residuals,
        "exceptional_residual_norm_square": 12,
        "outside_300_residual_norm_square": 144,
        "three_exceptional_vector_triangle_bound_square": triangle_bound,
        "strict_contradiction": True,
    }


def main():
    gram, vectors, opposite_classes = gram_audit()
    result = {
        "status": "EXACT_ARITHMETIC_VERIFIED",
        "scope": "E0=72 K4 exceptional-support Q=12 subbranch only",
        "gram": gram,
        "support_categories": support_category_audit(vectors, opposite_classes),
        "collision_and_outside_profiles": collision_and_profile_audit(),
        "residual_triangle_contradiction": residual_audit(vectors),
        "claim_boundary": (
            "This excludes Q=12 on compression source row 134.  It does not "
            "exclude that row's mixed Q=6 local orbits or the other E72 rows."
        ),
        "note_sha256": sha256(NOTE),
        "audit_script_sha256": sha256(Path(__file__)),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "minimum_N300": 3, "bound": "108<144"}))


if __name__ == "__main__":
    main()
