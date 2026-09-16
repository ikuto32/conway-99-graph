"""Merge complete E72 compression filter shards into partition 31."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import scratch_root_e72_q3_compression as e72


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--partition", type=int, default=31)
    parser.add_argument("--glob", default="scratch_root_e72_q3_filter_part31_shard*.json")
    args = parser.parse_args()
    e72.configure()
    generic = e72.generic
    path = e72.part_path(args.partition)
    source = json.loads(path.read_text(encoding="utf-8"))
    replacements = {}
    artifacts = []
    for shard_path in sorted(Path(".").glob(args.glob)):
        shard = json.loads(shard_path.read_text(encoding="utf-8"))
        assert shard["status"] == "COMPLETE"
        assert shard["partition_index"] == args.partition
        assert shard["completed"] == shard["end"] - shard["start"]
        for item in shard["rows"]:
            index = item["row_index"]
            assert shard["start"] <= index < shard["end"]
            assert index not in replacements
            assert item["row"]["filter_complete"]
            replacements[index] = item["row"]
        artifacts.append(str(shard_path))
    assert set(replacements) == set(range(len(source["rows"])))
    source["rows"] = [replacements[index] for index in range(len(source["rows"]))]
    source["summary"] = generic.summarize_rows(source["rows"])
    source["status"] = "COMPLETE"
    generic.refresh_scope_fields(source)
    assert source["summary"]["filter_rows_complete"] == len(source["rows"])
    assert source["summary"]["balanced_labelled_placements"] == source["coverage"][
        "balanced_labelled_placements"
    ]
    source["parallel_filter_shards"] = artifacts
    generic.atomic_json(path, source)
    print(json.dumps({
        "status": source["status"],
        "partition_index": args.partition,
        **source["summary"],
        "shards": len(artifacts),
    }, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
