"""Independent audit of the universal-baseline E75 assumption-core probe.

No SAT solve is performed here.  The script reconstructs the complete signed
assignments independently, differentially checks the fixed-local edge map for
the four probed representatives, and recomputes every core-containment result.
"""

from __future__ import annotations

from collections import Counter
import gc
import hashlib
import itertools
import json
from pathlib import Path
import sys
import time

from scratch_root_universal_core_harness import (
    PINNED_BASE_SHA256,
    audit_baseline,
    complete_signed_assignment,
    coordinate_sha256,
    enumerate_assignments,
    independent_coordinates,
    independent_normalize_catalog,
    literal_set_sha256,
    text_sha256,
)


BASE = Path("scratch_general_exact.cnf")
BASE_META = Path("scratch_general_exact_build.json")
CATALOGUE = Path("scratch_general_e75_incremental_records.json")
PROBE = Path("scratch_root_universal_core_probe.json")
SMOKE = Path("scratch_root_universal_core_harness_smoke.json")
OUTPUT = Path("scratch_root_universal_core_audit.json")
SELECTED_GLOBAL = (0, 128, 192, 288)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def require(condition, message, errors):
    if not condition:
        errors.append(message)


def independent_decode(core):
    labels, _label_index, variables, supports = independent_coordinates()
    inverse = {identifier: pair for pair, identifier in variables.items()}
    decoded = []
    for literal in core:
        u, v = inverse[abs(literal)]
        left, right = supports[u], supports[v]
        decoded.append({
            "literal": literal,
            "value": literal > 0,
            "outer_pair": [u, v],
            "labels": [list(labels[u]), list(labels[v])],
            "group_supports": [list(left), list(right)],
            "kind": "same" if left == right else "overlap",
        })
    return decoded


def fixed_local_differential(selected, errors):
    dependency_root = str(Path(".deps").resolve())
    if dependency_root not in sys.path:
        sys.path.insert(0, dependency_root)
    from scratch_e75_fixed_exact_sat import build_cnf

    _labels, _label_index, independent_variables, supports = independent_coordinates()
    rows = []
    for assignment in selected:
        started = time.monotonic()
        clauses, fixed_edge, fixed_variables, meta = build_cnf(
            assignment["global_representative_index"]
        )
        signed = {abs(literal): literal > 0 for literal in assignment["literals"]}
        local_errors = []
        boolean_count = variable_count = 0
        for pair, identifier in independent_variables.items():
            left, right = supports[pair[0]], supports[pair[1]]
            value = fixed_edge(*pair)
            if set(left).isdisjoint(right):
                variable_count += 1
                if type(value) is not int or identifier in signed:
                    local_errors.append(f"bad disjoint coordinate/value at {pair}")
            else:
                boolean_count += 1
                if type(value) is not bool or signed.get(identifier) is not value:
                    local_errors.append(f"bad fixed non-disjoint value at {pair}")
        if fixed_variables != independent_variables:
            local_errors.append("fixed-local full edge coordinate map differs")
        if (boolean_count, variable_count) != (1806, 1680):
            local_errors.append("fixed/variable outer-edge partition differs")
        if meta.get("BP_equalities") != 1176:
            local_errors.append("fixed-local BP count differs")
        if meta.get("outer_pair_equalities") != 3486:
            local_errors.append("fixed-local pair count differs")
        if meta.get("edge_variables") != 1680:
            local_errors.append("fixed-local disjoint variable count differs")
        row = {
            "global_representative_index": assignment["global_representative_index"],
            "record_index": assignment["record_index"],
            "representative_index": assignment["representative_index"],
            "fixed_boolean_non_disjoint_edges": boolean_count,
            "remaining_disjoint_edge_variables": variable_count,
            "fixed_local_clause_count": len(clauses),
            "fixed_local_variable_count": meta.get("variables"),
            "seconds": round(time.monotonic() - started, 6),
            "errors": local_errors,
            "ok": not local_errors,
        }
        errors.extend(
            f"fixed-local global {assignment['global_representative_index']}: {message}"
            for message in local_errors
        )
        rows.append(row)
        del clauses, fixed_edge, fixed_variables
        gc.collect()
    return rows


def main():
    started = time.monotonic()
    errors = []
    probe = json.loads(PROBE.read_text(encoding="utf-8"))
    smoke = json.loads(SMOKE.read_text(encoding="utf-8"))
    baseline = audit_baseline(BASE, BASE_META)
    catalogue = independent_normalize_catalog(CATALOGUE)
    independent = enumerate_assignments(catalogue)
    independent_by_global = {
        row["global_representative_index"]: row for row in independent
    }

    # Differential reconstruction against the original probe path.  The left
    # side uses only this task's independent catalogue/coordinate implementation.
    from scratch_root_universal_core_probe import all_e75_assignments

    original = all_e75_assignments()
    original_by_global = {
        row["global_representative_index"]: row for row in original
    }
    require(len(independent) == len(original) == 352, "assignment count is not 352", errors)
    assignment_mismatches = []
    for global_index in range(352):
        left = independent_by_global[global_index]
        right = original_by_global[global_index]
        if (
            left["record_index"],
            left["representative_index"],
            left["representative_id"],
            left["orbit_size"],
            left["literals"],
            left["assumption_sha256"],
        ) != (
            right["record_index"],
            right["representative_index"],
            right["representative_id"],
            right["orbit_size"],
            right["literals"],
            right["assumption_sha256"],
        ):
            assignment_mismatches.append(global_index)
    require(not assignment_mismatches, "independent/original assignments differ", errors)

    # Coordinate and exact-system arithmetic, independently recomputed.
    labels, _label_index, variables, supports = independent_coordinates()
    from scratch_general_exact_sat import coordinates as baseline_coordinates

    built_labels, _built_index, built_variables, _built_edge = baseline_coordinates()
    require(tuple(built_labels) == labels, "baseline-builder label order differs", errors)
    require(built_variables == variables, "baseline-builder edge variable map differs", errors)
    disjoint_ids = {
        identifier
        for (u, v), identifier in variables.items()
        if set(supports[u]).isdisjoint(supports[v])
    }
    nondisjoint_ids = set(range(1, 3487)) - disjoint_ids
    require(len(disjoint_ids) == 1680, "disjoint variable count differs", errors)
    require(len(nondisjoint_ids) == 1806, "non-disjoint variable count differs", errors)
    for row in independent:
        require(
            {abs(literal) for literal in row["literals"]} == nondisjoint_ids,
            f"assignment {row['global_representative_index']} domain is incomplete",
            errors,
        )
        require(
            row["positive_assumptions"] + row["negative_assumptions"] == 1806,
            f"assignment {row['global_representative_index']} sign count differs",
            errors,
        )

    pair_targets = Counter(
        2 - len(set(labels[u]).intersection(labels[v]))
        for u, v in variables
    )
    rhs_symbol_sum_per_vertex = 4 * 1 + 10 * 2
    outer_degree = rhs_symbol_sum_per_vertex // 2
    outer_edges = 84 * outer_degree // 2
    common_outer_pair_sum = 84 * (outer_degree * (outer_degree - 1) // 2)
    actual_lhs_sum = outer_edges + common_outer_pair_sum
    target_sum = sum(target * count for target, count in pair_targets.items())
    require(pair_targets == Counter({2: 2562, 1: 924}), "pair target histogram differs", errors)
    require(actual_lhs_sum == target_sum == 6048, "global equality sum differs", errors)

    selected = [independent_by_global[index] for index in SELECTED_GLOBAL]
    fixed_rows = fixed_local_differential(selected, errors)
    selected_probe = {
        row["global_representative_index"]: row for row in probe["selected"]
    }
    require(set(selected_probe) == set(SELECTED_GLOBAL), "probe selected set differs", errors)

    core_rows = []
    covered_union = set()
    for global_index in SELECTED_GLOBAL:
        source = independent_by_global[global_index]
        row = selected_probe[global_index]
        core = tuple(map(int, row.get("core_literals", ())))
        core_set = frozenset(core)
        local_errors = []
        if row.get("status") != "UNSAT":
            local_errors.append("status is not UNSAT")
        if not core or len(core) != len(core_set):
            local_errors.append("core is empty or repeats a literal")
        if len({abs(literal) for literal in core}) != len(core):
            local_errors.append("core repeats a variable/opposite sign")
        if not core_set <= source["literal_set"]:
            local_errors.append("signed core is not a subset of source assumptions")
        if not {abs(literal) for literal in core} <= nondisjoint_ids:
            local_errors.append("core contains a non-assumption/non-disjoint variable")
        if text_sha256(core) != row.get("core_sha256"):
            local_errors.append("reported ordered core SHA-256 differs")
        if independent_decode(core) != row.get("core_decoded"):
            local_errors.append("decoded core semantics differ")
        if source["assumption_sha256"] != row.get("assumption_sha256"):
            local_errors.append("source assumption hash differs")
        covered = [
            candidate["global_representative_index"]
            for candidate in independent
            if core_set <= candidate["literal_set"]
        ]
        unsigned_covered = [
            candidate["global_representative_index"]
            for candidate in independent
            if {abs(literal) for literal in core}
            <= {abs(literal) for literal in candidate["literals"]}
        ]
        reported_coverage = next(
            item
            for item in probe["cross_representative_coverage"]["per_core"]
            if item["source_global_representative_index"] == global_index
        )
        if covered != reported_coverage["covered_e75_global_indices"]:
            local_errors.append("recomputed signed containment differs")
        if covered != [global_index]:
            local_errors.append("core unexpectedly covers a different E75 assignment")
        if len(unsigned_covered) != 352:
            local_errors.append("unsigned-domain diagnostic does not cover all assignments")
        covered_union.update(covered)
        core_rows.append({
            "global_representative_index": global_index,
            "record_index": source["record_index"],
            "representative_index": source["representative_index"],
            "assumption_sha256": source["assumption_sha256"],
            "status": row.get("status"),
            "conflicts": row.get("stats_delta", {}).get("conflicts"),
            "solve_seconds": row.get("solve_seconds"),
            "core_size": len(core),
            "core_positive": sum(literal > 0 for literal in core),
            "core_negative": sum(literal < 0 for literal in core),
            "reported_ordered_core_sha256": row.get("core_sha256"),
            "canonical_literal_set_sha256": literal_set_sha256(core),
            "signed_e75_covered_global_indices": covered,
            "unsigned_variable_only_e75_covered_count": len(unsigned_covered),
            "errors": local_errors,
            "ok": not local_errors,
        })
        errors.extend(f"core global {global_index}: {message}" for message in local_errors)
    require(covered_union == set(SELECTED_GLOBAL), "four-core coverage union differs", errors)

    smoke_statuses = {
        int(key.split(":")[0][1:]) * 100000 + int(key.split(":")[1][1:]): value["status"]
        for key, value in smoke.get("results", {}).items()
    }
    require(len(smoke_statuses) == 4, "harness smoke result count differs", errors)
    require(
        all(status == "COVERED_UNSAT" for status in smoke_statuses.values()),
        "harness smoke did not cover all four source rows",
        errors,
    )

    record_sizes = Counter(row["record_index"] for row in independent)
    positive_histogram = Counter(row["positive_assumptions"] for row in independent)
    document = {
        "model": "independent audit of universal exact-CNF assumption cores",
        "ok": not errors,
        "errors": errors,
        "inputs": {
            "base_cnf": str(BASE),
            "base_cnf_sha256": sha256(BASE),
            "base_metadata_sha256": sha256(BASE_META),
            "e75_catalogue": str(CATALOGUE),
            "e75_catalogue_sha256": sha256(CATALOGUE),
            "probe": str(PROBE),
            "probe_sha256_after_scope_wording_correction": sha256(PROBE),
            "harness_smoke": str(SMOKE),
            "harness_smoke_sha256": sha256(SMOKE),
        },
        "baseline_coordinate_audit": baseline | {
            "pinned_sha256_match": baseline["sha256"] == PINNED_BASE_SHA256,
            "label_count": len(labels),
            "outer_edge_variable_count": len(variables),
            "non_disjoint_assumption_variable_count": len(nondisjoint_ids),
            "remaining_disjoint_variable_count": len(disjoint_ids),
            "coordinate_map_matches_baseline_builder": (
                tuple(built_labels) == labels and built_variables == variables
            ),
        },
        "independent_assignment_reconstruction": {
            "does_not_import_shared_or_fixed_encoder": True,
            "record_count": catalogue["record_count"],
            "representative_count": len(independent),
            "representatives_per_record": {
                str(index): record_sizes[index] for index in sorted(record_sizes)
            },
            "unique_assignment_hashes": len({row["assumption_sha256"] for row in independent}),
            "positive_assumption_histogram": {
                str(count): multiplicity
                for count, multiplicity in sorted(positive_histogram.items())
            },
            "all_352_literal_vectors_match_original_probe_path": not assignment_mismatches,
            "mismatching_global_indices": assignment_mismatches,
        },
        "fixed_local_differential": fixed_rows,
        "exact_system_equivalence": {
            "bp_symbol_rhs_sum_per_outer_vertex": rhs_symbol_sum_per_vertex,
            "forced_outer_degree": outer_degree,
            "forced_outer_edges": outer_edges,
            "forced_common_outer_two_path_sum": common_outer_pair_sum,
            "actual_edge_plus_common_sum": actual_lhs_sum,
            "pair_target_histogram": dict(sorted(pair_targets.items())),
            "pair_target_sum": target_sum,
            "universal_inequalities_become_equalities": actual_lhs_sum == target_sum,
            "ordinary_c4_block_scope": (
                "Not a BP-only claim. BP fixes degree 12 and makes overlap blocks "
                "incident with a C4 zero, hence the C4 has 40 disjoint incidences. "
                "Each opposite pair in the C4 already has its two internal common "
                "neighbours, so the outer-pair upper bound makes every external "
                "vertex incident at most once. There are exactly 40 vertices on "
                "disjoint supports, so every such incidence is exactly one."
            ),
            "projected_edge_solution_equivalence": (
                "With all 1806 non-disjoint edge values fixed, the universal CNF "
                "and the fixed-local CNF have the same feasible assignments on the "
                "remaining 1680 disjoint outer edges. Universal one-way product "
                "helpers can be set to exact AND values in the converse direction."
            ),
            "ok": actual_lhs_sum == target_sum == 6048 and all(row["ok"] for row in fixed_rows),
        },
        "core_audit": {
            "solver_core_semantics_used": (
                "For exact baseline F, CaDiCaL get_core after UNSAT under A returns "
                "C subset A with F AND C UNSAT. Therefore C subset B implies F AND B UNSAT."
            ),
            "required_match": "exact signed-literal containment",
            "unsigned_variable_match_is_unsafe": True,
            "exact_baseline_hash_required": PINNED_BASE_SHA256,
            "rows": core_rows,
            "distinct_e75_assignments_covered": len(covered_union),
            "covered_e75_global_indices": sorted(covered_union),
            "cross_source_e75_coverage": 0,
            "future_e74_evaluated": False,
            "future_e74_note": (
                "E74 has not yet been tested. Its normalized representatives must be "
                "converted to complete 1806-literal assignments in the identical "
                "coordinate map before these four literal sets can be screened."
            ),
        },
        "harness_audit": {
            "path": "scratch_root_universal_core_harness.py",
            "sha256": sha256(Path("scratch_root_universal_core_harness.py")),
            "screen_only_source_rows_all_covered": all(
                status == "COVERED_UNSAT" for status in smoke_statuses.values()
            ),
            "future_catalogue_schema": (
                "normalized record(s) with supports_in_fibre_order, local_vertex_order, "
                "and complete representative present-edge lists"
            ),
        },
        "claim_boundary": (
            "Four E75 representatives only were solved on the universal baseline. "
            "The raw CaDiCaL cores cover no other E75 representative, E74 containment "
            "is not yet evaluated, and no independently checked UNSAT proof certificate exists."
        ),
        "seconds": round(time.monotonic() - started, 6),
    }
    atomic = OUTPUT.with_name(OUTPUT.name + ".tmp")
    atomic.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    atomic.replace(OUTPUT)
    print(json.dumps({
        "ok": document["ok"],
        "errors": len(errors),
        "cores": len(core_rows),
        "e75_covered": len(covered_union),
        "output": str(OUTPUT),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
