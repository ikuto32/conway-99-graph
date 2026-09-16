"""All triangle-rooted six-vertex flag counts are affine in prism count.

Only 4^3 * 8 tiny rooted templates are considered, never an H8/H9 census.
Exact inclusion-exclusion derives induced counts from equitable valencies.
"""

from fractions import Fraction as F
import itertools as it
import json
from pathlib import Path

import scratch_theory_order9_cross_x_closure as encoding


FREE_PAIRS = ((0, 1), (0, 2), (1, 2))


def triangle_count(colors, m):
    """Unordered colored triangles, as constant + coefficient * t."""
    counts = [colors.count(c) for c in range(4)]
    if counts == [1, 1, 1, 0]:
        return F(0), F(1)
    if counts[3] == 1 and sum(x == 1 for x in counts[:3]) == 2:
        return F(m), F(-1)
    if counts[3] == 2 and sum(counts[:3]) == 1:
        return F(m * (m - 4), 2), F(1)
    if counts[3] == 3:
        return F(m * (m - 4) * (m - 8), 12), F(-1)
    return F(0), F(0)


def containing_count(colors, bits, m):
    """Ordered distinct triples containing the indicated edge set."""
    sizes = (m, m, m, m * (m - 2) // 2)
    degrees = ((1, 1, 1, m - 2),) * 3 + ((2, 2, 2, m - 4),)
    selected = [pair for bit, pair in enumerate(FREE_PAIRS) if bits >> bit & 1]
    if not selected:
        answer = 1
        used = [0] * 4
        for c in colors:
            answer *= sizes[c] - used[c]
            used[c] += 1
        return F(answer), F(0)
    if len(selected) == 1:
        i, j = selected[0]
        k = next(v for v in range(3) if v not in (i, j))
        a, b, c = colors[i], colors[j], colors[k]
        return F(sizes[a] * degrees[a][b] *
                 (sizes[c] - int(c == a) - int(c == b))), F(0)
    if len(selected) == 2:
        center = next(iter(set(selected[0]) & set(selected[1])))
        left, right = [v for v in range(3) if v != center]
        a, b, c = colors[center], colors[left], colors[right]
        return F(sizes[a] * degrees[a][b] *
                 (degrees[a][c] - int(b == c))), F(0)
    value = triangle_count(colors, m)
    multiplier = 1
    for color in range(4):
        for j in range(1, colors.count(color) + 1):
            multiplier *= j
    return tuple(multiplier * x for x in value)


def induced_count(colors, bits, m):
    answer = [F(0), F(0)]
    for superset in range(8):
        if superset & bits != bits:
            continue
        sign = (-1) ** ((superset ^ bits).bit_count())
        value = containing_count(colors, superset, m)
        answer = [a + sign * v for a, v in zip(answer, value)]
    edges = {pair for bit, pair in enumerate(FREE_PAIRS) if bits >> bit & 1}
    automorphisms = sum(
        all(colors[i] == colors[p[i]] for i in range(3)) and
        {tuple(sorted((p[i], p[j]))) for i, j in edges} == edges
        for p in it.permutations(range(3)))
    return tuple(x / automorphisms for x in answer)


def root_mask(colors, bits):
    edges = {(0, 1), (0, 2), (1, 2)}
    edges.update((c, i + 3) for i, c in enumerate(colors) if c < 3)
    edges.update((i + 3, j + 3) for bit, (i, j) in enumerate(FREE_PAIRS)
                 if bits >> bit & 1)
    raw = sum(1 << encoding.positions(6)[pair] for pair in edges)
    return raw, encoding.canonical(raw, 6, (0, 1, 2))


def catalogue(m):
    result = {}
    rejected = set()
    for colors in it.product(range(4), repeat=3):
        for bits in range(8):
            raw, mask = root_mask(colors, bits)
            value = induced_count(colors, bits, m)
            if not encoding.pair_upper(raw, 6):
                assert value == (0, 0)
                rejected.add(mask)
                continue
            if mask in result:
                assert result[mask]["affine"] == value
            else:
                result[mask] = {"colors": colors, "free_edge_bits": bits,
                                "affine": value}
    assert len(result) == 99 and len(rejected) == 21
    return result


def main():
    target = catalogue(12)
    assert all(all(x.denominator == 1 for x in r["affine"]) for r in target.values())
    assert sum(r["affine"][0] for r in target.values()) == 142880
    assert sum(r["affine"][1] for r in target.values()) == 0
    assert all(min(a, a + 12 * b) >= 0 for a, b in
               (r["affine"] for r in target.values()))
    for mask in (24699, 24939, 25147, 25507, 27179, 27299):
        assert target[mask]["affine"] == (12, 0)
    prior = json.loads(Path("scratch_theory_order9_rooted_flag_gram.json").read_text())
    prior_flags = {row["triangle_rooted_flag_mask"]
                   for row in prior["complete_visible_support_closure_test"]["diagonal_rows"]}
    assert len(prior_flags) == 74 and prior_flags <= target.keys()

    rook = catalogue(2)
    points = tuple(it.product(range(3), repeat=2))
    adj = [{j for j, w in enumerate(points) if v != w and
            (v[0] == w[0] or v[1] == w[1])} for v in points]
    checked_roots = 0
    for roots in it.permutations(range(9), 3):
        if not all(b in adj[a] for a, b in it.combinations(roots, 2)):
            continue
        counts = dict.fromkeys(target, 0)
        for free in it.combinations(sorted(set(range(9)) - set(roots)), 3):
            labels = roots + free
            raw = sum(1 << bit for bit, (i, j) in enumerate(encoding.edges(6))
                      if labels[j] in adj[labels[i]])
            mask = encoding.canonical(raw, 6, (0, 1, 2))
            counts[mask] += 1
        assert all(counts[mask] == a + 2 * b
                   for mask, record in rook.items() for a, b in [record["affine"]])
        checked_roots += 1
    assert checked_roots == 36

    result = {
        "status": "TRIANGLE_SIX_FLAG_AFFINE_FINITE_CHECKS_PASS",
        "labelled_templates": 512, "rooted_types": 120,
        "locally_admissible_types": 99, "pair_upper_impossible_types": 21,
        "prior_visible_subset": 74,
        "outside_cell_sizes": [12, 12, 12, 60],
        "outside_quotient": [[1, 1, 1, 10]] * 3 + [[2, 2, 2, 8]],
        "parameter": "t = number of prism-mate triangles of the fixed root triangle",
        "parameter_range": [0, 12],
        "flags": [{"mask": mask, "colors": record["colors"],
                   "free_edge_bits": record["free_edge_bits"],
                   "constant": int(record["affine"][0]),
                   "t_coefficient": int(record["affine"][1])}
                  for mask, record in sorted(target.items())],
        "nonconstant_flags": sum(r["affine"][1] != 0 for r in target.values()),
        "positive_flags_at_t_zero": sum(r["affine"][0] > 0 for r in target.values()),
        "full_raw_Gram": "1386 aa^T + 12P(ab^T+ba^T) + U bb^T",
        "U": "6 sum over unordered triangles of t(T)^2",
        "universal_Gram_rank_upper_bound": 2,
        "prism_free_Gram_rank": 1,
        "rook9_ordered_root_calibrations": checked_roots,
        "E0_lower_bound": None,
        "higher_order_affine_completion_obstruction_ruled_out": False,
        "frozen_order8_classes_regenerated": False,
    }
    Path("scratch_theory_triangle_six_flag_affine.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "flags"}, indent=2))


if __name__ == "__main__":
    main()
