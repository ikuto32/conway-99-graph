"""Independent structural audit for the E0=78 K2,3 local representative 6.

This uses only Python's standard library.  It does not import any generator,
SAT encoding, or verifier from the search scripts.
"""

from __future__ import annotations

from collections import Counter
import itertools
import json
from pathlib import Path


REPS = Path("scratch_general_e78_local_reps.json")
SEED = Path("scratch_root_e78_k23_rep6_layer.json")
OUTPUT = Path("scratch_e78_rep6_encoding_audit_subagent.json")


def canon(u: int, v: int) -> tuple[int, int]:
    assert u != v
    return (u, v) if u < v else (v, u)


def main() -> None:
    labels = tuple(
        pair
        for pair in itertools.combinations(range(14), 2)
        if pair[0] // 2 != pair[1] // 2
    )
    assert len(labels) == 84
    supports = tuple(tuple(sorted((a // 2, b // 2))) for a, b in labels)
    signs = tuple({a // 2: a % 2, b // 2: b % 2} for a, b in labels)
    support_order = tuple(itertools.combinations(range(7), 2))
    fibres = {
        support: tuple(u for u, value in enumerate(supports) if value == support)
        for support in support_order
    }
    assert all(len(fibre) == 4 for fibre in fibres.values())

    source = json.loads(REPS.read_text(encoding="utf-8"))
    records = [row for row in source["records"] if row["support_form"] == "K2,3"]
    assert len(records) == 1
    record = records[0]
    representative = record["representatives"][6]
    assert representative["representative_id"] == 6
    exceptional = frozenset(tuple(row) for row in record["supports_in_fibre_order"])
    ordinary = frozenset(fibres) - exceptional
    assert len(exceptional) == 6 and len(ordinary) == 15
    local_vertices = frozenset(u for support in exceptional for u in fibres[support])
    local_edges = frozenset(
        canon(*pair) for pair in representative["present_edges_outer_indices_zero_based"]
    )
    assert len(local_vertices) == 24 and len(local_edges) == 30

    def fixed_edge(u: int, v: int) -> bool | None:
        """Return None exactly for a disjoint-support edge variable."""
        A, B = supports[u], supports[v]
        if set(A).isdisjoint(B):
            return None
        key = canon(u, v)
        if u in local_vertices and v in local_vertices:
            return key in local_edges
        if A == B:
            return sum(signs[u][g] != signs[v][g] for g in A) == 1
        return False

    outer_pairs = tuple(itertools.combinations(range(84), 2))
    fixed_true = {pair for pair in outer_pairs if fixed_edge(*pair) is True}
    fixed_false = {pair for pair in outer_pairs if fixed_edge(*pair) is False}
    variable_pairs = {pair for pair in outer_pairs if fixed_edge(*pair) is None}
    assert len(fixed_true) == 90
    assert len(fixed_false) == 1716
    assert len(variable_pairs) == 1680
    assert len(fixed_true | fixed_false | variable_pairs) == len(outer_pairs)

    variable_blocks = []
    block_categories = Counter()
    for A, B in itertools.combinations(support_order, 2):
        if not set(A).isdisjoint(B):
            continue
        variable_blocks.append((A, B))
        category = (
            "low_low" if A in exceptional and B in exceptional
            else "ordinary_ordinary" if A in ordinary and B in ordinary
            else "ordinary_low"
        )
        block_categories[category] += 1
    assert len(variable_blocks) == 105
    assert block_categories == {
        "ordinary_ordinary": 51,
        "ordinary_low": 48,
        "low_low": 6,
    }

    raw_seed = json.loads(SEED.read_text(encoding="utf-8"))
    full_edges = frozenset(canon(int(u) - 1, int(v) - 1) for u, v in raw_seed["edges"])
    assert len(full_edges) == 693
    outer_seed = frozenset(
        (u - 15, v - 15) for u, v in full_edges if u >= 15 and v >= 15
    )
    assert len(outer_seed) == 504

    # Independently reconstruct the entire rooted scaffold.
    expected_scaffold = {canon(0, u) for u in range(1, 15)}
    expected_scaffold |= {canon(1 + 2 * g, 2 + 2 * g) for g in range(7)}
    for u, label in enumerate(labels):
        graph_vertex = 15 + u
        expected_scaffold |= {canon(graph_vertex, 1 + symbol) for symbol in label}
    actual_scaffold = {pair for pair in full_edges if pair[0] < 15 or pair[1] < 15}
    assert actual_scaffold == expected_scaffold

    fixed_mismatch = sorted(
        pair for pair in fixed_true if pair not in outer_seed
    ) + sorted(pair for pair in fixed_false if pair in outer_seed)
    assert not fixed_mismatch
    assert outer_seed & (fixed_true | fixed_false) == fixed_true

    # BP equations, independently evaluated on the outer graph.
    bp_bad = []
    bp_targets = Counter()
    for u, label in enumerate(labels):
        own = set(label)
        for symbol in range(14):
            target = 1 if symbol in own or (symbol ^ 1) in own else 2
            value = sum(
                canon(u, v) in outer_seed
                for v, other in enumerate(labels)
                if u != v and symbol in other
            )
            bp_targets[target] += 1
            if value != target:
                bp_bad.append([u, symbol, value, target])
    assert not bp_bad

    # Ordinary block permutation and ordinary/low one-sided permutation rules.
    block_bad = []
    seed_block_totals = {}
    for A, B in variable_blocks:
        rows = [sum(canon(u, v) in outer_seed for v in fibres[B]) for u in fibres[A]]
        cols = [sum(canon(u, v) in outer_seed for u in fibres[A]) for v in fibres[B]]
        seed_block_totals[f"{A}|{B}"] = sum(rows)
        if A in ordinary and B in ordinary:
            if rows != [1] * 4 or cols != [1] * 4:
                block_bad.append([A, B, rows, cols, "ordinary_ordinary"])
        elif A in ordinary or B in ordinary:
            low = B if B in exceptional else A
            low_counts = cols if B == low else rows
            if low_counts != [1] * 4:
                block_bad.append([A, B, rows, cols, "ordinary_low"])
    assert not block_bad

    # Derive exact low--low row counts from support-aggregate BP.  No values
    # from the seed are used to obtain the targets.
    low_row_records = []
    all_singleton = True
    for F in sorted(exceptional):
        disjoint_low = tuple(G for G in sorted(exceptional) if set(F).isdisjoint(G))
        assert len(disjoint_low) == 2
        for u in fibres[F]:
            same_degree = sum(fixed_edge(u, v) is True for v in fibres[F] if v != u)
            overlap_neighbours = tuple(
                v
                for G in exceptional
                if G != F and set(F) & set(G)
                for v in fibres[G]
                if fixed_edge(u, v) is True
            )
            required_total = len(disjoint_low) + same_degree - 2
            possibilities = []
            for values in itertools.product(range(5), repeat=2):
                if sum(values) != required_total:
                    continue
                if all(
                    sum(value for value, G in zip(values, disjoint_low) if group in G)
                    == sum(group in G for G in disjoint_low)
                    - sum(group in supports[v] for v in overlap_neighbours)
                    for group in range(7)
                    if group not in F
                ):
                    possibilities.append(values)
            assert possibilities
            actual = tuple(
                sum(canon(u, v) in outer_seed for v in fibres[G])
                for G in disjoint_low
            )
            assert actual in possibilities
            singleton = len(set(possibilities)) == 1
            all_singleton &= singleton
            low_row_records.append({
                "support": list(F),
                "outer_index_zero_based": u,
                "graph_vertex_one_based": u + 16,
                "same_fibre_degree": same_degree,
                "overlap_neighbour_count": len(overlap_neighbours),
                "disjoint_low_supports": [list(G) for G in disjoint_low],
                "required_total": required_total,
                "possible_block_row_counts": [list(values) for values in possibilities],
                "seed_block_row_counts": list(actual),
            })
    assert all_singleton

    # Singleton zero rows fix seven cells of each 4x4 low--low block to zero
    # (one full row and one full column, with their intersection shared).
    derived_low_low_false = set()
    for row in low_row_records:
        u = row["outer_index_zero_based"]
        for G, wanted in zip(
            map(tuple, row["disjoint_low_supports"]),
            row["possible_block_row_counts"][0],
        ):
            if wanted == 0:
                derived_low_low_false.update(canon(u, v) for v in fibres[G])
    assert len(derived_low_low_false) == 6 * 7
    assert not (derived_low_low_false & outer_seed)

    directed_zero = {}
    for row in low_row_records:
        F = tuple(row["support"])
        u = row["outer_index_zero_based"]
        targets = row["possible_block_row_counts"][0]
        for G, wanted in zip(map(tuple, row["disjoint_low_supports"]), targets):
            if wanted == 0:
                assert (F, G) not in directed_zero
                directed_zero[(F, G)] = u
    low_block_reductions = []
    for A, B in itertools.combinations(sorted(exceptional), 2):
        if not set(A).isdisjoint(B):
            continue
        u, v = directed_zero[(A, B)], directed_zero[(B, A)]
        fixed = {canon(u, q) for q in fibres[B]} | {canon(q, v) for q in fibres[A]}
        assert len(fixed) == 7 and fixed <= derived_low_low_false
        low_block_reductions.append({
            "supports": [list(A), list(B)],
            "zero_outer_indices_zero_based": [u, v],
            "zero_graph_vertices_one_based": [u + 16, v + 16],
            "active_outer_indices_zero_based": [
                [q for q in fibres[A] if q != u],
                [q for q in fibres[B] if q != v],
            ],
        })
    assert len(low_block_reductions) == 6

    def compact_edge(u: int, v: int) -> bool | None:
        key = canon(u, v)
        value = fixed_edge(u, v)
        return False if value is None and key in derived_low_low_false else value

    # All exact same-support equations, and all outer-pair residuals in seed.
    outer_adj = [set() for _ in range(84)]
    for u, v in outer_seed:
        outer_adj[u].add(v)
        outer_adj[v].add(u)
    same_support_bad = []
    pair_target_histogram = Counter()
    outer_residual_histogram = Counter()
    for u, v in outer_pairs:
        target = 2 - len(set(labels[u]) & set(labels[v]))
        value = int(v in outer_adj[u]) + len(outer_adj[u] & outer_adj[v])
        pair_target_histogram[target] += 1
        outer_residual_histogram[value - target] += 1
        if supports[u] == supports[v] and value != target:
            same_support_bad.append([u, v, value, target])
    assert not same_support_bad

    # Independently count the Boolean simplifications used by a compact exact
    # equality encoding.  None of these counts depend on the layer seed.
    products = direct_terms = constant_terms = 0
    residual_target_histogram = Counter()
    expression_length_histogram = Counter()
    duplicate_literal_equations = 0
    immediate_conflicts = 0
    for u, v in outer_pairs:
        fixed = 0
        symbolic = []
        uv = fixed_edge(u, v)
        if uv is True:
            fixed += 1
        elif uv is None:
            symbolic.append(("e",) + canon(u, v))
        for w in range(84):
            if w in (u, v):
                continue
            a, b = fixed_edge(u, w), fixed_edge(v, w)
            if a is False or b is False:
                continue
            if a is True and b is True:
                fixed += 1
                constant_terms += 1
            elif a is True:
                symbolic.append(("e",) + canon(v, w))
                direct_terms += 1
            elif b is True:
                symbolic.append(("e",) + canon(u, w))
                direct_terms += 1
            else:
                symbolic.append(("and", u, v, w))
                products += 1
        target = 2 - len(set(labels[u]) & set(labels[v]))
        residual = target - fixed
        residual_target_histogram[residual] += 1
        expression_length_histogram[len(symbolic)] += 1
        duplicate_literal_equations += int(len(symbolic) != len(set(symbolic)))
        immediate_conflicts += int(residual < 0 or residual > len(symbolic))
    assert products == 65520
    assert direct_terms == 7200
    assert constant_terms == 108
    assert duplicate_literal_equations == 0
    assert immediate_conflicts == 0

    compact_products = compact_direct_terms = compact_constant_terms = 0
    compact_residual_target_histogram = Counter()
    compact_expression_length_histogram = Counter()
    compact_duplicate_literal_equations = 0
    compact_immediate_conflicts = 0
    for u, v in outer_pairs:
        fixed = 0
        symbolic = []
        uv = compact_edge(u, v)
        if uv is True:
            fixed += 1
        elif uv is None:
            symbolic.append(("e",) + canon(u, v))
        for w in range(84):
            if w in (u, v):
                continue
            a, b = compact_edge(u, w), compact_edge(v, w)
            if a is False or b is False:
                continue
            if a is True and b is True:
                fixed += 1
                compact_constant_terms += 1
            elif a is True:
                symbolic.append(("e",) + canon(v, w))
                compact_direct_terms += 1
            elif b is True:
                symbolic.append(("e",) + canon(u, w))
                compact_direct_terms += 1
            else:
                symbolic.append(("and", u, v, w))
                compact_products += 1
        target = 2 - len(set(labels[u]) & set(labels[v]))
        residual = target - fixed
        compact_residual_target_histogram[residual] += 1
        compact_expression_length_histogram[len(symbolic)] += 1
        compact_duplicate_literal_equations += int(len(symbolic) != len(set(symbolic)))
        compact_immediate_conflicts += int(residual < 0 or residual > len(symbolic))
    assert compact_duplicate_literal_equations == 0
    assert compact_immediate_conflicts == 0

    # Independent all-99 verification metrics for the layer seed.
    adjacency = [set() for _ in range(99)]
    for u, v in full_edges:
        adjacency[u].add(v)
        adjacency[v].add(u)
    assert all(len(row) == 14 for row in adjacency)
    full_energy = 0
    full_bad = 0
    full_residual_histogram = Counter()
    for u, v in itertools.combinations(range(99), 2):
        target = 1 if v in adjacency[u] else 2
        residual = len(adjacency[u] & adjacency[v]) - target
        full_residual_histogram[residual] += 1
        full_energy += residual * residual
        full_bad += residual != 0
    assert full_energy == raw_seed["energy"] == 3574
    assert full_bad == raw_seed["bad_pairs"] == 2104

    # Internal-fibre edge total E0 and local edge partition.
    internal_by_support = {
        str(support): sum(pair in outer_seed for pair in itertools.combinations(fibres[support], 2))
        for support in support_order
    }
    assert sum(internal_by_support.values()) == 78
    assert Counter(internal_by_support.values()) == {4: 15, 3: 6}

    low_target_histogram = Counter(
        value
        for row in low_row_records
        for values in row["possible_block_row_counts"]
        for value in values
    )
    low_total_histogram = Counter(row["required_total"] for row in low_row_records)
    low_low_totals = {
        key: value
        for key, value in seed_block_totals.items()
        if all(tuple(int(x) for x in side.strip("()").split(", ")) in exceptional for side in key.split("|"))
    }

    result = {
        "input": str(SEED),
        "local_source": str(REPS),
        "branch": {"compression_orbit": 3, "local_representative": 6},
        "exceptional_supports": [list(row) for row in sorted(exceptional)],
        "representative": {
            "orbit_size": representative["orbit_size"],
            "stabilizer_order": representative["representative_action_stabilizer_order"],
            "present_local_edges": len(local_edges),
            "local_fixed_absent": representative["fixed_absent_nondisjoint_outer_pairs_zero_based"].__len__(),
            "overlap_square_M2": representative["overlap_square_M2"],
        },
        "outer_edge_space": {
            "pairs": len(outer_pairs),
            "fixed_present": len(fixed_true),
            "fixed_absent": len(fixed_false),
            "disjoint_support_variables": len(variable_pairs),
            "variable_blocks": len(variable_blocks),
            "block_categories": dict(block_categories),
            "derived_low_low_fixed_absent": len(derived_low_low_false),
            "remaining_edge_variables_after_safe_elimination": len(variable_pairs) - len(derived_low_low_false),
        },
        "fixed_present_partition": {
            "ordinary_C4_internal": 60,
            "exceptional_P4_internal": 18,
            "exceptional_overlap": 12,
        },
        "redundant_block_rules": {
            "ordinary_ordinary_permutation_blocks": 51,
            "ordinary_low_low_side_exactly_one_rows": 48 * 4,
            "low_low_total_row_constraints": 24,
            "low_low_individual_block_row_constraints": 48,
            "low_low_individual_target_histogram": dict(low_target_histogram),
            "low_low_total_target_histogram": dict(low_total_histogram),
            "seed_low_low_block_totals": low_low_totals,
        },
        "bp": {"constraints": 1176, "target_histogram": dict(bp_targets), "bad": len(bp_bad)},
        "outer_pair_equalities": {
            "constraints": len(outer_pairs),
            "target_histogram": dict(pair_target_histogram),
            "and_helpers": products,
            "direct_terms": direct_terms,
            "fixed_common_terms": constant_terms,
            "residual_target_histogram": dict(residual_target_histogram),
            "expression_length_histogram": dict(expression_length_histogram),
            "duplicate_symbolic_literal_equations": duplicate_literal_equations,
            "immediate_fixed_conflicts": immediate_conflicts,
        },
        "outer_pair_equalities_after_low_low_zero_elimination": {
            "and_helpers": compact_products,
            "direct_terms": compact_direct_terms,
            "fixed_common_terms": compact_constant_terms,
            "residual_target_histogram": dict(compact_residual_target_histogram),
            "expression_length_histogram": dict(compact_expression_length_histogram),
            "duplicate_symbolic_literal_equations": compact_duplicate_literal_equations,
            "immediate_fixed_conflicts": compact_immediate_conflicts,
        },
        "seed_checks": {
            "scaffold_exact": True,
            "edge_count": len(full_edges),
            "outer_edge_count": len(outer_seed),
            "all_degrees_14": True,
            "fixed_structure_exact": True,
            "bp_exact": True,
            "same_support_pair_equations_exact": True,
            "redundant_block_rules_exact": True,
            "full_energy": full_energy,
            "full_bad_pairs": full_bad,
            "full_residual_histogram": dict(full_residual_histogram),
            "outer_pair_residual_histogram": dict(outer_residual_histogram),
            "is_full_srg": full_energy == 0,
        },
        "low_row_targets": low_row_records,
        "low_block_reductions": low_block_reductions,
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in result.items() if key != "low_row_targets"}, indent=2))


if __name__ == "__main__":
    main()
