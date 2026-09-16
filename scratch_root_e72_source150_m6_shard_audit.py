"""Hash-bound aggregate audit for the source150 macro (6,0) exact sweep.

Only records proved UNSAT by the uncapped synchronized ordinary-pair CSP are
credited as excluded.  SAT and UNKNOWN records remain explicitly unresolved.
"""

from __future__ import annotations

from collections import Counter
import json
import os
from pathlib import Path

import scratch_root_e72_source150_m47_shard_audit as shared


MACRO = (6, 0)
EXPECTED_ORBITS = 704
EXPECTED_COVERAGE = 262_144
RUNNER = Path("scratch_root_e72_source150_m6_shard_runner.py")
RUN_MANIFEST = Path("scratch_root_e72_source150_m6_shard_run_manifest.json")
SOLVER = Path("scratch_theory_e72_source150_synchronized_config_csp.py")
OUTPUT = Path("scratch_root_e72_source150_m6_shard_audit.json")
REPORT = Path("scratch_root_e72_source150_m6_shard_audit.md")
SHARDS = (
    (0, 128),
    (128, 256),
    (256, 384),
    (384, 512),
    (512, 640),
    (640, 704),
)


def shard_path(start: int, stop: int) -> Path:
    return Path(
        f"scratch_theory_e72_source150_sync_localpair_m60_r{start}_{stop}.json"
    )


def atomic_text(path: Path, value: str) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(value, encoding="utf-8")
    temporary.replace(path)


def main() -> None:
    _exceptional, records_by_macro = shared.source_records()
    source_records = records_by_macro[MACRO]
    assert len(source_records) == EXPECTED_ORBITS
    assert sum(int(row["orbit_size"]) for row in source_records) == EXPECTED_COVERAGE

    manifest = shared.load(RUN_MANIFEST)
    assert manifest["status"] == "COMPLETE"
    assert manifest["macro"] == list(MACRO)
    assert manifest["ordinary_local_pair"] is True
    assert int(manifest["node_cap"]) == 0
    assert manifest["shard_ranges"] == [list(item) for item in SHARDS]
    assert manifest["solver"] == str(SOLVER)
    assert manifest["solver_sha256"] == shared.sha256(SOLVER)

    inputs = {
        str(path): shared.sha256(path)
        for path in (
            shared.LOCAL,
            shared.CATALOG,
            shared.FIBRE_FILTER,
            SOLVER,
            RUNNER,
            RUN_MANIFEST,
        )
    }
    seen: set[int] = set()
    rows = []
    status_histogram: Counter[str] = Counter()
    status_mass: Counter[str] = Counter()
    shard_summaries = []
    for start, stop in SHARDS:
        path = shard_path(start, stop)
        digest = shared.sha256(path)
        inputs[str(path)] = digest
        checkpoint = manifest["shards"][f"{start}:{stop}"]
        assert checkpoint["status"] == "COMPLETE"
        assert checkpoint["path"] == str(path)
        assert checkpoint["sha256"] == digest

        document = shared.load(path)
        mapped = shared.result_map(document, MACRO, records_by_macro)
        expected = set(range(start, stop))
        assert set(mapped) == expected
        summary = document["summary"]
        assert summary["slice_start"] == start
        assert summary["slice_stop"] == stop
        assert summary["input_orbits"] == stop - start
        assert summary["ordinary_local_pair_filter_enabled"] is True
        assert summary["ordinary_local_pair_every_depth_enabled"] is False
        assert summary["ordinary_joint_map_filter_enabled"] is False
        assert summary["fixed_block_projection"] == []
        assert summary["available_orbits_in_wanted_macros"] == EXPECTED_ORBITS

        shard_histogram: Counter[str] = Counter()
        shard_mass: Counter[str] = Counter()
        for record_number, result in sorted(mapped.items()):
            assert record_number not in seen
            seen.add(record_number)
            status = str(result[5])
            assert status in {"SAT", "UNSAT", "UNKNOWN"}
            orbit_size = int(result[2])
            status_histogram[status] += 1
            status_mass[status] += orbit_size
            shard_histogram[status] += 1
            shard_mass[status] += orbit_size
            rows.append({
                "record_number": record_number,
                "mask_hex": result[1],
                "orbit_size": orbit_size,
                "Q": int(result[3]),
                "status": status,
                "reason": result[6],
                "DFS_nodes": int(result[7]),
                "evidence_artifact": str(path),
                "evidence_sha256": digest,
            })

        assert dict(shard_histogram) == summary["status_histogram"]
        assert sum(shard_mass.values()) == int(summary["input_mass"])
        for status in ("SAT", "UNSAT", "UNKNOWN"):
            assert shard_mass[status] == int(summary[f"{status}_mass"])
        shard_summaries.append({
            "range": [start, stop],
            "artifact": str(path),
            "sha256": digest,
            "status_histogram": dict(sorted(shard_histogram.items())),
            "status_mass": {
                status: shard_mass[status]
                for status in ("SAT", "UNSAT", "UNKNOWN")
            },
            "maximum_DFS_nodes": int(summary["maximum_DFS_nodes"]),
            "elapsed_seconds": float(summary["elapsed_seconds"]),
        })

    assert seen == set(range(EXPECTED_ORBITS))
    assert sum(status_histogram.values()) == EXPECTED_ORBITS
    assert sum(status_mass.values()) == EXPECTED_COVERAGE
    excluded_orbits = status_histogram["UNSAT"]
    excluded_coverage = status_mass["UNSAT"]
    unresolved_orbits = status_histogram["SAT"] + status_histogram["UNKNOWN"]
    unresolved_coverage = status_mass["SAT"] + status_mass["UNKNOWN"]
    assert excluded_orbits + unresolved_orbits == EXPECTED_ORBITS
    assert excluded_coverage + unresolved_coverage == EXPECTED_COVERAGE

    result = {
        "status": "SOURCE150_M6_EXACT_SHARD_AGGREGATE_AUDIT_PASS",
        "inputs": inputs,
        "source_row_index": 150,
        "macro": list(MACRO),
        "mode": {
            "synchronized_config_CSP": True,
            "ordinary_local_pair": True,
            "node_cap": 0,
            "projection": [],
        },
        "catalog": {
            "local_graph_orbits": EXPECTED_ORBITS,
            "labelled_coverage": EXPECTED_COVERAGE,
        },
        "partition_audit": {
            "ranges": [list(item) for item in SHARDS],
            "records_seen_once": len(seen),
            "no_gaps": seen == set(range(EXPECTED_ORBITS)),
            "no_duplicates": len(rows) == len(seen),
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
        "shards": shard_summaries,
        "records": rows,
        "claim_boundary": (
            "Only rows returned UNSAT by the uncapped synchronized exact local "
            "CSP are excluded. SAT or UNKNOWN rows, if any, remain unresolved. "
            "This macro-specific audit is not a complete source150 or E0=72 "
            "exclusion and makes no DRAT claim."
        ),
    }
    shared.atomic_json(OUTPUT, result)

    report = f"""# source150 macro (6,0) exact shard audit

Status: `{result['status']}`

The 704 catalogued local-graph orbits of macro `(6,0)` were partitioned into
six contiguous, nonoverlapping shards. Their orbit mass is {EXPECTED_COVERAGE:,},
matching the catalog exactly. Each shard used the uncapped synchronized CSP
with exact ordinary-pair filtering and no projection.

| status | orbits | labelled coverage |
|---|---:|---:|
| UNSAT | {status_histogram['UNSAT']:,} | {status_mass['UNSAT']:,} |
| SAT | {status_histogram['SAT']:,} | {status_mass['SAT']:,} |
| UNKNOWN | {status_histogram['UNKNOWN']:,} | {status_mass['UNKNOWN']:,} |

Only the UNSAT row is credited as excluded. SAT and UNKNOWN are never counted
as exclusions. Consequently `all_catalog_orbits_excluded` is
`{str(unresolved_orbits == 0).lower()}`. This is a finite local-CSP result, not
a DRAT certificate and not by itself a complete source150 or E0=72 exclusion.

The JSON binds the source catalog, input filters, solver, runner, checkpoint
manifest, and all six shard artifacts by SHA-256 and contains the per-record
coverage bridge.
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
