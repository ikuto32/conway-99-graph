"""Independent disjoint-block integer minima for surviving E0=76 supports.

For disjoint support fibres F,G put x_FG=4-D_FG.  Physical block sizes give
-12 <= x <= 4 and BP gives sum_{G disjoint F} x_FG=2*delta_F.  This script
independently minimizes sum x_FG^2 for each locally surviving support branch,
directly verifies every returned witness, and applies the resulting proven
optimum to the actual local overlap-square values.
"""

from __future__ import annotations

from collections import Counter
import argparse
import itertools
import json
import math
import time
from pathlib import Path


LOCAL = Path("scratch_e76_independent_local.json")
COMPRESSION = Path("scratch_general_e76_compression_audit.json")
OUTPUT = Path("scratch_e76_independent_integer.json")
SUPPORTS = tuple(itertools.combinations(range(7), 2))
DISJOINT_PAIRS = tuple(
    (left, right)
    for left, right in itertools.combinations(range(21), 2)
    if set(SUPPORTS[left]).isdisjoint(SUPPORTS[right])
)
assert len(DISJOINT_PAIRS) == 105


def solve_minimum(deficits, square_limit, seconds, workers, seed):
    from ortools.sat.python import cp_model

    model = cp_model.CpModel()
    radius = math.isqrt(square_limit)
    lower, upper = max(-12, -radius), min(4, radius)
    x = {
        pair: model.NewIntVar(lower, upper, f"x_{pair[0]}_{pair[1]}")
        for pair in DISJOINT_PAIRS
    }
    squares = {}
    for pair, variable in x.items():
        square = model.NewIntVar(0, radius * radius, f"q_{pair[0]}_{pair[1]}")
        model.AddAllowedAssignments(
            (variable, square),
            tuple((value, value * value) for value in range(lower, upper + 1)),
        )
        squares[pair] = square
    for support_index in range(21):
        model.Add(sum(
            variable
            for pair, variable in x.items()
            if support_index in pair
        ) == 2 * deficits[support_index])
    objective = sum(squares.values())
    model.Add(objective <= square_limit)
    model.Minimize(objective)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = seed
    started = time.monotonic()
    status = solver.Solve(model)
    elapsed = time.monotonic() - started
    record = {
        "status": solver.StatusName(status),
        "seconds": round(elapsed, 3),
        "branches": solver.NumBranches(),
        "conflicts": solver.NumConflicts(),
        "best_objective_bound": solver.BestObjectiveBound(),
        "formal_proof_certificate": None,
        "square_limit": square_limit,
        "variable_domain": [lower, upper],
    }
    if status in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        values = {pair: solver.Value(variable) for pair, variable in x.items()}
        minimum = sum(value * value for value in values.values())
        row_sums = [
            sum(value for pair, value in values.items() if support_index in pair)
            for support_index in range(21)
        ]
        D_values = {pair: 4 - value for pair, value in values.items()}
        verified = (
            row_sums == [2 * value for value in deficits]
            and all(lower <= value <= upper for value in values.values())
            and all(0 <= value <= 16 for value in D_values.values())
            and minimum == round(solver.ObjectiveValue())
        )
        assert verified
        record.update({
            "minimum_square": minimum,
            "witness_nonzero": [
                [left, right, value]
                for (left, right), value in sorted(values.items())
                if value
            ],
            "witness_row_sums": row_sums,
            "witness_directly_verified": True,
        })
    return record


def representative_block_square(representative, exceptional):
    support_index = {support: index for index, support in enumerate(exceptional)}
    counts = Counter()
    for raw_u, raw_v in representative["edges_by_symbol_label"]:
        u, v = tuple(raw_u), tuple(raw_v)
        A = tuple(symbol // 2 for symbol in u)
        B = tuple(symbol // 2 for symbol in v)
        if A == B:
            continue
        assert set(A) & set(B)
        counts[tuple(sorted((support_index[A], support_index[B])))] += 1
    assert sum(counts.values()) == 16
    return sum(value * value for value in counts.values())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seconds", type=float, default=30)
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()
    local = json.loads(LOCAL.read_text(encoding="utf-8"))
    compression = json.loads(COMPRESSION.read_text(encoding="utf-8"))
    compression_map = {
        (tuple(row["partition"]), row["orbit_index"]): row
        for row in compression["rows"]
    }
    source_rows = [row for row in local["rows"] if row["local_graph_orbits"]]
    assert len(source_rows) == 10
    rows = []
    for offset, source in enumerate(source_rows):
        deficits = [0] * 21
        exceptional = []
        for item in source["exceptional_supports"]:
            index = item["support_index"]
            assert SUPPORTS[index] == tuple(item["support"])
            deficits[index] = item["deficit"]
            exceptional.append(tuple(item["support"]))
        forced_histogram = {
            int(square): count
            for square, count in source["after_forced_BP_square_histogram"].items()
        }
        square_limit = source["joint_square_budget"] - min(forced_histogram)
        solved = solve_minimum(
            deficits, square_limit, args.seconds, args.workers, 7600 + offset
        )
        canonical_partition = tuple(sorted(
            (item["deficit"] for item in source["exceptional_supports"]),
            reverse=True,
        ))
        key = (canonical_partition, source["compression_orbit_index"])
        input_integer = compression_map[key].get("disjoint_integer")
        if solved["status"] == "OPTIMAL" and input_integer:
            solved["agrees_with_compression_minimum"] = (
                solved["minimum_square"] == input_integer.get("minimum_square")
            )
            assert solved["agrees_with_compression_minimum"]

        minimum = solved.get("minimum_square") if solved["status"] == "OPTIMAL" else None
        kept_representatives = []
        kept_raw = 0
        if minimum is not None:
            kept_raw = sum(
                count
                for square, count in forced_histogram.items()
                if square + minimum <= source["joint_square_budget"]
            )
            for representative in source["representatives"]:
                square = representative_block_square(representative, exceptional)
                if square + minimum <= source["joint_square_budget"]:
                    copied = dict(representative)
                    copied["actual_overlap_block_square"] = square
                    copied["integer_plus_overlap_square"] = square + minimum
                    kept_representatives.append(copied)
            assert sum(row["local_orbit_size"] for row in kept_representatives) == kept_raw
        row = {
            "partition": list(canonical_partition),
            "deficits_in_support_order": deficits,
            "compression_orbit_index": source["compression_orbit_index"],
            "exceptional_supports": source["exceptional_supports"],
            "joint_square_budget": source["joint_square_budget"],
            "disjoint_integer": solved,
            "raw_local_graphs_before_integer_bound": source["distinct_forced_local_graphs"],
            "local_orbits_before_integer_bound": source["local_graph_orbits"],
            "raw_local_graphs_after_integer_bound": kept_raw,
            "local_orbits_after_integer_bound": len(kept_representatives),
            "representatives_after_integer_bound": kept_representatives,
        }
        rows.append(row)
        print(json.dumps({
            "offset": offset,
            "partition": row["partition"],
            "orbit": row["compression_orbit_index"],
            "status": solved["status"],
            "minimum": solved.get("minimum_square"),
            "raw_after": kept_raw,
            "orbits_after": len(kept_representatives),
        }), flush=True)

    all_optimal = all(row["disjoint_integer"]["status"] == "OPTIMAL" for row in rows)
    result = {
        "model": "independent E0=76 disjoint integer minima and local spectral filter",
        "inputs": [str(LOCAL), str(COMPRESSION)],
        "integer_system": {
            "variables": 105,
            "domain": [-12, 4],
            "row_equations": "sum_{G disjoint F} x_FG = 2 delta_F",
            "objective": "minimize sum x_FG^2",
            "physical_interpretation": "x_FG=4-D_FG with 0<=D_FG<=16",
        },
        "solver": "OR-Tools CP-SAT",
        "seconds_per_support": args.seconds,
        "workers": args.workers,
        "all_optimal": all_optimal,
        "proof_status": "no independently checked optimization certificates",
        "support_branches_before_integer_bound": len(rows),
        "local_graphs_before_integer_bound": sum(
            row["raw_local_graphs_before_integer_bound"] for row in rows
        ),
        "local_orbits_before_integer_bound": sum(
            row["local_orbits_before_integer_bound"] for row in rows
        ),
        "support_branches_after_integer_bound": sum(
            row["raw_local_graphs_after_integer_bound"] > 0 for row in rows
        ) if all_optimal else None,
        "local_graphs_after_integer_bound": sum(
            row["raw_local_graphs_after_integer_bound"] for row in rows
        ) if all_optimal else None,
        "local_orbits_after_integer_bound": sum(
            row["local_orbits_after_integer_bound"] for row in rows
        ) if all_optimal else None,
        "rows": rows,
        "existing_E76_integer_implementation_imported": False,
        "ok": all_optimal,
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": result["ok"],
        "minimums": [row["disjoint_integer"].get("minimum_square") for row in rows],
        "support_after": result["support_branches_after_integer_bound"],
        "graphs_after": result["local_graphs_after_integer_bound"],
        "orbits_after": result["local_orbits_after_integer_bound"],
    }))


if __name__ == "__main__":
    main()
