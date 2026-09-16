"""Normalize the ten positive E76 local-support rows for incremental SAT."""

from __future__ import annotations

import json
from pathlib import Path

from scratch_general_exact_sat import coordinates


INPUT = Path("scratch_e76_independent_local.json")
OUTPUT = Path("scratch_e76_incremental_records.json")


def main():
    source = json.loads(INPUT.read_text(encoding="utf-8"))
    labels, _label_index, _variables, _edge = coordinates()
    records = []
    for source_row_index, row in enumerate(source["rows"]):
        if not row["representatives"]:
            continue
        supports = tuple(
            tuple(item["support"]) for item in row["exceptional_supports"]
        )
        deficits = tuple(
            int(item["deficit"]) for item in row["exceptional_supports"]
        )
        assert deficits == tuple(row["deficits_in_support_order"])
        exceptional = set(supports)
        local_vertex_order = [
            {
                "symbol_label": list(label),
                "outer_index_zero_based": outer,
            }
            for outer, label in enumerate(labels)
            if tuple(symbol // 2 for symbol in label) in exceptional
        ]
        representatives = []
        for representative in row["representatives"]:
            index_edges = [
                list(map(int, edge))
                for edge in representative["edges_by_outer_index_zero_based"]
            ]
            symbol_edges = representative["edges_by_symbol_label"]
            assert len(index_edges) == len(symbol_edges) == representative["local_edge_count"]
            assert [
                [list(labels[u]), list(labels[v])] for u, v in index_edges
            ] == symbol_edges
            representatives.append({
                "representative_id": int(representative["representative_index"]),
                "orbit_size": int(representative["local_orbit_size"]),
                "present_edges_outer_indices_zero_based": index_edges,
            })
        assert len(representatives) == row["local_graph_orbits"]
        assert sum(item["orbit_size"] for item in representatives) == row["distinct_forced_local_graphs"]
        support_form = (
            "E76-partition-" + "+".join(map(str, row["partition"]))
            + f"-compression-orbit-{row['compression_orbit_index']}"
        )
        records.append({
            "support_form": support_form,
            "source_row_index": source_row_index,
            "compression_orbit_index": row["compression_orbit_index"],
            "partition": row["partition"],
            "deficits_in_support_order": list(deficits),
            "supports_in_fibre_order": [list(support) for support in supports],
            "local_vertex_order": local_vertex_order,
            "local_graph_count": row["distinct_forced_local_graphs"],
            "orbit_count_direct": row["local_graph_orbits"],
            "orbit_sizes": row["local_orbit_sizes"],
            "representatives": representatives,
        })
    assert len(records) == source["support_orbits_after_forced_BP"] == 10
    assert sum(len(record["representatives"]) for record in records) == source["local_graph_orbits"] == 311
    result = {
        "model": "normalized E76 local representatives for incremental exact SAT",
        "input": str(INPUT),
        "coverage": source["coverage"],
        "support_record_count": len(records),
        "local_representative_count": sum(len(record["representatives"]) for record in records),
        "records": records,
        "ok": True,
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": True,
        "records": len(records),
        "representatives": result["local_representative_count"],
        "counts": [len(record["representatives"]) for record in records],
    }))


if __name__ == "__main__":
    main()
