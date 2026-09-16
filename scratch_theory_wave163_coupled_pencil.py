#!/usr/bin/env python3
"""Exact compressed-pencil quotient test for the Wave163 draft lane.

This discovery script deliberately consumes the frozen class streams, linear
rows, and stored directions.  It does *not* rebuild the 916 order-eight
classes, the 208+944+4440 extension rows, or the 2,414 Wave147 matrices.

The full four-root matrices are also never materialised.  For root masks 3
and 12, the script contracts each induced-class contribution directly onto
the six/eight stored direction columns.  This produces exactly 21+36 affine
coefficient rows on (1,x7[208],x8[916]).  Ordinary deletion is then used as
an exact coordinate elimination, leaving (1,x8[916]), and sparse modular
row reduction computes the quotient rank over two primes.
"""

from __future__ import annotations

import ctypes
import gzip
import hashlib
import importlib.util
import itertools
import json
import math
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Sequence


ROOT = Path(__file__).resolve().parent
EXT = ROOT / "external_conway99_research"
W147 = EXT / "attempts/wave147-alternative-lane"
W148 = EXT / "attempts/wave148-marked-order8"
W152 = EXT / "attempts/wave152-four-root-order8"
W159 = EXT / "attempts/wave159-four-root-cut-loop"
W43_CHECK = EXT / "verification/wave43-seven-deck-endpoint/independent_check.py"
ROW_SYSTEM = EXT / "attempts/wave44-rooted-flags/row-system.json"

COEFFICIENT_ARCHIVE = W147 / "coefficients.json.gz"
W147_RESULT = W147 / "exact-results.json"
MARKED_ARCHIVE = W148 / "marked-rows.json.gz"
EVALUATION = W159 / "four-root-evaluation-after-fifteen-cuts.json"

CUT_PATHS = (
    W152 / "exact-cuts.json",
    W152 / "iteration2-cuts.json",
    W152 / "iteration3-mask13-cut.json",
    W152 / "iteration4-three-cuts.json",
    W152 / "simplified-mask12-cut.json",
    W152 / "iteration5-three-cuts.json",
    W152 / "simplified-mask12-cut-2.json",
    W159 / "fresh-two-cuts.json",
)

OUTPUT = ROOT / "scratch_theory_wave163_coupled_pencil.json"
COEFFICIENT_OUTPUT = (
    ROOT / "scratch_theory_wave163_coupled_pencil_coefficients.json.gz"
)

N = 99
N3 = 4158
ROOT_MASKS = (3, 12)
EXPECTED_DIRECTION_COUNTS = {3: 6, 12: 8}
PRIMES = (1_000_000_007, 1_000_000_009)
MIN_FREE_MEMORY_PERCENT = 18.0


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


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode(
        "ascii"
    )


def canonical_sha256(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def memory_record(label: str) -> dict[str, object]:
    status = MemoryStatusEx()
    status.length = ctypes.sizeof(status)
    ok = ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status))
    require(bool(ok), "GlobalMemoryStatusEx failed")
    free_percent = 100.0 * status.avail_phys / status.total_phys
    require(
        free_percent >= MIN_FREE_MEMORY_PERCENT,
        f"{label}: free physical memory {free_percent:.2f}% < 18% gate",
    )
    return {
        "label": label,
        "free_physical_memory_percent": round(free_percent, 4),
        "available_physical_gib": round(status.avail_phys / 2**30, 4),
        "total_physical_gib": round(status.total_phys / 2**30, 4),
    }


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_gzip_json(path: Path) -> dict[str, Any]:
    with gzip.open(path, "rt", encoding="ascii") as handle:
        return json.load(handle)


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    require(spec is not None and spec.loader is not None, f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def edges(order: int) -> tuple[tuple[int, int], ...]:
    return tuple(
        (left, right)
        for left in range(order)
        for right in range(left + 1, order)
    )


def edge_positions(order: int) -> dict[tuple[int, int], int]:
    return {edge: index for index, edge in enumerate(edges(order))}


def class_streams(
    coefficient_payload: dict[str, Any],
) -> dict[int, tuple[int, ...]]:
    streams_by_family: list[dict[int, list[int]]] = []
    for family_name in ("ordered_edge", "ordered_nonedge"):
        streams: dict[int, list[int]] = {order: [] for order in range(5, 9)}
        for record in coefficient_payload["families"][family_name][
            "class_coefficients"
        ]:
            streams[int(record["order"])].append(int(record["canonical_mask"]))
        streams_by_family.append(streams)
    require(streams_by_family[0] == streams_by_family[1], "family stream drift")
    streams = streams_by_family[0]
    require(
        tuple(len(streams[o]) for o in range(5, 9)) == (21, 62, 208, 916),
        "frozen class census changed",
    )
    return {order: tuple(values) for order, values in streams.items()}


def six_counts(classes6: Sequence[int]) -> dict[int, int]:
    """Evaluate only the frozen published six-class formula metadata."""
    w43 = load_module("wave163_frozen_w43_formulae", W43_CHECK)
    values = w43.evaluate_integral(w43.six_formulae(), N3)
    result = dict(zip(map(int, w43.SOURCE_N_MASKS), map(int, values), strict=True))
    require(set(result) == set(classes6), "six-class formula stream mismatch")
    require(sum(result.values()) == math.comb(N, 6), "six-count total mismatch")
    return result


def all_cuts() -> list[dict[str, Any]]:
    cuts: list[dict[str, Any]] = []
    for path in CUT_PATHS:
        payload = load_json(path)
        cuts.extend(payload["cuts"] if "cuts" in payload else [payload["cut"]])
    require(len(cuts) == 15, "retained cut count changed")
    return cuts


def dense_certificate(block: dict[str, Any]) -> list[int]:
    result = [0] * int(block["flag_count"])
    certificate = block["negative_certificate"]
    require(certificate is not None, "missing recurrent negative certificate")
    for index, value in zip(
        certificate["indices"], certificate["vector"], strict=True
    ):
        result[int(index)] = int(value)
    return result


def direction_data(
    cuts: Sequence[dict[str, Any]], evaluation: dict[str, Any]
) -> dict[int, dict[str, Any]]:
    blocks = {
        int(block["root_mask"]): block
        for block in evaluation["root_blocks"]
        if int(block["root_mask"]) in ROOT_MASKS
    }
    require(set(blocks) == set(ROOT_MASKS), "persistent blocks missing")
    result: dict[int, dict[str, Any]] = {}
    for root in ROOT_MASKS:
        block = blocks[root]
        flags = tuple(map(int, block["flag_masks"]))
        retained = [cut for cut in cuts if int(cut["root_mask"]) == root]
        directions = [list(map(int, cut["direction"])) for cut in retained]
        labels = [f"retained:{cut['cut_sha256']}" for cut in retained]
        directions.append(dense_certificate(block))
        recurrent_hash = canonical_sha256(directions[-1])
        labels.append(f"recurrent:{recurrent_hash}")
        require(
            len(directions) == EXPECTED_DIRECTION_COUNTS[root],
            f"root {root} direction count changed",
        )
        require(
            all(len(direction) == len(flags) for direction in directions),
            f"root {root} direction width changed",
        )
        # Stored certificate redundantly records the supported flag masks.
        certificate = block["negative_certificate"]
        require(
            list(map(int, certificate["flag_masks"]))
            == [flags[int(i)] for i in certificate["indices"]],
            f"root {root} recurrent flag-mask alignment failed",
        )
        result[root] = {
            "root_count": int(block["root_embedding_count"]),
            "flags": flags,
            "labels": labels,
            "directions": directions,
        }
    return result


def rank_columns_mod(columns: Sequence[Sequence[int]], prime: int) -> int:
    """Small exact modular rank; columns are stored direction vectors."""
    basis: dict[int, dict[int, int]] = {}
    rank = 0
    for column in columns:
        row = {i: int(v) % prime for i, v in enumerate(column) if int(v) % prime}
        while row:
            hit = next((key for key in row if key in basis), None)
            if hit is None:
                pivot = min(row)
                inverse = pow(row[pivot], -1, prime)
                row = {key: value * inverse % prime for key, value in row.items()}
                basis[pivot] = row
                rank += 1
                break
            factor = row[hit]
            for key, value in basis[hit].items():
                updated = (row.get(key, 0) - factor * value) % prime
                if updated:
                    row[key] = updated
                else:
                    row.pop(key, None)
    return rank


def extraction_configs(order: int) -> tuple[dict[str, Any], ...]:
    source_positions = edge_positions(order)
    target_edges = edges(6)
    result = []
    for roots in itertools.permutations(range(order), 4):
        complement = tuple(vertex for vertex in range(order) if vertex not in roots)
        pairs = tuple(itertools.combinations(complement, 2))
        root_bits = tuple(
            source_positions[tuple(sorted((roots[left], roots[right])))]
            for left, right in edges(4)
        )
        flag_bits = []
        for pair in pairs:
            selected = roots + pair
            flag_bits.append(
                tuple(
                    source_positions[
                        tuple(sorted((selected[left], selected[right])))
                    ]
                    for left, right in target_edges
                )
            )
        if order == 6:
            covering = ((0, 0),)
        else:
            covering = tuple(
                (left, right)
                for left in range(len(pairs))
                for right in range(left + 1, len(pairs))
                if len(set(pairs[left]).union(pairs[right])) == order - 4
            )
        result.append(
            {"root_bits": root_bits, "flag_bits": tuple(flag_bits), "covering": covering}
        )
    return tuple(result)


def extract_mask(graph_mask: int, bit_positions: Sequence[int]) -> int:
    result = 0
    for target, source in enumerate(bit_positions):
        result |= ((graph_mask >> source) & 1) << target
    return result


def free_swap_map() -> tuple[int, ...]:
    source = edge_positions(6)
    permutation = (0, 1, 2, 3, 5, 4)
    bit_map = tuple(
        source[tuple(sorted((permutation[left], permutation[right])))]
        for left, right in edges(6)
    )
    result = []
    for mask in range(1 << 15):
        swapped = extract_mask(mask, bit_map)
        result.append(min(mask, swapped))
    return tuple(result)


def triangular_pairs(size: int) -> tuple[tuple[int, int], ...]:
    return tuple((i, j) for i in range(size) for j in range(i, size))


def add_same_vector_outer(
    target: list[int], sparse_vector: Sequence[tuple[int, int]], pair_index: dict[tuple[int, int], int]
) -> None:
    for left, (i, vi) in enumerate(sparse_vector):
        for j, vj in sparse_vector[left:]:
            target[pair_index[(i, j)]] += vi * vj


def add_distinct_vector_pair(
    target: list[int],
    left_vector: Sequence[tuple[int, int]],
    right_vector: Sequence[tuple[int, int]],
    pair_index: dict[tuple[int, int], int],
) -> None:
    # One unordered free-pair pair represents both ordered products.  Mapping
    # the full outer product to an upper triangle automatically supplies both
    # cross terms; its diagonal needs the explicit factor two.
    for i, vi in left_vector:
        for j, vj in right_vector:
            key = (i, j) if i <= j else (j, i)
            target[pair_index[key]] += (2 if i == j else 1) * vi * vj


def build_compressed_rows(
    streams: dict[int, tuple[int, ...]],
    counts6: dict[int, int],
    roots: dict[int, dict[str, Any]],
    memory: list[dict[str, object]],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    swap = free_swap_map()
    work: dict[int, dict[str, Any]] = {}
    for root, data in roots.items():
        pairs = triangular_pairs(len(data["directions"]))
        flag_index = {mask: index for index, mask in enumerate(data["flags"])}
        vectors_by_flag = []
        for flag_position in range(len(data["flags"])):
            sparse = tuple(
                (column, int(direction[flag_position]))
                for column, direction in enumerate(data["directions"])
                if int(direction[flag_position])
            )
            vectors_by_flag.append(sparse)
        work[root] = {
            "pairs": pairs,
            "pair_index": {pair: index for index, pair in enumerate(pairs)},
            "flag_index": flag_index,
            "vectors_by_flag": tuple(vectors_by_flag),
            "weighted_q6": [0] * len(pairs),
            "weighted_s6": [0] * len(data["directions"]),
            "coeff7": [dict() for _ in pairs],
            "coeff8": [dict() for _ in pairs],
            "matched_embeddings": Counter(),
        }

    for order in (6, 7, 8):
        configs = extraction_configs(order)
        for class_index, graph_mask in enumerate(streams[order]):
            local = {
                root: [0] * len(work[root]["pairs"]) for root in ROOT_MASKS
            }
            local_s = {
                root: [0] * len(roots[root]["directions"]) for root in ROOT_MASKS
            }
            matched = Counter()
            for config in configs:
                induced_root = extract_mask(graph_mask, config["root_bits"])
                if induced_root not in work:
                    continue
                root_work = work[induced_root]
                flag_positions = []
                for bits in config["flag_bits"]:
                    induced_flag = extract_mask(graph_mask, bits)
                    canonical_flag = swap[induced_flag]
                    require(
                        canonical_flag in root_work["flag_index"],
                        "induced flag escaped frozen flag universe",
                    )
                    flag_positions.append(root_work["flag_index"][canonical_flag])
                vectors = [
                    root_work["vectors_by_flag"][position]
                    for position in flag_positions
                ]
                if order == 6:
                    for coordinate, value in vectors[0]:
                        local_s[induced_root][coordinate] += value
                    add_same_vector_outer(
                        local[induced_root],
                        vectors[0],
                        root_work["pair_index"],
                    )
                else:
                    for left, right in config["covering"]:
                        if vectors[left] and vectors[right]:
                            add_distinct_vector_pair(
                                local[induced_root],
                                vectors[left],
                                vectors[right],
                                root_work["pair_index"],
                            )
                matched[induced_root] += 1

            for root in ROOT_MASKS:
                root_work = work[root]
                root_work["matched_embeddings"][(order, class_index)] = matched[root]
                if order == 6:
                    weight = counts6[int(graph_mask)]
                    for index, value in enumerate(local[root]):
                        root_work["weighted_q6"][index] += weight * value
                    for index, value in enumerate(local_s[root]):
                        root_work["weighted_s6"][index] += weight * value
                else:
                    target = root_work[f"coeff{order}"]
                    for index, value in enumerate(local[root]):
                        if value:
                            target[index][class_index] = value
            if class_index % 64 == 0:
                memory.append(memory_record(f"contract_o{order}_class_{class_index}"))
        memory.append(memory_record(f"contract_order_{order}_complete"))

    rows: list[dict[str, Any]] = []
    summary: dict[str, Any] = {}
    for root in ROOT_MASKS:
        data = roots[root]
        root_work = work[root]
        root_count = int(data["root_count"])
        for pair_position, (left, right) in enumerate(root_work["pairs"]):
            constant = (
                root_count * root_work["weighted_q6"][pair_position]
                - root_work["weighted_s6"][left]
                * root_work["weighted_s6"][right]
            )
            a7 = {
                int(streams[7][index]): root_count * int(value)
                for index, value in root_work["coeff7"][pair_position].items()
            }
            a8 = {
                int(streams[8][index]): root_count * int(value)
                for index, value in root_work["coeff8"][pair_position].items()
            }
            divisor = 0
            for value in itertools.chain((constant,), a7.values(), a8.values()):
                divisor = math.gcd(divisor, abs(int(value)))
            # A bilinear cross entry can vanish identically even though both
            # diagonal quadratic forms are nonzero.  Retain that coordinate:
            # it is genuine quotient-kernel information (and matters to the
            # later PSD interpretation).  Use divisor one for its canonical
            # zero representation.
            if divisor == 0:
                divisor = 1
            core = {
                "root_mask": root,
                "direction_indices": [left, right],
                "direction_labels": [data["labels"][left], data["labels"][right]],
                "raw_divisor": str(divisor),
                "constant": str(constant // divisor),
                "order7_coefficients": [
                    [mask, str(value // divisor)] for mask, value in sorted(a7.items())
                ],
                "order8_coefficients": [
                    [mask, str(value // divisor)] for mask, value in sorted(a8.items())
                ],
            }
            rows.append({**core, "primitive_row_sha256": canonical_sha256(core)})
        summary[str(root)] = {
            "directions": len(data["directions"]),
            "compressed_rows": len(root_work["pairs"]),
            "root_embedding_count": root_count,
            "weighted_first_moments": list(map(str, root_work["weighted_s6"])),
            "weighted_order6_quadratic_upper": list(
                map(str, root_work["weighted_q6"])
            ),
            "matched_embedding_totals_by_order": {
                str(order): sum(
                    count
                    for (local_order, _), count in root_work[
                        "matched_embeddings"
                    ].items()
                    if local_order == order
                )
                for order in (6, 7, 8)
            },
        }
    require(len(rows) == 57, "compressed row count is not 57")
    return rows, summary


def row_maps(record: dict[str, Any]) -> tuple[int, dict[int, int], dict[int, int]]:
    divisor = int(record["raw_divisor"])
    constant = divisor * int(record["constant"])
    a7 = {
        int(mask): divisor * int(value)
        for mask, value in record["order7_coefficients"]
    }
    a8 = {
        int(mask): divisor * int(value)
        for mask, value in record["order8_coefficients"]
    }
    return constant, a7, a8


def validate_diagonal_cuts(
    rows: Sequence[dict[str, Any]], cuts: Sequence[dict[str, Any]]
) -> list[dict[str, Any]]:
    by_root_pair = {
        (int(row["root_mask"]), tuple(row["direction_indices"])): row for row in rows
    }
    records = []
    for root in ROOT_MASKS:
        retained = [cut for cut in cuts if int(cut["root_mask"]) == root]
        for index, cut in enumerate(retained):
            row = by_root_pair[(root, (index, index))]
            require(int(row["raw_divisor"]) == int(cut["primitive_divisor"]), "diagonal gcd drift")
            require(int(row["constant"]) == int(cut["constant"]), "diagonal constant drift")
            observed7 = {int(mask): int(value) for mask, value in row["order7_coefficients"]}
            expected7 = {
                int(item["canonical_mask"]): int(item["coefficient"])
                for item in cut["order7_coefficients"]
            }
            observed8 = {int(mask): int(value) for mask, value in row["order8_coefficients"]}
            expected8 = {
                int(item["canonical_mask"]): int(item["coefficient"])
                for item in cut["order8_coefficients"]
            }
            require((observed7, observed8) == (expected7, expected8), "diagonal coefficient drift")
            records.append(
                {
                    "root_mask": root,
                    "direction_index": index,
                    "cut_sha256": cut["cut_sha256"],
                    "coefficient_match": True,
                }
            )
    require(len(records) == 12, "expected twelve retained root-3/root-12 diagonals")
    return records


def deletion_maps(
    coefficient_payload: dict[str, Any], classes7: Sequence[int], classes8: Sequence[int]
) -> list[dict[int, int]]:
    index7 = {mask: index for index, mask in enumerate(classes7)}
    index8 = {mask: index for index, mask in enumerate(classes8)}
    result: list[dict[int, int]] = [dict() for _ in classes7]
    records = coefficient_payload["order7_to_order8_deletion_equations"]
    require(len(records) == len(classes7), "deletion row count drift")
    for record in records:
        require(int(record["left_multiplier"]) == 92, "deletion multiplier drift")
        row = index7[int(record["order7_mask"])]
        result[row] = {
            index8[int(mask)]: int(value)
            for mask, value in record["terms_order8_mask_multiplicity"]
        }
    require(all(result), "empty deletion expansion")
    return result


def eliminate_x7(
    constant: int,
    a7: dict[int, int],
    a8: dict[int, int],
    index7: dict[int, int],
    index8: dict[int, int],
    deletion: Sequence[dict[int, int]],
) -> dict[int, int]:
    # 92*x7_H = sum_K deletion(H,K)*x8_K.  Multiplying the transformed
    # equation by 92 keeps every coefficient integral.
    result: dict[int, int] = {}

    def increment(key: int, value: int) -> None:
        if not value:
            return
        updated = result.get(key, 0) + value
        if updated:
            result[key] = updated
        else:
            result.pop(key, None)

    increment(0, 92 * constant)
    for mask, value in a7.items():
        for column, multiplicity in deletion[index7[int(mask)]].items():
            increment(1 + column, int(value) * multiplicity)
    for mask, value in a8.items():
        increment(1 + index8[int(mask)], 92 * int(value))
    return result


def universal_reduced_rows(
    coefficient_payload: dict[str, Any],
    marked_payload: dict[str, Any],
    row_system: dict[str, Any],
    classes7: Sequence[int],
    classes8: Sequence[int],
) -> tuple[list[dict[int, int]], list[str], list[dict[int, int]]]:
    index7 = {mask: index for index, mask in enumerate(classes7)}
    index8 = {mask: index for index, mask in enumerate(classes8)}
    deletion = deletion_maps(coefficient_payload, classes7, classes8)
    rows: list[dict[int, int]] = []
    labels: list[str] = []

    def add(
        label: str, constant: int, a7: dict[int, int], a8: dict[int, int]
    ) -> None:
        reduced = eliminate_x7(constant, a7, a8, index7, index8, deletion)
        if reduced:
            rows.append(reduced)
            labels.append(label)

    # Exact count normalisations.
    add(
        "normalization:x7",
        -math.comb(N, 7),
        {int(mask): 1 for mask in classes7},
        {},
    )
    add(
        "normalization:x8",
        -math.comb(N, 8),
        {},
        {int(mask): 1 for mask in classes8},
    )

    # Wave44 rows are sum a_H*x7_H + a_y*n3 = rhs.  Here n3 is frozen
    # universally at the endpoint value 4158 and moved into the constant.
    for family_name in ("base", "vertex", "edge", "nonedge"):
        family = row_system["families"][family_name]
        for local_index, (raw, rhs) in enumerate(
            zip(family["rows"], family["rhs"], strict=True)
        ):
            require(len(raw) == len(classes7) + 1, "Wave44 width drift")
            add(
                f"wave44:{family_name}:{local_index}",
                int(raw[-1]) * N3 - int(rhs),
                {
                    int(mask): int(value)
                    for mask, value in zip(classes7, raw[:-1], strict=True)
                    if int(value)
                },
                {},
            )

    records = marked_payload["vertex_rows"] + marked_payload["ordered_pair_rows"]
    require(len(records) == 944 + 4440, "marked row count drift")
    for record in records:
        lhs = int(record["lhs_coefficient"])
        a7 = {int(record["order7_mask"]): lhs} if lhs else {}
        a8 = {
            int(mask): -int(value)
            for mask, value in record["terms_order8_mask_coefficient"]
            if int(value)
        }
        add(f"marked:{record['row_id']}", 0, a7, a8)
    return rows, labels, deletion


def primitive_sparse(row: dict[int, int]) -> dict[int, int]:
    if not row:
        return {}
    divisor = 0
    for value in row.values():
        divisor = math.gcd(divisor, abs(int(value)))
    require(divisor > 0, "cannot primitive-normalize zero row")
    result = {key: int(value) // divisor for key, value in row.items()}
    first = result[min(result)]
    if first < 0:
        result = {key: -value for key, value in result.items()}
    return result


def sparse_rows_sha256(rows: Sequence[dict[int, int]]) -> str:
    normalized = [
        [[int(key), str(value)] for key, value in sorted(primitive_sparse(row).items())]
        for row in rows
    ]
    return canonical_sha256(normalized)


def insert_sparse_row(
    source: dict[int, int],
    prime: int,
    basis: dict[int, dict[int, int]],
    pivot_age: dict[int, int],
    column_frequency: Sequence[int],
) -> bool:
    row = {key: int(value) % prime for key, value in source.items() if int(value) % prime}
    while row:
        hits = [key for key in row if key in basis]
        if hits:
            pivot = min(hits, key=pivot_age.__getitem__)
            factor = row[pivot]
            for key, value in basis[pivot].items():
                updated = (row.get(key, 0) - factor * value) % prime
                if updated:
                    row[key] = updated
                else:
                    row.pop(key, None)
            continue
        pivot = min(row, key=lambda key: (column_frequency[key], key))
        inverse = pow(row[pivot], -1, prime)
        row = {key: value * inverse % prime for key, value in row.items()}
        pivot_age[pivot] = len(basis)
        basis[pivot] = row
        return True
    return False


def reduce_sparse_row_mod(
    source: dict[int, int],
    prime: int,
    basis: dict[int, dict[int, int]],
    pivot_age: dict[int, int],
) -> dict[int, int]:
    """Return the canonical remainder after the insertion-order row basis."""
    row = {
        key: int(value) % prime
        for key, value in source.items()
        if int(value) % prime
    }
    while True:
        hits = [key for key in row if key in basis]
        if not hits:
            return row
        pivot = min(hits, key=pivot_age.__getitem__)
        factor = row[pivot]
        for key, value in basis[pivot].items():
            updated = (row.get(key, 0) - factor * value) % prime
            if updated:
                row[key] = updated
            else:
                row.pop(key, None)


def modular_quotient_rank(
    universal: Sequence[dict[int, int]],
    compressed: Sequence[dict[int, int]],
    prime: int,
    width: int,
) -> dict[str, Any]:
    frequencies = [0] * width
    for row in universal:
        for key in row:
            frequencies[key] += 1
    # Sparse-first row order is a deterministic fill-reduction heuristic.
    ordered = sorted(
        enumerate(universal), key=lambda item: (len(item[1]), min(item[1]), item[0])
    )
    basis: dict[int, dict[int, int]] = {}
    ages: dict[int, int] = {}
    independent_universal = 0
    for _, row in ordered:
        independent_universal += insert_sparse_row(
            row, prime, basis, ages, frequencies
        )
    universal_rank = len(basis)
    universal_pivots = tuple(basis)
    free_columns = tuple(column for column in range(width) if column not in basis)
    remainders = [
        reduce_sparse_row_mod(row, prime, basis, ages) for row in compressed
    ]
    require(
        all(set(row).issubset(free_columns) for row in remainders),
        "universal remainder retained a pivot column",
    )
    quotient_basis: dict[int, dict[int, int]] = {}
    quotient_ages: dict[int, int] = {}
    quotient_pivots = []
    for row_index, row in enumerate(remainders):
        if insert_sparse_row(
            row,
            prime,
            quotient_basis,
            quotient_ages,
            frequencies,
        ):
            quotient_pivots.append(row_index)
    return {
        "prime": prime,
        "reduced_universal_rank": universal_rank,
        "full_universal_rank_in_1125_coordinates": 208 + universal_rank,
        "compressed_quotient_rank": len(quotient_pivots),
        "compressed_quotient_nullity": len(compressed) - len(quotient_pivots),
        "compressed_pivot_row_indices": quotient_pivots,
        "combined_reduced_rank": universal_rank + len(quotient_pivots),
        "universal_pivot_columns": list(universal_pivots),
        "universal_free_columns": list(free_columns),
        "compressed_quotient_matrix": [
            [int(row.get(column, 0)) for column in free_columns]
            for row in remainders
        ],
        "basis_nonzero_entries": sum(len(row) for row in basis.values()),
        "maximum_basis_row_support": max(map(len, basis.values()), default=0),
    }


def build() -> tuple[dict[str, Any], bytes]:
    started = time.time()
    memory = [memory_record("start")]
    input_paths = [
        COEFFICIENT_ARCHIVE,
        W147_RESULT,
        MARKED_ARCHIVE,
        ROW_SYSTEM,
        W43_CHECK,
        EVALUATION,
        *CUT_PATHS,
    ]
    input_hashes = {str(path.relative_to(ROOT)): sha256_file(path) for path in input_paths}

    coefficients = load_gzip_json(COEFFICIENT_ARCHIVE)
    marked = load_gzip_json(MARKED_ARCHIVE)
    row_system = load_json(ROW_SYSTEM)
    streams = class_streams(coefficients)
    require(tuple(map(int, row_system["classes"])) == streams[7], "Wave44 stream drift")
    w147_result = load_json(W147_RESULT)
    require(
        tuple(map(int, w147_result["class_streams"]["8"]["canonical_masks"]))
        == streams[8],
        "order-eight stream drift",
    )
    memory.append(memory_record("frozen_inputs_loaded"))

    cuts = all_cuts()
    roots = direction_data(cuts, load_json(EVALUATION))
    direction_ranks = {
        str(root): {
            str(prime): rank_columns_mod(data["directions"], prime)
            for prime in PRIMES
        }
        for root, data in roots.items()
    }
    for root, ranks in direction_ranks.items():
        require(
            set(ranks.values()) == {EXPECTED_DIRECTION_COUNTS[int(root)]},
            f"root {root} directions are dependent",
        )

    counts6 = six_counts(streams[6])
    compressed_rows, contraction_summary = build_compressed_rows(
        streams, counts6, roots, memory
    )
    diagonal_replay = validate_diagonal_cuts(compressed_rows, cuts)
    memory.append(memory_record("compressed_rows_complete"))

    universal, universal_labels, deletion = universal_reduced_rows(
        coefficients, marked, row_system, streams[7], streams[8]
    )
    index7 = {mask: index for index, mask in enumerate(streams[7])}
    index8 = {mask: index for index, mask in enumerate(streams[8])}
    reduced_compressed = [
        eliminate_x7(*row_maps(row), index7, index8, deletion)
        for row in compressed_rows
    ]
    # Zero compressed rows and rows lying in the deletion span are allowed;
    # both correctly contribute to the quotient kernel.
    memory.append(memory_record("universal_rows_complete"))

    modular = []
    for prime in PRIMES:
        memory.append(memory_record(f"before_rank_mod_{prime}"))
        modular.append(
            modular_quotient_rank(
                universal, reduced_compressed, prime, 1 + len(streams[8])
            )
        )
        memory.append(memory_record(f"after_rank_mod_{prime}"))

    quotient_ranks = {record["compressed_quotient_rank"] for record in modular}
    nullities = {record["compressed_quotient_nullity"] for record in modular}
    require(len(quotient_ranks) == len(nullities) == 1, "prime rank disagreement")
    quotient_rank = next(iter(quotient_ranks))
    nullity = next(iter(nullities))

    direction_metadata = {
        str(root): {
            "flag_count": len(data["flags"]),
            "flag_masks_sha256": canonical_sha256(data["flags"]),
            "direction_count": len(data["directions"]),
            "direction_labels": data["labels"],
            "direction_sha256": [canonical_sha256(row) for row in data["directions"]],
            "direction_supports": [sum(value != 0 for value in row) for row in data["directions"]],
        }
        for root, data in roots.items()
    }

    coefficient_core = {
        "format": "wave163-compressed-four-root-pencil-coefficients-v1",
        "coordinate_system": {
            "constant": 1,
            "order7_masks": list(streams[7]),
            "order8_masks": list(streams[8]),
            "width": 1 + len(streams[7]) + len(streams[8]),
        },
        "directions": direction_metadata,
        "rows": compressed_rows,
    }
    coefficient_bytes = gzip.compress(canonical_bytes(coefficient_core), compresslevel=9, mtime=0)
    coefficient_payload_sha256 = canonical_sha256(coefficient_core)

    result = {
        "format": "wave163-coupled-conic-compressed-rank-v1",
        "claim_label": "EXACT_SCOPED_NULL" if nullity == 0 else "EXACT_KERNEL_FOUND",
        "scope": (
            "Only affine identities from the root-mask-3/root-mask-12 stored-direction "
            "compressed covariance rows modulo universal endpoint equalities; no count "
            "slacks, full four-root SDP, or fixed-x7/pair-root-zero rows."
        ),
        "target": {"srg": [99, 14, 1, 2], "n3": N3},
        "inputs_sha256": input_hashes,
        "frozen_inputs_consumed_not_regenerated": {
            "order8_classes": len(streams[8]),
            "ordinary_deletion_rows": len(coefficients["order7_to_order8_deletion_equations"]),
            "marked_vertex_rows": len(marked["vertex_rows"]),
            "marked_pair_rows": len(marked["ordered_pair_rows"]),
            "wave147_class_matrices": sum(
                len(family["class_coefficients"])
                for family in coefficients["families"].values()
            ),
        },
        "directions": direction_metadata,
        "direction_column_ranks_mod_primes": direction_ranks,
        "compressed_pencil": {
            "root3_symmetric_coordinates": 21,
            "root12_symmetric_coordinates": 36,
            "total_rows": len(compressed_rows),
            "contraction_summary": contraction_summary,
            "retained_diagonal_cut_replays": diagonal_replay,
            "coefficient_artifact": str(COEFFICIENT_OUTPUT.name),
            "coefficient_payload_sha256": coefficient_payload_sha256,
            "coefficient_gzip_sha256": hashlib.sha256(coefficient_bytes).hexdigest(),
            "coefficient_gzip_bytes": len(coefficient_bytes),
            "primitive_row_hashes_sha256": canonical_sha256(
                [row["primitive_row_sha256"] for row in compressed_rows]
            ),
        },
        "universal_endpoint_affine_space": {
            "original_coordinate_width": 1 + len(streams[7]) + len(streams[8]),
            "ordinary_deletion_pivots_eliminated": len(streams[7]),
            "reduced_coordinate_width": 1 + len(streams[8]),
            "input_row_counts": {
                "normalizations": 2,
                "wave44": sum(
                    len(row_system["families"][name]["rows"])
                    for name in ("base", "vertex", "edge", "nonedge")
                ),
                "deletion": len(streams[7]),
                "marked_vertex": len(marked["vertex_rows"]),
                "marked_pair": len(marked["ordered_pair_rows"]),
            },
            "nonzero_reduced_rows": len(universal),
            "reduced_row_labels_sha256": canonical_sha256(universal_labels),
            "reduced_primitive_rows_sha256": sparse_rows_sha256(universal),
            "compressed_reduced_primitive_rows_sha256": sparse_rows_sha256(reduced_compressed),
            "excluded_conditional_rows": ["fixed x7", "pair-root covariance zero face"],
        },
        "modular_rank_certificates": modular,
        "exact_conclusion": {
            "compressed_quotient_rank_over_Q": quotient_rank,
            "compressed_quotient_kernel_dimension_over_Q": nullity,
            "psd_kernel_test": "VACUOUS_NO_NONZERO_KERNEL" if nullity == 0 else "REQUIRED",
            "scoped_boundary": (
                "Full quotient rank rules out every nonzero (even indefinite) Y3,Y12 "
                "affine identity in this 57-coordinate compressed lane. It does not rule "
                "out nonnegative count slacks, directions outside U3/U12, other blocks, "
                "or higher-order variables."
                if nullity == 0
                else "A rational-kernel and exact PSD analysis is still required."
            ),
            "Conway_99": "UNKNOWN",
        },
        "resource_guard": {
            "minimum_free_physical_memory_percent_required": MIN_FREE_MEMORY_PERCENT,
            "samples": memory,
            "minimum_observed_free_physical_memory_percent": min(
                float(item["free_physical_memory_percent"]) for item in memory
            ),
            "elapsed_seconds": round(time.time() - started, 3),
        },
    }
    return result, coefficient_bytes


def main() -> int:
    result, coefficient_bytes = build()
    COEFFICIENT_OUTPUT.write_bytes(coefficient_bytes)
    OUTPUT.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(OUTPUT),
        "coefficient_output": str(COEFFICIENT_OUTPUT),
        "claim_label": result["claim_label"],
        "modular_rank_certificates": result["modular_rank_certificates"],
        "elapsed_seconds": result["resource_guard"]["elapsed_seconds"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
