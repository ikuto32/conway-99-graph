"""Apply the exact equitability-kernel/port filter to E72's largest open macros.

The coverage inventory identifies source 150 macros (4,0) and (7,0), each of
labelled coverage 524288, as the two largest individual open E72 macros after
the already audited exclusions.  This script applies only the one-root
84-vertex defect-row necessary conditions; it is not a full-SRG search.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import scratch_general_e72_q3_fast_expansion as fast
import scratch_theory_e71_defect_rank_probe as defect
import scratch_theory_e71_equitable_kernel_port_census as kernel


CATALOG = Path("scratch_general_e72_q3_gram_fast_expansion_macro_catalog.json")
MINING = Path("scratch_theory_e71_e72_e0_moment_mining.json")
INVENTORY = Path("scratch_root_e72_complete_coverage_inventory.json")
OUTPUT = Path("scratch_theory_e72_largest_open_defect_rank_probe.json")
SOURCE = 150
TARGET_KEYS = {(4, 0), (7, 0)}


def atomic_json(path: Path, value) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest().upper()


def macro_key(row):
    return (
        int(row["source_row_index"]),
        int(row["state_orbit_number"]),
        int(row["signature_stabilizer_orbit_number"]),
    )


def main() -> None:
    catalog_raw = CATALOG.read_bytes()
    mining_raw = MINING.read_bytes()
    inventory_raw = INVENTORY.read_bytes()
    catalog = json.loads(catalog_raw)
    mining = json.loads(mining_raw)
    inventory = json.loads(inventory_raw)

    entries = {
        macro_key(entry): entry for entry in catalog["macro_entries"]
        if entry["signature_stabilizer_canonical"]
        and int(entry["source_row_index"]) == SOURCE
        and (int(entry["state_orbit_number"]),
             int(entry["signature_stabilizer_orbit_number"])) in TARGET_KEYS
    }
    profiles = {}
    for profile in mining["profile_rows"]["72"]:
        key = macro_key(profile)
        if key in entries:
            profiles.setdefault(key, []).append(profile)
    assert len(entries) == len(profiles) == 2
    assert all(len(rows) == 1 for rows in profiles.values())

    inventory_macros = {
        tuple(row["macro"]): row
        for row in inventory["source150"]["macro_rows"]
    }
    assert all(inventory_macros[key]["status"] == "OPEN" for key in TARGET_KEYS)
    assert all(inventory_macros[key]["coverage"] == 524_288
               for key in TARGET_KEYS)

    preset = fast.PRESETS["e72gram"]
    fast.configure_generic(preset)
    _port, grouped = fast.input_rows(preset)
    source = next(
        row for rows in grouped.values() for row, _count in rows
        if int(row["source_row_index"]) == SOURCE
    )

    results = []
    for key in sorted(entries):
        entry = entries[key]
        profile = profiles[key][0]
        geometry = fast.RowGeometry(source)
        oriented = fast.oriented_assignment(geometry, entry["state_indices"])
        internal = fast.internal_mask(geometry, oriented)
        assert internal == int(entry["internal_mask_hex"], 16)
        domains = defect.exact_signature_domains(
            fast, geometry, oriented, entry
        )
        analysis = kernel.analyze_profile(
            entry, profile, source, geometry, oriented, domains, internal
        )
        results.append({
            "key": list(key),
            "Q": int(entry["Q"]),
            "coverage": int(entry["signature_orbit_labelled_coverage"]),
            "matching_completion_weight_per_state": int(
                entry["matching_completion_weight_per_state"]
            ),
            "group_domain_sizes": list(map(len, domains)),
            "analysis": analysis,
        })

    rejected = [row for row in results
                if not row["analysis"]["passes_kernel_port_CSP"]]
    result = {
        "status": "EXACT_E72_LARGEST_OPEN_DEFECT_RANK_PROBE_COMPLETE",
        "inputs": {
            str(CATALOG): sha256(catalog_raw),
            str(MINING): sha256(mining_raw),
            str(INVENTORY): sha256(inventory_raw),
        },
        "identity": "K4=16W^TW=28Z-Z^2",
        "pointwise_condition": (
            "8W[x,F]=4deg(x,F)-C[G,F]; every scaled vertex row lies "
            "in row(K4), with four rows per fibre summing to zero."
        ),
        "selection": {
            "reason": "two largest individual open macros in audited ledger",
            "source_row_index": SOURCE,
            "macro_keys": [list(key) for key in sorted(TARGET_KEYS)],
            "input_coverage": sum(row["coverage"] for row in results),
        },
        "summary": {
            "macros": len(results),
            "rejected_macros": len(rejected),
            "rejected_coverage": sum(row["coverage"] for row in rejected),
            "retained_macros": len(results) - len(rejected),
            "retained_coverage": sum(row["coverage"] for row in results)
                - sum(row["coverage"] for row in rejected),
        },
        "rows": results,
        "claim_boundary": (
            "A sound one-root necessary filter only. Passing macros remain open; "
            "no 99-vertex SAT or full pair-equation search is performed."
        ),
    }
    assert result["selection"]["input_coverage"] == 1_048_576
    assert result["summary"]["rejected_coverage"] + result["summary"][
        "retained_coverage"
    ] == result["selection"]["input_coverage"]
    atomic_json(OUTPUT, result)
    print(json.dumps({"path": str(OUTPUT), **result["summary"]}, sort_keys=True))


if __name__ == "__main__":
    main()
