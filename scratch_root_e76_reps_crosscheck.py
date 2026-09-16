"""Cross-check the two independently generated E0=76 representative lists."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


GENERAL = Path("scratch_general_e76_local_graph_reps.json")
INDEPENDENT = Path("scratch_e76_independent_local.json")
OUTPUT = Path("scratch_root_e76_reps_crosscheck.json")


def canonical_general(row):
    return {
        (
            tuple((tuple(left), tuple(right)) for left, right in rep["edges"]),
            rep["orbit_size"],
        )
        for rep in row["representatives"]
    }


def canonical_independent(row):
    return {
        (
            tuple(
                (tuple(left), tuple(right))
                for left, right in rep["edges_by_symbol_label"]
            ),
            rep["local_orbit_size"],
        )
        for rep in row["representatives"]
    }


def digest(value):
    payload = json.dumps(sorted(value), separators=(",", ":")).encode("ascii")
    return hashlib.sha256(payload).hexdigest().upper()


def main():
    general = json.loads(GENERAL.read_text(encoding="utf-8"))
    independent = json.loads(INDEPENDENT.read_text(encoding="utf-8"))
    independent_rows = {
        (tuple(sorted(row["partition"], reverse=True)), row["compression_orbit_index"]): row
        for row in independent["rows"]
        if row["representatives"]
    }
    assert len(general["support_rows"]) == len(independent_rows) == 10
    rows = []
    for row in general["support_rows"]:
        key = (tuple(sorted(row["partition"], reverse=True)), row["orbit_index"])
        other = independent_rows[key]
        left = canonical_general(row)
        right = canonical_independent(other)
        identical = left == right
        assert identical
        rows.append({
            "partition": list(key[0]),
            "compression_orbit_index": key[1],
            "general_representatives": len(left),
            "independent_representatives": len(right),
            "representative_edge_and_orbit_size_sha256": digest(left),
            "identical": identical,
        })
    result = {
        "model": "explicit cross-check of two independent E0=76 local representative sets",
        "inputs": [str(GENERAL), str(INDEPENDENT)],
        "support_rows": len(rows),
        "representatives": sum(row["general_representatives"] for row in rows),
        "all_explicit_edge_sets_and_orbit_sizes_identical": all(
            row["identical"] for row in rows
        ),
        "rows": rows,
    }
    assert result["representatives"] == 311
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "support_rows": result["support_rows"],
        "representatives": result["representatives"],
        "identical": result["all_explicit_edge_sets_and_orbit_sizes_identical"],
    }))


if __name__ == "__main__":
    main()
