"""Hash-bound exact coverage audit for source150 macro (2,0)."""

from __future__ import annotations

from pathlib import Path

import scratch_root_e72_source150_m47_shard_audit as shared


MACRO = (2, 0)
SHARDS = (
    (Path("scratch_theory_e72_source150_sync_localpair_m20_r0_128.json"),
     set(range(0, 128))),
    (Path("scratch_theory_e72_source150_sync_localpair_m20_r128_256.json"),
     set(range(128, 256))),
    (Path("scratch_theory_e72_source150_sync_localpair_m20_r256_384.json"),
     set(range(256, 384))),
    (Path("scratch_theory_e72_source150_sync_localpair_m20_r384_512.json"),
     set(range(384, 512))),
    (Path("scratch_theory_e72_source150_sync_localpair_m20_r512_576.json"),
     set(range(512, 576))),
)
OUTPUT = Path("scratch_root_e72_source150_m2_shard_audit.json")


def main() -> None:
    _exceptional, records = shared.source_records()
    assert len(records[MACRO]) == 576
    rows = []
    seen = set()
    inputs = {
        str(path): shared.sha256(path)
        for path in (shared.LOCAL, shared.CATALOG, shared.FIBRE_FILTER)
    }
    for path, expected in SHARDS:
        document = shared.load(path)
        mapped = shared.result_map(document, MACRO, records)
        assert set(mapped) == expected
        assert document["summary"]["ordinary_local_pair_filter_enabled"]
        assert document["summary"]["SAT_mass"] == 0
        assert document["summary"]["UNKNOWN_mass"] == 0
        inputs[str(path)] = shared.sha256(path)
        for record, result in sorted(mapped.items()):
            assert record not in seen and result[5] == "UNSAT"
            seen.add(record)
            rows.append({
                "record_number": record,
                "mask_hex": result[1],
                "orbit_size": int(result[2]),
                "evidence_artifact": str(path),
                "reason": result[6],
            })
    assert seen == set(range(576))
    coverage = sum(row["orbit_size"] for row in rows)
    assert coverage == 262_144
    result = {
        "status": "SOURCE150_M2_EXACT_SHARD_AUDIT_PASS",
        "inputs": inputs,
        "source_row_index": 150,
        "macro": list(MACRO),
        "local_graph_orbits": len(rows),
        "labelled_coverage": coverage,
        "catalog_macro_coverage": 262_144,
        "all_catalog_orbits_excluded": True,
        "evidence_class": "exact_solver_free_finite_local_CSP",
        "DRAT_certificate_present": False,
        "SAT_or_UNKNOWN_counted_as_excluded": False,
        "records": rows,
        "claim_boundary": (
            "All source150 macro (2,0) local-graph symmetry orbits are "
            "excluded by the synchronized exact local CSP.  This is not a "
            "complete source150 or E0=72 exclusion and carries no DRAT claim."
        ),
    }
    shared.atomic_json(OUTPUT, result)
    print({
        "status": result["status"],
        "orbits": len(rows),
        "coverage": coverage,
        "output": str(OUTPUT),
    })


if __name__ == "__main__":
    main()
