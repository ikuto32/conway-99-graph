"""Normalize conditional-priority E74 Q>=5 representatives for exact SAT."""

from __future__ import annotations

import json
import os
from pathlib import Path

from scratch_general_exact_sat import coordinates


INPUT_PATH = Path("scratch_general_e74_q5_local_graph_reps.json")
OUTPUT_PATH = Path("scratch_general_e74_q5_incremental_records.json")


def atomic_json(path, value):
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def main():
    source = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    assert source["status"] == "COMPLETE"
    assert len(source["support_rows"]) == 1
    labels, label_index, _variables, _edge = coordinates()
    records = []
    for source_row_index, row in enumerate(source["support_rows"]):
        exceptional = row["exceptional_supports"]
        supports = tuple(tuple(item["support"]) for item in exceptional)
        deficits = tuple(int(item["deficit"]) for item in exceptional)
        support_set = set(supports)
        local_vertex_order = [
            {"symbol_label": list(label), "outer_index_zero_based": outer}
            for outer, label in enumerate(labels)
            if tuple(sorted((label[0] // 2, label[1] // 2))) in support_set
        ]
        representatives = []
        for representative_index, representative in enumerate(row["representatives"]):
            assert representative["Q"] >= 5
            label_edges = [(tuple(left), tuple(right)) for left, right in representative["edges"]]
            index_edges = [
                list(sorted((label_index[left], label_index[right])))
                for left, right in label_edges
            ]
            assert len(index_edges) == len(set(map(tuple, index_edges)))
            representatives.append({
                "representative_id": representative_index,
                "orbit_size": representative["orbit_size"],
                "Q": representative["Q"],
                "present_edges_outer_indices_zero_based": index_edges,
                "source_mask_hex": representative["mask_hex"],
            })
        assert len(representatives) == row["orbit_count"] == 188
        assert sum(item["orbit_size"] for item in representatives) == row["raw_survivors"] == 16384
        records.append({
            "support_form": (
                "E74-CONDITIONAL-Qge5-partition-2+2+2+2+1+1-"
                f"compression-orbit-{row['compression_orbit_index']}"
            ),
            "source_row_index": source_row_index,
            "compression_orbit_index": row["compression_orbit_index"],
            "partition": sorted(deficits, reverse=True),
            "deficits_in_support_order": list(deficits),
            "supports_in_fibre_order": [list(support) for support in supports],
            "local_vertex_order": local_vertex_order,
            "local_graph_count": row["raw_survivors"],
            "orbit_count_direct": row["orbit_count"],
            "orbit_sizes": [item["orbit_size"] for item in representatives],
            "representatives": representatives,
        })
    result = {
        "status": "CONDITIONAL_PRIORITY_SUBCASE",
        "model": "normalized E0=74 Q>=5 local representatives for exact SAT",
        "premise_warning": (
            "Q>=5 is supplied only as an externally-premised search priority; "
            "this file cannot support an unconditional E0=74 exclusion"
        ),
        "input": str(INPUT_PATH),
        "support_record_count": 1,
        "local_representative_count": 188,
        "labelled_local_graphs_represented": 16384,
        "records": records,
    }
    atomic_json(OUTPUT_PATH, result)
    for index in range(4):
        probe_record = dict(records[0])
        representative = records[0]["representatives"][index]
        probe_record["representatives"] = [representative]
        probe_record["orbit_count_direct"] = 1
        probe_record["orbit_sizes"] = [representative["orbit_size"]]
        probe_record["local_graph_count"] = representative["orbit_size"]
        probe_record["support_form"] += f"-probe-representative-{index}"
        atomic_json(
            Path(f"scratch_general_e74_q5_probe_{index:02d}_record.json"),
            {
                "status": "PROBE_ONLY_CONDITIONAL_PRIORITY_SUBCASE",
                "coverage_warning": "one of 188 Q>=5 representatives only",
                "record": probe_record,
            },
        )
    print(json.dumps({
        "status": result["status"],
        "records": 1,
        "representatives": 188,
        "raw_graphs": 16384,
        "probe_files": 4,
    }))


if __name__ == "__main__":
    main()
