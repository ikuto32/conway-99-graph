#!/usr/bin/env python3
"""Exact PSD factorization of the evaluated Wave163 root-3/root-12 blocks."""

from __future__ import annotations

import argparse
import ctypes
import gzip
import hashlib
import json
from fractions import Fraction
from pathlib import Path
from typing import Sequence


ROOT = Path(__file__).resolve().parent
MATRIX_INPUT = ROOT / "scratch_theory_wave163_count_slack_full_block_matrices.json.gz"
DISCOVERY_INPUT = ROOT / "scratch_theory_wave163_count_slack_full_block.json"
CONTROL_AUDIT = ROOT / "scratch_theory_wave163_count_slack_exact_control_audit.json"
OUTPUT = ROOT / "scratch_theory_wave163_count_slack_full_block_exact_psd.json"
INTEGER_MATRIX_INPUT = ROOT / "scratch_theory_wave163_integer_lattice_full_block_matrices.json.gz"
INTEGER_DISCOVERY_INPUT = ROOT / "scratch_theory_wave163_integer_lattice_full_block.json"
INTEGER_CONTROL_AUDIT = ROOT / "scratch_theory_wave163_integer_lattice_audit.json"
INTEGER_OUTPUT = ROOT / "scratch_theory_wave163_integer_lattice_full_block_exact_psd.json"


class MemoryStatusEx(ctypes.Structure):
    _fields_ = [
        ("length", ctypes.c_ulong), ("memory_load", ctypes.c_ulong),
        ("total_phys", ctypes.c_ulonglong), ("avail_phys", ctypes.c_ulonglong),
        ("total_page_file", ctypes.c_ulonglong), ("avail_page_file", ctypes.c_ulonglong),
        ("total_virtual", ctypes.c_ulonglong), ("avail_virtual", ctypes.c_ulonglong),
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


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()


def fstr(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def exact_pivoted_ldl(matrix: Sequence[Sequence[int]]) -> dict[str, object]:
    """Return M=L D L^T with rectangular L and positive diagonal D.

    Rows remain in the original flag order.  Pivot choices use exact residual
    diagonals; a final all-entry reconstruction is the certificate.
    """
    size = len(matrix)
    require(all(len(row) == size for row in matrix), "matrix is not square")
    require(all(matrix[i][j] == matrix[j][i] for i in range(size) for j in range(size)), "matrix not symmetric")
    lower: list[list[Fraction]] = [[] for _ in range(size)]
    diagonal: list[Fraction] = []
    pivots: list[int] = []
    remaining = set(range(size))
    while True:
        residual_diagonal = {
            index: Fraction(matrix[index][index]) - sum(
                lower[index][k] * lower[index][k] * diagonal[k]
                for k in range(len(diagonal))
            )
            for index in remaining
        }
        require(all(value >= 0 for value in residual_diagonal.values()), "negative exact Schur diagonal")
        positive = [index for index, value in residual_diagonal.items() if value > 0]
        if not positive:
            break
        # The largest exact residual keeps the rational factors relatively
        # small.  This choice affects efficiency, not correctness.
        pivot = max(positive, key=lambda index: residual_diagonal[index])
        d = residual_diagonal[pivot]
        old_rank = len(diagonal)
        column = []
        for row in range(size):
            residual = Fraction(matrix[row][pivot]) - sum(
                lower[row][k] * diagonal[k] * lower[pivot][k]
                for k in range(old_rank)
            )
            column.append(residual / d)
        require(column[pivot] == 1, "pivot normalization failed")
        for previous in pivots:
            require(column[previous] == 0, "new column leaked into previous pivot")
        for row in range(size):
            lower[row].append(column[row])
        diagonal.append(d)
        pivots.append(pivot)
        remaining.remove(pivot)

    require(all(value > 0 for value in diagonal), "nonpositive retained pivot")
    # Full exact reconstruction proves both PSD and the stated rank.
    for row in range(size):
        for column in range(size):
            rebuilt = sum(
                lower[row][k] * diagonal[k] * lower[column][k]
                for k in range(len(diagonal))
            )
            require(rebuilt == matrix[row][column], f"LDL reconstruction failed at {row},{column}")
    sparse_lower = [
        [[column, fstr(value)] for column, value in enumerate(row) if value]
        for row in lower
    ]
    return {
        "size": size,
        "rank": len(diagonal),
        "nullity": size - len(diagonal),
        "pivot_indices": pivots,
        "positive_diagonal": list(map(fstr, diagonal)),
        "rectangular_L_sparse_sha256": canonical_sha256(sparse_lower),
        "exact_reconstructed_entries": size * size,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--integer-control", action="store_true")
    args = parser.parse_args()
    matrix_input = INTEGER_MATRIX_INPUT if args.integer_control else MATRIX_INPUT
    discovery_input = INTEGER_DISCOVERY_INPUT if args.integer_control else DISCOVERY_INPUT
    control_audit_path = INTEGER_CONTROL_AUDIT if args.integer_control else CONTROL_AUDIT
    output_path = INTEGER_OUTPUT if args.integer_control else OUTPUT
    memory = [memory_record("full_block_exact_psd_start")]
    with gzip.open(matrix_input, "rt", encoding="ascii") as handle:
        matrices = json.load(handle)
    discovery = json.loads(discovery_input.read_text(encoding="utf-8"))
    control_audit = json.loads(control_audit_path.read_text(encoding="utf-8"))
    expected_control_claim = (
        "INDEPENDENT_EXACT_INTEGRAL_COMPRESSED_FEASIBILITY_PASS"
        if args.integer_control else "INDEPENDENT_EXACT_COMPRESSED_COUNT_SLACK_FEASIBILITY_PASS"
    )
    require(control_audit["claim_label"] == expected_control_claim, "control audit drift")
    require(discovery["method"]["evaluated_matrix_archive_sha256"] == sha256_file(matrix_input), "matrix archive binding drift")
    require(int(matrices["count_denominator_scale"]) == (1 if args.integer_control else 40_000), "matrix scale drift")
    discovery_by_root = {int(block["root_mask"]): block for block in discovery["root_blocks"]}
    certificates = {}
    for record in matrices["blocks"]:
        root = int(record["root_mask"])
        matrix = [[int(value) for value in row] for row in record["centered_matrix"]]
        require(canonical_sha256(matrix) == discovery_by_root[root]["centered_matrix_sha256"], "matrix hash drift")
        certificate = exact_pivoted_ldl(matrix)
        expected_rank = {3: 15, 12: 16}[root]
        require(certificate["rank"] == expected_rank, f"root {root} exact rank drift")
        certificates[str(root)] = certificate
        memory.append(memory_record(f"full_block_exact_psd_root_{root}"))
    require(set(certificates) == {"3", "12"}, "root set drift")
    result = {
        "format": "wave163-exact-control-full-root3-root12-psd-certificate-v1",
        "claim_label": "EXACT_FULL_ROOT3_ROOT12_PSD_PASS",
        "inputs_sha256": {
            matrix_input.name: sha256_file(matrix_input),
            discovery_input.name: sha256_file(discovery_input),
            control_audit_path.name: sha256_file(control_audit_path),
        },
        "certificates": certificates,
        "conclusion": {
            "root3": "exact PSD, rank 15, nullity 140",
            "root12": "exact PSD, rank 16, nullity 162",
            "negative_direction": "NONE IN EITHER FULL BLOCK AT THIS CONTROL",
            "cutting_plane_action": "No valid negative scalar cut can be extracted from these two blocks at this control.",
            "endpoint_exclusion": "NOT_ESTABLISHED",
        },
        "scope_boundary": {
            "other_seven_four_root_types": "NOT_TESTED_AT_THIS_CONTROL",
            "graph_realizability": "NOT_CLAIMED",
            "Conway_99": "UNKNOWN",
        },
        "resource_guard": {"minimum_required": 18.0, "samples": memory},
    }
    result["control_kind"] = "integer_lattice" if args.integer_control else "rational_rounding"
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": output_path.name,
        "claim_label": result["claim_label"],
        "ranks": {root: certificates[root]["rank"] for root in certificates},
        "nullities": {root: certificates[root]["nullity"] for root in certificates},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
