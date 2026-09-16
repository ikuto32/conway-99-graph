#!/usr/bin/env python3
"""Bind the exact integral Wave163 order-8 boundary certificates."""

from __future__ import annotations

import gzip
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parent
COEFFICIENT = ROOT / "external_conway99_research/attempts/wave147-alternative-lane/coefficients.json.gz"
KERNEL = ROOT / "scratch_theory_wave163_coupled_kernel_basis.json.gz"
COUPLED = ROOT / "scratch_theory_wave163_coupled_pencil.json"
COUPLED_AUDIT = ROOT / "scratch_theory_wave163_coupled_pencil_independent_audit.json"
LATTICE = ROOT / "scratch_theory_wave163_integer_lattice.json"
LATTICE_AUDIT = ROOT / "scratch_theory_wave163_integer_lattice_audit.json"
PAIR = ROOT / "scratch_theory_wave163_integer_pair_root_blocks.json"
PAIR_AUDIT = ROOT / "scratch_theory_wave163_integer_pair_root_blocks_audit.json"
FOUR = ROOT / "scratch_theory_wave163_integer_all_four_root_blocks.json"
FOUR_AUDIT = ROOT / "scratch_theory_wave163_integer_all_four_root_blocks_audit.json"
FOUR_MATRICES = ROOT / "scratch_theory_wave163_integer_all_four_root_blocks_matrices.json.gz"
FOUR_LDL = ROOT / "scratch_theory_wave163_integer_all_four_root_blocks_ldl.json.gz"
OUTPUT = ROOT / "scratch_theory_wave163_integral_order8_boundary.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_gzip(path: Path) -> dict:
    with gzip.open(path, "rt", encoding="ascii") as handle:
        return json.load(handle)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_sha256(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def reconstruct_counts(lattice: dict) -> tuple[list[int], list[int], list[int], list[int]]:
    coefficients = load_gzip(COEFFICIENT)
    families = []
    for family in ("ordered_edge", "ordered_nonedge"):
        streams = {7: [], 8: []}
        for record in coefficients["families"][family]["class_coefficients"]:
            order = int(record["order"])
            if order in streams:
                streams[order].append(int(record["canonical_mask"]))
        families.append(streams)
    require(families[0] == families[1], "frozen family streams differ")
    masks7, masks8 = families[0][7], families[0][8]
    require((len(masks7), len(masks8)) == (208, 916), "frozen class census drift")

    kernel = load_gzip(KERNEL)
    basis = [[Fraction(0) for _ in range(8)] for _ in range(917)]
    for column, entries in enumerate(kernel["universal_nullspace_basis_sparse"]):
        for row, value in entries:
            basis[int(row)][column] = Fraction(value)
    t = list(map(Fraction, lattice["certificate"]["t_integral_free_x8_coordinates"]))
    x8f = [sum(basis[1 + row][column] * t[column] for column in range(8)) for row in range(916)]
    require(all(value.denominator == 1 and value >= 0 for value in x8f), "order-8 vector not nonnegative integral")
    x8 = [value.numerator for value in x8f]

    index7 = {mask: index for index, mask in enumerate(masks7)}
    index8 = {mask: index for index, mask in enumerate(masks8)}
    deletion: list[dict[int, int] | None] = [None] * 208
    for record in coefficients["order7_to_order8_deletion_equations"]:
        deletion[index7[int(record["order7_mask"])]] = {
            index8[int(mask)]: int(mult) for mask, mult in record["terms_order8_mask_multiplicity"]
        }
    require(all(row is not None for row in deletion), "missing order-7 deletion row")
    x7f = [
        sum(Fraction(mult) * x8[column] for column, mult in row.items()) / 92
        for row in deletion if row is not None
    ]
    require(all(value.denominator == 1 and value >= 0 for value in x7f), "order-7 vector not nonnegative integral")
    x7 = [value.numerator for value in x7f]
    return masks7, x7, masks8, x8


def main() -> int:
    coupled = load_json(COUPLED)
    coupled_audit = load_json(COUPLED_AUDIT)
    lattice = load_json(LATTICE)
    lattice_audit = load_json(LATTICE_AUDIT)
    pair = load_json(PAIR)
    pair_audit = load_json(PAIR_AUDIT)
    four = load_json(FOUR)
    four_audit = load_json(FOUR_AUDIT)

    require(coupled["claim_label"] == "EXACT_KERNEL_FOUND", "coupled claim drift")
    require(coupled_audit["claim_label"] == "VERIFIED_SCOPED_COMPRESSED_CONIC_NULL", "coupled audit claim drift")
    frozen = coupled["frozen_inputs_consumed_not_regenerated"]
    require(frozen == {
        "order8_classes": 916, "ordinary_deletion_rows": 208,
        "marked_vertex_rows": 944, "marked_pair_rows": 4440,
        "wave147_class_matrices": 2414,
    }, "frozen census drift")
    require(coupled["compressed_pencil"]["total_rows"] == 57, "compressed row count drift")
    require(coupled_audit["universal_affine_audit"]["ordinary_deletion_pivots"] == 208, "deletion audit drift")

    require(lattice["claim_label"] == "EXACT_INTEGRAL_COMPRESSED_PRIMAL_FEASIBLE", "integer claim drift")
    require(lattice_audit["claim_label"] == "INDEPENDENT_EXACT_INTEGRAL_COMPRESSED_FEASIBILITY_PASS", "integer audit drift")
    masks7, x7, masks8, x8 = reconstruct_counts(lattice)
    cert = lattice["certificate"]
    require(sum(x7) == math.comb(99, 7) and sum(x8) == math.comb(99, 8), "count normalization drift")
    require([i for i, value in enumerate(x7) if not value] == cert["x7_zero_indices"], "x7 zero face drift")
    require([i for i, value in enumerate(x8) if not value] == cert["x8_zero_indices"], "x8 zero face drift")
    require(min(value for value in x7 if value) == int(cert["minimum_positive_x7"]), "x7 minimum drift")
    require(min(value for value in x8 if value) == int(cert["minimum_positive_x8"]), "x8 minimum drift")
    require(cert["H_delta_count"] == "0", "H_delta is nonzero")
    count_audit = lattice_audit["count_audit"]
    require(count_audit["endpoint_n3"] == 4158, "endpoint n3 drift")
    require(count_audit["endpoint_prism_count_from_n3_plus_3P_equals_4158"] == "0", "P is nonzero")
    require(count_audit["sum_E0_from_6P_plus_H_delta"] == "0", "sum E0 is nonzero")

    require(pair["claim_label"] == "EXACT_PAIR_ROOT_PSD_PASS", "pair-root claim drift")
    require(pair_audit["claim_label"] == "INDEPENDENT_EXACT_INTEGER_PAIR_ROOT_PSD_PASS", "pair-root audit drift")
    require(pair_audit["coefficient_census"]["all_2414_class_matrices_consumed"], "pair-root matrix census incomplete")
    require(pair_audit["coefficient_census"]["class_matrix_records"] == 2414, "pair-root record drift")
    pair_blocks = pair_audit["blocks"]
    require({name: (block["size"], block["exact_rank_one_psd"]["rank"]) for name, block in pair_blocks.items()} == {
        "ordered_edge": (66, 1), "ordered_nonedge": (87, 1),
    }, "pair-root ranks drift")

    require(four["claim_label"] == "EXACT_ALL_NINE_FOUR_ROOT_PSD_PASS", "four-root claim drift")
    require(four_audit["claim_label"] == "INDEPENDENT_EXACT_ALL_NINE_FOUR_ROOT_PSD_PASS", "four-root audit drift")
    require(four["conclusion"]["negative_roots"] == [], "negative four-root block")
    four_table = [
        {
            "root_mask": int(root), "size": int(block["size"]), "rank": int(block["rank"]),
            "nullity": int(block["nullity"]), "matrix_sha256": block["matrix_sha256"],
            "identically_zero": bool(block["identically_zero"]),
        }
        for root, block in sorted(four_audit["blocks"].items(), key=lambda item: int(item[0]))
    ]
    require([(row["root_mask"], row["size"], row["rank"]) for row in four_table] == [
        (0, 224, 38), (1, 201, 27), (3, 155, 15), (7, 99, 3), (11, 69, 3),
        (12, 178, 16), (13, 125, 6), (15, 60, 0), (30, 70, 0),
    ], "four-root table drift")

    x7_pairs = [[mask, count] for mask, count in zip(masks7, x7, strict=True)]
    x8_pairs = [[mask, count] for mask, count in zip(masks8, x8, strict=True)]
    inputs = (
        COEFFICIENT, KERNEL, COUPLED, COUPLED_AUDIT, LATTICE, LATTICE_AUDIT,
        PAIR, PAIR_AUDIT, FOUR, FOUR_AUDIT, FOUR_MATRICES, FOUR_LDL,
    )
    result = {
        "format": "wave163-integral-complete-current-order8-boundary-v1",
        "claim_label": "EXPLICIT_INTEGRAL_FEASIBLE_BOUNDARY_FOR_CURRENT_ORDER8_RELAXATION",
        "frozen_census": {
            **frozen,
            "order7_classes": 208,
            "order6_classes_used_by_covariance_replay": 62,
            "compressed_four_root_pencil_rows": 57,
            "full_four_root_blocks": 9,
        },
        "integral_pseudocount": {
            "free_coordinates_t": cert["t_integral_free_x8_coordinates"],
            "order7_mask_count_pairs": x7_pairs,
            "order8_mask_count_pairs": x8_pairs,
            "order7_vector_sha256": canonical_sha256(x7_pairs),
            "order8_vector_sha256": canonical_sha256(x8_pairs),
            "order7_sum": str(sum(x7)), "order8_sum": str(sum(x8)),
            "order7_zero_count": x7.count(0), "order8_zero_count": x8.count(0),
            "minimum_positive_order7": str(min(value for value in x7 if value)),
            "minimum_positive_order8": str(min(value for value in x8 if value)),
            "all_nonnegative_integral": True,
        },
        "endpoint": {
            "n3": 4158, "P": 0, "H_delta": 0, "sum_E0": 0,
            "identities": ["n3+3P=4158", "sum_r E0(r)=6P+N(H_delta)"],
            "therefore_pointwise_E0": "E0(r)=0 for every root, since E0(r)>=0",
        },
        "universal_linear_and_compressed_layer": {
            "input_row_counts": coupled["universal_endpoint_affine_space"]["input_row_counts"],
            "reduced_coordinate_width": coupled["universal_endpoint_affine_space"]["reduced_coordinate_width"],
            "universal_nullity": 8,
            "independent_modular_primes": [1000000007, 1000000009],
            "compressed_blocks": {"root3_size": 6, "root12_size": 8, "status": "exact positive definite"},
            "independent_audit": coupled_audit["claim_label"],
        },
        "wave147_pair_root_covariance": {
            "all_2414_frozen_coefficient_matrices_consumed": True,
            "nonzero_upper_coefficients": pair_audit["coefficient_census"]["nonzero_upper_coefficients"],
            "blocks": {
                name: {
                    "size": block["size"], "rank": block["exact_rank_one_psd"]["rank"],
                    "nullity": block["exact_rank_one_psd"]["nullity"],
                    "matrix_sha256": block["matrix_sha256"], "exact_status": "PSD",
                }
                for name, block in pair_blocks.items()
            },
            "independent_audit": pair_audit["claim_label"],
        },
        "wave152_four_root_covariance": {
            "all_nine_blocks": four_table,
            "total_matrix_entries_exactly_reconstructed": four_audit["totals"]["matrix_entries_exactly_reconstructed"],
            "matrix_archive_sha256": sha256_file(FOUR_MATRICES),
            "exact_ldl_archive_sha256": sha256_file(FOUR_LDL),
            "negative_blocks": [], "exact_status": "PSD_ALL_NINE",
            "independent_audit": four_audit["claim_label"],
        },
        "logical_conclusion": {
            "current_frozen_order8_relaxation_at_T0": "EXACTLY FEASIBLE AT AN INTEGRAL PSEUDOCOUNT",
            "positive_E0_lower_bound_from_this_relaxation": "IMPOSSIBLE",
            "next_required_information": "higher-order synchronization or graph-realizability constraints",
            "graph_constructed": False,
            "endpoint_excluded": False,
            "Conway_99_problem": "OPEN",
        },
        "scope_boundary": {
            "complete_means": "the frozen universal linear rows, order-7/8 nonnegative integral cone, all Wave147 pair-root blocks, and all nine Wave152 four-root covariance blocks currently in this lane",
            "does_not_mean": "all conceivable order-8 inequalities or existence of a graph realizing the pseudocount",
        },
        "inputs_sha256": {str(path.relative_to(ROOT)): sha256_file(path) for path in inputs},
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": OUTPUT.name, "claim": result["claim_label"],
        "x7_sha256": result["integral_pseudocount"]["order7_vector_sha256"],
        "x8_sha256": result["integral_pseudocount"]["order8_vector_sha256"],
        "pair_root_ranks": {key: value["rank"] for key, value in result["wave147_pair_root_covariance"]["blocks"].items()},
        "four_root_ranks": {row["root_mask"]: row["rank"] for row in four_table},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
