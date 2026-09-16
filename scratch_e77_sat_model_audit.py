"""Solver-free structural audit of the independent exact E0=77 models."""

from __future__ import annotations

from collections import Counter
import itertools
import json
from pathlib import Path


REPS = Path("scratch_e77_sat_reps.json")
SAT = Path("scratch_e77_sat_exact_portfolio.json")
CPSAT = Path("scratch_e77_sat_cpsat.json")
OUTPUT = Path("scratch_e77_sat_model_audit.json")


def main():
    reps_source = json.loads(REPS.read_text(encoding="utf-8"))
    source = next(row for row in reps_source["rows"] if row["local_orbit_count"])
    exceptional = frozenset(tuple(raw) for raw in source["supports"])
    supports_all = tuple(itertools.combinations(range(7), 2))
    high = frozenset(set(supports_all) - set(exceptional))
    labels = tuple(
        pair
        for pair in itertools.combinations(range(14), 2)
        if pair[0] // 2 != pair[1] // 2
    )
    label_index = {label: index for index, label in enumerate(labels)}
    supports = tuple(tuple(symbol // 2 for symbol in label) for label in labels)
    signs = tuple({symbol // 2: symbol % 2 for symbol in label} for label in labels)
    fibres = {
        support: tuple(index for index, value in enumerate(supports) if value == support)
        for support in supports_all
    }

    block_types = Counter()
    for A, B in itertools.combinations(supports_all, 2):
        if not set(A).isdisjoint(B):
            continue
        block_types[
            "high_high" if A in high and B in high
            else "high_low" if A in high or B in high
            else "low_low"
        ] += 1
    assert block_types == Counter({"high_high": 46, "high_low": 48, "low_low": 11})

    audited_reps = []
    for representative in source["representatives"]:
        local = frozenset(
            tuple(sorted((label_index[tuple(raw[0])], label_index[tuple(raw[1])])))
            for raw in representative["local_graph_edges"]
        )
        internal = []
        overlap = []
        for u, v in local:
            A, B = supports[u], supports[v]
            if A == B:
                internal.append((u, v))
                assert A in exceptional
                assert sum(signs[u][g] != signs[v][g] for g in A) == 1
            else:
                overlap.append((u, v))
                assert A in exceptional and B in exceptional and set(A) & set(B)
        assert len(internal) == 21 and len(overlap) == 14
        assert all(
            sum(supports[pair[0]] == support for pair in internal)
            == 3
            for support in exceptional
        )

        neighbours = {u: set() for support in exceptional for u in fibres[support]}
        for u, v in local:
            neighbours[u].add(v)
            neighbours[v].add(u)
        # Internal plus exceptional-overlap edges must exactly fill every BP
        # quota belonging to either coordinate of the exceptional vertex.
        for support in exceptional:
            for u in fibres[support]:
                for group in support:
                    for symbol in (2 * group, 2 * group + 1):
                        assert sum(symbol in labels[v] for v in neighbours[u]) == 1

        # Local common-neighbour contributions may never exceed the exact
        # full equality's target.
        low_vertices = tuple(u for support in exceptional for u in fibres[support])
        for u, v in itertools.combinations(low_vertices, 2):
            adjacency = v in neighbours[u]
            common = len(neighbours[u] & neighbours[v])
            assert common + adjacency <= 2 - len(set(labels[u]) & set(labels[v]))

        classification = Counter()
        fixed_true = fixed_false = variable = 0
        for u, v in itertools.combinations(range(84), 2):
            A, B = supports[u], supports[v]
            if set(A).isdisjoint(B):
                classification["variable_disjoint"] += 1
                variable += 1
            else:
                if A == B:
                    chosen = (
                        (u, v) in local
                        if A in exceptional
                        else sum(signs[u][g] != signs[v][g] for g in A) == 1
                    )
                    classification["fixed_same"] += 1
                else:
                    chosen = A in exceptional and B in exceptional and (u, v) in local
                    classification["fixed_overlap"] += 1
                if chosen:
                    fixed_true += 1
                else:
                    fixed_false += 1
        assert variable == 105 * 16 == 1680
        assert fixed_true == 14 * 4 + 21 + 14 == 91
        assert fixed_true + fixed_false + variable == 3486
        audited_reps.append({
            "representative_index": representative["representative_index"],
            "fixed_local_internal_edges": len(internal),
            "fixed_local_overlap_edges": len(overlap),
            "fixed_true_outer_edges": fixed_true,
            "fixed_false_outer_edges": fixed_false,
            "variable_disjoint_outer_edges": variable,
            "local_BP_support_quotas_exact": True,
            "local_pair_upper_bounds_hold": True,
        })

    sat = json.loads(SAT.read_text(encoding="utf-8"))
    cpsat = json.loads(CPSAT.read_text(encoding="utf-8"))
    assert [row["status"] for row in sat["records"]] == ["UNSAT"] * 3
    assert [row["status"] for row in cpsat["records"]] == ["INFEASIBLE"] * 3
    for row in sat["records"]:
        meta = row["meta"]
        assert meta["edge_variables"] == 1680
        assert meta["product_variables"] == 84 * (40 * 39 // 2) == 65520
        assert meta["cardinality_equalities"] == 84 * 14 + 84 * 83 // 2 == 4662
        assert meta["exact_one_rows"] + meta["exact_one_columns"] == 560
        assert (
            meta["high_high_permutation_blocks"],
            meta["high_low_one_sided_blocks"],
            meta["unrestricted_low_low_disjoint_blocks"],
        ) == (46, 48, 11)
    for row in cpsat["records"]:
        meta = row["meta"]
        assert (
            meta["edge_variables"], meta["product_variables"],
            meta["block_equalities"], meta["bp_equalities"], meta["pair_equalities"],
        ) == (1680, 65520, 560, 1176, 3486)

    result = {
        "model": "solver-free structural audit of both exact E0=77 encodings",
        "local_representatives": audited_reps,
        "disjoint_support_block_types": dict(block_types),
        "ordinary_c4_implication": (
            "an outside vertex has at most one neighbour in a C4 fibre by its six "
            "same-fibre pair equations; 40 forced incidences over 40 eligible "
            "disjoint vertices make the appropriate side exactly one"
        ),
        "safe_block_constraints": {
            "high_high": "two exact-one sides (permutation)",
            "high_low": "only the low-vertex side exact-one",
            "low_low": "unrestricted 4x4 block",
        },
        "equation_coverage": {
            "BP_equalities": 1176,
            "outer_pair_equalities": 3486,
            "AND_products": 65520,
            "AND_encoding": "equivalence in both SAT and CP-SAT",
        },
        "solver_crosscheck": {
            "CaDiCaL_statuses": [row["status"] for row in sat["records"]],
            "CP_SAT_statuses": [row["status"] for row in cpsat["records"]],
            "formal_certificate": None,
        },
        "ok": True,
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "SAT": ["UNSAT"] * 3, "CP_SAT": ["INFEASIBLE"] * 3}))


if __name__ == "__main__":
    main()
