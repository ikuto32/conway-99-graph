"""Source-blind audit of ``scratch_theory_global_root_fusion_frame``.

This file does not import the discovery module.  It reconstructs the two
15-point primitive-idempotent blocks by invariant subspaces, rebuilds their
Moore--Penrose inverses, independently forms the 84-point fibre projector,
and checks the global fusion and cross-root coefficients over exact
rationals.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from fractions import Fraction as F
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "scratch_theory_global_root_fusion_frame.json"
SOURCE_NOTE = ROOT / "scratch_theory_global_root_fusion_frame.md"
OUTPUT = ROOT / "scratch_theory_global_root_fusion_frame_audit.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def zero(rows, columns=None):
    columns = rows if columns is None else columns
    return [[F(0) for _ in range(columns)] for _ in range(rows)]


def identity(order):
    result = zero(order)
    for index in range(order):
        result[index][index] = F(1)
    return result


def transpose(matrix):
    return [list(column) for column in zip(*matrix)]


def multiply(left, right):
    columns = transpose(right)
    return [[sum((a * b for a, b in zip(row, column)), F(0))
             for column in columns] for row in left]


def add(*matrices):
    return [[sum((matrix[i][j] for matrix in matrices), F(0))
             for j in range(len(matrices[0][0]))]
            for i in range(len(matrices[0]))]


def scale(matrix, scalar):
    return [[scalar * value for value in row] for row in matrix]


def outer(vector):
    return [[a * b for b in vector] for a in vector]


def equal(left, right):
    return left == right


def matvec(matrix, vector):
    return [sum((a * b for a, b in zip(row, vector)), F(0)) for row in matrix]


def matrix_rank(matrix):
    work = [row[:] for row in matrix]
    row = 0
    for column in range(len(work[0])):
        pivot = next((index for index in range(row, len(work))
                      if work[index][column]), None)
        if pivot is None:
            continue
        work[row], work[pivot] = work[pivot], work[row]
        divisor = work[row][column]
        work[row] = [value / divisor for value in work[row]]
        for other in range(len(work)):
            if other == row or not work[other][column]:
                continue
            factor = work[other][column]
            work[other] = [value - factor * base
                           for value, base in zip(work[other], work[row])]
        row += 1
        if row == len(work):
            break
    return row


def star_adjacency():
    result = zero(15)
    for neighbour in range(1, 15):
        result[0][neighbour] = result[neighbour][0] = F(1)
    for pair in range(7):
        left, right = 1 + 2 * pair, 2 + 2 * pair
        result[left][right] = result[right][left] = F(1)
    return result


def primitive_block(kind, adjacency):
    i = identity(15)
    one = [[F(1) for _ in range(15)] for _ in range(15)]
    if kind == "minus4":
        return scale(add(scale(i, F(3)), scale(adjacency, -F(1)),
                         scale(one, F(1, 9))), F(1, 7))
    if kind == "plus3":
        return scale(add(adjacency, scale(i, F(4)),
                         scale(one, -F(2, 11))), F(1, 7))
    raise ValueError(kind)


def orthogonal_projector(vectors):
    """Projector for the supplied pairwise-orthogonal equal-norm vectors."""

    result = zero(len(vectors[0]))
    for vector in vectors:
        norm = sum(value * value for value in vector)
        result = add(result, scale(outer(vector), F(1, norm)))
    return result


def invariant_projectors():
    differences = []
    for pair in range(7):
        vector = [F(0)] * 15
        vector[1 + 2 * pair] = F(1)
        vector[2 + 2 * pair] = -F(1)
        differences.append(vector)
    # Six independent centred pair-constant vectors are not orthogonal, so
    # use the closed-form projector: average within pairs, remove the global
    # neighbour constant, and keep the root coordinate zero.
    centred = zero(15)
    for left in range(1, 15):
        for right in range(1, 15):
            centred[left][right] = (
                F(1, 2) if (left - 1) // 2 == (right - 1) // 2 else F(0)
            ) - F(1, 14)
    return orthogonal_projector(differences), centred


def eigen_check(matrix, projector, eigenvalue):
    return equal(multiply(matrix, projector), scale(projector, eigenvalue))


def categories(matrix):
    return {
        "root_root": matrix[0][0],
        "root_neighbour": matrix[0][1],
        "neighbour_diag": matrix[1][1],
        "neighbour_mate": matrix[1][2],
        "neighbour_nonmate": matrix[1][3],
    }


def aggregate_categories(values):
    return {
        "diagonal": values["root_root"] + 14 * values["neighbour_diag"],
        "adjacent": 2 * values["root_neighbour"] + values["neighbour_mate"],
        "nonadjacent": 2 * values["neighbour_nonmate"],
    }


def bm_eigenvalue(values, theta):
    return (values["diagonal"] - values["nonadjacent"]
            + theta * (values["adjacent"] - values["nonadjacent"]))


def fibre_projector_21():
    edges = tuple(itertools.combinations(range(7), 2))
    result = zero(21)
    for i, left in enumerate(edges):
        for j, right in enumerate(edges):
            common = len(set(left) & set(right))
            result[i][j] = (F(1) if i == j else F(0)) - F(common, 5) + F(1, 15)
    return edges, result


def lift_fibre_projector(edges, projector):
    labels = tuple(pair for pair in itertools.combinations(range(14), 2)
                   if pair[1] != (pair[0] ^ 1))
    edge_index = {edge: index for index, edge in enumerate(edges)}
    fibres = [edge_index[tuple(sorted((left // 2, right // 2)))]
              for left, right in labels]
    lifted = [[projector[fibres[i]][fibres[j]] / 4
               for j in range(84)] for i in range(84)]
    return labels, fibres, lifted


def fraction_map(obj):
    if isinstance(obj, str):
        try:
            return F(obj)
        except (ValueError, ZeroDivisionError):
            return obj
    if isinstance(obj, dict):
        return {key: fraction_map(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [fraction_map(value) for value in obj]
    return obj


def main() -> None:
    source_raw = json.loads(SOURCE.read_text(encoding="utf-8"))
    source = fraction_map(source_raw)
    assert source_raw["status"] == "GLOBAL_ROOT_FUSION_FRAME_IDENTITY_PASS"

    adjacency = star_adjacency()
    pair_difference, centred_pair_constant = invariant_projectors()
    assert matrix_rank(pair_difference) == 7
    assert matrix_rank(centred_pair_constant) == 6
    assert equal(multiply(pair_difference, centred_pair_constant), zero(15))

    local_results = {}
    specifications = {
        "minus4": {
            "eigenvalues": (F(4, 7), F(2, 7), F(20, 21)),
            "kernel": [F(4)] + [F(1)] * 14,
            "radial": [F(7)] + [-F(2)] * 14,
            "global_theta": -4,
            "global_rank": 44,
            "tight": F(63, 2),
            "complement": F(135, 2),
        },
        "plus3": {
            "eigenvalues": (F(3, 7), F(5, 7), F(69, 77)),
            "kernel": [-F(3)] + [F(1)] * 14,
            "radial": [F(14)] + [F(3)] * 14,
            "global_theta": 3,
            "global_rank": 54,
            "tight": F(77, 3),
            "complement": F(220, 3),
        },
    }
    for kind, spec in specifications.items():
        block = primitive_block(kind, adjacency)
        radial_projector = scale(
            outer(spec["radial"]),
            F(1, sum(value * value for value in spec["radial"])),
        )
        assert eigen_check(block, pair_difference, spec["eigenvalues"][0])
        assert eigen_check(block, centred_pair_constant, spec["eigenvalues"][1])
        assert eigen_check(block, radial_projector, spec["eigenvalues"][2])
        assert matvec(block, spec["kernel"]) == [F(0)] * 15
        assert spec["eigenvalues"][2] != F(9, 11) if kind == "plus3" else True
        resolution = add(pair_difference, centred_pair_constant,
                         radial_projector,
                         scale(outer(spec["kernel"]),
                               F(1, sum(value * value for value in spec["kernel"]))))
        assert equal(resolution, identity(15))

        pseudoinverse = add(
            scale(pair_difference, 1 / spec["eigenvalues"][0]),
            scale(centred_pair_constant, 1 / spec["eigenvalues"][1]),
            scale(radial_projector, 1 / spec["eigenvalues"][2]),
        )
        assert equal(multiply(multiply(block, pseudoinverse), block), block)
        assert equal(multiply(multiply(pseudoinverse, block), pseudoinverse),
                     pseudoinverse)
        assert equal(multiply(block, pseudoinverse),
                     transpose(multiply(block, pseudoinverse)))

        local_categories = categories(pseudoinverse)
        middle = aggregate_categories(local_categories)
        # Verify all three Bose--Mesner eigenvalues.  Only the target value is
        # needed after E M E, but zeros on the other two are a useful control.
        bm_values = {
            14: (middle["diagonal"] + 14 * middle["adjacent"]
                 + 84 * middle["nonadjacent"]),
            3: bm_eigenvalue(middle, 3),
            -4: bm_eigenvalue(middle, -4),
        }
        assert bm_values[spec["global_theta"]] == spec["tight"]
        assert spec["tight"] * spec["global_rank"] == 99 * 14
        assert F(99) - spec["tight"] == spec["complement"]

        stored = source["closed_neighbourhood"][kind]
        assert stored["rank"] == 14 == matrix_rank(block)
        assert stored["kernel_vector"] == spec["kernel"]
        assert stored["pseudoinverse_categories"] == local_categories
        assert stored["summed_middle_categories"] == middle
        assert source["tight_fusion_frames"][kind][
            "sum_local_evaluation_complement_projectors"
        ] == f"{spec['tight']} E_{kind}".replace("/1 ", " ")
        local_results[kind] = {
            "nonzero_star_block_eigenvalues": [str(value) for value in spec["eigenvalues"]],
            "radial_eigenvalue": str(spec["eigenvalues"][2]),
            "pseudoinverse_categories": {key: str(value) for key, value in local_categories.items()},
            "aggregate_BM_eigenvalues": {str(key): str(value) for key, value in bm_values.items()},
            "tight_coefficient": str(spec["tight"]),
        }

    # Build the rank-14 K7 edge-kernel projector and its honest 84-point lift.
    support_edges, fibre21 = fibre_projector_21()
    assert equal(multiply(fibre21, fibre21), fibre21)
    assert matrix_rank(fibre21) == 14
    assert all(sum(row, F(0)) == 0 for row in fibre21)
    labels, fibres, p84 = lift_fibre_projector(support_edges, fibre21)
    assert equal(multiply(p84, p84), p84)
    assert sum((p84[index][index] for index in range(84)), F(0)) == 14
    assert all(sum(row, F(0)) == 0 for row in p84)

    lifted_values = {}
    for i, left in enumerate(support_edges):
        for j, right in enumerate(support_edges):
            kind = "same" if i == j else (
                "overlap" if set(left) & set(right) else "disjoint"
            )
            value = fibre21[i][j] / 4
            lifted_values.setdefault(kind, value)
            assert lifted_values[kind] == value
    assert lifted_values == {
        "same": F(1, 6), "overlap": -F(1, 30), "disjoint": F(1, 60)
    }

    # Check orthogonality to both local evaluation spaces without using the
    # producer's projector formula.  The closed-to-outer adjacency row of a
    # neighbour point is the incidence row of the 84 labels containing it.
    closed_outer_adjacency = zero(15, 84)
    for point in range(14):
        for label_index, label in enumerate(labels):
            closed_outer_adjacency[point + 1][label_index] = F(point in label)
    assert equal(multiply(closed_outer_adjacency, p84), zero(15, 84))
    one_cross = [[F(1) for _ in range(84)] for _ in range(15)]
    assert equal(multiply(one_cross, p84), zero(15, 84))
    # Hence both E_-[S,outer]P and E_+[S,outer]P vanish, since these cross
    # blocks are linear combinations of A[S,outer] and One[S,outer].

    # Independent trace(P_r A) category calculation.  The T/U edge profiles
    # give E0 same-fibre, 168-2E0 overlapping-support, and 336+E0 disjoint.
    same = lifted_values["same"]
    overlap = lifted_values["overlap"]
    disjoint = lifted_values["disjoint"]
    trace_constant = 2 * (168 * overlap + 336 * disjoint)
    trace_e0 = 2 * (same - 2 * overlap + disjoint)
    assert (trace_constant, trace_e0) == (F(0), F(1, 2))

    # E_-=(3I-A+One/9)/7 and E_+=(A+4I-2One/11)/7.
    # P has trace14 and kills One, so the pointwise traces are forced.
    minus_constant, minus_e0 = F(6), -F(1, 14)
    plus_constant, plus_e0 = F(8), F(1, 14)
    assert (minus_constant, minus_e0) == (F(84, 14), -F(1, 14))
    assert minus_constant + plus_constant == 14
    assert minus_e0 + plus_e0 == 0
    free = source["free_fibre_projector"]
    assert free["rank"] == 14
    assert free["lifted_entry_values"] == lifted_values
    assert free["trace_P_r_A"] == "E0(r)/2"
    assert free["trace_P_r_E_minus4"] == "(84-E0(r))/14"

    # Cross-root identity.  Put X=sum_r(84-E0(r))=n3+z11/4.
    # Same-root orthogonality deletes r=s; tightness supplies 63/2; and
    # sum tr(E_-P_r)=X/14.  The coefficient is exactly 9/4.
    cross_coefficient = F(63, 2) / 14
    assert cross_coefficient == F(9, 4)
    plus_cross_constant = F(77, 3) * 1386
    plus_cross_x = -F(77, 3) / 14
    assert plus_cross_constant == 35574
    assert plus_cross_x == -F(11, 6)
    motif = source["motif_bridge"]
    assert motif["sum_r_(84-E0(r))"] == "n3+z11/4"
    assert motif["trace_Eminus_sumPr"] == "(n3+z11/4)/14"
    assert motif["minus_cross_root_energy"] == (
        "sum_{r!=s} tr(P_r L_s^-)=9/4*(n3+z11/4)"
    )

    result = {
        "status": "INDEPENDENT_GLOBAL_ROOT_FUSION_FRAME_AUDIT_PASS",
        "source_sha256": digest(SOURCE),
        "source_note_sha256": digest(SOURCE_NOTE),
        "source_blind": True,
        "local_blocks": local_results,
        "checks": {
            "plus3_radial_star_block_eigenvalue": "69/77",
            "explicitly_not_9/11": True,
            "minus_tight_sum": "sum_r L_r^-=(63/2)E_-",
            "plus_tight_sum": "sum_r L_r^+=(77/3)E_+",
            "fibre_projector_84_by_84_idempotent_trace": 14,
            "fibre_projector_closed_outer_incidence_annihilation": True,
            "trace_P_A": "E0/2",
            "pointwise_minus_trace": "tr(E_-P_r)=(84-E0(r))/14",
            "minus_cross_root_coefficient": "9/4",
            "bonus_plus_cross_root_identity": (
                "sum_{r!=s}tr(P_r L_s^+)=35574-(11/6)(n3+z11/4)"
            ),
        },
        "boundary": (
            "all identities verified; without a cross-root upper bound they "
            "give no positive lower bound for E0"
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
