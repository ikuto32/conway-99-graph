"""Supplemental exact-integer disjoint-block screen for E0=76 port survivors."""

from __future__ import annotations

import json
from pathlib import Path

import scratch_general_e79_compression_audit as base


INPUT = Path("scratch_general_e76_port_audit.json")
OUTPUT = Path("scratch_root_e76_disjoint_integer.json")


def main():
    source = json.loads(INPUT.read_text(encoding="utf-8"))
    candidates = [
        row for row in source["rows"]
        if row["locally_port_feasible_assignments"]
    ]
    assert len(candidates) == 21
    rows = []
    for offset, row in enumerate(candidates):
        state = [0] * 21
        for item in row["exceptional_supports"]:
            state[item["support_index"]] = item["deficit"]
        # The relaxed overlap minimum is a lower bound for every actual
        # overlap completion, so this is the largest disjoint square budget
        # any lift of this support orbit could have.
        square_limit = (
            row["joint_square_budget"] - row["overlap_relaxed_minimum_square"]
        )
        result = base.disjoint_integer_minimum(tuple(state), square_limit)
        survives = result["status"] in ("OPTIMAL", "FEASIBLE")
        record = {
            "partition": row["partition"],
            "orbit_index": row["orbit_index"],
            "support_orbit_size": row["support_orbit_size"],
            "square_limit_after_relaxed_overlap": square_limit,
            "disjoint_integer": result,
            "survives_integer_disjoint_screen": survives,
        }
        rows.append(record)
        print(json.dumps({
            "offset": offset,
            "partition": record["partition"],
            "orbit_index": record["orbit_index"],
            "limit": square_limit,
            "status": result["status"],
            "minimum": result.get("minimum_square"),
        }), flush=True)
    output = {
        "model": "supplemental exact-integer disjoint-block E0=76 screen",
        "input": str(INPUT),
        "coverage": "all 21 support orbits surviving exact local port matchability",
        "claim_boundary": (
            "Positive rows are only compressed necessary witnesses.  Negative "
            "CP-SAT statuses have no independently checked proof certificates."
        ),
        "input_orbits": len(rows),
        "surviving_orbits": sum(
            row["survives_integer_disjoint_screen"] for row in rows
        ),
        "rows": rows,
    }
    OUTPUT.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "input_orbits": output["input_orbits"],
        "surviving_orbits": output["surviving_orbits"],
    }), flush=True)


if __name__ == "__main__":
    main()
