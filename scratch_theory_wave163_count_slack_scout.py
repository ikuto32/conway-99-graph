#!/usr/bin/env python3
"""Numerical scout for the *compressed* Wave163 primal with count slacks.

This stays in the eight-dimensional exact universal endpoint nullspace and
uses only the 6/8-direction compressed blocks.  It is diagnostic; no solver
status is an exact endpoint certificate.
"""

from __future__ import annotations

import gzip
import json
from fractions import Fraction
from pathlib import Path

import cvxpy as cp
import numpy as np

import scratch_theory_wave163_coupled_pencil as pencil


ROOT = Path(__file__).resolve().parent


def main():
    memory = [pencil.memory_record("count_slack_scout_start")]
    payload = json.load(gzip.open(ROOT / "scratch_theory_wave163_coupled_kernel_basis.json.gz", "rt"))
    nullspace = np.zeros((917, 8))
    for column, entries in enumerate(payload["universal_nullspace_basis_sparse"]):
        for row, value in entries:
            nullspace[int(row), column] = float(Fraction(value))
    qmap = np.asarray(
        [[float(Fraction(value)) for value in row] for row in payload["compressed_quotient_map_57_by_8"]]
    )
    roots = pencil.direction_data(pencil.all_cuts(), pencil.load_json(pencil.EVALUATION))
    scales = {
        root: [max(abs(value) for value in direction) for direction in data["directions"]]
        for root, data in roots.items()
    }
    block_maps = {}
    offset = 0
    for root, size in ((3, 6), (12, 8)):
        maps = np.zeros((size, size, 8))
        for left in range(size):
            for right in range(left, size):
                values = qmap[offset] / (scales[root][left] * scales[root][right])
                maps[left, right] = maps[right, left] = values
                offset += 1
        scale = np.max(np.abs(maps))
        block_maps[root] = maps / scale
    assert offset == 57

    # t=1,247,400*z makes the augmented constant equation simply
    # -z_2+3z_3+z_4=1.  The positive factor does not affect x8>=0 or PSD.
    parameter_scale = 1_247_400
    constant = parameter_scale * nullspace[0]
    z = cp.Variable(8)
    margin = cp.Variable()
    matrices = {
        root: cp.bmat(
            [
                [block_maps[root][i, j] @ z for j in range(block_maps[root].shape[1])]
                for i in range(block_maps[root].shape[0])
            ]
        )
        for root in (3, 12)
    }
    constraints = [
        constant @ z == 1,
        nullspace[1:] @ z >= 0,
        matrices[3] - margin * np.eye(6) >> 0,
        matrices[12] - margin * np.eye(8) >> 0,
    ]
    problem = cp.Problem(cp.Maximize(margin), constraints)
    runs = {}
    for solver in ("CLARABEL", "SCS"):
        options = {"verbose": False}
        if solver == "CLARABEL":
            options.update({"tol_gap_abs": 1e-9, "tol_feas": 1e-9, "tol_gap_rel": 1e-9, "max_iter": 1000})
        else:
            options.update({"eps": 1e-7, "max_iters": 300000})
        value = problem.solve(solver=solver, **options)
        runs[solver] = {
            "status": problem.status,
            "margin": value,
            "z": None if z.value is None else z.value.tolist(),
            "minimum_x8_coordinate": None if z.value is None else float(np.min(nullspace[1:] @ z.value)),
            "constant_residual": None if z.value is None else float(constant @ z.value - 1),
            "eigenvalues": None if z.value is None else {
                str(root): np.linalg.eigvalsh(
                    np.asarray([[block_maps[root][i, j] @ z.value for j in range(block_maps[root].shape[1])] for i in range(block_maps[root].shape[0])])
                ).tolist()
                for root in (3, 12)
            },
        }
    memory.append(pencil.memory_record("count_slack_scout_complete"))
    result = {
        "format": "wave163-compressed-count-slack-floating-scout-v1",
        "claim_label": "NUMERICAL_ONLY",
        "runs": runs,
        "resource_guard": {"minimum_required": 18.0, "samples": memory},
        "limitations": ["No numerical infeasibility or feasibility status is an exact certificate."],
    }
    path = ROOT / "scratch_theory_wave163_count_slack_scout.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({solver: {"status": run["status"], "margin": run["margin"], "min_x8": run["minimum_x8_coordinate"]} for solver, run in runs.items()}, indent=2))


if __name__ == "__main__":
    main()
