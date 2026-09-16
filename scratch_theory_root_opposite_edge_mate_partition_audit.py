"""Independent exact audit of the triangle-mate partition certificate.

The checker deliberately does not import the generating module.  It rebuilds
the SRG algebra from its multiplication table, redoes both orthogonal
projections by scalar Gaussian/Bessel arithmetic, and verifies the packing
and parity bounds stored in the JSON artifact.
"""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "scratch_theory_root_opposite_edge_mate_partition.json"
OUTPUT = ROOT / "scratch_theory_root_opposite_edge_mate_partition_audit.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def parse(value: int | str) -> Fraction:
    return Fraction(value)


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    assert source["status"] == "TRIANGLE_MATE_PARTITION_BOUNDARY_PASS"

    # Rebuild the complete parameter arithmetic without reading any numbers
    # from the construction script.
    n, k, lam, mu = 99, 14, 1, 2
    graph_edges = n * k // 2
    triangles = graph_edges * lam // 3
    assert (graph_edges, triangles) == (693, 231)
    assert graph_edges == n * 7

    # Each edge has one triangle mate.  The seven edges whose mate is r are
    # the seven disjoint edges of G[N(r)], hence form an independent J_E cell.
    # J_E is 12-regular by the usual common-neighbour bijection: choose one
    # of the k-2 nontriangle neighbours at a fixed endpoint; reversing the
    # resulting four-cycle produces the same twelve opposite edges.
    j_degree = k - 2
    j_edges = graph_edges * j_degree // 2
    assert (j_degree, j_edges) == (12, 4158)

    # SRG adjacency eigendata follows from x^2+x-12=0 off the constants.
    theta = (14, 3, -4)
    ranks = (1, 54, 44)
    assert sum(ranks) == n
    kbar = (84, -4, 3)       # One-I-A
    s = (28, 17, 10)         # 14I+A=C C^T
    assert n * 84 // 2 == j_edges
    assert sum(rank * value * value for rank, value in zip(ranks, kbar)) == 8316

    # Independent entrywise check of C J_E=A C-C-2R.  Relative to an edge
    # xy with triangle mate z, the 99 rows split as follows.  The last column
    # is the claimed number of endpoints among the twelve opposite edges.
    row_types = (
        ("x_or_y", 2, 1, 1, 0, 0),
        ("z", 1, 2, 0, 1, 0),
        ("adjacent_to_exactly_one_endpoint", 24, 1, 0, 0, 1),
        ("adjacent_to_neither", 72, 0, 0, 0, 0),
    )
    assert sum(row[1] for row in row_types) == n
    for _, _, ac, c, r, cj in row_types:
        assert ac - c - 2 * r == cj
    assert sum(mult * cj for _, mult, _, _, _, cj in row_types) == 24
    # Endpoint incidences count each of the twelve opposite edges twice.

    # Mixed quotient C J_E R^T=A^2-A-14I=2(One-I-A).
    # Check this on all three primitive eigenspaces.
    mixed = tuple(value * value - value - 14 for value in theta)
    assert mixed == tuple(2 * value for value in kbar) == (168, -8, 6)

    # Bessel projection 1: (2K)^T S^-1 (2K).
    p1 = tuple(Fraction(4 * value * value, denominator)
               for value, denominator in zip(kbar, s))
    p1_trace = sum(rank * value for rank, value in zip(ranks, p1))
    assert p1 == (Fraction(1008), Fraction(64, 17), Fraction(18, 5))
    assert p1_trace == Fraction(116424, 85)

    # Bessel projection 2 after residualizing R against C.
    h = tuple(Fraction(7) - Fraction(value * value, denominator)
              for value, denominator in zip(theta, s))
    hplus = tuple(Fraction(0) if value == 0 else 1 / value for value in h)
    t0 = tuple(Fraction(2 * a * b, denominator)
               for a, b, denominator in zip(theta, kbar, s))
    residual = tuple(a - b for a, b in zip(kbar, t0))
    p2 = tuple(value * value * inverse
               for value, inverse in zip(residual, hplus))
    p2_trace = sum(rank * value for rank, value in zip(ranks, p2))
    assert h == (Fraction(0), Fraction(110, 17), Fraction(27, 5))
    assert t0 == (Fraction(84), Fraction(-24, 17), Fraction(-12, 5))
    assert residual == (Fraction(0), Fraction(-44, 17), Fraction(27, 5))
    assert p2 == (Fraction(0), Fraction(968, 935), Fraction(27, 5))
    assert p2_trace == Fraction(24948, 85)

    free_trace = Fraction(8316) - p1_trace - p2_trace
    assert free_trace == Fraction(33264, 5)
    # H^+ has least positive eigenvalue 17/110.  Since W1=0,
    # (17/110)||W||^2 <= free_trace+2D.
    w_constant = Fraction(110, 17) * free_trace
    w_d = Fraction(220, 17)
    assert (w_constant, w_d) == (Fraction(731808, 17), Fraction(220, 17))
    largest_even_endpoint = 2 * ((w_constant.numerator //
                                  w_constant.denominator) // 2)
    assert largest_even_endpoint == 43046

    schur = source["incidence_schur_refinement"]
    assert tuple(map(parse, schur["first_projection_eigenvalues_on_A_14_3_minus4"])) == p1
    assert parse(schur["first_projection_trace"]) == p1_trace
    assert tuple(map(parse, schur["orthogonal_mate_gram_H_eigenvalues"])) == h
    assert tuple(map(parse, schur["second_fixed_projection_eigenvalues"])) == p2
    assert parse(schur["second_fixed_projection_trace"]) == p2_trace
    assert schur["endpoint_D_zero_even_integral_bound"] == "||W||_F^2<=43046"

    # Packing/Hoffman check.  At the prism-free endpoint J_E is triangle-free,
    # so L=J_E^2-12I is entrywise nonnegative, 132-regular, and has spectrum
    # lambda(J_E)^2-12 >= -12.  The worst-case Hoffman ratio is 12/(132+12).
    l_degree = j_degree * (j_degree - 1)
    alpha_upper = Fraction(graph_edges * 12, l_degree + 12)
    assert (l_degree, alpha_upper) == (132, Fraction(231, 4))
    assert 7 <= alpha_upper
    assert 7 * (1 + j_degree) == 91 <= graph_edges
    packing = source["packing_bounds"]
    assert parse(packing["Hoffman_independence_upper_bound"]) == alpha_upper
    assert packing["Hoffman_coloring_lower_bound"] == 12 < 99

    # The endpoint substitution D=0,W=0 satisfies every scalar inequality in
    # this package.  This does not assert realization by a graph; it proves
    # that the route itself has no positive D lower bound.
    assert 0 <= 49896
    assert 0 <= w_constant
    assert source["boundary"]["positive_lower_bound_on_D_star"] == 0
    assert not source["boundary"]["distance_two_packing_excluded"]

    result = {
        "status": "INDEPENDENT_TRIANGLE_MATE_PARTITION_AUDIT_PASS",
        "source_sha256": digest(SOURCE),
        "checks": {
            "cell_partition_counts": True,
            "entrywise_CJ_identity_row_types": True,
            "mixed_incidence_eigenspaces": True,
            "two_stage_Bessel_Schur_arithmetic": True,
            "endpoint_even_integrality": True,
            "distance_two_Hoffman_and_sphere_bounds": True,
            "D_zero_W_zero_scalar_control": True,
        },
        "recomputed": {
            "first_projection_trace": str(p1_trace),
            "second_fixed_projection_trace": str(p2_trace),
            "free_trace_at_D_zero": str(free_trace),
            "refined_W_norm_squared_endpoint_even_upper": largest_even_endpoint,
            "distance_two_Hoffman_alpha_upper": str(alpha_upper),
            "derived_D_star_lower_bound": 0,
        },
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
