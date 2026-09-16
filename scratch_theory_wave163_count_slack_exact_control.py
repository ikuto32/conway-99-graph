#!/usr/bin/env python3
"""Exact feasible control for the Wave163 compressed count-slack primal.

If successful, this rules out an infeasibility/Farkas certificate using only
the U3/U12 compressed PSD blocks, universal endpoint rows, and induced-count
nonnegativity.  It is not a graph and does not test the full four-root blocks.
"""

from __future__ import annotations

import gzip
import json
from fractions import Fraction
from pathlib import Path

import scratch_theory_wave163_coupled_kernel as kernel_tools
import scratch_theory_wave163_coupled_pencil as pencil


ROOT = Path(__file__).resolve().parent
KERNEL_INPUT = ROOT / "scratch_theory_wave163_coupled_kernel_basis.json.gz"
SCOUT_INPUT = ROOT / "scratch_theory_wave163_count_slack_scout.json"
OUTPUT = ROOT / "scratch_theory_wave163_count_slack_exact_control.json"
PARAMETER_SCALE = 1_247_400


def fstr(value: Fraction) -> str:
    return kernel_tools.fstr(value)


def main() -> int:
    memory = [pencil.memory_record("count_slack_exact_start")]
    payload = pencil.load_gzip_json(KERNEL_INPUT)
    nullspace = [[Fraction(0) for _ in range(8)] for _ in range(917)]
    for column, entries in enumerate(payload["universal_nullspace_basis_sparse"]):
        for row, value in entries:
            nullspace[int(row)][column] = Fraction(value)
    qmap = [[Fraction(value) for value in row] for row in payload["compressed_quotient_map_57_by_8"]]
    seed = pencil.load_json(SCOUT_INPUT)["runs"]["CLARABEL"]["z"]
    roots = pencil.direction_data(pencil.all_cuts(), pencil.load_json(pencil.EVALUATION))
    scales = {
        root: [max(abs(value) for value in direction) for direction in data["directions"]]
        for root, data in roots.items()
    }

    attempts = []
    certificate = None
    for power in range(6, 41, 2):
        denominator = 10**power
        z = [Fraction(round(float(value) * denominator), denominator) for value in seed]
        # The constant row is (-z2 + 3*z3 + z4)=1.  Enforce it exactly by
        # solving for z4 after rounding the other seven coordinates.
        z[4] = Fraction(1) + z[2] - 3 * z[3]
        # The 26 numerically active order-8 coordinates span one exact row:
        # they vanish precisely on z7=58/75.  Pin that face exactly; otherwise
        # independent decimal rounding puts some of the zero counts negative.
        z[7] = Fraction(58, 75)
        t = [PARAMETER_SCALE * value for value in z]
        augmented = [
            sum((nullspace[row][column] * t[column] for column in range(8)), Fraction(0))
            for row in range(917)
        ]
        constant_ok = augmented[0] == 1
        x8 = augmented[1:]
        count_ok = all(value >= 0 for value in x8)

        matrices = {
            3: [[Fraction(0) for _ in range(6)] for _ in range(6)],
            12: [[Fraction(0) for _ in range(8)] for _ in range(8)],
        }
        offset = 0
        for root, size in ((3, 6), (12, 8)):
            for left in range(size):
                for right in range(left, size):
                    value = sum((qmap[offset][k] * t[k] for k in range(8)), Fraction(0))
                    value /= scales[root][left] * scales[root][right]
                    matrices[root][left][right] = matrices[root][right][left] = value
                    offset += 1
        checks = {
            root: kernel_tools.ldlt_positive_definite(matrix)
            for root, matrix in matrices.items()
        }
        attempts.append(
            {
                "decimal_power": power,
                "constant_exact": constant_ok,
                "all_x8_nonnegative": count_ok,
                "x8_negative_count": sum(value < 0 for value in x8),
                "root3_positive_definite": checks[3][0],
                "root12_positive_definite": checks[12][0],
            }
        )
        if constant_ok and count_ok and all(status for status, _ in checks.values()):
            coefficient_payload = pencil.load_gzip_json(pencil.COEFFICIENT_ARCHIVE)
            streams = pencil.class_streams(coefficient_payload)
            deletion = pencil.deletion_maps(coefficient_payload, streams[7], streams[8])
            index7 = {mask: index for index, mask in enumerate(streams[7])}
            x7 = [
                sum((Fraction(multiplicity) * x8[column] for column, multiplicity in row.items()), Fraction(0)) / 92
                for row in deletion
            ]
            assert all(value >= 0 for value in x7)
            assert sum(x7) == Fraction(__import__("math").comb(99, 7))
            assert sum(x8) == Fraction(__import__("math").comb(99, 8))
            assert x7[index7[120568]] == 0
            certificate = {
                "rounding_denominator": str(denominator),
                "z_parameters": list(map(fstr, z)),
                "t_free_x8_coordinates": list(map(fstr, t)),
                "augmented_constant": "1",
                "x8_nonnegative": True,
                "x8_zero_coordinates": [index for index, value in enumerate(x8) if value == 0],
                "minimum_positive_x8": fstr(min(value for value in x8 if value > 0)),
                "x7_nonnegative": True,
                "x7_zero_coordinates": [index for index, value in enumerate(x7) if value == 0],
                "H_delta_mask": 120568,
                "H_delta_count": fstr(x7[index7[120568]]),
                "endpoint_prism_count": "0",
                "sum_E0_from_6P_plus_H_delta": fstr(x7[index7[120568]]),
                "sum_x7": str(sum(x7)),
                "sum_x8": str(sum(x8)),
                "direction_column_scales": {str(root): list(map(str, values)) for root, values in scales.items()},
                "compressed_Y_test_matrices": {
                    str(root): [[fstr(value) for value in row] for row in matrices[root]]
                    for root in (3, 12)
                },
                "exact_ldlt_positive_diagonals": {
                    str(root): list(map(fstr, checks[root][1])) for root in (3, 12)
                },
            }
            break
    if certificate is None:
        raise AssertionError("no exact strictly compressed-PSD nonnegative-count control found")
    memory.append(pencil.memory_record("count_slack_exact_complete"))
    result = {
        "format": "wave163-compressed-count-slack-exact-feasible-control-v1",
        "claim_label": "EXACT_COMPRESSED_PRIMAL_FEASIBLE",
        "inputs": {
            KERNEL_INPUT.name: pencil.sha256_file(KERNEL_INPUT),
            SCOUT_INPUT.name: pencil.sha256_file(SCOUT_INPUT),
            str(pencil.COEFFICIENT_ARCHIVE.relative_to(ROOT)): pencil.sha256_file(pencil.COEFFICIENT_ARCHIVE),
        },
        "certificate": certificate,
        "verification": {
            "universal_rows": "satisfied by exact nullspace parameterization",
            "all_x7_x8_counts_nonnegative": True,
            "both_compressed_blocks_positive_definite": True,
            "endpoint_n3_4158_and_sum_E0_zero": True,
            "implication": "No infeasibility dual/Farkas certificate exists using only these compressed PSD blocks, universal equalities, and x7/x8 nonnegativity.",
        },
        "attempts": attempts,
        "scope_boundary": {
            "full_four_root_blocks": "NOT_TESTED",
            "graph_realizability": "NOT_CLAIMED",
            "endpoint_n3_4158": "IMPOSED_BY_THE_UNIVERSAL_ENDPOINT_ROWS; GRAPH_EXISTENCE_UNKNOWN",
            "Conway_99": "UNKNOWN",
        },
        "resource_guard": {"minimum_required": 18.0, "samples": memory},
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(OUTPUT),
        "claim_label": result["claim_label"],
        "rounding_denominator": certificate["rounding_denominator"],
        "x8_zeros": len(certificate["x8_zero_coordinates"]),
        "x7_zeros": len(certificate["x7_zero_coordinates"]),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
