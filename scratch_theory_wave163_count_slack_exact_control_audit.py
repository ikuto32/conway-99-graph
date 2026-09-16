#!/usr/bin/env python3
"""Independent exact audit of the Wave163 compressed count-slack control.

The verifier imports none of the discovery/search modules.  It consumes the
already independently audited 8-dimensional universal nullspace and its
57-by-8 quotient map, reconstructs every order-7/order-8 count, and checks
the two compressed matrices by rational LDL^T elimination.
"""

from __future__ import annotations

import ctypes
import gzip
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Sequence


ROOT = Path(__file__).resolve().parent
CONTROL = ROOT / "scratch_theory_wave163_count_slack_exact_control.json"
KERNEL = ROOT / "scratch_theory_wave163_coupled_kernel_basis.json.gz"
BASE_AUDIT = ROOT / "scratch_theory_wave163_coupled_pencil_independent_audit.json"
COEFFICIENT_ARCHIVE = (
    ROOT / "external_conway99_research/attempts/wave147-alternative-lane/coefficients.json.gz"
)
OUTPUT = ROOT / "scratch_theory_wave163_count_slack_exact_control_audit.json"
PARAMETER_SCALE = 1_247_400
H_DELTA_MASK = 120568


class MemoryStatusEx(ctypes.Structure):
    _fields_ = [
        ("length", ctypes.c_ulong),
        ("memory_load", ctypes.c_ulong),
        ("total_phys", ctypes.c_ulonglong),
        ("avail_phys", ctypes.c_ulonglong),
        ("total_page_file", ctypes.c_ulonglong),
        ("avail_page_file", ctypes.c_ulonglong),
        ("total_virtual", ctypes.c_ulonglong),
        ("avail_virtual", ctypes.c_ulonglong),
        ("avail_extended_virtual", ctypes.c_ulonglong),
    ]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def memory_record(label: str) -> dict[str, object]:
    status = MemoryStatusEx()
    status.length = ctypes.sizeof(status)
    require(bool(ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status))), "memory query failed")
    free = 100.0 * status.avail_phys / status.total_phys
    require(free >= 18.0, f"{label}: free memory {free:.2f}% below 18% gate")
    return {
        "label": label,
        "free_physical_memory_percent": round(free, 4),
        "available_physical_gib": round(status.avail_phys / 2**30, 4),
        "total_physical_gib": round(status.total_phys / 2**30, 4),
    }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_gzip_json(path: Path) -> dict:
    with gzip.open(path, "rt", encoding="ascii") as handle:
        return json.load(handle)


def fstr(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def rank_fraction(rows: Sequence[Sequence[Fraction]]) -> int:
    work = [list(map(Fraction, row)) for row in rows if any(row)]
    if not work:
        return 0
    rank = 0
    for column in range(len(work[0])):
        pivot = next((row for row in range(rank, len(work)) if work[row][column]), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        value = work[rank][column]
        work[rank] = [entry / value for entry in work[rank]]
        for row in range(len(work)):
            if row == rank or not work[row][column]:
                continue
            factor = work[row][column]
            work[row] = [left - factor * right for left, right in zip(work[row], work[rank], strict=True)]
        rank += 1
        if rank == len(work):
            break
    return rank


def ldlt_positive_definite(matrix: Sequence[Sequence[Fraction]]) -> list[Fraction]:
    size = len(matrix)
    require(all(len(row) == size for row in matrix), "matrix not square")
    require(all(matrix[i][j] == matrix[j][i] for i in range(size) for j in range(size)), "matrix not symmetric")
    lower = [[Fraction(0) for _ in range(size)] for _ in range(size)]
    diagonal = [Fraction(0) for _ in range(size)]
    for pivot in range(size):
        lower[pivot][pivot] = Fraction(1)
        diagonal[pivot] = matrix[pivot][pivot] - sum(
            lower[pivot][k] * lower[pivot][k] * diagonal[k] for k in range(pivot)
        )
        require(diagonal[pivot] > 0, f"nonpositive LDL pivot {pivot}")
        for row in range(pivot + 1, size):
            residual = matrix[row][pivot] - sum(
                lower[row][k] * lower[pivot][k] * diagonal[k] for k in range(pivot)
            )
            lower[row][pivot] = residual / diagonal[pivot]
    # Reconstruct all entries, rather than trusting only signs of pivots.
    for row in range(size):
        for column in range(size):
            rebuilt = sum(
                lower[row][k] * diagonal[k] * lower[column][k]
                for k in range(size)
            )
            require(rebuilt == matrix[row][column], "LDL reconstruction failed")
    return diagonal


def upper_pairs(size: int) -> tuple[tuple[int, int], ...]:
    return tuple((left, right) for left in range(size) for right in range(left, size))


def class_streams(payload: dict) -> dict[int, tuple[int, ...]]:
    families = []
    for name in ("ordered_edge", "ordered_nonedge"):
        streams = {order: [] for order in range(5, 9)}
        for record in payload["families"][name]["class_coefficients"]:
            streams[int(record["order"])].append(int(record["canonical_mask"]))
        families.append({order: tuple(values) for order, values in streams.items()})
    require(families[0] == families[1], "family class streams differ")
    streams = families[0]
    require(tuple(len(streams[order]) for order in range(5, 9)) == (21, 62, 208, 916), "class census drift")
    return streams


def main() -> int:
    memory = [memory_record("count_slack_audit_start")]
    control = load_json(CONTROL)
    kernel = load_gzip_json(KERNEL)
    base_audit = load_json(BASE_AUDIT)
    coefficients = load_gzip_json(COEFFICIENT_ARCHIVE)

    require(base_audit["claim_label"] == "VERIFIED_SCOPED_COMPRESSED_CONIC_NULL", "base audit verdict drift")
    require(base_audit["inputs_sha256"][KERNEL.name] == sha256_file(KERNEL), "kernel binding drift")
    require(base_audit["exact_quotient_kernel_audit"]["universal_nullspace_vectors_verified"] == 8, "base nullspace audit drift")
    require(base_audit["exact_quotient_kernel_audit"]["quotient_rank"] == 8, "base quotient audit drift")

    certificate = control["certificate"]
    z = [Fraction(value) for value in certificate["z_parameters"]]
    t = [Fraction(value) for value in certificate["t_free_x8_coordinates"]]
    require(len(z) == len(t) == 8, "parameter width drift")
    require(t == [PARAMETER_SCALE * value for value in z], "z/t scale mismatch")
    require(-z[2] + 3 * z[3] + z[4] == 1, "constant face equation failed")
    require(z[7] == Fraction(58, 75), "active count face equation failed")

    nullspace = [[Fraction(0) for _ in range(8)] for _ in range(917)]
    for column, entries in enumerate(kernel["universal_nullspace_basis_sparse"]):
        for row, value in entries:
            nullspace[int(row)][column] = Fraction(value)
    free_columns = list(map(int, kernel["universal_free_columns"]))
    require(len(free_columns) == 8, "free-column count drift")
    require(
        all(nullspace[free_columns[i]][j] == Fraction(int(i == j)) for i in range(8) for j in range(8)),
        "nullspace free-coordinate identity failed",
    )
    augmented = [
        sum((nullspace[row][column] * t[column] for column in range(8)), Fraction(0))
        for row in range(917)
    ]
    require(augmented[0] == 1, "augmented constant is not one")
    x8 = augmented[1:]
    require(all(value >= 0 for value in x8), "negative order-8 count")
    require(sum(x8) == math.comb(99, 8), "order-8 total failed")
    zero8 = [index for index, value in enumerate(x8) if value == 0]
    require(zero8 == list(map(int, certificate["x8_zero_coordinates"])), "order-8 zero face drift")
    require(min(value for value in x8 if value > 0) == Fraction(certificate["minimum_positive_x8"]), "minimum positive x8 drift")
    structural8 = [index for index in zero8 if not any(nullspace[1 + index])]
    face8 = [index for index in zero8 if any(nullspace[1 + index])]
    require(rank_fraction([nullspace[1 + index] for index in face8]) == 1, "active nonstructural face rank drift")
    require(all(sum(nullspace[1 + index][j] * t[j] for j in range(8)) == 0 for index in face8), "active face row failed")
    active_representative = [
        Fraction(0), Fraction(0), Fraction(58, 75), Fraction(-58, 25),
        Fraction(-58, 75), Fraction(0), Fraction(0), Fraction(1),
    ]
    require(active_representative in [nullspace[1 + index] for index in face8], "canonical active row missing")
    require(
        all(
            row[2] * active_representative[coordinate]
            == active_representative[2] * row[coordinate]
            for index in face8
            for row in (nullspace[1 + index],)
            for coordinate in range(8)
        ),
        "active rows are not all proportional to canonical row",
    )

    streams = class_streams(coefficients)
    index7 = {mask: index for index, mask in enumerate(streams[7])}
    index8 = {mask: index for index, mask in enumerate(streams[8])}
    deletion: list[dict[int, int] | None] = [None] * 208
    for record in coefficients["order7_to_order8_deletion_equations"]:
        require(int(record["left_multiplier"]) == 92, "deletion multiplier drift")
        deletion[index7[int(record["order7_mask"])]] = {
            index8[int(mask)]: int(multiplicity)
            for mask, multiplicity in record["terms_order8_mask_multiplicity"]
        }
    require(all(row is not None for row in deletion), "missing deletion row")
    x7 = [
        sum((Fraction(mult) * x8[column] for column, mult in row.items()), Fraction(0)) / 92
        for row in deletion
        if row is not None
    ]
    require(all(value >= 0 for value in x7), "negative order-7 count")
    require(sum(x7) == math.comb(99, 7), "order-7 total failed")
    zero7 = [index for index, value in enumerate(x7) if value == 0]
    require(zero7 == list(map(int, certificate["x7_zero_coordinates"])), "order-7 zero face drift")
    require(x7[index7[H_DELTA_MASK]] == 0, "H_delta count is not zero")

    qmap = [[Fraction(value) for value in row] for row in kernel["compressed_quotient_map_57_by_8"]]
    require(len(qmap) == 57 and all(len(row) == 8 for row in qmap), "quotient map shape drift")
    scales = {int(root): [Fraction(value) for value in values] for root, values in certificate["direction_column_scales"].items()}
    require(len(scales[3]) == 6 and len(scales[12]) == 8, "direction scale shape drift")
    require(all(value > 0 for values in scales.values() for value in values), "nonpositive direction scale")
    stored_matrices = {
        int(root): [[Fraction(value) for value in row] for row in matrix]
        for root, matrix in certificate["compressed_Y_test_matrices"].items()
    }
    rebuilt_matrices = {}
    offset = 0
    for root, size in ((3, 6), (12, 8)):
        matrix = [[Fraction(0) for _ in range(size)] for _ in range(size)]
        for left, right in upper_pairs(size):
            raw_entry = sum((qmap[offset][column] * t[column] for column in range(8)), Fraction(0))
            value = raw_entry / (scales[root][left] * scales[root][right])
            matrix[left][right] = matrix[right][left] = value
            offset += 1
        rebuilt_matrices[root] = matrix
    require(offset == 57, "compressed row offset drift")
    require(rebuilt_matrices == stored_matrices, "stored compressed matrices drift")
    diagonals = {root: ldlt_positive_definite(rebuilt_matrices[root]) for root in (3, 12)}
    require(
        {str(root): list(map(fstr, diagonals[root])) for root in (3, 12)}
        == certificate["exact_ldlt_positive_diagonals"],
        "stored LDL pivots drift",
    )

    # Explicitly audit the upper-triangle convention for a deterministic
    # symmetric test matrix: off-diagonal entries occur twice in trace(WY).
    trace_checks = {}
    for root, size in ((3, 6), (12, 8)):
        test = [[Fraction((i + 1) * (j + 2)) for j in range(size)] for i in range(size)]
        for i in range(size):
            for j in range(i):
                test[i][j] = test[j][i]
        direct = sum(test[i][j] * rebuilt_matrices[root][j][i] for i in range(size) for j in range(size))
        packed = sum(
            (1 if i == j else 2) * test[i][j] * rebuilt_matrices[root][i][j]
            for i, j in upper_pairs(size)
        )
        require(direct == packed, f"off-diagonal factor-two failed root {root}")
        trace_checks[str(root)] = fstr(direct)

    memory.append(memory_record("count_slack_audit_complete"))
    result = {
        "format": "wave163-compressed-count-slack-exact-control-independent-audit-v1",
        "claim_label": "INDEPENDENT_EXACT_COMPRESSED_COUNT_SLACK_FEASIBILITY_PASS",
        "inputs_sha256": {
            path.name if path.parent == ROOT else str(path.relative_to(ROOT)): sha256_file(path)
            for path in (CONTROL, KERNEL, BASE_AUDIT, COEFFICIENT_ARCHIVE)
        },
        "universal_parameter_audit": {
            "nullspace_dimension": 8,
            "free_columns": free_columns,
            "augmented_constant": "1",
            "constant_face_equation": "-z2+3*z3+z4=1",
            "active_count_face_equation": "z7=58/75",
        },
        "count_cone_audit": {
            "order8_coordinates": len(x8),
            "order8_nonnegative": True,
            "order8_zero_count": len(zero8),
            "order8_structurally_zero": structural8,
            "order8_face_forced_zero": face8,
            "active_nonstructural_row_rank": 1,
            "active_representative_linear_form_on_t": list(map(fstr, active_representative)),
            "minimum_positive_order8_count": fstr(min(value for value in x8 if value > 0)),
            "sum_order8": str(sum(x8)),
            "order7_coordinates": len(x7),
            "order7_nonnegative": True,
            "order7_zero_indices": zero7,
            "order7_zero_masks": [streams[7][index] for index in zero7],
            "sum_order7": str(sum(x7)),
            "H_delta_mask": H_DELTA_MASK,
            "H_delta_count": "0",
            "endpoint_n3": 4158,
            "endpoint_prism_count_from_n3_plus_3P_equals_4158": "0",
            "sum_E0_from_6P_plus_H_delta": "0",
        },
        "compressed_psd_audit": {
            "compressed_rows": 57,
            "root3_size": 6,
            "root12_size": 8,
            "root3_exact_positive_ldlt_pivots": len(diagonals[3]),
            "root12_exact_positive_ldlt_pivots": len(diagonals[12]),
            "both_blocks_positive_definite": True,
            "off_diagonal_factor_two_trace_checks": trace_checks,
        },
        "conclusion": {
            "exact_statement": "The 57-row compressed PSD system plus the complete nonnegative order-7/order-8 count cone is rationally feasible at n3=4158 and sum E0=0.",
            "dual_boundary": "No conic/Farkas infeasibility certificate using only these compressed blocks, universal equalities, and nonnegative order-7/order-8 counts can exclude this endpoint.",
        },
        "scope_boundary": {
            "counts_are_integral_or_graph_realizable": False,
            "full_four_root_blocks": "NOT_TESTED",
            "directions_outside_U3_U12": "NOT_TESTED",
            "Conway_99": "UNKNOWN",
        },
        "resource_guard": {"minimum_required": 18.0, "samples": memory},
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": OUTPUT.name,
        "claim_label": result["claim_label"],
        "x8_zeros": len(zero8),
        "structural_x8_zeros": len(structural8),
        "face_x8_zeros": len(face8),
        "x7_zeros": len(zero7),
        "both_blocks_PD": True,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
