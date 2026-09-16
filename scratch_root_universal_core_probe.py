"""Probe portable local-assignment cores on the universal rooted baseline CNF.

The only assumptions are a complete truth assignment to all 1,806 outer-edge
variables whose two 2-group supports are not disjoint.  Therefore any returned
UNSAT core belongs to the fixed baseline CNF and is reusable for another local
assignment exactly when every signed core literal occurs in that assignment.
"""

from __future__ import annotations

import gc
import hashlib
import itertools
import json
from pathlib import Path
import sys
import time

from scratch_general_exact_sat import coordinates, verify
from scratch_incremental_local_exact_sat import atomic_write_json, normalize_source


BASE_CNF = Path("scratch_general_exact.cnf")
BASE_META = Path("scratch_general_exact_build.json")
E75 = Path("scratch_general_e75_incremental_records.json")
E75_AUDIT = Path("scratch_e75_incremental_audit.json")
OUTPUT = Path("scratch_root_universal_core_probe.json")
SELECTED = ((0, 0), (1, 0), (2, 0), (4, 0))
CONFLICT_BUDGET = 200_000


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def assignment_sha256(literals):
    return hashlib.sha256(" ".join(map(str, literals)).encode("ascii")).hexdigest().upper()


def support_groups(label):
    return tuple(symbol // 2 for symbol in label)


def complete_nondisjoint_assignment(source, representative_index):
    labels, _index, variables, _edge = coordinates()
    exceptional = frozenset(source["supports_in_fibre_order"])
    representative = source["representatives"][representative_index]
    present = representative["present_edges"]
    literals = []
    positive_pairs = set()
    side_positive = diagonal_positive = overlap_positive = 0
    same_count = overlap_count = 0
    for pair, variable in sorted(variables.items(), key=lambda item: item[1]):
        u, v = pair
        A, B = support_groups(labels[u]), support_groups(labels[v])
        if set(A).isdisjoint(B):
            continue
        if A == B:
            same_count += 1
            value = (
                pair in present if A in exceptional
                else len(set(labels[u]) & set(labels[v])) == 1
            )
            if value:
                if len(set(labels[u]) & set(labels[v])) == 1:
                    side_positive += 1
                else:
                    diagonal_positive += 1
        else:
            overlap_count += 1
            value = pair in present if A in exceptional and B in exceptional else False
            if value:
                overlap_positive += 1
        literals.append(variable if value else -variable)
        if value:
            positive_pairs.add(pair)
    assert same_count == 21 * 6 == 126
    assert overlap_count == 1680
    assert len(literals) == 1806 == len({abs(value) for value in literals})
    assert len(positive_pairs) == side_positive + diagonal_positive + overlap_positive
    return {
        "record_index": source["selection"]["record_index"],
        "representative_index": representative_index,
        "representative_id": representative["representative_id"],
        "orbit_size": representative["orbit_size"],
        "literals": tuple(literals),
        "literal_set": frozenset(literals),
        "assumption_sha256": assignment_sha256(literals),
        "positive_assumptions": sum(value > 0 for value in literals),
        "negative_assumptions": sum(value < 0 for value in literals),
        "positive_same_side_edges": side_positive,
        "positive_same_diagonal_edges": diagonal_positive,
        "positive_overlap_edges": overlap_positive,
        "positive_pairs": frozenset(positive_pairs),
    }


def all_e75_assignments():
    assignments = []
    global_index = 0
    for record_index in range(6):
        source = normalize_source(E75, record_index)
        for representative_index in range(len(source["representatives"])):
            row = complete_nondisjoint_assignment(source, representative_index)
            row["global_representative_index"] = global_index
            assignments.append(row)
            global_index += 1
    assert len(assignments) == 352
    assert len({row["assumption_sha256"] for row in assignments}) == 352
    return assignments


def fixed_local_mapping_audit(selected_assignments):
    """Compare the universal assumptions with the independent fixed edge()."""
    dependency_root = str(Path(".deps").resolve())
    if dependency_root not in sys.path:
        sys.path.insert(0, dependency_root)
    from scratch_e75_fixed_exact_sat import build_cnf

    labels, _index, universal_variables, _edge = coordinates()
    rows = []
    for assignment in selected_assignments:
        started = time.monotonic()
        clauses, fixed_edge, fixed_full_variables, meta = build_cnf(
            assignment["global_representative_index"]
        )
        signed = {abs(value): value > 0 for value in assignment["literals"]}
        errors = []
        fixed_boolean = fixed_variable = 0
        for pair, universal_variable in universal_variables.items():
            A = support_groups(labels[pair[0]])
            B = support_groups(labels[pair[1]])
            value = fixed_edge(*pair)
            if set(A).isdisjoint(B):
                fixed_variable += 1
                if type(value) is not int or universal_variable in signed:
                    errors.append(f"bad disjoint mapping {pair}")
            else:
                fixed_boolean += 1
                if type(value) is not bool or signed.get(universal_variable) is not value:
                    errors.append(f"bad fixed mapping {pair}")
        if fixed_full_variables != universal_variables:
            errors.append("full outer variable coordinate dictionary differs")
        if (fixed_boolean, fixed_variable) != (1806, 1680):
            errors.append("fixed/remaining mapping counts differ")
        if meta["BP_equalities"] != 1176 or meta["outer_pair_equalities"] != 3486:
            errors.append("fixed-local equation counts differ")
        if meta["edge_variables"] != 1680:
            errors.append("fixed-local remaining edge count differs")
        rows.append({
            "global_representative_index": assignment["global_representative_index"],
            "record_index": assignment["record_index"],
            "representative_index": assignment["representative_index"],
            "fixed_boolean_outer_edges": fixed_boolean,
            "remaining_disjoint_edge_variables": fixed_variable,
            "fixed_local_meta": meta,
            "comparison_seconds": round(time.monotonic() - started, 6),
            "errors": errors,
            "ok": not errors,
        })
        del clauses, fixed_edge, fixed_full_variables
        gc.collect()
    return rows


def decode_core(core):
    labels, _index, variables, _edge = coordinates()
    inverse = {variable: pair for pair, variable in variables.items()}
    decoded = []
    for literal in core:
        u, v = inverse[abs(literal)]
        A, B = support_groups(labels[u]), support_groups(labels[v])
        decoded.append({
            "literal": literal,
            "value": literal > 0,
            "outer_pair": [u, v],
            "labels": [list(labels[u]), list(labels[v])],
            "group_supports": [list(A), list(B)],
            "kind": "same" if A == B else "overlap",
        })
    return decoded


def result_document(base_audit, mapping_rows, probes, coverage, started, load_seconds):
    return {
        "model": "portable assumption cores on universal rooted baseline CNF",
        "base_cnf": str(BASE_CNF),
        "base_cnf_sha256": sha256(BASE_CNF),
        "baseline_audit": base_audit,
        "fixed_local_mapping_audit": mapping_rows,
        "selected": [{
            key: value for key, value in row.items()
            if key not in ("literals", "literal_set", "positive_pairs")
        } for row in probes],
        "cross_representative_coverage": coverage,
        "solver": "CaDiCaL 1.9.5, one baseline instance, complete local assumptions",
        "conflict_budget_per_selected_representative": CONFLICT_BUDGET,
        "baseline_load_seconds": round(load_seconds, 6),
        "wall_seconds": round(time.monotonic() - started, 6),
        "status": (
            "SAT" if any(row["status"] == "SAT" for row in probes)
            else "UNSAT" if probes and all(row["status"] == "UNSAT" for row in probes)
            else "UNKNOWN"
        ),
        "portable_core_rule": (
            "For this exact baseline CNF F, a returned core C certifies F AND C "
            "UNSAT. A different E75 or future E74 complete local assignment A is "
            "covered if and only if every signed literal of C is in A. Matching only "
            "variable numbers, unsigned edges, or a different baseline hash is unsafe."
        ),
        "claim_boundary": (
            "This is a small portability probe, not an exhaustive E74/E75 baseline "
            "sweep and not a proof certificate. Future reuse is tied to the exact "
            "baseline SHA-256 and the stable first-3486 outer-edge coordinate map."
        ),
    }


def main():
    dependency_root = str(Path(".deps").resolve())
    if dependency_root not in sys.path:
        sys.path.insert(0, dependency_root)
    from pysat.formula import CNF
    from pysat.solvers import Solver

    started = time.monotonic()
    meta = json.loads(BASE_META.read_text(encoding="utf-8"))
    e75_audit = json.loads(E75_AUDIT.read_text(encoding="utf-8"))
    assert e75_audit["ok"] and e75_audit["totals"]["representatives"] == 352
    assert sha256(BASE_CNF) == meta["cnf_sha256"]
    with BASE_CNF.open("r", encoding="ascii") as handle:
        header = handle.readline().split()
    assert header[:2] == ["p", "cnf"]
    assert (int(header[2]), int(header[3])) == (meta["variables"], meta["clauses"])
    labels, _index, variables, _edge = coordinates()
    disjoint = sum(
        set(support_groups(labels[u])).isdisjoint(support_groups(labels[v]))
        for u, v in variables
    )
    nondisjoint = len(variables) - disjoint
    target_histogram = {1: 0, 2: 0}
    for u, v in variables:
        target_histogram[2 - len(set(labels[u]) & set(labels[v]))] += 1
    target_sum = sum(key * value for key, value in target_histogram.items())
    degree_forced = 12
    lhs_sum = 84 * (degree_forced * (degree_forced - 1) // 2) + 84 * degree_forced // 2
    base_audit = {
        "outer_edge_variables": len(variables),
        "complete_nondisjoint_assumptions": nondisjoint,
        "remaining_disjoint_edge_variables": disjoint,
        "expected_counts_ok": (len(variables), nondisjoint, disjoint) == (3486, 1806, 1680),
        "bp_equations": meta["bp_constraints"],
        "bp_forced_outer_degree": degree_forced,
        "pair_upper_bounds": meta["outer_pair_constraints"],
        "pair_target_histogram": target_histogram,
        "sum_pair_targets": target_sum,
        "sum_actual_edge_plus_two_path_terms": lhs_sum,
        "upper_bounds_are_jointly_exact": target_sum == lhs_sum == 6048,
        "equivalence_explanation": (
            "BP forces degree 12. Every actual pair LHS is at most its target in the "
            "baseline, while the sums of all actual LHS and all targets both equal "
            "6048; hence every pair row is equality. Conversely an exact fixed-local "
            "outer graph extends the one-way product helpers by their AND values. "
            "Ordinary-C4 disjoint-block rows in fixed-local CNFs follow from the "
            "full exact system (pair upper bounds plus BP block totals)."
        ),
        "ordinary_c4_scope_correction": (
            "The disjoint-block exact-one property is not asserted from BP alone: "
            "BP supplies degree/zero-overlap and the total disjoint incidence, while "
            "the opposite-C4 pair upper bound supplies the at-most-one condition."
        ),
        "base_header": [int(header[2]), int(header[3])],
        "base_metadata_sha256": sha256(BASE_META),
        "e75_source_sha256": sha256(E75),
        "e75_audit_sha256": sha256(E75_AUDIT),
        "ok": (
            (len(variables), nondisjoint, disjoint) == (3486, 1806, 1680)
            and meta["bp_constraints"] == 1176
            and meta["outer_pair_constraints"] == 3486
            and target_sum == lhs_sum == 6048
        ),
    }
    assert base_audit["ok"]

    assignments = all_e75_assignments()
    by_key = {(row["record_index"], row["representative_index"]): row for row in assignments}
    selected_assignments = [by_key[key] for key in SELECTED]
    mapping_rows = fixed_local_mapping_audit(selected_assignments)
    assert all(row["ok"] for row in mapping_rows)

    formula_started = time.monotonic()
    formula = CNF(from_file=str(BASE_CNF))
    with Solver(name="cadical195", bootstrap_with=formula.clauses) as solver:
        load_seconds = time.monotonic() - formula_started
        del formula
        gc.collect()
        probes = []
        cores = []
        for selected in selected_assignments:
            before = solver.accum_stats()
            solve_started = time.monotonic()
            solver.conf_budget(CONFLICT_BUDGET)
            answer = solver.solve_limited(
                assumptions=list(selected["literals"]), expect_interrupt=True
            )
            elapsed = time.monotonic() - solve_started
            after = solver.accum_stats()
            status = "SAT" if answer is True else "UNSAT" if answer is False else "UNKNOWN"
            row = {
                key: value for key, value in selected.items()
                if key not in ("literals", "literal_set", "positive_pairs")
            }
            row.update({
                "status": status,
                "solve_seconds": round(elapsed, 6),
                "stats_delta": {
                    key: after.get(key, 0) - before.get(key, 0)
                    for key in sorted(set(before) | set(after))
                },
                "formal_proof_certificate": None,
            })
            if answer is False:
                core = tuple(solver.get_core() or ())
                assert core and set(core) <= selected["literal_set"]
                core_hash = assignment_sha256(core)
                row.update({
                    "core_size": len(core),
                    "core_positive": sum(value > 0 for value in core),
                    "core_negative": sum(value < 0 for value in core),
                    "core_sha256": core_hash,
                    "core_literals": list(core),
                    "core_decoded": decode_core(core),
                })
                cores.append({
                    "source_record_index": selected["record_index"],
                    "source_representative_index": selected["representative_index"],
                    "source_global_representative_index": selected["global_representative_index"],
                    "core_sha256": core_hash,
                    "core": frozenset(core),
                })
            elif answer is True:
                positive = {literal for literal in solver.get_model() if 0 < literal <= 3486}
                checked = verify(positive)
                row["verification"] = {
                    key: value for key, value in checked.items() if key != "edges"
                }
                row["verified_srg"] = bool(checked["ok"])
                if checked["ok"]:
                    Path("scratch_root_universal_core_solution.json").write_text(
                        json.dumps(checked, indent=2) + "\n", encoding="utf-8"
                    )
            probes.append(row)
            partial = result_document(base_audit, mapping_rows, probes, {}, started, load_seconds)
            atomic_write_json(OUTPUT, partial)
            print(json.dumps({
                "record_index": row["record_index"],
                "representative_index": row["representative_index"],
                "global_representative_index": row["global_representative_index"],
                "status": status,
                "solve_seconds": row["solve_seconds"],
                "conflicts": row["stats_delta"].get("conflicts"),
                "core_size": row.get("core_size"),
            }, sort_keys=True), flush=True)
            if answer is True and row.get("verified_srg"):
                break

    coverage_rows = []
    covered_union = set()
    for core in cores:
        covered = [
            row for row in assignments if core["core"] <= row["literal_set"]
        ]
        covered_indices = [row["global_representative_index"] for row in covered]
        covered_union.update(covered_indices)
        coverage_rows.append({
            key: value for key, value in core.items() if key != "core"
        } | {
            "covered_e75_representative_count": len(covered),
            "covered_e75_global_indices": covered_indices,
            "covered_e75_keys": [
                [row["record_index"], row["representative_index"]] for row in covered
            ],
            "source_assignment_is_covered": core["source_global_representative_index"] in covered_indices,
        })
    coverage = {
        "tested_core_count": len(cores),
        "e75_assignments_scanned": len(assignments),
        "distinct_e75_assignments_covered": len(covered_union),
        "distinct_e75_global_indices_covered": sorted(covered_union),
        "per_core": coverage_rows,
        "future_e74_criterion": (
            "construct the same complete 1806 signed baseline-edge assignment and "
            "test literal-set containment against these cores; require exact base hash"
        ),
    }
    result = result_document(base_audit, mapping_rows, probes, coverage, started, load_seconds)
    atomic_write_json(OUTPUT, result)
    print(json.dumps({
        "status": result["status"],
        "probes": len(probes),
        "cores": len(cores),
        "e75_covered": len(covered_union),
        "output": str(OUTPUT),
    }, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
