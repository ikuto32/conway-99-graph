"""Exhaust the small uniform pair-category cores on all regular survivors."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import scratch_theory_e72_k23_pair_category_core as category_model


INPUT = Path("scratch_general_e72_source133_hf_exception_csp.json")
VERTEX_INPUT = Path("scratch_general_e72_source133_pointwise_frontier.json")
OUTPUT = Path("scratch_general_e72_source133_pair_category_census.json")
EXPECTED = {
    0: frozenset(("EE_same", "EU_disjoint", "UU_overlap")),
    1: frozenset(("EU_disjoint",)),
    2: frozenset(("EE_same", "EU_disjoint", "UU_overlap")),
    3: frozenset(("EE_same", "EU_disjoint", "UU_overlap")),
}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest().upper()


def run(limit, limit_per_macro):
    dependency_root = str(Path(".deps").resolve())
    if dependency_root not in sys.path:
        sys.path.insert(0, dependency_root)
    from pysat.solvers import Solver

    started = time.monotonic()
    document = json.loads(INPUT.read_text(encoding="utf-8"))
    vertex_document = json.loads(VERTEX_INPUT.read_text(encoding="utf-8"))
    exceptional = tuple(tuple(row) for row in vertex_document["vertex_order"])
    records = [row for row in document["frontier"] if row[3] < 4]
    if limit is not None:
        records = records[:limit]
    if limit_per_macro is not None:
        selected = []
        seen = Counter()
        for row in records:
            if seen[row[3]] < limit_per_macro:
                selected.append(row)
                seen[row[3]] += 1
        records = selected
    per_macro = defaultdict(Counter)
    unexpected = []
    formula_sizes = Counter()
    for number, record in enumerate(records):
        macro = record[3]
        enabled = EXPECTED[macro]
        clauses, variables, pair_rows = category_model.build_instance(
            exceptional, int(record[0], 16), enabled
        )
        formula_sizes[(macro, variables, len(clauses))] += 1
        with Solver(name="cadical195", bootstrap_with=clauses) as solver:
            answer = solver.solve()
            stats = solver.accum_stats()
        status = "SAT" if answer else "UNSAT"
        per_macro[macro]["input_orbits"] += 1
        per_macro[macro]["input_mass"] += record[1]
        per_macro[macro][status] += 1
        per_macro[macro][f"{status}_mass"] += record[1]
        per_macro[macro]["conflicts"] += stats.get("conflicts", 0)
        if answer and len(unexpected) < 20:
            unexpected.append({
                "record_number": number,
                "mask_hex": record[0],
                "macro": macro,
                "enabled": sorted(enabled),
            })
    summary = {
        "input_orbits": len(records),
        "input_mass": sum(row[1] for row in records),
        "UNSAT_orbits": sum(row["UNSAT"] for row in per_macro.values()),
        "UNSAT_mass": sum(row["UNSAT_mass"] for row in per_macro.values()),
        "SAT_orbits": sum(row["SAT"] for row in per_macro.values()),
        "SAT_mass": sum(row["SAT_mass"] for row in per_macro.values()),
        "elapsed_seconds": round(time.monotonic() - started, 6),
    }
    complete = limit is None and limit_per_macro is None
    if complete:
        # The census is also useful when the deliberately reduced category
        # set leaves SAT instances.  Assert only the independently known
        # input coverage here and report the actual SAT/UNSAT split below.
        assert summary["input_orbits"] == 5_138
        assert summary["input_mass"] == 1_129_056
        assert summary["UNSAT_orbits"] + summary["SAT_orbits"] == 5_138
        assert summary["UNSAT_mass"] + summary["SAT_mass"] == 1_129_056
    excluded = complete and summary["SAT_orbits"] == 0
    result = {
        "status": (
            "COMPLETE_UNIFORM_CATEGORY_EXCLUSION"
            if excluded
            else "COMPLETE_CATEGORY_CENSUS_WITH_SURVIVORS"
            if complete
            else "PARTIAL_PROBE"
        ),
        "model": "source133 exact H/F recurrence with minimal pair categories",
        "inputs": {str(INPUT): sha256(INPUT), str(VERTEX_INPUT): sha256(VERTEX_INPUT)},
        "category_policy_by_macro": {
            str(macro): sorted(categories) for macro, categories in EXPECTED.items()
        },
        "summary": summary,
        "per_macro": {
            str(macro): dict(sorted(row.items()))
            for macro, row in sorted(per_macro.items())
        },
        "formula_size_histogram": {
            f"macro={macro},vars={variables},clauses={clauses}": count
            for (macro, variables, clauses), count in sorted(formula_sizes.items())
        },
        "unexpected_SAT_examples": unexpected,
        "checks": {
            "all_expected_category_formulas_solved_to_completion": True,
            "no_conflict_budgets": True,
            "macro1_uses_EU_disjoint_only": True,
            "macros_0_2_3_use_EE_same_plus_EU_disjoint_plus_UU_overlap_only": True,
            "uniform_category_policy_excludes_every_instance": excluded,
        },
        "claim_boundary": (
            "This is an exhaustive computational census of the finite local "
            "CNFs. Per-instance proof certificates are not emitted here."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], **summary}, sort_keys=True), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int)
    parser.add_argument("--limit-per-macro", type=int)
    args = parser.parse_args()
    run(args.limit, args.limit_per_macro)


if __name__ == "__main__":
    main()
