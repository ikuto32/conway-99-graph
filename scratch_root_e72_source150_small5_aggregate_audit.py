"""Independent hash-bound audit for five source150 macro exact sweeps."""

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
DIRECT_RUNNER = Path("scratch_root_e72_source150_small5_shard_runner.py")
DIRECT_MANIFEST = Path("scratch_root_e72_source150_small5_shard_run_manifest.json")
SUPPLEMENT_RUNNER = Path(
    "scratch_root_e72_source150_small5_joint_supplement_runner.py"
)
SUPPLEMENT_MANIFEST = Path(
    "scratch_root_e72_source150_small5_joint_supplement_manifest.json"
)
OUTPUT = Path("scratch_root_e72_source150_small5_aggregate_audit.json")
REPORT = Path("scratch_root_e72_source150_small5_aggregate_audit.md")
EXPECTED = {
    (1, 0): (96, 8_192, 4),
    (3, 3): (116, 8_192, 4),
    (9, 0): (52, 4_096, 8),
    (10, 0): (63, 8_192, 4),
    (11, 0): (73, 8_192, 4),
}
TASKS = (
    ((1, 0), 0, 64),
    ((1, 0), 64, 96),
    ((3, 3), 0, 64),
    ((3, 3), 64, 116),
    ((9, 0), 0, 52),
    ((10, 0), 0, 63),
    ((11, 0), 0, 64),
    ((11, 0), 64, 73),
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


def macro_key(macro: tuple[int, int]) -> str:
    return f"{macro[0]}:{macro[1]}"


def macro_tag(macro: tuple[int, int]) -> str:
    return f"m{macro[0]}{macro[1]}"


def direct_path(macro: tuple[int, int], start: int, stop: int) -> Path:
    return Path(
        "scratch_theory_e72_source150_sync_localpair_small5_"
        f"{macro_tag(macro)}_r{start}_{stop}.json"
    )


def supplement_path(macro: tuple[int, int]) -> Path:
    return Path(
        "scratch_theory_e72_source150_sync_jointmap_small5_"
        f"{macro_tag(macro)}_localSAT.json"
    )


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
    rows = [
        row for row in local["support_rows"]
        if row["partition"] == [2, 2, 2, 2, 1, 1, 1, 1]
        and int(row["compression_orbit_index"]) == 0
    ]
    assert len(rows) == 1
    row = rows[0]
    exceptional = tuple(
        tuple(item["support"]) for item in row["exceptional_supports"]
    )
    fibre_index = {value: index for index, value in enumerate(exceptional)}
    assert len(exceptional) == len(fibre_index) == 8
    overlap_pairs = tuple(
        pair for pair in itertools.combinations(range(8), 2)
        if set(exceptional[pair[0]]) & set(exceptional[pair[1]])
    )
    entries = [
        entry for entry in load(CATALOG)["macro_entries"]
        if int(entry["source_row_index"]) == 150
    ]
    by_key = {}
    for entry in entries:
        key = entry_key(entry, overlap_pairs)
        assert key not in by_key
        by_key[key] = entry
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
        assert key in by_key
        entry = by_key[key]
        macro = (
            int(entry["state_orbit_number"]),
            int(entry["signature_stabilizer_orbit_number"]),
        )
        records[macro].append(representative)
    return records


def verify_result(result, macro, records):
    record_number = int(result[0])
    representative = records[macro][record_number]
    assert result[1] == representative["mask_hex"]
    assert int(result[2]) == int(representative["orbit_size"])
    assert int(result[3]) == int(representative["Q"])
    assert tuple(result[4]) == macro
    assert result[5] in {"SAT", "UNSAT", "UNKNOWN"}
    return record_number, representative


def main() -> None:
    records = independently_reconstruct_records()
    for macro, (orbit_count, coverage, q) in EXPECTED.items():
        assert len(records[macro]) == orbit_count
        assert {int(row["Q"]) for row in records[macro]} == {q}
        assert sum(int(row["orbit_size"]) for row in records[macro]) == coverage

    base_inputs = (LOCAL, CATALOG, GRAM, FIBRE_FILTER, CONFIG_FRONTIER)
    direct_manifest = load(DIRECT_MANIFEST)
    assert direct_manifest["status"] == "COMPLETE"
    assert direct_manifest["macros"] == [list(macro) for macro in EXPECTED]
    assert direct_manifest["ordinary_local_pair"] is True
    assert direct_manifest["node_cap"] == 0
    assert direct_manifest["solver"] == str(SOLVER)
    assert direct_manifest["solver_sha256"] == sha256(SOLVER)
    assert direct_manifest["tasks"] == [
        [list(macro), start, stop] for macro, start, stop in TASKS
    ]

    inputs = {
        str(path): sha256(path)
        for path in (
            *base_inputs, SOLVER, DIRECT_RUNNER, DIRECT_MANIFEST,
            SUPPLEMENT_RUNNER, SUPPLEMENT_MANIFEST,
        )
    }
    direct_by_macro = {macro: {} for macro in EXPECTED}
    direct_hist = {macro: Counter() for macro in EXPECTED}
    direct_mass = {macro: Counter() for macro in EXPECTED}
    shard_summaries = []
    for macro, start, stop in TASKS:
        path = direct_path(macro, start, stop)
        digest = sha256(path)
        inputs[str(path)] = digest
        key = f"{macro_key(macro)}:{start}:{stop}"
        checkpoint = direct_manifest["shards"][key]
        assert checkpoint["status"] == "COMPLETE"
        assert checkpoint["path"] == str(path)
        assert checkpoint["sha256"] == digest
        document = load(path)
        assert document["status"] == "EXACT_SYNCHRONIZED_CONFIG_CSP_SLICE_COMPLETE"
        assert document["inputs"] == {
            str(input_path): sha256(input_path) for input_path in base_inputs
        }
        summary = document["summary"]
        assert summary["wanted_macros"] == [list(macro)]
        assert summary["available_orbits_in_wanted_macros"] == EXPECTED[macro][0]
        assert summary["slice_start"] == start
        assert summary["slice_stop"] == stop
        assert summary["explicit_record_selection"] == []
        assert summary["input_orbits"] == stop - start
        assert summary["ordinary_local_pair_filter_enabled"] is True
        assert summary["ordinary_local_pair_every_depth_enabled"] is False
        assert summary["ordinary_joint_map_filter_enabled"] is False
        assert summary["fixed_block_projection"] == []
        got_numbers = [int(result[0]) for result in document["results"]]
        assert got_numbers == list(range(start, stop))
        shard_hist = Counter()
        shard_mass = Counter()
        for result in document["results"]:
            record_number, representative = verify_result(result, macro, records)
            assert record_number not in direct_by_macro[macro]
            direct_by_macro[macro][record_number] = (result, path, digest)
            status = result[5]
            orbit_size = int(representative["orbit_size"])
            direct_hist[macro][status] += 1
            direct_mass[macro][status] += orbit_size
            shard_hist[status] += 1
            shard_mass[status] += orbit_size
        assert dict(shard_hist) == summary["status_histogram"]
        assert sum(shard_mass.values()) == summary["input_mass"]
        for status in ("SAT", "UNSAT", "UNKNOWN"):
            assert shard_mass[status] == summary[f"{status}_mass"]
        shard_summaries.append({
            "macro": list(macro),
            "range": [start, stop],
            "artifact": str(path),
            "sha256": digest,
            "status_histogram": {
                status: shard_hist[status]
                for status in ("SAT", "UNSAT", "UNKNOWN")
            },
            "status_mass": {
                status: shard_mass[status]
                for status in ("SAT", "UNSAT", "UNKNOWN")
            },
            "maximum_DFS_nodes": summary["maximum_DFS_nodes"],
            "elapsed_seconds": summary["elapsed_seconds"],
        })

    for macro, (orbit_count, coverage, _q) in EXPECTED.items():
        assert set(direct_by_macro[macro]) == set(range(orbit_count))
        assert sum(direct_hist[macro].values()) == orbit_count
        assert sum(direct_mass[macro].values()) == coverage
        assert direct_hist[macro]["UNKNOWN"] == 0
        assert direct_mass[macro]["UNKNOWN"] == 0

    supplement_manifest = load(SUPPLEMENT_MANIFEST)
    assert supplement_manifest["status"] == "COMPLETE"
    assert supplement_manifest["solver"] == str(SOLVER)
    assert supplement_manifest["solver_sha256"] == sha256(SOLVER)
    assert supplement_manifest["direct_manifest"] == str(DIRECT_MANIFEST)
    assert supplement_manifest["direct_manifest_sha256"] == sha256(DIRECT_MANIFEST)
    assert supplement_manifest["ordinary_joint_map"] is True
    assert supplement_manifest["node_cap"] == 0
    assert supplement_manifest["projection"] == []

    final_rows = []
    per_macro = []
    total_final_hist = Counter()
    total_final_mass = Counter()
    for macro, (orbit_count, coverage, q) in EXPECTED.items():
        key = macro_key(macro)
        sat_records = tuple(sorted(
            record_number
            for record_number, (result, _path, _digest)
            in direct_by_macro[macro].items()
            if result[5] == "SAT"
        ))
        assert supplement_manifest["direct_sat_records"][key] == list(sat_records)
        supplement_checkpoint = supplement_manifest["macros"][key]
        supplement_results = {}
        supplement_artifact = None
        if sat_records:
            supplement_artifact = supplement_path(macro)
            supplement_digest = sha256(supplement_artifact)
            inputs[str(supplement_artifact)] = supplement_digest
            assert supplement_checkpoint["status"] == "COMPLETE"
            assert supplement_checkpoint["path"] == str(supplement_artifact)
            assert supplement_checkpoint["sha256"] == supplement_digest
            document = load(supplement_artifact)
            assert document["status"] == "EXACT_SYNCHRONIZED_CONFIG_CSP_SLICE_COMPLETE"
            assert document["inputs"] == {
                str(input_path): sha256(input_path) for input_path in base_inputs
            }
            summary = document["summary"]
            assert summary["wanted_macros"] == [list(macro)]
            assert summary["available_orbits_in_wanted_macros"] == orbit_count
            assert summary["explicit_record_selection"] == list(sat_records)
            assert summary["input_orbits"] == len(sat_records)
            assert summary["ordinary_joint_map_filter_enabled"] is True
            assert summary["ordinary_joint_map_unknowns_relaxed_as_pass"] == 0
            assert summary["fixed_block_projection"] == []
            for result in document["results"]:
                record_number, _representative = verify_result(result, macro, records)
                assert record_number in sat_records
                assert record_number not in supplement_results
                supplement_results[record_number] = result
            assert set(supplement_results) == set(sat_records)
        else:
            assert supplement_checkpoint["status"] == "NO_DIRECT_SAT_INPUT"
            assert supplement_checkpoint["records"] == []

        final_hist = Counter()
        final_mass = Counter()
        for record_number in range(orbit_count):
            direct_result, direct_artifact, direct_digest = direct_by_macro[macro][
                record_number
            ]
            representative = records[macro][record_number]
            orbit_size = int(representative["orbit_size"])
            direct_status = direct_result[5]
            if direct_status == "UNSAT":
                evidence = direct_result
                artifact = direct_artifact
                digest = direct_digest
                mode = "direct_uncapped_ordinary_local_pair"
            else:
                assert direct_status == "SAT"
                evidence = supplement_results[record_number]
                assert evidence[5] == "UNSAT"
                artifact = supplement_artifact
                digest = sha256(supplement_artifact)
                mode = "uncapped_exact_synchronized_ordinary_joint_map_pair"
            final_status = evidence[5]
            final_hist[final_status] += 1
            final_mass[final_status] += orbit_size
            total_final_hist[final_status] += 1
            total_final_mass[final_status] += orbit_size
            final_rows.append({
                "macro": list(macro),
                "record_number": record_number,
                "mask_hex": representative["mask_hex"],
                "Q": int(representative["Q"]),
                "orbit_size": orbit_size,
                "direct_local_pair_status": direct_status,
                "final_exact_status": final_status,
                "evidence_mode": mode,
                "reason": evidence[6],
                "DFS_nodes": int(evidence[7]),
                "evidence_artifact": str(artifact),
                "evidence_sha256": digest,
            })
        assert final_hist["UNSAT"] == orbit_count
        assert final_hist["SAT"] == final_hist["UNKNOWN"] == 0
        assert final_mass["UNSAT"] == coverage
        assert final_mass["SAT"] == final_mass["UNKNOWN"] == 0
        per_macro.append({
            "macro": list(macro),
            "Q": q,
            "catalog_orbits": orbit_count,
            "catalog_coverage": coverage,
            "direct_local_pair_status_histogram": {
                status: direct_hist[macro][status]
                for status in ("SAT", "UNSAT", "UNKNOWN")
            },
            "direct_local_pair_status_mass": {
                status: direct_mass[macro][status]
                for status in ("SAT", "UNSAT", "UNKNOWN")
            },
            "joint_map_supplement_records": list(sat_records),
            "final_status_histogram": {
                status: final_hist[status]
                for status in ("SAT", "UNSAT", "UNKNOWN")
            },
            "final_status_mass": {
                status: final_mass[status]
                for status in ("SAT", "UNSAT", "UNKNOWN")
            },
        })

    expected_total_orbits = sum(value[0] for value in EXPECTED.values())
    expected_total_coverage = sum(value[1] for value in EXPECTED.values())
    assert total_final_hist["UNSAT"] == expected_total_orbits == 400
    assert total_final_hist["SAT"] == total_final_hist["UNKNOWN"] == 0
    assert total_final_mass["UNSAT"] == expected_total_coverage == 36_864
    assert total_final_mass["SAT"] == total_final_mass["UNKNOWN"] == 0
    assert len(final_rows) == expected_total_orbits

    result = {
        "status": "SOURCE150_SMALL5_INDEPENDENT_EXACT_AGGREGATE_AUDIT_PASS",
        "inputs": inputs,
        "source_row_index": 150,
        "macros": [list(macro) for macro in EXPECTED],
        "catalog_total_orbits": expected_total_orbits,
        "catalog_total_coverage": expected_total_coverage,
        "mode": {
            "direct_uncapped_ordinary_local_pair": True,
            "SAT_only_uncapped_exact_synchronized_joint_map_pair_supplement": True,
            "node_cap": 0,
            "projection": [],
        },
        "partition_audit": {
            "shards": [[list(macro), start, stop]
                       for macro, start, stop in TASKS],
            "representative_mask_Q_orbit_size_checked": True,
            "no_gaps_within_each_macro": True,
            "no_duplicates_within_each_macro": True,
            "orbit_mass_matches_catalog": True,
        },
        "per_macro": per_macro,
        "final_status_histogram": {
            status: total_final_hist[status]
            for status in ("SAT", "UNSAT", "UNKNOWN")
        },
        "final_status_mass": {
            status: total_final_mass[status]
            for status in ("SAT", "UNSAT", "UNKNOWN")
        },
        "all_five_catalog_macros_excluded": True,
        "SAT_or_UNKNOWN_counted_as_excluded": False,
        "projection_evidence_credited": False,
        "evidence_class": "exact_solver_free_finite_local_CSP",
        "DRAT_certificate_present": False,
        "shard_summaries": shard_summaries,
        "records": final_rows,
        "claim_boundary": (
            "Direct SAT records are not exclusions. Only exact direct UNSAT "
            "records and exact synchronized joint-map-pair UNSAT supplements "
            "are credited. This excludes the five listed source150 macros "
            "only, not all source150 or E0=72, and makes no DRAT claim."
        ),
    }
    atomic_json(OUTPUT, result)

    table_rows = []
    for row in per_macro:
        direct_values = row["direct_local_pair_status_histogram"]
        table_rows.append(
            f"| `{tuple(row['macro'])}` | {row['catalog_orbits']:,} | "
            f"{row['catalog_coverage']:,} | {direct_values['UNSAT']:,} | "
            f"{direct_values['SAT']:,} | "
            f"{len(row['joint_map_supplement_records']):,} |"
        )
    report = f"""# source150 five-macro independent aggregate audit

Status: `{result['status']}`

| macro | orbits | coverage | direct UNSAT | direct SAT | supplemented |
|---|---:|---:|---:|---:|---:|
{chr(10).join(table_rows)}

All {expected_total_orbits:,} catalog orbits / {expected_total_coverage:,}
labelled coverage have final exact UNSAT evidence. Final SAT and UNKNOWN counts
are both zero. Direct SAT rows were never credited directly: precisely those
rows were checked by the uncapped synchronized labelled ordinary-map cumulative
pair CSP. No projection evidence is used.

The audit independently reconstructs every macro from source150 representatives
and the macro catalog, then checks input hashes, mask, Q, orbit size, shard
partition, direct result, supplement target set, and final coverage. This is a
macro-local finite-CSP result, not a DRAT certificate or a complete exclusion
of source150/E0=72.
"""
    atomic_text(REPORT, report)
    print(json.dumps({
        "status": result["status"],
        "orbits": expected_total_orbits,
        "coverage": expected_total_coverage,
        "SAT": 0,
        "UNKNOWN": 0,
        "output": str(OUTPUT),
        "report": str(REPORT),
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
