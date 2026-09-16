"""Project the frozen Wave205 hostile controls onto the value-two relation.

This is a read-only cross-lane audit.  It checks whether the centered Gram
controls already contain an endpoint K2 relation that could be refined by
the unmatched flag matrix X.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path


INPUT = Path(
    "external_conway99_research/attempts/"
    "wave205-fourth-trace-hostile-controls/certificate.json"
)
OUTPUT = Path("scratch_theory_flag_support_wave205_control_projection.json")


def inner(left, right):
    # Ambient form diag(1^10,2), over F_3.
    return (sum(left[index] * right[index] for index in range(10))
            + 2 * left[10] * right[10]) % 3


def main():
    certificate = json.loads(INPUT.read_text(encoding="utf-8"))
    blocks = [frozenset(item["vertices"]) for item in certificate["blocks"]]
    assert len(blocks) == 231
    intersecting = {
        (left, right)
        for left in range(231) for right in range(left + 1, 231)
        if blocks[left] & blocks[right]
    }
    assert len(intersecting) == 2079

    summaries = {}
    for label in ("A", "B"):
        vectors = certificate[f"realization_{label}"]["block_vectors"]
        assert len(vectors) == 231 and {len(vector) for vector in vectors} == {11}
        gram = [[inner(vectors[left], vectors[right]) for right in range(231)]
                for left in range(231)]
        assert all(gram[index][index] == 0 for index in range(231))
        assert all(gram[left][right] == 1 for left, right in intersecting)

        selected_degree = [sum(gram[left][right] == 2 for right in range(231))
                           for left in range(231)]
        disjoint_profiles = []
        for left in range(231):
            profile = Counter(
                gram[left][right]
                for right in range(231)
                if right != left and not (blocks[left] & blocks[right])
            )
            disjoint_profiles.append(tuple(profile[value] for value in range(3)))
        selected_edges = sum(selected_degree) // 2
        summaries[label] = {
            "selected_value_two_degree_histogram": {
                str(k): v for k, v in sorted(Counter(selected_degree).items())
            },
            "selected_value_two_edge_count": selected_edges,
            "disjoint_row_profile_0_1_2_histogram": {
                str(list(k)): v for k, v in sorted(Counter(disjoint_profiles).items())
            },
            "has_endpoint_K2_degree_36": set(selected_degree) == {36},
            "has_endpoint_disjoint_profile_32_144_36":
                set(disjoint_profiles) == {(32, 144, 36)},
        }
        assert not summaries[label]["has_endpoint_K2_degree_36"]

    result = {
        "status": "EXACT_WAVE205_HOSTILE_CONTROL_K2_PROJECTION_AUDIT_PASS",
        "input_sha256": hashlib.sha256(INPUT.read_bytes()).hexdigest(),
        "realizations": summaries,
        "conclusion": (
            "Neither frozen Wave205 hostile realization has a 36-regular "
            "value-two relation, so neither supplies the endpoint K2 quotient "
            "needed before an unmatched flag lift X or Y-support can be defined."
        ),
        "scope": (
            "This audits the relaxed controls only.  It does not refute the "
            "Wave205 theorems and does not constrain an actual endpoint."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
