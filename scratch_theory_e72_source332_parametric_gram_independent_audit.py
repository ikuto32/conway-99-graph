"""Independent exact audit of the source-332 one-parameter Gram family."""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path


OUTPUT = Path("scratch_theory_e72_source332_parametric_gram_independent_audit.json")
NOTE = Path("scratch_theory_e72_source332_parametric_gram_independent.md")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def padd(left, right):
    size = max(len(left), len(right))
    return tuple(
        (left[index] if index < len(left) else 0)
        + (right[index] if index < len(right) else 0)
        for index in range(size)
    )


def pmul(left, right):
    answer = [0] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            answer[i + j] += a * b
    return tuple(answer)


def determinant(matrix):
    size = len(matrix)
    answer = 0
    for permutation in itertools.permutations(range(size)):
        inversions = sum(
            permutation[i] > permutation[j]
            for i in range(size) for j in range(i + 1, size)
        )
        term = 1
        for row, column in enumerate(permutation):
            term *= matrix[row][column]
        answer += (-1 if inversions % 2 else 1) * term
    return answer


def psd_by_principal_minors(matrix):
    size = len(matrix)
    minors = []
    for width in range(1, size + 1):
        for subset in itertools.combinations(range(size), width):
            value = determinant([[matrix[i][j] for j in subset] for i in subset])
            minors.append((subset, value))
    return all(value >= 0 for _subset, value in minors), minors


def H_at(t):
    return [
        [2, -1, 0, -t],
        [-1, 2, t, 0],
        [0, t, 2, -1],
        [-t, 0, -1, 2],
    ]


def polynomial_square_audit():
    # Polynomial entries are coefficient tuples in increasing powers of t.
    zero, one, minus_one, t, minus_t = (0,), (1,), (-1,), (0, 1), (0, -1)
    K = [
        [zero, minus_one, zero, minus_t],
        [minus_one, zero, t, zero],
        [zero, t, zero, minus_one],
        [minus_t, zero, minus_one, zero],
    ]
    square = []
    for i in range(4):
        row = []
        for j in range(4):
            value = (0,)
            for k in range(4):
                value = padd(value, pmul(K[i][k], K[k][j]))
            while len(value) > 1 and value[-1] == 0:
                value = value[:-1]
            row.append(value)
        square.append(row)
    expected = [[(1, 0, 1) if i == j else (0,) for j in range(4)] for i in range(4)]
    assert square == expected
    return square


def main():
    square = polynomial_square_audit()
    # The simultaneous range constraints 0<=3+t and 0<=3-t imply |t|<=3.
    cases = []
    feasible = []
    for t in range(-3, 4):
        blocks = [3 + t, 3 - t, 4 + t, 4 - t]
        in_range = all(0 <= value <= 16 for value in blocks)
        psd, minors = psd_by_principal_minors(H_at(t))
        record = {
            "t": t,
            "representative_disjoint_block_totals": blocks,
            "in_range": in_range,
            "psd_by_all_principal_minors": psd,
            "minimum_principal_minor": min(value for _subset, value in minors),
        }
        cases.append(record)
        if in_range and psd:
            feasible.append(t)
    assert feasible == [-1, 0, 1]
    result = {
        "status": "INDEPENDENT_EXACT_VERIFIED",
        "scope": "last-step discretization of the displayed source-332 H(t) family",
        "K_square_polynomial_matrix": [
            [[*entry] for entry in row] for row in square
        ],
        "eigenvalues_of_H": "2+sqrt(1+t^2) twice; 2-sqrt(1+t^2) twice",
        "PSD_condition": "t^2<=3",
        "integer_cases_from_3_plus_or_minus_t_range": cases,
        "feasible_parameters": feasible,
        "note_sha256": sha256(NOTE),
        "audit_script_sha256": sha256(Path(__file__)),
        "claim_boundary": (
            "The affine family and block forms are premises displayed in the note; "
            "this independent script audits their PSD/integrality consequence."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "feasible_parameters": feasible}))


if __name__ == "__main__":
    main()
