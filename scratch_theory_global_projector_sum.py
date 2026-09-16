"""Clean-room exact audit of the global rank-14 fibre-projector sum.

This script uses only the SRG parameter equations and elementary exact
linear algebra.  It does not import any discovery program and does not
enumerate the 916 order-eight graph classes.
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
from typing import Iterable, Sequence


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "scratch_theory_global_projector_sum.json"
CONTEXT = (
    ROOT / "scratch_theory_global_fibre_block_gram.json",
    ROOT / "scratch_theory_global_root_fusion_frame.json",
    ROOT / "scratch_root_e0_motif_first_moment_audit.json",
)
MEMORY_FLOOR_PERCENT = 18.0

V = 99
DEGREE = 14
LAMBDA = 1
MU = 2
M_PLUS = 54
M_MINUS = 44
EDGE_COUNT = V * DEGREE // 2
NONEDGE_COUNT = math.comb(V, 2) - EDGE_COUNT
OUTER_SIZE = V - DEGREE - 1
FIBRES_PER_ROOT = math.comb(7, 2)
FIBRE_SIZE = 4


class MemoryStatusEx(ctypes.Structure):
    _fields_ = [
        ("dwLength", ctypes.c_ulong),
        ("dwMemoryLoad", ctypes.c_ulong),
        ("ullTotalPhys", ctypes.c_ulonglong),
        ("ullAvailPhys", ctypes.c_ulonglong),
        ("ullTotalPageFile", ctypes.c_ulonglong),
        ("ullAvailPageFile", ctypes.c_ulonglong),
        ("ullTotalVirtual", ctypes.c_ulonglong),
        ("ullAvailVirtual", ctypes.c_ulonglong),
        ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
    ]


def memory_sample(label: str) -> dict[str, object]:
    status = MemoryStatusEx()
    status.dwLength = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise RuntimeError("GlobalMemoryStatusEx failed")
    free = 100.0 * status.ullAvailPhys / status.ullTotalPhys
    if free < MEMORY_FLOOR_PERCENT:
        raise MemoryError(f"18% memory gate failed at {label}: {free:.3f}%")
    return {
        "label": label,
        "free_physical_memory_percent": free,
        "available_physical_gib": status.ullAvailPhys / 2**30,
    }


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def fstr(value: Fraction | int) -> str:
    value = Fraction(value)
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def transpose(matrix: Sequence[Sequence[Fraction]]) -> list[list[Fraction]]:
    return [list(column) for column in zip(*matrix, strict=True)]


def matmul(
    left: Sequence[Sequence[Fraction]], right: Sequence[Sequence[Fraction]]
) -> list[list[Fraction]]:
    right_t = transpose(right)
    return [
        [sum((x * y for x, y in zip(row, column, strict=True)), Fraction(0)) for column in right_t]
        for row in left
    ]


def matrix_rank(matrix: Sequence[Sequence[Fraction]]) -> int:
    work = [list(map(Fraction, row)) for row in matrix]
    if not work:
        return 0
    rows, columns = len(work), len(work[0])
    pivot_row = 0
    for column in range(columns):
        pivot = next((row for row in range(pivot_row, rows) if work[row][column]), None)
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        scale = work[pivot_row][column]
        work[pivot_row] = [value / scale for value in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row or not work[row][column]:
                continue
            scale = work[row][column]
            work[row] = [
                value - scale * pivot_value
                for value, pivot_value in zip(work[row], work[pivot_row], strict=True)
            ]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def identity(order: int) -> list[list[Fraction]]:
    return [[Fraction(i == j) for j in range(order)] for i in range(order)]


def matrix_subtract(
    left: Sequence[Sequence[Fraction]], right: Sequence[Sequence[Fraction]]
) -> list[list[Fraction]]:
    return [
        [x - y for x, y in zip(left_row, right_row, strict=True)]
        for left_row, right_row in zip(left, right, strict=True)
    ]


# Coefficients of I,A,J in the Bose--Mesner algebra.
Algebra = tuple[Fraction, Fraction, Fraction]


def alg_add(*values: Algebra) -> Algebra:
    return tuple(sum(parts, Fraction(0)) for parts in zip(*values, strict=True))  # type: ignore[return-value]


def alg_scale(scale: Fraction | int, value: Algebra) -> Algebra:
    return tuple(Fraction(scale) * part for part in value)  # type: ignore[return-value]


def alg_mul(left: Algebra, right: Algebra) -> Algebra:
    x, y, z = left
    u, v, w = right
    return (
        x * u + 12 * y * v,
        x * v + y * u - y * v,
        x * w + z * u + 2 * y * v + 14 * (y * w + z * v) + 99 * z * w,
    )


def alg_eval(value: Algebra, adjacency_eigenvalue: int, j_eigenvalue: int) -> Fraction:
    return value[0] + adjacency_eigenvalue * value[1] + j_eigenvalue * value[2]


def alg_trace(value: Algebra) -> Fraction:
    return V * (value[0] + value[2])


def cmin(total: int, cells: int) -> int:
    quotient, remainder = divmod(total, cells)
    return cells * quotient * (quotient - 1) // 2 + remainder * quotient


def sqmin(total: int, cells: int) -> int:
    quotient, remainder = divmod(total, cells)
    return cells * quotient * quotient + remainder * (2 * quotient + 1)


def affine_projector_entry(eligible: int, shared_groups: int) -> tuple[Fraction, Fraction]:
    """Return constant and h coefficient after summing a lifted P_r entry."""
    same = Fraction(1, 6)
    overlap = Fraction(-1, 30)
    disjoint = Fraction(1, 60)
    # counts: equal=h, overlap=shared_groups-2h,
    # disjoint=eligible-shared_groups+h.
    constant = shared_groups * overlap + (eligible - shared_groups) * disjoint
    coefficient = same - 2 * overlap + disjoint
    return constant, coefficient


def main() -> int:
    started = time.monotonic()
    samples = [memory_sample("start")]
    require((EDGE_COUNT, NONEDGE_COUNT, OUTER_SIZE) == (693, 4158, 84), "parameter drift")

    # Exact K7 unsigned vertex-edge incidence and its orthogonal complement.
    supports = tuple(itertools.combinations(range(7), 2))
    incidence = [
        [Fraction(vertex in support) for support in supports] for vertex in range(7)
    ]
    gram7 = matmul(incidence, transpose(incidence))
    require(
        all(gram7[i][j] == (6 if i == j else 1) for i in range(7) for j in range(7)),
        "K7 incidence Gram drift",
    )
    gram7_inverse = [
        [Fraction(i == j, 5) - Fraction(1, 60) for j in range(7)] for i in range(7)
    ]
    require(matmul(gram7, gram7_inverse) == identity(7), "K7 Gram inverse failed")
    support_projector = matrix_subtract(
        identity(FIBRES_PER_ROOT),
        matmul(transpose(incidence), matmul(gram7_inverse, incidence)),
    )
    require(matmul(support_projector, support_projector) == support_projector, "Q^2 != Q")
    require(matrix_rank(support_projector) == 14, "support projector rank != 14")
    require(all(sum(row) == 0 for row in support_projector), "Q does not kill constants")
    relation_values: dict[str, set[Fraction]] = {"equal": set(), "overlap": set(), "disjoint": set()}
    relation_counts = {"equal": 0, "overlap": 0, "disjoint": 0}
    for i, support_i in enumerate(supports):
        for j, support_j in enumerate(supports):
            relation = "equal" if i == j else ("overlap" if set(support_i) & set(support_j) else "disjoint")
            relation_values[relation].add(support_projector[i][j])
            relation_counts[relation] += 1
    expected_q = {
        "equal": {Fraction(2, 3)},
        "overlap": {Fraction(-2, 15)},
        "disjoint": {Fraction(1, 15)},
    }
    require(relation_values == expected_q, "support-projector entry values drift")
    require(relation_counts == {"equal": 21, "overlap": 210, "disjoint": 210}, "support pair census")
    samples.append(memory_sample("support_projector"))

    # Derive the root-group Gram without a graph instance.  If C is the
    # vertex-triangle incidence, CC^T=7I+A.  For an oriented triangle
    # (r,t), its group column is (A-I)c_t-(A+I)e_r.  Summing its outer
    # products over r in t gives the following algebra expression.
    I: Algebra = (Fraction(1), Fraction(0), Fraction(0))
    A: Algebra = (Fraction(0), Fraction(1), Fraction(0))
    J: Algebra = (Fraction(0), Fraction(0), Fraction(1))
    plus = alg_add(A, I)
    minus = alg_add(A, alg_scale(-1, I))
    triangle_gram = alg_add(alg_scale(7, I), A)
    root_group_gram = alg_add(
        alg_scale(3, alg_mul(alg_mul(minus, triangle_gram), minus)),
        alg_scale(-1, alg_mul(alg_mul(minus, triangle_gram), plus)),
        alg_scale(-1, alg_mul(alg_mul(plus, triangle_gram), minus)),
        alg_scale(7, alg_mul(plus, plus)),
    )
    expected_root_group_gram: Algebra = (Fraction(126), Fraction(-18), Fraction(42))
    require(root_group_gram == expected_root_group_gram, "root-group Gram polynomial failed")
    require(alg_mul(A, A) == (Fraction(12), Fraction(-1), Fraction(2)), "SRG algebra drift")
    root_group_eigenvalues = {
        "constant": alg_eval(root_group_gram, 14, 99),
        "plus3": alg_eval(root_group_gram, 3, 0),
        "minus4": alg_eval(root_group_gram, -4, 0),
    }
    require(root_group_eigenvalues == {"constant": 4032, "plus3": 72, "minus4": 198}, "W Gram spectrum")

    edge_entry = affine_projector_entry(72, 24)
    nonedge_entry = affine_projector_entry(71, 42)
    require(edge_entry == (0, Fraction(1, 4)), "summed P edge entry")
    require(nonedge_entry == (Fraction(-11, 12), Fraction(1, 4)), "summed P nonedge entry")
    diagonal_entry = OUTER_SIZE * Fraction(2, 3) / FIBRE_SIZE
    require(diagonal_entry == 14, "summed P diagonal")

    # Primitive projectors, verified inside the SRG algebra.
    E0: Algebra = (Fraction(0), Fraction(0), Fraction(1, 99))
    Eplus: Algebra = (Fraction(4, 7), Fraction(1, 7), Fraction(-2, 77))
    Eminus: Algebra = (Fraction(3, 7), Fraction(-1, 7), Fraction(1, 63))
    require(alg_mul(E0, E0) == E0 and alg_mul(Eplus, Eplus) == Eplus and alg_mul(Eminus, Eminus) == Eminus, "primitive idempotence")
    require(alg_mul(Eplus, Eminus) == (0, 0, 0), "primitive orthogonality")
    require(alg_add(E0, Eplus, Eminus) == I, "primitive resolution")
    require((alg_trace(E0), alg_trace(Eplus), alg_trace(Eminus)) == (1, 54, 44), "primitive ranks")

    # Per-root edge-type census.  Each outer vertex has outer degree 12.
    # Each of seven root groups supports 24 outer vertices and exactly
    # 6+6+12=24 edges, so weighted shared-support incidence is 168.
    outer_edges = OUTER_SIZE * 12 // 2
    shared_group_edge_incidence = 7 * 24
    require((outer_edges, shared_group_edge_incidence) == (504, 168), "local outer census")
    # With e=E0(r): equal=e, overlap=168-2e, disjoint=336+e.
    trace_a_p_constant = 2 * (
        shared_group_edge_incidence * Fraction(-1, 30)
        + (outer_edges - shared_group_edge_incidence) * Fraction(1, 60)
    )
    trace_a_p_e_coefficient = 2 * (
        Fraction(1, 6) - 2 * Fraction(-1, 30) + Fraction(1, 60)
    )
    require((trace_a_p_constant, trace_a_p_e_coefficient) == (0, Fraction(1, 2)), "tr(A P_r)")

    # Global traces and square.  T=sum e_r and K=sum_{x<y} binom(H_xy,2).
    trace_s2_constant = (
        Fraction(723492, 16)
        + 49 * V
        + Fraction(121, 144) * 8316
        - Fraction(7, 2) * 8316
        - Fraction(11, 24) * (2 * 12474)
    )
    trace_s2_t = Fraction(11, 12)
    trace_s2_k = Fraction(1, 4)
    require(trace_s2_constant == Fraction(33033, 2), "tr(S^2) constant")

    # Frobenius pinching to the plus/minus primitive spaces.
    plus_trace_constant, plus_trace_t = Fraction(792), Fraction(1, 14)
    minus_trace_constant, minus_trace_t = Fraction(594), Fraction(-1, 14)
    rhs_constant = plus_trace_constant**2 / M_PLUS + minus_trace_constant**2 / M_MINUS
    rhs_t = (
        2 * plus_trace_constant * plus_trace_t / M_PLUS
        + 2 * minus_trace_constant * minus_trace_t / M_MINUS
    )
    rhs_t2 = plus_trace_t**2 / M_PLUS + minus_trace_t**2 / M_MINUS
    k_bound = (
        4 * (rhs_constant - trace_s2_constant),
        4 * (rhs_t - trace_s2_t),
        4 * rhs_t2,
    )
    require(k_bound == (Fraction(12474), Fraction(-3), Fraction(1, 1188)), "pinching K polynomial")

    integer_collision = []
    equality_minimum = []
    minimum_k: int | None = None
    for total_e0 in range(8317):
        bound = cmin(total_e0, EDGE_COUNT) + cmin(12474 - total_e0, NONEDGE_COUNT)
        psd_bound = Fraction(12474 - 3 * total_e0) + Fraction(total_e0 * total_e0, 1188)
        require(Fraction(bound) >= psd_bound, f"integer collision weaker at T={total_e0}")
        if minimum_k is None or bound < minimum_k:
            minimum_k = bound
            equality_minimum = [total_e0]
        elif bound == minimum_k:
            equality_minimum.append(total_e0)
        if total_e0 in (0, 1, 693, 1386, 2079, 4158, 8316):
            integer_collision.append(
                {
                    "T": total_e0,
                    "integer_K_lower": bound,
                    "PSD_K_lower": fstr(psd_bound),
                    "sum_E0_square_lower": sqmin(total_e0, V),
                    "sum_E0_square_upper": 84**2 * (total_e0 // 84) + (total_e0 % 84) ** 2,
                }
            )
    require(minimum_k == 10395, "absolute K minimum")
    require(equality_minimum == list(range(1386, 2080)), "K equality interval")

    # The individual primitive compressions also expose the second moment.
    # a_r=8+e_r/14, b_r=6-e_r/14.  Because each compression is a
    # rank-at-most-14 positive contraction, sum tr(B_r^2)<=sum tr(B_r)
    # yields E2<=931392-28T.  The elementary e_r^2<=84e_r is always stronger.
    for total_e0 in range(8317):
        require(84 * total_e0 <= 931392 - 28 * total_e0, "compression unexpectedly strengthens E2")

    # The exact T=0 relation-algebra boundary.
    Nmat = alg_add(J, alg_scale(-1, I), alg_scale(-1, A))
    H0 = alg_add(alg_scale(84, I), alg_scale(3, Nmat))
    S0 = alg_add(alg_scale(Fraction(1, 4), H0), alg_scale(-7, I), alg_scale(Fraction(-11, 12), Nmat))
    h0_eigen = {
        "constant": alg_eval(H0, 14, 99),
        "plus3": alg_eval(H0, 3, 0),
        "minus4": alg_eval(H0, -4, 0),
    }
    s0_eigen = {
        "constant": alg_eval(S0, 14, 99),
        "plus3": alg_eval(S0, 3, 0),
        "minus4": alg_eval(S0, -4, 0),
    }
    require(h0_eigen == {"constant": 336, "plus3": 72, "minus4": 93}, "H0 spectrum")
    require(s0_eigen == {"constant": 0, "plus3": Fraction(44, 3), "minus4": Fraction(27, 2)}, "S0 spectrum")
    h0_collision = NONEDGE_COUNT * math.comb(3, 2)
    s0_square = M_PLUS * s0_eigen["plus3"] ** 2 + M_MINUS * s0_eigen["minus4"] ** 2
    require(h0_collision == 12474 and s0_square == 19635, "H0 energy")
    s0_pointwise_square = Fraction(14**2) + OUTER_SIZE * Fraction(1, 6) ** 2
    require(V * s0_pointwise_square == s0_square, "H0 pointwise/global square")

    samples.append(memory_sample("complete"))
    context_hashes = {path.name: sha256_file(path) for path in CONTEXT if path.exists()}
    result = {
        "status": "GLOBAL_PROJECTOR_SUM_EXACT_AUDIT_PASS_NO_POSITIVE_E0_BOUND",
        "format": "global-rank14-fibre-projector-sum-v1",
        "scope": "SRG parameter-level and projector/incidence consequences; no 916-class regeneration and no binary M factorization claim",
        "context_only_sha256": context_hashes,
        "parameters": {
            "srg": [99, 14, 1, 2],
            "M_shape": [2079, 99],
            "W_shape": [99, 693],
            "fibres_per_root": 21,
            "fibre_size": 4,
            "outer_vertices_per_root": 84,
        },
        "K7_support_projector": {
            "formula": "Q=I-R^T(5I+J)^(-1)R, (5I+J)^(-1)=I/5-J/60",
            "rank": matrix_rank(support_projector),
            "idempotent": True,
            "kills_constants": True,
            "entries_support_coordinates": {key: fstr(next(iter(value))) for key, value in relation_values.items()},
            "entries_lifted_to_four_vertex_fibres": {"equal": "1/6", "overlap": "-1/30", "disjoint": "1/60"},
            "ordered_relation_counts": relation_counts,
        },
        "root_group_incidence": {
            "oriented_triangle_column": "w_(r,t)=(A-I)c_t-(A+I)e_r",
            "triangle_incidence_gram": "CC^T=7I+A",
            "direct_outer_product_sum_before_SRG_reduction": "3(A-I)(7I+A)(A-I)-(A-I)(7I+A)(A+I)-(A+I)(7I+A)(A-I)+7(A+I)^2",
            "reduced_gram": "WW^T=126I-18A+42J",
            "entry_values": {"diagonal": 168, "edge": 24, "nonedge": 42},
            "eigenvalues": {key: fstr(value) for key, value in root_group_eigenvalues.items()},
            "eligible_common_outer_roots": {"edge": 72, "nonedge": 71},
            "support_relation_counts_given_h": {
                "edge": {"equal": "h", "overlap": "24-2h", "disjoint": "48+h"},
                "nonedge": {"equal": "h", "overlap": "42-2h", "disjoint": "29+h"},
            },
            "H_entry_caps_from_nonnegative_overlap": {"edge": 12, "nonedge": 21},
        },
        "summed_projector": {
            "definition": "S=sum_r P_r",
            "exact_identity": "S=H/4-7I-(11/12)(J-I-A)",
            "entry_derivation": {"diagonal": "14", "edge": "H_xy/4", "nonedge": "H_xy/4-11/12"},
            "PSD": True,
            "operator_interval": "0<=S<=84I, since P_r is dominated by its outer-support coordinate projector and every vertex is outer for 84 roots",
            "kills_constants": True,
            "trace": 1386,
            "primitive_block_traces": {"plus3": "792+T/14", "minus4": "594-T/14"},
            "square_trace": "tr(S^2)=K/4+33033/2+11T/12",
            "primitive_pinching": "K>=12474-3T+T^2/1188",
        },
        "per_root_E0": {
            "outer_edge_counts": {"total": 504, "equal_support": "e_r", "overlap_support": "168-2e_r", "disjoint_support": "336+e_r"},
            "trace_A_Pr": "e_r/2",
            "primitive_block_traces": {"plus3": "8+e_r/14", "minus4": "6-e_r/14"},
            "pointwise_consequence": "0<=e_r<=84; no strictly positive lower bound",
            "sum_definition": "T=sum_r e_r",
            "second_moment_integer_interval": "sqmin(T,99)<=sum_r e_r^2<=84T, with exact box maximum 84^2 floor(T/84)+(T mod 84)^2",
            "block_trace_square_identities": {
                "sum_plus_trace_squared": "6336+8T/7+(sum e_r^2)/196",
                "sum_minus_trace_squared": "3564-6T/7+(sum e_r^2)/196",
            },
            "positive_contraction_upper_bound": "sum e_r^2<=931392-28T",
            "comparison": "84T<=931392-28T for every 0<=T<=8316, so the compression bound is redundant",
        },
        "integer_H_and_collisions": {
            "definition": "K=sum_(x<y) binom(H_xy,2)",
            "energy_identity": "tr(H^2)=723492+4K",
            "integer_lower_bound": "K>=cmin(T,693)+cmin(12474-T,4158)",
            "absolute_minimum": minimum_k,
            "minimum_T_interval": [equality_minimum[0], equality_minimum[-1]],
            "integer_bound_dominates_projector_pinching_for_all_8317_T": True,
            "samples": integer_collision,
        },
        "pointwise_S_row": {
            "definitions": "t_x=sum_(y~x)H_xy; sum over nonedges in row x is 252-t_x",
            "relation_row_sums": {"edge": "t_x/4", "nonedge": "-14-t_x/4"},
            "square_lower_bound": "(S^2)_xx>=196+t_x^2/224+(14+t_x/4)^2/84",
            "T_zero_value": fstr(s0_pointwise_square),
            "strict_positive_E0_consequence": False,
        },
        "T_zero_boundary": {
            "T": 0,
            "H0": "84I+3(J-I-A)",
            "H_entries": {"diagonal": 84, "edge": 0, "nonedge": 3},
            "H_eigenvalues": {key: fstr(value) for key, value in h0_eigen.items()},
            "S0": "14I-(J-I-A)/6",
            "S_eigenvalues": {key: fstr(value) for key, value in s0_eigen.items()},
            "S_PSD": True,
            "S_operator_bound_pass": True,
            "primitive_traces": {"plus3": 792, "minus4": 594},
            "tr_S_square": fstr(s0_square),
            "K": h0_collision,
            "integer_collision_bound_equality": True,
            "per_root_E0_forced_by_T_nonnegative": 0,
            "sum_E0_squared": 0,
            "support_counts": {
                "edge_pair": {"equal": 0, "overlap": 24, "disjoint": 48},
                "nonedge_pair": {"equal": 3, "overlap": 36, "disjoint": 32},
                "per_root_outer_edges_if_e_r_zero": {"equal": 0, "overlap": 168, "disjoint": 336},
            },
            "mod2": "H0 mod 2 is the complement adjacency: symmetric alternating with zero row sum, hence even rank at most 98",
            "passes_every_consequence_in_this_audit": True,
            "not_claimed": "existence of a binary 2079x99 block incidence M or a decomposition into the graph-derived P_r",
        },
        "conclusion": {
            "positive_pointwise_lower_bound_on_E0_r": False,
            "positive_average_lower_bound_on_T_over_99": False,
            "reason": "The exact T=0 relation-algebra boundary H0 passes WW^T compatibility counts, S PSD/operator/block-trace/square constraints, integer collision bounds, parity, and the complete second-moment bounds derived here.",
            "missing_step": "A constraint retaining the assignment of the 2079 fibre blocks to their 99 roots, or an actual binary/fibre-partition factorization, is needed to exclude H0.",
        },
        "resource_guard": {
            "minimum_required_free_physical_memory_percent": MEMORY_FLOOR_PERCENT,
            "minimum_observed_free_physical_memory_percent": min(float(sample["free_physical_memory_percent"]) for sample in samples),
            "samples": samples,
            "elapsed_seconds": time.monotonic() - started,
        },
    }
    OUTPUT.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "output": str(OUTPUT)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
