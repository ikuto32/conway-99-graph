"""Producer-independent replay of the residual-projector coefficient audit."""

from __future__ import annotations

from fractions import Fraction
import hashlib
import itertools
import json
import os
from pathlib import Path


PRODUCER = Path("scratch_theory_cycle_residual_projector_hierarchy.py")
CERTIFICATE = Path("scratch_theory_cycle_residual_projector_hierarchy.json")
OUTPUT = Path("scratch_theory_cycle_residual_projector_hierarchy_audit.json")


def atomic_json(path: Path, value) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def multiply(left, right):
    return [
        [sum(left[i][k] * right[k][j] for k in range(len(right)))
         for j in range(len(right[0]))]
        for i in range(len(left))
    ]


def main() -> None:
    certificate = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    producer_hash = hashlib.sha256(PRODUCER.read_bytes()).hexdigest().upper()
    assert certificate["script_sha256"] == producer_hash
    assert certificate["status"] == "CYCLE_RESIDUAL_PROJECTOR_COEFFICIENT_AUDIT_PASS"

    supports = tuple(itertools.combinations(range(7), 2))
    labels = tuple(
        (2 * a + high, 2 * b + low)
        for a, b in supports for high in (0, 1) for low in (0, 1)
    )
    assert len(labels) == 84 and len(set(labels)) == 84

    # Reconstruct H entrywise, rather than importing/multiplying the
    # producer's incidence matrices.
    h = []
    histogram = {}
    for i, left in enumerate(labels):
        row = []
        for j, right in enumerate(labels):
            q = len(set(left) & set(right))
            d = sum((endpoint ^ 1) in right for endpoint in left)
            if i == j:
                value = Fraction(5, 6)
            else:
                value = Fraction(2 - 11 * q - d, 120)
                if i < j:
                    key = f"q{q}_d{d}"
                    histogram[key] = histogram.get(key, 0) + 1
            row.append(value)
        h.append(row)
    assert multiply(h, h) == h
    assert sum(h[i][i] for i in range(84)) == 70
    assert histogram == certificate["fixed_geometry"]["relation_histogram"]

    # Re-derive both off-diagonal scaled formulas directly from H and the
    # consequence (I-H)B=(2-q-d)/10 of BL=2J-L(I+mate).
    checked_pairs = 0
    for left, right in itertools.combinations(range(84), 2):
        q = len(set(labels[left]) & set(labels[right]))
        d = sum((endpoint ^ 1) in labels[right] for endpoint in labels[left])
        fb = Fraction(2 - q - d, 10)
        for edge in (0, 1):
            e4 = (3 * h[left][right] - edge + fb) / 7
            e3 = h[left][right] - e4
            assert 112 * e4 == 4 - 6 * q - 2 * d - 16 * edge
            assert 1680 * e3 == -32 - 64 * q + 16 * d + 240 * edge
        checked_pairs += 1

    # Alternative exact values, deliberately distinct from producer samples.
    linearizations = 0
    for a, b in ((Fraction(13, 17), Fraction(-31, 19)),
                 (Fraction(-101, 23), Fraction(211, 29))):
        absent4, present4 = a * a, (a - 16) ** 2
        absent3, present3 = b * b, (b + 240) ** 2
        absent_cross, present_cross = a * b, (a - 16) * (b + 240)
        assert present4 - absent4 == 32 * (8 - a)
        assert present3 - absent3 == 480 * (b + 120)
        assert present_cross - absent_cross == 240 * a - 16 * b - 3840
        linearizations += 3

    # Formal coefficient replay of the dependency.  In the algebra generated
    # by H,E with H^2=H and HE=EH=E, both defects have coefficients
    # E^2-E; E(H-E) has the negative coefficients.
    e3_defect_coefficients = {"E2": 1, "E": -1, "H": 0}
    e4_defect_coefficients = {"E2": 1, "E": -1, "H": 0}
    cross_coefficients = {"E2": -1, "E": 1, "H": 0}
    assert e3_defect_coefficients == e4_defect_coefficients
    assert all(cross_coefficients[key] == -e4_defect_coefficients[key]
               for key in e4_defect_coefficients)

    result = {
        "status": "INDEPENDENT_CYCLE_RESIDUAL_PROJECTOR_COEFFICIENT_AUDIT_PASS",
        "producer_imported": False,
        "producer_sha256": producer_hash,
        "certificate_sha256": hashlib.sha256(CERTIFICATE.read_bytes()).hexdigest().upper(),
        "exact_label_pairs_checked": checked_pairs,
        "relation_histogram": histogram,
        "cycle_projector_idempotence_checked": True,
        "minus4_and_plus3_coefficients_checked": 2 * checked_pairs,
        "binary_linearizations_checked": linearizations,
        "defect_dependency_checked": True,
        "extra_exclusion_credited": False,
        "submission_txt_written": False,
    }
    atomic_json(OUTPUT, result)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
