"""Exact fibre-state port census for the fast E0=71,Q>=2 support list.

The underlying port enumerator is the audited E73 implementation.  This
wrapper changes only the branch constants, input adapter, paths and scope
labels; historical field names containing ``Q_at_least_4`` mean Q>=2 here.
"""

from __future__ import annotations

import json
from pathlib import Path

import scratch_root_e73_q4_port_census as generic


INPUT = Path("scratch_root_e71_weighted_port_fast_audit.json")
PLAN = Path("scratch_root_e71_q2_compression_plan.json")
OUTPUT = Path("scratch_root_e71_q2_port_census.json")
SCHEMA_NOTE = "legacy Q_at_least_4 field names mean the configured E71 threshold Q>=2"


def part_path(index):
    return Path(f"scratch_root_e71_q2_port_part_{index:02d}.json")


def adapted_source_rows_by_partition():
    source = json.loads(INPUT.read_text(encoding="utf-8"))
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    assert source["status"] == "COMPLETE"
    assert source["summary"]["spectral_real_survivors"] == 4398
    partition_index = {
        tuple(int(value) for value in row["partition"]): int(row["partition_index"])
        for row in plan["rows"]
    }
    grouped = {}
    for row in source["rows"]:
        assert row["passes_weighted_port_overlap_and_real_relaxation"]
        index = partition_index[tuple(row["partition"])]
        copied = dict(row)
        copied["orbit_index"] = len(grouped.setdefault(index, []))
        grouped[index].append(copied)
    assert sum(map(len, grouped.values())) == 4398
    return source, grouped


def refresh_scope_fields(result):
    result["model"] = "self-contained-root-reduced E0=71,Q>=2 labelled fibre-state port census"
    result["root_reduction_scope"] = (
        "E0=71 plus the independently audited self-contained S(r)<=69 theorem"
    )
    result["schema_compatibility"] = SCHEMA_NOTE
    result["claim_boundary"] = (
        "Necessary E0=71,Q>=2 selected-root branch only; exact port census, "
        "not an E0=71 exclusion."
    )
    return result


def merge_parts():
    source, grouped = adapted_source_rows_by_partition()
    parts = []
    for index in sorted(grouped):
        path = part_path(index)
        if not path.exists():
            raise RuntimeError(f"missing {path}")
        part = json.loads(path.read_text(encoding="utf-8"))
        if part["status"] != "COMPLETE":
            raise RuntimeError(f"incomplete {path}: {part['status']}")
        parts.append(part)
    rows = [row for part in parts for row in part["rows"]]
    result = refresh_scope_fields({
        "status": "COMPLETE",
        "input": str(INPUT),
        "input_sha256": generic.sha256(INPUT),
        "input_support_orbits": 4398,
        "Q_condition": "Q>=2",
        "fibre_state_counts": {
            str(deficit): len(generic.FIBRE_STATES[deficit]) for deficit in range(1, 5)
        },
        "matching_test": (
            "exact per-group category/Hall condition with extendable-prefix lookahead; "
            "first survivor checked by independent direct matching DFS"
        ),
        "summary": generic.summarize(rows),
        "by_partition": [
            {
                "partition_index": part["partition_index"],
                "partition": part["partition"],
                **part["summary"],
                "artifact": str(part_path(part["partition_index"])),
            }
            for part in parts
        ],
        "rows": rows,
    })
    assert result["summary"]["input_support_orbits"] == 4398
    assert result["summary"]["all_full_product_identities_verified"]
    assert result["summary"]["all_Q_target_identities_verified"]
    generic.atomic_json(OUTPUT, result)
    print(json.dumps({"path": str(OUTPUT), "status": "COMPLETE", **result["summary"]}, sort_keys=True))
    return result


def configure():
    generic.INPUT_PATH = INPUT
    generic.OUTPUT_PATH = OUTPUT
    generic.Q_MIN = 2
    generic.part_path = part_path
    generic.source_rows_by_partition = adapted_source_rows_by_partition
    generic.refresh_scope_fields = refresh_scope_fields
    generic.merge_parts = merge_parts


def main():
    configure()
    generic.main()


if __name__ == "__main__":
    main()
