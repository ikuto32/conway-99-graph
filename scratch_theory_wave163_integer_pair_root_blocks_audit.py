#!/usr/bin/env python3
"""Independent exact audit of the integer control in both Wave147 blocks."""

from __future__ import annotations

import ast
import ctypes
import gzip
import hashlib
import json
import math
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parent
EXT = ROOT / "external_conway99_research"
COEFFICIENTS = EXT / "attempts/wave147-alternative-lane/coefficients.json.gz"
W147_RESULT = EXT / "attempts/wave147-alternative-lane/exact-results.json"
SIX_SOURCE = EXT / "verification/wave43-seven-deck-endpoint/independent_check.py"
SIX_RESULT = EXT / "verification/wave43-seven-deck-endpoint/independent-result.json"
CONTROL = ROOT / "scratch_theory_wave163_integer_lattice.json"
CONTROL_AUDIT = ROOT / "scratch_theory_wave163_integer_lattice_audit.json"
KERNEL = ROOT / "scratch_theory_wave163_coupled_kernel_basis.json.gz"
DISCOVERY = ROOT / "scratch_theory_wave163_integer_pair_root_blocks.json"
MATRIX_ARCHIVE = ROOT / "scratch_theory_wave163_integer_pair_root_blocks_matrices.json.gz"
OUTPUT = ROOT / "scratch_theory_wave163_integer_pair_root_blocks_audit.json"
M_TO_CANONICAL_POSITIONS = (
    0, 1, 2, 6, 3, 9, 7, 5, 4, 12, 10, 8, 13, 16, 15, 14, 11, 19, 18, 20, 17
)


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


def memory_record(label: str) -> dict[str, object]:
    status = MemoryStatusEx()
    status.length = ctypes.sizeof(status)
    require(bool(ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status))), "memory query failed")
    free = 100.0 * status.avail_phys / status.total_phys
    require(free >= 18.0, f"{label}: free memory {free:.2f}% below 18% gate")
    return {"label": label, "free_physical_memory_percent": round(free, 4)}


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
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()


def streams(payload: dict) -> dict[int, tuple[int, ...]]:
    families = []
    for family in ("ordered_edge", "ordered_nonedge"):
        local = {order: [] for order in range(5, 9)}
        for record in payload["families"][family]["class_coefficients"]:
            local[int(record["order"])].append(int(record["canonical_mask"]))
        families.append({order: tuple(values) for order, values in local.items()})
    require(families[0] == families[1], "family streams differ")
    require(tuple(len(families[0][order]) for order in range(5, 9)) == (21, 62, 208, 916), "stream census drift")
    return families[0]


def source_six_masks() -> tuple[int, ...]:
    tree = ast.parse(SIX_SOURCE.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "SOURCE_N_MASKS" for target in node.targets):
            return tuple(map(int, ast.literal_eval(node.value)))
    raise AssertionError("SOURCE_N_MASKS missing")


def five_counts() -> tuple[int, ...]:
    n, k = 99, 14
    common = n * k * (k - 2)
    values = (
        Fraction(common * (k - 4) * (n - 4 * k + 6) * (k**3 - 6 * k**2 + 14 * k - 36), 960),
        Fraction(common * (k - 4) ** 2 * (k**3 - 8 * k**2 + 26 * k - 48), 96),
        Fraction(common * (k - 4) * (k**3 - 10 * k**2 + 38 * k - 60), 16),
        Fraction(common * (k - 4) * (k**3 - 10 * k**2 + 40 * k - 68), 32),
        Fraction(common * (k - 4) * (n - 4 * k + 8), 6),
        Fraction(common * (k - 4) * (k**2 - 8 * k + 20), 8),
        Fraction(common * (k - 4) * (k**2 - 7 * k + 16), 4),
        Fraction(common * (k - 4) * (n - 4 * k + 8), 24),
        Fraction(common * (k - 4) * (k - 6), 24),
        Fraction(common * (n - 4 * k + 8), 8),
        Fraction(common * (k - 4) ** 2, 2),
        Fraction(common * (k - 4) ** 2, 4),
        Fraction(common * (k**2 - 8 * k + 17), 2),
        Fraction(common * (k - 4) * (k - 6), 24),
        Fraction(common * (k - 4), 2),
        Fraction(common * (k - 3), 2),
        Fraction(common * (k - 4), 4),
        Fraction(common * (k - 4), 5),
        Fraction(common, 8),
        Fraction(common, 2),
        Fraction(common * (k - 4), 2),
    )
    require(all(value.denominator == 1 for value in values), "five-count formula nonintegral")
    return tuple(value.numerator for value in values)


def reconstruct_counts(payload: dict, class_streams: dict[int, tuple[int, ...]]) -> dict[int, dict[int, int]]:
    values5 = five_counts()
    count5 = {class_streams[5][position]: values5[source] for source, position in enumerate(M_TO_CANONICAL_POSITIONS)}
    independent = load_json(SIX_RESULT)
    masks6 = source_six_masks()
    values6 = tuple(map(int, independent["model"]["six_counts"]))
    require(canonical_sha256(masks6) == independent["model"]["six_source_masks_sha256"], "six masks hash mismatch")
    require(canonical_sha256(values6) == independent["model"]["six_counts_sha256"], "six counts hash mismatch")
    count6 = dict(zip(masks6, values6, strict=True))
    kernel = load_gzip(KERNEL)
    t = list(map(Fraction, load_json(CONTROL)["certificate"]["t_integral_free_x8_coordinates"]))
    nullspace = [[Fraction(0) for _ in range(8)] for _ in range(917)]
    for column, entries in enumerate(kernel["universal_nullspace_basis_sparse"]):
        for row, value in entries:
            nullspace[int(row)][column] = Fraction(value)
    count8_values = [sum(nullspace[1 + row][column] * t[column] for column in range(8)) for row in range(916)]
    require(all(value.denominator == 1 and value >= 0 for value in count8_values), "order-eight count failure")
    count8 = [value.numerator for value in count8_values]
    index7 = {mask: index for index, mask in enumerate(class_streams[7])}
    index8 = {mask: index for index, mask in enumerate(class_streams[8])}
    deletion: list[dict[int, int] | None] = [None] * 208
    for record in payload["order7_to_order8_deletion_equations"]:
        require(int(record["left_multiplier"]) == 92, "deletion multiplier drift")
        deletion[index7[int(record["order7_mask"])]] = {
            index8[int(mask)]: int(mult) for mask, mult in record["terms_order8_mask_multiplicity"]
        }
    require(all(row is not None for row in deletion), "missing deletion row")
    count7_values = [sum(Fraction(mult) * count8[column] for column, mult in row.items()) / 92 for row in deletion if row is not None]
    require(all(value.denominator == 1 and value >= 0 for value in count7_values), "order-seven count failure")
    result = {
        5: count5,
        6: {mask: count6[mask] for mask in class_streams[6]},
        7: {mask: count7_values[index].numerator for index, mask in enumerate(class_streams[7])},
        8: {mask: count8[index] for index, mask in enumerate(class_streams[8])},
    }
    require(tuple(sum(result[order].values()) for order in range(5, 9)) == tuple(math.comb(99, order) for order in range(5, 9)), "count totals drift")
    return result


def rank_one_psd_certificate(matrix: list[list[int]]) -> dict[str, object]:
    size = len(matrix)
    require(matrix == [list(row) for row in zip(*matrix)], "matrix asymmetric")
    require(all(matrix[index][index] >= 0 for index in range(size)), "negative diagonal")
    pivot = next((index for index in range(size) if matrix[index][index] > 0), None)
    require(pivot is not None, "zero matrix unexpected")
    diagonal = matrix[pivot][pivot]
    for row in range(size):
        for column in range(size):
            require(
                diagonal * matrix[row][column] == matrix[row][pivot] * matrix[pivot][column],
                f"rank-one identity failed at {row},{column}",
            )
    return {
        "rank": 1,
        "nullity": size - 1,
        "positive_pivot_index": pivot,
        "positive_pivot": str(diagonal),
        "pivot_column_sha256": canonical_sha256([matrix[row][pivot] for row in range(size)]),
        "identity": "M[p,p]*M[i,j]=M[i,p]*M[p,j] for every i,j",
        "quadratic_form": "v^T M v=(sum_i M[i,p]v_i)^2/M[p,p]>=0",
        "entries_verified": size * size,
    }


def main() -> int:
    memory = [memory_record("pair_root_audit_start")]
    payload = load_gzip(COEFFICIENTS)
    class_streams = streams(payload)
    counts = reconstruct_counts(payload, class_streams)
    discovery = load_json(DISCOVERY)
    require(discovery["claim_label"] == "EXACT_PAIR_ROOT_PSD_PASS", "discovery verdict drift")
    with gzip.open(MATRIX_ARCHIVE, "rt", encoding="ascii") as handle:
        archived = json.load(handle)
    archive_blocks = {record["family"]: record["matrix"] for record in archived["blocks"]}
    discovery_blocks = {record["family"]: record for record in discovery["blocks"]}
    audit_blocks = {}
    total_records = total_upper = 0
    for family_name in ("ordered_edge", "ordered_nonedge"):
        family = payload["families"][family_name]
        size = int(family["matrix_size"])
        matrix = [[0] * size for _ in range(size)]
        records = upper = 0
        for record in family["class_coefficients"]:
            records += 1
            weight = counts[int(record["order"])][int(record["canonical_mask"])]
            for row, column, value in record["upper_entries"]:
                row, column, value = int(row), int(column), int(value)
                matrix[row][column] += weight * value
                if row != column:
                    matrix[column][row] += weight * value
                upper += 1
        total_records += records
        total_upper += upper
        require(matrix == archive_blocks[family_name], f"{family_name} archived matrix mismatch")
        require(canonical_sha256(matrix) == discovery_blocks[family_name]["matrix_sha256"], "matrix hash mismatch")
        root_embeddings = 99 * (14 if family_name == "ordered_edge" else 84)
        expected_sum = root_embeddings * math.comb(97, 3) ** 2
        require(sum(map(sum, matrix)) == expected_sum, "Gram total mismatch")
        certificate = rank_one_psd_certificate(matrix)
        require(discovery_blocks[family_name]["exact_psd_certificate"]["rank"] == 1, "producer rank mismatch")
        audit_blocks[family_name] = {
            "size": size,
            "class_matrix_records": records,
            "nonzero_upper_coefficients": upper,
            "matrix_sha256": canonical_sha256(matrix),
            "sum_all_entries": str(expected_sum),
            "exact_rank_one_psd": certificate,
        }
        memory.append(memory_record(f"pair_root_audit_{family_name}"))
    require(total_records == 2414 and total_upper == 272_054, "coefficient census mismatch")
    result = {
        "format": "wave163-integer-control-wave147-pair-root-independent-audit-v1",
        "claim_label": "INDEPENDENT_EXACT_INTEGER_PAIR_ROOT_PSD_PASS",
        "inputs_sha256": {str(path.relative_to(ROOT)): sha256_file(path) for path in (
            COEFFICIENTS, W147_RESULT, SIX_SOURCE, SIX_RESULT, CONTROL, CONTROL_AUDIT,
            KERNEL, DISCOVERY, MATRIX_ARCHIVE,
        )},
        "coefficient_census": {
            "all_2414_class_matrices_consumed": True,
            "class_matrix_records": total_records,
            "nonzero_upper_coefficients": total_upper,
        },
        "blocks": audit_blocks,
        "conclusion": {
            "ordered_edge_66x66": "exact PSD rank 1",
            "ordered_nonedge_87x87": "exact PSD rank 1",
            "negative_direction": "NONE",
            "new_scalar_cut": "NONE",
            "endpoint_exclusion": "NOT_ESTABLISHED",
        },
        "scope_boundary": {"integer_counts_are_graph_realizable": False, "other_constraints": "NOT IMPLIED", "Conway_99": "UNKNOWN"},
        "resource_guard": {"minimum_required": 18.0, "minimum_observed": min(float(item["free_physical_memory_percent"]) for item in memory), "samples": memory},
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": OUTPUT.name, "claim": result["claim_label"], "census": result["coefficient_census"], "ranks": {name: record["exact_rank_one_psd"]["rank"] for name, record in audit_blocks.items()}}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
