"""Independent audit of the general-root T/U spectral calculation.

Unlike the producer, this checker obtains the projector traces from explicit
Lagrange polynomials in B.  It verifies rather than solves the triangular
Bernstein certificate for the joint residual Gram.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "scratch_theory_root_general_tu_spectral.json"
OUTPUT = ROOT / "scratch_theory_root_general_tu_spectral_audit.json"
F = Fraction


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def parse(value):
    return F(value)


def add(left, right):
    result = dict(left)
    for key, value in right.items():
        result[key] = result.get(key, F()) + value
    return {key: value for key, value in result.items() if value}


def scale(poly, scalar):
    return {key: value * scalar for key, value in poly.items() if value * scalar}


def multiply(left, right):
    result = {}
    for (i, j), a in left.items():
        for (p, q), b in right.items():
            key = i + p, j + q
            result[key] = result.get(key, F()) + a * b
    return {key: value for key, value in result.items() if value}


def power(poly, exponent):
    result = {(0, 0): F(1)}
    for _ in range(exponent):
        result = multiply(result, poly)
    return result


def substitute(poly, first, second):
    result = {}
    for (i, j), coefficient in poly.items():
        term = multiply(power(first, i), power(second, j))
        result = add(result, scale(term, coefficient))
    return result


def affine_to_poly(value):
    return {(0, 0): value[0], (1, 0): value[1], (0, 1): value[2]}


def affine_add(*values):
    return tuple(sum((value[index] for value in values), F()) for index in range(3))


def affine_scale(value, scalar):
    return tuple(scalar * entry for entry in value)


def one_variable_multiply(left, right):
    result = [F()] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            result[i + j] += a * b
    return result


def lagrange_polynomial(target, eigenvalues):
    numerator = [F(1)]
    denominator = F(1)
    for other in eigenvalues:
        if other == target:
            continue
        numerator = one_variable_multiply(numerator, [-F(other), F(1)])
        denominator *= target - other
    return tuple(value / denominator for value in numerator)


def projector_from_moments(moments, eigenvalues):
    answer = []
    for target in eigenvalues:
        polynomial = lagrange_polynomial(target, eigenvalues)
        answer.append(tuple(
            sum(polynomial[power] * moments[power][coordinate]
                for power in range(5))
            for coordinate in range(3)
        ))
    return tuple(answer)


def projection_inner(left, right, ranks):
    result = {}
    for a, b, rank in zip(left, right, ranks):
        result = add(result, scale(multiply(affine_to_poly(a), affine_to_poly(b)), F(1, rank)))
    return result


def parse_poly(records, variables=("S", "D")):
    return {
        (int(record[f"{variables[0]}_power"]),
         int(record[f"{variables[1]}_power"])):
            parse(record["coefficient"])
        for record in records
    }


def expand_bernstein(records, degree):
    """Expand a stored triangular Bernstein certificate into S,D monomials."""

    result = {}
    for record in records:
        i, j, k = map(int, record["i_j_k"])
        assert i + j + k == degree
        coefficient = parse(record["coefficient"])
        coefficient *= F(math.factorial(degree),
                         math.factorial(i) * math.factorial(j) * math.factorial(k))
        coefficient /= 84 ** i * 42 ** j
        # Expand (1-S/84-D/42)^k by first choosing total nonconstant degree,
        # then its S/D split.
        for total in range(k + 1):
            for s_extra in range(total + 1):
                d_extra = total - s_extra
                value = coefficient * (-1) ** total
                value *= math.comb(k, total) * math.comb(total, s_extra)
                value /= 84 ** s_extra * 42 ** d_extra
                key = i + s_extra, j + d_extra
                result[key] = result.get(key, F()) + value
    return {key: value for key, value in result.items() if value}


def main() -> None:
    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    assert source["status"] == "GENERAL_ROOT_TU_SPECTRAL_NULL_BOUNDARY_PASS"

    # Independent line-graph relation census.
    labels = [pair for pair in itertools.combinations(range(14), 2)
              if pair[1] != (pair[0] ^ 1)]
    neighbours = {
        label: {other for other in labels if other != label and set(label) & set(other)}
        for label in labels
    }
    counts = {}
    q2 = {}
    for left, right in itertools.combinations(labels, 2):
        key = (len(set(left) & set(right)),
               sum((point ^ 1) in right for point in left))
        counts[key] = counts.get(key, 0) + 1
        q2.setdefault(key, set()).add(len(neighbours[left] & neighbours[right]))
    assert counts == {(1, 0): 840, (1, 1): 84, (0, 0): 1680,
                      (0, 1): 840, (0, 2): 42}
    assert q2 == {(1, 0): {11}, (1, 1): {10}, (0, 0): {4},
                  (0, 1): {3}, (0, 2): {2}}

    # The five B moments are derived directly from edge profiles and
    # Q=10I+2One-B^2-B.  The pointwise formula gives the BQ moment; expanding
    # Q^2 gives the fourth moment.  Each entry is constant+S*S+D*D.
    t_q = (F(168), F(0), F(0))
    u_q = (F(0), F(2), F(0))
    t_q2 = (F(1848), -F(2), F(0))
    u_q2 = (F(504), F(14), -F(4))
    t_bq = (F(168), -F(2), F(0))
    u_bq = (F(168), -F(2), -F(4))

    def make_moments(q, q_squared, bq):
        m0 = (F(0), F(0), F(0))
        m1 = (F(168), F(0), F(0))
        # tr(FQ)=168-tr(FB^2).
        m2 = affine_add((F(168), F(0), F(0)), affine_scale(q, -1))
        # tr(FBQ)=5712-tr(FB^3)-tr(FB^2).
        m3 = affine_add((F(5712), F(0), F(0)),
                        affine_scale(m2, -1), affine_scale(bq, -1))
        # tr(FQ^2)=m4+2m3-19m2-20m1-41664.
        m4 = affine_add(q_squared, affine_scale(m3, -2),
                        affine_scale(m2, 19), affine_scale(m1, 20),
                        (F(41664), F(0), F(0)))
        return (m0, m1, m2, m3, m4)

    t_moments = make_moments(t_q, t_q2, t_bq)
    u_moments = make_moments(u_q, u_q2, u_bq)
    assert t_moments == (
        (F(0), F(0), F(0)), (F(168), F(0), F(0)),
        (F(0), F(0), F(0)), (F(5544), F(2), F(0)),
        (F(35784), -F(6), F(0)),
    )
    assert u_moments == (
        (F(0), F(0), F(0)), (F(168), F(0), F(0)),
        (F(168), -F(2), F(0)), (F(5376), F(4), F(4)),
        (F(37968), -F(32), -F(12)),
    )

    eigenvalues = (12, 3, 0, -2, -4)
    ranks = (1, 40, 7, 6, 30)
    t_projectors = projector_from_moments(t_moments, eigenvalues)
    u_projectors = projector_from_moments(u_moments, eigenvalues)
    stored_t = tuple(tuple(map(parse, row)) for row in
                     source["local_projector_traces_affine_constant_S_D"]["T"])
    stored_u = tuple(tuple(map(parse, row)) for row in
                     source["local_projector_traces_affine_constant_S_D"]["U"])
    assert t_projectors == stored_t
    assert u_projectors == stored_u

    # Root-sum substitution, performed again from the independently obtained
    # local formulae.
    def total(vector):
        return tuple((99 * c + 8316 * s, -2 * s + d, -d / 4)
                     for c, s, d in vector)
    stored_total_t = tuple(tuple(map(parse, row)) for row in
                           source["global_projector_traces_affine_constant_n3_z11"]["T"])
    stored_total_u = tuple(tuple(map(parse, row)) for row in
                           source["global_projector_traces_affine_constant_n3_z11"]["U"])
    assert total(t_projectors) == stored_total_t
    assert total(u_projectors) == stored_total_u

    # Rebuild the projected 2x2 residual Gram.
    p_t = projection_inner(t_projectors, t_projectors, ranks)
    p_u = projection_inner(u_projectors, u_projectors, ranks)
    p_tu = projection_inner(t_projectors, u_projectors, ranks)
    residual_t = add({(0, 0): F(168)}, scale(p_t, -1))
    residual_u = add({(0, 0): F(168), (0, 1): F(4)}, scale(p_u, -1))
    residual_cross = add({(1, 0): F(2)}, scale(p_tu, -1))
    determinant = add(multiply(residual_t, residual_u),
                      scale(multiply(residual_cross, residual_cross), -1))
    screen = source["scalar_projection_screen"]
    assert parse_poly(screen["projection_norm_T_polynomial"]) == p_t
    assert parse_poly(screen["projection_norm_U_polynomial"]) == p_u
    assert parse_poly(screen["projection_inner_TU_polynomial"]) == p_tu
    assert parse_poly(screen["residual_determinant_polynomial"]) == determinant

    # Verify the Bernstein certificates by exact expansion.  Positivity of
    # their coefficients proves positivity on the entire local simplex.
    records_t = screen["residual_T_Bernstein_degree2"]
    records_u = screen["residual_U_Bernstein_degree2"]
    records_det = screen["determinant_Bernstein_degree4"]
    assert expand_bernstein(records_t, 2) == residual_t
    assert expand_bernstein(records_u, 2) == residual_u
    assert expand_bernstein(records_det, 4) == determinant
    assert all(parse(record["coefficient"]) > 0 for record in records_t)
    assert all(parse(record["coefficient"]) > 0 for record in records_u)
    assert all(parse(record["coefficient"]) >= 0 for record in records_det)
    assert [record["i_j_k"] for record in records_det
            if parse(record["coefficient"]) == 0] == [[4, 0, 0]]

    # Recompute the displayed 99-root determinant polynomial.  The variables
    # of the substituted polynomial are now n3,z11 rather than S,D.
    global_determinant = scale(
        substitute(
            determinant,
            {(0, 0): F(84), (1, 0): -F(2, 99)},
            {(1, 0): F(1, 99), (0, 1): -F(1, 396)},
        ),
        F(99 * 99),
    )
    assert parse_poly(
        screen["aggregate_99_root_determinant_polynomial_in_n3_z11"],
        ("n3", "z11"),
    ) == global_determinant

    # Independently check the affine operator bounds at all simplex vertices.
    controls = []
    for s, d in ((F(0), F(0)), (F(84), F(0)), (F(0), F(42))):
        tv = tuple(c + ss * s + dd * d for c, ss, dd in t_projectors)
        uv = tuple(c + ss * s + dd * d for c, ss, dd in u_projectors)
        assert all(abs(value) <= 2 * rank for value, rank in zip(tv, ranks))
        assert all(abs(value) <= 2 * rank for value, rank in zip(uv, ranks))
        assert all(abs(a + b) <= 4 * rank for a, b, rank in zip(tv, uv, ranks))
        assert all(abs(a - b) <= 4 * rank for a, b, rank in zip(tv, uv, ranks))
        controls.append([int(s), int(d)])

    # The global barycentric coordinates are the normalized known counts:
    # x=S*/8316, y=2D*/8316, h=(8316-S*-2D*)/8316.
    # Substitution gives x=1-n/4158, y=(4n-z)/16632, h=z/16632.
    # Hence 0<=n<=4158 and 0<=z<=4n are exactly enough for the scalar screen.
    assert source["boundary"]["known_domain"] == "0<=n3<=4158 and 0<=z11<=4n3"
    assert source["boundary"]["new_inequality_in_n3_z11_or_E0"] is None

    result = {
        "status": "INDEPENDENT_GENERAL_ROOT_TU_SPECTRAL_AUDIT_PASS",
        "source_sha256": digest(SOURCE),
        "checks": {
            "line_graph_Q2_relation_table": True,
            "mixed_moments_from_Q_BQ_Q2": True,
            "Lagrange_projectors_independent_of_producer_solver": True,
            "99_root_sum_substitution": True,
            "two_factor_residual_Gram": True,
            "Bernstein_certificate_exact_expansion": True,
            "aggregate_99_root_determinant_substitution": True,
            "operator_bounds_at_all_simplex_vertices": controls,
            "global_known_domain_equals_mean_simplex": True,
        },
        "conclusion": "NO_NEW_N3_Z11_OR_E0_INEQUALITY_FROM_THIS_SCALAR_LANE",
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
