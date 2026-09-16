"""Independent arithmetic/proof-identity audit; no producer import or search."""

from fractions import Fraction as F
from itertools import combinations
import hashlib
import json
from pathlib import Path

SOURCE = Path("scratch_theory_uniform_compression_rounding.py")
NOTE = Path("scratch_theory_uniform_compression_rounding.md")
CERT = Path("scratch_theory_uniform_compression_rounding.json")
OUTPUT = Path("scratch_theory_uniform_compression_rounding_audit.json")


def multiply(left, right):
    return [[sum(left[i][k] * right[k][j] for k in range(len(right)))
             for j in range(len(right[0]))] for i in range(len(left))]


def transpose(matrix):
    return list(map(list, zip(*matrix)))


def phi(size, total):
    quotient, remainder = divmod(total, size)
    return (size - remainder) * quotient**2 + remainder * (quotient + 1)**2


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main():
    saved = json.loads(CERT.read_text(encoding="utf-8"))
    assert saved["source_sha256"] == sha(SOURCE)
    assert saved["status"] == "UNIFORM_COMPRESSION_ROUNDING_EXACT_ARITHMETIC_PASS"
    fibres = tuple(combinations(range(7), 2))
    labels = tuple((2 * a + p, 2 * b + q) for a, b in fibres for p in range(2) for q in range(2))
    ell = [[int(group in fibre) for group in range(7)] for fibre in fibres]
    incidence = [[int(label in pair) for pair in labels] for label in range(14)]
    ports = [[int(position // 4 == fibre) for fibre in range(21)] for position in range(84)]
    matching = [[int(i ^ 1 == j) for j in range(14)] for i in range(14)]
    assert multiply(transpose(ports), ports) == [[4 * int(i == j) for j in range(21)] for i in range(21)]
    assert multiply(transpose(ell), ell) == [[5 * int(i == j) + 1 for j in range(7)] for i in range(7)]
    nn = multiply(incidence, transpose(incidence))
    constant = [[F(1, 14)] * 14 for _ in range(14)]
    anti = [[F(int(i == j) - matching[i][j], 2) for j in range(14)] for i in range(14)]
    symmetric = [[F(int(i == j) + matching[i][j], 2) - F(1, 14) for j in range(14)] for i in range(14)]
    assert nn == [[24 * constant[i][j] + 12 * anti[i][j] + 10 * symmetric[i][j] for j in range(14)] for i in range(14)]
    # Formal BN^T = 2J - N^T(I+M) on each explicitly reconstructed subspace.
    lifted_rhs = [[2 - incidence[j][x] - incidence[j ^ 1][x] for j in range(14)] for x in range(84)]
    for projector, dimension, eigenvalue in ((constant, 1, 12), (anti, 7, 0), (symmetric, 6, -2)):
        assert multiply(projector, projector) == projector
        assert sum(projector[i][i] for i in range(14)) == dimension
        left = multiply(lifted_rhs, projector)
        lifted = multiply(transpose(incidence), projector)
        assert left == [[eigenvalue * value for value in row] for row in lifted]
    # On ker N, B^2+B=12I has roots 3,-4. Trace zero fixes multiplicities.
    assert 84 - (1 + 7 + 6) == 70
    assert 40 + 30 == 70 and 12 - 2 * 6 + 3 * 40 - 4 * 30 == 0
    h = [[F(len(set(a) & set(b)), 5) - F(1, 15) for b in fibres] for a in fibres]
    pi = [[int(i == j) - h[i][j] for j in range(21)] for i in range(21)]
    assert multiply(pi, pi) == pi and pi == transpose(pi)
    assert multiply(pi, ell) == [[0] * 7 for _ in range(21)]
    assert sum(pi[i][i] for i in range(21)) == 14
    assert multiply(multiply(incidence, ports), pi) == [[0] * 21 for _ in range(14)]
    fixed = [[F(8, 3) - 8 * h[i][j] for j in range(21)] for i in range(21)]
    assert multiply(fixed, ell) == [[16 - 8 * value for value in row] for row in ell]
    assert multiply(fixed, pi) == [[0] * 21 for _ in range(21)]
    assert sum(value**2 for row in fixed for value in row) == 2688
    g = [4 * e * e + phi(10, 16 - 4 * e) + phi(10, 32 + 2 * e) for e in range(5)]
    assert g == saved["row_bound"] == [132, 138, 156, 186, 224]
    slopes = [g[i + 1] - g[i] for i in range(4)]
    assert slopes == sorted(slopes) == [6, 18, 30, 38]
    # Supporting-line checks prove the 21-fibre optimum without a dynamic program.
    for q, slope in enumerate(slopes):
        assert all(g[e] >= g[q] + slope * (e - q) for e in range(5))
    defect_g = [4 * delta * delta + phi(10, -4 * delta) + phi(10, 2 * delta) for delta in range(5)]
    assert defect_g == [0, 10, 28, 58, 100]
    controls = saved["row_controls"]
    assert len(controls) == 5 and [row["delta"] for row in controls] == list(range(5))
    for row in controls:
        e, delta = row["e"], row["delta"]
        c, z = row["C_row"], row["Z_row"]
        assert e == 4 - delta and len(c) == len(z) == 21
        assert all(type(value) is int for value in c + z)
        assert all(0 <= value <= 16 for value in c)
        assert c[0] == 2 * e and sum(c) == 48
        assert multiply([c], ell) == [[8, 8, 16, 16, 16, 16, 16]]
        assert multiply([z], ell) == [[0] * 7]
        for j, fibre in enumerate(fibres):
            baseline = 8 if j == 0 else 0 if set(fibre) & {0, 1} else 4
            assert z[j] == baseline - c[j]
        assert sum(value**2 for value in c) == g[e] == row["row_square"]
        assert sum(value**2 for value in z) == defect_g[delta]
    computed, optional_exclusions = [], []
    for total in range(85):
        q, r = divmod(total, 21)
        lower = 21 * g[q] if r == 0 else (21 - r) * g[q] + r * g[q + 1]
        segment = min(total // 21, 3)
        intercepts = (2772, 2520, 2016, 1512)
        assert lower == intercepts[segment] + slopes[segment] * total
        average = [F(2 * total, 21), F(8, 5) - F(2 * total, 105), F(16, 5) + F(total, 105)]
        cbar = [[fixed[i][j] + F(total, 7) * pi[i][j] for j in range(21)] for i in range(21)]
        for i, a in enumerate(fibres):
            for j, b in enumerate(fibres):
                index = 0 if a == b else 1 if set(a) & set(b) else 2
                assert cbar[i][j] == average[index]
        average_square = 21 * average[0]**2 + 210 * average[1]**2 + 210 * average[2]**2
        assert average_square == 2688 + F(2 * total**2, 7)
        covariance = lower - average_square
        upper = 5376 - 8 * total
        assert covariance >= 0 and lower <= upper
        computed.append({"E0": total, "integer_trace_square_lower": lower,
                         "spectral_trace_square_upper": upper, "covariance_lower": str(covariance)})
        negative_count, residual = divmod(168 - 2 * total, 28)
        endpoints = [-16] * negative_count + [12] * (14 - negative_count)
        if residual:
            endpoints[negative_count] -= residual
        assert len(endpoints) == 14 and sum(endpoints) == 2 * total
        sharper_upper = upper - residual * (28 - residual)
        assert 2688 + sum(value**2 for value in endpoints) == sharper_upper
        if lower > sharper_upper:
            optional_exclusions.append(total)
    assert computed == saved["E0_bounds"]
    assert saved["at_E0_zero"] == {"trace_square_lower": 2772, "Cbar_trace_square": 2688, "mandatory_covariance": 84}
    assert optional_exclusions == [82, 83]
    result = {"status": "INDEPENDENT_UNIFORM_COMPRESSION_ROUNDING_AUDIT_PASS",
              "producer_imported": False, "graph_or_layer_search_used": False,
              "inputs_sha256": {str(path): sha(path) for path in (SOURCE, NOTE, CERT)},
              "incidence_and_projection_identities_checked": True,
              "outer_spectrum_graph_block_derivation_independently_reviewed": True,
              "outer_spectrum": {"12": 1, "3": 40, "0": 7, "-2": 6, "-4": 30},
              "explicit_row_controls_checked": 5, "integer_E0_values_checked": 85,
              "row_bound": g, "defect_row_bound": defect_g,
              "mandatory_covariance_at_zero": 84,
              "main_scalar_inequality_exclusions": [],
              "optional_fixed_14_eigenvalue_sharpening": {
                  "formula": "5376-8E-delta(28-delta), delta=(168-2E) mod 28",
                  "incompatible_with_B_at": optional_exclusions,
                  "new_inventory_or_layer_credit": 0,
                  "scope": "Separate analytic observation only; high layers 82 and 83 were already excluded by prior research. It gives no useful positive E0 lower bound."},
              "scope": "Universal necessary inequalities and arithmetic controls only. Row controls are not a symmetric matrix or graph. Scalar row-square bounds are implied when the integral compression entries and exact sums are already modeled. The graph-to-matrix implication is an independently reviewed mathematical proof, not a formally mechanized theorem.",
              "submission_txt_written": False}
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "row_controls": 5, "E0_values": 85,
                      "main_exclusions": [], "new_credited_exclusions": 0}, sort_keys=True))


if __name__ == "__main__":
    main()
