"""Boundary audit for the missing lower coupling behind edge fibre collisions.

This script does not regenerate any graph classes.  It reads the frozen
Wave147/148 coefficient packages, checks whether the already-defined
order-eight shadow is directly present in their matrix-entry vectors, and
exhibits the exact order-nine selector which the desired lower coupling
needs.  It also records the sharp T=0 nonedge-collision marginal control.
"""

from __future__ import annotations

from fractions import Fraction
import gzip
import hashlib
import itertools
import json
import math
import os
from pathlib import Path


OUTPUT = Path("scratch_theory_edge_shadow_lower_coupling_boundary.json")
EDGE_MOMENTS = Path("scratch_theory_edge_fibre_codegree_moments.json")
SHADOW = Path("scratch_theory_root_yyt_order8_shadow.json")
AUGMENTED = Path("scratch_theory_root_yyt_augmented_relation.json")
ORDER8_BOUNDARY = Path("scratch_root_order8_e0_lower_bound_boundary.json")
GLOBAL_GRAM = Path("scratch_theory_global_fibre_block_gram.json")
WAVE161 = Path(
    "external_conway99_research/verification/"
    "wave161-four-root-cut-loop/exact-results.json"
)
WAVE162 = Path(
    "external_conway99_research/attempts/"
    "wave162-four-root-facial-reduction/facial-reduction-audit.json"
)
COEFFICIENTS = Path(
    "external_conway99_research/attempts/"
    "wave147-alternative-lane/coefficients.json.gz"
)
MARKED_ROWS = Path(
    "external_conway99_research/attempts/"
    "wave148-marked-order8/marked-rows.json.gz"
)


def atomic_json(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def edge_positions(order: int) -> dict[tuple[int, int], int]:
    return {pair: bit for bit, pair in enumerate(itertools.combinations(range(order), 2))}


def encode_mask(edges: set[tuple[int, int]], order: int) -> int:
    positions = edge_positions(order)
    return sum(1 << positions[tuple(sorted(edge))] for edge in edges)


def decode_mask(mask: int, order: int) -> set[tuple[int, int]]:
    return {
        pair for pair, bit in edge_positions(order).items() if (mask >> bit) & 1
    }


def induced_delete_mask(mask: int, order: int, deleted: int) -> int:
    vertices = [vertex for vertex in range(order) if vertex != deleted]
    relabel = {vertex: index for index, vertex in enumerate(vertices)}
    edges = {
        tuple(sorted((relabel[x], relabel[y])))
        for x, y in decode_mask(mask, order)
        if x != deleted and y != deleted
    }
    return encode_mask(edges, order - 1)


def pair_upper(mask: int, order: int) -> bool:
    edges = decode_mask(mask, order)
    for x, y in itertools.combinations(range(order), 2):
        common = sum(
            tuple(sorted((x, z))) in edges and tuple(sorted((y, z))) in edges
            for z in range(order) if z not in (x, y)
        )
        if common > (1 if (x, y) in edges else 2):
            return False
    return True


def extension_quartets() -> list[dict[str, object]]:
    # Vertices 0,1,2 and 3,4,5 are source triangles, 7--8 is the
    # target edge, and 6 is its unique triangle mate.  Deleting 6 freezes
    # the same order-eight shadow while bits 0--6 and 3--6 choose X/Pi.
    strict_base = {
        (0, 1), (0, 2), (1, 2),
        (3, 4), (3, 5), (4, 5),
        (7, 8), (6, 7), (6, 8),
        (1, 7), (2, 8), (4, 7), (5, 8),
    }
    result = []
    for root_relation in (0, 1):
        records = []
        deleted_masks = set()
        for left_bit, right_bit in itertools.product((0, 1), repeat=2):
            edges = set(strict_base)
            if root_relation:
                edges.add((0, 3))
            if left_bit:
                edges.add((0, 6))
            if right_bit:
                edges.add((3, 6))
            mask = encode_mask(edges, 9)
            assert pair_upper(mask, 9)
            deleted = induced_delete_mask(mask, 9, 6)
            deleted_masks.add(deleted)
            # Each root has one augmented occurrence and no double in this
            # local base.  It is selected precisely when its mate bit is one.
            selected_left = left_bit
            selected_right = right_bit
            records.append({
                "mate_to_source_root_bits": [left_bit, right_bit],
                "labelled_order9_mask": mask,
                "order8_mask_after_deleting_mate": deleted,
                "pair_upper_feasible": True,
                "augmented_entries_at_roots": [1, 1],
                "selected_root_indicators": [selected_left, selected_right],
                "selected_pair_indicator": selected_left * selected_right,
            })
        assert len(deleted_masks) == 1
        assert [record["selected_pair_indicator"] for record in records] == [0, 0, 0, 1]
        result.append({
            "source_root_relation": "edge" if root_relation else "nonedge",
            "fixed_order8_labelled_mask": next(iter(deleted_masks)),
            "completion_records": records,
        })
    return result


def proportional(left: dict[int, int], right: dict[int, int]) -> bool:
    if set(left) != set(right) or not left:
        return False
    first = next(iter(left))
    ratio = Fraction(left[first], right[first])
    return all(Fraction(left[index], right[index]) == ratio for index in left)


def inspect_frozen_coefficients(shadow: dict[str, object]) -> dict[str, object]:
    with gzip.open(COEFFICIENTS, "rt", encoding="utf-8") as handle:
        coefficients = json.load(handle)
    with gzip.open(MARKED_ROWS, "rt", encoding="utf-8") as handle:
        marked = json.load(handle)
    assert sha256(COEFFICIENTS) == shadow["frozen_inputs"]["wave147_coefficients_sha256"]
    assert sha256(MARKED_ROWS) == shadow["frozen_inputs"]["wave148_marked_rows_sha256"]

    result = {}
    for family_name in ("ordered_edge", "ordered_nonedge"):
        family = coefficients["families"][family_name]
        classes = family["class_coefficients"]
        keys = [(int(row["order"]), int(row["canonical_mask"])) for row in classes]
        assert len(keys) == 1207 and len(set(keys)) == 1207
        assert sum(order == 8 for order, _ in keys) == 916
        index_by_key = {key: index for index, key in enumerate(keys)}
        target_pairs = shadow["shadow_coefficients"][family_name][
            "nonzero_order8_coefficients"
        ]
        target = {
            index_by_key[(8, int(mask))]: int(value) for mask, value in target_pairs
        }

        entry_vectors: dict[tuple[int, int], dict[int, int]] = {}
        for class_index, record in enumerate(classes):
            for row, column, value in record["upper_entries"]:
                entry_vectors.setdefault((int(row), int(column)), {})[class_index] = int(value)
        exact_single_entries = [
            list(position) for position, vector in entry_vectors.items()
            if proportional(vector, target)
        ]
        touching = [
            (len(vector), position)
            for position, vector in entry_vectors.items()
            if set(vector) & set(target)
        ]
        assert touching and not exact_single_entries
        span = shadow["wave147_entry_span"][family_name]
        assert span["rank_after_appending_shadow_mod_prime"] == span["rank_mod_prime"] + 1
        result[family_name] = {
            "matrix_size": int(family["matrix_size"]),
            "class_coefficient_records": len(classes),
            "nonzero_matrix_entry_vectors": len(entry_vectors),
            "shadow_support_size": len(target),
            "individual_entry_proportional_to_shadow": False,
            "minimum_support_size_of_entry_touching_shadow": min(size for size, _ in touching),
            "modular_span_check": {
                "modulus": span["modulus"],
                "entry_span_rank": span["rank_mod_prime"],
                "rank_after_appending_shadow": span["rank_after_appending_shadow_mod_prime"],
                "residual_support": span["shadow_modular_residual_support"],
                "interpretation": (
                    "The shadow is outside the entry span over this finite field. "
                    "This is an obstruction, not by itself a rational nonspan certificate."
                ),
            },
        }

    assert marked["class_streams"]["8"]["count"] == 916
    return {
        "frozen_sha256_verified": True,
        "represented_class_orders": [5, 6, 7, 8],
        "pair_root_class_coefficient_records": 2414,
        "marked_vertex_rows": 944,
        "marked_ordered_pair_rows": 4440,
        "order9_or_higher_columns": 0,
        "families": result,
    }


def nonedge_boundary() -> dict[str, object]:
    n3 = 4158
    d_star = 0
    side_total = 2 * n3
    diagonal_total = 4158 - d_star
    # One exact integer marginal cell type for each of 4158 nonedges.
    side_per_nonedge = 2
    diagonal_per_nonedge = 1
    h = side_per_nonedge + diagonal_per_nonedge
    ss = 4158 * math.comb(side_per_nonedge, 2)
    sd = 4158 * side_per_nonedge * diagonal_per_nonedge
    dd = 4158 * math.comb(diagonal_per_nonedge, 2)
    assert side_total == 8316 and diagonal_total == 4158
    assert ss + sd + dd == 4158 * math.comb(h, 2) == 12474
    # It also obeys the summed root-group incidence categories.
    assert (h, 42 - 2 * h, 29 + h) == (3, 36, 32)
    assert 2 * h + (42 - 2 * h) == 42
    return {
        "general_type_totals": {
            "nonedge_side_fibre_incidences": "2n3",
            "nonedge_diagonal_fibre_incidences": "4158-D_*",
            "sum": "12474-T",
        },
        "T_zero_integer_marginal": {
            "per_nonedge": {"side_roots": side_per_nonedge,
                            "diagonal_roots": diagonal_per_nonedge,
                            "H_xy": h},
            "totals": {"side": side_total, "diagonal": diagonal_total},
            "collision_by_type": {"side_side": ss,
                                  "side_diagonal": sd,
                                  "diagonal_diagonal": dd,
                                  "total_K_nonedge": ss + sd + dd},
            "root_group_same_overlap_disjoint": [3, 36, 32],
            "scope": (
                "An exact integer first/second-moment control, not an assignment "
                "of roots to actual fibre partitions."
            ),
        },
        "generic_two_root_flag_union_orders": {
            "side_side": 10,
            "side_diagonal": 11,
            "diagonal_diagonal": 12,
            "explanation": (
                "A rooted side membership needs six vertices after its unique "
                "triangle mate is implicit, a diagonal membership needs seven, "
                "and the two flags share only the target pair."
            ),
        },
    }


def main() -> None:
    input_paths = (
        EDGE_MOMENTS, SHADOW, AUGMENTED, ORDER8_BOUNDARY, GLOBAL_GRAM,
        WAVE161, WAVE162, COEFFICIENTS, MARKED_ROWS,
    )
    inputs = {str(path): sha256(path) for path in input_paths}
    edge_moments = json.loads(EDGE_MOMENTS.read_text(encoding="utf-8"))
    shadow = json.loads(SHADOW.read_text(encoding="utf-8"))
    augmented = json.loads(AUGMENTED.read_text(encoding="utf-8"))
    boundary = json.loads(ORDER8_BOUNDARY.read_text(encoding="utf-8"))
    global_gram = json.loads(GLOBAL_GRAM.read_text(encoding="utf-8"))
    wave161 = json.loads(WAVE161.read_text(encoding="utf-8"))
    wave162 = json.loads(WAVE162.read_text(encoding="utf-8"))
    assert edge_moments["status"] == "EDGE_FIBRE_CODEGREE_MOMENT_DECOMPOSITION_AND_BOUNDARY_PASS"
    assert shadow["status"] == "YYT_ORDER8_SHADOW_AND_FROZEN_SPAN_AUDIT_COMPLETE"
    assert augmented["status"] == "AUGMENTED_FLAG_RELATION_AND_BAD_MATE_CAPACITY_PASS"
    assert boundary["status"] == "ORDER8_E0_POSITIVE_LOWER_BOUND_BOUNDARY_PASS"
    assert global_gram["status"] == "GLOBAL_FIBRE_BLOCK_GRAM_IDENTITIES_AND_BOUNDARY_COMPLETE"
    assert wave161["claim_label"] == "VERIFIED"
    assert wave162["claim_label"] == "DERIVED"
    exact_negative_directions = wave161["four_root_feedback"][
        "independently_replayed_negative_certificates"
    ]
    assert {record["root_mask"] for record in exact_negative_directions} == {3, 12}
    assert all(record["strictly_negative"] for record in exact_negative_directions)
    assert all(int(record["quadratic_value_scaled"]) < 0
               for record in exact_negative_directions)

    quartets = extension_quartets()
    coefficient_inspection = inspect_frozen_coefficients(shadow)
    nonedge = nonedge_boundary()

    # Selector polynomial on the only three admissible local states.
    # m is the mate-adjacency bit and y is the augmented entry.
    selector_states = []
    for mate, y in ((0, 1), (0, 2), (1, 1)):
        selected = mate * y + math.comb(y, 2)
        assert selected == (1 if (mate, y) in ((0, 2), (1, 1)) else 0)
        selector_states.append({"mate_bit": mate, "Yhat_entry": y,
                                "selected_fibre_edge_indicator": selected})

    endpoint = edge_moments["exact_boundary"]
    assert endpoint["T"] == endpoint["K_edge"] == endpoint["D_star"] == 0
    assert endpoint["n3"] == 4158 and endpoint["Q2"] == 33264
    assert Fraction(endpoint["beta_e"]) + Fraction(endpoint["beta_n"]) == 45738
    assert nonedge["T_zero_integer_marginal"]["collision_by_type"]["total_K_nonedge"] == 12474
    assert boundary["exact_rational_pseudowitness"]["sum_E0_from_affine_formula"] == "0"
    assert boundary["logical_consequence"]["boundary_value"] == "sum_r E0(r)=0"

    result = {
        "status": "EDGE_SHADOW_LOWER_COUPLING_EXACT_BOUNDARY_COMPLETE",
        "inputs": inputs,
        "frozen_resource_inspection": coefficient_inspection,
        "selected_set_formula": {
            "notation": (
                "For target edge e with triangle mate u, y=Yhat[r,e] and "
                "m=1[r~u]."
            ),
            "formula": "s[r,e]=m*y+binom(y,2)",
            "meaning": (
                "s=1 exactly for a prism root (m,y)=(1,1) or a doubled/"
                "diagonal root (m,y)=(0,2); it is zero for a good singleton (0,1)."
            ),
            "local_states": selector_states,
            "pair_product_expansion": (
                "s[r,e]s[s,e] needs mate-bit-weighted and doubled-entry mixed "
                "moments; beta_rel only sums y[r,e]y[s,e]."
            ),
        },
        "order9_nonmeasurability_witness": {
            "quartets": quartets,
            "conclusion": (
                "For both adjacent and nonadjacent source roots, the same "
                "labelled order-eight shadow has four pair-upper-feasible "
                "mate extensions with selected-pair values 0,0,0,1.  Hence "
                "no positive coefficientwise lower bound of the selected pair "
                "by the order-eight shadow exists."
            ),
            "scope": (
                "This is an exact arity/nonmeasurability certificate for the "
                "frozen order-eight system, not a proof that all four local "
                "extensions occur in a full SRG."
            ),
        },
        "nonedge_collision_double_count": nonedge,
        "frozen_relaxation_boundary": {
            "Wave159": {
                "n3": 4158, "z11": 16632, "Q2": 33264,
                "D_star": 0, "T": 0, "K_edge": 0,
                "beta_sum": 45738,
                "pair_root_and_marked_relaxation_passes": True,
            },
            "H0_and_nonedge_margin": {
                "H": "84I+3(J-I-A)",
                "eigenvalues": [336, 72, 93],
                "K_edge": 0,
                "K_nonedge": 12474,
            },
            "consequence": (
                "No positive T lower bound is a conic/linear consequence of "
                "the frozen pair-root order-eight matrices, marked rows, and "
                "the scalar identities audited here."
            ),
            "essential_limit": (
                "Wave159 is not feasible for the full four-root PSD blocks. "
                "Those negative directions remove this particular rational "
                "point but have not been assembled into an exact dual proof "
                "that excludes every T=0 point."
            ),
            "exact_full_four_root_point_separators": exact_negative_directions,
            "point_separation_is_not_a_T_bound": True,
            "wave162_status": (
                "No unconditional forced four-root face was found in the "
                "stored exact witness/cut audit; endpoint n3=4158 remains UNKNOWN."
            ),
        },
        "lane_conclusion": {
            "positive_T_lower_bound_obtained": False,
            "strict_n3_upper_bound_obtained": False,
            "exact_linear_combination_from_2414_matrices_obtained": False,
            "why": [
                "The needed selected statistic contains the ninth-vertex mate bits.",
                "The same order-eight shadow admits selected-pair values zero and one.",
                "Even the coarser beta shadow increases the stored entry-span rank modulo 1000003 in both root relations.",
                "The nonedge collision has generic two-root flag union order 10--12 and its exact T=0 integer margin is feasible.",
            ],
            "minimal_next_data": (
                "An order-eight-to-nine extension statistic carrying both mate "
                "bits and doubled-root status, together with a PSD/affine dual; "
                "or a two-root fibre-membership lift of orders 10--12 for nonedges."
            ),
        },
    }
    atomic_json(OUTPUT, result)
    print(json.dumps({
        "path": str(OUTPUT), "status": result["status"],
        "pair_root_records": coefficient_inspection["pair_root_class_coefficient_records"],
        "positive_T": False, "K_nonedge_boundary": 12474,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
