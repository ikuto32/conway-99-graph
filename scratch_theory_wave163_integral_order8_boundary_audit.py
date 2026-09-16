#!/usr/bin/env python3
"""Clean-room aggregator audit for the Wave163 integral order-8 boundary.

No producer is imported and no graph-class catalogue or coefficient matrix is
regenerated.  Existing frozen streams and independently produced audit files
are reread, their hashes are cross-bound, the 208/916 count vectors are
reconstructed from the saved affine kernel, and the archived Wave147/Wave152
matrices are checked directly.
"""

from __future__ import annotations

import ctypes
import gzip
import hashlib
import json
import math
import time
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parent
EXT = ROOT / "external_conway99_research"
COEFFICIENT = EXT / "attempts/wave147-alternative-lane/coefficients.json.gz"
MARKED = EXT / "attempts/wave148-marked-order8/marked-rows.json.gz"
REFERENCE = EXT / "attempts/wave159-four-root-cut-loop/four-root-evaluation-after-fifteen-cuts.json"
SIX_SOURCE = EXT / "verification/wave43-seven-deck-endpoint/independent_check.py"
SIX_RESULT = EXT / "verification/wave43-seven-deck-endpoint/independent-result.json"
KERNEL = ROOT / "scratch_theory_wave163_coupled_kernel_basis.json.gz"
COUPLED = ROOT / "scratch_theory_wave163_coupled_pencil.json"
COUPLED_AUDIT = ROOT / "scratch_theory_wave163_coupled_pencil_independent_audit.json"
LATTICE = ROOT / "scratch_theory_wave163_integer_lattice.json"
LATTICE_AUDIT = ROOT / "scratch_theory_wave163_integer_lattice_audit.json"
PAIR = ROOT / "scratch_theory_wave163_integer_pair_root_blocks.json"
PAIR_AUDIT = ROOT / "scratch_theory_wave163_integer_pair_root_blocks_audit.json"
PAIR_MATRICES = ROOT / "scratch_theory_wave163_integer_pair_root_blocks_matrices.json.gz"
FOUR = ROOT / "scratch_theory_wave163_integer_all_four_root_blocks.json"
FOUR_AUDIT = ROOT / "scratch_theory_wave163_integer_all_four_root_blocks_audit.json"
FOUR_MATRICES = ROOT / "scratch_theory_wave163_integer_all_four_root_blocks_matrices.json.gz"
FOUR_LDL = ROOT / "scratch_theory_wave163_integer_all_four_root_blocks_ldl.json.gz"
CONSOLIDATED = ROOT / "scratch_theory_wave163_integral_order8_boundary.json"
OUTPUT = ROOT / "scratch_theory_wave163_integral_order8_boundary_audit.json"
H_DELTA_MASK = 120568
EXPECTED_ROOTS = (0, 1, 3, 7, 11, 12, 13, 15, 30)
EXPECTED_FOUR = {
    0: (224, 38), 1: (201, 27), 3: (155, 15), 7: (99, 3),
    11: (69, 3), 12: (178, 16), 13: (125, 6), 15: (60, 0), 30: (70, 0),
}


class MemoryStatusEx(ctypes.Structure):
    _fields_ = [
        ("length", ctypes.c_ulong), ("memory_load", ctypes.c_ulong),
        ("total_phys", ctypes.c_ulonglong), ("avail_phys", ctypes.c_ulonglong),
        ("total_page_file", ctypes.c_ulonglong), ("avail_page_file", ctypes.c_ulonglong),
        ("total_virtual", ctypes.c_ulonglong), ("avail_virtual", ctypes.c_ulonglong),
        ("avail_extended_virtual", ctypes.c_ulonglong),
    ]


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


def memory_record(label: str) -> dict[str, object]:
    status = MemoryStatusEx()
    status.length = ctypes.sizeof(status)
    require(bool(ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status))), "memory query failed")
    free = 100.0 * status.avail_phys / status.total_phys
    require(free >= 18.0, f"{label}: free memory {free:.2f}% below 18% gate")
    return {"label": label, "free_physical_memory_percent": round(free, 4)}


def relative_key(path: Path) -> str:
    return str(path.relative_to(ROOT))


def verify_manifest_hash(manifest: dict, path: Path, label: str) -> str:
    keys = (relative_key(path), relative_key(path).replace("\\", "/"), path.name)
    key = next((candidate for candidate in keys if candidate in manifest), None)
    require(key is not None, f"{label}: no manifest entry for {path.name}")
    actual = sha256_file(path)
    require(manifest[key] == actual, f"{label}: hash mismatch for {path.name}")
    return actual


def reconstruct_counts(coefficient: dict, lattice: dict) -> tuple[list[int], list[int], list[int], list[int]]:
    family_streams = []
    for family in ("ordered_edge", "ordered_nonedge"):
        streams = {7: [], 8: []}
        records = coefficient["families"][family]["class_coefficients"]
        require(len(records) == 1207, f"{family}: class-matrix record count drift")
        order_histogram = {order: 0 for order in range(5, 9)}
        for record in records:
            order = int(record["order"])
            order_histogram[order] += 1
            if order in streams:
                streams[order].append(int(record["canonical_mask"]))
        require(order_histogram == {5: 21, 6: 62, 7: 208, 8: 916}, f"{family}: stream histogram drift")
        family_streams.append(streams)
    require(family_streams[0] == family_streams[1], "two Wave147 families use different class streams")
    masks7, masks8 = family_streams[0][7], family_streams[0][8]

    kernel = load_gzip(KERNEL)
    basis = [[Fraction(0) for _ in range(8)] for _ in range(917)]
    for column, sparse in enumerate(kernel["universal_nullspace_basis_sparse"]):
        for row, value in sparse:
            basis[int(row)][column] = Fraction(value)
    require(len(kernel["universal_nullspace_basis_sparse"]) == 8, "universal nullity drift")
    t = list(map(Fraction, lattice["certificate"]["t_integral_free_x8_coordinates"]))
    require(len(t) == 8 and all(value.denominator == 1 for value in t), "integral free coordinates drift")
    x8f = [sum(basis[1 + row][column] * t[column] for column in range(8)) for row in range(916)]
    require(all(value.denominator == 1 and value >= 0 for value in x8f), "reconstructed x8 is not nonnegative integral")
    x8 = [value.numerator for value in x8f]

    index7 = {mask: index for index, mask in enumerate(masks7)}
    index8 = {mask: index for index, mask in enumerate(masks8)}
    rows: list[dict[int, int] | None] = [None] * 208
    deletion_records = coefficient["order7_to_order8_deletion_equations"]
    require(len(deletion_records) == 208, "deletion equation count drift")
    for record in deletion_records:
        rows[index7[int(record["order7_mask"])]] = {
            index8[int(mask)]: int(multiplicity)
            for mask, multiplicity in record["terms_order8_mask_multiplicity"]
        }
    require(all(row is not None for row in rows), "missing deletion equation")
    x7f = [
        sum(Fraction(mult) * x8[column] for column, mult in row.items()) / 92
        for row in rows if row is not None
    ]
    require(all(value.denominator == 1 and value >= 0 for value in x7f), "reconstructed x7 is not nonnegative integral")
    return masks7, [value.numerator for value in x7f], masks8, x8


def audit_pair_archive(pair_audit: dict, consolidated: dict) -> dict[str, object]:
    archive = load_gzip(PAIR_MATRICES)
    blocks = {block["family"]: block["matrix"] for block in archive["blocks"]}
    require(set(blocks) == {"ordered_edge", "ordered_nonedge"}, "pair matrix family drift")
    result = {}
    for family, expected_size in (("ordered_edge", 66), ("ordered_nonedge", 87)):
        matrix = blocks[family]
        require(len(matrix) == expected_size and all(len(row) == expected_size for row in matrix), f"{family}: size drift")
        require(all(matrix[i][j] == matrix[j][i] for i in range(expected_size) for j in range(expected_size)), f"{family}: asymmetry")
        pivot = int(matrix[0][0])
        require(pivot > 0, f"{family}: nonpositive pivot")
        require(all(
            pivot * int(matrix[i][j]) == int(matrix[i][0]) * int(matrix[0][j])
            for i in range(expected_size) for j in range(expected_size)
        ), f"{family}: rank-one identity failed")
        expected = pair_audit["blocks"][family]
        require(canonical_sha256(matrix) == expected["matrix_sha256"], f"{family}: audit matrix hash drift")
        boundary_block = consolidated["wave147_pair_root_covariance"]["blocks"][family]
        require(boundary_block["matrix_sha256"] == expected["matrix_sha256"], f"{family}: consolidated matrix hash drift")
        require((boundary_block["size"], boundary_block["rank"], boundary_block["nullity"]) == (expected_size, 1, expected_size - 1), f"{family}: consolidated rank drift")
        result[family] = {
            "size": expected_size, "rank": 1, "nullity": expected_size - 1,
            "positive_pivot": str(pivot), "matrix_sha256": expected["matrix_sha256"],
            "rank_one_entries_verified": expected_size**2,
        }
    return result


def audit_four_archives(four_audit: dict, consolidated: dict) -> tuple[dict[str, object], int]:
    matrix_payload = load_gzip(FOUR_MATRICES)
    ldl_payload = load_gzip(FOUR_LDL)
    matrices = {int(block["root_mask"]): block for block in matrix_payload["blocks"]}
    factors = {int(block["root_mask"]): block for block in ldl_payload["blocks"]}
    require(tuple(sorted(matrices)) == tuple(sorted(factors)) == EXPECTED_ROOTS, "four-root archive root set drift")
    boundary_blocks = {int(block["root_mask"]): block for block in consolidated["wave152_four_root_covariance"]["all_nine_blocks"]}
    result = {}
    total_entries = 0
    for root in EXPECTED_ROOTS:
        matrix = matrices[root]["centered_matrix"]
        size, rank = EXPECTED_FOUR[root]
        require(len(matrix) == size and all(len(row) == size for row in matrix), f"root {root}: matrix size drift")
        require(all(matrix[i][j] == matrix[j][i] for i in range(size) for j in range(size)), f"root {root}: asymmetry")
        digest = canonical_sha256(matrix)
        audited = four_audit["blocks"][str(root)]
        require(digest == audited["matrix_sha256"] == boundary_blocks[root]["matrix_sha256"], f"root {root}: matrix hash chain drift")
        factor = factors[root]
        require((int(factor["size"]), int(factor["rank"])) == (size, rank), f"root {root}: LDL metadata drift")
        require(len(factor["positive_diagonal"]) == rank and all(Fraction(value) > 0 for value in factor["positive_diagonal"]), f"root {root}: LDL diagonal drift")
        require(len(factor["rectangular_L_sparse"]) == size, f"root {root}: LDL row count drift")
        lower = [[Fraction(0) for _ in range(rank)] for _ in range(size)]
        for row, sparse in enumerate(factor["rectangular_L_sparse"]):
            for column, value in sparse:
                lower[row][int(column)] = Fraction(value)
        diagonal = list(map(Fraction, factor["positive_diagonal"]))
        for i in range(size):
            for j in range(size):
                reconstructed = sum(lower[i][k] * diagonal[k] * lower[j][k] for k in range(rank))
                require(reconstructed == matrix[i][j], f"root {root}: exact LDL reconstruction failed")
        identically_zero = not any(value for row in matrix for value in row)
        require(identically_zero == (root in (15, 30)), f"root {root}: zero-face drift")
        require((audited["size"], audited["rank"], audited["nullity"]) == (size, rank, size - rank), f"root {root}: audit rank drift")
        total_entries += size**2
        result[str(root)] = {
            "size": size, "rank": rank, "nullity": size - rank,
            "matrix_sha256": digest, "identically_zero": identically_zero,
            "exact_LDL_entries_reconstructed": size**2,
        }
    require(total_entries == 184973, "four-root entry census drift")
    return result, total_entries


def main() -> int:
    started = time.time()
    memory = [memory_record("aggregator_start")]
    consolidated = load_json(CONSOLIDATED)
    coupled = load_json(COUPLED)
    coupled_audit = load_json(COUPLED_AUDIT)
    lattice = load_json(LATTICE)
    lattice_audit = load_json(LATTICE_AUDIT)
    pair = load_json(PAIR)
    pair_audit = load_json(PAIR_AUDIT)
    four = load_json(FOUR)
    four_audit = load_json(FOUR_AUDIT)

    require(consolidated["claim_label"] == "EXPLICIT_INTEGRAL_FEASIBLE_BOUNDARY_FOR_CURRENT_ORDER8_RELAXATION", "consolidated claim drift")
    expected_claims = {
        "coupled": (coupled["claim_label"], "EXACT_KERNEL_FOUND"),
        "coupled_audit": (coupled_audit["claim_label"], "VERIFIED_SCOPED_COMPRESSED_CONIC_NULL"),
        "lattice": (lattice["claim_label"], "EXACT_INTEGRAL_COMPRESSED_PRIMAL_FEASIBLE"),
        "lattice_audit": (lattice_audit["claim_label"], "INDEPENDENT_EXACT_INTEGRAL_COMPRESSED_FEASIBILITY_PASS"),
        "pair": (pair["claim_label"], "EXACT_PAIR_ROOT_PSD_PASS"),
        "pair_audit": (pair_audit["claim_label"], "INDEPENDENT_EXACT_INTEGER_PAIR_ROOT_PSD_PASS"),
        "four": (four["claim_label"], "EXACT_ALL_NINE_FOUR_ROOT_PSD_PASS"),
        "four_audit": (four_audit["claim_label"], "INDEPENDENT_EXACT_ALL_NINE_FOUR_ROOT_PSD_PASS"),
    }
    require(all(actual == expected for actual, expected in expected_claims.values()), "upstream status chain drift")

    # First bind every file named by the consolidated producer to its current bytes.
    consolidated_hashes = consolidated["inputs_sha256"]
    consolidated_inputs = (
        COEFFICIENT, KERNEL, COUPLED, COUPLED_AUDIT, LATTICE, LATTICE_AUDIT,
        PAIR, PAIR_AUDIT, FOUR, FOUR_AUDIT, FOUR_MATRICES, FOUR_LDL,
    )
    actual_hashes = {relative_key(path): verify_manifest_hash(consolidated_hashes, path, "consolidated") for path in consolidated_inputs}

    # Then verify the cross-audit hash chain for the shared frozen inputs/control.
    shared_bindings = {
        "coefficient_archive": {
            "sha256": sha256_file(COEFFICIENT),
            "verified_by": [
                name for name, audit in (
                    ("coupled_audit", coupled_audit), ("lattice_audit", lattice_audit),
                    ("pair_audit", pair_audit), ("four_audit", four_audit),
                ) if verify_manifest_hash(audit["inputs_sha256"], COEFFICIENT, name)
            ],
        },
        "affine_kernel": {
            "sha256": sha256_file(KERNEL),
            "verified_by": [
                name for name, audit in (
                    ("coupled_audit", coupled_audit), ("lattice_audit", lattice_audit),
                    ("pair_audit", pair_audit), ("four_audit", four_audit),
                ) if verify_manifest_hash(audit["inputs_sha256"], KERNEL, name)
            ],
        },
        "integer_control": {
            "sha256": sha256_file(LATTICE),
            "verified_by": [
                name for name, audit in (("lattice_audit", lattice_audit), ("pair_audit", pair_audit), ("four_audit", four_audit))
                if verify_manifest_hash(audit["inputs_sha256"], LATTICE, name)
            ],
        },
    }
    verify_manifest_hash(pair_audit["inputs_sha256"], PAIR, "pair_audit")
    verify_manifest_hash(pair_audit["inputs_sha256"], PAIR_MATRICES, "pair_audit")
    verify_manifest_hash(four_audit["inputs_sha256"], FOUR, "four_audit")
    verify_manifest_hash(four_audit["inputs_sha256"], FOUR_MATRICES, "four_audit")
    verify_manifest_hash(four_audit["inputs_sha256"], FOUR_LDL, "four_audit")
    verify_manifest_hash(four_audit["inputs_sha256"], REFERENCE, "four_audit")
    verify_manifest_hash(four_audit["inputs_sha256"], SIX_SOURCE, "four_audit")
    verify_manifest_hash(four_audit["inputs_sha256"], SIX_RESULT, "four_audit")

    coefficient = load_gzip(COEFFICIENT)
    marked = load_gzip(MARKED)
    verify_manifest_hash(coupled_audit["inputs_sha256"], MARKED, "coupled_audit")
    require((len(marked["vertex_rows"]), len(marked["ordered_pair_rows"])) == (944, 4440), "marked row census drift")
    frozen = coupled["frozen_inputs_consumed_not_regenerated"]
    require(frozen == {
        "order8_classes": 916, "ordinary_deletion_rows": 208,
        "marked_vertex_rows": 944, "marked_pair_rows": 4440,
        "wave147_class_matrices": 2414,
    }, "coupled frozen census drift")
    require(pair_audit["coefficient_census"] == {
        "all_2414_class_matrices_consumed": True,
        "class_matrix_records": 2414,
        "nonzero_upper_coefficients": 272054,
    }, "pair coefficient census drift")
    memory.append(memory_record("aggregator_hash_chain_complete"))

    masks7, x7, masks8, x8 = reconstruct_counts(coefficient, lattice)
    x7_pairs = [[mask, count] for mask, count in zip(masks7, x7, strict=True)]
    x8_pairs = [[mask, count] for mask, count in zip(masks8, x8, strict=True)]
    stored = consolidated["integral_pseudocount"]
    require(stored["order7_mask_count_pairs"] == x7_pairs, "consolidated x7 vector mismatch")
    require(stored["order8_mask_count_pairs"] == x8_pairs, "consolidated x8 vector mismatch")
    require(stored["order7_vector_sha256"] == canonical_sha256(x7_pairs), "x7 vector hash drift")
    require(stored["order8_vector_sha256"] == canonical_sha256(x8_pairs), "x8 vector hash drift")
    require((sum(x7), sum(x8)) == (math.comb(99, 7), math.comb(99, 8)), "count totals drift")
    require((x7.count(0), x8.count(0)) == (4, 26), "count zero-face drift")
    require(x7[masks7.index(H_DELTA_MASK)] == 0, "H_delta count is nonzero")
    t = list(map(int, lattice["certificate"]["t_integral_free_x8_coordinates"]))
    require(t == stored["free_coordinates_t"], "free-coordinate binding drift")
    require(-t[2] + 3 * t[3] + t[4] == 1247400, "endpoint affine equation drift")
    count_audit = lattice_audit["count_audit"]
    require(count_audit["endpoint_n3"] == 4158, "n3 audit drift")
    require(count_audit["endpoint_prism_count_from_n3_plus_3P_equals_4158"] == "0", "P audit drift")
    require(count_audit["H_delta_count"] == "0" and count_audit["sum_E0_from_6P_plus_H_delta"] == "0", "T=0/E0 audit drift")
    require(consolidated["endpoint"] == {
        "H_delta": 0, "P": 0, "identities": ["n3+3P=4158", "sum_r E0(r)=6P+N(H_delta)"],
        "n3": 4158, "sum_E0": 0,
        "therefore_pointwise_E0": "E0(r)=0 for every root, since E0(r)>=0",
    }, "consolidated endpoint drift")
    memory.append(memory_record("aggregator_counts_complete"))

    pair_blocks = audit_pair_archive(pair_audit, consolidated)
    memory.append(memory_record("aggregator_pair_complete"))
    four_blocks, total_four_entries = audit_four_archives(four_audit, consolidated)
    memory.append(memory_record("aggregator_four_complete"))

    result = {
        "format": "wave163-integral-order8-boundary-clean-room-aggregator-audit-v1",
        "claim_label": "INDEPENDENT_INTEGRAL_ORDER8_BOUNDARY_BINDING_PASS",
        "method": {
            "consolidated_producer_imported": False,
            "other_producer_modules_imported": False,
            "graph_classes_regenerated": False,
            "coefficient_matrices_regenerated": False,
            "frozen_archives_reread": True,
            "all_upstream_statuses_reread": True,
            "all_cross_referenced_hashes_checked_against_current_bytes": True,
        },
        "upstream_status_chain": {name: actual for name, (actual, _) in expected_claims.items()},
        "same_frozen_data_binding": shared_bindings,
        "frozen_census": {
            "order7_classes_and_deletion_rows": 208, "order8_classes": 916,
            "marked_vertex_rows": 944, "marked_pair_rows": 4440,
            "Wave147_class_matrix_records": 2414,
        },
        "integral_count_replay": {
            "free_coordinates_t": t,
            "x7_entries": 208, "x8_entries": 916,
            "x7_mask_count_sha256": canonical_sha256(x7_pairs),
            "x8_mask_count_sha256": canonical_sha256(x8_pairs),
            "x7_sum": str(sum(x7)), "x8_sum": str(sum(x8)),
            "x7_zero_count": x7.count(0), "x8_zero_count": x8.count(0),
            "all_nonnegative_integral": True,
            "consolidated_vectors_match_entrywise": True,
        },
        "endpoint_replay": {
            "endpoint_affine_equation": "-t2+3*t3+t4=1247400",
            "n3": 4158, "P": 0, "H_delta": 0, "sum_E0": 0,
            "pointwise_E0_zero_follows_from_nonnegativity": True,
        },
        "Wave147_pair_root_archive_replay": {
            "all_2414_records_reported_consumed": True,
            "nonzero_upper_coefficients": 272054,
            "blocks": pair_blocks,
        },
        "Wave152_four_root_archive_replay": {
            "blocks": four_blocks,
            "all_nine_exact_PSD": True,
            "total_exact_LDL_entries_reconstructed": total_four_entries,
            "negative_blocks": [],
        },
        "conclusion": {
            "same_integer_pseudocount_used_by_pair_and_four_root_audits": True,
            "same_frozen_coefficient_stream_used_throughout": True,
            "current_frozen_order8_relaxation_has_explicit_integral_T0_boundary": True,
            "endpoint_excluded": False,
            "graph_realizability_established": False,
            "Conway_99": "OPEN",
        },
        "rigorous_scope": {
            "established": "the specific 208/916 nonnegative integral pseudocount is on the T=0 face and passes the audited universal affine rows, all 2414 Wave147 pair-root records, and all nine archived Wave152 four-root covariance blocks",
            "not_established": "existence of a graph realizing the pseudocount, feasibility for every conceivable order-8 inequality, or existence/nonexistence of srg(99,14,1,2)",
        },
        "inputs_sha256": {
            **actual_hashes,
            relative_key(CONSOLIDATED): sha256_file(CONSOLIDATED),
            relative_key(MARKED): sha256_file(MARKED),
            relative_key(PAIR_MATRICES): sha256_file(PAIR_MATRICES),
            relative_key(REFERENCE): sha256_file(REFERENCE),
            relative_key(SIX_SOURCE): sha256_file(SIX_SOURCE),
            relative_key(SIX_RESULT): sha256_file(SIX_RESULT),
        },
        "resource_guard": {
            "minimum_required": 18.0,
            "minimum_observed": min(float(record["free_physical_memory_percent"]) for record in memory),
            "samples": memory,
        },
        "elapsed_seconds": time.time() - started,
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": OUTPUT.name, "claim": result["claim_label"],
        "x7_sha256": result["integral_count_replay"]["x7_mask_count_sha256"],
        "x8_sha256": result["integral_count_replay"]["x8_mask_count_sha256"],
        "pair_ranks": {name: block["rank"] for name, block in pair_blocks.items()},
        "four_ranks": {root: block["rank"] for root, block in four_blocks.items()},
        "elapsed_seconds": result["elapsed_seconds"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
