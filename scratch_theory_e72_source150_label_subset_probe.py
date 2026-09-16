"""Six frozen E72 source150 profiles, no graph-search or worker operations."""

from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import time

import scratch_theory_e71_label_subset_moment_probe as local
import scratch_theory_e71_row_label_quota_moment_probe as quota

CATALOG = Path("scratch_general_e72_q3_gram_fast_expansion_macro_catalog.json")
FROZEN = Path("scratch_theory_e72_source150_degree_moment_applicability.json")
OUTPUT = Path("scratch_theory_e72_source150_label_subset_probe.json")
WANTED = {(150, 0, 3), (150, 1, 0), (150, 3, 3), (150, 9, 0), (150, 10, 0), (150, 11, 0)}


def solve(matrix, target):
    answer = local.lp.linprog(local.lp.np.zeros(len(matrix[0])),
                              A_eq=local.lp.np.asarray(matrix, dtype=float),
                              b_eq=local.lp.np.asarray(target, dtype=float),
                              bounds=(0, None), method="highs", options={"time_limit": 15})
    certificate = local.lp.farkas(matrix, target) if answer.status == 2 else None
    witness = None
    if answer.success:
        for cap in (1000, 100000, 10000000):
            weights = [Fraction(float(value)).limit_denominator(cap) for value in answer.x]
            if all(value >= 0 for value in weights) and all(sum(a * b for a, b in zip(row, weights)) == rhs for row, rhs in zip(matrix, target)):
                witness = {"nonzero_weights": [[i, str(value)] for i, value in enumerate(weights) if value],
                           "denominator_cap": cap, "exact_nonnegative_equations_checked": True}
                break
    return {"LP_status": int(answer.status), "exact_integer_certificate": certificate,
            "exact_feasible_witness": witness,
            "matrix_sha256": hashlib.sha256(json.dumps([matrix, target], separators=(",", ":")).encode()).hexdigest()}


def main():
    started = time.monotonic()
    frozen, catalog, mining = map(local.lp.base.read, (FROZEN, CATALOG, local.lp.base.MINING))
    assert {tuple(row["key"]) for row in frozen["rows"]} == WANTED
    assert len(frozen["rows"]) == 6 and sum(row["coverage"] for row in frozen["rows"]) == 40960
    for path in (CATALOG, local.lp.base.MINING):
        assert local.lp.base.sha(path) == frozen["inputs_sha256"][str(path)]
    entries = {local.lp.base.key(row): row for row in catalog["macro_entries"] if row["signature_stabilizer_canonical"]}
    profiles = [row for row in mining["profile_rows"]["72"] if local.lp.base.key(row) in WANTED]
    assert len(profiles) == 6 and {local.lp.base.key(row) for row in profiles} == WANTED
    rows, local_models = [], []
    for profile in profiles:
        key = local.lp.base.key(profile)
        entry = entries[key]
        data = local.subset_domains(entry)
        local_models.append({"key": list(key), "allowed_subsets": data[1], "counts": data[2]})
        matrix, target, metadata = local.model(entry, profile, data)
        assert metadata["rank_K4"] == 2
        subset_result = solve(matrix, target)
        _, compression, _, gram = local.lp.base.compression(entry, profile)
        _, domains = local.lp.raw_domains(compression, gram)
        degree_lookup = [{row["pivot"]: row["degree"] for row in domain} for domain in domains]
        keep, decisions, stats = [], [], Counter()
        for i, variable in enumerate(metadata["variables"]):
            x, pivot = variable["position"], tuple(variable["pivot"])
            passed, reason = quota.row_feasible(entry, x, degree_lookup[x // 4][pivot], data[1][x])
            decisions.append(passed)
            stats[reason["reason"]] += 1
            stats["max_DP_states"] = max(stats["max_DP_states"], reason["max_states"])
            if passed:
                keep.append(i)
        assert keep
        reduced = [[row[i] for i in keep] for row in matrix]
        quota_result = solve(reduced, target)
        rows.append({"key": list(key), "parameter": profile["parameter"],
                     "coverage": int(entry["signature_orbit_labelled_coverage"]),
                     "model": metadata, "subset": subset_result, "quota": quota_result,
                     "quota_retained_variable_indices": keep, "quota_row_decisions": decisions,
                     "quota_statistics": dict(stats)})
        print(json.dumps({"key": list(key), "raw_position_rows": metadata["raw_internal_degree_position_rows"],
                          "subset_rows": metadata["retained_position_rows"], "quota_rows": len(keep),
                          "subset_exact_feasible": subset_result["exact_feasible_witness"] is not None,
                          "quota_exact_feasible": quota_result["exact_feasible_witness"] is not None}), flush=True)
    result = {"status": "E72_SOURCE150_SIX_PROFILE_LABEL_SUBSET_QUOTA_PROBE_COMPLETE",
              "inputs_sha256": {str(path): local.lp.base.sha(path) for path in (CATALOG, local.lp.base.MINING, FROZEN, Path(local.__file__), Path(quota.__file__), Path(local.lp.__file__), Path(local.lp.base.__file__))},
              "rows": rows, "local_models": local_models,
              "summary": {"profiles": 6, "coverage": 40960,
                          "subset_exact_feasible_profiles": sum(row["subset"]["exact_feasible_witness"] is not None for row in rows),
                          "quota_exact_feasible_profiles": sum(row["quota"]["exact_feasible_witness"] is not None for row in rows),
                          "subset_exact_infeasible_profiles": sum(row["subset"]["exact_integer_certificate"] is not None for row in rows),
                          "quota_exact_infeasible_profiles": sum(row["quota"]["exact_integer_certificate"] is not None for row in rows),
                          "max_quota_DP_states": max(row["quota_statistics"]["max_DP_states"] for row in rows)},
              "scope": "Only the six source150 macro profiles frozen in the prior applicability artifact. 23-vertex single-row subset tests and at-most-972-state single-row root-label quota DP, then six subset and six quota moment LPs. No graph, overlap, matching or global-row completion search; no worker or inventory operations.",
              "elapsed_seconds": time.monotonic() - started,
              "requires_independent_audit": True, "submission_txt_written": False}
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
