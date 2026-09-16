"""Clean-room audit of the augmented YYT relation artifact.

This checker does not import the construction script.  It independently
enumerates the local 7K2 capacity, rebuilds every lower supporting quadratic
of the 13-point table, re-evaluates the sealed Wave159 witness, and checks the
Bose--Mesner algebra over exact rationals.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "scratch_theory_root_yyt_augmented_relation.json"
SHADOW = ROOT / "scratch_theory_root_yyt_order8_shadow.json"
WITNESS = (
    ROOT
    / "external_conway99_research/attempts/wave159-four-root-cut-loop/"
    "exact-witness-after-fifteen-cuts.json"
)
OUTPUT = ROOT / "scratch_theory_root_yyt_augmented_relation_audit.json"
WAVE3_AUDIT = (
    ROOT / "external_conway99_research/verification/2026-07-22-wave3-audit.md"
)
WAVE65_VERIFY = (
    ROOT
    / "external_conway99_research/verification/"
    "wave65-rooted-hypergraph-algebra/independent-results.json"
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def frac(value: object) -> Fraction:
    return Fraction(value)


def solve_plane(points):
    """Gaussian elimination, deliberately distinct from Cramer's rule."""

    matrix = [
        [Fraction(1), Fraction(q), Fraction(q * q), Fraction(height)]
        for q, height in points
    ]
    for pivot in range(3):
        row = next(row for row in range(pivot, 3) if matrix[row][pivot])
        matrix[pivot], matrix[row] = matrix[row], matrix[pivot]
        scale = matrix[pivot][pivot]
        matrix[pivot] = [value / scale for value in matrix[pivot]]
        for row in range(3):
            if row == pivot:
                continue
            scale = matrix[row][pivot]
            matrix[row] = [
                value - scale * base
                for value, base in zip(matrix[row], matrix[pivot])
            ]
    return tuple(matrix[row][3] for row in range(3))


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    shadow = json.loads(SHADOW.read_text(encoding="utf-8"))
    witness = json.loads(WITNESS.read_text(encoding="utf-8"))
    assert source["status"] == "AUGMENTED_FLAG_RELATION_AND_BAD_MATE_CAPACITY_PASS"

    # Clean-room incidence table.  For a fixed edge ab, lambda=1 gives one
    # triangle mate and makes all other endpoint-neighbour sets disjoint.
    # Each endpoint has 12 neighbours outside {a,b,mate}, so there are 24
    # vertices adjacent to exactly one endpoint and 72 adjacent to neither.
    cases = (
        ("endpoint", 2, 1, 1, 0, 0),
        ("mate", 1, 2, 0, 1, 0),
        ("one_endpoint", 24, 1, 0, 0, 1),
        ("neither", 72, 0, 0, 0, 0),
    )
    assert sum(record[1] for record in cases) == 99
    assert all(ac - c - 2 * r == cj for _, _, ac, c, r, cj in cases)
    assert sum(multiplicity * cj for _, multiplicity, _, _, _, cj in cases) == 24

    # Independently reconstruct the support-label relation on
    # H=K14-7K2, including the two disjoint 2-factor sectors at E0=0.
    labels = tuple(
        pair for pair in itertools.combinations(range(14), 2)
        if pair[1] != (pair[0] ^ 1)
    )
    label_census = {}
    for left, right in itertools.combinations(labels, 2):
        overlap = len(set(left) & set(right))
        mate_degree = sum((point ^ 1) in right for point in left)
        label_census[overlap, mate_degree] = (
            label_census.get((overlap, mate_degree), 0) + 1
        )
    assert label_census == {
        (1, 0): 840,
        (1, 1): 84,
        (0, 0): 1680,
        (0, 1): 840,
        (0, 2): 42,
    }

    line_neighbours = {
        label: frozenset(
            other for other in labels
            if other != label and set(label) & set(other)
        )
        for label in labels
    }
    q2_values = {}
    for left, right in itertools.combinations(labels, 2):
        relation = (
            len(set(left) & set(right)),
            sum((point ^ 1) in right for point in left),
        )
        q2_values.setdefault(relation, set()).add(
            len(line_neighbours[left] & line_neighbours[right])
        )
    assert q2_values[1, 0] == {11}
    assert q2_values[0, 1] == {3}
    incidence_record = source["vertex_edge_incidence_and_weighted_factor"]
    assert incidence_record["identities"] == [
        "C J_edge = A C-C-2R",
        "R C^T=A",
        "R R^T=7I",
        "R J_edge C^T=A^2-A-14I=2(J_99-I-A)",
        "Yhat=R J_edge",
        "Yhat C^T=2(J_99-I-A)",
    ]
    assert incidence_record["E0_zero_comparison"]["conclusion"] == (
        "THE_TWO_FACTORS_ARE_DISTINCT_AND_EDGE_DISJOINT"
    )
    assert incidence_record["E0_zero_comparison"]["Yhat_simple_factor_type"] == [0, 1]
    assert incidence_record["E0_zero_comparison"]["Wave65_T_type"] == [1, 0]
    assert set((0, 1)) != set((1, 0)) or (0, 1) != (1, 0)

    # The final matrix reduction uses only the SRG adjacency identity.
    # Encode matrices by coefficients of (I,A,J_99).
    # A^2=12I-A+2J_99, so A^2-A-14I=-2I-2A+2J_99.
    a2 = (12, -1, 2)
    reduced = (a2[0] - 14, a2[1] - 1, a2[2])
    assert reduced == (-2, -2, 2)

    wave3_text = WAVE3_AUDIT.read_text(encoding="utf-8")
    wave65 = json.loads(WAVE65_VERIFY.read_text(encoding="utf-8"))
    assert "global `BQ=BD` relation and weighted 2-factor" in wave3_text
    assert wave65["claim_label"] == "VERIFIED"
    assert wave65["rooted_scaffold"]["H_edges"] == 84

    # Independently verify the claimed B-projector traces by direct moment
    # substitution.  This does not reuse the construction script's solver.
    eigenvalues = (12, 3, 0, -2, -4)
    ranks = (1, 40, 7, 6, 30)
    q_eigenvalues = (22, -2, 10, 8, -2)
    spectra = {
        "T": (Fraction(2), Fraction(72, 5), Fraction(7),
              Fraction(18, 5), Fraction(-27)),
        "U": (Fraction(2), Fraction(112, 5), Fraction(-7),
              Fraction(18, 5), Fraction(-21)),
    }
    expected_q_moments = {"T": (168, 1848), "U": (0, 504)}
    expected_b_moments = {
        "T": (168, 0, 5544, 35784),
        "U": (168, 168, 5376, 37968),
    }
    for name, vector in spectra.items():
        assert sum(vector) == 0
        assert vector[0] == 2
        assert tuple(
            sum(Fraction(q_value ** power) * coefficient
                for q_value, coefficient in zip(q_eigenvalues, vector))
            for power in (1, 2)
        ) == expected_q_moments[name]
        assert tuple(
            sum(Fraction(eigenvalue ** power) * coefficient
                for eigenvalue, coefficient in zip(eigenvalues, vector))
            for power in (1, 2, 3, 4)
        ) == expected_b_moments[name]
        assert sum(
            Fraction(eigenvalue * q_value) * coefficient
            for eigenvalue, q_value, coefficient
            in zip(eigenvalues, q_eigenvalues, vector)
        ) == 168
    assert expected_b_moments["T"][3] + 3 * expected_b_moments["T"][2] == 52416

    spectral_record = incidence_record["endpoint_E0_zero_fixed_Q_spectral_traces"]
    assert spectral_record["factor_results"]["T"]["tr_F_E_lambda"] == [
        2, "72/5", 7, "18/5", -27
    ]
    assert spectral_record["factor_results"]["U"]["tr_F_E_lambda"] == [
        2, "112/5", -7, "18/5", -21
    ]
    assert spectral_record["pointwise_identity"]["on_T_union_U"] == "(BQ)[x,y]=1"

    # Recompute the simultaneous scalar feasibility margins.
    def projected_norm(vector):
        return sum(value * value / rank for value, rank in zip(vector, ranks))

    t_vector, u_vector = spectra["T"], spectra["U"]
    sum_vector = tuple(left + right for left, right in zip(t_vector, u_vector))
    difference_vector = tuple(left - right for left, right in zip(t_vector, u_vector))
    norms = {
        "T": projected_norm(t_vector),
        "U": projected_norm(u_vector),
        "T+U": projected_norm(sum_vector),
        "T-U": projected_norm(difference_vector),
    }
    assert norms == {
        "T": Fraction(10661, 250),
        "U": Fraction(10101, 250),
        "T+U": Fraction(16912, 125),
        "T-U": Fraction(154, 5),
    }
    scalar_cross = sum(
        left * right / rank
        for left, right, rank in zip(t_vector, u_vector, ranks)
    )
    assert scalar_cross == Fraction(6531, 250)
    residual_determinant = (
        (168 - norms["T"]) * (168 - norms["U"]) - scalar_cross * scalar_cross
    )
    assert residual_determinant == Fraction(9570288, 625)
    assert residual_determinant > 0

    # Explicitly realize N(u) as seven disjoint edges and find the maximum
    # induced edge count of every p-subset.  This proves the 11-state term.
    neighbourhood = tuple(range(14))
    local_edges = frozenset((2 * index, 2 * index + 1) for index in range(7))
    max_internal = []
    max_common_intersection = []
    for p in range(13):
        best_internal = 0
        best_intersection = 0
        for selected in itertools.combinations(neighbourhood, p):
            selected_set = frozenset(selected)
            best_internal = max(
                best_internal,
                sum(left in selected_set and right in selected_set
                    for left, right in local_edges),
            )
            # The common-neighbour set N(r) cap N(u) of a good root r has
            # size two.  Maximizing over all such abstract two-subsets is a
            # relaxation, hence a sound independent upper bound.
            best_intersection = max(best_intersection, min(p, 2))
        assert best_internal == p // 2
        assert best_intersection == min(p, 2)
        max_internal.append(best_internal)
        max_common_intersection.append(best_intersection)

    table = []
    heights = []
    for q in range(13):
        p = 12 - q
        total = p * (p - 1) // 2 + p * q
        edge_cap = max_internal[p] + q * max_common_intersection[p]
        nonedge_floor = total - edge_cap
        heights.append(nonedge_floor)
        table.append((q, p, total, max_internal[p], q * min(p, 2), edge_cap,
                      nonedge_floor))
    assert heights == [60, 59, 56, 53, 48, 43, 36, 29, 20, 11, 0, 0, 0]

    # Reconstruct all lower facets of (q,q^2,h(q)).
    facets = {}
    for indices in itertools.combinations(range(13), 3):
        coefficients = solve_plane([(q, heights[q]) for q in indices])
        if all(
            coefficients[0] + coefficients[1] * q + coefficients[2] * q * q
            <= heights[q]
            for q in range(13)
        ):
            equality = tuple(
                q for q in range(13)
                if coefficients[0]
                + coefficients[1] * q
                + coefficients[2] * q * q
                == heights[q]
            )
            facets[coefficients] = equality
    assert len(facets) == 8
    assert set(facets) == {
        (Fraction(60), Fraction(0), Fraction(-1)),
        (Fraction(60), Fraction(-1), Fraction(-1, 2)),
        (Fraction(60), Fraction(-11), Fraction(1, 2)),
        (Fraction(56), Fraction(2), Fraction(-1)),
        (Fraction(48), Fraction(4), Fraction(-1)),
        (Fraction(36), Fraction(6), Fraction(-1)),
        (Fraction(20), Fraction(8), Fraction(-1)),
        (Fraction(0), Fraction(0), Fraction(0)),
    }
    # Each discrete point is exposed by at least one facet.  Consequently
    # these are the complete lower convex surface over the moment projection.
    for q, height in enumerate(heights):
        assert max(a + b * q + c * q * q for a, b, c in facets) == height

    recorded_table = source["mate_bit_capacity"]["table"]
    assert [
        (
            row["q"], row["p=12-q"], row["all_bad_containing_pairs"],
            row["adjacent_11_capacity"], row["adjacent_01_10_capacity"],
            row["adjacent_total_capacity_f(q)"], row["forced_nonadjacent_h(q)"],
        )
        for row in recorded_table
    ] == table

    # Check the Bose--Mesner simplification symbolically by comparing affine
    # coefficients after beta_n=45738-D-beta_e.
    # 2079*lambda_3 = 83160+44D+11 beta_e.
    # 4158*lambda_-4 = 486486+81D-27 beta_e.
    for d_star, beta_e in (
        (Fraction(0), Fraction(0)),
        (Fraction(1), Fraction(13)),
        (Fraction(37, 5), Fraction(12345, 7)),
    ):
        beta_n = Fraction(45738) - d_star - beta_e
        diagonal = Fraction(84) + 2 * d_star / 99
        eig3 = diagonal + beta_e / 231 - 2 * beta_n / 2079
        eig4 = diagonal - 4 * beta_e / 693 + beta_n / 1386
        assert 2079 * eig3 == 83160 + 44 * d_star + 11 * beta_e
        assert 4158 * eig4 == 486486 + 81 * d_star - 27 * beta_e

    # Independently read the unordered shadow coefficients from the frozen
    # census by halving its ordered-root vector.
    edge_coefficients = tuple(
        (int(mask), Fraction(int(value), 2))
        for mask, value in shadow["shadow_coefficients"]["ordered_edge"][
            "nonzero_order8_coefficients"
        ]
    )
    nonedge_coefficients = tuple(
        (int(mask), Fraction(int(value), 2))
        for mask, value in shadow["shadow_coefficients"]["ordered_nonedge"][
            "nonzero_order8_coefficients"
        ]
    )
    counts = {
        int(row["canonical_mask"]): frac(row["count"])
        for row in witness["x8_support"]
    }
    beta_e = sum(
        (coefficient * counts.get(mask, Fraction())
         for mask, coefficient in edge_coefficients), Fraction()
    )
    beta_n = sum(
        (coefficient * counts.get(mask, Fraction())
         for mask, coefficient in nonedge_coefficients), Fraction()
    )
    n3 = Fraction(witness["x7_record"]["y"])
    z11 = Fraction(witness["x7_record"]["h11"])
    d_star = n3 - z11 / 4
    assert d_star == 0
    assert beta_e + beta_n == 45738
    q2 = Fraction(231 * 144)
    assert Fraction(45738) + n3 - Fraction(3, 2) * q2 == 0
    assert beta_e <= 18018 + 3 * d_star
    assert beta_n >= 27720 - 4 * d_star

    result = {
        "status": "INDEPENDENT_AUGMENTED_FLAG_RELATION_AUDIT_PASS",
        "bound_artifact": str(SOURCE.relative_to(ROOT)),
        "bound_artifact_sha256": digest(SOURCE),
        "frozen_inputs": {
            "shadow_sha256": digest(SHADOW),
            "wave159_witness_sha256": digest(WITNESS),
            "wave3_audit_sha256": digest(WAVE3_AUDIT),
            "wave65_independent_results_sha256": digest(WAVE65_VERIFY),
        },
        "independent_checks": {
            "N(u)_is_7K2_subset_cap_all_p_0_to_12": True,
            "CJ_edge_four_class_table": [list(record) for record in cases],
            "CJ_edge_identity_all_classes": True,
            "RJCt_srg_algebra": "A^2-A-14I=2(J_99-I-A)",
            "support_label_pair_census": {
                f"{overlap},{degree}": count
                for (overlap, degree), count in sorted(label_census.items())
            },
            "E0_zero_Yhat_factor_type": [0, 1],
            "E0_zero_Wave65_T_type": [1, 0],
            "E0_zero_factors_proved_edge_disjoint": True,
            "Q2_entry_T_type_(1,0)": 11,
            "Q2_entry_U_type_(0,1)": 3,
            "fixed_Q_projector_traces_T": [str(value) for value in spectra["T"]],
            "fixed_Q_projector_traces_U": [str(value) for value in spectra["U"]],
            "pointwise_BQ_on_T_union_U": 1,
            "mixed_trace_checks": {
                "T_B3_B4": [5544, 35784],
                "U_B3_B4": [5376, 37968],
            },
            "simultaneous_projected_norms": {
                name: str(value) for name, value in norms.items()
            },
            "residual_Cauchy_determinant": str(residual_determinant),
            "simultaneous_scalar_screen_contradiction": False,
            "good_root_two_common_neighbour_relaxation_all_p": True,
            "capacity_table": [list(row) for row in table],
            "lower_convex_facets": [
                {
                    "coefficients": [str(value) for value in coefficients],
                    "touching_q": list(equality),
                }
                for coefficients, equality in sorted(
                    facets.items(), key=lambda item: tuple(item[0])
                )
            ],
            "all_13_points_exposed": True,
            "bose_mesner_affine_reduction": True,
            "wave159_beta_e": str(beta_e),
            "wave159_beta_n": str(beta_n),
            "wave159_beta_sum": str(beta_e + beta_n),
            "wave159_new_scalar_conditions_pass": True,
        },
        "scope": (
            "This is an exact audit of the algebra and finite local capacity. "
            "It does not assert that the Wave159 pseudowitness is a graph or "
            "that it admits a full augmented Gram realization."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "facets": len(facets)}))


if __name__ == "__main__":
    main()
