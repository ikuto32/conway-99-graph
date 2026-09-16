"""Cross-check the theory sign prefilter against completed recurrence CSPs."""

from __future__ import annotations

import hashlib
import itertools
import json
import os
from collections import Counter
from pathlib import Path

from scratch_theory_e72_k23_exception_sign_filter import adjacency, regular_signs


BASE_INPUT = Path("scratch_general_e72_q3_fast_expansion_part_27.json")
THEORY_AUDIT = Path("scratch_theory_e72_k23_exception_sign_filter.json")
POINTWISE_INPUT = Path("scratch_general_e72_source133_pointwise_frontier.json")
RECURRENCE_OUTPUT = Path("scratch_general_e72_source133_hf_exception_csp.json")
OUTPUT = Path("scratch_general_e72_source133_sign_recurrence_crosscheck.json")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def atomic_json(path: Path, value) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def sign_passes(rep):
    graph = adjacency(rep)
    epsilon = regular_signs(graph)
    if epsilon is None:
        return False
    for x in range(24):
        fibre = x // 4
        internal = next(y for y in graph[x] if y // 4 == fibre)
        vertical_fibre = fibre + 3 if fibre < 3 else fibre - 3
        vertical = next(y for y in graph[x] if y // 4 == vertical_fibre)
        if abs(epsilon[x] + epsilon[internal] + epsilon[vertical]) != 1:
            return False
    return True


def run() -> None:
    base_document = json.loads(BASE_INPUT.read_text(encoding="utf-8"))
    theory = json.loads(THEORY_AUDIT.read_text(encoding="utf-8"))
    pointwise = json.loads(POINTWISE_INPUT.read_text(encoding="utf-8"))
    recurrence = json.loads(RECURRENCE_OUTPUT.read_text(encoding="utf-8"))
    base_rows = base_document["rows"][0]["local_graph_representatives"]
    base_by_mask = {int(row["mask_hex"], 16): row for row in base_rows}
    assert len(base_by_mask) == 8_060

    theory_passing = {
        mask for mask, row in base_by_mask.items() if sign_passes(row)
    }
    theory_by_q = Counter(base_by_mask[mask]["Q"] for mask in theory_passing)
    theory_mass_by_q = Counter()
    for mask in theory_passing:
        row = base_by_mask[mask]
        theory_mass_by_q[row["Q"]] += row["orbit_size"]
    assert len(theory_passing) == theory["passing_overlap_orbits"] == 933
    assert sum(theory_mass_by_q.values()) == theory["passing_labelled_overlap_mass"]

    vertices = tuple(tuple(row) for row in pointwise["vertex_order"])
    pairs = tuple(itertools.combinations(range(24), 2))
    overlap_bits = 0
    for bit, (left, right) in enumerate(pairs):
        support_left = {symbol // 2 for symbol in vertices[left]}
        support_right = {symbol // 2 for symbol in vertices[right]}
        if support_left & support_right:
            overlap_bits |= 1 << bit

    pointwise_base_masks = {
        int(row[0], 16) & overlap_bits
        for row in pointwise["representatives"] if row[3] < 4
    }
    recurrence_base_masks = {
        int(row[0], 16) & overlap_bits
        for row in recurrence["frontier"] if row[3] < 4
    }
    # The recurrence output has the later pair-collision filter as well.  Its
    # base projection is therefore a subset of, not the complete set passing
    # the exception sign condition.  Recompute the exception-row stage from
    # the documented per-base equivalence: intersect sign-pass with bases
    # which had at least one pointwise/pair completion.
    expected_exception_stage = theory_passing & pointwise_base_masks
    missing_before_recurrence = theory_passing - pointwise_base_masks
    assert len(expected_exception_stage) == 923
    assert Counter(base_by_mask[mask]["Q"] for mask in expected_exception_stage) == {
        4: 259, 6: 344, 8: 230, 12: 90,
    }
    assert len(missing_before_recurrence) == 10
    assert {base_by_mask[mask]["Q"] for mask in missing_before_recurrence} == {6}
    assert recurrence_base_masks <= expected_exception_stage

    result = {
        "status": "EXACT_SET_CROSSCHECK_COMPLETE",
        "inputs": {
            str(path): sha256(path)
            for path in (BASE_INPUT, THEORY_AUDIT, POINTWISE_INPUT,
                         RECURRENCE_OUTPUT)
        },
        "theory_sign_passing_base_orbits": len(theory_passing),
        "theory_sign_passing_base_mass": sum(theory_mass_by_q.values()),
        "theory_sign_passing_by_Q": {
            str(key): value for key, value in sorted(theory_by_q.items())
        },
        "sign_passing_bases_with_a_pointwise_pair_completion": len(
            expected_exception_stage
        ),
        "sign_passing_and_pointwise_nonempty_by_Q": {
            str(key): value for key, value in sorted(Counter(
                base_by_mask[mask]["Q"] for mask in expected_exception_stage
            ).items())
        },
        "sign_passing_but_already_pointwise_pair_empty": len(
            missing_before_recurrence
        ),
        "sign_passing_but_pointwise_pair_empty_Q": 6,
        "final_HF_pair_CSP_base_projection": len(recurrence_base_masks),
        "checks": {
            "theory_933_set_recomputed_from_raw_representatives": True,
            "difference_933_minus_923_is_exactly_ten_Q6_pair_empty_bases": True,
            "final_CSP_base_projection_is_subset_of_sign_intersection": True,
        },
    }
    atomic_json(OUTPUT, result)
    print(json.dumps(result, sort_keys=True), flush=True)


if __name__ == "__main__":
    run()
