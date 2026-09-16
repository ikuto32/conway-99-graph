"""Exhaustive direct-matching check of every E75 group signature domain."""

from __future__ import annotations

import itertools
import json
from pathlib import Path

import scratch_general_e75_port_audit as port75
import scratch_general_e78_port_audit as e78


INPUT_PATH = Path("scratch_general_e75_compression_audit.json")
OUTPUT_PATH = Path("scratch_general_e75_port_group_check.json")


def synthetic_ports(signatures):
    ports = []
    vertex = 0
    categories = ((0, 0), (0, 1), (1, 0), (1, 1))
    for fibre, signature in enumerate(signatures):
        for multiplicity, (sigma, required) in zip(signature, categories):
            for _ in range(multiplicity):
                ports.append((0, fibre, vertex, sigma, required))
                vertex += 1
    return tuple(ports)


def main():
    source = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    survivors = [
        row
        for row in source["rows"]
        if row["passes_weighted_port_overlap_and_real_relaxation"]
    ]
    assert len(survivors) == 96
    layouts = set()
    for row in survivors:
        for group in range(7):
            incident = []
            for item in row["exceptional_supports"]:
                support = tuple(item["support"])
                if group in support:
                    incident.append((item["deficit"], support.index(group)))
            if incident:
                layouts.add(tuple(sorted(incident)))
    rows = []
    total_assignments = 0
    total_unique_signatures = 0
    for layout in sorted(layouts):
        domains = [range(len(port75.FIBRE_STATES[deficit])) for deficit, _axis in layout]
        seen = set()
        assignments = 0
        hall_positive = 0
        for state_indices in itertools.product(*domains):
            assignments += 1
            signatures = tuple(
                port75.SIGNATURES[deficit][state_index][axis]
                for (deficit, axis), state_index in zip(layout, state_indices)
            )
            if signatures in seen:
                continue
            seen.add(signatures)
            hall = port75.group_matchable_signatures(signatures)
            direct = e78.direct_matching_exists(synthetic_ports(signatures))
            assert hall == direct
            hall_positive += hall
        total_assignments += assignments
        total_unique_signatures += len(seen)
        rows.append(
            {
                "incident_deficit_axis_layout": [list(item) for item in layout],
                "labelled_state_assignments_covered": assignments,
                "unique_signature_rows_checked": len(seen),
                "matchable_unique_signatures": hall_positive,
                "hall_equals_direct_DFS": True,
            }
        )
    result = {
        "status": "VERIFIED",
        "model": "all E0=75 root-group signature domains: Hall formula versus direct perfect-matching DFS",
        "input": str(INPUT_PATH),
        "support_survivors_scanned": len(survivors),
        "distinct_incident_deficit_axis_layouts": len(rows),
        "labelled_group_state_assignments_covered": total_assignments,
        "unique_signature_rows_checked": total_unique_signatures,
        "rows": rows,
    }
    OUTPUT_PATH.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("status", "distinct_incident_deficit_axis_layouts", "labelled_group_state_assignments_covered", "unique_signature_rows_checked")}))


if __name__ == "__main__":
    main()
