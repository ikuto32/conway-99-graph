"""Hash-bound exact coverage audit for source150 macro (0,0).

The raw producer result is accepted only after rebuilding the source150
record ordering from the frozen catalogue and checking every representative,
orbit mass, solver mode, and terminal status.
"""

from __future__ import annotations

from collections import Counter
import json
import os
from pathlib import Path

import scratch_root_e72_source150_m47_shard_audit as shared


MACRO = (0, 0)
EXPECTED_ORBITS = 45
EXPECTED_COVERAGE = 8_192
SOLVER = Path("scratch_theory_e72_source150_synchronized_config_csp.py")
EVIDENCE = Path("scratch_theory_e72_source150_sync_localpair_m00_full.json")
OUTPUT = Path("scratch_root_e72_source150_m00_exact_audit.json")
REPORT = Path("scratch_root_e72_source150_m00_exact_audit.md")


def atomic_text(path: Path, value: str) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(value, encoding="utf-8")
    temporary.replace(path)


def main() -> None:
    _exceptional, records_by_macro = shared.source_records()
    source_records = records_by_macro[MACRO]
    assert len(source_records) == EXPECTED_ORBITS
    assert sum(int(row["orbit_size"]) for row in source_records) == EXPECTED_COVERAGE

    document = shared.load(EVIDENCE)
    mapped = shared.result_map(document, MACRO, records_by_macro)
    assert set(mapped) == set(range(EXPECTED_ORBITS))

    summary = document["summary"]
    assert summary["available_orbits_in_wanted_macros"] == EXPECTED_ORBITS
    assert summary["slice_start"] == 0
    assert summary["slice_stop"] == EXPECTED_ORBITS
    assert summary["input_orbits"] == EXPECTED_ORBITS
    assert summary["input_mass"] == EXPECTED_COVERAGE
    assert summary["ordinary_local_pair_filter_enabled"] is True
    assert summary["ordinary_local_pair_every_depth_enabled"] is False
    assert summary["ordinary_joint_map_filter_enabled"] is False
    assert summary["fixed_block_projection"] == []

    status_histogram: Counter[str] = Counter()
    status_mass: Counter[str] = Counter()
    rows = []
    evidence_digest = shared.sha256(EVIDENCE)
    for record_number, result in sorted(mapped.items()):
        status = str(result[5])
        assert status in {"SAT", "UNSAT", "UNKNOWN"}
        orbit_size = int(result[2])
        status_histogram[status] += 1
        status_mass[status] += orbit_size
        rows.append({
            "record_number": record_number,
            "mask_hex": result[1],
            "orbit_size": orbit_size,
            "Q": int(result[3]),
            "status": status,
            "reason": result[6],
            "DFS_nodes": int(result[7]),
            "evidence_artifact": str(EVIDENCE),
            "evidence_sha256": evidence_digest,
        })

    assert dict(status_histogram) == summary["status_histogram"]
    assert sum(status_mass.values()) == EXPECTED_COVERAGE
    for status in ("SAT", "UNSAT", "UNKNOWN"):
        assert status_mass[status] == int(summary[f"{status}_mass"])

    excluded_orbits = status_histogram["UNSAT"]
    excluded_coverage = status_mass["UNSAT"]
    unresolved_orbits = status_histogram["SAT"] + status_histogram["UNKNOWN"]
    unresolved_coverage = status_mass["SAT"] + status_mass["UNKNOWN"]
    assert excluded_orbits + unresolved_orbits == EXPECTED_ORBITS
    assert excluded_coverage + unresolved_coverage == EXPECTED_COVERAGE

    inputs = {
        str(path): shared.sha256(path)
        for path in (
            shared.LOCAL,
            shared.CATALOG,
            shared.FIBRE_FILTER,
            SOLVER,
            EVIDENCE,
        )
    }
    result = {
        "status": "SOURCE150_M00_EXACT_AUDIT_PASS",
        "inputs": inputs,
        "source_row_index": 150,
        "macro": list(MACRO),
        "mode": {
            "synchronized_config_CSP": True,
            "ordinary_local_pair": True,
            "ordinary_local_pair_every_depth": False,
            "node_cap": 0,
            "projection": [],
        },
        "catalog": {
            "local_graph_orbits": EXPECTED_ORBITS,
            "labelled_coverage": EXPECTED_COVERAGE,
        },
        "partition_audit": {
            "record_range": [0, EXPECTED_ORBITS],
            "records_seen_once": len(mapped),
            "no_gaps": set(mapped) == set(range(EXPECTED_ORBITS)),
            "no_duplicates": len(mapped) == len(document["results"]),
            "orbit_mass_matches_catalog": sum(status_mass.values())
            == EXPECTED_COVERAGE,
        },
        "status_histogram": {
            status: status_histogram[status]
            for status in ("SAT", "UNSAT", "UNKNOWN")
        },
        "status_mass": {
            status: status_mass[status]
            for status in ("SAT", "UNSAT", "UNKNOWN")
        },
        "excluded_orbits": excluded_orbits,
        "excluded_labelled_coverage": excluded_coverage,
        "unresolved_orbits": unresolved_orbits,
        "unresolved_labelled_coverage": unresolved_coverage,
        "all_catalog_orbits_excluded": unresolved_orbits == 0,
        "SAT_or_UNKNOWN_counted_as_excluded": False,
        "evidence_class": "exact_solver_free_finite_local_CSP",
        "DRAT_certificate_present": False,
        "records": rows,
        "claim_boundary": (
            "Only rows returned UNSAT by the uncapped synchronized exact local "
            "CSP are excluded. SAT or UNKNOWN rows, if any, remain unresolved. "
            "This macro-specific audit is not a complete source150 or E0=72 "
            "exclusion and makes no DRAT claim."
        ),
    }
    shared.atomic_json(OUTPUT, result)

    report = f"""# source150 macro (0,0) exact audit

Status: `{result['status']}`

The {EXPECTED_ORBITS} catalogued local-graph orbits of macro `(0,0)` have
orbit mass {EXPECTED_COVERAGE:,}, matching the frozen catalogue exactly.
The evidence used the uncapped synchronized CSP with exact ordinary-pair
filtering and no projection.

| status | orbits | labelled coverage |
|---|---:|---:|
| UNSAT | {status_histogram['UNSAT']:,} | {status_mass['UNSAT']:,} |
| SAT | {status_histogram['SAT']:,} | {status_mass['SAT']:,} |
| UNKNOWN | {status_histogram['UNKNOWN']:,} | {status_mass['UNKNOWN']:,} |

Only UNSAT rows are credited. The JSON binds all frozen inputs, the exact
solver, and the evidence artifact by SHA-256 and checks every representative
against the independently reconstructed source150 record order.
"""
    atomic_text(REPORT, report)
    print(json.dumps({
        "status": result["status"],
        "orbits": EXPECTED_ORBITS,
        "coverage": EXPECTED_COVERAGE,
        "excluded_orbits": excluded_orbits,
        "excluded_coverage": excluded_coverage,
        "unresolved_orbits": unresolved_orbits,
        "unresolved_coverage": unresolved_coverage,
        "output": str(OUTPUT),
        "report": str(REPORT),
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
