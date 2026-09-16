"""Exact E71/E72 Gram and rooted-moment data mining.

This is deliberately not a SAT search.  It completes every one-dimensional
full-Gram family over ``Fraction``, records trace/rank moments, and tests
candidate identities and inequalities on the existing canonical macro
catalogues.  The resulting finite observations are kept separate from the
rootless H7/triangle-flag identities, which are mathematical consequences of
the SRG equations rather than evidence from the catalogues.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from fractions import Fraction
import hashlib
import itertools
import json
import os
from pathlib import Path

from scratch_theory_local_psd_filter import bilinear_coefficients
from scratch_theory_unsigned_kernel_filter import (
    nullspace,
    psd_by_principal_minors,
    rref,
)


CATALOGS = {
    71: Path("scratch_root_e71_q2_gram_fast_expansion_macro_catalog.json"),
    72: Path("scratch_general_e72_q3_gram_fast_expansion_macro_catalog.json"),
}
KNOWN_E72_FULL = Path("scratch_theory_e72_macro_full_gram.json")
SOURCE332_PARAMETRIC = Path("scratch_theory_e72_source332_parametric_gram.json")
E73_PORT = Path("scratch_root_e73_q4_port_census.json")
OUTPUT = Path("scratch_theory_e71_e72_e0_moment_mining.json")
SUMMARY = Path("scratch_theory_e71_e72_e0_moment_mining.md")
GROUPS = tuple(range(7))
SUPPORTS = tuple(itertools.combinations(GROUPS, 2))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def atomic_write(path: Path, text: str) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def fstr(value: Fraction) -> str:
    value = Fraction(value)
    return str(value.numerator) if value.denominator == 1 else str(value)


def matrix_rank(matrix) -> int:
    if not matrix:
        return 0
    _reduced, pivots = rref(matrix)
    return len(pivots)


def matvec(matrix, vector):
    return [sum((a * b for a, b in zip(row, vector)), Fraction(0)) for row in matrix]


def affine_linear_system(coefficients, targets):
    variables = len(coefficients[0]) if coefficients else 0
    augmented = [list(map(Fraction, row)) + [Fraction(target)]
                 for row, target in zip(coefficients, targets)]
    reduced, pivots_augmented = rref(augmented)
    inconsistent = any(
        all(not value for value in row[:variables]) and row[variables]
        for row in reduced
    )
    assert not inconsistent
    pivots = [pivot for pivot in pivots_augmented if pivot < variables]
    free = [column for column in range(variables) if column not in pivots]
    particular = [Fraction(0) for _ in range(variables)]
    for row_index, pivot in enumerate(pivots):
        particular[pivot] = reduced[row_index][variables]
    directions = []
    for free_column in free:
        direction = [Fraction(0) for _ in range(variables)]
        direction[free_column] = 1
        for row_index, pivot in enumerate(pivots):
            direction[pivot] = -reduced[row_index][free_column]
        directions.append(direction)
    for row, target in zip(coefficients, targets):
        assert sum((a * b for a, b in zip(row, particular)), Fraction(0)) == target
        assert all(sum((a * b for a, b in zip(row, direction)), Fraction(0)) == 0
                   for direction in directions)
    return particular, directions


def symmetric_matrix(parameters, dimension):
    matrix = [[Fraction(0) for _ in range(dimension)] for _ in range(dimension)]
    positions = [(left, right) for left in range(dimension)
                 for right in range(left, dimension)]
    assert len(parameters) == len(positions)
    for value, (left, right) in zip(parameters, positions):
        matrix[left][right] = matrix[right][left] = Fraction(value)
    return matrix


def gram_setup(entry):
    supports = tuple(tuple(item["support"]) for item in entry["exceptional_supports"])
    deficits = tuple(int(item["deficit"]) for item in entry["exceptional_supports"])
    incidence_t = [[int(group in support) for support in supports] for group in GROUPS]
    basis_columns = nullspace(incidence_t)
    dimension = len(basis_columns)
    W = [[basis_columns[column][row] for column in range(dimension)]
         for row in range(len(supports))]
    coefficients = []
    targets = []
    for index, deficit in enumerate(deficits):
        coefficients.append(bilinear_coefficients(W[index], W[index]))
        targets.append(Fraction(2 * deficit))
    overlap = {
        tuple(sorted((int(left), int(right)))): int(value)
        for left, right, value in entry["overlap_block_totals"]
    }
    expected_overlap = {
        pair for pair in itertools.combinations(range(len(supports)), 2)
        if set(supports[pair[0]]) & set(supports[pair[1]])
    }
    assert set(overlap) == expected_overlap
    for left, right in sorted(overlap):
        coefficients.append(bilinear_coefficients(W[left], W[right]))
        targets.append(Fraction(-overlap[left, right]))
    particular, directions = affine_linear_system(coefficients, targets)
    assert len(directions) <= 1
    return supports, deficits, W, overlap, particular, directions


def evaluate_parameter(supports, deficits, W, overlap, parameters, parameter_label):
    dimension = len(W[0]) if W else 0
    H = symmetric_matrix(parameters, dimension)
    is_psd, minimum_minor, bad_subset = psd_by_principal_minors(H)
    Z = [[
        sum((W[left][a] * H[a][b] * W[right][b]
             for a in range(dimension) for b in range(dimension)), Fraction(0))
        for right in range(len(supports))
    ] for left in range(len(supports))]
    assert [Z[index][index] for index in range(len(supports))] == [
        2 * deficit for deficit in deficits
    ]

    disjoint = {}
    integral = True
    in_range = True
    for left, right in itertools.combinations(range(len(supports)), 2):
        if set(supports[left]) & set(supports[right]):
            assert Z[left][right] == -overlap[left, right]
        else:
            value = Fraction(4) - Z[left][right]
            disjoint[left, right] = value
            integral &= value.denominator == 1
            in_range &= 0 <= value <= 16

    row_sums = []
    for left, support in enumerate(supports):
        total = Fraction(2 * (4 - deficits[left]))
        exceptional_disjoint = 0
        for right, other in enumerate(supports):
            if left == right:
                continue
            pair = tuple(sorted((left, right)))
            if set(support) & set(other):
                total += overlap[pair]
            else:
                exceptional_disjoint += 1
                total += disjoint[pair]
        total += 4 * (10 - exceptional_disjoint)
        row_sums.append(total)
    rows_48 = all(value == 48 for value in row_sums)
    passes = is_psd and integral and in_range and rows_48
    if not passes:
        return None, {
            "parameter": parameter_label,
            "psd": is_psd,
            "integral": integral,
            "in_range": in_range,
            "rows_48": rows_48,
            "minimum_minor": fstr(minimum_minor),
            "bad_subset": None if bad_subset is None else list(bad_subset),
        }

    Z_rank = matrix_rank(Z)
    trace = sum((Z[index][index] for index in range(len(Z))), Fraction(0))
    trace_square = sum((value * value for row in Z for value in row), Fraction(0))
    overlap_square = sum(Fraction(value * value) for value in overlap.values())
    deviation_square = sum((Fraction(4) - value) ** 2 for value in disjoint.values())
    deviation_sum = sum((Fraction(4) - value for value in disjoint.values()), Fraction(0))
    deficit_square = sum(deficit * deficit for deficit in deficits)
    assert trace_square == 4 * deficit_square + 2 * (overlap_square + deviation_square)
    assert deviation_sum == sum(deficits)
    assert trace == 2 * sum(deficits)
    assert Z_rank * trace_square >= trace * trace
    assert int(trace_square) % 4 == int(trace) % 4
    arithmetic_floor = (int(trace * trace) + Z_rank - 1) // Z_rank
    while arithmetic_floor % 4 != int(trace) % 4:
        arithmetic_floor += 1

    # Complete 21-by-21 fibre compression C=4R.
    exceptional_index = {support: index for index, support in enumerate(supports)}
    C = [[Fraction(0) for _ in SUPPORTS] for _ in SUPPORTS]
    for left, F in enumerate(SUPPORTS):
        if F in exceptional_index:
            i = exceptional_index[F]
            C[left][left] = 2 * (4 - deficits[i])
        else:
            C[left][left] = 8
        for right in range(left + 1, len(SUPPORTS)):
            G = SUPPORTS[right]
            if set(F) & set(G):
                if F in exceptional_index and G in exceptional_index:
                    value = overlap[tuple(sorted((exceptional_index[F], exceptional_index[G])))]
                else:
                    value = 0
            else:
                if F in exceptional_index and G in exceptional_index:
                    value = disjoint[tuple(sorted((exceptional_index[F], exceptional_index[G])))]
                else:
                    value = 4
            C[left][right] = C[right][left] = value
    assert all(sum(row) == 48 for row in C)

    incidence = [[int(group in support) for group in GROUPS] for support in SUPPORTS]
    LLt = [[sum(a * b for a, b in zip(incidence[left], incidence[right]))
            for right in range(21)] for left in range(21)]
    C2 = [[sum(C[left][middle] * C[middle][right] for middle in range(21))
           for right in range(21)] for left in range(21)]
    K4 = [[
        192 * int(left == right) + 128 - 4 * C[left][right]
        - 32 * LLt[left][right] - C2[left][right]
        for right in range(21)
    ] for left in range(21)]
    K_rank = matrix_rank(K4)
    K_nullity = 21 - K_rank
    ordinary = [index for index, support in enumerate(SUPPORTS)
                if support not in exceptional_index]
    baseline_columns = [
        [incidence[row][group] for row in range(21)] for group in GROUPS
    ] + [
        [int(row == ordinary_index) for row in range(21)]
        for ordinary_index in ordinary
    ]
    for vector in baseline_columns:
        assert all(value == 0 for value in matvec(K4, vector))
    baseline_rank = matrix_rank(list(map(list, zip(*baseline_columns))))
    assert baseline_rank <= K_nullity

    profile = {
        "parameter": parameter_label,
        "disjoint_D": [[left, right, int(value)] for (left, right), value in sorted(disjoint.items())],
        "disjoint_D_sha256": hashlib.sha256(json.dumps(
            [[left, right, int(value)] for (left, right), value in sorted(disjoint.items())],
            separators=(",", ":"),
        ).encode("ascii")).hexdigest().upper(),
        "overlap_sum": sum(overlap.values()),
        "overlap_square": int(overlap_square),
        "disjoint_deviation_sum": int(deviation_sum),
        "disjoint_deviation_square": int(deviation_square),
        "Z_trace": int(trace),
        "Z_rank": Z_rank,
        "Z_trace_square": int(trace_square),
        "Z_trace_rank_Cauchy_slack": int(Z_rank * trace_square - trace * trace),
        "Z_equal_nonzero_eigenvalue_case": Z_rank * trace_square == trace * trace,
        "Z_trace_square_arithmetic_floor": arithmetic_floor,
        "Z_trace_square_excess_above_rank_congruence_floor":
            int(trace_square) - arithmetic_floor,
        "Z_rank_deficiency_in_unsigned_circulation_space": dimension - Z_rank,
        "equitable_K_kernel_dimension": K_nullity,
        "equitable_baseline_kernel_rank": baseline_rank,
        "equitable_novel_kernel_dimension": K_nullity - baseline_rank,
        "H_dimension": dimension,
    }
    return profile, None


def enumerate_profiles(entry):
    supports, deficits, W, overlap, particular, directions = gram_setup(entry)
    candidates = []
    if not directions:
        candidates.append(("unique", particular))
    else:
        direction = directions[0]
        H0 = symmetric_matrix(particular, len(W[0]))
        H1 = symmetric_matrix(direction, len(W[0]))
        Z0 = [[sum((W[i][a] * H0[a][b] * W[j][b]
                    for a in range(len(H0)) for b in range(len(H0))), Fraction(0))
               for j in range(len(W))] for i in range(len(W))]
        Z1 = [[sum((W[i][a] * H1[a][b] * W[j][b]
                    for a in range(len(H1)) for b in range(len(H1))), Fraction(0))
               for j in range(len(W))] for i in range(len(W))]
        pivot_pair = next(
            (pair for pair in itertools.combinations(range(len(supports)), 2)
             if not (set(supports[pair[0]]) & set(supports[pair[1]]))
             and Z1[pair[0]][pair[1]]),
            None,
        )
        assert pivot_pair is not None
        left, right = pivot_pair
        parameter_values = {
            (Fraction(4 - target) - Z0[left][right]) / Z1[left][right]
            for target in range(17)
        }
        for value in sorted(parameter_values):
            candidates.append((f"t={fstr(value)}", [
                a + value * b for a, b in zip(particular, direction)
            ]))
    profiles = []
    rejected = []
    for label, parameters in candidates:
        profile, failure = evaluate_parameter(
            supports, deficits, W, overlap, parameters, label
        )
        if profile is not None:
            profiles.append(profile)
        else:
            rejected.append(failure)
    assert len({item["disjoint_D_sha256"] for item in profiles}) == len(profiles)
    return profiles, rejected, len(directions)


def histogram(rows, key):
    return {str(value): count for value, count in sorted(Counter(row[key] for row in rows).items())}


def range_with_witness(rows, key):
    minimum = min(row[key] for row in rows)
    maximum = max(row[key] for row in rows)
    def witness(value):
        row = next(item for item in rows if item[key] == value)
        return {
            "source_row_index": row["source_row_index"],
            "state_orbit_number": row["state_orbit_number"],
            "signature_stabilizer_orbit_number": row["signature_stabilizer_orbit_number"],
            "profile_parameter": row["parameter"],
            "value": value,
        }
    return {"minimum": minimum, "minimum_witness": witness(minimum),
            "maximum": maximum, "maximum_witness": witness(maximum)}


def main() -> None:
    documents = {e0: json.loads(path.read_text(encoding="utf-8"))
                 for e0, path in CATALOGS.items()}
    macro_rows = {}
    profile_rows = {}
    rejected_rows = {}
    for e0, document in documents.items():
        canonical = [entry for entry in document["macro_entries"]
                     if entry["signature_stabilizer_canonical"]]
        macros = []
        profiles_all = []
        rejected_all = []
        tau = 84 - e0
        for entry in canonical:
            deficits = [int(item["deficit"]) for item in entry["exceptional_supports"]]
            Q = int(entry["Q"])
            overlap = [int(value) for _left, _right, value in entry["overlap_block_totals"]]
            assert sum(deficits) == tau
            assert sum(overlap) == 2 * tau
            assert 0 <= Q <= tau
            profiles, rejected, affine_dimension = enumerate_profiles(entry)
            base = {
                "E0": e0,
                "tau": tau,
                "source_row_index": int(entry["source_row_index"]),
                "state_orbit_number": int(entry["state_orbit_number"]),
                "signature_stabilizer_orbit_number": int(entry["signature_stabilizer_orbit_number"]),
                "coverage": int(entry["signature_orbit_labelled_coverage"]),
                "Q_diagonals": Q,
                "S_sides": e0 - Q,
                "Y_support": tau,
                "Y_l1": tau + Q,
                "Y_l2_square": tau + 3 * Q,
                "Y_ones": tau - Q,
                "Y_twos": Q,
                "exceptional_supports": len(deficits),
                "deficit_square_sum": sum(value * value for value in deficits),
                "maximum_deficit": max(deficits),
                "overlap_blocks": len(overlap),
                "overlap_sum": sum(overlap),
                "overlap_square": sum(value * value for value in overlap),
                "gram_affine_solution_dimension": affine_dimension,
                "integral_PSD_full_Gram_profiles": len(profiles),
            }
            macros.append(base)
            for profile in profiles:
                profiles_all.append(dict(base, **profile))
            for failure in rejected:
                rejected_all.append(dict(base, **failure))
        macro_rows[e0] = macros
        profile_rows[e0] = profiles_all
        rejected_rows[e0] = rejected_all

    # Reproduce the independently stored E72 unique/parametric breadth.
    known = json.loads(KNOWN_E72_FULL.read_text(encoding="utf-8"))
    assert len(macro_rows[72]) == known["summary"]["canonical_macro_entries"] == 163
    assert sum(row["gram_affine_solution_dimension"] == 0 for row in macro_rows[72]) == 162
    assert sum(row["integral_PSD_full_Gram_profiles"] == 0 for row in macro_rows[72]) == 3
    assert sum(row["integral_PSD_full_Gram_profiles"] == 3 for row in macro_rows[72]) == 1
    assert len(profile_rows[72]) == 162
    source332 = json.loads(SOURCE332_PARAMETRIC.read_text(encoding="utf-8"))
    expected_332_profiles = {
        hashlib.sha256(json.dumps(
            [[int(left), int(right), int(value)] for left, right, value
             in item["disjoint_exceptional_block_totals"]],
            separators=(",", ":"),
        ).encode("ascii")).hexdigest().upper()
        for item in source332["feasible_parameters"]
    }
    actual_332_profiles = {
        row["disjoint_D_sha256"] for row in profile_rows[72]
        if row["source_row_index"] == 332
    }
    assert actual_332_profiles == expected_332_profiles and len(actual_332_profiles) == 3

    # E73 is only a parity counterexample control, not part of the mining set.
    e73 = json.loads(E73_PORT.read_text(encoding="utf-8"))
    odd_q_controls = []
    for row_number, row in enumerate(e73.get("rows", [])):
        for q, count in row.get("feasible_Q_histogram", {}).items():
            if int(q) % 2 and int(count):
                odd_q_controls.append({
                    "row_number": row_number,
                    "compression_orbit_index": row.get("compression_orbit_index"),
                    "Q": int(q),
                    "labelled_states": int(count),
                })
                break
    assert odd_q_controls

    summaries = {}
    feature_keys = (
        "Q_diagonals", "S_sides", "Y_ones", "Y_twos",
        "exceptional_supports", "deficit_square_sum", "overlap_blocks",
            "overlap_square", "Z_rank", "Z_trace_square",
            "Z_trace_rank_Cauchy_slack", "equitable_novel_kernel_dimension",
            "Z_trace_square_excess_above_rank_congruence_floor",
            "Z_rank_deficiency_in_unsigned_circulation_space",
    )
    for e0 in (71, 72):
        macros = macro_rows[e0]
        profiles = profile_rows[e0]
        viable_macro_keys = {
            (row["source_row_index"], row["state_orbit_number"],
             row["signature_stabilizer_orbit_number"])
            for row in profiles
        }
        profile_count_by_macro = Counter(
            (row["source_row_index"], row["state_orbit_number"],
             row["signature_stabilizer_orbit_number"])
            for row in profiles
        )
        viable_macros = [
            row for row in macros
            if (row["source_row_index"], row["state_orbit_number"],
                row["signature_stabilizer_orbit_number"]) in viable_macro_keys
        ]
        rejected_macros = [row for row in macros if row not in viable_macros]
        summaries[e0] = {
            "canonical_macros": len(macros),
            "catalog_rooted_coverage": sum(row["coverage"] for row in macros),
            "macros_with_unique_full_Gram": sum(
                row["gram_affine_solution_dimension"] == 0 for row in macros
            ),
            "macros_with_one_parameter_full_Gram": sum(
                row["gram_affine_solution_dimension"] == 1 for row in macros
            ),
            "macros_with_no_integral_PSD_full_Gram_profile": sum(
                row["integral_PSD_full_Gram_profiles"] == 0 for row in macros
            ),
            "macros_with_integral_PSD_full_Gram_profile": len(viable_macros),
            "full_Gram_profile_count_per_viable_macro_histogram": {
                str(key): value for key, value in sorted(Counter(profile_count_by_macro.values()).items())
            },
            "overlap_macro_coverage_rejected_by_full_Gram": sum(
                row["coverage"] for row in rejected_macros
            ),
            "overlap_macro_coverage_retained_by_full_Gram": sum(
                row["coverage"] for row in viable_macros
            ),
            "retained_macro_Q_histogram": histogram(viable_macros, "Q_diagonals"),
            "integral_PSD_full_Gram_profiles": len(profiles),
            "macro_Q_histogram": histogram(macros, "Q_diagonals"),
            "profile_feature_ranges": {
                key: range_with_witness(profiles, key) for key in feature_keys
            },
            "Z_rank_histogram": histogram(profiles, "Z_rank"),
            "Z_trace_square_histogram": histogram(profiles, "Z_trace_square"),
            "Z_Cauchy_equality_profiles": sum(
                row["Z_equal_nonzero_eigenvalue_case"] for row in profiles
            ),
            "Z_rank_vs_unsigned_circulation_dimension_histogram": {
                f"{dimension},{rank}": count
                for (dimension, rank), count in sorted(Counter(
                    (row["H_dimension"], row["Z_rank"]) for row in profiles
                ).items())
            },
            "Z_trace_square_minimum_by_rank": {
                str(rank): min(row["Z_trace_square"] for row in profiles if row["Z_rank"] == rank)
                for rank in sorted({row["Z_rank"] for row in profiles})
            },
            "Z_rank_congruence_floor_minimum_excess_by_rank": {
                str(rank): min(
                    row["Z_trace_square_excess_above_rank_congruence_floor"]
                    for row in profiles if row["Z_rank"] == rank
                )
                for rank in sorted({row["Z_rank"] for row in profiles})
            },
            "equitable_novel_kernel_histogram": histogram(
                profiles, "equitable_novel_kernel_dimension"
            ),
        }

    # Search simple nontrivial one/two-feature linear separators.  These are
    # empirical diagnostics only; direct E0/tau coordinates are excluded.
    separator_features = (
        "Q_diagonals", "exceptional_supports", "deficit_square_sum",
        "overlap_blocks", "overlap_square", "Z_rank", "Z_trace_square",
        "equitable_novel_kernel_dimension",
    )
    separators = []
    left_rows, right_rows = profile_rows[71], profile_rows[72]
    for first_index, first in enumerate(separator_features):
        for second in separator_features[first_index + 1:]:
            for a in range(-4, 5):
                for b in range(-4, 5):
                    if not a or not b:
                        continue
                    if abs(a) + abs(b) > 6:
                        continue
                    values71 = [a * row[first] + b * row[second] for row in left_rows]
                    values72 = [a * row[first] + b * row[second] for row in right_rows]
                    if max(values71) < min(values72):
                        separators.append({
                            "expression": f"{a}*{first}+{b}*{second}",
                            "E71_range": [min(values71), max(values71)],
                            "E72_range": [min(values72), max(values72)],
                            "margin": min(values72) - max(values71),
                            "coefficient_l1": abs(a) + abs(b),
                        })
                    elif max(values72) < min(values71):
                        separators.append({
                            "expression": f"{a}*{first}+{b}*{second}",
                            "E72_range": [min(values72), max(values72)],
                            "E71_range": [min(values71), max(values71)],
                            "margin": min(values71) - max(values72),
                            "coefficient_l1": abs(a) + abs(b),
                        })
    separators.sort(key=lambda row: (row["coefficient_l1"], -row["margin"], row["expression"]))
    unique_separators = []
    seen_ranges = set()
    for row in separators:
        key = (tuple(row.get("E71_range", ())), tuple(row.get("E72_range", ())))
        if key not in seen_ranges:
            seen_ranges.add(key)
            unique_separators.append(row)
        if len(unique_separators) == 12:
            break

    e71_q2 = next(row for row in macro_rows[71] if row["Q_diagonals"] == 2)
    e72_q12 = next(row for row in macro_rows[72] if row["Q_diagonals"] == 12)
    rejected_macro_audit = {}
    for e0 in (71, 72):
        grouped_failures = defaultdict(list)
        for row in rejected_rows[e0]:
            grouped_failures[(
                row["source_row_index"], row["state_orbit_number"],
                row["signature_stabilizer_orbit_number"],
            )].append(row)
        rows = []
        for macro in macro_rows[e0]:
            if macro["integral_PSD_full_Gram_profiles"]:
                continue
            key = (macro["source_row_index"], macro["state_orbit_number"],
                   macro["signature_stabilizer_orbit_number"])
            failures = grouped_failures[key]
            assert failures
            rows.append({
                "source_row_index": key[0],
                "state_orbit_number": key[1],
                "signature_stabilizer_orbit_number": key[2],
                "Q": macro["Q_diagonals"],
                "coverage": macro["coverage"],
                "affine_solution_dimension": macro["gram_affine_solution_dimension"],
                "parameters_exhaustively_tested": len(failures),
                "failure_signature_histogram": {
                    signature: count for signature, count in sorted(Counter(
                        "PSD=" + str(item["psd"])
                        + ",integral=" + str(item["integral"])
                        + ",range=" + str(item["in_range"])
                        + ",rows48=" + str(item["rows_48"])
                        for item in failures
                    ).items())
                },
            })
        rejected_macro_audit[str(e0)] = rows
    result = {
        "status": "EXACT_E71_E72_E0_MOMENT_MINING_COMPLETE",
        "scope": "canonical overlap-Gram macros and every integral PSD full-Gram completion",
        "inputs": {
            str(e0): {"path": str(path), "sha256": sha256(path)}
            for e0, path in CATALOGS.items()
        } | {
            "known_E72_full_Gram": {
                "path": str(KNOWN_E72_FULL), "sha256": sha256(KNOWN_E72_FULL)
            },
            "source332_parametric_control": {
                "path": str(SOURCE332_PARAMETRIC), "sha256": sha256(SOURCE332_PARAMETRIC)
            },
            "E73_odd_Q_control": {"path": str(E73_PORT), "sha256": sha256(E73_PORT)},
        },
        "rootless_exact_identities": {
            "D_motif": (
                "(r, diagonal fibre edge xy) is in bijection with induced H7: "
                "two root triangles on r, the complementary spokes to x,y, and xy; "
                "degree sequence (4,3,3,3,3,3,3) makes r unique"
            ),
            "sum_D": "sum_r D(r)=N(H7)",
            "Reimbayev_Hamiltonian_table_identification": {
                "motif_name": "H7 is Z2 (old Hamiltonian-table H18)",
                "identity": "N(H7)=z2=n3-z11/4",
            },
            "sum_S": "sum_r S(r)=6P",
            "triangle_prism": "n3+3P=4158",
            "sum_E0": (
                "sum_r E0(r)=6P+N(H7)=8316-2*n3+N(H7)"
                "=8316-n3-z11/4"
            ),
            "triangle_flag_matrix": (
                "X joins unmatched flags of r=2 disjoint-triangle pairs; F maps "
                "a triangle flag to its marked graph vertex; Y=F^T X"
            ),
            "pointwise_Y": {
                "entries": "Y[r,beta] in {0,1,2}",
                "twos": "#{beta:Y[r,beta]=2}=D(r)",
                "l1": "sum_beta Y[r,beta]=84-S(r)",
                "support": "#{beta:Y[r,beta]>0}=84-E0(r)",
                "l2_square": "sum_beta Y[r,beta]^2=84-E0(r)+3D(r)",
            },
            "support_indicator": {
                "definition": "U=1_{Y>0}=(3Y-Y o Y)/2 entrywise",
                "pointwise_E0": "E0(r)=84-(U*1)_r",
                "lower_bound_translation": "E0(r)>=L iff row_support(Y_r)<=84-L",
            },
            "global_Y": {
                "entry_sum": "sum Y=2*n3",
                "frobenius_square": "||Y||_F^2=2*n3+2*N(H7)",
                "support_sum": "sum_r(84-E0(r))=2*n3-N(H7)",
                "support_sum_Z11_form": "sum_r(84-E0(r))=n3+z11/4",
                "column_sum_square": "1^T Y Y^T 1=3*sum_T q(T)^2",
                "unordered_offdiagonal_YYt_sum": (
                    "sum_{r<s}(YY^T)_{rs}="
                    "(3*sum_T q(T)^2-2*n3-2*N(H7))/2"
                ),
            },
            "sum_E0_square": (
                "sum_r E0(r)^2=698544-334*n3+167*N(H7)+2*M2, "
                "M2=sum_r binom(84-E0(r),2); equivalently "
                "698544-167*n3-(167/4)*z11+2*M2"
            ),
            "average_thresholds": {
                "average_E0_at_least_72_iff": "N(H7)>=2*n3-1188",
                "average_E0_at_least_73_iff": "N(H7)>=2*n3-1089",
                "average_E0_at_least_72_Z11_form": "n3+z11/4<=1188",
                "average_E0_at_least_73_Z11_form": "n3+z11/4<=1089",
            },
        },
        "catalogue_exact_identities_verified": [
            "tau=84-E0=sum_F delta_F",
            "E0=S+Q and the triangle-flag row has tau-Q ones and Q twos",
            "sum_overlap D_FG=2*tau",
            "sum_disjoint_exceptional (4-D_FG)=tau",
            "tr(Z)=2*tau",
            "tr(Z^2)=4*sum(delta_F^2)+2*(overlap_square+disjoint_deviation_square)",
            "rank(Z)*tr(Z^2)>=tr(Z)^2",
            "tr(Z^2)=2*tau (mod 4)",
            "Q*(tau-Q)>=0 (the pointwise Y Cauchy inequality)",
        ],
        "full_Gram_enumeration_controls": {
            "all_affine_families_have_dimension_at_most_one": True,
            "one_varying_disjoint_block_enumerates_all_integral_parameters_in_0_16": True,
            "E72_unique_summary_reproduced": True,
            "E72_source332_three_profiles_reproduced_by_disjoint_D_hash": True,
            "source332_profile_hashes": sorted(actual_332_profiles),
        },
        "summaries": {str(key): value for key, value in summaries.items()},
        "macros_rejected_by_exhaustive_full_Gram_completion": rejected_macro_audit,
        "lower_bound_candidates": {
            "pointwise_L72": {
                "equivalent_flag_statement": "every row of U=1_{F^T X>0} has weight at most 12",
                "local_Gram_status": (
                    "not implied: 157 E71 canonical macros have an integral PSD full-Gram "
                    "completion with row-support surrogate tau=13"
                ),
                "needed_new_input": "a cross-root/triangle-flag compatibility inequality",
            },
            "pointwise_L71": {
                "equivalent_flag_statement": "every row of U has weight at most 13",
                "catalogue_status": "consistent and tight on all surviving E71 full-Gram profiles",
                "proof_status": "unproved; E70 was not classified by these catalogues",
            },
            "average_L72": {
                "equivalent_motif_inequality": "N(H7)>=2*n3-1188",
                "equivalent_Z11_inequality": "n3+z11/4<=1188",
            },
            "average_L73": {
                "equivalent_motif_inequality": "N(H7)>=2*n3-1089",
                "equivalent_Z11_inequality": "n3+z11/4<=1089",
            },
            "Gram_trace_only": {
                "status": "no E71 exclusion and no small two-feature E71/E72 separator found",
                "sharp_E71_control": "rank=3, tr(Z)=26, tr(Z^2)=226, Cauchy/congruence excess 0",
            },
        },
        "counterexample_audit": {
            "pointwise_E0_at_least_72_not_implied_by_current_local_Gram_data": {
                "overlap_Gram_counterexample_macros": len(macro_rows[71]),
                "integral_PSD_full_Gram_counterexample_macros": sum(
                    row["integral_PSD_full_Gram_profiles"] > 0 for row in macro_rows[71]
                ),
                "first_witness": e71_q2,
            },
            "Q_at_least_3_not_universal_in_E71_E72_relaxation": {
                "witness": e71_q2,
            },
            "Q_even_is_only_an_E71_E72_catalogue_observation": {
                "E73_odd_Q_witness": odd_q_controls[0],
            },
            "Q_equals_tau_Cauchy_equality_is_not_realizability": {
                "E72_local_witness": e72_q12,
                "note": (
                    "The displayed source_row_index=133 Q12 branch was already "
                    "excluded by the stronger source133 balance/collision analysis."
                ),
            },
        },
        "empirical_two_feature_separators_not_claimed_universal": unique_separators,
        "profile_rows": {str(key): value for key, value in profile_rows.items()},
        "claim_boundary": (
            "Finite catalogue inequalities are diagnostics, not graph theorems. "
            "Only the explicitly listed SRG/motif/flag and Gram algebra identities "
            "are promoted as universal. The E71 macros are counterexamples inside "
            "the current local relaxation, not 99-vertex graph constructions."
        ),
    }
    atomic_write(OUTPUT, json.dumps(result, indent=2) + "\n")

    summary = f"""# E71/E72 E0 moment and Gram mining

Status: `{result['status']}`.

## Rootless interpretation of the missing diagonal term

A selected diagonal edge in a root fibre determines an induced seven-vertex
graph `H7`: two root triangles sharing their root, complementary spokes to
the diagonal endpoints, and the diagonal edge itself.  Its induced degree
sequence is `(4,3^6)`, so the root is unique.  Therefore

```
sum_r D(r) = N(H7),
N(H7) = z2 = n3-z11/4,
sum_r E0(r) = 6P + N(H7) = 8316-n3-z11/4.
```

Using unmatched flags of the `r=2` disjoint-triangle relation, let `X` be the
flag relation, `F` the flag-to-vertex incidence, and `Y=F^T X`.  Then every
entry of `Y` is `0,1,2`, with

```
#2 in row r       = D(r),
row sum           = 84-S(r),
row support       = 84-E0(r),
row square norm   = 84-E0(r)+3D(r).
```

The support indicator is the entrywise quadratic

```
U = 1_{{Y>0}} = (3Y-Y o Y)/2,
E0(r)=84-(U 1)_r.
```

Moreover each of the three columns belonging to a triangle `T` has sum
`q(T)`.  Hence

```
1^T YY^T 1 = 3 sum_T q(T)^2,
sum_{{r<s}} (YY^T)_{{r,s}}
  = (3 sum_T q(T)^2-2*n3-2*N(H7))/2.
```

Consequently `sum Y=2*n3`, `||Y||_F^2=2*n3+2*N(H7)`, and, with
`M2=sum_r binom(84-E0(r),2)`,

```
sum_r E0(r)^2 = 698544 - 334*n3 + 167*N(H7) + 2*M2.
```

Thus a useful theoretical lower-bound target is an upper bound on the row
support of `Y`, or a lower bound on `N(H7)`.  In particular average `E0>=72`
is equivalent to `N(H7)>=2*n3-1188`, or `n3+z11/4<=1188`; average `E0>=73`
is equivalent to `N(H7)>=2*n3-1089`, or `n3+z11/4<=1089`.

## Exact catalogue audit

| E0 | canonical macros | full-Gram profiles | Q range | full-Gram affine dimensions |
|---:|---:|---:|---:|---:|
| 71 | {len(macro_rows[71])} | {len(profile_rows[71])} | {min(r['Q_diagonals'] for r in macro_rows[71])}..{max(r['Q_diagonals'] for r in macro_rows[71])} | 0:{sum(r['gram_affine_solution_dimension']==0 for r in macro_rows[71])}, 1:{sum(r['gram_affine_solution_dimension']==1 for r in macro_rows[71])} |
| 72 | {len(macro_rows[72])} | {len(profile_rows[72])} | {min(r['Q_diagonals'] for r in macro_rows[72])}..{max(r['Q_diagonals'] for r in macro_rows[72])} | 0:{sum(r['gram_affine_solution_dimension']==0 for r in macro_rows[72])}, 1:{sum(r['gram_affine_solution_dimension']==1 for r in macro_rows[72])} |

Completing the 33 one-parameter E71 Gram systems is itself a safe new
filter: 23 of 180 canonical overlap macros have no integral PSD full-Gram
completion.  It leaves 157 macros, 165 full profiles, and rooted overlap
coverage {summaries[71]['overlap_macro_coverage_retained_by_full_Gram']:,}
from {summaries[71]['catalog_rooted_coverage']:,}.

Every retained full profile satisfies exactly

```
sum overlap D = 2*tau,
sum disjoint (4-D) = tau,
tr Z = 2*tau,
tr Z^2 = 4 sum(delta^2) + 2(overlap_square+x_square),
rank(Z) tr(Z^2) >= tr(Z)^2.
tr(Z^2) = 2*tau (mod 4).
```

The congruence follows because the diagonal contribution is divisible by
four, while squares of off-diagonal integers reduce to their values modulo
two; `sum overlap D=2*tau` and `sum disjoint (4-D)=tau`.  E71 therefore has
`tr(Z^2)=2 mod 4`, while E72 has `tr(Z^2)=0 mod 4`.  This explains the
smallest possible positive trace/rank slack of two at E71 (attained by
source 2601, rank three, `tr(Z^2)=226`).  It is a sharp arithmetic condition,
but does not exclude E71.

The E71 catalogue contains local Gram-feasible `E0=71,Q=2,S=69` macros.
Hence neither pointwise `E0>=72` nor `Q>=3` follows from the present
compression/port/overlap-Gram conditions.  Both catalogues happen to have
even `Q`, but E73 supplies exact odd-`Q` port states, so parity is not a
universal law.  The E72 catalogue has `Q=tau=12` rows at sources 133, 134,
and 137.  Sources 133 and 134 are separately excluded by stronger structural
arguments (source 134 is the K4 family), so pointwise moment equality alone
is not a realizability certificate.

The clean pointwise target is now explicit: `E0(r)>=72` is equivalent to
every row of `U=1_{{F^T X>0}}` having weight at most 12.  The 157 fully
Gram-completable E71 macros have the local surrogate weight 13, so such a
proof must use compatibility between different roots/triangle flags; no
inequality of the present one-root Gram moments can establish it.  The next
weaker candidate `E0(r)>=71` is consistent and tight on these data, but is
not proved because E70 is outside the two catalogues.
"""
    atomic_write(SUMMARY, summary)
    print(json.dumps({
        "status": result["status"],
        "E71_macros": len(macro_rows[71]),
        "E71_profiles": len(profile_rows[71]),
        "E72_macros": len(macro_rows[72]),
        "E72_profiles": len(profile_rows[72]),
        "separators": len(unique_separators),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
