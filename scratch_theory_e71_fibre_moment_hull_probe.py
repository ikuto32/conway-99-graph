"""Bounded convex hulls of attainable four-row fibre moments.

No adjacency/port/matching completions are generated.  A cap ends the
profile as incomplete and never supplies an exclusion.
"""

from collections import defaultdict
import argparse
from fractions import Fraction
import hashlib
import itertools as it
import json
import math
from pathlib import Path
import time

import scratch_theory_e71_degree_moment_lp_audit as exact
import scratch_theory_e71_degree_moment_lp_probe as lp


OUTPUT = Path("scratch_theory_e71_fibre_moment_hull_probe.json")
INVENTORY = Path("scratch_root_e71_theory_frontier_before_label_subset.json")
TARGETS = {(724, 1, 0), (2378, 0, 0), (2378, 1, 0)}
PAIR_CAP = 200000
JOIN_CAP = 2000000
MOMENT_CAP = 10000
PROFILE_SECONDS = 30
LP_SECONDS = 15


class BoundReached(Exception):
    pass


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def moment(v, pairs):
    return tuple(v[i] * v[j] for i, j in pairs)


def fibre_options(domains, self_degrees, source, pairs, deadline, stats, position_domains=None):
    local = [tuple(v for v, degrees in domains if degrees[source] == required)
             for required in self_degrees]
    if position_domains is not None:
        selected = [tuple(tuple(v) for v in domain) for domain in position_domains]
        assert len(selected) == 4
        assert all(set(chosen) <= set(raw) for chosen, raw in zip(selected, local))
        local = selected
    if any(not values for values in local):
        return [], {"local_domain_sizes": list(map(len, local)), "empty_position": True}
    pair_maps = []
    for first, second in ((0, 1), (2, 3)):
        if len(local[first]) * len(local[second]) > PAIR_CAP:
            raise BoundReached("pair-side count cap")
        mapped = defaultdict(dict)
        for a, b in it.product(local[first], local[second]):
            vector_sum = add(a, b)
            pair_moment = add(moment(a, pairs), moment(b, pairs))
            mapped[vector_sum].setdefault(pair_moment, (a, b))
        pair_maps.append(mapped)
    choices = {}
    joined = 0
    for vector_sum, left in pair_maps[0].items():
        right = pair_maps[1].get(tuple(-v for v in vector_sum), {})
        for left_moment, left_rows in left.items():
            for right_moment, right_rows in right.items():
                joined += 1
                stats["joined_pair_moment_combinations"] += 1
                if stats["joined_pair_moment_combinations"] > JOIN_CAP:
                    raise BoundReached("profile joined-pair count cap")
                if joined % 1000 == 0 and time.monotonic() > deadline:
                    raise BoundReached("profile time cap")
                value = add(left_moment, right_moment)
                choices.setdefault(value, left_rows + right_rows)
                if len(choices) > MOMENT_CAP:
                    raise BoundReached("per-fibre distinct moment cap")
    return [{"moment": list(value), "row_pivots": [list(v) for v in choices[value]]}
            for value in sorted(choices)], {
                "local_domain_sizes": list(map(len, local)),
                "pair_sum_key_counts": [len(p) for p in pair_maps],
                "pair_sum_moment_counts": [sum(map(len, p.values())) for p in pair_maps],
                "joined_pair_moment_combinations": joined,
                "distinct_moments": len(choices), "empty_position": False}


def model(fibres, target):
    columns, variables = [], []
    for source, choices in enumerate(fibres):
        for index, choice in enumerate(choices):
            columns.append([int(i == source) for i in range(21)] + choice["moment"])
            variables.append([source, index])
    return list(map(list, zip(*columns))), [1] * 21 + list(target), variables


def rational_primal(matrix, target, values):
    for cap in (1000, 100000, 10000000):
        weights = [Fraction(float(v)).limit_denominator(cap) for v in values]
        if all(v >= 0 for v in weights) and all(sum(a * b for a, b in zip(row, weights)) == rhs for row, rhs in zip(matrix, target)):
            return {"nonzero_weights": [[i, str(v)] for i, v in enumerate(weights) if v],
                    "exact_all_equations_and_nonnegativity": True, "denominator_cap": cap}
    return None


def analyze(entry, profile, position_domains=None):
    started = time.monotonic()
    deadline = started + PROFILE_SECONDS
    exceptional, c, gram = exact.reconstruct(entry, profile)
    pivots, coordinates = exact.principal_coordinates(gram)
    domains = exact.all_raw_domains(c, pivots, coordinates)
    internal = exact.internal_degrees(entry, exceptional, c)
    pairs = tuple(it.combinations_with_replacement(range(len(pivots)), 2))
    target = tuple(4 * gram[pivots[i]][pivots[j]] for i, j in pairs)
    stats = {"joined_pair_moment_combinations": 0}
    fibres, metadata = [], []
    result = {"key": list(exact.macro_key(entry)), "parameter": profile["parameter"],
              "coverage": int(entry["signature_orbit_labelled_coverage"]),
              "rank_K4": len(pivots), "pivot_indices": list(pivots),
              "moment_pairs": list(map(list, pairs)), "target_moment": list(target),
              "raw_row_patterns": sum(map(len, domains))}
    try:
        for source in range(21):
            if time.monotonic() > deadline:
                raise BoundReached("profile time cap")
            choices, info = fibre_options(domains[source], internal[source], source, pairs, deadline, stats,
                                         None if position_domains is None else position_domains[4 * source:4 * source + 4])
            fibres.append(choices)
            metadata.append(info)
    except BoundReached as exc:
        result.update({"status": "CAPPED_NO_EXCLUSION", "cap_reason": str(exc),
                       "completed_fibres": len(fibres), "fibre_metadata": metadata,
                       "stats": stats, "elapsed_seconds": time.monotonic() - started})
        return result
    result.update({"complete_fibre_options": True, "fibre_options": fibres,
                   "fibre_metadata": metadata, "stats": stats})
    if any(not f for f in fibres):
        result.update({"status": "EMPTY_FIBRE_EXACT_CANDIDATE", "empty_fibres": [i for i, f in enumerate(fibres) if not f],
                       "elapsed_seconds": time.monotonic() - started})
        return result
    matrix, rhs, variables = model(fibres, target)
    answer = lp.linprog(lp.np.zeros(len(variables)), A_eq=lp.np.asarray(matrix, dtype=float),
                        b_eq=lp.np.asarray(rhs, dtype=float), bounds=(0, None), method="highs",
                        options={"time_limit": LP_SECONDS})
    certificate = lp.farkas(matrix, rhs) if answer.status == 2 else None
    primal = rational_primal(matrix, rhs, answer.x) if answer.success else None
    result.update({"status": "COMPLETE_FIBRE_MOMENT_HULL_MODEL", "LP_status": int(answer.status),
                   "matrix_sha256": hashlib.sha256(json.dumps([matrix, rhs], separators=(",", ":")).encode()).hexdigest(),
                   "variables": variables, "equations": len(rhs), "variable_count": len(variables),
                   "exact_Farkas_certificate": certificate, "exact_feasible_weights": primal,
                   "elapsed_seconds": time.monotonic() - started})
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--remaining", action="store_true")
    parser.add_argument("--output", type=Path, default=OUTPUT)
    arguments = parser.parse_args()
    catalog, mining, raw_lp = map(exact.read, (exact.CATALOG, exact.MINING, exact.CERT))
    entries = {exact.macro_key(r): r for r in catalog["macro_entries"] if r["signature_stabilizer_canonical"]}
    profiles = {(exact.macro_key(r), r["parameter"]): r for r in mining["profile_rows"]["71"]}
    inventory = exact.read(INVENTORY)
    wanted = set(map(tuple, inventory["remaining_keys"])) if arguments.remaining else TARGETS
    tasks = [r for r in raw_lp["profiles"] if tuple(r["key"]) in wanted and not r["exactly_certified_infeasible"]]
    if arguments.remaining:
        assert len(wanted) == 65 and len(tasks) == 71
    else:
        assert len(tasks) == 5
    assert {tuple(r["key"]) for r in tasks} == wanted
    results = []
    for task in tasks:
        key = tuple(task["key"])
        result = analyze(entries[key], profiles[(key, task["parameter"])])
        results.append(result)
        print(json.dumps({k: v for k, v in result.items() if k not in (
            "fibre_options", "fibre_metadata", "variables", "exact_Farkas_certificate", "exact_feasible_weights")}), flush=True)
    result = {"status": "BOUNDED_E71_FIBRE_MOMENT_HULL_PROBE_COMPLETE",
              "inputs_sha256": {str(p): exact.sha(p) for p in (exact.CATALOG, exact.MINING, exact.CERT, Path(exact.__file__), Path(lp.__file__), INVENTORY)},
              "caps": {"pair_side": PAIR_CAP, "joined_pair_moments_per_profile": JOIN_CAP,
                       "distinct_moments_per_fibre": MOMENT_CAP, "enumeration_seconds_per_profile": PROFILE_SECONDS,
                       "primal_LP_seconds": LP_SECONDS},
              "scope": ("The 65 frozen residual macros and their 71 raw-LP-passing profiles only. No global quartet product or adjacency completion."
                        if arguments.remaining else "Four surviving source2378 profiles plus source724 Q2 positive Gram control only. No global quartet product or adjacency completion."),
              "remaining_frontier_requested": arguments.remaining,
              "rows": results, "requires_independent_audit_before_exclusion_credit": True,
              "submission_txt_written": False}
    arguments.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
