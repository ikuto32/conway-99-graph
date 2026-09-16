"""Exact labelled fibre-state port census for the E0=72,Q>=3 branch.

It configures the audited E73 engine at Q_MIN=3.  Compatibility field names
containing ``at_least_4`` denote the configured target Q>=3 here; the explicit
``schema_compatibility`` field records this convention.
"""

from __future__ import annotations

import json
from pathlib import Path

import scratch_root_e73_q4_port_census as generic


INPUT = Path("scratch_root_e72_q3_compression_audit.json")
OUTPUT = Path("scratch_root_e72_q3_port_census.json")


def part_path(index):
    return Path(f"scratch_root_e72_q3_port_part_{index:02d}.json")


SCHEMA_NOTE = (
    "legacy fields whose names contain Q_at_least_4 or Q_below_4 mean the "
    "configured threshold Q>=3 or Q<3 in this E72 artifact"
)


def configure():
    generic.INPUT_PATH = INPUT
    generic.OUTPUT_PATH = OUTPUT
    generic.Q_MIN = 3
    generic.part_path = part_path

    def source_rows_by_partition():
        source = json.loads(INPUT.read_text(encoding="utf-8"))
        assert source["status"] == "COMPLETE"
        expected = source["summary"]["spectral_real_surviving_support_orbits"]
        partition_index = {
            tuple(row["partition"]): row["partition_index"]
            for row in source["by_partition"]
        }
        grouped = {}
        for row in source["rows"]:
            assert row["passes_weighted_port_overlap_and_real_relaxation"]
            grouped.setdefault(partition_index[tuple(row["partition"])], []).append(row)
        assert sum(map(len, grouped.values())) == expected
        return source, grouped

    def refresh_scope_fields(result):
        result["model"] = "self-contained-root-reduced E0=72,Q>=3 labelled fibre-state port census"
        result.pop("conditional_scope", None)
        result["root_reduction_scope"] = (
            "E0=72 plus the independently audited self-contained S(r)<=69 theorem"
        )
        result["Q_condition"] = "Q>=3"
        result["schema_compatibility"] = SCHEMA_NOTE
        result["claim_boundary"] = (
            "Necessary E0=72,Q>=3 selected-root branch only; exact port census, "
            "not an E0=72 exclusion."
        )
        return result

    def merge_parts():
        source, grouped = source_rows_by_partition()
        parts = []
        for partition_index in sorted(grouped):
            path = part_path(partition_index)
            if not path.exists():
                raise RuntimeError(f"missing {path}")
            part = json.loads(path.read_text(encoding="utf-8"))
            if part["status"] != "COMPLETE":
                raise RuntimeError(f"incomplete {path}: {part['status']}")
            parts.append(part)
        rows = [row for part in parts for row in part["rows"]]
        summary = generic.summarize(rows)
        expected = source["summary"]["spectral_real_surviving_support_orbits"]
        assert summary["input_support_orbits"] == expected
        assert summary["all_full_product_identities_verified"]
        assert summary["all_Q_target_identities_verified"]
        result = refresh_scope_fields({
            "status": "COMPLETE",
            "input": str(INPUT),
            "input_sha256": generic.sha256(INPUT),
            "input_support_orbits": expected,
            "fibre_state_counts": {
                str(d): len(generic.FIBRE_STATES[d]) for d in range(1, 5)
            },
            "fibre_state_Q_histograms": {
                str(d): {
                    str(q): count
                    for q, count in sorted(generic.Counter(generic.Q_VALUES[d]).items())
                }
                for d in range(1, 5)
            },
            "matching_test": (
                "exact per-group Hall condition with extendable-prefix lookahead; "
                "first survivor per positive support row receives direct matching DFS"
            ),
            "coverage": (
                "all labelled fibre-state assignments with Q>=3; exact suffix-Q "
                "counts prove both target and full Cartesian-product identities"
            ),
            "summary": summary,
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
        generic.atomic_json(OUTPUT, result)
        print(json.dumps({
            "path": str(OUTPUT), "status": "COMPLETE", **summary
        }, sort_keys=True), flush=True)
        return result

    generic.source_rows_by_partition = source_rows_by_partition
    generic.refresh_scope_fields = refresh_scope_fields
    generic.merge_parts = merge_parts


def main():
    configure()
    generic.main()


if __name__ == "__main__":
    main()
