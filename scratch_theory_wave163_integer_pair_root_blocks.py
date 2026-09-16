#!/usr/bin/env python3
"""Evaluate all 2,414 frozen Wave147 matrices at the integer Wave163 control."""

from __future__ import annotations

import ast
import gzip
import hashlib
import json
import math
import time
from fractions import Fraction
from pathlib import Path
from typing import Sequence

import numpy as np

import scratch_theory_wave163_coupled_pencil as pencil


ROOT = Path(__file__).resolve().parent
COEFFICIENTS = pencil.COEFFICIENT_ARCHIVE
W147_RESULT = pencil.W147_RESULT
SIX_SOURCE = ROOT / "external_conway99_research/verification/wave43-seven-deck-endpoint/independent_check.py"
SIX_RESULT = ROOT / "external_conway99_research/verification/wave43-seven-deck-endpoint/independent-result.json"
INTEGER_CONTROL = ROOT / "scratch_theory_wave163_integer_lattice.json"
KERNEL = ROOT / "scratch_theory_wave163_coupled_kernel_basis.json.gz"
OUTPUT = ROOT / "scratch_theory_wave163_integer_pair_root_blocks.json"
MATRIX_OUTPUT = ROOT / "scratch_theory_wave163_integer_pair_root_blocks_matrices.json.gz"
M_TO_CANONICAL_POSITIONS = (
    0, 1, 2, 6, 3, 9, 7, 5, 4, 12, 10, 8, 13, 16, 15, 14, 11, 19, 18, 20, 17
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()


def source_six_masks() -> tuple[int, ...]:
    tree = ast.parse(SIX_SOURCE.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "SOURCE_N_MASKS" for target in node.targets):
            return tuple(map(int, ast.literal_eval(node.value)))
    raise AssertionError("SOURCE_N_MASKS missing")


def five_counts() -> tuple[int, ...]:
    n, k = 99, 14
    common = n * k * (k - 2)
    values = (
        Fraction(common * (k - 4) * (n - 4 * k + 6) * (k**3 - 6 * k**2 + 14 * k - 36), 960),
        Fraction(common * (k - 4) ** 2 * (k**3 - 8 * k**2 + 26 * k - 48), 96),
        Fraction(common * (k - 4) * (k**3 - 10 * k**2 + 38 * k - 60), 16),
        Fraction(common * (k - 4) * (k**3 - 10 * k**2 + 40 * k - 68), 32),
        Fraction(common * (k - 4) * (n - 4 * k + 8), 6),
        Fraction(common * (k - 4) * (k**2 - 8 * k + 20), 8),
        Fraction(common * (k - 4) * (k**2 - 7 * k + 16), 4),
        Fraction(common * (k - 4) * (n - 4 * k + 8), 24),
        Fraction(common * (k - 4) * (k - 6), 24),
        Fraction(common * (n - 4 * k + 8), 8),
        Fraction(common * (k - 4) ** 2, 2),
        Fraction(common * (k - 4) ** 2, 4),
        Fraction(common * (k**2 - 8 * k + 17), 2),
        Fraction(common * (k - 4) * (k - 6), 24),
        Fraction(common * (k - 4), 2),
        Fraction(common * (k - 3), 2),
        Fraction(common * (k - 4), 4),
        Fraction(common * (k - 4), 5),
        Fraction(common, 8),
        Fraction(common, 2),
        Fraction(common * (k - 4), 2),
    )
    require(all(value.denominator == 1 for value in values), "five-count nonintegral")
    return tuple(value.numerator for value in values)


def class_streams(payload: dict) -> dict[int, tuple[int, ...]]:
    families = []
    for name in ("ordered_edge", "ordered_nonedge"):
        streams = {order: [] for order in range(5, 9)}
        for record in payload["families"][name]["class_coefficients"]:
            streams[int(record["order"])].append(int(record["canonical_mask"]))
        families.append({order: tuple(values) for order, values in streams.items()})
    require(families[0] == families[1], "family stream mismatch")
    streams = families[0]
    require(tuple(len(streams[order]) for order in range(5, 9)) == (21, 62, 208, 916), "class census drift")
    return streams


def all_counts(streams: dict[int, tuple[int, ...]], coefficient: dict) -> dict[int, dict[int, int]]:
    values5 = five_counts()
    counts5 = {
        streams[5][position]: values5[source]
        for source, position in enumerate(M_TO_CANONICAL_POSITIONS)
    }
    independent = pencil.load_json(SIX_RESULT)
    masks6 = source_six_masks()
    values6 = tuple(map(int, independent["model"]["six_counts"]))
    require(canonical_sha256(masks6) == independent["model"]["six_source_masks_sha256"], "six-mask hash drift")
    require(canonical_sha256(values6) == independent["model"]["six_counts_sha256"], "six-count hash drift")
    counts6 = dict(zip(masks6, values6, strict=True))
    require(set(counts5) == set(streams[5]) and set(counts6) == set(streams[6]), "lower-count mapping drift")

    kernel = pencil.load_gzip_json(KERNEL)
    t = list(map(Fraction, pencil.load_json(INTEGER_CONTROL)["certificate"]["t_integral_free_x8_coordinates"]))
    nullspace = [[Fraction(0) for _ in range(8)] for _ in range(917)]
    for column, entries in enumerate(kernel["universal_nullspace_basis_sparse"]):
        for row, value in entries:
            nullspace[int(row)][column] = Fraction(value)
    x8_fraction = [sum(nullspace[1 + row][column] * t[column] for column in range(8)) for row in range(916)]
    require(all(value.denominator == 1 and value >= 0 for value in x8_fraction), "x8 not nonnegative integral")
    x8 = [value.numerator for value in x8_fraction]
    deletion = pencil.deletion_maps(coefficient, streams[7], streams[8])
    x7_fraction = [sum(Fraction(mult) * x8[column] for column, mult in row.items()) / 92 for row in deletion]
    require(all(value.denominator == 1 and value >= 0 for value in x7_fraction), "x7 not nonnegative integral")
    x7 = [value.numerator for value in x7_fraction]
    counts = {
        5: counts5,
        6: {mask: counts6[mask] for mask in streams[6]},
        7: {mask: x7[index] for index, mask in enumerate(streams[7])},
        8: {mask: x8[index] for index, mask in enumerate(streams[8])},
    }
    require(sum(counts[5].values()) == math.comb(99, 5), "order-five total drift")
    require(sum(counts[6].values()) == math.comb(99, 6), "order-six total drift")
    require(sum(counts[7].values()) == math.comb(99, 7), "order-seven total drift")
    require(sum(counts[8].values()) == math.comb(99, 8), "order-eight total drift")
    return counts


def quadratic(matrix: Sequence[Sequence[int]], vector: Sequence[int]) -> int:
    support = [index for index, value in enumerate(vector) if value]
    return sum(vector[i] * matrix[i][j] * vector[j] for i in support for j in support)


def exact_negative_direction(matrix: Sequence[Sequence[int]], eigenvector: np.ndarray) -> list[int]:
    vector = np.rint(eigenvector * 1_000_000).astype(np.int64).tolist()
    require(any(vector), "rounded eigenvector vanished")
    require(quadratic(matrix, vector) < 0, "rounded eigenvector is not exactly negative")
    for index in np.argsort(np.abs(np.asarray(vector, dtype=np.int64))):
        old = vector[int(index)]
        if not old:
            continue
        vector[int(index)] = 0
        if quadratic(matrix, vector) >= 0:
            vector[int(index)] = old
    divisor = math.gcd(*(abs(value) for value in vector if value))
    vector = [value // divisor for value in vector]
    require(quadratic(matrix, vector) < 0, "primitive vector lost negativity")
    return vector


def scalar_cut(family: dict, counts: dict[int, dict[int, int]], vector: Sequence[int]) -> dict:
    coefficients = {order: [] for order in range(5, 9)}
    all_values = []
    raw_value = 0
    for record in family["class_coefficients"]:
        coefficient = 0
        for row, column, value in record["upper_entries"]:
            multiplier = 1 if int(row) == int(column) else 2
            coefficient += multiplier * vector[int(row)] * vector[int(column)] * int(value)
        if coefficient:
            order = int(record["order"])
            mask = int(record["canonical_mask"])
            coefficients[order].append([mask, coefficient])
            all_values.append(coefficient)
            raw_value += counts[order][mask] * coefficient
    divisor = math.gcd(*(abs(value) for value in all_values))
    require(divisor > 0 and raw_value < 0, "invalid negative scalar cut")
    return {
        "sense": "sum_H coefficient_H*x_H >= 0",
        "direction": list(map(int, vector)),
        "direction_support": sum(bool(value) for value in vector),
        "raw_quadratic_value": str(raw_value),
        "primitive_divisor": str(divisor),
        "primitive_value_at_integer_control": str(raw_value // divisor),
        "coefficients": {
            str(order): [[mask, str(value // divisor)] for mask, value in local]
            for order, local in coefficients.items()
        },
    }


def exact_pivoted_ldl(matrix: Sequence[Sequence[int]]) -> dict:
    size = len(matrix)
    lower: list[list[Fraction]] = [[] for _ in range(size)]
    diagonal: list[Fraction] = []
    pivots: list[int] = []
    remaining = set(range(size))
    while True:
        residual_diagonal = {
            index: Fraction(matrix[index][index]) - sum(lower[index][k] ** 2 * diagonal[k] for k in range(len(diagonal)))
            for index in remaining
        }
        if any(value < 0 for value in residual_diagonal.values()):
            return {"status": "INDEFINITE_DURING_EXACT_LDL"}
        positive = [index for index, value in residual_diagonal.items() if value]
        if not positive:
            break
        pivot = max(positive, key=residual_diagonal.__getitem__)
        d = residual_diagonal[pivot]
        column = []
        for row in range(size):
            residual = Fraction(matrix[row][pivot]) - sum(
                lower[row][k] * diagonal[k] * lower[pivot][k]
                for k in range(len(diagonal))
            )
            column.append(residual / d)
        for row in range(size):
            lower[row].append(column[row])
        diagonal.append(d)
        pivots.append(pivot)
        remaining.remove(pivot)
    for row in range(size):
        for column in range(size):
            if sum(lower[row][k] * diagonal[k] * lower[column][k] for k in range(len(diagonal))) != matrix[row][column]:
                return {"status": "NONZERO_FINAL_SCHUR_COMPLEMENT"}
    return {
        "status": "EXACT_PSD",
        "rank": len(diagonal),
        "nullity": size - len(diagonal),
        "pivot_indices": pivots,
        "positive_diagonal": [str(value) for value in diagonal],
        "rectangular_L_sha256": canonical_sha256(
            [[[column, str(value)] for column, value in enumerate(row) if value] for row in lower]
        ),
    }


def main() -> int:
    started = time.time()
    memory = [pencil.memory_record("pair_root_start")]
    coefficient = pencil.load_gzip_json(COEFFICIENTS)
    streams = class_streams(coefficient)
    counts = all_counts(streams, coefficient)
    metadata = pencil.load_json(W147_RESULT)
    matrices = []
    results = []
    total_records = total_nonzero_upper = 0
    for family_name in ("ordered_edge", "ordered_nonedge"):
        family = coefficient["families"][family_name]
        size = int(family["matrix_size"])
        require(size == {"ordered_edge": 66, "ordered_nonedge": 87}[family_name], "matrix size drift")
        matrix = [[0] * size for _ in range(size)]
        order_records = {order: 0 for order in range(5, 9)}
        order_nonzeros = {order: 0 for order in range(5, 9)}
        for record in family["class_coefficients"]:
            order = int(record["order"])
            mask = int(record["canonical_mask"])
            weight = counts[order][mask]
            order_records[order] += 1
            for row, column, value in record["upper_entries"]:
                row, column, value = int(row), int(column), int(value)
                matrix[row][column] += weight * value
                if row != column:
                    matrix[column][row] += weight * value
                order_nonzeros[order] += 1
        total_records += sum(order_records.values())
        total_nonzero_upper += sum(order_nonzeros.values())
        root_embeddings = 99 * (14 if family_name == "ordered_edge" else 84)
        expected_sum = root_embeddings * math.comb(97, 3) ** 2
        require(sum(map(sum, matrix)) == expected_sum, f"{family_name} all-entry sum drift")
        maximum = max(abs(value) for row in matrix for value in row)
        numeric = np.asarray(matrix, dtype=np.float64) / float(maximum)
        eigenvalues, eigenvectors = np.linalg.eigh(numeric)
        negative_count = int(np.sum(eigenvalues < -1e-9))
        certificate = None
        exact_psd = None
        if negative_count:
            vector = exact_negative_direction(matrix, eigenvectors[:, 0])
            certificate = scalar_cut(family, counts, vector)
            certificate["flag_masks_on_support"] = [
                metadata["families"][family_name]["flag_masks"][index]
                for index, value in enumerate(vector) if value
            ]
            certificate["direction_sha256"] = canonical_sha256(vector)
        else:
            exact_psd = exact_pivoted_ldl(matrix)
            require(exact_psd["status"] == "EXACT_PSD", f"{family_name} numerical PSD did not exactify")
        result = {
            "family": family_name,
            "size": size,
            "class_matrix_records": sum(order_records.values()),
            "records_by_order": {str(order): order_records[order] for order in range(5, 9)},
            "nonzero_upper_coefficients_by_order": {str(order): order_nonzeros[order] for order in range(5, 9)},
            "matrix_sha256": canonical_sha256(matrix),
            "sum_all_entries": str(sum(map(sum, matrix))),
            "expected_sum": str(expected_sum),
            "minimum_numeric_eigenvalue_after_max_entry_scaling": float(eigenvalues[0]),
            "negative_numeric_eigenvalue_count_below_minus_1e-9": negative_count,
            "smallest_ten_numeric_eigenvalues": eigenvalues[:10].tolist(),
            "exact_status": "NOT_PSD" if certificate is not None else "PSD",
            "negative_scalar_cut": certificate,
            "exact_psd_certificate": exact_psd,
        }
        results.append(result)
        matrices.append({"family": family_name, "matrix": matrix})
        memory.append(pencil.memory_record(f"pair_root_{family_name}_complete"))
    require(total_records == 2414, "2,414 matrix-record census drift")
    require(total_nonzero_upper == 272_054, "nonzero coefficient census drift")
    matrix_payload = {"format": "wave163-integer-control-wave147-pair-root-matrices-v1", "blocks": matrices}
    MATRIX_OUTPUT.write_bytes(gzip.compress(json.dumps(matrix_payload, sort_keys=True, separators=(",", ":")).encode("ascii"), compresslevel=9, mtime=0))
    negative_families = [result["family"] for result in results if result["negative_scalar_cut"] is not None]
    output = {
        "format": "wave163-integer-control-wave147-pair-root-evaluation-v1",
        "claim_label": "EXACT_PAIR_ROOT_NEGATIVE_CUTS_FOUND" if negative_families else "EXACT_PAIR_ROOT_PSD_PASS",
        "inputs_sha256": {
            str(COEFFICIENTS.relative_to(ROOT)): pencil.sha256_file(COEFFICIENTS),
            str(W147_RESULT.relative_to(ROOT)): pencil.sha256_file(W147_RESULT),
            INTEGER_CONTROL.name: pencil.sha256_file(INTEGER_CONTROL),
            KERNEL.name: pencil.sha256_file(KERNEL),
            str(SIX_RESULT.relative_to(ROOT)): pencil.sha256_file(SIX_RESULT),
        },
        "coefficient_census": {
            "class_matrix_records": total_records,
            "nonzero_upper_integer_coefficients": total_nonzero_upper,
            "all_frozen_records_consumed": True,
        },
        "blocks": results,
        "matrix_archive": {"path": MATRIX_OUTPUT.name, "sha256": pencil.sha256_file(MATRIX_OUTPUT)},
        "conclusion": {
            "negative_families": negative_families,
            "endpoint_exclusion": "NOT_ESTABLISHED",
            "control_status": "refuted by exact pair-root cut" if negative_families else "passes both pair-root PSD blocks exactly",
        },
        "resource_guard": {"minimum_required": 18.0, "minimum_observed": min(float(item["free_physical_memory_percent"]) for item in memory), "samples": memory},
        "elapsed_seconds": time.time() - started,
    }
    OUTPUT.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "output": OUTPUT.name,
        "claim": output["claim_label"],
        "blocks": [
            {"family": result["family"], "min_eigenvalue": result["minimum_numeric_eigenvalue_after_max_entry_scaling"], "exact_status": result["exact_status"], "rank": None if result["exact_psd_certificate"] is None else result["exact_psd_certificate"]["rank"], "cut_support": None if result["negative_scalar_cut"] is None else result["negative_scalar_cut"]["direction_support"]}
            for result in results
        ],
        "elapsed_seconds": output["elapsed_seconds"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
