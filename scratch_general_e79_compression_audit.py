"""Exact finite compression audit for total fibre deficit five (E0 = 79).

This file is independent of every E0=80 SAT result.  It classifies deficit
placements on the 21 supports (the edges of K7) modulo S7, solves the
nonnegative overlap-block row equations exhaustively, and solves the bounded
integer disjoint-block deviation equations with CP-SAT.  Every reported
witness is then checked directly with Python integer arithmetic.

Notation follows scratch_general_structural_v2.py.  For D=4R,

    D_FF = 8 - 2 delta_F,
    sum_{G overlaps F} D_FG = 4 delta_F,
    sum_{G disjoint F} D_FG = 40 - 2 delta_F.

On a disjoint block put x_FG=4-D_FG.  Then Hx=2 delta and D_FG>=0 is
x_FG<=4.  The spectral square bound at E0=79 is tr(D^2)<=4564.
"""

from __future__ import annotations

from collections import Counter, deque
from fractions import Fraction
import itertools
import json
import math
from pathlib import Path
import sys


SUPPORTS = tuple(itertools.combinations(range(7), 2))
SUPPORT_INDEX = {edge: i for i, edge in enumerate(SUPPORTS)}
PARTITIONS = (
    (4, 1),
    (3, 2),
    (3, 1, 1),
    (2, 2, 1),
    (2, 1, 1, 1),
    (1, 1, 1, 1, 1),
)
RESULT_PATH = Path("scratch_general_e79_compression_audit.json")


def overlap(i: int, j: int) -> bool:
    return bool(set(SUPPORTS[i]) & set(SUPPORTS[j]))


OVERLAP_PAIRS = tuple(
    (i, j) for i, j in itertools.combinations(range(21), 2) if overlap(i, j)
)
DISJOINT_PAIRS = tuple(
    (i, j) for i, j in itertools.combinations(range(21), 2) if not overlap(i, j)
)


def apply_group_permutation(state: tuple[int, ...], permutation: tuple[int, ...]):
    image = [0] * 21
    for i, value in enumerate(state):
        edge = tuple(sorted(permutation[v] for v in SUPPORTS[i]))
        image[SUPPORT_INDEX[edge]] = value
    return tuple(image)


GENERATORS = []
for q in range(6):
    permutation = list(range(7))
    permutation[q], permutation[q + 1] = permutation[q + 1], permutation[q]
    GENERATORS.append(tuple(permutation))
GENERATORS = tuple(GENERATORS)
ALL_GROUP_PERMUTATIONS = tuple(itertools.permutations(range(7)))


def labelled_states(partition: tuple[int, ...]):
    """Generate every labelled placement, with repeated deficits unlabelled."""
    counts = Counter(partition)

    def visit(values, available, state):
        if not values:
            yield tuple(state)
            return
        value, multiplicity = values[0]
        for chosen in itertools.combinations(available, multiplicity):
            next_state = list(state)
            for node in chosen:
                next_state[node] = value
            remaining = tuple(node for node in available if node not in chosen)
            yield from visit(values[1:], remaining, next_state)

    yield from visit(tuple(sorted(counts.items(), reverse=True)), tuple(range(21)), [0] * 21)


def placement_orbits(partition: tuple[int, ...]):
    remaining = set(labelled_states(partition))
    rows = []
    while remaining:
        seed = min(remaining)
        orbit = {seed}
        queue = deque((seed,))
        while queue:
            state = queue.popleft()
            for generator in GENERATORS:
                image = apply_group_permutation(state, generator)
                if image not in orbit:
                    orbit.add(image)
                    queue.append(image)
        representative = min(orbit)
        assert representative == seed
        assert orbit <= remaining
        remaining.difference_update(orbit)
        rows.append((representative, len(orbit)))
    assert sum(size for _, size in rows) == sum(1 for _ in labelled_states(partition))
    return rows


def overlap_minimum(state: tuple[int, ...]):
    """Exhaust all nonnegative integer overlap-block totals."""
    exceptional = tuple(i for i, value in enumerate(state) if value)
    local_edges = tuple(
        (i, j) for i, j in itertools.combinations(exceptional, 2) if overlap(i, j)
    )
    demands = [4 * value for value in state]
    best = math.inf
    witnesses = []
    visited_leaves = 0

    # Choose an edge touching a currently most constrained positive row.
    def visit(residual, remaining_edges, assignment, cost):
        nonlocal best, visited_leaves
        if cost > best:
            return
        positive = [i for i in exceptional if residual[i]]
        if not positive:
            visited_leaves += 1
            if cost < best:
                best = cost
                witnesses.clear()
            if cost == best and len(witnesses) < 64:
                witnesses.append(tuple(sorted((u, v, w) for (u, v), w in assignment.items() if w)))
            return
        # A zero residual endpoint forces all of its unused incident weights to 0.
        possible_by_node = {
            i: [edge for edge in remaining_edges if i in edge and residual[edge[1] if edge[0] == i else edge[0]]]
            for i in positive
        }
        node = min(positive, key=lambda i: (len(possible_by_node[i]), -residual[i], i))
        possible = possible_by_node[node]
        if not possible:
            return
        edge = possible[0]
        u, v = edge
        rest = tuple(item for item in remaining_edges if item != edge)
        maximum = min(residual[u], residual[v])
        for value in range(maximum + 1):
            next_residual = list(residual)
            next_residual[u] -= value
            next_residual[v] -= value
            # Remaining incident capacity is bounded by the other row demands.
            feasible = True
            for endpoint in (u, v):
                capacity = sum(
                    next_residual[b if a == endpoint else a]
                    for a, b in rest
                    if endpoint in (a, b)
                )
                if next_residual[endpoint] > capacity:
                    feasible = False
            if not feasible:
                continue
            assignment[edge] = value
            visit(next_residual, rest, assignment, cost + value * value)
            assignment.pop(edge)

    visit(demands, local_edges, {}, 0)
    return {
        "feasible": best < math.inf,
        "minimum_square": None if best == math.inf else best,
        "stored_minimizers": [list(map(list, witness)) for witness in witnesses],
        "stored_minimizer_count": len(witnesses),
        "visited_complete_assignments": visited_leaves,
    }


def continuous_disjoint_minimum(state: tuple[int, ...]) -> Fraction:
    """Exact real least-norm value for Hx=2 delta on KG(7,2)."""
    b = [2 * value for value in state]
    total = sum(b)
    group_sums = [
        sum(value for value, support in zip(b, SUPPORTS) if group in support)
        for group in range(7)
    ]
    norm = sum(value * value for value in b)
    weight_j = Fraction(total * total, 21)
    weight_group = Fraction(7 * sum(v * v for v in group_sums) - 4 * total * total, 35)
    weight_residual = Fraction(norm) - weight_j - weight_group
    assert min(weight_j, weight_group, weight_residual) >= 0
    return weight_j / 20 + weight_group / 6 + weight_residual / 11


def disjoint_integer_minimum(state: tuple[int, ...], square_limit: int):
    """Find the exact bounded integer minimum with CP-SAT.

    The bound |x_e|<=floor(sqrt(square_limit)) loses no vector whose total
    square is within square_limit.  x_e<=4 is exactly D_FG>=0.
    """
    if square_limit < 0:
        return {"status": "SKIPPED", "reason": "negative square budget"}
    sys.path.insert(0, str(Path(".ortools").resolve()))
    from ortools.sat.python import cp_model

    radius = math.isqrt(square_limit)
    lower = -radius
    upper = min(4, radius)
    domain = tuple(range(lower, upper + 1))
    model = cp_model.CpModel()
    xs = []
    qs = []
    incident = [[] for _ in range(21)]
    for edge_index, (u, v) in enumerate(DISJOINT_PAIRS):
        x = model.NewIntVar(lower, upper, f"x_{u}_{v}")
        q = model.NewIntVar(0, radius * radius, f"q_{u}_{v}")
        model.AddAllowedAssignments((x, q), ((value, value * value) for value in domain))
        xs.append(x)
        qs.append(q)
        incident[u].append(x)
        incident[v].append(x)
    for node in range(21):
        model.Add(sum(incident[node]) == 2 * state[node])
    model.Add(sum(qs) <= square_limit)
    model.Minimize(sum(qs))
    solver = cp_model.CpSolver()
    solver.parameters.num_search_workers = 1
    solver.parameters.cp_model_presolve = True
    status = solver.Solve(model)
    name = solver.StatusName(status)
    result = {
        "status": name,
        "square_limit": square_limit,
        "variable_domain": [lower, upper],
        "branches": solver.NumBranches(),
        "conflicts": solver.NumConflicts(),
    }
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        values = [solver.Value(x) for x in xs]
        square = sum(value * value for value in values)
        rows = [0] * 21
        witness = []
        for (u, v), value in zip(DISJOINT_PAIRS, values):
            rows[u] += value
            rows[v] += value
            if value:
                witness.append([u, v, value])
            assert value <= 4
        assert rows == [2 * value for value in state]
        assert square <= square_limit
        result.update({
            "minimum_square": square,
            "witness": witness,
            "witness_row_sums": rows,
            "witness_verified": True,
        })
    return result


def spectral_square_upper_e79() -> int:
    # Fixed Ritz values are 12,-2^6.  The remaining 14 lie in [-4,3]
    # and sum to 79/2.  The maximizing endpoint vector is 3^13,(1/2)^1.
    return 16 * (168 + 13 * 9) + 4


def diagonal_square(state):
    return sum((8 - 2 * value) ** 2 for value in state)


def state_description(state):
    return [
        {"support_index": i, "support": list(SUPPORTS[i]), "deficit": value}
        for i, value in enumerate(state)
        if value
    ]


def support_graph_signature(state):
    weighted_edges = [
        (SUPPORTS[i][0], SUPPORTS[i][1], value)
        for i, value in enumerate(state)
        if value
    ]
    simple_edges = [(u, v) for u, v, _ in weighted_edges]
    adjacency = [set() for _ in range(7)]
    for u, v in simple_edges:
        adjacency[u].add(v)
        adjacency[v].add(u)
    unseen = set(range(7))
    components = []
    while unseen:
        seed = min(unseen)
        component = {seed}
        queue = [seed]
        unseen.remove(seed)
        while queue:
            u = queue.pop()
            for v in adjacency[u]:
                if v in unseen:
                    unseen.remove(v)
                    component.add(v)
                    queue.append(v)
        edge_count = sum(u in component and v in component for u, v in simple_edges)
        triangles = sum(
            v in adjacency[u] and w in adjacency[u] and w in adjacency[v]
            for u, v, w in itertools.combinations(sorted(component), 3)
        )
        components.append({
            "vertices": len(component),
            "edges": edge_count,
            "degree_sequence": sorted((len(adjacency[u]) for u in component), reverse=True),
            "triangles": triangles,
        })
    components.sort(
        key=lambda row: (row["vertices"], row["edges"], row["degree_sequence"], row["triangles"]),
        reverse=True,
    )
    exceptional = [i for i, value in enumerate(state) if value]
    line_edges = [
        (i, j)
        for i, j in itertools.combinations(range(len(exceptional)), 2)
        if overlap(exceptional[i], exceptional[j])
    ]
    line_degrees = sorted(
        (sum(overlap(i, j) for j in exceptional if i != j) for i in exceptional),
        reverse=True,
    )
    canonical_line_bits = min(
        "".join(
            "1" if tuple(sorted((permutation[i], permutation[j]))) in line_edges else "0"
            for i, j in itertools.combinations(range(len(exceptional)), 2)
        )
        for permutation in itertools.permutations(range(len(exceptional)))
    )
    return {
        "degree_sequence_on_seven_groups": sorted((len(row) for row in adjacency), reverse=True),
        "components": components,
        "exceptional_overlap_graph_degree_sequence": line_degrees,
        "exceptional_overlap_graph_edges": [list(edge) for edge in line_edges],
        "exceptional_overlap_graph_canonical_bits": canonical_line_bits,
        "weighted_edges": [list(edge) for edge in weighted_edges],
    }


def audit():
    spectral_upper = spectral_square_upper_e79()
    assert spectral_upper == 4564
    result_rows = []
    orbit_totals = {}
    for partition in PARTITIONS:
        orbits = placement_orbits(partition)
        orbit_totals[str(partition)] = {
            "orbit_count": len(orbits),
            "labelled_count": sum(size for _, size in orbits),
        }
        for orbit_index, (state, orbit_size) in enumerate(orbits):
            stabilizer_order = sum(
                apply_group_permutation(state, permutation) == state
                for permutation in ALL_GROUP_PERMUTATIONS
            )
            assert orbit_size * stabilizer_order == 5040
            ov = overlap_minimum(state)
            diag = diagonal_square(state)
            # tr(D^2)=diag+3280+2*(overlap_square+x_square) at deficit 5.
            joint_budget = (spectral_upper - diag - 3280) // 2
            assert diag + 3280 + 2 * joint_budget <= spectral_upper
            continuous = continuous_disjoint_minimum(state)
            if ov["feasible"]:
                x_budget = joint_budget - ov["minimum_square"]
                disjoint = disjoint_integer_minimum(state, x_budget)
            else:
                x_budget = None
                disjoint = {"status": "SKIPPED", "reason": "overlap rows infeasible"}
            extended_disjoint = None
            if (
                partition == (2, 1, 1, 1)
                and ov["feasible"]
                and disjoint["status"] == "INFEASIBLE"
            ):
                # Record the actual nearby minimum, not merely failure inside
                # the spectral budget.  The independent sparse SAT audit uses
                # its signed-value profile as a positive encoding sanity test.
                extended_disjoint = disjoint_integer_minimum(state, 30)
                assert extended_disjoint["status"] == "OPTIMAL"
            passes = (
                ov["feasible"]
                and disjoint["status"] in ("OPTIMAL", "FEASIBLE")
                and ov["minimum_square"] + disjoint["minimum_square"] <= joint_budget
            )
            row = {
                "partition": list(partition),
                "orbit_index": orbit_index,
                "orbit_size": orbit_size,
                "stabilizer_order": stabilizer_order,
                "exceptional_supports": state_description(state),
                "exceptional_support_graph": support_graph_signature(state),
                "diagonal_square": diag,
                "joint_off_diagonal_square_budget": joint_budget,
                "overlap": ov,
                "disjoint_continuous_minimum": str(continuous),
                "disjoint_continuous_ceiling": math.ceil(continuous),
                "disjoint_square_budget_after_overlap_minimum": x_budget,
                "disjoint_integer": disjoint,
                "disjoint_integer_extended_limit_30": extended_disjoint,
                "passes_compression_square_and_BP": passes,
            }
            if passes:
                row["verified_total_D_square"] = (
                    diag + 3280 + 2 * (ov["minimum_square"] + disjoint["minimum_square"])
                )
                assert row["verified_total_D_square"] <= spectral_upper
            result_rows.append(row)
    return {
        "model": "E0=79 exact fibre-compression placement audit",
        "independence_warning": "No E0=80 SAT/UNSAT result is assumed or used.",
        "theorem_inputs": {
            "total_deficit": 5,
            "total_fibre_edges_E0": 79,
            "spectral_D_square_upper": spectral_upper,
            "spectral_maximizing_free_Ritz_multiset": [3] * 13 + [0.5],
            "BP_overlap_row_sum": "4*delta_F",
            "BP_disjoint_D_row_sum": "40-2*delta_F",
            "disjoint_deviation_row_sum": "sum x_FG=2*delta_F for x=4-D",
        },
        "method_audit": {
            "symmetry": "All labelled placements generated, exact S7 orbits formed using six adjacent transpositions, and every orbit size independently checked against its stabilizer by all 5040 permutations.",
            "overlap": "Pure Python exhaustive nonnegative-integer recursion; no solver.",
            "disjoint": "Finite one-worker CP-SAT optimization inside the exact spectral square radius; witnesses independently checked.",
            "claim_boundary": "Support classification is a reproducible computation, not a proof certificate for CP-SAT infeasibility/optimality.",
        },
        "orbit_totals": orbit_totals,
        "rows": result_rows,
    }


def main():
    result = audit()
    RESULT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    summary = Counter()
    for row in result["rows"]:
        summary[(tuple(row["partition"]), row["passes_compression_square_and_BP"])] += 1
    print(json.dumps({
        "orbits": len(result["rows"]),
        "passing_orbits": sum(row["passes_compression_square_and_BP"] for row in result["rows"]),
        "summary": {str(key): value for key, value in summary.items()},
    }, sort_keys=True))


if __name__ == "__main__":
    main()
