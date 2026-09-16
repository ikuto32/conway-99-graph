"""Independent exhaustive local port screen for E0=77 integer survivors."""

from __future__ import annotations

from collections import Counter
import itertools
import json
from pathlib import Path

from scratch_general_e78_port_audit import (
    FIBRE_STATES as E78_STATES,
    PAIRS,
    VERTICES,
    assignment_ports,
    group_matchable,
)


FIBRE_STATES = {
    1: E78_STATES[1],
    2: E78_STATES[2],
    3: tuple({
        "edges": (edge,),
        "type": "one_side" if
        sum(a != b for a, b in zip(VERTICES[edge[0]], VERTICES[edge[1]])) == 1
        else "one_diagonal",
    } for edge in PAIRS),
}
assert tuple(map(len, (FIBRE_STATES[1], FIBRE_STATES[2], FIBRE_STATES[3]))) == (4, 7, 6)


def main():
    source = json.loads(Path("scratch_root_e77_integer.json").read_text(encoding="utf-8"))
    candidates = [row for row in source["rows"] if row["passes_integer_screen"]]
    assert len(candidates) == 165
    output = []
    for index, row in enumerate(candidates):
        exceptional = row["exceptional_supports"]
        domains = [FIBRE_STATES[item["deficit"]] for item in exceptional]
        total = 1
        for domain in domains:
            total *= len(domain)
        feasible = 0
        types = Counter()
        first = None
        for choices in itertools.product(*domains):
            ports = assignment_ports(exceptional, choices)
            if not all(group_matchable(group_ports) for group_ports in ports):
                continue
            feasible += 1
            key = tuple(choice["type"] for choice in choices)
            types[key] += 1
            if first is None:
                first = {
                    "state_indices": [
                        domain.index(choice) for domain, choice in zip(domains, choices)
                    ],
                    "types": list(key),
                    "port_counts_by_group": [len(items) for items in ports],
                }
        out = {
            "partition": row["partition"],
            "orbit_index": row["orbit_index"],
            "orbit_size": row["orbit_size"],
            "exceptional_supports": exceptional,
            "labelled_fibre_state_assignments": total,
            "locally_port_feasible_assignments": feasible,
            "feasible_type_histogram": {
                "|".join(key): value for key, value in sorted(types.items())
            },
            "first_feasible": first,
        }
        output.append(out)
        print(json.dumps({
            "index": index,
            "partition": row["partition"],
            "orbit": row["orbit_index"],
            "total": total,
            "feasible": feasible,
        }), flush=True)
    result = {
        "model": "independent exhaustive E0=77 labelled fibre-state port screen",
        "input": "scratch_root_e77_integer.json",
        "fibre_state_counts": {"delta1": 4, "delta2": 7, "delta3": 6},
        "coverage": "all products of all labelled locally allowed fibre edge states",
        "claim_boundary": (
            "Closed-form exact port matchability only; no spectral matching-cost "
            "or full lift is asserted for positive rows."
        ),
        "input_orbits": len(output),
        "surviving_orbits": sum(r["locally_port_feasible_assignments"] > 0 for r in output),
        "rows": output,
    }
    Path("scratch_root_e77_port_screen.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({
        "input_orbits": result["input_orbits"],
        "surviving_orbits": result["surviving_orbits"],
    }), flush=True)


if __name__ == "__main__":
    main()
