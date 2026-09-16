"""Six-profile applicability check; never launches an E72 graph search."""

from fractions import Fraction
import json
from pathlib import Path

import scratch_theory_e71_degree_moment_lp_probe as lp
import scratch_theory_e71_degree_moment_affine_probe as affine


CATALOG = Path("scratch_general_e72_q3_gram_fast_expansion_macro_catalog.json")
INVENTORY = Path("scratch_root_e72_complete_coverage_inventory_before_m10.json")
OUTPUT = Path("scratch_theory_e72_source150_degree_moment_applicability.json")


def main():
    catalog, mining, inventory = map(lp.base.read, (CATALOG, lp.base.MINING, INVENTORY))
    wanted = {(150, *row["macro"]) for row in inventory["source150"]["macro_rows"] if row["status"] == "OPEN"}
    assert wanted == {(150, 0, 3), (150, 1, 0), (150, 3, 3), (150, 9, 0), (150, 10, 0), (150, 11, 0)}
    entries = {lp.base.key(r): r for r in catalog["macro_entries"] if r["signature_stabilizer_canonical"]}
    profiles = [r for r in mining["profile_rows"]["72"] if lp.base.key(r) in wanted]
    assert len(profiles) == len(wanted) == 6
    records = []
    for profile in profiles:
        key = lp.base.key(profile)
        entry = entries[key]
        aff = affine.analyze(entry, profile)
        matrix, target, metadata = lp.model(entry, profile)
        answer = lp.linprog(lp.np.zeros(len(matrix[0])), A_eq=lp.np.asarray(matrix, dtype=float),
                            b_eq=lp.np.asarray(target, dtype=float), bounds=(0, None), method="highs")
        certificate = lp.farkas(matrix, target) if answer.status == 2 else None
        witness = None
        if answer.success:
            for cap in (1000, 100000, 10000000):
                values = [Fraction(float(v)).limit_denominator(cap) for v in answer.x]
                if all(v >= 0 for v in values) and all(sum(a * b for a, b in zip(row, values)) == rhs for row, rhs in zip(matrix, target)):
                    witness = {"denominator_cap": cap, "nonzero_weights": [[i, str(v)] for i, v in enumerate(values) if v],
                               "exact_nonnegativity_and_all_equations_checked": True}
                    break
        records.append({"key": list(key), "coverage": int(entry["signature_orbit_labelled_coverage"]),
                        "parameter": profile["parameter"], "rank_K4": metadata["rank_K4"],
                        "raw_rows": metadata["raw_row_patterns"], "affine_inconsistent": aff["affine_inconsistent"],
                        "LP_status": int(answer.status), "exact_infeasible_certificate": certificate,
                        "exact_feasible_witness": witness, "model": metadata})
    result = {"status": "E72_SOURCE150_SIX_PROFILE_DEGREE_MOMENT_APPLICABILITY_COMPLETE",
              "inputs_sha256": {str(p): lp.base.sha(p) for p in (CATALOG, lp.base.MINING, INVENTORY, Path(lp.__file__), Path(affine.__file__))},
              "scope": "Only six historically OPEN source150 compressed profiles frozen in the before_m10 inventory snapshot, total coverage40960. These historical controls make no claim about current open status. Six small LP feasibility checks, no E72 completion solver or graph search launched or restarted.",
              "rows": records, "affine_rejected_profiles": sum(r["affine_inconsistent"] for r in records),
              "exact_LP_infeasible_profiles": sum(r["exact_infeasible_certificate"] is not None for r in records),
              "exact_LP_feasible_profiles": sum(r["exact_feasible_witness"] is not None for r in records),
              "submission_txt_written": False}
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k not in ("rows", "inputs_sha256")}, sort_keys=True))


if __name__ == "__main__":
    main()
