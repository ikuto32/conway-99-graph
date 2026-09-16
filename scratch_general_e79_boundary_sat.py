"""Independent sparse-CNF audit of the three E0=79 boundary exclusions.

The pure-Python overlap recursion leaves three placements of deficit pattern
(2,1,1,1).  Their overlap-square minima leave disjoint-deviation budgets
12, 12, and 8.  This script does not optimize: it exhausts every possible
global signed-value count profile with sum(x)=5 and sum(x^2) within the
budget, then asks a SAT solver for Hx=2*delta on KG(7,2).

Thus this is algorithmically independent of the integer CP-SAT optimization
used in scratch_general_e79_compression_audit.py.  It emits no claim about
lifting a compression to the 84 outer vertices.
"""

from __future__ import annotations

from collections import Counter
import argparse
import itertools
import json
import math
from pathlib import Path
import sys
import time
import types

from scratch_general_e79_compression_audit import DISJOINT_PAIRS


AUDIT_PATH = Path("scratch_general_e79_compression_audit.json")
RESULT_PATH = Path("scratch_general_e79_boundary_sat.json")


def install_pysat_path():
    sys.path.insert(0, str(Path(".deps").resolve()))
    try:
        import bz2  # noqa: F401
    except ModuleNotFoundError:
        placeholder = types.ModuleType("bz2")
        placeholder.BZ2File = None
        sys.modules["bz2"] = placeholder


def value_profiles(limit):
    radius = math.isqrt(limit)
    values = tuple(value for value in range(-radius, min(4, radius) + 1) if value)
    rows = []

    def visit(position, remaining_square, remaining_sum, counts):
        if position == len(values):
            if remaining_sum == 0:
                square = sum(value * value * count for value, count in zip(values, counts))
                rows.append({
                    "square": square,
                    "counts": {str(value): count for value, count in zip(values, counts) if count},
                })
            return
        value = values[position]
        maximum = remaining_square // (value * value)
        for count in range(maximum + 1):
            visit(
                position + 1,
                remaining_square - count * value * value,
                remaining_sum - count * value,
                counts + (count,),
            )

    visit(0, limit, 5, ())
    # Hx=even makes the odd-valued support Eulerian.  We deliberately retain
    # even the profiles with only one odd edge; the explicit parity CNF then
    # rejects them, which also audits that strengthening.
    rows.sort(key=lambda row: (row["square"], tuple(row["counts"].items())))
    return rows


def state_from_row(row):
    state = [0] * 21
    for item in row["exceptional_supports"]:
        state[item["support_index"]] = item["deficit"]
    return tuple(state)


def solve_profile(state, profile, solver_name):
    install_pysat_path()
    from pysat.card import CardEnc, EncType
    from pysat.formula import IDPool
    from pysat.solvers import Solver

    allowed_nonzero = tuple(sorted(int(value) for value in profile["counts"]))
    domain = (0,) + allowed_nonzero
    pool = IDPool()
    clauses = []
    choice = {}
    for edge_index, edge in enumerate(DISJOINT_PAIRS):
        literals = []
        for value in domain:
            literal = pool.id(("x", edge_index, value))
            choice[edge_index, value] = literal
            literals.append(literal)
        clauses.extend(CardEnc.equals(
            literals, 1, vpool=pool, encoding=EncType.seqcounter
        ).clauses)

    # Fix the complete signed-value count profile.  This is the key sparse
    # split that makes the independent SAT audit small and auditable.
    for value in allowed_nonzero:
        literals = [choice[edge_index, value] for edge_index in range(len(DISJOINT_PAIRS))]
        clauses.extend(CardEnc.equals(
            literals,
            int(profile["counts"][str(value)]),
            vpool=pool,
            encoding=EncType.seqcounter,
        ).clauses)

    def exactly_one(literals):
        if len(literals) == 1:
            clauses.append([literals[0]])
        else:
            clauses.extend(CardEnc.equals(
                literals, 1, vpool=pool, encoding=EncType.seqcounter
            ).clauses)

    # A deterministic sum automaton for each of the 21 rows.
    for node in range(21):
        incident = [
            edge_index for edge_index, edge in enumerate(DISJOINT_PAIRS) if node in edge
        ]
        assert len(incident) == 10
        target = 2 * state[node]
        forward = [{0}]
        for _ in incident:
            forward.append({total + value for total in forward[-1] for value in domain})
        suffix = [{0} for _ in range(11)]
        for position in range(9, -1, -1):
            suffix[position] = {value + total for value in domain for total in suffix[position + 1]}
        allowed = [
            {total for total in forward[position] if target - total in suffix[position]}
            for position in range(11)
        ]
        assert all(allowed)
        states = []
        for position, totals in enumerate(allowed):
            mapping = {
                total: pool.id(("row", node, position, total)) for total in sorted(totals)
            }
            exactly_one(list(mapping.values()))
            states.append(mapping)
        for position, edge_index in enumerate(incident):
            for total, state_literal in states[position].items():
                for value in domain:
                    value_literal = choice[edge_index, value]
                    following = total + value
                    if following in states[position + 1]:
                        clauses.append([
                            -state_literal, -value_literal, states[position + 1][following]
                        ])
                    else:
                        clauses.append([-state_literal, -value_literal])

    # Explicit mod-2 rows strengthen propagation.  Odd-valued selected edges
    # must have even degree at every support because every target is even.
    odd_values = tuple(value for value in allowed_nonzero if value % 2)
    for node in range(21):
        incident = [
            edge_index for edge_index, edge in enumerate(DISJOINT_PAIRS) if node in edge
        ]
        parity_inputs = []
        for edge_index in incident:
            odd = pool.id(("odd", edge_index))
            odd_choices = [choice[edge_index, value] for value in odd_values]
            if odd_choices:
                for literal in odd_choices:
                    clauses.append([-literal, odd])
                clauses.append([-odd] + odd_choices)
            else:
                clauses.append([-odd])
            parity_inputs.append(odd)
        accumulator = pool.id(("parity", node, 0))
        clauses.append([-accumulator])
        for position, literal in enumerate(parity_inputs, 1):
            following = pool.id(("parity", node, position))
            # following <-> accumulator XOR literal
            clauses.extend((
                [-accumulator, -literal, -following],
                [accumulator, literal, -following],
                [accumulator, -literal, following],
                [-accumulator, literal, following],
            ))
            accumulator = following
        clauses.append([-accumulator])

    started = time.monotonic()
    with Solver(name=solver_name, bootstrap_with=clauses) as solver:
        answer = solver.solve()
        model = solver.get_model() if answer else None
        stats = solver.accum_stats()
    result = {
        "profile": profile,
        "status": "SAT" if answer else "UNSAT",
        "variables": pool.top,
        "clauses": len(clauses),
        "solve_seconds": round(time.monotonic() - started, 6),
        "stats": stats,
    }
    if answer:
        positive = {literal for literal in model if literal > 0}
        values = []
        row_sums = [0] * 21
        witness = []
        for edge_index, (u, v) in enumerate(DISJOINT_PAIRS):
            selected = [value for value in domain if choice[edge_index, value] in positive]
            assert len(selected) == 1
            value = selected[0]
            values.append(value)
            row_sums[u] += value
            row_sums[v] += value
            if value:
                witness.append([u, v, value])
        assert row_sums == [2 * value for value in state]
        assert sum(values) == 5
        assert sum(value * value for value in values) == profile["square"]
        result.update({"witness": witness, "witness_verified": True})
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--solver", default="cadical195")
    args = parser.parse_args()
    audit = json.loads(AUDIT_PATH.read_text(encoding="utf-8"))
    boundary = [
        row for row in audit["rows"]
        if tuple(row["partition"]) == (2, 1, 1, 1) and row["overlap"]["feasible"]
    ]
    assert len(boundary) == 3
    records = []
    for row in boundary:
        state = state_from_row(row)
        limit = row["disjoint_square_budget_after_overlap_minimum"]
        profiles = value_profiles(limit)
        profile_records = []
        for profile in profiles:
            result = solve_profile(state, profile, args.solver)
            profile_records.append(result)
            print(json.dumps({
                "orbit_index": row["orbit_index"],
                "profile": profile,
                "status": result["status"],
                "seconds": result["solve_seconds"],
            }), flush=True)
        extended = row["disjoint_integer_extended_limit_30"]
        assert extended and extended["status"] == "OPTIMAL"
        value_counts = Counter(item[2] for item in extended["witness"])
        positive_profile = {
            "square": extended["minimum_square"],
            "counts": {str(value): count for value, count in sorted(value_counts.items())},
        }
        positive_control = solve_profile(state, positive_profile, args.solver)
        assert positive_control["status"] == "SAT" and positive_control["witness_verified"]
        records.append({
            "partition": row["partition"],
            "orbit_index": row["orbit_index"],
            "exceptional_supports": row["exceptional_supports"],
            "overlap_minimum_square": row["overlap"]["minimum_square"],
            "disjoint_square_limit": limit,
            "profile_count": len(profiles),
            "status": "SAT" if any(item["status"] == "SAT" for item in profile_records) else "UNSAT",
            "profiles": profile_records,
            "first_outside_budget_profile_positive_control": positive_control,
        })
    output = {
        "model": "independent sparse exact-CNF audit of three E0=79 boundary placements",
        "solver": f"{args.solver} via PySAT",
        "status": "UNSAT" if all(row["status"] == "UNSAT" for row in records) else "SAT",
        "method": "Exhaust all signed global value-count profiles, then exact row-sum SAT with explicit parity; the first CP-SAT-optimal profile outside each budget is separately required SAT as a positive encoding control.",
        "claim_boundary": "Compression-only computation; no proof certificate and no claim about E0=79 nonexistence.",
        "records": records,
    }
    RESULT_PATH.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": output["status"],
        "orbits": [(row["orbit_index"], row["status"], row["profile_count"]) for row in records],
    }), flush=True)


if __name__ == "__main__":
    main()
