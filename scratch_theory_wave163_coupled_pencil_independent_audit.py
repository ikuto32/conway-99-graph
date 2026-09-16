#!/usr/bin/env python3
"""Source-independent exact audit of the Wave163 compressed conic null result.

The verifier imports none of the Wave163 discovery/recovery/search programs.
It rebuilds all 57 four-root contractions directly from frozen graph masks and
directions, rebuilds the universal endpoint rows from the Wave44/147/148 raw
schemas, checks ranks over two primes, replays the rational quotient/kernel,
and verifies the positive-definite separating blocks with Fraction LDL^T.
"""

from __future__ import annotations

import ctypes
import functools
import gzip
import hashlib
import itertools
import json
import math
import time
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Sequence


ROOT = Path(__file__).resolve().parent
EXT = ROOT / "external_conway99_research"
ATT = EXT / "attempts"

COEFFICIENT_ARTIFACT = ROOT / "scratch_theory_wave163_coupled_pencil_coefficients.json.gz"
DISCOVERY_RESULT = ROOT / "scratch_theory_wave163_coupled_pencil.json"
KERNEL_ARTIFACT = ROOT / "scratch_theory_wave163_coupled_kernel_basis.json.gz"
KERNEL_RESULT = ROOT / "scratch_theory_wave163_coupled_kernel.json"
PSD_CERTIFICATE = ROOT / "scratch_theory_wave163_psd_exact.json"
OUTPUT = ROOT / "scratch_theory_wave163_coupled_pencil_independent_audit.json"

ROW_SYSTEM = ATT / "wave44-rooted-flags/row-system.json"
COEFFICIENT_ARCHIVE = ATT / "wave147-alternative-lane/coefficients.json.gz"
CLASS_RESULT = ATT / "wave147-alternative-lane/exact-results.json"
MARKED_ARCHIVE = ATT / "wave148-marked-order8/marked-rows.json.gz"
WITNESS = ATT / "wave159-four-root-cut-loop/exact-witness-after-fifteen-cuts.json"
EVALUATION = ATT / "wave159-four-root-cut-loop/four-root-evaluation-after-fifteen-cuts.json"

CUT_PATHS = (
    ATT / "wave152-four-root-order8/exact-cuts.json",
    ATT / "wave152-four-root-order8/iteration2-cuts.json",
    ATT / "wave152-four-root-order8/iteration3-mask13-cut.json",
    ATT / "wave152-four-root-order8/iteration4-three-cuts.json",
    ATT / "wave152-four-root-order8/simplified-mask12-cut.json",
    ATT / "wave152-four-root-order8/iteration5-three-cuts.json",
    ATT / "wave152-four-root-order8/simplified-mask12-cut-2.json",
    ATT / "wave159-four-root-cut-loop/fresh-two-cuts.json",
)

N = 99
N3 = 4158
ROOTS = (3, 12)
PRIMES = (1_000_000_007, 1_000_000_009)
MEMORY_FLOOR = 18.0


class MemoryStatusEx(ctypes.Structure):
    _fields_ = [
        ("length", ctypes.c_ulong),
        ("memory_load", ctypes.c_ulong),
        ("total_phys", ctypes.c_ulonglong),
        ("avail_phys", ctypes.c_ulonglong),
        ("total_page_file", ctypes.c_ulonglong),
        ("avail_page_file", ctypes.c_ulonglong),
        ("total_virtual", ctypes.c_ulonglong),
        ("avail_virtual", ctypes.c_ulonglong),
        ("avail_extended_virtual", ctypes.c_ulonglong),
    ]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def memory_record(label: str) -> dict[str, float | str]:
    status = MemoryStatusEx()
    status.length = ctypes.sizeof(status)
    require(
        bool(ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status))),
        "GlobalMemoryStatusEx failed",
    )
    free = 100.0 * status.avail_phys / status.total_phys
    require(free >= MEMORY_FLOOR, f"18% memory gate failed at {label}: {free:.3f}%")
    return {
        "label": label,
        "free_physical_memory_percent": free,
        "available_physical_gib": status.avail_phys / 2**30,
    }


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_gzip_json(path: Path) -> dict[str, Any]:
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        return json.load(stream)


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fstr(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def edges(order: int) -> tuple[tuple[int, int], ...]:
    return tuple((left, right) for left in range(order) for right in range(left + 1, order))


@functools.lru_cache(maxsize=None)
def positions(order: int) -> dict[tuple[int, int], int]:
    return {edge: index for index, edge in enumerate(edges(order))}


def adjacency_rows(mask: int, order: int) -> tuple[int, ...]:
    result = [0] * order
    for bit, (left, right) in enumerate(edges(order)):
        if mask >> bit & 1:
            result[left] |= 1 << right
            result[right] |= 1 << left
    return tuple(result)


def induced_from_adjacency(adjacency: Sequence[int], chosen: Sequence[int]) -> int:
    result = 0
    bit = 0
    for left_index, left in enumerate(chosen):
        for right in chosen[left_index + 1 :]:
            if adjacency[left] >> right & 1:
                result |= 1 << bit
            bit += 1
    return result


def transform_mask(mask: int, order: int, permutation: Sequence[int]) -> int:
    result = 0
    target = positions(order)
    for bit, (left, right) in enumerate(edges(order)):
        if mask >> bit & 1:
            edge = tuple(sorted((permutation[left], permutation[right])))
            result |= 1 << target[edge]
    return result


@functools.lru_cache(maxsize=None)
def canonical_unrooted(mask: int, order: int) -> int:
    adjacency = adjacency_rows(mask, order)
    groups: dict[int, list[int]] = {}
    for vertex, row in enumerate(adjacency):
        groups.setdefault(row.bit_count(), []).append(vertex)
    cell_maps = []
    start = 0
    for degree in sorted(groups):
        vertices = groups[degree]
        targets = tuple(range(start, start + len(vertices)))
        start += len(vertices)
        cell_maps.append(
            tuple(dict(zip(vertices, image, strict=True)) for image in itertools.permutations(targets))
        )
    best: int | None = None
    for choices in itertools.product(*cell_maps):
        permutation = [0] * order
        for mapping in choices:
            for source, target in mapping.items():
                permutation[source] = target
        value = transform_mask(mask, order, permutation)
        best = value if best is None else min(best, value)
    require(best is not None, "empty canonicalization")
    return best


@functools.lru_cache(maxsize=None)
def canonical_four_flag(mask: int) -> int:
    return min(mask, transform_mask(mask, 6, (0, 1, 2, 3, 5, 4)))


def class_streams(payload: dict[str, Any]) -> dict[int, tuple[int, ...]]:
    streams_by_family = []
    for family_name in ("ordered_edge", "ordered_nonedge"):
        result: dict[int, list[int]] = {order: [] for order in range(5, 9)}
        for record in payload["families"][family_name]["class_coefficients"]:
            result[int(record["order"])].append(int(record["canonical_mask"]))
        streams_by_family.append({order: tuple(values) for order, values in result.items()})
    require(streams_by_family[0] == streams_by_family[1], "Wave147 family streams differ")
    streams = streams_by_family[0]
    require(tuple(map(len, (streams[5], streams[6], streams[7], streams[8]))) == (21, 62, 208, 916), "class census drift")
    return streams


def derive_x6(classes6: Sequence[int]) -> dict[int, int]:
    witness = load_json(WITNESS)
    x7 = {
        int(record["canonical_mask"]): int(record["count"])
        for record in witness["x7_support"]
    }
    require(sum(x7.values()) == math.comb(N, 7), "x7 total drift")
    # The frozen Wave45/Wave147 stream keeps its historical representative
    # masks, rather than our lexicographically least representatives.  Build
    # an isomorphism-safe translation before accumulating deletion children.
    canonical_to_frozen = {
        canonical_unrooted(mask, 6): mask for mask in classes6
    }
    require(
        len(canonical_to_frozen) == len(classes6),
        "order-six canonical translation collision",
    )
    accumulated: Counter[int] = Counter()
    for mask, count in x7.items():
        adjacency = adjacency_rows(mask, 7)
        for deleted in range(7):
            chosen = tuple(vertex for vertex in range(7) if vertex != deleted)
            child = induced_from_adjacency(adjacency, chosen)
            canonical_child = canonical_unrooted(child, 6)
            require(
                canonical_child in canonical_to_frozen,
                "x6 deletion child outside frozen stream",
            )
            accumulated[canonical_to_frozen[canonical_child]] += count
    require(all(value % 93 == 0 for value in accumulated.values()), "nonintegral x6 deletion")
    x6 = {mask: accumulated.get(mask, 0) // 93 for mask in classes6}
    require(set(accumulated).issubset(set(classes6)), "x6 class outside frozen stream")
    require(sum(x6.values()) == math.comb(N, 6), "x6 total drift")
    return x6


def all_cuts() -> list[dict[str, Any]]:
    cuts = []
    for path in CUT_PATHS:
        payload = load_json(path)
        cuts.extend(payload["cuts"] if "cuts" in payload else [payload["cut"]])
    require(len(cuts) == 15, "retained cut count drift")
    return cuts


def direction_data() -> dict[int, dict[str, Any]]:
    evaluation = load_json(EVALUATION)
    blocks = {int(block["root_mask"]): block for block in evaluation["root_blocks"]}
    result: dict[int, dict[str, Any]] = {}
    cuts = all_cuts()
    for root in ROOTS:
        block = blocks[root]
        flags = tuple(int(mask) for mask in block["flag_masks"])
        retained = [cut for cut in cuts if int(cut["root_mask"]) == root]
        directions = [tuple(map(int, cut["direction"])) for cut in retained]
        labels = [f"retained:{cut['cut_sha256']}" for cut in retained]
        certificate = block["negative_certificate"]
        require(certificate is not None, f"missing recurrent direction root {root}")
        recurrent = [0] * int(block["flag_count"])
        for index, value in zip(certificate["indices"], certificate["vector"], strict=True):
            recurrent[int(index)] = int(value)
        recurrent_hash = canonical_sha256(recurrent)
        directions.append(tuple(recurrent))
        labels.append(f"recurrent:{recurrent_hash}")
        require(all(len(direction) == len(flags) for direction in directions), "direction width drift")
        result[root] = {
            "flags": flags,
            "directions": tuple(directions),
            "labels": tuple(labels),
            "root_count": int(block["root_embedding_count"]),
        }
    require(tuple(map(len, (result[3]["directions"], result[12]["directions"]))) == (6, 8), "direction count drift")
    return result


def upper_pairs(size: int) -> tuple[tuple[int, int], ...]:
    return tuple((left, right) for left in range(size) for right in range(left, size))


@functools.lru_cache(maxsize=None)
def root_templates(order: int) -> tuple[tuple[tuple[int, ...], tuple[tuple[int, int], ...]], ...]:
    vertices = tuple(range(order))
    return tuple(
        (
            roots,
            tuple(itertools.combinations(tuple(vertex for vertex in vertices if vertex not in roots), 2)),
        )
        for roots in itertools.permutations(vertices, 4)
    )


def covering_unordered(free_pairs: Sequence[tuple[int, int]], complement_size: int) -> tuple[tuple[int, int], ...]:
    return tuple(
        (left, right)
        for left in range(len(free_pairs))
        for right in range(left + 1, len(free_pairs))
        if len(set(free_pairs[left]).union(free_pairs[right])) == complement_size
    )


def contract_class(
    mask: int,
    order: int,
    roots_data: dict[int, dict[str, Any]],
) -> dict[int, tuple[list[int], list[int], int]]:
    adjacency = adjacency_rows(mask, order)
    work = {}
    for root in ROOTS:
        directions = roots_data[root]["directions"]
        work[root] = ([0] * len(directions), [0] * len(upper_pairs(len(directions))), 0)
    flag_indices = {
        root: {mask_value: index for index, mask_value in enumerate(roots_data[root]["flags"])}
        for root in ROOTS
    }
    transposed = {
        root: tuple(
            tuple(direction[index] for direction in roots_data[root]["directions"])
            for index in range(len(roots_data[root]["flags"]))
        )
        for root in ROOTS
    }
    for roots, free_pairs in root_templates(order):
        root_mask = induced_from_adjacency(adjacency, roots)
        if root_mask not in work:
            continue
        first, quadratic, matched = work[root_mask]
        values = []
        for free_pair in free_pairs:
            flag = canonical_four_flag(induced_from_adjacency(adjacency, roots + free_pair))
            require(flag in flag_indices[root_mask], "emitted flag outside frozen basis")
            values.append(transposed[root_mask][flag_indices[root_mask][flag]])
        if order == 6:
            require(len(values) == 1, "order-six free pair drift")
            for index, value in enumerate(values[0]):
                first[index] += value
            pair_position = 0
            vector = values[0]
            for left in range(len(vector)):
                for right in range(left, len(vector)):
                    quadratic[pair_position] += vector[left] * vector[right]
                    pair_position += 1
        else:
            covers = covering_unordered(free_pairs, order - 4)
            require(len(covers) == 3, "covering-pair census drift")
            for a, b in covers:
                left_vector, right_vector = values[a], values[b]
                pair_position = 0
                for left in range(len(left_vector)):
                    quadratic[pair_position] += 2 * left_vector[left] * right_vector[left]
                    pair_position += 1
                    for right in range(left + 1, len(left_vector)):
                        quadratic[pair_position] += (
                            left_vector[left] * right_vector[right]
                            + right_vector[left] * left_vector[right]
                        )
                        pair_position += 1
        work[root_mask] = (first, quadratic, matched + 1)
    return work


def rebuild_compressed_rows(
    streams: dict[int, tuple[int, ...]],
    x6: dict[int, int],
    roots_data: dict[int, dict[str, Any]],
    memory: list[dict[str, float | str]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    aggregate: dict[int, dict[str, Any]] = {}
    for root in ROOTS:
        size = len(roots_data[root]["directions"])
        aggregate[root] = {
            "first6": [0] * size,
            "quadratic6": [0] * len(upper_pairs(size)),
            "coeff7": [dict() for _ in upper_pairs(size)],
            "coeff8": [dict() for _ in upper_pairs(size)],
            "matched": {6: 0, 7: 0, 8: 0},
        }

    for order in (6, 7, 8):
        for class_index, mask in enumerate(streams[order]):
            contracted = contract_class(mask, order, roots_data)
            for root in ROOTS:
                first, quadratic, matched = contracted[root]
                target = aggregate[root]
                target["matched"][order] += matched
                if order == 6:
                    count = x6[int(mask)]
                    for index, value in enumerate(first):
                        target["first6"][index] += count * value
                    for index, value in enumerate(quadratic):
                        target["quadratic6"][index] += count * value
                else:
                    coefficients = target[f"coeff{order}"]
                    for index, value in enumerate(quadratic):
                        if value:
                            coefficients[index][int(mask)] = value
            if class_index % 128 == 0:
                memory.append(memory_record(f"direct_contract_order{order}_class{class_index}"))

    rows = []
    summary = {}
    for root in ROOTS:
        target = aggregate[root]
        root_count = int(roots_data[root]["root_count"])
        for position, (left, right) in enumerate(upper_pairs(len(roots_data[root]["directions"]))):
            constant = (
                root_count * target["quadratic6"][position]
                - target["first6"][left] * target["first6"][right]
            )
            a7 = {mask: root_count * value for mask, value in target["coeff7"][position].items()}
            a8 = {mask: root_count * value for mask, value in target["coeff8"][position].items()}
            divisor = 0
            for value in itertools.chain((constant,), a7.values(), a8.values()):
                divisor = math.gcd(divisor, abs(value))
            if divisor == 0:
                divisor = 1
            core = {
                "root_mask": root,
                "direction_indices": [left, right],
                "direction_labels": [roots_data[root]["labels"][left], roots_data[root]["labels"][right]],
                "raw_divisor": str(divisor),
                "constant": str(constant // divisor),
                "order7_coefficients": [[mask, str(value // divisor)] for mask, value in sorted(a7.items())],
                "order8_coefficients": [[mask, str(value // divisor)] for mask, value in sorted(a8.items())],
            }
            rows.append({**core, "primitive_row_sha256": canonical_sha256(core)})
        summary[str(root)] = {
            "weighted_first_moments": list(map(str, target["first6"])),
            "weighted_order6_quadratic_sha256": canonical_sha256(target["quadratic6"]),
            "matched_embeddings_by_order": {str(order): target["matched"][order] for order in (6, 7, 8)},
        }
    require(len(rows) == 57, "compressed row census drift")
    return rows, summary


def deletion_maps(
    coefficient_payload: dict[str, Any], classes7: Sequence[int], classes8: Sequence[int]
) -> list[dict[int, int]]:
    index7 = {mask: index for index, mask in enumerate(classes7)}
    index8 = {mask: index for index, mask in enumerate(classes8)}
    result = [dict() for _ in classes7]
    for record in coefficient_payload["order7_to_order8_deletion_equations"]:
        require(int(record["left_multiplier"]) == 92, "deletion multiplier drift")
        result[index7[int(record["order7_mask"])]] = {
            index8[int(mask)]: int(value)
            for mask, value in record["terms_order8_mask_multiplicity"]
        }
    require(all(result), "empty deletion row")
    return result


def eliminate_x7(
    constant: int,
    a7: dict[int, int],
    a8: dict[int, int],
    index7: dict[int, int],
    index8: dict[int, int],
    deletion: Sequence[dict[int, int]],
) -> dict[int, int]:
    result: dict[int, int] = {}

    def increment(column: int, value: int) -> None:
        if not value:
            return
        updated = result.get(column, 0) + value
        if updated:
            result[column] = updated
        else:
            result.pop(column, None)

    increment(0, 92 * constant)
    for mask, value in a7.items():
        for column, multiplicity in deletion[index7[mask]].items():
            increment(1 + column, value * multiplicity)
    for mask, value in a8.items():
        increment(1 + index8[mask], 92 * value)
    return result


def universal_rows(
    coefficient_payload: dict[str, Any], marked: dict[str, Any], row_system: dict[str, Any],
    classes7: Sequence[int], classes8: Sequence[int],
) -> tuple[list[dict[int, int]], list[dict[int, int]]]:
    index7 = {mask: index for index, mask in enumerate(classes7)}
    index8 = {mask: index for index, mask in enumerate(classes8)}
    deletion = deletion_maps(coefficient_payload, classes7, classes8)
    rows: list[dict[int, int]] = []

    def add(constant: int, a7: dict[int, int], a8: dict[int, int]) -> None:
        row = eliminate_x7(constant, a7, a8, index7, index8, deletion)
        if row:
            rows.append(row)

    add(-math.comb(N, 7), {mask: 1 for mask in classes7}, {})
    add(-math.comb(N, 8), {}, {mask: 1 for mask in classes8})
    for family_name in ("base", "vertex", "edge", "nonedge"):
        family = row_system["families"][family_name]
        for raw, rhs in zip(family["rows"], family["rhs"], strict=True):
            add(
                int(raw[-1]) * N3 - int(rhs),
                {mask: int(value) for mask, value in zip(classes7, raw[:-1], strict=True) if int(value)},
                {},
            )
    records = marked["vertex_rows"] + marked["ordered_pair_rows"]
    require(len(records) == 5384, "marked row census drift")
    for record in records:
        lhs = int(record["lhs_coefficient"])
        add(
            0,
            {int(record["order7_mask"]): lhs} if lhs else {},
            {int(mask): -int(value) for mask, value in record["terms_order8_mask_coefficient"] if int(value)},
        )
    require(len(rows) == 4663, "nonzero universal row census drift")
    return rows, deletion


def raw_row(record: dict[str, Any]) -> tuple[int, dict[int, int], dict[int, int]]:
    divisor = int(record["raw_divisor"])
    return (
        divisor * int(record["constant"]),
        {int(mask): divisor * int(value) for mask, value in record["order7_coefficients"]},
        {int(mask): divisor * int(value) for mask, value in record["order8_coefficients"]},
    )


def modular_rank(rows: Iterable[dict[int, int]], prime: int) -> int:
    basis: dict[int, dict[int, int]] = {}
    for source in rows:
        row = {column: value % prime for column, value in source.items() if value % prime}
        while row:
            pivot = min(row)
            prior = basis.get(pivot)
            if prior is None:
                inverse = pow(row[pivot], prime - 2, prime)
                basis[pivot] = {
                    column: value * inverse % prime
                    for column, value in row.items()
                    if value * inverse % prime
                }
                break
            factor = row[pivot]
            for column, value in prior.items():
                updated = (row.get(column, 0) - factor * value) % prime
                if updated:
                    row[column] = updated
                else:
                    row.pop(column, None)
    return len(basis)


def dot_sparse(row: dict[int, int], vector: dict[int, Fraction]) -> Fraction:
    if len(row) < len(vector):
        return sum(Fraction(value) * vector.get(column, Fraction(0)) for column, value in row.items())
    return sum(Fraction(row.get(column, 0)) * value for column, value in vector.items())


def fraction_rank(matrix: Sequence[Sequence[Fraction]]) -> int:
    work = [list(row) for row in matrix]
    rank = 0
    width = len(work[0]) if work else 0
    for column in range(width):
        found = next((row for row in range(rank, len(work)) if work[row][column]), None)
        if found is None:
            continue
        work[rank], work[found] = work[found], work[rank]
        pivot = work[rank][column]
        work[rank] = [value / pivot for value in work[rank]]
        for row in range(len(work)):
            if row == rank or not work[row][column]:
                continue
            factor = work[row][column]
            work[row] = [left - factor * right for left, right in zip(work[row], work[rank], strict=True)]
        rank += 1
        if rank == len(work):
            break
    return rank


def ldlt_positive(matrix: Sequence[Sequence[Fraction]]) -> tuple[list[Fraction], list[list[Fraction]]]:
    size = len(matrix)
    require(all(len(row) == size for row in matrix), "LDL matrix not square")
    require(all(matrix[i][j] == matrix[j][i] for i in range(size) for j in range(size)), "LDL matrix not symmetric")
    lower = [[Fraction(int(i == j)) for j in range(size)] for i in range(size)]
    diagonal = [Fraction(0) for _ in range(size)]
    for pivot in range(size):
        diagonal[pivot] = matrix[pivot][pivot] - sum(
            lower[pivot][prior] ** 2 * diagonal[prior] for prior in range(pivot)
        )
        require(diagonal[pivot] > 0, f"nonpositive LDL pivot {pivot}")
        for row in range(pivot + 1, size):
            residual = matrix[row][pivot] - sum(
                lower[row][prior] * lower[pivot][prior] * diagonal[prior]
                for prior in range(pivot)
            )
            lower[row][pivot] = residual / diagonal[pivot]
    return diagonal, lower


def main() -> int:
    started = time.time()
    memory = [memory_record("audit_start")]
    coefficient_payload = load_gzip_json(COEFFICIENT_ARCHIVE)
    marked = load_gzip_json(MARKED_ARCHIVE)
    row_system = load_json(ROW_SYSTEM)
    coefficient_artifact = load_gzip_json(COEFFICIENT_ARTIFACT)
    kernel_payload = load_gzip_json(KERNEL_ARTIFACT)
    psd = load_json(PSD_CERTIFICATE)
    streams = class_streams(coefficient_payload)
    require(tuple(coefficient_artifact["coordinate_system"]["order7_masks"]) == streams[7], "x7 coordinate stream drift")
    require(tuple(coefficient_artifact["coordinate_system"]["order8_masks"]) == streams[8], "x8 coordinate stream drift")

    x6 = derive_x6(streams[6])
    memory.append(memory_record("x6_derived"))
    roots_data = direction_data()
    rebuilt_rows, contraction_summary = rebuild_compressed_rows(streams, x6, roots_data, memory)
    stored_rows = coefficient_artifact["rows"]
    require(rebuilt_rows == stored_rows, "directly rebuilt compressed coefficient rows differ")
    memory.append(memory_record("direct_coefficients_verified"))

    expected_direction_metadata = coefficient_artifact["directions"]
    for root in ROOTS:
        data = roots_data[root]
        observed_hashes = [canonical_sha256(list(direction)) for direction in data["directions"]]
        require(observed_hashes == expected_direction_metadata[str(root)]["direction_sha256"], "direction hash drift")
        require(list(data["labels"]) == expected_direction_metadata[str(root)]["direction_labels"], "direction label drift")
        require(canonical_sha256(list(data["flags"])) == expected_direction_metadata[str(root)]["flag_masks_sha256"], "flag hash drift")

    universal, deletion = universal_rows(coefficient_payload, marked, row_system, streams[7], streams[8])
    index7 = {mask: index for index, mask in enumerate(streams[7])}
    index8 = {mask: index for index, mask in enumerate(streams[8])}
    compressed = [
        eliminate_x7(*raw_row(record), index7, index8, deletion)
        for record in rebuilt_rows
    ]
    modular = []
    for prime in PRIMES:
        memory.append(memory_record(f"before_rank_{prime}"))
        rank_universal = modular_rank(universal, prime)
        rank_combined = modular_rank(itertools.chain(universal, compressed), prime)
        modular.append({
            "prime": prime,
            "reduced_universal_rank": rank_universal,
            "reduced_combined_rank": rank_combined,
            "compressed_quotient_rank": rank_combined - rank_universal,
            "full_universal_rank": rank_universal + len(streams[7]),
        })
        require((rank_universal, rank_combined) == (909, 917), f"rank drift mod {prime}")
        memory.append(memory_record(f"after_rank_{prime}"))

    nullspace = [
        {int(index): Fraction(value) for index, value in column}
        for column in kernel_payload["universal_nullspace_basis_sparse"]
    ]
    free_columns = list(map(int, kernel_payload["universal_free_columns"]))
    require(len(nullspace) == len(free_columns) == 8, "nullspace dimension drift")
    for column, vector in enumerate(nullspace):
        require(all(vector.get(free, Fraction(0)) == Fraction(int(column == other)) for other, free in enumerate(free_columns)), "nullspace free-coordinate normalization drift")
        require(all(dot_sparse(row, vector) == 0 for row in universal), f"universal nullspace vector {column} failed")

    quotient = [[dot_sparse(row, vector) for vector in nullspace] for row in compressed]
    stored_quotient = [
        [Fraction(value) for value in row]
        for row in kernel_payload["compressed_quotient_map_57_by_8"]
    ]
    require(quotient == stored_quotient, "exact quotient map drift")
    quotient_hash = canonical_sha256([[fstr(value) for value in row] for row in quotient])
    pivots = list(map(int, kernel_payload["quotient_equation_pivot_coordinates"]))
    require(len(pivots) == 8 and fraction_rank([quotient[row] for row in pivots]) == 8, "quotient rank certificate failed")

    kernel_vectors = []
    nonpivots = [index for index in range(57) if index not in set(pivots)]
    for sparse_vector in kernel_payload["kernel_basis_sparse"]:
        vector = {int(index): Fraction(value) for index, value in sparse_vector}
        require(all(sum(vector.get(row, Fraction(0)) * quotient[row][column] for row in range(57)) == 0 for column in range(8)), "kernel vector failed exact quotient multiplication")
        kernel_vectors.append(vector)
    require(len(kernel_vectors) == 49, "kernel basis length drift")
    require(all(kernel_vectors[i].get(column, Fraction(0)) == Fraction(int(i == j)) for i, column in enumerate(nonpivots) for j in (i,)), "kernel free-coordinate normalization drift")
    # Stronger identity-submatrix check, including absence at every other free coordinate.
    require(all(kernel_vectors[i].get(nonpivots[j], Fraction(0)) == Fraction(int(i == j)) for i in range(49) for j in range(49)), "kernel basis independence certificate failed")

    certificate = psd["certificate"]
    coefficients = [Fraction(value) for value in certificate["quotient_equation_coefficients"]]
    require(len(coefficients) == 8, "separator coordinate length drift")
    scales = {
        root: [max(abs(value) for value in direction) for direction in roots_data[root]["directions"]]
        for root in ROOTS
    }
    require({str(root): list(map(str, scales[root])) for root in ROOTS} == certificate["direction_column_scales"], "direction scale drift")

    blocks: dict[int, list[list[Fraction]]] = {}
    offset = 0
    for root, size in ((3, 6), (12, 8)):
        matrix = [[Fraction(0) for _ in range(size)] for _ in range(size)]
        for left, right in upper_pairs(size):
            value = sum(coefficients[k] * quotient[offset][k] for k in range(8)) / (scales[root][left] * scales[root][right])
            matrix[left][right] = matrix[right][left] = value
            offset += 1
        blocks[root] = matrix
    require(offset == 57, "separator row offset drift")
    stored_blocks = {
        3: [[Fraction(value) for value in row] for row in certificate["H3"]],
        12: [[Fraction(value) for value in row] for row in certificate["H12"]],
    }
    require(blocks == stored_blocks, "stored H blocks drift")
    diagonals = {}
    for root in ROOTS:
        diagonal, _ = ldlt_positive(blocks[root])
        require([fstr(value) for value in diagonal] == certificate["exact_ldlt_positive_diagonals"][str(root)], f"stored LDL diagonal drift root {root}")
        diagonals[root] = diagonal

    # Explicitly exercise both the 2*off-diagonal Frobenius factor and the
    # direction normalization.  This deterministic symmetric test need not be
    # PSD; it is an algebraic convention audit.
    test_y = {
        3: [[Fraction((i + 1) * (j + 2)) for j in range(6)] for i in range(6)],
        12: [[Fraction((i + 2) * (j + 3)) for j in range(8)] for i in range(8)],
    }
    for root in ROOTS:
        size = len(test_y[root])
        for i in range(size):
            for j in range(i):
                test_y[root][i][j] = test_y[root][j][i]
    equations = [Fraction(0) for _ in range(8)]
    offset = 0
    for root, size in ((3, 6), (12, 8)):
        for left, right in upper_pairs(size):
            multiplicity = 1 if left == right else 2
            for k in range(8):
                equations[k] += multiplicity * test_y[root][left][right] * quotient[offset][k] / (scales[root][left] * scales[root][right])
            offset += 1
    left_side = sum(coefficients[k] * equations[k] for k in range(8))
    right_side = sum(
        test_y[root][i][j] * blocks[root][j][i]
        for root in ROOTS
        for i in range(len(test_y[root]))
        for j in range(len(test_y[root]))
    )
    require(left_side == right_side, "off-diagonal factor-two trace identity failed")
    require(kernel_payload["upper_triangle_convention"]["linear_coefficient"] == "Y_ii on diagonal C_ii; 2*Y_ij on off-diagonal C_ij", "stored upper-triangle convention drift")

    memory.append(memory_record("audit_complete"))
    inputs = [
        COEFFICIENT_ARTIFACT, DISCOVERY_RESULT, KERNEL_ARTIFACT, KERNEL_RESULT,
        PSD_CERTIFICATE, ROW_SYSTEM, COEFFICIENT_ARCHIVE, CLASS_RESULT,
        MARKED_ARCHIVE, WITNESS, EVALUATION, *CUT_PATHS,
    ]
    result = {
        "format": "wave163-source-independent-compressed-conic-audit-v1",
        "claim_label": "VERIFIED_SCOPED_COMPRESSED_CONIC_NULL",
        "inputs_sha256": {str(path.relative_to(ROOT)): sha256_file(path) for path in inputs},
        "direct_four_root_rebuild": {
            "rows_rebuilt_and_matched": len(rebuilt_rows),
            "row_hash_list_sha256": canonical_sha256([row["primitive_row_sha256"] for row in rebuilt_rows]),
            "x6_nonzero_support": sum(value != 0 for value in x6.values()),
            "x6_map_sha256": canonical_sha256([[mask, value] for mask, value in sorted(x6.items())]),
            "contraction_summary": contraction_summary,
            "wave147_pair_root_matrices_regenerated": False,
        },
        "universal_affine_audit": {
            "coordinate_width_after_deletion": 917,
            "ordinary_deletion_pivots": 208,
            "nonzero_reduced_rows": len(universal),
            "modular_ranks": modular,
            "fixed_x7_or_pair_root_zero_rows_used": False,
            "count_nonnegativity_slacks_used": False,
        },
        "exact_quotient_kernel_audit": {
            "universal_nullspace_vectors_verified": len(nullspace),
            "universal_free_columns": free_columns,
            "quotient_map_sha256": quotient_hash,
            "quotient_rank": 8,
            "kernel_basis_vectors_verified": len(kernel_vectors),
            "kernel_dimension": 49,
        },
        "positive_definite_separator_audit": {
            "quotient_equation_coefficients": list(map(fstr, coefficients)),
            "direction_column_scales": {str(root): list(map(str, scales[root])) for root in ROOTS},
            "H3_sha256": canonical_sha256([[fstr(value) for value in row] for row in blocks[3]]),
            "H12_sha256": canonical_sha256([[fstr(value) for value in row] for row in blocks[12]]),
            "ldlt_positive_diagonals": {str(root): list(map(fstr, diagonals[root])) for root in ROOTS},
            "all_ldlt_pivots_strictly_positive": True,
            "off_diagonal_factor_two_and_direction_scaling_identity": "EXACT_PASS",
            "verdict": "NO_NONZERO_PSD_PAIR_IN_THE_49_DIMENSIONAL_COMPRESSED_KERNEL",
        },
        "scope_boundary": {
            "result": "rigorous null only for span(U3), span(U12), universal affine equalities, and no count slacks",
            "Conway_99": "OPEN",
            "endpoint_n3_4158": "UNKNOWN",
            "full_four_root_SDP": "NOT_RUN",
        },
        "resource_guard": {
            "minimum_required_free_physical_memory_percent": MEMORY_FLOOR,
            "minimum_observed_free_physical_memory_percent": min(float(record["free_physical_memory_percent"]) for record in memory),
            "elapsed_seconds": time.time() - started,
            "samples": memory,
        },
    }
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["claim_label"],
        "direct_rows": len(rebuilt_rows),
        "modular": modular,
        "quotient_rank": 8,
        "kernel_dimension": 49,
        "pd": True,
        "output": str(OUTPUT),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
