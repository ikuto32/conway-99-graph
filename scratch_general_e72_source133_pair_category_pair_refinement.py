"""Find a uniform two-category refinement for source-133 macro 1.

Consumes the exhaustive single-addition census.  Monotonicity lets us skip a
pair solve whenever either member was already individually UNSAT; all other
instances are solved explicitly with the complete category pair enabled.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import sys
import time
from pathlib import Path

import scratch_theory_e72_k23_pair_category_core as category_model


INPUT = Path("scratch_general_e72_source133_hf_exception_csp.json")
VERTEX_INPUT = Path("scratch_general_e72_source133_pointwise_frontier.json")
REFINEMENT_INPUT = Path(
    "scratch_general_e72_source133_pair_category_refinement.json"
)
OUTPUT = Path(
    "scratch_general_e72_source133_pair_category_pair_refinement.json"
)
MACRO = 1
BASE = frozenset(("EU_disjoint",))


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest().upper()


def main():
    dependency_root = str(Path(".deps").resolve())
    if dependency_root not in sys.path:
        sys.path.insert(0, dependency_root)
    from pysat.solvers import Solver

    started = time.monotonic()
    document = json.loads(INPUT.read_text(encoding="utf-8"))
    vertex_document = json.loads(VERTEX_INPUT.read_text(encoding="utf-8"))
    refinement = json.loads(REFINEMENT_INPUT.read_text(encoding="utf-8"))
    exceptional = tuple(tuple(row) for row in vertex_document["vertex_order"])
    records = {
        row[0]: row for row in document["frontier"] if row[3] == MACRO
    }
    residuals = refinement["per_macro"][str(MACRO)]["residual_details"]
    assert len(residuals) == 179
    assert sum(row["mass"] for row in residuals) == 33_024
    candidates = tuple(sorted(
        set(category_model.CATEGORIES) - set(BASE)
    ))

    pair_results = []
    for additions in itertools.combinations(candidates, 2):
        additions_set = frozenset(additions)
        explicitly_solved = 0
        monotone_unsat = 0
        explicit_unsat = 0
        sat_rows = []
        conflicts = 0
        for detail in residuals:
            if additions_set & set(detail["single_category_UNSAT"]):
                monotone_unsat += 1
                continue
            record = records[detail["mask_hex"]]
            clauses, variables, pair_rows = category_model.build_instance(
                exceptional, int(record[0], 16), BASE | additions_set
            )
            with Solver(name="cadical195", bootstrap_with=clauses) as solver:
                answer = solver.solve()
                stats = solver.accum_stats()
            explicitly_solved += 1
            conflicts += stats.get("conflicts", 0)
            if answer:
                sat_rows.append({
                    "mask_hex": record[0],
                    "mass": record[1],
                })
            else:
                explicit_unsat += 1
        assert monotone_unsat + explicitly_solved == len(residuals)
        pair_results.append({
            "additional_categories": list(additions),
            "uniform_policy": sorted(BASE | additions_set),
            "monotone_single_category_UNSAT": monotone_unsat,
            "explicitly_solved": explicitly_solved,
            "explicit_UNSAT": explicit_unsat,
            "SAT_orbits": len(sat_rows),
            "SAT_mass": sum(row["mass"] for row in sat_rows),
            "conflicts": conflicts,
            "SAT_examples": sat_rows[:20],
        })

    excluding = [
        row for row in pair_results if row["SAT_orbits"] == 0
    ]
    assert excluding, "No two-category uniform policy excludes macro 1"
    selected = min(
        excluding,
        key=lambda row: (row["explicitly_solved"], row["additional_categories"]),
    )
    output = {
        "status": "COMPLETE_TWO_CATEGORY_UNIFORM_EXCLUSION",
        "inputs": {
            str(INPUT): sha256(INPUT),
            str(VERTEX_INPUT): sha256(VERTEX_INPUT),
            str(REFINEMENT_INPUT): sha256(REFINEMENT_INPUT),
        },
        "macro": MACRO,
        "base_policy": sorted(BASE),
        "input_residual_orbits": len(residuals),
        "input_residual_mass": sum(row["mass"] for row in residuals),
        "pair_results": pair_results,
        "excluding_pairs": [
            row["additional_categories"] for row in excluding
        ],
        "selected_uniform_policy": selected["uniform_policy"],
        "elapsed_seconds": round(time.monotonic() - started, 6),
        "checks": {
            "all_category_pairs_checked": len(pair_results)
            == len(tuple(itertools.combinations(candidates, 2))),
            "monotonic_single_category_results_reused_exactly": True,
            "all_remaining_instances_explicitly_solved_without_budget": True,
            "at_least_one_pair_excludes_all_179_residuals": True,
        },
        "claim_boundary": (
            "Exact exhaustive finite-CNF computation; no per-instance DRUP "
            "certificates are emitted by this script."
        ),
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": output["status"],
        "excluding_pairs": output["excluding_pairs"],
        "selected_uniform_policy": output["selected_uniform_policy"],
        "elapsed_seconds": output["elapsed_seconds"],
    }, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
