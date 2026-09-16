"""Independent replay of the final source-133 regular category exclusion.

Every regular frontier representative is rebuilt directly from the audited
input data and solved with one fixed, macro-dependent set of necessary
induced-pair-upper categories.  Earlier category census outputs are not read.
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import scratch_theory_e72_k23_pair_category_core as category_model


INPUT = Path("scratch_general_e72_source133_hf_exception_csp.json")
VERTEX_INPUT = Path("scratch_general_e72_source133_pointwise_frontier.json")
OUTPUT = Path("scratch_general_e72_source133_pair_category_exclusion_audit.json")
POLICY = {
    0: frozenset(("EE_disjoint", "EE_same", "EU_disjoint", "UU_overlap")),
    1: frozenset(("EE_disjoint", "EE_same", "EU_disjoint")),
    2: frozenset(("EE_same", "EU_disjoint", "UU_overlap")),
    3: frozenset(("EE_same", "EU_disjoint", "UU_overlap")),
}
EXPECTED = {
    0: (891, 135_520),
    1: (2_348, 625_856),
    2: (1_234, 232_800),
    3: (665, 134_880),
}


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
    exceptional = tuple(tuple(row) for row in vertex_document["vertex_order"])
    records = [row for row in document["frontier"] if row[3] < 4]
    assert len(records) == 5_138
    assert sum(row[1] for row in records) == 1_129_056

    per_macro = defaultdict(Counter)
    formula_sizes = Counter()
    manifest = hashlib.sha256()
    failures = []
    for number, record in enumerate(records):
        macro = record[3]
        enabled = POLICY[macro]
        clauses, variables, pair_rows = category_model.build_instance(
            exceptional, int(record[0], 16), enabled
        )
        with Solver(name="cadical195", bootstrap_with=clauses) as solver:
            answer = solver.solve()
            stats = solver.accum_stats()
        row = per_macro[macro]
        row["input_orbits"] += 1
        row["input_mass"] += record[1]
        row["UNSAT_orbits" if not answer else "SAT_orbits"] += 1
        row["UNSAT_mass" if not answer else "SAT_mass"] += record[1]
        row["conflicts"] += stats.get("conflicts", 0)
        formula_sizes[(macro, variables, len(clauses))] += 1
        manifest_row = (
            record[0], record[1], macro, sorted(enabled), variables,
            len(clauses), sorted(pair_rows.items()), "SAT" if answer else "UNSAT",
        )
        manifest.update(
            (json.dumps(manifest_row, separators=(",", ":")) + "\n").encode()
        )
        if answer and len(failures) < 20:
            failures.append({"record_number": number, "record": record})

    for macro, (orbits, mass) in EXPECTED.items():
        row = per_macro[macro]
        assert row["input_orbits"] == orbits
        assert row["input_mass"] == mass
        assert row["UNSAT_orbits"] == orbits
        assert row["UNSAT_mass"] == mass
        assert row["SAT_orbits"] == 0
        assert row["SAT_mass"] == 0
    assert not failures

    dependencies = (
        INPUT,
        VERTEX_INPUT,
        Path("scratch_general_e72_source133_hf_pair_sat.py"),
        Path("scratch_theory_e72_k23_pair_category_core.py"),
    )
    result = {
        "status": "EXACT_COMPUTATIONAL_FINITE_CATEGORY_EXCLUSION",
        "scope": "source133 regular macros 0,1,2,3",
        "solver": "PySAT CaDiCaL 1.9.5, no conflict or time budgets",
        "inputs_and_implementation_sha256": {
            str(path): sha256(path) for path in dependencies
        },
        "policy_by_macro": {
            str(macro): sorted(categories)
            for macro, categories in sorted(POLICY.items())
        },
        "summary": {
            "input_orbits": len(records),
            "input_mass": sum(row[1] for row in records),
            "UNSAT_orbits": sum(
                row["UNSAT_orbits"] for row in per_macro.values()
            ),
            "UNSAT_mass": sum(
                row["UNSAT_mass"] for row in per_macro.values()
            ),
            "SAT_orbits": 0,
            "SAT_mass": 0,
            "elapsed_seconds": round(time.monotonic() - started, 6),
        },
        "per_macro": {
            str(macro): dict(sorted(row.items()))
            for macro, row in sorted(per_macro.items())
        },
        "formula_size_histogram": {
            f"macro={macro},vars={variables},clauses={clauses}": count
            for (macro, variables, clauses), count
            in sorted(formula_sizes.items())
        },
        "ordered_instance_manifest_sha256": manifest.hexdigest().upper(),
        "checks": {
            "rebuilt_from_primary_frontier_without_prior_census_outputs": True,
            "all_5138_instances_solved_to_completion": True,
            "no_conflict_or_time_budgets": True,
            "all_instances_UNSAT": True,
            "orbit_mass_matches_recurrence_frontier": True,
        },
        "claim_boundary": (
            "This is an independently replayable exact finite-CNF census. "
            "It does not itself emit per-instance DRUP certificates."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], **result["summary"]},
                     sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
