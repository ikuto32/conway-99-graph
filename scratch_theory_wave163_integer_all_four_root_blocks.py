#!/usr/bin/env python3
"""Evaluate the integer Wave163 control in all nine Wave152 root blocks."""

from __future__ import annotations

import gzip
import hashlib
import itertools
import json
import math
import time
from fractions import Fraction
from pathlib import Path
from typing import Any, Sequence

import numpy as np

import scratch_theory_wave163_coupled_pencil as pencil


ROOT = Path(__file__).resolve().parent
INTEGER_CONTROL = ROOT / "scratch_theory_wave163_integer_lattice.json"
KERNEL = ROOT / "scratch_theory_wave163_coupled_kernel_basis.json.gz"
REFERENCE = pencil.EVALUATION
OUTPUT = ROOT / "scratch_theory_wave163_integer_all_four_root_blocks.json"
MATRIX_OUTPUT = ROOT / "scratch_theory_wave163_integer_all_four_root_blocks_matrices.json.gz"
LDL_OUTPUT = ROOT / "scratch_theory_wave163_integer_all_four_root_blocks_ldl.json.gz"
ROOT_MASKS = (0, 1, 3, 7, 11, 12, 13, 15, 30)
EXPECTED_SIZES = {0: 224, 1: 201, 3: 155, 7: 99, 11: 69, 12: 178, 13: 125, 15: 60, 30: 70}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()


def exact_counts() -> tuple[dict[int, dict[int, int]], dict[int, tuple[int, ...]]]:
    kernel = pencil.load_gzip_json(KERNEL)
    control = pencil.load_json(INTEGER_CONTROL)["certificate"]
    coefficient = pencil.load_gzip_json(pencil.COEFFICIENT_ARCHIVE)
    streams = pencil.class_streams(coefficient)
    nullspace = [[Fraction(0) for _ in range(8)] for _ in range(917)]
    for column, entries in enumerate(kernel["universal_nullspace_basis_sparse"]):
        for row, value in entries:
            nullspace[int(row)][column] = Fraction(value)
    t = list(map(Fraction, control["t_integral_free_x8_coordinates"]))
    x8f = [sum(nullspace[1 + row][column] * t[column] for column in range(8)) for row in range(916)]
    require(all(value.denominator == 1 and value >= 0 for value in x8f), "x8 integrality/nonnegativity failed")
    x8 = [value.numerator for value in x8f]
    deletion = pencil.deletion_maps(coefficient, streams[7], streams[8])
    x7f = [sum(Fraction(mult) * x8[column] for column, mult in row.items()) / 92 for row in deletion]
    require(all(value.denominator == 1 and value >= 0 for value in x7f), "x7 integrality/nonnegativity failed")
    counts6 = pencil.six_counts(streams[6])
    counts = {
        6: {mask: int(counts6[mask]) for mask in streams[6]},
        7: {mask: x7f[index].numerator for index, mask in enumerate(streams[7])},
        8: {mask: x8[index] for index, mask in enumerate(streams[8])},
    }
    require(tuple(sum(counts[order].values()) for order in (6, 7, 8)) == tuple(math.comb(99, order) for order in (6, 7, 8)), "count totals drift")
    return counts, streams


def dense_direction(certificate: dict[str, Any], size: int) -> list[int]:
    result = [0] * size
    for index, value in zip(certificate["indices"], certificate["vector"], strict=True):
        result[int(index)] = int(value)
    return result


def quadratic(matrix: Sequence[Sequence[int]], vector: Sequence[int]) -> int:
    support = [index for index, value in enumerate(vector) if value]
    return sum(vector[i] * matrix[i][j] * vector[j] for i in support for j in support)


def exact_pivoted_ldl(matrix: Sequence[Sequence[int]]) -> dict[str, Any]:
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
        require(all(value >= 0 for value in residual_diagonal.values()), "negative exact Schur diagonal in numerical PSD branch")
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
            require(sum(lower[row][k] * diagonal[k] * lower[column][k] for k in range(len(diagonal))) == matrix[row][column], "LDL reconstruction failed")
    sparse_lower = [[[column, str(value)] for column, value in enumerate(row) if value] for row in lower]
    return {
        "rank": len(diagonal), "nullity": size - len(diagonal),
        "pivot_indices": pivots, "positive_diagonal": [str(value) for value in diagonal],
        "rectangular_L_sha256": canonical_sha256(sparse_lower),
        "rectangular_L_sparse": sparse_lower,
        "reconstructed_entries": size * size,
    }


def class_coefficients(
    graph_mask: int, graph_order: int, root_mask: int, direction: Sequence[int],
    flag_index: dict[int, int], scout: Any, wave147: Any,
) -> tuple[int, int]:
    vertices = tuple(range(graph_order))
    pair_indices = scout.covering_pair_indices(graph_order - 4)
    first = quadratic_value = 0
    for roots in itertools.permutations(vertices, 4):
        if scout.induced_mask(graph_mask, graph_order, roots, wave147.edge_positions) != root_mask:
            continue
        complement = tuple(vertex for vertex in vertices if vertex not in roots)
        free_pairs = tuple(itertools.combinations(complement, 2))
        values = [
            direction[flag_index[scout.canonical_four_root_flag(
                scout.induced_mask(graph_mask, graph_order, roots + pair, wave147.edge_positions),
                wave147.transform_mask,
            )]]
            for pair in free_pairs
        ]
        if graph_order == 6:
            first += values[0]
        quadratic_value += sum(values[left] * values[right] for left, right in pair_indices)
    return first, quadratic_value


def build_scalar_cut(
    root: int, root_count: int, direction: Sequence[int], flags: Sequence[int],
    counts: dict[int, dict[int, int]], streams: dict[int, tuple[int, ...]], scout: Any,
    wave147: Any, matrix_value: int, memory: list[dict[str, object]],
) -> dict[str, Any]:
    flag_index = {flag: index for index, flag in enumerate(flags)}
    coefficients: dict[int, dict[int, int]] = {6: {}, 7: {}, 8: {}}
    first_coefficients: dict[int, int] = {}
    for order in (6, 7, 8):
        for class_index, mask in enumerate(streams[order]):
            first, second = class_coefficients(mask, order, root, direction, flag_index, scout, wave147)
            if order == 6 and first:
                first_coefficients[mask] = first
            if second:
                coefficients[order][mask] = second
            if class_index % 256 == 0:
                memory.append(pencil.memory_record(f"all_roots_cut_r{root}_o{order}_{class_index}"))
    projected_first = sum(counts[6][mask] * value for mask, value in first_coefficients.items())
    constant = root_count * sum(counts[6][mask] * value for mask, value in coefficients[6].items()) - projected_first**2
    dense7 = {mask: root_count * coefficients[7].get(mask, 0) for mask in streams[7]}
    dense8 = {mask: root_count * coefficients[8].get(mask, 0) for mask in streams[8]}
    exact_value = constant + sum(dense7[mask] * counts[7][mask] for mask in streams[7]) + sum(dense8[mask] * counts[8][mask] for mask in streams[8])
    require(exact_value == matrix_value < 0, "scalar-cut replay mismatch")
    divisor = math.gcd(abs(constant), *(abs(value) for value in dense7.values()), *(abs(value) for value in dense8.values()))
    require(divisor > 0, "zero scalar cut")
    core = {
        "root_mask": root,
        "sense": "constant + sum_H a7_H*x7_H + sum_K a8_K*x8_K >= 0",
        "direction": list(map(int, direction)),
        "direction_sha256": canonical_sha256(direction),
        "direction_support": sum(bool(value) for value in direction),
        "primitive_divisor": str(divisor),
        "constant": str(constant // divisor),
        "order7_coefficients": [[mask, str(value // divisor)] for mask, value in dense7.items() if value],
        "order8_coefficients": [[mask, str(value // divisor)] for mask, value in dense8.items() if value],
        "projected_first_moment": str(projected_first),
        "value_at_integer_control": str(exact_value // divisor),
        "unscaled_value_at_integer_control": str(exact_value),
    }
    return {**core, "cut_sha256": canonical_sha256(core)}


def main() -> int:
    started = time.time()
    memory = [pencil.memory_record("all_four_root_start")]
    counts, streams = exact_counts()
    scout = pencil.load_module("wave163_integer_all_roots_scout", ROOT / "external_conway99_research/attempts/wave152-four-root-order8/four_root_scout.py")
    wave147 = pencil.load_module("wave163_integer_all_roots_wave147", scout.WAVE147)
    reference = pencil.load_json(REFERENCE)
    reference_blocks = {int(block["root_mask"]): block for block in reference["root_blocks"]}
    require(set(reference_blocks) == set(ROOT_MASKS), "reference root set drift")
    flags = {root: tuple(map(int, reference_blocks[root]["flag_masks"])) for root in ROOT_MASKS}
    require({root: len(flags[root]) for root in ROOT_MASKS} == EXPECTED_SIZES, "flag sizes drift")
    flag_indices = [{flag: index for index, flag in enumerate(flags[root])} for root in ROOT_MASKS]
    root_to_index = {root: index for index, root in enumerate(ROOT_MASKS)}
    moments = [[[0] * len(flags[root]) for _ in flags[root]] for root in ROOT_MASKS]
    first = [[0] * len(flags[root]) for root in ROOT_MASKS]
    functions = {
        "edge_positions": wave147.edge_positions,
        "canonical_flag": lambda mask: scout.canonical_four_root_flag(mask, wave147.transform_mask),
    }
    enumeration = {}
    for order in (6, 7, 8):
        matched = products = nonzero = 0
        for class_index, mask in enumerate(streams[order]):
            weight = counts[order][mask]
            if not weight:
                continue
            nonzero += 1
            local_matched, local_products = scout.add_weighted_moments(
                mask, order, weight, root_to_index, flag_indices, moments, first, functions
            )
            matched += local_matched
            products += local_products
            if class_index % 128 == 0:
                memory.append(pencil.memory_record(f"all_roots_o{order}_{class_index}"))
        enumeration[str(order)] = {"classes": len(streams[order]), "nonzero_classes": nonzero, "matched": matched, "products": products}
        memory.append(pencil.memory_record(f"all_roots_o{order}_complete"))

    matrix_records = []
    ldl_records = []
    block_results = []
    free_pairs = math.comb(95, 2)
    for local, root in enumerate(ROOT_MASKS):
        root_count = int(reference_blocks[root]["root_embedding_count"])
        s = first[local]
        matrix = moments[local]
        require(sum(s) == root_count * free_pairs, f"root {root} first total")
        require(sum(map(sum, matrix)) == root_count * free_pairs**2, f"root {root} second total")
        centered = [[root_count * matrix[i][j] - s[i] * s[j] for j in range(len(s))] for i in range(len(s))]
        require(centered == [list(row) for row in zip(*centered)], f"root {root} asymmetry")
        maximum = max(abs(value) for row in centered for value in row)
        if maximum:
            numeric = np.asarray(centered, dtype=np.float64) / float(maximum)
            eigenvalues, eigenvectors = np.linalg.eigh(numeric)
        else:
            # The root-15 and root-30 controls land on the exact zero face.
            # Avoid emitting non-standard JSON NaN from a vacuous 0/0 scaling.
            eigenvalues = np.zeros(len(centered), dtype=np.float64)
            eigenvectors = np.eye(len(centered), dtype=np.float64)
        negative_count = int(np.sum(eigenvalues < -1e-9))
        negative_certificate = None
        exact_psd = None
        if negative_count:
            certificate = scout.exact_two_coordinate_certificate(centered)
            source = "two_coordinate"
            if certificate is None:
                certificate = scout.exact_eigenvector_certificate(centered, eigenvectors[:, 0])
                source = "rounded_minimum_eigenvector_then_greedy_support"
            direction = dense_direction(certificate, len(s))
            value = quadratic(centered, direction)
            require(value == int(certificate["quadratic_value_scaled"]) < 0, "negative direction replay failed")
            cut = build_scalar_cut(root, root_count, direction, flags[root], counts, streams, scout, wave147, value, memory)
            certificate["source"] = source
            certificate["flag_masks"] = [flags[root][int(index)] for index in certificate["indices"]]
            negative_certificate = {"matrix_certificate": certificate, "scalar_cut": cut}
        else:
            exact_psd = exact_pivoted_ldl(centered)
            ldl_records.append({
                "root_mask": root,
                "size": len(centered),
                "rank": exact_psd["rank"],
                "pivot_indices": exact_psd["pivot_indices"],
                "positive_diagonal": exact_psd["positive_diagonal"],
                "rectangular_L_sparse": exact_psd.pop("rectangular_L_sparse"),
            })
        block_results.append({
            "root_mask": root,
            "root_embedding_count": root_count,
            "size": len(s),
            "matrix_sha256": canonical_sha256(centered),
            "sum_all_entries": str(sum(map(sum, centered))),
            "minimum_numeric_eigenvalue_after_max_entry_scaling": float(eigenvalues[0]),
            "negative_numeric_eigenvalue_count_below_minus_1e-9": negative_count,
            "smallest_ten_numeric_eigenvalues": eigenvalues[:10].tolist(),
            "exact_status": "NOT_PSD" if negative_certificate else "PSD",
            "negative_certificate": negative_certificate,
            "exact_psd_certificate": exact_psd,
        })
        matrix_records.append({"root_mask": root, "flag_masks": list(flags[root]), "centered_matrix": centered})
        memory.append(pencil.memory_record(f"all_roots_r{root}_complete"))

    matrix_payload = {"format": "wave163-integer-control-all-nine-four-root-matrices-v1", "blocks": matrix_records}
    MATRIX_OUTPUT.write_bytes(gzip.compress(json.dumps(matrix_payload, sort_keys=True, separators=(",", ":")).encode("ascii"), compresslevel=9, mtime=0))
    ldl_payload = {"format": "wave163-integer-control-all-nine-four-root-exact-ldl-v1", "blocks": ldl_records}
    LDL_OUTPUT.write_bytes(gzip.compress(json.dumps(ldl_payload, sort_keys=True, separators=(",", ":")).encode("ascii"), compresslevel=9, mtime=0))
    negative_roots = [block["root_mask"] for block in block_results if block["negative_certificate"]]
    result = {
        "format": "wave163-integer-control-all-nine-four-root-evaluation-v1",
        "claim_label": "EXACT_FOUR_ROOT_CUTS_FOUND" if negative_roots else "EXACT_ALL_NINE_FOUR_ROOT_PSD_PASS",
        "inputs_sha256": {
            INTEGER_CONTROL.name: pencil.sha256_file(INTEGER_CONTROL),
            KERNEL.name: pencil.sha256_file(KERNEL),
            str(pencil.COEFFICIENT_ARCHIVE.relative_to(ROOT)): pencil.sha256_file(pencil.COEFFICIENT_ARCHIVE),
            str(REFERENCE.relative_to(ROOT)): pencil.sha256_file(REFERENCE),
        },
        "method": {
            "frozen_class_streams": {"6": 62, "7": 208, "8": 916},
            "class_regeneration": False,
            "coefficient_tensor_materialized": False,
            "matrix_sizes": {str(root): EXPECTED_SIZES[root] for root in ROOT_MASKS},
        },
        "enumeration": enumeration,
        "blocks": block_results,
        "matrix_archive": {"path": MATRIX_OUTPUT.name, "sha256": pencil.sha256_file(MATRIX_OUTPUT)},
        "exact_ldl_archive": {"path": LDL_OUTPUT.name, "sha256": pencil.sha256_file(LDL_OUTPUT)},
        "conclusion": {
            "negative_roots": negative_roots,
            "exact_scalar_cuts": len(negative_roots),
            "endpoint_exclusion": "NOT_ESTABLISHED",
            "control_status": "refuted" if negative_roots else "passes all nine four-root covariance blocks",
        },
        "resource_guard": {"minimum_required": 18.0, "minimum_observed": min(float(item["free_physical_memory_percent"]) for item in memory), "samples": memory},
        "elapsed_seconds": time.time() - started,
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "output": OUTPUT.name, "claim": result["claim_label"], "negative_roots": negative_roots,
        "blocks": [{"root": block["root_mask"], "size": block["size"], "min": block["minimum_numeric_eigenvalue_after_max_entry_scaling"], "status": block["exact_status"], "rank": None if block["exact_psd_certificate"] is None else block["exact_psd_certificate"]["rank"], "cut_support": None if block["negative_certificate"] is None else block["negative_certificate"]["scalar_cut"]["direction_support"]} for block in block_results],
        "elapsed_seconds": result["elapsed_seconds"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
