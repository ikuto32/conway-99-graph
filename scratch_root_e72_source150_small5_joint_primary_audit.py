"""Independent hash-bound audit of the small-five joint-map primary sweep."""

from __future__ import annotations

from collections import Counter
import json
import os
from pathlib import Path

import scratch_root_e72_source150_small5_aggregate_audit as foundation


EXPECTED = {
    (1, 0): (96, 8_192, 4),
    (3, 3): (116, 8_192, 4),
    (9, 0): (52, 4_096, 8),
    (10, 0): (63, 8_192, 4),
    (11, 0): (73, 8_192, 4),
}
SHARD_SIZE = 8
TASKS = tuple(
    (macro, start, min(start + SHARD_SIZE, count))
    for macro, (count, _coverage, _q) in EXPECTED.items()
    for start in range(0, count, SHARD_SIZE)
)
SOLVER = Path("scratch_theory_e72_source150_synchronized_config_csp.py")
PRIMARY_RUNNER = Path(
    "scratch_root_e72_source150_small5_joint_primary_runner.py"
)
PRIMARY_MANIFEST = Path(
    "scratch_root_e72_source150_small5_joint_primary_manifest.json"
)
AUDIT_FOUNDATION = Path(
    "scratch_root_e72_source150_small5_aggregate_audit.py"
)
MODEL_CODE = (
    Path("scratch_theory_e72_source150_norm_collision_filter.py"),
    Path("scratch_theory_e72_source150_fibre_recurrence_filter.py"),
    Path("scratch_theory_e72_source150_pointwise_recurrence_csp.py"),
    Path("scratch_theory_e72_source150_disjoint_graphical_filter.py"),
    Path("scratch_theory_e72_source150_map_collision_probe.py"),
)
OUTPUT = Path(
    "scratch_root_e72_source150_small5_joint_primary_audit.json"
)
REPORT = Path(
    "scratch_root_e72_source150_small5_joint_primary_audit.md"
)


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


def shard_path(macro: tuple[int, int], start: int, stop: int) -> Path:
    return Path(
        "scratch_theory_e72_source150_sync_jointprimary_small5_"
        f"{macro_tag(macro)}_r{start}_{stop}.json"
    )


def main() -> None:
    # This reconstruction is independent of the primary runner and solver.
    records = foundation.independently_reconstruct_records()
    for macro, (count, coverage, q) in EXPECTED.items():
        assert len(records[macro]) == count
        assert {int(row["Q"]) for row in records[macro]} == {q}
        assert sum(int(row["orbit_size"]) for row in records[macro]) == coverage

    manifest = foundation.load(PRIMARY_MANIFEST)
    assert manifest["status"] == "COMPLETE"
    assert manifest["macros"] == [list(macro) for macro in EXPECTED]
    assert manifest["expected_orbits"] == {
        macro_key(macro): values[0] for macro, values in EXPECTED.items()
    }
    assert manifest["solver"] == str(SOLVER)
    assert manifest["solver_sha256"] == foundation.sha256(SOLVER)
    assert manifest["ordinary_local_pair"] is True
    assert manifest["ordinary_local_pair_every_depth"] is True
    assert manifest["ordinary_joint_map"] is True
    assert manifest["node_cap"] == 0
    assert manifest["joint_map_node_cap"] == 0
    assert manifest["projection"] == []
    assert manifest["tasks"] == [
        [list(macro), start, stop] for macro, start, stop in TASKS
    ]

    base_inputs = (
        foundation.LOCAL,
        foundation.CATALOG,
        foundation.GRAM,
        foundation.FIBRE_FILTER,
        foundation.CONFIG_FRONTIER,
    )
    inputs = {
        str(path): foundation.sha256(path)
        for path in (
            *base_inputs, *MODEL_CODE, SOLVER, PRIMARY_RUNNER,
            PRIMARY_MANIFEST, AUDIT_FOUNDATION,
        )
    }
    seen = {macro: set() for macro in EXPECTED}
    per_macro_hist = {macro: Counter() for macro in EXPECTED}
    per_macro_mass = {macro: Counter() for macro in EXPECTED}
    shard_summaries = []
    audited_rows = []
    for macro, start, stop in TASKS:
        path = shard_path(macro, start, stop)
        digest = foundation.sha256(path)
        inputs[str(path)] = digest
        key = f"{macro_key(macro)}:{start}:{stop}"
        checkpoint = manifest["shards"][key]
        assert checkpoint["status"] == "COMPLETE"
        assert checkpoint["path"] == str(path)
        assert checkpoint["sha256"] == digest
        document = foundation.load(path)
        assert document["status"] == "EXACT_SYNCHRONIZED_CONFIG_CSP_SLICE_COMPLETE"
        assert document["inputs"] == {
            str(input_path): foundation.sha256(input_path)
            for input_path in base_inputs
        }
        summary = document["summary"]
        assert summary["wanted_macros"] == [list(macro)]
        assert summary["available_orbits_in_wanted_macros"] == EXPECTED[macro][0]
        assert summary["slice_start"] == start
        assert summary["slice_stop"] == stop
        assert summary["explicit_record_selection"] == []
        assert summary["input_orbits"] == stop - start
        assert summary["ordinary_local_pair_filter_enabled"] is True
        assert summary["ordinary_local_pair_every_depth_enabled"] is True
        assert summary["ordinary_joint_map_filter_enabled"] is True
        assert summary["ordinary_joint_map_unknowns_relaxed_as_pass"] == 0
        assert summary["fixed_block_projection"] == []
        assert [int(row[0]) for row in document["results"]] == list(
            range(start, stop)
        )
        shard_hist = Counter()
        shard_mass = Counter()
        for result in document["results"]:
            record_number, representative = foundation.verify_result(
                result, macro, records
            )
            assert record_number not in seen[macro]
            seen[macro].add(record_number)
            status = str(result[5])
            orbit_size = int(representative["orbit_size"])
            shard_hist[status] += 1
            shard_mass[status] += orbit_size
            per_macro_hist[macro][status] += 1
            per_macro_mass[macro][status] += orbit_size
            audited_rows.append({
                "macro": list(macro),
                "record_number": record_number,
                "mask_hex": representative["mask_hex"],
                "Q": int(representative["Q"]),
                "orbit_size": orbit_size,
                "status": status,
                "reason": result[6],
                "DFS_nodes": int(result[7]),
                "evidence_artifact": str(path),
                "evidence_sha256": digest,
            })
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
            "ordinary_joint_map_calls": summary["ordinary_joint_map_calls"],
            "ordinary_joint_map_nodes": summary["ordinary_joint_map_nodes"],
            "elapsed_seconds": summary["elapsed_seconds"],
        })

    per_macro = []
    total_hist = Counter()
    total_mass = Counter()
    for macro, (count, coverage, q) in EXPECTED.items():
        assert seen[macro] == set(range(count))
        assert per_macro_hist[macro]["UNSAT"] == count
        assert per_macro_hist[macro]["SAT"] == 0
        assert per_macro_hist[macro]["UNKNOWN"] == 0
        assert per_macro_mass[macro]["UNSAT"] == coverage
        assert per_macro_mass[macro]["SAT"] == 0
        assert per_macro_mass[macro]["UNKNOWN"] == 0
        total_hist.update(per_macro_hist[macro])
        total_mass.update(per_macro_mass[macro])
        per_macro.append({
            "macro": list(macro),
            "Q": q,
            "catalog_orbits": count,
            "catalog_coverage": coverage,
            "status_histogram": {
                status: per_macro_hist[macro][status]
                for status in ("SAT", "UNSAT", "UNKNOWN")
            },
            "status_mass": {
                status: per_macro_mass[macro][status]
                for status in ("SAT", "UNSAT", "UNKNOWN")
            },
        })
    total_orbits = sum(values[0] for values in EXPECTED.values())
    total_coverage = sum(values[1] for values in EXPECTED.values())
    assert len(audited_rows) == total_orbits == 400
    assert total_hist["UNSAT"] == total_orbits
    assert total_hist["SAT"] == total_hist["UNKNOWN"] == 0
    assert total_mass["UNSAT"] == total_coverage == 36_864
    assert total_mass["SAT"] == total_mass["UNKNOWN"] == 0

    result = {
        "status": "SOURCE150_SMALL5_JOINT_PRIMARY_INDEPENDENT_AUDIT_PASS",
        "inputs": inputs,
        "source_row_index": 150,
        "macros": [list(macro) for macro in EXPECTED],
        "catalog_total_orbits": total_orbits,
        "catalog_total_coverage": total_coverage,
        "mode": {
            "uncapped_exact_synchronized_ordinary_joint_map_pair_primary": True,
            "ordinary_local_pair_every_depth_necessary_prefilter": True,
            "node_cap": 0,
            "joint_map_node_cap": 0,
            "projection": [],
        },
        "model_necessity": {
            "pointwise_recurrence": (
                "Every SRG completion satisfies the pointwise (B+I)q=12c "
                "rows used by the synchronized exceptional-block CSP."
            ),
            "ordinary_map_completeness": (
                "For every fixed global ordinary configuration, the joint "
                "factor search enumerates all labelled one-sided maps from "
                "exceptional fibres to each ordinary fibre that realize those "
                "pointwise rows; it assumes no converse ordinary regularity."
            ),
            "pair_capacity": (
                "Cumulative exceptional-pair collisions cannot exceed the "
                "remaining common-neighbour capacities forced by lambda=1, "
                "mu=2, so failure of every map is a necessary-condition "
                "contradiction for an SRG completion."
            ),
            "safe_unknown_policy": (
                "Both DFS caps are zero. Any SAT or UNKNOWN output would remain "
                "unresolved and is never credited as excluded."
            ),
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
        "status_histogram": {
            status: total_hist[status]
            for status in ("SAT", "UNSAT", "UNKNOWN")
        },
        "status_mass": {
            status: total_mass[status]
            for status in ("SAT", "UNSAT", "UNKNOWN")
        },
        "all_five_catalog_macros_excluded": True,
        "SAT_or_UNKNOWN_counted_as_excluded": False,
        "projection_evidence_credited": False,
        "evidence_class": "exact_solver_free_finite_local_CSP",
        "DRAT_certificate_present": False,
        "shards": shard_summaries,
        "records": audited_rows,
        "claim_boundary": (
            "This excludes only the five listed source150 macros. It does not "
            "include macro (0,3), does not exclude all source150 or E0=72, and "
            "makes no DRAT claim."
        ),
    }
    atomic_json(OUTPUT, result)

    table = "\n".join(
        f"| `{tuple(row['macro'])}` | {row['Q']} | "
        f"{row['catalog_orbits']:,} | {row['catalog_coverage']:,} | "
        f"{row['status_histogram']['UNSAT']:,} |"
        for row in per_macro
    )
    report = f"""# source150 small-five joint-map primary audit

Status: `{result['status']}`

| macro | Q | orbits | coverage | exact UNSAT |
|---|---:|---:|---:|---:|
{table}

The five macros contain {total_orbits:,} local symmetry orbits with labelled
coverage {total_coverage:,}. Every case is exact UNSAT; SAT and UNKNOWN are
both zero. The primary search is uncapped synchronized labelled ordinary-map
enumeration with cumulative exceptional-pair capacities. An exact local-pair
necessary filter is applied at every block depth. No projection result is
credited.

The audit independently reconstructs the representative list and checks every
input hash, record number, mask, Q, orbit size, shard boundary, status, and
coverage mass. The recurrence, complete labelled-map enumeration, and SRG
common-neighbour capacities are all necessary for a full SRG completion;
therefore exhaustive failure is a sound local contradiction. This remains a
five-macro finite-CSP result, not a DRAT certificate or a full source150/E0=72
exclusion. Macro `(0,3)` is explicitly outside this artifact.
"""
    atomic_text(REPORT, report)
    print(json.dumps({
        "status": result["status"],
        "orbits": total_orbits,
        "coverage": total_coverage,
        "SAT": 0,
        "UNKNOWN": 0,
        "output": str(OUTPUT),
        "report": str(REPORT),
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
