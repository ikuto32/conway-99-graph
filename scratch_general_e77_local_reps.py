"""Serialize and recheck the three exact E0=77 local graph representatives."""

from __future__ import annotations

import json
from pathlib import Path

from scratch_general_e77_exact_sat import source_record


OUTPUT_PATH = Path("scratch_general_e77_local_reps.json")


def main():
    record = source_record()
    assert record["orbit_count_direct"] == record["orbit_count_burnside"] == 3
    assert sum(record["orbit_sizes"]) == record["local_graph_count"] == 512
    result = {
        "model": "exact E0=77 orbit-22 local representative coverage",
        "input": "scratch_root_e77_local.json",
        "action_audit": (
            "the full setwise support stabilizer and coordinate-flip action is "
            "recomputed; representative image sets are pairwise disjoint and sum to 512"
        ),
        "record": record,
    }
    OUTPUT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "orbits": record["orbit_count_direct"],
        "orbit_sizes": record["orbit_sizes"],
        "sum": sum(record["orbit_sizes"]),
    }))


if __name__ == "__main__":
    main()
