"""SAT audit of source-133 regular H/F exception-to-U pair upper.

For each regular mask surviving the exact recurrence/collision CSP, build the
complete 48-vertex induced subproblem consisting of the 24 exceptional and
24 bottom--outside U vertices.  Variables are all 384 exceptional-to-U
edges.  The CNF enforces:

* one neighbour in every disjoint ordinary U fibre for each exceptional
  vertex;
* the exact per-U target degrees represented by t in {-1,0,1};
* one H and one F fibre at each bottom index;
* all 24 exceptional-row recurrence sums; and
* the induced-pair upper bound on all 48 vertices.

SAT models are decoded and independently checked.  Macro 4 remains separate,
because the regular H/F theorem is not valid for it.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import scratch_general_e79_local_audit as local79
from scratch_general_e72_source133_hf_exception_csp import (
    BOTTOM,
    DIRECTION,
    REGULAR_MACROS,
    adjacency_from_mask,
    local_q_and_required_sums,
    support,
)


INPUT = Path("scratch_general_e72_source133_hf_exception_csp.json")
VERTEX_INPUT = Path("scratch_general_e72_source133_pointwise_frontier.json")
OUTPUT = Path("scratch_general_e72_source133_hf_pair_sat.json")
OUTSIDE = (5, 6)
T_VALUES = (-1, 0, 1)
BITS = tuple(itertools.product((0, 1), repeat=2))
SIDES = tuple(
    pair for pair in itertools.combinations(range(4), 2)
    if sum(BITS[pair[0]][axis] != BITS[pair[1]][axis]
           for axis in (0, 1)) == 1
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def atomic_json(path: Path, value) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, separators=(",", ":")) + "\n",
                         encoding="utf-8")
    temporary.replace(path)


def local_label(fibre, bits):
    return tuple(sorted((2 * fibre[0] + bits[0], 2 * fibre[1] + bits[1])))


def normal_pair(left, right):
    return (left, right) if left < right else (right, left)


def exact_k_clauses(literals, bound):
    literals = tuple(literals)
    assert 0 <= bound <= len(literals)
    clauses = []
    # At most bound.
    for subset in itertools.combinations(literals, bound + 1):
        clauses.append([-literal for literal in subset])
    # At least bound.
    for subset in itertools.combinations(literals, len(literals) - bound + 1):
        clauses.append(list(subset))
    return clauses


def gated_exact_k(clauses, selector, literals, bound, selector_positive=True):
    gate = -selector if selector_positive else selector
    clauses.extend([gate, *row] for row in exact_k_clauses(literals, bound))


def build_instance(exceptional_vertices, mask):
    dependency_root = str(Path(".deps").resolve())
    if dependency_root not in sys.path:
        sys.path.insert(0, dependency_root)
    from pysat.card import CardEnc, EncType
    from pysat.formula import IDPool

    pair_positions = tuple(itertools.combinations(range(24), 2))
    _eps, required, failure = local_q_and_required_sums(
        exceptional_vertices, pair_positions, mask
    )
    assert failure is None
    u_supports = tuple(itertools.product(BOTTOM, OUTSIDE))
    u_by_support = {
        fibre: tuple(local_label(fibre, bits) for bits in BITS)
        for fibre in u_supports
    }
    vertices = tuple(exceptional_vertices) + tuple(
        vertex for fibre in u_supports for vertex in u_by_support[fibre]
    )
    assert len(vertices) == len(set(vertices)) == 48
    vertex_index = {vertex: x for x, vertex in enumerate(vertices)}
    exceptional_by_support = defaultdict(list)
    for x, vertex in enumerate(exceptional_vertices):
        exceptional_by_support[support(vertex)].append(x)
    exceptional_by_support = {
        fibre: tuple(row) for fibre, row in exceptional_by_support.items()
    }

    pool = IDPool()
    edge_variables = {}
    for x, vertex in enumerate(exceptional_vertices):
        source_support = support(vertex)
        for target_support, target_vertices in u_by_support.items():
            if set(source_support) & set(target_support):
                continue
            for target in target_vertices:
                y = vertex_index[target]
                edge_variables[normal_pair(x, y)] = pool.id(("e", x, y))
    assert len(edge_variables) == 384
    t_variables = {
        (vertex_index[vertex], value): pool.id(("t", vertex_index[vertex], value))
        for fibre in u_supports for vertex in u_by_support[fibre]
        for value in T_VALUES
    }
    orientation = {bottom: pool.id(("H5", bottom)) for bottom in BOTTOM}
    clauses = []

    # Every exceptional vertex has one neighbour in each disjoint U fibre.
    for x, vertex in enumerate(exceptional_vertices):
        source_support = support(vertex)
        for target_support, target_vertices in u_by_support.items():
            if set(source_support) & set(target_support):
                continue
            clauses.extend(exact_k_clauses(
                (edge_variables[normal_pair(x, vertex_index[target])]
                 for target in target_vertices), 1
            ))

    # t is one-hot at every U vertex.
    for target_support in u_supports:
        for target in u_by_support[target_support]:
            y = vertex_index[target]
            clauses.extend(exact_k_clauses(
                (t_variables[(y, value)] for value in T_VALUES), 1
            ))

    # Target load in each exceptional block is 1 + coefficient*t.
    for target_support in u_supports:
        bottom, _outside = target_support
        plus, minus = DIRECTION[bottom]
        source_fibres = ((0, plus), (1, plus), (0, minus), (1, minus))
        for target in u_by_support[target_support]:
            y = vertex_index[target]
            for source_fibre in source_fibres:
                coefficient = (1 if source_fibre[0] == 0 else -1) * (
                    1 if source_fibre[1] == plus else -1
                )
                literals = [
                    edge_variables[normal_pair(x, y)]
                    for x in exceptional_by_support[source_fibre]
                ]
                for value in T_VALUES:
                    gated_exact_k(
                        clauses,
                        t_variables[(y, value)],
                        literals,
                        1 + coefficient * value,
                    )

    # H/F types, with orientation[bottom] true meaning U_i^5 is H.
    for bottom in BOTTOM:
        selector = orientation[bottom]
        for outside in OUTSIDE:
            is_h_when_selector_true = outside == 5
            zero_literals = [
                t_variables[(vertex_index[vertex], 0)]
                for vertex in u_by_support[(bottom, outside)]
            ]
            minus_literals = [
                t_variables[(vertex_index[vertex], -1)]
                for vertex in u_by_support[(bottom, outside)]
            ]
            plus_literals = [
                t_variables[(vertex_index[vertex], 1)]
                for vertex in u_by_support[(bottom, outside)]
            ]
            # selector orientation: H has counts (1,2,1), F=(2,0,2).
            for literals, h_bound, f_bound in (
                (minus_literals, 1, 2),
                (zero_literals, 2, 0),
                (plus_literals, 1, 2),
            ):
                gated_exact_k(clauses, selector, literals,
                              h_bound if is_h_when_selector_true else f_bound,
                              selector_positive=True)
                gated_exact_k(clauses, selector, literals,
                              f_bound if is_h_when_selector_true else h_bound,
                              selector_positive=False)

    # Exact exceptional recurrence T sums, encoded as forbidden local tables.
    for x, vertex in enumerate(exceptional_vertices):
        own_bottom = support(vertex)[1]
        for bottom in BOTTOM:
            if bottom == own_bottom:
                continue
            wanted = required[(x, bottom)]
            for target5 in u_by_support[(bottom, 5)]:
                y5 = vertex_index[target5]
                edge5 = edge_variables[normal_pair(x, y5)]
                for target6 in u_by_support[(bottom, 6)]:
                    y6 = vertex_index[target6]
                    edge6 = edge_variables[normal_pair(x, y6)]
                    for value5 in T_VALUES:
                        for value6 in T_VALUES:
                            if value5 + value6 == wanted:
                                continue
                            clauses.append([
                                -edge5,
                                -t_variables[(y5, value5)],
                                -edge6,
                                -t_variables[(y6, value6)],
                            ])

    base_clause_count = len(clauses)

    fixed_edges = set()
    for bit, pair in enumerate(pair_positions):
        if (mask >> bit) & 1:
            fixed_edges.add(pair)
    for target_support in u_supports:
        indices = tuple(vertex_index[vertex]
                        for vertex in u_by_support[target_support])
        for left, right in SIDES:
            fixed_edges.add(normal_pair(indices[left], indices[right]))

    def adjacency_literal(left, right):
        pair = normal_pair(left, right)
        if pair in fixed_edges:
            return True
        return edge_variables.get(pair)

    # Monotone exact induced-pair upper on the 48 materialized vertices.
    pair_rows = 0
    conjunctions = 0
    pair_clauses_by_category = defaultdict(list)
    for left, right in itertools.combinations(range(48), 2):
        if left < 24 and right < 24:
            category = (
                "E-E_same_fibre"
                if support(vertices[left]) == support(vertices[right])
                else "E-E_cross_fibre"
            )
        elif left < 24 or right < 24:
            category = (
                "E-U_overlap"
                if set(support(vertices[left])) & set(support(vertices[right]))
                else "E-U_disjoint"
            )
        else:
            left_support, right_support = support(vertices[left]), support(vertices[right])
            category = (
                "U-U_same_fibre"
                if left_support == right_support
                else "U-U_overlap"
                if set(left_support) & set(right_support)
                else "U-U_disjoint"
            )
        row_clauses = []
        target = 2 - len(set(vertices[left]) & set(vertices[right]))
        constant = 0
        literals = []
        direct = adjacency_literal(left, right)
        if direct is True:
            constant += 1
        elif direct is not None:
            literals.append(direct)
        for witness in range(48):
            if witness in (left, right):
                continue
            first = adjacency_literal(left, witness)
            second = adjacency_literal(right, witness)
            if first is None or second is None:
                continue
            if first is True and second is True:
                constant += 1
            elif first is True:
                literals.append(second)
            elif second is True:
                literals.append(first)
            else:
                conjunction = pool.id(("and", left, right, witness))
                row_clauses.extend((
                    [-conjunction, first],
                    [-conjunction, second],
                    [conjunction, -first, -second],
                ))
                conjunctions += 1
                literals.append(conjunction)
        bound = target - constant
        if bound < 0:
            row_clauses.append([])
        elif bound < len(literals):
            row_clauses.extend(CardEnc.atmost(
                lits=literals,
                bound=bound,
                vpool=pool,
                encoding=EncType.seqcounter,
            ).clauses)
        clauses.extend(row_clauses)
        pair_clauses_by_category[category].extend(row_clauses)
        pair_rows += 1
    return {
        "vertices": vertices,
        "edge_variables": edge_variables,
        "t_variables": t_variables,
        "orientation_variables": orientation,
        "clauses": clauses,
        "base_clause_count_before_pair_upper": base_clause_count,
        "pair_clauses_by_category": dict(pair_clauses_by_category),
        "variables": pool.top,
        "pair_rows": pair_rows,
        "conjunctions": conjunctions,
        "fixed_edges": frozenset(fixed_edges),
    }


def verify_model(instance, model):
    positive = {literal for literal in model if literal > 0}
    edges = set(instance["fixed_edges"])
    for pair, variable in instance["edge_variables"].items():
        if variable in positive:
            edges.add(pair)
    labelled_edges = frozenset(
        tuple(sorted((instance["vertices"][left], instance["vertices"][right])))
        for left, right in edges
    )
    assert local79.induced_pair_upper(instance["vertices"], labelled_edges)
    t_values = {}
    for (vertex, value), variable in instance["t_variables"].items():
        if variable in positive:
            assert vertex not in t_values
            t_values[vertex] = value
    assert len(t_values) == 24
    # Exactly three of the four U neighbours of every exceptional vertex
    # have nonzero t, an independently decoded consequence of the CNF.
    adjacency_sets = [set() for _ in instance["vertices"]]
    for left, right in edges:
        adjacency_sets[left].add(right)
        adjacency_sets[right].add(left)
    for x in range(24):
        selected = [y for y in adjacency_sets[x] if y >= 24]
        assert len(selected) == 4
        assert sum(t_values[y] != 0 for y in selected) == 3
    edge_rows = [
        [left, right]
        for (left, right), variable in sorted(instance["edge_variables"].items())
        if variable in positive
    ]
    return {
        "exception_to_U_edges_by_48_vertex_index": edge_rows,
        "t_values_in_U_vertex_order": [t_values[x] for x in range(24, 48)],
    }


def run(limit, conflicts):
    dependency_root = str(Path(".deps").resolve())
    if dependency_root not in sys.path:
        sys.path.insert(0, dependency_root)
    from pysat.solvers import Solver

    started = time.monotonic()
    document = json.loads(INPUT.read_text(encoding="utf-8"))
    vertex_document = json.loads(VERTEX_INPUT.read_text(encoding="utf-8"))
    exceptional_vertices = tuple(tuple(row)
                                 for row in vertex_document["vertex_order"])
    records = [row for row in document["frontier"] if row[3] in REGULAR_MACROS]
    if limit is not None:
        records = records[:limit]
    per_macro = defaultdict(Counter)
    survivors = []
    controls = []
    formula_histogram = Counter()
    for number, record in enumerate(records):
        instance = build_instance(exceptional_vertices, int(record[0], 16))
        formula_histogram[(instance["variables"], len(instance["clauses"]))] += 1
        with Solver(name="cadical195", bootstrap_with=instance["clauses"]) as solver:
            if conflicts:
                solver.conf_budget(conflicts)
                answer = solver.solve_limited(expect_interrupt=True)
            else:
                answer = solver.solve()
            stats = solver.accum_stats()
            model = solver.get_model() if answer is True else None
        macro = record[3]
        per_macro[macro]["input_orbits"] += 1
        per_macro[macro]["input_mass"] += record[1]
        status = "SAT" if answer is True else "UNSAT" if answer is False else "UNKNOWN"
        per_macro[macro][status] += 1
        per_macro[macro][f"{status}_mass"] += record[1]
        witness = verify_model(instance, model) if model is not None else None
        if answer is True:
            survivors.append([*record[:4], witness])
        if len(controls) < 20:
            controls.append({
                "record_number": number,
                "mask_hex": record[0],
                "state_macro_number": macro,
                "status": status,
                "variables": instance["variables"],
                "clauses": len(instance["clauses"]),
                "solver_stats": stats,
            })
    summary = {
        "input_regular_orbits": len(records),
        "input_regular_mass": sum(row[1] for row in records),
        "SAT_orbits": len(survivors),
        "SAT_mass": sum(row[1] for row in survivors),
        "UNSAT_orbits": sum(row["UNSAT"] for row in per_macro.values()),
        "UNSAT_mass": sum(row["UNSAT_mass"] for row in per_macro.values()),
        "UNKNOWN_orbits": sum(row["UNKNOWN"] for row in per_macro.values()),
        "UNKNOWN_mass": sum(row["UNKNOWN_mass"] for row in per_macro.values()),
        "elapsed_seconds": round(time.monotonic() - started, 6),
    }
    complete = limit is None and not conflicts
    if complete:
        assert summary["input_regular_orbits"] == 5_138
        assert summary["input_regular_mass"] == 1_129_056
        assert summary["UNKNOWN_orbits"] == 0
    result = {
        "status": "COMPLETE" if complete else "PROBE_COMPLETE",
        "model": "source133 regular 48-vertex H/F recurrence plus pair upper SAT",
        "inputs": {str(INPUT): sha256(INPUT), str(VERTEX_INPUT): sha256(VERTEX_INPUT)},
        "conflict_budget_per_instance": conflicts or None,
        "summary": summary,
        "per_macro": {
            str(macro): dict(sorted(row.items()))
            for macro, row in sorted(per_macro.items())
        },
        "formula_size_histogram": {
            f"vars={variables},clauses={clauses}": count
            for (variables, clauses), count in sorted(formula_histogram.items())
        },
        "controls": controls,
        "SAT_frontier_record_fields": [
            "mask_hex", "labelled_orbit_size", "Q", "state_macro_number",
            "decoded_48_vertex_witness",
        ],
        "SAT_frontier": survivors,
        "checks": {
            "every_SAT_model_directly_rechecked_for_pair_upper": True,
            "every_SAT_model_has_exactly_three_nonzero_U_neighbours_per_exception": True,
            "macro4_excluded_from_regular_model": True,
        },
        "claim_boundary": (
            "UNSAT excludes the corresponding regular exceptional mask from "
            "the H/F 48-vertex necessary subproblem (solver certificates are "
            "not emitted). SAT is only a partial 48-vertex witness."
        ),
    }
    atomic_json(OUTPUT, result)
    print(json.dumps({"status": result["status"], **summary}, sort_keys=True),
          flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int)
    parser.add_argument("--conflicts", type=int, default=0)
    args = parser.parse_args()
    run(args.limit, args.conflicts)


if __name__ == "__main__":
    main()
