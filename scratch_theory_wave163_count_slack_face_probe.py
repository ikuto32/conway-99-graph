#!/usr/bin/env python3
"""Numerical active-face probe for the Wave163 compressed count-slack point.

This file is deliberately diagnostic.  Exact certification is performed in a
separate script once the active linear face and matrix kernels are identified.
"""

from __future__ import annotations

import gzip
import json
from fractions import Fraction
from pathlib import Path

import numpy as np

import scratch_theory_wave163_coupled_pencil as pencil
import scratch_theory_wave163_coupled_kernel as kernel_tools


ROOT = Path(__file__).resolve().parent
PARAMETER_SCALE = 1_247_400


def main() -> int:
    payload = json.load(gzip.open(ROOT / "scratch_theory_wave163_coupled_kernel_basis.json.gz", "rt"))
    nullspace = np.zeros((917, 8))
    for column, entries in enumerate(payload["universal_nullspace_basis_sparse"]):
        for row, value in entries:
            nullspace[int(row), column] = float(Fraction(value))
    qmap = np.asarray(
        [[float(Fraction(value)) for value in row] for row in payload["compressed_quotient_map_57_by_8"]]
    )
    z = np.asarray(pencil.load_json(ROOT / "scratch_theory_wave163_count_slack_scout.json")["runs"]["CLARABEL"]["z"])
    x8 = nullspace[1:] @ z
    exact_nullspace = [[Fraction(0) for _ in range(8)] for _ in range(917)]
    for column, entries in enumerate(payload["universal_nullspace_basis_sparse"]):
        for row, value in entries:
            exact_nullspace[int(row)][column] = Fraction(value)
    roots = pencil.direction_data(pencil.all_cuts(), pencil.load_json(pencil.EVALUATION))
    scales = {
        root: [max(abs(value) for value in direction) for direction in data["directions"]]
        for root, data in roots.items()
    }
    matrices = {}
    offset = 0
    for root, size in ((3, 6), (12, 8)):
        matrix = np.zeros((size, size))
        for left in range(size):
            for right in range(left, size):
                value = qmap[offset] @ z / (scales[root][left] * scales[root][right])
                matrix[left, right] = matrix[right, left] = value
                offset += 1
        values, vectors = np.linalg.eigh(matrix)
        matrices[root] = {
            "matrix": matrix.tolist(),
            "eigenvalues": values.tolist(),
            "eigenvectors_by_column": vectors.tolist(),
        }
    order = np.argsort(x8)
    active_indices = [int(index) for index in order if abs(x8[index]) <= 1e-9]
    active_equations = [exact_nullspace[1 + index] for index in active_indices]
    active_reduced, active_pivots = kernel_tools.rref(active_equations)
    affine_equations = [
        [PARAMETER_SCALE * value for value in exact_nullspace[0]] + [Fraction(1)]
    ] + [row + [Fraction(0)] for row in active_equations]
    affine_reduced, affine_pivots_augmented = kernel_tools.rref(affine_equations)
    affine_variable_pivots = [pivot for pivot in affine_pivots_augmented if pivot < 8]
    result = {
        "format": "wave163-count-slack-active-face-numerical-probe-v1",
        "claim_label": "NUMERICAL_ONLY",
        "z": z.tolist(),
        "constant": float(1_247_400 * (nullspace[0] @ z)),
        "x8_sorted_first_64": [
            {"index": int(index), "value": float(x8[index])} for index in order[:64]
        ],
        "x8_threshold_counts": {
            str(threshold): int(np.sum(np.abs(x8) <= threshold))
            for threshold in (1e-13, 1e-11, 1e-9, 1e-7, 1e-5)
        },
        "active_indices_at_1e-9": active_indices,
        "active_exact_rank": len(active_pivots),
        "active_exact_pivots": active_pivots,
        "affine_exact_rank": len(affine_variable_pivots),
        "affine_exact_pivots": affine_variable_pivots,
        "affine_rref": [
            [str(value) for value in row]
            for row in affine_reduced
            if any(row)
        ],
        "active_row_vectors_first_64": {
            str(int(index)): nullspace[1 + int(index)].tolist() for index in order[:64]
        },
        "compressed_matrices": matrices,
    }
    output = ROOT / "scratch_theory_wave163_count_slack_face_probe.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": output.name,
        "threshold_counts": result["x8_threshold_counts"],
        "active_rank": result["active_exact_rank"],
        "affine_rank": result["affine_exact_rank"],
        "smallest": result["x8_sorted_first_64"][:16],
        "eigenvalues": {str(root): matrices[root]["eigenvalues"] for root in (3, 12)},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
