"""Exact coefficient audit for the two rooted cycle residual projectors.

This is a theorem-level arithmetic check.  It does not enumerate an E0
layer or any of the frozen order-eight classes.  For the 84 exact-label
edges of K14-7K2 it reconstructs the cycle projector H and checks the
off-diagonal coefficients used by the -4 and +3 residual projectors.

If B_xy is binary and

    G4_xy = a_xy - 16 B_xy,
    G3_xy = b_xy + 240 B_xy,

then diagonal idempotence of the two scaled projectors, and their mutual
orthogonality, become three linear weighted-degree equations.  The script
checks all fixed rational coefficients and the three binary linearizations.
"""

from __future__ import annotations

from fractions import Fraction
import hashlib
import itertools
import json
import os
from pathlib import Path


OUTPUT = Path("scratch_theory_cycle_residual_projector_hierarchy.json")
SUPPORTS = tuple(itertools.combinations(range(7), 2))
LABELS = tuple(
    (2 * support[0] + local // 2, 2 * support[1] + local % 2)
    for support in SUPPORTS for local in range(4)
)


def atomic_json(path: Path, value) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def transpose(matrix):
    return [list(column) for column in zip(*matrix)]


def matmul(left, right):
    right_t = transpose(right)
    return [
        [sum(a * b for a, b in zip(row, column)) for column in right_t]
        for row in left
    ]


def identity(size):
    return [[Fraction(int(i == j)) for j in range(size)] for i in range(size)]


def matrix_equal(left, right):
    return all(a == b for row_l, row_r in zip(left, right)
               for a, b in zip(row_l, row_r))


def main() -> None:
    # Unsigned endpoint incidence of the 84 edges of K14-7K2.
    incidence = [
        [Fraction(int(vertex in label)) for vertex in range(14)]
        for label in LABELS
    ]
    gram_inverse = [
        [
            Fraction(11 * int(i == j), 120)
            - Fraction(1, 240)
            + Fraction(int(i == (j ^ 1)), 120)
            for j in range(14)
        ]
        for i in range(14)
    ]
    gram = matmul(transpose(incidence), incidence)
    assert matrix_equal(matmul(gram, gram_inverse), identity(14))

    incidence_projection = matmul(matmul(incidence, gram_inverse), transpose(incidence))
    h = [
        [Fraction(int(i == j)) - incidence_projection[i][j] for j in range(84)]
        for i in range(84)
    ]
    assert matrix_equal(matmul(h, h), h)
    assert all(h[i][i] == Fraction(5, 6) for i in range(84))
    assert sum(h[i][i] for i in range(84)) == 70

    relation_histogram = {}
    for left, right in itertools.combinations(range(84), 2):
        q = len(set(LABELS[left]) & set(LABELS[right]))
        d = sum((value ^ 1) in LABELS[right] for value in LABELS[left])
        key = f"q{q}_d{d}"
        relation_histogram[key] = relation_histogram.get(key, 0) + 1

        # Direct coordinate formula for the cycle projector.
        assert h[left][right] == Fraction(2 - 11 * q - d, 120)

        # From BL=2J-L(I+mate), (I-H)B has the following fixed entry.
        fb = Fraction(2 - q - d, 10)
        for adjacency in (0, 1):
            # E4=H(3I-B)/7 and E3=H-E4, for distinct coordinates.
            e4 = (3 * h[left][right] - (adjacency - fb)) / 7
            e3 = h[left][right] - e4
            assert 112 * e4 == 4 - 6 * q - 2 * d - 16 * adjacency
            assert 1680 * e3 == -32 - 64 * q + 16 * d + 240 * adjacency

    # The fixed diagonals and the chosen integral scales.
    assert 112 * Fraction(5, 14) == 40
    assert 1680 * Fraction(10, 21) == 800

    # Binary linearizations.  Fractions deliberately exercise denominators.
    samples = (
        (Fraction(-17, 3), Fraction(29, 5)),
        (Fraction(0), Fraction(0)),
        (Fraction(41, 7), Fraction(-83, 11)),
    )
    for a, b in samples:
        for edge in (0, 1):
            g4 = a - 16 * edge
            g3 = b + 240 * edge
            assert g4 * g4 == a * a + 32 * edge * (8 - a)
            assert g3 * g3 == b * b + 480 * edge * (b + 120)
            assert g4 * g3 == a * b + edge * (240 * a - 16 * b - 3840)

    script_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest().upper()
    result = {
        "status": "CYCLE_RESIDUAL_PROJECTOR_COEFFICIENT_AUDIT_PASS",
        "scope": (
            "Theorem-level exact arithmetic only; no E0-layer census, "
            "order-eight regeneration, graph construction, or submission."
        ),
        "script_sha256": script_hash,
        "fixed_geometry": {
            "coordinates": 84,
            "cycle_projector_rank": 70,
            "cycle_projector_diagonal": "5/6",
            "relation_histogram": relation_histogram,
            "inverse_endpoint_gram": "11I/120-J/240+mate/120",
        },
        "minus4": {
            "projector": "E4=H(3I-B)/7",
            "coordinate_diagonal": "5/14",
            "scale": 112,
            "residual_diagonal": "g_x=40-s_x Z^+ s_x",
            "residual_off_diagonal": (
                "G4_xy=a_xy-16B_xy; "
                "a_xy=4-6q_xy-2d_xy-s_x Z^+ s_y"
            ),
            "diagonal_idempotence": (
                "sum_{y~x}(8-a_xy)="
                "(112g_x-g_x^2-sum_{y!=x}a_xy^2)/32"
            ),
        },
        "plus3": {
            "projector": "E3=H-E4=H(4I+B)/7",
            "coordinate_diagonal": "10/21",
            "scale": 1680,
            "coarse_denominator": "D=28K-Z",
            "coarse_row": "t_x=28K_G-Z_G+r_x",
            "residual_diagonal": "h_x=800-15t_x D^+ t_x",
            "residual_off_diagonal": (
                "G3_xy=b_xy+240B_xy; "
                "b_xy=-32-64q_xy+16d_xy-15t_x D^+ t_y"
            ),
            "diagonal_idempotence": (
                "sum_{y~x}(b_xy+120)="
                "(1680h_x-h_x^2-sum_{y!=x}b_xy^2)/480"
            ),
        },
        "cross": {
            "orthogonality": "G4 G3=0",
            "diagonal_linearization": (
                "sum_{y~x}(240a_xy-16b_xy-3840)="
                "-g_x h_x-sum_{y!=x}a_xy b_xy"
            ),
        },
        "dependency_warning": (
            "E3=H-E4 and HE4=E4 imply E3^2-E3=E4^2-E4 and "
            "E4E3=-(E4^2-E4).  After the coarse Gram and strong "
            "cross-block transport equations, the three residual diagonal "
            "rows may be equivalent; no extra exclusion is credited here."
        ),
        "binary_linearizations_checked": 6,
        "submission_txt_written": False,
    }
    atomic_json(OUTPUT, result)
    print(json.dumps({
        "path": str(OUTPUT),
        "status": result["status"],
        "relation_histogram": relation_histogram,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
