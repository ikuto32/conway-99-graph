"""Self-contained exact audit of the selected-root E0=75 exclusion.

The mathematical argument is documented in ``scratch_theory_gram_circulation.md``.
This audit deliberately does not read any earlier compression/SAT artifact.  It
enumerates every labelled placement on the 21 edges of K7 for the only three
deficit multisets capable of Q>=6, and applies exact Fraction linear algebra to
the Gram-circulation diagonal equations.
"""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path

from scratch_theory_unsigned_kernel_filter import analyze_support


OUTPUT = Path("scratch_theory_e75_gram_audit.json")
SUPPORTS = tuple(itertools.combinations(range(7), 2))
PATTERNS = (
    (3, 2, 2, 2),
    (2, 2, 2, 2, 1),
    (2, 2, 2, 1, 1, 1),
)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def unique_assignments(pattern):
    """All distinct orderings of a small multiset, without set-order reliance."""
    counts = Counter(pattern)

    def visit(prefix):
        if len(prefix) == len(pattern):
            yield tuple(prefix)
            return
        for value in sorted(counts, reverse=True):
            if not counts[value]:
                continue
            counts[value] -= 1
            yield from visit(prefix + [value])
            counts[value] += 1

    yield from visit([])


def q_capacity(pattern):
    return 2 * pattern.count(2) + pattern.count(3)


def labelled_count(pattern):
    m = len(pattern)
    answer = 1
    for value in range(21 - m + 1, 22):
        answer *= value
    for multiplicity in Counter(pattern).values():
        for value in range(2, multiplicity + 1):
            answer //= value
    return answer


def no_degree_one(chosen):
    degrees = [0] * 7
    for index in chosen:
        for group in SUPPORTS[index]:
            degrees[group] += 1
    return all(value != 1 for value in degrees)


def audit_pattern(pattern):
    orderings = tuple(unique_assignments(pattern))
    tested = 0
    degree_one_rejected = 0
    exact_tested = 0
    consistent = 0
    kernel_histogram = Counter()
    support_subsets = 0
    support_subsets_without_degree_one = 0
    for chosen in itertools.combinations(range(21), len(pattern)):
        support_subsets += 1
        good_degree = no_degree_one(chosen)
        if good_degree:
            support_subsets_without_degree_one += 1
        for assignment in orderings:
            tested += 1
            if not good_degree:
                degree_one_rejected += 1
                continue
            exceptional = [
                {"support": list(SUPPORTS[index]), "deficit": deficit}
                for index, deficit in zip(chosen, assignment)
            ]
            result = analyze_support(exceptional)
            exact_tested += 1
            kernel_histogram[result["unsigned_incidence_kernel_dimension"]] += 1
            if result["passes_exact_support_diagonal_psd_test"]:
                consistent += 1
    expected = labelled_count(pattern)
    assert tested == expected
    assert degree_one_rejected + exact_tested == tested
    assert consistent == 0
    return {
        "deficit_multiset": list(pattern),
        "Q_capacity": q_capacity(pattern),
        "support_subsets": support_subsets,
        "support_subsets_without_degree_one": support_subsets_without_degree_one,
        "distinct_weight_assignments_per_subset": len(orderings),
        "labelled_weighted_placements": tested,
        "rejected_immediately_by_degree_one": degree_one_rejected,
        "exact_gram_diagonal_systems_tested": exact_tested,
        "kernel_dimension_histogram_on_exact_tests": {
            str(key): value for key, value in sorted(kernel_histogram.items())
        },
        "PSD_compatible_placements": consistent,
    }


def verify_projector_entries():
    # L^T L = 5I+J, so (L^T L)^-1=I/5-J/60.  If two K7 edges
    # meet in c groups, P_U(F,G)=c/5-1/15 and P_1(F,G)=1/21.
    rows = []
    for common_groups in (0, 1, 2):
        p_u = Fraction(common_groups, 5) - Fraction(1, 15)
        p_const = Fraction(1, 21)
        p_centered = p_u - p_const
        correction = 9 * p_const - 5 * p_centered
        assert correction == 1 - common_groups
        rows.append({
            "common_support_groups": common_groups,
            "P_U_entry": str(p_u),
            "P_centered_entry": str(p_centered),
            "9P_const_minus_5P_centered": str(correction),
        })
    return rows


def enumerate_q_capable_partitions():
    # A deficit-d fibre has Q capacity 0,0,2,1,0 for d=0,1,2,3,4.
    partitions = []

    def visit(remaining, ceiling, prefix):
        if not remaining:
            partitions.append(tuple(prefix))
            return
        for value in range(min(ceiling, remaining, 4), 0, -1):
            visit(remaining - value, value, prefix + [value])

    visit(9, 4, [])
    capable = tuple(pattern for pattern in partitions if q_capacity(pattern) >= 6)
    assert capable == PATTERNS
    return {
        "all_deficit_9_partitions": len(partitions),
        "Q_at_least_6_capable_partitions": [list(value) for value in capable],
    }


def main():
    rows = [audit_pattern(pattern) for pattern in PATTERNS]
    result = {
        "status": "EXACT_ARITHMETIC_VERIFIED",
        "model": "selected-root E0=75 exclusion by PSD Gram circulation",
        "external_artifacts_read": [],
        "projector_entry_check": verify_projector_entries(),
        "fibre_Q_capacity": {
            "delta_0": 0,
            "delta_1": 0,
            "delta_2": 2,
            "delta_3": 1,
            "delta_4": 0,
        },
        "partition_check": enumerate_q_capable_partitions(),
        "rows": rows,
        "totals": {
            "labelled_weighted_placements": sum(row["labelled_weighted_placements"] for row in rows),
            "exact_gram_diagonal_systems_tested": sum(row["exact_gram_diagonal_systems_tested"] for row in rows),
            "PSD_compatible_placements": sum(row["PSD_compatible_placements"] for row in rows),
        },
        "conclusion": (
            "For a root with S<=69, E0=75 would force Q>=6.  Every one of "
            "the three Q-capable deficit patterns violates the necessary exact "
            "PSD Gram-circulation diagonal equations; hence that selected-root "
            "branch is impossible."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    result["audit_script_sha256"] = sha256(Path(__file__))
    # Store the script hash in a second atomic-looking final rewrite so the JSON
    # binds the implementation that produced it, without self-hashing the JSON.
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["totals"], sort_keys=True))


if __name__ == "__main__":
    main()
