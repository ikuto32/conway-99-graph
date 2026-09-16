"""Independent, hash-bound aggregate audit for source150 macro (3,1)."""

from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import itertools
import json
import os
from pathlib import Path


LOCAL = Path(
    "scratch_general_e72_q3_gram_frontier_disjoint_gram_filtered_reps.json"
)
CATALOG = Path("scratch_general_e72_q3_gram_fast_expansion_macro_catalog.json")
GRAM = Path("scratch_theory_e72_macro_full_gram.json")
FIBRE_FILTER = Path("scratch_theory_e72_source150_fibre_recurrence_filter.json")
CONFIG_FRONTIER = Path("scratch_theory_e72_source150_global_config_census.json")
SOLVER = Path("scratch_theory_e72_source150_synchronized_config_csp.py")
RUNNER = Path("scratch_root_e72_source150_m31_shard_runner.py")
MANIFEST = Path("scratch_root_e72_source150_m31_shard_run_manifest.json")
SUPPLEMENT = Path(
    "scratch_theory_e72_source150_sync_jointmap_m31_localSAT.json"
)
OUTPUT = Path("scratch_root_e72_source150_m31_shard_audit.json")
REPORT = Path("scratch_root_e72_source150_m31_shard_audit.md")
MACRO = (3, 1)
EXPECTED_ORBITS = 396
EXPECTED_COVERAGE = 131_072
SHARDS = (
    (0, 64),
    (64, 128),
    (128, 192),
    (192, 256),
    (256, 320),
    (320, 384),
    (384, 396),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_json(path: Path, value: object) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def atomic_text(path: Path, value: str) -> None:
    temporary = path.with_suffix(path.suffix + f".{os.getpid()}.tmp")
    temporary.write_text(value, encoding="utf-8")
    temporary.replace(path)


def support(vertex) -> tuple[int, int]:
    return tuple(sorted(int(symbol) // 2 for symbol in vertex))


def normal_edge(edge):
    return tuple(sorted(tuple(vertex) for vertex in edge))


def entry_key(entry, overlap_pairs):
    internal = tuple(sorted(normal_edge(edge) for edge in entry["internal_edges"]))
    overlap = {
        tuple(pair[:2]): int(pair[2]) for pair in entry["overlap_block_totals"]
    }
    return internal, tuple(overlap[pair] for pair in overlap_pairs)


def representative_key(edges, fibre_index, overlap_pairs):
    internal = []
    totals = Counter()
    for edge in edges:
        left, right = map(tuple, edge)
        left_fibre = fibre_index[support(left)]
        right_fibre = fibre_index[support(right)]
        if left_fibre == right_fibre:
            internal.append(normal_edge(edge))
        else:
            totals[tuple(sorted((left_fibre, right_fibre)))] += 1
    return tuple(sorted(internal)), tuple(totals[pair] for pair in overlap_pairs)


def independently_reconstruct_records():
    local = load(LOCAL)
    candidates = [
        row for row in local["support_rows"]
        if row["partition"] == [2, 2, 2, 2, 1, 1, 1, 1]
        and int(row["compression_orbit_index"]) == 0
    ]
    assert len(candidates) == 1
    row = candidates[0]
    exceptional = tuple(
        tuple(item["support"]) for item in row["exceptional_supports"]
    )
    assert len(exceptional) == 8
    fibre_index = {value: index for index, value in enumerate(exceptional)}
    assert len(fibre_index) == 8
    overlap_pairs = tuple(
        pair for pair in itertools.combinations(range(8), 2)
        if set(exceptional[pair[0]]) & set(exceptional[pair[1]])
    )
    catalog_entries = [
        entry for entry in load(CATALOG)["macro_entries"]
        if int(entry["source_row_index"]) == 150
    ]
    entry_by_key = {}
    for entry in catalog_entries:
        key = entry_key(entry, overlap_pairs)
        assert key not in entry_by_key
        entry_by_key[key] = entry
    surviving_masks = {
        str(item[0]) for item in load(FIBRE_FILTER)["survivors"]
    }
    records = defaultdict(list)
    for representative in row["representatives"]:
        if representative["mask_hex"] not in surviving_masks:
            continue
        key = representative_key(
            representative["edges"], fibre_index, overlap_pairs
        )
        assert key in entry_by_key
        entry = entry_by_key[key]
        macro = (
            int(entry["state_orbit_number"]),
            int(entry["signature_stabilizer_orbit_number"]),
        )
        records[macro].append(representative)
    return records


def shard_path(start: int, stop: int) -> Path:
    return Path(
        f"scratch_theory_e72_source150_sync_localpair_m31_r{start}_{stop}.json"
    )


def main() -> None:
    records_by_macro = independently_reconstruct_records()
    source_records = records_by_macro[MACRO]
    assert len(source_records) == EXPECTED_ORBITS
    assert {int(row["Q"]) for row in source_records} == {4}
    assert sum(int(row["orbit_size"]) for row in source_records) == EXPECTED_COVERAGE

    manifest = load(MANIFEST)
    assert manifest["status"] == "COMPLETE"
    assert manifest["macro"] == list(MACRO)
    assert manifest["ordinary_local_pair"] is True
    assert int(manifest["node_cap"]) == 0
    assert manifest["shard_ranges"] == [list(item) for item in SHARDS]
    assert manifest["solver"] == str(SOLVER)
    assert manifest["solver_sha256"] == sha256(SOLVER)

    base_inputs = (LOCAL, CATALOG, GRAM, FIBRE_FILTER, CONFIG_FRONTIER)
    inputs = {
        str(path): sha256(path)
        for path in (*base_inputs, SOLVER, RUNNER, MANIFEST, SUPPLEMENT)
    }
    seen = set()
    audited_rows = []
    shard_summaries = []
    status_histogram = Counter()
    status_mass = Counter()
    for start, stop in SHARDS:
        path = shard_path(start, stop)
        digest = sha256(path)
        inputs[str(path)] = digest
        checkpoint = manifest["shards"][f"{start}:{stop}"]
        assert checkpoint["status"] == "COMPLETE"
        assert checkpoint["path"] == str(path)
        assert checkpoint["sha256"] == digest
        document = load(path)
        assert document["status"] == "EXACT_SYNCHRONIZED_CONFIG_CSP_SLICE_COMPLETE"
        assert document["inputs"] == {
            str(input_path): sha256(input_path) for input_path in base_inputs
        }
        summary = document["summary"]
        assert summary["wanted_macros"] == [list(MACRO)]
        assert summary["available_orbits_in_wanted_macros"] == EXPECTED_ORBITS
        assert summary["slice_start"] == start
        assert summary["slice_stop"] == stop
        assert summary["explicit_record_selection"] == []
        assert summary["input_orbits"] == stop - start
        assert summary["ordinary_local_pair_filter_enabled"] is True
        assert summary["ordinary_local_pair_every_depth_enabled"] is False
        assert summary["ordinary_joint_map_filter_enabled"] is False
        assert summary["fixed_block_projection"] == []

        expected_numbers = list(range(start, stop))
        got_numbers = [int(result[0]) for result in document["results"]]
        assert got_numbers == expected_numbers
        shard_histogram = Counter()
        shard_mass = Counter()
        for result in document["results"]:
            record_number = int(result[0])
            assert record_number not in seen
            seen.add(record_number)
            representative = source_records[record_number]
            assert result[1] == representative["mask_hex"]
            assert int(result[2]) == int(representative["orbit_size"])
            assert int(result[3]) == int(representative["Q"])
            assert tuple(result[4]) == MACRO
            status = str(result[5])
            assert status in {"SAT", "UNSAT", "UNKNOWN"}
            orbit_size = int(result[2])
            status_histogram[status] += 1
            status_mass[status] += orbit_size
            shard_histogram[status] += 1
            shard_mass[status] += orbit_size
            audited_rows.append({
                "record_number": record_number,
                "mask_hex": result[1],
                "Q": int(result[3]),
                "orbit_size": orbit_size,
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
            "status_histogram": {
                status: shard_histogram[status]
                for status in ("SAT", "UNSAT", "UNKNOWN")
            },
            "status_mass": {
                status: shard_mass[status]
                for status in ("SAT", "UNSAT", "UNKNOWN")
            },
            "maximum_DFS_nodes": int(summary["maximum_DFS_nodes"]),
            "elapsed_seconds": float(summary["elapsed_seconds"]),
        })

    assert seen == set(range(EXPECTED_ORBITS))
    assert len(audited_rows) == len(seen)
    assert status_histogram["UNSAT"] == EXPECTED_ORBITS - 2
    assert status_histogram["SAT"] == 2
    assert status_histogram["UNKNOWN"] == 0
    assert status_mass["UNSAT"] == EXPECTED_COVERAGE - 384
    assert status_mass["SAT"] == 384
    assert status_mass["UNKNOWN"] == 0

    direct_sat = {
        row["record_number"]: row for row in audited_rows
        if row["status"] == "SAT"
    }
    assert set(direct_sat) == {190, 347}
    supplement = load(SUPPLEMENT)
    assert supplement["status"] == "EXACT_SYNCHRONIZED_CONFIG_CSP_SLICE_COMPLETE"
    assert supplement["inputs"] == {
        str(input_path): sha256(input_path) for input_path in base_inputs
    }
    supplement_summary = supplement["summary"]
    assert supplement_summary["wanted_macros"] == [list(MACRO)]
    assert supplement_summary["available_orbits_in_wanted_macros"] == EXPECTED_ORBITS
    assert supplement_summary["explicit_record_selection"] == [190, 347]
    assert supplement_summary["input_orbits"] == 2
    assert supplement_summary["input_mass"] == 384
    assert supplement_summary["ordinary_joint_map_filter_enabled"] is True
    assert supplement_summary["ordinary_joint_map_unknowns_relaxed_as_pass"] == 0
    assert supplement_summary["fixed_block_projection"] == []
    assert supplement_summary["status_histogram"] == {"UNSAT": 2}
    assert supplement_summary["SAT_mass"] == 0
    assert supplement_summary["UNSAT_mass"] == 384
    assert supplement_summary["UNKNOWN_mass"] == 0
    supplement_digest = sha256(SUPPLEMENT)
    supplement_by_record = {}
    for evidence in supplement["results"]:
        record_number = int(evidence[0])
        assert record_number in direct_sat
        assert record_number not in supplement_by_record
        representative = source_records[record_number]
        assert evidence[1] == representative["mask_hex"]
        assert int(evidence[2]) == int(representative["orbit_size"])
        assert int(evidence[3]) == int(representative["Q"])
        assert tuple(evidence[4]) == MACRO
        assert evidence[5] == "UNSAT"
        supplement_by_record[record_number] = evidence
    assert set(supplement_by_record) == set(direct_sat)

    final_rows = []
    for direct in audited_rows:
        row = dict(direct)
        row["direct_local_pair_status"] = row.pop("status")
        if row["direct_local_pair_status"] == "UNSAT":
            row["final_exact_status"] = "UNSAT"
            row["evidence_mode"] = "direct_uncapped_ordinary_local_pair"
        else:
            assert row["direct_local_pair_status"] == "SAT"
            evidence = supplement_by_record[row["record_number"]]
            row.update({
                "final_exact_status": "UNSAT",
                "reason": evidence[6],
                "DFS_nodes": int(evidence[7]),
                "evidence_artifact": str(SUPPLEMENT),
                "evidence_sha256": supplement_digest,
                "evidence_mode": (
                    "uncapped_exact_synchronized_ordinary_joint_map_pair"
                ),
            })
        final_rows.append(row)

    result = {
        "status": "SOURCE150_M31_INDEPENDENT_EXACT_SHARD_AUDIT_PASS",
        "inputs": inputs,
        "source_row_index": 150,
        "macro": list(MACRO),
        "mode": {
            "synchronized_config_CSP": True,
            "ordinary_local_pair_base": True,
            "ordinary_joint_map_pair_supplement_records": [190, 347],
            "node_cap": 0,
            "projection": [],
        },
        "catalog": {
            "local_graph_orbits": EXPECTED_ORBITS,
            "labelled_coverage": EXPECTED_COVERAGE,
            "Q_histogram": {"4": EXPECTED_ORBITS},
        },
        "partition_audit": {
            "ranges": [list(item) for item in SHARDS],
            "records_seen_once": len(seen),
            "no_gaps": True,
            "no_duplicates": True,
            "representative_mask_Q_orbit_size_checked": True,
            "orbit_mass_matches_catalog": True,
        },
        "direct_local_pair_status_histogram": {
            status: status_histogram[status]
            for status in ("SAT", "UNSAT", "UNKNOWN")
        },
        "direct_local_pair_status_mass": {
            status: status_mass[status]
            for status in ("SAT", "UNSAT", "UNKNOWN")
        },
        "supplement_status_histogram": {"SAT": 0, "UNSAT": 2, "UNKNOWN": 0},
        "supplement_status_mass": {"SAT": 0, "UNSAT": 384, "UNKNOWN": 0},
        "status_histogram": {"SAT": 0, "UNSAT": EXPECTED_ORBITS, "UNKNOWN": 0},
        "status_mass": {"SAT": 0, "UNSAT": EXPECTED_COVERAGE, "UNKNOWN": 0},
        "excluded_orbits": EXPECTED_ORBITS,
        "excluded_labelled_coverage": EXPECTED_COVERAGE,
        "unresolved_orbits": 0,
        "unresolved_labelled_coverage": 0,
        "all_catalog_orbits_excluded": True,
        "SAT_or_UNKNOWN_counted_as_excluded": False,
        "evidence_class": "exact_solver_free_finite_local_CSP",
        "DRAT_certificate_present": False,
        "shards": shard_summaries,
        "records": final_rows,
        "claim_boundary": (
            "This independently reconstructs source150 macro (3,1). Direct "
            "ordinary-local-pair CSP excludes 394 records; its two SAT records "
            "are not exclusions and are separately excluded by an uncapped "
            "exact synchronized labelled ordinary-map cumulative pair CSP. "
            "No projection evidence is credited. This excludes this macro "
            "only, not all source150 or E0=72, and makes no DRAT claim."
        ),
    }
    atomic_json(OUTPUT, result)
    report = f"""# source150 macro (3,1) independent shard audit

Status: `{result['status']}`

The audit independently reconstructed macro `(3,1)` from the source150 local
representatives and Gram macro catalog. It checked each stored mask, `Q`, orbit
size, macro key, and input hash against seven contiguous direct exact shards.
The direct ordinary-local-pair layer has two SAT witnesses; these are not
credited as exclusions there. An uncapped exact synchronized labelled-map pair
supplement excludes precisely those two records.

| direct local status | orbits | labelled coverage |
|---|---:|---:|
| UNSAT | {status_histogram['UNSAT']:,} | {status_mass['UNSAT']:,} |
| SAT | {status_histogram['SAT']:,} | {status_mass['SAT']:,} |
| UNKNOWN | {status_histogram['UNKNOWN']:,} | {status_mass['UNKNOWN']:,} |

After exact supplement: UNSAT {EXPECTED_ORBITS:,} orbits / {EXPECTED_COVERAGE:,}
labelled coverage, SAT 0, UNKNOWN 0. There are no gaps, duplicates, or
projection-derived exclusions. This is a macro-local finite CSP certificate
bridge, not a DRAT certificate or a complete exclusion of source150/E0=72.
"""
    atomic_text(REPORT, report)
    print(json.dumps({
        "status": result["status"],
        "orbits": EXPECTED_ORBITS,
        "coverage": EXPECTED_COVERAGE,
        "SAT": 0,
        "UNKNOWN": 0,
        "output": str(OUTPUT),
        "report": str(REPORT),
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
