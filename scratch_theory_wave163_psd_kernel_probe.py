#!/usr/bin/env python3
"""Independent numerical probe for a PSD element in the Wave163 kernel.

This reads only the frozen compressed coefficient artifact and the three raw
universal-row artifacts.  It deliberately does not import the Wave163
discovery program.  The probe eliminates x7 with the frozen deletion deck,
finds a modular pivot minor of the remaining universal rows, constructs a
floating nullspace chart from that minor, and tests the resulting eight
compressed quotient equations for a PSD solution.
"""

from __future__ import annotations

import ctypes
import gzip
import json
import math
import sys
from fractions import Fraction
from pathlib import Path

import cvxpy as cp
import numpy as np
from scipy import sparse
from scipy.optimize import linprog
from scipy.sparse.linalg import splu


ROOT = Path(__file__).resolve().parent
COEFF_PATH = ROOT / "scratch_theory_wave163_coupled_pencil_coefficients.json.gz"
W44_PATH = ROOT / "external_conway99_research/attempts/wave44-rooted-flags/row-system.json"
W147_PATH = ROOT / "external_conway99_research/attempts/wave147-alternative-lane/coefficients.json.gz"
W148_PATH = ROOT / "external_conway99_research/attempts/wave148-marked-order8/marked-rows.json.gz"
P = 1_000_000_007
N3 = 4158
C7 = math.comb(99, 7)
C8 = math.comb(99, 8)


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


def memory_gate() -> float:
    status = MemoryStatusEx()
    status.length = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise RuntimeError("GlobalMemoryStatusEx failed")
    free = 100.0 * status.avail_phys / status.total_phys
    if free < 18.0:
        raise RuntimeError(f"18% memory gate failed: {free:.3f}%")
    return free


def add(target: dict[int, int], column: int, value: int) -> None:
    if not value:
        return
    new = target.get(column, 0) + value
    if new:
        target[column] = new
    else:
        target.pop(column, None)


def primitive(row: dict[int, int]) -> dict[int, int]:
    if not row:
        return {}
    divisor = math.gcd(*(abs(value) for value in row.values()))
    out = {column: value // divisor for column, value in row.items()}
    first = out[min(out)]
    if first < 0:
        out = {column: -value for column, value in out.items()}
    return out


def build_rows() -> tuple[list[dict[int, int]], list[dict[int, int]], list[dict]]:
    compressed = json.load(gzip.open(COEFF_PATH, "rt", encoding="utf-8"))
    wave44 = json.loads(W44_PATH.read_text(encoding="utf-8"))
    wave147 = json.load(gzip.open(W147_PATH, "rt", encoding="utf-8"))
    wave148 = json.load(gzip.open(W148_PATH, "rt", encoding="utf-8"))

    masks7 = [int(mask) for mask in compressed["coordinate_system"]["order7_masks"]]
    masks8 = [int(mask) for mask in compressed["coordinate_system"]["order8_masks"]]
    assert masks7 == [int(mask) for mask in wave44["classes"]]
    index7 = {mask: i for i, mask in enumerate(masks7)}
    index8 = {mask: i for i, mask in enumerate(masks8)}
    deletion: list[dict[int, int]] = [{} for _ in masks7]
    for record in wave147["order7_to_order8_deletion_equations"]:
        h = index7[int(record["order7_mask"])]
        assert int(record["left_multiplier"]) == 92
        deletion[h] = {
            index8[int(mask)]: int(value)
            for mask, value in record["terms_order8_mask_multiplicity"]
        }

    # Reduced coordinates are (constant,x8); multiply every substituted row
    # by 92 to retain integers.
    universal: list[dict[int, int]] = []
    for family_name in ("base", "vertex", "edge", "nonedge"):
        family = wave44["families"][family_name]
        for raw, rhs in zip(family["rows"], family["rhs"], strict=True):
            row: dict[int, int] = {}
            add(row, 0, 92 * (int(raw[-1]) * N3 - int(rhs)))
            for h, coefficient in enumerate(raw[:-1]):
                for k, multiplicity in deletion[h].items():
                    add(row, 1 + k, int(coefficient) * multiplicity)
            universal.append(primitive(row))

    for record in wave148["vertex_rows"] + wave148["ordered_pair_rows"]:
        row = {}
        h = index7[int(record["order7_mask"])]
        lhs = int(record["lhs_coefficient"])
        for k, multiplicity in deletion[h].items():
            add(row, 1 + k, -lhs * multiplicity)
        for mask, coefficient in record["terms_order8_mask_coefficient"]:
            add(row, 1 + index8[int(mask)], 92 * int(coefficient))
        universal.append(primitive(row))

    norm7: dict[int, int] = {0: -92 * C7}
    for deck in deletion:
        for k, multiplicity in deck.items():
            add(norm7, 1 + k, multiplicity)
    universal.append(primitive(norm7))
    universal.append(primitive({0: -C8, **{1 + k: 1 for k in range(len(masks8))}}))
    universal = [row for row in universal if row]

    reduced_compressed: list[dict[int, int]] = []
    records: list[dict] = []
    for record in compressed["rows"]:
        row: dict[int, int] = {}
        add(row, 0, 92 * int(record["constant"]))
        for mask, coefficient in record["order7_coefficients"]:
            h = index7[int(mask)]
            for k, multiplicity in deletion[h].items():
                add(row, 1 + k, int(coefficient) * multiplicity)
        for mask, coefficient in record["order8_coefficients"]:
            add(row, 1 + index8[int(mask)], 92 * int(coefficient))
        reduced_compressed.append(primitive(row))
        records.append(record)
    return universal, reduced_compressed, records


def modular_pivots(rows: list[dict[int, int]]) -> tuple[list[int], list[int]]:
    basis: dict[int, dict[int, int]] = {}
    source_by_pivot: dict[int, int] = {}
    for source, raw in enumerate(rows):
        row = {column: value % P for column, value in raw.items() if value % P}
        while row:
            pivot = min(row)
            old = basis.get(pivot)
            if old is None:
                inverse = pow(row[pivot], P - 2, P)
                row = {
                    column: value * inverse % P
                    for column, value in row.items()
                    if value * inverse % P
                }
                basis[pivot] = row
                source_by_pivot[pivot] = source
                break
            factor = row[pivot]
            for column, value in old.items():
                new = (row.get(column, 0) - factor * value) % P
                if new:
                    row[column] = new
                else:
                    row.pop(column, None)
    pivots = sorted(basis)
    return pivots, [source_by_pivot[pivot] for pivot in pivots]


def modular_basis(rows: list[dict[int, int]], prime: int) -> dict[int, dict[int, int]]:
    basis: dict[int, dict[int, int]] = {}
    for raw in rows:
        row = {column: value % prime for column, value in raw.items() if value % prime}
        while row:
            pivot = min(row)
            old = basis.get(pivot)
            if old is None:
                inverse = pow(row[pivot], prime - 2, prime)
                basis[pivot] = {
                    column: value * inverse % prime
                    for column, value in row.items()
                    if value * inverse % prime
                }
                break
            factor = row[pivot]
            for column, value in old.items():
                new = (row.get(column, 0) - factor * value) % prime
                if new:
                    row[column] = new
                else:
                    row.pop(column, None)
    return basis


def quotient_relations(
    universal: list[dict[int, int]],
    compressed: list[dict[int, int]],
    prime: int,
) -> tuple[list[int], dict[int, dict[int, int]]]:
    universal_basis = modular_basis(universal, prime)
    universal_pivots = sorted(universal_basis)
    quotient_basis: dict[int, tuple[dict[int, int], dict[int, int]]] = {}
    quotient_pivots: list[int] = []
    relations: dict[int, dict[int, int]] = {}
    for source, raw in enumerate(compressed):
        row = {column: value % prime for column, value in raw.items() if value % prime}
        tag = {source: 1}
        # Reduce every universal pivot, not only the leading run.  The basis is
        # echelon (not reduced echelon), so a free leading column may precede
        # later pivot columns which still have to be cleared.
        for pivot in universal_pivots:
            factor = row.get(pivot, 0)
            if not factor:
                continue
            old = universal_basis[pivot]
            for column, value in old.items():
                new = (row.get(column, 0) - factor * value) % prime
                if new:
                    row[column] = new
                else:
                    row.pop(column, None)
        while row:
            pivot = min(row)
            pair = quotient_basis.get(pivot)
            if pair is None:
                inverse = pow(row[pivot], prime - 2, prime)
                row = {
                    column: value * inverse % prime
                    for column, value in row.items()
                    if value * inverse % prime
                }
                tag = {
                    index: value * inverse % prime
                    for index, value in tag.items()
                    if value * inverse % prime
                }
                quotient_basis[pivot] = (row, tag)
                quotient_pivots.append(source)
                break
            old, old_tag = pair
            factor = row[pivot]
            for column, value in old.items():
                new = (row.get(column, 0) - factor * value) % prime
                if new:
                    row[column] = new
                else:
                    row.pop(column, None)
            for index, value in old_tag.items():
                new = (tag.get(index, 0) - factor * value) % prime
                if new:
                    tag[index] = new
                else:
                    tag.pop(index, None)
        if not row:
            inverse = pow(tag[source], prime - 2, prime)
            relations[source] = {
                index: value * inverse % prime
                for index, value in tag.items()
                if value * inverse % prime
            }
    return quotient_pivots, relations


def crt_pair(first: int, p: int, second: int, q: int) -> int:
    return (first + p * ((second - first) * pow(p, q - 2, q) % q)) % (p * q)


def rational_reconstruct(value: int, modulus: int) -> Fraction | None:
    value %= modulus
    if value == 0:
        return Fraction(0)
    bound = math.isqrt(modulus // 2)
    old_r, r = modulus, value
    old_t, t = 0, 1
    while r > bound:
        quotient = old_r // r
        old_r, r = r, old_r - quotient * r
        old_t, t = t, old_t - quotient * t
    if not t or abs(t) > bound or math.gcd(r, t) != 1:
        return None
    if t < 0:
        r, t = -r, -t
    if (r - value * t) % modulus:
        return None
    return Fraction(r, t)


def modular_relation_probe(
    universal: list[dict[int, int]], compressed: list[dict[int, int]]
) -> None:
    p, q = 1_000_000_007, 1_000_000_009
    piv_p, rel_p = quotient_relations(universal, compressed, p)
    print(f"quotient_pivots_p={piv_p}")
    piv_q, rel_q = quotient_relations(universal, compressed, q)
    print(f"quotient_pivots_q={piv_q}")
    assert piv_p == piv_q and set(rel_p) == set(rel_q)
    modulus = p * q
    recovered: dict[int, dict[int, Fraction | None]] = {}
    failures = []
    for source in sorted(rel_p):
        recovered[source] = {}
        for index in sorted(set(rel_p[source]) | set(rel_q[source])):
            residue = crt_pair(rel_p[source].get(index, 0), p, rel_q[source].get(index, 0), q)
            value = rational_reconstruct(residue, modulus)
            recovered[source][index] = value
            if value is None:
                failures.append((source, index, residue))
    print(f"relation_count={len(recovered)} reconstruction_failures={len(failures)}")
    print("rational_relations=" + repr(recovered))
    if failures:
        print("failure_sample=" + repr(failures[:20]))


def csr_from_rows(rows: list[dict[int, int]], width: int) -> sparse.csr_matrix:
    rr: list[int] = []
    cc: list[int] = []
    vv: list[float] = []
    for i, row in enumerate(rows):
        if not row:
            continue
        scale = max(abs(value) for value in row.values())
        for column, value in row.items():
            rr.append(i)
            cc.append(column)
            vv.append(float(value) / float(scale))
    return sparse.coo_matrix((vv, (rr, cc)), shape=(len(rows), width)).tocsr()


def matrix_variables(records: list[dict]) -> tuple[cp.Variable, cp.Variable, list]:
    y3 = cp.Variable((6, 6), symmetric=True, name="Y3")
    y12 = cp.Variable((8, 8), symmetric=True, name="Y12")
    weights = []
    for record in records:
        i, j = map(int, record["direction_indices"])
        block = y3 if int(record["root_mask"]) == 3 else y12
        weights.append((1 if i == j else 2) * int(record["raw_divisor"]) * block[i, j])
    return y3, y12, weights


def main() -> None:
    print(f"memory_free_percent={memory_gate():.3f}")
    universal, compressed, records = build_rows()
    print("zero_compressed_rows=" + repr([i for i, row in enumerate(compressed) if not row]))
    if "--modular-relations" in sys.argv:
        modular_relation_probe(universal, compressed)
        return
    pivots, selected = modular_pivots(universal)
    width = 917
    free = [column for column in range(width) if column not in set(pivots)]
    print(f"universal_nonzero_rows={len(universal)} rank_mod_p={len(pivots)} free={free}")
    assert len(pivots) == 909 and len(free) == 8

    chosen = [universal[index] for index in selected]
    whole = csr_from_rows(chosen, width)
    b = whole[:, pivots].tocsc()
    f = whole[:, free].toarray()
    lu = splu(b)
    x = lu.solve(-f)
    null = np.zeros((width, 8))
    null[pivots, :] = x
    null[free, :] = np.eye(8)
    all_a = csr_from_rows(universal, width)
    residual = all_a @ null
    print(f"null_max_scaled_residual={np.max(np.abs(residual)):.3e} null_max={np.max(np.abs(null)):.3e}")

    c = csr_from_rows(compressed, width)
    quotient = np.asarray(c @ null)
    print(f"quotient_singular_values={np.linalg.svd(quotient, compute_uv=False)}")

    # Diagonal-only LP is an especially simple PSD test.
    diagonal_rows = [
        i for i, record in enumerate(records)
        if record["direction_indices"][0] == record["direction_indices"][1]
    ]
    diagonal = quotient[diagonal_rows, :].T.copy()
    for local, row_index in enumerate(diagonal_rows):
        diagonal[:, local] *= int(records[row_index]["raw_divisor"])
    eq = np.vstack([diagonal, np.ones((1, len(diagonal_rows)))])
    rhs = np.r_[np.zeros(8), 1.0]
    lp = linprog(
        np.zeros(len(diagonal_rows)), A_eq=eq, b_eq=rhs,
        bounds=[(0, None)] * len(diagonal_rows), method="highs",
    )
    print(f"diagonal_lp={lp.status}:{lp.message}")
    if lp.success:
        print("diagonal_weights=" + repr(lp.x.tolist()))
        print(f"diagonal_residual={np.max(np.abs(eq @ lp.x-rhs)):.3e}")

    y3, y12, weights = matrix_variables(records)
    equalities = []
    for coordinate in range(8):
        coefficients = np.asarray(quotient[:, coordinate], dtype=float)
        scale = max(
            abs(coefficients[row] * int(records[row]["raw_divisor"]))
            for row in range(57)
        )
        equalities.append(sum(coefficients[row] / scale * weights[row] for row in range(57)) == 0)
    t = cp.Variable(name="common_pd_margin")
    constraints = [*equalities, cp.trace(y3) + cp.trace(y12) == 1, y3 - t*np.eye(6) >> 0, y12 - t*np.eye(8) >> 0]
    problem = cp.Problem(cp.Maximize(t), constraints)
    problem.solve(solver="CLARABEL", verbose=False)
    print(f"sdp_status={problem.status} margin={t.value}")
    print("Y3=" + repr(np.asarray(y3.value).tolist()))
    print("Y12=" + repr(np.asarray(y12.value).tolist()))


if __name__ == "__main__":
    main()
