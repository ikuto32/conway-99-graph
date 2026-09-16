"""Exact positive hull-witness audit; no hull producer or LP solver import.

Each used quartet is checked directly in all 21 residual coordinates. This
positive audit does not need to trust completeness of any enumerated hull.
"""

from collections import defaultdict
from fractions import Fraction as F
import itertools as it
import json
from pathlib import Path

import scratch_theory_e71_degree_moment_lp_audit as matrices


PROBE = Path("scratch_theory_e71_fibre_moment_hull_probe.json")
REMAINING = Path("scratch_theory_e71_fibre_moment_hull_remaining.json")
INVENTORY = Path("scratch_root_e71_theory_frontier_before_label_subset.json")
OUTPUT = Path("scratch_theory_e71_fibre_moment_hull_audit.json")


def check(entry, profile, record):
    exceptional, compression, gram = matrices.reconstruct(entry, profile)
    selected, coordinates = matrices.principal_coordinates(gram)
    internal = matrices.internal_degrees(entry, exceptional, compression)
    assert list(selected) == record["pivot_indices"]
    pairs = tuple(it.combinations_with_replacement(range(len(selected)), 2))
    assert list(map(list, pairs)) == record["moment_pairs"]
    required = tuple(4 * gram[selected[i]][selected[j]] for i, j in pairs)
    assert list(required) == record["target_moment"]
    assert record["status"] == "COMPLETE_FIBRE_MOMENT_HULL_MODEL"
    assert record["exact_Farkas_certificate"] is None
    certificate = record["exact_feasible_weights"]
    assert certificate is not None
    fibre_weights = [F(0)] * 21
    total_moment = [F(0)] * len(pairs)
    used_indexes = set()
    checked_rows = 0
    for index, encoded_weight in certificate["nonzero_weights"]:
        assert index not in used_indexes and 0 <= index < len(record["variables"])
        used_indexes.add(index)
        weight = F(encoded_weight)
        assert weight > 0
        source, choice_index = record["variables"][index]
        choice = record["fibre_options"][source][choice_index]
        pivots = choice["row_pivots"]
        assert len(pivots) == 4 and all(len(row) == len(selected) for row in pivots)
        full_rows = []
        for local, pivot in enumerate(pivots):
            assert all(type(value) is int for value in pivot)
            residual = [sum(pivot[i] * coordinates[i][j] for i in range(len(selected))) for j in range(21)]
            degrees = [(residual[j] + compression[source][j]) / 4 for j in range(21)]
            assert all(d.denominator == 1 and 0 <= d <= 4 for d in degrees)
            assert sum(degrees) == 12 and degrees[source] == internal[source][local]
            assert [residual[j] for j in selected] == pivot
            full_rows.append(residual)
            checked_rows += 1
        assert all(sum(row[j] for row in full_rows) == 0 for j in range(21))
        actual_moment = tuple(sum(row[i] * row[j] for row in pivots) for i, j in pairs)
        assert list(actual_moment) == choice["moment"]
        fibre_weights[source] += weight
        total_moment = [a + weight * b for a, b in zip(total_moment, actual_moment)]
    assert fibre_weights == [1] * 21
    assert total_moment == list(required)
    principal = [[4 * gram[i][j] for j in selected] for i in selected]
    lifted = matrices.product(matrices.product(list(zip(*coordinates)), principal), coordinates)
    assert lifted == [[4 * value for value in row] for row in gram]
    return {"key": record["key"], "parameter": record["parameter"], "coverage": record["coverage"],
            "exact_feasible_hull_witness": True, "positive_weights": len(used_indexes),
            "quartet_rows_checked_in_all_21_coordinates": checked_rows,
            "all_fibre_zero_sums_verified": True, "full_Gram_lift_verified": True,
            "is_source724_Q2_control": tuple(record["key"]) == (724, 1, 0)}


def main():
    probe, remaining, inventory = map(matrices.read, (PROBE, REMAINING, INVENTORY))
    for document in (probe, remaining):
        for path, wanted in document["inputs_sha256"].items():
            assert matrices.sha(Path(path)) == wanted, path
    catalog, mining = map(matrices.read, (matrices.CATALOG, matrices.MINING))
    entries = {matrices.macro_key(r): r for r in catalog["macro_entries"] if r["signature_stabilizer_canonical"]}
    profiles = {(matrices.macro_key(r), r["parameter"]): r for r in mining["profile_rows"]["71"]}
    records = remaining["rows"] + [r for r in probe["rows"] if r["key"] == [724, 1, 0]]
    assert len(records) == 72
    assert len({(tuple(r["key"]), r["parameter"]) for r in records}) == len(records)
    residual_keys = set(map(tuple, inventory["remaining_keys"]))
    assert len(residual_keys) == 65
    assert {tuple(r["key"]) for r in remaining["rows"]} == residual_keys
    matrices.ordinary_internal_theorem()
    matrices.fibre_incidence_geometry()
    verified = [check(entries[tuple(r["key"])], profiles[(tuple(r["key"]), r["parameter"])], r) for r in records]
    result = {"status": "INDEPENDENT_E71_FIBRE_MOMENT_HULL_FEASIBLE_WITNESS_AUDIT_PASS",
              "hull_producer_imported": False, "LP_solver_used": False,
              "inputs_sha256": {str(p): matrices.sha(p) for p in (PROBE, REMAINING, INVENTORY, matrices.CATALOG, matrices.MINING, Path(matrices.__file__))},
              "verified_profiles": len(verified), "residual_profiles": 71, "residual_macros": 65,
              "source724_Q2_control_profiles": 1, "new_excluded_coverage": 0,
              "rows": verified,
              "scope": "Direct verification of every positively weighted quartet, nonnegative rational fibre weights, and full moment equality. No completeness claim about unused enumerated options is needed for these feasible controls. No adjacency graph is claimed.",
              "submission_txt_written": False}
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "verified_profiles": 72, "residual_macros": 65, "new_excluded_coverage": 0}, sort_keys=True))


if __name__ == "__main__":
    main()
