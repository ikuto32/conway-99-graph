"""Checkpointed exact fibre-compression audit for E0=75 (deficit nine).

Each integer partition is classified in its own file.  Placement orbits use
compact 3-bit state encodings so the largest labelled partitions do not need
millions of 21-tuples resident in memory.  The filtering phase is resumable
after the complete orbit list has been written.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import os
import time
from collections import Counter
from fractions import Fraction
from pathlib import Path

import scratch_general_e79_compression_audit as base


PARTITIONS = (
    (4, 4, 1),
    (4, 3, 2),
    (4, 3, 1, 1),
    (4, 2, 2, 1),
    (4, 2, 1, 1, 1),
    (4, 1, 1, 1, 1, 1),
    (3, 3, 3),
    (3, 3, 2, 1),
    (3, 3, 1, 1, 1),
    (3, 2, 2, 2),
    (3, 2, 2, 1, 1),
    (3, 2, 1, 1, 1, 1),
    (3, 1, 1, 1, 1, 1, 1),
    (2, 2, 2, 2, 1),
    (2, 2, 2, 1, 1, 1),
    (2, 2, 1, 1, 1, 1, 1),
    (2, 1, 1, 1, 1, 1, 1, 1),
    (1, 1, 1, 1, 1, 1, 1, 1, 1),
)

TOTAL_DEFICIT = 9
E0 = 75
SPECTRAL_UPPER = 4596
DISJOINT_CONSTANT = 3216
MASTER_PATH = Path("scratch_general_e75_compression_audit.json")
CHECKPOINT_EVERY = 1
SHIFT = tuple(3 * index for index in range(21))


def integer_partitions(total, maximum=4):
    def visit(residual, cap, prefix):
        if residual == 0:
            yield tuple(prefix)
            return
        for value in range(min(cap, residual), 0, -1):
            yield from visit(residual - value, value, prefix + (value,))

    return tuple(visit(total, maximum, ()))


assert PARTITIONS == integer_partitions(TOTAL_DEFICIT)


def support_action(permutation):
    return tuple(
        base.SUPPORT_INDEX[tuple(sorted((permutation[a], permutation[b])))]
        for a, b in base.SUPPORTS
    )


SUPPORT_ACTIONS = tuple(support_action(p) for p in itertools.permutations(range(7)))
assert len(SUPPORT_ACTIONS) == 5040
assert len(set(SUPPORT_ACTIONS)) == 5040


def part_path(index):
    return Path(f"scratch_general_e75_compression_part_{index:02d}.json")


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
        if (value := ((code >> shift) & 7))
    )


def labelled_codes(partition):
    """Yield every labelled placement once, repeated weights unlabelled."""
    value_counts = tuple(sorted(Counter(partition).items(), reverse=True))

    def visit(offset, available, entries):
        if offset == len(value_counts):
            yield encode_entries(entries)
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


def labelled_count(partition):
    length = len(partition)
    answer = math.prod(range(21 - length + 1, 22))
    for multiplicity in Counter(partition).values():
        answer //= math.factorial(multiplicity)
    return answer


def orbit_images(code):
    entries = nonzero_entries(code)
    images = set()
    for action in SUPPORT_ACTIONS:
        image = 0
        for index, value in entries:
            image |= value << SHIFT[action[index]]
        images.add(image)
    return images


def classify_partition(partition, progress_every=250000):
    expected = labelled_count(partition)
    seen = set()
    raw_orbits = []
    scanned = 0
    started = time.monotonic()
    for code in labelled_codes(partition):
        scanned += 1
        if code not in seen:
            images = orbit_images(code)
            representative = min(images)
            assert code in images
            seen.update(images)
            raw_orbits.append((representative, len(images)))
        if progress_every and scanned % progress_every == 0:
            print(
                json.dumps(
                    {
                        "phase": "classify",
                        "partition": partition,
                        "scanned": scanned,
                        "expected": expected,
                        "orbits": len(raw_orbits),
                        "elapsed_seconds": round(time.monotonic() - started, 3),
                    }
                ),
                flush=True,
            )
    assert scanned == expected
    assert len(seen) == expected
    raw_orbits.sort()
    assert len({code for code, _size in raw_orbits}) == len(raw_orbits)
    rows = []
    for orbit_index, (code, size) in enumerate(raw_orbits):
        assert 5040 % size == 0
        stabilizer = sum(
            all(
                ((code >> SHIFT[index]) & 7)
                == ((code >> SHIFT[action[index]]) & 7)
                for index in range(21)
            )
            for action in SUPPORT_ACTIONS
        )
        # The expression above compares state_i with state_{p(i)} and is
        # equivalent to p(state)=state because p is a permutation.
        assert size * stabilizer == 5040
        state = decode(code)
        rows.append(
            {
                "partition": list(partition),
                "orbit_index": orbit_index,
                "representative_code_hex": hex(code),
                "orbit_size": size,
                "weighted_stabilizer_order": stabilizer,
                "exceptional_supports": base.state_description(state),
                "filter_complete": False,
            }
        )
    assert sum(row["orbit_size"] for row in rows) == expected
    return rows, scanned, time.monotonic() - started


def weighted_port_balance(state):
    details = []
    for group in range(7):
        incident = [
            value
            for support, value in zip(base.SUPPORTS, state)
            if value and group in support
        ]
        if not incident:
            continue
        total = sum(incident)
        maximum = max(incident)
        row = {
            "group": group,
            "incident_deficits": incident,
            "total_deficit": total,
            "maximum_deficit": maximum,
            "passes": 2 * maximum <= total,
        }
        details.append(row)
        if not row["passes"]:
            return False, details
    return True, details


def compact_signature(state):
    simple_degrees = [0] * 7
    weighted_degrees = [0] * 7
    weighted_edges = []
    for support, value in zip(base.SUPPORTS, state):
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


def joint_budget(state):
    diagonal = base.diagonal_square(state)
    numerator = SPECTRAL_UPPER - diagonal - DISJOINT_CONSTANT
    assert numerator % 2 == 0
    return numerator // 2


def compact_overlap(state):
    result = base.overlap_minimum(state)
    compact = {
        "feasible": result["feasible"],
        "minimum_square": result["minimum_square"],
        "visited_complete_assignments": result["visited_complete_assignments"],
        "one_minimizer": (
            result["stored_minimizers"][0] if result["stored_minimizers"] else None
        ),
    }
    if compact["feasible"]:
        rows = [0] * 21
        square = 0
        for left, right, value in compact["one_minimizer"]:
            rows[left] += value
            rows[right] += value
            square += value * value
            assert value >= 0
            assert bool(set(base.SUPPORTS[left]) & set(base.SUPPORTS[right]))
        assert rows == [4 * value for value in state]
        assert square == compact["minimum_square"]
        compact["minimizer_verified"] = True
    return compact


def filter_row(row):
    state = decode(int(row["representative_code_hex"], 16))
    assert sum(state) == TOTAL_DEFICIT
    assert sorted((value for value in state if value), reverse=True) == row["partition"]
    balanced, balance_details = weighted_port_balance(state)
    diagonal = base.diagonal_square(state)
    budget = joint_budget(state)
    continuous = base.continuous_disjoint_minimum(state)
    if balanced:
        overlap = compact_overlap(state)
    else:
        overlap = {
            "status": "SKIPPED_BY_ANALYTIC_WEIGHTED_PORT_BALANCE",
            "feasible": None,
            "minimum_square": None,
            "visited_complete_assignments": 0,
            "one_minimizer": None,
        }
    passes = (
        balanced
        and bool(overlap["feasible"])
        and overlap["minimum_square"] + math.ceil(continuous) <= budget
    )
    row.update(
        {
            "support_signature": compact_signature(state),
            "diagonal_square": diagonal,
            "joint_off_diagonal_square_budget": budget,
            "disjoint_continuous_minimum": str(continuous),
            "disjoint_continuous_ceiling": math.ceil(continuous),
            "weighted_port_balance": balanced,
            "weighted_port_balance_details": balance_details,
            "overlap": overlap,
            "passes_weighted_port_overlap_and_real_relaxation": passes,
            "filter_complete": True,
        }
    )
    assert diagonal + DISJOINT_CONSTANT + 2 * budget == SPECTRAL_UPPER


def summarize(rows):
    complete = [row for row in rows if row["filter_complete"]]
    return {
        "orbits": len(rows),
        "filter_rows_complete": len(complete),
        "weighted_port_balance": sum(row["weighted_port_balance"] for row in complete),
        "overlap_rows_computed": sum(
            row["overlap"]["feasible"] is not None for row in complete
        ),
        "overlap_feasible": sum(row["overlap"]["feasible"] is True for row in complete),
        "overlap_real_relaxation": sum(
            row["overlap"]["feasible"] is True
            and row["overlap"]["minimum_square"]
            + row["disjoint_continuous_ceiling"]
            <= row["joint_off_diagonal_square_budget"]
            for row in complete
        ),
        "final_intersection": sum(
            row["passes_weighted_port_overlap_and_real_relaxation"] for row in complete
        ),
    }


def atomic_json(path, value):
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def spectral_endpoint_maximizer(count, lower, upper, target):
    """Return an exact box/sum maximizer of the convex square objective.

    A maximum of a convex function over the sliced box has at most one
    coordinate away from an endpoint.  Enumerating which of the other
    ``count-1`` coordinates are at the upper endpoint therefore gives a
    complete exact calculation (including endpoint degeneracies).
    """
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
    # Fixed Ritz values are 12,-2^6.  The fourteen free values lie in
    # [-4,3], sum to E0/2.  The endpoint calculation is exact over the
    # continuous interval, hence is a rigorous spectral upper bound.
    free_target = Fraction(E0, 2)
    free = spectral_endpoint_maximizer(14, Fraction(-4), Fraction(3), free_target)
    assert sum(free) == free_target
    free_square = sum(value * value for value in free)
    assert SPECTRAL_UPPER == 16 * (12**2 + 6 * 2**2 + free_square)
    # On the 105 disjoint unordered blocks,
    # 2 sum (4-x)^2 = 3360 - 16 sum(x) + 2 sum(x^2),
    # and sum(x)=total deficit=9.
    assert DISJOINT_CONSTANT == 3360 - 16 * TOTAL_DEFICIT
    return {
        "total_deficit": TOTAL_DEFICIT,
        "total_fibre_edges_E0": E0,
        "free_Ritz_interval": ["-4", "3"],
        "free_Ritz_sum": str(free_target),
        "spectral_maximizing_free_Ritz_multiset": [str(value) for value in free],
        "free_Ritz_maximum_square_sum": str(free_square),
        "spectral_D_square_upper": SPECTRAL_UPPER,
        "disjoint_constant_derivation": (
            f"3360-16*{TOTAL_DEFICIT}={DISJOINT_CONSTANT}"
        ),
        "trace_identity": (
            "tr(D^2)=sum_F(8-2*delta_F)^2+"
            f"{DISJOINT_CONSTANT}+2*(overlap_square+x_square)"
        ),
        "BP_overlap_row_sum": "4*delta_F",
        "disjoint_deviation_row_sum": "sum x_FG=2*delta_F for x=4-D",
        "weighted_port_balance": (
            "at every root group, 2*max(incident delta)<=sum(incident delta)"
        ),
    }


def initial_part_result(index, rows, labelled, elapsed):
    return {
        "status": "CLASSIFIED",
        "model": f"checkpointed exact E0={E0} fibre-compression partition audit",
        "partition_index": index,
        "partition": list(PARTITIONS[index]),
        "theorem_inputs": theorem_inputs(),
        "coverage": {
            "labelled_placements": labelled,
            "placement_orbits": len(rows),
            "classification_elapsed_seconds": round(elapsed, 6),
            "orbit_method": (
                "all labelled placements encoded in 3 bits per support; exact images "
                "under all 5040 S7 permutations; weighted state preserved"
            ),
            "checkpoint_method": (
                "complete placement list is committed before row filters; filtering "
                "is checkpointed every completed row and resumes from this file"
            ),
        },
        "summary": summarize(rows),
        "rows": rows,
    }


def run_partition(index, classify_only=False, force=False):
    partition = PARTITIONS[index]
    path = part_path(index)
    if path.exists() and not force:
        result = json.loads(path.read_text(encoding="utf-8"))
        assert result["partition_index"] == index
        assert tuple(result["partition"]) == partition
        print(json.dumps({"phase": "resume", "path": str(path), "status": result["status"]}), flush=True)
    else:
        rows, labelled, elapsed = classify_partition(partition)
        result = initial_part_result(index, rows, labelled, elapsed)
        atomic_json(path, result)
        print(
            json.dumps(
                {
                    "phase": "classified",
                    "partition_index": index,
                    "partition": partition,
                    "labelled": labelled,
                    "orbits": len(rows),
                    "elapsed_seconds": round(elapsed, 3),
                }
            ),
            flush=True,
        )
    if result["status"] == "COMPLETE":
        # Refresh summaries when the schema gains an audited derived count.
        result["summary"] = summarize(result["rows"])
        atomic_json(path, result)
        return result
    if classify_only:
        return result
    result["status"] = "FILTERING"
    for offset, row in enumerate(result["rows"]):
        if row["filter_complete"]:
            continue
        filter_row(row)
        if (offset + 1) % CHECKPOINT_EVERY == 0 or offset + 1 == len(result["rows"]):
            result["summary"] = summarize(result["rows"])
            atomic_json(path, result)
        if (offset + 1) % 10 == 0 or offset + 1 == len(result["rows"]):
            print(
                json.dumps(
                    {
                        "phase": "filter",
                        "partition_index": index,
                        "completed": offset + 1,
                        "orbits": len(result["rows"]),
                        "summary": result["summary"],
                    }
                ),
                flush=True,
            )
    result["status"] = "COMPLETE"
    result["summary"] = summarize(result["rows"])
    atomic_json(path, result)
    return result


def merge_parts():
    parts = []
    for index in range(len(PARTITIONS)):
        path = part_path(index)
        if not path.exists():
            raise RuntimeError(f"missing {path}")
        part = json.loads(path.read_text(encoding="utf-8"))
        if part["status"] != "COMPLETE":
            raise RuntimeError(f"incomplete {path}: {part['status']}")
        parts.append(part)
    rows = [row for part in parts for row in part["rows"]]
    result = {
        "status": "COMPLETE",
        "model": f"merged exact checkpointed E0={E0} fibre-compression audit",
        "theorem_inputs": theorem_inputs(),
        "method_audit": {
            "symmetry": "all labelled placements and all 5040 weighted S7 images",
            "overlap": (
                "solver-free exhaustive nonnegative-integer recursion on every "
                "weighted-port-balanced orbit; unbalanced rows are skipped only "
                "after their analytic obstruction is recorded"
            ),
            "disjoint_real": "exact Fraction least-norm bound",
            "weighted_port_balance": "orientation-independent analytic capacity condition",
            "claim_boundary": "no SAT/CP-SAT status is used in this artifact",
        },
        "labelled_placements": sum(part["coverage"]["labelled_placements"] for part in parts),
        "placement_orbits": len(rows),
        "summary": summarize(rows),
        "by_partition": [
            {
                "partition_index": part["partition_index"],
                "partition": part["partition"],
                "labelled_placements": part["coverage"]["labelled_placements"],
                **part["summary"],
                "artifact": str(part_path(part["partition_index"])),
            }
            for part in parts
        ],
        "rows": rows,
    }
    atomic_json(MASTER_PATH, result)
    print(json.dumps({key: result[key] for key in ("status", "labelled_placements", "placement_orbits", "summary")}), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--partition-index", type=int)
    parser.add_argument("--partition-indices", type=str)
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--merge", action="store_true")
    parser.add_argument("--classify-only", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    selected = sum(
        (
            args.partition_index is not None,
            args.partition_indices is not None,
            args.all,
            args.merge,
        )
    )
    if selected != 1:
        parser.error("choose exactly one of --partition-index, --all, --merge")
    if args.partition_index is not None:
        if not 0 <= args.partition_index < len(PARTITIONS):
            parser.error("partition index out of range")
        run_partition(args.partition_index, args.classify_only, args.force)
    elif args.partition_indices is not None:
        indices = tuple(int(value) for value in args.partition_indices.split(","))
        if not indices or len(set(indices)) != len(indices):
            parser.error("partition indices must be a nonempty duplicate-free CSV")
        if any(not 0 <= index < len(PARTITIONS) for index in indices):
            parser.error("partition index out of range")
        for index in indices:
            run_partition(index, args.classify_only, args.force)
    elif args.all:
        for index in range(len(PARTITIONS)):
            run_partition(index, args.classify_only, args.force)
    else:
        merge_parts()


if __name__ == "__main__":
    main()
