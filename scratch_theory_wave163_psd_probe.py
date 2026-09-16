#!/usr/bin/env python3
"""Numerical-only PSD probe for the exact Wave163 quotient kernel.

Any candidate emitted here must subsequently be rationalized and checked by
exact LDL; this file itself is not a certificate.
"""

from __future__ import annotations

import gzip
import json
import math
import random
from fractions import Fraction
from pathlib import Path

import scratch_theory_wave163_coupled_pencil as pencil


ROOT = Path(__file__).resolve().parent


def inner(pair_a, pair_b):
    return sum(
        a * b
        for block_a, block_b in zip(pair_a, pair_b, strict=True)
        for row_a, row_b in zip(block_a, block_b, strict=True)
        for a, b in zip(row_a, row_b, strict=True)
    )


def add_scaled(target, source, scale):
    return [
        [
            [a + scale * b for a, b in zip(row_a, row_b, strict=True)]
            for row_a, row_b in zip(block_a, block_b, strict=True)
        ]
        for block_a, block_b in zip(target, source, strict=True)
    ]


def subtract(a, b):
    return add_scaled(a, b, -1.0)


def solve(matrix, rhs):
    work = [list(row) + [value] for row, value in zip(matrix, rhs, strict=True)]
    n = len(rhs)
    for col in range(n):
        pivot = max(range(col, n), key=lambda row: abs(work[row][col]))
        if abs(work[pivot][col]) < 1e-14:
            raise RuntimeError("singular projection Gram")
        work[col], work[pivot] = work[pivot], work[col]
        value = work[col][col]
        work[col] = [x / value for x in work[col]]
        for row in range(n):
            if row == col:
                continue
            factor = work[row][col]
            if factor:
                work[row] = [x - factor * y for x, y in zip(work[row], work[col], strict=True)]
    return [work[row][-1] for row in range(n)]


def jacobi(matrix):
    a = [row[:] for row in matrix]
    n = len(a)
    vectors = [[float(i == j) for j in range(n)] for i in range(n)]
    for _ in range(100 * n * n):
        p, q = max(
            ((i, j) for i in range(n) for j in range(i + 1, n)),
            key=lambda ij: abs(a[ij[0]][ij[1]]),
        )
        if abs(a[p][q]) < 1e-13:
            break
        angle = 0.5 * math.atan2(2 * a[p][q], a[q][q] - a[p][p])
        c, s = math.cos(angle), math.sin(angle)
        app, aqq, apq = a[p][p], a[q][q], a[p][q]
        a[p][p] = c * c * app - 2 * s * c * apq + s * s * aqq
        a[q][q] = s * s * app + 2 * s * c * apq + c * c * aqq
        a[p][q] = a[q][p] = 0.0
        for k in range(n):
            if k in (p, q):
                continue
            akp, akq = a[k][p], a[k][q]
            a[k][p] = a[p][k] = c * akp - s * akq
            a[k][q] = a[q][k] = s * akp + c * akq
        for k in range(n):
            vkp, vkq = vectors[k][p], vectors[k][q]
            vectors[k][p] = c * vkp - s * vkq
            vectors[k][q] = s * vkp + c * vkq
    return [a[i][i] for i in range(n)], vectors


def project_psd(pair):
    result = []
    eigenvalues_all = []
    for matrix in pair:
        values, vectors = jacobi(matrix)
        eigenvalues_all.append(values)
        n = len(matrix)
        positive = [max(0.0, value) for value in values]
        result.append(
            [
                [sum(vectors[i][k] * positive[k] * vectors[j][k] for k in range(n)) for j in range(n)]
                for i in range(n)
            ]
        )
    return result, eigenvalues_all


def zero_pair():
    return [[[0.0] * size for _ in range(size)] for size in (6, 8)]


def build_constraints():
    kernel = json.load(gzip.open(ROOT / "scratch_theory_wave163_coupled_kernel_basis.json.gz", "rt"))
    qmap = [[float(Fraction(value)) for value in row] for row in kernel["compressed_quotient_map_57_by_8"]]
    cuts = pencil.all_cuts()
    roots = pencil.direction_data(cuts, pencil.load_json(pencil.EVALUATION))
    scales = {
        root: [max(abs(value) for value in direction) for direction in data["directions"]]
        for root, data in roots.items()
    }
    constraints = []
    for coordinate in range(8):
        pair = zero_pair()
        offset = 0
        for block_index, (root, size) in enumerate(((3, 6), (12, 8))):
            for i in range(size):
                for j in range(i, size):
                    value = qmap[offset][coordinate] / (scales[root][i] * scales[root][j])
                    pair[block_index][i][j] = pair[block_index][j][i] = value
                    offset += 1
        norm = math.sqrt(inner(pair, pair))
        constraints.append(add_scaled(zero_pair(), pair, 1.0 / norm))
    trace = zero_pair()
    for block in trace:
        for i in range(len(block)):
            block[i][i] = 1.0
    constraints.append(trace)
    rhs = [0.0] * 8 + [1.0]
    gram = [[inner(a, b) for b in constraints] for a in constraints]
    return constraints, rhs, gram, scales


def affine_projection(x, constraints, rhs, gram):
    residual = [inner(constraint, x) - target for constraint, target in zip(constraints, rhs, strict=True)]
    multipliers = solve(gram, residual)
    result = x
    for value, constraint in zip(multipliers, constraints, strict=True):
        result = add_scaled(result, constraint, -value)
    return result


def main():
    constraints, rhs, gram, scales = build_constraints()
    random.seed(163)
    x = zero_pair()
    for block in x:
        for i in range(len(block)):
            block[i][i] = 1.0 / 14
    p, q = zero_pair(), zero_pair()
    best = None
    for iteration in range(20000):
        y = affine_projection(add_scaled(x, p, 1), constraints, rhs, gram)
        p = subtract(add_scaled(x, p, 1), y)
        candidate, before_values = project_psd(add_scaled(y, q, 1))
        q = subtract(add_scaled(y, q, 1), candidate)
        x = candidate
        if iteration % 100 == 0 or iteration == 19999:
            affine = affine_projection(x, constraints, rhs, gram)
            distance = math.sqrt(inner(subtract(x, affine), subtract(x, affine)))
            values = [min(jacobi(block)[0]) for block in affine]
            record = (distance, min(values), iteration, affine, values)
            if best is None or (record[0], -record[1]) < (best[0], -best[1]):
                best = record
            if distance < 1e-10 and min(values) > 1e-8:
                break
    assert best is not None
    distance, minimum, iteration, affine, values = best
    p_coefficients = solve(gram, [inner(constraint, p) for constraint in constraints])
    separator = zero_pair()
    for value, constraint in zip(p_coefficients[:8], constraints[:8], strict=True):
        separator = add_scaled(separator, constraint, value)
    separator_eigenvalues = [jacobi(block)[0] for block in separator]
    output = {
        "status": "NUMERIC_INTERIOR_CANDIDATE" if distance < 1e-8 and minimum > 0 else "NUMERIC_NO_CERTIFICATE",
        "iteration": iteration,
        "affine_distance": distance,
        "minimum_eigenvalues": values,
        "direction_scales": {str(root): vals for root, vals in scales.items()},
        "normalized_Y3": affine[0],
        "normalized_Y12": affine[1],
        "dykstra_affine_correction_coefficients": p_coefficients,
        "candidate_separator_eigenvalues": separator_eigenvalues,
    }
    path = ROOT / "scratch_theory_wave163_psd_probe.json"
    path.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({k: output[k] for k in ("status", "iteration", "affine_distance", "minimum_eigenvalues")}, indent=2))


if __name__ == "__main__":
    main()
