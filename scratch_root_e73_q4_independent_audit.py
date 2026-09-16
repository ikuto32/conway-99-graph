"""Independent audit of the self-contained E0=73, Q>=4 reduction.

This program deliberately does not import either E73 producer.  It
reconstructs the four-vertex fibre catalogue, Q statistic, port incidences,
the exact Hall criterion, S7 actions, Burnside counts, overlap integer
minimum, and disjoint real minimum from their definitions.

The expensive port check visits every complete assignment with Q>=4 (there
are 4,758,382), performs the group tests only at a complete leaf, and compares
the exact surviving tuple set with the producer output.  Thus it does not
reuse the producer's prefix lookahead/pruning logic.
"""

from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import itertools
import json
import math
import os
from functools import lru_cache
from pathlib import Path
import time


PLAN_PATH = Path("scratch_root_e73_q4_compression_plan.json")
COMPRESSION_PATH = Path("scratch_root_e73_q4_compression_audit.json")
PORT_PATH = Path("scratch_root_e73_q4_port_census.json")
SIDE_AUDIT_PATH = Path("scratch_root_side_bound_selfcontained_audit.json")
OUTPUT_PATH = Path("scratch_root_e73_q4_independent_audit.json")
SUMMARY_PATH = Path("scratch_root_e73_q4_independent_audit.md")

TOTAL_DEFICIT = 11
E0 = 73
Q_MIN = 4
SPECTRAL_UPPER = 4660
DISJOINT_CONSTANT = 3184
SUPPORTS = tuple(itertools.combinations(range(7), 2))
SUPPORT_INDEX = {support: index for index, support in enumerate(SUPPORTS)}
SHIFTS = tuple(3 * index for index in range(21))


def part_path(index: int) -> Path:
    return Path(f"scratch_root_e73_q4_independent_port_part_{index:02d}.json")


def compression_part_path(index: int) -> Path:
    return Path(f"scratch_root_e73_q4_compression_part_{index:02d}.json")


def atomic_json(path: Path, value) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def tuple_hash(rows) -> str:
    body = json.dumps(sorted(rows), separators=(",", ":")).encode("ascii")
    return hashlib.sha256(body).hexdigest().upper()


def product(values) -> int:
    answer = 1
    for value in values:
        answer *= value
    return answer


def integer_partitions(total: int, maximum: int = 4):
    if total == 0:
        yield ()
        return
    for first in range(min(total, maximum), 0, -1):
        for tail in integer_partitions(total - first, first):
            yield (first,) + tail


PARTITIONS = tuple(integer_partitions(TOTAL_DEFICIT))
assert len(PARTITIONS) == 27


# Independently reconstructed labelled four-vertex state catalogue.
VERTICES = ((0, 0), (0, 1), (1, 0), (1, 1))
PAIRS = tuple(itertools.combinations(range(4), 2))
SIDES = tuple(
    edge
    for edge in PAIRS
    if sum(VERTICES[edge[0]][axis] != VERTICES[edge[1]][axis] for axis in (0, 1)) == 1
)
DIAGONALS = tuple(edge for edge in PAIRS if edge not in SIDES)
FIBRE_STATES = {
    1: tuple(tuple(edges) for edges in itertools.combinations(SIDES, 3)),
    2: tuple(tuple(edges) for edges in itertools.combinations(SIDES, 2))
    + (tuple(DIAGONALS),),
    3: tuple((edge,) for edge in PAIRS),
    4: ((),),
}
assert tuple(len(FIBRE_STATES[d]) for d in range(1, 5)) == (4, 7, 6, 1)


def state_q(deficit: int, state_index: int) -> int:
    return sum(edge in DIAGONALS for edge in FIBRE_STATES[deficit][state_index])


Q_VALUES = {
    deficit: tuple(state_q(deficit, index) for index in range(len(FIBRE_STATES[deficit])))
    for deficit in range(1, 5)
}
assert Counter(Q_VALUES[1]) == Counter({0: 4})
assert Counter(Q_VALUES[2]) == Counter({0: 6, 2: 1})
assert Counter(Q_VALUES[3]) == Counter({0: 4, 1: 2})
assert Counter(Q_VALUES[4]) == Counter({0: 1})


def fibre_signature(deficit: int, state_index: int, axis: int):
    adjacency = [set() for _ in range(4)]
    for left, right in FIBRE_STATES[deficit][state_index]:
        adjacency[left].add(right)
        adjacency[right].add(left)
    result = [0, 0, 0, 0]
    for vertex, signs in enumerate(VERTICES):
        for required in (0, 1):
            present = sum(VERTICES[other][axis] == required for other in adjacency[vertex])
            assert present <= 1
            if present == 0:
                result[2 * signs[axis] + required] += 1
    assert sum(result) == 2 * deficit
    return tuple(result)


SIGNATURES = {
    deficit: tuple(
        tuple(fibre_signature(deficit, state, axis) for axis in (0, 1))
        for state in range(len(FIBRE_STATES[deficit]))
    )
    for deficit in range(1, 5)
}


def group_matchable_from_rows(rows) -> bool:
    """Hall criterion for four port categories, derived independently."""
    if not rows:
        return True
    totals = tuple(sum(row[column] for row in rows) for column in range(4))
    if totals[0] % 2 or 2 * max(row[0] for row in rows) > totals[0]:
        return False
    if totals[3] % 2 or 2 * max(row[3] for row in rows) > totals[3]:
        return False
    if totals[1] != totals[2]:
        return False
    return all(row[1] + row[2] <= totals[1] for row in rows)


def individual_ports(exceptional, assignment):
    by_group = [[] for _ in range(7)]
    for fibre, (item, state_index) in enumerate(zip(exceptional, assignment)):
        support = tuple(item["support"])
        adjacency = [set() for _ in range(4)]
        for left, right in FIBRE_STATES[item["deficit"]][state_index]:
            adjacency[left].add(right)
            adjacency[right].add(left)
        count_before = sum(map(len, by_group))
        for vertex, signs in enumerate(VERTICES):
            for axis, group in enumerate(support):
                for required in (0, 1):
                    present = sum(
                        VERTICES[other][axis] == required for other in adjacency[vertex]
                    )
                    assert present <= 1
                    if present == 0:
                        by_group[group].append(
                            (group, fibre, vertex, signs[axis], required)
                        )
        assert sum(map(len, by_group)) - count_before == 4 * item["deficit"]
    return by_group


def direct_perfect_matching(ports) -> bool:
    """Bit-mask perfect matching, independent of the closed Hall formula."""
    ports = tuple(ports)
    size = len(ports)
    if size % 2:
        return False
    compatible = [0] * size
    for left in range(size):
        for right in range(left + 1, size):
            a, b = ports[left], ports[right]
            if a[1] != b[1] and a[3] == b[4] and b[3] == a[4]:
                compatible[left] |= 1 << right
                compatible[right] |= 1 << left

    @lru_cache(maxsize=None)
    def visit(mask: int) -> bool:
        if not mask:
            return True
        candidates = []
        residual = mask
        while residual:
            bit = residual & -residual
            vertex = bit.bit_length() - 1
            available = compatible[vertex] & mask
            candidates.append((available.bit_count(), vertex, available))
            residual ^= bit
        _degree, first, available = min(candidates)
        if not available:
            return False
        remainder = mask ^ (1 << first)
        available &= remainder
        while available:
            bit = available & -available
            if visit(remainder ^ bit):
                return True
            available ^= bit
        return False

    return visit((1 << size) - 1)


def q_distribution(deficits):
    distribution = Counter({0: 1})
    for deficit in deficits:
        following = Counter()
        for before, multiplicity in distribution.items():
            for added in Q_VALUES[deficit]:
                following[before + added] += multiplicity
        distribution = following
    return distribution


def independent_port_row(source):
    exceptional = source["exceptional_supports"]
    supports = tuple(tuple(item["support"]) for item in exceptional)
    deficits = tuple(item["deficit"] for item in exceptional)
    domains = tuple(tuple(range(len(FIBRE_STATES[d]))) for d in deficits)

    incident = {
        group: tuple(index for index, support in enumerate(supports) if group in support)
        for group in range(7)
    }
    allowed = {}
    local_counts = {}
    for group, variables in incident.items():
        feasible = set()
        if not variables:
            feasible.add(())
        else:
            for local_assignment in itertools.product(*(domains[index] for index in variables)):
                rows = []
                for variable, state_index in zip(variables, local_assignment):
                    axis = supports[variable].index(group)
                    rows.append(SIGNATURES[deficits[variable]][state_index][axis])
                if group_matchable_from_rows(rows):
                    feasible.add(local_assignment)
        allowed[group] = feasible
        local_counts[group] = {
            "incident_variables": list(variables),
            "all_local_assignments": product(len(domains[index]) for index in variables),
            "formula_matchable_local_assignments": len(feasible),
        }

    distribution = q_distribution(deficits)
    predicted_target = sum(count for q, count in distribution.items() if q >= Q_MIN)
    full_product = sum(distribution.values())

    # Unlike the producer's close-groups-first traversal, put Q-capable
    # variables first and do no Hall-prefix pruning.  Every Q>=4 complete leaf
    # is explicitly subjected to all seven group tests.
    order = tuple(
        sorted(
            range(len(deficits)),
            key=lambda index: (-max(Q_VALUES[deficits[index]]), index),
        )
    )
    suffix_max = [0] * (len(order) + 1)
    for depth in range(len(order) - 1, -1, -1):
        suffix_max[depth] = (
            suffix_max[depth + 1] + max(Q_VALUES[deficits[order[depth]]])
        )

    assignment = [-1] * len(deficits)
    target_count = 0
    target_histogram = Counter()
    feasible_rows = []
    feasible_histogram = Counter()
    recursion_nodes = 0

    def visit(depth: int, q_value: int):
        nonlocal target_count, recursion_nodes
        recursion_nodes += 1
        if q_value + suffix_max[depth] < Q_MIN:
            return
        if depth == len(order):
            assert q_value >= Q_MIN and all(value >= 0 for value in assignment)
            target_count += 1
            target_histogram[q_value] += 1
            if all(
                tuple(assignment[index] for index in incident[group]) in allowed[group]
                for group in range(7)
            ):
                row = tuple(assignment)
                feasible_rows.append(row)
                feasible_histogram[q_value] += 1
            return
        variable = order[depth]
        for state_index in domains[variable]:
            assignment[variable] = state_index
            visit(
                depth + 1,
                q_value + Q_VALUES[deficits[variable]][state_index],
            )
        assignment[variable] = -1

    started = time.monotonic()
    visit(0, 0)
    elapsed = time.monotonic() - started
    feasible_set = set(feasible_rows)
    stored_rows = [tuple(row) for row in source["feasible_state_indices"]]
    stored_set = set(stored_rows)
    errors = []
    if target_count != predicted_target:
        errors.append(f"target count {target_count} != polynomial {predicted_target}")
    if target_count != source["Q_at_least_4_assignments_covered"]:
        errors.append("target count differs from census")
    if len(feasible_rows) != len(feasible_set):
        errors.append("independent feasible tuples are not unique")
    if len(stored_rows) != len(stored_set):
        errors.append("stored feasible tuples are not unique")
    if feasible_set != stored_set:
        errors.append(
            f"exact feasible tuple mismatch: missing={len(feasible_set-stored_set)}, "
            f"extra={len(stored_set-feasible_set)}"
        )
    if len(feasible_rows) != source["locally_port_feasible_Q_at_least_4_assignments"]:
        errors.append("feasible count differs from census")
    if dict(sorted(feasible_histogram.items())) != {
        int(q): count for q, count in source["feasible_Q_histogram"].items()
    }:
        errors.append("feasible Q histogram differs from census")

    direct_groups = 0
    for row in feasible_rows:
        for ports in individual_ports(exceptional, row):
            direct_groups += 1
            if not direct_perfect_matching(ports):
                errors.append(f"direct matching rejected feasible tuple {row}")
                break
        if errors:
            break

    return {
        "compression_orbit_index": source["compression_orbit_index"],
        "partition": source["partition"],
        "exceptional_support_count": len(exceptional),
        "full_labelled_fibre_state_product": full_product,
        "independent_Q_distribution": {
            str(q): count for q, count in sorted(distribution.items())
        },
        "independent_Q_at_least_4_complete_leaves": target_count,
        "independent_target_Q_histogram": {
            str(q): count for q, count in sorted(target_histogram.items())
        },
        "independent_locally_port_feasible": len(feasible_rows),
        "independent_feasible_Q_histogram": {
            str(q): count for q, count in sorted(feasible_histogram.items())
        },
        "independent_feasible_tuple_sha256": tuple_hash(feasible_rows),
        "stored_feasible_tuple_sha256": tuple_hash(stored_rows),
        "exact_feasible_tuple_set_equal": feasible_set == stored_set,
        "all_independent_feasible_tuples_unique": len(feasible_rows) == len(feasible_set),
        "all_stored_feasible_tuples_unique": len(stored_rows) == len(stored_set),
        "direct_matching_groups_checked": direct_groups,
        "all_feasible_assignments_pass_independent_direct_matching": not errors,
        "independent_variable_order": list(order),
        "complete_leaf_group_tests": 7 * target_count,
        "recursion_nodes": recursion_nodes,
        "elapsed_seconds": elapsed,
        "local_formula_catalogue": local_counts,
        "errors": errors,
        "ok": not errors,
    }


def rows_by_partition():
    source = json.loads(PORT_PATH.read_text(encoding="utf-8"))
    index_for_partition = {
        tuple(row["partition"]): row["partition_index"]
        for row in source["by_partition"]
    }
    grouped = {}
    for row in source["rows"]:
        grouped.setdefault(index_for_partition[tuple(row["partition"])], []).append(row)
    return source, grouped


def run_port_partition(index: int, force: bool = False):
    source, grouped = rows_by_partition()
    source_rows = grouped.get(index, [])
    path = part_path(index)
    input_hash = sha256(PORT_PATH)
    if path.exists() and not force:
        result = json.loads(path.read_text(encoding="utf-8"))
        if result.get("status") == "COMPLETE" and result.get("input_sha256") == input_hash:
            print(json.dumps({"partition_index": index, "status": "COMPLETE", "resume": True}))
            return result
        completed = {row["compression_orbit_index"] for row in result.get("rows", [])}
    else:
        result = {
            "status": "RUNNING",
            "model": "independent complete-leaf brute port audit for E0=73,Q>=4",
            "partition_index": index,
            "partition": source_rows[0]["partition"] if source_rows else None,
            "input": str(PORT_PATH),
            "input_sha256": input_hash,
            "input_support_orbits": len(source_rows),
            "rows": [],
        }
        completed = set()
        atomic_json(path, result)
    for offset, source_row in enumerate(source_rows):
        orbit_index = source_row["compression_orbit_index"]
        if orbit_index in completed:
            continue
        row = independent_port_row(source_row)
        result["rows"].append(row)
        atomic_json(path, result)
        print(json.dumps({
            "partition_index": index,
            "offset": offset,
            "orbit_index": orbit_index,
            "target": row["independent_Q_at_least_4_complete_leaves"],
            "feasible": row["independent_locally_port_feasible"],
            "ok": row["ok"],
            "seconds": round(row["elapsed_seconds"], 3),
        }), flush=True)
        if not row["ok"]:
            raise AssertionError(row["errors"])
    assert len(result["rows"]) == len(source_rows)
    result["status"] = "COMPLETE"
    result["summary"] = {
        "input_support_orbits": len(result["rows"]),
        "complete_Q_at_least_4_assignments_tested": sum(
            row["independent_Q_at_least_4_complete_leaves"] for row in result["rows"]
        ),
        "locally_port_feasible_assignments": sum(
            row["independent_locally_port_feasible"] for row in result["rows"]
        ),
        "direct_matching_groups_checked": sum(
            row["direct_matching_groups_checked"] for row in result["rows"]
        ),
        "all_rows_ok": all(row["ok"] for row in result["rows"]),
        "elapsed_seconds": sum(row["elapsed_seconds"] for row in result["rows"]),
    }
    atomic_json(path, result)
    return result


def support_action(permutation):
    return tuple(
        SUPPORT_INDEX[tuple(sorted((permutation[left], permutation[right])))]
        for left, right in SUPPORTS
    )


GROUP_ACTIONS = tuple(
    support_action(permutation) for permutation in itertools.permutations(range(7))
)
assert len(GROUP_ACTIONS) == len(set(GROUP_ACTIONS)) == 5040


def action_cycle_type(action):
    unseen = set(range(21))
    cycles = []
    while unseen:
        vertex = min(unseen)
        current = vertex
        length = 0
        while current in unseen:
            unseen.remove(current)
            current = action[current]
            length += 1
        assert current == vertex
        cycles.append(length)
    return tuple(sorted(cycles, reverse=True))


CYCLE_TYPES = Counter(action_cycle_type(action) for action in GROUP_ACTIONS)


def fixed_placements(cycle_type, partition):
    multiplicities = tuple(sorted(Counter(partition).items(), reverse=True))
    initial = tuple(count for _weight, count in multiplicities)
    dp = Counter({initial: 1})
    for length in cycle_type:
        following = Counter()
        for residual, count in dp.items():
            following[residual] += count
            for index, remaining in enumerate(residual):
                if remaining >= length:
                    changed = list(residual)
                    changed[index] -= length
                    following[tuple(changed)] += count
        dp = following
    return dp[tuple(0 for _ in initial)]


def burnside(partition):
    numerator = sum(
        multiplicity * fixed_placements(cycle_type, partition)
        for cycle_type, multiplicity in CYCLE_TYPES.items()
    )
    assert numerator % 5040 == 0
    return numerator // 5040, numerator


def labelled_placements(partition):
    length = len(partition)
    answer = math.factorial(21) // math.factorial(21 - length)
    for multiplicity in Counter(partition).values():
        answer //= math.factorial(multiplicity)
    return answer


def decode(code: int):
    return tuple((code >> shift) & 7 for shift in SHIFTS)


def encode(state) -> int:
    return sum(value << shift for value, shift in zip(state, SHIFTS))


def orbit_codes(state):
    result = set()
    for action in GROUP_ACTIONS:
        image = [0] * 21
        for source, target in enumerate(action):
            image[target] = state[source]
        result.add(encode(image))
    return result


def weighted_balance(state) -> bool:
    for group in range(7):
        incident = [state[index] for index, support in enumerate(SUPPORTS) if group in support]
        if sum(incident) and 2 * max(incident) > sum(incident):
            return False
    return True


def continuous_disjoint_minimum(state):
    b = [2 * value for value in state]
    total = sum(b)
    group_sums = [
        sum(value for value, support in zip(b, SUPPORTS) if group in support)
        for group in range(7)
    ]
    norm = sum(value * value for value in b)
    component_0 = Fraction(total * total, 21)
    component_1 = Fraction(7 * sum(value * value for value in group_sums) - 4 * total * total, 35)
    component_2 = Fraction(norm) - component_0 - component_1
    assert min(component_0, component_1, component_2) >= 0
    return component_0 / 20 + component_1 / 6 + component_2 / 11


def bounded_compositions(total, bounds):
    if not bounds:
        if total == 0:
            yield ()
        return
    if total < 0 or total > sum(bounds):
        return
    lower = max(0, total - sum(bounds[1:]))
    for first in range(lower, min(bounds[0], total) + 1):
        for tail in bounded_compositions(total - first, bounds[1:]):
            yield (first,) + tail


def overlap_integer_minimum(state):
    exceptional = tuple(index for index, value in enumerate(state) if value)
    neighbours = {
        left: tuple(
            right
            for right in exceptional
            if right != left and set(SUPPORTS[left]).intersection(SUPPORTS[right])
        )
        for left in exceptional
    }
    initial = tuple(4 * state[index] for index in exceptional)
    position = {support: index for index, support in enumerate(exceptional)}
    calls = 0

    @lru_cache(maxsize=None)
    def solve(residual):
        nonlocal calls
        calls += 1
        if not any(residual):
            return 0
        positive = [index for index, demand in enumerate(residual) if demand]
        node = min(
            positive,
            key=lambda index: (
                sum(residual[position[other]] > 0 for other in neighbours[exceptional[index]]),
                -residual[index],
                index,
            ),
        )
        adjacent = tuple(
            position[other]
            for other in neighbours[exceptional[node]]
            if residual[position[other]] > 0
        )
        if not adjacent:
            return math.inf
        best = math.inf
        for values in bounded_compositions(
            residual[node], tuple(residual[index] for index in adjacent)
        ):
            following = list(residual)
            following[node] = 0
            for index, value in zip(adjacent, values):
                following[index] -= value
            tail = solve(tuple(following))
            if tail < math.inf:
                best = min(best, sum(value * value for value in values) + tail)
        return best

    answer = solve(initial)
    return (None if answer == math.inf else answer), calls


def independent_compression_audit():
    plan = json.loads(PLAN_PATH.read_text(encoding="utf-8"))
    compression = json.loads(COMPRESSION_PATH.read_text(encoding="utf-8"))
    side = json.loads(SIDE_AUDIT_PATH.read_text(encoding="utf-8"))
    errors = []
    plan_rows = plan["rows"]
    if tuple(tuple(row["partition"]) for row in plan_rows) != PARTITIONS:
        errors.append("partition list/order mismatch")

    recalculated_plan = []
    for index, partition in enumerate(PARTITIONS):
        orbits, numerator = burnside(partition)
        labelled = labelled_placements(partition)
        capacity = 2 * partition.count(2) + partition.count(3)
        row = plan_rows[index]
        expected = (
            row["labelled_placements"] == labelled
            and row["weighted_S7_orbits_by_Burnside"] == orbits
            and row["Burnside_fixed_sum"] == numerator
            and row["maximum_Q_capacity"] == capacity
            and row["passes_Q_at_least_4_capacity"] == (capacity >= Q_MIN)
        )
        if not expected:
            errors.append(f"plan row {index} mismatch")
        recalculated_plan.append({
            "partition_index": index,
            "partition": list(partition),
            "labelled_placements": labelled,
            "weighted_S7_orbits": orbits,
            "Burnside_fixed_sum": numerator,
            "maximum_Q_capacity": capacity,
        })

    master_rows = compression["rows"]
    codes_seen = set()
    orbit_images_seen = set()
    overlap_calls = 0
    labelled_mass = 0
    checked_rows = []
    rows_by_partition = Counter()
    mass_by_partition = Counter()
    for row in master_rows:
        code = int(row["representative_code_hex"], 16)
        state = decode(code)
        partition = tuple(sorted((value for value in state if value), reverse=True))
        row_errors = []
        if code in codes_seen:
            row_errors.append("duplicate representative code")
        codes_seen.add(code)
        if partition != tuple(row["partition"]):
            row_errors.append("decoded partition mismatch")
        if sum(state) != TOTAL_DEFICIT:
            row_errors.append("deficit sum mismatch")
        if not weighted_balance(state):
            row_errors.append("weighted port balance fails")
        images = orbit_codes(state)
        if min(images) != code:
            row_errors.append("representative is not canonical")
        if len(images) != row["orbit_size"]:
            row_errors.append("orbit size mismatch")
        if 5040 // len(images) != row["weighted_stabilizer_order"]:
            row_errors.append("stabilizer mismatch")
        if orbit_images_seen.intersection(images):
            row_errors.append("distinct representatives have intersecting orbits")
        orbit_images_seen.update(images)
        described = [
            {
                "support_index": index,
                "support": list(SUPPORTS[index]),
                "deficit": value,
            }
            for index, value in enumerate(state)
            if value
        ]
        if described != row["exceptional_supports"]:
            row_errors.append("exceptional support description mismatch")
        capacity = 2 * partition.count(2) + partition.count(3)
        if capacity < Q_MIN or capacity != row["maximum_Q_capacity"]:
            row_errors.append("Q capacity mismatch")

        diagonal = sum((8 - 2 * value) ** 2 for value in state)
        budget_numerator = SPECTRAL_UPPER - diagonal - DISJOINT_CONSTANT
        if budget_numerator % 2:
            row_errors.append("nonintegral spectral budget")
            budget = None
        else:
            budget = budget_numerator // 2
            if diagonal != row["diagonal_square"] or budget != row["joint_off_diagonal_square_budget"]:
                row_errors.append("diagonal or joint budget mismatch")
        real_minimum = continuous_disjoint_minimum(state)
        if Fraction(row["disjoint_continuous_minimum"]) != real_minimum:
            row_errors.append("continuous disjoint minimum mismatch")
        overlap_minimum, calls = overlap_integer_minimum(state)
        overlap_calls += calls
        if overlap_minimum != row["overlap"]["minimum_square"]:
            row_errors.append("exact overlap minimum mismatch")
        if budget is not None and overlap_minimum is not None:
            expected_pass = overlap_minimum + math.ceil(real_minimum) <= budget
            if expected_pass != row["passes_weighted_port_overlap_and_real_relaxation"]:
                row_errors.append("spectral real pass flag mismatch")

        rows_by_partition[partition] += 1
        mass_by_partition[partition] += len(images)
        labelled_mass += len(images)
        checked_rows.append({
            "partition": list(partition),
            "orbit_index": row["orbit_index"],
            "representative_code_hex": row["representative_code_hex"],
            "orbit_size": len(images),
            "stabilizer_order": 5040 // len(images),
            "independent_overlap_minimum_square": overlap_minimum,
            "independent_disjoint_continuous_minimum": str(real_minimum),
            "errors": row_errors,
            "ok": not row_errors,
        })
        errors.extend(f"row {partition}/{row['orbit_index']}: {error}" for error in row_errors)

    part_checks = []
    for index, partition in enumerate(PARTITIONS):
        part = json.loads(compression_part_path(index).read_text(encoding="utf-8"))
        plan_row = plan_rows[index]
        part_errors = []
        if plan_row["passes_Q_at_least_4_capacity"]:
            if part["status"] != "COMPLETE":
                part_errors.append("passing part is not COMPLETE")
            coverage = part["coverage"]
            if coverage["labelled_placements_scanned"] != plan_row["labelled_placements"]:
                part_errors.append("labelled scan count mismatch")
            if coverage["balanced_labelled_placements"] + coverage["unbalanced_labelled_placements"] != coverage["labelled_placements_scanned"]:
                part_errors.append("balance labelled identity mismatch")
            if coverage["balanced_orbits_materialized"] + coverage["unbalanced_orbits_by_difference"] != plan_row["weighted_S7_orbits_by_Burnside"]:
                part_errors.append("balance orbit identity mismatch")
            if rows_by_partition[partition] != coverage["balanced_orbits_materialized"]:
                part_errors.append("master row count mismatch")
            if mass_by_partition[partition] != coverage["balanced_labelled_placements"]:
                part_errors.append("balanced labelled orbit mass mismatch")
        else:
            if part["status"] != "COMPLETE_Q_CAPACITY_EXCLUDED":
                part_errors.append("capacity-excluded part status mismatch")
            if part["rows"]:
                part_errors.append("capacity-excluded part unexpectedly has rows")
        part_checks.append({
            "partition_index": index,
            "partition": list(partition),
            "status": part["status"],
            "errors": part_errors,
            "ok": not part_errors,
        })
        errors.extend(f"part {index}: {error}" for error in part_errors)

    totals = {
        "partition_count": len(PARTITIONS),
        "all_labelled_placements": sum(row["labelled_placements"] for row in recalculated_plan),
        "all_weighted_S7_orbits": sum(row["weighted_S7_orbits"] for row in recalculated_plan),
        "capacity_passing_partitions": sum(row["maximum_Q_capacity"] >= Q_MIN for row in recalculated_plan),
        "capacity_passing_labelled_placements": sum(row["labelled_placements"] for row in recalculated_plan if row["maximum_Q_capacity"] >= Q_MIN),
        "capacity_passing_weighted_S7_orbits": sum(row["weighted_S7_orbits"] for row in recalculated_plan if row["maximum_Q_capacity"] >= Q_MIN),
        "balanced_support_orbits": len(master_rows),
        "balanced_labelled_orbit_mass": labelled_mass,
        "independent_overlap_DP_states": overlap_calls,
    }
    expected_totals = {
        "partition_count": 27,
        "all_labelled_placements": 79_841_895,
        "all_weighted_S7_orbits": 21_699,
        "capacity_passing_partitions": 13,
        "capacity_passing_labelled_placements": 49_564_179,
        "capacity_passing_weighted_S7_orbits": 13_230,
        "balanced_support_orbits": 295,
        "balanced_labelled_orbit_mass": 865_830,
    }
    for key, expected in expected_totals.items():
        if totals[key] != expected:
            errors.append(f"total {key}={totals[key]} != {expected}")
    if not side.get("ok") or side.get("status") != "LOGIC_AND_ARITHMETIC_VERIFIED":
        errors.append("self-contained S<=69 audit is not verified")
    if compression["theorem_inputs"].get("external_premise_required") is not False:
        errors.append("compression scope still marks external premise required")
    return {
        "ok": not errors,
        "errors": errors,
        "self_contained_side_bound_audit": {
            "path": str(SIDE_AUDIT_PATH),
            "sha256": sha256(SIDE_AUDIT_PATH),
            "status": side.get("status"),
            "some_root_side_ceiling": side.get("independent_checks", {}).get("some_root_side_ceiling"),
        },
        "spectral_constants": {
            "free_Ritz_multiset": ["3"] * 13 + ["-5/2"],
            "free_square_sum": "493/4",
            "spectral_D_square_upper": SPECTRAL_UPPER,
            "disjoint_constant": DISJOINT_CONSTANT,
        },
        "totals": totals,
        "expected_totals": expected_totals,
        "plan_rows": recalculated_plan,
        "partition_checks": part_checks,
        "support_rows": checked_rows,
        "all_support_rows_canonical_unique_and_exact": all(row["ok"] for row in checked_rows),
    }


def merge():
    source, grouped = rows_by_partition()
    port_parts = []
    for index in sorted(grouped):
        path = part_path(index)
        if not path.exists():
            raise RuntimeError(f"missing {path}")
        part = json.loads(path.read_text(encoding="utf-8"))
        if part.get("status") != "COMPLETE" or part.get("input_sha256") != sha256(PORT_PATH):
            raise RuntimeError(f"incomplete or stale {path}")
        port_parts.append(part)
    port_rows = [row for part in port_parts for row in part["rows"]]
    port_errors = [error for row in port_rows for error in row["errors"]]
    port_summary = {
        "input_support_orbits": len(port_rows),
        "complete_Q_at_least_4_assignments_tested": sum(row["independent_Q_at_least_4_complete_leaves"] for row in port_rows),
        "locally_port_feasible_assignments": sum(row["independent_locally_port_feasible"] for row in port_rows),
        "direct_matching_groups_checked": sum(row["direct_matching_groups_checked"] for row in port_rows),
        "all_exact_feasible_tuple_sets_equal": all(row["exact_feasible_tuple_set_equal"] for row in port_rows),
        "all_rows_ok": all(row["ok"] for row in port_rows),
        "elapsed_seconds": sum(row["elapsed_seconds"] for row in port_rows),
    }
    expected_port = {
        "input_support_orbits": 295,
        "complete_Q_at_least_4_assignments_tested": 4_758_382,
        "locally_port_feasible_assignments": 980,
        "direct_matching_groups_checked": 6_860,
    }
    for key, expected in expected_port.items():
        if port_summary[key] != expected:
            port_errors.append(f"port summary {key}={port_summary[key]} != {expected}")
    if source["summary"]["Q_at_least_4_assignments_covered"] != 4_758_382:
        port_errors.append("producer master target total mismatch")
    if source["summary"]["locally_port_feasible_Q_at_least_4_assignments"] != 980:
        port_errors.append("producer master feasible total mismatch")

    compression = independent_compression_audit()
    errors = list(port_errors) + list(compression["errors"])
    result = {
        "status": "INDEPENDENTLY_VERIFIED" if not errors else "DISCREPANCY",
        "ok": not errors,
        "errors": errors,
        "model": "self-contained E0=73,Q>=4 compression and complete-leaf port audit",
        "inputs": {
            str(PLAN_PATH): sha256(PLAN_PATH),
            str(COMPRESSION_PATH): sha256(COMPRESSION_PATH),
            str(PORT_PATH): sha256(PORT_PATH),
            str(SIDE_AUDIT_PATH): sha256(SIDE_AUDIT_PATH),
        },
        "scope": (
            "The independently audited SRG consequence some root has S(r)<=69, "
            "together with E0=73, gives Q=E0-S>=4. No external n3 premise is "
            "used. This verifies a necessary root branch and does not exclude E0=73."
        ),
        "fibre_catalogue": {
            "state_counts_by_deficit": {str(d): len(FIBRE_STATES[d]) for d in range(1, 5)},
            "Q_histograms_by_deficit": {
                str(d): {str(q): count for q, count in sorted(Counter(Q_VALUES[d]).items())}
                for d in range(1, 5)
            },
        },
        "compression_audit": compression,
        "port_audit": {
            "method": (
                "independent state catalogue and port generation; every complete "
                "Q>=4 leaf receives seven closed Hall tests; exact tuple sets are "
                "compared; all 980 survivors receive direct bit-mask matchings"
            ),
            "summary": port_summary,
            "expected": expected_port,
            "parts": [
                {
                    "partition_index": part["partition_index"],
                    "partition": part["partition"],
                    "artifact": str(part_path(part["partition_index"])),
                    **part["summary"],
                }
                for part in port_parts
            ],
            "rows": port_rows,
        },
        "claim_boundary": (
            "Solver-free necessary-condition census only. It neither constructs an "
            "SRG nor proves nonexistence of the E0=73 branch."
        ),
    }
    atomic_json(OUTPUT_PATH, result)
    lines = [
        "# E0=73, Q>=4 independent audit",
        "",
        f"Status: **{result['status']}** (errors: {len(errors)}).",
        "",
        "The root reduction is self-contained: the separately audited side theorem "
        "gives a root with `S(r)<=69`; hence `E0=73` forces `Q>=4`. No external "
        "`n3` premise is used.",
        "",
        "Independent compression reconstruction found 27 deficit partitions, "
        "79,841,895 labelled placements and 21,699 weighted S7 orbits. The exact "
        "Q-capacity test leaves 13 partitions (49,564,179 placements / 13,230 "
        "orbits). All 295 stored balanced representatives were independently "
        "canonicalized under all 5,040 group permutations; their orbit mass is "
        "865,830. Exact integer overlap minima and exact-Fraction disjoint minima "
        "agree row by row.",
        "",
        "The independent port traversal tested every one of 4,758,382 complete "
        "labelled assignments with Q>=4. Its exact feasible tuple sets agree on all "
        "295 support rows: 980 assignments on 58 supports. Every survivor was also "
        "checked by direct matching DFS in all seven groups (6,860 checks).",
        "",
        "Boundary: this is a solver-free necessary-branch census, not an exclusion "
        "of E0=73 and not a construction of the Conway 99-graph.",
    ]
    SUMMARY_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({
        "path": str(OUTPUT_PATH),
        "summary": str(SUMMARY_PATH),
        "status": result["status"],
        "errors": len(errors),
        **port_summary,
        **compression["totals"],
    }, sort_keys=True), flush=True)
    if errors:
        raise AssertionError(errors[:20])
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port-partition", type=int)
    parser.add_argument("--all-port", action="store_true")
    parser.add_argument("--merge", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if sum((args.port_partition is not None, args.all_port, args.merge)) != 1:
        parser.error("choose exactly one mode")
    _source, grouped = rows_by_partition()
    if args.port_partition is not None:
        if args.port_partition not in grouped:
            parser.error("partition has no compression rows")
        run_port_partition(args.port_partition, args.force)
    elif args.all_port:
        for index in sorted(grouped):
            run_port_partition(index, args.force)
    else:
        merge()


if __name__ == "__main__":
    main()
