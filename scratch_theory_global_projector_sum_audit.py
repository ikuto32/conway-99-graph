"""Independent replay for scratch_theory_global_projector_sum.json.

No functions or modules are imported from the primary checker.  The K7
projector, triangle-incidence polynomial, trace identities, all 8,317
integer T cases, and the T=0 boundary are recomputed by separate formulas.
"""

from __future__ import annotations

import ctypes
import hashlib
import itertools
import json
import math
import time
from fractions import Fraction
from pathlib import Path
from typing import Sequence


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "scratch_theory_global_projector_sum.json"
SOURCE_CODE = HERE / "scratch_theory_global_projector_sum.py"
OUTPUT = HERE / "scratch_theory_global_projector_sum_audit.json"
MEMORY_FLOOR = 18.0


class Mem(ctypes.Structure):
    _fields_ = [
        ("length", ctypes.c_ulong),
        ("load", ctypes.c_ulong),
        ("total", ctypes.c_ulonglong),
        ("available", ctypes.c_ulonglong),
        ("page_total", ctypes.c_ulonglong),
        ("page_available", ctypes.c_ulonglong),
        ("virtual_total", ctypes.c_ulonglong),
        ("virtual_available", ctypes.c_ulonglong),
        ("extended", ctypes.c_ulonglong),
    ]


def free_memory(label: str) -> dict[str, object]:
    state = Mem()
    state.length = ctypes.sizeof(state)
    assert ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(state))
    percent = 100.0 * state.available / state.total
    assert percent >= MEMORY_FLOOR, (label, percent)
    return {"label": label, "free_physical_memory_percent": percent}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        while block := stream.read(1 << 20):
            value.update(block)
    return value.hexdigest()


def multiply(left: Sequence[Sequence[Fraction]], right: Sequence[Sequence[Fraction]]) -> list[list[Fraction]]:
    columns = tuple(zip(*right, strict=True))
    return [
        [sum((x * y for x, y in zip(row, column, strict=True)), Fraction()) for column in columns]
        for row in left
    ]


def collision_minimum(total: int, boxes: int) -> int:
    q, r = divmod(total, boxes)
    return boxes * q * (q - 1) // 2 + q * r


def square_minimum(total: int, boxes: int) -> int:
    q, r = divmod(total, boxes)
    return boxes * q * q + r * (2 * q + 1)


def parse_fraction(value: object) -> Fraction:
    return Fraction(str(value))


def main() -> int:
    begun = time.monotonic()
    memory = [free_memory("audit_start")]
    stored = json.loads(SOURCE.read_text(encoding="utf-8"))
    assert stored["status"] == "GLOBAL_PROJECTOR_SUM_EXACT_AUDIT_PASS_NO_POSITIVE_E0_BOUND"
    assert stored["parameters"]["M_shape"] == [2079, 99]
    assert stored["parameters"]["W_shape"] == [99, 693]
    for name, expected in stored["context_only_sha256"].items():
        assert digest(HERE / name) == expected

    # A second construction of Q uses only its three relation values.  The
    # multiplication below verifies idempotence entry by entry, rather than
    # using the inverse formula in the source checker.
    edges = tuple(itertools.combinations(range(7), 2))
    qmatrix: list[list[Fraction]] = []
    for first in edges:
        row = []
        for second in edges:
            intersection = len(set(first) & set(second))
            row.append(
                Fraction(2, 3)
                if first == second
                else (Fraction(-2, 15) if intersection else Fraction(1, 15))
            )
        qmatrix.append(row)
    assert multiply(qmatrix, qmatrix) == qmatrix
    assert all(sum(row) == 0 for row in qmatrix)
    assert sum(qmatrix[i][i] for i in range(21)) == 14
    assert stored["K7_support_projector"]["entries_support_coordinates"] == {
        "equal": "2/3",
        "overlap": "-2/15",
        "disjoint": "1/15",
    }

    # Expanding the oriented-triangle outer products first gives
    # p(A)=A^3+8A^2-23A+42I.  Evaluate at the three SRG eigenvalues and
    # independently interpolate alpha I+beta A+gamma J.
    polynomial = lambda x: x**3 + 8 * x**2 - 23 * x + 42
    eigenvalues = {"constant": polynomial(14), "plus3": polynomial(3), "minus4": polynomial(-4)}
    assert eigenvalues == {"constant": 4032, "plus3": 72, "minus4": 198}
    beta = Fraction(eigenvalues["plus3"] - eigenvalues["minus4"], 7)
    alpha = Fraction(eigenvalues["plus3"]) - 3 * beta
    gamma = Fraction(eigenvalues["constant"] - alpha - 14 * beta, 99)
    assert (alpha, beta, gamma) == (126, -18, 42)
    assert stored["root_group_incidence"]["reduced_gram"] == "WW^T=126I-18A+42J"
    assert stored["root_group_incidence"]["eigenvalues"] == {key: str(value) for key, value in eigenvalues.items()}

    # Direct relation-entry replay for S.  For h equal-support roots, shared
    # group incidence is 2h+overlap and the remaining eligible roots are
    # disjoint-support roots.
    lifted = (Fraction(1, 6), Fraction(-1, 30), Fraction(1, 60))
    for relation, eligible, common_groups, expected_constant in (
        ("edge", 72, 24, Fraction(0)),
        ("nonedge", 71, 42, Fraction(-11, 12)),
    ):
        values = []
        cap = common_groups // 2
        for h in range(cap + 1):
            counts = (h, common_groups - 2 * h, eligible - common_groups + h)
            assert all(count >= 0 for count in counts)
            values.append(sum(count * value for count, value in zip(counts, lifted, strict=True)))
            assert values[-1] == expected_constant + Fraction(h, 4), (relation, h)
    assert stored["summed_projector"]["exact_identity"] == "S=H/4-7I-(11/12)(J-I-A)"

    # Per-root outer-edge arithmetic.  e+o+d=504 and 2e+o=168.
    for e0 in range(85):
        overlap = 168 - 2 * e0
        disjoint = 336 + e0
        assert e0 + overlap + disjoint == 504
        trace_ap = 2 * (
            e0 * lifted[0] + overlap * lifted[1] + disjoint * lifted[2]
        )
        assert trace_ap == Fraction(e0, 2)
        assert Fraction(4 * 14, 7) + trace_ap / 7 == 8 + Fraction(e0, 14)
        assert Fraction(3 * 14, 7) - trace_ap / 7 == 6 - Fraction(e0, 14)

    # Re-expand tr(S^2) from S=H/4-7I-11N/12.  Here
    # tr(H)=tr(N^2)=8316 and tr(HN)=2(12474-T).
    s2_constant = (
        Fraction(723492, 16)
        + 49 * 99
        + Fraction(121 * 8316, 144)
        - Fraction(7 * 8316, 2)
        - Fraction(11 * 2 * 12474, 24)
    )
    assert s2_constant == Fraction(33033, 2)
    assert stored["summed_projector"]["square_trace"] == "tr(S^2)=K/4+33033/2+11T/12"

    # Independent coefficient extraction for the primitive pinching bound.
    # Four times [a(T)^2/54+b(T)^2/44-tr(S^2 without K/4)].
    def psd_k_bound(total: int) -> Fraction:
        plus_trace = Fraction(792) + Fraction(total, 14)
        minus_trace = Fraction(594) - Fraction(total, 14)
        return 4 * (
            plus_trace**2 / 54
            + minus_trace**2 / 44
            - s2_constant
            - Fraction(11 * total, 12)
        )

    minimum = 10**30
    minimizers = []
    maximum_integer_minus_psd = Fraction(-1)
    for total in range(8317):
        exact_polynomial = Fraction(12474 - 3 * total) + Fraction(total * total, 1188)
        assert psd_k_bound(total) == exact_polynomial
        integer_bound = collision_minimum(total, 693) + collision_minimum(12474 - total, 4158)
        assert integer_bound >= exact_polynomial
        maximum_integer_minus_psd = max(maximum_integer_minus_psd, integer_bound - exact_polynomial)
        if integer_bound < minimum:
            minimum, minimizers = integer_bound, [total]
        elif integer_bound == minimum:
            minimizers.append(total)
        # All second-moment consequences are compatible with the exact box.
        e2_min = square_minimum(total, 99)
        e2_box = 84**2 * (total // 84) + (total % 84) ** 2
        assert e2_min <= e2_box <= 84 * total
        assert 84 * total <= 931392 - 28 * total
    assert minimum == 10395 and minimizers == list(range(1386, 2080))

    # T=0 boundary, evaluated without the source checker's algebra class.
    # For X=aI+bA+cJ the eigenvalues are a+14b+99c,a+3b,a-4b.
    def relation_spectrum(coefficients: tuple[Fraction, Fraction, Fraction]) -> tuple[Fraction, Fraction, Fraction]:
        a, b, c = coefficients
        return a + 14 * b + 99 * c, a + 3 * b, a - 4 * b

    # 84I+3(J-I-A)=81I-3A+3J.
    h0_spectrum = relation_spectrum((Fraction(81), Fraction(-3), Fraction(3)))
    # 14I-(J-I-A)/6=(85I+A-J)/6.
    s0_spectrum = relation_spectrum((Fraction(85, 6), Fraction(1, 6), Fraction(-1, 6)))
    assert h0_spectrum == (336, 72, 93)
    assert s0_spectrum == (0, Fraction(44, 3), Fraction(27, 2))
    assert 54 * s0_spectrum[1] + 44 * s0_spectrum[2] == 1386
    assert 54 * s0_spectrum[1] ** 2 + 44 * s0_spectrum[2] ** 2 == 19635
    assert 4158 * math.comb(3, 2) == 12474
    assert psd_k_bound(0) == 12474
    assert square_minimum(0, 99) == 0
    assert stored["T_zero_boundary"]["passes_every_consequence_in_this_audit"] is True

    memory.append(free_memory("audit_complete"))
    result = {
        "status": "GLOBAL_PROJECTOR_SUM_INDEPENDENT_REPLAY_PASS",
        "input_sha256": {
            SOURCE.name: digest(SOURCE),
            SOURCE_CODE.name: digest(SOURCE_CODE),
        },
        "K7_projector_rebuilt_entrywise": True,
        "triangle_incidence_polynomial": "A^3+8A^2-23A+42I",
        "root_group_gram_interpolated": "126I-18A+42J",
        "root_group_gram_eigenvalues": {key: str(value) for key, value in eigenvalues.items()},
        "summed_projector_entry_identity_replayed": True,
        "per_root_E0_values_checked": 85,
        "per_root_block_traces_replayed": True,
        "trace_S_square_replayed": True,
        "all_integral_T_values_checked": 8317,
        "projector_pinching_polynomial_replayed": "K>=12474-3T+T^2/1188",
        "integer_collision_absolute_minimum": minimum,
        "integer_collision_minimizer_interval": [minimizers[0], minimizers[-1]],
        "maximum_integer_improvement_over_continuous_PSD_bound": str(maximum_integer_minus_psd),
        "E0_second_moment_compression_bound_redundant_for_all_T": True,
        "T_zero_boundary": {
            "H0_eigenvalues": [str(value) for value in h0_spectrum],
            "S0_eigenvalues": [str(value) for value in s0_spectrum],
            "K": 12474,
            "sum_E0_squared": 0,
            "passes_all_replayed_constraints": True,
            "binary_block_factorization_claimed": False,
        },
        "conclusion": "No positive pointwise or average E0 lower bound follows from the audited W/H/S, primitive pinching, integer collision, or E0 second-moment consequences.",
        "resource_guard": {
            "minimum_required_free_physical_memory_percent": MEMORY_FLOOR,
            "minimum_observed_free_physical_memory_percent": min(float(item["free_physical_memory_percent"]) for item in memory),
            "samples": memory,
            "elapsed_seconds": time.monotonic() - begun,
        },
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "output": str(OUTPUT)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
