"""Exact one-root defect-row census of the current E72 open macro frontier.

The input set is derived, rather than hand listed, from the hash-bound coverage
inventory: every OPEN source-150 macro and every macro belonging to an
``other_active_open_rows`` source.  Passing this filter is not realization.
"""

from __future__ import annotations

from collections import Counter, defaultdict
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
OUTPUT = Path("scratch_theory_e72_open_defect_rank_census.json")


def atomic_json(path: Path, value) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest().upper()


def key(row):
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
    assert inventory["status"] == "COMPLETE_E72_COVERAGE_INVENTORY_PASS"

    open150 = {
        tuple(row["macro"]) for row in inventory["source150"]["macro_rows"]
        if row["status"] == "OPEN"
    }
    other_sources = {
        int(row["source_row_index"])
        for row in inventory["other_active_open_rows"]
    }
    entries = {
        key(entry): entry for entry in catalog["macro_entries"]
        if entry["signature_stabilizer_canonical"] and (
            (int(entry["source_row_index"]) == 150
             and (int(entry["state_orbit_number"]),
                  int(entry["signature_stabilizer_orbit_number"])) in open150)
            or int(entry["source_row_index"]) in other_sources
        )
    }
    profiles = defaultdict(list)
    for profile in mining["profile_rows"]["72"]:
        if key(profile) in entries:
            profiles[key(profile)].append(profile)
    assert set(profiles) == set(entries)
    expected_coverage = inventory["global"]["unresolved_or_pending_coverage"]
    assert sum(int(entry["signature_orbit_labelled_coverage"])
               for entry in entries.values()) == expected_coverage == 2_236_416

    preset = fast.PRESETS["e72gram"]
    fast.configure_generic(preset)
    _port, grouped = fast.input_rows(preset)
    sources = {
        int(row["source_row_index"]): row
        for rows in grouped.values() for row, _count in rows
        if int(row["source_row_index"]) in ({150} | other_sources)
    }
    assert {macro_key[0] for macro_key in entries} <= set(sources)

    rows = []
    for number, macro_key in enumerate(sorted(entries), 1):
        entry = entries[macro_key]
        source = sources[macro_key[0]]
        geometry = fast.RowGeometry(source)
        oriented = fast.oriented_assignment(geometry, entry["state_indices"])
        internal = fast.internal_mask(geometry, oriented)
        assert internal == int(entry["internal_mask_hex"], 16)
        domains = defect.exact_signature_domains(fast, geometry, oriented, entry)
        analyses = [
            kernel.analyze_profile(
                entry, profile, source, geometry, oriented, domains, internal
            )
            for profile in profiles[macro_key]
        ]
        passes = any(row["passes_kernel_port_CSP"] for row in analyses)
        rows.append({
            "key": list(macro_key),
            "Q": int(entry["Q"]),
            "coverage": int(entry["signature_orbit_labelled_coverage"]),
            "profile_count": len(analyses),
            "profiles": analyses,
            "passes_some_full_Gram_profile_kernel_port_CSP": passes,
        })
        if number % 10 == 0:
            print(json.dumps({"processed": number, "total": len(entries)}),
                  flush=True)

    rejected = [row for row in rows
                if not row["passes_some_full_Gram_profile_kernel_port_CSP"]]
    retained = [row for row in rows
                if row["passes_some_full_Gram_profile_kernel_port_CSP"]]
    result = {
        "status": "EXACT_E72_OPEN_DEFECT_RANK_CENSUS_COMPLETE",
        "inputs": {
            str(CATALOG): sha256(catalog_raw),
            str(MINING): sha256(mining_raw),
            str(INVENTORY): sha256(inventory_raw),
        },
        "selection": {
            "source150_open_macro_count": len(open150),
            "other_open_source_count": len(other_sources),
            "canonical_macro_count": len(rows),
            "coverage": sum(row["coverage"] for row in rows),
        },
        "summary": {
            "profiles": sum(row["profile_count"] for row in rows),
            "rejected_macros": len(rejected),
            "rejected_source_rows": len({row["key"][0] for row in rejected}),
            "rejected_coverage": sum(row["coverage"] for row in rejected),
            "retained_macros": len(retained),
            "retained_coverage": sum(row["coverage"] for row in retained),
            "rank_histogram_profiles": dict(Counter(
                str(profile["K4_rank"])
                for row in rows for profile in row["profiles"]
            )),
            "Q_histogram_rejected_coverage": {
                str(q): sum(row["coverage"] for row in rejected if row["Q"] == q)
                for q in sorted({row["Q"] for row in rejected})
            },
        },
        "rows": rows,
        "claim_boundary": (
            "Exact one-root necessary conditions only; retained coverage stays "
            "open and rejected coverage requires inventory integration/audit."
        ),
    }
    assert result["summary"]["rejected_coverage"] + result["summary"][
        "retained_coverage"
    ] == result["selection"]["coverage"] == expected_coverage
    atomic_json(OUTPUT, result)
    print(json.dumps({"path": str(OUTPUT), **result["selection"],
                      **result["summary"]}, sort_keys=True))


if __name__ == "__main__":
    main()
