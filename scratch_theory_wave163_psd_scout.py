#!/usr/bin/env python3
"""Floating SDP scout for the Wave163 exact 49-dimensional kernel.

This is diagnostic only.  Exact conclusions belong in the kernel/audit
artifacts after rational reconstruction and exact LDL verification.
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


def build_blocks():
    payload = json.load(gzip.open(ROOT / "scratch_theory_wave163_coupled_kernel_basis.json.gz", "rt"))
    qmap = [[Fraction(value) for value in row] for row in payload["compressed_quotient_map_57_by_8"]]
    roots = pencil.direction_data(pencil.all_cuts(), pencil.load_json(pencil.EVALUATION))
    scales = {
        root: [max(abs(value) for value in direction) for direction in data["directions"]]
        for root, data in roots.items()
    }
    blocks = {3: [np.zeros((6, 6)) for _ in range(8)], 12: [np.zeros((8, 8)) for _ in range(8)]}
    offset = 0
    for root, size in ((3, 6), (12, 8)):
        for left in range(size):
            for right in range(left, size):
                for coordinate in range(8):
                    value = float(qmap[offset][coordinate] / (scales[root][left] * scales[root][right]))
                    blocks[root][coordinate][left, right] = value
                    blocks[root][coordinate][right, left] = value
                offset += 1
    # Independently normalise each quotient equation.
    for coordinate in range(8):
        norm = np.sqrt(sum(np.sum(blocks[root][coordinate] ** 2) for root in (3, 12)))
        for root in (3, 12):
            blocks[root][coordinate] /= norm
    return blocks, scales


def solve_problem(problem, solver):
    options = {"verbose": False}
    if solver == "CLARABEL":
        options.update({"tol_gap_abs": 1e-10, "tol_feas": 1e-10, "tol_gap_rel": 1e-10, "max_iter": 1000})
    else:
        options.update({"eps": 1e-8, "max_iters": 200000})
    value = problem.solve(solver=solver, **options)
    return {"status": problem.status, "value": value, "solver_stats": str(problem.solver_stats)}


def main():
    memory = [pencil.memory_record("psd_scout_start")]
    blocks, scales = build_blocks()

    y3 = cp.Variable((6, 6), symmetric=True)
    y12 = cp.Variable((8, 8), symmetric=True)
    t = cp.Variable()
    equations = [
        cp.trace(blocks[3][k] @ y3) + cp.trace(blocks[12][k] @ y12) == 0
        for k in range(8)
    ]
    primal = cp.Problem(
        cp.Maximize(t),
        equations
        + [cp.trace(y3) + cp.trace(y12) == 1, y3 - t * np.eye(6) >> 0, y12 - t * np.eye(8) >> 0],
    )
    primal_runs = {}
    for solver in ("CLARABEL", "SCS"):
        primal_runs[solver] = solve_problem(primal, solver)
        primal_runs[solver]["Y3"] = None if y3.value is None else y3.value.tolist()
        primal_runs[solver]["Y12"] = None if y12.value is None else y12.value.tolist()
        primal_runs[solver]["residuals"] = None if y3.value is None else [
            float(np.trace(blocks[3][k] @ y3.value) + np.trace(blocks[12][k] @ y12.value)) for k in range(8)
        ]
        primal_runs[solver]["eigenvalues"] = None if y3.value is None else {
            "Y3": np.linalg.eigvalsh(y3.value).tolist(),
            "Y12": np.linalg.eigvalsh(y12.value).tolist(),
        }

    c = cp.Variable(8)
    h3 = sum(c[k] * blocks[3][k] for k in range(8))
    h12 = sum(c[k] * blocks[12][k] for k in range(8))
    dual_t = cp.Variable()
    dual = cp.Problem(
        cp.Maximize(dual_t),
        [cp.trace(h3) + cp.trace(h12) == 1, h3 - dual_t * np.eye(6) >> 0, h12 - dual_t * np.eye(8) >> 0],
    )
    dual_runs = {}
    for solver in ("CLARABEL", "SCS"):
        dual_runs[solver] = solve_problem(dual, solver)
        dual_runs[solver]["coefficients"] = None if c.value is None else c.value.tolist()
        dual_runs[solver]["eigenvalues"] = None if c.value is None else {
            "H3": np.linalg.eigvalsh(sum(c.value[k] * blocks[3][k] for k in range(8))).tolist(),
            "H12": np.linalg.eigvalsh(sum(c.value[k] * blocks[12][k] for k in range(8))).tolist(),
        }

    memory.append(pencil.memory_record("psd_scout_complete"))
    result = {
        "format": "wave163-compressed-kernel-floating-psd-scout-v1",
        "claim_label": "NUMERICAL_ONLY",
        "direction_scales": {str(root): values for root, values in scales.items()},
        "primal_common_minimum_eigenvalue": primal_runs,
        "dual_positive_definite_separator": dual_runs,
        "resource_guard": {"minimum_required": 18.0, "samples": memory},
        "limitations": ["No floating solver status or eigenvalue is an exact certificate."],
    }
    path = ROOT / "scratch_theory_wave163_psd_scout.json"
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "primal": {s: {"status": r["status"], "value": r["value"]} for s, r in primal_runs.items()},
        "dual": {s: {"status": r["status"], "value": r["value"]} for s, r in dual_runs.items()},
    }, indent=2))


if __name__ == "__main__":
    main()
