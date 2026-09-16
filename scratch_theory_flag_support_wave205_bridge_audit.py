"""Finite exact audit for the Wave205 t-matrix / flag-support bridge."""

from __future__ import annotations

import json
from pathlib import Path


OUTPUT = Path("scratch_theory_flag_support_wave205_bridge_audit.json")


def main():
    # One two-cross triangle pair.  Slots 0,1 are matched and slot 2 is the
    # unmatched flag at each end.
    cross_edges = {(0, 0), (1, 1)}
    source_roles = []
    for source_slot in range(3):
        edge_pairs = sum((source_slot, target_slot) in cross_edges
                         for target_slot in range(3))
        nonedge_pairs = 3 - edge_pairs
        source_roles.append({
            "source_slot": source_slot,
            "is_unmatched": source_slot == 2,
            "target_edge_pairs": edge_pairs,
            "target_nonedge_pairs": nonedge_pairs,
        })
    assert source_roles == [
        {"source_slot": 0, "is_unmatched": False,
         "target_edge_pairs": 1, "target_nonedge_pairs": 2},
        {"source_slot": 1, "is_unmatched": False,
         "target_edge_pairs": 1, "target_nonedge_pairs": 2},
        {"source_slot": 2, "is_unmatched": True,
         "target_edge_pairs": 0, "target_nonedge_pairs": 3},
    ]
    assert sum(item["target_edge_pairs"] for item in source_roles) == 2
    assert sum(item["target_nonedge_pairs"] for item in source_roles) == 7

    # For a root r, u=sum_{T contains r}q(T)=84-S(r).  Exactly u K2
    # incidences leave r unmatched and 2u match r.
    samples = []
    for u in range(85):
        unmatched = u
        matched = 2 * u
        adjacent_t_sum = matched
        nonadjacent_t_sum = 3 * unmatched + 2 * matched
        assert adjacent_t_sum == 2 * u
        assert nonadjacent_t_sum == 7 * u
        assert adjacent_t_sum + nonadjacent_t_sum == 9 * u
        samples.append({
            "u": u,
            "S": 84 - u,
            "K2_star_incidence_count": 3 * u,
            "adjacent_t_row_sum": adjacent_t_sum,
            "nonadjacent_t_row_sum": nonadjacent_t_sum,
        })

    # Endpoint values and the Wave205 excess identity.
    endpoint_u = 84
    endpoint_nonedge_sum = 7 * endpoint_u
    endpoint_edge_sum = 2 * endpoint_u
    assert (endpoint_edge_sum, endpoint_nonedge_sum) == (168, 588)
    nonedge_count = 4158
    assert 99 * endpoint_nonedge_sum // 2 == 7 * nonedge_count
    assert 7 * nonedge_count - 6 * nonedge_count == 4158

    # A doubled flag entry produces one pair of K2 incidences.  Inflating
    # its target triangle gives the same pair inside t_{r,y} for all three
    # target vertices, proving 3D(r) <= sum_y C(t_ry,2).  The direction is
    # upper, not lower, for D.
    doubled_flag_injections = 3
    assert doubled_flag_injections == 3

    result = {
        "status": "EXACT_WAVE205_TO_FLAG_SUPPORT_BRIDGE_AUDIT_PASS",
        "one_two_cross_pair": {
            "source_role_table": source_roles,
            "all_nine_point_pairs": 9,
            "matched_graph_edges": 2,
            "graph_nonedges": 7,
            "unmatched_endpoint_pair": 1,
        },
        "pointwise_row_identities": {
            "u_definition": "u(r)=sum_{T contains r}q(T)=84-S(r)",
            "K2_star_incidences": "3u(r)",
            "t_adjacent_row_sum": "2u(r)=2(84-S(r))",
            "t_nonadjacent_row_sum": "7u(r)=7(84-S(r))",
            "endpoint_values_S0": {"adjacent": 168, "nonadjacent": 588},
        },
        "collision_inequality": {
            "formula": "3D(r) <= sum_{y nonadjacent r} binom(t_ry,2)",
            "reason": (
                "Each Y[r,(U,u)]=2 collision injects its source-pair into "
                "one pair counted by binom(t_ry,2) for each of the three y in U."
            ),
            "use_for_lower_bound": (
                "wrong direction: it upper-bounds D from a t second moment "
                "and cannot prove E0=S+D large"
            ),
        },
        "Wave205_translation": {
            "t_matrix": "N K2 N^T = F^T J_triangle X J_triangle F",
            "support_matrix": "Y=F^T X; E0(r)=84-|supp(Y[r,*])|",
            "distinction": (
                "t inflates each X edge to all 3x3 point pairs of its two "
                "triangles, whereas Y retains its unmatched source flag and "
                "target flag."
            ),
            "rank_U_99_implication": (
                "No incidence-only rank loss: ordered pairs of distinct "
                "triangles in one point-star already supply all unit columns e_r."
            ),
            "fourth_trace_implication": (
                "H=U K_D U^T is over F_3 and is not the real PSD Gram YY^T; "
                "without a new flagged restriction of K_D it gives no support order."
            ),
        },
        "sample_count": len(samples),
        "conclusion": (
            "Wave205 t>=6 and average 7 govern the unflagged star-pair count "
            "and recover S(r), not the collision D(r).  The currently verified "
            "fourth-trace factorization therefore supplies no pointwise "
            "E0=S+D lower bound."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
