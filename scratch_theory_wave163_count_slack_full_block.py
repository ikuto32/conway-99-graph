#!/usr/bin/env python3
"""Stream the full root-3/root-12 covariance at the exact Wave163 control.

This is a discovery stage.  It reuses the frozen 62/208/916 class streams
and never builds a new admissible-class catalogue or a full coefficient
tensor.  Only the two small dense evaluated matrices (155 and 178) are held.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import time
import gzip
from fractions import Fraction
from pathlib import Path

import numpy as np

import scratch_theory_wave163_coupled_pencil as pencil


ROOT = Path(__file__).resolve().parent
CONTROL = ROOT / "scratch_theory_wave163_count_slack_exact_control.json"
INTEGER_CONTROL = ROOT / "scratch_theory_wave163_integer_lattice.json"
KERNEL = ROOT / "scratch_theory_wave163_coupled_kernel_basis.json.gz"
REFERENCE_EVALUATION = pencil.EVALUATION
OUTPUT = ROOT / "scratch_theory_wave163_count_slack_full_block.json"
MATRIX_OUTPUT = ROOT / "scratch_theory_wave163_count_slack_full_block_matrices.json.gz"
ROOT_MASKS = (3, 12)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def exact_counts(integer_control: bool) -> tuple[dict[int, dict[int, Fraction]], dict[int, tuple[int, ...]], int]:
    payload = pencil.load_gzip_json(KERNEL)
    control = pencil.load_json(INTEGER_CONTROL if integer_control else CONTROL)["certificate"]
    coefficient_payload = pencil.load_gzip_json(pencil.COEFFICIENT_ARCHIVE)
    streams = pencil.class_streams(coefficient_payload)
    nullspace = [[Fraction(0) for _ in range(8)] for _ in range(917)]
    for column, entries in enumerate(payload["universal_nullspace_basis_sparse"]):
        for row, value in entries:
            nullspace[int(row)][column] = Fraction(value)
    t_key = "t_integral_free_x8_coordinates" if integer_control else "t_free_x8_coordinates"
    t = [Fraction(value) for value in control[t_key]]
    x8 = [
        sum((nullspace[1 + row][column] * t[column] for column in range(8)), Fraction(0))
        for row in range(916)
    ]
    deletion = pencil.deletion_maps(coefficient_payload, streams[7], streams[8])
    x7 = [
        sum((Fraction(mult) * x8[column] for column, mult in row.items()), Fraction(0)) / 92
        for row in deletion
    ]
    require(all(value >= 0 for value in x8 + x7), "control has negative counts")
    require(all(value.denominator == 1 for value in x7), "order-seven control ceased to be integral")
    counts6 = pencil.six_counts(streams[6])
    counts = {
        6: {mask: Fraction(counts6[mask]) for mask in streams[6]},
        7: {mask: x7[index] for index, mask in enumerate(streams[7])},
        8: {mask: x8[index] for index, mask in enumerate(streams[8])},
    }
    scale = math.lcm(*(value.denominator for order in counts.values() for value in order.values()))
    require(scale == (1 if integer_control else 40_000), "unexpected control count denominator")
    return counts, streams, scale


def dense_direction(certificate: dict, size: int) -> list[int]:
    result = [0] * size
    for index, value in zip(certificate["indices"], certificate["vector"], strict=True):
        result[int(index)] = int(value)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--integer-control", action="store_true")
    args = parser.parse_args()
    control_path = INTEGER_CONTROL if args.integer_control else CONTROL
    output_path = (
        ROOT / "scratch_theory_wave163_integer_lattice_full_block.json"
        if args.integer_control else OUTPUT
    )
    matrix_output_path = (
        ROOT / "scratch_theory_wave163_integer_lattice_full_block_matrices.json.gz"
        if args.integer_control else MATRIX_OUTPUT
    )
    started = time.time()
    memory = [pencil.memory_record("full_block_start")]
    counts, streams, count_scale = exact_counts(args.integer_control)
    scout = pencil.load_module(
        "wave163_control_full_block_scout", ROOT / "external_conway99_research/attempts/wave152-four-root-order8/four_root_scout.py"
    )
    wave147 = pencil.load_module("wave163_control_full_block_wave147", scout.WAVE147)
    reference = pencil.load_json(REFERENCE_EVALUATION)
    reference_blocks = {
        int(block["root_mask"]): block
        for block in reference["root_blocks"]
        if int(block["root_mask"]) in ROOT_MASKS
    }
    require(set(reference_blocks) == set(ROOT_MASKS), "reference root blocks missing")
    flags = {root: tuple(map(int, reference_blocks[root]["flag_masks"])) for root in ROOT_MASKS}
    require({root: len(flags[root]) for root in ROOT_MASKS} == {3: 155, 12: 178}, "flag width drift")
    flag_indices = [{mask: index for index, mask in enumerate(flags[root])} for root in ROOT_MASKS]
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
            scaled = weight * count_scale
            require(scaled.denominator == 1, "count scaling failed")
            local_matched, local_products = scout.add_weighted_moments(
                mask,
                order,
                int(scaled),
                root_to_index,
                flag_indices,
                moments,
                first,
                functions,
            )
            matched += local_matched
            products += local_products
            if class_index % 128 == 0:
                memory.append(pencil.memory_record(f"full_block_o{order}_class_{class_index}"))
        enumeration[str(order)] = {
            "classes_in_frozen_stream": len(streams[order]),
            "nonzero_classes": nonzero,
            "matched_root_embeddings_unweighted": matched,
            "emitted_products_unweighted": products,
        }
        memory.append(pencil.memory_record(f"full_block_o{order}_complete"))

    roots_data = pencil.direction_data(pencil.all_cuts(), reference)
    blocks = []
    matrix_records = []
    free_pairs = math.comb(99 - 4, 2)
    for local, root in enumerate(ROOT_MASKS):
        root_count = int(reference_blocks[root]["root_embedding_count"])
        require(root_count == 1_014_552, "root embedding count drift")
        s = first[local]
        matrix = moments[local]
        require(sum(s) == count_scale * root_count * free_pairs, "first moment total failed")
        require(sum(map(sum, matrix)) == count_scale * root_count * free_pairs**2, "second moment total failed")
        require(
            all(s[i] * s[j] % count_scale == 0 for i in range(len(s)) for j in range(len(s))),
            "centered matrix lost integrality",
        )
        centered = [
            [root_count * matrix[i][j] - s[i] * s[j] // count_scale for j in range(len(s))]
            for i in range(len(s))
        ]
        require(centered == [list(row) for row in zip(*centered)], "centered matrix is not symmetric")
        maximum = max(abs(value) for row in centered for value in row)
        numeric = np.asarray(centered, dtype=np.float64) / float(maximum)
        eigenvalues, eigenvectors = np.linalg.eigh(numeric)
        minimum = float(eigenvalues[0])
        negative_count = int(np.sum(eigenvalues < -1e-9))
        zero_count = int(np.sum(np.abs(eigenvalues) <= 1e-9))
        positive_values = eigenvalues[eigenvalues > 1e-9]
        existing = [list(map(int, vector)) for vector in roots_data[root]["directions"]]
        before = [pencil.rank_columns_mod(existing, prime) for prime in pencil.PRIMES]
        columns = np.asarray(existing, dtype=np.float64).T
        columns /= np.maximum(np.linalg.norm(columns, axis=0), 1.0)
        basis, singular, _ = np.linalg.svd(columns, full_matrices=False)
        rank = int(np.sum(singular > singular[0] * 1e-12))
        vector = eigenvectors[:, 0]
        projection = basis[:, :rank] @ (basis[:, :rank].T @ vector)
        residual_ratio = float(np.linalg.norm(vector - projection) / np.linalg.norm(vector))
        certificate = scout.exact_two_coordinate_certificate(centered)
        certificate_source = "two_coordinate" if certificate is not None else None
        if certificate is None and minimum < -1e-9:
            certificate = scout.exact_eigenvector_certificate(centered, eigenvectors[:, 0])
            certificate_source = "rounded_minimum_eigenvector_then_greedy_support"
        if certificate is not None:
            direction = dense_direction(certificate, len(s))
            exact_value = sum(
                direction[i] * centered[i][j] * direction[j]
                for i in range(len(s))
                for j in range(len(s))
            )
            require(exact_value == int(certificate["quadratic_value_scaled"]) < 0, "exact negative certificate drift")
            after = [pencil.rank_columns_mod(existing + [direction], prime) for prime in pencil.PRIMES]
            require(before == [len(existing)] * 2 and after == [len(existing) + 1] * 2, "new direction lies in retained span")
            certificate["flag_masks"] = [flags[root][int(index)] for index in certificate["indices"]]
            certificate["dense_direction_sha256"] = canonical_sha256(direction)
        else:
            after = before
        blocks.append({
            "root_mask": root,
            "root_embedding_count": root_count,
            "flag_count": len(s),
            "flag_masks_sha256": canonical_sha256(flags[root]),
            "centered_integer_scale": f"{count_scale}*(R*M-s*s^T)",
            "centered_matrix_sha256": canonical_sha256(centered),
            "maximum_absolute_centered_entry": str(maximum),
            "minimum_numeric_eigenvalue_after_max_entry_scaling": minimum,
            "numeric_negative_eigenvalue_count_below_minus_1e-9": negative_count,
            "numeric_zero_eigenvalue_count_at_1e-9": zero_count,
            "minimum_numeric_positive_eigenvalue_above_1e-9": (
                None if not len(positive_values) else float(positive_values[0])
            ),
            "smallest_twenty_numeric_eigenvalues": eigenvalues[:20].tolist(),
            "minimum_eigenvector_residual_norm_outside_retained_span": residual_ratio,
            "retained_direction_rank_mod_primes": before,
            "augmented_direction_rank_mod_primes": after,
            "exact_status": "NOT_PSD" if certificate is not None else "NUMERICALLY_NO_NEGATIVE_DIRECTION",
            "exact_certificate_source": certificate_source,
            "negative_certificate": certificate,
        })
        matrix_records.append({
            "root_mask": root,
            "flag_masks": list(flags[root]),
            "centered_matrix": centered,
        })
        memory.append(pencil.memory_record(f"full_block_root_{root}_complete"))

    matrix_payload = {
        "format": "wave163-exact-control-full-root3-root12-matrices-v1",
        "count_denominator_scale": count_scale,
        "blocks": matrix_records,
    }
    matrix_output_path.write_bytes(
        gzip.compress(
            json.dumps(matrix_payload, sort_keys=True, separators=(",", ":")).encode("ascii"),
            compresslevel=9,
            mtime=0,
        )
    )
    result = {
        "format": "wave163-exact-control-full-root3-root12-evaluation-v1",
        "claim_label": "FULL_BLOCK_CONTROL_EVALUATION_COMPLETE",
        "inputs_sha256": {
            control_path.name: pencil.sha256_file(control_path),
            KERNEL.name: pencil.sha256_file(KERNEL),
            str(pencil.COEFFICIENT_ARCHIVE.relative_to(ROOT)): pencil.sha256_file(pencil.COEFFICIENT_ARCHIVE),
            str(REFERENCE_EVALUATION.relative_to(ROOT)): pencil.sha256_file(REFERENCE_EVALUATION),
        },
        "method": {
            "class_policy": "reuse frozen order-6/7/8 streams; no class regeneration",
            "count_denominator_scale": count_scale,
            "dense_matrices_held": {"3": 155, "12": 178},
            "full_coefficient_tensor_materialized": False,
            "evaluated_matrix_archive": matrix_output_path.name,
            "evaluated_matrix_archive_sha256": pencil.sha256_file(matrix_output_path),
            "control_kind": "integer_lattice" if args.integer_control else "rational_rounding",
        },
        "enumeration": enumeration,
        "root_blocks": blocks,
        "conclusion": {
            "numeric_discovery": "reported separately for each full block",
            "exact_negative_roots": [block["root_mask"] for block in blocks if block["negative_certificate"] is not None],
            "endpoint_exclusion": "NOT_ESTABLISHED; only this rational control is refuted",
        },
        "resource_guard": {
            "minimum_required": 18.0,
            "minimum_observed": min(float(record["free_physical_memory_percent"]) for record in memory),
            "samples": memory,
        },
        "elapsed_seconds": time.time() - started,
    }
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": output_path.name,
        "claim_label": result["claim_label"],
        "blocks": [
            {
                "root": block["root_mask"],
                "min_eigenvalue": block["minimum_numeric_eigenvalue_after_max_entry_scaling"],
                "negative_count": block["numeric_negative_eigenvalue_count_below_minus_1e-9"],
                "zero_count": block["numeric_zero_eigenvalue_count_at_1e-9"],
                "min_positive": block["minimum_numeric_positive_eigenvalue_above_1e-9"],
                "support": None if block["negative_certificate"] is None else len(block["negative_certificate"]["indices"]),
                "exact_value": None if block["negative_certificate"] is None else block["negative_certificate"]["quadratic_value_scaled"],
                "outside_residual": block["minimum_eigenvector_residual_norm_outside_retained_span"],
            }
            for block in blocks
        ],
        "elapsed_seconds": result["elapsed_seconds"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
