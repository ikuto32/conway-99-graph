"""Exact category-core probe for the source-133 48-vertex pair bound.

This is deliberately a small diagnostic around the independent SAT model in
``scratch_general_e72_source133_hf_pair_sat.py``.  For one representative of
each regular macro it rebuilds the H/F plus exceptional-row CSP and enables
chosen classes of induced-pair upper bounds.  Exhausting all category subsets
identifies the inclusion-minimal collections which are already inconsistent.

The output is a diagnostic structural reduction, not a proof certificate for
all representatives.
"""

from __future__ import annotations

import itertools
import json
import sys
from collections import defaultdict
from pathlib import Path

import scratch_general_e72_source133_hf_pair_sat as base


INPUT = Path("scratch_general_e72_source133_hf_exception_csp.json")
VERTEX_INPUT = Path("scratch_general_e72_source133_pointwise_frontier.json")
OUTPUT = Path("scratch_theory_e72_k23_pair_category_core.json")

CATEGORIES = (
    "EE_same", "EE_overlap", "EE_disjoint",
    "EU_overlap", "EU_disjoint",
    "UU_same", "UU_overlap", "UU_disjoint",
)


def pair_category(vertices, left, right):
    left_exceptional = left < 24
    right_exceptional = right < 24
    if left_exceptional and right_exceptional:
        prefix = "EE"
    elif left_exceptional or right_exceptional:
        prefix = "EU"
    else:
        prefix = "UU"
    left_support = base.support(vertices[left])
    right_support = base.support(vertices[right])
    if left_support == right_support:
        suffix = "same"
    elif set(left_support) & set(right_support):
        suffix = "overlap"
    else:
        suffix = "disjoint"
    return f"{prefix}_{suffix}"


def build_instance(exceptional_vertices, mask, enabled):
    """Copy of the audited base CNF, with pair categories switchable."""

    dependency_root = str(Path(".deps").resolve())
    if dependency_root not in sys.path:
        sys.path.insert(0, dependency_root)
    from pysat.card import CardEnc, EncType
    from pysat.formula import IDPool

    pair_positions = tuple(itertools.combinations(range(24), 2))
    _eps, required, failure = base.local_q_and_required_sums(
        exceptional_vertices, pair_positions, mask
    )
    assert failure is None
    u_supports = tuple(itertools.product(base.BOTTOM, base.OUTSIDE))
    u_by_support = {
        fibre: tuple(base.local_label(fibre, bits) for bits in base.BITS)
        for fibre in u_supports
    }
    vertices = tuple(exceptional_vertices) + tuple(
        vertex for fibre in u_supports for vertex in u_by_support[fibre]
    )
    vertex_index = {vertex: x for x, vertex in enumerate(vertices)}
    exceptional_by_support = defaultdict(list)
    for x, vertex in enumerate(exceptional_vertices):
        exceptional_by_support[base.support(vertex)].append(x)

    pool = IDPool()
    edge_variables = {}
    for x, vertex in enumerate(exceptional_vertices):
        source_support = base.support(vertex)
        for target_support, targets in u_by_support.items():
            if set(source_support) & set(target_support):
                continue
            for target in targets:
                y = vertex_index[target]
                edge_variables[base.normal_pair(x, y)] = pool.id(("e", x, y))
    t_variables = {
        (vertex_index[vertex], value): pool.id(("t", vertex_index[vertex], value))
        for fibre in u_supports for vertex in u_by_support[fibre]
        for value in base.T_VALUES
    }
    orientation = {bottom: pool.id(("H5", bottom)) for bottom in base.BOTTOM}
    clauses = []

    for x, vertex in enumerate(exceptional_vertices):
        source_support = base.support(vertex)
        for target_support, targets in u_by_support.items():
            if set(source_support) & set(target_support):
                continue
            clauses.extend(base.exact_k_clauses(
                (edge_variables[base.normal_pair(x, vertex_index[target])]
                 for target in targets), 1
            ))

    for target_support in u_supports:
        for target in u_by_support[target_support]:
            y = vertex_index[target]
            clauses.extend(base.exact_k_clauses(
                (t_variables[(y, value)] for value in base.T_VALUES), 1
            ))

    for target_support in u_supports:
        bottom, _outside = target_support
        plus, minus = base.DIRECTION[bottom]
        source_fibres = ((0, plus), (1, plus), (0, minus), (1, minus))
        for target in u_by_support[target_support]:
            y = vertex_index[target]
            for source_fibre in source_fibres:
                coefficient = (1 if source_fibre[0] == 0 else -1) * (
                    1 if source_fibre[1] == plus else -1
                )
                literals = [
                    edge_variables[base.normal_pair(x, y)]
                    for x in exceptional_by_support[source_fibre]
                ]
                for value in base.T_VALUES:
                    base.gated_exact_k(
                        clauses, t_variables[(y, value)], literals,
                        1 + coefficient * value,
                    )

    for bottom in base.BOTTOM:
        selector = orientation[bottom]
        for outside in base.OUTSIDE:
            h_when_true = outside == 5
            rows = (
                ([t_variables[(vertex_index[v], -1)]
                  for v in u_by_support[(bottom, outside)]], 1, 2),
                ([t_variables[(vertex_index[v], 0)]
                  for v in u_by_support[(bottom, outside)]], 2, 0),
                ([t_variables[(vertex_index[v], 1)]
                  for v in u_by_support[(bottom, outside)]], 1, 2),
            )
            for literals, h_bound, f_bound in rows:
                base.gated_exact_k(
                    clauses, selector, literals,
                    h_bound if h_when_true else f_bound,
                    selector_positive=True,
                )
                base.gated_exact_k(
                    clauses, selector, literals,
                    f_bound if h_when_true else h_bound,
                    selector_positive=False,
                )

    for x, vertex in enumerate(exceptional_vertices):
        own_bottom = base.support(vertex)[1]
        for bottom in base.BOTTOM:
            if bottom == own_bottom:
                continue
            wanted = required[(x, bottom)]
            for target5 in u_by_support[(bottom, 5)]:
                y5 = vertex_index[target5]
                edge5 = edge_variables[base.normal_pair(x, y5)]
                for target6 in u_by_support[(bottom, 6)]:
                    y6 = vertex_index[target6]
                    edge6 = edge_variables[base.normal_pair(x, y6)]
                    for value5 in base.T_VALUES:
                        for value6 in base.T_VALUES:
                            if value5 + value6 == wanted:
                                continue
                            clauses.append([
                                -edge5, -t_variables[(y5, value5)],
                                -edge6, -t_variables[(y6, value6)],
                            ])

    fixed_edges = set()
    for bit, pair in enumerate(pair_positions):
        if (mask >> bit) & 1:
            fixed_edges.add(pair)
    for target_support in u_supports:
        indices = tuple(vertex_index[v] for v in u_by_support[target_support])
        for left, right in base.SIDES:
            fixed_edges.add(base.normal_pair(indices[left], indices[right]))

    def adjacency_literal(left, right):
        pair = base.normal_pair(left, right)
        if pair in fixed_edges:
            return True
        return edge_variables.get(pair)

    pair_rows = defaultdict(int)
    for left, right in itertools.combinations(range(48), 2):
        category = pair_category(vertices, left, right)
        if category not in enabled:
            continue
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
                clauses.extend((
                    [-conjunction, first], [-conjunction, second],
                    [conjunction, -first, -second],
                ))
                literals.append(conjunction)
        bound = target - constant
        if bound < 0:
            clauses.append([])
        elif bound < len(literals):
            clauses.extend(CardEnc.atmost(
                lits=literals, bound=bound, vpool=pool,
                encoding=EncType.seqcounter,
            ).clauses)
        pair_rows[category] += 1
    return clauses, pool.top, dict(pair_rows)


def minimal_unsat_sets(exceptional_vertices, mask):
    dependency_root = str(Path(".deps").resolve())
    if dependency_root not in sys.path:
        sys.path.insert(0, dependency_root)
    from pysat.solvers import Solver

    status = {}
    minimal = []
    for size in range(len(CATEGORIES) + 1):
        for enabled_tuple in itertools.combinations(CATEGORIES, size):
            enabled = frozenset(enabled_tuple)
            if any(core <= enabled for core in minimal):
                status[enabled_tuple] = "UNSAT_BY_SUBSET"
                continue
            clauses, variables, pair_rows = build_instance(
                exceptional_vertices, mask, enabled
            )
            with Solver(name="cadical195", bootstrap_with=clauses) as solver:
                answer = solver.solve()
            assert answer is not None
            if answer:
                status[enabled_tuple] = "SAT"
            else:
                status[enabled_tuple] = "UNSAT"
                minimal.append(enabled)
    return [sorted(core) for core in minimal], {
        "+".join(key) if key else "BASE": value
        for key, value in status.items()
    }


def main():
    document = json.loads(INPUT.read_text(encoding="utf-8"))
    exceptional_vertices = tuple(tuple(row) for row in json.loads(
        VERTEX_INPUT.read_text(encoding="utf-8")
    )["vertex_order"])
    representatives = {}
    for record in document["frontier"]:
        if record[3] in base.REGULAR_MACROS and record[3] not in representatives:
            representatives[record[3]] = record
    assert set(representatives) == set(base.REGULAR_MACROS)
    rows = []
    for macro, record in sorted(representatives.items()):
        minimal, statuses = minimal_unsat_sets(
            exceptional_vertices, int(record[0], 16)
        )
        rows.append({
            "macro": macro,
            "mask_hex": record[0],
            "minimal_unsat_category_sets": minimal,
            "subset_status": statuses,
        })
        print(macro, minimal, flush=True)
    result = {
        "status": "EXACT_FOUR_CONTROL_CATEGORY_PROBE_COMPLETE",
        "categories": list(CATEGORIES),
        "rows": rows,
        "claim_boundary": (
            "The four selected controls are exact SAT decisions.  This is a "
            "diagnostic of pair-bound mechanisms, not a census over all masks."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
