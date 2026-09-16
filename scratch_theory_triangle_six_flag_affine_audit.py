"""Independent coloured-graph/moment audit of all 99 triangle-rooted flags.

No producer or encoding module is imported.  Isomorphism fixes the three
roots and permutes only the three free vertices.  Triangle counts are solved
from edge-incidence balances and induced counts from triangular moment rows.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter
from fractions import Fraction
from math import comb, factorial
from pathlib import Path


CERT = Path("scratch_theory_triangle_six_flag_affine.json")
PRIOR = Path("scratch_theory_order9_rooted_flag_gram.json")
OUT = Path("scratch_theory_triangle_six_flag_affine_audit.json")
PAIRS = ((0, 1), (0, 2), (1, 2))
PERMUTATIONS = tuple(itertools.permutations(range(3)))
EDGE_SUBSETS = tuple(frozenset(pair for bit, pair in enumerate(PAIRS) if mask >> bit & 1)
                     for mask in range(8))


def normalize(colors: tuple[int, ...], edges: frozenset[tuple[int, int]]) -> tuple:
    representations = []
    for order in PERMUTATIONS:
        image_colors = tuple(colors[old] for old in order)
        image_edges = tuple(int(tuple(sorted((order[a], order[b]))) in edges)
                            for a, b in PAIRS)
        representations.append((image_colors, image_edges))
    return min(representations)


def automorphisms(colors: tuple[int, ...], edges: frozenset[tuple[int, int]]) -> int:
    return sum(tuple(colors[old] for old in order) == colors and
               all((tuple(sorted((order[a], order[b]))) in edges) == ((a, b) in edges)
                   for a, b in PAIRS) for order in PERMUTATIONS)


def rooted_graph(colors: tuple[int, ...], edges: frozenset[tuple[int, int]]) -> set[frozenset[int]]:
    return ({frozenset(pair) for pair in PAIRS}
            | {frozenset((color, index + 3)) for index, color in enumerate(colors) if color < 3}
            | {frozenset((a + 3, b + 3)) for a, b in edges})


def local_caps(edges: set[frozenset[int]]) -> bool:
    neighborhoods = [{other for other in range(6) if frozenset((v, other)) in edges}
                     for v in range(6)]
    return all(len(neighborhoods[a] & neighborhoods[b]) <=
               (1 if frozenset((a, b)) in edges else 2)
               for a, b in itertools.combinations(range(6), 2))


def decode(mask: int) -> tuple[tuple[int, ...], frozenset[tuple[int, int]]]:
    edges = {frozenset(pair) for bit, pair in
             enumerate(itertools.combinations(range(6), 2)) if mask >> bit & 1}
    assert all(frozenset(pair) in edges for pair in PAIRS)
    colors = []
    for free in range(3, 6):
        roots = [root for root in range(3) if frozenset((root, free)) in edges]
        assert len(roots) <= 1
        colors.append(roots[0] if roots else 3)
    free_edges = frozenset((a, b) for a, b in PAIRS
                           if frozenset((a + 3, b + 3)) in edges)
    return tuple(colors), free_edges


def solve_linear(matrix: list[list[int]], rhs: list[tuple[int, int]]) -> list[tuple[Fraction, Fraction]]:
    size = len(matrix)
    assert all(len(row) == size for row in matrix)
    augmented = [list(map(Fraction, row)) + list(map(Fraction, value))
                 for row, value in zip(matrix, rhs)]
    for column in range(size):
        pivot = next(row for row in range(column, size) if augmented[row][column])
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        divisor = augmented[column][column]
        augmented[column] = [value / divisor for value in augmented[column]]
        for row in range(size):
            if row == column:
                continue
            multiplier = augmented[row][column]
            augmented[row] = [a - multiplier * b for a, b in zip(augmented[row], augmented[column])]
    return [tuple(row[-2:]) for row in augmented]


def triangle_balances(m: int) -> tuple[dict, tuple, tuple]:
    sizes = (m, m, m, m * (m - 2) // 2)
    degree = ((1, 1, 1, m - 2),) * 3 + ((2, 2, 2, m - 4),)
    all_patterns = tuple(itertools.combinations_with_replacement(range(4), 3))
    allowed = tuple(pattern for pattern in all_patterns
                    if all(pattern.count(color) <= 1 for color in range(3)))
    assert len(all_patterns) == 20 and len(allowed) == 8
    equations, right = [], []
    for a, b in itertools.combinations_with_replacement(range(4), 2):
        if a == b and a < 3:
            continue  # These matching edges have the root as their triangle mate.
        row = [sum(tuple(sorted(pair)) == (a, b) for pair in itertools.combinations(pattern, 2))
               for pattern in allowed]
        edge_count = sizes[a] * degree[a][b] // (2 if a == b else 1)
        equations.append(row)
        right.append((edge_count, 0))
    equations.append([int(pattern == (0, 1, 2)) for pattern in allowed])
    right.append((0, 1))
    solution = solve_linear(equations, right)
    counts = {pattern: (Fraction(0), Fraction(0)) for pattern in all_patterns}
    counts.update(zip(allowed, solution))
    for row, target in zip(equations, right):
        assert tuple(sum(coefficient * value[j] for coefficient, value in zip(row, solution))
                     for j in range(2)) == target
    return counts, sizes, degree


def independent_catalogue(m: int) -> tuple[dict, set]:
    triangles, sizes, degree = triangle_balances(m)
    admitted, rejected = {}, set()
    for colors in itertools.product(range(4), repeat=3):
        moments = {}
        for edge_set in EDGE_SUBSETS:
            if len(edge_set) == 3:
                factor = 1
                for repeated in Counter(colors).values():
                    factor *= factorial(repeated)
                moments[edge_set] = tuple(factor * x for x in triangles[tuple(sorted(colors))])
            elif len(edge_set) == 2:
                centre = next(iter(set.intersection(*(set(edge) for edge in edge_set))))
                leaf_a, leaf_b = (index for index in range(3) if index != centre)
                a, b, c = colors[centre], colors[leaf_a], colors[leaf_b]
                moments[edge_set] = (Fraction(sizes[a] * degree[a][b]
                                             * (degree[a][c] - int(b == c))), Fraction(0))
            elif len(edge_set) == 1:
                a_index, b_index = next(iter(edge_set))
                c_index = next(index for index in range(3) if index not in (a_index, b_index))
                a, b, c = colors[a_index], colors[b_index], colors[c_index]
                moments[edge_set] = (Fraction(sizes[a] * degree[a][b]
                                             * (sizes[c] - int(c == a) - int(c == b))), Fraction(0))
            else:
                number = 1
                for color, multiplicity in Counter(colors).items():
                    for offset in range(multiplicity):
                        number *= sizes[color] - offset
                moments[edge_set] = Fraction(number), Fraction(0)
        # Back-substitution of F(S)=sum_{H containing S} z(H); no alternating formula.
        ordered_induced = {}
        for required in sorted(EDGE_SUBSETS, key=len, reverse=True):
            ordered_induced[required] = tuple(
                moments[required][component] - sum(
                    value[component] for present, value in ordered_induced.items()
                    if required < present)
                for component in range(2))
        for required, moment in moments.items():
            assert tuple(sum(value[component] for present, value in ordered_induced.items()
                             if required <= present) for component in range(2)) == moment
        for edges, values in ordered_induced.items():
            symmetry = automorphisms(colors, edges)
            values = tuple(value / symmetry for value in values)
            key = normalize(colors, edges)
            if not local_caps(rooted_graph(colors, edges)):
                assert values == (0, 0)
                rejected.add(key)
            else:
                if key in admitted:
                    assert admitted[key] == values
                admitted[key] = values
    assert len(admitted) == 99 and len(rejected) == 21
    assert not set(admitted) & rejected
    return admitted, rejected


def rook_calibration(catalogue: dict) -> int:
    points = tuple(itertools.product(range(3), repeat=2))
    adjacency = [{w for w in range(9) if w != v and
                  any(points[v][axis] == points[w][axis] for axis in (0, 1))}
                 for v in range(9)]
    checked = 0
    for root in itertools.permutations(range(9), 3):
        if not all(b in adjacency[a] for a, b in itertools.combinations(root, 2)):
            continue
        actual = Counter()
        t = 0
        outside = sorted(set(range(9)) - set(root))
        for selected in itertools.combinations(outside, 3):
            colors = tuple(next((index for index, r in enumerate(root)
                                 if v in adjacency[r]), 3) for v in selected)
            edges = frozenset((a, b) for a, b in PAIRS if selected[b] in adjacency[selected[a]])
            actual[normalize(colors, edges)] += 1
            t += int(sorted(colors) == [0, 1, 2] and len(edges) == 3)
        assert t == 2 and sum(actual.values()) == comb(6, 3)
        assert all(actual[key] == a + t * b for key, (a, b) in catalogue.items())
        checked += 1
    return checked


def main() -> None:
    certificate = json.loads(CERT.read_text(encoding="utf-8"))
    target, rejected = independent_catalogue(12)
    emitted = {}
    for row in certificate["flags"]:
        colors, edges = decode(int(row["mask"]))
        key = normalize(colors, edges)
        supplied_edges = EDGE_SUBSETS[int(row["free_edge_bits"])]
        assert key == normalize(tuple(row["colors"]), supplied_edges)
        assert key not in emitted
        emitted[key] = (int(row["constant"]), int(row["t_coefficient"]))
    assert emitted == target
    assert all(value.denominator == 1 for values in target.values() for value in values)
    assert sum(a for a, b in target.values()) == comb(96, 3) == 142880
    assert sum(b for a, b in target.values()) == 0
    assert sum(b != 0 for a, b in target.values()) == 54
    assert sum(a > 0 for a, b in target.values()) == 98
    assert all(min(a, a + 12 * b) >= 0 for a, b in target.values())
    prism_key = normalize((0, 1, 2), EDGE_SUBSETS[7])
    assert target[prism_key] == (0, 1)
    for mask in (24699, 24939, 25147, 25507, 27179, 27299):
        assert target[normalize(*decode(mask))] == (12, 0)
    prior = json.loads(PRIOR.read_text(encoding="utf-8"))
    old_keys = {normalize(*decode(int(row["triangle_rooted_flag_mask"])))
                for row in prior["complete_visible_support_closure_test"]["diagonal_rows"]}
    assert len(old_keys) == 74 and old_keys <= target.keys()
    rook, _ = independent_catalogue(2)
    roots = rook_calibration(rook)
    assert roots == 36
    assert certificate["universal_Gram_rank_upper_bound"] == 2
    assert certificate["prism_free_Gram_rank"] == 1
    assert certificate["higher_order_affine_completion_obstruction_ruled_out"] is False
    output = {
        "status": "INDEPENDENT_TRIANGLE_SIX_FLAG_AFFINE_AUDIT_PASS",
        "producer_or_encoding_imported": False,
        "certificate_sha256": hashlib.sha256(CERT.read_bytes()).hexdigest(),
        "prior_74_archive_sha256": hashlib.sha256(PRIOR.read_bytes()).hexdigest(),
        "labelled_templates_checked": 512,
        "rooted_isomorphism_types": len(target) + len(rejected),
        "admissible_affine_coefficients_checked": len(target),
        "identically_zero_rejected_types": len(rejected),
        "prior_74_types_independently_identified": len(old_keys),
        "coloured_triangle_linear_equations_per_parameter": 8,
        "moment_rows_per_ordered_colour_tuple": 8,
        "rook9_ordered_root_calibrations": roots,
        "constant_flags": 45, "nonconstant_flags": 54,
        "positive_at_t_zero": 98,
        "higher_order_completion_obstruction_ruled_out": False,
        "frozen_order8_classes_regenerated": False,
    }
    OUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
