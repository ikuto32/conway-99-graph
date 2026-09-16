"""Small independent fixed-local exact-CNF probe for E0=74 Q>=5 reps.

This is deliberately separate from the shared assumption CNF.  It fixes every
non-disjoint local edge as a Boolean constant, leaves all 1,680 disjoint edges
variable, imposes every BP and outer-pair equality, and fully verifies any SAT
return on 99 vertices.  It is only a three-branch crosscheck, not catalog proof.
"""

from __future__ import annotations

import itertools
import json
import time
from pathlib import Path

from scratch_general_exact_sat import coordinates, verify


SOURCE = Path("scratch_general_e74_q5_local_graph_reps.json")
OUTPUT = Path("scratch_e74_independent_q5_fixed_probe.json")
BRANCHES = (0, 94, 187)


def build(branch_index):
    from pysat.card import CardEnc, EncType
    from pysat.formula import IDPool

    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    row = source["support_rows"][0]
    representative = row["representatives"][branch_index]
    labels, label_index, full_variables, _full_edge = coordinates()
    supports = tuple(tuple(symbol // 2 for symbol in label) for label in labels)
    signs = tuple({symbol // 2: symbol % 2 for symbol in label} for label in labels)
    fibres = {
        support: tuple(index for index, value in enumerate(supports) if value == support)
        for support in itertools.combinations(range(7), 2)
    }
    deficits = {
        tuple(item["support"]): item["deficit"]
        for item in row["exceptional_supports"]
    }
    exceptional = frozenset(deficits)
    high = frozenset(set(fibres) - set(exceptional))
    assert len(exceptional) == 6 and sum(deficits.values()) == 10
    local_graph = frozenset(
        tuple(sorted((label_index[tuple(raw_u)], label_index[tuple(raw_v)])))
        for raw_u, raw_v in representative["edges"]
    )
    assert len(local_graph) == 34

    internal = overlap = 0
    internal_by_support = {support: 0 for support in exceptional}
    for u, v in local_graph:
        A, B = supports[u], supports[v]
        assert A in exceptional and B in exceptional
        if A == B:
            internal += 1
            internal_by_support[A] += 1
        else:
            assert set(A) & set(B)
            overlap += 1
    assert internal == 14 and overlap == 20
    assert all(internal_by_support[support] == 4 - deficit
               for support, deficit in deficits.items())

    pool = IDPool(start_from=1)
    edge_variables = {}
    disjoint_blocks = []
    for A, B in itertools.combinations(fibres, 2):
        if not set(A).isdisjoint(B):
            continue
        disjoint_blocks.append((A, B))
        for u in fibres[A]:
            for v in fibres[B]:
                pair = tuple(sorted((u, v)))
                edge_variables[pair] = pool.id(("edge",) + pair)
    assert len(disjoint_blocks) == 105 and len(edge_variables) == 1680

    def edge(u, v):
        if u == v:
            return False
        pair = tuple(sorted((u, v)))
        if pair in edge_variables:
            return edge_variables[pair]
        A, B = supports[u], supports[v]
        if A == B:
            if A in exceptional:
                return pair in local_graph
            return sum(signs[u][group] != signs[v][group] for group in A) == 1
        assert set(A) & set(B)
        return pair in local_graph

    clauses = []

    def exactly_one(literals):
        literals = tuple(literals)
        clauses.append(list(literals))
        clauses.extend([-a, -b] for a, b in itertools.combinations(literals, 2))

    high_high = high_low = low_low = forced_block_rows = 0
    for A, B in disjoint_blocks:
        if A in high and B in high:
            high_high += 1
        elif A in high or B in high:
            high_low += 1
        else:
            low_low += 1
        if A in high:
            for v in fibres[B]:
                exactly_one(edge(u, v) for u in fibres[A])
                forced_block_rows += 1
        if B in high:
            for u in fibres[A]:
                exactly_one(edge(u, v) for v in fibres[B])
                forced_block_rows += 1
    assert (high_high, high_low, low_low) == (51, 48, 6)
    assert forced_block_rows == 8 * 51 + 4 * 48

    cardinality_rows = 0

    def add_exact(expressions, wanted):
        nonlocal cardinality_rows
        fixed = sum(value is True for value in expressions)
        literals = [value for value in expressions if type(value) is int]
        target = wanted - fixed
        cardinality_rows += 1
        if target < 0 or target > len(literals):
            clauses.append([])
        elif not literals:
            if target:
                clauses.append([])
        else:
            clauses.extend(CardEnc.equals(
                literals, target, vpool=pool, encoding=EncType.seqcounter
            ).clauses)

    for u, label in enumerate(labels):
        own = set(label)
        for symbol in range(14):
            add_exact(
                [edge(u, v) for v, other in enumerate(labels)
                 if u != v and symbol in other],
                1 if symbol in own or (symbol ^ 1) in own else 2,
            )

    products = direct_terms = constant_terms = 0
    for u, v in itertools.combinations(range(84), 2):
        expressions = [edge(u, v)]
        for w in range(84):
            if w in (u, v):
                continue
            left, right = edge(u, w), edge(v, w)
            if left is False or right is False:
                continue
            if left is True and right is True:
                expressions.append(True)
                constant_terms += 1
            elif left is True:
                expressions.append(right)
                direct_terms += 1
            elif right is True:
                expressions.append(left)
                direct_terms += 1
            elif left == right:
                expressions.append(left)
                direct_terms += 1
            else:
                helper = pool.id(("and", u, v, w))
                clauses.extend(([-left, -right, helper],
                                [left, -helper], [right, -helper]))
                expressions.append(helper)
                products += 1
        add_exact(expressions, 2 - len(set(labels[u]) & set(labels[v])))
    assert cardinality_rows == 1176 + 3486
    assert products == 65520
    meta = {
        "branch_index": branch_index,
        "orbit_size": representative["orbit_size"],
        "Q": representative["Q"],
        "fixed_local_edges": len(local_graph),
        "fixed_internal_edges": internal,
        "fixed_overlap_edges": overlap,
        "disjoint_edge_variables": len(edge_variables),
        "product_variables": products,
        "direct_product_terms": direct_terms,
        "constant_product_terms": constant_terms,
        "BP_equalities": 1176,
        "outer_pair_equalities": 3486,
        "redundant_support_aggregate_rows": 0,
        "ordinary_C4_block_equalities": forced_block_rows,
        "variables": pool.top,
        "clauses": len(clauses),
    }
    return clauses, edge, full_variables, meta


def main():
    from pysat.solvers import Solver

    records = []
    for branch_index in BRANCHES:
        started = time.monotonic()
        clauses, edge, full_variables, meta = build(branch_index)
        built = time.monotonic()
        with Solver(name="cadical195", bootstrap_with=clauses) as solver:
            solver.conf_budget(200000)
            answer = solver.solve_limited(expect_interrupt=True)
            model = solver.get_model() if answer is True else None
            stats = solver.accum_stats()
        status = "SAT" if answer is True else "UNSAT" if answer is False else "UNKNOWN"
        record = {
            "branch_index": branch_index,
            "status": status,
            "conflict_budget": 200000,
            "build_seconds": round(built - started, 3),
            "solve_seconds": round(time.monotonic() - built, 3),
            "meta": meta,
            "stats": stats,
            "formal_proof_certificate": None,
        }
        if model:
            positive = {literal for literal in model if literal > 0}
            selected = set()
            for pair, identifier in full_variables.items():
                value = edge(*pair)
                if value is True or (type(value) is int and value in positive):
                    selected.add(identifier)
            checked = verify(selected)
            record["verification"] = {
                key: value for key, value in checked.items() if key != "edges"
            }
            if not checked["ok"]:
                record["status"] = "SAT_INVALID"
        records.append(record)
        print(json.dumps({"branch": branch_index, "status": record["status"],
                          "conflicts": stats.get("conflicts")}), flush=True)
    result = {
        "model": "independent three-branch fixed-local exact CNF crosscheck",
        "source": str(SOURCE),
        "branches": list(BRANCHES),
        "status_counts": dict(Counter(record["status"] for record in records)),
        "catalog_exhaustiveness_claim": False,
        "conditional_Q_at_least_5_scope": True,
        "external_n3_premise_reenacted": False,
        "proof_boundary": "solver-terminal statuses; no checked UNSAT certificates",
        "records": records,
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    from collections import Counter
    main()
