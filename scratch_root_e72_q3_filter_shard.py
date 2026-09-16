"""Parallel row shard for the expensive E72 compression filter phase."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import time

import scratch_root_e72_q3_compression as e72


def atomic_json(path, value):
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--partition", type=int, required=True)
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--end", type=int, required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    e72.configure()
    generic = e72.generic
    source_path = e72.part_path(args.partition)
    source = json.loads(source_path.read_text(encoding="utf-8"))
    assert source["status"] in ("FILTERING_COMPRESSION", "COMPLETE")
    assert 0 <= args.start <= args.end <= len(source["rows"])
    rows = []
    started = time.monotonic()
    output = Path(args.output)
    for index in range(args.start, args.end):
        row = json.loads(json.dumps(source["rows"][index]))
        if not row.get("filter_complete"):
            generic.filter_row(row)
        rows.append({"row_index": index, "row": row})
        if len(rows) % 10 == 0:
            atomic_json(output, {
                "status": "RUNNING",
                "partition_index": args.partition,
                "start": args.start,
                "end": args.end,
                "completed": len(rows),
                "rows": rows,
            })
    result = {
        "status": "COMPLETE",
        "partition_index": args.partition,
        "start": args.start,
        "end": args.end,
        "completed": len(rows),
        "elapsed_seconds": round(time.monotonic() - started, 6),
        "rows": rows,
    }
    atomic_json(output, result)
    print(json.dumps({key: result[key] for key in (
        "status", "partition_index", "start", "end", "completed", "elapsed_seconds"
    )}), flush=True)


if __name__ == "__main__":
    main()
