"""Snapshot completed unconditional E74 local rows for exact incremental SAT.

The local expansion files are atomically rewritten after every support row.  This
utility reads a consistent snapshot, keeps only rows which have survived the
forced ordinary-C4 BP test, and emits the generic record format consumed by
``scratch_incremental_local_exact_sat.py``.  Snapshot files are intentionally
immutable by convention: choose a fresh ``--output`` name while solvers run.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from scratch_general_exact_sat import coordinates


def atomic_json(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def normalize_row(row: dict, partition_index: int, source_path: Path,
                  source_row_index: int, label_index: dict) -> dict:
    exceptional = row["exceptional_supports"]
    supports = tuple(tuple(item["support"]) for item in exceptional)
    deficits = tuple(int(item["deficit"]) for item in exceptional)
    support_set = set(supports)
    labels, _, _, _ = coordinates()
    local_vertex_order = [
        {"symbol_label": list(label), "outer_index_zero_based": outer}
        for outer, label in enumerate(labels)
        if tuple(sorted((label[0] // 2, label[1] // 2))) in support_set
    ]
    representatives = []
    for representative_index, representative in enumerate(
        row["local_graph_representatives"]
    ):
        label_edges = [
            (tuple(left), tuple(right)) for left, right in representative["edges"]
        ]
        index_edges = [
            list(sorted((label_index[left], label_index[right])))
            for left, right in label_edges
        ]
        assert len(index_edges) == len(set(map(tuple, index_edges)))
        representatives.append(
            {
                "representative_id": representative_index,
                "orbit_size": int(representative["orbit_size"]),
                "Q": int(representative["Q"]),
                "present_edges_outer_indices_zero_based": index_edges,
                "source_mask_hex": representative["mask_hex"],
            }
        )
    assert len(representatives) == int(row["local_graph_orbits"])
    assert sum(item["orbit_size"] for item in representatives) == int(
        row["after_forced_C4_support_BP"]
    )
    partition_word = "+".join(map(str, sorted(deficits, reverse=True)))
    return {
        "support_form": (
            f"E74-partition-{partition_word}-compression-orbit-"
            f"{row['compression_orbit_index']}"
        ),
        "source_artifact": str(source_path),
        "source_partition_index": partition_index,
        "source_row_index": source_row_index,
        "compression_orbit_index": int(row["compression_orbit_index"]),
        "partition": sorted(deficits, reverse=True),
        "deficits_in_support_order": list(deficits),
        "supports_in_fibre_order": [list(support) for support in supports],
        "local_vertex_order": local_vertex_order,
        "local_graph_count": int(row["after_forced_C4_support_BP"]),
        "orbit_count_direct": len(representatives),
        "orbit_sizes": [item["orbit_size"] for item in representatives],
        "Q_histogram": row["forced_BP_Q_histogram"],
        "representatives": representatives,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--partitions",
        type=int,
        nargs="*",
        default=[11, 14, 15, 16, 17, 18, 19, 20, 21, 22],
    )
    args = parser.parse_args()
    labels, label_index, _, _ = coordinates()
    del labels
    records = []
    input_status = []
    seen = set()
    for partition_index in args.partitions:
        source_path = Path(
            f"scratch_general_e74_local_expansion_part_{partition_index:02d}.json"
        )
        if not source_path.exists():
            input_status.append(
                {"partition_index": partition_index, "status": "ABSENT", "rows": 0}
            )
            continue
        source = json.loads(source_path.read_text(encoding="utf-8"))
        assert source["partition_index"] == partition_index
        input_status.append(
            {
                "partition_index": partition_index,
                "status": source["status"],
                "rows": len(source["rows"]),
            }
        )
        for source_row_index, row in enumerate(source["rows"]):
            if int(row["after_forced_C4_support_BP"]) == 0:
                continue
            key = (partition_index, int(row["compression_orbit_index"]))
            assert key not in seen
            seen.add(key)
            records.append(
                normalize_row(
                    row, partition_index, source_path, source_row_index, label_index
                )
            )
    result = {
        "status": "UNCONDITIONAL_PARTIAL_SNAPSHOT",
        "model": "normalized completed E0=74 local rows for generic exact SAT",
        "coverage_warning": (
            "This snapshot covers only the atomically completed rows listed in "
            "input_status; it is not an unconditional E0=74 sweep unless every "
            "expansion part is COMPLETE and all later representatives are solved."
        ),
        "input_status": input_status,
        "support_record_count": len(records),
        "local_representative_count": sum(
            len(record["representatives"]) for record in records
        ),
        "labelled_local_graphs_represented": sum(
            record["local_graph_count"] for record in records
        ),
        "records": records,
    }
    atomic_json(args.output, result)
    print(
        json.dumps(
            {
                "status": result["status"],
                "output": str(args.output),
                "records": len(records),
                "representatives": result["local_representative_count"],
                "raw_graphs": result["labelled_local_graphs_represented"],
            }
        )
    )


if __name__ == "__main__":
    main()
