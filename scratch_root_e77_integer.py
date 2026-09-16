"""Independent bounded-integer disjoint screen for E0=77 candidates."""

from __future__ import annotations

import json
from pathlib import Path

from scratch_general_e79_compression_audit import (
    SUPPORTS,
    disjoint_integer_minimum,
)


def main():
    source = json.loads(Path("scratch_root_e77_screen.json").read_text(encoding="utf-8"))
    rows = []
    for index, row in enumerate(source["passing_rows"]):
        state = [0] * len(SUPPORTS)
        for item in row["exceptional_supports"]:
            assert tuple(item["support"]) == SUPPORTS[item["support_index"]]
            state[item["support_index"]] = item["deficit"]
        budget = row["joint_square_budget"] - row["overlap_minimum_square"]
        result = disjoint_integer_minimum(tuple(state), budget)
        passes = result["status"] in ("OPTIMAL", "FEASIBLE")
        out = dict(row)
        out.update({
            "disjoint_square_budget": budget,
            "disjoint_integer": result,
            "passes_integer_screen": passes,
        })
        rows.append(out)
        print(json.dumps({
            "index": index,
            "partition": row["partition"],
            "orbit": row["orbit_index"],
            "budget": budget,
            "status": result["status"],
            "minimum": result.get("minimum_square"),
        }), flush=True)
    output = {
        "model": "independent E0=77 bounded integer disjoint compression screen",
        "input": "scratch_root_e77_screen.json",
        "claim_boundary": (
            "CP-SAT bounded integer decisions have direct positive witness checks; "
            "UNSAT results have no external proof certificates"
        ),
        "input_rows": len(source["passing_rows"]),
        "passing_rows": sum(r["passes_integer_screen"] for r in rows),
        "rows": rows,
    }
    Path("scratch_root_e77_integer.json").write_text(
        json.dumps(output, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "input_rows": output["input_rows"],
        "passing_rows": output["passing_rows"],
    }), flush=True)


if __name__ == "__main__":
    main()
