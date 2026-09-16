"""Audit and continue the fast exhaustive E0=71 weighted-port census."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import scratch_root_e71_q2_compression as e71
import scratch_root_e73_q4_compression as generic


FAST = Path("scratch_root_e71_weighted_port_fast.json")
OUTPUT = Path("scratch_root_e71_weighted_port_fast_audit.json")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def validate_fast():
    e71.configure()
    fast = json.loads(FAST.read_text(encoding="utf-8"))
    plan = json.loads(e71.PLAN_PATH.read_text(encoding="utf-8"))
    assert fast["status"] == "COMPLETE"
    assert fast["total_deficit"] == 13
    assert fast["capacity_passing_labelled_placements"] == plan["coverage"][
        "capacity_passing_labelled_placements"
    ] == 486_185_889
    assert fast["balanced_labelled_placements"] + fast[
        "unbalanced_labelled_placements"
    ] == fast["capacity_passing_labelled_placements"]
    assert fast["balanced_orbits"] == len(fast["records"])

    seen_codes = set()
    orbit_sum = 0
    counts = defaultdict(lambda: {"orbits": 0, "labelled": 0})
    for record in fast["records"]:
        code = int(record["representative_code_hex"], 16)
        assert code not in seen_codes
        seen_codes.add(code)
        state = generic.decode(code)
        partition = tuple(sorted((value for value in state if value), reverse=True))
        assert partition == tuple(record["partition"])
        assert sum(partition) == 13
        assert generic.q_capacity(partition) >= 2
        assert generic.sparse_weighted_port_balance(generic.nonzero_entries(code))
        orbit_size = int(record["orbit_size"])
        assert 5040 % orbit_size == 0
        orbit_sum += orbit_size
        counts[partition]["orbits"] += 1
        counts[partition]["labelled"] += orbit_size
    assert orbit_sum == fast["balanced_labelled_placements"] == fast[
        "orbit_image_union_size"
    ] == 16_939_440

    # Cross-check every Python partition scan that had independently reached EOF.
    completed_crosschecks = []
    for plan_row in plan["rows"]:
        index = int(plan_row["partition_index"])
        path = e71.part_path(index)
        if not path.exists():
            continue
        part = json.loads(path.read_text(encoding="utf-8"))
        if part.get("status") != "COMPLETE" or "balanced_raw_orbits" not in part:
            continue
        expected = {
            (int(row["representative_code_hex"], 16), int(row["orbit_size"]))
            for row in part["balanced_raw_orbits"]
        }
        partition = tuple(part["partition"])
        actual = {
            (int(row["representative_code_hex"], 16), int(row["orbit_size"]))
            for row in fast["records"] if tuple(row["partition"]) == partition
        }
        assert actual == expected
        completed_crosschecks.append({
            "partition_index": index,
            "partition": list(partition),
            "orbits": len(actual),
            "labelled": sum(size for _code, size in actual),
            "exact_set_equality": True,
            "python_partition_sha256": sha256(path),
        })

    assert len(completed_crosschecks) >= 15
    return fast, plan, counts, completed_crosschecks


def make_rows(fast):
    rows = []
    for record in fast["records"]:
        code = int(record["representative_code_hex"], 16)
        state = generic.decode(code)
        orbit_size = int(record["orbit_size"])
        rows.append({
            "partition": list(record["partition"]),
            "representative_code_hex": hex(code),
            "orbit_size": orbit_size,
            "weighted_stabilizer_order": 5040 // orbit_size,
            "exceptional_supports": generic.base.state_description(state),
            "maximum_Q_capacity": generic.q_capacity(tuple(record["partition"])),
            "filter_complete": False,
        })
    return rows


def overlap_minimum_cpsat(state):
    dependency_root = str(Path(".ortools").resolve())
    if dependency_root not in sys.path:
        sys.path.insert(0, dependency_root)
    from ortools.sat.python import cp_model

    exceptional = tuple(index for index, value in enumerate(state) if value)
    edges = tuple(
        (left, right)
        for left in exceptional for right in exceptional
        if left < right and generic.base.overlap(left, right)
    )
    demands = [4 * value for value in state]
    model = cp_model.CpModel()
    variables = {}
    squares = {}
    incident = defaultdict(list)
    for left, right in edges:
        upper = min(demands[left], demands[right])
        variable = model.new_int_var(0, upper, f"x_{left}_{right}")
        square = model.new_int_var(0, upper * upper, f"q_{left}_{right}")
        model.add_element(variable, [value * value for value in range(upper + 1)], square)
        variables[left, right] = variable
        squares[left, right] = square
        incident[left].append(variable)
        incident[right].append(variable)
    for vertex in exceptional:
        model.add(sum(incident[vertex]) == demands[vertex])
    model.minimize(sum(squares.values()))
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    solver.parameters.cp_model_presolve = True
    status = solver.solve(model)
    if status == cp_model.INFEASIBLE:
        return {
            "feasible": False,
            "minimum_square": None,
            "visited_complete_assignments": 0,
            "one_minimizer": None,
            "solver": "OR-Tools CP-SAT exact integer optimization",
            "solver_status": "INFEASIBLE",
            "branches": solver.num_branches,
        }
    assert status == cp_model.OPTIMAL
    witness = [
        [left, right, solver.value(variable)]
        for (left, right), variable in variables.items()
        if solver.value(variable)
    ]
    objective = int(round(solver.objective_value))
    row_sums = [0] * 21
    square_sum = 0
    for left, right, value in witness:
        row_sums[left] += value
        row_sums[right] += value
        square_sum += value * value
    assert row_sums == demands and square_sum == objective
    return {
        "feasible": True,
        "minimum_square": objective,
        "visited_complete_assignments": 0,
        "one_minimizer": witness,
        "minimizer_verified": True,
        "solver": "OR-Tools CP-SAT exact integer optimization",
        "solver_status": "OPTIMAL",
        "branches": solver.num_branches,
    }


def filter_row_cpsat(row):
    state = generic.decode(int(row["representative_code_hex"], 16))
    entries = generic.nonzero_entries(int(row["representative_code_hex"], 16))
    balanced, balance_details = generic.sparse_weighted_port_balance(entries, with_details=True)
    assert balanced and sum(state) == 13
    diagonal = generic.diagonal_square(state)
    budget = generic.joint_budget(state)
    continuous = generic.base.continuous_disjoint_minimum(state)
    if math.ceil(continuous) > budget:
        overlap = {
            "status": "SKIPPED_BY_DISJOINT_REAL_BOUND",
            "feasible": None,
            "minimum_square": None,
            "visited_complete_assignments": 0,
            "one_minimizer": None,
            "solver": None,
        }
    else:
        overlap = overlap_minimum_cpsat(state)
    passes = (
        overlap["feasible"] is True
        and overlap["minimum_square"] + math.ceil(continuous) <= budget
    )
    row.update({
        "support_signature": generic.compact_signature(state),
        "diagonal_square": diagonal,
        "joint_off_diagonal_square_budget": budget,
        "disjoint_continuous_minimum": str(continuous),
        "disjoint_continuous_ceiling": math.ceil(continuous),
        "weighted_port_balance": True,
        "weighted_port_balance_details": balance_details,
        "overlap": overlap,
        "passes_weighted_port_overlap_and_real_relaxation": passes,
        "filter_complete": True,
    })


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--filter", action="store_true")
    parser.add_argument("--filter-cpsat", action="store_true")
    args = parser.parse_args()
    fast, plan, counts, crosschecks = validate_fast()
    rows = make_rows(fast)
    if OUTPUT.exists():
        previous = json.loads(OUTPUT.read_text(encoding="utf-8"))
        if previous.get("fast_sha256") == sha256(FAST):
            old = {
                row["representative_code_hex"]: row for row in previous.get("rows", [])
                if row.get("filter_complete")
            }
            for index, row in enumerate(rows):
                if row["representative_code_hex"] in old:
                    rows[index] = old[row["representative_code_hex"]]

    if args.filter or args.filter_cpsat:
        for index, row in enumerate(rows):
            if row["filter_complete"]:
                continue
            if args.filter_cpsat:
                filter_row_cpsat(row)
            else:
                generic.filter_row(row)
            if (index + 1) % 50 == 0:
                generic.atomic_json(OUTPUT, {
                    "status": "FILTERING_COMPRESSION",
                    "fast_sha256": sha256(FAST),
                    "filter_engine": (
                        "OR-Tools CP-SAT" if args.filter_cpsat else "exact recursion"
                    ),
                    "rows": rows,
                })
                print(json.dumps({
                    "filtered": index + 1,
                    "total": len(rows),
                    "survivors_so_far": sum(
                        item.get("passes_weighted_port_overlap_and_real_relaxation", False)
                        for item in rows[: index + 1]
                    ),
                }), flush=True)

    complete = all(row["filter_complete"] for row in rows)
    summary = generic.summarize_rows(rows)
    row_by_code = {row["representative_code_hex"]: row for row in rows}
    recursive_filter_crosschecks = []
    if complete:
        for check in crosschecks:
            part_path = e71.part_path(check["partition_index"])
            part = json.loads(part_path.read_text(encoding="utf-8"))
            for old in part.get("rows", []):
                new = row_by_code[old["representative_code_hex"]]
                assert old["filter_complete"]
                assert old["overlap"]["feasible"] == new["overlap"]["feasible"]
                assert old["overlap"]["minimum_square"] == new["overlap"]["minimum_square"]
                assert old["passes_weighted_port_overlap_and_real_relaxation"] == new[
                    "passes_weighted_port_overlap_and_real_relaxation"
                ]
                recursive_filter_crosschecks.append({
                    "partition_index": check["partition_index"],
                    "representative_code_hex": old["representative_code_hex"],
                    "minimum_square": new["overlap"]["minimum_square"],
                    "exact_match": True,
                })
    partition_summary = []
    for partition in sorted(counts, reverse=True):
        relevant = [row for row in rows if tuple(row["partition"]) == partition]
        partition_summary.append({
            "partition": list(partition),
            "balanced_orbits": counts[partition]["orbits"],
            "balanced_labelled": counts[partition]["labelled"],
            "filter_complete": sum(row["filter_complete"] for row in relevant),
            "spectral_real_survivors": sum(
                row.get("passes_weighted_port_overlap_and_real_relaxation", False)
                for row in relevant
            ),
            "spectral_real_surviving_labelled": sum(
                row["orbit_size"]
                for row in relevant
                if row.get("passes_weighted_port_overlap_and_real_relaxation", False)
            ),
        })
    result = {
        "status": "COMPLETE" if complete else "FAST_CENSUS_AUDITED_FILTER_PENDING",
        "model": "E0=71,Q>=2 fast weighted-port census and compression filter",
        "fast": str(FAST),
        "fast_sha256": sha256(FAST),
        "plan": str(e71.PLAN_PATH),
        "plan_sha256": sha256(e71.PLAN_PATH),
        "coverage": {
            "capacity_passing_labelled_placements": fast[
                "capacity_passing_labelled_placements"
            ],
            "balanced_labelled_placements": fast["balanced_labelled_placements"],
            "unbalanced_labelled_placements": fast["unbalanced_labelled_placements"],
            "balanced_orbits": fast["balanced_orbits"],
            "orbit_size_sum": sum(row["orbit_size"] for row in rows),
        },
        "independent_completed_partition_crosschecks": crosschecks,
        "independent_recursive_vs_cpsat_filter_crosschecks": recursive_filter_crosschecks,
        "summary": summary,
        "partition_summary": partition_summary,
        "rows": rows,
        "checks": {
            "every_record_decodes_to_deficit_13": True,
            "every_record_has_Q_capacity_at_least_2": True,
            "every_record_satisfies_weighted_port_balance": True,
            "representative_codes_unique": True,
            "all_orbit_sizes_divide_5040": True,
            "orbit_sum_identity": True,
            "completed_python_partition_exact_set_crosschecks": len(crosschecks),
            "recursive_vs_cpsat_exact_minimum_crosschecks": len(
                recursive_filter_crosschecks
            ),
        },
        "claim_boundary": (
            "This is an exhaustive necessary support census. COMPLETE means the "
            "overlap/real spectral compression filter was also evaluated, not that "
            "the E0=71 graph branch was excluded."
        ),
    }
    generic.atomic_json(OUTPUT, result)
    print(json.dumps({
        "status": result["status"],
        "balanced_orbits": summary["balanced_orbits"],
        "filtered": summary["filter_rows_complete"],
        "survivors": summary["spectral_real_survivors"],
        "crosschecks": len(crosschecks),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
