"""Exact row-candidate backtracking for the semiregular-C11 quotient.

This is independent of the CNF bit blasting.  Once the diagonal distribution
and row zero are fixed, every other complete row comes from one of seven
small multisets.  Two candidate rows are compatible exactly when symmetry
and the off-diagonal entry of ``B^2+B=12I+22J`` both hold.  A quotient matrix
is therefore a coloured clique containing one row of each colour 1..8.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import time
from collections import Counter
from functools import lru_cache
from pathlib import Path

from scratch_root_c11_quotient_sat import admissible_row_patterns, atomic_json, verify


OUTPUT = Path("scratch_root_c11_quotient_backtrack.json")


DIAGONAL_CASES = (
    (4, 4, 2, 0, 0, 0, 0, 0, 0),
    (4, 2, 2, 2, 0, 0, 0, 0, 0),
    (2, 2, 2, 2, 2, 0, 0, 0, 0),
)


@lru_cache(maxsize=None)
def distinct_permutations(values: tuple[int, ...]) -> tuple[tuple[int, ...], ...]:
    """Generate unique multiset permutations without materializing duplicates."""

    counts = Counter(values)
    keys = tuple(sorted(counts))
    result = []
    work: list[int] = []

    def visit() -> None:
        if len(work) == len(values):
            result.append(tuple(work))
            return
        for value in keys:
            if counts[value]:
                counts[value] -= 1
                work.append(value)
                visit()
                work.pop()
                counts[value] += 1

    visit()
    return tuple(result)


@lru_cache(maxsize=None)
def rows_for(position: int, diagonal: int) -> tuple[tuple[int, ...], ...]:
    answer = []
    patterns = admissible_row_patterns()[diagonal]
    for pattern in patterns:
        for offdiagonal in distinct_permutations(pattern):
            row = list(offdiagonal)
            row.insert(position, diagonal)
            row = tuple(row)
            assert sum(row) == 14
            assert sum(value * value for value in row) + diagonal == 34
            answer.append(row)
    assert len(answer) == len(set(answer))
    return tuple(answer)


def row_zero_candidates(diagonal: tuple[int, ...]) -> tuple[tuple[int, ...], ...]:
    """Use only safe orbit relabelling: sort B[0,j] inside diagonal classes."""

    answer = []
    for row in rows_for(0, diagonal[0]):
        if any(row[j] < row[j + 1] for j in range(1, 8) if diagonal[j] == diagonal[j + 1]):
            continue
        answer.append(row)
    return tuple(answer)


def compatible(left_index: int, left: tuple[int, ...], right_index: int,
               right: tuple[int, ...]) -> bool:
    return (
        left[right_index] == right[left_index]
        and sum(a * b for a, b in zip(left, right)) + left[right_index] == 22
    )


def solve(max_nodes: int | None = None, stop_after_first: bool = True) -> dict:
    started = time.monotonic()
    nodes = 0
    pair_tests = 0
    first_rows = 0
    empty_domains = 0
    solutions = []
    case_records = []
    stopped = False

    for case_number, diagonal in enumerate(DIAGONAL_CASES):
        case_started = time.monotonic()
        case_nodes_before = nodes
        case_first = 0
        case_solutions_before = len(solutions)
        for row_zero in row_zero_candidates(diagonal):
            first_rows += 1
            case_first += 1
            candidates: dict[int, tuple[tuple[int, ...], ...]] = {}
            impossible = False
            for index in range(1, 9):
                rows = tuple(
                    row for row in rows_for(index, diagonal[index])
                    if row[0] == row_zero[index]
                    and sum(a * b for a, b in zip(row_zero, row)) + row_zero[index] == 22
                )
                candidates[index] = rows
                if not rows:
                    impossible = True
                    empty_domains += 1
                    break
            if impossible:
                continue

            chosen: dict[int, tuple[int, ...]] = {0: row_zero}

            def visit(active: dict[int, tuple[tuple[int, ...], ...]]) -> bool:
                nonlocal nodes, pair_tests, stopped
                if max_nodes is not None and nodes >= max_nodes:
                    stopped = True
                    return True
                if not active:
                    matrix = [chosen[i] for i in range(9)]
                    verify(matrix)
                    solutions.append([list(row) for row in matrix])
                    return stop_after_first

                # Fail first: materialize compatibility with all chosen rows
                # for every colour, then branch on the smallest domain.
                filtered: dict[int, tuple[tuple[int, ...], ...]] = {}
                best_index = None
                best_rows = None
                for index, rows in active.items():
                    valid = []
                    for row in rows:
                        ok = True
                        for other_index, other in chosen.items():
                            pair_tests += 1
                            if not compatible(other_index, other, index, row):
                                ok = False
                                break
                        if ok:
                            valid.append(row)
                    if not valid:
                        return False
                    filtered[index] = tuple(valid)
                    if best_rows is None or len(valid) < len(best_rows):
                        best_index = index
                        best_rows = valid
                assert best_index is not None and best_rows is not None

                remainder = {
                    index: rows for index, rows in filtered.items()
                    if index != best_index
                }
                for row in best_rows:
                    nodes += 1
                    chosen[best_index] = row
                    if visit(remainder):
                        return True
                    del chosen[best_index]
                return False

            if visit(candidates):
                break
        case_records.append({
            "case_number": case_number,
            "diagonal": list(diagonal),
            "canonical_row_zero_candidates": case_first,
            "nodes": nodes - case_nodes_before,
            "solutions": len(solutions) - case_solutions_before,
            "seconds": round(time.monotonic() - case_started, 6),
        })
        print(json.dumps(case_records[-1], sort_keys=True), flush=True)
        if stopped or (solutions and stop_after_first):
            break

    status = "SAT" if solutions else "UNKNOWN" if stopped else "UNSAT"
    result = {
        "status": status,
        "model": "complete symmetric integral C11 quotient row-clique census",
        "diagonal_cases": [list(case) for case in DIAGONAL_CASES],
        "row_patterns": {
            str(key): [list(row) for row in value]
            for key, value in admissible_row_patterns().items()
        },
        "safe_symmetry_break": (
            "diagonal nonincreasing; B[0,j] nonincreasing within equal-diagonal "
            "classes among j=1..8"
        ),
        "canonical_row_zero_candidates": first_rows,
        "search_nodes": nodes,
        "pair_compatibility_tests": pair_tests,
        "empty_initial_domains": empty_domains,
        "max_nodes": max_nodes,
        "stop_after_first": stop_after_first,
        "case_records": case_records,
        "solution_count_stored": len(solutions),
        "solutions": solutions,
        "elapsed_seconds": round(time.monotonic() - started, 6),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest().upper(),
        "claim_boundary": (
            "UNSAT is a complete solver-free exclusion of necessary quotient "
            "matrices for the semiregular C11 subclass; SAT is only a quotient."
        ),
    }
    atomic_json(OUTPUT, result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-nodes", type=int)
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args()
    result = solve(args.max_nodes, not args.all)
    print(json.dumps({
        key: result[key]
        for key in (
            "status", "canonical_row_zero_candidates", "search_nodes",
            "pair_compatibility_tests", "solution_count_stored", "elapsed_seconds",
        )
    }, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
