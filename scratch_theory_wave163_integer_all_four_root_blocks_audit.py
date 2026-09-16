#!/usr/bin/env python3
"""Clean-room audit of the integer control in all nine Wave152 blocks.

The discovery module is deliberately not imported.  This script reads the
frozen 62/208/916 class streams, reconstructs the integral order-6/7/8
counts, restreams every ordered four-root embedding, compares every entry of
the nine archived covariance matrices, and proves PSD by an independent exact
pivoted LDL^T decomposition.
"""

from __future__ import annotations

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
CONTROL = ROOT / "scratch_theory_wave163_integer_lattice.json"
KERNEL = ROOT / "scratch_theory_wave163_coupled_kernel_basis.json.gz"
DISCOVERY = ROOT / "scratch_theory_wave163_integer_all_four_root_blocks.json"
MATRIX_ARCHIVE = ROOT / "scratch_theory_wave163_integer_all_four_root_blocks_matrices.json.gz"
LDL_ARCHIVE = ROOT / "scratch_theory_wave163_integer_all_four_root_blocks_ldl.json.gz"
OUTPUT = ROOT / "scratch_theory_wave163_integer_all_four_root_blocks_audit.json"
ROOT_MASKS = (0, 1, 3, 7, 11, 12, 13, 15, 30)
EXPECTED_SIZES = {0: 224, 1: 201, 3: 155, 7: 99, 11: 69, 12: 178, 13: 125, 15: 60, 30: 70}
EXPECTED_RANKS = {0: 38, 1: 27, 3: 15, 7: 3, 11: 3, 12: 16, 13: 6, 15: 0, 30: 0}


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
    require(free >= 18.0, f"{label}: free physical memory {free:.2f}% below 18% gate")
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
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def fstr(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def edges(order: int) -> tuple[tuple[int, int], ...]:
    return tuple((left, right) for left in range(order) for right in range(left + 1, order))


def edge_positions(order: int) -> dict[tuple[int, int], int]:
    return {edge: index for index, edge in enumerate(edges(order))}


def induced_mask(mask: int, order: int, chosen: Sequence[int]) -> int:
    source = edge_positions(order)
    result = target = 0
    for left_index, left in enumerate(chosen):
        for right in chosen[left_index + 1:]:
            if mask >> source[tuple(sorted((left, right)))] & 1:
                result |= 1 << target
            target += 1
    return result


def transform_mask(mask: int, order: int, permutation: Sequence[int]) -> int:
    positions = edge_positions(order)
    result = 0
    for edge, position in positions.items():
        if mask >> position & 1:
            image = tuple(sorted((permutation[edge[0]], permutation[edge[1]])))
            result |= 1 << positions[image]
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
    require(families[0] == families[1], "ordered pair families have different frozen streams")
    streams = families[0]
    require(tuple(len(streams[order]) for order in range(5, 9)) == (21, 62, 208, 916), "class census drift")
    return streams


def source_six_masks() -> tuple[int, ...]:
    tree = ast.parse(SIX_SOURCE.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "SOURCE_N_MASKS" for target in node.targets
        ):
            return tuple(map(int, ast.literal_eval(node.value)))
    raise AssertionError("SOURCE_N_MASKS not found")


def exact_counts(streams: dict[int, tuple[int, ...]], coefficient: dict) -> dict[int, dict[int, int]]:
    kernel = load_gzip(KERNEL)
    certificate = load_json(CONTROL)["certificate"]
    nullspace = [[Fraction(0) for _ in range(8)] for _ in range(917)]
    for column, entries in enumerate(kernel["universal_nullspace_basis_sparse"]):
        for row, value in entries:
            nullspace[int(row)][column] = Fraction(value)
    t = list(map(Fraction, certificate["t_integral_free_x8_coordinates"]))
    x8f = [sum(nullspace[1 + row][column] * t[column] for column in range(8)) for row in range(916)]
    require(all(value.denominator == 1 and value >= 0 for value in x8f), "x8 is not nonnegative integral")
    x8 = [value.numerator for value in x8f]
    index7 = {mask: index for index, mask in enumerate(streams[7])}
    index8 = {mask: index for index, mask in enumerate(streams[8])}
    deletion: list[dict[int, int] | None] = [None] * 208
    for record in coefficient["order7_to_order8_deletion_equations"]:
        deletion[index7[int(record["order7_mask"])]] = {
            index8[int(mask)]: int(mult) for mask, mult in record["terms_order8_mask_multiplicity"]
        }
    require(all(row is not None for row in deletion), "order7 deletion row missing")
    x7f = [
        sum(Fraction(mult) * x8[column] for column, mult in row.items()) / 92
        for row in deletion if row is not None
    ]
    require(all(value.denominator == 1 and value >= 0 for value in x7f), "x7 is not nonnegative integral")
    independent = load_json(SIX_RESULT)
    masks6 = source_six_masks()
    values6 = tuple(map(int, independent["model"]["six_counts"]))
    require(canonical_sha256(masks6) == independent["model"]["six_source_masks_sha256"], "six-mask source hash drift")
    require(canonical_sha256(values6) == independent["model"]["six_counts_sha256"], "six-count source hash drift")
    six = dict(zip(masks6, values6, strict=True))
    require(set(six) == set(streams[6]), "six-mask set drift")
    counts = {
        6: {mask: int(six[mask]) for mask in streams[6]},
        7: {mask: x7f[index].numerator for index, mask in enumerate(streams[7])},
        8: {mask: x8[index] for index, mask in enumerate(streams[8])},
    }
    require(tuple(sum(counts[order].values()) for order in (6, 7, 8)) == tuple(math.comb(99, order) for order in (6, 7, 8)), "global count totals drift")
    return counts


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
        require(all(value >= 0 for value in residual_diagonal.values()), "negative exact Schur diagonal")
        positive = [index for index, value in residual_diagonal.items() if value]
        if not positive:
            break
        pivot = max(positive, key=residual_diagonal.__getitem__)
        d = residual_diagonal[pivot]
        new_column = []
        for row in range(size):
            residual = Fraction(matrix[row][pivot]) - sum(
                lower[row][k] * diagonal[k] * lower[pivot][k] for k in range(len(diagonal))
            )
            new_column.append(residual / d)
        for row in range(size):
            lower[row].append(new_column[row])
        diagonal.append(d)
        pivots.append(pivot)
        remaining.remove(pivot)
    for row in range(size):
        for column in range(size):
            reconstructed = sum(lower[row][k] * diagonal[k] * lower[column][k] for k in range(len(diagonal)))
            require(reconstructed == matrix[row][column], "exact LDL reconstruction failure")
    return pivots, diagonal, lower


def main() -> int:
    started = time.time()
    memory = [memory_record("all_nine_audit_start")]
    coefficient = load_gzip(COEFFICIENT_ARCHIVE)
    streams = class_streams(coefficient)
    counts = exact_counts(streams, coefficient)
    reference = load_json(REFERENCE)
    reference_blocks = {int(block["root_mask"]): block for block in reference["root_blocks"]}
    require(set(reference_blocks) == set(ROOT_MASKS), "reference root set drift")
    flags = {root: tuple(map(int, reference_blocks[root]["flag_masks"])) for root in ROOT_MASKS}
    require({root: len(flags[root]) for root in ROOT_MASKS} == EXPECTED_SIZES, "flag sizes drift")
    indices = {root: {mask: index for index, mask in enumerate(flags[root])} for root in ROOT_MASKS}
    moments = {root: [[0] * len(flags[root]) for _ in flags[root]] for root in ROOT_MASKS}
    first = {root: [0] * len(flags[root]) for root in ROOT_MASKS}
    enumeration = {}
    for order in (6, 7, 8):
        covering = covering_pair_indices(order - 4)
        matched = products = nonzero = 0
        vertices = tuple(range(order))
        for class_index, mask in enumerate(streams[order]):
            weight = counts[order][mask]
            if not weight:
                continue
            nonzero += 1
            for roots in itertools.permutations(vertices, 4):
                root = induced_mask(mask, order, roots)
                if root not in indices:
                    continue
                matched += 1
                complement = tuple(vertex for vertex in vertices if vertex not in roots)
                free_pairs = tuple(itertools.combinations(complement, 2))
                positions = [
                    indices[root][canonical_flag(induced_mask(mask, order, roots + pair))]
                    for pair in free_pairs
                ]
                if order == 6:
                    first[root][positions[0]] += weight
                for left, right in covering:
                    moments[root][positions[left]][positions[right]] += weight
                    products += 1
            if class_index % 128 == 0:
                memory.append(memory_record(f"all_nine_audit_o{order}_{class_index}"))
        enumeration[str(order)] = {
            "classes": len(streams[order]), "nonzero_classes": nonzero,
            "matched": matched, "products": products,
        }
        memory.append(memory_record(f"all_nine_audit_o{order}_complete"))

    archive = load_gzip(MATRIX_ARCHIVE)
    archived = {int(block["root_mask"]): block for block in archive["blocks"]}
    ldl_archive = load_gzip(LDL_ARCHIVE)
    archived_ldl = {int(block["root_mask"]): block for block in ldl_archive["blocks"]}
    discovery = load_json(DISCOVERY)
    discovered = {int(block["root_mask"]): block for block in discovery["blocks"]}
    require(set(archived) == set(discovered) == set(ROOT_MASKS), "archived/discovery root set drift")
    require(set(archived_ldl) == set(ROOT_MASKS), "LDL archive root set drift")
    require(sha256_file(MATRIX_ARCHIVE) == discovery["matrix_archive"]["sha256"], "matrix archive file hash drift")
    require(sha256_file(LDL_ARCHIVE) == discovery["exact_ldl_archive"]["sha256"], "LDL archive file hash drift")
    require(enumeration == discovery["enumeration"], "enumeration census drift")
    free_pairs = math.comb(95, 2)
    audited = {}
    total_entries = 0
    for root in ROOT_MASKS:
        root_count = int(reference_blocks[root]["root_embedding_count"])
        s = first[root]
        require(sum(s) == root_count * free_pairs, f"root {root}: first total drift")
        require(sum(map(sum, moments[root])) == root_count * free_pairs**2, f"root {root}: second total drift")
        matrix = [[root_count * moments[root][i][j] - s[i] * s[j] for j in range(len(s))] for i in range(len(s))]
        require(archived[root]["flag_masks"] == list(flags[root]), f"root {root}: flag archive drift")
        require(matrix == archived[root]["centered_matrix"], f"root {root}: matrix archive mismatch")
        require(canonical_sha256(matrix) == discovered[root]["matrix_sha256"], f"root {root}: matrix hash drift")
        pivots, diagonal, lower = exact_ldl(matrix)
        stored = discovered[root]["exact_psd_certificate"]
        require(discovered[root]["exact_status"] == "PSD" and discovered[root]["negative_certificate"] is None, f"root {root}: status drift")
        require(len(diagonal) == EXPECTED_RANKS[root], f"root {root}: exact rank drift")
        require(stored["rank"] == len(diagonal) and stored["nullity"] == len(matrix) - len(diagonal), f"root {root}: stored rank drift")
        require(stored["pivot_indices"] == pivots, f"root {root}: pivot list drift")
        require(stored["positive_diagonal"] == list(map(fstr, diagonal)), f"root {root}: diagonal list drift")
        sparse_lower = [[[column, fstr(value)] for column, value in enumerate(row) if value] for row in lower]
        require(stored["rectangular_L_sha256"] == canonical_sha256(sparse_lower), f"root {root}: L hash drift")
        require(archived_ldl[root] == {
            "root_mask": root, "size": len(matrix), "rank": len(diagonal),
            "pivot_indices": pivots, "positive_diagonal": list(map(fstr, diagonal)),
            "rectangular_L_sparse": sparse_lower,
        }, f"root {root}: full LDL archive mismatch")
        require(stored["reconstructed_entries"] == len(matrix) ** 2, f"root {root}: reconstruction count drift")
        total_entries += len(matrix) ** 2
        audited[str(root)] = {
            "size": len(matrix), "rank": len(diagonal), "nullity": len(matrix) - len(diagonal),
            "matrix_sha256": canonical_sha256(matrix), "positive_pivots": len(diagonal),
            "exact_reconstructed_entries": len(matrix) ** 2,
            "identically_zero": not any(value for row in matrix for value in row),
        }
        memory.append(memory_record(f"all_nine_audit_r{root}_complete"))

    require(discovery["claim_label"] == "EXACT_ALL_NINE_FOUR_ROOT_PSD_PASS", "claim drift")
    require(discovery["conclusion"]["negative_roots"] == [], "unexpected negative root")
    result = {
        "format": "wave163-integer-control-all-nine-four-root-clean-room-audit-v1",
        "claim_label": "INDEPENDENT_EXACT_ALL_NINE_FOUR_ROOT_PSD_PASS",
        "inputs_sha256": {str(path.relative_to(ROOT)): sha256_file(path) for path in (
            COEFFICIENT_ARCHIVE, SIX_SOURCE, SIX_RESULT, REFERENCE, CONTROL, KERNEL,
            DISCOVERY, MATRIX_ARCHIVE, LDL_ARCHIVE,
        )},
        "method": {
            "producer_module_imported": False,
            "frozen_class_counts": {"6": 62, "7": 208, "8": 916},
            "class_catalogues_regenerated": False,
            "all_rooted_embeddings_restreamed": True,
            "all_matrix_entries_compared": True,
            "all_exact_LDL_entries_reconstructed": True,
            "integral_count_scale": 1,
            "root_masks": list(ROOT_MASKS),
        },
        "enumeration": enumeration,
        "blocks": audited,
        "totals": {"blocks": len(audited), "matrix_entries_exactly_reconstructed": total_entries},
        "conclusion": {
            "integer_control_all_nine_four_root_covariance_blocks": "PSD",
            "negative_direction_at_this_control": "NONE",
            "new_scalar_cut": "NONE",
            "endpoint_exclusion": "NOT_ESTABLISHED",
        },
        "scope_boundary": {
            "claim": "this exact integral pseudocount passes the complete nine-block Wave152 order-at-most-8 four-root covariance layer",
            "graph_realizability": "NOT_CLAIMED",
            "Conway_99": "UNKNOWN",
        },
        "resource_guard": {
            "minimum_required": 18.0,
            "minimum_observed": min(float(item["free_physical_memory_percent"]) for item in memory),
            "samples": memory,
        },
        "elapsed_seconds": time.time() - started,
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"output": OUTPUT.name, "claim": result["claim_label"], "blocks": audited, "elapsed_seconds": result["elapsed_seconds"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
