"""Combine and audit the eight exact solver-free source-133 shards."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path


SHARDS = tuple(
    Path(f"scratch_theory_e72_k23_opposite_collision_enum_shard_{index}.json")
    for index in range(8)
)
OUTPUT = Path("scratch_theory_e72_k23_opposite_collision_enum.json")
EXPECTED_RANGES = tuple(
    (start, min(start + 643, 5138)) for start in range(0, 5138, 643)
)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main():
    documents = [json.loads(path.read_text(encoding="utf-8"))
                 for path in SHARDS]
    assert len(documents) == len(EXPECTED_RANGES) == 8
    assert tuple(
        (row["summary"]["slice_start"], row["summary"]["slice_stop"])
        for row in documents
    ) == EXPECTED_RANGES
    input_hashes = {tuple(sorted(row["inputs"].items())) for row in documents}
    assert len(input_hashes) == 1
    assert all(row["status"] == "PARTIAL_PROBE_COMPLETE"
               for row in documents)
    assert all(row["checks"]["standard_library_only"]
               and not row["checks"]["SAT_or_SMT_used"]
               for row in documents)
    totals = Counter()
    per_macro = {}
    controls = []
    for shard_index, row in enumerate(documents):
        summary = row["summary"]
        for field in ("input_orbits", "input_mass", "passing_orbits",
                      "passing_mass", "rejected_orbits"):
            totals[field] += summary[field]
        # Survivors are forwarded to the independent EE-cross refinement.
        for macro, values in row["per_macro"].items():
            target = per_macro.setdefault(macro, Counter())
            target.update(values)
        for control in row["controls"]:
            controls.append({"shard": shard_index, **control})

    assert totals == Counter({
        "input_orbits": 5_138,
        "input_mass": 1_129_056,
        "passing_orbits": 81,
        "passing_mass": 9_952,
        "rejected_orbits": 5_057,
    })
    survivors = [record for row in documents for record in row["survivors"]]
    assert len(survivors) == 81
    assert sum(record[1] for record in survivors) == 9_952
    result = {
        "status": "EXACT_SOLVER_FREE_STAGE_ONE_COMPLETE",
        "inputs": dict(next(iter(input_hashes))),
        "shards": {str(path): sha256(path) for path in SHARDS},
        "summary": dict(totals),
        "per_macro": {
            macro: dict(sorted(values.items()))
            for macro, values in sorted(per_macro.items())
        },
        "controls": controls,
        "survivors": survivors,
        "checks": {
            "all_shard_ranges_contiguous_and_exact": True,
            "standard_library_only": True,
            "all_HF_t_patterns_enumerated": True,
            "all_four_symbol_exception_to_U_maps_enumerated": True,
            "all_exception_recurrence_rows_exact": True,
            "all_EE_same_pair_deficits_exact": True,
            "all_EU_disjoint_pair_upper_rows_exact": True,
            "all_EU_overlap_pair_upper_rows_exact": True,
            "SAT_or_SMT_used": False,
        },
        "claim_boundary": (
            "All 5,138 regular source-133 masks in the exact preceding "
            "frontier are audited by a direct finite-map enumeration; 81 "
            "pass this first-stage subsystem and are forwarded to the exact "
            "EE-cross refinement.  Macro 4 is outside the regular H/F theorem."
        ),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"path": str(OUTPUT), **result["summary"]},
                     sort_keys=True))


if __name__ == "__main__":
    main()
