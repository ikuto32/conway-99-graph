#!/usr/bin/env python3
"""Recover the exact Wave163 quotient kernel and seek exact PSD elements.

This is the second (discovery) stage.  It consumes the frozen compressed-row
artifact from ``scratch_theory_wave163_coupled_pencil.py``.  Modular RREFs are
combined by CRT until the eight-dimensional nullspace of the universal
endpoint rows rationally reconstructs and verifies against every integer
row.  The resulting 8 x 57 exact quotient map is row-reduced over Q, giving
all 49 kernel directions.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any, Sequence

import scratch_theory_wave163_coupled_pencil as core


ROOT = Path(__file__).resolve().parent
COEFFICIENT_INPUT = ROOT / "scratch_theory_wave163_coupled_pencil_coefficients.json.gz"
DISCOVERY_INPUT = ROOT / "scratch_theory_wave163_coupled_pencil.json"
OUTPUT = ROOT / "scratch_theory_wave163_coupled_kernel.json"
KERNEL_OUTPUT = ROOT / "scratch_theory_wave163_coupled_kernel_basis.json.gz"

MAX_PRIMES = 40


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def fstr(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def is_prime_32(value: int) -> bool:
    if value < 2:
        return False
    for small in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if value == small:
            return True
        if value % small == 0:
            return False
    d = value - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for base in (2, 3, 5, 7, 11):
        x = pow(base, d, value)
        if x in (1, value - 1):
            continue
        for _ in range(s - 1):
            x = x * x % value
            if x == value - 1:
                break
        else:
            return False
    return True


def prime_stream() -> Sequence[int]:
    result = [1_000_000_007, 1_000_000_009]
    candidate = 999_999_999
    while len(result) < MAX_PRIMES:
        if is_prime_32(candidate):
            result.append(candidate)
        candidate -= 2
    return result


def universal_basis_mod(
    universal: Sequence[dict[int, int]], prime: int, width: int
) -> tuple[dict[int, dict[int, int]], dict[int, int], tuple[int, ...]]:
    frequencies = [0] * width
    for row in universal:
        for key in row:
            frequencies[key] += 1
    ordered = sorted(
        enumerate(universal), key=lambda item: (len(item[1]), min(item[1]), item[0])
    )
    basis: dict[int, dict[int, int]] = {}
    ages: dict[int, int] = {}
    for _, row in ordered:
        core.insert_sparse_row(row, prime, basis, ages, frequencies)
    free = tuple(column for column in range(width) if column not in basis)
    require(len(basis) == width - 8 and len(free) == 8, "universal modular nullity drift")
    return basis, ages, free


def nullspace_mod(
    basis: dict[int, dict[int, int]], free: Sequence[int], prime: int, width: int
) -> list[list[int]]:
    vectors = [[0] * len(free) for _ in range(width)]
    for local, column in enumerate(free):
        vectors[column][local] = 1
    pivots = tuple(basis)
    for pivot in reversed(pivots):
        row = basis[pivot]
        for local in range(len(free)):
            total = sum(
                value * vectors[column][local]
                for column, value in row.items()
                if column != pivot
            )
            vectors[pivot][local] = -total % prime
    return vectors


def crt_update(values: list[int], modulus: int, residues: Sequence[int], prime: int) -> int:
    inverse = pow(modulus % prime, -1, prime)
    for index, residue in enumerate(residues):
        multiplier = ((int(residue) - values[index]) % prime) * inverse % prime
        values[index] += modulus * multiplier
    return modulus * prime


def rational_reconstruct(residue: int, modulus: int) -> Fraction | None:
    """Classical symmetric rational reconstruction below sqrt(modulus/2)."""
    residue %= modulus
    if residue == 0:
        return Fraction(0)
    bound = math.isqrt(modulus // 2)
    old_r, r = modulus, residue
    old_t, t = 0, 1
    while r > bound:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_t, t = t, old_t - quotient * t
    if r == 0 or t == 0 or abs(t) > bound:
        return None
    numerator, denominator = r, t
    if denominator < 0:
        numerator, denominator = -numerator, -denominator
    divisor = math.gcd(abs(numerator), denominator)
    numerator //= divisor
    denominator //= divisor
    if math.gcd(denominator, modulus) != 1:
        return None
    if (residue * denominator - numerator) % modulus:
        return None
    return Fraction(numerator, denominator)


def reconstruct_all(values: Sequence[int], modulus: int) -> list[Fraction] | None:
    result = []
    for value in values:
        reconstructed = rational_reconstruct(value, modulus)
        if reconstructed is None:
            return None
        result.append(reconstructed)
    return result


def dot_sparse_fraction(row: dict[int, int], vector: Sequence[Fraction]) -> Fraction:
    return sum((Fraction(value) * vector[column] for column, value in row.items()), Fraction(0))


def verify_nullspace(
    universal: Sequence[dict[int, int]],
    vectors: Sequence[Sequence[Fraction]],
    free: Sequence[int],
) -> bool:
    width = len(vectors)
    nullity = len(free)
    for column in range(nullity):
        for position, free_column in enumerate(free):
            expected = Fraction(int(position == column))
            if vectors[free_column][column] != expected:
                return False
        dense = [vectors[row][column] for row in range(width)]
        if any(dot_sparse_fraction(equation, dense) for equation in universal):
            return False
    return True


def rref(matrix: Sequence[Sequence[Fraction]]) -> tuple[list[list[Fraction]], list[int]]:
    work = [list(map(Fraction, row)) for row in matrix]
    rows = len(work)
    columns = len(work[0]) if rows else 0
    pivots = []
    target_row = 0
    for column in range(columns):
        pivot = next((r for r in range(target_row, rows) if work[r][column]), None)
        if pivot is None:
            continue
        work[target_row], work[pivot] = work[pivot], work[target_row]
        value = work[target_row][column]
        work[target_row] = [entry / value for entry in work[target_row]]
        for row in range(rows):
            if row == target_row or not work[row][column]:
                continue
            factor = work[row][column]
            work[row] = [
                entry - factor * pivot_entry
                for entry, pivot_entry in zip(work[row], work[target_row], strict=True)
            ]
        pivots.append(column)
        target_row += 1
        if target_row == rows:
            break
    return work, pivots


def kernel_basis(equations: Sequence[Sequence[Fraction]]) -> tuple[list[list[Fraction]], list[int]]:
    reduced, pivots = rref(equations)
    columns = len(reduced[0])
    free = [column for column in range(columns) if column not in pivots]
    basis = []
    for free_column in free:
        vector = [Fraction(0)] * columns
        vector[free_column] = Fraction(1)
        for row, pivot in enumerate(pivots):
            vector[pivot] = -reduced[row][free_column]
        basis.append(vector)
    for vector in basis:
        require(
            all(
                sum((row[c] * vector[c] for c in range(columns)), Fraction(0)) == 0
                for row in equations
            ),
            "rational kernel verification failed",
        )
    return basis, pivots


def upper_pairs(size: int) -> list[tuple[int, int]]:
    return [(i, j) for i in range(size) for j in range(i, size)]


def coefficient_vector_to_matrices(vector: Sequence[Fraction]) -> tuple[list[list[Fraction]], list[list[Fraction]]]:
    result = []
    offset = 0
    for size in (6, 8):
        matrix = [[Fraction(0) for _ in range(size)] for _ in range(size)]
        for local, (left, right) in enumerate(upper_pairs(size)):
            coefficient = vector[offset + local]
            # <Y,C> uses coefficient Y_ii on a diagonal row and 2Y_ij on
            # an off-diagonal row.
            value = coefficient if left == right else coefficient / 2
            matrix[left][right] = matrix[right][left] = value
        result.append(matrix)
        offset += size * (size + 1) // 2
    require(offset == len(vector), "matrix unpack width mismatch")
    return result[0], result[1]


def ldlt_positive_definite(matrix: Sequence[Sequence[Fraction]]) -> tuple[bool, list[Fraction]]:
    size = len(matrix)
    lower = [[Fraction(0) for _ in range(size)] for _ in range(size)]
    diagonal = [Fraction(0)] * size
    for i in range(size):
        lower[i][i] = 1
        diagonal[i] = matrix[i][i] - sum(
            lower[i][k] * lower[i][k] * diagonal[k] for k in range(i)
        )
        if diagonal[i] <= 0:
            return False, diagonal[: i + 1]
        for j in range(i + 1, size):
            lower[j][i] = (
                matrix[j][i]
                - sum(lower[j][k] * lower[i][k] * diagonal[k] for k in range(i))
            ) / diagonal[i]
    return True, diagonal


def try_diagonal_free_candidate(
    reduced_equations: Sequence[Sequence[Fraction]], pivots: Sequence[int]
) -> dict[str, Any] | None:
    """A deterministic exact candidate: identity on all nonpivot diagonals."""
    width = len(reduced_equations[0])
    vector = [Fraction(0)] * width
    pairs = upper_pairs(6) + upper_pairs(8)
    for column, (left, right) in enumerate(pairs):
        if column not in pivots and left == right:
            vector[column] = 1
    for row, pivot in enumerate(pivots):
        vector[pivot] = -sum(
            reduced_equations[row][column] * vector[column]
            for column in range(width)
            if column != pivot
        )
    matrices = coefficient_vector_to_matrices(vector)
    certificates = [ldlt_positive_definite(matrix) for matrix in matrices]
    if not all(status for status, _ in certificates):
        return None
    return {
        "construction": "all nonpivot diagonal Y entries set to one; off-diagonals zero; pivot coefficients solved exactly",
        "coefficient_vector": [fstr(value) for value in vector],
        "Y3": [[fstr(value) for value in row] for row in matrices[0]],
        "Y12": [[fstr(value) for value in row] for row in matrices[1]],
        "ldlt_positive_diagonals": [
            [fstr(value) for value in diagonal] for _, diagonal in certificates
        ],
    }


def main() -> int:
    memory = [core.memory_record("kernel_recovery_start")]
    coefficient_payload = core.load_gzip_json(core.COEFFICIENT_ARCHIVE)
    marked = core.load_gzip_json(core.MARKED_ARCHIVE)
    row_system = core.load_json(core.ROW_SYSTEM)
    streams = core.class_streams(coefficient_payload)
    universal, labels, deletion = core.universal_reduced_rows(
        coefficient_payload, marked, row_system, streams[7], streams[8]
    )
    coefficient_artifact = core.load_gzip_json(COEFFICIENT_INPUT)
    compressed_records = coefficient_artifact["rows"]
    index7 = {mask: index for index, mask in enumerate(streams[7])}
    index8 = {mask: index for index, mask in enumerate(streams[8])}
    compressed = [
        core.eliminate_x7(*core.row_maps(row), index7, index8, deletion)
        for row in compressed_records
    ]
    width = 1 + len(streams[8])
    # The 208 deletion equations have already been used as coordinate
    # pivots; the remaining reduced list has 5556-893=4663 nonzero rows.
    require((len(universal), len(compressed), width) == (4663, 57, 917), "input dimensions drift")

    crt_values = [0] * (width * 8)
    modulus = 1
    free_reference: tuple[int, ...] | None = None
    exact_nullspace: list[list[Fraction]] | None = None
    primes_used = []
    reconstruction_attempts = []
    for prime in prime_stream():
        memory.append(core.memory_record(f"before_kernel_prime_{prime}"))
        basis, ages, free = universal_basis_mod(universal, prime, width)
        if free_reference is None:
            free_reference = free
        require(free == free_reference, "modular pivot/free-column pattern changed")
        vectors_mod = nullspace_mod(basis, free, prime, width)
        flat = [value for row in vectors_mod for value in row]
        modulus = crt_update(crt_values, modulus, flat, prime)
        primes_used.append(prime)
        memory.append(core.memory_record(f"after_kernel_prime_{prime}"))
        if len(primes_used) < 3:
            continue
        reconstructed = reconstruct_all(crt_values, modulus)
        if reconstructed is None:
            reconstruction_attempts.append({"primes": len(primes_used), "status": "bounds_not_met"})
            continue
        candidate = [
            reconstructed[row * 8 : (row + 1) * 8] for row in range(width)
        ]
        verified = verify_nullspace(universal, candidate, free)
        reconstruction_attempts.append(
            {"primes": len(primes_used), "status": "verified" if verified else "spurious_reconstruction"}
        )
        if verified:
            exact_nullspace = candidate
            break
    require(exact_nullspace is not None and free_reference is not None, "rational nullspace reconstruction failed")

    quotient_map = []
    for row in compressed:
        quotient_map.append(
            [
                dot_sparse_fraction(row, [exact_nullspace[i][column] for i in range(width)])
                for column in range(8)
            ]
        )
    equations = [
        [quotient_map[row][column] for row in range(57)]
        for column in range(8)
    ]
    kernel, quotient_pivots = kernel_basis(equations)
    require(len(quotient_pivots) == 8 and len(kernel) == 49, "exact quotient rank/nullity drift")
    reduced_equations, repeated_pivots = rref(equations)
    require(repeated_pivots == quotient_pivots, "RREF pivot instability")

    psd_candidate = try_diagonal_free_candidate(reduced_equations, quotient_pivots)

    nullspace_sparse = []
    for column in range(8):
        entries = [
            [row, fstr(exact_nullspace[row][column])]
            for row in range(width)
            if exact_nullspace[row][column]
        ]
        nullspace_sparse.append(entries)
    kernel_sparse = [
        [[column, fstr(value)] for column, value in enumerate(vector) if value]
        for vector in kernel
    ]
    kernel_core = {
        "format": "wave163-exact-compressed-quotient-kernel-v1",
        "coefficient_input_sha256": core.sha256_file(COEFFICIENT_INPUT),
        "universal_free_columns": list(free_reference),
        "universal_nullspace_basis_sparse": nullspace_sparse,
        "compressed_quotient_map_57_by_8": [
            [fstr(value) for value in row] for row in quotient_map
        ],
        "quotient_equation_pivot_coordinates": quotient_pivots,
        "kernel_basis_sparse": kernel_sparse,
        "upper_triangle_convention": {
            "root3_rows": upper_pairs(6),
            "root12_rows": upper_pairs(8),
            "linear_coefficient": "Y_ii on diagonal C_ii; 2*Y_ij on off-diagonal C_ij",
        },
    }
    kernel_bytes = gzip.compress(core.canonical_bytes(kernel_core), compresslevel=9, mtime=0)

    result = {
        "format": "wave163-exact-compressed-kernel-recovery-v1",
        "claim_label": "EXACT_PSD_KERNEL_FOUND" if psd_candidate else "EXACT_KERNEL_PSD_UNRESOLVED",
        "inputs": {
            str(COEFFICIENT_INPUT.name): core.sha256_file(COEFFICIENT_INPUT),
            str(DISCOVERY_INPUT.name): core.sha256_file(DISCOVERY_INPUT),
            **{
                str(path.relative_to(ROOT)): core.sha256_file(path)
                for path in (core.COEFFICIENT_ARCHIVE, core.MARKED_ARCHIVE, core.ROW_SYSTEM)
            },
        },
        "crt_rational_reconstruction": {
            "primes_used": primes_used,
            "combined_modulus_decimal_digits": len(str(modulus)),
            "attempts": reconstruction_attempts,
            "universal_integer_rows_verified": len(universal),
            "nullspace_dimension_verified": 8,
            "free_columns": list(free_reference),
        },
        "exact_quotient": {
            "compressed_rows": 57,
            "rank": len(quotient_pivots),
            "kernel_dimension": len(kernel),
            "pivot_coordinates": quotient_pivots,
            "kernel_basis_vectors_verified": len(kernel),
            "kernel_artifact": str(KERNEL_OUTPUT.name),
            "kernel_payload_sha256": core.canonical_sha256(kernel_core),
            "kernel_gzip_sha256": hashlib.sha256(kernel_bytes).hexdigest(),
            "kernel_gzip_bytes": len(kernel_bytes),
        },
        "psd_kernel": psd_candidate or {
            "status": "deterministic diagonal-free candidate was not positive definite; further exact cone analysis required"
        },
        "boundary": {
            "affine_kernel_exists": True,
            "fixed_x7_or_pair_root_zero_used": False,
            "count_slacks_used": False,
            "full_four_root_sdp_run": False,
            "Conway_99": "UNKNOWN",
        },
        "resource_guard": {
            "minimum_free_physical_memory_percent_required": 18.0,
            "samples": memory,
            "minimum_observed_free_physical_memory_percent": min(
                float(item["free_physical_memory_percent"]) for item in memory
            ),
        },
    }
    KERNEL_OUTPUT.write_bytes(kernel_bytes)
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(OUTPUT),
        "kernel_output": str(KERNEL_OUTPUT),
        "claim_label": result["claim_label"],
        "primes_used": primes_used,
        "exact_rank": len(quotient_pivots),
        "kernel_dimension": len(kernel),
        "psd_candidate": psd_candidate is not None,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
