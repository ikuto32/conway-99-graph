"""Independent exact audit of the E71 support-diagonal Gram filter.

The producer implementation is not imported.  This audit deliberately uses
right-to-left pivots for its primary kernel and diagonal-system solve, then
compares invariant Z matrices.  A second conventional basis is used only to
verify the producer's stored coordinate matrices.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from collections import Counter, defaultdict, deque
from fractions import Fraction
from pathlib import Path


INPUT = Path("scratch_root_e71_q2_port_feasible_states.json")
FILTER_SCRIPT = Path("scratch_root_e71_unsigned_kernel_filter.py")
FILTER_OUTPUT = Path("scratch_root_e71_unsigned_kernel_filter.json")
THEORY = Path("scratch_theory_gram_circulation.md")
OUTPUT = Path("scratch_root_e71_unsigned_kernel_independent_audit.json")
REPORT = Path("scratch_root_e71_unsigned_kernel_independent_audit.md")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def echelon(matrix, reverse_columns=False, augmented=False):
    """Exact full elimination; augmented columns are never eligible pivots."""

    rows = [list(map(Fraction, row)) for row in matrix]
    if not rows:
        return rows, []
    variable_columns = len(rows[0]) - int(augmented)
    columns = range(variable_columns - 1, -1, -1) \
        if reverse_columns else range(variable_columns)
    pivots = []
    pivot_row = 0
    for column in columns:
        selected = next((row for row in range(pivot_row, len(rows))
                         if rows[row][column]), None)
        if selected is None:
            continue
        rows[pivot_row], rows[selected] = rows[selected], rows[pivot_row]
        divisor = rows[pivot_row][column]
        rows[pivot_row] = [value / divisor for value in rows[pivot_row]]
        for row in range(len(rows)):
            if row == pivot_row or not rows[row][column]:
                continue
            multiple = rows[row][column]
            rows[row] = [left - multiple * right
                         for left, right in zip(rows[row], rows[pivot_row])]
        pivots.append(column)
        pivot_row += 1
        if pivot_row == len(rows):
            break
    return rows, pivots


def nullspace(matrix, reverse_columns=False):
    reduced, pivots = echelon(matrix, reverse_columns=reverse_columns)
    columns = len(matrix[0])
    free = [column for column in range(columns) if column not in pivots]
    basis = []
    for free_column in free:
        vector = [Fraction(0)] * columns
        vector[free_column] = 1
        for row, pivot in enumerate(pivots):
            vector[pivot] = -reduced[row][free_column]
        assert all(sum(Fraction(value) * coordinate
                       for value, coordinate in zip(matrix_row, vector)) == 0
                   for matrix_row in matrix)
        basis.append(tuple(vector))
    return tuple(basis), len(pivots)


def solve_linear(coefficients, targets, reverse_columns=True):
    augmented = [list(row) + [target]
                 for row, target in zip(coefficients, targets)]
    reduced, pivots = echelon(
        augmented, reverse_columns=reverse_columns, augmented=True
    )
    variables = len(coefficients[0]) if coefficients else 0
    inconsistent = any(
        all(value == 0 for value in row[:variables]) and row[variables] != 0
        for row in reduced
    )
    if inconsistent:
        return {"consistent": False, "rank": len(pivots), "dimension": None}
    dimension = variables - len(pivots)
    result = {"consistent": True, "rank": len(pivots), "dimension": dimension}
    if dimension == 0:
        solution = [Fraction(0)] * variables
        for row, pivot in enumerate(pivots):
            solution[pivot] = reduced[row][variables]
        result["solution"] = tuple(solution)
    return result


def determinant(matrix):
    rows = [list(map(Fraction, row)) for row in matrix]
    answer = Fraction(1)
    for column in range(len(rows)):
        pivot = next((row for row in range(column, len(rows))
                      if rows[row][column]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != column:
            rows[column], rows[pivot] = rows[pivot], rows[column]
            answer = -answer
        value = rows[column][column]
        answer *= value
        for row in range(column + 1, len(rows)):
            if not rows[row][column]:
                continue
            multiple = rows[row][column] / value
            for later in range(column + 1, len(rows)):
                rows[row][later] -= multiple * rows[column][later]
    return answer


def principal_minor_test(matrix):
    minimum = None
    for size in range(1, len(matrix) + 1):
        for subset in itertools.combinations(range(len(matrix)), size):
            minor = [[matrix[row][column] for column in subset]
                     for row in subset]
            value = determinant(minor)
            minimum = value if minimum is None else min(minimum, value)
            if value < 0:
                return False, minimum, subset
    return True, minimum if minimum is not None else Fraction(0), None


def incidence_kernel_dimension_combinatorial(supports):
    """Rank of a signless graph incidence matrix, component by component."""

    graph = defaultdict(set)
    for first, second in supports:
        graph[first].add(second)
        graph[second].add(first)
    visited = set()
    rank = 0
    for start in graph:
        if start in visited:
            continue
        queue = deque([start])
        color = {start: 0}
        component = []
        bipartite = True
        while queue:
            vertex = queue.popleft()
            if vertex in visited:
                continue
            visited.add(vertex)
            component.append(vertex)
            for other in graph[vertex]:
                if other not in color:
                    color[other] = 1 - color[vertex]
                    queue.append(other)
                elif color[other] == color[vertex]:
                    bipartite = False
        rank += len(component) - int(bipartite)
    return len(supports) - rank


def analyze_independently(exceptional):
    supports = tuple(tuple(map(int, item["support"])) for item in exceptional)
    deficits = tuple(int(item["deficit"]) for item in exceptional)
    assert len(supports) == len(set(supports))
    assert all(0 <= first < second <= 6 for first, second in supports)
    incidence_transpose = [
        [int(group in support) for support in supports] for group in range(7)
    ]
    basis, incidence_rank = nullspace(
        incidence_transpose, reverse_columns=True
    )
    dimension = len(basis)
    assert dimension == len(supports) - incidence_rank
    assert dimension == incidence_kernel_dimension_combinatorial(supports)
    W = [[basis[column][row] for column in range(dimension)]
         for row in range(len(supports))]

    pairs = tuple((left, right)
                  for left in range(dimension - 1, -1, -1)
                  for right in range(dimension - 1, left - 1, -1))
    # The reversed triangular order still lists every symmetric parameter once.
    assert len(pairs) == dimension * (dimension + 1) // 2
    assert len(set(tuple(sorted(pair)) for pair in pairs)) == len(pairs)
    coefficients = []
    for row in W:
        coefficients.append(tuple(
            row[left] * row[right] * (1 if left == right else 2)
            for left, right in pairs
        ))
    status = solve_linear(coefficients, tuple(2 * value for value in deficits))
    result = {
        "support_count": len(supports),
        "kernel_dimension": dimension,
        "parameter_count": len(pairs),
        "consistent": status["consistent"],
        "rank": status["rank"],
        "solution_dimension": status["dimension"],
    }
    if "solution" in status:
        H = [[Fraction(0)] * dimension for _ in range(dimension)]
        for value, (left, right) in zip(status["solution"], pairs):
            H[left][right] = H[right][left] = value
        psd, minimum, bad = principal_minor_test(H)
        Z = [[
            sum((W[i][left] * H[left][right] * W[j][right]
                 for left in range(dimension) for right in range(dimension)),
                Fraction(0))
            for j in range(len(supports))
        ] for i in range(len(supports))]
        assert [Z[index][index] for index in range(len(supports))] \
            == [2 * value for value in deficits]
        assert all(sum(Z[row][column] * int(group in supports[column])
                       for column in range(len(supports))) == 0
                   for row in range(len(supports)) for group in range(7))
        result.update({"H": H, "Z": Z, "psd": psd,
                       "minimum_minor": minimum, "bad_subset": bad})
    result["passes"] = status["consistent"] and result.get("psd", True)
    return result


def main() -> None:
    raw_input = INPUT.read_bytes()
    source = json.loads(raw_input)
    produced = json.loads(FILTER_OUTPUT.read_text(encoding="utf-8"))
    assert source["status"] == produced["status"] == "COMPLETE"
    assert source["Q_condition"] == "Q>=2"
    assert source["schema_compatibility"] \
        == "legacy Q_at_least_4 field names mean the configured E71 threshold Q>=2"
    assert produced["input"] == str(INPUT)
    assert produced["input_sha256"] == hashlib.sha256(raw_input).hexdigest().upper()
    assert len(source["rows"]) == len(produced["rows"]) == 3220
    assert source["coverage"]["positive_support_rows_copied"] == 3220
    assert source["coverage"]["state_tuples_copied_exactly"] == 599_222

    input_assignments = 0
    passing_assignments = 0
    passing_weight = 0
    inconsistent_assignments = 0
    nonpsd_assignments = 0
    kernel_histogram = Counter()
    dimension_histogram = Counter()
    outcome_histogram = Counter()
    partition_stats = defaultdict(Counter)
    unique_Z_checks = 0
    conventional_H_checks = 0
    source_indices = set()

    for normalized_index, (row, stored) in enumerate(
        zip(source["rows"], produced["rows"])
    ):
        source_index = int(row["source_row_index"])
        assert source_index not in source_indices
        source_indices.add(source_index)
        assignments = int(row["locally_port_feasible_assignments"])
        assert assignments == row["locally_port_feasible_Q_at_least_4_assignments"]
        assert assignments == len(row["feasible_state_indices"])
        assert assignments == len(row["Q_by_feasible_state"])
        assert all(int(value) >= 2 for value in row["Q_by_feasible_state"])
        input_assignments += assignments

        independent_result = analyze_independently(row["exceptional_supports"])
        assert stored["normalized_row_index"] == normalized_index
        assert stored["source_row_index"] == source_index
        assert stored["partition"] == row["partition"]
        assert stored["compression_orbit_index"] == row["compression_orbit_index"]
        assert stored["support_orbit_size"] == row["support_orbit_size"]
        assert stored["port_feasible_state_assignments"] == assignments
        assert stored["exceptional_support_count"] \
            == independent_result["support_count"]
        assert stored["unsigned_incidence_kernel_dimension"] \
            == independent_result["kernel_dimension"]
        assert stored["gram_parameter_count"] \
            == independent_result["parameter_count"]
        assert stored["gram_diagonal_system_consistent"] \
            == independent_result["consistent"]
        assert stored["gram_diagonal_solution_dimension"] \
            == independent_result["solution_dimension"]
        if independent_result["consistent"]:
            assert stored["gram_diagonal_system_rank"] == independent_result["rank"]
        else:
            assert stored["gram_diagonal_system_rank"] is None
        assert stored["passes_exact_support_diagonal_psd_test"] \
            == independent_result["passes"]

        kernel_histogram[independent_result["kernel_dimension"]] += 1
        if independent_result["solution_dimension"] is not None:
            dimension_histogram[independent_result["solution_dimension"]] += 1

        if "Z" in independent_result:
            stored_Z = [[Fraction(value) for value in matrix_row]
                        for matrix_row in stored["unique_Z_matrix"]]
            assert stored_Z == independent_result["Z"]
            assert stored["unique_gram_parameter_matrix_psd"] \
                == independent_result["psd"]
            unique_Z_checks += 1

            # Verify the producer's stored H in its conventional left-pivot
            # coordinate basis, without using the producer's implementation.
            supports = tuple(tuple(item["support"])
                             for item in row["exceptional_supports"])
            incidence_t = [[int(group in support) for support in supports]
                           for group in range(7)]
            conventional_basis, _ = nullspace(
                incidence_t, reverse_columns=False
            )
            conventional_W = [[conventional_basis[column][support_index]
                               for column in range(len(conventional_basis))]
                              for support_index in range(len(supports))]
            stored_H = [[Fraction(value) for value in matrix_row]
                        for matrix_row in stored["unique_gram_parameter_matrix"]]
            rebuilt_Z = [[
                sum((conventional_W[i][left] * stored_H[left][right]
                     * conventional_W[j][right]
                     for left in range(len(stored_H))
                     for right in range(len(stored_H))), Fraction(0))
                for j in range(len(supports))
            ] for i in range(len(supports))]
            assert rebuilt_Z == stored_Z
            psd, minimum, bad = principal_minor_test(stored_H)
            assert psd == stored["unique_gram_parameter_matrix_psd"]
            assert str(minimum) == stored["minimum_checked_principal_minor"]
            assert (None if bad is None else list(bad)) \
                == stored["first_negative_principal_minor_subset"]
            conventional_H_checks += 1

        partition = tuple(map(int, row["partition"]))
        if independent_result["passes"]:
            passing_assignments += assignments
            passing_weight += int(row["support_orbit_size"])
            outcome = "passing"
        elif not independent_result["consistent"]:
            inconsistent_assignments += assignments
            outcome = "inconsistent"
        else:
            assert independent_result.get("psd") is False
            nonpsd_assignments += assignments
            outcome = "unique_non_psd"
        outcome_histogram[outcome] += 1
        partition_stats[partition][outcome + "_rows"] += 1
        partition_stats[partition][outcome + "_assignments"] += assignments

    assert len(source_indices) == 3220
    assert input_assignments == 599_222
    assert passing_assignments == 361_900
    assert inconsistent_assignments + nonpsd_assignments \
        == input_assignments - passing_assignments == 237_322
    assert outcome_histogram == Counter({
        "inconsistent": 1660,
        "passing": 1512,
        "unique_non_psd": 48,
    })
    assert passing_weight == 6_246_975
    assert unique_Z_checks == conventional_H_checks \
        == dimension_histogram[0] == 233

    summary = produced["summary"]
    assert summary["input_support_rows"] == 3220
    assert summary["input_port_feasible_state_assignments"] == input_assignments
    assert summary["inconsistent_diagonal_systems"] == 1660
    assert summary["unique_but_non_psd_systems"] == 48
    assert summary["passing_support_rows"] == 1512
    assert summary["passing_port_feasible_state_assignments"] \
        == passing_assignments
    assert summary["passing_support_labelled_weight"] == passing_weight
    assert summary["kernel_dimension_histogram"] \
        == {str(key): value for key, value in sorted(kernel_histogram.items())}
    assert summary["solution_dimension_histogram"] \
        == {str(key): value for key, value in sorted(dimension_histogram.items())}

    result = {
        "status": "E71_UNSIGNED_KERNEL_INDEPENDENT_AUDIT_PASS",
        "Q_condition": "Q>=2",
        "legacy_schema_note": source["schema_compatibility"],
        "inputs": {str(path): sha256(path)
                   for path in (INPUT, FILTER_SCRIPT, FILTER_OUTPUT, THEORY)},
        "coverage": {
            "input_support_rows": 3220,
            "input_port_feasible_state_assignments": input_assignments,
            "passing_support_rows": 1512,
            "passing_port_feasible_state_assignments": passing_assignments,
            "rejected_support_rows": 1708,
            "rejected_port_feasible_state_assignments": 237_322,
            "passing_support_labelled_weight": passing_weight,
        },
        "rejection_breakdown": {
            "inconsistent_diagonal_system_rows": 1660,
            "inconsistent_diagonal_system_assignments": inconsistent_assignments,
            "unique_non_PSD_rows": 48,
            "unique_non_PSD_assignments": nonpsd_assignments,
        },
        "independent_method": {
            "primary_kernel_basis": "exact Fraction elimination with right-to-left pivots",
            "kernel_dimension_also_checked_by": (
                "signless-incidence component rank: |V|-1 for bipartite and "
                "|V| for non-bipartite components"
            ),
            "diagonal_system": "independent right-pivot exact solve",
            "unique_invariant_Z_matrices_matched": unique_Z_checks,
            "stored_left_basis_H_matrices_checked": conventional_H_checks,
            "PSD_test": "all principal minors over Fraction",
            "kernel_dimension_histogram": {
                str(key): value for key, value in sorted(kernel_histogram.items())
            },
            "solution_dimension_histogram": {
                str(key): value for key, value in sorted(dimension_histogram.items())
            },
        },
        "by_partition": {
            str(partition): dict(sorted(stats.items()))
            for partition, stats in sorted(partition_stats.items(), reverse=True)
        },
        "soundness": (
            "For every realizable row, PSD Z with ZL=0 restricts on positive-"
            "deficit supports to Z=W H W^T with H PSD and diagonal 2*delta. "
            "An inconsistent diagonal system is impossible. If the system has "
            "a unique H and it is non-PSD, it is also impossible. Every "
            "consistent underdetermined system is retained, so no numerical or "
            "unproved semidefinite infeasibility is used."
        ),
        "claim_boundary": (
            "This exact support-only necessary filter reduces E71,Q>=2 from "
            "3,220 to 1,512 support rows and from 599,222 to 361,900 port-state "
            "tuples. Passing does not supply off-diagonal block totals, a local "
            "graph, or an srg(99,14,1,2), and the executable audit is not a "
            "proof-assistant certificate."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text("\n".join([
        "# E71 unsigned-kernel filter independent audit",
        "",
        "Status: **E71_UNSIGNED_KERNEL_INDEPENDENT_AUDIT_PASS**.",
        "",
        "The E71 `Q>=2` input contains 3,220 positive support rows and 599,222 "
        "port-feasible state tuples. The legacy `Q_at_least_4` field names in "
        "this pipeline mean the configured E71 threshold `Q>=2`.",
        "",
        "A separate exact implementation, using right-to-left rational pivots "
        "and a combinatorial signless-incidence rank check, reproduces 1,660 "
        "inconsistent diagonal systems and 48 uniquely forced non-PSD systems. "
        "Thus 1,512 rows / 361,900 tuples remain; 1,708 rows / 237,322 tuples "
        "are rejected. All 233 unique invariant `Z` matrices and the producer's "
        "stored coordinate `H` matrices were checked by exact principal minors.",
        "",
        "Soundness boundary: underdetermined consistent Gram systems are always "
        "retained. This is a support-only necessary condition, not an E71 "
        "exclusion, graph construction, or proof-assistant certificate.",
        "",
    ]), encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "input_rows": 3220,
        "passing_rows": 1512,
        "input_states": 599_222,
        "passing_states": 361_900,
        "unique_Z_checks": unique_Z_checks,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
