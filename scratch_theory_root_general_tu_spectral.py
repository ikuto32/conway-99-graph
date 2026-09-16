"""General-root spectral traces for the transition factor T and mate factor U.

The calculation is conditional on a putative srg(99,14,1,2), but does not
assume the prism-free endpoint.  It is standard-library only.  Besides the
affine trace formulae, it certifies that the natural scalar operator,
Frobenius and two-factor Cauchy tests are automatically feasible throughout
the elementary local (S,D) simplex.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "scratch_theory_root_general_tu_spectral.json"
INPUTS = {
    "motif_first_moment_audit":
        ROOT / "scratch_root_e0_motif_first_moment_audit.json",
    "augmented_relation":
        ROOT / "scratch_theory_root_yyt_augmented_relation.json",
    "wave65_independent": ROOT / (
        "external_conway99_research/verification/"
        "wave65-rooted-hypergraph-algebra/independent-results.json"
    ),
    "prism_bridge": ROOT / "scratch_root_e0_prism_bridge.md",
}

F = Fraction
Poly = dict[tuple[int, int], Fraction]
Affine = tuple[Fraction, Fraction, Fraction]  # constant + S*s + D*d


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def show(value: Fraction | int) -> int | str:
    value = F(value)
    return int(value) if value.denominator == 1 else str(value)


def solve(matrix, right):
    a = [[F(value) for value in row] + [F(rhs)]
         for row, rhs in zip(matrix, right)]
    n = len(a)
    assert all(len(row) == n + 1 for row in a)
    for column in range(n):
        pivot = next(row for row in range(column, n) if a[row][column])
        a[column], a[pivot] = a[pivot], a[column]
        scale = a[column][column]
        a[column] = [value / scale for value in a[column]]
        for row in range(n):
            if row == column:
                continue
            scale = a[row][column]
            a[row] = [value - scale * base
                      for value, base in zip(a[row], a[column])]
    return tuple(row[-1] for row in a)


def affine_add(left: Affine, right: Affine) -> Affine:
    return tuple(a + b for a, b in zip(left, right))  # type: ignore[return-value]


def affine_sub(left: Affine, right: Affine) -> Affine:
    return tuple(a - b for a, b in zip(left, right))  # type: ignore[return-value]


def affine_value(value: Affine, s: Fraction, d: Fraction) -> Fraction:
    return value[0] + value[1] * s + value[2] * d


def affine_power_moment(eigenvalues, vector, power):
    return tuple(
        sum(F(eigenvalue ** power) * value[index]
            for eigenvalue, value in zip(eigenvalues, vector))
        for index in range(3)
    )


def poly_add(left: Poly, right: Poly) -> Poly:
    result = dict(left)
    for monomial, coefficient in right.items():
        result[monomial] = result.get(monomial, F()) + coefficient
    return {monomial: coefficient for monomial, coefficient in result.items()
            if coefficient}


def poly_scale(poly: Poly, scale: Fraction) -> Poly:
    return {monomial: coefficient * scale
            for monomial, coefficient in poly.items() if coefficient * scale}


def poly_multiply(left: Poly, right: Poly) -> Poly:
    result: Poly = {}
    for (i, j), a in left.items():
        for (p, q), b in right.items():
            key = (i + p, j + q)
            result[key] = result.get(key, F()) + a * b
    return {monomial: coefficient for monomial, coefficient in result.items()
            if coefficient}


def poly_power(poly: Poly, power: int) -> Poly:
    answer: Poly = {(0, 0): F(1)}
    for _ in range(power):
        answer = poly_multiply(answer, poly)
    return answer


def poly_substitute(poly: Poly, first: Poly, second: Poly) -> Poly:
    answer: Poly = {}
    for (i, j), coefficient in poly.items():
        term = poly_multiply(poly_power(first, i), poly_power(second, j))
        answer = poly_add(answer, poly_scale(term, coefficient))
    return answer


def affine_poly(value: Affine) -> Poly:
    return {(0, 0): value[0], (1, 0): value[1], (0, 1): value[2]}


def projection_inner(left, right, ranks) -> Poly:
    result: Poly = {}
    for a, b, rank in zip(left, right, ranks):
        result = poly_add(
            result,
            poly_scale(poly_multiply(affine_poly(a), affine_poly(b)), F(1, rank)),
        )
    return result


def triangular_bernstein(poly: Poly, degree: int):
    """Convert p(84*x,42*y) to triangular Bernstein coefficients.

    The returned basis is multinomial(degree;i,j,k) x^i y^j h^k with
    h=1-x-y.  Exact nonnegative coefficients certify p>=0 on
    S>=0,D>=0,S+2D<=84.
    """

    scaled = {(i, j): coefficient * 84 ** i * 42 ** j
              for (i, j), coefficient in poly.items()}
    indices = tuple((i, j, degree - i - j)
                    for i in range(degree + 1)
                    for j in range(degree + 1 - i))
    monomials = tuple((i, j)
                      for i in range(degree + 1)
                      for j in range(degree + 1 - i))

    def expand_basis(i, j, k):
        answer: Poly = {}
        multinomial = F(math.factorial(degree),
                        math.factorial(i) * math.factorial(j) * math.factorial(k))
        for total in range(k + 1):
            for x_power in range(total + 1):
                y_power = total - x_power
                coefficient = (
                    multinomial * (-1) ** total
                    * math.comb(k, total) * math.comb(total, x_power)
                )
                key = (i + x_power, j + y_power)
                answer[key] = answer.get(key, F()) + coefficient
        return answer

    matrix = [
        [expand_basis(*index).get(monomial, F()) for index in indices]
        + [scaled.get(monomial, F())]
        for monomial in monomials
    ]
    coefficients = solve([row[:-1] for row in matrix], [row[-1] for row in matrix])
    return tuple(zip(indices, coefficients))


def serialize_affine(vector):
    return [[show(value) for value in entry] for entry in vector]


def serialize_poly(poly, variables=("S", "D")):
    return [
        {
            f"{variables[0]}_power": i,
            f"{variables[1]}_power": j,
            "coefficient": show(coefficient),
        }
        for (i, j), coefficient in sorted(poly.items())
    ]


def main() -> None:
    for path in INPUTS.values():
        assert path.is_file(), path
    motif = json.loads(INPUTS["motif_first_moment_audit"].read_text(encoding="utf-8"))
    augmented = json.loads(INPUTS["augmented_relation"].read_text(encoding="utf-8"))
    wave65 = json.loads(INPUTS["wave65_independent"].read_text(encoding="utf-8"))
    assert motif["status"] == "E0_MOTIF_FIRST_MOMENT_AUDIT_PASS"
    assert augmented["status"] == "AUGMENTED_FLAG_RELATION_AND_BAD_MATE_CAPACITY_PASS"
    assert wave65["claim_label"] == "VERIFIED"

    # Clean-room label census for H=K14-7K2 and its line graph Q.
    labels = tuple(pair for pair in itertools.combinations(range(14), 2)
                   if pair[1] != (pair[0] ^ 1))
    assert len(labels) == 84
    q_neighbours = {
        label: frozenset(other for other in labels
                         if other != label and set(label) & set(other))
        for label in labels
    }
    relation_count: dict[tuple[int, int], int] = {}
    q2_values: dict[tuple[int, int], set[int]] = {}
    for left, right in itertools.combinations(labels, 2):
        relation = (
            len(set(left) & set(right)),
            sum((point ^ 1) in right for point in left),
        )
        relation_count[relation] = relation_count.get(relation, 0) + 1
        q2_values.setdefault(relation, set()).add(
            len(q_neighbours[left] & q_neighbours[right])
        )
    assert relation_count == {
        (1, 0): 840, (1, 1): 84, (0, 0): 1680,
        (0, 1): 840, (0, 2): 42,
    }
    assert q2_values == {
        (1, 0): {11}, (1, 1): {10}, (0, 0): {4},
        (0, 1): {3}, (0, 2): {2},
    }

    # Q=10I+2One-B^2-B.  The Q eigenvalue/root pairs off constants are
    #  -2:{3,-4} (dimension70), 10:{0,-1} (dimension7),
    #   8:{1,-2} (dimension6).  B has 140 triangles for every root:
    # its 420 disjoint-label edges each lie in their unique outside triangle.
    # Trace and cubic trace determine the split uniquely.
    multiplicity_solutions = []
    for m3 in range(71):
        for m0 in range(8):
            for m1 in range(7):
                spectrum = {
                    12: 1, 3: m3, -4: 70 - m3,
                    0: m0, -1: 7 - m0,
                    1: m1, -2: 6 - m1,
                }
                if sum(value * count for value, count in spectrum.items()) != 0:
                    continue
                if sum(value * value * count for value, count in spectrum.items()) != 1008:
                    continue
                if sum(value ** 3 * count for value, count in spectrum.items()) != 840:
                    continue
                multiplicity_solutions.append((m3, m0, m1, spectrum))
    assert len(multiplicity_solutions) == 1
    assert multiplicity_solutions[0][:3] == (40, 7, 0)

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

    # T has 84 unit edges: 84-S of type(1,0), S of type(1,1).
    # U has S unit type(1,1), D double type(0,2), and 84-S-2D unit
    # type(0,1).  Solve the five trace equations coefficient by coefficient.
    t_rhs = (
        (0, 0, 0), (2, 0, 0), (168, 0, 0),
        (168, 0, 0), (1848, -2, 0),
    )
    u_rhs = (
        (0, 0, 0), (2, 0, 0), (168, 0, 0),
        (0, 2, 0), (504, 14, -4),
    )
    t_vector = tuple(zip(*(solve(system, [row[index] for row in t_rhs])
                           for index in range(3))))
    u_vector = tuple(zip(*(solve(system, [row[index] for row in u_rhs])
                           for index in range(3))))
    expected_t = (
        (F(2), F(0), F(0)),
        (F(72, 5), F(2, 105), F(0)),
        (F(7), -F(1, 12), F(0)),
        (F(18, 5), F(1, 10), F(0)),
        (-F(27), -F(1, 28), F(0)),
    )
    expected_u = (
        (F(2), F(0), F(0)),
        (F(112, 5), -F(8, 105), F(4, 105)),
        (-F(7), F(1, 12), -F(1, 6)),
        (F(18, 5), F(1, 10), F(1, 5)),
        (-F(21), -F(3, 28), -F(1, 14)),
    )
    assert t_vector == expected_t
    assert u_vector == expected_u

    # Direct mixed-moment checks, including the pointwise BQ relation.
    t_power = {power: affine_power_moment(eigenvalues, t_vector, power)
               for power in range(5)}
    u_power = {power: affine_power_moment(eigenvalues, u_vector, power)
               for power in range(5)}
    assert t_power == {
        0: (F(0), F(0), F(0)),
        1: (F(168), F(0), F(0)),
        2: (F(0), F(0), F(0)),
        3: (F(5544), F(2), F(0)),
        4: (F(35784), -F(6), F(0)),
    }
    assert u_power == {
        0: (F(0), F(0), F(0)),
        1: (F(168), F(0), F(0)),
        2: (F(168), -F(2), F(0)),
        3: (F(5376), F(4), F(4)),
        4: (F(37968), -F(32), -F(12)),
    }
    t_bq = tuple(sum(F(lam * q) * value[index]
                     for lam, q, value in zip(eigenvalues, q_eigenvalues, t_vector))
                 for index in range(3))
    u_bq = tuple(sum(F(lam * q) * value[index]
                     for lam, q, value in zip(eigenvalues, q_eigenvalues, u_vector))
                 for index in range(3))
    assert t_bq == (F(168), -F(2), F(0))
    assert u_bq == (F(168), -F(2), -F(4))

    # Global sums after S_*=8316-2n3 and D_*=n3-z11/4.
    total_t = (
        (F(198), F(0), F(0)),
        (F(1584), -F(4, 105), F(0)),
        (F(0), F(1, 6), F(0)),
        (F(1188), -F(1, 5), F(0)),
        (-F(2970), F(1, 14), F(0)),
    )
    total_u = (
        (F(198), F(0), F(0)),
        (F(1584), F(4, 21), -F(1, 105)),
        (F(0), -F(1, 3), F(1, 24)),
        (F(1188), F(0), -F(1, 20)),
        (-F(2970), F(1, 7), F(1, 56)),
    )
    # Reconstruct these totals mechanically from each local affine formula.
    # If a=c+s*S+d*D, summing gives 99c+s(8316-2n)+d(n-z/4).
    def root_sum(vector):
        answer = []
        for constant, s_coefficient, d_coefficient in vector:
            answer.append((
                99 * constant + 8316 * s_coefficient,
                -2 * s_coefficient + d_coefficient,
                -d_coefficient / 4,
            ))
        return tuple(answer)
    assert root_sum(t_vector) == total_t
    assert root_sum(u_vector) == total_u

    global_mixed = {
        "sum_tr_TBQ": (F(0), F(4), F(0)),
        "sum_tr_UBQ": (F(0), F(0), F(1)),
        "sum_tr_B2U": (F(0), F(4), F(0)),
        "sum_tr_B3T": (F(565488), -F(4), F(0)),
        "sum_tr_B4T": (F(3492720), F(12), F(0)),
        "sum_tr_B3U": (F(565488), -F(4), -F(1)),
        "sum_tr_B4U": (F(3492720), F(52), F(3)),
    }

    # Scalar Frobenius/Cauchy screen.  Orthogonal projection onto the five
    # normalized projectors gives the following 2x2 residual Gram.
    p_t = projection_inner(t_vector, t_vector, ranks)
    p_u = projection_inner(u_vector, u_vector, ranks)
    p_tu = projection_inner(t_vector, u_vector, ranks)
    residual_t = poly_add({(0, 0): F(168)}, poly_scale(p_t, -1))
    residual_u = poly_add(
        {(0, 0): F(168), (0, 1): F(4)}, poly_scale(p_u, -1)
    )
    residual_cross = poly_add(
        {(1, 0): F(2)}, poly_scale(p_tu, -1)
    )
    residual_determinant = poly_add(
        poly_multiply(residual_t, residual_u),
        poly_scale(poly_multiply(residual_cross, residual_cross), -1),
    )
    bernstein_t = triangular_bernstein(residual_t, 2)
    bernstein_u = triangular_bernstein(residual_u, 2)
    bernstein_det = triangular_bernstein(residual_determinant, 4)
    assert all(value > 0 for _, value in bernstein_t)
    assert all(value > 0 for _, value in bernstein_u)
    assert all(value >= 0 for _, value in bernstein_det)
    assert [index for index, value in bernstein_det if value == 0] == [(4, 0, 0)]

    # Operator trace bounds are affine in S,D, so it suffices to check the
    # three vertices of S>=0,D>=0,S+2D<=84.
    simplex_vertices = ((F(0), F(0)), (F(84), F(0)), (F(0), F(42)))
    operator_controls = []
    for s, d in simplex_vertices:
        t_value = tuple(affine_value(value, s, d) for value in t_vector)
        u_value = tuple(affine_value(value, s, d) for value in u_vector)
        plus = tuple(a + b for a, b in zip(t_value, u_value))
        minus = tuple(a - b for a, b in zip(t_value, u_value))
        assert all(abs(value) <= 2 * rank for value, rank in zip(t_value, ranks))
        assert all(abs(value) <= 2 * rank for value, rank in zip(u_value, ranks))
        assert all(abs(value) <= 4 * rank for value, rank in zip(plus, ranks))
        assert all(abs(value) <= 4 * rank for value, rank in zip(minus, ranks))
        operator_controls.append({
            "S_D": [show(s), show(d)],
            "T": [show(value) for value in t_value],
            "U": [show(value) for value in u_value],
            "T_plus_U": [show(value) for value in plus],
            "T_minus_U": [show(value) for value in minus],
        })

    # The global mean point has barycentric coordinates determined by the
    # already-known nonnegative global counts.  Thus the Bernstein certificate
    # proves the 99-root aggregate screen is redundant too.
    barycentric_global = {
        "x=S_*/8316": "1-n3/4158",
        "y=2D_*/8316": "(4n3-z11)/16632",
        "h=(8316-S_*-2D_*)/8316": "z11/16632",
    }
    # The determinant of the aggregate 99-root residual Gram is 99^2 times
    # the local determinant at Sbar=84-2n3/99,
    # Dbar=n3/99-z11/396.  Record its exact expanded form as an additional
    # machine-checkable bridge to the global variables.
    global_determinant = poly_scale(
        poly_substitute(
            residual_determinant,
            {(0, 0): F(84), (1, 0): -F(2, 99)},
            {(1, 0): F(1, 99), (0, 1): -F(1, 396)},
        ),
        F(99 * 99),
    )
    assert global_determinant == {
        (0, 1): -F(51282, 5),
        (0, 2): -F(17, 200),
        (1, 0): F(615384, 5),
        (1, 1): F(16, 15),
        (2, 0): -F(62, 5),
        (2, 1): -F(541, 6237000),
        (3, 0): -F(43, 519750),
        (4, 0): F(71, 5402801250),
    }

    result = {
        "status": "GENERAL_ROOT_TU_SPECTRAL_NULL_BOUNDARY_PASS",
        "scope": (
            "conditional exact general-root identities; no endpoint assumption, "
            "construction, or nonexistence claim"
        ),
        "input_sha256": {name: sha256(path) for name, path in INPUTS.items()},
        "fixed_root_scaffold": {
            "B_equation": "Q=10I+2One-B^2-B",
            "Q_relation_counts": {str(key): value for key, value in relation_count.items()},
            "Q2_by_(Q,d)_relation": {
                str(key): next(iter(value)) for key, value in q2_values.items()
            },
            "B_triangle_count": 140,
            "B_spectrum": {"12": 1, "3": 40, "0": 7, "-2": 6, "-4": 30},
            "spectrum_split_solution_count": len(multiplicity_solutions),
            "Q_eigenvalues_in_projector_order": list(q_eigenvalues),
            "projector_order": list(eigenvalues),
            "projector_ranks": list(ranks),
        },
        "local_factor_edge_profiles": {
            "T": ["84-S edges type (Q,d)=(1,0)", "S edges type (1,1)"],
            "U": [
                "S unit edges type (1,1)",
                "D double edges type (0,2)",
                "84-S-2D unit edges type (0,1)",
            ],
            "elementary_simplex": "S>=0, D>=0, S+2D<=84",
            "norms_and_overlap": [
                "tr(T^2)=168", "tr(U^2)=168+4D", "tr(TU)=2S"
            ],
        },
        "local_projector_traces_affine_constant_S_D": {
            "T": serialize_affine(t_vector),
            "U": serialize_affine(u_vector),
        },
        "local_mixed_traces_affine_constant_S_D": {
            "T_B_powers_0_to_4": {
                str(power): [show(value) for value in affine]
                for power, affine in t_power.items()
            },
            "U_B_powers_0_to_4": {
                str(power): [show(value) for value in affine]
                for power, affine in u_power.items()
            },
            "tr_TBQ": [show(value) for value in t_bq],
            "tr_UBQ": [show(value) for value in u_bq],
            "pointwise": (
                "on every selected B-edge xy, (BQ)[x,y]=2-Q[x,y]-d_r(x,y)"
            ),
        },
        "global_projector_traces_affine_constant_n3_z11": {
            "T": serialize_affine(total_t),
            "U": serialize_affine(total_u),
            "input_first_moments": [
                "S_*=8316-2n3", "D_*=n3-z11/4"
            ],
        },
        "global_mixed_traces_affine_constant_n3_z11": {
            name: [show(value) for value in affine]
            for name, affine in global_mixed.items()
        },
        "scalar_projection_screen": {
            "projection_norm_T_polynomial": serialize_poly(p_t),
            "projection_norm_U_polynomial": serialize_poly(p_u),
            "projection_inner_TU_polynomial": serialize_poly(p_tu),
            "residual_T_polynomial": serialize_poly(residual_t),
            "residual_U_polynomial": serialize_poly(residual_u),
            "residual_cross_polynomial": serialize_poly(residual_cross),
            "residual_determinant_polynomial": serialize_poly(residual_determinant),
            "Bernstein_basis": (
                "multinomial(m;i,j,k)*(S/84)^i*(D/42)^j*"
                "(1-S/84-D/42)^k"
            ),
            "residual_T_Bernstein_degree2": [
                {"i_j_k": list(index), "coefficient": show(value)}
                for index, value in bernstein_t
            ],
            "residual_U_Bernstein_degree2": [
                {"i_j_k": list(index), "coefficient": show(value)}
                for index, value in bernstein_u
            ],
            "determinant_Bernstein_degree4": [
                {"i_j_k": list(index), "coefficient": show(value)}
                for index, value in bernstein_det
            ],
            "operator_bound_simplex_vertex_controls": operator_controls,
            "global_mean_barycentric_coordinates": barycentric_global,
            "aggregate_99_root_determinant_polynomial_in_n3_z11":
                serialize_poly(global_determinant, ("n3", "z11")),
            "aggregate_bridge": (
                "det(R_global)=99^2*det(R_local at "
                "S=84-2n3/99,D=n3/99-z11/396)"
            ),
        },
        "integrality": {
            "local_mixed_power_traces": (
                "all displayed B-power/BQ traces are integral for integer S,D"
            ),
            "projector_traces": (
                "rational projector traces need not be integers; their "
                "denominators are those of the rational spectral projectors"
            ),
            "new_congruence": None,
        },
        "boundary": {
            "new_inequality_in_n3_z11_or_E0": None,
            "known_domain": "0<=n3<=4158 and 0<=z11<=4n3",
            "reason": (
                "this known domain is exactly the global mean (S,D) simplex; "
                "all operator controls pass its vertices and every Frobenius/"
                "Cauchy residual has a nonnegative Bernstein certificate"
            ),
            "known_identities_reexpressed": [
                "sum_r tr(T_r B_r Q_r)=4n3",
                "sum_r tr(U_r B_r Q_r)=z11",
                "sum_r tr(B_r^2 U_r)=4n3",
            ],
            "first_missing_information": (
                "entrywise/noncommutative placement of T_r and U_r inside "
                "the fixed Q scaffold, not their scalar projector traces"
            ),
            "claim": "SCALAR_GENERAL_ROOT_ROUTE_IS_EXACTLY_NULL",
        },
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "output": str(OUTPUT),
        "B_spectrum": result["fixed_root_scaffold"]["B_spectrum"],
        "determinant_Bernstein_nonnegative": True,
        "new_inequality": None,
    }, indent=2))


if __name__ == "__main__":
    main()
