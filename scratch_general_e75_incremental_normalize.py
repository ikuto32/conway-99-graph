"""Normalize the six E75 local-support rows for generic incremental SAT."""

from __future__ import annotations

import json
from pathlib import Path

from scratch_general_exact_sat import coordinates


INPUT_PATH = Path("scratch_general_e75_local_graph_reps.json")
OUTPUT_PATH = Path("scratch_general_e75_incremental_records.json")
PROBE_PATH = Path("scratch_general_e75_incremental_probe_records.json")


def main():
    source = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    labels, label_index, _variables, _edge = coordinates()
    records = []
    for source_row_index, row in enumerate(source["support_rows"]):
        exceptional = row["exceptional_supports"]
        supports = tuple(tuple(item["support"]) for item in exceptional)
        deficits = tuple(int(item["deficit"]) for item in exceptional)
        support_set = set(supports)
        local_vertex_order = [
            {
                "symbol_label": list(label),
                "outer_index_zero_based": outer,
            }
            for outer, label in enumerate(labels)
            if tuple(sorted((label[0] // 2, label[1] // 2))) in support_set
        ]
        representatives = []
        for representative_index, representative in enumerate(row["representatives"]):
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
                    "orbit_size": representative["orbit_size"],
                    "present_edges_outer_indices_zero_based": index_edges,
                    "source_mask_hex": representative["mask_hex"],
                }
            )
        assert len(representatives) == row["orbit_count"]
        assert sum(item["orbit_size"] for item in representatives) == row[
            "raw_survivors"
        ]
        partition_word = "+".join(map(str, sorted(deficits, reverse=True)))
        records.append(
            {
                "support_form": (
                    f"E75-partition-{partition_word}-compression-orbit-"
                    f"{row['compression_orbit_index']}"
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
            }
        )
    assert len(records) == 6
    assert sum(len(record["representatives"]) for record in records) == 352
    result = {
        "status": "COMPLETE",
        "model": "normalized E75 local representatives for generic incremental exact SAT",
        "input": str(INPUT_PATH),
        "support_record_count": len(records),
        "local_representative_count": 352,
        "labelled_local_graphs_represented": sum(
            record["local_graph_count"] for record in records
        ),
        "records": records,
    }
    OUTPUT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    probe_records = []
    for record in records:
        probe = dict(record)
        probe["representatives"] = [record["representatives"][0]]
        probe["orbit_count_direct"] = 1
        probe["orbit_sizes"] = [record["representatives"][0]["orbit_size"]]
        probe["local_graph_count"] = record["representatives"][0]["orbit_size"]
        probe["support_form"] += "-first-representative-probe"
        probe_records.append(probe)
    probe_result = {
        "status": "PROBE_ONLY",
        "model": "one first representative from each of six E75 support rows",
        "full_input": str(OUTPUT_PATH),
        "coverage_warning": "not a complete E0=75 sweep; exactly one representative per support row",
        "support_record_count": 6,
        "local_representative_count": 6,
        "records": probe_records,
    }
    PROBE_PATH.write_text(json.dumps(probe_result, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": "COMPLETE",
                "records": len(records),
                "representatives": 352,
                "raw_graphs": result["labelled_local_graphs_represented"],
                "probe_records": len(probe_records),
            }
        )
    )


if __name__ == "__main__":
    main()
