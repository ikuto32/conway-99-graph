"""Find one signed E0=0 block control on the fixed cyclic support skeleton.

This is a single bounded CP-SAT feasibility search, not an exhaustive
nonexistence computation.  A returned witness is checked directly before it
is written.  UNKNOWN or INFEASIBLE would make no claim about the full 33,880
candidate-block system because the support skeleton is deliberately fixed.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import itertools
import json
from pathlib import Path
import sys

import scratch_theory_e0_zero_hypergraph as base


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "scratch_theory_e0_zero_hypergraph_point_control.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def legacy_support_blocks() -> tuple[tuple[int, int, int], ...]:
    blocks = tuple(
        tuple(sorted(base.SUPPORT_INDEX[base.rotate_edge(edge, shift)] for edge in seed))
        for seed in base.CYCLIC_SUPPORT_SEEDS
        for shift in range(7)
    )
    base.require(len(blocks) == len(set(blocks)) == 140, "support skeleton")
    return blocks


def rotate_support_block(block: tuple[int, int, int], shift: int) -> tuple[int, int, int]:
    return tuple(
        sorted(
            base.SUPPORT_INDEX[base.rotate_edge(base.SUPPORTS[index], shift)]
            for index in block
        )
    )


def cyclic_support_orbits() -> tuple[tuple[tuple[int, int, int], ...], ...]:
    catalogue = set()
    for block in itertools.combinations(range(21), 3):
        try:
            base.abstract_shape(tuple(base.SUPPORTS[index] for index in block))
        except AssertionError:
            continue
        orbit = tuple(sorted({rotate_support_block(block, shift) for shift in range(7)}))
        base.require(len(orbit) == 7, "cyclic support orbit size")
        catalogue.add(orbit)
    orbits = tuple(sorted(catalogue))
    base.require(len(orbits) == 170, "cyclic support orbit count")
    base.require(len({block for orbit in orbits for block in orbit}) == 1190, "abstract block coverage")
    return orbits


def find_balanced_support_skeleton(cp_model, seconds: float, workers: int, random_seed: int):
    orbits = cyclic_support_orbits()
    model = cp_model.CpModel()
    variables = [model.NewBoolVar(f"orbit_{index}") for index in range(len(orbits))]
    model.Add(sum(variables) == 20)
    for support_index, edge in enumerate(base.SUPPORTS):
        model.Add(
            sum(
                sum(support_index in block for block in orbit) * variables[index]
                for index, orbit in enumerate(orbits)
            )
            == 20
        )
        for group in edge:
            model.Add(
                sum(
                    sum(
                        support_index in block
                        and any(other != support_index and group in base.SUPPORTS[other] for other in block)
                        for block in orbit
                    )
                    * variables[index]
                    for index, orbit in enumerate(orbits)
                )
                == 4
            )

    # Prefer a sparse-overlap support control when several balanced cyclic
    # skeletons exist.  This changes only which positive-control candidate is
    # sought; it is not used as a mathematical constraint.
    shape_penalty = {"3K2": 0, "P3+K2": 0, "P4": 1, "C3": 2}
    model.Minimize(
        sum(
            shape_penalty[base.abstract_shape(tuple(base.SUPPORTS[i] for i in orbit[0]))[0]]
            * variables[index]
            for index, orbit in enumerate(orbits)
        )
    )
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = min(seconds, 30.0)
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = random_seed
    status_code = solver.Solve(model)
    base.require(status_code in (cp_model.FEASIBLE, cp_model.OPTIMAL), "balanced cyclic support skeleton")
    selected_orbits = tuple(index for index, variable in enumerate(variables) if solver.Value(variable))
    blocks = tuple(block for index in selected_orbits for block in orbits[index])
    base.require(len(blocks) == len(set(blocks)) == 140, "balanced support blocks")
    port = support_port_audit(blocks)
    base.require(port["violation_count"] == 0, "balanced support ports")
    shape_counts = Counter(
        base.abstract_shape(tuple(base.SUPPORTS[index] for index in block))[0]
        for block in blocks
    )
    return blocks, {
        "status": solver.StatusName(status_code),
        "wall_seconds": solver.WallTime(),
        "branches": solver.NumBranches(),
        "conflicts": solver.NumConflicts(),
        "cyclic_orbits_available": len(orbits),
        "cyclic_orbits_selected": len(selected_orbits),
        "selected_orbit_indices": list(selected_orbits),
        "shape_counts": dict(sorted(shape_counts.items())),
        "support_port_audit": port,
    }


def candidates_for_skeleton(
    blocks: tuple[tuple[int, int, int], ...]
) -> tuple[tuple[int, tuple[int, int, int]], ...]:
    by_support: dict[int, list[int]] = defaultdict(list)
    for point_index, point in enumerate(base.POINTS):
        by_support[base.SUPPORT_INDEX[base.support(point)]].append(point_index)
    rows = []
    per_shape = Counter()
    support_shape_counts = Counter()
    for block_index, support_block in enumerate(blocks):
        shape, _ = base.abstract_shape(tuple(base.SUPPORTS[index] for index in support_block))
        support_shape_counts[shape] += 1
        count_before = len(rows)
        for point_indices in itertools.product(*(by_support[index] for index in support_block)):
            points = tuple(base.POINTS[index] for index in point_indices)
            if all(
                not (base.exact_symbols(left) & base.exact_symbols(right))
                for left, right in itertools.combinations(points, 2)
            ):
                rows.append((block_index, tuple(sorted(point_indices))))
        per_shape[shape] += len(rows) - count_before
    candidate_factor = {"3K2": 64, "P3+K2": 32, "P4": 16, "C3": 8}
    base.require(
        per_shape == Counter({shape: count * candidate_factor[shape] for shape, count in support_shape_counts.items()}),
        "candidate shape split",
    )
    return tuple(rows)


def support_port_audit(blocks: tuple[tuple[int, int, int], ...]) -> dict[str, object]:
    rows = []
    for support_index, edge in enumerate(base.SUPPORTS):
        for group in edge:
            value = sum(
                support_index in block
                and any(other != support_index and group in base.SUPPORTS[other] for other in block)
                for block in blocks
            )
            rows.append({"support": list(edge), "group": group, "overlap_blocks": value})
    histogram = Counter(row["overlap_blocks"] for row in rows)
    violations = [row for row in rows if row["overlap_blocks"] != 4]
    return {
        "necessary_equation": (
            "for every support fibre e and endpoint group g in e, exactly four selected blocks "
            "containing e must contain a second support through g"
        ),
        "reason": "sum the four signed point/group U exact-one rows in fibre e",
        "row_count": len(rows),
        "value_histogram": {str(value): count for value, count in sorted(histogram.items())},
        "violation_count": len(violations),
        "violations": violations,
    }


def u_coefficient(point_index: int, group: int, triple: tuple[int, int, int]) -> int:
    point = base.POINTS[point_index]
    count = 0
    for other_index in triple:
        if other_index == point_index:
            continue
        other = base.POINTS[other_index]
        if group not in base.support(other):
            continue
        if base.sign_at_group(point, group) != base.sign_at_group(other, group):
            count += 1
    return count


def direct_verify(
    blocks: tuple[tuple[int, int, int], ...],
    candidates: tuple[tuple[int, tuple[int, int, int]], ...],
    selected_indices: tuple[int, ...],
) -> dict[str, object]:
    base.require(len(selected_indices) == 140, "selected block count")
    selected = [candidates[index] for index in selected_indices]
    base.require(Counter(block_index for block_index, _ in selected) == Counter(range(140)), "one per skeleton block")

    degrees = Counter(point for _, triple in selected for point in triple)
    base.require(degrees == Counter({point: 5 for point in range(84)}), "signed point degrees")
    pair_counts = Counter(
        pair
        for _, triple in selected
        for pair in itertools.combinations(triple, 2)
    )
    base.require(max(pair_counts.values(), default=0) == 1, "point-level linearity")

    u_rows = {}
    for point_index, point in enumerate(base.POINTS):
        for group in base.support(point):
            value = sum(
                u_coefficient(point_index, group, triple)
                for _, triple in selected
                if point_index in triple
            )
            base.require(value == 1, "point/group U exact-one")
            u_rows[f"{point_index}:{group}"] = value

    shape_counts = Counter(
        base.abstract_shape(tuple(base.support(base.POINTS[index]) for index in triple))[0]
        for _, triple in selected
    )
    base.require(shape_counts == {"3K2": 56, "P3+K2": 84}, "selected shape counts")
    base.require(all(blocks[block_index] == tuple(sorted(base.SUPPORT_INDEX[base.support(base.POINTS[index])] for index in triple)) for block_index, triple in selected), "support projection")
    return {
        "selected_blocks": len(selected),
        "signed_point_degree_histogram": dict(sorted(Counter(degrees.values()).items())),
        "point_pair_multiplicity_histogram": dict(sorted(Counter(pair_counts.values()).items())),
        "point_group_U_rows": len(u_rows),
        "point_group_U_value_histogram": dict(sorted(Counter(u_rows.values()).items())),
        "shape_counts": dict(sorted(shape_counts.items())),
    }


def solve(seconds: float, workers: int, random_seed: int) -> dict[str, object]:
    sys.path.insert(0, str((ROOT / ".ortools").resolve()))
    from ortools.sat.python import cp_model

    old_blocks = legacy_support_blocks()
    old_port_audit = support_port_audit(old_blocks)
    base.require(old_port_audit["violation_count"] == 42, "legacy support control port audit")
    blocks, support_search = find_balanced_support_skeleton(
        cp_model, seconds, workers, random_seed
    )
    candidates = candidates_for_skeleton(blocks)
    port_audit = support_port_audit(blocks)
    model = cp_model.CpModel()
    variables = [model.NewBoolVar(f"b_{index}") for index in range(len(candidates))]

    by_block: dict[int, list[int]] = defaultdict(list)
    by_point: dict[int, list[int]] = defaultdict(list)
    by_pair: dict[tuple[int, int], list[int]] = defaultdict(list)
    by_point_group: dict[tuple[int, int], list[tuple[int, int]]] = defaultdict(list)
    for candidate_index, (block_index, triple) in enumerate(candidates):
        by_block[block_index].append(candidate_index)
        for point_index in triple:
            by_point[point_index].append(candidate_index)
            for group in base.support(base.POINTS[point_index]):
                coefficient = u_coefficient(point_index, group, triple)
                if coefficient:
                    by_point_group[(point_index, group)].append((candidate_index, coefficient))
        for pair in itertools.combinations(triple, 2):
            by_pair[pair].append(candidate_index)

    for block_index in range(140):
        model.AddExactlyOne(variables[index] for index in by_block[block_index])
    for point_index in range(84):
        model.Add(sum(variables[index] for index in by_point[point_index]) == 5)
        for group in base.support(base.POINTS[point_index]):
            model.Add(
                sum(coefficient * variables[index] for index, coefficient in by_point_group[(point_index, group)])
                == 1
            )
    for indices in by_pair.values():
        if len(indices) > 1:
            model.Add(sum(variables[index] for index in indices) <= 1)

    # Safe WLOG: independent flips of the seven root-neighbour mate pairs act
    # transitively on the 32 signed candidates of the first P3+K2 support block.
    first = min(by_block[0], key=lambda index: candidates[index][1])
    model.Add(variables[first] == 1)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = random_seed
    solver.parameters.stop_after_first_solution = True
    solver.parameters.cp_model_presolve = True
    status_code = solver.Solve(model)
    status = solver.StatusName(status_code)
    result: dict[str, object] = {
        "status": "SIGNED_POINT_CONTROL_SEARCH_" + status,
        "scope": (
            "single feasibility search on one fixed 140-block support skeleton; "
            "INFEASIBLE or UNKNOWN would not exclude the full 33,880-block system"
        ),
        "input": {
            "base_script": base.__file__,
            "base_script_sha256": sha256(Path(base.__file__)),
            "global_allowed_signed_blocks": 33880,
            "fixed_support_blocks": len(blocks),
            "signed_candidates_on_fixed_skeleton": len(candidates),
            "safe_first_block_sign_WLOG": True,
            "support_port_audit": port_audit,
            "legacy_shape_only_control": {
                "blocks": len(old_blocks),
                "support_port_audit": old_port_audit,
                "conclusion": (
                    "the old support-only control cannot lift to the 168 point/group U exact-one rows"
                ),
            },
            "balanced_support_search": support_search,
        },
        "model": {
            "Boolean_variables": len(variables),
            "one_candidate_per_support_block_rows": 140,
            "signed_point_degree_5_rows": 84,
            "point_group_U_exact_one_rows": 168,
            "point_pair_linearity_rows": sum(len(indices) > 1 for indices in by_pair.values()),
        },
        "solver": {
            "status": status,
            "wall_seconds": solver.WallTime(),
            "branches": solver.NumBranches(),
            "conflicts": solver.NumConflicts(),
            "workers": workers,
            "random_seed": random_seed,
            "time_limit_seconds": seconds,
        },
        "claim_boundary": "a feasible witness is only a necessary-condition control, never a Conway graph",
    }
    if status_code in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        selected_indices = tuple(index for index, variable in enumerate(variables) if solver.Value(variable))
        result["status"] = "SIGNED_POINT_CONTROL_FOUND"
        result["direct_verification"] = direct_verify(blocks, candidates, selected_indices)
        result["selected_signed_blocks"] = [
            [list(base.POINTS[point]) for point in candidates[index][1]]
            for index in selected_indices
        ]
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seconds", type=float, default=120.0)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--random-seed", type=int, default=6500)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    result = solve(args.seconds, args.workers, args.random_seed)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("status", "model", "solver")}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
