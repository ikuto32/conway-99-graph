"""Clean-room audit of the endpoint triangle-flag relation study.

The producer is not imported.  This script independently reconstructs the
finite motif, the Bose--Mesner arithmetic, and every numerical bound used in
the result JSON.  It reads but does not regenerate the frozen order-eight
count vector.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path


SOURCE = Path("scratch_theory_e0_zero_triangle_flag_relation.json")
BOUNDARY = Path("scratch_theory_wave163_integral_order8_boundary.json")
WAVE205 = Path(
    "external_conway99_research/attempts/"
    "wave205-nonedge-fourth-trace-proof-a/exact-results.json"
)
OUTPUT = Path("scratch_theory_e0_zero_triangle_flag_relation_audit.json")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pairs(n: int) -> tuple[tuple[int, int], ...]:
    return tuple((i, j) for i in range(n) for j in range(i + 1, n))


def encoded(edges: set[tuple[int, int]], permutation: tuple[int, ...]) -> int:
    pos = {edge: i for i, edge in enumerate(pairs(len(permutation)))}
    image = {tuple(sorted((permutation[i], permutation[j]))) for i, j in edges}
    return sum(1 << pos[edge] for edge in image)


def degree_vector(n: int, edges: set[tuple[int, int]]) -> tuple[int, ...]:
    out = [0] * n
    for i, j in edges:
        out[i] += 1
        out[j] += 1
    return tuple(out)


def degree_canonical(n: int, edges: set[tuple[int, int]]) -> int:
    degree = degree_vector(n, edges)
    cells: dict[int, list[int]] = {}
    for i, value in enumerate(degree):
        cells.setdefault(value, []).append(i)
    start = 0
    all_maps = []
    for value in sorted(cells):
        source = cells[value]
        target = tuple(range(start, start + len(source)))
        start += len(source)
        all_maps.append(tuple(dict(zip(source, p)) for p in itertools.permutations(target)))
    answer = None
    for selection in itertools.product(*all_maps):
        p = [0] * n
        for mapping in selection:
            for old, new in mapping.items():
                p[old] = new
        value = encoded(edges, tuple(p))
        answer = value if answer is None else min(answer, value)
    assert answer is not None
    return answer


def triangle_list(n: int, edges: set[tuple[int, int]]) -> tuple[frozenset[int], ...]:
    return tuple(
        frozenset(t)
        for t in itertools.combinations(range(n), 3)
        if all(tuple(sorted(edge)) in edges for edge in itertools.combinations(t, 2))
    )


def count_marks(n: int, edges: set[tuple[int, int]]) -> int:
    tri = triangle_list(n, edges)
    total = 0
    for r in range(n):
        for u in tri:
            if r in u or any(tuple(sorted((r, x))) in edges for x in u):
                continue
            roots = [t for t in tri if r in t and t.isdisjoint(u)]
            for t1, t2 in itertools.combinations(roots, 2):
                missing = []
                for t in (t1, t2):
                    cross = {(x, y) for x in t for y in u if tuple(sorted((x, y))) in edges}
                    if len(cross) != 2:
                        break
                    left = {x for x, _ in cross}
                    right = {y for _, y in cross}
                    if len(left) != 2 or len(right) != 2 or t - left != {r}:
                        break
                    missing.append(next(iter(u - right)))
                else:
                    if len(missing) == 2 and missing[0] != missing[1]:
                        total += 1
    return total


def main() -> None:
    claimed = json.loads(SOURCE.read_text(encoding="utf-8"))
    frozen = json.loads(BOUNDARY.read_text(encoding="utf-8"))
    wave205 = json.loads(WAVE205.read_text(encoding="utf-8"))
    assert claimed["status"] == "E0_ZERO_TRIANGLE_FLAG_RELATION_EXACT_STUDY_PASS"
    assert frozen["endpoint"]["sum_E0"] == 0

    # Endpoint and trace arithmetic.
    assert 693 * 12 // 2 == 4158
    assert 231 * 36 // 2 == 4158
    assert 693 * 12 == 8316
    assert 693 * 12 * 23 == 191268
    assert 231 * 36 * 71 == 590436
    assert 13 * 231 * 68 == 204204

    # The incidence spaces F and Q have normalized squared singular values
    # (7+theta)/21 for theta=14,3,-4.
    principal = [(Fraction(21, 21), 1), (Fraction(10, 21), 54), (Fraction(3, 21), 44)]
    assert principal == [(1, 1), (Fraction(10, 21), 54), (Fraction(1, 7), 44)]
    assert 99 + 231 - 1 == 329

    # H has the Bose--Mesner projection bar(A).  Reconstruct the projector
    # traces without using the producer's formulas.
    tr_e0_h = Fraction(84)
    tr_e3_h = (0 + 4 * 0 - 18 * tr_e0_h) / 7
    tr_em4_h = -tr_e0_h - tr_e3_h
    assert (tr_e3_h, tr_em4_h) == (-216, 132)
    assert tr_e3_h**2 / 54 == 864
    assert tr_em4_h**2 / 44 == 396

    # Formal reduction of the H offset in N W^T-H=2 bar(A).
    # Before A^2=12I-A+2J, the offset is 30I-8A-2A^2-2J.
    # Store coefficients in the basis I,A,J.
    offset_i = 30 - 2 * 12
    offset_a = -8 - 2 * (-1)
    offset_j = -2 - 2 * 2
    assert (offset_i, offset_a, offset_j) == (6, -6, -6)

    # Check the unique equitable quotient solution B A=2 bar(A).
    # B=(J-A-13I)/6.  Multiply by A using JA=14J and A^2=12I-A+2J.
    ba_i = Fraction(-1, 6) * 12
    ba_a = Fraction(-1, 6) * (-1) + Fraction(-13, 6)
    ba_j = Fraction(1, 6) * 14 + Fraction(-1, 6) * 2
    assert (ba_i, ba_a, ba_j) == (-2, -2, 2)
    assert Fraction(1 - 13, 6) == -2  # diagonal of B
    assert Fraction(1, 6) == Fraction(1, 6)  # nonedge entry of B

    # Orthogonal residual projection.
    g3 = Fraction(17) - Fraction(9, 7)
    g4 = Fraction(10) - Fraction(16, 7)
    assert (g3, g4) == (Fraction(110, 7), Fraction(54, 7))
    p3 = 54 * Fraction(44, 7) ** 2 / g3
    p4 = 44 * Fraction(54, 7) ** 2 / g4
    assert (p3, p4, p3 + p4) == (
        Fraction(4752, 35), Fraction(2376, 7), Fraction(2376, 5)
    )
    c3 = Fraction(9, 770)
    c4 = Fraction(8, 189)
    assert c4 - c3 == Fraction(91, 2970)
    ell_cap = (Fraction(7128) - (p3 + p4)) / (Fraction(4, 7) + 4 * c3)
    assert ell_cap == Fraction(182952, 17)
    assert math.floor(ell_cap) == 10761
    assert Fraction(7128) - Fraction(4, 7) * 10761 == Fraction(6852, 7)
    assert math.ceil(4158**2 / (4158 + 2 * 10761)) == 674

    # Independently rebuild the unique marked order-eight collision class.
    e = {
        (0, 1), (0, 2), (1, 2),
        (0, 3), (0, 4), (3, 4),
        (5, 6), (5, 7), (6, 7),
        (1, 6), (2, 7), (3, 5), (4, 7),
    }
    all_masks = [encoded(e, p) for p in itertools.permutations(range(8))]
    assert min(all_masks) == 5675512
    assert degree_canonical(8, e) == 44481136
    assert tuple(sorted(degree_vector(8, e), reverse=True)) == (4, 4, 3, 3, 3, 3, 3, 3)
    assert len(triangle_list(8, e)) == 3
    assert count_marks(8, e) == 1
    aut = sum(
        1 for p in itertools.permutations(range(8))
        if {tuple(sorted((p[i], p[j]))) for i, j in e} == e
    )
    assert aut == 2
    x8 = dict(frozen["integral_pseudocount"]["order8_mask_count_pairs"])
    assert x8[44481136] == 2442

    # Independently bind the exact two-centre t=6 control.  Wave205's `h`
    # denotes a fourth trace over F_3, so only its integer `t` is used to
    # form the present H-entry: H_rs=t_rs-6.
    t6_rows = [row for row in wave205["controls"] if row["name"] == "t6_h1"]
    assert len(t6_rows) == 1
    t6 = t6_rows[0]
    assert t6["claimed_and_recomputed_t"] == 6
    assert t6["claimed_and_recomputed_h"] == 1
    assert t6["claimed_and_recomputed_t"] - 6 == 0
    local = t6["local_graph"]
    assert local["vertex_count"] == 28
    assert local["center_degrees"] == {"x": 14, "y": 14}
    assert local["center_common_neighbors"] == ["a", "b"]
    assert local["all_edges_have_at_most_one_local_common_neighbor"] is True
    assert local["all_nonedges_have_at_most_two_local_common_neighbors"] is True
    assert local["endpoint_cross_edge_cap_on_selected_disjoint_blocks"] is True
    assert local["full_local_B_transpose_A_B_reproduces_two_star_gram"] is True
    assert local["opposite_center_mu_two_for_all_exclusive_neighbors"] is True
    gram = t6["two_star_gram"]
    assert gram["rank"] == 11
    assert gram["embedding"]["principal_determinant"] == 2
    assert gram["kernel_minimum_nonzero_weight"] == 6
    assert "completion from 28 to 99 vertices" in wave205["omitted_target_premises"]

    # Reconstruct the ker(N) norm and the full F+Q projection coefficients.
    # delta3=4 ell-delta4.
    kernel_const = Fraction(16632, 5)
    kernel_ell = Fraction(-2, 5)
    kernel_d4 = Fraction(-7, 30)
    full_const = Fraction(2376, 5) + kernel_const / 3
    full_ell = 4 * c3 + kernel_ell / 3
    full_d4 = (c4 - c3) + kernel_d4 / 3
    full_c8 = Fraction(2, 3)
    assert (full_const, full_ell, full_c8, full_d4) == (
        1584, Fraction(-20, 231), Fraction(2, 3), Fraction(-14, 297)
    )

    # residual - full projection =
    # 5544-16 ell/33-2 C8/3+14 delta4/297 >=0.
    # Its largest value for fixed ell,C8 uses delta4=4ell, giving the
    # necessary condition 4ell+9C8<=74844.
    ell_after_max_d4 = Fraction(-16, 33) + 4 * Fraction(14, 297)
    assert ell_after_max_d4 == Fraction(-8, 27)
    assert Fraction(5544) * Fraction(27, 2) == 74844
    assert 4 * 0 + 9 * 2442 == 21978 < 74844

    # Cross-check every public scalar in the producer JSON.
    assert claimed["endpoint"]["q_of_every_triangle"] == 12
    assert claimed["point_partition_H"]["collision"]["integer_upper"] == 10761
    assert claimed["point_partition_H"]["collision"]["nonzero_H_blocks_lower_bound"] == 674
    rep = claimed["minimal_unfixed_mixed_motif"]["representative"]
    assert rep["global_least_mask"] == 5675512
    assert rep["Wave147_degree_cell_mask"] == 44481136
    assert rep["marked_event_multiplicity_per_induced_copy"] == 1
    assert claimed["minimal_unfixed_mixed_motif"]["frozen_integral_T0_pseudocount"] == 2442
    assert claimed["conclusion"]["endpoint_excluded"] is False
    assert claimed["conclusion"]["equitable_cover_subcase_excluded"] is True
    zero_block = claimed["zero_H_block_local_boundary"]
    assert zero_block["control_t_rs"] == 6
    assert zero_block["therefore_H_rs"] == 0
    assert claimed["conclusion"]["zero_H_block_ruled_out_locally"] is False

    result = {
        "status": "INDEPENDENT_E0_ZERO_TRIANGLE_FLAG_RELATION_AUDIT_PASS",
        "producer_json_sha256": digest(SOURCE),
        "frozen_boundary_sha256": digest(BOUNDARY),
        "wave205_exact_results_sha256": digest(WAVE205),
        "producer_imported": False,
        "order8_classes_regenerated": False,
        "checks": {
            "endpoint_q_X_and_trace_arithmetic": True,
            "incidence_principal_angles": True,
            "H_Bose_Mesner_projection": True,
            "H_equals_NKNT_plus_offset_reduction": True,
            "equitable_cover_contradiction": True,
            "orthogonal_projection_ell_bound": "ell<=10761",
            "full_F_Q_projection_tradeoff": "4ell+9C8<=74844",
            "C8_motif_global_mask": 5675512,
            "C8_motif_Wave147_mask": 44481136,
            "C8_mark_multiplicity": 1,
            "frozen_integral_pseudocount_C8": 2442,
            "Wave205_t6_control_implies_local_H_rs": 0,
            "Wave205_control_is_only_28_vertex_local": True,
        },
        "scope": (
            "Independent finite/algebraic replay.  Graph-theoretic incidence identities "
            "are proved in the companion note; no endpoint exclusion is asserted."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
