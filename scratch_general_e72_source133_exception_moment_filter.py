"""Filter source-133 regular completions by exact exception moments.

The H/F and q=0 ordinary-fibre identities determine the contribution of
ordinary common witnesses to every pair of exceptional fibres.  Therefore
the already materialized exceptional graph must satisfy

    (M_E^T A_E^2 M_E)[F,G] = 8   for same-side or vertical F,G,
                              12  for disjoint F,G.

The sum is evaluated directly from every completed 24-vertex mask.  Macro 4
is kept separate because the regular-matching H/F lemma is not assumed there.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import os
import time
from collections import Counter, defaultdict
from pathlib import Path


INPUT = Path("scratch_general_e72_source133_pointwise_frontier.json")
THEORY = Path("scratch_theory_e72_k23_balance_audit.json")
OUTPUT = Path("scratch_general_e72_source133_exception_moment_filter.json")
REGULAR_MACROS = frozenset(range(4))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def atomic_json(path: Path, value) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, separators=(",", ":")) + "\n",
                         encoding="utf-8")
    temporary.replace(path)


def support(vertex):
    return tuple(sorted(symbol // 2 for symbol in vertex))


def adjacency(vertex_count, pair_positions, mask):
    rows = [0] * vertex_count
    while mask:
        low = mask & -mask
        bit = low.bit_length() - 1
        left, right = pair_positions[bit]
        rows[left] |= 1 << right
        rows[right] |= 1 << left
        mask ^= low
    return tuple(rows)


def run() -> None:
    started = time.monotonic()
    document = json.loads(INPUT.read_text(encoding="utf-8"))
    theory = json.loads(THEORY.read_text(encoding="utf-8"))
    assert theory["status"] == "EXACT_SUPPORT_ARITHMETIC_VERIFIED"
    vertices = tuple(tuple(value) for value in document["vertex_order"])
    pairs = tuple(itertools.combinations(range(len(vertices)), 2))
    fibre_order = tuple(tuple(value)
                        for value in document["exceptional_support_order"])
    by_fibre = {
        fibre: tuple(x for x, vertex in enumerate(vertices)
                     if support(vertex) == fibre)
        for fibre in fibre_order
    }
    assert all(len(row) == 4 for row in by_fibre.values())

    target_rows = []
    for left, right in itertools.combinations(fibre_order, 2):
        same_side = left[0] == right[0]
        vertical = left[1] == right[1]
        assert not (same_side and vertical)
        target = 8 if same_side or vertical else 12
        target_rows.append((left, right, target))

    survivors = []
    per_macro = defaultdict(Counter)
    first_failures = []
    observed_histograms = {
        "same_side": Counter(), "vertical": Counter(), "disjoint": Counter()
    }
    for number, record in enumerate(document["representatives"]):
        mask_hex, mass, q_value, macro = record
        stats = per_macro[macro]
        stats["input_orbits"] += 1
        stats["input_mass"] += mass
        if macro not in REGULAR_MACROS:
            stats["retained_nonregular_orbits"] += 1
            stats["retained_nonregular_mass"] += mass
            survivors.append(record)
            continue
        rows = adjacency(len(vertices), pairs, int(mask_hex, 16))
        failures = []
        for left, right, target in target_rows:
            actual = sum(
                (rows[x] & rows[y]).bit_count()
                for x in by_fibre[left] for y in by_fibre[right]
            )
            kind = (
                "same_side" if left[0] == right[0]
                else "vertical" if left[1] == right[1]
                else "disjoint"
            )
            observed_histograms[kind][actual] += 1
            if actual != target:
                failures.append((left, right, target, actual))
        if failures:
            stats["rejected_orbits"] += 1
            stats["rejected_mass"] += mass
            stats["failed_fibre_pair_tests"] += len(failures)
            if len(first_failures) < 20:
                first_failures.append({
                    "record_number": number,
                    "mask_hex": mask_hex,
                    "state_macro_number": macro,
                    "Q": q_value,
                    "failures": [
                        [list(left), list(right), target, actual]
                        for left, right, target, actual in failures
                    ],
                })
        else:
            stats["passing_orbits"] += 1
            stats["passing_mass"] += mass
            survivors.append(record)

    summary = {
        "input_orbits": len(document["representatives"]),
        "input_mass": sum(row[1] for row in document["representatives"]),
        "regular_input_orbits": sum(per_macro[m]["input_orbits"]
                                    for m in REGULAR_MACROS),
        "regular_input_mass": sum(per_macro[m]["input_mass"]
                                  for m in REGULAR_MACROS),
        "regular_passing_orbits": sum(per_macro[m]["passing_orbits"]
                                      for m in REGULAR_MACROS),
        "regular_passing_mass": sum(per_macro[m]["passing_mass"]
                                    for m in REGULAR_MACROS),
        "regular_rejected_orbits": sum(per_macro[m]["rejected_orbits"]
                                       for m in REGULAR_MACROS),
        "regular_rejected_mass": sum(per_macro[m]["rejected_mass"]
                                     for m in REGULAR_MACROS),
        "macro4_retained_orbits": per_macro[4]["retained_nonregular_orbits"],
        "macro4_retained_mass": per_macro[4]["retained_nonregular_mass"],
        "output_orbits": len(survivors),
        "output_mass": sum(row[1] for row in survivors),
        "elapsed_seconds": round(time.monotonic() - started, 6),
    }
    assert summary["input_orbits"] == 92_561
    assert summary["input_mass"] == 30_976_832
    assert summary["regular_input_orbits"] == 92_413
    assert summary["regular_input_mass"] == 30_938_816
    assert summary["macro4_retained_orbits"] == 148
    assert summary["macro4_retained_mass"] == 38_016
    assert summary["output_orbits"] == (
        summary["regular_passing_orbits"] + summary["macro4_retained_orbits"]
    )
    assert summary["output_mass"] == (
        summary["regular_passing_mass"] + summary["macro4_retained_mass"]
    )
    result = {
        "status": "EXACT_FILTER_COMPLETE",
        "model": "source133 exact exceptional-fibre A_E^2 moment filter",
        "inputs": {str(INPUT): sha256(INPUT), str(THEORY): sha256(THEORY)},
        "targets": [
            [list(left), list(right), target]
            for left, right, target in target_rows
        ],
        "summary": summary,
        "per_macro": {
            str(macro): dict(sorted(stats.items()))
            for macro, stats in sorted(per_macro.items())
        },
        "observed_value_histograms": {
            kind: {str(value): count for value, count in sorted(rows.items())}
            for kind, rows in observed_histograms.items()
        },
        "first_failures": first_failures,
        "frontier_record_fields": document["representative_fields"],
        "frontier": survivors,
        "checks": {
            "all_15_fibre_pair_moments_checked_per_regular_record": True,
            "macro4_retained_without_regular_matching_assumption": True,
        },
        "claim_boundary": (
            "Passing masks satisfy the exceptional-only moment identities. "
            "Unmaterialized ordinary edges and the full SRG constraints remain."
        ),
    }
    atomic_json(OUTPUT, result)
    print(json.dumps(summary, sort_keys=True), flush=True)


if __name__ == "__main__":
    run()
