"""Exact algebra audit for the augmented triangle-flag relation.

Let X be the two-cross-edge unmatched-endpoint relation from
``scratch_theory_root_flag_union.md``.  Add the prism relation Pi, where
(T,t) Pi (U,u) precisely when T and U form a triangular prism and tu is
one of its three matching edges.  Then Xhat=X+Pi is 12-regular.

This script records the resulting fixed-marginal Gram identities, evaluates
their order-eight shadow on the sealed Wave159 rational pseudowitness, and
computes the sharp lower hull (using only sum(q) and sum(q^2)) of the local
nonedge bad-mate capacity table.  It is intentionally standard-library only.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SHADOW = ROOT / "scratch_theory_root_yyt_order8_shadow.json"
WITNESS = (
    ROOT
    / "external_conway99_research/attempts/wave159-four-root-cut-loop/"
    "exact-witness-after-fifteen-cuts.json"
)
OUTPUT = ROOT / "scratch_theory_root_yyt_augmented_relation.json"
WAVE3_AUDIT = (
    ROOT / "external_conway99_research/verification/2026-07-22-wave3-audit.md"
)
WAVE65_VERIFY = (
    ROOT
    / "external_conway99_research/verification/"
    "wave65-rooted-hypergraph-algebra/independent-results.json"
)

EDGE_SHADOW = ((5691760, 1), (127242964, 2), (144594160, 1))
NONEDGE_SHADOW = (
    (15424580, 1),
    (15436356, 1),
    (44489072, 1),
    (110787152, 1),
    (127315016, 1),
    (149654084, 1),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def rational(value: object) -> Fraction:
    if isinstance(value, int):
        return Fraction(value)
    if not isinstance(value, str):
        raise TypeError(value)
    return Fraction(value)


def determinant3(matrix: list[list[Fraction]]) -> Fraction:
    return (
        matrix[0][0]
        * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
        - matrix[0][1]
        * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
        + matrix[0][2]
        * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
    )


def plane_through(indices: tuple[int, int, int], values: list[int]):
    matrix = [[Fraction(1), Fraction(q), Fraction(q * q)] for q in indices]
    determinant = determinant3(matrix)
    assert determinant
    answer = []
    for column in range(3):
        replaced = [row[:] for row in matrix]
        for row, q in enumerate(indices):
            replaced[row][column] = Fraction(values[q])
        answer.append(determinant3(replaced) / determinant)
    return tuple(answer)


def lower_supporting_planes(values: list[int]):
    """All distinct quadratic planes through >=3 table points and below it."""

    result = []
    for indices in itertools.combinations(range(len(values)), 3):
        coefficients = plane_through(indices, values)
        if all(
            coefficients[0] + coefficients[1] * q + coefficients[2] * q * q
            <= values[q]
            for q in range(len(values))
        ):
            equality = tuple(
                q
                for q in range(len(values))
                if coefficients[0]
                + coefficients[1] * q
                + coefficients[2] * q * q
                == values[q]
            )
            record = (equality, coefficients)
            if record not in result:
                result.append(record)
    return tuple(result)


def affine_sum(coefficients: tuple[Fraction, Fraction, Fraction]):
    """Sum over the 3 flags of each of 231 triangles.

    Uses sum_T q(T)=2*n3/3 and Q2=sum_T q(T)^2.  The return value is
    (constant, coefficient of n3, coefficient of Q2).
    """

    alpha, beta, gamma = coefficients
    return 3 * 231 * alpha, 2 * beta, 3 * gamma


def display_fraction(value: Fraction):
    return int(value) if value.denominator == 1 else str(value)


def solve_linear_system(matrix, right_hand_side):
    """Exact square Gaussian elimination over Fraction."""

    augmented = [
        [Fraction(value) for value in row] + [Fraction(value)]
        for row, value in zip(matrix, right_hand_side)
    ]
    order = len(augmented)
    assert all(len(row) == order + 1 for row in augmented)
    for column in range(order):
        pivot = next(row for row in range(column, order) if augmented[row][column])
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        scale = augmented[column][column]
        augmented[column] = [value / scale for value in augmented[column]]
        for row in range(order):
            if row == column:
                continue
            scale = augmented[row][column]
            augmented[row] = [
                value - scale * base
                for value, base in zip(augmented[row], augmented[column])
            ]
    return tuple(augmented[row][-1] for row in range(order))


def main() -> None:
    shadow = json.loads(SHADOW.read_text(encoding="utf-8"))
    witness = json.loads(WITNESS.read_text(encoding="utf-8"))
    wave3_text = WAVE3_AUDIT.read_text(encoding="utf-8")
    wave65 = json.loads(WAVE65_VERIFY.read_text(encoding="utf-8"))
    assert "global `BQ=BD` relation and weighted 2-factor" in wave3_text
    assert wave65["claim_label"] == "VERIFIED"
    assert wave65["rooted_scaffold"]["identity"] == "B^2+B=10I+2J-Q"

    # Bind the coefficient vectors independently found in the shadow census.
    observed_edge = tuple(
        (int(mask), int(value))
        for mask, value in shadow["shadow_coefficients"]["ordered_edge"][
            "nonzero_order8_coefficients"
        ]
    )
    observed_nonedge = tuple(
        (int(mask), int(value))
        for mask, value in shadow["shadow_coefficients"]["ordered_nonedge"][
            "nonzero_order8_coefficients"
        ]
    )
    # The frozen census stores ordered source-root pairs, whereas beta_e and
    # beta_n below are unordered off-diagonal Gram sums.
    assert observed_edge == tuple((mask, 2 * value) for mask, value in EDGE_SHADOW)
    assert observed_nonedge == tuple(
        (mask, 2 * value) for mask, value in NONEDGE_SHADOW
    )

    # For one target flag beta=(U,u), q=q(U) X-neighbours are good (mate
    # bit zero) and p=12-q prism neighbours are bad (mate bit one).
    # There are C(p,2)+pq bad-containing pairs.  Adjacent bad-bad roots
    # occupy a subset of N(u)=7K2, hence at most floor(p/2) edges.  Every
    # good root is nonadjacent to u and has exactly two neighbours in N(u),
    # hence contributes at most min(p,2), counted with flag multiplicity.
    capacity_table = []
    h_values = []
    for q in range(13):
        p = 12 - q
        correction = p * (p - 1) // 2 + p * q
        edge_capacity_11 = p // 2
        edge_capacity_01_10 = q * min(p, 2)
        edge_capacity = edge_capacity_11 + edge_capacity_01_10
        forced_nonedge = correction - edge_capacity
        assert correction == 66 - q * (q - 1) // 2
        assert forced_nonedge >= 0
        h_values.append(forced_nonedge)
        capacity_table.append(
            {
                "q": q,
                "p=12-q": p,
                "all_bad_containing_pairs": correction,
                "adjacent_11_capacity": edge_capacity_11,
                "adjacent_01_10_capacity": edge_capacity_01_10,
                "adjacent_total_capacity_f(q)": edge_capacity,
                "forced_nonadjacent_h(q)": forced_nonedge,
            }
        )

    planes = lower_supporting_planes(h_values)
    assert len(planes) == 8
    moment_bounds = []
    for equality, coefficients in planes:
        summed = affine_sum(coefficients)
        moment_bounds.append(
            {
                "touching_q_values": list(equality),
                "pointwise_plane_alpha_beta_gamma": [
                    display_fraction(value) for value in coefficients
                ],
                "bound_on_Rn_constant_n3_Q2": [
                    display_fraction(value) for value in summed
                ],
                "meaning": (
                    "Rn >= constant + n3_coefficient*n3 + "
                    "Q2_coefficient*Q2"
                ),
            }
        )

    expected_planes = {
        (Fraction(60), Fraction(0), Fraction(-1)),
        (Fraction(60), Fraction(-1), Fraction(-1, 2)),
        (Fraction(60), Fraction(-11), Fraction(1, 2)),
        (Fraction(56), Fraction(2), Fraction(-1)),
        (Fraction(48), Fraction(4), Fraction(-1)),
        (Fraction(36), Fraction(6), Fraction(-1)),
        (Fraction(20), Fraction(8), Fraction(-1)),
        (Fraction(0), Fraction(0), Fraction(0)),
    }
    assert {coefficients for _, coefficients in planes} == expected_planes

    # Exact Wave159 endpoint check.  This is only an evaluation of the
    # necessary linear identities on a pseudowitness, not a graph claim.
    counts8 = {
        int(record["canonical_mask"]): rational(record["count"])
        for record in witness["x8_support"]
    }
    beta_e = sum(
        (multiplicity * counts8.get(mask, Fraction())
         for mask, multiplicity in EDGE_SHADOW),
        Fraction(),
    )
    beta_n = sum(
        (multiplicity * counts8.get(mask, Fraction())
         for mask, multiplicity in NONEDGE_SHADOW),
        Fraction(),
    )
    n3 = Fraction(witness["x7_record"]["y"])
    z11 = Fraction(witness["x7_record"]["h11"])
    d_star = n3 - z11 / 4
    assert n3 == 4158 and d_star == 0
    assert beta_e + beta_n == 45738 - d_star

    # At n3=4158, nonnegative a3(T) and sum a3(T)=2P=0 force q(T)=12
    # for all 231 triangles.
    q2 = Fraction(231 * 12 * 12)
    correction_total = Fraction(45738) + n3 - Fraction(3, 2) * q2
    assert correction_total == 0

    # Bose--Mesner projection of G=Yhat Yhat^T.  Its diagonal average is
    # 84+2D*/99; edge/nonedge averages are beta_e/693,beta_n/4158.
    d = Fraction(84) + 2 * d_star / 99
    e = beta_e / 693
    f = beta_n / 4158
    eigenvalue_3 = d + 3 * e - 4 * f
    eigenvalue_minus4 = d - 4 * e + 3 * f
    assert eigenvalue_3 >= 0 and eigenvalue_minus4 >= 0
    assert beta_e <= 18018 + 3 * d_star
    assert beta_n >= 27720 - 4 * d_star

    # Vertex-edge incidence classification behind C J_edge=A C-C-2R.
    # For a fixed graph edge e, every vertex is an endpoint, its unique
    # triangle mate, adjacent to exactly one endpoint, or adjacent to neither.
    # The counts follow from k=14 and lambda=1.
    incidence_cases = [
        {
            "class": "endpoint_of_e",
            "multiplicity_for_fixed_e": 2,
            "(AC)_ve": 1,
            "C_ve": 1,
            "R_ve": 0,
            "(CJ_edge)_ve": 0,
        },
        {
            "class": "unique_triangle_mate_of_e",
            "multiplicity_for_fixed_e": 1,
            "(AC)_ve": 2,
            "C_ve": 0,
            "R_ve": 1,
            "(CJ_edge)_ve": 0,
        },
        {
            "class": "outside_adjacent_to_exactly_one_endpoint",
            "multiplicity_for_fixed_e": 24,
            "(AC)_ve": 1,
            "C_ve": 0,
            "R_ve": 0,
            "(CJ_edge)_ve": 1,
        },
        {
            "class": "outside_adjacent_to_neither_endpoint",
            "multiplicity_for_fixed_e": 72,
            "(AC)_ve": 0,
            "C_ve": 0,
            "R_ve": 0,
            "(CJ_edge)_ve": 0,
        },
    ]
    assert sum(case["multiplicity_for_fixed_e"] for case in incidence_cases) == 99
    for case in incidence_cases:
        assert (
            case["(AC)_ve"] - case["C_ve"] - 2 * case["R_ve"]
            == case["(CJ_edge)_ve"]
        )
    assert sum(
        case["multiplicity_for_fixed_e"] * case["(CJ_edge)_ve"]
        for case in incidence_cases
    ) == 24  # two endpoints on each of the twelve J_edge-neighbour edges

    # The five support-label pair types can be reconstructed without a graph.
    # Base points 0,...,13 have mate x^1; residual labels are nonmate pairs.
    base_points = tuple(range(14))
    labels = tuple(
        pair for pair in itertools.combinations(base_points, 2)
        if pair[1] != (pair[0] ^ 1)
    )
    assert len(labels) == 84
    support_pair_census: dict[tuple[int, int], int] = {}
    for left, right in itertools.combinations(labels, 2):
        q_overlap = len(set(left) & set(right))
        mate_crossings = sum((point ^ 1) in right for point in left)
        key = (q_overlap, mate_crossings)
        support_pair_census[key] = support_pair_census.get(key, 0) + 1
    assert support_pair_census == {
        (1, 0): 840,
        (1, 1): 84,
        (0, 0): 1680,
        (0, 1): 840,
        (0, 2): 42,
    }

    # Q is the line graph of H=K14-7K2.  Reconstruct Q^2 entry values on
    # the two E0=0 factor relations without using the claimed numbers.
    label_neighbours = {
        label: frozenset(
            other for other in labels
            if other != label and set(label) & set(other)
        )
        for label in labels
    }
    q2_by_relation: dict[tuple[int, int], set[int]] = {}
    for left, right in itertools.combinations(labels, 2):
        overlap = len(set(left) & set(right))
        mate_degree = sum((point ^ 1) in right for point in left)
        q2_entry = len(label_neighbours[left] & label_neighbours[right])
        q2_by_relation.setdefault((overlap, mate_degree), set()).add(q2_entry)
    assert q2_by_relation[(1, 0)] == {11}
    assert q2_by_relation[(0, 1)] == {3}

    # Solve for a_lambda(F)=tr(F E_lambda(B)) for F=T and F=U.  The five
    # equations are tr(F)=0, a_12=2, tr(FB)=168, and the fixed Q,Q^2 edge
    # traces.  Q acts by 22,10,8,-2,-2 on B eigenspaces
    # lambda=12,0,-2,3,-4 respectively.
    eigenvalues = (12, 3, 0, -2, -4)
    ranks = (1, 40, 7, 6, 30)
    q_eigenvalues = (22, -2, 10, 8, -2)
    system = (
        (1, 1, 1, 1, 1),
        (1, 0, 0, 0, 0),
        eigenvalues,
        q_eigenvalues,
        tuple(value * value for value in q_eigenvalues),
    )
    factor_inputs = {
        "T": {"relation": (1, 0), "tr_FQ": 168, "tr_FQ2": 1848},
        "U": {"relation": (0, 1), "tr_FQ": 0, "tr_FQ2": 504},
    }
    factor_spectra = {}
    expected_spectra = {
        "T": (Fraction(2), Fraction(72, 5), Fraction(7), Fraction(18, 5), Fraction(-27)),
        "U": (Fraction(2), Fraction(112, 5), Fraction(-7), Fraction(18, 5), Fraction(-21)),
    }
    for name, data in factor_inputs.items():
        solution = solve_linear_system(
            system,
            (0, 2, 168, data["tr_FQ"], data["tr_FQ2"]),
        )
        assert solution == expected_spectra[name]
        tr_bq = sum(
            eigenvalue * q_value * coefficient
            for eigenvalue, q_value, coefficient
            in zip(eigenvalues, q_eigenvalues, solution)
        )
        assert tr_bq == 168
        mixed_traces = {
            power: sum(
                Fraction(eigenvalue ** power) * coefficient
                for eigenvalue, coefficient in zip(eigenvalues, solution)
            )
            for power in range(1, 5)
        }
        factor_spectra[name] = {
            "relation_(Q,d)": list(data["relation"]),
            "Q2_entry_on_each_factor_edge": next(iter(q2_by_relation[data["relation"]])),
            "tr_FQ": data["tr_FQ"],
            "tr_FQ2": data["tr_FQ2"],
            "tr_FBQ_from_pointwise_identity": display_fraction(tr_bq),
            "spectral_projector_order": list(eigenvalues),
            "tr_F_E_lambda": [display_fraction(value) for value in solution],
            "tr_B_power_F": {
                str(power): display_fraction(value)
                for power, value in mixed_traces.items()
            },
        }
    assert factor_spectra["T"]["tr_B_power_F"]["3"] == 5544
    assert factor_spectra["T"]["tr_B_power_F"]["4"] == 35784
    assert factor_spectra["U"]["tr_B_power_F"]["3"] == 5376
    assert factor_spectra["U"]["tr_B_power_F"]["4"] == 37968
    assert 35784 + 3 * 5544 == 52416

    # Elementary simultaneous PSD/Cauchy screen.  It is only a necessary
    # scalar screen and deliberately records the substantial slack.
    t_spectrum = expected_spectra["T"]
    u_spectrum = expected_spectra["U"]
    sum_spectrum = tuple(left + right for left, right in zip(t_spectrum, u_spectrum))
    difference_spectrum = tuple(
        left - right for left, right in zip(t_spectrum, u_spectrum)
    )
    assert all(abs(value) <= 2 * rank for value, rank in zip(t_spectrum, ranks))
    assert all(abs(value) <= 2 * rank for value, rank in zip(u_spectrum, ranks))
    assert all(abs(value) <= 4 * rank for value, rank in zip(sum_spectrum, ranks))
    assert all(abs(value) <= 4 * rank for value, rank in zip(difference_spectrum, ranks))

    def scalar_projection_norm(vector):
        return sum(value * value / rank for value, rank in zip(vector, ranks))

    projection_norms = {
        "T": scalar_projection_norm(t_spectrum),
        "U": scalar_projection_norm(u_spectrum),
        "T+U": scalar_projection_norm(sum_spectrum),
        "T-U": scalar_projection_norm(difference_spectrum),
    }
    assert projection_norms["T"] <= 168
    assert projection_norms["U"] <= 168
    # Edge-disjoint 2-factors have tr(TU)=0 and hence both squared norms 336.
    assert projection_norms["T+U"] <= 336
    assert projection_norms["T-U"] <= 336
    scalar_inner_product = sum(
        left * right / rank
        for left, right, rank in zip(t_spectrum, u_spectrum, ranks)
    )
    residual_t = Fraction(168) - projection_norms["T"]
    residual_u = Fraction(168) - projection_norms["U"]
    assert scalar_inner_product * scalar_inner_product <= residual_t * residual_u

    result = {
        "status": "AUGMENTED_FLAG_RELATION_AND_BAD_MATE_CAPACITY_PASS",
        "frozen_inputs": {
            "order8_shadow": str(SHADOW.relative_to(ROOT)),
            "order8_shadow_sha256": sha256(SHADOW),
            "wave159_exact_witness": str(WITNESS.relative_to(ROOT)),
            "wave159_exact_witness_sha256": sha256(WITNESS),
            "wave3_audit": str(WAVE3_AUDIT.relative_to(ROOT)),
            "wave3_audit_sha256": sha256(WAVE3_AUDIT),
            "wave65_independent_results": str(WAVE65_VERIFY.relative_to(ROOT)),
            "wave65_independent_results_sha256": sha256(WAVE65_VERIFY),
        },
        "definitions": {
            "Pi": (
                "Pi[(T,t),(U,u)]=1 iff T,U form a triangular prism and "
                "tu is the corresponding perfect-matching edge"
            ),
            "Xhat": "X+Pi",
            "Yhat": "F^T Xhat",
            "G": "Yhat Yhat^T",
            "beta_e_beta_n": (
                "unordered adjacent/nonadjacent off-diagonal sums of G; "
                "equivalently the order-eight shadow functionals"
            ),
            "Re_Rn": (
                "parts of beta_e,beta_n whose unique target-edge mate "
                "is adjacent to at least one source root"
            ),
        },
        "graph_level_identities": {
            "Xhat_flag_degree": 12,
            "Yhat_row_sum": 84,
            "Yhat_column_sum": 12,
            "Yhat_entry_values": [0, 1, 2],
            "Yhat_value_two_characterization": (
                "Yhat[r,beta]=2 iff the old X-collapse Y[r,beta]=2; "
                "these are exactly the D(r) diagonal events"
            ),
            "G_diagonal": "G[r,r]=84+2D(r)",
            "trace_G": "8316+2D_*",
            "one_G_one": 99792,
            "beta_sum": "beta_e+beta_n=45738-D_*",
            "old_offdiagonal_sum": "a+b=(3Q2-2(n3+D_*))/2",
            "bad_mate_total": "Re+Rn=45738+n3-3Q2/2",
            "component_relation": "a=beta_e-Re; b=beta_n-Rn",
        },
        "bose_mesner_projection_of_G": {
            "nontrivial_eigenvalue_conditions": [
                "84+2D_*/99+3beta_e/693-4beta_n/4158 >= 0",
                "84+2D_*/99-4beta_e/693+3beta_n/4158 >= 0",
            ],
            "equivalent_nontrivial_bounds": [
                "beta_e >= -7560-4D_*",
                "beta_e <= 18018+3D_*",
                "beta_n >= 27720-4D_*",
                "beta_n <= 53298+3D_*",
            ],
            "useful_sides": [
                "beta_e <= 18018+3D_*",
                "beta_n >= 27720-4D_*",
            ],
            "four_root_raw_moment_form": [
                "M12[17724,29988] <= 72072+12D_*",
                "sum_(i in L,j in R) M1[i,j] >= 110880-16D_*",
            ],
        },
        "vertex_edge_incidence_and_weighted_factor": {
            "edge_column_identification": (
                "Identify flag (T,t) with the graph edge e=T\\{t}.  Then "
                "F^T is the triangle-mate incidence R and Xhat is the "
                "opposite-edge adjacency J_edge."
            ),
            "matrices": {
                "C": "99x693 ordinary vertex-edge incidence",
                "R": "99x693; R[v,e]=1 iff v is the unique triangle mate of e",
                "J_edge": (
                    "693x693; two disjoint edges are adjacent iff their four "
                    "cross incidences form a perfect matching"
                ),
                "J_99": "99x99 all-ones matrix",
            },
            "entrywise_case_table_for_CJ_edge": incidence_cases,
            "identities": [
                "C J_edge = A C-C-2R",
                "R C^T=A",
                "R R^T=7I",
                "R J_edge C^T=A^2-A-14I=2(J_99-I-A)",
                "Yhat=R J_edge",
                "Yhat C^T=2(J_99-I-A)",
            ],
            "weighted_two_factor": (
                "For each root r, the nonzero entries of row Yhat[r,*] are "
                "edges entirely inside the 84 nonneighbours of r, and their "
                "integer weights give weighted degree exactly 2 at every "
                "one of those 84 vertices.  Weight two occurs exactly on "
                "the D(r) fibre-diagonal edges."
            ),
            "support_label_relation": {
                "definition": (
                    "For residual support labels L(p),L(q), let d_r(p,q) be "
                    "the number of x in L(p) whose root-neighbour mate lies "
                    "in L(q).  On a residual graph edge pq, "
                    "Yhat[r,pq]=d_r(p,q)."
                ),
                "ambient_unordered_pair_census_by_(overlap,d_r)": {
                    f"{overlap},{degree}": count
                    for (overlap, degree), count in sorted(support_pair_census.items())
                },
            },
            "E0_zero_comparison": {
                "conclusion": "THE_TWO_FACTORS_ARE_DISTINCT_AND_EDGE_DISJOINT",
                "reason": (
                    "E0(r)=0 forces both S(r)=0 and D(r)=0.  Hence the Yhat "
                    "factor is the 84 selected residual edges of type "
                    "(support overlap,d_r)=(0,1).  Wave65's transition factor "
                    "T consists of the 84 selected exact-symbol-sharing edges, "
                    "which now have type (1,0)."
                ),
                "Yhat_simple_factor_type": [0, 1],
                "Wave65_T_type": [1, 0],
                "Yhat_factor_edges": 84,
                "Wave65_T_edges": 84,
                "containment": (
                    "The Yhat factor is a spanning simple 2-factor inside "
                    "Wave65's 10-regular disjoint-label point graph D, not T. "
                    "It is exactly the selected d_r=1 factor already appearing "
                    "in the independently verified Wave3 weighted-factor lane."
                ),
            },
            "endpoint_E0_zero_fixed_Q_spectral_traces": {
                "premises": [
                    "Q=10I+2J-B^2-B",
                    "spec(B)=12^1,3^40,0^7,(-2)^6,(-4)^30",
                    "Q eigenvalues on those spaces are 22,-2,10,8,-2",
                    "T and U are edge-disjoint simple spanning 2-factors",
                ],
                "line_graph_Q2_relation_values": {
                    "T_type_(1,0)": 11,
                    "U_type_(0,1)": 3,
                },
                "pointwise_identity": {
                    "general_selected_edge_formula": (
                        "For a selected outside edge xy, the two endpoint-"
                        "profile equations give (BQ)[x,y]=2-Q[x,y]-d_r(x,y)."
                    ),
                    "on_T_union_U": "(BQ)[x,y]=1",
                    "trace_TBQ": 168,
                    "trace_UBQ": 168,
                },
                "factor_results": factor_spectra,
                "comparison_with_Wave65": {
                    "Wave65_w=tr(T E_3)_now_fixed": "72/5",
                    "Wave65_prior_interval": wave65["scalar_coupling"]["w_interval"],
                    "Wave65_prior_tr_B3T_interval": wave65["scalar_coupling"][
                        "tr_B3T_interval"
                    ],
                    "new_tr_B3T": 5544,
                    "new_tr_B4T": 35784,
                    "Wave65_identity_checked": "35784+3*5544=52416",
                },
                "simultaneous_scalar_screen": {
                    "operator_trace_bounds_T_and_U": "all pass |tr(FE_lambda)|<=2 rank(E_lambda)",
                    "operator_trace_bounds_T_plus_minus_U": (
                        "all pass |tr((T+/-U)E_lambda)|<=4 rank(E_lambda)"
                    ),
                    "projected_Frobenius_lower_bounds": {
                        name: display_fraction(value)
                        for name, value in projection_norms.items()
                    },
                    "available_Frobenius_norms": {
                        "T": 168,
                        "U": 168,
                        "T+U": 336,
                        "T-U": 336,
                    },
                    "scalar_projection_inner_product": display_fraction(
                        scalar_inner_product
                    ),
                    "residual_Cauchy_slack_determinant": display_fraction(
                        residual_t * residual_u
                        - scalar_inner_product * scalar_inner_product
                    ),
                    "integrality_check": (
                        "tr(B^j F), tr(FQ), tr(FQ^2), and tr(FBQ) are all "
                        "integers; rational fifths occur only in projector traces"
                    ),
                    "conclusion": (
                        "NO_CONTRADICTION_FROM_THE_RECORDED_PSD_CAUCHY_"
                        "OR_INTEGRALITY_TESTS"
                    ),
                },
            },
        },
        "mate_bit_capacity": {
            "states": ["00 (good-good)", "01", "10", "11"],
            "explanation": (
                "For one target flag, p=12-q bad roots form a subset of "
                "N(u)=7K2, giving at most floor(p/2) adjacent 11 pairs. "
                "Each good root has exactly two neighbours in N(u), giving "
                "at most q*min(p,2) adjacent 01/10 flag pairs."
            ),
            "table": capacity_table,
            "exact_total": "Re+Rn=3 sum_T [66-binomial(q(T),2)]",
            "pointwise_Rn_bound": "Rn >= 3 sum_T h(q(T))",
            "sharp_sumq_Q2_lower_hull": moment_bounds,
            "scope": (
                "The eight displayed planes are all quadratic supporting "
                "planes through at least three of the 13 points "
                "(q,q^2,h(q)); their maximum is the sharp lower convex "
                "surface available from only sum(q) and sum(q^2)."
            ),
        },
        "wave159_boundary_evaluation": {
            "n3": display_fraction(n3),
            "z11": display_fraction(z11),
            "D_star": display_fraction(d_star),
            "Q2_forced_at_endpoint": display_fraction(q2),
            "beta_e": str(beta_e),
            "beta_e_decimal": float(beta_e),
            "beta_n": str(beta_n),
            "beta_n_decimal": float(beta_n),
            "beta_sum": display_fraction(beta_e + beta_n),
            "Re_plus_Rn": display_fraction(correction_total),
            "projected_eigenvalue_3": str(eigenvalue_3),
            "projected_eigenvalue_minus4": str(eigenvalue_minus4),
            "all_new_scalar_inequalities_pass": True,
            "interpretation": (
                "The exact rational pseudowitness has q=12 everywhere, so "
                "there are no prism/bad mates.  It obeys the augmented "
                "shadow identity and both projected PSD bounds while still "
                "having sum E0=0.  These scalar inequalities alone cannot "
                "yield a positive E0 lower bound."
            ),
        },
        "limitations": [
            "No existence of the augmented Gram for the rational pseudowitness is asserted.",
            "The capacity inequalities are necessary graph-level conditions, not sufficiency.",
            "They do not constrain D_* independently of the existing first moments.",
            "No srg(99,14,1,2), positive E0 bound, or Conway-problem resolution is claimed.",
        ],
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": result["status"],
                "supporting_planes": len(planes),
                "beta_sum": display_fraction(beta_e + beta_n),
                "wave159_pass": True,
            },
            separators=(",", ":"),
        )
    )


if __name__ == "__main__":
    main()
