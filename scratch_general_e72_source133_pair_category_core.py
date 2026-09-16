"""Find minimal pair-upper category cores for one source-133 mask per macro."""

from __future__ import annotations

import hashlib
import itertools
import json
import sys
from pathlib import Path

from scratch_general_e72_source133_hf_pair_sat import (
    INPUT,
    VERTEX_INPUT,
    build_instance,
)


OUTPUT = Path("scratch_general_e72_source133_pair_category_core.json")


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest().upper()


def main():
    dependency_root = str(Path(".deps").resolve())
    if dependency_root not in sys.path:
        sys.path.insert(0, dependency_root)
    from pysat.solvers import Solver

    document = json.loads(INPUT.read_text(encoding="utf-8"))
    vertex_document = json.loads(VERTEX_INPUT.read_text(encoding="utf-8"))
    exceptional = tuple(tuple(row) for row in vertex_document["vertex_order"])
    controls = {}
    for macro in range(4):
        record = next(row for row in document["frontier"] if row[3] == macro)
        instance = build_instance(exceptional, int(record[0], 16))
        categories = tuple(sorted(instance["pair_clauses_by_category"]))
        selectors = {
            category: instance["variables"] + 1 + index
            for index, category in enumerate(categories)
        }
        clauses = list(instance["clauses"][:instance[
            "base_clause_count_before_pair_upper"
        ]])
        for category in categories:
            selector = selectors[category]
            clauses.extend(
                [-selector, *clause]
                for clause in instance["pair_clauses_by_category"][category]
            )
        outcomes = {}
        with Solver(name="cadical195", bootstrap_with=clauses) as solver:
            for size in range(len(categories) + 1):
                for enabled in itertools.combinations(categories, size):
                    enabled = frozenset(enabled)
                    assumptions = [
                        selectors[category]
                        if category in enabled else -selectors[category]
                        for category in categories
                    ]
                    answer = solver.solve(assumptions=assumptions)
                    outcomes[tuple(sorted(enabled))] = answer
        unsat = [frozenset(key) for key, answer in outcomes.items() if not answer]
        minimum_size = min(map(len, unsat))
        minimum = sorted(
            (sorted(row) for row in unsat if len(row) == minimum_size)
        )
        inclusion_minimal = sorted(
            (sorted(row) for row in unsat
             if not any(other < row for other in unsat)),
            key=lambda row: (len(row), row),
        )
        controls[str(macro)] = {
            "mask_hex": record[0],
            "categories": list(categories),
            "category_clause_counts": {
                category: len(instance["pair_clauses_by_category"][category])
                for category in categories
            },
            "all_subsets_solved": len(outcomes),
            "SAT_subsets": sum(outcomes.values()),
            "UNSAT_subsets": len(outcomes) - sum(outcomes.values()),
            "minimum_UNSAT_category_count": minimum_size,
            "minimum_UNSAT_category_sets": minimum,
            "inclusion_minimal_UNSAT_category_sets": inclusion_minimal,
        }
    result = {
        "status": "EXACT_CATEGORY_SUBSET_AUDIT_COMPLETE",
        "inputs": {str(INPUT): sha256(INPUT), str(VERTEX_INPUT): sha256(VERTEX_INPUT)},
        "controls_by_regular_macro": controls,
        "solver": "CaDiCaL 1.9.5 via PySAT assumptions",
        "claim_boundary": (
            "Category cores are reported for one concrete surviving local "
            "mask in each regular macro; they are not asserted uniform until "
            "checked on every mask."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
