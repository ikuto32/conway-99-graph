"""Exact arithmetic audit of the self-contained rooted side bound.

This script checks the numerical and polynomial identities in
``scratch_root_side_bound_selfcontained.md``.  The combinatorial bijections
and the Schur-product proof are written out in that note; this program is a
small, dependency-free guard against transcription and divisibility errors.
It does not call a SAT solver and it does not assume a completed graph.
"""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path


OUTPUT = Path("scratch_root_side_bound_selfcontained.json")
SOURCE = Path(__file__)


def profile(q: int) -> tuple[int, int, int, int]:
    """Numbers of disjoint triangle partners with 0,1,2,3 cross edges."""
    return 20 + q, 180 - 3 * q, 3 * q, 12 - q


def main() -> None:
    # SRG spectrum: 14^1, 3^54, (-4)^44.
    f3 = (98 * 4 - 14) // 7
    fm4 = 98 - f3
    assert (f3, fm4) == (54, 44)
    assert 14 + 3 * f3 - 4 * fm4 == 0

    edges = 99 * 14 // 2
    triangles = edges // 3
    triangles_per_vertex = 14 // 2
    assert (edges, triangles, triangles_per_vertex) == (693, 231, 7)

    # Gamma eigenvalue, multiplicity, and the value of
    # C=Gamma^2-5Gamma-18I on that eigenspace.
    gamma_spectrum = [(18, 1), (7, 54), (0, 44), (-3, 132)]
    c_spectrum = [(g * g - 5 * g - 18, mult) for g, mult in gamma_spectrum]
    assert c_spectrum == [(216, 1), (-4, 54), (-18, 44), (6, 132)]

    # E=(3I+J-Gamma-C)/21 is the rank-44 zero-eigenspace projector.
    projector_values = []
    for index, ((g, mult), (c, _)) in enumerate(zip(gamma_spectrum, c_spectrum)):
        j = 231 if index == 0 else 0
        value = Fraction(3 + j - g - c, 21)
        projector_values.append((value, mult))
    assert projector_values == [
        (Fraction(0), 1),
        (Fraction(0), 54),
        (Fraction(1), 44),
        (Fraction(0), 132),
    ]

    profiles = []
    for q in range(13):
        a = profile(q)
        assert min(a) >= 0
        assert sum(a) == 212
        assert sum(r * a[r] for r in range(4)) == 216
        assert sum((r * (r - 1) // 2) * a[r] for r in range(4)) == 36
        # A row of M=21E has diagonal 4 and disjoint entries 1-r.
        cube_sum = 4**3 + sum(a[r] * (1 - r) ** 3 for r in range(4))
        assert cube_sum == 6 * (q - 2)
        profiles.append(
            {
                "q": q,
                "a0_a1_a2_a3": list(a),
                "row_cube_sum": cube_sum,
            }
        )

    # Integral lift.  W=M o M satisfies W=M (mod 2), and
    # D=(W-M)/2 has even diagonal (16-4)/2=6.
    m_values = [-2, -1, 0, 1, 4]
    assert all((m * m - m) % 2 == 0 for m in m_values)
    assert (4 * 4 - 4) // 2 == 6
    assert 6 % 2 == 0

    diagonal_count = triangles
    diagonal_floor = 4
    trace_floor = diagonal_count * diagonal_floor
    trace_coefficient = 84
    raw_delta_floor = (trace_floor + trace_coefficient - 1) // trace_coefficient
    # n3 and 693 are divisible by three, so their difference is too.
    divisible_delta_floor = (
        (raw_delta_floor + 3 - 1) // 3
    ) * 3
    n3_floor = 693 + divisible_delta_floor
    assert (trace_floor, raw_delta_floor, divisible_delta_floor, n3_floor) == (
        924,
        11,
        12,
        705,
    )

    # From n3+3P=4158, then sum_r S(r)=6P.
    prism_ceiling = (4158 - n3_floor) // 3
    total_side_ceiling = 6 * prism_ceiling
    minimum_root_side_ceiling = total_side_ceiling // 99
    assert (prism_ceiling, total_side_ceiling, minimum_root_side_ceiling) == (
        1151,
        6906,
        69,
    )
    assert 70 * 99 > total_side_ceiling

    result = {
        "status": "ARITHMETIC_VERIFIED",
        "scope": (
            "Exact arithmetic for a proof conditional only on the existence "
            "of an srg(99,14,1,2); no external n3 lower bound is assumed"
        ),
        "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest().upper(),
        "srg": {
            "parameters": [99, 14, 1, 2],
            "edges": edges,
            "triangles": triangles,
            "triangles_per_vertex": triangles_per_vertex,
            "adjacency_spectrum": [[14, 1], [3, f3], [-4, fm4]],
        },
        "triangle_intersection": {
            "vertex_count": triangles,
            "degree": 18,
            "spectrum": [list(row) for row in gamma_spectrum],
            "cross_edge_polynomial_spectrum": [list(row) for row in c_spectrum],
            "zero_projector_spectrum": [
                [str(value), mult] for value, mult in projector_values
            ],
            "row_profiles": profiles,
        },
        "schur_integral_lift": {
            "M_entry_values": m_values,
            "all_m_squared_congruent_m_mod_2": True,
            "D_diagonal": 6,
            "A4_diagonal_positive_multiple": 4,
            "diagonal_count": diagonal_count,
            "trace_floor": trace_floor,
            "trace_identity": "tr(A4)=84*(n3-693)",
            "raw_delta_floor": raw_delta_floor,
            "divisibility": "3 divides n3",
            "divisible_delta_floor": divisible_delta_floor,
            "n3_floor": n3_floor,
        },
        "prism_and_root_side": {
            "identity": "n3+3*P=4158",
            "prism_ceiling": prism_ceiling,
            "identity_root_sum": "sum_r S(r)=6*P",
            "total_side_ceiling": total_side_ceiling,
            "root_count": 99,
            "some_root_side_ceiling": minimum_root_side_ceiling,
            "strict_pigeonhole_check": "70*99=6930>6906",
        },
        "claim_boundary": {
            "combinatorial_arguments_machine_checked": False,
            "sat_solver_run": False,
            "formal_proof_certificate": False,
            "graph_constructed": False,
        },
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "n3_floor": n3_floor,
        "prism_ceiling": prism_ceiling,
        "total_side_ceiling": total_side_ceiling,
        "some_root_side_ceiling": minimum_root_side_ceiling,
        "output": str(OUTPUT),
    }))


if __name__ == "__main__":
    main()
