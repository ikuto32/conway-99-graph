"""Check whether the C11 quotient obstruction is already visible modulo two."""

from __future__ import annotations

import itertools
import json
from pathlib import Path

from scratch_root_c11_quotient_backtrack import DIAGONAL_CASES


DEGREES = {4: (6,), 2: (4,), 0: (2, 6)}


def rows(position: int, diagonal: int):
    result = []
    others = [i for i in range(9) if i != position]
    for degree in DEGREES[diagonal]:
        for support in itertools.combinations(others, degree):
            row = [0] * 9
            for value in support:
                row[value] = 1
            result.append(tuple(row))
    return tuple(result)


def compatible(i, left, j, right):
    return left[j] == right[i] and sum(a * b for a, b in zip(left, right)) % 2 == left[j]


def main() -> None:
    total_nodes = 0
    results = []
    for case_index, diagonal in enumerate(DIAGONAL_CASES):
        solutions = 0
        solution_matrices = []
        nodes = 0
        row0s = []
        for row in rows(0, diagonal[0]):
            if any(row[j] < row[j + 1] for j in range(1, 8) if diagonal[j] == diagonal[j + 1]):
                continue
            row0s.append(row)
        for row0 in row0s:
            candidates = {
                i: tuple(row for row in rows(i, diagonal[i]) if compatible(0, row0, i, row))
                for i in range(1, 9)
            }
            chosen = {0: row0}

            def visit(active):
                nonlocal nodes, solutions
                if not active:
                    matrix = [chosen[i] for i in range(9)]
                    # Idempotence and the odd pseudo-determinant force rank 4.
                    solutions += 1
                    solution_matrices.append(matrix)
                    return
                filtered = {}
                for i, candidates_i in active.items():
                    valid = tuple(
                        row for row in candidates_i
                        if all(compatible(j, chosen[j], i, row) for j in chosen)
                    )
                    if not valid:
                        return
                    filtered[i] = valid
                i = min(filtered, key=lambda key: len(filtered[key]))
                remainder = {key: value for key, value in filtered.items() if key != i}
                for row in filtered[i]:
                    nodes += 1
                    chosen[i] = row
                    visit(remainder)
                    del chosen[i]

            visit(candidates)
        total_nodes += nodes
        results.append({
            "case_index": case_index,
            "diagonal": diagonal,
            "canonical_row0": len(row0s),
            "nodes": nodes,
            "labelled_tail_solutions_under_row0_break": solutions,
            "solutions": solution_matrices,
        })
        print(json.dumps(results[-1]), flush=True)
    result = {"total_nodes": total_nodes, "results": results}
    Path("scratch_root_c11_quotient_parity_census.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
