#!/usr/bin/env python3
"""Rationalise and exactly certify a Wave163 positive-definite separator."""

from __future__ import annotations

import gzip
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path

import scratch_theory_wave163_coupled_kernel as kernel_tools
import scratch_theory_wave163_coupled_pencil as pencil


ROOT = Path(__file__).resolve().parent
KERNEL_INPUT = ROOT / "scratch_theory_wave163_coupled_kernel_basis.json.gz"
SCOUT_INPUT = ROOT / "scratch_theory_wave163_psd_scout.json"
OUTPUT = ROOT / "scratch_theory_wave163_psd_exact.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def fstr(value: Fraction) -> str:
    return kernel_tools.fstr(value)


def exact_blocks(qmap, scales, coefficients):
    blocks = {
        3: [[Fraction(0) for _ in range(6)] for _ in range(6)],
        12: [[Fraction(0) for _ in range(8)] for _ in range(8)],
    }
    offset = 0
    for root, size in ((3, 6), (12, 8)):
        for left in range(size):
            for right in range(left, size):
                value = sum(
                    (
                        coefficients[coordinate]
                        * qmap[offset][coordinate]
                        / (scales[root][left] * scales[root][right])
                    )
                    for coordinate in range(8)
                )
                blocks[root][left][right] = blocks[root][right][left] = value
                offset += 1
    require(offset == 57, "compressed row width drift")
    return blocks


def main() -> int:
    memory = [pencil.memory_record("exact_psd_separator_start")]
    kernel_payload = pencil.load_gzip_json(KERNEL_INPUT)
    qmap = [
        [Fraction(value) for value in row]
        for row in kernel_payload["compressed_quotient_map_57_by_8"]
    ]
    roots = pencil.direction_data(pencil.all_cuts(), pencil.load_json(pencil.EVALUATION))
    scales = {
        root: [max(abs(value) for value in direction) for direction in data["directions"]]
        for root, data in roots.items()
    }

    # Recompute the eight Frobenius normalisations used only by the floating
    # scout.  They are discarded after translating its coefficients back to
    # the exact unnormalised quotient equations.
    norms_squared = [0.0] * 8
    offset = 0
    for root, size in ((3, 6), (12, 8)):
        for left in range(size):
            for right in range(left, size):
                multiplicity = 1 if left == right else 2
                for coordinate in range(8):
                    value = float(
                        qmap[offset][coordinate]
                        / (scales[root][left] * scales[root][right])
                    )
                    norms_squared[coordinate] += multiplicity * value * value
                offset += 1
    norms = [math.sqrt(value) for value in norms_squared]

    scout = pencil.load_json(SCOUT_INPUT)
    attempts = []
    certificate = None
    for solver in ("SCS", "CLARABEL"):
        floating = scout["dual_positive_definite_separator"][solver]["coefficients"]
        unnormalised = [float(value) / norm for value, norm in zip(floating, norms, strict=True)]
        scale = max(abs(value) for value in unnormalised)
        unit = [value / scale for value in unnormalised]
        for decimal_power in range(6, 31, 2):
            denominator = 10**decimal_power
            rational = [Fraction(round(value * denominator), denominator) for value in unit]
            blocks = exact_blocks(qmap, scales, rational)
            checks = {
                root: kernel_tools.ldlt_positive_definite(blocks[root])
                for root in (3, 12)
            }
            attempts.append(
                {
                    "solver_seed": solver,
                    "decimal_power": decimal_power,
                    "root3_positive_definite": checks[3][0],
                    "root12_positive_definite": checks[12][0],
                }
            )
            if all(status for status, _ in checks.values()):
                certificate = {
                    "floating_seed_solver": solver,
                    "rounding_denominator": str(denominator),
                    "quotient_equation_coefficients": [fstr(value) for value in rational],
                    "direction_column_scales": {
                        str(root): list(map(str, values)) for root, values in scales.items()
                    },
                    "H3": [[fstr(value) for value in row] for row in blocks[3]],
                    "H12": [[fstr(value) for value in row] for row in blocks[12]],
                    "exact_ldlt_positive_diagonals": {
                        str(root): [fstr(value) for value in checks[root][1]]
                        for root in (3, 12)
                    },
                    "identity": (
                        "H_tau[i,j] = sum_k c_k Q[(tau,i,j),k]/(s_tau[i]s_tau[j]); "
                        "each exact LDL diagonal is strictly positive"
                    ),
                }
                break
        if certificate is not None:
            break
    memory.append(pencil.memory_record("exact_psd_separator_complete"))
    require(certificate is not None, "no rational positive-definite separator found")

    result = {
        "format": "wave163-exact-positive-definite-quotient-separator-v1",
        "claim_label": "EXACT_COMPRESSED_CONIC_NULL",
        "inputs": {
            KERNEL_INPUT.name: pencil.sha256_file(KERNEL_INPUT),
            SCOUT_INPUT.name: pencil.sha256_file(SCOUT_INPUT),
        },
        "certificate": certificate,
        "proof": [
            "The 8 exact quotient equations are trace(Y3*A3_k)+trace(Y12*A12_k)=0.",
            "The stored rational coefficients form H3=sum c_k*A3_k and H12=sum c_k*A12_k.",
            "Exact fraction LDL^T has strictly positive pivots for both H3 and H12, hence both are positive definite.",
            "For PSD Y3,Y12 in the quotient kernel, 0=trace(Y3*H3)+trace(Y12*H12); each term is nonnegative and vanishes only for the corresponding Y=0.",
            "Therefore the 49-dimensional affine kernel contains no nonzero PSD pair.",
        ],
        "search_attempts": attempts,
        "scope_boundary": {
            "result": "No nonzero compressed PSD exposing identity in span(U3) plus span(U12) modulo universal endpoint affine rows.",
            "fixed_x7_or_pair_root_zero_used": False,
            "count_nonnegativity_slacks_used": False,
            "directions_outside_U3_U12_covered": False,
            "full_four_root_SDP_covered": False,
            "Conway_99": "UNKNOWN",
        },
        "resource_guard": {
            "minimum_required_free_physical_memory_percent": 18.0,
            "samples": memory,
        },
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(OUTPUT),
        "claim_label": result["claim_label"],
        "seed": certificate["floating_seed_solver"],
        "rounding_denominator": certificate["rounding_denominator"],
        "certificate_sha256": hashlib.sha256(pencil.canonical_bytes(certificate)).hexdigest(),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
