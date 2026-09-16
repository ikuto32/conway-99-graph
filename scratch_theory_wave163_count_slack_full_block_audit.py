#!/usr/bin/env python3
"""Clean-room replay of the Wave163 exact-control full root-3/12 blocks.

No discovery/producer module is imported.  The 62/208/916 frozen class
streams and the saved eight-dimensional control are read directly, all
rooted embeddings are streamed again, every matrix entry is compared with
the producer archive, and PSD is proved by an independent exact LDL^T replay.
"""

from __future__ import annotations

import argparse
import ast
import ctypes
import gzip
import hashlib
import itertools
import json
import math
import time
from fractions import Fraction
from pathlib import Path
from typing import Sequence


ROOT = Path(__file__).resolve().parent
EXT = ROOT / "external_conway99_research"
COEFFICIENT_ARCHIVE = EXT / "attempts/wave147-alternative-lane/coefficients.json.gz"
SIX_SOURCE = EXT / "verification/wave43-seven-deck-endpoint/independent_check.py"
SIX_RESULT = EXT / "verification/wave43-seven-deck-endpoint/independent-result.json"
REFERENCE = EXT / "attempts/wave159-four-root-cut-loop/four-root-evaluation-after-fifteen-cuts.json"
CUT_PATHS = (
    EXT / "attempts/wave152-four-root-order8/exact-cuts.json",
    EXT / "attempts/wave152-four-root-order8/iteration2-cuts.json",
    EXT / "attempts/wave152-four-root-order8/iteration3-mask13-cut.json",
    EXT / "attempts/wave152-four-root-order8/iteration4-three-cuts.json",
    EXT / "attempts/wave152-four-root-order8/simplified-mask12-cut.json",
    EXT / "attempts/wave152-four-root-order8/iteration5-three-cuts.json",
    EXT / "attempts/wave152-four-root-order8/simplified-mask12-cut-2.json",
    EXT / "attempts/wave159-four-root-cut-loop/fresh-two-cuts.json",
)
CONTROL = ROOT / "scratch_theory_wave163_count_slack_exact_control.json"
KERNEL = ROOT / "scratch_theory_wave163_coupled_kernel_basis.json.gz"
COMPRESSED_ROWS = ROOT / "scratch_theory_wave163_coupled_pencil_coefficients.json.gz"
MATRIX_ARCHIVE = ROOT / "scratch_theory_wave163_count_slack_full_block_matrices.json.gz"
DISCOVERY = ROOT / "scratch_theory_wave163_count_slack_full_block.json"
EXACT_PSD = ROOT / "scratch_theory_wave163_count_slack_full_block_exact_psd.json"
OUTPUT = ROOT / "scratch_theory_wave163_count_slack_full_block_audit.json"
INTEGER_CONTROL = ROOT / "scratch_theory_wave163_integer_lattice.json"
INTEGER_MATRIX_ARCHIVE = ROOT / "scratch_theory_wave163_integer_lattice_full_block_matrices.json.gz"
INTEGER_DISCOVERY = ROOT / "scratch_theory_wave163_integer_lattice_full_block.json"
INTEGER_EXACT_PSD = ROOT / "scratch_theory_wave163_integer_lattice_full_block_exact_psd.json"
INTEGER_OUTPUT = ROOT / "scratch_theory_wave163_integer_lattice_full_block_audit.json"
ROOTS = (3, 12)
COUNT_SCALE = 40_000


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


def fstr(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def edges(order: int) -> tuple[tuple[int, int], ...]:
    return tuple((left, right) for left in range(order) for right in range(left + 1, order))


def edge_positions(order: int) -> dict[tuple[int, int], int]:
    return {edge: index for index, edge in enumerate(edges(order))}


def induced_mask(mask: int, order: int, chosen: Sequence[int]) -> int:
    source = edge_positions(order)
    result = 0
    target = 0
    for left_index, left in enumerate(chosen):
        for right in chosen[left_index + 1:]:
            if mask >> source[tuple(sorted((left, right)))] & 1:
                result |= 1 << target
            target += 1
    return result


def transform_mask(mask: int, order: int, permutation: Sequence[int]) -> int:
    source = edge_positions(order)
    result = 0
    for edge, position in source.items():
        if mask >> position & 1:
            image = tuple(sorted((permutation[edge[0]], permutation[edge[1]])))
            result |= 1 << source[image]
    return result


def canonical_flag(mask: int) -> int:
    return min(mask, transform_mask(mask, 6, (0, 1, 2, 3, 5, 4)))


def covering_pair_indices(complement_size: int) -> tuple[tuple[int, int], ...]:
    pairs = tuple(itertools.combinations(range(complement_size), 2))
    return tuple(
        (left, right)
        for left, first in enumerate(pairs)
        for right, second in enumerate(pairs)
        if len(set(first).union(second)) == complement_size
    )


def class_streams(payload: dict) -> dict[int, tuple[int, ...]]:
    families = []
    for name in ("ordered_edge", "ordered_nonedge"):
        streams = {order: [] for order in range(5, 9)}
        for record in payload["families"][name]["class_coefficients"]:
            streams[int(record["order"])].append(int(record["canonical_mask"]))
        families.append({order: tuple(values) for order, values in streams.items()})
    require(families[0] == families[1], "family stream mismatch")
    streams = families[0]
    require(tuple(len(streams[order]) for order in range(5, 9)) == (21, 62, 208, 916), "class census drift")
    return streams


def source_six_masks() -> tuple[int, ...]:
    tree = ast.parse(SIX_SOURCE.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "SOURCE_N_MASKS" for target in node.targets):
            value = ast.literal_eval(node.value)
            return tuple(map(int, value))
    raise AssertionError("SOURCE_N_MASKS not found")


def count_maps(
    streams: dict[int, tuple[int, ...]], coefficient: dict, control_path: Path,
    integer_control: bool,
) -> tuple[dict[int, dict[int, Fraction]], int]:
    kernel = load_gzip(KERNEL)
    control = load_json(control_path)["certificate"]
    nullspace = [[Fraction(0) for _ in range(8)] for _ in range(917)]
    for column, entries in enumerate(kernel["universal_nullspace_basis_sparse"]):
        for row, value in entries:
            nullspace[int(row)][column] = Fraction(value)
    t_key = "t_integral_free_x8_coordinates" if integer_control else "t_free_x8_coordinates"
    t = [Fraction(value) for value in control[t_key]]
    x8 = [sum(nullspace[1 + row][column] * t[column] for column in range(8)) for row in range(916)]
    index7 = {mask: index for index, mask in enumerate(streams[7])}
    index8 = {mask: index for index, mask in enumerate(streams[8])}
    deletion: list[dict[int, int] | None] = [None] * 208
    for record in coefficient["order7_to_order8_deletion_equations"]:
        deletion[index7[int(record["order7_mask"])]] = {
            index8[int(mask)]: int(mult)
            for mask, mult in record["terms_order8_mask_multiplicity"]
        }
    require(all(row is not None for row in deletion), "deletion row missing")
    x7 = [
        sum(Fraction(mult) * x8[column] for column, mult in row.items()) / 92
        for row in deletion if row is not None
    ]
    independent = load_json(SIX_RESULT)
    masks6 = source_six_masks()
    values6 = tuple(map(int, independent["model"]["six_counts"]))
    require(canonical_sha256(masks6) == independent["model"]["six_source_masks_sha256"], "six-mask hash drift")
    require(canonical_sha256(values6) == independent["model"]["six_counts_sha256"], "six-count hash drift")
    counts6 = dict(zip(masks6, values6, strict=True))
    require(set(counts6) == set(streams[6]), "six-mask stream set drift")
    counts = {
        6: {mask: Fraction(counts6[mask]) for mask in streams[6]},
        7: {mask: x7[index] for index, mask in enumerate(streams[7])},
        8: {mask: x8[index] for index, mask in enumerate(streams[8])},
    }
    count_scale = math.lcm(*(value.denominator for local in counts.values() for value in local.values()))
    require(count_scale == (1 if integer_control else COUNT_SCALE), "count scale drift")
    return counts, count_scale


def exact_ldl(matrix: Sequence[Sequence[int]]) -> tuple[list[int], list[Fraction], list[list[Fraction]]]:
    size = len(matrix)
    lower: list[list[Fraction]] = [[] for _ in range(size)]
    diagonal: list[Fraction] = []
    pivots: list[int] = []
    remaining = set(range(size))
    while True:
        residual_diagonal = {
            index: Fraction(matrix[index][index]) - sum(lower[index][k] ** 2 * diagonal[k] for k in range(len(diagonal)))
            for index in remaining
        }
        require(all(value >= 0 for value in residual_diagonal.values()), "negative Schur diagonal")
        positive = [index for index, value in residual_diagonal.items() if value]
        if not positive:
            break
        pivot = max(positive, key=residual_diagonal.__getitem__)
        d = residual_diagonal[pivot]
        column = []
        for row in range(size):
            residual = Fraction(matrix[row][pivot]) - sum(
                lower[row][k] * diagonal[k] * lower[pivot][k]
                for k in range(len(diagonal))
            )
            column.append(residual / d)
        for row in range(size):
            lower[row].append(column[row])
        diagonal.append(d)
        pivots.append(pivot)
        remaining.remove(pivot)
    for row in range(size):
        for column in range(size):
            require(
                sum(lower[row][k] * diagonal[k] * lower[column][k] for k in range(len(diagonal))) == matrix[row][column],
                "exact LDL reconstruction failure",
            )
    return pivots, diagonal, lower


def retained_directions(reference: dict) -> dict[int, list[list[int]]]:
    cuts = []
    for path in CUT_PATHS:
        payload = load_json(path)
        cuts.extend(payload["cuts"] if "cuts" in payload else [payload["cut"]])
    result = {}
    blocks = {int(block["root_mask"]): block for block in reference["root_blocks"]}
    for root in ROOTS:
        directions = [list(map(int, cut["direction"])) for cut in cuts if int(cut["root_mask"]) == root]
        recurrent = [0] * int(blocks[root]["flag_count"])
        certificate = blocks[root]["negative_certificate"]
        for index, value in zip(certificate["indices"], certificate["vector"], strict=True):
            recurrent[int(index)] = int(value)
        directions.append(recurrent)
        result[root] = directions
    require({root: len(result[root]) for root in ROOTS} == {3: 6, 12: 8}, "direction count drift")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--integer-control", action="store_true")
    args = parser.parse_args()
    control_path = INTEGER_CONTROL if args.integer_control else CONTROL
    matrix_archive_path = INTEGER_MATRIX_ARCHIVE if args.integer_control else MATRIX_ARCHIVE
    discovery_path = INTEGER_DISCOVERY if args.integer_control else DISCOVERY
    exact_psd_path = INTEGER_EXACT_PSD if args.integer_control else EXACT_PSD
    output_path = INTEGER_OUTPUT if args.integer_control else OUTPUT
    started = time.time()
    memory = [memory_record("full_block_audit_start")]
    coefficient = load_gzip(COEFFICIENT_ARCHIVE)
    streams = class_streams(coefficient)
    counts, count_scale = count_maps(streams, coefficient, control_path, args.integer_control)
    reference = load_json(REFERENCE)
    reference_blocks = {int(block["root_mask"]): block for block in reference["root_blocks"] if int(block["root_mask"]) in ROOTS}
    flags = {root: tuple(map(int, reference_blocks[root]["flag_masks"])) for root in ROOTS}
    flag_indices = {root: {mask: index for index, mask in enumerate(flags[root])} for root in ROOTS}
    moments = {root: [[0] * len(flags[root]) for _ in flags[root]] for root in ROOTS}
    first = {root: [0] * len(flags[root]) for root in ROOTS}
    enumeration = {}
    for order in (6, 7, 8):
        pair_indices = covering_pair_indices(order - 4)
        matched = products = 0
        for class_index, mask in enumerate(streams[order]):
            weight = counts[order][mask]
            if not weight:
                continue
            scaled = weight * count_scale
            require(scaled.denominator == 1, "scaled count nonintegral")
            vertices = tuple(range(order))
            for roots in itertools.permutations(vertices, 4):
                root = induced_mask(mask, order, roots)
                if root not in ROOTS:
                    continue
                matched += 1
                complement = tuple(vertex for vertex in vertices if vertex not in roots)
                free_pairs = tuple(itertools.combinations(complement, 2))
                positions = [
                    flag_indices[root][canonical_flag(induced_mask(mask, order, roots + pair))]
                    for pair in free_pairs
                ]
                if order == 6:
                    first[root][positions[0]] += int(scaled)
                for left, right in pair_indices:
                    moments[root][positions[left]][positions[right]] += int(scaled)
                    products += 1
            if class_index % 128 == 0:
                memory.append(memory_record(f"full_block_audit_o{order}_{class_index}"))
        enumeration[str(order)] = {"matched": matched, "products": products}
        memory.append(memory_record(f"full_block_audit_o{order}_complete"))

    with gzip.open(matrix_archive_path, "rt", encoding="ascii") as handle:
        archive = json.load(handle)
    archived = {int(block["root_mask"]): block for block in archive["blocks"]}
    exact_psd = load_json(exact_psd_path)
    compressed_rows = load_gzip(COMPRESSED_ROWS)["rows"]
    kernel = load_gzip(KERNEL)
    qmap = [[Fraction(value) for value in row] for row in kernel["compressed_quotient_map_57_by_8"]]
    control_certificate = load_json(control_path)["certificate"]
    t_key = "t_integral_free_x8_coordinates" if args.integer_control else "t_free_x8_coordinates"
    t = [Fraction(value) for value in control_certificate[t_key]]
    directions = retained_directions(reference)
    audit_blocks = {}
    offset = 0
    for root in ROOTS:
        root_count = int(reference_blocks[root]["root_embedding_count"])
        s = first[root]
        require(sum(s) == count_scale * root_count * math.comb(95, 2), "first total drift")
        require(sum(map(sum, moments[root])) == count_scale * root_count * math.comb(95, 2) ** 2, "second total drift")
        matrix = [
            [root_count * moments[root][i][j] - s[i] * s[j] // count_scale for j in range(len(s))]
            for i in range(len(s))
        ]
        require(all(s[i] * s[j] % count_scale == 0 for i in range(len(s)) for j in range(len(s))), "centering division drift")
        require(matrix == archived[root]["centered_matrix"], f"root {root} archive mismatch")
        require(canonical_sha256(matrix) == next(block for block in load_json(discovery_path)["root_blocks"] if int(block["root_mask"]) == root)["centered_matrix_sha256"], "discovery matrix hash drift")
        pivots, diagonal, lower = exact_ldl(matrix)
        stored = exact_psd["certificates"][str(root)]
        require(pivots == list(map(int, stored["pivot_indices"])), "stored pivot drift")
        require(list(map(fstr, diagonal)) == stored["positive_diagonal"], "stored diagonal drift")
        require(len(diagonal) == {3: 15, 12: 16}[root], "exact rank drift")
        projection_checks = 0
        size = len(directions[root])
        for left in range(size):
            for right in range(left, size):
                record = compressed_rows[offset]
                require(int(record["root_mask"]) == root and list(map(int, record["direction_indices"])) == [left, right], "compressed row order drift")
                projected = sum(
                    directions[root][left][i] * matrix[i][j] * directions[root][right][j]
                    for i in range(len(matrix)) for j in range(len(matrix))
                )
                quotient = sum(qmap[offset][column] * t[column] for column in range(8))
                require(Fraction(projected) == Fraction(count_scale, 92) * quotient, "full/compressed projection mismatch")
                projection_checks += 1
                offset += 1
        audit_blocks[str(root)] = {
            "size": len(matrix), "rank": len(diagonal), "nullity": len(matrix) - len(diagonal),
            "matrix_sha256": canonical_sha256(matrix), "positive_pivots": len(diagonal),
            "exact_reconstructed_entries": len(matrix) ** 2,
            "compressed_projection_rows_verified": projection_checks,
        }
        memory.append(memory_record(f"full_block_audit_root_{root}_complete"))
    require(offset == 57, "compressed projection count drift")
    result = {
        "format": "wave163-exact-control-full-root3-root12-clean-room-audit-v1",
        "claim_label": (
            "INDEPENDENT_EXACT_INTEGER_CONTROL_FULL_ROOT3_ROOT12_PSD_PASS"
            if args.integer_control else "INDEPENDENT_EXACT_FULL_ROOT3_ROOT12_PSD_PASS"
        ),
        "inputs_sha256": {str(path.relative_to(ROOT)): sha256_file(path) for path in (
            COEFFICIENT_ARCHIVE, SIX_SOURCE, SIX_RESULT, REFERENCE, control_path, KERNEL,
            COMPRESSED_ROWS, matrix_archive_path, discovery_path, exact_psd_path, *CUT_PATHS,
        )},
        "method": {
            "producer_module_imported": False,
            "frozen_class_counts": {"6": 62, "7": 208, "8": 916},
            "all_rooted_embeddings_restreamed": True,
            "all_matrix_entries_compared": True,
            "all_exact_LDL_entries_reconstructed": True,
            "raw_divisors_restored_before_quotient": True,
            "control_kind": "integer_lattice" if args.integer_control else "rational_rounding",
            "count_denominator_scale": count_scale,
        },
        "enumeration": enumeration,
        "blocks": audit_blocks,
        "conclusion": {
            "exact_control_full_root3_root12": "PSD",
            "negative_direction_at_this_control": "NONE",
            "new_scalar_cut": "NONE",
            "endpoint_exclusion": "NOT_ESTABLISHED",
        },
        "scope_boundary": {"other_root_types": "NOT_TESTED", "graph_realizability": "NOT_CLAIMED", "Conway_99": "UNKNOWN"},
        "resource_guard": {"minimum_required": 18.0, "minimum_observed": min(float(item["free_physical_memory_percent"]) for item in memory), "samples": memory},
        "elapsed_seconds": time.time() - started,
    }
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": output_path.name, "claim": result["claim_label"], "blocks": audit_blocks, "elapsed": result["elapsed_seconds"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
