"""Exact arithmetic for a uniform compression bound, with no layer search.

The graph-to-matrix proof is in the companion note.  This checks the fixed
incidences, projection algebra, integer rounding and five sharp row controls.
It does not assert that any compression or graph exists.
"""

from fractions import Fraction as F
from itertools import combinations
import hashlib
import json
from pathlib import Path

OUTPUT = Path("scratch_theory_uniform_compression_rounding.json")
FIBRES = list(combinations(range(7), 2))
LABELS = [(2 * a + s, 2 * b + t) for a, b in FIBRES
          for s in range(2) for t in range(2)]


def transpose(a):
    return list(map(list, zip(*a)))


def product(a, b):
    return [[sum(x * y for x, y in zip(row, col))
             for col in zip(*b)] for row in a]


def square_floor(count, total):
    q, r = divmod(total, count)
    return count * q * q + r * (2 * q + 1)


def row_control(delta):
    data = {
        0: ([0] * 5, [0] * 5, []),
        1: ([1, 1, 0, 0, 0], [0, 0, 1, 1, 0], [(0, 1), (2, 3)]),
        2: ([0, 1, 1, 1, 1], [1, 1, 1, 1, 0], [(0, 1), (1, 2), (2, 3), (3, 4)]),
        3: ([2, 1, 1, 1, 1], [2, 1, 1, 1, 1],
            [(0, 1), (0, 2), (0, 3), (0, 4), (1, 2), (3, 4)]),
        4: ([2, 2, 2, 1, 1], [2, 1, 1, 2, 2],
            [p for p in combinations(range(5), 2) if p not in {(1, 2), (3, 4)}]),
    }
    a, b, edges = data[delta]
    z = []
    for i, j in FIBRES:
        if (i, j) == (0, 1):
            value = 2 * delta
        elif i == 0:
            value = -a[j - 2]
        elif i == 1:
            value = -b[j - 2]
        else:
            value = int((i - 2, j - 2) in edges)
        z.append(value)
    c = [(8 if p == (0, 1) else 0 if set(p) & {0, 1} else 4) - value
         for p, value in zip(FIBRES, z)]
    return z, c


def main():
    p = [[int(x // 4 == f) for f in range(21)] for x in range(84)]
    n = [[int(a in label) for label in LABELS] for a in range(14)]
    ell = [[int(a in f) for a in range(7)] for f in FIBRES]
    pt, lt = transpose(p), transpose(ell)
    assert product(pt, p) == [[4 * int(i == j) for j in range(21)] for i in range(21)]
    nn = product(n, transpose(n))
    assert nn == [[12 if i == j else 0 if i // 2 == j // 2 else 1
                   for j in range(14)] for i in range(14)]
    np = product(n, p)
    assert np == [[2 * int(a // 2 in f) for f in FIBRES] for a in range(14)]
    ll = product(ell, lt)
    assert product(transpose(np), np) == [[8 * value for value in row] for row in ll]
    assert product(lt, ell) == [[5 * int(i == j) + 1 for j in range(7)] for i in range(7)]

    inverse = [[F(int(i == j), 5) - F(1, 60) for j in range(7)] for i in range(7)]
    h = product(product(ell, inverse), lt)
    cycle = [[int(i == j) - h[i][j] for j in range(21)] for i in range(21)]
    assert product(cycle, cycle) == cycle
    assert product(cycle, ell) == [[0] * 7 for _ in range(21)]
    assert sum(cycle[i][i] for i in range(21)) == 14
    fixed = [[F(8, 3) - 8 * h[i][j] for j in range(21)] for i in range(21)]
    assert product(fixed, ell) == [[16 - 8 * v for v in row] for row in ell]
    assert product(fixed, cycle) == [[0] * 21 for _ in range(21)]
    assert sum(v * v for row in fixed for v in row) == 2688

    g = [4 * e * e + square_floor(10, 16 - 4 * e) + square_floor(10, 32 + 2 * e)
         for e in range(5)]
    assert g == [132, 138, 156, 186, 224]
    assert [g[i + 1] - g[i] for i in range(4)] == [6, 18, 30, 38]
    controls = []
    for delta in range(5):
        z, c = row_control(delta)
        assert product([z], ell) == [[0] * 7]
        assert product([c], ell) == [[8, 8, 16, 16, 16, 16, 16]]
        assert sum(c) == 48 and c[0] == 2 * (4 - delta)
        assert all(0 <= value <= 16 for value in c)
        assert sum(value * value for value in c) == g[4 - delta]
        controls.append({"delta": delta, "e": 4 - delta, "Z_row": z,
                         "C_row": c, "row_square": g[4 - delta]})

    # A 21-step integer dynamic program over five fibre edge counts only.
    # This checks the closed-form convex bound, not any adjacency/compression.
    best = {0: 0}
    for _ in range(21):
        nxt = {}
        for total, value in best.items():
            for e in range(5):
                target = total + e
                nxt[target] = min(nxt.get(target, 10**9), value + g[e])
        best = nxt
    rows = []
    for e0 in range(85):
        q, r = divmod(e0, 21)
        bound = 21 * g[q] if q == 4 else (21 - r) * g[q] + r * g[q + 1]
        assert best[e0] == bound
        formula = (2772 + 6 * e0 if e0 <= 21 else
                   2520 + 18 * e0 if e0 <= 42 else
                   2016 + 30 * e0 if e0 <= 63 else 1512 + 38 * e0)
        assert bound == formula
        cbar = [[fixed[i][j] + F(e0, 7) * cycle[i][j] for j in range(21)] for i in range(21)]
        assert sum(cbar[i][i] for i in range(21)) == 2 * e0
        assert all(sum(row) == 48 for row in cbar)
        assert sum(v * v for row in cbar for v in row) == 2688 + F(2 * e0 * e0, 7)
        covariance = bound - 2688 - F(2 * e0 * e0, 7)
        assert covariance >= 0
        spectral_upper = 5376 - 8 * e0
        assert bound <= spectral_upper
        rows.append({"E0": e0, "integer_trace_square_lower": bound,
                     "spectral_trace_square_upper": spectral_upper,
                     "covariance_lower": str(covariance)})
    result = {
        "status": "UNIFORM_COMPRESSION_ROUNDING_EXACT_ARITHMETIC_PASS",
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest().upper(),
        "checked": ["fixed incidences", "cycle projection", "five sharp row controls",
                    "integer convex bound at all 85 E0 values", "spectral interval overlap"],
        "row_bound": g, "row_controls": controls, "E0_bounds": rows,
        "at_E0_zero": {"trace_square_lower": 2772, "Cbar_trace_square": 2688,
                       "mandatory_covariance": 84},
        "scope": "Necessary inequalities only. Row controls are not a jointly symmetric C. No graph, global C feasibility, positive E0 lower bound, SAT result, or layer exclusion is claimed.",
        "graph_search_used": False, "external_order8_classes_regenerated": False,
        "submission_txt_written": False,
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("status", "at_E0_zero", "scope")}, sort_keys=True))


if __name__ == "__main__":
    main()
