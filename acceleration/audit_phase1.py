"""Independently derive and evaluate phase-I rows from the full 99-vertex graph.

No optimization package or producer mapping is imported. Exact bounds use the
stored binary floating-point values as rational numbers; numerical objective
agreement alone never establishes infeasibility.
"""
import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
import json
import math
from pathlib import Path
import time

from audit_certificate import full_graph, graph_constraint, require


def graph_rows(candidate):
    adjacency, unknown = full_graph(candidate)
    edges = sorted((u - 15, v - 15) for u, v in unknown)
    index = {(u + 15, v + 15): i for i, (u, v) in enumerate(edges)}
    groups = []
    coordinates = [("label_quota", [u, s]) for u in range(84) for s in range(14)]
    coordinates += [("linear_pair_cap", list(pair)) for pair in combinations(range(84), 2)]
    omitted = []
    for kind, coordinate in coordinates:
        terms, rhs = graph_constraint(adjacency, unknown, kind, coordinate)
        row = dict(kind=kind, coordinate=coordinate,
                   terms=sorted(index[pair] for pair, count in terms.items() for _ in range(count)),
                   target=rhs, equality=kind == "label_quota")
        if row["equality"] and not row["terms"]:
            require(rhs == 0, "Nontrivial omitted quota")
            omitted.append(row)
        else:
            groups.append(row)
    require(len(edges) == 1680 and len(groups) == 4326, "Unexpected phase-I dimensions")
    return edges, groups, omitted


def finite_vector(values, size, name):
    require(type(values) is list and len(values) == size, f"Invalid {name} length")
    require(all(type(x) in (int, float) and math.isfinite(x) for x in values), f"Nonfinite {name}")
    return values


def evaluate(candidate, x, exact=False):
    """Return 840 quota and 3486 lexicographic outer-pair residuals."""
    edges, groups, omitted = graph_rows(candidate)
    finite_vector(x, len(edges), "X")
    require(all(0 <= value <= 1 for value in x), "X outside [0,1]")
    values = list(map(Fraction, x)) if exact else x
    residuals = [sum((values[e] for e in row["terms"]), 0) - row["target"] for row in groups]
    quota = sum(map(abs, residuals[:840]))
    pair = sum(max(0, value) for value in residuals[840:])
    return dict(total_violation=quota + pair, quota_violation=quota, pair_violation=pair,
                quota_residuals=residuals[:840], pair_residuals=residuals[840:])


def exact_bounds(groups, x, y):
    """Exact rational upper bound and clipped-dual lower bound, same fixed K."""
    qx = list(map(Fraction, x))
    qy = [min(Fraction(1), max(Fraction(-1 if row["equality"] else 0), Fraction(value)))
          for row, value in zip(groups, y)]
    residuals = [sum((qx[e] for e in row["terms"]), Fraction(0)) - row["target"] for row in groups]
    upper = sum(abs(r) if row["equality"] else max(0, r) for row, r in zip(groups, residuals))
    combined = [Fraction(0)] * len(x)
    rhs = Fraction(0)
    for row, weight in zip(groups, qy):
        rhs += row["target"] * weight
        for e in row["terms"]:
            combined[e] += weight
    lower = -rhs + sum(min(0, value) for value in combined)
    require(lower <= upper, "Exact weak duality violated")
    return upper, lower, qy, combined


def rational(value):
    return dict(numerator=str(value.numerator), denominator=str(value.denominator), approximate=float(value))


def exact_integer_certificate(candidate, result, candidate_sha256):
    """Clear stored binary dual denominators; no numerical reconstruction."""
    edges, groups, _ = graph_rows(candidate)
    compare_rows(result["constraint_groups"], groups)
    weighted = {(row["kind"], tuple(row["coordinate"])): weight
                for row, weight in zip(result["constraint_groups"], result["phase1_multipliers"])}
    y = [weighted.get((row["kind"], tuple(row["coordinate"])), 0) for row in groups]
    _, lower, qy, co = exact_bounds(groups, [min(1, max(0, x)) for x in result["numeric_edge_values"]], y)
    require(lower > 0, "No positive exact dual bound")
    scale = math.lcm(*(weight.denominator for weight in qy))
    weights = [int(weight * scale) for weight in qy]
    bounds = [int(max(0, -value) * scale) for value in co]
    divisor = math.gcd(*(abs(value) for value in weights + bounds))
    rhs = sum(row["target"] * weight for row, weight in zip(groups, weights)) + sum(bounds)
    require(rhs < 0 and Fraction(-rhs, scale) == lower, "Exact integer conversion failed")
    return dict(status="EXACT_INTEGER_WEIGHTED_CAPACITY_CONTRADICTION",
                candidate_sha256=candidate_sha256, disjoint_block_totals_assumed=False,
                combined_rhs=rhs // divisor,
                group_multipliers=[dict(kind=row["kind"], coordinate=row["coordinate"], multiplier=weight // divisor)
                                   for row, weight in zip(groups, weights) if weight],
                edge_upper_bound_multipliers=[dict(edge=list(edge), multiplier=weight // divisor)
                                              for edge, weight in zip(edges, bounds) if weight],
                provenance="Exact rational interpretation of clipped stored phase-I binary dual weights; no rounding.",
                denominator_lcm=str(scale), integer_common_divisor=str(divisor))


def compare_rows(actual, expected):
    """Metadata row order may omit only zero-term pair tautologies."""
    expected_by_key = {(row["kind"], tuple(row["coordinate"])): row for row in expected}
    seen = set()
    for row in actual:
        key = row["kind"], tuple(row["coordinate"])
        require(key in expected_by_key and key not in seen, "Missing or duplicate phase-I row")
        seen.add(key)
        truth = expected_by_key[key]
        require(Counter(row["terms"]) == Counter(truth["terms"]), f"Row term mismatch {key}")
        require(row["target"] == truth["target"] and row["equality"] == truth["equality"],
                f"Row RHS/kind mismatch {key}")
    for key, row in expected_by_key.items():
        if key not in seen:
            require(not row["equality"] and not row["terms"] and row["target"] >= 0,
                    f"Nontrivial omitted row {key}")
    return expected_by_key


def inspect_artifact(candidate_path, result_path, tolerance=1e-7):
    started = time.perf_counter()
    candidate_bytes, result_bytes = candidate_path.read_bytes(), result_path.read_bytes()
    candidate, result = json.loads(candidate_bytes), json.loads(result_bytes)
    require(result["candidate_sha256"] == sha256(candidate_bytes).hexdigest(), "Candidate SHA mismatch")
    edges, groups, omitted = graph_rows(candidate)
    actual_rows = result["constraint_groups"]
    compare_rows(actual_rows, groups)
    require(result["edge_variables"] == [list(edge) for edge in edges], "X variable order mismatch")
    require(result.get("disjoint_block_totals_assumed", False) is False, "Unsupported compression totals")
    for name, digest in result.get("source_sha256", {}).items():
        require(Path(name).name == name, "Unexpected producer source path")
        require(sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() == digest,
                f"Producer source hash mismatch: {name}")
    x = finite_vector(result["numeric_edge_values"], len(edges), "X")
    require(all(-tolerance <= value <= 1 + tolerance for value in x), "Numerically invalid X box")
    # Clipping gives an exactly box-feasible point even when solver roundoff is present.
    clipped_x = [min(1, max(0, value)) for value in x]
    evaluation = evaluate(candidate, clipped_x)
    numerical_objective = result["numeric_objective"]
    require(type(numerical_objective) in (int, float) and math.isfinite(numerical_objective), "Invalid objective")
    objective_difference = abs(evaluation["total_violation"] - numerical_objective)
    require(objective_difference <= tolerance * max(1, abs(numerical_objective)), "Objective mismatch")
    actual_y = finite_vector(result["phase1_multipliers"], len(actual_rows), "dual weights")
    marginals = finite_vector(result["row_duals"], len(actual_rows), "row marginals")
    require(all(y == -marginal for y, marginal in zip(actual_y, marginals)), "Row marginal sign mismatch")
    declared_residuals = finite_vector(result["row_residuals"], len(actual_rows), "row residuals")
    independent_residuals = [sum(clipped_x[e] for e in row["terms"]) - row["target"] for row in actual_rows]
    require(all(abs(a-b) <= tolerance for a, b in zip(declared_residuals, independent_residuals)),
            "Declared residual mismatch")
    for key in ("numeric_solver_objective", "numeric_slack_objective"):
        require(type(result[key]) in (int, float) and math.isfinite(result[key]), f"Invalid {key}")
        require(abs(result[key]-numerical_objective) <= tolerance * max(1, abs(numerical_objective)),
                f"{key} disagrees with residual merit")
    y_by_key = {(row["kind"], tuple(row["coordinate"])): weight for row, weight in zip(actual_rows, actual_y)}
    y = [y_by_key.get((row["kind"], tuple(row["coordinate"])), 0) for row in groups]
    dual_box_violation = max(max((-1 if row["equality"] else 0) - value, value - 1, 0)
                             for row, value in zip(groups, y))
    require(dual_box_violation <= tolerance, "Dual weight violates phase-I interval")
    upper, lower, clipped_y, combined = exact_bounds(groups, clipped_x, y)
    gap = upper - lower
    require(float(gap) <= tolerance * max(1, abs(float(upper))), "Phase-I primal-dual gap too large")
    for key, truth in (("numerical_dual_lower_bound", float(lower)),
                       ("numerical_primal_dual_gap", float(gap))):
        require(type(result[key]) in (int, float) and math.isfinite(result[key]), f"Invalid {key}")
        require(abs(result[key] - truth) <= tolerance * max(1, abs(float(upper))),
                f"Declared {key} mismatch")
    # Complementarity/subgradient conditions are checked separately to detect sign errors.
    residuals = evaluation["quota_residuals"] + evaluation["pair_residuals"]
    subgradient_error = 0.0
    for row, residual, weight in zip(groups, residuals, clipped_y):
        if residual > tolerance:
            subgradient_error = max(subgradient_error, abs(1 - float(weight)))
        elif residual < -tolerance:
            subgradient_error = max(subgradient_error, abs((-1 if row["equality"] else 0) - float(weight)))
    stationarity_error = max(max(float(c), 0) if value > tolerance else 0 for value, c in zip(clipped_x, combined))
    stationarity_error = max(stationarity_error,
                             max(max(-float(c), 0) if value < 1 - tolerance else 0 for value, c in zip(clipped_x, combined)))
    require(subgradient_error <= tolerance and stationarity_error <= tolerance, "KKT residual failed")
    report = dict(status="INDEPENDENT_PHASE1_GRAPH_MODEL_PRIMAL_DUAL_AUDIT_PASS",
                  inputs_sha256={str(candidate_path): sha256(candidate_bytes).hexdigest(),
                                 str(result_path): sha256(result_bytes).hexdigest()},
                  auditor_sha256=sha256(Path(__file__).read_bytes()).hexdigest(),
                  graph_auditor_sha256=sha256(Path(__file__).with_name("audit_certificate.py").read_bytes()).hexdigest(),
                  all_graph_rows_checked=4662, quota_rows=840, pair_rows=3486,
                  zero_quota_rows_omitted=len(omitted), producer_rows=len(actual_rows),
                  evaluation={key: value for key, value in evaluation.items() if not key.endswith("residuals")},
                  numerical_objective_difference=objective_difference, numerical_tolerance=tolerance,
                  dual_interval_violation=dual_box_violation, subgradient_error=subgradient_error,
                  box_stationarity_error=stationarity_error,
                  exact_primal_upper_bound=rational(upper), exact_dual_lower_bound=rational(lower),
                  exact_primal_dual_gap=rational(gap), exact_positive_dual_bound=lower > 0,
                  x_values_clipped=sum(a != b for a, b in zip(x, clipped_x)),
                  dual_weights_clipped=sum(Fraction(a) != b for a, b in zip(y, clipped_y)),
                  solver_or_producer_imported=False, elapsed_seconds=time.perf_counter()-started,
                  scope="Only this fixed overlap assignment. Numeric merit supplies no exclusion; a positive exact rational dual bound proves its necessary continuous system infeasible.")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--phase1", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--tolerance", type=float, default=1e-7)
    args = parser.parse_args()
    require(not args.out.exists(), "Use a fresh audit output")
    require(math.isfinite(args.tolerance) and args.tolerance > 0, "Invalid audit tolerance")
    report = inspect_artifact(args.candidate, args.phase1, args.tolerance)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8") as output:
        output.write(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
