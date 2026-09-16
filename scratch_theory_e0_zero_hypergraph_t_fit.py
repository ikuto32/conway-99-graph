"""Fit the transition 2-factor T to the fixed signed D/U control.

This is a bounded optimization experiment on one explicit relaxation point,
not an exhaustive E0=0 search and not an UNSAT proof.  It chooses the 14
exact-label perfect matchings, forbids T triangles, and minimizes the L1
entrywise defect in B^2+B=10I+2J-Q for B=T+D.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import sys

import scratch_theory_e0_zero_hypergraph as base


ROOT = Path(__file__).resolve().parent
CONTROL = ROOT / "scratch_theory_e0_zero_hypergraph_point_control.json"
OUTPUT = ROOT / "scratch_theory_e0_zero_hypergraph_t_fit.json"
EXPECTED_CONTROL_SHA256 = "C669C983B65BDBF8F5445B99D3847DDEF8FC91DEAB990343ECE53AFD214F1CA2"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load_d() -> tuple[tuple[tuple[int, int, int], ...], set[tuple[int, int]]]:
    base.require(sha256(CONTROL) == EXPECTED_CONTROL_SHA256, "D control hash drift")
    raw = json.loads(CONTROL.read_text(encoding="utf-8"))
    base.require(raw["status"] == "SIGNED_POINT_CONTROL_FOUND", "D control status")
    blocks = tuple(
        tuple(sorted(base.POINT_INDEX[tuple(point)] for point in block))
        for block in raw["selected_signed_blocks"]
    )
    base.require(len(blocks) == len(set(blocks)) == 140, "D blocks")
    edges = {
        pair for block in blocks for pair in itertools.combinations(block, 2)
    }
    base.require(len(edges) == 420, "linear D edges")
    return blocks, edges


def t_catalogue() -> tuple[tuple[int, int], ...]:
    edges = tuple(
        pair
        for pair in itertools.combinations(range(84), 2)
        if len(base.exact_symbols(base.POINTS[pair[0]]) & base.exact_symbols(base.POINTS[pair[1]])) == 1
        and base.support(base.POINTS[pair[0]]) != base.support(base.POINTS[pair[1]])
    )
    base.require(len(edges) == 840, "T candidate edge count")
    return edges


def q_value(left: int, right: int) -> int:
    return len(base.exact_symbols(base.POINTS[left]) & base.exact_symbols(base.POINTS[right]))


def direct_metrics(
    blocks: tuple[tuple[int, int, int], ...],
    d_edges: set[tuple[int, int]],
    t_edges: set[tuple[int, int]],
) -> dict[str, object]:
    base.require(len(t_edges) == 84 and not (d_edges & t_edges), "T edge count/disjointness")
    t_degrees = Counter(point for edge in t_edges for point in edge)
    base.require(t_degrees == Counter({point: 2 for point in range(84)}), "T degree")

    for label in itertools.product(range(7), (0, 1)):
        points = [index for index, point in enumerate(base.POINTS) if label in base.exact_symbols(point)]
        base.require(len(points) == 12, "exact-label fibre size")
        degrees = Counter(
            point
            for edge in t_edges
            if label == next(iter(base.exact_symbols(base.POINTS[edge[0]]) & base.exact_symbols(base.POINTS[edge[1]])), None)
            for point in edge
        )
        base.require(degrees == Counter({point: 1 for point in points}), "exact-label perfect matching")

    t_triangles = [
        triple
        for triple in itertools.combinations(range(84), 3)
        if all(tuple(sorted(pair)) in t_edges for pair in itertools.combinations(triple, 2))
    ]
    base.require(not t_triangles, "T triangle")
    b_edges = d_edges | t_edges
    b_degrees = Counter(point for edge in b_edges for point in edge)
    base.require(b_degrees == Counter({point: 12 for point in range(84)}), "B degree")
    adjacency = [set() for _ in range(84)]
    for left, right in b_edges:
        adjacency[left].add(right)
        adjacency[right].add(left)

    relation_rows: dict[str, list[int]] = defaultdict(list)
    signed_residuals = Counter()
    residual_matrix = [[0] * 84 for _ in range(84)]
    abs_sum = 0
    bad_entries = 0
    max_abs = 0
    for left, right in itertools.combinations(range(84), 2):
        pair = (left, right)
        common = len(adjacency[left] & adjacency[right])
        q = q_value(left, right)
        adjacent = int(pair in b_edges)
        residual = common + adjacent - (2 - q)
        if pair in d_edges:
            category = "D_edge"
        elif pair in t_edges:
            category = "T_edge"
        elif base.support(base.POINTS[left]) == base.support(base.POINTS[right]):
            category = "same_fibre_nonedge_Q" + str(q)
        else:
            category = "other_nonedge_Q" + str(q)
        relation_rows[category].append(residual)
        residual_matrix[left][right] = residual
        residual_matrix[right][left] = residual
        signed_residuals[residual] += 1
        abs_sum += abs(residual)
        bad_entries += residual != 0
        max_abs = max(max_abs, abs(residual))
    row_sums = [sum(row) for row in residual_matrix]
    base.require(row_sums == [0] * 84, "residual row sums")
    residual_frobenius_square = sum(value * value for row in residual_matrix for value in row)

    d_adjacency = [set() for _ in range(84)]
    for left, right in d_edges:
        d_adjacency[left].add(right)
        d_adjacency[right].add(left)
    d_edge_surplus = {
        pair: len(d_adjacency[pair[0]] & d_adjacency[pair[1]]) - 1
        for pair in d_edges
    }
    base.require(min(d_edge_surplus.values()) >= 0, "selected block is missing on a D edge")
    fixed_floor = sum(d_edge_surplus.values())
    base.require(fixed_floor == 261, "fixed Berge-triangle L1 floor")

    baseline_values = []
    for left, right in itertools.combinations(range(84), 2):
        dd = len(d_adjacency[left] & d_adjacency[right])
        baseline_values.append(dd + int((left, right) in d_edges) - (2 - q_value(left, right)))
    baseline_positive = sum(max(0, value) for value in baseline_values)
    baseline_sum = sum(baseline_values)
    base.require((baseline_positive, baseline_sum) == (774, -1848), "fixed D monotone baseline")
    monotone_l1_floor = 2 * baseline_positive

    b_triangles = [
        triple
        for triple in itertools.combinations(range(84), 3)
        if all(tuple(sorted(pair)) in b_edges for pair in itertools.combinations(triple, 2))
    ]
    triangle_t_edge_histogram = Counter(
        sum(tuple(sorted(pair)) in t_edges for pair in itertools.combinations(triple, 2))
        for triple in b_triangles
    )
    base.require(triangle_t_edge_histogram.get(3, 0) == 0, "T triangle leaked into B")
    adjacent_residual_sum = sum(
        residual_matrix[left][right] for left, right in b_edges
    )
    trace_B_E = 2 * adjacent_residual_sum
    cubic_excess = 6 * (len(b_triangles) - 140)
    base.require(trace_B_E == cubic_excess, "cubic trace/residual pairing")

    q_adjacency = [
        {right for right in range(84) if right != left and q_value(left, right) == 1}
        for left in range(84)
    ]
    base.require({len(row) for row in q_adjacency} == {22}, "Q degree")
    commutator_square = 0
    residual_commutator_square = 0
    for left in range(84):
        for right in range(84):
            bq = sum(int(right in q_adjacency[middle]) for middle in adjacency[left])
            qb = sum(int(right in adjacency[middle]) for middle in q_adjacency[left])
            commutator = bq - qb
            commutator_square += commutator * commutator
            be = sum(residual_matrix[middle][right] for middle in adjacency[left])
            eb = sum(residual_matrix[left][middle] for middle in adjacency[right])
            residual_commutator = be - eb
            residual_commutator_square += residual_commutator * residual_commutator
            base.require(commutator == residual_commutator, "[B,Q]=[B,E]")

    matching_trace_residuals = {}
    for delta in base.FLIPS:
        seen = set()
        total = 0
        for point_index, point in enumerate(base.POINTS):
            other = base.POINT_INDEX[base.flip(point, delta)]
            pair = tuple(sorted((point_index, other)))
            if pair in seen:
                continue
            seen.add(pair)
            total += 2 * residual_matrix[pair[0]][pair[1]]
        base.require(len(seen) == 42, "matching trace pair count")
        matching_trace_residuals[str(delta)] = total

    trace_cauchy = Fraction(trace_B_E * trace_B_E, 1008)

    return {
        "selected_T_edges": len(t_edges),
        "T_degree_histogram": dict(sorted(Counter(t_degrees.values()).items())),
        "T_triangles": len(t_triangles),
        "B_edges": len(b_edges),
        "B_degree_histogram": dict(sorted(Counter(b_degrees.values()).items())),
        "entrywise_residual": {
            "unordered_entries": 3486,
            "bad_entries": bad_entries,
            "L1": abs_sum,
            "maximum_absolute": max_abs,
            "Frobenius_square": residual_frobenius_square,
            "row_sum_histogram": {"0": 84},
            "signed_histogram": {str(value): count for value, count in sorted(signed_residuals.items())},
            "by_relation": {
                category: {
                    "entries": len(values),
                    "bad": sum(value != 0 for value in values),
                    "L1": sum(abs(value) for value in values),
                    "signed_histogram": {
                        str(value): count for value, count in sorted(Counter(values).items())
                    },
                }
                for category, values in sorted(relation_rows.items())
            },
        },
        "fixed_D_obstruction": {
            "D_edge_surplus_L1_floor": fixed_floor,
            "derivation": (
                "for a selected D edge xy the chosen block already supplies its required one common neighbour; "
                "every Berge triangle outside that block adds one noncancellable common D-neighbour"
            ),
            "outside_Berge_triangles": fixed_floor // 3,
            "fixed_control_dependent": True,
            "monotone_T_zero_baseline": {
                "signed_histogram": {
                    str(value): count for value, count in sorted(Counter(baseline_values).items())
                },
                "sum": baseline_sum,
                "positive_mass": baseline_positive,
                "all_T_terms_are_nonnegative": True,
                "final_residual_sum_for_every_12_regular_B": 0,
                "analytic_unordered_L1_floor": monotone_l1_floor,
            },
        },
        "trace_and_commutator_diagnostics": {
            "B_triangle_count": len(b_triangles),
            "B_triangle_histogram_by_number_of_T_edges": {
                str(value): count for value, count in sorted(triangle_t_edge_histogram.items())
            },
            "trace_B_cubed": 6 * len(b_triangles),
            "target_trace_B_cubed": 840,
            "trace_B_times_residual": trace_B_E,
            "exact_identity": "tr(BE)=tr(B^3)-840=6*(triangles(B)-140)",
            "fixed_D_lower_bound": "tr(BE)>=6*87=522",
            "Frobenius_Cauchy_lower_bound": {
                "formula": "||E||_F^2 >= tr(BE)^2/tr(B^2), with tr(B^2)=1008",
                "value_exact": f"{trace_cauchy.numerator}/{trace_cauchy.denominator}",
            },
            "Q_commutator_Frobenius_square": commutator_square,
            "residual_commutator_Frobenius_square": residual_commutator_square,
            "commutator_identity": "[B,Q]=[B,E]",
            "three_matching_trace_residuals": matching_trace_residuals,
        },
    }


def solve(seconds: float, workers: int, random_seed: int) -> dict[str, object]:
    sys.path.insert(0, str((ROOT / ".ortools").resolve()))
    from ortools.sat.python import cp_model

    blocks, d_edges = load_d()
    t_candidates = t_catalogue()
    t_index = {edge: index for index, edge in enumerate(t_candidates)}
    model = cp_model.CpModel()
    t_vars = [model.NewBoolVar(f"t_{left}_{right}") for left, right in t_candidates]

    by_label_point: dict[tuple[tuple[int, int], int], list[int]] = defaultdict(list)
    incident_by_point_label: dict[tuple[int, tuple[int, int]], list[int]] = defaultdict(list)
    for index, (left, right) in enumerate(t_candidates):
        shared = base.exact_symbols(base.POINTS[left]) & base.exact_symbols(base.POINTS[right])
        base.require(len(shared) == 1, "T shared label")
        label = next(iter(shared))
        by_label_point[(label, left)].append(index)
        by_label_point[(label, right)].append(index)
        incident_by_point_label[(left, label)].append(index)
        incident_by_point_label[(right, label)].append(index)
    for point_index, point in enumerate(base.POINTS):
        for label in base.exact_symbols(point):
            indices = by_label_point[(label, point_index)]
            base.require(len(indices) == 10, "T local candidate degree")
            model.AddExactlyOne(t_vars[index] for index in indices)

    candidate_triangles = []
    for triple in itertools.combinations(range(84), 3):
        pairs = tuple(tuple(sorted(pair)) for pair in itertools.combinations(triple, 2))
        if all(pair in t_index for pair in pairs):
            candidate_triangles.append(pairs)
            model.Add(sum(t_vars[t_index[pair]] for pair in pairs) <= 2)

    # One product variable for the two selected T edges through each potential
    # common neighbour z.  Edges belonging to the same exact-label matching
    # cannot both be selected, so only the 10x10 cross-label products matter.
    tt_by_endpoint_pair: dict[tuple[int, int], list] = defaultdict(list)
    tt_variables = []
    for middle, point in enumerate(base.POINTS):
        labels = tuple(sorted(base.exact_symbols(point)))
        first = incident_by_point_label[(middle, labels[0])]
        second = incident_by_point_label[(middle, labels[1])]
        base.require(len(first) == len(second) == 10, "T product fan")
        for left_index in first:
            left_edge = t_candidates[left_index]
            left = left_edge[0] if left_edge[1] == middle else left_edge[1]
            for right_index in second:
                right_edge = t_candidates[right_index]
                right = right_edge[0] if right_edge[1] == middle else right_edge[1]
                product = model.NewBoolVar(f"tt_{middle}_{left}_{right}")
                model.Add(product <= t_vars[left_index])
                model.Add(product <= t_vars[right_index])
                model.Add(product >= t_vars[left_index] + t_vars[right_index] - 1)
                tt_variables.append(product)
                tt_by_endpoint_pair[tuple(sorted((left, right)))].append(product)

    d_adjacency = [set() for _ in range(84)]
    for left, right in d_edges:
        d_adjacency[left].add(right)
        d_adjacency[right].add(left)

    abs_variables = []
    for left, right in itertools.combinations(range(84), 2):
        pair = (left, right)
        dd = len(d_adjacency[left] & d_adjacency[right])
        mixed = []
        for middle in d_adjacency[left]:
            edge = tuple(sorted((right, middle)))
            if edge in t_index:
                mixed.append(t_vars[t_index[edge]])
        for middle in d_adjacency[right]:
            edge = tuple(sorted((left, middle)))
            if edge in t_index:
                mixed.append(t_vars[t_index[edge]])
        b_edge = 1 if pair in d_edges else (t_vars[t_index[pair]] if pair in t_index else 0)
        target = 2 - q_value(left, right)
        difference = model.NewIntVar(-2, 12, f"res_{left}_{right}")
        model.Add(difference == dd + sum(mixed) + sum(tt_by_endpoint_pair[pair]) + b_edge - target)
        absolute = model.NewIntVar(0, 12, f"abs_{left}_{right}")
        model.AddAbsEquality(absolute, difference)
        abs_variables.append(absolute)

    model.Minimize(sum(abs_variables))
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = seconds
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = random_seed
    solver.parameters.cp_model_presolve = True
    status_code = solver.Solve(model)
    status = solver.StatusName(status_code)
    result: dict[str, object] = {
        "status": "FIXED_D_T_FIT_" + status,
        "sealed_input": {"point_control_sha256": sha256(CONTROL)},
        "model": {
            "T_candidate_edges": len(t_candidates),
            "exact_label_matching_rows": 168,
            "T_triangle_forbidding_rows": len(candidate_triangles),
            "TT_product_variables": len(tt_variables),
            "entrywise_absolute_defect_rows": len(abs_variables),
            "objective": "minimize unordered-entry L1 of B^2+B-(10I+2J-Q)",
        },
        "solver": {
            "status": status,
            "wall_seconds": solver.WallTime(),
            "branches": solver.NumBranches(),
            "conflicts": solver.NumConflicts(),
            "objective": solver.ObjectiveValue() if status_code in (cp_model.FEASIBLE, cp_model.OPTIMAL) else None,
            "best_bound": solver.BestObjectiveBound(),
            "time_limit_seconds": seconds,
            "workers": workers,
            "random_seed": random_seed,
        },
        "claim_boundary": (
            "bounded optimization for one fixed D/U control only; neither a universal lower bound nor an E0=0 exclusion"
        ),
    }
    if status_code in (cp_model.FEASIBLE, cp_model.OPTIMAL):
        selected = {
            edge for edge, variable in zip(t_candidates, t_vars) if solver.Value(variable)
        }
        result["selected_T_edges"] = [list(edge) for edge in sorted(selected)]
        result["direct_verification"] = direct_metrics(blocks, d_edges, selected)
        base.require(
            result["direct_verification"]["entrywise_residual"]["L1"] == round(solver.ObjectiveValue()),
            "solver/direct objective mismatch",
        )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seconds", type=float, default=120.0)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--random-seed", type=int, default=6501)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    result = solve(args.seconds, args.workers, args.random_seed)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("status", "model", "solver")}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
