"""Build a compact SAT frontier from the audited source133 completions."""

from __future__ import annotations

import hashlib
import itertools
import json
import os
from collections import Counter
from pathlib import Path


INPUT_PATH = Path("scratch_general_e72_source133_pointwise_completion.json")
OUTPUT_PATH = Path("scratch_general_e72_source133_pointwise_frontier.json")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def atomic_compact_json(path: Path, value) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(
        json.dumps(value, separators=(",", ":")) + "\n", encoding="utf-8"
    )
    temporary.replace(path)


def run() -> None:
    source = json.loads(INPUT_PATH.read_text(encoding="utf-8"))
    assert source["status"] == "COMPLETE"
    detailed = source["completed_graph_representatives"]
    masks = [int(row["mask_hex"], 16) for row in detailed]
    assert len(masks) == len(set(masks)) == source["summary"]["completed_graph_orbits"]
    assert all(mask.bit_count() == 48 for mask in masks)
    assert sum(row["orbit_size"] for row in detailed) == source["summary"][
        "completed_graph_orbit_mass"
    ]
    q_mass = Counter()
    q_orbits = Counter()
    macro_mass = Counter()
    macro_orbits = Counter()
    rows = []
    for row in detailed:
        q_mass[row["Q"]] += row["orbit_size"]
        q_orbits[row["Q"]] += 1
        macro_mass[row["state_macro_number"]] += row["orbit_size"]
        macro_orbits[row["state_macro_number"]] += 1
        rows.append(
            [
                row["mask_hex"],
                row["orbit_size"],
                row["Q"],
                row["state_macro_number"],
            ]
        )
    assert {str(q): value for q, value in sorted(q_mass.items())} == source[
        "summary"
    ]["completed_graph_Q_mass_histogram"]
    assert {str(q): value for q, value in sorted(q_orbits.items())} == source[
        "summary"
    ]["completed_graph_Q_orbit_histogram"]
    for macro in source["macro_summary"]:
        number = macro["state_macro_number"]
        assert macro_orbits[number] == macro["completed_graph_orbits"]
        assert macro_mass[number] == macro["after_induced_pair_upper_labelled_mass"]

    vertices = source["vertex_order_for_masks"]
    assert len(vertices) == 24
    assert len(tuple(itertools.combinations(vertices, 2))) == 276
    result = {
        "status": "COMPLETE",
        "model": "source133 pointwise-balanced exceptional-layer SAT frontier",
        "input": {"path": str(INPUT_PATH), "sha256": sha256(INPUT_PATH)},
        "source_row_index": 133,
        "partition_index": 27,
        "compression_orbit_index": 0,
        "exceptional_support_order": source["exceptional_support_order"],
        "vertex_order": vertices,
        "mask_encoding": (
            "bit i is the edge at index i in combinations(vertex_order,2), "
            "in Python itertools.combinations order"
        ),
        "representative_fields": [
            "mask_hex",
            "labelled_orbit_size",
            "Q",
            "state_macro_number",
        ],
        "summary": {
            "exceptional_edges_per_representative": 48,
            "completed_graph_orbits": len(rows),
            "completed_graph_orbit_mass": sum(q_mass.values()),
            "Q_mass_histogram": {
                str(q): value for q, value in sorted(q_mass.items())
            },
            "Q_orbit_histogram": {
                str(q): value for q, value in sorted(q_orbits.items())
            },
            "macro_mass_histogram": {
                str(macro): value for macro, value in sorted(macro_mass.items())
            },
            "macro_orbit_histogram": {
                str(macro): value for macro, value in sorted(macro_orbits.items())
            },
            "all_masks_distinct": True,
            "all_orbit_mass_identities_verified": True,
        },
        "representatives": rows,
        "claim_boundary": source["claim_boundary"],
    }
    atomic_compact_json(OUTPUT_PATH, result)
    print(json.dumps({"path": str(OUTPUT_PATH), **result["summary"]}), flush=True)


if __name__ == "__main__":
    run()
