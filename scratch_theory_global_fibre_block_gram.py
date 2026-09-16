"""Exact global Gram identities for all rooted four-vertex fibres.

The rows of M are the 21 four-sets in the distance-two fibre partition at
each of 99 roots.  This script works only with consequences visible in
H=M^T M, plus two explicitly identified refinements (root grouping and the
side/diagonal motif roles).  It deliberately does not regenerate the
order-eight graph catalogue.
"""

from __future__ import annotations

from fractions import Fraction
import hashlib
import itertools
import json
import math
import os
from pathlib import Path


OUTPUT = Path("scratch_theory_global_fibre_block_gram.json")
ORDER8_BOUNDARY = Path("scratch_root_order8_e0_lower_bound_boundary.json")
ROOT_FLAG_AUDIT = Path("scratch_theory_root_flag_union_audit.json")

N = 99
K = 14
LAMBDA = 1
MU = 2
OUTER = 84
FIBRES_PER_ROOT = 21
FIBRE_SIZE = 4
BLOCKS = N * FIBRES_PER_ROOT
EDGES = N * K // 2
NONEDGES = N * (N - 1 - K) // 2
TOTAL_PAIR_INCIDENCES = BLOCKS * math.comb(FIBRE_SIZE, 2)
TRACE_H = N * OUTER
ROW_SUM_H = OUTER * FIBRE_SIZE
T_MAX = N * FIBRES_PER_ROOT * 4


def atomic_json(path, value):
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def add(x, y):
    return tuple(x[i] + y[i] for i in range(3))


def scale(c, x):
    return tuple(c * value for value in x)


def multiply(x, y):
    """Multiply coefficients in the SRG adjacency algebra basis I,A,J."""
    xi, xa, xj = x
    yi, ya, yj = y
    answer = (Fraction(0), Fraction(0), Fraction(0))
    answer = add(answer, (xi * yi, Fraction(0), Fraction(0)))
    answer = add(answer, (Fraction(0), xi * ya + xa * yi, Fraction(0)))
    answer = add(answer, (Fraction(0), Fraction(0), xi * yj + xj * yi))
    # A^2=(k-mu)I+(lambda-mu)A+mu J = 12I-A+2J.
    answer = add(answer, scale(xa * ya, (12, -1, 2)))
    # AJ=JA=kJ and J^2=nJ.
    answer = add(answer, (Fraction(0), Fraction(0), K * (xa * yj + xj * ya)))
    answer = add(answer, (Fraction(0), Fraction(0), N * xj * yj))
    return answer


def matrix_trace(x):
    # tr(I)=n, tr(A)=0, tr(J)=n.
    return N * (x[0] + x[2])


def minimum_square_sum(total, cells):
    quotient, remainder = divmod(total, cells)
    return cells * quotient * quotient + remainder * (2 * quotient + 1)


def minimum_choose2_sum(total, cells):
    quotient, remainder = divmod(total, cells)
    return cells * math.comb(quotient, 2) + remainder * quotient


def minimum_second_moment(total, cells):
    return minimum_square_sum(total, cells)


def maximum_bounded_second_moment(total, cells, bound):
    full, remainder = divmod(total, bound)
    assert full <= cells and (full < cells or remainder == 0)
    return full * bound * bound + remainder * remainder


def projection_energy(T):
    return (
        Fraction(336 * 336)
        + 54 * (Fraction(72) + Fraction(T, 189)) ** 2
        + 44 * (Fraction(93) - Fraction(T, 154)) ** 2
    )


def integer_energy_lower_bound(T):
    return N * OUTER * OUTER + 2 * (
        minimum_square_sum(T, EDGES)
        + minimum_square_sum(TOTAL_PAIR_INCIDENCES - T, NONEDGES)
    )


def collision_lower_bound(T):
    return (
        minimum_choose2_sum(T, EDGES)
        + minimum_choose2_sum(TOTAL_PAIR_INCIDENCES - T, NONEDGES)
    )


def row_integer_energy_lower_bound(T):
    """Minimise row-wise after fixing integer t_x and sum_x t_x=2T."""
    def row_cost(t):
        return minimum_square_sum(t, K) + minimum_square_sum(252 - t, OUTER)

    quotient, remainder = divmod(2 * T, N)
    return N * OUTER * OUTER + (
        (N - remainder) * row_cost(quotient)
        + remainder * row_cost(quotient + 1)
    )


def cyclic_T_zero_event_margin_control():
    """Explicit 99x4158 (126,3)-biregular event-incidence control.

    Columns are abstract nonedge-event labels, not graph nonedges with their
    endpoints.  This tests exactly the row/column marginal and second-moment
    layer, while intentionally not claiming a decomposition into fibre K4s.
    """
    row_degrees = [0] * N
    column_degrees = []
    for start in range(N):
        for offset in range(42):
            roots = {start, (start + 1) % N, (start + offset + 2) % N}
            assert len(roots) == 3
            column_degrees.append(len(roots))
            for root in roots:
                row_degrees[root] += 1
    assert len(column_degrees) == NONEDGES
    assert row_degrees == [126] * N
    assert column_degrees == [3] * NONEDGES
    return {
        "shape": [N, NONEDGES],
        "construction": (
            "column (i,j), i in Z_99, 0<=j<42, is incident with "
            "roots {i,i+1,i+j+2} mod 99"
        ),
        "row_degrees": {"value": 126, "multiplicity": 99},
        "column_degrees": {"value": 3, "multiplicity": NONEDGES},
        "ones": N * 126,
        "column_pair_collision": NONEDGES * math.comb(3, 2),
        "edge_event_rows_E0": {"value": 0, "multiplicity": 99},
        "sum_E0_squared": 0,
        "scope": (
            "Exact integer margin control only: columns are abstract and the "
            "126 selected pairs in a row are not asserted to be 21 K4 pair sets."
        ),
    }


def edge_mask(edges, order=4):
    value = 0
    for bit, pair in enumerate(itertools.combinations(range(order), 2)):
        if tuple(sorted(pair)) in {tuple(sorted(edge)) for edge in edges}:
            value |= 1 << bit
    return value


def canonical_mask(edges, order=4):
    best = None
    for permutation in itertools.permutations(range(order)):
        moved = [tuple(sorted((permutation[x], permutation[y]))) for x, y in edges]
        value = edge_mask(moved, order)
        best = value if best is None else min(best, value)
    return best


def motif_role_audit():
    # Triangular prism: top 0,1,2; bottom 3,4,5; vertical i--i+3.
    side_endpoint_count = [0] * 6
    rooted_side_count = [0] * 6
    side_events = []
    for root in range(6):
        rooted_side_count[root] += 1
        index = root % 3
        opposite_triangle = range(3, 6) if root < 3 else range(0, 3)
        internal_edge = tuple(vertex for vertex in opposite_triangle
                              if vertex % 3 != index)
        assert len(internal_edge) == 2
        side_events.append([root, *internal_edge])
        for endpoint in internal_edge:
            side_endpoint_count[endpoint] += 1

    # H_delta convention from scratch_theory_root_flag_union.md:
    # root,a0,a1,b0,b1,x,y = 0,...,6 and chord x--y.
    h_delta_edges = {
        (0, 1), (0, 2), (1, 2),
        (0, 3), (0, 4), (3, 4),
        (1, 5), (3, 5), (2, 6), (4, 6), (5, 6),
    }
    degrees = [sum(vertex in edge for edge in h_delta_edges) for vertex in range(7)]
    assert degrees == [4, 3, 3, 3, 3, 3, 3]
    return {
        "triangular_prism": {
            "rooted_side_event_count_by_vertex": rooted_side_count,
            "internal_edge_endpoint_count_by_vertex": side_endpoint_count,
            "root_and_internal_edge_events": side_events,
            "identity_per_copy": "t_x contribution=2 and S(x) contribution=1",
        },
        "H_delta": {
            "rooted_diagonal_event_count_by_vertex": [1, 0, 0, 0, 0, 0, 0],
            "diagonal_chord_endpoint_count_by_vertex": [0, 0, 0, 0, 0, 1, 1],
            "degree_sequence": degrees,
            "identity_per_copy": "one root role R and two chord-endpoint roles L",
        },
        "global_pointwise_identity": (
            "t_x=sum_{y~x}H_xy=2 P_x+L_x; "
            "E0(x)=P_x+R_x; hence t_x=2E0(x)+L_x-2R_x"
        ),
        "second_moment_expansion": (
            "sum_x t_x^2=4 sum_x E0(x)^2+sum_x(L_x-2R_x)^2+"
            "4 sum_x E0(x)(L_x-2R_x)"
        ),
        "second_moment_sign_obstruction": (
            "The final mixed term has no fixed sign; sum L=2 sum R only "
            "controls its first-moment analogue."
        ),
        "role_totals": "sum_x L_x=2 sum_x R_x, so sum_x t_x=2T",
    }


def root_group_projector_audit():
    """Finite K7 check behind the summed rooted fibre projector."""
    supports = tuple(itertools.combinations(range(7), 2))
    projector = []
    for first in supports:
        row = []
        for second in supports:
            if first == second:
                value = Fraction(2, 3)
            elif set(first) & set(second):
                value = Fraction(-2, 15)
            else:
                value = Fraction(1, 15)
            row.append(value)
        projector.append(row)
    square = [[sum(projector[i][k] * projector[k][j]
                   for k in range(21)) for j in range(21)] for i in range(21)]
    assert square == projector
    assert sum(projector[i][i] for i in range(21)) == 14
    assert all(sum(row) == 0 for row in projector)

    # A lifted fibre-constant unit vector has four equal coordinates, so the
    # 84x84 projector entries are one quarter of the K7-edge projector.
    lifted = {
        "same_fibre": Fraction(1, 6),
        "overlap_support": Fraction(-1, 30),
        "disjoint_support": Fraction(1, 60),
    }
    return {
        "K7_support_projector_rank": 14,
        "K7_support_projector_is_idempotent": True,
        "lifted_outer_entry_values": {
            key: str(value) for key, value in lifted.items()
        },
        "root_group_incidence_Gram": (
            "U^T U=126I-18A+42J; diagonal/edge/nonedge entries 168/24/42"
        ),
        "support_overlap_counts_given_h_equals_Hxy": {
            "edge_pair": "same=h, overlap=24-2h, disjoint=48+h",
            "nonedge_pair": "same=h, overlap=42-2h, disjoint=29+h",
        },
        "sharpened_codegree_caps": {"edge": 12, "nonedge": 21},
        "summed_projector": (
            "G=sum_r P_r=H/4-7I-(11/12)(J-I-A)"
        ),
        "summed_projector_invariants": {
            "PSD": True,
            "operator_interval": "0<=G<=84I",
            "G1": 0,
            "trace": 1386,
            "trace_operator_rank_lower_bound": 17,
            "trace_P3_G": "792+T/14",
            "trace_Pminus4_G": "594-T/14",
            "trace_G_square": "K_fb/4+33033/2+11T/12",
        },
        "primitive_pinching_consequence": (
            "K_fb>=12474-3T+T^2/1188"
        ),
        "comparison": (
            "This is exactly the continuous relation-wise collision Jensen "
            "bound and is never stronger than the integer cmin bound.  G "
            "still aggregates away the 99 root classes, so it adds no "
            "sum_r E0(r)^2 relation."
        ),
        "T_zero_control_G": {
            "matrix": "14I-(1/6)(J-I-A)",
            "eigenvalues": {"constant": 0, "A_3": "44/3", "A_minus4": "27/2"},
            "rank": 98,
            "PSD": True,
        },
    }
def main():
    boundary_raw = ORDER8_BOUNDARY.read_bytes()
    root_flag_raw = ROOT_FLAG_AUDIT.read_bytes()
    boundary = json.loads(boundary_raw)
    root_flag = json.loads(root_flag_raw)
    pseudo = boundary["exact_rational_pseudowitness"]
    assert int(pseudo["n3"]) == 4158
    assert int(pseudo["z11"]) == 16632
    assert 8316 - int(pseudo["n3"]) - int(pseudo["z11"]) // 4 == 0
    assert root_flag["status"] == "TRIANGLE_FLAG_UNION_IDENTITY_FINITE_AUDIT_PASS"

    assert BLOCKS == 2079
    assert EDGES == 693 and NONEDGES == 4158
    assert TOTAL_PAIR_INCIDENCES == 12474
    assert TRACE_H == 8316 and ROW_SUM_H == 336 and T_MAX == 8316

    I = (Fraction(1), Fraction(0), Fraction(0))
    P0 = (Fraction(0), Fraction(0), Fraction(1, 99))
    P3 = (Fraction(4, 7), Fraction(1, 7), Fraction(-2, 77))
    Pm4 = (Fraction(3, 7), Fraction(-1, 7), Fraction(1, 63))
    zero = (Fraction(0), Fraction(0), Fraction(0))
    assert add(add(P0, P3), Pm4) == I
    for projector in (P0, P3, Pm4):
        assert multiply(projector, projector) == projector
    assert multiply(P0, P3) == multiply(P0, Pm4) == multiply(P3, Pm4) == zero
    assert [matrix_trace(projector) for projector in (P0, P3, Pm4)] == [1, 54, 44]

    gap_values = []
    collision_values = []
    schur_P3_slacks_over_box = []
    schur_Pm4_slacks_over_box = []
    root_group_pinching_slacks_below_integer = []
    for T in range(T_MAX + 1):
        integer_energy = integer_energy_lower_bound(T)
        projected_energy = projection_energy(T)
        gap = Fraction(integer_energy) - projected_energy
        assert gap >= 0
        edge_q, edge_r = divmod(T, EDGES)
        non_q, non_r = divmod(TOTAL_PAIR_INCIDENCES - T, NONEDGES)
        expected_gap = 2 * (
            Fraction(edge_r * (EDGES - edge_r), EDGES)
            + Fraction(non_r * (NONEDGES - non_r), NONEDGES)
        )
        assert gap == expected_gap
        assert integer_energy == 723492 + 4 * collision_lower_bound(T)
        assert row_integer_energy_lower_bound(T) == integer_energy
        t_square_box_upper = maximum_bounded_second_moment(2 * T, N, 252)
        schur_P3_upper = Fraction(93731904 + 840 * T, 11)
        schur_Pm4_upper = Fraction(8555008) - Fraction(56 * T, 3)
        assert schur_P3_upper >= t_square_box_upper
        assert schur_Pm4_upper >= t_square_box_upper
        schur_P3_slacks_over_box.append(schur_P3_upper - t_square_box_upper)
        schur_Pm4_slacks_over_box.append(schur_Pm4_upper - t_square_box_upper)
        root_group_continuous_K = (
            Fraction(12474) - 3 * T + Fraction(T * T, 1188)
        )
        assert collision_lower_bound(T) >= root_group_continuous_K
        root_group_pinching_slacks_below_integer.append(
            collision_lower_bound(T) - root_group_continuous_K
        )
        gap_values.append(gap)
        collision_values.append(collision_lower_bound(T))
    zero_gap = [T for T, gap in enumerate(gap_values) if gap == 0]
    maximum_gap = max(gap_values)
    maximum_gap_T = [T for T, gap in enumerate(gap_values) if gap == maximum_gap]
    minimum_collision = min(collision_values)
    minimum_collision_T = [
        T for T, value in enumerate(collision_values) if value == minimum_collision
    ]
    assert zero_gap == [0, 4158, 8316]
    assert maximum_gap == 2376
    assert maximum_gap_T == [1782, 2376, 5940, 6534]
    assert minimum_collision == 10395
    assert minimum_collision_T == list(range(1386, 2080))
    assert min(schur_P3_slacks_over_box) == Fraction(54613440, 11)
    assert min(schur_Pm4_slacks_over_box) == 4208512
    assert min(root_group_pinching_slacks_below_integer) == 0
    assert max(root_group_pinching_slacks_below_integer) == 594

    event_margin_control = cyclic_T_zero_event_margin_control()
    assert event_margin_control["ones"] == TOTAL_PAIR_INCIDENCES
    assert event_margin_control["column_pair_collision"] == 12474
    root_group_projector = root_group_projector_audit()

    controls = []
    for T, edge_entry, nonedge_entry in (
        (0, 0, 3), (4158, 6, 2), (8316, 12, 1)
    ):
        eigenvalues = {
            "constant": 336,
            "A_eigenvalue_3": 84 + 3 * edge_entry - 4 * nonedge_entry,
            "A_eigenvalue_minus4": 84 - 4 * edge_entry + 3 * nonedge_entry,
        }
        assert min(eigenvalues.values()) > 0
        assert 84 + K * edge_entry + OUTER * nonedge_entry == 336
        assert EDGES * edge_entry == T
        assert NONEDGES * nonedge_entry == TOTAL_PAIR_INCIDENCES - T
        controls.append({
            "T": T,
            "matrix": f"84 I + {edge_entry} A + {nonedge_entry}(J-I-A)",
            "entries": {"diagonal": 84, "edge": edge_entry,
                        "nonedge": nonedge_entry},
            "eigenvalues": eigenvalues,
            "rank": 99,
            "integer_nonnegative_PSD": True,
            "binary_four_set_factorization_claimed": False,
        })

    samples = []
    for T in (0, 1, 693, 1386, 2079, 4158, 6534, 8316):
        q99, r99 = divmod(T, 99)
        samples.append({
            "T": T,
            "projector_trace_constant": "336",
            "projector_trace_A_minus4": str(Fraction(4092) - Fraction(2 * T, 7)),
            "projector_trace_A_3": str(Fraction(3888) + Fraction(2 * T, 7)),
            "Bose_Mesner_projection_energy": str(projection_energy(T)),
            "integer_entry_energy_lower_bound": integer_energy_lower_bound(T),
            "integer_rounding_gap": str(gap_values[T]),
            "fibre_block_pair_collision_lower_bound": collision_values[T],
            "sum_E0_square_integer_lower_bound": (
                (99 - r99) * q99 * q99 + r99 * (q99 + 1) ** 2
            ),
            "sum_E0_square_box_upper_bound": maximum_bounded_second_moment(
                T, 99, 84
            ),
        })

    four_root_masks = {
        "root_pair_nonedge_shared_pair_nonedge": canonical_mask([]),
        "exactly_one_of_root_pair_shared_pair_is_an_edge": canonical_mask([(0, 1)]),
        "root_pair_edge_shared_pair_edge": canonical_mask([(0, 1), (2, 3)]),
    }
    assert four_root_masks == {
        "root_pair_nonedge_shared_pair_nonedge": 0,
        "exactly_one_of_root_pair_shared_pair_is_an_edge": 1,
        "root_pair_edge_shared_pair_edge": 12,
    }
    assert canonical_mask([(0, 1), (0, 2)]) == 3

    result = {
        "status": "GLOBAL_FIBRE_BLOCK_GRAM_IDENTITIES_AND_BOUNDARY_COMPLETE",
        "inputs": {
            str(ORDER8_BOUNDARY): hashlib.sha256(boundary_raw).hexdigest().upper(),
            str(ROOT_FLAG_AUDIT): hashlib.sha256(root_flag_raw).hexdigest().upper(),
        },
        "parameters": {
            "srg": [N, K, LAMBDA, MU],
            "roots": N,
            "fibres_per_root": FIBRES_PER_ROOT,
            "fibre_size": FIBRE_SIZE,
            "incidence_matrix_shape": [BLOCKS, N],
            "graph_edges": EDGES,
            "graph_nonedges": NONEDGES,
        },
        "incidence_double_counts": {
            "M_row_weight": 4,
            "M_column_weight": 84,
            "H_diagonal": 84,
            "H_row_sum": 336,
            "trace_H": TRACE_H,
            "sum_all_H_entries": N * ROW_SUM_H,
            "unordered_off_diagonal_sum": TOTAL_PAIR_INCIDENCES,
            "unordered_edge_sum": "T=sum_r E0(r)",
            "unordered_nonedge_sum": "12474-T",
            "T_range_from_0_le_e_fibre_le_4": [0, T_MAX],
        },
        "primitive_projectors": {
            "A_spectrum": {"14": 1, "3": 54, "-4": 44},
            "P0_in_I_A_J": ["0", "0", "1/99"],
            "P3_in_I_A_J": ["4/7", "1/7", "-2/77"],
            "Pminus4_in_I_A_J": ["3/7", "-1/7", "1/63"],
            "trace_P0_H": "336",
            "trace_Pminus4_H": "4092-2T/7",
            "trace_P3_H": "3888+2T/7",
            "all_three_projector_traces_strictly_positive_on_T_0_to_8316": True,
        },
        "rank_and_pinching": {
            "operator_interval": "0 <= H <= 336 I",
            "rank_upper_bound": 99,
            "trace_operator_rank_lower_bound": 25,
            "Bose_Mesner_projection": (
                "Hbar=84I+(T/693)A+((12474-T)/4158)(J-I-A)"
            ),
            "Hbar_eigenvalues": {
                "constant": "336",
                "A_eigenvalue_3": "72+T/189",
                "A_eigenvalue_minus4": "93-T/154",
            },
            "pinching_identity": (
                "||H||_F^2=||Hbar||_F^2+||H-Hbar||_F^2; "
                "||Hbar||_F^2=336^2+54(72+T/189)^2+44(93-T/154)^2"
            ),
            "continuous_entry_Jensen_is_exactly_the_same_bound": True,
        },
        "root_group_summed_fibre_projector": root_group_projector,
        "integer_entry_energy": {
            "minimum_square_sum_definition": (
                "sqmin(S,m)=m q^2+r(2q+1), S=mq+r, 0<=r<m"
            ),
            "lower_bound": (
                "tr(H^2)>=99*84^2+2[sqmin(T,693)+"
                "sqmin(12474-T,4158)]"
            ),
            "rounding_gap_over_pinching": (
                "2[rE(693-rE)/693+rN(4158-rN)/4158]"
            ),
            "zero_rounding_gap_T": zero_gap,
            "maximum_rounding_gap": str(maximum_gap),
            "maximum_rounding_gap_T": maximum_gap_T,
            "binary_incidence_parity": (
                "diag(H)=84 is even, so H mod 2 is alternating; "
                "rank_F2(H) is even and at most 98; H1=0 mod 2"
            ),
            "crude_root_availability_caps": {
                "edge_pair": 72,
                "nonedge_pair": 71,
                "proof": (
                    "H_xy roots avoid both closed neighbourhoods; their union "
                    "has size 27 for x~y and 28 for x nonadjacent y"
                ),
                "T_zero_control_entries_respect_caps": True,
            },
            "rowwise_integer_refinement": {
                "t_x": "sum_{y~x}H_xy",
                "constraints": "sum_x t_x=2T and 0<=t_x<=252",
                "row_bound": (
                    "sum_x[84^2+sqmin(t_x,14)+sqmin(252-t_x,84)]"
                ),
                "minimum_over_integer_t_equals_global_integer_bound_for_all_T": True,
                "T_values_checked": T_MAX + 1,
            },
        },
        "fibre_block_pair_collision_inequality": {
            "definition": (
                "K_fb=sum_{x<y} binom(H_xy,2)="
                "sum_{distinct fibre rows B<C} binom(|B intersect C|,2)"
            ),
            "exact_energy_identity": "tr(H^2)=723492+4K_fb",
            "T_dependent_lower_bound": (
                "K_fb>=cmin(T,693)+cmin(12474-T,4158), where "
                "cmin(S,m)=m*binom(q,2)+r*q"
            ),
            "absolute_universal_lower_bound": minimum_collision,
            "equality_T_interval": [min(minimum_collision_T), max(minimum_collision_T)],
            "novelty_and_limit": (
                "This is an exact integer fibre-flag collision inequality, "
                "but it has no positive-T consequence."
            ),
        },
        "sum_E0_square": {
            "universal_integer_interval": (
                "sqmin(T,99) <= sum_r E0(r)^2 <= "
                "84^2 floor(T/84)+(T mod 84)^2"
            ),
            "edge_event_incidence_matrix": (
                "X[root,edge]=1 iff the edge lies in one root fibre; "
                "row sums are E0(root), column sums are H_xy on graph edges"
            ),
            "row_collision": (
                "sum_r E0(r)^2=T+2 sum_r binom(E0(r),2)"
            ),
            "column_collision": (
                "sum_{xy edge} H_xy^2=T+2 sum_{xy edge} binom(H_xy,2)"
            ),
            "not_determined_by_H": (
                "H records the column sums but loses the assignment of its "
                "2079 rows to 99 root groups; the two collision counts are distinct."
            ),
            "explicit_T_zero_integer_margin_control": event_margin_control,
        },
        "pointwise_edge_row_motif_bridge": {
            **motif_role_audit(),
            "edge_role_refinement": {
                "h_e": (
                    "For an edge e, H_e=p_e+d_e, where p_e counts prism "
                    "triangle-edge roles and d_e counts H_delta chord roles"
                ),
                "K_edge": "sum_{e edge} binom(H_e,2)",
                "K_nonedge": "sum_{f nonedge} binom(H_f,2)",
                "K_fb_split": "K_fb=K_edge+K_nonedge",
                "incident_edge_pair_term": (
                    "W_inc=sum_x sum_{e<f incident to x} H_e H_f >=0"
                ),
                "t_square_identity": (
                    "sum_x t_x^2=2T+4K_edge+2W_inc"
                ),
                "consequent_lower_bound": (
                    "sum_x t_x^2>=2T+4cmin(T,693), alongside "
                    "sum_x t_x^2>=sqmin(2T,99)"
                ),
                "why_K_fb_does_not_bound_E0": (
                    "K_nonedge is independent of the prism/chord root roles and "
                    "can carry the whole T=0 lower bound K_fb>=12474."
                ),
            },
            "Schur_projector_test": {
                "PSD_contractions": (
                    "B3=H o P3 and B-4=H o P-4 satisfy 0<=B<=84I"
                ),
                "row_sums": {
                    "B3": "432/11+t_x/7",
                    "Bminus4": "124/3-t_x/7",
                },
                "t_square_upper_bounds": [
                    "sum t_x^2 <= (93731904+840T)/11",
                    "sum t_x^2 <= 8555008-56T/3",
                ],
                "both_weaker_than_box_bound_for_every_T": True,
                "box_bound": (
                    "sum t_x^2<=252^2 floor(2T/252)+(2T mod 252)^2"
                ),
                "minimum_slack_over_box": {
                    "P3": str(min(schur_P3_slacks_over_box)),
                    "Pminus4": str(min(schur_Pm4_slacks_over_box)),
                },
                "H_Hadamard_H": (
                    "H o H is PSD, but its rowwise integer/Jensen lower bound "
                    "reduces exactly to the already recorded global energy bound"
                ),
            },
        },
        "n3_z11_substitution": {
            "T": "8316-n3-z11/4=6P+N(H_delta)",
            "trace_Pminus4_H": "1716+2n3/7+z11/14",
            "trace_P3_H": "6264-2n3/7-z11/14",
            "collision_inequality": (
                "K_fb>=cmin(8316-n3-z11/4,693)+"
                "cmin(4158+n3+z11/4,4158)"
            ),
            "known_order8_pseudowitness": {
                "n3": int(pseudo["n3"]),
                "z11": int(pseudo["z11"]),
                "T": 0,
                "prism_count": int(pseudo["prism_count"]),
                "H_delta_count": int(pseudo["H_delta_count"]),
            },
        },
        "four_root_connection": {
            "collision_configuration": (
                "Choose distinct fibre rows (r,F),(s,G) and a shared pair "
                "{x,y}.  Fibre membership forces rx,ry,sx,sy all nonedges."
            ),
            "canonical_unlabelled_root_masks": four_root_masks,
            "root_mask_3_can_occur_in_this_collision_family": False,
            "root_mask_12_occurs_exactly_when": (
                "r~s and x~y; it is the two-disjoint-edges four-root type"
            ),
            "important_scope": (
                "K_fb counts fibre-membership-enriched flags inside masks 0,1,12, "
                "not the raw four-root class counts.  Existing mask-12 covariance "
                "directions do not evaluate K_fb without a new explicit flag lift."
            ),
        },
        "integer_PSD_relation_algebra_controls": controls,
        "sample_values": samples,
        "boundary": {
            "positive_global_T_lower_bound_from_listed_H_constraints": False,
            "positive_pointwise_E0_lower_bound_from_H_alone": False,
            "T_zero_control": controls[0],
            "why": (
                "H0=84I+3(J-I-A) is integer, entrywise nonnegative, positive "
                "definite of rank 99, has row sum 336, the required relation "
                "sums and projector traces at T=0, and attains both pinching and "
                "integer energy equality.  The explicit cyclic (126,3)-"
                "biregular event-incidence control also realizes T=0, "
                "sum E0^2=0 and K_nonedge=12474 at the marginal layer."
            ),
            "essential_caveat": (
                "No binary 2079x99 row-weight-four factorization of H0 is claimed. "
                "A stronger result must use that factorization together with the "
                "99 root partitions or a lifted four-root/flag compatibility."
            ),
            "T_zero_binary_factorization_translation": {
                "H0_factorization": (
                    "A binary row-weight-four M with M^T M=H0 would be a "
                    "3-fold K4 decomposition of the complement graph: every "
                    "row is an independent 4-set of G and every nonedge pair "
                    "occurs in exactly three rows."
                ),
                "divisibility_checks": {
                    "blocks_from_edges": 3 * NONEDGES // 6,
                    "blocks_through_each_vertex": 3 * OUTER // 3,
                    "matches_required_shape": (
                        3 * NONEDGES // 6 == BLOCKS
                        and 3 * OUTER // 3 == OUTER
                    ),
                },
                "extra_root_partition_requirement": (
                    "The 2079 rows must additionally split into 99 labelled "
                    "classes of 21 disjoint blocks covering V minus the closed "
                    "neighbourhood of that root, with the correct two-triangle "
                    "fibre support.  Neither PSD nor H records this requirement."
                ),
            },
        },
    }
    atomic_json(OUTPUT, result)
    print(json.dumps({
        "path": str(OUTPUT),
        "status": result["status"],
        "collision_lower_bound": minimum_collision,
        "pinching_zero_gap_T": zero_gap,
        "positive_T_lower_bound": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
