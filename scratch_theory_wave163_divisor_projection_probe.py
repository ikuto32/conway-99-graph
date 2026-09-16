#!/usr/bin/env python3
"""Check the primitive-row divisor needed to reconstruct covariance entries."""

from __future__ import annotations

import gzip
import json
from fractions import Fraction
from pathlib import Path

import scratch_theory_wave163_coupled_pencil as pencil


ROOT = Path(__file__).resolve().parent


def main() -> int:
    with gzip.open(ROOT / "scratch_theory_wave163_count_slack_full_block_matrices.json.gz", "rt") as handle:
        full = json.load(handle)
    coefficient = pencil.load_gzip_json(ROOT / "scratch_theory_wave163_coupled_pencil_coefficients.json.gz")
    kernel = pencil.load_gzip_json(ROOT / "scratch_theory_wave163_coupled_kernel_basis.json.gz")
    control = pencil.load_json(ROOT / "scratch_theory_wave163_count_slack_exact_control.json")["certificate"]
    roots = pencil.direction_data(pencil.all_cuts(), pencil.load_json(pencil.EVALUATION))
    qmap = [[Fraction(value) for value in row] for row in kernel["compressed_quotient_map_57_by_8"]]
    t = [Fraction(value) for value in control["t_free_x8_coordinates"]]
    matrices = {int(record["root_mask"]): record for record in full["blocks"]}
    rows = coefficient["rows"]
    checks = []
    for offset, record in enumerate(rows):
        root = int(record["root_mask"])
        left, right = map(int, record["direction_indices"])
        direction_left = roots[root]["directions"][left]
        direction_right = roots[root]["directions"][right]
        matrix = matrices[root]["centered_matrix"]
        full_projection = sum(
            int(direction_left[i]) * int(matrix[i][j]) * int(direction_right[j])
            for i in range(len(matrix))
            for j in range(len(matrix))
        )
        quotient_value = sum(qmap[offset][column] * t[column] for column in range(8))
        divisor = int(record["raw_divisor"])
        # row_maps() has already multiplied the primitive stored row by its
        # raw_divisor before deletion/elimination.  Hence qmap is in raw
        # covariance-entry units; only the common deletion factor 92 remains.
        predicted = Fraction(40_000, 92) * quotient_value
        if Fraction(full_projection) != predicted:
            raise AssertionError(f"projection mismatch row {offset}: {full_projection} != {predicted}")
        checks.append({
            "row": offset,
            "root": root,
            "pair": [left, right],
            "raw_divisor": str(divisor),
            "quotient_value": str(quotient_value),
            "full_projection": str(full_projection),
        })
    result = {
        "format": "wave163-primitive-divisor-full-projection-probe-v1",
        "claim_label": "RAW_DIVISOR_ALREADY_RESTORED_IN_QUOTIENT_MAP",
        "identity": "u_i^T C_scaled u_j = (40000/92)*(quotient_row_ij dot t)",
        "rows_verified": len(checks),
        "raw_divisors_by_root": {
            str(root): [record["raw_divisor"] for record in rows if int(record["root_mask"]) == root]
            for root in (3, 12)
        },
        "checks": checks,
        "consequence": "The quotient map contains coherent raw covariance entries: kernel recovery called row_maps(), which restored every primitive raw_divisor before x7 elimination. Direction-column congruence scaling is therefore sound.",
    }
    output = ROOT / "scratch_theory_wave163_divisor_projection_probe.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": output.name, "claim": result["claim_label"], "rows": len(checks)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
