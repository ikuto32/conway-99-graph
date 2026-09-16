"""Exact arithmetic study of the triangle-flag relation at sum E0 = 0.

This is a source-light discovery/checking artifact.  It does not enumerate
the 916 order-eight classes.  It reads the already frozen integral boundary
only to locate one explicitly identified order-eight class.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path


OUTPUT = Path("scratch_theory_e0_zero_triangle_flag_relation.json")
BOUNDARY = Path("scratch_theory_wave163_integral_order8_boundary.json")
WAVE205 = Path(
    "external_conway99_research/attempts/"
    "wave205-nonedge-fourth-trace-proof-a/exact-results.json"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def frac(value: Fraction | int) -> int | str:
    value = Fraction(value)
    return value.numerator if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def edge_pairs(order: int) -> tuple[tuple[int, int], ...]:
    return tuple(itertools.combinations(range(order), 2))


def mask_of(edges: set[tuple[int, int]], permutation: tuple[int, ...]) -> int:
    pairs = edge_pairs(len(permutation))
    positions = {edge: index for index, edge in enumerate(pairs)}
    transformed = {
        tuple(sorted((permutation[left], permutation[right]))) for left, right in edges
    }
    return sum(1 << positions[edge] for edge in transformed)


def degrees(order: int, edges: set[tuple[int, int]]) -> tuple[int, ...]:
    result = [0] * order
    for left, right in edges:
        result[left] += 1
        result[right] += 1
    return tuple(result)


def canonical_global(order: int, edges: set[tuple[int, int]]) -> int:
    return min(mask_of(edges, permutation) for permutation in itertools.permutations(range(order)))


def canonical_degree_cell(order: int, edges: set[tuple[int, int]]) -> int:
    degree = degrees(order, edges)
    cells: dict[int, list[int]] = {}
    for vertex, value in enumerate(degree):
        cells.setdefault(value, []).append(vertex)
    starts = 0
    choices = []
    for value in sorted(cells):
        vertices = cells[value]
        targets = tuple(range(starts, starts + len(vertices)))
        starts += len(vertices)
        choices.append(tuple(dict(zip(vertices, p)) for p in itertools.permutations(targets)))
    best = None
    for maps in itertools.product(*choices):
        permutation = [0] * order
        for mapping in maps:
            for source, target in mapping.items():
                permutation[source] = target
        value = mask_of(edges, tuple(permutation))
        best = value if best is None else min(best, value)
    assert best is not None
    return best


def triangles(order: int, edges: set[tuple[int, int]]) -> tuple[frozenset[int], ...]:
    return tuple(
        frozenset(vertices)
        for vertices in itertools.combinations(range(order), 3)
        if all(tuple(sorted(edge)) in edges for edge in itertools.combinations(vertices, 2))
    )


def locally_admissible(order: int, edges: set[tuple[int, int]]) -> bool:
    neighborhoods = [set() for _ in range(order)]
    for left, right in edges:
        neighborhoods[left].add(right)
        neighborhoods[right].add(left)
    for left in range(order):
        for right in range(left + 1, order):
            common = len(neighborhoods[left] & neighborhoods[right])
            adjacent = tuple(sorted((left, right))) in edges
            if common > (1 if adjacent else 2):
                return False
    return True


def collision_event_count(order: int, edges: set[tuple[int, int]]) -> int:
    """Count marked C_8 events in the induced graph.

    An event is (r,U,{T1,T2}), where T1,T2 are distinct triangles through r,
    U is a triangle anticomplete to r, and each Ti--U pair has exactly two
    independent cross edges leaving r and a different vertex of U unmatched.
    """
    tri = triangles(order, edges)
    count = 0
    for root in range(order):
        for target in tri:
            if root in target:
                continue
            if any(tuple(sorted((root, vertex))) in edges for vertex in target):
                continue
            sources = [item for item in tri if root in item and item.isdisjoint(target)]
            for first, second in itertools.combinations(sources, 2):
                unmatched_targets = []
                valid = True
                for source in (first, second):
                    cross = [
                        (left, right)
                        for left in source
                        for right in target
                        if tuple(sorted((left, right))) in edges
                    ]
                    if (
                        len(cross) != 2
                        or len({left for left, _ in cross}) != 2
                        or len({right for _, right in cross}) != 2
                    ):
                        valid = False
                        break
                    source_unmatched = next(iter(source - {left for left, _ in cross}))
                    target_unmatched = next(iter(target - {right for _, right in cross}))
                    if source_unmatched != root:
                        valid = False
                        break
                    unmatched_targets.append(target_unmatched)
                if valid and len(set(unmatched_targets)) == 2:
                    count += 1
    return count


def main() -> None:
    # Endpoint arithmetic.
    vertices = 99
    triangles_count = 231
    flags = 693
    x_degree = 12
    x_edges = flags * x_degree // 2
    assert x_edges == 4158
    assert (32, 144, 36, 0) == (20 + 12, 180 - 3 * 12, 3 * 12, 12 - 12)

    # SRG Bose--Mesner eigenvalues and incidence principal angles.
    a_eigen = {"regular": (14, 1), "plus3": (3, 54), "minus4": (-4, 44)}
    nn_eigen = {name: (7 + value, multiplicity) for name, (value, multiplicity) in a_eigen.items()}
    assert nn_eigen == {"regular": (21, 1), "plus3": (10, 54), "minus4": (3, 44)}

    # H=F^T X F has the same adjacency-algebra projection as bar(A).
    trace_e0_h = Fraction(84)
    trace_e3_h = Fraction(-216)
    trace_em4_h = Fraction(132)
    assert trace_e0_h + trace_e3_h + trace_em4_h == 0
    assert trace_e3_h == 54 * (-4)
    assert trace_em4_h == 44 * 3

    # Let ell=sum_{r<s} binom(H_rs,2), Delta=H-bar(A), and
    # delta_theta=||Delta E_theta||_F^2.  Then delta3+delta4=4 ell.
    ell_symbolic_coefficient = 4
    z3_floor = Fraction(trace_e3_h * trace_e3_h, 54)
    z4_floor = Fraction(trace_em4_h * trace_em4_h, 44)
    assert z3_floor == 864 and z4_floor == 396

    # Orthogonalize the ordinary edge-incidence space against F.
    residual_incidence_eigen = {
        "regular": Fraction(0),
        "plus3": Fraction(110, 7),
        "minus4": Fraction(54, 7),
    }
    base_projection_plus3 = 54 * Fraction(44, 7) ** 2 / residual_incidence_eigen["plus3"]
    base_projection_minus4 = 44 * Fraction(54, 7) ** 2 / residual_incidence_eigen["minus4"]
    base_projection = base_projection_plus3 + base_projection_minus4
    assert base_projection_plus3 == Fraction(4752, 35)
    assert base_projection_minus4 == Fraction(2376, 7)
    assert base_projection == Fraction(2376, 5)

    delta3_coefficient = Fraction(9, 770)
    delta4_coefficient = Fraction(8, 189)
    assert delta4_coefficient - delta3_coefficient == Fraction(91, 2970)
    ell_projection_coefficient = 4 * delta3_coefficient
    assert ell_projection_coefficient == Fraction(18, 385)

    # ||Y(I-P_F)||^2 = 7128-4 ell/7 dominates the projection above.
    ell_upper_rational = (Fraction(7128) - base_projection) / (
        Fraction(4, 7) + ell_projection_coefficient
    )
    assert ell_upper_rational == Fraction(182952, 17)
    ell_upper_integer = ell_upper_rational.numerator // ell_upper_rational.denominator
    assert ell_upper_integer == 10761
    minimum_vertex_partition_residual = Fraction(7128) - Fraction(4, 7) * ell_upper_integer
    assert minimum_vertex_partition_residual == Fraction(6852, 7)

    # The mixed point--triangle count W=F^T X Q has an order-eight collision.
    # This representative uses r=0, two source triangles 012 and 034, and
    # target triangle 567.  The two N3 matchings leave target 5 and 6 unmatched.
    c8_edges = {
        (0, 1), (0, 2), (1, 2),
        (0, 3), (0, 4), (3, 4),
        (5, 6), (5, 7), (6, 7),
        (1, 6), (2, 7), (3, 5), (4, 7),
    }
    c8_degree = tuple(sorted(degrees(8, c8_edges), reverse=True))
    c8_global_mask = canonical_global(8, c8_edges)
    c8_degree_mask = canonical_degree_cell(8, c8_edges)
    c8_events = collision_event_count(8, c8_edges)
    automorphisms = sum(
        1
        for permutation in itertools.permutations(range(8))
        if {
            tuple(sorted((permutation[left], permutation[right])))
            for left, right in c8_edges
        } == c8_edges
    )
    assert len(c8_edges) == 13
    assert c8_degree == (4, 4, 3, 3, 3, 3, 3, 3)
    assert locally_admissible(8, c8_edges)
    assert c8_global_mask == 5675512
    assert c8_degree_mask == 44481136
    assert c8_events == 1
    assert automorphisms == 2

    boundary = json.loads(BOUNDARY.read_text(encoding="utf-8"))
    x8 = dict(boundary["integral_pseudocount"]["order8_mask_count_pairs"])
    assert boundary["endpoint"]["sum_E0"] == 0
    assert x8[c8_degree_mask] == 2442

    # A frozen Wave205 two-centre control realizes the lowest permitted
    # nonedge value t_rs=6.  In the notation here H_rs=t_rs-6, so it is an
    # exact local H_rs=0 control.  The Wave205 field called ``h`` is a
    # different invariant (an F_3 fourth trace), not an entry of this H.
    wave205 = json.loads(WAVE205.read_text(encoding="utf-8"))
    wave205_t6 = next(item for item in wave205["controls"] if item["name"] == "t6_h1")
    assert wave205_t6["claimed_and_recomputed_t"] == 6
    assert wave205_t6["claimed_and_recomputed_h"] == 1
    wave205_local = wave205_t6["local_graph"]
    assert wave205_local["vertex_count"] == 28
    assert wave205_local["center_degrees"] == {"x": 14, "y": 14}
    assert wave205_local["center_common_neighbors"] == ["a", "b"]
    for key in (
        "all_edges_have_at_most_one_local_common_neighbor",
        "all_nonedges_have_at_most_two_local_common_neighbors",
        "endpoint_cross_edge_cap_on_selected_disjoint_blocks",
        "full_local_B_transpose_A_B_reproduces_two_star_gram",
        "opposite_center_mu_two_for_all_exclusive_neighbors",
    ):
        assert wave205_local[key] is True
    assert wave205_t6["two_star_gram"]["rank"] == 11
    assert wave205_t6["two_star_gram"]["embedding"]["principal_determinant"] == 2
    assert wave205_t6["two_star_gram"]["kernel_minimum_nonzero_weight"] == 6
    assert "completion from 28 to 99 vertices" in wave205["omitted_target_premises"]

    # Full triangle-partition projection.  C8 denotes sum binom(W_rT,2),
    # delta4=||Delta E_-4||^2, delta3=4 ell-delta4.
    # The component of NK outside row(N) has this exact squared norm.
    kernel_constant = Fraction(16632, 5)
    kernel_c8_coefficient = Fraction(2)
    kernel_ell_coefficient = Fraction(-2, 5)
    kernel_delta4_coefficient = Fraction(-7, 30)

    # Adding one third of that kernel norm to the incidence projection gives
    # 1584 -20 ell/231 +2 C8/3 -14 delta4/297.
    full_constant = base_projection + kernel_constant / 3
    full_ell_coefficient = ell_projection_coefficient + kernel_ell_coefficient / 3
    full_delta4_coefficient = (
        delta4_coefficient - delta3_coefficient + kernel_delta4_coefficient / 3
    )
    full_c8_coefficient = kernel_c8_coefficient / 3
    assert full_constant == 1584
    assert full_ell_coefficient == Fraction(-20, 231)
    assert full_delta4_coefficient == Fraction(-14, 297)
    assert full_c8_coefficient == Fraction(2, 3)

    # Using 0<=delta4<=4 ell yields the clean collision tradeoff.
    # 4 ell + 9 C8 <= 74844.
    assert Fraction(8, 27) * Fraction(27, 2) == 4
    assert Fraction(2, 3) * Fraction(27, 2) == 9
    assert Fraction(5544) * Fraction(27, 2) == 74844
    tradeoff_lhs_at_frozen_c8_and_ell_zero = 9 * x8[c8_degree_mask]
    assert tradeoff_lhs_at_frozen_c8_and_ell_zero == 21978 < 74844

    # At least this many of the 4,158 nonedge point-pairs carry an X edge.
    support_blocks_lower = math.ceil(4158**2 / (4158 + 2 * ell_upper_integer))
    assert support_blocks_lower == 674

    # Short-walk traces.  Fourth traces are the first unfrozen X moments.
    tr_x2 = flags * x_degree
    tr_x4_base = flags * x_degree * (2 * x_degree - 1)
    tr_k2 = triangles_count * 36
    tr_k4_base = triangles_count * 36 * (2 * 36 - 1)
    assert tr_x2 == 8316 and tr_x4_base == 191268
    assert tr_k2 == 8316 and tr_k4_base == 590436
    trace_s3 = 13 * triangles_count * 68
    assert trace_s3 == 204204

    result = {
        "status": "E0_ZERO_TRIANGLE_FLAG_RELATION_EXACT_STUDY_PASS",
        "scope": (
            "Necessary consequences conditional on a putative srg(99,14,1,2) "
            "and sum_r E0(r)=0.  No endpoint exclusion or graph construction."
        ),
        "inputs_sha256": {
            str(BOUNDARY): sha256(BOUNDARY),
            str(WAVE205): sha256(WAVE205),
            "scratch_theory_root_flag_union.md": sha256(Path("scratch_theory_root_flag_union.md")),
            "scratch_theory_root_yyt_augmented_relation.json": sha256(
                Path("scratch_theory_root_yyt_augmented_relation.json")
            ),
            "external_conway99_research/agents/2026-07-22-wave6-opposite-edge-graph.md": sha256(
                Path("external_conway99_research/agents/2026-07-22-wave6-opposite-edge-graph.md")
            ),
            "external_conway99_research/agents/2026-07-26-wave35-n3-4158-combinatorial.md": sha256(
                Path("external_conway99_research/agents/2026-07-26-wave35-n3-4158-combinatorial.md")
            ),
            "external_conway99_research/agents/2026-07-26-wave35-n3-upper-spectral.md": sha256(
                Path("external_conway99_research/agents/2026-07-26-wave35-n3-upper-spectral.md")
            ),
        },
        "endpoint": {
            "sum_E0": 0,
            "pointwise": "E0(r)=S(r)=D(r)=0 for every r",
            "P": 0,
            "n3": 4158,
            "q_of_every_triangle": 12,
            "triangle_profile_a0_a1_a2_a3": [32, 144, 36, 0],
        },
        "flag_relation_X": {
            "flags": flags,
            "identification": "(T,t) is the graph edge T\\{t}",
            "equals_opposite_edge_graph_at_endpoint": True,
            "simple_symmetric": True,
            "regular_degree": x_degree,
            "edges": x_edges,
            "triangle_free": True,
            "trace_X": 0,
            "trace_X2": tr_x2,
            "trace_X3": 0,
            "trace_X4": f"{tr_x4_base}+8*c4(X)",
            "first_unfixed_walk_moment": "c4(X), an order-at-most-eight motif count",
        },
        "incidence_algebra": {
            "matrices": {
                "F": "693x99 flag-to-unmatched-point incidence, F^T F=7I",
                "Q": "693x231 flag-to-triangle incidence, Q^T Q=3I",
                "N": "F^T Q, the 99x231 point-triangle incidence",
                "C": "ordinary point-edge incidence = N Q^T-F^T",
                "K": "Q^T X Q, the triangle N3 adjacency",
                "W": "F^T X Q",
                "H": "F^T X F",
            },
            "identities": [
                "N N^T=7I+A",
                "C X=A C-C-2F^T",
                "W=N K-2A N+4N",
                "N W^T-H=2(J-I-A)",
                "H=N K N^T+6I-6A-6J",
                "(F^T X) C^T=2(J-I-A)",
            ],
            "normalized_F_Q_principal_angles_squared": {
                "1": {"multiplicity": 1, "value": 1},
                "plus3": {"multiplicity": 54, "value": "10/21"},
                "minus4": {"multiplicity": 44, "value": "1/7"},
            },
            "span_dimension": 329,
        },
        "triangle_projector_and_quotient": {
            "M_identities": ["M^2=21M", "M1=0", "diag(M)=4", "rank(M)=44"],
            "endpoint_M_row": {"+1": 32, "0": 162, "-1": 36, "diagonal_4": 1},
            "K_from_M": "K=(M o M o M+M o M-2M)/2-36I=(M o M-M)/2-6I at the endpoint",
            "K_simple_regular_degree": 36,
            "K_edges": 4158,
            "trace_K2": tr_k2,
            "trace_K3": "6*tau_K, not fixed; tau_K is an order-nine triple of pairwise-disjoint triangles",
            "trace_K4": f"{tr_k4_base}+8*c4(K)",
            "signed_relation_identity": (
                "For S=P-K=M-4I, S^2=13S+68I and "
                "tr(P^3)-3tr(P^2K)+3tr(PK^2)-tr(K^3)=204204"
            ),
            "ordinary_projector_equation_does_not_isolate_tau_K": True,
        },
        "point_partition_H": {
            "entrywise": {
                "diagonal": 0,
                "graph_edge": 0,
                "graph_nonedge": "H_rs=(N K N^T)_rs-6 in {0,1,...,7}",
            },
            "why_blocks_are_partial_matchings": (
                "D(r)=D(s)=0 gives both column and row degrees at most one in "
                "each 7x7 block X[F_r,F_s]"
            ),
            "row_sum": 84,
            "adjacency_algebra_projection": "bar(A)=J-I-A",
            "wave205_t_profile": {
                "t": "N K N^T",
                "diagonal": 0,
                "graph_edge": 12,
                "graph_nonedge": "6+H_rs in {6,...,13}",
                "row_sum": 756,
            },
            "collision": {
                "ell_definition": "sum_{r<s} binom(H_rs,2)",
                "trace_H2": "8316+4*ell",
                "Delta_definition": "H-(J-I-A)",
                "norm_Delta_squared": "4*ell",
                "delta3_delta4": "||Delta E_3||_F^2+||Delta E_-4||_F^2=4*ell",
                "exact_upper_rational": frac(ell_upper_rational),
                "integer_upper": ell_upper_integer,
                "nonzero_H_blocks_lower_bound": support_blocks_lower,
            },
        },
        "zero_H_block_local_boundary": {
            "identity": "for a graph nonedge r,s, H_rs=(N K N^T)_rs-6=t_rs-6",
            "frozen_control": "Wave205 t6_h1",
            "control_t_rs": wave205_t6["claimed_and_recomputed_t"],
            "therefore_H_rs": wave205_t6["claimed_and_recomputed_t"] - 6,
            "Wave205_h_warning": (
                "the control field claimed_and_recomputed_h=1 is an F_3 fourth trace, "
                "not the entry H_rs used in this note"
            ),
            "local_control": {
                "vertices": wave205_local["vertex_count"],
                "center_degrees": wave205_local["center_degrees"],
                "center_common_neighbors": wave205_local["center_common_neighbors"],
                "lambda_mu_local_caps": True,
                "opposite_center_mu_two_for_all_exclusive_neighbors": True,
                "endpoint_selected_block_cap": True,
                "two_star_gram_reproduced": True,
                "two_star_gram_rank": wave205_t6["two_star_gram"]["rank"],
                "two_star_gram_principal_determinant": (
                    wave205_t6["two_star_gram"]["embedding"]["principal_determinant"]
                ),
                "kernel_minimum_nonzero_weight": (
                    wave205_t6["two_star_gram"]["kernel_minimum_nonzero_weight"]
                ),
            },
            "rigorous_boundary": (
                "The listed two-centre lambda/mu caps, selected endpoint block cap, "
                "and full local two-star Gram/projectivity conditions do not imply "
                "H_rs>=1.  The control is not a 99-vertex completion."
            ),
            "smallest_missing_synchronization": (
                "simultaneous compatibility of all 99 overlapping point-stars, including "
                "completion of every currently unsaturated pair outside the 28-vertex control"
            ),
        },
        "equitable_and_cover_boundary": {
            "equitable_iff": "X F=F B, equivalently H=7B",
            "partial_matching_consequence": (
                "B is a simple 12-regular graph supported on graph nonedges; "
                "X is a seven-sheet graph cover of B"
            ),
            "excluded": True,
            "proof": (
                "Equitability gives Y=B F^T, hence B A=2(J-I-A).  Since A is "
                "invertible, B=(J-A-13I)/6, whose diagonal is -2 and whose "
                "nonedge entries are 1/6."
            ),
            "quantitative_residual": {
                "norm_squared": "||X F-FH/7||_F^2=7128-4*ell/7",
                "lower_from_integer_ell_bound": frac(minimum_vertex_partition_residual),
            },
        },
        "triangle_partition": {
            "compression": "(Q/sqrt(3))^T X (Q/sqrt(3))=K/3",
            "not_equitable": (
                "each K-edge is represented by exactly one edge in its 3x3 flag block, "
                "so a nonzero block cannot have constant integral row degree"
            ),
            "gram_residual": "Q^T X^2 Q-K^2/3 is positive semidefinite",
            "gram_residual_trace": 5544,
        },
        "new_projection_bound": {
            "residual": "R=(F^T X)(I-FF^T/7)",
            "residual_norm_squared": "7128-4*ell/7",
            "residual_edge_incidence_gram_spectrum": {
                "regular": 0,
                "plus3": frac(residual_incidence_eigen["plus3"]),
                "minus4": frac(residual_incidence_eigen["minus4"]),
            },
            "projected_lower_bound": (
                "2376/5+(9/770)delta3+(8/189)delta4 "
                "=2376/5+(18/385)ell+(91/2970)delta4"
            ),
            "consequence": f"ell<={ell_upper_integer}",
            "full_F_plus_Q_projection": {
                "P0": "orthogonal projector onto ker(N) in triangle-label space",
                "extra_nonnegative_term": "(1/3)||N K P0||_F^2",
                "kernel_norm_identity": (
                    "||N K P0||_F^2=16632/5+2*C8-(2/5)ell-(7/30)delta4"
                ),
                "total_projected_lower_bound": (
                    "1584-(20/231)ell+(2/3)C8-(14/297)delta4"
                ),
                "clean_tradeoff_using_0_le_delta4_le_4ell": "4*ell+9*C8<=74844",
            },
        },
        "minimal_unfixed_mixed_motif": {
            "C8_definition": "sum_{r,U} binom(W_rU,2), W=F^T X Q",
            "interpretation": (
                "two N3 flag edges with one unmatched root r and one target triangle U; "
                "the two source triangles meet only in r"
            ),
            "order": 8,
            "W_entry_support": (
                "W_rU=0 if r lies in or is adjacent to U; otherwise W_rU is in {0,1,2,3}"
            ),
            "W_margins": {"row_sum": 84, "column_sum": 36},
            "norm_W_squared": "8316+2*C8",
            "representative": {
                "edges": [list(edge) for edge in sorted(c8_edges)],
                "edge_count": len(c8_edges),
                "degree_sequence": list(c8_degree),
                "global_least_mask": c8_global_mask,
                "Wave147_degree_cell_mask": c8_degree_mask,
                "automorphism_order": automorphisms,
                "marked_event_multiplicity_per_induced_copy": c8_events,
            },
            "frozen_integral_T0_pseudocount": x8[c8_degree_mask],
            "frozen_control_tradeoff_at_ell_zero": f"9*2442={tradeoff_lhs_at_frozen_c8_and_ell_zero}<74844",
            "larger_missing_term": (
                "ell synchronizes two X edges across the same pair of 7-flag point cells "
                "and generally reaches order ten"
            ),
        },
        "interlacing_boundary": {
            "compressions": ["H/7 on the 99-dimensional F-space", "K/3 on the 231-dimensional Q-space"],
            "trace_square_H_over_7": "(8316+4*ell)/49",
            "trace_square_K_over_3": 924,
            "conclusion": (
                "The fixed first three traces and these compressions do not contradict a "
                "12-regular triangle-free 693-vertex X; the fourth trace already contains c4(X)."
            ),
        },
        "conclusion": {
            "endpoint_excluded": False,
            "equitable_cover_subcase_excluded": True,
            "new_strict_collision_bound": "ell<=10761 (versus the partition-only maximum 12474)",
            "first_unfixed_trace_term": "c4(X), order at most eight",
            "first_unfixed_F_Q_synchronization": "C8=x8[44481136]",
            "first_unfixed_triangle_quotient_triangle_term": "tau_K, order nine",
            "zero_H_block_ruled_out_locally": False,
            "zero_H_block_control": "Wave205 t6_h1 has t_rs=6 and hence H_rs=0",
            "required_next_step": (
                "couple the order-eight C8 collision to the two-point collision ell/delta4, "
                "or control the endpoint labels around K-triangles; M^2=21M and scalar traces alone do neither"
            ),
        },
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
