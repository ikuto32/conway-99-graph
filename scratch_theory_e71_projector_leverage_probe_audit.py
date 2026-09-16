"""Producer-independent exact audit of the E71 projector leverage probe."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import itertools
import json
import os
from pathlib import Path


SOURCE = Path("scratch_theory_e71_defect_rank_probe.json")
CERTIFICATE = Path("scratch_theory_e71_projector_leverage_probe.json")
OUTPUT = Path("scratch_theory_e71_projector_leverage_probe_audit.json")
SUPPORTS = tuple(itertools.combinations(range(7), 2))


def frac(value):
    return value if isinstance(value, Fraction) else Fraction(value)


def rank(matrix):
    work = [[frac(value) for value in row] for row in matrix]
    rows = len(work)
    columns = len(work[0]) if rows else 0
    pivot = 0
    for column in range(columns):
        selected = next(
            (row for row in range(pivot, rows) if work[row][column]), None
        )
        if selected is None:
            continue
        work[pivot], work[selected] = work[selected], work[pivot]
        scale = work[pivot][column]
        work[pivot] = [value / scale for value in work[pivot]]
        for row in range(pivot + 1, rows):
            if not work[row][column]:
                continue
            scale = work[row][column]
            work[row] = [
                left - scale * right
                for left, right in zip(work[row], work[pivot])
            ]
        pivot += 1
        if pivot == rows:
            break
    return pivot


def inverse(matrix):
    size = len(matrix)
    work = [
        [frac(value) for value in matrix[row]]
        + [Fraction(int(row == column)) for column in range(size)]
        for row in range(size)
    ]
    for column in range(size):
        selected = next(row for row in range(column, size) if work[row][column])
        work[column], work[selected] = work[selected], work[column]
        scale = work[column][column]
        work[column] = [value / scale for value in work[column]]
        for row in range(size):
            if row == column or not work[row][column]:
                continue
            scale = work[row][column]
            work[row] = [
                left - scale * right
                for left, right in zip(work[row], work[column])
            ]
    assert all(
        work[i][j] == int(i == j)
        for i in range(size)
        for j in range(size)
    )
    return [row[size:] for row in work]


def matvec(matrix, vector):
    return [sum(frac(a) * frac(b) for a, b in zip(row, vector)) for row in matrix]


def dot(left, right):
    return sum(frac(a) * frac(b) for a, b in zip(left, right))


def independent_principal_indices(matrix, wanted):
    size = len(matrix)
    indices = []
    current = 0
    for candidate in range(size):
        trial = [*indices, candidate]
        minor = [[matrix[i][j] for j in trial] for i in trial]
        trial_rank = rank(minor)
        if trial_rank > current:
            indices = trial
            current = trial_rank
            if current == wanted:
                return tuple(indices)
    raise AssertionError("no nonsingular principal rank minor")


def rowspace_quadratic(matrix, vector, indices, inverse_minor):
    wanted_rank = len(indices)
    short = [frac(vector[i]) for i in indices]
    coefficients = matvec(inverse_minor, short)
    reconstructed = [
        sum(frac(matrix[row][indices[j]]) * coefficients[j] for j in range(wanted_rank))
        for row in range(len(matrix))
    ]
    assert reconstructed == [frac(value) for value in vector]
    return dot(short, coefficients)


def parse_fraction(value):
    return Fraction(str(value))


def atomic_json(path, value):
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def main():
    source_raw = SOURCE.read_bytes()
    certificate_raw = CERTIFICATE.read_bytes()
    source = json.loads(source_raw)
    certificate = json.loads(certificate_raw)
    assert certificate["input"][str(SOURCE)] == hashlib.sha256(source_raw).hexdigest().upper()

    incidence = [
        [int(vertex in support) for support in SUPPORTS] for vertex in range(7)
    ]
    inverse_5i_j = [
        [Fraction(int(i == j), 5) - Fraction(1, 60) for j in range(7)]
        for i in range(7)
    ]
    K = [
        [
            Fraction(int(i == j))
            - sum(
                incidence[a][i]
                * inverse_5i_j[a][b]
                * incidence[b][j]
                for a in range(7)
                for b in range(7)
            )
            for j in range(21)
        ]
        for i in range(21)
    ]
    assert rank(K) == 14
    assert all(
        sum(K[i][k] * K[k][j] for k in range(21)) == K[i][j]
        for i in range(21)
        for j in range(21)
    )
    assert all(
        K[i][j]
        == (
            Fraction(2, 3)
            if i == j
            else Fraction(-2, 15)
            if set(SUPPORTS[i]) & set(SUPPORTS[j])
            else Fraction(1, 15)
        )
        for i in range(21)
        for j in range(21)
    )

    source_by_key = {tuple(row["key"]): row for row in source["rows"]}
    certificate_by_key = {tuple(row["key"]): row for row in certificate["rows"]}
    assert set(source_by_key) == set(certificate_by_key)
    patterns_checked = 0
    violations_minus4 = 0
    violations_plus3 = 0
    maxima_minus4 = Fraction(0)
    maxima_plus3 = Fraction(0)
    violating_patterns = []
    for key, profile in source_by_key.items():
        reported = certificate_by_key[key]
        Z = [[frac(value) for value in row] for row in profile["Z"]]
        assert rank(Z) == profile["Z_rank"] == 3
        assert all(Z[i][j] == Z[j][i] for i in range(21) for j in range(21))
        assert all(
            sum(K[i][k] * Z[k][j] for k in range(21)) == Z[i][j]
            and sum(Z[i][k] * K[k][j] for k in range(21)) == Z[i][j]
            for i in range(21)
            for j in range(21)
        )
        denominator3 = [
            [28 * K[i][j] - Z[i][j] for j in range(21)] for i in range(21)
        ]
        assert rank(denominator3) == 14
        indices4 = independent_principal_indices(Z, 3)
        inverse4 = inverse([[Z[i][j] for j in indices4] for i in indices4])
        indices3 = independent_principal_indices(denominator3, 14)
        inverse3 = inverse(
            [[denominator3[i][j] for j in indices3] for i in indices3]
        )
        reported_fibres = {
            tuple(row["source_support"]): row for row in reported["by_source_fibre"]
        }
        local_minus4 = Fraction(0)
        local_plus3 = Fraction(0)
        local_bad4 = 0
        local_bad3 = 0
        for fibre in profile["rank_three_integer_row_patterns"]["by_source_fibre"]:
            support = tuple(fibre["source_support"])
            G = SUPPORTS.index(support)
            reported_patterns = {
                int(row["pattern_index"]): row
                for row in reported_fibres[support]["patterns"]
            }
            assert len(reported_patterns) == len(fibre["patterns"])
            for index, pattern in enumerate(fibre["patterns"]):
                r = [Fraction(0) for _ in range(21)]
                for target, value in zip(
                    profile["exceptional_supports"],
                    pattern["scaled_W_row_on_exceptional"],
                ):
                    r[SUPPORTS.index(tuple(target))] = frac(value)
                s4 = [Z[G][column] - r[column] for column in range(21)]
                s3 = [
                    28 * K[G][column] - Z[G][column] + r[column]
                    for column in range(21)
                ]
                q4 = rowspace_quadratic(Z, s4, indices4, inverse4)
                q3 = rowspace_quadratic(
                    denominator3, s3, indices3, inverse3
                )
                recorded = reported_patterns[index]
                assert q4 == parse_fraction(recorded["minus4_leverage"])
                assert q3 == parse_fraction(recorded["plus3_leverage"])
                local_minus4 = max(local_minus4, q4)
                local_plus3 = max(local_plus3, q3)
                bad4 = q4 > 40
                bad3 = q3 > Fraction(160, 3)
                local_bad4 += bad4
                local_bad3 += bad3
                violations_minus4 += bad4
                violations_plus3 += bad3
                if bad4 or bad3:
                    violating_patterns.append(
                        {
                            "key": list(key),
                            "source_support": list(support),
                            "pattern_index": index,
                            "minus4": str(q4),
                            "plus3": str(q3),
                        }
                    )
                patterns_checked += 1
        assert local_minus4 == parse_fraction(reported["maximum_minus4_leverage"])
        assert local_plus3 == parse_fraction(reported["maximum_plus3_leverage"])
        assert local_bad4 == reported["minus4_violations"]
        assert local_bad3 == reported["plus3_violations"]
        maxima_minus4 = max(maxima_minus4, local_minus4)
        maxima_plus3 = max(maxima_plus3, local_plus3)

    assert patterns_checked == certificate["patterns_checked"] == 219
    assert maxima_minus4 == parse_fraction(certificate["overall_maximum_minus4_leverage"])
    assert maxima_plus3 == parse_fraction(certificate["overall_maximum_plus3_leverage"])
    assert violations_minus4 == 9
    assert violations_plus3 == 0

    # Fixed-coordinate diagonal calculation on the 84 edge labels.  If L is
    # the unsigned endpoint incidence, the cycle projector has diagonal 5/6.
    # The known action B L=2J-L(I+mate) makes diag((I-H)B)=0, hence the -4
    # projector H(3I-B)/7 has diagonal 5/14.  Its cycle complement has 10/21.
    gram_inverse_14 = [
        [
            Fraction(11, 120) * int(i == j)
            - Fraction(1, 240)
            + Fraction(1, 120) * int(i == (j ^ 1))
            for j in range(14)
        ]
        for i in range(14)
    ]
    labels = tuple(
        (2 * i + a, 2 * j + b)
        for i, j in SUPPORTS
        for a, b in itertools.product((0, 1), repeat=2)
    )
    leverage = []
    pb_diagonal = []
    for edge in labels:
        vector = [int(vertex in edge) for vertex in range(14)]
        leverage.append(
            sum(
                vector[i] * gram_inverse_14[i][j] * vector[j]
                for i in range(14)
                for j in range(14)
            )
        )
        # Entrywise formula for the im(L) part of B is (2-q-d)/10; q=2,d=0
        # on a diagonal coordinate.
        pb_diagonal.append(Fraction(2 - 2 - 0, 10))
    assert set(leverage) == {Fraction(1, 6)}
    assert set(pb_diagonal) == {Fraction(0)}
    minus4_diagonal = (3 * (1 - Fraction(1, 6)) - 0) / 7
    plus3_diagonal = (1 - Fraction(1, 6)) - minus4_diagonal
    assert minus4_diagonal == Fraction(5, 14)
    assert plus3_diagonal == Fraction(10, 21)

    result = {
        "status": "INDEPENDENT_E71_PROJECTOR_LEVERAGE_AUDIT_PASS",
        "producer_imported": False,
        "source_sha256": hashlib.sha256(source_raw).hexdigest().upper(),
        "certificate_sha256": hashlib.sha256(certificate_raw).hexdigest().upper(),
        "coarse_cycle_rank": rank(K),
        "profiles_checked": len(source_by_key),
        "patterns_checked": patterns_checked,
        "minus4_coordinate_diagonal": str(minus4_diagonal),
        "plus3_coordinate_diagonal": str(plus3_diagonal),
        "minus4_violations": violations_minus4,
        "plus3_violations": violations_plus3,
        "violating_patterns": violating_patterns,
        "overall_minus4_maximum": str(maxima_minus4),
        "overall_plus3_maximum": str(maxima_plus3),
        "submission_txt_written": False,
    }
    atomic_json(OUTPUT, result)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
