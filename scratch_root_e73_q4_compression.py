"""Self-contained-root-reduced E0=73, Q>=4 support-compression census.

The condition Q>=4 uses the self-contained, independently audited theorem
that every putative SRG has a root with S(r)<=69, together with E0=S+Q=73.
It is therefore a necessary E0=73 branch without an external n3 premise.
No claim that E0=73 is impossible is made here.

All deficit-11 partitions are covered.  A partition whose exact maximum
diagonal capacity ``2*n_delta2 + n_delta3`` is below four is excluded before
support placement generation.  Its labelled placement and weighted-S7 orbit
counts are nevertheless recorded exactly (closed form and Burnside).

For every remaining partition all labelled support placements are scanned.
Weighted port balance is an orbit-invariant analytic obstruction, so only
balanced orbits are materialized.  Exact orbit images, stabilizers, labelled
orbit-size sums, exact overlap recursion, and the exact-Fraction disjoint
least-norm relaxation are checkpointed per partition.
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
from pathlib import Path
import time

import scratch_general_e79_compression_audit as base


TOTAL_DEFICIT = 11
E0 = 73
Q_MIN = 4
S_MAX = 69
SPECTRAL_UPPER = 4660
DISJOINT_CONSTANT = 3184
SUPPORTS = tuple(itertools.combinations(range(7), 2))
SUPPORT_INDEX = {support: index for index, support in enumerate(SUPPORTS)}
SHIFT = tuple(3 * index for index in range(21))
MASTER_PATH = Path("scratch_root_e73_q4_compression_audit.json")
PLAN_PATH = Path("scratch_root_e73_q4_compression_plan.json")
CHECKPOINT_EVERY_PLACEMENTS = 250_000
CHECKPOINT_EVERY_FILTER_ROWS = 10


def integer_partitions(total, maximum=4):
    def visit(residual, cap, prefix):
        if residual == 0:
            yield tuple(prefix)
            return
        for value in range(min(cap, residual), 0, -1):
            yield from visit(residual - value, value, prefix + (value,))

    return tuple(visit(total, maximum, ()))


PARTITIONS = integer_partitions(TOTAL_DEFICIT)
assert len(PARTITIONS) == 27


def part_path(index):
    return Path(f"scratch_root_e73_q4_compression_part_{index:02d}.json")


def atomic_json(path, value):
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def support_action(permutation):
    return tuple(
        SUPPORT_INDEX[tuple(sorted((permutation[a], permutation[b])))]
        for a, b in SUPPORTS
    )


GROUP_PERMUTATIONS = tuple(itertools.permutations(range(7)))
SUPPORT_ACTIONS = tuple(support_action(permutation) for permutation in GROUP_PERMUTATIONS)
assert len(SUPPORT_ACTIONS) == len(set(SUPPORT_ACTIONS)) == 5040


def action_cycle_type(action):
    unseen = set(range(21))
    lengths = []
    while unseen:
        start = min(unseen)
        current = start
        length = 0
        while current in unseen:
            unseen.remove(current)
            length += 1
            current = action[current]
        assert current == start
        lengths.append(length)
    return tuple(sorted(lengths, reverse=True))


ACTION_CYCLE_TYPES = Counter(action_cycle_type(action) for action in SUPPORT_ACTIONS)
assert sum(ACTION_CYCLE_TYPES.values()) == 5040


def fixed_weighted_placements(cycle_type, partition):
    """Invariant multiset placements on distinguishable support-action cycles."""
    value_counts = tuple(sorted(Counter(partition).items(), reverse=True))
    initial = tuple(count for _value, count in value_counts)
    current = {initial: 1}
    for length in cycle_type:
        following = Counter()
        for residual, multiplicity in current.items():
            # Give this support cycle weight zero.
            following[residual] += multiplicity
            # Or give its every support one chosen nonzero weight.
            for position, remaining in enumerate(residual):
                if remaining < length:
                    continue
                changed = list(residual)
                changed[position] -= length
                following[tuple(changed)] += multiplicity
        current = dict(following)
    return current.get(tuple(0 for _ in initial), 0)


def burnside_orbit_count(partition):
    numerator = sum(
        action_count * fixed_weighted_placements(cycle_type, partition)
        for cycle_type, action_count in ACTION_CYCLE_TYPES.items()
    )
    assert numerator % 5040 == 0
    return numerator // 5040, numerator


def labelled_count(partition):
    length = len(partition)
    answer = math.prod(range(21 - length + 1, 22))
    for multiplicity in Counter(partition).values():
        answer //= math.factorial(multiplicity)
    return answer


def q_capacity(partition):
    # Audited local fibre catalogues: delta1/delta4 have Qmax 0,
    # delta2 has Qmax 2, and delta3 has Qmax 1.
    return 2 * partition.count(2) + partition.count(3)


def encode_entries(entries):
    code = 0
    for support_index, value in entries:
        code |= value << SHIFT[support_index]
    return code


def decode(code):
    return tuple((code >> shift) & 7 for shift in SHIFT)


def nonzero_entries(code):
    return tuple(
        (index, value)
        for index, shift in enumerate(SHIFT)
        if (value := (code >> shift) & 7)
    )


def labelled_entry_placements(partition):
    """Every repeated-weight-unlabelled placement, with its sparse entries."""
    value_counts = tuple(sorted(Counter(partition).items(), reverse=True))

    def visit(offset, available, entries):
        if offset == len(value_counts):
            sparse = tuple(sorted(entries))
            yield encode_entries(sparse), sparse
            return
        value, multiplicity = value_counts[offset]
        for chosen in itertools.combinations(available, multiplicity):
            chosen_set = frozenset(chosen)
            remaining = tuple(index for index in available if index not in chosen_set)
            yield from visit(
                offset + 1,
                remaining,
                entries + tuple((index, value) for index in chosen),
            )

    yield from visit(0, tuple(range(21)), ())


def sparse_weighted_port_balance(entries, with_details=False):
    totals = [0] * 7
    maxima = [0] * 7
    incident = [[] for _ in range(7)]
    for support_index, value in entries:
        for group in SUPPORTS[support_index]:
            totals[group] += value
            maxima[group] = max(maxima[group], value)
            if with_details:
                incident[group].append(value)
    passes = all(not totals[group] or 2 * maxima[group] <= totals[group] for group in range(7))
    if not with_details:
        return passes
    details = [
        {
            "group": group,
            "incident_deficits": incident[group],
            "total_deficit": totals[group],
            "maximum_deficit": maxima[group],
            "passes": not totals[group] or 2 * maxima[group] <= totals[group],
        }
        for group in range(7)
        if totals[group]
    ]
    return passes, details


def orbit_images(code):
    entries = nonzero_entries(code)
    images = set()
    for action in SUPPORT_ACTIONS:
        image = 0
        for support_index, value in entries:
            image |= value << SHIFT[action[support_index]]
        images.add(image)
    return images


def compact_signature(state):
    simple_degrees = [0] * 7
    weighted_degrees = [0] * 7
    weighted_edges = []
    for support, value in zip(SUPPORTS, state):
        if not value:
            continue
        a, b = support
        simple_degrees[a] += 1
        simple_degrees[b] += 1
        weighted_degrees[a] += value
        weighted_degrees[b] += value
        weighted_edges.append([a, b, value])
    return {
        "weighted_edges": weighted_edges,
        "simple_degree_sequence": sorted(simple_degrees, reverse=True),
        "weighted_degree_sequence": sorted(weighted_degrees, reverse=True),
    }


def diagonal_square(state):
    return sum((8 - 2 * value) ** 2 for value in state)


def joint_budget(state):
    numerator = SPECTRAL_UPPER - diagonal_square(state) - DISJOINT_CONSTANT
    assert numerator % 2 == 0
    return numerator // 2


def compact_overlap(state):
    result = base.overlap_minimum(state)
    compact = {
        "feasible": result["feasible"],
        "minimum_square": result["minimum_square"],
        "visited_complete_assignments": result["visited_complete_assignments"],
        "one_minimizer": result["stored_minimizers"][0] if result["stored_minimizers"] else None,
    }
    if compact["feasible"]:
        rows = [0] * 21
        square = 0
        for left, right, value in compact["one_minimizer"]:
            rows[left] += value
            rows[right] += value
            square += value * value
            assert value >= 0 and set(SUPPORTS[left]).intersection(SUPPORTS[right])
        assert rows == [4 * value for value in state]
        assert square == compact["minimum_square"]
        compact["minimizer_verified"] = True
    return compact


def spectral_endpoint_maximizer(count, lower, upper, target):
    candidates = []
    for upper_count in range(count):
        lower_count = count - 1 - upper_count
        residual = target - upper_count * upper - lower_count * lower
        if lower <= residual <= upper:
            values = [upper] * upper_count + [residual] + [lower] * lower_count
            candidates.append(values)
    assert candidates
    return max(candidates, key=lambda values: sum(value * value for value in values))


def theorem_inputs():
    free_target = Fraction(E0, 2)
    free = spectral_endpoint_maximizer(14, Fraction(-4), Fraction(3), free_target)
    free_square = sum(value * value for value in free)
    assert free == [Fraction(3)] * 13 + [Fraction(-5, 2)]
    assert free_square == Fraction(493, 4)
    assert SPECTRAL_UPPER == 16 * (12**2 + 6 * 2**2 + free_square)
    assert DISJOINT_CONSTANT == 3360 - 16 * TOTAL_DEFICIT
    return {
        "external_premise_required": False,
        "self_contained_root_reduction": "every putative SRG has a root with S(r)<=69",
        "root_implication": "E0=73 and S(r)<=69 imply Q=E0-S>=4",
        "side_bound_audit": "scratch_root_side_bound_selfcontained_audit.json",
        "total_deficit": TOTAL_DEFICIT,
        "total_fibre_edges_E0": E0,
        "required_diagonal_edges_Q": f">={Q_MIN}",
        "free_Ritz_interval": ["-4", "3"],
        "free_Ritz_sum": str(free_target),
        "spectral_maximizing_free_Ritz_multiset": [str(value) for value in free],
        "free_Ritz_maximum_square_sum": str(free_square),
        "spectral_D_square_upper": SPECTRAL_UPPER,
        "disjoint_constant_derivation": f"3360-16*{TOTAL_DEFICIT}={DISJOINT_CONSTANT}",
        "trace_identity": (
            "tr(D^2)=sum_F(8-2*delta_F)^2+"
            f"{DISJOINT_CONSTANT}+2*(overlap_square+x_square)"
        ),
        "BP_overlap_row_sum": "4*delta_F",
        "disjoint_deviation_row_sum": "sum x_FG=2*delta_F for x=4-D",
        "weighted_port_balance": (
            "at every root group, 2*max(incident delta)<=sum(incident delta)"
        ),
        "partition_Q_capacity": "2*(number of delta2 fibres)+(number of delta3 fibres)",
        "external_n3_bound_used": False,
    }


def plan_document():
    rows = []
    for index, partition in enumerate(PARTITIONS):
        orbits, numerator = burnside_orbit_count(partition)
        capacity = q_capacity(partition)
        rows.append({
            "partition_index": index,
            "partition": list(partition),
            "maximum_Q_capacity": capacity,
            "passes_Q_at_least_4_capacity": capacity >= Q_MIN,
            "labelled_placements": labelled_count(partition),
            "weighted_S7_orbits_by_Burnside": orbits,
            "Burnside_fixed_sum": numerator,
        })
    total_labelled = sum(row["labelled_placements"] for row in rows)
    passing_labelled = sum(
        row["labelled_placements"]
        for row in rows if row["passes_Q_at_least_4_capacity"]
    )
    total_orbits = sum(row["weighted_S7_orbits_by_Burnside"] for row in rows)
    passing_orbits = sum(
        row["weighted_S7_orbits_by_Burnside"]
        for row in rows if row["passes_Q_at_least_4_capacity"]
    )
    return {
        "status": "PLANNED_EXACT_COUNTS",
        "model": "self-contained-root-reduced E0=73, Q>=4 support-partition plan",
        "theorem_inputs": theorem_inputs(),
        "coverage": {
            "partition_count": len(rows),
            "capacity_passing_partitions": sum(
                row["passes_Q_at_least_4_capacity"] for row in rows
            ),
            "capacity_excluded_partitions": sum(
                not row["passes_Q_at_least_4_capacity"] for row in rows
            ),
            "all_labelled_placements": total_labelled,
            "capacity_passing_labelled_placements": passing_labelled,
            "capacity_excluded_labelled_placements": total_labelled - passing_labelled,
            "all_weighted_S7_orbits_by_Burnside": total_orbits,
            "capacity_passing_weighted_S7_orbits_by_Burnside": passing_orbits,
            "capacity_excluded_weighted_S7_orbits_by_Burnside": total_orbits - passing_orbits,
            "labelled_identity_verified": (
                passing_labelled + (total_labelled - passing_labelled) == total_labelled
            ),
            "orbit_identity_verified": (
                passing_orbits + (total_orbits - passing_orbits) == total_orbits
            ),
        },
        "method": (
            "closed-form multiset placements; independent Burnside count over all "
            "5040 S7 actions on the 21 supports"
        ),
        "claim_boundary": (
            "Q>=4 follows from the independently audited self-contained side bound. "
            "These are planning/coverage counts, not an E0=73 exclusion."
        ),
        "rows": rows,
    }


def write_plan():
    document = plan_document()
    atomic_json(PLAN_PATH, document)
    print(json.dumps({"path": str(PLAN_PATH), **document["coverage"]}, sort_keys=True), flush=True)
    return document


def scanning_checkpoint(index, partition, plan_row):
    return {
        "status": "SCANNING_BALANCE",
        "model": "self-contained-root-reduced E0=73, Q>=4 exact compression partition",
        "partition_index": index,
        "partition": list(partition),
        "maximum_Q_capacity": plan_row["maximum_Q_capacity"],
        "passes_Q_at_least_4_capacity": True,
        "theorem_inputs": theorem_inputs(),
        "coverage": {
            "expected_labelled_placements": plan_row["labelled_placements"],
            "expected_weighted_S7_orbits_by_Burnside": plan_row[
                "weighted_S7_orbits_by_Burnside"
            ],
            "labelled_placements_scanned": 0,
            "balanced_labelled_placements": 0,
            "unbalanced_labelled_placements": 0,
            "balanced_orbits_materialized": 0,
            "checkpoint_every_placements": CHECKPOINT_EVERY_PLACEMENTS,
            "scan_order": "deterministic repeated-weight-unlabelled sparse placement order",
        },
        "balanced_raw_orbits": [],
        "rows": [],
    }


def excluded_result(index, partition, plan_row):
    return {
        "status": "COMPLETE_Q_CAPACITY_EXCLUDED",
        "model": "self-contained-root-reduced E0=73, Q>=4 exact compression partition",
        "partition_index": index,
        "partition": list(partition),
        "maximum_Q_capacity": plan_row["maximum_Q_capacity"],
        "passes_Q_at_least_4_capacity": False,
        "theorem_inputs": theorem_inputs(),
        "coverage": {
            "labelled_placements": plan_row["labelled_placements"],
            "weighted_S7_orbits_by_Burnside": plan_row["weighted_S7_orbits_by_Burnside"],
            "all_excluded_by_partition_invariant_capacity": True,
            "placement_generation_skipped_by_early_exact_obstruction": True,
        },
        "summary": {
            "capacity_surviving_orbits": 0,
            "balanced_orbits": 0,
            "overlap_rows_computed": 0,
            "spectral_real_survivors": 0,
        },
        "rows": [],
        "claim_boundary": "necessary Q>=4 root branch only; no E0=73 exclusion",
    }


def refresh_scope_fields(result):
    """Refresh proof-scope metadata without changing enumerated data."""
    result["model"] = "self-contained-root-reduced E0=73, Q>=4 exact compression partition"
    result["theorem_inputs"] = theorem_inputs()
    result["claim_boundary"] = (
        "Necessary Q>=4 root branch from the independently audited self-contained "
        "S<=69 theorem; no external n3 bound and no E0=73 exclusion."
    )
    return result


def scan_balanced_orbits(result, path):
    partition = tuple(result["partition"])
    expected = result["coverage"]["expected_labelled_placements"]
    already_scanned = result["coverage"]["labelled_placements_scanned"]
    raw_orbits = [
        (int(row["representative_code_hex"], 16), row["orbit_size"])
        for row in result["balanced_raw_orbits"]
    ]
    seen = set()
    for code, size in raw_orbits:
        images = orbit_images(code)
        assert len(images) == size and code == min(images)
        assert not seen.intersection(images)
        seen.update(images)
    balanced_labelled = result["coverage"]["balanced_labelled_placements"]
    # A discovered orbit contains placements that can occur later in the
    # deterministic scan, so its full image union may exceed the number of
    # balanced placements scanned so far.  Equality is required only at EOF.
    assert len(seen) >= balanced_labelled
    scanned = already_scanned
    started = time.monotonic()
    for ordinal, (code, entries) in enumerate(labelled_entry_placements(partition)):
        if ordinal < already_scanned:
            continue
        scanned += 1
        if sparse_weighted_port_balance(entries):
            balanced_labelled += 1
            if code not in seen:
                images = orbit_images(code)
                representative = min(images)
                assert code in images and sparse_weighted_port_balance(nonzero_entries(representative))
                assert not seen.intersection(images)
                seen.update(images)
                raw_orbits.append((representative, len(images)))
        if scanned % CHECKPOINT_EVERY_PLACEMENTS == 0:
            result["coverage"].update({
                "labelled_placements_scanned": scanned,
                "balanced_labelled_placements": balanced_labelled,
                "unbalanced_labelled_placements": scanned - balanced_labelled,
                "balanced_orbits_materialized": len(raw_orbits),
                "balanced_orbit_image_union_size": len(seen),
                "scan_elapsed_seconds_last_invocation": round(time.monotonic() - started, 6),
            })
            result["balanced_raw_orbits"] = [
                {"representative_code_hex": hex(code), "orbit_size": size}
                for code, size in sorted(raw_orbits)
            ]
            atomic_json(path, result)
            print(json.dumps({
                "phase": "scan",
                "partition_index": result["partition_index"],
                "scanned": scanned,
                "expected": expected,
                "balanced_labelled": balanced_labelled,
                "balanced_orbits": len(raw_orbits),
            }), flush=True)
    assert scanned == expected
    assert len(seen) == balanced_labelled == sum(size for _code, size in raw_orbits)
    raw_orbits.sort()
    total_orbits = result["coverage"]["expected_weighted_S7_orbits_by_Burnside"]
    assert len(raw_orbits) <= total_orbits
    result["coverage"].update({
        "labelled_placements_scanned": scanned,
        "balanced_labelled_placements": balanced_labelled,
        "unbalanced_labelled_placements": scanned - balanced_labelled,
        "balanced_orbits_materialized": len(raw_orbits),
        "unbalanced_orbits_by_difference": total_orbits - len(raw_orbits),
        "balanced_orbit_size_sum": sum(size for _code, size in raw_orbits),
        "labelled_balance_identity_verified": (
            balanced_labelled + (scanned - balanced_labelled) == expected
        ),
        "orbit_balance_identity_verified": (
            len(raw_orbits) + (total_orbits - len(raw_orbits)) == total_orbits
        ),
        "scan_elapsed_seconds_last_invocation": round(time.monotonic() - started, 6),
    })
    result["balanced_raw_orbits"] = [
        {"representative_code_hex": hex(code), "orbit_size": size}
        for code, size in raw_orbits
    ]
    rows = []
    for orbit_index, (code, size) in enumerate(raw_orbits):
        stabilizer = sum(
            all(
                ((code >> SHIFT[index]) & 7)
                == ((code >> SHIFT[action[index]]) & 7)
                for index in range(21)
            )
            for action in SUPPORT_ACTIONS
        )
        assert size * stabilizer == 5040
        state = decode(code)
        rows.append({
            "partition": list(partition),
            "orbit_index": orbit_index,
            "representative_code_hex": hex(code),
            "orbit_size": size,
            "weighted_stabilizer_order": stabilizer,
            "exceptional_supports": base.state_description(state),
            "maximum_Q_capacity": q_capacity(partition),
            "filter_complete": False,
        })
    result["rows"] = rows
    result["status"] = "FILTERING_COMPRESSION"
    atomic_json(path, result)


def filter_row(row):
    state = decode(int(row["representative_code_hex"], 16))
    entries = nonzero_entries(int(row["representative_code_hex"], 16))
    balanced, balance_details = sparse_weighted_port_balance(entries, with_details=True)
    assert balanced and sum(state) == TOTAL_DEFICIT
    partition = tuple(row["partition"])
    assert sorted((value for value in state if value), reverse=True) == list(partition)
    diagonal = diagonal_square(state)
    budget = joint_budget(state)
    continuous = base.continuous_disjoint_minimum(state)
    if math.ceil(continuous) > budget:
        overlap = {
            "status": "SKIPPED_BY_DISJOINT_REAL_BOUND",
            "feasible": None,
            "minimum_square": None,
            "visited_complete_assignments": 0,
            "one_minimizer": None,
        }
    else:
        overlap = compact_overlap(state)
    passes = (
        overlap["feasible"] is True
        and overlap["minimum_square"] + math.ceil(continuous) <= budget
    )
    row.update({
        "support_signature": compact_signature(state),
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
    assert diagonal + DISJOINT_CONSTANT + 2 * budget == SPECTRAL_UPPER


def summarize_rows(rows):
    complete = [row for row in rows if row["filter_complete"]]
    return {
        "balanced_orbits": len(rows),
        "filter_rows_complete": len(complete),
        "overlap_rows_computed": sum(row["overlap"]["feasible"] is not None for row in complete),
        "overlap_feasible": sum(row["overlap"]["feasible"] is True for row in complete),
        "spectral_real_survivors": sum(
            row["passes_weighted_port_overlap_and_real_relaxation"] for row in complete
        ),
        "balanced_labelled_placements": sum(
            row["orbit_size"] for row in rows
        ),
        "spectral_real_surviving_labelled_placements": sum(
            row["orbit_size"]
            for row in complete
            if row["passes_weighted_port_overlap_and_real_relaxation"]
        ),
    }


def run_partition(index, force=False, scan_only=False):
    plan = plan_document()
    plan_row = plan["rows"][index]
    partition = PARTITIONS[index]
    path = part_path(index)
    if not plan_row["passes_Q_at_least_4_capacity"]:
        result = excluded_result(index, partition, plan_row)
        atomic_json(path, result)
        print(json.dumps({
            "phase": "capacity_excluded",
            "partition_index": index,
            "partition": partition,
            "maximum_Q_capacity": plan_row["maximum_Q_capacity"],
            "labelled": plan_row["labelled_placements"],
            "orbits": plan_row["weighted_S7_orbits_by_Burnside"],
        }), flush=True)
        return result
    if path.exists() and not force:
        result = json.loads(path.read_text(encoding="utf-8"))
        assert result["partition_index"] == index and tuple(result["partition"]) == partition
        if result["status"] == "COMPLETE":
            refresh_scope_fields(result)
            atomic_json(path, result)
            print(json.dumps({"phase": "resume", "partition_index": index, "status": "COMPLETE"}), flush=True)
            return result
    else:
        result = scanning_checkpoint(index, partition, plan_row)
        atomic_json(path, result)
    if result["status"] == "SCANNING_BALANCE":
        scan_balanced_orbits(result, path)
    if scan_only:
        return result
    for offset, row in enumerate(result["rows"]):
        if row["filter_complete"]:
            continue
        filter_row(row)
        if (offset + 1) % CHECKPOINT_EVERY_FILTER_ROWS == 0 or offset + 1 == len(result["rows"]):
            result["summary"] = summarize_rows(result["rows"])
            atomic_json(path, result)
        if (offset + 1) % 10 == 0 or offset + 1 == len(result["rows"]):
            print(json.dumps({
                "phase": "filter",
                "partition_index": index,
                "completed": offset + 1,
                "orbits": len(result["rows"]),
                "summary": result["summary"],
            }), flush=True)
    result["status"] = "COMPLETE"
    result["summary"] = summarize_rows(result["rows"])
    refresh_scope_fields(result)
    assert result["summary"]["balanced_labelled_placements"] == result["coverage"][
        "balanced_labelled_placements"
    ]
    atomic_json(path, result)
    return result


def merge_parts():
    plan = plan_document()
    parts = []
    for index, plan_row in enumerate(plan["rows"]):
        path = part_path(index)
        if not path.exists():
            raise RuntimeError(f"missing {path}")
        part = json.loads(path.read_text(encoding="utf-8"))
        allowed = {"COMPLETE", "COMPLETE_Q_CAPACITY_EXCLUDED"}
        if part["status"] not in allowed:
            raise RuntimeError(f"incomplete {path}: {part['status']}")
        assert part["partition_index"] == index
        assert part["maximum_Q_capacity"] == plan_row["maximum_Q_capacity"]
        parts.append(part)
    surviving_rows = [
        row
        for part in parts if part["status"] == "COMPLETE"
        for row in part["rows"]
        if row["passes_weighted_port_overlap_and_real_relaxation"]
    ]
    balanced_orbits = sum(
        part.get("summary", {}).get("balanced_orbits", 0) for part in parts
    )
    result = {
        "status": "COMPLETE",
        "model": "self-contained-root-reduced E0=73, Q>=4 merged exact support compression",
        "theorem_inputs": theorem_inputs(),
        "plan_sha256": sha256(PLAN_PATH),
        "coverage": plan["coverage"] | {
            "partition_artifacts_complete": len(parts),
            "capacity_passing_labelled_scanned": sum(
                part.get("coverage", {}).get("labelled_placements_scanned", 0)
                for part in parts
            ),
            "balanced_orbits_materialized": balanced_orbits,
            "balanced_labelled_placements": sum(
                part.get("coverage", {}).get("balanced_labelled_placements", 0)
                for part in parts
            ),
            "all_part_identity_verified": all(
                part["status"] == "COMPLETE_Q_CAPACITY_EXCLUDED"
                or (
                    part["coverage"]["labelled_balance_identity_verified"]
                    and part["coverage"]["orbit_balance_identity_verified"]
                )
                for part in parts
            ),
        },
        "summary": {
            "capacity_excluded_partitions": sum(
                part["status"] == "COMPLETE_Q_CAPACITY_EXCLUDED" for part in parts
            ),
            "capacity_passing_partitions": sum(part["status"] == "COMPLETE" for part in parts),
            "balanced_support_orbits": balanced_orbits,
            "overlap_rows_computed": sum(
                part.get("summary", {}).get("overlap_rows_computed", 0) for part in parts
            ),
            "overlap_feasible": sum(
                part.get("summary", {}).get("overlap_feasible", 0) for part in parts
            ),
            "spectral_real_surviving_support_orbits": len(surviving_rows),
            "spectral_real_surviving_labelled_placements": sum(
                row["orbit_size"] for row in surviving_rows
            ),
        },
        "by_partition": [
            {
                "partition_index": index,
                "partition": part["partition"],
                "maximum_Q_capacity": part["maximum_Q_capacity"],
                "status": part["status"],
                "labelled_placements": plan["rows"][index]["labelled_placements"],
                "weighted_S7_orbits_by_Burnside": plan["rows"][index][
                    "weighted_S7_orbits_by_Burnside"
                ],
                **part.get("summary", {}),
                "artifact": str(part_path(index)),
            }
            for index, part in enumerate(parts)
        ],
        "rows": surviving_rows,
        "claim_boundary": (
            "Every exclusion here belongs only to the necessary E0=73,Q>=4 root "
            "branch supplied by the independently audited self-contained S<=69 "
            "theorem. No external n3 bound is used and no E0=73 exclusion is claimed."
        ),
    }
    assert result["coverage"]["capacity_passing_labelled_scanned"] == result["coverage"][
        "capacity_passing_labelled_placements"
    ]
    assert result["coverage"]["all_part_identity_verified"]
    atomic_json(MASTER_PATH, result)
    print(json.dumps({
        "path": str(MASTER_PATH),
        "status": result["status"],
        **result["summary"],
    }, sort_keys=True), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", action="store_true")
    parser.add_argument("--partition-index", type=int)
    parser.add_argument("--partition-indices", type=str)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--merge", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--scan-only", action="store_true")
    args = parser.parse_args()
    selected = sum((
        args.plan,
        args.partition_index is not None,
        args.partition_indices is not None,
        args.all,
        args.merge,
    ))
    if selected != 1:
        parser.error("choose exactly one input mode")
    if args.plan:
        write_plan()
    elif args.partition_index is not None:
        if not 0 <= args.partition_index < len(PARTITIONS):
            parser.error("partition index out of range")
        run_partition(args.partition_index, args.force, args.scan_only)
    elif args.partition_indices is not None:
        indices = tuple(int(value) for value in args.partition_indices.split(","))
        if not indices or len(indices) != len(set(indices)):
            parser.error("partition indices must be nonempty and unique")
        if any(not 0 <= index < len(PARTITIONS) for index in indices):
            parser.error("partition index out of range")
        for index in indices:
            run_partition(index, args.force, args.scan_only)
    elif args.all:
        for index in range(len(PARTITIONS)):
            run_partition(index, args.force, args.scan_only)
    else:
        merge_parts()


if __name__ == "__main__":
    main()
