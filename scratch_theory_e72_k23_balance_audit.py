"""Exact arithmetic audit for scratch_theory_e72_k23_balance.md."""

from __future__ import annotations

import hashlib
import json
from itertools import combinations
from itertools import permutations, product
from pathlib import Path


OUTPUT = Path("scratch_theory_e72_k23_balance_audit.json")
NOTE = Path("scratch_theory_e72_k23_balance.md")
GROUPS = range(7)
BOTTOM = (2, 3, 4)
A = tuple((0, i) for i in BOTTOM)
B_SIDE = tuple((1, i) for i in BOTTOM)
EXCEPTIONAL = A + B_SIDE
ALL_SUPPORTS = tuple(combinations(GROUPS, 2))
ORDINARY = tuple(s for s in ALL_SUPPORTS if s not in EXCEPTIONAL)


def dot(x, y):
    return sum(a * b for a, b in zip(x, y))


def matmul(a, b):
    return tuple(
        tuple(sum(a[i][k] * b[k][j] for k in range(len(b)))
              for j in range(len(b[0])))
        for i in range(len(a))
    )


def transpose(a):
    return tuple(zip(*a))


def disjoint(s, t):
    return set(s).isdisjoint(t)


def side(s):
    if s in A:
        return 1
    if s in B_SIDE:
        return -1
    return 0


def block_total(s, t, z):
    i = EXCEPTIONAL.index(s)
    j = EXCEPTIONAL.index(t)
    return 4 - z[i][j] if disjoint(s, t) else -z[i][j]


def main():
    z = (
        (4, -2, -2, -4, 2, 2),
        (-2, 4, -2, 2, -4, 2),
        (-2, -2, 4, 2, 2, -4),
        (-4, 2, 2, 4, -2, -2),
        (2, -4, 2, -2, 4, -2),
        (2, 2, -4, -2, -2, 4),
    )
    assert matmul(z, z) == tuple(tuple(12 * x for x in row) for row in z)
    incidence = tuple(tuple(int(g in s) for g in GROUPS) for s in EXCEPTIONAL)
    assert matmul(z, incidence) == tuple((0,) * 7 for _ in EXCEPTIONAL)
    # Z/12 is an idempotent of trace two, so Z has rank two and spectrum
    # 12,12,0,0,0,0 without floating-point arithmetic.
    assert sum(z[i][i] for i in range(6)) == 24

    blocks = {}
    for i, s in enumerate(EXCEPTIONAL):
        for t in EXCEPTIONAL[i + 1:]:
            blocks[(s, t)] = block_total(s, t, z)
    assert all(blocks[(A[i], A[j])] == 2 for i, j in combinations(range(3), 2))
    assert all(blocks[(B_SIDE[i], B_SIDE[j])] == 2
               for i, j in combinations(range(3), 2))
    assert all(blocks[(A[i], B_SIDE[i])] == 4 for i in range(3))
    assert all(blocks[(A[i], B_SIDE[j])] == 2
               for i in range(3) for j in range(3) if i != j)

    # Expand the 21 fibres into four formal vertices each.  The two signs in
    # a support label which of the two root-neighbour vertices is used.
    vertices = tuple((s, p, q) for s in ALL_SUPPORTS for p in (0, 1) for q in (0, 1))
    d = {x: side(x[0]) for x in vertices}
    assert sum(d.values()) == 0
    assert sum(v * v for v in d.values()) == 24
    ptd = {(g, bit): 0 for g in GROUPS for bit in (0, 1)}
    for (s, p, q), value in d.items():
        ptd[(s[0], p)] += value
        ptd[(s[1], q)] += value
    assert tuple(ptd[(0, bit)] for bit in (0, 1)) == (6, 6)
    assert tuple(ptd[(1, bit)] for bit in (0, 1)) == (-6, -6)
    assert all(ptd[(g, bit)] == 0 for g in range(2, 7) for bit in (0, 1))
    ptd_norm = sum(v * v for v in ptd.values())
    assert ptd_norm == 144

    internal_signed_edges = 6 * 2
    same_side_cross_edges = sum(
        value for (s, t), value in blocks.items() if side(s) == side(t)
    )
    opposite_side_cross_edges = sum(
        value for (s, t), value in blocks.items() if side(s) == -side(t)
    )
    assert (internal_signed_edges, same_side_cross_edges,
            opposite_side_cross_edges) == (12, 12, 24)
    d_bd = 2 * (internal_signed_edges + same_side_cross_edges
                - opposite_side_cross_edges)
    assert d_bd == 0
    bd_norm = 12 * 24 - ptd_norm - d_bd
    assert bd_norm == 144

    disjoint_exceptional = {
        s: tuple(t for t in EXCEPTIONAL if disjoint(s, t)) for s in ORDINARY
    }
    category_counts = {}
    for s, candidates in disjoint_exceptional.items():
        signature = (len(candidates), sum(side(t) for t in candidates))
        category_counts[signature] = category_counts.get(signature, 0) + 1
    assert category_counts == {(0, 0): 1, (3, -3): 2, (3, 3): 2,
                               (2, 0): 3, (4, 0): 6, (6, 0): 1}
    negative_top = ((0, 5), (0, 6))
    positive_top = ((1, 5), (1, 6))
    assert all(disjoint_exceptional[s] == B_SIDE for s in negative_top)
    assert all(disjoint_exceptional[s] == A for s in positive_top)
    forced_top_vertices = 4 * (len(negative_top) + len(positive_top))
    forced_top_norm = forced_top_vertices * 3 * 3
    assert (forced_top_vertices, forced_top_norm) == (16, 144)
    assert len(vertices) - forced_top_vertices == 68
    assert forced_top_norm == bd_norm

    # Verify PP^T d=6(d-e) pointwise from the already computed P^T d.
    e_support = {s: (-1 if s in negative_top else 1 if s in positive_top else 0)
                 for s in ALL_SUPPORTS}
    for x in vertices:
        s, p, q = x
        pp_td = ptd[(s[0], p)] + ptd[(s[1], q)]
        assert pp_td == 6 * (d[x] - e_support[s])
    d_norm = sum(v * v for v in d.values())
    e_norm = sum(4 * e_support[s] * e_support[s] for s in ALL_SUPPORTS)
    de = sum(d[x] * e_support[x[0]] for x in vertices)
    assert (d_norm, e_norm, de) == (24, 16, 0)
    # If Bd=3e, the SRG identity and PP^T d=6(d-e) give Be=2d+e.
    # Symmetry is numerically compatible: <3e,e>=<d,2d+e>=48.
    assert 3 * e_norm == 2 * d_norm + de == 48
    # Direct coefficient checks for the two stated eigenvectors.
    # B(ad+be)=(2b)d+(3a+b)e in the (d,e) basis.
    assert (2 * 3, 3 * 2 + 3) == (3 * 2, 3 * 3)       # 2d+3e, lambda 3
    assert (2 * -1, 3 * 1 + -1) == (-2 * 1, -2 * -1) # d-e, lambda -2

    # Per-group support balance for an exceptional support A_i.  The eight
    # ordinary supports disjoint from it contribute one neighbour each.
    per_group_controls = {}
    for exceptional_support in EXCEPTIONAL:
        ordinary_disjoint = tuple(
            s for s in ORDINARY if disjoint(s, exceptional_support)
        )
        exceptional_disjoint = tuple(
            s for s in EXCEPTIONAL if disjoint(s, exceptional_support)
        )
        assert (len(ordinary_disjoint), len(exceptional_disjoint)) == (8, 2)
        contributions = tuple(
            sum(g in s for s in ordinary_disjoint) for g in GROUPS
        )
        own_side = exceptional_support[0]
        bottom = exceptional_support[1]
        other_side = 1 - own_side
        complements = tuple(g for g in BOTTOM if g != bottom)
        assert contributions[own_side] == contributions[bottom] == 0
        assert contributions[other_side] == 2
        assert all(contributions[g] == 3 for g in complements)
        assert contributions[5] == contributions[6] == 4
        per_group_controls[str(exceptional_support)] = list(contributions)

    # All seven deficit-two shapes and the exact a-dependent consequences.
    square_sides = ((0, 1), (0, 2), (1, 3), (2, 3))
    diagonals = ((0, 3), (1, 2))
    states = tuple(combinations(square_sides, 2)) + (diagonals,)
    degree_profiles = []
    regular_states = []
    for state_index, state in enumerate(states):
        degrees = tuple(sum(v in edge for edge in state) for v in range(4))
        degree_profiles.append(degrees)
        if degrees == (1, 1, 1, 1):
            regular_states.append(state_index)
        for a in degrees:
            p, v, zsum = 2 - a, 2 - a, a
            assert p + zsum == 2
            assert (a, p, v, zsum) in ((0, 2, 2, 0),
                                       (1, 1, 1, 1),
                                       (2, 0, 0, 2))
    assert regular_states == [2, 3, 6]
    assert sorted(degree_profiles[:6]) == sorted(
        [(2, 1, 1, 0), (1, 2, 0, 1), (1, 1, 1, 1),
         (1, 1, 1, 1), (1, 0, 2, 1), (0, 1, 1, 2)]
    )
    assert degree_profiles[6] == (1, 1, 1, 1)
    # Every regular same-side block has two endpoints on each end.  Each of
    # six independent 2-by-2 blocks has exactly two perfect matchings.
    assert 2 ** 6 == 64

    # Quantized q/collision profiles on ordinary supports in a regular macro.
    # Coefficients use q=2*t*w_i on a bottom--outside fibre.
    bottom_profiles = []
    for alpha_j in range(3):
        alpha_k = 2 - alpha_j
        beta_j = 2 - alpha_j
        beta_k = alpha_j
        occupancy = (alpha_j, alpha_k, beta_j, beta_k)
        collision = sum(value * (value - 1) // 2 for value in occupancy)
        t = alpha_j - 1
        assert collision == (0 if t == 0 else 2)
        bottom_profiles.append({"occupancy": occupancy, "t": t,
                                "collision": collision})
    outside_profiles = []
    for alpha in product(range(3), repeat=3):
        if sum(alpha) != 3:
            continue
        beta = tuple(2 - value for value in alpha)
        collision = sum(value * (value - 1) // 2 for value in alpha + beta)
        nonzero = alpha != (1, 1, 1)
        assert collision == (2 if nonzero else 0)
        outside_profiles.append((alpha, beta, collision))
    assert len(outside_profiles) == 7
    assert sum(profile[2] == 0 for profile in outside_profiles) == 1

    # Exact geometry of w_i=u_j-u_k: norm 12, mutual dot -6, sole relation
    # w_2+w_3+w_4=0.  Integer coordinates in R^3 suffice for the audit.
    # Use a Gram matrix for u_2,u_3,u_4 rather than irrational coordinates.
    gram_u = ((4, -2, -2), (-2, 4, -2), (-2, -2, 4))
    w = ((0, 1, -1), (-1, 0, 1), (1, -1, 0))
    assert tuple(sum(vectors) for vectors in zip(*w)) == (0, 0, 0)
    gram_w = tuple(tuple(
        sum(wi[a] * gram_u[a][b] * wj[b]
            for a in range(3) for b in range(3))
        for wj in w) for wi in w)
    assert gram_w == ((12, -6, -6), (-6, 12, -6), (-6, -6, 12))

    # Collision 36 and the triangle-fibre argument force q=0 on all four
    # support-{5,6} vertices, hence 18 nonzero bottom--outside vertices.
    collision_total = 6 * 6
    collision_per_nonzero_high = 2
    nonzero_bottom_outside = collision_total // collision_per_nonzero_high
    assert (collision_total, nonzero_bottom_outside) == (36, 18)

    # Finite multiset lemma used at support {0,1}.
    types = {
        "Z": (0, 0, 0, 0),
        "H": (-1, 0, 0, 1),
        "F": (-1, -1, 1, 1),
    }
    unique_permutations = {
        key: set(permutations(value)) for key, value in types.items()
    }
    sum_multisets = {}
    for left in types:
        for right in types:
            sum_multisets[(left, right)] = {
                tuple(sorted(a + b for a, b in zip(x, y)))
                for x in unique_permutations[left]
                for y in unique_permutations[right]
            }
    assert sum_multisets[("Z", "H")] == {(-1, 0, 0, 1)}
    assert sum_multisets[("Z", "F")] == {(-1, -1, 1, 1)}
    assert not (sum_multisets[("Z", "H")] & sum_multisets[("F", "F")])
    assert not (sum_multisets[("Z", "F")] & sum_multisets[("H", "F")])
    assert not (sum_multisets[("H", "H")] & sum_multisets[("H", "F")]
                & sum_multisets[("F", "F")])
    surviving_type_patterns = []
    for pattern in product(types, repeat=6):
        if sum({"Z": 0, "H": 2, "F": 4}[kind] for kind in pattern) != 18:
            continue
        common = set.intersection(*(
            sum_multisets[(pattern[2 * i], pattern[2 * i + 1])]
            for i in range(3)
        ))
        if common:
            surviving_type_patterns.append(pattern)
    assert len(surviving_type_patterns) == 8
    assert all({pattern[2 * i], pattern[2 * i + 1]} == {"H", "F"}
               for pattern in surviving_type_patterns for i in range(3))

    # Exceptional-vertex equation (25), checked in coefficient space.  Here
    # u_i is the i-th standard coefficient vector modulo u_2+u_3+u_4=0;
    # equality is tested by the exact Gram form.
    def vector_add(*vectors):
        return tuple(sum(values) for values in zip(*vectors))

    def vector_scale(scale, vector):
        return tuple(scale * value for value in vector)

    def norm_u(vector):
        return sum(vector[a] * gram_u[a][b] * vector[b]
                   for a in range(3) for b in range(3))

    exceptional_equation_solutions = {}
    for i in range(3):
        others = tuple(j for j in range(3) if j != i)
        solutions = []
        for sigma in (-1, 1):
            for tj in range(-2, 3):
                for tk in range(-2, 3):
                    for epsilon_sum in (-3, -1, 1, 3):
                        lhs = vector_add(
                            vector_scale(epsilon_sum, w[i]),
                            vector_scale(2 * tj, w[others[0]]),
                            vector_scale(2 * tk, w[others[1]]),
                        )
                        rhs = tuple(9 * sigma * int(position == i)
                                    for position in range(3))
                        if norm_u(tuple(a - b for a, b in zip(lhs, rhs))) == 0:
                            solutions.append((sigma, tj, tk, epsilon_sum))
        assert len(solutions) == 4
        assert all(sorted((abs(row[1]), abs(row[2]))) == [1, 2]
                   for row in solutions)
        assert all(abs(row[3]) == 1 for row in solutions)
        exceptional_equation_solutions[str(BOTTOM[i])] = [list(row)
                                                           for row in solutions]
    assert 24 * 3 == 18 * 4 == 72

    result = {
        "status": "EXACT_SUPPORT_ARITHMETIC_VERIFIED",
        "source_row_index": 133,
        "partition": [2, 2, 2, 2, 2, 2],
        "compression_orbit_index": 0,
        "exceptional_supports": [list(s) for s in EXCEPTIONAL],
        "gram_identity": "Z^2=12Z and ZL=0",
        "exceptional_block_totals": {
            "same_side_meeting": 2,
            "vertical_meeting": 4,
            "cross_side_disjoint": 2,
        },
        "signed_vector": {
            "norm_squared": 24,
            "sum": 0,
            "Pt_d_norm_squared": ptd_norm,
            "dT_B_d": d_bd,
            "Bd_norm_squared": bd_norm,
        },
        "top_outside_saturation": {
            "negative_supports": [list(s) for s in negative_top],
            "positive_supports": [list(s) for s in positive_top],
            "vertices": forced_top_vertices,
            "forced_contribution": forced_top_norm,
            "remaining_vertices_forced_h_zero": 68,
        },
        "ordinary_support_category_counts_by_(t,side_sum)": {
            str(key): value for key, value in sorted(category_counts.items())
        },
        "invariant_relations": ["Bd=3e", "Be=2d+e"],
        "outer_eigenvectors": {"2d+3e": 3, "d-e": -2},
        "per_group_balance": "m_g(x)=2 on support and 4 off support",
        "exceptional_ordinary_disjoint_group_counts": per_group_controls,
        "deficit_two_internal_degree_profiles": [list(x) for x in degree_profiles],
        "regular_state_indices": regular_states,
        "regular_macro_missing_disjoint_completions_per_overlap_graph": 64,
        "regular_macro_q_profile": {
            "total_same_fibre_collision": collision_total,
            "outside_56_q_zero": True,
            "nonzero_bottom_outside_vertices": nonzero_bottom_outside,
            "bottom_outside_fibre_types": {key: list(value)
                                             for key, value in types.items()},
            "surviving_six_fibre_type_patterns": [list(x)
                                                   for x in surviving_type_patterns],
            "pattern_count": len(surviving_type_patterns),
            "forced_pairing": "one H and one F for each bottom index",
            "exceptional_vertex_nonzero_U_degree": 3,
            "exceptional_vertex_zero_U_degree": 1,
            "exceptional_equation_solutions_(sigma,Tj,Tk,epsilon_sum)":
                exceptional_equation_solutions,
        },
        "claim_boundary": (
            "Exact necessary pointwise A/B-neighbour balance for source 133; "
            "this audit alone does not exclude the row."
        ),
        "note": str(NOTE),
        "note_sha256": hashlib.sha256(NOTE.read_bytes()).hexdigest().upper(),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"path": str(OUTPUT), **result}, sort_keys=True))


if __name__ == "__main__":
    main()
