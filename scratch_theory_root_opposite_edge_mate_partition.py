"""Exact arithmetic certificate for the triangle-mate partition of J_E.

This is a theorem/arithmetic companion, not an existence search.  It records
the consequences of partitioning the 693 vertices of the opposite-edge graph
by the unique third vertex of their graph triangle.  All spectral calculations
are over :class:`fractions.Fraction` and use only the SRG Bose--Mesner data.
"""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "scratch_theory_root_opposite_edge_mate_partition.json"
INPUTS = {
    "wave6_opposite_edge": ROOT / (
        "external_conway99_research/agents/"
        "2026-07-22-wave6-opposite-edge-graph.md"
    ),
    "wave20_opposite_edge_compression": ROOT / (
        "external_conway99_research/attempts/"
        "wave20-global-obstruction/failed-routes.md"
    ),
    "wave35_endpoint_spectral": ROOT / (
        "external_conway99_research/agents/"
        "2026-07-26-wave35-n3-upper-spectral.md"
    ),
    "wave65_independent_results": ROOT / (
        "external_conway99_research/verification/"
        "wave65-rooted-hypergraph-algebra/independent-results.json"
    ),
    "augmented_flag_relation": ROOT /
        "scratch_theory_root_yyt_augmented_relation.json",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def show(value: Fraction | int) -> int | str:
    value = Fraction(value)
    return int(value) if value.denominator == 1 else str(value)


def bm_multiply(x: tuple[Fraction, Fraction, Fraction],
                y: tuple[Fraction, Fraction, Fraction]
                ) -> tuple[Fraction, Fraction, Fraction]:
    """Multiply coefficients of I,A,One using A^2=12I-A+2One.

    The other rules are A*One=14One and One^2=99One.
    """

    xi, xa, xj = x
    yi, ya, yj = y
    return (
        xi * yi + 12 * xa * ya,
        xi * ya + xa * yi - xa * ya,
        xi * yj + xj * yi + 2 * xa * ya
        + 14 * (xa * yj + xj * ya) + 99 * xj * yj,
    )


def bm_eigenvalues(x: tuple[Fraction, Fraction, Fraction]):
    """Eigenvalues on the A-eigenspaces 14,3,-4."""

    xi, xa, xj = x
    return (
        xi + 14 * xa + 99 * xj,
        xi + 3 * xa,
        xi - 4 * xa,
    )


def main() -> None:
    for path in INPUTS.values():
        assert path.is_file(), path

    # Basic parameters and the complement adjacency K=One-I-A.
    n, degree, edge_count = 99, 14, 693
    cell_count, cell_size = 99, 7
    j_degree, j_edge_count = 12, 4158
    multiplicities = (1, 54, 44)
    a_spectrum = (14, 3, -4)
    ident = (Fraction(1), Fraction(0), Fraction(0))
    adjacency = (Fraction(0), Fraction(1), Fraction(0))
    ones = (Fraction(0), Fraction(0), Fraction(1))
    complement = tuple(ones[i] - ident[i] - adjacency[i] for i in range(3))
    incidence_gram = tuple(
        14 * ident[i] + adjacency[i] for i in range(3)
    )
    assert bm_eigenvalues(complement) == (84, -4, 3)
    assert bm_eigenvalues(incidence_gram) == (28, 17, 10)
    assert edge_count == cell_count * cell_size
    assert j_edge_count == edge_count * j_degree // 2
    assert sum(multiplicities) == n

    # The old ordinary-incidence compression (Wave20), included to make the
    # distinction between C and the new triangle-mate incidence R explicit.
    cjc = (-2, 10, 2)  # C J_E C^T
    old_ritz = tuple(
        value / gram
        for value, gram in zip(
            bm_eigenvalues(cjc), bm_eigenvalues(incidence_gram)
        )
    )
    assert old_ritz == (Fraction(12), Fraction(28, 17), Fraction(-21, 5))

    # The two exact mixed-incidence identities.
    # C J_E R^T = 2K and hence R J_E C^T=2K.
    mixed = tuple(2 * value for value in complement)
    assert bm_eigenvalues(mixed) == (168, -8, 6)

    # Quotient notation:
    #   Z=R J_E R^T,
    #   G=R J_E^2 R^T=(R J_E)(R J_E)^T.
    # P=R^T/sqrt(7) is isometric, so the compression is Z/7 and
    # 7G-Z^2 is the Gram of the component perpendicular to im(P).
    trace_g_constant = cell_count * cell_size * j_degree
    assert trace_g_constant == 8316
    defect_trace_constant = 7 * trace_g_constant
    assert defect_trace_constant == 58212

    # At P=0 all 4,158 J_E edges project to nonedges of the root graph.
    # K has exactly 4,158 unordered support positions and row sum 84.
    complement_edges = n * 84 // 2
    assert complement_edges == j_edge_count
    trace_k_squared = sum(
        multiplicity * value * value
        for multiplicity, value in zip(multiplicities,
                                       bm_eigenvalues(complement))
    )
    assert trace_k_squared == 8316

    # Write Z=K+W.  Because Z and K have the same row sum and total support
    # weight, W has zero row sum and is Frobenius-orthogonal to I,A,One.
    # Thus tr(Z^2)=8316+||W||_F^2.  Combining with 7G-Z^2 >= 0 gives
    # ||W||^2 <= 49896+14D_*.
    basic_w_constant = defect_trace_constant - trace_k_squared
    assert basic_w_constant == 49896

    # First Bessel projection: project Y=J_E R^T onto im(C^T).
    # Its forced Gram is 4 K (14I+A)^(-1) K.
    k_eigen = bm_eigenvalues(complement)
    s_eigen = bm_eigenvalues(incidence_gram)
    first_projection_eigen = tuple(
        Fraction(4 * value * value, denominator)
        for value, denominator in zip(k_eigen, s_eigen)
    )
    assert first_projection_eigen == (
        Fraction(1008), Fraction(64, 17), Fraction(18, 5)
    )
    first_projection_trace = sum(
        multiplicity * value
        for multiplicity, value in zip(multiplicities, first_projection_eigen)
    )
    assert first_projection_trace == Fraction(116424, 85)

    # Orthogonalize the mate incidence against C:
    # U=(I-C^T S^-1 C)R^T, H=U^T U=7I-A S^-1 A.
    h_eigen = tuple(
        Fraction(7) - Fraction(theta * theta, denominator)
        for theta, denominator in zip(a_spectrum, s_eigen)
    )
    assert h_eigen == (Fraction(0), Fraction(110, 17), Fraction(27, 5))
    h_plus_eigen = tuple(
        Fraction(0) if value == 0 else Fraction(1, value)
        for value in h_eigen
    )
    assert h_plus_eigen == (Fraction(0), Fraction(17, 110), Fraction(5, 27))

    # U^T Y=Z-T0, T0=2 A S^-1 K.  At the endpoint Z=K+W.
    t0_eigen = tuple(
        Fraction(2 * theta * kval, denominator)
        for theta, kval, denominator in zip(a_spectrum, k_eigen, s_eigen)
    )
    v_eigen = tuple(
        kval - tval for kval, tval in zip(k_eigen, t0_eigen)
    )
    assert t0_eigen == (Fraction(84), Fraction(-24, 17), Fraction(-12, 5))
    assert v_eigen == (Fraction(0), Fraction(-44, 17), Fraction(27, 5))
    second_fixed_eigen = tuple(
        value * value * inverse
        for value, inverse in zip(v_eigen, h_plus_eigen)
    )
    assert second_fixed_eigen == (
        Fraction(0), Fraction(968, 935), Fraction(27, 5)
    )
    second_fixed_trace = sum(
        multiplicity * value
        for multiplicity, value in zip(multiplicities, second_fixed_eigen)
    )
    assert second_fixed_trace == Fraction(24948, 85)

    # Since W is orthogonal to every Bose--Mesner matrix, the cross term
    # vanishes in trace.  On 1^perp, H^+ >= 17/110 I.  Therefore
    # (17/110)||W||^2 <= tr(G)-the two fixed projection traces.
    schur_slack_constant = (
        Fraction(trace_g_constant)
        - first_projection_trace
        - second_fixed_trace
    )
    assert schur_slack_constant == Fraction(33264, 5)
    schur_w_constant = Fraction(110, 17) * schur_slack_constant
    schur_w_d_coefficient = Fraction(220, 17)
    assert schur_w_constant == Fraction(731808, 17)
    # At D_*=0, ||W||^2 is even (symmetric and hollow), so the rational
    # upper bound floors to the largest even integer below it.
    endpoint_even_upper = 2 * (schur_w_constant.numerator //
                               schur_w_constant.denominator // 2)
    assert endpoint_even_upper == 43046

    # Distance-two packing bound.  If P=0, J_E is triangle-free and
    # L=J_E^2-12I is a nonnegative weighted graph of degree 132.  Its least
    # eigenvalue is at least -12.  Hoffman therefore gives alpha(L)<=231/4;
    # a seven-set is very far below this.  Closed radius-one balls give the
    # still weaker 7*(1+12)=91<=693.
    l_degree = j_degree * j_degree - j_degree
    hoffman_alpha_upper = Fraction(edge_count * j_degree,
                                    l_degree + j_degree)
    assert l_degree == 132
    assert hoffman_alpha_upper == Fraction(231, 4)
    sphere_vertices = cell_size * (1 + j_degree)
    assert sphere_vertices == 91 <= edge_count

    result = {
        "status": "TRIANGLE_MATE_PARTITION_BOUNDARY_PASS",
        "scope": (
            "necessary consequences conditional on a putative "
            "srg(99,14,1,2); no construction or nonexistence claim"
        ),
        "input_sha256": {name: digest(path) for name, path in INPUTS.items()},
        "partition": {
            "opposite_edge_graph_vertices": edge_count,
            "cells": cell_count,
            "cell_size": cell_size,
            "cell_definition": (
                "R_r is the seven graph edges whose unique triangle mate is r"
            ),
            "independent_in_J_edge": True,
            "local_multiplicity": "k_r(v)=|(N_J_edge(v)) intersect R_r|",
            "D_r_identity": "D(r)=sum_v binom(k_r(v),2)",
            "distance_two_equivalence": (
                "D(r)=0 iff R_r is a distance-at-least-three packing in J_edge"
            ),
            "global_endpoint": (
                "D_*=0 iff all 99 cells are distance-at-least-three packings"
            ),
        },
        "incidence_identities": [
            "C C^T=14I+A",
            "R R^T=7I",
            "C R^T=R C^T=A",
            "C J_edge=A C-C-2R",
            "C J_edge R^T=R J_edge C^T=2(One-I-A)",
        ],
        "quotient_and_gram": {
            "definitions": [
                "Z=R J_edge R^T",
                "G=R J_edge^2 R^T=(R J_edge)(R J_edge)^T",
                "P=R^T/sqrt(7)",
            ],
            "always": [
                "Z=Z^T, diag(Z)=0, Z*1=84*1",
                "G is PSD, G*1=1008*1",
                "diag(G)_r=84+2D(r)",
                "tr(G)=8316+2D_*",
                "7G-Z^2 is PSD",
                "tr(Z^2)<=58212+14D_*",
            ],
            "prism_free_endpoint": [
                "J_edge is triangle-free",
                "Z is supported on K=One-I-A",
                "sum_{r<s} Z_rs=4158=sum_{r<s} K_rs",
                "W=Z-K has W*1=0 and is Frobenius-orthogonal to I,A,One",
                "tr(Z^2)=8316+||W||_F^2",
            ],
            "basic_variance_bound": "||W||_F^2<=49896+14D_*",
        },
        "incidence_schur_refinement": {
            "first_projection_eigenvalues_on_A_14_3_minus4": [
                show(value) for value in first_projection_eigen
            ],
            "first_projection_trace": show(first_projection_trace),
            "orthogonal_mate_gram_H_eigenvalues": [
                show(value) for value in h_eigen
            ],
            "second_fixed_projection_eigenvalues": [
                show(value) for value in second_fixed_eigen
            ],
            "second_fixed_projection_trace": show(second_fixed_trace),
            "remaining_trace_constant_plus_2D": "33264/5+2D_*",
            "refined_variance_bound": (
                "||W||_F^2<=731808/17+(220/17)D_*"
            ),
            "endpoint_D_zero_even_integral_bound": "||W||_F^2<=43046",
        },
        "packing_bounds": {
            "weighted_distance_two_graph": "L=J_edge^2-12I",
            "L_degree": l_degree,
            "least_eigenvalue_lower_bound": -12,
            "Hoffman_independence_upper_bound": show(hoffman_alpha_upper),
            "cell_size": cell_size,
            "Hoffman_coloring_lower_bound": 12,
            "number_of_cells": cell_count,
            "closed_neighborhood_sphere_size_for_one_cell": sphere_vertices,
            "ambient_vertices": edge_count,
        },
        "old_wave_comparison": {
            "Wave20_C_compression_Ritz_values": [
                show(value) for value in old_ritz
            ],
            "distinction": (
                "Wave20 compresses with ordinary endpoint incidence C; this "
                "artifact compresses with the triangle-mate partition R and "
                "then uses C only for a Schur refinement"
            ),
            "Wave35": (
                "uses the Wave6 prism-free/triangle-free endpoint for signed "
                "and one-triangle local constraints, but does not form this "
                "99-cell triangle-mate quotient"
            ),
            "Wave65": (
                "row r of R J_edge is precisely the second weighted factor U_r; "
                "at D(r)=0 it is the simple (Q,d)=(0,1) factor"
            ),
        },
        "boundary": {
            "positive_lower_bound_on_D_star": 0,
            "distance_two_packing_excluded": False,
            "reason": (
                "cell size 7 passes the sphere and Hoffman bounds, and all "
                "derived Gram/Schur inequalities admit D_*=0 (including W=0)"
            ),
            "W_zero_interpretation": (
                "exactly one J_edge edge between every nonadjacent pair of mate cells"
            ),
            "claim": "NULL_BOUNDARY_NO_ENDPOINT_EXCLUSION",
        },
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "output": str(OUTPUT),
        "refined_endpoint_W_norm_upper": endpoint_even_upper,
        "Hoffman_alpha_upper": show(hoffman_alpha_upper),
        "D_star_lower_bound": 0,
    }, indent=2))


if __name__ == "__main__":
    main()
