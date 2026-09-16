"""Independent audit of the Wave205 hostile-control K2 projection.

The producer is not imported.  This checker reconstructs both 231 by 231
centered Grams directly from the frozen certificate's ambient form and
column vectors, then re-counts their value-two relations.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path


CERTIFICATE = Path(
    "external_conway99_research/attempts/"
    "wave205-fourth-trace-hostile-controls/certificate.json"
)
PROJECTION = Path("scratch_theory_flag_support_wave205_control_projection.json")
PRODUCER = Path("scratch_theory_flag_support_wave205_control_projection.py")
OUTPUT = Path(
    "scratch_theory_flag_support_wave205_control_projection_"
    "independent_audit.json"
)


def bilinear(left, form, right):
    total = 0
    for row in range(len(form)):
        for column in range(len(form)):
            total += left[row] * form[row][column] * right[column]
    return total % 3


def main():
    certificate = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    claimed = json.loads(PROJECTION.read_text(encoding="utf-8"))
    assert claimed["status"] == "EXACT_WAVE205_HOSTILE_CONTROL_K2_PROJECTION_AUDIT_PASS"

    form = certificate["ambient_form"]
    assert len(form) == 11 and all(len(row) == 11 for row in form)
    assert all(form[row][column] == form[column][row]
               for row in range(11) for column in range(11))

    blocks = [set(block["vertices"]) for block in certificate["blocks"]]
    assert len(blocks) == 231 and all(len(block) == 3 for block in blocks)
    intersection_degree = []
    for left in range(231):
        intersection_degree.append(sum(
            bool(blocks[left] & blocks[right])
            for right in range(231) if right != left
        ))
    assert Counter(intersection_degree) == Counter({18: 231})

    reconstructed = {}
    for label in ("A", "B"):
        vectors = certificate[f"realization_{label}"]["block_vectors"]
        assert len(vectors) == 231
        relation_degrees = []
        disjoint_profiles = []
        selected_twice = 0
        for left in range(231):
            degree = 0
            profile = Counter()
            assert bilinear(vectors[left], form, vectors[left]) == 0
            for right in range(231):
                if right == left:
                    continue
                value = bilinear(vectors[left], form, vectors[right])
                if blocks[left] & blocks[right]:
                    assert value == 1
                    continue
                profile[value] += 1
                if value == 2:
                    degree += 1
                    selected_twice += 1
            assert sum(profile.values()) == 212
            relation_degrees.append(degree)
            disjoint_profiles.append(tuple(profile[value] for value in (0, 1, 2)))

        edge_count = selected_twice // 2
        degree_histogram = Counter(relation_degrees)
        profile_histogram = Counter(disjoint_profiles)
        assert sum(degree * multiplicity
                   for degree, multiplicity in degree_histogram.items()) == 2 * edge_count
        assert edge_count == 5580
        assert degree_histogram == Counter({
            21: 48, 24: 12, 30: 12, 33: 12, 39: 24,
            48: 48, 66: 48, 96: 18, 108: 9,
        })
        assert set(relation_degrees) != {36}
        assert set(disjoint_profiles) != {(32, 144, 36)}

        stored = claimed["realizations"][label]
        assert stored["selected_value_two_edge_count"] == edge_count
        assert {int(key): value for key, value in
                stored["selected_value_two_degree_histogram"].items()} == degree_histogram
        assert stored["has_endpoint_K2_degree_36"] is False
        assert stored["has_endpoint_disjoint_profile_32_144_36"] is False

        reconstructed[label] = {
            "selected_value_two_edge_count": edge_count,
            "degree_histogram": {
                str(key): value for key, value in sorted(degree_histogram.items())
            },
            "disjoint_profile_count": len(profile_histogram),
            "endpoint_edge_count_target": 4158,
            "endpoint_degree_target": 36,
            "edge_count_difference": edge_count - 4158,
        }

    result = {
        "status": "INDEPENDENT_EXACT_WAVE205_CONTROL_K2_PROJECTION_AUDIT_PASS",
        "certificate_sha256": hashlib.sha256(CERTIFICATE.read_bytes()).hexdigest(),
        "projection_sha256": hashlib.sha256(PROJECTION.read_bytes()).hexdigest(),
        "producer_sha256": hashlib.sha256(PRODUCER.read_bytes()).hexdigest(),
        "producer_imported": False,
        "reconstructed": reconstructed,
        "checks": {
            "ambient_gram_reconstructed_from_certificate": True,
            "intersecting_entries_equal_one": True,
            "value_two_degree_histograms_match": True,
            "value_two_edge_count_5580_matches": True,
            "endpoint_degree_36_fails": True,
            "endpoint_edge_count_4158_fails": True,
            "endpoint_profile_32_144_36_fails": True,
        },
        "scope": (
            "Independent audit of two relaxed Wave205 hostile controls.  "
            "It neither audits an actual endpoint nor changes the verified "
            "Wave205 theorem or Conway-99 status."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
