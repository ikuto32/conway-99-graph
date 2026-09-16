"""Refine the small pair-category policy on its exact residual frontier.

The first census deliberately used only the structurally cheapest category
sets.  This script re-identifies the SAT residuals for macros 0 and 1, tests
every single additional pair category, and computes an exact minimum set cover
whenever the single-category UNSAT witnesses cover the full residual frontier.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import scratch_theory_e72_k23_pair_category_core as category_model


INPUT = Path("scratch_general_e72_source133_hf_exception_csp.json")
VERTEX_INPUT = Path("scratch_general_e72_source133_pointwise_frontier.json")
OUTPUT = Path("scratch_general_e72_source133_pair_category_refinement.json")

ALL = frozenset(category_model.CATEGORIES)
BASE = {
    0: frozenset(("EE_same", "EU_disjoint", "UU_overlap")),
    1: frozenset(("EU_disjoint",)),
}
EXPECTED_INPUT = {
    0: (891, 135_520, 28, 3_392),
    1: (2_348, 625_856, 179, 33_024),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def solve(Solver, exceptional, record, enabled):
    clauses, variables, pair_rows = category_model.build_instance(
        exceptional, int(record[0], 16), enabled
    )
    with Solver(name="cadical195", bootstrap_with=clauses) as solver:
        answer = solver.solve()
        stats = solver.accum_stats()
    return answer, variables, len(clauses), pair_rows, stats


def minimum_covers(residuals, candidates, killed_by):
    universe = frozenset(range(len(residuals)))
    answers = []
    for size in range(len(candidates) + 1):
        for chosen in itertools.combinations(candidates, size):
            covered = frozenset().union(
                *(killed_by[category] for category in chosen)
            ) if chosen else frozenset()
            if covered == universe:
                answers.append(chosen)
        if answers:
            return answers
    return []


def main():
    dependency_root = str(Path(".deps").resolve())
    if dependency_root not in sys.path:
        sys.path.insert(0, dependency_root)
    from pysat.solvers import Solver

    started = time.monotonic()
    document = json.loads(INPUT.read_text(encoding="utf-8"))
    vertex_document = json.loads(VERTEX_INPUT.read_text(encoding="utf-8"))
    exceptional = tuple(tuple(row) for row in vertex_document["vertex_order"])
    records_by_macro = defaultdict(list)
    for record in document["frontier"]:
        if record[3] in BASE:
            records_by_macro[record[3]].append(record)

    results = {}
    chosen_policies = {}
    for macro in sorted(BASE):
        records = records_by_macro[macro]
        base = BASE[macro]
        residuals = []
        base_conflicts = 0
        for record in records:
            answer, _variables, _clauses, _rows, stats = solve(
                Solver, exceptional, record, base
            )
            base_conflicts += stats.get("conflicts", 0)
            if answer:
                residuals.append(record)

        expected_orbits, expected_mass, expected_sat, expected_sat_mass = (
            EXPECTED_INPUT[macro]
        )
        assert len(records) == expected_orbits
        assert sum(row[1] for row in records) == expected_mass
        assert len(residuals) == expected_sat
        assert sum(row[1] for row in residuals) == expected_sat_mass

        candidates = tuple(sorted(ALL - base))
        killed_by = {category: set() for category in candidates}
        candidate_counts = {}
        residual_details = []
        for number, record in enumerate(residuals):
            row_detail = {
                "mask_hex": record[0],
                "mass": record[1],
                "single_category_UNSAT": [],
            }
            for category in candidates:
                answer, variables, clauses, pair_rows, stats = solve(
                    Solver, exceptional, record, base | {category}
                )
                counts = candidate_counts.setdefault(category, Counter())
                status = "SAT" if answer else "UNSAT"
                counts[status] += 1
                counts[f"{status}_mass"] += record[1]
                counts["conflicts"] += stats.get("conflicts", 0)
                counts["variables"] = variables
                counts["clauses"] = clauses
                if not answer:
                    killed_by[category].add(number)
                    row_detail["single_category_UNSAT"].append(category)
            residual_details.append(row_detail)

        uncovered = [
            residual_details[number]
            for number in range(len(residuals))
            if not any(number in killed_by[c] for c in candidates)
        ]
        covers = minimum_covers(residuals, candidates, killed_by)
        if covers:
            chosen = covers[0]
            chosen_policy = base | frozenset(chosen)
            # Monotonicity makes the already-UNSAT base instances immediate;
            # still solve every residual again with the chosen uniform policy
            # as an independent implementation check of the set-cover lift.
            verified_unsat = 0
            verified_mass = 0
            for record in residuals:
                answer, *_rest = solve(
                    Solver, exceptional, record, chosen_policy
                )
                assert not answer
                verified_unsat += 1
                verified_mass += record[1]
            assert verified_unsat == len(residuals)
            assert verified_mass == sum(row[1] for row in residuals)
            chosen_policies[str(macro)] = sorted(chosen_policy)
        else:
            chosen = None
            chosen_policy = None

        results[str(macro)] = {
            "input_orbits": len(records),
            "input_mass": sum(row[1] for row in records),
            "base_policy": sorted(base),
            "base_UNSAT_orbits": len(records) - len(residuals),
            "base_SAT_orbits": len(residuals),
            "base_SAT_mass": sum(row[1] for row in residuals),
            "base_conflicts": base_conflicts,
            "single_addition_census": {
                category: dict(sorted(counts.items()))
                for category, counts in sorted(candidate_counts.items())
            },
            "residuals_with_no_single_category_killer": uncovered,
            "minimum_single_category_set_covers": [list(row) for row in covers],
            "selected_uniform_policy": (
                sorted(chosen_policy) if chosen_policy is not None else None
            ),
            "residual_details": residual_details,
        }

    complete = len(chosen_policies) == len(BASE)
    output = {
        "status": (
            "COMPLETE_REFINED_UNIFORM_CATEGORY_EXCLUSION"
            if complete else "PAIR_CATEGORY_REFINEMENT_HAS_HARD_RESIDUALS"
        ),
        "inputs": {
            str(INPUT): sha256(INPUT),
            str(VERTEX_INPUT): sha256(VERTEX_INPUT),
        },
        "all_categories": sorted(ALL),
        "chosen_policy_by_macro": chosen_policies,
        "per_macro": results,
        "elapsed_seconds": round(time.monotonic() - started, 6),
        "checks": {
            "base_residual_counts_match_full_census": True,
            "each_single_category_test_solved_without_budget": True,
            "selected_set_cover_rechecked_as_uniform_policy": complete,
            "monotone_lift_covers_base_UNSAT_instances": complete,
        },
        "claim_boundary": (
            "Exact exhaustive finite-CNF computation; no per-instance DRUP "
            "certificates are emitted by this script."
        ),
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": output["status"],
        "chosen_policy_by_macro": chosen_policies,
        "elapsed_seconds": output["elapsed_seconds"],
        "uncovered": {
            macro: len(row["residuals_with_no_single_category_killer"])
            for macro, row in results.items()
        },
    }, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
