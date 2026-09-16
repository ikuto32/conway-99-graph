"""Clean-room consequences of one rooted layer with E0(r)=0.

The only imported premise is the independently verified Wave65 summary.  All
signed-edge, fibre, block-shape, Fourier, and support-control enumerations in
this file are rebuilt directly.  The output is a necessary-condition audit,
not a construction or a nonexistence proof for srg(99,14,1,2).
"""

from __future__ import annotations

from collections import Counter
import hashlib
import itertools
import json
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parent
WAVE65_VERIFY = (
    ROOT
    / "external_conway99_research"
    / "verification"
    / "wave65-rooted-hypergraph-algebra"
    / "independent-results.json"
)
OUTPUT_JSON = ROOT / "scratch_theory_e0_zero_hypergraph.json"
OUTPUT_MD = ROOT / "scratch_theory_e0_zero_hypergraph.md"
POINT_CONTROL = ROOT / "scratch_theory_e0_zero_hypergraph_point_control.json"
EXPECTED_WAVE65_SHA256 = (
    "076293e960e704799ad1eb68b43aeff7892d83d240c9b3471789aadc9413349d"
)
EXPECTED_POINT_CONTROL_SHA256 = (
    "c669c983b65bdbf8f5445b99d3847ddef8fc91deab990343ece53afd214f1ca2"
)

SUPPORTS = tuple(itertools.combinations(range(7), 2))
SUPPORT_INDEX = {edge: index for index, edge in enumerate(SUPPORTS)}
POINTS = tuple(
    (g, h, a, b)
    for g, h in SUPPORTS
    for a, b in itertools.product((0, 1), repeat=2)
)
POINT_INDEX = {point: index for index, point in enumerate(POINTS)}
FLIPS = ((1, 0), (0, 1), (1, 1))
CHARACTERS = ((0, 0), (1, 0), (0, 1), (1, 1))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def atomic_write(path: Path, text: str) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def support(point: tuple[int, int, int, int]) -> tuple[int, int]:
    return point[:2]


def exact_symbols(point: tuple[int, int, int, int]) -> frozenset[tuple[int, int]]:
    g, h, a, b = point
    return frozenset(((g, a), (h, b)))


def sign_at_group(point: tuple[int, int, int, int], group: int) -> int:
    g, h, a, b = point
    require(group in (g, h), "group absent from signed support")
    return a if group == g else b


def local_opposite_edge_weight(
    left: tuple[int, int, int, int], right: tuple[int, int, int, int]
) -> int:
    """Number of root-neighbour mate edges opposite the outer pair.

    This is the local entry of the global triangle-mate/opposite-edge product
    R_tm J.  A common support group contributes exactly when the two outer
    points choose opposite members of that root-neighbour mate pair.
    """

    common_groups = set(support(left)) & set(support(right))
    return sum(sign_at_group(left, group) != sign_at_group(right, group) for group in common_groups)


def flip(point: tuple[int, int, int, int], delta: tuple[int, int]) -> tuple[int, int, int, int]:
    g, h, a, b = point
    return (g, h, a ^ delta[0], b ^ delta[1])


def relation_census() -> dict[str, object]:
    pairs: Counter[tuple[int, str]] = Counter()
    opposite_weight_types: Counter[tuple[int, str, int]] = Counter()
    for left, right in itertools.combinations(POINTS, 2):
        exact_overlap = len(exact_symbols(left) & exact_symbols(right))
        if support(left) == support(right):
            fibre_relation = "same_fibre"
        elif set(support(left)) & set(support(right)):
            fibre_relation = "overlapping_supports"
        else:
            fibre_relation = "disjoint_supports"
        pairs[(exact_overlap, fibre_relation)] += 1
        opposite_weight_types[(exact_overlap, fibre_relation, local_opposite_edge_weight(left, right))] += 1
    expected = {
        (1, "same_fibre"): 84,
        (0, "same_fibre"): 42,
        (1, "overlapping_supports"): 840,
        (0, "overlapping_supports"): 840,
        (0, "disjoint_supports"): 1680,
    }
    require(pairs == expected, "signed-edge relation census")
    require(
        opposite_weight_types
        == {
            (1, "same_fibre", 1): 84,
            (0, "same_fibre", 2): 42,
            (1, "overlapping_supports", 0): 840,
            (0, "overlapping_supports", 1): 840,
            (0, "disjoint_supports", 0): 1680,
        },
        "local opposite-edge weight table",
    )
    return {
        "all_unordered_point_pairs": sum(pairs.values()),
        "same_fibre_side_pairs_forbidden_from_T": pairs[(1, "same_fibre")],
        "same_fibre_diagonal_pairs_forbidden_from_D": pairs[(0, "same_fibre")],
        "remaining_T_candidate_positions": pairs[(1, "overlapping_supports")],
        "remaining_D_candidate_positions": (
            pairs[(0, "overlapping_supports")] + pairs[(0, "disjoint_supports")]
        ),
        "full_relation_histogram": [
            {
                "exact_symbol_overlap": exact_overlap,
                "support_relation": relation,
                "pairs": count,
            }
            for (exact_overlap, relation), count in sorted(pairs.items())
        ],
        "selected_edge_counts_for_E0_zero": {
            "T_overlapping_support": 84,
            "D_overlapping_support": 84,
            "D_disjoint_support": 336,
        },
        "triangle_mate_opposite_edge_weight_table": [
            {
                "exact_symbol_overlap": exact_overlap,
                "support_relation": relation,
                "weight": weight,
                "pairs": count,
            }
            for (exact_overlap, relation, weight), count in sorted(opposite_weight_types.items())
        ],
    }


def partitions(total: int, maximum: int | None = None) -> tuple[tuple[int, ...], ...]:
    if total == 0:
        return ((),)
    if maximum is None or maximum > total:
        maximum = total
    rows = []
    for first in range(maximum, 0, -1):
        rows.extend((first,) + tail for tail in partitions(total - first, first))
    return tuple(rows)


def forced_fibre_and_opposite_factor() -> dict[str, object]:
    """Auditable arithmetic forced by E0=0, including the global RJ bridge."""

    point_count = len(POINTS)
    fibre_count = len(SUPPORTS)
    require((point_count, fibre_count) == (84, 21), "signed fibre dimensions")

    # Each outer point has one D-neighbour through the mate of each of its two
    # support labels.  The SRG mu row supplies uniqueness: the original support
    # label is one common neighbour of x and its mate, leaving exactly one
    # outer common neighbour.  E0=0 prevents that neighbour from staying in
    # x's fibre.  Double counting gives two overlapping D incidences per point,
    # twelve per root group, and 84 such D edges globally.
    overlapping_D_oriented = point_count * 2
    overlapping_D_edges = overlapping_D_oriented // 2
    total_D_edges = point_count * 10 // 2
    disjoint_D_edges = total_D_edges - overlapping_D_edges
    require((overlapping_D_edges, total_D_edges, disjoint_D_edges) == (84, 420, 336), "D split")

    # Every support fibre contains four five-block points.  Since no selected
    # block repeats a fibre, it occurs in twenty distinct blocks.  Around one
    # of the seven root groups, 24 points create 120 block incidences.  The 12
    # overlapping D edges coloured by that group are precisely the blocks
    # containing two incident support fibres.
    fibre_block_degree = 4 * 5
    group_double_blocks = 24 // 2
    group_single_blocks = 24 * 5 - 2 * group_double_blocks
    group_zero_blocks = 140 - group_single_blocks - group_double_blocks
    require(
        (fibre_block_degree, group_zero_blocks, group_single_blocks, group_double_blocks)
        == (20, 32, 96, 12),
        "fibre/group block occupancy",
    )

    # For each root group g, T_g is the union of two six-edge matchings within
    # its two sign classes, whereas U_g is a twelve-edge matching between the
    # classes.  Alternation forces every cycle length in T_g+U_g to be a
    # multiple of four.  The possible signatures are four times partitions of
    # six, because the graph has 24 vertices.
    cycle_signatures = tuple(tuple(4 * part for part in row) for row in partitions(6))
    require(len(cycle_signatures) == 11, "local alternating cycle signatures")
    require(all(sum(row) == 24 and all(length % 4 == 0 for length in row) for row in cycle_signatures), "cycle lengths")

    return {
        "global_incidence_bridge": {
            "notation": (
                "C is unsigned vertex-edge incidence, R_tm marks the unique triangle mate of each edge, "
                "and J_e is the opposite-edge graph; R_tm is not the 140-block graph R"
            ),
            "entrywise_identity": "C*J_e=A*C-C-2*R_tm",
            "auxiliary_products": ["C*R_tm^T=A", "R_tm*R_tm^T=7I"],
            "degree_identity": "C*J_e*R_tm^T=2*(J_99-I-A)",
            "interpretation": (
                "row r of R_tm*J_e is a weighted graph on the 84 outer points, with weighted degree 2"
            ),
        },
        "opposite_factor_U": {
            "definition": "U=D restricted to distinct fibres whose group supports overlap",
            "is_the_Wave65_T": False,
            "T_edge_rule": "same exact root-neighbour label (equal sign at the shared group, Q=1)",
            "U_edge_rule": "mate root-neighbour labels (opposite sign at the shared group, Q=0)",
            "T_intersection_U_edges": 0,
            "degree": 2,
            "edges": overlapping_D_edges,
            "binary_reason": (
                "E0=0 deletes weight-one same-fibre sides and weight-two same-fibre diagonals; "
                "every surviving R_tm*J_e edge has weight one"
            ),
            "D_complement_degree": 8,
            "D_complement_edges": disjoint_D_edges,
        },
        "forced_block_occupancies": {
            "each_of_21_support_fibres": {"points": 4, "blocks_per_point": 5, "distinct_blocks": 20},
            "each_of_42_oriented_support_ports": {
                "overlap_blocks": 4,
                "derivation": (
                    "sum the four signed point/group U-degree-one equations in one support fibre"
                ),
            },
            "each_of_7_root_groups": {
                "outer_points_using_group": 24,
                "blocks_with_0_incident_supports": group_zero_blocks,
                "blocks_with_1_incident_support": group_single_blocks,
                "blocks_with_2_incident_supports": group_double_blocks,
            },
        },
        "seven_local_alternating_factors": {
            "T_g": "two perfect matchings of size 6, one inside each sign class",
            "U_g": "one perfect matching of size 12 between the two sign classes",
            "union": "a 2-factor on 24 points whose cycles alternate T_g,U_g",
            "cycle_lengths_divisible_by": 4,
            "possible_cycle_signatures": [list(row) for row in cycle_signatures],
            "real_rank_per_group": "rank(T_g+U_g)=24-2*c_g, where c_g is its number of cycles",
            "determinant_per_group": 0,
        },
        "shape_moments_of_U_inside_D": {
            "U_edges_per_D_block": {"3K2": 0, "P3+K2": 1, "P4": 2, "C3": 3},
            "edge_equation": "n_P3K2+2*n_P4+3*n_C3=84",
            "trace_U_squared": 168,
            "trace_U_cubed": "6*n_C3",
            "trace_U_squared_D": "2*n_P4+6*n_C3",
            "trace_U_squared_times_D_minus_U": "2*n_P4",
            "U_triangle_components": "n_C3",
        },
    }


def support_shape(points: tuple[tuple[int, int, int, int], ...]) -> str:
    supports = tuple(support(point) for point in points)
    if len(set(supports)) < len(supports):
        return "repeated_support"
    degrees = tuple(sorted(Counter(group for edge in supports for group in edge).values(), reverse=True))
    names = {
        (1, 1, 1, 1, 1, 1): "3K2",
        (2, 1, 1, 1, 1): "P3+K2",
        (2, 2, 1, 1): "P4",
        (2, 2, 2): "C3",
        (3, 1, 1, 1): "K1,3",
    }
    require(degrees in names, f"unknown support shape {degrees}")
    return names[degrees]


def product_character(point: tuple[int, int, int, int]) -> int:
    return -1 if (point[2] + point[3]) % 2 else 1


def block_catalogue() -> dict[str, object]:
    all_exact_disjoint: Counter[str] = Counter()
    e0_zero: Counter[str] = Counter()
    sign_split: Counter[tuple[str, int]] = Counter()
    for triple in itertools.combinations(POINTS, 3):
        if not all(
            not (exact_symbols(left) & exact_symbols(right))
            for left, right in itertools.combinations(triple, 2)
        ):
            continue
        shape = support_shape(triple)
        all_exact_disjoint[shape] += 1
        if shape == "repeated_support":
            continue
        e0_zero[shape] += 1
        sign_product = product_character(triple[0]) * product_character(triple[1]) * product_character(triple[2])
        sign_split[(shape, sign_product)] += 1

    require(
        all_exact_disjoint
        == {"3K2": 6720, "P3+K2": 20160, "P4": 6720, "C3": 280, "repeated_support": 1680},
        "exact-disjoint block catalogue",
    )
    require(
        e0_zero == {"3K2": 6720, "P3+K2": 20160, "P4": 6720, "C3": 280},
        "E0-zero block catalogue",
    )
    require(sign_split[("C3", -1)] == 280 and sign_split[("C3", 1)] == 0, "C3 parity")
    for shape in ("3K2", "P3+K2", "P4"):
        require(sign_split[(shape, -1)] == sign_split[(shape, 1)], f"{shape} sign balance")

    # In any selected five-regular block system, multiply one nontrivial
    # character over all 420 point-block incidences.  Each point occurs five
    # times, while the product of that character over the four points in one
    # fibre is +1.  Thus an even number of selected columns have product -1.
    fibre_character_products = {}
    for character in CHARACTERS[1:]:
        per_fibre = 1
        for bits in itertools.product((0, 1), repeat=2):
            per_fibre *= character_value(character, bits)
        require(per_fibre == 1, "nontrivial character fibre product")
        fibre_character_products[str(character)] = {
            "product_over_one_fibre": per_fibre,
            "selected_negative_column_count_mod_2": 0,
        }

    return {
        "all_pairwise_exact_disjoint_triples": sum(all_exact_disjoint.values()),
        "removed_by_42_diagonal_nonedges": all_exact_disjoint["repeated_support"],
        "E0_zero_allowed_triples": sum(e0_zero.values()),
        "all_shape_counts": dict(sorted(all_exact_disjoint.items())),
        "E0_zero_shape_counts": dict(sorted(e0_zero.items())),
        "product_character_counts": [
            {"shape": shape, "product": sign, "triples": count}
            for (shape, sign), count in sorted(sign_split.items())
        ],
        "selected_140_block_shape_equations": [
            "n_3K2+n_P3K2+n_P4+n_C3=140",
            "n_P3K2+2*n_P4+3*n_C3=84",
            "n_P3K2+n_C3 is even",
        ],
        "triangle_support_parity": (
            "for every C3 support block, the product of the three fibre product-characters is -1"
        ),
        "selected_block_character_parities": fibre_character_products,
        "C3_linked_parity": (
            "for character (1,1), n_C3 plus the number of negative-product selected non-C3 blocks is even"
        ),
    }


def character_value(character: tuple[int, int], bits: tuple[int, int]) -> int:
    return -1 if (character[0] * bits[0] + character[1] * bits[1]) % 2 else 1


def fourier_audit() -> dict[str, object]:
    bit_rows = tuple(itertools.product((0, 1), repeat=2))
    hadamard = tuple(
        tuple(character_value(character, bits) for bits in bit_rows)
        for character in CHARACTERS
    )
    gram = tuple(
        tuple(sum(hadamard[i][k] * hadamard[j][k] for k in range(4)) for j in range(4))
        for i in range(4)
    )
    require(gram == tuple(tuple(4 * int(i == j) for j in range(4)) for i in range(4)), "H4")
    flip_signs = {
        str(delta): [character_value(character, delta) for character in CHARACTERS]
        for delta in FLIPS
    }
    require(
        flip_signs
        == {
            "(1, 0)": [1, -1, 1, -1],
            "(0, 1)": [1, 1, -1, -1],
            "(1, 1)": [1, -1, -1, 1],
        },
        "flip character table",
    )
    return {
        "Hadamard_rows": [list(row) for row in hadamard],
        "flip_character_signs": flip_signs,
        "matrices": {
            "A": "R+3I=Z^T Z",
            "L_10": "Z^T P_10 Z",
            "L_01": "Z^T P_01 Z",
            "L_11": "Z^T P_11 Z",
            "G_00": "A+L_10+L_01+L_11",
            "G_10": "A-L_10+L_01-L_11",
            "G_01": "A+L_10-L_01-L_11",
            "G_11": "A-L_10-L_01+L_11",
        },
        "exact_Gram_decomposition": "G_00+G_10+G_01+G_11=4*(R+3I)",
        "each_G": {
            "shape": [140, 140],
            "positive_semidefinite": True,
            "rank_over_R_at_most": 21,
            "trace": 420,
            "all_22_by_22_minors_vanish": True,
            "offdiagonal_entries": "integers in [-3,3]",
        },
        "fibre_row_Grams": {
            "definition": "H_chi=W_chi*W_chi^T",
            "shape": [21, 21],
            "positive_semidefinite": True,
            "diagonal": 20,
            "rank_mod_2_at_most": 20,
        },
        "each_L_delta": {
            "shape": [140, 140],
            "symmetric_nonnegative_integral": True,
            "diagonal": 0,
            "row_sum": 15,
        },
        "row_sums": {"G_00": 60, "G_10": 0, "G_01": 0, "G_11": 0},
        "support_block_graph": {
            "definition": "R_support=G_00-3I=R+L_10+L_01+L_11",
            "offdiagonal_entry_range": [0, 3],
            "simple_graph": False,
            "weighted_degree": 57,
            "eigenvalue_minus_3_multiplicity_at_least": 119,
            "rank_mod_3_of_R_support_at_most": 20,
        },
        "finite_field_rank_proofs": {
            "mod_2": (
                "all W_chi reduce to W_00; its rows have even weight 20 and its columns have odd weight 3, "
                "so H_chi*1=W_chi*(W_chi^T*1)=W_00*(3*1)=20*3*1=0 and rank(H_chi)<=20"
            ),
            "mod_3": (
                "the 21 rows of W_00 sum to the zero row because every column has weight 3; "
                "hence rank(R_support)=rank(G_00)<=20 modulo 3"
            ),
        },
        "why_E0_zero_is_used": (
            "a block contains at most one point of each fibre, so every Fourier row entry is 0 or +/-1 "
            "and every G diagonal is exactly 3"
        ),
    }


def t_square_obstruction() -> dict[str, object]:
    rows = {}
    for delta in FLIPS:
        pairs = []
        seen = set()
        candidate_histogram: Counter[int] = Counter()
        for point in POINTS:
            other = flip(point, delta)
            pair = tuple(sorted((POINT_INDEX[point], POINT_INDEX[other])))
            if pair in seen:
                continue
            seen.add(pair)
            candidates = []
            for third in POINTS:
                if third in (point, other):
                    continue
                if len(exact_symbols(point) & exact_symbols(third)) != 1:
                    continue
                if len(exact_symbols(other) & exact_symbols(third)) != 1:
                    continue
                candidates.append(third)
            candidate_histogram[len(candidates)] += 1
            if delta == (1, 1):
                require(len(candidates) == 2, "diagonal T^2 candidates")
                require(all(support(third) == support(point) for third in candidates), "diagonal candidate fibre")
            else:
                require(len(candidates) == 10, "side T^2 candidates")
                common_symbol = exact_symbols(point) & exact_symbols(other)
                require(len(common_symbol) == 1, "side common symbol")
                require(
                    all(
                        exact_symbols(point) & exact_symbols(third) == common_symbol
                        and exact_symbols(other) & exact_symbols(third) == common_symbol
                        for third in candidates
                    ),
                    "side candidates do not reuse the common-symbol matching",
                )
            pairs.append(pair)
        require(len(pairs) == 42, "fibre matching size")
        rows[str(delta)] = {
            "matching_pairs": len(pairs),
            "potential_common_T_candidate_histogram": {
                str(count): multiplicity for count, multiplicity in sorted(candidate_histogram.items())
            },
            "actual_T_squared_entry": 0,
            "reason": (
                "the two candidates are same-fibre forbidden sides"
                if delta == (1, 1)
                else "using either candidate twice violates the perfect matching on its shared exact symbol"
            ),
        }
    return rows


def scaffold_rhs_trace_targets() -> dict[str, int]:
    targets = {}
    for delta in FLIPS:
        total = 0
        for point in POINTS:
            other = flip(point, delta)
            q = int(bool(exact_symbols(point) & exact_symbols(other)))
            total += 2 - q
        targets[str(delta)] = total
    require(targets == {"(1, 0)": 84, "(0, 1)": 84, "(1, 1)": 168}, "matching trace RHS")
    return targets


def rank_mod(matrix: list[list[int]], prime: int) -> int:
    work = [[value % prime for value in row] for row in matrix]
    pivot = 0
    columns = len(work[0]) if work else 0
    for column in range(columns):
        selected = next((row for row in range(pivot, len(work)) if work[row][column]), None)
        if selected is None:
            continue
        work[pivot], work[selected] = work[selected], work[pivot]
        inverse = pow(work[pivot][column], -1, prime)
        work[pivot] = [(inverse * value) % prime for value in work[pivot]]
        for row in range(len(work)):
            if row == pivot or not work[row][column]:
                continue
            scale = work[row][column]
            work[row] = [
                (left - scale * right) % prime
                for left, right in zip(work[row], work[pivot])
            ]
        pivot += 1
        if pivot == len(work):
            break
    return pivot


# Twenty Z7 orbit seeds.  Their 140 distinct translates give a small exact
# support-level control: 56 matchings plus 84 P3+K2 triples.
CYCLIC_SUPPORT_SEEDS = (
    ((0, 1), (0, 2), (3, 5)),
    ((0, 1), (0, 2), (3, 6)),
    ((0, 1), (0, 2), (4, 6)),
    ((0, 1), (0, 3), (2, 4)),
    ((0, 1), (0, 3), (2, 5)),
    ((0, 1), (0, 3), (2, 6)),
    ((0, 1), (0, 3), (4, 6)),
    ((0, 1), (0, 4), (2, 5)),
    ((0, 1), (0, 4), (3, 5)),
    ((0, 1), (0, 5), (2, 4)),
    ((0, 1), (2, 3), (4, 6)),
    ((0, 1), (2, 4), (3, 5)),
    ((0, 1), (2, 4), (3, 6)),
    ((0, 1), (2, 5), (3, 4)),
    ((0, 1), (2, 5), (3, 6)),
    ((0, 1), (2, 5), (4, 6)),
    ((0, 1), (2, 6), (3, 5)),
    ((0, 1), (3, 5), (4, 6)),
    ((0, 2), (0, 3), (1, 4)),
    ((0, 2), (0, 3), (1, 5)),
)


def rotate_edge(edge: tuple[int, int], shift: int) -> tuple[int, int]:
    return tuple(sorted(((edge[0] + shift) % 7, (edge[1] + shift) % 7)))


def abstract_shape(edges: tuple[tuple[int, int], ...]) -> tuple[str, int]:
    degrees = tuple(sorted(Counter(group for edge in edges for group in edge).values(), reverse=True))
    table = {
        (1, 1, 1, 1, 1, 1): ("3K2", 0),
        (2, 1, 1, 1, 1): ("P3+K2", 1),
        (2, 2, 1, 1): ("P4", 2),
        (2, 2, 2): ("C3", 3),
    }
    require(degrees in table, "forbidden abstract support triple")
    return table[degrees]


def support_level_positive_control() -> dict[str, object]:
    blocks = tuple(
        tuple(sorted(SUPPORT_INDEX[rotate_edge(edge, shift)] for edge in seed))
        for seed in CYCLIC_SUPPORT_SEEDS
        for shift in range(7)
    )
    require(len(blocks) == len(set(blocks)) == 140, "cyclic support blocks")
    incidence = [
        [int(support_index in block) for block in blocks]
        for support_index in range(21)
    ]
    require([sum(row) for row in incidence] == [20] * 21, "support row degrees")
    require([sum(column) for column in zip(*incidence)] == [3] * 140, "support column sizes")
    shape_counts: Counter[str] = Counter()
    overlap_pairs = 0
    for block in blocks:
        shape, overlaps = abstract_shape(tuple(SUPPORTS[index] for index in block))
        shape_counts[shape] += 1
        overlap_pairs += overlaps
    require(shape_counts == {"3K2": 56, "P3+K2": 84}, "control shape counts")
    require(overlap_pairs == 84, "control overlap edge count")

    port_values = []
    for support_index, edge in enumerate(SUPPORTS):
        for group in edge:
            port_values.append(
                sum(
                    support_index in block
                    and any(other != support_index and group in SUPPORTS[other] for other in block)
                    for block in blocks
                )
            )
    port_histogram = Counter(port_values)
    require(port_histogram == {0: 7, 1: 7, 2: 7, 5: 7, 6: 7, 10: 7}, "control port histogram")

    group_occupancies = {}
    for group in range(7):
        histogram = Counter(
            sum(group in SUPPORTS[index] for index in block)
            for block in blocks
        )
        require(histogram == {0: 32, 1: 96, 2: 12}, "control group occupancy")
        group_occupancies[str(group)] = {
            str(occupancy): count for occupancy, count in sorted(histogram.items())
        }

    row_gram = [
        [sum(incidence[i][column] * incidence[j][column] for column in range(140)) for j in range(21)]
        for i in range(21)
    ]
    require({row_gram[i][i] for i in range(21)} == {20}, "control Gram diagonal")
    require({sum(row) for row in row_gram} == {60}, "control Gram row sums")
    ranks = {str(prime): rank_mod(incidence, prime) for prime in (2, 3, 5, 7, 11)}
    require(ranks == {"2": 21, "3": 20, "5": 21, "7": 21, "11": 21}, "control ranks")
    column_gram = [
        [sum(incidence[row][i] * incidence[row][j] for row in range(21)) for j in range(140)]
        for i in range(140)
    ]
    column_gram_ranks = {str(prime): rank_mod(column_gram, prime) for prime in (2, 3)}
    row_gram_ranks = {str(prime): rank_mod(row_gram, prime) for prime in (2, 3)}
    require(column_gram_ranks == {"2": 21, "3": 19}, "control column-Gram ranks")
    require(row_gram_ranks == {"2": 20, "3": 20}, "control row-Gram ranks")
    codegrees = Counter(
        row_gram[i][j] for i, j in itertools.combinations(range(21), 2)
    )
    return {
        "status": "EXACT_SUPPORT_LEVEL_CONTROL_ONLY",
        "cyclic_orbit_seeds": [[list(edge) for edge in seed] for seed in CYCLIC_SUPPORT_SEEDS],
        "blocks": len(blocks),
        "distinct_blocks": len(set(blocks)),
        "row_degree": 20,
        "column_size": 3,
        "shape_counts": dict(sorted(shape_counts.items())),
        "overlapping_support_pairs_across_blocks": overlap_pairs,
        "oriented_support_port_histogram": {
            str(value): count for value, count in sorted(port_histogram.items())
        },
        "satisfies_new_U_port_equations": False,
        "root_group_occupancy_histograms": group_occupancies,
        "rank_mod_prime": ranks,
        "column_Gram_rank_mod_prime": column_gram_ranks,
        "row_Gram_rank_mod_prime": row_gram_ranks,
        "rank_over_Q": 21,
        "row_Gram_diagonal": 20,
        "row_Gram_row_sum": 60,
        "row_Gram_offdiagonal_histogram": {
            str(value): count for value, count in sorted(codegrees.items())
        },
        "scope": (
            "No signs, five-regular 84-point lift, linearity at point level, T, R local graph, "
            "or full residual equation is supplied."
        ),
    }


def signed_point_control_audit() -> dict[str, object]:
    require(POINT_CONTROL.is_file(), "missing signed point control")
    control_hash = sha256(POINT_CONTROL)
    require(control_hash == EXPECTED_POINT_CONTROL_SHA256, "signed point control hash drift")
    raw = json.loads(POINT_CONTROL.read_text(encoding="utf-8"))
    require(raw["status"] == "SIGNED_POINT_CONTROL_FOUND", "signed point control status")

    blocks = []
    for raw_block in raw["selected_signed_blocks"]:
        points = tuple(sorted(POINT_INDEX[tuple(point)] for point in raw_block))
        require(len(points) == len(set(points)) == 3, "signed block size")
        point_rows = tuple(POINTS[index] for index in points)
        require(len({support(point) for point in point_rows}) == 3, "signed block repeats fibre")
        require(
            all(
                not (exact_symbols(left) & exact_symbols(right))
                for left, right in itertools.combinations(point_rows, 2)
            ),
            "signed block is not exact-disjoint",
        )
        blocks.append(points)
    require(len(blocks) == len(set(blocks)) == 140, "signed control block count")

    point_degrees = Counter(point for block in blocks for point in block)
    require(point_degrees == Counter({point: 5 for point in range(84)}), "signed control degree five")
    pair_counts = Counter(pair for block in blocks for pair in itertools.combinations(block, 2))
    require(len(pair_counts) == 420 and set(pair_counts.values()) == {1}, "signed control linearity")
    d_edges = set(pair_counts)
    d_degrees = Counter(point for pair in d_edges for point in pair)
    require(d_degrees == Counter({point: 10 for point in range(84)}), "signed control D degree")

    support_degrees = Counter(
        SUPPORT_INDEX[support(POINTS[point])]
        for block in blocks
        for point in block
    )
    require(support_degrees == Counter({index: 20 for index in range(21)}), "support degree twenty")
    port_values = {}
    for support_index, edge in enumerate(SUPPORTS):
        for group in edge:
            value = sum(
                any(SUPPORT_INDEX[support(POINTS[point])] == support_index for point in block)
                and sum(group in support(POINTS[point]) for point in block) == 2
                for block in blocks
            )
            require(value == 4, "signed control support port")
            port_values[f"{support_index}:{group}"] = value

    u_edges = {
        pair
        for pair in d_edges
        if local_opposite_edge_weight(POINTS[pair[0]], POINTS[pair[1]]) == 1
    }
    require(len(u_edges) == 84, "signed control U edge count")
    u_degrees = Counter(point for pair in u_edges for point in pair)
    require(u_degrees == Counter({point: 2 for point in range(84)}), "signed control U degree")
    point_group_u = Counter()
    for left, right in u_edges:
        common_group = set(support(POINTS[left])) & set(support(POINTS[right]))
        require(len(common_group) == 1, "U shared group")
        group = next(iter(common_group))
        point_group_u[(left, group)] += 1
        point_group_u[(right, group)] += 1
    expected_point_group_rows = {
        (point, group) for point, row in enumerate(POINTS) for group in support(row)
    }
    require(set(point_group_u) == expected_point_group_rows, "signed control U point/group support")
    require(set(point_group_u.values()) == {1}, "signed control U exact one")

    u_adjacency = [set() for _ in range(84)]
    for left, right in u_edges:
        u_adjacency[left].add(right)
        u_adjacency[right].add(left)
    unseen = set(range(84))
    u_cycles = []
    while unseen:
        start = min(unseen)
        stack = [start]
        component = set()
        while stack:
            point = stack.pop()
            if point in component:
                continue
            component.add(point)
            stack.extend(u_adjacency[point] - component)
        require(all(len(u_adjacency[point]) == 2 for point in component), "U component degree")
        u_cycles.append(len(component))
        unseen -= component
    require(sum(u_cycles) == 84 and min(u_cycles) >= 3, "U cycle decomposition")

    selected_blocks = set(blocks)
    all_d_triangles = {
        triple
        for triple in itertools.combinations(range(84), 3)
        if all(tuple(sorted(pair)) in d_edges for pair in itertools.combinations(triple, 2))
    }
    outside_block_triangles = all_d_triangles - selected_blocks
    all_u_triangles = {
        triple
        for triple in itertools.combinations(range(84), 3)
        if all(tuple(sorted(pair)) in u_edges for pair in itertools.combinations(triple, 2))
    }

    block_neighbours = [set() for _ in range(140)]
    for left, right in itertools.combinations(range(140), 2):
        if set(blocks[left]) & set(blocks[right]):
            block_neighbours[left].add(right)
            block_neighbours[right].add(left)
    require({len(row) for row in block_neighbours} == {12}, "control block graph degree")
    local_extra_edges = 0
    for block_index, neighbours in enumerate(block_neighbours):
        expected_pairs = {
            tuple(sorted((left, right)))
            for point in blocks[block_index]
            for left, right in itertools.combinations(
                (other for other in neighbours if point in blocks[other]), 2
            )
        }
        actual_pairs = {
            tuple(sorted((left, right)))
            for left, right in itertools.combinations(neighbours, 2)
            if set(blocks[left]) & set(blocks[right])
        }
        require(expected_pairs <= actual_pairs, "control expected local cliques")
        local_extra_edges += len(actual_pairs - expected_pairs)
    require(local_extra_edges == 3 * len(outside_block_triangles), "Berge/local-extra correspondence")

    shape_counts = Counter(
        support_shape(tuple(POINTS[point] for point in block)) for block in blocks
    )
    require(shape_counts == {"3K2": 56, "P3+K2": 84}, "signed control shapes")
    return {
        "status": "INDEPENDENT_SIGNED_POINT_CONTROL_REPLAY_PASS",
        "sha256": control_hash,
        "solver_status_recorded_but_not_used_as_proof": raw["solver"]["status"],
        "constraints_replayed": {
            "blocks": len(blocks),
            "point_degree": dict(sorted(Counter(point_degrees.values()).items())),
            "linear_D_edges": len(d_edges),
            "support_fibre_degree": dict(sorted(Counter(support_degrees.values()).items())),
            "oriented_support_ports": dict(sorted(Counter(port_values.values()).items())),
            "U_edges": len(u_edges),
            "U_degree": dict(sorted(Counter(u_degrees.values()).items())),
            "point_group_U_exact_one_rows": len(point_group_u),
            "shape_counts": dict(sorted(shape_counts.items())),
            "U_cycle_lengths": sorted(u_cycles),
        },
        "stronger_Wave65_checks_not_imposed": {
            "all_D_triangles": len(all_d_triangles),
            "selected_block_triangles": len(selected_blocks),
            "Berge_triangles_outside_selected_blocks": len(outside_block_triangles),
            "U_triangles_outside_selected_blocks": len(all_u_triangles - selected_blocks),
            "block_graph_local_extra_edges_total": local_extra_edges,
            "R_local_is_3K4": local_extra_edges == 0,
        },
        "scope": (
            "exact positive control only for 5-regularity, point-level linearity, and all 168 U exact-one rows; "
            "it provides neither T nor the full rooted SRG equation"
        ),
    }


def markdown(result: dict[str, object]) -> str:
    signed = result["signed_point_U_factor_positive_control"]
    replay = signed["constraints_replayed"]
    stronger = signed["stronger_Wave65_checks_not_imposed"]
    return f"""# The `E0(r)=0` rooted hypergraph layer

Status: `{result['status']}`.

This is a clean-room necessary-condition audit.  It uses the independently
verified Wave65 identities but does not import or rerun its discovery code.
No graph, endpoint exclusion, or Conway-99 resolution is claimed.

## What `E0(r)=0` newly removes

The 84 residual points are the four signed versions of each of the 21 edges
of `K7`.  Within a fibre there are four side pairs sharing one exact symbol
and two complementary diagonals.  `E0(r)=0` makes all six pairs nonedges.
For the Wave65 split `B=T+D`, this removes 84 possible same-fibre `T` sides
and the 42 possible same-fibre `D` diagonals.

For a residual point `x` and the mate of either one of its two exact support
labels, `mu=2` leaves exactly one outer common neighbour after the original
support label.  The same-fibre prohibition forces this neighbour into a
different fibre.  Thus every point has exactly one overlapping-support `D`
neighbour through each support group.  Consequently `D` splits into 84
overlapping-support and 336 disjoint-support edges.  Each support fibre lies
in 20 distinct blocks, and relative to each of the seven root groups the 140
blocks have occupancy distribution

```text
number of incident supports in block:   0   1   2
number of blocks:                       32  96  12.
```

More sharply, for every support fibre `e` and each endpoint group `g` of
`e`, exactly four selected blocks containing `e` contain a second support
through `g`.  These are 42 separate support-port equalities, obtained by
summing the four signed point/group degree-one equations for `U`.

A `D` block is a triple of pairwise exact-symbol-disjoint points.  Of 35,560
such labelled triples, exactly 1,680 use a repeated support: one of the 42
diagonals followed by a point on one of ten disjoint supports, with four sign
choices.  They are all forbidden.  The remaining 33,880 triples have three
distinct supports, with catalogue

```text
3K2       6,720
P3+K2    20,160
P4        6,720
C3          280
```

If the selected 140 blocks have shape counts `n0,n1,n2,n3` in this order,

```text
n0+n1+n2+n3 = 140,
n1+2n2+3n3 = 84,
n1+n3 is even.
```

The second equation counts the 84 selected `D` edges whose supports meet.
For a `C3` support block, the product of the three within-fibre product signs
is necessarily `-1`; the script checks all 280 labelled cases.  For each of
the three nontrivial fibre characters, the number of selected blocks with
negative column-product is even.  For character `(1,1)` this says that
`n_C3` plus the negative-product non-`C3` count is even.

## The opposite-edge product supplies a second 2-factor

Let `C` be unsigned vertex-edge incidence, `R_tm` mark the unique triangle
mate of each graph edge, and `J_e` be the opposite-edge graph.  (`R_tm` is
not Wave65's 140-block graph `R`.)  Direct entrywise counting gives

```text
C J_e = A C-C-2R_tm,
C R_tm^T=A,                 R_tm R_tm^T=7I,
C J_e R_tm^T=2(J_99-I-A).
```

Therefore row `r` of `R_tm J_e`, viewed as weights on residual edges, has
weighted degree two at each of the 84 outer points and zero elsewhere.  Its
local weights are 1 on a same-fibre side, 2 on a same-fibre diagonal, 1 on a
distinct-fibre exact-disjoint pair with one common support group, and 0 on
the other pair types.  At `E0(r)=0` only the third type survives, with weight
one, so it is a binary 2-factor

```text
U = D restricted to overlapping group supports.
```

This is not Wave65's `T`: a `T` edge has equal signs at its shared group and
`Q=1`, while a `U` edge has opposite signs and `Q=0`.  Thus `T` and `U` are
edge-disjoint.  For each root group `g`, `T_g` is two six-edge matchings
inside the two sign classes and `U_g` is a twelve-edge matching between the
classes.  Every component of `T_g union U_g` is consequently an alternating
cycle of length divisible by four.  Its possible cycle signatures are four
times the 11 partitions of six, and

```text
rank_R(T_g+U_g)=24-2c_g,
```

where `c_g` is the number of cycles; in particular every such local matrix
is singular.  In the target, `lambda=1` also prevents any `D`-triangle made
from three different hyperedges.  Inside one selected `D` block the number
of `U` edges is `0,1,2,3` for the four shapes above, giving additionally

```text
tr(U^3)=6 n_C3,
tr(U^2 D)=2 n_P4+6 n_C3,
tr(U^2(D-U))=2 n_P4.
```

## New 21-fibre Fourier Gram system

Let `P10,P01,P11` flip the first, second, or both signs in every fibre, put
`L_delta=Z^T P_delta Z`, and put `A=R+3I=Z^T Z`.  Because no block repeats a
fibre, the four unnormalised fibre-character incidence matrices `W_chi` are
21 by 140 with entries in `{{0,+1,-1}}`.  Exact Hadamard orthogonality gives

```text
G00 = A+L10+L01+L11,
G10 = A-L10+L01-L11,
G01 = A+L10-L01-L11,
G11 = A-L10-L01+L11,

G00+G10+G01+G11 = 4(R+3I).
```

Every `G_chi=W_chi^T W_chi` is PSD, has trace 420 and rank at most 21;
therefore every 22 by 22 minor vanishes.  Each `L_delta` is symmetric,
nonnegative integral, hollow, and 15-regular.  The `G_chi` row sums are
respectively `60,0,0,0`.  In particular the weighted (not necessarily
simple) support-overlap block graph

```text
R_support=G00-3I=R+L10+L01+L11
```

is 57-regular and has eigenvalue `-3` with multiplicity at least 119.
Modulo 3 its rank is at most 20.  There is also a separate characteristic-two
constraint on the 21 by 21 fibre row-Grams

```text
H_chi=W_chi W_chi^T:    rank_F2(H_chi)<=20.
```

Indeed all four signed incidences reduce to the same matrix modulo 2; its row
weights are 20 and its column weights are 3, so `H_chi 1=0`.  (This does not
assert the same rank bound for the 140 by 140 column-Grams in characteristic
two.)  This four-Gram decomposition, its entry alphabet, and the large
kernels are information added by the same-fibre prohibition; Wave65's single
`Z^T Z` Gram does not record them.

## Diagonal-pair collision identity coupling `Z` and `T`

For all three fibre matchings, `T^2[x,Px]=0`.  For a side pair, every possible
common `T` candidate would use the same exact-symbol perfect matching twice;
for a diagonal pair the only two candidates are forbidden same-fibre sides.
The script exhausts all 42 pairs of each kind.

Let `L_delta=Z^T P_delta Z` and
`M_delta=tr(Z^T P_delta T Z)=tr(T D P_delta)`.  Taking the matching trace of
`B^2+B=10I+2J-Q` gives the new exact necessities

```text
tr(R L10)+2 M10 = 84,
tr(R L01)+2 M01 = 84,
tr(R L11)+2 M11 = 168.
```

For the 42 diagonal pairs define `A` as their total number of common
`D`-neighbours and `M` as their total mixed `T/D` common-neighbours.  Then

```text
A = tr(R L11)/2,
M = tr(Z^T P11 T Z),
A+M = 84.
```

Equivalently, between two diagonal-pair quotient vertices of disjoint
supports let `p,q <= 2` count the two orientation classes of selected `D`
edges.  Then `A=sum p*q`, so `sum p*q<=84`.  This is an entrywise collision
budget coupling the hypergraph blocks to `T`, not a scalar consequence of
`D+5I=ZZ^T` alone.

## Boundary

The original embedded 140-block cyclic support control has 56 `3K2` and 84
`P3+K2` blocks, support degree 20, rational rank 21, and the forced
`(32,96,12)` group occupancy.  It does *not* satisfy the new oriented-port
rows: its 42 values are `0,1,2,5,6,10`, each seven times.  Thus the new
2-factor bridge genuinely distinguishes it from a sign-liftable control.

A second bounded search selected 20 of all 170 cyclic support orbits, making
all 42 port values four, then searched the 6,272 compatible signed blocks on
that fixed skeleton.  It found a witness, which this clean-room script replays
without trusting the solver status:

```text
blocks / unique D edges / U edges:  {replay['blocks']} / {replay['linear_D_edges']} / {replay['U_edges']}
point-degree rows:                  {replay['point_degree']}
point/group U exact-one rows:       {replay['point_group_U_exact_one_rows']}
U cycle lengths:                    {replay['U_cycle_lengths']}
```

This proves that degree five, point-level linearity, and all 168 `U`
exact-one rows are jointly feasible; hence they yield no contradiction.
The control intentionally omitted `T` and the full rooted equation.  As a
diagnostic, it has {stronger['Berge_triangles_outside_selected_blocks']} Berge
triangles outside its selected blocks (including
{stronger['U_triangles_outside_selected_blocks']} `U`-triangles) and
{stronger['block_graph_local_extra_edges_total']} aggregate extra local
block-graph edges, so `R` is not locally `3K4`.  The first unresolved layer
is therefore the stronger compatibility of the four Fourier Grams, both
2-factors, the three matching-trace identities, the local `3K4` condition,
and Wave65's entrywise equation.  No Conway-99 conclusion is claimed.
"""


def main() -> None:
    require(WAVE65_VERIFY.is_file(), "missing Wave65 verifier summary")
    wave65_hash = sha256(WAVE65_VERIFY)
    require(wave65_hash == EXPECTED_WAVE65_SHA256, "Wave65 verifier hash drift")
    wave65 = json.loads(WAVE65_VERIFY.read_text(encoding="utf-8"))
    require(wave65["claim_label"] == "VERIFIED", "Wave65 verification status")
    require(wave65["generic_hypergraph"]["identity_D"] == "D+5I=ZZ^T", "Wave65 D Gram")
    require(wave65["generic_hypergraph"]["identity_R"] == "R+3I=Z^TZ", "Wave65 R Gram")
    require(wave65["rooted_scaffold"]["identity"] == "B^2+B=10I+2J-Q", "Wave65 block equation")

    relations = relation_census()
    forced = forced_fibre_and_opposite_factor()
    blocks = block_catalogue()
    fourier = fourier_audit()
    t2 = t_square_obstruction()
    rhs_targets = scaffold_rhs_trace_targets()
    control = support_level_positive_control()
    signed_control = signed_point_control_audit()

    result = {
        "status": "E0_ZERO_HYPERGRAPH_AUDIT_PASS",
        "condition": "one fixed root r of a hypothetical srg(99,14,1,2) has E0(r)=0",
        "sealed_input": {
            "wave65_independent_results_sha256": wave65_hash,
            "wave65_claim_label": wave65["claim_label"],
            "wave65_scope_reused": [
                "D+5I=ZZ^T",
                "R+3I=Z^TZ",
                "B^2+B=10I+2J-Q",
                "Z has shape 84x140, row sum 5, column sum 3",
                "T is the exact-symbol-sharing 2-factor",
            ],
            "signed_point_control_sha256": signed_control["sha256"],
        },
        "independent_signed_edge_census": relations,
        "forced_fibre_and_opposite_factor": forced,
        "independent_D_block_catalogue": blocks,
        "new_fibre_Fourier_Gram_system": fourier,
        "T_squared_same_fibre_audit": t2,
        "matching_trace_identities": {
            "scaffold_rhs_ordered_trace_targets": rhs_targets,
            "identities": {
                "P_10": "tr(R*L_10)+2*tr(Z^T*P_10*T*Z)=84",
                "P_01": "tr(R*L_01)+2*tr(Z^T*P_01*T*Z)=84",
                "P_11": "tr(R*L_11)+2*tr(Z^T*P_11*T*Z)=168",
            },
            "diagonal_collision_form": {
                "A": "tr(R*L_11)/2 = total common-D-neighbours over the 42 diagonal pairs",
                "M": "tr(Z^T*P_11*T*Z) = total mixed T/D common-neighbours",
                "identity": "A+M=84",
                "bounds": {"A": [0, 84], "M": [0, 84]},
                "quotient_orientation_form": "A=sum_{disjoint-support quotient pairs i<j} p_ij*q_ij",
                "orientation_cap": "0<=p_ij,q_ij<=2",
            },
        },
        "support_level_positive_control": control,
        "signed_point_U_factor_positive_control": signed_control,
        "outcome": {
            "contradiction_found": False,
            "new_necessary_information": [
                "every D block uses three distinct fibres; 1680 repeated-support candidate triples disappear",
                "the triangle-mate/opposite-edge product becomes a binary 2-factor U inside D, disjoint from T",
                "42 oriented support-port equalities force four overlap blocks at every fibre endpoint",
                "for each root group, T_g union U_g has only cycles of length divisible by four",
                "four PSD 140x140 fibre-character Grams of rank at most 21 sum to 4(R+3I)",
                "the support-overlap block graph has a -3 eigenspace of dimension at least 119",
                "the four 21x21 fibre row-Grams have rank at most 20 modulo 2",
                "three matching-trace identities couple the hypergraph Z to T",
                "the diagonal quotient collision budget is sum p*q<=84",
                "a signed 140-block control shows degree five, linearity, and all 168 U exact-one rows remain feasible",
            ],
            "remaining_gap": (
                "simultaneous sign lift and entrywise compatibility of the four Grams, T, and the rooted block equation"
            ),
        },
        "scope_wall": {
            "full_SAT_enumeration_run": False,
            "support_control_is_84_point_hypergraph": False,
            "support_control_is_residual_graph": False,
            "signed_point_control_is_full_Wave65_control": False,
            "E0_zero_excluded": False,
            "Conway_99": "UNKNOWN",
        },
    }
    atomic_write(OUTPUT_JSON, json.dumps(result, indent=2, sort_keys=True) + "\n")
    atomic_write(OUTPUT_MD, markdown(result))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
