"""Cheap source-blind transport/projector filters on the frozen E71 frontier.

No overlap completion or local graph is generated.  For every full-Gram
profile retained by the existing kernel-port census, only the integral
single-vertex fibre-degree rows are reconstructed.  Necessary leverage and
pointwise-transport support bounds are then propagated to a fixed point.
"""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
import hashlib
import itertools
import json
import math
import os
from pathlib import Path

import scratch_theory_e71_defect_rank_probe as defect
import scratch_theory_e71_equitable_kernel_port_census as kernel


CATALOG = Path("scratch_root_e71_q2_gram_fast_expansion_macro_catalog.json")
MINING = Path("scratch_theory_e71_e72_e0_moment_mining.json")
KERNEL = Path("scratch_theory_e71_equitable_kernel_port_census.json")
SOURCE724 = Path("scratch_theory_e71_source724_multiblock_transport_audit.json")
OUTPUT = Path("scratch_theory_e71_projector_transport_frontier.json")
SUPPORTS = tuple(itertools.combinations(range(7), 2))


def atomic_json(path, value):
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def matmul(left, right):
    columns = list(zip(*right))
    return [[sum(a * b for a, b in zip(row, column)) for column in columns]
            for row in left]


def determinant(matrix):
    matrix = [[Fraction(value) for value in row] for row in matrix]
    answer = Fraction(1)
    for column in range(len(matrix)):
        pivot = next((row for row in range(column, len(matrix))
                      if matrix[row][column]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            matrix[column], matrix[pivot] = matrix[pivot], matrix[column]
            answer = -answer
        scale = matrix[column][column]
        answer *= scale
        matrix[column] = [value / scale for value in matrix[column]]
        for row in range(column + 1, len(matrix)):
            if matrix[row][column]:
                factor = matrix[row][column]
                matrix[row] = [a - factor * b
                               for a, b in zip(matrix[row], matrix[column])]
    return answer


def solve(matrix, target):
    size = len(matrix)
    a = [[Fraction(value) for value in matrix[row]] + [Fraction(target[row])]
         for row in range(size)]
    for column in range(size):
        pivot = next(row for row in range(column, size) if a[row][column])
        a[column], a[pivot] = a[pivot], a[column]
        scale = a[column][column]
        a[column] = [value / scale for value in a[column]]
        for row in range(size):
            if row != column and a[row][column]:
                factor = a[row][column]
                a[row] = [x - factor * y for x, y in zip(a[row], a[column])]
    return tuple(row[-1] for row in a)


def pseudoinverse_form(matrix):
    rank = defect.rank(matrix)
    work = [[Fraction(value) for value in row] for row in matrix]
    pivot_columns = []
    pivot_row = 0
    for column in range(len(matrix)):
        chosen = next((row for row in range(pivot_row, len(matrix))
                       if work[row][column]), None)
        if chosen is None:
            continue
        work[pivot_row], work[chosen] = work[chosen], work[pivot_row]
        scale = work[pivot_row][column]
        work[pivot_row] = [value / scale for value in work[pivot_row]]
        for row in range(pivot_row + 1, len(matrix)):
            if work[row][column]:
                factor = work[row][column]
                work[row] = [a - factor * b
                             for a, b in zip(work[row], work[pivot_row])]
        pivot_columns.append(column)
        pivot_row += 1
        if pivot_row == rank:
            break
    assert len(pivot_columns) == rank
    # For a symmetric PSD matrix, any maximal independent column set indexes
    # a positive definite principal submatrix.
    pivot = tuple(pivot_columns)
    minor = [[matrix[i][j] for j in pivot] for i in pivot]
    assert determinant(minor)

    def coordinates(vector):
        return solve(minor, [vector[i] for i in pivot])

    def form(left, right=None):
        if right is None:
            right = left
        solution = coordinates(right)
        return sum(Fraction(left[i]) * solution[position]
                   for position, i in enumerate(pivot))

    return pivot, form, coordinates


def coarse_cycle_projector():
    incidence = [[int(vertex in support) for support in SUPPORTS]
                 for vertex in range(7)]
    inverse = [[Fraction(int(i == j), 5) - Fraction(1, 60)
                for j in range(7)] for i in range(7)]
    return [[
        Fraction(int(i == j)) - sum(
            Fraction(incidence[a][i]) * inverse[a][b]
            * Fraction(incidence[b][j])
            for a in range(7) for b in range(7)
        )
        for j in range(21)
    ] for i in range(21)]


COARSE_CYCLE = coarse_cycle_projector()


def primitive_directions(dimension):
    answer = set()
    for values in itertools.product((-1, 0, 1), repeat=dimension):
        if not any(values):
            continue
        first = next(value for value in values if value)
        if first < 0:
            values = tuple(-value for value in values)
        divisor = 0
        for value in values:
            divisor = math.gcd(divisor, abs(value))
        answer.add(tuple(value // divisor for value in values))
    return tuple(sorted(answer))


def fast_general_row_patterns(C, K4, exceptional):
    """The frozen row(K4) definition, with one inverse per profile."""
    exceptional_global = [SUPPORTS.index(support) for support in exceptional]
    KE = [[K4[left][right] for right in exceptional_global]
          for left in exceptional_global]
    dimension = defect.rank(KE)
    assert dimension == defect.rank(K4)
    basis = defect.independent_rows(KE, dimension)
    pivots = next(
        columns for columns in itertools.combinations(range(len(exceptional)), dimension)
        if defect.rank([[basis[row][column] for column in columns]
                        for row in range(dimension)]) == dimension
    )
    pivot_transpose = [[basis[row][column] for row in range(dimension)]
                       for column in pivots]
    inverse_columns = [
        solve(pivot_transpose, [int(i == column) for i in range(dimension)])
        for column in range(dimension)
    ]
    ordinary_global = [index for index in range(21)
                       if index not in exceptional_global]
    by_source = []
    for source, support in enumerate(SUPPORTS):
        baseline = [C[source][target] for target in exceptional_global]
        allowed = [tuple(4 * degree - baseline[column] for degree in range(5))
                   for column in pivots]
        patterns = []
        for pivot_values in itertools.product(*allowed):
            coefficients = [
                sum(Fraction(pivot_values[column]) * inverse_columns[column][row]
                    for column in range(dimension))
                for row in range(dimension)
            ]
            residual_fraction = [
                sum(coefficients[row] * basis[row][column]
                    for row in range(dimension))
                for column in range(len(exceptional))
            ]
            if any(value.denominator != 1 for value in residual_fraction):
                continue
            residual = tuple(map(int, residual_fraction))
            degrees = []
            for value, total in zip(residual, baseline):
                numerator = value + total
                if numerator % 4 or not 0 <= numerator // 4 <= 4:
                    break
                degrees.append(numerator // 4)
            else:
                ordinary_degrees = [C[source][target] // 4
                                    for target in ordinary_global]
                assert all(C[source][target] % 4 == 0 for target in ordinary_global)
                if sum(degrees) + sum(ordinary_degrees) == 12:
                    patterns.append({
                        "exceptional_degrees": degrees,
                        "scaled_W_row_on_exceptional": list(residual),
                        "pivot_scaled_W_coordinates": list(pivot_values),
                    })
        by_source.append({
            "source_support": list(support),
            "patterns": patterns,
            "pattern_count": len(patterns),
        })
    return dimension, pivots, by_source


def build_pattern_domains(C, Z, K4, exceptional):
    dimension, pivot_local, rows = fast_general_row_patterns(C, K4, exceptional)
    exceptional_global = tuple(SUPPORTS.index(support) for support in exceptional)
    pivot_global = tuple(exceptional_global[index] for index in pivot_local)
    z_pivot, z_form, z_coordinates = pseudoinverse_form(Z)
    shifted = [[28 * COARSE_CYCLE[i][j] - Z[i][j] for j in range(21)]
               for i in range(21)]
    d_pivot, d_form, _d_coordinates = pseudoinverse_form(shifted)
    domains = []
    raw = 0
    minus_rejected = plus_rejected = 0
    for source, row in enumerate(rows):
        values = []
        for index, pattern in enumerate(row["patterns"]):
            raw += 1
            residual = [0] * 21
            for local, global_index in enumerate(exceptional_global):
                residual[global_index] = int(
                    pattern["scaled_W_row_on_exceptional"][local]
                )
            s = [Z[source][column] - residual[column] for column in range(21)]
            t = [28 * COARSE_CYCLE[source][column] - Z[source][column]
                 + residual[column] for column in range(21)]
            minus = z_form(s)
            plus = d_form(t)
            bad_minus = minus > 40
            bad_plus = plus > Fraction(160, 3)
            minus_rejected += int(bad_minus)
            plus_rejected += int(bad_plus)
            degrees = []
            exceptional_index = {support: local for local, support in enumerate(exceptional)}
            for target, support in enumerate(SUPPORTS):
                if support in exceptional_index:
                    degrees.append(int(pattern["exceptional_degrees"][
                        exceptional_index[support]
                    ]))
                else:
                    assert C[source][target] % 4 == 0
                    degrees.append(C[source][target] // 4)
            values.append({
                "original_index": index,
                "residual": tuple(residual),
                "pivot": tuple(residual[column] for column in pivot_global),
                "degrees": tuple(degrees),
                "minus4_leverage": minus,
                "plus3_leverage": plus,
                "s_pivot": tuple(s[index] for index in z_pivot),
                "s_solution": tuple(z_coordinates(s)),
                "minus4_diagonal": Fraction(40) - minus,
                "local_mask": 15,
                "active": not (bad_minus or bad_plus),
                "transport_separator": None,
            })
        domains.append(values)
    z_scale = 1
    for domain in domains:
        for pattern in domain:
            for value in pattern["s_solution"]:
                z_scale = math.lcm(z_scale, value.denominator)
    for domain in domains:
        for pattern in domain:
            pattern["s_solution_scaled"] = tuple(
                int(value * z_scale) for value in pattern["s_solution"]
            )
            pattern["minus4_diagonal_numerator"] = int(
                pattern["minus4_diagonal"] * z_scale
            )
    return {
        "dimension": dimension,
        "pivot_local": tuple(pivot_local),
        "pivot_global": pivot_global,
        "Z_pseudoinverse_principal": z_pivot,
        "D_pseudoinverse_principal": d_pivot,
        "Z_form_denominator": z_scale,
        "domains": domains,
        "raw_patterns": raw,
        "minus4_rejected": minus_rejected,
        "plus3_rejected": plus_rejected,
    }


def zero_sum_exists(patterns):
    residuals = [pattern["residual"] for pattern in patterns if pattern["active"]]
    if not residuals:
        return False
    pair_sums = {
        tuple(left[i] + right[i] for i in range(21))
        for left in residuals for right in residuals
    }
    return any(tuple(-value for value in vector) in pair_sums for vector in pair_sums)


def localized_zero_sum_exists(patterns):
    active = [pattern for pattern in patterns if pattern["active"]]
    if any(not any(pattern["local_mask"] & (1 << local) for pattern in active)
           for local in range(4)):
        return False
    left = {
        tuple(a["residual"][i] + b["residual"][i] for i in range(21))
        for a in active if a["local_mask"] & 1
        for b in active if b["local_mask"] & 2
    }
    right = {
        tuple(a["residual"][i] + b["residual"][i] for i in range(21))
        for a in active if a["local_mask"] & 4
        for b in active if b["local_mask"] & 8
    }
    return any(tuple(-value for value in row) in right for row in left)


def rownorm_fixed_point(data, use_pair_minors):
    """Arc-consistency relaxation of one residual-projector row equation."""
    domains = data["domains"]
    labels = tuple(
        (2 * support[0] + local // 2, 2 * support[1] + local % 2)
        for support in SUPPORTS for local in range(4)
    )

    if "_bilinear_table" not in data:
        all_patterns = [pattern for domain in domains for pattern in domain]
        for uid, pattern in enumerate(all_patterns):
            pattern["_uid"] = uid
        data["_bilinear_table"] = [[
            sum(a * b for a, b in
                zip(left["s_pivot"], right["s_solution_scaled"]))
            for right in all_patterns
        ] for left in all_patterns]
    bilinear_table = data["_bilinear_table"]
    scale = data["Z_form_denominator"]

    iterations = []
    local_iterations = []
    first_separator = None
    while True:
        active = [[pattern for pattern in domain if pattern["active"]]
                  for domain in domains]
        if any(not domain for domain in active):
            break
        changes = []
        for source, domain in enumerate(active):
            for pattern in domain:
                old_mask = pattern["local_mask"]
                new_mask = 0
                gx_numerator = pattern["minus4_diagonal_numerator"]
                for source_local in range(4):
                    if not old_mask & (1 << source_local):
                        continue
                    x = 4 * source + source_local
                    lower = 0
                    upper = 0
                    feasible = True
                    for target in range(21):
                        available_locals = tuple(
                            local for local in range(4)
                            if not (target == source and local == source_local)
                        )
                        degree = pattern["degrees"][target]
                        if degree > len(available_locals):
                            feasible = False
                            break
                        status_bounds = {}
                        for target_local in available_locals:
                            y = 4 * target + target_local
                            q = len(set(labels[x]) & set(labels[y]))
                            d = sum((value ^ 1) in labels[y] for value in labels[x])
                            for edge in (0, 1):
                                values = []
                                for target_pattern in active[target]:
                                    if not target_pattern["local_mask"] & (1 << target_local):
                                        continue
                                    off_numerator = (
                                        (4 - 6 * q - 2 * d - 16 * edge) * scale
                                        - bilinear_table[pattern["_uid"]][
                                            target_pattern["_uid"]
                                        ]
                                    )
                                    square = off_numerator * off_numerator
                                    if use_pair_minors and square > (
                                        gx_numerator
                                        * target_pattern["minus4_diagonal_numerator"]
                                    ):
                                        continue
                                    values.append(square)
                                status_bounds[(target_local, edge)] = (
                                    None if not values else (min(values), max(values))
                                )
                        best_lower = None
                        best_upper = None
                        for adjacent_locals in itertools.combinations(
                            available_locals, degree
                        ):
                            adjacent_locals = set(adjacent_locals)
                            subtotal_lower = 0
                            subtotal_upper = 0
                            subset_feasible = True
                            for target_local in available_locals:
                                edge = int(target_local in adjacent_locals)
                                bounds = status_bounds[(target_local, edge)]
                                if bounds is None:
                                    subset_feasible = False
                                    break
                                subtotal_lower += bounds[0]
                                subtotal_upper += bounds[1]
                            if subset_feasible:
                                best_lower = (subtotal_lower if best_lower is None
                                              else min(best_lower, subtotal_lower))
                                best_upper = (subtotal_upper if best_upper is None
                                              else max(best_upper, subtotal_upper))
                        if best_lower is None:
                            feasible = False
                            break
                        lower += best_lower
                        upper += best_upper
                    target_value = (
                        112 * gx_numerator * scale - gx_numerator * gx_numerator
                    )
                    if feasible and lower <= target_value <= upper:
                        new_mask |= 1 << source_local
                    elif first_separator is None:
                        first_separator = {
                            "source_support": list(SUPPORTS[source]),
                            "pattern_index": pattern["original_index"],
                            "source_local": source_local,
                            "target_scaled_by_Z_denominator_squared": target_value,
                            "interval": None if not feasible else [
                                lower, upper
                            ],
                            "Z_form_denominator": scale,
                            "pair_minors_used": use_pair_minors,
                        }
                if new_mask != old_mask:
                    changes.append((pattern, old_mask, new_mask))
        if not changes:
            break
        rejected = 0
        removed_locals = 0
        for pattern, old_mask, new_mask in changes:
            pattern["local_mask"] = new_mask
            removed_locals += old_mask.bit_count() - new_mask.bit_count()
            if not new_mask:
                pattern["active"] = False
                rejected += 1
        iterations.append(rejected)
        local_iterations.append(removed_locals)
    return {
        "pattern_rejection_iterations": iterations,
        "local_assignment_rejection_iterations": local_iterations,
        "rejected_patterns": sum(iterations),
        "removed_local_assignments": sum(local_iterations),
        "first_separator": first_separator,
    }


def transport_fixed_point(C, K4, data):
    domains = data["domains"]
    pivots = data["pivot_global"]
    directions = primitive_directions(data["dimension"])
    iterations = []
    while True:
        active = [[pattern for pattern in domain if pattern["active"]]
                  for domain in domains]
        if any(not domain for domain in active):
            break
        extrema = []
        for domain in active:
            extrema.append([
                (
                    min(sum(direction[i] * pattern["pivot"][i]
                            for i in range(len(pivots))) for pattern in domain),
                    max(sum(direction[i] * pattern["pivot"][i]
                            for i in range(len(pivots))) for pattern in domain),
                )
                for direction in directions
            ])
        rejected = []
        for source, domain in enumerate(active):
            for pattern in domain:
                rhs = []
                for pivot in pivots:
                    value = K4[source][pivot] - sum(
                        pattern["residual"][target]
                        * (C[target][pivot] + 4 * int(target == pivot))
                        for target in range(21)
                    )
                    rhs.append(value)
                if any(value % 4 for value in rhs):
                    pattern["transport_separator"] = {
                        "kind": "nonintegral_rhs", "rhs": rhs,
                    }
                    rejected.append(pattern)
                    continue
                target = tuple(value // 4 for value in rhs)
                for direction_index, direction in enumerate(directions):
                    target_scalar = sum(direction[i] * target[i]
                                        for i in range(len(pivots)))
                    lower = sum(
                        pattern["degrees"][fibre] * extrema[fibre][direction_index][0]
                        for fibre in range(21)
                    )
                    upper = sum(
                        pattern["degrees"][fibre] * extrema[fibre][direction_index][1]
                        for fibre in range(21)
                    )
                    if target_scalar < lower or target_scalar > upper:
                        pattern["transport_separator"] = {
                            "kind": "support_interval",
                            "direction": direction,
                            "target": target_scalar,
                            "interval": (lower, upper),
                        }
                        rejected.append(pattern)
                        break
        if not rejected:
            break
        for pattern in rejected:
            pattern["active"] = False
        iterations.append(len(rejected))
    return {
        "directions": len(directions),
        "iterations": iterations,
        "rejected": sum(iterations),
        "empty_fibres": [list(SUPPORTS[source]) for source, domain in enumerate(domains)
                         if not any(pattern["active"] for pattern in domain)],
        "zero_sum_empty_fibres": [
            list(SUPPORTS[source]) for source, domain in enumerate(domains)
            if not zero_sum_exists(domain)
        ],
    }


def encode_fraction(value):
    value = Fraction(value)
    return value.numerator if value.denominator == 1 else str(value)


def analyze_profile(entry, profile):
    exceptional, _exceptional_index, C, _C0, Z = defect.build_compression(entry, profile)
    Z2 = matmul(Z, Z)
    K4 = [[28 * Z[i][j] - Z2[i][j] for j in range(21)] for i in range(21)]
    data = build_pattern_domains(C, Z, K4, exceptional)
    leverage_active = sum(pattern["active"] for domain in data["domains"] for pattern in domain)
    leverage_zero_sum_empty = [
        list(SUPPORTS[source]) for source, domain in enumerate(data["domains"])
        if not zero_sum_exists(domain)
    ]
    transport_stages = []
    rownorm_unfiltered_stages = []
    while True:
        transport = transport_fixed_point(C, K4, data)
        rownorm = rownorm_fixed_point(data, use_pair_minors=False)
        transport_stages.append(transport)
        rownorm_unfiltered_stages.append(rownorm)
        if not transport["rejected"] and not rownorm["removed_local_assignments"]:
            break
    active_after_unfiltered = sum(
        pattern["active"] for domain in data["domains"] for pattern in domain
    )
    rownorm_pair_stages = []
    while True:
        transport = transport_fixed_point(C, K4, data)
        rownorm = rownorm_fixed_point(data, use_pair_minors=True)
        transport_stages.append(transport)
        rownorm_pair_stages.append(rownorm)
        if not transport["rejected"] and not rownorm["removed_local_assignments"]:
            break
    active_after = sum(pattern["active"] for domain in data["domains"] for pattern in domain)
    transport_rejected = sum(stage["rejected"] for stage in transport_stages)
    rownorm_unfiltered_rejected = sum(
        stage["rejected_patterns"] for stage in rownorm_unfiltered_stages
    )
    rownorm_pair_rejected = sum(
        stage["rejected_patterns"] for stage in rownorm_pair_stages
    )
    final_zero_sum_empty = [
        list(SUPPORTS[source]) for source, domain in enumerate(data["domains"])
        if not localized_zero_sum_exists(domain)
    ]
    first_separator = next((
        {
            "source_support": list(SUPPORTS[source]),
            "pattern_index": pattern["original_index"],
            **{
                key: (list(value) if isinstance(value, tuple) else value)
                for key, value in pattern["transport_separator"].items()
            },
        }
        for source, domain in enumerate(data["domains"])
        for pattern in domain if pattern["transport_separator"] is not None
    ), None)
    return {
        "parameter": profile["parameter"],
        "Z_rank": defect.rank(Z),
        "raw_row_patterns": data["raw_patterns"],
        "minus4_leverage_rejected": data["minus4_rejected"],
        "plus3_leverage_rejected": data["plus3_rejected"],
        "patterns_after_leverage": leverage_active,
        "leverage_zero_sum_empty_fibres": leverage_zero_sum_empty,
        "transport_directions": transport["directions"],
        "transport_iterations": [
            iteration for stage in transport_stages for iteration in stage["iterations"]
        ],
        "transport_rejected": transport_rejected,
        "rownorm_unfiltered_rejected": rownorm_unfiltered_rejected,
        "rownorm_unfiltered_removed_local_assignments": sum(
            stage["removed_local_assignments"] for stage in rownorm_unfiltered_stages
        ),
        "patterns_after_rownorm_unfiltered": active_after_unfiltered,
        "rownorm_pair_rejected": rownorm_pair_rejected,
        "rownorm_pair_removed_local_assignments": sum(
            stage["removed_local_assignments"] for stage in rownorm_pair_stages
        ),
        "patterns_after_transport": active_after,
        "transport_empty_fibres": [
            list(SUPPORTS[source]) for source, domain in enumerate(data["domains"])
            if not any(pattern["active"] for pattern in domain)
        ],
        "transport_zero_sum_empty_fibres": final_zero_sum_empty,
        "profile_rejected_by_row_domain": bool(
            leverage_zero_sum_empty or final_zero_sum_empty
        ),
        "first_transport_separator": first_separator,
        "first_rownorm_unfiltered_separator": next((
            stage["first_separator"] for stage in rownorm_unfiltered_stages
            if stage["first_separator"] is not None
        ), None),
        "first_rownorm_pair_separator": next((
            stage["first_separator"] for stage in rownorm_pair_stages
            if stage["first_separator"] is not None
        ), None),
        "maximum_minus4_leverage": encode_fraction(max(
            pattern["minus4_leverage"] for domain in data["domains"] for pattern in domain
        )),
        "maximum_plus3_leverage": encode_fraction(max(
            pattern["plus3_leverage"] for domain in data["domains"] for pattern in domain
        )),
    }


def main():
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    mining = json.loads(MINING.read_text(encoding="utf-8"))
    census = json.loads(KERNEL.read_text(encoding="utf-8"))
    source724 = json.loads(SOURCE724.read_text(encoding="utf-8"))
    assert source724["status"] == "INDEPENDENT_SOURCE724_MULTIBLOCK_TRANSPORT_AUDIT_PASS"
    entries = {defect.macro_key(row): row for row in catalog["macro_entries"]
               if row["signature_stabilizer_canonical"]}
    mining_profiles = {}
    for profile in mining["profile_rows"]["71"]:
        mining_profiles[(defect.macro_key(profile), profile["parameter"])] = profile

    retained = [row for row in census["rows"]
                if row["macro_passes_some_full_Gram_profile_kernel_port_CSP"]]
    assert len(retained) == 132
    rows = []
    counters = Counter()
    for macro in retained:
        key = tuple(macro["key"])
        entry = entries[key]
        profiles = []
        for stored in macro["profiles"]:
            if not stored["passes_kernel_port_CSP"]:
                continue
            profile = mining_profiles[(key, stored["parameter"])]
            result = analyze_profile(entry, profile)
            profiles.append(result)
            counters["profiles_tested"] += 1
            counters["raw_row_patterns"] += result["raw_row_patterns"]
            counters["minus4_leverage_rejected_patterns"] += result[
                "minus4_leverage_rejected"
            ]
            counters["plus3_leverage_rejected_patterns"] += result[
                "plus3_leverage_rejected"
            ]
            counters["transport_rejected_patterns"] += result["transport_rejected"]
            counters["rownorm_unfiltered_rejected_patterns"] += result[
                "rownorm_unfiltered_rejected"
            ]
            counters["rownorm_unfiltered_removed_local_assignments"] += result[
                "rownorm_unfiltered_removed_local_assignments"
            ]
            counters["rownorm_pair_rejected_patterns"] += result[
                "rownorm_pair_rejected"
            ]
            counters["rownorm_pair_removed_local_assignments"] += result[
                "rownorm_pair_removed_local_assignments"
            ]
            counters["profiles_rejected_by_row_domain"] += int(
                result["profile_rejected_by_row_domain"]
            )
        row_domain_rejected = bool(profiles) and all(
            profile["profile_rejected_by_row_domain"] for profile in profiles
        )
        source724_exact = key == (724, 1, 0)
        excluded = row_domain_rejected or source724_exact
        coverage = int(macro["coverage"])
        counters["macros_tested"] += 1
        counters["coverage_tested"] += coverage
        counters["row_domain_rejected_macros"] += int(row_domain_rejected)
        counters["row_domain_rejected_coverage"] += coverage * int(row_domain_rejected)
        counters["source724_exact_macros"] += int(source724_exact)
        counters["source724_exact_coverage"] += coverage * int(source724_exact)
        counters["excluded_macros_union"] += int(excluded)
        counters["excluded_coverage_union"] += coverage * int(excluded)
        rows.append({
            "key": list(key), "Q": int(macro["Q"]), "coverage": coverage,
            "profiles": profiles,
            "row_domain_rejected": row_domain_rejected,
            "source724_exact_exclusion": source724_exact,
            "excluded_by_union": excluded,
        })

    assert counters["macros_tested"] == 132
    assert counters["coverage_tested"] == 49086464
    result = {
        "status": "EXACT_E71_PROJECTOR_TRANSPORT_FRONTIER_COMPLETE",
        "inputs_sha256": {str(path): sha256(path) for path in
                          (CATALOG, MINING, KERNEL, SOURCE724)},
        "scope": (
            "The 132 macros retained by the frozen kernel-port census only.  "
            "No overlap product, local graph, or lower E0 layer is enumerated."
        ),
        "method": {
            "row_domains": (
                "Integral single-vertex fibre-degree rows in row(K4), already defined "
                "by the frozen full-Gram profile."
            ),
            "leverage": (
                "Exact -4 and +3 residual-projector coordinate leverage caps."
            ),
            "transport": (
                "Fixed-point support intervals for 4BR=PK4-R(C+4I), allowing each "
                "neighbour row in every target fibre to be chosen independently with "
                "repetition.  Rejection is sound; passage is deliberately weak."
            ),
            "minus4_row_norm": (
                "For each candidate row and each of its four possible exact-label "
                "positions, diag(G4^2)=112diag(G4) is bounded fibre by fibre.  Target "
                "rows and adjacency choices are independent; a second stage also uses "
                "all residual-projector 2x2 minors."
            ),
            "zero_sum": (
                "After each filter, four rows in every fibre must be able to sum to zero; "
                "ports, matchings and cross-block synchronization are ignored."
            ),
        },
        "summary": dict(counters),
        "rows": rows,
        "plus3_cross_redundancy": (
            "At the exact matrix level E3=H-E4 and HE4=E4, hence "
            "E3^2-E3=E4^2-E4 and E4E3=-(E4^2-E4).  Once the common coarse Gram "
            "and cross transport blocks are exact, the corresponding +3 row-norm and "
            "cross-diagonal defect equations contain the same idempotence defect.  They "
            "are therefore not counted as independent exclusions in this cheap lane."
        ),
        "claim_boundary": (
            "A row-domain rejection excludes a full-Gram profile, and a macro only when "
            "all of its kernel-port-passing profiles reject.  Surviving domains are not "
            "local graph completions.  The separately audited source724 theorem is added "
            "as one exact macro exclusion; no E71-wide or E0 lower bound is claimed."
        ),
        "submission_txt_written": False,
    }
    atomic_json(OUTPUT, result)
    print(json.dumps({"path": str(OUTPUT), "status": result["status"],
                      "summary": result["summary"]}, sort_keys=True))


if __name__ == "__main__":
    main()
