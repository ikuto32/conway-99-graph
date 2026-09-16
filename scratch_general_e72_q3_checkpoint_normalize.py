"""Normalize completed E0=72,Q>=3 local rows for exact incremental SAT."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from scratch_general_e74_incremental_checkpoint_normalize import atomic_json, normalize_row
from scratch_general_exact_sat import coordinates


DEFAULT_PARTITIONS = [10, 12, 15, 17, 18, 19, 20, 22, 23, 24, 25]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--partitions", type=int, nargs="*", default=DEFAULT_PARTITIONS)
    args = parser.parse_args()
    _labels, label_index, _variables, _edge = coordinates()
    records = []
    input_status = []
    seen = set()
    for partition_index in args.partitions:
        source_path = Path(
            f"scratch_general_e72_q3_local_expansion_part_{partition_index:02d}.json"
        )
        if not source_path.exists():
            input_status.append({"partition_index": partition_index, "status": "ABSENT", "rows": 0})
            continue
        source = json.loads(source_path.read_text(encoding="utf-8"))
        assert source["partition_index"] == partition_index
        input_status.append({
            "partition_index": partition_index,
            "status": source["status"],
            "rows": len(source["rows"]),
        })
        for source_row_index, row in enumerate(source["rows"]):
            if int(row["after_forced_C4_support_BP"]) == 0:
                continue
            key = (partition_index, int(row["compression_orbit_index"]))
            assert key not in seen
            seen.add(key)
            record = normalize_row(
                row, partition_index, source_path, source_row_index, label_index
            )
            record["support_form"] = record["support_form"].replace(
                "E74-", "E72-Qge3-", 1
            )
            records.append(record)
    result = {
        "status": "E72_QGE3_PARTIAL_SNAPSHOT",
        "model": "normalized completed E0=72,Q>=3 local rows for exact SAT",
        "coverage_warning": (
            "Only the explicitly listed atomically completed partitions are covered; "
            "this snapshot alone is not a complete E0=72 exclusion."
        ),
        "input_status": input_status,
        "support_record_count": len(records),
        "local_representative_count": sum(len(record["representatives"]) for record in records),
        "labelled_local_graphs_represented": sum(record["local_graph_count"] for record in records),
        "records": records,
    }
    atomic_json(args.output, result)
    print(json.dumps({
        "status": result["status"],
        "output": str(args.output),
        "records": result["support_record_count"],
        "representatives": result["local_representative_count"],
        "raw_graphs": result["labelled_local_graphs_represented"],
    }))


if __name__ == "__main__":
    main()
