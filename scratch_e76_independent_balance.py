"""Independent aggregate and orientation-free port-balance audit for E0=76.

No E0=76 port-screen implementation is imported or read.  The sole input is
the compression JSON.  For each matched-pair group, a fibre of deficit d
contributes exactly 2d missing symbol ports, independently of its labelled
orientation.  Since overlap edges pair ports belonging to distinct fibres,
the largest incident deficit cannot exceed the sum of all other incident
deficits.
"""

from __future__ import annotations

from collections import defaultdict
import json
from pathlib import Path


INPUT = Path("scratch_general_e76_compression_audit.json")
OUTPUT = Path("scratch_e76_independent_balance.json")


def partition_key(row):
    return "+".join(map(str, row["partition"]))


def group_balance(row):
    diagnostics = []
    ok = True
    for group in range(7):
        incident = [
            item["deficit"]
            for item in row["exceptional_supports"]
            if group in item["support"]
        ]
        total = sum(incident)
        largest = max(incident, default=0)
        balanced = largest <= total - largest
        ok &= balanced
        diagnostics.append({
            "group": group,
            "incident_deficits": incident,
            "largest": largest,
            "sum_others": total - largest,
            "balanced": balanced,
        })
    return bool(ok), diagnostics


def main():
    source = json.loads(INPUT.read_text(encoding="utf-8"))
    rows = source["rows"]
    assert source["theorem_inputs"]["total_deficit"] == 8
    assert all(row["orbit_size"] * row["stabilizer_order"] == 5040 for row in rows)

    grouped = defaultdict(lambda: {
        "orbit_count": 0,
        "labelled_placements": 0,
        "real_pass_orbits": 0,
        "real_pass_labelled_placements": 0,
        "balanced_orbits": 0,
        "balanced_labelled_placements": 0,
    })
    real_rows = []
    survivors = []
    for row in rows:
        key = partition_key(row)
        group = grouped[key]
        group["orbit_count"] += 1
        group["labelled_placements"] += row["orbit_size"]
        if not row["passes_overlap_and_real_relaxation"]:
            continue
        real_rows.append(row)
        group["real_pass_orbits"] += 1
        group["real_pass_labelled_placements"] += row["orbit_size"]
        balanced, diagnostics = group_balance(row)
        if balanced:
            group["balanced_orbits"] += 1
            group["balanced_labelled_placements"] += row["orbit_size"]
            survivors.append({
                "partition": row["partition"],
                "orbit_index": row["orbit_index"],
                "orbit_size": row["orbit_size"],
                "stabilizer_order": row["stabilizer_order"],
                "exceptional_supports": row["exceptional_supports"],
                "group_balance": diagnostics,
            })

    totals = {
        "orbit_count": len(rows),
        "labelled_placements": sum(row["orbit_size"] for row in rows),
        "real_pass_orbits": len(real_rows),
        "real_pass_labelled_placements": sum(row["orbit_size"] for row in real_rows),
        "balanced_orbits": len(survivors),
        "balanced_labelled_placements": sum(row["orbit_size"] for row in survivors),
    }
    assert totals["orbit_count"] == 1260
    assert totals["labelled_placements"] == 3_070_914
    assert totals["real_pass_orbits"] == 639
    assert totals["balanced_orbits"] == 36
    expected_balanced = {
        "2+2+2+2": 1,
        "2+2+2+1+1": 1,
        "2+2+1+1+1+1": 4,
        "2+1+1+1+1+1+1": 8,
        "1+1+1+1+1+1+1+1": 22,
    }
    assert {
        key: value["balanced_orbits"]
        for key, value in grouped.items()
        if value["balanced_orbits"]
    } == expected_balanced

    result = {
        "model": "independent E0=76 aggregate and orientation-free port-balance audit",
        "input": str(INPUT),
        "derivation": (
            "a deficit-d fibre has 2d missing BP ports in each support group; "
            "ports must pair across distinct fibres, so max incident deficit <= sum others"
        ),
        "totals": totals,
        "by_partition": dict(sorted(grouped.items())),
        "balanced_survivors": survivors,
        "existing_E76_port_code_read_or_imported": False,
        "ok": True,
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "ok": True,
        "totals": totals,
        "balanced_by_partition": expected_balanced,
    }))


if __name__ == "__main__":
    main()
