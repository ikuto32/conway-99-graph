"""Strengthened exact CP-SAT model for the fixed-point-free C3 branch.

Let the 99 vertices be (i,a), where i is one of 33 vertex orbits and
a is in Z/3.  Between two distinct orbits i,j, an invariant bipartite
graph is a union of the three cyclic matchings.  Its multiplicity m_ij is
therefore the number of selected phase shifts.

This model combines two exact descriptions which were previously searched
separately:

* the quotient identities M^2 + M = 12 I + 6 J, with off-diagonal
  multiplicities in {0,1,2};
* all phase-level common-neighbour upper bounds.  Since all degrees are 14,
  the usual global double count makes these upper bounds equalities.

For the only remaining trace cases t=6 and t=27, the multiplicity-two
edges on the 33-t independent orbits form a simple 2-factor.  Every such
2-factor is, up to relabelling, a disjoint union of canonical consecutive
cycles whose lengths form a partition into parts at least three.  Selecting
one of those canonical forms is therefore a safe symmetry break.  For t=27
the two possibilities are C6 and 2C3; both are retained as explicit modes.

Every feasible assignment is expanded to 99 vertices and independently
checked on all 4,851 unordered pairs before a witness is written.
"""

from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path
from typing import Iterable

from ortools.sat.python import cp_model


N_ORBITS = 33
PHASES = 3
N = N_ORBITS * PHASES
T_VALUES = (6, 27)


def pair(i: int, j: int) -> tuple[int, int]:
    return (i, j) if i < j else (j, i)


def partitions_at_least_three(total: int, minimum: int = 3) -> Iterable[tuple[int, ...]]:
    """Yield nondecreasing partitions of total with every part >= 3."""
    if total == 0:
        yield ()
        return
    for first in range(minimum, total + 1):
        for rest in partitions_at_least_three(total - first, first):
            yield (first,) + rest


def canonical_cycle_edges(first_vertex: int, lengths: tuple[int, ...]) -> frozenset[tuple[int, int]]:
    """Canonical labelled disjoint cycles with the supplied lengths."""
    answer: set[tuple[int, int]] = set()
    start = first_vertex
    for length in lengths:
        vertices = list(range(start, start + length))
        assert length >= 3
        for index, u in enumerate(vertices):
            answer.add(pair(u, vertices[(index + 1) % length]))
        start += length
    assert start == N_ORBITS
    return frozenset(answer)


def expand_and_check(
    t_value: int,
    phase_values: dict[tuple[int, int, int], int],
) -> dict[str, object]:
    adjacency = [set() for _ in range(N)]

    def selected(i: int, a: int, j: int, b: int) -> bool:
        if i == j:
            return i < t_value and a != b
        if i < j:
            return bool(phase_values[i, j, (b - a) % PHASES])
        return bool(phase_values[j, i, (a - b) % PHASES])

    for u, v in itertools.combinations(range(N), 2):
        i, a = divmod(u, PHASES)
        j, b = divmod(v, PHASES)
        if selected(i, a, j, b):
            adjacency[u].add(v)
            adjacency[v].add(u)

    degrees = [len(row) for row in adjacency]
    bad: list[tuple[int, int, bool, int, int]] = []
    histogram: dict[str, int] = {}
    energy = 0
    for u, v in itertools.combinations(range(N), 2):
        adjacent = v in adjacency[u]
        common = len(adjacency[u].intersection(adjacency[v]))
        target = 1 if adjacent else 2
        residual = common - target
        histogram[str(residual)] = histogram.get(str(residual), 0) + 1
        energy += residual * residual
        if residual:
            bad.append((u, v, adjacent, common, target))

    edges = [
        (u + 1, v + 1)
        for u, v in itertools.combinations(range(N), 2)
        if v in adjacency[u]
    ]
    assert len(edges) == len(set(edges))
    return {
        "vertices": N,
        "edges_count": len(edges),
        "degree_min": min(degrees),
        "degree_max": max(degrees),
        "energy": energy,
        "bad_pairs": len(bad),
        "residual_histogram": histogram,
        "bad_examples": bad[:20],
        "edges": edges,
    }


def solve(
    t_value: int,
    seconds: float,
    workers: int,
    t27_shape: str,
    log: bool,
    random_seed: int,
) -> dict[str, object]:
    assert t_value in T_VALUES
    if t_value == 6 and t27_shape != "all":
        raise ValueError("--t27-shape applies only to t=27")

    model = cp_model.CpModel()
    orbit_pairs = list(itertools.combinations(range(N_ORBITS), 2))

    # z[i,j,d] selects the invariant matching (i,a)--(j,a+d).
    phase = {
        (i, j, d): model.new_bool_var("")
        for i, j in orbit_pairs
        for d in range(PHASES)
    }
    support = {p: model.new_bool_var("") for p in orbit_pairs}
    double: dict[tuple[int, int], cp_model.IntVar | int] = {}
    multiplicity: dict[tuple[int, int], cp_model.IntVar] = {}
    for i, j in orbit_pairs:
        if i >= t_value and j >= t_value:
            double[i, j] = model.new_bool_var("")
            model.add(double[i, j] <= support[i, j])
        else:
            double[i, j] = 0
        multiplicity[i, j] = model.new_int_var(0, 2, "")
        model.add(
            multiplicity[i, j]
            == sum(phase[i, j, d] for d in range(PHASES))
        )
        model.add(multiplicity[i, j] == support[i, j] + double[i, j])

    def x(i: int, j: int):
        return support[pair(i, j)]

    def y(i: int, j: int):
        return double[pair(i, j)]

    def m(i: int, j: int):
        return multiplicity[pair(i, j)]

    def edge(i: int, a: int, j: int, b: int):
        if i == j:
            return int(i < t_value and a != b)
        if i < j:
            return phase[i, j, (b - a) % PHASES]
        return phase[j, i, (a - b) % PHASES]

    # Quotient support and double-edge degrees.  These imply vertex degree 14:
    # triangle rows have internal degree 2 plus 12 single matchings; independent
    # rows have 12 support neighbours, two of them doubled.
    for i in range(N_ORBITS):
        model.add(sum(x(i, j) for j in range(N_ORBITS) if j != i) == 12)
        if i >= t_value:
            model.add(
                sum(y(i, j) for j in range(t_value, N_ORBITS) if j != i) == 2
            )

    # Safe complete canonicalization of the multiplicity-two 2-factor.
    independent_count = N_ORBITS - t_value
    shapes = list(partitions_at_least_three(independent_count))
    if t_value == 27:
        requested = {
            "all": {(6,), (3, 3)},
            "c6": {(6,)},
            "2c3": {(3, 3)},
        }[t27_shape]
        shapes = [shape for shape in shapes if shape in requested]
    assert shapes
    shape_edges = {
        shape: canonical_cycle_edges(t_value, shape) for shape in shapes
    }
    if len(shapes) == 1:
        selected_shape: dict[tuple[int, ...], cp_model.IntVar | int] = {shapes[0]: 1}
    else:
        selected_shape = {shape: model.new_bool_var("") for shape in shapes}
        model.add_exactly_one(selected_shape.values())
    for i, j in itertools.combinations(range(t_value, N_ORBITS), 2):
        containing = [selected_shape[s] for s in shapes if (i, j) in shape_edges[s]]
        # Every canonical 2-factor has exactly independent_count edges.  Some
        # labelled pairs occur in no canonical shape and are fixed to zero.
        model.add(y(i, j) == sum(containing))

    # Quotient off-diagonal entries of M^2+M=12I+6J.  Diagonal entries follow
    # already: sum m_ik^2 is 12 for triangle rows and 18 for independent rows.
    quotient_products = 0
    quotient_product: dict[tuple[int, int, int], cp_model.IntVar] = {}
    for i, j in orbit_pairs:
        terms = []
        for k in range(N_ORBITS):
            if k == i or k == j:
                continue
            product = model.new_int_var(0, 4, "")
            model.add_multiplication_equality(product, [m(i, k), m(k, j)])
            quotient_product[i, j, k] = product
            terms.append(product)
            quotient_products += 1
        diagonal_i = 2 if i < t_value else 0
        diagonal_j = 2 if j < t_value else 0
        model.add(
            sum(terms) + (diagonal_i + diagonal_j + 1) * m(i, j) == 6
        )

    # Orbit 0 is a triangle.  Every inter-orbit multiplicity incident with it
    # is at most one.  Independently rotate each other orbit to put any selected
    # matching at phase zero.  This gauge fixing does not constrain support.
    for j in range(1, N_ORBITS):
        model.add(phase[0, j, 1] == 0)
        model.add(phase[0, j, 2] == 0)

    # K3 orbit labels 1,...,t-1 remain freely permutable after fixing orbit 0.
    # Sorting its support incidences is therefore safe.  Independent labels are
    # deliberately not sorted because they have been used for the 2-factor.
    for j in range(1, t_value - 1):
        model.add(x(0, j) >= x(0, j + 1))

    # Phase-level constraints.  An implication-only helper lower-bounds each
    # conjunction.  The bound common(u,v)+adjacent(u,v)<=2 is sufficient: the
    # degree-14 global double count forces equality for every pair.
    phase_products = 0
    reused_literals = 0
    constant_common_terms = 0
    cross_product_groups: dict[tuple[int, int, int], list[cp_model.IntVar]] = {}
    internal_product_groups: dict[tuple[int, int], list[cp_model.IntVar]] = {}

    representatives: list[tuple[int, int, int, int]] = []
    for i in range(N_ORBITS):
        representatives.append((i, 0, i, 1))
    for i, j in orbit_pairs:
        for b in range(PHASES):
            representatives.append((i, 0, j, b))
    assert len(representatives) == 1617

    for i, a, j, b in representatives:
        terms = []
        constant = 0
        for k in range(N_ORBITS):
            for c in range(PHASES):
                if (k == i and c == a) or (k == j and c == b):
                    continue
                left = edge(i, a, k, c)
                right = edge(j, b, k, c)
                if (isinstance(left, int) and left == 0) or (
                    isinstance(right, int) and right == 0
                ):
                    continue
                if isinstance(left, int) and isinstance(right, int):
                    assert left == right == 1
                    constant += 1
                    constant_common_terms += 1
                elif isinstance(left, int):
                    assert left == 1
                    terms.append(right)
                    reused_literals += 1
                elif isinstance(right, int):
                    assert right == 1
                    terms.append(left)
                    reused_literals += 1
                elif left is right:
                    terms.append(left)
                    reused_literals += 1
                else:
                    both = model.new_bool_var("")
                    model.add_bool_or([~left, ~right, both])
                    terms.append(both)
                    phase_products += 1
                    if i != j and k != i and k != j:
                        cross_product_groups.setdefault((i, j, k), []).append(both)
                    elif i == j and k != i:
                        internal_product_groups.setdefault((i, k), []).append(both)
        adjacent = edge(i, a, j, b)
        model.add(sum(terms) + constant + adjacent <= 2)

    # Exact convolution links.  For distinct i,j,k, the nine phase products
    # (three relative phases and three possible vertices in orbit k) sum to
    # m_ik*m_kj.  For an internal pair in orbit i, the three products through
    # orbit k sum to one exactly when the i--k multiplicity is two.  Besides
    # being identities, these equations make every implication-only helper an
    # exact AND without two extra clauses per helper.
    assert len(cross_product_groups) == len(quotient_product) == 16368
    for key, terms in cross_product_groups.items():
        assert len(terms) == 9
        model.add(sum(terms) == quotient_product[key])
    assert len(internal_product_groups) == N_ORBITS * (N_ORBITS - 1)
    for (i, k), terms in internal_product_groups.items():
        assert len(terms) == 3
        model.add(sum(terms) == y(i, k))

    build: dict[str, object] = {
        "event": "built",
        "t": t_value,
        "t27_shape": t27_shape,
        "canonical_2factor_shapes": len(shapes),
        "phase_variables": len(phase),
        "support_variables": len(support),
        "double_variables": sum(not isinstance(value, int) for value in double.values()),
        "multiplicity_variables": len(multiplicity),
        "quotient_product_variables": quotient_products,
        "phase_pair_orbits": len(representatives),
        "phase_product_variables": phase_products,
        "cross_convolution_links": len(cross_product_groups),
        "internal_convolution_links": len(internal_product_groups),
        "reused_phase_literals": reused_literals,
        "constant_common_terms": constant_common_terms,
        "proto_variables": len(model.proto.variables),
        "proto_constraints": len(model.proto.constraints),
    }
    print(json.dumps(build), flush=True)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_search_workers = workers
    solver.parameters.log_search_progress = log
    solver.parameters.random_seed = random_seed
    status = solver.solve(model)
    record: dict[str, object] = {
        **build,
        "status": solver.status_name(status),
        "wall_seconds": solver.wall_time,
        "branches": solver.num_branches,
        "conflicts": solver.num_conflicts,
        "response_stats": solver.response_stats(),
    }
    suffix = f"t{t_value}" if t_value == 6 else f"t27_{t27_shape}"
    suffix += "_linked"
    result_path = Path(f"scratch_c3_strengthened_v2_{suffix}_result.json")
    result_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in record.items() if k != "response_stats"}), flush=True)

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        phase_values = {
            key: solver.value(var) for key, var in phase.items()
        }
        checked = expand_and_check(t_value, phase_values)
        assert checked["energy"] == 0
        assert checked["bad_pairs"] == 0
        assert checked["edges_count"] == 693
        assert checked["degree_min"] == checked["degree_max"] == 14

        selected_cycle_shape = next(
            shape
            for shape, selector in selected_shape.items()
            if (isinstance(selector, int) and selector == 1)
            or (not isinstance(selector, int) and solver.value(selector))
        )
        witness = {
            **record,
            "selected_2factor_shape": selected_cycle_shape,
            "verification": checked,
        }
        witness_path = Path(f"scratch_c3_strengthened_v2_{suffix}_witness.json")
        witness_path.write_text(json.dumps(witness, indent=2) + "\n", encoding="utf-8")
        record["verified_witness"] = str(witness_path)
    return record


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--t", type=int, required=True, choices=T_VALUES)
    parser.add_argument(
        "--t27-shape", choices=("all", "c6", "2c3"), default="all"
    )
    parser.add_argument("--seconds", type=float, default=300.0)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--random-seed", type=int, default=1)
    parser.add_argument("--log", action="store_true")
    args = parser.parse_args()
    solve(
        args.t,
        args.seconds,
        args.workers,
        args.t27_shape,
        args.log,
        args.random_seed,
    )


if __name__ == "__main__":
    main()
