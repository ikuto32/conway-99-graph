"""Single-row exact-rootlabel quotas, without matching/graph completions.

Consume the saved 16-subset local tests.  At most 972 seven-coordinate
states couple one vertex's choices; ordinary target singletons give
independent interval slack.  Integer Farkas checking is unchanged.
"""

import argparse
from collections import Counter
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import time

import scratch_theory_e71_label_subset_moment_probe as local


def incidence(fibre, bits):
    return tuple(sum(bool(bits >> j & 1) and 2 * group in local.lp.base.LABELS[4 * fibre + j]
                     for j in range(4)) for group in range(7))


@lru_cache(maxsize=None)
def degree_choices(allowed, degree):
    return tuple(bits for bits in allowed if bits.bit_count() == degree)


@lru_cache(maxsize=None)
def quota_dp(initial, options, quota, lower):
    if any(a > b for a, b in zip(initial, quota)):
        return False, 0
    states = {initial}
    max_states = 1
    for choices in options:
        states = {tuple(a + b for a, b in zip(state, addition))
                  for state in states for addition in choices
                  if all(a + b <= q for a, b, q in zip(state, addition, quota))}
        assert len(states) <= 972
        max_states = max(max_states, len(states))
        if not states:
            return False, max_states
    return any(all(a >= b for a, b in zip(state, lower)) for state in states), max_states


def row_feasible(entry, x, degrees, allowed):
    source = x // 4
    support = local.lp.base.SUPPORTS[source]
    quota = tuple(1 if group in support else 2 for group in range(7))
    group_totals = tuple(sum(degree for target, degree in enumerate(degrees)
                             if group in local.lp.base.SUPPORTS[target]) for group in range(7))
    if group_totals != tuple(2 * v for v in quota):
        return False, {"reason": "coarse_group_quota", "max_states": 0}
    exceptional = {tuple(row["support"]) for row in entry["exceptional_supports"]}
    own = degree_choices(tuple(allowed[source]), degrees[source])
    assert len(own) == 1
    initial = incidence(source, own[0])
    free = [0] * 7
    options = []
    for target, degree in enumerate(degrees):
        if target == source:
            continue
        choices = degree_choices(tuple(allowed[target]), degree)
        assert choices
        if local.lp.base.SUPPORTS[target] not in exceptional:
            assert degree in (0, 1)
            assert choices == ((0,) if degree == 0 else (1, 2, 4, 8))
            for group in local.lp.base.SUPPORTS[target]:
                free[group] += degree
        else:
            vectors = tuple(sorted({incidence(target, bits) for bits in choices}))
            if len(vectors) == 1:
                initial = tuple(a + b for a, b in zip(initial, vectors[0]))
            else:
                options.append(vectors)
    options.sort(key=lambda choices: (len(choices), choices))
    lower = tuple(max(0, q - count) for q, count in zip(quota, free))
    passed, max_states = quota_dp(initial, tuple(options), quota, lower)
    return passed, {"reason": "passed" if passed else "exact_label_quota_DP", "max_states": max_states}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--all-filtered", action="store_true")
    parser.add_argument("--output", type=Path, default=Path("scratch_theory_e71_row_label_quota_moment_probe.json"))
    args = parser.parse_args()
    started = time.monotonic()
    input_path = Path("scratch_theory_e71_label_subset_moment_frontier.json" if args.all_filtered
                      else "scratch_theory_e71_label_subset_moment_probe.json")
    saved = local.lp.base.read(input_path)
    for name, expected in saved["inputs_sha256"].items():
        assert local.lp.base.sha(Path(name)) == expected
    catalog, mining = map(local.lp.base.read, (local.lp.base.CATALOG, local.lp.base.MINING))
    entries = {local.lp.base.key(row): row for row in catalog["macro_entries"] if row["signature_stabilizer_canonical"]}
    profiles = {(local.lp.base.key(row), row["parameter"]): row for row in mining["profile_rows"]["71"]}
    local_records = {tuple(row["key"]): row for row in saved["local_models"]}
    results = []
    for record in saved["profiles"]:
        key, parameter = tuple(record["key"]), record["parameter"]
        entry, profile = entries[key], profiles[(key, parameter)]
        subsets = local_records[key]["allowed_subsets"]
        data = (local.internal_blocks(entry), subsets, local_records[key]["counts"])
        matrix, target, metadata = local.model(entry, profile, data)
        assert metadata == record["model"]
        _, c, _, k4 = local.lp.base.compression(entry, profile)
        _, raw = local.lp.raw_domains(c, k4)
        degrees_by_pivot = [{row["pivot"]: row["degree"] for row in domain} for domain in raw]
        keep, decisions = [], []
        statistics = Counter()
        for i, variable in enumerate(metadata["variables"]):
            x, pivot = variable["position"], tuple(variable["pivot"])
            degrees = degrees_by_pivot[x // 4][pivot]
            passed, reason = row_feasible(entry, x, degrees, subsets[x])
            statistics[reason["reason"]] += 1
            statistics["max_DP_states"] = max(statistics["max_DP_states"], reason["max_states"])
            decisions.append(passed)
            if passed:
                keep.append(i)
        reduced = [[row[i] for i in keep] for row in matrix]
        assert keep
        answer = local.lp.linprog(local.lp.np.zeros(len(keep)), A_eq=local.lp.np.asarray(reduced, dtype=float),
                                 b_eq=local.lp.np.asarray(target, dtype=float), bounds=(0, None), method="highs")
        certificate = local.lp.farkas(reduced, target) if answer.status == 2 else None
        row = {"key": list(key), "parameter": parameter, "coverage": record["coverage"],
               "subset_only_certified_infeasible": record["exact_integer_certificate"] is not None,
               "retained_variable_indices": keep, "row_decisions": decisions,
               "statistics": dict(statistics), "LP_status": int(answer.status),
               "exact_integer_certificate": certificate,
               "model_sha256": hashlib.sha256(json.dumps([reduced, target], separators=(",", ":")).encode()).hexdigest()}
        results.append(row)
        print(json.dumps({"key": list(key), "parameter": parameter,
                          "rows_before": len(decisions), "rows_after": len(keep),
                          "max_DP_states": statistics["max_DP_states"],
                          "exact_infeasible": certificate is not None,
                          "new_vs_subset": certificate is not None and record["exact_integer_certificate"] is None}), flush=True)
    result = {
        "status": "E71_SINGLE_ROW_ROOTLABEL_QUOTA_MOMENT_PROBE_COMPLETE",
        "inputs_sha256": {str(p): local.lp.base.sha(p) for p in (input_path, local.lp.base.CATALOG, local.lp.base.MINING)},
        "all_filtered_requested": args.all_filtered, "profiles": results,
        "profiles_tested": len(results),
        "exact_infeasible_profiles": sum(row["exact_integer_certificate"] is not None for row in results),
        "new_vs_subset_infeasible_profiles": sum(row["exact_integer_certificate"] is not None and
                                                 not row["subset_only_certified_infeasible"] for row in results),
        "max_DP_states": max(row["statistics"]["max_DP_states"] for row in results),
        "cache": str(quota_dp.cache_info()),
        "requires_independent_audit_before_inventory_credit": True,
        "full_local_completions_enumerated": 0, "pointwise_E0_lower_bound": None,
        "elapsed_seconds": time.monotonic() - started,
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "profiles"}), flush=True)


if __name__ == "__main__":
    main()
