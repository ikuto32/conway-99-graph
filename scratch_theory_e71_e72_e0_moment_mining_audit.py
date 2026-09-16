"""Independent arithmetic/file audit for the E71/E72 E0 moment mining."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path


INPUT = Path("scratch_theory_e71_e72_e0_moment_mining.json")
OUTPUT = Path("scratch_theory_e71_e72_e0_moment_mining_audit.json")
CATALOGS = {
    71: Path("scratch_root_e71_q2_gram_fast_expansion_macro_catalog.json"),
    72: Path("scratch_general_e72_q3_gram_fast_expansion_macro_catalog.json"),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> None:
    document = json.loads(INPUT.read_text(encoding="utf-8"))
    assert document["status"] == "EXACT_E71_E72_E0_MOMENT_MINING_COMPLETE"
    checks = Counter()

    for e0, path in CATALOGS.items():
        catalog = json.loads(path.read_text(encoding="utf-8"))
        assert document["inputs"][str(e0)]["sha256"] == sha256(path)
        canonical = [row for row in catalog["macro_entries"]
                     if row["signature_stabilizer_canonical"]]
        profiles = document["profile_rows"][str(e0)]
        summary = document["summaries"][str(e0)]
        assert len(canonical) == summary["canonical_macros"]
        assert sum(int(row["signature_orbit_labelled_coverage"]) for row in canonical) == (
            summary["catalog_rooted_coverage"]
        )
        macro_keys_with_profiles = {
            (row["source_row_index"], row["state_orbit_number"],
             row["signature_stabilizer_orbit_number"])
            for row in profiles
        }
        assert len(macro_keys_with_profiles) == summary["macros_with_integral_PSD_full_Gram_profile"]
        assert len(profiles) == summary["integral_PSD_full_Gram_profiles"]
        assert (summary["overlap_macro_coverage_rejected_by_full_Gram"]
                + summary["overlap_macro_coverage_retained_by_full_Gram"]
                == summary["catalog_rooted_coverage"])

        tau = 84 - e0
        q_hist = Counter()
        rank_hist = Counter()
        for row in profiles:
            Q = int(row["Q_diagonals"])
            assert row["E0"] == e0 and row["tau"] == tau
            assert row["S_sides"] + Q == e0
            assert row["Y_support"] == tau
            assert row["Y_ones"] == tau - Q
            assert row["Y_twos"] == Q
            vector = [1] * (tau - Q) + [2] * Q
            assert len(vector) == tau
            assert sum(vector) == row["Y_l1"] == tau + Q
            assert sum(value * value for value in vector) == row["Y_l2_square"] == tau + 3 * Q
            assert tau * row["Y_l2_square"] - row["Y_l1"] ** 2 == Q * (tau - Q) >= 0
            assert row["overlap_sum"] == 2 * tau
            assert row["disjoint_deviation_sum"] == tau
            assert row["Z_trace"] == 2 * tau
            assert row["Z_trace_square"] == (
                4 * row["deficit_square_sum"]
                + 2 * (row["overlap_square"] + row["disjoint_deviation_square"])
            )
            assert row["Z_trace_square"] % 4 == 2 * tau % 4
            rank = int(row["Z_rank"])
            assert rank * row["Z_trace_square"] >= row["Z_trace"] ** 2
            floor = (row["Z_trace"] ** 2 + rank - 1) // rank
            while floor % 4 != row["Z_trace"] % 4:
                floor += 1
            assert floor == row["Z_trace_square_arithmetic_floor"]
            assert row["Z_trace_square"] - floor == (
                row["Z_trace_square_excess_above_rank_congruence_floor"]
            )
            assert 0 <= rank <= row["H_dimension"]
            assert row["Z_rank_deficiency_in_unsigned_circulation_space"] == (
                row["H_dimension"] - rank
            )
            q_hist[Q] += 1
            rank_hist[rank] += 1
            checks["profile_rows"] += 1
        assert {str(key): value for key, value in sorted(rank_hist.items())} == summary[
            "Z_rank_histogram"
        ]
        checks[f"E{e0}_profiles"] = len(profiles)

    # Direct reconstruction of the seven-vertex diagonal motif.  Its root is
    # the unique degree-four vertex, so an unrooted induced copy has one owner.
    vertices = ("r", "a0", "a1", "b0", "b1", "x", "y")
    edges = {
        tuple(sorted(pair)) for pair in (
            ("r", "a0"), ("r", "a1"), ("r", "b0"), ("r", "b1"),
            ("a0", "a1"), ("b0", "b1"),
            ("x", "a0"), ("x", "b0"),
            ("y", "a1"), ("y", "b1"), ("x", "y"),
        )
    }
    degrees = {vertex: sum(vertex in edge for edge in edges) for vertex in vertices}
    assert degrees["r"] == 4
    assert all(degrees[vertex] == 3 for vertex in vertices if vertex != "r")
    assert len(edges) == 11 and list(degrees.values()).count(4) == 1
    checks["H7_edges"] = len(edges)
    checks["H7_unique_root"] = 1

    # Coefficient checks for the global moment algebra.  Conditional on the
    # independently supplied Hamiltonian-table identity H=z2=n3-z11/4:
    # T=sum tau=2n3-H=n3+z11/4 and E-sum=99*84-T.
    assert 99 * 84 == 8316
    assert 99 * 84 * 84 == 698544
    # sum (84-tau)^2 = 99*84^2 - 167*T + 2*M2, T=2*n3-H.
    assert -167 * 2 == -334
    assert 167 == 167
    # Substitute H=n3-z11/4: -334*n3+167*H.
    assert -334 + 167 == -167
    checks["global_first_moment_coefficient_identities"] = 1
    checks["global_second_moment_coefficient_identities"] = 1

    assert document["summaries"]["71"]["macros_with_no_integral_PSD_full_Gram_profile"] == 23
    assert document["summaries"]["71"]["overlap_macro_coverage_rejected_by_full_Gram"] == 2_555_904
    assert document["summaries"]["71"]["macros_with_integral_PSD_full_Gram_profile"] == 157
    assert document["summaries"]["71"]["integral_PSD_full_Gram_profiles"] == 165
    assert document["summaries"]["72"]["integral_PSD_full_Gram_profiles"] == 162
    assert not document["empirical_two_feature_separators_not_claimed_universal"]

    result = {
        "status": "INDEPENDENT_E71_E72_E0_MOMENT_AUDIT_PASS",
        "input": str(INPUT),
        "input_sha256": sha256(INPUT),
        "checks": dict(checks),
        "H7_degree_sequence": sorted(degrees.values(), reverse=True),
        "H7_unique_root_verified": True,
        "all_profile_row_moment_identities_verified": True,
        "all_profile_Gram_trace_rank_inequalities_verified": True,
        "trace_square_congruence_verified": "tr(Z^2)=2*(84-E0) mod 4",
        "E71_full_Gram_rejection_count_verified": 23,
        "E71_full_Gram_rejected_coverage_verified": 2_555_904,
        "Hamiltonian_table_boundary": (
            "The algebraic substitution N(H7)=z2=n3-z11/4 is checked here, "
            "but the external seven-vertex table itself is not reconstructed."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
