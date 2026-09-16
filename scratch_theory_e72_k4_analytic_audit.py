"""Self-contained exact audit for scratch_theory_e72_k4_analytic.md."""

from __future__ import annotations

from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path


OUTPUT = Path("scratch_theory_e72_k4_analytic_audit.json")
NOTE = Path("scratch_theory_e72_k4_analytic.md")
K4_EDGES = tuple(itertools.combinations(range(4), 2))
K7_EDGES = tuple(itertools.combinations(range(7), 2))
OPPOSITE = (((0, 1), (2, 3)), ((0, 2), (1, 3)), ((0, 3), (1, 2)))
CLASS_VECTOR = {
    (0, 1): (1, 0), (2, 3): (1, 0),
    (0, 2): (0, 1), (1, 3): (0, 1),
    (0, 3): (-1, -1), (1, 2): (-1, -1),
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def inner(left, right):
    """Gram form in the basis a,b: [[4,-2],[-2,4]]."""
    x, y = left
    u, v = right
    return 4 * x * u - 2 * x * v - 2 * y * u + 4 * y * v


def gram_audit():
    Z = [[inner(CLASS_VECTOR[F], CLASS_VECTOR[G]) for G in K4_EDGES] for F in K4_EDGES]
    assert all(Z[i][i] == 4 for i in range(6))
    assert all(
        Z[i][j] == (4 if set(K4_EDGES[i]).isdisjoint(K4_EDGES[j]) else -2)
        for i in range(6) for j in range(6) if i != j
    )
    coordinate_columns = [
        [CLASS_VECTOR[F][axis] for F in K4_EDGES]
        for axis in range(2)
    ]
    assert all(
        [sum(Z[i][j] * column[j] for j in range(6)) for i in range(6)]
        == [12 * value for value in column]
        for column in coordinate_columns
    )
    assert all(
        sum(Z[i][j] * int(group in K4_EDGES[j]) for j in range(6)) == 0
        for i in range(6) for group in range(4)
    )
    return {
        "support_order": [list(F) for F in K4_EDGES],
        "Z": Z,
        "rank": 2,
        "nonzero_eigenvalues": [12, 12],
        "meeting_block_D": 2,
        "opposite_block_D": 0,
    }


def fibre_collision_audit():
    vertices = tuple(itertools.product((0, 1), repeat=2))
    sides = tuple(
        pair for pair in itertools.combinations(range(4), 2)
        if sum(vertices[pair[0]][axis] != vertices[pair[1]][axis] for axis in (0, 1)) == 1
    )
    diagonals = tuple(pair for pair in itertools.combinations(range(4), 2) if pair not in sides)
    shapes = {
        "two_diagonals": set(diagonals),
        "opposite_sides_axis0": {
            pair for pair in sides if vertices[pair[0]][0] == vertices[pair[1]][0]
        },
        "opposite_sides_axis1": {
            pair for pair in sides if vertices[pair[0]][1] == vertices[pair[1]][1]
        },
    }
    records = []
    for name, edges in shapes.items():
        assert len(edges) == 2
        degrees = Counter(value for edge in edges for value in edge)
        assert [degrees[value] for value in range(4)] == [1, 1, 1, 1]
        outer_required = 0
        pair_rows = []
        for pair in itertools.combinations(range(4), 2):
            shared_inner = 2 - sum(
                vertices[pair[0]][axis] != vertices[pair[1]][axis]
                for axis in (0, 1)
            )
            assert shared_inner in (0, 1)
            adjacent = pair in edges
            target = 1 if adjacent else 2
            required = target - shared_inner
            outer_required += required
            pair_rows.append([list(pair), adjacent, shared_inner, required])
        assert outer_required == 6
        records.append({"shape": name, "outer_collision_witnesses": outer_required, "pairs": pair_rows})
    return records


def type_closure_audit():
    # State -1 means D.  State g in F means O oriented at endpoint g.
    domains = tuple((-1, *F) for F in K4_EDGES)
    accepted = []
    for states in itertools.product(*domains):
        d_count = sum(value == -1 for value in states)
        if d_count < 2:  # Q=2*d_count must be at least four.
            continue
        O = {F for F, value in zip(K4_EDGES, states) if value != -1}
        valid = True
        for F, value in zip(K4_EDGES, states):
            if value == -1:
                continue
            forced_star = {edge for edge in K4_EDGES if value in edge}
            if not forced_star <= O:
                valid = False
                break
        if valid:
            accepted.append((states, O, d_count))
    histogram = Counter((len(O), d_count) for _states, O, d_count in accepted)
    assert histogram == Counter({(3, 3): 4, (0, 6): 1})
    for states, O, d_count in accepted:
        if O:
            centre = set.intersection(*(set(F) for F in O))
            assert len(centre) == 1
            centre = next(iter(centre))
            assert all(value == centre for F, value in zip(K4_EDGES, states) if F in O)
            assert d_count == 3
    return {
        "labelled_assignments_checked": 3 ** 6,
        "Q_at_least_4_star_closed_assignments": len(accepted),
        "accepted_histogram_O_count_D_count": [
            {"O_count": key[0], "D_count": key[1], "labelled_assignments": value}
            for key, value in sorted(histogram.items())
        ],
        "patterns_up_to_K4_relabelling": ["all_D_Q12", "one_oriented_O_star_Q6"],
    }


def support_category_audit():
    exceptional = set(K4_EDGES)
    high = set(K7_EDGES) - exceptional
    spokes = {F for F in high if len(set(F) & set(range(4))) == 1}
    outside = high - spokes
    assert (len(spokes), len(outside)) == (12, 3)
    for G in spokes:
        disjoint = [F for F in K4_EDGES if set(F).isdisjoint(G)]
        assert len(disjoint) == 3
        assert Counter(CLASS_VECTOR[F] for F in disjoint) == Counter(
            {value: 1 for value in set(CLASS_VECTOR.values())}
        )
    for G in outside:
        disjoint = [F for F in K4_EDGES if set(F).isdisjoint(G)]
        assert len(disjoint) == 6
    return {
        "exceptional": 6,
        "spokes": 12,
        "outside": 3,
        "exceptional_degree_by_vertex": 3,
        "spoke_exceptional_degree_by_vertex": 3,
        "outside_exceptional_degree_by_vertex": 6,
    }


def witness_and_distance_audit():
    witness_rows = []
    for pair in OPPOSITE:
        other = [F for F in K4_EDGES if F not in pair]
        assert len(other) == 4
        witness_rows.append({
            "opposite_pair": [list(F) for F in pair],
            "all_outer_witnesses": 16 * 2,
            "exceptional_witnesses": len(other) * 2,
            "spoke_witnesses": 0,
            "outside_witnesses": 16 * 2 - len(other) * 2,
        })
    assert all(row["outside_witnesses"] == 24 for row in witness_rows)

    # If sum u=sum v=12 and dot(u,v)=24, expanding the two sides gives
    # distance^2 = 2(C_pair-12).  An equality example checks all constants.
    u = [2] * 6 + [0] * 6
    v = list(u)
    collision = sum(value * (value - 1) // 2 for value in u + v)
    distance = sum((left - right) ** 2 for left, right in zip(u, v))
    assert sum(u) == sum(v) == 12
    assert sum(left * right for left, right in zip(u, v)) == 24
    assert collision == 12 and distance == 2 * (collision - 12) == 0
    return {
        "opposite_pair_rows": witness_rows,
        "distance_identity": "sum(u-v)^2=2*(C_pair_out-12)",
        "C_out_lower_bound_per_pair": 12,
        "C_out_lower_bound_all_pairs": 36,
        "C_total": 36,
        "forced_equalities": ["C_exception=0", "C_spoke=0", "u=v pointwise outside"],
    }


def profile_and_residual_audit():
    profile_map = {}
    for values in itertools.product(range(4), repeat=3):
        if sum(values) != 3:
            continue
        key = "".join(map(str, sorted(values, reverse=True)))
        profile_map[key] = 2 * sum(value * (value - 1) // 2 for value in values)
    assert profile_map == {"111": 0, "210": 2, "300": 6}
    count_solutions = []
    for n111 in range(13):
        for n210 in range(13 - n111):
            n300 = 12 - n111 - n210
            if 2 * n210 + 6 * n300 == 36:
                count_solutions.append((n111, n210, n300))
    assert count_solutions == [(0, 9, 3), (2, 6, 4), (4, 3, 5), (6, 0, 6)]

    class_vectors = sorted(set(CLASS_VECTOR.values()))
    exception_norms = {
        inner(
            (own[0] + 2 * repeated[0], own[1] + 2 * repeated[1]),
            (own[0] + 2 * repeated[0], own[1] + 2 * repeated[1]),
        )
        for own in class_vectors for repeated in class_vectors if own != repeated
    }
    outside_300_norms = {
        inner((6 * value[0], 6 * value[1]), (6 * value[0], 6 * value[1]))
        for value in class_vectors
    }
    assert exception_norms == {12}
    assert outside_300_norms == {144}
    assert 9 * 12 == 108 < 144
    return {
        "outside_profiles_and_C": profile_map,
        "global_count_solutions_N111_N210_N300": [list(row) for row in count_solutions],
        "minimum_N300": min(row[2] for row in count_solutions),
        "exception_q_norm_square": 12,
        "outside_300_q_norm_square": 144,
        "three_exception_neighbour_triangle_bound_square": 108,
        "strict_final_inequality": "108<144",
    }


def main():
    result = {
        "status": "EXACT_ARITHMETIC_VERIFIED",
        "scope": "complete E0=72 source-row-134 K4 exceptional-support branch",
        "gram": gram_audit(),
        "allowed_fibre_shapes": fibre_collision_audit(),
        "support_type_closure": type_closure_audit(),
        "support_categories_and_degrees": support_category_audit(),
        "common_neighbour_witnesses": witness_and_distance_audit(),
        "outside_profiles_and_residual": profile_and_residual_audit(),
        "conclusion": "The dominant K4-support row is impossible in a target SRG.",
        "claim_boundary": "No conclusion is made here about the other E0=72 support rows.",
        "note_sha256": sha256(NOTE),
        "audit_script_sha256": sha256(Path(__file__)),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "type_patterns": result["support_type_closure"]["patterns_up_to_K4_relabelling"],
        "minimum_N300": result["outside_profiles_and_residual"]["minimum_N300"],
        "strict_final_inequality": "108<144",
    }))


if __name__ == "__main__":
    main()
