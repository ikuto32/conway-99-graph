"""Compress the full D_FG profiles attached to every E0=72 frontier orbit.

The input is intentionally the large, explicit post-BP representative file.
This script independently recomputes every overlap block total from its edge
list, joins it to the exact disjoint Gram totals, and emits only small
per-source profile/range statistics for SAT scheduling.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import os
from collections import Counter, defaultdict
from pathlib import Path

from scratch_general_e72_q3_disjoint_gram_filter import row_geometry


INPUT_PATH = Path(
    "scratch_general_e72_q3_gram_frontier_disjoint_gram_filtered_reps.json"
)
MACRO_PATH = Path("scratch_general_e72_q3_gram_fast_expansion_macro_catalog.json")
PARAMETRIC_PATH = Path("scratch_theory_e72_source332_parametric_gram.json")
OUTPUT_PATH = Path("scratch_general_e72_frontier_d_profile_audit.json")


def atomic_json(path: Path, value) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def row_key(row):
    return tuple(row["partition"]), row["compression_orbit_index"]


def complete_profile_key(support_count, overlap, disjoint):
    values = {**overlap, **disjoint}
    pairs = tuple(itertools.combinations(range(support_count), 2))
    assert set(values) == set(pairs)
    return tuple(values[pair] for pair in pairs)


def ranges_from_profiles(pairs, profiles):
    return {
        f"{left}-{right}": {
            "min": min(profile[index] for profile in profiles),
            "max": max(profile[index] for profile in profiles),
            "values": sorted({profile[index] for profile in profiles}),
        }
        for index, (left, right) in enumerate(pairs)
    }


def run() -> None:
    document = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    macro = json.loads(MACRO_PATH.read_text(encoding="utf-8"))
    parametric = json.loads(PARAMETRIC_PATH.read_text(encoding="utf-8"))
    assert document["status"] == "COMPLETE"

    key_sources = defaultdict(set)
    partition_indices = {}
    for entry in macro["macro_entries"]:
        key_sources[row_key(entry)].add(entry["source_row_index"])
        partition_indices[entry["source_row_index"]] = entry["partition_index"]
    assert all(len(sources) == 1 for sources in key_sources.values())

    param_cases = [
        {
            tuple(sorted((left, right))): int(value)
            for left, right, value in case["disjoint_exceptional_block_totals"]
        }
        for case in parametric["feasible_parameters"]
    ]
    output_rows = []
    total_mass = total_orbits = 0
    for row in document["support_rows"]:
        source = next(iter(key_sources[row_key(row)]))
        supports, _, fibre_of, _ = row_geometry(row)
        pairs = tuple(itertools.combinations(range(len(supports)), 2))
        profile_stats = defaultdict(lambda: {"orbits": 0, "raw_mass": 0, "Q": Counter()})
        row_mass = 0
        for representative in row["representatives"]:
            overlap = Counter(
                {
                    (left, right): 0
                    for left, right in pairs
                    if set(supports[left]) & set(supports[right])
                }
            )
            for left, right in representative["edges"]:
                left = tuple(left)
                right = tuple(right)
                f, g = fibre_of[left], fibre_of[right]
                if f != g and set(supports[f]) & set(supports[g]):
                    overlap[tuple(sorted((f, g)))] += 1
            detail = representative["disjoint_Gram_profile"]
            if detail["status"] == "UNIQUE_GRAM_DISJOINT_TOTALS":
                alternatives = [
                    {
                        tuple(sorted((left, right))): int(value)
                        for left, right, value in detail["targets"]
                    }
                ]
            else:
                assert source == 332
                assert detail["status"] == "PARAMETRIC_GRAM_CASE_RETAINED"
                alternatives = [
                    param_cases[index]
                    for index in detail["passing_parametric_case_indices"]
                ]
            mass = representative["orbit_size"]
            row_mass += mass
            for disjoint in alternatives:
                profile = complete_profile_key(len(supports), dict(overlap), disjoint)
                stats = profile_stats[profile]
                stats["orbits"] += 1
                stats["raw_mass"] += mass
                stats["Q"][representative["Q"]] += mass
        assert row_mass == row["raw_survivors"]
        assert len(row["representatives"]) == row["orbit_count"]
        profile_rows = []
        for number, (profile, stats) in enumerate(sorted(profile_stats.items())):
            profile_rows.append(
                {
                    "profile_number": number,
                    "D": [
                        [left, right, profile[index]]
                        for index, (left, right) in enumerate(pairs)
                    ],
                    "representative_memberships": stats["orbits"],
                    "raw_mass_memberships": stats["raw_mass"],
                    "Q_mass_memberships": {
                        str(q): value for q, value in sorted(stats["Q"].items())
                    },
                }
            )
        assert profile_rows
        output_rows.append(
            {
                "source_row_index": source,
                "partition_index": partition_indices[source],
                "partition": row["partition"],
                "compression_orbit_index": row["compression_orbit_index"],
                "raw_BP_survivors": row_mass,
                "local_graph_orbits": row["orbit_count"],
                "distinct_surviving_full_D_profiles": len(profile_rows),
                "surviving_complete_D_value_ranges": ranges_from_profiles(
                    pairs, tuple(profile_stats)
                ),
                "profiles": profile_rows,
            }
        )
        total_mass += row_mass
        total_orbits += row["orbit_count"]
    assert total_mass == document["summary"]["passing_raw_survivors"]
    assert total_orbits == document["summary"]["passing_orbits"]

    source248 = next(row for row in output_rows if row["source_row_index"] == 248)
    assert source248["raw_BP_survivors"] == 114_688
    assert source248["local_graph_orbits"] == 338
    assert source248["distinct_surviving_full_D_profiles"] == 1
    source332 = next(row for row in output_rows if row["source_row_index"] == 332)
    assert source332["distinct_surviving_full_D_profiles"] == 3
    assert all(
        profile["representative_memberships"] == source332["local_graph_orbits"]
        and profile["raw_mass_memberships"] == source332["raw_BP_survivors"]
        for profile in source332["profiles"]
    )

    result = {
        "status": "EXACT_D_PROFILE_AGGREGATION_VERIFIED",
        "scope": "all explicit E0=72 pair-and-BP local graph representatives",
        "inputs": {
            str(path): sha256(path)
            for path in (INPUT_PATH, MACRO_PATH, PARAMETRIC_PATH)
        },
        "summary": {
            "support_rows": len(output_rows),
            "raw_BP_survivors": total_mass,
            "local_graph_orbits": total_orbits,
            "all_overlap_D_recomputed_from_edges": True,
            "all_complete_D_profiles_have_every_fibre_pair": True,
            "source332_all_three_exact_parametric_cases_included": True,
        },
        "source_rows": sorted(output_rows, key=lambda row: row["source_row_index"]),
    }
    atomic_json(OUTPUT_PATH, result)
    print(json.dumps({"status": result["status"], **result["summary"]}), flush=True)


if __name__ == "__main__":
    run()
