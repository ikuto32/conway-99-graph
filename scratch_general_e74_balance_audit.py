"""Independent census of the E0=74 weighted-port balance obstruction.

This reads only the atomically committed placement-orbit files.  It does not
run overlap recursion, and therefore gives a cheap exact stage boundary before
the more expensive compression filters.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import scratch_general_e74_compression as e74


OUTPUT = Path("scratch_general_e74_balance_audit.json")


def atomic_json(path, value):
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def main():
    e74.configure()
    g = e74.generic
    by_partition = []
    total_labelled = 0
    total_orbits = 0
    total_balanced_labelled = 0
    total_balanced_orbits = 0

    for index, partition in enumerate(e74.PARTITIONS):
        path = e74.part_path(index)
        part = json.loads(path.read_text(encoding="utf-8"))
        assert part["status"] in {"CLASSIFIED", "FILTERING", "COMPLETE"}
        assert part["partition_index"] == index
        assert tuple(part["partition"]) == partition
        labelled = g.labelled_count(partition)
        assert part["coverage"]["labelled_placements"] == labelled
        assert sum(row["orbit_size"] for row in part["rows"]) == labelled

        balanced_rows = []
        balanced_labelled = 0
        for row in part["rows"]:
            state = g.decode(int(row["representative_code_hex"], 16))
            assert sum(state) == e74.TOTAL_DEFICIT
            passes, details = g.weighted_port_balance(state)
            if passes:
                balanced_rows.append(row["orbit_index"])
                balanced_labelled += row["orbit_size"]
            if row.get("filter_complete"):
                assert row["weighted_port_balance"] == passes
                assert row["weighted_port_balance_details"] == details

        item = {
            "partition_index": index,
            "partition": list(partition),
            "labelled_placements": labelled,
            "placement_orbits": len(part["rows"]),
            "weighted_port_balanced_labelled_placements": balanced_labelled,
            "weighted_port_balanced_orbits": len(balanced_rows),
            "balanced_orbit_indices": balanced_rows,
            "source": str(path),
        }
        by_partition.append(item)
        total_labelled += labelled
        total_orbits += len(part["rows"])
        total_balanced_labelled += balanced_labelled
        total_balanced_orbits += len(balanced_rows)

    result = {
        "status": "VERIFIED",
        "model": "E0=74 all-placement weighted-S7 orbit and weighted-port census",
        "claim_type": "solver-free exhaustive finite computation plus analytic obstruction",
        "analytic_obstruction": (
            "For each root group g, every deficit port incident with a fibre F "
            "must be paired through an overlap edge to a port of another fibre "
            "incident with g. Thus max_F(delta_F)<=sum_{H!=F}(delta_H), "
            "equivalently 2*max<=sum. This condition is orientation-independent."
        ),
        "coverage": {
            "partitions": len(e74.PARTITIONS),
            "labelled_placements": total_labelled,
            "placement_orbits": total_orbits,
            "orbit_size_sum": total_labelled,
            "classification": (
                "all repeated-weight-unlabelled placements on 21 supports; exact "
                "images under all 5040 S7 actions; weighted state preserved"
            ),
        },
        "weighted_port_balance": {
            "labelled_placements": total_balanced_labelled,
            "orbits": total_balanced_orbits,
        },
        "by_partition": by_partition,
    }
    atomic_json(OUTPUT, result)
    print(json.dumps({key: result[key] for key in ("status", "coverage", "weighted_port_balance")}))


if __name__ == "__main__":
    main()
