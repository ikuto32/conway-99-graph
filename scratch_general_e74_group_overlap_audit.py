"""Exact group-resolved overlap-square audit for the E0=74 survivors.

For a fibre F={g,h} of deficit d, BP=PA0 supplies exactly 2d ports at g
and 2d ports at h.  Hence overlap-block totals at each root group form a
loopless integer multigraph on the exceptional fibres incident with that
group, with degree 2d at fibre F.  The seven groups are edge-disjoint, so the
exact minimum overlap square is the sum of seven tiny degree-sequence DPs.

This strengthens the earlier relaxation which imposed only the combined row
sum 4d.  It is solver-free and makes no fibre-orientation assumption.
"""

from __future__ import annotations

import json
import math
import os
from functools import lru_cache
from pathlib import Path

import scratch_general_e74_compression as e74


INPUT = Path("scratch_general_e74_compression_audit.json")
OUTPUT = Path("scratch_general_e74_group_overlap_audit.json")


def atomic_json(path, value):
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def bounded_compositions(total, bounds):
    """Yield all nonnegative vectors of given sum within coordinate bounds."""
    if not bounds:
        if total == 0:
            yield ()
        return
    suffix_capacity = [0] * (len(bounds) + 1)
    for index in range(len(bounds) - 1, -1, -1):
        suffix_capacity[index] = suffix_capacity[index + 1] + bounds[index]

    def visit(index, residual, prefix):
        if index == len(bounds):
            if residual == 0:
                yield tuple(prefix)
            return
        low = max(0, residual - suffix_capacity[index + 1])
        high = min(bounds[index], residual)
        for value in range(low, high + 1):
            yield from visit(index + 1, residual - value, prefix + [value])

    yield from visit(0, total, [])


def degree_square_minimum(degrees):
    """Exact minimum sum m_ij^2 for a loopless integer multigraph."""
    degrees = tuple(degrees)

    @lru_cache(maxsize=None)
    def solve(residual):
        if not any(residual):
            return 0, ()
        positive = [index for index, value in enumerate(residual) if value]
        # Fix every edge incident with a most-constrained maximum-degree node.
        i = max(positive, key=lambda index: (residual[index], -index))
        others = [index for index in positive if index != i]
        if not others or residual[i] > sum(residual[j] for j in others):
            return math.inf, ()
        best_cost = math.inf
        best_edges = ()
        for amounts in bounded_compositions(
            residual[i], tuple(residual[j] for j in others)
        ):
            next_residual = list(residual)
            next_residual[i] = 0
            edges = []
            cost = 0
            for j, value in zip(others, amounts):
                next_residual[j] -= value
                if value:
                    edges.append((min(i, j), max(i, j), value))
                    cost += value * value
            tail_cost, tail_edges = solve(tuple(next_residual))
            cost += tail_cost
            if cost < best_cost:
                best_cost = cost
                best_edges = tuple(edges) + tail_edges
        return best_cost, best_edges

    cost, edges = solve(degrees)
    return cost, edges, solve.cache_info().currsize


def group_resolved_minimum(state, supports):
    total_cost = 0
    details = []
    for group in range(7):
        fibres = tuple(
            index for index, support in enumerate(supports)
            if group in support and state[index]
        )
        degrees = tuple(2 * state[index] for index in fibres)
        cost, local_edges, states = degree_square_minimum(degrees)
        if cost == math.inf:
            return math.inf, details
        witness = [
            [fibres[left], fibres[right], value]
            for left, right, value in local_edges
        ]
        row_sums = {index: 0 for index in fibres}
        for left, right, value in witness:
            assert group in set(supports[left]) & set(supports[right])
            row_sums[left] += value
            row_sums[right] += value
        assert [row_sums[index] for index in fibres] == list(degrees)
        assert sum(value * value for _left, _right, value in witness) == cost
        total_cost += cost
        details.append(
            {
                "group": group,
                "fibres": list(fibres),
                "degrees": list(degrees),
                "minimum_square": cost,
                "one_minimizer": witness,
                "dp_states": states,
            }
        )
    return total_cost, details


def main():
    e74.configure()
    g = e74.generic
    source = json.loads(INPUT.read_text(encoding="utf-8"))
    assert source["status"] == "COMPLETE"
    assert source["summary"]["final_intersection"] == 249
    rows = []
    for part in source["by_partition"]:
        part_source = json.loads(Path(part["artifact"]).read_text(encoding="utf-8"))
        assert part_source["status"] == "COMPLETE"
        for row in part_source["rows"]:
            if not row["passes_weighted_port_overlap_and_real_relaxation"]:
                continue
            state = g.decode(int(row["representative_code_hex"], 16))
            minimum, details = group_resolved_minimum(state, g.base.SUPPORTS)
            assert minimum < math.inf
            weak_minimum = row["overlap"]["minimum_square"]
            assert minimum >= weak_minimum
            continuous_ceiling = row["disjoint_continuous_ceiling"]
            budget = row["joint_off_diagonal_square_budget"]
            passes = minimum + continuous_ceiling <= budget
            rows.append(
                {
                    "partition_index": part["partition_index"],
                    "partition": part["partition"],
                    "orbit_index": row["orbit_index"],
                    "representative_code_hex": row["representative_code_hex"],
                    "orbit_size": row["orbit_size"],
                    "combined_row_overlap_minimum_square": weak_minimum,
                    "group_resolved_overlap_minimum_square": minimum,
                    "disjoint_continuous_minimum": row["disjoint_continuous_minimum"],
                    "disjoint_continuous_ceiling": continuous_ceiling,
                    "joint_off_diagonal_square_budget": budget,
                    "passes_group_resolved_overlap_and_real_bound": passes,
                    "groups": details,
                }
            )
    assert len(rows) == 249
    survivors = [row for row in rows if row["passes_group_resolved_overlap_and_real_bound"]]
    by_partition = []
    for index, partition in enumerate(e74.PARTITIONS):
        selected = [row for row in rows if row["partition_index"] == index]
        kept = [row for row in selected if row["passes_group_resolved_overlap_and_real_bound"]]
        if selected:
            by_partition.append(
                {
                    "partition_index": index,
                    "partition": list(partition),
                    "input_orbits": len(selected),
                    "surviving_orbits": len(kept),
                    "input_labelled": sum(row["orbit_size"] for row in selected),
                    "surviving_labelled": sum(row["orbit_size"] for row in kept),
                }
            )
    result = {
        "status": "VERIFIED",
        "model": "E0=74 exact group-resolved overlap-square DP",
        "claim_type": "analytic equations plus solver-free exhaustive finite DP",
        "derivation": (
            "Each deficit-d fibre has exactly 2d ports at each endpoint group. "
            "At each group the overlap totals are a loopless integer multigraph "
            "with those degrees. Distinct groups own disjoint overlap pairs, so "
            "the exact global minimum is the sum of the seven group minima."
        ),
        "input_orbits": len(rows),
        "input_labelled": sum(row["orbit_size"] for row in rows),
        "surviving_orbits": len(survivors),
        "surviving_labelled": sum(row["orbit_size"] for row in survivors),
        "by_partition": by_partition,
        "rows": rows,
    }
    atomic_json(OUTPUT, result)
    print(json.dumps({key: result[key] for key in (
        "status", "input_orbits", "input_labelled", "surviving_orbits", "surviving_labelled"
    )}))


if __name__ == "__main__":
    main()
