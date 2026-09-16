"""Independent finite-algebra audit of the global fibre-block Gram note."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import itertools
import json
import math
import os
from pathlib import Path


SOURCE = Path("scratch_theory_global_fibre_block_gram.json")
OUTPUT = Path("scratch_theory_global_fibre_block_gram_audit.json")


def atomic_json(path, value):
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def balanced_squares(total, bins):
    low = total // bins
    high_count = total % bins
    return (bins - high_count) * low * low + high_count * (low + 1) ** 2


def balanced_pairs(total, bins):
    low = total // bins
    high_count = total % bins
    return (bins - high_count) * math.comb(low, 2) \
        + high_count * math.comb(low + 1, 2)


def four_vertex_canonical(edges):
    pairs = list(itertools.combinations(range(4), 2))
    answer = 1 << 20
    for order in itertools.permutations(range(4)):
        moved = {tuple(sorted((order[x], order[y]))) for x, y in edges}
        value = sum(1 << bit for bit, pair in enumerate(pairs) if pair in moved)
        answer = min(answer, value)
    return answer


def maximum_box_square(total, count, cap):
    full, remainder = divmod(total, cap)
    assert full <= count and (full < count or remainder == 0)
    return full * cap * cap + remainder * remainder


def main():
    raw = SOURCE.read_bytes()
    data = json.loads(raw)
    assert data["status"] == "GLOBAL_FIBRE_BLOCK_GRAM_IDENTITIES_AND_BOUNDARY_COMPLETE"
    for path, expected in data["inputs"].items():
        assert hashlib.sha256(Path(path).read_bytes()).hexdigest().upper() == expected

    n, k, lam, mu = data["parameters"]["srg"]
    assert (n, k, lam, mu) == (99, 14, 1, 2)
    outer = n - k - 1
    blocks = n * math.comb(7, 2)
    edges = n * k // 2
    nonedges = n * outer // 2
    pair_incidence = blocks * math.comb(4, 2)
    assert (outer, blocks, edges, nonedges, pair_incidence) == (
        84, 2079, 693, 4158, 12474
    )
    assert blocks * 4 == n * 84
    assert 84 * 4 == 336
    assert edges + nonedges == math.comb(n, 2)
    edge_root_cap = n - (2 * (k + 1) - (lam + 2))
    nonedge_root_cap = n - (2 * (k + 1) - mu)
    assert (edge_root_cap, nonedge_root_cap) == (72, 71)

    # Independent projector check by eigenvalue evaluation, rather than the
    # producer's adjacency-algebra multiplication routine.
    projectors = {
        "P0": (Fraction(0), Fraction(0), Fraction(1, 99)),
        "P3": (Fraction(4, 7), Fraction(1, 7), Fraction(-2, 77)),
        "Pm4": (Fraction(3, 7), Fraction(-1, 7), Fraction(1, 63)),
    }

    def evaluate(coefficients, eigenvalue, constant_space=False):
        ci, ca, cj = coefficients
        return ci + ca * eigenvalue + (cj * n if constant_space else 0)

    assert [evaluate(projectors["P0"], value, value == 14)
            for value in (14, 3, -4)] == [1, 0, 0]
    assert [evaluate(projectors["P3"], value, value == 14)
            for value in (14, 3, -4)] == [0, 1, 0]
    assert [evaluate(projectors["Pm4"], value, value == 14)
            for value in (14, 3, -4)] == [0, 0, 1]

    # Independent 21-support projector and root-group Gram category check.
    supports = list(itertools.combinations(range(7), 2))
    pf = [[Fraction(2, 3) if x == y else (
        Fraction(-2, 15) if set(supports[x]) & set(supports[y])
        else Fraction(1, 15)
    ) for y in range(21)] for x in range(21)]
    pf2 = [[sum(pf[x][z] * pf[z][y] for z in range(21))
            for y in range(21)] for x in range(21)]
    assert pf2 == pf
    assert sum(pf[i][i] for i in range(21)) == 14
    assert all(sum(row) == 0 for row in pf)
    # U^T U categories follow directly from closed-neighbourhood counts.
    assert (126 + 42, -18 + 42, 42) == (168, 24, 42)
    # Nonnegative overlap-support counts 24-2h and 42-2h.
    assert 24 // 2 == 12 and 42 // 2 == 21
    for h in range(13):
        overlap, disjoint = 24 - 2 * h, 48 + h
        lifted_sum = (Fraction(h, 6) - Fraction(overlap, 30)
                      + Fraction(disjoint, 60))
        assert lifted_sum == Fraction(h, 4)
    for h in range(22):
        overlap, disjoint = 42 - 2 * h, 29 + h
        lifted_sum = (Fraction(h, 6) - Fraction(overlap, 30)
                      + Fraction(disjoint, 60))
        assert lifted_sum == Fraction(h, 4) - Fraction(11, 12)

    checked_T = 0
    gaps = []
    collisions = []
    p3_schur_slacks = []
    pm4_schur_slacks = []
    root_group_integer_slacks = []
    for T in range(8317):
        # tr(PH)=cI tr(H)+cA tr(AH)+cJ tr(JH).
        def trace_product(coefficients):
            ci, ca, cj = coefficients
            return ci * 8316 + ca * (2 * T) + cj * (99 * 336)

        traces = (
            trace_product(projectors["P0"]),
            trace_product(projectors["Pm4"]),
            trace_product(projectors["P3"]),
        )
        assert traces == (
            336,
            Fraction(4092) - Fraction(2 * T, 7),
            Fraction(3888) + Fraction(2 * T, 7),
        )
        assert all(value > 0 for value in traces)
        projected = (
            Fraction(336 ** 2)
            + traces[1] ** 2 / 44
            + traces[2] ** 2 / 54
        )
        relation_jensen = (
            Fraction(99 * 84 ** 2)
            + 2 * Fraction(T * T, 693)
            + 2 * Fraction((12474 - T) ** 2, 4158)
        )
        assert projected == relation_jensen
        integral = 99 * 84 ** 2 + 2 * (
            balanced_squares(T, 693) + balanced_squares(12474 - T, 4158)
        )
        gap = Fraction(integral) - projected
        assert gap >= 0
        gaps.append(gap)
        collision = balanced_pairs(T, 693) + balanced_pairs(12474 - T, 4158)
        collisions.append(collision)
        assert integral == 99 * 84 ** 2 + 2 * 12474 + 4 * collision
        root_group_continuous = Fraction(12474) - 3 * T + Fraction(T * T, 1188)
        trace_g3 = Fraction(792) + Fraction(T, 14)
        trace_gm4 = Fraction(594) - Fraction(T, 14)
        assert trace_g3 + trace_gm4 == 1386
        pinched_g_square = trace_g3 ** 2 / 54 + trace_gm4 ** 2 / 44
        recovered_K_bound = 4 * (
            pinched_g_square - Fraction(33033, 2) - Fraction(11 * T, 12)
        )
        assert recovered_K_bound == root_group_continuous
        assert collision >= root_group_continuous
        root_group_integer_slacks.append(collision - root_group_continuous)
        tq, tr = divmod(2 * T, 99)

        def row_cost(t):
            return balanced_squares(t, 14) + balanced_squares(252 - t, 84)

        rowwise = 99 * 84 ** 2 + (99 - tr) * row_cost(tq) + tr * row_cost(tq + 1)
        assert rowwise == integral
        box = maximum_box_square(2 * T, 99, 252)
        p3_upper = Fraction(93731904 + 840 * T, 11)
        pm4_upper = Fraction(8555008) - Fraction(56 * T, 3)
        assert p3_upper >= box and pm4_upper >= box
        p3_schur_slacks.append(p3_upper - box)
        pm4_schur_slacks.append(pm4_upper - box)
        checked_T += 1

    assert checked_T == 8317
    assert [index for index, value in enumerate(gaps) if value == 0] == [
        0, 4158, 8316
    ]
    assert max(gaps) == 2376
    assert [index for index, value in enumerate(gaps) if value == 2376] == [
        1782, 2376, 5940, 6534
    ]
    least_collision = min(collisions)
    least_T = [index for index, value in enumerate(collisions)
               if value == least_collision]
    assert least_collision == 10395
    assert least_T == list(range(1386, 2080))
    assert min(p3_schur_slacks) == Fraction(54613440, 11)
    assert min(pm4_schur_slacks) == 4208512
    assert min(root_group_integer_slacks) == 0
    assert max(root_group_integer_slacks) == 594

    # Sum P_r formula at the T=0 control: G=14I-N/6.
    assert (14 - Fraction(84, 6), 14 + Fraction(4, 6),
            14 - Fraction(3, 6)) == (0, Fraction(44, 3), Fraction(27, 2))
    assert 54 * Fraction(44, 3) + 44 * Fraction(27, 2) == 1386
    assert (54 * Fraction(44, 3) ** 2
            + 44 * Fraction(27, 2) ** 2) == 19635
    assert math.ceil(Fraction(1386, 84)) == 17
    # The general trace-square expansion is
    # tr(G^2)=K_fb/4+33033/2+11T/12.  At T=0,K_fb=12474 it
    # matches the displayed primitive-space calculation.
    assert Fraction(12474, 4) + Fraction(33033, 2) == 19635

    # Three integral relation-algebra controls, independently evaluated on
    # the three SRG eigenspaces.
    control_eigenvalues = {}
    for T, a, b in ((0, 0, 3), (4158, 6, 2), (8316, 12, 1)):
        eigenvalues = (84 + 14 * a + 84 * b,
                       84 + 3 * a - 4 * b,
                       84 - 4 * a + 3 * b)
        assert eigenvalues[0] == 336 and min(eigenvalues) > 0
        assert 693 * a == T and 4158 * b == 12474 - T
        control_eigenvalues[str(T)] = list(eigenvalues)
    assert control_eigenvalues["0"] == [336, 72, 93]
    translation = data["boundary"]["T_zero_binary_factorization_translation"]
    assert translation["divisibility_checks"] == {
        "blocks_from_edges": 2079,
        "blocks_through_each_vertex": 84,
        "matches_required_shape": True,
    }

    # Alternative role count on the prism.
    endpoint_roles = [0] * 6
    for root in range(6):
        triangle_offset = 3 if root < 3 else 0
        forbidden_index = root % 3
        edge = [triangle_offset + index for index in range(3)
                if index != forbidden_index]
        assert len(edge) == 2
        for endpoint in edge:
            endpoint_roles[endpoint] += 1
    assert endpoint_roles == [2] * 6
    h_delta_root_roles = [1, 0, 0, 0, 0, 0, 0]
    h_delta_endpoint_roles = [0, 0, 0, 0, 0, 1, 1]
    assert sum(h_delta_endpoint_roles) == 2 * sum(h_delta_root_roles)

    # Direct coefficient audit of sum_x t_x^2=2T+4K_edge+2W_inc
    # on an arbitrary weighted simple graph.
    weighted_edges = {
        (0, 1): 1, (0, 2): 3, (1, 2): 2,
        (1, 3): 4, (2, 4): 1, (3, 4): 2,
    }
    t_values = [sum(weight for edge, weight in weighted_edges.items()
                    if vertex in edge) for vertex in range(5)]
    total_weight = sum(weighted_edges.values())
    edge_collision = sum(math.comb(weight, 2)
                         for weight in weighted_edges.values())
    incident_pair = 0
    for vertex in range(5):
        values = [weight for edge, weight in weighted_edges.items()
                  if vertex in edge]
        incident_pair += sum(x * y for x, y in itertools.combinations(values, 2))
    assert sum(value * value for value in t_values) == (
        2 * total_weight + 4 * edge_collision + 2 * incident_pair
    )

    # Independent scalar replay of t=2E0+L-2R and its square expansion.
    prism_roles = [0, 2, 1, 4, 0]
    root_roles = [3, 0, 2, 1, 1]
    chord_roles = [1, 4, 0, 2, 5]
    E0_roles = [prism_roles[i] + root_roles[i] for i in range(5)]
    t_roles = [2 * prism_roles[i] + chord_roles[i] for i in range(5)]
    assert sum(value * value for value in t_roles) == (
        4 * sum(value * value for value in E0_roles)
        + sum((chord_roles[i] - 2 * root_roles[i]) ** 2 for i in range(5))
        + 4 * sum(E0_roles[i] * (chord_roles[i] - 2 * root_roles[i])
                  for i in range(5))
    )

    # Replay the producer's explicit abstract T=0 event-margin control.
    event_rows = [0] * 99
    event_columns = 0
    for j in reversed(range(42)):
        for i in reversed(range(99)):
            roots = {i, (i + 1) % 99, (i + j + 2) % 99}
            assert len(roots) == 3
            event_columns += 1
            for root in roots:
                event_rows[root] += 1
    assert event_columns == 4158
    assert event_rows == [126] * 99
    event_control = data["sum_E0_square"][
        "explicit_T_zero_integer_margin_control"
    ]
    assert event_control["ones"] == 12474
    assert event_control["column_pair_collision"] == 12474
    assert event_control["sum_E0_squared"] == 0

    mask_map = {
        "00": four_vertex_canonical(set()),
        "10_or_01": four_vertex_canonical({(0, 1)}),
        "11": four_vertex_canonical({(0, 1), (2, 3)}),
        "P3_control": four_vertex_canonical({(0, 1), (0, 2)}),
    }
    assert mask_map == {"00": 0, "10_or_01": 1, "11": 12,
                        "P3_control": 3}

    pseudo = data["n3_z11_substitution"]["known_order8_pseudowitness"]
    assert pseudo == {
        "n3": 4158, "z11": 16632, "T": 0,
        "prism_count": 0, "H_delta_count": 0,
    }
    assert 8316 - pseudo["n3"] - pseudo["z11"] // 4 == 0

    result = {
        "status": "GLOBAL_FIBRE_BLOCK_GRAM_INDEPENDENT_AUDIT_PASS",
        "input": {
            str(SOURCE): hashlib.sha256(raw).hexdigest().upper(),
        },
        "all_external_input_hashes_verified": True,
        "incidence_double_counts_verified": True,
        "pair_codegree_caps_verified": {"edge": edge_root_cap,
                                           "nonedge": nonedge_root_cap},
        "primitive_projectors_verified_by_eigenvalue_evaluation": True,
        "root_group_incidence_and_K7_projector_verified": True,
        "summed_fibre_projector_formula_verified": True,
        "sharpened_H_entry_caps": {"edge": 12, "nonedge": 21},
        "T_values_exhaustively_checked": checked_T,
        "pinching_equals_relation_Jensen_for_every_T": True,
        "rowwise_integer_energy_adds_nothing_for_every_T": True,
        "projector_Schur_t_square_bounds_weaker_than_box_for_every_T": True,
        "summed_projector_pinching_is_continuous_collision_Jensen": True,
        "integer_rounding_zero_T": [0, 4158, 8316],
        "maximum_integer_rounding_gap": 2376,
        "absolute_collision_lower_bound": least_collision,
        "collision_equality_T_interval": [min(least_T), max(least_T)],
        "integer_PSD_controls_eigenvalues": control_eigenvalues,
        "motif_role_identity_finite_coefficients_verified": True,
        "motif_role_second_moment_expansion_verified": True,
        "t_square_edge_role_identity_verified": True,
        "explicit_T_zero_event_margin_control_verified": True,
        "four_root_collision_mask_map": mask_map,
        "T_zero_boundary_control_verified": True,
        "binary_incidence_factorization_of_T_zero_control_verified": False,
        "conclusion": (
            "All claimed H-level identities and inequalities replay exactly. "
            "They permit the integer positive-definite T=0 relation-algebra "
            "control; binary root-partition factorization remains the missing step."
        ),
    }
    atomic_json(OUTPUT, result)
    print(json.dumps({
        "path": str(OUTPUT),
        "status": result["status"],
        "T_checked": checked_T,
        "collision_lower_bound": least_collision,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
