"""Independent exact replay of the six source150 feasible LP controls.

Uses only the independently audited reconstruction module, never the LP
producer, affine producer, their base module, NumPy, SciPy, or a solver.
"""

from collections import Counter
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path

import scratch_theory_e71_degree_moment_lp_audit as independent


CATALOG = Path("scratch_general_e72_q3_gram_fast_expansion_macro_catalog.json")
INVENTORY = Path("scratch_root_e72_complete_coverage_inventory_before_m10.json")
CERTIFICATE = Path("scratch_theory_e72_source150_degree_moment_applicability.json")
OUTPUT = Path("scratch_theory_e72_source150_degree_moment_applicability_audit.json")


def main():
    certificate, catalog, mining, inventory = map(independent.read, (CERTIFICATE, CATALOG, independent.MINING, INVENTORY))
    for path, wanted in certificate["inputs_sha256"].items():
        assert independent.sha(Path(path)) == wanted
    independent.ordinary_internal_theorem()
    independent.fibre_incidence_geometry()
    keys = {(150, *r["macro"]) for r in inventory["source150"]["macro_rows"] if r["status"] == "OPEN"}
    entries = {independent.macro_key(r): r for r in catalog["macro_entries"] if r["signature_stabilizer_canonical"]}
    profiles = {(independent.macro_key(r), r["parameter"]): r for r in mining["profile_rows"]["72"]}
    assert {tuple(r["key"]) for r in certificate["rows"]} == keys
    assert len(keys) == len(certificate["rows"]) == 6
    rows = []
    for stored in certificate["rows"]:
        key = tuple(stored["key"])
        entry, profile = entries[key], profiles[(key, stored["parameter"])]
        exceptional, compression, gram = independent.reconstruct(entry, profile)
        pivots, coordinates = independent.principal_coordinates(gram)
        raw = independent.all_raw_domains(compression, pivots, coordinates)
        internal = independent.internal_degrees(entry, exceptional, compression)
        rank = len(pivots)
        assert rank == stored["rank_K4"] == 2
        groups = [(source, degree, count) for source in range(21)
                  for degree, count in sorted(Counter(internal[source]).items())]
        pairs = tuple(itertools.combinations_with_replacement(range(rank), 2))
        columns, variables = [], []
        for group_index, (source, degree, _) in enumerate(groups):
            for pivot, degrees in raw[source]:
                if degrees[source] != degree:
                    continue
                column = [int(i == group_index) for i in range(len(groups))]
                column.extend(pivot[j] if fibre == source else 0 for fibre in range(21) for j in range(rank))
                column.extend(pivot[i] * pivot[j] for i, j in pairs)
                columns.append(column)
                variables.append({"source": source, "internal_degree": degree, "pivot": list(pivot)})
        matrix = list(map(list, zip(*columns)))
        target = [count for _, _, count in groups] + [0] * (21 * rank)
        target.extend(4 * gram[pivots[i]][pivots[j]] for i, j in pairs)
        metadata = stored["model"]
        model_hash = hashlib.sha256(json.dumps([matrix, target], separators=(",", ":")).encode()).hexdigest()
        assert model_hash == metadata["matrix_sha256"]
        assert variables == metadata["variables"]
        assert sum(map(len, raw)) == stored["raw_rows"] == metadata["raw_row_patterns"]
        witness = stored["exact_feasible_witness"]
        assert witness is not None and stored["exact_infeasible_certificate"] is None
        weights = [Fraction(0)] * len(variables)
        indexes = set()
        for index, value in witness["nonzero_weights"]:
            assert index not in indexes and 0 <= index < len(weights)
            indexes.add(index)
            weights[index] = Fraction(value)
        assert all(value >= 0 for value in weights)
        assert [sum(a * b for a, b in zip(row, weights)) for row in matrix] == target
        assert int(entry["signature_orbit_labelled_coverage"]) == stored["coverage"]
        rows.append({"key": list(key), "coverage": stored["coverage"], "raw_rows": sum(map(len, raw)),
                     "equations_replayed": len(target), "variables_reconstructed": len(variables),
                     "nonzero_rational_weights": len(indexes), "matrix_sha256": model_hash,
                     "exact_primal_witness_pass": True})
    assert sum(r["coverage"] for r in rows) == 40960
    result = {"status": "INDEPENDENT_E72_SOURCE150_DEGREE_MOMENT_FEASIBLE_CONTROLS_AUDIT_PASS",
              "LP_or_affine_producer_imported": False, "solver_used": False,
              "inputs_sha256": {str(p): independent.sha(p) for p in (CATALOG, independent.MINING, INVENTORY, CERTIFICATE, Path(independent.__file__))},
              "rows": rows, "exact_feasible_profiles": 6, "excluded_coverage": 0,
              "scope": "Only six historical source150 macro-level convex degree-moment models selected from the frozen before_m10 inventory snapshot, not the current open inventory. Rational feasible weights are not graph completions and do not certify every fixed overlap branch feasible. No graph-search process was started, stopped, or restarted.",
              "submission_txt_written": False}
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "exact_feasible_profiles": 6, "excluded_coverage": 0}, sort_keys=True))


if __name__ == "__main__":
    main()
