"""Exact scalar boundary for the T=0 signed-projector consequences.

No graph is constructed.  The certificate is an abstract simultaneous
spectral table for a specified collection of necessary scalar conditions.
"""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from math import comb
from pathlib import Path


OUTPUT = Path("scratch_theory_k_projector_crosscentre_spectrum.json")
SOURCE = Path("scratch_theory_e0_zero_triangle_flag_relation.md")
TABLE = (
    ("constant", 1, 36),
    ("E", 9, -15), ("E", 26, -9), ("E", 9, -3),
    ("F", 22, -6), ("F", 10, -3), ("F", 134, 3), ("F", 20, 6),
)


def rational(value: Fraction | int) -> str:
    return str(Fraction(value))


def main() -> None:
    rows = []
    for sector, multiplicity, k in TABLE:
        e0 = int(sector == "constant")
        e = int(sector == "E")
        f = int(sector == "F")
        m = 21 * e
        p = m + k - 4
        z = 231 * e0 - 1 - p - k
        s = m + 12 + 2 * k
        schur = {
            "E0_E0": Fraction(e0, 231),
            "E0_E": Fraction(e, 231),
            "E0_F": Fraction(f, 231),
            "E_E": Fraction(s, 441),
            "E_F": Fraction(4, 21) - Fraction(e, 231) - Fraction(s, 441),
            "F_F": Fraction(47, 77) + Fraction(e0, 231)
                     + Fraction(2 * e, 231) + Fraction(s, 441),
        }
        assert all(value >= 0 for value in schur.values())
        rows.append({
            "sector": sector, "multiplicity": multiplicity,
            "K": k, "M": m, "P": p, "Z": z, "S": s,
            "schur_projector_expression_eigenvalues": {
                key: rational(value) for key, value in schur.items()},
        })

    def trace(**powers: int) -> int:
        result = 0
        for row in rows:
            value = row["multiplicity"]
            for name, power in powers.items():
                value *= row[name] ** power
            result += value
        return result

    traces = {
        "tr_M": trace(M=1), "tr_M2": trace(M=2),
        "tr_K": trace(K=1), "tr_K2": trace(K=2), "tr_K3": trace(K=3),
        "tr_P": trace(P=1), "tr_P2": trace(P=2),
        "tr_Z": trace(Z=1), "tr_Z2": trace(Z=2),
        "tr_MK": trace(M=1, K=1), "tr_PK": trace(P=1, K=1),
        "tr_MK2": trace(M=1, K=2),
        "tr_P3": trace(P=3), "tr_P2K": trace(P=2, K=1),
        "tr_PK2": trace(P=1, K=2),
        "tr_S": trace(S=1), "tr_S2": trace(S=2),
    }
    assert traces["tr_M"] == 924 and traces["tr_M2"] == 19404
    assert traces["tr_K"] == traces["tr_P"] == traces["tr_Z"] == 0
    assert traces["tr_K2"] == 8316 and traces["tr_P2"] == 7392
    assert traces["tr_Z2"] == 37422
    assert traces["tr_MK"] == -8316 and traces["tr_PK"] == 0
    assert traces["tr_K3"] == 0
    assert traces["tr_S"] == 3696 and traces["tr_S2"] == 74844
    q = Fraction(traces["tr_MK2"], 21)
    eta = q - 3564
    assert q == 4212 and eta == 648
    a, b, c, d = (traces[key] for key in ("tr_P3", "tr_P2K", "tr_PK2", "tr_K3"))
    assert a == d + 63 * q - 219912
    assert b == d + 42 * q - 174636
    assert c == d + 21 * q - 33264
    assert d / 6 + 7 * eta == 4158 + b / 6

    # All ten induced three-point colour profiles: P, K, and the zero relation Z.
    triangle_counts = {
        "PPP": a // 6,
        "PPK": b // 2,
        "PKK": c // 2,
        "KKK": d // 6,
    }
    assert a % 6 == b % 2 == c % 2 == d % 6 == 0
    triangle_counts["PPZ"] = 231 * comb(32, 2) - 3 * triangle_counts["PPP"] - triangle_counts["PPK"]
    triangle_counts["KKZ"] = 231 * comb(36, 2) - 3 * triangle_counts["KKK"] - triangle_counts["PKK"]
    triangle_counts["PKZ"] = 231 * 32 * 36 - 2 * triangle_counts["PPK"] - 2 * triangle_counts["PKK"]
    triangle_counts["PZZ"] = (3696 * 229 - 3 * triangle_counts["PPP"]
                                - 2 * triangle_counts["PPK"] - triangle_counts["PKK"]
                                - 2 * triangle_counts["PPZ"] - triangle_counts["PKZ"])
    triangle_counts["KZZ"] = (4158 * 229 - 3 * triangle_counts["KKK"]
                                - triangle_counts["PPK"] - 2 * triangle_counts["PKK"]
                                - 2 * triangle_counts["KKZ"] - triangle_counts["PKZ"])
    triangle_counts["ZZZ"] = comb(231, 3) - sum(triangle_counts.values())
    assert all(value >= 0 for value in triangle_counts.values())
    assert triangle_counts["ZZZ"] * 6 == trace(Z=3)
    schur_ranks = {
        key: sum(row["multiplicity"] for row in rows
                 if Fraction(row["schur_projector_expression_eigenvalues"][key]) > 0)
        for key in rows[0]["schur_projector_expression_eigenvalues"]
    }
    assert schur_ranks["E_E"] <= 44 * 45 // 2
    result = {
        "status": "EXACT_K_PROJECTOR_CROSSCENTRE_SPECTRAL_BOUNDARY_PASS",
        "source_note_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "scope": {
            "assumed_endpoint": "sum_r E0(r)=0",
            "certificate_type": "abstract simultaneous spectrum and scalar moment table",
            "entrywise_integral_M_or_graph_realization_claimed": False,
            "full_entrywise_S_equals_M_schur_M_realization_claimed": False,
            "ambient_order9_census_generated": False,
            "frozen_H8_regenerated": False,
        },
        "general_derivation": {
            "projectors": "E0=J/231, E=M/21, F=I-E0-E; ranks 1,44,186",
            "q": "tr(E K^2)",
            "eta": "q-3564 = ||EKE+9E||_F^2 + ||FKE||_F^2 >= 0",
            "cubic_identities": {
                "tr_P3": "6*tau_K+63*q-219912",
                "tr_P2K": "6*tau_K+42*q-174636",
                "tr_PK2": "6*tau_K+21*q-33264",
            },
            "exact_crosscentre_identity": "tau_K+7*eta=4158+tr(P^2 K)/6",
            "necessary_bound": "tau_K >= 4158-7*eta",
            "missing_sufficient_bound_for_positive_tau": "eta<594",
            "K_triangle_to_X_triangle_gap_remains": True,
        },
        "spectral_table": rows,
        "traces": traces,
        "q": rational(q), "eta": rational(eta), "tau_K": 0,
        "all_ten_induced_relation_triangle_counts": triangle_counts,
        "schur_expression_ranks": schur_ranks,
        "claim_boundary": (
            "The listed scalar identities, six Schur-projector PSD expressions, "
            "and induced relation-triple nonnegativity do not force tau_K>0. "
            "The table is not a counterexample to the complete entrywise "
            "signed-projector problem.  No compatible closed wedge or positive "
            "E0 bound follows from this bounded lane."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUTPUT), "q": str(q), "eta": str(eta),
                      "tau_K": 0, "relation_triples": triangle_counts}, indent=2))


if __name__ == "__main__":
    main()
